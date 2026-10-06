"""The files the policy1 result depends on and their combined hash (``policy1_spec_sha``).

The new policy1 files (spec, architecture note, the two conditions, the research job, the world, the evaluator) plus
every file learn1's own hash covers, which policy1 reuses unchanged (the frozen lesson, learn1's conditions, beta1's
brief, researcher and t0-beta, Phase 0's generator, world parameters, menu, executor, instruments and behaviours). Any
change to one of them changes the hash; the scored world's seed is derived from it, and the scored run refuses unless
the preflight ran under the same hash. Until the spec is frozen its file is missing; ``missing()`` lists such files
and no scored or preflight world is generated while any is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from research_loop_proof.learn1.truth.spec import FROZEN as LEARN1_FROZEN

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/POLICY1_SPEC.md",
    "docs/research_loop_proof/POLICY1_ARCHITECTURE.md",
    "research_loop_proof/policy1/lab/researcher.py",
    "research_loop_proof/policy1/lab/run.py",
    "research_loop_proof/policy1/truth/observe.py",
    "research_loop_proof/policy1/truth/evaluate.py",
) + LEARN1_FROZEN


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() if (root / rel).is_file() else "missing"
            for rel in FROZEN}


def missing(root: Path = ROOT) -> list[str]:
    return [rel for rel, h in file_hashes(root).items() if h == "missing"]


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
