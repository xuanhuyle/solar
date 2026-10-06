# Kernel1 — Direct proof of the current autonomous research kernel

Read the repository at current HEAD before doing anything. In particular read:

- `docs/experiment_5/NORTH_STAR_CLARIFICATION.md`
- `docs/research_loop_proof/DESIGN.md`
- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/research_loop_proof/LEARN1_RESULTS.md`
- `docs/research_loop_proof/DISCOVERY1_SPEC.md`
- `docs/research_loop_proof/DISCOVERY1_RESULTS.md`
- `docs/research_loop_proof/HUMAN1_SPEC.md`
- `docs/research_loop_proof/HUMAN1_RESULTS.md`
- the current `research_loop_proof/discovery1/` implementation;
- the current PR description and latest research-loop commits.

This milestone is **Kernel1**.

The owner wants a direct answer to the original technical question. Do not decompose it into another narrower milestone.

> **Does the current autonomous researcher kernel, unchanged, reliably discover useful predictive information in a non-trivial hidden hypothesis space, reject false information, adapt when relationships change, and support its conclusions with experiments that survive unseen confirmation?**

This is a test of whether the kernel works. It is **not** a contest against a hand-written search script.

The scored result must end the current synthetic-kernel line with a binary scientific reading:

- `KERNEL PROVEN FOR THIS BENCHMARK`, or
- `KERNEL NOT PROVEN`.

Infrastructure or benchmark invalidity may prevent a scientific reading, but there is no `MIXED`, no new lesson, and no follow-up architecture in this task.

---

# 1. Freeze the current kernel

For the autonomous researcher use **Discovery1's L8 researcher exactly as frozen**, not Human1's narrowed two-candidate variant.

That means:

- the learn1 lesson-only researcher;
- the frozen beta1-derived lesson, unchanged (sha256 beginning `1c38b101`);
- the same pinned researcher model and effort;
- the same substantive system text;
- the same X01-X08 candidate universe;
- the same experiment menu;
- the same 7-day t0-beta context;
- the same three research rounds and final call;
- the same six-experiment total budget;
- at most three experiments per round;
- the same repair rule and token cap;
- the same notebook and belief machinery.

**Do not change the researcher prompt, lesson, policy, budget, schema, experiment menu, or methodological advice.**

Reuse/import the existing Discovery1 researcher rather than copying and editing it wherever possible.

Human1 established that the researcher can adjudicate a human-supplied pair but did not show residual agentic value. Kernel1 returns to the broad-search researcher because the technical proof is autonomous discovery.

Do not create:

- another lesson;
- Policy2;
- Human2;
- structured state;
- a new memory layer;
- extra research instructions;
- chain-of-thought requests;
- a larger experiment budget;
- an easier candidate universe.

---

# 2. What is being proved

The original audit-level proof is the target:

> Given a noisy hidden information universe containing genuinely predictive and spurious candidates, can the AI researcher autonomously identify useful predictive information, reject false information, respond to a regime change, and produce reproducible conclusions that survive an unseen holdout?

The benchmark is synthetic so the evaluator knows truth. Passing it does **not** prove real-market performance or commercial value.

A pass does establish enough technical evidence to move the unchanged kernel to a real-world research test.

A failure means the current kernel is not proven. Do not rescue it with another synthetic prompt/policy iteration.

---

# 3. Scored batch: 12 frozen hidden worlds

Create an isolated:

`research_loop_proof/kernel1/`

and:

- `docs/research_loop_proof/KERNEL1_SPEC.md`
- `docs/research_loop_proof/KERNEL1_RESULTS.md`
- `.github/workflows/research-loop-kernel1.yml`
- focused tests only.

Reuse the Discovery1 world/lab machinery aggressively.

Freeze **12 independent scored worlds** before the scored run:

- **8 change worlds**
- **2 stable worlds**
- **2 null worlds**

Use the same 154-day shape as Discovery1:

- days 1-126 are available to research through the existing three round cutoffs;
- days 127-154 are confirmation only and never held by the research job;
- same hidden-change timing family;
- same t0-beta instrument and pinned weights;
- same candidate anonymisation X01-X08.

## Change worlds

Use Discovery1's existing roles unchanged:

- R: predictive before the hidden change, retired after it;
- E: not predictive before the hidden change, predictive after it;
- D: correlated proxy of E, no direct target effect;
- N1-N5: independent irrelevant/noise candidates.

The target logic and effect strength should be the existing frozen Discovery1/Phase-0 family wherever possible.

## Stable worlds

Use the same generator and candidate identities, but make the old relationship genuinely stable:

- R remains predictive throughout research and confirmation;
- E never turns on;
- D remains only the proxy construction associated with E and therefore should not become useful merely because of a hidden change;
- N1-N5 remain irrelevant.

Do not tell the researcher the world is stable.

## Null worlds

Use the same candidate-generation machinery but set all candidate effects on the target to zero throughout.

Do not tell the researcher the world is null.

The candidate series should still look statistically realistic under the generator. A null world must not be trivially identifiable from metadata.

## Seeds and no rerolls

Derive scored seeds mechanically from:

`sha256("kernel1:<kernel1_spec_sha>:<scored workflow run id>:<world id>")`

or an equally auditable run-id-derived scheme.

The implementer must not be able to preview scored worlds before dispatch.

One scored dispatch only. Every dispatch is recorded.

No rerolls.

---

# 4. No scripted comparator as a gate

Do **not** build a new scripted search policy for Kernel1.

Do **not** require the researcher to beat a deterministic comparator in order to pass.

Human1 already answered the separate question of whether adaptive planning adds value over an obvious script on a supplied two-variable problem.

Kernel1 asks the more fundamental question:

> **Can the current autonomous researcher itself do the research job reliably?**

You may report trivial oracle/reference quantities from the evaluator. Do not turn them into a competing research arm.

Do not use ridge as a pass/fail condition. If an existing ridge confirmation is nearly free to reuse, it may be reported as context only.

---

# 5. Truth separation

Preserve the strongest existing separation guarantees:

- the research job has no truth files, role labels, seeds, change point or confirmation data;
- it receives only the observed artifact and its own notebook;
- every prompt is rebuilt byte for byte by the evaluator;
- every experiment is recomputed;
- canary scans run;
- post-cutoff poison tests run;
- model and data hashes are checked;
- the workflow statically proves which job receives which artifact and secret.

If practical, avoid the Human1 disclosed property where a job downloads other worlds' observed data. Each research job should receive only its own world's observed artifact. If removing that property requires significant generalisation, keep it and disclose it; it is not by itself a scientific failure because it contains no role information and the researcher has no tools. Do not delay the milestone for polish.

---

# 6. Informativeness and oracle quantities

The evaluator knows the hidden roles and may directly run t0-beta to determine what was actually discoverable.

All informativeness checks are frozen before the scored run.

## Change world is informative if

On observed post-change research data, using the same legal 7-day t0-beta context:

- E alone versus no covariate has a 95% lower bound above zero on at least one of the existing round-2 / round-3 post-change windows; and
- on confirmation days, the best current predictive set among the non-noise current candidates has a 95% lower bound above zero.

D is a predictive proxy, not automatically a false discovery. The project is testing predictive information, not causal identification.

## Stable world is informative if

- R alone versus no covariate has a 95% lower bound above zero on an observed research window; and
- R remains useful on confirmation.

## Null worlds

Null worlds are always scored if integrity is clean. Their purpose is false-discovery control.

## Oracle set and oracle fraction

For every informative non-null world, compute an evaluator-only **oracle current predictive set** by scoring the small set of truth-eligible current candidates:

- change: subsets of {E, D}, up to the lab's allowed size;
- stable: {R}.

Choose the subset with the lowest confirmation MAE among those whose confirmation skill versus no covariate has a lower bound above zero.

The **oracle fraction** is:

`researcher final-set confirmation skill / oracle-set confirmation skill`

using the same t0-beta configuration.

This is an evaluation quantity only. The researcher never sees it.

---

# 7. What counts as evidence-supported research

Do not reuse Discovery1's overly narrow criterion that only one exact experiment shape can support a final set.

Freeze this deterministic support rule before the run.

Let F be the researcher's final selected set.

F is **supported by the researcher's own evidence** if either:

### Direct support

There is a current-regime experiment with:

- covariates exactly F;
- any legal disjoint reference set;
- 95% lower bound above zero.

or, for every member of F individually, there is a current-regime experiment where that candidate is the sole tested covariate (with any legal reference) and the lower bound is above zero.

### Support by elimination

There is a current-regime positive experiment on a superset S containing F, and for every candidate z removed from S to reach F there is later current-regime evidence showing z does not add value given F (or the relevant retained subset), with lower bound less than or equal to zero.

This allows ordinary scientific elimination such as:

- {E,R} is positive;
- R given E is null;
- conclude E is the supported retained information.

Do not infer support merely from the hidden truth or from confirmation.

A good confirmation forecast can never rescue an unsupported research conclusion.

Use only experiments fully after the hidden change for current-regime support in change worlds.

---

# 8. Per-world success

Score the researcher on its **final selection and evidence**, not on whether it used the same path an evaluator would have chosen.

## Change world success

All must hold:

1. the world is informative;
2. the final selection is non-empty;
3. R is absent from the final selection;
4. no pure-noise N1-N5 candidate is in the final selection;
5. the final selection is supported by the researcher's own current-regime evidence under section 7;
6. the final selection's confirmation skill versus no covariate has a 95% lower bound above zero;
7. its oracle fraction is at least **0.70**.

D may be selected if it carries genuine predictive value for t0. It is not penalised merely because it is non-causal. The report must still show D-alone, E-alone, D-given-E and E-given-D confirmation quantities so we can see whether the researcher found the underlying stronger information or only a proxy.

## Stable world success

All must hold:

1. the world is informative;
2. the final selection is non-empty;
3. no pure-noise candidate is selected;
4. the final selection is supported by the researcher's own evidence;
5. confirmation skill has a 95% lower bound above zero;
6. oracle fraction is at least **0.70**.

Report whether the researcher incorrectly declared the stable relationship deteriorated, but do not fail it for wording alone if its final supported predictive selection is correct.

## Null world success

All must hold:

1. final selection is empty;
2. no candidate has final belief status `accepted`;
3. the final conclusion does not claim that any candidate has established current predictive value.

Promising/uncertain is allowed if it is not selected or presented as established.

---

# 9. Programme-level binary proof

Freeze this before the scored run.

First-match logic:

## 1. INFRASTRUCTURE FAILURE

Any material integrity failure:

- truth or confirmation data reaches the research job;
- prompt cannot be rebuilt;
- data or experiment recomputation fails;
- wrong model revision;
- workflow/separation violation;
- more than one scored world lacks a valid final researcher response after the existing repair rule.

Stop. Do not repair and rerun the scored batch in this task.

Closing line:

`BENCHMARK/INFRASTRUCTURE RESULT ONLY`

## 2. BENCHMARK FAILURE

Any of:

- fewer than **6 of 8** change worlds are informative;
- either stable world is not informative;
- a confirmed generator/evaluator defect makes the scientific scoring invalid.

Stop. Do not quietly regenerate worlds.

Closing line:

`BENCHMARK/INFRASTRUCTURE RESULT ONLY`

## 3. KERNEL PROVEN FOR THIS BENCHMARK

All must hold:

- researcher succeeds in at least **6 of the 8 change worlds**;
- researcher succeeds in **both stable worlds**;
- researcher succeeds in **both null worlds**;
- across informative non-null worlds, median oracle fraction is at least **0.80**;
- at most **one** informative non-null world ends with any pure-noise candidate in the final selection;
- there are **zero** false accepted candidates across the two null worlds.

Closing line:

`MOVE THE CURRENT KERNEL TO A REAL-WORLD RESEARCH TEST`

## 4. KERNEL NOT PROVEN

Every scientifically valid scored run that does not satisfy row 3.

No `MIXED`.

No reinterpretation.

No post-hoc softer threshold.

Closing line:

`STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL`

The phrase "proven" here means **demonstrated against this frozen synthetic benchmark at the predeclared thresholds**. It does not mean proven for arbitrary research problems or real markets.

---

# 10. Required reporting

For every world report:

- world type;
- hidden roles, revealed only in evaluate;
- change point where applicable;
- informativeness checks;
- every researcher experiment in order;
- belief changes;
- first post-change experiment containing useful information;
- final selection;
- whether the final set is supported, and by which exact experiment chain;
- retired R treatment where applicable;
- pure-noise candidates selected;
- E and D treatment;
- confirmation skill and interval;
- oracle set and oracle fraction;
- success/failure and the exact failed criterion;
- API attempts, refusals, repairs, tokens;
- t0-beta forecast count and wall time.

Aggregate:

- change-world success rate;
- stable-world success count;
- null-world success count;
- useful-information recall descriptively;
- retired-driver retention;
- pure-noise final selections;
- false accepts in null worlds;
- median and distribution of oracle fraction;
- experiment usage;
- API/token/compute cost.

Also report, descriptively:

- how often the researcher reopened stale negative findings after evidence of change;
- how often it used conditional/separation experiments;
- how often it exhausted all six experiments;
- whether it cited earlier failed experiments in later decisions.

Do not make these descriptive measures extra hidden pass/fail gates.

---

# 11. Process

Use progress over polish.

1. Implement the minimal isolated Kernel1 package by reusing Discovery1.
2. Write and freeze `KERNEL1_SPEC.md`.
3. Run **one focused independent pre-run check** of:
   - kernel identity: exact Discovery1 L8 researcher, no substantive prompt/policy change;
   - truth separation;
   - stable/null generator variants;
   - support-rule determinism;
   - programme-rule determinism;
   - seed/no-reroll mechanics.
4. Fix only confirmed implementation/evaluator defects before any scored world exists, and re-pin the spec.
5. Run **one non-scored operational preflight**. It checks only execution/schema/integrity. Do not inspect its hidden roles or use it for scientific tuning.
6. Dispatch the **single 12-world scored batch**.
7. Evaluate once.
8. Publish `KERNEL1_RESULTS.md`.
9. Update README and PR #3 with the frozen result.
10. Stop.

Do not dispatch reviewer swarms.

Do not add a comparator because the result looks weak.

Do not change thresholds after seeing any world.

Do not run a second scored batch.

---

# 12. What not to touch

Do not modify:

- Phase 0;
- beta1;
- learn1;
- policy1;
- discovery1;
- human1;
- Experiment 4;
- B1;
- the engine ledger;
- sealed/forward real data.

Do not promote any prior exploratory real-data result.

---

# 13. Stop condition

After `KERNEL1_RESULTS.md` and the PR note are published, stop.

Do not:

- propose Kernel2;
- improve the prompt;
- create another lesson;
- change the budget;
- widen or narrow the candidate universe;
- add memory/state architecture;
- run a real-world test;
- reinterpret a failure.

Bring the owner:

1. the exact frozen question;
2. proof that the researcher kernel was unchanged;
3. the 12-world batch composition;
4. integrity status;
5. per-world results;
6. aggregate success metrics;
7. evidence-support failures, if any;
8. null-world false discoveries;
9. total cost;
10. the frozen programme reading.

End with exactly one of:

- `MOVE THE CURRENT KERNEL TO A REAL-WORLD RESEARCH TEST`
- `STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL`
- `BENCHMARK/INFRASTRUCTURE RESULT ONLY`

Do not continue past that point.
