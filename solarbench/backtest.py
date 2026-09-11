"""Rolling-origin day-ahead backtest.

One forecast per delivery day, issued at the European day-ahead gate: 12:00
Europe/Paris on D-1, covering the whole of delivery day D (00:00-24:00 local).
Horizons therefore run from +12 h to +35.5 h (steps 24 to 71 of a 30-minute grid).

Delivery days are defined in local time (that is what a market day is) but every
timestamp is handled in UTC, so the 46- and 50-slot days at the DST switches are
forecast correctly instead of being silently misaligned or skipped.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Sequence

import numpy as np
import pandas as pd

from solarbench.data import PARIS, STEP
from solarbench.forecasters import Forecaster, Window

log = logging.getLogger(__name__)


@dataclass
class BacktestReport:
    """What was forecast, and what was dropped and why."""

    n_windows: int = 0
    skipped_no_origin: list[str] = field(default_factory=list)
    skipped_short_history: list[str] = field(default_factory=list)
    skipped_incomplete_target: list[str] = field(default_factory=list)
    skipped_nonfinite_forecast: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "n_windows": self.n_windows,
            "skipped_no_origin": len(self.skipped_no_origin),
            "skipped_short_history": len(self.skipped_short_history),
            "skipped_incomplete_target": len(self.skipped_incomplete_target),
            "skipped_nonfinite_forecast": len(self.skipped_nonfinite_forecast),
            "skipped_dates": sorted(
                self.skipped_no_origin
                + self.skipped_short_history
                + self.skipped_incomplete_target
                + self.skipped_nonfinite_forecast
            )[:40],
        }


def expected_slots(day: date) -> int:
    """How many 30-minute steps that local calendar day really has: 48, or 46/50 at a DST switch."""
    start = pd.Timestamp(year=day.year, month=day.month, day=day.day, tz=PARIS)
    nxt = day + timedelta(days=1)
    end = pd.Timestamp(year=nxt.year, month=nxt.month, day=nxt.day, tz=PARIS)
    return int((end - start) / STEP)


def local_day_index(index: pd.DatetimeIndex) -> dict[date, pd.DatetimeIndex]:
    """Group UTC timestamps by the Europe/Paris calendar day they fall in."""
    local = index.tz_convert(PARIS)
    groups: dict[date, list[pd.Timestamp]] = defaultdict(list)
    for utc_ts, local_ts in zip(index, local):
        groups[local_ts.date()].append(utc_ts)
    return {d: pd.DatetimeIndex(v) for d, v in groups.items()}


def build_windows(
    series: pd.Series,
    *,
    test_start: date,
    test_end: date,
    gate_hour: int,
    context_steps: int,
    report: BacktestReport | None = None,
) -> list[Window]:
    """Build one valid window per delivery day in ``[test_start, test_end]``."""
    report = report if report is not None else BacktestReport()
    by_day = local_day_index(series.index)
    available = series.index
    windows: list[Window] = []

    day = test_start
    while day <= test_end:
        targets = by_day.get(day)
        # Build the gate on D-1 in local time. Subtracting 24 h from local noon
        # on D would instead move absolute time and land on 11:00 or 13:00 at
        # the DST switches.
        gate_day = day - timedelta(days=1)
        try:
            origin = pd.Timestamp(
                year=gate_day.year, month=gate_day.month, day=gate_day.day,
                hour=gate_hour, tz=PARIS,
            ).tz_convert("UTC")
        except Exception:  # a gate hour that does not exist locally that day
            report.skipped_no_origin.append(str(day))
            day += timedelta(days=1)
            continue

        if targets is None or len(targets) == 0 or origin not in available:
            report.skipped_no_origin.append(str(day))
        elif len(targets) != expected_slots(day) or series.loc[targets].isna().any():
            report.skipped_incomplete_target.append(str(day))
        elif len(available[available <= origin]) < context_steps:
            report.skipped_short_history.append(str(day))
        else:
            window = Window(delivery_date=day, origin=origin, targets=targets)
            if window.targets[0] <= window.origin:
                raise AssertionError(f"{day}: first target {window.targets[0]} is not after origin {origin}")
            windows.append(window)
        day += timedelta(days=1)

    report.n_windows = len(windows)
    log.info("built %d windows (%s .. %s)", len(windows), test_start, test_end)
    return windows


def run_backtest(
    series: pd.Series,
    forecasters: Sequence[Forecaster],
    windows: Sequence[Window],
    *,
    report: BacktestReport | None = None,
) -> pd.DataFrame:
    """Run every forecaster over every window and return one tidy frame.

    Windows where any method produces a non-finite value are dropped for all
    methods, so the comparison stays balanced.
    """
    report = report if report is not None else BacktestReport()
    predictions: dict[str, list] = {}
    for forecaster in forecasters:
        preds = forecaster.predict(series, windows)
        if len(preds) != len(windows):
            raise AssertionError(f"{forecaster.name} returned {len(preds)} predictions for {len(windows)} windows")
        for window, pred in zip(windows, preds):
            # The leakage contract, asserted rather than assumed.
            if pred.max_source_time > window.origin:
                raise AssertionError(
                    f"{forecaster.name} used {pred.max_source_time} to forecast "
                    f"{window.delivery_date}, after the origin {window.origin}"
                )
            if len(pred.values) != len(window.targets):
                raise AssertionError(
                    f"{forecaster.name} returned {len(pred.values)} values for "
                    f"{len(window.targets)} targets on {window.delivery_date}"
                )
        predictions[forecaster.name] = preds

    keep = [
        i
        for i in range(len(windows))
        if all(np.isfinite(predictions[f.name][i].values).all() for f in forecasters)
    ]
    for i in set(range(len(windows))) - set(keep):
        report.skipped_nonfinite_forecast.append(str(windows[i].delivery_date))
    if len(keep) < len(windows):
        log.warning("dropped %d windows with non-finite forecasts", len(windows) - len(keep))

    rows = []
    for i in keep:
        window = windows[i]
        local = window.targets.tz_convert(PARIS)
        base = {
            "delivery_date": window.delivery_date,
            "origin": window.origin,
            "target_time": window.targets,
            "step": window.steps,
            "local_time": local,
            "slot": local.hour * 2 + (local.minute // 30),
            "month": [t.month for t in local],
            "y": series.loc[window.targets].to_numpy(dtype="float64"),
        }
        for forecaster in forecasters:
            values = np.clip(predictions[forecaster.name][i].values, 0.0, None)
            rows.append(pd.DataFrame({**base, "method": forecaster.name, "y_hat": values}))

    if not rows:
        raise RuntimeError("no usable windows - check the test period and the data coverage")
    out = pd.concat(rows, ignore_index=True)
    report.n_windows = len(keep)
    log.info("backtest produced %d rows over %d delivery days", len(out), len(keep))
    return out
