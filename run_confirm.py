#!/usr/bin/env python3
"""One-shot confirmation of claim C1 (``solarbench.confirm.CLAIM``).

    python run_confirm.py --year 2024   # dry run: the identical path on unsealed data
    python run_confirm.py --year 2025   # the one look at the sealed 2025 data

The dry run must reproduce Experiment 3's P4 numbers before 2025 is touched.
For 2025 the pinned model is loaded first, then ``confirm.open_sealed`` checks
the claim's fingerprint and the ledger; only then is the sealed data fetched.
Results go to ``results/confirm/``; the ledger entry is committed afterwards.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

import run_covariates as rc
import run_probes as rp
from solarbench import confirm, metrics, odre
from solarbench import probes as pr
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import STEP, STEPS_PER_DAY, _read_any
from solarbench.forecasters import T0_REPO_ID, statistical_baselines

log = logging.getLogger("run_confirm")
ROOT = Path(__file__).resolve().parent
COLUMNS = ["date_heure", "perimetre", "nature", "consommation"]


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--year", type=int, choices=[2024, 2025], required=True)
    p.add_argument("--probe-cache", type=Path, default=ROOT / "probecache")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "confirm")
    p.add_argument("--ledger", type=Path, default=confirm.LEDGER)
    p.add_argument("--repo-id", default=T0_REPO_ID)
    p.add_argument("--revision", default=None)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--context-days", type=int, default=90)
    p.add_argument("--gate-hour", type=int, default=12)
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args(argv)


def _year_share(series: pd.Series, year: int) -> float:
    """Valid share over the *whole* year's half-hours - a source that stops early fails."""
    expected = pd.date_range(f"{year}-01-01", f"{year + 1}-01-01", freq=STEP, tz="UTC", inclusive="left")
    return float(series.reindex(expected).notna().mean())


def load_source(args, access) -> tuple[str | None, pd.Series | None, pd.Series | None, dict]:
    """Apply the frozen source rule; return the source, consumption, RTE reference and coverages."""
    start, end = f"{args.year - 1}-09-01", f"{args.year + 1}-01-01"
    coverage: dict[str, float] = {}
    for dataset in confirm.SOURCES:
        try:
            path = odre.fetch_columns(dataset, COLUMNS, start, end, args.probe_cache, sealed_access=access)
            load = odre.load_column(path, "consommation")
        except Exception as exc:
            log.warning("%s unavailable: %s", dataset, exc)
            coverage[dataset] = 0.0
            continue
        coverage[dataset] = round(_year_share(load, args.year), 5)
        if confirm.choose_source(coverage) == dataset:
            try:
                ref_path = odre.fetch_columns(dataset, ["date_heure", "perimetre", "prevision_j1"], start, end,
                                              args.probe_cache, sealed_access=access)
                ref = odre.load_column(ref_path, "prevision_j1")
            except Exception as exc:  # a reference only
                log.warning("prevision_j1 unavailable from %s: %s", dataset, exc)
                ref = None
            return dataset, load, ref, coverage
    return None, None, None, coverage


def run(args) -> dict:
    started = time.time()
    claim = confirm.CLAIM
    if confirm.claim_sha256() != confirm.FROZEN_CLAIM_SHA256:
        raise SystemExit("the claim differs from the frozen one - refusing to run")
    if args.revision != claim["t0_arm"]["revision"] or args.repo_id != claim["t0_arm"]["repo_id"]:
        raise SystemExit("the model must be the claim's pinned repo and revision")
    model = rp._t0(args, "t0").load()  # before any sealed data: a model failure wastes nothing
    access = confirm.open_sealed(model_loaded=model is not None, ledger=args.ledger) if args.year >= 2025 else None

    out: dict = {"claim_id": claim["id"], "claim_sha256": confirm.claim_sha256(), "year": args.year,
                 "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    source, load, ref, coverage = load_source(args, access)
    out.update({"source": source, "coverage": coverage})
    if source is None:
        out.update({"verdict": "INCONCLUSIVE", "reason": "no source passes the 95% rule"})
        return out

    report = BacktestReport()
    windows = build_windows(load, test_start=date(args.year, 1, 1), test_end=date(args.year, 12, 31),
                            gate_hour=args.gate_hour, context_steps=args.context_days * STEPS_PER_DAY, report=report)
    blend = [m for m in statistical_baselines() if m.name == "blend_50"][0]
    methods = [rp._t0(args, "t0", model=model), rp._t0(args, "t0_cal", covariates=(pr.HolidayCovariate(),), model=model),
               blend]
    if ref is not None:
        methods.append(pr.ReferenceForecast(ref, name="rte_j1", label="RTE's own D-1 forecast (reference)"))
    df = run_backtest(load, methods, windows, report=report)
    per_day = metrics.per_day_errors(df)
    n_days = int(per_day["delivery_date"].nunique())

    s = metrics.bootstrap_skill(per_day, model="t0_cal", reference="blend_50", seed=args.seed, return_draws=True)
    lb = confirm.lower_bound(s.pop("draws"))
    primary = rp.compare(per_day, "t0_cal", "blend_50", args.seed)
    reported = [rp.compare(per_day, "t0", "blend_50", args.seed)]
    if ref is not None:
        reported.append(rp.compare(per_day, "t0_cal", "rte_j1", args.seed))
    mae = df.assign(ae=(df["y"] - df["y_hat"]).abs()).groupby("method")["ae"].mean()
    out.update({
        "scored_days": n_days, "first_day": str(min(w.delivery_date for w in windows)),
        "last_day": str(max(w.delivery_date for w in windows)),
        "mae_mw": {k: round(float(v), 1) for k, v in mae.items()},
        "skill": primary["skill"], "skill_ci95": [primary["skill_lo95"], primary["skill_hi95"]],
        "lower_bound_one_sided_95": lb, "threshold": claim["threshold"],
        "days_won": primary["days_won"], "days_lost": primary["days_lost"],
        "verdict": confirm.verdict(lb, n_days),
        "reported_only": reported,
        "report": report.as_full_dict(),
        "nature_counts": _nature_counts(args, source, access),
        "elapsed_s": round(time.time() - started, 1),
    })
    return out


def _nature_counts(args, source, access) -> dict:
    """The data vintage of the scored year's consumption rows (definitive / consolidated / real time)."""
    try:
        path = odre.fetch_columns(source, COLUMNS, f"{args.year - 1}-09-01", f"{args.year + 1}-01-01",
                                  args.probe_cache, sealed_access=access)
        df = _read_any(path)
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.loc[pd.to_numeric(df["consommation"], errors="coerce").notna()]
        year = df["date_heure"].astype(str).str.slice(0, 4) == str(args.year)
        return {str(k): int(v) for k, v in df.loc[year, "nature"].value_counts().items()}
    except Exception as exc:
        return {"error": str(exc)[:200]}


def write(out: dict, results: Path) -> None:
    results.mkdir(parents=True, exist_ok=True)
    rc._write_json(results / "confirm.json", out)
    lines = [f"# Confirmation of claim {out['claim_id']} on {out['year']}", "",
             f"- Claim sha256 `{out['claim_sha256']}` · source `{out.get('source')}` · coverage {out.get('coverage')}",
             f"- **Verdict: {out['verdict']}**"]
    if "skill" in out:
        lines += [
            f"- Scored days: {out['scored_days']} ({out['first_day']} .. {out['last_day']})",
            f"- MAE (MW): {out['mae_mw']}",
            f"- Skill of t0_cal vs blend_50: {out['skill']:+.1%} "
            f"[95% CI {out['skill_ci95'][0]:+.1%}, {out['skill_ci95'][1]:+.1%}]; "
            f"one-sided 95% lower bound {out['lower_bound_one_sided_95']:+.1%} vs threshold {out['threshold']:+.0%}",
            f"- Days won / lost: {out['days_won']} / {out['days_lost']}",
            "", "Reported only (not part of the verdict):", "",
        ]
        lines += [f"- {r['model']} vs {r['reference']}: {r['skill']:+.1%} [{r['skill_lo95']:+.1%}, {r['skill_hi95']:+.1%}]"
                  for r in out["reported_only"]]
    (results / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    out = run(args)
    write(out, args.results_dir)
    print((args.results_dir / "summary.md").read_text(encoding="utf-8"))
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
