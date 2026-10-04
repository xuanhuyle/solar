"""The Discovery1 researcher L8: learn1's lesson-only researcher L (``learn1/lab/researcher.py``, condition "L"),
adapted mechanically to eight candidates (NEXT_DISCOVERY_MILESTONE_PROMPT.md, "Researcher").

The adaptation is only what enumerating X01-X08 instead of X01-X04 requires:
- the brief: beta1's brief with exactly two lines changed, the sentence naming the candidates ("four ..., X01, X02, X03
  and X04" becomes "eight ..., X01, ..., X08") and the beliefs line ("(X01-X04)" becomes "(X01-X08)");
- the response schema: Phase 0's, with the candidate id enums listing X01-X08;
- the code checks: Phase 0's, with the eight ids (one belief row per candidate, ids in requests and the selection).

Everything else is L's, unchanged: the frozen beta1-derived lesson (``learn1/lab/lesson.json``) in its labelled section
between the brief and the schema, the user and repair prompts (Phase 0's, which never name the candidates), the one
repair turn, the 6-experiment budget with at most 3 per round, at most 4 covariates per experiment, the 80k token cap,
the pinned model and effort. No new advice. Tests check that the system text maps back to learn1's L text exactly, and
that each adapted function is Phase 0's with the id substitution only.
"""
from __future__ import annotations

import copy
import json

from research_loop_proof.beta1.lab import researcher as beta1
from research_loop_proof.discovery1.lab.executor import IDS8
from research_loop_proof.learn1.lab import researcher as learn1
from research_loop_proof.phase0.lab.executor import IDS, MENU, request_errors
from research_loop_proof.phase0.lab.researcher import (BUDGET, LIMITS, RESEARCHER, _clean, _now, budget_left,
                                                       call_plan, experiment_ids, repair_prompt, response_schema,
                                                       user_prompt)

CANDIDATES_LINE = ("There are four candidate covariate series, X01, X02, X03 and X04.",
                   "There are eight candidate covariate series, X01, X02, X03, X04, X05, X06, X07 and X08.")
BELIEFS_LINE = ("one row per candidate (X01-X04)", "one row per candidate (X01-X08)")


def _brief8(brief: str) -> str:
    for old, new in (CANDIDATES_LINE, BELIEFS_LINE):
        if brief.count(old) != 1:
            raise ValueError(f"the beta1 brief must contain {old!r} exactly once")
        brief = brief.replace(old, new)
    return brief


BRIEF8 = _brief8(beta1.BRIEF)


def _ids8(node):
    """The schema with every candidate-id enum (Phase 0's ``IDS``) replaced by ``IDS8``."""
    if isinstance(node, dict):
        if node.get("enum") == list(IDS):
            return dict(node, enum=list(IDS8))
        return {k: _ids8(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_ids8(v) for v in node]
    return node


def response_schema8() -> dict:
    return _ids8(copy.deepcopy(response_schema()))


def system_text8() -> str:
    return (BRIEF8.rstrip("\n") + "\n\n" + learn1.lesson_section(learn1.frozen_lesson())
            + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema8(), indent=1) + "\n")


# ----------------------------------------------------------------- checks (Phase 0's, with the eight ids)

def response_errors8(obj, step: dict, calls: list[dict]) -> list[str]:
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
            != list(IDS8):
        errs.append(f"beliefs must have exactly one row for each of {', '.join(IDS8)}")
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
            for m in request_errors(e, IDS8):
                errs.append(f"experiment {i}: {m}")
            if isinstance(e, dict):
                if e.get("expect") not in MENU["expect"]:
                    errs.append(f"experiment {i}: expect must be one of {MENU['expect']}")
                if not isinstance(e.get("because"), str) or len(e["because"]) > LIMITS["because_chars"]:
                    errs.append(f"experiment {i}: because must be a string of at most {LIMITS['because_chars']} "
                                "characters")
    sel, concl = obj["final_selection"], obj["conclusion"]
    if step["final"]:
        if not isinstance(sel, list) or len(set(map(str, sel))) != len(sel) or any(s not in IDS8 for s in sel):
            errs.append("final_selection must be a list of distinct candidate ids")
        if not isinstance(concl, str) or not concl.strip() or len(concl) > LIMITS["conclusion_chars"]:
            errs.append(f"conclusion must be a non-empty string of at most {LIMITS['conclusion_chars']} characters")
    else:
        if sel != []:
            errs.append("final_selection must be empty before the final call")
        if concl != "":
            errs.append("conclusion must be empty before the final call")
    return errs


def attempt_errors8(text: str, stop_reason: str | None, step: dict, calls: list[dict]) -> tuple[list[str], dict | None]:
    """The errors of one returned attempt and its parsed response (None if unusable)."""
    if stop_reason == "refusal":
        return ["the response was a refusal"], None
    if stop_reason == "max_tokens":
        return ["the response was cut off at the output limit"], None
    try:
        obj = json.loads(text)
    except ValueError as exc:
        return [f"the response is not valid JSON ({exc})"], None
    errs = response_errors8(obj, step, calls)
    return errs, (None if errs else _clean(obj))


# ----------------------------------------------------------------- the researcher

class Researcher8(learn1.Researcher):
    """learn1's researcher in condition L, with the eight-candidate brief, schema and checks."""

    def __init__(self, client, model: str, lab, **kwargs):
        super().__init__(client, model, lab, condition="L", **kwargs)
        self.system = system_text8()

    def _create(self, messages: list[dict], max_tokens: int):
        return self.client.messages.create(
            model=self.model, max_tokens=max_tokens, thinking={"type": "adaptive"},
            output_config={"effort": RESEARCHER["effort"],
                           "format": {"type": "json_schema", "schema": response_schema8()}},
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=messages)

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
            errs, obj = attempt_errors8(rec["response_text"], rec["stop_reason"], step, self.calls)
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


def rebuild_mismatches8(calls: list[dict]) -> list[str]:
    """Rebuild every recorded prompt from the recorded calls and list the ones that differ (empty when none do)."""
    out, earlier = [], []
    for step, c in zip(call_plan(), calls):
        if user_prompt(step, earlier) != c["user_prompt"]:
            out.append(f"call {c['call']}: user prompt")
        atts = c["attempts"]
        if len(atts) == 2 and "repair_prompt" in atts[1]:
            errs, _ = attempt_errors8(atts[0].get("response_text", ""), atts[0].get("stop_reason"), step, earlier)
            if repair_prompt(errs) != atts[1]["repair_prompt"]:
                out.append(f"call {c['call']}: repair prompt")
        earlier.append(c)
    return out
