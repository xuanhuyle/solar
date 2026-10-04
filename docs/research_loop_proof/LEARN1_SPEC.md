# learn1: a lesson from beta1, then one hidden world researched fresh and with the lesson (frozen specification)

*Owner instruction: [`NEXT_LEARNING_MILESTONE_PROMPT.md`](NEXT_LEARNING_MILESTONE_PROMPT.md). This document is frozen
before the preflight and the scored run. The frozen files are listed in `research_loop_proof/learn1/truth/spec.py`,
and their combined hash is `learn1_spec_sha`. That list includes the lesson and every file beta1's own hash covers. The
scored world's seed is derived from `learn1_spec_sha`, and the scored run refuses unless the preflight passed under the
same hash. beta1 and Phase 0 (specs, results, verdicts, branches) are unchanged; learn1 reuses their code by import.*

## 1. The lesson

**Source:** the beta1 scored record only: branch `beta1/run-37201189113`, `ai.json` with sha256 `901658e8…` pinned in
`learn1/lesson.py` and checked against the branch manifest.

**Input to the one lesson call** (built in code, rebuildable byte for byte):
- the beta1 notebook as the researcher saw it, all four calls (Phase 0's `render_call`). The last entry is the final
  call, with the final selection and the conclusion;
- the owner's evaluator feedback, verbatim: "The process changed. A candidate rejected on pre-change evidence became
  strongly predictive after the change. The researcher detected deterioration in the previously useful relationship
  but did not re-test candidates rejected under the earlier regime, so it missed the emerging signal."

It received nothing about the next world: no seed, no candidate mapping, no data and no answer. None of these could
exist yet, because the next world's seed hashes the frozen lesson.

**System text:** the owner's section 3 output requirements, restated:
- one lesson of at most 1,000 characters;
- a general principle, not a benchmark-specific instruction;
- in its own words, the distinction between "unhelpful under one regime" and "will remain unhelpful after the system
  changes";
- it may recommend how budgets respond when an established relationship deteriorates;
- no candidate ids, no days or numerals, no future-problem structure, no fixed experiment sequence.

**The call:**
- the pinned researcher model, checked by the sha256 of its id, which is never written;
- effort `high`, adaptive thinking, JSON schema `{"lesson": string}`;
- beta1's attempt record.

**Code checks:** non-empty, at most 1,000 characters, no `X\d+`, no digit. One repair turn is allowed. Without a valid
lesson after it, the milestone stops with LESSON DISTILLATION FAILURE.

**Record:** the exact system text and user prompt, every response, the model hashes, usage, refusal details and the
lesson's hash. They are on branch `learn1/run-<lesson run>` and copied unchanged to
`docs/research_loop_proof/learn1_lesson_record.json`. The lesson itself is copied byte-identical to
`research_loop_proof/learn1/lab/lesson.json`. It is never edited.

**The lesson call** was run 37216965299 at commit `94c46fe` (branch `learn1/run-37216965299`). It returned a valid
lesson on the first attempt (`end_turn`, no refusal, no repair; 4,500 input and 259 output tokens; the served model's
hash equals the pin).

**The frozen lesson** (896 characters, sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`), verbatim:

> When a relationship you relied on starts to decay, treat that as evidence that the system itself may have changed. A change in the system invalidates negative findings as much as positive ones. A null result describes one regime only. It says a factor did not help under the conditions in which it was tested. It does not say the factor will stay unhelpful once those conditions have shifted. If you see drift, mark every earlier rejection as provisional and dated, not settled. Then move budget away from repeatedly confirming the decline of the old favourite and towards re-screening previously dismissed factors on the most recent data, where an emerging signal would first show. Concluding that nothing works is safe only if every option has been examined after the change. Before calling a field empty, check whether your absence of evidence comes from the current regime or an outdated one.

## 2. Two researcher conditions on the same world

**F (fresh)** is beta1's researcher exactly. Its system text equals beta1's (brief plus schema; same sha256 as the
beta1 scored run).

**L (learned)** is the same researcher. Its system text is beta1's with one section inserted between the brief and the
schema:

```
PRIOR RESEARCH LESSON (distilled from an earlier, separate investigation)
<the frozen lesson, verbatim>
```

L never receives beta1's notebook.

**Held fixed between F and L:**
- the hidden world, candidate ids, observations and confirmation data;
- model, effort, API interface and response schema;
- user and repair prompts (a pure function of each condition's own record);
- the menu, 3 rounds and the 6-experiment budget (at most 3 per round), the 80k token cap;
- the evaluation.

**No policy code:** nothing acts on the lesson. There are no quotas, no reserved experiments and no forced re-screens.

**Separation:** the two researchers run in two parallel jobs, identical except for the condition. Each has its own
record, and neither sees the other's experiments or conclusions.

## 3. The world (beta1's family, unchanged)

beta1's world function: Phase 0's "phase_b" parameters and the frozen generator.
- **Candidates:** four anonymous candidates, X01–X04: R (retired at the change), E (emerging), D (`0.8·E +
  0.6·independent`, no causal effect) and N (noise). Each has a random observed sign.
- **Change point:** τ = 86 + U{0..6}.
- **Days:** days 1–126 are observed; days 127–154 exist only in the evaluate job.
- **Instrument:** t0-beta, unchanged (beta1's pinned bytes, `tfc-t0` 0.5.0).

**Seeds:**
- scored world: `int(sha256('learn1:<learn1_spec_sha>:<run id>')[:16], 16)`;
- preflight world: `int(sha256('learn1-preflight:<run id>')[:16], 16)`.

## 4. Preflight (non-scored, operational only)

Both conditions run on the preflight world, each under beta1's preflight rule:
- all 4 calls end with a valid response;
- every experiment is legal and ran;
- no integrity failure;
- at most 1 refusal.

The preflight passes only if both conditions pass. It is never evaluated against roles. If refusals occur, the
category is read, only the minimal prompt or interface correction is made (never to the lesson), and the preflight is
repeated once. A second failure ends the milestone with INFRASTRUCTURE FAILURE.

## 5. Evaluation

**Integrity, per condition:**
- the observed-data hash;
- the system text equals the frozen text of that condition;
- every user and repair prompt rebuilt byte for byte from that condition's own calls;
- every experiment recomputed with t0-beta;
- the canary, the model hash, the guard and the job results.

**Evidence check** (t0-beta, against no covariate): R on days 57–84; E on days 99–112 (available in round 2); E on
days 99–126.

**Confirmation** (days 127–154, t0-beta and ridge):
- {E}, {R}, {D}, {N} and {E, D}, each against no covariate;
- R, D and N each given E;
- E given D;
- F's and L's final selections, against no covariate.

**Round by round, for each condition:**
1. statuses entering the round;
2. experiments;
3. results (scored days relative to τ);
4. status changes;
5. budget left;
6. and 7. stale negatives re-opened, with the researcher's reason;
8. emerging driver found;
9. retired driver removed;
10. noise avoided;
11. final selection.

Mentions of the lesson are also recorded. Verbosity is not scored.

**Indicators:**
- **found(c):** E selected, R and N not.
- **first_e_round(c):** the first round (2 or 3) with an experiment including E whose lower bound is above 0.
- **reopened(c):** round 2–3 experiments including a candidate whose every earlier result was scored before τ with a
  lower bound at or below 0.
- **reconfirmations:** experiments testing R alone after an earlier post-change result for R alone (reported only).
- **lesson mentions:** notes, reasons, because or conclusion containing "lesson" or "prior research".
- beta1's B1–B10 and beta1's verdict map, applied to each condition separately. Row 3 is "the essential loop".

## 6. Outcome (owner's labels; the first match wins)

| # | Outcome | Condition |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | any of: an integrity issue; a call of either condition without a valid response after its repair |
| 2 | LEARNING SIGNAL OBSERVED | L did better than F (see below) **and** the improvement is linked to the lesson |
| 3 | BOTH SUCCEED | both conditions meet beta1's row 3 (BASIC AUTONOMOUS LOOP OBSERVED) |
| 4 | BOTH FAIL | neither condition found E |
| 5 | NO LEARNING SIGNAL | anything else |

**L did better than F** if any of:
- (a) found(L) and not found(F);
- (b) both found, and first_e_round(L) < first_e_round(F);
- (c) reopened(L) and not reopened(F), unless F found E and L did not.

**Linked to the lesson** means any of:
- L mentions the lesson;
- the improvement is (c);
- L re-opened E itself.

**Always reported:**
- one world and one stochastic trajectory per condition make this an existence test, not a rate. A difference can
  arise by chance;
- a forecasting gain alone is not a learning signal;
- whether E's evidence was present in this world.

**No reroll.** One scored paired world. A rerun is the owner's decision.
