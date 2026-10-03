"""Phase B's observe step (PHASE0_SPEC.md section 4): the hidden world's observed data, nothing else.

It refuses unless the published Phase A verdict is PASS under the current ``spec_sha``. The world's seed is
``int(sha256('<spec_sha>:<this run id>')[:16], 16)``. Exported: the target and the anonymous candidates X01-X04
for days 1-126, and their hash over the raw array bytes. The roles, the change day, the signs and days 127-154 stay
here; only the evaluate job regenerates them.

    python -m research_loop_proof.phase0.truth.observe --run-id ID --phase-a-dir DIR --out DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.phase0.truth.generator import WORLD, World, arrays_sha256, make_world, observed_arrays, seed_of
from research_loop_proof.phase0.truth.spec import spec_sha

PB = WORLD["phase_b"]


def hidden_world(run_id: str) -> World:
    if not str(run_id).isdigit():
        raise ValueError("the run id must be the dispatched run's numeric id")
    return make_world(seed_of(f"{spec_sha()}:{run_id}"), n_days=PB["n_days"], tau=None, form=PB["form"],
                      m=WORLD["calibration"]["m"], tau_rule=True)


def phase_a_errors(phase_a_dir: Path) -> list[str]:
    """Why the published Phase A result does not allow Phase B (empty when it does)."""
    try:
        verdict_bytes = (phase_a_dir / "verdict.json").read_bytes()
        manifest = (phase_a_dir / "MANIFEST.sha256").read_text()
    except OSError as exc:
        return [f"Phase A result not readable: {exc}"]
    listed = {line[66:].strip(): line[:64] for line in manifest.splitlines() if len(line) > 66}
    errs = []
    if listed.get("verdict.json") != hashlib.sha256(verdict_bytes).hexdigest():
        errs.append("verdict.json does not match the Phase A manifest")
    v = json.loads(verdict_bytes)
    if v.get("phase") != "A" or v.get("verdict") != "PASS":
        errs.append(f"the Phase A verdict is {v.get('verdict')!r}, not PASS")
    if v.get("spec_sha") != spec_sha():
        errs.append(f"Phase A ran under spec_sha {v.get('spec_sha')}, not the current {spec_sha()}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--phase-a-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    errs = phase_a_errors(Path(args.phase_a_dir))
    if errs:
        print("Phase B refused: " + "; ".join(errs))
        return 1
    w = hidden_world(args.run_id)
    obs = observed_arrays(w, PB["observed_days"][1])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "observed.npz", **obs)
    meta = {"spec_sha": spec_sha(), "run_id": args.run_id, "days": PB["observed_days"], "keys": sorted(obs),
            "arrays_sha256": arrays_sha256(obs)}
    (out / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
