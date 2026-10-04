"""The learn1 observe step: the one hidden world's observed data, nothing else (NEXT_LEARNING_MILESTONE_PROMPT.md
section 4).

The same problem family as beta1, unchanged: beta1's world function (``beta1/truth/observe._world``: Phase 0's
"phase_b" parameters and the frozen Phase 0 generator): four anonymous candidates (a driver retired at the change, a
driver emerging at it, a correlated proxy of the new driver, noise, each with a random observed sign), 154 days, the
change on day 86 + U{0..6}, days 1-126 observed, days 127-154 kept for confirmation. Both conditions research this one
world. Seeds:
- scored run: ``int(sha256('learn1:<learn1_spec_sha>:<run id>')[:16], 16)``; the hash covers the frozen lesson, so
  the world cannot exist before the lesson is frozen, and it exists only once the run is dispatched;
- preflight: ``int(sha256('learn1-preflight:<run id>')[:16], 16)``, a non-scored, expendable world.

Refusals: t0-beta must be pinned, every frozen file present (the lesson included) and the lesson matching its hash; the
scored run also needs a published learn1 preflight PASS under the same ``learn1_spec_sha``.

    python -m research_loop_proof.learn1.truth.observe --mode preflight|run --run-id ID [--preflight-dir D] --out D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.observe import PB, _run_id, _world
from research_loop_proof.learn1.lab.researcher import frozen_lesson
from research_loop_proof.learn1.truth import spec
from research_loop_proof.phase0.truth.generator import World, arrays_sha256, observed_arrays


def hidden_world(run_id: str) -> World:
    return _world(f"learn1:{spec.spec_sha()}:{_run_id(run_id)}")


def preflight_world(run_id: str) -> World:
    return _world(f"learn1-preflight:{_run_id(run_id)}")


def published_errors(d: Path, phase: str) -> list[str]:
    """Why a published result (verdict.json listed in its manifest) is not a PASS of ``phase`` under this spec."""
    try:
        body = (d / "verdict.json").read_bytes()
        manifest = (d / "MANIFEST.sha256").read_text()
    except OSError as exc:
        return [f"published result not readable: {exc}"]
    listed = {ln[66:].strip(): ln[:64] for ln in manifest.splitlines() if len(ln) > 66}
    errs = []
    if listed.get("verdict.json") != hashlib.sha256(body).hexdigest():
        errs.append("verdict.json does not match its manifest")
    v = json.loads(body)
    if v.get("phase") != phase or v.get("verdict") != "PASS":
        errs.append(f"{v.get('phase')!r} verdict {v.get('verdict')!r}, not a {phase} PASS")
    if v.get("spec_sha") != spec.spec_sha():
        errs.append(f"it ran under learn1_spec_sha {v.get('spec_sha')}, not the current {spec.spec_sha()}")
    return errs


def refusals(mode: str, preflight_dir: str | None) -> list[str]:
    errs = [] if t0_beta.PINNED else ["t0-beta is not pinned"]
    if spec.missing():
        errs.append("frozen files missing: " + ", ".join(spec.missing()))
    try:
        frozen_lesson()
    except Exception as exc:
        errs.append(str(exc))
    if mode == "run":
        errs += published_errors(Path(preflight_dir or "missing"), "learn1-preflight")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "run"], required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--preflight-dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    errs = refusals(args.mode, args.preflight_dir)
    if errs:
        print("refused: " + "; ".join(errs))
        return 1
    w = preflight_world(args.run_id) if args.mode == "preflight" else hidden_world(args.run_id)
    obs = observed_arrays(w, PB["observed_days"][1])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "observed.npz", **obs)
    meta = {"mode": args.mode, "spec_sha": spec.spec_sha(), "run_id": args.run_id, "days": PB["observed_days"],
            "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)}
    (out / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
