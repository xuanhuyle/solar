"""The Discovery1 preflight (operational only, no science): one non-scored world, researcher L8 and the comparator.

It verifies schema validity, candidate enumeration, t0 execution, prompt reconstruction and truth separation, as the
owner's prompt lists: beta1's operational rule on L8 (all 4 calls end with a valid response, every requested experiment
is legal over X01-X08 and ran, no integrity failure, at most 1 refusal), every belief table enumerating exactly
X01-X08, L8's system text equal to the frozen text, every prompt rebuilt from the record, the comparator's 6
experiments following its rule, and the guard. Its results are never evaluated against the world's roles and are not
used to tune anything.

    python -m research_loop_proof.discovery1.truth.preflight --research D --observed D --out D   # D/w1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from research_loop_proof.beta1.truth.preflight import MAX_REFUSALS, PLANNED_CALLS, check
from research_loop_proof.discovery1.lab import comparator
from research_loop_proof.discovery1.lab.executor import IDS8
from research_loop_proof.discovery1.lab.researcher import rebuild_mismatches8, system_text8
from research_loop_proof.discovery1.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import request_errors
from research_loop_proof.phase0.lab.researcher import sha256_text

FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "comparator.json")


def check8(research: Path) -> dict:
    out = check(research)
    ai = json.loads((research / "ai.json").read_text()) if (research / "ai.json").is_file() else {"calls": []}
    calls = ai.get("calls", [])
    exps = [e for c in calls for e in c.get("experiments", [])]
    out["illegal_experiments"] = sum(1 for e in exps if request_errors(e["request"], IDS8) or "result" not in e)
    out["enumeration_ok"] = bool(calls) and all(
        sorted(b["candidate"] for b in c["response"]["beliefs"]) == list(IDS8) for c in calls if c.get("valid"))
    out["system_text_ok"] = ai.get("system_text") == system_text8() and ai.get("system_sha256") == sha256_text(
        system_text8())
    out["prompt_rebuild_mismatches"] = rebuild_mismatches8(calls) if calls else ["no calls"]
    guard = json.loads((research / "guard.json").read_text()) if (research / "guard.json").is_file() else {}
    out["guard_ok"] = guard.get("truth_absent") is True
    comp = json.loads((research / "comparator.json").read_text()) if (research / "comparator.json").is_file() else {}
    out["comparator_errors"] = (comparator.selection_errors(comp) if comp else ["no comparator record"]) + [
        f"{e['id']}: illegal" for e in comp.get("experiments", []) if request_errors(e["request"], IDS8)]
    out["comparator_selection"] = comp.get("final_selection")
    out["verdict"] = "PASS" if (not out["failure"] and out["calls"] == PLANNED_CALLS
                                and out["valid_calls"] == PLANNED_CALLS and out["illegal_experiments"] == 0
                                and out["refusals"] <= MAX_REFUSALS and out["enumeration_ok"]
                                and out["system_text_ok"] and not out["prompt_rebuild_mismatches"]
                                and out["guard_ok"] and not out["comparator_errors"]) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research) / "w1", Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    r = check8(research)
    rec = {"phase": "discovery1-preflight", "verdict": r["verdict"], "spec_sha": spec_sha(),
           "run_id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"), "w1": r}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# Discovery1 preflight: {r['verdict']}", "",
             f"Researcher L8: calls {r['calls']} (valid {r['valid_calls']}); attempts {r['attempts']}; repairs "
             f"{r['repairs']}; refusals {r['refusals']} {r['refusal_categories']}; experiments {r['experiments']} "
             f"(illegal {r['illegal_experiments']}); tokens {r['tokens_used']}; failure {r['failure']}.",
             f"Enumeration X01-X08 in every belief table: {r['enumeration_ok']}. System text frozen: "
             f"{r['system_text_ok']}. Prompt rebuild mismatches: {r['prompt_rebuild_mismatches'] or 'none'}. Guard: "
             f"{r['guard_ok']}.",
             f"Comparator: {r['comparator_errors'] or 'six legal experiments following its rule'}.", ""]
    for call in r["per_call"]:
        lines.append(f"- call {call['call']}: valid {call['valid']}; experiments {call['experiments']}; attempts "
                     + "; ".join(f"#{a['attempt']} {a['stop_reason']} ({a['refusal_category']}, {a['elapsed_s']} s)"
                                 for a in call["attempts"]))
    if r["refusal_explanations"]:
        lines += ["", "Refusal explanations: " + " | ".join(r["refusal_explanations"])]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "w1").mkdir(exist_ok=True)
    for name in FILES:
        if (research / name).is_file():
            shutil.copyfile(research / name, out / "w1" / name)
    shutil.copyfile(Path(args.observed) / "w1" / "observed.json", out / "observed.json")
    print(json.dumps({"verdict": r["verdict"], "refusals": r["refusals"], "categories": r["refusal_categories"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
