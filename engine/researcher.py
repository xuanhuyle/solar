"""The AI researcher: reads the ledger digest and the catalogue, proposes the next probe.

It runs in its own GitHub Actions job with the Claude API key and nothing else:
no Hugging Face token, no data, no write access. It answers with a declarative
action - ``probe`` (a spec from the catalogue) or ``stop`` - as JSON constrained
by a schema built from the catalogue's own enums, so it can only name what
exists. The referee re-validates everything it proposes.

Every call is recorded (``research_call``): the served model, token usage,
request id, the ledger head it saw, the sha256 of the system and user prompts
(both are rebuilt byte for byte from the code and the ledger at that head),
and the full response text. Standard library + ``anthropic`` only.

    python -m engine.researcher --ledger ledgerro/ledger.jsonl --out results/engine --iteration 1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from engine import catalogue as cat
from engine import ledger
from engine.canon import canonical_json
from engine.spec import PROBE_VERSION, SpecError, validate_probe

MAX_TOKENS = 16000
HARD_MAX_ITERATIONS = 8
DEFAULT_TOKEN_CAP = 2_000_000  # per UTC day, input + output, across all research calls

OBJECTIVE = (
    "The core of the project is an AI researcher that uses t0's covariate capabilities. It investigates which "
    "information improves forecasts, validates those findings scientifically, and uses the accumulated evidence to "
    "guide subsequent experiments. The referee supports that research loop. The immediate milestone is one bounded, "
    "reproducible, independently confirmed predictive finding using t0, followed by an investigation that builds on it."
)

RULES = """You are the research agent of a forecasting knowledge engine. You never write code or touch data:
you choose the next *probe* - a declarative experiment made only of catalogue entries - and a referee you do
not control runs it on the discovery zone (2022-2025; 2025 is consumed: explore only) and records the result.

How the engine works:
- Every probe result is EXPLORATORY. It guides you; it is never a finding.
- Findings are confirmed only later, on sealed forward data that arrives after a claim is frozen, with the
  owner's approval. Aim for probes that could become a clean, freezable claim: one arm, one comparator,
  a large and stable effect across periods and scopes.
- Build on the accepted findings (see the digest). For consumption the accepted arm is t0 + holiday (claim C1).
  RTE's own forecast (rte_j1) is a reference you may compare against, but it never decides anything.
- Weather covariates are usable only after their known-answer gate passed (listed under "gates").
- Your budget counts every comparison you run; an identical probe returns its recorded result at no cost.
- Prefer questions that separate hypotheses; do not repeat a probe whose result you already have.
- When the exploratory evidence for an effect is strong and stable, you may instead *freeze* a claim
  batch (action "freeze", at most 4 claims, each citing the probe_result seqs it rests on, with a
  margin delta in {0, 0.05, 0.1, 0.2} that the skill must exceed). A frozen batch is confirmed only on
  84 days of forward data after a 14-day embargo - months later - and each batch spends a quarter of
  the ledger's whole error budget, so freeze rarely and only what you would bet on. Freezing ends
  this chain.
- Answer with the JSON object only. "note" explains your reasoning in at most 600 characters.
  Set "probe" for a probe, "claim_batch" for a freeze, and the other to null.
  Use action "stop" when nothing is worth its cost.
"""


def _enum(values) -> dict:
    return {"type": "string", "enum": sorted(values)}


def action_schema() -> dict:
    """JSON schema for the researcher's answer, built from the catalogue (no free-form names except arm names)."""
    transforms = sorted({t for c in cat.COVARIATES.values() for t in c["transforms"]})
    covariate = {"type": "object", "additionalProperties": False, "required": ["id", "transform"],
                 "properties": {"id": _enum(cat.COVARIATES), "transform": _enum(transforms)}}
    arm = {"type": "object", "additionalProperties": False, "required": ["name", "covariates"],
           "properties": {"name": {"type": "string"}, "covariates": {"type": "array", "items": covariate}}}
    comparison = {"type": "object", "additionalProperties": False, "required": ["arm", "vs", "metric"],
                  "properties": {"arm": {"type": "string"}, "vs": {"type": "string"}, "metric": _enum(cat.METRICS)}}
    probe = {"type": "object", "additionalProperties": False,
             "required": ["spec_version", "target", "period", "scope", "arms", "comparisons", "builds_on", "rationale"],
             "properties": {"spec_version": {"type": "string", "enum": [PROBE_VERSION]}, "target": _enum(cat.TARGETS),
                            "period": _enum(cat.PERIODS), "scope": _enum(cat.SCOPES),
                            "arms": {"type": "array", "items": arm}, "comparisons": {"type": "array", "items": comparison},
                            "builds_on": {"type": "array", "items": {"type": "integer"}},
                            "rationale": {"type": "string"}}}
    claim = {"type": "object", "additionalProperties": False,
             "required": ["id", "statement", "target", "arm", "comparator", "scope", "delta", "evidence"],
             "properties": {"id": {"type": "string"}, "statement": {"type": "string"}, "target": _enum(cat.TARGETS),
                            "arm": {"type": "object", "additionalProperties": False, "required": ["covariates"],
                                    "properties": {"covariates": {"type": "array", "items": covariate}}},
                            "comparator": _enum(["best_simple", "t0_base", "accepted"]), "scope": _enum(cat.SCOPES),
                            "delta": {"type": "number", "enum": [0.0, 0.05, 0.1, 0.2]},
                            "evidence": {"type": "array", "items": {"type": "integer"}}}}
    batch = {"type": "object", "additionalProperties": False, "required": ["batch_version", "claims"],
             "properties": {"batch_version": {"type": "string", "enum": ["claims/0"]},
                            "claims": {"type": "array", "items": claim}}}
    return {"type": "object", "additionalProperties": False, "required": ["action", "note", "probe", "claim_batch"],
            "properties": {"action": {"type": "string", "enum": ["probe", "freeze", "stop"]}, "note": {"type": "string"},
                           "probe": {"anyOf": [probe, {"type": "null"}]},
                           "claim_batch": {"anyOf": [batch, {"type": "null"}]}}}


def system_prompt() -> str:
    return f"{RULES}\nObjective (from the owner):\n{OBJECTIVE}\n\n{cat.catalogue_brief()}\n"


def user_prompt(digest: dict, remaining: int, iteration: int, max_iterations: int) -> str:
    return (f"Iteration {iteration} of at most {max_iterations} in this chain. "
            f"Discovery budget left: {remaining} evaluations.\n\nLedger digest (JSON):\n{canonical_json(digest)}\n\n"
            "Choose the next action.")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokens_used_today(entries: list[dict], now: datetime) -> int:
    day = now.date().isoformat()
    total = 0
    for e in entries:
        if e.get("kind") == "research_call" and str(e.get("at", "")).startswith(day):
            u = e["payload"].get("usage") or {}
            total += int(u.get("input_tokens", 0)) + int(u.get("output_tokens", 0)) \
                + int(u.get("cache_read_input_tokens", 0)) + int(u.get("cache_creation_input_tokens", 0))
    return total


def _usage(resp) -> dict:
    u = getattr(resp, "usage", None)
    keys = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    return {k: int(getattr(u, k, 0) or 0) for k in keys}


def _text(resp) -> str:
    return "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")


def call_model(client, model: str, effort: str, system: str, messages: list[dict]):
    kwargs = dict(model=model, max_tokens=MAX_TOKENS, thinking={"type": "adaptive"},
                  output_config={"effort": effort, "format": {"type": "json_schema", "schema": action_schema()}},
                  system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}], messages=messages)
    return client.messages.create(**kwargs)


def decide(client, model: str, effort: str, entries: list[dict], *, iteration: int, max_iterations: int,
           remaining: int, now: datetime | None = None, token_cap: int = DEFAULT_TOKEN_CAP) -> tuple[dict, list[dict]]:
    """One research step: at most one call plus one repair retry. Returns (action, research_call payloads)."""
    now = now or datetime.now(timezone.utc)
    if iteration > min(max_iterations, HARD_MAX_ITERATIONS):
        return {"action": "stop", "note": "iteration cap reached", "probe": None}, []
    if tokens_used_today(entries, now) >= token_cap:
        return {"action": "stop", "note": f"daily token cap {token_cap} reached", "probe": None}, []
    digest = ledger.digest(entries)
    system, user = system_prompt(), user_prompt(digest, remaining, iteration, max_iterations)
    messages = [{"role": "user", "content": user}]
    calls: list[dict] = []
    for attempt in (1, 2):
        resp = call_model(client, model, effort, system, messages)
        text = _text(resp)
        record = {"iteration": iteration, "attempt": attempt, "requested_model": model, "served_model": getattr(resp, "model", None),
                  "request_id": getattr(resp, "_request_id", None), "stop_reason": getattr(resp, "stop_reason", None),
                  "usage": _usage(resp), "effort": effort, "ledger_head": ledger.head(entries),
                  "system_sha256": _sha(system), "user_sha256": _sha(user), "response_text": text[:20000]}
        calls.append(record)
        if record["stop_reason"] == "refusal":
            details = getattr(resp, "stop_details", None)
            record["refusal_category"] = getattr(details, "category", None) if details else None
            return {"action": "stop", "note": "the model refused; chain stopped", "probe": None, "error": "refusal"}, calls
        if record["stop_reason"] == "max_tokens":
            return {"action": "stop", "note": "response cut at max_tokens", "probe": None, "error": "max_tokens"}, calls
        try:
            action = json.loads(text)
            if action.get("action") == "probe":
                action["probe"] = validate_probe(action.get("probe"))
            elif action.get("action") == "freeze":
                b = action.get("claim_batch")
                if not isinstance(b, dict) or not isinstance(b.get("claims"), list) or not 1 <= len(b["claims"]) <= 4:
                    raise SpecError(["a freeze needs claim_batch with 1..4 claims"])
            elif action.get("action") != "stop":
                raise SpecError([f"unknown action {action.get('action')!r}"])
            record["action"] = action.get("action")
            return action, calls
        except (json.JSONDecodeError, SpecError, AttributeError) as exc:
            reasons = exc.reasons if isinstance(exc, SpecError) else [f"{type(exc).__name__}: {exc}"]
            record["invalid"] = reasons
            if attempt == 2:
                return {"action": "stop", "note": "invalid proposal after one repair", "probe": None,
                        "error": "invalid", "reasons": reasons}, calls
            messages = messages + [{"role": "assistant", "content": text},
                                   {"role": "user", "content": "The referee rejected that proposal:\n- "
                                    + "\n- ".join(reasons) + "\nReturn a corrected JSON object."}]
    raise AssertionError("unreachable")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m engine.researcher")
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--iteration", type=int, default=1)
    p.add_argument("--max-iterations", type=int, default=3)
    args = p.parse_args(argv)
    model = os.environ.get("RESEARCHER_MODEL", "").strip()
    if not model:
        print("::error title=RESEARCHER_MODEL not set::set the repository variable RESEARCHER_MODEL")
        return 1
    effort = os.environ.get("RESEARCHER_EFFORT", "").strip() or "high"
    cap = int(os.environ.get("RESEARCHER_TOKEN_CAP", "").strip() or DEFAULT_TOKEN_CAP)
    import anthropic

    from engine.referee.budget import remaining as budget_remaining

    entries = ledger.read(args.ledger)
    client = anthropic.Anthropic()
    action, calls = decide(client, model, effort, entries, iteration=args.iteration,
                           max_iterations=args.max_iterations, remaining=budget_remaining(entries), token_cap=cap)
    ctx = ledger.run_context("research")
    items = [ledger.pending("research_call", c, ctx) for c in calls]
    args.out.mkdir(parents=True, exist_ok=True)
    ledger.write_pending(args.out / "pending_research.jsonl", items)
    (args.out / "action.json").write_text(json.dumps(action, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if action.get("action") == "probe":
        (args.out / "spec.json").write_text(json.dumps(action["probe"], ensure_ascii=False) + "\n", encoding="utf-8")
    if action.get("action") == "freeze":
        (args.out / "batch.json").write_text(json.dumps(action["claim_batch"], ensure_ascii=False) + "\n", encoding="utf-8")
    kind = action.get("action") if not action.get("error") else "error"
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"action={kind}\n")
    print(json.dumps({"action": kind, "note": action.get("note"), "calls": len(calls)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
