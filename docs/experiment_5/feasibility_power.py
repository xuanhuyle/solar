"""Power analogue for the feasibility review of the researcher's proposal (I1). It runs no forecast.

The proposed primary comparison (the B1 arm against C1 plus a linear temperature correction) has never been run, so
its precision cannot be measured. This script measures the closest recorded analogue: paired comparisons between
temperature-aware t0 arms that the engine already scored on the same days. It reads the per-day MAE recorded in
engine-ledger probe_result seq 51 (period ALL, 2024-05..2025-12) and computes pooled MAE skill
(1 - sum MAE_arm / sum MAE_ref) with a paired moving-block bootstrap, as the proposal specifies (14-day blocks,
2000 resamples, seed 0). The 7-day row reproduces the ledger's own recorded interval as a check.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/feasibility_power.py      # writes feasibility_power.json beside this file
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEQ = 51
PAIRS = [  # (label, arm, reference)
    ("a: B1 arm vs C1 (the competence-check analogue)", "cal_temp_raw", "accepted"),
    ("b: raw vs hdd15 temperature", "cal_temp_raw", "cal_hdd15"),
    ("c: raw vs hdd15+cdd22 temperature", "cal_temp_raw", "cal_hdd15_cdd22"),
    ("d: hdd15 vs hdd15+cdd22 (near-null pair)", "cal_hdd15", "cal_hdd15_cdd22"),
]
SLICES = {"all": lambda d: True, "2024": lambda d: d.startswith("2024"), "2025": lambda d: d.startswith("2025"),
          "winter (Nov-Mar)": lambda d: int(d[5:7]) in (11, 12, 1, 2, 3),
          "summer (May-Sep)": lambda d: int(d[5:7]) in (5, 6, 7, 8, 9)}
Z_HOLM_FIRST = 1.959964  # one-sided 0.025, the first Holm step over two comparisons
Z_POWER80 = 0.841621


def boot(a: np.ndarray, b: np.ndarray, block: int, resamples: int = 2000, seed: int = 0) -> dict:
    n = len(a)
    skill = 1 - a.sum() / b.sum()
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    draws = np.empty(resamples)
    for i in range(resamples):
        starts = rng.integers(0, n - block + 1, nb)
        idx = (starts[:, None] + np.arange(block)).ravel()[:n]
        draws[i] = 1 - a[idx].sum() / b[idx].sum()
    lo, hi = np.percentile(draws, [2.5, 97.5])
    sd = float(draws.std(ddof=1))
    return {"days": n, "skill": round(float(skill), 5), "ci95": [round(float(lo), 5), round(float(hi), 5)],
            "half_width_pts": round(float(hi - lo) * 50, 2), "bootstrap_sd_pts": round(sd * 100, 2),
            "mde80_pts_one_sided_0.025": round((Z_HOLM_FIRST + Z_POWER80) * sd * 100, 2),
            "p_one_sided": round(float((1 + (draws <= 0).sum()) / (resamples + 1)), 4)}


def main() -> int:
    raw = subprocess.run(["git", "show", "origin/engine-ledger:ledger.jsonl"], check=True, capture_output=True,
                         text=True).stdout
    entry = [json.loads(line) for line in raw.splitlines() if line.strip()][SEQ]
    assert entry["seq"] == SEQ and entry["kind"] == "probe_result"
    per_day = entry["payload"]["per_day"]
    dates = per_day["dates"]
    mae = {k: np.array([np.nan if v is None else v for v in vals], dtype=float)
           for k, vals in per_day["mae_mw"].items()}
    recorded = {c["arm"]: c for c in entry["payload"]["comparisons"]}
    out = {"source": f"engine-ledger seq {SEQ} (probe_result, period ALL), per_day.mae_mw",
           "method": "pooled MAE skill, paired moving-block bootstrap, 2000 resamples, seed 0",
           "caveat": ("an analogue: pairs of t0 arms that differ only in how temperature enters, not the proposed "
                      "B1-vs-corrected-C1 comparison; all days were used to select B1, so every figure is "
                      "exploratory"),
           "check_7day_block_vs_ledger": {}, "pairs": {}}
    a, b = mae["cal_temp_raw"], mae["accepted"]
    ok = np.isfinite(a) & np.isfinite(b)
    out["check_7day_block_vs_ledger"] = {"recomputed": boot(a[ok], b[ok], 7),
                                         "ledger": {"skill": recorded["cal_temp_raw"]["skill"],
                                                    "ci95": recorded["cal_temp_raw"]["ci95"]}}
    for label, arm, ref in PAIRS:
        rows = {}
        for name, keep in SLICES.items():
            sel = np.array([keep(d) for d in dates]) & np.isfinite(mae[arm]) & np.isfinite(mae[ref])
            rows[name] = boot(mae[arm][sel], mae[ref][sel], 14)
        out["pairs"][label] = rows
    (HERE / "feasibility_power.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for label, rows in out["pairs"].items():
        print(label)
        for name, r in rows.items():
            print(f"  {name:17s} n={r['days']:3d} skill={r['skill'] * 100:+6.2f}% "
                  f"CI[{r['ci95'][0] * 100:+6.2f},{r['ci95'][1] * 100:+6.2f}] hw={r['half_width_pts']:5.2f} "
                  f"MDE80={r['mde80_pts_one_sided_0.025']:5.2f}")
    print("7-day check:", out["check_7day_block_vs_ledger"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
