"""The files the learn1 result depends on and their combined hash (``learn1_spec_sha``).

The new learn1 files (spec document, frozen lesson, conditions, research job, world, evaluator) plus every file beta1's
own hash covers, which learn1 reuses unchanged (t0-beta, the beta1 brief and researcher, the Phase 0 generator, world
parameters, menu, executor, researcher base, instruments and behaviours). Any change to one of them changes the hash;
the scored world's seed is derived from it, and the scored run refuses unless the preflight ran under the same hash.
Until the lesson is frozen its file is missing; ``missing()`` lists such files and no world is generated while any is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from research_loop_proof.beta1.truth.spec import FROZEN as BETA1_FROZEN

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/LEARN1_SPEC.md",
    "research_loop_proof/learn1/lab/lesson.json",
    "research_loop_proof/learn1/lab/researcher.py",
    "research_loop_proof/learn1/lab/run.py",
    "research_loop_proof/learn1/truth/observe.py",
    "research_loop_proof/learn1/truth/evaluate.py",
) + BETA1_FROZEN


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() if (root / rel).is_file() else "missing"
            for rel in FROZEN}


def missing(root: Path = ROOT) -> list[str]:
    return [rel for rel, h in file_hashes(root).items() if h == "missing"]


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
