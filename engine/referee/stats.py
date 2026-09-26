"""Statistics the referee owns (numpy + the standard library; no scipy).

* **Verdict test** (vault): a one-sided t-test on 14-day block means of
  ``z = (1 - delta) * loss_ref - loss_arm`` - the null is "skill <= delta".
  With fewer than ``MIN_BLOCKS`` blocks the p-value is 1.
* **Holm** within a claim batch (<= 4 claims).
* **alpha spending** across the ledger: 0.05 split evenly over
  ``BATCH_BUDGET`` pre-declared confirmation batches.
* **power_table**: the minimum detectable skill at 6 and 8 blocks, from the
  day-to-day spread of a discovery comparison (ledgered before a freeze).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

ALPHA_TOTAL = 0.05
BATCH_BUDGET = 4
BLOCK_DAYS = 14
MIN_BLOCKS = 6


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularised incomplete beta (Numerical Recipes, Lentz)."""
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    return h


def betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    front = math.exp(lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: int) -> float:
    """P(T > t) for Student's t with ``df`` degrees of freedom."""
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return tail if t >= 0 else 1.0 - tail


#: A calendar block counts only if at least this many of its days were scored for both methods.
MIN_DAYS_PER_BLOCK = 10


def blocks(per_day: pd.DataFrame, arm: str, ref: str, delta: float, block_days: int = BLOCK_DAYS,
           start=None, n_blocks: int | None = None) -> np.ndarray:
    """Block means of the shifted loss difference ``(1 - delta) * loss_ref - loss_arm``.

    Blocks are *calendar* spans of ``block_days`` from ``start`` (default: the first common day),
    so a missing day shrinks one block instead of shifting every later one; a block counts only
    with at least ``MIN_DAYS_PER_BLOCK`` common days. ``n_blocks`` limits them to a fixed window
    (the vault's 6). The vault rehearsal found that cutting blocks from consecutive *scored* days
    lost a whole block - and forced p := 1 - whenever a single day of the 84 was missing.
    """
    wide = per_day.pivot(index="delivery_date", columns="method", values="sum_abs_err")[[arm, ref]].dropna().sort_index()
    if wide.empty:
        return np.array([])
    n = per_day.pivot(index="delivery_date", columns="method", values="n").loc[wide.index, [arm, ref]]
    z = ((1.0 - delta) * wide[ref] / n[ref] - wide[arm] / n[arm]).astype("float64")
    days = pd.to_datetime(pd.Index(wide.index))
    origin = pd.Timestamp(start) if start is not None else days.min()
    idx = np.asarray((days - origin).days // block_days)
    keep = idx >= 0
    if n_blocks is not None:
        keep &= idx < n_blocks
    groups = pd.Series(z.to_numpy()[keep]).groupby(idx[keep])
    counts, means = groups.size(), groups.mean()
    return means[counts >= MIN_DAYS_PER_BLOCK].to_numpy(dtype="float64")


def block_t_test(per_day: pd.DataFrame, arm: str, ref: str, delta: float, *, start=None,
                 n_blocks: int | None = None) -> dict:
    b = blocks(per_day, arm, ref, delta, start=start, n_blocks=n_blocks)
    if len(b) < MIN_BLOCKS:
        return {"blocks": int(len(b)), "t": None, "p": 1.0, "note": f"fewer than {MIN_BLOCKS} blocks: p := 1"}
    mean, sd = float(b.mean()), float(b.std(ddof=1))
    if sd == 0.0:
        return {"blocks": int(len(b)), "t": None, "p": 0.0 if mean > 0 else 1.0, "note": "zero variance"}
    t = mean / (sd / math.sqrt(len(b)))
    return {"blocks": int(len(b)), "t": round(t, 6), "p": t_sf(t, len(b) - 1), "mean_z": mean}


def holm(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    m = len(pvalues)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def alpha_for_batch(batches_spent: int) -> float:
    """Uniform alpha spending: each of the ``BATCH_BUDGET`` batches gets 0.05 / 4; none after that."""
    if batches_spent >= BATCH_BUDGET:
        raise ValueError(f"the ledger's alpha budget ({BATCH_BUDGET} confirmation batches) is spent")
    return ALPHA_TOTAL / BATCH_BUDGET


def t_crit(df: int, alpha: float) -> float:
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_sf(mid, df) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def power_table(per_day: pd.DataFrame, arm: str, ref: str, alpha: float, blocks_list=(6, 8, 12)) -> dict:
    """Minimum detectable skill (80% power, approx.) from the spread of 14-day block means."""
    b = blocks(per_day, arm, ref, 0.0)
    if len(b) < 3:
        return {"error": "fewer than 3 blocks of discovery evidence"}
    ref_mae = float(per_day.loc[per_day["method"] == ref, "sum_abs_err"].sum()
                    / per_day.loc[per_day["method"] == ref, "n"].sum())
    sd = float(b.std(ddof=1))
    out = {}
    for k in blocks_list:
        # mean difference needed: (t_crit + z_0.8) * sd / sqrt(k), as a share of the reference loss
        mde = (t_crit(k - 1, alpha) + 0.8416) * sd / math.sqrt(k) / ref_mae
        out[str(k)] = round(mde, 4)
    return {"alpha": alpha, "block_sd_mw": round(sd, 3), "ref_mae_mw": round(ref_mae, 3), "min_detectable_skill": out}
