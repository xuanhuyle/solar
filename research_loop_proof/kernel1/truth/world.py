"""Kernel1 worlds (KERNEL1_SPEC.md section 3): Discovery1's eight-candidate world in three kinds.

Every world starts from discovery1's ``make_world8(seed)``: the frozen Phase 0 generator (154 days, change day
86 + U{0..6}, linear effect, m = 2), the candidates R, E, D, N1-N5 standardised on days 1..tau-1 with random observed
signs, and a seeded permutation of the eight roles to X01-X08. Only the target differs between the kinds. With
c = sqrt(0.75 m), z_R and z_E the standardised R and E series (x = sign * z, so z = sign * x exactly) and ``before``
the hours of days 1..tau-1 (the absolute hour index):

- change: make_world8's target, unchanged (R predictive before the change, E after it; D is E's proxy; N1-N5 noise);
- stable: y - c * where(before, z_R, z_E) + c * z_R  (R predictive throughout; E never turns on);
- null:   y - c * where(before, z_R, z_E) + c * z_U  (no candidate has any effect). z_U is an unobserved series drawn
  the way a candidate is drawn, from the eighth child stream of the seed (make_world8 uses the first seven, which are
  unchanged), standardised on days 1..tau-1; it keeps the target's scale equal to the other kinds' and is never
  exported.

The candidate arrays, the change-day draw (in stable and null worlds only the standardisation window) and the id
permutation are the same for every kind of a given seed. Twelve scored worlds w01-w12 get their kinds (8 change,
2 stable, 2 null) from a permutation seeded by the spec hash and the run id, so neither a world nor its kind exists
before the scored run is dispatched.
"""
from __future__ import annotations

import hashlib
from dataclasses import replace

import numpy as np

from research_loop_proof.discovery1.truth.world import NOISE, PB, ROLES8, make_world8
from research_loop_proof.phase0.truth.generator import WORLD, World, _candidate, seed_of

H = WORLD["hours_per_day"]
KINDS = ("change", "stable", "null")
COMPOSITION = (("change", 8), ("stable", 2), ("null", 2))
SCORED_WORLDS = tuple(f"w{i:02d}" for i in range(1, 13))
PREFLIGHT_WORLD = "w01"
PREFLIGHT_KIND = "change"


def effect_scale(m: float) -> float:
    return float(np.sqrt(0.75 * m))


def unobserved(seed: int, n_days: int, tau: int) -> np.ndarray:
    """The null world's unobserved series z_U: a candidate-like series from the seed's eighth child stream,
    standardised on days 1..tau-1."""
    rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(8)[7])
    raw = _candidate(rng, n_days)
    pre = slice(0, (tau - 1) * H)
    return (raw - raw[pre].mean()) / raw[pre].std()


def kernel_world(seed: int, kind: str) -> World:
    if kind not in KINDS:
        raise ValueError(f"unknown world kind {kind!r}")
    w = make_world8(seed)
    if w.form != "linear":
        raise ValueError("Kernel1 worlds use the linear effect form")
    c = effect_scale(w.m)
    z_r, z_e = w.signs["R"] * w.x["R"], w.signs["E"] * w.x["E"]
    before = np.arange(w.n_days * H) < (w.tau - 1) * H
    if kind == "change":
        y = w.y
    else:
        no_effect = w.y - c * np.where(before, z_r, z_e)
        y = no_effect + c * (z_r if kind == "stable" else unobserved(seed, w.n_days, w.tau))
    canary = "CANARY-" + hashlib.sha256(f"kernel1:{seed}".encode()).hexdigest()[:20]
    return replace(w, y=y, canary=canary)


def world_from(text: str, kind: str) -> World:
    return kernel_world(seed_of(text), kind)


def world_kinds(spec_sha: str, run_id: str) -> dict:
    """The kind of each scored world: COMPOSITION in order, permuted by a seed from the spec hash and the run id."""
    pool = [kind for kind, n in COMPOSITION for _ in range(n)]
    perm = np.random.default_rng(seed_of(f"kernel1:{spec_sha}:{run_id}:types")).permutation(len(pool))
    return {k: pool[int(perm[i])] for i, k in enumerate(SCORED_WORLDS)}


__all__ = ["COMPOSITION", "H", "KINDS", "NOISE", "PB", "PREFLIGHT_KIND", "PREFLIGHT_WORLD", "ROLES8",
           "SCORED_WORLDS", "effect_scale", "kernel_world", "unobserved", "world_from", "world_kinds"]
