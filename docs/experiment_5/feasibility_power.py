"""Power analogue for the feasibility review of the researcher's proposal (I1). It runs no forecast.

The proposed primary comparison (the B1 arm against C1 plus a linear temperature correction) has never been run, so
its precision cannot be measured. This script measures the closest recorded analogue. It takes four pairs of t0
arms that the engine already scored on the same days:
- the B1 arm against C1 (t0 + holiday, with no temperature input), the analogue of the competence check;
- three pairs of temperature-aware arms that differ only in how temperature enters.

The input is the per-day MAE recorded in engine-ledger probe_result seq 51 (period ALL, 2024-05..2025-12).

How the bootstrap is reproduced:
- Each day's MAE is turned back into a sum of absolute errors over that Paris day's half-hours (46 or 48).
- The engine's own bootstrap, ``solarbench.metrics.bootstrap_skill``, is then run with the proposal's settings:
  14-day blocks, 2000 resamples, seed 0.
- A 7-day row reproduces the ledger's recorded figures, as a check.

The derived probabilities (power, equivalence, both years positive) are normal approximations on the bootstrap SDs.
They are labelled as such in the output.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/feasibility_power.py      # writes feasibility_power.json beside this file
"""
from __future__ import annotations

import json
import subprocess
import sys
from math import erf, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from solarbench import metrics  # noqa: E402

SEQ = 51
PAIRS = [  # (label, arm, reference)
    ("a: B1 arm vs C1 (no temperature input; the competence-check analogue)", "cal_temp_raw", "accepted"),
    ("b: raw vs hdd15 temperature", "cal_temp_raw", "cal_hdd15"),
    ("c: raw vs hdd15+cdd22 temperature", "cal_temp_raw", "cal_hdd15_cdd22"),
    ("d: hdd15 vs hdd15+cdd22 (near-null pair)", "cal_hdd15", "cal_hdd15_cdd22"),
]
WINTER, SUMMER = (11, 12, 1, 2, 3), (5, 6, 7, 8, 9)  # engine/catalogue.py SCOPES
SLICES = {"all": lambda d: True, "2024": lambda d: d.year == 2024, "2025": lambda d: d.year == 2025,
          "winter (Nov-Mar)": lambda d: d.month in WINTER, "summer (May-Sep)": lambda d: d.month in SUMMER}
Z = {"0.025": 1.959964, "0.05": 1.644854}
Z_POWER80 = 0.841621
EQUIV_MARGIN = 5.0  # points: the proposal's "CI within +/-5%"


def phi(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def half_hours(day: pd.Timestamp) -> int:
    start = pd.Timestamp(day.date()).tz_localize("Europe/Paris")
    end = (pd.Timestamp(day.date()) + pd.Timedelta(days=1)).tz_localize("Europe/Paris")
    return int((end - start) / pd.Timedelta(minutes=30))


def boot(frame: pd.DataFrame, arm: str, ref: str, block: int) -> dict:
    s = metrics.bootstrap_skill(frame, model=arm, reference=ref, block_days=block, seed=0, return_draws=True)
    draws = s["draws"]
    sd = float(draws.std(ddof=1)) * 100
    return {"days": s["n_days"], "skill": round(s["skill"], 6), "ci95": [round(s["skill_lo95"], 6),
                                                                         round(s["skill_hi95"], 6)],
            "half_width_pts": round((s["skill_hi95"] - s["skill_lo95"]) * 50, 2), "bootstrap_sd_pts": round(sd, 2),
            "mde80_pts_one_sided_0.025": round((Z["0.025"] + Z_POWER80) * sd, 2),
            "p_one_sided": round(float((1 + (draws <= 0).sum()) / (len(draws) + 1)), 4)}


def derived(rows: dict) -> dict:
    """Normal approximations on the pooled and per-year bootstrap SDs (points of skill)."""
    sd, sd24, sd25 = (rows[k]["bootstrap_sd_pts"] for k in ("all", "2024", "2025"))
    hw = Z["0.025"] * sd
    room = EQUIV_MARGIN - hw
    equiv = {f"delta_{d}": (round(phi((room - d) / sd) - phi((-room - d) / sd), 3) if room > 0 else 0.0)
             for d in (0, 2)}
    return {"note": "normal approximations, not measurements",
            "point_estimate_band_for_equivalence_pts": round(max(room, 0.0), 2),
            "p_equivalence_declared": equiv,
            "p_overall_significant": {f"alpha_{a}": {f"delta_{d}": round(phi(d / sd - z), 3) for d in (1, 2, 3, 5)}
                                      for a, z in Z.items()},
            "p_both_year_estimates_positive": {f"delta_{d}": round(phi(d / sd24) * phi(d / sd25), 3)
                                               for d in (2, 3, 5)}}


def main() -> int:
    raw = subprocess.run(["git", "show", "origin/engine-ledger:ledger.jsonl"], check=True, capture_output=True,
                         text=True).stdout
    entry = [json.loads(line) for line in raw.splitlines() if line.strip()][SEQ]
    assert entry["seq"] == SEQ and entry["kind"] == "probe_result"
    per_day = entry["payload"]["per_day"]
    dates = pd.to_datetime(per_day["dates"])
    n = np.array([half_hours(d) for d in dates])
    rows = []
    for method, vals in per_day["mae_mw"].items():
        mae = np.array([np.nan if v is None else v for v in vals], dtype=float)
        rows.append(pd.DataFrame({"delivery_date": dates, "method": method, "sum_abs_err": mae * n, "n": n}))
    long = pd.concat(rows, ignore_index=True).dropna()
    recorded = {c["arm"]: c for c in entry["payload"]["comparisons"]}

    def pair_frame(arm: str, ref: str, keep) -> pd.DataFrame:
        sub = long[long["method"].isin([arm, ref])]
        both = sub.groupby("delivery_date")["method"].nunique() == 2
        days = [d for d in both[both].index if keep(d)]
        return sub[sub["delivery_date"].isin(days)]

    out = {"source": f"engine-ledger seq {SEQ} (probe_result, period ALL), per_day.mae_mw x Paris half-hours",
           "method": "solarbench.metrics.bootstrap_skill, 14-day blocks, 2000 resamples, seed 0",
           "caveat": ("an analogue, not the proposed B1-vs-corrected-C1 comparison; all days were used to select B1, "
                      "so every figure is exploratory"),
           "check_7day_block_vs_ledger": {
               "recomputed": boot(pair_frame("cal_temp_raw", "accepted", SLICES["all"]), "cal_temp_raw",
                                  "accepted", 7),
               "ledger": {k: recorded["cal_temp_raw"][k] for k in ("skill", "ci95", "p_one_sided")}},
           "pairs": {}, "day_counts": {}}
    for label, arm, ref in PAIRS:
        rows = {name: boot(pair_frame(arm, ref, keep), arm, ref, 14) for name, keep in SLICES.items()}
        out["pairs"][label] = {"slices": rows, "derived": derived(rows)}
    b1 = sorted(pair_frame("cal_temp_raw", "accepted", SLICES["all"])["delivery_date"].unique())
    b1 = pd.DatetimeIndex(b1)
    late = b1[b1 >= pd.Timestamp("2024-07-01")]
    out["day_counts"] = {
        "b1_arm_days": len(b1), "first": str(b1[0].date()), "last": str(b1[-1].date()),
        "by_year": {str(y): int((b1.year == y).sum()) for y in (2024, 2025)},
        "winter": int(b1.month.isin(WINTER).sum()), "winter_2024": int((b1.month.isin(WINTER) & (b1.year == 2024)).sum()),
        "summer": int(b1.month.isin(SUMMER).sum()), "april_or_october": int(b1.month.isin((4, 10)).sum()),
        "from_2024_07_01": len(late), "from_2024_07_01_in_2024": int((late.year == 2024).sum())}
    (HERE / "feasibility_power.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for label, body in out["pairs"].items():
        print(label)
        for name, r in body["slices"].items():
            print(f"  {name:17s} n={r['days']:3d} skill={r['skill'] * 100:+6.2f}% "
                  f"CI[{r['ci95'][0] * 100:+6.2f},{r['ci95'][1] * 100:+6.2f}] hw={r['half_width_pts']:5.2f} "
                  f"sd={r['bootstrap_sd_pts']:4.2f} MDE80={r['mde80_pts_one_sided_0.025']:5.2f}")
        print("  derived:", json.dumps(body["derived"]))
    print("7-day check:", json.dumps(out["check_7day_block_vs_ledger"]))
    print("days:", json.dumps(out["day_counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
