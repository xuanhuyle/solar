"""The Kernel1 preflight (operational only, no science): one non-scored change world, researched by L8 exactly as the
scored worlds are (KERNEL1_SPEC.md section 9).

It checks execution, schema and integrity only. The checks are beta1's operational rule on L8 (all 4 calls end with a
valid response, no integrity failure, at most 1 refusal), every requested experiment legal over X01-X08 and run (beta1's
own count checks against Phase 0's four ids, so it is recomputed here and the verdict with it), every belief table
enumerating exactly X01-X08, the system text equal to the frozen L8 text, every prompt rebuilt from the record, and the
guard (truth absent, first run attempt). There is no comparator. Its world's roles are never read and nothing is tuned
from it.

    python -m research_loop_proof.kernel1.truth.preflight --research D --observed D --out D   # D/w01
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from research_loop_proof.beta1.truth.preflight import MAX_REFUSALS, PLANNED_CALLS, check
from research_loop_proof.discovery1.lab.executor import IDS8
from research_loop_proof.discovery1.lab.researcher import rebuild_mismatches8, system_text8
from research_loop_proof.kernel1.truth.observe import PREFLIGHT_PHASE
from research_loop_proof.kernel1.truth.spec import spec_sha
from research_loop_proof.kernel1.truth.world import PREFLIGHT_WORLD
from research_loop_proof.phase0.lab.executor import request_errors
from research_loop_proof.phase0.lab.researcher import sha256_text

FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "timing.json")


def check_k1(research: Path) -> dict:
    out = check(research)
    ai = json.loads((research / "ai.json").read_text()) if (research / "ai.json").is_file() else {"calls": []}
    calls = ai.get("calls", [])
    exps = [e for c in calls for e in c.get("experiments", [])]
    out["illegal_experiments"] = sum(1 for e in exps if request_errors(e["request"], IDS8) or "result" not in e)
    out["enumeration_ok"] = bool(calls) and all(
        sorted(b["candidate"] for b in c["response"]["beliefs"]) == list(IDS8) for c in calls if c.get("valid"))
    out["system_text_ok"] = ai.get("system_text") == system_text8() and ai.get("system_sha256") == sha256_text(
        system_text8())
    try:
        out["prompt_rebuild_mismatches"] = rebuild_mismatches8(calls) if calls else ["no calls"]
    except Exception as exc:  # a record that cannot be replayed fails the check, never crashes it
        out["prompt_rebuild_mismatches"] = [f"rebuild failed ({type(exc).__name__})"]
    guard = json.loads((research / "guard.json").read_text()) if (research / "guard.json").is_file() else {}
    out["guard_ok"] = guard.get("truth_absent") is True and str(guard.get("run_attempt")) == "1"
    out["verdict"] = "PASS" if (not out["failure"] and out["calls"] == PLANNED_CALLS
                                and out["valid_calls"] == PLANNED_CALLS and out["illegal_experiments"] == 0
                                and out["refusals"] <= MAX_REFUSALS and out["enumeration_ok"]
                                and out["system_text_ok"] and not out["prompt_rebuild_mismatches"]
                                and out["guard_ok"]) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research) / PREFLIGHT_WORLD, Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    r = check_k1(research)
    rec = {"phase": PREFLIGHT_PHASE, "verdict": r["verdict"], "spec_sha": spec_sha(),
           "run_id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"), PREFLIGHT_WORLD: r}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# Kernel1 preflight: {r['verdict']}", "",
             f"Researcher L8: calls {r['calls']} (valid {r['valid_calls']}); attempts {r['attempts']}; repairs "
             f"{r['repairs']}; refusals {r['refusals']} {r['refusal_categories']}; experiments {r['experiments']} "
             f"(illegal {r['illegal_experiments']}); tokens {r['tokens_used']}; failure {r['failure']}.",
             f"Enumeration X01-X08 in every belief table: {r['enumeration_ok']}. System text frozen: "
             f"{r['system_text_ok']}. Prompt rebuild mismatches: {r['prompt_rebuild_mismatches'] or 'none'}. Guard "
             f"(truth absent, first attempt): {r['guard_ok']}.", ""]
    for call in r["per_call"]:
        lines.append(f"- call {call['call']}: valid {call['valid']}; experiments {call['experiments']}; attempts "
                     + "; ".join(f"#{a['attempt']} {a['stop_reason']} ({a['refusal_category']}, {a['elapsed_s']} s)"
                                 for a in call["attempts"]))
    if r["refusal_explanations"]:
        lines += ["", "Refusal explanations: " + " | ".join(r["refusal_explanations"])]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / PREFLIGHT_WORLD).mkdir(exist_ok=True)
    for name in FILES:
        if (research / name).is_file():
            shutil.copyfile(research / name, out / PREFLIGHT_WORLD / name)
    obs_meta = Path(args.observed) / PREFLIGHT_WORLD / "observed.json"
    if obs_meta.is_file():
        shutil.copyfile(obs_meta, out / PREFLIGHT_WORLD / "observed.json")
    print(json.dumps({"verdict": r["verdict"], "refusals": r["refusals"], "categories": r["refusal_categories"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
