"""Tests for Experiment 3, the t0 strengths probe.

Offline only: t0 is a stub that echoes its inputs (last context value, plus the
horizon covariates, plus fixed quantile offsets), so every test can say exactly
what reached the model.  Every new method is poisoned: rewriting or blanking
anything after an origin must not move its forecast, and a change before the
origin must (so the test could see a leak).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_covariates as rc
import run_probes
import test_covariates as tc
from solarbench import covariates as cov
from solarbench import odre
from solarbench import probes as pr
from solarbench.backtest import build_windows, run_backtest
from solarbench.data import STEP
from solarbench.forecasters import Prediction, T0Forecaster, WeatherSlotRatio, night_zero_variant

CTX = 48 * 10


class QuantModel:
    """t0 stand-in: last context value (+ horizon covariates) and quantiles at fixed offsets."""

    def __init__(self):
        self.calls = []

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch

        ctx = np.nan_to_num(np.asarray(torch.as_tensor(context), dtype="float64"))
        med = np.repeat(ctx[..., -1:], horizon, axis=-1)
        if future_covariates is not None:
            fut = np.nan_to_num(np.asarray(torch.as_tensor(future_covariates), dtype="float64"))
            med = med + fut[:, :, ctx.shape[-1]:ctx.shape[-1] + horizon].sum(axis=1)
        q = med[..., None] + (np.asarray(quantiles) - 0.5)[None, :] * 100.0
        self.calls.append({"shape": ctx.shape, "horizon": horizon, "future": future_covariates is not None})
        return SimpleNamespace(median=torch.as_tensor(med), quantiles=torch.as_tensor(q))


def stub_t0(name, *, context=CTX, covariates=(), keep=True, model=None):
    return T0Forecaster(context_steps=context, name=name, covariates=tuple(covariates), keep_quantiles=keep,
                        quantiles=pr.T0_LEVELS if keep else (0.1, 0.5, 0.9),
                        fixed_horizon=cov.COV_HORIZON if covariates else None, _model=model or QuantModel())


class ConstBase:
    """A base model that forecasts a constant and reads nothing."""

    name = "const"

    def __init__(self, value=100.0):
        self.value = value

    def spec(self):
        return {"class": "ConstBase", "value": self.value}

    def predict(self, series, windows):
        return [Prediction(values=np.full(len(w.targets), self.value), max_source_time=w.origin,
                           source_latest=pd.DatetimeIndex([w.origin] * len(w.targets)),
                           source_earliest=pd.DatetimeIndex([w.origin] * len(w.targets)),
                           n_sources=np.ones(len(w.targets), dtype=int)) for w in windows]


def day_ramp(start="2024-01-01", end="2024-08-31 23:30") -> pd.Series:
    """y = 100 + (UTC day number): past errors of a constant-100 base are known exactly."""
    index = pd.date_range(start, end, freq=STEP, tz="UTC")
    days = (index.normalize() - index[0].normalize()).days
    return pd.Series(100.0 + np.asarray(days, dtype="float64"), index=index)


def regional_frame(series: pd.Series) -> pd.DataFrame:
    w = np.linspace(0.5, 1.5, 12)
    return pd.DataFrame({name: series * wi / w.sum() for name, wi in zip(cov.REGION_POINTS, w)})


# ------------------------------------------------------------- frozen spec


def test_probes_are_frozen_and_well_formed():
    assert 1 <= len(pr.PROBES) <= 4
    assert [p.id for p in pr.PROBES] == ["P1", "P2", "P3", "P4"]
    simple = {"wx_ratio", "wx_ratio_eq_night_zero", "ewma", "best_simple_2023"}
    for p in pr.PROBES:
        assert p.question and p.t0_arm and p.success and p.days
        assert p.metric in ("mae", "pinball")
        assert p.comparator in simple, f"{p.id} must be compared with the best simple method"
        assert p.t0_arm.startswith("t0") or "t0res" in p.t0_arm
    assert pr.T0_LEVELS == (0.1, 0.25, 0.5, 0.75, 0.9)
    assert set(pr.P4_CANDIDATES) >= {"ewma", "prev_week", "weekday_mean_4w"}


def test_covariate_slice_specs_are_unchanged():
    arm = T0Forecaster(context_steps=4320, fixed_horizon=73, covariates=(cov.GeometryCovariate(tc.EQUAL, 0),))
    assert "keep_quantiles" not in arm.spec()
    assert "keep_quantiles" in stub_t0("x").spec()


# ------------------------------------------------------------ utilities


def test_easter_and_french_holidays():
    assert pr.easter(2024) == date(2024, 3, 31) and pr.easter(2023) == date(2023, 4, 9)
    h = pr.french_holidays(2024)
    assert len(h) == 11 and {date(2024, 4, 1), date(2024, 5, 9), date(2024, 5, 20), date(2024, 7, 14)} <= h
    times = pd.date_range("2024-07-13 22:00", "2024-07-15 22:00", freq=STEP, tz="UTC", inclusive="left")
    v = pr.HolidayCovariate().values(times)
    local = times.tz_convert("Europe/Paris")
    assert (v[local.date == date(2024, 7, 14)] == 1).all() and (v[local.date == date(2024, 7, 15)] == 0).all()
    assert pr.HolidayCovariate().issued_at(times).isna().all()


@pytest.mark.parametrize("day,slots", [(date(2024, 3, 31), 46), (date(2024, 10, 27), 50), (date(2024, 6, 1), 48)])
def test_past_windows_come_from_the_calendar(day, slots):
    w = pr.past_windows([day])[0]
    assert len(w.targets) == slots
    assert w.origin.tz_convert("Europe/Paris").hour == 12 and w.origin < w.targets[0]


def test_pinball_by_hand():
    loss = pr.pinball(np.array([10.0]), np.array([[8.0, 10.0, 13.0]]), (0.1, 0.5, 0.9))
    assert loss[0] == pytest.approx((0.2 + 0.0 + 0.3) / 3)


def test_quantiles_flow_through_night_zero_and_the_backtest():
    series = tc.solar_series("2024-01-01", "2024-07-31 23:30")
    windows = tc.windows_for(series, "2024-06-10", "2024-06-12")
    df = run_backtest(series, [stub_t0("t0"), night_zero_variant("t0")], windows)
    for col in ("q10", "q25", "q50", "q75", "q90"):
        assert col in df.columns and (df[col] >= 0).all()
    nz = df.loc[df["method"] == "t0_night_zero"]
    from solarbench.astro import dark_mask
    mask = dark_mask(pd.DatetimeIndex(nz["target_time"]))
    assert (nz.loc[mask, ["q10", "q90"]] == 0).all().all()


# ------------------------------------------- by-hand checks of new methods


def test_empirical_quantiles_by_hand():
    y = day_ramp()
    w = tc.windows_for(y, "2024-06-20", "2024-06-20")[0]
    pred = pr.EmpiricalQuantiles(ConstBase(), name="eq").predict(y, [w])[0]
    i = int(np.flatnonzero(w.targets == pd.Timestamp("2024-06-20 06:00", tz="UTC"))[0])
    d = (w.targets[i].normalize() - y.index[0].normalize()).days
    errors = d - np.arange(1, 29)  # sources on the previous 28 days, all before the gate
    assert pred.quantiles[i] == pytest.approx(100 + np.quantile(errors, pr.T0_LEVELS))
    assert (pred.values == 100).all() and pred.source_latest.max() <= w.origin
    j = int(np.flatnonzero(w.targets == pd.Timestamp("2024-06-20 15:00", tz="UTC"))[0])
    later = d - np.arange(2, 30)  # the afternoon of D-1 is after the gate: skipped
    assert pred.quantiles[j] == pytest.approx(100 + np.quantile(later, pr.T0_LEVELS))


def test_bias_corrected_by_hand():
    y = day_ramp()
    w = tc.windows_for(y, "2024-06-20", "2024-06-20")[0]
    pred = pr.BiasCorrected(ConstBase(), name="bias").predict(y, [w])[0]
    i = int(np.flatnonzero(w.targets == pd.Timestamp("2024-06-20 06:00", tz="UTC"))[0])
    d = (w.targets[i].normalize() - y.index[0].normalize()).days
    weights = 0.7 ** np.arange(14)
    assert pred.values[i] == pytest.approx(100 + np.dot(weights, d - np.arange(1, 15)) / weights.sum())


def test_residual_t0_forecasts_the_base_models_errors():
    y = day_ramp()
    w = tc.windows_for(y, "2024-06-20", "2024-06-20")[0]
    model = QuantModel()
    pred = pr.ResidualT0(ConstBase(), stub_t0("inner", model=model), name="res").predict(y, [w])[0]
    r_origin = y.loc[w.origin] - 100.0  # the last residual the stub sees
    assert np.allclose(pred.values, 100.0 + r_origin)
    assert np.allclose(pred.quantiles[:, 2], pred.values)
    assert model.calls[0]["shape"] == (1, CTX)


def test_regional_joint_sums_regions_and_shapes_the_call():
    series = tc.solar_series("2024-01-01", "2024-07-31 23:30")
    regional = regional_frame(series)
    w = tc.windows_for(series, "2024-06-10", "2024-06-11")
    for joint, shape in ((True, (2, 12, CTX)), (False, (24, CTX))):
        model = QuantModel()
        f = pr.T0JointForecaster(regional, CTX, joint, "j", _t0=T0Forecaster(context_steps=CTX, _model=model))
        preds = f.predict(series, w)
        assert model.calls[0]["shape"] == shape
        assert np.allclose(preds[0].values, regional.loc[w[0].origin].sum())


def test_weekday_mean_uses_the_same_weekday():
    y = day_ramp()
    w = tc.windows_for(y, "2024-06-20", "2024-06-20")[0]
    pred = pr.weekday_mean_4w().predict(y, [w])[0]
    d = (w.targets[0].normalize() - y.index[0].normalize()).days
    assert pred.values[0] == pytest.approx(100 + d - 7 * 2.5)


# ------------------------------------------------------------ poisoning


def _poisoned(series: pd.Series | pd.DataFrame, origin, kind):
    out = series.copy()
    after = out.index > origin
    out.loc[after] = out.loc[after] * -7.5 + 1234.5 if kind == "affine" else np.nan
    return out


def _same(a: Prediction, b: Prediction) -> bool:
    ok = np.array_equal(a.values, b.values, equal_nan=True)
    if a.quantiles is not None:
        ok = ok and np.array_equal(a.quantiles, b.quantiles, equal_nan=True)
    return ok


def _new_methods():
    wx = tc.weather_cov()
    geo = cov.GeometryCovariate(tc.EQUAL, 15)
    return [
        pr.EmpiricalQuantiles(WeatherSlotRatio(wx), name="wx_ratio_eq"),
        pr.BiasCorrected(WeatherSlotRatio(wx), name="wx_ratio_bias"),
        pr.ResidualT0(WeatherSlotRatio(wx), stub_t0("inner", covariates=(geo, wx)), name="wx_ratio_t0res"),
        stub_t0("t0_cal", covariates=(pr.HolidayCovariate(),)),
        stub_t0("t0_wx", covariates=(geo, wx)),
        pr.weekday_mean_4w(),
        pr.ReferenceForecast(tc.solar_series("2024-01-01", "2024-12-31 23:30") * 0.9, name="rte_j1"),
    ]


@pytest.mark.parametrize("kind", ["affine", "nan"])
def test_every_new_method_ignores_everything_after_the_origin(kind):
    series = tc.solar_series("2023-09-01", "2024-12-31 23:30")
    windows = tc.windows_for(series, "2024-06-10", "2024-06-12") + tc.windows_for(series, "2024-10-26", "2024-10-28")
    for method in _new_methods():
        for w in windows:
            clean = method.predict(series, [w])[0]
            dirty = method.predict(_poisoned(series, w.origin, kind), [w])[0]
            assert _same(clean, dirty), f"{method.name} moved when only post-origin data changed ({kind}, {w.delivery_date})"
            if clean.covariate_issued_latest is not None and pd.notna(clean.covariate_issued_latest):
                assert clean.covariate_issued_latest <= w.origin, method.name


def test_error_based_methods_do_see_a_change_before_the_origin():
    series = tc.solar_series("2023-09-01", "2024-12-31 23:30")
    w = tc.windows_for(series, "2024-06-12", "2024-06-12")[0]
    for method in _new_methods()[:3]:
        clean = method.predict(series, [w])[0]
        moved = series.copy()
        moved.loc[w.origin - pd.Timedelta(days=1, hours=1): w.origin - pd.Timedelta(hours=1)] *= 1.7
        assert not _same(clean, method.predict(moved, [w])[0]), f"{method.name} is blind to its own history"


@pytest.mark.parametrize("kind", ["affine", "nan"])
@pytest.mark.parametrize("joint", [True, False])
def test_regional_forecast_ignores_the_future_of_every_region(kind, joint):
    series = tc.solar_series("2024-01-01", "2024-08-31 23:30")
    regional = regional_frame(series)
    for w in tc.windows_for(series, "2024-06-10", "2024-06-11"):
        f = pr.T0JointForecaster(regional, CTX, joint, "j", _t0=T0Forecaster(context_steps=CTX, _model=QuantModel()))
        clean = f.predict(series, [w])[0]
        dirty_frame = pr.T0JointForecaster(_poisoned(regional, w.origin, kind), CTX, joint, "j",
                                           _t0=T0Forecaster(context_steps=CTX, _model=QuantModel()))
        assert np.array_equal(clean.values, dirty_frame.predict(_poisoned(series, w.origin, kind), [w])[0].values)
        moved = regional.copy()
        moved.loc[w.origin] *= 2
        seen = pr.T0JointForecaster(moved, CTX, joint, "j", _t0=T0Forecaster(context_steps=CTX, _model=QuantModel()))
        assert not np.array_equal(clean.values, seen.predict(series, [w])[0].values)


def test_new_methods_pass_the_backtest_contract():
    series = tc.solar_series("2023-09-01", "2024-12-31 23:30")
    windows = tc.windows_for(series, "2024-06-10", "2024-06-14")
    df = run_backtest(series, _new_methods(), windows)
    assert df["delivery_date"].nunique() == 5
    assert (df.loc[df["cov_issued_latest"].notna(), "cov_issued_latest"] <= df.loc[df["cov_issued_latest"].notna(), "origin"]).all()


# ------------------------------------------------------------ ODRÉ loaders


def test_odre_loaders_and_seal(tmp_path, monkeypatch):
    stamps = pd.date_range("2024-01-01", periods=8, freq="15min", tz="UTC")
    rows = ["date_heure;perimetre;nature;consommation"] + [
        f"{t.isoformat()};France;Données définitives;{50000 + i}" for i, t in enumerate(stamps)]
    (tmp_path / "n.csv").write_text("\n".join(rows), encoding="utf-8")
    s = odre.load_column(tmp_path / "n.csv", "consommation")
    assert len(s) == 4 and s.iloc[0] == 50000 and s.iloc[1] == 50002  # 30-minute grid rows only
    reg = ["date_heure;libelle_region;nature;solaire"] + [
        f"{t.isoformat()};{r};Données définitives;{k}" for t in stamps[::2] for k, r in enumerate(["A", "B"])]
    (tmp_path / "r.csv").write_text("\n".join(reg), encoding="utf-8")
    frame = odre.load_regional(tmp_path / "r.csv", regions=["A", "B"])
    assert list(frame.columns) == ["A", "B"] and frame["B"].eq(1).all()

    def boom(*a, **k):
        raise AssertionError("network touched")

    monkeypatch.setattr(odre.requests, "get", boom)
    from solarbench.weather import SealedDataError
    with pytest.raises(SealedDataError):
        odre.fetch_columns(odre.NATIONAL, ["date_heure"], "2024-06-01", "2025-01-02", tmp_path)


# --------------------------------------------------------- end to end


def _stub_probe_inputs(monkeypatch, tmp_path):
    solar = tc.solar_series("2023-01-01", "2024-12-31 23:30")
    index = pd.date_range("2022-06-01", "2024-12-31 23:30", freq=STEP, tz="UTC")
    local = index.tz_convert("Europe/Paris")
    load = pd.Series(50_000 + 8_000 * np.sin((local.hour + local.minute / 60) / 24 * 2 * np.pi)
                     - 6_000 * (local.dayofweek >= 5)
                     + np.random.default_rng(1).normal(0, 800, len(index)), index=index)
    monkeypatch.setattr(run_probes, "load_solar", lambda args: solar)
    monkeypatch.setattr(run_probes, "load_consumption", lambda args: (load, load * 1.01))
    monkeypatch.setattr(run_probes, "load_regional", lambda args: regional_frame(solar))
    monkeypatch.setattr(rc, "build_covariates", lambda args: (cov.GeometryCovariate(tc.EQUAL, 15), tc.weather_cov(), None))
    monkeypatch.setattr(rc, "_require_frozen", lambda: None)
    monkeypatch.setattr(run_probes, "TEST_START", date(2024, 6, 10))
    monkeypatch.setattr(run_probes, "TEST_END", date(2024, 6, 23))
    monkeypatch.setattr(run_probes, "SELECT_START", date(2023, 3, 1))
    monkeypatch.setattr(run_probes, "SELECT_END", date(2023, 3, 20))
    monkeypatch.setattr(pr, "MIN_P3_DAYS", 5)
    model = QuantModel()

    def load_model(self):
        self._model = self._model or model
        return self._model

    monkeypatch.setattr(T0Forecaster, "load", load_model)
    return model


def test_check_end_to_end_offline(monkeypatch, tmp_path):
    _stub_probe_inputs(monkeypatch, tmp_path)
    assert run_probes.main(["check", "--context-days", "10", "--results-dir", str(tmp_path)]) == 0
    out = json.loads((tmp_path / "check.json").read_text())
    assert out["P1_P2_days"] == 14 and out["P3_days"] == 14 and out["P4_days"] == 14


def test_run_end_to_end_offline(monkeypatch, tmp_path):
    _stub_probe_inputs(monkeypatch, tmp_path)
    assert run_probes.main(["run", "--context-days", "10", "--results-dir", str(tmp_path)]) == 0
    table = pd.read_csv(tmp_path / "probes.csv")
    primary = table.loc[table["role"] == "primary"]
    assert list(primary["probe"]) == ["P1", "P2", "P3", "P4"]
    assert primary["p_holm"].notna().all() and primary["won"].notna().all()
    assert (primary["p_holm"] >= primary["p_one_sided"] - 1e-12).all()
    p4 = table.loc[(table["probe"] == "P4") & (table["role"] == "primary")].iloc[0]
    meta = json.loads((tmp_path / "run_meta.json").read_text())
    assert p4["reference"] == meta["probes"]["P4"]["best_simple_2023"]
    assert meta["probes"]["P4"]["best_simple_2023"] in pr.P4_CANDIDATES
    cover = pd.read_csv(tmp_path / "coverage.csv")
    assert set(cover["method"]) == {"t0_wx_night_zero", "wx_ratio_eq_night_zero", "wx_ratio_t0res_night_zero"}
    assert "Experiment 3" in (tmp_path / "summary.md").read_text()
