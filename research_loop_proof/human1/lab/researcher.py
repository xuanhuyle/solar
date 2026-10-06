"""The Human1 researcher L2: learn1's lesson-only researcher L (``learn1/lab/researcher.py``, condition "L"), given a
human-supplied two-candidate hypothesis (NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md section 3).

The adaptation is only what presenting the human-supplied pair, two rounds and four experiments requires:
- the brief: beta1's brief with four lines changed exactly once each (the candidate sentence names the two candidates
  X01 and X02; the rounds line names the two rounds, days 1-112 and days 1-126; the budget line says 4 experiments, at
  most 2 per round; the beliefs line says "(X01-X02)") and one inserted line, the owner's hypothesis packet verbatim;
- the response schema: Phase 0's, with the candidate id enums listing X01 and X02;
- the call plan, budget, user prompt and code checks: Phase 0's, with the two rounds, the 4-experiment budget (at most 2
  per round) and the two ids.

Everything else is L's, unchanged: the frozen beta1-derived lesson (``learn1/lab/lesson.json``) in its labelled section
between the brief and the schema, the set-evidence rule, the notebook rendering, the one repair turn, the 80k token
cap, the pinned model and effort. No new advice, and nothing about the candidates' hidden roles. Tests check that the
system text maps back to learn1's L text exactly once the five edits are reversed, and that each adapted function is
Phase 0's with the substitution only.
"""
from __future__ import annotations

import copy
import json

from research_loop_proof.beta1.lab import researcher as beta1
from research_loop_proof.human1.lab.executor import IDS2
from research_loop_proof.learn1.lab import researcher as learn1
from research_loop_proof.phase0.lab.executor import IDS, MENU, request_errors
from research_loop_proof.phase0.lab.researcher import (LIMITS, RESEARCHER, TOKEN_CAP, _clean, _now, experiment_ids,
                                                       render_call, repair_prompt, response_schema, sha256_text)

PACKET = ("A human analyst has supplied two anonymous candidate variables as a hypothesis worth testing after forecast "
          "behaviour changed. You are not being asked to search outside this pair. Determine what the evidence supports "
          "about each candidate's current predictive usefulness, including whether one adds value given the other. Use "
          "the experiment budget as you judge appropriate. Your final conclusion must distinguish supported evidence "
          "from uncertainty.")
CANDIDATES_LINE = ("There are four candidate covariate series, X01, X02, X03 and X04.",
                   "There are two candidate covariate series, X01 and X02.")
ROUNDS_LINE = ("Round 1: days 1-84 have been observed. Round 2: days 1-112. Round 3: days 1-126. Then a final call with "
               "no experiments.",
               "Round 1: days 1-112 have been observed. Round 2: days 1-126. Then a final call with no experiments.")
BUDGET_LINE = ("Budget: 6 experiments in total, at most 3 per round.", "Budget: 4 experiments in total, at most 2 per round.")
BELIEFS_LINE = ("one row per candidate (X01-X04)", "one row per candidate (X01-X02)")
REPLACEMENTS = (CANDIDATES_LINE, ROUNDS_LINE, BUDGET_LINE, BELIEFS_LINE)
CANDIDATES_FULL = ("- There are two candidate covariate series, X01 and X02. Their values for a day are known before that "
                   "day starts, so a forecast may use them for the day being forecast.\n")
ROUNDS2 = [(1, 112), (2, 126)]
FINAL_CUTOFF2 = ROUNDS2[-1][1]
BUDGET2 = {"total_experiments": 4, "max_per_round": 2}


def _brief2(brief: str) -> str:
    for old, new in REPLACEMENTS:
        if brief.count(old) != 1:
            raise ValueError(f"the beta1 brief must contain {old!r} exactly once")
        brief = brief.replace(old, new)
    if brief.count(CANDIDATES_FULL) != 1:
        raise ValueError("the candidate line must appear exactly once")
    return brief.replace(CANDIDATES_FULL, CANDIDATES_FULL + "- " + PACKET + "\n")


BRIEF2 = _brief2(beta1.BRIEF)


def _ids2(node):
    """The schema with every candidate-id enum (Phase 0's ``IDS``) replaced by ``IDS2``."""
    if isinstance(node, dict):
        if node.get("enum") == list(IDS):
            return dict(node, enum=list(IDS2))
        return {k: _ids2(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_ids2(v) for v in node]
    return node


def response_schema2() -> dict:
    return _ids2(copy.deepcopy(response_schema()))


def system_text2() -> str:
    return (BRIEF2.rstrip("\n") + "\n\n" + learn1.lesson_section(learn1.frozen_lesson())
            + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema2(), indent=1) + "\n")


# ----------------------------------------------------------------- the call plan and prompts (Phase 0's, two rounds)


def call_plan2() -> list[dict]:
    """The three calls: rounds 1-2 (experiments allowed), then the final call."""
    plan = [{"call": i + 1, "round": r, "cutoff": c, "final": False} for i, (r, c) in enumerate(ROUNDS2)]
    return plan + [{"call": len(ROUNDS2) + 1, "round": None, "cutoff": FINAL_CUTOFF2, "final": True}]


def budget_left2(calls: list[dict]) -> int:
    return BUDGET2["total_experiments"] - sum(len(c.get("experiments", [])) for c in calls)


def user_prompt2(step: dict, calls: list[dict]) -> str:
    """The user text of call ``step`` given the earlier recorded calls."""
    left = budget_left2(calls)
    total = len(call_plan2())
    if step["final"]:
        head = [f"CALL {step['call']} OF {total}: FINAL CALL", f"Observed so far: days 1-{step['cutoff']}.",
                "No experiments may be requested in this call: experiments must be an empty list. Give your "
                "final_selection (possibly empty) and your conclusion."]
    else:
        now = min(BUDGET2["max_per_round"], left)
        head = [f"CALL {step['call']} OF {total}: ROUND {step['round']}", f"Observed so far: days 1-{step['cutoff']}.",
                f"Experiment budget: {left} of {BUDGET2['total_experiments']} left; you may request at most {now} in "
                "this call. final_selection and conclusion must be empty in this call."]
    known = experiment_ids(calls)
    head.append("Experiment ids used so far: " + (", ".join(known) if known else "none") + ".")
    body = ["", "NOTEBOOK (everything recorded so far, oldest first)", ""]
    body += [render_call(c) + "\n" for c in calls] if calls else ["(empty: this is the first call)", ""]
    return "\n".join(head + body + ["Return one JSON object that matches the schema."])


# ----------------------------------------------------------------- checks (Phase 0's, with the two ids)


def response_errors2(obj, step: dict, calls: list[dict]) -> list[str]:
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
            != list(IDS2):
        errs.append(f"beliefs must have exactly one row for each of {', '.join(IDS2)}")
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
        allowed = min(BUDGET2["max_per_round"], budget_left2(calls))
        if len(exps) > allowed:
            errs.append(f"at most {allowed} experiments may be requested in this call")
        for i, e in enumerate(exps, 1):
            for m in request_errors(e, IDS2):
                errs.append(f"experiment {i}: {m}")
            if isinstance(e, dict):
                if e.get("expect") not in MENU["expect"]:
                    errs.append(f"experiment {i}: expect must be one of {MENU['expect']}")
                if not isinstance(e.get("because"), str) or len(e["because"]) > LIMITS["because_chars"]:
                    errs.append(f"experiment {i}: because must be a string of at most {LIMITS['because_chars']} "
                                "characters")
    sel, concl = obj["final_selection"], obj["conclusion"]
    if step["final"]:
        if not isinstance(sel, list) or len(set(map(str, sel))) != len(sel) or any(s not in IDS2 for s in sel):
            errs.append("final_selection must be a list of distinct candidate ids")
        if not isinstance(concl, str) or not concl.strip() or len(concl) > LIMITS["conclusion_chars"]:
            errs.append(f"conclusion must be a non-empty string of at most {LIMITS['conclusion_chars']} characters")
    else:
        if sel != []:
            errs.append("final_selection must be empty before the final call")
        if concl != "":
            errs.append("conclusion must be empty before the final call")
    return errs


def attempt_errors2(text: str, stop_reason: str | None, step: dict, calls: list[dict]) -> tuple[list[str], dict | None]:
    """The errors of one returned attempt and its parsed response (None if unusable)."""
    if stop_reason == "refusal":
        return ["the response was a refusal"], None
    if stop_reason == "max_tokens":
        return ["the response was cut off at the output limit"], None
    try:
        obj = json.loads(text)
    except ValueError as exc:
        return [f"the response is not valid JSON ({exc})"], None
    errs = response_errors2(obj, step, calls)
    return errs, (None if errs else _clean(obj))


# ----------------------------------------------------------------- the researcher

class Researcher2(learn1.Researcher):
    """learn1's researcher in condition L, with the two-candidate brief, schema, call plan and checks."""

    def __init__(self, client, model: str, lab, **kwargs):
        super().__init__(client, model, lab, condition="L", **kwargs)
        self.system = system_text2()

    def _create(self, messages: list[dict], max_tokens: int):
        return self.client.messages.create(
            model=self.model, max_tokens=max_tokens, thinking={"type": "adaptive"},
            output_config={"effort": RESEARCHER["effort"],
                           "format": {"type": "json_schema", "schema": response_schema2()}},
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=messages)

    def run_call(self, step: dict) -> dict:
        user = user_prompt2(step, self.calls)
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
            errs, obj = attempt_errors2(rec["response_text"], rec["stop_reason"], step, self.calls)
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
    def run_plan2(self) -> dict:
        self.emit({"event": "system", "system_text": self.system, "sha256": sha256_text(self.system), "at": _now()})
        for step in call_plan2():
            self.run_call(step)
        final = self.calls[-1]
        return {"calls": self.calls, "tokens_used": self.tokens, "token_cap": TOKEN_CAP,
                "system_sha256": sha256_text(self.system), "system_text": self.system,
                "final_valid": bool(final["final"] and final["valid"]),
                "final_selection": final["response"]["final_selection"] if final["valid"] else None,
                "conclusion": final["response"]["conclusion"] if final["valid"] else None}

    def run(self) -> dict:
        return {"condition": self.condition, **self.run_plan2()}


def rebuild_mismatches2(calls: list[dict]) -> list[str]:
    """Rebuild every recorded prompt from the recorded calls and list the ones that differ (empty when none do)."""
    out, earlier = [], []
    for step, c in zip(call_plan2(), calls):
        if user_prompt2(step, earlier) != c["user_prompt"]:
            out.append(f"call {c['call']}: user prompt")
        atts = c["attempts"]
        if len(atts) == 2 and "repair_prompt" in atts[1]:
            errs, _ = attempt_errors2(atts[0].get("response_text", ""), atts[0].get("stop_reason"), step, earlier)
            if repair_prompt(errs) != atts[1]["repair_prompt"]:
                out.append(f"call {c['call']}: repair prompt")
        earlier.append(c)
    return out
