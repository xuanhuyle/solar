"""The policy1 evaluate step (NEXT_POLICY_ARCHITECTURE_PROMPT.md sections 10-13): both trajectories on the one world.

Integrity per condition, as learn1 did: the observed-data hash; the system text is exactly the frozen one (L: learn1's
lesson condition; S: the same plus the research-state section and schema); every user and repair prompt rebuilt byte for
byte from that condition's own record (L with Phase 0's renderer, S with its own); every experiment recomputed with
t0-beta; the canary, the model hash, the guard and the research jobs' results.

Then it reveals the world, runs the evidence check, scores both final selections on days 127-154 with t0-beta and the
matched ridge, tabulates each trajectory round by round (S's structured state verbatim) and reads the outcome (first
match wins):

1. INFRASTRUCTURE FAILURE: an integrity issue, or a call of either condition without a valid response after its repair.
2. ARCHITECTURE SIGNAL OBSERVED, if either:
   (a) S found the emerging driver (E selected, R and N not) and L did not;
   (b) both found it, every member of S's selection is supported by its own test and L's selection is not.
   "Supported": the latest experiment in which the candidate was the only covariate (with or without a reference) had
   a lower bound above 0. The link to the structured state holds by construction (the conditions differ only by it, and
   every S experiment names the uncertainty it targets); the report quotes the fields.
3. BOTH SUCCEED: both complete the essential loop: found, supported, and the selection beats no covariate on the
   confirmation days (t0-beta lower bound above 0).
4. BOTH FAIL: neither completes the essential loop.
5. NO ARCHITECTURE SIGNAL: anything else.

    python -m research_loop_proof.policy1.truth.evaluate --run-id ID --observed D --research D --weights D --out D
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
from research_loop_proof.learn1.lab.researcher import LESSON_FILE, frozen_lesson
from research_loop_proof.learn1.truth import evaluate as l1
from research_loop_proof.phase0.lab.executor import IDS, Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays
from research_loop_proof.policy1.lab.researcher import CONDITIONS, S_KEYS, rebuild_for, system_text
from research_loop_proof.policy1.truth.observe import hidden_world
from research_loop_proof.policy1.truth.spec import spec_sha

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
CAVEATS = ["One world and one trajectory per condition: an existence test, not a rate. The researcher is stochastic, "
           "so a difference between L and S can arise by chance as well as from the architecture.",
           "The outcome reads research behaviour first; forecast accuracy alone is not an architecture signal."]


# ----------------------------------------------------------------- integrity

def integrity_issues(w: World, research_dir: Path, condition: str, recompute_lab,
                     job_result: str = "success") -> tuple[list[str], dict]:
    p = f"{condition}: "
    issues, info = [], {}
    if job_result != "success":
        issues.append(p + f"the research job ended with '{job_result}'")
    if not (research_dir / "ai.json").is_file():
        return issues + [p + "no research record (the research job failed: guard, crash or cancellation)"], info
    guard = json.loads((research_dir / "guard.json").read_text()) if (research_dir / "guard.json").is_file() else {}
    info["guard"] = guard
    if guard.get("truth_absent") is not True:
        issues.append(p + "the guard did not confirm that the truth was absent from the research job")
    failure = json.loads((research_dir / "integrity.json").read_text()).get("failure") \
        if (research_dir / "integrity.json").is_file() else {"kind": "missing", "error": "no integrity.json"}
    if failure:
        issues.append(p + f"research job {failure['kind']}: {failure['error']}")
    ai = json.loads((research_dir / "ai.json").read_text())
    calls = ai.get("calls", [])
    if ai.get("condition") != condition:
        issues.append(p + f"the record is condition {ai.get('condition')!r}")
    if any(c.get("replayed") for c in calls):
        issues.append(p + "the record contains replayed calls")
    expected = system_text(condition)
    info["system_sha256"] = ai.get("system_sha256")
    if calls and (ai.get("system_sha256") != sha256_text(expected) or ai.get("system_text") != expected):
        issues.append(p + "the system text is not the frozen text of this condition")
    try:
        mism = rebuild_for(condition)(calls)
    except (KeyError, TypeError) as exc:  # a record that is not of this condition's format
        mism = [f"the record cannot be rendered as condition {condition} ({type(exc).__name__}: {exc})"]
    if mism:
        issues.append(p + "prompt-rebuild mismatch: " + ", ".join(mism))
    if any(a.get("served_model_sha256") not in (None, RESEARCHER["model_sha256"]) for c in calls for a in c["attempts"]):
        issues.append(p + "researcher-model hash mismatch")
    bad = []
    for c in calls:
        for e in c.get("experiments", []):
            again = recompute_lab.run(e["request"], c["cutoff"], e["id"])
            if any(not _close(again[k], e["result"][k]) for k in again):
                bad.append(e["id"])
    info["experiments_recomputed"] = sum(len(c.get("experiments", [])) for c in calls)
    if bad:
        issues.append(p + "experiment results differ when recomputed from the observed data: " + ", ".join(bad))
    texts = [f.read_text(encoding="utf-8", errors="replace") for f in research_dir.rglob("*") if f.is_file()]
    if any(w.canary in t for t in texts):
        issues.append(p + "canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    return issues, info


# ----------------------------------------------------------------- behaviour indicators

def _results(calls: list[dict]) -> list[dict]:
    return [dict(e["result"], call=c["call"], round=c.get("round"), request=e["request"])
            for c in calls for e in c.get("experiments", [])]


def support(selection: list | None, calls: list[dict]) -> dict:
    """For each selected candidate, its latest experiment as the only covariate (with or without a reference)."""
    out = {}
    for x in selection or []:
        hits = [r for r in _results(calls) if r["covariates"] == [x]]
        last = hits[-1] if hits else None
        out[x] = {"latest_sole_test": last["id"] if last else None, "lo95": last["lo95"] if last else None,
                  "reference": last["reference"] if last else None, "supported": bool(last and last["lo95"] > 0)}
    return out


def reconfirmations(calls: list[dict], tau: int) -> list[str]:
    """Experiments testing a candidate alone after an earlier call already had a post-change sole test of it."""
    out = []
    for c in calls:
        earlier = [r for r in _results(calls) if r["call"] < c["call"] and len(r["covariates"]) == 1
                   and r["scored_days"][1] >= tau]
        for e in c.get("experiments", []):
            cov = e["result"]["covariates"]
            if len(cov) == 1 and any(r["covariates"] == cov for r in earlier):
                out.append(e["id"])
    return out


def experiment_type(req: dict) -> str:
    n = len(req["covariates"])
    return ("single" if n == 1 else "group") + ("-conditional" if req["reference"] else "")


def last_experiment(calls: list[dict], selection: list | None) -> dict | None:
    res = _results(calls)
    if not res:
        return None
    last = res[-1]
    return {"id": last["id"], "round": last["round"], "covariates": last["covariates"], "reference": last["reference"],
            "type": experiment_type(last["request"]), "lo95": last["lo95"],
            "tests_a_selected_member_alone": len(last["covariates"]) == 1 and last["covariates"][0] in (selection or [])}


def structured_state(calls: list[dict]) -> list[dict]:
    """S's research state per call, verbatim (empty for L)."""
    out = []
    for c in calls:
        r = c.get("response") or {}
        if c.get("valid") and "regime_assessment" in r:
            out.append({"call": c["call"], "round": c.get("round"),
                        **{k: r[k] for k in S_KEYS if k not in ("notes", "final_selection", "conclusion")}})
    return out


def attribution_after_groups(calls: list[dict]) -> list[dict]:
    """For S: after each positive multi-covariate result, the next table's attribution entries for its members."""
    tables = {c["call"]: {b["candidate"]: b for b in c["response"]["beliefs"]} for c in calls
              if c.get("valid") and c.get("response")}
    out = []
    for r in _results(calls):
        if len(r["covariates"]) >= 2 and r["lo95"] > 0:
            later = [k for k in tables if k > r["call"]]
            if later:
                t = tables[min(later)]
                out.append({"experiment": r["id"], "members": r["covariates"], "next_call": min(later),
                            "attribution": {x: t[x].get("attribution") for x in r["covariates"]},
                            "evidence_type": {x: t[x].get("evidence_type") for x in r["covariates"]}})
    return out


def analyse(condition: str, ai: dict, roles: dict, tau: int, evidence: dict, issues: list[str],
            confirm_sel: dict | None) -> dict:
    a = l1.analyse(condition, ai, roles, tau, evidence, issues, confirm_sel)
    calls = ai.get("calls", [])
    sel = a["final_selection"]
    sup = support(sel, calls)
    supported = bool(sel) and all(v["supported"] for v in sup.values())
    states = structured_state(calls)
    final_ok = bool(calls) and calls[-1].get("final") and calls[-1].get("valid")
    final_state = states[-1] if final_ok and states and states[-1]["call"] == calls[-1]["call"] else None
    a.update(beta1_row3=a.pop("essential_loop"), support=sup, supported=supported,
             unsupported_members=[x for x, v in sup.items() if not v["supported"]],
             essential_loop=bool(a["found"] and supported and confirm_sel and confirm_sel["t0"]["lo95"] > 0),
             reconfirmations=reconfirmations(calls, tau), last_experiment=last_experiment(calls, sel),
             structured_state=states, attribution_after_groups=attribution_after_groups(calls),
             final_uncertainties=final_state["decision_uncertainties"] if final_state else None)
    return a


def outcome(issues: list[str], l: dict, s: dict) -> tuple[str, str]:
    failures = [f"L {x}" for x in l["call_failures"]] + [f"S {x}" for x in s["call_failures"]]
    if issues or failures:
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(issues + failures)
    improved = []
    if s["found"] and not l["found"]:
        improved.append("(a) S found the emerging driver and L did not")
    if s["found"] and l["found"] and s["supported"] and not l["supported"]:
        improved.append("(b) both found it; every member of S's selection has its own positive test and L's does not")
    if improved:
        return "ARCHITECTURE SIGNAL OBSERVED", "row 2: " + "; ".join(improved)
    if l["essential_loop"] and s["essential_loop"]:
        return "BOTH SUCCEED", "row 3: both completed the essential loop"
    if not l["essential_loop"] and not s["essential_loop"]:
        return "BOTH FAIL", "row 4: neither completed the essential loop"
    return "NO ARCHITECTURE SIGNAL", "row 5"


# ----------------------------------------------------------------- run

def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    observed_dir, research = Path(args.observed), Path(args.research)
    w = hidden_world(args.run_id)
    roles = {role: w.ids[role] for role in ("R", "E", "D", "N")}
    from research_loop_proof.beta1.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    t0_obs = t0_beta.BetaT0(model)
    obs_lab = Lab(observed_arrays(w, OBS_LAST), t0_obs)
    issues, info = [], {}
    meta = json.loads((observed_dir / "observed.json").read_text())
    regen = arrays_sha256(observed_arrays(w, OBS_LAST))
    shipped = arrays_sha256(load_observed(observed_dir / "observed.npz"))
    info["observed_sha256"] = {"regenerated": regen, "shipped": shipped, "declared": meta["arrays_sha256"]}
    if not regen == shipped == meta["arrays_sha256"]:
        issues.append("observed-data hash mismatch")
    job_results = {"L": args.research_l_result, "S": args.research_s_result}
    ais = {}
    for c in CONDITIONS:
        i, inf_c = integrity_issues(w, research / c, c, obs_lab, job_results[c])
        issues += i
        info[c] = inf_c
        p = research / c / "ai.json"
        ais[c] = json.loads(p.read_text()) if p.is_file() else {"calls": []}
        ais[c].setdefault("calls", [])
    lesson = frozen_lesson()
    info["lesson_sha256"] = sha256_text(lesson)
    info["system_sha256_expected"] = {c: sha256_text(system_text(c)) for c in CONDITIONS}
    e = roles["E"]
    evidence = {
        "R_days_57_84": _row(obs_lab.run({"covariates": [roles["R"]], "reference": [], "window_days": 28}, 84,
                                         "evidence-R")),
        "E_days_99_112": _row(obs_lab.run({"covariates": [e], "reference": [], "window_days": 14}, 112,
                                          "evidence-E-round-2")),
        "E_days_99_126": _row(obs_lab.run({"covariates": [e], "reference": [], "window_days": 28}, 126,
                                          "evidence-E")),
    }
    full = {"y": w.y, **{w.ids[r]: w.x[r] for r in ("R", "E", "D", "N")}}
    t0_full, ridge = t0_beta.BetaT0(model), RidgeInstrument()
    labs = {"t0": Lab(full, t0_full), "ridge": Lab(full, ridge)}

    def confirm(cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in labs.items()}

    confirmation = {f"{{{r}}} vs {{}}": confirm([roles[r]], []) for r in ("E", "R", "D", "N")}
    confirmation["{E, D} vs {}"] = confirm([e, roles["D"]], [])
    for r in ("R", "D", "N"):
        confirmation[f"{r} given E ({{E, {r}}} vs {{E}})"] = confirm([roles[r]], [e])
    confirmation["E given D ({E, D} vs {D})"] = confirm([e], [roles["D"]])
    selections = {}
    for c in CONDITIONS:
        sel = ais[c].get("final_selection") if ais[c].get("final_valid") else None
        selections[c] = confirm(sel, []) if sel else None
    shared = [x for x in issues if not x.startswith(("L: ", "S: "))]
    cond_issues = {c: shared + [x for x in issues if x.startswith(f"{c}: ")] for c in CONDITIONS}
    per = {c: analyse(c, ais[c], roles, w.tau, evidence, cond_issues[c], selections[c]) for c in CONDITIONS}
    label, rule = outcome(issues, per["L"], per["S"])
    role_of = {v: k for k, v in roles.items()}
    final_status = {c: ({b["candidate"]: b["status"] for b in ais[c]["calls"][-1]["response"]["beliefs"]}
                        if ais[c].get("final_valid") else {}) for c in CONDITIONS}
    candidates = []
    for cid in IDS:
        r = role_of[cid]
        incr = confirmation["E given D ({E, D} vs {D})"] if r == "E" else confirmation[f"{r} given E ({{E, {r}}} vs {{E}})"]
        candidates.append({
            "id": cid, "role": r, "sign": w.signs[r],
            "causal": {"R": "before the change only", "E": "from the change on", "D": "never (proxy of E)",
                       "N": "never"}[r],
            "standalone": confirmation[f"{{{r}}} vs {{}}"], "incremental": incr,
            "incremental_label": "E given D" if r == "E" else f"{r} given E",
            **{f"{c}_final_status": final_status[c].get(cid) for c in CONDITIONS},
            **{f"{c}_selected": cid in (per[c]["final_selection"] or []) for c in CONDITIONS}})
    record = {
        "phase": "policy1-run", "outcome": label, "rule": rule, "caveats": CAVEATS, "spec_sha": spec_sha(),
        "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"), "instrument": load_record,
        "lesson": {"text": lesson, "sha256": sha256_text(lesson)},
        "truth": {"tau": w.tau, "roles": roles, "signs": {roles[r]: w.signs[r] for r in roles}, "form": w.form,
                  "m": w.m},
        "integrity": {"issues": issues, **info}, "evidence_check": evidence, "confirmation": confirmation,
        "confirmation_selections": selections, "conditions": per, "candidates": candidates,
        "t0_beta_forecasts": {"research_L": ais["L"].get("t0_forecasts"), "research_S": ais["S"].get("t0_forecasts"),
                              "evaluate": t0_obs.rows + t0_full.rows},
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": "policy1-run", "outcome": label, "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record, ais["S"]["calls"]), encoding="utf-8")
    for c in CONDITIONS:
        (out / c).mkdir(exist_ok=True)
        for name in ("ai.json", "notebook.jsonl", "integrity.json", "guard.json"):
            if (research / c / name).is_file():
                shutil.copyfile(research / c / name, out / c / name)
    shutil.copyfile(observed_dir / "observed.json", out / "observed.json")
    shutil.copyfile(LESSON_FILE, out / "lesson.json")
    return record


# ----------------------------------------------------------------- report

_pct, _yn = l1._pct, l1._yn


def _s_trajectory(ai_calls: list[dict], a: dict, role_of: dict, tau: int) -> list[str]:
    lines = []
    rows = {r["call"]: r for r in a["rounds"]}
    for c in ai_calls:
        row = rows[c["call"]]
        title = "final call" if c["final"] else f"round {c['round']}"
        lines += [f"#### Call {c['call']} ({title}, days 1-{c['cutoff']}); budget left after it: {row['budget_left']}", ""]
        if not c.get("valid"):
            lines += [f"No valid response: {'; '.join(c.get('errors', []))}", ""]
            continue
        r = c["response"]
        if "regime_assessment" not in r:
            lines += ["(this call has no structured research state)", ""]
            continue
        ra = r["regime_assessment"]
        lines += [f"Notes (written with the requests): {r['notes']}",
                  f"Regime assessment: **{ra['status']}** (cites {', '.join(ra['cites']) or 'none'}): {ra['justification']}",
                  "Decision uncertainties: " + ("none" if not r["decision_uncertainties"] else " | ".join(
                      f"{u['id']}: {u['uncertainty']} (matters: {u['why_it_matters']})" for u in r["decision_uncertainties"])),
                  f"Budget needs: {r['budget_needs']}", "Candidates (entering the round):"]
        for b in r["beliefs"]:
            lines.append(f"- {b['candidate']} ({role_of[b['candidate']]}): {b['status']}; freshness {b['freshness']}; "
                         f"evidence {b['evidence_type']}; last scored day {b['last_scored_day'] or '-'}; attribution: "
                         f"{b['attribution'] or 'none'}")
        for x in c.get("experiments", []):
            q, res = x["request"], x["result"]
            lines.append(f"- {x['id']}: covariates {q['covariates']}, reference {q['reference']}, {q['window_days']} days, "
                         f"targets {q['targets_uncertainty']} -> {_pct(res)} on days {res['scored_days'][0]}-"
                         f"{res['scored_days'][1]} ({l1.relative_to_change(res['scored_days'], tau)} the change). "
                         f"Because: {q['because']} Follow-up: {q['possible_followup']} Budget: {q['budget_rationale']}")
        if row.get("updates_after") is not None:
            lines.append("Belief updates after these results: " + (", ".join(
                f"{k} ({role_of[k]}) {o} -> {n}" for k, (o, n) in row["updates_after"].items()) or "none") + ".")
        if c["final"]:
            lines += [f"Final selection: {r['final_selection']}", f"Conclusion: {r['conclusion']}"]
        lines.append("")
    return lines


def report(rec: dict, s_calls: list[dict]) -> str:
    t = rec["truth"]
    role_of = {v: k for k, v in t["roles"].items()}
    L, S = rec["conditions"]["L"], rec["conditions"]["S"]
    lines = [f"# policy1 paired hidden-world result: {rec['outcome']}", "", f"Outcome {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"policy1_spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; instrument "
             f"{rec['instrument'].get('repo')} @ {rec['instrument'].get('served_revision')} (tfc-t0 "
             f"{rec['instrument'].get('tfc_t0')}).", "",
             "## Integrity", "", f"Issues: {rec['integrity']['issues'] or 'none'}. Call failures: L "
             f"{L['call_failures'] or 'none'}; S {S['call_failures'] or 'none'}.", "",
             "## Revealed world", "", f"First changed day {t['tau']}. " + ", ".join(
                 f"{r} = {i} (sign {t['signs'][i]:+d})" for r, i in t["roles"].items()) + ".", "",
             "Evidence check (t0-beta, against no covariate):", "",
             f"- R on days 57-84 (before the change): {_pct(rec['evidence_check']['R_days_57_84'])}",
             f"- E on days 99-112 (available in round 2): {_pct(rec['evidence_check']['E_days_99_112'])}",
             f"- E on days 99-126 (available in round 3): {_pct(rec['evidence_check']['E_days_99_126'])}", "",
             "## Side by side", "", "| | L (lesson only) | S (structured state) |", "|---|---|---|"]

    def reo(a):
        return "; ".join(f"{r['candidate']} ({role_of[r['candidate']]}) in {r['experiment']}" for r in a["reopened"]) or "none"

    def lastx(a):
        x = a["last_experiment"]
        return "-" if not x else (f"{x['id']} {x['type']} {x['covariates']} ref {x['reference']} (lo {x['lo95'] * 100:+.1f}%)"
                                  f"; tests a selected member alone: {_yn(x['tests_a_selected_member_alone'])}")

    rows = [("final selection", lambda a: f"{a['final_selection']}"),
            ("found the emerging driver (E selected, R and N not)", lambda a: _yn(a["found"])),
            ("every selected member supported by its own test", lambda a: _yn(a["supported"])
             + (f" (unsupported: {a['unsupported_members']})" if a["unsupported_members"] else "")),
            ("essential loop (found, supported, confirmation lower bound > 0)", lambda a: _yn(a["essential_loop"])),
            ("first round with positive evidence for E", lambda a: a["first_e_round"] or "never"),
            ("re-opened stale negatives", reo),
            ("retired driver excluded", lambda a: _yn(a["retired_removed"])),
            ("unsupported noise avoided (B10)", lambda a: _yn(a["noise_avoided"])),
            ("reconfirmations (sole re-tests after a post-change sole test)",
             lambda a: ", ".join(a["reconfirmations"]) or "none"),
            ("last experiment", lastx),
            ("decision uncertainties left at the end (S's own list)",
             lambda a: "-" if a["final_uncertainties"] is None else len(a["final_uncertainties"])),
            ("beta1 reading", lambda a: a["beta1_reading"]["verdict"]),
            ("tokens", lambda a: a["cost"]["tokens_used"])]
    lines += [f"| {name} | {fn(L)} | {fn(S)} |" for name, fn in rows]
    lines.append("")
    if S["attribution_after_groups"]:
        lines += ["S's attribution entries after positive group results:", ""] + [
            f"- after {g['experiment']} {g['members']} (call {g['next_call']} table): " + "; ".join(
                f"{x}: {g['evidence_type'][x]}, {g['attribution'][x] or 'none'}" for x in g["members"])
            for g in S["attribution_after_groups"]] + [""]
    if S["final_uncertainties"]:
        lines += ["S's unresolved uncertainties at the end:", ""] + [
            f"- {u['id']}: {u['uncertainty']} (matters: {u['why_it_matters']})" for u in S["final_uncertainties"]] + [""]
    lines += ["## Trajectory L (lesson only)", ""] + l1._trajectory(L, role_of)
    lines += ["## Trajectory S (structured research state)", ""]
    lines += _s_trajectory(s_calls, S, role_of, t["tau"])
    lines += ["## Candidates", "",
              "| id | role | causal effect | t0-beta alone (127-154) | incremental | L final | L selected | S final | "
              "S selected |", "|---|---|---|---|---|---|---|---|---|"]
    for c in rec["candidates"]:
        lines.append(f"| {c['id']} | {c['role']} | {c['causal']} | {_pct(c['standalone']['t0'])} | "
                     f"{c['incremental_label']}: {_pct(c['incremental']['t0'])} | {c['L_final_status']} | "
                     f"{c['L_selected']} | {c['S_final_status']} | {c['S_selected']} |")
    lines += ["", "## Confirmation (days 127-154; t0-beta and ridge)", "", "| comparison | t0-beta | ridge |",
              "|---|---|---|"]
    for name, r in rec["confirmation"].items():
        lines.append(f"| {name} | {_pct(r['t0'])} | {_pct(r['ridge'])} |")
    for c in CONDITIONS:
        r = rec["confirmation_selections"][c]
        lines.append(f"| {c}'s selection {rec['conditions'][c]['final_selection']} vs {{}} | "
                     f"{_pct(r['t0']) if r else 'empty or invalid'} | {_pct(r['ridge']) if r else '-'} |")
    lines += ["", "## Cost", ""]
    for c in CONDITIONS:
        k = rec["conditions"][c]["cost"]
        lines.append(f"- {c}: API attempts {k['api_attempts']} (refusals {k['refusals']} {k['refusal_categories']}, "
                     f"repairs {k['repairs']}); tokens {k['tokens_used']} ({k['usage_total']}); t0-beta forecasts "
                     f"{k['t0_forecasts']}.")
    lines += [f"- evaluate: t0-beta forecasts {rec['t0_beta_forecasts']['evaluate']}; {rec['elapsed_s']} s.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--observed", "--research", "--weights", "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--research-l-result", default="success")
    ap.add_argument("--research-s-result", default="success")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"outcome": rec["outcome"], "rule": rec["rule"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
