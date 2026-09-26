"""One reusable leak check for every method the engine runs.

``check_method(make, bundle, windows)`` takes a *factory* that builds the
method from a data bundle. For a few origins it:

1. poisons everything that was not known at the origin - target values after
   it, RTE's forecast after it, and every weather cell whose issue bound is
   after it - two ways (an affine rewrite and NaN), rebuilds the method from the
   poisoned bundle, and requires a byte-identical forecast;
2. changes a legal value before the origin (the last day of context) and
   requires the forecast to *move*, so the check could have seen a leak;
3. requires every covariate cell the method reads to have been issued by the
   origin.

Because the method is rebuilt from the bundle, data held inside a forecaster
(a covariate series) is poisoned too - which the older, per-test poisoning
checks could not reach. RTE's own forecast (``rte_j1``) is exempt: its values
are stamped at the target times and its issue time is unverified, so it is a
reference that never decides anything.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from engine import arms as am
from solarbench import covariates as cov
from solarbench.backtest import run_backtest

AFFINE = (-7.5, 1234.5)


def _poison_series(s: pd.Series | None, after: pd.Timestamp, kind: str, issued: pd.Series | None = None):
    if s is None:
        return None
    out = s.copy()
    mask = (issued > after).to_numpy() if issued is not None else (out.index > after)
    if kind == "nan":
        out.loc[mask] = np.nan
    else:
        out.loc[mask] = out.loc[mask] * AFFINE[0] + AFFINE[1]
    return out


def weather_issue_bounds(hourly: pd.Series, lead_days: int) -> pd.Series:
    """The referee's issue bound for each archived hourly value (never the provider's own claim)."""
    return pd.Series(cov.issue_bound(hourly.index, lead_days), index=hourly.index)


def poisoned_bundle(bundle: am.DataBundle, origin: pd.Timestamp, kind: str, leads: dict[str, int]) -> am.DataBundle:
    weather = {k: _poison_series(v, origin, kind, weather_issue_bounds(v, leads[k])) for k, v in bundle.weather.items()}
    return bundle.replaced(target=_poison_series(bundle.target, origin, kind),
                           reference=_poison_series(bundle.reference, origin, kind), weather=weather)


def _forecast(methods: list, series: pd.Series, window, scored: str) -> tuple[np.ndarray, pd.Timestamp | None]:
    """The scored method's forecast for one window; a forecast that became non-finite is NaN (never equal)."""
    try:
        df = run_backtest(series, methods, [window])
    except RuntimeError:  # every method dropped the window: its forecast went non-finite
        return np.full(len(window.targets), np.nan), None
    rows = df.loc[df["method"] == scored].sort_values("target_time")
    issued = rows["cov_issued_latest"].max() if "cov_issued_latest" in rows else None
    return rows["y_hat"].to_numpy(dtype="float64"), issued


def check_method(make: Callable[[am.DataBundle], am.Method], bundle: am.DataBundle, windows: list, *,
                 leads: dict[str, int], n_origins: int = 3) -> dict:
    """Run the three checks on ``n_origins`` windows (first, middle, last); pass iff all hold."""
    if not windows:
        return {"pass": False, "error": "no windows"}
    try:
        return _check(make, bundle, windows, leads, n_origins)
    except AssertionError as exc:  # the backtest's issue-time contract refused the method outright
        return {"pass": False, "contract_violation": str(exc)[:400]}


def _check(make, bundle, windows, leads, n_origins) -> dict:
    picks = sorted({0, len(windows) // 2, len(windows) - 1})[:n_origins]
    report = {"origins": [], "identical": True, "control_moved": True, "issued_by_origin": True}
    for i in picks:
        w = windows[i]
        method = make(bundle)
        clean, issued = _forecast(method.forecasters, bundle.target, w, method.scored)
        row = {"origin": str(w.origin), "delivery_date": str(w.delivery_date)}
        for kind in ("affine", "nan"):
            pb = poisoned_bundle(bundle, w.origin, kind, leads)
            pm = make(pb)
            got, _ = _forecast(pm.forecasters, pb.target, w, pm.scored)
            same = bool(np.array_equal(clean, got))
            row[f"identical_{kind}"] = same
            report["identical"] &= same
        # Positive control: scale the last legal day of the target (before the origin).
        legal = bundle.target.copy()
        last_day = (legal.index <= w.origin) & (legal.index > w.origin - pd.Timedelta(days=1))
        legal.loc[last_day] = legal.loc[last_day] * 1.5 + 100.0
        cb = bundle.replaced(target=legal)
        cm = make(cb)
        moved, _ = _forecast(cm.forecasters, cb.target, w, cm.scored)
        row["control_moved"] = not bool(np.array_equal(clean, moved))
        report["control_moved"] &= row["control_moved"]
        ok_issue = issued is None or pd.isna(issued) or pd.Timestamp(issued) <= w.origin
        row["covariate_issued_latest"] = None if issued is None or pd.isna(issued) else str(issued)
        report["issued_by_origin"] &= bool(ok_issue)
        report["origins"].append(row)
    report["pass"] = bool(report["identical"] and report["control_moved"] and report["issued_by_origin"])
    return report
