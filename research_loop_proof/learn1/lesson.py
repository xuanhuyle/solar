"""The one retrospective lesson-distillation call of learn1 (NEXT_LEARNING_MILESTONE_PROMPT.md section 3).

Before the next hidden world exists, one call converts the beta1 failure into one compact, portable research lesson.
Its input is built in code from the beta1 scored record only (``beta1/run-37201189113``, ``ai.json`` pinned by sha256):
- the beta1 notebook as the researcher saw it, all four calls rendered by Phase 0's ``render_call`` (the last entry is
  the final call, with the final selection and the conclusion);
- the owner's evaluator feedback, verbatim (``FEEDBACK``).
Nothing about the next world is given: its seed hashes the frozen lesson, so it cannot exist yet. The system text is
the owner's section 3 output requirements, restated. The call uses the pinned researcher model and effort
(``phase0/lab/menu.json``, the model checked by the sha256 of its id, never written) with a one-field JSON schema and
beta1's attempt record (refusal details, usage, request id, model hashes, elapsed time). The lesson is checked in code
(non-empty, at most 1,000 characters, no candidate id, no numeral); one repair turn is allowed for an operational or a
check failure. Without a valid lesson after it, the record says LESSON DISTILLATION FAILURE.

Outputs: ``lesson.json`` (the lesson exactly as returned, its sha256 and provenance; only when valid),
``lesson_record.json`` (the exact system text and user prompt and every attempt), ``verdict.json`` and ``REPORT.md``.

    python -m research_loop_proof.learn1.lesson --beta1 DIR --out DIR      # the API key only here
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

from research_loop_proof.beta1.lab.researcher import stop_details
from research_loop_proof.phase0.lab.researcher import (MAX_TRANSIENT_RETRIES, RESEARCHER, IntegrityError, _now,
                                                       _retry_after, _storable, _text, _usage, model_allowed, redact,
                                                       render_call, sha256_text, transient)

BETA1_RUN = "37201189113"
BETA1_AI_SHA256 = "901658e89c57506ace63149eae941860f95d5df33c6f5385c4c2deef04a81b39"
FEEDBACK = ("The process changed. A candidate rejected on pre-change evidence became strongly predictive after the "
            "change. The researcher detected deterioration in the previously useful relationship but did not re-test "
            "candidates rejected under the earlier regime, so it missed the emerging signal.")
MAX_CHARS = 1000
MAX_TOKENS = 16000
FAILURE = "LESSON DISTILLATION FAILURE"
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["lesson"],
          "properties": {"lesson": {"type": "string"}}}

SYSTEM = """You help an empirical research programme learn from its own completed investigations. You will receive the full research notebook of one completed investigation by an AI research agent (each round's notes, beliefs, experiment requests and results, then its final selection and conclusion) and the evaluator's feedback, written after the hidden truth was revealed.

This is not a request for a research proposal or a plan. Your sole job is to convert this failed investigation into one compact, portable research lesson that a researcher could carry into a different, future problem.

The lesson must:
- be a single research lesson of at most 1,000 characters;
- state a general empirical-research principle, not an instruction specific to this benchmark;
- capture, in your own words, the distinction between evidence that a relationship was unhelpful under one regime and evidence that it will remain unhelpful after the system changes.
It may recommend how experiment budgets should respond when previously established relationships deteriorate.

It must not contain:
- candidate identifiers;
- specific days, or any numerals at all;
- assumptions about the structure or the answer of any future problem;
- a fixed sequence of experiments.

Return one JSON object with a single field, "lesson", holding the lesson text.
"""

_ID = re.compile(r"\bX\d+\b", re.IGNORECASE)
_DIGIT = re.compile(r"\d")


def notebook(ai: dict) -> str:
    """The beta1 notebook as the researcher saw it, all four calls (the last one is the final call)."""
    return "\n\n".join(render_call(c) for c in ai["calls"])


def user_prompt(ai: dict) -> str:
    return ("COMPLETED INVESTIGATION: RESEARCH NOTEBOOK (oldest first; the last entry is the final call, with the final "
            "selection and the conclusion)\n\n" + notebook(ai)
            + "\n\nEVALUATOR FEEDBACK (written after the hidden truth was revealed)\n" + FEEDBACK
            + "\n\nReturn the JSON object.")


def repair_prompt(errors: list[str]) -> str:
    return ("That response was not accepted:\n- " + "\n- ".join(errors)
            + "\nReturn a corrected JSON object with the single field \"lesson\".")


def lesson_errors(obj) -> list[str]:
    """Why a parsed response is not a valid lesson (empty when it is)."""
    if not isinstance(obj, dict) or set(obj) != {"lesson"}:
        return ["the response must be a JSON object with exactly the field \"lesson\""]
    text = obj["lesson"]
    if not isinstance(text, str) or not text.strip():
        return ["the lesson must be a non-empty string"]
    errs = []
    if len(text) > MAX_CHARS:
        errs.append(f"the lesson has {len(text)} characters; at most {MAX_CHARS} are allowed")
    if _ID.search(text):
        errs.append("the lesson must not contain candidate identifiers")
    if _DIGIT.search(text):
        errs.append("the lesson must not contain numerals (no specific days, counts or identifiers)")
    return errs


def attempt_errors(text: str, stop_reason: str | None) -> tuple[list[str], str | None]:
    if stop_reason == "refusal":
        return ["the response was a refusal"], None
    if stop_reason == "max_tokens":
        return ["the response was cut off at the output limit"], None
    try:
        obj = json.loads(text)
    except ValueError as exc:
        return [f"the response is not valid JSON ({exc})"], None
    errs = lesson_errors(obj)
    return errs, (None if errs else obj["lesson"])


class Distiller:
    """The lesson call with one repair turn, every attempt recorded (beta1's attempt record)."""

    def __init__(self, client, model: str, *, sleep=time.sleep, clock=time.monotonic):
        if not model_allowed(model):
            raise IntegrityError("the model is not the researcher model pinned in menu.json (sha256 mismatch)")
        self.client, self.model, self.sleep, self.clock = client, model, sleep, clock

    def _create(self, messages: list[dict]):
        return self.client.messages.create(
            model=self.model, max_tokens=MAX_TOKENS, thinking={"type": "adaptive"},
            output_config={"effort": RESEARCHER["effort"], "format": {"type": "json_schema", "schema": SCHEMA}},
            system=[{"type": "text", "text": SYSTEM}], messages=messages)

    def _attempt(self, messages: list[dict], attempt: int) -> dict:
        record = {"attempt": attempt, "repair": attempt - 1, "started_at": _now(), "max_tokens": MAX_TOKENS,
                  "effort": RESEARCHER["effort"], "requested_model_sha256": sha256_text(self.model), "api_errors": []}
        retry = 0
        while True:
            started = self.clock()
            try:
                resp = self._create(messages)
                break
            except Exception as exc:  # recorded: a failed call may still have been billed
                record["api_errors"].append({
                    "retry": retry, "error": redact(f"{type(exc).__name__}: {exc}", self.model)[:1000],
                    "elapsed_s": round(self.clock() - started, 3), "transient": transient(exc),
                    "status_code": getattr(exc, "status_code", None), "request_id": getattr(exc, "request_id", None)})
                if transient(exc) and retry < MAX_TRANSIENT_RETRIES:
                    self.sleep(min(60.0, _retry_after(exc) or min(30.0, 2.0 * 2 ** retry)))
                    retry += 1
                    continue
                record.update(retry=retry, finished_at=_now(), errors=["the API call failed"], response_text=None,
                              stop_reason=None)
                return record
        served = getattr(resp, "model", None) or ""
        details = stop_details(resp)
        record.update(retry=retry, finished_at=_now(), elapsed_s=round(self.clock() - started, 3),
                      served_model_sha256=sha256_text(served), served_matches_requested=served == self.model,
                      request_id=getattr(resp, "_request_id", None), stop_reason=getattr(resp, "stop_reason", None),
                      stop_details=details, refusal_category=details["category"] if details else None,
                      usage=_usage(resp), response_text=_storable(_text(resp)))
        if not model_allowed(served):
            raise IntegrityError("the served model is not the pinned model")
        return record

    def run(self, user: str) -> dict:
        messages = [{"role": "user", "content": user}]
        rec = {"system_text": SYSTEM, "system_sha256": sha256_text(SYSTEM), "user_prompt": user,
               "user_prompt_sha256": sha256_text(user), "attempts": [], "lesson": None, "lesson_sha256": None,
               "status": FAILURE, "errors": []}
        self.rec = rec  # kept if an integrity failure interrupts the call
        for attempt in (1, 2):
            a = self._attempt(messages, attempt)
            if attempt == 2:
                a["messages"] = messages[1:]  # the repair turn as sent (empty when the first attempt never answered)
            rec["attempts"].append(a)
            if a.get("response_text") is None:
                rec["errors"] = a["errors"]
                continue  # nothing to repair: the second attempt resends the same request
            errs, lesson = attempt_errors(a["response_text"], a["stop_reason"])
            a["errors"] = errs
            if lesson is not None:
                rec.update(lesson=lesson, lesson_sha256=sha256_text(lesson), status="OK", errors=[])
                break
            rec["errors"] = errs
            if attempt == 1:
                messages = messages + [{"role": "assistant", "content": a["response_text"] or "(empty response)"},
                                       {"role": "user", "content": repair_prompt(errs)}]
        return rec


def beta1_record(d: Path) -> dict:
    """The beta1 scored record, refused unless it holds the pinned bytes and its manifest lists them."""
    body = (d / "ai.json").read_bytes()
    got = hashlib.sha256(body).hexdigest()
    listed = {ln[66:].strip(): ln[:64] for ln in (d / "MANIFEST.sha256").read_text().splitlines() if len(ln) > 66}
    if got != BETA1_AI_SHA256 or listed.get("ai.json") != got:
        raise IntegrityError(f"beta1 ai.json sha256 {got} is not the pinned {BETA1_AI_SHA256} (or not in its manifest)")
    return json.loads(body)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beta1", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model_id = os.environ.get("RESEARCHER_MODEL", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID")
    rec, failure, distiller = {"status": FAILURE}, None, None
    try:
        user = user_prompt(beta1_record(Path(args.beta1)))
        if not model_allowed(model_id):
            raise IntegrityError("RESEARCHER_MODEL does not hash to the pinned model (menu.json)")
        import anthropic

        distiller = Distiller(anthropic.Anthropic(timeout=480.0, max_retries=0), model_id)
        rec = distiller.run(user)
    except Exception as exc:  # recorded, never lost
        rec = getattr(distiller, "rec", rec)
        failure = {"kind": "integrity" if isinstance(exc, IntegrityError) else "crash",
                   "error": redact(f"{type(exc).__name__}: {exc}", model_id)[:2000],
                   "traceback": redact(traceback.format_exc(), model_id)[-4000:]}
        rec.update(status=FAILURE)
    source = {"beta1_run": BETA1_RUN, "beta1_ai_sha256": BETA1_AI_SHA256}
    rec.update(source=source, failure=failure, run_id=run_id, commit=os.environ.get("GITHUB_SHA"))
    (out / "lesson_record.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if rec["status"] == "OK":
        (out / "lesson.json").write_text(json.dumps(
            {"lesson": rec["lesson"], "lesson_sha256": rec["lesson_sha256"], "source": source, "lesson_run": run_id,
             "system_sha256": rec["system_sha256"], "user_prompt_sha256": rec["user_prompt_sha256"]},
            indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    verdict = {"phase": "learn1-lesson", "verdict": rec["status"], "lesson_sha256": rec.get("lesson_sha256"),
               "run_id": run_id, "commit": rec["commit"]}
    (out / "verdict.json").write_text(json.dumps(verdict, indent=1) + "\n")
    attempts = rec.get("attempts", [])
    lines = [f"# learn1 lesson distillation: {rec['status']}", "",
             f"Source: beta1 scored run {BETA1_RUN} (ai.json sha256 `{BETA1_AI_SHA256}`).", "",
             "Attempts: " + ("; ".join(f"#{a['attempt']} {a.get('stop_reason')}"
                                       + (f" ({a.get('refusal_category')})" if a.get("stop_reason") == "refusal" else "")
                                       + f", errors {a.get('errors') or 'none'}, usage {a.get('usage')}"
                                       for a in attempts) or "none") + ".", ""]
    if rec["status"] == "OK":
        lines += ["## Lesson", "", rec["lesson"], "", f"sha256 `{rec['lesson_sha256']}`; {len(rec['lesson'])} characters.",
                  ""]
    else:
        lines += [f"Errors: {rec.get('errors')}; failure: {failure and failure['error']}.", ""]
    (out / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": rec["status"], "lesson_sha256": rec.get("lesson_sha256")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
