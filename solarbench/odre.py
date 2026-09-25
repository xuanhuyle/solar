"""Other ODRÉ eCO2mix series for Experiment 3: national consumption, regional solar.

The Experiment 0 loader (``solarbench.data``) is left untouched; this module
reuses its parsing helpers for two more exports of the same open data:

* ``eco2mix-national-cons-def``: ``consommation`` (MW) and RTE's own
  day-ahead consumption forecast ``prevision_j1`` (a reference only);
* ``eco2mix-regional-cons-def``: ``solaire`` per region (MW).

Both keep only the 30-minute grid, exactly as ``data.load_series`` does, and
both refuse any date on or after the seal before a request is made.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from solarbench.data import STEP, _read_any, _to_utc_index, _where_clauses
from solarbench.weather import assert_before_seal

log = logging.getLogger(__name__)

NATIONAL = "eco2mix-national-cons-def"
REGIONAL = "eco2mix-regional-cons-def"


def _export_url(dataset: str) -> str:
    return f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/{dataset}/exports/csv"


def fetch_columns(
    dataset: str, columns: list[str], start: str, end: str, cache_dir: Path, *, timeout: int = 900
) -> Path:
    """Download ``columns`` of ``dataset`` for ``[start, end)`` as CSV, cached.

    ``end`` is exclusive, so the last day read is the day before it; that day
    must be before the seal.
    """
    assert_before_seal(start, pd.Timestamp(end) - pd.Timedelta(days=1))
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(json.dumps([dataset, columns, start, end]).encode()).hexdigest()[:12]
    dest = cache_dir / f"{dataset}_{start}_{end}_{key}.csv"
    if dest.exists() and dest.stat().st_size > 0:
        log.info("using cached %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)
        return dest
    base = {"select": ",".join(columns), "order_by": "date_heure", "delimiter": ";", "timezone": "UTC"}
    last: Exception | None = None
    for where in _where_clauses(start, end):
        try:
            with requests.get(_export_url(dataset), params=dict(base, where=where), stream=True, timeout=timeout) as resp:
                if resp.status_code != 200:
                    last = RuntimeError(f"HTTP {resp.status_code} from ODRÉ: {resp.text[:300]}")
                    log.warning("%s", last)
                    continue
                tmp = dest.with_suffix(".part")
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
                tmp.replace(dest)
        except requests.RequestException as exc:  # pragma: no cover - network
            last = exc
            continue
        with (cache_dir / "manifest.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"file": dest.name, "dataset": dataset, "columns": columns, "where": where,
                                 "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                                 "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}) + "\n")
        log.info("downloaded %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)
        return dest
    raise RuntimeError(f"could not download {dataset} {columns}: {last}")


def _grid(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    return pd.date_range(index.min(), index.max(), freq=STEP, tz="UTC")


def load_column(path: Path, column: str, *, perimeter: str | None = "france") -> pd.Series:
    """One numeric column on the strict 30-minute UTC grid; gaps stay NaN."""
    df = _read_any(Path(path))
    df.columns = [c.strip().lower() for c in df.columns]
    if column not in df.columns:
        raise KeyError(f"no '{column}' column in {path}; found {list(df.columns)}")
    if perimeter and "perimetre" in df.columns:
        df = df.loc[df["perimetre"].astype(str).str.strip().str.casefold() == perimeter]
    values = pd.to_numeric(df[column], errors="coerce")
    keep = values.notna()
    idx = _to_utc_index(df.loc[keep, "date_heure"])
    series = pd.Series(values[keep].to_numpy(dtype="float64"), index=idx, name=column)
    series = series[series.index.notna()]
    series = series[~series.index.duplicated(keep="first")].sort_index()
    grid = _grid(series.index)
    return series[series.index.isin(grid)].reindex(grid)


def load_regional(path: Path, column: str = "solaire", regions: list[str] | None = None) -> pd.DataFrame:
    """Regions as columns on the strict 30-minute UTC grid; gaps stay NaN."""
    df = _read_any(Path(path))
    df.columns = [c.strip().lower() for c in df.columns]
    values = pd.to_numeric(df[column], errors="coerce")
    keep = values.notna()
    frame = pd.DataFrame({
        "time": _to_utc_index(df.loc[keep, "date_heure"]),
        "region": df.loc[keep, "libelle_region"].astype(str).str.strip().to_numpy(),
        "value": values[keep].to_numpy(dtype="float64"),
    }).dropna(subset=["time"])
    wide = frame.pivot_table(index="time", columns="region", values="value", aggfunc="first")
    wide.index = pd.DatetimeIndex(wide.index)
    grid = _grid(wide.index)
    wide = wide[wide.index.isin(grid)].reindex(grid)
    if regions is not None:
        missing = sorted(set(regions) - set(wide.columns))
        if missing:
            raise ValueError(f"regions missing from {path}: {missing}; have {sorted(wide.columns)}")
        wide = wide[regions]
    return wide.sort_index(axis=1) if regions is None else wide
