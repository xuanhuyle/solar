"""The final-kernel preflight (operational only, no science): one non-scored company through the whole chain, E1, the
referee, E2-F and E2-K, the referee again, E3-F and E3-K (FINAL_KERNEL_SPEC.md section 11).

For every record: beta1's operational rule (all 4 calls end with a valid response, no integrity failure, at most 1
refusal), every requested experiment legal over X01-X08 and run, every belief table enumerating X01-X08, the frozen L8
system text, every prompt rebuilt from the record with the shipped context and the expected memory (the company's
memory artifact for K, the empty memory for E1 and F), the record's input hashes, and the guard (truth absent, first
attempt). For the memory artifacts: present, ``memory.txt`` the rendering of ``memory.json``, and K's memory not empty.
Its world's roles are never read and nothing is tuned from it.

    python -m research_loop_proof.final_kernel.truth.preflight --research D --observed D --memory D --out D
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
from research_loop_proof.discovery1.lab.researcher import system_text8
from research_loop_proof.final_kernel.lab import referee as ref
from research_loop_proof.final_kernel.lab.researcher import data_block, rebuild_mismatches_fk
from research_loop_proof.final_kernel.truth.observe import PREFLIGHT_PHASE
from research_loop_proof.final_kernel.truth.spec import spec_sha
from research_loop_proof.phase0.lab.executor import request_errors
from research_loop_proof.phase0.lab.researcher import sha256_text

COMPANY = "c1"
CHAIN = (("e1_c1", 1, "E1", None), ("e2f_c1", 2, "F", None), ("e2k_c1", 2, "K", "c1-e1"),
         ("e3f_c1", 3, "F", None), ("e3k_c1", 3, "K", "c1-e2"))
FILES = ("ai.json", "notebook.jsonl", "integrity.json", "guard.json", "timing.json")


def check_record(research: Path, context_text: str, memory_text: str, observed_sha: str) -> dict:
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
        out["prompt_rebuild_mismatches"] = rebuild_mismatches_fk(calls, data_block(context_text, memory_text)) \
            if calls else ["no calls"]
    except Exception as exc:  # a record that cannot be replayed fails the check, never crashes it
        out["prompt_rebuild_mismatches"] = [f"rebuild failed ({type(exc).__name__})"]
    inputs = ai.get("inputs") or {}
    out["inputs_ok"] = (inputs.get("observed_sha256") == observed_sha
                        and inputs.get("context_sha256") == sha256_text(context_text)
                        and inputs.get("memory_sha256") == (sha256_text(memory_text) if memory_text else None))
    guard = json.loads((research / "guard.json").read_text()) if (research / "guard.json").is_file() else {}
    out["guard_ok"] = guard.get("truth_absent") is True and str(guard.get("run_attempt")) == "1"
    out["verdict"] = "PASS" if (not out["failure"] and out["calls"] == PLANNED_CALLS
                                and out["valid_calls"] == PLANNED_CALLS and out["illegal_experiments"] == 0
                                and out["refusals"] <= MAX_REFUSALS and out["enumeration_ok"]
                                and out["system_text_ok"] and not out["prompt_rebuild_mismatches"]
                                and out["inputs_ok"] and out["guard_ok"]) else "FAIL"
    return out


def check_memory(d: Path) -> dict:
    if not (d / "memory.json").is_file() or not (d / "memory.txt").is_file():
        return {"ok": False, "entries": 0, "errors": ["memory artifact missing"]}
    mem = json.loads((d / "memory.json").read_text())
    text = (d / "memory.txt").read_text(encoding="utf-8")
    errs = [] if text == ref.render_memory(mem) else ["memory.txt is not the rendering of memory.json"]
    if not mem:
        errs.append("the memory is empty")
    return {"ok": not errs, "entries": len(mem), "errors": errs, "text": text}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for a in ("--research", "--observed", "--memory", "--out"):
        ap.add_argument(a, required=True)
    args = ap.parse_args(argv)
    research, obs, mem, out = Path(args.research), Path(args.observed), Path(args.memory), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    memories = {name: check_memory(mem / name) for name in ("c1-e1", "c1-e2")}
    records = {}
    for job, e, cond, mem_name in CHAIN:
        od = obs / f"{COMPANY}e{e}"
        ctx = (od / "context.txt").read_text(encoding="utf-8") if (od / "context.txt").is_file() else ""
        obs_sha = json.loads((od / "observed.json").read_text()).get("arrays_sha256") \
            if (od / "observed.json").is_file() else None
        mtext = memories[mem_name].get("text", "") if mem_name else ""
        records[job] = check_record(research / job, ctx, mtext, obs_sha)
    verdict = "PASS" if all(r["verdict"] == "PASS" for r in records.values()) and \
        all(m["ok"] for m in memories.values()) else "FAIL"
    rec = {"phase": PREFLIGHT_PHASE, "verdict": verdict, "spec_sha": spec_sha(), "run_id": os.environ.get(
        "GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"), "records": records,
           "memories": {k: {kk: vv for kk, vv in v.items() if kk != "text"} for k, v in memories.items()}}
    (out / "preflight.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec[k] for k in ("phase", "verdict", "spec_sha", "run_id",
                                                                      "commit")}, indent=1) + "\n")
    lines = [f"# Final-kernel preflight: {verdict}", ""]
    for job, r in records.items():
        lines.append(f"- {job}: {r['verdict']}; calls {r['calls']} (valid {r['valid_calls']}); attempts "
                     f"{r['attempts']}; repairs {r['repairs']}; refusals {r['refusals']}; experiments "
                     f"{r['experiments']} (illegal {r['illegal_experiments']}); tokens {r['tokens_used']}; system text "
                     f"{r['system_text_ok']}; prompt rebuild {r['prompt_rebuild_mismatches'] or 'ok'}; inputs "
                     f"{r['inputs_ok']}; guard {r['guard_ok']}; failure {r['failure']}")
    for name, m in memories.items():
        lines.append(f"- memory {name}: ok {m['ok']}; entries {m['entries']}; {m['errors'] or 'no errors'}")
    (out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for job, *_ in CHAIN:
        (out / job).mkdir(exist_ok=True)
        for name in FILES:
            if (research / job / name).is_file():
                shutil.copyfile(research / job / name, out / job / name)
    for name in memories:
        if (mem / name).is_dir():
            (out / "memory" / name).mkdir(parents=True, exist_ok=True)
            for f in (mem / name).iterdir():
                if f.is_file():
                    shutil.copyfile(f, out / "memory" / name / f.name)
    print(json.dumps({"verdict": verdict, "records": {k: v["verdict"] for k, v in records.items()},
                      "memories": {k: v["ok"] for k, v in memories.items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
