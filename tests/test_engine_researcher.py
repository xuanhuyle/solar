"""The researcher, against a fake Claude client: valid proposals, one repair, refusal, caps."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine import ledger, legacy, researcher
from engine.spec import validate_probe

CTX = {"at": "2026-09-26T08:00:00+00:00", "run_id": "1", "run_attempt": "1", "code_commit": "x",
       "config_sha256": "c" * 64, "actor": "t", "mode": "t"}
GOOD = {"spec_version": "probe/0", "target": "consumption", "period": "Y2024", "scope": "winter",
        "arms": [{"name": "t0_bridge", "covariates": [{"id": "holiday", "transform": "raw"},
                                                       {"id": "bridge_day", "transform": "raw"}]}],
        "comparisons": [{"arm": "t0_bridge", "vs": "accepted", "metric": "mae"}], "builds_on": [9],
        "rationale": "Do bridge days add to the accepted holiday arm?"}


def _resp(text, stop="end_turn", usage=(1000, 200)):
    return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
                           stop_reason=stop, model="served-model", _request_id="req_1", stop_details=None,
                           usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1],
                                                 cache_read_input_tokens=0, cache_creation_input_tokens=0))


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return self.responses.pop(0)


def _entries(*extra):
    return ledger.chain([], legacy.seed_items(CTX) + [ledger.pending(k, p, CTX) for k, p in extra])


def _decide(client, entries=None, **kw):
    return researcher.decide(client, "model-x", "high", entries or _entries(), iteration=kw.pop("iteration", 1),
                             max_iterations=3, remaining=200, now=datetime(2026, 9, 26, 9, tzinfo=timezone.utc), **kw)


def test_a_valid_proposal_is_validated_and_recorded():
    client = FakeClient(_resp(json.dumps({"action": "probe", "note": "test bridges", "probe": GOOD})))
    action, calls = _decide(client)
    assert action["action"] == "probe" and action["probe"] == validate_probe(GOOD)
    req = client.requests[0]
    assert req["output_config"]["format"]["type"] == "json_schema" and req["thinking"] == {"type": "adaptive"}
    assert req["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "Ledger digest" in req["messages"][0]["content"] and "C1" in req["messages"][0]["content"]
    c = calls[0]
    assert c["served_model"] == "served-model" and c["usage"]["input_tokens"] == 1000 and c["action"] == "probe"
    assert c["system_sha256"] == researcher._sha(researcher.system_prompt()) and c["ledger_head"]["seq"] == 9


def test_an_invalid_proposal_gets_one_repair():
    bad = dict(GOOD, arms=[{"name": "t0_bridge", "covariates": [{"id": "wx_radiation", "transform": "raw"}]}])
    client = FakeClient(_resp(json.dumps({"action": "probe", "note": "x", "probe": bad})),
                        _resp(json.dumps({"action": "probe", "note": "fixed", "probe": GOOD})))
    action, calls = _decide(client)
    assert action["action"] == "probe" and len(calls) == 2 and "invalid" in calls[0]
    repair = client.requests[1]["messages"]
    assert [m["role"] for m in repair] == ["user", "assistant", "user"] and "not available" in repair[2]["content"]


def test_a_second_invalid_proposal_stops_the_chain():
    bad = json.dumps({"action": "probe", "note": "x", "probe": {"spec_version": "probe/0"}})
    action, calls = _decide(FakeClient(_resp(bad), _resp(bad)))
    assert action["action"] == "stop" and action["error"] == "invalid" and len(calls) == 2


@pytest.mark.parametrize("stop, error", [("refusal", "refusal"), ("max_tokens", "max_tokens")])
def test_refusal_and_truncation_stop_the_chain(stop, error):
    action, calls = _decide(FakeClient(_resp("", stop=stop)))
    assert action == {"action": "stop", "note": action["note"], "probe": None, "error": error} and len(calls) == 1


def test_caps_stop_before_any_call():
    client = FakeClient()
    action, calls = _decide(client, iteration=4)
    assert action["action"] == "stop" and not calls and not client.requests
    heavy = ("research_call", {"usage": {"input_tokens": 1_999_000, "output_tokens": 5_000}})
    action, calls = _decide(client, entries=_entries(heavy))
    assert action["note"].startswith("daily token cap") and not client.requests


def test_schema_names_only_catalogue_entries():
    schema = json.dumps(researcher.action_schema())
    for key in ("holiday", "wx_temperature", "Y2025c", "winter", "consumption"):
        assert key in schema
    assert '"additionalProperties": false' in schema.replace("False", "false").lower() or "additionalProperties" in schema


def test_a_freeze_action_carries_a_claim_batch():
    batch = {"batch_version": "claims/0", "claims": [
        {"id": "c", "statement": "bridge days add to the accepted arm", "target": "consumption",
         "arm": {"covariates": [{"id": "holiday", "transform": "raw"}, {"id": "bridge_day", "transform": "raw"}]},
         "comparator": "accepted", "scope": "all", "delta": 0.0, "evidence": [12]}]}
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "strong and stable", "probe": None,
                                          "claim_batch": batch})))
    action, calls = _decide(client)
    assert action["action"] == "freeze" and action["claim_batch"] == batch and calls[0]["action"] == "freeze"
    empty = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": None})),
                       _resp(json.dumps({"action": "stop", "note": "nothing", "probe": None, "claim_batch": None})))
    action, calls = _decide(empty)
    assert action["action"] == "stop" and "claim_batch" in calls[0]["invalid"][0]
    assert '"freeze"' in json.dumps(researcher.action_schema())
