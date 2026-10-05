"""The Kernel1 observe step: the observed data of each hidden world, nothing else (KERNEL1_SPEC.md sections 3-4).

Worlds come from ``world.kernel_world``. Days 1-126 of the target and of X01-X08 are exported per world to
``<out>/<world>/observed.npz`` with a neutral ``observed.json`` (world id, keys, days, array hash; no spec hash, run id
or kind), and each world's research job downloads only its own directory. Seeds:
- scored run: twelve worlds w01-w12, ``int(sha256('kernel1:<kernel1_spec_sha>:<run id>:<world>')[:16], 16)``, with
  their kinds (8 change, 2 stable, 2 null) permuted by ``int(sha256('kernel1:<kernel1_spec_sha>:<run id>:types')
  [:16], 16)``; the hash covers the spec, the researcher (all of discovery1's frozen files), the rules, the evaluator
  and the workflow, so no scored world can exist before they are frozen;
- preflight: one change world w01, ``int(sha256('kernel1-preflight:<run id>')[:16], 16)``, non-scored.

Refusals: t0-beta must be pinned, every frozen file present and the lesson matching its hash. The scored run also
needs a published Kernel1 preflight PASS under the same ``kernel1_spec_sha``, must be the run's first attempt (a
re-run would hand the same worlds to a fresh researcher) and must find no published scored Kernel1 run (one scored
batch only).

    python -m research_loop_proof.kernel1.truth.observe --mode preflight|run --run-id ID --run-attempt N \
        [--preflight-dir D] [--published-dir D] --out D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.observe import _run_id
from research_loop_proof.kernel1.truth import spec
from research_loop_proof.kernel1.truth.world import (PB, PREFLIGHT_KIND, PREFLIGHT_WORLD, SCORED_WORLDS, world_from,
                                                     world_kinds)
from research_loop_proof.learn1.lab.researcher import frozen_lesson
from research_loop_proof.phase0.truth.generator import World, arrays_sha256, observed_arrays

RUN_PHASE = "kernel1-run"
PREFLIGHT_PHASE = "kernel1-preflight"


def worlds_of(mode: str) -> tuple[str, ...]:
    return SCORED_WORLDS if mode == "run" else (PREFLIGHT_WORLD,)


def kinds(run_id: str) -> dict:
    return world_kinds(spec.spec_sha(), _run_id(run_id))


def hidden_world(run_id: str, k: str) -> World:
    if k not in SCORED_WORLDS:
        raise ValueError(f"unknown world {k!r}")
    return world_from(f"kernel1:{spec.spec_sha()}:{_run_id(run_id)}:{k}", kinds(run_id)[k])


def preflight_world(run_id: str) -> World:
    return world_from(f"kernel1-preflight:{_run_id(run_id)}", PREFLIGHT_KIND)


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
        errs.append(f"it ran under kernel1_spec_sha {v.get('spec_sha')}, not the current {spec.spec_sha()}")
    return errs


def scored_runs(published_dir: str | None) -> list[str]:
    """Published Kernel1 runs whose verdict is a scored run's (``<published_dir>/<run id>/verdict.json``)."""
    found = []
    for p in sorted(Path(published_dir).glob("*/verdict.json")) if published_dir else []:
        try:
            if json.loads(p.read_text()).get("phase") == RUN_PHASE:
                found.append(p.parent.name)
        except (OSError, ValueError):
            found.append(p.parent.name + " (unreadable verdict)")
    return found


def refusals(mode: str, run_attempt: str, preflight_dir: str | None, published_dir: str | None) -> list[str]:
    errs = [] if t0_beta.PINNED else ["t0-beta is not pinned"]
    if spec.missing():
        errs.append("frozen files missing: " + ", ".join(spec.missing()))
    try:
        frozen_lesson()
    except Exception as exc:
        errs.append(str(exc))
    if mode == "run":
        errs += published_errors(Path(preflight_dir or "missing"), PREFLIGHT_PHASE)
        if str(run_attempt) != "1":
            errs.append(f"run attempt {run_attempt}: the scored batch is dispatched once and never re-run")
        if published_dir is None or not Path(published_dir).is_dir():
            errs.append("the list of published Kernel1 runs was not provided")
        elif scored_runs(published_dir):
            errs.append("a scored Kernel1 run is already published: " + ", ".join(scored_runs(published_dir)))
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "run"], required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--run-attempt", required=True)
    ap.add_argument("--preflight-dir")
    ap.add_argument("--published-dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    errs = refusals(args.mode, args.run_attempt, args.preflight_dir, args.published_dir)
    if errs:
        print("refused: " + "; ".join(errs))
        return 1
    out = Path(args.out)
    shas = {}
    for k in worlds_of(args.mode):
        w = preflight_world(args.run_id) if args.mode == "preflight" else hidden_world(args.run_id, k)
        obs = observed_arrays(w, PB["observed_days"][1])
        (out / k).mkdir(parents=True, exist_ok=True)
        np.savez(out / k / "observed.npz", **obs)
        meta = {"world": k, "days": PB["observed_days"], "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)}
        (out / k / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
        shas[k] = meta["arrays_sha256"]
    print(json.dumps({"mode": args.mode, "spec_sha": spec.spec_sha(), "run_id": args.run_id, "worlds": shas}))
    (out / "shas.env").write_text("".join(f"{k}={sha}\n" for k, sha in shas.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
