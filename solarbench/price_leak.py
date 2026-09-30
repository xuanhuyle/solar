"""Experiment 4's leak harness: the frozen leak controls as functions, run by the unit tests (stub t0)
and by ``run_prices.py check`` on real t0 at ``TEST_ORIGINS`` before anything is scored.

Each control is named by its content (PRICE_SPEC['leak_controls']):

* ``target_poisoning`` - every price cell whose pub_latest is after d is rewritten (affine,
  then NaN); the forecast must stay byte-identical;
* ``legal_change`` - an edit of D-1 13:00-23:00 local and of a D-2 hour must move the forecast;
  ``eq_error_quantiles_move`` - an edit of D-1 must move best_simple_eq's error quantiles;
* ``covariate_refusal`` - a covariate cell issued at 18:00 D-1 must be refused by the contract, on its own
  (``covariate_refusal``) and through each arm with a covariate (``covariate_refusal_arm``);
* ``weather_poisoning`` / ``weather_control`` - weather cells issued after d change nothing,
  +50 on cells issued before d moves the forecast;
* ``strict_controls`` - the strict arms under the literal old rule;
* ``context_end`` - the last context value is the hour the spec names;
* ``variate_whitelist`` - target = French price; covariates = holiday, wx_temperature, wx_radiation; no
  realised series.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta

import numpy as np
import pandas as pd

from solarbench import covariates as cov
from solarbench import price_exp as px
from solarbench import price_spec as ps
from solarbench import probes as pr

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


EQ_D1_SHIFT = 400.0


def eq_error_quantiles_move(eq, series: pd.Series, w, *, shift: float = EQ_D1_SHIFT) -> bool:
    """"editing D-1 must move best_simple_eq's error quantiles": an edit of every hour of D-1 must change
    Q_tau(E_t) itself (``eq.error_quantiles``, exact compare), not the bands f_D + Q_tau(E_t), which a base
    reading D-1 would move whatever the error cells are. The edit is tried as +``shift`` and then -``shift``:
    a D-1 error already at the top (bottom) of E_t moves no quantile when pushed further the same way, so a
    one-sided edit would fail on correct code (about 1% of real days at +40)."""
    base = eq.error_quantiles(series, [w])[0]
    d1 = px.day_hours(w.delivery_date - timedelta(days=1))
    for sign in (1.0, -1.0):
        s2 = series.copy()
        s2[d1] += sign * shift
        if not np.array_equal(base, eq.error_quantiles(s2, [w])[0], equal_nan=True):
            return True
    return False


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


#: The probe covariate's issue time: d + 6 h = 18:00 D-1 Paris (no DST switch falls between 12:00 and 18:00).
PROBE_ISSUE_AFTER_D = pd.Timedelta(hours=6)


def covariate_refusal_arm(arm, series: pd.Series, w) -> bool:
    """The refusal through the arm itself ("for every arm with a covariate"): a copy of ``arm`` (dataclasses.replace,
    its own ``missing``) with one extra covariate over ``arm.block_times(w.origin)``, every cell issued at d + 6 h,
    must be refused: True iff ``run_price_backtest`` on it raises AssertionError. An arm that stopped reporting
    its covariates' issue times would pass the arm-less ``covariate_refusal`` and fail here."""
    times = arm.block_times(w.origin)
    probe = cov.SeriesCovariate(name="probe_issued_18h", series=pd.Series(0.0, index=times),
                                issued=pd.Series(w.decision + PROBE_ISSUE_AFTER_D, index=times))
    probed = _with_covariates(arm, (*arm.covariates, probe))
    try:
        px.run_price_backtest(series, [probed], [w])
    except AssertionError:
        return True
    return False


#: leak_controls, variate whitelist: each t0 arm's covariates by name, in order (weather_p4.covariates).
WX_COVARIATES: tuple[str, ...] = tuple(ps.PRICE_SPEC["weather_p4"]["covariates"])
WHITELIST: dict[str, tuple[str, ...]] = {"t0": (), "t0_cal": ("holiday",), "t0_cal_strict": ("holiday",),
                                         "t0_cal_wx": WX_COVARIATES}


def variate_whitelist(arm, weather: tuple | None = None) -> dict[str, bool]:
    """leak_controls: "variate whitelist: target = French price; covariates = holiday, wx_temperature,
    wx_radiation (plus K3's oracle series under the two-key exemption); no realised series".

    For the run's t0 arms (a PriceT0Forecaster, whose target is the French price series it is given): t0 carries
    no covariate, t0_cal and t0_cal_strict exactly (holiday,), t0_cal_wx exactly (holiday, wx_temperature,
    wx_radiation) in that order; holiday is the calendar (a solarbench.probes.HolidayCovariate, from timestamps
    alone); each wx_* is a solarbench.covariates.SeriesCovariate with an issue series (issued not None) and not an
    oracle; with ``weather`` (the tuple load_weather returned) each wx_* is that very object. K3's oracle arms are
    not run arms and keep their own two-key exemption (price_exp._oracle_flags). Every value must be True."""
    name = getattr(arm, "name", None)
    want = WHITELIST.get(name)
    covs = tuple(getattr(arm, "covariates", ()) or ())
    out = {"known_arm": want is not None, "t0_arm": isinstance(arm, px.PriceT0Forecaster)}
    if want is None:
        return out
    out["names"] = tuple(getattr(c, "name", None) for c in covs) == want
    out["no_oracle"] = not any(bool(getattr(c, "oracle", False)) for c in covs)
    out["holiday_is_calendar"] = all(type(c) is pr.HolidayCovariate
                                     for c in covs if getattr(c, "name", None) == "holiday")
    wx = [c for c in covs if str(getattr(c, "name", "")).startswith("wx_")]
    out["weather_issue_bounded"] = all(type(c) is cov.SeriesCovariate and c.issued is not None for c in wx)
    if weather is not None and name == "t0_cal_wx":
        weather = tuple(weather)
        out["weather_is_loaded"] = len(wx) == len(weather) and all(a is b for a, b in zip(wx, weather))
    return out
