"""The Human1 evaluate step (NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md sections 7-9): the three hidden worlds, researcher
L2 and the fixed comparator on each human-supplied pair.

For each world it regenerates the world from its seed and checks the records against it:
- the observed-data hash (regenerated, shipped and declared);
- L2's system text is exactly the frozen text; every user and repair prompt rebuilt byte for byte from the world's own
  record; every experiment recomputed from that world's observed data with t0-beta;
- the comparator recomputed from the observed data: the same four experiments, results, statuses and selection;
- the canaries of all three worlds, the researcher model's hash, the guard and the research job's result.

Then it reveals the world and reads it:
- informative (``informativeness``, a function of the world and the instrument only, computed before any record is
  read): E alone beats no covariate (95% lower bound above 0) on days 99-112 or days 99-126 of the observed data, and
  the supplied contrast is present: E+D: E given D above 0 and D given E at or below 0 on days 99-126 (so the pair is
  distinguishable); E+noise: N alone and N given E at or below 0 on days 99-112 and 99-126; E+R: R alone and R given E
  at or below 0 on days 99-112 and 99-126. An uninformative world counts no success or failure;
- adjudication (``adjudicate.py``): the frozen claim, selection and pair-type rules, applied alike to L2 and to the
  comparator;
- confirmation (days 127-154, t0-beta, with the matched ridge for context only): {E}, {Z}, {E, Z}, Z given E, E given
  Z, and both final selections. Confirmation never rescues an unsupported conclusion.

Programme reading over the three worlds (first match wins; frozen before the run):
1. INFRASTRUCTURE FAILURE: an integrity issue, or an L2 call without a valid response after its repair (execution
   integrity), in any world.
2. BENCHMARK FAILURE: fewer than 2 informative worlds.
3. NARROW RESEARCHER FAILURE: L2 fails in at least 2 informative worlds.
4. SCRIPTABLE NARROW KERNEL: L2 and the comparator both succeed in every informative world, and L2 used more than 0.75
   times the comparator's experiments over the informative worlds (no research-efficiency advantage).
5. AGENTIC VALUE SIGNAL: L2 succeeds in every informative world, and the comparator fails in at least one, or L2 used
   at most 0.75 times the comparator's experiments over the informative worlds.
6. MIXED: anything else.
Closing line, predeclared: INFRASTRUCTURE or BENCHMARK FAILURE -> BENCHMARK/INFRASTRUCTURE RESULT ONLY; NARROW RESEARCHER
FAILURE -> STOP THIS RESEARCHER LINE; SCRIPTABLE NARROW KERNEL -> USE A SCRIPT / HUMAN-DRIVEN WORKFLOW; AGENTIC VALUE
SIGNAL -> AUTONOMOUS RESEARCH KERNEL SURVIVES; MIXED -> STOP THIS RESEARCHER LINE if the comparator succeeded in every
informative world in which L2 failed, otherwise USE A SCRIPT / HUMAN-DRIVEN WORKFLOW.

    python -m research_loop_proof.human1.truth.evaluate --run-id ID --observed D --research D --weights D --out D
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
from research_loop_proof.discovery1.truth.evaluate import _same_runs, cost
from research_loop_proof.human1.lab import comparator
from research_loop_proof.human1.lab.executor import IDS2, Lab2
from research_loop_proof.human1.lab.researcher import BUDGET2, call_plan2, rebuild_mismatches2, system_text2
from research_loop_proof.human1.truth.adjudicate import adjudicate, usable
from research_loop_proof.human1.truth.observe import SCORED_WORLDS, hidden_world
from research_loop_proof.human1.truth.spec import spec_sha
from research_loop_proof.human1.truth.world import PAIR_TYPE, PAIRS
from research_loop_proof.learn1.lab.researcher import LESSON_FILE, frozen_lesson
from research_loop_proof.learn1.truth.evaluate import _pct, _trajectory, _yn, lesson_mentions, relative_to_change
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
EFFICIENCY_RATIO = 0.75
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "comparator.json")
LINES = {"BENCHMARK/INFRASTRUCTURE RESULT ONLY", "STOP THIS RESEARCHER LINE", "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW",
         "AUTONOMOUS RESEARCH KERNEL SURVIVES"}
CAVEATS = ["Three worlds and one stochastic trajectory of the researcher in each: a small batch, not a rate.",
           "E is in every packet by construction: a benchmark condition (a good hypothesis supplied by a human), not a "
           "discovery claim. Hypothesis generation is not tested.",
           "The question is predictive information, not causation.",
           "The comparator's day-126 conditional tests are the contrasts the informativeness check runs, so in an "
           "informative E+D world the script resolves the pair by construction: it is the competence floor.",
           "Confirmation skill is reported separately and never rescues an unsupported conclusion."]


# ----------------------------------------------------------------- call failures and trajectory (two rounds)

def call_failures2(ai: dict) -> list[str]:
    """Calls that did not end with a valid response after their repair (service or format failures)."""
    calls = {c["call"]: c for c in ai.get("calls", [])}
    out = []
    for step in call_plan2():
        c = calls.get(step["call"])
        if c is None:
            out.append(f"call {step['call']}: never made")
        elif not c.get("valid"):
            cats = sorted({str(a.get("refusal_category")) for a in c["attempts"] if a.get("stop_reason") == "refusal"})
            out.append(f"call {step['call']}: no valid response after its repair ({'; '.join(c.get('errors', []))}"
                       + (f"; refusal categories {cats}" if cats else "") + ")")
    return out


def rounds_table2(calls: list[dict], tau: int) -> list[dict]:
    """One row per call (learn1's table with the Human1 budget). A call's belief table and notes are written together
    with its requests, before that round's results exist; the update the results caused is the change to the next
    valid call's table."""
    tables = {c["call"]: {b["candidate"]: b["status"] for b in c["response"]["beliefs"]} for c in calls if c.get("valid")}
    rows, used = [], 0
    for c in calls:
        row = {"call": c["call"], "round": c.get("round"), "cutoff": c["cutoff"], "final": c["final"],
               "valid": bool(c.get("valid"))}
        if c.get("valid"):
            r, now = c["response"], tables[c["call"]]
            later = [k for k in tables if k > c["call"]]
            nxt = tables[min(later)] if later else None
            row.update(entering=now, notes=r["notes"],
                       updates_after=None if nxt is None else {k: [v, nxt[k]] for k, v in now.items() if nxt[k] != v})
            if c["final"]:
                row.update(final_selection=r["final_selection"], conclusion=r["conclusion"])
        else:
            row.update(entering=None, updates_after=None, errors=c.get("errors", []))
        exps = []
        for e in c.get("experiments", []):
            q, res = e["request"], e["result"]
            exps.append({"id": e["id"], "covariates": q["covariates"], "reference": q["reference"],
                         "window_days": q["window_days"], "expect": q["expect"], "because": q["because"],
                         "scored_days": res["scored_days"], "skill": res["skill"], "lo95": res["lo95"],
                         "hi95": res["hi95"], "relative_to_change": relative_to_change(res["scored_days"], tau)})
        used += len(exps)
        row.update(experiments=exps, budget_left=BUDGET2["total_experiments"] - used)
        rows.append(row)
    return rows


# ----------------------------------------------------------------- integrity

def integrity_issues(w: World, research_dir: Path, k: str, recompute_lab, canaries: list[str],
                     job_result: str = "success") -> tuple[list[str], dict]:
    p = f"{k}: "
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
    if ai.get("condition") != "L":
        issues.append(p + f"the record is condition {ai.get('condition')!r}")
    expected = system_text2()
    info["system_sha256"] = ai.get("system_sha256")
    if calls and (ai.get("system_sha256") != sha256_text(expected) or ai.get("system_text") != expected):
        issues.append(p + "the system text is not the frozen L2 text")
    try:
        mism = rebuild_mismatches2(calls)
    except Exception as exc:  # a record that cannot be replayed is a mismatch, never a crash
        mism = [f"rebuild failed ({type(exc).__name__})"]
    if mism:
        issues.append(p + "prompt-rebuild mismatch: " + ", ".join(mism))
    if any(a.get("served_model_sha256") not in (None, RESEARCHER["model_sha256"]) for c in calls for a in c["attempts"]):
        issues.append(p + "researcher-model hash mismatch")
    bad = []
    for c in calls:
        for e in c.get("experiments", []):
            try:
                again = recompute_lab.run(e["request"], c["cutoff"], e["id"])
            except ValueError:
                bad.append(e["id"])
                continue
            if any(not _close(again[key], e["result"].get(key)) for key in again):
                bad.append(e["id"])
    info["experiments_recomputed"] = sum(len(c.get("experiments", [])) for c in calls)
    if bad:
        issues.append(p + "experiment results differ when recomputed from the observed data: " + ", ".join(bad))
    comp_path = research_dir / "comparator.json"
    if not comp_path.is_file():
        issues.append(p + "no comparator record")
    else:
        comp = json.loads(comp_path.read_text())
        again = comparator.run(recompute_lab)
        if not _same_runs(again["experiments"], comp.get("experiments", [])) or \
                again["final_selection"] != comp.get("final_selection") or again["statuses"] != comp.get("statuses"):
            issues.append(p + "the comparator's record differs from its recomputation on the observed data")
        info["comparator_recomputed"] = len(again["experiments"])
    texts = [f.read_text(encoding="utf-8", errors="replace") for f in research_dir.rglob("*") if f.is_file()]
    if any(c in t for c in canaries for t in texts):
        issues.append(p + "canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    return issues, info


# ----------------------------------------------------------------- informativeness (world and instrument only)

def informativeness(w: World, pair: tuple[str, str], model) -> dict:
    """Whether E is detectable after the change and the supplied contrast is present, by direct t0-beta tests on the
    observed data. It reads no research record."""
    pair_type = PAIR_TYPE[pair]
    e, z = w.ids["E"], w.ids[pair[1]]
    inst = t0_beta.BetaT0(model)
    lab = Lab2(observed_arrays(w, OBS_LAST), inst)

    def test(cov, ref, win, cutoff):
        return _row(lab.run({"covariates": [cov], "reference": [ref] if ref else [], "window_days": win}, cutoff,
                            "informativeness"))
    zn = pair[1]
    checks = {"E alone, days 99-112": test(e, None, 14, 112), "E alone, days 99-126": test(e, None, 28, 126)}
    e_detectable = any(r["lo95"] > 0 for r in checks.values())
    if pair_type == "E+D":
        checks["E given D, days 99-126"] = test(e, z, 28, 126)
        checks["D given E, days 99-126"] = test(z, e, 28, 126)
        contrast = checks["E given D, days 99-126"]["lo95"] > 0 and checks["D given E, days 99-126"]["lo95"] <= 0
        required = ["E given D, days 99-126 (above 0)", "D given E, days 99-126 (at or below 0)"]
        descriptive = {"D alone, days 99-112": test(z, None, 14, 112), "D alone, days 99-126": test(z, None, 28, 126)}
    else:
        names = [f"{zn} alone, days 99-112", f"{zn} alone, days 99-126", f"{zn} given E, days 99-112",
                 f"{zn} given E, days 99-126"]
        for name, (ref, win, cutoff) in zip(names, ((None, 14, 112), (None, 28, 126), (e, 14, 112), (e, 28, 126))):
            checks[name] = test(z, ref, win, cutoff)
        contrast = all(checks[n]["lo95"] <= 0 for n in names)
        required = [f"{n} (at or below 0)" for n in names]
        descriptive = {f"E given {zn}, days 99-126": test(e, z, 28, 126)}
        if pair_type == "E+R":
            descriptive.update({"R alone, days 57-84 (before the change)": test(z, None, 28, 84),
                                "R alone, days 85-112 (straddles the change)": test(z, None, 28, 112)})
    return {"pair_type": pair_type, "checks": checks, "required": ["E alone, days 99-112 or 99-126 (above 0)"] + required,
            "descriptive": descriptive, "e_detectable": e_detectable, "contrast_present": bool(contrast),
            "informative": bool(e_detectable and contrast), "t0_forecasts": inst.rows}


# ----------------------------------------------------------------- one world

def l2_experiments(ai: dict) -> list[dict]:
    return [dict(e, round=c["round"], cutoff=c["cutoff"]) for c in ai.get("calls", []) for e in c.get("experiments", [])]


def _listing(exps: list[dict], role_of: dict) -> list[dict]:
    return [{"id": x["id"], "round": x["round"], "covariates": x["request"]["covariates"],
             "reference": x["request"]["reference"], "roles": [role_of[i] for i in x["request"]["covariates"]],
             "reference_roles": [role_of[i] for i in x["request"]["reference"]],
             "window_days": x["request"]["window_days"], "scored_days": x["result"]["scored_days"],
             "skill": x["result"]["skill"], "lo95": x["result"]["lo95"], "hi95": x["result"]["hi95"],
             "usable": usable(x), "expect": x["request"].get("expect"), "because": x["request"].get("because")}
            for x in exps]


def evaluate_world(k: str, w: World, pair: tuple[str, str], model, observed_dir: Path, research_dir: Path,
                   job_result: str, canaries: list[str]) -> dict:
    pair_type = PAIR_TYPE[pair]
    inform = informativeness(w, pair, model)  # before any record is read
    role_of = {v: r for r, v in w.ids.items()}
    roles = {"E": w.ids["E"], "Z": w.ids[pair[1]]}
    t0_obs = t0_beta.BetaT0(model)
    obs_lab = Lab2(observed_arrays(w, OBS_LAST), t0_obs)
    issues, info = [], {}
    meta = json.loads((observed_dir / "observed.json").read_text())
    regen = arrays_sha256(observed_arrays(w, OBS_LAST))
    shipped = arrays_sha256(load_observed(observed_dir / "observed.npz"))
    info["observed_sha256"] = {"regenerated": regen, "shipped": shipped, "declared": meta["arrays_sha256"]}
    if not regen == shipped == meta["arrays_sha256"]:
        issues.append(f"{k}: observed-data hash mismatch")
    more, inf = integrity_issues(w, research_dir, k, obs_lab, canaries, job_result)
    issues += more
    info.update(inf)
    p = research_dir / "ai.json"
    ai = json.loads(p.read_text()) if p.is_file() else {}
    ai.setdefault("calls", [])
    p = research_dir / "comparator.json"
    comp = json.loads(p.read_text()) if p.is_file() else {"experiments": [], "statuses": {}, "final_selection": []}
    calls = ai["calls"]
    final = calls[-1] if ai.get("final_valid") else None
    l2_status = {b["candidate"]: b["status"] for b in final["response"]["beliefs"]} if final else {}
    l2_sel = ai.get("final_selection") if ai.get("final_valid") else []
    l2_exps = l2_experiments(ai)
    l2_adj = adjudicate(l2_exps, l2_status, l2_sel, roles, pair_type, inform["informative"])
    comp_adj = adjudicate(comp.get("experiments", []), comp.get("statuses"), comp.get("final_selection"), roles,
                          pair_type, inform["informative"])
    full = {"y": w.y, **{w.ids[r]: w.x[r] for r in pair}}
    t0_full, ridge = t0_beta.BetaT0(model), RidgeInstrument()
    labs = {"t0": Lab2(full, t0_full), "ridge": Lab2(full, ridge)}

    def confirm(cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in labs.items()}

    e, z, zn = roles["E"], roles["Z"], pair[1]
    confirmation = {"{E} vs {}": confirm([e], []), f"{{{zn}}} vs {{}}": confirm([z], []),
                    f"{{E, {zn}}} vs {{}}": confirm([e, z], []),
                    f"{zn} given E ({{E, {zn}}} vs {{E}})": confirm([z], [e]),
                    f"E given {zn} ({{E, {zn}}} vs {{{zn}}})": confirm([e], [z])}
    comp_sel = comp.get("final_selection") or []
    selections = {"L2": confirm(l2_sel, []) if l2_sel else None, "comparator": confirm(comp_sel, []) if comp_sel else None}
    reasons = {b["candidate"]: {"status": b["status"], "cites": b["cites"], "reason": b["reason"]}
               for b in final["response"]["beliefs"]} if final else {}
    l2 = {**l2_adj, "experiments_used": len(l2_exps), "experiments": _listing(l2_exps, role_of),
          "final_valid": bool(ai.get("final_valid")), "final_rows": reasons, "conclusion": ai.get("conclusion"),
          "call_failures": [f"{k}: L2 {x}" for x in call_failures2(ai)], "lesson_mentions": lesson_mentions(calls),
          "rounds": rounds_table2(calls, w.tau), "cost": cost(ai), "elapsed_s": ai.get("elapsed_s")}
    cmp_ = {**comp_adj, "experiments_used": len(comp.get("experiments", [])),
            "experiments": _listing(comp.get("experiments", []), role_of), "statuses": comp.get("statuses"),
            "t0_forecasts": comp.get("t0_forecasts"), "elapsed_s": comp.get("elapsed_s")}
    return {"world": k, "seed": w.seed, "pair_type": pair_type, "informative": inform["informative"],
            "informativeness": inform,
            "truth": {"tau": w.tau, "roles": {r: w.ids[r] for r in pair}, "signs": {w.ids[r]: w.signs[r] for r in pair}},
            "integrity": {"issues": issues, **info}, "L2": l2, "comparator": cmp_, "confirmation": confirmation,
            "confirmation_selections": selections,
            "t0_beta_forecasts": {"research_L2": ai.get("t0_forecasts"), "research_comparator": comp.get("t0_forecasts"),
                                  "evaluate": inform["t0_forecasts"] + t0_obs.rows + t0_full.rows}}


# ----------------------------------------------------------------- programme reading

def programme(issues: list[str], failures: list[str], worlds: dict) -> tuple[str, str]:
    if issues or failures:
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(issues + failures)
    informative = [k for k in worlds if worlds[k]["informative"]]
    if len(informative) < 2:
        return "BENCHMARK FAILURE", f"row 2: {len(informative)} informative world(s) ({', '.join(informative) or 'none'})"
    l2 = [k for k in informative if worlds[k]["L2"]["success"]]
    comp = [k for k in informative if worlds[k]["comparator"]["success"]]
    l2_exp = sum(worlds[k]["L2"]["experiments_used"] for k in informative)
    comp_exp = sum(worlds[k]["comparator"]["experiments_used"] for k in informative)
    efficient = l2_exp <= EFFICIENCY_RATIO * comp_exp
    counts = (f"informative {len(informative)} ({', '.join(informative)}); L2 succeeds in {len(l2)} "
              f"({', '.join(l2) or 'none'}), comparator in {len(comp)} ({', '.join(comp) or 'none'}); experiments over "
              f"informative worlds: L2 {l2_exp}, comparator {comp_exp} (efficiency advantage: {_yn(efficient)})")
    if len(informative) - len(l2) >= 2:
        return "NARROW RESEARCHER FAILURE", "row 3: " + counts
    if len(l2) == len(informative):
        if len(comp) == len(informative) and not efficient:
            return "SCRIPTABLE NARROW KERNEL", "row 4: " + counts
        return "AGENTIC VALUE SIGNAL", "row 5: " + counts
    return "MIXED", "row 6: " + counts


def closing_line(label: str, worlds: dict) -> str:
    if label in ("INFRASTRUCTURE FAILURE", "BENCHMARK FAILURE"):
        return "BENCHMARK/INFRASTRUCTURE RESULT ONLY"
    if label == "NARROW RESEARCHER FAILURE":
        return "STOP THIS RESEARCHER LINE"
    if label == "SCRIPTABLE NARROW KERNEL":
        return "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW"
    if label == "AGENTIC VALUE SIGNAL":
        return "AUTONOMOUS RESEARCH KERNEL SURVIVES"
    failed = [k for k in worlds if worlds[k]["informative"] and not worlds[k]["L2"]["success"]]
    if all(worlds[k]["comparator"]["success"] for k in failed):
        return "STOP THIS RESEARCHER LINE"
    return "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW"


# ----------------------------------------------------------------- run

def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    observed, research = Path(args.observed), Path(args.research)
    from research_loop_proof.beta1.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    worlds_gen = {k: hidden_world(args.run_id, k) for k in SCORED_WORLDS}
    canaries = [w.canary for w in worlds_gen.values()]
    results = {"w1": args.research_w1_result, "w2": args.research_w2_result, "w3": args.research_w3_result}
    worlds = {k: evaluate_world(k, worlds_gen[k], PAIRS[k], model, observed / k, research / k, results[k], canaries)
              for k in SCORED_WORLDS}
    issues = [x for k in SCORED_WORLDS for x in worlds[k]["integrity"]["issues"]]
    failures = [x for k in SCORED_WORLDS for x in worlds[k]["L2"]["call_failures"]]
    label, rule = programme(issues, failures, worlds)
    line = closing_line(label, worlds)
    lesson = frozen_lesson()
    record = {
        "phase": "human1-run", "reading": label, "rule": rule, "closing_line": line, "caveats": CAVEATS,
        "spec_sha": spec_sha(), "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"),
        "instrument": load_record, "lesson_sha256": sha256_text(lesson),
        "system_sha256_expected": sha256_text(system_text2()), "comparator_rule": comparator.RULE,
        "candidate_ids": list(IDS2), "integrity_issues": issues, "call_failures": failures, "worlds": worlds,
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": "human1-run", "reading": label, "closing_line": line,
                                                  "spec_sha": record["spec_sha"], "run_id": args.run_id,
                                                  "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record), encoding="utf-8")
    for k in SCORED_WORLDS:
        (out / k).mkdir(exist_ok=True)
        for name in FILES:
            if (research / k / name).is_file():
                shutil.copyfile(research / k / name, out / k / name)
        shutil.copyfile(observed / k / "observed.json", out / k / "observed.json")
    shutil.copyfile(LESSON_FILE, out / "lesson.json")
    return record


# ----------------------------------------------------------------- report

def _criteria(a: dict) -> str:
    return " ".join(f"{name.split('_')[0]}:{'Y' if v else 'n'}" for name, v in a["criteria"].items())


def _exp_lines(exps: list[dict]) -> list[str]:
    def ids(xs, rs):
        return "[" + ", ".join(f"{i} ({r})" for i, r in zip(xs, rs)) + "]" if xs else "none"
    return [f"- {x['id']} (round {x['round']}): {ids(x['covariates'], x['roles'])} given "
            f"{ids(x['reference'], x['reference_roles'])}, {x['window_days']} days, scored days {x['scored_days'][0]}-"
            f"{x['scored_days'][1]} -> {_pct(x)}{'' if x['usable'] else ' (not usable: mixed or under 14 days)'}"
            for x in exps] or ["- none"]


def _claims_table(a: dict, role_of: dict) -> list[str]:
    lines = ["| candidate | final status | selected | positive alone | positive given the other | negative alone | "
             "negative given the other | claim supported |", "|---|---|---|---|---|---|---|---|"]
    for cid, c in a["claims"].items():
        lines.append(f"| {cid} ({role_of[cid]}) | {c['status']} | {_yn(c['selected'])} | "
                     f"{_yn(c['pos_alone'])}{' (by elimination)' if c['alone_by_elimination'] else ''} | "
                     f"{_yn(c['pos_cond'])}{' (by elimination)' if c['cond_by_elimination'] else ''} | "
                     f"{_yn(c['neg_alone'])} | {_yn(c['neg_cond'])} | {_yn(c['supported'])} ({c['rule']}) |")
    lines.append(f"\nSelection {a['selection']} supported: {_yn(a['selection_supported'])}; incoherent: "
                 f"{a['incoherent'] or 'none'}; unsupported acceptances: {a['unsupported_acceptances'] or 'none'}; "
                 f"unsupported rejection or zero-effect claims: {a['unsupported_rejections'] or 'none'}.")
    return lines


def _world_report(k: str, r: dict) -> list[str]:
    t, inf, l2, cp = r["truth"], r["informativeness"], r["L2"], r["comparator"]
    role_of = {v: n for n, v in t["roles"].items()}
    lines = [f"## World {k}: {r['pair_type']}, {'informative' if r['informative'] else 'UNINFORMATIVE'}", "",
             f"First changed day {t['tau']}. Supplied pair: " + ", ".join(f"{n} = {i}" for n, i in t["roles"].items())
             + f". Integrity: {r['integrity']['issues'] or 'clean'}.", "",
             "Informativeness (direct t0-beta on the observed data; required: " + "; ".join(inf["required"]) + "):", ""]
    lines += [f"- {name}: {_pct(row)}" for name, row in inf["checks"].items()]
    lines += [f"- (descriptive) {name}: {_pct(row)}" for name, row in inf["descriptive"].items()]
    lines += ["", f"E detectable: {_yn(inf['e_detectable'])}; contrast present: {_yn(inf['contrast_present'])}.", "",
              "| | L2 (lesson-only researcher) | fixed comparator |", "|---|---|---|",
              f"| experiments used | {l2['experiments_used']} | {cp['experiments_used']} |",
              f"| final statuses | " + ", ".join(f"{c} ({role_of[c]}) {v['status']}" for c, v in l2["claims"].items())
              + " | " + ", ".join(f"{c} ({role_of[c]}) {v['status']}" for c, v in cp["claims"].items()) + " |",
              f"| final selection | {l2['selection']} | {cp['selection']} |",
              f"| criteria 1-5 | {_criteria(l2)} | {_criteria(cp)} |",
              f"| unsupported acceptances / rejections | {len(l2['unsupported_acceptances'])} / "
              f"{len(l2['unsupported_rejections'])} | {len(cp['unsupported_acceptances'])} / "
              f"{len(cp['unsupported_rejections'])} |",
              f"| SUCCESS | {'**yes**' if l2['success'] else 'no'} | {'**yes**' if cp['success'] else 'no'} |"]
    sels = r["confirmation_selections"]
    lines += [f"| final selection vs {{}} on days 127-154 (t0-beta; reported separately) | "
              f"{_pct(sels['L2'] and sels['L2']['t0']) if l2['selection'] else 'empty selection'} | "
              f"{_pct(sels['comparator'] and sels['comparator']['t0']) if cp['selection'] else 'empty selection'} |", ""]
    lines += ["### L2: experiments in order", ""] + _exp_lines(l2["experiments"])
    lines += ["", "### L2: final conclusion (verbatim)", ""]
    lines += [f"- {c} ({role_of[c]}): {v['status']}; cites {', '.join(v['cites']) or 'none'}; reason: {v['reason']}"
              for c, v in l2["final_rows"].items()]
    lines += ["", f"Conclusion: {l2['conclusion']}", "", "### L2: claims against its own experiments", ""]
    lines += _claims_table(l2, role_of)
    lines += ["", "### L2 trajectory", ""] + _trajectory(l2, role_of)
    lines += ["### Comparator: experiments in order", ""] + _exp_lines(cp["experiments"])
    lines += ["", "### Comparator: claims against its own experiments", ""] + _claims_table(cp, role_of)
    lines += ["", "### Confirmation (days 127-154)", "", "| comparison | t0-beta | ridge (context) |", "|---|---|---|"]
    lines += [f"| {name} | {_pct(c['t0'])} | {_pct(c['ridge'])} |" for name, c in r["confirmation"].items()]
    lines.append("")
    return lines


def report(rec: dict) -> str:
    lines = [f"# Human1 three-world result: {rec['reading']}", "", f"Reading {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"human1_spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; instrument "
             f"{rec['instrument'].get('repo')} @ {rec['instrument'].get('served_revision')} (tfc-t0 "
             f"{rec['instrument'].get('tfc_t0')}); lesson sha256 `{rec['lesson_sha256']}`.", "",
             f"Integrity: {rec['integrity_issues'] or 'clean'}. L2 call failures: {rec['call_failures'] or 'none'}.", "",
             "| world | pair | informative | L2 success | L2 criteria 1-5 | comparator success | comparator criteria 1-5 | "
             "experiments L2 / comparator |", "|---|---|---|---|---|---|---|---|"]
    for k, r in rec["worlds"].items():
        lines.append(f"| {k} | {r['pair_type']} | {_yn(r['informative'])} | {_yn(r['L2']['success'])} | "
                     f"{_criteria(r['L2'])} | {_yn(r['comparator']['success'])} | {_criteria(r['comparator'])} | "
                     f"{r['L2']['experiments_used']} / {r['comparator']['experiments_used']} |")
    lines += ["", f"Closing line (predeclared): {rec['closing_line']}", ""]
    for k, r in rec["worlds"].items():
        lines += _world_report(k, r)
    lines += ["## Cost", ""]
    for k, r in rec["worlds"].items():
        c = r["L2"]["cost"]
        lines.append(f"- {k}: L2 tokens {c['tokens_used']} ({c['usage_total']}); API attempts {c['api_attempts']} "
                     f"(refusals {c['refusals']}, repairs {c['repairs']}); research wall time L2 {r['L2']['elapsed_s']} "
                     f"s, comparator {r['comparator']['elapsed_s']} s; t0-beta forecasts: L2 "
                     f"{r['t0_beta_forecasts']['research_L2']}, comparator {r['t0_beta_forecasts']['research_comparator']}"
                     f", evaluate {r['t0_beta_forecasts']['evaluate']}.")
    lines += [f"- evaluate: {rec['elapsed_s']} s.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--observed", "--research", "--weights", "--out"):
        ap.add_argument(a, required=True)
    for k in SCORED_WORLDS:
        ap.add_argument(f"--research-{k}-result", default="success")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"reading": rec["reading"], "rule": rec["rule"], "closing_line": rec["closing_line"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
