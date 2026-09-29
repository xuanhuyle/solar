"""Experiment 4's run logic: selection, the arms, the in-run leak check, the scored run and its report.

Pure functions over data the runner loads (``run_prices.py`` is the only module that
reaches the price door). Everything follows ``PRICE_SPEC``; nothing here decides a
threshold, a day rule or a reading on its own.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from solarbench import metrics
from solarbench import price_exp as px
from solarbench import price_leak as lk
from solarbench import price_spec as ps

log = logging.getLogger(__name__)

SPEC = ps.PRICE_SPEC
PERIODS = SPEC["periods"]
ROOT = Path(__file__).resolve().parents[1]
K1_LOG = ROOT / "results" / "prices" / "k1_attempts.jsonl"


def file_sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- selection


def select_best_simple(series: pd.Series) -> dict:
    """simple_selection: the eight candidates on the 2023 windows, one common day set, lowest pooled MAE."""
    days = px.days_between(*PERIODS["selection"])
    report = px.WindowReport()
    windows = px.build_price_windows(series, days, report=report)
    rules = px.simple_rules()
    df = px.run_price_backtest(series, list(rules.values()), windows)
    finite = df.assign(ok=np.isfinite(df["y_hat"]) & np.isfinite(df["y"])).groupby(["delivery_date", "method"])["ok"].all()
    per_day_ok = finite.unstack("method").reindex(columns=list(rules))
    common = sorted(per_day_ok.index[per_day_ok.all(axis=1)])
    dropped = {m: sorted(str(d) for d in per_day_ok.index[~per_day_ok[m]]) for m in rules}
    sub = df[df["delivery_date"].isin(common)]
    mae = {m: float((sub.loc[sub["method"] == m, "y"] - sub.loc[sub["method"] == m, "y_hat"]).abs().mean())
           for m in rules}
    best = min(rules, key=lambda m: (mae[m], list(rules).index(m)))
    return {"best": best, "mae": mae, "days": len(common), "windows": report.as_dict(),
            "dropped_by_candidate": {m: v[:50] for m, v in dropped.items()},
            "dropped_count": {m: len(v) for m, v in dropped.items()}}


# ----------------------------------------------------------------------------------- K1 log


def k1_status(lear_sha: str | None = None) -> dict:
    """lear.scored_only_if: K1 counts only if a logged attempt passed with this exact solarbench/lear.py."""
    lear_sha = lear_sha or file_sha256("solarbench/lear.py")
    attempts = []
    if K1_LOG.exists():
        attempts = [json.loads(line) for line in K1_LOG.read_text().splitlines() if line.strip()]
    real = [a for a in attempts if not a.get("smoke")]
    passing = [a for a in real if a.get("pass") and a.get("lear_sha256") == lear_sha]
    return {"attempts": len(real), "passed": bool(passing), "lear_sha256": lear_sha,
            "passing_attempt": passing[0].get("run_id") if passing else None,
            "over_budget": len(real) > 3}


# -------------------------------------------------------------------------------------- arms


@dataclass
class Arms:
    best_name: str
    t0: object
    t0_cal: object
    t0_cal_strict: object
    t0_cal_wx: object | None
    best: object
    best_strict: object
    eq: object
    naive: object
    prev_week: object
    lear: object | None
    extra: dict = field(default_factory=dict)


def build_arms(best_name: str, model, *, weather: tuple | None, with_lear: bool) -> Arms:
    rules, strict_rules = px.simple_rules(), px.simple_rules(strict=True)
    best = px.Renamed(rules[best_name], "best_simple_2023")
    return Arms(
        best_name=best_name,
        t0=px.PriceT0Forecaster("t0", covariates=()).use_model(model),
        t0_cal=px.PriceT0Forecaster("t0_cal", covariates=(px.holiday(),)).use_model(model),
        t0_cal_strict=px.PriceT0Forecaster("t0_cal_strict", covariates=(px.holiday(),),
                                           horizon=px.STRICT_HORIZON).use_model(model),
        t0_cal_wx=(px.PriceT0Forecaster("t0_cal_wx", covariates=(px.holiday(), *weather)).use_model(model)
                   if weather else None),
        best=best,
        best_strict=px.Renamed(strict_rules[best_name], "best_simple_2023_strict"),
        eq=px.PriceEmpiricalQuantiles(base=px.Renamed(rules[best_name], "best_simple_2023")),
        naive=rules["naive_std"] if best_name != "naive_std" else px.Renamed(rules["naive_std"], "naive_std_ref"),
        prev_week=rules["prev_week"] if best_name != "prev_week" else px.Renamed(rules["prev_week"], "prev_week_ref"),
        lear=px.LearEnsemble() if with_lear else None,
    )


# ------------------------------------------------------------------------------ leak check


def in_run_leak_check(series: pd.Series, arms: Arms, *, p4_first_day: date, k3_passed: bool, k1_passed: bool) -> dict:
    """leak_controls: the real-model check at TEST_ORIGINS (each date = delivery day D), before any scoring."""
    out: dict = {"origins": {}, "pass": True}
    for ds in ps.TEST_ORIGINS:
        d = date.fromisoformat(ds)
        w = px.build_price_windows(series, [d], require_target=False)[0]
        ws = px.build_price_windows(series, [d], strict=True, require_target=False)[0]
        res: dict = {"covariate_refusal": lk.covariate_refusal(w)}
        normal = [arms.t0, arms.t0_cal, arms.best, arms.eq, arms.naive, arms.prev_week]
        if k1_passed and arms.lear is not None:
            normal.append(arms.lear)
        if k3_passed and arms.t0_cal_wx is not None and d >= p4_first_day:
            normal.append(arms.t0_cal_wx)
        for arm in normal:
            res[f"poison:{arm.name}"] = lk.target_poisoning(arm, series, w)
        for arm in [arms.t0, arms.t0_cal] + ([arms.lear] if k1_passed and arms.lear else []) + (
                [arms.t0_cal_wx] if k3_passed and arms.t0_cal_wx is not None and d >= p4_first_day else []):
            res[f"legal_afternoon:{arm.name}"] = lk.legal_change(arm, series, w, which="afternoon")
            res[f"legal_d2:{arm.name}"] = lk.legal_change(arm, series, w, which="d2")
        a = arms.eq.predict(series, [w])[0].quantiles
        s2 = series.copy()
        s2[px.day_hours(d - timedelta(days=1))] += 40.0
        res["legal_d1_moves_eq_bands"] = not np.array_equal(a, arms.eq.predict(s2, [w])[0].quantiles, equal_nan=True)
        for arm in (arms.t0_cal_strict, arms.best_strict):
            res[f"poison:{arm.name}"] = lk.target_poisoning(arm, series, ws)
        res["strict_afternoon_does_not_move"] = not lk.legal_change(arms.t0_cal_strict, series, ws, which="afternoon")
        res["strict_noon_moves"] = lk.legal_change(arms.t0_cal_strict, series, ws, which="noon")
        for arm in (arms.t0, arms.t0_cal):
            res[f"context_end:{arm.name}"] = lk.context_end(arm, series, w)
        res["context_end:t0_cal_strict"] = lk.context_end(arms.t0_cal_strict, series, ws)
        if k3_passed and arms.t0_cal_wx is not None and d >= p4_first_day:
            res["weather:t0_cal_wx"] = lk.weather_controls(arms.t0_cal_wx, series, w)
            res["context_end:t0_cal_wx"] = lk.context_end(arms.t0_cal_wx, series, w)
        ok = all((all(v.values()) if isinstance(v, dict) else bool(v)) for v in res.values())
        out["origins"][ds] = {"pass": ok, **{k: v for k, v in res.items()}}
        out["pass"] = out["pass"] and ok
    if k3_passed and arms.t0_cal_wx is not None:  # the P4 arm is also checked at its own first day
        w = px.build_price_windows(series, [p4_first_day], require_target=False)[0]
        res = {"poison": lk.target_poisoning(arms.t0_cal_wx, series, w),
               "weather": lk.weather_controls(arms.t0_cal_wx, series, w),
               "legal_afternoon": lk.legal_change(arms.t0_cal_wx, series, w, which="afternoon")}
        ok = all(res["poison"].values()) and all(res["weather"].values()) and res["legal_afternoon"]
        out["origins"][f"p4_first_day:{p4_first_day}"] = {"pass": ok, **res}
        out["pass"] = out["pass"] and ok
    return out


# ------------------------------------------------------------------------------ forecasting


def p4_day_ok(arm_wx, w) -> tuple[bool, str]:
    """weather_p4.day_rule: all 25 horizon cells of every covariate present, and each weather covariate's
    2160 context cells >= 98% valid (worst covariate)."""
    times = arm_wx.block_times(w.origin)
    c = arm_wx.context_hours
    for cv in arm_wx.covariates:
        v = np.asarray(cv.values(times), dtype="float64")
        if not np.isfinite(v[c:]).all():
            return False, "horizon"
        if getattr(cv, "issued", None) is not None and np.isfinite(v[:c]).mean() < px.MIN_VALID:
            return False, "context"
    return True, ""


def forecast_all(series: pd.Series, arms: Arms, *, p4_first_day: date, k3_passed: bool) -> tuple[pd.DataFrame, dict]:
    """Every arm once on its windows (t0.once): the test windows, the strict windows, the P4 windows."""
    info: dict = {}
    test_days = px.days_between(*PERIODS["test"])
    rep, rep_s = px.WindowReport(), px.WindowReport()
    windows = px.build_price_windows(series, test_days, report=rep)
    strict_windows = px.build_price_windows(series, test_days, strict=True, report=rep_s)
    info["windows"] = rep.as_dict()
    info["strict_windows"] = rep_s.as_dict()
    normal = [arms.t0, arms.t0_cal, arms.best, arms.eq, arms.naive, arms.prev_week]
    if arms.lear is not None:
        normal.append(arms.lear)
    frames = [px.run_price_backtest(series, normal, windows)]
    frames.append(px.run_price_backtest(series, [arms.t0_cal_strict, arms.best_strict], strict_windows))
    if k3_passed and arms.t0_cal_wx is not None:
        p4_last = date.fromisoformat(PERIODS["p4_days"][1])
        cand = [w for w in windows if p4_first_day <= w.delivery_date <= p4_last]
        keep, dropped = [], {"horizon": [], "context": []}
        for w in cand:
            ok, why = p4_day_ok(arms.t0_cal_wx, w)
            (keep.append(w) if ok else dropped[why].append(str(w.delivery_date)))
        info["p4_days"] = {"candidates": len(cand), "kept": len(keep), "dropped": dropped}
        if keep:
            frames.append(px.run_price_backtest(series, [arms.t0_cal_wx], keep))
    for arm in (arms.t0, arms.t0_cal, arms.t0_cal_strict, arms.t0_cal_wx):
        if arm is not None:
            info.setdefault("t0_missing", {})[arm.name] = arm.missing
    if arms.lear is not None:
        info["lear_logs"] = {str(n): {"forecast_days": lg.forecast_days, "no_forecast": lg.no_forecast,
                                      "dropped_rows": lg.dropped_rows, "scale_fallbacks": lg.scale_fallbacks}
                             for n, lg in arms.lear.logs.items()}
    return pd.concat(frames, ignore_index=True), info
