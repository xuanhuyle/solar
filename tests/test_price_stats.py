"""Experiment 4 statistics: day sets, per-day tables, compare / yearly / coverage, verdict states, the reading
table, report-only slices, secondaries and tables, and the carry-forward rule (offline, synthetic frames)."""

from __future__ import annotations

import sys
from datetime import date
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_covariates as rc
import run_probes
from engine import zones
from engine.referee import stats as referee_stats
from solarbench import metrics
from solarbench import price_exp as px
from solarbench import price_spec as ps
from solarbench import price_stats as st
from solarbench import probes as pr

PARIS = zones.PARIS
SPREAD = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
RT = ps.PRICE_SPEC["reading_table"]


def tidy(days, arms: dict, *, y_fn=None, spread: float = 5.0) -> pd.DataFrame:
    """A tidy frame as run_price_backtest writes it. ``arms`` maps method -> error: a number, or a callable
    (day index, day, local hours, y) -> error array. Quantiles are y_hat + spread x (-2, -1, 0, 1, 2)."""
    parts_t, parts_d, parts_i = [], [], []
    for i, d in enumerate(days):
        t = px.day_hours(d)
        parts_t.append(t)
        parts_d += [d] * len(t)
        parts_i += [i] * len(t)
    t = parts_t[0].append(parts_t[1:]) if len(parts_t) > 1 else parts_t[0]
    local = t.tz_convert(PARIS)
    idx = np.asarray(parts_i)
    y = (60 + 25 * np.sin(2 * np.pi * (local.hour.to_numpy() - 7) / 24) + 0.3 * idx) if y_fn is None \
        else np.asarray(y_fn(idx, local), dtype="float64")
    frames = []
    for m, e in arms.items():
        if callable(e):
            err = np.concatenate([np.asarray(e(i, d, local[idx == i].hour.to_numpy(), y[idx == i]), dtype="float64")
                                  * np.ones(int((idx == i).sum())) for i, d in enumerate(days)])
        else:
            err = np.full(len(t), float(e))
        yh = y + err
        f = pd.DataFrame({"delivery_date": parts_d, "method": m, "target_time": t, "local_time": local, "y": y,
                          "y_hat": yh, "source_latest": t - pd.Timedelta(hours=30),
                          "cov_issued_latest": pd.DatetimeIndex([pd.NaT] * len(t), tz="UTC")})
        for j, c in enumerate(st.Q_COLUMNS):
            f[c] = yh + spread * SPREAD[j]
        frames.append(f)
    return pd.concat(frames, ignore_index=True)


def noisy(scale: float, bias: float = 0.0, seed: int = 0):
    """An error function: per-day random level plus per-hour noise, reproducible per day index."""
    def err(i, d, hours, y):
        rng = np.random.default_rng(seed * 100_003 + i)
        return bias + scale * (rng.normal(0, 1) + rng.normal(0, 1, len(hours)))
    return err


def set_value(df, method, day, col, value, hour_pos=3):
    rows = df.index[(df["method"] == method) & (df["delivery_date"] == day)]
    df.loc[rows[hour_pos], col] = value
    return df


DAYS = px.days_between("2024-01-08", "2024-01-21") + [date(2024, 3, 31), date(2024, 10, 27)]


# ------------------------------------------------------------------ the spec is read, not paraphrased


def test_constants_are_the_frozen_spec():
    st._check_spec()
    assert st.FAMILY == ("P1", "P2", "P3", "P4") and st.ALPHA == 0.05 and st.TEST_YEARS == ("2024", "2025")
    assert st.probe_arms("P1") == ("t0_cal", "best_simple_2023", "mae")
    assert st.probe_arms("P2") == ("t0_cal", "lear_ens", "mae")
    assert st.probe_arms("P3") == ("t0_cal", "best_simple_eq", "pinball")
    assert st.probe_arms("P4") == ("t0_cal_wx", "t0_cal", "mae")
    assert list(st.SECONDARY_PAIRS) + [st.RMAE_KEY, st.RMSE_KEY] == ps.PRICE_SPEC["report_only"]["secondaries"]
    assert (st.SLICE_YEAR, st.SLICE_QUARTER, st.SLICE_APR_SEP, *st.HOUR_SLICES, st.SLICE_WEEKEND, st.SLICE_DST) \
        == tuple(ps.PRICE_SPEC["report_only"]["slices"])
    assert st.BLOCK_DAYS == 14 and st.SAMPLES == 2000 and st.SEED == 0
    with pytest.raises(ValueError):
        st.day_set(tidy(DAYS[:2], {"a": 1, "b": 2}), "a", "b", metric="rmse")


# ------------------------------------------------------------------ day sets


def test_day_set_takes_whole_days_both_arms_and_complete_targets():
    df = tidy(DAYS, {"a": 1.0, "b": -2.0, "c": 0.5})
    assert st.day_set(df, "a", "b", metric="mae") == sorted(DAYS)  # DST days (23 and 25 hours) included
    x, yday, z, w = date(2024, 1, 9), date(2024, 1, 10), date(2024, 1, 11), date(2024, 1, 12)
    set_value(df, "a", x, "y_hat", np.nan)                  # one hour of arm a
    set_value(df, "c", yday, "y_hat", np.nan)               # an arm outside the comparison
    df.loc[df["delivery_date"] == z, "y"] = df.loc[df["delivery_date"] == z, "y"].where(
        df.loc[df["delivery_date"] == z, "target_time"] != px.day_hours(z)[5])  # the target misses one hour
    drop = df.index[(df["method"] == "b") & (df["delivery_date"] == w)][7]
    df = df.drop(index=drop)                                # arm b lacks one hour's row
    ab = st.day_set(df, "a", "b", metric="mae")
    assert x not in ab and z not in ab and w not in ab and yday in ab
    assert len(ab) == len(DAYS) - 3
    bc = st.day_set(df, "b", "c", metric="mae")
    assert x in bc and yday not in bc and z not in bc and w not in bc
    assert st.day_set(df, "a", "b", metric="mae", allowed_days=["2024-01-08", date(2024, 1, 9), date(2024, 1, 10)]
                      ) == [date(2024, 1, 8), date(2024, 1, 10)]


def test_day_set_pinball_needs_all_five_quantiles():
    df = tidy(DAYS[:5], {"a": 1.0, "b": -2.0})
    d = DAYS[2]
    set_value(df, "a", d, "q25", np.nan)
    assert d in st.day_set(df, "a", "b", metric="mae")
    assert d not in st.day_set(df, "a", "b", metric="pinball")
    set_value(df, "b", DAYS[3], "q90", np.inf)
    assert DAYS[3] not in st.day_set(df, "a", "b", metric="pinball")


def test_day_set_refuses_two_targets_and_same_arm():
    df = tidy(DAYS[:3], {"a": 1.0, "b": 2.0})
    set_value(df, "b", DAYS[1], "y", 999.0)
    with pytest.raises(st.StatisticsError):
        st.day_set(df, "a", "b", metric="mae")
    with pytest.raises(ValueError):
        st.day_set(df, "a", "a", metric="mae")
    assert st.day_set(df, "a", "zz", metric="mae") == []


def test_complete_days_and_arm_missing_and_p2_coverage():
    days = px.days_between("2024-02-01", "2024-02-20")
    df = tidy(days, {"t0_cal": 1.0, "lear_ens": 2.0})
    df.loc[df["delivery_date"] == days[0], "y"] = np.nan
    set_value(df, "lear_ens", days[4], "y_hat", np.nan)
    complete = st.complete_days(df)
    assert complete == days[1:]
    assert st.arm_missing(df, "lear_ens", complete) == [days[4]]
    assert st.p2_coverage(df, complete) == pytest.approx(18 / 19)
    with pytest.raises(ValueError):
        st.p2_coverage(df, [])


# ------------------------------------------------------------------ per-day tables


def test_per_day_mae_sums_every_real_hour():
    df = tidy(DAYS, {"a": 1.5, "b": -3.0})
    days = st.day_set(df, "a", "b", metric="mae")
    t = st.per_day(df, "a", "b", metric="mae", days=days)
    assert list(t.columns) == ["delivery_date", "method", "sum_abs_err", "n"]
    n = t.set_index(["delivery_date", "method"])["n"]
    assert n[(date(2024, 3, 31), "a")] == 23 and n[(date(2024, 10, 27), "b")] == 25 and n[(DAYS[0], "a")] == 24
    s = t.set_index(["delivery_date", "method"])["sum_abs_err"]
    assert s[(DAYS[0], "a")] == pytest.approx(1.5 * 24) and s[(date(2024, 10, 27), "b")] == pytest.approx(75.0)


def test_per_day_pinball_is_the_probe_pinball_summed_per_day():
    df = tidy(DAYS, {"a": noisy(4.0), "b": noisy(6.0, seed=1)}, spread=3.0)
    days = st.day_set(df, "a", "b", metric="pinball")
    t = st.per_day(df, "a", "b", metric="pinball", days=days)
    sub = df.loc[(df["method"] == "a") & (df["delivery_date"] == DAYS[3])]
    manual = pr.pinball(sub["y"].to_numpy(), sub[list(st.Q_COLUMNS)].to_numpy(), px.LEVELS).sum()
    assert t.set_index(["delivery_date", "method"]).loc[(DAYS[3], "a"), "sum_abs_err"] == pytest.approx(manual)
    ref = run_probes.per_day_pinball(df, "a", "b", levels=px.LEVELS)  # identical when every hour is finite
    merged = t.merge(ref, on=["delivery_date", "method"], suffixes=("", "_ref"))
    assert len(merged) == len(t)
    np.testing.assert_allclose(merged["sum_abs_err"], merged["sum_abs_err_ref"])
    assert (merged["n"] == merged["n_ref"]).all()


def test_per_day_never_drops_a_single_hour():
    df = tidy(DAYS[:6], {"a": 1.0, "b": 2.0})
    set_value(df, "a", DAYS[2], "y_hat", np.nan)
    t = st.per_day(df, "a", "b", metric="mae", days=DAYS[:6])  # a day outside the day set, on purpose
    row = t.set_index(["delivery_date", "method"]).loc[(DAYS[2], "a")]
    assert np.isnan(row["sum_abs_err"]) and row["n"] == 24
    with pytest.raises(st.StatisticsError):
        st.compare(t, "a", "b")


def test_per_day_hour_mask_keeps_only_its_hours_and_drops_empty_days_for_both():
    df = tidy(DAYS[:4], {"a": 1.0, "b": 2.0})
    mask = (df["local_time"].dt.hour == 13) & (df["delivery_date"] != DAYS[1])
    t = st.per_day(df, "a", "b", metric="mae", days=DAYS[:4], hours=mask)
    assert set(t["delivery_date"]) == {DAYS[0], DAYS[2], DAYS[3]}
    assert (t["n"] == 1).all() and len(t) == 6
    t2 = st.per_day(df, "a", "b", metric="mae", days=DAYS[:4], hours=mask.to_numpy())
    pd.testing.assert_frame_equal(t, t2)
    with pytest.raises(ValueError):
        st.per_day(df, "a", "b", metric="mae", days=DAYS[:4], hours=np.ones(3, dtype=bool))


# ------------------------------------------------------------------ compare, yearly, coverage


def _two_year_days(n=40):
    return px.days_between("2024-05-01", "2024-12-31")[:n] + px.days_between("2025-03-01", "2025-12-31")[:n]


def test_compare_skill_bootstrap_interval_and_p():
    days = _two_year_days()
    df = tidy(days, {"a": noisy(4.0), "b": noisy(5.0, seed=3)})
    t = st.per_day(df, "a", "b", metric="mae", days=st.day_set(df, "a", "b", metric="mae"))
    c = st.compare(t, "a", "b")
    sums = t.groupby("method")["sum_abs_err"].sum()
    assert c["status"] == "ok" and c["skill"] == pytest.approx(1 - sums["a"] / sums["b"], abs=1e-14)
    boot = metrics.bootstrap_skill(t, model="a", reference="b", block_days=14, samples=2000, seed=0,
                                   return_draws=True)
    draws = boot["draws"]
    assert c["ci95"] == pytest.approx(list(np.percentile(draws, [2.5, 97.5])))
    assert c["p_one_sided"] == pytest.approx((1 + np.sum(draws <= 0.0)) / 2001)
    assert c["days"] == len(days) and c["hours"] == int(t.loc[t["method"] == "a", "n"].sum())
    assert c["loss_arm"] == pytest.approx(sums["a"] / c["hours"])
    wide = t.pivot(index="delivery_date", columns="method", values="sum_abs_err")
    assert c["days_won"] == int((wide["a"] < wide["b"]).sum()) and c["days_lost"] == int((wide["a"] > wide["b"]).sum())


def test_compare_margin_p_for_p2():
    days = _two_year_days()
    df = tidy(days, {"t0_cal": noisy(5.2, seed=5), "lear_ens": noisy(5.0, seed=6)})
    t = st.per_day(df, "t0_cal", "lear_ens", metric="mae", days=days)
    sup = st.compare(t, "t0_cal", "lear_ens")
    ni = st.compare(t, "t0_cal", "lear_ens", margin=st.MARGINS["P2"])
    draws = metrics.bootstrap_skill(t, model="t0_cal", reference="lear_ens", block_days=14, samples=2000, seed=0,
                                    return_draws=True)["draws"]
    assert ni["m"] == -0.05 and ni["p_one_sided"] == pytest.approx((1 + np.sum(draws <= -0.05)) / 2001)
    assert sup["p_one_sided"] == pytest.approx((1 + np.sum(draws <= 0.0)) / 2001)
    assert ni["p_one_sided"] <= sup["p_one_sided"] and ni["skill"] == sup["skill"]


def test_compare_checks_the_table_and_refuses_non_finite():
    days = DAYS[:10]
    df = tidy(days, {"a": noisy(2.0), "b": noisy(3.0, seed=2)})
    t = st.per_day(df, "a", "b", metric="mae", days=days)
    unbalanced = t.copy()
    unbalanced.loc[unbalanced.index[0], "n"] += 1
    with pytest.raises(st.StatisticsError):
        st.compare(unbalanced, "a", "b")
    with pytest.raises(st.StatisticsError):  # a day only one arm has
        st.compare(t.drop(index=t.index[(t["method"] == "b")][0]), "a", "b")
    zero = t.copy()
    zero.loc[zero["method"] == "b", "sum_abs_err"] = 0.0
    with pytest.raises(st.StatisticsError):  # non-finite pooled skill
        st.compare(zero, "a", "b")
    two = t.loc[t["delivery_date"].isin(days[:2])].copy()
    two.loc[(two["method"] == "b") & (two["delivery_date"] == days[0]), "sum_abs_err"] = 0.0
    with pytest.raises(st.StatisticsError):  # the pooled skill is finite, some draws are not
        st.compare(two, "a", "b")


def test_uncomputed_fields_call_no_metrics_function(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a metrics function was called")

    for name in ("bootstrap_skill", "_day_pivot", "concentration", "bootstrap_sensitivity"):
        monkeypatch.setattr(metrics, name, boom)
    monkeypatch.setattr(referee_stats, "power_table", boom)
    empty = st.per_day(tidy(DAYS[:2], {"a": 1, "b": 2}), "a", "b", metric="mae", days=[])
    assert empty.empty
    assert st.compare(None, "a", "b")["status"] == "not run"
    assert st.compare(empty, "a", "b")["status"] == "no days"
    assert st.compare(empty, "a", "b", scored=False)["status"] == "not run"
    assert st.yearly(None, "a", "b") == {"2024": "not run", "2025": "not run"}
    assert st.yearly(empty, "a", "b") == {"2024": "no days", "2025": "no days"}
    assert st.tables(None, "a", "b") == {"status": "not run"} and st.tables(empty, "a", "b") == {"status": "no days"}
    assert st.carry_forward(None, "a", "b", state="won")["status"] == "not run"
    assert st.carry_forward(empty, "a", "b", state="won")["status"] == "no days"
    df = tidy(DAYS[:3], {"a": 1.0, "b": 2.0})
    res, table = st.comparison(df, "a", "lear_ens", metric="mae", allowed_days=None, scored={"a"}, k1_passed=False)
    assert res["status"] == "not run" and table is None and res["yearly"]["2025"] == "not run"
    assert res["cause"] == "lear_ens not scored (K1 failed)"
    assert st.rmae(df, "t0_cal_wx", "a", allowed_days=None, scored={"a"}, k3_passed=False)["status"] == "not run"
    assert st.tables(empty, "a", "b", scored=False) == {"status": "not run"}
    res, table = st.comparison(df, "a", "b", metric="mae", allowed_days=[date(2023, 1, 1)], scored={"a", "b"})
    assert res["status"] == "no days" and table.empty and res["yearly"]["2024"] == "no days"
    sl = st.slices(df, "a", "b", metric="mae", days=None, scored=False)
    assert sl[st.SLICE_APR_SEP]["status"] == "not run" and sl[st.SLICE_YEAR]["2024"]["status"] == "not run"
    sl = st.slices(df, "a", "b", metric="mae", days=[])
    assert all(v["status"] == "no days" for k, v in sl.items() if k not in (st.SLICE_YEAR, st.SLICE_QUARTER))


def test_yearly_skill_and_an_empty_year():
    days = _two_year_days(20)
    df = tidy(days, {"a": noisy(3.0), "b": noisy(4.0, seed=9)})
    t = st.per_day(df, "a", "b", metric="mae", days=days)
    yr = st.yearly(t, "a", "b")
    for y in ("2024", "2025"):
        sub = t.loc[[d.year == int(y) for d in t["delivery_date"]]]
        s = sub.groupby("method")["sum_abs_err"].sum()
        assert yr[y] == pytest.approx(1 - s["a"] / s["b"])
    only_2024 = t.loc[[d.year == 2024 for d in t["delivery_date"]]]
    yr = st.yearly(only_2024, "a", "b")
    assert yr["2025"] == "no days" and isinstance(yr["2024"], float)
    v = st.states(_results(P1={"yearly": yr}))
    assert v["P1"]["state"] == "not stable"  # a year printed 'no days' fails statistics.per_year_rule


def test_coverage_is_closed_unclipped_and_unsorted():
    days = DAYS[:2]
    df = tidy(days, {"t0_cal": 0.0}, spread=5.0)  # q10 = y - 10, q90 = y + 10
    rows = df.index[df["method"] == "t0_cal"]
    y = df.loc[rows, "y"].to_numpy()
    df.loc[rows[0], "q10"] = y[0]             # y == q10: covered
    df.loc[rows[1], "q90"] = y[1]             # y == q90: covered
    df.loc[rows[2], "q10"] = y[2] + 1e-9      # just above: not covered
    df.loc[rows[3], ["q10", "q90"]] = [y[3] + 10, y[3] - 10]  # unsorted: not covered, never swapped
    n = len(rows)
    assert st.coverage(df, "t0_cal", days) == pytest.approx((n - 2) / n)
    assert st.coverage(df, "t0_cal", []) == "no days"
    set_value(df, "t0_cal", days[1], "q90", np.nan)
    with pytest.raises(st.StatisticsError):
        st.coverage(df, "t0_cal", days)


# ------------------------------------------------------------------ verdict states


def _results(**over):
    base = {"P1": {"runnable": True, "skill": 0.10, "p": 0.001, "yearly": {"2024": 0.08, "2025": 0.12},
                   "ci95": [0.05, 0.15]},
            "P2": {"runnable": True, "skill": -0.03, "p": 0.001, "yearly": {"2024": -0.04, "2025": -0.01}},
            "P3": {"runnable": True, "skill": 0.10, "p": 0.001, "yearly": {"2024": 0.1, "2025": 0.1},
                   "coverage": 0.80},
            "P4": {"runnable": True, "skill": 0.05, "p": 0.001, "yearly": {"2024": 0.04, "2025": 0.06}}}
    for pid, changes in over.items():
        base[pid] = {**base[pid], **changes}
    return base


def _st(**over):
    return {pid: v["state"] for pid, v in st.states(_results(**over)).items()}


def test_every_primary_can_be_won_and_holm_is_run_covariates_holm():
    v = st.states(_results())
    assert {pid: x["state"] for pid, x in v.items()} == dict.fromkeys(st.FAMILY, "won")
    assert [v[p]["p_holm"] for p in st.FAMILY] == pytest.approx(rc.holm([0.001] * 4))


def test_lost_on_threshold_and_on_holm():
    assert _st(P1={"skill": 0.0})["P1"] == "lost"               # strictly above 0
    assert _st(P1={"skill": "no days"})["P1"] == "lost"
    assert _st(P2={"skill": -0.05})["P2"] == "lost"             # strictly above -0.05
    assert _st(P2={"skill": -0.0499})["P2"] == "won"
    assert _st(P3={"skill": -0.01})["P3"] == "lost"
    assert _st(P4={"skill": 0.0})["P4"] == "lost"
    # raw p < 0.05 everywhere, but Holm lifts three of them to 0.09
    over = {"P1": {"p": 0.03}, "P2": {"p": 0.001}, "P3": {"p": 0.03}, "P4": {"p": 0.03}}
    v = st.states(_results(**over))
    assert [v[p]["p_holm"] for p in st.FAMILY] == pytest.approx(rc.holm([0.03, 0.001, 0.03, 0.03]))
    assert {p: v[p]["state"] for p in st.FAMILY} == {"P1": "lost", "P2": "won", "P3": "lost", "P4": "lost"}
    assert _st(P1={"p": 0.05})["P1"] == "lost"


def test_not_runnable_enters_holm_with_p_one():
    v = st.states(_results(P2={"runnable": False, "cause": "K1 failed", "p": 0.0001}))
    assert v["P2"]["state"] == "not runnable" and v["P2"]["cause"] == "K1 failed"
    assert v["P2"]["p_holm_input"] == 1.0 and v["P2"]["p"] == 0.0001
    assert [v[p]["p_holm"] for p in st.FAMILY] == pytest.approx(rc.holm([0.001, 1.0, 0.001, 0.001]))
    assert v["P2"]["p_holm"] == 1.0
    v = st.states(_results(P4={"skill": "no days", "p": "no days", "yearly": {"2024": "no days", "2025": "no days"}}))
    assert v["P4"]["state"] == "not runnable" and v["P4"]["cause"] == "no P4 day scored"
    v = st.states(_results(P4={"skill": "not run", "p": "not run"}, P2={"skill": "not run", "p": "not run"}))
    assert v["P4"]["state"] == v["P2"]["state"] == "not runnable" and v["P4"]["p_holm_input"] == 1.0
    assert "K3" in v["P4"]["cause"] and "K1" in v["P2"]["cause"]
    with pytest.raises(ValueError):
        st.states(_results(P1={"runnable": False}))
    with pytest.raises(ValueError):
        st.states(_results(P3={"runnable": False}))
    # a runnable primary whose p was not computed enters Holm with p = 1 too
    assert st.states(_results(P1={"skill": "no days", "p": "no days"}))["P1"]["p_holm_input"] == 1.0


def test_not_stable_per_year():
    assert _st(P1={"yearly": {"2024": 0.1, "2025": 0.0}})["P1"] == "not stable"
    assert _st(P1={"yearly": {"2024": -0.2, "2025": 0.3}})["P1"] == "not stable"
    assert _st(P2={"yearly": {"2024": -0.05, "2025": 0.1}})["P2"] == "not stable"
    assert _st(P2={"yearly": {"2024": -0.049, "2025": 0.1}})["P2"] == "won"
    assert _st(P4={"yearly": {"2024": "no days", "2025": 0.1}})["P4"] == "not stable"
    assert _st(P3={"yearly": {"2025": 0.1}})["P3"] == "not stable"  # a missing year fails too


def test_p3_lost_on_coverage_closed_band():
    assert _st(P3={"coverage": 0.70})["P3"] == "won"
    assert _st(P3={"coverage": 0.90})["P3"] == "won"
    assert _st(P3={"coverage": 0.6999999})["P3"] == "lost on coverage"
    assert _st(P3={"coverage": 0.9000001})["P3"] == "lost on coverage"
    assert _st(P3={"coverage": 0.5, "yearly": {"2024": -0.1, "2025": 0.1}})["P3"] == "not stable"  # first applies
    assert _st(P3={"coverage": 0.5, "skill": 0.0})["P3"] == "lost"
    with pytest.raises(ValueError):
        st.states(_results(P3={"coverage": "no days"}))


# ------------------------------------------------------------------ the reading table


P2_ROWS = {"won": "P1 won, P2 won", "lost": "P1 won, P2 lost or not stable",
           "not stable": "P1 won, P2 lost or not stable", "not runnable": "P1 won, P2 not runnable"}
BEATS = {"pooled": 0.02, "2024": 0.01, "2025": 0.03}
MISSES = {"pooled": 0.02, "2024": 0.01, "2025": -0.01}


def _rows(p1="won", p2="won", p3="won", p4="won", strict=None, **kw):
    return st.reading({"P1": p1, "P2": p2, "P3": p3, "P4": p4},
                      strict if strict is not None else {"best_simple_2023": BEATS}, **kw)


def test_the_p1_p2_row_for_every_combination():
    for p1, p2 in product(st.STATE_NAMES["P1"], st.STATE_NAMES["P2"]):
        row = _rows(p1, p2)[0]
        if p1 == "won":
            assert row == RT[P2_ROWS[p2]]
        elif p2 == "won":
            assert row == RT["P1 not won, P2 won"]
        else:
            expected = st.NOT_WON_BASE + (" " + st.NOT_WON_ADD_LEAR if p2 == "not runnable" else "")
            assert row == expected, (p1, p2)


def test_the_not_won_row_additions():
    row = _rows("lost", "not runnable", p1_ci95=[-0.2, -0.01])[0]
    assert row == " ".join([st.NOT_WON_BASE, st.NOT_WON_ADD_LEAR, st.NOT_WON_ADD_INTERVAL])
    assert _rows("lost", "lost", p1_ci95=[-0.2, 0.0])[0] == st.NOT_WON_BASE  # touching 0 is not entirely below
    assert _rows("not stable", "lost", p1_ci95=[-0.2, -0.1])[0] == st.NOT_WON_BASE + " " + st.NOT_WON_ADD_INTERVAL
    assert _rows("lost", "lost", p1_ci95="no days")[0] == st.NOT_WON_BASE
    v = st.states(_results(P1={"skill": -0.1, "ci95": [-0.15, -0.05]}, P2={"skill": -0.2}))  # ci95 via states()
    assert st.reading(v)[0] == st.NOT_WON_BASE + " " + st.NOT_WON_ADD_INTERVAL
    for s in (st.NOT_WON_BASE, st.NOT_WON_ADD_LEAR, st.NOT_WON_ADD_INTERVAL):
        assert s in RT["P1 not won, P2 not won"]


def test_the_p3_and_p4_rows():
    assert _rows(p3="won")[1] == RT["P3 won"]
    assert _rows(p3="lost on coverage")[1] == RT["P3 lost on coverage"]
    assert _rows(p3="lost")[1] == _rows(p3="not stable")[1] == RT["P3 lost or not stable"]
    assert _rows(p4="won")[2] == RT["P4 won"]
    assert _rows(p4="not runnable")[2] == RT["P4 not runnable"]
    assert _rows(p4="lost")[2] == _rows(p4="not stable")[2] == RT["P4 lost or not stable"]
    with pytest.raises(ValueError):
        _rows(p1="not runnable")
    with pytest.raises(ValueError):
        _rows(p4="lost on coverage")


def test_not_stable_rows_and_the_printing_order():
    rows = _rows("won", "not stable", "not stable", "lost")
    assert len(rows) == 3 + 2 + 1
    assert rows[3] == RT["not stable"].replace("<probe>", "P2") and rows[4].startswith("P3: the pooled result")
    assert "<probe>" not in "".join(rows)
    assert rows[5] == st.STRICT_NO_ALLOWANCE
    rows = _rows("not stable", "won", "won", "not stable")
    assert rows[3].startswith("P1:") and rows[4].startswith("P4:") and rows[-1] == st.STRICT_NOT_READ
    assert len(_rows()) == 4


def test_the_strict_row_read_only_when_p1_is_won():
    assert _rows(strict={"best_simple_2023": BEATS, "best_simple_2023_strict": BEATS})[-1] == st.STRICT_NO_ALLOWANCE
    assert _rows(strict={"best_simple_2023": MISSES, "best_simple_2023_strict": BEATS})[-1] == st.STRICT_OLD_RULE
    assert _rows(strict={"best_simple_2023": MISSES, "best_simple_2023_strict": MISSES})[-1] == st.STRICT_DEPENDS
    assert _rows(strict={"best_simple_2023": {"pooled": "no days", "2024": 1, "2025": 1},
                         "best_simple_2023_strict": {**BEATS, "2025": 0.0}})[-1] == st.STRICT_DEPENDS
    for p1 in ("lost", "not stable"):
        assert _rows(p1, strict={"best_simple_2023": BEATS})[-1] == st.STRICT_NOT_READ
        assert st.reading({"P1": p1, "P2": "won", "P3": "won", "P4": "won"})[-1] == st.STRICT_NOT_READ
    with pytest.raises(ValueError):
        st.reading({"P1": "won", "P2": "won", "P3": "won", "P4": "won"})


def test_every_printed_row_is_verbatim_spec_text():
    spec_text = " ".join(v for v in RT.values())
    for combo in product(*(st.STATE_NAMES[p] for p in st.FAMILY)):
        for strict in ({"best_simple_2023": BEATS}, {"best_simple_2023": MISSES, "best_simple_2023_strict": BEATS},
                       {}):
            rows = st.reading(dict(zip(st.FAMILY, combo)), strict, p1_ci95=[-1.0, -0.5])
            for row in rows:
                if row in RT.values() or row in {RT["not stable"].replace("<probe>", p) for p in st.FAMILY}:
                    continue
                if row.startswith(st.NOT_WON_BASE):
                    for part in (st.NOT_WON_BASE, st.NOT_WON_ADD_LEAR, st.NOT_WON_ADD_INTERVAL):
                        row = row.replace(part, "")
                    assert row.strip() == ""
                else:
                    assert row in spec_text, row


# ------------------------------------------------------------------ hour slices


def test_hour_slices():
    days = [date(2024, 1, 8), date(2024, 3, 31), date(2024, 10, 27), date(2024, 5, 1)]
    other = date(2024, 6, 3)

    def y_fn(idx, local):
        v = 30 + 40 * np.sin(2 * np.pi * (local.hour.to_numpy() - 9) / 24) + np.arange(len(idx)) * 0.01
        v[np.asarray(idx) == 4] = 5000.0  # the day outside the comparison's day set
        return v

    df = tidy(days + [other], {"a": 1.0, "b": -1.0}, y_fn=y_fn)
    m = st.hour_slices(df, days)
    assert set(m) == set(st.HOUR_SLICES)
    in_days = df["delivery_date"].isin(days)
    assert (m[st.SLICE_NEGATIVE] == (in_days & (df["y"] < 0))).all() and m[st.SLICE_NEGATIVE].any()
    unique_y = df.loc[in_days & (df["method"] == "a"), "y"].to_numpy()
    thr = np.quantile(np.abs(unique_y), 0.99)
    assert thr < 5000
    assert (m[st.SLICE_TOP] == (in_days & (df["y"].abs() >= thr))).all()
    assert m[st.SLICE_TOP][df["method"] == "a"].sum() == int((np.abs(unique_y) >= thr).sum())
    mid = df.loc[m[st.SLICE_MIDDAY]]
    assert set(mid["local_time"].dt.hour) == {11, 12, 13, 14, 15}
    assert mid.groupby(["delivery_date", "method"]).size().eq(5).all() and len(mid) == 5 * 4 * 2
    t = st.per_day(df, "a", "b", metric="mae", days=days, hours=m[st.SLICE_MIDDAY])
    assert (t["n"] == 5).all() and set(t["delivery_date"]) == set(days)
    neg_days = set(df.loc[m[st.SLICE_NEGATIVE], "delivery_date"])
    t = st.per_day(df, "a", "b", metric="mae", days=days, hours=m[st.SLICE_NEGATIVE])
    assert set(t["delivery_date"]) == neg_days


def test_day_slices_weekends_holidays_and_dst_weeks():
    test = st.period_days("test")
    assert st.dst_switch_days(test) == [date(2024, 3, 31), date(2024, 10, 27), date(2025, 3, 30), date(2025, 10, 26)]
    week = st.dst_week_days(test)
    assert len(week) == 28 and date(2024, 4, 6) in week and date(2024, 4, 7) not in week
    assert date(2024, 3, 30) not in week and date(2025, 11, 1) in week
    wh = st.weekend_holiday_days(px.days_between("2024-04-29", "2024-05-12"))
    assert wh == [date(2024, 5, 1), date(2024, 5, 4), date(2024, 5, 5), date(2024, 5, 8), date(2024, 5, 9),
                  date(2024, 5, 11), date(2024, 5, 12)]


def test_slices_cover_every_spec_slice(monkeypatch):
    days = px.days_between("2024-03-25", "2024-04-20") + px.days_between("2025-09-20", "2025-10-31")
    df = tidy(days, {"a": noisy(3.0), "b": noisy(4.0, seed=4)})
    ds = st.day_set(df, "a", "b", metric="mae")
    boot_days, real_boot = [], metrics.bootstrap_skill

    def spy(per_day_df, **kw):
        boot_days.append(frozenset(per_day_df["delivery_date"]))
        return real_boot(per_day_df, **kw)

    monkeypatch.setattr(metrics, "bootstrap_skill", spy)
    sl = st.slices(df, "a", "b", metric="mae", days=ds)
    assert set(sl) == set(ps.PRICE_SPEC["report_only"]["slices"])
    assert set(sl[st.SLICE_YEAR]) == {"2024", "2025"} and len(sl[st.SLICE_QUARTER]) == 8
    assert sl[st.SLICE_QUARTER]["2024Q3"]["status"] == "no days"
    assert sl[st.SLICE_QUARTER]["2024Q1"]["days"] == 7 and sl[st.SLICE_QUARTER]["2025Q4"]["days"] == 31
    assert sl[st.SLICE_APR_SEP]["days"] == 20 + 11
    assert sl[st.SLICE_DST]["days"] == 7 + 6  # 2024-03-31..04-06 and 2025-10-26..31
    table = st.per_day(df, "a", "b", metric="mae", days=ds)
    sub = table.loc[[d.year == 2025 for d in table["delivery_date"]]]
    assert sl[st.SLICE_YEAR]["2025"]["skill"] == pytest.approx(st.pooled_skill(sub, "a", "b"))
    assert sl[st.SLICE_MIDDAY]["hours"] == 5 * len(ds)
    # 'each year' is statistics.per_year_rule's skill only: no per-year bootstrap, interval or p (review D3)
    yr = st.yearly(table, "a", "b")
    assert sl[st.SLICE_YEAR] == {"2024": {"status": "ok", "arm": "a", "ref": "b", "skill": yr["2024"], "days": 27},
                                 "2025": {"status": "ok", "arm": "a", "ref": "b", "skill": yr["2025"], "days": 42}}
    year_sets = {frozenset(d for d in ds if d.year == y) for y in (2024, 2025)}
    assert boot_days and not year_sets & set(boot_days)  # the other slices are bootstrapped, no year alone is
    only_2024 = st.slices(df, "a", "b", metric="mae", days=[d for d in ds if d.year == 2024])
    assert only_2024[st.SLICE_YEAR]["2025"] == {"status": "no days", "arm": "a", "ref": "b"}


# ------------------------------------------------------------------ tables, secondaries


def test_tables_are_the_metrics_tables():
    days = _two_year_days(30)
    df = tidy(days, {"a": noisy(3.0), "b": noisy(4.0, seed=4)})
    t = st.per_day(df, "a", "b", metric="mae", days=days)
    out = st.tables(t, "a", "b")
    assert out["concentration"] == metrics.concentration(t, model="a", reference="b")
    sens = out["bootstrap_sensitivity"]
    assert [r["block_days"] for r in sens] == [1, 3, 7, 14, 30]
    assert sens == metrics.bootstrap_sensitivity(t, model="a", reference="b")


@pytest.mark.filterwarnings("ignore:invalid value encountered:RuntimeWarning")  # concentration's top-5 on 2 days
def test_tables_stop_on_a_non_finite_skill_or_draw(monkeypatch):
    days = DAYS[:10]
    df = tidy(days, {"a": noisy(2.0), "b": noisy(3.0, seed=2)})
    t = st.per_day(df, "a", "b", metric="mae", days=days)
    two = t.loc[t["delivery_date"].isin(days[:2])].copy()
    two.loc[(two["method"] == "b") & (two["delivery_date"] == days[0]), "sum_abs_err"] = 0.0
    metrics.concentration(two, model="a", reference="b")  # the pooled skill is finite ...
    with pytest.raises(ZeroDivisionError):  # ... but a resample has zero reference loss (review D4)
        metrics.bootstrap_sensitivity(two, model="a", reference="b", blocks=(1,), samples=2000, seed=0)
    with pytest.raises(st.StatisticsError, match="non-finite"):
        st.tables(two, "a", "b")
    unbalanced = t.copy()
    unbalanced.loc[unbalanced.index[0], "n"] += 1
    with pytest.raises(st.StatisticsError):
        st.tables(unbalanced, "a", "b")
    real_sens = metrics.bootstrap_sensitivity
    monkeypatch.setattr(metrics, "bootstrap_sensitivity",
                        lambda *a, **k: [{**r, "skill_hi95": float("nan")} for r in real_sens(*a, **k)])
    with pytest.raises(st.StatisticsError, match="block-length"):
        st.tables(t, "a", "b")

    def boom(*a, **k):
        raise AssertionError("a metrics table was computed")

    monkeypatch.setattr(metrics, "concentration", boom)
    monkeypatch.setattr(metrics, "bootstrap_sensitivity", boom)
    zero = t.copy()
    zero.loc[zero["method"] == "b", "sum_abs_err"] = 0.0
    with pytest.raises(st.StatisticsError):  # a non-finite pooled skill stops the run before any table
        st.tables(zero, "a", "b")


def test_a_missing_arm_reads_not_run_only_after_its_gate_failed():
    df = tidy(DAYS[:3], {"t0_cal": 1.0, "naive_std": 2.0})
    base = {"t0_cal", "naive_std"}
    gates_failed = {"k1_passed": False, "k3_passed": False}
    with pytest.raises(ValueError, match="prev_week"):  # never forecast, or renamed: an error, never 'not run'
        st.comparison(df, "t0_cal", "prev_week", metric="mae", allowed_days=None, scored=base, **gates_failed)
    with pytest.raises(ValueError, match="prev_week"):
        st.rmae(df, "t0_cal", "prev_week", allowed_days=None, scored=base, **gates_failed)
    for arm, gate in (("lear_ens", "K1"), (st.LEAR_BANDS, "K1"), ("t0_cal_wx", "K3")):
        flag = f"{gate.lower()}_passed"
        metric = "pinball" if arm == st.LEAR_BANDS else "mae"
        res, table = st.comparison(df, arm, "t0_cal", metric=metric, allowed_days=None, scored=base, **{flag: False})
        assert res["status"] == "not run" and table is None and res["cause"] == f"{arm} not scored ({gate} failed)"
        assert st.rmae(df, arm, "naive_std", allowed_days=None, scored=base, **{flag: False}) == {
            "status": "not run", "cause": f"{arm} not scored ({gate} failed)"}
        # a failed gate leaves its arm unscored even when the caller listed it
        res, _ = st.comparison(df, arm, "t0_cal", metric=metric, allowed_days=None, scored=base | {arm},
                               **{flag: False})
        assert res["status"] == "not run"
        for passed in (True, None):  # its gate passed (so it must have been scored), or the outcome is not given
            with pytest.raises(ValueError, match=arm):
                st.comparison(df, arm, "t0_cal", metric=metric, allowed_days=None, scored=base, **{flag: passed})
            with pytest.raises(ValueError, match=arm):
                st.rmae(df, arm, "naive_std", allowed_days=None, scored=base, **{flag: passed})
    # a gated arm scored after its gate passed but without a row reads 'no days', never 'not run'
    res, _ = st.comparison(df, "t0_cal_wx", "t0_cal", metric="mae", allowed_days=None, scored=base | {"t0_cal_wx"},
                           k3_passed=True)
    assert res["status"] == "no days" and res["yearly"] == {"2024": "no days", "2025": "no days"}
    assert st.rmae(df, "t0_cal_wx", "naive_std", allowed_days=None, scored=base | {"t0_cal_wx"},
                   k3_passed=True) == {"status": "no days"}
    with pytest.raises(ValueError, match="t0_cal_strict"):  # no gate applies to the strict arms either
        st.strict_skills(df, test_days=DAYS[:3])


def test_scored_arms_follow_the_gates():
    df = tidy(DAYS[:2], {"t0_cal": 1.0, "lear_ens": 2.0, st.LEAR_BANDS: 2.0, "t0_cal_wx": 1.0})
    assert st.scored_arms(df, k1_passed=False, k3_passed=False) == {"t0_cal"}
    assert st.scored_arms(df, k1_passed=True, k3_passed=False) == {"t0_cal", "lear_ens", st.LEAR_BANDS}
    no_rows = tidy(DAYS[:2], {"t0_cal": 1.0})  # a gate that passed scores its arm even with no row (review D1)
    assert st.scored_arms(no_rows, k1_passed=True, k3_passed=True) == {"t0_cal", "lear_ens", st.LEAR_BANDS,
                                                                        "t0_cal_wx"}
    assert st.scored_arms(no_rows, k1_passed=False, k3_passed=True, scored={"t0_cal", "lear_ens"}) == {
        "t0_cal", "t0_cal_wx"}


SECONDARY_ARMS = {"t0": noisy(3.0), "t0_cal": noisy(2.5, seed=1), "best_simple_2023": noisy(4.0, seed=2),
                  "naive_std": noisy(5.0, seed=3), "prev_week": noisy(6.0, seed=4), "lear_ens": noisy(3.5, seed=5),
                  "t0_cal_wx": noisy(2.4, seed=6), "t0_cal_strict": noisy(2.8, seed=7),
                  "best_simple_2023_strict": noisy(4.2, seed=8), "best_simple_eq": noisy(4.0, seed=2),
                  st.LEAR_BANDS: noisy(3.5, seed=5)}
SECONDARY_DAYS = px.days_between("2024-06-10", "2024-06-30")
GATES_PASSED = {"k1_passed": True, "k3_passed": True}


@pytest.fixture(scope="module")
def secondary_frame():
    return tidy(SECONDARY_DAYS, SECONDARY_ARMS)


def test_secondaries_rmae_and_rmse(secondary_frame):
    df, days = secondary_frame, SECONDARY_DAYS
    scored = st.scored_arms(df, **GATES_PASSED)
    out = st.secondaries(df, scored=scored, **GATES_PASSED, test_days=days, p4_rule_days=days[5:])
    assert list(out) == ps.PRICE_SPEC["report_only"]["secondaries"]
    assert all(out[k]["status"] == "ok" for k in st.SECONDARY_PAIRS)  # every arm ran: nothing reads 'not run'
    bands = out["lear_ens + empirical bands vs t0_cal bands"]  # computed once K1 passed (review D2)
    ref, _ = st.comparison(df, st.LEAR_BANDS, "t0_cal", metric="pinball", allowed_days=days, scored=scored)
    assert bands["metric"] == "pinball" and bands["skill"] == ref["skill"] and bands["days"] == len(days)
    r = out[st.RMAE_KEY]["naive_std"]["t0_cal"]
    s = df.loc[df["method"].isin(["t0_cal", "naive_std"])].assign(e=lambda f: (f["y"] - f["y_hat"]).abs())
    s = s.groupby("method")["e"].sum()
    assert r["rmae"] == pytest.approx(s["t0_cal"] / s["naive_std"]) and r["days"] == len(days)
    assert out[st.RMAE_KEY]["prev_week"]["t0_cal_wx"]["days"] == len(days) - 5
    assert "naive_std" not in out[st.RMAE_KEY]["naive_std"] and st.LEAR_BANDS not in out[st.RMAE_KEY]["prev_week"]
    assert "best_simple_eq" not in out[st.RMAE_KEY]["naive_std"]  # its medians are best_simple_2023's
    assert all(v["status"] == "ok" for ref in ("naive_std", "prev_week") for v in out[st.RMAE_KEY][ref].values())
    rm = out[st.RMSE_KEY]
    assert set(rm) == {"P1", "P2", "P4"} and rm["P4"]["days"] == len(days) - 5
    e = df.loc[df["method"] == "t0_cal", "y"] - df.loc[df["method"] == "t0_cal", "y_hat"]
    assert rm["P1"]["t0_cal"] == pytest.approx(float(np.sqrt(np.mean(e ** 2))))
    with pytest.raises(ValueError, match="weather_p4"):  # t0_cal_wx scored needs the weather day rule's days
        st.secondaries(df, scored=scored, **GATES_PASSED, test_days=days)


def test_secondaries_after_k1_and_k3_failed(secondary_frame):
    gated = ("lear_ens", st.LEAR_BANDS, "t0_cal_wx")
    df = secondary_frame.loc[~secondary_frame["method"].isin(gated)]
    failed = {"k1_passed": False, "k3_passed": False}
    out = st.secondaries(df, scored=st.scored_arms(df, **failed), **failed, test_days=SECONDARY_DAYS)
    not_run = {"lear_ens vs best_simple_2023": "lear_ens", "t0_cal vs lear_ens (superiority)": "lear_ens",
               "lear_ens + empirical bands vs t0_cal bands": st.LEAR_BANDS}
    for key in st.SECONDARY_PAIRS:
        if key in not_run:
            assert out[key]["status"] == "not run" and out[key]["cause"] == f"{not_run[key]} not scored (K1 failed)"
        else:
            assert out[key]["status"] == "ok", key
    for ref in ("naive_std", "prev_week"):
        rm = out[st.RMAE_KEY][ref]
        assert rm["lear_ens"] == {"status": "not run", "cause": "lear_ens not scored (K1 failed)"}
        assert rm["t0_cal_wx"] == {"status": "not run", "cause": "t0_cal_wx not scored (K3 failed)"}
        assert st.LEAR_BANDS not in rm and rm["t0_cal"]["status"] == "ok"
    assert out[st.RMSE_KEY]["P2"]["status"] == out[st.RMSE_KEY]["P4"]["status"] == "not run"
    assert out[st.RMSE_KEY]["P1"]["status"] == "ok"


def test_secondaries_lear_bands_after_k1_passed(secondary_frame):
    df = secondary_frame.loc[secondary_frame["method"] != st.LEAR_BANDS]  # K1 passed, but no lear_ens_eq row
    kw = {"test_days": SECONDARY_DAYS, "p4_rule_days": SECONDARY_DAYS}
    for gates in (GATES_PASSED, {}):  # given, or read from scored (lear_ens is there): never a silent 'not run'
        with pytest.raises(ValueError, match=f"{st.LEAR_BANDS} was not scored although K1 passed"):
            st.secondaries(df, scored=set(df["method"]), **gates, **kw)  # review D2 b
    no_lear = secondary_frame.loc[secondary_frame["method"] != "lear_ens"]  # bands without lear_ens
    with pytest.raises(ValueError, match="lear_ens was not scored although K1 passed"):
        st.secondaries(no_lear, scored=set(no_lear["method"]), **kw)
    out = st.secondaries(df, scored=st.scored_arms(df, **GATES_PASSED), **GATES_PASSED, **kw)
    assert out["lear_ens + empirical bands vs t0_cal bands"]["status"] == "no days"


def test_secondaries_read_gate_outcomes_from_scored_when_not_given(secondary_frame):
    """run_prices passes scored = the frame's arms (+ t0_cal_wx once K3 passed) and no gate flags."""
    df, days = secondary_frame, SECONDARY_DAYS
    given = st.secondaries(df, scored=st.scored_arms(df, **GATES_PASSED), **GATES_PASSED, test_days=days,
                           p4_rule_days=days)
    read = st.secondaries(df, scored=set(df["method"]), test_days=days, p4_rule_days=days)
    assert read.keys() == given.keys() and read[st.RMAE_KEY] == given[st.RMAE_KEY]
    assert all(read[k]["skill"] == given[k]["skill"] for k in st.SECONDARY_PAIRS)
    failed = {"k1_passed": False, "k3_passed": False}
    k1k3 = df.loc[~df["method"].isin(["lear_ens", st.LEAR_BANDS, "t0_cal_wx"])]
    given = st.secondaries(k1k3, scored=st.scored_arms(k1k3, **failed), **failed, test_days=days)
    read = st.secondaries(k1k3, scored=set(k1k3["method"]), test_days=days, p4_rule_days=[])
    assert read[st.RMAE_KEY] == given[st.RMAE_KEY] and read[st.RMSE_KEY] == given[st.RMSE_KEY]
    assert [read[k]["status"] for k in st.SECONDARY_PAIRS] == [given[k]["status"] for k in st.SECONDARY_PAIRS]
    # K3 passed with no P4 day kept: t0_cal_wx is in scored without a row, and reads 'no days'
    no_wx = df.loc[df["method"] != "t0_cal_wx"]
    out = st.secondaries(no_wx, scored=set(no_wx["method"]) | {"t0_cal_wx"}, test_days=days, p4_rule_days=[])
    assert out[st.RMAE_KEY]["naive_std"]["t0_cal_wx"] == {"status": "no days"}
    assert out[st.RMSE_KEY]["P4"] == {"status": "no days"}


def test_secondaries_rmae_refs_name_the_reference_arms(secondary_frame):
    df, days = secondary_frame, SECONDARY_DAYS
    kw = {**GATES_PASSED, "test_days": days, "p4_rule_days": days}
    plain = st.secondaries(df, scored=st.scored_arms(df, **GATES_PASSED), **kw)[st.RMAE_KEY]
    renamed = df.replace({"method": {"naive_std": "naive_std_ref"}})
    scored = st.scored_arms(renamed, **GATES_PASSED)
    with pytest.raises(ValueError, match="naive_std"):  # a renamed reference is never 'not run' (review D2 a)
        st.secondaries(renamed, scored=scored, **kw)
    rm = st.secondaries(renamed, scored=scored, rmae_refs={"naive_std": "naive_std_ref", "prev_week": "prev_week"},
                        **kw)[st.RMAE_KEY]
    assert set(rm) == {"naive_std", "prev_week"} and "naive_std_ref" not in rm["naive_std"]
    assert rm["naive_std"] == plain["naive_std"]
    assert rm["prev_week"]["naive_std_ref"] == plain["prev_week"]["naive_std"]
    with pytest.raises(ValueError, match="rmae_refs"):
        st.secondaries(renamed, scored=scored, rmae_refs={"naive_std": "naive_std_ref"}, **kw)


# ------------------------------------------------------------------ the primaries end to end


PRIMARY_ARMS = {"t0_cal": noisy(3.0, seed=1), "best_simple_2023": noisy(4.5, seed=2),
                "lear_ens": noisy(3.05, seed=3), "best_simple_eq": noisy(5.0, seed=4),
                "t0_cal_wx": noisy(2.7, seed=5), "t0_cal_strict": noisy(3.6, seed=6),
                "best_simple_2023_strict": noisy(4.8, seed=7), "t0": noisy(3.2, seed=8)}
PRIMARY_DAYS = px.days_between("2024-05-20", "2024-07-15") + px.days_between("2025-05-20", "2025-07-15")


@pytest.fixture(scope="module")
def primary_frame():
    return tidy(PRIMARY_DAYS, PRIMARY_ARMS, spread=2.0)


def test_primary_results_states_reading_and_summary(primary_frame):
    df = primary_frame
    res, tbl = st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=PRIMARY_DAYS,
                                  test_days=PRIMARY_DAYS)
    assert all(res[p]["status"] == "ok" for p in st.FAMILY)
    assert res["P4"]["days"] == len([d for d in PRIMARY_DAYS if d >= date(2024, 6, 6)])
    assert res["P1"]["days"] == len(PRIMARY_DAYS) and res["P2"]["p2_coverage"] == 1.0
    assert res["P2"]["compare"]["m"] == -0.05
    assert isinstance(res["P3"]["coverage"], float) and set(res["P3"]["coverage_yearly"]) == {"2024", "2025"}
    expected_cov = st.coverage(df, "t0_cal", PRIMARY_DAYS)
    assert res["P3"]["coverage"] == expected_cov
    v = st.states(res)
    assert [v[p]["p_holm"] for p in st.FAMILY] == pytest.approx(rc.holm([res[p]["p"] for p in st.FAMILY]))
    strict = st.strict_skills(df, test_days=PRIMARY_DAYS)
    assert set(strict) == {"best_simple_2023", "best_simple_2023_strict"} and strict["best_simple_2023"]["days"] > 0
    rows = st.reading(v, strict)
    lines = st.summary_lines(res, v, strict)
    assert lines[0] == "Status: " + ps.PRICE_SPEC["status"] and "discovery-grade" in lines[0]
    assert lines[-1] == ps.ATTRIBUTION
    for row in rows:
        assert f"- {row}" in lines
    text = "\n".join(lines)
    for p in st.FAMILY:
        assert f"{p} (" in text and "Holm p" in text
    assert "coverage" in text and "t0_cal_strict vs best_simple_2023_strict: pooled" in text
    cf = st.carry_forward_all(tbl, v)
    assert set(cf) == set(st.FAMILY) and all(cf[p]["status"] == "ok" for p in st.FAMILY)
    assert all(cf[p]["candidate"] is False for p in st.FAMILY if v[p]["state"] != "won")


def test_primary_results_when_gates_fail(primary_frame):
    df = primary_frame
    res, tbl = st.primary_results(df, k1_passed=False, k3_passed=False, p4_rule_days=None, test_days=PRIMARY_DAYS)
    assert res["P2"]["skill"] == "not run" and res["P2"]["runnable"] is False and res["P2"]["cause"] == "K1 failed"
    assert res["P4"]["skill"] == "not run" and res["P4"]["cause"] == "K3 failed" and tbl["P4"] is None
    assert res["P2"]["yearly"] == {"2024": "not run", "2025": "not run"}
    v = st.states(res)
    assert v["P2"]["state"] == v["P4"]["state"] == "not runnable"
    assert v["P2"]["p_holm_input"] == v["P4"]["p_holm_input"] == 1.0
    lines = st.summary_lines(res, v, st.strict_skills(df, test_days=PRIMARY_DAYS))
    assert "cause: K1 failed" in "\n".join(lines) and "pooled skill not run" in "\n".join(lines)
    with pytest.raises(ValueError):  # t0_cal_wx scored needs the weather day rule's days
        st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=None, test_days=PRIMARY_DAYS)
    res, _ = st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=[date(2024, 6, 1)],
                                test_days=PRIMARY_DAYS)
    assert res["P4"]["skill"] == "no days" and res["P4"]["cause"] == "no P4 day scored"
    assert st.states(res)["P4"]["state"] == "not runnable"


def test_p2_not_runnable_on_coverage_but_still_computed(primary_frame):
    df = primary_frame.copy()
    missing = PRIMARY_DAYS[::10]  # 12 of 114 days: coverage 0.895 < 0.95
    for d in missing:
        set_value(df, "lear_ens", d, "y_hat", np.nan)
    res, _ = st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=PRIMARY_DAYS,
                                test_days=PRIMARY_DAYS)
    assert res["P2"]["p2_coverage"] == pytest.approx(1 - len(missing) / len(PRIMARY_DAYS))
    assert res["P2"]["runnable"] is False and "p2_coverage" in res["P2"]["cause"]
    assert isinstance(res["P2"]["skill"], float) and res["P2"]["days"] == len(PRIMARY_DAYS) - len(missing)
    assert res["P1"]["days"] == len(PRIMARY_DAYS)  # lear_ens's missing days never leave P1's day set
    v = st.states(res)
    assert v["P2"]["state"] == "not runnable" and v["P2"]["p_holm_input"] == 1.0


def test_gates_passed_but_no_row_reads_no_days_not_not_run(primary_frame):
    """Review D1 (test gap 4): K3 passed but no day passed weather_p4.day_rule, so the runner wrote no t0_cal_wx
    row; K1 passed but lear_ens wrote no row. Both read 'no days' (never 'not run') with their own cause."""
    df = primary_frame.loc[~primary_frame["method"].isin(["t0_cal_wx", "lear_ens"])]
    strict = st.strict_skills(df, test_days=PRIMARY_DAYS)
    for rule_days in ([], PRIMARY_DAYS):
        res, tbl = st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=rule_days,
                                      test_days=PRIMARY_DAYS)
        p4 = res["P4"]
        assert p4["skill"] == p4["ci95"] == p4["p"] == p4["days"] == "no days" and tbl["P4"].empty
        assert p4["yearly"] == {"2024": "no days", "2025": "no days"} and p4["cause"] == "no P4 day scored"
        p2 = res["P2"]
        assert p2["skill"] == "no days" and p2["p2_coverage"] == 0.0 and p2["cause"] == "p2_coverage 0.0000 < 0.95"
        v = st.states(res)
        assert v["P4"]["state"] == v["P2"]["state"] == "not runnable" and v["P4"]["cause"] == "no P4 day scored"
        assert v["P4"]["p_holm_input"] == v["P2"]["p_holm_input"] == 1.0
        assert st.reading(v, strict)[2] == RT["P4 not runnable"]
        p4_line = next(x for x in st.summary_lines(res, v, strict) if x.startswith("  - P4 ("))
        assert "cause: no P4 day scored" in p4_line and "pooled skill no days" in p4_line
        assert "not run" not in p4_line.replace("state 'not runnable'", "")
        # the report-only readers of the same empty day set say 'no days' too (never 'not run')
        assert st.carry_forward_all(tbl, v)["P4"]["status"] == "no days"
        assert st.tables(tbl["P4"], "t0_cal_wx", "t0_cal") == {"status": "no days"}
        sl = st.slices(df, "t0_cal_wx", "t0_cal", metric="mae", days=[])
        assert sl[st.SLICE_APR_SEP]["status"] == "no days" and sl[st.SLICE_NEGATIVE]["status"] == "no days"


def test_p2_coverage_bound_is_inclusive():
    """Test gap 1: statistics.p2_coverage '>= 95%' -- 19 of 20 complete test days is runnable, 18 of 20 is not."""
    days = px.days_between("2024-06-10", "2024-06-29")
    arms = {k: PRIMARY_ARMS[k] for k in ("t0_cal", "best_simple_2023", "lear_ens", "best_simple_eq", "t0_cal_wx")}
    for n_missing, runnable in ((0, True), (1, True), (2, False)):
        df = tidy(days, arms, spread=2.0)
        for d in days[3:3 + n_missing]:
            set_value(df, "lear_ens", d, "y_hat", np.nan)
        res, _ = st.primary_results(df, k1_passed=True, k3_passed=True, p4_rule_days=days, test_days=days)
        assert res["P2"]["p2_coverage"] == (20 - n_missing) / 20 and res["P2"]["days"] == 20 - n_missing
        assert res["P2"]["runnable"] is runnable, n_missing
        v = st.states(res)
        assert (v["P2"]["state"] != "not runnable") is runnable
        assert (v["P2"]["p_holm_input"] == res["P2"]["p"]) is runnable
    assert 19 / 20 == st.P2_COVERAGE_MIN  # exactly on the bound, in floating point too


def test_p4_first_day_moves_later_never_earlier(monkeypatch, primary_frame):
    """Test gap 3: periods.p4_first_day_rule -- AVAIL.p4_first_day may move P4's first day later, never earlier;
    P4's day set and its 2024 part both start there."""
    rule = px.days_between("2024-05-01", "2024-08-31") + [date(2025, 12, 31), date(2026, 1, 1)]
    assert st.p4_allowed_days(rule)[0] == date(2024, 6, 6) and st.p4_allowed_days(rule)[-1] == date(2025, 12, 31)
    monkeypatch.setitem(ps.AVAIL, "p4_first_day", "2024-07-15")
    assert st.p4_allowed_days(rule)[0] == date(2024, 7, 15)
    assert len(st.p4_allowed_days(rule)) == len(px.days_between("2024-07-15", "2024-08-31")) + 1
    for earlier in ("2024-05-10", None):  # never earlier than periods.p4_days
        monkeypatch.setitem(ps.AVAIL, "p4_first_day", earlier)
        assert st.p4_allowed_days(rule)[0] == date(2024, 6, 6)
    monkeypatch.setitem(ps.AVAIL, "p4_first_day", date(2024, 7, 1))
    res, tbl = st.primary_results(primary_frame, k1_passed=True, k3_passed=True, p4_rule_days=PRIMARY_DAYS,
                                  test_days=PRIMARY_DAYS)
    kept = [d for d in PRIMARY_DAYS if d >= date(2024, 7, 1)]
    assert res["P4"]["days"] == len(kept) and min(tbl["P4"]["delivery_date"]) == date(2024, 7, 1)
    t2024 = tbl["P4"].loc[[d.year == 2024 for d in tbl["P4"]["delivery_date"]]]
    assert t2024["delivery_date"].nunique() == 15  # 2024-07-01..15
    assert res["P4"]["yearly"]["2024"] == st.pooled_skill(t2024, "t0_cal_wx", "t0_cal")


# ------------------------------------------------------------------ carry forward


def _per_day_table(days, arm_level, ref_level, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for d in days:
        common = rng.normal(0, 20)
        rows.append({"delivery_date": d, "method": "arm", "sum_abs_err": arm_level * 24 + common + rng.normal(0, 5),
                     "n": 24})
        rows.append({"delivery_date": d, "method": "ref", "sum_abs_err": ref_level * 24 + common + rng.normal(0, 5),
                     "n": 24})
    return pd.DataFrame(rows)


def test_carry_forward_rule():
    days = st.period_days("selection") + st.period_days("test")  # 2023 rows are not in A (test gap 2)
    t = _per_day_table(days, 6.0, 10.0)
    out = st.carry_forward(t, "arm", "ref", state="won")
    a = t.loc[[d.month in range(4, 10) and d.year in (2024, 2025) for d in t["delivery_date"]]]
    assert out["days"] == a["delivery_date"].nunique() == 2 * 183
    assert st.carry_forward(t.loc[[d.year == 2023 for d in t["delivery_date"]]], "arm", "ref",
                            state="won")["status"] == "no days"
    sums = a.groupby("method")["sum_abs_err"].sum()
    assert out["S"] == pytest.approx(1 - sums["arm"] / sums["ref"])
    power = referee_stats.power_table(a, "arm", "ref", alpha=0.0125)
    assert out["M"] == power["min_detectable_skill"]["12"]
    assert out["block_sd"] == power["block_sd_mw"] and out["ref_mae"] == power["ref_mae_mw"]
    assert set(out["M_info"]) == {"0.0125/2", "0.0125/3", "0.0125/4"}
    assert out["M_info"]["0.0125/4"] == referee_stats.power_table(a, "arm", "ref", alpha=0.0125 / 4)[
        "min_detectable_skill"]["12"]
    assert out["delta"] == max(d for d in (0.0, 0.05, 0.10, 0.20) if out["S"] - d >= out["M"])
    assert out["delta"] == 0.20 and out["candidate"] is True
    assert st.carry_forward(t, "arm", "ref", state="not stable")["candidate"] is False
    assert st.carry_forward(t, "arm", "ref")["candidate"] is False  # no state given: never a candidate


def test_carry_forward_deltas_and_no_candidate():
    days = st.period_days("test")
    t = _per_day_table(days, 9.0, 10.0, seed=1)
    out = st.carry_forward(t, "arm", "ref", state="won")
    passing = [d for d in (0.0, 0.05, 0.10, 0.20) if out["S"] - d >= out["M"]]
    assert out["delta"] == (max(passing) if passing else None)
    assert out["delta"] not in (0.20,)
    fixed = st.carry_forward(t, "arm", "ref", lambda a, arm, ref: out["M"] + 0.07, state="won")
    assert fixed["S"] == pytest.approx(out["M"] + 0.07) and fixed["delta"] == 0.05 and fixed["candidate"]
    low = st.carry_forward(t, "arm", "ref", lambda a, arm, ref: out["M"] - 0.001, state="won")
    assert low["delta"] is None and low["candidate"] is False
    winter = t.loc[[d.month in (1, 2, 3, 10, 11, 12) for d in t["delivery_date"]]]
    assert st.carry_forward(winter, "arm", "ref", state="won")["status"] == "no days"
    short = t.loc[[d.month == 4 and d.year == 2024 and d.day <= 20 for d in t["delivery_date"]]]
    out = st.carry_forward(short, "arm", "ref", state="won")
    assert out["M"] is None and "power_error" in out and out["candidate"] is False


# ------------------------------------------------------------------ on a real price backtest frame


def test_on_a_real_price_backtest_frame():
    from test_price_exp import prices, t0

    s = prices() - 40.0  # negative prices too
    days = px.days_between("2024-01-08", "2024-02-18")
    ws = px.build_price_windows(s, days)
    rules = px.simple_rules()
    best = px.Renamed(rules["naive_std"], "best_simple_2023")
    eq = px.PriceEmpiricalQuantiles(base=best)
    df = px.run_price_backtest(s, [best, t0("t0_cal"), eq], ws)
    for arm, ref, metric in (("t0_cal", "best_simple_2023", "mae"), ("t0_cal", "best_simple_eq", "pinball")):
        ds = st.day_set(df, arm, ref, metric=metric, allowed_days=st.period_days("test"))
        assert ds == days
        table = st.per_day(df, arm, ref, metric=metric, days=ds)
        c = st.compare(table, arm, ref)
        assert c["status"] == "ok" and np.isfinite(c["skill"]) and c["days"] == len(days)
        assert c["hours"] == 24 * len(days)
    assert 0.0 <= st.coverage(df, "t0_cal", ds) <= 1.0
    m = st.hour_slices(df, ds)
    assert m[st.SLICE_NEGATIVE].any()
    assert st.yearly(table, "t0_cal", "best_simple_eq")["2025"] == "no days"
