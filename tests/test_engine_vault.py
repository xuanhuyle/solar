"""The forward vault: freeze rules, a single guarded opening, the data door, verdicts."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_engine_discovery as td
import test_probes as tp
from engine import arms as am
from engine import data, ledger, legacy, vault, vault_run, zones
from engine.canon import sha256_of
from solarbench import odre

CTX = {"at": "2026-09-26T08:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "x",
       "config_sha256": "c" * 64, "actor": "t", "mode": "t"}
T0 = datetime(2026, 10, 1, 10, tzinfo=timezone.utc)
ARM = [{"id": "bridge_day", "transform": "raw"}, {"id": "holiday", "transform": "raw"}]
NO_GATES: set = set()


C1_ARM = am.latest_accepted([], "consumption")["arm"]  # what 'accepted' means on the seeded ledger


def _result(covariates=ARM, vs="accepted", **over):
    p = {"probe_sha256": "p", "status": "EXPLORATORY - x", "target": "consumption", "scope": "all",
         "leak_checks_passed": True, "limit_days": None, "accepted_arm": C1_ARM,
         "spec": {"arms": [{"name": "t0_x", "covariates": covariates}]},
         "comparisons": [{"arm": "t0_x", "vs": vs, "skill": 0.01}]}
    p.update(over)
    return ("probe_result", p)


def _entries(*extra, evidence=None):
    items = legacy.seed_items(CTX) + [ledger.pending(k, p, CTX) for k, p in ((evidence or _result()), *extra)]
    return ledger.chain([], items)


def _evidence_seq(entries):
    return next(e["seq"] for e in entries if e["kind"] == "probe_result" and e["payload"].get("spec"))


def _batch(entries=None, **over):
    claim = {"id": "a", "statement": "t0 + holiday + bridge days beat the accepted arm", "target": "consumption",
             "arm": {"covariates": list(reversed(ARM))}, "comparator": "accepted", "scope": "all", "delta": 0.0,
             "evidence": [_evidence_seq(entries if entries is not None else _entries())]}
    claim.update(over)
    return {"batch_version": "claims/0", "claims": [claim]}


def _frozen(entries=None, gates=NO_GATES, **over):
    entries = entries if entries is not None else _entries()
    return vault.freeze(_batch(entries, **over), entries, T0, gates=gates, submitted_by="researcher")


def test_freeze_sets_window_alpha_receipt_and_hash():
    f = _frozen()
    first, last = date(2026, 10, 16), date(2026, 10, 16) + timedelta(days=167)
    assert (last - first).days + 1 == vault.WINDOW_DAYS == 168 and last == date(2027, 4, 1)
    assert f["batch_id"] == "B1" and f["window"] == [str(first), str(last)] and f["alpha"] == 0.0125
    assert f["receipt"] == {"batch_id": "B1", "batch_sha256": f["batch_sha256"], "window": f["window"],
                            "opens_after": "2027-04-04"}
    body = {k: v for k, v in f.items() if k not in ("batch_sha256", "receipt")}
    assert sha256_of(body) == f["batch_sha256"] and f["claims"][0]["id"] == "C1"
    assert f["submitted_by"] == "researcher" and f["target"] == "consumption"
    assert f["claims"][0]["arm"]["covariates"] == ARM  # normalised order
    assert f["accepted_at_freeze"]["consumption"]["arm"]["covariates"] == [{"id": "holiday", "transform": "raw"}]
    assert f["test"]["min_blocks"] == 10 and "12 calendar spans" in f["test"]["blocks"]


@pytest.mark.parametrize("over, reason", [
    ({"comparator": "rte_j1"}, "never decides"),
    ({"delta": 0.3}, "delta"),
    ({"delta": True}, "delta"),
    ({"delta": 10 ** 400}, "delta"),  # compared exactly: no OverflowError
    ({"evidence": [3]}, "no cited probe_result"),
    ({"evidence": []}, "at least one"),
    ({"arm": {"covariates": [{"id": "wx_radiation"}]}}, "not in the catalogue"),
    ({"arm": {"covariates": [{"id": "holiday"}, {"id": "holiday", "transform": "raw"}]}}, "duplicate"),
    ({"arm": {"covariates": [{"id": "holiday"}], "extra": 1}}, "arm is exactly"),
    ({"extra": 1}, "fields must be exactly"),
    ({"scope": "summer"}, "could never pass"),  # 2026-10-16..2027-04-01 holds no summer day
    ({"scope": ["all"]}, "unknown scope"),  # unhashable values: refused, never a TypeError
    ({"target": {"x": 1}}, "unknown target"),
    ({"comparator": ["accepted"]}, "comparator must be"),
    ({"arm": {"covariates": [{"id": ["holiday"]}]}}, "strings"),
])
def test_invalid_claims_are_refused(over, reason):
    with pytest.raises(vault.VaultError, match=reason):
        _frozen(**over)


def test_malformed_batches_are_refused_not_crashed():
    entries = _entries()
    for bad in (None, [], "x", {"batch_version": "claims/0"}, {"batch_version": "claims/0", "claims": "x"},
                {"batch_version": "claims/0", "claims": [None]}, {"batch_version": "claims/0", "claims": [{}] * 5}):
        with pytest.raises(vault.VaultError):
            vault.freeze(bad, entries, T0, gates=NO_GATES)


def test_a_winter_scope_fits_the_window():
    entries = _entries(evidence=_result(scope="winter"))
    assert _frozen(entries, scope="winter")["claims"][0]["scope"] == "winter"


def test_one_target_per_batch():
    entries = _entries()
    b = _batch(entries)
    b["claims"].append(dict(b["claims"][0], target="solar", arm={"covariates": [{"id": "holiday"}]}))
    with pytest.raises(vault.VaultError, match="one target per batch"):
        vault.freeze(b, entries, T0, gates=NO_GATES)


@pytest.mark.parametrize("evidence, reason", [
    (_result(limit_days=12), "smoke run"),
    (_result(leak_checks_passed=False), "leaky"),
    (_result(status="INVALID - x"), "invalid"),
    (_result(covariates=[{"id": "holiday"}]), "another arm"),
    (_result(vs="best_simple"), "another comparator"),
    (_result(scope="winter"), "another scope"),
    (_result(target="solar"), "another target"),
    (_result(comparisons=[{"arm": "t0_x", "vs": "accepted"}]), "no skill"),
])
def test_a_claim_needs_evidence_that_tested_exactly_it(evidence, reason):
    entries = _entries(evidence=evidence)
    with pytest.raises(vault.VaultError, match="no cited probe_result"):
        _frozen(entries)


def test_weather_claims_need_a_passed_gate_and_accepted_needs_a_finding():
    temp = [{"id": "wx_temperature", "transform": "hdd15"}]
    entries = _entries(evidence=_result(covariates=temp, vs="best_simple"))
    kw = {"arm": {"covariates": temp}, "comparator": "best_simple"}
    with pytest.raises(vault.VaultError, match="no passed known-answer gate"):
        _frozen(entries, **kw)
    assert _frozen(entries, gates={("consumption", "wx_temperature")}, **kw)["claims"][0]["arm"]["covariates"] == temp
    # 'accepted' on a target with no accepted finding
    solar = _entries(evidence=_result(covariates=[{"id": "holiday"}], target="solar"))
    with pytest.raises(vault.VaultError, match="no accepted finding for solar"):
        _frozen(solar, target="solar", arm={"covariates": [{"id": "holiday"}]})
    # ... and an accepted arm that uses an ungated weather covariate cannot be the comparator
    finding = ("accepted_finding", {"finding_id": "B9-C1", "target": "consumption", "scope": "all", "comparator": "accepted",
                                    "beat": "C1", "arm": {"covariates": temp}, "statement": "x"})
    acc = _entries(finding)
    with pytest.raises(vault.VaultError, match="accepted arm uses wx_temperature"):
        _frozen(acc)


def test_one_open_batch_four_at_most_and_an_unsealed_batch_is_closed():
    first = _frozen()
    with pytest.raises(vault.VaultError, match="still open"):
        _frozen(_entries(("freeze", first)))
    # opened but never decided (a crash): the window is consumed, the engine is not locked
    unsealed = _entries(("freeze", first), ("unseal", {"batch_id": "B1"}))
    assert vault.open_batches(unsealed) == [] and _frozen(unsealed)["batch_id"] == "B2"
    closed = [("freeze", dict(first, batch_id=f"B{i}")) for i in range(1, 5)]
    closed += [("verdict", {"batch_id": f"B{i}", "claims": []}) for i in range(1, 5)]
    with pytest.raises(ValueError, match="spent"):
        _frozen(_entries(*closed))
    # a rehearsal is never an open batch and spends nothing
    dry = vault.freeze(_batch(), _entries(), datetime(2025, 1, 1, tzinfo=timezone.utc), gates=NO_GATES, rehearsal=True)
    assert vault.open_batches(_entries(("freeze", dry))) == []


def test_rehearsal_stays_in_the_discovery_zone():
    dry = vault.freeze(_batch(), _entries(), datetime(2025, 1, 1, tzinfo=timezone.utc), gates=NO_GATES, rehearsal=True)
    assert dry["batch_id"] == "DRY" and dry["rehearsal"] and dry["window"] == ["2025-01-16", "2025-07-02"]
    with pytest.raises(vault.VaultError, match="discovery zone"):
        vault.freeze(_batch(), _entries(), datetime(2025, 8, 1, tzinfo=timezone.utc), gates=NO_GATES, rehearsal=True)
    with pytest.raises(vault.VaultError, match="not confirmable"):
        vault.freeze(_batch(), _entries(), datetime(2025, 3, 1, tzinfo=timezone.utc), gates=NO_GATES)  # a real freeze in 2025
    with pytest.raises(vault.VaultError, match="rehearsal"):
        vault.open_forward(_entries(("freeze", dry)), "DRY", now=datetime(2030, 1, 1, tzinfo=timezone.utc),
                           model_loaded=True, approved_by="xuanhuyle")


def test_the_vault_opens_once_matured_approved_and_loaded(tmp_path, monkeypatch):
    f = _frozen()
    entries = _entries(("freeze", f))
    later = datetime(2027, 4, 4, tzinfo=timezone.utc)
    with pytest.raises(vault.VaultError, match="matures"):
        vault.open_forward(entries, "B1", now=datetime(2027, 4, 3, tzinfo=timezone.utc), model_loaded=True,
                           approved_by="xuanhuyle")
    with pytest.raises(vault.VaultError, match="approval"):
        vault.open_forward(entries, "B1", now=later, model_loaded=True, approved_by=None)
    with pytest.raises(vault.VaultError, match="model"):
        vault.open_forward(entries, "B1", now=later, model_loaded=False, approved_by="xuanhuyle")
    with pytest.raises(vault.VaultError, match="already opened"):
        vault.open_forward(_entries(("freeze", f), ("unseal", {"batch_id": "B1"})), "B1", now=later,
                           model_loaded=True, approved_by="xuanhuyle")
    for tampered in (dict(f, alpha=0.05), dict(f, submitted_by="owner"), dict(f, window=["2026-10-16", "2027-06-01"])):
        with pytest.raises(vault.VaultError, match="freeze hash"):
            vault.open_forward(_entries(("freeze", tampered)), "B1", now=later, model_loaded=True, approved_by="xuanhuyle")
    access, batch = vault.open_forward(entries, "B1", now=later, model_loaded=True, approved_by="xuanhuyle")
    assert vault.access_is_valid(access) and access.first_day == "2026-07-08" and access.last_day == "2027-04-01"
    # the data door: the issued access covers its window only; a look-alike never works
    seen = []
    monkeypatch.setattr(odre, "_download_columns", lambda *a, **k: seen.append(a) or pytest.skip("reached download"))
    forged = data.ForwardAccess(access.batch_id, access.batch_sha256, access.first_day, access.last_day)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2026-12-31", tmp_path, access=forged)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2027-05-01", tmp_path, access=access)
    vault.close(access)
    assert not vault.access_is_valid(access)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2026-12-31", tmp_path, access=access)
    assert not seen


def _cli_args(tmp_path, batch_text):
    path = tmp_path / "batch.json"
    path.write_text(batch_text, encoding="utf-8")
    return SimpleNamespace(batch_file=str(path), submitted_by="researcher", batch_id="B1", limit_days=None)


def test_a_cli_freeze_can_be_opened_after_recording(tmp_path, monkeypatch):
    """Review #0: the frozen payload that reaches the ledger must match its own hash."""
    import engine.__main__ as cli

    entries = _entries()
    monkeypatch.setattr(cli, "current_ledger", lambda: entries)
    monkeypatch.setattr(cli, "PENDING", tmp_path / "pending.jsonl")
    out = cli.freeze(_cli_args(tmp_path, json.dumps(_batch(entries))))
    assert out["ok"] and "receipt" in out
    recorded = entries + ledger.chain(entries, ledger.read_pending(tmp_path / "pending.jsonl"))
    frozen = recorded[-1]["payload"]
    assert recorded[-1]["kind"] == "freeze" and frozen["submitted_by"] == "researcher"
    last = date.fromisoformat(frozen["window"][1])
    access, batch = vault.open_forward(recorded, "B1", now=datetime.combine(last + timedelta(days=3), datetime.min.time(),
                                                                          tzinfo=timezone.utc),
                                       model_loaded=True, approved_by="xuanhuyle")
    assert batch["batch_sha256"] == frozen["batch_sha256"]
    vault.close(access)


@pytest.mark.parametrize("text", ["{not json", json.dumps({"batch_version": "claims/0", "claims": [{"id": 1}]}), "[]",
                                  json.dumps({"batch_version": "claims/0", "claims": [dict(
                                      id="a", statement="s", target="consumption", arm={"covariates": []},
                                      comparator="accepted", scope=["all"], delta=0.0, evidence=[1])]})])
def test_a_malformed_cli_freeze_is_recorded_as_a_rejection(tmp_path, monkeypatch, text):
    import engine.__main__ as cli

    monkeypatch.setattr(cli, "current_ledger", lambda: _entries())
    monkeypatch.setattr(cli, "PENDING", tmp_path / "pending.jsonl")
    out = cli.freeze(_cli_args(tmp_path, text))
    items = ledger.read_pending(tmp_path / "pending.jsonl")
    assert out["ok"] and "refused" in out and [i["kind"] for i in items] == ["probe_rejected"]
    assert items[0]["payload"]["freeze_refused"] and items[0]["payload"]["batch_text"] == text


def _opened_setup(tmp_path, monkeypatch, *, commit=None, declared=None, batch=None):
    """A batch frozen (at this checkout's commit) on 2026-01-01, matured, approved, ready for vault_open."""
    import engine.__main__ as cli
    from engine import approvals

    head = ledger._git_commit()
    entries = _entries()
    frozen = vault.freeze(batch or _batch(entries), entries, datetime(2026, 1, 1, tzinfo=timezone.utc), gates=NO_GATES)
    entries = entries + ledger.chain(entries, [ledger.pending("freeze", frozen, dict(CTX, code_commit=commit or head))])
    monkeypatch.setenv("ENGINE_CODE_COMMIT", head if declared is None else declared)
    monkeypatch.setattr(cli, "current_ledger", lambda: entries)
    monkeypatch.setattr(cli, "PENDING", tmp_path / "pending.jsonl")
    monkeypatch.setattr(am, "_t0", lambda *a, **k: SimpleNamespace(load=lambda: object()))
    monkeypatch.setattr(approvals, "owner_approval_from_env", lambda: "xuanhuyle")
    return entries


@pytest.mark.parametrize("commit, declared", [("0" * 40, None), (None, ""), (None, "f" * 40)])
def test_the_vault_scores_only_with_the_code_the_batch_was_frozen_with(tmp_path, monkeypatch, commit, declared):
    """Owner's decision (2026-09-27): a batch is scored at its freeze commit; anything else is refused before the unseal."""
    import engine.__main__ as cli

    _opened_setup(tmp_path, monkeypatch, commit=commit, declared=declared)
    monkeypatch.setattr(vault_run, "score_batch", lambda *a, **k: pytest.fail("scored with the wrong code"))
    out = cli.vault_open(SimpleNamespace(batch_id="B1"))
    items = ledger.read_pending(tmp_path / "pending.jsonl")
    assert not out["ok"] and [i["kind"] for i in items] == ["error"] and "frozen at" in out["refused"]


def test_a_changed_gate_fingerprint_is_refused_before_the_unseal(tmp_path, monkeypatch):
    import engine.__main__ as cli
    from engine import gates

    _opened_setup(tmp_path, monkeypatch)
    monkeypatch.setattr(gates, "gate_fingerprint", lambda: "changed")
    out = cli.vault_open(SimpleNamespace(batch_id="B1"))
    assert not out["ok"] and "fingerprint" in out["refused"]


def test_a_passing_claim_records_what_it_beat(tmp_path, monkeypatch):
    import engine.__main__ as cli

    _opened_setup(tmp_path, monkeypatch)
    monkeypatch.setattr(vault_run, "score_batch", lambda batch, **k: {
        "batch_id": "B1", "batch_sha256": batch["batch_sha256"], "alpha": 0.0125,
        "claims": [{"claim": "C1", "verdict": "PASS", "skill": 0.1, "p_holm": 0.001}]})
    out = cli.vault_open(SimpleNamespace(batch_id="B1"))
    items = ledger.read_pending(tmp_path / "pending.jsonl")
    assert out["ok"] and [i["kind"] for i in items] == ["unseal", "verdict", "accepted_finding"]
    f = items[2]["payload"]
    assert f["beat"] == "C1" and f["comparator"] == "accepted" and len(f["batch_sha256"]) == 64 and f["scope"] == "all"


def test_the_accepted_arm_changes_only_to_an_arm_confirmed_against_it():
    from engine.findings import latest_accepted

    def found(fid, comparator, beat=None, scope="all", covs=("x",)):
        return ("accepted_finding", {"finding_id": fid, "target": "consumption", "scope": scope, "comparator": comparator,
                                     "beat": beat, "arm": {"covariates": [{"id": c} for c in covs]}})
    base = ledger.chain([], legacy.seed_items(CTX))
    assert latest_accepted(base, "consumption")["finding_id"] == "C1"
    weaker = base + ledger.chain(base, [ledger.pending(k, p, CTX) for k, p in (found("B1-C2", "best_simple"),)])
    assert latest_accepted(weaker, "consumption")["finding_id"] == "C1"  # a co-passing arm vs a simple baseline
    winter = base + ledger.chain(base, [ledger.pending(k, p, CTX) for k, p in (found("B1-C1", "accepted", "C1", "winter"),)])
    assert latest_accepted(winter, "consumption")["finding_id"] == "C1"  # scope-limited
    better = base + ledger.chain(base, [ledger.pending(k, p, CTX) for k, p in (found("B1-C1", "accepted", "C1"),)])
    assert latest_accepted(better, "consumption")["finding_id"] == "B1-C1"
    stale = better + ledger.chain(better, [ledger.pending(k, p, CTX) for k, p in (found("B2-C1", "accepted", "C1"),)])
    assert latest_accepted(stale, "consumption")["finding_id"] == "B1-C1"  # it beat an arm that is no longer accepted
    assert latest_accepted(base, "solar") is None


def test_a_crash_after_the_unseal_still_closes_the_batch(tmp_path, monkeypatch):
    import engine.__main__ as cli
    from engine import approvals

    entries = _opened_setup(tmp_path, monkeypatch)
    monkeypatch.setattr(vault_run, "score_batch", lambda *a, **k: 1 / 0)
    out = cli.vault_open(SimpleNamespace(batch_id="B1"))
    items = ledger.read_pending(tmp_path / "pending.jsonl")
    assert out["ok"] and [i["kind"] for i in items] == ["unseal", "verdict"]
    assert items[0]["payload"]["ledger_head_seq"] == entries[-1]["seq"]
    v = items[1]["payload"]
    assert v["void"] and all(c["verdict"] == "NOT PASS" and "ZeroDivisionError" in c["error"] for c in v["claims"])
    after = entries + ledger.chain(entries, items)
    assert vault.open_batches(after) == []
    with pytest.raises(vault.VaultError, match="already opened"):
        vault.open_forward(after, "B1", now=datetime(2030, 1, 1, tzinfo=timezone.utc), model_loaded=True,
                           approved_by="xuanhuyle")


def _per_day(skill, n=168, seed=0, name="a"):
    rng = np.random.default_rng(seed)
    ref = 1000 + rng.normal(0, 40, n)
    arm = ref * (1 - skill) + rng.normal(0, 20, n)
    days = pd.date_range("2026-10-16", periods=n, freq="D").date
    rows = [{"delivery_date": d, "method": name, "sum_abs_err": v * 48, "n": 48} for d, v in zip(days, arm)]
    rows += [{"delivery_date": d, "method": "r", "sum_abs_err": v * 48, "n": 48} for d, v in zip(days, ref)]
    return pd.DataFrame(rows)


def test_decide_passes_real_effects_only():
    f = _frozen()
    good = vault.decide(f, _per_day(0.15), {"C1": ("a", "r")})
    assert good["claims"][0]["verdict"] == "PASS" and good["claims"][0]["blocks"] == 12
    null = vault.decide(f, _per_day(0.0, seed=3), {"C1": ("a", "r")})
    assert null["claims"][0]["verdict"] == "NOT PASS"
    short = vault.decide(f, _per_day(0.3, n=126), {"C1": ("a", "r")})  # 9 of 12 blocks: p := 1
    assert short["claims"][0]["p"] == 1.0 and short["claims"][0]["verdict"] == "NOT PASS"
    # ten blocks are enough (two blocks lost to missing data)
    holes = _per_day(0.15)
    lost = set(pd.date_range("2026-10-16", periods=5, freq="D").date) | set(pd.date_range("2027-03-19", periods=5).date)
    ten = vault.decide(f, holes.loc[~holes["delivery_date"].isin(lost)], {"C1": ("a", "r")})
    assert ten["claims"][0]["blocks"] == 10 and ten["claims"][0]["verdict"] == "PASS"


def test_an_unscorable_claim_stays_in_the_holm_family():
    entries = _entries()
    b = _batch(entries)
    b["claims"].append(dict(b["claims"][0], id="b", statement="another"))
    f = vault.freeze(b, entries, T0, gates=NO_GATES)
    alone = vault.decide(dict(f, claims=f["claims"][:1]), _per_day(0.005, seed=5), {"C1": ("a", "r")})
    both = vault.decide(f, _per_day(0.005, seed=5), {"C1": ("a", "r")}, {"C2": "could not score"})
    assert both["claims"][1]["p"] == 1.0 and both["claims"][1]["error"] == "could not score"
    assert both["claims"][0]["p_holm"] == pytest.approx(min(1.0, 2 * alone["claims"][0]["p"]), abs=1e-8)  # rounded to 8 dp
    void = vault.void_verdict(f, "boom")
    assert void["void"] and [c["verdict"] for c in void["claims"]] == ["NOT PASS", "NOT PASS"]


def test_skill_is_measured_on_the_days_both_methods_scored():
    pd_ = _per_day(0.2)
    extra = pd.DataFrame([{"delivery_date": date(2027, 4, 2), "method": "r", "sum_abs_err": 1e9, "n": 48}])
    f = _frozen()
    a = vault.decide(f, pd_, {"C1": ("a", "r")})["claims"][0]["skill"]
    b = vault.decide(f, pd.concat([pd_, extra], ignore_index=True), {"C1": ("a", "r")})["claims"][0]["skill"]
    assert a == b


def test_score_batch_runs_the_discovery_path_with_live_leak_checks(monkeypatch):
    bundle = td.consumption_bundle(False)
    monkeypatch.setattr(am, "load_bundle", lambda *a, **k: bundle)
    entries = _entries()
    dry = vault.freeze(_batch(entries), entries, datetime(2024, 1, 1, tzinfo=timezone.utc), gates=NO_GATES,
                       rehearsal=True)
    assert dry["window"] == ["2024-01-16", "2024-07-01"]
    out = vault_run.score_batch(dry, cache_dir=Path("."), model=tp.QuantModel())
    c = out["claims"][0]
    assert c["claim"] == "C1" and c["blocks"] == 12 and c["verdict"] in ("PASS", "NOT PASS") and "error" not in c
    assert out["sources"]["consumption"]["chosen"] == "eco2mix-national-cons-def"
    assert len(out["per_day"]["dates"]) == 168
    assert out["leak_checks"] == {"C1:arm": {"pass": True}, "C1:ref": {"pass": True}}


def test_score_batch_turns_a_failed_leak_check_into_an_error(monkeypatch):
    from engine.referee import leakcheck

    bundle = td.consumption_bundle(False)
    monkeypatch.setattr(am, "load_bundle", lambda *a, **k: bundle)
    monkeypatch.setattr(leakcheck, "check_method", lambda *a, **k: {"pass": False})
    entries = _entries()
    dry = vault.freeze(_batch(entries), entries, datetime(2024, 1, 1, tzinfo=timezone.utc), gates=NO_GATES,
                       rehearsal=True)
    out = vault_run.score_batch(dry, cache_dir=Path("."), model=tp.QuantModel())
    c = out["claims"][0]
    assert c["p"] == 1.0 and c["verdict"] == "NOT PASS" and "leak check failed" in c["error"]


def test_a_weather_read_failure_fails_only_the_claims_that_need_weather(monkeypatch):
    bundle = td.consumption_bundle(False)

    def load(target, first, last, cache_dir, *, weather=frozenset(), **k):
        if weather:
            raise RuntimeError("archive down")
        return bundle
    monkeypatch.setattr(am, "load_bundle", load)
    temp = [{"id": "wx_temperature", "transform": "hdd15"}]
    entries = _entries(_result(covariates=temp, vs="best_simple"))
    b = _batch(entries)
    b["claims"].append({"id": "t", "statement": "temperature beats blend_50", "target": "consumption",
                        "arm": {"covariates": temp}, "comparator": "best_simple", "scope": "all", "delta": 0.0,
                        "evidence": [entries[-1]["seq"]]})
    dry = vault.freeze(b, entries, datetime(2024, 1, 1, tzinfo=timezone.utc), gates={("consumption", "wx_temperature")},
                       rehearsal=True)
    out = vault_run.score_batch(dry, cache_dir=Path("."), model=tp.QuantModel())
    c1, c2 = out["claims"]
    assert "error" not in c1 and c1["blocks"] == 12
    assert c2["p"] == 1.0 and "weather temperature unavailable" in c2["error"]


def test_the_rehearsal_projects_evidence_seqs_as_the_record_job_will(tmp_path, monkeypatch):
    """Fix-check: payloads repeated from another run are recorded, so the projected seqs are the real ones."""
    import engine.__main__ as cli

    entries = _entries()
    ctx = dict(CTX, run_id="77", mode="vault_dryrun")
    item = ledger.pending("probe_submitted", {"submitted_by": "referee:rehearsal-evidence", "probe_sha256": "p"}, ctx)
    once = entries + ledger.chain(entries, [dict(item, context=dict(CTX, run_id="76"))])
    projected = cli._projected(once, [item], ctx)
    assert [e["kind"] for e in projected] == ["probe_submitted"] and projected[0]["seq"] == once[-1]["seq"] + 1


def test_the_freeze_pins_the_ledger_schema():
    assert _frozen()["ledger_schema"] == ledger.schema_sha256()


@pytest.mark.parametrize("text", ['{"batch_version": "claims/0", "claims": [{"statement": "\\ud800"}]}',
                                  '{"batch_version": "claims/0", "claims": [{"delta": ' + "9" * 401 + '}]}'])
def test_unstorable_or_overflowing_batches_are_recorded_refusals(tmp_path, monkeypatch, text):
    import engine.__main__ as cli

    monkeypatch.setattr(cli, "current_ledger", lambda: _entries())
    monkeypatch.setattr(cli, "PENDING", tmp_path / "pending.jsonl")
    out = cli.freeze(_cli_args(tmp_path, text))
    items = ledger.read_pending(tmp_path / "pending.jsonl")
    assert out["ok"] and [i["kind"] for i in items] == ["probe_rejected"]


def test_the_researcher_and_the_vault_share_the_freeze_blockers():
    from engine import claims

    f = _frozen()
    open_ = _entries(("freeze", f))
    assert vault.open_batches(open_) == claims.open_batches(open_) == ["B1"]
    assert "still open" in claims.freeze_blockers(open_)[0]
    spent = _entries(*[("freeze", dict(f, batch_id=f"B{i}")) for i in range(1, 5)],
                     *[("verdict", {"batch_id": f"B{i}", "claims": []}) for i in range(1, 5)])
    assert claims.freeze_blockers(spent) == ["the ledger's alpha budget (4 confirmation batches) is spent"]
    assert claims.freeze_blockers(_entries()) == []
