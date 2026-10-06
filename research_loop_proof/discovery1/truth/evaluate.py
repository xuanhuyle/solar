"""The Discovery1 evaluate step (NEXT_DISCOVERY_MILESTONE_PROMPT.md, "Evaluation" and "Programme reading"): the three
hidden worlds, researcher L8 and the fixed comparator on each.

For each world it regenerates the world from its seed and checks the records against it:
- the observed-data hash (regenerated, shipped and declared);
- L8's system text is exactly the frozen text; every user and repair prompt rebuilt byte for byte from the world's own
  record; every experiment recomputed from that world's observed data with t0-beta;
- the comparator recomputed from the observed data: the same six experiments, results and final selection;
- the canaries of all three worlds, the researcher model's hash, the guard and the research job's result.

Then it reveals the world and reads it:
- detectable: t0-beta with E alone against no covariate on the observed post-change windows, days 99-112 (available in
  round 2) and days 99-126 (available in round 3). The world is informative if either 95% lower bound is above 0;
  otherwise it is uninformative for researcher competence and no success or failure is counted in it;
- success (the owner's six criteria, applied alike to L8 and the comparator):
  1. E was detectable;
  2. E was among the covariates of a round 2-3 experiment (every round 2-3 window ends after the change);
  3. E is in the final selection;
  4. R and all five noise candidates are absent from the final selection (D may be selected; the report separates D's
     proxy value and its increment given E);
  5. supporting evidence of its own: a round 2-3 experiment with a lower bound above 0 that has either E as its only
     covariate (with or without a reference), or exactly the final selection as covariates and no reference;
  6. the final selection beats no covariate on the confirmation days 127-154 (t0-beta lower bound above 0); an empty
     selection, or one of more than 4 candidates (which the lab cannot score), fails it;
- confirmation (days 127-154, t0-beta, with the matched ridge for context only): {E}, {R}, {D}, {E, D}, D given E,
  E given D, R given E, and both final selections.

Programme reading over the three worlds (first match wins; frozen before the run):
1. INFRASTRUCTURE FAILURE: an integrity issue, or an L8 call without a valid response after its repair, in any world.
2. BENCHMARK FAILURE: fewer than 2 informative worlds.
3. DISCOVERY SIGNAL: L8 succeeds in at least 2 informative worlds, and in more of them than the comparator.
4. BOTH SUCCEED: L8 and the comparator each succeed in at least 2 informative worlds.
5. NO DISCOVERY SIGNAL: L8 fails in at least 2 informative worlds.
6. NO DISCOVERY SIGNAL (predeclared fallback, the only case rows 1-5 leave): exactly 2 informative worlds and L8
   succeeds in 1 of them, so it does not succeed in at least 2.
Closing line, predeclared: DISCOVERY SIGNAL -> MOVE TO A REAL-WORLD RESEARCH TEST; NO DISCOVERY SIGNAL -> NARROW TO
HUMAN-SUPPLIED HYPOTHESES; BOTH SUCCEED, BENCHMARK FAILURE, INFRASTRUCTURE FAILURE -> BENCHMARK/INFRASTRUCTURE RESULT
ONLY.

    python -m research_loop_proof.discovery1.truth.evaluate --run-id ID --observed D --research D --weights D --out D
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
from research_loop_proof.beta1.truth.evaluate import call_failures
from research_loop_proof.discovery1.lab import comparator
from research_loop_proof.discovery1.lab.executor import IDS8, Lab8
from research_loop_proof.discovery1.lab.researcher import rebuild_mismatches8, system_text8
from research_loop_proof.discovery1.truth.observe import SCORED_WORLDS, hidden_world
from research_loop_proof.discovery1.truth.spec import spec_sha
from research_loop_proof.discovery1.truth.world import NOISE, ROLES8
from research_loop_proof.learn1.lab.researcher import LESSON_FILE, frozen_lesson
from research_loop_proof.learn1.truth.evaluate import _pct, _trajectory, _yn, lesson_mentions, reopened, rounds_table
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
MAX_COVARIATES = 4
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "comparator.json")
CLOSING = {"DISCOVERY SIGNAL": "MOVE TO A REAL-WORLD RESEARCH TEST",
           "NO DISCOVERY SIGNAL": "NARROW TO HUMAN-SUPPLIED HYPOTHESES",
           "BOTH SUCCEED": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "BENCHMARK FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "INFRASTRUCTURE FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY"}
CAVEATS = ["Three worlds and one stochastic trajectory of the researcher in each: a small batch, not a rate.",
           "The comparator resolves candidates to pairs only; it can succeed only where the emerging driver's pair "
           "partner is its proxy.",
           "Forecast accuracy alone is not discovery: success needs the six criteria, supporting evidence included."]


# ----------------------------------------------------------------- integrity

def _same_runs(a: list[dict], b: list[dict]) -> bool:
    keys = ("id", "round", "cutoff", "request")
    return len(a) == len(b) and all(all(x.get(k) == y.get(k) for k in keys)
                                    and all(_close(x["result"][k], y["result"].get(k)) for k in x["result"])
                                    for x, y in zip(a, b))


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
    expected = system_text8()
    info["system_sha256"] = ai.get("system_sha256")
    if calls and (ai.get("system_sha256") != sha256_text(expected) or ai.get("system_text") != expected):
        issues.append(p + "the system text is not the frozen L8 text")
    try:
        mism = rebuild_mismatches8(calls)
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
                again["final_selection"] != comp.get("final_selection"):
            issues.append(p + "the comparator's record differs from its recomputation on the observed data")
        info["comparator_recomputed"] = len(again["experiments"])
    texts = [f.read_text(encoding="utf-8", errors="replace") for f in research_dir.rglob("*") if f.is_file()]
    if any(c in t for c in canaries for t in texts):
        issues.append(p + "canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    return issues, info


# ----------------------------------------------------------------- indicators and success

def l8_experiments(ai: dict) -> list[dict]:
    return [dict(e, round=c["round"], cutoff=c["cutoff"]) for c in ai.get("calls", []) for e in c.get("experiments", [])]


def _brief(x: dict) -> dict:
    r = x["result"]
    return {"id": x["id"], "round": x["round"], "covariates": x["request"]["covariates"],
            "reference": x["request"]["reference"], "window_days": x["request"]["window_days"],
            "scored_days": r["scored_days"], "skill": r["skill"], "lo95": r["lo95"], "hi95": r["hi95"]}


def indicators(exps: list[dict], selection: list | None, roles: dict) -> dict:
    """What a search (L8's or the comparator's experiments, each with its round) did about E, R, D and the noise."""
    sel = list(selection or [])
    e, d = roles["E"], roles["D"]
    post = [x for x in exps if x["round"] in (2, 3)]
    entered = [x for x in exps if e in x["request"]["covariates"] or e in x["request"]["reference"]]
    tested = [x for x in post if e in x["request"]["covariates"]]
    alone = [x for x in post if x["request"]["covariates"] == [e]]
    distinguished = [x for x in alone if x["result"]["lo95"] > 0]
    set_support = [x for x in post if sel and sorted(x["request"]["covariates"]) == sorted(sel)
                   and not x["request"]["reference"] and x["result"]["lo95"] > 0]
    noise = [roles[n] for n in NOISE]
    return {
        "experiments_used": len(exps), "final_selection": sel,
        "first_entered": None if not entered else {"id": entered[0]["id"], "round": entered[0]["round"],
                                                   "as": "covariate" if e in entered[0]["request"]["covariates"]
                                                   else "reference"},
        "tested_post_change": bool(tested), "first_post_change_test": tested[0]["id"] if tested else None,
        "e_alone_post_change": [_brief(x) for x in alone], "distinguished": bool(distinguished),
        "supporting_evidence": list(dict.fromkeys(x["id"] for x in distinguished + set_support)),
        "e_selected": e in sel, "r_selected": roles["R"] in sel, "noise_selected": [c for c in sel if c in noise],
        "d_selected": d in sel, "d_experiments": [_brief(x) for x in exps if d in x["request"]["covariates"]],
    }


def success(ind: dict, informative: bool, confirm_t0: dict | None) -> dict:
    crit = {"1_e_detectable": informative, "2_e_tested_post_change": ind["tested_post_change"],
            "3_e_selected": ind["e_selected"],
            "4_no_r_no_noise": not ind["r_selected"] and not ind["noise_selected"],
            "5_supporting_evidence": bool(ind["supporting_evidence"]),
            "6_confirmation_lower_bound_above_0": bool(confirm_t0) and confirm_t0["lo95"] > 0}
    return {"criteria": crit, "success": all(crit.values())}


def programme(issues: list[str], failures: list[str], worlds: dict) -> tuple[str, str]:
    if issues or failures:
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(issues + failures)
    informative = [k for k in worlds if worlds[k]["informative"]]
    if len(informative) < 2:
        return "BENCHMARK FAILURE", f"row 2: {len(informative)} informative world(s) ({', '.join(informative) or 'none'})"
    l8 = [k for k in informative if worlds[k]["L8"]["success"]]
    comp = [k for k in informative if worlds[k]["comparator"]["success"]]
    counts = (f"informative {len(informative)} ({', '.join(informative)}); L8 succeeds in {len(l8)} "
              f"({', '.join(l8) or 'none'}); comparator in {len(comp)} ({', '.join(comp) or 'none'})")
    if len(l8) >= 2 and len(l8) > len(comp):
        return "DISCOVERY SIGNAL", "row 3: " + counts
    if len(l8) >= 2 and len(comp) >= 2:
        return "BOTH SUCCEED", "row 4: " + counts
    if len(informative) - len(l8) >= 2:
        return "NO DISCOVERY SIGNAL", "row 5: " + counts
    return "NO DISCOVERY SIGNAL", "row 6 (fallback): " + counts


def scorable(selection: list | None) -> bool:
    """A final selection the lab can confirm: 1 to 4 candidates (the menu's covariate limit). A larger selection holds at
    least three of R and the noise candidates, so it fails criterion 4 anyway; it is reported as not scored and fails
    criterion 6, instead of stopping the evaluation."""
    return bool(selection) and len(selection) <= MAX_COVARIATES


def cost(ai: dict) -> dict:
    attempts = [a for c in ai.get("calls", []) for a in c["attempts"]]
    usage = [a["usage"] for a in attempts if a.get("usage")]
    return {"tokens_used": ai.get("tokens_used"), "api_attempts": len(attempts),
            "refusals": sum(1 for a in attempts if a.get("stop_reason") == "refusal"),
            "refusal_categories": sorted({str(a.get("refusal_category")) for a in attempts
                                          if a.get("stop_reason") == "refusal"}),
            "repairs": sum(1 for a in attempts if a.get("attempt") == 2),
            "usage_total": {k: sum(u[k] for u in usage) for k in usage[0]} if usage else {},
            "t0_forecasts": ai.get("t0_forecasts")}


# ----------------------------------------------------------------- one world

def evaluate_world(k: str, w: World, model, observed_dir: Path, research_dir: Path, job_result: str,
                   canaries: list[str]) -> dict:
    roles = {r: w.ids[r] for r in ROLES8}
    t0_obs = t0_beta.BetaT0(model)
    obs_lab = Lab8(observed_arrays(w, OBS_LAST), t0_obs)
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
    comp = json.loads(p.read_text()) if p.is_file() else {"experiments": [], "final_selection": []}
    e = roles["E"]
    detect = {"E_days_99_112": _row(obs_lab.run({"covariates": [e], "reference": [], "window_days": 14}, 112,
                                                "detect-E-round-2")),
              "E_days_99_126": _row(obs_lab.run({"covariates": [e], "reference": [], "window_days": 28}, 126,
                                                "detect-E-round-3"))}
    informative = any(r["lo95"] > 0 for r in detect.values())
    full = {"y": w.y, **{w.ids[r]: w.x[r] for r in ROLES8}}
    t0_full, ridge = t0_beta.BetaT0(model), RidgeInstrument()
    labs = {"t0": Lab8(full, t0_full), "ridge": Lab8(full, ridge)}

    def confirm(cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in labs.items()}

    confirmation = {f"{{{r}}} vs {{}}": confirm([roles[r]], []) for r in ("E", "R", "D")}
    confirmation["{E, D} vs {}"] = confirm([e, roles["D"]], [])
    confirmation["D given E ({E, D} vs {E})"] = confirm([roles["D"]], [e])
    confirmation["E given D ({E, D} vs {D})"] = confirm([e], [roles["D"]])
    confirmation["R given E ({E, R} vs {E})"] = confirm([roles["R"]], [e])
    l8_sel = ai.get("final_selection") if ai.get("final_valid") else None
    comp_sel = comp.get("final_selection") or []
    selections = {"L8": confirm(l8_sel, []) if scorable(l8_sel) else None,
                  "comparator": confirm(comp_sel, []) if scorable(comp_sel) else None}
    l8_ind = indicators(l8_experiments(ai), l8_sel, roles)
    comp_ind = indicators(comp.get("experiments", []), comp_sel, roles)
    calls = ai["calls"]
    final_status = ({b["candidate"]: b["status"] for b in calls[-1]["response"]["beliefs"]}
                    if ai.get("final_valid") else {})
    l8 = {**l8_ind, **success(l8_ind, informative, selections["L8"] and selections["L8"]["t0"]),
          "selection_scored": scorable(l8_sel), "final_valid": bool(ai.get("final_valid")), "conclusion": ai.get("conclusion"), "final_status": final_status,
          "call_failures": [f"{k}: L8 {x}" for x in call_failures(ai)], "reopened": reopened(calls, w.tau),
          "lesson_mentions": lesson_mentions(calls), "rounds": rounds_table(calls, w.tau), "cost": cost(ai)}
    cmp_ = {**comp_ind, **success(comp_ind, informative, selections["comparator"] and selections["comparator"]["t0"]),
            "selection_scored": scorable(comp_sel), "winner": comp.get("winner"), "experiments": [_brief(x) for x in comp.get("experiments", [])],
            "t0_forecasts": comp.get("t0_forecasts")}
    return {"world": k, "seed": w.seed, "informative": informative, "detectability": detect,
            "truth": {"tau": w.tau, "roles": roles, "signs": {roles[r]: w.signs[r] for r in ROLES8}},
            "integrity": {"issues": issues, **info}, "L8": l8, "comparator": cmp_, "confirmation": confirmation,
            "confirmation_selections": selections,
            "t0_beta_forecasts": {"research_L8": ai.get("t0_forecasts"), "research_comparator": comp.get("t0_forecasts"),
                                  "evaluate": t0_obs.rows + t0_full.rows}}


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
    worlds = {k: evaluate_world(k, worlds_gen[k], model, observed / k, research / k, results[k], canaries)
              for k in SCORED_WORLDS}
    issues = [x for k in SCORED_WORLDS for x in worlds[k]["integrity"]["issues"]]
    failures = [x for k in SCORED_WORLDS for x in worlds[k]["L8"]["call_failures"]]
    label, rule = programme(issues, failures, worlds)
    lesson = frozen_lesson()
    record = {
        "phase": "discovery1-run", "reading": label, "rule": rule, "closing_line": CLOSING[label], "caveats": CAVEATS,
        "spec_sha": spec_sha(), "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"),
        "instrument": load_record, "lesson_sha256": sha256_text(lesson),
        "system_sha256_expected": sha256_text(system_text8()), "comparator_rule": comparator.RULE,
        "integrity_issues": issues, "call_failures": failures, "worlds": worlds,
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": "discovery1-run", "reading": label,
                                                  "closing_line": CLOSING[label], "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
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

def _criteria(s: dict) -> str:
    return " ".join(f"{name.split('_')[0]}:{'Y' if v else 'n'}" for name, v in s["criteria"].items())


def _world_report(k: str, r: dict) -> list[str]:
    t = r["truth"]
    role_of = {v: n for n, v in t["roles"].items()}
    l8, cp = r["L8"], r["comparator"]

    def named(ids):
        return "[" + ", ".join(f"{i} ({role_of[i]})" for i in ids) + "]" if ids else "[]"

    def first(ind):
        f = ind["first_entered"]
        return "never" if not f else f"{f['id']} (round {f['round']}, as {f['as']})"
    lines = [f"## World {k}: {'informative' if r['informative'] else 'UNINFORMATIVE (E not detectable)'}", "",
             f"First changed day {t['tau']}. " + ", ".join(f"{n} = {i}" for n, i in t["roles"].items()) + ".", "",
             f"Detectability (t0-beta, E alone vs no covariate): days 99-112 {_pct(r['detectability']['E_days_99_112'])}"
             f"; days 99-126 {_pct(r['detectability']['E_days_99_126'])}.", "",
             f"Integrity: {r['integrity']['issues'] or 'clean'}.", "",
             "| | L8 (lesson-only researcher) | fixed comparator |", "|---|---|---|"]
    rows = [("experiments used", lambda a: a["experiments_used"]),
            ("first experiment E entered", first),
            ("E tested after the change (as a covariate, rounds 2-3)",
             lambda a: _yn(a["tested_post_change"]) + (f" ({a['first_post_change_test']})" if a["tested_post_change"]
                                                       else "")),
            ("E distinguished from its companions (E the only covariate, lower bound > 0)",
             lambda a: _yn(a["distinguished"])),
            ("supporting evidence of its own (criterion 5)", lambda a: ", ".join(a["supporting_evidence"]) or "none"),
            ("final selection", lambda a: named(a["final_selection"])),
            ("R removed", lambda a: _yn(not a["r_selected"])),
            ("noise selected", lambda a: named(a["noise_selected"]) if a["noise_selected"] else "none"),
            ("D selected", lambda a: _yn(a["d_selected"])),
            ("criteria 1-6", _criteria), ("SUCCESS", lambda a: "**yes**" if a["success"] else "no")]
    lines += [f"| {name} | {fn(l8)} | {fn(cp)} |" for name, fn in rows]
    sels = r["confirmation_selections"]

    def conf(who, inst):
        a = r[who]
        if not a["final_selection"]:
            return "empty selection"
        return _pct(sels[who][inst]) if a["selection_scored"] else "not scored (more than 4 candidates)"
    lines += [f"| final selection vs {{}} on days 127-154 (t0-beta) | {conf('L8', 't0')} | {conf('comparator', 't0')} |",
              f"| same, ridge (context only) | {conf('L8', 'ridge')} | {conf('comparator', 'ridge')} |", ""]
    d = t["roles"]["D"]
    lines += [f"D ({d}): L8 final status {l8['final_status'].get(d)}; L8 experiments including D: "
              + ("; ".join(f"{x['id']} {x['covariates']} vs {x['reference']} {_pct(x)}" for x in l8["d_experiments"])
                 or "none")
              + f". On confirmation, D alone {_pct(r['confirmation']['{D} vs {}']['t0'])}, D given E "
              f"{_pct(r['confirmation']['D given E ({E, D} vs {E})']['t0'])}.", ""]
    lines += [f"L8 re-opened stale negatives: " + ("; ".join(f"{x['candidate']} ({role_of[x['candidate']]}) in "
                                                           f"{x['experiment']}" for x in l8["reopened"]) or "none")
              + f". Lesson mentions: {len(l8['lesson_mentions'])}. Tokens {l8['cost']['tokens_used']}; API attempts "
              f"{l8['cost']['api_attempts']} (repairs {l8['cost']['repairs']}, refusals {l8['cost']['refusals']}).", ""]
    lines += ["### L8 trajectory", ""] + _trajectory(l8, role_of)
    lines += ["### Comparator", "", f"Winning group in round 2: {named(cp['winner'] or [])}.", ""]
    lines += [f"- {x['id']} (round {x['round']}): {named(x['covariates'])} vs none, {x['window_days']} days -> {_pct(x)}"
              for x in cp["experiments"]]
    lines += ["", "### Confirmation (days 127-154)", "", "| comparison | t0-beta | ridge (context) |", "|---|---|---|"]
    lines += [f"| {name} | {_pct(c['t0'])} | {_pct(c['ridge'])} |" for name, c in r["confirmation"].items()]
    lines.append("")
    return lines


def report(rec: dict) -> str:
    lines = [f"# Discovery1 three-world result: {rec['reading']}", "", f"Reading {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"discovery1_spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; instrument "
             f"{rec['instrument'].get('repo')} @ {rec['instrument'].get('served_revision')} (tfc-t0 "
             f"{rec['instrument'].get('tfc_t0')}); lesson sha256 `{rec['lesson_sha256']}`.", "",
             f"Integrity: {rec['integrity_issues'] or 'clean'}. L8 call failures: {rec['call_failures'] or 'none'}.", "",
             "| world | informative | L8 success | L8 criteria 1-6 | comparator success | comparator criteria 1-6 |",
             "|---|---|---|---|---|---|"]
    for k, r in rec["worlds"].items():
        lines.append(f"| {k} | {_yn(r['informative'])} | {_yn(r['L8']['success'])} | {_criteria(r['L8'])} | "
                     f"{_yn(r['comparator']['success'])} | {_criteria(r['comparator'])} |")
    lines += ["", f"Closing line (predeclared): {rec['closing_line']}", ""]
    for k, r in rec["worlds"].items():
        lines += _world_report(k, r)
    lines += ["## Cost", ""]
    for k, r in rec["worlds"].items():
        c = r["L8"]["cost"]
        lines.append(f"- {k}: L8 tokens {c['tokens_used']} ({c['usage_total']}); API attempts {c['api_attempts']}; "
                     f"t0-beta forecasts: L8 {r['t0_beta_forecasts']['research_L8']}, comparator "
                     f"{r['t0_beta_forecasts']['research_comparator']}, evaluate {r['t0_beta_forecasts']['evaluate']}.")
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
