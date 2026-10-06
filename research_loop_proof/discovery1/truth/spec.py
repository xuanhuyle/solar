"""The files the Discovery1 result depends on and their combined hash (``discovery1_spec_sha``).

The new Discovery1 files (spec document, the eight-candidate lab, researcher L8, the fixed comparator, the research job,
the world, the observe step and the evaluator) plus every file learn1's own hash covers, which Discovery1 reuses
unchanged (the frozen lesson, learn1's conditions, beta1's brief, researcher and t0-beta, Phase 0's generator, world
parameters, menu, executor, instruments and behaviours). Any change to one of them changes the hash; the three scored
worlds' seeds are derived from it, and the scored run refuses unless the preflight ran under the same hash. Until the
spec is frozen its file is missing; ``missing()`` lists such files and no world is generated while any is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from research_loop_proof.learn1.truth.spec import FROZEN as LEARN1_FROZEN

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/DISCOVERY1_SPEC.md",
    "research_loop_proof/discovery1/lab/executor.py",
    "research_loop_proof/discovery1/lab/researcher.py",
    "research_loop_proof/discovery1/lab/comparator.py",
    "research_loop_proof/discovery1/lab/run.py",
    "research_loop_proof/discovery1/truth/world.py",
    "research_loop_proof/discovery1/truth/observe.py",
    "research_loop_proof/discovery1/truth/evaluate.py",
) + LEARN1_FROZEN


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() if (root / rel).is_file() else "missing"
            for rel in FROZEN}


def missing(root: Path = ROOT) -> list[str]:
    return [rel for rel, h in file_hashes(root).items() if h == "missing"]


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
