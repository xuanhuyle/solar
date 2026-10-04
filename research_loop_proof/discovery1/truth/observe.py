"""The Discovery1 observe step: the observed data of the hidden worlds, nothing else (NEXT_DISCOVERY_MILESTONE_PROMPT.md,
"Three-world frozen batch").

Worlds come from ``world.make_world8`` (Phase 0's beta1-parameter world with eight anonymous candidates): days 1-126 are
exported, days 127-154 are kept for confirmation. Seeds:
- scored run: three worlds w1, w2, w3, ``int(sha256('discovery1:<discovery1_spec_sha>:<run id>:w<k>')[:16], 16)``;
  the hash covers the spec, the researcher, the comparator and the evaluator, so no scored world can exist before they
  are frozen, and the worlds exist only once the run is dispatched;
- preflight: one world w1, ``int(sha256('discovery1-preflight:<run id>')[:16], 16)``, non-scored and expendable.

Refusals: t0-beta must be pinned, every frozen file present and the lesson matching its hash; the scored run also needs
a published Discovery1 preflight PASS under the same ``discovery1_spec_sha``.

    python -m research_loop_proof.discovery1.truth.observe --mode preflight|run --run-id ID [--preflight-dir D] --out D
                                                                          # writes D/w<k>/observed.{npz,json}
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
from research_loop_proof.discovery1.truth import spec
from research_loop_proof.discovery1.truth.world import PB, world_from
from research_loop_proof.learn1.lab.researcher import frozen_lesson
from research_loop_proof.phase0.truth.generator import World, arrays_sha256, observed_arrays

SCORED_WORLDS = ("w1", "w2", "w3")
PREFLIGHT_WORLDS = ("w1",)


def worlds_of(mode: str) -> tuple[str, ...]:
    return SCORED_WORLDS if mode == "run" else PREFLIGHT_WORLDS


def hidden_world(run_id: str, k: str) -> World:
    if k not in SCORED_WORLDS:
        raise ValueError(f"unknown world {k!r}")
    return world_from(f"discovery1:{spec.spec_sha()}:{_run_id(run_id)}:{k}")


def preflight_world(run_id: str) -> World:
    return world_from(f"discovery1-preflight:{_run_id(run_id)}")


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
        errs.append(f"it ran under discovery1_spec_sha {v.get('spec_sha')}, not the current {spec.spec_sha()}")
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
        errs += published_errors(Path(preflight_dir or "missing"), "discovery1-preflight")
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
    out = Path(args.out)
    summary = {"mode": args.mode, "spec_sha": spec.spec_sha(), "run_id": args.run_id, "worlds": {}}
    for k in worlds_of(args.mode):
        w = preflight_world(args.run_id) if args.mode == "preflight" else hidden_world(args.run_id, k)
        obs = observed_arrays(w, PB["observed_days"][1])
        (out / k).mkdir(parents=True, exist_ok=True)
        np.savez(out / k / "observed.npz", **obs)
        meta = {"mode": args.mode, "world": k, "spec_sha": spec.spec_sha(), "run_id": args.run_id,
                "days": PB["observed_days"], "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)}
        (out / k / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
        summary["worlds"][k] = meta["arrays_sha256"]
    (out / "observed.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
