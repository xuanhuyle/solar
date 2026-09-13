#!/usr/bin/env python3
"""Benchmark t0-alpha against historical-only baselines on RTE French national solar.

One command reproduces the whole experiment:

    python run_benchmark.py

It downloads RTE eCO2mix national solar generation (30-minute, MW) from ODRE,
caches it, runs a rolling day-ahead backtest over the test year, and writes
metrics and figures to ``results/``.  Identical arguments re-use the cached
forecasts and skip inference; metrics, bootstraps and figures are recomputed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from solarbench import metrics, plots
from solarbench.astro import CIVIL_TWILIGHT_ELEVATION_DEG, SUNSET_ELEVATION_DEG, dark_mask, mask_spec
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import (
    STEPS_PER_DAY,
    load_or_fetch,
    manifest_path,
    nature_counts_in,
    series_fingerprint,
)
from solarbench.forecasters import (
    BLEND_WEIGHT,
    EWMA_ALPHA,
    EWMA_SOURCES,
    SAME_SLOT_LOOKBACK_DAYS,
    T0_REPO_ID,
    Derived,
    T0Forecaster,
    night_zero_variant,
    statistical_baselines,
)

log = logging.getLogger("run_benchmark")

ROOT = Path(__file__).resolve().parent
PRIMARY = "t0"
#: The single pre-registered comparison of Phase 2. Everything else is secondary.
PRIMARY_REFERENCE = "blend_50"
#: Every method gets a CI'd skill against these in the ranking table.
RANKING_REFERENCES = ("prev_day", "blend_50")
#: The Phase 1 method set: their rows must reproduce the published numbers.
PHASE1_METHODS = ("t0", "prev_day", "prev_week")
#: Bump when the forecast frame's columns or a method's meaning changes, so a
#: cached parquet from older code is never served.
FORECAST_SCHEMA_VERSION = 2
FORECAST_COLUMNS = ("source_latest", "source_earliest", "n_sources")

DATA_VINTAGE = (
    "Inputs and targets are RTE's ex-post definitive eCO2mix series. Within the "
    "backtest nothing crosses the origin: every source timestamp is asserted at or "
    "before 12:00 D-1 and rewriting post-origin data changes no forecast. But the "
    "pre-origin values are final revised figures, not the real-time vintage an "
    "operator held at each noon gate; RTE later revises its real-time estimates in "
    "the consolidated and definitive publications. This is a controlled ex-post "
    "comparison of methods on identical history, not a reconstruction of live "
    "trading. Inputs are identical for every method; whether the ranking transfers "
    "to real-time-vintage inputs is untested."
)


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
    p.add_argument(
        "--methods", default=None,
        help="comma-separated subset of methods to run (default: all); e.g. t0,prev_day,prev_week reproduces Phase 1",
    )
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


def _resolve_revision(repo_id: str, revision: str | None) -> str:
    """The commit the weights actually came from, without touching the network.

    A pinned full sha resolves to itself. Otherwise the Hugging Face cache knows:
    ``refs/<branch>`` holds the sha a branch name resolved to at download time.
    """
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        return revision
    try:
        from huggingface_hub import constants

        root = Path(constants.HF_HUB_CACHE) / f"models--{repo_id.replace('/', '--')}"
        ref = root / "refs" / (revision or "main")
        if ref.exists():
            return ref.read_text(encoding="utf-8").strip()
        snapshots = sorted(p.name for p in (root / "snapshots").iterdir())
        if len(snapshots) == 1:
            return snapshots[0]
    except Exception:  # no cache, no hub library - nothing to resolve from
        pass
    return "unresolved"


def build_forecasters(args: argparse.Namespace) -> list:
    """The method list, from the registries; ``--methods`` selects a subset.

    Order is the reporting order. A derived method needs its source in the list.
    """
    candidates: list = []
    if not args.no_t0:
        candidates.append(
            T0Forecaster(
                context_steps=args.context_days * STEPS_PER_DAY, repo_id=args.repo_id,
                revision=args.revision, batch_size=args.batch_size,
            )
        )
        candidates.append(night_zero_variant(PRIMARY))
    candidates.extend(statistical_baselines())
    if not args.methods:
        return candidates
    wanted = [m.strip() for m in args.methods.split(",") if m.strip()]
    known = {f.name for f in candidates}
    unknown = sorted(set(wanted) - known)
    if unknown:
        hint = " (t0 and t0_night_zero are unavailable with --no-t0)" if args.no_t0 else ""
        raise SystemExit(f"unknown method(s) {unknown}; known: {sorted(known)}{hint}")
    chosen = [f for f in candidates if f.name in wanted]
    names = {f.name for f in chosen}
    for f in chosen:
        if isinstance(f, Derived) and f.source not in names:
            raise SystemExit(f"{f.name} derives from {f.source}, which --methods left out")
    return chosen


def comparison_pairs(methods: list[str]) -> list[tuple[str, str, str]]:
    """The pre-registered pairs: (model, reference, role)."""
    present = set(methods)
    pairs: list[tuple[str, str, str]] = []
    if PRIMARY in present and PRIMARY_REFERENCE in present:
        pairs.append((PRIMARY, PRIMARY_REFERENCE, "primary"))
    if PRIMARY in present:
        for m in methods:
            if m not in (PRIMARY, "t0_night_zero", PRIMARY_REFERENCE):
                pairs.append((PRIMARY, m, "secondary"))
    if "t0_night_zero" in present:
        for ref in (PRIMARY_REFERENCE, PRIMARY, "prev_day"):
            if ref in present:
                pairs.append(("t0_night_zero", ref, "secondary"))
    return pairs


def _cache_key(args: argparse.Namespace, fingerprint: str, forecasters: list) -> tuple[str, dict]:
    payload = {
        "schema": FORECAST_SCHEMA_VERSION,
        "data_fingerprint": fingerprint,
        "data_window": [args.data_start, args.data_end],
        "csv": str(args.csv) if args.csv else None,
        "test": [args.test_start, args.test_end],
        "gate_hour": args.gate_hour,
        "context_days": args.context_days,
        "methods": [f.name for f in forecasters],
        "specs": {f.name: f.spec() for f in forecasters},
        "repo_id": args.repo_id,
        "revision": args.revision,
        "batch_size": args.batch_size,
        "limit_days": args.limit_days,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16], payload


def _context_gap_windows(series: pd.Series, windows, context_steps: int) -> int:
    """How many origins have a missing half-hour inside the t0 context."""
    missing = series.index[series.isna()]
    if len(missing) == 0:
        return 0
    count = 0
    for w in windows:
        start = w.origin - (context_steps - 1) * pd.Timedelta(minutes=30)
        if ((missing >= start) & (missing <= w.origin)).any():
            count += 1
    return count


def _markdown_table(header: list[str], rows: list[list[str]], align: str | None = None) -> list[str]:
    align = align or ("---" + "|---:" * (len(header) - 1))
    lines = ["| " + " | ".join(header) + " |", "|" + align + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines


def ranking_markdown(rank: pd.DataFrame, labels: dict[str, str], slice_name: str) -> list[str]:
    sub = rank.loc[rank["slice"] == slice_name]
    header = ["#", "Method", "MAE (MW)", "nMAE (mean)", "nMAE (peak)"]
    refs = [r for r in RANKING_REFERENCES if f"vs_{r}_skill" in sub.columns]
    header += [f"vs {labels.get(r, r)}" for r in refs]
    rows = []
    for _, r in sub.iterrows():
        row = [str(int(r["rank"])), labels.get(r["method"], r["method"]), f"{r['mae_mw']:,.0f}",
               f"{r['nmae_mean']:.1%}", f"{r['nmae_peak']:.2%}"]
        for ref in refs:
            if r["method"] == ref:
                row.append("—")
            elif pd.isna(r.get(f"vs_{ref}_lo95", np.nan)):
                row.append(f"{r[f'vs_{ref}_skill']:+.1%}")
            else:
                row.append(f"{r[f'vs_{ref}_skill']:+.1%} [{r[f'vs_{ref}_lo95']:+.1%}, {r[f'vs_{ref}_hi95']:+.1%}]")
        rows.append(row)
    return _markdown_table(header, rows, align="---|---|---:|---:|---:" + "|---:" * len(refs))


def pairwise_markdown(pairwise: pd.DataFrame, labels: dict[str, str]) -> list[str]:
    header = ["Comparison", "Slice", "MAE reduction", "95% CI", "Days won / lost / tied", "Sign test p"]
    rows = []
    for _, r in pairwise.iterrows():
        name = f"{labels.get(r['model'], r['model'])} vs {labels.get(r['reference'], r['reference'])}"
        if r["role"] == "primary":
            name = f"**{name}** (primary)"
        rows.append([
            name, r["slice"].replace("_", " "), f"{r['skill']:+.1%}",
            f"[{r['skill_lo95']:+.1%}, {r['skill_hi95']:+.1%}]",
            f"{int(r['wins'])} / {int(r['losses'])} / {int(r['ties'])} of {int(r['n_days'])}",
            "n/a (all tied)" if r["wins"] + r["losses"] == 0 else f"{r['p_value']:.3f}",
        ])
    return _markdown_table(header, rows, align="---|---|---:|---:|---:|---:")


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
    scored: tuple[str, str],
    model: dict | None = None,
    phase2: dict | None = None,
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
        f"- Delivery days scored: **{report['n_windows']}** ({scored[0]} to {scored[1]}"
        + (f", limited from {args.test_start}..{args.test_end})" if args.limit_days else ")"),
        f"- Forecast issued at **{args.gate_hour:02d}:00 Europe/Paris on D-1**, covering 00:00-24:00 local of day D",
        f"- Context: **{args.context_days} days** ({args.context_days * STEPS_PER_DAY} half-hours) of solar history, no weather covariates",
        *(
            [f"- Weights: `{model['repo_id']}` @ `{model['revision_resolved']}`"
             + ("" if model["revision_requested"] else " (unpinned - follows `main`)")]
            if model else ["- Weights: none (baselines only)"]
        ),
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
    ]

    if phase2:
        rank = phase2["ranking"]
        lines += [
            "## Ranking (all hours)",
            "",
            "Every method, best to worst by pooled MAE, with its MAE reduction against the two",
            "reference baselines (95% moving-block bootstrap intervals).",
            "",
            *ranking_markdown(rank, labels, "all_hours"),
            "",
            "## Ranking (daytime only)",
            "",
            *ranking_markdown(rank, labels, "daytime_only"),
            "",
            "## Pairwise comparisons",
            "",
            f"The single pre-registered primary comparison is **{labels.get(PRIMARY, PRIMARY)} vs "
            f"{labels.get(PRIMARY_REFERENCE, PRIMARY_REFERENCE)}**; the others are secondary and should be",
            "read with the number of comparisons in mind. Win counts are per delivery day; the p-value is",
            "an exact two-sided sign test over the non-tied days.",
            "",
            *pairwise_markdown(phase2["pairwise"], labels),
            "",
        ]
        if phase2.get("night_zero") is not None and len(phase2["night_zero"]):
            nz = phase2["night_zero"]
            lines += [
                "## Night-zero audit",
                "",
                "What the dark mask covers on the scored rows, and what zeroing the raw t0 forecast",
                "there does to its error. The first row is the scored `t0_night_zero` mask; the",
                "civil-twilight row is a sensitivity computed from the same t0 forecasts, not a method.",
                "",
                "| Mask | Half-hours masked | Share | Inside reporting daytime | Actual inside mask (MW, sum / max) | t0 abs. error inside mask | MAE all hours | MAE daytime | vs blend_50 (all hours) | vs prev_day (all hours) |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
            for _, r in nz.iterrows():
                lines.append(
                    f"| {r['mask']} | {int(r['masked_half_hours']):,} | {r['masked_share']:.1%} | "
                    f"{int(r['masked_inside_reporting_daytime'])} | {r['sum_actual_inside_mask_mw']:,.0f} / {r['max_actual_inside_mask_mw']:,.0f} | "
                    f"{r['source_abs_err_inside_mask_mw']:,.0f} ({r['source_abs_err_inside_mask_mw'] / r['source_abs_err_total_mw']:.1%} of total) | "
                    f"{r.get('zeroed_mae_all_hours', float('nan')):,.0f} | {r.get('zeroed_mae_daytime_only', float('nan')):,.0f} | "
                    f"{r.get('zeroed_skill_vs_blend_50_all_hours', float('nan')):+.1%} [{r.get('zeroed_skill_vs_blend_50_all_hours_lo95', float('nan')):+.1%}, {r.get('zeroed_skill_vs_blend_50_all_hours_hi95', float('nan')):+.1%}] | "
                    f"{r.get('zeroed_skill_vs_prev_day_all_hours', float('nan')):+.1%} [{r.get('zeroed_skill_vs_prev_day_all_hours_lo95', float('nan')):+.1%}, {r.get('zeroed_skill_vs_prev_day_all_hours_hi95', float('nan')):+.1%}] |"
                )
            lines.append("")
        audit = phase2["source_audit"]
        lines += [
            "## Source-time audit",
            "",
            "Per method, from the saved forecasts: rows whose latest source lies after the origin",
            "(must be 0), the availability lag (origin minus latest source) and the age of the",
            "sources (target minus source), in hours.",
            "",
            "| Method | Rows after origin | Availability lag (min / median / max) | Source age (min / median / max) | Oldest source age | Sources per target |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for _, r in audit.iterrows():
            lines.append(
                f"| {labels.get(r['method'], r['method'])} | {int(r['rows_after_origin'])} | "
                f"{r['avail_lag_h_min']:.1f} / {r['avail_lag_h_median']:.1f} / {r['avail_lag_h_max']:.1f} | "
                f"{r['age_h_min']:.1f} / {r['age_h_median']:.1f} / {r['age_h_max']:.1f} | "
                f"{r['oldest_source_age_h_max']:.1f} | {r['n_sources_min']:.0f}–{r['n_sources_max']:.0f} |"
            )
        lines.append("")
        if phase2.get("daytime_mask_invariant") is not None:
            lines += [
                f"Reporting daytime mask identical on the Phase 1 rows and on all rows: "
                f"**{phase2['daytime_mask_invariant']}**.",
                "",
            ]

    lines += [
        "## Night sanity check",
        "",
        "Mean forecast on night half-hours — anything far from 0 MW means the model is",
        "hallucinating generation in the dark. (t0_night_zero reads small but non-zero",
        "here because the reporting night is climatological and its mask is astronomical.)",
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
        "| `figures/fig1_representative_days.png` | Four delivery days picked by a fixed rule (Phase 1 methods) |",
        "| `figures/fig2_error_by_time_of_day.png` | MAE by position in the delivery day (Phase 1 methods) |",
        "| `figures/fig3_by_month.png` | Seasonal breakdown (Phase 1 methods) |",
        "| `figures/fig4_skill.png` | Improvement over each Phase 1 baseline, with bootstrap CIs |",
        "| `figures/fig5_forecast_vs_actual.png` | Forecast vs actual, daytime only (Phase 1 methods) |",
        "| `figures/fig6_ranking.png` | Every method's MAE, both slices |",
        "| `figures/fig7_pairwise_skill.png` | Every pre-registered comparison with its interval |",
        "| `figures/fig8_phase2_by_time_of_day.png` | MAE by position in the delivery day: t0, t0_night_zero, prev_day, blend_50 |",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
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
    raw_path = series.attrs.get("raw_path") or (str(args.csv) if args.csv else None)
    mpath = manifest_path(args.cache_dir, args.data_start, args.data_end)
    manifest = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else {}
    log.info("series: %d half-hours, %s .. %s", len(series), series.index[0], series.index[-1])

    context_steps = args.context_days * STEPS_PER_DAY
    forecasters = build_forecasters(args)
    labels = {f.name: f.label for f in forecasters}
    methods = [f.name for f in forecasters]
    log.info("methods: %s", ", ".join(methods))

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
        raise SystemExit("no valid delivery days - widen the data window or move the test period")

    key, key_payload = _cache_key(args, series_fingerprint(series), forecasters)
    cached = results / f"forecasts_{key}.parquet"
    cached_report = results / f"forecasts_{key}.report.json"
    df = None
    if cached.exists() and cached_report.exists() and not args.force_forecast:
        candidate = pd.read_parquet(cached)
        if all(c in candidate.columns for c in FORECAST_COLUMNS):
            log.info("re-using cached forecasts %s", cached)
            df = candidate
            report = BacktestReport.from_full_dict(json.loads(cached_report.read_text(encoding="utf-8"))["report"])
        else:
            log.warning("cached forecasts %s predate the current schema; recomputing", cached)
    if df is None:
        df = run_backtest(series, forecasters, windows, report=report)
        df.to_parquet(cached)
        cached_report.write_text(
            json.dumps({"key_payload": key_payload, "git_sha": _git_sha(), "report": report.as_full_dict()},
                       indent=2) + "\n",
            encoding="utf-8",
        )
        log.info("wrote %s", cached)

    slots = metrics.daytime_slots(df)
    mask_invariant = metrics.daytime_mask_invariant(df, PHASE1_METHODS)
    if not mask_invariant:
        log.warning("the reporting daytime mask differs between the Phase 1 rows and all rows")
    df = metrics.add_daytime_flag(df, slots)
    pd.DataFrame(sorted(slots), columns=["month", "slot"]).assign(is_daytime=True).to_csv(
        results / "daytime_mask.csv", index=False
    )

    peak = metrics.peak_proxy(df.loc[df["method"] == methods[0], "y"])
    overall = metrics.summarise(df, peak=peak)
    daytime_df = df.loc[df["is_daytime"]]
    daytime = metrics.summarise(daytime_df, peak=peak)

    per_day = metrics.per_day_errors(df)
    per_day_daytime = metrics.per_day_errors(daytime_df)
    primary = PRIMARY if PRIMARY in methods else methods[0]
    baselines = [f.name for f in forecasters if f.name != primary and not isinstance(f, Derived)]
    skills = [metrics.pair_skill(per_day, model=primary, reference=b, seed=args.seed) for b in baselines]
    skills_daytime = [
        metrics.pair_skill(per_day_daytime, model=primary, reference=b, seed=args.seed) for b in baselines
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
    per_day_daytime.to_csv(results / "per_day_errors_daytime.csv", index=False)
    metrics.mae_by(df, "month").to_csv(results / "by_month.csv", index=False)
    metrics.mae_by(df, "slot").to_csv(results / "by_slot.csv", index=False)

    # ---------------------------------------------------------------- Phase 2
    per_day_by_slice = {"all_hours": per_day, "daytime_only": per_day_daytime}
    pairs = comparison_pairs(methods)
    pairwise = metrics.pairwise_skill(per_day_by_slice, pairs, seed=args.seed) if pairs else pd.DataFrame()
    rank = metrics.ranking(
        {"all_hours": overall, "daytime_only": daytime}, per_day_by_slice,
        references=tuple(r for r in RANKING_REFERENCES if r in methods), seed=args.seed,
    )
    pairwise.to_csv(results / "pairwise.csv", index=False)
    rank.to_csv(results / "ranking.csv", index=False)
    if pairs:
        pd.DataFrame(
            [dict(metrics.concentration(pd_, model=m, reference=r), role=role, slice=name)
             for (m, r, role) in pairs for name, pd_ in per_day_by_slice.items()]
        ).to_csv(results / "concentration.csv", index=False)
        sensitivity_pairs = [p for p in pairs if p[2] == "primary" or p[:2] in ((PRIMARY, "prev_day"), ("t0_night_zero", PRIMARY_REFERENCE))]
        pd.DataFrame(
            [dict(row, slice=name)
             for (m, r, _) in sensitivity_pairs for name, pd_ in per_day_by_slice.items()
             for row in metrics.bootstrap_sensitivity(pd_, model=m, reference=r, seed=args.seed)]
        ).to_csv(results / "bootstrap_sensitivity.csv", index=False)
        metrics.skill_by(df, "month", pairs).to_csv(results / "pairwise_by_month.csv", index=False)
    banded = metrics.add_band_flag(df)
    band_mae = metrics.mae_by(banded, "band")
    band_mae.to_csv(results / "by_band.csv", index=False)
    if pairs:
        metrics.skill_by(banded, "band", pairs).to_csv(results / "pairwise_by_band.csv", index=False)
    audit = metrics.source_audit(df)
    audit.to_csv(results / "source_audit.csv", index=False)

    night_zero = None
    if PRIMARY in methods and "t0_night_zero" in methods and PRIMARY_REFERENCE in methods:
        src = df.loc[df["method"] == PRIMARY].reset_index(drop=True)
        target_index = pd.DatetimeIndex(src["target_time"])
        masks = {
            f"sun below {SUNSET_ELEVATION_DEG} deg (scored)": dark_mask(target_index, threshold_deg=SUNSET_ELEVATION_DEG),
            f"civil twilight {CIVIL_TWILIGHT_ELEVATION_DEG:.0f} deg (sensitivity)": dark_mask(target_index, threshold_deg=CIVIL_TWILIGHT_ELEVATION_DEG),
        }
        night_zero = metrics.night_zero_audit(df, masks=masks, daytime_slots_used=slots)
        extra_rows = []
        by_slot_rows = []
        for label, mask in masks.items():
            zeroed = src.copy()
            zeroed["y_hat"] = np.where(mask, 0.0, zeroed["y_hat"])
            zeroed["method"] = "zeroed"
            others = df.loc[df["method"].isin([PRIMARY_REFERENCE, "prev_day"])]
            frame = pd.concat([zeroed, others], ignore_index=True)
            extra = {}
            for name, sub in (("all_hours", frame), ("daytime_only", frame.loc[frame["is_daytime"]])):
                summ = metrics.summarise(sub, peak=peak).set_index("method")
                extra[f"zeroed_mae_{name}"] = float(summ.loc["zeroed", "mae_mw"])
                extra[f"zeroed_nmae_{name}"] = float(summ.loc["zeroed", "nmae_mean"])
                pdz = metrics.per_day_errors(sub)
                for ref in (PRIMARY_REFERENCE, "prev_day"):
                    if ref in set(sub["method"]):
                        s = metrics.pair_skill(pdz, model="zeroed", reference=ref, seed=args.seed)
                        extra[f"zeroed_skill_vs_{ref}_{name}"] = s["skill"]
                        extra[f"zeroed_skill_vs_{ref}_{name}_lo95"] = s["skill_lo95"]
                        extra[f"zeroed_skill_vs_{ref}_{name}_hi95"] = s["skill_hi95"]
            extra_rows.append(extra)
            per_slot = src.assign(masked=mask).groupby("slot")
            for slot, sub in per_slot:
                m = sub["masked"].to_numpy()
                by_slot_rows.append({
                    "mask": label, "slot": int(slot), "days": int(len(sub)), "masked_days": int(m.sum()),
                    "sum_actual_inside_mask_mw": float(sub.loc[m, "y"].sum()),
                    "max_actual_inside_mask_mw": float(sub.loc[m, "y"].max()) if m.any() else float("nan"),
                    "source_abs_err_inside_mask_mw": float((sub.loc[m, "y"] - sub.loc[m, "y_hat"]).abs().sum()),
                })
        night_zero = pd.concat([night_zero, pd.DataFrame(extra_rows)], axis=1)
        night_zero.to_csv(results / "night_zero_audit.csv", index=False)
        pd.DataFrame(by_slot_rows).to_csv(results / "night_zero_audit_by_slot.csv", index=False)

    phase2 = {
        "ranking": rank, "pairwise": pairwise, "source_audit": audit,
        "night_zero": night_zero, "daytime_mask_invariant": mask_invariant,
    }

    # ---------------------------------------------------------------- figures
    plot_labels = {m: labels[m] for m in PHASE1_METHODS if m in labels}
    plot_skills = [s for s in skills if s["reference"] in plot_labels]
    plots.plot_representative_days(df, plot_labels, figures / "fig1_representative_days.png", primary)
    plots.plot_error_by_time_of_day(df, plot_labels, figures / "fig2_error_by_time_of_day.png")
    plots.plot_by_month(df, plot_labels, figures / "fig3_by_month.png")
    if plot_skills:
        plots.plot_skill(plot_skills, per_day, plot_labels, figures / "fig4_skill.png", primary)
    plots.plot_predicted_vs_actual(df, plot_labels, figures / "fig5_forecast_vs_actual.png")
    plots.plot_ranking(rank, labels, figures / "fig6_ranking.png")
    if len(pairwise):
        plots.plot_pairwise(pairwise, labels, figures / "fig7_pairwise_skill.png")
    phase2_labels = {m: labels[m] for m in ("t0", "t0_night_zero", "prev_day", "blend_50") if m in labels}
    if phase2_labels:
        plots.plot_error_by_time_of_day(df, phase2_labels, figures / "fig8_phase2_by_time_of_day.png",
                                        title="Error by position in the delivery day - Phase 2 methods")

    # ---------------------------------------------------------------- write-up
    elapsed = time.time() - started
    model = None
    if not args.no_t0:
        model = {
            "repo_id": args.repo_id,
            "revision_requested": args.revision,
            "revision_resolved": _resolve_revision(args.repo_id, args.revision),
        }
    write_summary(
        results / "summary.md", args=args, labels=labels, overall=overall, daytime=daytime,
        skills=skills, skills_daytime=skills_daytime, night=night, peak=peak,
        report=report.as_dict(), elapsed=elapsed, manifest=manifest, primary=primary,
        scored=(str(df["delivery_date"].min()), str(df["delivery_date"].max())),
        model=model, phase2=phase2,
    )
    readme_tables = ["## Ranking (all hours)", "", *ranking_markdown(rank, labels, "all_hours"), "",
                     "## Ranking (daytime only)", "", *ranking_markdown(rank, labels, "daytime_only"), ""]
    if len(pairwise):
        readme_tables += ["## Pairwise comparisons", "", *pairwise_markdown(pairwise, labels), ""]
    (results / "readme_tables.md").write_text("\n".join(readme_tables), encoding="utf-8")

    test_end_exclusive = (date.fromisoformat(args.test_end) + timedelta(days=1)).isoformat()
    nature_test_period = nature_counts_in(Path(raw_path), args.test_start, test_end_exclusive) if raw_path and Path(raw_path).exists() else {}
    (results / "run_meta.json").write_text(
        json.dumps(
            {
                "git_sha": _git_sha(),
                "args": {k: str(v) for k, v in vars(args).items()},
                "model": model,
                "methods": methods,
                "method_specs": {f.name: f.spec() for f in forecasters},
                "phase2": {
                    "primary_comparison": [PRIMARY, PRIMARY_REFERENCE],
                    "ranking_references": list(RANKING_REFERENCES),
                    "ewma_alpha": EWMA_ALPHA, "ewma_sources": EWMA_SOURCES,
                    "same_slot_lookback_days": SAME_SLOT_LOOKBACK_DAYS, "blend_weight": BLEND_WEIGHT,
                    "night_zero_mask": mask_spec(SUNSET_ELEVATION_DEG),
                    "daytime_mask_invariant": mask_invariant,
                    "forecast_cache_key": key,
                },
                "data": {
                    "fingerprint": series_fingerprint(series),
                    "sha256": manifest.get("sha256"),
                    "fetched_at": manifest.get("fetched_at"),
                    "source": manifest.get("source"),
                    "nature_counts_window": manifest.get("nature_counts_window", {}),
                    "nature_counts_test_period": nature_test_period,
                    "context_gap_windows": _context_gap_windows(series, windows, context_steps),
                    "data_vintage": DATA_VINTAGE,
                },
                "python": sys.version.split()[0],
                "packages": _versions(),
                "data_manifest": manifest,
                "backtest": report.as_full_dict(),
                "peak_proxy_mw": peak,
                "elapsed_seconds": round(elapsed, 1),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _echo(results / "summary.md")
    return 0


def _echo(path: Path) -> None:
    """Echo the summary, tolerating a console that cannot encode it.

    The file is UTF-8, but the terminal's encoding is not ours to choose —
    cp1252 or cp932 on Windows, ASCII in a redirected pipe. A completed run must
    not die on a decorative character in its own output.
    """
    text = path.read_text(encoding="utf-8")
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    sys.stdout.write("\n" + text.encode(encoding, "replace").decode(encoding, "replace") + "\n")


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
