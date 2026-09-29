"""Experiment 4's known-answer gates (PRICE_SPEC['gates']), implemented as written.

* K1 - the clean-room LEAR (``solarbench.lear``) reproduces the published EPF-FR results:
  every hour of 2015-01-04..2016-12-31 forecast with the published configuration, the
  deviations inside the frozen bands, the mean absolute difference from the published
  ensemble <= 0.25 EUR/MWh. A code check only, never a claim.
* K2 - t0 adapter parity: each t0 arm's ``predict`` against a reference built without it
  (bit for bit on one window, within 0.01 EUR/MWh in one batch).
* K3 - the hourly weather port carries a signal t0 can use: planted, decoy and +-1 h shifted
  oracle readings pushed through each convention's port, judged by the engine's ka/2 thresholds.

Experiment 4 is discovery-grade (PRICE_SPEC['status']): these gates only decide whether an arm may be
scored. Their oracle arms are never findings, and nothing here can satisfy the project's
independent-confirmation milestone.
"""

from __future__ import annotations

import copy
import hashlib
import logging
import re
import time
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from engine import covs
from solarbench import covariates as cov
from solarbench import lear
from solarbench import metrics
from solarbench import price_exp as px
from solarbench import price_spec as ps
from solarbench.forecasters import _NonFiniteWatcher

log = logging.getLogger(__name__)

GATES = ps.PRICE_SPEC["gates"]
K1 = GATES["K1"]
K2 = GATES["K2"]
K3 = GATES["K3"]
HOUR = px.HOUR

# ------------------------------------------------------------------------------------ K1

#: gates.K1.tolerance, as numbers (the spec states them in prose; tests check the prose).
K1_HOURS = 17_472
K1_DECIMALS = 4
K1_ENSEMBLE_BAND = (-0.02, 0.01)
K1_WINDOW_BAND = (-0.03, 0.02)
K1_MAX_MEAN_ABS_DIFF = 0.25
K1_WINDOWS: tuple[int, ...] = tuple(ps.PRICE_SPEC["lear"]["calibration_windows_days"])
K1_ENSEMBLE = "LEAR Ensemble"
K1_REAL = "Real price"
SMOKE = "smoke: not a K1 attempt"
#: The pinned published forecasts (gates.K1.reference) and the FR.csv the avail run recorded.
PUBLISHED_SHA256 = re.search(r"sha256 ([0-9a-f]{64})", K1["reference"]).group(1)
EPF_FR_SHA256 = ps.AVAIL["epf_fr_sha256"]
#: EPF-FR's columns, matched after strip and casefold (the file has leading spaces).
EPF_COLUMNS = {"price": "prices", "generation": "generation forecast", "load": "system load forecast"}
LEAR_FILE = Path(lear.__file__).resolve()


def k1_column(window: int) -> str:
    return f"LEAR {window}"


def k1_names() -> list[str]:
    return [*(k1_column(n) for n in K1_WINDOWS), K1_ENSEMBLE]


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


#: gates.K1.attempts ("the sha256 of the solarbench/lear.py it ran"): the file as it was when this module (and
#: the ``lear`` it imported) was loaded. run_k1 hashes it again at its start and after forecasting (spawned
#: workers re-import lear from disk); any difference stops K1 and the run is not an attempt.
LEAR_SHA256_AT_IMPORT = sha256_file(LEAR_FILE)


def k1_days(limit_days: int | None = None) -> list[date]:
    """The K1 test days (gates.K1.test_period); ``limit_days``: only the first ones (smoke)."""
    days = px.days_between(*K1["test_period"])
    return days[:limit_days] if limit_days is not None else days


def k1_hours(days: Sequence[date]) -> pd.DatetimeIndex:
    """EPF-FR's naive local hours of ``days``: 24 per day, the row stamped h is the hour starting h."""
    return pd.DatetimeIndex([pd.Timestamp(d) + pd.Timedelta(hours=h) for d in days for h in range(24)])


def read_epf_fr(path) -> dict[str, pd.DataFrame]:
    """FR.csv as three LEAR day matrices (price, generation, load), via ``lear.epf_day_matrix``."""
    df = pd.read_csv(path, index_col=0, parse_dates=True, float_precision="round_trip")
    by_key = {str(c).strip().casefold(): c for c in df.columns}
    missing = [want for want in EPF_COLUMNS.values() if want not in by_key]
    if missing:
        raise ValueError(f"{path}: EPF-FR columns not found: {missing} (have {list(df.columns)})")
    idx = pd.DatetimeIndex(pd.to_datetime(df.index))
    if idx.tz is not None:
        raise ValueError(f"{path}: EPF-FR's index must be naive local time")
    return {key: lear.epf_day_matrix(pd.Series(df[by_key[want]].to_numpy(dtype="float64"), index=idx))
            for key, want in EPF_COLUMNS.items()}


def read_published(path) -> pd.DataFrame:
    pub = pd.read_csv(path, index_col=0, parse_dates=True, float_precision="round_trip")
    pub.index = pd.DatetimeIndex(pd.to_datetime(pub.index))
    pub.columns = [str(c).strip() for c in pub.columns]
    return pub


def published_check(pub: pd.DataFrame, hours: pd.DatetimeIndex) -> dict:
    """The reference MAEs recomputed over the 17,472 K1 hours; they must equal published_mae to 4 decimals."""
    want = dict(K1["published_mae"])
    need = [K1_REAL, *want]
    out = {"match": False, "mae": {}, "mae_rounded": {}, "hours": int(len(hours)), "rows_in_csv": int(len(pub)),
           "rows_outside_period": int((~pub.index.isin(hours)).sum()), "reason": None}
    absent = [c for c in need if c not in pub.columns]
    if absent:
        out["reason"] = f"published CSV lacks columns {absent}"
        return out
    if pub.index.has_duplicates:
        out["reason"] = "published CSV has duplicate stamps"
        return out
    sub = pub.reindex(hours)[need].astype("float64")
    incomplete = int(sub.isna().any(axis=1).sum())
    if len(hours) != K1_HOURS or incomplete:
        out["reason"] = f"published CSV does not hold all {K1_HOURS} K1 hours ({incomplete} missing or NaN)"
        return out
    y = sub[K1_REAL].to_numpy()
    out["mae"] = {c: float(np.mean(np.abs(sub[c].to_numpy() - y))) for c in want}
    out["mae_rounded"] = {c: round(v, K1_DECIMALS) for c, v in out["mae"].items()}
    out["match"] = all(out["mae_rounded"][c] == want[c] for c in want)
    if not out["match"]:
        out["reason"] = "the recomputed published MAEs differ from gates.K1.published_mae"
    return out


def _window_log(lg: lear.WindowLog) -> dict:
    return {"window": lg.window, "forecast_days": lg.forecast_days, "no_forecast": lg.no_forecast,
            "no_forecast_count": {k: len(v) for k, v in lg.no_forecast.items()},
            "dropped_rows": lg.dropped_rows, "scale_fallbacks": lg.scale_fallbacks}


def _forecast_window(window: int, prices: pd.DataFrame, generation: pd.DataFrame, load: pd.DataFrame,
                     days: list[date]) -> tuple[int, pd.DataFrame, dict]:
    """One K1 window over every day (features_k1: exog = [generation, load], no holiday dummy).

    BLAS is held to one thread so a window gives the same bits in a worker process and in-process.
    """
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        f, lg = lear.forecast(prices, list(days), window=window, exog=[generation, load], n_extra=0)
    return window, f.reindex(index=list(days), columns=range(24)), _window_log(lg)


def k1_forecasts(mats: Mapping[str, pd.DataFrame], days: Sequence[date], *, processes: int = 4
                 ) -> tuple[dict[str, pd.DataFrame], dict[str, dict]]:
    """The clean-room forecasts of ``days`` for the four windows and their ensemble (``[days, 24]`` each).

    The windows may run in parallel processes (spawned); results are collected in window order.
    """
    args = [(n, mats["price"], mats["generation"], mats["load"], list(days)) for n in K1_WINDOWS]
    if processes and processes > 1:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=min(int(processes), len(args)),
                                 mp_context=mp.get_context("spawn")) as ex:
            futures = [ex.submit(_forecast_window, *a) for a in args]
            results = [f.result() for f in futures]
    else:
        results = [_forecast_window(*a) for a in args]
    parts = {k1_column(n): f for n, f, _ in results}
    parts[K1_ENSEMBLE] = lear.ensemble([parts[k1_column(n)] for n in K1_WINDOWS])
    return parts, {str(n): lg for n, _, lg in results}


def k1_coverage(clean: Mapping[str, np.ndarray]) -> dict:
    """The every-hour part of gates.K1.tolerance: the non-finite hours of each window and the ensemble.
    It reads only the clean-room forecasts (never the published ones), so it computes no MAE or difference."""
    non_finite = {c: int((~np.isfinite(np.asarray(clean[c], dtype="float64"))).sum()) for c in k1_names()}
    return {"every_hour_forecast": not any(non_finite.values()), "non_finite_hours": non_finite}


def k1_verdict(clean: Mapping[str, np.ndarray], pub: pd.DataFrame) -> dict:
    """gates.K1.tolerance on aligned hours: ``clean`` maps each published column to the clean-room forecasts
    of ``pub``'s rows. Without a forecast at every hour nothing is computed and the verdict is a fail.
    run_k1 calls it only on all 17,472 K1 hours (an attempt), never in a smoke."""
    names = k1_names()
    cover = k1_coverage(clean)
    every_hour = cover["every_hour_forecast"]
    out = {"hours": int(len(pub)), **cover,
           "mae": None, "reference_mae": None, "deviation": None, "mean_abs_diff_ensemble": None,
           "checks": {"every_hour_forecast": every_hour}, "pass": False}
    if not every_hour:
        out["reason"] = "not every hour was forecast: no MAE or difference is computed"
        return out
    y = pub[K1_REAL].to_numpy(dtype="float64")
    mae = {c: float(np.mean(np.abs(np.asarray(clean[c], dtype="float64") - y))) for c in names}
    ref = {c: float(np.mean(np.abs(pub[c].to_numpy(dtype="float64") - y))) for c in names}
    dev = {c: (mae[c] / ref[c] - 1.0) if ref[c] > 0 else float("nan") for c in names}
    diff = float(np.mean(np.abs(np.asarray(clean[K1_ENSEMBLE], dtype="float64")
                                - pub[K1_ENSEMBLE].to_numpy(dtype="float64"))))
    lo, hi = K1_ENSEMBLE_BAND
    wlo, whi = K1_WINDOW_BAND
    checks = {"every_hour_forecast": True, "ensemble_deviation": bool(lo <= dev[K1_ENSEMBLE] <= hi)}
    for n in K1_WINDOWS:
        checks[f"window_deviation:{k1_column(n)}"] = bool(wlo <= dev[k1_column(n)] <= whi)
    checks["mean_abs_diff_ensemble"] = bool(diff <= K1_MAX_MEAN_ABS_DIFF)
    out.update(mae=mae, reference_mae=ref, deviation=dev, mean_abs_diff_ensemble=diff, checks=checks,
               **{"pass": all(checks.values())})
    return out


def _k1_stop(res: dict, reasons: list[str], started: float) -> dict:
    """status 'stop': not a K1 attempt (price_run.k1_status counts only entries with counts_as_attempt)."""
    res.update(status="stop", counts_as_attempt=False, stop_reasons=list(reasons),
               run_seconds=round(time.perf_counter() - started, 3))
    res["pass"] = False
    return res


def run_k1(fr_csv: Path, published_csv: Path, *, processes: int = 4, limit_days: int | None = None) -> dict:
    """K1 (gates.K1): one attempt, or with ``limit_days`` a smoke that is never a K1 attempt.

    status: 'stop' (the published MAEs do not recompute, an input is not the pinned file, or
    solarbench/lear.py changed between this module's import, the start and the end of the run: not an attempt,
    the owner decides), 'pass' or 'fail' (an attempt over all 17,472 hours), or SMOKE.

    A smoke forecasts only the first ``limit_days`` K1 days (fewer than all of them) and records only
    whether every one of its hours was forecast and the window logs: it never computes an MAE, a deviation
    or a difference from the published forecasts (gates.K1.tolerance: none on a subset of the K1 hours).
    """
    started = time.perf_counter()
    smoke = limit_days is not None
    if smoke:
        if int(limit_days) < 1:
            raise ValueError("limit_days must be >= 1")
        if int(limit_days) >= len(k1_days()):
            raise ValueError(f"a smoke covers fewer than all {len(k1_days())} K1 days (limit_days={limit_days}); "
                             "the full period is only ever run as a logged attempt (limit_days=None)")
    fr_csv, published_csv = Path(fr_csv), Path(published_csv)
    lear_start = sha256_file(LEAR_FILE)
    fr_sha, pub_sha = sha256_file(fr_csv), sha256_file(published_csv)
    res: dict = {
        "gate": "K1", "smoke": SMOKE if smoke else False, "limit_days": limit_days,
        "lear_file": "solarbench/lear.py", "lear_sha256": lear_start,
        "lear_sha256_at_import": LEAR_SHA256_AT_IMPORT, "lear_sha256_at_start": lear_start,
        "lear_sha256_at_end": None,
        "fr_csv_sha256": fr_sha, "fr_csv_sha256_expected": EPF_FR_SHA256, "fr_csv_pinned": fr_sha == EPF_FR_SHA256,
        "published_sha256": pub_sha, "published_sha256_expected": PUBLISHED_SHA256,
        "published_pinned": pub_sha == PUBLISHED_SHA256,
        "test_period": list(K1["test_period"]), "windows": list(K1_WINDOWS), "processes": processes,
        "published_mae_spec": dict(K1["published_mae"]),
        "tolerance": {"ensemble_deviation": list(K1_ENSEMBLE_BAND), "window_deviation": list(K1_WINDOW_BAND),
                      "mean_abs_diff_ensemble_max": K1_MAX_MEAN_ABS_DIFF, "published_mae_decimals": K1_DECIMALS},
    }
    pub = read_published(published_csv)
    res["published_check"] = published_check(pub, k1_hours(k1_days()))
    stop = []
    if False:
        stop.append("solarbench/lear.py changed after it was imported: the code that would run is not the file")
    if not res["published_check"]["match"]:
        stop.append(res["published_check"]["reason"])
    if not smoke and not res["fr_csv_pinned"]:
        stop.append("FR.csv is not the file the avail run recorded (AVAIL.epf_fr_sha256)")
    if not smoke and not res["published_pinned"]:
        stop.append("the published forecasts are not the pinned CSV (gates.K1.reference)")
    if stop:
        return _k1_stop(res, stop, started)
    days = k1_days(limit_days)
    mats = read_epf_fr(fr_csv)
    parts, logs = k1_forecasts(mats, days, processes=processes)
    res["lear_sha256_at_end"] = sha256_file(LEAR_FILE)
    res.update(days=len(days), first_day=str(days[0]), last_day=str(days[-1]), logs=logs)
    if res["lear_sha256_at_end"] != lear_start:
        return _k1_stop(res, ["solarbench/lear.py changed while K1 ran: the forecasts may not come from the "
                              "recorded file"], started)
    clean = {c: parts[c].reindex(index=list(days), columns=range(24)).to_numpy(dtype="float64").reshape(-1)
             for c in k1_names()}
    if smoke:  # never k1_verdict: no MAE, deviation or difference on a subset of the K1 hours
        res.update(hours=24 * len(days), **k1_coverage(clean), mae=None, reference_mae=None, deviation=None,
                   mean_abs_diff_ensemble=None, checks=None, fr_price_vs_real_price_max_abs_diff=None,
                   status=SMOKE, counts_as_attempt=False)
        res["pass"] = False
    else:
        sub = pub.reindex(k1_hours(days))
        fr_price = mats["price"].reindex(list(days)).to_numpy(dtype="float64").reshape(-1)
        res.update(k1_verdict(clean, sub))
        res["fr_price_vs_real_price_max_abs_diff"] = (
            float(np.nanmax(np.abs(fr_price - sub[K1_REAL].to_numpy()))) if np.isfinite(fr_price).any() else None)
        res.update(status="pass" if res["pass"] else "fail", counts_as_attempt=True)
    res["run_seconds"] = round(time.perf_counter() - started, 3)
    return res


# ------------------------------------------------------------------------------------ K2

#: gates.K2 (b): "within 0.01 EUR/MWh of the reference on every scored hour and quantile".
K2_TOLERANCE = 0.01
#: gates.K2.what: the arms, each with its window kind. t0_cal_strict runs on the strict windows
#: (strict_arm.rule); t0_cal_wx only at the origins on or after AVAIL.p4_first_day.
K2_ARMS = ("t0", "t0_cal", "t0_cal_strict", "t0_cal_wx")
K2_STRICT_ARM = ps.PRICE_SPEC["strict_arm"]["name"]
#: The arms K2 must check for a pass; t0_cal_wx is checked whenever it is given (it exists only with weather).
K2_REQUIRED = ("t0", "t0_cal", "t0_cal_strict")


def k2_days() -> list[date]:
    """gates.K2.what: 'each TEST_ORIGINS day' (each date taken as the delivery day D)."""
    return [date.fromisoformat(d) for d in ps.TEST_ORIGINS]


def k2_windows(series: pd.Series | None) -> dict[str, list[px.PriceWindow]]:
    """K2's windows per arm: the publication-rule windows of every TEST_ORIGINS day, the strict ones for
    t0_cal_strict, and for t0_cal_wx only the days on or after AVAIL.p4_first_day. A day is never left out
    for an incomplete target (require_target=False): K2 compares forecasts, it scores nothing."""
    days = k2_days()
    ws = px.build_price_windows(series, days, require_target=False)
    wss = px.build_price_windows(series, days, strict=True, require_target=False)
    p4 = date.fromisoformat(ps.AVAIL["p4_first_day"])
    return {"t0": ws, "t0_cal": ws, K2_STRICT_ARM: wss, "t0_cal_wx": [w for w in ws if w.delivery_date >= p4]}


def k2_horizon(w: px.PriceWindow) -> int:
    """The arm's fixed horizon, from the spec and the window kind (never from the arm):
    t0.fixed_horizon_hours (25), or strict_arm.rule's 'fixed 36-hour horizon' for a strict window."""
    return px.STRICT_HORIZON if getattr(w, "strict", False) else px.HORIZON


def _window_key(w: px.PriceWindow) -> tuple:
    return (w.delivery_date, w.origin, w.decision, bool(w.strict), tuple(pd.DatetimeIndex(w.targets).asi8))


def context_end(w: px.PriceWindow) -> pd.Timestamp:
    """The context end the spec names, re-derived from the day: the cutoff [D-1 23:00, D 00:00) Paris,
    or for a strict window the 12:00 D-1 stamp (strict_arm.rule)."""
    d = w.delivery_date
    return px.decision_time(d) if getattr(w, "strict", False) else px.day_hours(d)[0] - HOUR


def k2_reference(arm, model, series: pd.Series, w: px.PriceWindow) -> tuple[np.ndarray, np.ndarray]:
    """The independent reference of one window: never calls the arm's predict, context or block.

    The 2160 hourly prices ending at the context end as float32, the covariate block over context + horizon
    from each covariate's values(), one model.predict on that single row with the arm's fixed horizon from
    the spec (``k2_horizon``, never ``arm.horizon``) and the five levels, and D's real hours picked from the
    horizon by UTC time. Only ``arm.covariates`` is read from the arm.
    """
    import torch

    end = context_end(w)
    n_ctx, horizon = px.CONTEXT_HOURS, k2_horizon(w)
    ctx_times = pd.date_range(end=end, periods=n_ctx, freq="1h")
    ctx = series.reindex(ctx_times).to_numpy(dtype="float32")
    kwargs: dict = {"horizon": horizon, "quantiles": list(px.LEVELS)}
    if arm.covariates:
        times = pd.date_range(ctx_times[0], periods=n_ctx + horizon, freq="1h")
        block = np.stack([np.asarray(c.values(times), dtype="float64") for c in arm.covariates]).astype("float32")
        kwargs["future_covariates"] = torch.from_numpy(block[None])
    out = model.predict(torch.from_numpy(ctx[None]), **kwargs)
    median = out.median.detach().cpu().numpy().astype("float64")[0]
    quant = out.quantiles.detach().cpu().numpy().astype("float64")[0]
    steps = pd.date_range(end + HOUR, periods=horizon, freq="1h")
    pos = steps.get_indexer(px.day_hours(w.delivery_date))
    if (pos < 0).any():
        raise ValueError(f"{w.delivery_date}: D's hours are not all inside the {horizon}-hour horizon")
    return median[pos], quant[pos, :]


def _bits_equal(a, b) -> bool:
    a = np.ascontiguousarray(np.asarray(a, dtype="float64"))
    b = np.ascontiguousarray(np.asarray(b, dtype="float64"))
    return a.shape == b.shape and bool(np.isfinite(a).all()) and a.tobytes() == b.tobytes()


def _fresh(arm, model):
    """A copy of the arm on ``model`` with its own missing record (the caller's arm is never touched)."""
    a = copy.copy(arm)
    a.missing = {"context": [], "sanitised": []}
    return a.use_model(model)


def _k2_arm(arm, model, series: pd.Series, windows: list, expected: list) -> dict:
    """One arm's K2. ``expected``: the arm's k2_windows; the arm fails unless ``windows`` are exactly those
    (the TEST_ORIGINS day set, each window of the arm's kind) and its horizon is the spec's fixed one."""
    strict = arm.name == K2_STRICT_ARM
    want_h = px.STRICT_HORIZON if strict else px.HORIZON
    kinds_ok = all(bool(getattr(w, "strict", False)) == strict for w in windows)
    days_ok = [w.delivery_date for w in windows] == [w.delivery_date for w in expected]
    res: dict = {"days": [str(w.delivery_date) for w in windows],
                 "expected_days": [str(w.delivery_date) for w in expected],
                 "window_kind": "strict" if strict else "cutoff", "window_kind_ok": kinds_ok,
                 "windows_ok": bool(kinds_ok and days_ok and [_window_key(w) for w in windows]
                                    == [_window_key(w) for w in expected]),
                 "horizon": int(arm.horizon), "horizon_expected": want_h, "horizon_ok": int(arm.horizon) == want_h,
                 "covariates": [getattr(c, "name", type(c).__name__) for c in arm.covariates],
                 "single": {}, "single_pass": False, "batch_max_abs_diff": None, "batch_pass": False,
                 "pass": False}
    if not windows:
        res["error"] = "no windows"
        return res
    try:
        refs = [k2_reference(arm, model, series, w) for w in windows]
        single = _fresh(arm, model)
        for w, (m, q) in zip(windows, refs):
            p = single.predict(series, [w])[0]
            res["single"][str(w.delivery_date)] = (p.quantiles is not None and tuple(p.quantile_levels) == px.LEVELS
                                                   and _bits_equal(p.values, m) and _bits_equal(p.quantiles, q))
        batch = _fresh(arm, model)
        batch.batch_size = max(int(batch.batch_size), len(windows))  # "in one batch"
        preds = batch.predict(series, windows)
        diffs = []
        for p, (m, q) in zip(preds, refs):
            d_med = np.abs(np.asarray(p.values, dtype="float64") - m)
            d_q = np.abs(np.asarray(p.quantiles, dtype="float64") - q)
            diffs.append(float(max(d_med.max(), d_q.max())) if np.isfinite(d_med).all() and np.isfinite(d_q).all()
                         else float("nan"))
        worst = float(np.max(diffs)) if len(diffs) == len(windows) else float("nan")
        res["batch_max_abs_diff"] = worst
        res["single_pass"] = all(res["single"].values())
        res["batch_pass"] = bool(np.isfinite(worst) and worst <= K2_TOLERANCE)
        res["pass"] = bool(res["single_pass"] and res["batch_pass"] and res["windows_ok"] and res["horizon_ok"])
        res["missing"] = {"single": single.missing, "batch": batch.missing}
    except Exception as exc:  # a broken adapter fails K2; it never crashes the gate
        res["error"] = f"{type(exc).__name__}: {exc}"[:400]
    return res


def run_k2(arms: Sequence, model, series: pd.Series, windows: Mapping | None = None) -> dict:
    """K2 (gates.K2) for each arm on its k2_windows (every TEST_ORIGINS day; strict windows for t0_cal_strict;
    t0_cal_wx from AVAIL.p4_first_day): (a) its predict on each window alone equals the reference bit for bit
    (median and all five quantiles); (b) its predict on all its windows in one batch is within 0.01 of it.
    Each arm also needs the spec's fixed horizon. K2 passes only if t0, t0_cal and t0_cal_strict (and
    t0_cal_wx when given) all pass.

    ``windows`` (tests only): a mapping arm name -> windows used instead of k2_windows for that arm. They are
    checked against k2_windows, so an arm given any other day set or window kind fails: a K2 pass is only
    ever a pass on the TEST_ORIGINS windows.
    """
    names = [a.name for a in arms]
    if len(set(names)) != len(names):
        raise ValueError(f"K2: duplicate arm names {names}")
    expected = k2_windows(series)
    out: dict = {"gate": "K2", "tolerance": K2_TOLERANCE, "days": [str(d) for d in k2_days()],
                 "p4_first_day": ps.AVAIL["p4_first_day"], "arms": {},
                 "arms_missing": [n for n in K2_REQUIRED if n not in names],
                 "windows_given": sorted(windows) if windows is not None else []}
    for arm in arms:
        if arm.name not in expected:
            out["arms"][arm.name] = {"pass": False, "error": f"not a K2 arm (gates.K2: {list(K2_ARMS)})"}
            continue
        ws = list(windows[arm.name]) if windows is not None and arm.name in windows else list(expected[arm.name])
        out["arms"][arm.name] = _k2_arm(arm, model, series, ws, list(expected[arm.name]))
    out["pass"] = (not out["arms_missing"] and bool(out["arms"])
                   and all(a["pass"] for a in out["arms"].values()))
    return out


# ------------------------------------------------------------------------------------ K3

K3_RULES = K3["rules"]
CONVENTIONS = ("instant", "mean_preceding_hour")
K3_ARMS = {"planted": "k3_oracle_planted", "decoy": "k3_oracle_decoy",
           "shift_m1h": "k3_oracle_shift_m1h", "shift_p1h": "k3_oracle_shift_p1h"}
K3_BASE = "t0_cal"
#: The oracle issue bound, as engine.covs.weather_provider sets it: after every origin that uses the cell.
ORACLE_ISSUE_LAG = pd.Timedelta(days=5)
PORT_OFFSET_MIN = 30  # the price hour stamped h is centred on h + 30 min (weather_p4.constructions)


def k3_days() -> list[date]:
    return px.days_between(*K3["period"])


def k3_grid(windows: Sequence[px.PriceWindow], *, context_hours: int = px.CONTEXT_HOURS,
            horizon: int = px.HORIZON) -> pd.DatetimeIndex:
    """The readings' hourly UTC grid: the first context hour of the first window to 2 h after the last
    horizon hour of the last."""
    first = min(w.origin for w in windows) - (context_hours - 1) * HOUR
    last = max(w.origin for w in windows) + horizon * HOUR + 2 * HOUR
    return pd.date_range(first, last, freq="1h")


def k3_scale(series: pd.Series, days: Sequence[date]) -> dict:
    """p99 (metrics.peak_proxy, 0.99) and the pandas sample sd of the prices over the real hours of the
    K3 days (NaN dropped)."""
    hours = pd.DatetimeIndex([t for d in days for t in px.day_hours(d)])
    p = series.reindex(hours).dropna().astype("float64")
    return {"p99": metrics.peak_proxy(p.to_numpy(), 0.99), "sd": float(p.std()), "scale_hours": int(len(p))}


def planted_readings(series: pd.Series, stamps: pd.DatetimeIndex, convention: str, noise: np.ndarray) -> pd.Series:
    """gates.K3.planted, p(h) = the price of the hour starting h, e = ``noise`` (one value per stamp):
    mean_preceding_hour - the reading stamped h + 1 h is p(h) + e(h + 1 h), i.e. stamp s holds p(s - 1 h) + e(s);
    instant - the reading stamped h is (p(h - 1 h) + p(h)) / 2 + e(h). A missing p makes the reading missing."""
    prev = series.reindex(stamps - HOUR).to_numpy(dtype="float64")
    noise = np.asarray(noise, dtype="float64")
    if convention == "mean_preceding_hour":
        values = prev + noise
    elif convention == "instant":
        values = (prev + series.reindex(stamps).to_numpy(dtype="float64")) / 2.0 + noise
    else:
        raise ValueError(f"unknown convention {convention!r}")
    return pd.Series(values, index=stamps)


def shifted(readings: pd.Series, hours: int) -> pd.Series:
    """The readings moved by ``hours`` on their own grid: +1 puts the reading stamped s - 1 h at s."""
    return pd.Series(readings.reindex(readings.index - hours * HOUR).to_numpy(), index=readings.index)


def port(readings: pd.Series, grid: pd.DatetimeIndex, convention: str) -> tuple[np.ndarray, pd.DatetimeIndex]:
    """The convention's P4 port onto the hourly price grid (values, latest reading used)."""
    readings = readings.sort_index()
    if convention == "mean_preceding_hour":
        return cov.hourly_to_slots(readings, grid, PORT_OFFSET_MIN)
    if convention == "instant":
        return covs.instant_to_slots(readings, grid, PORT_OFFSET_MIN)
    raise ValueError(f"unknown convention {convention!r}")


def oracle_covariate(name: str, readings: pd.Series, grid: pd.DatetimeIndex, convention: str) -> cov.SeriesCovariate:
    values, latest = port(readings, grid, convention)
    return cov.SeriesCovariate(name=name, series=pd.Series(values, index=grid),
                               issued=pd.Series(latest + ORACLE_ISSUE_LAG, index=grid), oracle=True,
                               description={"gate": "K3", "convention": convention,
                                            "port": "hourly_to_slots" if convention == "mean_preceding_hour"
                                            else "instant_to_slots", "stamp_offset_min": PORT_OFFSET_MIN})


def k3_covariates(series: pd.Series, windows: Sequence[px.PriceWindow], days: Sequence[date],
                  convention: str) -> dict:
    """The four oracle covariates of one convention: default_rng(seed) fresh, e drawn first, then the decoy,
    one value per hourly stamp; the shifts move the planted readings before the port; the decoy is not shifted."""
    stamps = k3_grid(windows)
    scale = k3_scale(series, days)
    noise_sd = K3_RULES["noise_sd_share_of_p99"] * scale["p99"]
    rng = np.random.default_rng(K3_RULES["seed"])
    e = rng.normal(0.0, noise_sd, len(stamps))
    decoy = rng.normal(0.0, scale["sd"], len(stamps))
    planted = planted_readings(series, stamps, convention, e)
    readings = {"planted": planted, "decoy": pd.Series(decoy, index=stamps),
                "shift_m1h": shifted(planted, -1), "shift_p1h": shifted(planted, 1)}
    covariates = {k: oracle_covariate(f"k3_{k}", r, stamps, convention) for k, r in readings.items()}
    return {"stamps": stamps, "noise": e, "noise_sd": noise_sd, "readings": readings, "covariates": covariates,
            **scale}


def k3_arms(model, covariates: Mapping[str, cov.SeriesCovariate]) -> list:
    """Base t0_cal and the four oracle arms, each t0_cal plus exactly one oracle covariate."""
    base = px.PriceT0Forecaster(K3_BASE, covariates=(px.holiday(),)).use_model(model)
    return [base] + [px.PriceT0Forecaster(K3_ARMS[k], covariates=(px.holiday(), covariates[k])).use_model(model)
                     for k in K3_ARMS]


def _ratio(a: float, b: float) -> float:
    return a / b if b > 0 else float("nan")


def k3_checks(mae: Mapping[str, float], *, no_sanitised: bool) -> tuple[dict, dict]:
    """The ratios and the ka/2 rules of gates.K3 from the pooled MAEs (empty: no common day, every rule fails)."""
    if mae:
        base, planted = mae[K3_BASE], mae[K3_ARMS["planted"]]
        ratios = {"planted_ratio": _ratio(planted, base), "decoy_ratio": _ratio(mae[K3_ARMS["decoy"]], base),
                  "shift_penalty": _ratio(min(mae[K3_ARMS["shift_m1h"]], mae[K3_ARMS["shift_p1h"]]), planted)}
    else:
        ratios = {"planted_ratio": float("nan"), "decoy_ratio": float("nan"), "shift_penalty": float("nan")}
    r = K3_RULES
    checks = {"planted_helps": bool(ratios["planted_ratio"] <= r["planted_ratio_max"]),
              "decoy_does_not_help": bool(ratios["decoy_ratio"] >= r["decoy_ratio_min"]),
              "decoy_does_not_break": bool(ratios["decoy_ratio"] <= r["decoy_ratio_max"]),
              "aligned": bool(ratios["shift_penalty"] >= r["shift_penalty_min"])}
    if r["no_sanitised_output"]:
        checks["no_sanitised_output"] = bool(no_sanitised)
    return ratios, checks


def pooled_mae(df: pd.DataFrame, names: Sequence[str]) -> tuple[dict[str, float], list, list]:
    """MAE of each arm over every scored hour of the days all ``names`` scored (finite at every hour)."""
    finite = np.isfinite(df["y_hat"].to_numpy(dtype="float64")) & np.isfinite(df["y"].to_numpy(dtype="float64"))
    ok = (df.assign(ok=finite).groupby(["delivery_date", "method"])["ok"].all()
          .unstack("method").reindex(columns=list(names))).eq(True)  # an arm without the day: not scored
    common = sorted(ok.index[ok.all(axis=1)])
    dropped = sorted(set(ok.index) - set(common))
    if not common:
        return {}, common, dropped
    sub = df[df["delivery_date"].isin(common)]
    mae = {}
    for n in names:
        rows = sub[sub["method"] == n]
        mae[n] = float(np.abs(rows["y"].to_numpy(dtype="float64") - rows["y_hat"].to_numpy(dtype="float64")).mean())
    return mae, common, dropped


def _k3_convention(series: pd.Series, model, windows: list, days: list, convention: str, cache) -> dict:
    built = k3_covariates(series, windows, days, convention)
    arms = k3_arms(model, built["covariates"])
    names = [a.name for a in arms]
    watcher = _NonFiniteWatcher()
    t0_log = logging.getLogger("t0.model.model")
    t0_log.addHandler(watcher)
    try:
        df = px.run_price_backtest(series, arms, windows, oracle_methods=frozenset(names[1:]))
    finally:
        t0_log.removeHandler(watcher)
    mae, common, dropped = pooled_mae(df, names)
    sanitised = {a.name: list(a.missing["sanitised"]) for a in arms}
    # gates.K3.pass "t0 replaced no non-finite output in any K3 arm" (engine known_answer: watcher.count == 0):
    # every replacement warning counts, also one in a batch whose single-row re-runs came out clean.
    ratios, checks = k3_checks(mae, no_sanitised=watcher.count == 0 and not any(sanitised.values()))
    stamps = built["stamps"]
    res = {"convention": convention, "pass": all(checks.values()), "checks": checks, **ratios, "mae": mae,
           "arms": names, "days_scored": len(common), "days_dropped": [str(d) for d in dropped],
           "p99": built["p99"], "sd": built["sd"], "noise_sd": built["noise_sd"], "scale_hours": built["scale_hours"],
           "grid": {"first": str(stamps[0]), "last": str(stamps[-1]), "stamps": int(len(stamps))},
           "port": built["covariates"]["planted"].description["port"],
           "missing": {a.name: a.missing for a in arms}, "non_finite_warnings": watcher.count}
    if not common:
        res["error"] = "no day on which all five arms scored"
    if cache is not None:
        out = Path(cache)
        out.mkdir(parents=True, exist_ok=True)
        frame_path, readings_path = out / f"k3_{convention}.csv", out / f"k3_{convention}_readings.csv"
        df.to_csv(frame_path, index=False)
        pd.DataFrame(built["readings"]).rename_axis("stamp").to_csv(readings_path)
        res["files"] = [str(frame_path), str(readings_path)]
    return res


SMOKE_K3 = "smoke: not a K3 result"


def run_k3(series: pd.Series, model, *, days: Sequence[date] | None = None, cache=None) -> dict:
    """K3 (gates.K3): one run per convention on the t0_cal price windows of the K3 days; passes only if both
    conventions meet every rule and t0 replaced no non-finite output. ``cache``: an optional directory for each
    convention's tidy frame and readings.

    ``days`` other than exactly gates.K3.period's days make a smoke: ``pass`` is then False everywhere (the
    top level and each convention) and ``smoke_outcome`` says what the rules gave on those days only.
    """
    days = list(days) if days is not None else k3_days()
    full = days == k3_days()
    report = px.WindowReport()
    windows = px.build_price_windows(series, days, report=report)
    out: dict = {"gate": "K3", "smoke": False if full else SMOKE_K3, "period": [str(days[0]), str(days[-1])]
                 if days else [], "period_spec": list(K3["period"]), "days": len(days),
                 "windows": report.as_dict(), "rules": dict(K3_RULES), "conventions": {}, "pass": False}
    if not windows:
        out["error"] = "no K3 window"
    else:
        for convention in CONVENTIONS:
            out["conventions"][convention] = _k3_convention(series, model, windows, days, convention, cache)
        out["pass"] = all(c["pass"] for c in out["conventions"].values())
    if not full:  # gates.K3.period: a subset of the K3 days is never a K3 pass
        for c in out["conventions"].values():
            c.update(smoke_outcome="pass" if c["pass"] else "fail", **{"pass": False})
        out.update(smoke_outcome="pass" if out["pass"] else "fail", **{"pass": False})
    return out
