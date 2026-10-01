"""Experiment 4, replication Track 2: the frozen statistics code re-executed on the run's original forecasts.

NOT an independent check. This runs ``run_prices._stats`` exactly as frozen at ``2b407f4``, imported from a git
worktree of that commit, on the hourly forecasts held in the authenticated artifact. It shows whether the published
``results.json`` follows, byte for byte, from the recorded forecasts and the frozen code. Independence comes from
Track 1 (``blind_replicate.py``).

Usage (numpy 2.4.6 and pandas 2.3.3, as in the run)::

    git worktree add --detach /tmp/exp4-frozen 2b407f42c03d2734ef4170cfb3e66962dbba9552
    python docs/experiment_4/replication/reexecute_frozen.py --frozen /tmp/exp4-frozen --artifact <unzipped dir>

Writes ``reexecute_frozen.json`` (the comparison) next to this file and exits non-zero on any difference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
FROZEN = "2b407f42c03d2734ef4170cfb3e66962dbba9552"


def load_forecasts(path: Path) -> pd.DataFrame:
    """The forecasts frame with the dtypes ``price_run.forecast_all`` gave it in memory."""
    df = pd.read_csv(path, float_precision="round_trip", dtype={"cov_issued_latest": "string"})
    df["delivery_date"] = pd.to_datetime(df["delivery_date"]).dt.date
    df["target_time"] = pd.to_datetime(df["target_time"], utc=True)
    df["local_time"] = df["target_time"].dt.tz_convert("Europe/Paris")
    df["source_latest"] = pd.to_datetime(df["source_latest"], utc=True)
    df["cov_issued_latest"] = pd.to_datetime(df["cov_issued_latest"], utc=True)
    return df


def diff(a, b, path="") -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        out = [f"{path}/{k}: only in published" for k in a.keys() - b.keys()]
        out += [f"{path}/{k}: only in re-execution" for k in b.keys() - a.keys()]
        for k in a.keys() & b.keys():
            out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f"{path}/{i}")]
    return [] if a == b else [f"{path}: published {a!r} vs re-executed {b!r}"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frozen", type=Path, required=True, help="a git worktree checked out at 2b407f4")
    ap.add_argument("--artifact", type=Path, required=True, help="the unzipped original artifact")
    args = ap.parse_args()
    head = subprocess.run(["git", "-C", str(args.frozen), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    if head != FROZEN:
        raise SystemExit(f"the worktree is at {head}, not the freeze commit {FROZEN}")
    sys.path.insert(0, str(args.frozen))
    import run_prices  # noqa: E402  (the frozen module, from the worktree)
    if Path(run_prices.__file__).resolve().parent != args.frozen.resolve():
        raise SystemExit(f"imported {run_prices.__file__}, not the frozen worktree")

    meta = json.loads((args.artifact / "run_meta.json").read_text())
    published_bytes = (args.artifact / "results.json").read_bytes()
    df = load_forecasts(args.artifact / "forecasts.csv.gz")
    ctx = {"k1_passed": bool(meta["k1"]["passed"]), "k3_passed": bool(meta["k3"]["pass"])}
    out, lines, tables = run_prices._stats(df, meta["forecast"], ctx, set(meta["scored_arms"]))
    tmp = HERE / "_reexecuted_results.json"
    run_prices._dump(tmp, out)
    mine = tmp.read_bytes()
    tmp.unlink()
    summary_ok = "\n".join([*lines, "", run_prices.AMENDMENT_LINE, ""]).encode() == \
        (args.artifact / "summary.md").read_bytes()
    per_day_ok = {pid: t is None or t.to_csv(index=False).encode() == (args.artifact / f"per_day_{pid}.csv").read_bytes()
                  for pid, t in tables.items()}
    differences = diff(json.loads(published_bytes), json.loads(mine))
    report = {
        "track": "2: frozen code re-executed (NOT independent)",
        "frozen_commit": head,
        "numpy": np.__version__, "pandas": pd.__version__,
        "results_json_byte_identical": mine == published_bytes,
        "results_json_sha256": {"published": hashlib.sha256(published_bytes).hexdigest(),
                                "re_executed": hashlib.sha256(mine).hexdigest()},
        "summary_md_byte_identical": summary_ok,
        "per_day_csv_byte_identical": per_day_ok,
        "field_differences": differences,
    }
    (HERE / "reexecute_frozen.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "field_differences"}, indent=2))
    print(f"{len(differences)} field differences")
    for d in differences[:50]:
        print("  ", d)
    ok = report["results_json_byte_identical"] and summary_ok and all(per_day_ok.values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
