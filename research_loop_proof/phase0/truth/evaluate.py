"""Phase B's evaluate step (PHASE0_SPEC.md section 4): integrity, confirmation, evidence check, behaviours, verdict.

It regenerates the hidden world from the seed, checks the research job's record against it (observed-data hash,
prompts rebuilt byte for byte, experiment results recomputed from the observed data, the canary, the researcher
model's hash, the guard), then scores the final selections on the confirmation days 127-154 with t0 and ridge, runs
the evidence check, computes the behaviours B1-B8 from the notebook and applies the frozen verdict map.

    python -m research_loop_proof.phase0.truth.evaluate --run-id ID --phase-a-dir D --observed D --research D \
        --weights D --out D
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

from research_loop_proof.phase0.lab.executor import IDS, Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.instruments import T0, ridge_forecast
from research_loop_proof.phase0.lab.researcher import (RESEARCHER, call_plan, rebuild_mismatches, sha256_text,
                                                       system_text)
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays
from research_loop_proof.phase0.truth.observe import hidden_world, phase_a_errors
from research_loop_proof.phase0.truth.spec import spec_sha

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
TESTED = ("promising", "accepted", "rejected", "deteriorated", "redundant")
FLOAT_TOL = 1e-4
CAVEATS = ["One world is an existence check, not a rate.",
           "Even an ideal researcher completes the whole chain only when both R's and E's evidence is present in this "
           "world; the evidence check reports whether it was."]


class RidgeInstrument:
    """The matched ridge behind the same interface as ``T0`` (it reads only the window it is given)."""

    rows = sanitised = 0

    def forecast(self, requests):
        self.rows += len(requests)
        out = []
        for ctx, block in requests:
            days = len(ctx) // 24
            y = np.r_[ctx, np.full(24, np.nan)]
            out.append(ridge_forecast(y, [] if block is None else list(block), days + 1, days))
        return out


# ----------------------------------------------------------------- integrity

def _close(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= FLOAT_TOL
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b))
    return a == b


def integrity_issues(w: World, observed_dir: Path, research_dir: Path, recompute_lab,
                     research_job_result: str = "success") -> tuple[list[str], dict]:
    issues, info = [], {}
    if research_job_result != "success":
        issues.append(f"the research job ended with '{research_job_result}'")
    meta = json.loads((observed_dir / "observed.json").read_text())
    regen = arrays_sha256(observed_arrays(w, OBS_LAST))
    shipped = arrays_sha256(load_observed(observed_dir / "observed.npz"))
    info["observed_sha256"] = {"regenerated": regen, "shipped": shipped, "declared": meta["arrays_sha256"]}
    if not regen == shipped == meta["arrays_sha256"]:
        issues.append("observed-data hash mismatch")
    if not (research_dir / "ai.json").is_file():
        return issues + ["no research record (the research job failed: guard, crash or cancellation)"], info
    guard = json.loads((research_dir / "guard.json").read_text()) if (research_dir / "guard.json").is_file() else {}
    info["guard"] = guard
    if guard.get("truth_absent") is not True:
        issues.append("the guard did not confirm that the truth was absent from the research job")
    failure = json.loads((research_dir / "integrity.json").read_text()).get("failure")
    if failure:
        issues.append(f"research job {failure['kind']}: {failure['error']}")
    ai = json.loads((research_dir / "ai.json").read_text())
    calls = ai.get("calls", [])
    if calls and ai.get("system_sha256") != sha256_text(system_text()):
        issues.append("system prompt mismatch")
    mism = rebuild_mismatches(calls)
    if mism:
        issues.append("prompt-rebuild mismatch: " + ", ".join(mism))
    for c in calls:
        for a in c["attempts"]:
            if a.get("served_model_sha256") not in (None, RESEARCHER["model_sha256"]):
                issues.append("researcher-model hash mismatch")
    bad = []
    for c in calls:
        for e in c.get("experiments", []):
            again = recompute_lab.run(e["request"], c["cutoff"], e["id"])
            if any(not _close(again[k], e["result"][k]) for k in again):
                bad.append(e["id"])
    info["experiments_recomputed"] = sum(len(c.get("experiments", [])) for c in calls)
    if bad:
        issues.append("experiment results differ when recomputed from the observed data: " + ", ".join(bad))
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in research_dir.rglob("*") if p.is_file()]
    if any(w.canary in t for t in texts):
        issues.append("canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    return issues, info


# ----------------------------------------------------------------- behaviours

def _results_before(calls: list[dict], k: int) -> list[dict]:
    """Experiments visible to call k (those run in earlier calls), oldest first, with the call that ran them."""
    return [dict(e["result"], call=c["call"]) for c in calls if c["call"] < k for e in c.get("experiments", [])]


def latest_single(results: list[dict], cand: str) -> dict | None:
    hits = [r for r in results if r["covariates"] == [cand]]
    return hits[-1] if hits else None


def behaviours(calls: list[dict], roles: dict, tau: int) -> dict:
    """B1-B8 (PHASE0_SPEC.md section 4). ``roles`` maps role -> observed id."""
    valid = [c for c in calls if c.get("valid")]
    all_exps = [dict(e["result"], call=c["call"]) for c in calls for e in c.get("experiments", [])]
    by_id = {r["id"]: r for r in all_exps}
    status = {c["call"]: {b["candidate"]: b for b in c["response"]["beliefs"]} for c in valid}
    first = next((c for c in calls if c["call"] == 1), None)
    b1 = bool(first and first.get("valid") and any(q.get("because", "").strip()
                                                   for q in first["response"]["experiments"]))
    b2 = bool(all_exps)
    errors = []
    for c in valid:
        seen = _results_before(calls, c["call"])
        for cand, row in status[c["call"]].items():
            last = latest_single(seen, cand)
            if last is None:
                continue
            if row["status"] == "accepted" and last["lo95"] <= 0:
                errors.append({"call": c["call"], "candidate": cand, "status": "accepted", "latest": last["id"]})
            if row["status"] == "rejected" and last["lo95"] > 0:
                errors.append({"call": c["call"], "candidate": cand, "status": "rejected", "latest": last["id"]})
    b4 = False
    for e in all_exps:
        if e["lo95"] > 0:
            continue
        cited_later = any(e["id"] in row["cites"] for c in valid if c["call"] > e["call"]
                          for row in status[c["call"]].values())
        if not cited_later:
            continue
        ok = True
        for cand in e["covariates"]:
            for c in valid:
                if c["call"] > e["call"] and status[c["call"]][cand]["status"] == "accepted":
                    newer = [r for r in _results_before(calls, c["call"])
                             if r["call"] > e["call"] and cand in r["covariates"] and r["lo95"] > 0]
                    ok = ok and bool(newer)
        b4 = b4 or ok
    r_id, e_id = roles["R"], roles["E"]
    b5 = False
    for j in valid:
        if status[j["call"]][r_id]["status"] in ("promising", "accepted"):
            for k in valid:
                row = status[k["call"]][r_id]
                if k["call"] > j["call"] and row["status"] in ("deteriorated", "rejected") and any(
                        cid in by_id and by_id[cid]["scored_days"][1] >= tau for cid in row["cites"]):
                    b5 = True
    b6 = False
    for e in all_exps:
        prev = [r for r in all_exps if r["call"] < e["call"] or (r["call"] == e["call"] and r["id"] < e["id"])]
        weakened = len(e["covariates"]) == 1 and any(
            r["covariates"] == e["covariates"] and r["skill"] > e["skill"] for r in prev)
        if not (e["lo95"] <= 0 or weakened):
            continue
        for c in calls:
            if c["call"] <= e["call"] or c["final"]:
                continue
            tested_before = {x for r in all_exps if r["call"] < c["call"] for x in r["covariates"]}
            rejected = {x for v in valid if v["call"] <= c["call"]  # this call's table is written with its requests
                        for x, row in status[v["call"]].items() if row["status"] == "rejected"}
            for q in c.get("experiments", []):
                if any(x not in tested_before or x in rejected for x in q["request"]["covariates"]):
                    b6 = True
    final = calls[-1] if calls and calls[-1].get("final") else None
    b7 = bool(final and final.get("valid") and status[final["call"]][e_id]["status"] == "accepted"
              and e_id in final["response"]["final_selection"])
    b8 = False
    for cand in IDS:
        rows = [(c["call"], status[c["call"]][cand]) for c in valid]
        for (j, a), (k, b) in zip(rows, rows[1:]):
            if a["status"] in TESTED and b["status"] in TESTED and a["status"] != b["status"] and any(
                    cid in by_id and by_id[cid]["call"] >= j for cid in b["cites"]):
                b8 = True
    return {"B1": b1, "B2": b2, "B3": not errors, "B3_errors": errors, "B4": b4, "B5": b5, "B6": b6, "B7": b7,
            "B8": b8}


# ----------------------------------------------------------------- verdict

def verdict(issues: list[str], phase_a_ok: bool, ai: dict, beh: dict, roles: dict, evidence: dict,
            confirm_ai: dict | None) -> tuple[str, str]:
    if issues:
        return "INTEGRITY FAILURE (no verdict)", "row 0: " + "; ".join(issues)
    if not phase_a_ok:
        return "INSTRUMENT FEASIBILITY FAILED", "row 1"
    calls = ai["calls"]
    sel = ai.get("final_selection")
    all_res = [e["result"] for c in calls for e in c.get("experiments", [])]
    r_id, e_id, n_id = roles["R"], roles["E"], roles["N"]
    reasons = []
    if not ai.get("final_valid"):
        reasons.append("no valid final conclusion")
    sel = sel or []
    if r_id in sel:
        reasons.append("R in the final selection")
    last_n = latest_single(all_res, n_id)
    if n_id in sel and (last_n is None or last_n["lo95"] <= 0):
        reasons.append("N in the final selection with its latest lower bound <= 0 or never tested")
    if len(beh["B3_errors"]) >= 2:
        reasons.append(f"{len(beh['B3_errors'])} interpretation errors")
    e_tested_late = any(e_id in e["request"]["covariates"] for c in calls if c.get("round") in (2, 3)
                        for e in c.get("experiments", []))
    if evidence["E_days_99_126"]["lo95"] > 0 and not e_tested_late and e_id not in sel:
        reasons.append("E was detectable on days 99-126 but never tested in rounds 2-3 and not selected")
    if reasons:
        return "RESEARCHER FEASIBILITY FAILED", "row 2: " + "; ".join(reasons)
    if (e_id in sel and r_id not in sel and n_id not in sel and beh["B3"] and beh["B5"] and beh["B7"] and beh["B8"]
            and confirm_ai is not None and confirm_ai["t0"]["lo95"] > 0):
        return "BASIC LOOP FEASIBLE", "row 3"
    return "AMBIGUOUS", "row 4"


# ----------------------------------------------------------------- run

def _row(res: dict) -> dict:
    keep = ("skill", "lo95", "hi95", "reference_mae", "candidate_mae", "wins", "losses", "ties", "scored_days")
    return {k: res[k] for k in keep}


def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    observed_dir, research_dir = Path(args.observed), Path(args.research)
    phase_a_ok = not phase_a_errors(Path(args.phase_a_dir))
    w = hidden_world(args.run_id)
    roles = {role: w.ids[role] for role in ("R", "E", "D", "N")}
    from research_loop_proof.phase0.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    t0_obs = T0(model)
    obs_lab = Lab(observed_arrays(w, OBS_LAST), t0_obs)  # recompute and evidence check: observed days only
    issues, info = integrity_issues(w, observed_dir, research_dir, obs_lab, args.research_job_result)
    ai = json.loads((research_dir / "ai.json").read_text()) if (research_dir / "ai.json").is_file() else {"calls": []}
    scripted = json.loads((research_dir / "scripted.json").read_text()) \
        if (research_dir / "scripted.json").is_file() else None
    evidence = {"R_days_57_84": _row(obs_lab.run({"covariates": [roles["R"]], "reference": [], "window_days": 28},
                                                 84, "evidence-R")),
                "E_days_99_126": _row(obs_lab.run({"covariates": [roles["E"]], "reference": [], "window_days": 28},
                                                  126, "evidence-E"))}
    full = {"y": w.y, **{w.ids[r]: w.x[r] for r in ("R", "E", "D", "N")}}
    t0_full, ridge = T0(model), RidgeInstrument()
    labs = {"t0": Lab(full, t0_full), "ridge": Lab(full, ridge)}

    def confirm(cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in labs.items()}

    sets = {"{E}": [roles["E"]], "{R}": [roles["R"]], "{D}": [roles["D"]], "{N}": [roles["N"]],
            "{E, D}": [roles["E"], roles["D"]]}
    confirmation = {f"{name} vs {{}}": confirm(s, []) for name, s in sets.items()}
    confirmation["D given E ({E, D} vs {E})"] = confirm([roles["D"]], [roles["E"]])
    confirmation["E given D ({E, D} vs {D})"] = confirm([roles["E"]], [roles["D"]])
    ai_sel = ai.get("final_selection") if ai.get("final_valid") else None
    confirm_ai = confirm(ai_sel, []) if ai_sel else None
    confirm_script = confirm(scripted["final_selection"], []) if scripted and scripted["final_selection"] else None
    beh = behaviours(ai.get("calls", []), roles, w.tau) if ai.get("calls") else {
        k: False for k in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8")} | {"B3_errors": []}
    outcome, rule = verdict(issues, phase_a_ok, ai, beh, roles, evidence, confirm_ai)
    role_of = {v: k for k, v in roles.items()}
    final_status = {}
    if ai.get("final_valid"):
        final_status = {b["candidate"]: b["status"] for b in ai["calls"][-1]["response"]["beliefs"]}
    candidates = [{"id": c, "role": role_of[c], "sign": w.signs[role_of[c]],
                   "causal": {"R": "before the change only", "E": "from the change on", "D": "never (proxy of E)",
                              "N": "never"}[role_of[c]],
                   "confirmation_t0_vs_none": confirmation[f"{{{role_of[c]}}} vs {{}}"]["t0"],
                   "researcher_final_status": final_status.get(c), "researcher_selected": bool(ai_sel and c in ai_sel),
                   "script_selected": bool(scripted and c in scripted["final_selection"])} for c in IDS]
    usage = [a.get("usage") for c in ai.get("calls", []) for a in c["attempts"] if a.get("usage")]
    record = {
        "phase": "B", "verdict": outcome, "rule": rule, "caveats": CAVEATS, "spec_sha": spec_sha(),
        "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"),
        "truth": {"tau": w.tau, "roles": roles, "signs": {roles[r]: w.signs[r] for r in roles}, "form": w.form,
                  "m": w.m, "seed_rule": PB["seed_rule"]},
        "integrity": {"issues": issues, **info}, "load": load_record, "phase_a_ok": phase_a_ok,
        "evidence_check": evidence, "confirmation": confirmation,
        "confirmation_ai_selection": confirm_ai, "confirmation_script_selection": confirm_script,
        "behaviours": beh, "candidates": candidates,
        "ai": {"final_valid": ai.get("final_valid"), "final_selection": ai_sel, "conclusion": ai.get("conclusion"),
               "tokens_used": ai.get("tokens_used"), "api_calls": len(usage),
               "usage_total": {k: sum(u[k] for u in usage) for k in usage[0]} if usage else {}},
        "script": {"final_selection": scripted["final_selection"] if scripted else None},
        "t0_forecasts": {"research_scripted": scripted.get("t0_forecasts") if scripted else None,
                         "research_ai": ai.get("t0_forecasts"),
                         "evaluate": t0_obs.rows + t0_full.rows},
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    (out / "verdict.json").write_text(json.dumps({"phase": "B", "verdict": outcome, "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record, ai, scripted), encoding="utf-8")
    for name in ("ai.json", "scripted.json", "notebook.jsonl", "integrity.json", "guard.json"):
        if (research_dir / name).is_file():
            shutil.copyfile(research_dir / name, out / name)
    shutil.copyfile(observed_dir / "observed.json", out / "observed.json")
    return record


def _pct(r: dict) -> str:
    return f"{r['skill'] * 100:+.1f}% [{r['lo95'] * 100:+.1f}, {r['hi95'] * 100:+.1f}]"


def report(rec: dict, ai: dict, scripted: dict | None) -> str:
    t = rec["truth"]
    lines = [f"# Phase B result: {rec['verdict']}", "", f"Verdict map {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}.", "",
             "## The hidden world (revealed after the research job)", "",
             f"Change at day {t['tau']} (first changed day). Roles: " + ", ".join(
                 f"{r} = {i} (sign {t['signs'][i]:+d})" for r, i in t["roles"].items()) + ".", "",
             "## Integrity", "", f"Issues: {rec['integrity']['issues'] or 'none'}.", "",
             "## Evidence check (t0, 28 days, against no covariate)", "",
             f"- R on days 57-84 (before the change): {_pct(rec['evidence_check']['R_days_57_84'])}",
             f"- E on days 99-126 (after the change): {_pct(rec['evidence_check']['E_days_99_126'])}", "",
             "## Researcher trajectory", ""]
    for c in ai.get("calls", []):
        head = f"### Call {c['call']} ({'final' if c['final'] else 'round ' + str(c['round'])}, days 1-{c['cutoff']})"
        lines.append(head)
        if not c.get("valid"):
            lines += ["", f"No valid response: {'; '.join(c.get('errors', []))}", ""]
            continue
        r = c["response"]
        lines += ["", f"Notes: {r['notes']}", ""]
        for b in r["beliefs"]:
            role = {v: k for k, v in t["roles"].items()}[b["candidate"]]
            lines.append(f"- {b['candidate']} ({role}): **{b['status']}**; cites {', '.join(b['cites']) or 'none'}; "
                         f"{b['reason']}")
        for e in c.get("experiments", []):
            q = e["request"]
            lines.append(f"- {e['id']}: covariates {q['covariates']}, reference {q['reference']}, {q['window_days']} "
                         f"days, expected {q['expect']}: {_pct(e['result'])} on days "
                         f"{e['result']['scored_days'][0]}-{e['result']['scored_days'][1]}")
        if c["final"]:
            lines += [f"- Final selection: {r['final_selection']}", f"- Conclusion: {r['conclusion']}"]
        lines.append("")
    b = rec["behaviours"]
    lines += ["## Behaviours", "", " | ".join(f"{k} {'yes' if b[k] else 'no'}" for k in
                                             ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8")),
              f"Interpretation errors: {len(b['B3_errors'])}.", "",
              "## Candidates: causal role, predictive use, selection", "",
              "| id | role | causal effect | t0 on days 127-154 vs no covariate | researcher final | selected | script |",
              "|---|---|---|---|---|---|---|"]
    for c in rec["candidates"]:
        lines.append(f"| {c['id']} | {c['role']} | {c['causal']} | {_pct(c['confirmation_t0_vs_none'])} | "
                     f"{c['researcher_final_status']} | {c['researcher_selected']} | {c['script_selected']} |")
    lines += ["", "## Confirmation (days 127-154; t0 and ridge)", "", "| comparison | t0 | ridge |", "|---|---|---|"]
    for name, r in rec["confirmation"].items():
        lines.append(f"| {name} | {_pct(r['t0'])} | {_pct(r['ridge'])} |")
    for label, key in (("AI selection", "confirmation_ai_selection"), ("script selection",
                                                                      "confirmation_script_selection")):
        r = rec[key]
        lines.append(f"| {label} vs {{}} | {_pct(r['t0']) if r else 'empty or invalid'} | "
                     f"{_pct(r['ridge']) if r else '-'} |")
    lines += ["", f"Script selection: {rec['script']['final_selection']}; AI selection: {rec['ai']['final_selection']}.",
              "", "## Cost", "", f"API calls {rec['ai']['api_calls']}; tokens {rec['ai']['tokens_used']} "
              f"({rec['ai']['usage_total']}); t0 forecasts {rec['t0_forecasts']}; evaluate {rec['elapsed_s']} s.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--phase-a-dir", "--observed", "--research", "--weights", "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--research-job-result", default="success")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"verdict": rec["verdict"], "rule": rec["rule"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
