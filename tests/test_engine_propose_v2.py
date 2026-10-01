"""The second proposal-only decision (mandate v2): the owner's clarification carried verbatim, an answer shape that
cannot execute anything, one decision per mandate, and the first decision left untouched."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import ledger, legacy, propose, propose_v2  # noqa: E402

CTX = {"at": "2026-10-01T08:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "x",
       "config_sha256": "c" * 64, "actor": "t", "mode": "t"}
NOW = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
CLARIFICATION = ROOT / "docs" / "experiment_5" / "NORTH_STAR_CLARIFICATION.md"


def _entries():
    return ledger.chain([], legacy.seed_items(CTX))


def _pack(entries, ids=("X1", "X2")):
    h = ledger.head(entries)
    pack = {"built_from": {"ledger": {"head_seq": h["seq"], "head_sha256": h["sha256"]}}, "record_ids": list(ids),
            "records": [{"id": i} for i in ids]}
    text = json.dumps(pack, sort_keys=True)
    return text, pack, hashlib.sha256(text.encode()).hexdigest()


def _candidate(cid):
    return {"id": cid, "scientific_question": "q",
            "why_it_matters_to_the_north_star": {"components": ["low_data_generalisation"], "explanation": "e"},
            "motivating_evidence": {"explanation": "e", "evidence_ids": ["X1"]},
            "competing_explanations": ["k"],
            "foundation_model_comparative_advantage": {"why_a_foundation_model_might_help": "a",
                                                       "when_a_specialist_model_should_win": "b"},
            "historical_data_requirement": {"what_each_comparator_receives": "a",
                                            "how_levels_are_chosen_without_outcome_tuning": "b"},
            "regime_definition": None, "covariate_search_mechanism": None, "conventional_comparator": "c",
            "research_cost": {k: "x" for k in ("ai_decision_calls", "human_modelling_work", "implementation_work",
                                               "compute", "predictive_evaluations")},
            "possible_outcomes": [{"outcome": "o", "what_we_would_learn": "w"}], "t0_beta": None}


def _s4():
    return {"local_data_scarcity": {"consideration": "c", "can_it_be_tested_credibly_with_existing_evidence_or_data": "t",
                                    "evidence_ids": ["X1"]},
            "regime_change": {"consideration": "c", "evidence_ids": []},
            "cheap_covariate_exploration": {"consideration": "c", "evidence_ids": []},
            "discovery_rather_than_integration": {"consideration": "c", "evidence_ids": []}}


def answer(action="propose", n=2, **over):
    a = {"action": action, "summary": "s", "section_4_consideration": _s4(),
         "A_learned": [{"finding": "f", "status": "exploratory", "evidence_ids": ["X1", "X2"]}],
         "B_unexplained": [{"issue": "i", "why_it_matters": "w", "evidence_ids": ["X2"]}],
         "C_candidates": [_candidate(f"N{i + 1}") for i in range(n)],
         "D_decision": {"chosen": "N1" if action == "propose" else "none", "i1_disposition": "redesigned",
                        "i1_disposition_reasoning": "r", "why_this_is_the_right_next_step": "m",
                        "why_not_the_others": "o",
                        "abstention": None if action == "propose" else
                        {"reason": "too little", "smallest_new_benchmark_or_dataset": "a benchmark"}},
         "E_protocol": ({f: {"value": "v", "status": "proposed", "evidence_ids": ["X1"]}
                         for f in propose_v2.PROTOCOL_FIELDS} if action == "propose" else None),
         "G_accumulated_knowledge": {"new_empirical_knowledge": "k", "how_it_alters_the_next_decision": "n",
                                     "future_controlled_experiment": "f"}}
    a.update(over)
    return a


def _resp(text, stop="end_turn"):
    return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking="t", signature="sig"),
                                    SimpleNamespace(type="text", text=text)],
                           stop_reason=stop, model="served-model", _request_id=None,
                           stop_details=SimpleNamespace(category="cyber") if stop == "refusal" else None,
                           usage=SimpleNamespace(input_tokens=150000, output_tokens=30000, cache_read_input_tokens=0,
                                                 cache_creation_input_tokens=9000))


class FakeCall:
    def __init__(self, *outcomes):
        self.outcomes, self.requests = list(outcomes), []

    def __call__(self, client, model, effort, system, messages):
        self.requests.append({"model": model, "effort": effort, "system": system, "messages": list(messages)})
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out, "req_stream"


def _run(call, entries=None, pack=None, **kw):
    entries = entries or _entries()
    text, p, sha = pack or _pack(entries)
    recorded = []
    result, calls = propose_v2.propose_v2(None, "model-x", "high", entries, text, p, sha,
                                          pack_path="docs/pack_v2.json", now=NOW, on_call=recorded.append, call=call,
                                          sleep=lambda s: None, **kw)
    return result, calls, recorded


def _keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _keys(v)


# ------------------------------------------------------------------ the owner's text, verbatim


def test_the_mandate_is_the_owners_section_7_verbatim():
    doc = CLARIFICATION.read_text(encoding="utf-8")
    assert f"```text\n{propose_v2.MANDATE_V2}\n```" in doc  # quoted in the engineering note
    quoted = [line for line in propose_v2.owner_section(7).splitlines() if line.startswith(">")]
    assert "\n".join(line[2:] if line.startswith("> ") else line[1:] for line in quoted) == propose_v2.MANDATE_V2
    sha = hashlib.sha256(propose_v2.MANDATE_V2.encode()).hexdigest()
    assert sha in doc and hashlib.sha256(propose.MANDATE.encode()).hexdigest() in doc


def test_the_rules_carry_the_owners_sections_word_for_word():
    rules = propose_v2.proposal_rules_v2()
    for n in (1, 4, 7, 8, 9, 10):
        section = propose_v2.owner_section(n)
        assert section in rules and section.startswith(f"# {n}. ")
    assert propose.MANDATE not in rules  # the first decision's mandate is not reused
    assert "never switch a frozen experiment from t0-alpha to t0-beta" not in rules.lower()  # replaced by section 9
    sys_text = propose_v2.system_text_v2()
    assert sys_text.startswith(rules) and json.dumps(propose_v2.proposal_schema_v2(), indent=1) in sys_text


def test_the_owner_text_is_the_whole_clarification_between_markers():
    text = propose_v2.owner_text()
    assert text.startswith("# Owner clarification") and text.rstrip().endswith("evolving systems better over time.")
    assert [f"# {n}. " in text for n in range(1, 15)] == [True] * 14


# ------------------------------------------------------------------ the answer cannot execute anything


def test_the_schema_has_no_probe_or_freeze_path_and_is_closed():
    schema = propose_v2.proposal_schema_v2()
    assert not set(_keys(schema)) & {"probe", "claim_batch", "spec", "batch", "freeze"}
    assert schema["properties"]["action"]["enum"] == ["propose", "abstain"]
    d = schema["properties"]["D_decision"]["properties"]
    assert d["i1_disposition"]["enum"] == ["retained", "redesigned", "replaced", "abandoned"]

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


def test_a_valid_proposal_and_a_valid_abstention_pass():
    assert propose_v2.validate_proposal_v2(answer(), {"X1", "X2"}) == []
    assert propose_v2.validate_proposal_v2(answer("abstain", n=0), {"X1", "X2"}) == []
    # the dataset is required only when the public data cannot test the hypothesis (owner, section 7)
    no_dataset = answer("abstain", n=0, D_decision={**answer("abstain")["D_decision"],
                                                    "abstention": {"reason": "r", "smallest_new_benchmark_or_dataset": None}})
    assert propose_v2.validate_proposal_v2(no_dataset, {"X1", "X2"}) == []
    levels_null = answer(C_candidates=[{**_candidate("N1"), "historical_data_requirement": {
        "what_each_comparator_receives": "a", "how_levels_are_chosen_without_outcome_tuning": None}}])
    assert propose_v2.validate_proposal_v2(levels_null, {"X1", "X2"}) == []


def test_shape_errors_do_not_hide_citation_length_or_cap_errors():
    """A shape error must not hide citation, length or list-cap errors, and errors inside a nullable object are
    reported by field."""
    e = {f: {"value": "v", "status": "proposed", "evidence_ids": ["X1"]} for f in propose_v2.PROTOCOL_FIELDS}
    e["target"] = {"value": "v", "status": "not applicable", "evidence_ids": ["X1"]}
    bad = answer(E_protocol=e, summary="x" * 4001,
                 A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["NOPE"]}])
    errors = propose_v2.validate_proposal_v2(bad, {"X1", "X2"})
    joined = "\n".join(errors)
    assert "$.E_protocol.target.status" in joined and "not in the evidence" in joined and "longer than" in joined
    bad = answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["X1"]}] * 31, summary=None)
    joined = "\n".join(propose_v2.validate_proposal_v2(bad, {"X1", "X2"}))
    assert "at most 30" in joined and "expected string" in joined
    bad = answer(C_candidates=[{**_candidate("N1"), "regime_definition": {"boundary": "b"}}])
    joined = "\n".join(propose_v2.validate_proposal_v2(bad, {"X1", "X2"}))
    assert "regime_definition: missing field 'independent_information_used'" in joined


def test_a_shape_error_does_not_hide_consistency_errors():
    """The consistency checks run on the well-typed parts of an answer that also has a shape error, so one repair
    sees them all; a malformed answer never crashes the validator; an over-long list of errors says what it left out."""
    bad = answer()
    del bad["summary"]
    bad["D_decision"]["abstention"] = {"reason": "r", "smallest_new_benchmark_or_dataset": None}
    bad["A_learned"][0]["evidence_ids"] = []
    bad["section_4_consideration"]["regime_change"]["consideration"] = ""
    bad["C_candidates"] = [_candidate("N2")]
    joined = "\n".join(propose_v2.validate_proposal_v2(bad, {"X1", "X2"}))
    for why in ("missing field 'summary'", "in order", "not one of the candidates", "abstention to be null",
                "cites no evidence", "regime_change: empty"):
        assert why in joined, why
    for broken in (dict.fromkeys(answer(), None), dict.fromkeys(answer(), 1), {**answer(), "C_candidates": [1, None]},
                   {**answer("abstain", n=0), "D_decision": {"chosen": "none", "abstention": {"reason": 3}}}):
        assert propose_v2.validate_proposal_v2(broken, {"X1", "X2"})
    many = answer(A_learned=[{"finding": 1, "status": "nope", "evidence_ids": ["NOPE"]}] * 30)
    errors = propose_v2.validate_proposal_v2(many, {"X1", "X2"})
    assert len(errors) == propose_v2.MAX_ERRORS and errors[-1].startswith("... and ")


@pytest.mark.parametrize("bad, why", [
    (answer(n=4), "at most 3"),
    (answer(C_candidates=[_candidate("N2")]), "in order"),
    (answer(C_candidates=[_candidate("I1")]), "is not one of"),
    (answer(D_decision={**answer()["D_decision"], "chosen": "N3"}), "not one of the candidates"),
    (answer(E_protocol=None), "needs E_protocol"),
    (answer(D_decision={**answer()["D_decision"], "abstention": {"reason": "r",
                                                                 "smallest_new_benchmark_or_dataset": "b"}}),
     "abstention to be null"),
    (answer("abstain", n=0, D_decision={**answer("abstain")["D_decision"], "abstention": None}),
     "needs D_decision.abstention with a reason"),
    (answer("abstain", n=0, D_decision={**answer("abstain")["D_decision"],
                                        "abstention": {"reason": " ", "smallest_new_benchmark_or_dataset": None}}),
     "needs D_decision.abstention with a reason"),
    (answer("abstain", n=0, D_decision={**answer("abstain")["D_decision"],
                                        "abstention": {"reason": "r", "smallest_new_benchmark_or_dataset": " "}}),
     "give it, or null"),
    (answer(section_4_consideration={**_s4(), "regime_change": {"consideration": " ", "evidence_ids": []}}),
     "section_4_consideration.regime_change: empty"),
    (answer(section_4_consideration={k: v for k, v in _s4().items() if k != "regime_change"}), "missing field"),
    (answer("abstain", n=0, E_protocol={f: {"value": "v", "status": "proposed", "evidence_ids": []}
                                        for f in propose_v2.PROTOCOL_FIELDS}), "E_protocol to null"),
    (answer(D_decision={**answer()["D_decision"], "i1_disposition": "kept"}), "is not one of"),
    (answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["NOPE"]}]), "not in the evidence"),
    (answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": []}]), "cites no evidence"),
    (answer(summary="x" * 4001), "longer than"),
    (answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["X1"]}] * 31), "at most 30"),
    (answer(C_candidates=[{**_candidate("N1"), "possible_outcomes": []}]), "no possible outcome"),
    (answer(C_candidates=[{**_candidate("N1"), "why_it_matters_to_the_north_star":
                           {"components": [], "explanation": "e"}}]), "no North Star component"),
    (answer(C_candidates=[{**_candidate("N1"), "why_it_matters_to_the_north_star":
                           {"components": ["marketing"], "explanation": "e"}}]), "is not one of"),
    (answer(C_candidates=[{**_candidate("N1"), "probe": {}}]), "unexpected field"),
])
def test_invalid_proposals_are_refused(bad, why):
    errors = propose_v2.validate_proposal_v2(bad, {"X1", "X2"})
    assert errors and any(why in e for e in errors), errors


# ------------------------------------------------------------------ one decision, recorded in full


def test_a_valid_proposal_is_recorded_with_both_mandates_and_the_full_prompt():
    call = FakeCall(_resp(json.dumps(answer())))
    result, calls, recorded = _run(call)
    assert result["action"] == "propose" and len(recorded) == 1
    c = recorded[0]
    text, _, sha = _pack(_entries())
    system = propose_v2.system_text_v2()
    assert c["mandate_version"] == "v2" and c["mandate_sha256"] == hashlib.sha256(
        propose_v2.MANDATE_V2.encode()).hexdigest()
    assert c["previous_mandate_sha256"] == "beaeb415037078ddd5a8721df1adf0d3d32f621807f0c316e5bffb4339374754"
    assert c["previous_proposal_rules_sha256"] == "5cc6c4460586ac0d2594ff3efde585ba31048ab024ba6c4877f884dfb4ee412d"
    assert c["previous_system_sha256"] == "29b8b29b597a6b851947c8ab8a3a6bf5071d9f89392190f9dd86d9e6dd32fc04"
    assert c["previous_call"] == {"seq": 74, "run_id": "36855466970", "mandate_version": "v1"}
    assert c["system_text"] == system and c["system_sha256"] == hashlib.sha256(system.encode()).hexdigest()
    assert c["user_prompt"] == propose.user_prompt(text, sha) and c["evidence_pack_sha256"] == sha
    assert c["schema_sha256"] == propose_v2.schema_sha256_v2() and c["max_tokens"] == 128000
    assert c["served_model"] == "served-model" and c["response_text"] and c["action"] == "propose"
    assert call.requests[0]["system"] == system


def test_the_repair_returns_the_replys_own_content_blocks_then_only_the_validators_text():
    bad = answer(A_learned=[{"finding": "f", "status": "exploratory", "evidence_ids": ["NOPE"]}])
    first = _resp(json.dumps(bad))
    call = FakeCall(first, _resp(json.dumps(answer())))
    result, _, recorded = _run(call)
    assert result["action"] == "propose" and len(recorded) == 2 and "invalid" in recorded[0]
    repair = call.requests[1]["messages"]
    assert [m["role"] for m in repair] == ["user", "assistant", "user"]
    assert repair[1]["content"] is first.content  # thinking block included, unchanged
    assert repair[2]["content"].startswith("The answer failed these checks:") and "NOPE" in repair[2]["content"]


def test_a_second_invalid_answer_is_an_error_and_both_calls_are_recorded():
    bad = json.dumps(answer(n=4))
    result, _, recorded = _run(FakeCall(_resp(bad), _resp(bad)))
    assert result["action"] == "error" and len(recorded) == 2 and all("invalid" in r for r in recorded)


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_a_refusal_or_truncation_is_recorded_and_ends_the_call(stop):
    result, _, recorded = _run(FakeCall(_resp("{}", stop=stop)))
    assert result == {"action": "error", "error": stop} and len(recorded) == 1


def test_a_transient_error_is_retried_and_every_attempt_recorded():
    err = type("APIConnectionError", (Exception,), {})("dropped")
    result, _, recorded = _run(FakeCall(err, _resp(json.dumps(answer()))))
    assert result["action"] == "propose" and len(recorded) == 2 and recorded[0]["transient"] is True
    assert "response_text" not in recorded[0]


def test_a_stream_error_event_is_retried_as_transient():
    err = type("APIStatusError", (Exception,), {})("overloaded")
    err.status_code, err.body = 200, {"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
    result, _, recorded = _run(FakeCall(err, _resp(json.dumps(answer()))))
    assert result["action"] == "propose" and len(recorded) == 2 and recorded[0]["transient"] is True


def _with_v2_call(response_text):
    entries = _entries()
    payload = {"purpose": "proposal", "mandate_version": "v2", "response_text": response_text}
    return entries + ledger.chain(entries, [ledger.pending("research_call", payload, dict(CTX, mode="propose"))])


def test_an_answered_mandate_is_refused_before_any_call():
    entries = _with_v2_call('{"action": "propose"}')
    call = FakeCall()
    with pytest.raises(SystemExit, match="already answered"):
        _run(call, entries=entries, pack=_pack(entries))
    assert call.requests == []


def test_a_call_with_no_response_text_does_not_count_as_answered():
    assert propose_v2.answered(_with_v2_call("")) == []
    assert propose_v2.answered(_with_v2_call("{}")) != []


def test_the_first_decisions_calls_do_not_count_as_v2_answers():
    entries = _entries()
    v1_call = {"purpose": "proposal", "response_text": "{...}", "action": "propose"}  # seq 74 has no mandate_version
    entries = entries + ledger.chain(entries, [ledger.pending("research_call", v1_call, dict(CTX, mode="propose"))])
    assert propose_v2.answered(entries) == []


def test_a_pack_built_against_another_ledger_head_is_refused_before_any_call():
    entries = _entries()
    text, pack, sha = _pack(entries)
    pack["built_from"]["ledger"]["head_seq"] = 999
    call = FakeCall()
    with pytest.raises(SystemExit, match="rebuild the pack"):
        _run(call, entries=entries, pack=(text, pack, sha))
    assert call.requests == []


def test_main_refuses_an_answered_mandate_before_any_output(tmp_path, monkeypatch):
    entries = _with_v2_call("{}")
    led = tmp_path / "ledger.jsonl"
    led.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    (tmp_path / "a.md").write_text("one", encoding="utf-8")
    _, pack_obj, _ = _pack(entries)
    pack_obj["built_from"]["repo_files_sha256"] = {"a.md": hashlib.sha256(b"one").hexdigest()}
    text = json.dumps(pack_obj, sort_keys=True)
    pack = tmp_path / "pack.json"
    pack.write_text(text, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RESEARCHER_MODEL", "model-x")
    monkeypatch.setenv("EVIDENCE_SHA256", hashlib.sha256(text.encode()).hexdigest())
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match="already answered"):
        propose_v2.main(["--ledger", str(led), "--pack", str(pack), "--out", str(out)])
    assert not out.exists()


def test_the_module_imports_without_the_forecasting_stack():
    """The research job installs only the API client: the module must not need pandas or numpy."""
    code = ("import sys\n"
            "class Block:\n"
            "    def find_spec(self, name, path=None, target=None):\n"
            "        if name.split('.')[0] in ('pandas', 'numpy', 'torch'):\n"
            "            raise ImportError('blocked: ' + name)\n"
            "sys.meta_path.insert(0, Block())\n"
            "import engine.propose_v2 as m\n"
            "assert m.system_text_v2()\n")
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True)


# ------------------------------------------------------------------ the committed v2 pack


def test_the_committed_v2_pack_is_well_formed():
    path = ROOT / "docs" / "experiment_5" / "evidence_pack_v2.json"
    if not path.exists():
        pytest.skip("the v2 pack is built in a later step")
    pack = json.loads(path.read_text(encoding="utf-8"))
    ids = [r["id"] for r in pack["records"]]
    assert ids == pack["record_ids"] and len(ids) == len(set(ids))
    assert not set(ids) & set(propose_v2.CANDIDATE_IDS)
    for r in pack["records"]:
        assert r["evidence_grade"] in pack["evidence_grades"] and r["verification"] in pack["verification_labels"]
    text = path.read_text(encoding="utf-8").lower()
    for word in ("claude-opus", "claude-sonnet", "claude-haiku", "claude-fable", "served_model", "requested_model"):
        assert word not in text


def test_the_rendering_covers_every_field_of_the_answer():
    """``render_researcher_docs_v2`` renders each top-level field of the answer, in the schema's order."""
    sys.path.insert(0, str(ROOT / "docs" / "experiment_5"))
    import render_researcher_docs_v2 as render
    assert list(render.TITLES) == list(propose_v2.proposal_schema_v2()["properties"])
    text = render.render_proposal_v2(answer())
    positions = [text.index(f"### {title}\n") for title in render.TITLES.values()]
    assert positions == sorted(positions)
    with pytest.raises(SystemExit):
        render.render_proposal_v2({**answer(), "unexpected": 1})
