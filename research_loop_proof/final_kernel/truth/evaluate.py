"""The final-kernel evaluator (FINAL_KERNEL_SPEC.md sections 5-10): integrity, memory recomputation, K/F separation,
informativeness, the referee's findings, scoring, the secondary K-versus-F diagnostic, the transfer descriptives,
economics and the programme reading, from the published research records and memory artifacts and the worlds
regenerated from their seeds.

The truth (roles, useful/stale/irrelevant candidates) is used only here, only for scoring. The findings scored are the
referee's (``lab/referee.py``) recomputed here from each record with t0-beta on the holdout data; the shipped memory
artifacts must match that recomputation (ids, configurations, granularity and statuses exactly; numbers within 1e-4).

    python -m research_loop_proof.final_kernel.truth.evaluate --run-id ID --observed D --holdout D --research D \
        --memory D --weights D --out D --job-result e1_c1=success ...
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.evaluate import call_failures
from research_loop_proof.discovery1.lab.executor import Lab8
from research_loop_proof.discovery1.truth.evaluate import cost
from research_loop_proof.discovery1.truth.world import make_world8
from research_loop_proof.final_kernel.lab import referee as ref
from research_loop_proof.final_kernel.lab.researcher import data_block, rebuild_mismatches_fk
from research_loop_proof.final_kernel.truth import rules
from research_loop_proof.final_kernel.truth.observe import RUN_PHASE, designs, ep_key
from research_loop_proof.final_kernel.truth.spec import spec_sha
from research_loop_proof.final_kernel.truth.world import (EPISODES, SCORED_EPISODES, SEQUENCES, episode_context,
                                                          episode_world)
from research_loop_proof.kernel1.truth import evaluate as k1
from research_loop_proof.kernel1.truth.world import effect_scale, unobserved
from research_loop_proof.learn1.lab.researcher import LESSON_FILE, frozen_lesson
from research_loop_proof.learn1.truth.evaluate import _pct
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays

PB = WORLD["phase_b"]
H = WORLD["hours_per_day"]
OBS_LAST = PB["observed_days"][1]
L8_SYSTEM_SHA256 = k1.L8_SYSTEM_SHA256
LESSON_SHA256 = k1.LESSON_SHA256
DETECT_WINDOWS = ((14, 84), (14, 112), (14, 126), (28, 84), (28, 112), (28, 126))
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "timing.json")
CAVEATS = ["Four synthetic companies, eight scored episodes, one stochastic trajectory per condition and episode.",
           "Synthetic worlds from one generator family: a pass does not establish real-market performance or "
           "commercial value; 'proven' means demonstrated against this frozen benchmark at its thresholds.",
           "The benchmark tests predictive information, not causal identification, and does not measure the full "
           "human or engineering cost of a conventional workflow."]
MEMORY_WORDS = re.compile(r"\bM\d+\b|memory|earlier finding|earlier investigation|study period [12]\b", re.I)


def job_name(company: str, episode: int, condition: str) -> str:
    return f"e1_{company}" if episode == 1 else f"e{episode}{condition.lower()}_{company}"


def jobs_of(companies) -> list[tuple[str, str, int, str]]:
    out = []
    for c in companies:
        out.append((job_name(c, 1, "E1"), c, 1, "E1"))
        for e in SCORED_EPISODES:
            for cond in ("F", "K"):
                out.append((job_name(c, e, cond), c, e, cond))
    return out


class Holdout:
    """Holdout confirmations (days 127-154, cutoff 154, 28-day window) with t0-beta on one episode's full data."""

    def __init__(self, w: World, model):
        self.t0 = t0_beta.BetaT0(model)
        self.lab = Lab8(observed_arrays(w, w.n_days), self.t0)

    def __call__(self, cov, refs):
        req = {"covariates": sorted(cov), "reference": sorted(refs), "window_days": ref.CONFIRMATION["window_days"]}
        return self.lab.run(req, ref.CONFIRMATION["cutoff"], "confirmation")


# ----------------------------------------------------------------- informativeness (world and instrument only)

def eligible_sets(useful: list[str]) -> dict:
    if not useful:
        return {}
    sets = {"{" + u + "}": [u] for u in useful}
    if len(useful) == 2:
        sets["{" + ", ".join(useful) + "}"] = list(useful)
    return sets


def informativeness(w: World, useful: list[str], model, confirm: Holdout) -> dict:
    """A truth-eligible current set is detectable when one of its non-indicative legal research windows (14 or 28
    days at cutoff 84, 112 or 126) has lower bound > 0, and confirms when its holdout lower bound is > 0."""
    if not useful:
        return {"informative": None, "sets": {}, "oracle": None, "oracle_ids": None, "oracle_skill": None,
                "t0_forecasts": 0}
    inst = t0_beta.BetaT0(model)
    lab = Lab8(observed_arrays(w, OBS_LAST), inst)
    sets = {}
    for label, ids in eligible_sets(useful).items():
        det = {f"{win} days to day {cut}": _row(lab.run({"covariates": ids, "reference": [], "window_days": win},
                                                        cut, "detect")) for win, cut in DETECT_WINDOWS}
        conf = _row(confirm(ids, []))
        sets[label] = {"ids": ids, "detect": det, "detected": any(r["lo95"] > 0 for r in det.values()),
                       "confirmation": conf, "passes": any(r["lo95"] > 0 for r in det.values()) and conf["lo95"] > 0}
    cands = {k: {**v["confirmation"], "size": len(v["ids"]), "ids": v["ids"]} for k, v in sets.items()}
    best = rules.oracle(cands)
    return {"informative": any(v["passes"] for v in sets.values()), "sets": sets, "oracle": best,
            "oracle_ids": cands[best]["ids"] if best else None,
            "oracle_skill": cands[best]["skill"] if best else None, "t0_forecasts": inst.rows}


# ----------------------------------------------------------------- integrity

def record_integrity(job: str, condition: str, w: World, research_dir: Path, job_result: str, *, expected: dict,
                     canaries: list[str], model) -> dict:
    """Material issues, the reason a valid final response is missing (if it is), and notes, for one record."""
    p = f"{job}: "
    material, notes, info, no_final = [], [], {}, None
    guard = json.loads((research_dir / "guard.json").read_text()) if (research_dir / "guard.json").is_file() else {}
    info["guard"] = guard
    guard_ok = guard.get("truth_absent") is True and str(guard.get("run_attempt")) == "1"
    if guard.get("truth_absent") is not True:
        material.append(p + "the guard did not confirm that the truth was absent from the research job")
    elif str(guard.get("run_attempt")) != "1":
        material.append(p + f"the research record comes from run attempt {guard.get('run_attempt')!r}, not 1")
    if job_result != "success":
        notes.append(f"the research job ended with '{job_result}'")
    texts = [f.read_text(encoding="utf-8", errors="replace") for f in research_dir.rglob("*") if f.is_file()] \
        if research_dir.is_dir() else []
    if any(cn in t for cn in canaries for t in texts):
        material.append(p + "canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    if not (research_dir / "ai.json").is_file():
        return {"material": material, "no_final": f"no research record (job '{job_result}'"
                + (", guard confirmed)" if guard_ok else ")"), "notes": notes, **info}
    failure = json.loads((research_dir / "integrity.json").read_text()).get("failure") \
        if (research_dir / "integrity.json").is_file() else {"kind": "missing", "error": "no integrity.json"}
    info["failure"] = failure
    if failure:
        if failure.get("kind") == "integrity" and str(failure.get("error", "")).startswith(rules.OUTAGE_PREFIX):
            no_final = f"API outage after the retries ({failure['error']})"
        else:
            material.append(p + f"research job {failure.get('kind')}: {failure.get('error')}")
    ai = json.loads((research_dir / "ai.json").read_text())
    calls = ai.get("calls", [])
    inputs = ai.get("inputs") or {}
    info["inputs"] = inputs
    if ai.get("condition") != condition or inputs.get("condition") != condition:
        material.append(p + f"the record is condition {ai.get('condition')!r}, expected {condition!r}")
    for k in ("observed_sha256", "context_sha256", "memory_sha256"):
        if inputs.get(k) != expected[k]:
            material.append(p + f"{k} {inputs.get(k)} differs from the expected {expected[k]}")
    if calls and (ai.get("system_sha256") != L8_SYSTEM_SHA256 or sha256_text(ai.get("system_text") or "")
                  != L8_SYSTEM_SHA256):
        material.append(p + "the system text is not the frozen L8 text")
    try:
        mism = rebuild_mismatches_fk(calls, expected["data_block"])
    except Exception as exc:  # a record that cannot be replayed is a mismatch, never a crash
        mism = [f"rebuild failed ({type(exc).__name__})"]
    if mism:
        material.append(p + "prompt-rebuild mismatch: " + ", ".join(mism))
    attempts = [a for c in calls for a in c.get("attempts", [])]
    if any(a.get("served_model_sha256") not in (None, RESEARCHER["model_sha256"]) or
           a.get("requested_model_sha256") not in (None, RESEARCHER["model_sha256"]) for a in attempts):
        material.append(p + "researcher-model hash mismatch")
    inst = t0_beta.BetaT0(model)
    lab = Lab8(observed_arrays(w, OBS_LAST), inst)
    bad = []
    for c in calls:
        for e in c.get("experiments", []):
            try:
                again = lab.run(e["request"], c["cutoff"], e["id"])
            except ValueError:
                bad.append(e["id"])
                continue
            if any(not _close(again[key], e["result"].get(key)) for key in again):
                bad.append(e["id"])
    info["experiments_recomputed"] = sum(len(c.get("experiments", [])) for c in calls)
    if bad:
        material.append(p + "experiment results differ when recomputed from the observed data: " + ", ".join(bad))
    poisoned, rows = k1.poison_mismatches(w, calls, model)
    info["poison_tests"] = {"experiments": info["experiments_recomputed"], "poisons": list(k1.POISONS),
                            "mismatches": poisoned}
    if poisoned:
        material.append(p + "results change when the data after the cutoff is poisoned: " + ", ".join(poisoned))
    info["t0_forecasts"] = inst.rows + rows
    if no_final is None and not ai.get("final_valid"):
        no_final = "the final call ended without a valid response after its repair"
    return {"material": material, "no_final": no_final, "notes": notes, **info}


def generator_defects(d: dict, episode: int, w: World, truth: dict) -> list[str]:
    """The frozen construction, recomputed from make_world8: the target minus the useful source's effect (or z_U)
    equals make_world8's target minus both of its effects."""
    b = make_world8(truth["seed"])
    errs = []
    if w.tau != b.tau or any(not np.array_equal(w.x[r], b.x[r]) for r in b.x):
        errs.append("candidates or change day differ from make_world8")
    c = effect_scale(b.m)
    z = {r: b.signs[r] * b.x[r] for r in b.x}
    before = np.arange(b.n_days * H) < (b.tau - 1) * H
    plan = truth["plan"]
    if plan["useful_source"] is None:
        driver = unobserved(truth["seed"], b.n_days, b.tau)
    else:
        driver = z[truth["roles"][d["x_ids"][plan["useful_source"]]]]
    if not np.allclose(w.y - c * driver, b.y - c * np.where(before, z["R"], z["E"]), rtol=0, atol=1e-9):
        errs.append("the target does not follow its frozen construction")
    return errs


# ----------------------------------------------------------------- descriptive measures

def transfer(memory: list[dict], exps: list[dict], record: dict, report: dict, regime: str) -> dict:
    """How K's episode related to its memory (descriptive): prior positives used in its first call, stale negatives
    reopened, stable negatives left untested, stale positives abandoned, prior unresolved sets resolved, and memory
    mentioned in its texts."""
    pos = {x for m in memory if m["status"] == "positive" for x in m["covariates"]}
    neg = {x for m in memory if m["status"] in ("negative", "deteriorated") for x in m["covariates"]}
    neg_same = {x for m in memory if m["status"] in ("negative", "deteriorated") and m["regime"] == regime
                for x in m["covariates"]} - pos
    neg_other = {x for m in memory if m["status"] in ("negative", "deteriorated") and m["regime"] != regime
                 for x in m["covariates"]} - pos
    pos_other = {x for m in memory if m["status"] == "positive" and m["regime"] != regime for x in m["covariates"]}
    tested = {x for e in exps for x in e["request"]["covariates"]}
    first_call = {x for e in exps if e["call"] == 1 for x in e["request"]["covariates"]}
    approved_single = {c["covariates"][0] for c in rules.individual_approvals(report)}
    selected = set(record.get("final_selection") or [])
    sets = [m for m in memory if m["status"] == "positive" and len(m["covariates"]) > 1]
    resolved = [m["id"] for m in sets if any(len(e["request"]["covariates"]) == 1 and e["request"]["covariates"][0]
                                             in m["covariates"] for e in exps)]
    texts = []
    for c in record.get("calls", []):
        r = c.get("response") or {}
        texts += [r.get("notes", ""), r.get("conclusion", "")] + [b.get("reason", "") for b in r.get("beliefs", [])]
        texts += [e["request"].get("because", "") for e in c.get("experiments", [])]
    mentions = sum(1 for t in texts if MEMORY_WORDS.search(t or ""))
    out = {"memory_entries": len(memory), "prior_positive_used": sorted(pos & first_call),
           "stale_negative_reopened": sorted(neg_other & tested), "stable_negative_avoided": sorted(neg_same - tested),
           "stale_positive_abandoned": sorted(pos_other - approved_single - selected),
           "prior_unresolved_resolved": resolved, "memory_mentions": mentions,
           "negatives_in_memory": sorted(neg)}
    out["memory_ignored"] = bool(memory) and not (out["prior_positive_used"] or out["stale_negative_reopened"]
                                                 or out["prior_unresolved_resolved"] or mentions)
    return out


def _sentences_naming_candidates(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;!?])\s+", text or "") if re.search(r"\bX0[1-8]\b", s)]


# ----------------------------------------------------------------- run

def _load_memory(d: Path) -> dict:
    if not (d / "memory.json").is_file():
        return {"present": False, "memory": None, "text": None}
    return {"present": True, "memory": json.loads((d / "memory.json").read_text()),
            "text": (d / "memory.txt").read_text(encoding="utf-8") if (d / "memory.txt").is_file() else None,
            "referee": json.loads((d / "referee.json").read_text()) if (d / "referee.json").is_file() else None}


def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    obs_root, hold_root = Path(args.observed), Path(args.holdout)
    res_root, mem_root = Path(args.research), Path(args.memory)
    from research_loop_proof.beta1.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    ds = designs("run", args.run_id)
    results = dict(x.split("=", 1) for x in args.job_result or [])
    material, defects, missing_scored = [], [], []
    worlds, contexts, truths, holdouts, epinfo = {}, {}, {}, {}, {}
    for c, d in ds.items():
        for e in EPISODES:
            key = ep_key(c, e)
            w, t = episode_world(d, e)
            ctx = episode_context(d, e)
            worlds[key], truths[key], contexts[key] = w, t, ctx
            holdouts[key] = Holdout(w, model)
            od, hd = obs_root / key, hold_root / key
            exp_obs = arrays_sha256(observed_arrays(w, OBS_LAST))
            exp_hold = arrays_sha256(observed_arrays(w, w.n_days))
            exp_ctx = sha256_text(ctx["text"])
            shipped = {"observed": arrays_sha256(load_observed(od / "observed.npz")) if (od / "observed.npz").is_file()
                       else None,
                       "declared": json.loads((od / "observed.json").read_text()).get("arrays_sha256")
                       if (od / "observed.json").is_file() else None,
                       "context": sha256_text((od / "context.txt").read_text(encoding="utf-8"))
                       if (od / "context.txt").is_file() else None,
                       "holdout": arrays_sha256(load_observed(hd / "holdout.npz")) if (hd / "holdout.npz").is_file()
                       else None}
            if not exp_obs == shipped["observed"] == shipped["declared"]:
                material.append(f"{key}: observed-data hash mismatch")
            if shipped["context"] != exp_ctx:
                material.append(f"{key}: context differs from its regeneration")
            if shipped["holdout"] != exp_hold:
                material.append(f"{key}: holdout-data hash mismatch")
            defects += [f"{key}: {x}" for x in generator_defects(d, e, w, t)]
            epinfo[key] = {"observed_sha256": exp_obs, "context_sha256": exp_ctx, "holdout_sha256": exp_hold}
    seqs = Counter(d["sequence"] for d in ds.values())
    if sorted(seqs) != sorted(SEQUENCES) or set(seqs.values()) != {1}:
        defects.append(f"sequence assignment {dict(seqs)} is not one company per sequence")
    patterns = Counter(SEQUENCES[d["sequence"]][e - 1][2] for d in ds.values() for e in SCORED_EPISODES)
    if patterns != Counter({"P1": 2, "P2": 2, "P3": 2, "P4": 2}):
        defects.append(f"scored patterns {dict(patterns)} are not 2 of each")
    if sha256_text(frozen_lesson()) != LESSON_SHA256:
        material.append("the lesson does not match its pinned sha256")
    canaries = [w.canary for w in worlds.values()]
    # memory: recompute after E1 and after E2-K, compare with the shipped artifacts
    memories, memory_checks = {}, {}
    records = {}
    for job, c, e, cond in jobs_of(ds):
        p = res_root / job / "ai.json"
        records[job] = json.loads(p.read_text()) if p.is_file() else None
    for c, d in ds.items():
        prev: list = []
        for stage, job in ((1, job_name(c, 1, "E1")), (2, job_name(c, 2, "K"))):
            key = ep_key(c, stage)
            ctx = contexts[key]
            shipped = _load_memory(mem_root / f"{c}-e{stage}")
            rec = records[job]
            if rec is None:
                recomputed = list(prev)
                rep = None
            else:
                rep = ref.adjudicate(rec, holdouts[key])
                recomputed = ref.extend_memory(prev, rep, company=c, episode=stage, regime=ctx["regime"],
                                               names=ctx["names"])
            check = {"present": shipped["present"]}
            if not shipped["present"]:
                check["differences"] = ["memory artifact missing"]
            else:
                check["differences"] = ref.memory_differences(shipped["memory"], recomputed)
                if shipped["text"] != ref.render_memory(shipped["memory"]):
                    check["differences"].append("memory.txt is not the rendering of memory.json")
                for m in shipped["memory"]:
                    if any(cn in json.dumps(m) for cn in canaries):
                        check["differences"].append(f"{m.get('id')}: canary in memory")
            if check["differences"]:
                material.append(f"{c}: memory after study period {stage} differs from its recomputation: "
                                + "; ".join(check["differences"]))
            memory_checks[f"{c}-e{stage}"] = check
            memories[(c, stage)] = shipped if shipped["present"] else {"memory": recomputed,
                                                                          "text": ref.render_memory(recomputed)}
            prev = shipped["memory"] if shipped["present"] else recomputed
    # per record
    recs = {}
    for job, c, e, cond in jobs_of(ds):
        key = ep_key(c, e)
        ctx = contexts[key]
        mem = memories.get((c, e - 1)) if cond == "K" else None
        mem_text = (mem or {}).get("text") or ""
        expected = {"observed_sha256": epinfo[key]["observed_sha256"], "context_sha256": epinfo[key]["context_sha256"],
                    "memory_sha256": sha256_text(mem_text) if cond == "K" else None,
                    "data_block": data_block(ctx["text"], mem_text if cond == "K" else "")}
        integ = record_integrity(job, cond, worlds[key], res_root / job, results.get(job, "missing"),
                                 expected=expected, canaries=canaries, model=model)
        material += integ["material"]
        rec = records[job] or {}
        final_valid = bool(rec.get("final_valid")) and integ["no_final"] is None
        if not final_valid and e in SCORED_EPISODES:
            missing_scored.append(job)
        recs[job] = {"job": job, "company": c, "episode": e, "condition": cond, "record": rec,
                     "integrity": integ, "final_valid": final_valid,
                     "memory_entries": len((mem or {}).get("memory") or []) if cond == "K" else 0}
    # scoring
    episodes, pairs = {}, {}
    for c, d in ds.items():
        for e in EPISODES:
            key = ep_key(c, e)
            t = truths[key]
            inf = informativeness(worlds[key], t["useful"], model, holdouts[key])
            conds = ("E1",) if e == 1 else ("F", "K")
            per = {}
            for cond in conds:
                job = job_name(c, e, cond)
                r = recs[job]
                rec = r["record"]
                report = ref.adjudicate(rec, holdouts[key]) if rec.get("calls") else \
                    {"experiments": 0, "configurations": [], "approved_positive": [], "headline": None, "selection": None}
                exps = ref.experiments(rec) if rec.get("calls") else []
                prefixes, n = [], 0
                for call in (rec.get("calls") or []):
                    if call.get("final"):
                        continue
                    n += len(call.get("experiments", []))
                    prefixes.append((n, ref.adjudicate(rec, holdouts[key], calls_limit=call["call"],
                                                       with_selection=False)))
                null = t["plan"]["useful_source"] is None
                st = rules.strong(report, t["useful"], inf["informative"]) if not null else None
                nu = rules.null_success(report, rec) if null else None
                if not r["final_valid"]:
                    if st:
                        st = {**st, "strong": False, "partial": False, "failed": st["failed"] + ["final response"]}
                    if nu:
                        nu = {**nu, "success": False}
                head = report["headline"]
                frac = None
                if not null and head and inf["oracle_skill"]:
                    frac = rules.oracle_fraction(_row(holdouts[key](head["covariates"], []))["skill"],
                                                 inf["oracle_skill"])
                incorrect = rules.incorrect_approvals(report, t["useful"])
                mem = memories.get((c, e - 1), {}).get("memory") if cond == "K" else []
                final = (rec.get("calls") or [{}])[-1]
                per[cond] = {
                    "job": job, "final_valid": r["final_valid"], "integrity": r["integrity"],
                    "experiments": [{"id": x["id"], "call": x["call"], "covariates": x["request"]["covariates"],
                                     "reference": x["request"]["reference"], "window_days": x["request"]["window_days"],
                                     "scored_days": x["result"]["scored_days"], "skill": x["result"]["skill"],
                                     "lo95": x["result"]["lo95"], "hi95": x["result"]["hi95"],
                                     "because": x["request"]["because"]} for x in exps],
                    "experiments_used": len(exps), "report": report,
                    "final_selection": rec.get("final_selection") if r["final_valid"] else None,
                    "final_status": ({b["candidate"]: b["status"] for b in final["response"]["beliefs"]}
                                     if r["final_valid"] else {}),
                    "conclusion": rec.get("conclusion") if r["final_valid"] else None,
                    "conclusion_sentences_naming_candidates": _sentences_naming_candidates(rec.get("conclusion"))
                    if r["final_valid"] else [],
                    "strong": st, "null": nu,
                    "discovery_index": rules.discovery_index(prefixes, t["useful"]) if not null else None,
                    "oracle_fraction": frac,
                    "incorrect": [x["covariates"] + x["reference"] for x in incorrect],
                    "transfer": transfer(mem or [], exps, rec, report, contexts[key]["regime"]) if cond == "K"
                    else None,
                    "call_failures": call_failures(rec) if rec.get("calls") else ["no calls recorded"],
                    "cost": cost(rec) if rec.get("calls") else {},
                    "timing": json.loads((res_root / job / "timing.json").read_text())
                    if (res_root / job / "timing.json").is_file() else None,
                    "t0_forecasts": rec.get("t0_forecasts")}
            episodes[key] = {"company": c, "episode": e, "sequence": d["sequence"], "pattern": t["plan"]["pattern"],
                             "regime": contexts[key]["regime"], "null": t["plan"]["useful_source"] is None,
                             "truth": {k: t[k] for k in ("useful", "stale", "irrelevant", "useful_names", "roles")},
                             "informativeness": inf, "informative": inf["informative"], "conditions": per,
                             "K": per.get("K"), "context_text": contexts[key]["text"]}
            if e in SCORED_EPISODES:
                k_, f_ = per["K"], per["F"]
                ks = {"strong": bool(k_["strong"] and k_["strong"]["strong"]), "index": k_["discovery_index"],
                      "experiments": k_["experiments_used"]}
                fs = {"strong": bool(f_["strong"] and f_["strong"]["strong"]), "index": f_["discovery_index"],
                      "experiments": f_["experiments_used"]}
                outcome, why = rules.pair_outcome(ks, fs)
                pairs[key] = {"outcome": outcome, "why": why, "K": ks, "F": fs,
                              "experiments_saved": fs["experiments"] - ks["experiments"],
                              "earlier_by": (fs["index"] - ks["index"]) if ks["index"] and fs["index"] else None}
    scored = {k: v for k, v in episodes.items() if v["episode"] in SCORED_EPISODES}
    prog_eps = {k: {"null": v["null"], "pattern": v["pattern"], "informative": v["informative"],
                    "K": {"strong": v["K"]["strong"] or {"strong": False}, "null": v["K"]["null"] or {"success": False},
                          "incorrect": bool(v["K"]["incorrect"]), "oracle_fraction": v["K"]["oracle_fraction"]}}
                for k, v in scored.items()}
    label, rule = rules.programme(prog_eps, material, defects, missing_scored)
    agg = aggregates(scored, pairs, recs)
    record = {
        "phase": RUN_PHASE, "reading": label, "rule": rule, "closing_line": rules.CLOSING[label], "caveats": CAVEATS,
        "spec_sha": spec_sha(), "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"),
        "instrument": load_record, "lesson_sha256": sha256_text(frozen_lesson()),
        "system_sha256_pinned": L8_SYSTEM_SHA256,
        "designs": {c: {"sequence": d["sequence"], "x_ids": d["x_ids"], "F_A": d["F_A"], "F_O": d["F_O"],
                        "letters": d["letters"]} for c, d in ds.items()},
        "material_integrity_issues": material, "generator_defects": defects, "missing_scored": missing_scored,
        "memory_checks": memory_checks, "episodes": episodes, "pairs": pairs, "aggregates": agg,
        "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False, default=str) + "\n",
                                         encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": RUN_PHASE, "reading": label,
                                                  "closing_line": record["closing_line"], "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report_md(record), encoding="utf-8")
    for job, *_ in jobs_of(ds):
        (out / "research" / job).mkdir(parents=True, exist_ok=True)
        for name in FILES:
            if (res_root / job / name).is_file():
                shutil.copyfile(res_root / job / name, out / "research" / job / name)
    for d in mem_root.iterdir() if mem_root.is_dir() else []:
        (out / "memory" / d.name).mkdir(parents=True, exist_ok=True)
        for f in d.iterdir():
            if f.is_file() and f.name != "MANIFEST.sha256":
                shutil.copyfile(f, out / "memory" / d.name / f.name)
    for key in episodes:
        (out / "context").mkdir(exist_ok=True)
        (out / "context" / f"{key}.txt").write_text(contexts[key]["text"], encoding="utf-8")
    shutil.copyfile(LESSON_FILE, out / "lesson.json")
    return record


def aggregates(scored: dict, pairs: dict, recs: dict) -> dict:
    k = {key: v["K"] for key, v in scored.items()}
    f = {key: v["conditions"]["F"] for key, v in scored.items()}

    def count(per: dict, nulls: bool) -> int:
        if nulls:
            return sum(1 for key, x in per.items() if scored[key]["null"] and x["null"] and x["null"]["success"])
        return sum(1 for key, x in per.items() if not scored[key]["null"] and x["strong"] and x["strong"]["strong"])

    costs = [r["record"] for r in recs.values() if r["record"].get("calls")]
    toks = [cost(c) for c in costs]
    exps = sum(len(ref.experiments(c)) for c in costs)
    validated = sum(sum(1 for a in v["report"]["approved_positive"] if a.get("confirmation") and
                        a["confirmation"]["lo95"] > 0) for ep in scored.values() for v in ep["conditions"].values())
    loop_s = sum((v.get("timing") or {}).get("loop_wall_s", 0) for ep in scored.values()
                 for v in ep["conditions"].values())
    out = {
        "K_strong": count(k, False), "F_strong": count(f, False), "K_null_success": count(k, True),
        "F_null_success": count(f, True),
        "K_partial": sum(1 for x in k.values() if x["strong"] and x["strong"]["partial"]),
        "F_partial": sum(1 for x in f.values() if x["strong"] and x["strong"]["partial"]),
        "K_incorrect_episodes": sorted(key for key, x in k.items() if x["incorrect"]),
        "F_incorrect_episodes": sorted(key for key, x in f.items() if x["incorrect"]),
        "K_oracle_fractions": {key: x["oracle_fraction"] for key, x in k.items() if x["oracle_fraction"] is not None},
        "pair_outcomes": dict(Counter(p["outcome"] for p in pairs.values())),
        "K_discovery_index": {key: x["discovery_index"] for key, x in k.items()},
        "F_discovery_index": {key: x["discovery_index"] for key, x in f.items()},
        "experiments_saved_by_K": sum(p["experiments_saved"] for p in pairs.values()),
        "memory_use": {key: x["transfer"] for key, x in k.items()},
        "tokens_used": sum(t.get("tokens_used") or 0 for t in toks),
        "api_attempts": sum(t.get("api_attempts", 0) for t in toks),
        "refusals": sum(t.get("refusals", 0) for t in toks), "repairs": sum(t.get("repairs", 0) for t in toks),
        "experiments_all_records": exps,
        "t0_forecasts_research": sum(c.get("t0_forecasts") or 0 for c in costs),
        "validated_findings_scored": validated,
        "scored_loop_minutes": round(loop_s / 60, 2),
    }
    out["K_median_oracle_fraction"] = rules.median(list(out["K_oracle_fractions"].values()))
    return out


def _f(v, digits=3) -> str:
    return "-" if v is None else f"{v:.{digits}f}"


def _exp_lines(x: dict) -> list[str]:
    return [f"  - {e['id']} (call {e['call']}): {e['covariates']} | ref {e['reference'] or '-'} | {e['window_days']} d "
            f"days {e['scored_days'][0]}-{e['scored_days'][1]} | {_pct(e)}" for e in x["experiments"]]


def report_md(rec: dict) -> str:
    a = rec["aggregates"]
    lines = [f"# Final kernel result: {rec['reading']}", "", f"Rule: {rec['rule']}", "",
             f"Closing line: {rec['closing_line']}", "",
             f"Spec {rec['spec_sha']}; run {rec['run_id']}; commit {rec['commit']}; lesson {rec['lesson_sha256']}.",
             f"Material integrity issues: {rec['material_integrity_issues'] or 'none'}. Generator defects: "
             f"{rec['generator_defects'] or 'none'}. Missing scored trajectories: {rec['missing_scored'] or 'none'}.",
             "", f"K strong {a['K_strong']} of 6, null success {a['K_null_success']} of 2, partial {a['K_partial']}; "
             f"F strong {a['F_strong']} of 6, null {a['F_null_success']} of 2. K median oracle fraction "
             f"{_f(a['K_median_oracle_fraction'])}. Pairs {a['pair_outcomes']}. Tokens {a['tokens_used']}; attempts "
             f"{a['api_attempts']}; refusals {a['refusals']}; repairs {a['repairs']}; t0 forecasts (research) "
             f"{a['t0_forecasts_research']}; evaluate {rec['elapsed_s']} s.", "", "Caveats: " + " ".join(rec["caveats"]),
             ""]
    for key, ep in rec["episodes"].items():
        lines += [f"## {key} ({ep['sequence']}, {ep['pattern'] or 'E1'}; {'null' if ep['null'] else 'non-null'})", "",
                  f"Regime: {ep['regime']}. Useful: {ep['truth']['useful']} {ep['truth']['useful_names']}; stale "
                  f"{ep['truth']['stale']}. Informative: {ep['informative']}; oracle {ep['informativeness']['oracle']}.",
                  ""]
        for cond, x in ep["conditions"].items():
            head = x["report"]["headline"]
            verdict = (x["null"] and f"null success {x['null']['success']} {x['null']['failed']}") or \
                (x["strong"] and f"strong {x['strong']['strong']} partial {x['strong']['partial']} "
                 f"{x['strong']['failed']}")
            lines += [f"- {cond}: {verdict}; headline "
                      + (f"{head['covariates']} | ref {head['reference'] or '-'} ({head['granularity']}), "
                         f"confirmation {_pct(head['confirmation'])}" if head else "none")
                      + f"; discovery index {x['discovery_index']}; experiments {x['experiments_used']}; oracle "
                      f"fraction {_f(x['oracle_fraction'])}; incorrect approvals {x['incorrect'] or 'none'}; "
                      f"selection {x['final_selection']}"]
            lines += _exp_lines(x)
            if x["transfer"]:
                lines.append(f"  - memory use: {x['transfer']}")
        if key in rec["pairs"]:
            p = rec["pairs"][key]
            lines.append(f"- pair: {p['outcome']} ({p['why']})")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--observed", "--holdout", "--research", "--memory", "--weights", "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--job-result", action="append", help="<job>=<needs.<job>.result>")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"reading": rec["reading"], "rule": rec["rule"], "closing_line": rec["closing_line"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
