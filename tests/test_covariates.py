"""Tests for the covariate slice: t0 with solar geometry and archived weather forecasts.

Everything is offline: the network is stubbed and t0 is replaced by a model
that echoes its inputs, so each test can say exactly which value reached the
model and when it was issued.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run_benchmark
import run_covariates
from solarbench import covariates as cov
from solarbench import weather
from solarbench.astro import dark_mask, solar_elevation
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import STEP
from solarbench.forecasters import (
    Derived,
    Prediction,
    T0Forecaster,
    WeatherSlotRatio,
    night_zero_variant,
    statistical_baselines,
)

CTX = 48 * 10
EQUAL = {k: 1.0 for k in cov.REGION_POINTS}
EXP0_COLUMNS = [
    "delivery_date", "origin", "target_time", "step", "local_time", "slot", "month", "y",
    "method", "y_hat", "source_latest", "source_earliest", "n_sources",
]


def solar_series(start="2023-09-01", end="2024-12-31 23:30") -> pd.Series:
    index = pd.date_range(start, end, freq=STEP, tz="UTC")
    el = solar_elevation(index, 46.0, 2.0)
    wobble = 1 + 0.3 * np.sin(np.arange(len(index)) / (48 * 3.7))
    return pd.Series(12_000 * np.maximum(np.sin(np.deg2rad(el)), 0) * wobble, index=index, name="solar_mw")


def hourly_frame(start="2023-09-30", end="2025-01-01", scale=900.0, shift=0.0) -> pd.DataFrame:
    """Synthetic hourly irradiance per region, stamped at the end of each hour."""
    index = pd.date_range(pd.Timestamp(start, tz="UTC") + pd.Timedelta(hours=1), pd.Timestamp(end, tz="UTC"), freq="h")
    cols = {}
    for region, (lat, lon) in cov.REGION_POINTS.items():
        el = solar_elevation(index - pd.Timedelta(minutes=30), lat, lon)
        cols[region] = scale * np.maximum(np.sin(np.deg2rad(el)), 0) * (1 + 0.2 * np.sin(np.arange(len(index)) / 29.0)) + shift
    return pd.DataFrame(cols, index=index)


def windows_for(series, first, last, context=CTX):
    return build_windows(series, test_start=date.fromisoformat(first), test_end=date.fromisoformat(last),
                         gate_hour=12, context_steps=context)


class CovEchoModel:
    """Stands in for t0: last context value + the horizon covariates (+ a trace of the context ones).

    Records every call.  A context whose last value is -999 makes it log t0's
    sanitisation warning, as the real model does on non-finite output.
    """

    def __init__(self):
        self.calls = []

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch

        ctx = torch.as_tensor(context, dtype=torch.float64)
        record = {"horizon": horizon, "batch": int(ctx.shape[0]), "futures": None}
        median = ctx[:, -1:].repeat(1, horizon)
        if future_covariates is not None:
            fut = torch.as_tensor(future_covariates, dtype=torch.float64)
            record["futures"] = fut.numpy().copy()
            T = ctx.shape[-1]
            median = median + torch.nan_to_num(fut[:, :, T:T + horizon]).sum(dim=1)
            median = median + 1e-6 * torch.nan_to_num(fut[:, :, :T]).sum(dim=(1, 2))[:, None]
        if (ctx[:, -1] == -999).any():
            logging.getLogger("t0.model.model").warning("replaced %d non-finite prediction values with 0.0", 1)
        self.calls.append(record)
        return SimpleNamespace(median=median)


def stub_t0(name="t0_x", covariates=(), batch_size=64, model=None, fixed=cov.COV_HORIZON):
    return T0Forecaster(context_steps=CTX, name=name, batch_size=batch_size, covariates=tuple(covariates),
                        fixed_horizon=fixed if covariates else None, _model=model or CovEchoModel())


def weather_cov(frame=None, lead=2, offset=15, oracle=False, name="weather"):
    frame = hourly_frame() if frame is None else frame
    grid = pd.date_range("2023-09-30", "2025-01-01", freq=STEP, tz="UTC", inclusive="left")
    return cov.weather_covariate(cov.national_mean(frame, EQUAL), grid, lead_days=lead,
                                 stamp_offset_min=offset, oracle=oracle, name=name)


# ------------------------------------------------------- Experiment 0 intact


def test_experiment0_cache_key_is_unchanged():
    """Pinned from ``main`` before any covariate code existed."""
    args = run_benchmark.parse_args(["--revision", "9b02c5f4bb6c89ba15d9fa74554018fe6464220b"])
    key, _ = run_benchmark._cache_key(args, "0123456789abcdef", run_benchmark.build_forecasters(args))
    assert key == "6d6e81c353cfb512"


def test_experiment0_frame_columns_are_unchanged():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    windows = windows_for(series, "2024-02-01", "2024-02-05")
    methods = [T0Forecaster(context_steps=CTX, _model=CovEchoModel()), night_zero_variant("t0"), *statistical_baselines()]
    df = run_backtest(series, methods, windows)
    assert list(df.columns) == EXP0_COLUMNS


def test_default_t0_call_passes_no_covariates():
    model = CovEchoModel()
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    T0Forecaster(context_steps=CTX, _model=model).predict(series, windows_for(series, "2024-02-01", "2024-02-03"))
    assert model.calls and all(c["futures"] is None for c in model.calls)
    assert "covariates" not in T0Forecaster(context_steps=CTX).spec()


# ------------------------------------------------------------ transforms


def test_parse_hourly_multi_and_single_location(tmp_path):
    stamps = [1717200000, 1717203600]
    multi = [{"hourly": {"time": stamps, "v": [1.0, None]}}, {"hourly": {"time": stamps, "v": [3.0, 4.0]}}]
    (tmp_path / "m.json").write_text(json.dumps(multi))
    frame = weather.parse_hourly(tmp_path / "m.json", "v", ["a", "b"])
    assert frame.index.tz is not None and frame.index[0] == pd.Timestamp("2024-06-01 00:00", tz="UTC")
    assert np.isnan(frame.loc[frame.index[1], "a"]) and frame["b"].tolist() == [3.0, 4.0]
    (tmp_path / "s.json").write_text(json.dumps(multi[1]))
    assert weather.parse_hourly(tmp_path / "s.json", "v", ["b"])["b"].tolist() == [3.0, 4.0]
    with pytest.raises(ValueError):
        weather.parse_hourly(tmp_path / "m.json", "v", ["a"])


@pytest.mark.parametrize("offset,expected,stamps", [
    (15, [10, 10, 20, 20], ["02:00", "02:00", "03:00", "03:00"]),
    (0, [5, 10, 15, 20], ["02:00", "02:00", "03:00", "03:00"]),
    (-15, [0, 10, 10, 20], ["01:00", "02:00", "02:00", "03:00"]),
])
def test_hourly_to_slots_uses_only_overlapping_hours(offset, expected, stamps):
    hourly = pd.Series(np.arange(6) * 10.0, index=pd.date_range("2024-06-01 01:00", periods=6, freq="h", tz="UTC"))
    times = pd.date_range("2024-06-01 01:00", periods=4, freq="30min", tz="UTC")
    values, latest = cov.hourly_to_slots(hourly, times, offset)
    assert values.tolist() == expected
    assert [t.strftime("%H:%M") for t in latest] == stamps


def test_hourly_to_slots_propagates_a_missing_hour_and_never_fills():
    hourly = pd.Series([0.0, 10.0, np.nan, 30.0], index=pd.date_range("2024-06-01 01:00", periods=4, freq="h", tz="UTC"))
    times = pd.date_range("2024-06-01 01:00", periods=6, freq="30min", tz="UTC")
    values, _ = cov.hourly_to_slots(hourly, times, 0)
    # centred slots at 02:00 and 03:00 straddle the missing hour stamped 03:00
    assert np.isnan(values[[2, 3, 4]]).all() and np.isfinite(values[[0, 1, 5]]).all()


@pytest.mark.parametrize("day,slots", [("2024-03-31", 46), ("2024-10-27", 50)])
def test_dst_days_get_every_slot(day, slots):
    local = pd.date_range(day, periods=2, freq="D", tz="Europe/Paris")
    times = pd.date_range(local[0].tz_convert("UTC"), local[1].tz_convert("UTC"), freq=STEP, inclusive="left")
    assert len(times) == slots
    values, _ = cov.hourly_to_slots(cov.national_mean(hourly_frame(), EQUAL), times, 15)
    assert np.isfinite(values).all()


@pytest.mark.parametrize("offset", [15, 0, -15])
def test_issue_bound_holds_for_lead_2_and_3_and_fails_for_1(offset):
    series = solar_series("2023-12-01", "2024-12-31 23:30")
    windows = windows_for(series, "2024-01-01", "2024-12-31")
    assert len(windows) > 360
    worst = {}
    for lead in (1, 2, 3):
        margin = []
        for w in windows:
            times = cov.covariate_times(w.origin, CTX, cov.COV_HORIZON)
            _, latest = cov.hourly_to_slots(pd.Series(dtype="float64"), times, offset)
            margin.append((w.origin - cov.issue_bound(latest, lead).max()) / pd.Timedelta(hours=1))
        worst[lead] = min(margin)
    assert worst[2] >= 0.5 and worst[3] >= 24.5
    assert worst[1] < 0


def test_sealed_period_is_refused_before_any_request(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network touched")

    monkeypatch.setattr(weather.requests, "get", boom)
    for call in (
        lambda: weather.fetch_previous_runs("m", ["v"], "2024-12-01", "2025-01-01", Path("/nonexistent")),
        lambda: weather.fetch_era5("v", "2025-01-01", "2025-02-01", Path("/nonexistent")),
        lambda: weather.fetch_single_run("m", "v", pd.Timestamp("2024-12-29", tz="UTC"), (45.0, 2.0), Path("/nonexistent")),
    ):
        with pytest.raises(weather.SealedDataError):
            call()


def test_geometry_is_nonnegative_and_zero_whenever_it_is_dark_everywhere():
    times = pd.date_range("2024-01-01", "2024-12-31 23:30", freq=STEP, tz="UTC")
    for offset in (15, 0, -15):
        g = cov.GeometryCovariate(EQUAL, offset).values(times)
        assert (g >= 0).all() and g.max() > 0.5
        assert (g[dark_mask(times)] == 0).all()


def test_geometry_memo_matches_a_fresh_computation():
    geo = cov.GeometryCovariate(EQUAL, 15)
    a = geo.values(pd.date_range("2024-06-01", periods=500, freq=STEP, tz="UTC"))
    b = geo.values(pd.date_range("2024-06-05", periods=500, freq=STEP, tz="UTC"))
    fresh = cov.GeometryCovariate(EQUAL, 15).values(pd.date_range("2024-06-05", periods=500, freq=STEP, tz="UTC"))
    assert np.array_equal(b, fresh) and len(a) == 500


def test_weights_are_normalised_and_points_are_in_france():
    w = cov.normalised_weights({k: i + 1.0 for i, k in enumerate(cov.REGION_POINTS)})
    assert len(w) == 12 and abs(sum(w.values()) - 1) < 1e-12
    for lat, lon in cov.REGION_POINTS.values():
        assert 41.3 <= lat <= 51.1 and -5.2 <= lon <= 9.6
    with pytest.raises(ValueError):
        cov.normalised_weights({"Bretagne": 1.0})


def test_region_weights_parse_the_grouped_odre_answer(monkeypatch, tmp_path):
    body = {"results": [{"libelle_region": name.upper() if i % 2 else name, "solaire_sum": float(i + 1)}
                        for i, name in enumerate(cov.REGION_POINTS)]}
    (tmp_path / "r.json").write_text(json.dumps(body))
    monkeypatch.setattr(weather, "fetch_json", lambda *a, **k: tmp_path / "r.json")
    weights, raw = weather.fetch_region_weights_2023(tmp_path)
    assert abs(sum(weights.values()) - 1) < 1e-12
    assert weights["Occitanie"] == pytest.approx(10 / 78)


# ------------------------------------------------------------- the adapter


def test_covariates_reach_the_model_at_the_exact_positions():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    windows = windows_for(series, "2024-02-01", "2024-02-04")
    grid = pd.date_range("2023-12-01", "2024-04-30", freq=STEP, tz="UTC")
    clock = cov.SeriesCovariate("clock", pd.Series((grid - grid[0]) / pd.Timedelta(hours=1), index=grid))
    model = CovEchoModel()
    stub_t0(covariates=(clock,), model=model).predict(series, windows)
    fut = model.calls[0]["futures"]
    assert fut.shape == (4, 1, CTX + cov.COV_HORIZON)
    for row, w in enumerate(windows):
        times = cov.covariate_times(w.origin, CTX, cov.COV_HORIZON)
        assert times[CTX - 1] == w.origin and times[CTX] == w.origin + STEP
        expected = (times - grid[0]) / pd.Timedelta(hours=1)
        assert np.allclose(fut[row, 0], expected)


def test_fixed_horizon_and_batch_composition_do_not_change_forecasts():
    series = solar_series("2024-01-01", "2024-11-30 23:30")
    windows = windows_for(series, "2024-03-29", "2024-04-02") + windows_for(series, "2024-10-25", "2024-10-29")
    wx = weather_cov()
    big, one = CovEchoModel(), CovEchoModel()
    a = stub_t0(covariates=(wx,), model=big).predict(series, windows)
    b = stub_t0(covariates=(wx,), model=one, batch_size=1).predict(series, windows)
    assert {c["horizon"] for c in big.calls + one.calls} == {cov.COV_HORIZON}
    for x, y in zip(a, b):
        assert np.array_equal(x.values, y.values)


def test_poisoning_the_future_changes_nothing_but_the_window_does():
    series = solar_series("2024-01-01", "2024-08-31 23:30")
    wx = weather_cov()
    arm = stub_t0(covariates=(cov.GeometryCovariate(EQUAL, 15), wx))
    for w in windows_for(series, "2024-06-10", "2024-06-12") + windows_for(series, "2024-03-30", "2024-03-31"):
        clean = arm.predict(series, [w])[0]
        poisoned = series.copy()
        poisoned.loc[poisoned.index > w.origin] = poisoned.loc[poisoned.index > w.origin] * -7.5 + 1234.5
        assert np.array_equal(clean.values, arm.predict(poisoned, [w])[0].values)

        times = cov.covariate_times(w.origin, CTX, cov.COV_HORIZON)
        outside = wx.series.copy()
        outside.loc[~outside.index.isin(times)] = 1e6
        moved = stub_t0(covariates=(cov.GeometryCovariate(EQUAL, 15), cov.SeriesCovariate("w", outside, wx.issued)))
        assert np.array_equal(clean.values, moved.predict(series, [w])[0].values)

        inside = wx.series.copy()
        inside.loc[times[CTX + 30]] += 100.0
        seen = stub_t0(covariates=(cov.GeometryCovariate(EQUAL, 15), cov.SeriesCovariate("w", inside, wx.issued)))
        assert not np.array_equal(clean.values, seen.predict(series, [w])[0].values), "a leak would be invisible"


def test_contract_rejects_a_covariate_issued_after_the_origin():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    windows = windows_for(series, "2024-02-01", "2024-02-03")
    early = weather_cov(lead=2)
    df = run_backtest(series, [stub_t0("t0_wx", (early,))], windows)
    assert (df["cov_issued_latest"] <= df["origin"]).all()
    late = weather_cov(lead=1)
    with pytest.raises(AssertionError, match="issued"):
        run_backtest(series, [stub_t0("t0_wx", (late,))], windows)


def test_the_oracle_exemption_needs_both_keys():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    windows = windows_for(series, "2024-02-01", "2024-02-02")
    era = weather_cov(lead=0, oracle=True, name="era5")
    arm = stub_t0("t0_wx_oracle", (era,))
    with pytest.raises(AssertionError, match="oracle"):
        run_backtest(series, [arm], windows)  # flagged, not declared
    with pytest.raises(AssertionError, match="name"):
        run_backtest(series, [stub_t0("t0_reference", (era,))], windows, oracle_methods=frozenset({"t0_reference"}))
    with pytest.raises(AssertionError, match="oracle"):
        run_backtest(series, [stub_t0("t0_wx", (weather_cov(),))], windows, oracle_methods=frozenset({"t0_wx"}))
    nz = night_zero_variant("t0_wx_oracle")
    df = run_backtest(series, [arm, nz], windows, oracle_methods=frozenset({"t0_wx_oracle", "t0_wx_oracle_night_zero"}))
    assert (df["cov_issued_latest"] > df["origin"]).all()  # allowed only for the declared reference arm
    with pytest.raises(AssertionError, match="oracle"):
        run_backtest(series, [arm, nz], windows, oracle_methods=frozenset({"t0_wx_oracle"}))  # derived undeclared


def test_nonfinite_model_output_drops_that_day_for_every_method():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    windows = windows_for(series, "2024-02-01", "2024-02-05")
    series.loc[windows[2].origin] = -999.0  # the stub "sanitises" this row
    report = BacktestReport()
    df = run_backtest(series, [stub_t0("t0_wx", (weather_cov(),)), *statistical_baselines()], windows, report=report)
    assert str(windows[2].delivery_date) in report.skipped_nonfinite_forecast
    assert report.skipped_nonfinite_by_method == {"t0_wx": [str(windows[2].delivery_date)]}
    assert df["delivery_date"].nunique() == 4


def test_derived_methods_carry_the_issue_time():
    pred = Prediction(values=np.ones(3), max_source_time=pd.Timestamp("2024-01-01", tz="UTC"),
                      covariate_issued_latest=pd.Timestamp("2023-12-31", tz="UTC"))
    w = SimpleNamespace(targets=pd.date_range("2024-01-02", periods=3, freq=STEP, tz="UTC"))
    d = Derived(name="d", label="d", source="s", transform=lambda win, v: v)
    assert d.derive(w, pred).covariate_issued_latest == pred.covariate_issued_latest


def test_coverage_needs_a_complete_horizon_and_a_nearly_complete_context():
    series = solar_series("2024-01-01", "2024-03-31 23:30")
    w = windows_for(series, "2024-02-10", "2024-02-10")[0]
    wx = weather_cov()
    times = cov.covariate_times(w.origin, CTX, cov.COV_HORIZON)
    assert cov.window_coverage(w.origin, [wx], CTX, cov.COV_HORIZON) == (1.0, True)
    hole = cov.SeriesCovariate("w", wx.series.copy(), wx.issued)
    hole.series.loc[times[CTX + 5]] = np.nan
    assert cov.window_coverage(w.origin, [hole], CTX, cov.COV_HORIZON)[1] is False
    small = cov.SeriesCovariate("w", wx.series.copy(), wx.issued)
    small.series.loc[times[:5]] = np.nan
    share, ok = cov.window_coverage(w.origin, [small], CTX, cov.COV_HORIZON)
    assert ok and share >= cov.MIN_CONTEXT_VALID
    keep, dropped = run_covariates._eligible([w], [hole], CTX)
    assert keep == [] and dropped[0]["horizon_complete"] is False


# ------------------------------------------------------------- wx_ratio


def test_wx_ratio_by_hand():
    index = pd.date_range("2024-05-01", "2024-06-30 23:30", freq=STEP, tz="UTC")
    y = pd.Series(2.0, index=index)
    g = pd.Series(4.0, index=index)
    w = windows_for(y, "2024-06-20", "2024-06-20")[0]
    g.loc[w.targets[10]] = 8.0  # forecast doubles for one target
    y.loc[w.targets[10] - pd.Timedelta(days=3)] = np.nan  # a missing source is skipped, not zero
    gs = cov.SeriesCovariate("g", g, pd.Series(w.origin - pd.Timedelta(hours=1), index=index))
    pred = WeatherSlotRatio(gs).predict(y, [w])[0]
    assert np.allclose(np.delete(pred.values, 10), 2.0) and pred.values[10] == pytest.approx(4.0)
    assert pred.n_sources.min() == 14 and pred.covariate_issued_latest <= w.origin
    assert (pred.source_latest <= w.origin).all()
    dark = cov.SeriesCovariate("g", pd.Series(0.0, index=index))
    assert (WeatherSlotRatio(dark).predict(y, [w])[0].values == 0).all()


# --------------------------------------------------------------- statistics


def test_holm_step_down():
    assert run_covariates.holm([0.01, 0.04, 0.03, 0.2]) == pytest.approx([0.04, 0.09, 0.09, 0.2])


# ------------------------------------------------------------ probe logic


def _single_runs(day2: pd.Series, lead_window: tuple[int, int]):
    """Fake single runs: a run matches day2 only for leads in ``lead_window`` hours."""

    def fetch(model, variable, run, point, cache, forecast_hours=120):
        stamps = pd.date_range(run + pd.Timedelta(hours=1), periods=forecast_hours, freq="h")
        lead = (stamps - run) / pd.Timedelta(hours=1)
        base = day2.reindex(stamps).to_numpy()
        match = (lead >= lead_window[0]) & (lead < lead_window[1])
        return pd.Series(np.where(match, base, base + 50.0), index=stamps)

    return fetch


@pytest.mark.parametrize("lead_window,verified", [((48, 54), True), ((30, 36), False)])
def test_day2_semantics_check(monkeypatch, lead_window, verified):
    day2 = cov.national_mean(hourly_frame(), EQUAL)
    monkeypatch.setattr(weather, "fetch_single_run", _single_runs(day2, lead_window))
    monkeypatch.setattr(run_covariates.time, "sleep", lambda s: None)
    out = run_covariates.check_day2_semantics("m", day2, (43.6, 1.4), Path("/tmp"))
    assert out["hours_checked"] >= 20 and out["verified_n2"] is verified


def _stub_everything(monkeypatch, tmp_path, series):
    monkeypatch.setattr(run_covariates, "_series", lambda args: series)
    monkeypatch.setattr(run_covariates, "TEST_START", date(2024, 6, 1))
    monkeypatch.setattr(run_covariates, "TEST_END", date(2024, 6, 21))
    frame = hourly_frame()

    def previous_runs(model, variables, start, end, cache, points=cov.REGION_POINTS):
        weather.assert_before_seal(start, end)
        return {v: frame * (1.0 if v.endswith("day2") else 0.9) for v in variables}

    monkeypatch.setattr(weather, "fetch_previous_runs", previous_runs)
    monkeypatch.setattr(weather, "fetch_era5", lambda var, s, e, c, points=cov.REGION_POINTS: frame * 1.1)
    monkeypatch.setattr(weather, "fetch_region_weights_2023", lambda cache: (cov.normalised_weights(EQUAL), {"totals": {}}))
    monkeypatch.setattr(weather, "fetch_single_run", _single_runs(frame[run_covariates.SEMANTICS_REGION], (48, 54)))
    monkeypatch.setattr(run_covariates.time, "sleep", lambda s: None)
    model = CovEchoModel()

    def load(self):
        self._model = self._model or model
        return self._model

    monkeypatch.setattr(T0Forecaster, "load", load)
    return model


def test_probe_end_to_end_offline(monkeypatch, tmp_path):
    series = solar_series("2023-01-01", "2024-12-31 23:30")
    _stub_everything(monkeypatch, tmp_path, series)
    monkeypatch.setattr(run_covariates, "MIN_SCORABLE_DAYS", 5)
    rc = run_covariates.main(["probe", "--context-days", "10", "--results-dir", str(tmp_path), "--wx-cache", str(tmp_path)])
    assert rc == 0
    out = json.loads((tmp_path / "probe.json").read_text())
    assert out["semantics"]["verified_n2"] is True
    assert out["chosen"]["model"] == "ecmwf_ifs025" and out["chosen"]["lead_days"] == 2
    assert out["stamp"]["chosen"] in (15, 0, -15)
    assert out["era5"]["share_nonnull"] > 0.99
    assert any(line.startswith("WX_SHA256 = ") for line in out["frozen_constants"])


def test_run_end_to_end_offline(monkeypatch, tmp_path):
    series = solar_series("2024-01-01", "2024-12-31 23:30")
    model = _stub_everything(monkeypatch, tmp_path, series)
    grid = run_covariates._grid()
    frame = hourly_frame()
    wx = cov.weather_covariate(cov.national_mean(frame, EQUAL), grid, lead_days=2, stamp_offset_min=15)
    era = cov.weather_covariate(cov.national_mean(frame * 1.1, EQUAL), grid, lead_days=0, stamp_offset_min=15, oracle=True)
    for name, value in {
        "REGION_WEIGHTS": EQUAL, "STAMP_OFFSET_MIN": 15, "WX_MODEL": "ecmwf_ifs025", "WX_LEAD_DAYS": 2,
        "WX_SHA256": cov.series_sha256(wx.series, wx.issued), "ERA5_SHA256": cov.series_sha256(era.series, era.issued),
    }.items():
        monkeypatch.setattr(cov, name, value)
    rc = run_covariates.main(["run", "--context-days", "10", "--results-dir", str(tmp_path), "--wx-cache", str(tmp_path)])
    assert rc == 0
    pairwise = pd.read_csv(tmp_path / "pairwise.csv")
    assert set(zip(pairwise["model"], pairwise["reference"])) == {(m, r) for m, r, _ in run_covariates.COMPARISONS}
    assert pairwise.loc[pairwise["role"] == "secondary", "p_holm_all_hours"].notna().sum() == 4
    ranking = pd.read_csv(tmp_path / "ranking.csv")
    assert not ranking["method"].isin(run_covariates.ORACLE_METHODS).any()
    meta = json.loads((tmp_path / "run_meta.json").read_text())
    assert meta["scored_days"] == 21 and meta["covariate_issue_margin_h"]["min"] >= 0.5
    summary = (tmp_path / "summary.md").read_text()
    assert "primary" in summary and "ERA5 reference arm" in summary
    assert {c["horizon"] for c in model.calls if c["futures"] is not None} == {cov.COV_HORIZON}


def test_run_refuses_unfrozen_constants(monkeypatch, tmp_path):
    monkeypatch.setattr(cov, "WX_MODEL", None)
    with pytest.raises(SystemExit, match="not frozen"):
        run_covariates.main(["run", "--results-dir", str(tmp_path)])


def test_run_refuses_a_changed_weather_series(monkeypatch, tmp_path):
    series = solar_series("2024-01-01", "2024-12-31 23:30")
    _stub_everything(monkeypatch, tmp_path, series)
    for name, value in {"REGION_WEIGHTS": EQUAL, "STAMP_OFFSET_MIN": 15, "WX_MODEL": "ecmwf_ifs025",
                        "WX_LEAD_DAYS": 2, "WX_SHA256": "0" * 64}.items():
        monkeypatch.setattr(cov, name, value)
    with pytest.raises(SystemExit, match="differs"):
        run_covariates.main(["run", "--context-days", "10", "--results-dir", str(tmp_path), "--wx-cache", str(tmp_path)])
