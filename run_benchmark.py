#!/usr/bin/env python3
"""Benchmark t0-alpha against naive persistence on RTE French national solar.

One command reproduces the whole experiment:

    python run_benchmark.py

It downloads RTE eCO2mix national solar generation (30-minute, MW) from ODRE,
caches it, runs a rolling day-ahead backtest over the test year, and writes
metrics and figures to ``results/``.  Re-runs read the caches and recompute
nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from solarbench import metrics, plots
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import STEPS_PER_DAY, load_or_fetch, manifest_path, series_fingerprint
from solarbench.forecasters import T0_REPO_ID, T0Forecaster, same_day_baseline, same_week_baseline

log = logging.getLogger("run_benchmark")

ROOT = Path(__file__).resolve().parent
PRIMARY = "t0"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-start", default="2022-01-01", help="first day to download (inclusive)")
    p.add_argument("--data-end", default="2025-01-01", help="last day to download (exclusive)")
    p.add_argument("--test-start", default="2024-01-01", help="first delivery day to score")
    p.add_argument("--test-end", default="2024-12-31", help="last delivery day to score")
    p.add_argument("--context-days", type=int, default=90, help="days of history given to t0 at each origin")
    p.add_argument("--gate-hour", type=int, default=12, help="local hour on D-1 at which forecasts are issued")
    p.add_argument("--csv", type=Path, default=None, help="parse this file instead of downloading")
    p.add_argument("--cache-dir", type=Path, default=ROOT / "data")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results")
    p.add_argument("--repo-id", default=T0_REPO_ID, help="Hugging Face model repo")
    p.add_argument("--revision", default=None, help="pin a model revision for exact reproducibility")
    p.add_argument("--batch-size", type=int, default=64, help="origins per t0 forward pass")
    p.add_argument("--no-t0", action="store_true", help="baselines only (no model download)")
    p.add_argument("--limit-days", type=int, default=None, help="score only the first N delivery days")
    p.add_argument("--force-download", action="store_true")
    p.add_argument("--force-forecast", action="store_true", help="ignore the cached forecasts")
    p.add_argument("--seed", type=int, default=0, help="bootstrap seed")
    return p.parse_args(argv)


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "unknown"


def _cache_key(args: argparse.Namespace, fingerprint: str, methods: list[str]) -> str:
    payload = {
        "data_fingerprint": fingerprint,
        "data_window": [args.data_start, args.data_end],
        "csv": str(args.csv) if args.csv else None,
        "test": [args.test_start, args.test_end],
        "gate_hour": args.gate_hour,
        "context_days": args.context_days,
        "methods": methods,
        "repo_id": args.repo_id,
        "revision": args.revision,
        "limit_days": args.limit_days,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def write_summary(
    path: Path,
    *,
    args: argparse.Namespace,
    labels: dict[str, str],
    overall: pd.DataFrame,
    daytime: pd.DataFrame,
    skills: list[dict],
    skills_daytime: list[dict],
    night: pd.DataFrame,
    peak: float,
    report: dict,
    elapsed: float,
    manifest: dict,
    primary: str,
) -> None:
    def table(frame: pd.DataFrame) -> list[str]:
        lines = ["| Method | MAE (MW) | nMAE (mean) | nMAE (peak) | points |", "|---|---:|---:|---:|---:|"]
        for _, r in frame.iterrows():
            lines.append(
                f"| {labels.get(r['method'], r['method'])} | {r['mae_mw']:,.0f} | "
                f"{r['nmae_mean']:.1%} | {r['nmae_peak']:.2%} | {int(r['n_points']):,} |"
            )
        return lines

    lead = labels.get(primary, primary)

    def skill_table(rows: list[dict]) -> list[str]:
        lines = [
            f"| Baseline | MAE reduction by {lead} | 95% CI | {lead} wins |",
            "|---|---:|---:|---:|",
        ]
        for s in rows:
            lines.append(
                f"| {labels.get(s['reference'], s['reference'])} | {s['skill']:+.1%} | "
                f"[{s['skill_lo95']:+.1%}, {s['skill_hi95']:+.1%}] | {s['win_rate']:.0%} of {s['n_days']} days |"
            )
        return lines

    lines = [
        "# Benchmark results",
        "",
        f"- Delivery days scored: **{report['n_windows']}** ({args.test_start} to {args.test_end})",
        f"- Forecast issued at **{args.gate_hour:02d}:00 Europe/Paris on D-1**, covering 00:00-24:00 local of day D",
        f"- Context: **{args.context_days} days** ({args.context_days * STEPS_PER_DAY} half-hours) of solar history, no weather covariates",
        f"- Peak proxy for nMAE(peak): **{peak:,.0f} MW** (p99 of actual generation over the scored period)",
        f"- Data as benchmarked: {manifest.get('rows', 0):,} half-hours, "
        f"{manifest.get('start', '?')} to {manifest.get('end', '?')} "
        f"({manifest.get('missing_steps', 0)} missing)",
        f"- Runtime: {elapsed / 60:.1f} min · generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## All hours",
        "",
        *table(overall),
        "",
        "## Daytime half-hours only",
        "",
        "Night is roughly half of every day and every method predicts ~0 there, which flatters",
        "all of them equally. These are the same metrics over daytime slots only.",
        "",
        *table(daytime),
        "",
        f"## Relative improvement of {lead} (all hours)",
        "",
        *skill_table(skills),
        "",
        f"## Relative improvement of {lead} (daytime only)",
        "",
        *skill_table(skills_daytime),
        "",
        "## Night sanity check",
        "",
        "Mean forecast on night half-hours — anything far from 0 MW means the model is",
        "hallucinating generation in the dark.",
        "",
        "| Method | Mean night forecast (MW) |",
        "|---|---:|",
        *[
            f"| {labels.get(r['method'], r['method'])} | {r['night_mean_forecast_mw']:,.1f} |"
            for _, r in night.iterrows()
        ],
        "",
        "## Windows dropped",
        "",
        "```json",
        json.dumps(report, indent=2),
        "```",
        "",
        "## Figures",
        "",
        "| Figure | What it shows |",
        "|---|---|",
        "| `figures/fig1_representative_days.png` | Four delivery days picked by a fixed rule |",
        "| `figures/fig2_error_by_time_of_day.png` | MAE by position in the delivery day |",
        "| `figures/fig3_by_month.png` | Seasonal breakdown |",
        "| `figures/fig4_skill.png` | Improvement over each baseline, with bootstrap CIs |",
        "| `figures/fig5_forecast_vs_actual.png` | Forecast vs actual, daytime only |",
        "",
    ]
    path.write_text("\n".join(lines))
    log.info("wrote %s", path)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    started = time.time()

    results = args.results_dir
    figures = results / "figures"
    results.mkdir(parents=True, exist_ok=True)

    series = load_or_fetch(
        start=args.data_start, end=args.data_end, cache_dir=args.cache_dir,
        csv=args.csv, force=args.force_download,
    )
    mpath = manifest_path(args.cache_dir, args.data_start, args.data_end)
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    log.info("series: %d half-hours, %s .. %s", len(series), series.index[0], series.index[-1])

    context_steps = args.context_days * STEPS_PER_DAY
    forecasters = [same_day_baseline(), same_week_baseline()]
    if not args.no_t0:
        forecasters.insert(
            0,
            T0Forecaster(
                context_steps=context_steps, repo_id=args.repo_id,
                revision=args.revision, batch_size=args.batch_size,
            ),
        )
    labels = {f.name: f.label for f in forecasters}
    methods = [f.name for f in forecasters]

    report = BacktestReport()
    windows = build_windows(
        series,
        test_start=date.fromisoformat(args.test_start),
        test_end=date.fromisoformat(args.test_end),
        gate_hour=args.gate_hour,
        context_steps=context_steps,
        report=report,
    )
    if args.limit_days:
        windows = windows[: args.limit_days]
    if not windows:
        raise SystemExit("no valid delivery days — widen the data window or move the test period")

    key = _cache_key(args, series_fingerprint(series), methods)
    cached = results / f"forecasts_{key}.parquet"
    if cached.exists() and not args.force_forecast:
        log.info("re-using cached forecasts %s", cached)
        df = pd.read_parquet(cached)
        report.n_windows = df["delivery_date"].nunique()
    else:
        df = run_backtest(series, forecasters, windows, report=report)
        df.to_parquet(cached)
        log.info("wrote %s", cached)

    df = metrics.add_daytime_flag(df, metrics.daytime_slots(df))

    peak = metrics.peak_proxy(df.loc[df["method"] == methods[0], "y"])
    overall = metrics.summarise(df, peak=peak)
    daytime_df = df.loc[df["is_daytime"]]
    daytime = metrics.summarise(daytime_df, peak=peak)

    per_day = metrics.per_day_errors(df)
    per_day_daytime = metrics.per_day_errors(daytime_df)
    primary = PRIMARY if PRIMARY in methods else methods[0]
    baselines = [m for m in methods if m != primary]
    skills = [
        metrics.bootstrap_skill(per_day, model=primary, reference=b, seed=args.seed) for b in baselines
    ]
    skills_daytime = [
        metrics.bootstrap_skill(per_day_daytime, model=primary, reference=b, seed=args.seed) for b in baselines
    ]
    night = metrics.night_forecast_diagnostic(df)

    tidy = pd.concat(
        [overall.assign(slice="all_hours"), daytime.assign(slice="daytime_only")], ignore_index=True
    )
    tidy.to_csv(results / "metrics.csv", index=False)
    pd.DataFrame(
        [dict(s, slice="all_hours") for s in skills]
        + [dict(s, slice="daytime_only") for s in skills_daytime]
    ).to_csv(results / "skill.csv", index=False)
    per_day.to_csv(results / "per_day_errors.csv", index=False)

    plots.plot_representative_days(df, labels, figures / "fig1_representative_days.png", primary)
    plots.plot_error_by_time_of_day(df, labels, figures / "fig2_error_by_time_of_day.png")
    plots.plot_by_month(df, labels, figures / "fig3_by_month.png")
    plots.plot_skill(skills, per_day, labels, figures / "fig4_skill.png", primary)
    plots.plot_predicted_vs_actual(df, labels, figures / "fig5_forecast_vs_actual.png")

    elapsed = time.time() - started
    write_summary(
        results / "summary.md", args=args, labels=labels, overall=overall, daytime=daytime,
        skills=skills, skills_daytime=skills_daytime, night=night, peak=peak,
        report=report.as_dict(), elapsed=elapsed, manifest=manifest, primary=primary,
    )
    (results / "run_meta.json").write_text(
        json.dumps(
            {
                "git_sha": _git_sha(),
                "args": {k: str(v) for k, v in vars(args).items()},
                "python": sys.version.split()[0],
                "packages": _versions(),
                "data_manifest": manifest,
                "backtest": report.as_dict(),
                "peak_proxy_mw": peak,
                "elapsed_seconds": round(elapsed, 1),
            },
            indent=2,
        )
        + "\n"
    )

    print("\n" + (results / "summary.md").read_text())
    return 0


def _versions() -> dict[str, str]:
    import importlib.metadata as md

    out = {}
    for name in ("numpy", "pandas", "matplotlib", "pyarrow", "requests", "torch", "tfc-t0"):
        try:
            out[name] = md.version(name)
        except Exception:
            out[name] = "not installed"
    return out


if __name__ == "__main__":
    raise SystemExit(main())
