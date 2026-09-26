"""Command line for the knowledge engine: ``python -m engine <mode>``.

Modes built so far:

* ``selftest`` - no network: zones, fingerprints, the data door's refusals.
* ``seed`` - leaves the ledger's genesis, legacy results and C1 as pending
  entries for the record job (a no-op once the ledger has a genesis).
* ``probe`` - run one declarative probe spec (``ENGINE_SPEC_JSON`` or
  ``--spec-file``) on the discovery zone; result stamped EXPLORATORY.
* ``reproduce`` - the referee's self-check: P4 (2024) and C1 (2025) rerun as
  declarative specs must match their recorded numbers.
* ``avail`` - data coverage only, never forecast skill: national consumption
  2021-10 .. 2025-12 by month and vintage; Open-Meteo archived temperature
  forecasts by model and year at one point; 2023 regional consumption weights.
"""

from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import os

from engine import canon, data, ledger, zones

log = logging.getLogger("engine")
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "engine"
CACHE = ROOT / "enginecache"
PENDING = RESULTS / "pending.jsonl"


def current_ledger() -> list[dict]:
    """The ledger as fetched read-only by the workflow (``ENGINE_LEDGER``); verified on read."""
    path = os.environ.get("ENGINE_LEDGER")
    return ledger.read(Path(path)) if path else []


def _write(name: str, obj) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / name
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return path


def selftest(args) -> dict:
    checks: dict[str, bool] = {}
    checks["forward boundary is Paris midnight"] = str(zones.local_midnight_utc(zones.FORWARD_FROM)) == "2025-12-31 23:00:00+00:00"
    checks["request bounds round inward"] = zones.utc_request_days("2022-01-01", "2025-12-31")[1] == "2025-12-31"
    try:
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2025-12-01", "2026-01-15", CACHE)
        checks["forward read refused"] = False
    except zones.ZoneError:
        checks["forward read refused"] = True
    checks["2025 is not confirmable"] = not zones.confirmable("2025-06-01")
    checks["2026 is confirmable"] = zones.confirmable("2026-06-01")
    checks["canonical hash is stable"] = canon.sha256_of({"b": 1, "a": [1, 2]}) == canon.sha256_of({"a": [1, 2], "b": 1})
    out = {"mode": "selftest", "python": platform.python_version(), "checks": checks, "ok": all(checks.values())}
    return out


def _month_coverage(series: pd.Series, start: str, end: str) -> dict[str, float]:
    grid = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(pd.Timestamp(end) + pd.Timedelta(days=1)),
                         freq="30min", inclusive="left")
    ok = series.reindex(grid).notna()
    local = grid.tz_convert(zones.PARIS)
    return {str(k): round(float(v), 4) for k, v in ok.groupby(local.strftime("%Y-%m")).mean().items()}


def avail(args) -> dict:
    out: dict = {"mode": "avail", "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    # 1. National consumption, discovery zone plus the context lead-in.
    try:
        cons = data.load_odre(data.NATIONAL, "consommation", "2021-10-01", "2025-12-31", CACHE)
        out["consumption"] = {"first": str(cons.first_valid_index()), "last": str(cons.last_valid_index()),
                              "by_month": _month_coverage(cons, "2021-10-01", "2025-12-31")}
    except Exception as exc:  # report, do not hide
        out["consumption"] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
    # 2. Archived temperature forecasts at Paris, per model and year (coverage only).
    from solarbench.weather import WX_MODEL_PREFERENCE

    paris = {"Île-de-France": (48.857, 2.352)}
    variables = [f"temperature_2m_previous_day{n}" for n in (1, 2, 3)]
    wx: dict = {}
    for model in WX_MODEL_PREFERENCE:
        wx[model] = {}
        for year in (2022, 2023, 2024, 2025):
            start, end = f"{year}-01-01", f"{year}-12-31"
            try:
                frames = data.fetch_weather_previous_runs(model, variables, start, end, CACHE, points=paris)
                wx[model][year] = {v: {"valid_share": round(float(f.iloc[:, 0].notna().mean()), 4),
                                       "first_valid": str(f.iloc[:, 0].first_valid_index())}
                                   for v, f in frames.items()}
            except Exception as exc:
                wx[model][year] = {"error": f"{type(exc).__name__}: {exc}"[:300]}
    out["temperature_previous_runs"] = wx
    # 3. 2023 regional consumption shares (weights for a national temperature).
    try:
        weights, meta = data.consumption_region_weights_2023(CACHE)
        out["consumption_region_weights_2023"] = {k: round(v, 6) for k, v in weights.items()}
    except Exception as exc:
        out["consumption_region_weights_2023"] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
    return out


def _spec_from(args) -> dict:
    raw = Path(args.spec_file).read_text(encoding="utf-8") if args.spec_file else os.environ.get("ENGINE_SPEC_JSON", "")
    if not raw.strip():
        raise SystemExit("no spec: pass --spec-file or set ENGINE_SPEC_JSON")
    return json.loads(raw)


def _probe_entries(spec_raw: dict, submitted_by: str, ctx: dict, *, limit_days=None, model=None) -> tuple[list, dict]:
    """Run one probe; return its pending ledger entries and the result (or the rejection)."""
    from engine import arms, discover
    from engine.spec import SpecError, spec_sha256, validate_probe

    entries = current_ledger()
    try:
        norm = validate_probe(spec_raw)
    except SpecError as exc:
        payload = {"submitted_by": submitted_by, "spec": spec_raw, "reasons": exc.reasons}
        return [ledger.pending("probe_rejected", payload, ctx)], payload
    sha = spec_sha256(norm)
    items = [ledger.pending("probe_submitted", {"submitted_by": submitted_by, "probe_sha256": sha, "spec": norm}, ctx)]
    try:
        result = discover.run_probe(norm, cache_dir=CACHE, accepted=arms.latest_accepted(entries, norm["target"]),
                                    limit_days=limit_days, model=model)
    except Exception as exc:
        payload = {"submitted_by": submitted_by, "probe_sha256": sha, "error": f"{type(exc).__name__}: {exc}"[:500]}
        items.append(ledger.pending("error", payload, ctx))
        return items, payload
    result["submitted_by"] = submitted_by
    items.append(ledger.pending("probe_result", result, ctx))
    return items, result


def probe(args) -> dict:
    ctx = ledger.run_context("probe")
    items, result = _probe_entries(_spec_from(args), args.submitted_by, ctx, limit_days=args.limit_days)
    ledger.write_pending(PENDING, items)
    return {"mode": "probe", "result": result, "ok": "comparisons" in result}


#: The recorded numbers a declarative rerun must match (MAE in MW; README / ledger/confirmations.jsonl).
REPRODUCTIONS = {
    "P4_2024": {"period": "Y2024", "mae": {"t0_cal": 1571.0, "best_simple": 3114.4, "t0_plain": 1644.4, "rte_j1": 1368.2},
                "skill_t0_cal_vs_best_simple": 0.496},
    "C1_2025": {"period": "Y2025c", "mae": {"t0_cal": 1627.8, "best_simple": 3031.6, "t0_plain": 1711.0, "rte_j1": 1322.4},
                "skill_t0_cal_vs_best_simple": 0.463},
}


def reproduce(args) -> dict:
    ctx = ledger.run_context("reproduce")
    from engine import arms

    model = arms._t0("loader", (), None).load()
    all_items, checks = [], {}
    for key, want in REPRODUCTIONS.items():
        spec_raw = {"spec_version": "probe/0", "target": "consumption", "period": want["period"], "scope": "all",
                    "arms": [{"name": "t0_cal", "covariates": [{"id": "holiday", "transform": "raw"}]},
                             {"name": "t0_plain", "covariates": []}],
                    "comparisons": [{"arm": "t0_cal", "vs": "best_simple", "metric": "mae"},
                                    {"arm": "t0_plain", "vs": "best_simple", "metric": "mae"},
                                    {"arm": "t0_cal", "vs": "rte_j1", "metric": "mae"}],
                    "rationale": f"referee self-check: reproduce {key} through the declarative path"}
        items, result = _probe_entries(spec_raw, "referee:reproduction", ctx, limit_days=args.limit_days, model=model)
        all_items += items
        if "comparisons" not in result:
            checks[key] = {"pass": False, "error": result.get("error") or result.get("reasons")}
            continue
        got = {}
        for c in result["comparisons"]:
            got[c["arm"]] = c.get("mae_arm")
            got[c["vs"]] = c.get("mae_vs")
        skill = result["comparisons"][0].get("skill")
        rel = {k: None if got.get(k) is None else round(got[k] / v - 1.0, 5) for k, v in want["mae"].items()}
        ok = all(r is not None and abs(r) <= 0.005 for r in rel.values()) and skill is not None \
            and abs(skill - want["skill_t0_cal_vs_best_simple"]) <= 0.005
        checks[key] = {"pass": bool(ok), "mae_got": got, "mae_recorded": want["mae"], "relative_diff": rel,
                       "skill_got": skill, "skill_recorded": want["skill_t0_cal_vs_best_simple"],
                       "days": [c.get("days") for c in result["comparisons"]]}
    passed = all(v["pass"] for v in checks.values()) and not args.limit_days
    all_items.append(ledger.pending("gate", {"gate": "reproduction", "pass": passed, "tolerance": "0.5% MAE, 0.5 pp skill",
                                            "limit_days": args.limit_days, "checks": checks}, ctx))
    ledger.write_pending(PENDING, all_items)
    return {"mode": "reproduce", "checks": checks, "ok": passed or bool(args.limit_days)}


def seed(args) -> dict:
    from engine import legacy

    entries = current_ledger()
    if entries:
        return {"mode": "seed", "skipped": "the ledger already has a genesis", "head": ledger.head(entries)}
    items = legacy.seed_items(ledger.run_context("seed"))
    ledger.write_pending(PENDING, items)
    return {"mode": "seed", "pending": [i["kind"] for i in items]}


MODES = {"selftest": selftest, "avail": avail, "seed": seed, "probe": probe, "reproduce": reproduce}


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="python -m engine", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=sorted(MODES))
    p.add_argument("--spec-file", default=None)
    p.add_argument("--submitted-by", default="owner:manual")
    p.add_argument("--limit-days", type=int, default=None)
    args = p.parse_args(argv)
    out = MODES[args.mode](args)
    path = _write(f"{args.mode}.json", out)
    print(path.read_text(encoding="utf-8"))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
