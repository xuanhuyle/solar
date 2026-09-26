"""The referee: the leak harness catches planted leaks and passes every catalogue method;
the statistics match hand-computed values."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_engine_discovery as td
import test_probes as tp
from engine import arms as am
from engine import covs
from engine.referee import leakcheck, stats
from engine.spec import validate_probe
from solarbench import covariates as cov
from solarbench.backtest import build_windows
from solarbench.forecasters import Prediction

LEADS = {"temperature": covs.TEMPERATURE_LEAD_DAYS, "radiation": covs.RADIATION_LEAD_DAYS}


def _windows(bundle, start="2024-06-03", end="2024-06-20"):
    return build_windows(bundle.target, test_start=pd.Timestamp(start).date(), test_end=pd.Timestamp(end).date(),
                         gate_hour=12, context_steps=am.CONTEXT_STEPS if hasattr(am, "CONTEXT_STEPS") else 90 * 48)


SPEC = validate_probe(td.spec(arms=[{"name": "t0_cal", "covariates": [{"id": "holiday"}, {"id": "bridge_day"}]},
                                    {"name": "t0_temp", "covariates": [{"id": "wx_temperature", "transform": "hdd15"}]}],
                              comparisons=[{"arm": "t0_cal", "vs": "best_simple"}, {"arm": "t0_temp", "vs": "accepted"},
                                           {"arm": "t0_cal", "vs": "t0_base"}]))


@pytest.mark.parametrize("name", ["t0_cal", "t0_temp", "best_simple", "t0_base", "accepted"])
def test_every_catalogue_method_passes_the_leak_check(name):
    bundle = td.consumption_bundle()
    model = tp.QuantModel()
    accepted = am.latest_accepted([], "consumption")
    make = lambda b: am.build_method(name, SPEC, b, model, accepted)
    out = leakcheck.check_method(make, bundle, _windows(bundle), leads=LEADS)
    assert out["pass"], out


# ---------------------------------------------------------------- mutants


@dataclass
class TargetAsCovariate:
    """A leak: the realised target handed to t0 as a known-future covariate."""

    series: pd.Series
    name: str = "target_copy"
    oracle: bool = False

    def spec(self):
        return {"class": "TargetAsCovariate"}

    def values(self, times):
        return self.series.reindex(times).to_numpy(dtype="float64")

    def issued_at(self, times):
        return pd.DatetimeIndex([pd.NaT] * len(times), tz="UTC")


class PeekPastGate:
    """A leak: a 'baseline' that reads the target 6 hours after the gate."""

    name = "peek"

    def spec(self):
        return {"class": "PeekPastGate"}

    def predict(self, series, windows):
        out = []
        for w in windows:
            v = float(series.reindex([w.origin + pd.Timedelta(hours=6)]).iloc[0])
            out.append(Prediction(values=np.full(len(w.targets), v), max_source_time=w.origin,
                                  source_latest=pd.DatetimeIndex([w.origin] * len(w.targets)),
                                  source_earliest=pd.DatetimeIndex([w.origin] * len(w.targets)),
                                  n_sources=np.ones(len(w.targets), dtype=int)))
        return out


def _mutant(kind, model):
    def make(b):
        if kind == "target_as_covariate":
            t0 = am._t0("m", (TargetAsCovariate(b.target),), model)
            return am.Method("m", [t0], "m")
        if kind == "peek_past_gate":
            return am.Method("m", [PeekPastGate()], "peek")
        if kind == "lead_zero_weather":  # a weather value treated as known at its valid time
            base = cov.weather_covariate(b.weather["temperature"], b.target.index, lead_days=0, stamp_offset_min=0,
                                         name="wx0")
            return am.Method("m", [am._t0("m", (base,), model)], "m", (base,))
        if kind == "future_weather_label":  # correct issue bound, but the arm reads it as lead 3 while it is lead 0
            vals = cov.weather_covariate(b.weather["temperature"], b.target.index, lead_days=3, stamp_offset_min=0,
                                         name="wx")
            vals.series = b.target.rolling(3, min_periods=1).mean()  # quietly swap in realised data
            return am.Method("m", [am._t0("m", (vals,), model)], "m", (vals,))
        raise KeyError(kind)
    return make


@pytest.mark.parametrize("kind", ["target_as_covariate", "peek_past_gate", "lead_zero_weather", "future_weather_label"])
def test_planted_leaks_are_caught(kind):
    bundle = td.consumption_bundle()
    out = leakcheck.check_method(_mutant(kind, tp.QuantModel()), bundle, _windows(bundle), leads=LEADS)
    assert not out["pass"], out


# ---------------------------------------------------------------- statistics


def test_t_distribution_matches_tables():
    assert stats.t_sf(2.015048, 5) == pytest.approx(0.05, abs=1e-5)
    assert stats.t_sf(3.364930, 5) == pytest.approx(0.01, abs=1e-5)
    assert stats.t_sf(2.228139, 10) == pytest.approx(0.025, abs=1e-5)
    assert stats.t_sf(-1.0, 7) == pytest.approx(1 - stats.t_sf(1.0, 7))
    assert stats.t_crit(5, 0.0125) == pytest.approx(3.1634, abs=1e-3)


def _per_day(arm_mae, ref_mae):
    days = pd.date_range("2024-01-01", periods=len(arm_mae), freq="D").date
    rows = [{"delivery_date": d, "method": "arm", "sum_abs_err": a * 48, "n": 48} for d, a in zip(days, arm_mae)]
    rows += [{"delivery_date": d, "method": "ref", "sum_abs_err": r * 48, "n": 48} for d, r in zip(days, ref_mae)]
    return pd.DataFrame(rows)


def test_block_t_test_by_hand():
    rng = np.random.default_rng(0)
    ref = 1000 + rng.normal(0, 50, 84)
    arm = ref * 0.6 + rng.normal(0, 30, 84)  # ~40% better
    pd_ = _per_day(arm, ref)
    b = stats.blocks(pd_, "arm", "ref", 0.25)
    z = 0.75 * ref - arm
    assert len(b) == 6 and np.allclose(b, z.reshape(6, 14).mean(axis=1))
    res = stats.block_t_test(pd_, "arm", "ref", 0.25)
    t = b.mean() / (b.std(ddof=1) / np.sqrt(6))
    assert res["t"] == pytest.approx(t, rel=1e-6) and res["p"] < 0.0125
    assert stats.block_t_test(pd_, "arm", "ref", 0.45)["p"] > 0.5  # skill ~0.40 does not beat 0.45
    assert stats.block_t_test(_per_day(arm[:70], ref[:70]), "arm", "ref", 0.0)["p"] == 1.0  # 5 blocks


def test_holm_and_alpha_budget():
    assert stats.holm([0.01, 0.04, 0.03, 0.2]) == pytest.approx([0.04, 0.09, 0.09, 0.2])
    assert stats.alpha_for_batch(0) == stats.alpha_for_batch(3) == 0.0125
    with pytest.raises(ValueError, match="spent"):
        stats.alpha_for_batch(4)


def test_power_table_is_monotone_in_blocks():
    rng = np.random.default_rng(1)
    ref = 1000 + rng.normal(0, 80, 140)
    table = stats.power_table(_per_day(ref * 0.9, ref), "arm", "ref", 0.0125)["min_detectable_skill"]
    assert table["6"] > table["8"] > table["12"] > 0


# ------------------------------------------------------ gate, budget, wiring


class CovModel:
    """t0 stand-in that forecasts its first covariate when it has one (else the last context value)."""

    def predict(self, context, horizon, quantiles, future_covariates=None):
        import torch
        from types import SimpleNamespace

        ctx = np.nan_to_num(np.asarray(torch.as_tensor(context), dtype="float64"))
        med = np.repeat(ctx[..., -1:], horizon, axis=-1)
        if future_covariates is not None:
            fut = np.nan_to_num(np.asarray(torch.as_tensor(future_covariates), dtype="float64"))
            med = fut[:, 0, ctx.shape[-1]:ctx.shape[-1] + horizon][:, None, :] if med.ndim == 3 else \
                fut[:, 0, ctx.shape[-1]:ctx.shape[-1] + horizon]
        q = med[..., None] + (np.asarray(quantiles) - 0.5)[None, :] * 100.0
        return SimpleNamespace(median=torch.as_tensor(med), quantiles=torch.as_tensor(q))


def test_known_answer_gate_runs_and_reports(monkeypatch):
    from engine.referee import known_answer

    bundle = td.consumption_bundle()
    monkeypatch.setattr(known_answer, "KA_PERIOD", ("2024-09-02", "2024-09-20"))
    out = known_answer.run_gate("consumption", "wx_temperature", cache_dir=Path("."), model=CovModel(),
                                bundle=bundle)
    assert out["gate"] == "known_answer" and out["days"] > 10
    assert set(out["checks"]) == {"planted_helps", "decoy_does_not_help", "decoy_does_not_break", "aligned",
                                  "no_sanitised_output"}
    # This stub forecasts the covariate itself: the planted copy helps, a 1 h shift hurts, noise breaks it.
    assert out["checks"]["planted_helps"] and out["checks"]["aligned"] and not out["checks"]["decoy_does_not_break"]
    assert not out["pass"]
    with pytest.raises(ValueError):
        known_answer.run_gate("solar", "wx_temperature", cache_dir=Path("."), model=tp.QuantModel(), bundle=bundle)


def test_only_full_passing_gates_unlock_a_covariate():
    from engine.referee import known_answer

    def gate(ok, limit=None):
        return {"kind": "gate", "payload": {"gate": "known_answer", "target": "consumption",
                                            "covariate": "wx_temperature", "pass": ok, "limit_days": limit}}
    assert known_answer.passed_gates([gate(True, limit=5)]) == set()
    assert known_answer.passed_gates([gate(True)]) == {("consumption", "wx_temperature")}
    assert known_answer.passed_gates([gate(True), gate(False)]) == set()  # the latest full gate decides


def _entries_with(*payloads):
    from engine import ledger, legacy

    ctx = {"at": "2026-09-26T00:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "x",
           "config_sha256": "c" * 64, "actor": "t", "mode": "t"}
    items = legacy.seed_items(ctx) + [ledger.pending(k, p, ctx) for k, p in payloads]
    return ledger.chain([], items)


def test_probe_wiring_gates_budget_and_duplicates(monkeypatch):
    import engine.__main__ as cli
    from engine import discover
    from engine.referee import budget

    calls = []
    monkeypatch.setattr(discover, "run_probe", lambda norm, **k: calls.append(norm) or
                        {"probe_sha256": "x", "comparisons": [{"arm": "a", "vs": "b"}]})
    ctx = {"at": "t", "run_id": "1", "run_attempt": "1", "code_commit": "x", "config_sha256": "c" * 64,
           "actor": "t", "mode": "probe"}
    temp = td.spec(arms=[{"name": "t0_temp", "covariates": [{"id": "wx_temperature"}]}],
                   comparisons=[{"arm": "t0_temp", "vs": "t0_base"}])
    monkeypatch.setattr(cli, "current_ledger", lambda: _entries_with())
    items, out = cli._probe_entries(temp, "researcher", ctx)
    assert items[0]["kind"] == "probe_rejected" and "known-answer gate" in out["reasons"][0] and not calls
    gate_ok = ("gate", {"gate": "known_answer", "target": "consumption", "covariate": "wx_temperature", "pass": True})
    monkeypatch.setattr(cli, "current_ledger", lambda: _entries_with(gate_ok))
    items, out = cli._probe_entries(temp, "researcher", ctx)
    assert [i["kind"] for i in items] == ["probe_submitted", "probe_result"] and len(calls) == 1
    # an identical spec costs nothing and is not rerun
    from engine.spec import spec_sha256, validate_probe

    sha = spec_sha256(validate_probe(temp))
    done = ("probe_result", {"submitted_by": "researcher", "probe_sha256": sha, "comparisons": [{"a": 1}]})
    monkeypatch.setattr(cli, "current_ledger", lambda: _entries_with(gate_ok, done))
    items, out = cli._probe_entries(temp, "researcher", ctx)
    assert items[0]["kind"] == "note" and out["probe_sha256"] == sha and len(calls) == 1
    # a spent budget refuses new probes (owner runs are not charged)
    spent = [("probe_result", {"submitted_by": "researcher", "probe_sha256": f"p{i}",
                               "comparisons": [{}] * 50}) for i in range(4)]
    monkeypatch.setattr(cli, "current_ledger", lambda: _entries_with(gate_ok, *spent))
    assert budget.remaining(cli.current_ledger()) == 0
    items, out = cli._probe_entries(td.spec(), "researcher", ctx)
    assert items[0]["kind"] == "probe_rejected" and "budget" in out["reasons"][0]
    items, out = cli._probe_entries(td.spec(), "owner:manual", ctx)
    assert items[-1]["kind"] == "probe_result"


def test_discovery_results_carry_live_leak_checks():
    from engine import discover

    out = discover.run_probe(td.spec(), cache_dir=Path("."), bundle=td.consumption_bundle(False),
                             model=tp.QuantModel(), accepted=am.latest_accepted([], "consumption"), limit_days=6)
    assert out["leak_checks_passed"] and out["status"].startswith("EXPLORATORY")
    for name in ("t0_cal", "best_simple"):
        assert out["methods"][name]["leak_check"]["pass"]


def test_instant_readings_map_to_slot_centres_exactly():
    hours = pd.date_range("2024-06-01", periods=6, freq="h", tz="UTC")
    ramp = pd.Series(np.arange(6, dtype=float) * 10.0, index=hours)  # 0, 10, 20, ... at each hour
    slots = pd.date_range("2024-06-01 00:00", "2024-06-01 04:30", freq="30min", tz="UTC")
    values, latest = covs.instant_to_slots(ramp, slots, 0)
    assert np.allclose(values, np.arange(len(slots)) * 5.0)  # linear in time, exactly
    assert latest[1] == hours[1] and latest[2] == hours[1] and latest[3] == hours[2]  # 00:30 -> 01:00; 01:00 alone; 01:30 -> 02:00
    gapped = ramp.copy(); gapped.iloc[2] = np.nan
    v, _ = covs.instant_to_slots(gapped, slots, 0)
    assert np.isnan(v[3]) and np.isnan(v[4]) and not np.isnan(v[2])  # 01:30 and 02:00 need the 02:00 reading


def test_radiation_gate_aligns_with_its_own_convention(monkeypatch):
    from engine.referee import known_answer

    monkeypatch.setattr(known_answer, "KA_PERIOD", ("2024-09-02", "2024-09-20"))
    b = td.consumption_bundle()
    hours = pd.date_range("2024-02-06", "2024-12-31 23:00", freq="h", tz="UTC")
    solar = b.replaced(target_id="solar", weather={"radiation": pd.Series(np.ones(len(hours)), index=hours)})
    out = known_answer.run_gate("solar", "wx_radiation", cache_dir=Path("."), model=CovModel(), bundle=solar)
    assert out["convention"] == "mean_preceding_hour" and out["checks"]["aligned"] and out["checks"]["planted_helps"]


def test_recorded_outcomes_do_not_fail_the_job(monkeypatch, tmp_path):
    """A failed gate or a rejected probe is a result in the ledger, not a red CI job; a crash is."""
    import types

    import engine.__main__ as cli
    from engine.referee import known_answer

    monkeypatch.setattr(cli, "PENDING", tmp_path / "pending.jsonl")
    monkeypatch.setattr(cli, "current_ledger", lambda: _entries_with())
    monkeypatch.setattr(am, "_t0", lambda *a, **k: types.SimpleNamespace(load=lambda: object()))
    monkeypatch.setattr(known_answer, "run_gate", lambda t, c, **k: {"gate": "known_answer", "target": t,
                                                                      "covariate": c, "pass": False})
    out = cli.gate(types.SimpleNamespace(limit_days=None))
    assert out["ok"] and not out["all_passed"]

    def boom(t, c, **k):
        raise RuntimeError("download failed")
    monkeypatch.setattr(known_answer, "run_gate", boom)
    assert not cli.gate(types.SimpleNamespace(limit_days=None))["ok"]
    monkeypatch.setenv("ENGINE_SPEC_JSON", '{"spec_version": "probe/0"}')
    out = cli.probe(types.SimpleNamespace(spec_file=None, submitted_by="owner:manual", limit_days=None))
    assert out["ok"] and "reasons" in out["result"]
