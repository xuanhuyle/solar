# Discovery1 — Test discovery in a larger hypothesis space

Read the repository at current HEAD and in particular:

- `docs/experiment_5/NORTH_STAR_CLARIFICATION.md`
- `docs/research_loop_proof/PHASE0_RESULTS.md`
- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/research_loop_proof/LEARN1_RESULTS.md`
- `docs/research_loop_proof/POLICY1_RESULTS.md`
- `research_loop_proof/phase0/lab/menu.json`
- `research_loop_proof/beta1/lab/brief.md`
- `research_loop_proof/learn1/`
- `research_loop_proof/policy1/`

The next milestone is **Discovery1**.

Do not improve the researcher.

Policy1 produced `NO ARCHITECTURE SIGNAL`. Its structured-policy condition S performed worse than the lesson-only condition L. For this milestone, treat L — the beta1 researcher plus the frozen beta1-derived lesson from learn1 — as the strongest current researcher.

Do not create Policy2.  
Do not distill another lesson.  
Do not add structured state.  
Do not change the research policy based on policy1's failure.

## Scientific question

Can the existing researcher discover newly useful predictive information when the candidate information universe is too large to test every candidate individually within its experiment budget?

The current four-candidate worlds leave too much of the search problem to the benchmark designer. Discovery1 should remove that scaffold while changing as little else as possible.

## Minimal design

Create an isolated:

`research_loop_proof/discovery1/`

Reuse the existing beta1/learn1 machinery aggressively. Preserve all historical experiments and files unchanged.

Extend the hidden-world family minimally from four anonymous candidates to eight anonymous candidates:

- R: retired driver, as today;
- E: emerging driver, as today;
- D: correlated non-causal proxy of E, as today;
- five independent irrelevant/noise candidates.

Randomly permute the eight roles into X01-X08 for every world. The research job must never receive the roles.

Preserve the current world logic wherever possible:

- hidden regime change;
- same effect calibration;
- same observation schedule;
- same 7-day forecasting context;
- t0-beta as the experimental instrument;
- same experiment result fields;
- same 7/14/28-day experiment windows;
- same three research rounds;
- same final hidden confirmation period;
- truth absent from the research job.

Keep the total research budget at **SIX experiments**.

Keep at most three experiments per round.

An experiment may use at most four candidate covariates so that the eight-variable space cannot be collapsed into one trivial all-variable test.

The researcher must therefore decide how to search the candidate universe under budget.

## Researcher

Use the learn1 lesson-only researcher L.

The frozen lesson must be unchanged.

Adapt the brief and schema only mechanically where required to enumerate X01-X08 instead of X01-X04.

Do not add any new substantive research advice.

Do not add prose derived from policy1.

## Comparator

Implement one simple fixed budget-matched search policy before any scored world exists.

It may use a straightforward fixed group-screen / split strategy over the eight anonymous candidates.

Do not optimize the comparator.  
Do not make it an intelligent planner.  
Freeze it before generating the scored worlds.

Its purpose is only to determine whether an adaptive LLM researcher is doing something that a simple fixed search policy does not.

## Three-world frozen batch

Do not run one world and redesign.

Freeze the complete specification first, then generate **THREE independent hidden worlds** from the frozen specification.

Run the exact same L researcher and fixed comparator on all three.

No lesson or prompt changes between worlds.  
No rerolls.  
No tuning after seeing any world's result.

A preflight may use a separate non-scored world only to verify:

- schema validity;
- candidate enumeration;
- t0 execution;
- prompt reconstruction;
- truth separation.

Do not scientifically tune against the preflight.

## Evaluation

For every scored world, first establish whether E was actually detectable on the relevant post-change windows.

If it was not detectable, label that world uninformative for researcher competence rather than manufacturing a failure.

For informative worlds report at minimum:

- whether the researcher tested E post-change;
- first experiment in which E entered;
- whether it distinguished E from grouped companions;
- whether R was removed after deterioration;
- whether any pure-noise candidate was selected;
- treatment of D, including incremental evidence where relevant;
- final selection;
- final-selection confirmation skill;
- E-alone confirmation skill;
- fixed comparator result;
- ridge confirmation for context only;
- experiments used and API/token cost.

Define a successful discovery conservatively:

1. E was detectable;
2. the researcher brought E into a post-change experiment;
3. E is in the final selection;
4. R and all pure-noise candidates are absent from the final selection;
5. E or the final selected set has positive supporting evidence from the researcher's own experiments;
6. the final selection has a confirmation lower bound above zero.

D may be selected only if the report clearly distinguishes proxy value from evidence about E and records whether D adds incremental value given E.

## Programme reading

Predeclare the programme-level reading before the scored run:

- `DISCOVERY SIGNAL`: researcher succeeds in at least 2 of the 3 informative worlds and performs better than the fixed search policy on successful supported discovery.
- `BOTH SUCCEED`: researcher and fixed policy both succeed in at least 2 of 3.
- `NO DISCOVERY SIGNAL`: researcher fails in at least 2 informative worlds.
- `BENCHMARK FAILURE`: fewer than 2 worlds contain detectable E evidence or another scientific-design defect prevents interpretation.
- `INFRASTRUCTURE FAILURE`: integrity or execution failure invalidates the run.

Do not reinterpret these labels after seeing the outcome.

## Scope discipline

This milestone is **not** about:

- new research-policy architecture;
- another lesson;
- persistent memory;
- t0 versus ridge superiority;
- open-web covariate sourcing;
- real-world data integration;
- commercial product design;
- UI;
- a general agent platform.

It tests one thing:

> Can the existing researcher search a meaningfully larger hypothesis space under a constrained experimental budget?

## Progress over polish

Use existing code rather than generalising the repository.

One short spec.  
One implementation.  
One operational preflight.  
One focused integrity check.  
One frozen three-world scored batch.  
One results document.

Do not create a large framework for arbitrary candidate counts.

Do not dispatch reviewer swarms unless a concrete integrity issue needs resolving.

## Stop condition

After publishing the result, stop.

Do not propose or implement a response to the result.

The owner will decide.

The final report must end with one of:

- `MOVE TO A REAL-WORLD RESEARCH TEST`
- `NARROW TO HUMAN-SUPPLIED HYPOTHESES`
- `STOP THE AUTONOMOUS-RESEARCHER THESIS`
- `BENCHMARK/INFRASTRUCTURE RESULT ONLY`
