"""Network access for the covariate slice: Open-Meteo weather and ODRÉ regional weights.

Every request is cached as raw JSON under ``wxcache/`` with a manifest entry
(URL, parameters, sha256, fetch time), so a rerun reproduces the exact bytes
without touching the network.  Every function refuses a date on or after
``SEALED_FROM`` *before* any request is made: 2025 onwards is reserved for a
later, independent confirmation and must not be read here.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from solarbench.covariates import REGION_POINTS
from solarbench.data import _where_clauses

log = logging.getLogger(__name__)

SEALED_FROM = date(2025, 1, 1)

PREVIOUS_RUNS_URL = "https://previous-runs-api.open-meteo.com/v1/forecast"
SINGLE_RUNS_URL = "https://single-runs-api.open-meteo.com/v1/forecast"
ERA5_URL = "https://archive-api.open-meteo.com/v1/archive"
ODRE_REGIONAL_DATASET = "eco2mix-regional-cons-def"
ODRE_REGIONAL_URL = (
    f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/{ODRE_REGIONAL_DATASET}/records"
)

#: Weather models in the order they are tried, fixed before the probe.
#: Single models only: "seamless" blends switch models across leads and dates.
WX_MODEL_PREFERENCE = ("ecmwf_ifs025", "meteofrance_arpege_europe", "icon_eu", "gfs_global")


class SealedDataError(RuntimeError):
    """A request would have read data from the sealed period."""


def assert_before_seal(*days: str | date | pd.Timestamp) -> None:
    for d in days:
        day = pd.Timestamp(d).date()
        if day >= SEALED_FROM:
            raise SealedDataError(f"{day} is on or after {SEALED_FROM}: sealed data is never fetched here")


def _cache_path(cache_dir: Path, url: str, params: dict) -> Path:
    key = hashlib.sha256(json.dumps([url, sorted(params.items())], default=str).encode()).hexdigest()[:24]
    return Path(cache_dir) / f"{key}.json"


def fetch_json(url: str, params: dict, cache_dir: Path, *, retries: int = 6, timeout: int = 300) -> Path:
    """GET ``url`` once and cache the body; later calls read the cache.

    Retries with exponential backoff on 429 / 5xx / connection errors (the free
    Open-Meteo tier is rate-limited per IP, and runner IPs are shared).  A 4xx
    other than 429 is final and raises with the server's message.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = _cache_path(cache_dir, url, params)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    delay = 5.0
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
        except requests.RequestException as exc:  # pragma: no cover - network
            last = exc
        else:
            if resp.status_code == 200:
                tmp = dest.with_suffix(".part")
                tmp.write_bytes(resp.content)
                tmp.replace(dest)
                _record(cache_dir, url, params, dest)
                return dest
            last = RuntimeError(f"HTTP {resp.status_code} from {url}: {resp.text[:300]}")
            if resp.status_code != 429 and resp.status_code < 500:
                raise last
            retry_after = resp.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                delay = max(delay, float(retry_after))
        log.warning("attempt %d/%d failed (%s); retrying in %.0f s", attempt + 1, retries, last, delay)
        time.sleep(delay)
        delay = min(delay * 2, 120.0)
    raise RuntimeError(f"giving up on {url}: {last}")


def _record(cache_dir: Path, url: str, params: dict, path: Path) -> None:
    manifest = Path(cache_dir) / "manifest.jsonl"
    entry = {
        "file": path.name,
        "url": url,
        "params": params,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with manifest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _points_params(points: dict[str, tuple[float, float]]) -> dict:
    return {
        "latitude": ",".join(f"{lat:.3f}" for lat, _ in points.values()),
        "longitude": ",".join(f"{lon:.3f}" for _, lon in points.values()),
    }


def parse_hourly(path: Path, variable: str, names: list[str]) -> pd.DataFrame:
    """One Open-Meteo response -> UTC-indexed frame, one column per point.

    A multi-location request returns a JSON list in request order; a single
    location returns one object.  JSON nulls become NaN and are never filled.
    """
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    items = body if isinstance(body, list) else [body]
    if len(items) != len(names):
        raise ValueError(f"{path.name}: {len(items)} locations returned, {len(names)} requested")
    columns = {}
    index = None
    for name, item in zip(names, items):
        hourly = item.get("hourly") or {}
        if variable not in hourly:
            raise KeyError(f"{path.name}: no hourly '{variable}' (have {sorted(hourly)})")
        stamps = pd.to_datetime(np.asarray(hourly["time"], dtype="int64"), unit="s", utc=True)
        values = np.array([np.nan if v is None else float(v) for v in hourly[variable]], dtype="float64")
        if index is None:
            index = stamps
        elif not index.equals(stamps):
            raise ValueError(f"{path.name}: locations disagree on timestamps")
        columns[name] = values
    return pd.DataFrame(columns, index=index)


def fetch_previous_runs(
    model: str, variables: list[str], start: str, end: str, cache_dir: Path,
    points: dict[str, tuple[float, float]] = REGION_POINTS,
) -> dict[str, pd.DataFrame]:
    """Archived forecasts at fixed lead offsets (``<var>_previous_dayN``), hourly, UTC.

    ``start``/``end`` are inclusive dates; ``end`` must be before the seal.
    """
    assert_before_seal(start, end)
    params = {
        **_points_params(points), "hourly": ",".join(variables), "models": model,
        "start_date": start, "end_date": end, "timezone": "GMT", "timeformat": "unixtime",
    }
    path = fetch_json(PREVIOUS_RUNS_URL, params, cache_dir)
    return {v: parse_hourly(path, v, list(points)) for v in variables}


def fetch_era5(
    variable: str, start: str, end: str, cache_dir: Path,
    points: dict[str, tuple[float, float]] = REGION_POINTS,
) -> pd.DataFrame:
    """ERA5 reanalysis, hourly, UTC - the non-point-in-time reference arm."""
    assert_before_seal(start, end)
    params = {
        **_points_params(points), "hourly": variable, "models": "era5",
        "start_date": start, "end_date": end, "timezone": "GMT", "timeformat": "unixtime",
    }
    return parse_hourly(fetch_json(ERA5_URL, params, cache_dir), variable, list(points))


def fetch_single_run(
    model: str, variable: str, run: pd.Timestamp, point: tuple[float, float], cache_dir: Path,
    *, forecast_hours: int = 96,
) -> pd.Series:
    """One model run by its start time - used only to check what ``previous_dayN`` means."""
    run = pd.Timestamp(run)
    assert_before_seal(run, run + pd.Timedelta(hours=forecast_hours))
    params = {
        "latitude": f"{point[0]:.3f}", "longitude": f"{point[1]:.3f}", "hourly": variable,
        "models": model, "run": run.strftime("%Y-%m-%dT%H:%M"), "forecast_hours": forecast_hours,
        "timezone": "GMT", "timeformat": "unixtime",
    }
    frame = parse_hourly(fetch_json(SINGLE_RUNS_URL, params, cache_dir), variable, ["point"])
    return frame["point"]


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold().replace("'", "").replace("’", "").strip()


def fetch_region_weights_2023(cache_dir: Path) -> tuple[dict[str, float], dict]:
    """Each mainland region's share of 2023 solar production, from ODRÉ definitive data.

    One grouped query.  Returns the normalised weights and the raw totals.
    Fails loudly (no fallback) if a region is missing or the query is refused.
    """
    last: Exception | None = None
    for where in _where_clauses("2023-01-01", "2024-01-01"):
        params = {
            "select": "libelle_region, sum(solaire) as solaire_sum",
            "where": where,
            "group_by": "libelle_region",
            "limit": 100,
        }
        try:
            body = json.loads(fetch_json(ODRE_REGIONAL_URL, params, cache_dir, retries=3).read_text(encoding="utf-8"))
        except RuntimeError as exc:
            last = exc
            continue
        totals = {r["libelle_region"]: float(r["solaire_sum"] or 0.0) for r in body.get("results", [])}
        by_fold = {_fold(k): v for k, v in totals.items()}
        missing = [r for r in REGION_POINTS if _fold(r) not in by_fold]
        if missing:
            raise ValueError(f"ODRÉ 2023 totals lack regions {missing}; got {sorted(totals)}")
        raw = {r: by_fold[_fold(r)] for r in REGION_POINTS}
        total = sum(raw.values())
        if not total > 0:
            raise ValueError(f"ODRÉ 2023 solar totals sum to {total}")
        return {r: v / total for r, v in raw.items()}, {"totals": raw, "all_rows": totals, "where": where}
    raise RuntimeError(f"ODRÉ regional query failed: {last}")
