# Discovery1: the lesson-only researcher in eight-candidate worlds, three frozen worlds (frozen specification)

*Owner instruction: [`NEXT_DISCOVERY_MILESTONE_PROMPT.md`](NEXT_DISCOVERY_MILESTONE_PROMPT.md). This document is frozen
before the preflight and the scored run. The frozen files are listed in `research_loop_proof/discovery1/truth/spec.py`
(they include everything learn1's hash covers), and their combined hash is `discovery1_spec_sha`. The three scored
worlds' seeds are derived from it, and the scored run refuses unless the preflight passed under the same hash. Phase 0,
beta1, learn1 and policy1 are unchanged; Discovery1 reuses their code by import.*

**The question:** can the existing researcher discover newly useful predictive information when there are too many
candidates to test each one individually within its six-experiment budget?

## 1. The world: Phase 0's family with eight anonymous candidates

**Kept from beta1, learn1 and policy1, unchanged:** Phase 0's frozen generator with the "phase_b" parameters.
- 154 days; the hidden change on day 86 + U{0..6}; the same target and effect calibration (m = 2);
- a retired driver R and an emerging driver E (linear), each with a random observed sign;
- days 1–126 observed; days 127–154 exist only in the evaluate job.

**The candidates** (`truth/world.py`), eight in all:
- R, E and D (D = 0.8·E + 0.6·independent: a correlated proxy of E with no causal effect), as before;
- five independent noise candidates: the base world's noise candidate (N1), plus N2–N5 drawn the same way as every
  other candidate from new child streams of the same seed, standardised on pre-change days, with random signs.

The target depends only on R and E, so it is the base world's target bit for bit. A seeded permutation maps the eight
roles to X01–X08 in every world. The research job never receives the roles.

**Seeds:**
- scored worlds w1, w2, w3: `int(sha256('discovery1:<discovery1_spec_sha>:<run id>:w<k>')[:16], 16)`;
- preflight world: `discovery1-preflight:<run id>`.

## 2. The researcher L8: learn1's L, adapted only mechanically

**Unchanged from learn1's lesson-only condition L** (the strongest current researcher after policy1):
- beta1's brief and the frozen beta1-derived lesson (`learn1/lab/lesson.json`, unchanged), in the same labelled
  section between the brief and the schema;
- Phase 0's user and repair prompts and notebook (they never name the candidates);
- one repair turn per call; four calls; the pinned model and effort; the 80k token cap;
- the menu: 1 to 4 covariates, a disjoint reference of 0 to 2, a window of the last 7, 14 or 28 revealed days;
- 3 rounds (days 84, 112, 126), then a final call; 6 experiments in total, at most 3 per round;
- the instrument: beta1's pinned t0-beta (`tfc-t0` 0.5.0), 7-day context, the same result fields.

**The mechanical adaptation, and nothing else:**
- the brief's candidate sentence names eight candidates, X01–X08, instead of four;
- the brief's beliefs line says "(X01-X08)" instead of "(X01-X04)";
- the schema's candidate-id enums and the code checks use X01–X08.

Tests check that L8's system text maps back to learn1's L text exactly once these substitutions are reversed, and that
every adapted function is Phase 0's with the id substitution only. No new advice and nothing derived from policy1.

## 3. The fixed comparator (`lab/comparator.py`)

One simple group-screen/split policy. It was frozen before any scored world existed and has not been optimised.
It uses the same lab, menu, rounds and budget as L8: 6 experiments, each against no covariate on the last 28 revealed
days.

| Round | Experiments | Rule |
|---|---|---|
| 1 (days 1–84) | A = X01–X04; B = X05–X08 | — |
| 2 (days 1–112) | A; B | W = the group with the higher round-2 skill (A on a tie); the round-1 screen is superseded |
| 3 (days 1–126) | W's first two ids; W's last two ids | — |
| Final | — | every candidate of a round-3 half whose lower bound is above 0 |

It resolves candidates to pairs only. It can therefore succeed (section 5) only where E's pair partner is D. The
research job runs it on the observed data, and the evaluator recomputes it.

## 4. The batch

- One scored run: three independent hidden worlds from this frozen specification.
- The same L8 and the same comparator on all three. No lesson or prompt change between worlds, no reroll, and no
  tuning after any result.
- Three research jobs, identical except for the world, each without any truth on disk.

**Preflight** (one non-scored world, operational only). It must show:
- 4 valid L8 calls and every experiment legal over X01–X08;
- at most 1 refusal;
- every belief table enumerating exactly X01–X08;
- the system text equal to the frozen text, and every prompt rebuilt from the record;
- the comparator's 6 experiments following its rule;
- the guard confirmed.

It is never evaluated against the world's roles and is not used to tune anything. If it fails on refusals, only the
minimal correction is made and it is repeated once.

## 5. Evaluation, per world

**Integrity:**
- the observed-data hash;
- L8's system text equal to the frozen text;
- every prompt rebuilt byte for byte from that world's record;
- every L8 experiment recomputed from that world's observed data;
- the comparator recomputed: the same experiments, results and selection;
- the canaries of all three worlds, the model hash, the guard and the job results.

**Detectability, decided first.** t0-beta, E alone against no covariate, on the observed post-change windows: days 99–112
(round 2) and days 99–126 (round 3). The world is **informative** if either lower bound is above 0. Otherwise it is
uninformative for researcher competence, and no success or failure is counted in it.

**Reported for L8 and for the comparator** (the six criteria are listed under Success below):
- the experiments used;
- the first experiment E entered;
- whether E was tested after the change;
- whether E was distinguished from its group companions: a round 2–3 experiment with E as the only covariate and a
  lower bound above 0;
- whether R was removed;
- any noise candidate selected;
- D: whether it was selected, the researcher's experiments including D, D alone and D given E on confirmation;
- the final selection and its confirmation skill;
- re-opened stale negatives and lesson mentions (L8);
- token and API cost.

**Confirmation** (days 127–154; t0-beta, with the matched ridge for context only):
- {E}, {R}, {D} and {E, D};
- D given E, E given D, R given E;
- both final selections.

**Success** (the owner's six criteria, applied alike to L8 and the comparator):
1. E was detectable (the world is informative).
2. E was among the covariates of a round 2–3 experiment. Every round 2–3 window ends after the change.
3. E is in the final selection.
4. R and all five noise candidates are absent from the final selection. D may be selected; the report separates its
   proxy value from its increment given E.
5. Supporting evidence of its own: a round 2–3 experiment with a lower bound above 0 that has either E as its only
   covariate (with or without a reference), or exactly the final selection as covariates and no reference.
6. The final selection beats no covariate on the confirmation days (t0-beta lower bound above 0). An empty selection
   fails this criterion. So does a selection of more than 4 candidates: the lab cannot score it (its at-most-4 rule), so
   it is reported as not scored. Such a selection holds at least three of R and the noise candidates, so it fails
   criterion 4 anyway.

## 6. Programme reading (the owner's labels; the first match wins; never reinterpreted)

| # | Reading | Condition |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | an integrity issue, or an L8 call without a valid response after its repair, in any world |
| 2 | BENCHMARK FAILURE | fewer than 2 informative worlds |
| 3 | DISCOVERY SIGNAL | L8 succeeds in at least 2 informative worlds, and in more of them than the comparator |
| 4 | BOTH SUCCEED | L8 and the comparator each succeed in at least 2 informative worlds |
| 5 | NO DISCOVERY SIGNAL | L8 fails in at least 2 informative worlds |
| 6 | NO DISCOVERY SIGNAL | predeclared fallback, the only case rows 1–5 leave: exactly 2 informative worlds, and L8 succeeds in 1 of them, so not in at least 2 |

**BENCHMARK FAILURE also covers a demonstrable scientific-design defect** (an error in the world, lab or evaluator) that
prevents interpretation. Such a defect would be reported with its evidence, never inferred from a disliked outcome.

**Closing line, predeclared:**

| Reading | Closing line |
|---|---|
| DISCOVERY SIGNAL | MOVE TO A REAL-WORLD RESEARCH TEST |
| NO DISCOVERY SIGNAL | NARROW TO HUMAN-SUPPLIED HYPOTHESES |
| BOTH SUCCEED | BENCHMARK/INFRASTRUCTURE RESULT ONLY (the benchmark did not separate adaptive research from fixed search) |
| BENCHMARK FAILURE or INFRASTRUCTURE FAILURE | BENCHMARK/INFRASTRUCTURE RESULT ONLY |

**Always reported:**
- three worlds with one stochastic trajectory each: a small batch, not a rate;
- forecast accuracy alone is not discovery;
- the comparator's pair-resolution limit.

## 7. The one pre-run check

One focused check (a single agent, read-only) covered five items:
- truth leakage;
- prompt differences beyond the mechanical adaptation;
- future-data leakage inside experiments;
- world-family fidelity;
- evaluator reproducibility.

Nothing was found for the first four. One inherited property was noted and is not a defect: every candidate is
standardised on the pre-change days, as in Phase 0, beta1, learn1 and policy1. The change day can therefore be
recovered from the raw observed arrays, but the researcher never sees raw data and the comparator does not use them.

**Evaluator: one defect, confirmed and corrected** before any preflight or scored world existed. The correction is in
`evaluate.py` and in criterion 6 of this spec, so it changed `discovery1_spec_sha`.
- **The defect:** a valid L8 final selection of 5 to 8 candidates stopped the evaluation, because the confirmation goes
  through the lab's at-most-4 rule. That would have lost the scored batch, with no possible re-run.
- **The correction:** such a selection is now reported as not scored and fails criterion 6.
- **Why no reading changes:** such a selection fails criterion 4 regardless.
