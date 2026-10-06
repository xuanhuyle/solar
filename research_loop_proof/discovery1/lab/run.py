"""The research job of one Discovery1 world, in three steps, each its own process:

    python -m research_loop_proof.discovery1.lab.run weights --weights DIR             # t0-beta is ungated: no secret
    python -m research_loop_proof.discovery1.lab.run comparator --observed F --observed-sha S --weights DIR --out OUT
    python -m research_loop_proof.discovery1.lab.run loop --observed F --observed-sha S --weights DIR --out OUT
                                                                                        # the API key only here

The three world jobs are identical except for the world they read. Each checkout lacks every world-generator and
evaluator package (a guard step checks it); the instrument is beta1's t0-beta, verified against its pins when
downloaded and again when loaded. The comparator needs no API key. Any integrity failure or crash in the loop is
written to ``integrity.json`` with whatever was recorded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

from research_loop_proof.beta1.lab import run as beta1_run
from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.discovery1.lab import comparator
from research_loop_proof.discovery1.lab.executor import Lab8
from research_loop_proof.discovery1.lab.researcher import Researcher8
from research_loop_proof.phase0.lab.executor import arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import IntegrityError, model_allowed, redact, sha256_text


def observed_lab(args) -> Lab8:
    obs = load_observed(args.observed)
    got = arrays_sha256(obs)
    if got != args.observed_sha:
        raise IntegrityError(f"observed data hash {got} != declared {args.observed_sha}")
    model, _ = beta1_run.load_t0(Path(args.weights))
    return Lab8(obs, t0_beta.BetaT0(model))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["weights", "comparator", "loop"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--observed")
    ap.add_argument("--observed-sha")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.step == "weights":
        return beta1_run.main(["weights", "--weights", args.weights])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.step == "comparator":
        lab = observed_lab(args)
        res = comparator.run(lab)
        res.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        (out / "comparator.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"comparator_selection": res["final_selection"], "t0_forecasts": lab.inst.rows}))
        return 0
    notebook = (out / "notebook.jsonl").open("a", encoding="utf-8")

    def emit(event: dict) -> None:
        notebook.write(json.dumps(event, ensure_ascii=False) + "\n")
        notebook.flush()

    researcher, record = None, {"condition": "L"}
    model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
    try:
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        import anthropic

        lab = observed_lab(args)
        client = anthropic.Anthropic(timeout=480.0, max_retries=0)
        researcher = Researcher8(client, model_id, lab, emit=emit)
        record = researcher.run()
        record.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        failure = None
    except Exception as exc:  # recorded, never lost
        failure = {"kind": "integrity" if isinstance(exc, IntegrityError) else "crash",
                   "error": redact(f"{type(exc).__name__}: {exc}", model_id)[:2000],
                   "traceback": redact(traceback.format_exc(), model_id)[-4000:]}
        if researcher is not None:
            record = {"condition": "L", "calls": researcher.calls, "tokens_used": researcher.tokens,
                      "final_valid": False, "system_sha256": sha256_text(researcher.system),
                      "system_text": researcher.system}
    finally:
        notebook.close()
    (out / "ai.json").write_text(json.dumps(record, indent=1) + "\n")
    (out / "integrity.json").write_text(json.dumps({"failure": failure}, indent=1) + "\n")
    print(json.dumps({"failure": failure and failure["error"], "tokens_used": record.get("tokens_used"),
                      "final_selection": record.get("final_selection")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
