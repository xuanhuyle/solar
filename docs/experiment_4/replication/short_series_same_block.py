"""Experiment 4 replication: the two short-slice discrepancies come from the block length alone.

For P4's two short report-only slices (2024Q2, 25 days; the weeks after each DST switch, 21 days), the frozen
``metrics.bootstrap_skill`` shortens its 14-day blocks to ``n_days // 2`` (12 and 10 days), while the blind
re-implementation used literal 14-day blocks. This script runs the blind bootstrap (``blind/blind_replicate.py``'s
own ``mbb_draws`` and ``ci_p``, loaded from its source without running the script) with the frozen block lengths,
on the per-day tables of the authenticated artifact. If it then reproduces the published interval and p, the
discrepancy is entirely the block-length reading.

Usage::

    python docs/experiment_4/replication/short_series_same_block.py --artifact <unzipped artifact dir>
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SLICES = {"/slices/P4/each quarter (2025 Q4 is quarter-hour derived)/2024Q2": ("2024-04-01", "2024-06-30"),
          "/slices/P4/the weeks after each DST switch": None}
DST_SWITCHES = ("2024-03-31", "2024-10-27", "2025-03-30", "2025-10-26")


def blind_functions() -> dict:
    """``mbb_draws`` and ``ci_p`` exactly as the blind script defines them, without executing the script."""
    tree = ast.parse((HERE / "blind" / "blind_replicate.py").read_text(encoding="utf-8"))
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("mbb_draws", "ci_p")]
    ns: dict = {"np": np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "blind_replicate.py", "exec"), ns)
    return ns


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--artifact", type=Path, required=True)
    args = ap.parse_args()
    fns = blind_functions()
    pub = json.loads((args.artifact / "results.json").read_text())
    table = pd.read_csv(args.artifact / "per_day_P4.csv", float_precision="round_trip")
    wide = table.pivot(index="delivery_date", columns="method", values="sum_abs_err").sort_index()
    dst = {str((pd.Timestamp(d) + pd.Timedelta(days=k)).date()) for d in DST_SWITCHES for k in range(7)}
    out = {}
    for path, span in SLICES.items():
        days = [d for d in wide.index if (span[0] <= d <= span[1] if span else d in dst)]
        sub = wide.loc[days]
        n = len(days)
        entry = pub
        for k in path.strip("/").split("/"):
            entry = entry[k]
        res = {"n_days": n}
        for block in (n // 2, 14):
            draws = fns["mbb_draws"](sub["t0_cal_wx"].to_numpy(), sub["t0_cal"].to_numpy(), block, 2000, 0)
            ci, p, k = fns["ci_p"](draws, 0.0)
            res[f"blind_bootstrap_block_{block}"] = {
                "ci95": ci, "p": p,
                "equals_published": {"ci95_rel_diff": [abs(a - b) / abs(b) for a, b in zip(ci, entry["ci95"])],
                                     "p_identical": p == entry["p_one_sided"]}}
        res["published"] = {"ci95": entry["ci95"], "p": entry["p_one_sided"]}
        out[path] = res
    (HERE / "short_series_same_block.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
