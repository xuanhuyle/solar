"""The learn1 researcher preflight (operational only, no science): beta1's check, on both conditions.

On a non-scored world, each condition (F and L, with the scored run's model, effort, schema, system texts, interface
and notebook) must pass beta1's operational rule: all 4 calls end with a valid response, every requested experiment is
legal and ran, no integrity failure, at most 1 refusal in all. PASS only when both pass. The trajectories are never
evaluated against the world's roles.

    python -m research_loop_proof.learn1.truth.preflight --research D --observed D --out D   # D/F and D/L
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from research_loop_proof.beta1.truth.preflight import check
from research_loop_proof.learn1.lab.researcher import CONDITIONS
from research_loop_proof.learn1.truth.spec import spec_sha


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--observed", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    per = {c: check(research / c) for c in CONDITIONS}
    verdict = "PASS" if all(per[c]["verdict"] == "PASS" for c in CONDITIONS) else "FAIL"
    rec = {"phase": "learn1-preflight", "verdict": verdict, "spec_sha": spec_sha(),
           "run_id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"), "conditions": per}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# learn1 researcher preflight: {verdict}", ""]
    for c in CONDITIONS:
        r = per[c]
        lines += [f"## Condition {c}: {r['verdict']}", "",
                  f"Calls {r['calls']} (valid {r['valid_calls']}); attempts {r['attempts']}; repairs {r['repairs']}; "
                  f"refusals {r['refusals']} {r['refusal_categories']}; experiments {r['experiments']} (illegal "
                  f"{r['illegal_experiments']}); tokens {r['tokens_used']}; failure {r['failure']}.", ""]
        for call in r["per_call"]:
            lines.append(f"- call {call['call']}: valid {call['valid']}; experiments {call['experiments']}; attempts "
                         + "; ".join(f"#{a['attempt']} {a['stop_reason']} ({a['refusal_category']}, {a['elapsed_s']} s)"
                                     for a in call["attempts"]))
        if r["refusal_explanations"]:
            lines += ["", "Refusal explanations: " + " | ".join(r["refusal_explanations"])]
        lines.append("")
        (out / c).mkdir(exist_ok=True)
        for name in ("ai.json", "notebook.jsonl", "integrity.json", "guard.json"):
            if (research / c / name).is_file():
                shutil.copyfile(research / c / name, out / c / name)
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    shutil.copyfile(Path(args.observed) / "observed.json", out / "observed.json")
    print(json.dumps({"verdict": verdict, **{c: per[c]["verdict"] for c in CONDITIONS}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
