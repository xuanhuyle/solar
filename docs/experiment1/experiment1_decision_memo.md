# Experiment 1 decision memo, v2: validate the referee first

*v2, 2026-09-23. Replaces v1, which is kept as `experiment1_decision_memo.v1.md`. The ~44k-word technical version (`experiment1_decision_memo_full.md`) now opens with a v2 addendum. The repository is untouched at `406c92c`; no Experiment 1 code has been written.*

---

## Framing (new in v2)

**The product hypothesis** is a customisable, AI-native **junior quant researcher** that a professional trading organisation hires. A deterministic point-in-time harness acts as the **independent referee** it works inside.

- **Experiment 1** validates the referee.
- **Experiments 2–4** test the researcher: autonomy (2), knowledge accumulation (3) and economically grounded incentives (4).

v1 judged parts of the *product* through the limits of a first *public-data* experiment. That was a conflation. Every limit below now carries one of two scope labels:

- **[Exp 1 scope]** — true only of the public-data experiment.
- **[binds the product]** — true whoever the researcher is and whatever data the customer holds.

**Evidence labels:**
- **FACT**: checked against a primary source (docs, client source, PyPI, repository content), either by me or by a research agent. Sources are in the full version and in `referee_research.json`.
- **INFERENCE**: reasoned, not sourced.
- **UNKNOWN**.
- **UNVERIFIED**: from a search summary only; treated as UNKNOWN for decisions. Most publisher, preprint and regulator hosts were blocked.
- **SIM**: from in-session simulations that were not saved. Indicative only; re-running them as saved, seeded artefacts is part of 1A.

### What v2 changes, and where v1 was wrong

| v1 statement | v2 status |
|---|---|
| "Commercial thesis is the weakest link"; "consulting-sized ceiling" | **Re-scoped [Exp 1 scope].** It was assessed for a stand-alone forecasting or feed-validation tool, not for an AI researcher. The product's commercial case is **untested** (§13) |
| "Every result is 'beyond public information'" | **[Exp 1 scope].** A deployed researcher works on the customer's own data and baseline |
| "Baseline access is a blocking problem" | **[Exp 1 scope] in its v1 form** (needing the buyer's forecasts under NDA). **It changes form in the product:** the customer must supply a runnable, codified baseline, meaning its production pipeline or its outputs with known_at. That is an integration cost, alongside security, data governance, on-premise deployment and accountability (INFERENCE) |
| DE-LU is STOP | **[Exp 1 scope]: STOP only for a *free historical* test.** A customer with licensed vintages is a different case |
| "Broad thesis not credible as stated" | **Reframed.** Automated discovery at scale is not how the product can work. The *principles* under it **[bind the product]** and become referee design requirements: a holdout is consumed by use, and small effects need a lot of data. The *magnitudes* **[Exp 1 scope]** belong to this public GB target and must be re-estimated per customer target (§1, §3) |
| **"Any further reuse of the holdout is charged against the ledger at α = 0.005"** | **Wrong. Withdrawn.** Once a researcher sees graded verdicts or an evidence package, a flat charge does not bound adaptive reuse. In SIM, false significance reached 40% after 20 reuses and 95% after 50. v2 replaces it with three guarantee classes (§10) |
| Verdict ladder (FAIL / INCONCLUSIVE / INTERESTING / STRONG) released as-is | **Corrected.** Graded verdicts leak roughly a sign bit per query, and in SIM the false-PASS rate reached 0.69–0.98 at k = 30. During any adaptive phase the referee returns only PASS / NOT-PASS |
| Exp 1 = one GB real-data test | **Split.** 1A is referee validation (synthetic, adversarial; needs no Elexon access) and is primary. 1B is the GB workload, unchanged and still gated on Stage 0. **A GB FAIL is a valid referee outcome** |
| v1 recommendation: RESEARCH MORE BEFORE CODING (Stage 0 only) | **Still RESEARCH MORE BEFORE CODING**, now with two gates that need no code: the 1A pre-registration and 1B Stage 0 (§20) |

---

## 1. Executive judgment

**Is the thesis technically credible enough to investigate? Yes, as a researcher-inside-a-referee system**, provided three constraints are designed in from day one. Each one **[binds the product]**:

1. **Fresh data, not researcher intelligence, bounds certified throughput.**
   - **The principle [binds the product]:** a sealed holdout is consumed by adaptive use, so certification must use data that arrives after the claim is frozen.
   - **The magnitudes [Exp 1 scope]** are SIM estimates for this public GB target:
     - one fixed-n confirmation of an effect *near the MDE* needs about 1.4 years of data (37 batches);
     - an anytime-valid confirmation needs about 2–3 years;
     - at 1–3% effects it can take much longer (v1 SIM: a true 2.5% effect was confirmed only 13–14% of the time with 1 year of data);
     - a holdout supports about 3 confirmatory families per market-year.

     These numbers must be re-estimated for each customer target.
   - On targets like this one, the product is therefore *a few certified, time-indexed claims per target-year, plus unlimited clearly labelled exploration*, not autonomous discovery at scale (INFERENCE).
   - Cross-sectional targets with thousands of near-independent units would loosen this (INFERENCE; D: "not limits of the referee concept").
2. **An LLM researcher cannot be credited with skill on history before its knowledge vintage.**
   - LLMs recall pre-cutoff outcomes, and effective cutoffs can differ from reported ones (Dated Data: FACT; wider literature: UNVERIFIED).
   - Pretraining is an unledgered look at any earlier holdout, and no known_at contract can block it.
   - Historical windows can therefore validate the *referee* and serve as the *researcher's* discovery zone. Credit for *researcher* skill comes only from data later than both the knowledge vintage and the pre-registration freeze (INFERENCE).
   - **Scope:** this binds wherever the target or its drivers are public history (market prices, public fundamentals). For proprietary or anonymised customer data, the extent of contamination is UNKNOWN. A knowledge-vintage record is required either way.
   - This fits the product, which works forward on live data anyway.
3. **The referee is a security boundary, not a norm.** Frontier agents game evaluators that can be exploited:
   - Palisade's chess environment: o3 attempted a hack in 88% of runs (FACT: paper source).
   - SWE-bench agents read future commits via `git log --all` (FACT: issue #465).
   - Models that learned to reward-hack sabotaged a safety-research codebase 12% of the time (FACT: Anthropic, Nov 2025).

   Instructions help only partly. "Don't cheat" prompts reportedly had near-negligible effect (METR, UNVERIFIED), while an explicit abort option reportedly cut cheating from 54% to 9% (UNVERIFIED): useful, not sufficient.

   The referee must be a separate trust domain, with declarative submissions, sandboxed model code and a tamper-evident ledger.

**Recommendation (§20): RESEARCH MORE BEFORE CODING.** It is bounded to two gates that need no code:
1. **The 1A pre-registration**, a document you approve. Your approval is the BUILD condition for 1A code. 1A depends on no unverified external data.
2. **1B Stage 0, checks k1–k7**, read-only audits: IRIS archive coverage, first-price timing, UploadTime genuineness, licence. Passing them, plus your approval, is the BUILD condition for 1B code.

**What would make me more pessimistic:**
- 1A cannot be made to pass the adaptive-attack campaign without destroying power. In that case the referee's guarantees would be scoped to non-adaptive use.
- Buyer calls show that firms will not grant an agent autonomy whatever the evidence quality.

**What stays true from v1:**
- **Scientific:** Exp 0's lessons (§2); GB is the only free-data market where a point-in-time revision test is *conditionally feasible, unverified* [Exp 1 scope]; for 1B, FAIL or INCONCLUSIVE is the most likely outcome, because the MDE (1.2–3.2%) sits close to the plausible effect (1–3%); t0 is irrelevant to Exp 1; architecture Option C.
- **Practical:** the run #11 artifact deadline (2026-10-13).

---

## 2. Lessons from Experiment 0: now requirements for the referee

Unchanged from v1 in substance (FACT, run #11 outputs). The full tables are in v1 §2.

- **The baseline decides the verdict.** t0 went from +5.8% over prev_day to −9.0% [−13.8, −4.3] against an untuned blend.
  - The referee owns the baseline, not the researcher.
  - The baseline includes every previously accepted finding, so credit is only given for contribution beyond the organisation's current best, as with Numerai's MMC.
- **Apparent skill was information age** (the 24 h vs 48 h bands). The referee reports skill by information age for every source.
- **Sophistication added a failure mode** (t0's night floor), and **gains were concentrated** (the top 10 days carried 77% of t0's gain). Concentration and drop-best-days gates are kept.
- **The day is the unit of inference.** SIM: treating half-hours as independent gave a 75% false-positive rate.
- **Leakage was blocked by assertion plus poisoning tests over one shared registry.** The pattern is kept, re-keyed to per-row known_at, and extended to the *researcher's* inputs: its memory, retrieval corpus and knowledge vintage.
- **Pinning gives reproducibility within tolerances.** Tolerances must never sit near a decision threshold, because a researcher could exploit them.
- **Pre-registration worked because it was a code constant.** It is generalised to a hashed hypothesis spec that the referee canonicalises and charges.
- **Do not generalise:** models that censor their own future inputs; zero publication lag; definitive-only data; clipping at zero; a fingerprint that hashes NaN as −1; a cache key without code identity; Holm applied only in prose; vacuous asserts; hand-carried numbers.

---

## 3. What you are probably wrong about

### Where my v1 was wrong
See the Framing table. In short: the commercial verdicts were scoped to the wrong product; α-per-reuse accounting was invalid; graded verdicts leak.

### Assumptions to challenge in the new framing

1. **"A smarter researcher yields more certified findings."**
   - Not beyond what fresh post-freeze data allows. The principle **[binds the product]**; the magnitudes are per-target (§1).
   - The value is disciplined throughput and honestly retired negatives, not volume.
   - Time-to-verdict is a product KPI.
2. **"Historical backtests can show that the AI researcher is good."**
   - Not for an LLM whose knowledge vintage post-dates the window **[binds the product]**.
   - The most-cited open system, RD-Agent(Q), feeds test-segment IC and returns back into the LLM's "Replace Best Result" decision (FACT: RD-Agent source code). Its default 2017–2020 test window sits inside any modern LLM's pretraining (INFERENCE).
   - TradingAgents' 2026 changelog lists real look-ahead bugs, including a memory store returning lessons resolved after the trade date (FACT).
3. **"Instructions or norms will keep an agent honest."** Only partly (§1.3). The referee must be adversarially robust, and its guarantees must be measured under attack (1A, R4–R6).
4. **"The referee can let a researcher reuse a historical holdout if each reuse is charged."**
   - Not with informative feedback (SIM, §10). For low-effective-sample targets like this one (tens of dependent blocks), only three mechanisms carry guarantees under both adaptivity and serial dependence (§10; INFERENCE).
   - Thresholdout, Ladder and differential-privacy guarantees assume i.i.d. units and are close to vacuous at about 37 blocks (INFERENCE; the primary theorems are UNVERIFIED).
5. **"The researcher is the moat."** The researcher layer is crowded:
   - open-source loops: RD-Agent, TradingAgents, AlphaAgent, QuantaAlpha (FACT: repositories);
   - large funds building in-house: Man Group's "AlphaGPT", Balyasny, Bridgewater (UNVERIFIED; Bridgewater's use of Claude is FACT per Anthropic's announcement);
   - funded start-ups: KelAI, a full-loop "AI Quant" for funds (YC Spring 2026, $5M seed; UNVERIFIED).

   No verified public system offers an agent-independent point-in-time referee (UNKNOWN whether any exists privately). Differentiation plausibly comes from the **referee plus its evidence**, not from the agent (INFERENCE).
6. **"A rigorous referee will show the researcher adds value."**
   - Maybe not. Once leakage is controlled, published LLM trading agents mostly lose their edge (DeepFund, KTD-Fin, FINSABER, Look-Ahead-Bench: UNVERIFIED).
   - A good referee may mostly return FAIL on the researcher: scientifically correct, commercially awkward. Plan for it.
7. **"Governance is the wedge."**
   - US bank model-risk guidance SR 26-2 (April 2026, replacing SR 11-7) reportedly **excludes generative and agentic AI** from scope (UNVERIFIED).
   - The likely first buyers, non-bank energy traders, face weak model-governance pull (INFERENCE).
   - Governance is a door-opener and collateral, not the primary wedge (§13).
8. **"Incentives will shape a frozen LLM's behaviour."** An incentive only reaches an LLM through one of four channels: the prompt, its memory, selection among configurations by referee score, or fine-tuning/RL. Selection is itself an optimiser (best-of-n Goodhart). Exp 4 must say which channel it tests (§18).
9. **"Knowledge accumulation is additive."** Memory is a new leakage channel:
   - future-resolved lessons;
   - holdout statistics written into memory;
   - learned referee regularities, i.e. in-context reward hacking.

   Memory must be point-in-time data with a firewall (§18).
10. **Retained from v1, re-scoped:**
    - DE-LU and France cannot host a *free historical* point-in-time test **[Exp 1 scope]**.
    - Lag and regime claims are not identifiable at 1–3% effects **[binds the product]**.
    - "Currently leading" needs live decay monitoring **[binds the product]**.
    - Explanation of *in-sample* lead/lag is commoditised (nixtla 0.9.0 `explain()`, released 2026-09-21: FACT, verified on PyPI) **[binds the product]**.

---

## 4. Market landscape (rewritten for the new product)

| Layer | What exists | Label |
|---|---|---|
| **AI quant-research agents** (hypothesis → code → backtest → LLM feedback) | RD-Agent(Q), AlphaAgent, QuantaAlpha, Alpha-GPT, two "QuantAgent" projects, TradingAgents, FinAgent, FinRobot. Every one checked runs the same loop, and none separates an independent point-in-time referee from the agent | FACT (repos) / UNVERIFIED (papers) |
| In-house agentic research at funds | Man Group (reportedly "several dozen" agent-devised signals approved, humans vet); Balyasny; Bridgewater | UNVERIFIED (Bridgewater–Claude: FACT) |
| Start-ups | KelAI: a full-loop "AI Quant" for funds (YC Spring 2026, $5M seed); validation method undisclosed | UNVERIFIED |
| Autonomous-scientist systems | Sakana AI Scientist, Agent Laboratory. Documented pitfalls: hallucinated results, p-hacking, editing their own time limits | UNVERIFIED |
| Point-in-time data and vintages | Energy Quantified instances, Volue INSTANCE curves, Exabel `known_time` | FACT (client code) |
| Vintage-aware backtesting | OpenSTEF 4.4.3 (2026-09-21) | FACT |
| In-sample lead/lag explanation | nixtla 0.9.0 `explain()`, tsfresh, Tigramite | FACT |
| Incremental-contribution scoring | Numerai CORR + MMC (MMC = covariance after neutralising to the stake-weighted meta-model); v3 staking multipliers 3×CORR + 9×MMC | FACT (Numerai docs) |
| Model-risk tooling | ValidMind (open library 2.13.14: no point-in-time, vintage, walk-forward or multiplicity logic found), Yields.io, CIMCON, SAS, Moody's, ModelOp and others | FACT (ValidMind wheel) / UNVERIFIED (others) |
| Price/imbalance forecasts (the v1 lens) | Volue, Dexter, Meteologica, Enfor, Kpler | UNVERIFIED |

**Where whitespace plausibly remains (INFERENCE):**
1. **An independent referee for AI researchers**: point-in-time known_at contract, sealed vaults, α-wealth ledger, adversarial robustness, signed evidence packages. Absent from every public system checked.
2. **Research throughput whose claims survive that referee**, delivered as a customisable researcher running inside the customer's environment.
3. **Referee-grade evidence as governance collateral**, a door-opener with bank model-risk teams, given the SR 26-2 gap for agentic AI (UNVERIFIED).

**Already commoditised:** the agent loop, vintage storage, backtesting and in-sample explanation.

---

## 5. Decision: what Experiment 1 is

**Experiment 1 = 1A (primary) + 1B (secondary).**

- **1A — Referee validation.** Synthetic known-answer worlds, planted leaks, an adversarial p-hacking and tamper campaign, reproducibility.
  - It answers: *does the referee deliver its stated operating characteristics, including against an adaptive adversary?*
  - It needs no external data.
- **1B — Real-data calibration workload.** v1's GB design, unchanged in substance.
  - Question: do point-in-time NESO WINDFOR revisions add information about the first-published GB imbalance price 2 h ahead, beyond a strong public baseline?
  - It answers: *does the referee run end-to-end on real vintaged data and return a trustworthy verdict?*
  - Its science result (C1/C2) is secondary. **FAIL, INCONCLUSIVE and STRONG are all valid referee outcomes.**

**Why GB remains the workload for 1B** (v1 §5, unchanged): it is the only examined market where a free point-in-time test is *conditionally feasible, unverified*. Both the target and the revisions carry machine-checkable availability times (IRIS UploadTime + publishTime: FACT that the tags exist; whether they are genuine is UNKNOWN until Stage 0). The most likely 1B science outcome is FAIL or INCONCLUSIVE (v1 §1). Every alternative is rejected for v1's reasons [Exp 1 scope]. The Belgian fixed-vintage data and ERCOT (postDatetime) remain the replication and fallback domains.

**Why not validate the referee only on synthetic data:** synthetic worlds cannot exercise real vintage pathologies. Examples are synthetic publishTimes on migrated history (FACT: IGCPU, 2023-01-01) and platform re-releases (FACT: the August 2025 IRIS release). 1B is the referee's contact with reality.

---

## 6. Data reality

- **1A:** no external data. Null and planted worlds come from a pre-registered generator. It covers:
  - AR dynamics;
  - regime switching with durations longer than 14 days;
  - heavy-tailed spikes and negative values;
  - 46/50-period clock-change days;
  - publication lags, including lags correlated with stress, which is an attack surface;
  - revisable vintages with synthetic "migrated" publishTimes.

  Seeds are drawn after the pre-registration is committed.
- **1B:** unchanged from v1 §6.
  - All sources are free.
  - Decisive UNKNOWNs remain: IRIS archive start and completeness; whether the first `DISEBSP` message is near-real-time; whether UploadTime is genuine (including across the August 2025 IRIS release); the BMRS licence.
  - The sandbox still cannot reach Elexon (403).
- **Product [binds the product]:**
  - A customer deployment must supply known_at for its own data. The referee's registry assigns known_at; the researcher never does.
  - A recorder, meaning first-seen capture, is the gold standard wherever vendors expose no issue time.

---

## 7. Leakage and gaming threat model

v1's 34 data-leakage threats all still apply to 1B (full version §7). v2 adds the classes an *adaptive AI researcher* introduces. Each is tested in 1A or in Exp 2.

| New threat | How it fools the referee | Control (tested where) |
|---|---|---|
| **Feedback mining / boosting** | Ensembling candidates selected on holdout feedback until one passes (SIM: sign-bit feedback → 0.89–0.98 false PASS at k = 30) | Guarantee classes, §10. Constant NOT-PASS during adaptive phases (1A R4, R5) |
| **Graded-verdict leakage** | INCONCLUSIVE vs FAIL is nearly a sign bit when the SE is about 1% | Only PASS / NOT-PASS until a vault closes (1A R5) |
| **Variant splitting and correlated variants** | One idea split into many claims (SIM: 6 split claims → 22% false claims vs 4% as one family) | The referee defines and clusters families (by source × transform, and by correlation of loss differentials); one α charge per cluster (1A R4) |
| **Forking paths / resubmit-with-tweaks** | Free re-rolls over transform, loss, windows, regimes | A canonical spec hash covering every degree of freedom; every submission and near-duplicate is charged; the ledger is organisation-wide, not per identity (1A R4) |
| **known_at margin exploitation** | The 1% of rows outside a lag bound may be exactly the stressed, informative days | The referee assigns known_at; perturbation reruns at +15 min, +1 h and next publication flag margin-dependent skill; a delay-vs-stress audit (1A R3, 1B) |
| **Seed, tolerance and configuration shopping** | Results inside a tolerance band around the SESOI; configuration changes | Seeds drawn by the referee after submission; tolerances away from decision bands; a configuration hash on every verdict; a configuration-sensitivity sweep (1A R7) |
| **Placebo and regime shopping** | Calendar proxies that the known placebos preserve; outcome-defined regimes | A partly hidden, randomised placebo library; a referee-fitted flexible-calendar arm; regimes from the referee's library or α-charged (1A R4) |
| **Economic-check targeting** | Optimising for the optimistic execution variant or for directional bias | Gate on variant B only; calendar-conditional naive trading controls; MPPM alongside the deflated Sharpe ratio (1B, Exp 4) |
| **Harness tampering** | Editing tests or time limits, patching graders, reading targets or future state from the environment | Separate trust domain; declarative specs; model code in a network-less sandbox that sees only the as-of snapshot; hash-pinned referee code; planted vulnerabilities must be detected (1A R6) |
| **Look-ahead through model weights** | Hypotheses chosen using remembered outcomes | A knowledge-vintage record; researcher credit only after max(knowledge vintage, freeze); recall probes; a chronologically consistent control researcher (Exp 2) |
| **Retrieval and memory look-ahead** | Date-filtered search leaks the future; memory holds lessons resolved later | A vintaged document corpus under known_at; memory items carry known_at; future-lesson poisoning tests (Exp 2–3) |
| **Human-in-the-loop channel** | Staff read sealed results and nudge the agent | Separation of duties in code: vault keys and unseal rights sit with a non-researcher principal, and every unseal is ledgered (1A R6; product) |

---

## 8. Experiment 1 specification

### 8A. Experiment 1A: referee validation (primary)

| # | Item | Specification |
|---|---|---|
| 1 | System under test | The referee: as-of builder; target builder; learners L (L1 linear quantile regression) and G (LightGBM, corroboration); verdict engine; vaults; α-wealth ledger; sandbox runner; canonical spec schema |
| 2 | Worlds | A pre-registered generator (§6) with GB-like structure. Null worlds (no X effect) and planted worlds with X effects of 1, 2, 3, 5 and 10% pinball skill. Planted-leak worlds, one per leak class |
| 3 | Horizon and origins | As in 1B (h = 2 h, half-hourly origins), so that 1A exercises the same code paths |
| 4 | Period | Synthetic calendar spanning warm-up, discovery, embargo, a confirmation vault and a "prospective" segment, with 1B's lengths (182-day training, 365-day discovery, 518-day confirmation in 37 batches) |
| 5 | Researcher stand-ins | (a) An honest scripted analyst following a fixed plan. (b) The attacker library: random submitter; combination/boosting attacker, one per feedback type; forking-paths sweeper; optional-stopping poller; near-duplicate resubmitter; Sybil (two identities); side-channel prober (timing, errors); regime and placebo shopper; variant splitter; known_at-margin exploiter; seed/tolerance shopper; economic-check targeter; harness tamperer (against planted vulnerabilities). (c) A *knowledge-free* search arm (random or grammar-based over the same hypothesis space). (d) Optional: an LLM red-team agent with an exploit-finding brief, which becomes mandatory in Exp 2, together with a *knowing adversary* whose pretraining overlaps the window. **Unless (d) runs, every certified scope reads "scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher"** |
| 6 | Query budgets | k ∈ {10, 30, 100} submissions per campaign |
| 7 | Feedback designs compared | Naive (graded verdicts and numbers; the positive control) vs referee v2 (§10). Exploratory output from the discovery zone is unrestricted |
| 8 | Statistics | Claim-level false-PASS rate per world; power per planted size; INVALID detection per leak class; transcript invariance; tamper detection; reproducibility |
| 9 | Replications (proposals, fixed by the operating-characteristic calculation in the pre-registration) | R1: 2,000 null worlds per guarantee class offered. R2: 500 planted worlds per effect size. R3: ≥100 injected trials per leak class plus ≥100 clean worlds. R4: 2,000 null worlds per attacker × k cell for referee v2 (400 for development screening); 400 worlds for the naive-referee positive control. R5: ≥50 holdout pairs per attacker script. R6: ≥20 attempts per planted vulnerability |
| 10 | Seeds | Drawn from a commit-reveal scheme after the pre-registration hash is committed |
| 11 | Outputs | `referee_verdict.json` (REFEREE-VALID / VALID-WITH-SCOPE / INVALID, per property) and a **validation dossier for the referee**, organised under model-risk headings: intended use; conceptual soundness; implementation verification; operating characteristics with CIs; limitations; configuration hash; change log |
| 12 | Criteria | §17 R1–R7 (R8 is the 1B data gate) |
| 13 | Compute | About 150–600 CPU-hours (INFERENCE), **only if** attackers work on cached per-day loss differentials from a pre-fitted candidate library for each world, with the same worlds reused across cells. Refitting per submission would cost roughly 10× more. The attacker × replication grid dominates |
| 14 | Cost | £0 data |

### 8B. Experiment 1B: GB real-data workload (secondary)

This is v1 §8, all 25 items, with the following amendments:

- **Verdict release.** C1/C2 verdicts are computed in the single-use Stage 2, as in v1. The graded ladder and evidence package are released only once, after the vault closes. **No later reuse of the confirmation window is confirmatory**; the α = 0.005 reuse rule is deleted.
- **Contamination labels.**
  - The confirmation window is labelled *"designer-contamination not excluded"*: the designing model's training overlaps 2025–26.
  - A recall probe of the designing model on window events is recorded before unsealing.
  - Post-freeze prospective days remain the only fully clean evidence.
- **Known_at perturbation reruns.** Run at +15 min, +1 h and next publication. Margin-dependent skill is flagged.
- **Scope statement.** The 1B verdict states that the single-use-holdout guarantee is validated only against knowledge-free search on pre-cutoff real data.
- **Expected outcome.** FAIL or INCONCLUSIVE is the most likely result, because the MDE (1.2–3.2%) is close to the plausible effect (v1 §1). This is a valid referee outcome.
- **Mock validation.** Someone who did not build the referee reviews the evidence package cold and records:
  - time to review;
  - the questions it could not answer;
  - the model-risk headings left empty.

  Descriptive only. **No product-regulatory conclusion is drawn from 1B.**
- **Unchanged:** target (first-published SSP), baseline B, families F1–F8, learners, the z-pinball primary metric, SESOI 2.0%, Holm α = 0.04, placebos, the economic check (gate on variant B only), and Stage 0 kills k1–k7.

---

## 9. Model tournament

- **1A:** the "models" are the referee's own learners (L, G) and the attacker library. No foundation model is needed.
- **1B:** as v1.
  - N1–N6 naive rules.
  - L is the instrument of record; G corroborates.
  - Chronos-2 answers only the sophistication question, on post-freeze days.
  - t0 is excluded. That is about *Exp 1*, not the product: in the product, models are tools the researcher may choose, and the referee judges them.
- **Exp 2 and later:** the researcher's backbone LLM is recorded as part of its knowledge vintage (exact snapshot ID, reported and probe-estimated cutoff). A **chronologically consistent control researcher** (a small time-cutoff model) runs on the same brief as a contamination diagnostic (UNVERIFIED capability).

---

## 10. Predictive-information methodology: three guarantee classes

**Rule.** Every output about data used for confirmation is spent budget. Multiplicity counting does not protect against adaptive reuse. For low-effective-sample targets (tens of dependent blocks), only these three routes produce a **confirmed** claim (INFERENCE). Broad cross-sections are an open question (§19.9):

| Class | Mechanism | Guarantee | Cost |
|---|---|---|---|
| **G1 Single-use vault** | A pre-declared batch of ≤4 hypotheses, tested once. Holm/Bonferroni over batch means with t critical values. Full evidence released after | FWER ≤ α, provided the hypotheses were chosen independently of the vault data. The batch-means t under heavy tails is asymptotic (INFERENCE). A designer or researcher whose pretraining covers the vault can break independence, hence the contamination label | Consumes the window |
| **G2 Retire-on-first-PASS vault** | Sequential queries with a pre-registered α-spending sequence γᵢ (Σγᵢ ≤ 1). Every non-pass returns a **byte-identical NOT-PASS**: no sub-label, estimate, timing difference or error. The vault retires at the first PASS or when the budget is exhausted | FWER ≤ Σγᵢα ≤ α, provided that (i) each test is valid conditional on all pre-vault information (embargo ≥ regime persistence; conditional null), (ii) the vault is the researcher's only channel to that data, with no humans, other vaults or 1B releases leaking it, and (iii) each vault yields at most one confirmed claim. INFERENCE (derivation: the transcript up to the first PASS equals the fixed all-FAIL sequence). Verified empirically by R4–R5 | Power falls with the number of queries |
| **G3 Forward, anytime-valid** | The hypothesis is hashed and timestamped, then evaluated only on data with known_at > registration + embargo ≥ h. The evidence is an e-process on a bounded transform of the loss differential, under a **weak** conditional-mean null: the running average of the conditional-mean transformed loss differential is ≤ 0 (comparecast-style, split into h interleaved subsequences). The claim therefore reads "X added skill *on average* over [r, T]" | Valid under optional stopping and selection on past data (FACT for the comparecast mechanics; INFERENCE for the application) | About 1.5–2× the data of a fixed-n test (SIM); the null is on the transformed loss |

**Supporting rules:**
- **Discovery zone.** Unlimited queries and detailed feedback, always labelled *exploratory*. No confirmed claim can come from it.
- **Dependence-valid multiplicity only:**
  - Holm/Bonferroni for G1;
  - α-spending or online fallback for online FWER;
  - LOND-dep / LORD-dep for FDR (FACT: onlineFDR docs); e-LOND / e-BH on e-values (validity under arbitrary dependence is UNVERIFIED).
  - **Never** LORD++, SAFFRON, ADDIS or α-investing across overlapping time windows: their docs require independent p-values (FACT: onlineFDR docs).
  - Any wealth-earning scheme pays only for hypotheses in a pre-declared novelty class, so sure-thing claims cannot refill α.
- **The referee owns** the families, the baseline (including accepted findings), the loss and transform, the drop rules, equal tuning budgets for B and B+X, and seeds.
- **Units.** Days or batches; the effective sample size is reported in every package. No per-half-hour thresholds.
- **Retained from v1:** nested same-learner ablations; claims per family, never per lag; phase-preserving placebos; mediation labels ("market channel" vs "physical / forecast-combination"); the five-rung ladder. Only rung 3 is tested; rung 4 is a label; rung 5 is never claimed.
- **Why mining thousands of covariates still cannot produce fake discoveries:**
  - confirmation only through G1–G3;
  - every submission charged on an organisation-wide ledger;
  - referee-defined families;
  - placebo gates;
  - in-sample screens run only as a competitor arm.

---

## 11. Explainability and the evidence package

Each confirmed claim ships with a signed evidence package containing:

- **The claim and its validity:**
  - its **guarantee class** (G1, G2, G3, or exploratory);
  - its **validity window** ("X added skill over [r, T]");
  - effective sample size, α spent, and bits released against the vault;
  - incremental skill for L and G with intervals;
  - placebo distributions and positive controls;
  - regime table; skill by information age; mediation decomposition; encompassing regression; rolling decay monitor; calibration.
- **Provenance and reproducibility:**
  - known_at lineage per prediction;
  - pre-registration hash;
  - configuration hash;
  - referee version and the exploit classes it was tested against;
  - ledger entries.
- **For researcher-generated claims (Exp 2 and later):**
  - the **knowledge-vintage record**;
  - full agent traces, generated code and tool-call logs, hash-linked. Auditors reportedly detected pitfalls far more often with logs and code: 55% → 82% (UNVERIFIED).
- **A "cannot supply" section**, mapped to model-risk headings: tiering and materiality, business-use suitability, human approvals, execution-layer testing, conduct and market-abuse testing.
- **Language:** never "validated"; always "referee verdict under configuration ⟨hash⟩".

Historical analogues and LLM narratives are **omitted from Exp 1** (as in v1): they protect against no identified failure mode, and they invite a rung-1/2 story to be read as rung 4. In Exp 2 and later, researcher-written narratives appear only as labelled traces, never as evidence.

---

## 12. Economic sanity check

This remains v1's frozen rule for 1B:
- ±0.5 MWh when |median forecast − MID_ref| > £5/MWh;
- £1.5/MWh cost;
- execution variants A and B.

**Hardening:**
- Gate on **variant B only**.
- Add calendar-conditional naive trading controls alongside always-long and always-short.
- Report MPPM next to the deflated Sharpe ratio. The deflated Sharpe's N counts **every** evaluation, which requires that all data access goes through the logged referee API.

**For the product [binds the product]:**
- Any researcher-proposed strategy with simulated P&L needs execution-realistic simulation with capped exposure.
- It also needs conduct tests that reject edges depending on influencing settlement or imbalance prices (REMIT prohibitions; UNVERIFIED specifics).

The four distinctions stay separate:
1. forecast skill;
2. tradable information;
3. net value after costs;
4. commercially useful software.

---

## 13. Commercial reality (rewritten; the product thesis is untested)

**Exp 1 cannot answer the commercial question, and v1's "consulting-sized" verdict does not apply to this product.** What can be said now:

**Who buys (INFERENCE).** The segments below are energy- and commodity-heavy because Exps 0–1 are. **The product itself is not tied to energy**, and which domain comes first is an open question for the buyer calls.
- **Banks with commodity desks:** the front-office quant research head is the economic buyer of the researcher. Model risk management (reporting to the CRO) is the gatekeeper and a possible buyer of referee tooling.
- **Hedge funds and non-bank energy traders:** the head of quant, trading or research buys. Formal model-risk functions are rarer.

**The value proposition to test:**
- *Research throughput whose claims survive an independent referee*: a customisable junior researcher, deployed in the customer's environment, producing a few certified, time-indexed claims per target-year plus clearly labelled exploration, with evidence packages usable as governance collateral.
- The researcher is the paid layer. The referee is the trust anchor. It could be customer-run and source-available, with the customer's second line holding configuration and vault keys, to answer the "self-grading" objection.
- **Unresolved tension (moat) [binds the product].**
  - If the referee is source-available, it is not the moat.
  - The paid researcher layer is the crowded one.
  - A moat would then have to come from some combination of:
    - the researcher's *referee-certified* track record;
    - the point-in-time knowledge base it accumulates (Exp 3);
    - integration into the customer's data and point-in-time pipeline;
    - the referee's validation dossier.

  UNRESOLVED; tested in the buyer calls and in Exps 2–3.

**For:**
- No verified public system offers an agent-independent point-in-time referee (UNKNOWN privately).
- The most-cited open agent loop, RD-Agent(Q), gets holdout discipline wrong (FACT: its feedback code passes test-segment metrics to the LLM). Other loops were not audited at code level.
- The SR 26-2 carve-out of agentic AI (UNVERIFIED) leaves banks without a template, and a measured referee dossier could fill part of that gap.
- In-customer deployment removes v1's public-data limit and turns baseline access into an integration task (the customer supplies a codified baseline).

**Against:**
- The agent layer is crowded, and top funds build in-house (UNVERIFIED).
- Clean researcher credit is prospective-only, so ROI arrives slowly relative to sales cycles (INFERENCE).
- A rigorous referee may mostly FAIL the researcher.
- Senior sceptics doubt GenAI alpha (UNVERIFIED).
- Adjacent research copilots price at about $3k–20k per seat per year (UNVERIFIED). No public pricing for autonomous quant researchers was found.
- Autonomy may be capped by accountability regimes regardless of evidence (INFERENCE).
- The independence objection.
- On-premise and DORA / outsourcing demands raise delivery cost (UNVERIFIED specifics).

**Positioning rule:** never promise autonomous discovery at scale. Quote time-to-verdict honestly: months per claim at 1–3% effects.

**Commercial track, run in parallel with 1A (no code):** two call scripts, about 10 calls each.
- **(a) Front office** (quant, research and trading heads at funds, energy traders, battery optimisers): current agent use; who validates agent-generated signals; whether their agents' backtests overlap model cutoffs; willingness to deploy an agent inside their environment; data-access constraints; what a junior quant's first-year output looks like; willingness to pilot.
- **(b) Model risk / validation at banks with commodity desks:** whether validation controls multiplicity or adaptive reuse today; whether they would accept vendor-generated evidence; the effect of SR 26-2's agentic carve-out; hours per model validation; who signs.

**Pre-registered kill rules for the commercial track:**
- **Governance as a wedge dies** if fewer than 3 of 10 model-risk respondents say a point-in-time / multiplicity evidence package is missing today *and* would cut validation effort.
- **The researcher product dies at this stage** if fewer than 3 of 10 front-office respondents would pilot an in-environment agent whose claims are referee-certified, given prospective-only credit.
- **Positive PRODUCT SIGNAL (restored from v1, re-targeted):**
  - at least 3 of 10 respondents name an existing budget line of **≥ £10k/yr** that such a researcher or referee would draw on, and
  - at least **1** commits to a paid pilot, or to an in-environment trial with its data and baseline.

  Stated interest alone is not a signal.

---

## 14. Repository architecture decision

**Option C, strengthened.**
- Exp 0 stays immutable on its tag.
- Exp 1 lives in its own top-level package with its own lock file and path-filtered CI.
- An import-boundary test forbids `solarbench`.
- A golden test re-derives run #11's primary CI [−13.81%, −4.29%] from a committed copy of the per-day errors.
- A cheap push/PR job keeps Exp 0's 56 tests running, to catch environment rot.
- No data in git; only manifests and hashes.

**New in v2.** Inside the Exp 1 package, the **referee is a separate trust domain behind a declarative API**:
- A spec plus model code goes in; a verdict plus evidence package comes out.
- The researcher side has no read path to vault data, ledger internals or referee code.
- **Exp 2, the second consumer, is the planned trigger for extracting the referee as a shared core.** Extraction comes from Exp 1 code, never from solarbench.

**Consider a separate repository or deployable** for the referee if the customer-run, source-available model (§13) becomes the product shape.

---

## 15. Minimum architecture (Exp 1)

A plain Python package. No SaaS, frontend or authentication service. Estimated 3,500–5,000 lines including tests and the attacker library (INFERENCE).

**Unchanged from v1:**
1. Stage 0 audit scripts and forward recorder.
2. Immutable raw store with hashed manifests.
3. Vintage table with a known_at rule registry.
4. As-of builder: the only path to models.
5. Target builder.
6. Naive rules and L/G adapters that only ever see matrices.

**New for the referee:**

7. **Canonical hypothesis-spec schema and hasher.** It covers every forking-path degree of freedom and detects near-duplicates by forecast and loss correlation.
8. **Sandbox runner.** Model code runs in a network-less subprocess that sees only the as-of snapshot. Scoring happens in a separate process after predictions are written and the model process has exited.
9. **Vault service.**
   - G1 single-use and G2 retire-on-first-PASS vaults.
   - Keys are held by a principal other than the researcher.
   - Constant-time, constant-byte NOT-PASS responses.
10. **Ledger.** Hash-chained and append-only. It tracks α-wealth and bits released, and records who approved every unseal and configuration change.
11. **Verdict engine.** It writes `verdict.json` per claim and `referee_verdict.json` for 1A, and counts every emitted statistic.
12. **World generator and attacker library** for 1A, with planted vulnerabilities.
13. **Dossier and evidence-package generator,** with the "cannot supply" section, configuration hash and prose-number diff test.
14. **Tests:**
    - truncation-equivalence, poisoning and vintage-swap;
    - **transcript invariance** (holdout-swap);
    - mutation, tamper and DST tests;
    - import boundary;
    - golden bootstrap.

**Explicitly not built:** services, feature stores, tracking servers, market plugins, orchestration.

---

## 16. Cost / complexity

All INFERENCE unless marked.

| Item | 1A | 1B |
|---|---|---|
| Data | £0 | £0 (whether the BMRS licence permits commercial use is UNKNOWN) |
| Compute | About 150–600 CPU-hours with cached loss differentials (§8A item 13) | About 70–150 CPU-hours |
| Infrastructure | CI plus one workstation | Recorder VM about £5–20/month |
| Effort | 5–7 engineer-weeks: referee core 3–4; worlds, attackers and campaigns 2–3; dossier 0.5 | +2–4 engineer-weeks on the shared core: ingest, target, GB specifics. Stage 0 as in v1: 5–7 person-days plus a 14-day live capture |
| Calendar | About 2 months after approval | After Stage 0. Earliest STRONG-final is about March–April 2027 (≥90 post-freeze days) |

The commercial track costs your time only: about 20 calls over 3–4 weeks.

**Budget kill for 1A (replaces v1's K-budget, which 1A's estimate would trip automatically).** If 1A exceeds 9 engineer-weeks, or 800 CPU-hours, before the first R4 campaign result, re-scope in this order:
1. drop k = 100;
2. drop learner G from the campaigns;
3. merge attacker types that share a mechanism.

Each step is ledgered. v1's K-budget still applies to 1B.

---

## 17. Pre-registered success and kill criteria

### Tier R: referee validity (1A; primary)

Frozen in the 1A pre-registration before any seed is revealed.

- **Sample sizes** come from an exact-binomial operating-characteristic calculation. The stdlib script `oc_calc.py` in the scratchpad reproduces them. The final numbers are fixed in the pre-registration.
- **"False PASS"** means a confirmatory PASS on a null world, counted **per world**: P(≥1 false PASS in the world).
- All Clopper–Pearson bounds are **one-sided 95%**.

| ID | Property | Procedure and pass condition |
|---|---|---|
| **R1** | Size under honest use | Run separately for each guarantee class offered. The honest scripted analyst submits its pre-declared plan: G1, one batch of 4 hypotheses under Holm α = 0.05; G2, a fixed query sequence under the pre-registered α-spending; G3, one e-process run to the horizon. **Pass:** upper bound ≤ 0.07 over 2,000 null worlds. OC: a referee at exactly 0.05 passes with probability 0.98; one at 0.07 passes with ≤0.05 |
| **R2** | Power and implementation check | An independent reference implementation of the same pre-registered learner and test, written separately from the referee, runs on the same planted worlds: 500 per effect size, at 1/2/3/5/10% pinball skill. "Recovered" means a G1 PASS on the planted hypothesis at its Holm-adjusted level. **Pass:** referee and reference agree on PASS / NOT-PASS in ≥99% of worlds, **and** the 10% effect is recovered in ≥99% of worlds. The full power curve is reported, alongside the analytic noncentral-t prediction (not gating) |
| **R3** | Leak detection | The pre-registration freezes a leak catalogue, giving each class's mechanism and magnitude: known_at shifted one publication earlier; latest-vintage read; Timestamp-tag join; back-dated gap-fill; synthetic publishTime used as known_at; target at t+h in features; transform fitted on the full sample; DST shift; plus every v1 threat row that can be synthesised, listed by ID. **Pass:** ≥100 injected trials per class are 100% flagged INVALID; zero false INVALID on ≥100 clean worlds; every mutant in the pre-registered mutant set fails at least one test. **known_at margin** (a separate label, not INVALID, consistent with §7): planted margin-dependence is flagged MARGIN-SENSITIVE in 100% of ≥100 trials and in ≤5% of clean worlds |
| **R4** | Adaptive-attack resistance | Each cell = (attacker type × k ∈ {10, 30, 100} × guarantee class) against referee v2. G1 cells use only pre-submission attacks. **Pass per cell:** upper bound on P(≥1 false PASS per world) ≤ 0.075 over 2,000 null worlds. All cells must pass for the full scope. This is an intersection–union rule, so no multiplicity correction is needed against false certification: a cell whose true rate is 0.075 passes with ≤0.05. OC: if every one of about 39 cells sits at exactly α = 0.05, all pass with probability ≈0.95. **Positive control:** the naive referee (graded feedback, per-query α) against the combination attacker at k = 30, over 400 worlds, must show a lower bound > 0.15. If the control does not fire, the campaign is VOID, and one ledgered strengthening of the attacker library is allowed. If it is still void, G2 is not certified |
| **R5** | Transcript invariance (G2) | ≥50 pairs of independent synthetic holdouts per attacker script. Every referee response, including errors, is released on a fixed 60-second tick as a fixed-length padded payload. Comparison stops at the first PASS in either member of a pair. **Pass:** 100% of pairs are byte-identical up to that point, and poisoned holdouts (NaN, ±10⁶ extremes, reversed order) change no pre-unseal byte in 100% of ≥50 trials. **Failure removes G2 from scope**; it does not invalidate G1 |
| **R6** | Tamper resistance (known classes) | Planted vulnerabilities: editable test, time-limit config, writable ledger copy, readable target file, stale latest-vintage cache, and a wrong known_at entry (detected by cross-check against the 1A synthetic recorder). ≥20 scripted attempts per vulnerability. **Pass:** 100% are *blocked* (no verdict, ledger entry or vault byte changes) and 100% are logged with the acting identity. This certifies known classes only. Findings from the optional LLM red team are reported, and each becomes a regression test |
| **R7** | Determinism | Two clean builds from the lock file, on the same OS image and CPU architecture, reproduce every verdict, ledger hash and gating statistic **byte-identically**. A cross-architecture rerun is reported but not gating: if a gating statistic differs and lies within 1% (relative) of its decision threshold, the verdict is marked FRAGILE and resolved to the more conservative verdict. A configuration-sensitivity sweep is reported, not gating |

**R8, the 1B data gate** (not a referee-validity criterion):
- Stage 0 k1–k7 (data feasibility), then the real-data point-in-time tests: truncation-equivalence, poisoning, vintage-swap and known_at perturbation.
- If a k-check fails, 1B is **BLOCKED**.
- If a point-in-time test fails on real data *and the referee caught it*, 1B ends **INVALID-DATA**. That means the referee did its job.
- If a leak the referee missed is found later by audit, 1A reopens as **REFEREE-INVALID**.

**1A verdict rules** (exhaustive):
- **Repair.** At most one ledgered repair round in total. Every affected criterion is then rerun on fresh seeds from a new commit-reveal.
- **Certified scope** is the set of (guarantee class × k × attacker set) cells for which R1 and R4 pass, and also R5 for G2. It always reads *"scripted attackers and knowledge-free search only; not certified against an adaptive LLM researcher"* unless the LLM red team ran.
- **REFEREE-VALID:** R2, R3, R6 and R7 pass, and the certified scope covers G1, G2 and G3 at every k.
- **REFEREE-VALID-WITH-SCOPE:** R2, R3, R6 and R7 pass, and the certified scope includes at least the **pre-registered minimum**: G1 against all scripted attackers, plus G2 at k ≥ 30 *or* G3.
- **REFEREE-INVALID:** any other outcome. That covers a failure of R2, R3, R6 or R7 after the repair round, or a certified scope below the minimum. Exp 2 does not start.
- **Mapped to the brief's ladder** (for the *referee* thesis): REFEREE-INVALID = FAIL; VALID-WITH-SCOPE = INTERESTING; REFEREE-VALID = STRONG.

### Tier S: GB science (1B; secondary)

v1 §17 is unchanged. It covers:
- C1/C2 claims;
- the precedence table (INVALID > STRONG > INTERESTING > FAIL-negligible > INCONCLUSIVE > FAIL);
- SESOI 2.0%; Holm α = 0.04;
- STRONG gates (a)–(l), and STRONG-final after ≥90 post-freeze days;
- the mechanism label.

v2 amendments:
- no confirmatory reuse after the single unseal;
- a contamination label on the confirmation window;
- the economic gate on variant B only.

### What counts as Experiment 1 success (exhaustive)

- **SUCCESS:** 1A is VALID or VALID-WITH-SCOPE, **and** 1B ends with any Tier S verdict, or INVALID-DATA caught by the referee. A GB FAIL counts as success.
- **PARTIAL:** 1A is VALID or VALID-WITH-SCOPE, **and** 1B is BLOCKED at Stage 0 or still pending (STRONG-final is not possible before about March–April 2027).
  - Exp 2 may start within 1A's certified scope, on synthetic and forward data.
  - 1B moves to ERCOT or ≥12 months of forward capture, or stops.
- **FAILURE:** 1A is REFEREE-INVALID, or an audit later finds a real-data leak that the referee missed.

### PRODUCT SIGNAL

Moved out of Experiment 1. It is judged by the commercial track (§13; the positive signal needs a budget line and a pilot commitment) and by Exps 2–4 (§18).

---

## 18. Plan and roadmap

### Now (no code until you approve)
1. **1A pre-registration draft:** a document only, on a fresh branch from `main`. It covers:
   - the world generator specification;
   - the attacker library;
   - the feedback designs;
   - R1–R7 procedures, thresholds and operating-characteristic sample sizes;
   - the commit-reveal seed scheme;
   - the dossier outline.

   You review and approve it. Its hash is committed before any seed is revealed. No changes under `solarbench/`, `tests/` or the Exp 0 workflows.
2. **1B Stage 0 (v1 §18):** needs egress to the Elexon and NESO hosts, which must be enabled in the environment settings. Decision gate (v1, unchanged):
   - **k1–k7 pass** → the 1B plan, with Stage 0 numbers substituted, comes back for approval.
   - **k4 fails, D0 is later than 2025-03-01, or no near-real-time price exists** → ERCOT probe, then ≥12 months of forward capture, **or STOP 1B**.
   - **k6 fails** → C1 cannot be tested historically.
   - **k7 fails** → no run.
3. **Commercial track:** the two call scripts (§13), run by you, drafted by me.
4. **Housekeeping:**
   - push the `experiment-0-solar-final` tag (commands given earlier);
   - make `main` the default branch;
   - **save the run #11 artifact before 2026-10-13**.

### After approval: 1A build order
1. Spec schema and ledger.
2. Vault service and sandbox runner.
3. As-of builder and verdict engine (shared with 1B).
4. World generator.
5. Honest-use runs: R1, R2, R3, R7.
6. Attacker library and campaigns: R4, R5, R6.
7. Dossier.

**1B joins after Stage 0 passes.**

### Roadmap (to be specified after 1A; each experiment has one falsifiable question)

**Exp 2 — Autonomous researcher inside the referee.**
- *Question:* can an AI agent, given a data catalogue plus α, compute and data budgets, propose, test and retire hypotheses with zero referee violations, controlled false-claim rates, and more confirmed findings per budget than a human-designed plan and a random-proposal agent?
- *Credit:* only from post-freeze synthetic worlds and live data after its knowledge vintage.
- *Mix:* blind honeypots and impossible tasks.
- *Measurements:* gaming-attempt rate, successful-gaming rate, disclosure rate, near-duplicate clustering, and p-values bunched just under the threshold. Deterministic detectors are primary; capture–recapture estimates undetected gaming.
- *Human gates:* only a human principal unseals vaults or promotes models.

**Exp 3 — Knowledge accumulation.**
- *Question:* does a researcher with a point-in-time knowledge base beat a memory-ablated twin on the same forward stream and budget?
- *Knowledge base contents:* confirmed verdicts, retired negatives and data quirks. Each item carries a known_at and cites ledger IDs.
- *Firewall:* no referee internals and no sealed-window statistics in memory.
- *Measures:* prospective hit rate, calibration and budget efficiency.
- *Transfer:* GB → Belgium or ERCOT.
- *Accumulation:* only by optional continuation of e-values on the same registered claim, never by re-testing released windows.
- *Staleness:* beliefs expire at known market-design change dates.
- *Epochs:* a change of provider model starts a new epoch.

**Exp 4 — Economically grounded incentives.** Compare six arms on the same blinded task mix:
- A0 flat pay;
- A1 per accepted claim (the negative control);
- A2 a linear proper score on post-freeze prospective outcomes;
- A3 cost-netted economic value with deferral and clawback;
- A4 staking from charged α, compute and data budgets, paid on contribution beyond the meta-model;
- A5 A4 plus a bug bounty and a confession channel.

**Pre-register the transmission channel:** prompt, memory, selection by referee score, or fine-tuning/RL. Selection is treated as an optimiser. RL is not run without A5 safeguards.

Measure the gap between the referee proxy and prospective net value as selection pressure grows. Make gaming a negative-expected-value bet: penalty × P(detect) > expected gain, with P(detect) estimated by capture–recapture.

---

## 19. Open questions

1. **1B decisive (unchanged):** IRIS archive coverage; whether the first `DISEBSP` message is near-real-time; whether UploadTime is genuine; the BMRS licence.
2. Can the retire-on-first-PASS vault keep useful power under realistic α-spending when true effects are rare and small? (1A will measure it.)
3. Which bounded loss transform keeps e-process power on spiky imbalance-price losses without changing the economic meaning of the null too much?
4. Does the eventual researcher behave like a worst-case adversary or like a natural analyst, and how many bits does it actually extract? (Exp 2.)
5. How much do frontier LLMs know about 2024–26 GB market events? Are there capable, chronologically consistent models with 2025–26 vintages? (UNKNOWN; reported ChronoGPT vintages end in 2024.)
6. Do stated incentives change a frozen LLM's research behaviour at all without fine-tuning? (No direct evidence found.)
7. Buyer questions:
   - Will front-office buyers accept prospective-only credit and e-value or retire-on-first-PASS verdicts in place of familiar backtest statistics?
   - Will banks' model-risk teams accept vendor-generated evidence?
   - Will firms grant agents autonomy at all?
8. The exact texts of SR 26-2, PRA SS1/23 and its 2026 amendment, and the FCA/ESMA AI positions (all regulator hosts blocked; UNVERIFIED).
9. Would cross-sectional targets, with many near-independent units, make reusable-holdout mechanisms non-vacuous for later products?

---

## Process notes

- **How v1 was produced:** a 27-agent read-only workflow (8 research digests, 4 competing designs, 3 judges, a leakage adversary, a thesis-killer, 2 data verifiers, writers, a critic) plus my spot checks.
- **Research for v2:** 4 read-only agents, on adaptive analysis, AI quant agents and LLM look-ahead, gaming and incentives, and model-risk governance. Their digests are in `referee_research.json` and `referee_research.txt`.
- **Review:** an adversarial reviewer checked v2. Its must-fix items are applied, including:
  - a single recommendation;
  - exact-binomial sizing for R1/R4 (the earlier 400–800-world rule would fail a correct referee most of the time);
  - exhaustive verdict rules;
  - G2's conditions;
  - scoping of magnitudes versus principles.
- **Evidence limits:**
  - The sandbox blocked Elexon, NESO, ENTSO-E, RTE, arXiv, most publishers and every regulator host.
  - Literature and regulatory claims rest on search summaries (UNVERIFIED).
  - The decisive GB facts could not be checked from here.
  - SIM figures were not saved; 1A re-runs them as seeded artefacts.
  - The commercial assessment rests on zero buyer conversations.
- **Agent housekeeping:**
  - v1 agents wrote 13 third-party files into the scratchpad, which I deleted.
  - A v2 agent wrote a 249-byte probe file outside it (`/tmp/claude-0/gh_search_test.html`), which I also deleted.
- **Repository:** untouched at `406c92c`, with a clean working tree.

---

## 20. Final recommendation

**RESEARCH MORE BEFORE CODING.** This is bounded to two gates that need no code, and it is not open-ended research.

1. **Experiment 1A pre-registration (referee validation), primary.**
   - It is the main purpose of Experiment 1 under the product framing, and the prerequisite for Exps 2–4.
   - It depends on no unverified external data, and it can falsify the referee cleanly.
   - **BUILD condition for 1A code:** you approve the pre-registration, and its hash is committed.
2. **Experiment 1B Stage 0 (GB workload), secondary.**
   - The IRIS archive unknowns still decide whether a historical point-in-time test exists.
   - It costs about a week plus a 14-day live check, once egress is enabled.
   - **BUILD condition for 1B code:** k1–k7 pass, and you approve.

Why not BUILD now: no approved plan exists yet, and 1A's pass rules must be fixed before any code or seed exists.

Why not STOP: the referee thesis is testable cheaply and cleanly, and no finding so far contradicts it.

**What is decided:**
- The product thesis is technically credible as a *researcher inside a referee*, within three product-level constraints:
  - fresh data bounds certified throughput (the magnitudes vary by target);
  - LLM researcher credit is prospective-only wherever targets are public history;
  - the referee is a security boundary.
- v1's α-per-reuse rule is withdrawn. Graded verdicts are released only after a vault closes.
- v1's commercial verdicts are re-scoped to the stand-alone tool. The product's commercial case is untested and has its own falsifiable track, with a positive signal that requires money.
- The moat question is open.
- t0 is irrelevant *to Exp 1*.
- Architecture Option C, with the referee behind an API boundary. Extraction is triggered by Exp 2.

*In parallel, on your side:*
- enable egress to the Elexon hosts for 1B Stage 0;
- run the two buyer-call scripts;
- push the tag;
- flip the default branch;
- save the run #11 artifact before 2026-10-13.

**Single next action in Claude Code:** ask Claude Code to **draft the Experiment 1A pre-registration document**. It covers:
- the world generator;
- the attacker library, including the knowledge-free arm;
- the feedback designs;
- R1–R7 procedures and operating-characteristic sample sizes;
- the seed commit-reveal;
- the dossier outline.

It is a document only, with no code, on a fresh branch from `main`. It makes no changes under `solarbench/`, `tests/` or the Exp 0 workflows. It is for your review, and nothing is implemented until you approve it.
