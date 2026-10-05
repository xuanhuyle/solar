"""The Kernel1 evaluator (KERNEL1_SPEC.md sections 4-9): integrity, informativeness, support, confirmation, per-world
success and the programme reading for the twelve scored worlds, from the published research records and the worlds
regenerated from their seeds.

Per world:
- integrity: the observed data's hash (regenerated, shipped, declared); the guard (truth absent, first run attempt);
  the research job's failure record; the record's condition and system text (the frozen L8 text, sha pinned from
  Discovery1's scored run); every prompt rebuilt; the served model's hash; every experiment recomputed on the observed
  data and again on the full 154-day data poisoned after its cutoff (+1e6 and NaN); canaries of all twelve worlds.
  Material issues give programme row 1. A missing valid final response is counted separately (more than one such
  world gives row 1; one fails that world): an API outage after the retries, a job ended without a record after a
  confirmed guard, or a final call without a valid response after its repair;
- informativeness (the world and the instrument only): change, E alone vs none lower bound > 0 on days 99-112 or
  99-126 and an oracle set exists; stable, R alone vs none lower bound > 0 on days 57-84, 85-112 or 99-126 and an
  oracle set exists; null worlds are always scored;
- oracle set (confirmation days 127-154): change, the lowest-MAE set among {E}, {D}, {E, D} whose skill vs none has a
  lower bound > 0; stable, {R} if its lower bound > 0. Oracle fraction = the final set's skill / the oracle set's;
- support of the final set by the researcher's own current-regime experiments (rules.support), success (rules.success)
  and the descriptive measures; the programme reading is rules.programme.

    python -m research_loop_proof.kernel1.truth.evaluate --run-id ID --observed D --research D --weights D --out D \
        --job-result w01=success ... --job-result w12=success
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
from research_loop_proof.discovery1.lab.researcher import rebuild_mismatches8, system_text8
from research_loop_proof.discovery1.truth.evaluate import cost
from research_loop_proof.discovery1.truth.world import make_world8
from research_loop_proof.kernel1.truth import rules
from research_loop_proof.kernel1.truth.observe import RUN_PHASE, hidden_world, kinds
from research_loop_proof.kernel1.truth.spec import spec_sha
from research_loop_proof.kernel1.truth.world import (COMPOSITION, H, NOISE, ROLES8, SCORED_WORLDS, effect_scale,
                                                     unobserved)
from research_loop_proof.learn1.lab.researcher import LESSON_FILE, frozen_lesson
from research_loop_proof.learn1.truth.evaluate import _pct, reopened, rounds_table
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import RESEARCHER, sha256_text
from research_loop_proof.phase0.truth.evaluate import RidgeInstrument, _close, _row
from research_loop_proof.phase0.truth.generator import WORLD, World, observed_arrays, seed_of

PB = WORLD["phase_b"]
CONF_FIRST, CONF_LAST = PB["confirmation_days"]
OBS_LAST = PB["observed_days"][1]
L8_SYSTEM_SHA256 = "78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d"  # Discovery1's scored run
LESSON_SHA256 = "1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb"
POISONS = ("shift", "nan")
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "timing.json")
CAVEATS = ["Twelve worlds and one stochastic trajectory of the researcher in each.",
           "Synthetic worlds from one frozen generator family: a pass does not establish real-market performance or "
           "commercial value; 'proven' means demonstrated against this benchmark at the predeclared thresholds.",
           "The benchmark tests predictive information, not causal identification: D (E's proxy) may be selected."]


def _full(w: World) -> dict:
    return {"y": w.y, **{w.ids[r]: w.x[r] for r in ROLES8}}


class Confirmer:
    """Confirmation-day experiments (days 127-154, cutoff 154, the 28-day window) with t0-beta and, as context only,
    ridge, on the full 154-day data of one world."""

    def __init__(self, w: World, model):
        self.t0 = t0_beta.BetaT0(model)
        self.labs = {"t0": Lab8(_full(w), self.t0), "ridge": Lab8(_full(w), RidgeInstrument())}

    def row(self, cov: list[str], ref: list[str]) -> dict:
        req = {"covariates": sorted(cov), "reference": sorted(ref), "window_days": CONF_LAST - CONF_FIRST + 1}
        return {name: _row(lab.run(req, CONF_LAST, "confirmation")) for name, lab in self.labs.items()}


# ----------------------------------------------------------------- informativeness (world and instrument only)

def informativeness(w: World, kind: str, model, confirmer: Confirmer) -> dict:
    roles = {r: w.ids[r] for r in ROLES8}
    obs_t0 = t0_beta.BetaT0(model)
    obs = Lab8(observed_arrays(w, OBS_LAST), obs_t0)
    e, d, r = roles["E"], roles["D"], roles["R"]

    def run(cid: str, win: int, cutoff: int) -> dict:
        return _row(obs.run({"covariates": [cid], "reference": [], "window_days": win}, cutoff, "detect"))

    detect = {}
    if kind == "change":
        detect = {"E alone, days 99-112": run(e, 14, 112), "E alone, days 99-126": run(e, 28, 126)}
    elif kind == "stable":
        detect = {"R alone, days 57-84": run(r, 28, 84), "R alone, days 85-112": run(r, 28, 112),
                  "R alone, days 99-126": run(r, 28, 126)}
    conf = {"{E} vs {}": confirmer.row([e], []), "{D} vs {}": confirmer.row([d], []),
            "{R} vs {}": confirmer.row([r], []), "{E, D} vs {}": confirmer.row([e, d], []),
            "D given E ({E, D} vs {E})": confirmer.row([d], [e]), "E given D ({E, D} vs {D})": confirmer.row([e], [d]),
            "R given E ({E, R} vs {E})": confirmer.row([r], [e])}
    sets = ({"{E}": ([e], "{E} vs {}"), "{D}": ([d], "{D} vs {}"), "{E, D}": ([e, d], "{E, D} vs {}")}
            if kind == "change" else {"{R}": ([r], "{R} vs {}")} if kind == "stable" else {})
    cands = {k: {**conf[row]["t0"], "size": len(ids), "ids": sorted(ids)} for k, (ids, row) in sets.items()}
    best = rules.oracle(cands)
    detected = any(x["lo95"] > 0 for x in detect.values())
    return {"detect": detect, "detected": detected, "confirmation": conf, "oracle_candidates": cands,
            "oracle": best, "oracle_ids": cands[best]["ids"] if best else None,
            "oracle_skill": cands[best]["skill"] if best else None,
            "informative": None if kind == "null" else bool(detected and best is not None),
            "t0_forecasts": obs_t0.rows}


# ----------------------------------------------------------------- integrity

def poison_mismatches(w: World, calls: list[dict], model) -> tuple[list[str], int]:
    """Every experiment re-run on the full 154-day data with the target and all candidates after its call's cutoff
    replaced (+1e6, then NaN): a lab that reads past its cutoff changes its results."""
    bad, rows = [], 0
    full = _full(w)
    for cutoff in sorted({c["cutoff"] for c in calls if c.get("experiments")}):
        exps = [e for c in calls if c["cutoff"] == cutoff for e in c.get("experiments", [])]
        for poison in POISONS:
            arrays = {}
            for key, a in full.items():
                a = np.array(a, dtype="float64")
                a[cutoff * H:] = a[cutoff * H:] + 1e6 if poison == "shift" else np.nan
                arrays[key] = a
            inst = t0_beta.BetaT0(model)
            lab = Lab8(arrays, inst)
            for e in exps:
                try:
                    again = lab.run(e["request"], cutoff, e["id"])
                except ValueError:
                    bad.append(f"{e['id']} ({poison})")
                    continue
                if any(not _close(again[key], e["result"].get(key)) for key in again):
                    bad.append(f"{e['id']} ({poison})")
            rows += inst.rows
    return bad, rows


def integrity(w: World, k: str, observed_dir: Path, research_dir: Path, job_result: str, canaries: list[str],
              model) -> dict:
    """Material issues (programme row 1), the reason a valid final response is missing (if it is), and notes."""
    p = f"{k}: "
    material, notes, info, no_final = [], [], {}, None
    meta = json.loads((observed_dir / "observed.json").read_text()) if (observed_dir / "observed.json").is_file() \
        else {}
    regen = arrays_sha256(observed_arrays(w, OBS_LAST))
    shipped = arrays_sha256(load_observed(observed_dir / "observed.npz")) \
        if (observed_dir / "observed.npz").is_file() else None
    info["observed_sha256"] = {"regenerated": regen, "shipped": shipped, "declared": meta.get("arrays_sha256")}
    if not regen == shipped == meta.get("arrays_sha256"):
        material.append(p + "observed-data hash mismatch (regenerated, shipped, declared)")
    guard = json.loads((research_dir / "guard.json").read_text()) if (research_dir / "guard.json").is_file() else {}
    info["guard"] = guard
    guard_ok = guard.get("truth_absent") is True and str(guard.get("run_attempt")) == "1"
    if guard.get("truth_absent") is not True:
        material.append(p + "the guard did not confirm that the truth was absent from the research job")
    elif str(guard.get("run_attempt")) != "1":
        material.append(p + f"the research record comes from run attempt {guard.get('run_attempt')!r}, not 1")
    if job_result != "success":
        notes.append(f"the research job ended with '{job_result}'")
    if not (research_dir / "ai.json").is_file():
        if guard_ok:
            no_final = f"no research record (job '{job_result}' after a confirmed guard)"
        info["experiments_recomputed"] = 0
        return {"material": material, "no_final": no_final or "no research record", "notes": notes, **info}
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
    if ai.get("condition") != "L":
        material.append(p + f"the record is condition {ai.get('condition')!r}")
    info["system_sha256"] = ai.get("system_sha256")
    if calls and (ai.get("system_sha256") != L8_SYSTEM_SHA256 or ai.get("system_text") != system_text8()
                  or sha256_text(system_text8()) != L8_SYSTEM_SHA256):
        material.append(p + "the system text is not the frozen L8 text")
    try:
        mism = rebuild_mismatches8(calls)
    except Exception as exc:  # a record that cannot be replayed is a mismatch, never a crash
        mism = [f"rebuild failed ({type(exc).__name__})"]
    if mism:
        material.append(p + "prompt-rebuild mismatch: " + ", ".join(mism))
    attempts = [a for c in calls for a in c.get("attempts", [])]
    if any(a.get("served_model_sha256") not in (None, RESEARCHER["model_sha256"]) or
           a.get("requested_model_sha256") not in (None, RESEARCHER["model_sha256"]) for a in attempts):
        material.append(p + "researcher-model hash mismatch")
    obs_t0 = t0_beta.BetaT0(model)
    lab = Lab8(observed_arrays(w, OBS_LAST), obs_t0)
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
    poisoned, rows = poison_mismatches(w, calls, model)
    info["poison_tests"] = {"experiments": info["experiments_recomputed"], "poisons": list(POISONS),
                            "mismatches": poisoned}
    if poisoned:
        material.append(p + "results change when the data after the cutoff is poisoned: " + ", ".join(poisoned))
    texts = [f.read_text(encoding="utf-8", errors="replace") for f in research_dir.rglob("*") if f.is_file()]
    if any(cn in t for cn in canaries for t in texts):
        material.append(p + "canary found in the research record")
    info["canary_scanned_files"] = len(texts)
    info["t0_forecasts"] = obs_t0.rows + rows
    if no_final is None and not ai.get("final_valid"):
        no_final = "the final call ended without a valid response after its repair"
    return {"material": material, "no_final": no_final, "notes": notes, **info}


def generator_defects(w: World, kind: str) -> list[str]:
    """The frozen kind identities, recomputed from make_world8 (a failure is a confirmed generator defect)."""
    b = make_world8(w.seed)
    errs = []
    if w.tau != b.tau or w.ids != b.ids or any(not np.array_equal(w.x[r], b.x[r]) for r in ROLES8):
        errs.append("candidates, change day or ids differ from make_world8")
    c = effect_scale(b.m)
    z = {r: b.signs[r] * b.x[r] for r in ("R", "E")}
    before = np.arange(b.n_days * H) < (b.tau - 1) * H
    driver = {"change": np.where(before, z["R"], z["E"]), "stable": z["R"],
              "null": unobserved(w.seed, b.n_days, b.tau)}[kind]
    if not np.allclose(w.y - c * driver, b.y - c * np.where(before, z["R"], z["E"]), rtol=0, atol=1e-9):
        errs.append(f"the {kind} target does not follow its frozen construction")
    return errs


# ----------------------------------------------------------------- descriptive measures

CITE = re.compile(r"\bE([0-9]+)\b")


def cited_failures(calls: list[dict]) -> list[dict]:
    """Later calls citing (in belief cites, reasons, notes, conclusion or a because) an earlier experiment whose lower
    bound was at or below 0."""
    out = []
    for c in calls:
        if not c.get("valid"):
            continue
        failed = {e["id"] for d in calls if d["call"] < c["call"] for e in d.get("experiments", [])
                  if e["result"]["lo95"] <= 0}
        r = c["response"]
        texts = [r.get("notes", ""), r.get("conclusion", "")] + [b.get("reason", "") for b in r["beliefs"]] + \
            [e["request"].get("because", "") for e in c.get("experiments", [])]
        cited = {x for b in r["beliefs"] for x in b.get("cites", [])} | {f"E{m}" for t in texts for m in CITE.findall(t)}
        out += [{"call": c["call"], "experiment": x} for x in sorted(cited & failed)]
    return out


def separation(exps: list[dict]) -> list[str]:
    """Conditional experiments (a non-empty reference) and separation experiments (covariates a proper subset of an
    earlier experiment's multi-candidate covariates)."""
    out = []
    for i, e in enumerate(exps):
        cov = set(e["request"]["covariates"])
        if e["request"]["reference"] or any(cov < set(x["request"]["covariates"]) for x in exps[:i]
                                            if len(x["request"]["covariates"]) > 1):
            out.append(e["id"])
    return out


def _sentences_naming_candidates(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;!?])\s+", text or "") if re.search(r"\bX0[1-8]\b", s)]


def _listing(exps: list[dict], role_of: dict, kind: str, tau: int) -> list[dict]:
    return [{"id": e["id"], "call": e["call"], "round": e["round"],
             "covariates": e["request"]["covariates"], "covariate_roles": [role_of[c] for c in e["request"]["covariates"]],
             "reference": e["request"]["reference"], "reference_roles": [role_of[c] for c in e["request"]["reference"]],
             "window_days": e["request"]["window_days"], "scored_days": e["result"]["scored_days"],
             "skill": e["result"]["skill"], "lo95": e["result"]["lo95"], "hi95": e["result"]["hi95"],
             "current": rules.current(e, kind, tau), "because": e["request"]["because"]} for e in exps]


# ----------------------------------------------------------------- one world

def evaluate_world(k: str, kind: str, w: World, model, observed_dir: Path, research_dir: Path, job_result: str,
                   canaries: list[str]) -> dict:
    roles = {r: w.ids[r] for r in ROLES8}
    role_of = {v: r for r, v in roles.items()}
    confirmer = Confirmer(w, model)
    inf = informativeness(w, kind, model, confirmer)
    integ = integrity(w, k, observed_dir, research_dir, job_result, canaries, model)
    defects = generator_defects(w, kind)
    p = research_dir / "ai.json"
    ai = json.loads(p.read_text()) if p.is_file() else {}
    calls = ai.get("calls", [])
    final_valid = bool(ai.get("final_valid")) and integ["no_final"] is None
    sel = sorted(ai.get("final_selection") or []) if final_valid else None
    statuses = ({b["candidate"]: b["status"] for b in calls[-1]["response"]["beliefs"]} if final_valid else {})
    exps = rules.experiments(ai)
    sup = rules.support(exps, sel, kind, w.tau) if kind != "null" else {"supported": None, "how": None, "chain": []}
    conf_sel = confirmer.row(sel, []) if rules.scorable(sel) else None
    frac = rules.oracle_fraction(conf_sel["t0"]["skill"] if conf_sel else None, inf["oracle_skill"]) \
        if kind != "null" else None
    noise = [roles[n] for n in NOISE]
    succ = rules.success(kind, final_valid=final_valid, informative=inf["informative"], selection=sel, roles=roles,
                         supported=bool(sup["supported"]), confirm_lo95=conf_sel["t0"]["lo95"] if conf_sel else None,
                         fraction=frac or 0.0, statuses=statuses)
    accepted = sorted(c for c, s in statuses.items() if s == "accepted")
    useful = {"change": ("E", "D"), "stable": ("R",), "null": ()}[kind]
    first_useful = next((e["id"] for e in exps if rules.current(e, kind, w.tau)
                         and any(role_of[c] in useful for c in e["request"]["covariates"])), None)
    rounds = rounds_table(calls, w.tau) if calls else []
    if kind != "change":
        for row in rounds:
            for x in row["experiments"]:
                x["relative_to_change"] = "no change in this world"
    return {
        "world": k, "kind": kind, "seed": w.seed,
        "truth": {"roles": roles, "signs": {roles[r]: w.signs[r] for r in ROLES8},
                  "change_day": w.tau if kind == "change" else None, "standardisation_days": [1, w.tau - 1]},
        "integrity": integ, "generator_defects": defects,
        "informativeness": inf, "informative": inf["informative"],
        "final_valid": final_valid, "final_selection": sel,
        "final_selection_roles": [role_of[c] for c in sel] if sel else [],
        "final_status": {f"{c} ({role_of[c]})": s for c, s in statuses.items()},
        "conclusion": ai.get("conclusion") if final_valid else None,
        "conclusion_sentences_naming_candidates": _sentences_naming_candidates(ai.get("conclusion")) if final_valid
        else [],
        "support": sup, "confirmation_selection": conf_sel, "oracle_fraction": frac, "success": succ,
        "accepted": accepted, "noise_selected": [c for c in (sel or []) if c in noise],
        "r_selected": roles["R"] in (sel or []), "e_selected": roles["E"] in (sel or []),
        "d_selected": roles["D"] in (sel or []),
        "r_final_status": statuses.get(roles["R"]),
        "useful_recalled": any(role_of[c] in useful for c in (sel or [])) if useful else None,
        "zero_effect_extras": [c for c in (sel or []) if role_of[c] in ("E", "D")] if kind == "stable" else [],
        "experiments": _listing(exps, role_of, kind, w.tau), "experiments_used": len(exps),
        "exhausted_six": len(exps) == 6, "first_current_useful_experiment": first_useful,
        "conditional_or_separation": separation(exps),
        "reopened": reopened(calls, w.tau) if kind == "change" and calls else [],
        "cited_failed_experiments": cited_failures(calls), "rounds": rounds,
        "call_failures": call_failures(ai) if calls else ["no calls recorded"],
        "cost": cost(ai) if calls else {}, "timing": json.loads((research_dir / "timing.json").read_text())
        if (research_dir / "timing.json").is_file() else None,
        "t0_beta_forecasts": {"research": ai.get("t0_forecasts"),
                              "evaluate": inf["t0_forecasts"] + confirmer.t0.rows + integ.get("t0_forecasts", 0)},
    }


# ----------------------------------------------------------------- run

def aggregates(worlds: dict) -> dict:
    by = {kind: [w for w in worlds.values() if w["kind"] == kind] for kind in ("change", "stable", "null")}
    informative = [w for w in by["change"] + by["stable"] if w["informative"]]
    fractions = [w["oracle_fraction"] for w in informative]
    costs = [w["cost"] for w in worlds.values() if w["cost"]]
    return {
        "change_successes": sum(w["success"]["success"] for w in by["change"]), "change_worlds": len(by["change"]),
        "informative_change": sum(bool(w["informative"]) for w in by["change"]),
        "stable_successes": sum(w["success"]["success"] for w in by["stable"]),
        "null_successes": sum(w["success"]["success"] for w in by["null"]),
        "useful_recalled": {w["world"]: w["useful_recalled"] for w in by["change"] + by["stable"]},
        "r_retained_in_change_worlds": [w["world"] for w in by["change"] if w["r_selected"]],
        "pure_noise_selections": {w["world"]: w["noise_selected"] for w in worlds.values() if w["noise_selected"]},
        "null_false_accepts": {w["world"]: w["accepted"] for w in by["null"]},
        "oracle_fractions": {w["world"]: w["oracle_fraction"] for w in informative},
        "median_oracle_fraction": rules.median(fractions),
        "experiments_used": dict(Counter(w["experiments_used"] for w in worlds.values())),
        "exhausted_six": sum(w["exhausted_six"] for w in worlds.values()),
        "worlds_with_conditional_or_separation": sum(bool(w["conditional_or_separation"]) for w in worlds.values()),
        "change_worlds_reopening_stale_negatives": sum(bool(w["reopened"]) for w in by["change"]),
        "worlds_citing_failed_experiments": sum(bool(w["cited_failed_experiments"]) for w in worlds.values()),
        "tokens_used": sum(c.get("tokens_used") or 0 for c in costs),
        "api_attempts": sum(c.get("api_attempts", 0) for c in costs),
        "refusals": sum(c.get("refusals", 0) for c in costs), "repairs": sum(c.get("repairs", 0) for c in costs),
        "t0_forecasts_research": sum(w["t0_beta_forecasts"]["research"] or 0 for w in worlds.values()),
        "t0_forecasts_evaluate": sum(w["t0_beta_forecasts"]["evaluate"] for w in worlds.values()),
    }


def run(args) -> dict:
    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    observed, research = Path(args.observed), Path(args.research)
    from research_loop_proof.beta1.lab.run import load_t0

    model, load_record = load_t0(Path(args.weights))
    world_kind = kinds(args.run_id)
    gen = {k: hidden_world(args.run_id, k) for k in SCORED_WORLDS}
    canaries = [w.canary for w in gen.values()]
    results = dict(x.split("=", 1) for x in args.job_result or [])
    worlds = {k: evaluate_world(k, world_kind[k], gen[k], model, observed / k, research / k,
                                results.get(k, "missing"), canaries) for k in SCORED_WORLDS}
    material = [x for k in SCORED_WORLDS for x in worlds[k]["integrity"]["material"]]
    defects = [f"{k}: {x}" for k in SCORED_WORLDS for x in worlds[k]["generator_defects"]]
    if sorted(Counter(world_kind.values()).items()) != sorted(COMPOSITION):
        defects.append(f"batch composition {dict(Counter(world_kind.values()))} is not {dict(COMPOSITION)}")
    if sha256_text(frozen_lesson()) != LESSON_SHA256:
        material.append("the lesson does not match its pinned sha256")
    label, rule = rules.programme({k: {"kind": w["kind"], "final_valid": w["final_valid"],
                                       "informative": w["informative"], "success": w["success"]["success"],
                                       "oracle_fraction": w["oracle_fraction"], "noise_selected": w["noise_selected"],
                                       "accepted": w["accepted"]} for k, w in worlds.items()}, material, defects)
    record = {
        "phase": RUN_PHASE, "reading": label, "rule": rule, "closing_line": rules.CLOSING[label], "caveats": CAVEATS,
        "spec_sha": spec_sha(), "run_id": args.run_id, "commit": os.environ.get("GITHUB_SHA"),
        "instrument": load_record, "lesson_sha256": sha256_text(frozen_lesson()),
        "system_sha256_pinned": L8_SYSTEM_SHA256, "system_sha256_frozen_text": sha256_text(system_text8()),
        "composition": dict(Counter(world_kind.values())), "kinds": world_kind,
        "seeds": {k: seed_of(f"kernel1:{spec_sha()}:{args.run_id}:{k}") for k in SCORED_WORLDS},
        "material_integrity_issues": material, "generator_defects": defects,
        "no_final_worlds": {k: w["integrity"]["no_final"] for k, w in worlds.items() if not w["final_valid"]},
        "aggregates": aggregates(worlds), "worlds": worlds, "elapsed_s": round(time.time() - started, 1),
    }
    (out / "evaluation.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps({"phase": RUN_PHASE, "reading": label,
                                                  "closing_line": record["closing_line"], "spec_sha": record["spec_sha"],
                                                  "run_id": args.run_id, "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record), encoding="utf-8")
    for k in SCORED_WORLDS:
        (out / k).mkdir(exist_ok=True)
        for name in FILES + ("observed.json",):
            src = (observed if name == "observed.json" else research) / k / name
            if src.is_file():
                shutil.copyfile(src, out / k / name)
    shutil.copyfile(LESSON_FILE, out / "lesson.json")
    return record


# ----------------------------------------------------------------- report

def _f(v, digits=3) -> str:
    return "-" if v is None else f"{v:.{digits}f}"


def _world_report(k: str, r: dict) -> list[str]:
    roles = r["truth"]["roles"]
    inf = r["informativeness"]
    lines = [f"## {k}: {r['kind']} world, {'SUCCESS' if r['success']['success'] else 'FAILURE'}"
             + ("" if r["success"]["success"] else f" (failed: {', '.join(r['success']['failed'])})"), "",
             f"Roles: {', '.join(f'{role} {cid}' for role, cid in roles.items())}. Change day: "
             f"{r['truth']['change_day'] or 'none (no change in this world)'}.",
             f"Informative: {r['informative'] if r['kind'] != 'null' else 'always scored (null)'}; detection: "
             + ("; ".join(f"{name} {_pct(x)}" for name, x in inf["detect"].items()) or "-")
             + f"; oracle set {inf['oracle'] or 'none'} ({inf['oracle_ids'] or '-'}), skill {_f(inf['oracle_skill'])}.",
             "Confirmation (t0-beta, days 127-154): " + "; ".join(f"{name} {_pct(x['t0'])}"
                                                                  for name, x in inf["confirmation"].items()) + ".",
             "", "| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |",
             "|---|---|---|---|---|---|---|"]
    for x in r["experiments"]:
        lines.append(f"| {x['id']} | {x['call']} | {x['covariates']} ({', '.join(x['covariate_roles'])}) | "
                     f"{x['reference']} ({', '.join(x['reference_roles']) or '-'}) | {x['scored_days'][0]}-"
                     f"{x['scored_days'][1]} | {_pct(x)} | {'yes' if x['current'] else 'no'} |")
    conf = r["confirmation_selection"]
    lines += ["", f"Final selection: {r['final_selection']} ({', '.join(r['final_selection_roles']) or '-'}); valid "
              f"final response: {r['final_valid']}"
              + (f" ({r['integrity']['no_final']})" if r['integrity']['no_final'] else "") + ".",
              f"Final statuses: {r['final_status'] or '-'}.",
              f"Support: {r['support']['supported']} ({r['support']['how'] or '-'}; chain {r['support']['chain']}).",
              f"Confirmation of the selection: {_pct(conf['t0']) if conf else 'not scored'}"
              + (f" (ridge, context only: {_pct(conf['ridge'])})" if conf else "")
              + f"; oracle fraction {_f(r['oracle_fraction'])}.",
              f"R selected {r['r_selected']} (final status {r['r_final_status']}); E selected {r['e_selected']}; D "
              f"selected {r['d_selected']}; pure noise selected {r['noise_selected'] or 'none'}; accepted "
              f"{r['accepted'] or 'none'}.",
              f"First current experiment containing useful information: {r['first_current_useful_experiment']}; "
              f"conditional or separation experiments: {r['conditional_or_separation'] or 'none'}; reopened stale "
              f"negatives: {[x['experiment'] for x in r['reopened']] or 'none'}; cited earlier failed experiments: "
              f"{[x['experiment'] for x in r['cited_failed_experiments']] or 'none'}; experiments used "
              f"{r['experiments_used']}.",
              f"Conclusion (verbatim): {r['conclusion']}",
              f"Cost: {r['cost']}; t0-beta forecasts {r['t0_beta_forecasts']}; timing {r['timing']}.",
              f"Integrity: material {r['integrity']['material'] or 'none'}; notes {r['integrity']['notes'] or 'none'}; "
              f"call failures {r['call_failures'] or 'none'}.", ""]
    return lines


def report(rec: dict) -> str:
    a = rec["aggregates"]
    lines = [f"# Kernel1 twelve-world result: {rec['reading']}", "", f"Rule: {rec['rule']}", "",
             f"Closing line: {rec['closing_line']}", "",
             f"Spec {rec['spec_sha']}; run {rec['run_id']}; commit {rec['commit']}; lesson {rec['lesson_sha256']}; "
             f"L8 system text {rec['system_sha256_frozen_text']} (pinned {rec['system_sha256_pinned']}).",
             f"Composition {rec['composition']}; kinds {rec['kinds']}.",
             f"Material integrity issues: {rec['material_integrity_issues'] or 'none'}. Generator defects: "
             f"{rec['generator_defects'] or 'none'}. Worlds without a valid final response: "
             f"{rec['no_final_worlds'] or 'none'}.", "",
             f"Change successes {a['change_successes']} of {a['change_worlds']} (informative {a['informative_change']}); "
             f"stable {a['stable_successes']} of 2; null {a['null_successes']} of 2; median oracle fraction "
             f"{_f(a['median_oracle_fraction'])} ({a['oracle_fractions']}); pure-noise selections "
             f"{a['pure_noise_selections'] or 'none'}; null false accepts {a['null_false_accepts']}; R retained "
             f"{a['r_retained_in_change_worlds'] or 'none'}.",
             f"Tokens {a['tokens_used']}; attempts {a['api_attempts']}; refusals {a['refusals']}; repairs {a['repairs']}; "
             f"t0-beta forecasts research {a['t0_forecasts_research']}, evaluate {a['t0_forecasts_evaluate']}; "
             f"evaluate {rec['elapsed_s']} s.", "", "Caveats: " + " ".join(rec["caveats"]), ""]
    for k in SCORED_WORLDS:
        lines += _world_report(k, rec["worlds"][k])
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--run-id", "--observed", "--research", "--weights", "--out"):
        ap.add_argument(a, required=True)
    ap.add_argument("--job-result", action="append", help="wNN=<needs.research_wNN.result>")
    rec = run(ap.parse_args(argv))
    print(json.dumps({"reading": rec["reading"], "rule": rec["rule"], "closing_line": rec["closing_line"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
