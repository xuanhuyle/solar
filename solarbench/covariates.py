"""Known-future covariates for t0: solar geometry and archived weather forecasts.

A covariate is handed to t0 as one value per half-hour over the whole model
window: the ``T`` context steps ending at the origin *and* the ``H`` steps after
it.  t0 reads that window bidirectionally, so every value in it can move every
forecast step.  The leakage question is therefore not "is this value in the
past?" but "had this value been *issued* by the gate?"  Each provider answers
it per cell with ``issued_at``:

* solar geometry depends on the timestamp alone (``NaT``: nothing to issue);
* an archived weather forecast of lead ``N`` days was produced by a model run
  that started at most ``24 N`` hours before its valid time and was published
  at most ``WX_P_MAX_H`` hours after that start - a conservative upper bound
  on when the value first existed;
* the ERA5 reanalysis is published days after the fact, so it is never
  point-in-time; it exists only as a flagged ``oracle`` reference arm.

The pure transforms live here; everything that touches the network is in
``solarbench.weather``.  Constants marked *frozen* were set from the probe run
(``run_covariates.py probe``), which reports data coverage and semantics only,
never forecast skill.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from solarbench.astro import solar_elevation
from solarbench.data import STEP

#: One representative point per mainland region: the regional prefecture.
#: An objective rule, fixed before any data was seen. Corsica is outside the
#: eCO2mix national perimeter and is left out.
REGION_POINTS: dict[str, tuple[float, float]] = {
    "Auvergne-Rhône-Alpes": (45.764, 4.836),  # Lyon
    "Bourgogne-Franche-Comté": (47.322, 5.041),  # Dijon
    "Bretagne": (48.117, -1.678),  # Rennes
    "Centre-Val de Loire": (47.903, 1.909),  # Orléans
    "Grand Est": (48.573, 7.752),  # Strasbourg
    "Hauts-de-France": (50.629, 3.057),  # Lille
    "Île-de-France": (48.857, 2.352),  # Paris
    "Normandie": (49.443, 1.099),  # Rouen
    "Nouvelle-Aquitaine": (44.838, -0.579),  # Bordeaux
    "Occitanie": (43.605, 1.444),  # Toulouse
    "Pays de la Loire": (47.218, -1.554),  # Nantes
    "Provence-Alpes-Côte d'Azur": (43.296, 5.370),  # Marseille
}

#: Frozen from the probe: each region's share of 2023 solar production
#: (ODRÉ ``eco2mix-regional-cons-def``, calendar year 2023 - before the test year).
REGION_WEIGHTS: dict[str, float] | None = {
    "Auvergne-Rhône-Alpes": 0.11393156474662404,
    "Bourgogne-Franche-Comté": 0.039416210523438355,
    "Bretagne": 0.023627420999703653,
    "Centre-Val de Loire": 0.049438560646575806,
    "Grand Est": 0.06482233736051664,
    "Hauts-de-France": 0.02585547556850912,
    "Île-de-France": 0.014592530250597483,
    "Normandie": 0.0147012196836811,
    "Nouvelle-Aquitaine": 0.24919989873666493,
    "Occitanie": 0.20508896670304735,
    "Pays de la Loire": 0.05728685190435393,
    "Provence-Alpes-Côte d'Azur": 0.14203896287628762,
}

#: Frozen from the probe: minutes from an eCO2mix stamp to the centre of the
#: half-hour it reports (+15: stamp = start, 0: centre, -15: end).
STAMP_OFFSET_MIN: int | None = 0  # probe: measured -3.95 min, nearest of +15 / 0 / -15

#: Frozen from the probe: the archived weather model and forecast lead in days.
#: Lead 3 because the probe could not verify what ``previous_day2`` means: the
#: Single Runs API had none of the 2024 ECMWF runs it was asked for.
WX_MODEL: str | None = "ecmwf_ifs025"
WX_LEAD_DAYS: int | None = 3
#: Frozen from the probe: sha256 of the processed slot-level covariate series.
WX_SHA256: str | None = "a0f16f323f5b372062fe8c7c1b95c077f774a8ca7106d8e32d443c2b4c3883ca"
ERA5_SHA256: str | None = "48533c4d86ccdbf06801b72b74d6f62171cbeb093078cdf78a039b9a43f79185"

WX_VARIABLE = "shortwave_radiation"
#: Upper bound on the delay between a model run's start and its publication.
WX_P_MAX_H = 10
#: The horizon every covariate arm asks t0 for: the longest real horizon
#: (73 steps on the autumn DST day), so the covariate window never depends on
#: which other days share a batch.
COV_HORIZON = 73
#: A day is scored only if its horizon cells are complete and at least this
#: share of its context cells is valid (the rest go to t0 as missing).
MIN_CONTEXT_VALID = 0.98
#: Instants (minutes around the slot centre) at which geometry is averaged.
GEOMETRY_INSTANTS_MIN = (-10, 0, 10)


def normalised_weights(weights: dict[str, float]) -> dict[str, float]:
    """Weights restricted to ``REGION_POINTS``, positive, summing to one."""
    unknown = sorted(set(weights) - set(REGION_POINTS))
    if unknown:
        raise ValueError(f"weights for unknown regions {unknown}")
    missing = sorted(set(REGION_POINTS) - set(weights))
    if missing:
        raise ValueError(f"no weight for regions {missing}")
    total = float(sum(weights.values()))
    if not total > 0 or any(w < 0 for w in weights.values()):
        raise ValueError("weights must be non-negative with a positive sum")
    return {k: float(weights[k]) / total for k in REGION_POINTS}


def covariate_times(origin: pd.Timestamp, context_steps: int, horizon: int) -> pd.DatetimeIndex:
    """The ``T + H`` stamps of one t0 window: index ``T - 1`` is the origin itself."""
    start = origin - (context_steps - 1) * STEP
    return pd.date_range(start, periods=context_steps + horizon, freq=STEP)


def slot_bounds(times: pd.DatetimeIndex, stamp_offset_min: int) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """The ``[start, end)`` interval each 30-minute stamp reports."""
    centre = pd.DatetimeIndex(times) + pd.Timedelta(minutes=stamp_offset_min)
    return centre - pd.Timedelta(minutes=15), centre + pd.Timedelta(minutes=15)


def hourly_to_slots(
    hourly: pd.Series, times: pd.DatetimeIndex, stamp_offset_min: int
) -> tuple[np.ndarray, pd.DatetimeIndex]:
    """Half-hour values from an hourly series stamped at the *end* of its hour.

    Open-Meteo radiation is the mean over the hour preceding its stamp ``h``,
    i.e. over ``[h - 1 h, h)``.  Each half-hour takes the time-weighted mean of
    only the one or two hourly values that overlap it - no interpolation, no
    gap filling, so a value can never borrow from a later-issued hour it does
    not overlap.  A missing contributing hour makes the half-hour missing.

    Returns the values and, per half-hour, the latest hourly stamp used.
    """
    start, end = slot_bounds(times, stamp_offset_min)
    hour = pd.Timedelta(hours=1)
    first_stamp = start.floor("h") + hour  # the hour [floor, floor+1h) is stamped floor+1h
    second_stamp = first_stamp + hour
    # Overlap of [start, end) with [first_stamp - 1h, first_stamp).
    overlap_first = (np.minimum(end, first_stamp) - start) / pd.Timedelta(minutes=30)
    overlap_first = np.clip(np.asarray(overlap_first, dtype="float64"), 0.0, 1.0)
    overlap_second = 1.0 - overlap_first
    v1 = hourly.reindex(first_stamp).to_numpy(dtype="float64")
    v2 = hourly.reindex(second_stamp).to_numpy(dtype="float64")
    uses_second = overlap_second > 1e-12
    values = overlap_first * v1 + overlap_second * np.where(uses_second, v2, 0.0)
    # A NaN in a contributing hour must propagate even when its weight is small.
    values[np.isnan(v1) | (uses_second & np.isnan(v2))] = np.nan
    latest = pd.to_datetime(np.where(uses_second, second_stamp.asi8, first_stamp.asi8), utc=True)
    return values, latest


def issue_bound(stamps: pd.DatetimeIndex, lead_days: int, p_max_h: int = WX_P_MAX_H) -> pd.DatetimeIndex:
    """Latest time a lead-``N`` value for each hourly stamp can have been published."""
    return pd.DatetimeIndex(stamps) - pd.Timedelta(hours=24 * lead_days) + pd.Timedelta(hours=p_max_h)


def national_mean(frame: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Capacity-weighted mean over the regions; missing if any region is missing."""
    w = normalised_weights(weights)
    cols = list(w)
    missing = sorted(set(cols) - set(frame.columns))
    if missing:
        raise ValueError(f"no column for regions {missing}")
    values = frame[cols].to_numpy(dtype="float64")
    out = values @ np.array([w[c] for c in cols])
    out[np.isnan(values).any(axis=1)] = np.nan
    return pd.Series(out, index=frame.index)


def series_sha256(values: pd.Series, issued: pd.Series | None = None) -> str:
    """Fingerprint of a processed covariate - frozen at the probe, checked at the run."""
    h = hashlib.sha256()
    h.update(np.asarray(values.index.asi8, dtype="int64").tobytes())
    h.update(np.round(values.to_numpy(dtype="float64"), 6).tobytes())
    if issued is not None:
        h.update(np.asarray(pd.DatetimeIndex(issued.to_numpy()).asi8, dtype="int64").tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------ providers


@dataclass
class GeometryCovariate:
    """K1: capacity-weighted mean of ``max(sin(solar elevation), 0)`` over the regions.

    A clear-sky shape computed from timestamps alone: it reads no data, so it
    cannot leak, and ``issued_at`` is ``NaT`` everywhere.
    """

    weights: dict[str, float]
    stamp_offset_min: int
    name: str = "geometry"
    oracle: bool = False
    _memo: pd.Series | None = field(default=None, repr=False, compare=False)

    def spec(self) -> dict:
        return {
            "class": "GeometryCovariate",
            "weights": {k: round(v, 6) for k, v in normalised_weights(self.weights).items()},
            "points": {k: list(v) for k, v in REGION_POINTS.items()},
            "stamp_offset_min": self.stamp_offset_min,
            "instants_min": list(GEOMETRY_INSTANTS_MIN),
        }

    def values(self, times: pd.DatetimeIndex) -> np.ndarray:
        # Consecutive windows overlap almost entirely, so each stamp is computed once.
        times = pd.DatetimeIndex(times)
        missing = times if self._memo is None else times[~times.isin(self._memo.index)]
        if len(missing):
            fresh = pd.Series(self._compute(missing.unique()), index=missing.unique())
            self._memo = fresh if self._memo is None else pd.concat([self._memo, fresh]).sort_index()
        return self._memo.reindex(times).to_numpy(dtype="float64")

    def _compute(self, times: pd.DatetimeIndex) -> np.ndarray:
        w = normalised_weights(self.weights)
        centre = pd.DatetimeIndex(times) + pd.Timedelta(minutes=self.stamp_offset_min)
        total = np.zeros(len(centre))
        for region, (lat, lon) in REGION_POINTS.items():
            acc = np.zeros(len(centre))
            for offset in GEOMETRY_INSTANTS_MIN:
                el = solar_elevation(centre + pd.Timedelta(minutes=offset), lat, lon)
                acc += np.maximum(np.sin(np.deg2rad(el)), 0.0)
            total += w[region] * acc / len(GEOMETRY_INSTANTS_MIN)
        return total

    def issued_at(self, times: pd.DatetimeIndex) -> pd.DatetimeIndex:
        return pd.DatetimeIndex([pd.NaT] * len(times), tz="UTC")


@dataclass
class SeriesCovariate:
    """A covariate held as a slot-level series with a per-cell issue bound.

    ``issued`` is ``None`` for a covariate that depends on timestamps only.
    Cells outside the stored index are missing.
    """

    name: str
    series: pd.Series
    issued: pd.Series | None = None
    oracle: bool = False
    description: dict = field(default_factory=dict)

    def spec(self) -> dict:
        return {
            "class": "SeriesCovariate",
            "name": self.name,
            "oracle": self.oracle,
            "sha256": series_sha256(self.series, self.issued),
            **self.description,
        }

    def values(self, times: pd.DatetimeIndex) -> np.ndarray:
        return self.series.reindex(times).to_numpy(dtype="float64")

    def issued_at(self, times: pd.DatetimeIndex) -> pd.DatetimeIndex:
        if self.issued is None:
            return pd.DatetimeIndex([pd.NaT] * len(times), tz="UTC")
        return pd.DatetimeIndex(self.issued.reindex(times))


def weather_covariate(
    hourly: pd.Series, grid: pd.DatetimeIndex, *, lead_days: int, stamp_offset_min: int,
    name: str = "weather", oracle: bool = False, description: dict | None = None,
) -> SeriesCovariate:
    """Map an hourly national series onto the slot grid, with its issue bounds.

    For the ERA5 reference (``oracle=True``) the issue bound is the valid time
    plus five days - after every origin that uses it, by construction.
    """
    values, latest = hourly_to_slots(hourly, grid, stamp_offset_min)
    if oracle:
        issued = latest + pd.Timedelta(days=5)
    else:
        issued = issue_bound(latest, lead_days)
    return SeriesCovariate(
        name=name,
        series=pd.Series(values, index=grid),
        issued=pd.Series(issued, index=grid),
        oracle=oracle,
        description=dict(description or {}, lead_days=lead_days, stamp_offset_min=stamp_offset_min),
    )


def window_coverage(
    origin: pd.Timestamp, providers, context_steps: int, horizon: int
) -> tuple[float, bool]:
    """Share of valid context cells (worst provider) and whether the horizon is complete."""
    times = covariate_times(origin, context_steps, horizon)
    ctx_share, horizon_ok = 1.0, True
    for p in providers:
        v = np.asarray(p.values(times), dtype="float64")
        ok = np.isfinite(v)
        ctx_share = min(ctx_share, float(ok[:context_steps].mean()))
        horizon_ok = horizon_ok and bool(ok[context_steps:].all())
    return ctx_share, horizon_ok
