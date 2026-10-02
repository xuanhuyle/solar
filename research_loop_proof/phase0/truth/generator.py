"""Phase 0 worlds (docs/research_loop_proof/PHASE0_SPEC.md, frozen numbers in world.json).

One hourly target and four candidate covariates, all known in advance (known-future):
- R: drives the target before the change, nothing after (retired);
- E: nothing before the change, drives the target from the change on (emerging), linearly or through a hinge;
- D: 0.8*x_E + 0.6*x_indep, no causal effect: a correlated proxy that becomes predictive after the change;
- N: independent noise.

Total effect variance is the same before and after the change, so the target's variance does not reveal it.
Everything is deterministic in the seed (numpy PCG64; numpy is pinned in constraints-ci.txt).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
WORLD = json.loads((HERE / "world.json").read_text(encoding="utf-8"))
H = WORLD["hours_per_day"]
ROLES = ("R", "E", "D", "N")


def seed_of(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def _ar1(rng: np.random.Generator, n: int, phi: float, var: float) -> np.ndarray:
    """A stationary AR(1) of length n with marginal variance var."""
    out = np.empty(n)
    out[0] = rng.normal(0.0, np.sqrt(var))
    sd = np.sqrt(var * (1.0 - phi * phi))
    eps = rng.normal(0.0, sd, size=n)
    for t in range(1, n):
        out[t] = phi * out[t - 1] + eps[t]
    return out


def _candidate(rng: np.random.Generator, n_days: int) -> np.ndarray:
    c = WORLD["candidate"]
    level = np.repeat(_ar1(rng, n_days, c["daily_level"]["phi"], c["daily_level"]["variance"]), H)
    return level + _ar1(rng, n_days * H, c["hourly_noise"]["phi"], c["hourly_noise"]["variance"])


def _hinge_moments(q_level: float) -> tuple[float, float, float]:
    """Threshold q and the mean and sd of max(0, x - q) for x ~ N(0, 1), in closed form."""
    nd = NormalDist()
    q = nd.inv_cdf(q_level)
    tail, dens = 1.0 - nd.cdf(q), nd.pdf(q)
    mean = dens - q * tail
    second = (1.0 + q * q) * tail - q * dens
    return q, mean, float(np.sqrt(second - mean * mean))


def effect(x: np.ndarray, form: str) -> np.ndarray:
    if form == "linear":
        return x
    if form == "hinge":
        q, mean, sd = _hinge_moments(WORLD["hinge"]["quantile"])
        return (np.maximum(0.0, x - q) - mean) / sd
    raise ValueError(f"unknown form {form!r}")


@dataclass
class World:
    seed: int
    n_days: int
    tau: int  # first changed day, 1-based
    form: str
    m: float
    y: np.ndarray  # [n_days * 24]
    x: dict  # role -> [n_days * 24], standardised on pre-change days
    ids: dict = field(default_factory=dict)  # role -> X0n (Phase B only)
    canary: str = ""

    def day_slice(self, first: int, last: int) -> slice:
        """Hours of days first..last (1-based, inclusive)."""
        return slice((first - 1) * H, last * H)


def make_world(seed: int, *, n_days: int, tau: int | None, form: str, m: float, tau_rule: bool = False) -> World:
    """A world from its seed. With ``tau_rule`` the change day follows Phase B's rule (86 + U{0..6}) and the
    candidate ids are a seeded permutation; otherwise ``tau`` is given."""
    series_ss, tau_ss, ids_ss = np.random.SeedSequence(seed).spawn(3)
    rng = np.random.default_rng(series_ss)
    if tau_rule:
        tau = 86 + int(np.random.default_rng(tau_ss).integers(0, 7))
    if tau is None or not 1 < tau <= n_days:
        raise ValueError(f"bad change day {tau}")
    t = WORLD["target"]
    hours = np.arange(n_days * H) % H
    base = np.sin(2 * np.pi * (hours - 6) / 24)
    shock = np.repeat(_ar1(rng, n_days, t["daily_shock"]["phi"], t["daily_shock"]["variance"]), H)
    noise = _ar1(rng, n_days * H, t["hourly_noise"]["phi"], t["hourly_noise"]["variance"])
    raw = {"R": _candidate(rng, n_days), "E": _candidate(rng, n_days), "N": _candidate(rng, n_days)}
    indep = _candidate(rng, n_days)
    raw["D"] = 0.8 * raw["E"] + 0.6 * indep
    pre = slice(0, (tau - 1) * H)
    x = {r: (raw[r] - raw[r][pre].mean()) / raw[r][pre].std() for r in ROLES}
    c = float(np.sqrt(0.75 * m))
    before = np.arange(n_days * H) < (tau - 1) * H
    y = base + shock + noise + np.where(before, c * x["R"], c * effect(x["E"], form))
    ids = {}
    if tau_rule:
        perm = np.random.default_rng(ids_ss).permutation(4)
        ids = {role: f"X0{perm[i] + 1}" for i, role in enumerate(ROLES)}
    canary = "CANARY-" + hashlib.sha256(f"phase0:{seed}".encode()).hexdigest()[:20]
    return World(seed=seed, n_days=n_days, tau=tau, form=form, m=m, y=y, x=x, ids=ids, canary=canary)


def observed_arrays(w: World, last_day: int) -> dict:
    """What the lab may see: the target and the anonymous candidates for days 1..last_day, as float64."""
    if not w.ids:
        raise ValueError("observed export is for Phase B worlds (anonymous ids)")
    sl = w.day_slice(1, last_day)
    out = {"y": np.ascontiguousarray(w.y[sl], dtype="float64")}
    for role, xid in sorted(w.ids.items(), key=lambda kv: kv[1]):
        out[xid] = np.ascontiguousarray(w.x[role][sl], dtype="float64")
    return out


def arrays_sha256(arrays: dict) -> str:
    """sha256 over the raw bytes of the arrays in key order (a .npz file's zip metadata is not hashed)."""
    h = hashlib.sha256()
    for key in sorted(arrays):
        a = np.ascontiguousarray(arrays[key], dtype="float64")
        h.update(key.encode() + b"\0" + str(a.shape).encode() + b"\0" + a.tobytes())
    return h.hexdigest()
