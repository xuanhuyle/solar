"""Final-kernel worlds and company designs (FINAL_KERNEL_SPEC.md sections 3-4).

Sequences (frozen; A is a source of the company's family F_A, B and C a source of its other three-source family F_O,
the two-source family is never useful; regimes are indices 0, 1, 2 of the company's regime descriptor):

    S1: E1 (0, A)  E2 (1, B: P2, A stale)          E3 (0, A: P1 recurrence)
    S2: E1 (0, A)  E2 (1, C: P3, unhelpful before) E3 (2, none: P4 null)
    S3: E1 (0, A)  E2 (0, A: P1 recurrence)        E3 (1, B: P2, A stale)
    S4: E1 (0, A)  E2 (1, none: P4 null)           E3 (2, C: P3, unhelpful before)

Every episode's event log names both three-source families (the genuine family and the other one), so the text never
tells them apart; null episodes' genuine clue is the regime change.

Seeded per run (``design``): which company gets which sequence, the X ids of each company's sources (stable across its
episodes), which three-source family is F_A, and which source of F_A is A and of F_O is B/C. Each episode is a world
from discovery1's ``make_world8(seed)``: the measurement pair of the company takes roles E and D (D = 0.8 E + 0.6
independent), the useful source takes role R when it is outside the pair, the remaining sources take N1-N5 and the
spare R in seeded order. The target is make_world8's with both of its effects removed and the useful source's effect
c * z added for the whole episode (in a null episode, kernel1's unobserved z_U instead), so relationships hold within
an episode and change only between episodes, as the regime descriptor shows.
"""
from __future__ import annotations

import hashlib
from dataclasses import replace

import numpy as np

from research_loop_proof.discovery1.truth.world import make_world8
from research_loop_proof.final_kernel.truth import companies as C
from research_loop_proof.kernel1.truth.world import effect_scale, unobserved
from research_loop_proof.phase0.truth.generator import WORLD, World, seed_of

H = WORLD["hours_per_day"]
COMPANY_KEYS = tuple(c["key"] for c in C.COMPANIES)
EPISODES = (1, 2, 3)
SCORED_EPISODES = (2, 3)
# per sequence: per episode (regime index, useful source letter or None, pattern label or None)
SEQUENCES = {
    "S1": ((0, "A", None), (1, "B", "P2"), (0, "A", "P1")),
    "S2": ((0, "A", None), (1, "C", "P3"), (2, None, "P4")),
    "S3": ((0, "A", None), (0, "A", "P1"), (1, "B", "P2")),
    "S4": ((0, "A", None), (1, None, "P4"), (2, "C", "P3")),
}
ROLE_ORDER = ("R", "N1", "N2", "N3", "N4", "N5")


def company(key: str) -> dict:
    return next(c for c in C.COMPANIES if c["key"] == key)


def design(spec_sha: str, run_id: str, *, preflight: bool = False) -> dict:
    """The seeded design of every company: its sequence, X ids, F_A/F_O and its letters A/B/C (source indices)."""
    if preflight:
        keys = ("c1",)
        seqs = {"c1": "S1"}
        prefix = f"final_kernel-preflight:{run_id}"
    else:
        keys = COMPANY_KEYS
        perm = np.random.default_rng(seed_of(f"final_kernel:{spec_sha}:{run_id}:sequences")).permutation(4)
        seqs = {k: f"S{int(perm[i]) + 1}" for i, k in enumerate(keys)}
        prefix = f"final_kernel:{spec_sha}:{run_id}"
    out = {}
    for k in keys:
        comp = company(k)
        rng = np.random.default_rng(seed_of(f"{prefix}:{k}:design"))
        srcs = C.sources(comp)
        xperm = rng.permutation(C.SOURCES_PER_COMPANY)
        x_ids = {i: f"X0{int(xperm[i]) + 1}" for i in range(len(srcs))}
        fa = int(rng.integers(0, 2))
        fo = 1 - fa
        in_fam = {f: [i for i, s in enumerate(srcs) if s["family"] == f] for f in (0, 1)}
        a = int(rng.choice(in_fam[fa]))
        bc = int(rng.choice(in_fam[fo]))
        out[k] = {"company": k, "sequence": seqs[k], "x_ids": x_ids, "F_A": fa, "F_O": fo,
                  "letters": {"A": a, "B": bc, "C": bc}, "prefix": prefix}
    return out


def episode_plan(d: dict, episode: int) -> dict:
    regime, letter, pattern = SEQUENCES[d["sequence"]][episode - 1]
    useful = None if letter is None else d["letters"][letter]
    return {"episode": episode, "regime": regime, "letter": letter, "pattern": pattern, "useful_source": useful}


def useful_sources(comp: dict, source: int | None) -> list[int]:
    """The useful source plus its pair partner when it belongs to the measurement pair."""
    if source is None:
        return []
    srcs = C.sources(comp)
    if srcs[source]["pair"]:
        return sorted(i for i, s in enumerate(srcs) if s["pair"])
    return [source]


def episode_world(d: dict, episode: int) -> tuple[World, dict]:
    """The episode's world and its truth (roles by source, useful/stale/irrelevant X ids)."""
    comp = company(d["company"])
    plan = episode_plan(d, episode)
    seed = seed_of(f"{d['prefix']}:{d['company']}:{episode}")
    w = make_world8(seed)
    srcs = C.sources(comp)
    pair = [i for i, s in enumerate(srcs) if s["pair"]]
    role_of = {pair[0]: "E", pair[1]: "D"}
    useful = plan["useful_source"]
    rest = [i for i in range(len(srcs)) if i not in role_of]
    if useful is not None and useful not in role_of:
        role_of[useful] = "R"
        rest.remove(useful)
        slots = list(ROLE_ORDER[1:])
    else:
        slots = list(ROLE_ORDER)
    order = np.random.default_rng(np.random.SeedSequence(seed).spawn(9)[8]).permutation(len(rest))
    for slot, j in zip(slots, order):
        role_of[rest[int(j)]] = slot
    c = effect_scale(w.m)
    z = {r: w.signs[r] * w.x[r] for r in w.x}
    before = np.arange(w.n_days * H) < (w.tau - 1) * H
    base = w.y - c * np.where(before, z["R"], z["E"])
    y = base + c * (z[role_of[useful]] if useful is not None else unobserved(seed, w.n_days, w.tau))
    ids = {role_of[i]: d["x_ids"][i] for i in range(len(srcs))}
    canary = "CANARY-" + hashlib.sha256(f"final_kernel:{seed}".encode()).hexdigest()[:20]
    world = replace(w, y=y, ids=ids, canary=canary)
    useful_x = [d["x_ids"][i] for i in useful_sources(comp, useful)]
    earlier = [episode_plan(d, e)["useful_source"] for e in range(1, episode)]
    stale = sorted({d["x_ids"][i] for u in earlier for i in useful_sources(comp, u)} - set(useful_x))
    truth = {"seed": seed, "plan": plan, "roles": {d["x_ids"][i]: role_of[i] for i in range(len(srcs))},
             "useful": sorted(useful_x), "stale": stale,
             "irrelevant": sorted(set(d["x_ids"].values()) - set(useful_x)),
             "useful_names": [srcs[i]["name"] for i in useful_sources(comp, useful)], "tau": w.tau}
    return world, truth


def episode_context(d: dict, episode: int) -> dict:
    """The episode's context: both three-source families named in the event log (role-free), the regime, the
    dictionary under the company's X ids."""
    comp = company(d["company"])
    plan = episode_plan(d, episode)
    rng = np.random.default_rng(seed_of(f"{d['prefix']}:{d['company']}:{episode}:events"))
    events = C.event_log(comp, [0, 1], rng)
    return C.context(comp, d["x_ids"], episode, plan["regime"], events)
