# Next experiment prompt — t0-beta on real RTE consumption data

You are working in `xuanhuyle/solar`.

Your job is to design and implement **one narrow real-data experiment**:

> **Run the qualified t0-beta model on French national electricity-consumption data from RTE/ODRÉ, using the real covariate capability of t0-beta, and determine what it can do on a forecasting problem the repository already understands.**

This is **not** another synthetic research-loop benchmark.  
This is **not** an opportunity to redesign Solar.  
This is **not** an invitation to add an autonomous researcher.

The purpose is to establish a clean real-world substrate result before we build any Lovable-like forecasting interface.

---

## 0. First reconstruct the existing evidence

Before changing code, read the relevant repository history and artifacts, including at minimum:

- `README.md`
- `solarbench/odre.py`
- `solarbench/forecasters.py`
- `solarbench/probes.py`
- `engine/catalogue.py`
- `engine/data.py`
- `engine/covs.py`
- `engine/arms.py`
- `research_loop_proof/beta1/lab/t0_beta.py`
- `docs/research_loop_proof/BETA1_SPEC.md`
- `docs/research_loop_proof/BETA1_RESULTS.md`
- `docs/experiment_3/T0_STRENGTHS.md`
- `docs/experiment_5/RESEARCHER_PROPOSAL.md`
- `docs/experiment_5/RESEARCHER_PROPOSAL_V2.md`
- `docs/experiment_5/FEASIBILITY_REVIEW.md`
- `docs/experiment_5/PROPOSAL_V2_REVIEW.md`

Reconstruct and state clearly:

1. what RTE/ODRÉ target data already exist in the repo;
2. what RTE's own `prevision_j1` series represents and what is still unverified about its issue time;
3. what the strongest existing simple baseline is for national consumption;
4. what t0-alpha already demonstrated on this problem;
5. what the archived holiday and temperature covariates are;
6. what is already qualified about t0-beta;
7. why the existing t0-beta adapter cannot simply be reused unchanged for a 30-minute, full-day RTE forecast.

Do not rely on memory or prose summaries when the repo can answer the question.

---

# 1. The experiment question

The experiment should answer:

> **On French national electricity consumption, how strong is t0-beta when used zero-shot with only information that would have been available at the forecast gate, and how much do obvious known-future covariates add?**

Use the existing business/operational forecasting convention where possible:

- target: French national electricity consumption;
- source: RTE/ODRÉ `eco2mix-national-cons-def`, `consommation`;
- frequency: 30 minutes;
- forecast target: one local calendar day D;
- forecast gate: **12:00 Europe/Paris on D-1**;
- horizon: the full local day D;
- primary point forecast: t0-beta median;
- primary metric: MAE in MW.

The experiment is deliberately small. Do not add candidate covariates, model search, autonomous discovery, scenario optimisation, or an LLM researcher.

---

# 2. Pre-specified arms

Freeze exactly these decision arms before looking at the scored results.

## A — t0-beta base

Inputs:

- national consumption history available by the gate;
- no covariates.

## B — t0-beta + calendar

Inputs:

- same target history;
- the existing French holiday/calendar information that is genuinely known in advance.

Use the repository's existing construction where valid. Do not invent a new calendar encoding after seeing outcomes.

## C — t0-beta + calendar + archived temperature forecast

Inputs:

- same target history;
- the same calendar input as B;
- the repository's existing **archived temperature forecast** construction, using only forecast values whose issue-time bounds make them legal at the 12:00 D-1 gate.

Use the existing raw temperature construction unless a repository invariant requires a different frozen encoding. Do not tune HDD/CDD transforms on the scored period.

---

# 3. Comparators

Report these comparators on the same scored days wherever possible:

## Naive baseline

Use the existing frozen consumption baseline, currently `blend_50`, exactly as defined by the repo.

Do not retune it on 2026.

## RTE J+1 reference

Use RTE's published `prevision_j1` only as a **reference** unless you can independently verify that its publication/issue timing is comparable with the 12:00 D-1 Solar gate.

Do not feed RTE's forecast into t0-beta.

If same-gate availability cannot be proven from the source metadata, state that clearly and keep RTE out of any pass/fail verdict.

## Optional diagnostic: t0-alpha

If it is nearly free and can be run under the exact same target days, gate, context budget and covariates without touching frozen historical experiment artifacts, report t0-alpha as a **diagnostic only**.

Do not make alpha-vs-beta a gate if doing so complicates the experiment.

---

# 4. Use genuinely new data if available

The preferred scored period is an **untouched 2026 period** that has not previously been used in the repository's model/covariate selection.

Before freezing the period:

1. inspect RTE/ODRÉ coverage through the latest available date;
2. inspect target `nature` / vintage information;
3. inspect `prevision_j1` coverage;
4. inspect archived temperature-forecast coverage;
5. determine the latest contiguous period that supports a fair comparison.

Prefer a substantial 2026 window, ideally from 2026-01-01 through the latest complete month that is available for all required series.

If 2026 data cannot support the experiment cleanly, do **not** silently fall back to previously explored data. Stop and explain exactly why, then propose the smallest valid alternative.

---

# 5. Freeze the data vintage

A previous review identified a real weakness: the target loader did not preserve enough information about RTE data vintage.

Fix this for this experiment.

Every scored run must record at least:

- exact source dataset;
- retrieval timestamp;
- exact start/end dates;
- row counts;
- counts by RTE `nature` / vintage field where available;
- a cryptographic hash of the target values and timestamps;
- a hash/fingerprint of each covariate input;
- a hash/fingerprint of the RTE J+1 reference rows;
- model revision and weight hashes;
- `tfc-t0` runtime version;
- Git commit SHA;
- experiment specification hash.

Do not overwrite or mutate the historical experiment records.

---

# 6. t0-beta integration rule

Use **the actual qualified t0-beta model** already pinned in:

`research_loop_proof/beta1/lab/t0_beta.py`

Do not substitute t0-alpha.  
Do not use a fake adapter.  
Do not reimplement the model.

However, the beta1 adapter is hard-coded for its synthetic research-loop geometry:

- `H = 24`.

RTE consumption is on a 30-minute grid, so a full day normally requires 48 forecast steps, with DST days handled explicitly.

Implement the minimum isolated adapter/generalisation required for this real-data experiment.

Requirements:

- do not change the frozen semantics of beta1 or Final Kernel;
- do not alter prior scored artifacts;
- preserve model-byte verification;
- preserve the minimum runtime requirement;
- preserve non-finite detection;
- support the RTE horizon safely;
- make DST handling explicit and tested;
- make future-covariate shape checks explicit and tested.

Prefer a new experiment-local wrapper over changing frozen research-loop code.

---

# 7. Information-boundary rule

This experiment is only useful if it is point-in-time defensible.

For every forecast day D, enforce:

> **No target value or covariate value may be used unless it was knowable by 12:00 Europe/Paris on D-1.**

Specifically:

- target context ends at the gate;
- calendar variables are allowed only because their future values are deterministic and known;
- archived temperature forecasts must carry source/issue bounds proving they were available by the gate;
- no ERA5 or other realised-weather oracle may enter A/B/C;
- no RTE J+1 forecast may enter A/B/C;
- no future target values may enter preprocessing/scaling/selection.

Add explicit leakage tests.

At minimum, include a history-boundary poison test showing that modifying data after the gate cannot change a forecast.

---

# 8. Preflight before scoring

Before any scored 2026 run, create a preflight that verifies:

1. t0-beta loads from the qualified bytes;
2. the runtime is valid;
3. a 48-step non-DST forecast works;
4. DST day handling is correct;
5. A, B and C all execute with valid shapes;
6. outputs are finite and non-degenerate;
7. repeat loading produces reproducible forecasts within the model/runtime's established tolerance;
8. all covariates obey issue-time constraints;
9. the target and covariate fingerprints are recorded;
10. the same-gate naive baseline is computable.

The preflight must not inspect or summarise the scored-period forecast errors.

---

# 9. Freeze before score

Create a frozen experiment specification before running the scored period.

At minimum create:

- `docs/experiment_6/T0_BETA_RTE_SPEC.md`

The spec must contain:

- question;
- target;
- gate;
- horizon;
- exact scored period;
- exact arms;
- exact comparators;
- metric;
- handling of missing days;
- DST rule;
- target/context length;
- covariate construction;
- model/runtime pins;
- point-in-time rules;
- data-vintage rules;
- statistical summaries;
- interpretation rules;
- explicit non-goals.

Hash the files that determine the result and record the hash before scoring.

Do not change the spec after seeing scored results. Any post-score correction must be documented as a correction, not silently folded into the frozen spec.

---

# 10. Scoring and reporting

For each arm/comparator report:

- number of scored days;
- MAE in MW;
- relative skill versus `blend_50`;
- arm B versus A;
- arm C versus B;
- arm C versus A;
- if timing is comparable, descriptive difference versus RTE J+1;
- monthly breakdown;
- winter/summer breakdown using the repo's already-defined month sets;
- forecast-error distribution;
- any dropped days and exact reason.

Use paired day-level differences and an appropriate block/bootstrap or equivalent interval that respects serial dependence.

Do not introduce a forest of significance tests. The main point is effect size and robustness.

If probabilistic quantiles are almost free to retain from t0-beta, save them for later analysis, but **do not expand this experiment into a probabilistic-calibration project**.

---

# 11. Interpretation rules

Do not declare a "kernel" from this experiment.

Use restrained conclusions.

The result can establish things such as:

- t0-beta is or is not a strong zero-shot instrument on real RTE consumption;
- obvious known-future context materially helps or does not help;
- t0-beta closes or does not close the gap to a professional published reference;
- the substrate is strong enough or not strong enough to justify putting a Lovable-like forecasting interface on top.

The experiment does **not** establish:

- that Solar's autonomous researcher works;
- that non-forecasters can use forecasting safely;
- that a flywheel exists;
- that Solar is a business;
- that t0-beta beats RTE operationally unless timing and information sets are actually comparable.

---

# 12. Decision framing

At the end, answer these questions explicitly:

### Q1 — Is the base instrument strong?

Does t0-beta A clearly beat the frozen naive baseline on the untouched real-data period?

### Q2 — Does context help?

Do calendar and archived temperature produce a meaningful and reasonably stable incremental gain?

### Q3 — How large is the remaining professional gap?

If the RTE reference is timing-comparable, how far is the best beta arm from it?

If it is not timing-comparable, report the descriptive gap and refuse a stronger claim.

### Q4 — Is this substrate good enough for the product experiment?

Would a non-forecaster receiving the best t0-beta result have something plausibly useful enough to justify testing the next layer:

> plain-English forecasting intent → defensible forecast → transparent assumptions → later forecast-vs-actual loop

This is a product-readiness judgment, not a scientific pass/fail claim.

---

# 13. Keep the implementation small

Create only what the experiment requires.

Likely new artifacts:

- `docs/experiment_6/T0_BETA_RTE_SPEC.md`
- `docs/experiment_6/T0_BETA_RTE_RESULTS.md`
- a small isolated experiment runner/package;
- tests for the new adapter/data boundary;
- optionally a dedicated GitHub Actions workflow if needed for reproducibility.

Do not modify Final Kernel files.

Do not rewrite the research-loop architecture.

Do not add a UI.

Do not add an agent.

Do not use the scored outcome to invent a new arm.

---

# 14. Stop conditions

Stop and report rather than patch around the problem if any of these is true:

- the 2026 RTE target period cannot be frozen cleanly;
- archived temperature forecasts do not cover a valid untouched 2026 period;
- t0-beta cannot support the required horizon/covariate geometry without a material model change;
- point-in-time validity cannot be established;
- RTE J+1 timing cannot be established and someone tries to use it as a verdict gate;
- the only way to get a positive result is to tune arms after seeing 2026 errors.

A clean negative result is more valuable than a rescued positive one.

---

# 15. Deliverable

When complete, report:

1. files added/changed;
2. frozen spec hash;
3. preflight result;
4. scored period and exact data vintage;
5. A/B/C performance;
6. naive and RTE references;
7. robustness/slices;
8. integrity checks;
9. what was actually learned;
10. whether this strengthens or weakens the case for building the Lovable-like Solar prototype.

Do not claim more than the evidence supports.
