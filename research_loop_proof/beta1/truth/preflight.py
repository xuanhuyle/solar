"""The beta1 researcher preflight check (NEXT_MILESTONE_PROMPT.md section 5): operational only, no science.

On a non-scored world, with the scored run's model, effort, schema, brief, experiment interface and notebook, it asks
whether the researcher API can perform the task: valid structured answers, legal experiments, the whole sequence
without repeated service refusals. PASS when every one of the 4 calls ends with a valid response, every requested
experiment is legal and ran, there is no integrity failure, and at most 1 attempt in total was a refusal. Its result
is never evaluated against the world's roles.

    python -m research_loop_proof.beta1.truth.preflight --research D --observed D --out D
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

from research_loop_proof.beta1.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import request_errors

MAX_REFUSALS = 1
PLANNED_CALLS = 4


def check(research: Path) -> dict:
    out = {"rules": {"valid_calls": PLANNED_CALLS, "max_refusals": MAX_REFUSALS}}
    ai_path = research / "ai.json"
    failure = json.loads((research / "integrity.json").read_text()).get("failure") \
        if (research / "integrity.json").is_file() else {"kind": "missing", "error": "no integrity.json"}
    ai = json.loads(ai_path.read_text()) if ai_path.is_file() else {"calls": []}
    calls = ai.get("calls", [])
    attempts = [a for c in calls for a in c["attempts"]]
    refusals = [a for a in attempts if a.get("stop_reason") == "refusal"]
    experiments = [e for c in calls for e in c.get("experiments", [])]
    out.update(
        failure=failure, calls=len(calls), valid_calls=sum(bool(c.get("valid")) for c in calls),
        attempts=len(attempts), repairs=sum(1 for a in attempts if a.get("attempt") == 2), refusals=len(refusals),
        refusal_categories=dict(Counter(str(a.get("refusal_category")) for a in refusals)),
        refusal_explanations=sorted({(a.get("stop_details") or {}).get("explanation") or "" for a in refusals} - {""}),
        experiments=len(experiments),
        illegal_experiments=sum(1 for e in experiments if request_errors(e["request"]) or "result" not in e),
        tokens_used=ai.get("tokens_used"),
        per_call=[{"call": c["call"], "valid": c.get("valid"), "errors": c.get("errors"),
                   "attempts": [{k: a.get(k) for k in ("attempt", "stop_reason", "refusal_category", "elapsed_s",
                                                       "usage", "request_id", "served_matches_requested")}
                                for a in c["attempts"]], "experiments": len(c.get("experiments", []))} for c in calls])
    out["verdict"] = "PASS" if (not failure and out["calls"] == PLANNED_CALLS and out["valid_calls"] == PLANNED_CALLS
                                and out["illegal_experiments"] == 0 and out["refusals"] <= MAX_REFUSALS) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"phase": "beta1-preflight", "spec_sha": spec_sha(), "run_id": os.environ.get("GITHUB_RUN_ID"),
           "commit": os.environ.get("GITHUB_SHA"), **check(research)}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# beta1 researcher preflight: {rec['verdict']}", "",
             f"Calls {rec['calls']} (valid {rec['valid_calls']}); attempts {rec['attempts']}; repairs {rec['repairs']}; "
             f"refusals {rec['refusals']} {rec['refusal_categories']}; experiments {rec['experiments']} "
             f"(illegal {rec['illegal_experiments']}); tokens {rec['tokens_used']}; failure {rec['failure']}.", ""]
    for c in rec["per_call"]:
        lines.append(f"- call {c['call']}: valid {c['valid']}; experiments {c['experiments']}; attempts " + "; ".join(
            f"#{a['attempt']} {a['stop_reason']} ({a['refusal_category']}, {a['elapsed_s']} s)" for a in c["attempts"]))
    if rec["refusal_explanations"]:
        lines += ["", "Refusal explanations: " + " | ".join(rec["refusal_explanations"])]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for name in ("ai.json", "notebook.jsonl", "integrity.json", "guard.json"):
        if (research / name).is_file():
            shutil.copyfile(research / name, out / name)
    shutil.copyfile(Path(args.observed) / "observed.json", out / "observed.json")
    print(json.dumps({"verdict": rec["verdict"], "refusals": rec["refusals"], "categories": rec["refusal_categories"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
