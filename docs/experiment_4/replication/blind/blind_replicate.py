#!/usr/bin/env python3
"""Blind replication of Experiment 4 (t0 on French day-ahead prices).

Reads only the packet files: forecasts.csv.gz, spec_excerpt.json, p4_kept_days.json
(README_PACKET.md was read by the analyst for the documented function behaviour).
Implements the frozen rules in spec_excerpt.json ('statistics', 'probes', 'periods',
'report_only', 'carry_forward', 'AVAIL') and writes blind_outputs.json.
"""
import json
import math
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

try:  # scipy only for the Student-t quantile
    from scipy.stats import t as _student_t

    def t_crit(df, alpha):
        return float(_student_t.ppf(1.0 - alpha, df))

    T_SOURCE = "scipy.stats.t.ppf"
except Exception:  # pragma: no cover - fallback implementation
    def _t_cdf(x, df):
        # regularized incomplete beta via continued fraction
        from math import lgamma, exp, log

        def betacf(a, b, z):
            MAXIT, EPS, FPMIN = 400, 3e-16, 1e-300
            qab, qap, qam = a + b, a + 1.0, a - 1.0
            c, d = 1.0, 1.0 - qab * z / qap
            d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
            h = d
            for m in range(1, MAXIT + 1):
                m2 = 2 * m
                aa = m * (b - m) * z / ((qam + m2) * (a + m2))
                d = 1.0 + aa * d
                d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
                c = 1.0 + aa / c
                c = c if abs(c) > FPMIN else FPMIN
                h *= d * c
                aa = -(a + m) * (qab + m) * z / ((a + m2) * (qap + m2))
                d = 1.0 + aa * d
                d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
                c = 1.0 + aa / c
                c = c if abs(c) > FPMIN else FPMIN
                de = d * c
                h *= de
                if abs(de - 1.0) < EPS:
                    break
            return h

        def ibeta(a, b, z):
            if z <= 0:
                return 0.0
            if z >= 1:
                return 1.0
            bt = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(z) + b * log(1 - z))
            if z < (a + 1) / (a + b + 2):
                return bt * betacf(a, b, z) / a
            return 1.0 - bt * betacf(b, a, 1 - z) / b

        z = df / (df + x * x)
        p = 0.5 * ibeta(df / 2.0, 0.5, z)
        return 1.0 - p if x > 0 else p

    def t_crit(df, alpha):
        lo, hi = 0.0, 1000.0
        for _ in range(300):
            mid = 0.5 * (lo + hi)
            if _t_cdf(mid, df) < 1.0 - alpha:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    T_SOURCE = "bisection on own regularized-incomplete-beta Student-t CDF"


PKT = os.path.dirname(os.path.abspath(__file__))
F_FORECASTS = os.path.join(PKT, "forecasts.csv.gz")
F_SPEC = os.path.join(PKT, "spec_excerpt.json")
F_P4 = os.path.join(PKT, "p4_kept_days.json")
F_README = os.path.join(PKT, "README_PACKET.md")
F_OUT = os.path.join(PKT, "blind_outputs.json")

LEVELS = (0.10, 0.25, 0.50, 0.75, 0.90)
QCOLS = ("q10", "q25", "q50", "q75", "q90")
BLOCK_DAYS = 14
SAMPLES = 2000
SEED = 0
N_SEEDS = 200
MIN_DAYS_PER_BLOCK = 10
SENS_BLOCKS = (1, 3, 7, 14, 30)

spec = json.load(open(F_SPEC))
p4_meta = json.load(open(F_P4))
STATS = spec["statistics"]
ALPHA = float(STATS["alpha"])
PERIODS = spec["periods"]
TEST_LO, TEST_HI = PERIODS["test"]
TEST_YEARS = list(PERIODS["test_years"])
P4_FIRST = spec["AVAIL"]["p4_first_day"]
P4_LO, P4_HI = PERIODS["p4_days"]
P4_LO = max(P4_LO, P4_FIRST)  # "from AVAIL.p4_first_day" (never earlier)
P4_KEPT = set(p4_meta["kept_days"])
PROBES = {p["id"]: p for p in spec["probes"]}

ASSUMPTIONS = []


def note(s):
    ASSUMPTIONS.append(s)


# --------------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------------
df = pd.read_csv(F_FORECASTS, float_precision="round_trip", low_memory=False)
df["target_time"] = pd.to_datetime(df["target_time"], utc=True)
df["local"] = pd.to_datetime(df["local_time"], utc=True).dt.tz_convert("Europe/Paris")
assert (df["local"] == df["target_time"]).all()
assert (df["local"].dt.strftime("%Y-%m-%d") == df["delivery_date"]).all()
assert not df.duplicated(["method", "target_time"]).any()

ARMS = sorted(df["method"].unique())

# Expected number of scored hours of each Paris delivery day (23/24/25)
all_days = pd.date_range(TEST_LO, TEST_HI, freq="D")


def paris_day_hours(d):
    a = pd.Timestamp(d).tz_localize("Europe/Paris")
    b = (pd.Timestamp(d) + pd.Timedelta(days=1)).tz_localize("Europe/Paris")
    return int(round((b - a).total_seconds() / 3600))


EXP_HOURS = {d.strftime("%Y-%m-%d"): paris_day_hours(d) for d in all_days}
DST_DAYS = sorted(k for k, v in EXP_HOURS.items() if v != 24)

# Hourly base frame: one row per target hour (the union over arms)
base = (
    df[["target_time", "delivery_date", "local", "y"]]
    .drop_duplicates("target_time")
    .set_index("target_time")
    .sort_index()
)
# y must be identical across arms
ychk = df.pivot(index="target_time", columns="method", values="y")
assert float(np.nanmax((ychk.max(axis=1) - ychk.min(axis=1)).abs().values)) == 0.0

H = base.copy()
H["date"] = H["delivery_date"]
H["year"] = H["date"].str[:4]
H["month"] = H["date"].str[5:7].astype(int)
H["lhour"] = H["local"].dt.hour
y = H["y"].values

for m in ARMS:
    g = df[df["method"] == m].set_index("target_time").reindex(H.index)
    err = y - g["y_hat"].values
    H[f"{m}|ae"] = np.abs(err)
    H[f"{m}|se"] = err * err
    H[f"{m}|okp"] = np.isfinite(g["y_hat"].values)
    qs = np.column_stack([g[c].values for c in QCOLS])
    okq = np.isfinite(qs).all(axis=1)
    H[f"{m}|okq"] = okq
    if okq.any():
        pin = np.zeros(len(H))
        for j, tau in enumerate(LEVELS):
            u = y - qs[:, j]
            pin = pin + np.where(u >= 0, tau * u, (tau - 1.0) * u)
        H[f"{m}|pb"] = pin / len(LEVELS)  # mean pinball over the five levels
        H[f"{m}|cov"] = (qs[:, 0] <= y) & (y <= qs[:, 4])  # q10 <= y <= q90, as output
    else:
        H[f"{m}|pb"] = np.nan
        H[f"{m}|cov"] = False

note(
    "Pinball loss for level tau is (y-q)*tau if y>=q else (y-q)*(tau-1) (no factor 2); each hour's loss is the "
    "mean over the five levels 0.10,0.25,0.50,0.75,0.90; per-day table holds the sum of these hourly means and n = "
    "hours. Any constant scaling cancels in the skill, block means ratio and M."
)

# Target completeness per day: every real Paris hour present with finite y
hours_present = H.groupby("date").size()
y_finite = H.groupby("date")["y"].apply(lambda s: bool(np.isfinite(s.values).all()))
TARGET_OK = {
    d: bool(hours_present.get(d, 0) == EXP_HOURS[d] and y_finite.get(d, False)) for d in EXP_HOURS
}


def arm_day_ok(arm, kind):
    col = f"{arm}|okp" if kind == "point" else f"{arm}|okq"
    s = H.groupby("date")[col].all()
    return {d: bool(s.get(d, False) and hours_present.get(d, 0) == EXP_HOURS[d]) for d in EXP_HOURS}


ARM_OK = {(a, k): arm_day_ok(a, k) for a in ARMS for k in ("point", "quant")}

# Missing days by cause (reported)
MISSING = {}
for a in ARMS:
    rows = df[df["method"] == a]
    present_days = set(rows["delivery_date"].unique())
    test_days = list(EXP_HOURS)
    no_rows = [d for d in test_days if d not in present_days]
    nonfinite = [d for d in test_days if d in present_days and not ARM_OK[(a, "point")][d]]
    MISSING[a] = {"no_forecast_rows": len(no_rows), "nonfinite_point_hour": len(nonfinite)}
    if a == "t0_cal_wx":
        MISSING[a]["no_rows_before_p4_first_day"] = sum(1 for d in no_rows if d < P4_FIRST)
        MISSING[a]["no_rows_failed_p4_day_rule"] = sum(1 for d in no_rows if d >= P4_FIRST and d not in P4_KEPT)
        MISSING[a]["no_rows_other"] = sum(1 for d in no_rows if d >= P4_FIRST and d in P4_KEPT)
MISSING["_target_incomplete_days"] = sum(1 for d in EXP_HOURS if not TARGET_OK[d])


# --------------------------------------------------------------------------------------
# Calendars: French public holidays, DST weeks
# --------------------------------------------------------------------------------------
def easter(yr):
    a = yr % 19
    b, c = divmod(yr, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(yr, month, day)


def fr_holidays(yr):
    e = easter(yr)
    return {
        date(yr, 1, 1),
        e + timedelta(days=1),  # Easter Monday
        date(yr, 5, 1),
        date(yr, 5, 8),
        e + timedelta(days=39),  # Ascension
        e + timedelta(days=50),  # Whit Monday
        date(yr, 7, 14),
        date(yr, 8, 15),
        date(yr, 11, 1),
        date(yr, 11, 11),
        date(yr, 12, 25),
    }


HOLIDAYS = sorted(d.isoformat() for yr in (2024, 2025) for d in fr_holidays(yr))
note(
    "French public holidays = the 11 national holidays (1 Jan, Easter Monday, 1 May, 8 May, Ascension = Easter+39, "
    "Whit Monday = Easter+50, 14 Jul, 15 Aug, 1 Nov, 11 Nov, 25 Dec), Easter by the anonymous Gregorian computus "
    "(Meeus/Jones/Butcher); Alsace-Moselle extras (Good Friday, 26 Dec) and Whit Monday's 'solidarity day' status "
    "ignored. 2024/2025: " + ", ".join(HOLIDAYS)
)
WEEKEND_HOL = {
    d for d in EXP_HOURS if pd.Timestamp(d).dayofweek >= 5 or d in set(HOLIDAYS)
}
note("'weekends and holidays' = Paris delivery days that are Saturday, Sunday or a French public holiday (whole days).")

DST_WEEK_DAYS = set()
for sd in DST_DAYS:
    for k in range(7):
        DST_WEEK_DAYS.add((pd.Timestamp(sd) + pd.Timedelta(days=k)).strftime("%Y-%m-%d"))
note(
    "'the weeks after each DST switch' = for each switch day (Paris days with 23 or 25 hours: "
    + ", ".join(DST_DAYS)
    + ") the 7 delivery days starting on the switch day (switch day + next 6 days), pooled into one slice of whole days."
)


# --------------------------------------------------------------------------------------
# Per-day tables and statistics
# --------------------------------------------------------------------------------------
def day_set(arm, ref, metric, day_rule):
    kind = "quant" if metric == "pinball" else "point"
    out = []
    for d in sorted(EXP_HOURS):
        if not day_rule(d):
            continue
        if not TARGET_OK[d]:
            continue
        if not (ARM_OK[(arm, kind)][d] and ARM_OK[(ref, kind)][d]):
            continue
        out.append(d)
    return out


def per_day(arm, ref, metric, days, hour_filter=None):
    """Per-day table (date order) of the loss sums of arm and ref and the hour count n."""
    lc = "pb" if metric == "pinball" else "ae"
    h = H[H["date"].isin(days)]
    if hour_filter is not None:
        h = h[hour_filter(h)]
    g = h.groupby("date", sort=True)
    tab = pd.DataFrame(
        {
            "a": g[f"{arm}|{lc}"].sum(),
            "r": g[f"{ref}|{lc}"].sum(),
            "n": g.size(),
            "na_a": g[f"{arm}|{lc}"].apply(lambda s: int(s.isna().sum())),
            "na_r": g[f"{ref}|{lc}"].apply(lambda s: int(s.isna().sum())),
        }
    )
    # metrics._day_pivot-style check: same days, equal hour counts, no NaN
    assert (tab["na_a"] == 0).all() and (tab["na_r"] == 0).all()
    assert np.isfinite(tab[["a", "r"]].values).all()
    return tab[["a", "r", "n"]], h


def skill_of(tab):
    return float(1.0 - tab["a"].sum() / tab["r"].sum())


def mbb_draws(a, r, L, B, seed):
    """Moving-block bootstrap (Kuensch, non-circular) of the pooled-sum skill.

    ceil(n/L) blocks of L consecutive days with starts uniform on {0..n-L}, concatenated and truncated to n
    days; the same index is applied to arm and ref. Implemented via block sums: the first nb-1 blocks
    contribute their full L-day sum, the last its first rl = n-(nb-1)L days (exactly the truncation).
    """
    a = np.asarray(a, float)
    r = np.asarray(r, float)
    n = len(a)
    L = min(L, n)
    nb = -(-n // L)
    rl = n - (nb - 1) * L
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n - L + 1, size=(B, nb))
    sw = np.lib.stride_tricks.sliding_window_view
    fa, fr = sw(a, L).sum(axis=1), sw(r, L).sum(axis=1)
    pa, pr = sw(a, rl).sum(axis=1)[: n - L + 1], sw(r, rl).sum(axis=1)[: n - L + 1]
    sa = fa[starts[:, : nb - 1]].sum(axis=1) + pa[starts[:, nb - 1]]
    sr = fr[starts[:, : nb - 1]].sum(axis=1) + pr[starts[:, nb - 1]]
    draws = 1.0 - sa / sr
    if not np.isfinite(draws).all():
        raise SystemExit("non-finite bootstrap draw: run stops with nothing reported")
    return draws


def ci_p(draws, margin):
    lo, hi = np.percentile(draws, [2.5, 97.5])
    k = int(np.sum(draws <= margin))
    p = (1 + k) / (len(draws) + 1)
    return [float(lo), float(hi)], float(p), k


def seed_spread(tab, margin, L=BLOCK_DAYS):
    lo, hi, ks = [], [], []
    for s in range(N_SEEDS):
        d = mbb_draws(tab["a"].values, tab["r"].values, L, SAMPLES, s)
        c, _, k = ci_p(d, margin)
        lo.append(c[0])
        hi.append(c[1])
        ks.append(k)
    return {"ci_lo": lo, "ci_hi": hi, "k": ks}


def full_comparison(arm, ref, metric, day_rule, margin=0.0, hour_filter=None, with_spread=True):
    days = day_set(arm, ref, metric, day_rule)
    if not days:
        return None, None, None
    tab, h = per_day(arm, ref, metric, days, hour_filter)
    if len(tab) == 0:
        return None, None, None
    sk = skill_of(tab)
    if not math.isfinite(sk):
        raise SystemExit("non-finite skill: run stops")
    draws = mbb_draws(tab["a"].values, tab["r"].values, BLOCK_DAYS, SAMPLES, SEED)
    ci, p, k = ci_p(draws, margin)
    res = {
        "arm": arm,
        "ref": ref,
        "metric": metric,
        "days": int(len(tab)),
        "hours": int(tab["n"].sum()),
        "loss_arm": float(tab["a"].sum() / tab["n"].sum()),
        "loss_ref": float(tab["r"].sum() / tab["n"].sum()),
        "skill": sk,
        "days_won": int((tab["a"] < tab["r"]).sum()),
        "days_lost": int((tab["a"] > tab["r"]).sum()),
        "ci95": ci,
        "p": p,
        "draws_le_margin": k,
        "margin": margin,
    }
    if with_spread:
        res["seed_spread"] = seed_spread(tab, margin)
    return res, tab, h


def yearly(tab):
    out = {}
    for yr in TEST_YEARS:
        t = tab[tab.index.str[:4] == yr]
        out[yr] = skill_of(t) if len(t) else None  # None = 'no days'
    return out


def in_period(lo, hi):
    return lambda d: lo <= d <= hi


note(
    "Bootstrap = moving-block (Kuensch, non-circular) on the per-day table in date order with dropped days "
    "skipped: block length L = 14 days (min(14, n) if a slice has fewer than 14 days), ceil(n/L) blocks with start "
    "indices drawn i.i.d. uniform on {0,...,n-L} by numpy.random.default_rng(seed).integers(0, n-L+1, "
    "size=(2000, nb)), blocks concatenated and truncated to n days, the same indices for arm and reference; each "
    "draw's skill = 1 - sum(arm loss sums)/sum(ref loss sums)."
)
note(
    "95% interval = percentile interval numpy.percentile(draws, [2.5, 97.5]) (linear interpolation); p = (1 + "
    "#draws <= m)/2001 with m = 0 (superiority) from the same seed-0 draws; seed_spread repeats the identical "
    "procedure for seeds 0..199 and k = #draws <= m for each seed."
)
note(
    "Day sets: a day is complete when the Paris calendar's 23/24/25 hours are all present with finite y "
    "(y is identical across arms; checked); an arm is finite on a day when y_hat (P3: q10..q90) is finite at every "
    "hour. All 731 test days are complete and all arms are finite on every day they have rows. loss_arm/loss_ref = "
    "pooled MAE (P3: pooled mean pinball). P3 coverage counts every scored UTC hour (both autumn 02:00 hours) of "
    "P3's pooled day set; coverage_yearly is the same share by delivery year. Primaries' yearly skills have no "
    "bootstrap (the year slices carry report-only intervals)."
)
note(
    "days_won / days_lost = days on which the arm's daily loss is strictly lower / strictly higher than the "
    "reference's (ties counted in neither)."
)

# --------------------------------------------------------------------------------------
# Primaries
# --------------------------------------------------------------------------------------
test_rule = in_period(TEST_LO, TEST_HI)
p4_rule = lambda d: P4_LO <= d <= P4_HI and d in P4_KEPT  # noqa: E731

note(
    "P4 day rule (weather_p4.day_rule) taken as the recorded p4_kept_days.json list (572 days), intersected with "
    "periods.p4_days from AVAIL.p4_first_day (2024-06-06), complete target and both arms finite at every hour."
)
note(
    "K3 treated as passed because t0_cal_wx was scored (spec: t0_cal_wx would be 'not run' after K3 failed); K1 "
    "failed per README_PACKET.md so lear_ens is not scored: P2 not runnable, enters Holm with p = 1, and every "
    "lear_ens comparison is 'not run'."
)

prim = {}
tabs = {}
hrs = {}
spec_rule = {"P1": test_rule, "P3": test_rule, "P4": p4_rule}
for pid in ("P1", "P3", "P4"):
    pr = PROBES[pid]
    arm = pr["t0_arm"].split(" ")[0]
    ref = pr["comparator"]
    metric = pr["metric"]
    res, tab, h = full_comparison(arm, ref, metric, spec_rule[pid], margin=0.0)
    res["yearly"] = yearly(tab)
    if pid == "P3":
        hh = h  # all scored hours of P3's pooled day set
        res["coverage"] = float(hh[f"{arm}|cov"].mean())
        res["coverage_yearly"] = {
            yr: (float(hh[hh["year"] == yr][f"{arm}|cov"].mean()) if (hh["year"] == yr).any() else None)
            for yr in TEST_YEARS
        }
        res["coverage_hours_in_band"] = int(hh[f"{arm}|cov"].sum())
    prim[pid] = res
    tabs[pid] = tab
    hrs[pid] = h

prim["P2"] = {
    "runnable": False,
    "p": 1.0,
    "arm": "t0_cal",
    "ref": "lear_ens",
    "metric": "mae",
    "reason": "K1 reproduction gate failed on all three attempts; lear_ens not scored",
}
order = ["P1", "P2", "P3", "P4"]


def holm(pvals):
    p = np.asarray(pvals, float)
    m = len(p)
    idx = np.argsort(p, kind="stable")
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(idx):
        run = max(run, min(1.0, (m - i) * p[j]))
        adj[j] = run
    return [float(v) for v in adj]


note("Holm step-down over (P1, P2, P3, P4) in that input order; ties in p broken by input order (stable sort); "
     "adjusted p = running max of min(1, (m-i+1) p_(i)).")

holm_in = [prim["P1"]["p"], 1.0, prim["P3"]["p"], prim["P4"]["p"]]
holm_adj = holm(holm_in)
for pid, hp in zip(order, holm_adj):
    prim[pid]["holm_p"] = hp


def verdict(pid):
    r = prim[pid]
    if pid == "P2":
        return "not runnable"
    if pid == "P4" and r.get("days", 0) == 0:
        return "not runnable"
    thr = 0.0
    if not (r["skill"] > thr) or not (r["holm_p"] < ALPHA):
        return "lost"
    if any((v is None) or not (v > thr) for v in r["yearly"].values()):
        return "not stable"
    if pid == "P3" and not (0.70 <= r["coverage"] <= 0.90):
        return "lost on coverage"
    return "won"


states = {pid: verdict(pid) for pid in order}
for pid in order:
    prim[pid]["state"] = states[pid]
    if pid != "P2":
        prim[pid]["yearly_pass"] = {k: (v is not None and v > 0) for k, v in prim[pid]["yearly"].items()}

# --------------------------------------------------------------------------------------
# Secondaries and strict comparisons
# --------------------------------------------------------------------------------------
SEC_MAP = {
    "t0 (no calendar) vs best_simple_2023": ("t0", "best_simple_2023"),
    "t0_cal vs t0": ("t0_cal", "t0"),
    "t0_cal_strict vs best_simple_2023 (t0 alone without the allowance)": ("t0_cal_strict", "best_simple_2023"),
    "t0_cal_strict vs best_simple_2023_strict (the old rule for both)": ("t0_cal_strict", "best_simple_2023_strict"),
    "t0_cal vs t0_cal_strict (value of the D-1 afternoon to t0)": ("t0_cal", "t0_cal_strict"),
}
secondaries = {}
strict = {}
for name in spec["report_only"]["secondaries"]:
    if name in SEC_MAP:
        arm, ref = SEC_MAP[name]
        res, tab, _ = full_comparison(arm, ref, "mae", test_rule, margin=0.0)
        res["yearly"] = yearly(tab)
        secondaries[name] = res
        if "strict" in arm or "strict" in ref:
            strict[name] = {"arm": arm, "ref": ref, "skill": res["skill"], "yearly": res["yearly"],
                            "days": res["days"], "ci95": res["ci95"], "p": res["p"]}
    elif "lear_ens" in name:
        secondaries[name] = {"not_run": "lear_ens was not scored (K1 failed on all three attempts)"}
    elif name.startswith("rMAE"):
        secondaries[name] = {"not_run": "not a single arm-vs-ref bootstrap comparison; values are under top-level 'rmae'"}
    elif name == "RMSE":
        secondaries[name] = {"not_run": "not a bootstrap comparison; values are under top-level 'rmse'"}
    else:
        secondaries[name] = {"not_run": "unrecognised secondary"}

note(
    "Secondaries are MAE comparisons (arm = first named, ref = second) on their own paired day set within "
    "periods.test, 14-day MBB / 2000 draws / seed 0, superiority margin 0. The 'strict' block lists the three "
    "secondaries that involve a _strict arm."
)

# rMAE vs naive_std and prev_week
rmae = {}
for ref in ("naive_std", "prev_week"):
    rmae[ref] = {}
    for arm in ARMS:
        if arm == ref:
            continue
        days = day_set(arm, ref, "mae", test_rule)
        if not days:
            rmae[ref][arm] = None
            continue
        tab, _ = per_day(arm, ref, "mae", days)
        rmae[ref][arm] = float(tab["a"].sum() / tab["r"].sum())
note(
    "rMAE(arm | ref) = pooled MAE of arm / pooled MAE of ref over their own paired day set within periods.test "
    "(for t0_cal_wx that is its 572 scored days)."
)

# RMSE on the primaries' day sets
rmse = {}
for pid in ("P1", "P4"):
    h = hrs[pid]
    arm, ref = prim[pid]["arm"], prim[pid]["ref"]
    rmse[pid] = {a: float(np.sqrt(h[f"{a}|se"].mean())) for a in (arm, ref)}
note("RMSE = sqrt(mean squared error) pooled over every scored hour of P1's / P4's day set, for its two arms.")

# --------------------------------------------------------------------------------------
# Slices
# --------------------------------------------------------------------------------------
QUARTERS = [f"{yr}Q{q}" for yr in TEST_YEARS for q in (1, 2, 3, 4)]


def quarter_of(d):
    return f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"


def slice_defs():
    out = []
    for yr in TEST_YEARS:
        out.append((yr, lambda d, yr=yr: d[:4] == yr, None))
    for q in QUARTERS:
        out.append((q, lambda d, q=q: quarter_of(d) == q, None))
    out.append(("April-September", lambda d: 4 <= int(d[5:7]) <= 9, None))
    out.append(("negative-price hours", None, lambda h: h["y"] < 0))
    out.append(
        ("top 1% absolute prices", None,
         lambda h: np.abs(h["y"]) >= np.quantile(np.abs(h["y"].values), 0.99))
    )
    out.append(("11:00-16:00 local", None, lambda h: h["lhour"].between(11, 15)))
    out.append(("weekends and holidays", lambda d: d in WEEKEND_HOL, None))
    out.append(("the weeks after each DST switch", lambda d: d in DST_WEEK_DAYS, None))
    return out


note(
    "Slices are scored on the comparison's own day set: day slices keep whole days of it (quarters = calendar "
    "quarters of the Paris delivery date; 'April-September' pools both years); hour slices keep only their hours "
    "('negative-price hours' y < 0; 'top 1% absolute prices' |y| >= numpy.quantile(|y|, 0.99) over every scored "
    "hour of that comparison's day set, each hour once since y is common to both arms; '11:00-16:00 local' = Paris "
    "local start hour 11..15), dropping days with none of them. Each slice gets its own 14-day MBB, 2000 draws, seed "
    "0, margin 0 and a 200-seed spread. An empty slice is printed with status 'no days' and null numbers."
)

slices = {}
for pid in ("P1", "P3", "P4"):
    arm, ref, metric = prim[pid]["arm"], prim[pid]["ref"], prim[pid]["metric"]
    base_rule = spec_rule[pid]
    slices[pid] = {}
    for label, drule, hfilt in slice_defs():
        rule = (lambda d, br=base_rule, dr=drule: br(d) and dr(d)) if drule is not None else base_rule
        if hfilt is not None:
            # hour slice: the day set is the comparison's full day set; the hour filter is applied inside
            res, tab, _ = full_comparison(arm, ref, metric, base_rule, hour_filter=hfilt)
        else:
            res, tab, _ = full_comparison(arm, ref, metric, rule)
        if res is None:
            slices[pid][label] = {"status": "no days", "skill": None, "days": 0, "hours": 0, "ci95": None,
                                  "p": None, "seed_spread": None}
        else:
            slices[pid][label] = {
                "skill": res["skill"], "days": res["days"], "hours": res["hours"], "ci95": res["ci95"],
                "p": res["p"], "draws_le_margin": res["draws_le_margin"], "loss_arm": res["loss_arm"],
                "loss_ref": res["loss_ref"], "seed_spread": res["seed_spread"],
            }
            if label == "top 1% absolute prices":
                hh = hrs[pid]
                slices[pid][label]["threshold_abs_y"] = float(np.quantile(np.abs(hh["y"].values), 0.99))

# --------------------------------------------------------------------------------------
# Tables: concentration and bootstrap sensitivity
# --------------------------------------------------------------------------------------
def concentration(tab, top=(5, 10, 20)):
    a, r = tab["a"].values, tab["r"].values
    g = r - a
    net = float(g.sum())
    order_ = np.argsort(-g, kind="stable")
    out = {"net_gain": net}
    for N in top:
        sel = order_[:N]
        keep = np.ones(len(g), bool)
        keep[sel] = False
        out[f"top{N}_share"] = float(g[sel].sum() / net)
        out[f"skill_without_top{N}"] = float(1.0 - a[keep].sum() / r[keep].sum())
    return out


note(
    "Concentration: per-day gain g = ref loss sum - arm loss sum (EUR/MWh summed over hours; P3 pinball sums); "
    "net_gain = sum g; topN_share = sum of the N largest g / net_gain; skill_without_topN = pooled skill after "
    "removing those N days."
)

concentration_out = {pid: concentration(tabs[pid]) for pid in ("P1", "P3", "P4")}

bootstrap_sensitivity = {}
for pid in ("P1", "P3", "P4"):
    tab = tabs[pid]
    rows = []
    for L in SENS_BLOCKS:
        d = mbb_draws(tab["a"].values, tab["r"].values, L, SAMPLES, SEED)
        c, p, k = ci_p(d, 0.0)
        rows.append({"block": L, "ci95": c, "p": p})
    bootstrap_sensitivity[pid] = rows
note("Bootstrap sensitivity uses the same MBB, 2000 draws, seed 0, block lengths 1, 3, 7, 14, 30 days.")

# --------------------------------------------------------------------------------------
# Carry-forward
# --------------------------------------------------------------------------------------
def blocks(tab, delta, block_days=BLOCK_DAYS, start=None):
    dates = pd.to_datetime(tab.index)
    start = dates.min() if start is None else pd.Timestamp(start)
    k = ((dates - start).days // block_days).values
    d = (1.0 - delta) * (tab["r"].values / tab["n"].values) - tab["a"].values / tab["n"].values
    s = pd.Series(d).groupby(k)
    cnt, mean = s.size(), s.mean()
    return mean[cnt >= MIN_DAYS_PER_BLOCK].values, int((cnt >= MIN_DAYS_PER_BLOCK).sum()), int(len(cnt))


def power_table(tab, alpha, blocks_list=(6, 8, 12)):
    b, nk, _ = blocks(tab, 0.0)
    if len(b) < 3:
        return None
    sd = float(np.std(b, ddof=1))
    ref_mae = float(tab["r"].sum() / tab["n"].sum())
    mds = {}
    mds_raw = {}
    for k in blocks_list:
        mk = (t_crit(k - 1, alpha) + 0.8416) * sd / math.sqrt(k) / ref_mae
        mds_raw[str(k)] = mk
        mds[str(k)] = round(mk, 4)
    return {"block_sd": round(sd, 3), "ref_mae": round(ref_mae, 3), "min_detectable_skill": mds,
            "_sd": sd, "_ref_mae": ref_mae, "_mds_raw": mds_raw, "_n_blocks": nk}


carry = {}
CF_ALPHA = 0.0125
for pid in ("P1", "P3", "P4"):
    tab = tabs[pid]
    A = tab[tab.index.map(lambda d: d[:4] in ("2024", "2025") and 4 <= int(d[5:7]) <= 9)]
    S = skill_of(A)
    pt = power_table(A, CF_ALPHA)
    M = pt["min_detectable_skill"]["12"]
    info = {}
    for lab, div in (("alpha/2", 2), ("alpha/3", 3), ("alpha/4", 4)):
        info[lab] = power_table(A, CF_ALPHA / div)["min_detectable_skill"]["12"]
    delta = None
    for dlt in (0.0, 0.05, 0.10, 0.20):
        if S - dlt >= M:
            delta = dlt  # largest satisfying value (list ascending)
    carry[pid] = {
        "A_days": int(len(A)),
        "S": S,
        "block_sd": pt["block_sd"],
        "ref_mae": pt["ref_mae"],
        "M": M,
        "M_info": info,
        "delta": delta,
        "candidate": bool(states[pid] == "won" and delta is not None),
        "n_blocks_kept": pt["_n_blocks"],
        "unrounded": {"block_sd": pt["_sd"], "ref_mae": pt["_ref_mae"], "M": pt["_mds_raw"]["12"],
                      "M_k": pt["_mds_raw"]},
        "M_k_rounded": pt["min_detectable_skill"],
        "state": states[pid],
    }
note(
    "Carry-forward: A = the primary's own per-day table restricted to Paris delivery dates in April-September 2024 "
    "or 2025; blocks are calendar 14-day spans from A's first day (2024-04-01 for P1/P3, 2024-06-06 for P4), a "
    "block kept with >= 10 days; block mean of (loss_ref - loss_arm) with daily mean loss = sum/n; sd ddof=1; M = "
    "M_12 at alpha 0.0125 rounded to 4 decimals (block_sd, ref_mae rounded to 3) and compared as rounded; delta = "
    "largest of {0, 0.05, 0.10, 0.20} with S - delta >= M, reported even when the state is not 'won' (null if "
    "none); candidate requires state 'won'. M_info at alpha 0.0125/2, /3, /4. t quantile: " + T_SOURCE + "."
)

# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------
def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        o = float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


out = {
    "files_read": [F_README, F_SPEC, F_P4, F_FORECASTS],
    "assumptions": ASSUMPTIONS,
    "data_checks": {
        "rows": int(len(df)),
        "arms": ARMS,
        "test_days": len(EXP_HOURS),
        "dst_days": DST_DAYS,
        "target_incomplete_days": MISSING["_target_incomplete_days"],
        "arm_missing_days_by_cause": {k: v for k, v in MISSING.items() if not k.startswith("_")},
        "p4_kept_days": len(P4_KEPT),
    },
    "primaries": {k: prim[k] for k in order},
    "holm": {"order": order, "input": holm_in, "adjusted": holm_adj},
    "states": states,
    "strict": strict,
    "secondaries": secondaries,
    "rmae": rmae,
    "rmse": rmse,
    "slices": slices,
    "concentration": concentration_out,
    "bootstrap_sensitivity": bootstrap_sensitivity,
    "carry_forward": carry,
}
with open(F_OUT, "w") as fh:
    json.dump(clean(out), fh, indent=1)
print("wrote", F_OUT)
