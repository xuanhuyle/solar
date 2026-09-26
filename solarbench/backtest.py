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
from solarbench.forecasters import Derived, Forecaster, Prediction, Window

log = logging.getLogger(__name__)


@dataclass
class BacktestReport:
    """What was forecast, and what was dropped and why."""

    n_windows: int = 0
    skipped_no_origin: list[str] = field(default_factory=list)
    skipped_short_history: list[str] = field(default_factory=list)
    skipped_incomplete_target: list[str] = field(default_factory=list)
    skipped_nonfinite_forecast: list[str] = field(default_factory=list)
    #: Which method(s) were non-finite on each dropped delivery day.
    skipped_nonfinite_by_method: dict[str, list[str]] = field(default_factory=dict)

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

    def as_full_dict(self) -> dict:
        """Everything, untruncated and attributed — for report.json and run_meta."""
        return {
            "n_windows": self.n_windows,
            "skipped_no_origin": sorted(self.skipped_no_origin),
            "skipped_short_history": sorted(self.skipped_short_history),
            "skipped_incomplete_target": sorted(self.skipped_incomplete_target),
            "skipped_nonfinite_forecast": sorted(self.skipped_nonfinite_forecast),
            "skipped_nonfinite_by_method": {
                k: sorted(v) for k, v in sorted(self.skipped_nonfinite_by_method.items())
            },
        }

    @classmethod
    def from_full_dict(cls, d: dict) -> "BacktestReport":
        return cls(
            n_windows=int(d.get("n_windows", 0)),
            skipped_no_origin=list(d.get("skipped_no_origin", [])),
            skipped_short_history=list(d.get("skipped_short_history", [])),
            skipped_incomplete_target=list(d.get("skipped_incomplete_target", [])),
            skipped_nonfinite_forecast=list(d.get("skipped_nonfinite_forecast", [])),
            skipped_nonfinite_by_method={
                k: list(v) for k, v in d.get("skipped_nonfinite_by_method", {}).items()
            },
        )


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


def quantile_column(level: float) -> str:
    """``q10`` for 0.1, ``q25`` for 0.25, ..."""
    return f"q{int(round(level * 100)):02d}"


def _check_contract(name: str, window: Window, pred: Prediction, *, oracle: bool = False) -> None:
    """The leakage contract, asserted rather than assumed.

    Target history must end at the origin for every method.  Covariate values
    must have been issued by the origin too, except for an explicitly declared
    ``oracle`` reference arm, which is never reported as a finding.
    """
    issued = pred.covariate_issued_latest
    if not oracle and issued is not None and pd.notna(issued) and issued > window.origin:
        raise AssertionError(
            f"{name} read a covariate value issued at {issued} to forecast "
            f"{window.delivery_date}, after the origin {window.origin}"
        )
    if pd.notna(pred.max_source_time) and pred.max_source_time > window.origin:
        raise AssertionError(
            f"{name} used {pred.max_source_time} to forecast "
            f"{window.delivery_date}, after the origin {window.origin}"
        )
    if pred.source_latest is not None:
        late = pred.source_latest[pred.source_latest.notna() & (pred.source_latest > window.origin)]
        if len(late):
            raise AssertionError(
                f"{name} used {late[0]} to forecast {window.delivery_date}, after the origin {window.origin}"
            )
    if len(pred.values) != len(window.targets):
        raise AssertionError(
            f"{name} returned {len(pred.values)} values for "
            f"{len(window.targets)} targets on {window.delivery_date}"
        )


def run_backtest(
    series: pd.Series,
    forecasters: Sequence[Forecaster | Derived],
    windows: Sequence[Window],
    *,
    report: BacktestReport | None = None,
    oracle_methods: frozenset[str] = frozenset(),
) -> pd.DataFrame:
    """Run every forecaster over every window and return one tidy frame.

    Derived methods are built after every real forecaster has predicted, from
    the source method's own predictions.  Windows where any method produces a
    non-finite value are dropped for all methods, so the comparison stays
    balanced.

    ``oracle_methods`` is the second key of the oracle exemption: a method
    whose covariates are flagged ``oracle`` must be listed here, and carry
    ``oracle`` in its name, or the run stops - and a listed method that is
    not flagged stops it too.  A derived method inherits its source's flag.
    """
    report = report if report is not None else BacktestReport()
    predictions: dict[str, list[Prediction]] = {}
    real = [f for f in forecasters if not isinstance(f, Derived)]
    derived = [f for f in forecasters if isinstance(f, Derived)]

    flags: dict[str, bool] = {f.name: bool(getattr(f, "oracle", False)) for f in real}
    for d in derived:
        flags[d.name] = flags.get(d.source, False)
    for name, flagged in flags.items():
        listed = name in oracle_methods
        if flagged != listed:
            raise AssertionError(
                f"{name}: oracle covariates {'present' if flagged else 'absent'} but "
                f"{'not ' if not listed else ''}declared in oracle_methods"
            )
        if flagged and "oracle" not in name.split("_"):
            raise AssertionError(f"{name}: an oracle arm must carry 'oracle' in its name")
    unknown = sorted(set(oracle_methods) - set(flags))
    if unknown:
        raise AssertionError(f"oracle_methods names methods that are not run: {unknown}")

    for forecaster in real:
        preds = forecaster.predict(series, windows)
        if len(preds) != len(windows):
            raise AssertionError(f"{forecaster.name} returned {len(preds)} predictions for {len(windows)} windows")
        for window, pred in zip(windows, preds):
            _check_contract(forecaster.name, window, pred, oracle=flags[forecaster.name])
        predictions[forecaster.name] = preds

    for d in derived:
        if d.source not in predictions:
            raise ValueError(f"{d.name} derives from {d.source!r}, which is not among the methods run")
        preds = [d.derive(w, p) for w, p in zip(windows, predictions[d.source])]
        for window, pred in zip(windows, preds):
            _check_contract(d.name, window, pred, oracle=flags[d.name])
        predictions[d.name] = preds

    keep = []
    for i, window in enumerate(windows):
        bad = [f.name for f in forecasters if not np.isfinite(predictions[f.name][i].values).all()]
        if bad:
            report.skipped_nonfinite_forecast.append(str(window.delivery_date))
            for name in bad:
                report.skipped_nonfinite_by_method.setdefault(name, []).append(str(window.delivery_date))
        else:
            keep.append(i)
    if len(keep) < len(windows):
        log.warning("dropped %d windows with non-finite forecasts", len(windows) - len(keep))

    # Only the covariate slice adds this column, so Experiment 0 frames are unchanged.
    with_covariates = any(p.covariate_issued_latest is not None for preds in predictions.values() for p in preds)
    # Likewise only probabilistic methods (Experiment 3) add quantile columns.
    levels = sorted({lv for preds in predictions.values() for p in preds if p.quantiles is not None
                     for lv in p.quantile_levels})
    rows = []
    for i in keep:
        window = windows[i]
        local = window.targets.tz_convert(PARIS)
        n = len(window.targets)
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
            pred = predictions[forecaster.name][i]
            values = np.clip(pred.values, 0.0, None)
            latest = pred.source_latest if pred.source_latest is not None else pd.DatetimeIndex([pred.max_source_time] * n)
            earliest = pred.source_earliest if pred.source_earliest is not None else pd.DatetimeIndex([pd.NaT] * n, tz="UTC")
            n_sources = pred.n_sources if pred.n_sources is not None else np.full(n, np.nan)
            frame = {
                **base,
                "method": forecaster.name,
                "y_hat": values,
                "source_latest": latest,
                "source_earliest": earliest,
                "n_sources": np.asarray(n_sources, dtype="float64"),
            }
            if with_covariates:
                issued = pred.covariate_issued_latest
                frame["cov_issued_latest"] = pd.DatetimeIndex(
                    [issued if issued is not None else pd.NaT] * n, tz="UTC"
                )
            for level in levels:
                column = np.full(n, np.nan)
                if pred.quantiles is not None and level in pred.quantile_levels:
                    column = np.clip(pred.quantiles[:, pred.quantile_levels.index(level)], 0.0, None)
                frame[quantile_column(level)] = column
            rows.append(pd.DataFrame(frame))

    if not rows:
        raise RuntimeError("no usable windows - check the test period and the data coverage")
    out = pd.concat(rows, ignore_index=True)
    report.n_windows = len(keep)
    log.info("backtest produced %d rows over %d delivery days", len(out), len(keep))
    return out
