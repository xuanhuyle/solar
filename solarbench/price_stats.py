"""Experiment 4's statistics: day sets, per-day losses, skills and the bootstrap, the verdict states, the
reading table, the report-only secondaries, slices and tables, and the carry-forward rule.

Everything here implements ``solarbench.price_spec.PRICE_SPEC`` as written (``statistics``, ``probes``,
``report_only``, ``reading_table``, ``carry_forward``); nothing reinterprets it.

Experiment 4 is discovery-grade (``PRICE_SPEC['status']``): 2024-2025 French prices are public and already
studied, and 2025 is consumed. No number computed here is a confirmation, and Experiment 4 cannot by itself
satisfy the project's independent-confirmation milestone: ``carry_forward`` only names vault candidates for a
later, separate confirmation, and the choice of any follow-up investigation is not made here.

Conventions

* A comparison's per-day table has the columns ``delivery_date, method, sum_abs_err, n`` for exactly its two
  arms; for the pinball metric ``sum_abs_err`` holds the per-day pinball sum (as ``run_probes.per_day_pinball``,
  ``metrics.bootstrap_skill`` and ``engine.referee.stats.power_table`` expect).
* A field that ``statistics.day_sets`` leaves uncomputed holds the string ``'not run'`` (an arm a failed gate
  left unscored: lear_ens and lear_ens_eq after K1 failed, t0_cal_wx after K3 failed) or ``'no days'`` (an
  empty day set, year or slice); nothing numeric is ever invented for it, and no metrics function is called
  for it. Any other arm missing from a comparison raises ``ValueError`` (``unscored``).
* A failed per-day check (``metrics._day_pivot``), or a non-finite skill or draw, raises ``StatisticsError``:
  the run stops with nothing reported.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from types import MappingProxyType
from typing import Callable, Iterable, Mapping

import numpy as np
import pandas as pd

from engine import claims, zones
from engine.referee import stats as referee_stats
from solarbench import metrics
from solarbench import price_exp as px
from solarbench import price_spec as ps
from solarbench import probes as pr

SPEC = ps.PRICE_SPEC
STATS = SPEC["statistics"]
RT = SPEC["reading_table"]
CF = SPEC["carry_forward"]

FAMILY: tuple[str, ...] = tuple(STATS["family"])
ALPHA: float = float(STATS["alpha"])
TEST_YEARS: tuple[str, ...] = tuple(SPEC["periods"]["test_years"])
PROBES: dict[str, dict] = {p["id"]: p for p in SPEC["probes"]}

#: statistics.bootstrap: 14-day blocks (engine.claims.BLOCK_DAYS), 2000 draws, seed 0.
BLOCK_DAYS: int = claims.BLOCK_DAYS
SAMPLES = 2000
SEED = 0
SENSITIVITY_BLOCKS = (1, 3, 7, 14, 30)
#: probes[*].success: the pooled and per-year thresholds (passed only strictly above).
THRESHOLDS = {"P1": 0.0, "P2": -0.05, "P3": 0.0, "P4": 0.0}
#: statistics.p_value: m = -margin (0 for superiority, -0.05 for P2's non-inferiority).
MARGINS = {"P1": 0.0, "P2": 0.05, "P3": 0.0, "P4": 0.0}
#: P3's coverage band, closed and unrounded.
COVERAGE_BAND = (0.70, 0.90)
#: statistics.p2_coverage.
P2_COVERAGE_MIN = 0.95
#: carry_forward.rule.
CARRY_DELTAS = (0.0, 0.05, 0.10, 0.20)
CARRY_ALPHA = 0.0125
CARRY_MONTHS = frozenset(range(4, 10))  # April-September
CARRY_YEARS = frozenset(int(y) for y in TEST_YEARS)
CARRY_BLOCKS = "12"

NOT_RUN = "not run"
NO_DAYS = "no days"
METRICS = ("mae", "pinball")
Q_COLUMNS: tuple[str, ...] = tuple(px.quantile_column(level) for level in px.LEVELS)
STATE_NAMES = {"P1": ("won", "lost", "not stable"),
               "P2": ("won", "lost", "not stable", "not runnable"),
               "P3": ("won", "lost", "not stable", "lost on coverage"),
               "P4": ("won", "lost", "not stable", "not runnable")}

#: The arm that is lear_ens plus empirical bands (report_only secondaries); lear_ens's K1 rule applies to it.
LEAR_BANDS = "lear_ens_eq"
#: statistics.day_sets: the only arms that may go unscored, each with the gate whose failure leaves it unscored
#: ('not run': lear_ens after K1 failed, t0_cal_wx after K3 failed; lear_ens's bands follow lear_ens). Any other
#: arm missing from a comparison is a wiring error (never forecast, or renamed) and raises ValueError.
GATED_ARMS: Mapping[str, str] = MappingProxyType({"lear_ens": "K1", LEAR_BANDS: "K1", "t0_cal_wx": "K3"})
STRICT_ARM = SPEC["strict_arm"]["name"]
STRICT_COMPARATORS = tuple(SPEC["strict_arm"]["comparators"])

# The sentences the reading table asks to add or print, quoted there verbatim; checked against the spec below.
NOT_WON_BASE = "This study does not show that t0 is useful on French prices from price history alone."
NOT_WON_ADD_LEAR = "the comparison with LEAR was not made."
NOT_WON_ADD_INTERVAL = "the best simple rule was more accurate (interval not adjusted for multiplicity)."
STRICT_NO_ALLOWANCE = "P1 does not rest on t0 reading the D-1 afternoon prices."
STRICT_OLD_RULE = ("Under the old rule for every arm t0 still beats the same simple rule; its edge over the rule that "
                   "keeps the allowance needs the D-1 afternoon.")
STRICT_DEPENDS = "P1's win depends on the D-1 afternoon allowance."
STRICT_NOT_READ = "P1 was not won, so the strict check is not read; its skills are printed for information only."

SECONDARY_PAIRS: dict[str, tuple[str, str, str]] = {
    "t0 (no calendar) vs best_simple_2023": ("t0", "best_simple_2023", "mae"),
    "t0_cal vs t0": ("t0_cal", "t0", "mae"),
    "t0_cal_strict vs best_simple_2023 (t0 alone without the allowance)": (STRICT_ARM, "best_simple_2023", "mae"),
    "t0_cal_strict vs best_simple_2023_strict (the old rule for both)": (STRICT_ARM, "best_simple_2023_strict",
                                                                         "mae"),
    "t0_cal vs t0_cal_strict (value of the D-1 afternoon to t0)": ("t0_cal", STRICT_ARM, "mae"),
    "lear_ens vs best_simple_2023": ("lear_ens", "best_simple_2023", "mae"),
    "t0_cal vs lear_ens (superiority)": ("t0_cal", "lear_ens", "mae"),
    "lear_ens + empirical bands vs t0_cal bands": (LEAR_BANDS, "t0_cal", "pinball"),
}
RMAE_KEY = "rMAE vs naive_std and vs prev_week"
#: The rMAE references: spec name -> the arm's name in the frame (the runner scores both under these names; a
#: caller whose frame names them otherwise passes secondaries(rmae_refs=...)).
RMAE_REFS: Mapping[str, str] = MappingProxyType({"naive_std": "naive_std", "prev_week": "prev_week"})
RMSE_KEY = "RMSE"
SLICE_YEAR, SLICE_QUARTER, SLICE_APR_SEP, SLICE_NEGATIVE, SLICE_TOP, SLICE_MIDDAY, SLICE_WEEKEND, SLICE_DST = (
    SPEC["report_only"]["slices"])
HOUR_SLICES = (SLICE_NEGATIVE, SLICE_TOP, SLICE_MIDDAY)
TOP_QUANTILE = 0.99
MIDDAY_HOURS = range(11, 16)  # hours starting 11:00 .. 15:00 Europe/Paris
DST_WEEK_DAYS = 7


class StatisticsError(RuntimeError):
    """A failed per-day check, or a non-finite skill or draw: the run stops with nothing reported."""


def _check_spec() -> None:
    """The constants above are the frozen spec's own words (a mismatch is a build error, never a silent edit)."""
    quoted = {"P1 not won, P2 not won": (NOT_WON_ADD_LEAR, NOT_WON_ADD_INTERVAL),
              "strict": (STRICT_NO_ALLOWANCE, STRICT_OLD_RULE, STRICT_DEPENDS, STRICT_NOT_READ)}
    for key, sentences in quoted.items():
        for s in sentences:
            if f"'{s}'" not in RT[key]:
                raise RuntimeError(f"reading_table[{key!r}] does not quote {s!r}")
    if not RT["P1 not won, P2 not won"].startswith(NOT_WON_BASE + " "):
        raise RuntimeError("reading_table['P1 not won, P2 not won'] does not open with NOT_WON_BASE")
    success = {pid: PROBES[pid]["success"] for pid in FAMILY}
    for pid, thr in THRESHOLDS.items():
        word = "skill > 0" if thr == 0.0 else "skill > -0.05"
        if word not in success[pid]:
            raise RuntimeError(f"{pid}'s success rule does not say {word!r}")
    if "m = -0.05 for P2" not in STATS["p_value"] or "/ 2001" not in STATS["p_value"]:
        raise RuntimeError("statistics.p_value is not the rule implemented here")
    if "[0.70, 0.90]" not in PROBES["P3"]["success"] or ">= 95%" not in STATS["p2_coverage"]:
        raise RuntimeError("P3's coverage band or P2's coverage rule differs from the constants")
    if BLOCK_DAYS != 14 or "block_days=14, samples=2000, seed=0" not in STATS["bootstrap"]:
        raise RuntimeError("statistics.bootstrap differs from the constants")
    if "alpha=0.0125)['min_detectable_skill']['12']" not in CF["rule"] or "{0, 0.05, 0.10, 0.20}" not in CF["rule"]:
        raise RuntimeError("carry_forward.rule differs from the constants")
    if not set(SECONDARY_PAIRS) | {RMAE_KEY, RMSE_KEY} == set(SPEC["report_only"]["secondaries"]):
        raise RuntimeError("report_only.secondaries differs from SECONDARY_PAIRS")
    if not all(f"vs {ref}" in RMAE_KEY for ref in RMAE_REFS):
        raise RuntimeError("the rMAE references differ from report_only.secondaries")
    if "lear_ens after K1 failed, t0_cal_wx after K3 failed" not in STATS["day_sets"]:
        raise RuntimeError("statistics.day_sets names other unscored arms than GATED_ARMS")
    if ("the hours starting 11:00 to 15:00 Europe/Paris" not in STATS["day_sets"] or MIDDAY_HOURS != range(11, 16)
            or f"numpy.quantile(|y|, {TOP_QUANTILE})" not in STATS["day_sets"]):
        raise RuntimeError("statistics.day_sets' hour slices differ from MIDDAY_HOURS / TOP_QUANTILE")
    if "bootstrap_sensitivity, " + ", ".join(map(str, SENSITIVITY_BLOCKS)) + ")" not in STATS["bootstrap"]:
        raise RuntimeError("statistics.bootstrap's block-length table differs from SENSITIVITY_BLOCKS")
    if ("April-September of " + " or ".join(TEST_YEARS) not in CF["rule"] or CARRY_MONTHS != frozenset(range(4, 10))
            or CARRY_YEARS != frozenset(int(y) for y in TEST_YEARS)):
        raise RuntimeError("carry_forward.rule's months or years differ from CARRY_MONTHS / CARRY_YEARS")


_check_spec()


# ------------------------------------------------------------------------------ helpers


def _to_date(x) -> date:
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    return pd.Timestamp(x).date()


def _dates(values: pd.Series) -> pd.Series:
    """Delivery dates as ``datetime.date`` (mapped once per distinct value)."""
    if pd.api.types.is_datetime64_any_dtype(values):
        return values.dt.date
    lookup = {u: _to_date(u) for u in pd.unique(values)}
    return values.map(lookup)


def _num(x) -> bool:
    """A finite number (not a status string, not None, not a bool)."""
    return isinstance(x, (int, float, np.integer, np.floating)) and not isinstance(x, bool) and math.isfinite(x)


def _value_columns(metric: str) -> list[str]:
    if metric == "mae":
        return ["y_hat"]
    if metric == "pinball":
        return list(Q_COLUMNS)
    raise ValueError(f"unknown metric {metric!r} (one of {METRICS})")


def probe_arms(pid: str) -> tuple[str, str, str]:
    """(t0 arm, comparator, metric) of a primary, from PRICE_SPEC['probes']."""
    p = PROBES[pid]
    return p["t0_arm"].split()[0], p["comparator"], p["metric"]


def period_days(key: str) -> list[date]:
    """The Paris delivery days of PRICE_SPEC['periods'][key]."""
    start, end = SPEC["periods"][key]
    return px.days_between(start, end)


def p4_allowed_days(rule_days: Iterable) -> list[date]:
    """P4's allowed days: the days passing weather_p4.day_rule, within periods.p4_days from AVAIL.p4_first_day."""
    start, end = (_to_date(d) for d in SPEC["periods"]["p4_days"])
    first = ps.AVAIL.get("p4_first_day")
    if first is not None:
        start = max(start, _to_date(first))
    return sorted({d for d in map(_to_date, rule_days) if start <= d <= end})


def dst_switch_days(days: Iterable) -> list[date]:
    """The days among ``days`` whose Paris day has 23 or 25 hours."""
    return sorted(d for d in {_to_date(x) for x in days} if len(px.day_hours(d)) != 24)


_HOUR_NS = 3_600_000_000_000


def _full_days(sub: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Per (day, method) of ``sub``: True iff the method has exactly the real hours of the Paris day, each once,
    with ``y`` and every column of ``cols`` finite. Index (day, method), one boolean column ``full``."""
    if sub.empty:
        return pd.DataFrame({"full": pd.Series(dtype=bool)},
                            index=pd.MultiIndex.from_arrays([[], []], names=["day", "method"]))
    t = pd.DatetimeIndex(sub["target_time"])
    ns = t.as_unit("ns").asi8
    finite = np.isfinite(sub[["y", *cols]].to_numpy(dtype="float64")).all(axis=1)
    frame = pd.DataFrame({"day": _dates(sub["delivery_date"]).to_numpy(), "method": sub["method"].to_numpy(),
                          "t": ns, "ok": finite & (ns % _HOUR_NS == 0)})
    agg = frame.groupby(["day", "method"], sort=True).agg(
        n=("t", "size"), unique=("t", "nunique"), first=("t", "min"), last=("t", "max"), ok=("ok", "all"))
    expected = {}
    for d in agg.index.get_level_values("day").unique():
        h = px.day_hours(d).as_unit("ns").asi8
        expected[d] = (len(h), h[0], h[-1])
    exp = np.array([expected[d] for d in agg.index.get_level_values("day")], dtype="int64")
    full = (agg["ok"].to_numpy() & (agg["n"].to_numpy() == exp[:, 0]) & (agg["unique"].to_numpy() == exp[:, 0])
            & (agg["first"].to_numpy() == exp[:, 1]) & (agg["last"].to_numpy() == exp[:, 2]))
    return pd.DataFrame({"full": full}, index=agg.index)


# ------------------------------------------------------------------------------ day sets


def day_set(df: pd.DataFrame, arm: str, ref: str, *, metric: str, allowed_days: Iterable | None = None
            ) -> list[date]:
    """statistics.day_sets: the allowed days whose target is complete and on which both arms are finite at
    every scored hour ('mae': y_hat; 'pinball': all five quantiles). A day enters or leaves whole; arms
    outside the comparison never remove its days. Sorted ``datetime.date`` list."""
    if arm == ref:
        raise ValueError("a comparison needs two different arms")
    cols = _value_columns(metric)
    sub = df.loc[df["method"].isin([arm, ref]), ["delivery_date", "method", "target_time", "y", *cols]]
    if allowed_days is not None:
        allowed = {_to_date(d) for d in allowed_days}
        sub = sub.loc[_dates(sub["delivery_date"]).isin(allowed).to_numpy()]
    full = _full_days(sub, cols)["full"].unstack("method", fill_value=False)
    if full.empty or arm not in full.columns or ref not in full.columns:
        return []
    both = full[arm].astype(bool) & full[ref].astype(bool)
    days = sorted(both.index[both.to_numpy()])
    if days:  # the target is one series: both arms must carry the same y at the same hours
        keep = _dates(sub["delivery_date"]).isin(set(days)).to_numpy()
        ys = {m: sub.loc[keep & (sub["method"] == m).to_numpy()].set_index("target_time")["y"].sort_index()
              for m in (arm, ref)}
        if not (ys[arm].index.equals(ys[ref].index)
                and np.array_equal(ys[arm].to_numpy(), ys[ref].to_numpy())):
            raise StatisticsError(f"{arm} and {ref} carry different targets on their common days")
    return days


def complete_days(df: pd.DataFrame, days: Iterable | None = None) -> list[date]:
    """The days (among ``days``, default every day in ``df``) whose target is complete: y present and finite at
    every real hour of the Paris day."""
    sub = df.drop_duplicates("target_time")[["delivery_date", "target_time", "y"]].assign(method="target")
    if days is not None:
        allowed = {_to_date(d) for d in days}
        sub = sub.loc[_dates(sub["delivery_date"]).isin(allowed).to_numpy()]
    full = _full_days(sub, [])
    return sorted(d for (d, _), ok in full["full"].items() if ok)


def arm_days(df: pd.DataFrame, arm: str, days: Iterable, *, metric: str = "mae") -> list[date]:
    """The days among ``days`` on which ``arm`` is finite at every real hour (target complete)."""
    cols = _value_columns(metric)
    allowed = {_to_date(d) for d in days}
    sub = df.loc[(df["method"] == arm).to_numpy(), ["delivery_date", "method", "target_time", "y", *cols]]
    sub = sub.loc[_dates(sub["delivery_date"]).isin(allowed).to_numpy()]
    full = _full_days(sub, cols)
    return sorted(d for (d, _), ok in full["full"].items() if ok)


def arm_missing(df: pd.DataFrame, arm: str, days: Iterable, *, metric: str = "mae") -> list[date]:
    """The days among ``days`` (complete targets) on which ``arm`` is not finite at every hour (reported by
    cause with the arm's own record, e.g. PriceT0Forecaster.missing)."""
    have = set(arm_days(df, arm, days, metric=metric))
    return sorted({_to_date(d) for d in days} - have)


def p2_coverage(df: pd.DataFrame, days: Iterable, arm: str = "lear_ens") -> float:
    """statistics.p2_coverage: the share of ``days`` (the test days whose target is complete) on which ``arm``
    is finite at every hour."""
    days = sorted({_to_date(d) for d in days})
    if not days:
        raise ValueError("p2_coverage needs the complete test days")
    return len(arm_days(df, arm, days)) / len(days)


# ------------------------------------------------------------------------------ per-day tables


def _row_mask(df: pd.DataFrame, hours) -> np.ndarray:
    if isinstance(hours, pd.Series):
        return hours.reindex(df.index, fill_value=False).to_numpy(dtype=bool)
    mask = np.asarray(hours, dtype=bool)
    if mask.shape != (len(df),):
        raise ValueError(f"an hour mask must have one entry per row ({len(df)}), got {mask.shape}")
    return mask


def per_day(df: pd.DataFrame, arm: str, ref: str, *, metric: str, days: Iterable,
            hours=None) -> pd.DataFrame:
    """The per-day table of a comparison: ``delivery_date, method, sum_abs_err, n`` for its two arms on ``days``.

    'mae': the sum of |y - y_hat|; 'pinball': per hour the mean pinball loss over the five levels
    (solarbench.probes.pinball), summed per day. ``hours`` is an optional boolean row mask (an hour slice): the
    table then holds only those hours, and a day with none of them is left out for both arms. A single
    non-finite hour is never dropped: it makes its day's sum NaN, which the per-day check refuses.
    """
    cols = _value_columns(metric)
    wanted = {_to_date(d) for d in days}
    mask = df["method"].isin([arm, ref]).to_numpy() & _dates(df["delivery_date"]).isin(wanted).to_numpy()
    if hours is not None:
        mask &= _row_mask(df, hours)
    sub = df.loc[mask]
    if sub.empty:
        return pd.DataFrame({"delivery_date": pd.Series(dtype=object), "method": pd.Series(dtype=object),
                             "sum_abs_err": pd.Series(dtype="float64"), "n": pd.Series(dtype="int64")})
    y = sub["y"].to_numpy(dtype="float64")
    if metric == "mae":
        loss = np.abs(y - sub["y_hat"].to_numpy(dtype="float64"))
    else:
        loss = pr.pinball(y, sub[cols].to_numpy(dtype="float64"), px.LEVELS)
    frame = pd.DataFrame({"delivery_date": _dates(sub["delivery_date"]).to_numpy(),
                          "method": sub["method"].to_numpy(), "loss": loss, "bad": ~np.isfinite(loss)})
    g = frame.groupby(["delivery_date", "method"], sort=True)
    out = g.agg(sum_abs_err=("loss", "sum"), n=("loss", "size"), bad=("bad", "any"))
    out.loc[out["bad"], "sum_abs_err"] = np.nan
    out = out.drop(columns="bad").reset_index()
    out["n"] = out["n"].astype("int64")
    return out[["delivery_date", "method", "sum_abs_err", "n"]]


def _two(per_day_df: pd.DataFrame, arm: str, ref: str) -> pd.DataFrame:
    return per_day_df.loc[per_day_df["method"].isin([arm, ref])]


def _checked(per_day_df: pd.DataFrame, arm: str, ref: str):
    """metrics._day_pivot (same days, equal hour counts, no NaN); a failure stops the run."""
    try:
        return metrics._day_pivot(per_day_df, arm, ref)
    except (KeyError, ValueError) as exc:
        raise StatisticsError(f"per-day check failed for {arm} vs {ref}: {exc}") from exc


def _skill(loss_arm: float, loss_ref: float, what: str) -> float:
    with np.errstate(divide="ignore", invalid="ignore"):
        s = 1.0 - np.float64(loss_arm) / np.float64(loss_ref)
    if not np.isfinite(s):
        raise StatisticsError(f"non-finite skill for {what} (sum arm {loss_arm}, sum ref {loss_ref})")
    return float(s)


def pooled_skill(per_day_df: pd.DataFrame, arm: str, ref: str) -> float:
    """1 - sum arm / sum ref over the per-day table (checked first)."""
    _, err_a, err_r, _ = _checked(_two(per_day_df, arm, ref), arm, ref)
    return _skill(err_a.sum(), err_r.sum(), f"{arm} vs {ref}")


# ------------------------------------------------------------------------------ comparisons


def _gate_passed(gate: str, k1_passed: bool | None, k3_passed: bool | None) -> bool | None:
    return {"K1": k1_passed, "K3": k3_passed}[gate]


def unscored(arms: Iterable[str], scored: Iterable[str], *, k1_passed: bool | None = None,
             k3_passed: bool | None = None) -> list[str]:
    """statistics.day_sets: the causes (e.g. 'lear_ens not scored (K1 failed)') of the arms among ``arms`` left
    unscored by a failed gate; empty if every arm was scored, and the comparison is then computed.

    Only lear_ens and lear_ens_eq (K1 failed) and t0_cal_wx (K3 failed) may be unscored; a gated arm is unscored
    whenever its gate failed, whatever ``scored`` says. Any other arm missing from ``scored`` (never forecast,
    or forecast under another name), or a gated arm missing although its gate passed or with its gate outcome
    not given, raises ValueError: 'not run' is never printed for any other cause.
    """
    scored = set(scored)
    causes = []
    for a in arms:
        gate = GATED_ARMS.get(a)
        passed = None if gate is None else _gate_passed(gate, k1_passed, k3_passed)
        if passed is False:
            causes.append(f"{a} not scored ({gate} failed)")
        elif a not in scored:
            if gate is None:
                raise ValueError(f"{a} was not scored; only {sorted(GATED_ARMS)} may go unscored, after their gate "
                                 "failed (statistics.day_sets)")
            if passed is None:
                raise ValueError(f"{a} was not scored and {gate}'s outcome was not given ({gate.lower()}_passed)")
            raise ValueError(f"{a} was not scored although {gate} passed")
    return causes


def compare(per_day_df: pd.DataFrame | None, arm: str, ref: str, *, margin: float = 0.0,
            scored: bool = True) -> dict:
    """Pooled skill, the 14-day block bootstrap's 95% interval and one-sided p (statistics.bootstrap, p_value).

    p = (1 + #draws <= -margin) / (1 + #draws). ``scored=False`` (or no table) returns {'status': 'not run'}
    and an empty table {'status': 'no days'}, in both cases without calling any metrics function.
    """
    if not scored or per_day_df is None:
        return {"status": NOT_RUN, "arm": arm, "ref": ref}
    table = _two(per_day_df, arm, ref)
    if table.empty:
        return {"status": NO_DAYS, "arm": arm, "ref": ref}
    days, err_a, err_r, n = _checked(table, arm, ref)
    what = f"{arm} vs {ref}"
    skill = _skill(err_a.sum(), err_r.sum(), what)
    try:
        boot = metrics.bootstrap_skill(table, model=arm, reference=ref, block_days=BLOCK_DAYS, samples=SAMPLES,
                                       seed=SEED, return_draws=True)
    except ZeroDivisionError as exc:
        raise StatisticsError(f"non-finite bootstrap draw for {what}") from exc
    draws = np.asarray(boot["draws"], dtype="float64")
    if not np.isfinite(draws).all():
        raise StatisticsError(f"non-finite bootstrap draw for {what}")
    lo, hi = np.percentile(draws, [2.5, 97.5])
    m = -float(margin)
    daily_a, daily_r = err_a / n, err_r / n
    return {"status": "ok", "arm": arm, "ref": ref, "skill": skill, "ci95": [float(lo), float(hi)],
            "p_one_sided": float((1 + np.sum(draws <= m)) / (1 + len(draws))), "margin": float(margin), "m": m,
            "days": int(len(days)), "hours": int(n.sum()),
            "loss_arm": float(err_a.sum() / n.sum()), "loss_ref": float(err_r.sum() / n.sum()),
            "days_won": int(np.sum(daily_a < daily_r)), "days_lost": int(np.sum(daily_a > daily_r))}


def _year_of(per_day_df: pd.DataFrame) -> np.ndarray:
    return np.array([_to_date(d).year for d in per_day_df["delivery_date"]], dtype=int)


def yearly(per_day_df: pd.DataFrame | None, arm: str, ref: str, *, years: Iterable[str] = TEST_YEARS,
           scored: bool = True) -> dict:
    """statistics.per_year_rule: the pooled-sum skill over the day set restricted to the Paris delivery days of
    each year (no bootstrap, no p); 'no days' for a year without a day (which fails the rule)."""
    years = [str(y) for y in years]
    if not scored or per_day_df is None:
        return {y: NOT_RUN for y in years}
    table = _two(per_day_df, arm, ref)
    year = _year_of(table) if len(table) else np.array([], dtype=int)
    out = {}
    for y in years:
        sub = table.loc[year == int(y)]
        out[y] = NO_DAYS if sub.empty else pooled_skill(sub, arm, ref)
    return out


def coverage(df: pd.DataFrame, arm: str, days: Iterable) -> float | str:
    """P3: the share of the scored hours of ``days`` with q10 <= y <= q90 (closed; the arm's own q10 and q90,
    unclipped and unsorted; both hours of a repeated autumn hour count). 'no days' if ``days`` is empty."""
    wanted = {_to_date(d) for d in days}
    if not wanted:
        return NO_DAYS
    rows = df.loc[(df["method"] == arm).to_numpy() & _dates(df["delivery_date"]).isin(wanted).to_numpy()]
    if rows.empty:
        return NO_DAYS
    y, lo, hi = (rows[c].to_numpy(dtype="float64") for c in ("y", "q10", "q90"))
    if not (np.isfinite(y).all() and np.isfinite(lo).all() and np.isfinite(hi).all()):
        raise StatisticsError(f"{arm}: coverage asked on hours that are not finite (outside its day set)")
    return float(np.mean((lo <= y) & (y <= hi)))


def rmse(df: pd.DataFrame, arm: str, days: Iterable) -> float | str:
    """Report-only RMSE of ``arm`` over every scored hour of ``days``."""
    wanted = {_to_date(d) for d in days}
    rows = df.loc[(df["method"] == arm).to_numpy() & _dates(df["delivery_date"]).isin(wanted).to_numpy()]
    if rows.empty:
        return NO_DAYS
    err = rows["y"].to_numpy(dtype="float64") - rows["y_hat"].to_numpy(dtype="float64")
    if not np.isfinite(err).all():
        raise StatisticsError(f"{arm}: RMSE asked on hours that are not finite")
    return float(np.sqrt(np.mean(err ** 2)))


def comparison(df: pd.DataFrame, arm: str, ref: str, *, metric: str, allowed_days: Iterable | None,
               scored: Iterable[str], margin: float = 0.0, k1_passed: bool | None = None,
               k3_passed: bool | None = None) -> tuple[dict, pd.DataFrame | None]:
    """One comparison end to end: day set, per-day table, compare() and yearly(). Returns (result, per-day
    table or None). Computed only if both arms were scored and the day set is non-empty; 'not run' only for an
    arm a failed gate left unscored (``unscored``: any other missing arm raises ValueError)."""
    causes = unscored((arm, ref), scored, k1_passed=k1_passed, k3_passed=k3_passed)
    if causes:
        res = compare(None, arm, ref, margin=margin, scored=False)
        res.update({"metric": metric, "yearly": yearly(None, arm, ref, scored=False), "cause": "; ".join(causes)})
        return res, None
    days = day_set(df, arm, ref, metric=metric, allowed_days=allowed_days)
    table = per_day(df, arm, ref, metric=metric, days=days) if days else None
    if table is None:
        return {"status": NO_DAYS, "arm": arm, "ref": ref, "metric": metric,
                "yearly": {y: NO_DAYS for y in TEST_YEARS}}, None
    res = compare(table, arm, ref, margin=margin)
    res.update({"metric": metric, "yearly": yearly(table, arm, ref)})
    return res, table


# ------------------------------------------------------------------------------ verdicts


def _runnable(pid: str, r: Mapping) -> tuple[bool, str | None]:
    flag = bool(r.get("runnable", True))
    skill = r.get("skill")
    cause = r.get("cause")
    if pid in ("P1", "P3"):
        if not flag:
            raise ValueError(f"{pid} is never 'not runnable' (statistics.verdict_states)")
        return True, None
    if pid == "P2" and skill == NOT_RUN:
        return False, cause or "lear_ens was not scored (K1 failed)"
    if pid == "P4" and skill in (NOT_RUN, NO_DAYS):
        return False, cause or ("t0_cal_wx was not scored (K3 failed)" if skill == NOT_RUN else "no P4 day scored")
    return flag, (cause if not flag else None)


def _state(pid: str, r: Mapping, runnable: bool, p_holm: float) -> str:
    if not runnable:
        return "not runnable"
    thr = THRESHOLDS[pid]
    skill = r.get("skill")
    if not _num(skill) or not skill > thr or not p_holm < ALPHA:
        return "lost"
    year = r.get("yearly") or {}
    if any(not _num(year.get(y)) or not year[y] > thr for y in TEST_YEARS):
        return "not stable"
    if pid == "P3":
        cov = r.get("coverage")
        if not _num(cov):
            raise ValueError("P3 passes on pinball but has no pooled coverage")
        lo, hi = COVERAGE_BAND
        if not lo <= cov <= hi:
            return "lost on coverage"
    return "won"


def states(results: Mapping[str, Mapping]) -> dict:
    """statistics.verdict_states and each probe's success rule.

    ``results[pid]`` holds ``runnable`` (bool; P2: K1 passed and p2_coverage >= 0.95; P4: K3 passed and a P4
    day scored), ``skill``, ``p`` (raw one-sided p), ``yearly`` ({'2024': .., '2025': ..}), ``coverage`` (P3)
    and optionally ``ci95`` and ``cause``; uncomputed fields hold 'not run' / 'no days'. Holm
    (run_covariates.holm) runs over P1..P4 at alpha 0.05, a not-runnable primary (or one whose p was not
    computed) entering with p = 1. Returns {pid: {'state', 'p_holm', 'p_holm_input', 'p', 'threshold',
    'ci95', 'cause'}}.
    """
    from run_covariates import holm

    missing = [pid for pid in FAMILY if pid not in results]
    if missing:
        raise ValueError(f"no result for {missing}")
    run = {pid: _runnable(pid, results[pid]) for pid in FAMILY}
    p_in = [float(results[pid]["p"]) if run[pid][0] and _num(results[pid].get("p")) else 1.0 for pid in FAMILY]
    adjusted = holm(p_in)
    out = {}
    for pid, p, h in zip(FAMILY, p_in, adjusted):
        r = results[pid]
        runnable, cause = run[pid]
        out[pid] = {"state": _state(pid, r, runnable, float(h)), "p_holm": float(h), "p_holm_input": p,
                    "p": r.get("p"), "threshold": THRESHOLDS[pid], "ci95": r.get("ci95"), "cause": cause}
    return out


# ------------------------------------------------------------------------------ the reading table


def _state_of(value) -> str:
    return value["state"] if isinstance(value, Mapping) else value


def beats(entry: Mapping | None) -> bool:
    """reading_table.strict: 'beats' = the point MAE skill is > 0 pooled, in 2024 and in 2025."""
    if not entry:
        return False
    return all(_num(entry.get(k)) and entry[k] > 0 for k in ("pooled", *TEST_YEARS))


def _interval_below_zero(ci) -> bool:
    return (isinstance(ci, (list, tuple)) and len(ci) == 2 and all(_num(c) for c in ci)
            and ci[0] < 0 and ci[1] < 0)


def _p1p2_row(p1: str, p2: str, p1_ci95) -> str:
    if p1 == "won":
        if p2 == "won":
            return RT["P1 won, P2 won"]
        if p2 in ("lost", "not stable"):
            return RT["P1 won, P2 lost or not stable"]
        return RT["P1 won, P2 not runnable"]
    if p2 == "won":
        return RT["P1 not won, P2 won"]
    parts = [NOT_WON_BASE]
    if p2 == "not runnable":
        parts.append(NOT_WON_ADD_LEAR)
    if _interval_below_zero(p1_ci95):
        parts.append(NOT_WON_ADD_INTERVAL)
    return " ".join(parts)


def strict_row(p1_state: str, strict: Mapping | None) -> str:
    """reading_table.strict: the sentence its rule selects (read only when P1 is 'won')."""
    if p1_state != "won":
        return STRICT_NOT_READ
    if strict is None:
        raise ValueError("P1 is won: the strict row needs t0_cal_strict's skills (strict_skills)")
    if beats(strict.get("best_simple_2023")):
        return STRICT_NO_ALLOWANCE
    if beats(strict.get("best_simple_2023_strict")):
        return STRICT_OLD_RULE
    return STRICT_DEPENDS


def reading(states: Mapping, strict: Mapping | None = None, *, p1_ci95=None) -> list[str]:
    """The reading-table rows printed, verbatim, following reading_table.printing: one P1/P2 row, one P3 row,
    one P4 row, the 'not stable' row for each primary in that state (``<probe>`` substituted), then the strict
    row. ``states`` maps each primary to its state (or to states()'s dict). The 'P1 not won, P2 not won' row is
    printed as its first sentence plus the quoted additions its own text calls for (P1's interval is taken from
    ``p1_ci95`` or states['P1']['ci95'])."""
    st = {pid: _state_of(states[pid]) for pid in FAMILY}
    for pid, s in st.items():
        if s not in STATE_NAMES[pid]:
            raise ValueError(f"{pid} cannot be in state {s!r}")
    if p1_ci95 is None and isinstance(states["P1"], Mapping):
        p1_ci95 = states["P1"].get("ci95")
    rows = [_p1p2_row(st["P1"], st["P2"], p1_ci95),
            RT["P3 won"] if st["P3"] == "won" else RT["P3 lost on coverage"] if st["P3"] == "lost on coverage"
            else RT["P3 lost or not stable"],
            RT["P4 won"] if st["P4"] == "won" else RT["P4 not runnable"] if st["P4"] == "not runnable"
            else RT["P4 lost or not stable"]]
    rows += [RT["not stable"].replace("<probe>", pid) for pid in FAMILY if st[pid] == "not stable"]
    rows.append(strict_row(st["P1"], strict))
    return rows


def status_line() -> str:
    """The line summary.md opens with (reading_table.printing)."""
    return f"Status: {SPEC['status']}"


def _fmt(v, digits: int = 4) -> str:
    if v is None:
        return NOT_RUN
    if isinstance(v, str):
        return v
    if isinstance(v, (int, np.integer)) and not isinstance(v, bool):
        return str(int(v))
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x, digits) for x in v) + "]"
    if _num(v):
        return f"{float(v):.{digits}f}"
    return str(v)


def probe_numbers(pid: str, r: Mapping, v: Mapping) -> str:
    """The numbers printed beside a probe's row: pooled skill, 95% interval, raw p, Holm p, yearly skills
    (P3: coverage pooled and per year; a not-runnable primary: its cause)."""
    arm, ref, metric = probe_arms(pid)
    year = r.get("yearly") or {}
    parts = [f"{pid} ({arm} vs {ref}, {'pinball' if metric == 'pinball' else 'MAE'} skill): state '{v['state']}'",
             f"pooled skill {_fmt(r.get('skill'))}", f"95% interval {_fmt(r.get('ci95'))}",
             f"raw p {_fmt(r.get('p'))}", f"Holm p {_fmt(v['p_holm'])}",
             *(f"{y} {_fmt(year.get(y, NO_DAYS))}" for y in TEST_YEARS), f"days {_fmt(r.get('days'))}"]
    if pid == "P3":
        cy = r.get("coverage_yearly") or {}
        parts.append(f"coverage {_fmt(r.get('coverage'))} (" + ", ".join(
            f"{y} {_fmt(cy.get(y, NO_DAYS))}" for y in TEST_YEARS) + ")")
    if v.get("cause"):
        parts.append(f"cause: {v['cause']}")
    return "; ".join(parts)


def strict_numbers(strict: Mapping | None) -> str:
    out = []
    for ref in STRICT_COMPARATORS:
        e = (strict or {}).get(ref) or {}
        out.append(f"{STRICT_ARM} vs {ref}: pooled {_fmt(e.get('pooled', NOT_RUN))}, " + ", ".join(
            f"{y} {_fmt(e.get(y, NOT_RUN))}" for y in TEST_YEARS))
    return "; ".join(out)


def summary_lines(results: Mapping[str, Mapping], verdicts: Mapping[str, Mapping],
                  strict: Mapping | None = None) -> list[str]:
    """reading_table.printing as markdown lines: the status line, then each row verbatim with its probes'
    numbers beside it, the 'not stable' rows, the strict row with its six skills, and the attribution."""
    rows = reading(verdicts, strict)
    lines = [status_line(), ""]
    beside = [("P1", "P2"), ("P3",), ("P4",)]
    for row, pids in zip(rows[:3], beside):
        lines.append(f"- {row}")
        lines += [f"  - {probe_numbers(pid, results[pid], verdicts[pid])}" for pid in pids]
    for row in rows[3:-1]:
        lines.append(f"- {row}")
    lines.append(f"- {rows[-1]}")
    lines.append(f"  - {strict_numbers(strict)}")
    lines += ["", ps.ATTRIBUTION]
    return lines


# ------------------------------------------------------------------------------ the primaries end to end


def scored_arms(df: pd.DataFrame, *, k1_passed: bool, k3_passed: bool, scored: Iterable[str] | None = None
                ) -> set[str]:
    """The arms scored (statistics.day_sets): those in ``df`` (or ``scored``); lear_ens and its bands exactly when
    K1 passed, t0_cal_wx exactly when K3 passed. A gated arm whose gate passed is scored even with no row in
    ``df`` (the runner adds no t0_cal_wx row when no day passes weather_p4.day_rule): its comparisons then read
    'no days', never 'not run'."""
    arms = set(df["method"]) if scored is None else set(scored)
    for arm, gate in GATED_ARMS.items():
        if _gate_passed(gate, k1_passed, k3_passed):
            arms.add(arm)
        else:
            arms.discard(arm)
    return arms


def primary_results(df: pd.DataFrame, *, k1_passed: bool, k3_passed: bool, p4_rule_days: Iterable | None,
                    scored: Iterable[str] | None = None, test_days: Iterable | None = None
                    ) -> tuple[dict, dict]:
    """Every primary's comparison on its own day set, the input states() reads, and the per-day tables.

    ``p4_rule_days``: the days passing weather_p4.day_rule (required once t0_cal_wx is scored); P4's days are
    those within periods.p4_days from AVAIL.p4_first_day. Returns (results, per-day tables by probe).
    """
    arms = scored_arms(df, k1_passed=k1_passed, k3_passed=k3_passed, scored=scored)
    test = period_days("test") if test_days is None else sorted({_to_date(d) for d in test_days})
    if "t0_cal_wx" in arms and p4_rule_days is None:
        raise ValueError("t0_cal_wx is scored: P4's day set needs the days passing weather_p4.day_rule")
    p4 = p4_allowed_days(p4_rule_days or [])
    results, tables = {}, {}
    for pid in FAMILY:
        arm, ref, metric = probe_arms(pid)
        res, table = comparison(df, arm, ref, metric=metric, allowed_days=p4 if pid == "P4" else test,
                                scored=arms, margin=MARGINS[pid], k1_passed=k1_passed, k3_passed=k3_passed)
        status = res["status"]
        r = {"arm": arm, "ref": ref, "metric": metric, "status": status,
             "skill": res.get("skill", status), "ci95": res.get("ci95", status), "p": res.get("p_one_sided", status),
             "yearly": res["yearly"], "days": res.get("days", status), "compare": res,
             "runnable": True, "cause": None}
        if pid == "P2":
            complete = complete_days(df, test)
            share = NOT_RUN if ref not in arms else p2_coverage(df, complete, arm=ref) if complete else NO_DAYS
            r["p2_coverage"] = share
            if not k1_passed:
                r.update(runnable=False, cause="K1 failed")
            elif not (_num(share) and share >= P2_COVERAGE_MIN):
                r.update(runnable=False, cause=f"p2_coverage {_fmt(share)} < {P2_COVERAGE_MIN}")
        if pid == "P4":
            if not k3_passed:
                r.update(runnable=False, cause="K3 failed")
            elif status == NO_DAYS:  # K3 passed, so t0_cal_wx is scored ('not run' is impossible here)
                r.update(runnable=False, cause="no P4 day scored")
        if pid == "P3":
            days = [] if table is None else sorted(set(table["delivery_date"]))
            if table is None:
                r["coverage"], r["coverage_yearly"] = status, {y: status for y in TEST_YEARS}
            else:
                r["coverage"] = coverage(df, arm, days)
                r["coverage_yearly"] = {y: coverage(df, arm, [d for d in days if d.year == int(y)])
                                        for y in TEST_YEARS}
        results[pid], tables[pid] = r, table
    return results, tables


def strict_skills(df: pd.DataFrame, *, scored: Iterable[str] | None = None, test_days: Iterable | None = None
                  ) -> dict:
    """reading_table.strict: point MAE skill of t0_cal_strict vs each strict comparator, pooled and in each year
    alone, each on its own strict_arm.days (no interval, no p)."""
    arms = set(df["method"]) if scored is None else set(scored)
    test = period_days("test") if test_days is None else test_days
    out = {}
    for ref in STRICT_COMPARATORS:
        unscored((STRICT_ARM, ref), arms)  # no gate applies: a missing strict arm is an error, never 'not run'
        days = day_set(df, STRICT_ARM, ref, metric="mae", allowed_days=test)
        if not days:
            out[ref] = {"pooled": NO_DAYS, **{y: NO_DAYS for y in TEST_YEARS}, "days": 0}
            continue
        table = per_day(df, STRICT_ARM, ref, metric="mae", days=days)
        out[ref] = {"pooled": pooled_skill(table, STRICT_ARM, ref), **yearly(table, STRICT_ARM, ref),
                    "days": len(days)}
    return out


# ------------------------------------------------------------------------------ report only


def hour_slices(df: pd.DataFrame, days: Iterable) -> dict[str, pd.Series]:
    """The hour slices of report_only.slices as boolean row masks over ``df`` (rows outside ``days`` are False):
    'negative-price hours' (y < 0); 'top 1% absolute prices' (|y| >= numpy.quantile(|y|, 0.99), default linear,
    over every scored hour of the day set, each UTC hour once); '11:00-16:00 local' (hours starting 11:00 to
    15:00 Europe/Paris)."""
    wanted = {_to_date(d) for d in days}
    in_days = _dates(df["delivery_date"]).isin(wanted).to_numpy()
    y = df["y"].to_numpy(dtype="float64")
    if not np.isfinite(y[in_days]).all():
        raise StatisticsError("hour slices asked on days whose target is not complete")
    hours = df.loc[in_days, ["target_time", "y"]]
    if hours.groupby("target_time")["y"].nunique().gt(1).any():
        raise StatisticsError("two rows carry different targets for the same hour")
    unique_y = hours.drop_duplicates("target_time")["y"].to_numpy(dtype="float64")
    threshold = float(np.quantile(np.abs(unique_y), TOP_QUANTILE)) if len(unique_y) else np.inf
    local_hour = pd.DatetimeIndex(df["target_time"]).tz_convert(zones.PARIS).hour.to_numpy()
    masks = {SLICE_NEGATIVE: in_days & (y < 0),
             SLICE_TOP: in_days & (np.abs(y) >= threshold),
             SLICE_MIDDAY: in_days & np.isin(local_hour, list(MIDDAY_HOURS))}
    return {k: pd.Series(v, index=df.index, name=k) for k, v in masks.items()}


def weekend_holiday_days(days: Iterable) -> list[date]:
    """Saturdays, Sundays and French public holidays (solarbench.probes.french_holidays) among ``days``."""
    out = []
    for d in sorted({_to_date(x) for x in days}):
        if d.weekday() >= 5 or d in pr.french_holidays(d.year):
            out.append(d)
    return out


def dst_week_days(days: Iterable, *, switches: Iterable | None = None) -> list[date]:
    """The days among ``days`` in the week after a DST switch: the switch day (23 or 25 hours) and the six days
    after it. ``switches`` defaults to the switch days of the test period."""
    days = {_to_date(x) for x in days}
    sw = dst_switch_days(period_days("test")) if switches is None else [_to_date(s) for s in switches]
    week = {s + timedelta(days=k) for s in sw for k in range(DST_WEEK_DAYS)}
    return sorted(days & week)


def _restrict(table: pd.DataFrame, keep: Callable[[date], bool]) -> pd.DataFrame:
    if table.empty:
        return table
    return table.loc[[keep(_to_date(d)) for d in table["delivery_date"]]]


def _year_slice(table: pd.DataFrame, arm: str, ref: str) -> dict:
    """The 'each year' slice: statistics.per_year_rule's per-year skill only (no per-year bootstrap or p)."""
    year = _year_of(table) if len(table) else np.array([], dtype=int)
    out = {}
    for y, v in yearly(table, arm, ref).items():
        out[y] = ({"status": "ok", "arm": arm, "ref": ref, "skill": v,
                   "days": int(table.loc[year == int(y), "delivery_date"].nunique())} if _num(v)
                  else {"status": v, "arm": arm, "ref": ref})
    return out


def slices(df: pd.DataFrame, arm: str, ref: str, *, metric: str, days: Iterable | None, margin: float = 0.0,
           scored: bool = True) -> dict:
    """report_only.slices for one comparison on its own days (or hours) of the comparison's day set ``days``:
    each year (its per-year skill only: statistics.per_year_rule has no per-year bootstrap or p), and by
    compare() each quarter, April-September, weekends and holidays, the weeks after each DST switch, and the
    three hour slices. Every slice not computed reads 'not run' / 'no days'."""
    quarters = [f"{y}Q{q}" for y in TEST_YEARS for q in range(1, 5)]
    names = [SLICE_APR_SEP, SLICE_WEEKEND, SLICE_DST, *HOUR_SLICES]
    if not scored or days is None:
        empty = {"status": NOT_RUN, "arm": arm, "ref": ref}
        return {SLICE_YEAR: {y: dict(empty) for y in TEST_YEARS}, SLICE_QUARTER: {q: dict(empty) for q in quarters},
                **{k: dict(empty) for k in names}}
    days = sorted({_to_date(d) for d in days})
    table = per_day(df, arm, ref, metric=metric, days=days)
    weekend, dst = set(weekend_holiday_days(days)), set(dst_week_days(days))
    out = {SLICE_YEAR: _year_slice(table, arm, ref),
           SLICE_QUARTER: {q: compare(_restrict(table, lambda d, q=q: d.year == int(q[:4])
                                                and (d.month - 1) // 3 + 1 == int(q[-1])), arm, ref, margin=margin)
                           for q in quarters},
           SLICE_APR_SEP: compare(_restrict(table, lambda d: d.month in CARRY_MONTHS), arm, ref, margin=margin),
           SLICE_WEEKEND: compare(_restrict(table, lambda d: d in weekend), arm, ref, margin=margin),
           SLICE_DST: compare(_restrict(table, lambda d: d in dst), arm, ref, margin=margin)}
    for name, mask in hour_slices(df, days).items():
        out[name] = compare(per_day(df, arm, ref, metric=metric, days=days, hours=mask), arm, ref, margin=margin)
    return out


def tables(per_day_df: pd.DataFrame | None, arm: str, ref: str, *, scored: bool = True) -> dict:
    """report_only.tables: concentration (metrics.concentration) and the block-length table
    (metrics.bootstrap_sensitivity at 1, 3, 7, 14, 30 days) on the comparison's per-day table."""
    if not scored or per_day_df is None:
        return {"status": NOT_RUN}
    table = _two(per_day_df, arm, ref)
    if table.empty:
        return {"status": NO_DAYS}
    _, err_a, err_r, _ = _checked(table, arm, ref)
    what = f"{arm} vs {ref}"
    _skill(err_a.sum(), err_r.sum(), what)  # a non-finite pooled skill stops the run before any table
    try:  # a resample (or a day subset) with zero reference loss: a non-finite skill or draw stops the run
        conc = metrics.concentration(table, model=arm, reference=ref)
        sens = metrics.bootstrap_sensitivity(table, model=arm, reference=ref, blocks=SENSITIVITY_BLOCKS,
                                             samples=SAMPLES, seed=SEED)
    except ZeroDivisionError as exc:
        raise StatisticsError(f"non-finite skill or bootstrap draw in the report-only tables for {what}") from exc
    for row in sens:
        if not all(np.isfinite(row[k]) for k in ("skill", "skill_lo95", "skill_hi95")):
            raise StatisticsError(f"non-finite block-length table row for {what}: {row}")
    return {"status": "ok", "concentration": conc, "bootstrap_sensitivity": sens}


def rmae(df: pd.DataFrame, arm: str, ref: str, *, allowed_days: Iterable | None, scored: Iterable[str],
         k1_passed: bool | None = None, k3_passed: bool | None = None) -> dict:
    """Report-only rMAE = MAE(arm) / MAE(ref) pooled over their day set (= 1 - skill; no interval, no p). 'not
    run' only for an arm a failed gate left unscored (``unscored``: any other missing arm raises ValueError)."""
    causes = unscored((arm, ref), scored, k1_passed=k1_passed, k3_passed=k3_passed)
    if causes:
        return {"status": NOT_RUN, "cause": "; ".join(causes)}
    days = day_set(df, arm, ref, metric="mae", allowed_days=allowed_days)
    if not days:
        return {"status": NO_DAYS}
    _, err_a, err_r, _ = _checked(per_day(df, arm, ref, metric="mae", days=days), arm, ref)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.float64(err_a.sum()) / np.float64(err_r.sum())
    if not np.isfinite(ratio):
        raise StatisticsError(f"non-finite rMAE for {arm} vs {ref}")
    return {"status": "ok", "rmae": float(ratio), "days": len(days)}


def secondaries(df: pd.DataFrame, *, scored: Iterable[str], k1_passed: bool | None = None,
                k3_passed: bool | None = None, test_days: Iterable | None = None,
                p4_rule_days: Iterable | None = None, rmae_refs: Mapping[str, str] | None = None) -> dict:
    """report_only.secondaries, keyed by their spec text: the eight comparisons (compare() and yearly() on their
    own day sets within the test period), rMAE of every point arm vs naive_std and vs prev_week, and the RMSE of
    both arms of each point-metric primary on that primary's day set. Nothing here changes a state.

    ``scored`` is scored_arms(df, k1_passed=..., k3_passed=...) and the gate outcomes are passed as well: only an
    arm their failure left unscored prints 'not run'; any other arm missing from ``scored`` raises ValueError.
    ``rmae_refs`` maps each rMAE reference's spec name ('naive_std', 'prev_week') to its arm name in ``df``
    (default: the same names); the rMAE table stays keyed by the spec names."""
    arms = set(scored)
    gates = {"k1_passed": k1_passed, "k3_passed": k3_passed}
    refs = dict(RMAE_REFS if rmae_refs is None else rmae_refs)
    if set(refs) != set(RMAE_REFS):
        raise ValueError(f"rmae_refs must map exactly {sorted(RMAE_REFS)} to arm names, got {sorted(refs)}")
    test = period_days("test") if test_days is None else sorted({_to_date(d) for d in test_days})
    if p4_rule_days is None and k3_passed is not False and "t0_cal_wx" in arms:
        raise ValueError("t0_cal_wx is scored: its day sets need the days passing weather_p4.day_rule")
    p4 = p4_allowed_days(p4_rule_days or [])

    def allowed(a: str, b: str) -> list[date]:
        return p4 if "t0_cal_wx" in (a, b) else test

    out: dict = {}
    for key, (a, b, metric) in SECONDARY_PAIRS.items():
        out[key], _ = comparison(df, a, b, metric=metric, allowed_days=allowed(a, b), scored=arms, **gates)
    # every point arm: the scored ones, and the gated ones a failed gate left unscored (printed 'not run')
    gated_off = {a for a, g in GATED_ARMS.items() if _gate_passed(g, k1_passed, k3_passed) is False}
    point_arms = sorted((arms | gated_off) - {LEAR_BANDS})
    out[RMAE_KEY] = {name: {a: rmae(df, a, ref, allowed_days=allowed(a, ref), scored=arms, **gates)
                            for a in point_arms if a != ref} for name, ref in refs.items()}
    out[RMSE_KEY] = {}
    for pid in FAMILY:
        a, b, metric = probe_arms(pid)
        if metric != "mae":
            continue
        causes = unscored((a, b), arms, **gates)
        if causes:
            out[RMSE_KEY][pid] = {"status": NOT_RUN, "cause": "; ".join(causes)}
            continue
        days = day_set(df, a, b, metric="mae", allowed_days=p4 if pid == "P4" else test)
        out[RMSE_KEY][pid] = ({"status": "ok", a: rmse(df, a, days), b: rmse(df, b, days), "days": len(days)}
                              if days else {"status": NO_DAYS})
    return out


# ------------------------------------------------------------------------------ toward confirmation


def carry_forward(per_day_df: pd.DataFrame | None, arm: str, ref: str,
                  skill_fn: Callable[[pd.DataFrame, str, str], float] | None = None, *,
                  state: str | None = None) -> dict:
    """PRICE_SPEC['carry_forward']['rule'].

    A = the per-day table of the primary (its own day set) restricted to Paris delivery dates in April-September
    of 2024 or 2025; S = ``skill_fn(A, arm, ref)`` (default: the pooled-sum skill); M =
    engine.referee.stats.power_table(A, arm, ref, alpha=0.0125)['min_detectable_skill']['12']; delta = the
    largest of {0, 0.05, 0.10, 0.20} with S - delta >= M. A vault candidate only if ``state`` is 'won' and such a
    delta exists (``state`` None is never a candidate). S, M, A's day count, block_sd and ref_mae are returned,
    and M at alpha 0.0125/2, /3 and /4 for information only. A candidate is not a confirmation.
    """
    out: dict = {"arm": arm, "ref": ref, "state": state, "candidate": False, "delta": None}
    if per_day_df is None:
        out["status"] = NOT_RUN
        return out
    table = _two(per_day_df, arm, ref)
    a = _restrict(table, lambda d: d.month in CARRY_MONTHS and d.year in CARRY_YEARS)
    if a.empty:
        out.update(status=NO_DAYS, days=0)
        return out
    _checked(a, arm, ref)
    s = float((skill_fn or pooled_skill)(a, arm, ref))
    if not math.isfinite(s):
        raise StatisticsError(f"non-finite carry-forward skill for {arm} vs {ref}")
    power = referee_stats.power_table(a, arm, ref, alpha=CARRY_ALPHA)
    out.update(status="ok", S=s, days=int(a["delivery_date"].nunique()))
    if "error" in power:
        out.update(M=None, block_sd=None, ref_mae=None, power_error=power["error"],
                   M_info={f"{CARRY_ALPHA}/{k}": None for k in (2, 3, 4)})
        return out
    m = float(power["min_detectable_skill"][CARRY_BLOCKS])
    info = {}
    for k in (2, 3, 4):
        extra = referee_stats.power_table(a, arm, ref, alpha=CARRY_ALPHA / k)
        info[f"{CARRY_ALPHA}/{k}"] = extra["min_detectable_skill"][CARRY_BLOCKS]
    passing = [d for d in CARRY_DELTAS if s - d >= m]
    delta = max(passing) if passing else None
    out.update(M=m, block_sd=power["block_sd_mw"], ref_mae=power["ref_mae_mw"], M_info=info, delta=delta,
               candidate=bool(state == "won" and delta is not None))
    return out


def carry_forward_all(tables_by_probe: Mapping[str, pd.DataFrame | None], verdicts: Mapping[str, Mapping]) -> dict:
    """carry_forward for every primary, with its own arms, per-day table and state."""
    out = {}
    for pid in FAMILY:
        arm, ref, _ = probe_arms(pid)
        out[pid] = carry_forward(tables_by_probe.get(pid), arm, ref, state=_state_of(verdicts[pid]))
    return out
