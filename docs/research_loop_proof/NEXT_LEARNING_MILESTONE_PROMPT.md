# Next milestone — Turn the beta1 failure into persistent research knowledge

We now have enough evidence to move to the next core question.

Read first:

- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/research_loop_proof/BETA1_SPEC.md`
- `research_loop_proof/beta1/`
- `docs/research_loop_proof/PHASE0_RESULTS.md`
- `docs/research_loop_proof/NEXT_MILESTONE_PROMPT.md`

Do not reopen old design questions unless they block this experiment.

The important beta1 result is:

- infrastructure was clean;
- t0-beta clearly exposed the new predictive signal;
- the researcher correctly found the incumbent relationship;
- it noticed that relationship deteriorating;
- it updated its belief and removed the old driver;
- but it treated pre-change negative findings as permanent;
- it spent the remaining budget reconfirming the old driver's decline instead of reopening candidates rejected under the old regime;
- it therefore missed a strongly detectable emerging driver.

The next question is no longer whether t0-beta can expose the signal.

It can.

The next question is:

> **Can the researcher turn a failed investigation into a general research lesson, carry that lesson into a new problem, and use it to allocate experiments better?**

This is the first direct test of the project's learning-from-experience hypothesis.

The goal is new empirical evidence, not more infrastructure.

---

# 1. Progress over polish

For this task:

- do not redesign the sandbox;
- do not change t0-beta;
- do not increase the research budget;
- do not add more candidate variables;
- do not launch a broad multi-agent review;
- do not reopen N1;
- do not run another model benchmark;
- do not build generic memory infrastructure;
- do not refactor the existing engine.

Reuse beta1 as much as possible.

One focused integrity check before the scored run is enough.

If an imperfection does not threaten truth separation, future leakage, reproducibility, or interpretation, move on.

---

# 2. Preserve beta1 exactly

Do not rewrite or reinterpret beta1.

Its verdict remains:

`RESEARCHER FEASIBILITY FAILED`

The beta1 run is historical evidence.

Do not change:

- `BETA1_SPEC.md`;
- `BETA1_RESULTS.md`;
- the beta1 published result branches;
- Phase 0;
- B1;
- Experiment 4;
- the engine ledger;
- sealed data.

Build the next experiment separately, reusing beta1 code where practical.

---

# 3. First create ONE portable lesson from beta1

Before generating the next hidden world, make one retrospective lesson-distillation call.

This is not another research proposal.

Its sole job is to convert the beta1 failure into a compact, portable research lesson.

## Input to the lesson call

Give it:

- the beta1 research trajectory/notebook;
- the beta1 final conclusion;
- the minimal evaluator feedback necessary to explain the failure:

> The process changed. A candidate rejected on pre-change evidence became strongly predictive after the change. The researcher detected deterioration in the previously useful relationship but did not re-test candidates rejected under the earlier regime, so it missed the emerging signal.

Do not give the lesson call:

- the next world's seed;
- the next world's candidate mapping;
- any future-world data;
- any answer about which candidate will matter next.

## Output

A single research lesson of at most 1,000 characters.

It should be a general empirical-research principle, not a benchmark-specific instruction.

It should capture, in its own words, the distinction between:

- evidence that a relationship was unhelpful under one regime; and
- evidence that it will remain unhelpful after the system changes.

It may recommend how experiment budgets should respond when previously established relationships deteriorate.

It must not contain:

- X01/X02/X03/X04;
- exact beta1 days;
- the next world's structure or answer;
- a hard-coded sequence of experiments.

Record:

- exact prompt;
- response;
- model;
- usage;
- lesson hash.

Freeze the lesson before the new hidden world is generated.

Do not manually rewrite the lesson after seeing it.

If the call fails operationally, one repair is allowed. If it still fails, stop and report `LESSON DISTILLATION FAILURE`.

---

# 4. One new hidden world, same problem family

Generate exactly one fresh hidden world after the lesson is frozen.

Use the same beta1 world family:

- four anonymous candidates;
- one relationship useful before the change and retired afterward;
- one emerging driver;
- one correlated proxy;
- one noise variable;
- hidden change point;
- unchanged t0-beta instrument;
- unchanged experiment menu;
- unchanged three rounds;
- unchanged total budget of 6 experiments;
- unchanged confirmation segment;
- unchanged truth separation.

The new world's seed must not exist before dispatch.

Do not make the world easier.

Do not tune signal strength.

Do not alter the generator in response to beta1.

---

# 5. Run TWO researcher conditions on the SAME hidden world

This is still one world.

The purpose of the second trajectory is to make the learning question interpretable without building a large benchmark.

## F — Fresh condition

A fresh researcher receives:

- the beta1 research brief;
- no persistent lesson;
- an empty notebook at the start;
- the same model, effort, schema, menu and 6-experiment budget.

This is the control.

## L — Learned condition

A separate fresh researcher receives:

- exactly the same brief;
- exactly the same model, effort, schema, menu and budget;
- the frozen portable lesson from section 3 in a clearly labelled `PRIOR RESEARCH LESSON` section;
- an empty current-world notebook at the start.

It does NOT receive beta1's raw notebook.

It receives only the distilled lesson.

## Hold fixed

Between F and L:

- hidden world;
- candidate ids;
- observations;
- model;
- effort;
- API interface;
- response schema;
- experiment menu;
- number of rounds;
- 6-experiment budget;
- confirmation data;
- evaluation.

The only intended difference is the portable lesson.

Do not let one condition see the other's experiments or conclusions.

Do not rerun either trajectory because its decisions are poor.

---

# 6. Do not turn the lesson into a hand-written policy

The learned condition must still decide what to do.

Do not add code such as:

- "if deterioration then retest rejected candidates";
- mandatory rescreening;
- forced exploration quotas;
- reserved experiments;
- special treatment of a previously rejected candidate.

The lesson is text available to the researcher.

The researcher decides whether, when and how to use it.

This distinction matters.

We are testing whether accumulated research knowledge changes autonomous research behaviour, not whether a programmer can patch the failed policy.

---

# 7. Keep the budget at six experiments

Do not give the learned researcher additional budget.

The hard problem is experiment allocation.

The researcher must decide how to balance:

- confirming an incumbent relationship;
- detecting deterioration;
- screening untested candidates;
- reopening stale negative findings;
- conditional tests where useful.

The six-experiment constraint stays.

Do not add extra experiments because the previous run ran out of budget.

---

# 8. Primary empirical question

The main question is:

> **Does the beta1-derived lesson change experiment allocation in a way that helps the learned researcher respond to a new regime better than the fresh researcher on the same hidden world?**

This is not a claim of general superiority.

One world is an existence test.

Report the trajectories first.

---

# 9. What to measure

For BOTH F and L, record round by round:

1. hypotheses/beliefs entering the round;
2. experiments chosen;
3. results received;
4. belief updates;
5. budget remaining;
6. whether older findings were treated as potentially stale after evidence of change;
7. whether rejected candidates were re-opened and why;
8. whether the emerging information was found;
9. whether the retired driver was removed;
10. whether unsupported noise was avoided;
11. final selection.

Also record whether the learned condition explicitly cites or applies the prior lesson.

Do not score verbosity.

Score behaviour.

---

# 10. Confirmation and truth

As in beta1, the confirmation segment remains unavailable to both researchers.

After both trajectories end, reveal the truth only to the evaluator.

Report for the hidden world:

- retired driver;
- emerging driver;
- proxy;
- noise;
- change point;
- standalone predictive usefulness;
- incremental usefulness where relevant.

Evaluate both final selections with t0-beta and the existing ridge reference.

Do not change the conventional comparator.

---

# 11. Minimal outcome reading

Do not invent an elaborate new score.

Use a simple owner-facing reading.

## `LEARNING SIGNAL OBSERVED`

Use this only if the learned condition demonstrates a materially better research response than the fresh condition in the same world, with behaviour plausibly linked to the carried lesson.

Examples of meaningful improvement include:

- reopening stale negative findings after detecting change;
- finding the emerging driver when F does not;
- finding it materially earlier;
- using fewer wasted experiments on reconfirming an obsolete relationship;
- producing a better supported final selection.

A forecasting gain alone is not sufficient if the research behaviour did not improve.

## `NO LEARNING SIGNAL`

Use this if the lesson is available but does not produce a meaningful improvement in research behaviour or outcome.

## `BOTH SUCCEED`

Use this if both F and L complete the essential research loop. The world was not discriminating enough to demonstrate value from the lesson.

## `BOTH FAIL`

Use this if both miss the essential discovery despite clean infrastructure.

## `INFRASTRUCTURE FAILURE`

Use only for a service/integrity failure that prevents interpreting the paired experiment.

These are descriptive one-world outcomes, not statistical claims.

---

# 12. Research behaviour still matters more than the final label

A particularly important pattern would be:

**beta1**
→ detects deterioration
→ fails to reopen stale negatives
→ misses emerging information

**new world, learned condition**
→ detects deterioration
→ recognizes old negative evidence may be stale
→ reallocates remaining experiments
→ re-tests alternatives
→ finds or better approaches the emerging information

If we observe that, preserve the exact trajectory.

That is more important than making a broad claim from one world.

---

# 13. Cost and scope

Keep this small.

Expected incremental work should be mostly:

- lesson-distillation call;
- one fresh hidden-world generation;
- two researcher trajectories instead of one;
- existing evaluator adapted to compare them;
- concise results document.

Do not perform another beta qualification.

Do not run the full 10-scenario benchmark.

Do not run the previously proposed 72-trajectory learning study.

Do not add a persistent database.

A file containing the frozen lesson is enough for this experiment.

Record:

- lesson-call tokens;
- F tokens;
- L tokens;
- API attempts/refusals/repairs;
- t0-beta forecasts;
- runner time;
- approximate implementation effort.

---

# 14. Freeze and dispatch discipline

Before the scored world exists, freeze:

- the distilled lesson;
- lesson hash;
- F and L prompts;
- model/effort/schema;
- menu and budget;
- generator reference;
- evaluator;
- outcome definitions above.

Run one focused check for:

- truth leakage;
- condition contamination;
- prompt differences beyond the lesson;
- future-data leakage;
- evaluator reproducibility.

Then dispatch ONE scored paired world.

No reroll without owner approval.

---

# 15. Final report

Bring me a concise report with:

## 1. The lesson

Show the exact frozen portable lesson produced from beta1.

Explain what input it received and confirm it contained no next-world information.

## 2. Integrity

Confirm F and L differed only by the lesson and had no access to truth or confirmation data.

## 3. Fresh trajectory

Round by round:
- experiments;
- evidence;
- belief updates;
- final selection.

## 4. Learned trajectory

Round by round:
- experiments;
- evidence;
- belief updates;
- where, if anywhere, the prior lesson affected the decision;
- final selection.

## 5. Revealed world

- retired driver;
- emerging driver;
- proxy;
- noise;
- change point;
- evidence availability.

## 6. Side-by-side comparison

Did L, relative to F:

- reopen stale negative findings?
- detect the emerging driver?
- detect it earlier?
- spend fewer experiments reconfirming the obsolete driver?
- avoid noise?
- produce a better supported final selection?

## 7. Confirmation

Relevant t0-beta and ridge numbers for both final selections and the true emerging information.

## 8. Cost

Actual compute, calls, tokens and implementation effort.

## 9. Outcome

Choose exactly one:

- `LEARNING SIGNAL OBSERVED`
- `NO LEARNING SIGNAL`
- `BOTH SUCCEED`
- `BOTH FAIL`
- `INFRASTRUCTURE FAILURE`

Then answer directly:

> **Did knowledge extracted from the previous failed investigation materially improve the next autonomous investigation in this one controlled world?**

Do not overclaim.

Then stop.

---

# 16. Priority

This is the first small test of accumulated research knowledge.

Do not optimize it into a general memory architecture.

The important sequence is:

**experiment → failure → generalized lesson → new experiment policy → new evidence**

Get that result.
