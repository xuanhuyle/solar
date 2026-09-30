"""Experiment 4's runner: the licence rule, the K1 and K2 logs, the order of the stops and an offline end-to-end
scored run (synthetic prices, a stand-in for t0, the gates stubbed). Nothing here fetches data or loads t0."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from datetime import date
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import run_prices as rp
from engine import zones
from solarbench import price_data as pd_
from solarbench import price_exp as px
from solarbench import price_run as pr_
from solarbench import price_spec as ps
from solarbench import price_stats as st

#: The stand-in t0 reports replacing non-finite output (t0's own warning) for every row whose context ends with
#: SENTINEL; the synthetic prices put it on the last hour before SANITISED_DAY, so the normal-window t0 arms have
#: no forecast that day ('sanitised'), while t0_cal_strict (context ending at 12:00 D-1) is untouched.
SANITISED_DAY = date(2024, 9, 10)
SENTINEL = 4321.0
NAN_DAY = date(2024, 8, 14)  # the one injected NaN price day (an incomplete test day)


class EchoT0:
    """Stands in for t0 (as tests/test_price_exp.py): a weighted sum of the context plus the horizon covariates."""

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch

        raw = torch.as_tensor(context, dtype=torch.float64)
        if bool((raw[:, -1] == SENTINEL).any()):
            logging.getLogger("t0.model.model").warning("replaced 3 non-finite prediction values")
        ctx = torch.nan_to_num(raw)
        T = ctx.shape[-1]
        w = torch.linspace(0.1, 1.0, T, dtype=torch.float64)
        median = ((ctx * w).sum(dim=1, keepdim=True) / w.sum() + 0.5 * ctx[:, -1:]).repeat(1, horizon)
        if future_covariates is not None:
            fut = torch.nan_to_num(torch.as_tensor(future_covariates, dtype=torch.float64))
            median = median + fut[:, :, T:T + horizon].sum(dim=1) * 1e-3 + 1e-6 * fut[:, :, :T].sum(dim=(1, 2))[:, None]
        spread = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=torch.float64)
        return SimpleNamespace(median=median, quantiles=median[:, :, None] + spread[None, None, :] * 5.0)

LICENCE = ps.AVAIL["licence_info"][0]


def _ec_file(tmp_path, name, licence):
    body = {"unix_seconds": [1704063600], "price": [50.0]}
    if licence is not None:
        body["license_info"] = licence
    path = tmp_path / name
    path.write_text(json.dumps(body), encoding="utf-8")
    return path


def test_the_licence_rule_refuses_a_missing_a_failing_or_an_unrecorded_string(tmp_path):
    good = _ec_file(tmp_path, "good.json", LICENCE)
    assert pd_.licence_refusals([good], [LICENCE]) == []
    missing = _ec_file(tmp_path, "missing.json", None)
    wrong = _ec_file(tmp_path, "wrong.json", "CC BY 4.0 from someone else")
    other = _ec_file(tmp_path, "other.json", "CC BY 4.0 from Bundesnetzagentur | SMARD.de (new wording)")
    bad = pd_.licence_refusals([good, missing, wrong, other], [LICENCE])
    assert [b.split(":")[0] for b in bad] == ["missing.json", "wrong.json", "other.json"]


def test_k1_counts_only_the_first_three_real_attempts_with_this_lear(tmp_path, monkeypatch):
    log = tmp_path / "k1_attempts.jsonl"
    monkeypatch.setattr(pr_, "K1_LOG", log)
    assert pr_.k1_status("abc") == {"attempts": 0, "passed": False, "lear_sha256": "abc", "passing_attempt": None,
                                    "over_budget": False, "log_present": False, "log_sha256": None}
    rows = [{"run_id": "s", "smoke": True, "pass": False, "lear_sha256": "abc"},
            {"run_id": "1", "pass": False, "lear_sha256": "old", "counts_as_attempt": True},
            {"run_id": "x", "pass": False, "lear_sha256": "abc", "counts_as_attempt": False},
            {"run_id": "2", "pass": True, "lear_sha256": "old", "counts_as_attempt": True}]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    st = pr_.k1_status("abc")
    assert st["attempts"] == 2 and not st["passed"]  # the pass ran another lear.py
    assert pr_.k1_status("old")["passed"] and pr_.k1_status("old")["passing_attempt"] == "2"
    rows += [{"run_id": "3", "pass": False, "lear_sha256": "abc"}, {"run_id": "4", "pass": True, "lear_sha256": "abc"}]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    st = pr_.k1_status("abc")
    assert st["attempts"] == 4 and st["over_budget"] and not st["passed"]  # a fourth attempt never counts


# ---------------------------------------------------------------------------- the K1 and K2 logs (tracked)


def _git_checkout() -> bool:
    return (pr_.ROOT / ".git").exists()


@pytest.mark.skipif(not _git_checkout(), reason="not a git checkout")
def test_the_k1_and_k2_logs_are_tracked_paths_never_git_ignored():
    """results/ is git-ignored: a log there never reaches a fresh checkout and reads as 'no attempt'."""
    assert pr_.K1_LOG.relative_to(pr_.ROOT).as_posix() == "docs/experiment_4/k1_attempts.jsonl"
    assert pr_.K2_LOG.relative_to(pr_.ROOT).as_posix() == "docs/experiment_4/k2_attempts.jsonl"
    for path in (pr_.K1_LOG, pr_.K2_LOG):
        assert path.is_file(), path  # committed, empty until an attempt is transcribed
        r = subprocess.run(["git", "-C", str(pr_.ROOT), "check-ignore", "-q", "--", str(path)])
        assert r.returncode == 1, f"{path} is git-ignored"
    ignored = subprocess.run(["git", "-C", str(pr_.ROOT), "check-ignore", "-q", "--",
                              str(pr_.ROOT / "results" / "prices" / "k1_attempts.jsonl")])
    assert ignored.returncode == 0  # the old place: the check above can tell


@pytest.mark.skipif(not _git_checkout(), reason="not a git checkout")
def test_git_tracked_is_git_ls_files(tmp_path, monkeypatch):
    assert rp.git_tracked(pr_.ROOT / "run_prices.py")
    stray = tmp_path / "k1_attempts.jsonl"
    stray.write_text("")
    assert not rp.git_tracked(stray)  # outside the repository
    assert not rp.git_tracked(pr_.ROOT / "results" / "prices" / "k1_attempts.jsonl")  # ignored, never tracked
    monkeypatch.setattr(pr_, "K1_LOG", pr_.ROOT / "run_prices.py")  # any tracked file passes the real check
    rp.require_k1_log()
    monkeypatch.setattr(pr_, "K1_LOG", stray)
    with pytest.raises(rp.StopRun, match="not tracked by git"):
        rp.require_k1_log()


def _never(what):
    def fail(*a, **kw):
        raise AssertionError(f"{what} ran too early")
    return fail


@pytest.mark.parametrize("cmd", ["cmd_run", "cmd_check", "cmd_gate_lear"])
def test_a_missing_or_untracked_k1_log_stops_before_anything_runs(offline, monkeypatch, tmp_path, cmd):
    monkeypatch.setattr(rp, "load_model", _never("t0"))
    monkeypatch.setattr(rp, "load_prices", _never("the price fetch"))
    monkeypatch.setattr(rp, "_download", _never("the EPF-FR download"))
    args = rp.argparse.Namespace(cache_dir=str(tmp_path / "cache"), run_id="x", processes=1, limit_days=None)
    monkeypatch.setattr(pr_, "K1_LOG", tmp_path / "absent.jsonl")
    with pytest.raises(rp.StopRun, match="K1 attempt log .* is missing"):
        getattr(rp, cmd)(args)
    present = tmp_path / "present.jsonl"
    present.write_text("")
    monkeypatch.setattr(pr_, "K1_LOG", present)
    monkeypatch.setattr(rp, "git_tracked", lambda path: False)
    if _git_checkout():
        with pytest.raises(rp.StopRun, match="K1 attempt log .* is not tracked by git"):
            getattr(rp, cmd)(args)


@pytest.mark.skipif(not _git_checkout(), reason="not a git checkout")
def test_the_real_tracked_check_refuses_a_log_git_does_not_track(tmp_path, monkeypatch):
    """No stub of git_tracked here: a present but untracked log stops the run."""
    log = tmp_path / "k1_attempts.jsonl"
    log.write_text("")
    monkeypatch.setattr(pr_, "K1_LOG", log)
    monkeypatch.setattr(rp, "OUT", tmp_path / "out")
    monkeypatch.setattr(rp, "load_model", _never("t0"))
    monkeypatch.setattr(rp, "load_prices", _never("the price fetch"))
    args = rp.argparse.Namespace(cache_dir=str(tmp_path / "cache"), run_id="x", processes=1)
    with pytest.raises(rp.StopRun, match="not tracked by git"):
        rp.cmd_run(args)
    meta = json.loads((tmp_path / "out" / "run_meta.json").read_text())
    assert meta["k1"]["log_present"] and meta["k1"]["log_sha256"] == hashlib.sha256(b"").hexdigest()


# ---------------------------------------------------------------------------- t0 first


@pytest.mark.parametrize("cmd, written", [("cmd_run", "run_meta.json"), ("cmd_check", "check.json"),
                                          ("cmd_smoke", "smoke.json")])
def test_t0_is_loaded_before_any_data_is_fetched_and_a_load_failure_stops(offline, monkeypatch, cmd, written):
    from solarbench import t0_pinned

    def refused():
        raise t0_pinned.PinnedWeightsError("the Hub head does not hold the frozen bytes")

    monkeypatch.setattr(rp, "load_model", refused)
    monkeypatch.setattr(rp, "load_prices", _never("the price fetch"))
    monkeypatch.setattr(rp, "load_weather", _never("the weather fetch"))
    args = rp.argparse.Namespace(cache_dir="unused", run_id="x", processes=1)
    with pytest.raises(rp.StopRun, match=r"t0-alpha could not be loaded \(PinnedWeightsError\)"):
        getattr(rp, cmd)(args)
    meta = json.loads((offline / written).read_text())
    assert meta["t0_weights"]["error_type"] == "PinnedWeightsError" and not meta["t0_weights"]["loaded"]
    assert "prices" not in meta and "selection" not in meta  # nothing was fetched


def test_check_keeps_the_retrieval_record_and_prints_the_k2_record(offline, monkeypatch, capsys):
    monkeypatch.setattr(pr_, "in_run_leak_check", lambda *a, **kw: {"pass": True, "origins": {}})
    model = EchoT0()

    def loaded():
        rp.T0_PROVENANCE.update({"served_by_revision": "fdd1896", "verified": True})
        return model

    monkeypatch.setattr(rp, "load_model", loaded)
    args = rp.argparse.Namespace(cache_dir="unused", run_id="4242", processes=1)
    assert rp.cmd_check(args) == 0
    meta = json.loads((offline / "check.json").read_text())
    assert meta["t0_weights"] == {"served_by_revision": "fdd1896", "verified": True}
    # gates.K2.on_fail: the earlier logged attempts first, then this dispatch's
    assert meta["k2_attempts"][0] == EARLIER_K2
    assert meta["k2_attempts"][-1]["this_run"] and meta["k2_attempts"][-1]["run_id"] == "4242"
    lines = capsys.readouterr().out.splitlines()
    i = next(i for i, x in enumerate(lines) if x.startswith("K2 record (transcribe into "))
    assert json.loads(lines[i + 1]) == {"run_id": "4242", "commit": meta["commit"], "pass": True}


# ---------------------------------------------------------------------------- sources.agreement_rule


def test_smard_agreement_prints_2024_06_26(monkeypatch, tmp_path):
    idx = pd.date_range(zones.local_midnight_utc(date(2022, 1, 1)), zones.local_midnight_utc(date(2025, 12, 29)),
                        freq="1h", tz="UTC", inclusive="left")
    ec = pd.Series(np.round(np.arange(len(idx)) % 97 + 0.25, 2), index=idx)
    day = pd.date_range(zones.local_midnight_utc(date(2024, 6, 26)), periods=24, freq="1h", tz="UTC")
    smard = ec.copy()
    smard[day[13]] += 5.0
    monkeypatch.setattr(pd_, "fetch_smard", lambda *a, **kw: ([], "FR"))
    monkeypatch.setattr(pd_, "load_smard", lambda paths: smard)
    out = rp.smard_agreement(ec, tmp_path, "start")
    assert out["day_2024_06_26"] == {"energy_charts": ec[day].tolist(), "smard": smard[day].tolist()}
    assert len(out["day_2024_06_26"]["smard"]) == 24 and out["day_2024_06_26"]["smard"][13] == ec[day[13]] + 5.0


# ---------------------------------------------------------------------------- missing days by cause


def _arm_rows(method, days, *, y_hat=(), q=()):
    """One arm's rows on complete days: finite everywhere except y_hat NaN on ``y_hat`` days and the five
    quantiles NaN on ``q`` days."""
    frames = []
    for d in days:
        t = px.day_hours(d)
        n = len(t)
        frame = {"delivery_date": d, "method": method, "target_time": t, "y": np.full(n, 50.0),
                 "y_hat": np.full(n, np.nan if d in y_hat else 49.0)}
        for c in st.Q_COLUMNS:
            frame[c] = np.full(n, np.nan if d in y_hat or d in q else 48.0)
        frames.append(pd.DataFrame(frame))
    return frames


def test_missing_days_are_reported_by_cause():
    d1, d2, d3 = date(2024, 7, 1), date(2024, 7, 2), date(2024, 7, 3)
    days = [d1, d2, d3]
    df = pd.concat([*_arm_rows("t0", days, y_hat={d1}), *_arm_rows("naive_std", days, y_hat={d2}),
                    *_arm_rows("prev_week", days),
                    *_arm_rows("best_simple_eq", days, q={d2}, y_hat={d3}),
                    *_arm_rows("lear_ens", days, y_hat={d3}),
                    *_arm_rows("lear_ens_eq", days, y_hat={d1}, q={d2}),
                    *_arm_rows("t0_cal_wx", [d2, d3]),
                    *_arm_rows("t0_cal_strict", days, y_hat={d3}), *_arm_rows("best_simple_2023_strict", days)],
                   ignore_index=True)
    info = {"t0_missing": {"t0": {"context": [str(d1)], "sanitised": []}, "t0_cal_strict": {"context": [],
                                                                                           "sanitised": [str(d3)]}},
            "lear_logs": {"56": {"no_forecast": {"missing_features": [str(d3)], "fit_failed": []}}},
            "lear_eq_logs": {"1456": {"no_forecast": {"missing_features": [], "fit_failed": [str(d1)]}}},
            "p4_days": {"dropped": {"horizon": [str(d1)], "context": []}}}
    scored = set(df["method"])
    got = rp.missing_by_arm(df, info, scored, strict_arms=("t0_cal_strict", "best_simple_2023_strict"),
                            band_arms=("best_simple_eq", "lear_ens_eq"), p4_first_day=date(2024, 6, 6))
    assert set(got) == scored
    causes = {arm: v["by_cause"] for arm, v in got.items()}
    assert causes["t0"] == {"context": [str(d1)]}
    assert causes["naive_std"] == {rp.NON_FINITE: [str(d2)]}
    assert causes["prev_week"] == {} and got["prev_week"]["missing"] == 0 and got["prev_week"]["days"] == 3
    assert causes["best_simple_eq"] == {"fewer than 14 legal error cells": [str(d2)], rp.NON_FINITE: [str(d3)]}
    assert causes["lear_ens"] == {"LEAR window 56: missing_features": [str(d3)]}
    assert causes["lear_ens_eq"] == {"LEAR window 1456: fit_failed": [str(d1)],
                                     "fewer than 14 legal error cells": [str(d2)]}
    assert causes["t0_cal_wx"] == {"weather_p4.day_rule: horizon": [str(d1)]}
    assert causes["t0_cal_strict"] == {"sanitised": [str(d3)]}
    assert got["best_simple_eq"]["metric"] == "pinball" and got["t0"]["metric"] == "mae"


# ---------------------------------------------------------------------------- offline end to end


def synthetic_prices(seed=0) -> pd.Series:
    start, end = ps.PRICE_SPEC["periods"]["fetch_prices"]
    idx = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(date(2026, 1, 1)), freq="1h",
                        tz="UTC", inclusive="left")
    local = idx.tz_convert(zones.PARIS)
    rng = np.random.default_rng(seed)
    v = 60 + 25 * np.sin(2 * np.pi * (local.hour - 7) / 24) - 30 * (local.hour == 13) + rng.normal(0, 8, len(idx))
    s = pd.Series(v, index=idx, name="price")
    s[s.index.tz_convert(zones.PARIS).date == NAN_DAY] = np.nan  # one incomplete test day
    s[zones.local_midnight_utc(SANITISED_DAY) - pd.Timedelta(hours=1)] = SENTINEL
    return s


def synthetic_weather(grid: pd.DatetimeIndex):
    readings = pd.date_range("2024-02-06", "2025-12-30", freq="1h", tz="UTC")
    rng = np.random.default_rng(1)
    temp = pd.Series(12 + 8 * np.sin(np.arange(len(readings)) / 500) + rng.normal(0, 1, len(readings)),
                     index=readings)
    rad = pd.Series(np.clip(300 * np.sin(2 * np.pi * (readings.hour - 6) / 24), 0, None), index=readings)
    return px.weather_covariates(temp, rad.where(rad.index >= "2024-03-08"), grid)


EARLIER_K2 = {"run_id": "earlier", "commit": "0" * 40, "pass": False}


@pytest.fixture
def offline(tmp_path, monkeypatch):
    series = synthetic_prices()
    model = EchoT0()
    monkeypatch.setattr(rp, "OUT", tmp_path / "out")
    k1_log, k2_log = tmp_path / "k1_attempts.jsonl", tmp_path / "k2_attempts.jsonl"
    k1_log.write_text("")  # an empty log: no attempt, K1 not passed
    k2_log.write_text(json.dumps(EARLIER_K2) + "\n")  # one earlier (failed) K2 attempt
    monkeypatch.setattr(pr_, "K1_LOG", k1_log)
    monkeypatch.setattr(pr_, "K2_LOG", k2_log)
    monkeypatch.setattr(rp, "git_tracked", lambda path: True)  # the tmp logs stand in for committed files
    monkeypatch.setattr(rp, "load_prices", lambda work, meta, cross_check: series)
    monkeypatch.setattr(rp, "load_weather", lambda work, grid, meta: synthetic_weather(grid))
    monkeypatch.setattr(rp, "load_model", lambda: model)
    from solarbench import price_gates as pg

    monkeypatch.setattr(pg, "run_k3", lambda series, model, **kw: {"pass": True, "stub": True})
    monkeypatch.setattr(pg, "run_k2_at_origins", lambda *a, **kw: {"pass": True, "stub": True})
    return tmp_path / "out"


def test_offline_scored_run_end_to_end(offline):
    args = rp.argparse.Namespace(cache_dir="unused", run_id="offline", processes=1)
    assert rp.cmd_run(args) == 0
    meta = json.loads((offline / "run_meta.json").read_text())
    res = json.loads((offline / "results.json").read_text())
    assert meta["leak_check"]["pass"]
    assert meta["k2_attempts"][0] == EARLIER_K2 and meta["k2_attempts"][-1]["pass"]  # earlier logged ones first
    assert meta["k2_attempts"][-1]["this_run"] and meta["k2_attempts"][-1]["run_id"] == "offline"
    assert meta["lear_sha256_start"] == meta["lear_sha256_end"]
    assert not meta["k1"]["passed"] and "lear_ens" not in meta["scored_arms"]
    assert meta["k1"]["log_present"] and meta["k1"]["log_sha256"] == hashlib.sha256(b"").hexdigest()
    assert res["attribution"] == ps.ATTRIBUTION
    # statistics.day_sets: each scored arm's missing days by cause
    mba = meta["missing_by_arm"]
    assert set(mba) == set(meta["scored_arms"])
    for arm in ("t0", "t0_cal", "t0_cal_wx"):
        assert mba[arm]["by_cause"].get("sanitised") == [str(SANITISED_DAY)], (arm, mba[arm])
    assert str(SANITISED_DAY) not in sum(mba["t0_cal_strict"]["by_cause"].values(), [])
    assert "2024-08-21" in mba["prev_week"]["by_cause"][rp.NON_FINITE]  # reads the NaN day's same hours (D-7)
    assert "2024-08-15" in mba["naive_std"]["by_cause"][rp.NON_FINITE]  # a Thursday: reads D-1, the NaN day
    assert all(str(NAN_DAY) not in days for m in mba.values() for days in m["by_cause"].values())  # incomplete
    assert mba["best_simple_eq"]["metric"] == "pinball" and mba["t0"]["metric"] == "mae"
    assert mba["t0"]["days"] == mba["best_simple_2023"]["days"] > 700
    assert meta["forecast"]["p4_days"]["kept"] > 0
    states = {pid: v["state"] for pid, v in res["verdicts"].items()}
    assert list(states) == ["P1", "P2", "P3", "P4"]
    assert states["P2"] == "not runnable" and res["verdicts"]["P2"]["cause"]
    assert all(s in ("won", "lost", "not stable", "lost on coverage", "not runnable") for s in states.values())
    summary = (offline / "summary.md").read_text()
    assert summary.splitlines()[0] == st.status_line()  # reading_table.printing: it opens with the status line
    assert ps.PRICE_SPEC["status"].split(":")[0] in summary and "discovery-grade" in summary
    assert ps.ATTRIBUTION in summary
    assert rp.PROGRAM_ROLE not in summary and meta["program_role"] == rp.PROGRAM_ROLE
    role = (offline / "program_role.md").read_text()
    assert "discovery-grade" in role
    assert "cannot by itself satisfy the project's independent-confirmation milestone" in role
    for pid in ("P1", "P3", "P4"):
        assert (offline / f"per_day_{pid}.csv").exists()
    fc = pd.read_csv(offline / "forecasts.csv.gz", low_memory=False)
    assert {"t0", "t0_cal", "t0_cal_strict", "t0_cal_wx", "best_simple_2023", "best_simple_2023_strict",
            "best_simple_eq", "naive_std", "prev_week"} <= set(fc["method"])


def test_a_failed_leak_check_scores_nothing(offline, monkeypatch):
    monkeypatch.setattr(pr_, "in_run_leak_check", lambda *a, **kw: {"pass": False, "origins": {}})
    args = rp.argparse.Namespace(cache_dir="unused", run_id="offline", processes=1)
    assert rp.cmd_run(args) == 3
    meta = json.loads((offline / "run_meta.json").read_text())
    assert "leak check failed" in meta["stopped"]
    assert not (offline / "results.json").exists() and not (offline / "forecasts.csv.gz").exists()
