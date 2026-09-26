"""The engine's data zones, in Europe/Paris local days.

* **discovery** - 2022-01-01 .. 2025-12-31: the researcher may explore it freely;
  results are exploratory and never count as confirmed.
* **consumed** - 2025 was spent on claim C1's one-shot confirmation (run #20). It
  may be explored, but it can never confirm anything again.
* **forward** - from 2026-01-01: sealed. Only the vault opens it, and only for a
  frozen claim batch whose window starts after the freeze.

The C1 audit found that a UTC-midnight seal leaks the first local hour of the
next day, so every boundary here is a Paris-local midnight, and the UTC request
bounds derived from it are rounded *inward* (a day may be lost, never read early).
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

PARIS = "Europe/Paris"
DISCOVERY_START = date(2022, 1, 1)
DISCOVERY_END = date(2025, 12, 31)  # inclusive, Paris local
FORWARD_FROM = DISCOVERY_END + timedelta(days=1)
#: Years whose data was used for a confirmation: explorable, never confirmable again.
CONSUMED: dict[int, str] = {2025: "claim C1, one-shot confirmation, Actions run #20 (36145552543)"}


class ZoneError(RuntimeError):
    """A request would read data outside the zone it is allowed to read."""


def _day(d) -> date:
    return pd.Timestamp(d).date()


def zone_of(d) -> str:
    day = _day(d)
    if day < DISCOVERY_START:
        return "before"
    if day <= DISCOVERY_END:
        return "discovery"
    return "forward"


def assert_readable(start, end) -> None:
    """A data read may reach back before the discovery zone (a 90-day context for
    early 2022 needs late 2021) but must never reach the forward zone."""
    s, e = _day(start), _day(end)
    if e < s:
        raise ZoneError(f"empty range {s} .. {e}")
    if zone_of(e) == "forward":
        raise ZoneError(f"{e} is in the forward zone (from {FORWARD_FROM}): only the vault reads it")


def assert_discovery(start, end) -> None:
    """Both inclusive local days - days to be *scored* - must lie in the discovery zone."""
    s, e = _day(start), _day(end)
    if e < s:
        raise ZoneError(f"empty range {s} .. {e}")
    for day in (s, e):
        if zone_of(day) != "discovery":
            raise ZoneError(f"{day} is in the {zone_of(day)} zone; discovery is {DISCOVERY_START} .. {DISCOVERY_END}")


def local_midnight_utc(d) -> pd.Timestamp:
    """The UTC instant at which the Paris-local day ``d`` starts."""
    return pd.Timestamp(_day(d)).tz_localize(PARIS).tz_convert("UTC")


def utc_request_days(start, end) -> tuple[str, str]:
    """Day-granular UTC bounds ``[a, b)`` for an API that filters on UTC dates.

    ``a`` is the UTC date of the local start (it may include the last UTC hour
    of the previous local day - harmless, as that day is earlier). ``b`` is the
    UTC date *on or before* the local midnight that ends ``end``, so no row
    after the local end is ever requested; at worst the last local day is cut short.
    """
    a = local_midnight_utc(start).date()
    b = local_midnight_utc(_day(end) + timedelta(days=1)).date()  # floor: the UTC date of that instant
    return a.isoformat(), b.isoformat()


def confirmable(d) -> bool:
    """Only forward days, never a consumed year, can confirm a claim."""
    day = _day(d)
    return zone_of(day) == "forward" and day.year not in CONSUMED
