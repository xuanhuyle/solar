"""The research jobs of learn1, one condition per job and per process:

    python -m research_loop_proof.learn1.lab.run weights --weights DIR             # t0-beta is ungated: no secret
    python -m research_loop_proof.learn1.lab.run loop --condition F|L --observed F --observed-sha S --weights DIR --out OUT
                                                                                    # the API key only here

The F and L jobs are identical except for ``--condition``. Each checkout lacks every world-generator and evaluator
package (a guard step checks it); the instrument is beta1's t0-beta, verified against its pins when downloaded and again
when loaded. Any integrity failure or crash is written to ``integrity.json`` with whatever was recorded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

from research_loop_proof.beta1.lab import run as beta1_run
from research_loop_proof.learn1.lab.researcher import CONDITIONS, Researcher
from research_loop_proof.phase0.lab.researcher import IntegrityError, model_allowed, redact, sha256_text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["weights", "loop"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--condition", choices=CONDITIONS)
    ap.add_argument("--observed")
    ap.add_argument("--observed-sha")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.step == "weights":
        return beta1_run.main(["weights", "--weights", args.weights])
    if args.condition is None:
        ap.error("loop needs --condition F or L")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    notebook = (out / "notebook.jsonl").open("a", encoding="utf-8")

    def emit(event: dict) -> None:
        notebook.write(json.dumps(event, ensure_ascii=False) + "\n")
        notebook.flush()

    researcher, record = None, {"condition": args.condition}
    model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
    try:
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        import anthropic

        lab = beta1_run.observed_lab(args)
        client = anthropic.Anthropic(timeout=480.0, max_retries=0)
        researcher = Researcher(client, model_id, lab, emit=emit, condition=args.condition)
        record = researcher.run()
        record.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
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
    (out / "ai.json").write_text(json.dumps(record, indent=1) + "\n")
    (out / "integrity.json").write_text(json.dumps({"failure": failure}, indent=1) + "\n")
    print(json.dumps({"condition": args.condition, "failure": failure and failure["error"],
                      "tokens_used": record.get("tokens_used"), "final_selection": record.get("final_selection")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
