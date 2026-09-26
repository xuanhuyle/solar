"""Command line for the knowledge engine: ``python -m engine <mode>``.

Modes built so far:

* ``selftest`` - no network: zones, fingerprints, the data door's refusals.
* ``seed`` - leaves the ledger's genesis, legacy results and C1 as pending
  entries for the record job (a no-op once the ledger has a genesis).
* ``probe`` - run one declarative probe spec (``ENGINE_SPEC_JSON`` or
  ``--spec-file``) on the discovery zone; result stamped EXPLORATORY.
* ``reproduce`` - the referee's self-check: P4 (2024) and C1 (2025) rerun as
  declarative specs must match their recorded numbers.
* ``gate`` - the known-answer gate for each weather covariate (real t0);
  a weather covariate is refused in probes until its gate has passed.
* ``freeze`` - freeze a claim batch (``ENGINE_BATCH_JSON`` or ``--batch-file``):
  window, alpha share and a receipt are fixed now.
* ``vault`` - open a matured batch's forward window once (``--batch-id``), in a
  run the owner approved for the engine-vault environment; PASS / NOT PASS.
* ``vault_dryrun`` - the same scoring path on consumed 2025 data, labelled
  NON-CONFIRMATORY (a rehearsal, never a verdict).
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

    from engine.referee import budget, known_answer

    entries = current_ledger()
    try:
        norm = validate_probe(spec_raw)
    except SpecError as exc:
        payload = {"submitted_by": submitted_by, "spec": spec_raw, "reasons": exc.reasons}
        return [ledger.pending("probe_rejected", payload, ctx)], payload
    sha = spec_sha256(norm)
    reasons = []
    gates = known_answer.passed_gates(entries)
    for arm in norm["arms"]:
        for c in arm["covariates"]:
            if c["id"] in known_answer.WEATHER and (norm["target"], c["id"]) not in gates:
                reasons.append(f"{c['id']} has not passed its known-answer gate for {norm['target']} yet")
    researcher = submitted_by.startswith("researcher")
    if researcher and not reasons:
        prior = budget.recorded(entries, sha)
        if prior is not None:
            payload = {"submitted_by": submitted_by, "probe_sha256": sha, "duplicate_of_seq": prior["seq"],
                       "note": "identical probe already run; its recorded result is returned at no cost"}
            return [ledger.pending("note", payload, ctx)], prior
        if budget.remaining(entries) < len(norm["comparisons"]):
            reasons.append(f"discovery budget spent ({budget.spent(entries)} of {budget.DISCOVERY_BUDGET} evaluations)")
    if reasons:
        payload = {"submitted_by": submitted_by, "spec": norm, "probe_sha256": sha, "reasons": reasons}
        return [ledger.pending("probe_rejected", payload, ctx)], payload
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


def gate(args) -> dict:
    """The known-answer gate for every weather covariate in the catalogue (real t0)."""
    from engine import arms
    from engine.referee import known_answer

    ctx = ledger.run_context("gate")
    model = arms._t0("loader", (), None).load()
    items, out = [], {}
    for cid, _ in known_answer.WEATHER.items():
        from engine import catalogue as cat_

        for target in cat_.COVARIATES[cid]["targets"]:
            try:
                res = known_answer.run_gate(target, cid, cache_dir=CACHE, model=model, limit_days=args.limit_days)
            except Exception as exc:
                res = {"gate": "known_answer", "target": target, "covariate": cid, "pass": False,
                       "error": f"{type(exc).__name__}: {exc}"[:400], "limit_days": args.limit_days}
            items.append(ledger.pending("gate", res, ctx))
            out[f"{target}/{cid}"] = res
    ledger.write_pending(PENDING, items)
    return {"mode": "gate", "gates": out, "ok": all(v["pass"] for v in out.values())}


def _batch_from(args) -> dict:
    raw = Path(args.batch_file).read_text(encoding="utf-8") if args.batch_file else os.environ.get("ENGINE_BATCH_JSON", "")
    if not raw.strip():
        raise SystemExit("no batch: pass --batch-file or set ENGINE_BATCH_JSON")
    return json.loads(raw)


def freeze(args) -> dict:
    from datetime import datetime, timezone

    from engine import arms, vault

    ctx = ledger.run_context("freeze")
    entries = current_ledger()
    batch = _batch_from(args)
    try:
        targets = {c.get("target") for c in batch.get("claims", []) if isinstance(c, dict)}
        accepted = {t: arms.latest_accepted(entries, t) for t in targets if t in ("consumption", "solar")}
        frozen = vault.freeze(batch, entries, datetime.now(timezone.utc),
                              accepted=next(iter(accepted.values())) if len(accepted) == 1 else accepted or None)
    except (vault.VaultError, ValueError) as exc:
        payload = {"submitted_by": args.submitted_by, "batch": batch, "reasons": [str(exc)]}
        ledger.write_pending(PENDING, [ledger.pending("probe_rejected", payload, ctx)])
        return {"mode": "freeze", "refused": str(exc), "ok": False}
    frozen["submitted_by"] = args.submitted_by
    ledger.write_pending(PENDING, [ledger.pending("freeze", frozen, ctx)])
    return {"mode": "freeze", "receipt": frozen["receipt"], "ok": True}


def vault_open(args) -> dict:
    from datetime import datetime, timezone

    from engine import arms, vault, vault_run
    from engine.approvals import owner_approval_from_env

    ctx = ledger.run_context("vault")
    entries = current_ledger()
    model = arms._t0("loader", (), None).load()
    approver = owner_approval_from_env()
    try:
        access, batch = vault.open_forward(entries, args.batch_id, now=datetime.now(timezone.utc),
                                           model_loaded=model is not None, approved_by=approver)
    except vault.VaultError as exc:
        ledger.write_pending(PENDING, [ledger.pending("error", {"batch_id": args.batch_id, "unseal_refused": str(exc)}, ctx)])
        return {"mode": "vault", "refused": str(exc), "ok": False}
    # Recorded before any sealed byte is read: a crash after this still consumes the window.
    ledger.write_pending(PENDING, [ledger.pending("unseal", {"batch_id": batch["batch_id"], "batch_sha256": batch["batch_sha256"],
                                                            "approved_by": approver, "window": batch["window"]}, ctx)])
    try:
        verdict = vault_run.score_batch(batch, cache_dir=ROOT / "vaultcache", model=model, access=access)
    finally:
        vault.close(access)
    items = [ledger.pending("verdict", verdict, ctx)]
    for c in verdict["claims"]:
        if c.get("verdict") == "PASS":
            claim = next(x for x in batch["claims"] if x["id"] == c["claim"])
            items.append(ledger.pending("accepted_finding", {
                "finding_id": f"{batch['batch_id']}-{claim['id']}", "statement": claim["statement"],
                "target": claim["target"], "arm": claim["arm"], "comparator": claim["comparator"], "metric": "mae",
                "confirmed_on": f"forward window {batch['window'][0]}..{batch['window'][1]}",
                "skill": c.get("skill"), "delta": claim["delta"], "p_holm": c.get("p_holm")}, ctx))
    ledger.write_pending(PENDING, items)
    return {"mode": "vault", "verdict": verdict, "ok": True}


DRYRUN_BATCH = {"batch_version": "claims/0", "claims": [
    {"id": "x", "statement": "t0 + holiday beats blend_50 by more than 20% (C1 replayed)", "target": "consumption",
     "arm": {"covariates": [{"id": "holiday", "transform": "raw"}]}, "comparator": "best_simple", "scope": "all",
     "delta": 0.20, "evidence": []},
    {"id": "y", "statement": "adding bridge days beats the accepted arm (any margin)", "target": "consumption",
     "arm": {"covariates": [{"id": "bridge_day", "transform": "raw"}, {"id": "holiday", "transform": "raw"}]},
     "comparator": "accepted", "scope": "all", "delta": 0.0, "evidence": []}]}


def vault_dryrun(args) -> dict:
    """Freeze a fixed batch as if on 2025-01-01 and score it on the consumed 2025 window (no vault access)."""
    import copy
    from datetime import datetime, timezone

    from engine import arms, vault, vault_run

    ctx = ledger.run_context("vault_dryrun")
    entries = current_ledger()
    evidence = [e["seq"] for e in entries if e.get("kind") == "probe_result"
                and e["payload"].get("target") == "consumption"][-1:]
    batch_raw = copy.deepcopy(DRYRUN_BATCH)
    for c in batch_raw["claims"]:
        c["evidence"] = evidence
    batch = vault.freeze(batch_raw, entries, datetime(2025, 1, 1, tzinfo=timezone.utc),
                         accepted=arms.latest_accepted(entries, "consumption"), rehearsal=True)
    model = arms._t0("loader", (), None).load()
    result = vault_run.score_batch(batch, cache_dir=CACHE, model=model, access=None)
    result["status"] = vault_run.NON_CONFIRMATORY
    ledger.write_pending(PENDING, [ledger.pending("note", {"vault_dryrun": result, "batch": batch}, ctx)])
    return {"mode": "vault_dryrun", "result": {k: v for k, v in result.items() if k != "per_day"}, "ok": True}


def seed(args) -> dict:
    from engine import legacy

    entries = current_ledger()
    if entries:
        return {"mode": "seed", "skipped": "the ledger already has a genesis", "head": ledger.head(entries)}
    items = legacy.seed_items(ledger.run_context("seed"))
    ledger.write_pending(PENDING, items)
    return {"mode": "seed", "pending": [i["kind"] for i in items]}


MODES = {"selftest": selftest, "avail": avail, "seed": seed, "probe": probe, "reproduce": reproduce, "gate": gate,
         "freeze": freeze, "vault": vault_open, "vault_dryrun": vault_dryrun}


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="python -m engine", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=sorted(MODES))
    p.add_argument("--spec-file", default=None)
    p.add_argument("--submitted-by", default="owner:manual")
    p.add_argument("--limit-days", type=int, default=None)
    p.add_argument("--batch-file", default=None)
    p.add_argument("--batch-id", default=None)
    args = p.parse_args(argv)
    out = MODES[args.mode](args)
    path = _write(f"{args.mode}.json", out)
    print(path.read_text(encoding="utf-8"))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
