"""The two researcher conditions of policy1 (NEXT_POLICY_ARCHITECTURE_PROMPT.md sections 4-8; POLICY1_ARCHITECTURE.md).

- L (lesson only): learn1's learned condition exactly (``learn1/lab/researcher.py``, condition "L"): beta1's brief,
  the frozen beta1-derived lesson, beta1's schema and notebook.
- S (structured research policy): the same brief and lesson, plus one structured research-state interface. Every call
  also returns a regime assessment, at most three decision-critical uncertainties, what the remaining budget must
  resolve, the freshness, type, date and unresolved attribution of each candidate's evidence, and for each experiment
  the uncertainty it targets, its likely follow-up and why it is worth a budget slot now. Its own earlier state is
  rendered back to it in the notebook.

The software only validates the new fields (types, enums, lengths; an experiment must name a listed uncertainty). No
code acts on them: there is no planner, quota, reserved experiment or forced split. Everything else is L's: prompts
otherwise as Phase 0 builds them, the one repair turn, the 6-experiment budget, the 80k token cap, the pinned model and
effort. Prompts stay a pure function of the record (``user_prompt_s``, ``rebuild_mismatches_s``).

``run_replay`` is for the non-scored regression replays only: the recorded requests of an earlier run's first calls
are re-run on the lab and shown as replayed evidence, then S makes the remaining calls.
"""
from __future__ import annotations

import copy
import json

from research_loop_proof.beta1.lab import researcher as beta1
from research_loop_proof.learn1.lab import researcher as learn1
from research_loop_proof.phase0.lab import researcher as base
from research_loop_proof.phase0.lab.executor import render_result
from research_loop_proof.phase0.lab.researcher import (BUDGET, LIMITS, RESEARCHER, _clean, _ids, _now, call_plan,
                                                       experiment_ids, repair_prompt, response_schema)

CONDITIONS = ("L", "S")
REGIMES = ("stable", "possible_change", "changed", "unknown")
FRESHNESS = ("current", "possibly_stale", "stale", "unknown")
EVIDENCE_TYPES = ("none", "direct", "grouped", "conditional")
UNCERTAINTY_IDS = ("U1", "U2", "U3")
STATE_LIMITS = {"justification": 300, "uncertainty": 300, "why_it_matters": 300, "budget_needs": 300,
                "attribution": 200, "possible_followup": 300, "budget_rationale": 300}
S_KEYS = ("notes", "regime_assessment", "decision_uncertainties", "budget_needs", "beliefs", "experiments",
          "final_selection", "conclusion")
BASE_KEYS = ("notes", "beliefs", "experiments", "final_selection", "conclusion")
ROW_KEYS = {"candidate", "status", "cites", "reason", "freshness", "evidence_type", "last_scored_day", "attribution"}
EXP_KEYS = {"covariates", "reference", "window_days", "expect", "because", "targets_uncertainty", "possible_followup",
            "budget_rationale"}

STATE_SECTION = """RESEARCH STATE (returned in every call, in addition to the fields above)
- regime_assessment: whether the process generating the data looks stable, possibly changed, changed or unknown so far (status: stable, possible_change, changed or unknown), the experiment ids this rests on (cites) and a one-sentence justification.
- decision_uncertainties: at most 3 items, ids U1 to U3. Each names what is still unresolved (uncertainty) and why it matters for the final selection (why_it_matters). In the final call, list what remains unresolved.
- budget_needs: one sentence on what you may still need to resolve before the final selection, given the experiments remaining.
- In each beliefs row, also: freshness (whether the evidence this status rests on still describes the current process: current, possibly_stale, stale or unknown); evidence_type (none; direct: the candidate tested alone; grouped: tested only inside a set of several covariates; conditional: tested against a reference of other candidates); last_scored_day (the last scored day of the most recent evidence it rests on, 0 if none); attribution (what is unresolved about this candidate's own contribution, empty if nothing).
- In each experiment, also: targets_uncertainty (the id of the decision uncertainty it addresses, from this call's list); possible_followup (what further experiment might be needed if the result is positive, negative or ambiguous); budget_rationale (why it is worth one of the remaining experiments now).
Keep these fields short: justification, uncertainty, why_it_matters, budget_needs, possible_followup and budget_rationale at most 300 characters each; attribution at most 200.
"""


# ----------------------------------------------------------------- schema and system texts

def response_schema_s() -> dict:
    s = copy.deepcopy(response_schema())
    props = s["properties"]
    row = props["beliefs"]["items"]
    row["properties"].update(freshness={"type": "string", "enum": list(FRESHNESS)},
                             evidence_type={"type": "string", "enum": list(EVIDENCE_TYPES)},
                             last_scored_day={"type": "integer"}, attribution={"type": "string"})
    row["required"] = row["required"] + ["freshness", "evidence_type", "last_scored_day", "attribution"]
    exp = props["experiments"]["items"]
    exp["properties"].update(targets_uncertainty={"type": "string", "enum": list(UNCERTAINTY_IDS)},
                             possible_followup={"type": "string"}, budget_rationale={"type": "string"})
    exp["required"] = exp["required"] + ["targets_uncertainty", "possible_followup", "budget_rationale"]
    state = {
        "regime_assessment": {"type": "object", "additionalProperties": False,
                              "required": ["status", "cites", "justification"],
                              "properties": {"status": {"type": "string", "enum": list(REGIMES)},
                                             "cites": {"type": "array", "items": {"type": "string"}},
                                             "justification": {"type": "string"}}},
        "decision_uncertainties": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["id", "uncertainty", "why_it_matters"],
            "properties": {"id": {"type": "string", "enum": list(UNCERTAINTY_IDS)}, "uncertainty": {"type": "string"},
                           "why_it_matters": {"type": "string"}}}},
        "budget_needs": {"type": "string"},
    }
    s["properties"] = {k: (state[k] if k in state else props[k]) for k in S_KEYS}
    s["required"] = list(S_KEYS)
    return s


def system_text(condition: str) -> str:
    if condition == "L":
        return learn1.system_text("L")
    if condition == "S":
        return (beta1.BRIEF.rstrip("\n") + "\n\n" + learn1.lesson_section(learn1.frozen_lesson()) + "\n\n"
                + STATE_SECTION.rstrip("\n") + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema_s(), indent=1)
                + "\n")
    raise ValueError(f"unknown condition {condition!r}")


# ----------------------------------------------------------------- the S notebook (a pure function of the record)

def _head(c: dict) -> str:
    return (f"=== Call {c['call']}: " + (f"round {c['round']}" if not c["final"] else "final call")
            + f", days 1-{c['cutoff']} observed")


def render_call_s(c: dict) -> str:
    if c.get("replayed"):
        lines = [_head(c) + " (replayed: evidence from an earlier investigation; no research state was recorded) ===",
                 "Experiments run:"]
        for e in c["experiments"]:
            q = e["request"]
            lines.append(f"- {e['id']}: covariates {_ids(q['covariates'])}, reference {_ids(q['reference'])}, "
                         f"window {q['window_days']} days")
            lines.append(f"  Result {e['id']}: {render_result(e['result'])}")
        return "\n".join(lines)
    head = _head(c) + " ==="
    if not c.get("valid"):
        errs = "; ".join(c.get("errors", [])) or "no valid response"
        return f"{head}\nNo valid response after one repair ({errs}). No experiment ran in this call."
    r = c["response"]
    ra = r["regime_assessment"]
    lines = [head, f"Notes: {r['notes']}",
             f"Regime assessment: {ra['status']}; cites: {', '.join(ra['cites']) or 'none'}; justification: "
             f"{ra['justification']}",
             "Decision uncertainties:" + ("" if r["decision_uncertainties"] else " none")]
    lines += [f"- {u['id']}: {u['uncertainty']} Why it matters: {u['why_it_matters']}"
              for u in r["decision_uncertainties"]]
    lines += [f"Budget needs: {r['budget_needs']}", "Beliefs:"]
    for b in r["beliefs"]:
        lines.append(f"- {b['candidate']}: {b['status']}; cites: {', '.join(b['cites']) or 'none'}; reason: "
                     f"{b['reason']}; freshness: {b['freshness']}; evidence: {b['evidence_type']}; last scored day: "
                     f"{b['last_scored_day'] or 'none'}; attribution: {b['attribution'] or 'none'}")
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
                         f"window {q['window_days']} days; expected: {q['expect']}; because: {q['because']}; targets: "
                         f"{q['targets_uncertainty']}; possible follow-up: {q['possible_followup']}; budget rationale: "
                         f"{q['budget_rationale']}")
            lines.append(f"  Result {e['id']}: {render_result(e['result'])}")
    return "\n".join(lines)


def user_prompt_s(step: dict, calls: list[dict]) -> str:
    """Phase 0's ``user_prompt`` with the S notebook rendering (the header lines are identical)."""
    left = base.budget_left(calls)
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
    body += [render_call_s(c) + "\n" for c in calls] if calls else ["(empty: this is the first call)", ""]
    return "\n".join(head + body + ["Return one JSON object that matches the schema."])


# ----------------------------------------------------------------- checks

def _short(v, n: int) -> bool:
    return isinstance(v, str) and len(v) <= n


def response_errors_s(obj, step: dict, calls: list[dict]) -> list[str]:
    """Phase 0's checks on the base fields plus the research-state checks (empty when valid)."""
    if not isinstance(obj, dict):
        return ["the response must be a JSON object"]
    if set(obj) != set(S_KEYS):
        return [f"the response must have exactly the keys {sorted(S_KEYS)}"]
    errs = base.response_errors({k: obj[k] for k in BASE_KEYS}, step, calls)
    known = set(experiment_ids(calls))
    ra = obj["regime_assessment"]
    if not isinstance(ra, dict) or set(ra) != {"status", "cites", "justification"}:
        errs.append("regime_assessment must have exactly status, cites and justification")
    else:
        if ra["status"] not in REGIMES:
            errs.append(f"regime_assessment status must be one of {list(REGIMES)}")
        if not isinstance(ra["cites"], list) or len(ra["cites"]) > LIMITS["cites_per_row"] or \
                any(c not in known for c in ra["cites"]):
            errs.append(f"regime_assessment cites must be at most {LIMITS['cites_per_row']} ids of experiments already "
                        f"run ({', '.join(sorted(known)) or 'none yet'})")
        if not _short(ra["justification"], STATE_LIMITS["justification"]):
            errs.append(f"regime_assessment justification must be a string of at most {STATE_LIMITS['justification']} "
                        "characters")
    du, uids = obj["decision_uncertainties"], []
    if not isinstance(du, list) or len(du) > len(UNCERTAINTY_IDS):
        errs.append("decision_uncertainties must be a list of at most 3 items")
    else:
        for u in du:
            if not isinstance(u, dict) or set(u) != {"id", "uncertainty", "why_it_matters"}:
                errs.append("each decision uncertainty must have exactly id, uncertainty and why_it_matters")
                continue
            if u["id"] not in UNCERTAINTY_IDS or u["id"] in uids:
                errs.append("decision uncertainty ids must be distinct ids from U1, U2, U3")
            uids.append(u["id"])
            for k in ("uncertainty", "why_it_matters"):
                if not _short(u[k], STATE_LIMITS[k]):
                    errs.append(f"{u['id']}: {k} must be a string of at most {STATE_LIMITS[k]} characters")
    if not _short(obj["budget_needs"], STATE_LIMITS["budget_needs"]):
        errs.append(f"budget_needs must be a string of at most {STATE_LIMITS['budget_needs']} characters")
    for b in obj["beliefs"] if isinstance(obj["beliefs"], list) else []:
        if not isinstance(b, dict) or set(b) != ROW_KEYS:
            errs.append(f"each beliefs row must have exactly {sorted(ROW_KEYS)}")
            continue
        name = b.get("candidate")
        if b["freshness"] not in FRESHNESS:
            errs.append(f"{name}: freshness must be one of {list(FRESHNESS)}")
        if b["evidence_type"] not in EVIDENCE_TYPES:
            errs.append(f"{name}: evidence_type must be one of {list(EVIDENCE_TYPES)}")
        d = b["last_scored_day"]
        if isinstance(d, bool) or not isinstance(d, int) or not 0 <= d <= step["cutoff"]:
            errs.append(f"{name}: last_scored_day must be an integer from 0 to {step['cutoff']}")
        if not _short(b["attribution"], STATE_LIMITS["attribution"]):
            errs.append(f"{name}: attribution must be a string of at most {STATE_LIMITS['attribution']} characters")
    for i, e in enumerate(obj["experiments"] if isinstance(obj["experiments"], list) else [], 1):
        if not isinstance(e, dict) or set(e) != EXP_KEYS:
            errs.append(f"experiment {i}: must have exactly {sorted(EXP_KEYS)}")
            continue
        if e["targets_uncertainty"] not in uids:
            errs.append(f"experiment {i}: targets_uncertainty must be one of this call's decision uncertainty ids "
                        f"({', '.join(uids) or 'none listed'})")
        for k in ("possible_followup", "budget_rationale"):
            if not _short(e[k], STATE_LIMITS[k]):
                errs.append(f"experiment {i}: {k} must be a string of at most {STATE_LIMITS[k]} characters")
    return errs


def attempt_errors_s(text: str, stop_reason: str | None, step: dict, calls: list[dict]) -> tuple[list[str], dict | None]:
    if stop_reason == "refusal":
        return ["the response was a refusal"], None
    if stop_reason == "max_tokens":
        return ["the response was cut off at the output limit"], None
    try:
        obj = json.loads(text)
    except ValueError as exc:
        return [f"the response is not valid JSON ({exc})"], None
    errs = response_errors_s(obj, step, calls)
    return errs, (None if errs else _clean(obj))


# ----------------------------------------------------------------- the S researcher

class StructuredResearcher(beta1.Researcher):
    condition = "S"

    def __init__(self, client, model: str, lab, **kwargs):
        super().__init__(client, model, lab, **kwargs)
        self.system = system_text("S")

    def _create(self, messages: list[dict], max_tokens: int):
        return self.client.messages.create(
            model=self.model, max_tokens=max_tokens, thinking={"type": "adaptive"},
            output_config={"effort": RESEARCHER["effort"],
                           "format": {"type": "json_schema", "schema": response_schema_s()}},
            system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
            messages=messages)

    def run_call(self, step: dict) -> dict:
        """Phase 0's ``run_call`` with the S prompt and checks."""
        user = user_prompt_s(step, self.calls)
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
            errs, obj = attempt_errors_s(rec["response_text"], rec["stop_reason"], step, self.calls)
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
            r = call["response"]
            self.emit({"event": "state", "call": step["call"], **{k: r[k] for k in S_KEYS if k != "experiments"}})
        self.calls.append(call)
        return call

    def run(self) -> dict:
        return {"condition": "S", **super().run()}

    def run_replay(self, prefix: list[list[dict]]) -> dict:
        """Non-scored replay: re-run the recorded requests of the first calls (shown as replayed), then make the rest."""
        self.emit({"event": "system", "system_text": self.system, "sha256": base.sha256_text(self.system),
                   "at": _now(), "replay_prefix_calls": len(prefix)})
        plan = call_plan()
        for step, requests in zip(plan, prefix):
            known, exps = len(experiment_ids(self.calls)), []
            for i, q in enumerate(requests, 1):
                q = {k: q[k] for k in ("covariates", "reference", "window_days")}
                exps.append({"id": f"E{known + i}", "request": q, "result": self.lab.run(q, step["cutoff"],
                                                                                         f"E{known + i}")})
            self.calls.append({"call": step["call"], "round": step["round"], "cutoff": step["cutoff"],
                               "final": False, "replayed": True, "valid": True, "response": None, "attempts": [],
                               "errors": [], "experiments": exps, "user_prompt": None})
        for step in plan[len(prefix):]:
            self.run_call(step)
        final = self.calls[-1]
        return {"condition": "S", "replay_prefix_calls": len(prefix), "calls": self.calls, "tokens_used": self.tokens,
                "token_cap": base.TOKEN_CAP, "system_sha256": base.sha256_text(self.system),
                "system_text": self.system, "final_valid": bool(final["final"] and final["valid"]),
                "final_selection": final["response"]["final_selection"] if final["valid"] else None,
                "conclusion": final["response"]["conclusion"] if final["valid"] else None}


def rebuild_mismatches_s(calls: list[dict]) -> list[str]:
    """Rebuild every S prompt from the recorded calls (replayed calls are evidence, not prompts)."""
    out, earlier = [], []
    for step, c in zip(call_plan(), calls):
        if not c.get("replayed"):
            if user_prompt_s(step, earlier) != c["user_prompt"]:
                out.append(f"call {c['call']}: user prompt")
            atts = c["attempts"]
            if len(atts) == 2 and "repair_prompt" in atts[1]:
                errs, _ = attempt_errors_s(atts[0].get("response_text", ""), atts[0].get("stop_reason"), step, earlier)
                if repair_prompt(errs) != atts[1]["repair_prompt"]:
                    out.append(f"call {c['call']}: repair prompt")
        earlier.append(c)
    return out


def researcher_for(condition: str, client, model: str, lab, **kwargs):
    if condition == "L":
        return learn1.Researcher(client, model, lab, condition="L", **kwargs)
    if condition == "S":
        return StructuredResearcher(client, model, lab, **kwargs)
    raise ValueError(f"unknown condition {condition!r}")


def rebuild_for(condition: str):
    return learn1.rebuild_mismatches if condition == "L" else rebuild_mismatches_s
