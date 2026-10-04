"""The policy1 regression replays: a non-scored engineering check (NEXT_POLICY_ARCHITECTURE_PROMPT.md section 6).

Not evidence. The two worlds and their failures are known to us, so these replays are contaminated by that knowledge and
are never reported as validation. They only ask whether the structured interface makes the missing concepts
representable and usable at the two known decision points:
- beta1 replay: beta1's own first two rounds of evidence (X03 helpful, then fading; X01/X02 rejected before the change),
  then S chooses round 3 (one experiment left) and the final call;
- learn1 replay: learn1 L's first two rounds (the three rejected singles re-screened jointly, +15%), then S chooses round
  3 (one experiment left) and the final call.

Operational checks: the replayed results equal the published originals (same data, same t0-beta), S's calls are valid,
its prompts rebuild byte for byte, and no failure was recorded. The report prints S's structured state verbatim; the
worlds' published roles are shown for the reader only (the research job never saw them).

    python -m research_loop_proof.policy1.truth.replay --research D --published D --out D     # D/beta1, D/learn1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from research_loop_proof.phase0.truth.evaluate import _close
from research_loop_proof.policy1.lab.researcher import rebuild_mismatches_s, render_call_s
from research_loop_proof.policy1.truth.observe import PREFIX_CALLS, REPLAYS, published_record

PUBLISHED_ROLES = {"beta1": {"R": "X03", "E": "X02", "D": "X01", "N": "X04", "tau": 88},
                   "learn1": {"R": "X04", "E": "X01", "D": "X03", "N": "X02", "tau": 88}}


def check_replay(d: Path, original: dict) -> dict:
    failure = json.loads((d / "integrity.json").read_text()).get("failure") \
        if (d / "integrity.json").is_file() else {"kind": "missing", "error": "no integrity.json"}
    ai = json.loads((d / "ai.json").read_text()) if (d / "ai.json").is_file() else {"calls": []}
    calls = ai.get("calls", [])
    replayed = [e["result"] for c in calls if c.get("replayed") for e in c["experiments"]]
    orig = [e["result"] for c in original["calls"][:PREFIX_CALLS] for e in c["experiments"]]
    same = len(replayed) == len(orig) and all(
        all(_close(a[k], b[k]) for k in ("covariates", "reference", "scored_days", "skill", "lo95", "hi95"))
        for a, b in zip(replayed, orig))
    live = [c for c in calls if not c.get("replayed")]
    attempts = [a for c in live for a in c["attempts"]]
    out = {"failure": failure, "condition": ai.get("condition"), "replayed_results_match_published": same,
           "live_calls": len(live), "valid_live_calls": sum(bool(c.get("valid")) for c in live),
           "attempts": len(attempts), "repairs": sum(1 for a in attempts if a.get("attempt") == 2),
           "refusals": sum(1 for a in attempts if a.get("stop_reason") == "refusal"),
           "rebuild_mismatches": rebuild_mismatches_s(calls), "tokens_used": ai.get("tokens_used"),
           "t0_forecasts": ai.get("t0_forecasts")}
    out["operational"] = "PASS" if (not failure and same and out["condition"] == "S" and len(live) == 2
                                    and out["valid_live_calls"] == 2 and not out["rebuild_mismatches"]) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--published", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    research, out = Path(args.research), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    per, lines = {}, ["# policy1 regression replays (engineering check, not evidence)", "",
                      "Contaminated by our knowledge of these worlds; never reported as validation.", ""]
    for name in REPLAYS:
        original = published_record(Path(args.published) / name, name)
        per[name] = check_replay(research / name, original)
        r, roles = per[name], PUBLISHED_ROLES[name]
        lines += [f"## {name} replay: operational {r['operational']}", "",
                  f"Published roles (not shown to the researcher): R = {roles['R']}, E = {roles['E']}, D = {roles['D']}, "
                  f"N = {roles['N']}; first changed day {roles['tau']}.", "",
                  f"Replayed results equal the published ones: {r['replayed_results_match_published']}. Live calls "
                  f"{r['live_calls']} (valid {r['valid_live_calls']}); attempts {r['attempts']}; repairs {r['repairs']}; "
                  f"refusals {r['refusals']}; prompt rebuild mismatches {r['rebuild_mismatches'] or 'none'}; tokens "
                  f"{r['tokens_used']}; t0-beta forecasts {r['t0_forecasts']}; failure {r['failure']}.", "",
                  "### The notebook S produced (replayed evidence, then its own calls), verbatim", "", "```"]
        ai = json.loads((research / name / "ai.json").read_text()) if (research / name / "ai.json").is_file() else {}
        lines += [render_call_s(c) + "\n" for c in ai.get("calls", [])] + ["```", ""]
        (out / name).mkdir(exist_ok=True)
        for f in ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "prefix.json"):
            if (research / name / f).is_file():
                shutil.copyfile(research / name / f, out / name / f)
    verdict = "PASS" if all(per[n]["operational"] == "PASS" for n in REPLAYS) else "FAIL"
    rec = {"phase": "policy1-replay", "verdict": verdict, "run_id": os.environ.get("GITHUB_RUN_ID"),
           "commit": os.environ.get("GITHUB_SHA"), "replays": per}
    (out / "replay.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "run_id", "commit")},
                                                 indent=1) + "\n")
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"verdict": verdict, **{n: per[n]["operational"] for n in REPLAYS}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
