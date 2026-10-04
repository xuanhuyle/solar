# Next milestone — Replace accumulating prompt lessons with a minimal research-policy architecture

We have reached an architectural inflection point.

Read first:

- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/research_loop_proof/LEARN1_RESULTS.md`
- `docs/research_loop_proof/BETA1_SPEC.md`
- `docs/research_loop_proof/LEARN1_SPEC.md`
- `research_loop_proof/beta1/`
- `research_loop_proof/learn1/`

Do not start by proposing another prose lesson.

The evidence so far is:

## beta1
The researcher:
- found a useful incumbent relationship;
- detected its deterioration;
- updated its belief and removed it;
- but treated pre-change negative findings as permanently valid;
- therefore failed to reopen candidates after the regime changed.

## learn1
A portable lesson from beta1 changed the next investigation:
- the learned condition explicitly treated old rejections as "provisional and dated";
- it re-screened dismissed candidates on recent data;
- it found a positive set containing the new driver;
- it then ran a conditional experiment.

But it still failed:
- the positive set was not decomposed far enough;
- the researcher exhausted its budget before resolving attribution;
- it selected a noise variable it could not distinguish from the useful variable.

The important progression is:

> stale-evidence failure → lesson changes exploration → attribution/budget failure

The next question is therefore not:

> "What paragraph should we add next?"

It is:

> **What is the smallest general research algorithm that explains both failures and makes the researcher reason explicitly about evidence validity, unresolved uncertainty, and the future value of its remaining experiment budget?**

This milestone should implement and test that minimal architecture.

The objective is empirical evidence, not framework-building.

---

# 1. Progress over polish

For this task:

- do not add another accumulated prose lesson;
- do not build a generic agent framework;
- do not build a database;
- do not redesign t0-beta;
- do not increase the six-experiment budget;
- do not add more variables;
- do not run the full 10-scenario benchmark;
- do not create a large planning subsystem;
- do not reopen N1, B1, Experiment 4 or historical results;
- do not launch a broad review programme.

Use beta1/learn1 as engineering evidence.

Produce at most one short architecture note, then build and test.

One focused pre-run integrity check is enough.

---

# 2. The architectural hypothesis

The two observed failures may share a small number of general research primitives:

## A. Evidence has validity conditions

A finding is not just:

> X helps / X does not help.

It also has:

- when it was observed;
- under which apparent regime;
- how recent it is;
- whether later evidence makes it stale;
- whether it was direct or only inferred from a group.

## B. Research decisions should target unresolved decision-critical uncertainty

The researcher should know not only its candidate beliefs, but also:

- what uncertainty currently blocks a defensible final decision;
- which experiment would reduce that uncertainty;
- whether an experiment is likely to create a new attribution problem.

## C. Experiment budget has option value

Before spending an experiment, the researcher should consider:

- what it expects to learn;
- what follow-up would be required under the important possible outcomes;
- whether enough budget would remain to resolve that follow-up.

This does NOT mean hard-coding a particular search policy.

The LLM still chooses the experiments.

The architecture should make the relevant state and trade-offs explicit.

---

# 3. Do not encode the answer as if/then policy code

Do NOT add rules such as:

- "if regime change then retest rejected candidates";
- "always reserve one experiment";
- "if a group is positive then split it";
- "never select a candidate without a single-variable test";
- forced exploration quotas;
- mandatory experiment sequences.

Those would simply program the benchmark answer.

Instead, expose structured research state and require the researcher to reason over it.

The researcher must still decide:

- whether evidence is stale;
- which uncertainty matters;
- whether a retest is worth the budget;
- whether a grouped experiment is worth doing;
- whether its likely follow-up cost is acceptable;
- what to select at the end.

---

# 4. Minimal structured research state

Design the smallest state that can represent what beta1 and learn1 were missing.

Do not overengineer this.

A reasonable starting point is:

## Global state

- `regime_assessment`:
  - stable / possible_change / changed / unknown
  - evidence ids
  - short justification

- `decision_uncertainties`:
  - at most 3 items;
  - each item says what is unresolved and why it matters for the final forecast decision.

- `budget`:
  - experiments remaining;
  - a short statement of what the researcher may need to resolve before final selection.

## Per-candidate state

For each candidate:

- current status;
- evidence ids;
- most recent scored period;
- evidence freshness: current / possibly_stale / stale / unknown;
- evidence type: direct / grouped / conditional;
- unresolved attribution, if any.

Do not mechanically infer these fields from hidden truth.

They are the researcher's state.

## Per-experiment request

In addition to the existing experiment definition, require concise fields such as:

- `targets_uncertainty`: which decision uncertainty this experiment addresses;
- `possible_followup`: what additional experiment might be needed if the result is positive, negative or ambiguous;
- `budget_rationale`: why this is worth spending one experiment now.

Keep all such fields short.

Do not request chain-of-thought.

Ask only for concise research-state summaries and decisions.

---

# 5. The minimal research loop

The software loop should become explicitly:

1. receive the latest evidence;
2. update structured research state;
3. identify the current decision-critical uncertainty;
4. choose experiment(s) under the remaining budget;
5. run them;
6. append results;
7. repeat;
8. make a final selection with a clear statement of unresolved uncertainty.

The LLM makes steps 2–4 and 8.

The software:

- validates the schema;
- enforces the experiment budget;
- runs the experiments;
- records the evidence;
- prevents leakage.

Do not add a software "planner" that chooses the experiments for the model.

---

# 6. First use beta1 and learn1 only as regression cases

Before spending a new hidden world, use the already-published beta1 and learn1 observed data as **non-scored engineering replays**.

Purpose:

> Does the structured interface actually make the missing research concepts representable and usable?

These replays are NOT scientific evidence.

They are explicitly contaminated by our knowledge of those failures and must never be reported as validation.

The research job must still not receive truth.

For beta1 replay, inspect whether the architecture at least makes it possible for the researcher to represent:

- X03 deterioration;
- pre-change rejections becoming possibly stale;
- the need to choose between another X03 confirmation and re-exploration.

For learn1 replay, inspect whether it can represent:

- the positive grouped result;
- unresolved attribution inside that group;
- the fact that a final grouped claim may require follow-up;
- the remaining-budget consequence.

Do not tune repeatedly until both replays "win".

One implementation pass plus one correction for a clear interface defect is enough.

The replays are smoke/regression tests, not targets to optimize.

---

# 7. Scored test: one new paired hidden world

After the architecture works mechanically, generate exactly one fresh hidden world.

The seed must not exist before dispatch.

Use the same world family as beta1/learn1:

- four anonymous candidates;
- retired driver;
- emerging driver;
- correlated proxy;
- noise;
- hidden change point;
- t0-beta;
- three rounds;
- six experiments total;
- same confirmation segment;
- same truth separation.

Do not make the world easier.

Do not change signal strength.

Do not reroll.

---

# 8. Two conditions on the SAME hidden world

Run two independent researchers.

## L — lesson-only baseline

Use the learn1 learned condition:

- beta1 brief;
- frozen beta1-derived lesson;
- existing belief format;
- no new structured research-policy state.

This is the strongest existing researcher we have actually tested.

## S — structured research-policy condition

Use:

- the same beta1-derived lesson as L;
- the same model;
- same effort;
- same observations;
- same experiment menu;
- same six-experiment budget;
- same rounds;
- same confirmation data;

plus only the new structured research-state / budget-awareness interface from this milestone.

Do NOT give S a new prose lesson distilled from learn1.

The point is to test the architecture, not another paragraph.

The intended difference between L and S is:

> **S must explicitly represent evidence freshness, unresolved uncertainty, and likely follow-up needs before allocating experiments.**

Nothing else.

Run L and S separately so neither sees the other's experiments.

---

# 9. Why this comparison matters

The experimental question is:

> **Does making research state and future experiment cost explicit improve the autonomous research policy beyond the previous lesson-only researcher?**

We are not trying to prove general superiority from one world.

We want to know whether the architectural abstraction suggested by beta1 + learn1 produces a measurable behavioural improvement.

---

# 10. What to record

For both conditions, round by round:

- beliefs entering the round;
- regime assessment, where available;
- decision-critical uncertainties;
- candidate evidence freshness;
- experiments chosen;
- what uncertainty each experiment targets;
- expected follow-up needs;
- results;
- belief/state updates;
- remaining budget;
- final selection;
- unresolved uncertainty at the end.

For S specifically, preserve the structured state exactly as produced.

Do not score verbosity.

---

# 11. Evaluation

Keep the same hidden truth and confirmation evaluation used in beta1/learn1.

Report:

- retired driver;
- emerging driver;
- proxy;
- noise;
- change point;
- evidence availability by round;
- standalone predictive value;
- incremental value where relevant.

Evaluate both final selections with:

- t0-beta;
- the existing ridge reference.

Do not change the forecasting comparison.

---

# 12. Behavioural questions

Compare S with L on:

1. Did it recognise when old evidence might no longer be current?
2. Did it re-open stale hypotheses when warranted?
3. Did it identify unresolved attribution after grouped evidence?
4. Did it spend its remaining budget in a way that could resolve the final decision?
5. Did it avoid spending the last experiment on redundant confirmation?
6. Did it identify the emerging driver?
7. Did it exclude the retired driver?
8. Did it avoid unsupported noise?
9. Was its final selection better supported by its own experiments?
10. Did it finish with fewer decision-critical uncertainties unresolved?

These are the main outputs.

---

# 13. Outcome labels

Keep the reading simple.

## `ARCHITECTURE SIGNAL OBSERVED`

Use this when S shows a materially better research policy than L on the same world, and the improvement is plausibly connected to the structured state.

Strong examples:

- S finds the emerging driver and L does not;
- both find it, but S resolves attribution while L leaves an unsupported variable;
- S uses its final experiments to resolve a decision-critical uncertainty that L leaves unresolved;
- S produces a materially better-supported final selection because it planned follow-up needs under the same budget.

Forecast accuracy alone is not enough.

## `NO ARCHITECTURE SIGNAL`

Use when S's structured state does not materially improve research behaviour or outcome.

## `BOTH SUCCEED`

Use when both complete the essential loop cleanly, leaving the one world unable to distinguish the architectures.

## `BOTH FAIL`

Use when neither completes the essential loop.

## `INFRASTRUCTURE FAILURE`

Use only when service/integrity problems prevent interpretation.

One world is an existence test, not a rate.

---

# 14. Do not optimize the comparator

Do not weaken L.

Use the strongest lesson-only condition from learn1.

Do not add a scripted strategy unless it is essentially free to reuse; it is not the decision-relevant comparison here.

Do not add more conditions.

Two conditions are enough.

---

# 15. Implementation discipline

Create a small isolated package, for example:

`research_loop_proof/policy1/`

Reuse beta1/learn1 components aggressively.

Do not duplicate large amounts of code where an import is safe.

A short architecture note is allowed:

`docs/research_loop_proof/POLICY1_ARCHITECTURE.md`

Maximum roughly one page.

It should state:

- the minimal structured state;
- why each field exists;
- which observed failure it addresses;
- what is deliberately NOT encoded.

Do not wait for owner approval after writing that note.

Proceed directly unless you find a genuine blocker.

---

# 16. Preflight and integrity

One non-scored preflight is allowed only to ensure:

- the new schema is accepted;
- no reasoning-extraction refusal;
- both conditions complete all calls;
- the structured fields serialize and replay correctly.

Do not use preflight to tune scientific choices.

Before the scored run, do one focused check for:

- truth leakage;
- cross-condition contamination;
- prompt differences beyond the intended architecture;
- future-data leakage;
- evaluator reproducibility.

Then dispatch one scored paired world.

---

# 17. Cost

Record:

- implementation effort;
- preflight calls/tokens;
- scored L calls/tokens;
- scored S calls/tokens;
- t0-beta forecasts;
- runner time;
- refusals/repairs.

Do not build new accounting machinery.

---

# 18. Final report

Bring me a concise report with:

## 1. Minimal architecture

Show the structured state you implemented and why.

State explicitly what behavior was NOT hard-coded.

## 2. Regression replays

Very briefly:
- beta1 replay: did the architecture represent stale evidence?
- learn1 replay: did it represent unresolved attribution / follow-up cost?

Label these engineering checks, not evidence.

## 3. Integrity

Confirm L and S differed only by the intended research-policy architecture and both were isolated from truth.

## 4. Hidden world

Reveal after both runs:
- retired driver;
- emerging driver;
- proxy;
- noise;
- change point;
- evidence available by round.

## 5. Lesson-only trajectory (L)

Round by round:
- experiments;
- evidence;
- belief updates;
- final selection.

## 6. Structured-policy trajectory (S)

Round by round:
- regime assessment;
- decision uncertainties;
- evidence freshness;
- experiments;
- targeted uncertainty;
- anticipated follow-up;
- evidence;
- updates;
- remaining budget;
- final selection.

## 7. Side-by-side

Answer the ten behavioural questions from section 12.

## 8. Confirmation

Relevant t0-beta and ridge results for:
- E;
- L final selection;
- S final selection;
- key incremental comparisons.

## 9. Cost

Actual compute, calls, tokens and implementation effort.

## 10. Outcome

Choose exactly one:

- `ARCHITECTURE SIGNAL OBSERVED`
- `NO ARCHITECTURE SIGNAL`
- `BOTH SUCCEED`
- `BOTH FAIL`
- `INFRASTRUCTURE FAILURE`

Then answer directly:

> **Did a small general research-policy architecture improve autonomous investigation beyond adding a prose lesson?**

If yes, identify exactly what changed.

If no, identify the single dominant remaining bottleneck.

Then stop.

---

# 19. Priority

We are no longer trying to accumulate tips.

We are trying to discover the minimal algorithm behind competent empirical research.

The sequence so far is:

**evidence → failure → lesson → changed behaviour → new failure → architectural abstraction**

Now test whether that abstraction actually helps.

Move forward.
