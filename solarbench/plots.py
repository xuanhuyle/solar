"""The benchmark's figures.

Light-mode PNGs for the README.  Three methods means three categorical hues,
assigned in fixed order and held constant across every figure; the actual series
is ink, because it is the reference rather than a fourth competitor.  No figure
uses two y-scales — where a second measure helps, it gets its own panel.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from solarbench import metrics

log = logging.getLogger(__name__)

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#e4e3df"
NIGHT = "#eceae4"

#: Validated categorical palette (all-pairs, light surface): blue, orange, aqua.
SERIES_COLORS = {"t0": "#2a78d6", "prev_day": "#eb6834", "prev_week": "#1baf7a"}
#: Aqua sits below 3:1 on the light surface, so it also carries a dash pattern.
SERIES_DASHES = {"t0": (None, None), "prev_day": (None, None), "prev_week": (5, 2)}

FIG_KW = dict(facecolor=SURFACE, dpi=150)


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_SOFT, labelsize=9)
    ax.xaxis.label.set_color(INK_SOFT)
    ax.yaxis.label.set_color(INK_SOFT)


def _color(method: str) -> str:
    return SERIES_COLORS.get(method, INK_SOFT)


def _plot_series(ax, x, y, method: str, labels: dict[str, str], **kw):
    dashes = SERIES_DASHES.get(method, (None, None))
    line, = ax.plot(x, y, color=_color(method), linewidth=2.0, label=labels.get(method, method), **kw)
    if dashes[0] is not None:
        line.set_dashes(dashes)
    return line


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    log.info("wrote %s", path)
    return path


def choose_representative_days(df: pd.DataFrame, primary: str) -> list[tuple[str, pd.Timestamp]]:
    """Pick four delivery days by a fixed rule, so the panel cannot be cherry-picked."""
    per_day = metrics.per_day_errors(df)
    focus = per_day.loc[per_day["method"] == primary].set_index("delivery_date")["mae_mw"].sort_values()
    daily_energy = df.loc[df["method"] == primary].groupby("delivery_date")["y"].sum()
    months = {d: pd.Timestamp(d).month for d in daily_energy.index}

    summer = daily_energy[[m in (6, 7, 8) for m in months.values()]]
    winter = daily_energy[[m in (11, 12, 1, 2) for m in months.values()]]

    picks: list[tuple[str, object]] = []
    if len(focus):
        picks.append((f"Median {primary} error day", focus.index[len(focus) // 2]))
        picks.append((f"Worst {primary} error day", focus.index[-1]))
    if len(summer):
        picks.append(("Highest-output summer day", summer.idxmax()))
    if len(winter):
        picks.append(("Lowest-output winter day", winter.idxmin()))
    return picks[:4]


def plot_representative_days(df: pd.DataFrame, labels: dict[str, str], out: Path, primary: str) -> Path:
    picks = choose_representative_days(df, primary)
    per_day = metrics.per_day_errors(df)
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharey=True, **FIG_KW)
    methods = [m for m in labels if m in set(df["method"])]

    for ax, (title, day) in zip(axes.ravel(), picks):
        _style(ax)
        day_df = df.loc[df["delivery_date"] == day]
        actual = day_df.loc[day_df["method"] == methods[0]].sort_values("slot")
        hours = actual["slot"].to_numpy() / 2.0

        night = ~actual["is_daytime"].to_numpy()
        for lo, hi in _runs(hours, night):
            ax.axvspan(lo, hi, color=NIGHT, zorder=0, linewidth=0)

        ax.plot(hours, actual["y"] / 1000, color=INK, linewidth=2.6, label="Actual", zorder=5)
        notes = []
        for method in methods:
            sub = day_df.loc[day_df["method"] == method].sort_values("slot")
            _plot_series(ax, sub["slot"] / 2.0, sub["y_hat"] / 1000, method, labels, zorder=4)
            mae = per_day.loc[
                (per_day["delivery_date"] == day) & (per_day["method"] == method), "mae_mw"
            ]
            if len(mae):
                notes.append(f"{labels[method]}: {mae.iloc[0]:,.0f} MW")
        ax.set_title(f"{title} — {day}", fontsize=10, color=INK, loc="left")
        ax.text(
            0.02, 0.97, "\n".join(f"MAE  {n}" for n in notes), transform=ax.transAxes,
            va="top", ha="left", fontsize=7.5, color=INK_SOFT,
        )
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 6))
        ax.set_xlabel("Hour of delivery day (Europe/Paris)")

    for ax in axes[:, 0]:
        ax.set_ylabel("Solar generation (GW)")
    handles, lab = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, lab, loc="lower center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Day-ahead forecasts on four days chosen by a fixed rule", color=INK, fontsize=12, x=0.09, ha="left")
    fig.tight_layout()
    return _save(fig, out)


def _runs(x: np.ndarray, flag: np.ndarray) -> list[tuple[float, float]]:
    """Contiguous spans of ``x`` where ``flag`` is True, as (start, end) pairs."""
    spans, start = [], None
    for i, f in enumerate(flag):
        if f and start is None:
            start = x[i]
        elif not f and start is not None:
            spans.append((start, x[i]))
            start = None
    if start is not None:
        spans.append((start, x[-1] + 0.5))
    return spans


def plot_error_by_time_of_day(df: pd.DataFrame, labels: dict[str, str], out: Path) -> Path:
    by_slot = metrics.mae_by(df, "slot")
    mean_actual = df.groupby(["slot", "method"])["y"].mean().groupby("slot").first()

    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(10, 6.4), sharex=True, gridspec_kw={"height_ratios": [3, 1]}, **FIG_KW
    )
    _style(ax)
    _style(ax2)
    for method in labels:
        sub = by_slot.loc[by_slot["method"] == method].sort_values("slot")
        if sub.empty:
            continue
        _plot_series(ax, sub["slot"] / 2.0, sub["mae_mw"], method, labels)
    ax.set_ylabel("MAE (MW)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax.set_title("Error by position in the delivery day", color=INK, fontsize=12, loc="left")
    ax.legend(frameon=False, fontsize=9, loc="upper left")

    ax2.fill_between(mean_actual.index / 2.0, mean_actual.to_numpy() / 1000, color=GRID, zorder=1)
    ax2.set_ylabel("Mean actual (GW)")
    ax2.set_xlabel("Hour of delivery day (Europe/Paris)")
    ax2.set_xlim(0, 23.5)
    ax2.set_xticks(range(0, 24, 3))
    fig.tight_layout()
    return _save(fig, out)


def plot_by_month(df: pd.DataFrame, labels: dict[str, str], out: Path) -> Path:
    by_month = metrics.mae_by(df, "month")
    months = sorted(by_month["month"].unique())
    names = [pd.Timestamp(2024, m, 1).strftime("%b") for m in months]
    active = [m for m in labels if m in set(by_month["method"])]
    width = 0.8 / max(len(active), 1)

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, **FIG_KW)
    for axis, column, ylabel in ((ax, "mae_mw", "MAE (MW)"), (ax2, "nmae_mean", "nMAE (MAE / mean actual)")):
        _style(axis)
        for i, method in enumerate(active):
            sub = by_month.loc[by_month["method"] == method].set_index("month").reindex(months)
            offset = (i - (len(active) - 1) / 2) * width
            axis.bar(
                np.arange(len(months)) + offset, sub[column], width=width * 0.92,
                color=_color(method), label=labels[method], zorder=3, linewidth=0,
            )
        axis.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax2.set_xticks(np.arange(len(months)), names)
    ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_title("Seasonal breakdown", color=INK, fontsize=12, loc="left", pad=26)
    ax.legend(
        frameon=False, fontsize=9, ncol=len(active), loc="lower center",
        bbox_to_anchor=(0.5, 1.0), borderaxespad=0,
    )
    fig.tight_layout()
    return _save(fig, out)


def plot_skill(skills: list[dict], per_day: pd.DataFrame, labels: dict[str, str], out: Path, primary: str) -> Path:
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1, 1.3]}, **FIG_KW)
    _style(ax)
    _style(ax2)

    names = [labels.get(s["reference"], s["reference"]) for s in skills]
    values = [s["skill"] for s in skills]
    lo = [s["skill"] - s["skill_lo95"] for s in skills]
    hi = [s["skill_hi95"] - s["skill"] for s in skills]
    colors = [_color(s["reference"]) for s in skills]
    y = np.arange(len(skills))
    ax.barh(y, values, color=colors, height=0.5, zorder=3, linewidth=0)
    ax.errorbar(values, y, xerr=[lo, hi], fmt="none", ecolor=INK_SOFT, elinewidth=1.4, capsize=4, zorder=4)
    ax.axvline(0, color=INK, linewidth=1.2, zorder=5)
    for i, s in enumerate(skills):
        ax.annotate(
            f"{s['skill']:+.1%}   wins {s['win_rate']:.0%} of days",
            (max(s["skill"], 0), i), xytext=(8, 0), textcoords="offset points",
            va="center", fontsize=8.5, color=INK_SOFT,
        )
    ax.set_yticks(y, names)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=6))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_xlabel(f"MAE reduction by {labels.get(primary, primary)} (95% block bootstrap)")
    ax.set_title("Relative improvement over each baseline", color=INK, fontsize=12, loc="left")
    ax.margins(x=0.28)

    wide = per_day.pivot(index="delivery_date", columns="method", values="mae_mw")
    for s in skills:
        if s["reference"] not in wide or primary not in wide:
            continue
        diff = wide[s["reference"]] - wide[primary]
        ax2.hist(
            diff, bins=40, histtype="stepfilled", alpha=0.55, linewidth=1.4,
            color=_color(s["reference"]), edgecolor=_color(s["reference"]),
            label=f"vs {labels.get(s['reference'], s['reference'])}", zorder=3,
        )
    ax2.axvline(0, color=INK, linewidth=1.2, zorder=5)
    ax2.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax2.set_xlabel(f"Daily MAE advantage of {labels.get(primary, primary)} (MW)")
    ax2.set_ylabel("Delivery days")
    ax2.set_title("Per-day paired differences", color=INK, fontsize=12, loc="left")
    ax2.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    return _save(fig, out)


def plot_predicted_vs_actual(df: pd.DataFrame, labels: dict[str, str], out: Path) -> Path:
    day = df.loc[df["is_daytime"]]
    active = [m for m in labels if m in set(day["method"])]
    fig, axes = plt.subplots(1, len(active), figsize=(4.2 * len(active), 4.3), sharex=True, sharey=True, **FIG_KW)
    axes = np.atleast_1d(axes)
    top = max(day["y"].max(), day["y_hat"].quantile(0.999)) / 1000

    for ax, method in zip(axes, active):
        _style(ax)
        sub = day.loc[day["method"] == method]
        x, yv = sub["y"] / 1000, sub["y_hat"] / 1000
        ax.hexbin(x, yv, gridsize=45, cmap="Blues", mincnt=1, linewidths=0, zorder=2, bins="log")
        ax.set_xlim(0, top)
        ax.set_ylim(0, top)
        ax.plot([0, top], [0, top], color=INK, linewidth=1.2, linestyle="--", zorder=4)
        slope = float(np.sum(x * yv) / np.sum(x * x)) if float(np.sum(x * x)) else float("nan")
        bias = float((sub["y_hat"] - sub["y"]).mean())
        ax.set_title(labels[method], color=INK, fontsize=11, loc="left")
        ax.text(
            0.03, 0.95, f"slope {slope:.2f}\nbias {bias:+,.0f} MW", transform=ax.transAxes,
            va="top", fontsize=8.5, color=INK_SOFT,
        )
        ax.set_xlabel("Actual (GW)")
    axes[0].set_ylabel("Forecast (GW)")
    fig.suptitle("Forecast vs actual, daytime half-hours only", color=INK, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, out)
