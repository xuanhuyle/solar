"""Tests for the four things that silently break a forecasting benchmark:
data alignment, forecast horizons, timezone/DST handling, and leakage.

All fixtures are synthetic — the tests never touch the network.
"""

from __future__ import annotations

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
from solarbench.forecasters import Prediction, Window, same_day_baseline, same_week_baseline

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
        "2024-01-01T00:30:00+00:00;France;Données définitives;0\n"
    )
    series = load_series(path)
    assert series.iloc[0] == -2, "RTE reports small negative solar at night; do not silently clip"


# ------------------------------------------------------------- forecast horizons


def _windows(series, start, end, gate_hour=GATE_HOUR, context=CONTEXT_STEPS):
    return build_windows(
        series, test_start=date.fromisoformat(start), test_end=date.fromisoformat(end),
        gate_hour=gate_hour, context_steps=context, report=BacktestReport(),
    )


def test_normal_day_has_48_targets_and_a_72_step_horizon():
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
