"""The engine's only door to data.

Every ODRÉ export and every Open-Meteo response the engine reads comes through
this module, which checks the zone (``engine.zones``) *before* any request and
re-checks the rows it got back. The downloads reuse ``solarbench``'s cached
fetchers; a test (``tests/test_engine_doors.py``) pins that nothing else in the
engine calls them. Forward-zone data needs a ``ForwardAccess`` from the vault.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from engine import zones
from solarbench import odre, weather

log = logging.getLogger(__name__)

NATIONAL = odre.NATIONAL  # eco2mix-national-cons-def
NATIONAL_TR = "eco2mix-national-tr"


@dataclass(frozen=True)
class ForwardAccess:
    """Issued only by ``engine.vault`` for one frozen batch and its window (milestone M5)."""

    batch_id: str
    batch_sha256: str
    first_day: str
    last_day: str

    def covers(self, start, end) -> bool:
        from engine import vault  # the vault decides; this object only carries the claim

        return vault.access_is_valid(self) and pd.Timestamp(start).date() >= pd.Timestamp(self.first_day).date() \
            and pd.Timestamp(end).date() <= pd.Timestamp(self.last_day).date()


def _guard(start, end, access: ForwardAccess | None) -> None:
    if zones.zone_of(end) != "forward":
        zones.assert_readable(start, end)
        return
    if access is None or not isinstance(access, ForwardAccess) or not access.covers(start, end):
        raise zones.ZoneError(f"{start} .. {end} reaches the forward zone: only the vault may read it")


def assert_rows_within(series: pd.Series | pd.DataFrame, end, access: ForwardAccess | None = None) -> None:
    """After a read: no row may be stamped at or after the local midnight ending ``end``."""
    if access is not None:
        return
    limit = zones.local_midnight_utc(pd.Timestamp(end).date() + pd.Timedelta(days=1))
    idx = series.dropna(how="all").index if isinstance(series, pd.DataFrame) else series.dropna().index
    if len(idx) and idx.max() >= limit:
        raise zones.ZoneError(f"a read returned rows up to {idx.max()}, at or after {limit}")


def fetch_odre(dataset: str, columns: list[str], start, end, cache_dir: Path, *,
               access: ForwardAccess | None = None) -> Path:
    """Columns of an ODRÉ export for the inclusive local days ``start .. end``."""
    _guard(start, end, access)
    a, b = zones.utc_request_days(start, end)
    return odre._download_columns(dataset, columns, a, b, Path(cache_dir))


def load_odre(dataset: str, column: str, start, end, cache_dir: Path, *, perimeter: str | None = "france",
              access: ForwardAccess | None = None, extra: tuple[str, ...] = ("nature",)) -> pd.Series:
    """One numeric column on the 30-minute UTC grid, zone-checked before and after."""
    cols = ["date_heure", "perimetre", *extra, column]
    path = fetch_odre(dataset, cols, start, end, cache_dir, access=access)
    series = odre.load_column(path, column, perimeter=perimeter)
    assert_rows_within(series, end, access)
    return series


def fetch_weather_previous_runs(model: str, variables: list[str], start, end, cache_dir: Path, *,
                                points: dict[str, tuple[float, float]], access: ForwardAccess | None = None,
                                ) -> dict[str, pd.DataFrame]:
    """Archived forecasts (``<var>_previous_dayN``) by *valid* day, inclusive, hourly UTC.

    The valid day decides the zone: a forecast valid in the forward zone is
    about the sealed period, whenever it was issued.
    """
    _guard(start, end, access)
    a, b = zones.utc_request_days(start, end)
    last = (pd.Timestamp(b) - pd.Timedelta(days=1)).date().isoformat()  # Open-Meteo end_date is inclusive
    params = {
        **weather._points_params(points), "hourly": ",".join(variables), "models": model,
        "start_date": a, "end_date": last, "timezone": "GMT", "timeformat": "unixtime",
    }
    path = weather.fetch_json(weather.PREVIOUS_RUNS_URL, params, Path(cache_dir))
    out = {v: weather.parse_hourly(path, v, list(points)) for v in variables}
    for frame in out.values():
        assert_rows_within(frame, end, access)
    return out


def consumption_region_weights_2023(cache_dir: Path) -> tuple[dict[str, float], dict]:
    """Each mainland region's share of 2023 electricity consumption (ODRÉ regional, definitive).

    One grouped query, like ``weather.fetch_region_weights_2023`` for solar. It
    weights the regional temperature forecasts into one national temperature.
    """
    import json

    from solarbench.covariates import REGION_POINTS
    from solarbench.data import _where_clauses

    zones.assert_readable("2023-01-01", "2023-12-31")
    last: Exception | None = None
    for where in _where_clauses("2023-01-01", "2024-01-01"):
        params = {"select": "libelle_region, sum(consommation) as conso_sum", "where": where,
                  "group_by": "libelle_region", "limit": 100}
        try:
            body = json.loads(weather.fetch_json(weather.ODRE_REGIONAL_URL, params, Path(cache_dir), retries=3)
                              .read_text(encoding="utf-8"))
        except RuntimeError as exc:
            last = exc
            continue
        totals = {r["libelle_region"]: float(r["conso_sum"] or 0.0) for r in body.get("results", [])}
        by_fold = {weather._fold(k): v for k, v in totals.items()}
        missing = [r for r in REGION_POINTS if weather._fold(r) not in by_fold]
        if missing:
            raise ValueError(f"ODRÉ 2023 consumption totals lack regions {missing}; got {sorted(totals)}")
        raw = {r: by_fold[weather._fold(r)] for r in REGION_POINTS}
        total = sum(raw.values())
        return {r: v / total for r, v in raw.items()}, {"totals": raw, "where": where}
    raise RuntimeError(f"ODRÉ regional consumption query failed: {last}")
