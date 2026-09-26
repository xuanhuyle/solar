"""The known-answer gate: before any discovery with a weather covariate, prove on
real t0 that the covariate pipeline is aligned and that t0 uses it.

A *planted* covariate - a noisy copy of the target's own future, pushed through
exactly the pipeline the real weather covariate uses (hourly archive values
mapped onto 30-minute slots) - must cut t0's error; a *decoy* of pure noise
must not; shifting the planted signal by one hour must cost accuracy. The
planted and decoy arms are oracles by construction (they read the future), so
they run under the backtest's two-key oracle exemption and are never findings.

``KA_RULES`` is fixed here before the gate's first run.
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd

from engine import arms as am
from engine import catalogue as cat
from engine import covs
from solarbench import metrics
from solarbench.backtest import build_windows, run_backtest

KA_PERIOD = ("2024-09-02", "2024-11-04")  # 64 days where every weather covariate is covered
KA_RULES = {
    "planted_ratio_max": 0.95,       # planted MAE / t0 MAE: the planted signal must help by >= 5%
    "decoy_ratio_min": 0.98,         # pure noise must not help ...
    "decoy_ratio_max": 1.05,         # ... nor break t0
    "shift_penalty_min": 1.01,       # a +-1 h shift must cost >= 1%
    "noise_sd_share_of_p99": 0.05,
    "seed": 0,
}
WEATHER = {"wx_temperature": "temperature", "wx_radiation": "radiation"}


def _mae(df: pd.DataFrame, name: str) -> float:
    rows = df.loc[df["method"] == name]
    return float((rows["y"] - rows["y_hat"]).abs().mean())


def run_gate(target_id: str, covariate: str, *, cache_dir, model=None, bundle: am.DataBundle | None = None,
             limit_days: int | None = None) -> dict:
    from solarbench.forecasters import _NonFiniteWatcher

    if covariate not in WEATHER or target_id not in cat.COVARIATES[covariate]["targets"]:
        raise ValueError(f"no known-answer gate for {target_id} / {covariate}")
    watcher = _NonFiniteWatcher()
    logging.getLogger("t0.model.model").addHandler(watcher)
    start, end = KA_PERIOD
    if bundle is None:
        bundle = am.load_bundle(target_id, start, end, cache_dir, weather={WEATHER[covariate]}, with_reference=False)
    windows = build_windows(bundle.target, test_start=date.fromisoformat(start), test_end=date.fromisoformat(end),
                            gate_hour=12, context_steps=am.CONTEXT_DAYS * 48)
    if limit_days:
        windows = windows[:limit_days]
    if model is None:
        model = am._t0("loader", (), None).load()
    y = bundle.target
    rng = np.random.default_rng(KA_RULES["seed"])
    p99 = metrics.peak_proxy(y.dropna())
    convention = covs.CONVENTION[WEATHER[covariate]]
    if convention == "mean_preceding_hour":  # the value stamped h is the mean over [h - 1 h, h)
        hourly = y.resample("1h", label="right", closed="left").mean()
    else:  # an instantaneous reading at h: the slot centred on h
        hourly = y.reindex(pd.date_range(y.index[0].ceil("h"), y.index[-1], freq="1h"))
    planted = hourly + rng.normal(0.0, KA_RULES["noise_sd_share_of_p99"] * p99, len(hourly))
    decoy = pd.Series(rng.normal(0.0, float(hourly.std()), len(hourly)), index=hourly.index)

    def arm(name, h):
        provider = covs.weather_provider(name, h, y.index, 0, convention, oracle=True)
        return am._t0(name, (provider,), model)

    arms = {"t0_base": am._t0("t0_base", (), model),
            "ka_oracle_planted": arm("ka_oracle_planted", planted),
            "ka_oracle_decoy": arm("ka_oracle_decoy", decoy),
            "ka_oracle_shift_m1h": arm("ka_oracle_shift_m1h", planted.shift(-1)),
            "ka_oracle_shift_p1h": arm("ka_oracle_shift_p1h", planted.shift(1))}
    oracle = frozenset(k for k in arms if "oracle" in k)
    df = run_backtest(y, list(arms.values()), windows, oracle_methods=oracle)
    mae = {k: _mae(df, k) for k in arms}
    planted_ratio = mae["ka_oracle_planted"] / mae["t0_base"]
    decoy_ratio = mae["ka_oracle_decoy"] / mae["t0_base"]
    shift_penalty = min(mae["ka_oracle_shift_m1h"], mae["ka_oracle_shift_p1h"]) / mae["ka_oracle_planted"]
    checks = {
        "planted_helps": planted_ratio <= KA_RULES["planted_ratio_max"],
        "decoy_does_not_help": decoy_ratio >= KA_RULES["decoy_ratio_min"],
        "decoy_does_not_break": decoy_ratio <= KA_RULES["decoy_ratio_max"],
        "aligned": shift_penalty >= KA_RULES["shift_penalty_min"],
        "no_sanitised_output": watcher.count == 0,
    }
    return {"gate": "known_answer", "target": target_id, "covariate": covariate, "pass": all(checks.values()),
            "checks": checks, "rules": KA_RULES, "period": list(KA_PERIOD), "days": int(df["delivery_date"].nunique()),
            "mae_mw": {k: round(v, 2) for k, v in mae.items()}, "planted_ratio": round(planted_ratio, 4),
            "decoy_ratio": round(decoy_ratio, 4), "shift_penalty": round(shift_penalty, 4),
            "convention": convention, "limit_days": limit_days}


def passed_gates(entries: list[dict]) -> set[tuple[str, str]]:
    """(target, covariate) pairs whose latest known-answer gate passed, under full (not smoke) runs."""
    latest: dict[tuple[str, str], bool] = {}
    for e in entries:
        p = e.get("payload", {})
        if e.get("kind") == "gate" and p.get("gate") == "known_answer" and not p.get("limit_days"):
            latest[(p["target"], p["covariate"])] = bool(p.get("pass"))
    return {k for k, ok in latest.items() if ok}
