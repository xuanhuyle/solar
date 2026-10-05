"""The files the final-kernel result depends on and their combined hash (``final_kernel_spec_sha``).

The new final-kernel files (the spec document, the lab: researcher with the data block, referee and memory, research
and referee jobs; the truth side: companies and contexts, worlds and designs, observe, scoring rules, evaluator,
preflight; the workflow) plus every file Kernel1's hash covers (which includes discovery1's researcher L8 and its
research job, learn1's frozen lesson and conditions, beta1's brief, researcher, t0-beta and preflight check, Phase 0's
generator, world parameters, menu, executor, instruments and evaluator helpers, and Kernel1's world helpers). Any change
to one of them changes the hash; the scored worlds' seeds and designs are derived from it, and the scored run refuses
unless the preflight ran under the same hash. Until the spec is frozen its file is missing; ``missing()`` lists such
files and no world is generated while any is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from research_loop_proof.kernel1.truth.spec import FROZEN as KERNEL1_FROZEN

ROOT = Path(__file__).resolve().parents[3]
FROZEN = (
    "docs/research_loop_proof/FINAL_KERNEL_SPEC.md",
    "research_loop_proof/final_kernel/lab/researcher.py",
    "research_loop_proof/final_kernel/lab/referee.py",
    "research_loop_proof/final_kernel/lab/run.py",
    "research_loop_proof/final_kernel/truth/companies.py",
    "research_loop_proof/final_kernel/truth/world.py",
    "research_loop_proof/final_kernel/truth/observe.py",
    "research_loop_proof/final_kernel/truth/rules.py",
    "research_loop_proof/final_kernel/truth/evaluate.py",
    "research_loop_proof/final_kernel/truth/preflight.py",
    ".github/workflows/research-loop-final-kernel.yml",
) + KERNEL1_FROZEN


def file_hashes(root: Path = ROOT) -> dict:
    return {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() if (root / rel).is_file() else "missing"
            for rel in FROZEN}


def missing(root: Path = ROOT) -> list[str]:
    return [rel for rel, h in file_hashes(root).items() if h == "missing"]


def spec_sha(root: Path = ROOT) -> str:
    joined = "".join(f"{rel}\0{h}\n" for rel, h in sorted(file_hashes(root).items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
