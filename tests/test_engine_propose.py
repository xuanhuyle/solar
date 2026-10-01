"""Proposal-only research mode (engine/propose.py): the answer can never execute anything; every call is recorded;
the loop researcher, the ledger schema pinned by batch B1 and the workflow's trust boundaries are unchanged."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import ledger, legacy, propose, record, researcher

yaml = pytest.importorskip("yaml")

CTX = {"at": "2026-10-01T08:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "x",
       "config_sha256": "c" * 64, "actor": "t", "mode": "t"}
B1_LEDGER_SCHEMA = "ce2ed6e8a12032542941e2fbd22aba4c527595af715a5f962bbb913bfde4bcef"
LOOP_SYSTEM_SHA256 = "f6c2af00a218e17de5c3236e66428c41e8275e71243f32050b8c613e94db48fd"  # ledger seqs 58-70
NOW = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)


def _entries():
    return ledger.chain([], legacy.seed_items(CTX))


def _pack(entries, ids=("X1", "X2")):
    h = ledger.head(entries)
    pack = {"built_from": {"ledger": {"head_seq": h["seq"], "head_sha256": h["sha256"]}}, "record_ids": list(ids),
            "records": [{"id": i} for i in ids]}
    text = json.dumps(pack, sort_keys=True)
    return text, pack, hashlib.sha256(text.encode()).hexdigest()


def _element(v="x"):
    return {"value": v, "status": "proposed", "evidence_ids": ["X1"]}


def _outcome():
    return {"what_would_count": "a", "knowledge_update": "b", "what_next": "c"}


def _candidate(cid):
    c = {f: "text" for f in propose.CANDIDATE_FIELDS}
    c.update(id=cid, motivating_evidence={"explanation": "e", "evidence_ids": ["X1"]}, competing_explanations=["k"])
    return c


def answer(action="propose", n=2, **over):
    a = {"action": action, "summary": "s",
         "A_learned": [{"finding": "f", "status": "exploratory", "evidence_ids": ["X1", "X2"]}],
         "B_unexplained": [{"issue": "i", "why_it_matters": "w", "evidence_ids": ["X2"]}],
         "C_candidates": [_candidate(f"I{i + 1}") for i in range(n)],
         "D_decision": {"chosen": "I1" if action == "propose" else "none", "why_this_is_a_meaningful_next_step": "m",
                        "why_not_the_others": "o", "abstention_reason": None if action == "propose" else "too little"},
         "E_protocol": {f: _element() for f in propose.PROTOCOL_FIELDS} if action == "propose" else None,
         "F_knowledge_update": {o: _outcome() for o in propose.OUTCOMES}}
    a.update(over)
    return a


def _resp(text, stop="end_turn"):
    return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
                           stop_reason=stop, model="served-model", _request_id=None,
                           stop_details=SimpleNamespace(category="cyber") if stop == "refusal" else None,
                           usage=SimpleNamespace(input_tokens=50000, output_tokens=9000, cache_read_input_tokens=0,
                                                 cache_creation_input_tokens=4000))


class FakeCall:
    def __init__(self, *outcomes):
        self.outcomes, self.requests = list(outcomes), []

    def __call__(self, client, model, effort, system, messages):
        self.requests.append({"model": model, "effort": effort, "system": system, "messages": messages})
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out, "req_stream"


def _run(call, entries=None, pack=None, **kw):
    entries = entries or _entries()
    text, p, sha = pack or _pack(entries)
    recorded = []
    result, calls = propose.propose(None, "model-x", "high", entries, text, p, sha, pack_path="docs/pack.json",
                                    now=NOW, on_call=recorded.append, call=call, sleep=lambda s: None, **kw)
    return result, calls, recorded


# ------------------------------------------------------------------ the answer cannot execute anything


def _keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _keys(v)


def test_the_schema_has_no_probe_or_freeze_path_and_is_closed():
    schema = propose.proposal_schema()
    keys = set(_keys(schema))
    assert not keys & {"probe", "claim_batch", "spec", "batch", "freeze"}
    assert schema["properties"]["action"]["enum"] == ["propose", "abstain"]

    def closed(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node["additionalProperties"] is False and set(node["required"]) == set(node["properties"])
            for v in node.values():
                closed(v)
        elif isinstance(node, list):
            for v in node:
                closed(v)
    closed(schema)


def test_the_owner_mandate_is_carried_verbatim_and_the_rules_are_pinned():
    assert propose.MANDATE in propose.PROPOSAL_RULES
    assert propose.MANDATE.startswith("Review the accumulated findings, failures and unresolved questions")
    assert "You are not rewarded for discovering a positive result." in propose.MANDATE
    assert "what you would investigate next under either outcome." in propose.MANDATE
    for phrase in ("t0-beta", "abstain", "economic usefulness", "sealed", "read-only"):
        assert phrase in propose.PROPOSAL_RULES
    # The loop's objective (one confirmed positive finding) is not reused as a rule here.
    assert researcher.OBJECTIVE not in propose.PROPOSAL_RULES and researcher.RULES not in propose.PROPOSAL_RULES


# ------------------------------------------------------------------ validation


def test_a_valid_proposal_and_a_valid_abstention_pass():
    ids = {"X1", "X2"}
    assert propose.validate_proposal(answer(), ids) == []
    assert propose.validate_proposal(answer("abstain", n=0), ids) == []
    assert propose.validate_proposal(answer("abstain", n=2), ids) == []


@pytest.mark.parametrize("bad, needle", [
    (answer(n=4, D_decision={"chosen": "I1", "why_this_is_a_meaningful_next_step": "m", "why_not_the_others": "o",
                             "abstention_reason": None}), "at most 3"),
    (answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["NOPE"]}]), "not in the evidence pack"),
    (answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": []}]), "cites no evidence"),
    (answer("abstain", n=0, E_protocol={f: _element() for f in propose.PROTOCOL_FIELDS}), "E_protocol to null"),
    (answer("abstain", n=0, D_decision={"chosen": "none", "why_this_is_a_meaningful_next_step": "",
                                        "why_not_the_others": "", "abstention_reason": " "}), "abstention_reason"),
    (answer(D_decision={"chosen": "I3", "why_this_is_a_meaningful_next_step": "m", "why_not_the_others": "o",
                        "abstention_reason": None}), "not one of the candidates"),
    (answer(E_protocol=None), "needs E_protocol"),
    (answer(summary="x" * (propose.MAX_STRING + 1)), "longer than"),
    (answer(C_candidates=[_candidate("I2")]), "I1, I2, I3 in order"),
    (answer(action="probe"), "is not one of ['propose', 'abstain']"),
])
def test_invalid_proposals_are_refused(bad, needle):
    errors = propose.validate_proposal(bad, {"X1", "X2"})
    assert any(needle in e for e in errors), errors


# ------------------------------------------------------------------ the call and its record


def test_a_valid_proposal_is_recorded_with_the_pack_hash():
    call = FakeCall(_resp(json.dumps(answer())))
    result, calls, recorded = _run(call)
    assert result["action"] == "propose" and result["proposal"]["D_decision"]["chosen"] == "I1"
    assert len(calls) == len(recorded) == 1
    c = recorded[0]
    text, _, sha = _pack(_entries())
    assert c["purpose"] == "proposal" and c["evidence_pack_sha256"] == sha and c["action"] == "propose"
    assert c["user_prompt"] == propose.user_prompt(text, sha) and text in c["user_prompt"]
    assert c["system_sha256"] == hashlib.sha256(propose.system_text().encode()).hexdigest()
    assert c["proposal_rules_sha256"] == hashlib.sha256(propose.PROPOSAL_RULES.encode()).hexdigest()
    assert c["schema_sha256"] == propose.schema_sha256() and c["evidence_ids_cited"] == ["X1", "X2"]
    assert c["served_model"] == "served-model" and c["request_id"] == "req_stream" and c["response_text"]
    assert c["usage"]["input_tokens"] == 50000 and c["ledger_head"] == ledger.head(_entries())
    assert call.requests[0]["system"] == propose.system_text() and call.requests[0]["effort"] == "high"
    assert propose.system_text().startswith(propose.PROPOSAL_RULES)
    assert json.dumps(propose.proposal_schema(), indent=1) in propose.system_text()


def test_an_abstention_is_recorded_as_such():
    result, _, recorded = _run(FakeCall(_resp(json.dumps(answer("abstain", n=1)))))
    assert result["action"] == "abstain" and recorded[0]["action"] == "abstain"


def test_an_invalid_answer_gets_exactly_one_repair_with_only_the_validators_text():
    bad = answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["NOPE"]}])
    call = FakeCall(_resp(json.dumps(bad)), _resp(json.dumps(answer())))
    result, calls, recorded = _run(call)
    assert result["action"] == "propose" and len(recorded) == 2 and "invalid" in recorded[0]
    repair = call.requests[1]["messages"]
    assert [m["role"] for m in repair] == ["user", "assistant", "user"]
    assert repair[2]["content"].startswith("The answer failed these checks:") and "NOPE" in repair[2]["content"]
    assert recorded[1]["repair_prompt"] == repair[2]["content"]


def test_a_second_invalid_answer_is_an_error_and_both_calls_are_recorded():
    bad = json.dumps(answer(n=4))
    result, calls, recorded = _run(FakeCall(_resp(bad), _resp(bad)))
    assert result["action"] == "error" and len(recorded) == 2 and all("invalid" in r for r in recorded)


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_a_refusal_or_truncation_is_recorded_and_ends_the_call(stop):
    result, calls, recorded = _run(FakeCall(_resp("{}", stop=stop)))
    assert result == {"action": "error", "error": stop} and len(recorded) == 1
    if stop == "refusal":
        assert recorded[0]["refusal_category"] == "cyber"


def test_a_transient_error_is_retried_and_every_attempt_recorded():
    err = type("APIConnectionError", (Exception,), {})("dropped")
    result, calls, recorded = _run(FakeCall(err, _resp(json.dumps(answer()))))
    assert result["action"] == "propose" and len(recorded) == 2 and recorded[0]["transient"] is True


def test_a_pack_built_against_another_ledger_head_is_refused_before_any_call():
    entries = _entries()
    text, pack, sha = _pack(entries)
    pack["built_from"]["ledger"]["head_seq"] = 999
    call = FakeCall()
    with pytest.raises(SystemExit, match="rebuild the pack"):
        _run(call, entries=entries, pack=(text, pack, sha))
    assert call.requests == []


def test_a_pack_with_another_hash_is_refused(tmp_path):
    path = tmp_path / "pack.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="refused"):
        propose.load_pack(path, "0" * 64)
    with pytest.raises(SystemExit, match="refused"):
        propose.load_pack(path, "")
    assert propose.load_pack(path, hashlib.sha256(b"{}").hexdigest())[1] == {}


def _main_setup(tmp_path, monkeypatch, *, change_source=False):
    entries = _entries()
    led = tmp_path / "ledger.jsonl"
    led.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    (tmp_path / "a.md").write_text("one", encoding="utf-8")
    _, pack_obj, _ = _pack(entries)
    pack_obj["built_from"]["repo_files_sha256"] = {"a.md": hashlib.sha256(b"one").hexdigest()}
    text = json.dumps(pack_obj, sort_keys=True)
    sha = hashlib.sha256(text.encode()).hexdigest()
    pack = tmp_path / "pack.json"
    pack.write_text(text, encoding="utf-8")
    if change_source:
        (tmp_path / "a.md").write_text("two", encoding="utf-8")  # a source changed after the pack was built
    monkeypatch.chdir(tmp_path)
    return led, pack, sha


def test_main_refuses_a_stale_pack_before_any_call_or_output(tmp_path, monkeypatch):
    led, pack, sha = _main_setup(tmp_path, monkeypatch, change_source=True)
    monkeypatch.setenv("RESEARCHER_MODEL", "model-x")
    monkeypatch.setenv("EVIDENCE_SHA256", sha)
    call = FakeCall(_resp(json.dumps(answer())))
    monkeypatch.setattr(propose, "call_stream", call)
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match="stale"):
        propose.main(["--ledger", str(led), "--pack", str(pack), "--out", str(out)])
    assert call.requests == [] and not out.exists()


def test_main_writes_only_the_proposal_and_its_record(tmp_path, monkeypatch):
    led, pack, sha = _main_setup(tmp_path, monkeypatch)
    monkeypatch.setenv("RESEARCHER_MODEL", "model-x")
    monkeypatch.setenv("EVIDENCE_SHA256", sha)
    monkeypatch.setattr(propose, "call_stream", FakeCall(_resp(json.dumps(answer()))))
    anthropic = pytest.importorskip("anthropic")
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: None)
    original = propose.propose
    monkeypatch.setattr(propose, "propose", lambda *a, **kw: original(*a, **kw, call=propose.call_stream))
    out = tmp_path / "out"
    assert propose.main(["--ledger", str(led), "--pack", str(pack), "--out", str(out)]) == 0
    assert sorted(p.name for p in out.iterdir()) == ["pending_research.jsonl", "proposal.json"]
    items = ledger.read_pending(out / "pending_research.jsonl")
    assert [i["kind"] for i in items] == ["research_call"]
    assert json.loads((out / "proposal.json").read_text())["action"] == "propose"


# ------------------------------------------------------------------ the record job and the ledger schema


def _pend(kind, payload):
    return ledger.pending(kind, payload, CTX)


def test_the_record_job_accepts_only_research_calls_in_propose_mode():
    entries = _entries()
    ok = record.prepare(entries, [_pend("research_call", {"purpose": "proposal"})], [], mode="propose",
                        run_id="5", run_attempt="1")
    assert [i["kind"] for i in ok] == ["research_call"] and ok[0]["context"]["mode"] == "propose"
    for kind in ("probe_result", "probe_submitted", "freeze", "note", "error", "unseal", "verdict", "gate"):
        with pytest.raises(record.RecordError):
            record.prepare(entries, [], [_pend(kind, {"x": 1})], mode="propose", run_id="5", run_attempt="1")
    with pytest.raises(record.RecordError):
        record.prepare(entries, [_pend("freeze", {"x": 1})], [], mode="propose", run_id="5", run_attempt="1")
    with pytest.raises(record.RecordError):  # research records stay refused outside the research modes
        record.prepare(entries, [_pend("research_call", {"a": 1})], [], mode="probe", run_id="5", run_attempt="1")
    assert not record.must_leave_record("propose", "skipped", "skipped", "propose")


def test_the_ledger_schema_pinned_by_b1_and_the_loop_researcher_are_unchanged():
    assert ledger.schema_sha256() == B1_LEDGER_SCHEMA
    assert researcher._sha(researcher.system_prompt()) == LOOP_SYSTEM_SHA256


# ------------------------------------------------------------------ the workflow


@pytest.fixture(scope="module")
def workflow():
    return yaml.safe_load((ROOT / ".github" / "workflows" / "engine.yml").read_text(encoding="utf-8"))


def test_the_workflow_runs_only_the_researcher_in_propose_mode(workflow):
    jobs = workflow["jobs"]
    trigger = workflow.get("on", workflow.get(True))
    inputs = trigger["workflow_dispatch"]["inputs"]
    assert "propose" in inputs["mode"]["options"] and inputs["evidence_sha256"]["default"] == ""
    assert jobs["research"]["if"] == "inputs.mode == 'loop' || inputs.mode == 'propose'"
    assert "inputs.mode != 'propose'" in jobs["referee"]["if"]
    assert jobs["vault"]["if"] == "inputs.mode == 'vault'"
    assert "inputs.mode == 'loop'" in jobs["chain"]["if"]
    decide = next(s for s in jobs["research"]["steps"] if s.get("id") == "decide")
    assert "HF_TOKEN" not in json.dumps(jobs["research"]) and jobs["research"]["permissions"] == {"contents": "read"}
    assert decide["env"]["EVIDENCE_SHA256"] == "${{ inputs.evidence_sha256 }}"
    assert "inputs." not in decide["run"]
    # The workflow now runs the second decision (mandate v2); the first (v1) is history and is never dispatched again.
    assert "python -m engine.propose_v2 --ledger ledgerro/ledger.jsonl --out research" in decide["run"]
    assert "--pack docs/experiment_5/evidence_pack_v2.json" in decide["run"]
    assert "python -m engine.propose " not in decide["run"] and "evidence_pack.json" not in decide["run"]


def test_the_first_decision_stays_reproducible():
    """The first decision (ledger seq 74) is history: its mandate, rules, schema and system text must not change,
    so render_researcher_docs.py --verify keeps reproducing its record."""
    assert propose.schema_sha256() == "cf2ecda7995e8ecbd5353ce98e3da014e07ed0cb74ea64c7ed0011d64f9ad859"
    assert hashlib.sha256(propose.PROPOSAL_RULES.encode()).hexdigest() == \
        "5cc6c4460586ac0d2594ff3efde585ba31048ab024ba6c4877f884dfb4ee412d"
    assert hashlib.sha256(propose.system_text().encode()).hexdigest() == \
        "29b8b29b597a6b851947c8ab8a3a6bf5071d9f89392190f9dd86d9e6dd32fc04"
    assert hashlib.sha256(propose.MANDATE.encode()).hexdigest() == \
        "beaeb415037078ddd5a8721df1adf0d3d32f621807f0c316e5bffb4339374754"


def test_a_pack_whose_sources_changed_since_it_was_built_is_refused(tmp_path):
    (tmp_path / "a.md").write_text("one", encoding="utf-8")
    pack = {"built_from": {"repo_files_sha256": {"a.md": hashlib.sha256(b"one").hexdigest()}}}
    assert propose.stale_sources(pack, tmp_path) == []
    (tmp_path / "a.md").write_text("two", encoding="utf-8")
    assert propose.stale_sources(pack, tmp_path) == ["a.md"]
    (tmp_path / "a.md").unlink()
    assert propose.stale_sources(pack, tmp_path) == ["a.md"]


def test_the_committed_pack_is_well_formed():
    # Its currency is checked at dispatch (propose.main refuses a stale pack); after the call the pack is the
    # historical record of what the researcher received, so later edits to its sources must not fail this test.
    pack = json.loads((ROOT / "docs" / "experiment_5" / "evidence_pack.json").read_text(encoding="utf-8"))
    ids = pack["record_ids"]
    assert len(ids) == len(set(ids)) == len(pack["records"]) and ids == [r["id"] for r in pack["records"]]
    assert {r["evidence_grade"] for r in pack["records"]} <= set(pack["evidence_grades"])
    assert {r["verification"] for r in pack["records"]} <= set(pack["verification_labels"])


def test_confirmed_means_the_packs_own_grade():
    assert "Only records graded confirmed_on_sealed_data count as confirmed." in " ".join(propose.PROPOSAL_RULES.split())


@pytest.mark.parametrize("mutate, needle", [
    (lambda a: a.pop("summary"), "missing field 'summary'"),
    (lambda a: a.update(extra=1), "unexpected field 'extra'"),
    (lambda a: a["A_learned"][0].update(status="probable"), "is not one of"),
    (lambda a: a.update(A_learned="x"), "expected array"),
    (lambda a: a["C_candidates"][0].pop("hypothesis"), "missing field 'hypothesis'"),
    (lambda a: a.update(E_protocol="none"), "matches none of the allowed forms"),
    (lambda a: a["F_knowledge_update"].pop("insufficient_data_quality"), "missing field"),
])
def test_the_answer_is_checked_against_the_schema_in_code(mutate, needle):
    a = answer()
    mutate(a)
    errors = propose.validate_proposal(a, {"X1", "X2"})
    assert any(needle in e for e in errors), errors


def test_the_request_has_no_grammar_constrained_format_and_fences_are_tolerated():
    class Stream:
        request_id = "req_s"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def __iter__(self):
            return iter(())

        def get_final_message(self):
            return _resp("```json\n" + json.dumps(answer()) + "\n```")
    seen = {}

    class Client:
        messages = SimpleNamespace(stream=lambda **kw: seen.update(kw) or Stream())
    resp, rid = propose.call_stream(Client(), "m", "high", "sys", [{"role": "user", "content": "u"}])
    assert seen["output_config"] == {"effort": "high"} and "format" not in seen["output_config"]
    assert seen["max_tokens"] == propose.PROPOSAL_MAX_TOKENS and seen["thinking"] == {"type": "adaptive"}
    assert rid == "req_s" and propose.parse_answer(resp.content[1].text)["action"] == "propose"
