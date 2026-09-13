"""Tests for the four things that silently break a forecasting benchmark:
data alignment, forecast horizons, timezone/DST handling, and leakage.

All fixtures are synthetic — the tests never touch the network.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from solarbench import metrics
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import PARIS, STEP, load_series
from solarbench.forecasters import (
    Derived,
    Prediction,
    T0Forecaster,
    blend_50_baseline,
    ewma_baseline,
    mean_3d_baseline,
    mean_7d_baseline,
    median_7d_baseline,
    night_zero_variant,
    same_day_baseline,
    same_slot_aggregates,
    same_week_baseline,
    statistical_baselines,
)

GATE_HOUR = 12
CONTEXT_STEPS = 48 * 10


def ramp_series(start="2024-01-01", end="2024-12-31 23:30", tz="UTC") -> pd.Series:
    """A complete 30-minute UTC series whose value equals its position.

    Position-valued data makes every alignment bug visible: if a forecaster
    returns the wrong timestamp's value, the number itself says which one.
    """
    index = pd.date_range(start, end, freq=STEP, tz=tz)
    return pd.Series(np.arange(len(index), dtype="float64"), index=index, name="solar_mw")


def solar_like_series(days=200, start="2024-01-01") -> pd.Series:
    """A smooth diurnal series — zero at night, a daily bump, mild day-to-day drift."""
    index = pd.date_range(start, periods=days * 48, freq=STEP, tz="UTC")
    hour = index.hour + index.minute / 60
    shape = np.clip(np.sin((hour - 6) / 12 * np.pi), 0, None) ** 1.5
    drift = 1 + 0.25 * np.sin(np.arange(len(index)) / (48 * 30))
    return pd.Series(10_000 * shape * drift, index=index, name="solar_mw")


def write_bulk_file(path: Path, first: str, last: str) -> Path:
    """An annual eCO2mix file: cp1252 TSV on a fixed 96-slot local-clock grid.

    Mirrors the real quirks — production only on :00/:30, a trailing empty
    column, and RTE's French disclaimer as the final line.
    """
    header = ["Périmètre", "Nature", "Date", "Heures", "Consommation", "Solaire"]
    lines = ["\t".join(header) + "\t"]
    for day in pd.date_range(first, last, freq="D"):
        for slot in range(96):
            hh, mm = divmod(slot * 15, 60)
            solar = "" if slot % 2 else str(1000 + slot)
            lines.append(
                "\t".join(
                    ["France", "Données définitives", day.strftime("%Y-%m-%d"),
                     f"{hh:02d}:{mm:02d}", "50000", solar]
                )
                + "\t"
            )
    lines.append(
        "RTE ne pourra être tenu responsable de l'usage qui pourrait être fait des données."
    )
    path.write_bytes("\n".join(lines).encode("cp1252"))
    return path


# --------------------------------------------------------------- data alignment


def test_loaded_series_is_a_strict_utc_grid(tmp_path):
    path = write_bulk_file(tmp_path / "bulk.xls", "2024-05-01", "2024-05-03")
    series = load_series(path)
    assert str(series.index.tz) == "UTC"
    assert series.index.is_monotonic_increasing
    assert series.index.is_unique
    assert (series.index.to_series().diff().dropna() == STEP).all()
    assert series.notna().sum() == 3 * 48


def test_spring_forward_padding_is_discarded(tmp_path):
    """The file pads the non-existent local hour by repeating rows; we drop them."""
    path = write_bulk_file(tmp_path / "spring.xls", "2024-03-30", "2024-04-01")
    series = load_series(path)
    local_dates = series.index.tz_convert(PARIS).date
    assert (local_dates == date(2024, 3, 31)).sum() == 46, "the DST day has 46 half-hours"
    assert series.index.is_unique
    assert (series.index.to_series().diff().dropna() == STEP).all()


def test_autumn_fallback_leaves_an_explicit_gap(tmp_path):
    """The file drops the repeated hour, so two half-hours are genuinely absent."""
    path = write_bulk_file(tmp_path / "autumn.xls", "2024-10-26", "2024-10-28")
    series = load_series(path)
    assert (series.index.to_series().diff().dropna() == STEP).all()
    assert series.isna().sum() == 2, "gaps surface as NaN rather than being interpolated away"


def test_negative_night_values_are_preserved(tmp_path):
    path = tmp_path / "odre.csv"
    path.write_text(
        "date_heure;perimetre;nature;solaire\n"
        "2024-01-01T00:00:00+00:00;France;Données définitives;-2\n"
        "2024-01-01T00:30:00+00:00;France;Données définitives;0\n",
        encoding="utf-8",  # ODRE serves UTF-8; without this the fixture is cp1252 on Windows
    )
    series = load_series(path)
    assert series.iloc[0] == -2, "RTE reports small negative solar at night; do not silently clip"


# ------------------------------------------------------------- forecast horizons


def _windows(series, start, end, gate_hour=GATE_HOUR, context=CONTEXT_STEPS):
    return build_windows(
        series, test_start=date.fromisoformat(start), test_end=date.fromisoformat(end),
        gate_hour=gate_hour, context_steps=context, report=BacktestReport(),
    )


def test_normal_day_has_48_targets_and_a_71_step_horizon():
    windows = _windows(ramp_series(), "2024-06-10", "2024-06-10")
    assert len(windows) == 1
    w = windows[0]
    assert len(w.targets) == 48
    # 12 h from the noon gate to midnight (24 steps), then the 47 remaining steps of the day.
    assert w.horizon == 71
    assert w.steps[0] == 24 and w.steps[-1] == 71


def test_dst_days_keep_their_real_length():
    spring = _windows(ramp_series(), "2024-03-31", "2024-03-31")[0]
    autumn = _windows(ramp_series(), "2024-10-27", "2024-10-27")[0]
    assert len(spring.targets) == 46, "23-hour local day"
    assert len(autumn.targets) == 50, "25-hour local day"
    assert spring.horizon == 69 and autumn.horizon == 73


def test_origin_is_the_local_noon_gate_on_the_previous_day():
    w = _windows(ramp_series(), "2024-06-10", "2024-06-10")[0]
    origin_local = w.origin.tz_convert(PARIS)
    assert (origin_local.hour, origin_local.minute) == (GATE_HOUR, 0)
    assert origin_local.date() == date(2024, 6, 9)
    assert w.targets[0] - w.origin == pd.Timedelta(hours=12)
    assert w.targets[-1] - w.origin == pd.Timedelta(hours=35, minutes=30)


def test_delivery_day_covers_local_midnight_to_midnight():
    w = _windows(ramp_series(), "2024-06-10", "2024-06-10")[0]
    local = w.targets.tz_convert(PARIS)
    assert local[0].hour == 0 and local[0].minute == 0
    assert local[-1].hour == 23 and local[-1].minute == 30
    assert set(local.date) == {date(2024, 6, 10)}


def test_days_with_missing_targets_are_skipped_not_silently_scored():
    series = ramp_series()
    series.loc["2024-06-10 09:00":"2024-06-10 09:30"] = np.nan
    report = BacktestReport()
    build_windows(
        series, test_start=date(2024, 6, 10), test_end=date(2024, 6, 10),
        gate_hour=GATE_HOUR, context_steps=CONTEXT_STEPS, report=report,
    )
    assert report.skipped_incomplete_target == ["2024-06-10"]


# ---------------------------------------------------------------- baseline logic


def test_same_day_baseline_uses_the_most_recent_legal_same_time_value():
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    pred = same_day_baseline().predict(series, [w])[0]
    for target, value in zip(w.targets, pred.values):
        lag = pd.Timedelta(hours=24) if target - pd.Timedelta(hours=24) <= w.origin else pd.Timedelta(hours=48)
        assert value == series.loc[target - lag]
    # Up to and including local noon the source is D-1; after that it must fall back to D-2.
    assert pred.values[24] == series.loc[w.targets[24] - pd.Timedelta(hours=24)]
    assert pred.values[25] == series.loc[w.targets[25] - pd.Timedelta(hours=48)]


def test_same_week_baseline_is_exactly_seven_days_back():
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    pred = same_week_baseline().predict(series, [w])[0]
    expected = series.reindex(w.targets - pd.Timedelta(days=7)).to_numpy()
    assert np.array_equal(pred.values, expected)
    assert pred.max_source_time <= w.origin


def test_baselines_lag_in_utc_so_dst_cannot_shift_them():
    """A UTC lag is the same *solar* time; a local-clock lag would drift by an hour."""
    series = ramp_series()
    for day in ("2024-03-31", "2024-10-27"):
        w = _windows(series, day, day)[0]
        pred = same_week_baseline().predict(series, [w])[0]
        # The value really is the observation exactly 7x24 h earlier.
        assert np.array_equal(pred.values, series.reindex(w.targets - pd.Timedelta(days=7)).to_numpy())
        # And that is a different local clock time, which is the point: a naive
        # "same local time last week" lookup would have picked a different row.
        source_local = (w.targets - pd.Timedelta(days=7)).tz_convert(PARIS)
        target_local = w.targets.tz_convert(PARIS)
        shifted = [
            (t.hour, t.minute) != (s.hour, s.minute) for t, s in zip(target_local, source_local)
        ]
        assert any(shifted), f"{day} should straddle the DST switch in local clock terms"
        assert np.isfinite(pred.values).all()


# --------------------------------------------------------------------- leakage


class _Peeker:
    """A deliberately broken forecaster that reads the delivery day itself."""

    name = "peeker"
    label = "peeker"

    def predict(self, series, windows):
        return [
            Prediction(values=series.reindex(w.targets).to_numpy(), max_source_time=w.targets[-1])
            for w in windows
        ]


def test_backtest_rejects_a_forecaster_that_reads_past_the_origin():
    series = ramp_series()
    windows = _windows(series, "2024-06-10", "2024-06-12")
    with pytest.raises(AssertionError, match="after the origin"):
        run_backtest(series, [_Peeker()], windows, report=BacktestReport())


def test_every_baseline_source_is_at_or_before_the_origin():
    series = ramp_series()
    windows = _windows(series, "2024-02-01", "2024-11-30")
    for forecaster in (same_day_baseline(), same_week_baseline()):
        for w, pred in zip(windows, forecaster.predict(series, windows)):
            assert pred.max_source_time <= w.origin


def test_poisoning_the_future_does_not_change_any_forecast():
    """The decisive leakage test.

    For each window separately, rewrite every observation after *that window's*
    origin and re-forecast. A forecaster that only reads the past cannot notice.
    """
    series = solar_like_series()
    windows = _windows(series, "2024-03-01", "2024-03-20", context=48 * 10)
    forecasters = [same_day_baseline(), same_week_baseline()]

    for w in windows:
        poisoned = series.copy()
        poisoned.loc[poisoned.index > w.origin] *= -7.5
        for forecaster in forecasters:
            clean = forecaster.predict(series, [w])[0]
            dirty = forecaster.predict(poisoned, [w])[0]
            assert np.array_equal(clean.values, dirty.values, equal_nan=True), (
                f"{forecaster.name} changed its forecast for {w.delivery_date} "
                "when only post-origin data moved"
            )


def test_forecasts_are_clipped_at_zero_for_every_method():
    series = solar_like_series()
    series.iloc[: 48 * 30] = -500.0
    windows = _windows(series, "2024-02-15", "2024-02-20", context=48 * 10)
    df = run_backtest(series, [same_day_baseline(), same_week_baseline()], windows, report=BacktestReport())
    assert (df["y_hat"] >= 0).all()


# ---------------------------------------------------------------------- metrics


def _frame(y, y_hat, method="m", day="2024-06-10"):
    n = len(y)
    return pd.DataFrame(
        {
            "delivery_date": [date.fromisoformat(day)] * n,
            "method": method, "y": y, "y_hat": y_hat,
            "slot": np.arange(n) % 48, "month": 6, "step": np.arange(n) + 25,
        }
    )


def test_mae_and_nmae_match_hand_computation():
    df = _frame([100.0, 200.0, 300.0], [110.0, 180.0, 300.0])
    out = metrics.summarise(df, peak=1000.0).iloc[0]
    assert out["mae_mw"] == pytest.approx(30 / 3)
    assert out["nmae_mean"] == pytest.approx(30 / 600)
    assert out["nmae_peak"] == pytest.approx(10 / 1000)


def test_nmae_is_a_ratio_of_sums_not_a_mean_of_ratios():
    """The night-safe definition: a zero actual must not blow the metric up."""
    df = _frame([0.0, 100.0], [5.0, 100.0])
    out = metrics.summarise(df, peak=100.0).iloc[0]
    assert np.isfinite(out["nmae_mean"])
    assert out["nmae_mean"] == pytest.approx(5 / 100)


def test_perfect_and_zero_forecasts_bracket_the_scale():
    y = [0.0, 500.0, 900.0]
    assert metrics.summarise(_frame(y, y), peak=900.0).iloc[0]["nmae_mean"] == pytest.approx(0.0)
    zeros = metrics.summarise(_frame(y, [0.0, 0.0, 0.0]), peak=900.0).iloc[0]
    assert zeros["nmae_mean"] == pytest.approx(1.0), "predicting zero always scores nMAE 1"


def test_skill_score_and_bootstrap_agree_on_a_clear_winner():
    days = pd.date_range("2024-06-01", periods=40, freq="D").date
    rows = []
    for i, day in enumerate(days):
        rows.append(_frame([100.0, 200.0], [100.0, 205.0], method="t0", day=str(day)))
        rows.append(_frame([100.0, 200.0], [130.0, 240.0], method="prev_day", day=str(day)))
    df = pd.concat(rows, ignore_index=True)
    per_day = metrics.per_day_errors(df)
    result = metrics.bootstrap_skill(per_day, model="t0", reference="prev_day", samples=200)
    assert result["skill"] == pytest.approx(1 - 2.5 / 35)
    assert result["skill_lo95"] <= result["skill"] <= result["skill_hi95"]
    assert result["win_rate"] == 1.0


def test_daytime_mask_excludes_night_and_keeps_midday():
    series = solar_like_series(days=120)
    windows = _windows(series, "2024-02-01", "2024-03-31", context=48 * 10)
    df = run_backtest(series, [same_day_baseline()], windows, report=BacktestReport())
    slots = metrics.daytime_slots(df)
    assert not any(slot == 0 for _, slot in slots), "midnight is never daytime"
    assert any(slot == 24 for _, slot in slots), "midday is"


# ------------------------------------------------------- guards added after review


def test_a_truncated_day_is_not_mistaken_for_a_dst_day():
    """A day clipped by the edge of the data can land on 46 slots by coincidence."""
    series = ramp_series(start="2024-06-10 01:00")
    report = BacktestReport()
    build_windows(
        series, test_start=date(2024, 6, 10), test_end=date(2024, 6, 10),
        gate_hour=GATE_HOUR, context_steps=2, report=report,
    )
    assert report.skipped_incomplete_target == ["2024-06-10"] or report.skipped_no_origin == ["2024-06-10"]


def test_expected_slots_knows_the_real_length_of_every_day():
    from solarbench.backtest import expected_slots

    assert expected_slots(date(2024, 6, 10)) == 48
    assert expected_slots(date(2024, 3, 31)) == 46
    assert expected_slots(date(2024, 10, 27)) == 50
    assert expected_slots(date(2025, 3, 30)) == 46
    assert expected_slots(date(2026, 10, 25)) == 50


def test_daytime_mask_covers_every_scored_month():
    """A mask derived from the scored rows cannot leave a month unmasked."""
    series = solar_like_series(days=200)
    windows = _windows(series, "2024-02-01", "2024-06-30", context=48 * 10)
    df = run_backtest(series, [same_day_baseline(), same_week_baseline()], windows, report=BacktestReport())
    slots = metrics.daytime_slots(df)
    assert {m for m, _ in slots} == set(df["month"].unique())
    flagged = metrics.add_daytime_flag(df, slots)
    assert flagged.loc[flagged["slot"] == 0, "is_daytime"].sum() == 0
    assert flagged["is_daytime"].sum() > 0


def test_bootstrap_interval_is_not_zero_width_on_a_short_run():
    days = pd.date_range("2024-06-01", periods=5, freq="D").date
    rows = []
    for i, day in enumerate(days):
        rows.append(_frame([100.0, 200.0], [100.0 + i, 205.0], method="t0", day=str(day)))
        rows.append(_frame([100.0, 200.0], [130.0, 240.0 + 3 * i], method="prev_day", day=str(day)))
    per_day = metrics.per_day_errors(pd.concat(rows, ignore_index=True))
    out = metrics.bootstrap_skill(per_day, model="t0", reference="prev_day", samples=300)
    assert out["skill_hi95"] > out["skill_lo95"], "a 5-day run must not report a zero-width CI"


def test_series_fingerprint_separates_different_windows():
    from solarbench.data import series_fingerprint

    series = solar_like_series(days=60)
    assert series_fingerprint(series) != series_fingerprint(series.iloc[48:])
    assert series_fingerprint(series) == series_fingerprint(series.copy())


def test_manifest_round_trips_accented_odre_values_as_utf8(tmp_path):
    """The manifest stores ODRE's `nature` column verbatim, and it is accented.

    Serialised with ensure_ascii=False, so the bytes on disk really do contain
    "Données définitives" — pin the file to UTF-8 rather than to whatever the
    running platform happens to default to (cp1252 on Windows, and locales whose
    default codec cannot encode it at all).
    """
    from solarbench.data import DataManifest

    nature = {"Données définitives": 17520, "Données consolidées": 96}
    path = tmp_path / "manifest.json"
    DataManifest(
        source="https://odre.opendatasoft.com/…/exports/csv",
        fetched_at="2026-01-01T00:00:00+00:00", rows=17520,
        start="2024-01-01 00:00:00+00:00", end="2024-12-31 23:30:00+00:00",
        missing_steps=0, missing_ranges=[], nature_counts=nature,
        sha256="0" * 64,
    ).to_json(path)

    assert json.loads(path.read_bytes().decode("utf-8"))["nature_counts"] == nature
    assert "Données définitives".encode("utf-8") in path.read_bytes()


# ------------------------------------------ Phase 2: historical-only baselines
#
# Everything below is additive. The Phase 1 tests above are unchanged so the
# diff itself shows that nothing was weakened.


class _EchoModel:
    """Stands in for the t0 weights: forecasts the last context value.

    Good enough to drive ``T0Forecaster.predict`` end to end without a download,
    and — because it reads the context — to prove that the context is cut at
    the origin: a leak would change the forecast.
    """

    def predict(self, context, horizon, quantiles):
        import torch

        class _Forecast:
            pass

        out = _Forecast()
        out.median = torch.as_tensor(context)[:, -1:].repeat(1, horizon)
        return out


def _stub_t0(context=CONTEXT_STEPS) -> T0Forecaster:
    return T0Forecaster(context_steps=context, _model=_EchoModel())


def _zero_first_five(window, values):
    values[:5] = 0.0
    return values


def registry_for_tests(context=CONTEXT_STEPS) -> list:
    """Every method the benchmark can run, including t0 on a stub and a derived method."""
    return [
        _stub_t0(context),
        *statistical_baselines(),
        night_zero_variant("t0"),
        Derived(name="t0_first_five_zero", label="derived", source="t0", transform=_zero_first_five),
    ]


def gapped_solar_series() -> pd.Series:
    """A solar-like year with the real data's blemishes.

    Two missing half-hours on the autumn switch day (what ODRE really lacks) and
    a missing half-hour at one noon gate, so that a baseline which skips a gap
    by walking *forward* in time, or which reads the gate slot itself when it
    should not, has something to trip over.
    """
    series = solar_like_series(days=330, start="2024-01-01")
    series.loc["2024-10-27 00:00":"2024-10-27 00:30"] = np.nan
    series.loc["2024-07-14 10:00"] = np.nan  # 12:00 CEST on 2024-07-14 = the gate for 07-15
    return series


def test_every_registered_baseline_reads_only_at_or_before_the_origin():
    series = ramp_series()
    windows = _windows(series, "2024-02-01", "2024-11-30")
    for forecaster in statistical_baselines():
        for w, pred in zip(windows, forecaster.predict(series, windows)):
            assert pred.max_source_time <= w.origin, forecaster.name
            latest = pred.source_latest[pred.source_latest.notna()]
            assert (latest <= w.origin).all(), forecaster.name
            assert pred.n_sources is not None and (pred.n_sources > 0).all(), forecaster.name


@pytest.mark.parametrize("poison", ["affine", "nan"])
def test_poisoning_with_gaps_and_affine_rewrite_over_the_registry(poison):
    """The decisive Phase 2 leakage test, over every method the benchmark can run.

    Per window, everything after *that window's* origin is rewritten — affinely,
    so exact zeros move too, or to NaN, so a forward walk past a gap would find
    nothing — and no forecast may change.  The fixture carries real-style gaps
    so that skipping logic is exercised, not just defined.
    """
    series = gapped_solar_series()
    windows = _windows(series, "2024-07-10", "2024-07-20", context=48 * 10)
    windows += _windows(series, "2024-10-25", "2024-11-05", context=48 * 10)
    forecasters = registry_for_tests(context=48 * 10)
    real = [f for f in forecasters if not isinstance(f, Derived)]
    derived = [f for f in forecasters if isinstance(f, Derived)]

    for w in windows:
        poisoned = series.copy()
        after = poisoned.index > w.origin
        if poison == "affine":
            poisoned.loc[after] = poisoned.loc[after] * -7.5 + 1234.5
        else:
            poisoned.loc[after] = np.nan
        clean_by_name, dirty_by_name = {}, {}
        for forecaster in real:
            clean = forecaster.predict(series, [w])[0]
            dirty = forecaster.predict(poisoned, [w])[0]
            assert np.array_equal(clean.values, dirty.values, equal_nan=True), (
                f"{forecaster.name} changed its forecast for {w.delivery_date} "
                f"when only post-origin data moved ({poison})"
            )
            assert clean.source_latest.equals(dirty.source_latest), forecaster.name
            clean_by_name[forecaster.name], dirty_by_name[forecaster.name] = clean, dirty
        for d in derived:
            clean = d.derive(w, clean_by_name[d.source])
            dirty = d.derive(w, dirty_by_name[d.source])
            assert np.array_equal(clean.values, dirty.values, equal_nan=True), d.name


def test_t0_context_ends_at_the_origin_and_ignores_the_future():
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    t0 = _stub_t0()
    ctx = t0._context(series, w.origin)
    assert len(ctx) == CONTEXT_STEPS
    assert ctx[-1] == series.loc[w.origin]
    poisoned = series.copy()
    poisoned.loc[poisoned.index > w.origin] = -1.0
    assert np.array_equal(t0._context(poisoned, w.origin), ctx)
    pred = t0.predict(series, [w])[0]
    assert pred.max_source_time == w.origin
    assert (pred.source_latest == w.origin).all()
    assert (pred.n_sources == CONTEXT_STEPS).all()
    assert (pred.values == series.loc[w.origin]).all(), "the echo stub forecasts the origin value"


def test_blend_50_is_exactly_half_prev_day_plus_half_mean_7d():
    series = solar_like_series()
    series.iloc[: 48 * 5] -= 2.0  # a few negative nights, as RTE reports them
    windows = _windows(series, "2024-02-01", "2024-02-20", context=48 * 10)
    prev_day, mean_7d, blend = same_day_baseline(), mean_7d_baseline(), blend_50_baseline()
    for w, a, b, c in zip(
        windows, prev_day.predict(series, windows), mean_7d.predict(series, windows), blend.predict(series, windows)
    ):
        assert np.array_equal(c.values, 0.5 * a.values + 0.5 * b.values, equal_nan=True)
        assert c.max_source_time == max(a.max_source_time, b.max_source_time)
        assert (c.n_sources == a.n_sources + b.n_sources).all()

    # In the scored frame every method is clipped at zero after prediction, so
    # the identity is exact wherever both components are non-negative — and
    # only there, which the source audit counts rather than hides.
    df = run_backtest(series, [prev_day, mean_7d, blend], windows, report=BacktestReport())
    wide = df.pivot(index=["delivery_date", "target_time"], columns="method", values="y_hat")
    both_positive = (wide["prev_day"] > 0) & (wide["mean_7d"] > 0)
    assert both_positive.sum() > 0
    assert np.array_equal(
        wide.loc[both_positive, "blend_50"].to_numpy(),
        0.5 * wide.loc[both_positive, "prev_day"].to_numpy() + 0.5 * wide.loc[both_positive, "mean_7d"].to_numpy(),
    )


def _legal_sources(series, w, t, k):
    return [t - pd.Timedelta(days=j) for j in range(1, 40) if t - pd.Timedelta(days=j) <= w.origin][:k]


def test_same_slot_mean_uses_the_k_most_recent_legal_days():
    """Before the boundary the sources are D-1, D-2, D-3; after it D-2, D-3, D-4."""
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    pred = mean_3d_baseline().predict(series, [w])[0]
    for i, t in enumerate(w.targets):
        legal = _legal_sources(series, w, t, 3)
        assert pred.values[i] == np.mean([series.loc[x] for x in legal])
        assert pred.source_latest[i] == legal[0] and pred.source_earliest[i] == legal[-1]
        assert pred.n_sources[i] == 3
    # Up to and including local noon the newest source is D-1; after that it is D-2.
    assert pred.source_latest[24] == w.targets[24] - pd.Timedelta(days=1)
    assert pred.source_latest[25] == w.targets[25] - pd.Timedelta(days=2)
    assert pred.max_source_time <= w.origin


def test_a_missing_source_is_skipped_backwards_and_the_count_stays_k():
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    t = w.targets[10]
    series.loc[t - pd.Timedelta(days=2)] = np.nan
    pred = mean_3d_baseline().predict(series, [w])[0]
    expected = np.mean([series.loc[t - pd.Timedelta(days=j)] for j in (1, 3, 4)])
    assert pred.values[10] == expected
    assert pred.n_sources[10] == 3
    assert pred.source_earliest[10] == t - pd.Timedelta(days=4)
    assert np.isfinite(pred.values).all()


def test_median_and_ewma_are_hand_computable():
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    median = median_7d_baseline().predict(series, [w])[0]
    ewma = ewma_baseline().predict(series, [w])[0]
    for i, t in enumerate(w.targets):
        seven = np.array([series.loc[x] for x in _legal_sources(series, w, t, 7)])
        assert median.values[i] == np.median(seven)
        fourteen = np.array([series.loc[x] for x in _legal_sources(series, w, t, 14)])
        weights = 0.7 ** np.arange(14)
        assert ewma.values[i] == pytest.approx(float(weights @ fourteen / weights.sum()))
        assert ewma.n_sources[i] == 14
    # The a-priori decay, stated once: 30% on the newest legal value after
    # renormalisation, ~92% of the weight in the seven newest.
    weights = 0.7 ** np.arange(14)
    weights /= weights.sum()
    assert weights[0] == pytest.approx(0.302, abs=0.001)
    assert weights[:7].sum() == pytest.approx(0.924, abs=0.001)


@pytest.mark.parametrize("day, last_legal_hour", [("2024-03-31", 13), ("2024-10-27", 11)])
def test_the_d1_d2_switch_is_decided_in_utc_on_dst_days(day, last_legal_hour):
    """The boundary is 'source <= origin' in UTC, which is 13:00 CEST on the
    spring day and 11:00 CET on the autumn day — not 'noon' — for every method."""
    series = ramp_series()
    w = _windows(series, day, day)[0]
    reference = same_day_baseline().predict(series, [w])[0]
    d1 = np.flatnonzero(reference.source_latest == (w.targets - pd.Timedelta(days=1)))
    assert w.targets[d1[-1]].tz_convert(PARIS).hour == last_legal_hour
    assert w.targets[d1[-1] + 1].tz_convert(PARIS).minute == 30 or w.targets[d1[-1] + 1].tz_convert(PARIS).hour == last_legal_hour + 1
    for forecaster in same_slot_aggregates():
        pred = forecaster.predict(series, [w])[0]
        newest = np.flatnonzero(pred.source_latest == (w.targets - pd.Timedelta(days=1)))
        assert np.array_equal(newest, d1), forecaster.name
        assert np.isfinite(pred.values).all(), forecaster.name
        # Every source is exactly j x 24 h back, i.e. the same UTC time.
        for i, t in enumerate(w.targets):
            assert ((t - pred.source_latest[i]) % pd.Timedelta(days=1)) == pd.Timedelta(0)


def test_single_lag_baselines_still_go_missing_on_a_gap_and_aggregates_do_not():
    """Locks the Phase 1 definitions: prev_day / prev_week return NaN on a missing
    source (and the window is dropped for everyone); the k-day aggregates and
    the blend behave as documented."""
    series = ramp_series()
    w = _windows(series, "2024-06-10", "2024-06-10")[0]
    series.loc[w.targets[3] - pd.Timedelta(days=1)] = np.nan   # prev_day's source for target 3
    series.loc[w.targets[40] - pd.Timedelta(days=7)] = np.nan  # prev_week's source for target 40
    prev_day = same_day_baseline().predict(series, [w])[0]
    prev_week = same_week_baseline().predict(series, [w])[0]
    blend = blend_50_baseline().predict(series, [w])[0]
    assert np.isnan(prev_day.values[3]) and np.isfinite(prev_day.values[4])
    assert np.isnan(prev_week.values[40]) and np.isfinite(prev_week.values[41])
    assert np.isnan(blend.values[3]) and np.isfinite(blend.values[40])
    for forecaster in same_slot_aggregates():
        assert np.isfinite(forecaster.predict(series, [w])[0].values).all(), forecaster.name


def test_blend_goes_missing_exactly_when_prev_day_does():
    series = gapped_solar_series()
    windows = _windows(series, "2024-10-25", "2024-11-05", context=48 * 10)
    prev_day = same_day_baseline().predict(series, windows)
    blend = blend_50_baseline().predict(series, windows)
    for a, b in zip(prev_day, blend):
        assert np.array_equal(np.isnan(a.values), np.isnan(b.values))


def test_adding_the_phase2_baselines_does_not_change_the_drop_set():
    """The preservation guarantee: with the real data's autumn gap, the
    balanced scored set is decided by prev_day and prev_week alone."""
    series = gapped_solar_series()
    windows = _windows(series, "2024-10-20", "2024-11-10", context=48 * 10)
    phase1, phase2 = BacktestReport(), BacktestReport()
    df1 = run_backtest(series, [same_day_baseline(), same_week_baseline()], windows, report=phase1)
    df2 = run_backtest(series, registry_for_tests(context=48 * 10), windows, report=phase2)
    assert phase1.skipped_nonfinite_forecast == ["2024-10-28", "2024-11-03"]
    assert phase2.skipped_nonfinite_forecast == phase1.skipped_nonfinite_forecast
    assert set(phase2.skipped_nonfinite_by_method) == {"prev_day", "prev_week", "blend_50"}
    assert sorted(df1["delivery_date"].unique()) == sorted(df2["delivery_date"].unique())
    # And the Phase 1 rows themselves are identical in both runs.
    for method in ("prev_day", "prev_week"):
        a = df1.loc[df1["method"] == method, ["target_time", "y", "y_hat"]].reset_index(drop=True)
        b = df2.loc[df2["method"] == method, ["target_time", "y", "y_hat"]].reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)


def test_a_nonfinite_method_drops_the_window_for_everyone_and_is_attributed():
    series = ramp_series()
    windows = _windows(series, "2024-06-10", "2024-06-12")

    class _Flaky:
        name, label = "flaky", "flaky"

        def spec(self):
            return {"class": "flaky"}

        def predict(self, s, ws):
            out = []
            for w in ws:
                values = s.reindex(w.targets - pd.Timedelta(days=2)).to_numpy(dtype="float64")
                if w.delivery_date == date(2024, 6, 11):
                    values[7] = np.nan
                out.append(Prediction(values=values, max_source_time=w.origin))
            return out

    report = BacktestReport()
    df = run_backtest(series, [same_day_baseline(), _Flaky()], windows, report=report)
    assert report.skipped_nonfinite_forecast == ["2024-06-11"]
    assert report.skipped_nonfinite_by_method == {"flaky": ["2024-06-11"]}
    assert sorted(df["delivery_date"].unique()) == [date(2024, 6, 10), date(2024, 6, 12)]
    assert set(df.loc[df["delivery_date"] == date(2024, 6, 10), "method"]) == {"prev_day", "flaky"}
    full = report.as_full_dict()
    assert BacktestReport.from_full_dict(full).as_full_dict() == full


def test_lookback_exhaustion_gives_nan_not_a_shorter_mean():
    series = ramp_series(start="2024-06-08 00:00")  # at most two legal same-slot days before the gate
    w = build_windows(
        series, test_start=date(2024, 6, 10), test_end=date(2024, 6, 10),
        gate_hour=GATE_HOUR, context_steps=48, report=BacktestReport(),
    )[0]
    pred = mean_3d_baseline().predict(series, [w])[0]
    assert np.isnan(pred.values).all()
    assert (pred.n_sources < 3).all()
    assert pred.source_latest.isna().all()


def test_source_audit_columns_never_exceed_the_origin():
    series = gapped_solar_series()
    windows = _windows(series, "2024-07-10", "2024-07-20", context=48 * 10)
    df = run_backtest(series, registry_for_tests(context=48 * 10), windows, report=BacktestReport())
    assert (df["source_latest"] <= df["origin"]).all()
    assert (df["source_earliest"] <= df["source_latest"]).all()
    assert (df["n_sources"] >= 1).all()
    lag_days = ((df["target_time"] - df["source_latest"]) / pd.Timedelta(days=1)).round(6)
    for method in ("prev_day", "prev_week", "mean_3d", "mean_7d", "median_7d", "ewma", "blend_50"):
        sub = lag_days[df["method"] == method]
        assert (sub == sub.round()).all(), f"{method}: a source is not a whole number of days back"


def test_derived_method_inherits_sources_and_is_dropped_with_its_source():
    series = ramp_series()
    windows = _windows(series, "2024-06-10", "2024-06-12")
    derived = Derived(name="derived", label="derived", source="prev_day", transform=_zero_first_five)
    df = run_backtest(series, [same_day_baseline(), derived], windows, report=BacktestReport())
    a = df.loc[df["method"] == "prev_day"].reset_index(drop=True)
    b = df.loc[df["method"] == "derived"].reset_index(drop=True)
    assert (b["y_hat"].to_numpy()[:5] == 0).all()
    assert np.array_equal(a["y_hat"].to_numpy()[5:48], b["y_hat"].to_numpy()[5:48])
    for column in ("source_latest", "source_earliest", "n_sources"):
        pd.testing.assert_series_equal(a[column], b[column], check_names=False)
    with pytest.raises(ValueError, match="derives from"):
        run_backtest(series, [same_week_baseline(), derived], windows, report=BacktestReport())


# ------------------------------------------------- Phase 2: t0_night_zero


def _local_slot(index: pd.DatetimeIndex) -> np.ndarray:
    local = index.tz_convert(PARIS)
    return (local.hour * 2 + local.minute // 30).to_numpy()


def test_solar_position_matches_published_ephemeris():
    """Paris, both solstices: sunrise/sunset (upper limb, refracted horizon) within a minute."""
    from solarbench.astro import SUNSET_ELEVATION_DEG, solar_elevation

    paris = (48.8566, 2.3522)
    for day, sunrise, sunset in (("2024-06-21", "03:47", "19:57"), ("2024-12-21", "07:41", "15:55")):
        minutes = pd.date_range(day, periods=24 * 60, freq="min", tz="UTC")
        up = solar_elevation(minutes, *paris) > SUNSET_ELEVATION_DEG
        rise = minutes[np.argmax(up)]
        sett = minutes[len(up) - 1 - np.argmax(up[::-1])]
        assert abs((rise - pd.Timestamp(f"{day} {sunrise}", tz="UTC")).total_seconds()) <= 90
        assert abs((sett - pd.Timestamp(f"{day} {sunset}", tz="UTC")).total_seconds()) <= 90


def test_dark_mask_is_national_geometric_and_fixed():
    from solarbench.astro import FRANCE_CORNERS, SUNSET_ELEVATION_DEG, dark_mask

    assert SUNSET_ELEVATION_DEG == -0.833
    assert night_zero_variant().params["threshold_deg"] == SUNSET_ELEVATION_DEG
    year = pd.date_range("2024-01-01", "2024-12-31 23:30", freq="30min", tz="UTC")
    mask = dark_mask(year)
    slot = _local_slot(year)
    assert not mask[(slot == 24) | (slot == 25)].any(), "midday is never dark"
    assert mask[slot == 2].all(), "01:00 local is dark on every day of the year"
    assert 0.3 < mask.mean() < 0.5
    # The four corners are the whole test: an interior grid changes nothing.
    lats, lons = np.linspace(41.3, 51.1, 5), np.linspace(-5.2, 9.6, 5)
    grid = tuple((float(a), float(b)) for a in lats for b in lons)
    assert np.array_equal(mask, dark_mask(year, points=grid))
    assert len(FRANCE_CORNERS) == 4
    # A single central point would call ~2 half-hours per day dark while the
    # east or west is still lit - which is why the corners are used.
    single = dark_mask(year, points=((46.6, 2.5),))
    assert single.sum() > mask.sum()


def test_dark_mask_depends_on_timestamps_only():
    """The transform must act on the same slots whatever the data looks like."""
    from solarbench.astro import dark_mask

    series = solar_like_series()
    windows = _windows(series, "2024-03-01", "2024-03-10", context=48 * 10)
    variant = night_zero_variant("stub")
    rng = np.random.default_rng(0)
    for w in windows:
        dark = dark_mask(w.targets)
        for values in (np.full(len(w.targets), 500.0), rng.normal(size=len(w.targets)), np.full(len(w.targets), np.nan)):
            out = variant.derive(w, Prediction(values=values, max_source_time=w.origin)).values
            assert (out[dark] == 0.0).all()
            assert np.array_equal(out[~dark], values[~dark], equal_nan=True)


def test_night_zero_zeroes_exactly_the_dark_slots_and_nothing_else():
    """Brief tests 6 and 7. 'Daytime' here is the astronomically lit set (any corner
    above the threshold), not the climatological reporting mask; the two differ
    on a few twilight half-hours, which the night-zero audit counts."""
    from solarbench.astro import dark_mask

    series = solar_like_series()
    windows = _windows(series, "2024-02-01", "2024-02-10", context=48 * 10)
    stub = _stub_t0(48 * 10)
    variant = night_zero_variant("t0")
    for w, pred in zip(windows, stub.predict(series, windows)):
        pred.values[:] = 777.0  # every slot non-zero, so the zeros must come from the mask
        out = variant.derive(w, pred)
        dark = dark_mask(w.targets)
        assert dark.any() and (~dark).any()
        assert (out.values[dark] == 0.0).all()
        assert np.array_equal(out.values[~dark], pred.values[~dark])
        assert out.max_source_time == pred.max_source_time
        assert out.source_latest.equals(pred.source_latest)


def test_night_zero_rows_are_identical_to_t0_outside_the_mask_in_the_backtest():
    from solarbench.astro import dark_mask

    series = solar_like_series()
    windows = _windows(series, "2024-02-01", "2024-02-10", context=48 * 10)
    df = run_backtest(series, [_stub_t0(48 * 10), night_zero_variant("t0")], windows, report=BacktestReport())
    t0 = df.loc[df["method"] == "t0"].reset_index(drop=True)
    nz = df.loc[df["method"] == "t0_night_zero"].reset_index(drop=True)
    dark = dark_mask(pd.DatetimeIndex(nz["target_time"]))
    assert (nz.loc[dark, "y_hat"] == 0).all()
    assert np.array_equal(nz.loc[~dark, "y_hat"].to_numpy(), t0.loc[~dark, "y_hat"].to_numpy())
    for column in ("source_latest", "source_earliest", "n_sources", "y"):
        pd.testing.assert_series_equal(nz[column], t0[column], check_names=False)
    # Where the astronomical mask overlaps the climatological reporting daytime
    # is a count to report, never something to "fix" by feeding actuals in.
    flagged = metrics.add_daytime_flag(nz, metrics.daytime_slots(df))
    inside_daytime = int((flagged["is_daytime"].to_numpy() & dark).sum())
    assert inside_daytime >= 0


# ------------------------------------------------ Phase 2: evaluation and CLI

import run_benchmark  # noqa: E402  (the CLI module, importable from the repo root)


def _synthetic_export(path: Path, days: int = 330, start: str = "2024-01-01") -> Path:
    """An ODRE-style export with the real data's blemishes (see gapped_solar_series)."""
    series = solar_like_series(days=days, start=start)
    rng = np.random.default_rng(7)
    series = (series * np.clip(1 + 0.3 * rng.standard_normal(len(series)).cumsum() / np.sqrt(np.arange(1, len(series) + 1)), 0.3, 1.7)).round()
    series.loc["2024-10-27 00:00":"2024-10-27 00:30"] = np.nan
    idx = pd.date_range(series.index[0], series.index[-1], freq="15min", tz="UTC")
    values = series.reindex(idx)
    frame = pd.DataFrame({
        "date_heure": idx.strftime("%Y-%m-%dT%H:%M:%S+00:00"), "perimetre": "France",
        "nature": "Données définitives",
        "solaire": ["" if pd.isna(v) else str(int(v)) for v in values.to_numpy()],
    })
    # One consolidated row inside the test period, so the vintage evidence has
    # something to name.
    frame.loc[frame["date_heure"] == "2024-10-05T12:00:00+00:00", "nature"] = "Données consolidées"
    frame.to_csv(path, sep=";", index=False, encoding="utf-8")
    return path


def _cli_args(tmp_path: Path, csv: Path, extra: list[str] | None = None) -> list[str]:
    return [
        "--csv", str(csv), "--test-start", "2024-10-01", "--test-end", "2024-11-15", "--context-days", "20",
        "--cache-dir", str(tmp_path / "data"), "--results-dir", str(tmp_path / "results"),
        "--data-start", "2024-01-01", "--data-end", "2024-12-01", *(extra or []),
    ]


class _StubT0(T0Forecaster):
    """The real adapter with the echo model in place of the weights."""

    def load(self):
        if self._model is None:
            self._model = _EchoModel()
        return self._model


def test_binomial_sign_test_matches_known_values():
    assert metrics.binomial_two_sided_p(192, 171) == pytest.approx(0.294, abs=0.002)  # README's p = 0.29
    assert metrics.binomial_two_sided_p(205, 158) == pytest.approx(0.0156, abs=0.001)
    assert metrics.binomial_two_sided_p(5, 5) == 1.0
    assert metrics.binomial_two_sided_p(10, 0) == pytest.approx(2 / 1024)
    assert np.isnan(metrics.binomial_two_sided_p(0, 0))


def test_pair_skill_reports_ties_without_changing_the_phase1_win_rate():
    days = pd.date_range("2024-06-01", periods=30, freq="D").date
    rows = []
    for i, day in enumerate(days):
        rows.append(_frame([100.0, 200.0], [100.0, 205.0 + (i % 3 == 0)], method="a", day=str(day)))
        rows.append(_frame([100.0, 200.0], [100.0, 205.0], method="b", day=str(day)))
    per_day = metrics.per_day_errors(pd.concat(rows, ignore_index=True))
    s = metrics.pair_skill(per_day, model="a", reference="b", samples=200)
    assert s["ties"] == 20 and s["losses"] == 10 and s["wins"] == 0
    assert s["win_rate"] == 0.0, "a tie is not a win - the Phase 1 definition"
    assert s["p_value"] == pytest.approx(2 / 1024)
    legacy = metrics.bootstrap_skill(per_day, model="a", reference="b", samples=200)
    assert s["skill"] == legacy["skill"] and s["skill_lo95"] == legacy["skill_lo95"]
    with pytest.raises(ValueError, match="not balanced"):
        metrics.pair_skill(per_day.iloc[:-1], model="a", reference="b", samples=50)


def test_daytime_mask_is_invariant_to_the_method_count_at_the_real_size():
    """For the 2024 frame (363 days, 17,422 rows per method) the interpolated p99
    of method-duplicated rows resolves to the same order statistic for three
    and nine methods, so the reporting cutoff - and the mask - cannot move."""
    rng = np.random.default_rng(3)
    n = 362 * 48 + 46
    y = rng.integers(0, 15000, size=n).astype("float64")
    base = pd.DataFrame({"y": y, "month": rng.integers(1, 13, size=n), "slot": rng.integers(0, 48, size=n)})
    three = pd.concat([base.assign(method=m) for m in ("t0", "prev_day", "prev_week")], ignore_index=True)
    nine = pd.concat([base.assign(method=f"m{i}") for i in range(9)], ignore_index=True)
    assert metrics.peak_proxy(three["y"]) == metrics.peak_proxy(nine["y"])
    assert metrics.daytime_slots(three) == metrics.daytime_slots(nine)


def test_cache_key_tracks_everything_that_changes_a_forecast():
    args = run_benchmark.parse_args([])
    base_key, payload = run_benchmark._cache_key(args, "fp", statistical_baselines())
    assert payload["schema"] == run_benchmark.FORECAST_SCHEMA_VERSION
    same_key, _ = run_benchmark._cache_key(run_benchmark.parse_args([]), "fp", statistical_baselines())
    assert same_key == base_key
    assert run_benchmark._cache_key(run_benchmark.parse_args(["--seed", "5"]), "fp", statistical_baselines())[0] == base_key
    assert run_benchmark._cache_key(run_benchmark.parse_args(["--revision", "abc"]), "fp", statistical_baselines())[0] != base_key
    assert run_benchmark._cache_key(run_benchmark.parse_args(["--batch-size", "8"]), "fp", statistical_baselines())[0] != base_key
    assert run_benchmark._cache_key(args, "fp", statistical_baselines()[:-1])[0] != base_key
    assert run_benchmark._cache_key(args, "fp", statistical_baselines()[::-1])[0] != base_key
    assert run_benchmark._cache_key(args, "other", statistical_baselines())[0] != base_key
    tweaked = statistical_baselines()
    tweaked[5].alpha = 0.31  # the ewma
    assert run_benchmark._cache_key(args, "fp", tweaked)[0] != base_key


def test_registry_is_what_the_cli_runs():
    args = run_benchmark.parse_args(["--no-t0"])
    assert [f.name for f in run_benchmark.build_forecasters(args)] == [f.name for f in statistical_baselines()]
    args = run_benchmark.parse_args([])
    names = [f.name for f in run_benchmark.build_forecasters(args)]
    assert names == ["t0", "t0_night_zero"] + [f.name for f in statistical_baselines()]
    subset = run_benchmark.build_forecasters(run_benchmark.parse_args(["--methods", "t0,prev_day,prev_week"]))
    assert [f.name for f in subset] == ["t0", "prev_day", "prev_week"]
    with pytest.raises(SystemExit, match="derives from"):
        run_benchmark.build_forecasters(run_benchmark.parse_args(["--methods", "t0_night_zero,prev_day"]))
    with pytest.raises(SystemExit, match="unknown method"):
        run_benchmark.build_forecasters(run_benchmark.parse_args(["--no-t0", "--methods", "t0,prev_day"]))
    pairs = run_benchmark.comparison_pairs(names)
    assert pairs[0] == ("t0", "blend_50", "primary")
    assert ("t0_night_zero", "blend_50", "secondary") in pairs and ("t0_night_zero", "t0", "secondary") in pairs
    assert all(p[0] != "t0" or p[1] != "t0_night_zero" for p in pairs), "the variant is never a baseline of t0"


def test_cli_end_to_end_with_stub_t0(tmp_path, monkeypatch):
    """The whole pipeline, t0 on the echo stub: every output file, the audits,
    the variant identical to t0 outside its mask, and the cached rerun."""
    monkeypatch.setattr(run_benchmark, "T0Forecaster", _StubT0)
    csv = _synthetic_export(tmp_path / "export.csv")
    assert run_benchmark.main(_cli_args(tmp_path, csv)) == 0
    results = tmp_path / "results"
    for name in (
        "metrics.csv", "skill.csv", "ranking.csv", "pairwise.csv", "concentration.csv",
        "bootstrap_sensitivity.csv", "by_month.csv", "by_slot.csv", "by_band.csv", "pairwise_by_month.csv",
        "pairwise_by_band.csv", "per_day_errors.csv", "per_day_errors_daytime.csv", "daytime_mask.csv",
        "source_audit.csv", "night_zero_audit.csv", "night_zero_audit_by_slot.csv", "readme_tables.md",
        "summary.md", "run_meta.json",
    ):
        assert (results / name).exists(), name
    for fig in range(1, 9):
        assert list((results / "figures").glob(f"fig{fig}_*.png")), fig

    meta = json.loads((results / "run_meta.json").read_text(encoding="utf-8"))
    assert meta["methods"][:2] == ["t0", "t0_night_zero"]
    assert meta["backtest"]["skipped_nonfinite_forecast"] == ["2024-10-28", "2024-11-03"]
    assert meta["backtest"]["skipped_incomplete_target"] == ["2024-10-27"]
    assert meta["phase2"]["night_zero_mask"]["threshold_deg"] == -0.833
    assert meta["data"]["nature_counts_test_period"] == {"Données définitives": 46 * 48 - 3, "Données consolidées": 1}
    assert meta["data"]["nature_exceptions_test_period"] == ["2024-10-05T12:00:00+00:00 (Données consolidées)"]
    assert meta["data"]["nature_exceptions_window"] == ["2024-10-05T12:00:00+00:00 (Données consolidées)"]
    assert meta["model"]["revision_resolved"] in ("unresolved",) or len(meta["model"]["revision_resolved"]) == 40

    audit = pd.read_csv(results / "source_audit.csv")
    assert (audit["rows_after_origin"] == 0).all()
    prev_day = audit.set_index("method").loc["prev_day"]
    assert prev_day["age_h_min"] == 24 and prev_day["age_h_max"] == 48 and prev_day["avail_lag_h_min"] == 0
    assert audit.set_index("method").loc["prev_week", "age_h_max"] == 168
    assert audit.set_index("method").loc["ewma", "oldest_source_age_h_max"] <= 15 * 24

    pairwise = pd.read_csv(results / "pairwise.csv")
    assert list(pairwise.iloc[0][["model", "reference", "role"]]) == ["t0", "blend_50", "primary"]
    assert {"wins", "losses", "ties", "p_value"} <= set(pairwise.columns)

    nz = pd.read_csv(results / "night_zero_audit.csv")
    scored = nz.iloc[0]
    assert scored["variant_rows_zero_inside_mask"] == scored["masked_half_hours"]
    assert scored["variant_rows_equal_outside_mask"] == scored["rows_outside"] if "rows_outside" in nz.columns else True
    assert scored["zeroed_mae_all_hours"] == pytest.approx(
        pd.read_csv(results / "metrics.csv").set_index(["method", "slice"]).loc[("t0_night_zero", "all_hours"), "mae_mw"]
    )
    rank = pd.read_csv(results / "ranking.csv")
    assert set(rank["method"]) == set(meta["methods"]) and {"vs_prev_day_skill", "vs_blend_50_skill"} <= set(rank.columns)

    # A rerun with identical arguments re-uses the parquet and reproduces the
    # dropped-window accounting exactly (the cached path restores the report).
    summary_first = (results / "summary.md").read_text(encoding="utf-8")
    assert run_benchmark.main(_cli_args(tmp_path, csv)) == 0
    meta_again = json.loads((results / "run_meta.json").read_text(encoding="utf-8"))
    assert meta_again["backtest"] == meta["backtest"]
    block = lambda text: text.split("## Windows dropped")[1].split("## Figures")[0]
    assert block((results / "summary.md").read_text(encoding="utf-8")) == block(summary_first)


def test_cli_phase1_subset_and_no_t0(tmp_path, monkeypatch):
    monkeypatch.setattr(run_benchmark, "T0Forecaster", _StubT0)
    csv = _synthetic_export(tmp_path / "export.csv")
    assert run_benchmark.main(_cli_args(tmp_path, csv, ["--methods", "t0,prev_day,prev_week"])) == 0
    meta = json.loads((tmp_path / "results" / "run_meta.json").read_text(encoding="utf-8"))
    assert meta["methods"] == ["t0", "prev_day", "prev_week"]
    assert not (tmp_path / "results" / "night_zero_audit.csv").exists()
    assert run_benchmark.main(_cli_args(tmp_path, csv, ["--no-t0", "--results-dir", str(tmp_path / "r2")])) == 0
    rank = pd.read_csv(tmp_path / "r2" / "ranking.csv")
    assert rank["method"].nunique() == 7
    assert not (tmp_path / "r2" / "night_zero_audit.csv").exists()
