"""The files the beta1 result depends on and their combined hash (``beta1_spec_sha``).

New beta1 files plus the Phase 0 files it reuses unchanged (generator, world parameters, menu, executor, scripted
strategy, the researcher base, the window function and the behaviours). Any change to one of them changes the hash;
the scored world's seed is derived from it and the scored run refuses unless the preflight ran under the same hash.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/BETA1_SPEC.md",
    "research_loop_proof/beta1/lab/brief.md",
    "research_loop_proof/beta1/lab/t0_beta.py",
    "research_loop_proof/beta1/lab/researcher.py",
    "research_loop_proof/beta1/lab/run.py",
    "research_loop_proof/beta1/truth/observe.py",
    "research_loop_proof/beta1/truth/evaluate.py",
    "research_loop_proof/phase0/truth/world.json",
    "research_loop_proof/phase0/truth/generator.py",
    "research_loop_proof/phase0/truth/evaluate.py",
    "research_loop_proof/phase0/lab/menu.json",
    "research_loop_proof/phase0/lab/executor.py",
    "research_loop_proof/phase0/lab/scripted.py",
    "research_loop_proof/phase0/lab/researcher.py",
    "research_loop_proof/phase0/lab/instruments.py",
)


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in FROZEN}


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
