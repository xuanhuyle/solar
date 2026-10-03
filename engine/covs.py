"""Covariate providers for the catalogue, each built from a ``DataBundle`` alone.

Building every provider from the bundle (never from a global cache) is what
lets the referee poison a bundle after an origin and rebuild the arm: data held
inside a covariate is then poisoned too.

Constants marked *frozen* come from ``python -m engine avail`` (coverage only,
never skill) and are fixed before any probe uses the covariate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from solarbench import covariates as cov
from solarbench.probes import HolidayCovariate, french_holidays

PARIS = "Europe/Paris"

#: Frozen from the engine's avail run (Actions run 36241652637, coverage only, no skill):
#: - ECMWF IFS 0.25, the covariate slice's model: previous_day3 valid from 2024-02-06, complete through 2025.
#:   ARPEGE, ICON and GFS returned identical 2024 coverage to four decimals (not independent archives),
#:   and GFS's apparent 2022-2023 history could not be verified, so they are not used.
#: - Lead 3 days, as for radiation: the value was issued well before any 12:00 D-1 gate.
#: - Weights: each mainland region's share of 2023 consumption (ODRÉ regional, definitive).
TEMPERATURE_MODEL: str | None = "ecmwf_ifs025"
TEMPERATURE_LEAD_DAYS = 3
TEMPERATURE_FIRST: str | None = "2024-02-06"
CONSUMPTION_WEIGHTS: dict[str, float] | None = {
    "Auvergne-Rhône-Alpes": 0.139444, "Bourgogne-Franche-Comté": 0.044883, "Bretagne": 0.049161,
    "Centre-Val de Loire": 0.039734, "Grand Est": 0.093865, "Hauts-de-France": 0.105995,
    "Île-de-France": 0.14513, "Normandie": 0.058773, "Nouvelle-Aquitaine": 0.093962, "Occitanie": 0.082869,
    "Pays de la Loire": 0.057452, "Provence-Alpes-Côte d'Azur": 0.088731,
}
TEMPERATURE_VARIABLE = "temperature_2m"

#: The covariate slice's frozen radiation construction (solar only).
RADIATION_MODEL = cov.WX_MODEL
RADIATION_LEAD_DAYS = cov.WX_LEAD_DAYS
RADIATION_VARIABLE = cov.WX_VARIABLE


def bridge_days(year: int) -> set[date]:
    """Mondays before a Tuesday holiday and Fridays after a Thursday holiday."""
    out = set()
    for h in french_holidays(year):
        if h.weekday() == 1:
            out.add(h - timedelta(days=1))
        elif h.weekday() == 3:
            out.add(h + timedelta(days=1))
    return out


@dataclass
class BridgeDayCovariate:
    """1.0 on French bridge days ("ponts"), else 0.0 - from timestamps alone."""

    name: str = "bridge_day"
    oracle: bool = False

    def spec(self) -> dict:
        return {"class": "BridgeDayCovariate", "rule": "Monday before a Tuesday holiday, Friday after a Thursday holiday"}

    def values(self, times: pd.DatetimeIndex) -> np.ndarray:
        local = pd.DatetimeIndex(times).tz_convert(PARIS)
        days = sorted(d for y in set(local.year) for d in bridge_days(int(y)))
        return pd.Index(local.date).isin(days).astype("float64")

    def issued_at(self, times: pd.DatetimeIndex) -> pd.DatetimeIndex:
        return pd.DatetimeIndex([pd.NaT] * len(times), tz="UTC")


TRANSFORMS = {
    "raw": lambda x: x,
    "hdd15": lambda x: np.maximum(15.0 - x, 0.0),
    "cdd22": lambda x: np.maximum(x - 22.0, 0.0),
}


#: How an archived hourly value relates to time. Open-Meteo radiation is the mean over the hour
#: *before* its stamp; temperature is an instantaneous reading *at* its stamp. The known-answer gate
#: caught the first draft mapping temperature with the radiation convention (about 45 min late).
CONVENTION = {"temperature": "instant", "radiation": "mean_preceding_hour"}


def instant_to_slots(hourly: pd.Series, times: pd.DatetimeIndex, stamp_offset_min: int) -> tuple[np.ndarray, pd.DatetimeIndex]:
    """Half-hour values from instantaneous hourly readings: linear interpolation at each slot centre
    between the readings at the hour on or before it and the hour after it (no extrapolation, no gap
    filling). Returns the values and, per half-hour, the latest hourly stamp used."""
    centre = pd.DatetimeIndex(times) + pd.Timedelta(minutes=stamp_offset_min)
    before = centre.floor("h")
    after = before + pd.Timedelta(hours=1)
    w = np.asarray((centre - before) / pd.Timedelta(hours=1), dtype="float64")
    v0 = hourly.reindex(before).to_numpy(dtype="float64")
    v1 = hourly.reindex(after).to_numpy(dtype="float64")
    uses_after = w > 1e-12
    values = (1.0 - w) * v0 + w * np.where(uses_after, v1, 0.0)
    values[np.isnan(v0) | (uses_after & np.isnan(v1))] = np.nan
    latest = pd.to_datetime(np.where(uses_after, after.asi8, before.asi8), utc=True)
    return values, latest


def weather_provider(name: str, hourly: pd.Series, grid: pd.DatetimeIndex, lead_days: int, convention: str,
                     *, transform: str = "raw", oracle: bool = False, description: dict | None = None
                     ) -> cov.SeriesCovariate:
    """An archived hourly forecast as a slot-level covariate with per-cell issue bounds.

    The issue bound of each slot is taken from the *latest* hourly stamp it uses, so a slot never
    borrows from a value issued after its bound. ``oracle`` (known-answer arms only) marks values
    that read the future; they run only under the backtest's two-key exemption.
    """
    offset = cov.STAMP_OFFSET_MIN or 0
    if convention == "mean_preceding_hour":
        values, latest = cov.hourly_to_slots(hourly, grid, offset)
    elif convention == "instant":
        values, latest = instant_to_slots(hourly, grid, offset)
    else:
        raise ValueError(f"unknown convention {convention!r}")
    issued = latest + pd.Timedelta(days=5) if oracle else cov.issue_bound(latest, lead_days)
    label = name if transform == "raw" else f"{name}_{transform}"
    return cov.SeriesCovariate(
        name=label, series=pd.Series(TRANSFORMS[transform](values), index=grid),
        issued=pd.Series(issued, index=grid), oracle=oracle,
        description=dict(description or {}, lead_days=lead_days, convention=convention, transform=transform,
                         stamp_offset_min=offset))


def _weather_provider(name: str, hourly: pd.Series, grid: pd.DatetimeIndex, lead_days: int, transform: str,
                      description: dict, convention: str) -> cov.SeriesCovariate:
    return weather_provider(name, hourly, grid, lead_days, convention, transform=transform, description=description)


def build_covariate(cid: str, transform: str, bundle) -> object:
    """One catalogue covariate as a t0 covariate provider (``values``/``issued_at``/``spec``)."""
    if cid == "holiday":
        return HolidayCovariate()
    if cid == "bridge_day":
        return BridgeDayCovariate()
    if cid == "geometry":
        return cov.GeometryCovariate(cov.REGION_WEIGHTS, cov.STAMP_OFFSET_MIN or 0)
    if cid == "wx_temperature":
        return _weather_provider("wx_temperature", bundle.weather["temperature"], bundle.target.index,
                                 TEMPERATURE_LEAD_DAYS, transform,
                                 {"model": TEMPERATURE_MODEL, "variable": f"{TEMPERATURE_VARIABLE}_previous_day{TEMPERATURE_LEAD_DAYS}",
                                  "weights": "2023 regional consumption"}, CONVENTION["temperature"])
    if cid == "wx_radiation":
        return _weather_provider("wx_radiation", bundle.weather["radiation"], bundle.target.index,
                                 RADIATION_LEAD_DAYS, transform,
                                 {"model": RADIATION_MODEL, "variable": f"{RADIATION_VARIABLE}_previous_day{RADIATION_LEAD_DAYS}",
                                  "weights": "2023 regional solar"}, CONVENTION["radiation"])
    raise KeyError(f"no provider for covariate {cid!r}")
