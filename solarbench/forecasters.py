"""Forecasters: two naive baselines and the t0-alpha adapter.

Every forecaster sees one delivery-day window at a time and must return one
value per target timestamp, using only observations at or before the window's
origin.  Each prediction reports the latest observation it touched so the
backtest can assert that leakage-free contract instead of trusting it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol, Sequence

import numpy as np
import pandas as pd

from solarbench.data import STEP

log = logging.getLogger(__name__)

#: Quantile levels requested from t0; the median is the point forecast because
#: MAE is minimised by the conditional median.
T0_QUANTILES = (0.1, 0.5, 0.9)
T0_REPO_ID = "theforecastingcompany/t0-alpha"


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


class Forecaster(Protocol):
    name: str
    label: str

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]: ...


@dataclass
class SameClockTime:
    """The same UTC clock time, ``period_days`` back — as recently as allowed.

    For each target the source is ``target - k * period_days``, with ``k`` the
    smallest positive integer that lands at or before the origin.  With a 12:00
    D-1 gate and ``period_days=1`` that is yesterday for the first half of the
    delivery day and the day before for the rest: the most recent same-time
    observation an operator actually holds when the gate closes.

    The lag is taken in UTC, not local clock time, so the diurnal alignment
    survives both DST switches.
    """

    period_days: int
    name: str
    label: str

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
            out.append(Prediction(values=values, max_source_time=src_index.max()))
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
    _model: object | None = field(default=None, repr=False)

    def load(self):
        if self._model is None:
            from t0 import T0Forecaster as _T0  # imported lazily: torch is heavy

            kwargs = {"token": True}
            if self.revision:
                kwargs["revision"] = self.revision
            log.info("loading %s from Hugging Face (gated repo — needs an accepted licence)", self.repo_id)
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

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        import torch

        model = self.load()
        results: list[Prediction] = []
        for start in range(0, len(windows), self.batch_size):
            batch = list(windows[start : start + self.batch_size])
            contexts = np.stack([self._context(series, w.origin) for w in batch])
            horizon = max(w.horizon for w in batch)
            log.info(
                "t0 batch %d-%d of %d (horizon %d, context %d)",
                start + 1, start + len(batch), len(windows), horizon, self.context_steps,
            )
            forecast = model.predict(
                torch.from_numpy(contexts), horizon=horizon, quantiles=list(self.quantiles)
            )
            median = forecast.median.detach().cpu().numpy()
            for row, w in enumerate(batch):
                results.append(
                    Prediction(
                        values=median[row, w.steps - 1].astype("float64"),
                        max_source_time=w.origin,
                    )
                )
        return results
