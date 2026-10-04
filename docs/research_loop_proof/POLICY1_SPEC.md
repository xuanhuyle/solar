# policy1: a structured research-policy layer against the lesson-only researcher (frozen specification)

*Owner instruction: [`NEXT_POLICY_ARCHITECTURE_PROMPT.md`](NEXT_POLICY_ARCHITECTURE_PROMPT.md). Architecture note:
[`POLICY1_ARCHITECTURE.md`](POLICY1_ARCHITECTURE.md). This document is frozen before the preflight and the scored run.
The frozen files are listed in `research_loop_proof/policy1/truth/spec.py` (they include everything learn1's hash
covers), and their combined hash is `policy1_spec_sha`. The scored world's seed is derived from it, and the scored run
refuses unless the preflight passed under the same hash. beta1, learn1 and Phase 0 are unchanged; policy1 reuses their
code by import.*

## 1. Two conditions on the same world

**L (lesson only)** is learn1's learned condition, byte for byte:
- beta1's brief;
- the frozen beta1-derived lesson (`learn1/lab/lesson.json`, sha256 `1c38b101…`);
- beta1's schema and notebook.

**S (structured research policy)** is the same brief and the same lesson, plus only the research-state interface of
`POLICY1_ARCHITECTURE.md`:
- one "RESEARCH STATE" section in the system text, between the lesson and the schema;
- the extended schema:
  - `regime_assessment`;
  - at most three `decision_uncertainties`;
  - `budget_needs`;
  - per candidate: `freshness`, `evidence_type`, `last_scored_day` and `attribution`;
  - per experiment: `targets_uncertainty`, `possible_followup` and `budget_rationale`;
- its own earlier state rendered back in the notebook;
- code checks of the new fields (types, enums, lengths; an experiment must name a listed uncertainty), with the same
  single repair turn.

**Not encoded:** no rule, planner, quota, reserved experiment, forced split or forced single-variable test. The model
fills every field and chooses every experiment. No new prose lesson was given to S.

**Held fixed:**
- world, candidate ids, observations and confirmation data;
- model, effort and API interface;
- the menu, the 3 rounds and the 6-experiment budget (at most 3 per round);
- the 80k token cap;
- the instrument (beta1's pinned t0-beta, `tfc-t0` 0.5.0);
- the evaluation.

**Separation:** two parallel research jobs, identical except for the condition, each with its own record.

## 2. The world (beta1's family, unchanged)

beta1's world function: Phase 0's "phase_b" parameters and generator.
- **Candidates:** four anonymous candidates, R (retired), E (emerging), D (proxy of E) and N (noise), each with a
  random sign.
- **Change point:** τ = 86 + U{0..6}.
- **Days:** days 1–126 are observed; days 127–154 exist only in the evaluate job.

**Seeds:**
- scored world: `int(sha256('policy1:<policy1_spec_sha>:<run id>')[:16], 16)`;
- preflight world: `policy1-preflight:<run id>`.

## 3. Regression replays (non-scored engineering checks, not evidence)

**Run:** 37227665244 at commit `0660a3d` (branch `policy1/run-37227665244`).
- Both published worlds were regenerated, and their observed hashes equal the published ones.
- S replayed each run's first two rounds of recorded evidence, then made round 3 (one experiment left) and the final
  call.
- **Operational result:** PASS. The replayed results equal the published originals; there were 4 valid live calls, no
  refusal, no repair, and every prompt rebuilt.

**What the state represented** (contaminated by our knowledge of these worlds; never validation):
- **beta1 replay:**
  - X03 deteriorated, freshness possibly_stale;
  - X01 and X02 stale, "dated to the pre-change regime";
  - regime possible_change;
  - an explicit choice to re-screen rather than "re-confirming X03's decline";
  - after a positive pair, attribution marked unresolved.
- **learn1 replay:**
  - the positive group, with each member's evidence typed "grouped" and its attribution unresolved;
  - "Attribution (U2) … will stay unresolved" with one experiment left.

**No interface correction was made.** The replays are not targets to optimise.

## 4. Preflight (non-scored, operational only)

L and S run on the preflight world. Each must pass beta1's rule:
- all 4 calls valid;
- every experiment legal and run;
- no integrity failure;
- at most 1 refusal.

Each record's prompts must also rebuild from the record. The preflight passes only if both conditions pass. It is
never evaluated against roles and is not used to tune anything. If refusals occur, only the minimal correction is made,
and the preflight is repeated once.

## 5. Evaluation

**Integrity, per condition:**
- the observed-data hash;
- the system text equals the frozen text of that condition;
- every prompt rebuilt byte for byte from that condition's own record;
- experiments recomputed;
- the canary, the model hash, the guard and the job results.

**Evidence check:** R on days 57–84; E on days 99–112 (round 2); E on days 99–126 (round 3).

**Confirmation** (days 127–154, t0-beta and ridge):
- {E}, {R}, {D}, {N} and {E, D};
- R, D and N each given E;
- E given D;
- L's and S's final selections.

**Recorded round by round:**
- beliefs entering the round;
- experiments and results;
- updates;
- budget left.

For S, the structured state is kept verbatim. Also recorded:
- re-opened stale negatives;
- the first round with positive evidence for E;
- reconfirmations (a repeat of an earlier post-change sole test of the same candidate with the same reference);
- the last experiment's type;
- S's attribution entries after positive groups;
- S's unresolved uncertainties at the end.

**Indicators:**
- **found(c):** E selected, R and N not.
- **supported(c):** every selected candidate has support: its latest standalone test (the only covariate, no
  reference) or its latest conditional test (the only covariate, against a reference) had a lower bound above 0. A
  conditional test adds support but never cancels a positive standalone test. Several tests of one kind in the same
  call must all be positive, so the order in which they were listed does not matter.
- **essential loop(c):** found, supported, and c's selection beats no covariate on confirmation (t0-beta lower bound
  above 0).

## 6. Outcome (owner's labels; the first match wins)

| # | Outcome | Condition |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | an integrity issue, or a call of either condition without a valid response after its repair |
| 2 | ARCHITECTURE SIGNAL OBSERVED | (a) found(S) and not found(L); or (b) both found, supported(S) and not supported(L) |
| 3 | BOTH SUCCEED | both complete the essential loop |
| 4 | BOTH FAIL | neither completes the essential loop |
| 5 | NO ARCHITECTURE SIGNAL | anything else |

**The link to the structured state** holds by construction: the conditions differ only by it, and every S experiment
names the uncertainty it targets. The report quotes the fields.

**Always reported:**
- one world and one stochastic trajectory per condition, which is an existence test, not a rate;
- forecast accuracy alone is not an architecture signal;
- whether E's evidence was present.

**No reroll.** One scored paired world. A rerun is the owner's decision.

## 7. The one pre-run check

One focused check (workflow `wf_23ad1c7f-838`, 5 checkers, each finding verified by a skeptic) covered the owner's five
items. Truth leakage, cross-condition contamination, prompt differences beyond the architecture and future-data leakage:
nothing found. Evaluator: one defect was confirmed and corrected before any preflight or scored world existed (in
`evaluate.py` and this spec, so it changed `policy1_spec_sha`). Support had taken the latest sole test with or without
a reference, so a later conditional attribution test (for example E given its proxy), or the listing order within a
call, could cancel a positive standalone test. That biased the reading against the condition more likely to run
attribution tests. A second finding was judged real but below the bar, because it affects only a descriptive row:
reconfirmations ignored the reference, so a conditional attribution test counted as a redundant reconfirmation. It was
corrected in the same change.
