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
from datetime import date
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
#: The K1 and K2 attempt logs, hand-transcribed and tracked in git (results/ is git-ignored, so a log there would
#: never reach a fresh checkout): lear.scored_only_if and gates.K1.attempts read K1_LOG; gates.K2.on_fail
#: ("every attempt logged in run_meta") reads K2_LOG. An empty file means no attempt.
K1_LOG = ROOT / "docs" / "experiment_4" / "k1_attempts.jsonl"
K2_LOG = ROOT / "docs" / "experiment_4" / "k2_attempts.jsonl"
K1_MAX_ATTEMPTS = 3


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
            "dropped_by_candidate": dropped,  # counted and listed: every dropped day
            "dropped_count": {m: len(v) for m, v in dropped.items()}}


# ----------------------------------------------------------------------------------- K1 log


def _jsonl(raw: bytes | None) -> list[dict]:
    return [] if raw is None else [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


def k1_status(lear_sha: str | None = None) -> dict:
    """lear.scored_only_if: K1 counts only if a logged attempt passed with this exact solarbench/lear.py.
    ``log_present`` / ``log_sha256`` record which log was read (the sha256 of its bytes; None if absent)."""
    lear_sha = lear_sha or file_sha256("solarbench/lear.py")
    raw = K1_LOG.read_bytes() if K1_LOG.exists() else None
    attempts = _jsonl(raw)
    real = [a for a in attempts if not a.get("smoke") and a.get("counts_as_attempt", True)]
    within = real[:K1_MAX_ATTEMPTS]  # gates.K1.attempts: at most 3; a logged fourth never counts
    passing = [a for a in within if a.get("pass") and a.get("lear_sha256") == lear_sha]
    return {"attempts": len(real), "passed": bool(passing), "lear_sha256": lear_sha,
            "passing_attempt": passing[0].get("run_id") if passing else None,
            "over_budget": len(real) > K1_MAX_ATTEMPTS, "log_present": raw is not None,
            "log_sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None}


def k2_attempts() -> list[dict]:
    """gates.K2.on_fail ("every attempt logged in run_meta"): the earlier K2 attempts, one JSON object per line of
    the tracked K2_LOG (an empty list if the file is absent); the current dispatch's attempt goes after them."""
    return _jsonl(K2_LOG.read_bytes() if K2_LOG.exists() else None)


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
    lear_eq: object | None = None  # lear_ens_eq: the one object the check poisons and the scored pass forecasts
    extra: dict = field(default_factory=dict)


def build_arms(best_name: str, model, *, weather: tuple | None, with_lear: bool, lear_processes: int = 1) -> Arms:
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
        naive=rules["naive_std"],
        prev_week=rules["prev_week"],
        lear=px.LearEnsemble(processes=lear_processes) if with_lear else None,
        # the bands' base is its own LearEnsemble (same code, same bits), so arms.lear.logs stay lear_ens's own
        lear_eq=(px.PriceEmpiricalQuantiles(base=px.LearEnsemble(processes=lear_processes), name="lear_ens_eq")
                 if with_lear else None),
    )


# ------------------------------------------------------------------------------ leak check


def _t0_arms(arms: Arms, k3_passed: bool) -> list:
    """The t0 arms a run forecasts: t0, t0_cal, t0_cal_strict, and t0_cal_wx only when K3 passed."""
    return [arms.t0, arms.t0_cal, arms.t0_cal_strict] + (
        [arms.t0_cal_wx] if k3_passed and arms.t0_cal_wx is not None else [])


def _lear_arms(arms: Arms, with_lear: bool) -> list:
    """lear_ens and its bands lear_ens_eq, the one object build_arms made (never a second instance)."""
    if not with_lear or arms.lear is None:
        return []
    if arms.lear_eq is None:
        raise ValueError("lear_ens without lear_ens_eq: build the arms with build_arms")
    return [arms.lear, arms.lear_eq]


def _passed(res: dict) -> bool:
    return all((all(v.values()) if isinstance(v, dict) else bool(v)) for v in res.values())


def refuse_unlisted_variates(arms: Arms, *, k3_passed: bool, weather: tuple | None = None) -> None:
    """leak_controls, variate whitelist: raise before anything is forecast if a t0 arm to be run carries a
    covariate outside the whitelist (price_leak.variate_whitelist)."""
    for arm in _t0_arms(arms, k3_passed):
        res = lk.variate_whitelist(arm, weather)
        if not all(res.values()):
            raise AssertionError(f"variate whitelist: {getattr(arm, 'name', arm)} refused: {res}")


def in_run_leak_check(series: pd.Series, arms: Arms, *, p4_first_day: date, k3_passed: bool, k1_passed: bool,
                      weather: tuple | None = None) -> dict:
    """leak_controls: the real-model check at TEST_ORIGINS (each date = delivery day D), before any scoring.
    ``weather`` is the tuple load_weather returned (the whitelist then checks t0_cal_wx carries those objects)."""
    out: dict = {"origins": {}, "pass": True}
    wx_checked = k3_passed and arms.t0_cal_wx is not None
    lear = _lear_arms(arms, k1_passed)
    out["whitelist"] = {f"whitelist:{arm.name}": lk.variate_whitelist(arm, weather)
                        for arm in _t0_arms(arms, k3_passed)}
    out["pass"] = _passed(out["whitelist"])
    for ds in ps.TEST_ORIGINS:
        d = date.fromisoformat(ds)
        w = px.build_price_windows(series, [d], require_target=False)[0]
        ws = px.build_price_windows(series, [d], strict=True, require_target=False)[0]
        wx_here = wx_checked and d >= p4_first_day
        res: dict = {"covariate_refusal": lk.covariate_refusal(w)}
        normal = [arms.t0, arms.t0_cal, arms.best, arms.eq, arms.naive, arms.prev_week, *lear]
        if wx_here:
            normal.append(arms.t0_cal_wx)
        for arm in normal:
            res[f"poison:{arm.name}"] = lk.target_poisoning(arm, series, w)
        for arm in [arms.t0, arms.t0_cal] + ([arms.lear] if lear else []) + ([arms.t0_cal_wx] if wx_here else []):
            res[f"legal_afternoon:{arm.name}"] = lk.legal_change(arm, series, w, which="afternoon")
            res[f"legal_d2:{arm.name}"] = lk.legal_change(arm, series, w, which="d2")
        # "editing D-1 must move best_simple_eq's error quantiles": Q_tau(E_t) itself, not f_D + Q_tau(E_t)
        res["legal_d1_moves_eq_error_quantiles"] = lk.eq_error_quantiles_move(arms.eq, series, w)
        for arm in (arms.t0_cal_strict, arms.best_strict):
            res[f"poison:{arm.name}"] = lk.target_poisoning(arm, series, ws)
        res["strict_afternoon_does_not_move"] = not lk.legal_change(arms.t0_cal_strict, series, ws, which="afternoon")
        res["strict_noon_moves"] = lk.legal_change(arms.t0_cal_strict, series, ws, which="noon")
        res[f"covariate_refusal:{arms.t0_cal.name}"] = lk.covariate_refusal_arm(arms.t0_cal, series, w)
        res[f"covariate_refusal:{arms.t0_cal_strict.name}"] = lk.covariate_refusal_arm(arms.t0_cal_strict, series, ws)
        for arm in (arms.t0, arms.t0_cal, arms.best):
            res[f"context_end:{arm.name}"] = lk.context_end(arm, series, w)
        for arm in (arms.t0_cal_strict, arms.best_strict):
            res[f"context_end:{arm.name}"] = lk.context_end(arm, series, ws)
        if wx_here:
            res["weather:t0_cal_wx"] = lk.weather_controls(arms.t0_cal_wx, series, w)
            res["context_end:t0_cal_wx"] = lk.context_end(arms.t0_cal_wx, series, w)
            res["covariate_refusal:t0_cal_wx"] = lk.covariate_refusal_arm(arms.t0_cal_wx, series, w)
        ok = _passed(res)
        out["origins"][ds] = {"pass": ok, **res}
        out["pass"] = out["pass"] and ok
    if wx_checked:  # the P4 arm is also checked at its own first day, with every control that names it
        w = px.build_price_windows(series, [p4_first_day], require_target=False)[0]
        res = {"poison": lk.target_poisoning(arms.t0_cal_wx, series, w),
               "weather": lk.weather_controls(arms.t0_cal_wx, series, w),
               "legal_afternoon": lk.legal_change(arms.t0_cal_wx, series, w, which="afternoon"),
               "legal_d2": lk.legal_change(arms.t0_cal_wx, series, w, which="d2"),
               "context_end": lk.context_end(arms.t0_cal_wx, series, w),
               "covariate_refusal": lk.covariate_refusal_arm(arms.t0_cal_wx, series, w)}
        ok = _passed(res)
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


def _lear_logs(ens) -> dict:
    return {str(n): {"forecast_days": lg.forecast_days, "no_forecast": lg.no_forecast,
                     "dropped_rows": lg.dropped_rows, "scale_fallbacks": lg.scale_fallbacks}
            for n, lg in ens.logs.items()}


def forecast_all(series: pd.Series, arms: Arms, *, p4_first_day: date, k3_passed: bool,
                 weather: tuple | None = None) -> tuple[pd.DataFrame, dict]:
    """Every arm once on its windows (t0.once): the test windows, the strict windows, the P4 windows.
    A t0 arm outside the variate whitelist is refused before anything is forecast."""
    refuse_unlisted_variates(arms, k3_passed=k3_passed, weather=weather)
    info: dict = {}
    for arm in (arms.t0, arms.t0_cal, arms.t0_cal_strict, arms.t0_cal_wx):  # count this pass only, not the checks
        if arm is not None:
            arm.missing = {"context": [], "sanitised": []}
    test_days = px.days_between(*PERIODS["test"])
    rep, rep_s = px.WindowReport(), px.WindowReport()
    windows = px.build_price_windows(series, test_days, report=rep)
    strict_windows = px.build_price_windows(series, test_days, strict=True, report=rep_s)
    info["windows"] = rep.as_dict()
    info["strict_windows"] = rep_s.as_dict()
    # K1 passed (arms.lear built): lear_ens, and its empirical bands (the report-only secondary), the same
    # lear_ens_eq object the in-run leak check poisoned
    normal = [arms.t0, arms.t0_cal, arms.best, arms.eq, arms.naive, arms.prev_week, *_lear_arms(arms, True)]
    frames = [px.run_price_backtest(series, normal, windows)]
    frames.append(px.run_price_backtest(series, [arms.t0_cal_strict, arms.best_strict], strict_windows))
    if k3_passed and arms.t0_cal_wx is not None:
        p4_last = date.fromisoformat(PERIODS["p4_days"][1])
        cand = [w for w in windows if p4_first_day <= w.delivery_date <= p4_last]
        keep, dropped = [], {"horizon": [], "context": []}
        for w in cand:
            ok, why = p4_day_ok(arms.t0_cal_wx, w)
            (keep.append(w) if ok else dropped[why].append(str(w.delivery_date)))
        info["p4_days"] = {"candidates": len(cand), "kept": len(keep), "dropped": dropped,
                           "kept_days": [str(w.delivery_date) for w in keep]}
        if keep:
            frames.append(px.run_price_backtest(series, [arms.t0_cal_wx], keep))
    for arm in (arms.t0, arms.t0_cal, arms.t0_cal_strict, arms.t0_cal_wx):
        if arm is not None:
            info.setdefault("t0_missing", {})[arm.name] = arm.missing
    if arms.lear is not None:
        info["lear_logs"] = _lear_logs(arms.lear)
        info["lear_eq_logs"] = _lear_logs(arms.lear_eq.base)  # its last pass: the history windows of the bands
    return pd.concat(frames, ignore_index=True), info
