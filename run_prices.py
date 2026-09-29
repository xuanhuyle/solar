"""Experiment 4: t0 on French day-ahead prices (the frozen spec is ``solarbench.price_spec``).

Commands:

* ``avail`` - coverage and semantics only: what the sources hold, how they stamp
  time, whether they agree, the EPF-FR files for the LEAR gate and the weather
  coverage for P4. It never builds a forecast or computes an error metric. Its
  facts fill ``price_spec.AVAIL`` before the first forecast.
* ``gate-lear`` - K1: one logged attempt of the clean-room LEAR on EPF-FR 2015-2016
  (``--limit-days`` makes it a smoke: not an attempt, no metric).
* ``smoke`` - plumbing on a few 2023 days (outside the test period); no error metric.
* ``check`` - the in-run leak check at ``TEST_ORIGINS`` and K2, with real t0; nothing scored.
* ``run`` - the scored run. Its commit is the freeze commit (``lear.scored_only_if``):
  checks first, then every arm once on its windows, then the frozen statistics.

Every command but ``avail`` refuses to start unless the spec is frozen and AVAIL filled.
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


def weather_series(work: Path) -> tuple[pd.Series, pd.Series]:
    """The two national hourly weather series of weather_p4.constructions (temperature, radiation), read only
    through engine.data.fetch_weather_previous_runs (via engine.arms._national_weather)."""
    from engine import arms as am
    from engine import covs
    from solarbench import covariates as cov

    start, end = ps.PRICE_SPEC["periods"]["fetch_weather"]
    temp = am._national_weather(covs.TEMPERATURE_VARIABLE, covs.TEMPERATURE_MODEL, covs.TEMPERATURE_LEAD_DAYS,
                                covs.CONSUMPTION_WEIGHTS, max(start, covs.TEMPERATURE_FIRST), end, work / "weather")
    rad = am._national_weather(covs.RADIATION_VARIABLE, covs.RADIATION_MODEL, covs.RADIATION_LEAD_DAYS,
                               cov.REGION_WEIGHTS, "2024-03-08", end, work / "weather")
    return temp, rad


def ported_weather(work: Path) -> dict[str, pd.Series]:
    """The two P4 weather series on the hourly price grid, ported per weather_p4.hourly_conventions."""
    from engine import covs
    from solarbench import covariates as cov

    start, end = ps.PRICE_SPEC["periods"]["fetch_weather"]
    temp, rad = weather_series(work)
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


# ============================================================== gate-lear, smoke, check, run


class StopRun(RuntimeError):
    """A frozen rule stops the command before anything is scored; the owner decides."""


PRICE_FIRST_DAY_MAX = "2019-12-02"  # periods.price_first_day_max
SMOKE_DAYS = ("2023-03-26", "2023-06-15", "2023-10-29", "2023-12-31")  # 23-, 24-, 25- and 24-hour days of 2023
PROGRAM_ROLE = ("Programme role (docs/experiment_4/PROGRAM_ROLE.md, not part of the frozen reading table): P4 is "
                "the first price-domain test of the core product primitive, whether additional public information "
                "supplied through t0 covariates creates incremental predictive value. Experiment 4 is "
                "discovery-grade and cannot by itself satisfy the project's independent-confirmation milestone.")


def _jsonable(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (pd.Timestamp, date)):
        return o.isoformat()
    if isinstance(o, (set, frozenset)):
        return sorted(o, key=str)
    if isinstance(o, pd.DataFrame):
        return f"<table: {len(o)} rows>"
    return str(o)


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_jsonable) + "\n", encoding="utf-8")


def _commit() -> str | None:
    import os
    import subprocess

    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def _versions() -> dict:
    import importlib.metadata as im

    out = {"python": sys.version.split()[0]}
    for pkg in ("numpy", "pandas", "scikit-learn", "torch", "t0"):
        try:
            out[pkg] = im.version(pkg)
        except im.PackageNotFoundError:
            out[pkg] = None
    return out


def base_meta(args, command: str) -> dict:
    from solarbench import price_run as pr_

    return {"command": command, "experiment": ps.PRICE_SPEC["experiment"], "status": ps.PRICE_SPEC["status"],
            "spec_sha256": ps.spec_sha256(), "pinned_spec_sha256": ps.PRICE_SPEC_SHA256, "avail": dict(ps.AVAIL),
            "commit": _commit(), "run_id": getattr(args, "run_id", None),
            "lear_sha256_start": pr_.file_sha256("solarbench/lear.py"),
            "t0": {k: ps.PRICE_SPEC["t0"][k] for k in ("repo_id", "revision")}, "versions": _versions(),
            "attribution": ps.ATTRIBUTION}


def smard_agreement(hourly: pd.Series, work: Path, stamp: str) -> dict:
    """sources.agreement_rule on the series this command scores (the same files and rule as the avail run)."""
    h_paths, region = pd_.fetch_smard("2022-01-01", "2025-10-05", work, resolution="hour")
    q_paths, _ = pd_.fetch_smard("2025-09-29", "2025-12-28", work, resolution="quarterhour", regions=(region,))
    smard_raw = _split_resolution(pd_.load_smard(h_paths), pd_.load_smard(q_paths), stamp)
    smard_hourly, _ = pd_.to_hourly(smard_raw, stamp=stamp)
    out = pd_.compare_sources(hourly, smard_hourly, start="2022-01-01", end="2025-12-28")
    out.update(region=region, not_cross_checked=["2025-12-29", "2025-12-30", "2025-12-31"])
    return out


def load_prices(work: Path, meta: dict, *, cross_check: bool) -> pd.Series:
    """The scored hourly French price series under the frozen rules: price_first_day_max, the seal (the door),
    the licence rule, AVAIL's stamp convention and (``cross_check``) sources.agreement_rule. A failed rule or an
    unreachable source stops the command (StopRun / PriceDataError); nothing is switched or relaxed."""
    p = ps.PRICE_SPEC["periods"]
    if ps.AVAIL["price_first_day"] > PRICE_FIRST_DAY_MAX:
        raise StopRun(f"AVAIL.price_first_day {ps.AVAIL['price_first_day']} is after {PRICE_FIRST_DAY_MAX}")
    paths = pd_.fetch_energy_charts(p["fetch_prices"][0], p["fetch_prices"][1], work)
    refusals = pd_.licence_refusals(paths, list(ps.AVAIL["licence_info"]))
    meta["licence"] = {"files": len(paths), "refusals": refusals}
    if refusals or not paths:
        raise StopRun(f"licence rule failed: {refusals or 'no response'}")
    raw, licences = pd_.load_energy_charts(paths)
    meta["licence"]["seen"] = sorted(licences)
    stamp = ps.AVAIL["price_stamp"]
    hourly, info = pd_.to_hourly(raw, stamp=stamp)
    meta["prices"] = {"stamp": stamp, "hourly": info, "first": str(hourly.first_valid_index()),
                      "last": str(hourly.last_valid_index())}
    if cross_check:
        agreement = smard_agreement(hourly, work, stamp)
        meta["agreement"] = agreement
        if not (agreement.get("share_agreeing") is not None and agreement["share_agreeing"] >= 0.999):
            raise StopRun(f"sources.agreement_rule failed: share {agreement.get('share_agreeing')}")
    return hourly


def load_weather(work: Path, grid: pd.DatetimeIndex, meta: dict) -> tuple:
    """t0_cal_wx's two weather covariates on the price grid (weather_p4). A failed read stops the command:
    an unreachable source is never turned into a P4 state."""
    try:
        temp, rad = weather_series(work)
    except Exception as exc:
        raise StopRun(f"weather could not be read: {type(exc).__name__}: {exc}") from exc
    t, r = px_().weather_covariates(temp, rad, grid)
    meta["weather"] = {c.name: {"cells": int(np.isfinite(c.series.to_numpy()).sum()),
                                "first": str(c.series.first_valid_index()), "last": str(c.series.last_valid_index())}
                       for c in (t, r)}
    return t, r


def px_():
    from solarbench import price_exp

    return price_exp


def load_model():
    """t0-alpha at the pinned revision (HF_TOKEN from the environment; never printed)."""
    return px_().PriceT0Forecaster("loader").load()


def cmd_gate_lear(args) -> int:
    """K1: one logged attempt of the clean-room LEAR on EPF-FR 2015-2016 (or, with --limit-days, a smoke that is
    not an attempt and computes no metric). The printed record is transcribed into results/prices/k1_attempts.jsonl
    by hand, with this run's id; the sha256 of solarbench/lear.py it ran is part of it."""
    from solarbench import price_gates as pg
    from solarbench import price_run as pr_

    ps.require_frozen()
    work = Path(args.cache_dir)
    meta = base_meta(args, "gate-lear")
    status = pr_.k1_status(meta["lear_sha256_start"])
    meta["k1_log_before"] = status
    if args.limit_days is None and status["attempts"] >= 3:
        raise StopRun("gates.K1.attempts: three attempts are logged; no further attempt is allowed")
    fr, fr_sha = _download(EPF_FR_URL, work / "epf" / "FR.csv")
    pub, pub_sha = _download(EPF_PUBLISHED_URL, work / "epf" / "published_FR.csv")
    meta["inputs"] = {"fr_csv_sha256": fr_sha, "published_sha256": pub_sha}
    if fr_sha != ps.AVAIL["epf_fr_sha256"] or pub_sha != EPF_PUBLISHED_SHA256:
        raise StopRun("K1 inputs differ from the pinned sha256 (AVAIL.epf_fr_sha256 / the published CSV)")
    result = pg.run_k1(fr, pub, processes=args.processes, limit_days=args.limit_days)
    record = {"run_id": args.run_id, "commit": meta["commit"], "lear_sha256": result.get("lear_sha256"),
              "status": result.get("status"), "pass": bool(result.get("pass")), "smoke": bool(result.get("smoke")),
              "counts_as_attempt": bool(result.get("counts_as_attempt")),
              "attempt_number": status["attempts"] + 1 if result.get("counts_as_attempt") else None}
    meta["record"] = record
    _dump(OUT / "k1_attempt.json", {"meta": meta, "result": result})
    print("K1 record (transcribe into results/prices/k1_attempts.jsonl):")
    print(json.dumps(record, sort_keys=True))
    return 0 if record["pass"] or record["smoke"] else 2


def _prepare(args, meta: dict, *, cross_check: bool) -> dict:
    """What check and run share: frozen spec, prices, the 2023 selection, K1 from the log, weather, t0, K3,
    the arms. Nothing here scores a test day."""
    from solarbench import price_gates as pg
    from solarbench import price_run as pr_

    ps.require_frozen()
    work = Path(args.cache_dir)
    series = load_prices(work, meta, cross_check=cross_check)
    sel = pr_.select_best_simple(series)
    meta["selection"] = sel
    k1 = pr_.k1_status(meta["lear_sha256_start"])
    meta["k1"] = k1
    wx = load_weather(work, series.index, meta)
    model = load_model()
    k3 = pg.run_k3(series, model)
    meta["k3"] = k3
    k3_passed = bool(k3.get("pass"))
    arms = pr_.build_arms(sel["best"], model, weather=wx, with_lear=k1["passed"], lear_processes=args.processes)
    return {"series": series, "model": model, "arms": arms, "k1_passed": bool(k1["passed"]), "k3_passed": k3_passed,
            "p4_first_day": date.fromisoformat(ps.AVAIL["p4_first_day"])}


def _checks(ctx: dict, meta: dict) -> bool:
    """The in-run leak check at TEST_ORIGINS, then K2; both before anything is scored."""
    from solarbench import price_gates as pg
    from solarbench import price_run as pr_

    leak = pr_.in_run_leak_check(ctx["series"], ctx["arms"], p4_first_day=ctx["p4_first_day"],
                                 k3_passed=ctx["k3_passed"], k1_passed=ctx["k1_passed"])
    meta["leak_check"] = leak
    if not leak["pass"]:
        meta["stopped"] = "the in-run leak check failed: nothing is scored"
        return False
    k2 = pg.run_k2_at_origins(ctx["arms"], ctx["model"], ctx["series"], p4_first_day=ctx["p4_first_day"],
                              k3_passed=ctx["k3_passed"])
    meta["k2_attempts"] = [k2]
    if not k2["pass"]:
        meta["stopped"] = "K2 failed: nothing is scored"
        return False
    return True


def cmd_check(args) -> int:
    meta = base_meta(args, "check")
    meta["note"] = "the in-run leak check at TEST_ORIGINS and K2: no test day is scored"
    try:
        ctx = _prepare(args, meta, cross_check=True)
        ok = _checks(ctx, meta)
    finally:
        _dump(OUT / "check.json", meta)
    print(json.dumps({"leak_check_pass": meta.get("leak_check", {}).get("pass"),
                      "k2_pass": (meta.get("k2_attempts") or [{}])[-1].get("pass"),
                      "k1": meta.get("k1"), "k3_pass": meta.get("k3", {}).get("pass"),
                      "selection": meta.get("selection", {}).get("best")}, indent=2, default=_jsonable))
    return 0 if ok else 2


def cmd_smoke(args) -> int:
    """Plumbing only, on a few 2023 days (outside the test period): every arm but t0_cal_wx (no weather before
    2024-02-06) forecasts them, the weather day rule is counted, and K3 runs on two of its days. No error
    metric of any arm is computed and nothing here is a result."""
    import time

    from solarbench import price_gates as pg
    from solarbench import price_run as pr_

    ps.require_frozen()
    px = px_()
    work = Path(args.cache_dir)
    meta = base_meta(args, "smoke")
    meta["note"] = "plumbing only: 2023 days, no error metric, no result"
    try:
        series = load_prices(work, meta, cross_check=False)
        sel = pr_.select_best_simple(series)
        meta["selection"] = sel
        wx = load_weather(work, series.index, meta)
        model = load_model()
        arms = pr_.build_arms(sel["best"], model, weather=wx, with_lear=True, lear_processes=args.processes)
        days = [date.fromisoformat(d) for d in SMOKE_DAYS]
        windows = px.build_price_windows(series, days)
        strict = px.build_price_windows(series, days, strict=True)
        lear_eq = px.PriceEmpiricalQuantiles(base=px.LearEnsemble(processes=args.processes), name="lear_ens_eq")
        runs = [(a, windows) for a in (arms.t0, arms.t0_cal, arms.best, arms.eq, arms.naive, arms.prev_week,
                                       arms.lear, lear_eq)]
        runs += [(arms.t0_cal_strict, strict), (arms.best_strict, strict)]
        out = {}
        for arm, ws in runs:
            t = time.time()
            df = px.run_price_backtest(series, [arm], ws)
            q = [c for c in df.columns if c.startswith("q")]
            out[arm.name] = {"seconds": round(time.time() - t, 2), "windows": len(ws), "rows": int(len(df)),
                             "hours_per_day": {str(k): int(v) for k, v in df.groupby("delivery_date").size().items()},
                             "finite_point_share": float(np.isfinite(df["y_hat"]).mean()),
                             "finite_quantile_share": (float(np.isfinite(df[q].to_numpy()).mean()) if q else None)}
        meta["arms"] = out
        meta["t0_missing"] = {a.name: a.missing for a in (arms.t0, arms.t0_cal, arms.t0_cal_strict)}
        p4 = [date.fromisoformat(d) for d in ps.TEST_ORIGINS if d >= ps.AVAIL["p4_first_day"]]
        meta["weather_day_rule_at_test_origins"] = {
            str(w.delivery_date): pr_.p4_day_ok(arms.t0_cal_wx, w)
            for w in px.build_price_windows(series, sorted(p4), require_target=False)}
        t = time.time()
        meta["k3_smoke"] = pg.run_k3(series, model, days=pg.k3_days()[:2])
        meta["k3_smoke_seconds"] = round(time.time() - t, 1)
    finally:
        _dump(OUT / "smoke.json", meta)
    print(json.dumps({"arms": meta.get("arms"), "k3_smoke_outcome": meta.get("k3_smoke", {}).get("smoke_outcome")},
                     indent=2, default=_jsonable))
    return 0


def _stats(df: pd.DataFrame, info: dict, ctx: dict, scored: set[str]) -> tuple[dict, list[str], dict]:
    """The primaries, their states and the reading table, the strict row, the secondaries, the slices and
    tables of each primary, and carry-forward, all from price_stats as frozen."""
    from solarbench import price_stats as st

    p4_rule_days = [date.fromisoformat(d) for d in info.get("p4_days", {}).get("kept_days", [])]
    results, tables = st.primary_results(df, k1_passed=ctx["k1_passed"], k3_passed=ctx["k3_passed"],
                                         p4_rule_days=p4_rule_days if ctx["k3_passed"] else None, scored=scored)
    verdicts = st.states(results)
    strict = st.strict_skills(df, scored=scored)
    lines = st.summary_lines(results, verdicts, strict)
    out = {"primaries": results, "verdicts": verdicts, "strict": strict,
           "secondaries": st.secondaries(df, scored=scored, p4_rule_days=p4_rule_days, k1_passed=ctx["k1_passed"],
                                         k3_passed=ctx["k3_passed"]), "slices": {},
           "tables": {}}
    for pid in st.FAMILY:
        arm, ref, metric = st.probe_arms(pid)
        table = tables.get(pid)
        days = None if table is None else sorted(set(table["delivery_date"]))
        ok = table is not None and arm in scored and ref in scored
        out["slices"][pid] = st.slices(df, arm, ref, metric=metric, days=days, margin=st.MARGINS[pid], scored=ok)
        out["tables"][pid] = st.tables(table, arm, ref, scored=ok)
    out["carry_forward"] = st.carry_forward_all(tables, verdicts)
    return out, lines, tables


def cmd_run(args) -> int:
    """The scored run (its commit is the freeze commit): every check first, then every arm once on its windows,
    then the frozen statistics and reading table. Any stop leaves nothing scored."""
    from solarbench import price_run as pr_

    meta = base_meta(args, "run")
    try:
        ctx = _prepare(args, meta, cross_check=True)
        if not _checks(ctx, meta):
            return 3
        df, info = pr_.forecast_all(ctx["series"], ctx["arms"], p4_first_day=ctx["p4_first_day"],
                                    k3_passed=ctx["k3_passed"])
        meta["forecast"] = info
        meta["lear_sha256_end"] = pr_.file_sha256("solarbench/lear.py")
        if meta["lear_sha256_end"] != meta["lear_sha256_start"]:
            meta["stopped"] = "solarbench/lear.py changed during the run: nothing is scored"
            return 3
        scored = set(df["method"])
        if ctx["k3_passed"]:
            scored.add("t0_cal_wx")  # scored even if no P4 day passed the day rule ('no P4 day scored')
        meta["scored_arms"] = sorted(scored)
        out, lines, tables = _stats(df, info, ctx, scored)
        OUT.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUT / "forecasts.csv.gz", index=False)
        for pid, table in tables.items():
            if table is not None:
                table.to_csv(OUT / f"per_day_{pid}.csv", index=False)
        _dump(OUT / "results.json", out)
        summary = ["# Experiment 4: t0 on French day-ahead prices", "", *lines, "", PROGRAM_ROLE, ""]
        (OUT / "summary.md").write_text("\n".join(summary), encoding="utf-8")
        print("\n".join(summary))
    finally:
        _dump(OUT / "run_meta.json", meta)
    return 0


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("avail", help="coverage and semantics only; no forecasts")
    a.add_argument("--cache-dir", default="pricecache")
    for name, text in (("gate-lear", "K1: one logged LEAR attempt on EPF-FR (or a smoke with --limit-days)"),
                       ("smoke", "plumbing on a few 2023 days; no error metric"),
                       ("check", "the in-run leak check at TEST_ORIGINS and K2; nothing scored"),
                       ("run", "the scored run")):
        c = sub.add_parser(name, help=text)
        c.add_argument("--cache-dir", default="pricecache")
        c.add_argument("--run-id", default=None)
        c.add_argument("--processes", type=int, default=4)
        if name == "gate-lear":
            c.add_argument("--limit-days", type=int, default=None)
    args = ap.parse_args(argv)
    commands = {"avail": cmd_avail, "gate-lear": cmd_gate_lear, "smoke": cmd_smoke, "check": cmd_check,
                "run": cmd_run}
    try:
        return commands[args.cmd](args)
    except (StopRun, pd_.PriceDataError) as exc:
        log.error("stopped: %s", exc)
        print(f"STOPPED: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
