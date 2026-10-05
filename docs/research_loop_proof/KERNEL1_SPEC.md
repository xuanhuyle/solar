# Kernel1: a direct frozen test of the current autonomous researcher kernel (frozen specification)

*Owner instruction: [`NEXT_KERNEL_PROOF_PROMPT.md`](NEXT_KERNEL_PROOF_PROMPT.md). This document is frozen before the
preflight and the scored run. The frozen files are listed in `research_loop_proof/kernel1/truth/spec.py`: this
document, Kernel1's truth files and workflow, beta1's preflight check and everything discovery1's hash covers. Their
combined hash is `kernel1_spec_sha`; the twelve scored worlds' seeds and kinds are derived from it, and the scored run
refuses unless the preflight passed under the same hash. Phase 0, beta1, learn1, policy1, discovery1 and human1 are
unchanged.*

## 1. The frozen question

> Does the current autonomous researcher kernel, unchanged, reliably discover useful predictive information in a
> non-trivial hidden hypothesis space, reject false information, adapt when relationships change, and support its
> conclusions with experiments that survive unseen confirmation?

The answer is one of `KERNEL PROVEN FOR THIS BENCHMARK` or `KERNEL NOT PROVEN`, unless infrastructure or benchmark
invalidity prevents a scientific reading. "Proven" means demonstrated against this frozen synthetic benchmark at the
predeclared thresholds; it says nothing about arbitrary research problems, real markets or commercial value. The
question is about predictive information, not causation. There is no comparator arm: ridge appears only as context.

## 2. The kernel: Discovery1's researcher L8, unchanged

Each research job runs Discovery1's research job itself, not a copy:

    python -m research_loop_proof.discovery1.lab.run weights --weights W
    python -m research_loop_proof.discovery1.lab.run loop --observed F --observed-sha S --weights W --out OUT

Kernel1 has no lab code. Everything the researcher is made of is therefore unchanged and covered by this spec's hash
through discovery1's frozen list:
- learn1's lesson-only researcher, with the frozen beta1-derived lesson (`learn1/lab/lesson.json`, sha256
  `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`);
- the L8 system text (sha256 `78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d`, the value recorded in
  Discovery1's scored run `discovery1/run-37238629496`);
- the pinned model and effort, X01-X08, the experiment menu, beta1's pinned t0-beta with a 7-day context;
- three rounds (days 1-84, 1-112, 1-126) and a final call, 6 experiments in total with at most 3 per round, one repair
  turn per call, the 80k token cap, and the notebook and belief table.

Discovery1's comparator step is not run.

## 3. The twelve worlds (`truth/world.py`)

**Base.** Every world starts from discovery1's `make_world8(seed)`. That is the frozen Phase 0 generator:
- 154 days, with the change on day τ = 86 + U{0..6};
- linear effect strength m = 2;
- the candidates R, E, D = 0.8·E + 0.6·independent, and N1-N5, each standardised on days 1..τ-1 with a random
  observed sign;
- a seeded permutation of the eight roles to X01-X08.

Only the target differs between kinds. Let c = √(0.75·m), z_R and z_E be the standardised R and E series, and
"before" mean the hours of days 1..τ-1:

| kind | target | meaning |
|---|---|---|
| change | Discovery1's target, unchanged: c·z_R before τ, c·z_E from τ | R retires at the change, E turns on, D is E's proxy, N1-N5 are irrelevant |
| stable | y − c·where(before, z_R, z_E) + c·z_R | R is predictive throughout research and confirmation; E never turns on; D is only E's proxy; N1-N5 are irrelevant |
| null | y − c·where(before, z_R, z_E) + c·z_U | no candidate has any effect on the target |

**What stays the same across kinds:**
- z_U is an unobserved series, drawn the way a candidate is drawn, from the seed's eighth child stream (make_world8
  uses the first seven, which are unchanged), and standardised on days 1..τ-1.
- z_U is never exported. It keeps the null target's scale equal to the other kinds' (without it the null target's
  variance would be about half). Every candidate effect is zero.
- The candidate arrays, the τ draw (in stable and null worlds only the standardisation window) and the id permutation
  are identical for every kind of a given seed.
- Pre-change standardisation encodes τ in every kind's candidates alike. The researcher sees no raw values.

**Composition and seeds:**
- The twelve scored worlds w01-w12 are 8 change, 2 stable and 2 null.
- The kinds are assigned by a permutation seeded with `int(sha256('kernel1:<kernel1_spec_sha>:<run id>:types')[:16],
  16)`.
- World seeds are `int(sha256('kernel1:<kernel1_spec_sha>:<run id>:<world id>')[:16], 16)`.
- No world or kind can be previewed before the scored run is dispatched.
- The non-scored preflight is one change world, `kernel1-preflight:<run id>`, as w01.

## 4. Truth separation and integrity

**Observe** exports, per world, days 1-126 of the target and X01-X08 (`<world>/observed.npz`), with neutral metadata
only: world id, keys, days and array hash. There is no spec hash, run id or kind. Each world is its own artifact
(`kernel1-observed-<world>`), and research job `research_<world>` downloads only its own. Days 127-154, the roles, the
kind, the seed and the change day never leave the truth side.

**Each research job:**
- has a sparse checkout without any `*/truth/` package (Phase 0, beta1, learn1, policy1, discovery1, human1, Kernel1)
  or `tests/`;
- runs a guard that checks they are absent, greps for generator code, records the run attempt in `guard.json`, then
  removes `.git`;
- holds the API key only in the loop step, with t0-beta offline;
- has a workflow step that writes `timing.json` (loop wall time).

Isolation comes from the workflow code; as in every earlier milestone, any job's runtime token could fetch any artifact
of its run. The research jobs run in three waves of four (w01-w04, w05-w08, w09-w12), each wave after the previous
one, whatever its outcome.

**No reroll.** The scored run refuses unless all of the following hold:
- it is the run's first attempt (`GITHUB_RUN_ATTEMPT` = 1);
- there is a published preflight PASS under the same hash;
- no published `kernel1/run-*` branch carries a scored verdict.

A research record from any attempt other than 1 is a material integrity failure. If the evaluate job fails on its
runner, only evaluate may be re-run, over the same artifacts; it is deterministic and the re-run is reported. An
evaluator code defect found after the worlds exist is a BENCHMARK FAILURE, never fixed and rescored. Every dispatch of
this workflow (preflight and scored) is listed in the results.

**Material integrity failures** (programme row 1), in any world:
- the observed-data hash differs between regenerated, shipped and declared;
- the guard did not confirm the truth absent, or the record comes from a run attempt other than 1;
- the research job recorded a crash, or an integrity failure other than an API outage;
- the system text is not the frozen L8 text with its pinned sha;
- any prompt cannot be rebuilt byte for byte from the record;
- the requested or served model is not the pinned one;
- an experiment's result differs when recomputed on the observed data (Phase 0's tolerance 1e-4);
- **poison test:** an experiment's result changes when recomputed on the regenerated full 154-day data with the target
  and all candidates after its call's cutoff replaced (by +1e6, then by NaN). Round-3 experiments are included;
- a canary of any of the twelve worlds appears in a research file;
- the lesson differs from its pin;
- the t0-beta weights differ from their pins (refused at load).

**Missing final response.** A world lacks a valid final researcher response when any of these holds:
- its final call ended without a valid response after the repair;
- its job recorded a failure whose error starts exactly `IntegrityError: API outage:` (the existing retries
  exhausted);
- its job ended without a record after a confirmed guard.

More than one such world is programme row 1. Exactly one fails that world. Calls before the final call without a valid
response are reported, not scored.

**Generator self-check.** Each world's candidates, τ and ids must equal make_world8's, and its target must follow its
kind's construction (tolerance 1e-9). A failure, or a batch composition other than 8/2/2, is a confirmed generator
defect.

## 5. Informativeness and the oracle set (evaluator only, t0-beta, the lab's 7-day context)

**Change world informative** when both hold:
- E alone vs no covariate has a 95% lower bound above 0 on days 99-112 (the 14-day window at cutoff 112) or days
  99-126 (the 28-day window at cutoff 126), Discovery1's windows; and
- an oracle set exists.

**Stable world informative** when both hold:
- R alone vs no covariate has a lower bound above 0 on days 57-84, 85-112 or 99-126 (28-day windows at cutoffs 84,
  112, 126); and
- an oracle set exists, meaning R alone has a lower bound above 0 on confirmation.

**Null worlds** are always scored.

**Oracle set.** Confirmation runs over days 127-154: the 28-day window at cutoff 154, on the full data, vs no
covariate.
- Change: among {E}, {D} and {E, D}, those with a lower bound above 0. The oracle is the one with the lowest candidate
  MAE; ties go to the smaller set, then the sorted ids.
- Stable: {R}.

**Oracle fraction** = the final set's confirmation skill ÷ the oracle set's. It is 0 when the final set cannot be
confirmed: no valid final response, an empty set, or more than 4 candidates (the lab's limit; such a set holds at least
2 noise candidates).

**Reported only:**
- confirmation of {E}, {D}, {R}, {E, D}, D given E, E given D and R given E;
- ridge confirmation (context only);
- the researcher's selection.

## 6. Support by the researcher's own evidence (`truth/rules.py`)

**Current regime.** An experiment is current-regime when:
- in a change world, its first scored day is on or after τ. That means every window at cutoff 112 or 126 except the
  28-day window at 112, whose days 85-112 straddle the change;
- in a stable or null world, always.

Any legal window counts, since the owner's rule sets no window limit. Experiments are read in notebook order.

**F is supported** when one of these holds:
- **direct, set:** a current experiment has covariates exactly F, any legal reference, and a lower bound above 0;
- **direct, members:** for every member f of F, a current experiment has covariates exactly [f], any reference, and a
  lower bound above 0;
- **elimination:** a current experiment X on a covariate set S, a proper superset of F, with any reference and a lower
  bound above 0; and, for every z in S \ F, a current experiment Y **from a later call than X** such that:
  - z is among Y's covariates;
  - Y's covariates lie within S \ F;
  - Y's reference is non-empty and lies within F;
  - Y's lower bound is at or below 0.

  For example: {E, R} positive, then R given E null, supports {E}. Experiments of the same call are designed together,
  so neither is "later".

The first qualifying experiments in notebook order form the reported chain. An empty F is not supported. Neither the
hidden truth nor confirmation ever supports or rescues a conclusion.

## 7. Per-world success (owner section 8)

Every world first needs a valid final response (criterion 0). "Pure noise" means the roles N1-N5.

| kind | all of |
|---|---|
| change | (1) informative; (2) final selection non-empty; (3) R absent; (4) no N1-N5; (5) supported by its own current-regime evidence (section 6); (6) the selection's confirmation skill vs no covariate has a lower bound above 0; (7) oracle fraction ≥ 0.70 |
| stable | (1) informative; (2) non-empty; (3) no N1-N5; (4) supported; (5) confirmation lower bound above 0; (6) oracle fraction ≥ 0.70 |
| null | (1) final selection empty; (2) no final belief status `accepted`; (3) no candidate presented as established |

**Notes on the criteria:**
- D may be selected in a change world.
- In a stable world, E or D selected is reported as a zero-effect extra but is not "pure noise".
- A stable world's R wrongly declared deteriorated is reported, not failed.
- **Null criterion 3, the frozen reading:** the researcher's formal conclusion is its final belief statuses and its
  final selection, so criterion 3 holds when no candidate is accepted or selected. "Promising" or another uncertain
  status is allowed. The prose conclusion is quoted verbatim, and its sentences naming a candidate are flagged; the
  flag is descriptive only.
- "False accepted" means the final status `accepted` in a null world.

## 8. Programme reading (first match)

1. **INFRASTRUCTURE FAILURE:** any material integrity failure, or more than one world without a valid final response.
2. **BENCHMARK FAILURE:** any of:
   - fewer than 6 of the 8 change worlds are informative;
   - either stable world is not informative;
   - a confirmed generator or evaluator defect.
3. **KERNEL PROVEN FOR THIS BENCHMARK:** all of:
   - at least 6 of the 8 change worlds succeed;
   - both stable worlds succeed;
   - both null worlds succeed;
   - the median oracle fraction over the informative non-null worlds is ≥ 0.80 (for an even count, the mean of the
     middle two);
   - at most 1 informative non-null world has any N1-N5 in its final selection;
   - there are 0 accepted candidates across the null worlds.
4. **KERNEL NOT PROVEN:** every other scientifically valid result.

There is no MIXED. Closing lines:
- rows 1 and 2: `BENCHMARK/INFRASTRUCTURE RESULT ONLY`;
- row 3: `MOVE THE CURRENT KERNEL TO A REAL-WORLD RESEARCH TEST`;
- row 4: `STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL`.

## 9. Process

1. One focused independent pre-run check (no swarm). Confirmed defects are fixed before any scored world exists, and
   the spec is re-pinned.
2. One non-scored preflight. It checks:
   - 4 valid calls, at most 1 refusal and no failure;
   - legal experiments over X01-X08, and every belief table enumerating X01-X08;
   - the frozen system text, every prompt rebuilt, and the guard (truth absent, first attempt).

   Its roles are never read and nothing is tuned from it.
3. One scored dispatch of the twelve worlds, evaluated once. No reroll, no second batch, no threshold change, no
   comparator.

## 10. Reporting

**Per world:**
- kind, roles and change day (revealed only in evaluate);
- the informativeness checks;
- every experiment in order, with its role labels and current-regime flag;
- belief changes;
- the first current experiment containing useful information (E or D in a change world, R in a stable world);
- the final selection;
- support and its chain;
- R's treatment; any pure noise selected; E and D;
- the selection's confirmation with its interval; the oracle set and fraction;
- success or the exact failed criteria;
- API attempts, refusals, repairs and tokens;
- t0-beta forecasts and wall time.

**Aggregate:**
- change success count; stable and null success counts;
- useful-information recall; R retention; pure-noise selections; null false accepts;
- the oracle fractions and their median;
- experiment usage; cost.

**Descriptive only:**
- reopened stale negatives (learn1's rule);
- conditional or separation experiments (a non-empty reference, or a later proper subset of an earlier multi-candidate
  set);
- all six experiments used;
- later citations of an earlier experiment with a lower bound at or below 0.
