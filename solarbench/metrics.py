"""Error metrics, skill scores and their uncertainty.

Normalised MAE is always computed as a ratio of sums, never as a mean of
per-point ratios: solar generation is zero for half of every day, so per-point
ratios are undefined at night and explode at dawn.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: A half-hour slot counts as daytime if its historical mean generation clears
#: this fraction of the peak proxy.
DAYTIME_THRESHOLD = 0.01
BOOTSTRAP_BLOCK_DAYS = 7
BOOTSTRAP_SAMPLES = 2000


def peak_proxy(y: np.ndarray | pd.Series, quantile: float = 0.99) -> float:
    """Capacity stand-in: a high quantile of observed generation.

    The 99th percentile rather than the maximum, which is a single half-hour and
    swings year to year.  This is a reporting scale only — no model sees it.
    """
    return float(np.quantile(np.asarray(y, dtype="float64"), quantile))


def daytime_slots(history: pd.Series, *, tz: str, threshold: float = DAYTIME_THRESHOLD) -> set[tuple[int, int]]:
    """Daytime ``(month, half-hour slot)`` pairs, learned from history alone.

    Derived from data strictly before the test period, so the mask never sees a
    value it is used to score.  Using generation climatology rather than solar
    geometry keeps the benchmark free of any astronomical input as well.
    """
    local = history.index.tz_convert(tz)
    frame = pd.DataFrame(
        {
            "y": history.to_numpy(dtype="float64"),
            "month": local.month,
            "slot": local.hour * 2 + (local.minute // 30),
        }
    ).dropna()
    if frame.empty:
        raise ValueError("no history available to derive the daytime mask")
    cutoff = threshold * peak_proxy(frame["y"])
    means = frame.groupby(["month", "slot"])["y"].mean()
    return {(int(m), int(s)) for (m, s), v in means.items() if v > cutoff}


def add_daytime_flag(df: pd.DataFrame, slots: set[tuple[int, int]]) -> pd.DataFrame:
    out = df.copy()
    out["is_daytime"] = [ (m, s) in slots for m, s in zip(out["month"], out["slot"]) ]
    return out


def _pooled(group: pd.DataFrame) -> pd.Series:
    abs_err = (group["y"] - group["y_hat"]).abs()
    return pd.Series({"sum_abs_err": abs_err.sum(), "sum_y": group["y"].sum(), "n": len(group)})


def summarise(df: pd.DataFrame, *, peak: float) -> pd.DataFrame:
    """Pooled MAE and both nMAE variants, per method."""
    agg = df.groupby("method", sort=False).apply(_pooled, include_groups=False)
    out = pd.DataFrame(
        {
            "n_points": agg["n"].astype(int),
            "mae_mw": agg["sum_abs_err"] / agg["n"],
            "nmae_mean": agg["sum_abs_err"] / agg["sum_y"],
            "nmae_peak": (agg["sum_abs_err"] / agg["n"]) / peak,
        }
    )
    return out.reset_index()


def per_day_errors(df: pd.DataFrame) -> pd.DataFrame:
    """Per delivery day and method: absolute-error sum, point count, actual sum."""
    grouped = df.groupby(["delivery_date", "method"], sort=True).apply(_pooled, include_groups=False)
    out = grouped.reset_index()
    out["mae_mw"] = out["sum_abs_err"] / out["n"]
    return out


def skill_score(mae_model: float, mae_reference: float) -> float:
    """Relative improvement: the share of the reference's MAE that is removed."""
    return 1.0 - mae_model / mae_reference


def _pooled_mae(sum_abs_err: np.ndarray, n: np.ndarray) -> float:
    return float(sum_abs_err.sum() / n.sum())


def bootstrap_skill(
    per_day: pd.DataFrame,
    *,
    model: str,
    reference: str,
    block_days: int = BOOTSTRAP_BLOCK_DAYS,
    samples: int = BOOTSTRAP_SAMPLES,
    seed: int = 0,
) -> dict:
    """Moving-block bootstrap CI for the skill of ``model`` over ``reference``.

    Blocks of whole weeks, because forecast errors on consecutive days share a
    weather regime and an i.i.d. resample would understate the uncertainty.
    Each resample recomputes the skill from pooled sums — a skill score is a
    ratio of totals, not an average of daily ratios.
    """
    wide = per_day.pivot(index="delivery_date", columns="method", values=["sum_abs_err", "n"])
    days = wide.index.to_numpy()
    if len(days) == 0:
        raise ValueError("no days to bootstrap over")

    err_m = wide[("sum_abs_err", model)].to_numpy(dtype="float64")
    err_r = wide[("sum_abs_err", reference)].to_numpy(dtype="float64")
    n_m = wide[("n", model)].to_numpy(dtype="float64")
    n_r = wide[("n", reference)].to_numpy(dtype="float64")

    point = skill_score(_pooled_mae(err_m, n_m), _pooled_mae(err_r, n_r))
    wins = float(np.mean((err_m / n_m) < (err_r / n_r)))

    rng = np.random.default_rng(seed)
    n_days = len(days)
    block = min(block_days, n_days)
    n_blocks = int(np.ceil(n_days / block))
    draws = np.empty(samples, dtype="float64")
    for i in range(samples):
        starts = rng.integers(0, n_days - block + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n_days]
        draws[i] = skill_score(_pooled_mae(err_m[idx], n_m[idx]), _pooled_mae(err_r[idx], n_r[idx]))

    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "model": model,
        "reference": reference,
        "skill": point,
        "skill_lo95": float(lo),
        "skill_hi95": float(hi),
        "win_rate": wins,
        "n_days": int(n_days),
    }


def night_forecast_diagnostic(df: pd.DataFrame) -> pd.DataFrame:
    """Mean forecast on night slots — should be ~0 MW for a sane model."""
    night = df.loc[~df["is_daytime"]]
    out = night.groupby("method", sort=False)["y_hat"].mean().rename("night_mean_forecast_mw")
    return out.reset_index()


def mae_by(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Pooled MAE and mean-normalised nMAE by an arbitrary column (slot, month...)."""
    grouped = df.groupby([key, "method"], sort=True).apply(_pooled, include_groups=False).reset_index()
    grouped["mae_mw"] = grouped["sum_abs_err"] / grouped["n"]
    grouped["nmae_mean"] = np.where(
        grouped["sum_y"] > 0, grouped["sum_abs_err"] / grouped["sum_y"], np.nan
    )
    return grouped
