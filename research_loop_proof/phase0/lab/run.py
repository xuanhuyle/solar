"""The research job of Phase B (PHASE0_SPEC.md section 4), in three steps, each its own process:

    python -m research_loop_proof.phase0.lab.run weights --weights DIR          # HF_TOKEN only here
    python -m research_loop_proof.phase0.lab.run scripted --observed F --observed-sha S --weights DIR --out OUT
    python -m research_loop_proof.phase0.lab.run loop --observed F --observed-sha S --weights DIR --out OUT
                                                                                 # the API key only here

The job's checkout lacks the world generator and evaluator package (a guard step checks it); this module and
everything it imports live outside that package. The weights are verified by sha256 when downloaded and again when loaded offline. An
integrity failure (model hash, observed-data hash, API outage) or a crash in the loop is written to
``integrity.json`` with whatever was recorded, so the evaluate job can report it.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

from research_loop_proof.phase0.lab import scripted
from research_loop_proof.phase0.lab.executor import Lab, arrays_sha256, load_observed
from research_loop_proof.phase0.lab.instruments import T0
from research_loop_proof.phase0.lab.researcher import IntegrityError, Researcher, model_allowed, sha256_text
from solarbench import t0_pinned

REPO, REVISION = "theforecastingcompany/t0-alpha", "9b02c5f4bb6c89ba15d9fa74554018fe6464220b"


def fetch_weights(weights: Path) -> dict:
    local, record = t0_pinned.fetch(REPO, REVISION)
    weights.mkdir(parents=True, exist_ok=True)
    for name in t0_pinned.FILES:
        shutil.copyfile(Path(local) / name, weights / name)
    (weights / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def load_t0(weights: Path):
    """t0 from the local copy, re-verified against the pinned sha256 (no network)."""
    from t0 import T0Forecaster

    rec = json.loads((weights / "record.json").read_text())
    local, record = t0_pinned.fetch(REPO, REVISION, head=lambda repo: rec["served_by_revision"],
                                    download=lambda repo, rev: str(weights))
    return T0Forecaster.from_pretrained(str(local)).eval(), record


def observed_lab(args, model=None) -> Lab:
    obs = load_observed(args.observed)
    got = arrays_sha256(obs)
    if got != args.observed_sha:
        raise IntegrityError(f"observed data hash {got} != declared {args.observed_sha}")
    if model is None:
        model, _ = load_t0(Path(args.weights))
    return Lab(obs, T0(model))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["weights", "scripted", "loop"])
    ap.add_argument("--weights", required=True)
    ap.add_argument("--observed")
    ap.add_argument("--observed-sha")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.step == "weights":
        print(json.dumps(fetch_weights(Path(args.weights))))
        return 0
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.step == "scripted":
        lab = observed_lab(args)
        res = scripted.run(lab)
        res["t0_forecasts"] = lab.inst.rows
        res["sanitised"] = lab.inst.sanitised
        (out / "scripted.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps({"scripted_selection": res["final_selection"], "t0_forecasts": lab.inst.rows}))
        return 0
    # loop: the only step with the API key
    notebook = (out / "notebook.jsonl").open("a", encoding="utf-8")

    def emit(event: dict) -> None:
        notebook.write(json.dumps(event, ensure_ascii=False) + "\n")
        notebook.flush()

    researcher, record = None, {}
    try:
        model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        import anthropic

        lab = observed_lab(args)
        client = anthropic.Anthropic(timeout=480.0, max_retries=0)
        researcher = Researcher(client, model_id, lab, emit=emit)
        record = researcher.run()
        record.update(t0_forecasts=lab.inst.rows, sanitised=lab.inst.sanitised)
        failure = None
    except Exception as exc:  # recorded, never lost: the evaluate job reports it as verdict row 0
        failure = {"kind": "integrity" if isinstance(exc, IntegrityError) else "crash",
                   "error": f"{type(exc).__name__}: {exc}"[:2000], "traceback": traceback.format_exc()[-4000:]}
        if researcher is not None:
            record = {"calls": researcher.calls, "tokens_used": researcher.tokens, "final_valid": False,
                      "system_sha256": sha256_text(researcher.system)}
    finally:
        notebook.close()
    (out / "ai.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    (out / "integrity.json").write_text(json.dumps({"failure": failure}, indent=1) + "\n")
    print(json.dumps({"failure": failure and failure["error"], "tokens_used": record.get("tokens_used"),
                      "final_selection": record.get("final_selection")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
