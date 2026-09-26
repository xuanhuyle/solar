"""The engine ledger: hash chain, tamper detection, pending entries, seed and digest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine import ledger, legacy, record
from engine.canon import canonical_json


def _ctx(mode="test", config="c" * 64):
    return {"at": "2026-09-26T00:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "abc",
            "config_sha256": config, "actor": "tester", "mode": mode}


def _seeded(tmp_path) -> Path:
    path = tmp_path / "ledger.jsonl"
    ledger.append(path, legacy.seed_items(_ctx("seed")))
    return path


def _lines(path):
    return path.read_text(encoding="utf-8").splitlines()


def test_seed_builds_a_verified_chain(tmp_path):
    path = _seeded(tmp_path)
    entries = ledger.read(path)
    kinds = [e["kind"] for e in entries]
    assert kinds[0] == "genesis" and kinds[1] == "config" and kinds[-1] == "accepted_finding"
    assert kinds.count("legacy_result") == len(legacy.LEGACY_RESULTS) + 1
    c1 = next(e for e in entries if e["kind"] == "legacy_result" and e["payload"]["id"] == "C1")
    line = next(l for l in Path(legacy.confirm.LEDGER).read_text(encoding="utf-8").splitlines() if l.strip())
    assert c1["payload"]["confirmations_jsonl_line"] == json.loads(line)
    assert all(e["payload"].get("status", ledger.LEGACY) == ledger.LEGACY
               for e in entries if e["kind"] == "legacy_result")


@pytest.mark.parametrize("attack", ["edit", "drop", "reorder", "insert", "edit_and_rehash"])
def test_tampering_breaks_the_chain(tmp_path, attack):
    path = _seeded(tmp_path)
    lines = _lines(path)
    if attack == "edit":
        e = json.loads(lines[4]); e["payload"]["summary"] = "won"; lines[4] = canonical_json(e)
    elif attack == "drop":
        del lines[5]
    elif attack == "reorder":
        lines[3], lines[4] = lines[4], lines[3]
    elif attack == "insert":
        lines.insert(3, lines[3])
    elif attack == "edit_and_rehash":  # a forger who recomputes the entry's own hash still breaks the next link
        e = json.loads(lines[4]); e["payload"]["summary"] = "won"; e["sha256"] = ledger.entry_sha256(e)
        lines[4] = canonical_json(e)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ledger.LedgerError):
        ledger.read(path)


def test_genesis_only_once_and_nothing_before_it(tmp_path):
    path = tmp_path / "l.jsonl"
    with pytest.raises(ledger.LedgerError, match="genesis"):
        ledger.append(path, [ledger.pending("note", {"x": 1}, _ctx())])
    path = _seeded(tmp_path)
    n = len(ledger.read(path))
    assert ledger.append(path, legacy.seed_items(_ctx("seed")))[0]["kind"] == "legacy_result"  # genesis skipped
    assert sum(e["kind"] == "genesis" for e in ledger.read(path)) == 1 and len(ledger.read(path)) > n


def test_config_entry_marks_every_change_of_referee_code(tmp_path):
    path = _seeded(tmp_path)
    ledger.append(path, [ledger.pending("note", {"a": 1}, _ctx(config="c" * 64))])
    assert ledger.read(path)[-1]["kind"] == "note"  # same fingerprint: no new config entry
    ledger.append(path, [ledger.pending("note", {"a": 2}, _ctx(config="d" * 64))], manifest={"engine/x.py": "e" * 64})
    tail = ledger.read(path)[-2:]
    assert [e["kind"] for e in tail] == ["config", "note"] and tail[0]["payload"]["config_sha256"] == "d" * 64


def test_pending_entries_are_validated(tmp_path):
    with pytest.raises(ledger.LedgerError):
        ledger.pending("made_up", {}, _ctx())
    with pytest.raises(ledger.LedgerError, match="non-finite"):
        ledger.pending("note", {"x": float("nan")}, _ctx())
    bad = tmp_path / "p.jsonl"
    bad.write_text(json.dumps({"kind": "note", "payload": {}, "context": {"at": "x"}}) + "\n")
    with pytest.raises(ledger.LedgerError, match="malformed"):
        ledger.read_pending(bad)


def test_record_cli_appends_and_verifies(tmp_path, capsys):
    pend = ledger.write_pending(tmp_path / "pending.jsonl", legacy.seed_items(_ctx("seed")))
    assert record.main(["--mode", "seed", "--pending", str(pend), "--ledger", str(tmp_path / "l.jsonl")]) == 0
    assert record.main(["--verify", str(tmp_path / "l.jsonl")]) == 0
    assert "chain verified" in capsys.readouterr().out


def test_digest_shows_findings_results_and_open_batches(tmp_path):
    path = _seeded(tmp_path)
    ledger.append(path, [
        ledger.pending("probe_result", {"probe_sha256": "p1", "status": ledger.EXPLORATORY, "skill": 0.1}, _ctx()),
        ledger.pending("freeze", {"batch_id": "B1", "window": ["2026-11-21", "2027-02-12"]}, _ctx()),
    ])
    d = ledger.digest(ledger.read(path))
    assert d["accepted_findings"][0]["finding_id"] == "C1"
    assert d["probe_results"][0]["status"] == ledger.EXPLORATORY
    assert d["open_batches"] == [{"seq": d["head"]["seq"], "batch_id": "B1", "window": ["2026-11-21", "2027-02-12"]}]


# ------------------------------------------------------------ record trust


def _pend(kind, payload, **ctx):
    return ledger.pending(kind, payload, dict(_ctx(), **ctx))


def test_record_allows_kinds_by_source_and_mode(tmp_path):
    path = _seeded(tmp_path)
    entries = ledger.read(path)
    forged = [_pend("accepted_finding", {"finding_id": "X", "target": "consumption"})]
    with pytest.raises(record.RecordError, match="research file may not carry"):
        record.prepare(entries, forged, [], mode="loop", run_id="9", run_attempt="1")
    with pytest.raises(record.RecordError, match="may not carry 'verdict'"):
        record.prepare(entries, [], [_pend("verdict", {"batch_id": "B1"})], mode="probe", run_id="9", run_attempt="1")
    with pytest.raises(record.RecordError, match="outside loop mode"):
        record.prepare(entries, [_pend("research_call", {"a": 1})], [], mode="probe", run_id="9", run_attempt="1")
    ok = record.prepare(entries, [_pend("research_call", {"a": 1})], [_pend("probe_rejected", {"r": 1})],
                        mode="loop", run_id="9", run_attempt="2")
    assert [i["kind"] for i in ok] == ["research_call", "probe_rejected"]


def test_record_stamps_its_own_run_identity_and_skips_duplicates(tmp_path):
    path = _seeded(tmp_path)
    items = record.prepare(ledger.read(path), [], [_pend("note", {"n": 1}, run_id="forged", mode="vault")],
                           mode="probe", run_id="42", run_attempt="3")
    assert items[0]["context"]["run_id"] == "42" and items[0]["context"]["mode"] == "probe"
    ledger.append(path, items)
    again = record.prepare(ledger.read(path), [], [_pend("note", {"n": 1})], mode="probe", run_id="42", run_attempt="4")
    assert again == []  # a re-run of the same record job adds nothing


def test_record_refuses_stale_freezes_and_requires_vault_output(tmp_path):
    path = _seeded(tmp_path)
    entries = ledger.read(path)
    stale = _pend("freeze", {"batch_id": "B1", "ledger_head_seq": entries[-1]["seq"] - 1})
    with pytest.raises(record.RecordError, match="refused"):
        record.prepare(entries, [], [stale], mode="freeze", run_id="1", run_attempt="1")
    fresh = _pend("freeze", {"batch_id": "B1", "ledger_head_seq": entries[-1]["seq"]})
    assert record.prepare(entries, [], [fresh], mode="freeze", run_id="1", run_attempt="1")
    empty = tmp_path / "none.jsonl"
    assert record.main(["--mode", "vault", "--pending", str(empty), "--ledger", str(path), "--require-pending"]) == 1
