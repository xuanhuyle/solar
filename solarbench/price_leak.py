"""Experiment 4's leak harness: the frozen leak controls as functions, run by the unit tests (stub t0)
and by ``run_prices.py check`` on real t0 at ``TEST_ORIGINS`` before anything is scored.

Each control is named by its content (PRICE_SPEC['leak_controls']):

* ``target_poisoning`` - every price cell whose pub_latest is after d is rewritten (affine,
  then NaN); the forecast must stay byte-identical;
* ``legal_change`` - an edit of D-1 13:00-23:00 local and of a D-2 hour must move the forecast;
* ``covariate_refusal`` - a covariate cell issued at 18:00 D-1 must be refused by the contract;
* ``weather_poisoning`` / ``weather_control`` - weather cells issued after d change nothing,
  +50 on cells issued before d moves the forecast;
* ``strict_controls`` - the strict arms under the literal old rule;
* ``context_end`` - the last context value is the hour the spec names.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta

import numpy as np
import pandas as pd

from solarbench import covariates as cov
from solarbench import price_exp as px

AFFINE = (-7.5, 1234.5)  # engine.referee.leakcheck.AFFINE: a large, sign-flipping rewrite
WX_CONTROL_SHIFT = 50.0


def _one(arm, series: pd.Series, w) -> tuple[np.ndarray, np.ndarray | None]:
    p = arm.predict(series, [w])[0]
    return np.asarray(p.values, dtype="float64"), (None if p.quantiles is None else np.asarray(p.quantiles))


def same(a, b) -> bool:
    return np.array_equal(a[0], b[0], equal_nan=True) and (
        (a[1] is None and b[1] is None) or (a[1] is not None and b[1] is not None
                                            and np.array_equal(a[1], b[1], equal_nan=True)))


def moved(a, b) -> bool:
    return not same(a, b)


def poison_after(series: pd.Series, after: pd.Timestamp, *, by_publication: bool, mode: str) -> pd.Series:
    """Rewrite every cell unknown at ``after``: by publication time (pub_latest > after) under the new
    rule, or by stamp (> after) under the literal old rule. ``mode``: 'affine' or 'nan'."""
    s = series.copy()
    if by_publication:
        mask = np.asarray(px.pub_latest(s.index) > after)
    else:
        mask = np.asarray(s.index > after)
    if mode == "affine":
        s[mask] = AFFINE[0] * s[mask] + AFFINE[1]
    else:
        s[mask] = np.nan
    return s


def target_poisoning(arm, series: pd.Series, w) -> dict:
    """The new rule for every window (strict windows use the literal old rule on their own origin)."""
    base = _one(arm, series, w)
    out = {}
    for mode in ("affine", "nan"):
        if w.strict:
            poisoned = poison_after(series, w.origin, by_publication=False, mode=mode)
        else:
            poisoned = poison_after(series, w.decision, by_publication=True, mode=mode)
        out[mode] = same(base, _one(arm, poisoned, w))
    return out


def local_hours(day, hours) -> pd.DatetimeIndex:
    stamps = px.day_hours(day)
    return stamps[np.isin(stamps.tz_convert("Europe/Paris").hour, list(hours))]


def legal_change(arm, series: pd.Series, w, *, which: str) -> bool:
    """True if the forecast moves when a legal cell changes: 'afternoon' = D-1 13:00-23:00 local x1.5 + 100;
    'd2' = one D-2 hour (the local 10:00) + 250; 'noon' = the 12:00 D-1 stamp + 250 (strict arm)."""
    d = w.delivery_date
    s = series.copy()
    if which == "afternoon":
        idx = local_hours(d - timedelta(days=1), range(13, 24))
        s[idx] = 1.5 * s[idx] + 100.0
    elif which == "d2":
        idx = local_hours(d - timedelta(days=2), [10])
        s[idx] = s[idx] + 250.0
    elif which == "noon":
        idx = local_hours(d - timedelta(days=1), [12])
        s[idx] = s[idx] + 250.0
    else:
        raise ValueError(which)
    return moved(_one(arm, series, w), _one(arm, s, w))


def covariate_refusal(window) -> bool:
    """A covariate cell issued at 18:00 D-1 (after d) must be refused by the price contract."""
    from solarbench.forecasters import Prediction

    late = window.decision + pd.Timedelta(hours=6)
    n = len(window.targets)
    pred = Prediction(values=np.zeros(n), max_source_time=window.origin,
                      source_latest=pd.DatetimeIndex([window.origin] * n), covariate_issued_latest=late)
    try:
        px.check_price_contract("probe", window, pred)
    except AssertionError:
        return True
    return False


def _with_covariates(arm, covariates):
    return replace(arm, covariates=tuple(covariates), missing={"context": [], "sanitised": []})


def weather_controls(arm, series: pd.Series, w) -> dict:
    """Weather cells issued after d: rewritten without effect; +50 on cells issued before d: must move."""
    base = _one(arm, series, w)
    after_ok, before_moves = True, True
    for mode in ("affine", "nan"):
        covs = []
        for c in arm.covariates:
            if isinstance(c, cov.SeriesCovariate) and c.issued is not None:
                s = c.series.copy()
                late = np.asarray(c.issued.reindex(s.index) > w.decision)
                s[late] = (AFFINE[0] * s[late] + AFFINE[1]) if mode == "affine" else np.nan
                c = replace(c, series=s)
            covs.append(c)
        after_ok = after_ok and same(base, _one(_with_covariates(arm, covs), series, w))
    covs = []
    for c in arm.covariates:
        if isinstance(c, cov.SeriesCovariate) and c.issued is not None:
            s = c.series.copy()
            early = np.asarray(c.issued.reindex(s.index) <= w.decision) & np.isfinite(s.to_numpy())
            s[early] = s[early] + WX_CONTROL_SHIFT
            c = replace(c, series=s)
        covs.append(c)
    before_moves = moved(base, _one(_with_covariates(arm, covs), series, w))
    return {"after_d_no_effect": after_ok, "before_d_moves": before_moves}


def context_end(arm, series: pd.Series, w) -> bool:
    """The t0 context ends at the origin the spec names: [D-1 23:00, D 00:00) Paris, or the 12:00 D-1 stamp."""
    want = (w.decision if w.strict else px.day_hours(w.delivery_date)[0] - px.HOUR)
    if w.origin != want:
        return False
    ctx, _ = arm.context(series, w.origin) if hasattr(arm, "context") else (None, None)
    if ctx is None:
        return True
    return bool(np.array_equal(ctx[-1:], np.asarray([series.loc[want]], dtype="float32"), equal_nan=True))
