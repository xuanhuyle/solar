"""Experiment 3, "t0 strengths probe": four probes of what t0 is designed to be good at.

``PROBES`` below is the frozen specification: question, t0 arm, comparator (the
best simple method), metric and success rule for each probe.  It was committed
before any probe was run and must not be edited afterwards; results are read
against it, not the other way round.

The new methods here all obey the benchmark's leakage contract and are covered
by the poisoning tests in ``tests/test_probes.py``:

* ``EmpiricalQuantiles`` - a base forecast plus the empirical quantiles of the
  base's own past day-ahead errors (the simple probabilistic comparator);
* ``BiasCorrected`` - a base forecast plus an EWMA of those errors;
* ``ResidualT0`` - a base forecast plus t0's forecast of the base's residuals;
* ``T0JointForecaster`` - t0 on the 12 regional solar series at once, summed;
* ``HolidayCovariate`` - French public holidays, from the calendar alone;
* ``ReferenceForecast`` - a published forecast (RTE's own), reference only.

Past errors come from ``past_windows``, which builds each past delivery day
from the calendar alone.  It never looks at the data, so rewriting or blanking
anything after an origin cannot change which past days exist.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Sequence

import numpy as np
import pandas as pd

from solarbench.data import PARIS, STEP
from solarbench.forecasters import (
    EWMA_ALPHA,
    EWMA_SOURCES,
    Prediction,
    SameSlotAggregate,
    T0Forecaster,
    Window,
    _NonFiniteWatcher,
    _from_utc64,
    _index_max,
    _utc64,
)

log = logging.getLogger(__name__)

# ------------------------------------------------------------ frozen spec

ALPHA = 0.05
#: t0's native quantile levels (tfc-t0 0.3.2 config): nothing is interpolated.
T0_LEVELS = (0.1, 0.25, 0.5, 0.75, 0.9)
#: P1 success also needs t0's 10-90 band to cover this share of daytime actuals.
COVERAGE_BAND = (0.70, 0.90)
#: Empirical error quantiles: the last 28 legal same-slot days, at least 14.
EQ_WINDOW_DAYS, EQ_MIN_N, EQ_LOOKBACK_DAYS = 28, 14, 35
#: Context of the residual model: 60 days of the base model's past errors.
RESID_CONTEXT_DAYS = 60
#: Regional joint forecast: samples per t0 call (12 rows each).
JOINT_BATCH = 8
#: P3 is run only if at least this many 2024 days have regional data.
MIN_P3_DAYS = 200
#: P4 comparator: the lowest-MAE of these on 2023 (not the test year).
P4_CANDIDATES = ("prev_day", "prev_week", "mean_7d", "ewma", "blend_50", "weekday_mean_4w")


@dataclass(frozen=True)
class Probe:
    id: str
    question: str
    t0_arm: str
    comparator: str
    metric: str
    success: str
    secondary: tuple[tuple[str, str, str], ...]
    days: str


PROBES: tuple[Probe, ...] = (
    Probe(
        id="P1",
        question="Are t0's uncertainty bands better than simple bands around the best simple forecast?",
        t0_arm="t0_wx_night_zero",
        comparator="wx_ratio_eq_night_zero",
        metric="pinball",
        success="pinball skill > 0 with Holm p < 0.05, and t0's 10-90 band covers 70-90% of daytime actuals",
        secondary=(("wx_ratio_t0res_night_zero", "wx_ratio_eq_night_zero", "pinball"),),
        days="2024 days with complete weather covariates (as the covariate slice)",
    ),
    Probe(
        id="P2",
        question="Can t0 correct the errors of the best simple forecast?",
        t0_arm="wx_ratio_t0res_night_zero",
        comparator="wx_ratio",
        metric="mae",
        success="MAE skill > 0 with Holm p < 0.05",
        secondary=(("wx_ratio_t0res_night_zero", "wx_ratio_bias", "mae"),),
        days="2024 days with complete weather covariates (as the covariate slice)",
    ),
    Probe(
        id="P3",
        question="Does forecasting the 12 regional solar series jointly beat forecasting the national one?",
        t0_arm="t0_regjoint_night_zero",
        comparator="ewma",
        metric="mae",
        success="MAE skill > 0 with Holm p < 0.05 (not runnable below 200 days of regional data)",
        secondary=(
            ("t0_regjoint_night_zero", "t0_night_zero", "mae"),
            ("t0_regjoint_night_zero", "t0_regindep_night_zero", "mae"),
        ),
        days="all buildable 2024 days whose 12 regional contexts are >= 98% valid",
    ),
    Probe(
        id="P4",
        question="On national electricity consumption, does t0 beat the best simple method?",
        t0_arm="t0_cal",
        comparator="best_simple_2023",
        metric="mae",
        success="MAE skill > 0 with Holm p < 0.05",
        secondary=(("t0", "best_simple_2023", "mae"), ("t0_cal", "t0", "mae"), ("t0_cal", "rte_j1", "mae")),
        days="all buildable 2024 days",
    ),
)


# ------------------------------------------------------------- utilities


def local_day_targets(day: date) -> pd.DatetimeIndex:
    """The UTC half-hours of one Europe/Paris calendar day (46, 48 or 50 of them)."""
    start = pd.Timestamp(day.isoformat(), tz=PARIS).tz_convert("UTC")
    end = pd.Timestamp((day + timedelta(days=1)).isoformat(), tz=PARIS).tz_convert("UTC")
    return pd.date_range(start, end, freq=STEP, inclusive="left")


def gate(day: date, gate_hour: int = 12) -> pd.Timestamp:
    """The origin for delivery day ``day``: ``gate_hour`` local time on the day before."""
    prev = day - timedelta(days=1)
    return pd.Timestamp(year=prev.year, month=prev.month, day=prev.day, hour=gate_hour, tz=PARIS).tz_convert("UTC")


def past_windows(days: Sequence[date], gate_hour: int = 12) -> list[Window]:
    """Day-ahead windows built from the calendar alone - never from the data."""
    return [Window(delivery_date=d, origin=gate(d, gate_hour), targets=local_day_targets(d)) for d in days]


def _gate_hour(windows: Sequence[Window]) -> int:
    return int(windows[0].origin.tz_convert(PARIS).hour)


def pinball(y: np.ndarray, q: np.ndarray, levels: Sequence[float]) -> np.ndarray:
    """Mean pinball loss over ``levels`` per row; ``q`` is ``[n, len(levels)]``."""
    y = np.asarray(y, dtype="float64")[:, None]
    tau = np.asarray(levels, dtype="float64")[None, :]
    diff = y - np.asarray(q, dtype="float64")
    return np.mean(np.maximum(tau * diff, (tau - 1.0) * diff), axis=1)


def easter(year: int) -> date:
    """Gregorian Easter Sunday (anonymous Gregorian algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month, day = divmod(h + ell - 7 * m + 114, 31)
    return date(year, month, day + 1)


def french_holidays(year: int) -> set[date]:
    """The eleven French public holidays of ``year``."""
    fixed = {date(year, mo, dy) for mo, dy in ((1, 1), (5, 1), (5, 8), (7, 14), (8, 15), (11, 1), (11, 11), (12, 25))}
    e = easter(year)
    return fixed | {e + timedelta(days=1), e + timedelta(days=39), e + timedelta(days=50)}


@dataclass
class HolidayCovariate:
    """1.0 on French public holidays (local calendar), else 0.0 - from timestamps alone."""

    name: str = "holiday"
    oracle: bool = False

    def spec(self) -> dict:
        return {"class": "HolidayCovariate", "calendar": "France public holidays (fixed + Easter-based)"}

    def values(self, times: pd.DatetimeIndex) -> np.ndarray:
        local = pd.DatetimeIndex(times).tz_convert(PARIS)
        days = sorted(d for y in set(local.year) for d in french_holidays(int(y)))
        return pd.Index(local.date).isin(days).astype("float64")

    def issued_at(self, times: pd.DatetimeIndex) -> pd.DatetimeIndex:
        return pd.DatetimeIndex([pd.NaT] * len(times), tz="UTC")


def weekday_mean_4w() -> SameSlotAggregate:
    """Same slot, same weekday: the mean of the last 4 legal weeks."""
    return SameSlotAggregate(k=4, aggregate="mean", period_days=7, lookback_days=35,
                             name="weekday_mean_4w", label="Same time and weekday, mean of 4 legal weeks")


# ------------------------------------------------ base-model error history


def _issued(pred: Prediction) -> pd.Timestamp:
    return pred.covariate_issued_latest if pred.covariate_issued_latest is not None else pd.NaT


def _max_time(*stamps) -> pd.Timestamp:
    valid = [s for s in stamps if s is not None and pd.notna(s)]
    return max(valid) if valid else pd.NaT


@dataclass
class _History:
    """A base model's day-ahead forecasts for past days, as a series over their targets."""

    forecast: pd.Series  # clipped at 0, like every scored forecast
    issued_by_day: dict[date, pd.Timestamp]


def base_history(base, series: pd.Series, days: Sequence[date], gate_hour: int) -> _History:
    windows = past_windows(sorted(set(days)), gate_hour)
    preds = base.predict(series, windows)
    parts, issued = [], {}
    for w, p in zip(windows, preds):
        parts.append(pd.Series(np.clip(np.asarray(p.values, dtype="float64"), 0.0, None), index=w.targets))
        issued[w.delivery_date] = _issued(p)
    forecast = pd.concat(parts) if parts else pd.Series(dtype="float64")
    return _History(forecast=forecast[~forecast.index.duplicated()].sort_index(), issued_by_day=issued)


def _history_issued(hist: _History, day: date, lookback: int) -> pd.Timestamp:
    return _max_time(*(hist.issued_by_day.get(day - timedelta(days=k)) for k in range(1, lookback + 1)))


def _slot_errors(series: pd.Series, hist: _History, window: Window, lookback: int):
    """Per target: candidate past same-slot errors (most recent first) and their legality."""
    targets = _utc64(window.targets)
    origin = _utc64(pd.DatetimeIndex([window.origin]))[0]
    lags = np.arange(1, lookback + 1)
    cands = targets[:, None] - lags[None, :] * np.timedelta64(1, "D")
    flat = _from_utc64(cands.ravel())
    y = series.reindex(flat).to_numpy(dtype="float64")
    f = hist.forecast.reindex(flat).to_numpy(dtype="float64")
    err = (y - f).reshape(cands.shape)
    legal = (cands <= origin) & np.isfinite(err)
    return cands, err, legal


@dataclass
class EmpiricalQuantiles:
    """``base`` plus the empirical quantiles of its own past day-ahead errors.

    For each target, the errors of the base's day-ahead forecasts at the same
    UTC slot on the last ``window`` legal days (observed by the origin) give the
    band: ``q_tau = max(base, 0) + quantile_tau(errors)``.  Fewer than
    ``min_n`` legal errors gives NaN.  The point forecast is the base's own.
    """

    base: object
    name: str
    label: str = ""
    levels: tuple[float, ...] = T0_LEVELS
    window: int = EQ_WINDOW_DAYS
    min_n: int = EQ_MIN_N
    lookback: int = EQ_LOOKBACK_DAYS

    def spec(self) -> dict:
        return {"class": "EmpiricalQuantiles", "base": self.base.spec(), "levels": list(self.levels),
                "window": self.window, "min_n": self.min_n, "lookback": self.lookback}

    @property
    def oracle(self) -> bool:
        return bool(getattr(self.base, "oracle", False))

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        now = self.base.predict(series, windows)
        days = {w.delivery_date - timedelta(days=k) for w in windows for k in range(1, self.lookback + 2)}
        hist = base_history(self.base, series, days, _gate_hour(windows))
        out = []
        for w, p in zip(windows, now):
            cands, err, legal = _slot_errors(series, hist, w, self.lookback)
            point = np.clip(np.asarray(p.values, dtype="float64"), 0.0, None)
            n = len(w.targets)
            q = np.full((n, len(self.levels)), np.nan)
            n_src = np.zeros(n, dtype=int)
            latest = np.full(n, np.datetime64("NaT", "ns"))
            for i in range(n):
                picks = np.flatnonzero(legal[i])[: self.window]
                n_src[i] = len(picks)
                if len(picks) >= self.min_n and np.isfinite(point[i]):
                    q[i] = point[i] + np.quantile(err[i, picks], self.levels)
                    latest[i] = cands[i, picks[0]]
            src = _from_utc64(np.fmax(latest, _utc64(p.source_latest)) if p.source_latest is not None else latest)
            out.append(Prediction(
                values=np.asarray(p.values, dtype="float64"), max_source_time=_max_time(p.max_source_time, _index_max(src)),
                source_latest=src, source_earliest=p.source_earliest, n_sources=n_src,
                covariate_issued_latest=_max_time(_issued(p), _history_issued(hist, w.delivery_date, self.lookback)),
                quantiles=q, quantile_levels=tuple(self.levels),
            ))
        return out


@dataclass
class BiasCorrected:
    """``base`` plus an EWMA of its own last ``k`` legal same-slot day-ahead errors."""

    base: object
    name: str
    label: str = ""
    alpha: float = EWMA_ALPHA
    k: int = EWMA_SOURCES
    lookback: int = 30

    def spec(self) -> dict:
        return {"class": "BiasCorrected", "base": self.base.spec(), "alpha": self.alpha, "k": self.k,
                "lookback": self.lookback}

    @property
    def oracle(self) -> bool:
        return bool(getattr(self.base, "oracle", False))

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        now = self.base.predict(series, windows)
        days = {w.delivery_date - timedelta(days=k) for w in windows for k in range(1, self.lookback + 2)}
        hist = base_history(self.base, series, days, _gate_hour(windows))
        weights = (1.0 - self.alpha) ** np.arange(self.k, dtype="float64")
        out = []
        for w, p in zip(windows, now):
            cands, err, legal = _slot_errors(series, hist, w, self.lookback)
            point = np.clip(np.asarray(p.values, dtype="float64"), 0.0, None)
            n = len(w.targets)
            values = np.full(n, np.nan)
            latest = np.full(n, np.datetime64("NaT", "ns"))
            for i in range(n):
                picks = np.flatnonzero(legal[i])[: self.k]
                if len(picks) == self.k:
                    values[i] = point[i] + np.dot(weights, err[i, picks]) / weights.sum()
                    latest[i] = cands[i, picks[0]]
            src = _from_utc64(np.fmax(latest, _utc64(p.source_latest)) if p.source_latest is not None else latest)
            out.append(Prediction(
                values=values, max_source_time=_max_time(p.max_source_time, _index_max(src)),
                source_latest=src, source_earliest=p.source_earliest, n_sources=np.full(n, self.k),
                covariate_issued_latest=_max_time(_issued(p), _history_issued(hist, w.delivery_date, self.lookback)),
            ))
        return out


@dataclass
class ResidualT0:
    """``base`` plus t0's forecast of the base's residuals.

    The residual series ``r = y - max(base day-ahead forecast, 0)`` is built
    from the base's forecasts for past days (each issued at its own gate).  t0
    reads ``r`` only up to the origin, like any target history, and its median
    and quantiles are added to the base's forecast for the delivery day.
    """

    base: object
    t0: T0Forecaster
    name: str
    label: str = ""

    def spec(self) -> dict:
        return {"class": "ResidualT0", "base": self.base.spec(), "t0": self.t0.spec()}

    @property
    def oracle(self) -> bool:
        return bool(getattr(self.base, "oracle", False) or self.t0.oracle)

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        now = self.base.predict(series, windows)
        ctx_days = self.t0.context_steps // 48 + 2
        days = {w.delivery_date - timedelta(days=k) for w in windows for k in range(1, ctx_days + 1)}
        hist = base_history(self.base, series, days, _gate_hour(windows))
        start = min(w.origin for w in windows) - (self.t0.context_steps - 1) * STEP
        grid = pd.date_range(start, max(w.origin for w in windows), freq=STEP)
        residual = (series.reindex(grid) - hist.forecast.reindex(grid)).rename("residual")
        inner = self.t0.predict(residual, windows)
        out = []
        for w, p, r in zip(windows, now, inner):
            point = np.clip(np.asarray(p.values, dtype="float64"), 0.0, None)
            quantiles = None if r.quantiles is None else point[:, None] + r.quantiles
            out.append(Prediction(
                values=point + r.values, max_source_time=_max_time(p.max_source_time, w.origin),
                source_latest=pd.DatetimeIndex([w.origin] * len(w.targets)),
                source_earliest=r.source_earliest, n_sources=r.n_sources,
                covariate_issued_latest=_max_time(_issued(p), _issued(r),
                                                  _history_issued(hist, w.delivery_date, ctx_days)),
                quantiles=quantiles, quantile_levels=r.quantile_levels,
            ))
        return out


# ------------------------------------------------------ regional joint t0


@dataclass
class T0JointForecaster:
    """t0 on the regional series (``[B, V, T]``), summed into a national forecast.

    ``joint=True`` forecasts the regions of one origin together (t0's rows
    attend to one another); ``joint=False`` forecasts each region on its own.
    The regional frame is cut at each origin, like any target history; the
    national series passed to ``predict`` is not read.
    """

    regional: pd.DataFrame
    context_steps: int
    joint: bool
    name: str
    label: str = ""
    repo_id: str = "theforecastingcompany/t0-alpha"
    revision: str | None = None
    batch_size: int = JOINT_BATCH
    quantiles: tuple[float, ...] = (0.1, 0.5, 0.9)
    _t0: T0Forecaster | None = field(default=None, repr=False)

    def spec(self) -> dict:
        payload = pd.util.hash_pandas_object(self.regional.fillna(-1.0), index=True).to_numpy().tobytes()
        return {"class": "T0JointForecaster", "joint": self.joint, "context_steps": self.context_steps,
                "regions": list(self.regional.columns), "repo_id": self.repo_id, "revision": self.revision,
                "batch_size": self.batch_size, "data_sha256": hashlib.sha256(payload).hexdigest()[:16]}

    def load(self):
        if self._t0 is None:
            self._t0 = T0Forecaster(context_steps=self.context_steps, repo_id=self.repo_id, revision=self.revision)
        return self._t0.load()

    def _context(self, origin: pd.Timestamp) -> np.ndarray:
        ctx = self.regional.loc[:origin]
        if len(ctx) < self.context_steps or ctx.index[-1] != origin:
            raise ValueError(f"{self.name}: regional history does not reach {origin} with {self.context_steps} steps")
        return ctx.iloc[-self.context_steps :].to_numpy(dtype="float32").T  # [V, T]

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        import torch

        model = self.load()
        v = self.regional.shape[1]
        out: list[Prediction] = []
        for start in range(0, len(windows), self.batch_size):
            batch = list(windows[start : start + self.batch_size])
            ctx = np.stack([self._context(w.origin) for w in batch])  # [B, V, T]
            horizon = max(w.horizon for w in batch)

            def run(c):
                watcher = _NonFiniteWatcher()
                t0_log = logging.getLogger("t0.model.model")
                t0_log.addHandler(watcher)
                try:
                    if self.joint:
                        fc = model.predict(torch.from_numpy(c), horizon=horizon, quantiles=list(self.quantiles))
                        med = fc.median.detach().cpu().numpy()  # [b, V, H]
                    else:
                        b = c.shape[0]
                        fc = model.predict(torch.from_numpy(c.reshape(b * v, -1)), horizon=horizon,
                                           quantiles=list(self.quantiles))
                        med = fc.median.detach().cpu().numpy().reshape(b, v, -1)
                finally:
                    t0_log.removeHandler(watcher)
                return med.astype("float64").sum(axis=1), watcher.count  # [b, H]

            log.info("%s batch %d-%d of %d (V=%d, horizon %d)", self.name, start + 1, start + len(batch),
                     len(windows), v, horizon)
            total, flagged = run(ctx)
            if flagged:
                for row in range(len(batch)):
                    _, bad = run(ctx[row : row + 1])
                    if bad:
                        total[row] = np.nan
            for row, w in enumerate(batch):
                n = len(w.targets)
                out.append(Prediction(
                    values=total[row, w.steps - 1], max_source_time=w.origin,
                    source_latest=pd.DatetimeIndex([w.origin] * n),
                    source_earliest=pd.DatetimeIndex([w.origin - (self.context_steps - 1) * STEP] * n),
                    n_sources=np.full(n, self.context_steps * v, dtype=int),
                ))
        return out


def regional_coverage(regional: pd.DataFrame, origin: pd.Timestamp, context_steps: int) -> float:
    """Worst region's share of valid cells in the context ending at ``origin``."""
    ctx = regional.loc[:origin].iloc[-context_steps:]
    if len(ctx) < context_steps:
        return 0.0
    return float(ctx.notna().mean().min())


# ------------------------------------------------------ reference forecast


@dataclass
class ReferenceForecast:
    """A published forecast (RTE's own day-ahead consumption forecast).

    It reads nothing from the target series.  Its issue time is not verified,
    so it is reported as a reference only and never decides a probe.
    """

    forecast: pd.Series
    name: str
    label: str = ""

    def spec(self) -> dict:
        return {"class": "ReferenceForecast", "name": self.name}

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        out = []
        for w in windows:
            n = len(w.targets)
            out.append(Prediction(
                values=self.forecast.reindex(w.targets).to_numpy(dtype="float64"), max_source_time=pd.NaT,
                source_latest=pd.DatetimeIndex([pd.NaT] * n, tz="UTC"),
                source_earliest=pd.DatetimeIndex([pd.NaT] * n, tz="UTC"), n_sources=np.zeros(n, dtype=int),
            ))
        return out
