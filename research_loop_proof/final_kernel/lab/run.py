"""The final-kernel research and referee jobs, each step its own process:

    python -m research_loop_proof.final_kernel.lab.run weights --weights DIR          # t0-beta is ungated: no secret
    python -m research_loop_proof.final_kernel.lab.run loop --condition E1|K|F --observed F --observed-sha S \
        --context C --context-sha S [--memory M --memory-sha S] --weights DIR --out OUT   # the API key only here
    python -m research_loop_proof.final_kernel.lab.run referee --record R --context-json C --holdout F \
        --holdout-sha S [--memory-in M] --weights DIR --out OUT                            # no secret

``loop`` runs the final-kernel researcher (Discovery1's L8, its system text byte-identical, with the context and the
memory as a data block before every user prompt) on one episode's observed data. E1 and F get the empty memory; K gets
the memory artifact its company's previous referee job produced, checked against the hash that job declared. The
record carries the condition and the hashes of the observed data, the context and the memory it used. ``referee``
adjudicates one research record (truth-free: the record, the context tags and the holdout data of configurations that
were tested and approved or selected) and appends the episode's entries to the company's memory. Neither step imports a
truth package; a guard step checks that none is on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

from research_loop_proof.beta1.lab import run as beta1_run
from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.discovery1.lab.executor import Lab8
from research_loop_proof.final_kernel.lab import referee as ref
from research_loop_proof.final_kernel.lab.researcher import ResearcherFK
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import IntegrityError, model_allowed, redact, sha256_text

CONDITIONS = ("E1", "K", "F")


def file_sha(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_lab(path: str, declared: str, weights: str) -> Lab8:
    obs = load_observed(path)
    got = arrays_sha256(obs)
    if got != declared:
        raise IntegrityError(f"data hash {got} != declared {declared}")
    model, _ = beta1_run.load_t0(Path(weights))
    return Lab8(obs, t0_beta.BetaT0(model))


def _text(path: str | None, declared: str | None, what: str) -> str:
    if path is None:
        return ""
    got = file_sha(path)
    if got != declared:
        raise IntegrityError(f"{what} hash {got} != declared {declared}")
    return Path(path).read_text(encoding="utf-8")


def loop(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    notebook = (out / "notebook.jsonl").open("a", encoding="utf-8")

    def emit(event: dict) -> None:
        notebook.write(json.dumps(event, ensure_ascii=False) + "\n")
        notebook.flush()

    researcher, record = None, {"condition": args.condition}
    model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
    inputs = {"condition": args.condition, "observed_sha256": args.observed_sha, "context_sha256": None,
              "memory_sha256": None}
    try:
        if args.condition not in CONDITIONS:
            raise IntegrityError(f"unknown condition {args.condition!r}")
        if (args.condition == "K") != (args.memory is not None):
            raise IntegrityError("memory is given to condition K only, and K always gets it")
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        context = _text(args.context, args.context_sha, "context")
        memory = _text(args.memory, args.memory_sha, "memory")
        inputs.update(context_sha256=args.context_sha, memory_sha256=args.memory_sha)
        import anthropic

        lab = checked_lab(args.observed, args.observed_sha, args.weights)
        client = anthropic.Anthropic(timeout=480.0, max_retries=0)
        researcher = ResearcherFK(client, model_id, lab, context_text=context, memory_text=memory, emit=emit)
        record = researcher.run()
        record.update(condition=args.condition, t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        failure = None
    except Exception as exc:  # recorded, never lost
        failure = {"kind": "integrity" if isinstance(exc, IntegrityError) else "crash",
                   "error": redact(f"{type(exc).__name__}: {exc}", model_id)[:2000],
                   "traceback": redact(traceback.format_exc(), model_id)[-4000:]}
        if researcher is not None:
            record = {"condition": args.condition, "calls": researcher.calls, "tokens_used": researcher.tokens,
                      "final_valid": False, "system_sha256": sha256_text(researcher.system),
                      "system_text": researcher.system}
    finally:
        notebook.close()
    record["inputs"] = inputs
    (out / "ai.json").write_text(json.dumps(record, indent=1) + "\n")
    (out / "integrity.json").write_text(json.dumps({"failure": failure}, indent=1) + "\n")
    print(json.dumps({"condition": args.condition, "failure": failure and failure["error"],
                      "tokens_used": record.get("tokens_used"), "final_selection": record.get("final_selection")}))
    return 0


def referee(args) -> int:
    """Adjudicate one record and write the company's memory after this episode (``memory.json``, ``memory.txt``) and
    the referee's report (``referee.json``). A missing record leaves the memory unchanged and says so."""
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ctx = json.loads(Path(args.context_json).read_text(encoding="utf-8"))
    memory = json.loads(Path(args.memory_in).read_text(encoding="utf-8")) if args.memory_in else []
    lab = checked_lab(args.holdout, args.holdout_sha, args.weights)

    def confirm(cov, refs):
        req = {"covariates": list(cov), "reference": list(refs), "window_days": ref.CONFIRMATION["window_days"]}
        return lab.run(req, ref.CONFIRMATION["cutoff"], "confirmation")

    rec_path = Path(args.record)
    report = {"company": ctx["company"], "episode": ctx["episode"], "regime": ctx["regime"], "record": None}
    if rec_path.is_file():
        record = json.loads(rec_path.read_text())
        report.update(record="present", condition=record.get("condition"),
                      **ref.adjudicate(record, confirm))
        memory = ref.extend_memory(memory, report, company=ctx["company"], episode=ctx["episode"],
                                   regime=ctx["regime"], names=ctx["names"])
    else:
        report["record"] = "missing"
    report["t0_forecasts"] = lab.inst.rows
    (out / "memory.json").write_text(ref.memory_json(memory), encoding="utf-8")
    (out / "memory.txt").write_text(ref.render_memory(memory), encoding="utf-8")
    (out / "referee.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"company": ctx["company"], "episode": ctx["episode"], "record": report["record"],
                      "memory_entries": len(memory), "memory_sha256": file_sha(out / "memory.txt")}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["weights", "loop", "referee"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--condition")
    ap.add_argument("--observed")
    ap.add_argument("--observed-sha")
    ap.add_argument("--context")
    ap.add_argument("--context-sha")
    ap.add_argument("--memory")
    ap.add_argument("--memory-sha")
    ap.add_argument("--record")
    ap.add_argument("--context-json")
    ap.add_argument("--holdout")
    ap.add_argument("--holdout-sha")
    ap.add_argument("--memory-in")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.step == "weights":
        return beta1_run.main(["weights", "--weights", args.weights])
    return loop(args) if args.step == "loop" else referee(args)


if __name__ == "__main__":
    sys.exit(main())
