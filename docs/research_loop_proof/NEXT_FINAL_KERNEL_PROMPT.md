# Final kernel proof — context, cheap trials, referee, memory

Read current HEAD, especially:
- docs/experiment_5/NORTH_STAR_CLARIFICATION.md
- docs/research_loop_proof/LEARN1_RESULTS.md
- docs/research_loop_proof/HUMAN1_RESULTS.md
- docs/research_loop_proof/KERNEL1_SPEC.md
- docs/research_loop_proof/KERNEL1_RESULTS.md
- research_loop_proof/discovery1/
- research_loop_proof/kernel1/
- current PR #3.

This is the final synthetic test of the **product kernel**.

Preserve Kernel1 as a valid result: the context-free, memory-light L8 researcher was not proven as an anonymous search-and-adjudication engine. Do not reinterpret or rescue that result.

The product kernel being tested here is:

> company/domain context + AI researcher + covariate-capable forecasting foundation model as a cheap experimental instrument + deterministic scientific referee + accumulated validated research knowledge.

The final question is:

> When the researcher has realistic company context and can accumulate validated empirical knowledge across related investigations, can the full loop repeatedly turn cheap covariate trials into scientifically valid predictive findings, and does accumulated knowledge materially improve later research versus the same researcher starting fresh?

The scored result must be binary:
- FULL KERNEL PROVEN FOR THIS BENCHMARK
- FULL KERNEL NOT PROVEN

Infrastructure/benchmark invalidity may prevent a scientific reading. There is no MIXED and no further synthetic milestone.

## 1. Keep the foundation-model thesis correct

Do not test whether t0-beta is a better forecasting model than ridge/ARX/boosting.

The relevant hypothesis is that a pretrained covariate-capable forecaster makes the marginal experiment “does this information help?” cheap because the same generic instrument can test many covariate sets without fitting a new task-specific forecasting model for every hypothesis.

Use pinned t0-beta as the experiment instrument. No task-specific model fitting is allowed in the research path.

Report experiments, t0 forecast calls/forecast-days, runner time, API calls/tokens, validated findings per experiment and per runner-minute. Do not use conventional-model forecast accuracy as a pass/fail gate and do not claim this benchmark measures the full human/engineering cost counterfactual.

## 2. Research policy: no Kernel1 repair

Use Discovery1's L8 researcher as the policy base:
- same pinned researcher model/effort;
- byte-identical L8 system text (sha beginning 78fb0061);
- same frozen learn1 lesson (sha beginning 1c38b101);
- X01-X08 experiment API;
- same t0-beta context;
- 3 rounds plus final call;
- 6 experiments total, max 3/round;
- same repair/token rules.

Do not add methodological advice from Kernel1. In particular do not tell it to split groups, test candidates individually, perform conditional decomposition, avoid noise, or save budget for attribution.

The only new inputs are **data**:
1. current company context;
2. validated research memory.

Keep the L8 system text byte-identical. Add context/memory to the user prompt as clearly labelled data, not new methodological instructions.

## 3. Full loop

A. Researcher chooses hypotheses/tests.

B. t0-beta executes declarative covariate experiments with no task-specific training.

C. Deterministic referee adjudicates only evidence the researcher actually generated. It may approve individual, conditional, set-level, negative, or “attribution unresolved” findings. A positive group test cannot become unsupported individual claims.

D. Structured memory stores only referee-supported findings, failures and unresolved results, scoped to conditions/regimes, for use in later investigations.

## 4. Benchmark

Create:
- research_loop_proof/final_kernel/
- docs/research_loop_proof/FINAL_KERNEL_SPEC.md
- docs/research_loop_proof/FINAL_KERNEL_RESULTS.md
- .github/workflows/research-loop-final-kernel.yml
- focused tests.

Reuse existing numeric/t0/integrity machinery aggressively.

Use **4 synthetic companies**, each with **3 sequential episodes** E1-E3. Candidate semantic identity is stable within a company. E2 and E3 (8 episodes total) are scored. E1 creates genuine prior research history.

Each episode has:
- company profile;
- forecast mandate;
- data dictionary mapping X01-X08 to plausible semantic information sources;
- dated operating/event log;
- observable regime/context descriptors;
- current research question.

Context must be informative but not an answer key. Every scored episode must include at least two plausible explanations: one genuinely relevant clue and at least one plausible red herring. Prefer clues that narrow to an information family rather than reveal the exact useful variable.

Never use semantic labels such as noise, driver, proxy or retired.

## 5. Sequence patterns

Across the 8 scored later episodes, freeze exactly 2 examples of each:

P1 RECURRENCE — a previously validated relationship becomes useful again under observably similar conditions.

P2 STALE POSITIVE — a previously useful relationship stops after an observable contextual/regime change.

P3 RE-OPENED NEGATIVE — a previously unhelpful candidate/family becomes useful after an observable contextual change.

P4 STABLE NEGATIVE / NULL — a plausible candidate remains unhelpful, or no candidate is currently useful, despite tempting contextual events.

At least 2 scored episodes must be true current-null episodes.

Use different role permutations across companies so no fixed semantic label solves the benchmark.

## 6. Paired conditions

K = FULL KERNEL:
- current company context;
- accumulated validated memory from prior episodes of that company;
- frozen L8 policy and t0-beta.

F = FRESH-CONTEXT CONTROL:
- identical current company context/data;
- empty memory;
- otherwise identical model, policy, effort, menu, budget, cutoffs and instrument.

E1 runs once per company with empty memory. Its evidence is passed through the referee and becomes K's initial memory.

E2: run K and F independently on identical current data/context. Add only K's referee-supported E2 evidence to K memory.

E3: run K and F independently on identical current data/context. F is reset empty again.

No cross-condition information sharing.

## 7. Referee and memory rules

Freeze them before the scored run.

The referee may use:
- current context;
- recorded experiments/results;
- final beliefs/conclusion;
- later confirmation only for configurations actually tested or explicitly selected.

It may not use hidden roles, coefficients or oracle-only experiments to create product knowledge.

Positive findings are approved only at the granularity supported:
- X03 alone positive -> X03 may be approved.
- X03 given X05 positive -> conditional claim may be approved.
- {X03,X05} positive without separation -> only the set-level finding is approved, with attribution unresolved.

Negative findings remain scoped to tested configuration/window/context and are never rewritten as “never useful”.

Memory is deterministic, not a new LLM lesson. Each entry must include:
- id/company/episode;
- context/regime tags;
- candidate/reference configuration;
- positive/negative/unresolved/deteriorated status;
- exact claim granularity;
- experiment refs;
- research-window result;
- confirmation status/result if applicable.

Store negative and unresolved evidence as well as positives.

The memory builder must be unable to import/read hidden truth or oracle-only artifacts.

## 8. Informativeness

The hidden evaluator may use truth only for scoring.

A scored non-null episode is informative if at least one current true predictive candidate or truth-eligible current set:
- is detectable with the pinned t0-beta instrument in a legal research window (95% lower bound > 0), and
- confirms positively (95% lower bound > 0).

Null episodes are always scored if integrity is clean.

All 6 non-null scored later episodes must be informative. Otherwise BENCHMARK FAILURE; no reroll.

## 9. Episode scoring

Score the researcher's experiments plus **referee-approved findings**, not the raw LLM final selection alone.

STRONG SUCCESS, informative non-null:
1. researcher generated evidence from which referee can approve a current positive finding;
2. narrowest approved positive finding contains at most 2 candidates;
3. hidden evaluation shows it contains at least one genuinely current useful candidate;
4. confirmation lower bound > 0;
5. any irrelevant member of a 2-candidate set is not approved individually without evidence;
6. no retired/pure-noise candidate is separately approved as currently predictive without evidence.

A 2-candidate set-level finding with unresolved attribution is allowed. The task is predictive information, not causal identification.

PARTIAL SUCCESS:
a confirmed current positive set of 3-4 candidates is approved but not narrowed to <=2. Report it; it does not count as strong success.

NULL SUCCESS:
no positive current finding is approved and the user-facing conclusion contains no established positive claim.

## 10. Compounding score

For each of the 8 K-vs-F pairs:

K WIN if:
- K strong-success, F not; or
- both strong-success but K reaches its first referee-approvable strong finding >=2 experiments earlier; or
- both strong-success at same discovery timing but K uses >=2 fewer total experiments.

F WIN = symmetric opposite. Otherwise TIE.

Also report how K used prior positives, avoided stable negatives, reopened stale negatives, abandoned stale positives, or ignored memory. These are descriptive; the paired win/loss is scored.

## 11. Final programme reading

First match wins.

1. INFRASTRUCTURE FAILURE — material truth leak, future-data leak, prompt rebuild/recompute failure, wrong model/instrument, broken K/F memory separation, or >1 missing scored trajectory.
Closing line: BENCHMARK/INFRASTRUCTURE RESULT ONLY

2. BENCHMARK FAILURE — fewer than 6/6 non-null scored episodes informative; confirmed world/context/referee defect; or memory uses truth/oracle-only knowledge.
Closing line: BENCHMARK/INFRASTRUCTURE RESULT ONLY

3. FULL KERNEL PROVEN FOR THIS BENCHMARK — ALL:
- K strong-success in >=6/8 scored later episodes;
- K succeeds in both null episodes;
- <=1 episode where pure-noise/retired candidate is incorrectly approved individually as current;
- >=3 K wins over F and <=1 F win;
- >=2 K wins arise from earlier validated discovery / fewer experiments, not merely different final stochastic wording;
- where defined, median oracle-fraction analogue of K's narrowest approved positive findings >=0.75.

Closing line:
MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST

4. FULL KERNEL NOT PROVEN — every valid scored run not satisfying row 3.
No MIXED, threshold relaxation or “basically worked” reinterpretation.

Closing line:
STOP SYNTHETIC KERNEL WORK

“Proven” means demonstrated on this frozen benchmark, not universal proof.

## 12. Integrity/process

Preserve:
- seeds derived from frozen spec hash + scored run id;
- no scored preview;
- one scored dispatch only;
- no reroll;
- per-job own observed data only;
- K/F current data/context byte-identical within pair;
- only K gets memory;
- truth/confirmation absent from research jobs;
- prompt rebuild, canary, poison/future-data tests, experiment recompute, model/weight hashes;
- static workflow/memory-separation tests.

Process:
1. minimal implementation by reuse;
2. freeze FINAL_KERNEL_SPEC.md;
3. one focused independent pre-run check: L8 identity, context-as-data, K/F equality, memory isolation, sequence fidelity, referee determinism, programme determinism, no-reroll mechanics;
4. fix only confirmed defects before scored worlds exist; re-pin;
5. one operational preflight, no truth inspection/tuning;
6. one scored 4-company/12-episode workflow;
7. evaluate once;
8. publish FINAL_KERNEL_RESULTS.md;
9. update README and PR #3;
10. stop.

Do not ask for owner approval unless the focused check finds a genuine ambiguity that cannot be resolved mechanically.

Do not modify/reinterpret Phase0, beta1, learn1, policy1, discovery1, human1, Kernel1, Experiment4, B1, engine ledger or sealed real data.

## 13. Owner report

Bring:
1. exact kernel definition;
2. proof L8 policy was not repaired;
3. context construction;
4. memory construction and no-truth proof;
5. company sequences/patterns;
6. integrity;
7. per-episode K/F experiments;
8. referee-approved findings;
9. strong/partial/null success;
10. K/F wins/losses/ties;
11. where memory helped/hurt/was ignored;
12. cheap-trial economics;
13. total cost;
14. frozen programme reading.

End with exactly one:
- MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST
- STOP SYNTHETIC KERNEL WORK
- BENCHMARK/INFRASTRUCTURE RESULT ONLY

Do not continue past that point.
