"""Load French national solar generation as a UTC-indexed 30-minute series in MW.

Primary source: RTE eCO2mix, published as open data on Open Data Reseaux Energies
(ODRE), dataset ``eco2mix-national-cons-def``.  The national production columns
are populated on a 30-minute grid even though the file's row grid is 15 minutes.

Everything downstream of this module works in UTC.  That is deliberate: the
diurnal solar cycle follows solar time, not the civil clock, so a fixed 24-hour
UTC lag is "the same solar time yesterday" and the twice-yearly French DST
switch cannot corrupt the lag alignment.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

log = logging.getLogger(__name__)

ODRE_DATASET = "eco2mix-national-cons-def"
ODRE_EXPORT_URL = (
    f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/{ODRE_DATASET}/exports/csv"
)
ODRE_COLUMNS = ["date_heure", "perimetre", "nature", "solaire"]

PARIS = "Europe/Paris"
STEP = pd.Timedelta(minutes=30)
STEPS_PER_DAY = 48

#: Column holding solar generation in the annual eCO2mix bulk files.
BULK_SOLAR_COLUMN = "Solaire"
BULK_DISCLAIMER_PREFIX = "RTE ne pourra"


@dataclass
class DataManifest:
    """Provenance for one normalised series — written next to the cached parquet."""

    source: str
    fetched_at: str
    rows: int
    start: str
    end: str
    missing_steps: int
    missing_ranges: list[tuple[str, str]]
    nature_counts: dict[str, int]
    sha256: str
    #: ``nature`` values counted over the benchmarked window only (Phase 2);
    #: ``nature_counts`` above is over the whole raw file.
    nature_counts_window: dict[str, int] = field(default_factory=dict)

    def to_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- fetch


def _where_clauses(start: str, end: str) -> list[str]:
    """Candidate ODSQL filters, most specific first.

    The exact date-literal syntax accepted by the Explore v2.1 ``where``
    parameter is the one thing about this endpoint we could not verify offline,
    so we try both documented spellings and fall back to an unfiltered export.
    """
    return [
        f"date_heure >= date'{start}' AND date_heure < date'{end}'",
        f"date_heure >= '{start}' AND date_heure < '{end}'",
    ]


def fetch_eco2mix(start: str, end: str, cache_dir: Path, *, timeout: int = 600, force: bool = False) -> Path:
    """Download the ODRE CSV export for ``[start, end)`` and return the cached path.

    ``start``/``end`` are ``YYYY-MM-DD`` strings.  The download is cached; a
    second run with the same window re-uses the file and never hits the network.
    """
    raw_dir = cache_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / f"eco2mix_national_{start}_{end}.csv"
    if dest.exists() and dest.stat().st_size > 0 and not force:
        log.info("using cached download %s (%.1f MB)", dest, dest.stat().st_size / 1e6)
        return dest

    base = {
        "select": ",".join(ODRE_COLUMNS),
        "order_by": "date_heure",
        "delimiter": ";",
        "timezone": "UTC",
    }
    attempts = [dict(base, where=w) for w in _where_clauses(start, end)] + [dict(base)]
    last_error: Exception | None = None
    for i, params in enumerate(attempts):
        kind = "filtered" if "where" in params else "UNFILTERED (whole dataset)"
        log.info("requesting ODRE export, attempt %d/%d - %s", i + 1, len(attempts), kind)
        try:
            with requests.get(ODRE_EXPORT_URL, params=params, stream=True, timeout=timeout) as resp:
                if resp.status_code != 200:
                    last_error = RuntimeError(
                        f"HTTP {resp.status_code} from ODRE: {resp.text[:300]}"
                    )
                    log.warning("attempt failed: %s", last_error)
                    continue
                tmp = dest.with_suffix(".part")
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
                tmp.replace(dest)
            log.info("downloaded %s (%.1f MB)", dest, dest.stat().st_size / 1e6)
            return dest
        except requests.RequestException as exc:  # pragma: no cover - network
            last_error = exc
            log.warning("attempt failed: %s", exc)
    raise RuntimeError(
        f"could not download {ODRE_DATASET} from ODRE. Last error: {last_error}. "
        "Download a file manually and pass it with --csv."
    ) from last_error


# --------------------------------------------------------------------------- parse


def _read_any(path: Path) -> pd.DataFrame:
    """Read either an ODRE CSV export or an annual eCO2mix bulk file.

    The annual files are named ``.xls`` but are tab-separated cp1252 text with a
    trailing empty column and a French disclaimer as the last line.
    """
    head = path.open("rb").read(4096)
    if b"\t" in head.split(b"\n")[0]:
        df = pd.read_csv(
            path,
            sep="\t",
            encoding="cp1252",
            engine="python",
            skipfooter=0,
            na_values=["ND", "-", "DC", ""],
        )
        df = df.loc[~df.iloc[:, 0].astype(str).str.startswith(BULK_DISCLAIMER_PREFIX)]
        df = df.dropna(axis=1, how="all")  # drops the trailing empty column
        rename = {"Date": "date", "Heures": "heure", BULK_SOLAR_COLUMN: "solaire",
                  "Périmètre": "perimetre", "Nature": "nature"}
        df = df.rename(columns=rename)
        df["date_heure"] = df["date"].astype(str) + " " + df["heure"].astype(str)
        return df
    sep = ";" if b";" in head.split(b"\n")[0] else ","
    return pd.read_csv(path, sep=sep, encoding="utf-8", na_values=["ND", "-", "DC"])


def _to_utc_index(raw: pd.Series) -> pd.DatetimeIndex:
    """Parse eCO2mix timestamps to UTC, handling both offset-aware and naive input.

    Naive values are local Paris wall-clock.  In the bulk files the spring-forward
    gap is padded with repeated rows (timestamps that do not exist locally) and
    the autumn repeated hour is dropped, so non-existent times are discarded and
    ambiguous ones resolved to standard time.
    """
    sample = str(raw.dropna().iloc[0])
    aware = bool(re.search(r"(Z|[+-]\d{2}:?\d{2})$", sample))
    if aware:
        return pd.DatetimeIndex(pd.to_datetime(raw, utc=True, format="mixed"))
    naive = pd.to_datetime(raw, format="mixed")
    localised = naive.dt.tz_localize(PARIS, ambiguous=False, nonexistent="NaT")
    return pd.DatetimeIndex(localised.dt.tz_convert("UTC"))


def series_fingerprint(series: pd.Series) -> str:
    """Identify the exact series in use — for cache keys that must not go stale."""
    payload = pd.util.hash_pandas_object(series.fillna(-1.0), index=True).to_numpy().tobytes()
    return hashlib.sha256(payload).hexdigest()[:16]


def describe(series: pd.Series, *, source: str, raw_path: Path) -> DataManifest:
    """Provenance for the series as benchmarked, gaps included."""
    missing = series.index[series.isna()]
    return DataManifest(
        source=source,
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        rows=int(series.notna().sum()),
        start=str(series.index[0]),
        end=str(series.index[-1]),
        missing_steps=int(len(missing)),
        missing_ranges=[(str(t), str(t)) for t in missing[:50]],
        nature_counts={},
        sha256=_sha256(raw_path),
    )


def load_series(path: Path) -> pd.Series:
    """Normalise a raw eCO2mix file into a UTC 30-minute ``Series`` of solar MW.

    Gaps in the source become explicit NaNs on a strict 30-minute UTC grid, and
    are recorded in the manifest rather than silently interpolated.
    """
    df = _read_any(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "solaire" not in df.columns:
        raise ValueError(f"no 'solaire' column in {path}; found {list(df.columns)}")
    if "perimetre" in df.columns:
        df = df.loc[df["perimetre"].astype(str).str.strip().str.casefold() == "france"]

    solar = pd.to_numeric(df["solaire"], errors="coerce")
    keep = solar.notna()
    df, solar = df.loc[keep], solar.loc[keep]
    if df.empty:
        raise ValueError(f"no usable solar rows in {path}")

    idx = _to_utc_index(df["date_heure"])
    series = pd.Series(solar.to_numpy(dtype="float64"), index=idx, name="solar_mw")
    series = series[series.index.notna()]
    series = series[~series.index.duplicated(keep="first")].sort_index()

    grid = pd.date_range(series.index[0], series.index[-1], freq=STEP, tz="UTC")
    off_grid = int((~series.index.isin(grid)).sum())
    if off_grid:
        log.warning("dropping %d timestamps that are not on the 30-minute grid", off_grid)
        series = series[series.index.isin(grid)]
    series = series.reindex(grid)

    if "nature" in df.columns:
        series.attrs["nature_counts"] = {str(k): int(v) for k, v in df["nature"].value_counts().items()}
    return series


def nature_counts_in(path: Path, start: str, end: str) -> dict[str, int]:
    """Count the ``nature`` values of the usable solar rows inside ``[start, end)``.

    The data vintage, made checkable: RTE publishes the same series as real-time,
    consolidated and definitive data, and the export does not filter on it.
    """
    df = _read_any(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "nature" not in df.columns or "solaire" not in df.columns:
        return {}
    if "perimetre" in df.columns:
        df = df.loc[df["perimetre"].astype(str).str.strip().str.casefold() == "france"]
    keep = pd.to_numeric(df["solaire"], errors="coerce").notna()
    df = df.loc[keep]
    idx = _to_utc_index(df["date_heure"])
    inside = (idx >= pd.Timestamp(start, tz="UTC")) & (idx < pd.Timestamp(end, tz="UTC"))
    counts = df.loc[np.asarray(inside, dtype=bool), "nature"].value_counts()
    return {str(k): int(v) for k, v in counts.items()}


def raw_download_path(cache_dir: Path, start: str, end: str) -> Path:
    return cache_dir / "raw" / f"eco2mix_national_{start}_{end}.csv"


def manifest_path(cache_dir: Path, start: str, end: str) -> Path:
    """One manifest per data window, so a cached window cannot inherit another's provenance."""
    return cache_dir / f"manifest_{start}_{end}.json"


def load_or_fetch(
    *, start: str, end: str, cache_dir: Path, csv: Path | None = None, force: bool = False
) -> pd.Series:
    """Return the normalised series for ``[start, end)``, downloading it if necessary."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    parquet = cache_dir / f"solar_fr_30min_{start}_{end}.parquet"
    if csv is None and parquet.exists() and not force:
        log.info("using cached series %s", parquet)
        series = pd.read_parquet(parquet)["solar_mw"]
        mpath = manifest_path(cache_dir, start, end)
        raw = raw_download_path(cache_dir, start, end)
        if not mpath.exists():
            # Provenance regenerated from the cache: the hash is the parquet's,
            # and the nature counts are unknown unless the raw export is still here.
            regenerated = describe(series, source="regenerated from cache", raw_path=parquet)
            if raw.exists():
                regenerated.nature_counts_window = nature_counts_in(raw, start, end)
            regenerated.to_json(mpath)
        else:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
            if not manifest.get("nature_counts_window") and raw.exists() and _sha256(raw) == manifest.get("sha256"):
                # The raw export that produced this parquet is still in the cache:
                # add the window-scoped vintage counts without re-downloading.
                manifest["nature_counts_window"] = nature_counts_in(raw, start, end)
                mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        series.attrs["raw_path"] = str(raw) if raw.exists() else None
        return series

    raw = Path(csv) if csv is not None else fetch_eco2mix(start, end, cache_dir, force=force)
    full = load_series(raw)
    series = full.loc[
        (full.index >= pd.Timestamp(start, tz="UTC")) & (full.index < pd.Timestamp(end, tz="UTC"))
    ]
    if series.empty:
        raise ValueError(
            f"no data in window [{start}, {end}) after normalisation; the file covers "
            f"{full.index[0]} .. {full.index[-1]}"
        )
    manifest = describe(series, source=str(csv) if csv else ODRE_EXPORT_URL, raw_path=raw)
    manifest.nature_counts = full.attrs.get("nature_counts", {})
    manifest.nature_counts_window = nature_counts_in(raw, start, end)
    manifest.to_json(manifest_path(cache_dir, start, end))
    series.to_frame().to_parquet(parquet)
    series.attrs["raw_path"] = str(raw)
    return series
