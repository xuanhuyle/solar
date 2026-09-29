"""Experiment 4's only door to French day-ahead price data.

Two public sources of the same SMARD/Bundesnetzagentur series (CC BY 4.0):

* **Energy-Charts** (Fraunhofer ISE), ``/price?bzn=FR`` - the scored series;
* **SMARD** chart_data, filter 254 ("Marktpreis: Frankreich") - the cross-check.

Every request is checked against the engine's zones *before* it is made
(``engine.zones.assert_readable``: nothing on or after 2026-01-01 Europe/Paris),
its bounds are unix seconds derived from Paris-local day bounds and rounded
inward, and the rows that come back are checked again. A raw response holding
any stamp at or after the forward boundary is deleted from the cache and the
read fails. SMARD serves fixed weekly files, so the week that crosses into 2026
is never requested at all. Raw bytes are cached with a sha256 manifest line.

``to_hourly`` turns the raw series (hourly until the SDAC 15-minute go-live,
quarter-hourly after) into the scored hourly series: from the switch on, an
hour is the mean of its four quarter-hours and is missing unless all four are.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from engine import zones

log = logging.getLogger(__name__)

ENERGY_CHARTS_URL = "https://api.energy-charts.info/price"
SMARD_BASE = "https://www.smard.de/app/chart_data"
SMARD_FILTER = 254
SMARD_REGIONS = ("DE", "DE-LU")  # tried in order; the one that answers is logged
PRICE_CACHE_VERSION = "v1"
#: From this Paris delivery day the auction clears quarter-hours (SDAC 15-minute go-live).
QUARTER_HOUR_FROM = date(2025, 10, 1)
USER_AGENT = "solarbench-exp4 (research; github.com/xuanhuyle/solar)"


class PriceDataError(RuntimeError):
    """A price read failed, or returned something it must not."""


# ------------------------------------------------------------------ bounds


def forward_limit() -> pd.Timestamp:
    """The first UTC instant of the forward zone (2026-01-01 00:00 Europe/Paris)."""
    return zones.local_midnight_utc(zones.FORWARD_FROM)


def unix_bounds(start, end) -> tuple[int, int]:
    """Inclusive unix seconds covering the Paris-local days ``start .. end`` and nothing after."""
    zones.assert_readable(start, end)
    a = zones.local_midnight_utc(start)
    b = zones.local_midnight_utc(pd.Timestamp(end).date() + timedelta(days=1)) - pd.Timedelta(seconds=1)
    return int(a.timestamp()), int(b.timestamp())


def month_chunks(start, end) -> list[tuple[date, date]]:
    """Calendar-month pieces of the inclusive local days ``start .. end``."""
    s, e = pd.Timestamp(start).date(), pd.Timestamp(end).date()
    out = []
    cur = s
    while cur <= e:
        nxt = (pd.Timestamp(cur) + pd.offsets.MonthBegin(1)).date()
        out.append((cur, min(e, nxt - timedelta(days=1))))
        cur = nxt
    return out


# ------------------------------------------------------------------- cache


def _manifest(cache_dir: Path, record: dict) -> None:
    with (cache_dir / "manifest.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _get(session: requests.Session, url: str, params: dict | None, *, timeout: int = 120,
         tries: int = 6) -> requests.Response:
    """GET with backoff on 429/5xx/connection errors (Retry-After honoured, capped at 120 s)."""
    last: Exception | None = None
    for attempt in range(tries):
        try:
            resp = session.get(url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT})
        except requests.RequestException as exc:  # pragma: no cover - network
            last = exc
            time.sleep(min(120, 2 ** (attempt + 1)))
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = resp.headers.get("Retry-After")
            delay = min(120, int(wait)) if wait and wait.isdigit() else min(120, 2 ** (attempt + 1))
            log.warning("HTTP %s from %s; retrying in %s s", resp.status_code, url, delay)
            last = PriceDataError(f"HTTP {resp.status_code} from {url}")
            time.sleep(delay)
            continue
        return resp
    raise PriceDataError(f"giving up on {url}: {last}")


def _cached(cache_dir: Path, name: str) -> Path | None:
    path = cache_dir / name
    return path if path.exists() and path.stat().st_size > 0 else None


def _store(cache_dir: Path, name: str, body: bytes, record: dict) -> Path:
    path = cache_dir / name
    tmp = path.with_suffix(".part")
    tmp.write_bytes(body)
    tmp.replace(path)
    _manifest(cache_dir, {"file": name, "sha256": hashlib.sha256(body).hexdigest(),
                          "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record})
    return path


def _refuse_forward(path: Path, stamps: pd.DatetimeIndex, what: str) -> None:
    """A raw file holding a forward stamp is removed from the cache and the read fails."""
    if len(stamps) and stamps.max() >= forward_limit():
        path.unlink(missing_ok=True)
        raise PriceDataError(f"{what} returned a stamp at {stamps.max()}, in the forward zone: file removed")


# ----------------------------------------------------------- Energy-Charts


def fetch_energy_charts(start, end, cache_dir: Path, *, session: requests.Session | None = None) -> list[Path]:
    """Raw Energy-Charts responses for the inclusive local days ``start .. end``, one file per month.

    Bounds are inclusive unix seconds (``unix_bounds``); every stamp a response
    returns must lie within them, checked before any byte is cached.
    """
    cache_dir = Path(cache_dir) / f"energy-charts-{PRICE_CACHE_VERSION}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    session = session or requests.Session()
    paths = []
    for a, b in month_chunks(start, end):
        lo, hi = unix_bounds(a, b)
        name = f"FR_{a.isoformat()}_{b.isoformat()}.json"
        path = _cached(cache_dir, name)
        if path is None:
            params = {"bzn": "FR", "start": str(lo), "end": str(hi)}
            resp = _get(session, ENERGY_CHARTS_URL, params)
            if resp.status_code == 404:  # no data for that zone and range: kept as an explicit empty answer
                body = json.dumps({"status": 404, "unix_seconds": [], "price": []}).encode()
            elif resp.status_code != 200:
                raise PriceDataError(f"HTTP {resp.status_code} from Energy-Charts for {a}..{b}: {resp.text[:300]}")
            else:
                body = resp.content
            secs = np.asarray(json.loads(body.decode("utf-8")).get("unix_seconds") or [], dtype="int64")
            if len(secs) and (secs.min() < lo or secs.max() > hi):
                raise PriceDataError(f"Energy-Charts returned stamps outside [{lo}, {hi}] for {a}..{b}: not cached")
            path = _store(cache_dir, name, body, {"source": "energy-charts", "url": ENERGY_CHARTS_URL,
                                                  "params": params, "status": resp.status_code})
        stamps, _, _ = _parse_energy_charts(path)
        _refuse_forward(path, stamps, "Energy-Charts")
        paths.append(path)
    return paths


def licence_ok(licence: str | None) -> bool:
    """The spec's licence rule for an Energy-Charts response."""
    return bool(licence) and "CC BY 4.0" in licence and "Bundesnetzagentur | SMARD.de" in licence


def _parse_energy_charts(path: Path) -> tuple[pd.DatetimeIndex, np.ndarray, str | None]:
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    secs = body.get("unix_seconds") or []
    prices = [np.nan if p is None else float(p) for p in (body.get("price") or [])]
    if len(secs) != len(prices):
        raise PriceDataError(f"{path.name}: {len(secs)} stamps but {len(prices)} prices")
    stamps = pd.to_datetime(np.asarray(secs, dtype="int64"), unit="s", utc=True)
    return pd.DatetimeIndex(stamps), np.asarray(prices, dtype="float64"), body.get("license_info")


def load_energy_charts(paths: list[Path]) -> tuple[pd.Series, set[str]]:
    """The raw series (as stamped by the source) and the licence strings seen."""
    parts, licences = [], set()
    for path in paths:
        stamps, values, licence = _parse_energy_charts(path)
        if licence:
            licences.add(licence)
        parts.append(pd.Series(values, index=stamps))
    return _merge(parts, "Energy-Charts"), licences


def _merge(parts: list[pd.Series], what: str) -> pd.Series:
    if not parts:
        return pd.Series(dtype="float64")
    raw = pd.concat(parts).sort_index()
    dup = raw.index.duplicated(keep=False)
    if dup.any():
        clash = raw[dup].groupby(level=0).nunique(dropna=False)
        if (clash > 1).any():
            raise PriceDataError(f"{what}: conflicting values for {int((clash > 1).sum())} repeated stamps")
        raw = raw[~raw.index.duplicated(keep="first")]
    raw.name = "price"
    return raw


# ------------------------------------------------------------------- SMARD


def smard_url(region: str, resolution: str, timestamp_ms: int | None = None) -> str:
    if timestamp_ms is None:
        return f"{SMARD_BASE}/{SMARD_FILTER}/{region}/index_{resolution}.json"
    return f"{SMARD_BASE}/{SMARD_FILTER}/{region}/{SMARD_FILTER}_{region}_{resolution}_{timestamp_ms}.json"


def smard_file_days(t_ms: int) -> tuple[date, date]:
    """The Paris days a weekly SMARD file covers: Monday .. Sunday from its start stamp."""
    first = pd.Timestamp(t_ms, unit="ms", tz="UTC").tz_convert(zones.PARIS).date()
    return first, first + timedelta(days=6)


def smard_chunks_to_fetch(index_ms: list[int], start, end) -> list[int]:
    """Weekly SMARD files that overlap ``start .. end`` and whose last day is before the forward zone.

    A file reaching the forward zone (the one starting 2025-12-29) is never
    requested, even if part of it is in range.
    """
    s, e = pd.Timestamp(start).date(), pd.Timestamp(end).date()
    out = []
    for t in sorted(int(x) for x in index_ms):
        first, last = smard_file_days(t)
        if last < s or first > e:
            continue
        if zones.zone_of(last) == "forward":
            log.info("SMARD file %s..%s reaches the forward zone: not requested", first, last)
            continue
        out.append(t)
    return out


def fetch_smard(start, end, cache_dir: Path, *, resolution: str, session: requests.Session | None = None,
                regions: tuple[str, ...] = SMARD_REGIONS) -> tuple[list[Path], str]:
    """Raw SMARD weekly files for ``start .. end`` at ``resolution`` ('hour' or 'quarterhour')."""
    zones.assert_readable(start, end)
    cache_dir = Path(cache_dir) / f"smard-{PRICE_CACHE_VERSION}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    session = session or requests.Session()
    last = None
    for region in regions:
        resp = _get(session, smard_url(region, resolution), None)  # timestamps only: not a data request
        if resp.status_code != 200:
            last = f"HTTP {resp.status_code} for region {region}"
            continue
        index = resp.json().get("timestamps") or []
        paths = []
        for t in smard_chunks_to_fetch(index, start, end):
            first, final = smard_file_days(t)
            zones.assert_readable(first, final)  # the file's own days, before it is requested
            name = f"FR_{region}_{resolution}_{t}.json"
            path = _cached(cache_dir, name)
            if path is None:
                url = smard_url(region, resolution, t)
                r = _get(session, url, None)
                if r.status_code != 200:
                    raise PriceDataError(f"HTTP {r.status_code} from SMARD {url}")
                rows = json.loads(r.content.decode("utf-8")).get("series") or []
                hi = zones.local_midnight_utc(final + timedelta(days=1))
                if rows and max(int(x[0]) for x in rows) >= int(hi.timestamp() * 1000):
                    raise PriceDataError(f"SMARD file {url} holds stamps after its week: not cached")
                path = _store(cache_dir, name, r.content, {"source": "smard", "url": url, "status": r.status_code})
            stamps, _ = _parse_smard(path)
            _refuse_forward(path, stamps, "SMARD")
            paths.append(path)
        return paths, region
    raise PriceDataError(f"SMARD filter {SMARD_FILTER} unreachable: {last}")


def _parse_smard(path: Path) -> tuple[pd.DatetimeIndex, np.ndarray]:
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = body.get("series") or []
    stamps = pd.to_datetime(np.asarray([r[0] for r in rows], dtype="int64"), unit="ms", utc=True)
    values = np.asarray([np.nan if r[1] is None else float(r[1]) for r in rows], dtype="float64")
    return pd.DatetimeIndex(stamps), values


def load_smard(paths: list[Path]) -> pd.Series:
    return _merge([pd.Series(v, index=s) for s, v in (_parse_smard(p) for p in paths)], "SMARD")


# ------------------------------------------------------------- hourly target


def to_hourly(raw: pd.Series, *, stamp: str = "start") -> tuple[pd.Series, dict]:
    """The scored hourly series (start-stamped, UTC) from the raw source series.

    ``stamp`` says whether the source labels a period by its ``"start"`` or its
    ``"end"`` (decided by the avail run). Before ``QUARTER_HOUR_FROM`` each hour
    takes its native hourly value. From that Paris day on, each UTC hour is the
    mean of its four quarter-hours and is NaN unless all four are present (a
    lone :00 value is never used). Returns the series and counts of what was done.
    """
    if stamp not in ("start", "end"):
        raise ValueError(f"unknown stamp convention {stamp!r}")
    raw = raw.dropna().sort_index()
    if raw.empty:
        return pd.Series(dtype="float64", name="price"), {"hours": 0}
    switch = zones.local_midnight_utc(QUARTER_HOUR_FROM)
    t, v = raw.index, raw.to_numpy(dtype="float64")
    hourly_mask = np.asarray(t < switch) if stamp == "start" else np.asarray(t <= switch)
    hour, quarter_len = pd.Timedelta(hours=1), pd.Timedelta(minutes=15)
    h_start = t[hourly_mask] - (hour if stamp == "end" else pd.Timedelta(0))
    q_start = t[~hourly_mask] - (quarter_len if stamp == "end" else pd.Timedelta(0))
    hourly = pd.Series(v[hourly_mask], index=h_start)
    off_grid_hourly = int((hourly.index.minute != 0).sum())
    hourly = hourly[hourly.index.minute == 0]
    quarter = pd.Series(v[~hourly_mask], index=q_start)
    off_grid_quarter = int((quarter.index.minute % 15 != 0).sum() + (quarter.index < switch).sum())
    quarter = quarter[(quarter.index.minute % 15 == 0) & (quarter.index >= switch)]
    grouped = quarter.groupby(quarter.index.floor("h"))
    counts, means = grouped.count(), grouped.mean()
    q_hours = means.where(counts == 4)  # stamps are unique, so 4 on the 15-minute grid are the four quarters
    out = pd.concat([hourly, q_hours]).sort_index()
    if out.index.duplicated().any():
        raise PriceDataError("an hour was built twice (hourly and quarter-hourly)")
    grid = pd.date_range(out.index.min(), out.index.max(), freq="1h", tz="UTC")
    out = out.reindex(grid)
    out.name = "price"
    info = {"hours": int(out.notna().sum()), "grid_hours": len(grid), "native_hours": int(len(hourly)),
            "hours_from_quarters": int((counts == 4).sum()), "incomplete_quarter_hours": int((counts != 4).sum()),
            "off_grid_hourly": off_grid_hourly, "off_grid_quarter": off_grid_quarter}
    return out, info


def compare_sources(a: pd.Series, b: pd.Series, *, start, end, tol: float = 0.01) -> dict:
    """Agreement of two hourly series over every UTC hour of the local days ``start .. end``.

    An hour missing or NaN in either series counts as a disagreement (spec: sources.agreement_rule).
    """
    lo = zones.local_midnight_utc(start)
    hi = zones.local_midnight_utc(pd.Timestamp(end).date() + timedelta(days=1))
    grid = pd.date_range(lo, hi, freq="1h", tz="UTC", inclusive="left")
    both = pd.concat([a.reindex(grid).rename("a"), b.reindex(grid).rename("b")], axis=1)
    diff = (both["a"] - both["b"]).abs()
    bad = both[~(diff <= tol)]  # NaN in either side fails the comparison
    return {"hours": int(len(grid)), "hours_differing": int(len(bad)),
            "missing_a": int(both["a"].isna().sum()), "missing_b": int(both["b"].isna().sum()),
            "share_agreeing": float(1 - len(bad) / len(grid)) if len(grid) else None,
            "max_abs_diff": float(diff.max()) if diff.notna().any() else None,
            "first_mismatches": [[str(t), None if pd.isna(r.a) else float(r.a), None if pd.isna(r.b) else float(r.b)]
                                 for t, r in bad.head(50).iterrows()]}


def local_hour_frame(raw: pd.Series, stamp: str) -> pd.Series:
    """Raw hourly values keyed by (Paris date, local hour) under a stamp convention (pre-2025-10-01 only)."""
    s = raw.dropna()
    start = s.index - (pd.Timedelta(hours=1) if stamp == "end" else pd.Timedelta(0))
    local = start.tz_convert(zones.PARIS)
    frame = pd.Series(s.to_numpy(), index=pd.MultiIndex.from_arrays([local.date, local.hour], names=["day", "hour"]))
    return frame[~frame.index.duplicated(keep=False)]  # an autumn repeated hour is ambiguous: dropped


def stamp_test(raw: pd.Series, epf: pd.Series, *, tol: float = 0.01) -> dict:
    """target.stamp_rule: agreement with EPF-FR (keyed by Paris date and hour) under each convention.

    ``epf`` is indexed by naive local timestamps (row h = the hour starting h); only its 24-hour days with
    rows 00..23 are used, and only the hours present under both mappings are compared.
    """
    e = epf.dropna()
    frame = pd.Series(e.to_numpy(), index=pd.MultiIndex.from_arrays([e.index.date, e.index.hour], names=["day", "hour"]))
    full = frame.groupby(level=0).size()
    days24 = {d for d, n in full.items() if n == 24 and sorted(frame.loc[d].index) == list(range(24))}
    frame = frame[frame.index.get_level_values(0).isin(days24)]
    maps = {c: local_hour_frame(raw, c) for c in ("start", "end")}
    common = frame.index.intersection(maps["start"].index).intersection(maps["end"].index)
    out = {"hours_compared": int(len(common))}
    for c, m in maps.items():
        agree = (m.reindex(common) - frame.reindex(common)).abs() <= tol
        out[f"share_{c}"] = float(agree.mean()) if len(common) else None
    s, e_ = out["share_start"], out["share_end"]
    verdict = None
    if s is not None and s >= 0.99 and e_ < 0.5:
        verdict = "start"
    elif e_ is not None and e_ >= 0.99 and s < 0.5:
        verdict = "end"
    out["verdict"] = verdict
    return out
