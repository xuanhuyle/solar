"""The AI researcher of the beta1 run (NEXT_MILESTONE_PROMPT.md sections 4-8).

Phase 0's researcher unchanged in everything that shapes the research (``phase0/lab/researcher.py``: prompts as a pure
function of the record, code checks with one repair turn per call, the 6-experiment budget with at most 3 per round,
the 80k token cap, the model pinned by hash and the effort from ``phase0/lab/menu.json``), with two differences:

- the system text is ``beta1/lab/brief.md`` (Phase 0's brief plus one general evidence rule) and the same schema;
- every API attempt also records the refusal details (``stop_details``: type, category, explanation), the elapsed
  time, the requested and served model's sha256 (never the identifier) and whether they match, and the repair and
  retry numbers.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

from research_loop_proof.phase0.lab import researcher as base
from research_loop_proof.phase0.lab.researcher import (MAX_TOKENS, MAX_TRANSIENT_RETRIES, MIN_CALL_TOKENS, RESEARCHER,
                                                       TOKEN_CAP, IntegrityError, _now, _retry_after, _storable,
                                                       _text, _usage, model_allowed, redact, response_schema,
                                                       sha256_text, tokens_of, transient)

HERE = Path(__file__).resolve().parent
BRIEF = (HERE / "brief.md").read_text(encoding="utf-8")


def system_text() -> str:
    return BRIEF.rstrip("\n") + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema(), indent=1) + "\n"


def stop_details(resp) -> dict | None:
    """The refusal details the API returned (``RefusalStopDetails``), as plain data."""
    d = getattr(resp, "stop_details", None)
    if d is None:
        return None
    explanation = getattr(d, "explanation", None)
    return {"type": getattr(d, "type", None), "category": getattr(d, "category", None),
            "explanation": _storable(explanation) if isinstance(explanation, str) else None}


class Researcher(base.Researcher):
    def __init__(self, client, model: str, lab, *, emit=None, sleep=time.sleep, clock=time.monotonic):
        super().__init__(client, model, lab, emit=emit, sleep=sleep)
        self.system = system_text()
        self.clock = clock

    def _attempt(self, step: dict, messages: list[dict], attempt: int) -> dict:
        prompt_chars = len(self.system) + sum(len(m["content"]) if isinstance(m["content"], str) else
                                              sum(len(b.get("text", "")) for b in m["content"]) for m in messages)
        room = TOKEN_CAP - self.tokens - math.ceil(prompt_chars / 2)  # 2 characters per token: conservative
        max_tokens = min(MAX_TOKENS, room)
        record = {"call": step["call"], "attempt": attempt, "repair": attempt - 1, "started_at": _now(),
                  "max_tokens": max_tokens, "effort": RESEARCHER["effort"],
                  "requested_model_sha256": sha256_text(self.model)}
        if max_tokens < MIN_CALL_TOKENS:
            record.update(skipped="token cap: not enough room left for a call", tokens_used=self.tokens)
            self.emit({"event": "attempt", **record})
            return record
        retry = 0
        while True:
            started = self.clock()
            try:
                resp = self._create(messages, max_tokens)
                break
            except Exception as exc:  # recorded: a failed call may still have been billed
                fail = dict(record, retry=retry, error=redact(f"{type(exc).__name__}: {exc}", self.model)[:1000],
                            finished_at=_now(), elapsed_s=round(self.clock() - started, 3), transient=transient(exc),
                            status_code=getattr(exc, "status_code", None),
                            request_id=getattr(exc, "request_id", None))
                self.emit({"event": "api_error", **fail})
                if transient(exc) and retry < MAX_TRANSIENT_RETRIES:
                    self.sleep(min(60.0, _retry_after(exc) or min(30.0, 2.0 * 2 ** retry)))
                    retry += 1
                    continue
                raise IntegrityError(f"API outage: {type(exc).__name__}") from exc
        elapsed = round(self.clock() - started, 3)
        usage = _usage(resp)
        self.tokens += tokens_of(usage)
        served = getattr(resp, "model", None) or ""
        details = stop_details(resp)
        record.update(retry=retry, finished_at=_now(), elapsed_s=elapsed, served_model_sha256=sha256_text(served),
                      served_matches_requested=served == self.model,
                      request_id=getattr(resp, "_request_id", None), stop_reason=getattr(resp, "stop_reason", None),
                      stop_details=details, refusal_category=details["category"] if details else None,
                      usage=usage, tokens_used=self.tokens, response_text=_storable(_text(resp)))
        if not model_allowed(served):
            self.emit({"event": "attempt", **record, "integrity": "served model hash mismatch"})
            raise IntegrityError("the served model is not the pinned model")
        return record


rebuild_mismatches = base.rebuild_mismatches  # user and repair prompts do not depend on the brief
call_plan = base.call_plan
