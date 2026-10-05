"""The Human1 preflight (operational only, no science): one non-scored world, researcher L2 and the comparator.

It verifies what the owner's prompt lists (section 10): schema validity and candidate enumeration (every belief table has
exactly X01 and X02), t0 execution (every requested experiment legal over X01-X02 and ran), prompt reconstruction
(every prompt rebuilt from the record), truth separation (the guard), the frozen system text, at most 1 refusal and no
integrity failure, all 3 calls valid, and the comparator's 4 experiments following its protocol. Its results are never
evaluated against the world's roles and are not used to tune anything.

    python -m research_loop_proof.human1.truth.preflight --research D --observed D --out D   # D/w1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

from research_loop_proof.human1.lab import comparator
from research_loop_proof.human1.lab.executor import IDS2
from research_loop_proof.human1.lab.researcher import call_plan2, rebuild_mismatches2, system_text2
from research_loop_proof.human1.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import request_errors
from research_loop_proof.phase0.lab.researcher import sha256_text

MAX_REFUSALS = 1
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "comparator.json")


def check2(research: Path) -> dict:
    planned = len(call_plan2())
    failure = json.loads((research / "integrity.json").read_text()).get("failure") \
        if (research / "integrity.json").is_file() else {"kind": "missing", "error": "no integrity.json"}
    ai = json.loads((research / "ai.json").read_text()) if (research / "ai.json").is_file() else {"calls": []}
    calls = ai.get("calls", [])
    attempts = [a for c in calls for a in c["attempts"]]
    refusals = [a for a in attempts if a.get("stop_reason") == "refusal"]
    exps = [e for c in calls for e in c.get("experiments", [])]
    guard = json.loads((research / "guard.json").read_text()) if (research / "guard.json").is_file() else {}
    comp = json.loads((research / "comparator.json").read_text()) if (research / "comparator.json").is_file() else {}
    out = {"rules": {"valid_calls": planned, "max_refusals": MAX_REFUSALS}, "failure": failure, "calls": len(calls),
           "valid_calls": sum(bool(c.get("valid")) for c in calls), "attempts": len(attempts),
           "repairs": sum(1 for a in attempts if a.get("attempt") == 2), "refusals": len(refusals),
           "refusal_categories": dict(Counter(str(a.get("refusal_category")) for a in refusals)),
           "refusal_explanations": sorted({(a.get("stop_details") or {}).get("explanation") or ""
                                           for a in refusals} - {""}),
           "experiments": len(exps),
           "illegal_experiments": sum(1 for e in exps if request_errors(e["request"], IDS2) or "result" not in e),
           "tokens_used": ai.get("tokens_used"),
           "enumeration_ok": bool(calls) and all(sorted(b["candidate"] for b in c["response"]["beliefs"]) == list(IDS2)
                                                 for c in calls if c.get("valid")),
           "system_text_ok": ai.get("system_text") == system_text2()
           and ai.get("system_sha256") == sha256_text(system_text2()),
           "prompt_rebuild_mismatches": rebuild_mismatches2(calls) if calls else ["no calls"],
           "guard_ok": guard.get("truth_absent") is True,
           "comparator_errors": (comparator.selection_errors(comp) if comp else ["no comparator record"])
           + [f"{e['id']}: illegal" for e in comp.get("experiments", []) if request_errors(e["request"], IDS2)],
           "comparator_selection": comp.get("final_selection"),
           "per_call": [{"call": c["call"], "valid": c.get("valid"), "errors": c.get("errors"),
                         "attempts": [{k: a.get(k) for k in ("attempt", "stop_reason", "refusal_category", "elapsed_s",
                                                             "usage", "request_id", "served_matches_requested")}
                                      for a in c["attempts"]], "experiments": len(c.get("experiments", []))}
                        for c in calls]}
    out["verdict"] = "PASS" if (not failure and out["calls"] == planned and out["valid_calls"] == planned
                                and out["illegal_experiments"] == 0 and out["refusals"] <= MAX_REFUSALS
                                and out["enumeration_ok"] and out["system_text_ok"]
                                and not out["prompt_rebuild_mismatches"] and out["guard_ok"]
                                and not out["comparator_errors"]) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research) / "w1", Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    r = check2(research)
    rec = {"phase": "human1-preflight", "verdict": r["verdict"], "spec_sha": spec_sha(),
           "run_id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"), "w1": r}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# Human1 preflight: {r['verdict']}", "",
             f"Researcher L2: calls {r['calls']} (valid {r['valid_calls']}); attempts {r['attempts']}; repairs "
             f"{r['repairs']}; refusals {r['refusals']} {r['refusal_categories']}; experiments {r['experiments']} "
             f"(illegal {r['illegal_experiments']}); tokens {r['tokens_used']}; failure {r['failure']}.",
             f"Enumeration X01-X02 in every belief table: {r['enumeration_ok']}. System text frozen: "
             f"{r['system_text_ok']}. Prompt rebuild mismatches: {r['prompt_rebuild_mismatches'] or 'none'}. Guard: "
             f"{r['guard_ok']}.",
             f"Comparator: {r['comparator_errors'] or 'four legal experiments following its protocol'}.", ""]
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
