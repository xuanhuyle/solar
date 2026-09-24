#!/usr/bin/env python3
"""The covariate slice: does t0 forecast French solar better with known-future covariates?

Three steps, run in this order (on GitHub Actions: the data and the gated
weights are not reachable from everywhere):

    python run_covariates.py probe          # coverage and semantics of the inputs; no forecasts
    python run_covariates.py known-answer   # real t0 on 2023: does it use a planted covariate, aligned?
    python run_covariates.py run            # the 2024 comparison, with the probe's constants frozen

Everything reads data up to 2024-12-31 only; 2025 onwards is sealed for a later,
independent confirmation.  Results go to ``results/covariates/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from solarbench import covariates as cov
from solarbench import metrics, weather
from solarbench.backtest import BacktestReport, build_windows, run_backtest
from solarbench.data import STEP, STEPS_PER_DAY, load_or_fetch
from solarbench.forecasters import (
    T0_REPO_ID,
    T0Forecaster,
    WeatherSlotRatio,
    night_zero_variant,
    statistical_baselines,
)

log = logging.getLogger("run_covariates")

ROOT = Path(__file__).resolve().parent
#: The Experiment 0 data window, so the cached ODRÉ download is reused as is.
DATA_START, DATA_END = "2022-01-01", "2025-01-01"
TEST_START, TEST_END = date(2024, 1, 1), date(2024, 12, 31)
#: Weather is fetched from here: the 90-day context of the first 2024 origin.
WX_FETCH_START, WX_FETCH_END = "2023-09-30", "2024-12-31"
#: Known-answer check: 64 delivery days of 2023, before the test year.
KA_START, KA_END = date(2023, 5, 1), date(2023, 7, 3)
#: Days on which the meaning of ``previous_day2`` is checked against single runs.
SEMANTICS_DAYS = ("2024-04-10", "2024-05-20", "2024-07-01", "2024-08-12", "2024-09-23")
SEMANTICS_REGION = "Occitanie"
#: Probe rules, fixed before the probe ran.
MIN_SCORABLE_DAYS = 200
MIN_SCORABLE_DAYS_UNDERPOWERED = 120
RELAXED_CONTEXT_DAYS = 28

# ----------------------------------------------------------- frozen analysis

#: Every comparison reported, fixed before the known-answer and full runs.
#: ``(model, reference, role)``; one-sided question "does model beat reference?".
PRIMARY = ("t0_wx_night_zero", "t0_night_zero", "primary")
SECONDARY = [
    ("t0_wx_night_zero", "wx_ratio", "secondary"),
    ("t0_wx_night_zero", "ewma", "secondary"),
    ("t0_geo_night_zero", "t0_night_zero", "secondary"),
    ("t0_wx_night_zero", "t0_geo_night_zero", "secondary"),
]
DIAGNOSTIC = [("t0_wx_oracle_night_zero", "t0_wx_night_zero", "diagnostic")]
COMPARISONS = [PRIMARY, *SECONDARY, *DIAGNOSTIC]
ALPHA = 0.05
ORACLE_METHODS = frozenset({"t0_wx_oracle", "t0_wx_oracle_night_zero"})

LABELS = {
    "t0": "t0 (no covariates)",
    "t0_night_zero": "t0, night zero",
    "t0_geo": "t0 + geometry",
    "t0_geo_night_zero": "t0 + geometry, night zero",
    "t0_wx": "t0 + geometry + weather forecast",
    "t0_wx_night_zero": "t0 + geometry + weather forecast, night zero",
    "t0_wx_oracle": "t0 + geometry + ERA5 (reference, not point-in-time)",
    "t0_wx_oracle_night_zero": "t0 + geometry + ERA5, night zero (reference)",
    "wx_ratio": "Weather forecast x same-slot ratio (no t0)",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["probe", "known-answer", "run"])
    p.add_argument("--cache-dir", type=Path, default=ROOT / "data")
    p.add_argument("--wx-cache", type=Path, default=ROOT / "wxcache")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "covariates")
    p.add_argument("--repo-id", default=T0_REPO_ID)
    p.add_argument("--revision", default=None)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--context-days", type=int, default=90)
    p.add_argument("--gate-hour", type=int, default=12)
    p.add_argument("--limit-days", type=int, default=None, help="score only the first N eligible days")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args(argv)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _grid() -> pd.DatetimeIndex:
    """The slot grid the weather covariates are materialised on."""
    return pd.date_range(WX_FETCH_START, "2025-01-01", freq=STEP, tz="UTC", inclusive="left")


def _series(args) -> pd.Series:
    return load_or_fetch(start=DATA_START, end=DATA_END, cache_dir=args.cache_dir)


def _eligible(windows, providers, context_steps: int, *, relaxed: bool = False) -> tuple[list, list[dict]]:
    """Split windows by covariate coverage: horizon complete, context >= 98% valid.

    ``relaxed`` checks the context rule over the last 28 days only.
    """
    keep, dropped = [], []
    for w in windows:
        steps = RELAXED_CONTEXT_DAYS * STEPS_PER_DAY if relaxed else context_steps
        share, horizon_ok = cov.window_coverage(w.origin, providers, steps, cov.COV_HORIZON)
        if horizon_ok and share >= cov.MIN_CONTEXT_VALID:
            keep.append(w)
        else:
            dropped.append({"delivery_date": str(w.delivery_date), "context_valid": round(share, 4),
                            "horizon_complete": horizon_ok})
    return keep, dropped


# ------------------------------------------------------------------- probe


def measure_stamp_offset(series: pd.Series, weights: dict[str, float]) -> dict:
    """Where inside its half-hour does an eCO2mix stamp sit?  Measured on 2023.

    Per UTC day, the centre of mass in time of national output is compared
    with that of the geometry covariate evaluated at the stamps themselves.
    If a stamp marks the start of its half-hour the output's centre of mass
    reads about 15 minutes early, and so on.  The nearest of +15 / 0 / -15
    minutes is chosen.
    """
    y = series.loc["2023-01-01":"2023-12-31 23:30"]
    geo = cov.GeometryCovariate(weights, stamp_offset_min=0).values(y.index)
    frame = pd.DataFrame({"y": y.to_numpy(), "g": geo}, index=y.index)
    frame["minute"] = frame.index.hour * 60 + frame.index.minute
    rows = []
    for day, sub in frame.groupby(frame.index.date):
        if len(sub) != STEPS_PER_DAY or sub["y"].isna().any() or sub["y"].clip(lower=0).sum() <= 0:
            continue
        yy = sub["y"].clip(lower=0)
        rows.append((np.dot(sub["minute"], yy) / yy.sum()) - (np.dot(sub["minute"], sub["g"]) / sub["g"].sum()))
    delta = float(np.median(rows))
    implied = -delta
    chosen = min((15, 0, -15), key=lambda c: abs(implied - c))
    return {"days": len(rows), "median_com_difference_min": round(delta, 2),
            "implied_offset_min": round(implied, 2), "chosen": chosen}


def check_day2_semantics(model: str, day2: pd.Series, point: tuple[float, float], cache: Path) -> dict:
    """Does every checked ``previous_day2`` value equal a run started >= 48 h earlier?

    For a sample of valid hours, the archived day-2 value is matched against
    single runs started from D-3 00z to D-1 18z.  The value is point-in-time
    available at the N=2 bound if some run started at or before ``h - 48 h``
    produced it.  Hours with no matching run make the check unverifiable.
    """
    checked = ok = late = unmatched = 0
    lags: list[float] = []
    errors: list[str] = []
    for day in SEMANTICS_DAYS:
        d = pd.Timestamp(day, tz="UTC")
        runs = {}
        for k in range(12):
            init = d - pd.Timedelta(days=3) + pd.Timedelta(hours=6 * k)
            try:
                runs[init] = weather.fetch_single_run(model, cov.WX_VARIABLE, init, point, cache, forecast_hours=120)
            except Exception as exc:  # recorded, never fatal: unverifiable means N=3
                errors.append(f"{init:%Y-%m-%dT%H}: {str(exc)[:160]}")
            time.sleep(0.3)
        for h in pd.date_range(d + pd.Timedelta(hours=1), periods=24, freq="h"):
            v = day2.get(h, np.nan)
            if not np.isfinite(v) or v <= 20.0:
                continue
            checked += 1
            matches = [i for i, s in runs.items() if h in s.index and np.isfinite(s[h]) and abs(s[h] - v) <= 0.5]
            if not matches:
                unmatched += 1
            elif min(matches) <= h - pd.Timedelta(hours=48):
                ok += 1
                lags.append((h - max(m for m in matches if m <= h - pd.Timedelta(hours=48))) / pd.Timedelta(hours=1))
            else:
                late += 1
    verified = checked >= 20 and ok == checked
    return {"model": model, "hours_checked": checked, "hours_ok": ok, "hours_only_later_runs": late,
            "hours_unmatched": unmatched, "lead_hours_of_latest_ok_match": sorted(set(lags))[:20],
            "verified_n2": verified, "errors": errors[:20]}


def probe(args) -> int:
    out: dict = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "rules": {"min_scorable_days": MIN_SCORABLE_DAYS, "underpowered": MIN_SCORABLE_DAYS_UNDERPOWERED,
                           "min_context_valid": cov.MIN_CONTEXT_VALID, "horizon": cov.COV_HORIZON,
                           "p_max_h": cov.WX_P_MAX_H, "preference": list(weather.WX_MODEL_PREFERENCE)}}
    context_steps = args.context_days * STEPS_PER_DAY
    series = _series(args)

    weights, raw = weather.fetch_region_weights_2023(args.wx_cache)
    out["weights"] = {"weights": weights, **raw}
    log.info("2023 regional weights: %s", {k: round(v, 4) for k, v in weights.items()})

    out["stamp"] = measure_stamp_offset(series, weights)
    stamp = out["stamp"]["chosen"]
    log.info("stamp convention: %s", out["stamp"])

    grid = _grid()
    windows = build_windows(series, test_start=TEST_START, test_end=TEST_END,
                            gate_hour=args.gate_hour, context_steps=context_steps)
    geo = cov.GeometryCovariate(weights, stamp)
    out["windows_2024"] = len(windows)

    models: dict[str, dict] = {}
    chosen = None
    for model in weather.WX_MODEL_PREFERENCE:
        entry: dict = {}
        variables = [f"{cov.WX_VARIABLE}_previous_day2", f"{cov.WX_VARIABLE}_previous_day3"]
        try:
            frames = weather.fetch_previous_runs(model, variables, WX_FETCH_START, WX_FETCH_END, args.wx_cache)
        except Exception as exc:
            entry["error"] = str(exc)[:400]
            models[model] = entry
            log.warning("%s: %s", model, entry["error"])
            continue
        if model == weather.WX_MODEL_PREFERENCE[0]:
            point = cov.REGION_POINTS[SEMANTICS_REGION]
            out["semantics"] = check_day2_semantics(model, frames[variables[0]][SEMANTICS_REGION], point, args.wx_cache)
            log.info("previous_day2 semantics: %s", out["semantics"])
        verified = out.get("semantics", {}).get("verified_n2", False) and model == weather.WX_MODEL_PREFERENCE[0]
        lead = 2 if verified else 3
        frame = frames[f"{cov.WX_VARIABLE}_previous_day{lead}"]
        nonnull = frame.notna()
        entry.update({
            "lead_days": lead,
            "first_complete_hour": str(nonnull.all(axis=1).idxmax()) if nonnull.all(axis=1).any() else None,
            "share_nonnull_by_region": {k: round(float(v), 4) for k, v in nonnull.mean().items()},
        })
        hourly = cov.national_mean(frame, weights)
        wx = cov.weather_covariate(hourly, grid, lead_days=lead, stamp_offset_min=stamp)
        primary, _ = _eligible(windows, [geo, wx], context_steps)
        relaxed, _ = _eligible(windows, [geo, wx], context_steps, relaxed=True)
        entry.update({"scorable_days": len(primary), "scorable_days_relaxed": len(relaxed),
                      "first_scorable": str(primary[0].delivery_date) if primary else None,
                      "sha256": cov.series_sha256(wx.series, wx.issued)})
        models[model] = entry
        log.info("%s: %s", model, {k: v for k, v in entry.items() if k != "share_nonnull_by_region"})
        if len(primary) >= MIN_SCORABLE_DAYS:
            chosen = {"model": model, "lead_days": lead, "rule": "primary", "days": len(primary), "sha256": entry["sha256"]}
            break
    out["models"] = models
    if chosen is None:
        usable = [(m, e) for m, e in models.items() if "scorable_days" in e]
        relaxed_ok = [(m, e) for m, e in usable if e["scorable_days_relaxed"] >= MIN_SCORABLE_DAYS]
        if relaxed_ok:
            m, e = relaxed_ok[0]
            chosen = {"model": m, "lead_days": e["lead_days"], "rule": "relaxed_context", "days": e["scorable_days_relaxed"], "sha256": e["sha256"]}
        elif usable:
            m, e = max(usable, key=lambda me: me[1]["scorable_days"])
            if e["scorable_days"] >= MIN_SCORABLE_DAYS_UNDERPOWERED:
                chosen = {"model": m, "lead_days": e["lead_days"], "rule": "underpowered", "days": e["scorable_days"], "sha256": e["sha256"]}
    out["chosen"] = chosen

    try:
        era = weather.fetch_era5(cov.WX_VARIABLE, WX_FETCH_START, WX_FETCH_END, args.wx_cache)
        era_cov = cov.weather_covariate(cov.national_mean(era, weights), grid, lead_days=0,
                                        stamp_offset_min=stamp, name="era5", oracle=True)
        in_range = era_cov.series.loc[: "2024-12-31 23:30"]
        out["era5"] = {"share_nonnull": round(float(in_range.notna().mean()), 5),
                       "sha256": cov.series_sha256(era_cov.series, era_cov.issued)}
    except Exception as exc:
        out["era5"] = {"error": str(exc)[:400]}
    log.info("era5: %s", out["era5"])

    frozen = [
        f"REGION_WEIGHTS = {json.dumps({k: round(v, 6) for k, v in weights.items()}, ensure_ascii=False)}",
        f"STAMP_OFFSET_MIN = {stamp}",
        f"WX_MODEL = {json.dumps(chosen['model']) if chosen else None}",
        f"WX_LEAD_DAYS = {chosen['lead_days'] if chosen else None}",
        f"WX_SHA256 = {json.dumps(chosen['sha256']) if chosen else None}",
        f"ERA5_SHA256 = {json.dumps(out['era5'].get('sha256'))}",
    ]
    out["frozen_constants"] = frozen
    _write_json(args.results_dir / "probe.json", out)
    print("\n".join(["FROZEN CONSTANTS (paste into solarbench/covariates.py):", *frozen]))
    return 0


# ------------------------------------------------------------ known answer


def _t0(args, name: str, *, covariates=(), batch_size: int | None = None, model=None) -> T0Forecaster:
    return T0Forecaster(
        context_steps=args.context_days * STEPS_PER_DAY, repo_id=args.repo_id, revision=args.revision,
        batch_size=batch_size or args.batch_size, name=name, label=LABELS.get(name, name),
        fixed_horizon=cov.COV_HORIZON if covariates else None, covariates=tuple(covariates), _model=model,
    )


def _mae(series: pd.Series, windows, preds) -> float:
    err = [np.abs(series.loc[w.targets].to_numpy() - np.clip(p.values, 0, None)) for w, p in zip(windows, preds)]
    return float(np.nanmean(np.concatenate(err)))


def known_answer(args) -> int:
    """Real t0 on 2023 with a planted covariate: a noisy copy of the future target."""
    import logging as _logging

    from solarbench.forecasters import _NonFiniteWatcher

    watcher = _NonFiniteWatcher()
    _logging.getLogger("t0.model.model").addHandler(watcher)
    context_steps = args.context_days * STEPS_PER_DAY
    series = _series(args)
    windows = build_windows(series, test_start=KA_START, test_end=KA_END,
                            gate_hour=args.gate_hour, context_steps=context_steps)
    p99 = metrics.peak_proxy(series.loc["2023-01-01":"2023-12-31 23:30"].dropna())
    rng = np.random.default_rng(args.seed)
    planted = series + rng.normal(0.0, 0.05 * p99, len(series))
    decoy = pd.Series(rng.normal(0.0, float(series.std()), len(series)), index=series.index)

    base = _t0(args, "t0")
    model = base.load()

    def arm(name, x):
        return _t0(args, name, covariates=(cov.SeriesCovariate(name, x, oracle=True),), model=model)

    maes = {"t0": _mae(series, windows, base.predict(series, windows))}
    planted_arm = arm("planted", planted)
    planted_preds = planted_arm.predict(series, windows)
    maes["planted"] = _mae(series, windows, planted_preds)
    for s in (-2, -1, 1, 2):
        maes[f"planted_shift_{s:+d}"] = _mae(series, windows, arm(f"shift{s}", planted.shift(s)).predict(series, windows))
    maes["decoy"] = _mae(series, windows, arm("decoy", decoy).predict(series, windows))

    # (d) batch composition must not matter.
    few = windows[:8]
    single = _t0(args, "planted_b1", covariates=planted_arm.covariates, batch_size=1, model=model).predict(series, few)
    batch_diff = float(max(np.max(np.abs(a.values - b.values)) for a, b in zip(single, planted_preds[:8])))

    # (e) post-origin target values and covariate cells outside the window change nothing;
    #     a covariate cell inside the horizon does (the check can see a leak).
    one = _t0(args, "planted_b1", covariates=planted_arm.covariates, batch_size=1, model=model)
    leak = {"target_rewrite_identical": True, "outside_rewrite_identical": True, "inside_change_detected": True}
    for w in (windows[0], windows[len(windows) // 2], windows[-1]):
        clean = one.predict(series, [w])[0].values
        poisoned = series.copy()
        after = poisoned.index > w.origin
        poisoned.loc[after] = poisoned.loc[after] * -7.5 + 1234.5
        leak["target_rewrite_identical"] &= bool(np.array_equal(clean, one.predict(poisoned, [w])[0].values))
        times = cov.covariate_times(w.origin, context_steps, cov.COV_HORIZON)
        outside = planted.copy()
        outside.loc[~outside.index.isin(times)] = 1e6
        arm_out = _t0(args, "outside", covariates=(cov.SeriesCovariate("planted", outside, oracle=True),), batch_size=1, model=model)
        leak["outside_rewrite_identical"] &= bool(np.array_equal(clean, arm_out.predict(series, [w])[0].values))
        inside = planted.copy()
        inside.loc[times[context_steps:]] += 5000.0
        arm_in = _t0(args, "inside", covariates=(cov.SeriesCovariate("planted", inside, oracle=True),), batch_size=1, model=model)
        leak["inside_change_detected"] &= not bool(np.array_equal(clean, arm_in.predict(series, [w])[0].values))

    ratio = maes["planted"] / maes["t0"]
    shifts = {k: v for k, v in maes.items() if k.startswith("planted_shift")}
    sharp = min(maes["planted_shift_-1"], maes["planted_shift_+1"]) / maes["planted"]
    verdict = {
        "a_uses_covariate": ratio <= 0.5,
        "b_aligned": all(maes["planted"] < v for v in shifts.values()),
        "b_sharp_1_step_ge_20pct": sharp >= 1.2,
        "d_batch_invariant_le_1mw": batch_diff <= 1.0,
        "e_no_leak": leak["target_rewrite_identical"] and leak["outside_rewrite_identical"] and leak["inside_change_detected"],
        "f_no_sanitised_output": watcher.count == 0,
    }
    out = {
        "windows": len(windows), "first": str(windows[0].delivery_date), "last": str(windows[-1].delivery_date),
        "p99_mw": p99, "noise_sd_mw": 0.05 * p99, "mae_mw": {k: round(v, 2) for k, v in maes.items()},
        "ratio_planted_to_t0": round(ratio, 4), "ratio_1step_shift_to_planted": round(sharp, 4),
        "batch_max_abs_diff_mw": batch_diff, "leak_checks": leak, "sanitised_warnings": watcher.count,
        "verdict": verdict, "passed": all(verdict.values()),
    }
    _write_json(args.results_dir / "known_answer.json", out)
    print(json.dumps(out, indent=2, default=str))
    return 0


# --------------------------------------------------------------------- run


def _require_frozen() -> None:
    missing = [n for n in ("REGION_WEIGHTS", "STAMP_OFFSET_MIN", "WX_MODEL", "WX_LEAD_DAYS", "WX_SHA256")
               if getattr(cov, n) is None]
    if missing:
        raise SystemExit(f"constants not frozen yet: {missing}. Run the probe and freeze them in solarbench/covariates.py")


def build_covariates(args) -> tuple[cov.GeometryCovariate, cov.SeriesCovariate, cov.SeriesCovariate | None]:
    """The frozen covariates, re-derived from the cached raw data and checked against the probe."""
    grid = _grid()
    var = f"{cov.WX_VARIABLE}_previous_day{cov.WX_LEAD_DAYS}"
    frame = weather.fetch_previous_runs(cov.WX_MODEL, [var], WX_FETCH_START, WX_FETCH_END, args.wx_cache)[var]
    wx = cov.weather_covariate(
        cov.national_mean(frame, cov.REGION_WEIGHTS), grid, lead_days=cov.WX_LEAD_DAYS,
        stamp_offset_min=cov.STAMP_OFFSET_MIN, name="weather",
        description={"model": cov.WX_MODEL, "variable": var, "p_max_h": cov.WX_P_MAX_H},
    )
    if cov.series_sha256(wx.series, wx.issued) != cov.WX_SHA256:
        raise SystemExit("the weather covariate differs from the one frozen at the probe - refusing to run")
    era = None
    if cov.ERA5_SHA256:
        frame = weather.fetch_era5(cov.WX_VARIABLE, WX_FETCH_START, WX_FETCH_END, args.wx_cache)
        era = cov.weather_covariate(
            cov.national_mean(frame, cov.REGION_WEIGHTS), grid, lead_days=0, stamp_offset_min=cov.STAMP_OFFSET_MIN,
            name="era5", oracle=True, description={"source": "ERA5 reanalysis via Open-Meteo archive"},
        )
        if cov.series_sha256(era.series, era.issued) != cov.ERA5_SHA256:
            raise SystemExit("the ERA5 covariate differs from the one frozen at the probe - refusing to run")
    return cov.GeometryCovariate(cov.REGION_WEIGHTS, cov.STAMP_OFFSET_MIN), wx, era


def one_sided_p(per_day: pd.DataFrame, model: str, reference: str, seed: int) -> float:
    """Block-bootstrap p-value for "model does not beat reference" (skill <= 0)."""
    draws = metrics.bootstrap_skill(per_day, model=model, reference=reference, seed=seed, return_draws=True)["draws"]
    return float((1 + np.sum(draws <= 0.0)) / (1 + len(draws)))


def holm(pvalues: list[float]) -> list[float]:
    order = np.argsort(pvalues)
    m = len(pvalues)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def run(args) -> int:
    _require_frozen()
    started = time.time()
    context_steps = args.context_days * STEPS_PER_DAY
    series = _series(args)
    geo, wx, era = build_covariates(args)
    providers = [geo, wx] + ([era] if era is not None else [])

    report = BacktestReport()
    windows = build_windows(series, test_start=TEST_START, test_end=TEST_END, gate_hour=args.gate_hour,
                            context_steps=context_steps, report=report)
    eligible, dropped = _eligible(windows, providers, context_steps)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [{"delivery_date": str(w.delivery_date), "scored": True} for w in eligible]
        + [dict(d, scored=False) for d in dropped]
    ).sort_values("delivery_date").to_csv(args.results_dir / "scored_days.csv", index=False)
    if args.limit_days:
        eligible = eligible[: args.limit_days]
    log.info("%d of %d windows have complete covariates; scoring %d", len(eligible) + 0, len(windows), len(eligible))

    base = _t0(args, "t0")
    model = base.load()
    forecasters = [
        base, night_zero_variant("t0", label=LABELS["t0_night_zero"]),
        _t0(args, "t0_geo", covariates=(geo,), model=model),
        night_zero_variant("t0_geo", label=LABELS["t0_geo_night_zero"]),
        _t0(args, "t0_wx", covariates=(geo, wx), model=model),
        night_zero_variant("t0_wx", label=LABELS["t0_wx_night_zero"]),
    ]
    oracle = frozenset()
    if era is not None:
        forecasters += [_t0(args, "t0_wx_oracle", covariates=(geo, era), model=model),
                        night_zero_variant("t0_wx_oracle", label=LABELS["t0_wx_oracle_night_zero"])]
        oracle = ORACLE_METHODS
    forecasters += [WeatherSlotRatio(wx), *statistical_baselines()]
    labels = {f.name: getattr(f, "label", f.name) for f in forecasters} | LABELS

    df = run_backtest(series, forecasters, eligible, report=report, oracle_methods=oracle)
    df.to_parquet(args.results_dir / "forecasts.parquet")

    peak = metrics.peak_proxy(df.loc[df["method"] == "t0", "y"])
    slots = metrics.daytime_slots(df)
    df = metrics.add_daytime_flag(df, slots)
    overall = metrics.summarise(df, peak=peak)
    daytime = metrics.summarise(df.loc[df["is_daytime"]], peak=peak)
    per_day = metrics.per_day_errors(df)
    per_day_daytime = metrics.per_day_errors(df.loc[df["is_daytime"]])
    per_day_by_slice = {"all_hours": per_day, "daytime_only": per_day_daytime}
    pd.concat([overall.assign(slice="all_hours"), daytime.assign(slice="daytime_only")]).to_csv(
        args.results_dir / "metrics.csv", index=False)
    per_day.to_csv(args.results_dir / "per_day_errors.csv", index=False)

    present = set(df["method"])
    pairs = [c for c in COMPARISONS if c[0] in present and c[1] in present]
    pairwise = metrics.pairwise_skill(per_day_by_slice, pairs, seed=args.seed)
    pvals = {(m, r): one_sided_p(per_day, m, r, args.seed) for m, r, _ in pairs}
    pairwise["p_one_sided_all_hours"] = [pvals[(m, r)] if s == "all_hours" else np.nan
                                         for m, r, s in zip(pairwise["model"], pairwise["reference"], pairwise["slice"])]
    sec = [(m, r) for m, r, role in pairs if role == "secondary"]
    adjusted = dict(zip(sec, holm([pvals[k] for k in sec]))) if sec else {}
    pairwise["p_holm_all_hours"] = [adjusted.get((m, r), np.nan) if s == "all_hours" else np.nan
                                    for m, r, s in zip(pairwise["model"], pairwise["reference"], pairwise["slice"])]
    pairwise.to_csv(args.results_dir / "pairwise.csv", index=False)

    ranked = {k: v.loc[~v["method"].isin(ORACLE_METHODS)] for k, v in (("all_hours", overall), ("daytime_only", daytime))}
    rank = metrics.ranking(ranked, per_day_by_slice, references=("t0_night_zero", "ewma"), seed=args.seed)
    rank.to_csv(args.results_dir / "ranking.csv", index=False)
    audit = metrics.source_audit(df, blend=None)
    audit.to_csv(args.results_dir / "source_audit.csv", index=False)
    issued = df.loc[~df["method"].isin(ORACLE_METHODS) & df["cov_issued_latest"].notna()]
    margin_h = ((issued["origin"] - issued["cov_issued_latest"]) / pd.Timedelta(hours=1))

    from run_benchmark import _git_sha, _resolve_revision, _versions

    elapsed = time.time() - started
    meta = {
        "git_sha": _git_sha(), "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "args": {k: str(v) for k, v in vars(args).items()},
        "model": {"repo_id": args.repo_id, "revision_requested": args.revision,
                  "revision_resolved": _resolve_revision(args.repo_id, args.revision)},
        "frozen": {"weights": cov.REGION_WEIGHTS, "stamp_offset_min": cov.STAMP_OFFSET_MIN, "wx_model": cov.WX_MODEL,
                   "wx_lead_days": cov.WX_LEAD_DAYS, "wx_sha256": cov.WX_SHA256, "era5_sha256": cov.ERA5_SHA256,
                   "p_max_h": cov.WX_P_MAX_H, "horizon": cov.COV_HORIZON, "min_context_valid": cov.MIN_CONTEXT_VALID},
        "specs": {f.name: f.spec() for f in forecasters},
        "comparisons": COMPARISONS, "windows_2024": len(windows), "scored_days": int(df["delivery_date"].nunique()),
        "report": report.as_full_dict(), "peak_mw": peak,
        "covariate_issue_margin_h": {"min": float(margin_h.min()), "median": float(margin_h.median())} if len(margin_h) else None,
        "elapsed_s": round(elapsed, 1), "packages": _versions(),
    }
    _write_json(args.results_dir / "run_meta.json", meta)
    write_summary(args, labels, overall, rank, pairwise, meta)
    print((args.results_dir / "summary.md").read_text(encoding="utf-8"))
    return 0


def ranking_markdown(rank: pd.DataFrame, labels: dict[str, str], slice_name: str) -> list[str]:
    sub = rank.loc[rank["slice"] == slice_name]
    refs = [r for r in ("t0_night_zero", "ewma") if f"vs_{r}_skill" in sub.columns]
    lines = ["| # | Method | MAE (MW) | nMAE (mean) | " + " | ".join(f"vs {labels.get(r, r)}" for r in refs) + " |",
             "|---|---|---:|---:|" + "---:|" * len(refs)]
    for _, r in sub.iterrows():
        cells = []
        for ref in refs:
            if r["method"] == ref:
                cells.append("—")
            elif pd.isna(r.get(f"vs_{ref}_lo95", np.nan)):
                cells.append(f"{r[f'vs_{ref}_skill']:+.1%}")
            else:
                cells.append(f"{r[f'vs_{ref}_skill']:+.1%} [{r[f'vs_{ref}_lo95']:+.1%}, {r[f'vs_{ref}_hi95']:+.1%}]")
        lines.append(f"| {int(r['rank'])} | {labels.get(r['method'], r['method'])} | {r['mae_mw']:,.0f} | "
                     f"{r['nmae_mean']:.1%} | " + " | ".join(cells) + " |")
    return lines


def write_summary(args, labels, overall, rank, pairwise, meta) -> None:
    all_hours = pairwise.loc[pairwise["slice"] == "all_hours"]

    def verdict(r) -> str:
        p = r["p_holm_all_hours"] if r["role"] == "secondary" else r["p_one_sided_all_hours"]
        if r["role"] == "diagnostic":
            return "diagnostic only"
        return "better (p < 0.05)" if r["skill"] > 0 and p < ALPHA else "not shown"

    rows = [
        f"| {r['role']} | {labels.get(r['model'], r['model'])} | {labels.get(r['reference'], r['reference'])} | "
        f"{r['skill']:+.1%} [{r['skill_lo95']:+.1%}, {r['skill_hi95']:+.1%}] | "
        f"{r['mae_model']:,.0f} vs {r['mae_reference']:,.0f} | {r['p_one_sided_all_hours']:.4f} | "
        f"{'' if np.isnan(r['p_holm_all_hours']) else format(r['p_holm_all_hours'], '.4f')} | {verdict(r)} |"
        for _, r in all_hours.iterrows()
    ]
    oracle_rows = overall.loc[overall["method"].isin(ORACLE_METHODS)]
    lines = [
        "# Covariate slice: t0 with solar geometry and archived weather forecasts",
        "",
        f"- Delivery days scored: **{meta['scored_days']}** of {meta['windows_2024']} buildable 2024 days "
        "(a day is scored only if every covariate is complete over its horizon and >= 98% valid over its context)",
        f"- Weather: `{cov.WX_MODEL}` `{cov.WX_VARIABLE}_previous_day{cov.WX_LEAD_DAYS}`, 12 regional points, "
        "2023-production weights; each value issued at least "
        f"{meta['covariate_issue_margin_h']['min']:.1f} h before its gate (conservative bound)"
        if meta["covariate_issue_margin_h"] else "- Weather: none",
        f"- Weights: `{meta['model']['repo_id']}` @ `{meta['model']['revision_resolved']}`",
        f"- Runtime {meta['elapsed_s'] / 60:.1f} min · git `{meta['git_sha']}`",
        "",
        "## Frozen comparisons (all hours; one-sided block-bootstrap p; Holm over the secondary set)",
        "",
        "| Role | Model | Reference | MAE reduction [95% CI] | MAE (MW) | p | p (Holm) | Reading |",
        "|---|---|---|---:|---:|---:|---:|---|",
        *rows,
        "",
        "## Ranking, all hours (point-in-time methods only)",
        "",
        *ranking_markdown(rank, labels, "all_hours"),
        "",
        "## Ranking, daytime only",
        "",
        *ranking_markdown(rank, labels, "daytime_only"),
        "",
    ]
    if len(oracle_rows):
        lines += ["## ERA5 reference arm (not point-in-time; never a finding)", ""]
        lines += [f"- {labels.get(r['method'], r['method'])}: MAE {r['mae_mw']:,.0f} MW" for _, r in oracle_rows.iterrows()]
        lines += [""]
    lines += [
        "## What this is and is not",
        "",
        "- Discovery grade on 2024 only. The 2024 test year was already used by Experiment 0;",
        "  an independent confirmation needs sealed 2025 data and the owner's approval.",
        "- The weather forecast is two or three days old at the gate (an operator would use a",
        "  12-36 h forecast), so the value of weather is understated here, not overstated.",
        "- Inputs are RTE's definitive data, as in Experiment 0.",
        "",
    ]
    (args.results_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    return {"probe": probe, "known-answer": known_answer, "run": run}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
