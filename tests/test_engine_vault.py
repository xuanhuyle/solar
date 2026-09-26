"""The forward vault: freeze rules, a single guarded opening, the data door, verdicts."""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

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


def _entries(*extra):
    result = ("probe_result", {"probe_sha256": "p", "status": "EXPLORATORY - x", "target": "consumption",
                               "leak_checks_passed": True, "comparisons": [{}]})
    return ledger.chain([], legacy.seed_items(CTX) + [ledger.pending(k, p, CTX) for k, p in (result, *extra)])


def _batch(**over):
    claim = {"id": "a", "statement": "t0 + holiday + bridge days beat the accepted arm", "target": "consumption",
             "arm": {"covariates": [{"id": "holiday", "transform": "raw"}, {"id": "bridge_day", "transform": "raw"}]},
             "comparator": "accepted", "scope": "all", "delta": 0.0, "evidence": [10]}
    claim.update(over)
    return {"batch_version": "claims/0", "claims": [claim]}


def _frozen(entries=None, **over):
    entries = entries if entries is not None else _entries()
    return vault.freeze(_batch(**over), entries, T0)


def test_freeze_sets_window_alpha_and_receipt():
    f = _frozen()
    assert f["batch_id"] == "B1" and f["window"] == ["2026-10-16", "2027-01-07"] and f["alpha"] == 0.0125
    assert f["receipt"] == {"batch_id": "B1", "batch_sha256": f["batch_sha256"], "window": f["window"],
                            "opens_after": "2027-01-10"}
    body = {k: v for k, v in f.items() if k not in ("batch_sha256", "receipt")}
    assert sha256_of(body) == f["batch_sha256"] and f["claims"][0]["id"] == "C1"


@pytest.mark.parametrize("over, reason", [
    ({"comparator": "rte_j1"}, "never decides"),
    ({"delta": 0.3}, "delta"),
    ({"evidence": [3]}, "not a valid exploratory"),
    ({"evidence": []}, "cite at least one"),
    ({"arm": {"covariates": [{"id": "wx_radiation"}]}}, "not in the catalogue"),
    ({"extra": 1}, "fields must be exactly"),
])
def test_invalid_claims_are_refused(over, reason):
    with pytest.raises(vault.VaultError, match=reason):
        _frozen(**over)


def test_one_open_batch_and_four_batches_at_most():
    first = _frozen()
    with pytest.raises(vault.VaultError, match="still open"):
        _frozen(_entries(("freeze", first)))
    closed = [("freeze", dict(first, batch_id=f"B{i}")) for i in range(1, 5)]
    closed += [("verdict", {"batch_id": f"B{i}", "claims": []}) for i in range(1, 5)]
    with pytest.raises(ValueError, match="spent"):
        _frozen(_entries(*closed))


def test_rehearsal_stays_in_the_discovery_zone():
    dry = vault.freeze(_batch(), _entries(), datetime(2025, 1, 1, tzinfo=timezone.utc), rehearsal=True)
    assert dry["batch_id"] == "DRY" and dry["rehearsal"] and dry["window"] == ["2025-01-16", "2025-04-09"]
    with pytest.raises(vault.VaultError, match="discovery zone"):
        vault.freeze(_batch(), _entries(), datetime(2025, 11, 1, tzinfo=timezone.utc), rehearsal=True)
    with pytest.raises(vault.VaultError, match="not confirmable"):
        vault.freeze(_batch(), _entries(), datetime(2025, 3, 1, tzinfo=timezone.utc))  # a real freeze in 2025


def test_the_vault_opens_once_matured_approved_and_loaded(tmp_path, monkeypatch):
    f = _frozen()
    entries = _entries(("freeze", f))
    later = datetime(2027, 1, 11, tzinfo=timezone.utc)
    with pytest.raises(vault.VaultError, match="matures"):
        vault.open_forward(entries, "B1", now=datetime(2027, 1, 8, tzinfo=timezone.utc), model_loaded=True, approved_by="xuanhuyle")
    with pytest.raises(vault.VaultError, match="approval"):
        vault.open_forward(entries, "B1", now=later, model_loaded=True, approved_by=None)
    with pytest.raises(vault.VaultError, match="model"):
        vault.open_forward(entries, "B1", now=later, model_loaded=False, approved_by="xuanhuyle")
    with pytest.raises(vault.VaultError, match="already opened"):
        vault.open_forward(_entries(("freeze", f), ("unseal", {"batch_id": "B1"})), "B1", now=later,
                           model_loaded=True, approved_by="xuanhuyle")
    tampered = dict(f, alpha=0.05)
    with pytest.raises(vault.VaultError, match="freeze hash"):
        vault.open_forward(_entries(("freeze", tampered)), "B1", now=later, model_loaded=True, approved_by="xuanhuyle")
    access, batch = vault.open_forward(entries, "B1", now=later, model_loaded=True, approved_by="xuanhuyle")
    assert vault.access_is_valid(access) and access.first_day == "2026-07-08" and access.last_day == "2027-01-07"
    # the data door: the issued access covers its window only; a look-alike never works
    seen = []
    monkeypatch.setattr(odre, "_download_columns", lambda *a, **k: seen.append(a) or pytest.skip("reached download"))
    forged = data.ForwardAccess(access.batch_id, access.batch_sha256, access.first_day, access.last_day)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2026-12-31", tmp_path, access=forged)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2027-02-01", tmp_path, access=access)
    vault.close(access)
    assert not vault.access_is_valid(access)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-10-16", "2026-12-31", tmp_path, access=access)
    assert not seen


def _per_day(skill, n=84, seed=0):
    rng = np.random.default_rng(seed)
    ref = 1000 + rng.normal(0, 40, n)
    arm = ref * (1 - skill) + rng.normal(0, 20, n)
    days = pd.date_range("2026-10-16", periods=n, freq="D").date
    rows = [{"delivery_date": d, "method": "a", "sum_abs_err": v * 48, "n": 48} for d, v in zip(days, arm)]
    rows += [{"delivery_date": d, "method": "r", "sum_abs_err": v * 48, "n": 48} for d, v in zip(days, ref)]
    return pd.DataFrame(rows)


def test_decide_passes_real_effects_only():
    f = _frozen()
    good = vault.decide(f, _per_day(0.15), {"C1": ("a", "r")})
    assert good["claims"][0]["verdict"] == "PASS" and good["claims"][0]["blocks"] == 6
    null = vault.decide(f, _per_day(0.0, seed=3), {"C1": ("a", "r")})
    assert null["claims"][0]["verdict"] == "NOT PASS"
    short = vault.decide(f, _per_day(0.3, n=70), {"C1": ("a", "r")})  # 5 blocks: p := 1
    assert short["claims"][0]["p"] == 1.0 and short["claims"][0]["verdict"] == "NOT PASS"


def test_score_batch_runs_the_discovery_path(monkeypatch):
    bundle = td.consumption_bundle(False)
    monkeypatch.setattr(am, "load_bundle", lambda *a, **k: bundle)
    dry = vault.freeze(_batch(), _entries(), datetime(2024, 1, 1, tzinfo=timezone.utc), rehearsal=True,
                       accepted=am.latest_accepted([], "consumption"))
    out = vault_run.score_batch(dry, cache_dir=Path("."), model=tp.QuantModel())
    c = out["claims"][0]
    assert c["claim"] == "C1" and c["blocks"] == 6 and c["verdict"] in ("PASS", "NOT PASS")
    assert out["sources"]["consumption"]["chosen"] == "eco2mix-national-cons-def"
    assert len(out["per_day"]["dates"]) == 84
