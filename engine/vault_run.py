"""Scoring a frozen claim batch on its window - shared by the real vault and the dry run.

The real vault reads the forward window through the ``ForwardAccess`` the vault
issued; the dry run replays the same path on the consumed 2025 data and is
labelled NON-CONFIRMATORY. Both build every method exactly as discovery does.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from engine import arms as am
from engine import catalogue as cat
from engine import vault
from engine.discover import CONTEXT_STEPS, _eligible
from solarbench import metrics
from solarbench.backtest import BacktestReport, build_windows, run_backtest

NON_CONFIRMATORY = "NON-CONFIRMATORY dry run on consumed data - not a verdict"


def _coverage(series: pd.Series, first: date, last: date) -> float:
    from engine import zones

    grid = pd.date_range(zones.local_midnight_utc(first), zones.local_midnight_utc(pd.Timestamp(last) + pd.Timedelta(days=1)),
                         freq="30min", inclusive="left")
    return float(series.reindex(grid).notna().mean())


def score_batch(batch: dict, *, cache_dir: Path, model, access=None) -> dict:
    """Per-claim verdicts plus the full release package (skill, blocks, per-day errors, data vintage)."""
    first, last = (date.fromisoformat(d) for d in batch["window"])
    frames, names, info = [], {}, {}
    by_target: dict[str, list[dict]] = {}
    for c in batch["claims"]:
        by_target.setdefault(c["target"], []).append(c)
    sources = {}
    for target, claims in by_target.items():
        weather = set()
        for c in claims:
            weather |= am.weather_needs({"arms": [{"covariates": c["arm"]["covariates"]}]})
        bundle, chosen, cover = None, None, {}
        for dataset in vault.SOURCES:  # the frozen source rule: the first >= 95% valid over the window
            try:
                b = am.load_bundle(target, first, last, cache_dir, weather=weather, with_reference=False,
                                   access=access, dataset=dataset)
            except Exception as exc:
                cover[dataset] = f"unavailable: {type(exc).__name__}"
                continue
            cover[dataset] = round(_coverage(b.target, first, last), 5)
            if cover[dataset] >= vault.MIN_VALID:
                bundle, chosen = b, dataset
                break
        sources[target] = {"chosen": chosen, "coverage": cover}
        if bundle is None:
            for c in claims:
                info[c["id"]] = {"error": "no source passes the 95% rule"}
            continue
        windows = build_windows(bundle.target, test_start=first, test_end=last, gate_hour=12, context_steps=CONTEXT_STEPS)
        for c in claims:
            months = cat.SCOPES[c["scope"]]
            ws = [w for w in windows if months is None or w.delivery_date.month in months]
            spec = {"arms": [{"name": f"arm_{c['id'].lower()}", "covariates": c["arm"]["covariates"]}]}
            pair = {}
            for role, name in (("arm", f"arm_{c['id'].lower()}"), ("ref", c["comparator"])):
                method = am.build_method(name, spec, bundle, model, batch.get("accepted_at_freeze"))
                elig = _eligible(method, ws)
                df = run_backtest(bundle.target, method.forecasters, elig, report=BacktestReport()) if elig else pd.DataFrame()
                label = f"{c['id']}:{role}"
                if len(df):
                    df = df.loc[df["method"] == method.scored].copy()
                    df["method"] = label
                    frames.append(df)
                pair[role] = label
            names[c["id"]] = (pair["arm"], pair["ref"])
    per_day = metrics.per_day_errors(pd.concat(frames, ignore_index=True)) if frames else pd.DataFrame()
    decided = vault.decide(batch, per_day, {k: v for k, v in names.items() if k not in info}) if len(per_day) else \
        {"batch_id": batch["batch_id"], "claims": []}
    for cid, err in info.items():
        decided["claims"].append({"claim": cid, "verdict": "NOT PASS", **err})
    evidence = {}
    if len(per_day):
        wide = per_day.assign(mae=per_day["sum_abs_err"] / per_day["n"]).pivot(
            index="delivery_date", columns="method", values="mae").sort_index()
        evidence = {"dates": [str(d) for d in wide.index],
                    "mae_mw": {m: [None if pd.isna(v) else round(float(v), 2) for v in wide[m]] for m in wide.columns}}
    decided.update({"window": batch["window"], "sources": sources, "per_day": evidence})
    return decided
