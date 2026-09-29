"""Experiment 4's gates (solarbench.price_gates), offline: K1 on a tiny EPF-like dataset and fake published
forecasts, K2 and K3 with stand-ins for t0 on synthetic hourly prices."""

from __future__ import annotations

import hashlib
import logging
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import test_price_exp as tpx
from engine import covs
from engine.gates import KA_RULES
from solarbench import covariates as cov
from solarbench import lear
from solarbench import price_exp as px
from solarbench import price_gates as pg
from solarbench import price_spec as ps

pytest.importorskip("sklearn")
torch = pytest.importorskip("torch")

HOUR = pd.Timedelta(hours=1)


# ================================================================================== K1

EPF_START, EPF_END = "2014-09-20", "2015-01-12"
SMOKE_DAYS = 1


def epf_like(start: str = EPF_START, end: str = EPF_END, seed: int = 0) -> pd.DataFrame:
    """EPF-FR's shape: a naive local hourly index (24 rows a day) and its three columns, leading spaces kept."""
    idx = pd.date_range(start, end, freq="h", inclusive="left")
    rng = np.random.default_rng(seed)
    h, dow, n = idx.hour.to_numpy(), idx.dayofweek.to_numpy(), len(idx)
    load = 55000 + 8000 * np.sin(2 * np.pi * (h - 7) / 24) - 4000 * (dow >= 5) + rng.normal(0, 800, n)
    gen = 60000 + 3000 * np.sin(2 * np.pi * (h - 8) / 24) + rng.normal(0, 1000, n)
    price = 40 + 0.002 * (load - 55000) - 0.0005 * (gen - 60000) + rng.normal(0, 2, n)
    return pd.DataFrame({" Prices": price, " Generation forecast": gen, " System load forecast": load}, index=idx)


def published_frame(*, subset: dict | None = None, real_subset: np.ndarray | None = None,
                    mae: dict | None = None, seed: int = 1) -> pd.DataFrame:
    """A fake published CSV over the 17,472 K1 hours whose MAEs recompute to ``mae`` (default: the spec's).

    Every column is the real price +- a constant, except on the first hours, where ``subset`` gives each
    column's values (and ``real_subset`` the real price); the constant then makes the total MAE exact.
    """
    hours = pg.k1_hours(pg.k1_days())
    rng = np.random.default_rng(seed)
    real = 50 + 10 * rng.standard_normal(len(hours))
    mae = dict(pg.K1["published_mae"] if mae is None else mae)
    n_sub = 0 if real_subset is None else len(real_subset)
    if n_sub:
        real[:n_sub] = real_subset
    frame = {"Real price": real}
    for j, c in enumerate(mae):
        signs = rng.choice([-1.0, 1.0], size=len(hours))
        if n_sub:
            s = float(np.abs(np.asarray(subset[c]) - real_subset).sum())
            b = (mae[c] * len(hours) - s) / (len(hours) - n_sub)
            v = real + b * signs
            v[:n_sub] = subset[c]
        else:
            v = real + mae[c] * signs
        frame[c] = v
    frame["DNN Ensemble"] = real + 1.0  # the real file carries other columns too
    return pd.DataFrame(frame, index=hours)


def write(frame: pd.DataFrame, path) -> str:
    frame.to_csv(path, index_label="Date")
    return str(path)


@pytest.fixture(scope="module")
def epf(tmp_path_factory):
    d = tmp_path_factory.mktemp("epf")
    df = epf_like()
    return d, write(df, d / "FR.csv"), df


@pytest.fixture(scope="module")
def smoke_forecasts(epf):
    """The clean-room forecasts of the first smoke day, computed once, in-process."""
    _, fr, _ = epf
    return pg.k1_forecasts(pg.read_epf_fr(fr), pg.k1_days(SMOKE_DAYS), processes=1)


def flat(frame: pd.DataFrame) -> np.ndarray:
    return frame.to_numpy(dtype="float64").reshape(-1)


def test_k1_constants_are_the_frozen_text():
    tol = pg.K1["tolerance"]
    assert "[-2%, +1%]" in tol and "[-3%, +2%]" in tol and "<= 0.25 EUR/MWh" in tol
    assert "17,472" in tol and "4 decimals" in tol
    assert pg.K1_ENSEMBLE_BAND == (-0.02, 0.01) and pg.K1_WINDOW_BAND == (-0.03, 0.02)
    assert pg.K1_MAX_MEAN_ABS_DIFF == 0.25 and pg.K1_DECIMALS == 4
    hours = pg.k1_hours(pg.k1_days())
    assert len(hours) == pg.K1_HOURS == 17_472
    assert hours[0] == pd.Timestamp("2015-01-04 00:00") and hours[-1] == pd.Timestamp("2016-12-31 23:00")
    assert pg.PUBLISHED_SHA256 == "671d65842180fd7fc0f603eca6281f4ddc581983cbfb4991e97e291d5d88ab08"
    assert set(pg.k1_names()) == set(pg.K1["published_mae"]) and pg.K1_WINDOWS == (56, 84, 1092, 1456)
    assert "within 0.01 EUR/MWh" in pg.K2["what"] and pg.K2_TOLERANCE == 0.01


def test_read_epf_fr_matches_columns_after_strip_and_builds_day_matrices(tmp_path):
    df = epf_like("2014-12-01", "2014-12-05")
    df.columns = ["  PRICES", "Generation forecast ", " system load forecast"]
    mats = pg.read_epf_fr(write(df, tmp_path / "fr.csv"))
    assert set(mats) == {"price", "generation", "load"}
    np.testing.assert_allclose(mats["price"].loc[date(2014, 12, 2)].to_numpy(),
                               df.iloc[24:48, 0].to_numpy(), rtol=0, atol=1e-9)
    np.testing.assert_allclose(mats["load"].loc[date(2014, 12, 3)].to_numpy(), df.iloc[48:72, 2].to_numpy())
    with pytest.raises(ValueError, match="columns not found"):
        pg.read_epf_fr(write(df.iloc[:, :2], tmp_path / "bad.csv"))


def test_k1_forecast_uses_the_published_configuration(epf, monkeypatch):
    """features_k1: both exogenous series (at D, D-1, D-7), no holiday dummy, every window, all days."""
    _, fr, _ = epf
    seen = []

    def spy(prices, days, *, window, exog=(), dummies=None, n_extra=0):
        seen.append((window, len(exog), n_extra, dummies, list(days)))
        return pd.DataFrame(np.ones((len(days), 24)) * window, index=list(days)), lear.WindowLog(window)

    monkeypatch.setattr(lear, "forecast", spy)
    days = pg.k1_days(3)
    parts, logs = pg.k1_forecasts(pg.read_epf_fr(fr), days, processes=1)
    assert [s[0] for s in seen] == [56, 84, 1092, 1456]
    assert all(s[1] == 2 and s[2] == 0 and s[3] is None and s[4] == days for s in seen)
    assert parts["LEAR Ensemble"].to_numpy().mean() == pytest.approx(np.mean([56, 84, 1092, 1456]))
    assert set(logs) == {"56", "84", "1092", "1456"}
    assert lear.EXOG_LAGS == (0, 1, 7)  # the exogenous lags features() applies


def test_k1_stops_when_the_published_maes_do_not_recompute(epf, tmp_path, monkeypatch):
    _, fr, _ = epf

    def never(*a, **k):
        raise AssertionError("a stopped K1 must not forecast")

    monkeypatch.setattr(pg, "k1_forecasts", never)
    wrong = dict(pg.K1["published_mae"], **{"LEAR 84": 4.5755})
    res = pg.run_k1(fr, write(published_frame(mae=wrong), tmp_path / "p1.csv"), processes=1)
    assert res["status"] == "stop" and res["pass"] is False and res["counts_as_attempt"] is False
    assert res["published_check"]["mae_rounded"]["LEAR 84"] == 4.5755 and not res["published_check"]["match"]
    # a missing hour cannot be recomputed either (also in a smoke)
    short = published_frame().drop(pd.Timestamp("2016-06-01 05:00"))
    res = pg.run_k1(fr, write(short, tmp_path / "p2.csv"), processes=1, limit_days=1)
    assert res["status"] == "stop" and "17472" in res["published_check"]["reason"]
    # the right MAEs recompute exactly
    good = pg.published_check(published_frame(), pg.k1_hours(pg.k1_days()))
    assert good["match"] and good["mae_rounded"] == pg.K1["published_mae"]


def test_k1_attempt_stops_on_files_that_are_not_the_pinned_ones(epf, tmp_path, monkeypatch):
    _, fr, _ = epf
    monkeypatch.setattr(pg, "k1_forecasts", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no forecast")))
    res = pg.run_k1(fr, write(published_frame(), tmp_path / "p.csv"), processes=1)
    assert res["status"] == "stop" and len(res["stop_reasons"]) == 2
    assert not res["fr_csv_pinned"] and not res["published_pinned"]


#: What a smoke never computes (gates.K1.tolerance: "no MAE or difference is ever computed on a subset").
SMOKE_NONE = ("mae", "reference_mae", "deviation", "mean_abs_diff_ensemble", "checks",
              "fr_price_vs_real_price_max_abs_diff")


def never_judge(*a, **k):
    raise AssertionError("a smoke never applies the K1 rule")


def test_k1_smoke_on_the_real_lear_computes_no_metric(epf, smoke_forecasts, tmp_path, monkeypatch):
    """A smoke runs the real LEAR on its days and records only coverage and the logs; it never judges."""
    _, fr, _ = epf
    _, logs = smoke_forecasts
    monkeypatch.setattr(pg, "k1_verdict", never_judge)
    res = pg.run_k1(fr, write(published_frame(), tmp_path / "pub.csv"), processes=1, limit_days=SMOKE_DAYS)
    assert res["status"] == pg.SMOKE == res["smoke"] == "smoke: not a K1 attempt"
    assert res["pass"] is False and res["counts_as_attempt"] is False and "smoke_outcome" not in res
    assert res["every_hour_forecast"] and res["hours"] == 24 * SMOKE_DAYS
    assert res["non_finite_hours"] == {c: 0 for c in pg.k1_names()}
    assert all(res[k] is None for k in SMOKE_NONE), {k: res[k] for k in SMOKE_NONE}
    sha = hashlib.sha256(Path(lear.__file__).read_bytes()).hexdigest()
    assert res["lear_sha256"] == res["lear_sha256_at_import"] == res["lear_sha256_at_start"] == sha
    assert res["lear_sha256_at_end"] == sha and res["lear_file"] == "solarbench/lear.py"
    assert set(res["logs"]) == {"56", "84", "1092", "1456"} and res["logs"] == logs
    for lg in res["logs"].values():
        assert {"dropped_rows", "scale_fallbacks", "no_forecast", "forecast_days"} <= set(lg)
    assert res["logs"]["56"]["dropped_rows"] == 0 and res["logs"]["1456"]["dropped_rows"] > 0  # short history
    assert res["run_seconds"] > 0


def test_k1_smoke_output_does_not_depend_on_the_published_forecasts_of_its_hours(epf, smoke_forecasts,
                                                                                  tmp_path, monkeypatch):
    """Two published files that differ only on the smoke's hours (one would pass the rule there, one would
    fail it) give the same smoke record: nothing of the published forecasts on a subset is read."""
    _, fr, df = epf
    parts, _ = smoke_forecasts
    monkeypatch.setattr(pg, "k1_forecasts", lambda *a, **k: smoke_forecasts)
    real = df[" Prices"].reindex(pg.k1_hours(pg.k1_days(SMOKE_DAYS))).to_numpy()
    same = {c: flat(parts[c]) for c in pg.k1_names()}
    away = dict(same, **{"LEAR Ensemble": same["LEAR Ensemble"] + 1.0})
    out = []
    for j, sub in enumerate((same, away)):
        res = pg.run_k1(fr, write(published_frame(subset=sub, real_subset=real), tmp_path / f"p{j}.csv"),
                        processes=1, limit_days=SMOKE_DAYS)
        assert res["published_check"]["match"] and res["status"] == pg.SMOKE
        out.append({k: v for k, v in res.items() if k not in ("published_sha256", "published_check", "run_seconds")})
    assert out[0] == out[1]


@pytest.mark.parametrize("limit", [0, 728, 729, 10_000])
def test_k1_smoke_cannot_cover_the_full_period(epf, tmp_path, monkeypatch, limit):
    _, fr, _ = epf
    monkeypatch.setattr(pg, "k1_forecasts", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no forecast")))
    assert len(pg.k1_days()) == 728
    with pytest.raises(ValueError, match="limit_days"):
        pg.run_k1(fr, write(published_frame(), tmp_path / "pub.csv"), processes=1, limit_days=limit)


def test_k1_rule_on_the_smoke_forecasts_by_direct_calls(epf, smoke_forecasts):
    """The rule itself (k1_verdict) on the real LEAR's smoke forecasts and a synthetic published frame of the
    same hours: equal forecasts pass with deviation 0; an ensemble 1 EUR/MWh away fails the difference rule
    (and moves the reference MAE); a mirrored ensemble (same MAE, other side of y) fails only that rule."""
    _, _, df = epf
    parts, _ = smoke_forecasts
    hours = pg.k1_hours(pg.k1_days(SMOKE_DAYS))
    clean = {c: flat(parts[c]) for c in pg.k1_names()}
    real = df[" Prices"].reindex(hours).to_numpy()
    pub = pd.DataFrame({"Real price": real, **clean}, index=hours)
    v = pg.k1_verdict(clean, pub)
    assert v["pass"] is True and v["hours"] == 24 * SMOKE_DAYS and all(v["checks"].values())
    assert all(abs(d) < 1e-12 for d in v["deviation"].values()) and v["mean_abs_diff_ensemble"] < 1e-12
    v = pg.k1_verdict(clean, pub.assign(**{"LEAR Ensemble": pub["LEAR Ensemble"] + 1.0}))
    assert v["pass"] is False and v["mean_abs_diff_ensemble"] == pytest.approx(1.0)
    assert not v["checks"]["mean_abs_diff_ensemble"]
    mirrored = 2 * real - clean["LEAR Ensemble"]
    v = pg.k1_verdict(clean, pub.assign(**{"LEAR Ensemble": mirrored}))
    assert abs(v["deviation"]["LEAR Ensemble"]) < 1e-12 and v["mean_abs_diff_ensemble"] > 0.25
    assert [k for k, ok in v["checks"].items() if not ok] == ["mean_abs_diff_ensemble"] and v["pass"] is False


def test_k1_every_hour_rule_in_a_smoke(tmp_path, monkeypatch):
    df = epf_like()
    df.loc[pd.Timestamp("2015-01-03 05:00"), " Prices"] = np.nan  # D-1 of the first K1 day
    fr = write(df, tmp_path / "FR.csv")
    monkeypatch.setattr(pg, "k1_verdict", never_judge)
    res = pg.run_k1(fr, write(published_frame(), tmp_path / "pub.csv"), processes=1, limit_days=1)
    assert res["status"] == pg.SMOKE and res["pass"] is False and not res["every_hour_forecast"]
    assert "smoke_outcome" not in res and all(res[k] is None for k in SMOKE_NONE)
    assert all(n == 24 for n in res["non_finite_hours"].values())
    assert all(lg["no_forecast"]["missing_features"] == ["2015-01-04"] for lg in res["logs"].values())


def test_k1_windows_in_parallel_processes_give_the_same_bits(epf, smoke_forecasts):
    _, fr, _ = epf
    parts, logs = pg.k1_forecasts(pg.read_epf_fr(fr), pg.k1_days(SMOKE_DAYS), processes=2)
    ref_parts, ref_logs = smoke_forecasts
    assert list(parts) == list(ref_parts) == pg.k1_names()
    for c in parts:
        assert np.array_equal(parts[c].to_numpy(), ref_parts[c].to_numpy())
        assert parts[c].index.equals(ref_parts[c].index)
    assert logs == ref_logs


@pytest.fixture
def attempt(epf, tmp_path, monkeypatch):
    """A full (non-smoke) attempt with pinned fakes and synthetic clean-room forecasts of all 728 days."""
    _, fr, _ = epf
    pub = published_frame()
    path = write(pub, tmp_path / "published.csv")
    monkeypatch.setattr(pg, "PUBLISHED_SHA256", pg.sha256_file(path))
    monkeypatch.setattr(pg, "EPF_FR_SHA256", pg.sha256_file(fr))
    days = pg.k1_days()
    y = pub["Real price"].to_numpy()

    def run(transform=lambda c, v: v, during=None):
        def fake(mats, ds, *, processes=4):
            assert list(ds) == days
            if during is not None:
                during()
            parts = {c: pd.DataFrame(transform(c, pub[c].to_numpy().copy()).reshape(len(days), 24), index=days)
                     for c in pg.k1_names()}
            return parts, {str(n): {"window": n, "dropped_rows": 0, "scale_fallbacks": 0} for n in pg.K1_WINDOWS}

        monkeypatch.setattr(pg, "k1_forecasts", fake)
        return pg.run_k1(fr, path, processes=1)

    return run, y


def scaled(target: str, factor: float, y: np.ndarray):
    """Scale ``target``'s errors by ``factor``: its MAE deviation is then factor - 1."""
    return lambda c, v: (y + factor * (v - y)) if c == target else v


def test_k1_attempt_passes_on_the_published_forecasts(attempt):
    run, _ = attempt
    res = run()
    assert res["status"] == "pass" and res["pass"] is True and res["counts_as_attempt"] is True
    assert res["smoke"] is False and res["hours"] == 17_472 and res["every_hour_forecast"]
    assert all(abs(v) < 1e-12 for v in res["deviation"].values()) and res["mean_abs_diff_ensemble"] == 0.0
    sha = hashlib.sha256(Path(lear.__file__).read_bytes()).hexdigest()
    assert res["lear_sha256"] == res["lear_sha256_at_import"] == res["lear_sha256_at_start"] == sha
    assert res["lear_sha256_at_end"] == sha == pg.LEAR_SHA256_AT_IMPORT


def test_k1_stops_if_lear_py_changed_after_import(attempt, monkeypatch):
    """The file on disk at the start is not the lear the process imported: stop, nothing forecast."""
    run, _ = attempt
    monkeypatch.setattr(pg, "LEAR_SHA256_AT_IMPORT", "0" * 64)
    called = []
    res = run(during=lambda: called.append(1))
    assert called == [] and res["status"] == "stop" and res["counts_as_attempt"] is False and res["pass"] is False
    assert res["stop_reasons"] == ["solarbench/lear.py changed after it was imported: the code that would run "
                                   "is not the file"]
    assert res["lear_sha256_at_end"] is None and "mae" not in res and "every_hour_forecast" not in res


@pytest.mark.parametrize("smoke", [False, True])
def test_k1_stops_if_lear_py_changes_while_it_runs(attempt, epf, tmp_path, monkeypatch, smoke):
    """lear.py hashed at import, start and end (spawned workers re-import it): an edit during the run stops
    K1 before any verdict, and the entry is not an attempt."""
    run, _ = attempt
    copy_ = tmp_path / "lear.py"
    copy_.write_bytes(Path(lear.__file__).read_bytes())
    monkeypatch.setattr(pg, "LEAR_FILE", copy_)
    monkeypatch.setattr(pg, "LEAR_SHA256_AT_IMPORT", pg.sha256_file(copy_))
    monkeypatch.setattr(pg, "k1_verdict", never_judge)

    def edit():
        copy_.write_text(copy_.read_text() + "\n# edited mid-run\n")

    if smoke:
        _, fr, _ = epf
        monkeypatch.setattr(pg, "k1_forecasts", lambda *a, **k: (edit(), ({}, {}))[1])
        res = pg.run_k1(fr, write(published_frame(), tmp_path / "pub.csv"), processes=1, limit_days=2)
        assert res["smoke"] == pg.SMOKE
    else:
        res = run(during=edit)
    assert res["status"] == "stop" and res["counts_as_attempt"] is False and res["pass"] is False
    assert res["lear_sha256_at_start"] == res["lear_sha256_at_import"] != res["lear_sha256_at_end"]
    assert res["lear_sha256_at_end"] == pg.sha256_file(copy_) and "changed while K1 ran" in res["stop_reasons"][0]
    assert "mae" not in res and "every_hour_forecast" not in res


@pytest.mark.parametrize("target,factor,ok", [
    ("LEAR 56", 1.019, True), ("LEAR 56", 1.021, False), ("LEAR 1456", 0.971, True), ("LEAR 1092", 0.969, False),
    ("LEAR Ensemble", 1.009, True), ("LEAR Ensemble", 1.011, False), ("LEAR Ensemble", 0.981, True),
    ("LEAR Ensemble", 0.979, False)])
def test_k1_attempt_deviation_bands(attempt, target, factor, ok):
    run, y = attempt
    res = run(scaled(target, factor, y))
    assert res["deviation"][target] == pytest.approx(factor - 1.0, abs=1e-9)
    assert res["pass"] is ok and res["status"] == ("pass" if ok else "fail") and res["counts_as_attempt"]
    key = "ensemble_deviation" if target == "LEAR Ensemble" else f"window_deviation:{target}"
    assert res["checks"][key] is ok and res["checks"]["mean_abs_diff_ensemble"]


def test_k1_attempt_fails_on_the_difference_from_the_published_ensemble(attempt):
    run, y = attempt
    rng = np.random.default_rng(7)
    mae = pg.K1["published_mae"]["LEAR Ensemble"]
    res = run(lambda c, v: y + mae * rng.choice([-1.0, 1.0], len(v)) if c == "LEAR Ensemble" else v)
    assert abs(res["deviation"]["LEAR Ensemble"]) < 1e-9  # same MAE, different hours
    assert res["mean_abs_diff_ensemble"] > 0.25 and res["status"] == "fail"
    assert not res["checks"]["mean_abs_diff_ensemble"] and res["checks"]["ensemble_deviation"]


def test_k1_attempt_fails_if_any_hour_is_not_forecast(attempt):
    run, _ = attempt

    def one_gap(c, v):
        if c == "LEAR 1092":
            v[9000] = np.nan
        return v

    res = run(one_gap)
    assert res["status"] == "fail" and res["counts_as_attempt"] and not res["every_hour_forecast"]
    assert res["non_finite_hours"]["LEAR 1092"] == 1 and res["mae"] is None and res["deviation"] is None
    assert res["mean_abs_diff_ensemble"] is None


# ================================================================================== K2

#: A synthetic price series long enough for every TEST_ORIGINS day (2160-h contexts from 2023-10, up to
#: 2025-12-31); nothing on or after 2026-01-01 Paris.
K2_START, K2_END = "2023-09-01", "2026-01-01"
K2_DAYS = [date.fromisoformat(d) for d in ps.TEST_ORIGINS]
P4_FIRST = date.fromisoformat(ps.AVAIL["p4_first_day"])


@pytest.fixture(scope="module")
def k2_data():
    s = tpx.prices(K2_START, K2_END)
    grid = pd.date_range(s.index[0], s.index[-1] + pd.Timedelta(days=2), freq="1h", tz="UTC")
    rng = np.random.default_rng(3)
    wx = pd.Series(rng.normal(10, 5, len(grid) + 1),
                   index=pd.date_range(grid[0], periods=len(grid) + 1, freq="1h", tz="UTC"))
    return s, px.weather_covariates(wx, wx.abs(), grid)


def k2_setup(k2_data):
    """The series, fresh K2 arms (t0, t0_cal, t0_cal_strict, t0_cal_wx) and their k2_windows."""
    s, (temp, rad) = k2_data
    arms = [px.PriceT0Forecaster("t0", covariates=()), px.PriceT0Forecaster("t0_cal", covariates=(px.holiday(),)),
            px.PriceT0Forecaster("t0_cal_strict", covariates=(px.holiday(),), horizon=px.STRICT_HORIZON),
            px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), temp, rad))]
    return s, arms, pg.k2_windows(s)


class BatchShift(tpx.EchoT0):
    """t0 whose output moves with the batch size (as batch composition moves the real one)."""

    def __init__(self, eps: float):
        super().__init__()
        self.eps = eps

    def predict(self, context, horizon, quantiles, future_covariates=None):
        out = super().predict(context, horizon, quantiles, future_covariates)
        shift = self.eps * (out.median.shape[0] - 1)
        return SimpleNamespace(median=out.median + shift, quantiles=out.quantiles + shift)


class HorizonSpy(tpx.EchoT0):
    """EchoT0 that records the horizon of every call."""

    def __init__(self):
        super().__init__()
        self.horizons: list[int] = []

    def predict(self, context, horizon, quantiles, future_covariates=None):
        self.horizons.append(int(horizon))
        return super().predict(context, horizon, quantiles, future_covariates)


class ShiftedContext(px.PriceT0Forecaster):
    """A broken adapter: its context ends one hour early."""

    def context(self, series, origin):
        return super().context(series, origin - HOUR)


class Float64Block(px.PriceT0Forecaster):
    """A broken adapter: it hands t0 the covariate block in float64 instead of float32."""

    def block(self, origin):
        times = self.block_times(origin)
        return np.stack([np.asarray(c.values(times), dtype="float64") for c in self.covariates]), pd.NaT


class Raising(px.PriceT0Forecaster):
    def predict(self, series, windows):
        raise RuntimeError("adapter exploded")


PREDICT_CALLS: list[int] = []


class Spy(px.PriceT0Forecaster):
    def predict(self, series, windows):
        PREDICT_CALLS.append(len(windows))
        return super().predict(series, windows)


def test_k2_windows_are_every_test_origin_day_of_each_arms_kind(k2_data):
    s, _, ws = k2_setup(k2_data)
    assert set(ws) == set(pg.K2_ARMS) == {"t0", "t0_cal", "t0_cal_strict", "t0_cal_wx"}
    assert pg.K2_STRICT_ARM == "t0_cal_strict" and len(K2_DAYS) == 11 and pg.k2_days() == K2_DAYS
    for name in ("t0", "t0_cal", "t0_cal_strict"):
        assert [w.delivery_date for w in ws[name]] == K2_DAYS, name
    for w in ws["t0"] + ws["t0_cal"]:
        assert not w.strict and w.origin == w.targets[0] - HOUR == pg.context_end(w)
    for w in ws["t0_cal_strict"]:
        assert w.strict and w.origin == w.decision == pg.context_end(w)
        assert w.origin.tz_convert("Europe/Paris").hour == 12
    # t0_cal_wx: only the origins on or after AVAIL.p4_first_day, as cutoff windows
    assert P4_FIRST == date(2024, 6, 6)
    assert [w.delivery_date for w in ws["t0_cal_wx"]] == [d for d in K2_DAYS if d >= P4_FIRST]
    assert len(ws["t0_cal_wx"]) == 9 and not any(w.strict for w in ws["t0_cal_wx"])
    # a TEST_ORIGINS day with an incomplete target is never silently left out
    s2 = s.copy()
    s2[px.day_hours(date(2024, 6, 26))[5]] = np.nan
    assert len(px.build_price_windows(s2, K2_DAYS)) == 10
    assert all(len(v) == len(ws[k]) for k, v in pg.k2_windows(s2).items())


def test_k2_passes_every_arm_with_the_faithful_adapter(k2_data):
    s, arms, _ = k2_setup(k2_data)
    before = [(a.missing, a._model) for a in arms]
    res = pg.run_k2(arms, tpx.EchoT0(), s)
    assert res["pass"] is True and set(res["arms"]) == {"t0", "t0_cal", "t0_cal_strict", "t0_cal_wx"}
    assert res["arms_missing"] == [] and res["windows_given"] == [] and res["days"] == ps.TEST_ORIGINS
    for name, r in res["arms"].items():
        assert r["pass"] and r["single_pass"] and r["batch_pass"], (name, r)
        assert r["windows_ok"] and r["window_kind_ok"] and r["horizon_ok"]
        assert all(r["single"].values()) and r["days"] == r["expected_days"]
        assert r["batch_max_abs_diff"] == 0.0  # the stand-in is row-wise, so the batch is exact
    assert [len(res["arms"][n]["single"]) for n in pg.K2_ARMS] == [11, 11, 11, 9]
    assert res["arms"]["t0_cal_strict"]["horizon"] == 36 and res["arms"]["t0_cal_strict"]["window_kind"] == "strict"
    assert res["arms"]["t0_cal_wx"]["covariates"] == ["holiday", "wx_temperature", "wx_radiation"]
    assert [(a.missing, a._model) for a in arms] == before  # the caller's arms are untouched
    assert all(a.missing == {"context": [], "sanitised": []} for a in arms)
    # without weather, K2 passes on the three arms it always needs
    assert pg.run_k2(arms[:3], tpx.EchoT0(), s)["pass"] is True


def test_k2_needs_t0_t0_cal_and_t0_cal_strict(k2_data):
    s, arms, _ = k2_setup(k2_data)
    res = pg.run_k2(arms[:2], tpx.EchoT0(), s)
    assert all(r["pass"] for r in res["arms"].values()) and res["arms_missing"] == ["t0_cal_strict"]
    assert res["pass"] is False
    res = pg.run_k2([arms[1], px.PriceT0Forecaster("t0_other", covariates=())] + [arms[0], arms[2]],
                    tpx.EchoT0(), s)
    assert res["arms"]["t0_other"]["pass"] is False and "not a K2 arm" in res["arms"]["t0_other"]["error"]
    assert res["pass"] is False
    assert pg.run_k2([], tpx.EchoT0(), s)["pass"] is False


def test_k2_reference_is_built_without_the_arm_and_calls_the_model_once_per_window(k2_data):
    s, arms, windows = k2_setup(k2_data)
    model = tpx.EchoT0()
    PREDICT_CALLS.clear()
    res = pg.run_k2([Spy("t0_cal", covariates=(px.holiday(),)), arms[0], arms[2]], model, s)
    n = len(K2_DAYS)
    assert res["pass"] and PREDICT_CALLS == [1] * n + [n]  # the singles and one batch; the reference never
    model = tpx.EchoT0()
    pg.run_k2([Spy("t0_cal", covariates=(px.holiday(),))], model, s)
    assert model.calls == n + n + 1  # one model call per reference row, per single, and the batch
    # the reference reads D's hours by UTC time: 25 on an autumn day, 23 in spring
    for d, hours in ((date(2024, 10, 27), 25), (date(2024, 3, 31), 23), (date(2025, 10, 26), 25)):
        for w in (px.build_price_windows(s, [d])[0], px.build_price_windows(s, [d], strict=True)[0]):
            m, q = pg.k2_reference(arms[1], tpx.EchoT0(), s, w)
            assert m.shape == (hours,) and q.shape == (hours, 5)


def test_k2_reference_horizon_is_the_spec_fixed_horizon_not_the_arms(k2_data):
    s, arms, windows = k2_setup(k2_data)
    assert "fixed 36-hour horizon" in ps.PRICE_SPEC["strict_arm"]["rule"] and px.STRICT_HORIZON == 36
    assert ps.PRICE_SPEC["t0"]["fixed_horizon_hours"] == px.HORIZON == 25
    long_cal = px.PriceT0Forecaster("t0_cal", covariates=(px.holiday(),), horizon=36)
    spy = HorizonSpy()
    pg.k2_reference(long_cal, spy, s, windows["t0_cal"][0])
    pg.k2_reference(px.PriceT0Forecaster("t0_cal_strict", covariates=(px.holiday(),), horizon=25), spy, s,
                    windows["t0_cal_strict"][0])
    assert spy.horizons == [25, 36]  # from the window kind, whatever the arm says
    # t0_cal with a 36-hour horizon: EchoT0 gives the same bits on D's hours, but the arm is not the spec's
    res = pg.run_k2([arms[0], long_cal, arms[2]], tpx.EchoT0(), s)
    r = res["arms"]["t0_cal"]
    assert r["single_pass"] and r["batch_pass"] and r["horizon"] == 36 and r["horizon_expected"] == 25
    assert r["horizon_ok"] is False and r["pass"] is False and res["pass"] is False
    # t0_cal_strict with 25 hours cannot even reach D's last hour from 12:00 D-1
    short = px.PriceT0Forecaster("t0_cal_strict", covariates=(px.holiday(),), horizon=25)
    r = pg.run_k2([arms[0], arms[1], short], tpx.EchoT0(), s)["arms"]["t0_cal_strict"]
    assert r["horizon_ok"] is False and r["pass"] is False and "needs 35 steps" in r["error"]


def test_k2_checks_each_arms_window_kind_and_day_set(k2_data):
    s, arms, ws = k2_setup(k2_data)
    model = tpx.EchoT0()
    # the strict arm on cutoff windows: its outputs match a cutoff reference, but the windows are wrong
    res = pg.run_k2(arms, model, s, windows={"t0_cal_strict": ws["t0"]})
    r = res["arms"]["t0_cal_strict"]
    assert r["single_pass"] and not r["window_kind_ok"] and not r["windows_ok"] and r["pass"] is False
    assert res["pass"] is False and res["windows_given"] == ["t0_cal_strict"]
    assert all(res["arms"][n]["pass"] for n in ("t0", "t0_cal", "t0_cal_wx"))
    # a cutoff arm on strict windows
    r = pg.run_k2(arms, model, s, windows={"t0_cal": ws["t0_cal_strict"]})["arms"]["t0_cal"]
    assert not r["window_kind_ok"] and r["pass"] is False
    # other day sets: a subset of TEST_ORIGINS, other days, t0_cal_wx before AVAIL.p4_first_day
    for name, given in (("t0", ws["t0"][:4]), ("t0_cal", px.build_price_windows(s, [date(2024, 1, 15)])),
                        ("t0_cal_wx", ws["t0"])):
        r = pg.run_k2(arms, model, s, windows={name: given})["arms"][name]
        assert r["window_kind_ok"] and not r["windows_ok"] and r["pass"] is False, name
    # windows equal to k2_windows are K2's own
    assert pg.run_k2(arms, model, s, windows=pg.k2_windows(s))["pass"] is True


def test_k2_fails_a_broken_adapter(k2_data):
    s, arms, _ = k2_setup(k2_data)
    broken = ShiftedContext("t0_cal", covariates=(px.holiday(),))
    with pytest.raises(ValueError, match="duplicate"):
        pg.run_k2([arms[1], broken], tpx.EchoT0(), s)
    res = pg.run_k2([arms[0], broken, arms[2]], tpx.EchoT0(), s)
    r = res["arms"]["t0_cal"]
    assert not r["single_pass"] and not any(r["single"].values()) and not r["batch_pass"]
    assert r["batch_max_abs_diff"] > pg.K2_TOLERANCE and res["pass"] is False


def test_k2_is_bit_for_bit_on_a_single_window(k2_data):
    s, arms, _ = k2_setup(k2_data)
    wx = arms[3]
    f64 = Float64Block("t0_cal_wx", covariates=wx.covariates)
    r = pg.run_k2([f64], tpx.EchoT0(), s)["arms"]["t0_cal_wx"]
    assert not r["single_pass"] and r["batch_pass"] and 0 < r["batch_max_abs_diff"] < 1e-3 and not r["pass"]


def test_k2_batch_tolerance_is_0_01(k2_data):
    s, arms, _ = k2_setup(k2_data)
    n = len(K2_DAYS)
    for eps, ok in ((0.02, False), (0.0101 / (n - 1), False), (0.0099 / (n - 1), True), (1e-4, True)):
        res = pg.run_k2(arms[:3], BatchShift(eps), s)
        for name, r in res["arms"].items():
            assert r["single_pass"] and r["batch_pass"] is ok, (eps, name, r)
            assert r["batch_max_abs_diff"] == pytest.approx(eps * (n - 1), rel=1e-6)
        assert res["pass"] is ok


def test_k2_at_origins_takes_the_runners_arms(k2_data):
    s, arms, _ = k2_setup(k2_data)
    runner = SimpleNamespace(t0=arms[0], t0_cal=arms[1], t0_cal_strict=arms[2], t0_cal_wx=arms[3])
    res = pg.run_k2_at_origins(runner, tpx.EchoT0(), s, p4_first_day=P4_FIRST, k3_passed=False)
    assert res["pass"] is True and list(res["arms"]) == list(pg.K2_ARMS) and res["k3_passed"] is False
    no_wx = SimpleNamespace(t0=arms[0], t0_cal=arms[1], t0_cal_strict=arms[2], t0_cal_wx=None)
    res = pg.run_k2_at_origins(no_wx, tpx.EchoT0(), s)
    assert res["pass"] is True and list(res["arms"]) == ["t0", "t0_cal", "t0_cal_strict"]
    with pytest.raises(ValueError, match="p4_first_day"):
        pg.run_k2_at_origins(runner, tpx.EchoT0(), s, p4_first_day=date(2024, 6, 7))


def test_k2_a_raising_adapter_fails_without_stopping_the_gate(k2_data):
    s, arms, _ = k2_setup(k2_data)
    res = pg.run_k2([Raising("t0", covariates=()), arms[1], arms[2]], tpx.EchoT0(), s)
    assert res["arms"]["t0"]["pass"] is False and "adapter exploded" in res["arms"]["t0"]["error"]
    assert res["arms"]["t0_cal"]["pass"] is True and res["pass"] is False
    assert res["arms"]["t0_cal_strict"]["pass"] is True


# ================================================================================== K3


class RegressionEcho:
    """Stands in for a t0 that uses a covariate as far as it explains the context: with more than one
    covariate, the last one's horizon cells regressed on the context, weighted by R^2; otherwise (and for
    the rest of the weight) yesterday's same hour."""

    def __init__(self):
        self.calls = 0

    def forecast(self, ctx: np.ndarray, fut: np.ndarray | None, horizon: int) -> np.ndarray:
        B, T = ctx.shape
        k = np.arange(horizon)
        naive = ctx[:, T - 24 + (k % 24)]
        med = naive.copy()
        if fut is not None and fut.shape[1] > 1:
            for b in range(B):
                x, y = fut[b, -1, :T], ctx[b]
                xc, yc = x - x.mean(), y - y.mean()
                sxx, sxy = float((xc * xc).sum()), float((xc * yc).sum())
                if sxx > 0:
                    r2 = sxy ** 2 / (sxx * float((yc * yc).sum()))
                    fit = y.mean() + sxy / sxx * (fut[b, -1, T:T + horizon] - x.mean())
                    med[b] = r2 * fit + (1 - r2) * naive[b]
        return med

    def predict(self, context, horizon, quantiles, future_covariates=None):
        self.calls += 1
        ctx = np.nan_to_num(np.asarray(context, dtype="float64"))
        fut = None if future_covariates is None else np.nan_to_num(np.asarray(future_covariates, dtype="float64"))
        med = self.forecast(ctx, fut, horizon)
        q = med[:, :, None] + np.array([-2.0, -1.0, 0.0, 1.0, 2.0])[None, None, :] * 5.0
        return SimpleNamespace(median=torch.from_numpy(med), quantiles=torch.from_numpy(q))


MARK = 123.456


class FlaggingRegression(RegressionEcho):
    """Logs t0's 'replaced non-finite values' warning for the decoy row of the window whose last context
    price is MARK (so the single-row re-run is flagged too)."""

    def predict(self, context, horizon, quantiles, future_covariates=None):
        if future_covariates is not None and future_covariates.shape[1] > 1:
            ctx = np.asarray(context, dtype="float64")
            T = ctx.shape[1]
            fut = np.asarray(future_covariates, dtype="float64")
            decoy_like = np.abs(np.nanmean(fut[:, -1, T:T + horizon], axis=1)) < 20
            if (decoy_like & (np.abs(ctx[:, -1] - MARK) < 1e-3)).any():
                logging.getLogger("t0.model.model").warning("t0 replaced 3 non-finite prediction values")
        return super().predict(context, horizon, quantiles, future_covariates)


def k3_setup(n_days: int | None = None):
    s = tpx.prices()
    days = pg.k3_days() if n_days is None else pg.k3_days()[:n_days]
    return s, days, px.build_price_windows(s, days)


def test_k3_rules_are_the_engine_ka2_thresholds():
    for k in ("planted_ratio_max", "decoy_ratio_min", "decoy_ratio_max", "shift_penalty_min",
              "noise_sd_share_of_p99", "seed"):
        assert pg.K3_RULES[k] == KA_RULES[k]
    assert pg.K3_RULES["no_sanitised_output"] is True and KA_RULES["version"] == "ka/2"
    assert pg.k3_days()[0] == date(2023, 10, 2) and pg.k3_days()[-1] == date(2023, 12, 3)


def test_k3_rule_evaluation_is_inclusive_and_needs_every_rule():
    a = pg.K3_ARMS

    def mae(base, planted, decoy, m1, p1):
        return {"t0_cal": base, a["planted"]: planted, a["decoy"]: decoy, a["shift_m1h"]: m1, a["shift_p1h"]: p1}

    ratios, checks = pg.k3_checks(mae(2.0, 1.0, 2.0, 1.5, 1.2), no_sanitised=True)
    assert ratios == {"planted_ratio": 0.5, "decoy_ratio": 1.0, "shift_penalty": 1.2} and all(checks.values())
    assert list(checks) == ["planted_helps", "decoy_does_not_help", "decoy_does_not_break", "aligned",
                            "no_sanitised_output"]
    # the thresholds themselves pass: 0.95, 0.98, 1.10 and 1.01
    for case in (mae(100.0, 95.0, 98.0, 200.0, 300.0), mae(100.0, 95.0, 110.0, 200.0, 300.0),
                 mae(200.0, 100.0, 200.0, 300.0, 101.0)):
        ratios, checks = pg.k3_checks(case, no_sanitised=True)
        assert all(checks.values()), (ratios, checks)
    for case, rule in ((mae(100.0, 95.1, 100.0, 200.0, 300.0), "planted_helps"),
                       (mae(100.0, 50.0, 97.9, 200.0, 300.0), "decoy_does_not_help"),
                       (mae(100.0, 50.0, 110.1, 200.0, 300.0), "decoy_does_not_break"),
                       (mae(200.0, 100.0, 200.0, 100.9, 300.0), "aligned")):
        _, checks = pg.k3_checks(case, no_sanitised=True)
        assert [k for k, v in checks.items() if not v] == [rule]
    _, checks = pg.k3_checks(mae(2.0, 1.0, 2.0, 1.5, 1.2), no_sanitised=False)
    assert [k for k, v in checks.items() if not v] == ["no_sanitised_output"]
    _, checks = pg.k3_checks({}, no_sanitised=True)
    assert not any(checks[k] for k in ("planted_helps", "decoy_does_not_help", "decoy_does_not_break", "aligned"))


def test_k3_grid_scale_and_rng_are_deterministic():
    s, days, windows = k3_setup(5)
    stamps = pg.k3_grid(windows)
    assert stamps[0] == windows[0].origin - 2159 * HOUR and stamps[-1] == windows[-1].origin + 27 * HOUR
    assert (np.diff(stamps.asi8) == HOUR.value).all()
    hours = pd.DatetimeIndex([t for d in days for t in px.day_hours(d)])
    p = s.reindex(hours).to_numpy()
    scale = pg.k3_scale(s, days)
    assert scale["p99"] == np.quantile(p, 0.99) and scale["sd"] == pd.Series(p).std(ddof=1)
    first = {c: pg.k3_covariates(s, windows, days, c) for c in pg.CONVENTIONS}
    again = {c: pg.k3_covariates(s, windows, days, c) for c in pg.CONVENTIONS}
    rng = np.random.default_rng(0)
    e = rng.normal(0.0, 0.05 * scale["p99"], len(stamps))  # e first ...
    decoy = rng.normal(0.0, scale["sd"], len(stamps))  # ... then the decoy
    for c in pg.CONVENTIONS:
        assert np.array_equal(first[c]["noise"], e)  # fresh default_rng(0) for each convention
        assert np.array_equal(first[c]["readings"]["decoy"].to_numpy(), decoy)  # never shifted
        for k in pg.K3_ARMS:
            assert first[c]["readings"][k].equals(again[c]["readings"][k])
            assert first[c]["covariates"][k].series.equals(again[c]["covariates"][k].series)


def test_k3_planted_signal_is_centred_on_the_hour_for_both_conventions():
    s, days, windows = k3_setup(5)
    stamps = pg.k3_grid(windows)
    p = s.reindex(stamps)
    p_prev, p_next = s.reindex(stamps - HOUR).to_numpy(), s.reindex(stamps + HOUR).to_numpy()
    zero = np.zeros(len(stamps))
    # noise-free: mean_preceding_hour returns p(h) itself, instant the centred kernel (1/4, 1/2, 1/4)
    mp, latest = pg.port(pg.planted_readings(s, stamps, "mean_preceding_hour", zero), stamps, "mean_preceding_hour")
    ok = np.isfinite(mp)
    assert ok[:-1].all() and np.array_equal(mp[ok], p.to_numpy()[ok]) and (latest == stamps + HOUR).all()
    ins, latest = pg.port(pg.planted_readings(s, stamps, "instant", zero), stamps, "instant")
    ok = np.isfinite(ins)
    np.testing.assert_allclose(ins[ok], ((p_prev + 2 * p.to_numpy() + p_next) / 4)[ok], rtol=0, atol=1e-9)
    assert (latest == stamps + HOUR).all()
    # the readings as the spec writes them, with the gate's own noise
    for conv in pg.CONVENTIONS:
        built = pg.k3_covariates(s, windows, days, conv)
        e = pd.Series(built["noise"], index=stamps)
        r = built["readings"]["planted"]
        h = stamps[100]
        if conv == "mean_preceding_hour":  # the reading stamped h + 1 h is p(h) + e(h + 1 h)
            assert r[h + HOUR] == s[h] + e[h + HOUR]
        else:  # the reading stamped h is (p(h - 1 h) + p(h)) / 2 + e(h)
            assert r[h] == (s[h - HOUR] + s[h]) / 2 + e[h]
        assert built["readings"]["shift_m1h"][h] == r[h + HOUR] and built["readings"]["shift_p1h"][h] == r[h - HOUR]
        # through the port: the planted cell is centred on its own hour, the shifts on the neighbours
        cells = {k: c.values(stamps) for k, c in built["covariates"].items()}
        if conv == "mean_preceding_hour":
            np.testing.assert_array_equal(cells["planted"][:-2], (p + e.shift(-1)).to_numpy()[:-2])
        scored = np.isin(stamps, pd.DatetimeIndex([t for d in days for t in px.day_hours(d)]))

        def best_lag(x):
            corr = {lag: np.corrcoef(x[scored], s.reindex(stamps + lag * HOUR).to_numpy()[scored])[0, 1]
                    for lag in (-1, 0, 1)}
            return max(corr, key=corr.get)

        assert best_lag(cells["planted"]) == 0
        assert best_lag(cells["shift_m1h"]) == 1 and best_lag(cells["shift_p1h"]) == -1
        assert np.isfinite(cells["planted"][:-2]).all()


def test_k3_oracle_covariates_arms_and_the_two_key_exemption():
    s, days, windows = k3_setup(3)
    built = pg.k3_covariates(s, windows, days, "instant")
    stamps = built["stamps"]
    for k, c in built["covariates"].items():
        assert c.oracle and c.name == f"k3_{k}" and c.description["convention"] == "instant"
        assert (c.issued_at(stamps) == stamps + HOUR + pd.Timedelta(days=5)).all()  # latest used + 5 days
    arms = pg.k3_arms(tpx.EchoT0(), built["covariates"])
    assert [a.name for a in arms] == ["t0_cal", "k3_oracle_planted", "k3_oracle_decoy", "k3_oracle_shift_m1h",
                                      "k3_oracle_shift_p1h"]
    assert [a.oracle for a in arms] == [False, True, True, True, True]
    assert all(len(a.covariates) == 2 and a.covariates[0].name == "holiday" for a in arms[1:])
    assert arms[0].covariates[0].name == "holiday" and len(arms[0].covariates) == 1
    with pytest.raises(AssertionError, match="two-key"):
        px.run_price_backtest(s, arms, windows)  # oracles run only under the exemption
    b = pg.k3_covariates(s, windows, days, "mean_preceding_hour")["covariates"]["planted"]
    assert (b.issued_at(stamps) == stamps + HOUR + pd.Timedelta(days=5)).all()
    assert b.description["port"] == "hourly_to_slots" and built["covariates"]["planted"].description[
        "port"] == "instant_to_slots"
    # the ports are the ones weather_p4 names (hourly_to_slots / instant_to_slots at +30 min)
    rv, _ = cov.hourly_to_slots(built["readings"]["planted"], stamps, 30)
    iv, _ = covs.instant_to_slots(built["readings"]["planted"], stamps, 30)
    np.testing.assert_array_equal(built["covariates"]["planted"].series.to_numpy(), iv)
    assert not np.array_equal(rv, iv, equal_nan=True)


def test_k3_passes_with_a_stand_in_that_uses_the_signal(tmp_path):
    s = tpx.prices()
    res = pg.run_k3(s, RegressionEcho(), cache=tmp_path)
    assert res["days"] == 63 and res["windows"]["built"] == 63 and res["pass"] is True
    assert res["smoke"] is False and "smoke_outcome" not in res and res["period_spec"] == ["2023-10-02", "2023-12-03"]
    assert list(res["conventions"]) == ["instant", "mean_preceding_hour"]
    for conv, r in res["conventions"].items():
        assert r["pass"] and all(r["checks"].values()), (conv, r)
        assert r["days_scored"] == 63 and r["planted_ratio"] < 0.95 and 0.98 <= r["decoy_ratio"] <= 1.10
        assert r["shift_penalty"] >= 1.01 and r["non_finite_warnings"] == 0
        assert r["noise_sd"] == pytest.approx(0.05 * r["p99"])
        assert len(r["files"]) == 2 and all((tmp_path / f.split("/")[-1]).exists() for f in r["files"])
        frame = pd.read_csv(r["files"][0])
        assert frame["method"].nunique() == 5 and frame["delivery_date"].nunique() == 63
    # MAE pooled over every scored hour of the common days, recomputed from the saved frame
    frame = pd.read_csv(res["conventions"]["instant"]["files"][0])
    t0 = frame[frame["method"] == "t0_cal"]
    assert res["conventions"]["instant"]["mae"]["t0_cal"] == pytest.approx((t0["y"] - t0["y_hat"]).abs().mean())
    again = pg.run_k3(s, RegressionEcho())
    assert again["conventions"]["instant"]["mae"] == res["conventions"]["instant"]["mae"]  # deterministic


def test_k3_fails_when_the_planted_signal_does_not_help():
    s, days, _ = k3_setup(7)
    res = pg.run_k3(s, tpx.EchoT0(), days=days)  # adds the covariate on top of its level: planted hurts
    assert res["pass"] is False and res["smoke_outcome"] == "fail"
    for r in res["conventions"].values():
        assert not r["checks"]["planted_helps"] and r["planted_ratio"] > 0.95 and r["checks"]["no_sanitised_output"]
        assert r["smoke_outcome"] == "fail" and r["pass"] is False


def test_k3_a_sanitised_arm_fails_the_gate():
    s, days, windows = k3_setup(14)
    marked = windows[5]
    s = s.copy()
    s[marked.origin] = MARK
    res = pg.run_k3(s, FlaggingRegression(), days=days)
    assert res["pass"] is False
    for r in res["conventions"].values():
        assert r["missing"]["k3_oracle_decoy"]["sanitised"] == [str(marked.delivery_date)]
        assert all(not v["sanitised"] for k, v in r["missing"].items() if k != "k3_oracle_decoy")
        assert [k for k, v in r["checks"].items() if not v] == ["no_sanitised_output"]
        assert r["days_scored"] == 13 and r["days_dropped"] == [str(marked.delivery_date)]
        assert r["non_finite_warnings"] >= 2  # the flagged batch and its single-row re-run
        assert r["smoke_outcome"] == "fail"


class BatchOnlyWarn(RegressionEcho):
    """Logs t0's 'replaced non-finite values' warning on every multi-row batch; its single-row re-runs are
    clean, so no window is NaN'd (missing['sanitised'] stays empty) although t0 did replace output."""

    def predict(self, context, horizon, quantiles, future_covariates=None):
        if np.asarray(context).shape[0] > 1:
            logging.getLogger("t0.model.model").warning("t0 replaced 3 non-finite prediction values")
        return super().predict(context, horizon, quantiles, future_covariates)


K3_SUBSET = 20


def test_k3_on_a_subset_of_its_days_is_never_a_pass():
    """gates.K3.period: the rules may all hold on a subset, but that is a smoke, never a K3 pass."""
    s, days, _ = k3_setup(K3_SUBSET)
    res = pg.run_k3(s, RegressionEcho(), days=days)
    assert res["pass"] is False and res["smoke"] == pg.SMOKE_K3 == "smoke: not a K3 result"
    assert res["smoke_outcome"] == "pass" and res["days"] == K3_SUBSET
    for conv, r in res["conventions"].items():
        assert all(r["checks"].values()) and r["smoke_outcome"] == "pass" and r["pass"] is False, conv
        assert r["non_finite_warnings"] == 0 and r["days_scored"] == K3_SUBSET


def test_k3_a_replacement_warning_fails_even_when_no_window_is_sanitised():
    """gates.K3.pass 't0 replaced no non-finite output in any K3 arm' (engine: watcher.count == 0): a warning
    in a batch whose single-row re-runs are clean still fails no_sanitised_output."""
    s, days, _ = k3_setup(K3_SUBSET)
    res = pg.run_k3(s, BatchOnlyWarn(), days=days)
    assert res["pass"] is False and res["smoke_outcome"] == "fail"
    for conv, r in res["conventions"].items():
        assert all(not v["sanitised"] for v in r["missing"].values()) and r["days_scored"] == K3_SUBSET, conv
        assert r["non_finite_warnings"] > 0 and r["checks"]["no_sanitised_output"] is False
        assert [k for k, v in r["checks"].items() if not v] == ["no_sanitised_output"]
        assert r["smoke_outcome"] == "fail" and r["pass"] is False


def test_k3_only_exactly_the_period_days_is_a_k3_run():
    """Which day lists count as K3 (cheap: every target incomplete, so no window is ever forecast)."""
    s = tpx.prices().copy()
    for d in pg.k3_days():
        s[px.day_hours(d)[3]] = np.nan
    full = pg.run_k3(s, RegressionEcho())
    assert full["smoke"] is False and "smoke_outcome" not in full and full["error"] == "no K3 window"
    assert pg.run_k3(s, RegressionEcho(), days=pg.k3_days())["smoke"] is False
    for days in (pg.k3_days()[:-1], pg.k3_days()[1:], pg.k3_days()[::-1], pg.k3_days() + [date(2023, 12, 4)]):
        res = pg.run_k3(s, RegressionEcho(), days=days)
        assert res["smoke"] == pg.SMOKE_K3 and res["pass"] is False and res["smoke_outcome"] == "fail"


def test_k3_with_no_scorable_day_fails():
    s, days, _ = k3_setup(3)
    s = s.copy()
    for d in days:
        s[px.day_hours(d)[3]] = np.nan  # every target incomplete: no window
    res = pg.run_k3(s, RegressionEcho(), days=days)
    assert res["pass"] is False and res["error"] == "no K3 window" and res["windows"]["incomplete_target"] == 3
