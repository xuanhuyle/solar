"""Experiment 4's leak controls as the runner applies them (price_leak, price_run): the variate whitelist, the
per-arm covariate refusal, the in-run check's arm list, lear_ens_eq as one object, the tracked K1/K2 logs and
the selection's dropped days (offline: synthetic prices and the stand-in t0 of tests/test_price_exp.py)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import date, timedelta
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from solarbench import covariates as cov
from solarbench import price_exp as px
from solarbench import price_leak as lk
from solarbench import price_run as pr_
from solarbench import price_spec as ps
from solarbench.forecasters import Prediction
from test_price_exp import EchoT0, prices

D = date(2024, 1, 10)  # a Wednesday
P4_FIRST = date(2024, 1, 9)  # stands in for AVAIL.p4_first_day (not an origin here)


def weather(series: pd.Series) -> tuple:
    grid = pd.date_range(series.index[0], series.index[-1] + pd.Timedelta(days=2), freq="1h", tz="UTC")
    rng = np.random.default_rng(3)
    wx = pd.Series(rng.normal(10, 5, len(grid) + 1),
                   index=pd.date_range(grid[0], periods=len(grid) + 1, freq="1h", tz="UTC"))
    return px.weather_covariates(wx, wx.abs(), grid)


@pytest.fixture(scope="module")
def s():
    return prices()


@pytest.fixture(scope="module")
def wx(s):
    return weather(s)


def arms_for(wx, *, model=None, best="naive_std") -> pr_.Arms:
    return pr_.build_arms(best, model or EchoT0(), weather=wx, with_lear=False)


def realised_radiation(series: pd.Series) -> cov.SeriesCovariate:
    """A covariate under a whitelisted name built from the price series itself, with no issue times."""
    return cov.SeriesCovariate(name="wx_radiation", series=series.copy(), issued=None)


# ---------------------------------------------------------------------------- L1 variate whitelist


def test_the_real_arms_pass_the_variate_whitelist(wx):
    arms = arms_for(wx)
    for arm in (arms.t0, arms.t0_cal, arms.t0_cal_strict, arms.t0_cal_wx):
        res = lk.variate_whitelist(arm, wx)
        assert res and all(res.values()), (arm.name, res)
    assert lk.variate_whitelist(arms.t0_cal_wx, wx)["weather_is_loaded"]
    assert [c.name for c in arms.t0_cal_wx.covariates] == ps.PRICE_SPEC["weather_p4"]["covariates"]


def test_a_realised_series_under_a_whitelisted_name_is_refused(s, wx):
    arms = arms_for(wx)
    temp, _ = wx
    bad = px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), temp, realised_radiation(s))).use_model(EchoT0())
    res = lk.variate_whitelist(bad)
    assert res["names"] and not res["weather_issue_bounded"]
    assert not all(lk.variate_whitelist(bad, wx).values())
    # the other ways out of the whitelist
    oracle = cov.SeriesCovariate(name="wx_radiation", series=wx[1].series, issued=wx[1].issued, oracle=True)
    for arm, key in [
        (px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), temp, oracle)), "no_oracle"),
        (px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), *weather(s))), "weather_is_loaded"),
        (px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), wx[1], temp)), "names"),
        (px.PriceT0Forecaster("t0_cal", covariates=(px.holiday(), temp)), "names"),
        (px.PriceT0Forecaster("t0", covariates=(px.holiday(),)), "names"),
        (px.PriceT0Forecaster("t0_cal_strict", covariates=()), "names"),
        (px.PriceT0Forecaster("t0_cal", covariates=(cov.SeriesCovariate("holiday", s.copy()),)), "holiday_is_calendar"),
        (px.PriceT0Forecaster("t0_extra", covariates=()), "known_arm"),
    ]:
        assert not lk.variate_whitelist(arm, wx)[key], (arm.name, key)
    assert arms.t0_cal_wx.covariates[1] is wx[0]


def test_forecast_all_refuses_an_unlisted_variate_before_forecasting(s, wx, monkeypatch):
    model = EchoT0()
    arms = arms_for(wx, model=model)
    arms.t0_cal_wx = px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), wx[0], realised_radiation(s))
                                          ).use_model(model)
    monkeypatch.setattr(pr_, "PERIODS", {**pr_.PERIODS, "test": ["2024-01-08", "2024-01-09"],
                                         "p4_days": ["2024-01-08", "2024-01-09"]})
    with pytest.raises(AssertionError, match="variate whitelist"):
        pr_.forecast_all(s, arms, p4_first_day=date(2024, 1, 8), k3_passed=True)
    assert model.calls == 0
    arms = arms_for(wx, model=model)  # the real arms, but weather that is not the loaded tuple
    with pytest.raises(AssertionError, match="variate whitelist"):
        pr_.forecast_all(s, arms, p4_first_day=date(2024, 1, 8), k3_passed=True, weather=weather(s))
    assert model.calls == 0
    df, _ = pr_.forecast_all(s, arms, p4_first_day=date(2024, 1, 8), k3_passed=True, weather=wx)
    assert model.calls > 0 and "t0_cal_wx" in set(df["method"])


def test_the_in_run_check_fails_on_an_unlisted_variate(s, wx, monkeypatch):
    monkeypatch.setattr(ps, "TEST_ORIGINS", [])
    arms = arms_for(wx)
    arms.t0_cal = px.PriceT0Forecaster("t0_cal", covariates=(px.holiday(), realised_radiation(s))).use_model(EchoT0())
    out = pr_.in_run_leak_check(s, arms, p4_first_day=P4_FIRST, k3_passed=False, k1_passed=False, weather=wx)
    assert not out["pass"] and not all(out["whitelist"]["whitelist:t0_cal"].values())
    assert set(out["whitelist"]) == {"whitelist:t0", "whitelist:t0_cal", "whitelist:t0_cal_strict"}


# ---------------------------------------------------------------------------- L3 per-arm refusal


def test_the_per_arm_covariate_refusal(s, wx, monkeypatch):
    arms = arms_for(wx)
    w = px.build_price_windows(s, [D], require_target=False)[0]
    ws = px.build_price_windows(s, [D], strict=True, require_target=False)[0]
    missing = arms.t0_cal.missing
    assert lk.covariate_refusal_arm(arms.t0_cal, s, w)
    assert lk.covariate_refusal_arm(arms.t0_cal_strict, s, ws)
    assert lk.covariate_refusal_arm(arms.t0_cal_wx, s, w)
    assert arms.t0_cal.missing is missing and len(arms.t0_cal.covariates) == 1  # the arm itself is untouched
    orig = px.PriceT0Forecaster.block

    def block_without_issue_times(self, origin):  # a mutation: the arm stops reporting its issue times
        return orig(self, origin)[0], pd.NaT

    monkeypatch.setattr(px.PriceT0Forecaster, "block", block_without_issue_times)
    assert lk.covariate_refusal(w)  # the arm-less control cannot see it
    assert not lk.covariate_refusal_arm(arms.t0_cal, s, w)
    assert not lk.covariate_refusal_arm(arms.t0_cal_strict, s, ws)


# ---------------------------------------------------------------------------- the in-run check's arm list


@dataclass
class StubLear:
    """A cheap stand-in for lear_ens: each hour of D is the mean of D-1 and D-2 at that UTC hour plus the
    mean of D-1's afternoon; the last price read is D-1's last hour."""

    name: str = "lear_ens"
    processes: int = 1
    logs: dict = field(default_factory=dict)
    calls: int = 0

    def predict(self, series, windows):
        self.calls += 1
        out = []
        for w in windows:
            prev = px.day_hours(w.delivery_date - timedelta(days=1))
            aft = series.reindex(lk.local_hours(w.delivery_date - timedelta(days=1), range(13, 24))).mean()
            v = [(series.get(t - pd.Timedelta(days=1), np.nan) + series.get(t - pd.Timedelta(days=2), np.nan)) / 2
                 + 0.1 * aft for t in w.targets]
            out.append(Prediction(values=np.asarray(v, dtype="float64"), max_source_time=prev[-1],
                                  source_latest=pd.DatetimeIndex([prev[-1]] * len(w.targets))))
        self.logs = {56: SimpleNamespace(forecast_days=len(windows), no_forecast={}, dropped_rows=0,
                                         scale_fallbacks=self.calls)}
        return out


class SpyEQ(px.PriceEmpiricalQuantiles):
    calls = 0

    def predict(self, series, windows):
        type(self).calls += 1
        return super().predict(series, windows)


def test_build_arms_makes_lear_ens_eq_once(wx):
    arms = pr_.build_arms("naive_std", EchoT0(), weather=wx, with_lear=True, lear_processes=3)
    assert isinstance(arms.lear_eq, px.PriceEmpiricalQuantiles) and arms.lear_eq.name == "lear_ens_eq"
    assert isinstance(arms.lear_eq.base, px.LearEnsemble) and arms.lear_eq.base.processes == 3
    assert arms.lear_eq.base is not arms.lear and arms.lear.processes == 3
    assert arms_for(wx).lear_eq is None


def test_the_in_run_check_runs_every_named_control_on_every_named_arm(s, wx, monkeypatch):
    monkeypatch.setattr(ps, "TEST_ORIGINS", [str(D)])
    arms = arms_for(wx)
    arms.lear, SpyEQ.calls = StubLear(), 0
    arms.lear_eq = SpyEQ(base=StubLear(), name="lear_ens_eq")
    out = pr_.in_run_leak_check(s, arms, p4_first_day=P4_FIRST, k3_passed=True, k1_passed=True, weather=wx)
    res = out["origins"][str(D)]
    # L1: the whitelist of every t0 arm checked
    assert set(out["whitelist"]) == {f"whitelist:{a}" for a in ("t0", "t0_cal", "t0_cal_strict", "t0_cal_wx")}
    assert all(all(v.values()) for v in out["whitelist"].values())
    # L2: the error quantiles themselves
    assert res["legal_d1_moves_eq_error_quantiles"] is True and "legal_d1_moves_eq_bands" not in res
    # L3: the refusal through each arm with a covariate
    for a in ("t0_cal", "t0_cal_strict", "t0_cal_wx"):
        assert res[f"covariate_refusal:{a}"] is True, a
    # L4: the comparators' context end
    assert res["context_end:best_simple_2023"] is True and res["context_end:best_simple_2023_strict"] is True
    # L6: lear_ens_eq poisoned, the Arms object itself
    assert res["poison:lear_ens_eq"] == {"affine": True, "nan": True} and SpyEQ.calls >= 3
    assert res["poison:lear_ens"] == {"affine": True, "nan": True}
    # L5: every control that names t0_cal_wx at its own first day
    p4 = out["origins"][f"p4_first_day:{P4_FIRST}"]
    assert {"poison", "weather", "legal_afternoon", "legal_d2", "context_end", "covariate_refusal"} <= set(p4)
    assert p4["legal_d2"] is True and p4["context_end"] is True and p4["covariate_refusal"] is True
    assert p4["pass"] and res["pass"] and out["pass"], {k: v for k, v in res.items() if v is not True}


def test_the_p4_first_day_block_counts_its_new_controls(s, wx, monkeypatch):
    monkeypatch.setattr(ps, "TEST_ORIGINS", [])
    arms = arms_for(wx)
    orig = px.PriceT0Forecaster.block

    def block_without_issue_times(self, origin):
        return orig(self, origin)[0], pd.NaT

    monkeypatch.setattr(px.PriceT0Forecaster, "block", block_without_issue_times)
    out = pr_.in_run_leak_check(s, arms, p4_first_day=P4_FIRST, k3_passed=True, k1_passed=False, weather=wx)
    p4 = out["origins"][f"p4_first_day:{P4_FIRST}"]
    assert p4["covariate_refusal"] is False and not p4["pass"] and not out["pass"]


def test_forecast_all_scores_the_checked_lear_ens_eq_and_logs_it(s, wx, monkeypatch):
    monkeypatch.setattr(pr_, "PERIODS", {**pr_.PERIODS, "test": ["2024-01-08", "2024-01-12"]})
    arms = arms_for(wx)
    arms.lear, SpyEQ.calls = StubLear(), 0
    arms.lear_eq = SpyEQ(base=StubLear(), name="lear_ens_eq")
    df, info = pr_.forecast_all(s, arms, p4_first_day=P4_FIRST, k3_passed=False, weather=wx)
    assert SpyEQ.calls == 1 and {"lear_ens", "lear_ens_eq"} <= set(df["method"])
    assert np.isfinite(df.loc[df["method"] == "lear_ens_eq", "q50"]).any()
    test_days = px.days_between("2024-01-08", "2024-01-12")
    hist_days = {d - timedelta(days=k) for d in test_days for k in range(1, arms.lear_eq.lookback + 2)}
    assert info["lear_eq_logs"] == {"56": {"forecast_days": len(hist_days), "no_forecast": {}, "dropped_rows": 0,
                                           "scale_fallbacks": 2}}  # its last pass: the bands' history windows
    assert info["lear_logs"]["56"]["forecast_days"] == 5
    arms.lear_eq = None
    with pytest.raises(ValueError, match="lear_ens_eq"):
        pr_.forecast_all(s, arms, p4_first_day=P4_FIRST, k3_passed=False, weather=wx)


# ---------------------------------------------------------------------------- K1 / K2 logs


def test_the_k1_and_k2_logs_are_tracked_paths():
    for path, name in ((pr_.K1_LOG, "k1_attempts.jsonl"), (pr_.K2_LOG, "k2_attempts.jsonl")):
        assert path == pr_.ROOT / "docs" / "experiment_4" / name
        rc = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=pr_.ROOT).returncode
        assert rc == 1, f"{path} is git-ignored"


def test_k1_status_records_the_log_it_read_and_k2_attempts_reads_its_log(tmp_path, monkeypatch):
    monkeypatch.setattr(pr_, "K1_LOG", tmp_path / "k1.jsonl")
    monkeypatch.setattr(pr_, "K2_LOG", tmp_path / "k2.jsonl")
    st = pr_.k1_status("abc")
    assert st["log_present"] is False and st["log_sha256"] is None and st["attempts"] == 0
    assert pr_.k2_attempts() == []
    (tmp_path / "k1.jsonl").write_bytes(b"")
    st = pr_.k1_status("abc")
    assert st["log_present"] is True and st["log_sha256"] == hashlib.sha256(b"").hexdigest()
    body = (json.dumps({"run_id": "1", "pass": True, "lear_sha256": "abc", "counts_as_attempt": True}) + "\n").encode()
    (tmp_path / "k1.jsonl").write_bytes(body)
    st = pr_.k1_status("abc")
    assert st["passed"] and st["log_sha256"] == hashlib.sha256(body).hexdigest()
    rows = [{"run_id": "a", "pass": False}, {"run_id": "b", "pass": True}]
    (tmp_path / "k2.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n\n")
    assert pr_.k2_attempts() == rows


# ---------------------------------------------------------------------------- selection: every dropped day


@dataclass
class Flat:
    name: str
    nan_days: frozenset = frozenset()

    def predict(self, series, windows):
        return [Prediction(values=np.full(len(w.targets), np.nan if w.delivery_date in self.nan_days else 50.0),
                           max_source_time=w.origin, source_latest=pd.DatetimeIndex([w.origin] * len(w.targets)))
                for w in windows]


def test_the_selection_lists_every_dropped_day(monkeypatch):
    s = prices(start="2022-12-01", end="2024-01-03")
    days = px.days_between(*pr_.PERIODS["selection"])
    nan_days = frozenset(days[10:70])  # 60 days, more than the old cap of 50
    names = ps.PRICE_SPEC["simple_candidates"]
    monkeypatch.setattr(px, "simple_rules", lambda strict=False: {
        n: Flat(n, nan_days if n == "prev_day" else frozenset()) for n in names})
    sel = pr_.select_best_simple(s)
    assert sel["dropped_count"]["prev_day"] == 60
    assert sel["dropped_by_candidate"]["prev_day"] == sorted(str(d) for d in nan_days)
    assert sel["days"] == len(days) - 60 and sel["dropped_by_candidate"]["naive_std"] == []


def test_the_eq_control_holds_when_d1_errors_are_already_extreme():
    """Fix-check defect 1: a D-1 price jump puts D-1's error at the top of E_t, where +40 moved no quantile and the
    control failed on correct code (about 1% of real days); the two-sided edit moves them."""
    s = prices().copy()
    s[px.day_hours(D - timedelta(days=1))] += 300.0
    w = px.build_price_windows(s, [D])[0]
    for name in ("prev_day", "naive_std", "prev_week", "blend_50"):
        eq = px.PriceEmpiricalQuantiles(base=px.Renamed(px.simple_rules()[name], "best_simple_2023"))
        assert lk.eq_error_quantiles_move(eq, s, w), name


def test_the_in_run_check_runs_the_error_quantile_control(s, wx, monkeypatch):
    """Fix-check defect 2: the in-run key must run the error-quantile control (the band compare passes this bug)."""
    from test_price_exp import EqLegalOnlyToD2

    monkeypatch.setattr(ps, "TEST_ORIGINS", [str(D)])
    arms = arms_for(wx)
    arms.eq = EqLegalOnlyToD2(base=px.Renamed(px.NaiveStd(), "best_simple_2023"))
    out = pr_.in_run_leak_check(s, arms, p4_first_day=P4_FIRST, k3_passed=False, k1_passed=False, weather=wx)
    assert out["origins"][str(D)]["legal_d1_moves_eq_error_quantiles"] is False and not out["pass"]
