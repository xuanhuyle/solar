"""Experiment 4, replication Track 3 (report-only): how much the published intervals and p depend on the seed.

The frozen bootstrap (``metrics.bootstrap_skill`` at ``2b407f4``; NOT independent) is rerun on the run's own
per-day tables with seeds 1..199 besides the frozen seed 0. For each primary this reports:
- where the published seed-0 interval endpoints and p sit in that spread;
- the share of seeds under which a primary's state would change. The states follow the frozen rules; only the
  bootstrap seed varies.

Nothing here changes a state: the seed is frozen at 0.

Usage::

    python docs/experiment_4/replication/mc_tolerance.py --frozen /tmp/exp4-frozen --artifact <unzipped dir>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FROZEN = "2b407f42c03d2734ef4170cfb3e66962dbba9552"
SEEDS = range(0, 200)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frozen", type=Path, required=True)
    ap.add_argument("--artifact", type=Path, required=True)
    args = ap.parse_args()
    head = subprocess.run(["git", "-C", str(args.frozen), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    if head != FROZEN:
        raise SystemExit(f"worktree at {head}, not {FROZEN}")
    sys.path.insert(0, str(args.frozen))
    from solarbench import metrics  # noqa: E402  (frozen)
    from solarbench import price_stats as st  # noqa: E402  (frozen)

    published = json.loads((args.artifact / "results.json").read_text())
    out = {"track": "3: Monte-Carlo spread of the frozen bootstrap (report-only, NOT independent)",
           "frozen_commit": head, "seeds": [SEEDS.start, SEEDS.stop - 1], "primaries": {}}
    p_by_seed = {}
    for pid in ("P1", "P3", "P4"):
        arm, ref, _ = st.probe_arms(pid)
        table = pd.read_csv(args.artifact / f"per_day_{pid}.csv", float_precision="round_trip")
        lo, hi, k = [], [], []
        margin = -st.MARGINS[pid]
        for seed in SEEDS:
            r = metrics.bootstrap_skill(table, model=arm, reference=ref, block_days=14, samples=2000, seed=seed,
                                        return_draws=True)
            draws = np.asarray(r["draws"], dtype="float64")
            q = np.percentile(draws, [2.5, 97.5])
            lo.append(float(q[0]))
            hi.append(float(q[1]))
            k.append(int(np.sum(draws <= margin)))
        lo, hi, k = np.array(lo), np.array(hi), np.array(k)
        pub = published["primaries"][pid]
        p_by_seed[pid] = (1 + k) / 2001
        out["primaries"][pid] = {
            "seed0_reproduces_published": bool(lo[0] == pub["ci95"][0] and hi[0] == pub["ci95"][1]
                                               and (1 + k[0]) / 2001 == pub["p"]),
            "ci_lo": {"published": pub["ci95"][0], "min": lo.min(), "p0.5": np.percentile(lo, 0.5),
                      "median": float(np.median(lo)), "p99.5": np.percentile(lo, 99.5), "max": lo.max(),
                      "published_rank_share": float(np.mean(lo <= pub["ci95"][0]))},
            "ci_hi": {"published": pub["ci95"][1], "min": hi.min(), "p0.5": np.percentile(hi, 0.5),
                      "median": float(np.median(hi)), "p99.5": np.percentile(hi, 99.5), "max": hi.max(),
                      "published_rank_share": float(np.mean(hi <= pub["ci95"][1]))},
            "draws_le_margin": {"published_k": int(round(pub["p"] * 2001 - 1)), "min": int(k.min()),
                                "median": float(np.median(k)), "max": int(k.max()),
                                "share_of_seeds_with_k_0": float(np.mean(k == 0))},
            "ci_lo_above_zero_in_every_seed": bool((lo > 0).all()),
        }
    # Holm over P1..P4 (P2 = 1) per seed; a primary's state changes only if its Holm p reaches 0.05,
    # since its pooled skill and yearly skills do not depend on the seed.
    changes = 0
    worst = 0.0
    for i in range(len(SEEDS)):
        ps = [p_by_seed["P1"][i], 1.0, p_by_seed["P3"][i], p_by_seed["P4"][i]]
        order = np.argsort(ps, kind="stable")
        adj, running = [0.0] * 4, 0.0
        for rank, idx in enumerate(order):
            running = max(running, min(1.0, (4 - rank) * ps[idx]))
            adj[idx] = running
        worst = max(worst, max(adj[0], adj[2], adj[3]))
        changes += any(a >= 0.05 for j, a in enumerate(adj) if j != 1)
    out["holm"] = {"max_holm_p_over_seeds_for_P1_P3_P4": worst,
                   "share_of_seeds_changing_any_state": changes / len(SEEDS)}
    (HERE / "mc_tolerance.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=2, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
