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


ARM2 = [{"id": "holiday", "transform": "raw"}, {"id": "bridge_day", "transform": "raw"}]


def _evidence(accepted_arm=None, **over):
    from engine.findings import latest_accepted

    p = {"probe_sha256": "p", "status": "EXPLORATORY - x", "target": "consumption", "scope": "all",
         "leak_checks_passed": True, "limit_days": None,
         "accepted_arm": accepted_arm if accepted_arm is not None else latest_accepted(_entries(), "consumption")["arm"],
         "spec": {"arms": [{"name": "t0_bridge", "covariates": ARM2}]},
         "comparisons": [{"arm": "t0_bridge", "vs": "accepted", "skill": 0.02}]}
    p.update(over)
    entries = _entries(("probe_result", p))
    return entries, entries[-1]["seq"]


def _freeze(seq, **over):
    claim = {"id": "c", "statement": "bridge days add to the accepted arm", "target": "consumption",
             "arm": {"covariates": ARM2}, "comparator": "accepted", "scope": "all", "delta": 0.0, "evidence": [seq]}
    claim.update(over)
    return {"batch_version": "claims/0", "claims": [claim]}


def test_a_freeze_action_carries_a_claim_batch():
    entries, seq = _evidence()
    batch = _freeze(seq)
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "strong and stable", "probe": None,
                                          "claim_batch": batch})))
    action, calls = _decide(client, entries=entries)
    assert action["action"] == "freeze" and action["claim_batch"] == batch and calls[0]["action"] == "freeze"
    empty = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": None})),
                       _resp(json.dumps({"action": "stop", "note": "nothing", "probe": None, "claim_batch": None})))
    action, calls = _decide(empty)
    assert action["action"] == "stop" and "claim_batch" in calls[0]["invalid"][0]
    assert '"freeze"' in json.dumps(researcher.action_schema())


@pytest.mark.parametrize("over, reason", [
    ({"accepted_arm": {"covariates": []}}, "measured against another accepted arm"),
    ({"leak_checks_passed": None}, "leak checks did not pass"),
    ({"limit_days": 12}, "a smoke run"),
])
def test_a_freeze_citing_inadmissible_evidence_gets_its_repair(over, reason):
    """Fix-check: the vault's ledger checks run in the researcher job too, so the model can correct a citation."""
    entries, seq = _evidence(**over)
    bad = _freeze(seq)
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": bad})),
                        _resp(json.dumps({"action": "stop", "note": "ok", "probe": None, "claim_batch": None})))
    action, calls = _decide(client, entries=entries)
    assert action["action"] == "stop" and reason in " ".join(calls[0]["invalid"])
    assert reason in client.requests[1]["messages"][2]["content"]


def test_a_freeze_of_the_accepted_arm_or_a_locked_covariate_is_repaired():
    entries, seq = _evidence()
    same = _freeze(seq, arm={"covariates": [{"id": "holiday", "transform": "raw"}]})
    locked = _freeze(seq, arm={"covariates": [{"id": "wx_temperature", "transform": "hdd15"}]}, comparator="t0_base")
    for bad, reason in ((same, "cannot beat itself"), (locked, "no passed known-answer gate")):
        client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": bad})),
                            _resp(json.dumps({"action": "stop", "note": "ok", "probe": None, "claim_batch": None})))
        action, calls = _decide(client, entries=entries)
        assert reason in " ".join(calls[0]["invalid"]), reason


def test_a_probe_against_a_missing_accepted_finding_is_repaired():
    solar = dict(GOOD, target="solar", scope="all", arms=[{"name": "t0_h", "covariates": [{"id": "holiday", "transform": "raw"}]}],
                 comparisons=[{"arm": "t0_h", "vs": "accepted", "metric": "mae"}])
    client = FakeClient(_resp(json.dumps({"action": "probe", "note": "x", "probe": solar, "claim_batch": None})),
                        _resp(json.dumps({"action": "probe", "note": "fixed", "probe": GOOD, "claim_batch": None})))
    action, calls = _decide(client)
    assert action["probe"]["target"] == "consumption" and "no accepted finding for solar" in calls[0]["invalid"][0]


def test_iteration_must_be_at_least_one():
    for bad in (0, -1):
        with pytest.raises(ValueError, match=">= 1"):
            _decide(FakeClient(), iteration=bad)
    with pytest.raises(SystemExit):
        researcher.main(["--ledger", "x", "--out", "y", "--iteration", "0"])


def test_each_call_is_recorded_as_it_returns_with_full_prompt_and_response():
    long_note = "n" * 30_000
    client = FakeClient(_resp(json.dumps({"action": "stop", "note": long_note, "probe": None, "claim_batch": None})))
    seen = []
    action, calls = _decide(client, on_call=seen.append)
    assert seen == calls and len(seen[0]["response_text"]) > 30_000  # never truncated
    assert seen[0]["user_prompt"] == client.requests[0]["messages"][0]["content"]
    assert seen[0]["user_sha256"] == researcher._sha(seen[0]["user_prompt"]) and seen[0]["repair_prompt"] is None


def test_a_call_that_raises_is_recorded_before_the_error_propagates():
    class Boom(FakeClient):
        def _create(self, **kwargs):
            self.requests.append(kwargs)
            if len(self.requests) == 2:
                raise RuntimeError("connection reset")
            return _resp(json.dumps({"action": "probe", "note": "x", "probe": {"spec_version": "probe/0"}}))

    seen = []
    with pytest.raises(RuntimeError):
        _decide(Boom(), on_call=seen.append)
    assert [s["attempt"] for s in seen] == [1, 2] and "invalid" in seen[0] and "connection reset" in seen[1]["error"]
    assert seen[1]["repair_prompt"].startswith("The referee rejected")


def test_main_keeps_the_record_when_the_api_fails(tmp_path, monkeypatch):
    import types

    path = tmp_path / "ledger.jsonl"
    ledger.append(path, [ledger.pending(k["kind"], k["payload"], k["context"]) for k in legacy.seed_items(CTX)])

    class Anthropic(FakeClient):
        def __init__(self, **kwargs):
            seen_kwargs.update(kwargs)
            super().__init__(_resp("not json"))

        def _create(self, **kwargs):
            if self.requests:
                raise RuntimeError("overloaded")
            return super()._create(**kwargs)

    seen_kwargs: dict = {}
    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(Anthropic=Anthropic))
    monkeypatch.setenv("RESEARCHER_MODEL", "model-x")
    out = tmp_path / "out"
    assert researcher.main(["--ledger", str(path), "--out", str(out)]) == 1
    recorded = ledger.read_pending(out / "pending_research.jsonl")
    assert [r["kind"] for r in recorded] == ["research_call", "research_call"]
    assert "invalid" in recorded[0]["payload"] and "overloaded" in recorded[1]["payload"]["error"]
    assert json.loads((out / "action.json").read_text())["error"].startswith("RuntimeError")
    # a hard per-call timeout and no hidden SDK retries: every attempt is one recorded research_call
    assert seen_kwargs == {"timeout": researcher.CALL_TIMEOUT_S, "max_retries": 0} and 2 * researcher.CALL_TIMEOUT_S < 20 * 60


def test_a_malformed_freeze_gets_the_vaults_structural_check_and_one_repair():
    entries, seq = _evidence()
    claim = _freeze(seq)["claims"][0]
    two_targets = {"batch_version": "claims/0", "claims": [claim, dict(claim, target="solar")]}
    good = {"batch_version": "claims/0", "claims": [claim]}
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": two_targets})),
                        _resp(json.dumps({"action": "freeze", "note": "y", "probe": None, "claim_batch": good})))
    action, calls = _decide(client, entries=entries)
    assert action["action"] == "freeze" and "one target per batch" in " ".join(calls[0]["invalid"])
    assert "one target per batch" in client.requests[1]["messages"][2]["content"]


def test_the_brief_states_the_window_and_the_margin_rule():
    text = researcher.system_prompt()
    assert "168 days" in text and "12 blocks of 14" in text and "at least 0.10 below" in text and "84 days" not in text



class _Transient(Exception):
    def __init__(self, status):
        super().__init__(f"status {status}")
        self.status_code = status


class APITimeoutError(Exception):  # named like the SDK's class: a timeout is never retried
    pass


class _Flaky(FakeClient):
    def __init__(self, errors, *responses):
        super().__init__(*responses)
        self.errors = list(errors)

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        if self.errors:
            raise self.errors.pop(0)
        return self.responses.pop(0)


def test_transient_api_errors_are_retried_and_each_attempt_recorded():
    naps = []
    ok = _resp(json.dumps({"action": "stop", "note": "done", "probe": None, "claim_batch": None}))
    client = _Flaky([_Transient(529), _Transient(429)], ok)
    seen = []
    action, calls = _decide(client, on_call=seen.append, sleep=naps.append, clock=lambda: 0.0)
    assert action["action"] == "stop" and [c.get("retry") for c in seen] == [0, 1, 2] and len(naps) == 2
    assert seen[0]["transient"] and "529" in seen[0]["error"] and seen[2]["served_model"] == "served-model"


@pytest.mark.parametrize("exc", [_Transient(400), APITimeoutError("timed out")])
def test_other_errors_and_timeouts_are_not_retried(exc):
    seen = []
    with pytest.raises(type(exc)):
        _decide(_Flaky([exc]), on_call=seen.append, sleep=lambda s: pytest.fail("slept"), clock=lambda: 0.0)
    assert len(seen) == 1 and not seen[0]["transient"]


def test_retries_stop_when_the_job_budget_is_used_up():
    seen = []
    with pytest.raises(_Transient):
        ticks = iter([0.0, researcher.JOB_BUDGET_S - 60.0])  # started at 0; the first failure comes late
        _decide(_Flaky([_Transient(503), _Transient(503)]), on_call=seen.append, sleep=lambda s: None,
                clock=lambda: next(ticks))
    assert len(seen) == 1


def test_an_unexpected_validation_error_still_records_the_billed_call(monkeypatch):
    from engine import claims

    entries, seq = _evidence()
    monkeypatch.setattr(claims, "ledger_errors", lambda *a, **k: (_ for _ in ()).throw(OSError("disk")))
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": _freeze(seq)})))
    seen = []
    with pytest.raises(OSError):
        _decide(client, entries=entries, on_call=seen.append)
    assert len(seen) == 1 and seen[0]["usage"]["input_tokens"] == 1000 and "OSError" in seen[0]["invalid"][0]


def test_a_response_with_a_lone_surrogate_is_recorded_safely_and_repaired():
    bad = '{"action": "stop", "note": "\\ud800", "probe": null, "claim_batch": null}'
    ok = _resp(json.dumps({"action": "stop", "note": "fine", "probe": None, "claim_batch": None}))
    seen = []
    action, calls = _decide(FakeClient(_resp(bad), ok), on_call=seen.append)
    assert action["note"] == "fine" and "invalid" in seen[0]
    for rec in seen:
        json.dumps(rec, ensure_ascii=False).encode("utf-8")  # storable


def test_the_brief_and_digest_say_what_accepted_means_and_freezes_respect_open_batches():
    assert "accepted_now" in researcher.system_prompt() and "claim C1" not in researcher.RULES
    d = ledger.digest(_entries())
    assert d["accepted_now"]["consumption"]["finding_id"] == "C1" and d["accepted_now"]["solar"] is None
    entries, seq = _evidence()
    open_ = entries + ledger.chain(entries, [ledger.pending("freeze", {"batch_id": "B1", "window": ["a", "b"]}, CTX)])
    client = FakeClient(_resp(json.dumps({"action": "freeze", "note": "x", "probe": None, "claim_batch": _freeze(seq)})),
                        _resp(json.dumps({"action": "stop", "note": "ok", "probe": None, "claim_batch": None})))
    action, calls = _decide(client, entries=open_)
    assert "still open" in calls[0]["invalid"][0]
