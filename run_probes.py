#!/usr/bin/env python3
"""Experiment 3, "t0 strengths probe": run the four probes frozen in ``solarbench.probes``.

    python run_probes.py check   # data coverage and day counts only; no forecasts
    python run_probes.py run     # all four probes; --probes P1,P3 for a subset

Data up to 2024-12-31 only.  Results go to ``results/probes/``.  Probes P1 and
P2 reuse the covariate slice's frozen weather covariates; P3 reads ODRÉ regional
solar; P4 reads ODRÉ national consumption.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import run_covariates as rc
from solarbench import covariates as cov
from solarbench import metrics, odre
from solarbench import probes as pr
from solarbench.backtest import BacktestReport, build_windows, quantile_column, run_backtest
from solarbench.data import STEPS_PER_DAY, load_or_fetch
from solarbench.forecasters import T0_REPO_ID, T0Forecaster, WeatherSlotRatio, night_zero_variant, statistical_baselines

log = logging.getLogger("run_probes")

ROOT = Path(__file__).resolve().parent
TEST_START, TEST_END = date(2024, 1, 1), date(2024, 12, 31)
SELECT_START, SELECT_END = date(2023, 1, 1), date(2023, 12, 31)
ODRE_START, ODRE_END = "2022-01-01", "2025-01-01"  # end exclusive: last day read is 2024-12-31


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["check", "run"])
    p.add_argument("--probes", default="P1,P2,P3,P4")
    p.add_argument("--cache-dir", type=Path, default=ROOT / "data")
    p.add_argument("--wx-cache", type=Path, default=ROOT / "wxcache")
    p.add_argument("--probe-cache", type=Path, default=ROOT / "probecache")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "probes")
    p.add_argument("--repo-id", default=T0_REPO_ID)
    p.add_argument("--revision", default=None)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--context-days", type=int, default=90)
    p.add_argument("--gate-hour", type=int, default=12)
    p.add_argument("--limit-days", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args(argv)


# ------------------------------------------------------------------ data


def load_solar(args) -> pd.Series:
    return load_or_fetch(start=ODRE_START, end=ODRE_END, cache_dir=args.cache_dir)


def load_consumption(args) -> tuple[pd.Series, pd.Series | None]:
    path = odre.fetch_columns(odre.NATIONAL, ["date_heure", "perimetre", "nature", "consommation"],
                              ODRE_START, ODRE_END, args.probe_cache)
    load = odre.load_column(path, "consommation")
    try:  # RTE's own forecast is a reference only: its absence changes no probe
        ref_path = odre.fetch_columns(odre.NATIONAL, ["date_heure", "perimetre", "prevision_j1"],
                                      ODRE_START, ODRE_END, args.probe_cache)
        ref = odre.load_column(ref_path, "prevision_j1")
    except Exception as exc:
        log.warning("prevision_j1 unavailable (%s); the RTE reference is dropped", exc)
        ref = None
    return load, ref


def load_regional(args) -> pd.DataFrame:
    path = odre.fetch_columns(odre.REGIONAL, ["date_heure", "libelle_region", "nature", "solaire"],
                              ODRE_START, ODRE_END, args.probe_cache)
    return odre.load_regional(path, "solaire", regions=list(cov.REGION_POINTS))


def windows_for(series, args, start=None, end=None, report=None):
    return build_windows(series, test_start=start or TEST_START, test_end=end or TEST_END, gate_hour=args.gate_hour,
                         context_steps=args.context_days * STEPS_PER_DAY, report=report)


def p3_windows(solar, regional, args):
    t = args.context_days * STEPS_PER_DAY
    all_w = windows_for(solar, args)
    keep = [w for w in all_w if pr.regional_coverage(regional, w.origin, t) >= cov.MIN_CONTEXT_VALID]
    return all_w, keep


# ----------------------------------------------------------------- check


def check(args) -> int:
    out: dict = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    solar = load_solar(args)
    t = args.context_days * STEPS_PER_DAY
    geo, wx, _ = rc.build_covariates(args)
    w12 = windows_for(solar, args)
    elig, _ = rc._eligible(w12, [geo, wx], t)
    out["P1_P2_days"] = len(elig)
    try:
        regional = load_regional(args)
        in_test = regional.loc["2024-01-01":"2024-12-31 23:30"]
        out["regional"] = {"regions": list(regional.columns), "first": str(regional.index[0]),
                           "last": str(regional.index[-1]),
                           "share_valid_2024_by_region": {k: round(float(v), 4) for k, v in in_test.notna().mean().items()}}
        _, keep = p3_windows(solar, regional, args)
        out["P3_days"] = len(keep)
    except Exception as exc:
        out["regional"] = {"error": str(exc)[:400]}
        out["P3_days"] = 0
    try:
        load, ref = load_consumption(args)
        out["consumption"] = {"first": str(load.index[0]), "last": str(load.index[-1]),
                              "share_valid_2024": round(float(load.loc["2024-01-01":"2024-12-31 23:30"].notna().mean()), 4),
                              "reference_available": ref is not None}
        out["P4_days"] = len(windows_for(load, args))
        out["P4_selection_days"] = len(windows_for(load, args, SELECT_START, SELECT_END))
    except Exception as exc:
        out["consumption"] = {"error": str(exc)[:400]}
        out["P4_days"] = 0
    rc._write_json(args.results_dir / "check.json", out)
    print(json.dumps(out, indent=2))
    return 0


# ------------------------------------------------------------------- run


def _t0(args, name, *, context_days=None, covariates=(), keep_quantiles=False, model=None) -> T0Forecaster:
    return T0Forecaster(
        context_steps=(context_days or args.context_days) * STEPS_PER_DAY, repo_id=args.repo_id,
        revision=args.revision, batch_size=args.batch_size, name=name, label=name,
        quantiles=pr.T0_LEVELS if keep_quantiles else (0.1, 0.5, 0.9),
        fixed_horizon=cov.COV_HORIZON if covariates else None, covariates=tuple(covariates),
        keep_quantiles=keep_quantiles, _model=model,
    )


def per_day_pinball(df: pd.DataFrame, model: str, reference: str, levels=pr.T0_LEVELS) -> pd.DataFrame:
    """Per-day pinball sums for two methods, over the targets where both have every quantile."""
    cols = [quantile_column(lv) for lv in levels]
    sub = df.loc[df["method"].isin([model, reference])].copy()
    sub["loss"] = pr.pinball(sub["y"].to_numpy(), sub[cols].to_numpy(), levels)
    wide = sub.pivot_table(index=["delivery_date", "target_time"], columns="method", values="loss").dropna()
    long = wide.stack().rename("loss").reset_index()
    g = long.groupby(["delivery_date", "method"])["loss"]
    return pd.DataFrame({"sum_abs_err": g.sum(), "n": g.size()}).reset_index()


def compare(per_day: pd.DataFrame, model: str, reference: str, seed: int) -> dict:
    s = metrics.bootstrap_skill(per_day, model=model, reference=reference, seed=seed, return_draws=True)
    draws = s.pop("draws")
    wide = per_day.pivot(index="delivery_date", columns="method", values="sum_abs_err")
    n = per_day.pivot(index="delivery_date", columns="method", values="n")
    dm, dr = wide[model] / n[model], wide[reference] / n[reference]
    s.update({"p_one_sided": float((1 + np.sum(draws <= 0.0)) / (1 + len(draws))),
              "loss_model": float(wide[model].sum() / n[model].sum()),
              "loss_reference": float(wide[reference].sum() / n[reference].sum()),
              "days_won": int((dm < dr).sum()), "days_lost": int((dm > dr).sum())})
    return s


def run_p1_p2(args, solar, geo, wx, model) -> tuple[pd.DataFrame, dict]:
    t = args.context_days * STEPS_PER_DAY
    elig, _ = rc._eligible(windows_for(solar, args), [geo, wx], t)
    if args.limit_days:
        elig = elig[: args.limit_days]
    ratio = WeatherSlotRatio(wx)
    inner = _t0(args, "wx_ratio_t0res_inner", context_days=pr.RESID_CONTEXT_DAYS, covariates=(geo, wx),
                keep_quantiles=True, model=model)
    methods = [
        _t0(args, "t0_wx", covariates=(geo, wx), keep_quantiles=True, model=model), night_zero_variant("t0_wx"),
        ratio,
        pr.EmpiricalQuantiles(WeatherSlotRatio(wx), name="wx_ratio_eq"), night_zero_variant("wx_ratio_eq"),
        pr.BiasCorrected(WeatherSlotRatio(wx), name="wx_ratio_bias"),
        pr.ResidualT0(WeatherSlotRatio(wx), inner, name="wx_ratio_t0res"), night_zero_variant("wx_ratio_t0res"),
    ]
    report = BacktestReport()
    df = run_backtest(solar, methods, elig, report=report)
    return df, {"windows": len(elig), "report": report.as_full_dict(), "specs": {m.name: m.spec() for m in methods}}


def run_p3(args, solar, regional, model) -> tuple[pd.DataFrame | None, dict]:
    all_w, keep = p3_windows(solar, regional, args)
    info = {"buildable": len(all_w), "eligible": len(keep)}
    if len(keep) < pr.MIN_P3_DAYS and not args.limit_days:
        info["not_runnable"] = f"only {len(keep)} days with regional data (< {pr.MIN_P3_DAYS})"
        return None, info
    if args.limit_days:
        keep = keep[: args.limit_days]
    t = args.context_days * STEPS_PER_DAY
    shared = T0Forecaster(context_steps=t, repo_id=args.repo_id, revision=args.revision, _model=model)
    ewma = [m for m in statistical_baselines() if m.name == "ewma"][0]
    methods = [
        _t0(args, "t0", model=model), night_zero_variant("t0"), ewma,
        pr.T0JointForecaster(regional, t, True, "t0_regjoint", repo_id=args.repo_id, revision=args.revision, _t0=shared),
        night_zero_variant("t0_regjoint"),
        pr.T0JointForecaster(regional, t, False, "t0_regindep", repo_id=args.repo_id, revision=args.revision, _t0=shared),
        night_zero_variant("t0_regindep"),
    ]
    report = BacktestReport()
    df = run_backtest(solar, methods, keep, report=report)
    info.update({"windows": len(keep), "report": report.as_full_dict(), "specs": {m.name: m.spec() for m in methods}})
    return df, info


def select_best_simple(args, load: pd.Series) -> tuple[str, pd.DataFrame]:
    """The P4 comparator: lowest MAE on 2023 among the frozen candidates (no t0 involved)."""
    cands = {m.name: m for m in [*statistical_baselines(), pr.weekday_mean_4w()] if m.name in pr.P4_CANDIDATES}
    df = run_backtest(load, list(cands.values()), windows_for(load, args, SELECT_START, SELECT_END))
    mae = df.assign(ae=(df["y"] - df["y_hat"]).abs()).groupby("method")["ae"].mean().sort_values()
    return str(mae.index[0]), mae.rename("mae_2023_mw").reset_index()


def run_p4(args, load, ref, model) -> tuple[pd.DataFrame, dict]:
    best, table = select_best_simple(args, load)
    windows = windows_for(load, args)
    if args.limit_days:
        windows = windows[: args.limit_days]
    cands = {m.name: m for m in [*statistical_baselines(), pr.weekday_mean_4w()]}
    methods = [_t0(args, "t0", model=model), _t0(args, "t0_cal", covariates=(pr.HolidayCovariate(),), model=model),
               cands[best]]
    if ref is not None:
        methods.append(pr.ReferenceForecast(ref, name="rte_j1", label="RTE's own D-1 forecast (reference)"))
    report = BacktestReport()
    df = run_backtest(load, methods, windows, report=report)
    return df, {"best_simple_2023": best, "selection_2023": table.to_dict(orient="records"), "windows": len(windows),
                "report": report.as_full_dict(), "specs": {m.name: m.spec() for m in methods}}


def run(args) -> int:
    rc._require_frozen()
    started = time.time()
    wanted = [p.strip() for p in args.probes.split(",") if p.strip()]
    solar = load_solar(args)
    base = _t0(args, "t0")
    model = base.load()
    rows, meta, frames = [], {"probes": {}}, {}
    if {"P1", "P2"} & set(wanted):
        geo, wx, _ = rc.build_covariates(args)
        df, info = run_p1_p2(args, solar, geo, wx, model)
        frames["P1P2"] = df
        meta["probes"]["P1P2"] = info
    if "P3" in wanted:
        df, info = run_p3(args, solar, load_regional(args), model)
        meta["probes"]["P3"] = info
        if df is not None:
            frames["P3"] = df
    if "P4" in wanted:
        load, ref = load_consumption(args)
        df, info = run_p4(args, load, ref, model)
        frames["P4"] = df
        meta["probes"]["P4"] = info

    args.results_dir.mkdir(parents=True, exist_ok=True)
    coverage = []
    for key, df in frames.items():
        df.to_parquet(args.results_dir / f"forecasts_{key}.parquet")
        metrics.summarise(df, peak=metrics.peak_proxy(df["y"])).to_csv(args.results_dir / f"metrics_{key}.csv", index=False)
    for probe in pr.PROBES:
        if probe.id not in wanted:
            continue
        key = "P1P2" if probe.id in ("P1", "P2") else probe.id
        if key not in frames:
            rows.append({"probe": probe.id, "role": "primary", "model": probe.t0_arm, "reference": probe.comparator,
                         "metric": probe.metric, "status": meta["probes"].get(key, {}).get("not_runnable", "not run")})
            continue
        df = frames[key]
        comparator = meta["probes"]["P4"]["best_simple_2023"] if probe.comparator == "best_simple_2023" else probe.comparator
        mae_days = metrics.per_day_errors(df)
        pairs = [("primary", (probe.t0_arm, comparator, probe.metric))] + [("secondary", x) for x in probe.secondary]
        for role, (m, r, metric) in pairs:
            r = comparator if r == "best_simple_2023" else r
            if m not in set(df["method"]) or r not in set(df["method"]):
                continue
            days = per_day_pinball(df, m, r) if metric == "pinball" else mae_days
            rows.append({"probe": probe.id, "role": role, "metric": metric, "status": "run",
                         **compare(days, m, r, args.seed)})
        if probe.id == "P1":
            slots = metrics.daytime_slots(df)
            day = metrics.add_daytime_flag(df, slots)
            day = day.loc[day["is_daytime"]]
            for name in ("t0_wx_night_zero", "wx_ratio_eq_night_zero", "wx_ratio_t0res_night_zero"):
                sub = day.loc[(day["method"] == name)].dropna(subset=["q10", "q90"])
                coverage.append({"method": name, "daytime_rows": int(len(sub)),
                                 "coverage_10_90": float(((sub["y"] >= sub["q10"]) & (sub["y"] <= sub["q90"])).mean()),
                                 "coverage_25_75": float(((sub["y"] >= sub["q25"]) & (sub["y"] <= sub["q75"])).mean()),
                                 "mean_width_10_90_mw": float((sub["q90"] - sub["q10"]).mean())})
    table = pd.DataFrame(rows)
    primaries = table.loc[(table["role"] == "primary") & (table["status"] == "run")]
    if len(primaries):
        adjusted = rc.holm(primaries["p_one_sided"].tolist())
        table.loc[primaries.index, "p_holm"] = adjusted
        cov_ok = {c["method"]: pr.COVERAGE_BAND[0] <= c["coverage_10_90"] <= pr.COVERAGE_BAND[1] for c in coverage}
        for i in primaries.index:
            won = table.at[i, "skill"] > 0 and table.at[i, "p_holm"] < pr.ALPHA
            if table.at[i, "probe"] == "P1":
                won = won and cov_ok.get(table.at[i, "model"], False)
            table.at[i, "won"] = bool(won)
    table.to_csv(args.results_dir / "probes.csv", index=False)
    pd.DataFrame(coverage).to_csv(args.results_dir / "coverage.csv", index=False)

    from run_benchmark import _git_sha, _resolve_revision, _versions

    meta.update({"git_sha": _git_sha(), "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "model": {"repo_id": args.repo_id, "revision_resolved": _resolve_revision(args.repo_id, args.revision)},
                 "frozen_probes": [p.__dict__ for p in pr.PROBES], "coverage": coverage,
                 "elapsed_s": round(time.time() - started, 1), "packages": _versions(),
                 "args": {k: str(v) for k, v in vars(args).items()}})
    rc._write_json(args.results_dir / "run_meta.json", meta)
    write_summary(args.results_dir, table, coverage, meta)
    print((args.results_dir / "summary.md").read_text(encoding="utf-8"))
    return 0


def write_summary(out: Path, table: pd.DataFrame, coverage: list[dict], meta: dict) -> None:
    lines = ["# Experiment 3: t0 strengths probe", "",
             f"Git `{meta['git_sha']}` · weights `{meta['model']['revision_resolved']}` · "
             f"{meta['elapsed_s'] / 60:.1f} min. Data up to 2024-12-31 only.", "",
             "| Probe | Role | t0 arm | vs | Metric | Skill [95% CI] | Loss (t0 vs ref) | Days won/lost | p | p (Holm) | Won |",
             "|---|---|---|---|---|---:|---:|---:|---:|---:|---|"]
    for _, r in table.iterrows():
        if r.get("status") != "run":
            lines.append(f"| {r['probe']} | {r['role']} | {r['model']} | {r['reference']} | {r['metric']} | "
                         f"{r['status']} | | | | | no |")
            continue
        holm = "" if pd.isna(r.get("p_holm", np.nan)) else f"{r['p_holm']:.4f}"
        won = "" if r["role"] != "primary" else ("**yes**" if r.get("won") else "no")
        lines.append(
            f"| {r['probe']} | {r['role']} | {r['model']} | {r['reference']} | {r['metric']} | "
            f"{r['skill']:+.1%} [{r['skill_lo95']:+.1%}, {r['skill_hi95']:+.1%}] | "
            f"{r['loss_model']:,.1f} vs {r['loss_reference']:,.1f} | {r['days_won']}/{r['days_lost']} | "
            f"{r['p_one_sided']:.4f} | {holm} | {won} |")
    if coverage:
        lines += ["", "## P1 band coverage (daytime actuals)", "",
                  "| Method | 10-90 coverage | 25-75 coverage | Mean 10-90 width (MW) |", "|---|---:|---:|---:|"]
        lines += [f"| {c['method']} | {c['coverage_10_90']:.1%} | {c['coverage_25_75']:.1%} | {c['mean_width_10_90_mw']:,.0f} |"
                  for c in coverage]
    p4 = meta["probes"].get("P4")
    if p4:
        lines += ["", f"## P4 comparator chosen on 2023: `{p4['best_simple_2023']}`", "",
                  "| Candidate | 2023 MAE (MW) |", "|---|---:|"]
        lines += [f"| {r['method']} | {r['mae_2023_mw']:,.0f} |" for r in p4["selection_2023"]]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    return {"check": check, "run": run}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
