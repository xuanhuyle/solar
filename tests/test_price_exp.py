"""Experiment 4 core: the publication rule, price windows, the price backtest and every arm's leak controls
(offline: synthetic hourly prices and a stand-in for t0)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from engine import zones
from solarbench import covariates as cov
from solarbench import price_exp as px
from solarbench import price_leak as lk
from solarbench import price_spec as ps
from solarbench.backtest import build_windows, run_backtest

PARIS = zones.PARIS


def prices(start="2023-06-01", end="2024-04-15", seed=0) -> pd.Series:
    idx = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(end), freq="1h", tz="UTC",
                        inclusive="left")
    local = idx.tz_convert(PARIS)
    rng = np.random.default_rng(seed)
    v = 60 + 25 * np.sin(2 * np.pi * (local.hour - 7) / 24) - 30 * (local.hour == 13) + rng.normal(0, 8, len(idx))
    return pd.Series(v, index=idx)  # includes negative-ish midday dips


class EchoT0:
    """Stands in for t0: a weighted sum of the whole context plus the horizon covariates; five 'quantiles'."""

    def __init__(self):
        self.calls = 0

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch

        self.calls += 1
        ctx = torch.nan_to_num(torch.as_tensor(context, dtype=torch.float64))
        T = ctx.shape[-1]
        w = torch.linspace(0.1, 1.0, T, dtype=torch.float64)
        base = (ctx * w).sum(dim=1, keepdim=True) / w.sum() + 0.5 * ctx[:, -1:]
        median = base.repeat(1, horizon)
        if future_covariates is not None:
            fut = torch.nan_to_num(torch.as_tensor(future_covariates, dtype=torch.float64))
            median = median + fut[:, :, T:T + horizon].sum(dim=1) + 1e-6 * fut[:, :, :T].sum(dim=(1, 2))[:, None]
        spread = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=torch.float64)
        q = median[:, :, None] + spread[None, None, :] * 5.0
        return SimpleNamespace(median=median, quantiles=q)


def t0(name="t0_cal", covariates=None, horizon=px.HORIZON):
    covs = (px.holiday(),) if covariates is None else tuple(covariates)
    return px.PriceT0Forecaster(name=name, covariates=covs, horizon=horizon).use_model(EchoT0())


# ------------------------------------------------------------------ publication rule and windows


def _paris_midnight_utc(d: date, hour: int = 0) -> datetime:
    """zoneinfo only: ``hour``:00 Europe/Paris on ``d``, in UTC."""
    return datetime(d.year, d.month, d.day, hour, tzinfo=ZoneInfo("Europe/Paris")).astimezone(timezone.utc)


def test_the_publication_rule_rederived_independently():
    """leak_controls[0]: every window 2023-2025 and the TEST_ORIGINS days, normal and strict, against the rule
    re-derived with zoneinfo alone (no module helper): decision = 12:00 Paris on D-1; targets = the real 23/24/25
    UTC hours of D; origin = first target - 1 h (strict: the decision); pub_latest of every target = D 00:00 Paris,
    pub_earliest of every target = 12:00 D-1 Paris; pub_latest(origin) <= decision."""
    hour = timedelta(hours=1)
    days = sorted(set(px.days_between("2023-01-01", "2025-12-31")) | {date.fromisoformat(d) for d in ps.TEST_ORIGINS})
    lens = {}
    for strict in (False, True):
        windows = px.build_price_windows(None, days, strict=strict, require_target=False)
        assert [w.delivery_date for w in windows] == days
        for w in windows:
            d = w.delivery_date
            decision = _paris_midnight_utc(d - timedelta(days=1), 12)
            start, end = _paris_midnight_utc(d), _paris_midnight_utc(d + timedelta(days=1))
            n = (end - start) // hour
            targets = [start + k * hour for k in range(n)]
            origin = decision if strict else targets[0] - hour
            assert n in (23, 24, 25) and w.strict == strict
            assert list(w.targets) == targets and w.decision == decision and w.origin == origin, (d, strict)
            assert list(px.pub_latest(w.targets)) == [start] * n, d
            assert list(px.pub_earliest(w.targets)) == [decision] * n, d
            origin_day = origin.astimezone(ZoneInfo("Europe/Paris")).date()
            assert px.pub_latest([w.origin])[0] == _paris_midnight_utc(origin_day) <= decision, (d, strict)
            lens[(d, strict)] = n
    assert len(lens) == 2 * 1096
    for strict in (False, True):
        assert {d for (d, st), n in lens.items() if st == strict and n == 23} == {
            date(2023, 3, 26), date(2024, 3, 31), date(2025, 3, 30)}
        assert {d for (d, st), n in lens.items() if st == strict and n == 25} == {
            date(2023, 10, 29), date(2024, 10, 27), date(2025, 10, 26)}


def test_a_later_decision_is_refused_and_missing_targets_are_counted():
    s = prices()
    with pytest.raises(ValueError):
        px.build_price_windows(s, [date(2024, 1, 10)], decision_hour=13)
    s2 = s.copy()
    s2[px.day_hours(date(2024, 1, 10))[5]] = np.nan
    rep = px.WindowReport()
    ws = px.build_price_windows(s2, [date(2024, 1, 9), date(2024, 1, 10)], report=rep)
    assert [w.delivery_date for w in ws] == [date(2024, 1, 9)] and rep.incomplete_target == [date(2024, 1, 10)]


def test_strict_windows_end_at_the_decision_stamp():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)], strict=True)[0]
    assert w.origin == w.decision and w.origin.tz_convert(PARIS).hour == 12
    assert w.horizon <= px.STRICT_HORIZON


# ------------------------------------------------------------------ backtest


def test_no_clipping_and_no_all_methods_drop():
    s = prices() - 70.0  # many negative prices
    ws = px.build_price_windows(s, px.days_between("2024-01-08", "2024-01-20"))
    rules = px.simple_rules()
    df = px.run_price_backtest(s, [rules["prev_day"], rules["naive_std"], t0()], ws)
    assert (df["y_hat"] < 0).any() and set(df["method"]) == {"prev_day", "naive_std", "t0_cal"}
    assert df.groupby("method")["delivery_date"].nunique().eq(len(ws)).all()


def test_parity_with_run_backtest_on_a_non_negative_half_hour_series():
    idx = pd.date_range("2023-11-01", "2024-02-01", freq="30min", tz="UTC")
    s = pd.Series(100 + 20 * np.sin(np.arange(len(idx)) / 7.0), index=idx)
    ws = build_windows(s, test_start=date(2024, 1, 5), test_end=date(2024, 1, 20), gate_hour=12, context_steps=96)
    rules = px.simple_rules()
    for name in ("prev_day", "prev_week", "mean_7d", "ewma", "blend_50"):
        a = run_backtest(s, [rules[name]], ws)
        b = px.run_price_backtest(s, [rules[name]], ws)
        np.testing.assert_array_equal(a["y_hat"].to_numpy(), b["y_hat"].to_numpy())


def test_a_covariate_issued_after_d_is_refused():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)])[0]
    assert lk.covariate_refusal(w)


# ------------------------------------------------------------------ poisoning of every arm


ARMS_DAYS = [date(2024, 1, 10), date(2024, 3, 31), date(2023, 10, 29), date(2024, 1, 15)]


def all_arms(series):
    rules = px.simple_rules()
    eq = px.PriceEmpiricalQuantiles(base=px.Renamed(rules["naive_std"], "best_simple_2023"))
    return [*rules.values(), t0("t0", covariates=()), t0("t0_cal"), eq]


@pytest.mark.parametrize("day", ARMS_DAYS)
def test_target_poisoning_leaves_every_arm_identical(day):
    s = prices()
    w = px.build_price_windows(s, [day])[0]
    for arm in all_arms(s):
        res = lk.target_poisoning(arm, s, w)
        assert res == {"affine": True, "nan": True}, (arm.name, day, res)


def test_legal_changes_move_the_arms_that_read_them():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)])[0]  # a Wednesday: naive_std reads D-1
    for arm in (t0("t0", covariates=()), t0("t0_cal"), px.NaiveStd()):
        assert lk.legal_change(arm, s, w, which="afternoon"), arm.name
    for arm in (t0("t0", covariates=()), t0("t0_cal")):
        assert lk.legal_change(arm, s, w, which="d2"), arm.name
    eq = px.PriceEmpiricalQuantiles(base=px.Renamed(px.NaiveStd(), "best_simple_2023"))
    assert lk.eq_error_quantiles_move(eq, s, w)  # D-1's errors enter the error quantiles themselves


class EqLegalOnlyToD2(px.PriceEmpiricalQuantiles):
    """A mutation: the error cells of D-1 are made illegal (legal only up to D-2)."""

    def last_legal_day(self, d):
        return d - timedelta(days=2)


def test_the_eq_control_compares_the_error_quantiles_not_the_bands():
    """L2/FID-2: with naive_std on a Wednesday (it reads D-1), the bands f_D + Q(E) move under the D-1 edit even
    when no D-1 error enters Q(E); the control on Q(E) itself catches the mutation the old one passed."""
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)])[0]
    assert w.delivery_date.weekday() == 2
    base = px.Renamed(px.NaiveStd(), "best_simple_2023")
    bad = EqLegalOnlyToD2(base=base)
    s2 = s.copy()
    s2[px.day_hours(date(2024, 1, 9))] += lk.EQ_D1_SHIFT
    old_control = not np.array_equal(bad.predict(s, [w])[0].quantiles, bad.predict(s2, [w])[0].quantiles,
                                     equal_nan=True)
    assert old_control  # the old control passed the mutation
    assert not lk.eq_error_quantiles_move(bad, s, w)  # the new one fails it
    assert lk.eq_error_quantiles_move(px.PriceEmpiricalQuantiles(base=base), s, w)


def _eq_predict_before_the_refactor(eq, series, windows):
    """PriceEmpiricalQuantiles.predict as it was before error_quantiles was split out (verbatim)."""
    from solarbench.forecasters import Prediction

    base_scored = eq.base.predict(series, windows)
    need = sorted({w.delivery_date - timedelta(days=k) for w in windows for k in range(1, eq.lookback + 2)})
    hist_windows = px.build_price_windows(None, need, require_target=False)
    hist_preds = eq.base.predict(series, hist_windows)
    f_hist = pd.concat([pd.Series(p.values, index=hw.targets) for hw, p in zip(hist_windows, hist_preds)])
    f_hist = f_hist[~f_hist.index.duplicated(keep="first")]
    out = []
    for w, p in zip(windows, base_scored):
        d = w.delivery_date
        n = len(w.targets)
        q = np.full((n, len(eq.levels)), np.nan)
        latest = list(p.source_latest) if p.source_latest is not None else [p.max_source_time] * n
        for i, t in enumerate(w.targets):
            cells = pd.DatetimeIndex([t - pd.Timedelta(days=j) for j in range(1, eq.lookback + 1)])
            legal_day = px.paris_day(cells) <= d - timedelta(days=1)
            err = series.reindex(cells).to_numpy(dtype="float64") - f_hist.reindex(cells).to_numpy(dtype="float64")
            ok = legal_day & np.isfinite(err)
            picks = np.flatnonzero(ok)[: eq.window]
            if len(picks) >= eq.min_n and np.isfinite(p.values[i]):
                q[i] = p.values[i] + np.quantile(err[picks], eq.levels)
                latest[i] = max(latest[i], cells[picks[0]]) if pd.notna(latest[i]) else cells[picks[0]]
        idx = pd.DatetimeIndex(latest)
        out.append(Prediction(values=np.asarray(p.values, dtype="float64"), max_source_time=idx.max(),
                              source_latest=idx, source_earliest=p.source_earliest, n_sources=p.n_sources,
                              quantiles=q, quantile_levels=tuple(eq.levels)))
    return out


def test_eq_predict_is_bit_identical_after_the_refactor_and_shares_the_cell_rule():
    s = prices()
    local = s.index.tz_convert(PARIS)
    s[(s.index >= "2023-12-08") & (s.index < "2024-01-07") & (local.hour < 6)] = np.nan  # early hours under min_n
    s[s.index.tz_convert(PARIS).date == date(2024, 1, 3)] = np.nan
    days = [date(2024, 1, 5), date(2024, 1, 10), date(2024, 1, 15), date(2024, 3, 31), date(2023, 10, 29)]
    ws = px.build_price_windows(s, days, require_target=False)
    rules = px.simple_rules()
    for name in ("naive_std", "prev_day", "weekday_mean_4w", "blend_50"):
        eq = px.PriceEmpiricalQuantiles(base=px.Renamed(rules[name], "best_simple_2023"))
        new, old = eq.predict(s, ws), _eq_predict_before_the_refactor(eq, s, ws)
        eqs = eq.error_quantiles(s, ws)
        for w, a, b, e in zip(ws, new, old, eqs):
            assert np.array_equal(a.values, b.values, equal_nan=True), (name, w.delivery_date)
            assert np.array_equal(a.quantiles, b.quantiles, equal_nan=True), (name, w.delivery_date)
            assert a.source_latest.equals(b.source_latest) and a.max_source_time == b.max_source_time
            assert e.shape == (len(w.targets), len(px.LEVELS))
            finite = np.isfinite(a.values)
            np.testing.assert_array_equal(a.quantiles[finite], (a.values[:, None] + e)[finite])
        assert any(np.isnan(e).all(axis=1).any() and not np.isnan(e).all() for e in eqs), name  # both cases hit


def test_the_strict_arm_obeys_the_old_rule():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)], strict=True)[0]
    arm = t0("t0_cal_strict", horizon=px.STRICT_HORIZON)
    assert lk.target_poisoning(arm, s, w) == {"affine": True, "nan": True}
    assert not lk.legal_change(arm, s, w, which="afternoon")
    assert lk.legal_change(arm, s, w, which="noon")
    strict_rule = px.simple_rules(strict=True)["naive_std"]
    assert lk.target_poisoning(strict_rule, s, w) == {"affine": True, "nan": True}
    assert lk.context_end(arm, s, w)


def test_context_ends_at_the_last_hour_of_d_minus_1():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 3, 31)])[0]
    assert lk.context_end(t0(), s, w)


# ------------------------------------------------------------------ naive_std DST rules


def test_naive_std_local_hours_and_dst():
    s = prices()
    # Tuesday 2024-04-02: lag D-1 = 2024-04-01 (normal); Monday 2024-04-01: lag D-7 = 2024-03-25
    w = px.build_price_windows(s, [date(2024, 4, 2)])[0]
    v = px.NaiveStd().predict(s, [w])[0].values
    lag = s[px.day_hours(date(2024, 4, 1))]
    np.testing.assert_allclose(v, lag.to_numpy())
    # Monday after the spring switch: lag day 2024-03-25 has 24 hours, D has 24; Sunday 2024-03-31 (23 h) lags 03-24
    w = px.build_price_windows(s, [date(2024, 3, 31)])[0]
    v = px.NaiveStd().predict(s, [w])[0].values
    assert len(v) == 23 and np.isfinite(v).all()
    # a day whose D-7 is the spring day (2024-04-07, Sunday) fills local 02:00 from 01:00
    w = px.build_price_windows(s, [date(2024, 4, 7)])[0]
    v = px.NaiveStd().predict(s, [w])[0].values
    lag = s[px.day_hours(date(2024, 3, 31))]
    by_h = dict(zip(lag.index.tz_convert(PARIS).hour, lag.to_numpy()))
    assert v[2] == pytest.approx(by_h[1])


# ------------------------------------------------------------------ t0 NaN rule and weather port


def test_t0_is_nan_when_its_context_is_under_98_percent_valid():
    s = prices()
    w = px.build_price_windows(s, [date(2024, 1, 10)])[0]
    s2 = s.copy()
    ctx_idx = pd.date_range(end=w.origin, periods=px.CONTEXT_HOURS, freq="1h")
    s2[ctx_idx[:60]] = np.nan  # 60 / 2160 = 2.8% missing
    arm = t0()
    p = arm.predict(s2, [w])[0]
    assert np.isnan(p.values).all() and np.isnan(p.quantiles).all() and arm.missing["context"] == ["2024-01-10"]


def test_weather_port_parity():
    grid = pd.date_range("2024-06-01 00:00", periods=2, freq="1h", tz="UTC")
    readings = pd.Series([0.0, 10.0, 20.0], index=pd.date_range("2024-06-01 00:00", periods=3, freq="1h", tz="UTC"))
    t, r = px.weather_covariates(readings, readings, grid)
    np.testing.assert_allclose(r.values(grid), [10.0, 20.0])
    np.testing.assert_allclose(t.values(grid), [5.0, 15.0])
    # issue bound from the latest reading used (h + 1 h), lead 3 days + 10 h
    assert t.issued_at(grid)[0] == grid[0] + pd.Timedelta(hours=1) - pd.Timedelta(days=3) + pd.Timedelta(hours=10)


def test_weather_poisoning_and_control_on_t0_cal_wx():
    s = prices()
    grid = pd.date_range(s.index[0], s.index[-1] + pd.Timedelta(days=2), freq="1h", tz="UTC")
    rng = np.random.default_rng(3)
    wx = pd.Series(rng.normal(10, 5, len(grid) + 1),
                   index=pd.date_range(grid[0], periods=len(grid) + 1, freq="1h", tz="UTC"))
    temp, rad = px.weather_covariates(wx, wx.abs(), grid)
    arm = t0("t0_cal_wx", covariates=(px.holiday(), temp, rad))
    w = px.build_price_windows(s, [date(2024, 1, 10)])[0]
    assert lk.weather_controls(arm, s, w) == {"after_d_no_effect": True, "before_d_moves": True}
    assert lk.target_poisoning(arm, s, w) == {"affine": True, "nan": True}
