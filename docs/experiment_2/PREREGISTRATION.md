# Experiment 2: blinded knowledge-creation benchmark, pre-registration

| Field | Value |
|---|---|
| Document | `docs/experiment_2/PREREGISTRATION.md` |
| Version | v0.1-draft (2026-09-24). It includes the owner's clarification of 2026-09-23 on the t0 research-loop objective (§0.7, §T), the fixes from an adversarial design review (§R.1), and a fix check (§R.2) |
| Status | **DRAFT for owner review. Not frozen.** No pre-registration hash exists; §O.2 defines how it is computed at freeze. Committed for review in draft pull request #2 (branch `experiment-1a-preregistration`), together with Experiment 1A v0.3-draft |
| Companion | `docs/experiment_2/OWNER_REVIEW.md` (decisions requested from the owner) |
| Related | `docs/experiment_1a/PREREGISTRATION.md` v0.3-draft (referee certification); `docs/experiment_1a/OWNER_REVIEW.md` v0.3: Part I, the minimum trustworthy-referee subset (MRS); Part I.5, the 1A parts needed for the first t0 demonstration |
| Experiment 1B status | **`BLOCKED_BY_ACCESS`** (§0.5). Experiment 2 uses no market data |
| Position after the owner's clarification | **Not recommended as the next experiment.** As drafted, this benchmark does not exercise t0 or its covariates (§0.7). The recommended next experiment is the first t0 covariate demonstration, "Experiment 2-T0" (§T), which has no pre-registration yet. This benchmark is kept as a later experiment, to be adapted to use t0 as its forecaster (owner decision 5) |

---

## 0. How to read this document

### 0.1 Authorization boundary

This task authorizes documentation and experimental design only. `[DECISION]`

**Not done in this task:**
- no implementation, and no executable experiment code;
- no simulation or benchmark run;
- no seeds, secrets or commitments generated, revealed or committed;
- no freeze, and no pre-registration hash (P_H) computed;
- no contact with Elexon, IRIS, NESO, ODRÉ, any weather archive or any other external dataset;
- no merge of pull request #2;
- no change to Experiment 0, `solarbench/`, `tests/` or `.github/`.

**The only computations performed** were closed-form arithmetic for the operating characteristics (Appendix A): normal-approximation power with Student-t critical values, exact binomial (Clopper–Pearson) bounds, and deterministic numerical integration. They ran in memory, use no randomness, and wrote no files. The formulas are given so anyone can re-derive the numbers. `[DECISION]`

**Two gates follow.** `[DECISION]`
- Implementation may begin only after the owner has approved and frozen this pre-registration and instructed implementation (§S.3).
- The evaluation ceremony C2-eval, and every evaluation world-run, may begin only after the MRS gate (§B.3) and the post-tuning calibration gate (§P.2) have passed on development worlds.

### 0.2 Labels

Labels have the same meaning as in Experiment 1A §0.2.

| Label | Meaning |
|---|---|
| `[DECISION]` | A pre-registered choice. Changing it after freeze requires an amendment (§S). |
| `[INFERENCE]` | Reasoned, not measured or sourced. It may be wrong, and it is never used as evidence. |
| `[ASSUMPTION]` | A premise the design relies on. If it is false, the stated consequence follows. |
| `[OPEN]` | Unresolved: it needs an owner decision (`OWNER_REVIEW.md`) or a measurement in a non-model calibration stage (§P.2). |

**No experimental results exist.** Nothing in this document is a measured result. Simulation figures in earlier decision memos (labelled "SIM" there) were never saved and are not used here. `[DECISION]`

### 0.3 Sources and precedence

When sources conflict, the higher-ranked one wins, and every material conflict is recorded in §Q rather than resolved silently. `[DECISION]`

| Rank | Source | Role |
|---|---|---|
| 0 | The owner's clarification of 2026-09-23 on the t0 research-loop objective, issued after the instruction that redefined Experiment 2. The core is an AI researcher using t0's covariate capabilities; the immediate milestone is one t0 finding plus a building investigation; full referee certification is a later objective | Governs priorities and sequencing (§0.7, §T). Authorizes no implementation, freeze or P_H |
| 1 | The owner's instruction of 2026-09-23 redefining Experiment 2 | Objective, decisive question, arms, endpoints, kill rule, claim boundaries, authorization boundary |
| 2 | Experiment 1A pre-registration v0.3-draft and its owner review v0.3 | Referee components, controls and seed protocol reused here; the MRS split |
| 3 | Experiment 1 decision memo v2, condensed (`experiment1_decision_memo.md`, session scratchpad), §7 threat model and §18 roadmap | Earlier framing of Experiments 2–4 |
| 4 | Experiment 1 decision memo, full version with its v2 addendum | Shared definitions only |
| 5 | Experiment 0 README (this repository) and the t0 paper (`docs/2609.24559.pdf`) | Facts about t0 and about the French solar data |

The memos in ranks 3–4 live in the session scratchpad, not in this repository. This document is written to be self-contained. `[DECISION]`

### 0.4 Relation to Experiment 1A

- **Experiment 1A is the rigorous referee-certification specification.** Its criteria are preserved unchanged. 1A v0.3-draft only updates status language, adds a note at §H.8, and adds log entries: contradictions CL-30 to CL-41, a review record, and a change-log row.
- **Experiment 2 tests whether the integrated researcher-plus-referee system creates true, replicated knowledge.** It scores every claim against **concealed ground truth**, so its conclusions do not rest on the referee's certified guarantees.
- **Gate.** Experiment 2 is gated by the **minimum trustworthy-referee subset (MRS, §B.3)**, not by a 1A certification outcome.
  - This departs from 1A §H.1 and §H.8 and from memo v2 §17, which gate Experiment 2 on REFEREE-VALID or REFEREE-VALID-WITH-SCOPE.
  - The departure is recorded (§Q, CX-01) and needs owner decision 1. `[OPEN]`
- **No Experiment 2 result counts toward, or substitutes for, any 1A criterion (R1–R7) or outcome.** `[DECISION]`

### 0.5 Experiment 1B status

**Experiment 1B (the GB/Elexon real-data workload) is `BLOCKED_BY_ACCESS`.** It is not a scientific failure, and it has not been redesigned. Experiment 2 neither needs nor uses Elexon, IRIS, NESO or any other market data. `[DECISION]`

### 0.6 Notation and glossary

| Term | Definition |
|---|---|
| day, t | One UTC calendar day. There is no daylight-saving time in 𝒢₂ |
| origin | The end of day t (00:00 UTC of day t + 1). The forecast made at origin t targets y_{t+1} |
| known_at | The earliest time a row may be used. B-REG derives it from the row's publish_time (§C.3). A row is admissible at origin t iff known_at ≤ origin (inclusive; margin 0) |
| world | One synthetic realisation from 𝒢₂ (or from the sealed annex 𝒢₂ᴬ) with one derived seed |
| world-run | One (world, arm) execution. It is its own organisation, with a fresh vault, ledger and budget meters |
| 𝒢₂ | The in-family generator (§C) |
| 𝒢₂ᴬ | The sealed out-of-family annex (§C.9) |
| κ₂ | The campaign configuration (§C.11) |
| ι₂ | The isolation configuration (§B.2) |
| B* | The referee-owned strong baseline (§C.10) |
| claim | A structured statement in the §F schema, positive or negative |
| θ(c) | Relative skill of claim c: 1 − E[ℓ(M_c)] / E[ℓ(B*)] on in-scope days. ℓ is squared error; M_c is B* plus c's features, fitted by the referee learner |
| δ_c | The minimum effect stated in claim c (δ_c ≥ δ_min = 0.01) |
| forward law P | The generator's law for days ≥ 1,460, after the discovery freeze |
| oracle | The harness's Monte Carlo evaluator of θ under P (§J.1) |
| mechanism | A planted term g_j in the outcome equation under P (§C.5) |
| TRK | True replicated knowledge: the number of distinct planted mechanisms covered by an arm's validated, TRUE positive claims in one world (§J.3) |
| MEI | Minimum effect of interest for TRK differences: 0.3 mechanisms per non-null world (§K.3) |
| MRS | Minimum trustworthy-referee subset (§B.3) |
| TCB, TH | Trusted computing base; test harness (as in 1A §B.2) |
| UB_c, LB_c | One-sided upper or lower bound at confidence c |
| t0 | The Forecasting Company's open-weights time-series foundation model (paper `docs/2609.24559.pdf`). Details below the table |

**t0, as far as this document relies on it:**
- **Variants.** `t0-alpha` (about 102M parameters) is the variant Experiment 0 pinned: `tfc-t0` 0.3.2, Hugging Face revision `9b02c5f4…`. It emits the native quantiles 0.1, 0.25, 0.5, 0.75 and 0.9. `t0-beta` (256M) emits 21 native levels from 0.01 to 0.99 (paper §6).
- **Known-future covariates** enter `future_covariates`. They are observed over context and horizon, standardised over the whole span, and read bidirectionally.
- **Past covariates enter the context in one of two ways:**
  - through the public `predict` API, as TARGET-typed variates that are forecast jointly with the target;
  - through a hand-built `TimeSeries` passed to `predict_from_time_series`, as HISTORICAL-typed variates, the role the paper describes (§T.1, M-10).

### 0.7 Clarified objective and alignment of this design

**The owner's clarification of 2026-09-23 (the t0 research-loop objective):**
- The core of the project is an **AI researcher that uses t0's covariate capabilities**. It investigates which information improves forecasts, validates those findings scientifically, and uses the accumulated evidence to guide subsequent experiments.
- The referee supports that research loop. **Full referee certification is a later objective.**
- **The immediate milestone** is one bounded, reproducible, independently confirmed predictive finding using t0, followed by an investigation that builds on it.

**Does this design exercise t0 and its covariates? No, and neither does Experiment 1A.**
- 1A §C.10 and §A.4 item 7: 1A's learner is elastic-net quantile regression, and its learner G is not run.
- §C.11 here: this benchmark's learner is ridge.
- The mismatches are listed in §T.1, M-01 to M-10.

**Consequences for this document.** Its design is kept, because the owner asked for it and because it measures research competence against controls at scale. It is no longer recommended as the **next** experiment. §T gives the recommended adjustment:
- run a t0-centred first demonstration (Experiment 2-T0) first;
- run this benchmark later, with t0 as its forecaster.

`[OPEN: owner decisions 1 and 5]`

---

## A. Question, hypotheses and claim boundaries

### A.1 Decisive question (verbatim from the owner)

> "Given a previously unseen, noisy, point-in-time research universe containing genuine mechanisms, null relationships and spurious signals, can the integrated researcher-referee system produce more novel, correct and independently replicated claims per fixed research budget than matched controls, while controlling false discoveries—and does validated memory improve performance on related future problems?"

**Objective (owner).** An AI-native quantitative research institution: an AI researcher operating inside a deterministic scientific control plane, with validated positive and negative findings accumulating as auditable institutional knowledge.

### A.2 Hypotheses

`[DECISION]`

| ID | Hypothesis | Test |
|---|---|---|
| **H1 (primary, confirmatory)** | The full system (A5: AI researcher + referee + structured validated memory) produces more true replicated knowledge (TRK) per world, at a fixed budget, than each control in 𝒞, without inflating false discoveries. Under the recommended decision-2 alternative, A5 must also be no worse than the memory-ablated A4 by more than MEI | §K.3 intersection–union rule over 𝒞; FDR gates §K.4 |
| **H2 (memory)** | Validated memory improves performance: A5 > A4 | Owner decision 2: confirmatory component of H1 (default), or non-inferiority here with superiority tested in Experiment 3 (recommended) |
| **H3 (referee value)** | The referee adds value: A4 beats A3 on TRK, and A4 and A5 have lower false-discovery rates than A3 | A5 vs A3 on TRK is part of H1. The rest is **exploratory and descriptive** (S11); the FDR component is reported (§K.4, F3), not tested |

### A.3 What Experiment 2 can establish

- **System level.** Whether the full system produces more true, replicated, non-duplicative knowledge per world than the controls in 𝒞, with false discoveries measured against concealed ground truth. This holds only on worlds drawn from 𝒢₂ and 𝒢₂ᴬ after the freeze, under κ₂ and ι₂, with the pinned researcher model snapshot and the stated budgets.
  - Only the H1 contrasts (A5 against each control in 𝒞) are confirmatory.
  - They establish **system-level**, not component-level, superiority.
  - Under the default decision 2, memory (A5 vs A4) is also confirmatory.
- **Component level (exploratory, unadjusted).** Estimates of where any difference arises: search (A4 against A1 and A2), the referee (A4 against A3) and memory (A5 against A4).

### A.4 What Experiment 2 cannot establish

`[DECISION]` The full list is in §N. In brief, synthetic success shows **controlled epistemic competence on this generator family only**. It does **not** show:
1. tradable alpha or any profitability;
2. causal knowledge (truth here is predictive, §J.1);
3. robustness on real data;
4. willingness to pay;
5. that the referee is certified (it has passed only the MRS, §B.3);
6. memory benefit on related future problems beyond the transfer probe (that is Experiment 3, §M);
7. anything about t0 or its covariate pathway. As drafted, the forecaster inside the benchmark is the κ₂ ridge learner (§0.7, §T.1).

### A.5 Mandatory caveat

Every Experiment 2 conclusion, report and evidence package must carry this sentence, verbatim: `[DECISION]`

> "Synthetic knowledge-creation benchmark on generator family 𝒢₂ and its sealed annex only; truth is predictive, not causal; no market data were used; the referee passed only the minimum trustworthy-referee subset and is not certified; this is not evidence of tradable alpha, real-data robustness or willingness to pay."

When an Experiment 1A certification later exists, its own §A.5 caveat is added; it never replaces this one.

---

## B. System under test

### B.1 Components

Nothing below exists yet. Components marked "1A" reuse the Experiment 1A design, retargeted to κ₂. `[DECISION]`

| ID | Component | Responsibility | TCB | Origin |
|---|---|---|---|---|
| B-CLM | Claim validator and hasher | Parses, type-checks and canonicalises claims (§E, §F); rejects referee-owned fields; hashes | Yes | 1A B-SPEC, extended |
| B-REG | known_at registry | Derives known_at from each row's publish_time (§C.3, §D.2) | Yes | 1A |
| B-ASOF | As-of builder | The only path from rows to features. Runs the point-in-time controls inline (§B.3, MRS-2) | Yes | 1A |
| B-DSL | DSL evaluator | Evaluates canonical expressions on as-of data, trailing and causal only (§E) | Yes | New |
| B-BASE | Baseline owner | Defines and fits B* (§C.10) | Yes | 1A |
| B-LRN | Learner | Ridge regression under κ₂ (§C.11) | Yes | 1A B-LRN, with a new learner |
| B-VER | Verdict engine | The G1 test with shifted nulls and two Holm families (§G.2) | Yes | 1A |
| B-VAULT | Vault service | Holds the sealed confirmation segment. Single use; fixed-length receipts | Yes | 1A |
| B-LEDGER | Ledger | One append-only, hash-chained ledger per world-run | Yes | 1A |
| B-DISC | Discovery service | `discover()` (§D.3) on released data only. Outputs are stamped `EXPLORATORY` | No read right on sealed stores | 1A |
| B-EVAL | Sandbox evaluator library | A frozen, non-TCB copy of the B-DSL and B-LRN semantics, placed in the sandbox of A1, A2, A4 and A5 (not A3) so that search is limited by CPU, not by call count (§H) | No | New |
| B-SBX | Sandbox | Runs researcher code and scripted arms under ι₂ (§B.2) | Boundary | 1A, extended for the model agent |
| B-MEM | Memory store | A5 only: structured, validated items (§I.4). Schema-validated; no truth fields | Yes (writes are validated by the TCB) | New |
| B-EVID | Evidence packages | Released only after closure, through the release endpoint (§B.1) | Yes | 1A |
| B-SEED | Seed service | Commitments and derivation (§O) | Yes | 1A |
| B-AUDIT | Audit log | Errors, tamper attempts, blocked accesses and canary scans | Yes | 1A |

**Test harness (TH),** outside the system under test and trusted for ground truth only:
- the generator 𝒢₂, the sealed annex 𝒢₂ᴬ and the truth store;
- the oracle (§J.1), the coverage ablation (§J.3) and the harness replication service (§G.4). **These call the same B-DSL, B-ASOF and B-LRN code as the referee**, so truth is computed with exactly the referee's evaluator and learner code; the estimand is forward-law-trained skill (§J.1);
- the campaign orchestrator;
- the mutant, injection and planted-vulnerability libraries for the MRS;
- the scripted arms A1 and A2, the truth-submitting arms ORC and ORC-A, and A0 scoring (§I);
- the canary planter and scanner;
- the analysis code (§K).

**The agent runner and tool wrappers are a separate least-privilege principal, not part of the TH.**
- **It may reach:** the model API; the sandbox I/O; the TCB tool endpoints (`discover()`, the as-of API, vault submission); the read-only memory snapshot; the metering and recording stores; and the release endpoint, which serves post-closure evidence (the evidence package, and the replication verdict and statistic) only after closure.
- **It has no read right on:** the truth, annex, vault, replication, oracle or seed stores. `[DECISION]`

### B.2 Trust boundary and isolation configuration ι₂

`[DECISION]`

- **Researcher side** (outside the TCB): the model's outputs, every process the agent starts in B-SBX, everything B-SBX writes, and scripted-arm processes.
- **ι₂ extends 1A's ι_1A** (1A §B.2):
  - B-SBX runs in its own user, PID, mount, IPC and network namespaces, with **no network**;
  - its mount namespace holds only: the arm's released data (the as-of discovery bundle, or raw files for A3); B-EVAL (not for A3); a private fixed-size tmpfs; and, for A5, a read-only memory snapshot;
  - no TCB path, sealed store, truth store, annex, seed store or harness code path exists in it (lookups return ENOENT).
- **Model access.** The agent runner calls the model provider's API from outside the sandbox.
  - Server-side tools (web search, web fetch, code execution) are disabled.
  - Every request and response is recorded byte for byte.
  - The sandbox cannot reach the API or any other host.
- **Canaries.** Unique random strings are planted in every sealed store: vault rows, replication data, truth store, annex, seed store and B-AUDIT (§O.4). The scanner checks every sandbox-visible byte, every model request and response, every claim and every memory item.
- **Conformance.** A conformance script (TH) asserts all of the above, including the runner principal's access set, before every world-run. A failed assertion is a harness error (§C.12).
- **Scope.** As in 1A, conformance is checked, not attacked. Co-residency, microarchitectural and filesystem-metadata channels are untested.

### B.3 Prerequisite gate: the minimum trustworthy-referee subset (MRS)

**Purpose.** Experiment 2 scores claims against concealed ground truth. Many referee failures therefore show up **inside** the benchmark, as measured false discoveries or lost power. The MRS targets the failures the benchmark could **not** see:
- leaks of ground truth or sealed data into the researcher side;
- point-in-time leaks that would help every referee arm equally (for example LK13, a vault-to-discovery leak);
- nondeterminism that would make results unreproducible;
- evaluator, learner or oracle faults.

The oracle calls the referee's own B-DSL, B-ASOF and B-LRN (§B.1), so an evaluator or learner bug would be reproduced in the truth itself. Protection against such bugs rests on MRS-2 (DC), MRS-3 (LKD1–LKD8) and the closed-form checks of MRS-11. **The MRS does not certify the referee.** `[DECISION]`

**When and on what.**
- The MRS runs on κ₂ and 𝒢₂ development worlds (ceremony C2-dev), before the evaluation ceremony.
- Any failed item stops the experiment for an owner decision: fix and rerun, or stop.

**Binding to the evaluated build** `[DECISION]`:
1. A pre-registered **component-to-MRS-item map** lists, for each item, the TCB components, B-EVAL, the TH and runner components (agent runner, tool wrappers, conformance script, canary scanner) and the κ₂ settings (including λ) that item depends on.
2. For every item that passes, the SHA-256 of each mapped component, the lock file and the container digest are recorded. Those hashes and the MRS results go into F_H(2-eval).
3. The code-freeze build must be **byte-identical** to the MRS-tested build for every mapped component.
4. Any change to a mapped component after the item passed requires rerunning every item mapped to that component, on fresh development worlds, before C2-eval. This includes a fix made after another item failed, and any tuning change to the agent runner or tool wrappers.
5. MRS-1's model replay and MRS-9 therefore run after tuning ends (§P.2). λ is frozen before MRS-4 and MRS-5 run.

**Inline controls are metered to the TH, not to the arm** (§H). They run at 1A's 200 origins per world:
- on B*;
- on every submitted or asserted claim;
- on a sample of `discover()` expressions, stratified so that every operator type in the world-run's `discover()` expressions is checked at least once, plus a uniform 1-in-50 sample.

The sample is drawn with seed purpose `inline` (§O.3) and is hidden from the arms. The number of expressions checked per world-run is reported. `[DECISION]`

**The MRS items:**

| ID | Check | From 1A | Pass rule |
|---|---|---|---|
| MRS-1 | **Determinism and record/replay.** Two same-machine runs of 5 development worlds for each non-model arm. Replay of 5 recorded tuning world-runs of A3–A5, made on the code-freeze agent runner and TCB, from their recorded model outputs | EK1; R7 (partial) | 0 differing bytes in verdicts, receipts, evidence packages, ledgers, replication results, oracle grades and scores |
| MRS-2 | **Inline point-in-time controls** TE, PO, LP, VS, TI, CI (day assignment and the one-day horizon), LN, AB, AC, CK, FP, DA, as in 1A §G.4.1 and sampled as above. Plus **DC** (DSL causality): for each checked operator, features rebuilt after rewriting all data with valid day > origin are byte-identical. Plus **EV** (evaluator agreement): B-EVAL outputs are byte-identical to `discover()` for the sampled expressions | §G.4.1 | 0 INVALID world-runs on 20 clean development worlds. During the campaign, a control failure makes that world-run INVALID (§G.5) |
| MRS-3 | **Leak mutants**, each with a κ₂ magnitude, a designated control and a liveness artefact (table below). Trial definition below | §G.4.2 | Each mutant live on 5 development worlds (1A liveness rule), then detected (world-run INVALID) in 20/20 trials |
| MRS-4 | **G1 size screen, positive family, test mode.** On 400 null development worlds, with every claim's δ_c set to 0 (a harness test mode that bypasses the §F grid, so that H0 sits at θ = 0, 1A's boundary). The batch is HA₂: the 4 atoms with the highest discovery t among the 35 × 2 legal `S(series, vintage)` atoms (every series except Y, §E.2), distinct drivers. No replication | EK4 / R1 screen | Fail iff LB₉₅(x, 400) > 0.05, i.e. x ≥ 28 worlds with ≥ 1 PASS |
| MRS-4N | **G1 size screen, negative family.** On 400 in-family non-null development worlds, the exact DSL encoding of up to 2 planted mechanisms per world is submitted as a negative claim. δ_c is set to the largest §F grid value ≤ θ̂_o(encoding) − 0.01, and a mechanism is skipped if that value is below δ_min, so H0 (θ ≥ δ_c) holds with a margin | New | Fail iff x ≥ 28 worlds with ≥ 1 negative PASS |
| MRS-5 | **Positive control PC-G1** in the MRS-4 test mode: a vault-snooping analyst against a deliberately broken G1 that allows vault reads, on the same 400 null worlds | PC-G1 | Must fire: x ≥ 73 of 400. At EK-B1, before MRS-5 is scored, S-GEN shows on separate development worlds (stream `dev-mrs`) that this rule is reachable in test mode; if it is not, the experiment stops for an owner decision |
| MRS-5N | **Positive control PC-G1N**: a deliberately broken negative statistic (the sign of d⁻ flipped), on the MRS-4N worlds | New | Must fire: x ≥ 73 of 400 |
| MRS-6 | **Receipt invariance**: 50 pairs of worlds sharing everything before the vault and differing after, plus mutant M-R1 (receipt length depends on the first claim's vault sign) | R5.G1 | 50/50 pairs byte-identical, and M-R1 detected |
| MRS-7 | **Tamper and sealing.** 1A's V1–V5, V7 and V8, plus V12 (path traversal) and V13 (a readable truth store, annex, replication store, seed store or B-AUDIT). Each gets 20 scripted attempts from the sandbox and U_V liveness. V13 also gets 20 attempts made with the runner principal's credentials | R6 subset, plus V12 and V13 | Each V: 20/20 blocked and 20/20 logged |
| MRS-8 | **Canaries**: mutant M-CAN exposes one canary through each sealed store in turn | New | Each exposure detected; 0 canary hits in all clean MRS runs |
| MRS-9 | **ι₂ conformance** for the agent sandbox, the model relay and the runner principal's access set (§B.1, §B.2) | ι_1A conformance | All assertions hold on every MRS world-run |
| MRS-10 | **Metadata uniformity.** IDs are fresh random tokens (§C.2) and padded file sizes are used. A deterministic metadata probe (logistic regression on catalogue metadata, trained on 40 development worlds and evaluated on 40 others) is run for three role labels: mechanism component (driver or regime series); trap; and trap within the subset whose harness-computed `discover()` statistics are attractive (§G.5) | §C.8 | LB₉₅ of every AUC ≤ 0.55 |
| MRS-11 | **Oracle validation and generator self-checks.** Details below the table | §C.12 | See below |

**MRS-11 in full.**
- **Where it runs.** On 20 linear-Gaussian validation worlds: Gaussian noise, no revisions, **row missingness 0**, K = 160, a training draw of 10⁵ days (§J.1) and about 10⁵ test days per draw. The achieved s_o is reported for every checked claim.
- **What is compared.** The oracle's θ is compared with a closed form for these claim classes:
  - true-mechanism atoms;
  - null-series claims (θ = 0 up to the O(1/n) finite-training term);
  - correlated-null and proxy claims (closed form from the joint Gaussian covariance);
  - the linear operators lag, diff, ma and sub;
  - hinge, clip and gt (by one-dimensional Gaussian quadrature);
  - scope-gated claims (truncated-Gaussian moments);
  - the DSL encodings of every trap archetype whose population value under P has a closed form. That is all six, with TRAP-REV on a validation world type with revisions.
- **Also checked:** the coverage computation, against a_j·θ_j (§J.3), and the §C.12 self-checks.
- **Trap design check.** On linear-Gaussian stress worlds with persistent strong mechanisms (driver φ = 0.97, θ_solo = 0.15, J = 4), the closed-form population θ of every trap archetype's single-series encodings (§C.6) is computed and must be < δ_min. This includes TRAP-RED at lags beyond t − 8 and TRAP-LAG at its actual lag.
- **Pass rule, per claim:** |θ_oracle − θ_closed| ≤ c·s_o + 10⁻³, with c the t_{K−1} quantile at 0.01/(2·n_checks). n_checks is fixed by the validation seeds before the run.
- **Pass rule, in aggregate:** |mean signed error| over all checked claims ≤ 2·SE + 5·10⁻⁴.
- Every self-check passes.

**MRS-3 mutants (κ₂ column)** `[DECISION]`:

| Mutant | κ₂ magnitude | Designated control | Liveness artefact |
|---|---|---|---|
| LK01 | Admission uses known_at − 1 day | TE | Features |
| LK02 | Vintage selector returns the highest vintage regardless of known_at | VS | Features |
| LK03 | Admission on valid_day ≤ origin day, ignoring known_at | TE | Features |
| LK06 | A feature is built from y_{t+1} | LN | Features |
| LK07 | Scalers, medians and rank tables fitted on the full sample | TI | Fitted parameters |
| LK09 | Label admission on valid day instead of known_at, live through y at day 1,460 (the first label after the freeze) | LP | Coefficients |
| LK10 | Deduplication keeps the last-uploaded row per valid day | VS | Features |
| LK11 | λ or another frozen κ₂ parameter selected on vault or confirmation data | DA | λ table |
| LK12 | Imputation with the full-sample median | TI | Fitted parameters |
| LK13 | B-DISC reads vault-period rows or forecasts | AB | `discover()` outputs |
| LK15 | Cache key omits configuration and code identity | CK | Cache key |
| LK16 | Fingerprint hashes NaN as −1 | FP | Fingerprint |
| LK17 | Scored days dropped when a claim feature is missing, in M_c only | AC | Scored-day sets |
| LK18 | M_c reads the final-vintage Y where B* reads the first release | AC | Features |
| LK21 | Admission uses the metadata's nominal lag instead of per-row known_at | TE | Features (live on worlds with TRAP-LAG) |
| LKH | Horizon mutant: target y_t instead of y_{t+1} | CI | Scored pairs |
| LKD1–LKD8 | Centred moving average; rolling z-score with the full-sample mean; rank over the full sample; hinge, gt or clip quantiles fitted on the full sample; diff reading forward; negative lag accepted; scope predicate reading the outcome; `first` selector returning the final vintage | DC (LKD7 also RV-style validation in B-CLM) | Features or validation result |

**MRS-3 trial definition.**
- **Batch.** The fixed batch is defined by role, and the harness resolves the IDs in each world: a TRAP-LAG encoding at its nominal lag; a revised series at vintage `asof`; D1; and lag[7] of Y.
- **Worlds.** Development worlds are selected deterministically, from stream `dev-mrs`, so that each contains TRAP-LAG and TRAP-REV.
- **Moved to "Not in the MRS".** A mutant that cannot be live on the κ₂ grid (known_at at 23:00, origin at 00:00) moves out before freeze, with its reason. LK23 (known_at ≤ t + 60 s) is out for this reason: the daily grid has no sub-day boundary.

**Not in the MRS** (full institutional certification only):
- R1 and R4 at certification sample sizes;
- the adaptive-attack cells AT1–AT13 and KF;
- R2 and the clean-room reference;
- R3 at 100 trials per class;
- R5 for G2 and G3, and the wall-clock timing rig;
- R7 across architectures;
- G2 and G3;
- leak classes LK08 (DST: κ₂ has none), LK04, LK05 and LK19 (injections into fields 𝒢₂ does not have), LK14 (covered by LKD7), LK20 (G3), LK22 (half-hour units) and LK23 (no sub-day boundary);
- V6, which in 1A is detected only by the recorder cross-check RC, and 𝒢₂ has no recorder;
- the LLM red team.

`[DECISION]`

The guarantees the MRS does and does not provide are tabulated in `docs/experiment_1a/OWNER_REVIEW.md`, Part I. **If this section and that table conflict, this section wins.** `[DECISION]`

**MRS reopen rule** `[DECISION]`. If an audit finds a leak or sealed-store exposure that the MRS should have caught:
- **Before campaign close (§K.8):** the MRS result is revoked. The affected world-runs, including every later A5 world-run whose memory snapshot depended on an affected run (§I.4), are rerun after a fix on the same evaluation worlds (A5 in the original order from the last clean snapshot, §I.4), so the analysis stays paired, unless the owner declines the rerun (§L rule 1(b)). Every dependent conclusion is suspended until then. If the leak is a SUT-attributed critical-leak event (§K.5), KILL-LEAK stands, and a KILL-FUTILITY already released at EK-B2 (§K.7) stands; in either case the rerun serves only as input to any new pre-registration and cannot change the outcome.
- **After campaign close:** a finding may suspend the outcome while it is attributed. If the §K.5 attribution map assigns it to the SUT (unattributable findings included, as the map requires), the outcome becomes KILL-LEAK or KILL-REPRO, whatever the earlier outcome. If the map assigns it to the TH, a CONTINUE is withdrawn and reported as "not established", and an AMBIGUOUS outcome is unchanged. **It never converts a KILL or AMBIGUOUS into VOID-BENCHMARK, and it never triggers a rerun** (§L).

### B.4 Authorship and separation

`[DECISION]`

| Session | Writes | Must not see |
|---|---|---|
| **S-GEN** | Generator 𝒢₂, the sealed annex 𝒢₂ᴬ, truth store, oracle, coverage ablation, harness replication, orchestrator, conformance script, MRS libraries, canaries, ORC, ORC-A, and A0 scoring (the AUC against the truth store, inside the analysis code) | — |
| **S-REF** | Every TCB component, and B-EVAL | The annex; any world |
| **S-SCR** | The scripted arms A1 and A2, built only from §D.3, §E, §F, §G, the Appendix C allowed content and the tuning worlds | §C (beyond what Appendix C allows); the annex; evaluation worlds |
| **S-AGT** | The agent runner, the brief, the A0 prompt and runner, the tool schemas and descriptions, their default parameters and any helper code, for A0 and A3–A5, tuned on the tuning worlds only | §C (beyond what Appendix C allows); the annex; evaluation worlds; the S-GEN parameter tables |

- **Model separation** `[OPEN: owner decision 10]`.
  - S-GEN uses a different model snapshot from the researcher snapshot that runs A0 and A3–A5, where one is available (owner decision 10).
  - The recommended option under decision 10: the annex forms are chosen by the owner, or by an author outside the model family (a human, or a model from another vendor), from a longer sealed list.
  - The residual common-model risk is stated in §N, item 12.
- **Artefact audit.** A separate session checks every S-SCR and S-AGT artefact (code, prompts, tool schemas, constants, priority orders) against the Appendix C forbidden list.
  - **Tool wrappers must be thin pass-throughs** of the §D.3 interfaces, with no candidate generation, ranking or filtering.
  - Tool content must be identical across A3–A5, except for the Appendix C arm differences.
  - A constant specific to §C (for example "hinge only at {0.5, 0.75}", or "gate only by binaries") is allowed only if the audit record cites a ledgered tuning run, and the feedback release (§B.4) from which the constant was chosen.
  - The check is ledgered and hashed into F_H(2-eval).
- **Tuning parity.**
  - S-SCR and S-AGT each get at most 10 engineer-days and the same 40 tuning worlds (development indices 40–79).
  - **Tuning and EK-B1 worlds are null or in-family only**, in the §C.7 null:non-null ratio of 1:4, with every non-null world in-family (for example 8 null and 32 in-family of 40, as at EK-B1). Annex worlds are generated under C2-dev only for S-GEN's self-checks and for the sealed out-of-family calibration of §C.9 (ORC-A and the frozen A1, stream `dev-oof`), which releases only pass or fail. Their contents and per-world results are seen only by S-GEN and the owner.
  - **Tuning feedback is identical for both sessions:** per world-run TRK, FDP at both levels, and validated-unit counts. No mechanism, trap, proxy or world-type identities are given. Every feedback release is ledgered.
  - A1 and A2 may be rerun on the tuning worlds without a run cap, while A3–A5 tuning is capped at ≤ 60 model world-runs. This asymmetry favours the control and is an accepted deviation (§Q.2, DV-08).
- **Freeze.** The SHA-256 hashes of A1, A2, the brief, the A0 prompt and the agent code are ledgered before the post-tuning calibration gate (§P.2) and included in F_H(2-eval) at the code-freeze commit.

---

## C. Generator family 𝒢₂

Every material degree of freedom is pre-registered (`[DECISION]`) or flagged `[OPEN]`. The generator belongs to the TH. **Worlds are generated only after the freeze, from seeds that do not exist yet (§O).** `[DECISION]`

### C.0 Parameter table

`[DECISION]`, subject to one calibration amendment (§P.2).

| Parameter | Value |
|---|---|
| Resolution | Daily, UTC, no DST |
| Segments | §C.1 |
| Catalogue size | M = 36 series per world, including the outcome Y and the two disclosed drivers D1, D2 |
| Latent factors | 6 latent AR(1) factors F₁…F₆, each with φ ~ U[0.5, 0.97] |
| Idiosyncratic processes | AR(1), φ ~ U[0.3, 0.95] |
| Factor loadings (non-binary, non-trap series) | a_i ~ U[0, 0.8]; x_i = a_i·F_{k(i)} + √(1 − a_i²)·U_i, with k(i) uniform on {1…6}. Every x_i has unit stationary variance |
| Trap base components | Factor-free: a_i = 0, a pure AR(1) with φ from the idiosyncratic law (§C.6) |
| Publication lag L_i | 1, 2, 3 or 5 days, with probabilities 0.4, 0.3, 0.2 and 0.1. **Exceptions:** Y (L = 0); D1, D2 and all three binary series (L = 1); TRAP-LAG (the actual lag is the nominal lag + 10) |
| Revisions | Each non-binary, non-trap series other than Y, D1 and D2 is revised with probability 0.5; traps other than TRAP-REV with probability 0.4, so that P(revised \| trap) = 0.5 (the other traps take 5/6 of trap slots and TRAP-REV is always revised). The first release is x + η, with η ~ N(0, r_i²) and r_i ~ U[0.2, 0.6]; the final vintage equals x and is published R_i ∈ {7, 30} days after the first release (equally likely). **Exceptions:** binary series, D1 and D2 are never revised; Y has its own rule (§C.3) |
| Row missingness | 0.5% of first-release rows, independent of everything else |
| Outcome noise ε (in-family) | Student t₅, scaled to unit variance |
| Outcome AR | ρ₁ ~ U[0.2, 0.5], ρ₇ ~ U[0, 0.2] |
| Seasonality | Day-of-week effects ~ N(0, 0.3²), centred; annual amplitude A ~ U[0.2, 0.6] with phase U[0, 2π) |
| Disclosed drivers | b₁, b₂ ~ U[0.3, 0.6] |
| Mechanisms per non-null world | J ~ Uniform{2, 3, 4} |
| Phantom drivers per null world | J′ ~ Uniform{2, 3, 4}: generated exactly as mechanism drivers, but with no effect on Y |
| Mechanism types (in-family) | LIN, HNG and REG, uniform (§C.5) |
| Mechanism strength | Standalone skill θ_j^solo ~ LogUniform[0.05, 0.15], set by joint calibration (§C.5) |
| Traps per world | 3 archetypes drawn without replacement from 6 (§C.6), in null and non-null worlds alike |
| Proxies | For each mechanism driver or phantom driver, with probability 0.5, one proxy series (§C.5) |
| Binary series | 3 per world: the regime series S and 2 null binary series. All are two-state Markov with mean spell 60 days, L = 1, never revised |

### C.1 Calendar and segments

`[DECISION]`

| Segment | Days | Use |
|---|---|---|
| Warm-up | 0–364 (365) | Feature history and training only |
| Discovery | 365–1,459 (1,095) | Released to every arm, as of the discovery freeze |
| Discovery freeze ("now") | End of day 1,459 | Rows with known_at ≤ freeze are released; nothing later |
| Embargo | 1,460–1,489 (30) | Unused |
| Confirmation vault | 1,490–2,584 (1,095) | Sealed; single use (§G.2). 78 blocks of 14 days; the last 3 days are dropped |
| Replication | A fresh, independent draw from the forward law P: 365 warm-up, 1,095 training and 1,095 test days (§G.4) | Harness only |
| Oracle | K fresh training draws and 5,000 test days per draw, from P (§J.1) | Harness only |

**Forward law.** The law of every day ≥ 1,460 is P. P equals the discovery-period law except for break traps (§C.6, TRAP-BRK). Truth, confirmation, replication and the oracle all refer to P. `[DECISION]`

### C.2 Catalogue roles and identifiers

Each world's 36 series are, in a per-world random order:
- **Y**, the outcome;
- **D1, D2**, the disclosed baseline drivers;
- **J mechanism drivers**, or J′ phantom drivers in null worlds;
- **proxies** (0–4) of those drivers;
- **3 binary series** (S and two null binaries);
- **3 trap series**;
- **null series**: the remainder, 19–25 in every world, including correlated nulls through shared factors.

**Identifiers.**
- Each world's series IDs are fresh 12-character base-32 tokens drawn from seed(`permute_ids`, stream, index).
- They are **unique across all development, evaluation and probe worlds**. The only exception is S7 siblings, which inherit their parent's IDs by design.
- The role labels Y, D1 and D2 stay visible. Series IDs carry no meaning across unrelated worlds.

`[DECISION]`

### C.3 Publication, revision and known_at

`[DECISION]`
- **Stored row schema** (1A §C.4a, reduced to daily rows): `series_id`, `valid_day`, `vintage_no`, `publish_time`, `value`, `is_missing`.
- **known_at is not stored.** B-REG derives it as known_at = publish_time, which is 1A §C.4a's rule with upload_time = publish_time. A TH-side recomputation of every known_at from the publication law below is a harness cross-check.
- **Regular series:** the first release of valid day s is published at the end of day s + L_i, minus 1 hour. The final vintage (revised series only) is published R_i days later.
- **Y:** the first release is published at the end of day s, minus 1 hour. A revision, Y plus N(0, 0.1²) noise, follows 7 days later. **The target is the first release.**
- **D1, D2 and binary series:** L = 1, never revised.
- **Metadata** shown to arms:
  - the ID;
  - the nominal publication lag (for TRAP-LAG, the understated nominal lag);
  - whether the series is revised;
  - a unit class drawn uniformly from {level, rate, index, count}, independently of role.

  The metadata never states a role, except that Y, D1 and D2 are identified: they are the task and the disclosed baseline.

### C.4 Outcome equation

For the forecast made at origin t: `[DECISION]`

y_{t+1} = μ + ρ₁·y_t + ρ₇·y_{t−6} + dow(t+1) + A·sin(2π·doy(t+1)/365.25 + φ_A) + b₁·D1(a_{D1}(t)) + b₂·D2(a_{D2}(t)) + Σ_{j∈J} g_j(t) + σ·ε_{t+1}

- σ = 1 and μ = 0.
- **Availability.** For series i, the latest valid day available at origin t is a_i(t) = t − L_i.
- Every mechanism g_j(t) is a function of **true** driver values at a_i(t). At origin t, a revised driver is observable only as its first release, so it is observed with attenuation.

### C.5 Planted mechanisms (in-family)

`[DECISION]`

| Type | g_j(t) | Parameters |
|---|---|---|
| **LIN** (lagged linear) | β_j·x̃_i(a_i(t)) | x̃ is the driver standardised to its stationary law |
| **HNG** (threshold / hinge) | β_j·max(0, x̃_i(a_i(t)) − c_j) | c_j is the stationary quantile q ∈ {0.5, 0.75}, equally likely |
| **REG** (regime-conditional) | β_j·x̃_i(a_i(t))·1{S(a_S(t)) = 1} | S is the regime series; a_S(t) = t − 1 |

- **Drivers** are distinct non-binary series, chosen uniformly among the non-trap, non-disclosed series.
- **Proxies.** A proxy of driver i is ρ·x_i + √(1 − ρ²)·V, with ρ ~ U[0.6, 0.9] and V an independent AR(1). Its lag and revision are drawn from the base distributions.
- **Joint calibration.** θ_j^solo is the oracle's standalone skill of B* plus the exact true-value mechanism feature, against B*, under P, with all other mechanisms present.
  - Every β is set jointly by Gauss–Seidel sweeps of per-mechanism bisection, on the fixed `calib` draws with common random numbers, until every |θ̂_calib,j − target_j| ≤ 0.002 on those draws.
  - There are at most 20 sweeps; after that the world is a harness error.
  - TRAP-BRK is calibrated inside the same sweep under the discovery-period law (days < 1,460, break mechanism active).
  - The achieved s_o is recorded for every mechanism.
- **Discoverability.** Every in-family mechanism is exactly expressible in the DSL (§E), up to first-release attenuation of non-binary drivers.

### C.6 Traps and decoys

**Truth rule.** Every trap is **false under predictive truth** (§J.1) for its **single-series encodings**: the trap series under any §E.2-legal chain of unary operators, with no other series. Their forward, point-in-time skill over B* is below δ_min.
- Two-series expressions that combine a trap with lag[k](Y) (k ≥ 7) or with another series can be predictive given B*. The oracle grades those like any other claim.
- The base stochastic component of every trap is factor-free (§C.0).
- Each world draws 3 of the 6 archetypes.

`[DECISION]`

| ID | Archetype | Construction | Why it is attractive | Truth under P (single-series encodings) |
|---|---|---|---|---|
| TRAP-REV | Revision look-ahead | A revised series whose first release is a factor-free null AR(1) w_s, and whose final vintage (R ∈ {7, 30} days) is w_s + λ·ε_{s+L+1} | A researcher who aligns final vintages by valid day sees the future outcome innovation; λ is set so that the leaky skill is 0.15–0.30 | Null: the final vintage is never available at the origin where it would help |
| TRAP-LAG | Publication-lag trap | Metadata states nominal lag L_nom; the actual lag is L_nom + 10. Values: P_s = ε_{s+L_nom+1} + N(0, 0.5²) | Aligning by nominal lag uses values published after the target is realised | Null given B*: the admissible value carries only innovations ε_{t−9} or older |
| TRAP-SEL | Finite-sample spurious (discovery-selected) | The harness draws 2,000 factor-free null AR(1) paths over days 0–1,459 and keeps the one with the highest **first-release (point-in-time)** discovery-period incremental skill over B*. After day 1,459 it continues as an independent AR(1). The pool stays at 2,000: the selected path is attractive among catalogue atoms (expected maximum null t ≈ 3.4), but a full-budget screen of derived expressions can reach null t ≈ 4.2–4.8, depending on the cost per evaluation (Appendix A.4), so TRAP-SEL mainly lures narrow screens. EK-B1 reports its selected t against the arms' search maxima | High discovery skill, by selection | Null |
| TRAP-RED | Redundant given B* | D1 + N(0, 0.3²) | Predictive against any baseline without D1 | Null given B*, which holds D1 at 8 lags (§C.10) |
| TRAP-SEAS | Seasonal confound | The outcome's annual seasonal term plus factor-free AR(1) noise | Predictive against a baseline without seasonality | Null given B* |
| TRAP-BRK | Break after discovery | A LIN mechanism (θ^solo ~ LogUniform[0.05, 0.15]) on its own factor-free driver, active only for days < 1,460 | Genuine during discovery | Null under P |

**Trap redraw.** If a trap fails its §C.12 truth check, only that trap's parameters are redrawn within the same archetype, from a pre-registered seed sub-stream, at most 5 times. The check uses `calib`-purpose oracle seeds, not the grading draws. All of this happens before TRUTH_H is ledgered, and the redraw count is recorded in the truth store. If the redraws run out, the world is a harness error. `[DECISION]`

**Proxies and correlated series** that are genuinely predictive given B* are **not decoys**. They can earn partial or full coverage of the mechanism they proxy (§J.3), and are reported as "proxy-true".

**Phantom drivers and their proxies** in null worlds are null series. They cannot earn coverage.

### C.7 World types and mixture

`[DECISION]`

| Type | Share | Content |
|---|---|---|
| Null | ⌈N/4⌉ worlds (about 20%) | No planted mechanism (J = 0). J′ phantom drivers, with their proxies ("proxies-of-nothing"); traps, nulls and binaries as usual |
| In-family non-null | 0.8·N | §C.5 mechanisms |
| Out-of-family non-null | 0.2·N | Drawn from the sealed annex 𝒢₂ᴬ (§C.9) |

- N is the number of non-null evaluation worlds (§K.7).
- The type sequence is fixed by the evaluation seed and interleaved in the world order (§I.6).
- **Default** (owner decision 3): N = 60, giving 75 evaluation worlds: 15 null, 48 in-family and 12 out-of-family. That is 16% of evaluation worlds out-of-family.

### C.8 Hidden from every arm and from S-SCR and S-AGT

`[DECISION]`
- world type, J, mechanism types, parameters, driver identities, trap identities, proxy and phantom identities;
- the forward law, the vault, the replication draw and the oracle draws;
- the annex;
- all seeds;
- this document's §C, beyond what Appendix C allows.

### C.9 Sealed out-of-family annex 𝒢₂ᴬ

`[DECISION]`, with its content sealed. `[OPEN: owner decision 7]`
- **Content.** S-GEN writes the annex before the development ceremony, or the owner or an out-of-family author does (owner decision 10). It specifies:
  - at least two mechanism forms outside §C.5;
  - at least one change to the noise, publication or revision law;
  - for each mechanism form, a strength prior calibrated as in §C.5;
  - for each mechanism form, a designated DSL approximation whose oracle coverage reaches ½·θ_solo at the prior's median.
- **Commitment.** Its SHA-256 is committed in F_H(2-dev) (§O.2), and it is shown to the owner before commitment.
- **Secrecy.** It is not shown to S-SCR, S-AGT or any researcher arm. It is revealed at campaign close.
- **Calibration.** Before C2-eval, a sealed ORC-A arm (which submits the designated approximations) and A1 run on out-of-family development worlds from stream `dev-oof`. Only pass or fail is released (§P.2).
- **Coverage.** Out-of-family mechanisms need not be exactly expressible in the DSL; coverage by approximation is scored by §J.3.
- **Purpose and limit.**
  - The annex limits gaming by any party who knows §C, including a model whose training data might contain this document (§N).
  - It covers 20% of non-null worlds, which is 16% of evaluation worlds (12 of 75), and it covers mechanism search only.
  - Trap avoidance and null-world false-discovery control are computed on the public §C constructions, and are protected only as far as the annex covers them.
- **Design extension, for the re-draft after Experiment 2-T0** (draft text only):
  - 𝒢₂ᴬ also defines at least one sealed trap archetype and a sealed null-world variant under its changed law;
  - a pre-registered share of null worlds is drawn from 𝒢₂ᴬ;
  - F1, F2 and the null-world FWER are reported separately by family.

### C.10 Baseline B* (owned by the referee)

`[DECISION]`
- **Features** at origin t, all point-in-time:
  - first-release y at days t … t − 6 (7 lags);
  - 6 day-of-week dummies;
  - annual Fourier terms sin and cos of 2πk·doy/365.25, for k = 1, 2;
  - D1 and D2 at their latest available day and the 7 days before it (8 lags each);
  - a missingness indicator for each of these.
- **Learner:** the κ₂ ridge learner (§C.11).
- **Scope of B*.** B* contains every disclosed driver and the outcome's own dynamics. Novelty is measured against B* (§J.6).
- Submissions cannot change B*. Every claim's comparator must be B* (§F).

### C.11 Campaign configuration κ₂

`[DECISION]`, except where marked `[OPEN]`.

| Item | κ₂ |
|---|---|
| Horizon | 1 day (target y_{t+1} at origin t) |
| Loss | Squared error on the first-published target |
| Learner | `[OPEN: owner decision 5]` Ridge regression on features standardised in-window. Intercept unpenalised. λ is frozen from the tuning worlds: grid {0.1, 0.3, 1, 3, 10}, chosen by the mean blocked-CV loss of B*. Deterministic Cholesky solver, pinned at code freeze |
| Training | One fit at the discovery freeze, on days 365–1,459. Each training row's features are built as of its own origin, and its label's known_at must be ≤ the freeze |
| Imputation | Median of the training window (1A §C.8); missingness indicator added |
| Feature construction | Every feature is rebuilt from the as-of snapshot at its own origin (1A §C.8 semantics) |
| Confirmation | §G.2 |
| Replication | §G.4 |
| Oracle | §J.1 |

**No Experiment 1A certification transfers to κ₂** (§Q, CX-03). `[DECISION]`

### C.12 Generator self-checks and harness errors

**Self-checks** run on every world. `[DECISION]`
- 36 series, with IDs unique within the world and across worlds (outside parent–sibling pairs), and padded file sizes identical across worlds;
- every x_i's stationary variance, computed analytically from its drawn parameters, is 1 within 10⁻⁹;
- joint calibration converged: every |θ̂_calib,j − target_j| ≤ 0.002 on the `calib` draws (§C.5). An independent-draw re-estimate is a campaign-level diagnostic, reported but not a per-world error;
- every trap satisfies its single-series truth condition (§C.6): oracle θ + 3·s_o < δ_min on the `calib` draws, for the encodings in S-GEN's trap table, after at most 5 redraws;
- every series' assigned revision probability equals its §C.0 value (0.5 for mechanism and phantom drivers, proxies and nulls; 0.4 for traps other than TRAP-REV; 1 for TRAP-REV), so that the marginal P(revised | role class) is 0.5 for every class except the fixed exceptions (Y, D1, D2 and binary series);
- the truth store's manifest hash is ledgered before any arm starts the world (§O.3).

A trap truth-condition failure caused by factor sharing indicates a generator bug, except for TRAP-RED, whose D1 component carries D1's factor loading by design; a TRAP-RED failure is handled by the §C.6 redraw rule.

**Harness error (definition)** `[DECISION]`:
- **Harness error.** A TH fault that reproduces from the recorded inputs and does not depend on researcher outputs. This includes a failed self-check or conformance assertion. It also includes a verified provider-infrastructure failure: an HTTP 5xx, a rate limit or a network failure at the relay, shown in the relay log, that persists after 3 pre-registered retries from the recorded state.
- **Not a harness error: model-behaviour failures.** Refusals; malformed or oversized tool calls or outputs; context overflow; timeouts caused by the model's own actions; exceptions triggered by researcher outputs. These are SUT events, scored like exhaustion (TRK = 0, R = 0; for A0, the world is dropped from A0's AUC and reported, §I.2), counted in S4 and reported per arm.
- **Pairing.** A world with a harness error in any of A1–A5 is excluded for every one of those arms; a harness error in A0 removes that world from A0's AUC only. Frozen code decides this before any truth is released, so the analysis stays paired.
- **Threshold.** If harness errors exceed 2% of world-runs, pooled or for any single arm among A1–A5, the outcome is VOID-BENCHMARK (§L), under the preservation rule of §L. A0 harness errors are reported and count toward the pooled rate only.

---

## D. Point-in-time data catalogue and access

### D.1 Catalogue

Per world:
- 36 series with the metadata of §C.3;
- the row files for days 0–1,459, with only vintages whose known_at ≤ the freeze;
- a manifest with SHA-256 hashes.

`[DECISION]`

### D.2 known_at registry

B-REG derives known_at from each row's publish_time (§C.3). It is the only place known_at is determined. `[DECISION]`

### D.3 Interfaces

`[DECISION]`

| Call | Available to | Returns |
|---|---|---|
| `catalogue()` | All arms | Metadata (§C.3) |
| `asof(series, origin, vintage ∈ {asof, first})` | A1, A2, A4, A5 | Values admissible at that origin, under 1A §C.8 semantics (no carry-forward) |
| `raw(series)` | A3 only `[OPEN: owner decision 8]` | The row file itself, with every vintage and its derived known_at, for vintages with known_at ≤ freeze |
| `discover(expression, scope, subsample?)` | A1, A2, A4, A5 | Discovery skill θ̂_disc from 5-fold blocked CV on days 365–1,459 (blocks of 219 days); its Newey–West (lag 7) t-statistic; the scope's day coverage; a NEAR_DUPLICATE flag. Stamped `EXPLORATORY`. Metered as one unit of Q (reported) |
| `submit(batch)` | A1, A2, A4, A5 | A fixed-length receipt (§G.2) |
| `assert(batch)` | A3 | A fixed-length receipt. The batch is final |
| `memory_read()` | A5 | The memory snapshot (§I.4) |

**Every arm sees the same information content: the discovery segment as of the freeze.** A3 sees it as raw vintage-tagged files, the others through the as-of path. The sandbox evaluator library B-EVAL gives A1, A2, A4 and A5 the `discover()` computation locally, metered by CPU. `[DECISION]`

---

## E. Hypothesis DSL

### E.1 Grammar

`[DECISION]`

```
expr  := atom | unop(expr) | mul(expr, expr) | sub(expr, expr) | gate(expr, pred)
atom  := S(series_id, vintage)                     # vintage ∈ {asof, first}
unop  := lag[k]       k ∈ {1..14}                  # extra lag beyond availability
       | diff[k]      k ∈ {1, 7}
       | ma[w]        w ∈ {3, 7, 28}               # trailing mean
       | zs[w]        w ∈ {28, 91}                 # trailing z-score
       | rank[w]      w ∈ {28, 91}                 # trailing rank in [0, 1]
       | hinge[q]     q ∈ {0.25, 0.5, 0.75}        # max(0, e − c_q), c_q fitted on the training window
       | sign | abs
       | clip[q]      q ∈ {0.01, 0.05}             # winsorise at training-window quantiles q and 1 − q
pred  := B(series_id, vintage)                     # binary series only (§E.2); true iff the admissible value equals 1; false if the row is missing
       | gt(expr, q)  q ∈ {0.25, 0.5, 0.75}        # e > training-window quantile
       | not(pred) | and(pred, pred)
```

### E.2 Limits

`[DECISION]`
- depth ≤ 3 nested operators. Predicate operators (`gt`, `not`, `and`) count toward depth and node count; a bare predicate atom `B(·)` adds one node and no depth;
- ≤ 8 nodes per expression;
- `B(·)` admits only binary series: every discovery-segment value of the series is in {0, 1}, type-checked by B-CLM and B-EVAL. A2's grid for `B(·)` follows this type;
- ≤ 2 distinct series in an expression, and ≤ 1 further series in the scope predicate;
- parameters only from the grids above, so no continuous parameter can be tuned;
- any series used must exist in the world's catalogue. Y may appear only through `lag[k]` with k ≥ 7, because short lags of Y are already in B*.

### E.3 Semantics and causality

`[DECISION]`
- Every value used at origin t is admissible at t (§0.6).
- Rolling operators use only the trailing window of values available at t.
- Quantile parameters (hinge, gt, clip) are fitted on the training window only, and then frozen.
- The evaluator is the only path from the DSL to features (B-DSL through B-ASOF). The same code serves the vault, the replication, the oracle and B-EVAL (§B.1).
- The inline control DC and the mutants LKD1–LKD8 test causality for every operator (§B.3).

### E.4 Canonical form and deduplication

`[DECISION]`
- **Canonical form.** An AST in RFC 8785 (JCS) JSON.
  - Arguments of `mul` and `and` are sorted by their canonical hash.
  - `not(not p)` becomes p; `abs(abs e)` becomes `abs e`; `sign(sign e)` becomes `sign e`.
  - `lag[k](lag[m] e)` becomes `lag[k+m]` if k + m ≤ 14, and is otherwise invalid.
- **Expression hash:** SHA-256 of the canonical JSON.
- **DUPLICATE:** two claims in one batch with the same claim hash. The second is rejected and still counts toward the cap.
- **NEAR_DUPLICATE:** a claim whose discovery-CV **incremental** forecasts (M_c − B*, with the transformation ungated) correlate ≥ 0.95 with those of another claim in the same batch. It is flagged and charged in full (as 1A D39). It stays in the batch, and the mechanism-attributed clusters of §J.4 stop it from lowering the false-discovery proportion.

---

## F. Claim schema

`[DECISION]`
- Every field is mandatory.
- The claim hash is SHA-256 of JCS over every field except `rationale` and `identity`.

| Field | Content | Constraint |
|---|---|---|
| `spec_version` | `"2-1"` | Fixed |
| `direction` | `positive` or `negative` | — |
| `outcome` | The world's outcome ID | Must equal Y's ID (κ₂ has one outcome per world) |
| `horizon` | Days ahead | Fixed-value field: must equal 1 under κ₂ |
| `information_set` | B* plus the list of (series ID, vintage selector) used by `transformation` and `scope` | Must match the series in the expression and predicate exactly. **Canonical form:** entries sorted by (series ID, vintage selector) in byte order, without duplicates. B-CLM derives the list from the canonical ASTs before hashing, so a different order cannot change the claim hash |
| `transformation` | A canonical DSL expression (§E) | §E.2 limits |
| `comparator` | `"B*"` | Fixed-value field: must equal B* (no baseline shopping) |
| `min_effect` δ | Relative MSE reduction | δ ∈ {0.01, 0.015, …, 0.20}; δ ≥ δ_min = 0.01 |
| `scope` | `all`, or a DSL predicate | Must cover ≥ 20% of discovery days. May use only catalogue series under §E.3 semantics, never the outcome at or after the target day |
| `falsification_condition` | A template that B-CLM generates from δ and scope (below) | Not free text |
| `rationale` | Free text, at most 1,000 characters | Recorded; not hashed or scored |
| `identity` | The arm | Recorded; not hashed |

**Falsification template** (generated):
- **Positive claim:** "Falsified if, on data not used to select or fit it, the relative MSE reduction of B* + transformation over B* on in-scope days is below δ. Operationally: NOT-PASS at sealed confirmation (Holm, α = 0.05) or at harness replication (α = 0.05). For benchmark scoring only: oracle grade FALSE."
- **Negative claim:** the same, with "at least δ" and the reversed tests.

**Referee-owned settings.**
- The fixed-value fields `horizon` and `comparator` are validated to equal κ₂'s values (1 and B*).
- Apart from those two, referee-owned settings can never appear in a claim: learner, λ, training window, loss, baseline definition, test, α, block length, seeds and tolerances.
- A claim carrying any unknown field is invalid, rejected with a fixed-length receipt, and counted against the cap.

`[DECISION]`

---

## G. Stages, validated knowledge and anti-gaming controls

### G.1 Discovery

- Each arm works on the discovery segment (§D.3) within its budget (§H).
- Everything computed here is `EXPLORATORY` and can never be credited by itself.

`[DECISION]`

### G.2 Sealed single-use confirmation (referee arms A1, A2, A4, A5)

`[DECISION]`

| Item | Specification |
|---|---|
| Input | One batch per world-run: ≤ 4 positive claims (m_pos) and ≤ 2 negative claims (m_neg). A second batch is refused with a fixed-length receipt |
| Model | For each claim c, M_c = B* + c's features (gated by its scope), fitted once on the training window (§C.11). B* is fitted once on the same window |
| Days | Vault days 1,490–2,584 that are in scope, in order; consecutive blocks of 14 in-scope days; the incomplete last block is dropped. n_b is the number of blocks |
| Positive statistic | d_t = (1 − δ_c)·ℓ_{B*,t} − ℓ_{M_c,t}; b_j = the mean of d over block j; T = √n_b·mean(b)/sd(b); p = 1 − F_{t, n_b−1}(T). H0: θ(c) ≤ δ_c |
| Negative statistic | d⁻_t = ℓ_{M_c,t} − (1 − δ_c)·ℓ_{B*,t}, in the same form. H0: θ(c) ≥ δ_c |
| Degenerate cases | p := 1 if n_b < 6, or if sd(b) ≤ 10⁻¹²·(1 + \|mean(b)\|) (1A §D.1) |
| Multiplicity | Holm at α = 0.05 within the positive family, and separately within the negative family. Ties are broken by claim hash (1A §D.1). The per-vault family-wise error across both families is ≤ 0.10 `[INFERENCE]` |
| Before closure | A fixed-length receipt: world-run ID, claim hashes, tick index |
| At closure | The graded evidence package (per claim: θ̂ on vault days, T, p, adjusted p, decision). The vault is consumed |
| Errors | Any TCB exception maps to p := 1 for that claim and is logged in B-AUDIT (1A §D.1) |

**A3 has no vault.** Its batch, with the same caps and schema, is final at `assert()`. The harness also runs A3's batch through this §G.2 test, with Holm within A3's batch ("as-if confirmation"). The result is never shown to A3 or stored in memory, and it decides A3's primary TRK credit (§G.5). `[DECISION]`

### G.3 Closure

After the receipt, the world-run accepts no new claim or modification. Any later analysis of that world is `EXPLORATORY` and never credited. **Reformulation after the holdout is impossible by construction:** replication and truth scoring evaluate the claim hash recorded at submission. `[DECISION]`

### G.4 Fresh harness replication

`[DECISION]`
- **Who.** The harness (TH), using the referee's own evaluator and learner (§B.1). The replication data are never visible to any arm before the claim is frozen.
- **What.** Every confirmed claim (referee arms) and every asserted claim (A3).
- **Data.** A fresh, independent draw from the forward law P, with seed purpose `replicate`. Its seeds are fixed by the evaluation ceremony before the campaign, and it shares no innovation with the discovery, vault or oracle data.
- **Procedure.** Refit M_c and B* on the 1,095 fresh training days, then apply the §G.2 statistic for the claim's direction on the 1,095 fresh test days, at α_rep = 0.05 one-sided per claim. There is no multiplicity adjustment; this is a second, independent filter.
- **UNTESTABLE.** Fewer than 6 blocks of in-scope test days. An UNTESTABLE claim is not replicated.
- **Release.** The replication verdict and its statistic are released to the arm after closure, through the release endpoint. A5 may store them in memory.

**Scope of the word "replication":** this is a same-law harness replication, not an independent laboratory, team or dataset (§N).

### G.5 When a result becomes a unit of validated knowledge

`[DECISION]`

A **validated positive unit** is a positive claim c from a world-run such that all of the following hold:
1. c passed structural validation and is not a DUPLICATE;
2. c PASSed sealed confirmation under Holm in the positive family. For A3, this is the harness's as-if confirmation (§G.2);
3. c PASSed harness replication;
4. the world-run has no INVALID flag (MRS-2 inline controls) and no critical-leak event (§K.5);
5. the world-run is not in the failed-reproduction set, meaning world-runs in the replay subset with a verdict-level mismatch (§K.5).

A **validated negative unit** is a negative claim that meets the same five conditions with the negative family and the reversed tests.

**Labels.** Memory labels apply conditions 1–4 at world-run close (§I.4). Condition 5 is applied retroactively for scoring and for the knowledge ledger, and is never fed back into memory. A3's replication-only units (conditions 1 and 3–5, without the as-if confirmation) are reported as a pre-specified sensitivity analysis (S11).

**The knowledge ledger.** A validated unit is recorded in the institutional knowledge ledger, which stays sealed until campaign close (§K.8), with:
- the claim hash and fields;
- confirmation and replication evidence;
- ledger IDs;
- the scope string;
- the §A.5 caveat.

**"Validated" does not mean "true".** Truth is known only to the harness, and is sealed until campaign close. The benchmark measures how often validated units are true.

**Attractive expression.** An expression or claim is attractive if its referee-computed discovery skill θ̂_disc ≥ δ_min and its discovery t ≥ 2.5. This label is used by MRS-10 and by A1 step (iv).

**A useful negative finding** is a validated negative unit that meets all of the following:
- its grade is TRUE-NEG (§J.5);
- it has δ_c = δ_min;
- it is attractive, and its discovery t is also ≥ 4.05. The 4.05 is a **fixed convention**, Φ⁻¹(0.95^{1/2000}) (the 95th percentile of the maximum of 2,000 independent null t-statistics), applied identically to every arm and not tied to any arm's search count. Under C₀ an arm can screen far more expressions (Appendix A.4), so EK-B1 reports how many null expressions per world exceed it. For A3, the harness computes the same discovery statistics after closure;
- its ungated transformation does not equal, and its §J.4 cluster does not match, any positive claim in the same batch.

Validated TRUE-NEG negatives with δ_c > δ_min are reported separately as "effect-bounded". `[DECISION]`

### G.6 Controls on splitting, duplication and reformulation

`[DECISION]`

| Threat | Control |
|---|---|
| Claim splitting (one mechanism as several claims) | TRK counts **mechanisms covered**, not claims (§J.3), and S1 precision is at mechanism level. Splitting cannot raise either. The claim cap is m_pos ≤ 4 |
| Padding the FDP with near-copies or pieces of a true claim | Clusters are mechanism-attributed (§J.4), so every piece of one mechanism is one cluster, and a cluster is false if any member is false |
| Exact duplicates | Rejected (§E.4); still charged against the cap |
| Near-duplicates | Flagged and charged in full (§E.4) |
| Post-holdout reformulation | One batch; the vault is consumed; the scored object is the hash recorded at submission (§G.3) |
| Scope shopping | Scope is part of the hash. It must cover ≥ 20% of discovery days. Its forking paths are paid for in discovery, and confirmation is sealed |
| Baseline shopping | The comparator is fixed to B* |
| Trivial δ | δ ≥ δ_min; a larger δ earns nothing extra |
| Harvesting cheap negatives | Negative credit requires the §G.5 conditions (δ_min, a discovery t of at least 4.05, no positive twin). At most 2 negatives per world. S6 reports how often each arm saturates the cap |
| Rerunning a world | Each world-run happens once. The model rerun (§K.6) is a separate, pre-registered variance study, never used in the primary analysis. Exceptions: the §I.4 memory-quarantine reruns of A5 and the §B.3 MRS-reopen reruns, which replace the affected world-runs |

---

## H. Budgets

Budgets are identical across arms, except where a resource does not exist for an arm. Every resource is metered by the TH and ledgered. `[DECISION]`, with values `[OPEN]` under owner decision 6.

| Resource | Per world-run | Applies to |
|---|---|---|
| Data | The discovery segment, as of the freeze (§D.3) | All |
| **CPU C₀ (binding search budget)** | 2 CPU-hours: sandbox code (including B-EVAL evaluations), `discover()` and scripted-arm compute, all metered to the arm. **The referee's inline controls are metered to the TH, not to the arm** | All |
| Wall-clock W₀ | 4 hours | All |
| Model tokens T₀ | 4 × 10⁶ input tokens (including cached) and 4 × 10⁵ output tokens | A3, A4, A5. A0: 5 × 10⁴ in total. For A5, a post-closure memory-writing allowance of 5 × 10⁴ tokens is reserved inside T₀, so A5's in-run cap is T₀ minus the allowance, and its total never exceeds A4's |
| Discovery evaluations Q | **Reported meter only, not a cap.** Q counts `discover()` calls and B-EVAL evaluations | A1, A2, A4, A5 |
| Claim cap | m_pos ≤ 4, m_neg ≤ 2, one batch | All |
| Vault uses | 1 | A1, A2, A4, A5 |
| Memory | Read at world start; written after closure. At most 200 items and 2 × 10⁵ tokens; overflow rule in §I.4 | A5 |

- **Exhaustion.** When any cap is reached, the arm must submit (or assert) within 10 minutes of wall-clock time. Otherwise it submits nothing, and the world-run scores TRK = 0 with R = 0.
- **Self-written evaluation.** Evaluation code that the AI arms write themselves is metered by CPU only (§N).
- **Budget sweep** (secondary, S10): A1 and A2 are also run at C ∈ {0.25, 4} × C₀ on the first 20 non-null evaluation worlds in the §I.6 order. This shows how much scripted search budget is needed to match the AI arms.
- **Cost.** Token cost is reported per world-run (tokens × the pinned snapshot's price on the run date), including the memory-writing call. It is never used in the primary analysis.

---

## I. Arms

### I.1 Common rules

`[DECISION]`
- Every arm runs every evaluation world once (except the §I.4 quarantine reruns of A5 and the §B.3 MRS-reopen reruns), in the same fixed world order (§I.6), with a fresh organisation per world-run (1A §B.1a).
- Every arm submits claims in the §F schema, and every claim goes through the same harness replication and truth scoring.
- Arms A3–A5 use the **same pinned model snapshot**, sampling settings and agent runner. They differ only in the tools and memory listed below. The brief follows Appendix C.

### I.2 Arm definitions

| Arm | Definition | Referee | Memory |
|---|---|---|---|
| **A1: scripted plan** `[OPEN: owner decision 9]` | Written by S-SCR without §C knowledge (§B.4), frozen before evaluation. Within C₀, using B-EVAL and `discover()`, it: (i) screens the DSL in a fixed priority order based on generic grammar properties (node count, then a stated operator order: atoms × vintage selectors, then unary operators, then gates by each binary series, then products among the top 50 atoms); (ii) applies stability selection, 20 half-sample refits of the top 50; (iii) submits up to 4 positive claims with distinct drivers, ranked by selection frequency and then discovery t, with δ = δ_min and scope `all` unless the top expression is gated; (iv) submits up to 2 negative claims on the attractive expressions (§G.5) with the highest discovery t that fail stability selection. The canonical candidate count for each priority level, and the level at which C₀ truncates the screen, are measured at EK-B1 and reported. Hyperparameters are tuned on the tuning worlds | Yes | No |
| **A2: grammar random search** | A frozen sampler, specified here, not by S-SCR. Draw a depth d uniformly from {0, 1, 2, 3}. Then draw a production uniformly at each node, and operator parameters and series IDs uniformly from their grids. Within each depth, sampling is without replacement over canonical hashes. If a depth's canonical space is exhausted, its remaining draws are reassigned uniformly to the deeper levels. Seed purpose `a2_search`. A2 samples until C₀ is exhausted, ranks by discovery t, and submits the top 4 with distinct drivers (δ = δ_min, scope `all`). No negative claims. The depth d is the exact depth under §E.2. **A2 is an enumerator with naive selection** (§I.3) | Yes | No |
| **A3: AI without referee** `[OPEN: owner decision 8]` | The pinned model with raw vintage-tagged files, the sandbox (no B-EVAL) and the brief. No `discover()`, as-of API or vault. Its asserted batch is final | No | No |
| **A4: AI + referee, no memory** | The pinned model with the as-of API, `discover()`, B-EVAL, the sandbox and a G1 vault. A fresh context in every world | Yes | No |
| **A5: full system** | A4 plus structured validated memory (§I.4) | Yes | Yes |

**Validity arms** (not comparators):
- **ORC (truth-submitting arm).** For in-family worlds, the harness submits the DSL encodings of the true mechanisms (at most 4) through the §G.2 vault and §G.4 replication:
  - exact driver, operator and threshold;
  - vintage `asof`;
  - δ = δ_min;
  - scope `all`, or the regime gate for REG.

  ORC measures the pipeline's ceiling: how many planted mechanisms the confirmation and replication budget can certify at all.
- **ORC-A.** The same for out-of-family worlds, using the annex's designated approximations (§C.9).
- **A0 (metadata probe).** The pinned model sees only the catalogue metadata (§C.3), through the fixed A0 prompt template (Appendix C). It ranks every non-disclosed series by the likelihood that it predicts Y given B*.
  - It is scored by AUC against the mechanism-component and trap roles.
  - **A0 detects implementation metadata leaks only.** Roles are drawn independently of the metadata, so it cannot detect prior knowledge of the family (§N, item 12).
  - Malformed or incomplete A0 output is retried once, under a pre-registered rule; otherwise it is a model-behaviour failure (§C.12), not a harness error: that world is dropped from A0's AUC and reported, and no other arm's world-run is affected. It is never scored as tied ranks.

`[DECISION]`

### I.3 Why these arms are fair

`[DECISION]`
- **Same data.** Every arm gets the same discovery information. No arm gets confirmation data. Every arm's claims face the same replication and oracle, and **every arm's primary TRK passes the same two filters**: confirmation (as-if for A3) and replication.
- **Same budget.**
  - CPU (C₀), wall-clock (W₀) and, for model arms, tokens (T₀) are the binding search budgets for every arm.
  - The referee's inline controls are metered to the TH, not to any arm.
  - A5's memory writing is inside T₀.
- **Strong scripted control.** A1 is the strongest non-AI plan S-SCR can build without §C and with equal tuning effort. It is not a straw man, and it is not tuned to the hidden family.
- **A2 is an enumerator with naive selection, not a weak floor** `[INFERENCE]`.
  - Depth 0 holds 70 legal atoms (35 non-Y series × 2 vintages). Depth 1 holds about 9,900 canonical expressions: 2,116 unary, 2,485 `mul`, 4,830 `sub` and 420 gates on binary predicates.
  - **Every in-family exact encoding lies at depth ≤ 1:** LIN = S(driver, asof); HNG = hinge[q](S(driver, asof)); REG = gate(S(driver, asof), B(S, asof)).
  - Depth 1 receives a quarter of A2's draws (a third once depth 0 is exhausted), so A2 exhausts it within about 3 × 10⁴ draws. That fits in C₀ (7,200 CPU-s) if one evaluation costs ≲ 0.2 CPU-s; the EK-B1 Q meter settles this.
  - A1's priority order (70 atoms, then 2,116 unary expressions, then 420 binary gates) reaches every exact encoding within about 2.6 × 10³ evaluations, which fits in C₀ up to about 2.7 CPU-s per evaluation.
  - A2's weakness is therefore selection (the top discovery t among many candidates, with no stability selection and no trap awareness), not coverage.
- **What the in-family comparison measures.** In-family, CONTINUE measures selection and validation under a fixed budget, not hypothesis generation. Generation is only probed by the 12 out-of-family worlds (S9, exploratory, not gated). Enlarging the in-family family beyond enumeration is an alternative under owner decision 9.
- **Referee ablation.** A3 differs from A4 by exactly the referee: the point-in-time path, `discover()`, B-EVAL, the sealed vault and the charging rules.
- **Memory ablation.** A5 differs from A4 by exactly the memory, including the reflection call that writes it, at equal total model budget.
- **Blind search.** Series are obfuscated, so no arm can use domain semantics. Experiment 2 tests **blind** search (§N).

### I.4 Memory (A5)

`[DECISION]`

**Contents.** Items are written only after a world-run closes. They derive only from what the institution legitimately observes: its own claims, discovery statistics, confirmation evidence packages and replication verdicts. Item kinds:
- `VALIDATED_POSITIVE`;
- `VALIDATED_NEGATIVE`, for validated negatives with δ_c = δ_min only;
- `VALIDATED_UPPER_BOUND`, for validated negatives with δ_c > δ_min, carrying δ_c. This rule uses claim fields only;
- `CONFIRMATION_FAILED`;
- `REPLICATION_FAILED`;
- `PROCEDURAL_NOTE`: at most 500 characters, written by the model in the post-closure call.

The "validated" labels apply §G.5 conditions 1–4 (§G.5).

**Item schema:** item ID, source world-run index, kind, canonical claim (if any), statistics, ledger IDs, note.

**Never in memory:**
- oracle grades, coverage or mechanism attribution;
- world type, generator parameters, the annex or seeds;
- anything from the truth store;
- anything from another arm.

**Enforcement.**
- B-MEM validates every write against the schema.
- The canary scanner checks every item.
- A violation is a critical-leak event (§K.5).

**Validity of writes.**
- B-MEM writes nothing from a world-run that is flagged INVALID (MRS-2), that has a harness error, or that has a critical-leak event.
- If such a flag, or an MRS reopen, arrives after the write, the items are quarantined, and every later A5 world-run whose snapshot contained them is marked affected.
- **Remedy (pre-registered):** the affected A5 world-runs are rerun on the same worlds, in the original order, from the last clean snapshot. That keeps the pairing with the controls. It is a registered exception to §G.6 and is carried out before campaign close; campaign close (§K.8) waits for it. A flag that arrives after campaign close triggers no rerun and is handled by the §B.3 post-close rule. A quarantine rerun never recomputes a released EK-B2 decision.
- Truncating A5's primary analysis at the first affected index is only a reported sensitivity analysis.

**Order and state.**
- **Strictly sequential.** A5 runs in the §I.6 order. World i starts only after world i − 1 has closed, its replication verdict has been released and its memory has been written.
- **Snapshots.** The snapshot for world i contains only items from worlds < i that have not been evicted (overflow rule) or quarantined. Its SHA-256 is ledgered at world i's start.
- **Start state.** Memory is empty at evaluation world 1. Nothing from development or tuning worlds is kept.
- **Overflow.** First-in-first-out eviction by source world index, ties within a world broken by item ID, validated and ledgered by B-MEM. Per world index, the item count, token count and number of evictions are reported. At the start of the S7 probe, the memory contents and the share of the probe's source-world items still held are reported.
- **Reruns.** The §K.6 rerun of world i reads exactly the ledgered snapshot of world i, verified by hash. Rerun writes go to an isolated per-rerun store that no other world-run reads, and that store is discarded after S5 is computed. A rerun write reaching the primary store is a §K.5 critical-leak event.
- **Probe.** The S7 probe runs after the full primary chain.

**Transfer content.** Series IDs are unique across unrelated worlds (§C.2), so memory can transfer only procedural regularities of the family. Examples: how revised series behave; which trap archetypes recur; which discovery-statistic ranges tend to replicate.

### I.5 Negative and positive claims across arms

A1, A3, A4 and A5 may submit negative claims; A2 does not. The negative endpoint (S6) compares arms that may submit negatives. `[DECISION]`

### I.6 World order

`[DECISION]`
- **One order for all arms,** drawn with seed purpose `order` at the evaluation ceremony, with world types interleaved.
- **The first 20 worlds form the interim block** (§K.7). The order is stratified so that this block contains 4 null, 13 in-family and 3 out-of-family worlds.
- **The transfer probe** (§K.2, S7) runs after the primary block.
- **The A5 chain** is started first, and the other arms run in the remaining parallel slots (§P.3).

---

## J. Ground truth and scoring

### J.1 Oracle: predictive truth of the whole claim pipeline

`[DECISION]`
- **Estimand (forward-law-trained skill).** θ_o(c) = 1 − E[ℓ(M_c)] / E[ℓ(B*)] on in-scope days under P.
  - M_c and B* are fitted by the κ₂ learner on a fresh training draw from P of the same length as the discovery segment (365 warm-up + 1,095 training days), and scored under P.
  - The expectation is over training draws and test days.
  - The oracle calls the referee's B-DSL, B-ASOF and B-LRN (§B.1).
- **Computation.**
  - K = 20 independent training draws, each scored on 5,000 fresh test days: 10⁵ test days in total.
  - Common random numbers for M_c and B*.
  - θ_k is the per-draw estimate; θ̂_o = mean(θ_k); s_o = sd(θ_k)/√K.
  - **Escalation (one rule for §J.1–§J.5).** K doubles while s_o > δ_c/6 or the grade is INDETERMINATE (for coverage: while s_D > τ_j/6 or the classification is COVERAGE-INDETERMINATE), up to K = 160. Draws 21–160 use pre-registered common seeds (purpose `oracle`), shared by every arm and by P and P^−j. Frozen code applies the rule identically at EK-B1 and at scoring. Per-arm escalation counts, and the INDETERMINATE shares left at K = 160, are reported.
- **What truth means.** Truth is graded by what the referee learner can exploit under P.
- **Where delivered skill can differ** `[ASSUMPTION]`. In TRAP-BRK worlds and on TRAP-SEL's selected path, the discovery-period training data differ from P, so delivered skill can differ from θ_o. Trap claims are FALSE under either estimand. Any difference for other claims is not graded.
- **Difference from 1A's estimand** (§Q.1, CX-12). 1A's ground truth is the conditional skill of the fitted forecasts on the vault days actually used. Here truth is the expected pipeline skill. For every confirmed claim a secondary, 1A-style **conditional grade** is also reported: the exact conditional skill of the M_c fitted on discovery data, on the vault days used, computed from the generator's conditional mean and variance under squared error. The analogous grade is reported for the replication fit, and FDP is split into referee test error and estimand gap.
- **Closed-form validation** (MRS-11). On linear-Gaussian validation worlds, with a correctly specified linear M_c and a large training draw (10⁵ days), a true-mechanism atom's θ_o is compared with 1 − (σ² + v_rest)/(σ² + v_rest + v_c).
  - v_c is the explained variance of the claim's feature given B*.
  - v_rest is the residual variance of the other mechanisms given B* and the claim.
  - The other MRS-11 claim classes use the closed forms listed in §B.3.

### J.2 Grades (positive claims)

`[DECISION]`

| Grade | Rule |
|---|---|
| TRUE | θ̂_o − 3·s_o ≥ δ_c |
| FALSE | θ̂_o + 3·s_o < δ_c. Sub-labels: **NULL** (θ̂_o + 3·s_o ≤ 0) and **OVERSTATED** (otherwise) |
| INDETERMINATE | Neither. **Primary analysis:** counted as false in FDP, and not credited in TRK. **Sensitivity analysis:** excluded from both |

### J.3 Mechanism coverage and TRK (primary endpoint)

`[DECISION]`
- **Credited set.** For arm a in world w, C_{a,w} is the set of the arm's validated positive units (§G.5) that are graded TRUE.
- **Set model.** M(C) = B* + every feature of C (each gated by its own scope), fitted as in §J.1 and evaluated on all days.
- **Mechanism ablation.** For each planted mechanism j, P^{−j} is P with g_j set to 0 and everything else identical, under common random numbers.
- **Coverage statistic (common denominator):**

  cov_j(C) = {[E_P ℓ(B*) − E_P ℓ(M(C))] − [E_{P^−j} ℓ(B*) − E_{P^−j} ℓ(M(C))]} / E_P ℓ(B*)

  - It is computed from the K paired draws, with Monte Carlo SE s_D = sd(cov_{j,k})/√K.
  - cov_j = a_j·θ_j exactly only in the orthogonal linear-Gaussian case, where a_j is the captured fraction. MRS-11 checks this.
- **Threshold τ_j.**
  - For LIN mechanisms, and for proxies of LIN drivers: τ_j = max(½·θ_j^solo, δ_min).
  - For HNG and REG mechanisms, the harness computes, under common random numbers:
    - θ_j^ref, the coverage difference of the exact DSL encoding on the admissible vintage;
    - L_j, the coverage difference of the best ungated linear-in-driver encoding (same driver, same lag, vintage `asof`).

    Then τ_j = max(½·θ_j^solo, δ_min, L_j + ½·(θ_j^ref − L_j)). At unit variance and with no revision, this is about 0.75·θ for REG and HNG-0.75, and about 0.87·θ for HNG-0.5.
  - If θ_j^ref − L_j < 0.1·θ_j^ref, the form cannot be told apart on the admissible vintage. The mechanism is then scored under the LIN rule and flagged. This is not a harness error.
  - For out-of-family (annex) mechanisms: τ_j = max(½·θ_j^solo, δ_min), matching the designated-approximation rule of §C.9.
- **Escalation.** As in §J.1: K doubles while s_D > τ_j/6 or the classification is COVERAGE-INDETERMINATE, up to 160.
- **Classification of mechanism j:**
  - **covered** iff cov_j − 3·s_D ≥ τ_j;
  - **not covered** iff cov_j + 3·s_D < τ_j;
  - **COVERAGE-INDETERMINATE** otherwise.

  COVERAGE-INDETERMINATE is not credited in the primary TRK or in the ORC and A1 calibration checks. It is credited in a pre-registered sensitivity analysis, and the share is reported per arm.
- **TRK_{a,w}** = the number of covered mechanisms.
  - It is non-duplicative by construction: splitting, proxies and duplicates cannot raise it.
  - Proxy-based coverage counts, and is reported separately as "proxy-true".
  - "Form-correct" and "linear-proxy" coverage are reported separately (S1).
- **Null worlds** have TRK = 0 for every arm. They enter only the false-discovery endpoints.

### J.4 False discoveries

`[DECISION]` These are computed by frozen code from the sealed truth store, and released at campaign close (§K.8).

- **Clusters, computed separately on each level's claim set** (asserted positive claims, and validated positive units):
  1. For every claim, whatever its grade, compute the single-claim coverage cov_j({c}) (§J.3 form) for each planted mechanism j.
  2. Attribute the claim to the j with the largest value, if that value is ≥ δ_min. Break ties by claim hash.
  3. All claims attributed to the same mechanism form one cluster.
  4. The unattributed claims are grouped by single linkage (connected components) on the correlation of their incremental forecasts (M_c − B*, transformation ungated) on the first oracle test draw, with threshold ≥ 0.9.
  5. A cluster is false if any member is FALSE or INDETERMINATE.
  6. **Negative claims:** steps 1–4 are applied to the arm's validated negative units together with every positive claim in the same batch, confirmed or not (for A3, every asserted positive claim). A negative matches a positive claim (§G.5) if they share a cluster. S6 counts useful negatives once per cluster.
- **Asserted level** (confirmed claims for referee arms; asserted claims for A3):
  - R^asr_{a,w} = the number of clusters;
  - V^asr_{a,w} = the number of false clusters.
- **Validated level:** R^val and V^val, the same on the validated positive units.
- **Per-world quantities:**
  - FDP_{a,w} = V / max(R, 1) at each level;
  - the indicator Z_{a,w} = 1{V^val_{a,w} ≥ 1}.
- **FDR^lvl_a** = the mean of FDP^lvl_{a,w} over all evaluation worlds, null worlds included, and **mFDR^lvl_a** = ΣV^lvl / ΣR^lvl pooled over all evaluation worlds (0 if ΣR^lvl = 0), for lvl ∈ {asr, val}. FDR_a without a superscript means FDR^val_a, which is bounded above by mean(Z). F2 uses mFDR^asr.
- **FWER on null worlds** = the share of null worlds with R^val ≥ 1 (reported).
- **Diagnostic:** the inherited-cluster variant (validated clusters inherited from the asserted level), as a sensitivity analysis.

### J.5 Grades (negative claims)

TRUE-NEG iff θ̂_o + 3·s_o < δ_c; FALSE-NEG iff θ̂_o − 3·s_o ≥ δ_c; otherwise INDETERMINATE. `[DECISION]`

### J.6 Novelty and deduplication

`[DECISION]`
- **Novelty against the baseline.** B* contains all disclosed information (§C.10), and every credited claim must beat it by δ_c. Every credited claim is therefore novel relative to B*.
- **Novelty against credited claims.** Coverage is computed at set level, so a second claim on an already covered mechanism adds nothing.
- **Deduplication** acts at the level of the planted mechanism (§J.3) and of the mechanism-attributed cluster (§J.4).

---

## K. Endpoints and statistics

### K.1 Primary endpoint

`[DECISION]`
- **TRK_{a,w}** (§J.3): distinct planted mechanisms covered by the arm's validated, TRUE positive claims, at the fixed budget of §H.
- **Primary comparison:** paired across non-null evaluation worlds. For each control c ∈ 𝒞, Δ_{c,w} = TRK_{A5,w} − TRK_{c,w}, and Δ_c = the mean over worlds.
- **Gates.** The primary endpoint counts only if these hold:
  - the FDR gates (§K.4);
  - zero critical leakage (§K.5);
  - reproducibility (§K.5).
- **INVALID or failed-reproduction world-runs (§G.5 conditions 4–5) that are not critical-leak events and do not already decide the outcome (§K.5):**
  - for a comparator arm c, world w is dropped from the Δ_c contrast and from the matching F2 difference (pairwise deletion);
  - for A5, TRK_{A5,w} = 0, and for F1 and FDP, Z_{A5,w} and FDP_{A5,w} are computed on its confirmed and replicated claims without §G.5 condition 4 (conservative).

  If INVALID world-runs exceed 2% of world-runs, pooled or for any single arm, the outcome is VOID-BENCHMARK (§L, as for harness errors in §C.12); this VOID never replaces a KILL-type outcome (§L rule 1(b)). Per-arm INVALID counts are reported.

### K.2 Secondary endpoints

These are reported with 95% intervals. They are not adjusted for multiplicity and are labelled exploratory. `[DECISION]`

| ID | Endpoint | Definition |
|---|---|---|
| S1 | Precision and recall over discoverable mechanisms | **Mechanism precision:** (distinct mechanisms attributed to TRUE validated units + unattributed TRUE clusters) ÷ (that number + V^val). Per-claim precision is descriptive only. **Recall against planted:** covered ÷ planted (J_w), in-family and out-of-family separately. **Pipeline-discoverable recall:** Σ_w \|covered ∩ ORC-covered\| ÷ Σ_w \|ORC-covered\|, pooled over in-family worlds. It is not defined for out-of-family worlds, and coverage outside ORC's set is reported as a count. Form-correct and linear-proxy coverage are reported separately |
| S2 | False discoveries | FDR and mFDR at both levels; mean(Z); FWER on null worlds; the OVERSTATED and NULL shares; the distribution of per-world FDP^val for A5 (the share of worlds with FDP > 0.10); the sensitivity analysis without INDETERMINATE; **trap-lured claims**, i.e. claims graded FALSE whose driver is a TRAP-REV or TRAP-LAG series; the FALSE-NEG and INDETERMINATE shares of validated negatives; the 1A-style conditional grades and the split of FDP into test error and estimand gap (§J.1) |
| S3 | Predictive improvement over strong baselines | Θ(C_{a,w}; P) against B*, and against A1's credited set in the same world |
| S4 | Research-policy violations | Per world-run counts from deterministic detectors: blocked accesses (B-AUDIT); invalid fields; cap and second-batch attempts; post-receipt modification attempts; matches of the frozen transcript pattern list; model-behaviour failures (§C.12) |
| S5 | Reproducibility | Record/replay mismatches (§K.5); the run-to-run SD of TRK from the model rerun (§K.6) |
| S6 | Useful negative findings | Useful negatives (§G.5) per world, counted per cluster; TRUE-NEG precision; how often each arm saturates the cap of 2; the count under the older rule (discovery t ≥ 2.5) as a sensitivity analysis |
| S7 | Transfer to related unseen worlds (probe) | A block of 12 sibling worlds after the primary block. Each shares the catalogue IDs and roles of one primary world: 4 with identical mechanisms, 4 with one mechanism removed (a false-import trap), and 4 with one mechanism added. Arms A1, A4 and A5. **Measures:** TRK; the **false-import rate**, defined as A5's excess of FALSE claims on removed drivers over A4 and A1 on the same drivers; the **stale-negative import metric**: among added mechanisms whose driver has a VALIDATED_NEGATIVE, CONFIRMATION_FAILED or REPLICATION_FAILED item in A5's memory, the share not covered by A5, next to A4's non-coverage share on the same set; reported as a count and denominator, and undefined when the set is empty. Non-gating; Experiment 3 is the real test (§M) |
| S8 | Memory gain | Δ(A5 − A4) on TRK and FDR, overall and by world-index tercile (the learning curve); memory item and eviction counts |
| S9 | Out-of-family generalisation | Every endpoint on the out-of-family subset; Δ_c separately for in-family and out-of-family worlds. Exploratory and unadjusted; also A5's in-family minus out-of-family TRK gap relative to A1's (confounded by genuine generalisation, and underpowered with 12 annex worlds) |
| S10 | Budget sensitivity | A1 and A2 at C ∈ {0.25, 1, 4} × C₀ on the first 20 non-null worlds; evaluation counts |
| S11 | Referee value | A4 against A3 on TRK; A4 and A5 against A3 on FDR (F3); A3's replication-only TRK |
| S12 | Pipeline ceiling | ORC coverage per world |

### K.3 Primary decision statistics and the central kill rule

`[DECISION]`, with the scope of H2 `[OPEN]` under owner decision 2.

**Controls.**
- **Default (the owner's literal kill rule):** 𝒞 = {A1, A2, A3, A4}.
- **Recommended alternative (owner decision 2):** 𝒞 = {A1, A2, A3}, plus two memory conditions:
  - memory non-inferiority: LB₉₅(Δ_{A4}) > −MEI;
  - memory harm: UB_{98.75}(Δ_{A4}) < −MEI, which is a KILL route.

  Under this alternative, memory superiority (Δ_{A4} > 0) is secondary here (S8) and primary in Experiment 3.

**Statistics.**
- For each c: the paired mean Δ̂_c.
- **Standard error:** SE_c = sd(Δ_{c,w})/√N over the N non-null evaluation worlds.
  - For every statistic involving A5, SE = max(the iid SE, the Newey–West SE along world order with lag 4 and a Bartlett kernel).
  - One-sided bounds use Student t with N − 1 degrees of freedom.
  - The lag-1 to lag-4 autocorrelations of Δ_{c,w}, FDP_{A5,w} and Z_{A5,w} in world order are reported as a diagnostic.
- **Assumption** `[ASSUMPTION]`. Inference is conditional on the single realised memory trajectory. A persistent effect of early memory cannot be separated from A5's mean effect, and the §K.6 rerun does not measure between-trajectory variance.
  - As an option under owner decision 3, a second A5 trajectory on an independently drawn world order supplies that variance. It costs about +75 A5 world-runs, or about 0.75–3 × 10⁸ input tokens.

**MEI** = 0.3 covered mechanisms per non-null world, about 10% of the mean planted count (owner decision 4). `[OPEN]`

**Per-control rules:**
- **beats(c):** LB₉₅(Δ_c) > 0 **and** Δ̂_c ≥ MEI.
- **fails(c):** UB_{98.75}(Δ_c) < MEI.
  - 98.75% = 1 − 0.05/4 is a Bonferroni split over the four KILL tests on TRK: fails(c) for each c in the default 𝒞, or fails(c) for the three controls plus memory harm under the recommended alternative.
  - **The probability that one of these four tests kills wrongly, when every Δ_c = MEI, is ≤ 0.05.** This covers only these four tests; the total over all kill routes is stated below.

**Intersection–union.** CONTINUE requires beats(c) for **every** c. Each beats(c) is tested at one-sided α = 0.05, and requiring all of them is an intersection–union test. The probability of a false CONTINUE when any Δ_c ≤ 0 is therefore ≤ 0.05, with no multiplicity correction. `[INFERENCE, standard IUT property; conditional on the SE being valid]`

**Total wrongful-KILL probability** `[INFERENCE, union bound, σ_Δ = 1, N = 60]`. When every Δ_c = MEI and the FDR gates sit exactly at their boundaries, the kill routes add up to at most about 0.17:

| Route | Contribution |
|---|---|
| KILL-FUTILITY (UB₉₅ rule, §K.7) | 0.04 |
| The four TRK kill tests | ≤ 0.044 |
| F1-kill at a per-world false-validation rate of 0.10 | ≈ 0.034 |
| F2-kill, Bonferroni over 3 controls (0.017 each at an inflation of exactly 0.05) | ≤ 0.05 |

When the FDR gates are comfortably met, the total is about 0.08. With the UB₈₀ futility alternative, the futility route alone is 0.19.

**Central kill rule (owner, verbatim intent):** "the full system fails if it cannot outperform scripted and ablated controls on true replicated knowledge per fixed budget without inflating false discoveries." It is operationalised in §L.

### K.4 False-discovery gates

`[DECISION]`, with thresholds `[OPEN]` under owner decision 4.

| Gate | Rule | Role |
|---|---|---|
| **F1: ceiling** | Let x = the number of evaluation worlds with Z_{A5,w} = 1, i.e. with at least one false validated cluster (§J.4). F1 passes iff the Clopper–Pearson UB₉₅(x, n_worlds) ≤ 0.10. At 75 worlds that means x ≤ 2 (UB = 0.082); at 150 worlds, x ≤ 8 | Required for CONTINUE |
| **F1-kill** | LB₉₅(x, n_worlds) > 0.10: x ≥ 13 of 75, or x ≥ 22 of 150 | KILL |
| **F2: no inflation** | For every referee control c ∈ {A1, A2, A4}: the estimate of mFDR^asr_{A5} − mFDR^asr_c is ≤ 0.05 **and** its UB₉₅ is ≤ 0.10 (the same shape as beats(c)). The paired difference of pooled ratios is bounded by the delta method with world-level clustering; if ΣV^asr < 10 in either arm, by a percentile bound that resamples whole worlds, pre-registered with the analysis code | Required for CONTINUE |
| **F2, sparse controls** | If ΣR^asr_c < 20, the precision of control c cannot be estimated. For that control, m_c is replaced by a reference value of 0.05: F2 requires the estimate of mFDR^asr_{A5} ≤ 0.10 and its UB₉₅ ≤ 0.15, and F2-kill fires if its LB_{98.33} > 0.10 | Required for CONTINUE |
| **F2-kill** | For some c ∈ {A1, A2, A4}: LB_{98.33} of the same paired difference > 0.05. This is a Bonferroni split over 3 controls. F2 and F2-kill are mutually exclusive, because F2 needs an estimate ≤ 0.05 | KILL |
| **F3: A3** | FDR and mFDR of A4 and A5 against A3 | Reported (S11) |
| **Validity of negatives** | The FALSE-NEG share of validated negatives | **Reported, ungated.** The recommended default under decision 4; the alternative is a KILL-type flag if LB₉₅ of the share exceeds 0.10 |

**Why a world indicator for F1.** FDP_w ≤ Z_w, so a valid upper bound on mean(Z) is a valid, conservative upper bound on FDR. The Clopper–Pearson bound stays valid for independent, non-identically distributed Bernoulli indicators in this tail (Hoeffding, 1956). A Student-t bound on the zero-inflated FDP values would under-cover. For A5 the Z_{A5,w} are serially dependent through memory, so F1 and F1-kill are interpreted conditional on the realised memory trajectory (§K.3). `[INFERENCE]`

**Why F2 has two conditions.** With about 75 worlds and a few asserted clusters per world, the SE of the paired difference is about 0.010–0.058 (Appendix A.7). A rule of UB₉₅ ≤ 0.05 alone would fail about half the time even with no inflation. The adopted rule passes with probability 0.53–1.00 with no inflation (0.96 at the conservative planning values of Appendix A.7, 0.99 at m = 0.05) and at most 0.50 at an inflation of 0.05. The earlier rule passed only 0.55 at those planning values. `[INFERENCE]`

**What F1 and F2 measure.** Pipeline truth (§J.1), not referee size.

### K.5 Leakage and reproducibility gates

`[DECISION]`

**Critical-leak events:**
- a canary in any sandbox-visible byte, model request or response, claim or memory item;
- a sealed-store read that returned data;
- network egress from the sandbox;
- a memory item that violates §I.4, or a rerun write reaching the primary memory store;
- an INVALID world-run (MRS-2) whose failing control affected a submitted claim's features.

A blocked attempt is a policy violation (S4), not a leak.

**Attribution map.** Attribution is pre-registered in F_H(2-eval) and applied by frozen code. The owner of the first-exposure or first-mismatch path in B-AUDIT decides:

| Path owner | Attribution |
|---|---|
| S-GEN-owned code: generator, truth store, oracle, replication, orchestrator | **TH** |
| The agent runner, tool wrappers or relay (a separate principal, §B.1) | **TH** |
| S-REF-owned TCB, B-SBX, the B-MEM validator | **SUT** |
| Unattributable | **SUT** |

**One rule for KILL-LEAK.** A SUT-attributed critical-leak event in any world-run whose failed boundary is part of the SUT → **KILL-LEAK**. That covers referee components in A1, A2, A4 and A5, and the sandbox or memory validator in A0 and A3–A5. KILL-LEAK takes precedence over any VOID caused by an MRS revocation that the same leak triggered.

**Zero critical leakage** is a gate for CONTINUE. For the referee arms it is a gate, not a finding.

**Reproducibility.**
- **Replay subset.** After the last world-run closes, and before campaign close (§K.8), a 20% subset of every arm's world-runs is selected with M_post (the 1A §I.7 rule, with the stream names of §O).
- **Replay.** The subset is replayed from recorded model outputs.
- **Gate:** 0 verdict-level mismatches. A verdict-level mismatch is any difference in a receipt, verdict, replication result, grade or TRK.
- **Failed-reproduction set** = world-runs in the replay subset with a verdict-level mismatch.
- **Attribution:** SUT-attributed → KILL-REPRO. TH-attributed, in generation, the oracle, replication or scoring → VOID-BENCHMARK. TH-attributed elsewhere (agent runner, tool wrappers, relay) → VOID-BENCHMARK, under the §L preservation rule. Differences confined to logs are reported.

**Metadata leak.** VOID-BENCHMARK if LB₉₅ of A0's pooled AUC for mechanism components, or for traps, exceeds 0.60, evaluated at the post-tuning calibration gate on 40 fresh development worlds from stream `dev-cal` (8 null, 32 in-family), never tuning worlds, before C2-eval. One failure voids; no amendment applies, because the only permitted amendment changes the generator prior and cannot repair a metadata leak. On evaluation worlds the AUC is a diagnostic.

**Contamination check** `[DECISION]`:
- **(a) Record dates.** Record the pinned researcher model's declared training-data cutoff, and the date of the first public commit of the Experiment 2 documents. If the cutoff is earlier, contamination by this document is excluded.
- **(b) Recall probe.** Otherwise, before the campaign, run a recall probe. It asks the model to recall §C-specific facts (hinge quantiles, θ^solo bounds, trap-archetype names, segment boundaries) against matched decoy facts. It is report-only: the accuracy on §C facts and on the matched decoys, and the exact binomial 95% interval of their difference, are reported with the §N item 12 caveat. It gates nothing.
- **(c) Optional canary.** A public document canary chosen by the owner, distinct from §O.4's sealed-store canaries and never mapped to a critical-leak event.

### K.6 Model run-to-run variance

`[DECISION]`
- 15 evaluation worlds, fixed by seed purpose `order` at the ceremony, are rerun once for A4 and A5 with fresh sampling: 30 world-runs.
- A5 reruns use the ledgered snapshot of the same world index, with isolated writes (§I.4).
- The reruns give the between-run SD of TRK. This is secondary (S5); the primary analysis uses the first run only.

### K.7 Sample size and interim

**Default N** `[OPEN]`, owner decision 3:
- 60 non-null evaluation worlds (48 in-family, 12 out-of-family) and ⌈60/4⌉ = 15 null worlds;
- 12 transfer-probe worlds;
- 15 rerun worlds (30 world-runs: A4 and A5).

**Planning SD:** σ_Δ = 1.0 covered mechanism per world `[ASSUMPTION]`.

**Blind re-estimation.** After EK-B1, σ_Δ is re-estimated on the **non-null** EK-B1 development worlds only (32 by default), or on the fresh post-amendment non-null development worlds if a calibration amendment is made. The re-estimate is conservative and does not assume positive correlation between arms:

σ̂_Δ = max(sd(TRK_A1 − TRK_A2), √(var(TRK_A1) + var(TRK_ORC)))

Both components are reported.
- N is set to ⌈(1.15·σ̂_Δ/(0.5·MEI))²⌉, rounded up to a multiple of 5 and bounded to [60, 120] non-null worlds.
- The null count is ⌈N/4⌉. The in-family and out-of-family counts are 0.8N and 0.2N, which are integers because N is a multiple of 5.
- **Guarantee.** This keeps P(beats(c)) ≥ 0.875 at Δ_c = 1.5·MEI only while σ̂_Δ ≤ 1.43. Above that, N is capped at 120, and P(beats) at 1.5·MEI = 1 − Φ((max(t₀.₉₅·SE, MEI) − 1.5·MEI)/SE), with SE = σ̂_Δ/√120: for example 0.863 at σ̂_Δ = 1.5 and about 0.79 at 2.0. That value is reported in the re-estimation record.

`[DECISION]`

**Operating characteristics** at N = 60 and σ_Δ = 1 (normal approximation with Student-t critical values, under independence across worlds; Appendix A):

| True Δ_c | P(beats(c)) | P(fails(c)) |
|---|---|---|
| −0.2 | 0.000 | 0.942 |
| 0 | 0.010 | 0.509 |
| 0.15 | 0.123 | 0.128 |
| 0.3 (= MEI) | 0.500 | 0.011 |
| 0.45 | 0.877 | 0.000 |
| 0.6 | 0.990 | 0.000 |

- With every control at Δ = 0.6, P(the TRK conditions of CONTINUE hold) ≥ 0.959 (Bonferroni bound; 0.960 if the comparisons were independent). At Δ = 0.45 it is ≥ 0.509 (Bonferroni; 0.59 if independent). Δ = 0.6 against A1 and A2 is optimistic, because A1 reaches every in-family exact encoding within about 2.6 × 10³ evaluations, and A2 exhausts DSL depth ≤ 1 if an evaluation costs ≲ 0.2 CPU-s (§I.3).
- **Consequence for the literal rule** `[INFERENCE]`. If memory has no effect (Δ_{A4} = 0), then P(KILL) ≥ 0.509 and P(CONTINUE) ≤ 0.010 from the TRK conditions alone. The other kill routes can only raise P(KILL).
- **Under the recommended alternative,** the memory non-inferiority condition passes with probability 0.743 at Δ_{A4} = 0 (Appendix A.5).

**Interim futility (EK-B2; binding).**
- After the first 20 evaluation worlds (16 non-null), compute an upper bound on Δ_{A1}. **If it is below MEI → stop: KILL-FUTILITY.** Otherwise continue.
- Nothing else is unblinded; only the stop or continue decision is released.
- Binding futility cannot raise the probability of a false CONTINUE.
- **Default (recommended):** UB₉₅ with t₁₅ = 1.753 and the §K.3 SE. At σ_Δ = 1 (SE = 0.25) this is: stop iff Δ̂_{A1} < −0.138.
- **Alternative:** UB₈₀ with t₁₅ = 0.866. At σ_Δ = 1: stop iff Δ̂_{A1} < 0.083.

**Futility operating characteristics** (σ_Δ = 1; Appendix A.2):

| Rule | P(stop), Δ = 0 | Δ = MEI | Δ = 2·MEI | Linear learning curve 0.15 → 0.45 (mean MEI) | Linear learning curve 0 → 0.6 (mean MEI) |
|---|---|---|---|---|---|
| **UB₉₅ (default)** | 0.29 | 0.04 | 0.002 | 0.10 | 0.20 |
| UB₈₀ | 0.63 | 0.19 | 0.02 | 0.34 | 0.51 |

The default keeps P(stop) ≤ 0.20 when the campaign-mean Δ equals MEI, under the two linear learning curves of Appendix A.2 (σ_Δ = 1, 75 worlds). A steeper or back-loaded curve, or a smaller σ_Δ, can raise it (for example about 0.26 for the 0 → 0.6 curve at σ_Δ = 0.8). That matters because A5's memory starts empty and the interim block has the smallest memory.

**No extension.** An AMBIGUOUS outcome is final and is reported as "not established". Any follow-up needs a new pre-registration on fresh worlds. `[DECISION]`

### K.8 Blinding

`[DECISION]`
- **What is blinded until campaign close:** truth grades, coverage, TRK, FDR, per-arm confirmation decisions, evidence packages, replication verdicts, validated-unit counts and institutional-ledger entries.
- The TH delivers these only to the originating world-run's sealed record and to A5's memory writer (§I.4). Every other person and session is denied access, and the access list is ledgered.
- **Campaign close** is reached when the replay subset, every §I.4 quarantine rerun, every §B.3 MRS-reopen rerun and every attribution (§K.5) are complete. Blinding lasts until then.
- **In-campaign judgement calls.** Every in-campaign attribution, harness-error classification and memory audit is made either by frozen code hashed in F_H(2-eval), or by a named person with no access to the blinded items. That person's decision is recorded in the ledger before any unblinding.
- **Exceptions:** the EK-B2 stop or continue decision, and the pre-C2-eval calibration results, are computed by frozen code and released as pass or fail.
- The analysis code is hashed in F_H(2-eval).

---

## L. Outcomes: kill, continue, ambiguous and void

`[DECISION]`

**Preservation rule** (mirroring 1A §H.1).
- A KILL, KILL-LEAK, KILL-REPRO, KILL-FUTILITY, F1-kill or F2-kill computed by frozen code is **never turned into VOID-BENCHMARK**. The only exception is a trigger that invalidates the worlds or the truth itself:
  - a TH-attributed critical leak whose first-exposure path is S-GEN-owned code (generator, truth store, oracle, replication, orchestrator);
  - a TH-attributed reproducibility mismatch in generation, the oracle, replication or scoring;
  - generator self-check failures above 2% of worlds.

  These apply to events detected and attributed before campaign close (§K.8); later findings follow §B.3.
- An MRS revocation before campaign close (§K.8) whose rerun the owner declines, an amendment after C2-eval, or an operator-inducible void (harness errors, including verified provider-infrastructure failures, §C.12; INVALID world-runs above 2%; a TH-attributed critical leak or mismatch in the agent runner, tool wrappers or relay) can void a CONTINUE or an AMBIGUOUS outcome, but never a completed KILL. After campaign close, an audit finding follows §B.3: if the §K.5 map assigns it to the SUT (unattributable included), the outcome becomes KILL-LEAK or KILL-REPRO, whatever the earlier outcome; if it assigns it to the TH, a CONTINUE is withdrawn and reported as "not established", and every other outcome is unchanged. It never produces VOID-BENCHMARK and never triggers a rerun.

**Rules**, evaluated in this order; the first that applies decides:

| Order | Outcome | Condition |
|---|---|---|
| 1 | **VOID-BENCHMARK** | (a) **Always, for events detected and attributed before campaign close (§K.8):** a TH-attributed critical leak in S-GEN-owned code; a TH-attributed reproducibility mismatch in generation, the oracle, replication or scoring; generator self-check failures above 2% of worlds; before C2-eval, the A0 metadata-leak rule (§K.5) or a second calibration failure (§P.2). (b) **Only if none of rules 2–5 applies:** harness errors above 2% of world-runs (pooled, or for any of A1–A5; §C.12) or INVALID world-runs above 2% (pooled or for any arm); a TH-attributed critical leak or reproducibility mismatch in the agent runner, tool wrappers or relay; an MRS revocation before campaign close whose rerun the owner declines; an amendment after C2-eval (§S). Findings after campaign close follow §B.3, never this rule. **The benchmark design, not the thesis, has failed** |
| 2 | **KILL-LEAK** | A SUT-attributed critical-leak event (§K.5) |
| 3 | **KILL-REPRO** | A SUT-attributed verdict-level reproducibility mismatch |
| 4 | **KILL-FUTILITY** | The EK-B2 futility rule fired (§K.7) |
| 5 | **KILL** (central rule) | Any of: fails(c) for some c ∈ 𝒞; F1-kill; F2-kill; or, under the recommended decision-2 alternative, memory harm |
| 6 | **CONTINUE** | All of: beats(c) for every c ∈ 𝒞; F1; F2; zero critical leakage; the reproducibility gate; and, under the recommended alternative, memory non-inferiority |
| 7 | **AMBIGUOUS** | Otherwise. **Final**; reported as "not established" (no extension) |

**Calibration VOIDs happen before C2-eval, not after.** The in-family ORC floor, the in-family headroom rule, and the out-of-family ORC-A floor and headroom rule run at EK-B1 and again at the post-tuning calibration gate, on held-out development worlds (§P.2). The A0 metadata-leak rule runs at the post-tuning gate. Their pass or fail is ledgered before C2-eval. On evaluation worlds, ORC and A1 coverage and A0's AUC are **diagnostics only**. This removes a route by which a KILL could be turned into a VOID.
- **Expected ORC in-family coverage** is about 0.91 (Appendix A.4), a margin of about 0.10 to the 0.80 floor `[INFERENCE]`.
- **The headroom rule is the check most likely to fail,** because A1 can enumerate every in-family exact encoding (§I.3). The single permitted amendment can create headroom only by weakening the mechanisms (strength or J).

**Closure after a second VOID.** A second VOID-BENCHMARK from C2-eval onward, or a second abort of the same stage, closes Experiment 2 as VOID. Any further attempt needs a new, approved pre-registration that discloses any use of the released truth stores in redesigning the generator.

**Meaning of each outcome:**
- **CONTINUE, under the default decision 2:** on 𝒢₂ and its annex, the full system produced more true, replicated, non-duplicative knowledge per fixed budget than A1, A2, A3 and A4, with controlled false discoveries. In-family, this measures selection and validation under a fixed budget, not hypothesis generation (§I.3).
- **CONTINUE, under the recommended alternative:** the same, but against A1, A2 and A3 only. A5 was not worse than the memory-ablated A4 by more than MEI, and memory superiority is not established (it is tested in Experiment 3).
- **What CONTINUE authorizes:** writing the Experiment 3 pre-registration. It authorizes no product or real-data claim (§N).
- **KILL:** the integrated-system thesis fails as tested. The owner decides whether to stop, or to redesign under a new pre-registration. A KILL cannot be reversed by reanalysis or by a later audit (§B.3).
- **AMBIGUOUS:** the thesis is neither supported nor refuted at this sample size.

**Mutual exclusivity.** beats(c) requires Δ̂_c ≥ MEI, so UB(Δ_c) > MEI, and fails(c) cannot then hold. Rules 5 and 6 cannot both hold. `[INFERENCE, arithmetic]`

Appendix B gives the machine-readable logic.

---

## M. Separation from the knowledge-accumulation test (Experiment 3)

**Why Experiment 2 is not the memory test.** `[DECISION]`
- Experiment 2's worlds are independent draws with IDs unique to each world, so memory can carry only procedural regularities of the family.
- It therefore tests whether memory helps research **procedure**, not whether accumulated **substantive** knowledge transfers.
- Its transfer probe (S7) is a 12-world pilot, too small to decide anything.

**Experiment 3 (sketch; its own pre-registration, ceremony and worlds are required).** `[INFERENCE, not a pre-registered decision]`

**Question.** Does validated, structured memory raise TRK and cut false claims on related but non-identical future worlds, compared with a memory-ablated twin, without importing false conclusions?

**Lineages.** A root world and 4 sequential descendants.
- **Same catalogue.** Every descendant keeps exactly the parent's set of series IDs and its catalogue size.
  - Retired and altered drivers stay under their IDs, the retired ones as null series.
  - New mechanisms are planted on existing series, for example formerly null ones.
  - If new series are ever needed, every descendant replaces a fixed number of randomly chosen series with fresh IDs, and the roles of the fresh series are drawn independently of their novelty. Novelty then carries no role information.
- **Controlled edits:**
  1. persistent mechanisms (unchanged);
  2. **retired** mechanisms, removed (the false-import trap);
  3. **altered** mechanisms: a threshold moves, a sign flips, or a regime gate changes;
  4. new mechanisms;
  5. **negative reversal**: a new mechanism planted on a series that was null but attractive (discovery t ≥ 2.5) in the parent, so stale negatives can occur by design;
  6. a procedural change in the publication or revision law.
- **Hidden change points.** Change points are **never disclosed to any arm**, and the harness never edits, filters or expires memory using truth. Any expiry depends only on an item's age (world index) or on capacity.

**Trap-transfer worlds.** A mechanism validated in the parent is retired in the child. Retired drivers occur both **with** a spurious discovery-period correlation (a TRAP-SEL path: import plus susceptibility) and **without** one (pure import, where memoryless arms have no reason to claim).

**Arms:**
- A5 (memory);
- A4 (memory ablated);
- A5-placebo;
- A1 as the scripted floor.

**The A5-placebo memory.** It comes from a different lineage and is re-keyed to the current lineage by a seeded bijection.
- The bijection maps Y, D1 and D2 to themselves, and binary series to binary series.
- Otherwise it matches series only on disclosed metadata (nominal lag, revised flag, unit class), choosing uniformly among metadata-matched candidates, independently of every hidden role.
- Placebo items then match real memory in format, ID coverage and metadata consistency, while their overlap with true drivers is at chance.
- The mapping and its seed are ledgered at the ceremony and sealed until campaign close.

**Guards against importing false conclusions:**
- every memory item carries known_at (its world index) and provenance;
- a claim identical to a memory item still needs fresh confirmation and replication in the new world. **Protection against false imports comes only from that mandatory fresh confirmation and replication**;
- memory never holds truth;
- validated negatives with δ_c > δ_min are stored as upper bounds (§I.4), never as "no effect".

**Metrics:**
- TRK on descendants;
- the **false-import rate**: A5's excess rate of FALSE claims on retired or altered drivers over A5-placebo and over A4 on the same drivers, reported separately for retired drivers with and without a TRAP-SEL path;
- the **stale-negative import rate**: among new, altered or reversed mechanisms whose driver has a VALIDATED_NEGATIVE, CONFIRMATION_FAILED or REPLICATION_FAILED item in A5's memory from an earlier world, the share not covered by A5, against A4's non-coverage share on the same set;
- **stale-procedure effects** for edit 6: claims or policy violations consistent with the parent's stale publication or revision law, as A5's excess over A5-placebo and A4;
- worlds until the first validated unit on a persistent mechanism;
- budget efficiency (TRK per token and per CPU-hour);
- calibration of the system's stated confidence.

**Relation to Experiment 2.** Under the recommended decision-2 alternative, Experiment 3's primary endpoint is memory superiority, and Experiment 2 contributes only non-inferiority and the S7 and S8 pilot estimates. Experiment 4 (incentives) is unchanged from memo v2 §18.

---

## N. Claim boundaries

`[DECISION]`

**A CONTINUE on Experiment 2 shows only controlled epistemic competence.** On synthetic worlds from 𝒢₂ and its sealed annex, generated after the freeze, the integrated system found more true, replicated, non-duplicative predictive relationships per fixed budget than the controls in 𝒞, while keeping false discoveries within the gates. Under the recommended decision 2, it also shows that memory did not hurt by more than MEI; it does not show that memory helped.

**It does not show any of the following:**
1. **Tradable alpha or profitability.** There are no prices, costs, positions or markets. Predictive skill of 1–15% relative MSE on a synthetic outcome says nothing about returns.
2. **Causal knowledge.** Truth is predictive under the forward law (§J.1), and proxies can earn coverage. Planted mechanisms are causal inside the generator, but no claim is tested for causality.
3. **Real-data robustness.** There are no real vintages, real publication pathologies, structural breaks beyond TRAP-BRK, or non-stationarity beyond the family. 1B is `BLOCKED_BY_ACCESS`.
4. **Willingness to pay**, or any commercial signal.
5. **A certified referee.**
   - The referee passed the MRS only (§B.3). The Experiment 1A §A.5 caveat applies in addition to this document's caveat whenever 1A claims are made.
   - The researcher-code sandbox ι₂ is conformance-checked (MRS-9), not attacked or certified (§B.2).
   - The oracle shares the referee's evaluator and learner (§B.1), so an evaluator bug that MRS-2, MRS-3 and MRS-11 miss would be invisible to the truth.
6. **Resistance to deliberate adversaries.** No red-team arm is run. Gaming is measured only as policy violations (S4).
7. **Domain reasoning.** Series are obfuscated, so the test covers blind search only. It says nothing about using economic semantics, or about behaviour on named real series.
8. **Search equivalence.** The AI arms may search with self-written code, metered by CPU only; the scripted arms use B-EVAL within the same CPU budget.
9. **Generalisation** beyond 𝒢₂ and 𝒢₂ᴬ, beyond κ₂ (daily, horizon 1, one outcome), or beyond the pinned model snapshot, brief and budgets.
10. **Independent replication in the scientific sense.** Replication is a same-law harness replication (§G.4).
11. **Memory benefit on related future problems** beyond the 12-world probe. That is Experiment 3.
12. **Freedom from common-model bias** `[ASSUMPTION]`.
    - This pre-registration, including §C, the DSL, the traps and its adversarial review, was drafted by Claude sessions, the same model family as a likely researcher model.
    - If the researcher's training data contain this document, it may exploit design regularities.
    - The annex (16% of evaluation worlds, mechanism search only; §C.9), the A0 probe (which detects implementation metadata leaks only), the §K.5 contamination check and model separation reduce this risk but do not remove it.
    - **Recommended before freeze (owner decision 10):** an independent human or different-vendor review.
13. **Anything about t0.** Unless owner decision 5 replaces the κ₂ ridge learner with t0, no Experiment 2 result says anything about t0 or its covariate pathway. Even under decision 5, results concern t0 on 𝒢₂ only, and no Experiment 2 result says anything about real forecasting targets (item 3).
14. **Hypothesis generation.** Every in-family exact encoding lies at DSL depth ≤ 1 (about 10⁴ expressions), which the scripted controls can screen within C₀ (A1 at up to about 2.7 CPU-s per evaluation; A2's full enumeration if an evaluation costs ≲ 0.2 CPU-s; measured by the EK-B1 Q meter, §I.3). In-family, a CONTINUE therefore shows better selection and validation under a fixed budget, not better hypothesis generation. Generation is only probed by the 12 out-of-family worlds (S9, exploratory, not gated).
15. **Robustness of A5's result to its memory trajectory** `[ASSUMPTION]`. Inference on every A5 statistic is conditional on the single realised memory trajectory (§K.3). A persistent effect of early memory cannot be separated from A5's mean effect, and the §K.6 rerun does not measure between-trajectory variance.

---

## O. Seed and ground-truth commitment protocol

The protocol reuses 1A §I, with new domains and purposes. **No seed, secret or commitment was generated in drafting this document.** `[DECISION]`

### O.1 Ceremonies

| Ceremony | Domain | When | Purpose |
|---|---|---|---|
| C2-dev | `2-dev` | After freeze and owner approval | MRS; EK-B1; tuning worlds; λ; the post-tuning calibration gate (stream `dev-cal`); out-of-family calibration (`dev-oof`); calibration amendment, if any |
| C2-eval | `2-eval` | After the MRS, the post-tuning calibration gate and the code-freeze commit | Evaluation, transfer-probe and rerun worlds |

Development worlds are never reused for evaluation. `[DECISION]`

### O.2 What is committed before any secret exists

`[DECISION]`
- **P_H(2)** = SHA-256 of this file's exact committed bytes at its frozen version.
- **F_H(2-dev)** covers:
  - this document;
  - the annex hash;
  - the generator, oracle and replication code;
  - the MRS libraries;
  - the canary scheme;
  - the component-to-MRS-item map.
- **F_H(2-eval)** covers, in addition:
  - every TCB component, and B-EVAL;
  - the MRS results, with the hashes of their mapped components (§B.3);
  - A1, A2, ORC, ORC-A and the A0 prompt;
  - the brief, the agent runner and the tool wrappers, together with the artefact-audit record (§B.4);
  - the pinned model snapshot identifier and sampling settings;
  - the budgets;
  - the transcript pattern list (S4);
  - the attribution map (§K.5);
  - the analysis code;
  - the λ table and any calibration amendment;
  - the lock file and the container image digest.
- **Custody.** Entropy, custody and injection follow 1A §I.3–§I.4: a protected GitHub Environment named after the domain (`2-dev`, `2-eval`), the owner's secret S_O plus the Environment secret S_I, and the abort-and-intersection rule. They follow the owner's 1A decision 7, which must be decided before this document is frozen (see the 1A owner review, Part II).
- **Aborts and operator-inducible voids.**
  - For a C2-eval ceremony aborted after any world-run has started, and for any void an operator could induce, the frozen analysis is run on that ceremony's completed world-runs and published.
  - **The reported outcome is the less favourable of the two campaigns,** ordered KILL, then AMBIGUOUS, then CONTINUE.
  - A ceremony aborted before any world-run starts is re-held once, under 1A §I.4, with fresh entropy.

### O.3 Seed derivation and ground truth

`[DECISION]`
- **Derivation.** M and seed(purpose, stream, index) as in 1A §I.5, with the domain strings above and the prefix `2-master-v1`.
- **Purposes:** `world`, `permute_ids`, `calib`, `trap_redraw`, `replicate`, `oracle`, `order`, `a2_search`, `inline`, `canary`, `probe`.
- **Streams:** `dev-mrs`, `dev-ekb1`, `dev-tune`, `dev-cal`, `dev-oof`, `dev-null`, `dev-val` (linear validation worlds), `eval`, `xfer`.
- **Replication and oracle seeds** are determined by M, so they are fixed before any arm runs. No arm and no runner principal can read them (MRS-7).
- **Ground-truth commitment.** When it generates each world, the harness writes the truth store (roles, mechanisms, parameters, trap table, redraw counts). It then appends TRUTH_H(world) = SHA-256 of the store's manifest to the campaign ledger, **before any arm starts that world**. Oracle grades are computed after all arms finish a world, and written to the sealed store.
- **Release.** M, the secrets and the truth stores are published at campaign close. Anyone can then regenerate every world and re-derive every grade.

### O.4 Canaries

`[DECISION]`
- Canary strings are 32-character values derived with purpose `canary`.
- They are planted in every sealed store (at least one per file), every truth-store record, the annex, the seed store and B-AUDIT.
- The scanner (TH) checks the §B.2 surfaces continuously. Any hit is a critical-leak event (§K.5).

### O.5 Protection against shopping and rerolls

1A §I.8 applies, adapted to Experiment 2's outcomes by the §L preservation rule and the §O.2 abort rule. In addition, **the world order, the interim block and the rerun subset are fixed by the evaluation ceremony**, so no one can choose which worlds count. `[DECISION]`

---

## P. Smallest credible implementation

All `[INFERENCE]`; nothing has been measured. The design optimises for the fastest experiment that can falsify the thesis.

### P.1 Build (engineer-weeks)

| Component | Weeks |
|---|---|
| Referee core retargeted to κ₂: claim validator and hasher, registry, as-of builder, B*, ridge learner, G1 with two Holm families, vault, ledger, receipts, evidence packages, release endpoint. Reuses the 1A lean-build design | 3 |
| Generator 𝒢₂, sealed annex, truth store, oracle, coverage ablation, harness replication, joint calibration | 2 |
| DSL: parser, type checker, canonicaliser, causal evaluator, B-EVAL packaging | 1.5 |
| Agent harness: ι₂ sandbox, least-privilege runner, tool wrappers, budget meters, model relay, record/replay, memory store, canary scanner | 2 |
| Arms A1, A2, ORC, ORC-A and A0; analysis code and blinding | 1 |
| MRS libraries: mutants, V-classes, conformance, oracle validation, screens, positive controls, the component map | 1.5 |
| **Tuning allowance (§B.4): S-SCR and S-AGT, 10 engineer-days each** | ≤ 4 |
| **Total** | **≈ 15 (14–17)** |

**The 1A lean build is not required on this path.** If the owner also wants it on κ_1A, 1A §K.1 estimates it at 3–4 engineer-weeks `[INFERENCE]`. Besides 𝒢_1A and its θ̃ oracle, it needs:
- the elastic-net quantile-regression learner with λ selection;
- G2 and its vault;
- FP-N;
- the PC-G2 screen;
- the AT1, AT2, AT3 and AT6 stand-ins.

Components shared with the κ₂ core (ledger, sandbox, registry, as-of builder) may reduce this by an amount that has not been estimated.

### P.2 Falsification-first staging

| Stage | When (from build start) | Work | Kill, void or gate point |
|---|---|---|---|
| **EK-B1** (no model calls) | Weeks 1–7 | Generator, oracle, DSL, referee core; MRS-11 (oracle validation against closed forms, trap design check and the §C.12 self-checks), passed before any calibration verdict or MRS-4N δ_c is computed; λ selected on the tuning worlds by B*'s blocked-CV loss and frozen (§C.11), before MRS-4 and MRS-5; ORC, A1 and A2 on the 40 EK-B1 development worlds (32 non-null, 8 null; in-family and null only); MRS-4, MRS-4N, the MRS-5 reachability check, MRS-5, MRS-5N; MRS-10; the out-of-family ORC-A and A1 check (stream `dev-oof`). Reported: A1's asserted clusters per world and pooled false-cluster ratio (the Appendix A.7 F2 planning values), the Q meter per arm, TRAP-SEL's selected t, and how many null expressions per world exceed discovery t 4.05 | **Calibration (all required):** ORC in-family coverage ≥ 0.80; headroom 0.8·E[J]·(ORC_cov − A1_cov) ≥ 2·MEI, i.e. ORC − A1 ≥ 0.25 at E[J] = 3; out-of-family (stream `dev-oof`): ORC-A coverage ≥ 0.5, and ORC-A − A1 coverage ≥ 0.25. **One** ledgered calibration amendment may change the generator prior (mechanism strength or J) only, before C2-eval (for an out-of-family failure, the annex's strength prior; the amended annex's SHA-256 is ledgered and shown to the owner before C2-eval); it is rerun on fresh development worlds. A second failure → **VOID-BENCHMARK** (redesign). **MRS-4 or MRS-4N fails** → a referee problem → stop for an owner decision. Expected ORC in-family coverage `[INFERENCE]`: about 0.91 including first-release attenuation and the HNG and REG forms (0.87–0.93 by type; Appendix A.4). **The headroom rule is the most likely calibration failure** (§I.3, §L) |
| Agent harness and MRS | Weeks 8–10 | Agent harness; MRS-1's same-machine determinism runs of the non-model arms; MRS-2 (including EV), MRS-3, MRS-6 to MRS-8 (MRS-11 is rerun here only if a mapped component changed, §B.3 item 4) | Any MRS item fails → stop for an owner decision (§B.3) |
| Tuning (parity) | Weeks 11–14 | S-SCR and S-AGT tuning on development indices 40–79, with parity (§B.4) | — |
| **Post-tuning calibration gate** | Week 15 | A1, A2, the brief, the A0 prompt and the agent code hashed into F_H(2-eval) (§B.4); the frozen, tuned A1 with ORC on fresh development worlds (stream `dev-cal`), and ORC-A with A1's out-of-family check on fresh `dev-oof` worlds (§C.9); A0 on 40 fresh `dev-cal` development worlds (§K.5 metadata-leak rule); MRS-1's model replay and MRS-9 on the code-freeze runner; reruns of any MRS items bound to changed components | Same calibration rules as EK-B1, using the single amendment if it is still unused. A failure may amend only the generator prior, never A1 or any other arm frozen in F_H(2-eval). A second failure → VOID-BENCHMARK. **The A0 metadata-leak rule (§K.5) is separate: one failure → VOID-BENCHMARK; no amendment applies** |
| **EK-B2** | About week 16 | C2-eval; the first 20 evaluation worlds for every arm | **KILL-FUTILITY** if the §K.7 rule fires: P = 0.29 under the default when the system is no better than A1 |
| Full run | Weeks 16–18 | The remaining evaluation worlds, the transfer probe, the reruns, the replay subset, attribution and analysis | §L |

**Elapsed time:** about 4–4.5 months from build start to the §L outcome, for one engineer working with separate Claude Code sessions, plus the owner's decision points.
- **The earliest design VOID** is at about week 7, with no model spend.
- **The earliest model-based kill** is EK-B2, at about week 16, after the MRS gate, tuning (≤ 2.4 × 10⁸ tokens) and EK-B2 (0.6–2.4 × 10⁸ tokens).

### P.3 Compute, tokens and wall-clock

**CPU** `[INFERENCE]`. C₀ is binding for every arm, so the scripted arms use their full budget.

| Item | CPU-h at N = 60 |
|---|---|
| A1 and A2 at C₀ on 75 evaluation worlds, plus A1 on the 12 probe worlds | ≈ 324 |
| The C-sweep (0.25× and 4×) on 20 worlds for A1 and A2 | ≈ 340 |
| Model arms: 339 world-runs, capped at 2 CPU-h each (expected about 0.5) | ≈ 170 (cap 678) |
| Development: EK-B1 and post-tuning A1/A2 runs; uncapped tuning runs of A1 and A2 | ≈ 240; ≤ 400 |
| MRS screens and mutants | ≈ 40 |
| Oracle grades and replication; coverage, including the §J.4 single-claim ablations (every positive claim × every planted mechanism × K paired draws under P and P^−j); joint calibration (§C.5: per generated world, (J_w + 1) terms × about 8 bisection steps × sweeps (≤ 20) × 20 fits with 5,000-day predictions). All measured at EK-B1 | ≈ 50 (range 20–100) |
| Inline controls (metered to the TH) | ≈ 100 |
| **Total** | **≈ 1,300–2,200 CPU-h** (≈ 1,700–2,200 if the A1/A2 tuning allowance is fully used) |

- **At N = 120,** the total is about 1,800–3,200 CPU-h (the oracle and inline-control rows scale with the number of world-runs).
- **Escalation** (§J.1) costs up to 8× per escalated item: about +350 CPU-h at the central oracle estimate if every item escalated, and up to about +700 at the row's upper end.
- Cost per CPU-hour is not estimated here.

**Model world-runs.** A3–A5 use 1–4 × 10⁶ input tokens each, and output is about 10% of input. MRS-1 reuses recorded tuning world-runs, so the MRS adds no tokens.

| Block | World-runs (N = 60) | Input tokens (N = 60) | Input tokens (N = 120) |
|---|---|---|---|
| Tuning (40 worlds; capped) | ≤ 60 | ≤ 2.4 × 10⁸ | ≤ 2.4 × 10⁸ |
| Evaluation, primary (75 or 150 worlds × 3 arms) | 225 | 2.3–9.0 × 10⁸ | 4.5–18 × 10⁸ |
| Transfer probe (12 × 2 model arms) | 24 | 0.2–1.0 × 10⁸ | 0.2–1.0 × 10⁸ |
| Rerun (15 × 2 arms) | 30 | 0.3–1.2 × 10⁸ | 0.3–1.2 × 10⁸ |
| A0 (evaluation + 40 development worlds) | 115 | ≤ 6 × 10⁶ | ≤ 1 × 10⁷ |
| **Total** | **≈ 454** | **≈ 3.4–13.6 × 10⁸** | **≈ 5.7–22.7 × 10⁸** |
| of which EK-B2 (20 × 3 arms) | 60 | 0.6–2.4 × 10⁸ | 0.6–2.4 × 10⁸ |

**Money cost** = tokens × the pinned snapshot's price on the run date. It is `[OPEN]` until owner decision 6.

**Wall-clock.** The A5 chain is strictly sequential (§I.4), so it sets the critical path:
- (N + ⌈N/4⌉ + 12) world-runs × 1–4 h, plus per-link closure and replication latency;
- about 3.6–14.5 days at N = 60, and about 6.8–27 days at N = 120.

The other arms (354 world-runs: A1–A4 on 75 worlds, A1 and A4 on the probe, and the reruns) run in parallel slots: about 1.8–7.4 days at 8 slots for N = 60, at 1–4 h per world-run.

---

## Q. Contradictions and deviations

### Q.1 Contradictions with Experiment 1A

Mirrored in 1A §L.1: CX-01 to CX-08 are CL-30 to CL-37; CX-09 is covered by CL-31; CX-10 is CL-39; CX-11 is CL-40; CX-12 is CL-41. 1A CL-38 mirrors deviation DV-01 (§Q.2).

| ID | Conflict | 1A reference | Resolution | Status |
|---|---|---|---|---|
| CX-01 | 1A gates Experiment 2 on REFEREE-VALID or VALID-WITH-SCOPE, and after two CAMPAIGN-VOIDs requires a new 1A pre-registration. Memo v2 §17 says "Exp 2 does not start" unless 1A passes | §H.1 (last bullet), §H.8 table; v2 §17 | The redefined Experiment 2 is gated by the MRS (§B.3). The 1A text is unchanged and now governs institutional use of certified guarantees (1A §H.8 v0.3 note) | **OPEN: decision 1** |
| CX-02 | 1A requires an LLM red team and a knowing-adversary arm in Experiment 2; 1A owner decision 8 and CL-29 defer the red team to Experiment 2 | §H.8, §E.5; 1A decision 8 | The redefined Experiment 2 has neither. Both move to the full-certification track. Gaming is measured as policy violations (S4). The 1A §A.5 caveat is unchanged | **OPEN: decision 1** |
| CX-03 | 1A limits Experiment 2 to 𝒢_1A and κ_1A (half-hourly, 5 quantiles) | §H.8 (ii), (iv); §C.10 | Experiment 2 uses 𝒢₂ and κ₂ (daily, squared error, ridge). No 1A certification transfers to κ₂; the MRS runs on κ₂ | Resolved (documented) |
| CX-04 | 1A offers G1, G2 and G3, and its minimum scope requires G2 or G3 | §H.2, §H.8 (i) | Experiment 2 uses G1 plus harness replication only | Resolved (documented) |
| CX-05 | 1A's G1 accepts m ≤ 4 hypotheses of form (candidate × T1–T5 × regime), spec version `1a-1` | §B.3, §D.1 | Experiment 2 uses DSL claims (spec version `2-1`): ≤ 4 positive and ≤ 2 negative, in two Holm families per vault use (per-vault error ≤ 0.10), with shifted nulls at δ_c | Resolved (documented) |
| CX-06 | 1A §H.8 (iii): researcher code needs a new sandbox certification | §H.8, D17 | Claims stay declarative. The model's exploratory code runs in a sandbox checked by conformance (MRS-9), not certified (§N, item 5) | Resolved (documented) |
| CX-07 | 1A's reopen rule refers to a certified referee | §H.8 | Experiment 2 defines an MRS reopen rule (§B.3); 1A's rule is unchanged | Resolved |
| CX-08 | Stale status: 1A §0.1 said "no commit, tag, push or pull request", and the 1A owner review said the draft was not committed | 1A §0.1; 1A owner review | 1A v0.3 adds a status note; the owner review is updated | Resolved |
| CX-09 | The LLM red team's destination: "Experiment 2" in 1A | 1A decision 8, CL-29 | Full institutional certification, by amendment (1A §E.5 unchanged) | **OPEN: decision 1** (with CX-02) |
| CX-10 | Neither 1A nor this benchmark exercises t0. 1A's learner is elastic-net quantile regression (LightGBM G not run); this benchmark's is ridge. The owner's clarified objective centres on t0's covariates | 1A §C.10, §A.4 item 7; Exp 2 §C.11 | §T recommends Experiment 2-T0 next. 1A certification stays a later objective, and would need a configuration with t0 as the learner to say anything about t0 | **OPEN: decisions 1 and 5** |
| CX-11 | The recommended Experiment 2-T0 runs discovery and both sealed segments on **real historical ODRÉ data (2021–2026)**. 1A §H.8 (iv) reserves real historical data until a real-data point-in-time validation (1B or a successor; CL-09) | 1A §H.8 (iv), CL-09 | **Substitutes:** Experiment 0's truncation and poisoning tests; the Part I.5 controls on the real ODRÉ vintages, including forecast-level controls; the forward recorder. **Proposed:** only the forward window after the tested claim batch's hash (the premise batch for Stage 4, the building batch for Stage 5) is ledgered and recorder go-live is verified (§T.2), and not before the researcher's knowledge vintage, earns credit as hindsight-free evidence | **OPEN: decision 1** |
| CX-12 | Truth estimand. 1A's G1 ground truth is the exact conditional skill of the fitted forecasts on the vault days used (1A §C.9: "exactly the estimand of the test's mean of batch means"; D3: "The referee tests fitted-forecast skill"). Experiment 2's truth is the expected pipeline skill over training draws and test days under P | 1A §C.9, D3; 1A decision 5 | Experiment 2 scores knowledge, not referee size. A 1A-style conditional grade is reported as secondary, and FDP is split into test error and estimand gap (§J.1, S2) | Resolved (documented) |

### Q.2 Deviations from the memo v2 roadmap, and accepted asymmetries

| ID | v2 or design element | Deviation | Reason | Approval |
|---|---|---|---|---|
| DV-01 | Exp 2 = autonomy; Exp 3 = knowledge accumulation | Experiment 2 includes the memory arm A5 and a 12-world transfer probe; Experiment 3 remains the accumulation test | The owner's arm list | Checklist |
| DV-02 | Exp 2 controls: a human-designed plan and a random-proposal agent | A1 (a strong scripted plan built without §C) and A2 (a grammar random search that exhausts DSL depth ≤ 1 within C₀ if an evaluation costs ≲ 0.2 CPU-s, with naive selection; §I.3), plus the A3 and A4 ablations | The owner's arm list | Checklist |
| DV-03 | Exp 2 measures honeypots, impossible tasks, gaming-attempt rates and capture–recapture | Null worlds and traps serve as honeypots and impossible tasks. Gaming attempts are counted by deterministic detectors (S4). **Capture–recapture is not included** | Smallest design | Checklist |
| DV-04 | Credit only from post-freeze synthetic worlds and live data after the knowledge vintage | Synthetic post-freeze worlds only; no live data | Scope; 1B is blocked | Checklist |
| DV-05 | Human gates: only a human unseals vaults | Vault closure is automatic after submission in the benchmark. No human acts during the campaign except in the ceremonies | Blinding and reproducibility | Checklist |
| DV-06 | v2's "Stage 0 checks" (not the 2-T0 Stage-0 metadata audit of §T.2), "knowing adversary" | Not included in this benchmark (CX-02) | — | Decision 1 |
| DV-07 | §20: "t0 is irrelevant to Exp 1" | Under the owner's clarification, t0 with covariates is the core of the research loop, and this benchmark's forecaster should become t0 (§T) | Owner clarification (rank 0) | Decisions 1 and 5 |
| DV-08 | Tuning parity (§B.4) | A1 and A2 may be rerun on the tuning worlds without a run cap, while A3–A5 tuning is capped at ≤ 60 model world-runs. This favours the control | A1 costs little to rerun; capping it would weaken the control | Checklist |

### Q.3 Interpretations of the owner instruction

These are recorded so that none is silent. `[DECISION]`
- **Arm list:** kept exactly (A1–A5). A0, ORC and ORC-A are validity arms, not comparators.
- **"Ablated controls"** in the kill rule is read as A3 (referee ablated) and A4 (memory ablated). Owner decision 2 may change the memory part.
- **Primary endpoint unit.** "True, replicated, non-duplicative claims" is counted as the number of distinct planted mechanisms covered by validated TRUE positive claims (TRK, §J.3). Counting mechanisms rather than claims means splitting, proxies and duplicates cannot raise the count.
- **"FDP ceiling"** is implemented as a ceiling on the per-world probability of any false validated discovery (mean Z, §J.4). This bounds FDR from above and is tested with an exact Clopper–Pearson bound (§K.4, F1). A per-world FDP ceiling of the form P(FDP > γ) ≤ α would need a different test and many more worlds. Mean FDP and mFDR are reported (S2).
- **Negative findings** are a secondary endpoint (S6), not part of the primary TRK. This keeps the primary endpoint split-proof and resistant to cheap negatives.
- **"Transfer to related unseen worlds"** is covered in Experiment 2 by the S7 probe only. The substantive test is Experiment 3.
- **Horizon and outcome** are fixed (1 day; one outcome per world) under κ₂. The schema fields are kept and validated, so extending them later needs only an amendment.

---

## R. Adversarial review log

### R.1 Adversarial design review

**The review.** v0.1-draft (as first drafted on 2026-09-23, including §0.7 and §T) went through a read-only adversarial design review, workflow `exp2-design-review-v2`.
- **Finders.** Eight finder agents covered sixteen lenses, in two finder rounds followed by a completeness critic:
  - the owner's ten areas: benchmark gaming, leakage, brute-force search, ground-truth validity, multiple testing, claim splitting, common-model bias, replication validity, memory contamination and compute feasibility;
  - six more: 1A consistency, cross-reference accuracy, stale status, owner compliance, statistics arithmetic, and the t0 alignment of §T.
- **Merging.** A merge agent removed duplicates across lenses and rounds.
- **Verification.** Each finding was adjudicated by three refuters with different lenses:
  - **text**: is the defect in the text?
  - **design**: is it a real flaw?
  - **fix**: would the fix break a requirement?
- **Confirmation rule.** A finding is confirmed if at least 2 of the 3 did not refute it.
- **An earlier run was stopped.** A first run of the same review (`exp2-design-review`) was stopped before any verification, because the owner's clarification changed the text under review. None of its output was used.

**Totals.** 156 findings, of which 148 were confirmed (37 must-fix, 79 should-fix, 32 nits) and 8 were rejected. R1-57 received only two votes, both confirming.

**Byte-identity check of the Experiment 1A pre-registration against `e9aa4cc`.**
- **Changed:** the header rows, the §0.1 status note, the added §H.8 v0.3 note (§H.8's original text is unchanged), §L.1 rows CL-30 to CL-41, §L.3, and the §N change log.
- **Byte-identical:** §A–§G, §H.1–§H.7, §I, §J, §K, §M and Appendices A–C (verified mechanically).

**Dispositions:**
- **Fixed:** the change was applied as proposed, or as corrected by the fix refuter.
- **Fixed (variant):** fixed differently from the proposal, with the reason given.
- **Fixed (completed after the fix check):** the first application was partial; the fix check (§R.2) gave the residual edit, which was then applied.
- **Carried to §T.4:** recorded as a binding requirement for the Experiment 2-T0 pre-registration.
- **Moot:** the rule it concerned was deleted by another fix.
- **Rejected:** fewer than 2 of 3 refuters confirmed it.

In the table, votes read "text/design/fix", with R = refuted, C = confirmed and – = no vote.

Lens codes: BG benchmark gaming; LK leakage; BF brute-force search; GT ground-truth validity; MT multiple testing and statistics; SA statistics arithmetic; CS claim splitting, duplicates and reformulation; CM common-model bias; RV replication validity; MC memory contamination; CF compute feasibility; 1A 1A consistency; XR cross-reference; SS stale status; OC owner compliance; T0 t0 alignment / Experiment 2-T0; CR completeness critic. Where: E2P = this document; E2O = `OWNER_REVIEW.md`; 1AP and 1AO (or E1AO, 1A OR) = the Experiment 1A pre-registration and owner review; d = decision.

| ID | Lens | Sev. | Votes | Defect (first sentence) | Disposition | Where |
|---|---|---|---|---|---|---|
| R1-01 | BG, GT, MT, OC, T0 | must | C/C/C | Comparator (b), the current best forecast, cannot be scored under the loss the document states. | Fixed (completed after the fix check) | E2P §T.2 'Comparators, losses and the claim test', Stage 5; §T.1 M-08 |
| R1-02 | BG, LK, GT, MT, CM, SA, T0 | must | C/C/C | The placebo size check is invalid, for six reasons. | Fixed (completed after the fix check) | E2P §T.2 K4 row, Controls ('real-data size check') |
| R1-03 | GT, CS, OC, T0 | must | C/R/C | Comparator (a), raw 't0 without X', lets a claim pass without any new information in X. | Fixed | E2P §T.2 Question, K1 row, leg (a); §T.1 M-02, M-08; 1A OR Part I.5 B-BASE |
| R1-04 | LK, RV, CF, 1A, OC, T0 | must | C/C/C | No stage says which ODRÉ vintage it uses for inputs and targets, or how known_at is set for historical rows. | Fixed | E2P §T.2 vintage table, custody, Timeline; §T.1 M-07; §T.4 item 1; 1A OR Part I.5 B-TGT, B-REG |
| R1-05 | RV, MT, CF, SA, T0 | must | C/C/C | The forward replication that the milestone depends on is underpowered and not specified. | Fixed (completed after the fix check) | E2P §T.2 Stages 3–4, Outcomes, Timeline; App. A.6; §T.4 items 5, 12 |
| R1-06 | OC, T0, LK, RV, CF | must | C/C/C | The timing of the milestone is misstated and 'the freeze' is undefined. | Fixed (completed after the fix check) | E2P §T.2 Stage 3, Stage 4 'Window', Timeline, Custody; E2P CX-11; 1A CL-40 |
| R1-07 | LK, 1A, OC, T0 | must | C/C/C | The Part I.5 subset keeps mutants whose designated detecting controls it drops, and it leaves out controls that 2-T0's own design makes relevant. | Fixed | 1A OR Part I.5 rows B-ASOF, R3, R6, gate table, Cost; 1A OR Scope estimates (2-T0 subset 2.5 wk) |
| R1-08 | 1A, OC | must | C/C/C | Part I.5 misstates what the 2-T0 subset guarantees. | Fixed (completed after the fix check) | 1A OR header bullet (Part I 'required before the Experiment 2 benchmark'), Part I heading, … |
| R1-09 | OC | must | C/C/C | NO-FINDING is labelled 'a valid null', but nothing mandatory shows that the t0 covariate path can detect a real effect, because the known-answer … | Fixed (completed after the fix check) | E2P §T.2 Controls (known-answer gate), Outcomes (INVALID, NO-FINDING) |
| R1-10 | 1A, OC | must | C/C/C | A contradiction with 1A is not logged. | Fixed | 1A PREREG §L.1 CL-40, §H.8 v0.3 note items 5–6, header, §0.1, §L.3, §N |
| R1-11 | XR, OC, T0 | must | C/R/C | The adversarial review log that owner deliverable 12 requires is an empty placeholder. | Fixed | E2P §R (prose, byte-identity block, areas table; table placeholder excluded); §S change log |
| R1-12 | 1A | must | C/C/C | The owner review lets the MRS stand in for the 1A lean build as the precondition for the full certification campaign. | Fixed | 1A OR Part II Recommendation ('Authorize the full certification campaign separately') |
| R1-13 | SS, OC | must | C/C/C | One checklist item would let approval of 1A authorize implementation of the MRS path. | Fixed | 1A OR Part II Approval checklist |
| R1-14 | OC | must | C/C/C | Wrong cross-reference. | Fixed | E2P §K.4 header; E2O d4 |
| R1-15 | BF, CF | must | C/C/C | Arithmetic error: | Fixed | E2P §H (Q is a reported meter, C₀ binding), §I.2 A1, §I.3, §D.3, §P.3, S10; E2O d9 |
| R1-16 | BF | must | C/C/C | The in-family hypothesis space is small enough to enumerate within budget. | Fixed (completed after the fix check) | E2P §B.4 (S-SCR row, artefact audit, freeze), §I.2 A1, §I.3, §O.2 F_H(2-eval); E2O d9 |
| R1-17 | BF | must | C/C/C | Trial budgets are not comparable across arms, which violates the owner's requirement of fixed, comparable trial budgets. | Fixed | E2P §B.1 B-EVAL, §B.2 mount, §B.4 S-REF, §D.3, §H (C₀ binding, Q reported, Self-written … |
| R1-18 | BG, RV | must | C/C/C | TRK credits A3 through one filter (replication) and the referee arms through two (Holm confirmation and replication). | Fixed | E2P §G.2 A3 paragraph, §G.5 condition 2 and Labels, §I.3, §K.2 S11, App B TRK_A3_credit; E2O d8 |
| R1-19 | BG | must | C/C/C | Whether a critical leak or a replay mismatch is attributed to the SUT (KILL-LEAK / KILL-REPRO) or to the TH (VOID-BENCHMARK, fixed and rerun on fresh … | Fixed (completed after the fix check) | E2P §K.5 Attribution map, §K.8, §B.3 reopen rule, §L preservation, App. B |
| R1-20 | BG, CM | must | C/C/C | The rule against revealing §C constrains only the brief text. | Fixed | E2P §B.4 S-AGT row, Artefact audit, Freeze; §C.8; App C header and A0 template; §O.2 F_H(2-eval) |
| R1-21 | LK, GT | must | C/C/C | TRAP-LAG's point-in-time value can be predictive given B*, which contradicts its stated truth. | Fixed (completed after the fix check) | E2P §C.0 lag row, §C.6 truth rule + TRAP-LAG/TRAP-RED rows + trap redraw, §C.10 (D1, D2 at 8 … |
| R1-22 | GT | must | C/C/C | The coverage test differences two ratio skills that have different denominators, E_P[ℓ(B*)] and E_{P^−j}[ℓ(B*)]. | Fixed (completed after the fix check): ORC coverage re-derived with the HNG and REG forms (≈ 0.91); escalation while INDETERMINATE added | E2P §J.3 coverage statistic and classification, §B.3 MRS-11, App. A.4, §P.2 EK-B1 cell, §L |
| R1-23 | CS | must | C/C/C | Clusters are built from the correlation of full M_c forecasts, which are dominated by the shared B* component. | Fixed (completed after the fix check) | E2P §J.4 Clusters steps 1–5, §E.4 NEAR_DUPLICATE, §G.6 padding row, §J.6; §P.3 (missing) |
| R1-24 | MT | must | C/C/C | F1 and F2 put Student-t bounds on means of bounded, zero-inflated FDP values. | Fixed (variant): one exact Clopper–Pearson bound on the per-world indicator Z | E2P §K.4 (F1, F1-kill, 'Why a world indicator for F1'), §J.4 (Z, FDR ≤ mean Z), §Q.3, §K.3 … |
| R1-25 | MT | must | C/C/C | F2 compares means of FDP_w over all worlds, with FDP_w = 0 whenever R = 0. | Fixed (completed after the fix check): F2 redesigned as estimate ≤ 0.05 and UB₉₅ ≤ 0.10, with a sparse rule, a small-count bound and Appendix A.7 operating characteristics | E2P §J.4 mFDR, §K.4 F2 / F2 sparse / F2-kill, §K.3 kill-route table, App. B |
| R1-26 | MT | must | C/C/C | The inverse-normal extension re-applies the full-level stage-1 boundaries to the combined statistic. | Fixed | E2P §K.7 'No extension', §L rule 7, App. B 'AMBIGUOUS: otherwise |
| R1-27 | MT, SA | must | C/C/C | §K.3 says the probability of a wrongful KILL is ≤ 0.05 when every Δ_c = MEI. | Fixed | E2P §K.3 (fails(c) '≤ 0.05' restricted to the four TRK tests |
| R1-28 | MT | must | C/C/C | MRS-4 screens G1's size only on null worlds, where every claim has θ ≤ 0. | Fixed (completed after the fix check) | E2P §B.3 MRS-4, MRS-5; 1A OR I.2 MRS-4/MRS-4N rows, I.3 P2, P3 |
| R1-29 | MC, CF, SA | must | C/C/C | No rule says A5's world i may start only after world i−1 has closed, its replication verdict has been released and its memory has been written. | Fixed | E2P §I.4 Order and state, §I.6, §K.6, §P.3 Wall-clock, §P.2 Full run row |
| R1-30 | MC | must | C/C/C | Two rules in the Experiment 3 sketch leak ground truth about which mechanisms changed, so the false-import test becomes uninterpretable. | Fixed | E2P §M Lineages ('Same catalogue', 'Hidden change points'), Guards; §C.2 Identifiers; §K.2 S7 |
| R1-31 | LK, RV, MT, CM, T0 | should | C/C/C | The building investigation (Stage 4) has internal contradictions and a sealed-data exposure. | Fixed (variant, completed after the fix check): building claims are scored only on forward days after their own claim-batch hash, over the same fixed length | E2P §T.2 Stage 5 (building investigation), Outcomes; E2O |
| R1-32 | MT, T0 | should | C/R/C | The 2-T0 outcome table leaves cases unmapped. | Fixed (variant): per-claim outcomes with a run-level rule, and a fixed-horizon forward test instead of a sequential stop | E2P §T.2 Outcomes, Stage 3–4; §T.4 item 2; E2O 'Outcomes of Experiment 2-T0' |
| R1-33 | LK, RV, CM, OC, T0 | should | C/C/C | The sealed segments may not be independent of the forecaster or of the researcher. | Fixed (completed after the fix check) | E2P §T.2 Forecaster, Claim boundaries; §0.6 glossary; §T.4 items 2–3 |
| R1-34 | BF, OC, T0 | should | C/C/C | Experiment 2-T0 has no scripted or exhaustive-screen control. | Fixed (completed after the fix check) | E2P §T.2 Claim boundaries (last bullet); §T.4 item 4 |
| R1-35 | OC, RV, T0 | should | C/C/C | The owner's milestone is an 'independently confirmed' finding, but §T.2 never says what 'independent' means. | Fixed | E2P §T.2 Claim boundaries; §N item 13; E2O decision 5 (§N item 13), decision 10 (§N item 12) |
| R1-36 | LK, T0 | should | C/C/C | The known-future rule covers only horizon values, but t0 standardises a known-future covariate over the whole span 1:T+H and reads it bidirectionally. | Fixed | 1A OR Part I.5 rows B-REG and R3; Exp 2 §T.2 catalogue K3 (and K1); §T.1 M-02 |
| R1-37 | LK, T0 | should | C/C/C | The point-in-time controls check t0's input arrays, not its forecasts, so a leak created inside the t0 call passes them. | Fixed | 1A OR Part I.5 rows B-ASOF (forecast-level controls) and R3; gate table; Exp 2 §T.2 Controls |
| R1-38 | 1A, CF | should | C/C/C | Part I.5 carries over 1A pass rules whose trial units are synthetic worlds, while also saying that no generator or world seeds are needed. | Fixed | 1A OR Part I.5 'Real-data trial units' block, rows R3, R5.G1, B-SEED; gate table |
| R1-39 | 1A | should | C/C/C | The table claims to map every 1A element but leaves out several that 2-T0 relies on: | Fixed | 1A OR Part I.5 table (intro 'maps the main 1A elements' |
| R1-40 | T0 | should | C/R/C | 2-T0 is said to be 'gated by' the Part I.5 subset, but Part I.5 is a component mapping, not a gate. | Fixed | 1A OR Part I.5 'Gate for Experiment 2-T0' table plus stop, binding and reopen rules |
| R1-41 | T0 | should | C/C/C | The steps are in the wrong order. | Fixed (completed after the fix check) | E2P §T.2 Covariate catalogue (Order, Stage-0 audit limits, no-audit fallback), Timeline |
| R1-42 | CF | should | C/C/C | The 2-T0 cost estimate is incomplete and its arithmetic is off. | Fixed (completed after the fix check) | E2P §T.2 Estimate, Timeline, Stage 1; §T.4 item 6; E2O decision 1, scope row; 1A OR Part I.5 Cost |
| R1-43 | CF, T0 | should | C/R/C | The cross-runner difference used to size the 2-T0 determinism tolerance is the smaller of two figures in Experiment 0. | Fixed | E2P §T.1 M-06; §T.4 item 7; 1A OR Part I.5 R7 row and gate |
| R1-44 | XR, OC, T0 | should | C/C/C | CL-39 is OPEN pending Exp 2 decisions 1 and 5, but the checklist and the next prompt route only CL-30 and CL-31 to the Experiment 2 decisions, so … | Fixed | 1A OR Part II Approval checklist |
| R1-45 | BG | should | C/C/C | The A1 ceiling (VOID if A1 covers more than 0.70) is calibrated at EK-B1 on an untuned A1. | Fixed (variant): a post-tuning calibration gate on held-out development worlds | E2P §P.2 post-tuning calibration gate row (week 15, dev-cal), §O.1 C2-dev purposes, §0.1, §B.4 … |
| R1-46 | BG | should | C/C/C | Two things about the tuning worlds are unspecified: | Fixed (completed after the fix check) | E2P §B.4 Tuning parity; §P.2 EK-B1 and tuning rows; §Q.2 DV-08; E2O d9 |
| R1-47 | BF | should | C/C/C | The attractiveness bar for a useful negative (discovery t ≥ 2.5) sits below the expected maximum null t of any screen. | Fixed (completed after the fix check): "attractive" defined (θ̂_disc ≥ δ_min, t ≥ 2.5); useful negatives keep t ≥ 4.05 as a fixed convention | E2P §G.5 useful negative, §G.6 'Harvesting cheap negatives', §K.2 S6; §B.3 MRS-10 |
| R1-48 | RV, CS | should | C/R/C | A negative claim is graded TRUE-NEG against its own δ_c, which can be as large as 0.20, and 'attractive' requires only θ̂_disc ≥ δ_c. | Fixed (variant, completed after the fix check): two-tier attractive / useful rule; negative claims join the §J.4 clusters | E2P §G.5 useful negative, §G.6 cheap-negatives row, §I.4 kinds, §K.2 S6, §M guards |
| R1-49 | BF | should | C/C/C | A2's sampling distribution ('uniformly from the depth-≤3 grammar') is not defined and is left to S-SCR. | Fixed (variant, completed after the fix check): A2's sampler is specified in §I.2, and A2 is characterised as an enumerator of DSL depth ≤ 1 with naive selection (§I.3); the residual "floor control" text was not applied | E2P §I.2 A2, §I.3, §K.7 blind re-estimation |
| R1-50 | MC | should | C/C/C | The memory cap fills partway through the campaign, and no eviction rule is given. | Fixed (completed after the fix check) | E2P §H Memory row; §I.4 Order and state (Overflow, Snapshots); §K.2 S8 |
| R1-51 | MC | should | C/C/C | The memory state for A5's reruns is not specified. | Fixed | E2P §I.4 'Snapshots' and 'Reruns' bullets; §K.5 critical-leak list; §K.6 |
| R1-52 | MC, CS | should | R/R/C | The document does not say whether sibling worlds get fresh innovations. | Rejected (text, design): probe siblings use their own `xfer` seed stream, so their innovations are fresh; the common-random-number rule applies only within the oracle's ablation | — |
| R1-53 | MC | should | C/R/C | A5-placebo gets memory from a different lineage, and that memory names series IDs that do not exist in the current lineage. | Fixed | E2P §M 'The A5-placebo memory' |
| R1-54 | MC | should | C/C/C | Both false-import metrics count only wrongly imported positive conclusions. | Fixed (completed after the fix check) | E2P §K.2 S7; §M controlled edit 5 'negative reversal' and Metrics |
| R1-55 | GT | should | C/C/C | The TRAP-BRK driver is a non-binary series, so it receives a factor loading. | Fixed | E2P §C.0 (factor-loading row 'non-binary, non-trap series' |
| R1-56 | GT, CF | should | C/C/C | The mechanism calibration is ill-posed and its self-check cannot be met. | Fixed (completed after the fix check) | E2P §C.5 joint calibration, §C.6 TRAP-BRK, §C.12, §P.3 CPU table |
| R1-57 | GT | should | –/C/C | Binary series are non-trap series, so each is revised with probability 0.5. | Fixed | E2P §C.0 revisions row + binary row, §C.3, §C.5 discoverability, §E.1 pred |
| R1-58 | GT | should | C/C/C | MRS-11 applies a 3-sigma tolerance to each of about 60 claims with no multiplicity control, and s_o is estimated from K draws. | Fixed | E2P §B.3 MRS-11 in full; §J.1 closed-form validation |
| R1-59 | CS | should | C/C/C | S1 precision is computed per claim, whereas FDP is computed per harness cluster. | Fixed | E2P §K.2 S1 (mechanism precision); §G.6 claim-splitting row; §J.4 attribution |
| R1-60 | MT | should | C/C/C | σ_Δ is re-estimated over all 40 EK-B1 development worlds, including 8 null worlds where TRK is 0 for every arm and Δ ≡ 0. | Fixed | E2P §K.7 'Blind re-estimation' and 'Guarantee' bullet; §P.2 EK-B1 row |
| R1-61 | MT | should | C/C/C | The primary t-bounds treat the Δ_{c,w} as independent across worlds. | Fixed (completed after the fix check) | E2P §K.3 (SE=max(iid, Newey–West lag 4 Bartlett) for every A5 statistic |
| R1-62 | MT | should | C/C/C | Three rules treat a SUT-attributed critical leak differently. | Fixed (completed after the fix check) | E2P §K.5 'One rule for KILL-LEAK'; §L rule 2; App. B KILL_LEAK; §K.1 INVALID handling and cap |
| R1-63 | MT | should | C/C/C | Under the recommended decision-2 alternative, A4 is tested only for non-inferiority (LB₉₅ > −MEI), so a CONTINUE is compatible with A5 being worse … | Fixed (completed after the fix check) | E2P §A.2 H1, §L 'Meaning of each outcome', §N opening; E2O one-page CONTINUE and KILL bullets |
| R1-64 | MT | should | C/C/C | §A.3 says Experiment 2 can establish which component produces a difference (search, referee, memory). | Fixed | E2P §A.2 H3, §A.3 |
| R1-65 | CF | should | C/C/C | The inline controls, including the new per-origin DSL-causality check DC, are to run on 'every operator in an evaluated expression' in every referee … | Fixed (completed after the fix check) | E2P §B.3 inline-controls paragraph and MRS-2; §H C₀ row; §I.3; §O.3 `inline` |
| R1-66 | CF, SA | should | R/R/C | The CPU estimates state no unit costs and leave out major items: | Rejected (text, design): the items fall under §P.3's labelled aggregate; §P.3 was re-estimated anyway (R1-68, R2-29 and the fix check) | — |
| R1-67 | CF, SA, T0 | should | C/C/C | The cost of recommended decision 5 (t0 as the benchmark's forecaster) is understated. | Fixed (completed after the fix check) | E2P §T.3 'Cost of that adaptation'; E2O decision 5 |
| R1-68 | CF | should | C/C/C | The ≈ 11 engineer-week build omits §B.4's tuning allowance (2 × 10 engineer-days = 4 engineer-weeks). | Fixed | E2P §P.1 (tuning row ≤ 4 |
| R1-69 | CM | should | C/R/C | Model separation covers only S-GEN's code, and only 'where one is available'. | Fixed (completed after the fix check) | E2P §C.9 content, §B.4 model separation, §N item 12, §T.3; E2O d5, d10 |
| R1-70 | CM | should | C/C/C | Contrary to the text, A0 cannot detect prior knowledge of the family. | Fixed (completed after the fix check) | E2P §I.2 A0, §K.5 Contamination check, §N item 12, S9; E2O d10 |
| R1-71 | SA | should | C/C/C | The justification for using z instead of t is false at the 98.75% quantile. | Fixed | E2P App. A method line, A.1, A.5, §K.7 OC table and bullets; E2O d2, d3 |
| R1-72 | OC | should | C/R/C | The one-page kill and void summary uses vague, unthresholded words where the pre-registration has exact rules. | Fixed | E2O 'Kill, continue and void for this benchmark, in one page' |
| R1-73 | OC | should | C/C/C | The gate is circular. | Fixed | E2P §0.1 'Two gates follow' |
| R1-74 | OC | should | C/C/C | §Q.3 promises that no interpretation is left silent, but two material interpretations of the primary endpoint are missing. | Fixed (variant): the FDP ceiling is a ceiling on mean Z, tested by exact Clopper–Pearson | E2P §Q.3 bullets 'Primary endpoint unit' and 'FDP ceiling'; §K.2 S2 |
| R1-75 | GT | nit | C/R/C | The oracle fits M_c and B* on fresh draws from the forward law P, but the pipeline fits them on days 365–1,459, which follow the discovery-period law. | Fixed | E2P §J.1 Estimand, 'What truth means', 'Where delivered skill can differ' [ASSUMPTION] |
| R1-76 | CS | nit | C/C/C | `information_set` is a list, and JCS canonicalises object keys but not array order. | Fixed | E2P §F information_set row |
| R1-77 | XR | nit | C/C/C | The claim of one-to-one mirroring is wrong. | Fixed | E2P §Q.1 intro |
| R1-78 | XR | nit | C/R/C | CL-35 cites Experiment 2 §N as where the researcher-code sandbox is documented as uncertified, but none of §N's twelve items covers the sandbox. | Fixed | 1A PREREG §L.1 CL-35; Exp 2 §N item 5 |
| R1-79 | SS | nit | C/C/C | 'Unchanged in substance from v0.2, except decision 8' understates the v0.3 edits to Part II. | Fixed (completed after the fix check) | 1A OR header bullet (line 9) and Part II introduction |
| R1-80 | XR | nit | C/R/C | The two documents number the same owner clarification differently. | Fixed | 1A PREREG §0.1 status note; Exp 2 §0.3 ranks 0–1, §0.7; 1A OR 'Your later clarification' |
| R1-81 | 1A, OC | nit | C/C/C | V13 gets a third meaning. | Fixed | 1A OR Part I.5 row R6 |
| R1-82 | XR | nit | C/C/C | The extra effort quoted for adding the 1A lean build does not match 1A §K.1. | Fixed | E2P §P.1 note under the build table |
| R1-83 | 1A | nit | C/R/C | Decision 8's recommendation (move the red team to the full-certification track) is unconditional, but it holds only if Exp 2 decision 1 is approved. | Fixed | 1A OR decision 8 row; Part II intro bullet |
| R1-84 | 1A | nit | C/C/C | LK11 is left out of MRS-3 on the grounds that DA covers it inline. | Fixed | E2P §B.3 MRS-3 κ₂ table (LK11 → DA, λ table) and Not-in-MRS list |
| R1-85 | SA | nit | C/C/C | Counting error: | Fixed | E2P §K.7 Default N; §K.6; §P.3 |
| R1-86 | SA | nit | C/C/C | Inconsistent rounding. | Fixed | E2P App A.1 |
| R1-87 | SA | nit | C/C/C | The null-series range of 19–25 holds only for non-null worlds. | Fixed | E2P §C.0 (phantom-driver row, proxies row), §C.2, §C.6 phantom note, §C.7 null row |
| R1-88 | OC | nit | C/R/C | A statement of fact is labelled [DECISION], which §0.2 defines as a pre-registered choice that needs an amendment to change. | Fixed | E2P §0.7 |
| R1-89 | T0 | nit | C/C/C | K1 credits `solarbench/astro.py` with clear-sky proxies it does not contain; | Fixed | E2P §T.2 K1 and K2 rows; 1A OR Part I.5 B-REG exemption |
| R2-01 | BG, 1A | must | C/C/C | Voids can be used as rerolls. | Fixed (completed after the fix check) | E2P §L preservation rule, rules table, calibration and second-VOID paragraphs; App B |
| R2-02 | LK | must | C/C/C | The 'revised' metadata flag partly reveals which series are traps, although §C.8 requires trap identities to stay hidden. | Fixed (completed after the fix check) | E2P §C.0 revisions row, §C.6 TRAP-REV (R ∈ {7,30}) and TRAP-SEL (first-release selection), … |
| R2-03 | LK | must | C/R/C | The 2-T0 seal has no custody rule. | Fixed | E2P §T.2 'Custody of the sealed segments', Stage-0 audit limits, K4/Controls |
| R2-04 | MC | must | C/C/C | 'Permuted IDs' can be read as one fixed label set reshuffled in each world, and nothing requires IDs to be unique across worlds. | Fixed | E2P §C.2 identifiers, §C.12 first self-check, §I.4 transfer content, §O.3 purposes … |
| R2-05 | 1A | must | C/C/C | MRS-3 imports 1A leak mutants 'retargeted to κ₂' but pre-registers neither κ₂ magnitudes nor a κ₂ trial definition, and some mutants can never be … | Fixed (completed after the fix check) | E2P §B.3 MRS-3 κ₂ table, trial definition, 'Moved to Not in the MRS', Not-in-MRS list |
| R2-06 | BF | should | C/C/C | The coverage threshold ½·θ_solo does not require the nonlinear or regime-dependent form the owner asked for. | Fixed (completed after the fix check): τ_j for annex mechanisms; HNG and REG in App. A.4 | E2P §J.3 Threshold τ_j and classification, S1, App. A.4 |
| R2-07 | GT, BF | should | C/C/C | Coverage is the unit of the primary endpoint TRK, but the coverage decision has no control of Monte Carlo error. | Fixed | E2P §J.3 coverage statistic, Escalation, Classification |
| R2-08 | BF | should | C/C/C | The calibration band accepts benchmarks whose in-family headroom over the scripted plan is below MEI. | Fixed (completed after the fix check) | E2P §P.2 EK-B1 + post-tuning rows, §B.4 freeze (A1 hashed before the gate), §K.3 MEI (decision … |
| R2-09 | GT, BF | should | C/C/C | Out-of-family worlds have no strength calibration, no discoverability requirement, no ORC ceiling and no A1 ceiling, and the annex stays sealed until … | Fixed (completed after the fix check) | E2P §C.9 (content, calibration), §P.2 EK-B1 + post-tuning rows, §O.1/§O.3 (dev-oof), §K.2 S9, … |
| R2-10 | BG | should | C/C/C | 'Harness error' is never defined, and the design does not say how an errored world-run enters the paired analysis. | Fixed (completed after the fix check) | E2P §C.12 harness-error definition, §K.2 S4, §L preservation rule + rule 1, App B; E2O one-page |
| R2-11 | BG | should | C/C/C | The documents contradict each other on who writes the A0 probe, and A0's prompt is unconstrained, although A0's AUC can void the campaign. | Fixed (variant, completed after the fix check): malformed A0 output is a model-behaviour failure, not a harness error | E2P §B.4 S-GEN/S-AGT rows and Freeze; §I.2 A0; App C header, A0 template and Arm differences |
| R2-12 | LK | should | C/R/C | The forward recorder is specified only as storing 'the real-time vintage'. | Fixed | E2P §T.2 Stage 4 'Recorder' bullet, K3 row, catalogue order; §T.4 #11 |
| R2-13 | LK | should | R/R/C | No rule says which sealed segment a follow-up attempt uses after NO-FINDING or NOT-REPLICATED. | Rejected (text, design): a consumed vault is exploratory only (1A §D.1, via Part I.5), and a new catalogue needs a new sealed segment (§T.2 NO-FINDING) | — |
| R2-14 | LK | should | C/C/C | The agent runner and the tool wrappers run as part of the TH, the principal trusted with ground truth. | Fixed | E2P §B.1 runner principal; §B.2 Conformance |
| R2-15 | MC | should | C/C/C | Memory writes carry no validity condition. | Fixed | E2P §I.4 Validity of writes; §B.3 MRS reopen rule (before campaign close) |
| R2-16 | MC | should | C/R/C | A5's memory notes are written by the model after closure, once the replication verdict has been released. | Fixed | E2P §H T₀ row and Cost bullet; §I.3 Same budget and Memory ablation; §I.4 PROCEDURAL_NOTE; E2O d6 |
| R2-17 | MC, MT | should | C/C/C | The extension (C2-ext) leaves A5's starting memory unspecified. | Moot: the §K.7 extension was deleted (R1-26) | E2P §K.7 'No extension'; §L rule 7; App. B |
| R2-18 | MC, MT | should | C/C/C | The operating characteristics of the binding futility rule assume that Δ_{A1,w} has the same mean in every world. | Fixed | E2P §K.7 interim futility and OC table (linear learning curves), App. A.2, §P.2 EK-B2 row; E2O d3 |
| R2-19 | MC | should | C/R/C | The Experiment 3 false-import metric does not isolate importing. | Fixed | E2P §M Trap-transfer worlds, Lineages edit 6, Metrics; §K.2 S7 |
| R2-20 | MC | should | R/R/C | 'Never in memory: | Rejected (text, design): memory is defined by provenance; "never in memory" means hidden harness quantities, not the model's own inference | — |
| R2-21 | RV, MT | should | C/R/C | The forward window has a minimum length but no fixed end ('at least 90 delivery days'), and Part I.5 allows a fixed-horizon test. | Fixed (completed after the fix check): the forward-window length is a referee-owned constant, powered at the confirmation-1 effect | E2P §T.2 Stage 4 'Length'/'Single look'; §T.4 #1, #12; E1AO Part I.5 G3 row |
| R2-22 | GT | should | C/C/C | MRS-11 validates the oracle only on true-mechanism claims in LIN-only worlds, so only bare atoms S(driver, asof) are ever checked. | Fixed (completed after the fix check) | E2P §B.3 MRS-11 in full; §J.1; 1A OR I.2 MRS-11 row, I.3 P7 |
| R2-23 | GT | should | C/C/C | The document never says whether the oracle, the coverage ablation and the harness replication (written by S-GEN) reuse the referee's B-DSL, B-ASOF … | Fixed | E2P §B.1 TH list, §B.3 purpose and paragraph, §E.3, §G.4, §J.1, §N item 5 |
| R2-24 | GT | should | C/R/C | An unlogged contradiction with 1A on the truth estimand. | Fixed | E2P §J.1 'Difference from 1A's estimand', §Q.1 CX-12 and mapping line, S2, §K.4 'What F1 and … |
| R2-25 | MT | should | C/R/C | The negative G1 family (H0: | Fixed | E2P §B.3 MRS-4N, MRS-5N; §P.2 EK-B1; §K.2 S2; §K.4 'Validity of negatives'; E2O d4 |
| R2-26 | CS | should | C/R/C | §T.3 lends the §F claim schema and the §G.6 anti-splitting and anti-reformulation controls to 2-T0, but neither can work there. | Carried to §T.4 (item 1) | E2P §T.4 #1 (R2-26); §T.3 'What transfers'; E1AO Part I.5 B-SPEC row |
| R2-27 | MT, OC | should | C/R/C | Experiment 2-T0 has no negative-claim family, so it can never produce a validated negative finding. | Fixed | E2P §T.2 Outcomes NO-FINDING row and following sentence; §T.4 #2, #8 |
| R2-28 | CS | should | C/R/C | Clusters are defined by a pairwise threshold that is not transitive, with no linkage rule. | Fixed | E2P §J.4 Clusters (step 4, 'computed separately on each level's claim set', Diagnostic) |
| R2-29 | CF | should | C/C/C | The token and wall-clock totals are computed only at the default N = 60. | Fixed (completed after the fix check) | E2P §P.3 (token table N = 120 column, CPU at N = 120, wall-clock at N = 120); E2O d6 |
| R2-30 | CM | should | R/R/C | The only mitigation offered for t0 having been pretrained on covariate-effect generators is a check that cannot be done from public material. | Rejected (text, design): M-04 already states the consequence, and a family-level overlap check is feasible from the paper | — |
| R2-31 | CM | should | C/R/C | The annex changes only mechanisms and one law. | Fixed | E2P §C.9 'Purpose and limit' + 'Design extension', §C.7 default, §N item 12; E2O d7 |
| R2-32 | CM | should | C/R/C | The owner review defers decisions 6 (the researcher's model snapshot and knowledge vintage) and 10 (mitigation of common-model bias) as relevant … | Fixed | E2O deferral paragraph, 'Choices for the 2-T0 pre-registration', next prompt |
| R2-33 | CF | should | C/R/C | The owner's immediate milestone has two parts: | Fixed (variant, completed after the fix check): grades relabelled "first finding"; the milestone completes when a building claim is scored | E2P §T.2 Stage 5, Timeline, Outcomes |
| R2-34 | 1A | should | C/C/C | MRS-7 keeps V6, but in 1A V6 is detected only by the recorder cross-check RC, and RC does not exist in κ₂. | Fixed | E2P §C.3 row schema, §D.2, §0.6, §B.1 B-REG, §D.3 raw(); §B.3 MRS-7 and Not-in-MRS (V6) |
| R2-35 | 1A, OC, T0 | should | C/C/C | Part I.5 lists G3 as an optional part of the 2-T0 subset. | Fixed | 1A OR Part I.5 row G3 and (e)/N3; Exp 2 OR contradiction 4; Exp 2 §T.4 #12 |
| R2-36 | 1A | should | C/R/C | Custody of seeds and commitments for both Experiment 2 and 2-T0 is routed to 1A decision 7, yet the recommended path tells the owner the 1A decisions … | Fixed | 1A OR Part II Recommendation (decision 7 exception), decision 7 row, checklist, Part I.5 B-SEED |
| R2-37 | 1A, OC | should | C/C/C | On the recommended path the owner answers only Exp 2 decisions 1 and 5 and defers the 1A decisions. | Fixed | E2O Next Claude Code prompt |
| R2-38 | OC | should | C/C/C | Decision 5's stated consequences cover cost, leak mutants and pretraining overlap, but not that the benchmark's ground-truth machinery is defined for … | Fixed | E2O decision 5 'Consequence'; E2P §T.3 'Recommended adaptation' |
| R2-39 | OC | should | R/R/C | A mismatch with the clarified objective is not flagged. | Rejected (text, design): §I.3, §N item 7 and M-04 already state that the benchmark tests blind search | — |
| R2-40 | OC, T0 | should | C/R/C | Part II was not brought into line with the clarification. | Fixed | 1A OR decision 1 alternatives ('Defer until a t0 configuration is drafted'), Part II … |
| R2-41 | OC, T0 | should | C/R/C | The choice between t0-alpha and t0-beta is labelled an 'owner decision', but it has no route: | Fixed (variant): the t0 variant is a choice for the 2-T0 pre-registration (§T.4 item 2), not an 11th decision | E2P §T.2 Forecaster; §T.4 #2 (R2-41); E2O 'Choices for the Experiment 2-T0 pre-registration' |
| R2-42 | T0 | should | C/C/C | The list of referee-owned t0 settings leaves out inputs that change t0's forecasts, so a claim's result can depend on how the call is built. | Fixed | 1A OR Part I.5 rows B-SPEC and B-ASOF (batch-composition invariance, role conformance) |
| R2-43 | T0 | should | C/C/C | The daily loss for the G1 test is not defined, and Experiment 0 showed that its definition decides the result for t0. | Fixed (completed after the fix check) | E2P §T.2 'Comparators, losses and the claim test'; §T.4 #2; E2O 2-T0 choices |
| R2-44 | MC | nit | C/R/C | VALIDATED_POSITIVE and VALIDATED_NEGATIVE items are written when each world-run closes. | Fixed | E2P §G.5 Labels and condition 5, §I.4, §K.5 Reproducibility |
| R2-45 | LK, RV | nit | C/R/C | 2-T0's segments run back to back with no embargo: | Fixed | E2P §T.2 Stages 2–3 and vintage table (segments start 2025-01-15 and 2026-01-15); §T.4 #9 (R2-45) |
| R2-46 | GT | nit | C/C/C | 'Pipeline-discoverable' recall is undefined in every out-of-family world, where ORC is not run, and in any world where ORC covers nothing. | Fixed | E2P §K.2 S1 |
| R2-47 | CS | nit | C/C/C | §F makes `horizon` and `comparator` mandatory claim fields, then says that horizon and baseline 'can never appear in a claim'. | Fixed | E2P §F table and 'Referee-owned settings' |
| R2-48 | MT | nit | C/C/C | N is rounded up to a multiple of 5 while 'the null share stays at 20%'. | Fixed | E2P §K.7 (null count ⌈N/4⌉, 0.8N/0.2N integers), §C.7 table, §P.3 wall-clock |
| R2-49 | CS | nit | R/R/C | The canonical form merges only lag∘lag. | Rejected (text, design): semantically identical rewrites give identical forecasts, so NEAR_DUPLICATE, clustering and mechanism-level TRK neutralise them | — |
| R2-50 | CF, OC | nit | C/C/C | M-09 says the benchmark needs its full build and full token budget 'before its first outcome'. | Fixed | E2P §T.1 M-09 |
| R2-51 | 1A | nit | C/C/C | Part I.4 says the MRS becomes the first thing built if Exp 2 decision 1 is approved. | Fixed | 1A OR Part I.4 'Relation to the 1A lean build'; Scope estimates 'Earliest technical kill point' |
| R2-52 | 1A | nit | C/C/C | CX-09, which records where the red team goes, is marked 'Resolved (with CX-02)', but CX-02 is OPEN pending decision 1 and its mirror CL-31 is also … | Fixed | E2P §Q.1 CX-09 |
| R2-53 | 1A, OC, T0 | nit | C/C/C | Wrong cross-reference, which makes the table contradict itself. | Fixed | 1A OR Part I.5 row 'B-EVID evidence package' |
| R2-54 | SA | nit | C/C/C | The F1 operating characteristics given to the owner hold only at the more favourable planning SD of 0.20, and the SD is not stated. | Fixed (variant): F1 is now an exact Clopper–Pearson rule, so no planning SD is involved | E2O d4; E2P §K.4 F1, App A.3 |
| R2-55 | T0 | nit | C/R/C | CI is listed as an inline 2-T0 control ('DST, as in Experiment 0'), but the imported 1A definition requires 'target start − origin = 120 min for … | Fixed | 1A OR Part I.5 row B-ASOF ('CI, adapted'); R3 row LK08 (DST; CI) |
| R2-56 | T0 | nit | C/C/C | M-08 reports Experiment 0's daytime result as a tie. | Fixed | E2P §T.1 M-08 |
| C-01 | CR | must | C/C/C | The documents say t0's past-covariate pathway is used by passing 'extra context variates', but that is wrong for the pinned t0 package. | Fixed | E2P §0.6, §T.1 M-02 and M-10, §T.2 Forecaster and known-answer gate, §T.4 row 2 |
| C-02 | CR | must | C/C/C | The referee build that passes the MRS is never bound to the build that runs the evaluation. | Fixed (completed after the fix check) | E2P §B.3 'Binding to the evaluated build' 1–5; §O.2 F_H(2-dev)/(2-eval); §P.2; §T.4 #10 |
| C-03 | CR | should | C/C/C | The blinding rule covers only 'truth grade, coverage, TRK or FDR per arm'. | Fixed | E2P §K.8 (blinded list, delivery only to the sealed record and A5's memory writer, ledgered … |
| C-04 | CR | should | C/R/C | The recommended next experiment has no operating characteristics for its decisive step. | Fixed (variant): an operating-characteristics block in §T.2; the full table is required by §T.4 item 5 | E2P §T.2 'Operating characteristics of confirmation 1', 'Recommendation', NO-FINDING row, §T … |
| C-05 | CR | should | R/R/C | Decision 5 says that replacing ridge with t0 and 'DSL claims constructing t0 past or known-future covariates' makes the benchmark test 'the research … | Rejected (text, design): a lag-shifted catalogue series is known over the horizon, so 𝒢₂ mechanisms can be encoded as known-future covariates without leaking | — |
| C-06 | CR | should | C/C/C | Decision 2 gives the owner P(CONTINUE) ≈ 0.73, but that figure counts only the TRK conditions. | Fixed | E2O d2; E2P §K.7, App A.5 |
| C-07 | CR | nit | C/C/C | The text says the re-estimation rule 'keeps P(beats(c)) ≥ 0.875 at Δ_c = 1.5·MEI'. | Fixed | E2P §K.7 'Guarantee' bullet |
| C-08 | CR | nit | C/C/C | The glossary says t0 (both t0-alpha and t0-beta) 'emits the quantiles 0.1, 0.25, 0.5, 0.75 and 0.9'. | Fixed | E2P §0.6 t0 bullet; §T.2 Forecaster (t0-beta alternative) |
| C-09 | CR | nit | C/C/C | §C.0's exceptions are incomplete. | Fixed | E2P §C.0 lag, revisions and binary rows, §C.3, §C.5 REG (a_S(t) = t − 1), §B.3 MRS-10, §K.5, … |
| C-10 | CR | nit | C/C/C | The MRS gate is budgeted at ≤ 1 × 10⁷ model tokens. | Fixed (completed after the fix check) | E2P §B.3 MRS-1 and binding item 5, §P.2 post-tuning row, §P.3; E2O scope table |
| C-11 | CR | nit | C/C/C | 2-T0 reuses Experiment 0's pinned t0 stack, which silently replaces non-finite forecast values with 0.0 and only logs a warning. | Fixed (completed after the fix check) | E2P §T.2 Forecaster 'Numerical failures', Outcomes INVALID row, Estimate (adapter line) |

**Areas covered** (owner deliverable 12), generated from the lens codes; a finding can appear in more than one area:

| Area | Lens codes | Confirmed findings |
|---|---|---|
| Benchmark gaming | BG | R1-01, R1-02, R1-18, R1-19, R1-20, R1-45, R1-46, R2-01, R2-10, R2-11 (10) |
| Leakage | LK | R1-02, R1-04, R1-06, R1-07, R1-21, R1-31, R1-33, R1-36, R1-37, R2-02, R2-03, R2-12, R2-14, R2-45 (14) |
| Brute-force search | BF | R1-15, R1-16, R1-17, R1-34, R1-47, R1-49, R2-06, R2-07, R2-08, R2-09 (10) |
| Ground-truth validity | GT | R1-01, R1-02, R1-03, R1-21, R1-22, R1-55, R1-56, R1-57, R1-58, R1-75, R2-07, R2-09, R2-22, R2-23, R2-24, R2-46 (16) |
| Multiple testing and statistics | MT, SA | R1-01, R1-02, R1-05, R1-24, R1-25, R1-26, R1-27, R1-28, R1-29, R1-31, R1-32, R1-60, R1-61, R1-62, R1-63, R1-64, R1-67, R1-71, R1-85, R1-86, R1-87, R2-17, R2-18, R2-21, R2-25, R2-27, R2-48, R2-54 (28) |
| Claim splitting, duplicates and reformulation | CS | R1-03, R1-23, R1-48, R1-59, R1-76, R2-26, R2-28, R2-47 (8) |
| Common-model bias | CM | R1-02, R1-20, R1-31, R1-33, R1-69, R1-70, R2-31, R2-32 (8) |
| Replication validity | RV | R1-04, R1-05, R1-06, R1-18, R1-31, R1-33, R1-35, R1-48, R2-21, R2-45 (10) |
| Memory contamination | MC | R1-29, R1-30, R1-50, R1-51, R1-53, R1-54, R2-04, R2-15, R2-16, R2-17, R2-18, R2-19, R2-44 (13) |
| Compute feasibility | CF | R1-04, R1-05, R1-06, R1-15, R1-29, R1-38, R1-42, R1-43, R1-56, R1-65, R1-67, R1-68, R2-29, R2-33, R2-50 (15) |
| 1A consistency, cross-reference and stale status | 1A, XR, SS | R1-04, R1-07, R1-08, R1-10, R1-11, R1-12, R1-13, R1-38, R1-39, R1-44, R1-77, R1-78, R1-79, R1-80, R1-81, R1-82, R1-83, R1-84, R2-01, R2-05, R2-34, R2-35, R2-36, R2-37, R2-51, R2-52, R2-53 (27) |
| Owner compliance | OC | R1-01, R1-03, R1-04, R1-06, R1-07, R1-08, R1-09, R1-10, R1-11, R1-13, R1-14, R1-33, R1-34, R1-35, R1-44, R1-72, R1-73, R1-74, R1-81, R1-88, R2-27, R2-35, R2-37, R2-38, R2-40, R2-41, R2-50, R2-53 (28) |
| t0 alignment (§T) | T0 | R1-01, R1-02, R1-03, R1-04, R1-05, R1-06, R1-07, R1-11, R1-31, R1-32, R1-33, R1-34, R1-35, R1-36, R1-37, R1-40, R1-41, R1-43, R1-44, R1-67, R1-89, R2-35, R2-40, R2-41, R2-42, R2-43, R2-53, R2-55, R2-56 (29) |
| Completeness critic | CR | C-01, C-02, C-03, C-04, C-06, C-07, C-08, C-09, C-10, C-11 (10) |

### R.2 Fix check

**Process.** After the fixes were applied, a read-only workflow (`exp2-fix-check`, 10 agents) checked every confirmed finding against the revised text:
- 8 batch verifiers, one per group of findings;
- a regression reviewer over all four documents;
- an arithmetic and 1A cross-reference checker, which recomputed every derivable figure by closed form or deterministic integration.

**Results.**
- **First application:** 90 fixed, 7 fixed as variants, 1 carried to §T.4, 1 moot, and 49 only partially fixed (17 must-fix, 29 should-fix, 3 nits). Each partial fix came with an exact residual edit, and all residuals were then applied.
- **Additional items:** 38 new issues, 25 regression issues and 15 arithmetic issues. All were applied, with the adjudications below.
- **Confirmed intact:** 1A byte identity; 10 decisions per owner review; the CX↔CL mirror; every 1A cross-reference; and every cited Experiment 0 figure.

**Adjudications between conflicting residuals.**
- **Malformed A0 output after its retry** is a model-behaviour failure dropped from A0's AUC only (R2-10), not a harness error (R2-11's residual was declined).
- **"Attractive"** (θ̂_disc ≥ δ_min, t ≥ 2.5) is used by MRS-10 and A1; a useful negative also needs t ≥ 4.05 (R1-47 over R1-48(a)).
- **Building claims** are scored on their own later-starting forward days, over the full fixed length. This was preferred over a 6-block minimum (R1-31) and over a shared end date (G11).
- **Milestone wording** follows the owner's words ("a finding, followed by an investigation that builds on it"). It does not require a building claim to succeed (a variant of R2-33).

**Design changes caused by the fix check.** These went beyond the residual edits, and an independent planning review of the adjudications adopted them.
1. **F2 was redesigned** (§K.4, Appendix A.7).
   - Its operating characteristics showed that UB₉₅ ≤ 0.05 alone passes only about 0.55 per control with no inflation at the conservative planning values, which would make CONTINUE unlikely without any inflation.
   - F2 now requires an estimate ≤ 0.05 **and** UB₉₅ ≤ 0.10 (the shape of beats(c)). This passes with probability 0.96 at those values (0.99 at m = 0.05) and at most 0.50 at an inflation of 0.05. F2-kill is unchanged, and the two are mutually exclusive.
   - A 0.10 margin alone was rejected, because it would pass a doubling of the false-discovery ratio.
2. **Brute force** (§I.3, §N item 14).
   - Every in-family exact encoding lies at DSL depth ≤ 1 (about 10⁴ expressions), within reach of A1 under C₀ and of A2 if an evaluation costs ≲ 0.2 CPU-s.
   - In-family, the benchmark therefore measures selection and validation, not hypothesis generation, and the EK-B1 headroom rule is the most likely calibration failure.
   - "Enlarge the in-family family" was added as an alternative under owner decision 9.
3. **Escalation while INDETERMINATE** (§J.1).
   - The Monte Carlo band could leave weak HNG and REG mechanisms INDETERMINATE at K = 20.
   - K now doubles, up to 160, while an item is INDETERMINATE, with common seeds for every arm.
4. **Experiment 2-T0 timeline and estimates** (§T.2).
   - Build is about 9–10.5 engineer-weeks, plus 0.5 for the Stage-0 audit, and about 2.3 × 10⁶ t0 calls.
   - First finding, historical grade: about 3–4 months after approval. Hindsight-free grade: about Q4 2027. Milestone complete: November 2027 to February 2028.
   - Outcomes are defined per comparator leg.
5. **Smaller corrections.** The §N item references; the scope of the 2% VOID thresholds; campaign close, defined as the end of replay, quarantine reruns and attribution; the post-close audit rule; A.3–A.6 rounding and values; the §P.3 CPU totals (1,300–2,200 CPU-h); the A2 atom count (35 × 2); and the numeric known-answer thresholds required by §T.4 item 13.

**Second verification.** A second read-only workflow (`exp2-fix-check-2`, 5 agents) re-checked all 127 items from the first fix check, ran a fresh regression review, and recomputed the new figures.
- **Items:** 93 landed and 26 landed as variants. The 3 declined by adjudication are R2-11's harness-error exception, R1-49's draw-probability text and G25's status wording, which becomes true on commit. 5 partially landed; they were completed.
- **New issues:** 17 new, 24 regression and 11 arithmetic issues, all applied. The substantive ones:
  - **VOID ordering.** Operator-inducible VOIDs (harness errors, INVALID world-runs, runner or relay mismatches, a declined MRS rerun) now apply only if no KILL-type rule applies (§L rule 1(b)), which closes a reroll route.
  - **A0 metadata-leak rule.** It is not amendable: one failure voids.
  - **Post-close findings** follow the §K.5 map, so an unattributable finding counts as SUT.
  - **Oracle before calibration.** MRS-11 validates the oracle before any EK-B1 calibration verdict.
  - **Binary predicates.** `B(·)` is restricted to binary series.
  - **Building claims** get defined outcomes, and outcome precedence is separate for the historical and forward results.
  - **Campaign close** waits for quarantine reruns.
  - **Other fixes:** conditional wording on enumeration; A.4's screen size tied to an explicit per-evaluation cost; the A.7 planning row labelled conservative; and small arithmetic corrections (UB(3, 75) = 0.1001; P(CONTINUE) ≤ 0.010 under the literal rule; 1,800–3,200 CPU-h at N = 120; escalation up to about +700 CPU-h).
- **Confirmed intact:** 1A byte identity, 10 decisions per owner review, and 0 malformed table rows across 109 tables.

**Final check.** A third read-only pass (`exp2-fix-check-3`, 2 agents) confirmed that 56 of the 57 second-round items had landed. It found no must-fix items. It reported 2 residuals and 17 should-fix items or nits, all applied. The substantive ones:
- **Time limit on the always-VOID triggers.** Rule 1(a) applies only to events detected before campaign close, and only to TH leaks in the harness's own (S-GEN-owned) code. Leaks through the agent runner, tool wrappers or relay are operator-inducible (rule 1(b)), so they cannot erase a KILL.
- **Amendments after C2-eval** are added to rule 1(b) and Appendix B.
- **The post-close rule** is stated once and used everywhere.
- **MRS-reopen reruns** run on the same worlds, so the analysis stays paired. They cannot recompute a released EK-B2 decision, and campaign close waits for them.
- **The A0 leak check** runs on named fresh `dev-cal` worlds.
- **Appendix references** now say "Appendix A.x".

---

## S. Freeze, approval and amendment protocol

`[DECISION]`
1. **Draft stage (now).** Edits are free, and nothing is frozen.
2. **Approval.** The owner answers the decisions in `OWNER_REVIEW.md` and approves the checklist. The document becomes v1.0, which records the decisions and removes each `[OPEN]` they resolve.
3. **Freeze.** v1.0 is committed on the owner's instruction, and P_H(2) is computed and ledgered. Implementation may begin only after this step, and only when the owner instructs it.
4. **Amendments after freeze.** Each is a new version with a change-log entry (what, why, which endpoints it affects, owner approval) and a new P_H(2).
   - The one calibration amendment (§P.2) is permitted before C2-eval.
   - An amendment after C2-eval voids a CONTINUE or AMBIGUOUS outcome, and a new evaluation ceremony is needed. **It cannot convert a completed KILL** (§L).
5. **Change log:**

   | Version | Date | Change |
   |---|---|---|
   | v0.1-draft | 2026-09-24 | First draft (2026-09-23). Includes the owner's clarification of the t0 research-loop objective (§0.7, §T), the confirmed findings of the adversarial design review (§R.1), and the fix check with the design changes it caused (§R.2) |

---

## T. Recommended adjustment: the next experiment should be a t0 first demonstration ("Experiment 2-T0")

`[INFERENCE: a recommendation for the owner, not a pre-registered decision.]`
- Experiment 2-T0 has no pre-registration yet. Drafting one is the recommended next documentation task (`OWNER_REVIEW.md`, next prompt).
- Nothing here authorizes implementation, a freeze, P_H, or access to ODRÉ, a weather archive or any other external data.
- §T.4 lists the binding requirements that its pre-registration must meet.

### T.1 Mismatches between the current designs and the clarified objective

| ID | Mismatch | Where | Consequence |
|---|---|---|---|
| M-01 | **Neither design runs t0.** 1A's learner is elastic-net quantile regression, and its LightGBM learner G is not run. This benchmark's learner is ridge. Memo v2 §20 said "t0 is irrelevant to Exp 1" | 1A §C.10, §A.4 item 7; §C.11 here | No result of either experiment says anything about t0 or its covariates. 1A certification under κ_1A does not transfer to a t0 pipeline |
| M-02 | **t0's covariate pathway is never exercised.** Past covariates enter the context (as TARGET-typed co-targets through `predict`, or as HISTORICAL-typed variates through a hand-built `TimeSeries`; M-10). Known-future covariates enter `future_covariates` over context and horizon, are standardised over the whole span, and are read bidirectionally, so the horizon length H must not depend on how origins are batched. This benchmark's DSL builds ridge features instead | §E here; t0 paper §4.1; `tfc-t0` 0.3.2 | **The central point-in-time risk of the objective is in neither leak catalogue** (1A §G.4.2, MRS-3). That risk is a known-future covariate filled, anywhere in its span, with values not known at the gate, or a past covariate passed as known-future. Without K3 (weather forecasts), the known-future pathway is exercised only by deterministic K1 information |
| M-03 | **Unit of success.** This benchmark's CONTINUE is a statistical statement over 75 synthetic worlds. The milestone is one real, bounded finding plus a building investigation | §K, §L | The benchmark can pass or fail without producing a single finding |
| M-04 | **Data.** Synthetic, obfuscated, daily worlds. t0 was pretrained on real series and on synthetic "covariate-effect" generators that include decoy covariates | t0 paper §4.2 | A t0 run on 𝒢₂ would partly test t0 inside its own pretraining distribution. A real target is needed for a meaningful finding |
| M-05 | **Building on evidence.** This benchmark's memory spans independent worlds with unique IDs. The milestone needs a second investigation in the same domain that uses the first finding: the baseline updated, and a conditional hypothesis | §I.4, §M | This is closer to Experiment 3's lineages, and to the "baseline includes accepted findings" that 1A does not test (1A §A.4 item 12) |
| M-06 | **Reproducibility.** MRS-1 here and 1A R7 require byte-identical outputs; §K.5 requires zero verdict-level mismatches. In Experiment 0, t0 forecasts at the same pinned weights differed by about 0.03 MW per point between Phase 1 runs #5 and #6, before numpy and pandas were pinned, and by ≤ 0.003 MW per point between Phase 2 runs #9 and #10 under the pinned run-#6 stack (README) | MRS-1; 1A §G.8; Experiment 0 README | A t0 pipeline needs same-machine byte identity with the pinned lock file and container digest, plus a cross-runner tolerance fixed by a stated measurement procedure and resolved by 1A's FRAGILE rule (§H.6) |
| M-07 | **Vintages.** Experiment 0 used RTE's ex-post definitive series; real-time vintages were untested. ODRÉ data are consolidated at M+1 and definitive in H2 of A+1 (README, "Data vintage") | Experiment 0 | Every 2-T0 stage must state its input vintage, target vintage and known_at convention (§T.2, vintage table) |
| M-08 | **Comparator.** In Experiment 0 (MAE of the median, all hours), zero-shot t0 without covariates lost to `blend_50` by 9.0% [−13.8, −4.3]. 98.9% of that deficit sits on night half-hours. `ewma` ranked first by MAE (641 MW). In daytime t0 was indistinguishable from `blend_50`: −0.1% [−4.9, +4.5], a null result, not equivalence | Experiment 0 README, Phase 2 | "X improves t0" and "t0 + X beats the organisation's best forecast" are different claims, and both must be tested, each with its own loss (§T.2) |
| M-09 | **Speed.** This benchmark's earliest outcomes are a design VOID at about week 7 with no model tokens, and a futility KILL at EK-B2 around week 16, after up to about 4.8 × 10⁸ input tokens. A CONTINUE needs the full build (about 15 engineer-weeks) and 3.4–13.6 × 10⁸ tokens | §P | None of these outcomes produces a t0 finding |
| M-10 | **t0's public API does not use the paper's past-covariate role.** In `tfc-t0` 0.3.2, `predict` builds its input with `TimeSeries.from_array`, which types every context row as TARGET (`t0/data.py`). A context covariate is therefore forecast jointly with the target, and its horizon is withheld. The HISTORICAL role, the past-covariate role the paper describes, is reached only through a hand-built `TimeSeries` passed to `predict_from_time_series`. The package does not say which path produced the paper's past-covariate results, and Experiment 0 exercised neither | Pinned package source; t0 paper §4.1 | The past-covariate role encoding must be a referee-owned setting, fixed in the 2-T0 pre-registration and checked by a known-answer test (§T.2) |

### T.2 Recommended design of Experiment 2-T0 (sketch for the owner's review)

**Question.** Does information X, supplied to pinned t0 as a past or known-future covariate, improve day-ahead forecasts of a real target, on sealed data? X is chosen by the AI researcher from a pre-registered point-in-time catalogue. The improvement is measured against two comparators:
- (a) t0 with a matched placebo of X;
- (b) the organisation's best forecast.

A second question is whether the finding replicates on later, sealed data and on data collected after the claim freeze.

**Target and gate.**
- Experiment 0's setting: French national solar generation from ODRÉ.
- Half-hourly UTC grid; 12:00 Europe/Paris gate on D−1; delivery day D of 46, 48 or 50 half-hours; horizons +12 h to +35.5 h on a 48-slot day (+34.5 h and +36.5 h on the 46- and 50-slot days; steps 24–71, 24–69 and 24–73).
- It reuses Experiment 0's loader, DST handling, leakage tests, baselines and pinned t0 stack.
- It needs no Elexon, IRIS or NESO data. Another target is an owner decision.

**Forecaster.**
- **Recommended default:** `t0-alpha` at Experiment 0's revision (Hugging Face `9b02c5f4…`, `tfc-t0` 0.3.2, CPU). Its real pretraining data end before 2022 (paper §4.2 and §5.6.1), before the first sealed day, 2025-01-01.
- **Alternative: `t0-beta`.** It has higher overall fev-bench skill, including on the covariate-informed tasks (paper Table 4: 46.2 against 39.7). Its covariate lift is not reported; Table 5 covers `t0-alpha` only. Choosing it requires all of the following:
  - a documented pretraining cutoff before 2025-01-01, or the sealed segments become screening only and the first finding can be earned only as FINDING-REPLICATED-FORWARD;
  - a pinned package version and revision that load it;
  - resolving whether T_c is a native subset of its 21 levels;
  - re-measuring its determinism tolerance and its cost per call. It is about 2.2–3.2× slower (paper Table 11), and the M-06 figures do not carry over.
- **Scored quantiles:** T_c = {0.1, 0.25, 0.5, 0.75, 0.9}, identical to 1A's T_c.
- **Numerical failures.** The pinned stack replaces non-finite outputs with 0.0 and only logs a warning. The referee's adapter must detect non-finite values before sanitisation and raise a TCB exception:
  - in a claim's forecast, the claim gets p := 1;
  - in a comparator or placebo forecast on a scored segment, every affected claim gets p := 1 and the stage is INVALID;
  - in discovery, it is logged and reported to the researcher as an error, not as a score.
- **The t0 input construction is referee-owned:**
  - the API path;
  - **one fixed role encoding for past covariates** (recommended: HISTORICAL through `predict_from_time_series`, validated by the known-answer gate; alternative: TARGET co-targets through `predict`, stated in the claim boundaries);
  - H per origin as a function of the origin only;
  - a deterministic batch rule;
  - the MISSING and PAD mask conventions.

**Covariate catalogue.**
- **Order:** Stage-0 audit (only with the owner's explicit authorization) → catalogue and known_at rules fixed → 2-T0 freeze → build and discovery.
- **Stage-0 audit limits.** Read-only metadata, schemas, licences, coverage listings, and issue-time and vintage fields. Rows dated up to 2024-12-31 may be read only to check that they exist and to check their timestamps. No 2025–2026 values are read, and no covariate–target statistic is computed. The audit's scope, and every file, endpoint and date window it touched, are recorded in the ledger.
- **If no audit before the freeze:** the pre-registration is frozen with K3, and any K2 entry whose vintage rule is unresolved, excluded. One ledgered catalogue amendment is allowed before discovery.

| ID | Candidates | Role in t0 | Point-in-time status |
|---|---|---|---|
| K1 | Solar geometry from `solarbench/astro.py` (`solar_elevation`, `max_elevation`); clear-sky proxies derived from it by new code, with fixed pre-registered sites, weights and constants; calendar | Known-future | Deterministic functions of time and fixed geography; no vintage risk; no new data source. **K1 is part of the base configuration (t0 + K1, with Experiment 0's timestamp-only dark mask applied to every arm), not a candidate finding.** It is reported as a replication of Experiment 0's night result |
| K2 | Other ODRÉ series available at the gate: regional solar, national consumption, wind, exchanges. A capacity-weighted proxy needs an installed-capacity series with its own vintage rule, and belongs here | Past | A vintage rule per entry (vintage table below) |
| K3 | Weather forecasts issued before the gate: irradiance, cloud cover, temperature. Each entry pre-registers the representation of its context portion, for example archived forecasts at the same lead time as the horizon portion | Known-future | Archive availability, issue-time stamps and licence are UNKNOWN until the Stage-0 audit. **Every value over the whole span 1:T+H must have known_at ≤ the gate** |
| K4 | **Harness-only placebos** (not in the researcher's catalogue) | Both | Null by construction. See Controls |

**Comparators, losses and the claim test.**
- **Daily differentials.** Leg (a): d_D^a = the unweighted mean, over all half-hours of local day D, of the mean pinball loss over T_c, comparator minus claim. Leg (b): d_D^b = the unweighted mean, over all half-hours of local day D, of the absolute error of the best point forecast minus that of the claim's median. The rules below apply to both legs.
  - Every method's quantiles and point forecasts are clipped at 0 identically, and observations are left unclipped.
  - No energy or day weighting is applied.
  - **Primary:** all hours. **Secondary (reported, not used for the milestone):** daytime only, by a timestamp-only astronomical mask fixed before discovery, never Experiment 0's actuals-derived reporting mask.
  - Scope may be restricted only to entries of a fixed scope list published before discovery.
- **Leg (a), information value.**
  - t0 + K1 + X is compared with t0 + K1 + a **matched placebo of X**.
  - The placebo is in the same role and shape, drawn under a committed seed purpose. It keeps X's marginal distribution and diurnal shape, breaks day-specific alignment, and uses only values admissible at the gate. It is averaged over k draws, with k fixed in advance.
  - The loss is pinball over T_c, with margin δ_a.
  - Raw "t0 + K1 without X" is a secondary comparison only.
- **Leg (b), competitiveness.**
  - The MAE of t0 + K1 + X's median is compared with the best point forecast.
  - That best forecast is selected on 2021–2024 data only, by mean d_D^b with a fixed tie rule, from Experiment 0's Phase 2 methods: `prev_day`, `prev_week`, `mean_3d`, `mean_7d`, `median_7d`, `ewma`, `blend_50`, `t0` and `t0_night_zero`.
  - The margin δ_b ≥ 0 is stated separately.
- **Per-claim test.** p = max(p_a, p_b), the intersection–union p-value, with Holm across the at most 4 claims applied to those maxima.
- **Blocks.** 14-day blocks of delivery days, with shifted nulls at δ_a and δ_b.

**Vintage table** (to be confirmed by the Stage-0 audit):

| Stage | Input vintage | Target vintage | known_at convention |
|---|---|---|---|
| Discovery, 2021-01-01 to 2024-12-31 | Definitive | Definitive | Historical real-time values cannot be rebuilt, so known_at := valid_end + the nominal real-time lag, and the rows are flagged `vintage_substituted`. TE, VS and LN are defined against this convention |
| Confirmation 1, 2025-01-15 to 2025-12-31 | Definitive if published before the vault fetch, otherwise consolidated | The same | As for discovery. The segment is snapshotted and hashed at the fetch, with ODRÉ `nature` counts, and scored on that snapshot even if ODRÉ revises it later |
| Confirmation 2 / replication, 2026-01-15 to the last month consolidated before the 2-T0 pre-registration freeze | Consolidated (M+1) | Consolidated | As for discovery |
| Forward window | Real-time, as captured by the recorder at each gate; never rebuilt from a later vintage | Consolidated at M+1 for the gating score, as for segment 2; real-time for a separate, non-gating transfer test (NOT-TRANSFERRED-TO-REAL-TIME) | Real known_at, from the recorder's hash-chained capture |

The per-stage vintage map of this table enters each claim's information set.

**Stages** (each claim is frozen by its hash before the segment that tests it is opened):
1. **Discovery.** The AI researcher (pinned model, sandbox, no network) uses `discover()` on 2021–2024, with K1 in the base. The discovery budget Q is stated in the pre-registration: about 200 candidate evaluations over 1,461 days.
2. **Sealed confirmation 1** (single-use G1; at most 4 claims; Holm on the max-p; embargo of the first 14 days). Segment: 2025-01-15 to 2025-12-31, about 25 blocks.
3. **Replication on sealed segment 2** (per claim: the G1 statistic in 14-day blocks, both legs combined by p = max(p_a, p_b), shifted nulls at δ_a and δ_b, one-sided α = 0.05; fixed horizon, single look; 14-day embargo). Segment: 2026-01-15 to the last month consolidated before the 2-T0 pre-registration freeze, about 17–18 blocks, which gives about 0.8 power at the effect sizes that confirmation 1 detects with 0.8 power (Appendix A.6). A claim with n_b < 6 is UNTESTABLE.
4. **Prospective forward replication** (the hindsight-free test).
   - **Window.** It starts on the first delivery day after both of these: the claim-batch hash is ledgered, and recorder go-live is verified (an RC-style cross-check of the first recorded gate: capture_time ≤ gate and known_at consistent).
   - **Length.** A referee-owned constant (§T.4 item 1), identical for every claim and fixed in the 2-T0 pre-registration before its freeze: an exact count of eligible delivery days in complete 14-day blocks, about 17–20 blocks. It is chosen for about 0.8 power on each leg at the effect that confirmation 1 detects with power 0.8 (a per-block standardised effect of about 0.65 above the margin; Appendix A.6), capped at one annual cycle. Season becomes a scope condition of each window unless that window covers a full cycle.
   - **Test.** As Stage 3: per claim, the G1 statistic in 14-day blocks, both legs combined by p = max(p_a, p_b), shifted nulls at δ_a and δ_b, one-sided α = 0.05.
   - **Single look.** One look at the end; no forward statistic is computed or released before the end date.
   - **Recorder.** At each gate the recorder captures every input any frozen claim uses, including each known-future forecast run with its issue time. Each snapshot is hashed into the ledger before the gate; a day whose snapshot is late or missing is ineligible and is never backfilled. The run is INVALID if more than 10% of days are ineligible.
5. **Building investigation.**
   - **Entry.** It enters after the premise finding reaches FINDING-REPLICATED (Stage 3).
   - **Premise.** The current best forecast becomes t0 + K1 + X.
   - **Evidence released to the researcher:** the discovery evidence, plus confirmation-1 and confirmation-2 per-day results after their closure. Forward-window per-day outputs are never released before the building claims are frozen.
   - **Claims.** Using that ledgered evidence, the researcher proposes at most 4 conditional hypotheses: a transform of X, a second covariate, or a regime-restricted effect from the fixed scope list. Their discovery budget Q is stated in the pre-registration.
   - **Window.** The building claims are frozen, then tested prospectively only on forward delivery days after their own claim-batch hash is ledgered and the recorder's capture of every input they add is verified as in Stage 4, over the same fixed length as Stage 4. Their window therefore overlaps the premise's and ends about 1–2 months later.
   - **Test.** This is their only confirmation, so the G1 max-p per claim is tested with Holm across the building batch at one-sided α = 0.05. Leg (a): the building claim's forecast (for example t0 + K1 + X + X₂) against the same forecast with a matched placebo of the new element. Leg (b): the MAE of its median against the median of t0 + K1 + X, the current best forecast, with margin δ_b. Power at the premise's planning effect is about 0.6–0.7 under Holm with 4 claims, and lower for smaller incremental effects `[INFERENCE]`.
   - **Dependence.** The two forward tests share days and are not independent replications.
   - **No adaptation.** The building window runs to its fixed end whatever the premise's forward result. Voiding is applied after both are scored.
   - **Outcomes.** Each building claim is scored PASS if its Holm-adjusted max-p ≤ 0.05 and no control failed. Otherwise the INCONCLUSIVE / UNDERPOWERED and NOT-REPLICATED rows of the Outcomes table apply to its own forward window; UNTESTABLE-FORWARD if n_b < 6; INVALID as in the Outcomes table.
   - **Voiding.** Building findings count only if the premise reaches FINDING-REPLICATED-FORWARD. They are void if the premise's forward outcome is NOT-REPLICATED, and reported as suspended (not as findings) if it is INCONCLUSIVE / UNDERPOWERED, UNTESTABLE-FORWARD or INVALID.
   - **Slower alternative:** a disjoint second forward window, which would complete in about the second half of 2028.

**Controls** (the Part I.5 gate, 1A owner review):
- the inline point-in-time controls on t0's `context` and `future_covariates` arrays;
- **forecast-level controls:** PO and TE on the forecasts, over whole batches, plus batch-composition invariance;
- the t0-specific leak mutants, run on real-data trial units built from discovery data only;
- **a mandatory known-answer gate before discovery,** on a semi-synthetic target with the same gate, horizon and array layout, built from discovery-era data:
  - a planted known-future covariate carrying the horizon values of the target plus noise must PASS by a pre-registered margin (§T.4 item 13);
  - a planted past covariate leading the target by at least the horizon must PASS through the chosen role encoding;
  - a decoy must not beat a matched placebo of itself beyond a pre-registered tolerance;
  - shifting the `future_covariates` horizon by one step must reduce the planted known-future covariate's leg-(a) mean block differential by at least a pre-registered fraction r;
- **a real-data size check,** after the vault closes:
  - at least 100 K4 placebos, drawn under a dedicated committed seed purpose, each tested alone on each closed sealed segment through the identical pipeline (G1 statistic, 14-day blocks, one-sided α = 0.05, δ = 0) against t0 + K1 + an independent placebo of the same construction;
  - the placebos are null by construction: synthetic series matched in marginal distribution and autocorrelation, or phase-randomised or day-block-permuted surrogates of real series (permuted only among days admissible at the gate, with 2021–2024 per-slot and day-of-year profiles removed);
  - no lead shifts;
  - the check is INVALID iff the PASS count exceeds the 95th percentile of its block sign-flip null distribution (which calibrates for dependence between placebos), and the full placebo T-distribution is reported;
  - a positive control must drive this check to INVALID: an anti-conservative verdict engine that tests half-hour units, and leaky placebos built from post-gate target values.

**Custody of the sealed segments.**
- Until the confirmation-1 vault closes, no person or session that writes the catalogue, the comparators, the placebos, the adapter, the brief or the researcher configuration may fetch or open ODRÉ values dated after 2024-12-31. The same applies to values after 2025-12-31 until confirmation 2 closes.
- A vault service fetches each sealed segment once, after the 2-T0 P_H and the claim-batch hash tested on that segment are ledgered. It records the file hash, the vintage counts and the fetch time.
- Every project fetch from ODRÉ is logged with its date window.
- Any exposure to the sealed periods before the 2-T0 pre-registration freeze, including the owner's and the model's, is disclosed in the claim boundaries.

**Outcomes** (per claim, and FINDING-REPLICATED for the run if any claim reaches it). Precedence: INVALID, then UNTESTABLE, then the rest, applied separately to the historical result (confirmation 1 and segment 2) and to the forward result. A forward INVALID or UNTESTABLE-FORWARD leaves an earned FINDING-REPLICATED standing and is reported as the forward outcome. Every row except INVALID requires that no control failed. Building claims are scored as in Stage 5.

| Outcome | Condition |
|---|---|
| INVALID | A point-in-time, forecast-level, placebo or known-answer control failure; a reproducibility failure; or a t0 numerical failure in a comparator or placebo forecast |
| UNTESTABLE / UNTESTABLE-FORWARD | n_b < 6 in a replication segment or window |
| **FINDING-REPLICATED** | Confirmation-1 PASS on both legs, and replication PASS on segment 2 on both legs. **The first finding, historical grade** |
| **FINDING-REPLICATED-FORWARD** | Additionally, a forward PASS on both legs. **The first finding, hindsight-free grade** |
| IMPROVES-T0-ONLY | At confirmation 1, leg (a) PASS in a separately pre-registered secondary Holm family, and leg (b) NOT-PASS. A bounded finding, not the milestone; leg (a)'s segment-2 and forward replications are reported |
| INCONCLUSIVE / UNDERPOWERED | A replication (segment 2 or forward), or a building claim's forward test, fails, and for every failing leg ℓ ∈ {a, b} the one-sided 95% upper t-bound of that segment's mean 14-day-block differential is ≥ δ_ℓ |
| NOT-REPLICATED | A replication, or a building claim's forward test, fails and, for some failing leg ℓ, that upper bound is < δ_ℓ |
| NOT-TRANSFERRED-TO-REAL-TIME | A forward PASS against the consolidated target but a fail against the real-time target. Reported; it does not change FINDING-REPLICATED-FORWARD |
| NO-FINDING | No confirmation-1 PASS. **Not evidence that X is uninformative.** Valid only if the known-answer gate passed. The 2025 vault is then consumed, and a new catalogue needs a new sealed segment (the forward window) |

**Milestone complete** when the first finding reaches FINDING-REPLICATED-FORWARD **and** at least one building claim, frozen before its window, is scored to PASS, NOT-REPLICATED or INCONCLUSIVE / UNDERPOWERED. INVALID, UNTESTABLE-FORWARD, void or suspended do not count. The report names which outcome occurred. This follows the owner's wording ("a finding, followed by an investigation that builds on it"); it does not require the building claim to succeed.

As drafted, 2-T0 produces no validated negative units. An optional negative family is listed in §T.4.

**Operating characteristics of confirmation 1** `[INFERENCE; planning SE from Experiment 0's 2024 interval on the MAE-of-median basis, to be replaced by the SE from Experiment 0's 2024 per-day errors under the pre-registered losses; no 2025 data used]`
- **Planning SE.** About 2.4 percentage points over Experiment 0's 26 blocks, rescaled to about 2.5 pp over confirmation 1's 25 blocks.
- **Hurdle against leg (b).** The minimum detectable effect is about δ_b + 4.2–5.9 pp for 50% power, and δ_b + 6.3–8.0 pp for 80%. The ranges run from m = 1 to m = 4 claims, the Holm first step being α/m.
- **What X must deliver.** t0 + K1 (night-zeroed) starts about 2.3% behind `ewma` by MAE (Experiment 0: 656 against 641 MW). X must therefore improve MAE by about 8.5–10% plus δ_b for 80% power on leg (b) (i = 1 − (641/656)(1 − MDE₈₀ − δ_b)).
- **Feasibility.** Weather forecasts at national scale plausibly do this; history-only K2 information plausibly does not.
- **Consequence.** A K1/K2-only confirmation is expected to end NO-FINDING or IMPROVES-T0-ONLY on leg (b), and would consume the 2025 vault.

**Recommendation.** Authorize the Stage-0 weather-archive audit before the 2-T0 freeze, and spend the 2025 vault only with K3 in the catalogue, unless the owner accepts IMPROVES-T0-ONLY as the realistic outcome.

**Timeline** `[INFERENCE]`, if the owner approves drafting now:

| Step | When |
|---|---|
| 2-T0 pre-registration drafted and approved | About 2–3 weeks |
| Stage-0 audit (if authorized) | Within those weeks, before the freeze |
| Build | About 9–10.5 engineer-weeks (one engineer) |
| Discovery | About 1–2 weeks |
| First sealed confirmation | About 10–13 weeks after build start |
| **First finding, historical grade** (confirmation 1 plus replication on segment 2) | About 3–4 months after approval: January–February 2027 if approved in early October 2026 |
| Premise forward window | Opens on the first delivery day after the claim-batch hash is ledgered and recorder go-live is verified (Stage 4); about 17–20 blocks (8–9 months), plus the one-month consolidation lag |
| **First finding, hindsight-free grade** | About Q4 2027 |
| **Milestone complete** (the building investigation scored in its own forward window) | About 13–16 months after approval: November 2027 to February 2028 |

**Claim boundaries.**
- One target, one gate and one t0 revision. Predictive, not causal. No trading value.
- The referee is not certified; it has only the Part I.5 subset.
- The vintage is stated per stage.
- **"Independent" means** later, disjoint, procedurally sealed public data (segment 2) and, for the forward grade, prospectively collected data, all scored by the same pinned pipeline. It does not mean an independent team, implementation or clean-room re-computation (1A R2 is not run).
- A second country's solar is a **transfer test** that cannot yield FINDING-REPLICATED for the French claim, unless the claim's scope covered both targets before confirmation 1.
- If the pinned researcher's knowledge vintage is later than the start of a sealed segment, that segment is recorded as not blind to the researcher, and only the forward window is hindsight-free.
- The researcher and the harness authors may share a model family; shared blind spots are not excluded, especially on the sealed segments.
- FINDING-REPLICATED does not show that the AI researcher outperforms an exhaustive screen of the catalogue (§T.4).

**Estimate** `[INFERENCE]`

| Item | Engineer-weeks |
|---|---|
| *Before the freeze:* Stage-0 audit (once authorized) | *0.5* |
| Registry, catalogue, vintage rules and as-of path for t0 inputs | 1.0 |
| t0 adapter (role path, batch rules, non-finite detection) and `discover()` | 1.0 |
| Comparators: the Experiment 0 baselines reused, plus the matched-placebo comparator | 0.5 |
| G1 vault, ledger, claim schema, evidence packages | 1.5 |
| Minimal agent harness and brief | 2.0 |
| Referee-subset checks: inline and forecast-level controls, mutants on real-data trial units, R5.G1, R6 subset, canaries | 1.5 |
| Known-answer gate, placebo generator, size check and its positive controls | 1.0 |
| Forward recorder | 0.5 |
| **Build sum** (excluding the audit) | **9.0**, so **about 9–10.5 with up to 15% contingency**, plus 0.5 for the audit before the freeze |

- **Compute.** About 2.3 × 10⁶ t0 calls: both discovery stages about 1.5 × 10⁶ (200 evaluations × 1,461 origins × about 2.5 t0 calls per candidate-origin × 2 stages: the claim forecast plus, on average, about 1.5 placebo forecasts, since placebo legs are not run for every candidate), mutants and receipts about 0.5 × 10⁶, and about 0.3 × 10⁶ for the confirmations, the placebo check and the known-answer gate. At 0.2–1 s per call, and about 1.5× for added variates, that is about 190–960 CPU-h. It is measured in build week 1.
- **Tokens.** About 0.7–2.8 × 10⁷: about seven researcher sessions at 1–4 × 10⁶ each, including brief development.

### T.3 What happens to this benchmark

**What transfers to Experiment 2-T0, and what does not.**
- **Transfers:** the single-batch rule, the claim caps, the hash, the duplicate and near-duplicate rules, closure, the MRS approach, and the Experiment 3 lineage design.
- **Does not transfer:** TRK coverage, harness clusters and same-law harness replication all need a generator oracle, which real data do not have. The §F schema does not transfer either. 2-T0 needs its own schema (§T.4). §G.5 is adapted: condition 3 becomes "replication PASS", and condition 4 becomes "no 2-T0 control failure".

**When the benchmark runs.** After Experiment 2-T0, as the test of research competence at scale against controls.

**Recommended adaptation (owner decision 5).** Replace the κ₂ ridge learner with pinned t0, and have the DSL construct t0 covariates (past or known-future) rather than ridge features. Adopting it also requires re-specifying:
- **B*.** For example, t0 with the disclosed drivers as covariates.
- **M_c and the oracle estimand.** t0 is not fitted, so the K training draws become context draws.
- **The §C.5 β calibration and the trap truth conditions** of §C.6 and §C.12, which are defined relative to a ridge B*.
- **The oracle checks.** MRS-11 is kept to validate the oracle's machinery with a linear learner, and a t0 known-answer check is added.
- **What truth means.** Truth is about the pipeline, so a planted mechanism that t0 does not use is FALSE for every arm. The ORC < 0.80 calibration rule may then fail, and EK-B1 must measure this.
- **𝒢₂ and the annex.** They must be checked for overlap with t0's published effect families, and at least one annex form must lie outside them.

**Cost of that adaptation, to be established before re-drafting** `[INFERENCE]`:
- About 6–28 CPU-h per claim for M_c alone at K = 20 (10⁵ t0 forecasts at 0.2–1 s); about 11–56 CPU-h if B* forecasts are not cached per world; up to 8× that at K = 160.
- At campaign level, of order 10⁴–10⁵ CPU-h across grading, set-level coverage ablations and calibration.
- Shrinking the oracle's test days raises s_o by up to √10. Through the K-doubling rule and INDETERMINATE-as-false, that can inflate FDR and the F1-kill risk. It would therefore require re-deriving the §J.1 K rule, the §J.2 margins and the INDETERMINATE share, or else a validated, cheaper truth for t0.

### T.4 Binding requirements for the Experiment 2-T0 pre-registration

Each requirement comes from a confirmed review finding (§R.1) or from the fix check (§R.2). They are recorded here so the next draft cannot drop them. `[DECISION for the drafting task; the design choices themselves remain the owner's]`

| # | Requirement | Finding |
|---|---|---|
| 1 | **Claim schema** with its own `spec_version`. The hash covers: target and the per-stage target-vintage map of the §T.2 vintage table; catalogue ID and role (past or known-future); a transform from an enumerated half-hourly grammar; scope from the fixed scope list, with a coverage floor in delivery days; δ_a and δ_b; direction. The comparators, α, block length and forward window are referee-owned constants | R2-26 |
| 2 | **Owner choices to be recorded in the 2-T0 owner review:** the t0 variant (default `t0-alpha`); the past-covariate role encoding (default HISTORICAL); the primary slice (default all hours); milestone strictness (default both legs; alternative leg (a) only); whether K3 enters the first catalogue; an optional negative family; the researcher model and its knowledge vintage; common-model mitigation; seed custody (1A decision 7); the replication design (default: 2026 sealed replication, then the forward window, with the building claims in their own later-starting window; alternative: a disjoint second forward window) | R2-41, C-01, R2-43, R1-32, C-04, R2-27, R2-32, R2-36 |
| 3 | **Researcher model and knowledge vintage** named and recorded. Catalogue authors attest which 2025–2026 data they examined. The known_at rules are audited by the owner, or by a session from another model family, with the auditor recorded | R1-33, R2-32 |
| 4 | **Scripted comparison.** Before discovery, a pre-registered script runs an exhaustive single-covariate screen of K2 and K3 (K1 is in the base configuration) in each admissible role, on top of the t0 + K1 base, under the same t0-call budget. Its top-4 ranking is hash-ledgered, hidden from the researcher, and compared descriptively after closure. Optionally, its batch is sealed and graded for comparison only. The milestone is defined on the AI arm's Holm family alone | R1-34 |
| 5 | **Operating-characteristics table** for confirmation 1 and each replication segment, using the SE from Experiment 0's 2024 per-day errors under the pre-registered losses, with the minimum detectable effect per leg and a prior feasibility per catalogue entry | C-04, R1-05 |
| 6 | **Itemised build and compute estimate**, with per-call cost measured in week 1, and tokens per session | R1-42 |
| 7 | **Determinism rule:** the pinned lock file and container digest; same-machine byte identity; a cross-runner tolerance fixed by a pre-specified measurement before discovery, resolved by 1A §H.6 | R1-43 |
| 8 | **Optional negative family** (owner choice): up to 2 negative claims per stage, tested with the §G.2 negative statistic as a separate Holm family and replicated under the same fixed-window rule. Adopting it adds a negative-family condition to the known-answer gate: over pre-registered repeated trials, a planted covariate with known effect above δ must not yield negative PASSes at a rate above α. Only a validated negative may be recorded as negative knowledge or used to retire a catalogue entry | R2-27 |
| 9 | **Embargo** of one 14-day block at the start of each sealed segment, with a sensitivity analysis dropping the first block. t0's context may read embargoed days | R2-45 |
| 10 | **The Part I.5 gate table** (1A owner review), with its stop and reopen rules, and the binding of the tested build to the evaluated build, as in §B.3 here | R1-40, C-02 |
| 11 | **Forward recorder** captures every input of every frozen claim at each gate, including known-future forecast runs with their issue times. A snapshot written after the gate with a backdated known_at is a mutant to be detected | R2-12 |
| 12 | **Fixed-horizon forward test:** a single look at a pre-registered length; forward data sealed until the end date; no monitoring unless a separate anytime-valid test is specified (1A's G3 does not apply at a 12:00 D−1 gate) | R2-21, R2-35 |
| 13 | **Numeric gate thresholds**, fixed before discovery: the known-answer gate's planted-covariate PASS margin, its decoy tolerance and the minimum horizon-shift degradation r (with its statistic). The size check's INVALID level is the §T.2 default (95th percentile of the block sign-flip null) unless the 2-T0 pre-registration states otherwise | Fix check (§R.2) |

---

## Appendix A. Operating-characteristic arithmetic

**Method.** Normal approximation to the paired t-statistic, with Student-t critical values:

P(beats(c)) = 1 − Φ((max(t_{N−1,0.95}·SE, MEI) − Δ)/SE); P(fails(c)) = Φ((MEI − t_{N−1,0.9875}·SE − Δ)/SE), with SE = σ_Δ/√N.

- The critical values are t_{59,0.95} = 1.671 (z = 1.645) and t_{59,0.9875} = 2.300 (z = 2.241), computed by deterministic numerical integration of the t density.
- The operating characteristics assume independence across worlds (§K.3).
- **Binomial bounds** are exact Clopper–Pearson bounds, computed by bisection on the binomial CDF.
- Deterministic; no randomness.

### A.1 Per-control rules (σ_Δ = 1, MEI = 0.3)

| True Δ | N = 60: beats | N = 60: fails | N = 100: beats | N = 100: fails | N = 120: beats | N = 120: fails |
|---|---|---|---|---|---|---|
| −0.20 | 0.000 | 0.942 | 0.000 | 0.997 | 0.000 | 0.999 |
| 0 | 0.010 | 0.509 | 0.001 | 0.765 | 0.001 | 0.845 |
| 0.15 | 0.123 | 0.128 | 0.067 | 0.219 | 0.050 | 0.265 |
| 0.30 | 0.500 | 0.011 | 0.500 | 0.011 | 0.500 | 0.012 |
| 0.45 | 0.877 | 0.000 | 0.933 | 0.000 | 0.950 | 0.000 |
| 0.60 | 0.990 | 0.000 | 0.999 | 0.000 | 0.999 | 0.000 |

**Sample size for significance alone** (LB₉₅ > 0 with 90% power, ignoring the Δ̂ ≥ MEI requirement), n = 8.564·(σ_Δ/Δ)²: 96 at Δ = 0.3; 54 at 0.4; 43 at 0.45; 35 at 0.5.

**With the MEI requirement,** P(beats) ≥ 0.875 at Δ = 1.5·MEI needs n = (1.15·σ_Δ/(0.5·MEI))² = 58.8 at σ_Δ = 1, so N = 60 (§K.7).

### A.2 Interim futility (n = 16 non-null worlds)

| Rule | Stop iff Δ̂_{A1} < | Δ = 0 | 0.15 | 0.30 | 0.45 | 0.60 | Linear 0.15 → 0.45 | Linear 0 → 0.6 |
|---|---|---|---|---|---|---|---|---|
| UB₉₅, t₁₅ = 1.753 (default) | −0.138 | 0.290 | 0.124 | 0.040 | 0.009 | 0.002 | 0.096 | 0.195 |
| UB₈₀, t₁₅ = 0.866 | 0.083 | 0.631 | 0.395 | 0.193 | 0.071 | 0.019 | 0.337 | 0.510 |

The "linear" columns are campaign-mean-MEI learning curves. For a linear rise from a to b over 75 worlds, the interim mean is a + 0.128·(b − a).

### A.3 F1 ceiling and F1-kill (exact Clopper–Pearson on the per-world indicator Z)

At 75 worlds, F1 passes iff x ≤ 2 (UB(2, 75) = 0.0816; UB(3, 75) = 0.1001 > 0.10), and F1-kill fires iff x ≥ 13 (LB = 0.1057). At 150 worlds: pass iff x ≤ 8, kill iff x ≥ 22.

| Per-world false-validation rate p | 0.005 | 0.01 | 0.02 | 0.03 | 0.05 | 0.10 | 0.15 |
|---|---|---|---|---|---|---|---|
| P(F1 passes), 75 worlds | 0.994 | 0.960 | 0.810 | 0.608 | 0.270 | 0.016 | 0.001 |
| P(F1-kill), 75 worlds | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.034 | 0.332 |
| P(F1 passes), 150 worlds | 1.000 | 1.000 | 0.997 | 0.962 | 0.664 | 0.031 | 0.000 |

- Under honest use, the referee arms' expected probability of falsely validating one null claim is at most α_conf × α_rep ≈ 0.0025 `[INFERENCE]`. With up to 4 claims per world, a per-world rate p of about 0.01 or less is plausible.
- **This is not measured;** EK-B1 measures it for A1.
- **At 75 worlds, F1 is demanding:** it passes with probability 0.61 at p = 0.03. Owner decision 4 may raise N or the ceiling.

### A.4 Detection per mechanism (approximation; EK-B1 measures it)

- **Per-day signal-to-noise** of the shifted differential for a mechanism with skill θ against δ = 0.01 is about (θ − δ)/(2√θ). This is a Gaussian approximation that ignores estimation error and dependence.
- **Over 1,095 days:**

  | θ | Mean T | P(confirm) at α/4 | P(replicate) at α | Discovery t (θ against 0) |
  |---|---|---|---|---|
  | 0.04 | 2.48 | 0.59 | 0.80 | 3.31 |
  | 0.06 | 3.38 | 0.87 | 0.96 | 4.05 |
  | 0.08 | 4.09 | 0.97 | 0.99 | 4.68 |
  | 0.10 | 4.71 | 0.99 | 1.00 | 5.23 |
  | 0.15 | 5.98 | 1.00 | 1.00 | 6.41 |

- **Expected ORC coverage** under θ^solo ~ LogUniform[0.05, 0.15], as E[P(confirm at α/4) × P(replicate at α)] with ORC's exact encodings:
  - **First-release attenuation.** Half the drivers are revised, with r ~ U[0.2, 0.6]. A linear driver keeps the fraction 1/(1 + r²) of its skill. A hinge keeps less (by two-dimensional Gaussian quadrature): 0.95, 0.82 and 0.66 at q = 0.5, and 0.93, 0.77 and 0.59 at q = 0.75, for r = 0.2, 0.4 and 0.6.
  - **REG** is confirmed on its regime scope: about half the days, with in-scope skill 2θ/(1 + θ).
  - **By type:** LIN 0.90; REG 0.93; HNG-0.5 0.89; HNG-0.75 0.87. **In-family mix ≈ 0.91** (0.93 for LIN without attenuation).
  - **Set effects.** Holm across ORC's J ≤ 4 claims is already covered by using α/4. Coverage under the τ_j rule needs cov_j − 3·s_D ≥ τ_j, a margin of only ½(θ_ref − L_j) ≈ 0.13–0.25·θ_ref for HNG and REG. At K = 20, s_D (about 0.0014 at θ = 0.05) can leave weak mechanisms COVERAGE-INDETERMINATE, which the §J.1 escalation rule resolves (s_D ≈ 0.0005 at K = 160).

  That leaves a margin of about 0.10 to the 0.80 calibration floor `[INFERENCE]`. EK-B1 measures it. Under the previous LogUniform[0.04, 0.15] prior, ORC's LIN coverage would have been about 0.84.

  **A1.** No closed-form expectation is derived. A1 reaches every in-family exact encoding within about 2.6 × 10³ evaluations (§I.3), so its coverage is limited mainly by selection (stability selection, distinct drivers, at most 4 claims) and can approach ORC's. The headroom rule (ORC − A1 ≥ 0.25) is therefore the check most likely to fail (§L). EK-B1 measures A1's coverage by type.
- **Discovery t and search size.** The discovery t for θ = 0.05 is about 3.7. The expected maximum of n independent null t-statistics is 3.44 at n = 2,000, 4.38 at 10⁵ and 4.79 at 7 × 10⁵ (deterministic integration). Under C₀ (7,200 CPU-s) an arm can screen about 3.6 × 10⁴ expressions at 0.2 CPU-s per evaluation (expected maximum null t ≈ 4.2), and about 1.4–7 × 10⁵ at an assumed 10–50 ms `[INFERENCE]`; the EK-B1 Q meter measures it. Either way, a discovery t near the prior's lower end is not distinguishable from selection noise without confirmation. This is why confirmation and replication, not discovery t, decide credit.

### A.5 Memory rule under owner decision 2 (N = 60, σ_Δ = 1)

| Rule | Δ_{A4} = 0 | Δ_{A4} = MEI |
|---|---|---|
| Literal (A5 must beat A4) | P(beats) = 0.010; P(fails) = 0.509 | P(beats) = 0.50; P(fails) = 0.011 |
| Recommended (non-inferiority, margin MEI) | P(pass) = 0.743 | P(pass) ≈ 0.999 |

**P(CONTINUE), recommended rule** `[INFERENCE, independence assumed]`. With memory neutral and every other control at Δ = 0.6:
- the TRK conditions hold with probability ≈ 0.99³ × 0.743 ≈ 0.72;
- including EK-B2 survival (0.998 under the default) and F1: ≈ 0.69 at a per-world false-validation rate of 0.01, or about 0.58 at 0.02;
- including F2 at the conservative planning values of Appendix A.7 (0.96 per control, 0.89 for all three): **P(CONTINUE) ≈ 0.61 at 0.01, or ≈ 0.52 at 0.02** (about 0.67 and 0.57 at m = 0.05). F2's planning uncertainty is large (Appendix A.7), so these figures are indicative only.
- **Caveat.** Δ = 0.6 against A1 and A2 is optimistic, because A1 reaches every in-family exact encoding within about 2.6 × 10³ evaluations, and A2 exhausts DSL depth ≤ 1 if an evaluation costs ≲ 0.2 CPU-s (§I.3).

### A.6 Experiment 2-T0 replication power (planning)

- Take an effect that confirmation 1 detects with power 0.8 over 25 blocks at Holm α/4 (per-block standardised effect ≈ 0.65; exact noncentral t, 24 df).
- Its replication power at one-sided α = 0.05 is about 0.39 over 6 blocks, 0.82–0.84 over 17–18 blocks, and 0.88 over 20 blocks, before winner's-curse shrinkage.
- Hence segment 2's length, about 17–18 blocks, and the forward window of about 17–20 blocks.
- **Building claims** are tested with Holm across up to 4 claims (first step α/4). At the same effect, their power is about 0.59 over 17 blocks and 0.68 over 20 blocks, and lower for smaller incremental effects.

### A.7 F2 operating characteristics (planning model)

**Model** `[INFERENCE]`.
- Over 75 worlds, A5 and a control each assert R̄ clusters per world on average, with pooled asserted false-cluster ratio m.
- The delta-method variance of a pooled ratio with world clustering is ≈ R̄·m(1 − m)/(75·R̄²), treating each world's false count as binomial (this ignores within-world clustering).
- The paired difference has SE ≈ √(2·var·(1 − ρ)), where ρ is the correlation between the arms' world-level residuals.
- For confirmed claims, m ≈ 0.01–0.05 is the likely range, because a false claim passes sealed confirmation with probability at most α/4 to α. The larger values are stress cases.
- **Rule** (§K.4): F2 passes iff the estimate ≤ 0.05 and UB₉₅ ≤ 0.10; F2-kill fires iff LB_{98.33} > 0.05.
- EK-B1 reports A1's R̄ and m̂ to replace these planning values.

| R̄ | m | ρ | SE | P(F2), no inflation | P(F2), inflation 0.05 | P(F2-kill), inflation 0.05 | P(F2-kill), inflation 0.10 |
|---|---|---|---|---|---|---|---|
| 1.0 | 0.02 | 0 | 0.023 | 0.99 | 0.50 | 0.017 | 0.52 |
| 1.0 | 0.05 | 0 | 0.036 | 0.88 | 0.41 | 0.017 | 0.23 |
| 1.0 | 0.10 | 0 | 0.049 | 0.65 | 0.27 | 0.017 | 0.13 |
| 1.0 | 0.15 | 0 | 0.058 | 0.53 | 0.22 | 0.017 | 0.10 |
| 1.5 | 0.02 | 0.5 | 0.013 | 1.00 | 0.50 | 0.017 | 0.95 |
| 1.5 | 0.05 | 0.5 | 0.021 | 0.99 | 0.50 | 0.017 | 0.62 |
| **1.5** | **0.10** | **0.5** | **0.028** | **0.96** | **0.50** | **0.017** | **0.36** |
| 1.5 | 0.15 | 0.5 | 0.034 | 0.91 | 0.44 | 0.017 | 0.26 |
| 2.5 | 0.05 | 0 | 0.023 | 0.99 | 0.50 | 0.017 | 0.54 |
| 2.5 | 0.10 | 0 | 0.031 | 0.94 | 0.49 | 0.017 | 0.30 |
| 2.5 | 0.15 | 0.5 | 0.026 | 0.97 | 0.50 | 0.017 | 0.42 |

- **Across the full grid** (R̄ ∈ {1, 1.5, 2.5}, m ∈ {0.02, 0.05, 0.10, 0.15}, ρ ∈ {0, 0.5}), P(F2 | no inflation) ranges from 0.53 to 1.00. The bold row is the planning case used in Appendix A.5 and the owner review. It is conservative: m = 0.10 lies above the likely range, and at m = 0.05 the same R̄ and ρ give 0.99.
- **Comparison with the earlier rule.** Under UB₉₅ ≤ 0.05 alone, the bold planning case passes only 0.55 of the time. Over the full grid it passes 0.41–0.93 at m = 0.05 and 0.22–0.74 at m ≥ 0.10, and three controls must all pass.
- **At an inflation of exactly 0.05,** P(F2) ≤ 0.50 and P(F2-kill) = 0.017 per control, which is ≤ 0.05 over three controls.
- **Small counts.** With ΣV < 10 in either arm the delta method is unreliable, so a whole-world resampling bound is used instead (§K.4).

---

## Appendix B. Machine-readable outcome logic

```yaml
order: [VOID_BENCHMARK, KILL_LEAK, KILL_REPRO, KILL_FUTILITY, KILL, CONTINUE, AMBIGUOUS]
preservation: completed KILL-type outcomes are never converted to VOID_BENCHMARK, except by
  [TH_attributed_critical_leak_in_S_GEN_owned_code, TH_attributed_repro_mismatch_in_generation_oracle_replication_or_scoring,
   generator_self_check_failure_rate > 0.02]      # detected before campaign close; later findings follow post_campaign_close_audit
controls:
  default_literal: [A1, A2, A3, A4]          # owner decision 2, default
  recommended: [A1, A2, A3]                  # plus memory non-inferiority and memory harm vs A4
MEI: 0.3                                     # OPEN, owner decision 4
SE(A5 contrasts): max(iid, Newey-West lag 4 Bartlett, world order); t with N-1 df
beats(c): LB95_t(mean(TRK_A5 - TRK_c)) > 0 AND mean(TRK_A5 - TRK_c) >= MEI
fails(c): UB98.75_t(mean(TRK_A5 - TRK_c)) < MEI
memory_noninferior (recommended only): LB95_t(mean(TRK_A5 - TRK_A4)) > -MEI
memory_harm (recommended only): UB98.75_t(mean(TRK_A5 - TRK_A4)) < -MEI
TRK_A3_credit: requires harness as-if confirmation (Holm within A3 batch) AND replication
F1: ClopperPearson_UB95(count_w(V_val_A5_w >= 1), n_worlds) <= 0.10     # 75 worlds: x <= 2
F1_kill: ClopperPearson_LB95(count_w(V_val_A5_w >= 1), n_worlds) > 0.10 # 75 worlds: x >= 13
F2: all c in [A1, A2, A4]: est(mFDR_asr_A5 - mFDR_asr_c) <= 0.05 AND UB95(mFDR_asr_A5 - mFDR_asr_c) <= 0.10
    (bound: delta method, world-clustered; whole-world resampling if sum V_asr < 10 in either arm)
    (if sum R_asr_c < 20: m_c := 0.05, i.e. est(mFDR_asr_A5) <= 0.10 AND UB95(mFDR_asr_A5) <= 0.15)
F2_kill: any c in [A1, A2, A4]: LB98.33(mFDR_asr_A5 - mFDR_asr_c) > 0.05
    (if sum R_asr_c < 20: LB98.33(mFDR_asr_A5) > 0.10)
VOID_BENCHMARK_always:     # events detected before campaign close (§K.8); later findings follow post_campaign_close_audit
  - TH_attributed_critical_leak in S-GEN-owned code
  - TH_attributed_repro_mismatch in generation, oracle, replication or scoring
  - generator_self_check_failure_rate > 0.02 (of worlds)
VOID_BENCHMARK_unless_KILL_type_outcome:     # rule 1(b): never replaces KILL, KILL_LEAK, KILL_REPRO or KILL_FUTILITY
  - harness_error_rate > 0.02 (pooled or any of A1-A5)
  - INVALID_world_run_rate > 0.02 (pooled or any arm)
  - TH_attributed_critical_leak or repro_mismatch in agent runner, tool wrappers or relay
  - MRS_revoked_before_campaign_close_and_rerun_declined
  - amendment_after_C2_eval     # §S item 4
VOID_BENCHMARK_before_C2_eval:
  - a second calibration_before_C2_eval failure (any item, at EK-B1 or the post-tuning gate, once the single amendment has been used)
  - A0_metadata_leak_at_post_tuning_gate: LB95(A0_AUC_mechanism_component) > 0.60 OR LB95(A0_AUC_trap) > 0.60   # development worlds; one failure; not amendable
calibration_before_C2_eval (EK-B1 and post-tuning gate; ledgered pass/fail; evaluation-world values are diagnostics only):
  - ORC_in_family_coverage >= 0.80
  - 0.8 * E[J] * (ORC_cov - A1_cov) >= 2 * MEI
  - ORC_A_out_of_family_coverage >= 0.5
  - ORC_A_cov_oof - A1_cov_oof >= 0.25
post_campaign_close_audit: SUT (including unattributable, per the §K.5 map) -> KILL_LEAK or KILL_REPRO; TH -> CONTINUE withdrawn ("not established"), every other outcome unchanged;
  never converts KILL or AMBIGUOUS to VOID_BENCHMARK; triggers no rerun
KILL_LEAK: SUT_attributed_critical_leak in any world-run whose failed boundary is SUT
KILL_REPRO: SUT_attributed_verdict_level_mismatch
KILL_FUTILITY: interim(n=20 worlds): UB95_t15(mean(TRK_A5 - TRK_A1)) < MEI   # default; UB80 alternative
KILL_if_any: [any(fails(c) for c in controls), F1_kill, F2_kill, memory_harm (recommended only)]
CONTINUE_if_all: [all(beats(c) for c in controls), F1, F2, zero_critical_leakage, repro_gate, memory_noninferior (recommended only)]
AMBIGUOUS: otherwise; final (no extension)
second_VOID_from_C2_eval_or_second_abort_of_stage: Experiment 2 closes as VOID
mandatory_caveat: "Synthetic knowledge-creation benchmark on generator family 𝒢₂ and its sealed annex only; truth is predictive, not causal; no market data were used; the referee passed only the minimum trustworthy-referee subset and is not certified; this is not evidence of tradable alpha, real-data robustness or willingness to pay."
```

---

## Appendix C. Brief content rules (arms A0, A3–A5)

`[DECISION]` S-AGT writes the brief, the A0 prompt and every other S-AGT artefact within these rules. A separate session checks them against the forbidden list before freeze; the check is ledgered and hashed into F_H(2-eval) (§B.4).

**Allowed:**
- The task: produce validated knowledge about the outcome, in the §F schema, within the §H budget.
- The scoring principles: credit for true, replicated, non-duplicative claims; penalties for false claims; negative findings credited only under the §G.5 conditions.
- The DSL (§E), the claim schema (§F), the interfaces (§D.3) and the stage rules (§G).
- The definition of B* (§C.10) and of the κ₂ learner (§C.11), so that every arm, including A3, can compute skill against B*.
- Generic data facts: series may be revised; publication lags vary; known_at is authoritative; some series are predictive and many are not; some worlds contain no predictive series.

**Forbidden:**
- §C's mechanism types, prior ranges, trap archetypes, world mixture, catalogue composition, or segment lengths beyond those the interfaces reveal;
- anything about the annex;
- any development or evaluation world's content;
- any statement about which arms exist or how the other arms behave.

**Exception (§B.4).** A constant that matches §C is allowed in an S-SCR or S-AGT artefact only if the audit record cites a ledgered tuning run, and the feedback release (§B.4) from which the constant was chosen.

**The A0 prompt template (fixed).** It contains:
- the generic data facts;
- the §C.3 metadata fields;
- an instruction to rank every non-disclosed series by the likelihood that it predicts Y given B*;
- a strict, machine-parseable full-ranking output format.

**Arm differences.** For A3–A5, only tool availability differs (A3: raw files, no B-EVAL and no vault; A5: the memory tool). The task text is otherwise identical. A0 uses the fixed template above.
