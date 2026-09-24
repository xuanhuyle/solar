"""Forecasters: naive and statistical baselines, the t0-alpha adapter, and derived variants.

Every forecaster sees one delivery-day window at a time and must return one
value per target timestamp, using only observations at or before the window's
origin.  Each prediction reports the latest observation it touched so the
backtest can assert that leakage-free contract instead of trusting it — and,
since Phase 2, the per-target source timestamps and source counts as well, so
the contract can be audited from the saved forecasts rather than from the
forecaster's word alone.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Protocol, Sequence

import numpy as np
import pandas as pd

from solarbench.astro import SUNSET_ELEVATION_DEG, dark_mask, mask_spec
from solarbench.covariates import covariate_times
from solarbench.data import STEP

log = logging.getLogger(__name__)

#: Quantile levels requested from t0; the median is the point forecast because
#: MAE is minimised by the conditional median.
T0_QUANTILES = (0.1, 0.5, 0.9)
T0_REPO_ID = "theforecastingcompany/t0-alpha"

#: Phase 2 parameters, fixed before any Phase 2 result was produced. They are
#: recorded in run_meta.json and must not be tuned against the test year.
EWMA_ALPHA = 0.3
EWMA_SOURCES = 14
SAME_SLOT_LOOKBACK_DAYS = 30
BLEND_WEIGHT = 0.5


@dataclass(frozen=True)
class Window:
    """One day-ahead forecasting problem."""

    delivery_date: date
    origin: pd.Timestamp
    targets: pd.DatetimeIndex

    @property
    def horizon(self) -> int:
        """Steps from the origin to the last target (71 normally, 69/73 at DST)."""
        return int((self.targets[-1] - self.origin) / STEP)

    @property
    def steps(self) -> np.ndarray:
        """1-based step index of each target, counted from the origin."""
        return np.asarray((self.targets - self.origin) / STEP, dtype=int)


@dataclass
class Prediction:
    values: np.ndarray
    max_source_time: pd.Timestamp
    #: Per-target latest / earliest observation used (NaT where none was found).
    source_latest: pd.DatetimeIndex | None = None
    source_earliest: pd.DatetimeIndex | None = None
    #: Per-target number of observations combined into the forecast.
    n_sources: np.ndarray | None = None
    #: Latest time any covariate value the forecast read can have been issued
    #: (``None`` for methods without covariates). ``source_latest`` keeps
    #: meaning the target's own history only.
    covariate_issued_latest: pd.Timestamp | None = None


class Forecaster(Protocol):
    name: str
    label: str

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]: ...

    def spec(self) -> dict: ...


# ------------------------------------------------------------------ helpers


def _utc64(index: pd.DatetimeIndex) -> np.ndarray:
    """A tz-aware index as naive UTC ``datetime64[ns]`` — what numpy arithmetic wants."""
    return index.tz_convert("UTC").tz_localize(None).to_numpy(dtype="datetime64[ns]")


def _from_utc64(values: np.ndarray) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(np.asarray(values, dtype="datetime64[ns]")).tz_localize("UTC")


def _index_max(index: pd.DatetimeIndex) -> pd.Timestamp:
    """Max ignoring NaT; NaT if nothing else is there."""
    return index.max() if index.notna().any() else pd.NaT


# ------------------------------------------------------------ persistence


@dataclass
class SameClockTime:
    """The same UTC clock time, ``period_days`` back — as recently as allowed.

    For each target the source is ``target - k * period_days``, with ``k`` the
    smallest positive integer that lands at or before the origin.  With a 12:00
    D-1 gate and ``period_days=1`` that is yesterday for the first half of the
    delivery day and the day before for the rest: the most recent same-time
    observation an operator actually holds when the gate closes.

    The lag is taken in UTC, not local clock time, so the diurnal alignment
    survives both DST switches.  A missing source stays missing: this is the
    Phase 1 definition, and it is why the delivery days whose single source
    falls in the autumn-DST gap are dropped from the backtest.
    """

    period_days: int
    name: str
    label: str

    def spec(self) -> dict:
        return {"class": "SameClockTime", "period_days": self.period_days}

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        period = pd.Timedelta(days=self.period_days)
        out: list[Prediction] = []
        for w in windows:
            sources = []
            for t in w.targets:
                k = 1
                while t - k * period > w.origin:
                    k += 1
                sources.append(t - k * period)
            src_index = pd.DatetimeIndex(sources)
            values = series.reindex(src_index).to_numpy(dtype="float64")
            out.append(
                Prediction(
                    values=values,
                    max_source_time=src_index.max(),
                    source_latest=src_index,
                    source_earliest=src_index,
                    n_sources=np.ones(len(src_index), dtype=int),
                )
            )
        return out


def same_day_baseline() -> SameClockTime:
    return SameClockTime(
        period_days=1,
        name="prev_day",
        label="Same time, previous day",
    )


def same_week_baseline() -> SameClockTime:
    return SameClockTime(
        period_days=7,
        name="prev_week",
        label="Same time, previous week",
    )


# --------------------------------------------------- same-slot aggregates


@dataclass
class SameSlotAggregate:
    """An aggregate of the ``k`` most recent *legally available* same-slot values.

    For a target ``t`` the candidate sources are ``t - j * 24 h`` for
    ``j = 1, 2, ...``; a candidate is legal when its timestamp is at or before
    the origin **and** the observation is not missing.  The ``k`` most recent
    legal candidates are combined.  Two consequences follow from that definition:

    * after local noon on the delivery day the D-1 value is not yet observable
      at the D-1 noon gate, so the sources are D-2, D-3, ...; the switch is
      decided in UTC exactly as for ``SameClockTime``;
    * a missing observation (the autumn-DST gap) is skipped, so the aggregate
      reaches one day further back instead of going missing — the scored set
      is therefore the same as for the single-lag baselines.

    Fewer than ``k`` legal candidates within ``lookback_days`` gives NaN, never
    a silently shorter aggregate.

    ``aggregate`` is ``"mean"``, ``"median"`` or ``"ewma"``.  The EWMA is a
    truncated, renormalised rank-weighted mean: weight ``(1 - alpha) ** r`` on
    the source of recency rank ``r = 0, 1, ...`` (a skipped missing source
    consumes no rank), over the ``k`` most recent legal sources.
    """

    k: int
    aggregate: str
    name: str
    label: str
    alpha: float | None = None
    lookback_days: int = SAME_SLOT_LOOKBACK_DAYS
    period_days: int = 1

    def __post_init__(self) -> None:
        if self.aggregate not in ("mean", "median", "ewma"):
            raise ValueError(f"unknown aggregate {self.aggregate!r}")
        if self.aggregate == "ewma" and not (self.alpha and 0.0 < self.alpha < 1.0):
            raise ValueError("ewma needs 0 < alpha < 1")
        if self.k < 1 or self.lookback_days < self.k * self.period_days:
            raise ValueError("lookback must cover at least k periods")

    def spec(self) -> dict:
        return {
            "class": "SameSlotAggregate",
            "k": self.k,
            "aggregate": self.aggregate,
            "alpha": self.alpha,
            "lookback_days": self.lookback_days,
            "period_days": self.period_days,
        }

    def _reduce(self, x: np.ndarray) -> float:
        if self.aggregate == "mean":
            return float(np.mean(x))
        if self.aggregate == "median":
            return float(np.median(x))
        weights = (1.0 - self.alpha) ** np.arange(len(x), dtype="float64")
        return float(np.dot(weights, x) / weights.sum())

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        period = np.timedelta64(self.period_days, "D")
        lags = np.arange(1, self.lookback_days // self.period_days + 1)
        out: list[Prediction] = []
        for w in windows:
            targets = _utc64(w.targets)
            origin = _utc64(pd.DatetimeIndex([w.origin]))[0]
            candidates = targets[:, None] - lags[None, :] * period  # (targets, lags)
            observed = series.reindex(_from_utc64(candidates.ravel())).to_numpy(dtype="float64")
            observed = observed.reshape(candidates.shape)
            legal = (candidates <= origin) & np.isfinite(observed)

            n = len(targets)
            values = np.full(n, np.nan)
            n_sources = np.zeros(n, dtype=int)
            latest = np.full(n, np.datetime64("NaT", "ns"))
            earliest = latest.copy()
            for i in range(n):
                picks = np.flatnonzero(legal[i])[: self.k]
                n_sources[i] = len(picks)
                if len(picks) == self.k:
                    values[i] = self._reduce(observed[i, picks])
                    latest[i] = candidates[i, picks[0]]
                    earliest[i] = candidates[i, picks[-1]]
            latest_index = _from_utc64(latest)
            out.append(
                Prediction(
                    values=values,
                    max_source_time=_index_max(latest_index),
                    source_latest=latest_index,
                    source_earliest=_from_utc64(earliest),
                    n_sources=n_sources,
                )
            )
        return out


def mean_3d_baseline() -> SameSlotAggregate:
    return SameSlotAggregate(k=3, aggregate="mean", name="mean_3d", label="Same time, mean of 3 legal days")


def mean_7d_baseline() -> SameSlotAggregate:
    return SameSlotAggregate(k=7, aggregate="mean", name="mean_7d", label="Same time, mean of 7 legal days")


def median_7d_baseline() -> SameSlotAggregate:
    return SameSlotAggregate(
        k=7, aggregate="median", name="median_7d", label="Same time, median of 7 legal days"
    )


def ewma_baseline() -> SameSlotAggregate:
    return SameSlotAggregate(
        k=EWMA_SOURCES, aggregate="ewma", alpha=EWMA_ALPHA, name="ewma",
        label=f"Same time, EWMA (alpha {EWMA_ALPHA}, {EWMA_SOURCES} legal days)",
    )


# -------------------------------------------------------------------- blend


@dataclass
class Blend:
    """A fixed-weight point-by-point blend of other forecasters' raw predictions.

    The blend is formed on the components' *unclipped* values; the backtest then
    clips every method at zero in the same place.  Where a component is
    negative (RTE reports -1/-2 MW at night) the clipped blend can differ from
    the blend of clipped components by up to that amount; ``source_audit``
    counts those rows.  A missing component makes the blend missing.
    """

    components: list[tuple[float, object]]
    name: str
    label: str

    def spec(self) -> dict:
        return {
            "class": "Blend",
            "components": [[weight, c.name, c.spec()] for weight, c in self.components],
        }

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        parts = [c.predict(series, windows) for _, c in self.components]
        out: list[Prediction] = []
        for i in range(len(windows)):
            values = None
            for (weight, _), preds in zip(self.components, parts):
                term = weight * preds[i].values
                values = term if values is None else values + term
            latest = _from_utc64(
                np.fmax.reduce([_utc64(p[i].source_latest) for p in parts])
            )
            earliest = _from_utc64(
                np.fmin.reduce([_utc64(p[i].source_earliest) for p in parts])
            )
            out.append(
                Prediction(
                    values=values,
                    max_source_time=_index_max(pd.DatetimeIndex([p[i].max_source_time for p in parts])),
                    source_latest=latest,
                    source_earliest=earliest,
                    n_sources=sum(p[i].n_sources for p in parts),
                )
            )
        return out


def blend_50_baseline() -> Blend:
    return Blend(
        components=[(BLEND_WEIGHT, same_day_baseline()), (1.0 - BLEND_WEIGHT, mean_7d_baseline())],
        name="blend_50",
        label="Blend: 50% previous day + 50% 7-day mean",
    )


# ------------------------------------------------------------- registries


def same_slot_aggregates() -> list[SameSlotAggregate]:
    """The Phase 2 k-day aggregates: finite wherever the history has k legal days."""
    return [mean_3d_baseline(), mean_7d_baseline(), median_7d_baseline(), ewma_baseline()]


def statistical_baselines() -> list:
    """Every historical-only baseline, in reporting order.

    The benchmark builds its method list from this registry and so do the
    leakage tests, so a baseline cannot exist without being poisoned.
    """
    return [same_day_baseline(), same_week_baseline(), *same_slot_aggregates(), blend_50_baseline()]


# -------------------------------------------------------------- t0-alpha


class _NonFiniteWatcher(logging.Handler):
    """Counts t0's "replaced N non-finite prediction values" warnings."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.count = 0

    def emit(self, record: logging.LogRecord) -> None:
        if "non-finite" in record.getMessage():
            self.count += 1


@dataclass
class T0Forecaster:
    """Zero-shot forecasts from The Forecasting Company's ``t0-alpha``.

    The whole backtest is pushed through ``predict`` in batches: one forward
    pass covers many origins, which is far cheaper than looping day by day.
    Because horizons differ by a step or two at the DST switches, each batch
    asks for the longest horizon it contains and slices each window's own
    target steps out of the result.
    """

    context_steps: int
    repo_id: str = T0_REPO_ID
    revision: str | None = None
    batch_size: int = 64
    quantiles: tuple[float, ...] = T0_QUANTILES
    name: str = "t0"
    label: str = "t0-alpha (zero-shot)"
    #: Covariate slice only: ask for this horizon on every batch, and pass
    #: these known-future covariate providers (``solarbench.covariates``).
    #: Both default to the Experiment 0 behaviour and leave ``spec()`` unchanged.
    fixed_horizon: int | None = None
    covariates: tuple = ()
    _model: object | None = field(default=None, repr=False)

    def spec(self) -> dict:
        out = {
            "class": "T0Forecaster",
            "repo_id": self.repo_id,
            "revision": self.revision,
            "context_steps": self.context_steps,
            "quantiles": list(self.quantiles),
        }
        if self.fixed_horizon is not None:
            out["fixed_horizon"] = self.fixed_horizon
        if self.covariates:
            out["covariates"] = [c.spec() for c in self.covariates]
        return out

    @property
    def oracle(self) -> bool:
        """True if any covariate is a non-point-in-time reference (never a finding)."""
        return any(getattr(c, "oracle", False) for c in self.covariates)

    def load(self):
        if self._model is None:
            from t0 import T0Forecaster as _T0  # imported lazily: torch is heavy

            kwargs = {"token": True}
            if self.revision:
                kwargs["revision"] = self.revision
            log.info("loading %s from Hugging Face (gated repo - needs an accepted licence)", self.repo_id)
            self._model = _T0.from_pretrained(self.repo_id, **kwargs).eval()
        return self._model

    def _context(self, series: pd.Series, origin: pd.Timestamp) -> np.ndarray:
        ctx = series.loc[:origin]
        if len(ctx) < self.context_steps:
            raise ValueError(f"only {len(ctx)} steps of history before {origin}, need {self.context_steps}")
        ctx = ctx.iloc[-self.context_steps :]
        if ctx.index[-1] != origin:
            raise ValueError(f"context must end exactly at the origin {origin}, ends at {ctx.index[-1]}")
        return ctx.to_numpy(dtype="float32")

    def _future(self, series: pd.Series, window: Window, horizon: int) -> tuple[np.ndarray, pd.Timestamp]:
        """The ``[F, T + H]`` covariate block of one window and its latest issue time."""
        times = covariate_times(window.origin, self.context_steps, horizon)
        ctx_index = series.loc[: window.origin].index[-self.context_steps :]
        if not ctx_index.equals(times[: self.context_steps]):
            raise AssertionError(f"{self.name}: covariate window is misaligned with the context at {window.origin}")
        block = np.stack([np.asarray(c.values(times), dtype="float64") for c in self.covariates])
        parts = [pd.DatetimeIndex(c.issued_at(times)) for c in self.covariates]
        issued = parts[0].append(parts[1:]) if len(parts) > 1 else parts[0]
        issued = issued[issued.notna()]
        return block.astype("float32"), (issued.max() if len(issued) else pd.NaT)

    def _predict_covariates(self, model, contexts: np.ndarray, horizon: int, futures: np.ndarray) -> np.ndarray:
        """Median forecasts; rows whose raw output was non-finite come back as NaN.

        t0 silently replaces non-finite outputs with 0.0 (and logs it).  A zero
        would be scored as a real forecast, so the warning is caught, the batch
        is re-run one row at a time, and the offending rows are returned as NaN:
        the backtest then drops those days for every method.
        """
        import torch

        def run(ctx, fut):
            watcher = _NonFiniteWatcher()
            t0_log = logging.getLogger("t0.model.model")
            t0_log.addHandler(watcher)
            try:
                forecast = model.predict(
                    torch.from_numpy(ctx), horizon=horizon, quantiles=list(self.quantiles),
                    future_covariates=torch.from_numpy(fut),
                )
            finally:
                t0_log.removeHandler(watcher)
            return forecast.median.detach().cpu().numpy().astype("float64"), watcher.count

        median, flagged = run(contexts, futures)
        if flagged:
            log.warning("%s: t0 sanitised non-finite output in a batch; re-running row by row", self.name)
            for row in range(len(contexts)):
                values, bad = run(contexts[row : row + 1], futures[row : row + 1])
                if bad:
                    median[row] = np.nan
        return median

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        import torch

        model = self.load()
        results: list[Prediction] = []
        for start in range(0, len(windows), self.batch_size):
            batch = list(windows[start : start + self.batch_size])
            contexts = np.stack([self._context(series, w.origin) for w in batch])
            horizon = max(w.horizon for w in batch)
            if self.fixed_horizon is not None:
                if horizon > self.fixed_horizon:
                    raise ValueError(f"{self.name}: a window needs {horizon} steps, fixed horizon is {self.fixed_horizon}")
                horizon = self.fixed_horizon
            if self.covariates:
                blocks = [self._future(series, w, horizon) for w in batch]
                futures = np.stack([b for b, _ in blocks])
                log.info(
                    "%s batch %d-%d of %d (horizon %d, context %d, covariates %d)",
                    self.name, start + 1, start + len(batch), len(windows), horizon,
                    self.context_steps, futures.shape[1],
                )
                median = self._predict_covariates(model, contexts, horizon, futures)
                for row, w in enumerate(batch):
                    n = len(w.targets)
                    results.append(
                        Prediction(
                            values=median[row, w.steps - 1],
                            max_source_time=w.origin,
                            source_latest=pd.DatetimeIndex([w.origin] * n),
                            source_earliest=pd.DatetimeIndex([w.origin - (self.context_steps - 1) * STEP] * n),
                            n_sources=np.full(n, self.context_steps, dtype=int),
                            covariate_issued_latest=blocks[row][1],
                        )
                    )
                continue
            log.info(
                "t0 batch %d-%d of %d (horizon %d, context %d)",
                start + 1, start + len(batch), len(windows), horizon, self.context_steps,
            )
            forecast = model.predict(
                torch.from_numpy(contexts), horizon=horizon, quantiles=list(self.quantiles)
            )
            median = forecast.median.detach().cpu().numpy()
            for row, w in enumerate(batch):
                n = len(w.targets)
                results.append(
                    Prediction(
                        values=median[row, w.steps - 1].astype("float64"),
                        max_source_time=w.origin,
                        source_latest=pd.DatetimeIndex([w.origin] * n),
                        source_earliest=pd.DatetimeIndex([w.origin - (self.context_steps - 1) * STEP] * n),
                        n_sources=np.full(n, self.context_steps, dtype=int),
                    )
                )
        return results


# ------------------------------------------------- weather ratio baseline


@dataclass
class WeatherSlotRatio:
    """``wx_ratio``: the forecast weather scaled by how that weather turned into output.

    For a target ``t`` the sources are the same UTC slot on earlier days
    (``t - j * 24 h``), legal when at or before the origin with both the
    observation and the covariate present - the same selection rule as
    ``ewma``.  With the ``k`` most recent legal sources,
    ``y_hat(t) = G(t) * sum(y_src) / sum(G_src)``, and zero where the
    sources saw no sunshine.  ``G`` is the point-in-time weather covariate
    for every time involved (the forecast as issued, never an observation), so
    a per-slot ratio absorbs the capacity, panel geometry and model bias the
    covariate does not know about.  The strongest simple non-t0 use of the
    same information t0 receives.
    """

    covariate: object
    k: int = EWMA_SOURCES
    lookback_days: int = SAME_SLOT_LOOKBACK_DAYS
    name: str = "wx_ratio"
    label: str = "Forecast irradiance x same-slot output ratio (no t0)"
    #: Below this summed source irradiance (W/m2) the slot is treated as dark.
    min_sum: float = 1.0

    def spec(self) -> dict:
        return {
            "class": "WeatherSlotRatio", "k": self.k, "lookback_days": self.lookback_days,
            "min_sum": self.min_sum, "covariate": self.covariate.spec(),
        }

    @property
    def oracle(self) -> bool:
        return bool(getattr(self.covariate, "oracle", False))

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        period = np.timedelta64(1, "D")
        lags = np.arange(1, self.lookback_days + 1)
        out: list[Prediction] = []
        for w in windows:
            targets = _utc64(w.targets)
            origin = _utc64(pd.DatetimeIndex([w.origin]))[0]
            candidates = targets[:, None] - lags[None, :] * period
            flat = _from_utc64(candidates.ravel())
            observed = series.reindex(flat).to_numpy(dtype="float64").reshape(candidates.shape)
            g_src = np.asarray(self.covariate.values(flat), dtype="float64").reshape(candidates.shape)
            legal = (candidates <= origin) & np.isfinite(observed) & np.isfinite(g_src)
            g_target = np.asarray(self.covariate.values(w.targets), dtype="float64")

            n = len(targets)
            values = np.full(n, np.nan)
            n_sources = np.zeros(n, dtype=int)
            latest = np.full(n, np.datetime64("NaT", "ns"))
            earliest = latest.copy()
            for i in range(n):
                picks = np.flatnonzero(legal[i])[: self.k]
                n_sources[i] = len(picks)
                if len(picks) < self.k:
                    continue
                latest[i] = candidates[i, picks[0]]
                earliest[i] = candidates[i, picks[-1]]
                denominator = g_src[i, picks].sum()
                values[i] = 0.0 if denominator < self.min_sum else g_target[i] * observed[i, picks].sum() / denominator
            latest_index = _from_utc64(latest)
            issued = pd.DatetimeIndex(self.covariate.issued_at(w.targets)).append(
                pd.DatetimeIndex(self.covariate.issued_at(flat))[legal.ravel()]
            )
            issued = issued[issued.notna()]
            out.append(
                Prediction(
                    values=values,
                    max_source_time=_index_max(latest_index),
                    source_latest=latest_index,
                    source_earliest=_from_utc64(earliest),
                    n_sources=n_sources,
                    covariate_issued_latest=issued.max() if len(issued) else pd.NaT,
                )
            )
        return out


# ------------------------------------------------------- derived methods


@dataclass
class Derived:
    """A method defined as a deterministic transform of another method's forecast.

    The backtest builds it from the source method's own ``Prediction`` objects
    (values copied, source-time fields inherited), so the two are identical by
    construction wherever the transform is the identity, and the transform sits
    inside the leakage contract and the poisoning tests like any forecaster.
    ``transform(window, values)`` receives a private copy and returns the new
    values.
    """

    name: str
    label: str
    source: str
    transform: Callable[[Window, np.ndarray], np.ndarray]
    params: dict = field(default_factory=dict)

    def spec(self) -> dict:
        return {"class": "Derived", "source": self.source, **self.params}

    def derive(self, window: Window, pred: Prediction) -> Prediction:
        values = self.transform(window, np.array(pred.values, dtype="float64", copy=True))
        if len(values) != len(pred.values):
            raise AssertionError(f"{self.name}: transform changed the number of values")
        return Prediction(
            values=values,
            max_source_time=pred.max_source_time,
            source_latest=pred.source_latest,
            source_earliest=pred.source_earliest,
            n_sources=pred.n_sources,
            covariate_issued_latest=pred.covariate_issued_latest,
        )


def night_zero_variant(
    source: str = "t0", threshold_deg: float = SUNSET_ELEVATION_DEG, label: str | None = None
) -> Derived:
    """The source method with its forecast set to zero wherever it is physically dark.

    "Dark" is decided from the target timestamps and a fixed geography alone
    (``solarbench.astro.dark_mask``): the sun below the horizon at every corner
    of metropolitan France for the whole half-hour.  Nothing observed enters
    the rule, so the variant answers exactly one question - what does the
    source achieve after the most trivial known physical constraint - and it
    cannot leak.  The reporting daytime mask, which is derived from actuals,
    is never used here.
    """

    def transform(window: Window, values: np.ndarray) -> np.ndarray:
        values[dark_mask(window.targets, threshold_deg=threshold_deg)] = 0.0
        return values

    return Derived(
        name=f"{source}_night_zero",
        label=label or "t0-alpha, zero when dark everywhere in France",
        source=source,
        transform=transform,
        params={"transform": "night_zero", **mask_spec(threshold_deg)},
    )
