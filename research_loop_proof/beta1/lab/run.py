"""The research job of the beta1 run, in three steps, each its own process (as in Phase 0):

    python -m research_loop_proof.beta1.lab.run weights --weights DIR           # t0-beta is ungated: no secret
    python -m research_loop_proof.beta1.lab.run scripted --observed F --observed-sha S --weights DIR --out OUT
    python -m research_loop_proof.beta1.lab.run loop --observed F --observed-sha S --weights DIR --out OUT
                                                                                 # the API key only here

The job's checkout lacks both world-generator and evaluator packages (a guard step checks it). The instrument is
t0-beta (``t0_beta.BetaT0``), verified against the qualification pins when downloaded and again when loaded. Any
integrity failure or crash in the loop is written to ``integrity.json`` with whatever was recorded.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.lab.researcher import Researcher
from research_loop_proof.phase0.lab import scripted
from research_loop_proof.phase0.lab.executor import Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.researcher import IntegrityError, model_allowed, redact, sha256_text


def load_t0(weights: Path):
    return t0_beta.load(weights)


def observed_lab(args) -> Lab:
    obs = load_observed(args.observed)
    got = arrays_sha256(obs)
    if got != args.observed_sha:
        raise IntegrityError(f"observed data hash {got} != declared {args.observed_sha}")
    model, _ = load_t0(Path(args.weights))
    return Lab(obs, t0_beta.BetaT0(model))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["weights", "scripted", "loop"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--observed")
    ap.add_argument("--observed-sha")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.step == "weights":
        if not t0_beta.PINNED:
            print("t0-beta is not pinned yet (qualification first)")
            return 1
        print(json.dumps(t0_beta.fetch(Path(args.weights))))
        return 0
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.step == "scripted":
        lab = observed_lab(args)
        res = scripted.run(lab)
        res.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        (out / "scripted.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"scripted_selection": res["final_selection"], "t0_forecasts": lab.inst.rows}))
        return 0
    notebook = (out / "notebook.jsonl").open("a", encoding="utf-8")

    def emit(event: dict) -> None:
        notebook.write(json.dumps(event, ensure_ascii=False) + "\n")
        notebook.flush()

    researcher, record = None, {}
    model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
    try:
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        import anthropic

        lab = observed_lab(args)
        client = anthropic.Anthropic(timeout=480.0, max_retries=0)
        researcher = Researcher(client, model_id, lab, emit=emit)
        record = researcher.run()
        record.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        failure = None
    except Exception as exc:  # recorded, never lost
        failure = {"kind": "integrity" if isinstance(exc, IntegrityError) else "crash",
                   "error": redact(f"{type(exc).__name__}: {exc}", model_id)[:2000],
                   "traceback": redact(traceback.format_exc(), model_id)[-4000:]}
        if researcher is not None:
            record = {"calls": researcher.calls, "tokens_used": researcher.tokens, "final_valid": False,
                      "system_sha256": sha256_text(researcher.system)}
    finally:
        notebook.close()
    (out / "ai.json").write_text(json.dumps(record, indent=1) + "\n")
    (out / "integrity.json").write_text(json.dumps({"failure": failure}, indent=1) + "\n")
    print(json.dumps({"failure": failure and failure["error"], "tokens_used": record.get("tokens_used"),
                      "final_selection": record.get("final_selection")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
