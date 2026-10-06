"""The AI researcher of Phase B (PHASE0_SPEC.md section 4): four calls, at most six t0 experiments.

Each call is one fresh request: the brief (``lab/brief.md``, verbatim) and the response schema as the system text;
the call, the revealed days, the remaining budget and the notebook (every earlier note, belief table, request and
result) as the user text. Every prompt is a pure function of the recorded calls (``user_prompt``, ``repair_prompt``),
so the evaluator can rebuild it byte for byte. Counts, ids and lengths are checked in code with one repair turn per
call; an invalid round runs no experiment and is recorded. The model is fixed by the sha256 of its id in
``menu.json`` (the id itself is not written anywhere in the repository); the effort is ``menu.json``'s literal.
Usage is capped at 80k tokens in all, in code. The API helpers follow ``engine/researcher.py``.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from research_loop_proof.phase0.lab.executor import IDS, MENU, render_result, request_errors

HERE = Path(__file__).resolve().parent
BRIEF = (HERE / "brief.md").read_text(encoding="utf-8")
RESEARCHER = MENU["researcher"]
LIMITS = MENU["limits"]
BUDGET = MENU["budget"]
TOKEN_CAP = MENU["calls"]["token_cap_total"]
ROUNDS = [(r["round"], r["revealed_through_day"]) for r in MENU["rounds"]]
FINAL_CUTOFF = ROUNDS[-1][1]
MAX_TOKENS = 16000  # per call; lowered when the remaining token cap requires it
MIN_CALL_TOKENS = 4000  # a call that cannot be given this many output tokens is not made
CALL_TIMEOUT_S = 480.0
MAX_TRANSIENT_RETRIES = 5  # waits of 2, 4, 8, 16 and 30 s (or the server's retry-after, up to 60 s)
TRANSIENT_STATUS = frozenset({408, 409, 429})


class IntegrityError(RuntimeError):
    """A condition the spec counts as an integrity failure (verdict row 0)."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def model_allowed(model_id: str | None) -> bool:
    return bool(model_id) and sha256_text(model_id) == RESEARCHER["model_sha256"]


_MODEL_LIKE = re.compile(r"claude-[A-Za-z0-9._-]+", re.IGNORECASE)


def redact(text: str, model: str | None) -> str:
    """Error text with any model identifier removed (no identifier may reach a published file)."""
    if model:
        text = text.replace(model, "<model>")
    return _MODEL_LIKE.sub("<model>", text)


# ----------------------------------------------------------------- schema and prompts

def response_schema() -> dict:
    ids = {"type": "string", "enum": list(IDS)}
    belief = {"type": "object", "additionalProperties": False, "required": ["candidate", "status", "cites", "reason"],
              "properties": {"candidate": ids, "status": {"type": "string", "enum": list(MENU["statuses"])},
                             "cites": {"type": "array", "items": {"type": "string"}},
                             "reason": {"type": "string"}}}
    experiment = {"type": "object", "additionalProperties": False,
                  "required": ["covariates", "reference", "window_days", "expect", "because"],
                  "properties": {"covariates": {"type": "array", "items": ids},
                                 "reference": {"type": "array", "items": ids},
                                 "window_days": {"type": "integer", "enum": list(MENU["experiment"]["window_days"])},
                                 "expect": {"type": "string", "enum": list(MENU["expect"])},
                                 "because": {"type": "string"}}}
    return {"type": "object", "additionalProperties": False,
            "required": ["notes", "beliefs", "experiments", "final_selection", "conclusion"],
            "properties": {"notes": {"type": "string"}, "beliefs": {"type": "array", "items": belief},
                           "experiments": {"type": "array", "items": experiment},
                           "final_selection": {"type": "array", "items": ids}, "conclusion": {"type": "string"}}}


def system_text() -> str:
    return BRIEF.rstrip("\n") + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema(), indent=1) + "\n"


def call_plan() -> list[dict]:
    """The four calls: rounds 1-3 (experiments allowed), then the final call."""
    plan = [{"call": i + 1, "round": r, "cutoff": c, "final": False} for i, (r, c) in enumerate(ROUNDS)]
    return plan + [{"call": len(ROUNDS) + 1, "round": None, "cutoff": FINAL_CUTOFF, "final": True}]


def budget_left(calls: list[dict]) -> int:
    return BUDGET["total_experiments"] - sum(len(c.get("experiments", [])) for c in calls)


def experiment_ids(calls: list[dict]) -> list[str]:
    return [e["id"] for c in calls for e in c.get("experiments", [])]


def _ids(xs) -> str:
    return "[" + ", ".join(xs) + "]" if xs else "[none]"


def render_call(c: dict) -> str:
    head = (f"=== Call {c['call']}: " + (f"round {c['round']}" if not c["final"] else "final call")
            + f", days 1-{c['cutoff']} observed ===")
    if not c.get("valid"):
        errs = "; ".join(c.get("errors", [])) or "no valid response"
        return f"{head}\nNo valid response after one repair ({errs}). No experiment ran in this call."
    r = c["response"]
    lines = [head, f"Notes: {r['notes']}", "Beliefs:"]
    for b in r["beliefs"]:
        cites = ", ".join(b["cites"]) if b["cites"] else "none"
        lines.append(f"- {b['candidate']}: {b['status']}; cites: {cites}; reason: {b['reason']}")
    if c["final"]:
        lines += [f"Final selection: {_ids(r['final_selection'])}", f"Conclusion: {r['conclusion']}"]
        return "\n".join(lines)
    if not c.get("experiments"):
        lines.append("Experiments requested: none")
    else:
        lines.append("Experiments requested:")
        for e in c["experiments"]:
            q = e["request"]
            lines.append(f"- {e['id']}: covariates {_ids(q['covariates'])}, reference {_ids(q['reference'])}, "
                         f"window {q['window_days']} days; expected: {q['expect']}; because: {q['because']}")
            lines.append(f"  Result {e['id']}: {render_result(e['result'])}")
    return "\n".join(lines)


def user_prompt(step: dict, calls: list[dict]) -> str:
    """The user text of call ``step`` given the earlier recorded calls."""
    left = budget_left(calls)
    total = len(call_plan())
    if step["final"]:
        head = [f"CALL {step['call']} OF {total}: FINAL CALL", f"Observed so far: days 1-{step['cutoff']}.",
                "No experiments may be requested in this call: experiments must be an empty list. Give your "
                "final_selection (possibly empty) and your conclusion."]
    else:
        now = min(BUDGET["max_per_round"], left)
        head = [f"CALL {step['call']} OF {total}: ROUND {step['round']}", f"Observed so far: days 1-{step['cutoff']}.",
                f"Experiment budget: {left} of {BUDGET['total_experiments']} left; you may request at most {now} in "
                "this call. final_selection and conclusion must be empty in this call."]
    known = experiment_ids(calls)
    head.append("Experiment ids used so far: " + (", ".join(known) if known else "none") + ".")
    body = ["", "NOTEBOOK (everything recorded so far, oldest first)", ""]
    body += [render_call(c) + "\n" for c in calls] if calls else ["(empty: this is the first call)", ""]
    return "\n".join(head + body + ["Return one JSON object that matches the schema."])


def repair_prompt(errors: list[str]) -> str:
    return ("The lab rejected that response:\n- " + "\n- ".join(errors)
            + "\nReturn a corrected JSON object that matches the schema.")


# ----------------------------------------------------------------- checks

def response_errors(obj, step: dict, calls: list[dict]) -> list[str]:
    """Why a parsed response is not valid for this call (empty when it is)."""
    if not isinstance(obj, dict):
        return ["the response must be a JSON object"]
    errs = []
    keys = {"notes", "beliefs", "experiments", "final_selection", "conclusion"}
    if set(obj) != keys:
        return [f"the response must have exactly the keys {sorted(keys)}"]
    known = set(experiment_ids(calls))
    if not isinstance(obj["notes"], str) or len(obj["notes"]) > LIMITS["notes_chars"]:
        errs.append(f"notes must be a string of at most {LIMITS['notes_chars']} characters")
    beliefs = obj["beliefs"]
    if not isinstance(beliefs, list) or sorted(str(b.get("candidate")) if isinstance(b, dict) else "" for b in beliefs) \
            != list(IDS):
        errs.append(f"beliefs must have exactly one row for each of {', '.join(IDS)}")
    else:
        for b in beliefs:
            if b.get("status") not in MENU["statuses"]:
                errs.append(f"{b['candidate']}: unknown status {b.get('status')!r}")
            cites = b.get("cites")
            if not isinstance(cites, list) or len(cites) > LIMITS["cites_per_row"] or \
                    any(c not in known for c in cites):
                errs.append(f"{b['candidate']}: cites must be at most {LIMITS['cites_per_row']} ids of experiments "
                            f"already run ({', '.join(sorted(known)) or 'none yet'})")
            if not isinstance(b.get("reason"), str) or len(b["reason"]) > LIMITS["reason_chars"]:
                errs.append(f"{b['candidate']}: reason must be a string of at most {LIMITS['reason_chars']} characters")
    exps = obj["experiments"]
    if not isinstance(exps, list):
        errs.append("experiments must be a list")
    elif step["final"]:
        if exps:
            errs.append("experiments must be empty in the final call")
    else:
        allowed = min(BUDGET["max_per_round"], budget_left(calls))
        if len(exps) > allowed:
            errs.append(f"at most {allowed} experiments may be requested in this call")
        for i, e in enumerate(exps, 1):
            for m in request_errors(e):
                errs.append(f"experiment {i}: {m}")
            if isinstance(e, dict):
                if e.get("expect") not in MENU["expect"]:
                    errs.append(f"experiment {i}: expect must be one of {MENU['expect']}")
                if not isinstance(e.get("because"), str) or len(e["because"]) > LIMITS["because_chars"]:
                    errs.append(f"experiment {i}: because must be a string of at most {LIMITS['because_chars']} "
                                "characters")
    sel, concl = obj["final_selection"], obj["conclusion"]
    if step["final"]:
        if not isinstance(sel, list) or len(set(map(str, sel))) != len(sel) or any(s not in IDS for s in sel):
            errs.append("final_selection must be a list of distinct candidate ids")
        if not isinstance(concl, str) or not concl.strip() or len(concl) > LIMITS["conclusion_chars"]:
            errs.append(f"conclusion must be a non-empty string of at most {LIMITS['conclusion_chars']} characters")
    else:
        if sel != []:
            errs.append("final_selection must be empty before the final call")
        if concl != "":
            errs.append("conclusion must be empty before the final call")
    return errs


def attempt_errors(text: str, stop_reason: str | None, step: dict, calls: list[dict]) -> tuple[list[str], dict | None]:
    """The errors of one returned attempt and its parsed response (None if unusable)."""
    if stop_reason == "refusal":
        return ["the response was a refusal"], None
    if stop_reason == "max_tokens":
        return ["the response was cut off at the output limit"], None
    try:
        obj = json.loads(text)
    except ValueError as exc:
        return [f"the response is not valid JSON ({exc})"], None
    errs = response_errors(obj, step, calls)
    return errs, (None if errs else _clean(obj))


# ----------------------------------------------------------------- API (helpers as in engine/researcher.py)

def _usage(resp) -> dict:
    u = getattr(resp, "usage", None)
    keys = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    return {k: int(getattr(u, k, 0) or 0) for k in keys}


def _text(resp) -> str:
    return "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")


def _storable(text: str) -> str:
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


def _clean(x):
    """Every string made storable (an escaped lone surrogate in the JSON would stop the record)."""
    if isinstance(x, str):
        return _storable(x)
    if isinstance(x, list):
        return [_clean(v) for v in x]
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    return x


def transient(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int) and (status in TRANSIENT_STATUS or status >= 500):
        return True
    names = {c.__name__ for c in type(exc).__mro__}
    return "APIConnectionError" in names and "APITimeoutError" not in names


def _retry_after(exc: BaseException) -> float | None:
    headers = getattr(getattr(exc, "response", None), "headers", None) or {}
    try:
        return float(headers.get("retry-after"))
    except (TypeError, ValueError):
        return None


def tokens_of(usage: dict) -> int:
    return sum(usage.values())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Researcher:
    """Runs the four calls against ``lab`` (an ``executor.Lab``), recording everything through ``emit``."""

    def __init__(self, client, model: str, lab, *, emit=None, sleep=time.sleep):
        if not model_allowed(model):
            raise IntegrityError("the researcher model is not the one pinned in menu.json (sha256 mismatch)")
        self.client, self.model, self.lab = client, model, lab
        self.emit = emit or (lambda event: None)
        self.sleep = sleep
        self.system = system_text()
        self.tokens = 0
        self.calls: list[dict] = []

    def _create(self, messages: list[dict], max_tokens: int):
        return self.client.messages.create(
            model=self.model, max_tokens=max_tokens, thinking={"type": "adaptive"},
            output_config={"effort": RESEARCHER["effort"],
                           "format": {"type": "json_schema", "schema": response_schema()}},
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=messages)

    def _attempt(self, step: dict, messages: list[dict], attempt: int) -> dict:
        prompt_chars = len(self.system) + sum(len(m["content"]) if isinstance(m["content"], str) else
                                              sum(len(b.get("text", "")) for b in m["content"]) for m in messages)
        room = TOKEN_CAP - self.tokens - math.ceil(prompt_chars / 2)  # 2 characters per token: conservative
        max_tokens = min(MAX_TOKENS, room)
        record = {"call": step["call"], "attempt": attempt, "started_at": _now(), "max_tokens": max_tokens,
                  "effort": RESEARCHER["effort"], "requested_model_sha256": sha256_text(self.model)}
        if max_tokens < MIN_CALL_TOKENS:
            record.update(skipped="token cap: not enough room left for a call", tokens_used=self.tokens)
            self.emit({"event": "attempt", **record})
            return record
        retry = 0
        while True:
            try:
                resp = self._create(messages, max_tokens)
                break
            except Exception as exc:  # recorded: a failed call may still have been billed
                fail = dict(record, retry=retry, error=redact(f"{type(exc).__name__}: {exc}", self.model)[:1000],
                            finished_at=_now(), transient=transient(exc))
                self.emit({"event": "api_error", **fail})
                if transient(exc) and retry < MAX_TRANSIENT_RETRIES:
                    self.sleep(min(60.0, _retry_after(exc) or min(30.0, 2.0 * 2 ** retry)))
                    retry += 1
                    continue
                raise IntegrityError(f"API outage: {type(exc).__name__}") from exc
        usage = _usage(resp)
        self.tokens += tokens_of(usage)
        served = getattr(resp, "model", None) or ""
        record.update(retry=retry, finished_at=_now(), served_model_sha256=sha256_text(served),
                      request_id=getattr(resp, "_request_id", None), stop_reason=getattr(resp, "stop_reason", None),
                      usage=usage, tokens_used=self.tokens, response_text=_storable(_text(resp)))
        if not model_allowed(served):
            self.emit({"event": "attempt", **record, "integrity": "served model hash mismatch"})
            raise IntegrityError("the served model is not the pinned model")
        return record

    def run_call(self, step: dict) -> dict:
        user = user_prompt(step, self.calls)
        self.emit({"event": "prompt", "call": step["call"], "user_prompt": user, "at": _now()})
        messages = [{"role": "user", "content": user}]
        call = {"call": step["call"], "round": step["round"], "cutoff": step["cutoff"], "final": step["final"],
                "user_prompt": user, "attempts": [], "valid": False, "response": None, "errors": [],
                "experiments": []}
        for attempt in (1, 2):
            rec = self._attempt(step, messages, attempt)
            if attempt == 2:
                rec["repair_prompt"] = messages[-1]["content"]
            call["attempts"].append(rec)
            if "skipped" in rec:
                call["errors"] = [rec["skipped"]]
                break
            errs, obj = attempt_errors(rec["response_text"], rec["stop_reason"], step, self.calls)
            rec["errors"] = errs
            self.emit({"event": "attempt", **rec})
            if obj is not None:
                call.update(valid=True, response=obj, errors=[])
                break
            call["errors"] = errs
            if attempt == 1:
                text = rec["response_text"] or "(empty response)"
                messages = messages + [{"role": "assistant", "content": text},
                                       {"role": "user", "content": repair_prompt(errs)}]
        if call["valid"] and not step["final"]:
            known = len(experiment_ids(self.calls))
            for i, q in enumerate(call["response"]["experiments"], 1):
                exp_id = f"E{known + i}"
                result = self.lab.run(q, step["cutoff"], exp_id)
                call["experiments"].append({"id": exp_id, "request": q, "result": result})
                self.emit({"event": "experiment", "call": step["call"], "id": exp_id, "request": q,
                           "result": result, "at": _now()})
        if call["valid"]:
            self.emit({"event": "beliefs", "call": step["call"], "beliefs": call["response"]["beliefs"],
                       "notes": call["response"]["notes"]})
        self.calls.append(call)
        return call

    def run(self) -> dict:
        self.emit({"event": "system", "system_text": self.system, "sha256": sha256_text(self.system), "at": _now()})
        for step in call_plan():
            self.run_call(step)
        final = self.calls[-1]
        return {"calls": self.calls, "tokens_used": self.tokens, "token_cap": TOKEN_CAP,
                "system_sha256": sha256_text(self.system), "system_text": self.system,
                "final_valid": bool(final["final"] and final["valid"]),
                "final_selection": final["response"]["final_selection"] if final["valid"] else None,
                "conclusion": final["response"]["conclusion"] if final["valid"] else None}


def rebuild_mismatches(calls: list[dict]) -> list[str]:
    """Rebuild every recorded prompt from the recorded calls and list the ones that differ (empty when none do)."""
    out, earlier = [], []
    for step, c in zip(call_plan(), calls):
        if user_prompt(step, earlier) != c["user_prompt"]:
            out.append(f"call {c['call']}: user prompt")
        atts = c["attempts"]
        if len(atts) == 2 and "repair_prompt" in atts[1]:
            errs, _ = attempt_errors(atts[0].get("response_text", ""), atts[0].get("stop_reason"), step, earlier)
            if repair_prompt(errs) != atts[1]["repair_prompt"]:
                out.append(f"call {c['call']}: repair prompt")
        earlier.append(c)
    return out
