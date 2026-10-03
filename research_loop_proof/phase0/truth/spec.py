"""The frozen Phase 0 rule files and their combined hash (``spec_sha``).

The rule files define the worlds, the calibration, the two instruments, the Phase A gate, the researcher's brief
and menu, and the written spec. Any change to one of them changes ``spec_sha``. Phase B refuses to run unless Phase A's published verdict carries the
same ``spec_sha``, and the hidden world's seed is derived from it (with the scored run's id).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/PHASE0_SPEC.md",
    "research_loop_proof/phase0/truth/world.json",
    "research_loop_proof/phase0/truth/generator.py",
    "research_loop_proof/phase0/truth/calibrate.py",
    "research_loop_proof/phase0/truth/phase_a.py",
    "research_loop_proof/phase0/lab/instruments.py",
    "research_loop_proof/phase0/lab/menu.json",
    "research_loop_proof/phase0/lab/brief.md",
)


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in FROZEN}


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
