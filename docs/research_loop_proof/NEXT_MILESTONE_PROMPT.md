# Next milestone — Use t0-beta and get one clean autonomous-research result

We have enough design work.

The priority now is to obtain a meaningful empirical result, not to continue polishing the research infrastructure.

Read the current repository, especially:

- `docs/research_loop_proof/PHASE0_SPEC.md`
- `docs/research_loop_proof/PHASE0_RESULTS.md`
- `research_loop_proof/phase0/`
- `solarbench/t0_pinned.py`
- the Experiment 5 North Star documents

Phase 0 established:

1. **The forecasting-instrument mechanism is real enough to continue.**
   - t0-alpha exploited a newly predictive covariate after only 1–3 post-change days.
   - The gain increased with more post-change evidence.
   - A matched ridge showed a broadly similar adaptation curve.
   - This does not establish t0 superiority, but it establishes that the kind of experiment we need is technically viable.

2. **The first researcher run is not clean evidence about research reasoning.**
   - rounds 1 and 2 were lost to API refusals before the researcher produced any output;
   - five of seven API attempts were refusals;
   - refusal categories were not recorded;
   - with only one effective research round left, the researcher made a coarse pairwise screen and selected a proxy plus an untested noise variable;
   - the frozen historical verdict remains `RESEARCHER FEASIBILITY FAILED`.

Do not rewrite or reinterpret that historical result.

The next milestone is:

> **Run one clean hidden-world experiment with t0-beta and determine whether we can observe an autonomous empirical research loop end to end.**

That means:

**hypothesis → experiment → evidence → belief update → next experiment → discovery / rejection**

This is the result I care about now.

---

# 1. Progress over polish

For this task:

- do not launch large multi-agent review swarms;
- do not redesign Phase 0;
- do not reopen N1;
- do not run another broad researcher-proposal cycle;
- do not build generic infrastructure;
- do not spend significant effort optimizing minor statistical details;
- do not improve documentation unless it affects the scientific interpretation or reproducibility.

Use engineering judgement for ordinary implementation choices.

A review is warranted only if a defect could:

- leak the hidden truth;
- invalidate the experiment;
- make the result uninterpretable;
- break model or API execution.

One focused pre-run check is enough.

When choosing between:

- polishing a minor aspect of the system; and
- obtaining the next significant piece of evidence;

prefer the latter unless the imperfection would invalidate the result.

---

# 2. Adopt t0-beta for new work

t0-alpha remains the instrument used in the historical experiments.

Do not modify:

- Experiment 4;
- B1;
- historical Phase 0 alpha results;
- frozen specifications;
- sealed data.

For all **new research-loop experiments**, use **t0-beta** as the default forecasting foundation model.

Do not run a formal alpha-vs-beta benchmark.

Do not spend time proving that beta improves alpha's exact Phase-A numbers.

The project is not about model-version benchmarking.

The assumption for new work is:

> beta is the current successor instrument and should be used unless it fails to operate correctly for our use case.

---

# 3. Minimal beta qualification only

Before using beta in the hidden-world experiment, perform the smallest technical qualification necessary.

Verify from authoritative model/package information:

- official beta model id;
- compatible `tfc-t0` version;
- model files required;
- covariate API;
- context/horizon interface.

Create an isolated, content-verified beta loading path.

Do not alter the historical alpha loader.

Record:

- model id;
- revision/source;
- relevant file hashes;
- package version;
- retrieval provenance.

Then run only a **small smoke qualification** on a few existing Phase-A worlds.

The qualification asks only:

1. Does beta load reproducibly?
2. Does it accept the required known-future covariates?
3. Are forecasts finite and non-degenerate?
4. Does the emerging covariate produce a clearly positive signal in at least a few representative post-change cases?

Do NOT:

- rerun all 40 worlds;
- compare every alpha and beta bin;
- rerun every context length;
- rerun the hinge battery;
- perform a statistical superiority test;
- tune the world for beta.

If beta passes this basic qualification, move on immediately.

If beta cannot operate reliably, fall back to alpha and report `BETA NOT VIABLE`.

---

# 4. Fix the actual Phase-B failure mode

Before consuming another hidden world, improve refusal observability.

For every researcher API attempt, record:

- stop reason;
- `stop_details`;
- refusal category, if available;
- request id;
- requested model;
- served model;
- usage;
- elapsed time;
- retry/repair number.

The old Phase-B result remains unchanged.

Do not retroactively reinterpret its refusals.

---

# 5. One non-scored researcher preflight

Before the next hidden world, run a small researcher preflight on an expendable/calibration world.

Purpose:

> verify that the researcher API can actually perform the legitimate synthetic research task under the real brief/schema.

This is not a scientific result.

Use the same:

- model;
- effort;
- response schema;
- research brief;
- experiment interface;
- notebook format;

that will be used in the scored run.

Do not coach the researcher toward the correct answer.

Do not show hidden roles.

Do not evaluate its scientific performance.

The preflight passes if it can reliably:

- return valid structured answers;
- request legal experiments;
- complete the sequence without repeated service refusals.

If refusals occur:

1. capture the refusal category;
2. identify the minimal cause;
3. make only the minimal prompt/interface correction necessary for the model to answer;
4. repeat the preflight once.

If it still cannot operate:

stop with:

`RESEARCH INFRASTRUCTURE FAILURE`

Do not spend another extended cycle engineering around it.

---

# 6. Improve one clear weakness in the research brief

The first researcher correctly noted that a pairwise result did not identify which member carried the signal, but nevertheless accepted both.

Add one general scientific rule to the brief:

> Evidence about a multi-variable set applies to the set. It does not by itself establish that every member is useful. Claims about individual candidates require evidence that distinguishes them.

This is generic experimental hygiene.

Do not tell the researcher:

- which variable is useful;
- which variable is noise;
- which pair should be decomposed;
- when the regime changes.

Do not otherwise coach it toward the planted answer.

---

# 7. Run ONE new hidden-world researcher experiment

Only if:

- beta qualification passes, or alpha is explicitly retained because beta is not viable;
- researcher preflight passes.

Generate exactly one new hidden world.

Its seed must not exist before dispatch.

The world should preserve the essential Phase-B structure:

- four anonymous candidates;
- one driver useful before the change;
- that driver becomes obsolete;
- a different driver becomes useful;
- one correlated predictive proxy;
- one noise variable;
- hidden change point;
- fixed research budget;
- multiple research rounds;
- untouched confirmation segment.

Do not make the world easier because the previous researcher failed.

Do not tune it after seeing the result.

---

# 8. Keep the research budget small

Reuse approximately the existing Phase-B scale:

- 4 anonymous candidates;
- 3 research rounds;
- 6 total experiments;
- maximum 3 experiments per round;
- one final conclusion.

The researcher chooses:

- candidate(s);
- reference set if useful;
- allowed window;
- whether to retest something;
- experiment rationale.

The researcher does not see raw arrays.

It receives only experimental results.

The researcher writes no code.

---

# 9. The research trajectory is the primary result

Record the sequence in full.

I want to know whether the researcher:

1. forms an initial hypothesis;
2. chooses an informative test;
3. interprets the evidence;
4. preserves negative results;
5. notices deterioration in a previously useful relationship;
6. investigates another candidate;
7. uses conditional or separation experiments when evidence is ambiguous;
8. identifies newly useful information;
9. avoids unsupported noise;
10. changes its beliefs when evidence changes.

Store:

- every prompt;
- every response;
- every belief table;
- every requested experiment;
- every result;
- usage;
- timing.

Do not summarize away the trajectory.

---

# 10. Distinguish proxy discovery from causal discovery

The purpose is forecasting research, not causal inference.

A correlated proxy that forecasts well is not automatically a failure.

Report separately:

- planted causal role;
- standalone predictive usefulness;
- incremental value conditional on the true driver;
- researcher belief;
- final selection.

The key distinction is:

> Did the researcher discover useful predictive information, and did it understand whether that information was redundant with something else?

---

# 11. Keep a simple script baseline

Retain one frozen scripted strategy under the same experiment budget.

Do not optimize it heavily.

Its purpose is descriptive:

> does adaptive AI-directed experimentation behave differently from a trivial fixed search?

One hidden world cannot establish superiority.

Do not claim otherwise.

---

# 12. Keep ridge as a conventional forecasting reference

Where useful, report the matched ridge result on:

- emerging driver;
- final researcher selection;
- scripted selection.

Do not turn this into another t0-vs-ridge benchmark.

The broader thesis is not:

> t0 must beat ridge.

It is:

> foundation forecasting may reduce the task-specific modelling friction involved in rapidly testing changing information.

---

# 13. Service failure is not scientific failure

For the new run, distinguish explicitly:

## `RESEARCH INFRASTRUCTURE FAILURE`

Examples:

- repeated API refusals preventing the research rounds;
- service failure;
- model mismatch;
- malformed response after the allowed repair;
- research process cannot execute.

## `RESEARCHER FEASIBILITY FAILED`

The system works normally but the researcher performs poorly:

- ignores useful evidence;
- accepts unsupported noise;
- fails to investigate a detectable emerging variable;
- retains a clearly obsolete variable;
- misunderstands experiment results;
- fails to update its beliefs.

Do not count a service/API refusal as scientific evidence against the researcher.

This applies only to the new experiment.

Do not rewrite the historical verdict.

---

# 14. Confirmation segment

Keep the confirmation period unavailable to the researcher.

After the research process ends, evaluate:

- emerging driver alone;
- retired driver alone;
- proxy alone;
- noise alone;
- useful combinations;
- researcher's final set;
- scripted final set.

Evaluate incremental relationships where useful, e.g.:

- proxy given emerging driver;
- emerging driver given proxy.

This allows us to distinguish:

- useful information;
- redundant information;
- unsupported information.

---

# 15. Cost

Record simply:

- beta forecast-days;
- Actions runner time;
- researcher API attempts;
- refusals;
- repairs;
- tokens;
- approximate engineering effort.

Do not create elaborate accounting infrastructure.

---

# 16. Authorized scope

Authorized:

- isolated t0-beta integration for new work;
- minimal beta smoke qualification;
- refusal instrumentation;
- one non-scored researcher preflight;
- one new hidden Phase-B world;
- evaluation;
- concise result documentation.

Not authorized:

- formal alpha-vs-beta benchmark;
- full 10-scenario sandbox;
- N1 implementation;
- changing B1;
- changing Experiment 4;
- migrating frozen experiments to beta;
- opening sealed data;
- broad architecture refactoring;
- another proposal/review cycle.

---

# 17. Pre-run freeze

Before the scored hidden-world dispatch, freeze only the parts required to interpret the result:

- chosen foundation model;
- hidden-world generator;
- candidate roles;
- change-point rule;
- experiment budget;
- researcher brief;
- experiment menu;
- scripted strategy;
- confirmation period;
- verdict definitions.

Do not create an unnecessarily elaborate freeze process.

Run one focused independent check for:

- truth leakage;
- future-data leakage;
- broken verdict logic;
- inability to reproduce prompts/results.

If clean, dispatch.

---

# 18. Do not reroll

Run one hidden world.

If the researcher performs badly:

record the failure.

Do not reroll because you dislike the result.

A rerun requires a separate owner decision.

---

# 19. Final report

Bring me a concise report with:

## 1. Beta qualification

- model/version/hash;
- smoke results;
- pass/fail;
- any reason alpha had to be retained.

Do not give me a large alpha-vs-beta benchmark.

## 2. Research infrastructure

- did the preflight work?
- were there refusals?
- if yes, what category?
- what minimal correction was required?

## 3. Hidden world trajectory

Round by round:

- belief state;
- experiments requested;
- results;
- subsequent belief update.

## 4. Revealed truth

Only after the run:

- retired driver;
- emerging driver;
- proxy;
- noise;
- change point.

## 5. Research behaviour

Did the researcher:

- detect the old relationship?
- notice deterioration?
- investigate alternatives?
- identify emerging predictive information?
- separate ambiguous pairs?
- avoid unsupported noise?
- update its beliefs?

## 6. Confirmation

Show final-set performance and incremental relationships.

## 7. Script

What did the fixed search do?

## 8. Conventional model

Only the relevant ridge comparisons.

## 9. Cost

Actual:
- runner time;
- t0 forecasts;
- API calls;
- tokens;
- approximate implementation effort.

## 10. Verdict

Choose exactly one:

- `RESEARCH INFRASTRUCTURE FAILURE`
- `RESEARCHER FEASIBILITY FAILED`
- `BASIC AUTONOMOUS LOOP OBSERVED`
- `AMBIGUOUS`

Then answer directly:

> **Have we actually observed an autonomous empirical researcher complete a meaningful hypothesis → experiment → evidence → belief-update loop in a hidden changing environment?**

If yes, say exactly what was observed.

If no, identify the single dominant bottleneck.

Then stop.

---

# 20. Priority

Do not optimize the machinery beyond what is necessary to trust the result.

The next milestone is empirical, not architectural.

Move forward.
