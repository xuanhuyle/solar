"""Pre-freeze measurement behind the interval block rule (PHASE0_SPEC.md section 7, item 3). Not a rule file.

Null "lower bound above 0" rate of ``metrics.pair_skill`` by window (7, 14, 28 days) and block length (1-7 days).
Ridge only, never t0; non-scored seeds 'phase0-null-<i>', linear, m = 2, change at day 60, 7-day context. The pair
is ridge{R} against ridge{N} on k = 7..34, where neither covariate has an effect and the context is fully
post-change; each window is the last 7, 14 or 28 of those days.

    python -m research_loop_proof.phase0.truth.null_rates 400 docs/research_loop_proof/phase0_null_rates.json
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from research_loop_proof.phase0.lab.instruments import ridge_forecast
from research_loop_proof.phase0.truth.generator import make_world, seed_of
from solarbench import metrics


def measure(n_worlds: int) -> dict:
    errs = []
    for i in range(n_worlds):
        w = make_world(seed_of(f"phase0-null-{i}"), n_days=96, tau=60, form="linear", m=2.0)
        row = []
        for k in range(7, 35):
            d = w.tau + k
            t = w.y[w.day_slice(d, d)]
            row.append([np.abs(ridge_forecast(w.y, [w.x[r]], d, 7) - t).sum() for r in ("R", "N")])
        errs.append(row)
    errs = np.array(errs)
    out = {"worlds": n_worlds}
    for win in (7, 14, 28):
        for b in range(1, 8):
            lo = hi = 0
            for i in range(n_worlds):
                e = errs[i, 28 - win:]
                df = pd.DataFrame([{"delivery_date": j, "method": m, "sum_abs_err": e[j, c], "n": 24}
                                   for j in range(win) for c, m in ((0, "a"), (1, "b"))])
                r = metrics.pair_skill(df, model="a", reference="b", block_days=b)
                lo += r["skill_lo95"] > 0
                hi += r["skill_hi95"] < 0
            out[f"w{win}_b{b}"] = {"lb_above_0": lo / n_worlds, "ub_below_0": hi / n_worlds}
    return out


if __name__ == "__main__":
    res = measure(int(sys.argv[1]))
    with open(sys.argv[2], "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
