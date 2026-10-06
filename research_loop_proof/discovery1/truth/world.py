"""Discovery1 worlds: Phase 0's world family extended from four to eight anonymous candidates
(NEXT_DISCOVERY_MILESTONE_PROMPT.md, "Minimal design").

The base world is the frozen Phase 0 world with beta1's parameters, unchanged (``phase0/truth/generator.make_world``
with world.json's "phase_b" values): 154 days, the change on day 86 + U{0..6}, the same target and effect calibration,
a retired driver R, an emerging driver E (linear), D = 0.8*E + 0.6*independent (a correlated proxy of E with no causal
effect) and one independent noise candidate, here N1. Four more independent noise candidates N2-N5 are drawn like every
other candidate (Phase 0's ``_candidate``) from new child streams of the same seed, standardised on pre-change days and
given random observed signs. The target depends only on R and E, so it is the base world's target, bit for bit: the
regime change, calibration and observation schedule are the same. The eight roles are mapped to X01-X08 by a seeded
permutation (the base world's four-candidate ids are not used).

Child streams of ``SeedSequence(seed)``: 0-3 are the base world's (series, change day, ids, signs), 4 draws N2-N5, 5
their signs, 6 the eight-role permutation.
"""
from __future__ import annotations

import hashlib

import numpy as np

from research_loop_proof.phase0.truth.generator import WORLD, World, _candidate, make_world, seed_of

PB = WORLD["phase_b"]
ROLES8 = ("R", "E", "D", "N1", "N2", "N3", "N4", "N5")
NOISE = ROLES8[3:]


def make_world8(seed: int) -> World:
    base = make_world(seed, n_days=PB["n_days"], tau=None, form=PB["form"], m=WORLD["calibration"]["m"],
                      tau_rule=True)
    n = base.n_days
    noise_ss, sign_ss, ids_ss = np.random.SeedSequence(seed).spawn(7)[4:]
    rng = np.random.default_rng(noise_ss)
    pre = slice(0, (base.tau - 1) * WORLD["hours_per_day"])
    signs = np.random.default_rng(sign_ss).integers(0, 2, size=4) * 2 - 1
    x = {"R": base.x["R"], "E": base.x["E"], "D": base.x["D"], "N1": base.x["N"]}
    sign = {"R": base.signs["R"], "E": base.signs["E"], "D": base.signs["D"], "N1": base.signs["N"]}
    for role, s in zip(NOISE[1:], signs):
        raw = _candidate(rng, n)
        x[role] = int(s) * (raw - raw[pre].mean()) / raw[pre].std()
        sign[role] = int(s)
    perm = np.random.default_rng(ids_ss).permutation(8)
    ids = {role: f"X0{perm[i] + 1}" for i, role in enumerate(ROLES8)}
    canary = "CANARY-" + hashlib.sha256(f"discovery1:{seed}".encode()).hexdigest()[:20]
    return World(seed=seed, n_days=n, tau=base.tau, form=base.form, m=base.m, y=base.y, x=x, ids=ids, canary=canary,
                 signs=sign)


def world_from(text: str) -> World:
    return make_world8(seed_of(text))
