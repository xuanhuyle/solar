"""Experiment 4's runner: the licence rule, the K1 log and an offline end-to-end scored run (synthetic prices,
a stand-in for t0, the gates stubbed). Nothing here fetches data or loads t0."""

from __future__ import annotations

import json
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


class EchoT0:
    """Stands in for t0 (as tests/test_price_exp.py): a weighted sum of the context plus the horizon covariates."""

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch

        ctx = torch.nan_to_num(torch.as_tensor(context, dtype=torch.float64))
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
                                    "over_budget": False}
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


# ---------------------------------------------------------------------------- offline end to end


def synthetic_prices(seed=0) -> pd.Series:
    start, end = ps.PRICE_SPEC["periods"]["fetch_prices"]
    idx = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(date(2026, 1, 1)), freq="1h",
                        tz="UTC", inclusive="left")
    local = idx.tz_convert(zones.PARIS)
    rng = np.random.default_rng(seed)
    v = 60 + 25 * np.sin(2 * np.pi * (local.hour - 7) / 24) - 30 * (local.hour == 13) + rng.normal(0, 8, len(idx))
    s = pd.Series(v, index=idx, name="price")
    s[s.index.tz_convert(zones.PARIS).date == date(2024, 8, 14)] = np.nan  # one incomplete test day
    return s


def synthetic_weather(grid: pd.DatetimeIndex):
    readings = pd.date_range("2024-02-06", "2025-12-30", freq="1h", tz="UTC")
    rng = np.random.default_rng(1)
    temp = pd.Series(12 + 8 * np.sin(np.arange(len(readings)) / 500) + rng.normal(0, 1, len(readings)),
                     index=readings)
    rad = pd.Series(np.clip(300 * np.sin(2 * np.pi * (readings.hour - 6) / 24), 0, None), index=readings)
    return px.weather_covariates(temp, rad.where(rad.index >= "2024-03-08"), grid)


@pytest.fixture
def offline(tmp_path, monkeypatch):
    series = synthetic_prices()
    model = EchoT0()
    monkeypatch.setattr(rp, "OUT", tmp_path / "out")
    monkeypatch.setattr(pr_, "K1_LOG", tmp_path / "k1_attempts.jsonl")  # no attempt logged: K1 not passed
    monkeypatch.setattr(rp, "load_prices", lambda work, meta, cross_check: series)
    monkeypatch.setattr(rp, "load_weather", lambda work, grid, meta: synthetic_weather(grid))
    monkeypatch.setattr(rp, "load_model", lambda: model)
    from solarbench import price_gates as pg

    monkeypatch.setattr(pg, "run_k3", lambda series, model, **kw: {"pass": True, "stub": True})
    monkeypatch.setattr(pg, "run_k2_at_origins", lambda *a, **kw: {"pass": True, "stub": True}, raising=False)
    return tmp_path / "out"


def test_offline_scored_run_end_to_end(offline):
    args = rp.argparse.Namespace(cache_dir="unused", run_id="offline", processes=1)
    assert rp.cmd_run(args) == 0
    meta = json.loads((offline / "run_meta.json").read_text())
    res = json.loads((offline / "results.json").read_text())
    assert meta["leak_check"]["pass"] and meta["k2_attempts"][0]["pass"]
    assert meta["lear_sha256_start"] == meta["lear_sha256_end"]
    assert not meta["k1"]["passed"] and "lear_ens" not in meta["scored_arms"]
    assert meta["forecast"]["p4_days"]["kept"] > 0
    states = {pid: v["state"] for pid, v in res["verdicts"].items()}
    assert list(states) == ["P1", "P2", "P3", "P4"]
    assert states["P2"] == "not runnable" and res["verdicts"]["P2"]["cause"]
    assert all(s in ("won", "lost", "not stable", "lost on coverage", "not runnable") for s in states.values())
    summary = (offline / "summary.md").read_text()
    assert ps.PRICE_SPEC["status"].split(":")[0] in summary and "discovery-grade" in summary
    assert "cannot by itself satisfy the project's independent-confirmation milestone" in summary
    assert ps.ATTRIBUTION in summary
    for pid in ("P1", "P3", "P4"):
        assert (offline / f"per_day_{pid}.csv").exists()
    fc = pd.read_csv(offline / "forecasts.csv.gz")
    assert {"t0", "t0_cal", "t0_cal_strict", "t0_cal_wx", "best_simple_2023", "best_simple_2023_strict",
            "best_simple_eq", "naive_std", "prev_week"} <= set(fc["method"])


def test_a_failed_leak_check_scores_nothing(offline, monkeypatch):
    monkeypatch.setattr(pr_, "in_run_leak_check", lambda *a, **kw: {"pass": False, "origins": {}})
    args = rp.argparse.Namespace(cache_dir="unused", run_id="offline", processes=1)
    assert rp.cmd_run(args) == 3
    meta = json.loads((offline / "run_meta.json").read_text())
    assert "leak check failed" in meta["stopped"]
    assert not (offline / "results.json").exists() and not (offline / "forecasts.csv.gz").exists()
