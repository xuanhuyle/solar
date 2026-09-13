"""Error metrics, skill scores and their uncertainty.

Normalised MAE is always computed as a ratio of sums, never as a mean of
per-point ratios: solar generation is zero for half of every day, so per-point
ratios are undefined at night and explode at dawn.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

#: A half-hour slot counts as daytime if its historical mean generation clears
#: this fraction of the peak proxy.
log = logging.getLogger(__name__)

DAYTIME_THRESHOLD = 0.01
BOOTSTRAP_BLOCK_DAYS = 7
BOOTSTRAP_SAMPLES = 2000


def peak_proxy(y: np.ndarray | pd.Series, quantile: float = 0.99) -> float:
    """Capacity stand-in: a high quantile of observed generation.

    The 99th percentile rather than the maximum, which is a single half-hour and
    swings year to year.  This is a reporting scale only — no model sees it.
    """
    return float(np.quantile(np.asarray(y, dtype="float64"), quantile))


def daytime_slots(scored: pd.DataFrame, *, threshold: float = DAYTIME_THRESHOLD) -> set[tuple[int, int]]:
    """Daytime ``(month, half-hour slot)`` pairs, from the scored period's own actuals.

    This is a *reporting filter*: it chooses which observed rows the daytime tables
    average over, identically for every method, and is never an input to any
    forecaster — so it cannot leak anything into a forecast. Deriving it from the
    scored period rather than from prior history means it is always defined for
    every month actually being scored; a mask learned from a short history would
    mark whole calendar months as night and silently corrupt both the daytime
    tables and the night diagnostic.

    Using generation climatology rather than solar geometry also keeps the
    benchmark free of astronomical inputs.
    """
    frame = scored.loc[:, ["month", "slot", "y"]].dropna()
    if frame.empty:
        raise ValueError("no scored rows available to derive the daytime mask")
    cutoff = threshold * peak_proxy(frame["y"])
    means = frame.groupby(["month", "slot"])["y"].mean()
    slots = {(int(m), int(s)) for (m, s), v in means.items() if v > cutoff}
    uncovered = sorted({int(m) for m in frame["month"]} - {m for m, _ in slots})
    if uncovered:
        raise ValueError(
            f"month(s) {uncovered} have no daytime half-hour above {threshold:.0%} of the "
            "peak — the scored data looks wrong (all-zero or all-missing generation?)"
        )
    return slots


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
    # Keep at least two distinct block starts; otherwise every resample is the
    # identical block and the interval collapses to zero width.
    block = max(1, min(block_days, n_days // 2))
    if n_days < 2 * block_days:
        log.warning(
            "only %d delivery days: block length reduced to %d, and the bootstrap "
            "interval should be read as indicative only",
            n_days, block,
        )
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


# ------------------------------------------------------------ Phase 2 additions
#
# Everything above is untouched: the Phase 1 numbers depend on it. Below are the
# evaluation pieces the many-method comparison needs - exact sign tests, pairwise
# tables, a ranking, concentration of gains, block-length sensitivity, the D-1/D-2
# band split, and the audits that make the new methods checkable from the files.

import math
from itertools import product


def binomial_two_sided_p(wins: int, losses: int) -> float:
    """Exact two-sided sign test of ``wins`` against 50 % over ``wins + losses`` days.

    Ties are excluded before calling (they carry no information about the sign).
    Two-sided: the total probability of every outcome at least as unlikely as the
    observed count under p = 0.5. No scipy needed.
    """
    n = wins + losses
    if n == 0:
        return float("nan")
    pmf = [math.comb(n, k) / 2.0 ** n for k in range(n + 1)]
    observed = pmf[wins]
    return float(min(1.0, sum(p for p in pmf if p <= observed * (1 + 1e-12))))


def _day_pivot(per_day: pd.DataFrame, model: str, reference: str):
    wide = per_day.pivot(index="delivery_date", columns="method", values=["sum_abs_err", "n"])
    for column in (("sum_abs_err", model), ("sum_abs_err", reference), ("n", model), ("n", reference)):
        if column not in wide.columns:
            raise KeyError(f"{column[1]} has no per-day rows")
    err_m = wide[("sum_abs_err", model)].to_numpy(dtype="float64")
    err_r = wide[("sum_abs_err", reference)].to_numpy(dtype="float64")
    n_m = wide[("n", model)].to_numpy(dtype="float64")
    n_r = wide[("n", reference)].to_numpy(dtype="float64")
    if np.isnan(err_m).any() or np.isnan(err_r).any() or not np.array_equal(n_m, n_r):
        raise ValueError(f"per-day frame is not balanced between {model} and {reference}")
    return wide.index.to_numpy(), err_m, err_r, n_m


def pair_skill(
    per_day: pd.DataFrame,
    *,
    model: str,
    reference: str,
    block_days: int = BOOTSTRAP_BLOCK_DAYS,
    samples: int = BOOTSTRAP_SAMPLES,
    seed: int = 0,
) -> dict:
    """``bootstrap_skill`` plus wins / losses / ties and an exact sign-test p-value.

    The bootstrap and ``win_rate`` are exactly the Phase 1 quantities (same RNG
    path, same definition: a tie is not a win). The p-value is a sign test on
    the non-tied days only.
    """
    _day_pivot(per_day, model, reference)  # balance check, raises rather than NaN
    out = bootstrap_skill(
        per_day, model=model, reference=reference, block_days=block_days, samples=samples, seed=seed
    )
    _, err_m, err_r, n = _day_pivot(per_day, model, reference)
    daily_m, daily_r = err_m / n, err_r / n
    wins = int(np.sum(daily_m < daily_r))
    losses = int(np.sum(daily_m > daily_r))
    ties = int(np.sum(daily_m == daily_r))
    out.update(
        {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "p_value": binomial_two_sided_p(wins, losses),
            "mae_model": _pooled_mae(err_m, n),
            "mae_reference": _pooled_mae(err_r, n),
        }
    )
    return out


def pairwise_skill(
    per_day_by_slice: dict[str, pd.DataFrame],
    pairs: list[tuple[str, str, str]],
    *,
    seed: int = 0,
    block_days: int = BOOTSTRAP_BLOCK_DAYS,
    samples: int = BOOTSTRAP_SAMPLES,
) -> pd.DataFrame:
    """One row per (pair, slice). ``pairs`` are ``(model, reference, role)``."""
    rows = []
    for (model, reference, role), (slice_name, per_day) in product(pairs, per_day_by_slice.items()):
        result = pair_skill(
            per_day, model=model, reference=reference, seed=seed, block_days=block_days, samples=samples
        )
        rows.append({"role": role, "slice": slice_name, **result})
    columns = [
        "role", "model", "reference", "slice", "skill", "skill_lo95", "skill_hi95",
        "wins", "losses", "ties", "win_rate", "p_value", "n_days", "mae_model", "mae_reference",
    ]
    return pd.DataFrame(rows, columns=columns)


def ranking(
    summaries: dict[str, pd.DataFrame],
    per_day_by_slice: dict[str, pd.DataFrame],
    *,
    references: tuple[str, ...] = ("prev_day", "blend_50"),
    seed: int = 0,
) -> pd.DataFrame:
    """Every method, best to worst by all-hours MAE, with CI'd skill against each reference.

    ``summaries`` maps slice name -> ``summarise`` output; every method present
    gets a seeded block bootstrap against every reference present, both slices.
    """
    rows = []
    for slice_name, summary in summaries.items():
        per_day = per_day_by_slice[slice_name]
        methods = list(summary["method"])
        for _, r in summary.iterrows():
            row = {
                "method": r["method"], "slice": slice_name, "n_points": int(r["n_points"]),
                "mae_mw": r["mae_mw"], "nmae_mean": r["nmae_mean"], "nmae_peak": r["nmae_peak"],
            }
            for reference in references:
                prefix = f"vs_{reference}"
                if reference not in methods:
                    continue
                if r["method"] == reference:
                    row.update({f"{prefix}_skill": 0.0})
                    continue
                s = pair_skill(per_day, model=r["method"], reference=reference, seed=seed)
                row.update(
                    {
                        f"{prefix}_skill": s["skill"], f"{prefix}_lo95": s["skill_lo95"],
                        f"{prefix}_hi95": s["skill_hi95"], f"{prefix}_wins": s["wins"],
                        f"{prefix}_losses": s["losses"], f"{prefix}_ties": s["ties"],
                        f"{prefix}_win_rate": s["win_rate"], f"{prefix}_p_value": s["p_value"],
                    }
                )
            rows.append(row)
    out = pd.DataFrame(rows)
    out["rank"] = out.groupby("slice")["mae_mw"].rank(method="min").astype(int)
    return out.sort_values(["slice", "rank"]).reset_index(drop=True)


def concentration(
    per_day: pd.DataFrame, *, model: str, reference: str, top: tuple[int, ...] = (5, 10, 20)
) -> dict:
    """How much of the model's net gain over the reference sits in its best days.

    Descriptive, no interval: the share of the net absolute-error reduction
    carried by the top-N days, and the skill once those days are removed.
    """
    days, err_m, err_r, n = _day_pivot(per_day, model, reference)
    gain = err_r - err_m  # MW of absolute error removed on each day
    net = float(gain.sum())
    order = np.argsort(-gain)
    out = {"model": model, "reference": reference, "net_gain_mw": net, "n_days": int(len(days)),
           "skill": skill_score(_pooled_mae(err_m, n), _pooled_mae(err_r, n))}
    for k in top:
        keep = np.ones(len(days), dtype=bool)
        keep[order[:k]] = False
        out[f"top{k}_share_of_net_gain"] = float(gain[order[:k]].sum() / net) if net != 0 else float("nan")
        out[f"skill_without_top{k}"] = skill_score(_pooled_mae(err_m[keep], n[keep]), _pooled_mae(err_r[keep], n[keep]))
    return out


def bootstrap_sensitivity(
    per_day: pd.DataFrame, *, model: str, reference: str, blocks: tuple[int, ...] = (1, 3, 7, 14, 30),
    samples: int = BOOTSTRAP_SAMPLES, seed: int = 0,
) -> list[dict]:
    """The skill CI under different block lengths; the point estimate does not move."""
    out = []
    for block in blocks:
        s = bootstrap_skill(per_day, model=model, reference=reference, block_days=block, samples=samples, seed=seed)
        out.append({"model": model, "reference": reference, "block_days": block,
                    "skill": s["skill"], "skill_lo95": s["skill_lo95"], "skill_hi95": s["skill_hi95"]})
    return out


def add_band_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Split the delivery day by whether a D-1 same-slot source exists at the gate.

    A target ``step`` <= 48 lies within 24 h of the origin, so ``target - 24 h``
    is at or before it and the previous-day baseline holds a 24-hour-old copy;
    beyond that it holds a 48-hour-old one. Defined in steps, so it is right on
    the DST days too, where the local-clock boundary is 13:00 / 11:00.
    """
    out = df.copy()
    out["band"] = np.where(out["step"] <= 48, "d1_source", "d2_source")
    return out


def skill_by(df: pd.DataFrame, key: str, pairs: list[tuple[str, str, str]]) -> pd.DataFrame:
    """Point skill of each pair within every value of ``key`` (month, band, ...)."""
    pooled = mae_by(df, key)
    rows = []
    for value in sorted(pooled[key].unique()):
        sub = pooled.loc[pooled[key] == value].set_index("method")
        for model, reference, role in pairs:
            if model in sub.index and reference in sub.index:
                rows.append({key: value, "model": model, "reference": reference, "role": role,
                             "mae_model": sub.loc[model, "mae_mw"], "mae_reference": sub.loc[reference, "mae_mw"],
                             "skill": skill_score(sub.loc[model, "mae_mw"], sub.loc[reference, "mae_mw"]),
                             "sum_y": sub.loc[model, "sum_y"], "n": int(sub.loc[model, "n"])})
    return pd.DataFrame(rows)


def source_audit(df: pd.DataFrame, *, blend: str | None = "blend_50",
                 components: tuple[str, str] = ("prev_day", "mean_7d")) -> pd.DataFrame:
    """Per method: are the sources where the contract says, and how old are they?"""
    hours = pd.Timedelta(hours=1)
    rows = []
    for method, sub in df.groupby("method", sort=False):
        avail = (sub["origin"] - sub["source_latest"]) / hours
        age = (sub["target_time"] - sub["source_latest"]) / hours
        oldest = (sub["target_time"] - sub["source_earliest"]) / hours
        rows.append({
            "method": method, "rows": int(len(sub)),
            "rows_after_origin": int((sub["source_latest"] > sub["origin"]).sum()),
            "avail_lag_h_min": float(avail.min()), "avail_lag_h_median": float(avail.median()), "avail_lag_h_max": float(avail.max()),
            "age_h_min": float(age.min()), "age_h_median": float(age.median()), "age_h_max": float(age.max()),
            "oldest_source_age_h_max": float(oldest.max()),
            "n_sources_min": float(sub["n_sources"].min()), "n_sources_max": float(sub["n_sources"].max()),
        })
    out = pd.DataFrame(rows)
    if blend and blend in set(df["method"]) and all(c in set(df["method"]) for c in components):
        wide = df.pivot(index=["delivery_date", "target_time"], columns="method", values="y_hat")
        recon = 0.5 * wide[components[0]] + 0.5 * wide[components[1]]
        deviation = (wide[blend] - recon).abs()
        out.loc[out["method"] == blend, "blend_postclip_rows_off"] = int((deviation > 0).sum())
        out.loc[out["method"] == blend, "blend_postclip_max_dev_mw"] = float(deviation.max())
    return out


def night_zero_audit(
    df: pd.DataFrame, *, source: str = "t0", variant: str = "t0_night_zero",
    masks: dict[str, np.ndarray], daytime_slots_used: set[tuple[int, int]],
) -> pd.DataFrame:
    """What each dark mask covers, and what it would do to the source's error.

    ``masks`` maps a label (e.g. the threshold) to a boolean array aligned with
    the source method's rows. The scored variant's own rows are also checked
    against the first mask.
    """
    src = df.loc[df["method"] == source].reset_index(drop=True)
    var = df.loc[df["method"] == variant].reset_index(drop=True) if variant in set(df["method"]) else None
    daytime = np.array([(m, s) in daytime_slots_used for m, s in zip(src["month"], src["slot"])])
    rows = []
    for label, mask in masks.items():
        mask = np.asarray(mask, dtype=bool)
        abs_err = (src["y"] - src["y_hat"]).abs().to_numpy()
        zeroed_err = np.where(mask, src["y"].abs().to_numpy(), abs_err)
        row = {
            "mask": label,
            "masked_half_hours": int(mask.sum()),
            "masked_share": float(mask.mean()),
            "masked_inside_reporting_daytime": int((mask & daytime).sum()),
            "reporting_night_half_hours": int((~daytime).sum()),
            "sum_actual_inside_mask_mw": float(src.loc[mask, "y"].sum()),
            "max_actual_inside_mask_mw": float(src.loc[mask, "y"].max()) if mask.any() else float("nan"),
            "source_abs_err_inside_mask_mw": float(abs_err[mask].sum()),
            "source_abs_err_total_mw": float(abs_err.sum()),
            "source_abs_err_after_zeroing_mw": float(zeroed_err.sum()),
            "source_night_mean_forecast_mw": float(src.loc[~daytime, "y_hat"].mean()),
        }
        if var is not None and label == next(iter(masks)):
            row["variant_rows_zero_inside_mask"] = int((var.loc[mask, "y_hat"] == 0).sum())
            row["variant_rows_equal_outside_mask"] = int((var.loc[~mask, "y_hat"].to_numpy() == src.loc[~mask, "y_hat"].to_numpy()).sum())
            row["variant_night_mean_forecast_mw"] = float(var.loc[~daytime, "y_hat"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def daytime_mask_invariant(df: pd.DataFrame, phase1_methods: tuple[str, ...] = ("t0", "prev_day", "prev_week")) -> bool:
    """Is the reporting mask the same whether computed on the Phase 1 rows or on all rows?

    The cutoff is 1 % of a p99 over method-duplicated rows; for the full 2024
    frame the interpolated p99 resolves to the same order statistic for the
    Phase 1 and the Phase 2 method counts, so the mask is identical. Recorded
    per run rather than assumed.
    """
    present = [m for m in phase1_methods if m in set(df["method"])]
    if not present:
        return True
    return daytime_slots(df) == daytime_slots(df.loc[df["method"].isin(present)])
