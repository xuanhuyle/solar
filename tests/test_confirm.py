"""Tests for the one-shot 2025 confirmation of claim C1: the frozen claim, the vault and the verdict."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_confirm
import test_probes as tp
from solarbench import confirm, odre
from solarbench.data import STEP
from solarbench.forecasters import T0Forecaster
from solarbench.weather import SealedDataError

REV = confirm.CLAIM["t0_arm"]["revision"]


def test_the_claim_is_frozen():
    assert confirm.claim_sha256() == confirm.FROZEN_CLAIM_SHA256
    assert confirm.CLAIM["threshold"] == 0.25 and confirm.CLAIM["period"]["year"] == 2025
    changed = dict(confirm.CLAIM, threshold=0.20)
    assert confirm.claim_sha256(changed) != confirm.FROZEN_CLAIM_SHA256


def test_sealed_data_needs_the_vault(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network touched")

    monkeypatch.setattr(odre.requests, "get", boom)
    with pytest.raises(SealedDataError):
        odre.fetch_columns(odre.NATIONAL, ["date_heure"], "2024-09-01", "2026-01-01", tmp_path)
    fake = type("Fake", (), {"valid": lambda self: True})()
    with pytest.raises(confirm.VaultError):
        odre.fetch_columns(odre.NATIONAL, ["date_heure"], "2024-09-01", "2026-01-01", tmp_path, sealed_access=fake)


def test_the_vault_refuses_a_changed_claim_an_unloaded_model_and_a_second_use(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.jsonl"
    access = confirm.open_sealed(model_loaded=True, ledger=ledger)
    assert access.valid()
    with pytest.raises(confirm.VaultError, match="model"):
        confirm.open_sealed(model_loaded=False, ledger=ledger)
    ledger.write_text(json.dumps({"claim_id": "C1", "run": "https://example/run"}) + "\n")
    with pytest.raises(confirm.VaultError, match="already"):
        confirm.open_sealed(model_loaded=True, ledger=ledger)
    monkeypatch.setitem(confirm.CLAIM, "threshold", 0.10)
    with pytest.raises(confirm.VaultError, match="differs"):
        confirm.open_sealed(model_loaded=True, ledger=tmp_path / "empty.jsonl")
    assert not access.valid()


def test_committed_ledger_entries_are_well_formed():
    for entry in confirm.ledger_entries():
        assert entry["claim_id"] == "C1" and entry["claim_sha256"] == confirm.FROZEN_CLAIM_SHA256
        assert entry["verdict"] in ("CONFIRMED", "NOT CONFIRMED", "INCONCLUSIVE") and entry["run"]


def test_the_committed_ledger_keeps_the_vault_shut():
    assert [e["claim_id"] for e in confirm.ledger_entries()] == ["C1"], "C1 was tested once, in run #20"
    with pytest.raises(confirm.VaultError, match="already"):
        confirm.open_sealed(model_loaded=True)


def test_lower_bound_and_verdict_by_hand():
    draws = np.linspace(0.0, 1.0, 101)
    assert confirm.lower_bound(draws) == pytest.approx(0.05)
    assert confirm.verdict(0.26, 365) == "CONFIRMED"
    assert confirm.verdict(0.25, 365) == "NOT CONFIRMED"
    assert confirm.verdict(0.60, 299) == "INCONCLUSIVE"
    assert confirm.verdict(None, 365) == "INCONCLUSIVE"


def test_source_rule():
    assert confirm.choose_source({"eco2mix-national-cons-def": 0.99}) == "eco2mix-national-cons-def"
    assert confirm.choose_source({"eco2mix-national-cons-def": 0.4, "eco2mix-national-tr": 0.97}) == "eco2mix-national-tr"
    assert confirm.choose_source({"eco2mix-national-cons-def": 0.4, "eco2mix-national-tr": 0.9}) is None


def _consumption(start, end):
    index = pd.date_range(start, end, freq=STEP, tz="UTC", inclusive="left")
    local = index.tz_convert("Europe/Paris")
    rng = np.random.default_rng(3)
    return pd.Series(50_000 + 8_000 * np.sin((local.hour + local.minute / 60) / 24 * 2 * np.pi)
                     - 6_000 * (local.dayofweek >= 5) + rng.normal(0, 800, len(index)), index=index)


@pytest.mark.parametrize("year,sealed", [(2024, False), (2025, True)])
def test_confirmation_end_to_end_offline(tmp_path, monkeypatch, year, sealed):
    seen = []

    def fetch(dataset, columns, start, end, cache, *, sealed_access=None, **k):
        seen.append((dataset, start, end, sealed_access))
        if pd.Timestamp(end) > pd.Timestamp("2025-01-01") and sealed_access is None:
            raise SealedDataError("sealed")
        return Path(f"{dataset}|{columns[-1]}|{start}|{end}")

    def load_column(path, column, **k):
        dataset, col, start, end = str(path).split("|")
        return _consumption(start, end) * (1.01 if col == "prevision_j1" else 1.0)

    monkeypatch.setattr(odre, "fetch_columns", fetch)
    monkeypatch.setattr(odre, "load_column", load_column)
    model = tp.QuantModel()
    monkeypatch.setattr(T0Forecaster, "load", lambda self: self._model or model)
    ledger = tmp_path / "ledger.jsonl"
    rc = run_confirm.main(["--year", str(year), "--revision", REV, "--results-dir", str(tmp_path),
                           "--ledger", str(ledger), "--probe-cache", str(tmp_path)])
    assert rc == 0
    out = json.loads((tmp_path / "confirm.json").read_text())
    assert out["source"] == "eco2mix-national-cons-def" and out["scored_days"] >= 360
    assert out["verdict"] in ("CONFIRMED", "NOT CONFIRMED")
    assert out["claim_sha256"] == confirm.FROZEN_CLAIM_SHA256
    assert all((acc is not None) == sealed for _, _, _, acc in seen)
    assert not ledger.exists(), "the runner never writes the ledger; the result is committed by hand"


def test_the_runner_refuses_another_model(tmp_path):
    with pytest.raises(SystemExit, match="pinned"):
        run_confirm.main(["--year", "2025", "--revision", "main", "--results-dir", str(tmp_path)])


def test_a_source_that_stops_early_fails_the_coverage_rule(tmp_path, monkeypatch):
    def fetch(dataset, columns, start, end, cache, *, sealed_access=None, **k):
        return Path(f"{dataset}|{columns[-1]}|{start}|{end}")

    def load_column(path, column, **k):
        dataset, col, start, end = str(path).split("|")
        stop = "2025-07-01" if dataset == "eco2mix-national-cons-def" else end
        return _consumption(start, stop)

    monkeypatch.setattr(odre, "fetch_columns", fetch)
    monkeypatch.setattr(odre, "load_column", load_column)
    args = run_confirm.parse_args(["--year", "2025", "--probe-cache", str(tmp_path)])
    source, load, ref, coverage = run_confirm.load_source(args, access=None)
    assert coverage["eco2mix-national-cons-def"] < 0.6 and source == "eco2mix-national-tr"
