# Experiment 1A: owner review

Companion to `PREREGISTRATION.md` v0.3-draft (2026-09-24).

**Status: DRAFT.** v0.2 was committed (`e9aa4cc`) and pushed to draft pull request #2 on your instruction, and v0.3 is committed to the same PR. Nothing is frozen or implemented, and no P_H has been computed.

**What changed in v0.3.** You redefined Experiment 2 as a blinded knowledge-creation benchmark (`docs/experiment_2/`). This review is therefore split in two:
- **Part I:** the **minimum trustworthy-referee subset (MRS)**, required before the Experiment 2 benchmark;
- **Part II:** **full institutional referee certification** (the 1A campaign). Its criteria are unchanged from v0.2 (see the Part II introduction for the v0.3 edits).

**Your later clarification (also 2026-09-23; the t0 research-loop objective).**
- The core is an AI researcher that uses **t0's covariate capabilities**, and the referee supports that research loop.
- **Full referee certification (Part II) is a later objective.**
- The immediate milestone is one bounded, reproducible, independently confirmed t0 finding, followed by an investigation that builds on it.

**The 1A design does not exercise t0 at all** (CL-39). Its learner is elastic-net quantile regression, and its generator 𝒢_1A has no t0 input. **Part I.5** below therefore lists which parts of 1A the first t0 demonstration ("Experiment 2-T0") needs, with its own gate.

**No 1A certification criterion, threshold or outcome rule changed.** The only edits to `PREREGISTRATION.md` are status language, a note at §H.8, and new log entries: CL-30 to CL-41, the review record and the change log.

---

## Part I. The minimum trustworthy-referee subset (MRS): the gate for the Experiment 2 benchmark

**Authoritative definition:** `docs/experiment_2/PREREGISTRATION.md` §B.3. If this summary and §B.3 disagree, §B.3 wins.

**Decision:** Experiment 2 owner decision 1 (it adds no decision to this review).

### I.1 Why a subset is enough for the Experiment 2 benchmark, and what it is for

The Experiment 2 benchmark grades every claim against **concealed ground truth**, not against referee verdicts. A referee that lets false claims through is therefore *measured* there, as a higher false-discovery rate or lost power; it is not hidden. `[INFERENCE]`

The MRS targets the failures that ground-truth scoring **cannot** see:
- **exposure of sealed data or truth** to the researcher side, which would inflate true discoveries invisibly;
- **point-in-time or vault-to-discovery leaks** that help every referee arm alike (for example LK13), which would inflate the referee arms' true discoveries relative to the no-referee arm;
- **nondeterminism**, which would make results unreproducible;
- **evaluator, learner or oracle faults.** The oracle calls the referee's own evaluator and learner, so a bug there would be reproduced in the truth itself. Only the MRS checks guard against it.

**This reasoning does not carry over to Experiment 2-T0,** which runs on real data with no ground truth (Part I.5).

### I.2 Composition (summary)

Everything runs on the daily κ₂ and 𝒢₂ development worlds, not on 𝒢_1A. Every MRS item is bound, by hash, to the build that is evaluated (Exp 2 §B.3).

| ID | Check | Derived from 1A | Pass rule |
|---|---|---|---|
| MRS-1 | Same-machine determinism; after tuning, replay of 5 recorded tuning world-runs of A3–A5 made on the code-freeze runner and TCB (no new model tokens) | EK1; R7 (partial) | 0 differing bytes |
| MRS-2 | Inline point-in-time controls (§G.4.1: TE, PO, LP, VS, TI, CI, LN, AB, AC, CK, FP, DA), plus DSL causality (DC) and agreement of the sandbox evaluator library with `discover()` (EV) | §G.4.1 | 0 INVALID on 20 clean worlds; INVALID world-runs during the campaign |
| MRS-3 | Leak mutants LK01–03, 06, 07, 09–13, 15–18, 21, a horizon mutant, and 8 DSL-operator mutants, each with a κ₂ magnitude, designated control and liveness artefact | §G.4.2 | Each live, then detected in 20/20 trials |
| MRS-4 | G1 size screen in test mode (δ = 0), 400 null worlds | EK4 | Fail iff x ≥ 28 |
| MRS-4N | G1 size screen, negative family: exact encodings of up to 2 planted mechanisms per world as negative claims, δ_c = the largest §F grid value ≤ θ̂_o − 0.01 (H0 true with a margin), on 400 in-family non-null worlds | New | Fail iff x ≥ 28 |
| MRS-5, MRS-5N | Positive controls against a deliberately broken G1 and a broken negative statistic | PC-G1 | Each fires: x ≥ 73 of 400 |
| MRS-6 | G1 receipt invariance, 50 pairs, plus mutant M-R1 | R5.G1 | 50/50 identical; M-R1 detected |
| MRS-7 | Tamper and sealing: V1–V5, V7, V8, plus V12 (path traversal) and V13 (readable truth store, annex, replication store, seed store or audit log), including attempts with the agent runner's credentials | R6 subset (V12 and V13 were untested candidates in 1A §G.7) | 20/20 blocked and logged per V |
| MRS-8 | Canary tokens in every sealed store; scanning of every sandbox-visible byte, model request and response, claim and memory item | New | Planted exposure detected; 0 hits in clean runs |
| MRS-9 | ι₂ isolation conformance for the model-agent sandbox, the relay and the runner's access set | ι_1A conformance | All assertions hold |
| MRS-10 | Fresh random series IDs, unique across worlds (Exp 2 §C.2), padded file sizes, and a metadata-role probe (mechanism components, traps, attractive traps) | §C.8 | Every role AUC LB₉₅ ≤ 0.55 |
| MRS-11 | Oracle validated against closed forms on linear worlds, for every claim class and trap archetype with a closed form; coverage check; generator self-checks | §C.12 | Per-claim and aggregate tolerances (Exp 2 §B.3) |

**Not in the MRS** (Part II only):
- R1 and R4 at certification sample sizes;
- the AT1–AT13 and KF attack cells;
- R2 and the clean-room reference;
- R3 at 100 trials per class;
- R5 for G2 and G3, and the wall-clock rig;
- cross-architecture R7;
- G2 and G3;
- LK04, LK05, LK08, LK14, LK19, LK20, LK22 and LK23 (each with its reason in Exp 2 §B.3), and V6 (𝒢₂ has no recorder);
- the LLM red team and the knowing-adversary arm.

### I.3 Guarantees the MRS does and does not provide

| # | The MRS **does** provide (functional, known classes, κ₂ and 𝒢₂ only) | Strength |
|---|---|---|
| P1 | The as-of path and the DSL operators detect each listed κ₂ mutant (Exp 2 §B.3, MRS-3 table) | Each mutant detected in 20/20 trials: LB₉₅ per mutant 0.861 (1A Appendix A.4) |
| P2 | G1 is not grossly oversized under honest scripted use: the positive family at the boundary θ = 0, in a test mode with δ_c = 0 on 400 null worlds (MRS-4); the negative family on 400 in-family non-null worlds where H0 (θ ≥ δ_c) holds with a margin of at least 0.01 (MRS-4N), so negative size exactly at the δ_c boundary is not screened | A referee whose true per-world false-PASS rate is 0.10 fails the screen with probability 0.985; one at 0.05 fails with probability 0.048 (binomial arithmetic of 1A Appendix A.3) |
| P3 | Both size screens can fire in the settings they screen: PC-G1 (vault reads allowed) in the MRS-4 test mode, and PC-G1N (sign of d⁻ flipped) on the MRS-4N worlds | Each positive control fires with probability ≥ 0.825 at a true rate of 0.20 |
| P4 | G1 receipts release nothing that depends on the vault before closure | 50/50 pairs identical, and the planted mutant detected |
| P5 | Sealed stores (vault, replication data, truth store, annex, seeds, audit log) cannot be read or written from the sandbox for classes V1–V5, V7, V8, V12 and V13, and cannot be read with the agent runner's credentials (V13 only); planted canary exposure is detected | 20/20 per class; functional |
| P6 | Verdicts and scores replay byte-for-byte from recorded model outputs, on the evaluated build | 0 differing bytes |
| P7 | The oracle matches the closed forms on linear-Gaussian worlds, for the claim classes and trap archetypes listed in Exp 2 §B.3 (MRS-11); the trap design holds on stress worlds | Per claim within the achieved c·s_o + 10⁻³ (c multiplicity-adjusted); no aggregate bias beyond \|mean signed error\| ≤ 2·SE + 5·10⁻⁴ |

| # | The MRS **does not** provide | Consequence |
|---|---|---|
| N1 | Certified size at the R1 bound (0.07) or the R4 bound (0.075) | No certified false-PASS rate. The Experiment 2 benchmark *measures* false discoveries against truth instead |
| N2 | Resistance to adaptive attack (the R4 cells), including by the model researcher | Adaptive gaming shows up in the benchmark only as measured false discoveries and policy violations. It is not bounded in advance |
| N3 | G2 or G3 | The benchmark uses G1 only |
| N4 | Agreement with an independent implementation (R2) | A shared implementation bug would affect every referee arm alike, and the oracle, which calls the same evaluator and learner, would reproduce it. Only MRS-2, MRS-3 and MRS-11 guard against it |
| N5 | Timing, co-residency or filesystem-metadata side channels (beyond padding) | Untested, as in 1A |
| N6 | Vulnerability classes outside V1–V5, V7, V8, V12 and V13 (including V6) | Untested |
| N7 | Any guarantee under κ_1A, 𝒢_1A, real data or product configurations | Nothing transfers |
| N8 | The right to say "validated referee" (1A §K.2) | Still prohibited |
| N9 | Removal of the 1A §A.5 caveat | The caveat stays on every 1A conclusion. Experiment 2 carries its own "not certified" caveat |

### I.4 Cost

Part of the Experiment 2 benchmark build: about 1.5 engineer-weeks for the MRS libraries, on top of a referee core of about 3 engineer-weeks that reuses the 1A lean-build design, retargeted to κ₂. Compute ≈ 40 CPU-h for the MRS screens and mutants, plus ≈ 100 CPU-h for the inline controls run in every referee world-run of the campaign, metered to the TH (Exp 2 §P.3) `[INFERENCE]`.

**Relation to the 1A lean build.**
- **If Experiment 2 decision 1 is approved,** nothing in 1A is built now. The next step is drafting the Experiment 2-T0 pre-registration (documentation only). A later 2-T0 build, once separately authorized, needs only the Part I.5 subset. The MRS is built with the later Experiment 2 benchmark, and the 1A lean build is deferred.
- **The MRS does not replace the lean build as the §K.2 precondition for the full campaign.** It runs on κ₂ and 𝒢₂, not κ_1A and 𝒢_1A. It has no counterpart of EK3 (the calibration gate), EK5 (PC-G2) or EK6 (the solve-time projection), and it omits LK08 from EK2. Its EK1 and EK4 analogues do not transfer to κ_1A (CL-32).
- **Otherwise,** the Part II plan below stands.

### I.5 Which parts of 1A the first t0 demonstration needs

This is the recommended next experiment, "Experiment 2-T0" (`docs/experiment_2/PREREGISTRATION.md` §T.2): one t0 covariate finding on French national solar, confirmed on a sealed 2025 segment, replicated on a sealed 2026 segment and then prospectively, then built on.
- The first table maps the main 1A elements to that demonstration. Its "Needed" rows are the **referee subset for Experiment 2-T0**.
- The second table is the **gate**, to be carried into the 2-T0 pre-registration.
- The 1A specification is not changed. `[INFERENCE: recommendation]`

**Real-data trial units** (used by R3 and R5 below). The sealed segments are never read.
- **Pseudo-vault layout:** 2021–2023 as pseudo-discovery and 2024 as pseudo-vault, both inside the discovery window.
- **R3:** each mutant runs on 20 seeded, perturbed copies of the pseudo-vault (block permutations or block-bootstrap draws of the 2024 values). Detection means that copy's run ends INVALID. The 20/20 rule (LB₉₅ ≈ 0.861) is kept.
- **R5.G1:** 50 pairs that share the real pseudo-discovery data and differ only in two seeded block-bootstrap replacements of the pseudo-vault.

| 1A element | Needed for Experiment 2-T0? | Adaptation |
|---|---|---|
| B-SPEC canonical hypothesis and hasher (§B.3) | **Yes** | The hypothesis becomes a covariate claim in the 2-T0 schema (Exp 2 §T.4, item 1): catalogue ID, role (past or known-future), transform, scope and margins. **Referee-owned:** the model, weights, quantiles, context length and gate, and the whole t0 input construction: the API path; one fixed role encoding for past covariates; H per origin as a function of the origin only, never of the batch; a deterministic batch rule keyed by origin order; the MISSING and PAD mask conventions |
| B-REG known_at registry and row schema (§C.4a) | **Yes** | known_at for every ODRÉ vintage and every covariate, with the stage vintage table (Exp 2 §T.2) and the `vintage_substituted` flag. **Known-future rule:** every value of `future_covariates` over the whole span 1:T+H has known_at ≤ the gate, because t0 standardises and reads known-future covariates over the whole span. **Exemption:** functions of the timestamp, fixed geography and constants whose derivation uses discovery data only, verified by DA |
| B-ASOF as-of builder and the inline controls (§G.4.1) | **Yes** | Applied to t0's `context` and `future_covariates` arrays: TE, PO, VS, LN, TI, AC, CK, FP, AB (discovery outputs byte-identical when both sealed segments and the forward store are replaced by NaN), DA (the best-forecast choice, placebo construction and every threshold traced to 2021–2024 only), UA (daily units, 14-eligible-day blocks), LP (retargeted: admission of target history into t0's context), and RV (retargeted: every scope restriction evaluated is an entry of the fixed scope list published before discovery; Exp 2 §T.2). **CI, adapted:** the origin is 12:00 Europe/Paris on D−1; the local delivery-day assignment and period index k equal a static calendar table; target start − origin = 12 h + 30 min × k (steps 24–71 on a 48-slot day, 24–69 on the 46-slot day, 24–73 on the 50-slot day), as in Experiment 0's horizon and DST tests. **Forecast-level controls, new:** forecast-level PO and TE (for sampled origins t, rewrite or delete every value in the whole batch with known_at > t, rerun with identical shapes, and require byte-identical forecasts for t); batch-composition invariance (each sampled origin forecast alone and in its production batch agree within the pre-registered cross-runner tolerance or tighter); role conformance (every variate's role and type in the built input equals the claim's declared role and the pre-registered encoding) |
| B-DISC discovery service (§B.1) | **Yes** | `discover()` for Stage 1, stamped `EXPLORATORY`; checked by AB and LK13 |
| B-TGT target builder (§C.5) | **Yes** | The target vintage is stated per stage (Exp 2 §T.2 vintage table) |
| B-BASE baseline owner (§C.7) | **Yes** | Two referee-owned comparators, fixed on discovery data: t0 + K1 + a matched placebo of X (leg a), and the best Experiment 0 point forecast selected on 2021–2024 (leg b). After a replicated finding, the current best forecast includes it. This is 1A §A.4 item 12, untested in 1A |
| Learner L, elastic-net quantile regression (§C.10) | No | Replaced by pinned t0, which needs no fitting |
| B-VER G1 test and Holm (§D.1) | **Yes** | 14-day blocks of delivery days; shifted nulls at δ_a and δ_b; per-claim p = max(p_a, p_b), with Holm across ≤ 4 claims. **t0 numerical failures:** the pinned `tfc-t0` stack replaces non-finite outputs with 0.0 and only logs a warning, so the referee's adapter detects non-finite values before sanitisation and raises a TCB exception. In a claim's forecast, the claim gets p := 1. In a comparator or placebo forecast on a scored segment, every affected claim gets p := 1 and the stage is INVALID. In discovery, the event is logged in B-AUDIT and reported to the researcher as an error (Exp 2 §T.2, Forecaster) |
| B-VAULT single-use vault and sealed-set rule (§D.1, §C.2a) | **Yes** | Sealed segments: 2025-01-15 to 2025-12-31 (confirmation 1) and 2026-01-15 to the last month consolidated before the 2-T0 pre-registration freeze (replication), each with a 14-day embargo. The seal is procedural for public data, so custody rules apply (Exp 2 §T.2), and the prospective forward window is the hindsight-free test |
| G2 (§D.2) | No | — |
| G3 (§D.3) | No | The forward replication is a single-look, fixed-horizon test. 1A's G3 does not apply at a 12:00 D−1 gate without re-derivation: day D's forecast is issued before day D−1's outcome is known, so an interleaved split, a new L_P and a new clip rule would be needed. Any anytime-valid monitoring would be a separate, uncertified test specified in the 2-T0 pre-registration, or a later 1A amendment. It would not be 1A's G3 |
| B-LEDGER (§B.1a) | **Yes** | Every discovery call, submission and verdict is recorded. The ledger is the evidence the building investigation uses |
| B-AUDIT audit log (§B.1) | **Yes** | Required by the R6 subset and by the canary scanner |
| B-SBX sandbox and ι_1A conformance (§B.2) | **Yes**, if the AI researcher runs code | As Exp 2 ι₂: no network; the model relay runs outside the sandbox |
| §B.4 frozen interfaces and authorship | **Yes, reduced** | The catalogue, comparators, placebos, adapter and referee code are written and frozen by sessions other than the researcher, under the custody rules of Exp 2 §T.2 |
| B-EVID evidence package (§B.1, reduced; release per §B.2 and the §D.1 "At closure" row) | **Yes** | One package per finding, carrying its claim boundaries and stage vintages |
| B-SEED seed protocol (§I) | **Partly** | No world seeds. Seeds for the R3 perturbations, the R5 replacements, the matched placebos, the K4 placebos and the known-answer gate's synthetic series (planted-covariate noise and decoys), committed under the 1A §I-style protocol at a future ceremony (none generated now). The P_H commitment is ledgered before any sealed segment is fetched. **Custody per decision 7, which must be decided before the 2-T0 freeze** |
| §C.6 margin perturbations and the MARGIN-SENSITIVE label (§H.6) | **Yes**, for K2 and K3 covariates published near the 12:00 gate | Reruns with the publication time shifted, sealed until closure as in 1A §B.1a |
| §F.1 and §F.2 feedback policy and output channels | **Yes** | The 2-T0 channels (discover() outputs, receipts, verdicts, evidence packages, the release of per-day results) are listed, each with its control |
| Generator 𝒢_1A and the θ̃ oracle (§C) | No | Replaced by the **mandatory known-answer gate** on a semi-synthetic target built from discovery-era data (Exp 2 §T.2): a planted known-future and a planted past covariate must PASS, a decoy must not, and a one-step horizon shift must degrade the known-future result |
| R1 size (§G.2) | **Adapted** | After the vault closes: at least 100 harness-only K4 placebos, null by construction, each tested alone by the G1 statistic in 14-day blocks at one-sided α = 0.05 and δ = 0 against t0 + K1 + an independent placebo. The check is INVALID iff the PASS count exceeds the 95th percentile of its block sign-flip null, which calibrates for dependence between placebos. **Positive controls:** an anti-conservative verdict engine (testing on half-hour units, or an iid variance) and leaky placebos built from post-gate target values must each drive the check to INVALID |
| R2 power and clean-room agreement (§G.3) | No | Later (Part II) |
| R3 leak mutants (§G.4.2) | **Yes, subset plus new ones**, on the real-data trial units | LK01, LK02, LK03, LK06, LK07, **LK08 (DST; CI)**, LK09 (LP, retargeted), LK10, **LK11 (DA)**, LK12, **LK13 (AB)**, **LK14 (RV; an outcome-defined scope accepted)**, LK15, LK16, LK17, LK18, LK21, **LK22 (UA)**, LK23. **LK04, LK05 and LK19** retargeted as injections into the forward recorder's store or a synthetic replica of it, with **GA, PA and RC** for that recorder. **New t0 mutants, each with its designated control:** realised values passed as a known-future covariate (TE on `future_covariates`); the context part of a known-future covariate filled with values published after the gate (TE and PO on `future_covariates`); a time-function covariate whose parameters were fitted on data including a sealed segment (DA); a past covariate passed as known-future (role conformance); a past covariate standardised over the horizon (TE on the arrays); a context crossing the gate (TE); rows of different origins sharing one group_id (forecast-level PO); one shared known-future vintage for all origins in a multi-origin pass (TE on `future_covariates`); padding marked MISSING instead of PAD (batch-composition invariance); a recorder snapshot written after the gate with a backdated known_at (RC). Each live, then detected in 20/20 trials |
| R4 adaptive-attack campaign (§G.5) | No | Later (Part II) |
| R5 transcript invariance: receipts (§G.6, R5.G1) | **Yes** (cheap) | 50 pairs on the real-data trial units, plus M-R1 |
| R6 tamper (§G.7) | **Partly** | V1 (if the researcher runs code), V3, V4 (including a readable sealed confirmation segment), V5r and V5w, V6 (detected by RC against the forward recorder), V7, V8, V13 as in 1A §G.7 (a readable B-AUDIT store), plus a new t0-specific class **VT1** (a readable forward-window or evidence store before closure). Each with 20 scripted attempts and U_V liveness. **Canaries** in the harness's local copies of the sealed segments and the forward store, scanned in every sandbox-visible byte and model request. This detects harness exposure only, not public-data knowledge in the model |
| R7 determinism (§G.8) | **Adapted** | The pinned lock file and container digest; same-machine byte identity; a cross-runner tolerance fixed by a pre-specified measurement before discovery and resolved by the §H.6 FRAGILE rule. In Experiment 0, t0 forecasts differed by ≤ 0.003 MW per point across runners under the pinned stack (Phase 2), and by about 0.03 MW per point before numpy and pandas were pinned (Phase 1) |
| §E stand-ins and attackers | No | Later (Part II) |
| §H outcome mapping, §J dossier, §K.3 commercial condition | No | Later (Part II). Experiment 2-T0 has its own outcomes (Exp 2 §T.2) |
| §A.5 caveat | **Yes**, on anything that cites 1A | Experiment 2-T0 also carries its own "not certified" caveat |

**Gate for Experiment 2-T0** (to be carried into its pre-registration):

| When | Item | Pass rule |
|---|---|---|
| Before discovery | Inline and forecast-level controls (TE, PO, VS, LN, CI, TI, AC, CK, FP, AB, DA, UA, LP, RV; forecast-level PO and TE; batch-composition invariance; role conformance) | 0 failures on discovery data |
| Before discovery | R3 mutants, including the t0 mutants and the recorder injections | Each live, then detected in 20/20 trials on the real-data trial units |
| Before discovery | R6 subset and canaries | Each V: 20/20 blocked and 20/20 logged in B-AUDIT; a planted canary exposure detected; 0 hits in clean runs |
| Before discovery | R5.G1 | 50/50 byte-identical receipt pairs, and M-R1 detected |
| Before discovery | R7 | Same-machine byte identity for two runs; cross-runner tolerance measured and fixed |
| Before discovery | Known-answer gate | Every planted-covariate, decoy and horizon-shift condition met at its numeric threshold, fixed before discovery (Exp 2 §T.2, §T.4 item 13) |
| Before unsealing | P_H and the claim-batch hash tested on that segment | Ledgered before each sealed segment is fetched; the fetch's file hash and vintage counts recorded (at a future ceremony; nothing computed now) |
| Before the forward window | Recorder go-live | An RC-style cross-check of the first recorded gate |
| After each vault closes (validity, not gate) | K4 placebo size check and its positive controls | PASS count ≤ the 95th percentile of its block sign-flip null; each positive control drives the check to INVALID |

- **Stop rule.** Any failed gate item stops 2-T0 for your decision: fix and rerun, or stop.
- **Binding.** As in Exp 2 §B.3, each passed item is bound by hash to the components it depends on. The evaluated build must be byte-identical for those components.
- **Reopen rule.** A later-found leak or sealed-store exposure revokes the subset result and suspends every dependent finding, including building-investigation findings that depend on it.

**What this subset provides.**
- Point-in-time integrity of t0's inputs and forecasts for the listed leak classes, including the known-future, role, batching and recorder classes;
- a sealed, single-use confirmation, with a real-data size check that is itself shown able to fire;
- a mandatory known-answer check that the t0 covariate path can recover a planted signal and ignore a decoy;
- a ledger, determinism within a stated tolerance, and protection of sealed and forward stores against the listed tamper classes.

**What it does not provide** (specific to 2-T0; it replaces rows N1–N9 of §I.3 for this purpose):
- (a) **No ground truth.** The false-PASS rate is neither certified nor measured.
- (b) The placebo check tests the per-test calibration of **non-selected** placebos, not the researcher's adaptive selection.
- (c) **Adaptive gaming by the AI researcher is neither bounded nor measured.** Only the sealed replication and the prospective forward replication mitigate it.
- (d) A shared implementation bug (N4) can go undetected.
- (e) N3, N8 and N9 apply as written. N7 becomes: no guarantee transfers to κ_1A, 𝒢_1A, other real-data targets, gates or t0 revisions, or product configurations (see f). N5 applies without the padding exception (2-T0 has no padding control). N6 becomes: tamper classes outside those in the R6 row above are untested, in particular V2 (writable time-limit configuration), V12 (path traversal), and V1 if the researcher runs no code.
- (f) Nothing beyond one target, one gate and one t0 revision.

**Cost:** about 7 of the 9 itemised build engineer-weeks of Experiment 2-T0's estimate (Exp 2 §T.2): the gate checks (1.5 + 1.0), plus the registry and as-of path (1.0), adapter and `discover()` (1.0), comparators (0.5), vault, ledger and evidence packages (1.5) and forward recorder (0.5) lines `[INFERENCE]`. It does not require the 1A generator, the lean build or the full campaign.

---

## Part II. Full institutional referee certification (Experiment 1A campaign)

**Its criteria are unchanged from v0.2.** The v0.3 edits are:
- decision 8's recommendation, consequence and alternatives (the red team moves to the full-certification track, if Experiment 2 decision 1 is approved);
- cross-references to Experiment 2 in decisions 1, 5 (CL-41) and 7, and a "defer" alternative in decision 1;
- a CL-40 bullet in the Experiment 1B and Elexon section;
- the recommendation (deferral of decisions 1–6 and 8–10 and the v1.0 freeze, except decision 7) and its authorization path, including the note that the MRS does not substitute for the lean build; the scope table, the early-kill text, the checklist and the next prompt, which are now conditional on Experiment 2 decision 1.

Under your clarification it is **a later objective**: it may follow Experiment 2-T0 and the Experiment 2 benchmark.

**It certifies nothing about t0 as specified** (CL-39). A certification relevant to the t0 research loop would need an amendment defining a configuration with pinned t0 as the learner and t0's covariate roles in the generator.

It remains required before:
- any claim of a validated or certified referee;
- any use of certified guarantees, such as G2/G3 claims, product claims or evidence packages to third parties.

### Recommendation

**Recommendation** `[DECISION, subject to owner approval]`:
- **If Experiment 2 decision 1 is approved (recommended):** defer decisions 1–6 and 8–10 and the v1.0 freeze, because full certification is a later objective and freezing now would turn a later t0 configuration into a post-freeze amendment with a new P_H.
  - **Exception: decision 7 (seed custody).** Experiment 2 (§O.2) and Experiment 2-T0 (Part I.5, B-SEED) also use it. It must be decided before either is frozen, and before any seed or commitment is generated, even if the other decisions are deferred.
- **Otherwise:** approve `PREREGISTRATION.md` with the ten recommended choices below.

**What to authorize now:**
- **If Experiment 2 decision 1 is approved:** nothing in 1A. The next step is drafting the Experiment 2-T0 pre-registration (documentation only), which later needs only the Part I.5 subset. The MRS (Part I) comes with the Experiment 2 benchmark. The 1A lean build on 𝒢_1A and the full campaign are deferred.
- **Otherwise:** only the lean, non-certifying falsification build:
  - 3–4 engineer-weeks and ≤ 40 CPU-h `[INFERENCE]`;
  - no market data is used, Elexon is irrelevant, and 1B stays `BLOCKED_BY_ACCESS`;
  - it is the cheapest way to learn whether the architecture holds, whether the point-in-time controls catch obvious leaks, whether runs are deterministic, and whether the attack programme can break a deliberately naive referee (early kills EK1–EK7);
  - it certifies nothing.

**Authorize the full certification campaign separately:**
- only after the lean build ends without an unresolved kill (1A §K.2 precondition 1), and after the decision-9 condition is met. **The MRS does not substitute for the lean build** (Part I.4);
- it costs +6–10 engineer-weeks and 150–600 CPU-h if the measured solve time is ≤ 31–35 ms `[INFERENCE]`.

Until that campaign passes, the product may not claim a validated referee. Every certified conclusion carries the caveat: "Certified against the pre-registered scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher."

### Decisions requested (10)

| # | Decision | Recommended | Consequence of the recommendation | Alternatives and their consequences |
|---|---|---|---|---|
| 1 | **Campaign configuration κ_1A** (§C.10; D5, D6, D43) | 8 origins a day, 5 quantiles, quarterly refits, frozen λ; L = elastic-net quantile regression with a tiny ridge, so the solution is unique; LightGBM G not run | 150–600 CPU-h if the mean solve time is ≤ 35 ms (N = 2,000) or ≤ 31 ms (N = 2,400); measured at EK6. **Certification does not transfer** to the 1B configuration, to product configurations, to Experiment 2's κ₂, or to t0 | **1B configuration** (19 quantiles, 48 origins, weekly refits, per-refit CV, G gating): transfers directly, but plausibly needs 10–100× the compute `[INFERENCE]`. **Defer until a t0 configuration is drafted** (pinned t0 as learner L, with t0's covariate roles in 𝒢_1A; CL-39): no 1A freeze until then; certification relevant to t0 if run. Recommended if Experiment 2 decision 1 is approved |
| 2 | **R1/R4 world count, and repair-round threshold** (§G.5, §H.7; D21, D34) | **N = 2,400 per class stream.** Repair (if invoked) carries passing results forward and re-tests rerun cells at one-sided 99% CP | A referee exactly at α gets full scope with probability 0.956, and is wrongly declared INVALID (below minimum scope) with probability 0.010. Two-attempt false certification ≤ 0.055 per cell. Compute +7.3 M solves (≈ +14%) | **N = 2,000 (v2):** full scope 0.830; wrong INVALID 0.038. **N = 2,300:** 0.937 / 0.014. **Repair at 95%:** a failing-in-truth cell can be certified with probability up to 0.091 |
| 3 | **R7 scope** (§G.8; D16) | A 10% subset per stream, drawn after campaign close from M_post; plus a mandatory cross-architecture rerun on the same subset | ≈ +8.5 M solves in total | **Full rerun:** ≈ ×1.75 total compute; byte-identity shown for every output |
| 4 | **G3 parameters** (§D.3, §C.2; D20, D22) | L_P = 518 days; λ grid {0.05 … 0.8}; per-SP clip at the 99th percentile of \|ℓ^B − ℓ^H\| over the 365 days before registration (restricted to the hypothesis's regime); k slots ⌊L_P/k⌋ apart | **A G3 PASS certifies improvement in the *clipped* differential only.** Unclipped skill and the clip-flip rate are reported, not tested | **365 days:** −17% G3 compute; lower power. **730 days:** more power; +24% G3 compute |
| 5 | **Ground truth and embargo** (§C.9; D3, D4) | θ̃ is the exact conditional skill of the fitted forecasts; 21-day embargo | False PASS is defined for what the referee actually tests. The risk from regime persistence is measured directly by R1/R4. Experiment 2 uses a different estimand (CL-41) | **Generator-level null plus embargo ≥ regime persistence** (mean spell 45 days; no hard bound exists): counts learner-level skill as false PASS; shortens the vault or lengthens the worlds |
| 6 | **Economic gate** (§E.4; D14) | None. AT13 is kept as a statistical attacker, as you listed it | Smallest design; economic-gate correctness is not certified | **Add a synthetic variant-B gate:** a new false-PASS criterion with its own cells and world counts, and more effort |
| 7 | **Seed custody** (§I.3–I.4; D18) | A protected GitHub Environment (only the frozen tag may deploy; you are the required reviewer). S_I is generated by a job inside it; S_O by you. No public beacon. **Experiment 2 (Exp 2 §O.2) and Experiment 2-T0 (Part I.5, B-SEED) reuse the same custody, so this decision is needed before either is frozen** | No Claude Code session can read either secret. Aborts and operator-inducible voids are published and intersected, so they cannot be used as rerolls. The dossier lists every principal who could read the secrets | **A plain repository secret:** readable by anyone who can push a workflow; rejected. **Owner-run execution:** strongest custody, but you run the campaign. **Public beacon:** needs network at run time, and is only needed to re-hold a stage after an abort (a third principal's secret is the alternative) |
| 8 | **LLM red team** (§E.5) | **Changed in v0.3, if Experiment 2 decision 1 is approved:** defer to the full-certification track, as a 1A amendment run after the MRS-gated Experiment 2 benchmark (CL-31). **If decision 1 is rejected:** as in v0.2, mandatory in Experiment 2 per §H.8 | The §A.5 caveat stays on every 1A conclusion until that amendment runs and passes. The Experiment 2 benchmark measures the model researcher's gaming only as policy violations and false discoveries. **Experiment 2-T0 does not measure gaming at all** (Part I.5, item c) | **Include in 1A by amendment now:** could remove the caveat earlier, but needs a model snapshot, a brief, a sandbox and ≥ 2,400 worlds per cell; cost UNKNOWN. **Put a red-team arm into Experiment 2:** adds an arm and model cost, and mixes a security test into a knowledge benchmark |
| 9 | **Full-campaign authorization: commercial condition and budget** (§K.3, §K.1 EK7; D35–D37) | ≥ 10 front-office **and** ≥ 10 model-risk calls; neither v2 kill rule fires; ≥ 1 design partner confirms in writing that they will review the dossier. **EK7 budget: 14 engineer-weeks or 800 CPU-h** before the first certified R4 result | The Stage-2 spend is gated on a signal and on a realistic budget. The condition is **not** a PRODUCT SIGNAL | **v2's 9 engineer-weeks:** likely triggers EK7, given the 9–14-week estimate. **No commercial condition:** science first, with the risk of certifying a referee nobody asked for. **A paid pilot:** stricter; delays Stage 2 |
| 10 | **R2 rules** (§G.3; D10, D40) | v2's pooled agreement (≤ 25 disagreements in 2,500 worlds) with a borderline tolerance band. **Add** R2-G2/R2-G3: liveness ≥ 269/500 at θ = 10%, and ≤ 5/500 disagreements | A correct referee passes R2 with 0.958 (at power 0.995, disagreement 0.005). A G2 or G3 that can never PASS cannot be certified | **Strict per-θ agreement (v0.1):** passes only 0.089 of the time at a 1% disagreement rate. **No R2-G2/G3:** a dead G2 or G3 could be certified |

**Approved through the checklist rather than decided here:** deviations D1, D2, D7–D9, D11–D13, D15, D17, D19, D23–D33, D38, D39, D41, D42, D44, D45 (§M).

### Scope estimates

All `[INFERENCE]`; nothing has been measured.

| Stage | Engineering | Compute | Output |
|---|---|---|---|
| Lean falsification build (on 𝒢_1A; deferred if Experiment 2 decision 1 is approved) | 3–4 engineer-weeks | ≈ 1.7 M solves; ≤ 40 CPU-h if the solve time is ≤ 70 ms. The build stops for your decision if the projection after 50 worlds exceeds 40 | Non-certifying screens; measured solve time; go / no-go |
| MRS (Part I; on κ₂, inside the Experiment 2 benchmark build) | ≈ 1.5 engineer-weeks on top of the referee core | ≈ 40 CPU-h, plus ≈ 100 CPU-h of campaign inline controls (Exp 2 §P.3) | MRS pass or fail; certifies nothing |
| Experiment 2-T0 subset (Part I.5; inside the 2-T0 build) | ≈ 7 engineer-weeks of the 2-T0 estimate (2.5 of them for the gate checks) | Included in the 2-T0 estimate (Exp 2 §T.2) | Gate pass or fail; certifies nothing |
| Full certification campaign | +6–10 engineer-weeks (9–14 in total; v2 said 5–7) | ≈ 51–59 M solves: 150–600 CPU-h if the solve time is ≤ 35 ms (N = 2,000) or ≤ 31 ms (N = 2,400); ≈ 1,700–1,950 CPU-h at 100 ms | R1–R7 verdicts; certified scope; validation dossier |

**Earliest technical kill point:** EK1 (same-machine determinism), in week 1 of the lean build. On the Experiment 2 benchmark path it is EK-B1 (build weeks 1–7): a failure of MRS-4, MRS-4N or MRS-5 stops for your decision, and a second calibration failure is VOID-BENCHMARK (Exp 2 §P.2); MRS-1 follows in weeks 8–10. Experiment 2-T0's kill points are to be set in its own pre-registration. The earliest decisive kill for the adversarial programme is EK5 (PC-G2), after the calibration gate, about 2–3 weeks into the lean build: if a deliberately naive referee cannot be broken on 400 worlds, certification could show nothing.

### Experiment 1B and Elexon

- **Elexon, IRIS and NESO are irrelevant to 1A.** No 1A criterion uses market data.
- **1B remains `BLOCKED_BY_ACCESS`.** That is not a scientific failure. No endpoint was retried, no substitute data or market was used, and 1B was not redesigned.
- Experiment 2-T0 would use real historical ODRÉ data, which §H.8 (iv) reserves until a real-data point-in-time validation (1B or a successor). This is logged as CL-40 and routed to Experiment 2 decision 1.

### Approval checklist

- [ ] Decisions 1–10 answered, the recommendations accepted, or deferred as recommended (decision 7 is not deferred past the Experiment 2-T0 freeze).
- [ ] Every deviation listed in §M approved.
- [ ] Contradiction log (§L.1) reviewed:
  - its OPEN rows are resolved by decisions 1, 2, 5, 6, 9 and 10; for CL-30, CL-31 and CL-40, by Experiment 2 decision 1; and for CL-39, by Experiment 2 decisions 1 and 5;
  - §L.2 (items not adopted) accepted.
- [ ] §A.4 ("cannot establish") and the §A.5 caveat accepted.
- [ ] Outcome mapping, repair rule and Experiment 2 consequences (§H, including the §H.8 v0.3 note) accepted.
- [ ] Seed protocol and custody (§I, decision 7) accepted.
- [ ] Part I (MRS) and Part I.5 (the Experiment 2-T0 subset and its gate) reviewed together with Experiment 2 decision 1.
- [ ] CL-39 (no t0 in 1A) acknowledged. A t0 configuration for certification is a later amendment.
- [ ] Authorization follows the Recommendation. If Experiment 2 decision 1 is approved: nothing in 1A is authorized for implementation; the next step is drafting the Experiment 2-T0 pre-registration, and the MRS is authorized only later, together with the Experiment 2 benchmark. Otherwise: only the lean build is authorized. The full campaign needs a separate authorization under decision 9 and §K.2.
- [ ] Instruction given to freeze v1.0, or the freeze deferred (this draft is committed for review in PR #2, not frozen).

### Next Claude Code prompt (use only if you want 1A frozen now, as specified: κ_1A, no t0)

**Not the next step if Experiment 2 decision 1 is approved as recommended.** Use it only when you decide to freeze 1A, for example when certification resumes. If 1A is frozen now, a later t0 configuration requires a post-freeze amendment with a new P_H.

> On branch `experiment-1a-preregistration`, update `docs/experiment_1a/PREREGISTRATION.md` to v1.0 and `docs/experiment_1a/OWNER_REVIEW.md` accordingly:
> - apply my decisions below;
> - mark every deviation listed in §M as approved;
> - remove each [OPEN] label those decisions resolve, and list any that remain;
> - record Experiment 2 decision 1 (sequencing and gates) in the §H.8 v0.3 note and in CL-30, CL-31 and CL-40, and Experiment 2 decisions 1 and 5 in CL-39;
> - append a v1.0 change-log entry.
>
> Commit only files under `docs/`, push the branch, and update draft PR #2 (keep it a draft). Compute P_H exactly as defined in §I.2 and report it.
>
> Then STOP. Do not write any code, calendar or parameter table, seed, secret or commitment. Do not start the lean build or the MRS, and do not access Elexon or any market data. If Experiment 2 decision 1 was rejected, I will start the S-GEN and S-REF sessions separately.
>
> My decisions: 1 = …, 2 = …, 3 = …, 4 = …, 5 = …, 6 = …, 7 = …, 8 = …, 9 = …, 10 = …; Experiment 2 decisions 1 = …, 5 = ….
