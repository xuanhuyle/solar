"""Solar geometry from timestamps alone, for the night-zero variant of t0.

Nothing here reads data.  ``dark_mask`` answers one question per half-hour:
*is the sun below the horizon everywhere in metropolitan France for the whole
of this half-hour?*  It is the deterministic, data-free physical constraint
that ``t0_night_zero`` applies to the raw t0 forecast.

The solar position is the NOAA "solar calculator" algorithm (Meeus), accurate
to well under 0.01 degrees for this century, implemented in numpy so the
benchmark gains no dependency.  Its output is checked against published
ephemeris in the tests (Paris solstice sunrise/sunset within a minute).

Every parameter below was fixed before any Phase 2 result was produced and is
recorded in ``run_meta.json``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: "The sun has set": upper limb below the refracted horizon, the standard
#: sunrise/sunset convention (0.833 deg = 34' refraction + 16' semi-diameter).
SUNSET_ELEVATION_DEG = -0.833
#: Civil twilight, reported as a sensitivity only (never used for the scored method).
CIVIL_TWILIGHT_ELEVATION_DEG = -6.0

#: Bounding box of metropolitan France including Corsica (lat 41.3-51.1 N,
#: lon -5.2-9.6 E).  Darkness is required at all four corners; the sun's
#: elevation over a box this size is maximal at a corner, so the corners are
#: the whole test (a 5x5 interior grid gives the identical mask - see tests).
FRANCE_CORNERS = ((41.3, -5.2), (41.3, 9.6), (51.1, -5.2), (51.1, 9.6))

#: Instants checked for each half-hour stamped t, in minutes relative to t.
#: Covering [t - 30, t + 30] makes the rule safe whichever interval the RTE
#: stamp denotes (the half-hour starting, centred on, or ending at t).
SLOT_OFFSETS_MIN = (-30, -15, 0, 15, 30)

_D2R = np.pi / 180.0


def solar_elevation(times_utc: pd.DatetimeIndex, lat: float, lon: float) -> np.ndarray:
    """Geometric solar elevation in degrees (no refraction) at one location."""
    t = pd.DatetimeIndex(times_utc)
    if t.tz is None:
        raise ValueError("times must be tz-aware")
    t = t.tz_convert("UTC")
    jd = t.to_julian_date().to_numpy(dtype="float64")
    T = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000.0

    L0 = (280.46646 + T * (36000.76983 + 0.0003032 * T)) % 360.0  # geometric mean longitude
    M = 357.52911 + T * (35999.05029 - 0.0001537 * T)  # mean anomaly
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)  # eccentricity
    C = (
        np.sin(M * _D2R) * (1.914602 - T * (0.004817 + 0.000014 * T))
        + np.sin(2 * M * _D2R) * (0.019993 - 0.000101 * T)
        + np.sin(3 * M * _D2R) * 0.000289
    )  # equation of centre
    true_long = L0 + C
    omega = 125.04 - 1934.136 * T
    apparent_long = true_long - 0.00569 - 0.00478 * np.sin(omega * _D2R)
    eps0 = 23.0 + (26.0 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60.0) / 60.0
    eps = eps0 + 0.00256 * np.cos(omega * _D2R)  # obliquity, corrected
    declination = np.arcsin(np.sin(eps * _D2R) * np.sin(apparent_long * _D2R))

    y = np.tan(eps * _D2R / 2.0) ** 2
    eot = 4.0 / _D2R * (
        y * np.sin(2 * L0 * _D2R)
        - 2 * e * np.sin(M * _D2R)
        + 4 * e * y * np.sin(M * _D2R) * np.cos(2 * L0 * _D2R)
        - 0.5 * y * y * np.sin(4 * L0 * _D2R)
        - 1.25 * e * e * np.sin(2 * M * _D2R)
    )  # equation of time, minutes
    minutes = (t.hour * 60 + t.minute + t.second / 60.0).to_numpy(dtype="float64")
    true_solar = (minutes + eot + 4.0 * lon) % 1440.0
    hour_angle = true_solar / 4.0 - 180.0
    hour_angle = np.where(hour_angle < -180.0, hour_angle + 360.0, hour_angle)

    sin_h = np.sin(lat * _D2R) * np.sin(declination) + np.cos(lat * _D2R) * np.cos(declination) * np.cos(
        hour_angle * _D2R
    )
    return np.arcsin(np.clip(sin_h, -1.0, 1.0)) / _D2R


def max_elevation(
    times_utc: pd.DatetimeIndex,
    *,
    points: tuple[tuple[float, float], ...] = FRANCE_CORNERS,
    offsets_min: tuple[int, ...] = SLOT_OFFSETS_MIN,
) -> np.ndarray:
    """Highest solar elevation over the points and the instants of each half-hour."""
    t = pd.DatetimeIndex(times_utc).tz_convert("UTC")
    best = np.full(len(t), -np.inf)
    for offset in offsets_min:
        shifted = t + pd.Timedelta(minutes=offset)
        for lat, lon in points:
            best = np.maximum(best, solar_elevation(shifted, lat, lon))
    return best


def dark_mask(
    times_utc: pd.DatetimeIndex,
    *,
    threshold_deg: float = SUNSET_ELEVATION_DEG,
    points: tuple[tuple[float, float], ...] = FRANCE_CORNERS,
    offsets_min: tuple[int, ...] = SLOT_OFFSETS_MIN,
) -> np.ndarray:
    """True where the sun is below ``threshold_deg`` at every point for the whole half-hour."""
    return max_elevation(times_utc, points=points, offsets_min=offsets_min) < threshold_deg


def mask_spec(threshold_deg: float = SUNSET_ELEVATION_DEG) -> dict:
    """The mask's parameters, for run_meta.json and the cache key."""
    return {
        "rule": "sun below threshold at every point for every instant of the half-hour",
        "threshold_deg": threshold_deg,
        "points_lat_lon": [list(p) for p in FRANCE_CORNERS],
        "offsets_min": list(SLOT_OFFSETS_MIN),
        "algorithm": "NOAA solar position (Meeus), geometric elevation, numpy",
    }
