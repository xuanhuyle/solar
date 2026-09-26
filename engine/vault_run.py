"""Scoring a frozen claim batch on its window - shared by the real vault and the dry run.

The real vault reads the forward window through the ``ForwardAccess`` the vault
issued; the dry run replays the same path on the consumed 2025 data and is
labelled NON-CONFIRMATORY. Both build every method exactly as discovery does,
run the live leak check on every arm and comparator against the window's own
data, and turn anything that cannot be scored into an error for that claim
(p = 1, kept in the batch's Holm family) - never into a crash.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from engine import arms as am
from engine import catalogue as cat
from engine import vault
from engine.discover import CONTEXT_STEPS, LEADS, _eligible
from engine.referee import leakcheck
from solarbench import metrics
from solarbench.backtest import BacktestReport, build_windows, run_backtest

NON_CONFIRMATORY = "NON-CONFIRMATORY dry run on consumed data - not a verdict"


def _coverage(series: pd.Series, first: date, last: date) -> float:
    from engine import zones

    grid = pd.date_range(zones.local_midnight_utc(first), zones.local_midnight_utc(pd.Timestamp(last) + pd.Timedelta(days=1)),
                         freq="30min", inclusive="left")
    return float(series.reindex(grid).notna().mean())


def score_batch(batch: dict, *, cache_dir: Path, model, access=None) -> dict:
    """Per-claim verdicts plus the full release package (skill, blocks, per-day errors, sources, leak checks)."""
    first, last = (date.fromisoformat(d) for d in batch["window"])
    target = batch["target"]
    accepted = (batch.get("accepted_at_freeze") or {}).get(target)
    weather = set()
    for c in batch["claims"]:
        weather |= am.weather_needs({"arms": [{"covariates": c["arm"]["covariates"]}]})
    if accepted and any(c["comparator"] == "accepted" for c in batch["claims"]):
        weather |= am.weather_needs({"arms": [{"covariates": accepted["arm"]["covariates"]}]})
    bundle, chosen, cover = None, None, {}
    for dataset in vault.SOURCES:  # the frozen source rule: the first >= 95% valid over the window
        try:
            b = am.load_bundle(target, first, last, cache_dir, weather=weather, with_reference=False,
                               access=access, dataset=dataset)
        except Exception as exc:
            cover[dataset] = f"unavailable: {type(exc).__name__}: {exc}"[:200]
            continue
        cover[dataset] = round(_coverage(b.target, first, last), 5)
        if cover[dataset] >= vault.MIN_VALID:
            bundle, chosen = b, dataset
            break
    errors: dict[str, str] = {}
    frames, names, leak = [], {}, {}
    if bundle is None:
        errors = {c["id"]: "no source passes the 95% rule over the window" for c in batch["claims"]}
    else:
        windows = build_windows(bundle.target, test_start=first, test_end=last, gate_hour=12, context_steps=CONTEXT_STEPS)
        for c in batch["claims"]:
            months = cat.SCOPES[c["scope"]]
            ws = [w for w in windows if months is None or w.delivery_date.month in months]
            spec = {"arms": [{"name": f"arm_{c['id'].lower()}", "covariates": c["arm"]["covariates"]}]}
            pair = {}
            try:
                for role, name in (("arm", f"arm_{c['id'].lower()}"), ("ref", c["comparator"])):
                    make = lambda b, n=name: am.build_method(n, spec, b, model, accepted)
                    method = make(bundle)
                    elig = _eligible(method, ws)
                    if not elig:
                        raise ValueError(f"{role} {name}: no eligible day in the window")
                    check = leakcheck.check_method(make, bundle, elig, leads=LEADS)
                    leak[f"{c['id']}:{role}"] = check
                    if not check["pass"]:
                        raise ValueError(f"{role} {name}: the live leak check failed")
                    df = run_backtest(bundle.target, method.forecasters, elig, report=BacktestReport())
                    df = df.loc[df["method"] == method.scored].copy()
                    df["method"] = f"{c['id']}:{role}"
                    frames.append(df)
                    pair[role] = f"{c['id']}:{role}"
                names[c["id"]] = (pair["arm"], pair["ref"])
            except Exception as exc:
                errors[c["id"]] = f"{type(exc).__name__}: {exc}"[:300]
    per_day = metrics.per_day_errors(pd.concat(frames, ignore_index=True)) if frames else \
        pd.DataFrame(columns=["delivery_date", "method", "sum_abs_err", "n"])
    decided = vault.decide(batch, per_day, names, errors)
    evidence = {}
    if len(per_day):
        wide = per_day.assign(mae=per_day["sum_abs_err"] / per_day["n"]).pivot(
            index="delivery_date", columns="method", values="mae").sort_index()
        evidence = {"dates": [str(d) for d in wide.index],
                    "mae_mw": {m: [None if pd.isna(v) else round(float(v), 2) for v in wide[m]] for m in wide.columns}}
    decided.update({"window": batch["window"], "sources": {target: {"chosen": chosen, "coverage": cover}},
                    "leak_checks": {k: {"pass": v["pass"]} for k, v in leak.items()}, "per_day": evidence})
    return decided
