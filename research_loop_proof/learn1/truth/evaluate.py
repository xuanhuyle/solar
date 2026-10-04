"""The learn1 evaluate step (NEXT_LEARNING_MILESTONE_PROMPT.md sections 9-11): both trajectories on the one world.

It regenerates the hidden world from its seed and checks each condition's record against it, as beta1 did:
- the observed-data hash;
- the condition's system text is exactly the frozen one (F: beta1's; L: beta1's with the lesson section);
- every user and repair prompt rebuilt byte for byte from that condition's own calls (so neither condition's prompts
  carried anything from the other);
- every experiment recomputed from the observed data with t0-beta;
- the canary, the researcher model's hash, the guard and the research jobs' results.

Then it reveals the world, runs the evidence check, scores both final selections on the confirmation days 127-154 with
t0-beta and the matched ridge, tabulates each trajectory round by round, and reads the paired outcome (first match
wins):

1. INFRASTRUCTURE FAILURE: an integrity issue, or a call of either condition without a valid response after its repair.
2. LEARNING SIGNAL OBSERVED: L did better than F (any of (a)-(c)) and the improvement is linked to the lesson:
   (a) L found the emerging driver (E selected, R and N not) and F did not;
   (b) both found it, and L first had positive evidence for E (an experiment including E with a lower bound above 0)
       in an earlier round than F;
   (c) L re-opened a stale negative (a round 2-3 experiment including a candidate every earlier result of which was
       scored before the change with a lower bound at or below 0) and F re-opened none, while F did not find E where
       L missed it;
   linked: L's notes, reasons, because or conclusion mention the lesson ("lesson" or "prior research"), or the
   improvement is a re-opening (c), or L re-opened E itself.
3. BOTH SUCCEED: both trajectories meet beta1's row 3 (BASIC AUTONOMOUS LOOP OBSERVED).
4. BOTH FAIL: neither found the emerging driver.
5. NO LEARNING SIGNAL: anything else.

    python -m research_loop_proof.learn1.truth.evaluate --run-id ID --observed D --research D --weights D --out D
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.evaluate import behaviours, call_failures
from research_loop_proof.beta1.truth.evaluate import verdict as beta1_verdict
from research_loop_proof.learn1.lab.researcher import (CONDITIONS, LESSON_FILE, frozen_lesson, rebuild_mismatches,
                                                       system_text)
from research_loop_proof.learn1.truth.observe import hidden_world
from research_loop_proof.learn1.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import IDS, Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import BUDGET, RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
CAVEATS = ["One world and one trajectory per condition: an existence test, not a rate. The researcher is stochastic, "
           "so a difference between F and L can arise by chance as well as from the lesson.",
           "The outcome reads research behaviour first; a forecasting gain alone is not a learning signal."]
LESSON_WORDS = re.compile(r"\blesson\b|\bprior research\b", re.IGNORECASE)
NO_BEHAVIOUR = {k: False for k in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10")} | {"B3_errors": []}


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
    expected = system_text(condition)
    info["system_sha256"] = ai.get("system_sha256")
    if calls and (ai.get("system_sha256") != sha256_text(expected) or ai.get("system_text") != expected):
        issues.append(p + "the system text is not the frozen text of this condition")
    mism = rebuild_mismatches(calls)
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

def found(selection: list | None, roles: dict) -> bool:
    sel = selection or []
    return roles["E"] in sel and roles["R"] not in sel and roles["N"] not in sel


def first_positive_round(calls: list[dict], cand: str) -> int | None:
    """The first round (2 or 3) with an experiment that includes ``cand`` and has a lower bound above 0."""
    rounds = [c["round"] for c in calls if c.get("round") in (2, 3) for e in c.get("experiments", [])
              if cand in e["request"]["covariates"] and e["result"]["lo95"] > 0]
    return min(rounds) if rounds else None


def _tables(calls: list[dict]) -> dict:
    return {c["call"]: {b["candidate"]: b for b in c["response"]["beliefs"]} for c in calls if c.get("valid")}


def reopened(calls: list[dict], tau: int) -> list[dict]:
    """Round 2-3 experiments re-testing a candidate whose earlier evidence was negative and from before the change:
    it was a covariate in at least one experiment of an earlier call, and every such result was scored entirely
    before the change with a lower bound at or below 0. (A call's belief table is written together with its requests,
    so the status shown is the one the researcher gave in the re-testing call.)"""
    tables, out = _tables(calls), []
    for c in calls:
        if c.get("round") not in (2, 3):
            continue
        earlier = [e["result"] for d in calls if d["call"] < c["call"] for e in d.get("experiments", [])]
        for e in c.get("experiments", []):
            for cand in e["request"]["covariates"]:
                hits = [r for r in earlier if cand in r["covariates"]]
                if hits and all(r["scored_days"][1] < tau and r["lo95"] <= 0 for r in hits):
                    out.append({"round": c["round"], "experiment": e["id"], "candidate": cand,
                                "status_in_call": tables.get(c["call"], {}).get(cand, {}).get("status"),
                                "earlier": [r["id"] for r in hits], "because": e["request"]["because"]})
    return out


def obsolete_retests(calls: list[dict], r_id: str, tau: int) -> list[str]:
    """Experiments testing R alone after an earlier call already had a post-change result for R alone."""
    out = []
    for c in calls:
        post_before = any(e["result"]["covariates"] == [r_id] and e["result"]["scored_days"][1] >= tau
                          for d in calls if d["call"] < c["call"] for e in d.get("experiments", []))
        out += [e["id"] for e in c.get("experiments", []) if e["result"]["covariates"] == [r_id] and post_before]
    return out


def lesson_mentions(calls: list[dict]) -> list[dict]:
    out = []
    for c in calls:
        if not c.get("valid"):
            continue
        r = c["response"]
        fields = [("notes", r["notes"]), ("conclusion", r["conclusion"])]
        fields += [(f"reason {b['candidate']}", b["reason"]) for b in r["beliefs"]]
        fields += [(f"because {e['id']}", e["request"]["because"]) for e in c.get("experiments", [])]
        out += [{"call": c["call"], "field": name, "text": text} for name, text in fields if LESSON_WORDS.search(text)]
    return out


def relative_to_change(scored: list[int], tau: int) -> str:
    return "before" if scored[1] < tau else "after" if scored[0] >= tau else "straddles"


def rounds_table(calls: list[dict], tau: int) -> list[dict]:
    rows, prev, used = [], None, 0
    for c in calls:
        row = {"call": c["call"], "round": c.get("round"), "cutoff": c["cutoff"], "final": c["final"],
               "valid": bool(c.get("valid")), "entering": prev}
        if c.get("valid"):
            r = c["response"]
            now = {b["candidate"]: b["status"] for b in r["beliefs"]}
            row.update(status=now, changes={k: [(prev or {}).get(k), v] for k, v in now.items()
                                            if (prev or {}).get(k) != v}, notes=r["notes"])
            if c["final"]:
                row.update(final_selection=r["final_selection"], conclusion=r["conclusion"])
            prev = now
        else:
            row["errors"] = c.get("errors", [])
        exps = []
        for e in c.get("experiments", []):
            q, res = e["request"], e["result"]
            exps.append({"id": e["id"], "covariates": q["covariates"], "reference": q["reference"],
                         "window_days": q["window_days"], "expect": q["expect"], "because": q["because"],
                         "scored_days": res["scored_days"], "skill": res["skill"], "lo95": res["lo95"],
                         "hi95": res["hi95"], "relative_to_change": relative_to_change(res["scored_days"], tau)})
        used += len(exps)
        row.update(experiments=exps, budget_left=BUDGET["total_experiments"] - used)
        rows.append(row)
    return rows


def analyse(condition: str, ai: dict, roles: dict, tau: int, evidence: dict, issues: list[str],
            confirm_sel: dict | None) -> dict:
    calls = ai.get("calls", [])
    sel = ai.get("final_selection") if ai.get("final_valid") else None
    failures = call_failures(ai)
    beh = behaviours(calls, roles, tau, sel) if calls else dict(NO_BEHAVIOUR)
    reading, rule = beta1_verdict(issues, failures, ai, beh, roles, evidence, confirm_sel)
    attempts = [a for c in calls for a in c["attempts"]]
    usage = [a["usage"] for a in attempts if a.get("usage")]
    return {
        "condition": condition, "final_valid": bool(ai.get("final_valid")), "final_selection": sel,
        "conclusion": ai.get("conclusion"), "call_failures": failures, "behaviours": beh,
        "beta1_reading": {"verdict": reading, "rule": rule},
        "essential_loop": reading == "BASIC AUTONOMOUS LOOP OBSERVED",
        "found": found(sel, roles), "emerging_selected": roles["E"] in (sel or []),
        "retired_removed": roles["R"] not in (sel or []), "noise_avoided": bool(beh["B10"]),
        "first_e_round": first_positive_round(calls, roles["E"]), "reopened": reopened(calls, tau),
        "obsolete_retests": obsolete_retests(calls, roles["R"], tau), "lesson_mentions": lesson_mentions(calls),
        "rounds": rounds_table(calls, tau),
        "cost": {"tokens_used": ai.get("tokens_used"), "api_attempts": len(attempts),
                 "refusals": sum(1 for a in attempts if a.get("stop_reason") == "refusal"),
                 "refusal_categories": sorted({str(a.get("refusal_category")) for a in attempts
                                               if a.get("stop_reason") == "refusal"}),
                 "repairs": sum(1 for a in attempts if a.get("attempt") == 2),
                 "usage_total": {k: sum(u[k] for u in usage) for k in usage[0]} if usage else {},
                 "t0_forecasts": ai.get("t0_forecasts")},
    }


# ----------------------------------------------------------------- the paired outcome

def outcome(issues: list[str], f: dict, l: dict, roles: dict) -> tuple[str, str]:
    failures = [f"F {x}" for x in f["call_failures"]] + [f"L {x}" for x in l["call_failures"]]
    if issues or failures:
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(issues + failures)
    inf = float("inf")
    improved = []
    if l["found"] and not f["found"]:
        improved.append("(a) L found the emerging driver and F did not")
    if l["found"] and f["found"] and (l["first_e_round"] or inf) < (f["first_e_round"] or inf):
        improved.append("(b) both found it; L had positive evidence for it in an earlier round")
    if l["reopened"] and not f["reopened"] and not (f["found"] and not l["found"]):
        improved.append("(c) L re-opened candidates rejected on pre-change evidence and F did not")
    links = []
    if l["lesson_mentions"]:
        links.append("L mentions the lesson (calls " + ", ".join(sorted({str(m["call"]) for m in l["lesson_mentions"]}))
                     + ")")
    if any(x.startswith("(c)") for x in improved):
        links.append("the improvement is a re-opening")
    if any(r["candidate"] == roles["E"] for r in l["reopened"]):
        links.append("L re-opened the emerging driver")
    if improved and links:
        return "LEARNING SIGNAL OBSERVED", "row 2: " + "; ".join(improved) + "; linked: " + "; ".join(links)
    if f["essential_loop"] and l["essential_loop"]:
        return "BOTH SUCCEED", "row 3: both meet beta1's row 3"
    if not f["found"] and not l["found"]:
        return "BOTH FAIL", "row 4: neither found the emerging driver"
    return "NO LEARNING SIGNAL", "row 5" + (": L did better (" + "; ".join(improved) + ") but no link to the lesson "
                                           "was shown" if improved else "")


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
    job_results = {"F": args.research_f_result, "L": args.research_l_result}
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
    shared = [x for x in issues if not x.startswith(("F: ", "L: "))]  # the observed data serve both conditions
    cond_issues = {c: shared + [x for x in issues if x.startswith(f"{c}: ")] for c in CONDITIONS}
    per = {c: analyse(c, ais[c], roles, w.tau, evidence, cond_issues[c], selections[c]) for c in CONDITIONS}
    label, rule = outcome(issues, per["F"], per["L"], roles)
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
        "phase": "learn1-run", "outcome": label, "rule": rule, "caveats": CAVEATS, "spec_sha": spec_sha(),
        "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"), "instrument": load_record,
        "lesson": {"text": lesson, "sha256": sha256_text(lesson)},
        "truth": {"tau": w.tau, "roles": roles, "signs": {roles[r]: w.signs[r] for r in roles}, "form": w.form,
                  "m": w.m},
        "integrity": {"issues": issues, **info}, "evidence_check": evidence, "confirmation": confirmation,
        "confirmation_selections": selections, "conditions": per, "candidates": candidates,
        "t0_beta_forecasts": {"research_F": ais["F"].get("t0_forecasts"), "research_L": ais["L"].get("t0_forecasts"),
                              "evaluate": t0_obs.rows + t0_full.rows},
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": "learn1-run", "outcome": label, "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record), encoding="utf-8")
    for c in CONDITIONS:
        (out / c).mkdir(exist_ok=True)
        for name in ("ai.json", "notebook.jsonl", "integrity.json", "guard.json"):
            if (research / c / name).is_file():
                shutil.copyfile(research / c / name, out / c / name)
    shutil.copyfile(observed_dir / "observed.json", out / "observed.json")
    shutil.copyfile(LESSON_FILE, out / "lesson.json")
    return record


# ----------------------------------------------------------------- report

def _pct(r: dict | None) -> str:
    return "-" if not r else f"{r['skill'] * 100:+.1f}% [{r['lo95'] * 100:+.1f}, {r['hi95'] * 100:+.1f}]"


def _yn(v) -> str:
    return "yes" if v else "no"


def _trajectory(a: dict, role_of: dict) -> list[str]:
    lines = []
    for row in a["rounds"]:
        title = "final call" if row["final"] else f"round {row['round']}"
        lines += [f"#### Call {row['call']} ({title}, days 1-{row['cutoff']}); budget left after it: {row['budget_left']}",
                  ""]
        if row["entering"]:
            lines.append("Entering: " + ", ".join(f"{k} ({role_of[k]}) {v}" for k, v in row["entering"].items()) + ".")
        if not row["valid"]:
            lines += [f"No valid response: {'; '.join(row.get('errors', []))}", ""]
            continue
        for x in row["experiments"]:
            lines.append(f"- {x['id']}: covariates {x['covariates']}, reference {x['reference']}, {x['window_days']} days, "
                         f"expected {x['expect']} -> {_pct(x)} on days {x['scored_days'][0]}-{x['scored_days'][1]} "
                         f"({x['relative_to_change']} the change). Because: {x['because']}")
        if row["changes"]:
            lines.append("Belief changes: " + ", ".join(f"{k} ({role_of[k]}) {o or '-'} -> {n}"
                                                        for k, (o, n) in row["changes"].items()) + ".")
        lines.append(f"Notes: {row['notes']}")
        if row["final"]:
            lines += [f"Final selection: {row['final_selection']}", f"Conclusion: {row['conclusion']}"]
        lines.append("")
    return lines


def report(rec: dict) -> str:
    t = rec["truth"]
    role_of = {v: k for k, v in t["roles"].items()}
    f, l = rec["conditions"]["F"], rec["conditions"]["L"]
    lines = [f"# learn1 paired hidden-world result: {rec['outcome']}", "", f"Outcome {rec['rule']}.", "",
             *[f"- {c}" for c in rec["caveats"]], "",
             f"learn1_spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; instrument "
             f"{rec['instrument'].get('repo')} @ {rec['instrument'].get('served_revision')} (tfc-t0 "
             f"{rec['instrument'].get('tfc_t0')}).", "",
             "## The prior research lesson (condition L only)", "", rec["lesson"]["text"], "",
             f"sha256 `{rec['lesson']['sha256']}`.", "",
             "## Integrity", "", f"Issues: {rec['integrity']['issues'] or 'none'}. Call failures: F "
             f"{f['call_failures'] or 'none'}; L {l['call_failures'] or 'none'}.", "",
             "## Revealed world", "", f"First changed day {t['tau']}. " + ", ".join(
                 f"{r} = {i} (sign {t['signs'][i]:+d})" for r, i in t["roles"].items()) + ".", "",
             "Evidence check (t0-beta, against no covariate):", "",
             f"- R on days 57-84 (before the change): {_pct(rec['evidence_check']['R_days_57_84'])}",
             f"- E on days 99-112 (available in round 2): {_pct(rec['evidence_check']['E_days_99_112'])}",
             f"- E on days 99-126 (available in round 3): {_pct(rec['evidence_check']['E_days_99_126'])}", "",
             "## Side by side", "", "| | F (fresh) | L (lesson) |", "|---|---|---|"]

    def reo(a):
        return "; ".join(f"{r['candidate']} ({role_of[r['candidate']]}) in {r['experiment']}, round {r['round']}"
                         for r in a["reopened"]) or "none"
    rows = [("final selection", lambda a: f"{a['final_selection']}"),
            ("found the emerging driver (E selected, R and N not)", lambda a: _yn(a["found"])),
            ("first round with positive evidence for E", lambda a: a["first_e_round"] or "never"),
            ("re-opened stale negatives", reo),
            ("retired driver removed", lambda a: _yn(a["retired_removed"])),
            ("unsupported noise avoided (B10)", lambda a: _yn(a["noise_avoided"])),
            ("reconfirmations of R after a post-change R result", lambda a: ", ".join(a["obsolete_retests"]) or "none"),
            ("mentions of the lesson", lambda a: len(a["lesson_mentions"])),
            ("beta1 reading", lambda a: a["beta1_reading"]["verdict"]),
            ("behaviours B1-B10", lambda a: " ".join(k for k in NO_BEHAVIOUR if k != "B3_errors" and a["behaviours"][k])),
            ("tokens", lambda a: a["cost"]["tokens_used"])]
    lines += [f"| {name} | {fn(f)} | {fn(l)} |" for name, fn in rows]
    lines.append("")
    if l["lesson_mentions"]:
        lines += ["Where L mentions the lesson:", ""] + [f"- call {m['call']}, {m['field']}: {m['text']}"
                                                        for m in l["lesson_mentions"]] + [""]
    for name, a in (("F (fresh)", f), ("L (lesson)", l)):
        lines += [f"## Trajectory {name}", ""] + _trajectory(a, role_of)
    lines += ["## Candidates", "",
              "| id | role | causal effect | t0-beta alone (127-154) | incremental | F final | F selected | L final | "
              "L selected |", "|---|---|---|---|---|---|---|---|---|"]
    for c in rec["candidates"]:
        lines.append(f"| {c['id']} | {c['role']} | {c['causal']} | {_pct(c['standalone']['t0'])} | "
                     f"{c['incremental_label']}: {_pct(c['incremental']['t0'])} | {c['F_final_status']} | "
                     f"{c['F_selected']} | {c['L_final_status']} | {c['L_selected']} |")
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
    ap.add_argument("--research-f-result", default="success")
    ap.add_argument("--research-l-result", default="success")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"outcome": rec["outcome"], "rule": rec["rule"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
