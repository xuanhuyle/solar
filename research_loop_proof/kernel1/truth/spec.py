"""The files the Kernel1 result depends on and their combined hash (``kernel1_spec_sha``).

The new Kernel1 files (the spec document, the world kinds, the observe step, the scoring rules, the evaluator, the
preflight check and the workflow) plus every file discovery1's own hash covers: the researcher L8 and its research
job exactly as Discovery1 froze them (discovery1's lab, learn1's frozen lesson and conditions, beta1's brief,
researcher and t0-beta, Phase 0's generator, world parameters, menu, executor, instruments and evaluator helpers), and
beta1's operational preflight check, which Kernel1's check reuses. Any change to one of them changes the hash; the
twelve scored worlds' seeds and kinds are derived from it, and the scored run refuses unless the preflight ran under
the same hash. Until the spec is frozen its file is missing; ``missing()`` lists such files and no world is generated
while any is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from research_loop_proof.discovery1.truth.spec import FROZEN as DISCOVERY1_FROZEN

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/KERNEL1_SPEC.md",
    "research_loop_proof/kernel1/truth/world.py",
    "research_loop_proof/kernel1/truth/observe.py",
    "research_loop_proof/kernel1/truth/rules.py",
    "research_loop_proof/kernel1/truth/evaluate.py",
    "research_loop_proof/kernel1/truth/preflight.py",
    ".github/workflows/research-loop-kernel1.yml",
    "research_loop_proof/beta1/truth/preflight.py",
) + DISCOVERY1_FROZEN


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() if (root / rel).is_file() else "missing"
            for rel in FROZEN}


def missing(root: Path = ROOT) -> list[str]:
    return [rel for rel, h in file_hashes(root).items() if h == "missing"]


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
