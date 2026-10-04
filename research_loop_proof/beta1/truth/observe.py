"""The beta1 observe step: the hidden world's observed data, nothing else (NEXT_MILESTONE_PROMPT.md section 7).

The world keeps Phase B's structure and parameters unchanged (``phase0/truth/world.json`` "phase_b" and the frozen
Phase 0 generator): four anonymous candidates (a driver retired at the change, a driver emerging at it, a correlated
proxy of the new driver, noise, each with a random observed sign), 154 days, the change on day 86 + U{0..6}, days
1-126 observed, days 127-154 kept for confirmation. Seeds:
- scored run: ``int(sha256('beta1:<beta1_spec_sha>:<run id>')[:16], 16)`` - exists only once the run is dispatched;
- preflight: ``int(sha256('beta1-preflight:<run id>')[:16], 16)`` - a non-scored, expendable world.

Refusals: t0-beta must be pinned (qualified); the scored run needs a published preflight PASS under the same
``beta1_spec_sha``.

    python -m research_loop_proof.beta1.truth.observe --mode preflight|run --run-id ID [--preflight-dir D] --out D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.spec import spec_sha
from research_loop_proof.phase0.truth.generator import WORLD, World, arrays_sha256, make_world, observed_arrays, seed_of

PB = WORLD["phase_b"]


def _world(text: str) -> World:
    return make_world(seed_of(text), n_days=PB["n_days"], tau=None, form=PB["form"], m=WORLD["calibration"]["m"],
                      tau_rule=True)


def _run_id(run_id: str) -> str:
    if not str(run_id).isdigit():
        raise ValueError("the run id must be the dispatched run's numeric id")
    return str(run_id)


def hidden_world(run_id: str) -> World:
    return _world(f"beta1:{spec_sha()}:{_run_id(run_id)}")


def preflight_world(run_id: str) -> World:
    return _world(f"beta1-preflight:{_run_id(run_id)}")


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
    if v.get("spec_sha") != spec_sha():
        errs.append(f"it ran under beta1_spec_sha {v.get('spec_sha')}, not the current {spec_sha()}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "run"], required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--preflight-dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    errs = [] if t0_beta.PINNED else ["t0-beta is not pinned (qualification first)"]
    if args.mode == "run":
        errs += published_errors(Path(args.preflight_dir or "missing"), "beta1-preflight")
    if errs:
        print("refused: " + "; ".join(errs))
        return 1
    w = preflight_world(args.run_id) if args.mode == "preflight" else hidden_world(args.run_id)
    obs = observed_arrays(w, PB["observed_days"][1])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "observed.npz", **obs)
    meta = {"mode": args.mode, "spec_sha": spec_sha(), "run_id": args.run_id, "days": PB["observed_days"],
            "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)}
    (out / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
