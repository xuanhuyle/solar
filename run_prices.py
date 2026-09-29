"""Experiment 4: t0 on French day-ahead prices (the frozen spec is ``solarbench.price_spec``).

Commands:

* ``avail`` - coverage and semantics only: what the sources hold, how they stamp
  time, whether they agree, the EPF-FR files for the LEAR gate and the weather
  coverage for P4. It never builds a forecast or computes an error metric. Its
  facts fill ``price_spec.AVAIL`` before the first forecast.

(The gate, check and run commands are added before the freeze commit.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from engine import zones
from solarbench import price_data as pd_
from solarbench import price_spec as ps

log = logging.getLogger("run_prices")

OUT = Path("results/prices")
EPF_FR_URL = "https://zenodo.org/records/4624805/files/FR.csv?download=1"
EPF_PUBLISHED_URL = ("https://raw.githubusercontent.com/jeslago/epftoolbox/47d6e0629f65ebd19d3c12cb5689dbad0c2ea078/"
                     "forecasts/Forecasts_FR_DNN_LEAR_ensembles.csv")
EPF_PUBLISHED_SHA256 = "671d65842180fd7fc0f603eca6281f4ddc581983cbfb4991e97e291d5d88ab08"
DST_DAYS = ("2024-03-31", "2024-10-27", "2025-03-30", "2025-10-26")


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _local_days(series: pd.Series) -> pd.Series:
    """Values present per Europe/Paris day."""
    s = series.dropna()
    return s.groupby(s.index.tz_convert(zones.PARIS).date).size()


def expected_hours(day: date) -> int:
    a = zones.local_midnight_utc(day)
    b = zones.local_midnight_utc(day + timedelta(days=1))
    return int((b - a) / pd.Timedelta(hours=1))


def _download(url: str, dest: Path) -> tuple[Path, str]:
    import requests

    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        resp = pd_._get(requests.Session(), url, None, timeout=300)
        if resp.status_code != 200:
            raise pd_.PriceDataError(f"HTTP {resp.status_code} from {url}")
        dest.write_bytes(resp.content)
    return dest, hashlib.sha256(dest.read_bytes()).hexdigest()


def epf_files(work: Path) -> dict:
    """The K1 gate's inputs: EPF-FR (Zenodo) and the pinned published LEAR forecasts."""
    out: dict = {}
    try:
        path, sha = _download(EPF_FR_URL, work / "epf" / "FR.csv")
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        out["fr_csv"] = {"sha256": sha, "columns": list(df.columns), "first": str(df.index.min()),
                         "last": str(df.index.max()), "rows": int(len(df))}
    except Exception as exc:  # reported, not fatal: K1 then cannot run
        out["fr_csv"] = {"error": f"{type(exc).__name__}: {exc}"}
        df = None
    try:
        path, sha = _download(EPF_PUBLISHED_URL, work / "epf" / "published_FR.csv")
        pub = pd.read_csv(path, index_col=0, parse_dates=True)
        out["published"] = {"sha256": sha, "pinned_match": sha == EPF_PUBLISHED_SHA256, "rows": int(len(pub)),
                            "published_mae": {c: round(float((pub[c] - pub["Real price"]).abs().mean()), 4)
                                              for c in pub.columns if c.startswith("LEAR")}}
        if df is not None:
            price_col = df.columns[0]
            joined = pd.concat([df[price_col].rename("fr"), pub["Real price"].rename("pub")], axis=1).dropna()
            out["published"]["fr_csv_price_column"] = price_col
            out["published"]["fr_csv_matches_real_price"] = {
                "rows": int(len(joined)), "max_abs_diff": float((joined["fr"] - joined["pub"]).abs().max())}
    except Exception as exc:
        out["published"] = {"error": f"{type(exc).__name__}: {exc}"}
    return out, (df if df is not None else None)


def ported_weather(work: Path) -> dict[str, pd.Series]:
    """The two P4 weather series on the hourly price grid, ported per weather_p4.hourly_conventions."""
    from engine import arms as am
    from engine import covs
    from solarbench import covariates as cov

    start, end = ps.PRICE_SPEC["periods"]["fetch_weather"]
    temp = am._national_weather(covs.TEMPERATURE_VARIABLE, covs.TEMPERATURE_MODEL, covs.TEMPERATURE_LEAD_DAYS,
                                covs.CONSUMPTION_WEIGHTS, max(start, covs.TEMPERATURE_FIRST), end, work / "weather")
    rad = am._national_weather(covs.RADIATION_VARIABLE, covs.RADIATION_MODEL, covs.RADIATION_LEAD_DAYS,
                               cov.REGION_WEIGHTS, "2024-03-08", end, work / "weather")
    grid = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(
        pd.Timestamp(end).date() + timedelta(days=1)), freq="1h", tz="UTC", inclusive="left")
    rad_v, _ = cov.hourly_to_slots(rad.sort_index(), grid, 30)
    temp_v, _ = covs.instant_to_slots(temp.sort_index(), grid, 30)
    return {"wx_radiation": pd.Series(rad_v, index=grid), "wx_temperature": pd.Series(temp_v, index=grid)}


def p4_days(cells: dict[str, pd.Series]) -> dict:
    """weather_p4.day_rule on the ported cells: the first qualifying day and the count."""
    t0 = ps.PRICE_SPEC["t0"]
    first = pd.Timestamp(ps.PRICE_SPEC["periods"]["p4_days"][0]).date()
    last = pd.Timestamp(ps.PRICE_SPEC["periods"]["p4_days"][1]).date()
    ok_days, reasons = [], {"horizon": 0, "context": 0}
    d = first
    while d <= last:
        cutoff = zones.local_midnight_utc(d) - pd.Timedelta(hours=1)
        horizon = pd.date_range(cutoff + pd.Timedelta(hours=1), periods=t0["fixed_horizon_hours"], freq="1h")
        context = pd.date_range(end=cutoff, periods=t0["context_hours"], freq="1h")
        h_ok = all(s.reindex(horizon).notna().all() for s in cells.values())
        c_ok = min(float(s.reindex(context).notna().mean()) for s in cells.values()) >= t0["min_context_valid"]
        if h_ok and c_ok:
            ok_days.append(d)
        else:
            reasons["horizon" if not h_ok else "context"] += 1
        d += timedelta(days=1)
    return {"first_day": ok_days[0].isoformat() if ok_days else None, "days": len(ok_days),
            "failed": reasons, "failed_days": [str(x) for x in sorted(
                set(pd.date_range(first, last).date) - set(ok_days))][:100]}


def _split_resolution(hourly_raw: pd.Series, quarter_raw: pd.Series, stamp: str) -> pd.Series:
    """Hourly-file rows before the switch and quarter-hour-file rows from it (no overlapping stamps)."""
    switch = zones.local_midnight_utc(pd_.QUARTER_HOUR_FROM)
    h = hourly_raw[hourly_raw.index < switch] if stamp == "start" else hourly_raw[hourly_raw.index <= switch]
    q = quarter_raw[quarter_raw.index >= switch] if stamp == "start" else quarter_raw[quarter_raw.index > switch]
    return pd.concat([h, q]).sort_index()


def cmd_avail(args) -> int:
    work = Path(args.cache_dir)
    OUT.mkdir(parents=True, exist_ok=True)
    spec = ps.PRICE_SPEC
    p = spec["periods"]
    report: dict = {"spec_sha256": ps.spec_sha256(), "pinned": ps.PRICE_SPEC_SHA256,
                    "note": "coverage and semantics only: no forecast, no error metric"}

    # 1. the scored source over the fetch period, and the licence rule
    paths = pd_.fetch_energy_charts(p["fetch_prices"][0], p["fetch_prices"][1], work)
    raw, licences = pd_.load_energy_charts(paths)
    report["energy_charts"] = {"files": len(paths), "raw_values": int(raw.notna().sum()),
                               "first": str(raw.first_valid_index()), "last": str(raw.last_valid_index()),
                               "licence_info": sorted(licences)}

    # 2. the stamp convention, by content only (target.stamp_rule)
    report["epf"], epf = epf_files(work)
    ov = p["fetch_prices_overlap_check"]["days"]
    try:
        ov_raw, ov_lic = pd_.load_energy_charts(pd_.fetch_energy_charts(ov[0], ov[1], work))
        licences |= ov_lic
    except pd_.PriceDataError as exc:
        ov_raw = pd.Series(dtype="float64")
        report["overlap_error"] = str(exc)
    stamp_report: dict = {"energy_charts_overlap_values": int(ov_raw.notna().sum())}
    verdict = None
    if epf is not None:
        price = epf[epf.columns[0]]
        if ov_raw.notna().sum():
            stamp_report["energy_charts"] = pd_.stamp_test(ov_raw, price)
            verdict = stamp_report["energy_charts"]["verdict"]
        if verdict is None and not ov_raw.notna().sum():
            try:
                sp, _ = pd_.fetch_smard(ov[0], ov[1], work, resolution="hour")
                stamp_report["smard"] = pd_.stamp_test(pd_.load_smard(sp), price)
                stamp_report["smard_transfer_pending_agreement"] = True
                verdict = stamp_report["smard"]["verdict"]
            except pd_.PriceDataError as exc:
                stamp_report["smard_error"] = str(exc)
    report["stamp_rule"] = stamp_report
    stamp = verdict or "start"  # for the descriptive counts below only; the checks fail without a verdict

    # 3. hourly target, day completeness, DST days, quarter-hours
    hourly, info = pd_.to_hourly(raw, stamp=stamp)
    report["hourly"] = info
    per_day = _local_days(hourly)
    days = pd.date_range(p["fetch_prices"][0], p["fetch_prices"][1], freq="D").date
    complete = [d for d in days if per_day.get(d, 0) == expected_hours(d)]
    incomplete = [str(d) for d in days if per_day.get(d, 0) != expected_hours(d)]
    report["days"] = {"total": len(days), "complete": len(complete),
                      "first_complete": str(complete[0]) if complete else None,
                      "incomplete_count": len(incomplete), "incomplete": incomplete[:200]}
    report["dst_days"] = {d: {"hours": int(per_day.get(date.fromisoformat(d), 0)),
                              "expected": expected_hours(date.fromisoformat(d))} for d in DST_DAYS}
    q4 = raw[raw.index >= zones.local_midnight_utc(pd_.QUARTER_HOUR_FROM)].dropna()
    q4_counts = q4.groupby(q4.index.tz_convert(zones.PARIS).date).size()
    report["quarter_hours_per_day"] = {"days": int(len(q4_counts)),
                                       "counts": {str(k): int(v) for k, v in q4_counts.value_counts().items()}}
    monthly = hourly.dropna().groupby(hourly.dropna().index.tz_convert(zones.PARIS).strftime("%Y-%m")).size()
    report["hours_per_month"] = {k: int(v) for k, v in monthly.items()}

    # 4. the cross-check source (sources.agreement_rule)
    try:
        h_paths, region = pd_.fetch_smard("2022-01-01", "2025-10-05", work, resolution="hour")
        q_paths, _ = pd_.fetch_smard("2025-09-29", "2025-12-28", work, resolution="quarterhour", regions=(region,))
        smard_raw = _split_resolution(pd_.load_smard(h_paths), pd_.load_smard(q_paths), stamp)
        smard_hourly, smard_info = pd_.to_hourly(smard_raw, stamp=stamp)
        report["smard"] = {"region": region, "files": len(h_paths) + len(q_paths), "hourly": smard_info,
                           "last": str(smard_raw.last_valid_index())}
        report["agreement"] = pd_.compare_sources(hourly, smard_hourly, start="2022-01-01", end="2025-12-28")
        report["agreement"]["not_cross_checked"] = ["2025-12-29", "2025-12-30", "2025-12-31"]
        day = pd.Timestamp("2024-06-26")
        lo, hi = zones.local_midnight_utc(day), zones.local_midnight_utc(day + pd.Timedelta(days=1))
        report["day_2024_06_26"] = {
            "energy_charts": hourly[(hourly.index >= lo) & (hourly.index < hi)].round(2).tolist(),
            "smard": smard_hourly[(smard_hourly.index >= lo) & (smard_hourly.index < hi)].round(2).tolist()}
    except pd_.PriceDataError as exc:
        report["smard"] = {"error": str(exc)}
    agree = report.get("agreement", {}).get("share_agreeing")
    if "smard" in stamp_report and verdict is not None:  # SMARD's convention transfers only if the raw stamps agree
        verdict = verdict if agree is not None and agree >= 0.999 else None
        stamp_report["transferred"] = verdict is not None

    # 5. weather for P4
    try:
        report["p4"] = p4_days(ported_weather(work))
    except Exception as exc:
        report["p4"] = {"error": f"{type(exc).__name__}: {exc}"}

    # 6. the AVAIL facts this run proposes (committed by hand after review) and the checks
    first_day = report["days"]["first_complete"]
    report["proposed_avail"] = {
        "price_stamp": verdict,
        "price_first_day": first_day,
        "p4_first_day": report.get("p4", {}).get("first_day"),
        "epf_fr_sha256": report["epf"].get("fr_csv", {}).get("sha256"),
        "licence_info": sorted(licences),
    }
    report["checks"] = {
        "stamp_decided": verdict in ("start", "end"),
        "sources_agree": agree is not None and agree >= 0.999,
        "licence_ok": bool(licences) and all(pd_.licence_ok(x) for x in licences),
        "price_first_day_ok": first_day is not None and first_day <= "2019-12-02",
        "dst_days_ok": all(v["hours"] == v["expected"] for v in report["dst_days"].values()),
        "published_forecasts_pinned": report["epf"].get("published", {}).get("pinned_match") is True,
        "published_mae_match": report["epf"].get("published", {}).get("published_mae") == {
            k: v for k, v in ps.PRICE_SPEC["gates"]["K1"]["published_mae"].items()},
        "p4_first_day_found": report["proposed_avail"]["p4_first_day"] is not None,
    }
    _write_json(OUT / "avail.json", report)
    print(json.dumps({k: report[k] for k in ("checks", "proposed_avail", "stamp_rule", "days", "dst_days",
                                              "quarter_hours_per_day")}, indent=2, default=str))
    print(json.dumps({k: report.get(k) for k in ("energy_charts", "hourly", "smard", "agreement", "epf", "p4",
                                                  "day_2024_06_26")}, indent=2, default=str))
    return 0 if all(report["checks"].values()) else 2


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("avail", help="coverage and semantics only; no forecasts")
    a.add_argument("--cache-dir", default="pricecache")
    args = ap.parse_args(argv)
    if args.cmd == "avail":
        return cmd_avail(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
