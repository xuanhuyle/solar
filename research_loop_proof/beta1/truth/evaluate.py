"""The beta1 evaluate step (NEXT_MILESTONE_PROMPT.md sections 9-14): integrity, confirmation, behaviours, verdict.

It regenerates the hidden world from its seed and checks the research record against it, as Phase B did:
- the observed-data hash;
- every prompt rebuilt byte for byte;
- the experiments recomputed from the observed data with t0-beta;
- the canary;
- the researcher model's hash;
- the guard.

Then it scores the final selections on the confirmation days 127-154 with t0-beta and the matched ridge, runs the
evidence check, computes the behaviours B1-B10 from the notebook, and applies the verdict map (first match wins):

1. RESEARCH INFRASTRUCTURE FAILURE, if any of:
   - an integrity issue (hash, prompt rebuild, recompute, canary, model hash, guard, a failed research job);
   - any of the 4 calls without a valid response after its repair (a refusal, an API error or a malformed
     response).
2. RESEARCHER FEASIBILITY FAILED, if any of:
   - R in the final selection;
   - N in it while its latest single-candidate result has a lower bound <= 0, or N was never tested alone;
   - 2 or more interpretation errors;
   - E detectable in the evidence check (lower bound above 0 on days 99-126), yet never in an experiment's covariates
     in rounds 2-3 and not selected.
3. BASIC AUTONOMOUS LOOP OBSERVED, if all of:
   - E selected, and R and N not selected;
   - B3, B5, B7 and B8 hold;
   - t0-beta with the final selection beats t0-beta without covariates on the confirmation days (lower bound
     above 0).
4. AMBIGUOUS: anything else, including D selected without E.

    python -m research_loop_proof.beta1.truth.evaluate --run-id ID --observed D --research D --weights D --out D
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.lab.researcher import rebuild_mismatches, system_text
from research_loop_proof.beta1.truth.observe import hidden_world
from research_loop_proof.beta1.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import IDS, Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, call_plan, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row, latest_single
from research_loop_proof.phase0.truth.evaluate import behaviours as phase0_behaviours
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
CAVEATS = ["One world is an existence check, not a rate; nothing here establishes superiority over the script.",
           "Even an ideal researcher completes the whole chain only when both R's and E's evidence is present in this "
           "world; the evidence check reports whether it was."]


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


def call_failures(ai: dict) -> list[str]:
    """Calls that did not end with a valid response after their repair (service or format failures)."""
    calls = {c["call"]: c for c in ai.get("calls", [])}
    out = []
    for step in call_plan():
        c = calls.get(step["call"])
        if c is None:
            out.append(f"call {step['call']}: never made")
        elif not c.get("valid"):
            cats = sorted({str(a.get("refusal_category")) for a in c["attempts"] if a.get("stop_reason") == "refusal"})
            out.append(f"call {step['call']}: no valid response after its repair ({'; '.join(c.get('errors', []))}"
                       + (f"; refusal categories {cats}" if cats else "") + ")")
    return out


def behaviours(calls: list[dict], roles: dict, tau: int, final_selection: list | None) -> dict:
    """Phase 0's B1-B8 plus B9 (separation or conditional tests) and B10 (no unsupported noise)."""
    beh = phase0_behaviours(calls, roles, tau)
    exps = [dict(e["request"], call=c["call"], result=e["result"]) for c in calls for e in c.get("experiments", [])]
    b9 = any(e["reference"] for e in exps) or any(
        0 < len(set(e["covariates"])) < len(set(m["covariates"])) and set(e["covariates"]) < set(m["covariates"])
        for m in exps if len(m["covariates"]) >= 2 for e in exps if e["call"] > m["call"])
    n_id = roles["N"]
    last_n = latest_single([e["result"] for e in exps], n_id)
    b10 = n_id not in (final_selection or []) or (last_n is not None and last_n["lo95"] > 0)
    return {**beh, "B9": bool(b9), "B10": bool(b10)}


def verdict(issues: list[str], failures: list[str], ai: dict, beh: dict, roles: dict, evidence: dict,
            confirm_ai: dict | None) -> tuple[str, str]:
    if issues or failures:
        return "RESEARCH INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(issues + failures)
    calls = ai["calls"]
    sel = ai.get("final_selection") or []
    all_res = [e["result"] for c in calls for e in c.get("experiments", [])]
    r_id, e_id, n_id = roles["R"], roles["E"], roles["N"]
    reasons = []
    if r_id in sel:
        reasons.append("R in the final selection")
    last_n = latest_single(all_res, n_id)
    if n_id in sel and (last_n is None or last_n["lo95"] <= 0):
        reasons.append("N in the final selection with its latest lower bound <= 0 or never tested alone")
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
        return "BASIC AUTONOMOUS LOOP OBSERVED", "row 3"
    return "AMBIGUOUS", "row 4"


def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    observed_dir, research_dir = Path(args.observed), Path(args.research)
    w = hidden_world(args.run_id)
    roles = {role: w.ids[role] for role in ("R", "E", "D", "N")}
    from research_loop_proof.beta1.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    t0_obs = t0_beta.BetaT0(model)
    obs_lab = Lab(observed_arrays(w, OBS_LAST), t0_obs)
    issues, info = integrity_issues(w, observed_dir, research_dir, obs_lab, args.research_job_result)
    ai = json.loads((research_dir / "ai.json").read_text()) if (research_dir / "ai.json").is_file() else {"calls": []}
    scripted = json.loads((research_dir / "scripted.json").read_text()) \
        if (research_dir / "scripted.json").is_file() else None
    failures = call_failures(ai)
    evidence = {"R_days_57_84": _row(obs_lab.run({"covariates": [roles["R"]], "reference": [], "window_days": 28},
                                                 84, "evidence-R")),
                "E_days_99_126": _row(obs_lab.run({"covariates": [roles["E"]], "reference": [], "window_days": 28},
                                                  126, "evidence-E"))}
    full = {"y": w.y, **{w.ids[r]: w.x[r] for r in ("R", "E", "D", "N")}}
    t0_full, ridge = t0_beta.BetaT0(model), RidgeInstrument()
    labs = {"t0": Lab(full, t0_full), "ridge": Lab(full, ridge)}

    def confirm(cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in labs.items()}

    e = roles["E"]
    confirmation = {f"{{{r}}} vs {{}}": confirm([roles[r]], []) for r in ("E", "R", "D", "N")}
    confirmation["{E, D} vs {}"] = confirm([e, roles["D"]], [])
    for r in ("R", "D", "N"):
        confirmation[f"{r} given E ({{E, {r}}} vs {{E}})"] = confirm([roles[r]], [e])
    confirmation["E given D ({E, D} vs {D})"] = confirm([e], [roles["D"]])
    ai_sel = ai.get("final_selection") if ai.get("final_valid") else None
    confirm_ai = confirm(ai_sel, []) if ai_sel else None
    confirm_script = confirm(scripted["final_selection"], []) if scripted and scripted["final_selection"] else None
    beh = behaviours(ai.get("calls", []), roles, w.tau, ai_sel) if ai.get("calls") else {
        k: False for k in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10")} | {"B3_errors": []}
    outcome, rule = verdict(issues, failures, ai, beh, roles, evidence, confirm_ai)
    role_of = {v: k for k, v in roles.items()}
    final_status = {}
    if ai.get("final_valid"):
        final_status = {b["candidate"]: b["status"] for b in ai["calls"][-1]["response"]["beliefs"]}
    candidates = []
    for c in IDS:
        r = role_of[c]
        given_e = confirmation["E given D ({E, D} vs {D})"] if r == "E" else confirmation[f"{r} given E ({{E, {r}}} vs {{E}})"]
        candidates.append({
            "id": c, "role": r, "sign": w.signs[r],
            "causal": {"R": "before the change only", "E": "from the change on", "D": "never (proxy of E)",
                       "N": "never"}[r],
            "standalone": confirmation[f"{{{r}}} vs {{}}"], "incremental": given_e,
            "incremental_label": "E given D" if r == "E" else f"{r} given E",
            "researcher_final_status": final_status.get(c), "researcher_selected": bool(ai_sel and c in ai_sel),
            "script_selected": bool(scripted and c in scripted["final_selection"])})
    attempts = [a for c in ai.get("calls", []) for a in c["attempts"]]
    usage = [a["usage"] for a in attempts if a.get("usage")]
    record = {
        "phase": "beta1-run", "verdict": outcome, "rule": rule, "caveats": CAVEATS, "spec_sha": spec_sha(),
        "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"), "instrument": load_record,
        "truth": {"tau": w.tau, "roles": roles, "signs": {roles[r]: w.signs[r] for r in roles}, "form": w.form,
                  "m": w.m},
        "integrity": {"issues": issues, **info}, "call_failures": failures,
        "evidence_check": evidence, "confirmation": confirmation,
        "confirmation_ai_selection": confirm_ai, "confirmation_script_selection": confirm_script,
        "behaviours": beh, "candidates": candidates,
        "ai": {"final_valid": ai.get("final_valid"), "final_selection": ai_sel, "conclusion": ai.get("conclusion"),
               "tokens_used": ai.get("tokens_used"), "api_attempts": len(attempts),
               "refusals": sum(1 for a in attempts if a.get("stop_reason") == "refusal"),
               "refusal_categories": sorted({str(a.get("refusal_category")) for a in attempts
                                             if a.get("stop_reason") == "refusal"}),
               "repairs": sum(1 for a in attempts if a.get("attempt") == 2),
               "usage_total": {k: sum(u[k] for u in usage) for k in usage[0]} if usage else {}},
        "script": {"final_selection": scripted["final_selection"] if scripted else None},
        "t0_beta_forecasts": {"research_scripted": scripted.get("t0_forecasts") if scripted else None,
                              "research_ai": ai.get("t0_forecasts"), "evaluate": t0_obs.rows + t0_full.rows},
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    (out / "verdict.json").write_text(json.dumps({"phase": "beta1-run", "verdict": outcome, "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record, ai, scripted), encoding="utf-8")
    for name in ("ai.json", "scripted.json", "notebook.jsonl", "integrity.json", "guard.json"):
        if (research_dir / name).is_file():
            shutil.copyfile(research_dir / name, out / name)
    shutil.copyfile(observed_dir / "observed.json", out / "observed.json")
    return record


def _pct(r: dict | None) -> str:
    return "-" if not r else f"{r['skill'] * 100:+.1f}% [{r['lo95'] * 100:+.1f}, {r['hi95'] * 100:+.1f}]"


def report(rec: dict, ai: dict, scripted: dict | None) -> str:
    t = rec["truth"]
    role_of = {v: k for k, v in t["roles"].items()}
    lines = [f"# beta1 hidden-world result: {rec['verdict']}", "", f"Verdict map {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"beta1_spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; instrument "
             f"{rec['instrument'].get('repo')} @ {rec['instrument'].get('served_revision')} (tfc-t0 "
             f"{rec['instrument'].get('tfc_t0')}).", "",
             "## Research trajectory (round by round)", ""]
    for c in ai.get("calls", []):
        lines.append(f"### Call {c['call']} ({'final' if c['final'] else 'round ' + str(c['round'])}, days 1-{c['cutoff']})")
        lines.append("")
        lines.append("API attempts: " + "; ".join(
            f"#{a.get('attempt')} {a.get('stop_reason')}" + (f" ({a.get('refusal_category')})" if a.get("stop_reason") == "refusal" else "")
            + f", {a.get('elapsed_s')} s" for a in c["attempts"]))
        if not c.get("valid"):
            lines += ["", f"No valid response: {'; '.join(c.get('errors', []))}", ""]
            continue
        r = c["response"]
        lines += ["", f"Notes: {r['notes']}", "", "Beliefs:"]
        for b in r["beliefs"]:
            lines.append(f"- {b['candidate']} ({role_of[b['candidate']]}): **{b['status']}**; cites "
                         f"{', '.join(b['cites']) or 'none'}; {b['reason']}")
        if c.get("experiments"):
            lines.append("Experiments:")
        for e in c.get("experiments", []):
            q = e["request"]
            lines.append(f"- {e['id']}: covariates {q['covariates']}, reference {q['reference']}, {q['window_days']} "
                         f"days, expected {q['expect']} ({q['because']}) -> {_pct(e['result'])} on days "
                         f"{e['result']['scored_days'][0]}-{e['result']['scored_days'][1]}")
        if c["final"]:
            lines += [f"- Final selection: {r['final_selection']}", f"- Conclusion: {r['conclusion']}"]
        lines.append("")
    lines += ["## Revealed truth", "", f"First changed day {t['tau']}. " + ", ".join(
        f"{r} = {i} (sign {t['signs'][i]:+d})" for r, i in t["roles"].items()) + ".", "",
              "## Integrity and infrastructure", "", f"Integrity issues: {rec['integrity']['issues'] or 'none'}. "
              f"Call failures: {rec['call_failures'] or 'none'}.", "",
              "## Evidence check (t0-beta, 28 days, against no covariate)", "",
              f"- R on days 57-84 (before the change): {_pct(rec['evidence_check']['R_days_57_84'])}",
              f"- E on days 99-126 (after the change): {_pct(rec['evidence_check']['E_days_99_126'])}", "",
              "## Behaviours", ""]
    b = rec["behaviours"]
    names = {"B1": "initial hypothesis", "B2": "test", "B3": "correct interpretation", "B4": "negative result kept",
             "B5": "weakening noticed", "B6": "another candidate investigated", "B7": "new covariate identified",
             "B8": "beliefs revised", "B9": "separation or conditional test", "B10": "no unsupported noise"}
    lines += [f"- {k} {names[k]}: {'yes' if b[k] else 'no'}" for k in names]
    lines += [f"- interpretation errors: {len(b['B3_errors'])}", "",
              "## Candidates: planted role, predictive use, researcher", "",
              "| id | role | causal effect | t0-beta alone (127-154) | incremental | researcher final | selected | script |",
              "|---|---|---|---|---|---|---|---|"]
    for c in rec["candidates"]:
        lines.append(f"| {c['id']} | {c['role']} | {c['causal']} | {_pct(c['standalone']['t0'])} | "
                     f"{c['incremental_label']}: {_pct(c['incremental']['t0'])} | {c['researcher_final_status']} | "
                     f"{c['researcher_selected']} | {c['script_selected']} |")
    lines += ["", "## Confirmation (days 127-154; t0-beta and ridge)", "", "| comparison | t0-beta | ridge |",
              "|---|---|---|"]
    for name, r in rec["confirmation"].items():
        lines.append(f"| {name} | {_pct(r['t0'])} | {_pct(r['ridge'])} |")
    for label, key in (("AI selection", "confirmation_ai_selection"),
                       ("script selection", "confirmation_script_selection")):
        r = rec[key]
        lines.append(f"| {label} vs {{}} | {_pct(r['t0']) if r else 'empty or invalid'} | "
                     f"{_pct(r['ridge']) if r else '-'} |")
    lines += ["", f"AI selection: {rec['ai']['final_selection']}; script selection: {rec['script']['final_selection']}.",
              ""]
    if scripted:
        lines += ["## Script", ""] + [
            f"- {x['id']} (round {x['round']}): {x['request']['covariates']} vs none, {x['request']['window_days']} days -> "
            f"{_pct(x['result'])} on days {x['result']['scored_days'][0]}-{x['result']['scored_days'][1]}"
            for x in scripted["experiments"]] + [""]
    a = rec["ai"]
    lines += ["## Cost", "", f"API attempts {a['api_attempts']} (refusals {a['refusals']} {a['refusal_categories']}, "
              f"repairs {a['repairs']}); tokens {a['tokens_used']} ({a['usage_total']}); t0-beta forecasts "
              f"{rec['t0_beta_forecasts']}; evaluate {rec['elapsed_s']} s.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--observed", "--research", "--weights", "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--research-job-result", default="success")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"verdict": rec["verdict"], "rule": rec["rule"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
