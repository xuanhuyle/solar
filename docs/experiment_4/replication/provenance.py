"""Experiment 4: provenance and internal-consistency checks of the scored run's original artifact.

Authenticates the copy of artifact 11145568607 on branch ``evidence/exp4-run-36823477529`` and checks the data it
holds against itself and against the run's committed outputs. Nothing here recomputes a statistic of the
experiment; that is ``blind_replicate.py`` (independent) and ``reexecute_frozen.py`` (the frozen code).

Usage::

    git fetch origin refs/heads/evidence/exp4-run-36823477529:refs/remotes/origin/evidence/exp4-run-36823477529
    python docs/experiment_4/replication/provenance.py --api-digest sha256:<digest read from the GitHub API now>

Writes ``provenance.json`` next to this file and exits non-zero if any check fails.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BRANCH = "origin/evidence/exp4-run-36823477529"
ZIP = "prices-run-36823477529.zip"
RECORDED_DIGEST = "sha256:98d8ca1f7c6f8f6bdfeba807b925bfee25ed1cd9da7a5e46b24acc88be436165"
SIZE = 5588744
RUN_ID, ARTIFACT_ID = 36823477529, 11145568607
HEAD_SHA = "2b407f42c03d2734ef4170cfb3e66962dbba9552"
PRINTED = ("summary.md", "results.json", "run_meta.json", "program_role.md")
MEMBERS = {"forecasts.csv.gz", "per_day_P1.csv", "per_day_P3.csv", "per_day_P4.csv", *PRINTED}
PARIS = ZoneInfo("Europe/Paris")
LEVELS = (0.1, 0.25, 0.5, 0.75, 0.9)
QCOLS = ("q10", "q25", "q50", "q75", "q90")
STRICT = {"t0_cal_strict", "best_simple_2023_strict"}
PAIRS = {"P1": ("t0_cal", "best_simple_2023", "abs"), "P3": ("t0_cal", "best_simple_eq", "pinball"),
         "P4": ("t0_cal_wx", "t0_cal", "abs")}


def git_bytes(path: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{BRANCH}:{path}"], check=True,
                          capture_output=True).stdout


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def paris_utc(day, hour: int) -> pd.Timestamp:
    """The UTC instant of ``hour``:00 Europe/Paris on ``day``."""
    return pd.Timestamp(datetime.combine(day, time(hour), tzinfo=PARIS)).tz_convert("UTC")


def hours_in(day) -> int:
    # Same-zone aware datetimes subtract as wall-clock times, so compare UTC instants.
    return int((paris_utc(day + timedelta(days=1), 0) - paris_utc(day, 0)).total_seconds() // 3600)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--api-digest", required=True, help="the artifact digest read from the GitHub API at check time")
    args = ap.parse_args()
    checks: dict[str, dict] = {}

    def check(name: str, ok: bool, **detail) -> None:
        checks[name] = {"ok": bool(ok), **detail}

    raw = git_bytes(ZIP)
    branch_head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", BRANCH], check=True, capture_output=True,
                                 text=True).stdout.strip()
    check("zip sha256 equals the digest read from the API now", "sha256:" + sha256(raw) == args.api_digest,
          zip_sha256=sha256(raw), api_digest=args.api_digest)
    check("zip sha256 equals the digest recorded at upload", "sha256:" + sha256(raw) == RECORDED_DIGEST,
          recorded=RECORDED_DIGEST)
    check("zip size", len(raw) == SIZE, size=len(raw))
    api = json.loads(git_bytes("artifact_api.json"))
    check("copied API record names this run and commit",
          api["id"] == ARTIFACT_ID and api["workflow_run"]["id"] == RUN_ID
          and api["workflow_run"]["head_sha"] == HEAD_SHA and api["digest"] == RECORDED_DIGEST)
    manifest = json.loads(git_bytes("manifest.json"))

    z = zipfile.ZipFile(io.BytesIO(raw))
    check("zip integrity (testzip)", z.testzip() is None)
    names = {i.filename for i in z.infolist()}
    check("zip holds exactly the 8 expected members", names == MEMBERS, members=sorted(names))
    data = {n: z.read(n) for n in names}
    mine = {n: sha256(b) for n, b in data.items()}
    theirs = {m["name"]: m["sha256"] for m in manifest["members"]}
    check("member sha256 equal the copying workflow's manifest", mine == theirs, members=mine)
    for n in PRINTED:
        committed = (ROOT / "docs" / "experiment_4" / "scored_run" / n).read_bytes()
        check(f"{n} is byte-identical to docs/experiment_4/scored_run/{n}", data[n] == committed)

    meta = json.loads(data["run_meta.json"])
    check("run_meta commit and run id", meta["commit"] == HEAD_SHA and int(meta["run_id"]) == RUN_ID)
    check("run_meta spec hash equals its pinned hash", meta["spec_sha256"] == meta["pinned_spec_sha256"],
          spec_sha256=meta["spec_sha256"])

    f = pd.read_csv(io.BytesIO(data["forecasts.csv.gz"]), compression="gzip", float_precision="round_trip",
                    dtype={"cov_issued_latest": "string"})
    f["delivery_date"] = pd.to_datetime(f["delivery_date"]).dt.date
    for c in ("target_time", "source_latest"):
        f[c] = pd.to_datetime(f[c], utc=True)
    f["cov_issued_latest"] = pd.to_datetime(f["cov_issued_latest"], utc=True)
    arms = sorted(f["method"].unique())
    check("arms in forecasts equal run_meta.scored_arms", arms == sorted(meta["scored_arms"]), arms=arms)

    per_day_rows = f.groupby(["method", "delivery_date"]).size()
    expected = np.array([hours_in(d) for _, d in per_day_rows.index])
    check("every arm has every hour of each of its days (23/24/25)", bool((per_day_rows.to_numpy() == expected).all()),
          rows=int(len(f)))
    dup = f.duplicated(["method", "target_time"]).sum()
    check("no duplicated (arm, target hour)", dup == 0)
    check("no non-finite y or y_hat", bool(np.isfinite(f[["y", "y_hat"]].to_numpy()).all()))
    test_days = sorted(f.loc[f["method"] == "t0_cal", "delivery_date"].unique())
    check("test days: 731 Paris days 2024-01-01..2025-12-31",
          len(test_days) == 731 and str(test_days[0]) == "2024-01-01" and str(test_days[-1]) == "2025-12-31")
    y_by_hour = f.groupby("target_time")["y"].nunique()
    check("every arm sees the same observed price for a given hour", bool((y_by_hour == 1).all()))

    # Point in time, from the run's own per-row provenance columns.
    days = f["delivery_date"].unique()
    cutoff = {d: paris_utc(d - timedelta(days=1), 23) for d in days}
    noon = {d: paris_utc(d - timedelta(days=1), 12) for d in days}
    lim = np.where(f["method"].isin(STRICT), f["delivery_date"].map(noon), f["delivery_date"].map(cutoff))
    lim = pd.to_datetime(pd.Series(lim), utc=True)
    check("every price read is stamped at or before its window's last allowed stamp "
          "(23:00 D-1 Paris; 12:00 D-1 for strict arms)", bool((f["source_latest"] <= lim).all()))
    wx = f[f["method"] == "t0_cal_wx"]
    cov_ok = (wx["cov_issued_latest"].notna() & (wx["cov_issued_latest"] <= wx["delivery_date"].map(noon))).all()
    check("every weather input of t0_cal_wx was issued by 12:00 D-1 Paris", bool(cov_ok))
    check("no other arm reports a covariate issue time",
          bool(f.loc[f["method"] != "t0_cal_wx", "cov_issued_latest"].isna().all()))

    kept = sorted(pd.to_datetime(meta["forecast"]["p4_days"]["kept_days"]).date)
    wx_days = sorted(wx["delivery_date"].unique())
    check("t0_cal_wx days equal run_meta.forecast.p4_days.kept_days (572)", wx_days == kept and len(kept) == 572)

    f["abs"] = (f["y"] - f["y_hat"]).abs()
    u = f["y"].to_numpy()[:, None] - f[list(QCOLS)].to_numpy()
    tau = np.array(LEVELS)[None, :]
    f["pinball"] = np.maximum(tau * u, (tau - 1.0) * u).mean(axis=1)
    worst = 0.0
    for p, (arm, ref, loss) in PAIRS.items():
        t = pd.read_csv(io.BytesIO(data[f"per_day_{p}.csv"]), float_precision="round_trip")
        t["delivery_date"] = pd.to_datetime(t["delivery_date"]).dt.date
        mine_t = (f[f["method"].isin([arm, ref])].groupby(["delivery_date", "method"])
                  .agg(sum_abs_err=(loss, "sum"), n=(loss, "size")).reset_index())
        if p == "P4":
            mine_t = mine_t[mine_t["delivery_date"].isin(set(kept))]
        merged = t.merge(mine_t, on=["delivery_date", "method"], how="outer", suffixes=("_run", "_mine"),
                         indicator=True)
        same_keys = bool((merged["_merge"] == "both").all())
        rel = (merged["sum_abs_err_run"] - merged["sum_abs_err_mine"]).abs() / merged["sum_abs_err_run"].abs()
        worst = max(worst, float(rel.max()))
        check(f"per_day_{p}.csv equals the per-day sums derived from forecasts.csv.gz",
              same_keys and bool((merged["n_run"] == merged["n_mine"]).all()) and float(rel.max()) <= 1e-12,
              rows=int(len(t)), max_relative_difference=float(rel.max()),
              bit_exact_rows=int((merged["sum_abs_err_run"] == merged["sum_abs_err_mine"]).sum()))

    out = {"evidence_branch": "evidence/exp4-run-36823477529", "evidence_commit": branch_head,
           "copied_by_run": manifest["copied_by"]["run_id"], "zip_sha256": sha256(raw),
           "api_digest_at_check": args.api_digest, "member_sha256": mine,
           "all_ok": all(c["ok"] for c in checks.values()), "checks": checks}
    (HERE / "provenance.json").write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    for name, c in checks.items():
        print(("ok   " if c["ok"] else "FAIL ") + name)
    print("all ok" if out["all_ok"] else "SOME CHECKS FAILED")
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
