"""Human1 worlds and the human-supplied hypothesis packet (NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md section 4).

The world is the frozen Phase 0 world with beta1's parameters, unchanged (``phase0/truth/generator.make_world`` with
world.json's "phase_b" values, as beta1, learn1 and policy1 used): 154 days, the change on day 86 + U{0..6}, the same
target and effect calibration, a retired driver R, an emerging driver E (linear), D = 0.8*E + 0.6*independent (a
correlated proxy of E with no incremental value once E is known) and one independent noise candidate N, each with a
random observed sign.

The packet: the evaluator supplies two of those roles as the human's hypothesis, by predeclared pair type, one per
scored world: w1 = E and D, w2 = E and N (pure noise), w3 = E and R. That E is in every packet is a benchmark condition
(a good hypothesis supplied by an external human), not a discovery claim; hypothesis generation is not tested. The two
roles are mapped to X01 and X02 by a seeded order from a new child stream of the seed (children 0-3 are the base
world's); the base world's four-candidate ids are not used. Only the target and the two supplied candidates are ever
exported. The non-scored preflight world uses the E and D pair type.
"""
from __future__ import annotations

import hashlib

import numpy as np

from research_loop_proof.phase0.truth.generator import WORLD, World, make_world, seed_of

PB = WORLD["phase_b"]
PAIRS = {"w1": ("E", "D"), "w2": ("E", "N"), "w3": ("E", "R")}
PREFLIGHT_PAIR = ("E", "D")
PAIR_TYPE = {("E", "D"): "E+D", ("E", "N"): "E+noise", ("E", "R"): "E+R"}


def make_world_pair(seed: int, pair: tuple[str, str]) -> World:
    if pair not in PAIR_TYPE:
        raise ValueError(f"unknown pair type {pair!r}")
    base = make_world(seed, n_days=PB["n_days"], tau=None, form=PB["form"], m=WORLD["calibration"]["m"],
                      tau_rule=True)
    order = np.random.default_rng(np.random.SeedSequence(seed).spawn(5)[4]).permutation(2)
    ids = {pair[int(order[0])]: "X01", pair[int(order[1])]: "X02"}
    canary = "CANARY-" + hashlib.sha256(f"human1:{seed}".encode()).hexdigest()[:20]
    return World(seed=seed, n_days=base.n_days, tau=base.tau, form=base.form, m=base.m, y=base.y, x=base.x, ids=ids,
                 canary=canary, signs=base.signs)


def world_from(text: str, pair: tuple[str, str]) -> World:
    return make_world_pair(seed_of(text), pair)
