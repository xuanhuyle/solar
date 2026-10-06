# Human1 — Falsify the narrowed researcher kernel

Read the repository at current HEAD before doing anything. In particular, read:

- `docs/experiment_5/NORTH_STAR_CLARIFICATION.md`
- `docs/research_loop_proof/PHASE0_RESULTS.md`
- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/research_loop_proof/LEARN1_RESULTS.md`
- `docs/research_loop_proof/POLICY1_RESULTS.md`
- `docs/research_loop_proof/DISCOVERY1_SPEC.md`
- `docs/research_loop_proof/DISCOVERY1_RESULTS.md`
- the current `research_loop_proof/discovery1/` implementation
- the current PR description and latest commits relevant to the research-loop programme.

Do not treat this prompt as evidence that the project should continue.

The last frozen result was `NO DISCOVERY SIGNAL`. The predeclared closing line was:

> `NARROW TO HUMAN-SUPPLIED HYPOTHESES`

Take that narrowing seriously.

Do not improve the researcher.  
Do not create another lesson.  
Do not create another policy architecture.  
Do not add persistent memory.  
Do not enlarge the candidate universe.  
Do not give the researcher new methodological advice derived from the previous failures.

The purpose of this milestone is to test whether a meaningful researcher kernel remains **after a human has already supplied a good bounded hypothesis**.

---

# 1. Most vulnerable surviving assumption

The assumption to try to falsify is:

> **If a human supplies a small, genuinely relevant hypothesis set, the existing researcher can turn it into a scientifically supported conclusion under a tight experimental budget, rather than merely choosing a good forecast set or relying on an obvious deterministic test script.**

This is now more fundamental than open-ended discovery.

If the existing researcher cannot reliably adjudicate a good two-candidate hypothesis when the search problem has already been removed, there is little basis for continuing to argue that the current system is an autonomous empirical researcher.

There are two separate questions:

### A. Researcher competence

Can the current researcher reach a correct, evidence-supported conclusion from a human-supplied hypothesis?

### B. Residual agentic value

Does adaptive LLM research planning add anything beyond a fixed deterministic protocol once the hypothesis has been supplied?

Do not blur these two questions.

A result can show competence while also showing that the workflow is fully scriptable.

---

# 2. Milestone name and scope

Call this milestone **Human1**.

Create an isolated:

`research_loop_proof/human1/`

and:

- `docs/research_loop_proof/HUMAN1_SPEC.md`
- `docs/research_loop_proof/HUMAN1_RESULTS.md`
- `.github/workflows/research-loop-human1.yml`
- focused tests only.

Reuse the beta1 / learn1 / discovery1 machinery aggressively.

Preserve all previous experiments, prompts, lessons, results, branches and workflow records unchanged.

This is a disposable falsification milestone, not a new framework.

---

# 3. Researcher condition

Use the strongest existing researcher from Discovery1:

- the lesson-only researcher;
- the same model family and substantive research policy;
- the same frozen lesson;
- no new substantive advice.

Mechanically adapt only what is required to present a **human-supplied two-candidate hypothesis** instead of an eight-candidate search universe.

The researcher must be told, in substance:

> A human analyst has supplied two anonymous candidate variables as a hypothesis worth testing after forecast behaviour changed. You are not being asked to search outside this pair. Determine what the evidence supports about each candidate's current predictive usefulness, including whether one adds value given the other. Use the experiment budget as you judge appropriate. Your final conclusion must distinguish supported evidence from uncertainty.

Do not tell it which hidden role either candidate has.

Do not tell it that one candidate is guaranteed to be useful.

Do not add instructions such as "test each candidate alone", "run conditional tests", "confirm the final set", or any other advice learned from Discovery1. Choosing the experiment sequence is the researcher's job.

---

# 4. Hidden worlds

Reuse the same synthetic regime-change family and t0-beta instrument used by the recent milestones unless a concrete technical reason prevents it.

Freeze **three independent hidden worlds** before any scored run.

Each world contains the familiar hidden roles:

- R: a driver that was useful before the change and retires;
- E: a driver that becomes useful after the change;
- D: a correlated predictive proxy of E with no incremental value once E is known;
- noise candidates as needed by the generator.

The full world remains hidden from the research job.

For Human1, the evaluator constructs a human-supplied two-candidate hypothesis packet. This is intentionally a good hypothesis supplied by an external human; hypothesis generation is not being tested.

Use these three predeclared pair types, one per world:

1. **E + D** — useful driver versus correlated proxy;
2. **E + pure noise** — useful driver versus irrelevant candidate;
3. **E + R** — emerging driver versus a relationship that has retired.

Randomly map the two supplied roles to anonymous candidate IDs in each world.

The researcher sees only the two anonymous IDs and the observed data/results available under the existing truth-separation design.

The fact that the human hypothesis includes E is a benchmark condition, not a discovery claim. State this explicitly in the spec and results.

---

# 5. Timing and experiment budget

Keep the regime-change timing, observation schedule, 7-day forecasting context, t0-beta configuration, result fields and hidden confirmation period as close as possible to Discovery1.

Use **two research rounds** corresponding, where practical, to the existing post-change cutoffs around the recent milestones:

- an earlier mixed/recent window;
- a later fresher post-change window.

Freeze the exact cutoffs before scored worlds.

Give the researcher a total budget of **FOUR experiments per world**, at most two per round.

Use the existing experiment declaration language wherever possible:

- selected covariates;
- optional reference covariates;
- allowed history/window choices;
- paired skill and interval;
- sub-window information already available in the current executor.

Do not add new experiment types unless technically unavoidable.

Four experiments are deliberately enough for a deterministic protocol to test two candidates thoroughly. That is a feature, not a defect: Human1 asks whether the agent contributes anything when the problem is narrow enough to be scriptable.

---

# 6. Fixed deterministic comparator

Before generating any scored world, freeze one deterministic comparator using the same t0-beta instrument, the same data cutoffs and the same four-experiment budget.

Keep it intentionally simple and strong.

A suitable fixed sequence is:

1. candidate A versus no covariate on the first research cutoff;
2. candidate B versus no covariate on the first research cutoff;
3. candidate A conditional on B on the later cutoff;
4. candidate B conditional on A on the later cutoff.

If the existing executor requires a slightly different but equivalent encoding, document it and freeze it before the worlds.

The comparator must not know the hidden roles.

Do not optimize it after seeing any result.

Its purpose is to establish the competence floor for a problem a script can plausibly solve.

---

# 7. Scientific evaluation

Before scoring researcher competence, establish from hidden truth and direct t0-beta evaluation that the world is informative:

- E must have positive post-change predictive value on the relevant observed windows;
- the supplied contrast must actually be distinguishable enough to support the intended adjudication.

If a world is not informative, label it as such rather than manufacturing researcher failure.

For each informative world, report every experiment from the researcher and comparator, then evaluate the final conclusion.

Do **not** use causal language merely because the generator knows the roles. The product question is predictive information.

### Required conclusions by pair type

#### E + D

A scientifically adequate conclusion should:

- support E as currently predictive;
- avoid claiming that D has independent/incremental value unless D given E is actually supported;
- distinguish "D is predictive as a proxy" from "D adds information beyond E";
- avoid unsupported certainty.

Selecting D alongside E is not automatically a failure if the conclusion correctly states that D's incremental value is unsupported. The key test is whether the researcher resolves the ambiguity rather than conflating raw predictive association with incremental information.

#### E + noise

A scientifically adequate conclusion should:

- support E;
- not accept the pure-noise candidate as useful based on noise;
- base the conclusion on its own experiments.

#### E + R

A scientifically adequate conclusion should:

- support E on current/post-change evidence;
- recognize that R's old usefulness is not sufficient evidence of current usefulness;
- not retain R as currently useful without fresh positive evidence.

### Evidence discipline

A conclusion counts as supported only when the researcher's own recorded experiments justify it.

Do not recreate Discovery1's overly narrow criterion that only one exact test shape can count. Use ordinary scientific logic, frozen in the spec before the run.

At minimum:

- a variable called currently useful needs positive evidence on a relevant post-change test;
- a claim of incremental value needs an appropriate conditional comparison;
- a claim that evidence is insufficient may be correct;
- a null interval is not proof of zero effect;
- inference by elimination is allowed only when the relevant conditional evidence logically supports it.

Freeze the exact adjudication rules before the scored run.

---

# 8. Primary metrics

For each world report:

- every researcher experiment in order;
- every comparator experiment in order;
- experiment windows and references;
- which candidate entered which test;
- the researcher's final conclusion verbatim;
- whether each factual/scientific claim in that conclusion is supported by its own experiments;
- whether E was correctly supported;
- whether the supplied distractor was treated correctly for its pair type;
- unsupported acceptance count;
- unsupported rejection/zero-effect claims;
- final-selection confirmation skill, reported separately from research correctness;
- E-alone confirmation skill;
- fixed comparator conclusion;
- experiments used;
- API attempts, refusals, repairs, tokens;
- t0-beta forecast count and wall time.

Do not let a good confirmation forecast rescue an unsupported research conclusion.

---

# 9. Frozen programme reading

Predeclare the programme-level reading before any scored world exists.

Use first-match logic:

1. **INFRASTRUCTURE FAILURE**
   - truth separation, prompt reconstruction, model pinning, execution integrity or evaluator integrity fails.

2. **BENCHMARK FAILURE**
   - fewer than two worlds are scientifically informative for the supplied contrast.

3. **NARROW RESEARCHER FAILURE**
   - the researcher fails the scientific adjudication in at least two informative worlds, especially where the deterministic comparator succeeds.

4. **SCRIPTABLE NARROW KERNEL**
   - the researcher succeeds in all informative worlds, but the deterministic comparator also succeeds in all informative worlds with the same or lower experiment budget, and there is no clear research-efficiency advantage from adaptive planning.

5. **AGENTIC VALUE SIGNAL**
   - the researcher succeeds in all informative worlds and the deterministic comparator fails in at least one because its fixed plan cannot resolve the evidence under the same budget, **or** the researcher achieves the same correct adjudications with materially fewer experiments while preserving evidence quality.

6. **MIXED**
   - anything else.

Do not reinterpret the labels after seeing the outcome.

Human1 is small. Three worlds and one trajectory each are not a rate estimate. State that limitation.

---

# 10. Preflight and integrity

Before the scored batch:

1. freeze `HUMAN1_SPEC.md`;
2. run one focused independent check of:
   - truth separation;
   - pair construction;
   - prompt reconstruction;
   - adjudication-rule determinism;
   - comparator budget matching;
3. fix only confirmed implementation/evaluator defects;
4. repin the spec if required;
5. run one non-scored operational preflight;
6. do not read the preflight for scientific tuning;
7. run the frozen three-world scored batch once.

No rerolls.  
No prompt tuning between worlds.  
No second trajectory because the first is inconvenient.  
No reviewer swarm.

---

# 11. What this milestone does and does not test

Human1 tests:

> whether the current researcher can perform disciplined empirical adjudication once a human has already supplied a good, bounded hypothesis, and whether adaptive LLM planning contributes anything beyond an obvious fixed protocol.

It does **not** test:

- open-ended covariate discovery;
- web search for information sources;
- learning across tasks;
- a new memory architecture;
- t0-beta versus ridge superiority;
- real-market validity;
- product-market fit;
- UI;
- commercial willingness to pay.

Do not widen the interpretation.

---

# 12. Kill logic

The point of Human1 is to make continuation harder to rationalize.

If the researcher cannot adjudicate these supplied two-candidate hypotheses reliably while the fixed comparator can, stop treating the current research policy as a viable autonomous-researcher kernel.

If both succeed and the result is `SCRIPTABLE NARROW KERNEL`, do not call that evidence for autonomous research. It means the forecasting/testing substrate may be useful, but this benchmark does not show that an LLM research planner is necessary.

Only `AGENTIC VALUE SIGNAL` is evidence that adaptive researcher planning itself contributed under this narrowed setting.

---

# 13. Progress over polish

Use existing code.

One short spec.  
One small implementation.  
One focused check.  
One operational preflight.  
One frozen three-world run.  
One results document.

Do not generalize Human1 into an arbitrary natural-language science platform.

Do not modify:

- Phase 0;
- beta1;
- learn1;
- policy1;
- discovery1;
- Experiment 4;
- B1;
- the engine ledger;
- sealed/forward data.

---

# 14. Stop condition

After publishing `HUMAN1_RESULTS.md`, stop.

Do not:

- improve the researcher in response;
- create Human2;
- distill another lesson;
- propose a product;
- widen the hypothesis space;
- run a real-world test;
- reinterpret Discovery1.

Bring the owner:

1. the frozen Human1 question;
2. the exact researcher condition;
3. the exact human-supplied hypothesis construction;
4. the fixed comparator;
5. the three-world result;
6. where the researcher was scientifically correct or unsupported;
7. whether adaptive planning added anything beyond the script;
8. total cost;
9. the programme reading.

End with exactly one of:

- `AUTONOMOUS RESEARCH KERNEL SURVIVES`
- `USE A SCRIPT / HUMAN-DRIVEN WORKFLOW`
- `STOP THIS RESEARCHER LINE`
- `BENCHMARK/INFRASTRUCTURE RESULT ONLY`

Do not continue past that point.
