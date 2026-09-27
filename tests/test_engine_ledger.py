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


def test_record_stamps_its_own_run_identity_and_skips_only_its_own_records(tmp_path):
    path = _seeded(tmp_path)
    items = record.prepare(ledger.read(path), [], [_pend("note", {"n": 1}, run_id="forged", mode="vault")],
                           mode="probe", run_id="42", run_attempt="3")
    assert items[0]["context"]["run_id"] == "42" and items[0]["context"]["mode"] == "probe"
    ledger.append(path, items)
    again = record.prepare(ledger.read(path), [], [_pend("note", {"n": 1})], mode="probe", run_id="42", run_attempt="4")
    assert again == []  # a re-run of the same record job adds nothing
    # Fix-check: the same payload from *another* run is a new fact (it was silently dropped before).
    other = record.prepare(ledger.read(path), [], [_pend("note", {"n": 1})], mode="probe", run_id="43", run_attempt="1")
    assert [i["kind"] for i in other] == ["note"]
    # ... and two identical items in one run are both kept
    twice = record.prepare(ledger.read(path), [], [_pend("note", {"n": 2}), _pend("note", {"n": 2})],
                           mode="probe", run_id="44", run_attempt="1")
    assert len(twice) == 2


def _frozen_entry(path, batch_id="B1", sha="s" * 64, rehearsal=False):
    head = ledger.read(path)[-1]["seq"]
    return ledger.append(path, [_pend("freeze", {"batch_id": batch_id, "batch_sha256": sha, "rehearsal": rehearsal,
                                                 "ledger_head_seq": head})])[-1]


def test_record_refuses_a_freeze_only_when_its_state_moved(tmp_path):
    path = _seeded(tmp_path)
    head = ledger.read(path)[-1]["seq"]
    ledger.append(path, [_pend("note", {"n": 1}), _pend("probe_result", {"probe_sha256": "p"})])
    entries = ledger.read(path)
    ok = _pend("freeze", {"batch_id": "B1", "ledger_head_seq": head})
    assert record.prepare(entries, [], [ok], mode="freeze", run_id="1", run_attempt="1")  # notes and results don't matter
    ledger.append(path, [_pend("gate", {"gate": "known_answer"})])
    with pytest.raises(record.RecordError, match="landed since"):
        record.prepare(ledger.read(path), [], [ok], mode="freeze", run_id="1", run_attempt="1")
    for bad in (None, "3", True, 10_000):
        with pytest.raises(record.RecordError, match="does not have"):
            record.prepare(entries, [], [_pend("freeze", {"batch_id": "B1", "ledger_head_seq": bad})],
                           mode="freeze", run_id="1", run_attempt="1")


def test_record_always_records_a_real_unseal_and_refuses_a_forged_one(tmp_path):
    path = _seeded(tmp_path)
    _frozen_entry(path)
    ledger.append(path, [_pend("note", {"n": "something landed after the vault read"})])
    entries = ledger.read(path)
    unseal = _pend("unseal", {"batch_id": "B1", "batch_sha256": "s" * 64, "ledger_head_seq": 3})
    verdict = _pend("verdict", {"batch_id": "B1", "batch_sha256": "s" * 64, "claims": []})
    found = _pend("accepted_finding", {"finding_id": "B1-C1", "batch_sha256": "s" * 64, "target": "consumption"})
    got = record.prepare(entries, [], [unseal, verdict, found], mode="vault", run_id="7", run_attempt="2")
    assert [i["kind"] for i in got] == ["unseal", "verdict", "accepted_finding"]  # a stale head no longer blocks recovery
    for forged in (_pend("unseal", {"batch_id": "B9", "batch_sha256": "s" * 64}),
                   _pend("unseal", {"batch_id": "B1", "batch_sha256": "x" * 64}),
                   _pend("accepted_finding", {"finding_id": "B2-C1", "target": "consumption"})):
        with pytest.raises(record.RecordError, match="matches no frozen batch"):
            record.prepare(entries, [], [forged], mode="vault", run_id="7", run_attempt="1")
    _frozen_entry(path, batch_id="DRY", rehearsal=True)
    with pytest.raises(record.RecordError, match="matches no frozen batch"):
        record.prepare(ledger.read(path), [], [_pend("unseal", {"batch_id": "DRY", "batch_sha256": "s" * 64})],
                       mode="vault", run_id="7", run_attempt="1")


def test_record_reads_only_the_pending_file_its_producer_declared(tmp_path):
    path = _seeded(tmp_path)
    pend = ledger.write_pending(tmp_path / "pending.jsonl", [_pend("note", {"n": 1})])
    sha = record.file_sha256(pend)
    assert record.declared_pending(pend, sha)[0]["kind"] == "note"
    assert record.declared_pending(pend, "none") == [] and record.declared_pending(pend, "") == []
    with pytest.raises(record.RecordError, match="declared"):
        record.declared_pending(pend, "0" * 64)  # e.g. forged by the research job, or a stale attempt's artifact
    base = ["--mode", "probe", "--pending", str(pend), "--ledger", str(path)]
    assert record.main(base + ["--pending-sha256", "0" * 64]) == 1
    assert record.main(base + ["--pending-sha256", sha]) == 0 and ledger.read(path)[-1]["kind"] == "note"
    assert record.file_sha256(tmp_path / "missing.jsonl") == "none"


@pytest.mark.parametrize("mode, referee, vault, action, must", [
    ("vault", "", "failure", "", True), ("vault", "", "success", "", True),
    ("probe", "success", "skipped", "", True), ("gate", "success", "skipped", "", True),
    ("probe", "failure", "skipped", "", False), ("seed", "success", "skipped", "", False),
    ("loop", "success", "skipped", "probe", True), ("loop", "success", "skipped", "freeze", True),
    ("loop", "skipped", "skipped", "stop", False), ("selftest", "success", "skipped", "", False),
])
def test_producing_runs_must_leave_a_record(mode, referee, vault, action, must):
    assert record.must_leave_record(mode, referee, vault, action) is must


def test_record_requires_vault_output_and_finds_the_freeze_commit(tmp_path):
    path = _seeded(tmp_path)
    empty = tmp_path / "none.jsonl"
    assert record.main(["--mode", "vault", "--pending", str(empty), "--ledger", str(path), "--require-pending"]) == 1
    assert record.main(["--mode", "vault", "--pending", str(empty), "--ledger", str(path), "--vault-result", "failure",
                        "--pending-sha256", "none"]) == 1
    with pytest.raises(record.RecordError, match="no frozen batch"):
        record.freeze_commit(ledger.read(path), "B1")
    commit = "a" * 40
    head = ledger.read(path)[-1]["seq"]
    ledger.append(path, [ledger.pending("freeze", {"batch_id": "B1", "ledger_head_seq": head},
                                        dict(_ctx(), code_commit=commit))])
    assert record.freeze_commit(ledger.read(path), "B1") == commit
    assert record.main(["--ledger", str(path), "--freeze-commit", "B1"]) == 0
