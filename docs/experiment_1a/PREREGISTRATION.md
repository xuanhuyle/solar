# Experiment 1A: referee-validation pre-registration

| Field | Value |
|---|---|
| Document | `docs/experiment_1a/PREREGISTRATION.md` |
| Version | v0.3-draft (2026-09-24). Supersedes v0.2-draft (commit `e9aa4cc`). v0.3 changes **no criterion, threshold or outcome rule**. It updates status language, adds a note at §H.8 on the redefined Experiment 2 and the owner's clarification of the t0 objective, and adds log entries (CL-30 to CL-41, §L.3, §N). v0.2 superseded v0.1-draft after an adversarial review (§L.3). |
| Status | **DRAFT for owner review. Not frozen.** Committed for review in draft pull request #2 on the owner's instruction. No pre-registration hash exists yet; §I.2 defines how it is computed at freeze. |
| Branch | `experiment-1a-preregistration`, created from `main` at `406c92c`. That commit's tree is identical to the validated Experiment 0 tip `b2ab52c`; Experiment 0 run #11 ran on `3c4abb9`. |
| Companion | `docs/experiment_1a/OWNER_REVIEW.md` (decisions requested from the owner; v0.3 adds Part I, the minimum trustworthy-referee subset, and Part I.5, the subset and gate for Experiment 2-T0) |
| Related | `docs/experiment_2/PREREGISTRATION.md` and `docs/experiment_2/OWNER_REVIEW.md` (the redefined Experiment 2; see the §H.8 v0.3 note) |
| Experiment 1B status | **`BLOCKED_BY_ACCESS`** (§0.4) |

---

## 0. How to read this document

### 0.1 Authorization boundary

This task authorizes documentation only. `[DECISION]`

**Not done in this task:**
- no implementation, and no executable experiment code;
- no simulation;
- no seeds created or revealed;
- no new dependencies;
- no external data downloads;
- no changes to Experiment 0, `solarbench/`, `tests/` or `.github/`;
- no commit, tag, push or pull request.

**The only computations performed** were exact-binomial arithmetic for the operating characteristics (Appendix A) and arithmetic for the compute formula (§K.2). They ran in memory, use no randomness, and wrote no files. The formulas are given so anyone can re-derive the numbers. `[DECISION]`

**Implementation may begin only after the owner has approved and frozen this pre-registration (§N).** `[DECISION]`

**Status note (v0.3).** The list above records the boundary of the original drafting task. Later instructions from the owner, on 2026-09-23:
- v0.2 was committed (`e9aa4cc`) and pushed to draft pull request #2, on the owner's instruction;
- v0.3 is committed to the same pull request, on the owner's instruction redefining Experiment 2.

That instruction (redefining Experiment 2) governs only the relation between 1A and Experiment 2 (§H.8 v0.3 note; CL-30 to CL-38 and CL-41) and changes no 1A criterion.

The owner's later clarification of the same day (the t0 research-loop objective) states that the core is an AI researcher using t0's covariate capabilities, that the immediate milestone is one bounded, reproducible, independently confirmed t0 finding followed by an investigation that builds on it, and that full referee certification is a later objective. It changes no 1A criterion either. The mismatches it reveals are logged as CL-39 and CL-40, and the parts of 1A needed for that milestone are listed in `OWNER_REVIEW.md` Part I.5. Nothing is frozen, P_H is not computed, and nothing is implemented. The v0.3 edits involved no computation.

### 0.2 Labels

| Label | Meaning |
|---|---|
| `[DECISION]` | A pre-registered choice. Changing it after freeze requires an amendment (§N). |
| `[INFERENCE]` | Reasoned, not measured or sourced. It may be wrong, and it is never used as evidence. |
| `[ASSUMPTION]` | A premise the design relies on. If it is false, the stated consequence follows. |
| `[OPEN]` | Unresolved: it needs an owner decision (`OWNER_REVIEW.md`) or a lean-build measurement (§K.1). |

**No experimental results exist.** Simulation figures in earlier decision memos (labelled "SIM" there) were never saved: there is no code, parameter set or seed. They are cited only as unreproducible motivation, never as evidence. `[DECISION]`

### 0.3 Sources and precedence

When sources conflict, the higher-ranked one wins, and every material conflict is recorded in §L rather than resolved silently. `[DECISION]`

| Rank | Source | Role |
|---|---|---|
| 1 | Owner instruction of 2026-09-23 on drafting the 1A pre-registration | The most recent explicit decision: scope, authorization boundary, contemplated sample sizes, 1B = `BLOCKED_BY_ACCESS` |
| 2 | Experiment 1 decision memo v2, condensed (`experiment1_decision_memo.md`, session scratchpad, 2026-09-23, post-critic) | Authoritative framing. Sources for §7 threats, §8A, §10 guarantee classes, §15 architecture, §16 budget, §17 R1–R7 |
| 3 | Experiment 1 decision memo, full technical version with its v2 addendum (`experiment1_decision_memo_full.md`) | Shared definitions: §8.4–8.8, §8.11, §8.15, §8.25, §10.3, and the 34-row threat model in §7 |
| 4 | Experiment 0 `README.md` and the run #11 outputs | Lessons only |
| 5 | `referee_research.txt` (research digests) | Design rationale only. UNVERIFIED and SIM items are never evidence |

The memos in ranks 2–3 live in the session scratchpad, not in this repository. This document is written to be self-contained. `[DECISION]`

### 0.4 Experiment 1B status

**Experiment 1B (the GB/Elexon real-data workload) is `BLOCKED_BY_ACCESS`.** Elexon, IRIS and NESO could not be reached from the drafting environment. `[DECISION]`

- This is **not** a scientific failure. It says nothing about the referee or about GB markets.
- No endpoint was retried, no website was scraped, and no latest or definitive data was used as a substitute. No other market was substituted, and 1B has not been redesigned. The only 1B-related text here is labelled non-binding (§D.3, §L).
- **Experiment 1A needs no market data. Elexon is irrelevant to every criterion in this document.**

### 0.5 Notation and glossary

| Term | Definition |
|---|---|
| SP, s | Half-hour settlement period, identified by its UTC start time; `s_end = s + 30 min` |
| D(s) | Local (Europe/London) settlement date of s. A date has 46, 48 or 50 SPs |
| h | Forecast horizon, 2 h (4 SPs). The origin for target s is t(s) = s − 2 h |
| known_at | The earliest time a row may be used. A row is admissible at t iff `known_at ≤ t` (inclusive; margin 0 in 1A; §C.6) |
| B | The baseline information set, owned by the referee (§C.7) |
| candidate, X | A synthetic covariate series offered to researchers (§C.8) |
| hypothesis, submission | §B.3 |
| z | The transformed target, z = asinh(Y/c), with c = 1 in 1A |
| T_c | Campaign quantile set: {0.10, 0.25, 0.50, 0.75, 0.90} |
| ℓ(q⃗, z) | Mean pinball loss over T_c: (1/5) Σ_τ (1{z < q_τ} − τ)(q_τ − z) |
| d_D | Daily differential: the mean over scored s ∈ D of ℓ(q⃗^B_s, z_s) − ℓ(q⃗^H_s, z_s). Positive means H helped |
| 𝔉_s | Generator filtration for SP s: the σ-field generated by every primitive draw of the world **except** the innovations ε_{s'} for s' ≥ s. Primitive draws are listed in §C.3–C.8. Quantities derived from ε_{s'} with s' ≥ s are not 𝔉_s-measurable (z, Y¹, Y², X17, X18 at s'). 𝔉_s grows with s |
| c_s | Conditional loss differential: E[ℓ(q⃗^B_s, z_s) − ℓ(q⃗^H_s, z_s) \| 𝔉_s]. Computed in closed form (§C.9), because the as-of contract makes every forecast for s 𝔉_s-measurable |
| θ̃ | Ground-truth skill of a tested hypothesis: class-specific (§C.9) |
| θ | Planted, design-level oracle skill (§C.9) |
| false PASS | A PASS whose class-specific ground truth is ≤ ε_θ (§C.9) |
| world | One synthetic realisation from one derived seed |
| run | One (world, stand-in or arm, k) execution. It is its own organisation with fresh vaults and ledger (§B.1) |
| cell | One (class × arm × k) combination in R4 |
| κ_1A | Campaign configuration (§C.10). Certification applies to κ_1A only |
| 𝒢_1A | Generator family (§C). Certification applies to 𝒢_1A only |
| TCB | Trusted computing base (§B.2) |
| TH | Test harness (§B.2) |
| CP bound | One-sided Clopper–Pearson bound at the stated confidence (Appendix A) |

---

## A. Research question and falsifiable claim

### A.1 Question

Does the referee deliver its pre-declared statistical, point-in-time, security and reproducibility guarantees on synthetic known-answer worlds, including under the adaptive attacks specified here? `[DECISION]`

### A.2 Falsifiable claim C-1A

Under configuration κ_1A, generator family 𝒢_1A and isolation configuration ι_1A (§B.2):

1. **Size (R1).** Each offered guarantee class (G1, G2, G3) keeps the per-world probability of at least one false PASS under honest use at or below the R1 bound.
2. **Power and correctness (R2).**
   - G1, with learner L and the fixed R2 batch, recovers a planted 10% effect in at least the R2-required share of worlds.
   - Its decisions agree with an independently written reference implementation.
   - G2 and G3 can PASS a planted 10% effect (liveness) and agree with the reference.
3. **Point-in-time leakage (R3).** The referee flags every leak class in ℒ, and flags margin-dependent skill.
4. **Adaptive attack (R4).** Each offered class keeps the per-world false-PASS probability at or below the R4 bound against every arm in 𝒜 at every certified k.
5. **Transcript invariance (R5).** Before closure, no byte released to the researcher side depends on the contents of a vault, or on forward data not yet released.
6. **Tamper resistance (R6).** Every planted vulnerability in 𝒱 is blocked and logged.
7. **Determinism (R7).** Outputs reproduce byte for byte.

Any criterion that fails under §G–§H falsifies the claim for the scope stated in §H. `[DECISION]`

### A.3 What 1A can establish

- That the referee, **as implemented under κ_1A and ι_1A**, has the stated operating characteristics on worlds drawn from 𝒢_1A, at the confidence stated for each criterion.
- That the attacks in 𝒜 break deliberately naive referees (the positive controls) but do not break the proposed referee within the certified scope.

### A.4 What 1A cannot establish

`[DECISION]`

1. That an AI researcher generates valuable hypotheses. That is Experiment 2's question.
2. That any market strategy is profitable. 1A has no economic gate (owner decision 6).
3. That the system works on Elexon or any other real data. 1B is `BLOCKED_BY_ACCESS`.
4. That quant firms will buy it. That is the commercial track's question (§K.3 is a gate, not a validation).
5. Resistance to attack classes not in 𝒜, or to vulnerability classes not in 𝒱 (for example, the candidate classes V9–V13 in §G.7 are untested).
6. Resistance to an adaptive LLM, unless an LLM red team is actually run under an amendment (§E.5).
7. Behaviour under any configuration other than κ_1A, including the 1B configuration and the LightGBM learner G, which is not run in 1A.
8. Behaviour on data-generating processes outside 𝒢_1A. Examples: latent (unpublished) regimes, lagged-target dynamics, cross-sectional targets, non-stationarity beyond regime switching. The v0.1 non-gating stress classes S-LAT and S-LAG are removed from 1A (§M, D2).
9. Safety of executing researcher-supplied model code. 1A accepts declarative specs only (§B.3).
10. Correctness of placebo gates or economic gates, which are not in the system under test.
11. G2 and G3 power beyond liveness at θ = 10%; power at θ ≤ 5% is reported, not certified.
12. Several vaults per organisation on one target, a baseline updated with accepted findings (v2 §2), and leakage from a retired vault's graded release or from G3 releases into a later vault. 1A tests one vault per class per run.
13. Side channels through co-residency, microarchitecture or filesystem metadata. These are untested; the certification holds only under isolation configuration ι_1A (§B.2), which is checked by conformance, not attacked.
14. Resistance to human operators beyond the ledger audit of CH13 (§F.2).
15. Calibration of the G1 and G2 tests exactly at θ̃ = 0. R1 measures the false-PASS frequency of the stand-ins' own choices only; the R1-B diagnostic (§G.2) is reported, not gating.

### A.5 Mandatory caveat

Every certified conclusion, dossier and evidence package must carry this sentence, verbatim: `[DECISION]`

> "Certified against the pre-registered scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher."

The caveat may be removed only after an LLM red-team campaign has been specified by amendment, run, and passed under rules at least as strict as R4.

---

## B. System under test

### B.1 Components

Nothing below exists yet. `[DECISION]`

| ID | Component | Responsibility | TCB | Tested by |
|---|---|---|---|---|
| B-SPEC | Canonical spec and hasher | Parses, validates and canonicalises submissions (§B.3). Rejects fields the researcher may not set. FP-N and FP-R use the same validator | Yes | R4 (AT5, AT6, AT12), R5 |
| B-REG | known_at registry | Holds per-source nominal schedules and the rule mapping row fields to known_at (§C.4a). The only place known_at is assigned | Yes | R3 (LK01, LK05, LK21, LK23), R6 (V6) |
| B-ASOF | As-of builder | The only path from rows to feature matrices (semantics in §C.8). Runs the point-in-time controls in §G.4.1 inline. Persists lineage per prediction | Yes | R3 |
| B-TGT | Target builder | Builds z from the first-published target row; asserts known_at > s_end | Yes | R3 |
| B-BASE | Baseline owner | Defines and fits B (§C.7). Submissions cannot change B | Yes | R4 (AT9), R3 (LK18) |
| B-LRN | Learner runner | The learner L under κ_1A (§C.10) | Yes | R2, R7 |
| B-VER | Loss and verdict engine | Losses, differentials, the G1/G2 test, Holm, α-spending, the G3 e-process, MARGIN-SENSITIVE reruns, and an emitted-statistic census | Yes | R1, R2, R4 |
| B-VAULT | Vault service | Holds the sealed set (§C.2a). Enforces single use or retirement, the response schedule (§D.2) and fixed-length responses | Yes | R1, R4, R5, R6 |
| B-LEDGER | Ledger | One append-only, hash-chained ledger L_run per run (§B.1a) | Yes | R4 (AT6), R6 (V3), R7 |
| B-SBX | Sandbox runner | Runs researcher and attacker processes under isolation configuration ι_1A (§B.2) | Boundary | R5, R6 |
| B-EVID | Evidence-package generator | Builds the graded package only after closure | Yes | R5 |
| B-SEED | Seed service | Checks ceremony commitments and derives seeds inside the trust domain (§I) | Yes | R6 (V8), R7 |
| B-AUDIT | Audit log (referee side) | Errors, tamper attempts and diagnostics; also the TCB-side monitor log for R6. Never readable from the sandbox | Yes | R6 |
| B-DISC | Discovery-zone service | Exploratory answers computed from data released to the discovery zone. Every output is stamped `EXPLORATORY` | No: no read, stat or list right on vault stores | R3 (LK13), R5 |

#### B.1a Runs, vault instances and ledger schema

`[DECISION]`
- **Runs.** Each run (world, stand-in or arm, k) is its own organisation, with fresh vault instances and its own ledger L_run. Arms therefore never interfere with one another through a shared vault.
- **Campaign ledger.** After all runs finish, the campaign ledger appends (run_id, head(L_run)) in lexicographic run_id order.
- **Pre-closure ledger entries** contain exactly these fields:
  - entry index, identity, class, vault_id, query or registration index;
  - hypothesis hash, submission hash;
  - a `NEAR_DUPLICATE` flag, computed from discovery data;
  - α_i, remaining budget, tick index;
  - status ∈ {RECEIPT, NOT-PASS, PASS}.
- **Vault-derived values stay sealed.** Statistics, error classes, MARGIN-SENSITIVE results and census counts go to B-VAULT's sealed store until closure. They enter no sandbox-visible field and no hash visible to the sandbox before closure.
- **What the sandbox sees** is its own entries' fields listed above. The chain hash is not visible before closure.
- **Released outcomes.** The ledger counts released outcomes per vault: the number of responses that are not the constant NOT-PASS. This is 1A's form of v2's "bits released" (§M, D38).

### B.2 Trust boundary and isolation configuration ι_1A

`[DECISION]`

**Inside the TCB:** B-SPEC, B-REG, B-ASOF, B-TGT, B-BASE, B-LRN, B-VER, B-VAULT, B-LEDGER, B-EVID, B-SEED, B-AUDIT, and the process boundary of B-SBX.

**Outside the TCB:**
- researcher and attacker processes;
- everything the sandbox writes;
- every human except the key-holding principal (§I.6).

**Test harness (TH).** Outside the SUT; trusted for ground truth only; kept independent of the SUT under §C.12. It comprises:
- the generator 𝒢_1A and the θ̃ oracle;
- the clean-room reference implementation;
- the campaign orchestrator;
- the mutant and injection library;
- the planted-vulnerability library, with its builds U_V;
- the FP-N naive referee and the broken-G1 referee;
- the R5 mutant referees;
- the sandbox-conformance script.

**Isolation configuration ι_1A** (certification campaign):
- B-SBX runs in its own user, PID, mount, IPC and network namespaces.
- It uses CPU cores that share no SMT sibling with TCB processes.
- /proc is mounted `hidepid=2`, and no host-wide /proc or /sys/fs/cgroup file is visible.
- The mount namespace holds only:
  - a read-only, size-padded discovery bundle;
  - a private fixed-size tmpfs.

  No TCB path exists in it (lookups return ENOENT).
- The only channel between the two sides is the tick-released queue.
- A TH conformance script, whose hash is in F_H(cert), asserts all of the above before every run. A failed assertion is a harness error.

**Scope of ι_1A.** Conformance is checked, not attacked. Co-residency, microarchitectural and filesystem-metadata channels are **not tested** in 1A (§A.4 item 13).

**Interfaces** (declarative):

| Call | Returns |
|---|---|
| `discover(spec)` | exploratory report |
| `submit_g1(batch)` | fixed-length receipt |
| `query_g2(vault_id, spec)` | PASS or NOT-PASS |
| `register_g3(spec)` | fixed-length receipt |
| `status_g3(registration_id)` | PASS or NOT-PASS on the daily tick |

Evidence packages are released only through B-EVID, after closure.

### B.3 Canonical hypothesis and submission

`[DECISION]`

- **Hypothesis fields:**
  - `spec_version = "1a-1"`;
  - `members`: either one {candidate ID, transform ∈ T1–T5} or a list of 2–99 hypothesis hashes;
  - `regime_restriction ∈ {all, R1, R2, R3}`.
- **Hypothesis hash:** SHA-256 of the RFC 8785 (JCS) serialisation of the hypothesis fields.
- **Submission fields:** `identity`, `class ∈ {G1, G2, G3}`, `vault_id`, plus the hypothesis. The submission hash is SHA-256 of JCS over {hypothesis hash, class, vault_id}.

  `identity` is recorded but excluded from both hashes, so the same hypothesis gets the same hash from every identity.
- **Ensembles.** An ensemble lists hypothesis hashes already recorded in the same run's ledger (discovery or vault). Its forecast is the equal-weight average of its members' cached quantiles, re-sorted per SP. No model is fitted.
- **Referee-owned settings** cannot appear in a submission:
  - baseline, loss, horizon, windows;
  - learner, hyperparameters;
  - seeds, tolerances, known_at margins;
  - test schedule.

  A submission with any unknown field is **invalid**. Invalid submissions are charged like valid ones:
  - G2 and G3: the standard NOT-PASS;
  - G1: rejected at submission by a structural check that reads no vault data, with a fixed-length rejection receipt that does not depend on the vault.
- **Near-duplicates.** A hypothesis whose discovery-zone quantile forecasts correlate above 0.99 with an earlier hypothesis in the same run (averaged over T_c) is flagged `NEAR_DUPLICATE`. It is charged in full, with no α discount. The flag is reported per R4 cell.

### B.4 Frozen interfaces and authorship

These interfaces are fixed by P_H at freeze. `[DECISION]`

1. **Row schema** (§C.4a).
2. **World file layout.** One file per source per world: rows sorted by (valid_start_utc, vintage_no), padded to a fixed byte length per source. A manifest lists paths and SHA-256.
3. **Cached-forecast array.** float64 of shape [hypothesis, scored SP, τ], plus an index file mapping hypothesis hashes to rows.
4. **SUT hook points.** Mutants, mutant referees and U_V builds are written as patches at these points, so the TH never needs SUT internals:
   - as-of admission predicate;
   - vintage selector;
   - join key;
   - scaler-fit window;
   - label admission;
   - cache key;
   - fingerprint;
   - evaluated-SP filter;
   - inference unit;
   - regime-restriction validator;
   - G3 registration filter;
   - response release;
   - error mapping;
   - ledger writer;
   - discovery data source.

**Authorship.** Three Claude Code sessions, each given only this pre-registration and §B.4:

| Session | Writes |
|---|---|
| **S-GEN** | The generator and θ̃ oracle; the calendar and parameter tables; the orchestrator; attackers and stand-ins; the mutant, injection and vulnerability libraries (as hook patches); the conformance script |
| **S-REF** | Every SUT component, plus the FP-N and broken-G1 referees (as SUT configurations) |
| **S-CLEAN** | The reference implementation (§G.3), written after the lean build. Its code is hashed and committed before any S-REF code is shown to the person or session operating R2 |

Lean-build code may be carried into certification only if this separation held during the lean build. `[DECISION]`

---

## C. Synthetic world generator 𝒢_1A

Every material degree of freedom is pre-registered (`[DECISION]`) or flagged `[OPEN]`. The generator belongs to the TH.

### C.0 Parameter table

`[DECISION]`

| Parameter | Value |
|---|---|
| Calendar anchor | Local date 2023-06-01 = day 0; Europe/London DST rule; committed static table (§C.1) |
| Regime spells | 15 + Geometric(p = 1/31) days on {0, 1, …}; next state uniform over the other two; initial state uniform |
| Regime publication | 21:00 local on day D − 1 for day D |
| μ_R, σ_R (R = 1, 2, 3) | (1.0, 1.3, 1.6), (0.6, 0.8, 1.1) |
| π_blk (local 4-hour blocks from 00:00) | (−0.3, −0.1, 0.2, 0.1, 0.3, −0.2) |
| a₁, a₂, a₃ | 0.4, −0.5, 0.3 |
| p1(k), local period index k | 0.8·sin(2π(k − 14)/48), evaluated on local clock time (on 46/50-SP days, k follows the local clock) |
| AR(1) coefficients φ | W1 0.98; W2 0.995; X01 0.99; X02–X09 per §C.8. Every process starts from a stationary draw at day 0 |
| V, ν | V_s i.i.d. N(0, 1); ν ~ N(0, 0.5²) |
| Revision delay Δ | 0 with probability 1 − π_R; else Uniform[0, 60] min; π = (0.05, 0.10, 0.40) |
| ε | (1 − J)·T/√3 + J·(2 + E). T ~ t₃ truncated to \|T\| ≤ 1000 by rejection (removed mass 2.2·10⁻⁹). J ~ Bernoulli(p_R), p = (0.002, 0.005, 0.03). E ~ Exponential(mean 1.5) |
| Y revision noise ζ | N(0, 0.1²) |
| Target missingness | 0.005 per SP in regimes 1–2; 0.015 in regime 3 |
| Candidate constructions | §C.8 |
| β, β_M | 0 in null worlds; calibrated by §C.9 in planted and margin-planted worlds |

### C.1 Calendar

- Half-hourly UTC SPs. Local settlement dates follow Europe/London: BST from the last Sunday of March at 01:00 UTC to the last Sunday of October at 01:00 UTC.
- A **committed static table** gives each day's date, SP count and the UTC start of each SP. It is generated once and committed in F_H(dev). Neither the generator nor the referee computes DST from runtime tzdata.
- **Self-check** (failure → CAMPAIGN-VOID):
  - every day has 46, 48 or 50 SPs;
  - no UTC start is duplicated;
  - the table's DST days match the rule.

`[DECISION]`

### C.2 Segments

Days are local days. `[DECISION]`, except where marked `[OPEN]`.

| Segment | G1/G2 worlds | G3 worlds | Use |
|---|---|---|---|
| Warm-up | days 0–181 (182) | days 0–181 | Training only |
| Discovery | days 182–546 (365) | days 182–546 | Discovery zone |
| Embargo | days 547–567 (21) | — | Unused. 21 d is 1B's value; 1A's longest feature lag is 1 day (T3) |
| Confirmation vault | days 568–1085 (518 = 37 × 14) | — | Sealed (§C.2a) |
| Forward | — | days 547 … 546 + L_P | Released to the discovery zone under §D.3 |

- **L_P is `[OPEN]`**; the default is 518 (owner decision 4).
- **G1, G2 and G3 never share a world.** Each class and each criterion stream has its own derived seeds (§I.5).

#### C.2a Sealed set (G1/G2 worlds)

`[DECISION]` The sealed set S_v comprises:
1. every generated row whose valid time falls in days 568–1085, for every series (Y¹, Y², W1, W2, V¹, V², A, R_D, X01–X20, missing-row markers, and every time field);
2. every artefact computed from such a row: refits whose training window intersects days 568–1085; all forecasts, losses and differentials for days ≥ 568; cache entries; B-AUDIT records; evidence packages.

S_v is written only to B-VAULT's store. B-DISC has its own forecast cache, filled only from refits whose training labels all have valid time ≤ day 546. The "cached quantile forecasts" that attackers use (§E.1) are discovery-zone forecasts only. Vault-day evaluation of ensembles happens inside B-VER.

### C.3 Regime process

- Regime R_D ∈ {1, 2, 3} per local day; regime 3 is "stressed". Spell law as in §C.0, so every spell is longer than 14 days and the mean spell is 45 days.
- The regime for day D is published at 21:00 local on D − 1. It is therefore known at every origin for every SP of D (the earliest origin for D is 22:00 local on D − 1). B includes it (§C.7).

`[DECISION]`

### C.4 Drivers and revisable source

| Series | Dynamics | Publication | In B |
|---|---|---|---|
| W1 | p1(k) + u1; u1 is AR(1), φ = 0.98 | exact, at s − 6 h | Yes |
| W2 | AR(1), φ = 0.995 | exact, at s − 6 h | Yes |
| V | i.i.d. N(0, 1). Independence keeps the B-oracle exactly linear | V¹ = V + ν at s − 6 h. V² = V at s − 2 h 30 min + Δ_s | Yes |

**Stress-correlated availability.** At t = s − 2 h, the revision V² is available iff Δ_s ≤ 30 min. A_s ∈ {0, 1} records availability, and P(A_s = 1 | r) = 1 − 0.5·π_r. `[DECISION]`

#### C.4a Row schema, recorder and known_at rule

`[DECISION]`

**Row fields** (every generated row):

| Field | Meaning |
|---|---|
| `source` | Source identifier |
| `series_key` | Series identifier |
| `valid_start_utc`, `valid_end_utc` | Valid period |
| `tag_time` | = `valid_start_utc` |
| `publish_time` | Publication time |
| `upload_time` | Upload time |
| `capture_time` | First-seen time (the synthetic recorder) |
| `vintage_no` | Vintage number |
| `gap_fill` | Gap-fill flag |
| `value` | float64; NaN iff `is_missing` |
| `is_missing` | Missing flag |

All times are int64 UTC seconds.

**Clean worlds:**
- publish_time = upload_time = the actual publication time given in §C.3–C.8 (for DP-2, s_end + Δ′).
- capture_time = upload_time + U{0 … 60} s, drawn once per row.
- The registry holds each source's **nominal** schedule separately.

**B-REG rule:**
- known_at = max(publish_time, upload_time);
- for rows with gap_fill = true, known_at = capture_time;
- capture_time is otherwise used only by the recorder cross-check (§G.4.1).

**Injected defects** (R3 only; magnitudes in §G.4) change these fields. Clean worlds contain none.

### C.5 Target

z_s = μ_R + π_blk(s) + a₁W1_s + a₂W2_s + a₃V_s + β·X01_s + β_M·X19_s·m_s + σ_R·ε_s, and Y_s = sinh(z_s), with c = 1. `[DECISION]`

- m_s = 1 if the X19 row for s is available at t(s), else 0 (§C.8).
- **Heavy tails, spikes and negative values** come from Y = sinh(z): spikes when J = 1, negative values when z < 0.
- **Generator self-check:** max |z| ≤ 700 in every world. `[DECISION]`
- **Target publication:**
  - The first-published target Y¹_s = Y_s has known_at = s_end + 20 min. **The target is Y¹.**
  - The revision Y²_s = Y_s + ζ_s has known_at = s_end + 5 days. Y revisions are pure noise given B.
  - Missing Y¹ rows are explicit, and those SPs are dropped identically for every arm.

  `[DECISION]`
- **c = 1** makes the referee's z identical to the generator's (§M, D1). `[DECISION]`

### C.6 known_at rule and margin perturbations

- **Admissibility:** known_at ≤ t (inclusive; margin 0). `[DECISION]`
- **MARGIN-SENSITIVE reruns** re-fit only the tested hypothesis's arm, with its candidates' rows shifted in turn by:
  - +15 min;
  - +1 h;
  - to the source's **next scheduled publication**: min{p in the nominal schedule : p > known_at}.

  B is unchanged. For ensembles, the shift applies to every member. `[DECISION]`

### C.7 Baseline B (owned by the referee)

B's features for target s at origin t: `[DECISION]`

1. **Cell structure.** An unpenalised global intercept; regime dummies for R2 and R3; a dummy for A = 0; and the interactions R2×(A = 0) and R3×(A = 0). Together these are 6 parameters spanning the 6 (regime, availability) cells.
2. **Local-block dummies**: 5, with [00–04) as reference.
3. **Drivers:** W1_s and W2_s.
4. **Revisable source:** V^latest_s·1{A_s = 1} and V^latest_s·1{A_s = 0}.
5. **Per source in B:** information age (t − known_at of the latest vintage used) and a missingness indicator.

**Minimum-rows rule.** Any dummy or interaction column with fewer than 20 rows in the training window is dropped and contributes 0 at forecast time. An unseen cell is therefore forecast at the reference level. `[DECISION]`

**B has no lagged-target features** (§M, D23). `[DECISION]`

**Oracle linearity** `[INFERENCE]`, derivation:
- Given B's information at t, z_s − m^B_s = a₃η·1{A = 0} + β·X01_s + σ_R·ε_s, where η ~ N(0, wω²) with w = 1/(1 + ω²), and X01_s ~ N(0, 1) is independent of B's information.
- m^B_s is linear in items 1–4.
- So every τ-quantile of z_s given B is linear in B's features with a cell-specific offset. The same holds for B + X01, without the β term.
- **Consequence.** L is correctly specified for both oracles. Its fit is consistent only for cells with at least 20 training rows. The TH reports the share of scored vault SPs that fall outside this condition.
  - From the regime law, about 13% of 91-day forecast periods follow a training window that is missing a regime. This is `[INFERENCE]`, computed exactly by dynamic programming from §C.0.

### C.8 Candidate library, as-of semantics and transforms

**Library.** Each world has M = 20 candidates, with IDs permuted per world (inside the trust domain) and padded file sizes. `[DECISION]`

| Slot | Kind | Construction | Publication (actual) | Status under the correct referee |
|---|---|---|---|---|
| X01 | Genuine slot | AR(1), φ = 0.99 | s − 3 h | Null if β = 0; genuine if β > 0 |
| X02–X09 | Correlated independent nulls | Two blocks of four; φ = (0.9, 0.99, 0.999, 0.99) within each block; within-block innovations equicorrelated at ρ = 0.5; independent of z | s − 3 h | Null |
| X10, X11 | Near-duplicates | X10 = 0.99·X02 + √(1 − 0.99²)·U, where U is an independent AR(1) with X02's φ; X11 likewise from X06 | s − 3 h | Null |
| X12–X14 | Redundant | W1 + N(0, 0.3²), W2 + N(0, 0.3²), V¹ + N(0, 0.3²) | s − 3 h | Null given B |
| X15, X16 | DP-1 (looks predictive against a weaker baseline) | 1{R_D = 3} + N(0, 0.5²); sin(2π·localhour/24) + N(0, 0.3²) | s − 3 h | Null given B; predictive only against a weaker B′ |
| X17, X18 | DP-2 (timing proxy) | σ_R·ε_s + N(0, 0.2²) | Nominal s − 2 h − 5 min; **actual s_end + Δ′**, Δ′ ~ U[10, 40] min in regimes 1–2 and U[10, 90] min in regime 3 | Never available at t; null. Leaks only if known_at is violated or the nominal schedule is trusted |
| X19, X20 | MB (margin-borderline) | AR(1), φ = 0.99 | s − 2 h − 5 min, plus a delay U[0, 20] min with probability 0.1 (regimes 1–2) or 0.5 (regime 3). So m_s = 1 with probability 0.925, 0.925 and 0.625 in regimes 1–3 | Null if β_M = 0. In margin-planted worlds X19 enters z and is legitimately informative, only because it is published 5 min before t |

**Identifiability.** IDs are permuted and padded so that no metadata reveals slot or world class. The design does **not** assume that slot or class is statistically unidentifiable: X01 can be identified from discovery data in planted worlds, and no guarantee depends on hiding it. `[DECISION]`

**As-of semantics** `[DECISION]`:
- x(s) as of t is the latest vintage of the row with valid period s among rows with known_at ≤ t; otherwise the value is missing. There is **no carry-forward**.
- Missing values are imputed with the median of non-missing values in the training window.
- Information age of a missing value = t − known_at of the series' latest row with known_at ≤ t.
- A column with no non-missing value in the training window is dropped. For example, DP-2 under the correct referee: its B+X model is then identical to B.

**Transforms**, computed on as-of values: `[DECISION]`

| ID | Transform |
|---|---|
| T1 | x(s) |
| T2 | x(s) − x(s − 2 SPs) |
| T3 | x(s) − x(s − 48 SPs) |
| T4 | sign(x(s)) |
| T5 | Rank within the training window, fitted in-window |

- T2 and T3 are missing if any input is missing.
- The features added to B are the transformed value, the candidate's missingness indicator and its information age.
- The single-hypothesis space is 20 candidates × 5 transforms (100 fitted models per world, plus B) × 4 regime restrictions, plus ensembles. Regime restrictions and ensembles need no new fits.

### C.9 Ground truth, estimand and calibration

**Closed-form expectations** `[DECISION]`. Given 𝔉_s, z_s = m^full_s + σ_R·ε_s, where m^full is 𝔉_s-measurable. For any forecast q:

E ρ_τ(z − q) = E(z − q)⁺ − (1 − τ)(E z − q)

- **t component:** E(z − q)⁺ is (σ_R/√3)·E(T − a)⁺ with a = √3(q − m)/σ_R. For t₃, E(T − a)⁺ = ((3 + a²)/2)·f₃(a) − a·(1 − F₃(a)), corrected for the truncation at |T| ≤ 1000 by subtracting both tail partial expectations and renormalising.
- **Spike component:** σ_R·E(2 + E − b)⁺ with b = (q − m)/σ_R, which equals 1.5·e^{−(b−2)/1.5} if b ≥ 2 and 3.5 − b otherwise.
- **Piecewise-linear integrands.** The unclipped differential ℓ^B − ℓ^H and the clipped G3 differential are piecewise-linear in z. Their expectations are exact sums of partial moments of z over the intervals between breakpoints.

**Ground truth by class** `[DECISION]`:
- **G1/G2.** Let 𝒟 be the used vault days (§D.1: complete blocks of 14 eligible days) and S_D the scored SPs of day D. Then

  θ̃(H) = (1/|𝒟|) Σ_{D∈𝒟} (1/|S_D|) Σ_{s∈S_D} c_s

  This is exactly the estimand of the test's mean of batch means. The SP-weighted θ̃_SP is reported alongside, together with the count of PASSes where the two differ in sign.
- **G3.** Σ_{i≤n} μ_i with μ_i = E[x_i | 𝔉_{s_i}] on the clipped, rescaled differential (§D.3), taken at the stopping index n. The unclipped θ̃ is reported.
- **Tie rule.** ε_θ = 10⁻⁶ × the mean over the tested window of E[ℓ(q⃗^B_s, z_s) | 𝔉_s] (and ×1/(2B_H) for G3). **A false PASS is a PASS with ground truth ≤ ε_θ.** PASSes with ε_θ < ground truth ≤ 10·ε_θ are reported separately.
- **Scope of computation.** Ground truth is computed for PASSes (to classify them), for the calibration gate, and for R1-B. It is not computed for all tested hypotheses.
- **Baseline-weakness metric** (reported, non-gating): the share of PASSes on generator-null hypotheses whose ground truth exceeds ε_θ.

**Design-level planted skill θ** `[DECISION]`:
- θ(β) = 1 − E[ℓ(oracle q⃗^{B+X01})] / E[ℓ(oracle q⃗^{B})], over T_c and the stationary law of the cells.
- Each expectation is Σ_cell π_cell·L_cell, with π_cell = (1/3)·P(A | r) and L_cell the expected pinball loss of the cell's residual law at its own quantiles.
- Cells whose residual includes a Gaussian term (η, or β·X01 in the B-oracle) need a one-dimensional integral of the closed form above over that Gaussian.
- β for each θ ∈ {1%, 2%, 3%, 5%, 10%} is found by bisection until |θ(β) − θ_target| ≤ 10⁻⁴. No seeds are involved.
- **Margin-planted class:** β_M is calibrated to θ_M = 10% over cells (r, a, m), with P(m = 1 | r) = 1 − q_r·15/20, where q_r is the MB delay probability (0.1, 0.1, 0.5). The oracle (B + X19) uses β_M·X19 only when m = 1. L(B + X19) is misspecified for this hypothesis, because missingness interacts with the cells; this is accepted and reported. **The lean build measures the margin-planted PASS rate on 100 development worlds and raises θ_M before freeze if it is below 0.97.**

**Calibration gate** (lean build, development ceremony) `[DECISION]`:
- **Worlds and hypotheses:** 200 null worlds and 200 planted worlds (θ = 10%); each of the 19 generator-null candidates separately, with T1 and T2, as a single hypothesis against L(B) on the vault window.
- **Pass (per candidate × transform):** the one-sided 95% upper t-bound of mean θ̃ across worlds is ≤ ε_θ, or every world has |θ̃| ≤ ε_θ.
- **Reported:** per candidate, the fraction of worlds with θ̃ > ε_θ and its CP upper bound.
- **On failure:** the candidate is reclassified as "learner-level informative" in the dossier, or the generator is amended before the certification freeze.

### C.10 Campaign configuration κ_1A

The whole configuration is subject to owner decision 1. `[OPEN]`

| Item | κ_1A (certified) | 1B configuration (not certified by 1A) |
|---|---|---|
| Origins | 8 per UTC day (00:00, 03:00, …, 21:00) | 48 |
| Quantiles | T_c (5 levels) | 19 levels |
| Learner L | Elastic-net quantile regression per τ (objective below). Continuous features standardised in-window; zero-variance and all-missing columns dropped. Solved as a convex QP with a deterministic single-threaded solver pinned at code freeze. Quantile crossings fixed by sorting | LASSO-QR with per-refit purged CV |
| L objective | Mean pinball + λ_τ·‖β_cont‖₁ + (γ/2)·‖β_all‖², with γ = 10⁻⁶ on every coefficient, including the intercept and dummies. The problem is strictly convex, so **the solution is unique** | — |
| λ_τ | Frozen from the development stream: grid {10⁻⁴, 3·10⁻⁴, 10⁻³, 3·10⁻³, 10⁻²}, chosen by mean out-of-sample pinball of L(B) on the discovery segments of 50 calibration worlds | Per-refit CV |
| Learner G (LightGBM) | **Not run in 1A** (§M, D6) | Corroborating learner |
| Training window | Rolling 182 days | Same |
| Refits | Quarterly: days 182 + 91j, j = 0…9. A training row is admitted iff its features were built as of its own origin and its label's known_at ≤ the refit time | Weekly |
| Inference unit | Local settlement day | Same |

**Certification applies only to κ_1A.** `[DECISION]`

### C.11 Hidden from attackers

Attackers never see:
- world class, β, β_M or θ;
- the slot identities;
- generator parameters beyond this document;
- world, vault, permutation or ceremony seeds.

`[DECISION]` Attacker seeds are the exception: §I.5.

### C.12 Independence of generator and scorer, and self-checks

`[DECISION]`

1. **Separation.** The generator and θ̃ oracle (TH) and the referee (SUT) are separate packages. An import-boundary test fails if either imports the other. Authorship follows §B.4.
2. **Different numerics.**
   - The reference implementation (S-CLEAN) uses a different QP algorithm from S-REF (for example interior-point against active-set).
   - The θ̃ oracle computes every closed-form term (§C.9) and cross-checks it with adaptive Gauss–Kronrod quadrature, with breakpoints at every kink. Tolerance per SP term: |closed − GK| ≤ 10⁻¹⁰ + 10⁻⁷·|closed|. The same rule applies to each L_cell used in calibration and to each Σμ_i at a G3 stopping time.
3. **Generator self-checks.** These run on every world (the KS check on the 200 calibration worlds and on the first 200 worlds of every certification stream). Any failure → CAMPAIGN-VOID.
   - the calendar invariants;
   - every regime spell ≥ 15 days;
   - max |z| ≤ 700;
   - candidate count = 20;
   - the calibrated β and β_M reproduce θ within 10⁻⁴;
   - the quadrature cross-check;
   - **SC-ε:** per regime, the Kolmogorov–Smirnov distance between the realised ε and the oracle CDF is ≤ 3.272/√n_r. This is the DKW bound at a false-alarm rate of 10⁻⁹ per check.
4. **SC-𝒲.** The TH independently derives the scored SP sets, used days, batch membership and B_H from the generator and the static calendar, and compares them with the SUT's. A mismatch is a **referee defect**: the world counts as X_w = 1 in R1/R4, and as a disagreement in R2.
5. **Residual common-mode risk** `[ASSUMPTION]`: numerical libraries shared by all three sessions, and a common model family behind all three sessions. The dossier states this risk; 1A cannot remove it.

---

## D. Guarantee classes

**Tested null, per class** `[DECISION]`:
- G1/G2: H0: θ̃(H) ≤ ε_θ (§C.9);
- G3: the clipped weak null (§D.3).

**α = 0.05** family-wise per vault or per registration set. SESOI is not used in 1A.

### D.1 G1: single-use sealed vault

| Item | Specification |
|---|---|
| Input | One batch of m ≤ 4 hypotheses per vault per run. A second batch from any identity is refused with a fixed-length receipt `[DECISION]` |
| Eligible days | Vault days with ≥ 1 scored SP, after `regime_restriction`, in chronological order `[DECISION]` |
| Batches | Consecutive blocks of 14 eligible days; the incomplete last block is dropped; n_b = ⌊eligible / 14⌋. With no restriction and no fully missing day, n_b = 37 `[DECISION]` |
| Statistic | b_j = mean of d_D over block j; T = √n_b·mean(b)/sd(b) (sd with divisor n_b − 1); p = 1 − F_{t, n_b − 1}(T) `[DECISION]` |
| Degenerate cases | p := 1 if n_b < 6, or max_D \|d_D\| ≤ 10⁻¹²·(1 + mean ℓ^B), or sd(b) ≤ 10⁻¹²·(1 + \|mean(b)\|) `[DECISION]` |
| Holm | Sort by p ascending, ties broken by hypothesis hash (lowercase hex, lexicographic). j* is the smallest rank with p_(j) > α/(m − j + 1). PASS exactly the ranks below j* (all of them if no such j exists). Adjusted p is reported: p̃_(j) = max_{i≤j} min(1, (m − i + 1)·p_(i)) `[DECISION]` |
| Before closure | A fixed-length receipt (vault ID, submission hashes, tick index) that does not depend on vault data `[DECISION]` |
| At closure | The full graded evidence package, once. The vault is consumed; later tests on it are exploratory only `[DECISION]` |
| Errors | Any TCB exception is mapped to p := 1 for the affected hypothesis and logged to B-AUDIT `[DECISION]` |
| Guarantee | FWER ≤ α per vault `[INFERENCE]`. Derivation: a false rejection of i implies the centred statistic T\*\*_i = √n_b·(mean(b) − θ̃_i)/sd(b) exceeds its critical value, so under (A2) Bonferroni gives FWER ≤ Σ α/m = α. Holm's step-down with the data-dependent null set is an `[ASSUMPTION]`, measured by R1 |
| Assumptions | (A1) hypotheses were chosen without access to S_v. (A2) T\*\* is approximately t_{n_b−1} under heavy tails and dependence. (A3) No other channel to S_v. (A4) Single use per vault `[ASSUMPTION]` |
| Invalidated by | Any read of S_v before submission; acceptance of a second batch; an R5 side channel |
| Positive control PC-G1 | Run against a **deliberately broken G1** (a separate SUT configuration) that allows vault reads before submission. A vault-snooping analyst evaluates all 100 single hypotheses (T1–T5, regime `all`) on the vault and submits the best one alone at α = 0.05. Fires iff x ≥ 73 of 400 null worlds (LB > 0.15) `[DECISION]` |

### D.2 G2: retire-on-first-PASS vault

| Item | Specification |
|---|---|
| Budget | K ∈ {10, 30, 100} queries per vault per run `[DECISION]` |
| α-spending | γ_i = 1/K, so α_i = 0.05/K `[DECISION]` |
| Test | The §D.1 single-hypothesis test (same batching and degenerate rules) at level α_i |
| Response schedule | A query submitted during tick q is answered **exactly at the boundary of tick q + 2**, and at no other tick. B-VAULT computes under a hard deadline of boundary(q + 2) − 5 s. On a miss it cancels the computation, releases the standard NOT-PASS (charged) and writes a B-AUDIT entry. Campaigns use a logical tick (the query index), which carries no timing evidence. Wall-clock ticks are 60 s (§G.6) `[DECISION]` |
| NOT-PASS | A byte-identical, fixed 256-byte payload: vault ID, query index, remaining budget, status, tick index. Nothing else `[DECISION]` |
| Errors | Invalid submissions, solver failures, NaNs and deadline misses all return the standard NOT-PASS and are charged; details go to B-AUDIT. The orchestrator never retries or restarts a referee call. A TCB exception that escapes B-VAULT is a **referee defect**: X_w = 1 in R1/R4, and a differing pair in R5 `[DECISION]` |
| Retirement | At the first PASS, or when the budget is exhausted. Then: `PASS` (if any), the evidence package, and the graded results of all queries `[DECISION]` |
| Guarantee | FWER ≤ Σ α_i = α per vault under arbitrary adaptivity `[INFERENCE]`. Derivation: until the first PASS, the released transcript equals the fixed all-NOT-PASS transcript, so the queries form a fixed sequence given pre-vault information; the union bound applies |
| Assumptions | (i) each query's test is valid conditional on all pre-vault information (measured by R1/R4 against θ̃). (ii) The vault is the only channel to S_v; R5 and R6 test channels within a vault only, and cross-vault leakage is untested (§A.4 item 12). (iii) At most one confirmed claim per vault `[ASSUMPTION]` |
| Invalidated by | Any pre-PASS byte that depends on S_v; a query accepted beyond K; per-identity budgets; any graded release before retirement |
| Positive control PC-G2 | The FP-N naive referee (graded feedback, α_i = 0.05/K; §M, D28) against AT2 at K = 30. Fires iff x ≥ 73 of 400 null worlds `[DECISION]` |

### D.3 G3: forward, anytime-valid

| Item | Specification |
|---|---|
| Registration slots | For every G3 stand-in, registration i ∈ {0, …, k − 1} happens at the end of forward day i·⌊L_P/k⌋. A stand-in chooses **what** to register at each slot, never **when**. α_i = 0.05/k `[DECISION]` |
| Release of forward data | A forward row is released to the discovery zone at the first daily release tick at or after its known_at. The daily release tick is local midnight `[DECISION]` |
| Evaluated SPs | Scored SPs whose origin t(s) is later than the registration time, up to the horizon (the end of the forward segment). An SP is skipped (not an increment) if Y¹_s is missing or its forecast cannot be produced at t(s). Skipping is 𝔉-predictable `[DECISION]` |
| Clipped increment | δ_s = clip(ℓ^B_s − ℓ^H_s, −B_H, B_H), where B_H is the 99th percentile of \|ℓ^B − ℓ^H\| over SPs admitted by `regime_restriction` in the 365 days before the registration, fixed at registration. x_s = δ_s/(2B_H) ∈ [−½, ½]. If B_H < 10⁻⁹, then x_s := 0 and the registration cannot PASS `[DECISION]` |
| Process | Λ = {0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8}. M^λ_n = exp(λ Σ_{i≤n} x_i − ψ_E(λ)·Σ_{i≤n}(x_i − x̂_{i−1})²), with ψ_E(λ) = −log(1 − λ) − λ, and x̂_{i−1} the running mean of past increments clipped to [−½, ½] (x̂_0 = 0). M_n = (1/9)·Σ_λ M^λ_n `[DECISION]` |
| PASS | At the first n with M_n ≥ 1/α_i. Monitoring stops at the first PASS or at the horizon. A daily PASS / NOT-PASS status is released on the daily tick `[DECISION]` |
| Tested null (clipped, weak) | H0^w: Σ_{i≤n} μ_i ≤ 0 at the stopping index, where μ_i = E[x_i \| 𝔉_{s_i}] `[DECISION]` |
| Claim text | "X improved the clipped pinball differential (clip ±B_H = ⟨value⟩, fixed at registration) on average over [first evaluated SP, stopping SP]; this is not a claim about unclipped pinball skill." `[DECISION]` |
| Order under κ_1A | Scored targets are 3 h apart. The previous target's label (known at s_prev_end + 20 min = s − 2 h 10 min) is known before the next forecast is issued (s − 2 h), so each x_i is 𝔉_{s_{i+1}}-measurable and no interleaved split is needed `[DECISION]` |
| Guarantee | P(PASS at n and Σ_{i≤n} μ_i ≤ 0) ≤ α_i per registration; FWER over registrations ≤ Σ α_i `[INFERENCE]`. **Self-contained derivation:** (1) *Elementary lemma:* for ξ ≥ −1 and λ ∈ [0, 1), exp(λξ − ψ_E(λ)ξ²) ≤ 1 + λξ. (2) With ξ_i = x_i − x̂_{i−1} ∈ [−1, 1], and x̂_{i−1}, μ_i both 𝔉_{s_i}-measurable: E[exp(λ(x_i − μ_i) − ψ_E(λ)ξ_i²) \| 𝔉_{s_i}] ≤ (1 + λ(μ_i − x̂_{i−1}))·e^{−λ(μ_i − x̂_{i−1})} ≤ 1. The centred process is therefore a non-negative supermartingale for each λ, and so is its mixture. (3) On {Σμ_i ≤ 0}, the uncentred M^λ_n ≤ the centred one, because λ ≥ 0. (4) Ville's inequality bounds the probability that the centred mixture ever reaches 1/α_i. The TH checks the lemma numerically on a grid (ξ ∈ [−1, 1], λ ∈ Λ) as a lean-build self-test |
| Ground truth | Σ_{i≤n} μ_i by closed form (§C.9). False PASS iff ≤ ε_θ/(2B_H). Reported, non-gating: unclipped θ̃ and the **clip-flip rate** (PASSes with clipped truth > 0 but unclipped θ̃ ≤ 0), with its CP upper bound |
| Assumptions | (i) Registration precedes evaluated forecasts (LK20). (ii) B_H uses pre-registration data only. (iii) Release follows the release rule above `[ASSUMPTION]` |
| Positive control PC-G3 | HA's G3 plan (k = 10, the same slots and hypotheses), with each registration monitored by a naive peeking t-test instead of the e-process. From 14 days after registration, at the end of each forward day, a one-sided t-test of the mean daily d since registration at α_i = 0.05/10; PASS at the first rejection. Ground truth is as for the SUT, with B_H computed as the SUT would. Fires iff x ≥ 51 of 400 null worlds (LB > 0.10) `[DECISION]` |
| Non-binding note for 1B | `[INFERENCE, not a 1A decision]` With 48 origins a day and a 20-min label lag, a split into ⌈(120 + 30 + 20)/30⌉ = 6 interleaved subsequences would be needed; that controls only per-subsequence weak nulls. v2 §10 says h (= 4). 1B's design is unchanged and remains `BLOCKED_BY_ACCESS` (§L) |

### D.4 Discovery zone (no guarantee)

- Queries are unrestricted, on released data only, with detailed numeric feedback. Every output is stamped `EXPLORATORY` and can never become a confirmed claim.
- The attacker discovery budget is 400 exploratory evaluations per run.

`[DECISION]`

---

## E. Researcher stand-ins and attackers

### E.1 Common rules

`[DECISION]`

- **Determinism.** Every stand-in is a deterministic function of its attacker seed (§I.5) and the transcript it receives. It runs in B-SBX, calls only the §B.2 interfaces, and sees only discovery-zone outputs and fixed-format responses.
- **Cached forecasts only.** Stand-ins act on cached discovery-zone quantile forecasts and never fit models. This is a stated scope limit.
- **Query budgets k ∈ {10, 30, 100}:**
  - G1: not applicable (one batch of ≤ 4 hypotheses);
  - G2: K = k;
  - G3: k slots per §D.3.

### E.2 Honest analyst (HA) and knowledge-free search (KF)

| ID | Algorithm |
|---|---|
| HA | Ranks the 100 single hypotheses (20 candidates × T1–T5, regime `all`) by a one-sided Newey–West t (lag 7) on discovery-zone daily d, ties broken by hypothesis hash. **G1:** submits the top 4 with distinct candidates. **G2 (R1: K = 30):** queries in rank order. **G3 (R1: k = 10):** at each slot, registers the highest-ranked hypothesis not yet registered, re-ranked on all data released before the slot |
| KF | Enumerates a fixed grammar: single hypotheses × regime restrictions × ensembles of 2–3 drawn from the discovery top 10. It uses a pseudo-random order fixed by the attacker seed, ranks by discovery score, and submits like HA with budget k. It is the control arm for a later "knowing adversary" |

### E.3 Attacker library 𝒜

| ID | Attacker | Algorithm (G2 form unless stated) | G1 | G2 | G3 |
|---|---|---|---|---|---|
| AT1 | Random submitter | Uniform random single hypotheses | ✓ | ✓ | ✓ |
| AT2 | Combination / boosting | k − 1 distinct random single hypotheses, then an ensemble as the k-th. Under FP-N: of the favourable ones (positive skill sign), capped at 99. Under FP-R: of all prior ones. Run under each feedback policy | — | ✓ | ✓ (ensemble registered at the last slot) |
| AT3 | Forking-paths sweeper | Spends the whole discovery budget over transforms × regimes × candidates × ensembles of ≤ 5; submits the best k (G1: the best 4) | ✓ | ✓ | ✓ |
| AT4 | Optional-stopping poller | G2: re-queries the same hypothesis (charged; identical result). G3: at each slot, re-registers the hypothesis from the previous slot (charged) and polls status daily | — | ✓ | ✓ |
| AT5 | Near-duplicate resubmitter | Correlated variants (X02 then X10; one candidate across T1–T3). G1: tries a second batch, which must be refused | ✓ | ✓ | ✓ |
| AT6 | Sybil | Two identities split the budget, each acting like AT3 with k/2. G1: identity 2 submits a second batch, which must be refused | ✓ | ✓ | ✓ |
| AT7 | Side-channel prober | Submits hypotheses likely to trigger vault-dependent behaviour: sign transforms of near-constant series; single-regime restrictions; ensembles of ≤ 5 extreme members. Records every released byte, length, tick index and error. Any variation is used as feedback, AT2-style | ✓ (receipts) | ✓ | ✓ |
| AT8 | Regime shopper | Regime restriction with the best discovery score, for the top candidates | ✓ | ✓ | ✓ |
| AT9 | Placebo / baseline shopper | DP-1 proxies (X15, X16) and T3 variants that look predictive against a weaker internal baseline B′ in the discovery zone | ✓ | ✓ | ✓ |
| AT10 | Variant splitter | All transform variants of the best discovery candidate as separate claims | ✓ | ✓ | ✓ |
| AT11 | known_at-margin exploiter | Hypotheses on X17–X20. Also submissions carrying margin, known_at or schedule fields (invalid; charged) | ✓ | ✓ | ✓ |
| AT12 | Seed / tolerance / configuration shopper | Submissions carrying seed, tolerance, λ, window, baseline, loss or horizon fields (invalid; charged). Identical resubmissions | ✓ | ✓ | ✓ |
| AT13 | Economic-score targeter | Ranks hypotheses by discovery-zone P&L under variant A (§E.4) and submits the top k | ✓ | ✓ | ✓ |
| AT14 | Tamperer | Scripted attempts against V1–V8 (R6 only) | R6 | R6 | R6 |

The R4 arms are AT1–AT13 plus KF. `[DECISION]`

### E.4 Synthetic economic rule (AT13 only)

- **Position:** sign(q^H_{0.5}(s) − y_ref(s)), where y_ref is the last first-published Y known at t.
- **Variant A:** settles at Y_s − y_ref(s). This is optimistic and leak-like.

The rule is a ranking signal only. There is no economic gate. `[DECISION]`

### E.5 LLM red team

- Not part of 1A unless an amendment specifies the model snapshot, the brief, the budgets, the sandbox, the world counts, and pass rules at least as strict as R4.
- Without it, the §A.5 caveat is mandatory (owner decision 8).

`[DECISION]`

---

## F. Feedback policies and output channels

### F.1 Policies

| Policy | Used for | Released |
|---|---|---|
| FP-N, naive | Positive controls only | Skill estimate, t, p, CI and a ladder label per query; natural timing; detailed errors |
| FP-R, referee | The system under test | **G1:** receipt, then the package at closure. **G2:** PASS / NOT-PASS until retirement, then graded results. **G3:** daily PASS / NOT-PASS per registration, then the package at stop or horizon |
| FP-D, discovery zone | All stand-ins | Unrestricted numeric output on released data, stamped `EXPLORATORY` |

FP-N and FP-R share B-SPEC. `[DECISION]`

### F.2 Output-channel inventory

`[DECISION]`

| # | Channel | Control | Tested by |
|---|---|---|---|
| CH1 | Verdict status | PASS / NOT-PASS only before closure | R4, R5 |
| CH2 | Payload content | Fixed schema; graded content only after closure | R5 |
| CH3 | Payload length | Fixed 256 bytes | R5 (M-P) |
| CH4 | Response timing | Tick q + 2 schedule with a hard deadline (§D.2) | R5 wall-clock rig (M-T) |
| CH5 | Errors and exceptions | Mapped to the standard response; details only in B-AUDIT | R5 (M-E) |
| CH6 | Exit codes | Constant for referee calls | R5 |
| CH7 | stdout / stderr visible to the researcher | The referee writes none | R5 |
| CH8 | Ledger view | The §B.1a pre-closure schema; no vault-derived value; no chain hash | R5 (M-L) |
| CH9 | Co-resident contention (CPU, LLC, /proc, PIDs) | ι_1A isolation | **Conformance check only; side-channel leakage not tested** |
| CH10 | Filesystem metadata (names, sizes, mtimes, statvfs) | ι_1A mount namespace; padded bundle | **Conformance check only; not tested** |
| CH11 | Caches | Segment-partitioned stores; no vault-derived cache is readable or stat-able outside B-VAULT (§C.2a) | R3 (LK13), R6 (V4 widened) |
| CH12 | Evidence release | Only at closure, retirement or stop | R5 |
| CH13 | Humans | No human action during certification except the ceremony steps; every human action is ledgered | Ledger audit (dossier §7); not attacked |
| CH14 | Discovery outputs | Computed only from released data | R3 (LK13), R5 (M-D) |
| CH15 | Rate limits and queue position | Not exposed; no dependence on vault data | R5 |
| CH16 | World metadata | Permuted IDs, fixed count, padded sizes, no class labels | R4 (AT7) |
| CH17 | Seeds | World, vault, permutation and ceremony seeds exist only in B-SEED. Attacker seeds are HMAC outputs with domain separation (a PRF), so revealing them reveals nothing about any other seed (§I.5) | R6 (V8) |
| CH18 | Network | None, by namespace | R6 (V7) |
| CH19 | Retirement and exhaustion notices | Deterministic given the PASS / NOT-PASS sequence | R5 |
| CH20 | G3 daily status | Daily tick; release rule (§D.3) | R5.G3 prefix pairs (M-G3) |
| CH21 | Receipts | Fixed length; hashes and ticks only | R5.G1 (M-R1), R5.G3 (M-R3) |

---

## G. Success criteria R1–R7

### G.1 Common definitions

`[DECISION]`

- **Units of inference.** Each criterion states its own unit:
  - world: R1, R2, R4;
  - trial: R3;
  - pair: R5;
  - attempt: R6;
  - output bundle: R7.
- **World types:**
  - The class world sets (streams `G1`, `G2`, `G3`) are **null worlds**: β = 0 and β_M = 0, so X01 and X19 are null candidates. R1, R4 and the positive controls use them. The positive controls use indices 0–399.
  - Planted worlds (β > 0) are used only in R2, R2-G2, R2-G3 and R3-marginclean.
  - Margin-planted worlds (β_M > 0) are used only in R3-margin.
  - The other R3 trials, and R5 and R6, use null worlds.
- **False PASS** is defined as in §C.9 (ground truth ≤ ε_θ). A PASS labelled MARGIN-SENSITIVE still counts as a PASS.
- **Harness errors.**
  - A harness error is a failure inside the TH: generator, oracle, orchestrator or conformance script.
  - A world that ends in a harness error counts as X_w = 1 in every affected cell. n stays at its pre-registered value, so thresholds are unchanged.
  - If the harness-error rate exceeds 1% in any cell or criterion, the result is CAMPAIGN-VOID (§H.1).
  - A TCB exception is never a harness error. It is either mapped to a standard response (§D) or, if it escapes, treated as a referee defect.
- **Repair** follows §H.7; **FRAGILE** follows §H.6.

### G.2 R1: size under honest use

```yaml
id: R1
applies_to: [G1, G2, G3]            # evaluated separately per offered class c
unit: world
worlds: null (beta = 0, beta_M = 0); stream c, indices 0..n-1
procedure: HA (§E.2): G1 batch of 4; G2 K = 30; G3 k = 10 slots
statistic: x_c = number of worlds with >= 1 false PASS
n: 2000 per class        # OPEN, owner decision 2 (recommended 2400)
null_H0: p_c >= 0.07
alternative_H1: p_c < 0.07
bound: {method: clopper_pearson, sided: one, conf: 0.95, type: upper}
pass: UB(x_c, n) <= 0.07      # x_c <= 120 (n=2000); <= 140 (2300); <= 147 (2400)
fail: UB(x_c, n) > 0.07
void: any §H.1 trigger in this criterion
repair: §H.7 (repair-round threshold: one-sided 99% CP; x_c <= 113 at n=2000, <= 139 at n=2400)
scope_on_fail: remove class c
reported_non_gating: R1-B diagnostic (below)
```

- **Operating characteristic at n = 2,000:** P(pass) = 0.980 at a true rate of 0.05, 0.524 at 0.06 and 0.041 at 0.07 (Appendix A). The 0.07 bound is v2's. `[DECISION]`
- **R1-B diagnostic** (reported, non-gating; no new worlds). For every hypothesis tested in R1 and R4, the TH computes the centred statistic:
  - G1/G2: T\*\* = √n_b·(mean(b) − θ̃)/sd(b);
  - G3: the centred mixture sup_n M'_n.

  It reports how often T\*\* exceeds its critical value, with the CP upper bound, split by α level. This addresses §A.4 item 15. `[DECISION]`

### G.3 R2: power, liveness and independent-implementation agreement

`[DECISION]`, except where marked `[OPEN]`.

**R2 (G1):**

```yaml
id: R2
applies_to: [G1]
unit: world (one planted G1 world; one Holm batch)
worlds: planted, theta in {0.01, 0.02, 0.03, 0.05, 0.10}; 500 per theta (streams R2-t01 .. R2-t10)
procedure: fixed batch {X01*T1, X02*T1, X12*T1, X15*T1} (genuine, null, redundant, DP-1) in a G1 vault, Holm alpha = 0.05; the SUT and the S-CLEAN reference both compute every t_i and the Holm decisions
statistics_per_world:
  recovered: SUT PASSes X01
  agreement: the SUT and the reference give X01 the same Holm decision, OR the world is borderline
  borderline: in either implementation, some hypothesis ranked at or above X01 has |t_i - t_crit_i| <= 0.01, or two such hypotheses have |t_a - t_b| <= 0.01
  t_crit_i: F^-1_{t, n_b - 1}(1 - alpha / (m - rank_i + 1))
null_H0: power_10 <= 0.979 OR pooled disagreement rate >= 0.0139
alternative_H1: power_10 > 0.979 AND pooled disagreement rate < 0.0139
bound: {method: clopper_pearson, sided: one, conf: 0.95}   # LB(495,500) = 0.9791; UB(25,2500) = 0.0139
pass: recovered at theta = 0.10 >= 495 of 500 AND disagreements pooled over all 2,500 worlds <= 25
fail: otherwise
void: S-CLEAN code not hashed and committed before S-REF code was shown to the R2 operator (clean-room breach); SC-W mismatches count as disagreements, not void
repair: §H.7
scope_on_fail: REFEREE-INVALID (no partial scope)
reported_non_gating: power curve per theta with the analytic noncentral-t prediction; |Delta t| distribution; learner-achieved skill vs theta
```

**R2-G2 and R2-G3 (liveness and agreement).** New relative to v2 (§M, D40). The thresholds are `[OPEN]`, owner decision 10.

```yaml
id: R2-G2 / R2-G3
unit: world
worlds: planted theta = 0.10; 500 G2 worlds (stream R2-G2); 500 G3 worlds (stream R2-G3)
procedure:
  R2-G2: K = 30; first query X01*T1 at alpha/30; the reference implements the same single-hypothesis test
  R2-G3: k = 10; registration of X01*T1 at slot 0 (alpha_0 = 0.005); the reference implements the same e-process
statistics:
  live: the SUT PASSes X01 (G2: on query 1; G3: by the horizon)
  disagree_G2: PASS status differs AND |t_sut - t_crit| > 0.01
  disagree_G3: PASS status or stopping SP differs AND |ln M_n - ln(1/alpha_0)| > 0.01 * ln(1/alpha_0) at both crossings
null_H0: live rate <= 0.5 OR disagreement rate >= 0.0209
alternative_H1: live rate > 0.5 AND disagreement rate < 0.0209
bound: {method: clopper_pearson, sided: one, conf: 0.95}   # LB(269,500) = 0.5002; UB(5,500) = 0.0209
pass: live >= 269 of 500 AND disagreements <= 5 of 500 (per class)
fail: otherwise
void: clean-room breach
repair: §H.7
scope_on_fail: remove G2 (R2-G2) or G3 (R2-G3) from the certified scope
```

**Operating characteristics** (Appendix A):
- Recovery: P(pass) = 0.616, 0.958 and 1.000 at true power 0.99, 0.995 and 0.999.
- Pooled agreement: P(pass) = 0.9995 at a disagreement rate of 0.005, and 0.553 at 0.01.
- The whole R2 rule: 0.958 at (power 0.995, disagreement 0.005).

**Interpretation of the thresholds.** The v2 thresholds are exactly one-sided 95% CP tests of the nulls stated above. **0.99 is the design target, not the null boundary.**

### G.4 R3: leak and margin-sensitivity detection

#### G.4.1 Referee point-in-time controls

B-ASOF and B-VER run these controls **inline, in every world-run of every criterion**, before any verdict is read. A world-run is **INVALID** iff any control fails. `[DECISION]`

| Control | Definition |
|---|---|
| TE (truncation equivalence) | On 200 origins per world (all DST-day origins; all origins within ±1 SP of any source's scheduled publication; the remainder chosen uniformly by index from the world seed), rebuild features after physically deleting rows whose registry known_at > t. Pass iff the feature bytes are identical. Boundary fixtures at t − 1 s, t and t + 1 s are included |
| PO (poisoning) | On the same origins, rewrite rows with known_at > t per source, in turn to 10⁶·x + 10⁶, NaN and −x. Pass iff the features are byte-identical |
| LP (label poisoning) | At one refit per world (index from the world seed), rewrite labels with known_at > refit time and refit L(B). Pass iff the coefficients are byte-identical |
| VS (vintage swap) | Swap vintages 1↔2 for rows whose vintage-2 known_at > t. Pass iff the features are byte-identical |
| TI (transform invariance) | At the same refit, rewrite all data with valid time after the refit time as x → 3x + 7. Pass iff every parameter fitted at that refit (scalers, medians, rank tables, coefficients) is byte-identical |
| CI (calendar and horizon) | The SUT's local period index and day assignment equal the static table's for every scored SP, and target start − origin = 120 min for every scored pair |
| LN (lineage) | Every feature value's known_at ≤ t |
| GA (gap-fill audit) | No gap-fill row has upload_time < capture_time − 60 s |
| PA (publishTime audit) | No source has ≥ 48 consecutive rows sharing one publish_time whose valid times span > 1 day, and no row has publish_time < upload_time − 1 day |
| RC (recorder cross-check) | No row has capture_time < upload_time − 60 s, and no registry known_at is earlier than the row's capture_time − 60 s (V6) |
| AB (access boundary) | Discovery outputs recomputed with the vault store replaced by NaN are byte-identical |
| AC (arm consistency) | The B columns in each B+X arm are byte-identical to the B arm's, and the scored-unit sets are identical across arms |
| UA (unit assertion) | The verdict engine's batches match §D.1 (daily units, 14-eligible-day blocks) |
| CK (cache key) | Changing the configuration identifier invalidates every cached forecast |
| FP (fingerprint) | The row fingerprint hashes (value, is_missing) and distinguishes NaN from every finite sentinel |
| RV (restriction validator) | Every regime restriction evaluated is in {all, R1, R2, R3} as published |
| RT (registration time) | Every G3-evaluated SP has t(s) > its registration time |
| DA (date assertion) | λ and every frozen parameter trace to development data only |

#### G.4.2 Leak catalogue ℒ

**Trial definition.** One null world of stream R3-LKnn, with the fixed G1 batch {X01·T1, X12·T1, X17·T1, X19·T1}, and the mutant or injection applied. Two exceptions:
- **LK14:** the fourth hypothesis is replaced by X15·T1 restricted to an outcome-defined day set (the top tercile of realised |d|).
- **LK20:** a null G3 world with one registration of X01·T1 at slot 0.

**Detection** means the trial's world-run ends INVALID. The designated control is reported. `[DECISION]`

| ID | Leak class and magnitude | Kind | Designated control | Threat rows (full memo §7) |
|---|---|---|---|---|
| LK01 | Admission predicate uses known_at − 30 min for every source | mutant | TE | 3, 9, 26 |
| LK02 | Vintage selector returns the highest vintage regardless of known_at | mutant | VS | 1, 5, 8, 13 |
| LK03 | Admission on tag_time ≤ t instead of known_at | mutant | TE | 3 |
| LK04 | 2% of V¹ rows in discovery and vault withheld and re-delivered as gap-fill rows: upload_time back-dated to the original schedule; capture_time = original + U{1…7} days | injection | GA | 21 |
| LK05 | W2 rows for days 0–90 delivered with one publish_time (2023-01-01T00:00Z) and upload_time = day 91 00:00 UTC | injection | PA | 4, 6 |
| LK06 | Feature built from Y¹ of the target SP | mutant | LN | 7, 15 |
| LK07 | Scalers, medians and rank tables fitted on the full sample | mutant | TI | 14 |
| LK08 | Local period computed with a fixed UTC offset (DST ignored) | mutant | CI | 11, 12 |
| LK09 | Label admission uses valid time instead of known_at | mutant | LP | 15 |
| LK10 | Deduplication keeps the last-uploaded row per valid period | mutant | VS | 5 |
| LK11 | λ selected on vault data | mutant | DA | 17 |
| LK12 | Imputation with the full-sample median | mutant | TI | 21 |
| LK13 | B-DISC reads rows and forecasts from the vault period | mutant | AB | 18, 20 |
| LK14 | Validator accepts outcome-defined restrictions | mutant | RV | 28 |
| LK15 | Cache key omits configuration and code identity | mutant | CK | 32 |
| LK16 | Fingerprint hashes NaN as −1 | mutant | FP | 32 |
| LK17 | Scored units dropped when X is missing, in the B+X arm only | mutant | AC | 22 |
| LK18 | The B+X arm uses V² where B uses V¹ | mutant | AC | 23 |
| LK19 | capture_time of V² shifted by −15 min over one 30-day discovery span | injection | RC | 31 |
| LK20 | G3 evaluates SPs with t(s) ≥ registration time − 1 day | mutant | RT | 34 |
| LK21 | Admission uses the nominal schedule instead of per-row known_at | mutant | TE | 9, 10 |
| LK22 | Test computed on half-hour units | mutant | UA | 16 |
| LK23 | Admission predicate known_at ≤ t + 60 s | mutant | TE (boundary fixtures) | 26 |

**Liveness.** A mutant or injection is live iff, in at least 1 of 5 liveness worlds with the detecting controls disabled, its designated artefact differs from the clean run. The artefacts are:
- forecasts: LK01–LK03, LK06–LK10, LK12, LK17, LK18, LK21, LK23;
- discovery outputs: LK13;
- spec acceptance: LK14;
- cache key: LK15;
- fingerprint: LK16;
- evaluated-SP set: LK20;
- test statistic: LK22;
- λ table: LK11;
- audit fields: LK04, LK05, LK19.

Liveness is established on development seeds before code freeze, and the results are included in F_H(cert). A mutant that is not live at C-cert is a harness error. `[DECISION]`

```yaml
id: R3
unit: trial (one world x one leak class), or one world for the clean and margin sets
trials: 100 per leak class (23 classes); 100 clean null worlds (stream R3-clean)
margin_planted: 100 margin-planted worlds (stream R3-margin); single hypothesis {X19*T1} alone in a G1 vault at alpha = 0.05
margin_clean: 100 planted worlds, theta = 0.10 (stream R3-marginclean); single hypothesis {X01*T1}
margin_procedure: each PASS is refitted with the three perturbations of §C.6 (H arm only) and re-tested at the same level
null_H0: detection probability per class <= 0.97, OR false-INVALID rate >= 0.03
alternative_H1: detection > 0.97 for every class AND false-INVALID rate < 0.03
bound: {method: clopper_pearson, sided: one, conf: 0.95}   # 100/100 -> LB 0.9705; 0/100 -> UB 0.0295
pass: every class detected in 100/100
      AND false_invalid == 0/100
      AND ms_detect == D_planted (PASS worlds in margin_planted; must be >= 90)
      AND ms_false <= floor(0.05 * D_clean) (PASS worlds in margin_clean; must be >= 90)
fail: otherwise
void: a non-live class at C-cert (harness error); D_planted < 90 or D_clean < 90 -> CAMPAIGN-VOID (§H.1)
repair: §H.7
scope_on_fail: REFEREE-INVALID (point-in-time control is foundational)
reported_non_gating: delay-vs-stress audit (per-source correlation of publication delay with regime)
```

- The margin rules are point-estimate rules. P(pass) = 0.985 at a true false-flag rate of 0.02 and 0.616 at 0.05 (D = 100); 0.965 and 0.530 at D = 90 (Appendix A).
- The lean build raises θ_M before freeze if the margin-planted PASS rate is below 0.97 (§C.9).

`[DECISION]`

### G.5 R4: adaptive-attack resistance

**Cell list.** `[DECISION]`; n per cell is `[OPEN]` (owner decision 2).

| Class | Arms | k | Cells |
|---|---|---|---|
| G1 | AT1, AT3, AT5, AT6, AT7, AT8, AT9, AT10, AT11, AT12, AT13, KF | — | 12 |
| G2 | AT1–AT13, KF | 10, 30, 100 | 42 |
| G3 | AT1–AT13, KF | 10, 30, 100 | 42 |
| **Total** | | | **96** |

```yaml
id: R4
unit: world
worlds: null; the class stream's indices 0..n-1 (shared with R1)
cell_statistic: x_cell = worlds with >= 1 false PASS for that arm, class and k
n_per_cell: 2000        # OPEN, owner decision 2 (recommended 2400)
null_H0_cell: p_cell >= 0.075
alternative_H1_cell: p_cell < 0.075
bound: {method: clopper_pearson, sided: one, conf: 0.95, type: upper}
pass_cell: UB(x_cell, n) <= 0.075 AND sut_error_rate_cell <= 0.001
           # x_cell <= 130 (2000), <= 151 (2300), <= 158 (2400)
           # sut_error_rate_cell = NOT-PASSes caused by SUT-internal errors on valid submissions (from B-AUDIT) / evaluations
fail_cell: UB(x_cell, n) > 0.075 OR sut_error_rate_cell > 0.001
decision_rule: intersection-union per (class, k): certified at k only if every cell with k' <= k passes
positive_controls:
  PC-G1: {stand_in: vault-snooping analyst vs broken G1, worlds: G1 indices 0..399, fire: x >= 73 (LB > 0.15)}
  PC-G2: {stand_in: AT2 under FP-N at K = 30, worlds: G2 indices 0..399, fire: x >= 73}
  PC-G3: {stand_in: HA-G3 plan with naive peeking t-test, worlds: G3 indices 0..399, fire: x >= 51 (LB > 0.10)}
void: a PC that does not fire -> CAMPAIGN-VOID (§H.1) with one permitted strengthening; a harness-error rate > 1% in a cell -> CAMPAIGN-VOID
repair: §H.7 (repair-round cells at one-sided 99% CP: x_cell <= 122 (2000) / 150 (2400))
scope_on_fail: a failure of cell (c, arm, k) removes (c, every k' >= k); an arm can never be scoped out
development_screens: lean build only, non-gating: n = 400; a screen fails iff LB(x, 400) > 0.05 (x >= 28)
```

**Error statements** `[INFERENCE, arithmetic]`:
- **Per (class, k) claim:** P(certifying a claim that contains a cell with p ≥ 0.075) ≤ 0.047.
- **Unions.** The OR in the minimum scope and the multi-class scope string are unions: worst case ≤ 0.091 for a false VALID-WITH-SCOPE label, and ≤ 0.134 for at least one false element in a three-class scope string.
- **Joint pass probability** (every cell and R1 exactly at α; cells treated as independent; Appendix A.2):

  | n | All 96 cells pass | Full scope (3 × R1 + 96 cells) | Below minimum scope (→ INVALID) |
  |---|---|---|---|
  | 2,000 | 0.882 | 0.830 | 0.038 |
  | 2,300 | 0.962 | 0.937 | 0.014 |
  | 2,400 | 0.974 | 0.956 | 0.010 |

**Flagged inconsistency (§L, CL-02).** v2's "≈ 0.95 for about 39 cells" does not hold for 96 cells. v2's n = 2,000 is retained as the default pending owner decision 2. `[DECISION]` for the retained default; `[OPEN]` for n.

### G.6 R5: transcript invariance

`[DECISION]` The thresholds for the wall-clock rig and the mutants are new (§M, D11 and D31).

**Pair construction** (all components):
- The two members share every generator draw with valid time before the split point, the ID permutation seed, the attacker seeds and all B-DISC state.
- Member B's data after the split point come from seed(`vault_resample` or `r5_split`, stream, i).
- **Compared items**, per tick, up to the first PASS in either member:
  1. every byte returned by every interface call, including `discover()`;
  2. the sandbox ledger view;
  3. stdout, stderr and exit codes delivered to the sandbox;
  4. retirement and exhaustion notices;
  5. receipts.

```yaml
id: R5
unit: pair (receipts, G2 transcripts, G3 prefixes); trial (poisoning); query (wall-clock rig)
components:
  R5.G1:
    pairs: 50 (stream R5-G1; 25 HA, 25 AT7); split at day 568
    mutant: M-R1 (receipt length depends on the sign of the first hypothesis's vault mean d); detected iff >= 1 pair differs
    pass: 50/50 pairs identical AND M-R1 detected
  R5.G2:
    pairs: 700 (50 x 14 arms, K = 100, stream R5-G2); split at day 568
    poisoning: 50 worlds (25 AT2, 25 AT7) x {NaN, +/-1e6 alternating, reversed day order}, applied to every vault-day series; control = the same world unpoisoned; compared up to the first PASS in either run
    wall_clock_rig: 10 pairs (5 AT7, 5 AT2) x 2 members x K = 10 queries = 200 queries; tick 60 s; answers at tick q+2; deadline boundary - 5 s
    wall_clock_rules:
      - paired tick indices identical
      - every release offset delta (sandbox CLOCK_MONOTONIC receipt minus scheduled boundary) in [0, 50 ms]
      - Spearman |rho(delta, |t_TH|)| <= 0.1826 over the 200 queries (two-sided alpha = 0.01), where t_TH is the vault t computed by the TH
      - paired sign test on delta_A - delta_B not significant (two-sided exact binomial, alpha = 0.01)
    mutants:
      M-P: payload length depends on sign(t); 50 pairs; detected iff >= 1 pair differs
      M-E: distinct error when a vault value used in the tested differential is NaN; the 50 NaN-poisoning trials vs control; detected iff >= 1 trial differs
      M-T: release delay = 10 ms x min(|t|, 3); wall-clock rig; detected iff the Spearman rule rejects
      M-L: ledger entry carries sign(t) before closure; 50 pairs; detected iff >= 1 pair differs
      M-D: B-DISC reads vault-period forecasts; 50 pairs; detected iff >= 1 pair differs
    pass: 700/700 pairs identical AND all poisoning trials invariant AND the wall-clock rules hold AND all five mutants detected
  R5.G3:
    pairs: 200 (50 each of AT2, AT4, AT7, KF at k = 30; stream R5-G3)
    split: members share every draw with known_at <= the end of forward day d*, where d* = 30 + (first 8 bytes of seed(r5_split, R5-G3, i) mod (L_P - 60)); later draws regenerated
    compared: every released item up to and including the day-d* release tick, truncated at the first PASS in either member
    mutants: M-G3 (status on day d computed from rows up to day d+1); M-R3 (registration receipt length depends on the next day's first outcome); each detected iff >= 1 pair differs
    pass: 200/200 prefixes identical AND both mutants detected
null_H0 (per component): per-pair difference probability >= UB(0, n_pairs)   # 0.058 (50), 0.0043 (700), 0.0149 (200)
alternative_H1: per-pair difference probability < that bound
bound: {method: clopper_pearson, sided: one, conf: 0.95}
fail(component): NOT pass(component)
void: any mutant undetected -> CAMPAIGN-VOID
repair: §H.7
scope_on_fail: R5.G1 -> remove G1 (the scope falls below the minimum, so REFEREE-INVALID); R5.G2 -> remove G2; R5.G3 -> remove G3
```

### G.7 R6: tamper resistance (known classes)

`[DECISION]`

| V | Planted vulnerability | Type |
|---|---|---|
| V1 | Editable referee test file | write |
| V2 | Writable time-limit configuration | write |
| V3 | Writable copy of the ledger | write |
| V4 | Readable target, vault or vault-derived file (forecast, differential or refit cache) | read |
| V5 | Stale latest-vintage cache: V5r (read) and V5w (write) | read / write |
| V6 | Wrong known_at entry in the registry (detected by RC against the synthetic recorder) | write |
| V7 | Network egress attempt from the sandbox | egress |
| V8 | Reading seeds, secrets or environment of the trust domain (the liveness check uses a world seed, not an attacker seed) | read |

```yaml
id: R6
unit: attempt
attempts: 20 scripted attempts per vulnerability (AT14), stream R6
blocked:
  read: the bytes and errno returned to AT14 are identical across two runs whose secret contents differ, and equal the pre-registered denial (ENOENT)
  write: no verdict, ledger entry or vault byte differs from the matched control, and the executed code and config hashes equal their F_H entries
  egress: a host-side TH capture sees zero packets from the sandbox network namespace
logged: an entry written by a TCB-side monitor (seccomp user-notify, LSM audit or netns firewall log) into B-AUDIT, with identity, V class and syscall, within one tick of the attempt
liveness: in build U_V (the same code with only V's control disabled, listed per V in F_H), AT14 succeeds in 20/20 attempts; otherwise V is not live
null_H0: per-attempt block-and-log rate <= 0.86
alternative_H1: rate > 0.86
bound: {method: clopper_pearson, sided: one, conf: 0.95}   # 20/20 -> LB 0.861
pass: every V: blocked == 20 AND logged == 20
fail: otherwise
void: a non-live V -> CAMPAIGN-VOID
repair: §H.7
scope_on_fail: REFEREE-INVALID (the security boundary is foundational)
scope_statement: "known vulnerability classes V1-V8 only"
untested_candidates (listed in §A.4 item 5): V9 other caches; V10 referee /proc entries; V11 core dumps; V12 path traversal; V13 a readable B-AUDIT or TH ground-truth store
```

R6 is a functional test of known classes, not a rate estimate. `[DECISION]`

### G.8 R7: determinism and reproducibility

```yaml
id: R7
unit: output bundle per world-run (verdict file, serialized gating statistics, evidence-package bytes, head(L_run))
subset: OPEN (owner decision 3). Default: 10% of each stream, selected after campaign close (§I.7); n = ceil(0.10 * N_stream), e.g. 200 of 2,000
builds: two clean builds from the lock file, on the same OS image digest and CPU architecture (x86-64)
null_H0: the non-reproducing fraction f >= UB(0, n)     # 0.0149 at n = 200
alternative_H1: f < UB(0, n)
bound: {method: clopper_pearson, sided: one, conf: 0.95}
pass: 0 differing bundles; the campaign ledger recomputed from the stored heads is identical
fail: any differing byte
void: a build fails for environmental reasons -> CAMPAIGN-VOID (operator-inducible: the §I.4 abort rule applies)
repair: §H.7
scope_on_fail: REFEREE-INVALID
cross_architecture_rerun: mandatory on the same subset (aarch64, image digest in F_H); differences are handled by the §H.6 FRAGILE rule
```

`[DECISION]`

### G.9 Sample-size summary

| Criterion | Worlds, trials or pairs (n = 2,000 default) |
|---|---|
| R1 + R4 + PCs | 3 class streams × 2,000 null worlds (2,400 under owner decision 2); PCs on indices 0–399 |
| R2 | 2,500 planted G1 worlds |
| R2-G2, R2-G3 | 500 + 500 planted worlds |
| R3 | 23 × 100 trials + 100 clean + 100 margin-planted + 100 margin-clean |
| R5 | G1: 50 pairs. G2: 700 pairs + 150 poisoning trials + 200 wall-clock queries + mutants (M-P, M-L, M-D on 50 pairs each; M-E on the NaN-poisoning trials; M-T in the wall-clock rig). G3: 200 prefix pairs + mutants (M-G3, M-R3) |
| R6 | 8 × 20 attempts (+ U_V liveness) |
| R7 | 10% of every stream (default), plus the same subset on aarch64 |

---

## H. Outcome mapping

### H.1 CAMPAIGN-VOID

`[DECISION]` Triggers:
- a generator self-check fails (§C.12);
- the harness-error rate exceeds 1% in any cell or criterion;
- an R2 clean-room breach;
- an R3 class that is not live, or D_planted < 90, or D_clean < 90;
- an R6 V that is not live;
- an R5 mutant goes undetected;
- an R7 environment failure;
- a positive control does not fire (after one permitted strengthening, see below);
- any amendment after C-cert;
- an abort, per §I.4.

**Ordering.** The orchestrator computes the void triggers and ledgers them **before any R1 or R4 count is released to a human**.

**Completed results are preserved.** A criterion whose gating computation completed before a VOID event keeps its result, unless the void cause invalidates the worlds themselves (a generator self-check or the quadrature cross-check). **A completed FAIL is never erased by a VOID**, and it triggers §H.7.

**Positive-control failure.**
- A PC that does not fire → CAMPAIGN-VOID.
- One attacker strengthening is permitted, made by amendment, followed by a fresh full C-cert ceremony. It does not consume the repair round.
- If the same PC fails again, its class is UNCERTIFIABLE.
- UNCERTIFIABLE for G1, or for both G2 and G3, → CAMPAIGN-VOID (final).

**Consequence.**
- Fix the cause and hold a new C-cert ceremony; this does not consume the repair round.
- **After a second CAMPAIGN-VOID, 1A closes as CAMPAIGN-VOID** (no ladder rung). Experiment 2 then needs a new, approved 1A pre-registration that reaches VALID or VALID-WITH-SCOPE.

### H.2 Certified scope

`[DECISION]`
- **G1** is certified iff all of the following pass: R1.G1; PC-G1 fired; every G1 R4 cell; R5.G1.
- **G2** is certified up to K₂ = the largest k ∈ {10, 30, 100} such that all of the following pass: R1.G2; PC-G2 fired; R5.G2; R2-G2; every G2 cell with k′ ≤ k.
- **G3** is certified up to K₃, defined the same way with R1.G3, PC-G3, R5.G3, R2-G3 and the G3 cells.
- **An arm can never be scoped out.**
- **Minimum scope (v2):** G1, plus either G2 at k ≥ 30 or G3 at any certified k.

**Scope string:**

> "Certified scope: G1 [all 12 G1 arms]; G2 k ≤ K₂; G3 k ≤ K₃ (clipped-loss null); configuration κ_1A = ⟨hash⟩; generator family 𝒢_1A = ⟨hash⟩; isolation configuration ι_1A = ⟨hash⟩ (co-residency, microarchitectural and filesystem-metadata channels untested); vulnerability classes V1–V8 only. Certified against the pre-registered scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher."

### H.3 REFEREE-INVALID

REFEREE-INVALID iff the campaign is not CAMPAIGN-VOID, the repair decision is final (§H.7), and either:
- any of R2 (G1), R3, R6 or R7 fails; or
- the certified scope is below the minimum.

`[DECISION]`

### H.4 REFEREE-VALID-WITH-SCOPE

R2 (G1), R3, R6 and R7 pass; the scope contains the minimum; and the scope is not full. `[DECISION]`

### H.5 REFEREE-VALID

R2 (G1), R3, R6 and R7 pass, and the scope is full: G1, G2 at k ≤ 100, G3 at k ≤ 100. `[DECISION]`

### H.6 FRAGILE and MARGIN-SENSITIVE

`[DECISION]`

**FRAGILE** uses v2's "within 1% (relative) of the decision threshold". It is computed from the mandatory cross-architecture rerun, and the criterion is then evaluated with the conservative value:

| Quantity | FRAGILE when | Conservative value |
|---|---|---|
| t statistics | t_primary ≠ t_cross and \|t − t_crit\| ≤ 0.01·\|t_crit\| for either value | The value that gives NOT-PASS |
| e-process | \|ln M_n − ln(1/α_i)\| ≤ 0.01·ln(1/α_i) for either value | The value that gives NOT-PASS |
| Counts | x_primary ≠ x_cross and exactly one of the two is on the passing side | The value that fails the rule: the larger count for false-PASS counts; the smaller count for positive-control fires, R2 recoveries and R3 detections |

If the conservative evaluation changes the outcome, the conservatively resolved outcome is reported.

**MARGIN-SENSITIVE** is a claim-level label, not a campaign outcome:
- It applies iff the primary verdict is PASS and any §C.6 perturbation rerun gives NOT-PASS.
- It is released only at closure.
- It counts as a PASS in R1 and R4.
- It must travel with the claim.

### H.7 Repair

`[DECISION]`, except where marked `[OPEN]`.

- **Optional.** After any FAIL, the outcome is PROVISIONAL. Within 14 days, the owner either invokes repair or declines it, in a ledger entry. If the owner declines, the outcome is computed from the original results.
- **At most one repair round.**
- **Admissible** only if the repair diff changes at least one file in the failing criterion's committed dependency set (the component-to-criterion map in F_H(cert)).
- **Procedure:**
  1. commit the diff;
  2. append a ledger entry;
  3. hold a C-rep ceremony with fresh entropy (domain `rep1`);
  4. rerun only the criteria and cells whose dependency set intersects the diff, carrying every other result forward.
- **Repair-round thresholds** for R1 and R4 cells: one-sided 99% CP. `[OPEN]` (owner decision 2).

  | n | R1 | R4 cell |
  |---|---|---|
  | 2,000 | x ≤ 113 | x ≤ 122 |
  | 2,400 | x ≤ 139 | x ≤ 150 |

  Worst-case two-attempt false certification: ≤ 0.055 per R4 cell and ≤ 0.050 for R1 at n = 2,000; ≤ 0.055 and ≤ 0.058 at n = 2,400. With an unchanged 95% threshold, a failing-in-truth cell would be certified with probability up to 0.091.
- **Rerun results** replace the originals for the rerun criteria. Any FAIL in the repair round is final.

### H.8 Precedence, ladder and Experiment 2

**Precedence:** CAMPAIGN-VOID > REFEREE-INVALID > REFEREE-VALID-WITH-SCOPE > REFEREE-VALID. FRAGILE resolution is applied first. `[DECISION]`

**Mapping to the ladder in the Experiment 1 brief** (referee thesis only):
- REFEREE-INVALID = FAIL;
- VALID-WITH-SCOPE = INTERESTING;
- VALID = STRONG;
- CAMPAIGN-VOID = no rung.

PRODUCT SIGNAL is not decided by 1A. `[DECISION]`

| Outcome | Experiment 2 |
|---|---|
| REFEREE-VALID | May be specified **only by its own pre-registration with owner approval**, and may use only: (i) G1, G2 at k ≤ 100 and G3 at k ≤ 100; (ii) configuration κ_1A; (iii) declarative specs (researcher code needs a new sandbox certification); (iv) synthetic worlds from 𝒢_1A, plus forward data whose known_at is later than max(freeze, the researcher's knowledge vintage). Real historical data first needs a real-data point-in-time validation (1B or a successor). **An LLM red team and a knowing-adversary arm are mandatory.** Every claim carries the certified-scope string |
| REFEREE-VALID-WITH-SCOPE | The same, but only within the certified (class, k) set |
| REFEREE-INVALID | Not specified. A referee redesign needs a new 1A pre-registration and campaign |
| CAMPAIGN-VOID | Not specified or started (§H.1) |
| FRAGILE (flag) | Follow the conservatively resolved outcome |
| MARGIN-SENSITIVE (label) | No effect on gating; the label travels with the claim |

**Reopen rule (v2 R8)** `[DECISION]`. If any later audit, in Experiment 2 or elsewhere, finds a leak that the certified referee missed:
- the 1A outcome is reset to REFEREE-INVALID;
- Experiment 2 claims that depend on it are suspended.

**v0.3 note: relation to the redefined Experiment 2** `[OPEN: Experiment 2 owner decision 1]`. This note was added in v0.3; the text of §H.1–§H.8 above is unchanged.

1. **The redefinition.** On 2026-09-23 the owner redefined Experiment 2 as a blinded knowledge-creation benchmark (`docs/experiment_2/PREREGISTRATION.md`). It scores claims against concealed ground truth. The owner also asked for a minimum trustworthy-referee subset (MRS) to be distinguished from full institutional certification (`OWNER_REVIEW.md`, Part I).
2. **If Experiment 2 decision 1 is approved:**
   - the redefined Experiment 2 is gated by the MRS (Experiment 2 §B.3), not by a 1A outcome;
   - the table above, the last bullet of §H.1 and the reopen rule then govern **institutional use of certified guarantees**: any claim, product statement or evidence package that relies on a certified referee;
   - the LLM red team and the knowing-adversary arm that the table makes mandatory move to the full-certification track (§E.5, by amendment).
3. **If it is rejected:** the table above governs unchanged. Experiment 2 then waits for REFEREE-VALID or REFEREE-VALID-WITH-SCOPE, and must be re-specified within §H.8's limits.
4. **In either case:**
   - no Experiment 2 result counts toward, or substitutes for, any R1–R7 result or 1A outcome;
   - the §A.5 caveat applies to every 1A conclusion;
   - no 1A certification transfers to Experiment 2's configuration κ₂ or generator 𝒢₂;
   - Experiment 2 carries its own "not certified" caveat (Experiment 2 §A.5) and its own MRS reopen rule (Experiment 2 §B.3).
5. **Contradictions:** CL-30 to CL-41 (§L.1).
6. **The owner's clarification (t0 objective).** The immediate milestone is one bounded, reproducible, independently confirmed t0 covariate finding, followed by an investigation that builds on it (the recommended "Experiment 2-T0", Experiment 2 §T).
   - **If Experiment 2 decision 1 is approved,** it would likewise be gated by a referee subset (`OWNER_REVIEW.md` Part I.5), not by a 1A outcome. **If it is rejected,** item 3 applies to it as well.
   - It would run on real historical ODRÉ data, which the table above reserves until a real-data point-in-time validation (1B or a successor). The substitutes it proposes, and the credit it restricts to forward data, are logged as CL-40.
   - Full certification under this document is a later objective, and it says nothing about t0 unless a later amendment defines a configuration with t0 as the learner (CL-39).

---

## I. Seed commit–reveal protocol

**No seed, secret or commitment was generated in drafting this document.** `[DECISION]`

### I.1 Ceremonies

`[DECISION]`

| Ceremony | Domain | When | Purpose |
|---|---|---|---|
| C-dev | `dev` | After freeze and owner approval | Lean build: λ, calibration gate, development screens, timing, liveness worlds |
| C-cert | `cert` | After the code-freeze commit | Certification (R1–R7) |
| C-rep | `rep1` | Only after an invoked repair | Repair rerun |

Lean-build worlds are never reused for certification. `[DECISION]`

### I.2 What is committed before any secret exists

`[DECISION]`
- **P_H** = SHA-256 of the exact committed bytes (UTF-8, LF line endings) of this file at its frozen version.
- **F_H(domain)** = SHA-256 of the RFC 8785 (JCS) serialisation of {path: lowercase-hex SHA-256} over the frozen artefacts:
  - **dev:** the pre-registration, the static calendar table, the parameter table, the §B.4 interface definitions.
  - **cert, additionally:**
    - the referee, the generator and θ̃ oracle, the reference implementation, the orchestrator and stand-ins;
    - the R3 mutant and injection library with its liveness results;
    - the R5 mutant referees;
    - the R6 library and the U_V builds;
    - the FP-N and broken-G1 referees;
    - the calibrated β and β_M table, the λ table, and the calibration-gate results and reclassifications;
    - the component-to-criterion map;
    - the lock file and the container-image digests (x86-64 and aarch64);
    - the ι_1A conformance script.
  - **rep1, additionally:** the repair diff.
- P_H and F_H are recorded in git and in the ledger.

### I.3 Entropy, order and custody

The mechanism is subject to owner decision 7. `[DECISION]`

**Strict order, enforced by timestamps in git and in the ledger:**
1. P_H and F_H are committed.
2. A CI job running in a **protected GitHub Environment `1a-<domain>`** generates S_I (32 bytes) from its CSPRNG. The Environment's deployment rule admits only the frozen tag, and its required reviewer is the owner. The job writes S_I only to that Environment's secret store and commits Com_I.
3. The owner generates S_O (32 bytes) on their own machine with an operating-system CSPRNG, and commits Com_O.
4. The owner stores S_O in the same Environment.

**Neither secret is stored in any readable form before both commitments are recorded.** No Claude Code session and no workflow outside the Environment can read either secret. The dossier lists every principal who could read them.

### I.4 Injection, publication and aborts

`[DECISION]`
- **Injection.** The campaign job inside the Environment injects both secrets into B-SEED. B-SEED verifies both commitments (logging the result), derives M, and never releases M or any world, vault or permutation seed outside the trust domain.
- **Publication.** S_O, S_I and M are published in the dossier after the campaign closes.
- **Aborts.** If a ceremony is aborted after both commitments are recorded (a failed injection, a failed check, or a cancellation), then:
  - both secrets are published at close;
  - the orchestrator runs the frozen campaign on the aborted ceremony's M and reports its full results in dossier §7;
  - **the certified scope is the intersection** of the scopes from the aborted and the completed ceremonies.

  The same rule applies to every CAMPAIGN-VOID whose cause an operator could induce: R7 environment failure, or harness-error voids.
- **Re-holding a stage.** A stage may be re-held once. The re-held ceremony needs additional entropy fixed after the abort that neither party could know: a public-beacon round (if owner decision 7 enables it), or a secret from a third principal. More than one abort per stage → CAMPAIGN-VOID.

### I.5 Serialization and seed derivation

`[DECISION]`
- **Encoding.** enc(s) = uint16_be(len(s)) ‖ ASCII(s). Hashes and secrets enter as 32 raw bytes. Hex is used only in human-readable records, in lowercase.
- **Commitments.** Com_X = SHA-256(enc("1a-commit-v1") ‖ enc(domain) ‖ enc(X) ‖ S_X), for X ∈ {"O", "I"}.
- **Master seed.** M = SHA-256(enc("1a-master-v1") ‖ enc(domain) ‖ P_H ‖ F_H ‖ S_O ‖ S_I [‖ enc(beacon_id) ‖ uint64_be(round) ‖ SHA-256(beacon_value)]).
- **Seeds.** seed(purpose, stream, index) = HMAC-SHA256(key = M, msg = enc(purpose) ‖ enc(stream) ‖ uint64_be(index)).
- **Purposes:** `world`, `vault_resample`, `r5_split`, `attacker`, `permute_ids`, `liveness` (dev only).
- **Streams:**
  - `G1`, `G2`, `G3`;
  - `R2-t01`, `R2-t02`, `R2-t03`, `R2-t05`, `R2-t10`, `R2-G2`, `R2-G3`;
  - `R3-LK01` … `R3-LK23`, `R3-clean`, `R3-margin`, `R3-marginclean`;
  - `R5-G1`, `R5-G2`, `R5-G3`, `R6`;
  - `cal` (dev only).

  The positive controls use indices 0–399 of `G1`, `G2` and `G3`.
- **Attacker seeds** use the stream "⟨class⟩/⟨arm⟩/k⟨k⟩" (for example `G2/AT7/k30`), indexed by world.
- **Generator input.** The 32-byte output, read as a big-endian integer, is the entropy of `numpy.random.SeedSequence`, feeding `PCG64`. The numpy version is pinned in the lock file, and the order of generator calls is fixed in the code at freeze.
- **Attacker seeds are given to their own attacker processes.** Because HMAC-SHA256 is a pseudorandom function and inputs are domain-separated, this reveals nothing about any other seed. `[INFERENCE, standard PRF property]`

### I.6 Roles

| Role | Controls | Cannot |
|---|---|---|
| Owner (the key-holding principal) | S_O; approving each Environment deployment; publication | Choose M alone |
| Implementer (S-GEN, S-REF, S-CLEAN) | Nothing secret. S_I is generated by the Environment job | Read S_O, S_I or M before close. This is enforced only by the Environment protection, and the dossier lists every principal who could read the secrets |
| Trust domain (B-SEED) | Verification and derivation | Release M, or world, vault or permutation seeds, to the sandbox |

`[DECISION]`

### I.7 R7 subset selection

`[DECISION]`
- O_H = SHA-256(JCS({path: sha256_hex})) over all campaign output files.
- M_post = SHA-256(enc("1a-post-v1") ‖ M ‖ O_H).
- World i of stream s is in the R7 subset iff uint64_be(the first 8 bytes of HMAC-SHA256(M_post, enc("r7") ‖ enc(s) ‖ uint64_be(i))) < ⌊0.1·2⁶⁴⌋.

### I.8 Protection against seed shopping

| Route | Protection |
|---|---|
| Tuning code to the seeds | P_H and F_H are fixed before either secret exists. F_H(cert) covers every artefact that decides pass or fail |
| One party choosing M | Two secrets, each committed before either is readable |
| Rerolling | Seeds are deterministic in M; a new M needs a new ceremony, and aborts are published and intersected (§I.4) |
| Tuning on certification worlds | Development and certification ceremonies are separate; certification seeds are derived after code freeze |
| Repair used as a reroll | **Bounded:** one optional repair, admissible only if the diff touches the failing criterion's dependencies; carry-forward; repair-round cells at 99% CP; two-attempt error ≤ 0.055 per R4 cell |
| Voids used as rerolls | Void triggers are ledgered before counts are seen; completed FAILs survive voids; operator-inducible voids follow the abort rule |
| Choosing the R7 subset | The subset depends on M_post, and so on the campaign's outputs |

`[DECISION]`

---

## J. Validation dossier

The dossier is produced only after the certification campaign closes. `[DECISION]`

| # | Section | Content |
|---|---|---|
| 1 | Intended use | What a certified referee guarantees, per class and k, under κ_1A, 𝒢_1A and ι_1A |
| 2 | Prohibited use | Everything in §A.4. Any claim without the §A.5 caveat. G3 claims worded as unclipped skill |
| 3 | Conceptual soundness | The G1–G3 derivations (§D, labelled INFERENCE), their assumptions and the conditions that invalidate them |
| 4 | Implementation verification | R2, R2-G2 and R2-G3 agreement; R3 results and liveness; import-boundary and clean-room records; quadrature cross-checks; SC-ε and SC-𝒲 |
| 5 | Operating characteristics | For every criterion: x, n, CP bound, threshold and the OC table (Appendix A); the union and two-attempt error statements; power curves |
| 6 | Attack-campaign results | Every R4 cell (x, n, bound, SUT-error rate, NEAR_DUPLICATE counts); positive-control results; development-screen history, labelled non-certifying |
| 7 | Failed tests | Every FAIL, VOID and abort, with the aborted ceremonies' full results; the repair diff and the rerun results |
| 8 | Limitations | §A.4 in full; the residual common-mode risk (§C.12); the share of scored vault SPs in cells with fewer than 20 training rows (§C.7) |
| 9 | Certified scope | The §H.2 string, verbatim |
| 10 | Configuration and code hashes | P_H, F_H(dev/cert/rep1), the lock file, image digests, and the κ_1A, 𝒢_1A and ι_1A hashes; ceremony commitments |
| 11 | Reproducibility record | R7 and the cross-architecture results; the published S_O, S_I and M; the principals who could read secrets; reproduction commands |
| 12 | Change log | Every amendment, deviation (§M) and ledger event |
| 13 | "Cannot supply" | Real-data performance; resistance to an LLM adversary (unless tested); researcher skill; economic value; model-risk tiering, materiality and business-use suitability; human approvals; execution-layer and conduct testing |

**Also delivered:**
- `referee_verdict.json`: the machine-readable outcome per property and overall, following Appendix C.
- Reported, non-gating metrics:
  - the baseline-weakness metric;
  - the clip-flip rate;
  - R1-B;
  - the delay-vs-stress audit;
  - released-outcome counts per vault.

**Every number in the dossier is generated from committed code outputs**, and a test that compares prose numbers with their source outputs fails on any difference. `[DECISION]`

---

## K. Two-stage execution plan

### K.1 Stage 1: lean falsification build (non-certifying)

**Label.** Every output is labelled **"LEAN BUILD — NON-CERTIFYING — NOT VALIDATION"**. No lean result may be cited as validation. `[DECISION]`

**Authorship.** S-GEN and S-REF work in separate sessions (§B.4). S-CLEAN starts after the lean build. `[DECISION]`

**Scope** `[DECISION]`:
- **Generator:** full, with all 20 candidates.
- **Lean hypothesis space:** {X01, X02, X06, X10, X12, X14, X15, X17, X19, X20} × {T1, T2}.
- **Components:**
  - B-SPEC, B-REG, B-ASOF (with the TE, PO, VS, CI and LN controls), B-TGT, B-BASE, B-LRN;
  - B-VER (G1, G2), the G1 and G2 vaults (logical tick), and FP-N;
  - B-LEDGER, as one file per run;
  - B-SBX as a subprocess in its own network namespace.
- **Stand-ins:** HA, AT1, AT2, AT3, AT6.
- **Lean mutants:** LK01, LK02, LK03, LK06, LK08.
- **Ceremony:** C-dev only.
- **Not in the lean build:** G3, R5's wall-clock rig and mutants, R6, the clean-room reference, and full ι_1A isolation.

**Steps and early kills,** cheapest first. Each kill is a pre-registered stop followed by an owner decision. `[DECISION]`

| Step | Work | Early kill (rule) |
|---|---|---|
| 1 | Static calendar, generator, θ̃ oracle (closed form and GK cross-check, lemma grid self-test), L, λ selection; one world run twice | **EK1 Determinism:** two same-machine runs of one world differ in any byte, and the cause is not fixed within 3 engineer-days |
| 2 | Lean mutants on 20 worlds each (after liveness on 5 dev worlds) | **EK2 Obvious leak:** any lean mutant undetected in any of its 20 trials |
| 3 | Calibration gate (§C.9: 200 null and 200 planted worlds); margin-planted PASS rate on 100 dev worlds | **EK3 Calibration:** a null candidate fails the gate and neither reclassification nor an amendment is approved |
| 4 | R1-G1 screen (400 null worlds) | **EK4 Gross size violation:** LB(x, 400) > 0.05, i.e. x ≥ 28 |
| 5 | PC-G2 and the AT1/AT2/AT3/AT6 screens on 400 G2 worlds at K = 20 (19 distinct singles, then the ensemble) | **EK5 Positive control dead:** PC-G2 gives x < 73 of 400 after one ledgered strengthening |
| 6 | Measure CPU-seconds per QP solve and per world; project the full campaign with the §K.2 formula | **EK6 Compute:** projection > 600 CPU-h under κ_1A → owner decision (reduce, raise the budget, or stop) |
| any | Cumulative spend | **EK7 Budget** (v2 §16, threshold per owner decision 9): cumulative effort or compute above the approved budget before the first certified R4 result → stop, owner decision. Permitted re-scopes, each by amendment before C-cert: (1) drop k = 100, with full scope and REFEREE-VALID redefined as k ≤ 30 and the scope string saying so; (2) merge arms that share a mechanism, before code freeze only. G is already excluded |

**Estimates** `[INFERENCE]`:
- **Effort:** 3–4 engineer-weeks, based on code volume. Not measured.
- **Compute:** ≈ 1.7 M solves, so ≤ 40 CPU-h iff the mean solve time is ≤ 70 ms (with 20% overhead). After the first 50 lean worlds, the projected lean CPU-h is reported, and the build stops for an owner decision if it exceeds 40.

### K.2 Stage 2: full certification campaign

**Preconditions** `[DECISION]`:
1. The lean build ended with no unresolved early kill.
2. The owner authorizes the campaign, and §K.3 is met (owner decision 9).
3. All §B components are implemented, and S-CLEAN's code is committed.
4. The code-freeze commit and the C-cert ceremony are done.

**Scope.** R1–R7 in full (§G.9), then the dossier (§J). **The product may not claim a validated referee before this campaign passes.** `[DECISION]`

**Effort** `[INFERENCE, not bottom-up]`:
- +6–10 engineer-weeks after the lean build, for **9–14 in total**.
- Basis: an estimated 12–14 thousand lines including tests: generator and oracle about 1.5k; orchestrator and stand-ins about 2k; libraries about 1.5k; SUT about 5k; reference about 0.6k; tests about 3k.
- v2's 5–7 weeks predates the components added in D18–D20, D25, D29, D31 and D40 (§L, CL-26).

**Compute: planning range 150–600 CPU-h** (v2), retained **conditional on κ_1A and on the measured solve time**. `[INFERENCE]`

Solve counts at n = 2,000 (S = 100 fitted hypotheses + B = 101 models; 5 quantiles; 10 refits):

| Group | Formula | LP/QP solves |
|---|---|---|
| Class world sets G1, G2, G3 (null; including the PCs) | 3 × N × 101 × 10 × 5 | 30.3 M (36.4 M at N = 2,400) |
| R2 (fixed 4-hypothesis batch; SUT + reference) | 2,500 × 5 × 10 × 5 × 2 | 1.25 M |
| R2-G2, R2-G3 (B + X01; SUT + reference) | 1,000 × 2 × 10 × 5 × 2 | 0.2 M |
| R3 (2,600 trial-worlds × 5 models) | 2,600 × 5 × 10 × 5 | 0.65 M |
| R5.G2 pairs | 700 × (5,050 + 3,030) | 5.66 M |
| R5.G2 poisoning | 150 × 3,030 | 0.45 M |
| R5 mutants and wall-clock rig | 3 × 50 × 8,080 + 50 × 3,030 + 10 × 8,080 | 1.44 M |
| R5.G3 prefix pairs and their mutants | 300 × 7,575 (200 pairs + 50 per mutant) | 2.27 M |
| MARGIN-SENSITIVE reruns | ≈ 2,700 PASSes × 3 × 6 × 5 × 1.2 | ≈ 0.3 M |
| Inline LP and TI refits | ≈ 15,000 world-runs × 2 × 5 | ≈ 0.15 M |
| **Sum before R7** | | **≈ 42.7 M** |
| R7 same-architecture subset (10%) + cross-architecture rerun | | ≈ 8.5 M |
| **Total** | | **≈ 51.2 M** (58.5 M at N = 2,400) |

CPU-hours at 20% overhead:

| Mean solve time | N = 2,000 | N = 2,400 |
|---|---|---|
| 10 ms | ≈ 170 | ≈ 195 |
| 20 ms | ≈ 340 | ≈ 390 |
| 30 ms | ≈ 510 | ≈ 585 |
| 45 ms | ≈ 770 | ≈ 880 |
| 100 ms | ≈ 1,710 | ≈ 1,950 |

**The 150–600 range holds iff the mean solve time is about 9–35 ms (N = 2,000), or up to 31 ms (N = 2,400).** EK6 measures this.
- A full R7 rerun (owner decision 3) raises the total to ≈ 89.6 M solves (×1.75).
- Under the 1B configuration (19 quantiles, 48 origins, weekly refits, per-refit CV), compute is plausibly 10–100× higher. `[INFERENCE]`

### K.3 Condition for authorizing Stage 2

`[OPEN]` (owner decision 9). Recommended condition:

1. **Calls logged.** At least 10 completed front-office calls (script a) and at least 10 completed model-risk calls (script b), each logged with its date and an anonymised respondent ID.
2. **Neither v2 kill rule fires**, counted over the first 10 completed calls of each script in date order:
   - at least 3 front-office respondents answer yes to the scripted pilot question;
   - at least 3 model-risk respondents state both that a point-in-time / multiplicity evidence package is missing today and that it would cut validation effort.
3. **Design partner.** At least 1 named respondent has confirmed in writing that they will review the dossier.

The owner records the tallies in the ledger before authorizing Stage 2.

**This condition means only that no commercial kill fired. It is not a PRODUCT SIGNAL, and it validates neither demand nor the referee.** Stage 1 needs no commercial evidence.

---

## L. Contradiction log and review record

### L.1 Source contradictions

| ID | Conflict | Sources | Resolution | Status |
|---|---|---|---|---|
| CL-01 | R4 sizing: "≥ 400 worlds (800 final), two-sided CP ≤ 0.07" vs "2,000 per cell, one-sided ≤ 0.075" | digest vs v2 §17 and the owner instruction | Rank 1–2 wins. The digest's rule passes a cell at α only 29% of the time | Resolved |
| CL-02 | "P(all cells pass \| all at α) ≈ 0.95 for about 39 cells" vs 96 enumerated cells (0.882; full scope 0.830) | v2 §17 vs §G.5 | v2's n is kept as the default; 2,400 is recommended | **OPEN: decision 2** |
| CL-03 | G2 "embargo ≥ regime persistence" vs spells ≥ 15 d (mean 45) and a 21-d embargo | v2 §10 vs §C | θ̃ ground truth; R1/R4 measure the risk | **OPEN: decision 5** |
| CL-04 | R2 "≥ 99% agreement" vs numerical differences between independent implementations | v2 §17 vs design check | Pooled v2 rule plus a tolerance band | **OPEN: decision 10** |
| CL-05 | "Fixed 60-second tick" vs campaign scale (100 queries × 2,000 worlds × 60 s ≈ 139 days per G2 cell) | v2 §17 vs §G.6 | Logical tick in campaigns; wall-clock rig | Resolved (D11) |
| CL-06 | 1B's tuning segment and Politis–White switch vs none in 1A | full §8.5, §8.19 | Hyperparameters frozen; fixed 14-eligible-day blocks | Resolved (D7, D8) |
| CL-07 | Holm α = 0.04 + extension 0.01 (1B) vs α = 0.05 (1A) | full §8.19 | No extension in 1A | Resolved (D9) |
| CL-08 | 1B configuration vs κ_1A | full §8.7, §8.15 | Compute | **OPEN: decision 1** |
| CL-09 | k8 is listed as Stage 0 in the decision record and as the build gate in the full memo; it is now subsumed by R3 | decision record vs full memo | R3 subsumes k8 for the referee. A real-fixture R3 rerun remains a 1B requirement | Resolved |
| CL-10 | "1B: research more, needs egress" vs `BLOCKED_BY_ACCESS` | v2 §20 vs owner | The owner instruction wins; 1B is not redesigned | Resolved |
| CL-11 | Economic-check targeter and gate vs no gate in the SUT | v2 §7, §12 | AT13 is kept as a statistical attacker | **OPEN: decision 6** |
| CL-12 | 1B placebo gates vs none in the SUT | v2 §7, §10 | AT9 redefined | Resolved (D13) |
| CL-13 | c = warm-up MAD vs c = 1 | full §8.8 | Exact linearity | Resolved (D1) |
| CL-14 | Sandbox runs model code vs declarative specs only | v2 §15 | Exp 2 extension | Resolved (D17) |
| CL-15 | The design check suggested dropping the economic-score targeter, but the owner listed it | design check vs owner | Owner wins: AT13 kept | Resolved |
| CL-16 | Compute: v2's 150–600 vs the design check's 10–100× under the 1B configuration, and v0.1's under-counted formula | v2 §16, design check, review | Retained conditional on κ_1A and t_solve ≤ 35 ms (31 ms at N = 2,400); measured at EK6 | Resolved (conditional) |
| CL-17 | 2-day interleaved split (design check) vs per-SP increments; v2 §10 "h subsequences" for 1B | design check, v2 §10 | Per-SP under κ_1A needs no split. The 1B note is non-binding | Resolved (1B noted, not decided) |
| CL-18 | G2 condition (ii) mentions 1B releases, but 1B is blocked | v2 §10 | Cross-vault leakage is untested (§A.4 item 12) | Resolved |
| CL-19 | The remote default branch is still `claude/t0-solar-benchmark-ochpix` | git state | No effect on 1A (identical trees); owner housekeeping | Noted |
| CL-20 | The local tag `experiment-0-solar-final` → `406c92c` is not pushed | git state | No effect on 1A; owner housekeeping | Noted |
| CL-21 | R2 "≥ 99% of worlds" (pooled) vs v0.1's per-θ rule | v2 §17 vs v0.1 | v2's pooled rule restored | Resolved |
| CL-22 | Minimum scope "G2 k ≥ 30 or G3" vs v0.1's "G3 k ≥ 30" | v2 §17 vs v0.1 | v2's wording restored | Resolved |
| CL-23 | A dead PC → campaign VOID (v2) vs v0.1's per-class re-ceremony | v2 §17 vs v0.1 | v2 restored, plus UNCERTIFIABLE after one strengthening | Resolved |
| CL-24 | FRAGILE "within 1% relative" vs v0.1's absolute band | v2 §17 vs v0.1 | v2 restored and extended to e-processes and counts | Resolved |
| CL-25 | The v2 §16 budget kill vs its absence in v0.1 | v2 §16 | Restored as EK7 | Resolved (threshold: decision 9) |
| CL-26 | v2 1A effort 5–7 engineer-weeks vs the code-volume estimate of 9–14 | v2 §16 vs §K.2 | Both are shown. EK7's threshold must reflect the owner's choice | **OPEN: decision 9** |
| CL-27 | "One α charge per cluster" vs every hypothesis charged in full | v2 §7, §15 | Stricter; the NEAR_DUPLICATE flag is reported | Resolved (D39) |
| CL-28 | v2 R8 reopen rule vs its omission in v0.1 | v2 §17 | Restored (§H.8) | Resolved |
| CL-29 | "LLM red-team findings become regression tests" | v2 §17 R6 | Deferred with the red team (Exp 2) | Resolved (D29) |
| CL-30 | Experiment 2 is gated on REFEREE-VALID or VALID-WITH-SCOPE (§H.8 table; the last bullet of §H.1; v2 §17 "Exp 2 does not start"), whereas the redefined Experiment 2 is gated by the MRS | Owner instruction of 2026-09-23 (Exp 2) vs §H.1, §H.8, v2 §17 | §H.8 v0.3 note. The text of §H.1 and §H.8 is unchanged and would govern institutional use of certified guarantees | **OPEN: Exp 2 decision 1** |
| CL-31 | §H.8 makes an LLM red team and a knowing-adversary arm mandatory in Experiment 2; `OWNER_REVIEW.md` decision 8 and CL-29 defer the red team "to Experiment 2". The redefined Experiment 2 contains neither | §H.8, §E.5, CL-29 vs Exp 2 §I | Both move to the full-certification track (a §E.5 amendment). Decision 8's recommendation is updated in `OWNER_REVIEW.md` v0.3. The §A.5 caveat is unchanged | **OPEN: Exp 2 decision 1** |
| CL-32 | §H.8 limits Experiment 2 to κ_1A and 𝒢_1A; the redefined Experiment 2 uses the daily κ₂ and 𝒢₂ | §H.8 (ii), (iv) vs Exp 2 §C | No 1A certification transfers to κ₂. The MRS runs on κ₂ | Resolved (documented) |
| CL-33 | §H.8 (i) offers G1, G2 and G3, and the minimum scope needs G2 or G3; the redefined Experiment 2 uses G1 plus harness replication only | §H.2, §H.8 vs Exp 2 §G | G2 and G3 stay in 1A's certification scope. They are not used by Experiment 2 | Resolved (documented) |
| CL-34 | 1A's G1 accepts m ≤ 4 hypotheses of form `1a-1`; Experiment 2's G1 accepts ≤ 4 positive and ≤ 2 negative DSL claims (`2-1`) in two Holm families with shifted nulls | §B.3, §D.1 vs Exp 2 §F, §G.2 | Experiment 2 defines its own G1 variant; §D.1 is unchanged | Resolved (documented) |
| CL-35 | §H.8 (iii): researcher code needs a new sandbox certification; Experiment 2's model agent executes exploratory code in a sandbox checked only by conformance (claims stay declarative) | §H.8, D17 vs Exp 2 §B.2 | Documented as conformance-checked only, not certified or attacked: Experiment 2 §B.2 (Scope), CX-06, MRS-9 and §N item 5 | Resolved (documented) |
| CL-36 | The reopen rule refers to a certified referee; Experiment 2's referee is MRS-checked only | §H.8 vs Exp 2 §B.3 | Experiment 2 has its own MRS reopen rule; this rule is unchanged | Resolved |
| CL-37 | §0.1 ("no commit, tag, push or pull request") and the v0.2 owner review ("not committed") vs the commit of v0.2 in draft PR #2 | §0.1 vs owner instruction | §0.1 status note; `OWNER_REVIEW.md` v0.3 | Resolved |
| CL-38 | The v2 roadmap has Exp 2 as autonomy and Exp 3 as knowledge accumulation; the redefined Experiment 2 includes a memory arm and a small transfer probe | v2 §18 vs Exp 2 §I, §M | Experiment 3 remains the accumulation test; Experiment 2's memory arm is an in-benchmark ablation | Resolved |
| CL-39 | 1A does not exercise t0: learner L is elastic-net quantile regression (§C.10), learner G is not run, and 𝒢_1A has no t0 input. v2 §20 said "t0 is irrelevant to Exp 1". The owner's clarified objective centres on an AI researcher using t0's covariates (past and known-future), and the known-future covariate leak classes are in no catalogue | §C.10, §A.4 item 7, §G.4.2; v2 §20 vs owner clarification | No 1A criterion changes. Full certification is a later objective. The first t0 demonstration uses the subset in `OWNER_REVIEW.md` Part I.5, adding t0-specific leak mutants. Certification relevant to t0 would need a later amendment with a t0 configuration | **OPEN: Exp 2 decisions 1 and 5** |
| CL-40 | The recommended Experiment 2-T0 uses real historical ODRÉ data (2021–2026) for discovery and both sealed segments. §H.8 (iv) admits real historical data only after a real-data point-in-time validation (1B or a successor), and CL-09 keeps a real-fixture R3 rerun as a 1B requirement. 1B is `BLOCKED_BY_ACCESS` | §H.8 (iv), CL-09 vs Exp 2 §T.2 | No 1A text changes, and §H.8 (iv) still governs certified use. For 2-T0 only, the proposed substitutes are Experiment 0's truncation and poisoning tests, the `OWNER_REVIEW.md` Part I.5 controls on the real ODRÉ vintages (including forecast-level controls) and the forward recorder. Proposed: only the forward window after the tested claim batch's hash (the premise batch for Stage 4, the building batch for Stage 5) is ledgered and recorder go-live is verified (Exp 2 §T.2), and not before the researcher's knowledge vintage, earns credit as hindsight-free evidence | **OPEN: Exp 2 decision 1** |
| CL-41 | Truth estimand. §C.9 defines G1 ground truth as the skill of the fitted forecasts on the vault days used ("exactly the estimand of the test's mean of batch means"; D3: "The referee tests fitted-forecast skill"). Experiment 2's truth is the expected skill of the claim pipeline over training draws and test days under the forward law | §C.9, D3, decision 5 vs Exp 2 §J.1 | Experiment 2 scores knowledge, not referee size. It reports a 1A-style conditional grade as secondary and splits its false-discovery proportion into test error and estimand gap (Exp 2 §J.1, S2). §C.9 is unchanged | Resolved (documented) |

### L.2 Items not adopted from the design check or the review, with reasons

| Item | Reason |
|---|---|
| Redefine the G1/G2 ground truth to follow the test's own weighting (review M05, M17) | That would hide weighting-induced errors. Instead, the test is aligned to the claim (blocks of 14 eligible days, day-weighted θ̃), and θ̃_SP is reported (§C.9) |
| Per-θ R2 agreement | Stricter than v2 and unrecorded; v2's pooled rule was restored |
| Prober arm AT7-C and mutant M-R for co-residency channels | Not required for internal consistency. The channels are declared untested (§A.4 item 13, the scope string). They can be added by amendment |
| V9–V13 as mandatory R6 classes | A scope expansion. They are listed as untested |
| Dropping the economic-score targeter (design check) | The owner listed it explicitly (CL-15) |

### L.3 Review record

`[DECISION]` (record only)

**v0.1 → v0.2.** v0.1-draft went through a read-only adversarial review: 7 lens reviewers and 2 refuting verifiers.
- **Findings:** 84 in total: 46 must-fix, 35 should-fix, 3 nits.
- **Verification:** the verifiers confirmed 41 of the 46 must-fix findings. All 41 are addressed in v0.2, some in the verifiers' corrected form.
- **The 5 not confirmed as must-fix:**
  - M05 and M17: see §L.2.
  - Sealed-set scope: clarified as §C.2a, and V4 widened.
  - Ledger dictionary attack: clarified as §B.1a.
  - Filtration ambiguity: clarified as the 𝔉_s definition.

The main must-fix corrections were these (the full list is in the review record):

| Area | Correction |
|---|---|
| Repair | The repair round was an unbounded reroll |
| Test definition | Degenerate cases, regime-restricted batching and Holm were undefined |
| R2 | The R2 null and its operating characteristics were misstated |
| Compute | The compute formula under-counted |
| G2/G3 liveness | No test checked that G2 or G3 could ever PASS |
| G3 claim | The G3 claim wording did not say "clipped" |
| R5 | R5's mutants could not be detected; the G3 test was vacuous; the timing rule was undefined |
| Isolation claim | Side-channel coverage was claimed but not tested |
| R6 | The "blocked" definition was wrong for read-type vulnerabilities |
| Seeds | Custody and abort-based rerolls |
| θ̃ | The cross-check was infeasible |
| Generator | There was no row schema or recorder; margin calibration was undefined; B lacked an intercept when a regime was missing from the window |
| Criterion fields | Some R-criteria were missing required fields |
| Outcomes | Some VOID states were unmapped |
| Registration | The G3 registration schedule was inconsistent |
| Logs | The deviation log was incomplete |
| Commercial | The call counts made the condition impossible to evaluate |
| Next prompt | The next prompt was unsafe and unbounded |

**v0.2 → v0.3.** No criterion was reopened. The v0.3 edits (status language, the §H.8 note, CL-30 to CL-41) were checked by the adversarial design review of Experiment 2 v0.1-draft, whose 1A-consistency lens added CL-40 (finding R1-10) and corrected CL-35 and the naming of the owner's instructions (R1-78, R1-80). A mechanical comparison against `e9aa4cc` confirmed that §A–§G, §H.1–§H.7, §I, §J, §K, §M and Appendices A–C are byte-identical to v0.2, and that the original §H.8 text is unchanged. The review record is in Experiment 2 §R.

---

## M. Deviations from the v2 decision memo

**Format:** ID · v2 reference · deviation · reason · effect · approval route. Every row needs owner approval, either through an owner decision or through the checklist in `OWNER_REVIEW.md`. `[DECISION]`

| ID | v2 ref | Deviation | Reason | Effect | Approval |
|---|---|---|---|---|---|
| D1 | full §8.8 | c = 1 instead of the warm-up MAD | Exact oracle linearity | Fitted-transform leakage is tested via scalers (LK07) | Checklist |
| D2 | §8A item 2 | Regimes published in B. The latent-regime and lagged-target classes are removed from 1A | L correctly specified; smallest design | Not certified (§A.4 item 8) | Checklist |
| D3 | §17 R1/R4 "null worlds" | False PASS judged by the fitted-forecast θ̃, not by the generator null | The referee tests fitted-forecast skill | Baseline weakness reported separately | Decision 5 |
| D4 | §10 G2 (i) | 21-day embargo; "≥ regime persistence" becomes a tested assumption | Avoids a ≥ 45-day embargo | Measured by R1/R4 | Decision 5 |
| D5 | §8A item 3 | κ_1A (8 origins, 5 quantiles, quarterly refits, frozen λ) | Compute | Certification limited to κ_1A | Decision 1 |
| D6 | §8A item 1 | LightGBM G not run | Compute; smallest design | G uncertified | Decision 1 |
| D7 | full §8.5 | No tuning segment | Hyperparameters frozen | None | Checklist |
| D8 | full §8.19 | No Politis–White switch; 14-eligible-day blocks; minimum n_b = 6 | Deterministic path; regime restrictions | Size measured by R1 | Checklist |
| D9 | full §8.19 | α = 0.05, no extension | No extension in 1A | None | Checklist |
| D10 | §17 R2 | Tolerance band for borderline worlds; \|Δt\| non-gating | Numerical noise at the threshold | Slightly weaker agreement test | Decision 10 |
| D11 | §17 R5 | Logical tick in campaigns; wall-clock rig with the q + 2 schedule, 5-s deadline, 50-ms window and Spearman rule | Campaign scale; timing was undefined | Timing evidence rests on the rig | Checklist |
| D12 | §17 R4 | G1 cells have no k | G1 is single-use | None | Checklist |
| D13 | §7, §10 | No placebo gates; AT9 redefined | Scope | Placebo gates uncertified | Checklist |
| D14 | §7, §12 | No economic gate | Smallest design | Economic gate uncertified | Decision 6 |
| D15 | §17 verdict rules | Arms can never be scoped out | An adversary would use the excluded attack | Stricter | Checklist |
| D16 | §17 R7 | R7 on a post-campaign 10% subset | Compute | Weaker than a full rerun | Decision 3 |
| D17 | §15 item 8 | Declarative specs only | Smallest TCB | Code sandboxing uncertified | Checklist |
| D18 | (new) | Separate world streams per class; three ceremonies; protected-Environment custody; the abort and intersection rule | Leakage and rerolls | Stronger | Decision 7 |
| D19 | §17 R4 | Per-class PCs (PC-G1 and PC-G3 added) gate their class's scope; R5 mutant controls | Tests must be able to fail | Stronger | Checklist |
| D20 | §10 G3 | G3 fully specified: per-SP clipping, empirical-Bernstein mixture, clipped weak null, claim text | v2 left it undefined | G3 certifies clipped-loss improvement only | Decision 4 |
| D21 | §17 R4 | n per class set tied to the 96 cells and full scope | Consistency of the OC claim | CL-02 | Decision 2 |
| D22 | §8A item 4 | L_P = 518 by default | v2 unspecified | Sets G3 power and compute | Decision 4 |
| D23 | (new) | B has no lagged targets; intercept with unpenalised structure and the minimum-rows rule | Exact linearity; unseen cells | Lagged-target dynamics uncertified | Checklist |
| D24 | §17 R1 | R1-G3: k = 10 registrations at α/10, not one e-process | Exercises the α-spent registration set | Different honest-use scenario | Checklist |
| D25 | §17 R3; §8A item 2 | Code mutants for 20 classes, injections for 3; controls defined (§G.4.1); fixed trial batch | Implementability; smallest design | None on the claim | Checklist |
| D26 | §17 R3 margin | Single-hypothesis margin trials; denominators are PASS worlds ≥ 90; ms_false ≤ ⌊0.05·D⌋ | Well-defined denominators | Keeps v2's 5% | Checklist |
| D27 | §8A item 9 | R1 and R4 share the class sets; PCs use indices 0–399 | Compute | R1 and R4 failures are correlated | Checklist |
| D28 | §17 R4 PC | The naive PC-G2 uses α_i = 0.05/K ("per-query α" read as a Bonferroni ledger) | Isolates the feedback channel; unadjusted α would fire through multiplicity alone | The PC tests feedback leakage specifically | Checklist |
| D29 | §17 R6 | V7 and V8 added; per-type "blocked"; TCB-side monitor; U_V liveness; V4 widened; LLM-finding regression rule deferred | Correct read and egress semantics | Stronger | Checklist |
| D30 | §17 R7 | Cross-architecture rerun mandatory on the R7 subset (x86-64 and aarch64) | FRAGILE needs data | More compute | Checklist |
| D31 | §17 R5 | G2 pairs at K = 100; new G1 receipt and G3 prefix components; a G1 or G3 component failure removes that class (G1 removal → INVALID) | Coverage of G1 and G3 | Stricter than v2 ("does not invalidate G1") | Checklist |
| D32 | §17 certified scope | Adds PC-fired, per-class R5 components and R2-G2/R2-G3 | Tests must be able to fail | Stricter | Checklist |
| D33 | §17 verdict rules | CAMPAIGN-VOID is a fourth outcome with precedence | Owner instruction | Harness defects are not labelled INVALID | Checklist |
| D34 | §17 repair | Optional, owner-invoked within 14 days; admissibility rule; carry-forward; repair-round cells at 99% CP | A reroll would inflate error | Two-attempt error ≤ 0.055 per cell | Decision 2 |
| D35 | §16 budget kill | EK7 with an owner-set threshold; re-scopes constrained by D15 | Restores v2's kill | — | Decision 9 |
| D36 | §16 effort | 9–14 engineer-weeks (code-volume estimate) against v2's 5–7 | Scope added in review | Budget | Decision 9 |
| D37 | §13 | Stage-2 commercial condition: 10 calls per script, written design-partner confirmation | Evaluable rule | Not a PRODUCT SIGNAL | Decision 9 |
| D38 | §8A item 1, §11, §15 item 10 | "α-wealth" and "bits released" become uniform α-spending and released-outcome counts | Smallest design | No wealth earn-back | Checklist |
| D39 | §7, §15 item 7 | Every hypothesis charged in full; NEAR_DUPLICATE (forecast correlation) reported, no cluster discount | Stricter FWER | Lower power for variant-heavy strategies | Checklist |
| D40 | §17 R2 | R2-G2 and R2-G3 (liveness and agreement) added | A dead G2/G3 would otherwise certify | Stricter | Decision 10 |
| D41 | §7 | Delay-vs-stress audit reported (non-gating) | v2 left its role undefined | Report only | Checklist |
| D42 | §8A item 11; §14–15 | `referee_verdict.json` kept (§J). The Experiment 0 golden-bootstrap test is outside 1A's scope (repository architecture) | Scope | None on the referee | Checklist |
| D43 | full §8.7 | L is elastic-net QR (γ = 10⁻⁶ ridge, QP), not LASSO-QR (LP) | Unique solution for R2 and R7 | New solver dependency later | Decision 1 |
| D44 | (new) | R4 SUT-error gate (≤ 0.1% internal-error NOT-PASS on valid submissions) | An always-erroring referee must not pass | Stricter | Checklist |
| D45 | (new) | t₃ truncated at \|T\| ≤ 1000 | Floating-point overflow of sinh | Removed mass 2.2·10⁻⁹ | Checklist |

---

## N. Freeze, approval and amendment protocol

`[DECISION]`

1. **Draft stage (now).** Edits are free, and nothing is committed without the owner's instruction.
2. **Approval.** The owner answers the decisions in `OWNER_REVIEW.md` and approves the checklist. The document becomes v1.0, which records the decisions and removes each `[OPEN]` they resolve.
3. **Freeze.** v1.0 is committed on the owner's instruction, and P_H is computed (§I.2) and ledgered. **Implementation may begin only after this step**, starting with the §B.4 artefacts and C-dev.
4. **Amendments after freeze.** Each amendment is a new version with a change-log entry (what, why, which criteria it affects, owner approval) and a new P_H. An amendment after C-cert → CAMPAIGN-VOID (§H.1).
5. **Change log:**

   | Version | Date | Change |
   |---|---|---|
   | v0.1-draft | 2026-09-23 | First draft |
   | v0.2-draft | 2026-09-23 | All 41 confirmed must-fix review findings and the adopted should-fix findings applied (§L.3); deviations D24–D45 added |
   | v0.3-draft | 2026-09-24 | No criterion changed. Status language (header, §0.1); §H.8 v0.3 note on the redefined Experiment 2, the MRS gate and the owner's t0 clarification; CL-30 to CL-41; §L.3 record. Companion `OWNER_REVIEW.md` v0.3 adds Part I (MRS) and Part I.5 (the subset and gate for the first t0 demonstration), and updates Part II (decisions 1, 5, 7 and 8; the recommendation; the scope table and early-kill text; the Experiment 1B and Elexon section (CL-40); the checklist and next prompt) |

---

## Appendix A. Exact-binomial operating characteristics

**Formulas:**
- UB(x, n) = Beta⁻¹(c; x + 1, n − x), with UB(n, n) = 1.
- LB(x, n) = Beta⁻¹(1 − c; x, n − x + 1), with LB(0, n) = 0.
- c = 0.95 unless stated.
- x_max(n, m) is the largest x with UB(x, n) ≤ m.
- P(pass | p) = P(Binomial(n, p) ≤ x_max).

**Method:** exact log-gamma summation and bisection. Deterministic; no randomness.

### A.1 Upper-bound pass rules

| Rule | n | m | x_max (95%) | x_max (99%, repair round) |
|---|---|---|---|---|
| R1 | 2,000 | 0.07 | 120 | 113 |
| R1 | 2,300 | 0.07 | 140 | 132 |
| R1 | 2,400 | 0.07 | 147 | 139 |
| R4 cell | 2,000 | 0.075 | 130 | 122 |
| R4 cell | 2,300 | 0.075 | 151 | 143 |
| R4 cell | 2,400 | 0.075 | 158 | 150 |

**P(pass | p), 95% rules:**

| p | R1, n = 2,000 | R1, n = 2,400 | R4 cell, n = 2,000 | R4 cell, n = 2,400 |
|---|---|---|---|---|
| 0.050 | 0.9801 | 0.9939 | 0.9987 | 0.9997 |
| 0.055 | 0.8483 | — | 0.9756 | — |
| 0.060 | 0.5243 | — | 0.8387 | — |
| 0.065 | 0.1953 | — | 0.5233 | — |
| 0.070 | 0.0414 | 0.0484 | 0.2036 | — |
| 0.075 | 0.0050 | — | 0.0467 | 0.0458 |
| 0.080 | 0.0004 | — | 0.0063 | — |

**Repair-round (99%) rules at p = 0.05:**
- R1 passes with 0.915 (n = 2,000) or 0.951 (n = 2,300).
- An R4 cell passes with 0.988 (n = 2,000) or 0.996 (n = 2,300).
- All 96 cells pass with 0.305 (n = 2,000), 0.674 (n = 2,300) or 0.761 (n = 2,400). **This is why carry-forward is the default.**

**Two-attempt false certification** (95% then 99%):
- R4 cell at p = 0.075: 0.0546 (n = 2,000), 0.0551 (n = 2,400).
- R1 at p = 0.07: 0.0496 (n = 2,000), 0.0577 (n = 2,400).

### A.2 Joint pass probabilities

Every rate is exactly 0.05, with an independence lower bound:

| n | Per R4 cell | 12 cells | 42 cells | 96 cells | Full scope (3 R1 + 96) | Below minimum scope |
|---|---|---|---|---|---|---|
| 2,000 | 0.99869 | 0.984 | 0.947 | 0.882 | 0.830 | 0.038 |
| 2,300 | 0.99960 | 0.995 | 0.983 | 0.962 | 0.937 | 0.014 |
| 2,400 | 0.99973 | — | — | 0.974 | 0.956 | 0.010 |

A full-scope probability of at least 0.95 needs n ≥ 2,370.

### A.3 Positive controls and screens (n = 400)

| Rule | Threshold | Probability of firing (or of failing, for the screen) at the true rate |
|---|---|---|
| PC-G1, PC-G2: fire iff LB > 0.15 | x ≥ 73 | 0.043 at 0.15; 0.825 at 0.20; 0.9995 at 0.25 |
| PC-G3: fire iff LB > 0.10 | x ≥ 51 | 0.044 at 0.10; 0.911 at 0.15; 0.9999 at 0.20 |
| Development screen: fail iff LB > 0.05 | x ≥ 28 | 0.048 at 0.05; 0.528 at 0.07; 0.985 at 0.10 |

For comparison, the digest's rule (n = 400, two-sided, UB ≤ 0.07) gives x_max = 17 and passes a cell at 0.05 with probability only 0.291.

### A.4 Other bounds and rules

| Rule | Value |
|---|---|
| LB(100, 100) | 0.9705 |
| LB(20, 20) | 0.8609 |
| LB(495, 500) | 0.9791 |
| LB(269, 500) | 0.5002 (LB(268, 500) = 0.4982) |
| UB(0, 50) | 0.0582 |
| UB(0, 100) | 0.0295 |
| UB(0, 200) | 0.0149 |
| UB(0, 500) | 0.0060 |
| UB(0, 700) | 0.0043 |
| UB(5, 500) | 0.0209 |
| UB(25, 2,500) | 0.0139 |
| R2 recovery (≥ 495/500) | 0.616 / 0.958 / 1.000 at power 0.99 / 0.995 / 0.999 |
| R2 pooled agreement (≤ 25/2,500) | 0.9995 at 0.005; 0.553 at 0.01 |
| Whole R2 rule | 0.958 at (0.995, 0.005); 0.616 at (0.99, 0.005) |
| R3 margin false flags | ≤ 5 of D = 100: 0.985 at 0.02, 0.616 at 0.05. ≤ 4 of D = 90: 0.965 at 0.02, 0.530 at 0.05 |
| Spearman critical value (n = 200, two-sided 0.01) | z₀.₉₉₅/√199 = 0.1826 |
| DKW constant for SC-ε (false alarm 10⁻⁹) | √(ln(2·10⁹)/2) = 3.272 |

---

## Appendix B. Threat-model coverage (full memo §7)

| Row | Threat | 1A coverage |
|---|---|---|
| 1 | Target vintage revisions | LK02; the target builder uses Y¹ |
| 2 | First message not near-real-time | **Not synthesizable** (the semantics of a real feed; 1B) |
| 3 | Meaning of the timestamp tag | LK01, LK03 |
| 4 | UploadTime not genuine | LK05. Real-feed genuineness is **1B only** |
| 5 | REST latest views; dedup | LK02, LK10 |
| 6 | Migrated synthetic publishTime | LK05 |
| 7 | Settlement inputs for the same SP | LK06 |
| 8 | Revised fundamentals | LK02. Reference-data semantics are **1B only** |
| 9 | Publication delays | LK01, LK21; DP-2; MB (MARGIN-SENSITIVE) |
| 10 | Exchange data | LK21 (the analogue). Specifics are **1B only** |
| 11 | Timezones | LK08 |
| 12 | DST | LK08; calendar invariants (CI) |
| 13 | Reanalysis passed off as forecasts | LK02 |
| 14 | Fitted transforms using the future | LK07 |
| 15 | Label availability | LK06, LK09 |
| 16 | Overlapping horizons and dependence | R1; LK22 |
| 17 | Hyperparameter selection on the test period | LK11 |
| 18 | Holdout reuse | G1 single use; R4 (AT5, AT6); LK13 |
| 19 | Multiplicity | R1, R4; Holm; α-spending |
| 20 | Designer snooping | Seed protocol (§I). Synthetic worlds are generated after the freeze |
| 21 | Imputation using the future | LK04, LK12 |
| 22 | Survivorship | LK17 |
| 23 | Information-set asymmetry | LK18 |
| 24 | Forecast combination read as market information | **Not applicable** (an interpretation question) |
| 25 | Placebo design | **Not applicable** (D13) |
| 26 | As-of boundary ties | LK23 |
| 27 | Transaction costs | **Not applicable** (D14) |
| 28 | Regimes chosen after the outcome | LK14 |
| 29 | Market-rule changes | **Not synthesizable**; regime switches stand in only partially |
| 30 | Pretraining contamination | **Not applicable** to 1A; Exp 2 |
| 31 | Recorder clock | LK19; R6 V6 |
| 32 | Provenance and caching | LK15, LK16 |
| 33 | Vacuous controls; prose leakage | Liveness rules (R3, R6); positive controls; the prose-number test (§J) |
| 34 | Prospective data before the freeze | LK20; seed protocol |

---

## Appendix C. Machine-readable outcome logic

```yaml
precedence: [CAMPAIGN_VOID, REFEREE_INVALID, REFEREE_VALID_WITH_SCOPE, REFEREE_VALID]
fragile_resolution_first: true
campaign_void_if_any:
  - generator_self_check_failed
  - any_cell_or_criterion_harness_error_rate > 0.01
  - R2.clean_room_breach OR R2_G2.clean_room_breach OR R2_G3.clean_room_breach
  - R3.any_class_not_live OR R3.D_planted < 90 OR R3.D_clean < 90
  - R6.any_V_not_live
  - R5.any_mutant_undetected
  - R7.environment_failure
  - PC_G1.uncertifiable OR (PC_G2.uncertifiable AND PC_G3.uncertifiable)
  - PC_any.not_fired_first_attempt        # -> one strengthening by amendment + fresh C-cert
  - amendment_after_cert_ceremony
  - aborted_ceremonies_in_stage > 1
void_preserves: completed gating results unless the cause invalidates worlds; completed FAILs are never erased
certified_classes:
  G1: R1.G1.pass AND PC_G1.fired AND all(R4.G1.cells.pass) AND R5.G1.pass
  G2: {max_k: max k in [10,30,100] s.t. R1.G2.pass AND PC_G2.fired AND R5.G2.pass AND R2_G2.pass AND all(R4.G2.cells[k' <= k].pass)}
  G3: {max_k: max k in [10,30,100] s.t. R1.G3.pass AND PC_G3.fired AND R5.G3.pass AND R2_G3.pass AND all(R4.G3.cells[k' <= k].pass)}
minimum_scope: G1 AND (G2.max_k >= 30 OR G3.max_k >= 10)
full_scope: G1 AND G2.max_k == 100 AND G3.max_k == 100
referee_invalid_if_any: [NOT R2.pass, NOT R3.pass, NOT R6.pass, NOT R7.pass, NOT minimum_scope]
referee_valid_with_scope: R2.pass AND R3.pass AND R6.pass AND R7.pass AND minimum_scope AND NOT full_scope
referee_valid: R2.pass AND R3.pass AND R6.pass AND R7.pass AND full_scope
repair:
  optional: true
  decision_window_days: 14
  outcome_before_decision: PROVISIONAL
  max_rounds: 1
  admissible_if: diff intersects failing criterion's dependency set
  rerun: criteria and cells whose dependency set intersects the diff; others carried forward
  repair_round_thresholds: {R1: "UB99 <= 0.07", R4_cell: "UB99 <= 0.075"}   # OPEN (owner decision 2)
  rerun_results_replace_originals: true
  fail_in_repair_is_final: true
flags:
  FRAGILE: cross_arch differs AND within 1% (relative) of the threshold -> evaluate with the conservative value (§H.6)
  MARGIN_SENSITIVE: primary == PASS AND any(perturbed == NOT_PASS); counts as PASS in R1/R4
reopen: a later audit finds a missed leak -> outcome := REFEREE_INVALID; dependent Exp 2 claims suspended
mandatory_caveat: "Certified against the pre-registered scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher."
```
