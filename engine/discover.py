"""Run one declarative probe on the discovery zone and return its result.

Each method (arm or comparator) runs in its own backtest over the windows it is
eligible for, so one method's missing values never drop days from another
comparison; each comparison is then scored on the days *both* of its methods
forecast. Results are exploratory: they guide the researcher, and never count
as findings.
"""

from __future__ import annotations

import logging
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from engine import arms as am
from engine import catalogue as cat
from engine.ledger import EXPLORATORY
from engine.spec import spec_sha256, validate_probe
from solarbench import covariates as cov
from solarbench import metrics
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import STEPS_PER_DAY

log = logging.getLogger(__name__)
CONTEXT_STEPS = am.CONTEXT_DAYS * STEPS_PER_DAY


def _eligible(method: am.Method, windows: list) -> list:
    """Windows whose covariate horizon is complete and whose covariate context is >= 98% valid."""
    weather = [p for p in method.providers if getattr(p, "issued", None) is not None]
    if not weather:
        return list(windows)
    keep = []
    for w in windows:
        share, horizon_ok = cov.window_coverage(w.origin, weather, CONTEXT_STEPS, cov.COV_HORIZON)
        if horizon_ok and share >= cov.MIN_CONTEXT_VALID:
            keep.append(w)
    return keep


def compare(per_day: pd.DataFrame, model: str, reference: str, seed: int) -> dict:
    """Skill of ``model`` over ``reference`` on their common days (paired 7-day block bootstrap)."""
    wide = per_day.pivot(index="delivery_date", columns="method", values="sum_abs_err")[[model, reference]].dropna()
    n = per_day.pivot(index="delivery_date", columns="method", values="n").loc[wide.index, [model, reference]]
    pair = per_day.loc[per_day["delivery_date"].isin(wide.index) & per_day["method"].isin([model, reference])]
    s = metrics.bootstrap_skill(pair, model=model, reference=reference, seed=seed, return_draws=True)
    draws = s.pop("draws")
    dm, dr = wide[model] / n[model], wide[reference] / n[reference]
    return {
        "days": int(len(wide)), "skill": round(float(s["skill"]), 6),
        "ci95": [round(float(s["skill_lo95"]), 6), round(float(s["skill_hi95"]), 6)],
        "p_one_sided": round(float((1 + np.sum(draws <= 0.0)) / (1 + len(draws))), 6),
        "mae_arm": round(float(wide[model].sum() / n[model].sum()), 3),
        "mae_vs": round(float(wide[reference].sum() / n[reference].sum()), 3),
        "days_won": int((dm < dr).sum()), "days_lost": int((dm > dr).sum()),
    }


def run_probe(spec_raw: dict, *, cache_dir: Path, accepted: dict | None = None, model=None, seed: int = 0,
              limit_days: int | None = None, bundle: am.DataBundle | None = None) -> dict:
    started = time.time()
    spec = validate_probe(spec_raw)
    sha = spec_sha256(spec)
    start, end = cat.PERIODS[spec["period"]]
    if bundle is None:
        bundle = am.load_bundle(spec["target"], start, end, cache_dir, weather=am.weather_needs(spec))
    report = BacktestReport()
    windows = build_windows(bundle.target, test_start=date.fromisoformat(start), test_end=date.fromisoformat(end),
                            gate_hour=12, context_steps=CONTEXT_STEPS, report=report)
    months = cat.SCOPES[spec["scope"]]
    if months is not None:
        windows = [w for w in windows if w.delivery_date.month in months]
    if limit_days:
        windows = windows[:limit_days]
    names = []
    for c in spec["comparisons"]:
        for n in (c["arm"], c["vs"]):
            if n not in names:
                names.append(n)
    needs_t0 = any(n not in ("best_simple", "rte_j1") for n in names)
    if needs_t0 and model is None:
        model = am._t0("loader", (), None).load()
    frames, info = [], {}
    for name in names:
        method = am.build_method(name, spec, bundle, model, accepted)
        elig = _eligible(method, windows)
        r = BacktestReport()
        df = run_backtest(bundle.target, method.forecasters, elig, report=r) if elig else pd.DataFrame()
        if len(df):
            df = df.loc[df["method"] == method.scored].copy()
            df["method"] = name
            frames.append(df)
        info[name] = {"scored_as": method.scored, "eligible_days": len(elig), "spec": method.spec(),
                      "dropped_nonfinite": r.as_full_dict().get("skipped_nonfinite_forecast", [])}
    per_day = metrics.per_day_errors(pd.concat(frames, ignore_index=True)) if frames else pd.DataFrame()
    results = []
    for c in spec["comparisons"]:
        row = {"arm": c["arm"], "vs": c["vs"], "metric": c["metric"]}
        if len(per_day) and {c["arm"], c["vs"]} <= set(per_day["method"]):
            row.update(compare(per_day, c["arm"], c["vs"], seed))
        else:
            row["error"] = "no common scored days"
        if c["vs"] == "rte_j1":
            row["note"] = "reference only: RTE's forecast never decides anything"
        results.append(row)
    evidence = {}
    if len(per_day):
        wide = per_day.assign(mae=per_day["sum_abs_err"] / per_day["n"]).pivot(
            index="delivery_date", columns="method", values="mae").sort_index()
        evidence = {"dates": [str(d) for d in wide.index],
                    "mae_mw": {m: [None if pd.isna(v) else round(float(v), 2) for v in wide[m]] for m in wide.columns}}
    return {
        "probe_sha256": sha, "spec": spec, "status": EXPLORATORY, "catalogue_sha256": cat.catalogue_sha256(),
        "target": spec["target"], "period": spec["period"], "scope": spec["scope"],
        "data": bundle.meta, "windows_built": len(windows), "methods": info, "comparisons": results,
        "per_day": evidence, "elapsed_s": round(time.time() - started, 1),
    }
