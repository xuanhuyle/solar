# Experiment 2: owner review

Companion to `PREREGISTRATION.md` v0.1-draft (2026-09-24).

**Status: DRAFT.** It is committed for review in draft pull request #2 (branch `experiment-1a-preregistration`). Nothing is frozen or implemented. No P_H has been computed, and no seed exists.

## What your clarification changes

**You clarified** that the core is an AI researcher that uses **t0's covariate capabilities** to find which information improves forecasts, validates those findings, and builds on them. The immediate milestone is **one bounded, reproducible, independently confirmed predictive finding using t0, followed by an investigation that builds on it.**

**Neither the Experiment 1A design nor this benchmark exercises t0 or its covariates.**
- 1A's learner is elastic-net quantile regression.
- This benchmark's learner is ridge, on synthetic, obfuscated worlds.
- Experiment 0 ran t0 without covariates, by design.

Ten specific mismatches are listed in `PREREGISTRATION.md` §T.1. The most important:
- **The t0 covariate pathway is untested.** Known-future covariates (`future_covariates`) are standardised over the whole span and read bidirectionally, so any value in that span not known at the gate leaks. No leak catalogue covers them yet.
- **t0's public API treats past covariates as extra targets.** In the pinned package, `predict` types every context row as a target, so a past covariate is forecast jointly with the target. The paper's past-covariate role needs a hand-built input (M-10). Which encoding a claim uses must be fixed and checked by a known-answer test.
- **This benchmark produces no finding.** Its success is a statistical comparison over 75 synthetic worlds.
- **Experiment 0's evidence.** Zero-shot t0 lost to `blend_50` by 9.0% over all hours (MAE of the median), with 98.9% of the deficit at night. A finding must therefore be tested both for information value (against t0 with a matched placebo of the covariate) and for competitiveness (against the organisation's best forecast).

## Recommendation

**Recommendation** `[DECISION, subject to owner approval]`:
1. **Make the next experiment the t0 first demonstration, "Experiment 2-T0"** (§T.2). It targets French national solar (Experiment 0's setting), with pinned `t0-alpha` and a pre-registered point-in-time covariate catalogue.
   - The AI researcher proposes at most 4 covariate claims from discovery data (2021–2024).
   - They face sealed single-use confirmation on 2025, against two comparators: t0 with a matched placebo of the covariate (pinball loss), and the best Experiment 0 point forecast (MAE).
   - Surviving claims are replicated on a sealed 2026 segment (the first finding's **historical grade**), then prospectively on data collected after the claim-batch hash is ledgered and the recorder is verified live (its **hindsight-free grade**). The building investigation's claims are tested in their own forward window of the same fixed length, which starts after their own claim-batch hash, overlaps the premise's and ends about 1–2 months later (§T.2 Stage 5).
   - About 9–10.5 engineer-weeks of build (plus 0.5 for a Stage-0 audit before the freeze), 190–960 CPU-h and 0.7–2.8 × 10⁷ model tokens `[INFERENCE]`.
   - First finding, historical grade: about 3–4 months after approval (January–February 2027 if approved in early October 2026). Hindsight-free grade: about Q4 2027. The milestone as you defined it (the finding, followed by a building investigation scored in its own forward window) completes about 13–16 months after approval, November 2027 to February 2028.
   - Its referee needs only the subset and gate in the Experiment 1A owner review, Part I.5.
   - **Realistic expectation:** without weather forecasts (catalogue K3), confirmation is expected to end NO-FINDING or IMPROVES-T0-ONLY against the best forecast, and would consume the 2025 vault (§T.2, operating characteristics). K3 depends on a Stage-0 audit of weather-archive availability, which needs your explicit authorization.
2. **Authorize now only the drafting of the Experiment 2-T0 pre-registration** (documentation, next prompt below) **and, if you so decide under decision 1, the metadata-only Stage-0 audit within the §T.2 limits.** Authorize nothing in this benchmark.
3. **Keep this benchmark** as the later test of research competence at scale against matched controls, adapted to use t0 as its forecaster (decision 5).
4. **Keep full 1A certification** as a later objective, as you stated.

**What a CONTINUE on this benchmark would mean** (when it runs): controlled epistemic competence on synthetic worlds only. It is not evidence of tradable alpha, causal knowledge, real-data robustness or willingness to pay, and the referee it uses is not certified (§N).

## Decisions requested (10)

| # | Decision | Recommended | Consequence of the recommendation | Alternatives and their consequences |
|---|---|---|---|---|
| 1 | **Sequencing and gates** (§0.7, §T; §B.3; §Q CX-01, CX-02, CX-09, CX-10, CX-11; 1A §H.8 v0.3 note) | **Next: Experiment 2-T0**, gated by the Part I.5 subset and gate (1A owner review). **Later: this benchmark**, gated by the MRS (§B.3). **Later still: full 1A certification.** The LLM red team and the knowing-adversary arm move to the certification track. 2-T0 uses real historical ODRÉ data with the substitutes listed in CX-11, and only forward data earn hindsight-free credit. **Also authorize the Stage-0 metadata-only audit** of candidate sources before the 2-T0 freeze (§T.2 limits) | The first sealed confirmation comes about 10–13 weeks after the 2-T0 build starts (9–10.5 weeks of build, then 1–2 of discovery). The first finding's historical grade also needs the 2026 replication: about 3–4 months after approval. Its hindsight-free grade needs the forward window, which opens only when the claim-batch hash is ledgered and the recorder is verified live, and completes about Q4 2027. The milestone completes when the building investigation is scored in its own window, about November 2027 to February 2028. Every result carries a "not certified" caveat | **This benchmark next (as drafted):** exercises no t0 and produces no finding; about 15 engineer-weeks to its first model-based kill point. **Keep 1A §H.8:** every experiment waits for full certification (9–14 engineer-weeks, 150–600 CPU-h), is restricted to 𝒢_1A/κ_1A, which contain no t0, and may not use real historical data before a real-data point-in-time validation (1B is blocked). **No gate:** a leak through `future_covariates` or a sealed store would go unseen. **No Stage-0 audit:** K3 is excluded from the first catalogue, and confirmation is then expected to end NO-FINDING or IMPROVES-T0-ONLY |
| 2 | **Memory arm and the scope of the kill rule** (§K.3, §L, App. A.5) | Controls {A1, A2, A3}, plus **memory non-inferiority** against A4 (LB₉₅(A5 − A4) > −MEI) and a memory-harm kill (UB_{98.75}(A5 − A4) < −MEI). A5 is kept. Memory superiority becomes Experiment 3's primary endpoint | If memory is neutral in independent worlds and the rest of the system is strong (Δ = 0.6 against A1–A3), P(the TRK conditions of CONTINUE hold) ≈ 0.72 (0.99³ × 0.743) `[INFERENCE]`. Including EK-B2 survival, F1 and F2 at its conservative planning values, P(CONTINUE) ≈ 0.61 at a per-world false-validation rate of 0.01, or ≈ 0.52 at 0.02 (about 0.67 and 0.57 at m = 0.05; App. A.5, A.7; indicative only). Δ = 0.6 against A1 and A2 is optimistic, because A1 reaches every in-family exact encoding, and A2 does if an evaluation costs ≲ 0.2 CPU-s (§I.3). A memory that *harms* still kills | **Default (your literal rule: A5 must beat A4 too):** in the same situation P(KILL) ≥ 0.509 and P(CONTINUE) ≤ 0.010 from the TRK conditions alone (the other kill routes can only raise P(KILL)), although independent worlds let memory carry only procedural lessons. **Drop A5:** not recommended, because you listed it |
| 3 | **Sample size, interim and probes** (§K.3, §K.6, §K.7, S7) | 60 non-null + 15 null evaluation worlds, re-estimated blind within [60, 120] non-null; binding futility after 20 worlds using UB₉₅; **no extension** (AMBIGUOUS is final); 12-world transfer probe; 15-world model rerun | Per control, P(fails) = 0.51 when the system is no better (Δ = 0), and ≤ 0.011 at Δ = MEI. P(beats) = 0.88 at 1.5·MEI. EK-B2 stops with P = 0.29 at Δ = 0 and 0.04 at Δ = MEI; ≤ 0.20 under the two pre-registered linear learning curves with campaign mean MEI (σ_Δ = 1). All kill routes together wrongly kill a system exactly at MEI with probability ≤ about 0.17, or about 0.08 when the FDR gates are comfortably met | **100 non-null worlds:** P(fails at Δ = 0) = 0.77; about +67% primary model tokens. **UB₈₀ futility:** stops with P = 0.63 at Δ = 0 but also 0.19 at Δ = MEI, and 0.51 under the steeper learning curve. **No interim:** loses the week-16 kill and saves nothing. **A second A5 trajectory** on an independent world order: measures between-trajectory memory variance; about +75 A5 world-runs (0.75–3 × 10⁸ input tokens). **No transfer probe:** −24 model world-runs, and no early memory-transfer signal |
| 4 | **Effect and error thresholds** (§K.3, §K.4, §F, App. A.3) | MEI = 0.3 covered mechanisms per non-null world; δ_min = 0.01. **F1:** Clopper–Pearson UB₉₅ of the share of worlds with any false validated cluster ≤ 0.10 (at 75 worlds: at most 2 such worlds); **F1-kill** at LB₉₅ > 0.10 (13 or more). **F2:** for each referee control, the estimate of A5's pooled asserted false-discovery ratio minus the control's ≤ 0.05 **and** its UB₉₅ ≤ 0.10 (the shape of beats(c)); **F2-kill** at LB_{98.33} > 0.05. For a control with fewer than 20 asserted clusters in total, the control's ratio is taken as 0.05. False negative validations reported, ungated | A gain below about a third of a mechanism per world is treated as nil. F1 passes with probability 0.96 at a per-world false-validation rate of 0.01, 0.81 at 0.02, 0.61 at 0.03 and 0.27 at 0.05. F1-kill fires with probability about 0.034 at a rate of 0.10. F2 passes with probability 0.53–1.00 per control with no inflation (0.96 at the conservative planning values, 0.99 at m = 0.05) and at most 0.50 at an inflation of 0.05 (App. A.7) | **MEI = 0.2:** about 2.25× the worlds. **MEI = 0.5:** a modest real gain can be killed. **Ceiling 0.05:** at 75 worlds F1 passes only if no world has a false validation (probability 0.47 at a rate of 0.01, 0.22 at 0.02). **Ceiling 0.10 at 150 worlds:** passes with probability 0.96 at 0.03, for about twice the evaluation tokens. **Ceiling 0.20:** weak control. **F2 as UB₉₅ ≤ 0.05 alone (the earlier draft):** passes only 0.55 per control at the planning values with no inflation (0.41–0.93 at m = 0.05 and 0.22–0.74 at m ≥ 0.10; App. A.7), so CONTINUE would be unlikely even without inflation. **Gate false negative validations:** a KILL-type flag if LB₉₅ of their share exceeds 0.10 |
| 5 | **Forecaster inside this benchmark** (§C.11, §T.3) | **Pinned t0**, with DSL claims constructing t0 past or known-future covariates instead of ridge features. Adopted when this benchmark is re-drafted after Experiment 2-T0 | The benchmark then tests the research loop on the forecaster the objective is about. It requires re-specifying B*, M_c, the oracle estimand, the mechanism calibration and the trap truth conditions; the known-future leak mutants join MRS-3. A planted mechanism that t0 does not use becomes FALSE for every arm, so the calibration floor may fail. **The oracle becomes expensive:** about 6–28 CPU-h per claim at K = 20 for M_c alone (11–56 if B* forecasts are not cached per world; up to 8× at K = 160), and of order 10⁴–10⁵ CPU-h per campaign, unless a cheaper, validated truth for t0 is found. Cost to be established before re-drafting `[INFERENCE]`. 𝒢₂ must be checked for overlap with t0's pretraining generators | **Keep ridge (as drafted):** cheaper and exactly analysable, but it says nothing about t0 (§N item 13) |
| 6 | **Researcher model and budgets** (§H, §I.1, §P.3) | One pinned snapshot for A0 and A3–A5 (the most capable model available at freeze, with its training-data cutoff recorded); server-side tools off. Per world-run: C₀ = 2 CPU-h (binding for every arm), W₀ = 4 h, T₀ = 4 × 10⁶ input and 4 × 10⁵ output tokens (A5's memory writing inside T₀). Discovery evaluations are metered and reported, not capped | About 3.4–13.6 × 10⁸ input tokens in total at N = 60 (5.7–22.7 × 10⁸ at N = 120), and about 1,300–2,200 CPU-h (1,800–3,200 at N = 120). The sequential A5 chain takes about 3.6–14.5 days at N = 60 and 6.8–27 days at N = 120. Money cost = tokens × the snapshot's price on the run date: `[OPEN]` | **T₀ = 1 × 10⁶:** about 3× cheaper; the agent may be starved. **A cheaper model:** tests a weaker researcher |
| 7 | **Generator transparency** (§C.9, App. C) | Public in-family specification plus a **sealed out-of-family annex** (hash committed; 20% of non-null worlds, 16% of evaluation worlds). The family stays out of the brief | You can audit the in-family design now. The annex protects mechanism search only; trap avoidance and null-world false-discovery control rest on the public constructions | **Fully public, no annex:** tuning to §C is undetectable. **Fully sealed:** you cannot audit the design before the results. **Extend the annex** (proposed for the re-draft, §C.9) to a sealed trap archetype and a sealed null-world variant |
| 8 | **A3's data access** (§D.3, §I.2) | Raw vintage-tagged files, the sandbox and the definition of B*; no `discover()`, as-of API, evaluator library or vault. A3's claims are credited only after the harness's as-if confirmation | A3 against A4 measures the whole referee: point-in-time path, discovery service, sealed confirmation and charging | **Give A3 the as-of API and `discover()`:** then only sealed confirmation is isolated |
| 9 | **Strength and authorship of the scripted plan** (§I.2, §B.4) | A1 = a generic priority-ordered screen within C₀ with stability selection, written by S-SCR without the generator specification, audited against the forbidden list, with tuning parity (≤ 10 engineer-days, the same 40 tuning worlds, identical feedback) | "Beats the scripted plan" means beating the strongest non-AI plan buildable without knowledge of the hidden family and with equal effort. **Every in-family exact encoding lies at DSL depth ≤ 1 (about 10⁴ expressions), which A1 reaches within about 2.6 × 10³ evaluations and A2 exhausts if an evaluation costs ≲ 0.2 CPU-s (§I.3; settled by the EK-B1 Q meter).** In-family, CONTINUE therefore measures selection and validation under a fixed budget, not hypothesis generation; generation is only probed by the 12 out-of-family worlds (S9, exploratory). The EK-B1 headroom rule (ORC − A1 ≥ 0.25) is the most likely calibration failure; the single permitted calibration amendment can create headroom only by weakening the mechanisms (strength or J; §L) | **A simple hand plan:** easier to beat; overstates the AI's contribution. **A plan written with §C knowledge:** an upper bound, but tuned to the family the AI arms cannot see. **Enlarge the in-family family** (depth-2 and depth-3 forms such as gated hinges, diff/ma transforms and two-series products, with the DSL candidate count stated in §C.5, so that no screen within C₀ can enumerate it): the benchmark would then also test generation, but Appendix A.4, ORC coverage and the EK-B1 calibration must be re-derived. Suggested for the re-draft after Experiment 2-T0 |
| 10 | **Common-model-bias mitigation** (§B.4, §K.5, §N item 12) | S-GEN uses a different model snapshot from the researcher; the annex forms are chosen by you or by an author outside the model family; a separate session audits the scripted and agent artefacts; the contamination check (training cutoff, recall probe); an independent human or different-vendor review before freeze | Reduces, and measures part of, the risk that the researcher exploits regularities of a harness written by its own model family. It does not remove it: this pre-registration and its review were written by the same model family | **Same snapshot everywhere:** cheaper, but confounded. **No outside review:** shared blind spots in the design are not excluded |

**Approved through the checklist rather than decided here:**
- the §Q.2 deviations DV-01 to DV-08 (DV-06 and DV-07 follow decisions 1 and 5);
- the §Q.3 interpretations of your instruction;
- the §C and §E specifications.

**Decisions 2–4 and 6–10 matter only when this benchmark runs,** and can be deferred until it is re-drafted after Experiment 2-T0. **Experiment 2-T0 needs its own equivalents of decisions 6 (researcher model and knowledge vintage) and 10 (common-model mitigation),** decided in its own pre-registration before its freeze.

**Choices for the Experiment 2-T0 pre-registration** (§T.4; not decided here):
- the t0 variant (recommended: `t0-alpha`);
- the past-covariate role encoding (recommended: the paper's past-covariate role through a hand-built input, checked by the known-answer gate);
- the primary loss slice (recommended: all hours);
- milestone strictness (recommended: both comparators; alternative: information value only);
- whether weather forecasts (K3) enter the first catalogue, which needs the Stage-0 audit;
- an optional negative-claim family;
- the researcher model, its knowledge vintage, and who audits the known_at rules;
- common-model mitigation (the 2-T0 equivalent of decision 10);
- the replication design (recommended: 2026 sealed replication, then the forward window, with the building claims in their own later-starting window of the same length; alternative: a disjoint second forward window, completing in about the second half of 2028);
- seed custody, which is **1A decision 7** and must be decided before the 2-T0 freeze.

## Scope estimates

All `[INFERENCE]`; nothing has been measured.

| Stage | Engineering | Compute | Model tokens (input) | Output |
|---|---|---|---|---|
| **Experiment 2-T0** (recommended next; §T.2) | ≈ 9.0 engineer-weeks of build itemised (9–10.5 with contingency), plus 0.5 for the Stage-0 audit before the freeze | ≈ 2.3 × 10⁶ t0 calls, about 190–960 CPU-h (per-call cost measured in build week 1) | ≈ 0.7–2.8 × 10⁷ | First sealed confirmation about 10–13 weeks after build start; first finding, historical grade about 3–4 months after approval; hindsight-free grade about Q4 2027; milestone complete about November 2027 to February 2028 |
| This benchmark, EK-B1 (no model calls) | Weeks 1–7 of its build | ≈ 250 CPU-h (development runs of ORC, A1 and A2 at the binding CPU budget, and MRS screens) | 0 | Benchmark calibration; earliest design VOID |
| This benchmark, agent harness and MRS | Weeks 8–10 | ≈ 40 CPU-h | 0 (MRS-1 replays recorded tuning runs) | MRS pass or fail |
| This benchmark, tuning and post-tuning calibration gate | Weeks 11–15 | Included below | ≤ 2.4 × 10⁸ | Frozen arms; calibration pass or fail |
| This benchmark, EK-B2 and full run | Weeks 16–18 at N = 60 (A5 chain 3.6–14.5 days); about weeks 16–21 at N = 120 (6.8–27 days) | Total ≈ 1,300–2,200 CPU-h at N = 60, ≈ 1,800–3,200 at N = 120, with ridge (much more with t0; decision 5) | Total 3.4–13.6 × 10⁸ at N = 60, 5.7–22.7 × 10⁸ at N = 120 (EK-B2: 0.6–2.4 × 10⁸) | §L outcome |

**Totals for this benchmark:** about 15 engineer-weeks (14–17, including tuning), and 4–4.5 months elapsed. Full 1A certification (9–14 engineer-weeks: the 3–4-week lean build, which the MRS does not replace, plus the +6–10-week campaign) is separate and later.

## Kill, continue and void for this benchmark, in one page

Exact rules: §L and Appendix B. MEI = 0.3; "TRK" is the number of planted mechanisms covered by an arm's validated, true claims in a world.

- **Before the evaluation ceremony** (development worlds; ledgered pass or fail): VOID-BENCHMARK if, after the single permitted calibration amendment, ORC covers < 0.80 of in-family mechanisms, or the headroom rule fails (ORC − A1 coverage < 0.25 at the expected planted count), or ORC-A covers < 0.5 of out-of-family mechanisms or leads A1 there by < 0.25. Separately, at the post-tuning gate and with no amendment, VOID-BENCHMARK if LB₉₅ of A0's pooled AUC for mechanism components or for traps exceeds 0.60.
- **VOID-BENCHMARK** (the design failed, not the thesis), for events found before campaign close:
  - **always:** a TH-attributed critical leak in the harness's own code (generator, truth store, oracle, replication, orchestrator); a TH-attributed reproducibility mismatch in generation, the oracle, replication or scoring; generator self-check failures in > 2% of worlds;
  - **only if no KILL-type rule applies:** harness errors in > 2% of world-runs (pooled or for any of A1–A5) or INVALID world-runs in > 2% (pooled or for any arm); a TH-attributed leak or mismatch in the agent runner, tool wrappers or relay; an MRS revocation whose rerun you decline; an amendment after C2-eval.
  - **A completed KILL is never turned into a VOID** except by the "always" triggers. Findings after campaign close only turn the outcome into KILL-LEAK or KILL-REPRO (SUT) or withdraw a CONTINUE (TH).
- **KILL** (the thesis fails as tested), any of:
  - **central rule:** for some control c in 𝒞 ({A1, A2, A3} under the recommended decision 2; {A1, A2, A3, A4} under the default), UB_{98.75}(TRK_A5 − TRK_c) < 0.3;
  - **F1-kill:** LB₉₅ of the share of worlds with a false validated A5 cluster > 0.10 (13 or more of 75 worlds);
  - **F2-kill:** for some c in {A1, A2, A4}, LB_{98.33} of A5's pooled asserted false-discovery ratio minus c's > 0.05 (for a control with fewer than 20 asserted clusters, LB_{98.33} of A5's ratio > 0.10);
  - under the recommended decision-2 alternative, **memory harm:** UB_{98.75}(TRK_A5 − TRK_A4) < −0.3;
  - a SUT-attributed critical leak (KILL-LEAK) or verdict-level replay mismatch (KILL-REPRO);
  - the EK-B2 futility stop: UB₉₅ of TRK_A5 − TRK_A1 over the first 16 non-null worlds < 0.3 (KILL-FUTILITY).
- **CONTINUE:** for every control in 𝒞, LB₉₅(TRK_A5 − TRK_c) > 0 and the mean difference ≥ 0.3; F1 passes; F2 passes (for each referee control, A5's excess false-discovery ratio has an estimate ≤ 0.05 and UB₉₅ ≤ 0.10); zero critical leakage; the replay subset reproduces; and, under the recommended alternative, LB₉₅(TRK_A5 − TRK_A4) > −0.3.
- **AMBIGUOUS:** anything else. **Final; no extension.** Reported as "not established".

**Outcomes of Experiment 2-T0** (§T.2), per claim, with INVALID and UNTESTABLE taking precedence separately for the historical result and the forward result (a forward INVALID or UNTESTABLE-FORWARD leaves an earned FINDING-REPLICATED standing; building claims are scored as in §T.2 Stage 5):
- INVALID (a point-in-time, forecast-level, placebo, known-answer, reproducibility or t0 numerical failure);
- UNTESTABLE (fewer than 6 blocks in a replication segment or window);
- **FINDING-REPLICATED** (confirmation and 2026 replication pass on both comparators: the first finding, historical grade);
- **FINDING-REPLICATED-FORWARD** (plus the forward replication: the first finding, hindsight-free grade);
- IMPROVES-T0-ONLY (information value confirmed at confirmation 1, competitiveness not: a bounded finding, not the milestone);
- INCONCLUSIVE / UNDERPOWERED and NOT-REPLICATED (judged per comparator leg against its own margin);
- NOT-TRANSFERRED-TO-REAL-TIME (reported only);
- NO-FINDING (not evidence that the covariate is uninformative).

**Milestone complete:** the first finding reaches FINDING-REPLICATED-FORWARD, and at least one building claim, frozen before its own forward window, is scored to PASS, NOT-REPLICATED or INCONCLUSIVE / UNDERPOWERED. The report names which. The milestone does not require the building claim to succeed, following your wording.

## Contradictions with Experiment 1A (details in §Q.1 and 1A §L.1, CL-30 to CL-41)

1. **Gate.** 1A §H.1 and §H.8, and memo v2 §17, gate Experiment 2 on a 1A certification outcome. The recommended gates are the Part I.5 subset for Experiment 2-T0 and the MRS for this benchmark (decision 1). The 1A text is unchanged; a v0.3 note records the proposal.
2. **Adversaries.** 1A §H.8 makes an LLM red team and a knowing-adversary arm mandatory in Experiment 2, and 1A decision 8 deferred the red team "to Experiment 2". Neither the benchmark nor Experiment 2-T0 contains them; they move to the certification track.
3. **Generator and configuration.** 1A §H.8 restricts Experiment 2 to 𝒢_1A and κ_1A. This benchmark uses 𝒢₂ and κ₂, and Experiment 2-T0 uses real ODRÉ data with t0. No 1A certification transfers to either.
4. **Guarantee classes.** Only G1 (plus replication) is used. Both experiments use G1 claims of a different form from 1A's. 1A's G3 does not apply at 2-T0's 12:00 D−1 gate.
5. **Researcher code.** 1A §H.8 (iii) requires a new sandbox certification for researcher code. Here, exploratory code runs under a conformance-checked sandbox, and claims stay declarative.
6. **No t0 anywhere in 1A.** Its learner and generator do not involve t0 (CL-39). Certifying a t0 pipeline would need a later 1A amendment with t0 as the learner.
7. **Real historical data** (CL-40). 1A §H.8 (iv) reserves real historical data until a real-data point-in-time validation (1B or a successor). Experiment 2-T0 runs discovery and both sealed segments on 2021–2026 ODRÉ data, with Experiment 0's tests, the Part I.5 controls and the forward recorder as substitutes. Only the forward window earns hindsight-free credit.
8. **Truth estimand** (CL-41). 1A grades the conditional skill of the fitted forecasts on the vault days used; this benchmark grades the expected skill of the claim pipeline under the forward law. A 1A-style conditional grade is reported as secondary.

## Experiment 1B and Elexon

- **1B remains `BLOCKED_BY_ACCESS`.** It is not a scientific failure, and it has not been redesigned.
- Neither this benchmark nor Experiment 2-T0 uses Elexon, IRIS or NESO. None of them was contacted.
- Experiment 2-T0's candidate data sources (ODRÉ; a weather-forecast archive for K3) were **not** contacted either. Any Stage-0 audit needs your explicit authorization.

## Approval checklist

- [ ] Decision 1 (sequencing and gates) answered, including whether the Stage-0 metadata-only audit is authorized. Decisions 2–10 answered now, or deferred to the benchmark's re-draft.
- [ ] §T accepted as the basis for drafting the Experiment 2-T0 pre-registration, including the binding requirements in §T.4.
- [ ] 1A decision 7 (seed custody) answered, or scheduled before the Experiment 2-T0 freeze.
- [ ] §Q.2 deviations and §Q.3 interpretations approved.
- [ ] §A.4, §A.5 and §N (claim boundaries and the mandatory caveat) accepted.
- [ ] The adversarial review log (§R) reviewed.
- [ ] The Experiment 1A owner review v0.3, Part I (MRS) and Part I.5 (the t0 demonstration subset and gate), reviewed together with decision 1.
- [ ] Nothing is authorized for implementation. The next step is documentation only, plus the metadata-only Stage-0 audit if decision 1 authorizes it (§T.2 limits).

## Next Claude Code prompt (use only if you accept the recommendation)

> On branch `experiment-1a-preregistration`, draft `docs/experiment_2_t0/PREREGISTRATION.md` (v0.1-draft) and `docs/experiment_2_t0/OWNER_REVIEW.md` for Experiment 2-T0. Base them on `docs/experiment_2/PREREGISTRATION.md` §T.2 and §T.4, and on the Experiment 1A owner review Part I.5 (subset and gate):
> - one bounded, reproducible, independently confirmed t0 covariate finding, then a building investigation;
> - French national solar at the 12:00 D-1 gate, with the stage vintage table;
> - a pinned t0 model with a referee-owned input construction (API path, past-covariate role encoding, batching, masks);
> - a pre-registered covariate catalogue with known_at rules, and the Stage-0 audit rules;
> - a claim schema of its own;
> - sealed single-use confirmation on 2025 against t0 with a matched placebo (pinball) and the best Experiment 0 point forecast (MAE), then a sealed 2026 replication, then a fixed-horizon prospective forward replication;
> - custody rules for the sealed segments;
> - the known-answer gate, harness-only placebos and the size check with its positive controls;
> - t0-specific leak mutants, including for `future_covariates`, roles and batching;
> - a determinism rule with a cross-runner tolerance;
> - the researcher model and knowledge vintage, common-model mitigation, and seed custody (as `[OPEN: 1A decision 7]` if deferred);
> - an operating-characteristics table and an itemised estimate;
> - claim boundaries.
>
> Also record my decisions 1 and 5 as a draft revision (Experiment 2 v0.2-draft; 1A v0.4-draft; not v1.0, not frozen, no P_H):
> - in `docs/experiment_2/PREREGISTRATION.md`, update §0.4, §0.7, CX-01, CX-02, CX-09, CX-10, CX-11 and the approval fields of DV-06 and DV-07, and add a §S change-log row;
> - in `docs/experiment_1a/PREREGISTRATION.md`, update the §H.8 v0.3 note and CL-30, CL-31, CL-39 and CL-40, and add a §N row. Change no 1A criterion. Keep §A–§G, §H.1–§H.7, §I–§K, §M and Appendices A–C byte-identical, and verify that against the previous commit;
> - record my decisions in both owner reviews.
>
> Commit only files under `docs/`, push, and update draft PR #2 (keep it a draft).
>
> Then STOP. Do not write code, generate seeds, freeze anything or compute P_H. Do not download or query any dataset (ODRÉ, weather archives, Elexon or others), with one exception: if my decision 1 authorizes the metadata-only Stage-0 audit, perform that audit on ODRÉ and weather-archive metadata only, within the §T.2 "Stage-0 audit limits", and ledger every file, endpoint and date window it touches.
>
> My decisions: 1 = … (Stage-0 metadata audit: authorized / not authorized), 5 = …; the others: now = … / deferred. 1A decision 7 (custody) = … / deferred until the 2-T0 freeze.
