# Experiment 1 decision memo — full technical version

> ## Framing addendum (v2, 2026-09-23): read this first
>
> **The product hypothesis has changed.** It is now a customisable, AI-native **junior quant researcher** hired by a trading organisation. A deterministic point-in-time harness is the **independent referee** it works inside.
> - **Experiment 1 validates the referee.**
> - **Experiments 2–4** test the researcher: autonomy, knowledge accumulation and economically grounded incentives.
>
> The body below is the v1 technical analysis. It stays authoritative for the **GB workload (now Experiment 1B)**, with these amendments. The decision-level text is in the condensed memo v2 (`experiment1_decision_memo.md`). The v1 snapshot is `experiment1_decision_memo_full.v1.md`.
>
> 1. **Structure.** Experiment 1 = **1A** + **1B**.
>    - **1A — referee validation** (synthetic known-answer worlds, planted leaks, adaptive-attack and tamper campaigns, reproducibility). It needs no Elexon access, and it is the primary part.
>    - **1B — the GB workload in this document**, still gated on Stage 0 k1–k7.
>    - A GB FAIL is a valid referee outcome, not an Experiment 1 failure.
>    - Tier-R criteria R1–R7 come first (condensed memo §17), with exact-binomial sample sizes and exhaustive verdict rules. R8 is the 1B data gate. The §17 criteria below become Tier S (science, secondary).
>
>    **PRODUCT SIGNAL (§17.8) moves out of Experiment 1.** It goes to the commercial track and Exps 2–4.
> 2. **Correction: the reuse rule is withdrawn.**
>    - Every "any other reuse spends α = 0.005 / FWER bound 0.05 + 0.005k" statement is struck through in place.
>    - Why: once graded verdicts or an evidence package have been seen, a flat α per reuse does not bound adaptive FWER. In SIM, a researcher ensembling on numeric feedback got false significance at α = 0.005 of 10.5% / 39.6% / 95.5% after 10 / 20 / 50 reuses, against 0.5% on fresh data. Graded ladders leak about a sign bit per query: 0.69–0.98 false PASS at k = 30.
>    - After the single unseal, further tests on the window are **exploratory, ledgered as such, and never confirmatory**.
>    - Only three guarantee classes confirm a claim (condensed memo §10):
>      - **G1** single-use sealed batch (Holm);
>      - **G2** retire-on-first-PASS vault with α-spending and a byte-identical NOT-PASS;
>      - **G3** forward, anytime-valid e-processes on data after registration.
>    - During any adaptive phase the referee releases only PASS / NOT-PASS.
>    - Reusable-holdout, Ladder and differential-privacy mechanisms are close to vacuous at about 37 dependent blocks (INFERENCE).
>    - Online FDR under serial dependence: LOND-dep / LORD-dep / α-spending / e-LOND only. **Not** LORD++ / SAFFRON / ADDIS, which assume independence (FACT: onlineFDR docs).
> 3. **Additional 1B amendments.**
>    - The confirmation window is labelled *"designer contamination not excluded"*, and a recall probe of the designing model is recorded before unsealing.
>    - known_at perturbation reruns at +15 min, +1 h and next publication.
>    - The economic check gates on execution variant B only, with calendar-conditional naive trading controls and MPPM next to the deflated Sharpe ratio.
>    - A mock cold review of the evidence package by someone other than its builder (descriptive only).
> 4. **Scope labels.** Limits in this document are tagged **[v2: Exp 1 scope]** where they hold only for a public-data, stand-alone test:
>    - "beyond public information";
>    - baseline access;
>    - DE-LU / FR STOP (for a *free historical* test);
>    - the "commercial thesis is the weakest link" and "consulting-sized" verdicts in §1, §13 and §20, which assessed a stand-alone forecasting / feed-validation / audit tool, **not** the AI-researcher product.
>
>    These constraints **bind the product** and are now referee design requirements:
>    - realistic effects of 1–3% on daily units make lag and regime claims non-identifiable;
>    - a sealed holdout is consumed by use, so fresh post-freeze data bounds certified throughput;
>    - regimes break every 12–18 months, so "currently leading" needs live decay monitoring;
>    - in-sample explanation is commoditised.
> 5. **New product-level constraints** (condensed memo §1, §3):
>    - **LLM look-ahead.** A researcher's skill can be credited only on data later than max(knowledge vintage, freeze).
>    - **The referee is a security boundary.** It needs a separate trust domain, declarative specs, sandboxed model code and a tamper-evident ledger, because agents game exploitable evaluators (FACT: Palisade, SWE-bench #465, Anthropic Nov 2025).
>    **Magnitudes are per-target.** The principles above bind the product, but the magnitudes in this document (1–3% effects, about 1.4 years per claim near the MDE, about 3 families per market-year, 12–18-month regimes) are **[Exp 1 scope]** estimates for this public GB target.
>
>    **Product-level caveats:**
>    - Baseline access *changes form* in the product: the customer must supply a codified, runnable baseline.
>    - The product's moat is an open question: if the referee is source-available, it is not the moat.
> 6. **Recommendation: RESEARCH MORE BEFORE CODING**, bounded to two gates that need no code:
>    - the 1A pre-registration, which is the primary gate: your approval is the BUILD condition for 1A;
>    - 1B Stage 0 k1–k7, below: passing them, plus your approval, is the BUILD condition for 1B.
>
>    **Single next action:** draft the 1A pre-registration document for your approval. It is a document only, on a fresh branch from `main`, with no code and no changes under `solarbench/`, `tests/` or the Exp 0 workflows.

---

## 1. Executive judgment

**Label key.**
- **FACT**: checked against a primary or authoritative source, either in this pass or in a prior digest marked verified.
- **INFERENCE**: reasoned, not directly sourced.
- **UNKNOWN**: not established.
- **UNVERIFIED (search summary)**: taken from a web-search summary without opening the primary source. It counts as UNKNOWN for decisions.
- **SIMULATION**: from in-session simulations that were never saved; see the note under item 1 below.

**Recommendation: RESEARCH MORE BEFORE CODING.** Stage 0 is bounded at about 1–2 weeks and consists of read-only metadata audits plus buyer calls. It is neither STOP nor BUILD.

**Scope of Stage 0.**
- Stage 0 covers kill checks k1–k7: archive metadata audits, reading licences, and a 14-day live capture with Elexon's stock IRIS client.
- It involves no Experiment 1 code. Registering for IRIS and running the stock client on a VM still need your approval.
- The decision record lists k8 (harness tests on synthetic fixtures) among the Stage 0 kill checks. k8 requires Experiment 1 code, so it is treated here as the **first gate of the approved build**, passed before any real data is modelled.
- Experiment 1 code is written only if k1–k7 pass and you then approve.

**Is the thesis technically credible enough to investigate? The verdict splits four ways.**

1. **The broad thesis is not technically credible as stated.** **[v2: reframed. The product does not rely on autonomous discovery at scale. The statistical limits below bind the product and become referee design requirements (addendum point 4).]** The broad thesis is a system that finds which variables currently lead which market variables, at what lag and in what regime, validates them out of sample, and explains them.
   - **Lag and regime are unlikely to be identifiable at realistic 1–3% effect sizes.**
     - SIMULATION: 33% of true-signal claims named the wrong lag, and a true 2.5% effect was confirmed only 13–14% of the time with 1 year of data.
     - The same point holds without the simulation. Exp 0's pooled-skill CIs were about ±2–5 points on 363 daily units (FACT: run11/pairwise.csv). That is wider than the effects in question. A lag claim needs the *difference* between two small effects, which is noisier still (INFERENCE).
   - **Discovery at scale uses up the holdout.**
     - SIMULATION: a sealed holdout supports about 3 confirmatory families per market-year, and reusing it over 10 rounds raised the family-wise error rate (FWER) from 1% to 19%.
     - The qualitative point is standard: adaptive reuse of a holdout voids its error guarantee (INFERENCE).
   - **"Currently leading" cannot be certified.** Homogeneous regimes last roughly 12–18 months (INFERENCE from these dates):

     | Break | Date | Label |
     |---|---|---|
     | IDA | 2024-06-13 | UNVERIFIED (search summary) |
     | BE MARI | 2024-05-22 | This is also the start of Elia's per-minute prices (FACT: elia-py docstrings). The MARI association is UNVERIFIED |
     | FR 15-min imbalance settlement | 2025-01-01 | UNVERIFIED (search summary) |
     | SDAC 15-min | 2025-10-01 | UNVERIFIED (search summary) |
     | IFS 50r1 | 2026-05-12 | FACT: S3 listings and dynamical.org code |

   - **Public data can only establish "beyond public information"** (INFERENCE). **[v2: Exp 1 scope. A deployed researcher works on the customer's own data.]**
   - **How to read the simulation numbers.** They ran in memory in an earlier research step and were never saved.
     - The only recorded parameters are those quoted: 1 year of daily data, a 2.5% effect, 10 reuse rounds, 100 null runs and 2,000 null candidates.
     - The noise model, dependence structure, lag correlation and candidate count M were not found in any saved file. A grep for "wrong lag" and "FWER" across the scratchpad in this pass returned nothing.
     - They are therefore indicative, not reproducible.
     - Proposed Stage 0 task, with your approval: re-implement them and save the code, seed and data-generating process to the scratchpad.
2. **The narrow core is credible, and testable only in GB, conditional on Stage 0.** The narrow core asks whether one pre-registered, point-in-time-verified public forecast-revision family adds information about one fast-resolving market variable beyond a strong baseline.
   - **Literature prior**, UNVERIFIED (search summaries; no paper opened, publisher hosts blocked):
     - German continuous intraday prices absorb renewable updates within about 1 minute (Kremer, Kiesel & Paraschiv 2021).
     - There is no mean effect beyond the first price-change lag (Hirsch & Ziel 2024).
   - The most probable outcomes are FAIL or INCONCLUSIVE (INFERENCE from these unverified summaries).
   - Plausible effect beyond a strong baseline: 1–3% (INFERENCE).
   - Detectable effect at 80% power: about 1.2–3.2% skill over 37 fourteen-day batches (INFERENCE, computed from Exp 0 dispersion ratios of 0.10–0.22).
3. **The commercial thesis is the weakest link.** **[v2: Exp 1 scope. This was assessed for a stand-alone forecasting / feed-validation tool, not for the AI-researcher product. See the v2 addendum, point 4.]**
   - These pieces are already commoditised (FACT: PyPI wheels and client source):
     - vintage queries (Energy Quantified instances, Volue INSTANCE curves);
     - point-in-time backtesting (OpenSTEF 4.4.3 VersionedTimeSeriesDataset);
     - in-sample lead-lag "explanations" (nixtla 0.9.0 `explain()`, released 2026-09-21).
   - The only plausible whitespace is an independent, pre-registered, vintage-correct audit of incremental information against the buyer's own baseline. That is likely consulting-sized (INFERENCE). **[v2: Exp 1 scope; not a verdict on the product.]**
4. **t0 is not relevant.** **[v2: to Exp 1.]**
   - It lost to smoothed baselines in Exp 0: −9.0% [−13.8, −4.3] against blend_50 (FACT: run11/pairwise.csv row 1).
   - t0-alpha clamps quantiles to 0.1–0.9 (FACT: t0 paper).
   - There is no intraday or imbalance evidence for it.
   - The right instrument is a classical nested linear quantile model.

**What Experiment 1 would and would not establish, on the five-level ladder.**

| Level | Claim type | Status in Experiment 1 |
|---|---|---|
| 1. Correlation | X and Y co-move | Not tested. Never reported as evidence |
| 2. Lead/lag association | X at t−k associates with Y at t | Descriptive only: the reference-vintage profile, plus an in-sample Granger/transfer-entropy screen run as a *competitor arm* |
| 3. Incremental predictive information | Information about X known at t improves the forecast distribution of Y at t+h beyond B, out of sample | **The only claim tested.** Nested L(B) vs L(B+F1) on a sealed, single-use confirmation window |
| 4. Plausible mechanism | A physical or economic channel | Supported only by pre-registered mediation (B+W*, a wind-outturn target) and directional checks. The result is labelled "market channel" or "physical / forecast-combination channel" |
| 5. Causal effect | Intervening on X changes Y | Never claimed |

**Why not BUILD.** GB is the only market examined where the test can be point-in-time from free data (INFERENCE, §6.6). The chosen design rests on three facts that cannot be verified from this environment. archive.data.elexon.co.uk, data.elexon.co.uk and api.neso.energy all returned CONNECT 403 when re-probed on 2026-09-23 (FACT).

1. **When the IRIS archive starts and how complete each dataset is.** UNKNOWN. Elexon's docs show only example blobs dated 2023-06-18 and 2023-11-14 (FACT: https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/iris_archive.md).
2. **Whether the first DISEBSP message per settlement period (SP) is a near-real-time indicative price.** UNKNOWN. The evidence points both ways:
   - *Toward the risk.* The system-price REST endpoints describe prices "generated by the SAA … relating to the data for a settlement run" and return "only messages generated for the latest settlement run" (FACT: elexonpy 1.0.16 `indicative_imbalance_settlement_api.py:1566, :1665`). The response model has no run-type field (FACT: elexon-bmrs 0.3.0 `generated_models.py:593`, SystemPriceResponse). Interim Information (II) run data for B1610 is "published five days after the end of the operational period" (FACT: elexon-bmrs 0.3.0 `generated_client.py:7726`). That a DISEBSP II message would have the same timing is INFERENCE.
   - *Against the risk (weak).* In the IRIS archive, DISEBSP shares the `createdDateTime` Timestamp group with DISPTAV ("Indicative Volumes") and EBOCF ("Indicative Cashflows") (FACT: insights-docs `dataset_and_timestamp_reference.md:14-18`). That hints at a near-real-time indicative calculation (weak INFERENCE). A search summary says about 15 min after the SP (UNVERIFIED).
   - *Stakes.* If the first message is a run days later, the baseline's lagged-price features never existed in real time and the design collapses.
3. **Whether UploadTime tags are genuine first-availability times.**
   - Elexon defines UploadTime as "The time when the blob was uploaded to IRIS" (FACT: iris_archive.md:40). It describes the archive as "a carbon copy of every JSON message sent to IRIS users … updated in near-real-time" (FACT: insights_data_platform.md:87).
   - Whether this holds for historical blobs is UNKNOWN. The tag-query examples are dated 2025-04-14.
   - An "IRIS Release August 2025" forced re-registration before 2 October 2025, with a new tenant ID and Service Bus namespace, and old queues deleted after that date (FACT: https://raw.githubusercontent.com/elexon-data/iris-clients/main/README.md lines 1–11). Whether the archive's uploader also changed, i.e. a "re-platform", is INFERENCE. This falls inside the confirmation window.

**Verifiers contradicted four data claims made by candidate designs.** All four are corrected in the spec:
- NDF/TSDF were said to update every 30 minutes. The docs also say "received daily".
- 100 m wind and SSRD do not exist in ECMWF open data before 2024-03-06 (FACT: S3 `.index` files).
- The ECMWF 0.25° grid starts on 2024-02-01.
- The 06/18z stream name changes from `scda` to `oper` from 2026-05-12.

**IGCPU history carries a synthetic publishTime.** Migrated IGCPU history was "assigned a default publishTime of 2023-01-01 00:00 during the migration" (FACT: elexon-bmrs 0.3.0 `generated_client.py:7896-7897`).

Building on unverified timing semantics would repeat Exp 0's silent assumptions: zero publication delay, a definitive-only vintage, and a single fetched_at.

**Why not STOP.**
- The narrow core is credible and costs £0 in data.
- FAIL or FAIL-BY-POWER would end this narrow GB public-data version of the revision hypothesis.
- INCONCLUSIVE has material probability, because the MDE of about 1.2–3.2% is close to the plausible 1–3% effect (INFERENCE).
- No outcome transfers to other markets, to paid DE-LU data, or to richer professional information sets (INFERENCE).
- Stage 0 costs about 1 week.

**DE-LU (your first hypothesis): STOP for that version.** **[v2: Exp 1 scope. STOP for a *free historical* test only; a customer with licensed vintages is a different case.]**
- **TSO revision vintages cannot be reconstructed.**
  - ENTSO-E serves the latest version only (INFERENCE, strongly supported by maintainers and by parser design).
  - The netztransparenz `prognose` series ended 2022-12-15 (FACT: client code).
  - One unchecked escape hatch remains. The SMARD `table_data` response carries `meta_data.version`/`created` and a per-timestamp `versions` array (FACT: SMARD OpenAPI, https://raw.githubusercontent.com/bundesAPI/smard-api/main/openapi.yaml lines 52 and 80, re-read upstream after the workflow, TimeSeries2 schema). Their semantics are UNKNOWN. About a 1-hour check is warranted before DE-LU is closed.
- **The target and baseline are paid EPEX data for internal use only.** The academic licence is €480/yr and non-transferable (FACT: pucandrzej/csvr_scenario_generation README). The commercial price is UNKNOWN.
- **The only historical X is open NWP, and its timestamps are conservative.**
  - The only historically timestamped copy, the AWS mirror, shows S3 LastModified 6.45–8.57 h after init (FACT: 280-run sample).
  - ECMWF's own open-data release time is UNKNOWN.
  - So a null result could reflect conservative timestamping as much as absence of information (INFERENCE).

**Condition for BUILD.**
1. Stage 0 passes k1–k7.
2. You approve.
3. k8 passes on synthetic fixtures before any real data is modelled.

**Process disclosure.**

- **Files written during this phase and still present.** This phase's rule was read-only. Thirteen files were written to the scratchpad after the brief was saved (`exp1_brief.md` mtime 2026-09-23 09:00:32 UTC). They existed when this memo was written (FACT: `find -newer exp1_brief.md`) and have since been deleted (see below):

  | Time (UTC) | Files |
  |---|---|
  | 09:06 | `_entsoe_py.txt` |
  | 09:11 | `_smard_openapi.yaml`, `_smard_README.md`, `_jao_readme.md`, `_jao_jao.py`, `_jao_publicationtool.py`, `_jao___init__.py` |
  | 09:14 | `_obsyd_README.md`, `_obsyd_data-sources.md`, `_obsyd_DATA_SOURCES.md`, `_obsyd_LICENSES.md`, `_obsyd_NOTICE.md` |
  | 09:17 | `_entsoe_parsers.txt` |

  - Five of them are 14 bytes, probably error bodies (INFERENCE).
  - **Update after the workflow:** the main session deleted all thirteen, since they were scratch copies of public third-party docs and code. The one claim that cited a local copy (SMARD `versions`/`created` fields) was re-checked against the upstream file and now cites it.
- **Files created and deleted in the same session.**
  - A third-party client file (gridstatus `ercot_api.py`).
  - `_prior_dump.txt`, `_ukspf_readme.md` and `_uwf_view.txt`, each disclosed in its digest.
- **Files from earlier research phases**, written before this brief was saved:
  - 06:00–06:54 UTC: `om_opendata_readme.md`, `ec_openapi.yml`, `batinkesc_readme_{main,master}.md`, `rd_*.md` (4 files), `fev_readme.md`, `dyn_ens.ipynb`, `dyn_tc.py`, `_baak.md`, `_rte.md`, `fev_task.py`, `fev_metrics.py`, `fevb_tasks.yaml`, `fevb_README.md`.
  - 07:38–08:49 UTC: `t0_050/`, `weights_out.txt`, `run12_log.txt`, `experiment-0-tag-message.txt`.
  - Whether those phases allowed scratchpad writes is not recorded in anything I can read (UNKNOWN).
- **This revision pass wrote nothing.** The Python wheels were read in memory only.
- **The repository is untouched.** HEAD 406c92c is the tag `experiment-0-solar-final`, with a clean working tree (FACT: `git status`, this pass).

## 2. Lessons from Experiment 0

**Evidence base.**
- The repository at 406c92c (tag `experiment-0-solar-final`), plus the canonical run #11 outputs in `scratchpad/run11/`.
- File:line references were checked in an earlier pass. Row k was re-checked against `run11/run_meta.json` in this pass.
- Numbers come from the run11 CSV/JSON files unless stated otherwise.

### 2.1 Carry forward (established by evidence)

| # | Lesson Exp 0 actually established | Evidence (label, source) | What it becomes in Experiment 1 |
|---|---|---|---|
| 1 | **The baseline's strength decides the verdict, not the model.** | t0 was +5.8% [+1.2, +10.3] against prev_day, but −9.0% [−13.8, −4.3] against an unoptimised 50/50 blend (sign test p = 0.0011; 150 wins, 213 losses). Its rank fell from 1 of 3 to 7 of 9. EWMA was best at 640.8 MW vs t0's 703.8 (FACT: run11/pairwise.csv rows 1–4, run11/metrics.csv; README.md:314-324). | Six naive rules N1–N6, including EWMA (N4) and the NESO-incumbent rule (N6). K-competence: L(B) must beat the best N by ≥5% in discovery. STRONG gate (j): the best B+X model must beat N1–N6, L(B) and G(B). |
| 2 | **Apparent skill was mostly a difference in information age.** | Where the target was within 24 h of the origin, t0 was 15.6% worse than prev_day (447.7 vs 387.4 MW). Where the gate forced prev_day onto a 48-h-old copy, t0 was 13.7% better (982.3 vs 1,138.7). blend_50 got 79% of its improvement over prev_day in that 48-h band (FACT: run11/by_band.csv; README.md:131-165). | Skill by information age (t − known_at) is a mandatory diagnostic for both B and X sources. B holds the latest level of every revised forecast. This, not the margin, is F1's protection: F1/F2 derive from WINDFOR, which is in B, so they share margin_B = 2 min. The asymmetric margin (margin_X = 10 min) protects only X-only sources: REMIT, NESO and ECMWF. |
| 3 | **Sophistication added a failure mode that no naive method had.** | t0 forecasts a night floor: mean night forecast 117.5 MW against actuals of about 0. Night-zeroing removes 6.9% [6.0, 7.7] of t0's error and only brings it to a tie with blend_50: −1.5% [−6.2, +2.9] (FACT: run11/night_zero_audit.csv, pairwise.csv). "98.9% of the deficit is at night" appears only in README.md:371-374 and was computed outside the pipeline (FACT: absent from run11/*.csv). | t0 is excluded. Chronos-2 answers only the "does sophistication help?" question. The instrument of record is a linear quantile model (L), corroborated by LightGBM (G). |
| 4 | **Gains were concentrated in a few days.** | For t0 vs prev_day, the top 10 days carry 77.4% of the net gain. Skill is +1.4% without them and −1.7% without the top 20. The sign test (192 vs 171, p = 0.29) disagrees with the pooled CI (FACT: run11/concentration.csv, pairwise.csv). | STRONG gate (e): skill ≥1.0% after dropping the 5 best days, and the top 10 days must carry <50% of the gain. A sign flip when the top 10 are dropped caps the verdict at INTERESTING. |
| 5 | **Power is day-limited.** | With 363 daily units, CI width tracks how correlated the compared errors are. ewma vs blend_50 spans 4.35 points (daily MAE correlation 0.953); t0 vs blend_50 spans 9.5 points (0.751) (FACT: recomputed from run11/per_day_errors_wide.csv). | Nested ablation with the same learner, so compared errors are highly correlated. The day stays the inference unit. The MDE rule is applied before unsealing. |
| 6 | **Leakage was enforced by assertion plus poisoning tests over a registry shared by CLI and tests.** | `_check_contract` raises on any source time after the origin (FACT: backtest.py:150-167). Poisoning rewrites post-origin data affinely and to NaN (FACT: tests/test_benchmark.py:474-535). The CLI method list equals the registry (FACT: forecasters.py:348-354; tests/test_benchmark.py:464-471). | Keep the pattern, but re-key it to per-row, per-source known_at. Add vintage-swap, label-poisoning and truncation-equivalence tests (§7). |
| 7 | **Pinning gives reproducibility within a tolerance, not bitwise.** | Model revision 9b02c5f4 was pinned and resolved via HfApi. `constraints-ci.txt` pins 12 packages. t0 reproduces to ≤0.003 MW per point across runs #9–#11, and to about 0.03 MW between runs #5 and #6 (FACT: README.md:52-59; run11/run_meta.json). | Pin the lock file, set LightGBM `deterministic=true`, and declare numeric tolerances in advance (Chronos-2: 1e-3 £ per quantile). |
| 8 | **Pre-registering a primary comparison works when it is a code constant.** | PRIMARY and PRIMARY_REFERENCE are recorded in run_meta (FACT: run_benchmark.py:56-62). | The pre-registration YAML is hashed and committed. The loader refuses confirmation data without that hash. |
| 9 | **The bootstrap code reproduces exactly.** | Recomputing t0 vs blend_50 in memory gives [−13.81%, −4.29%], matching the run output (FACT: metrics.py:104-160; run11/per_day_errors_wide.csv). | Golden test: Exp 1's copied bootstrap must re-derive this CI from a committed copy of the CSV. |
| 10 | **Never interpolate, never silently shorten an aggregate, and attribute drops per method.** | Gaps stay NaN. Aggregates with too few legal sources return NaN. A balanced drop rule applies (FACT: data.py:212-245; backtest.py:205-215). | Keep no-interpolation and explicit NaN. Change the drop rule: units are dropped only when the *target* is missing, never because X is missing (§7 row 22). |

### 2.2 Do not generalise (Exp 0 patterns that would break Experiment 1)

| # | Exp 0 pattern | Evidence | Why it fails for Experiment 1 | Replacement |
|---|---|---|---|---|
| a | Every model receives the full series and is trusted to censor itself. | `predict(series, windows)` (FACT: forecasters.py:74). For t0, `source_latest` equals the origin by construction (FACT: forecasters.py:426-436, digest). | With vintaged covariates, self-censoring cannot be audited. | The harness builds the as-of snapshot. Models receive only that snapshot. |
| b | Zero publication lag: "origin slot inclusive". | Context must end exactly at the origin (FACT: forecasters.py:405-406). source_audit shows a minimum availability lag of 0.0 h (FACT: run11/source_audit.csv; README.md:875-879). | GB prices arrive after the SP ends. Porting this would leak the last 1–2 SPs. | known_at comes from measured UploadTime plus a margin. Staleness is a feature. |
| c | Definitive-only data, with one fetched_at for the whole file. | 52,606 definitive and 2 consolidated rows. fetched_at 2026-09-12T07:57:14Z (FACT: run11/run_meta.json). | The defence that "inputs are identical for every method" fails for covariate ablations, because a revised covariate helps only the arm that uses it. | First-published target. Per-row known_at. A vintage table. |
| d | One origin per day at 12:00 D-1; nothing fitted. | FACT: backtest.py:83-147; README.md:476-486. | It gives no control over label availability at refit, fitted transforms, purged CV or hyperparameter leakage. | Weekly refits on a fixed 182-day window, label-known_at gating and a transform-invariance test. |
| e | STEP = 30 min and 48 slots/day as constants; same-slot lags in UTC. | FACT: data.py:35-37; forecasters.py:48-56. | Price seasonality follows civil time. GB settlement days have 46, 48 or 50 SPs. | Key on the payload's UTC startTime. "Same SP D-1" means local clock time, which is 23 or 25 h back on clock-change days. |
| f | Every forecast clipped at zero. | `np.clip(pred.values, 0.0, None)` (FACT: backtest.py:234). | Negative GB prices and NIV are legitimate. | No clipping. Fix quantile crossing by sorting. |
| g | The fingerprint conflates NaN with −1. | `series.fillna(-1.0)` before hashing (FACT: data.py:192). | Price and NIV can legitimately take the value −1. | Hash (value, isnull). |
| h | The cache key omits code identity. | FACT: run_benchmark.py:187-203. | A leaky as-of definition would survive its own fix. | The cache key covers the raw-snapshot manifest, as-of definition, pre-registration hash, model spec, git SHA and lock hash. Reproduction runs never read the cache. |
| i | Multiplicity handled in prose. | Holm and Bonferroni exist only in README.md:429-442. About 44 CI-bearing comparisons were emitted against a stated family of 19–20. The 2024 test year was reused across Phase 1 and Phase 2 (FACT: grep of *.py; run11/ranking.csv; README.md:202-212). | Forking paths go unaccounted. | Code-level Holm, BH and batch-means tests. Every emitted statistic is counted. Hash-chained ledger. |
| j | A reporting mask built from test-period actuals. | FACT: metrics.py:33-65. | Harmless there, but a precedent for outcome-defined subsets. | Regimes are defined only from information known at t, with thresholds from discovery. |
| k | DST handled by silent resolve and dedup; the cause of drops is not logged. | `tz_localize(..., ambiguous=False)` (FACT: data.py:186). Duplicates dropped with `keep='first'` (FACT: data.py:231-241). The manifest counts *and itemises* the gaps: rows 52,602 vs 52,608 raw; `missing_steps` = 6; `missing_ranges` = 00:00 and 00:30 UTC on 2022-10-30, 2023-10-29 and 2024-10-27, all autumn clock-change days. 2024-10-27 was then skipped as `skipped_incomplete_target` (FACT: run11/run_meta.json, this pass). The reason is not logged. The pattern matches `ambiguous=False` plus `keep='first'` collapsing the repeated local hour (INFERENCE). | A timezone convention cost a test day and showed up only as a gap. In GB, 46- and 50-SP days are routine. | Every dropped row is logged with a reason code. Invariants on SP counts per day. |
| l | Controls that check nothing. | Vacuous asserts at tests/test_benchmark.py:866 and :1031 (FACT: AST check, digest). | They give false assurance. | Mutation tests: each control must fail when its bug is planted. |
| m | Hand-carried prose numbers. | "92" persisted from 3c4abb9 until 294d66a, although run #11 reports 90 (FACT: git history; run_meta `context_gap_windows` = 90). | Documentation drift. | A test diffs every memo number against run outputs. |
| n | Undersized inference. | A 7-day moving-block bootstrap with B = 2000 leaves about 2.6 draws per Bonferroni tail (FACT: arithmetic on README.md:429-442). SIMULATION: it ran at 7–10% size for a nominal 5%. | Probably anti-conservative. | 14-day batch means with t(nb−1) critical values. SIMULATION: 5.3–6.5% size. A size check with saved code is part of the proposed simulation-persistence task. |
| o | CI runs only on manual dispatch. | FACT: .github/workflows/benchmark.yml:7-15. | Leakage tests do not run on every push. | CI on push for Exp 1 only, path-filtered. |
| p | tfc-t0 pinned below 0.4. | FACT: requirements.txt:9. 0.5.0 renames the quantile argument (FACT per prior digest, not re-verified in this pass). | It blocks t0-beta and would break the adapter. | Not needed: t0 is excluded. |

**Net lessons.**
- Exp 0's verdict turned on the strength of the baseline and on information age, not on the model.
- The component Exp 1 most needs has no counterpart in Exp 0: a known_at as-of store with vintages and label-availability gating.
- Only about 90 lines of Exp 0 are free of domain assumptions (FACT: AST line counts, digest).
- **Housekeeping deadline:** the run #11 artifact `results-full-11`, which includes the forecasts parquet, expires on 2026-10-13 (FACT: tag message).

## 3. What I am probably wrong about

### 3.1 The strongest weak assumptions in the brief

| # | Assumption | Why it is weak | Evidence (label) | Consequence |
|---|---|---|---|---|
| 1 | DE-LU is the right first market. | Feasibility is decided by whether vintages are available, not by how rich the market is. | ENTSO-E serves the latest version only (INFERENCE, strongly supported). netztransparenz `prognose` ended 2022-12-15 (FACT: client code). Free recorders are recent: baakflo archive files start 2026-08-16 (FACT). The Energy-Data-Science/entsoe-realtime-data collector, apparently KU Leuven, keeps 14 days on GitHub. Its earliest example path is 2026-05-20, and its older files go to a university store of unknown public status (INFERENCE that it starts in 2026). Continuous intraday is paid EPEX data, internal use only (FACT). | "TSO wind revisions move DE intraday prices" cannot be tested honestly on free data, subject to the SMARD check in row 2. |
| 2 | Historical TSO forecast vintages exist in the obvious public sources. | None of these three offers a vintage request parameter or a documented issue time. | SMARD: no vintage parameter, but `table_data` responses carry `meta_data.version`/`created` and a per-timestamp `versions` array, with UNKNOWN semantics, not investigated (FACT: https://raw.githubusercontent.com/bundesAPI/smard-api/main/openapi.yaml lines 52 and 80). Energy-Charts: the OpenAPI `public_power_forecast` has no issue-time field (FACT). ENTSO-E: latest only (INFERENCE). | Treating today's download as history is leakage. GB (IRIS UploadTime, publishTime) and possibly ERCOT (postDatetime, depth UNKNOWN) come closest. A 1-hour look at SMARD `versions` is owed before DE-LU is closed. |
| 3 | Forecast revisions are unpriced, market-moving information. | In continuous markets, updates are reportedly priced within about a minute. Algebraically, B+revision ≡ B+older vintage, so a gain can come purely from forecast combination. | Kremer et al. 2021; Hirsch & Ziel 2024 (UNVERIFIED, search summaries only). B contains the latest level and F1 = latest − ref (FACT: spec algebra). | Only a mediation control can separate the market channel from forecast combination. A STRONG F1 alone is at most level 3, not level 4. |
| 4 | A system can determine at what lag and in what regime a variable leads. | Lag and regime are probably not identifiable at 1–3% effect sizes. | SIMULATION: 33% wrong-lag rate; a true 2.5% effect is confirmed 13–14% of the time with 1 year of data. Supporting: Exp 0 CIs of ±2–5 points on 363 days (FACT). | Claims are made per family only. Lag and regime profiles are descriptive. |
| 5 | Mining many covariates yields discoveries at scale. | A holdout supports only a few confirmatory families. | SIMULATION: 2,000 null candidates gave 84 naive hits and 0 after BH, BY, Bonferroni or max-t; holdout reuse over 10 rounds gave FWER 19%; about 3 families per market-year. | The credible artefact is a harness for testing hypotheses, not a discovery engine. |
| 6 | High-frequency outcomes accumulate evidence quickly. | The effective independent unit is the day, not the half-hour. | Exp 0: ±2–5 points on 363 days (FACT). SIMULATION: half-hourly losses treated as independent gave a 75% false-positive rate at nominal 5%. | INCONCLUSIVE is the most likely non-FAIL outcome (INFERENCE). |
| 7 | A public-data result says something about value to professionals. | Professionals see richer and possibly earlier data. | The only historically timestamped copy of ECMWF open data, the AWS mirror, shows LastModified 6.45–8.57 h after init (FACT: 280-run sample). ECMWF's own release time is UNKNOWN. EQ and Volue sell issue-stamped vintages (FACT: client source). | Every verdict reads "beyond public information". **[v2: Exp 1 scope.]** |
| 8 | Weather archives are historical forecasts. | Several are reconstructions, not the forecasts issued at the time. | Open-Meteo Historical Forecast is stitched from runs. The 2024 ECMWF Single Runs are 49R1 hindcasts (FACT: open-meteo-website docs source). There is no 100 m wind or SSRD before 2024-03-06 (FACT: S3 `.index`). | These sources are denylisted. F6 is evaluable only from 2024-09-04. |
| 9 | t0 or any TSFM is relevant. | t0 lost to trivial baselines. Its "−51% on DE prices" result compares t0 with vs without covariates, on 20 windows of epftoolbox-era data. | FACT: run11/pairwise.csv; t0_paper.txt:878-887; fevb_tasks.yaml (horizon 24, num_windows 20). | A classical nested quantile model is the instrument. |
| 10 | Explanation is the differentiator. | In-sample "explanations" are a free SDK call. | nixtla 0.9.0 `explain()` states that its weights "do not establish that changing a feature will cause the target to change" (FACT: nixtla-0.9.0 wheel, nixtla_client.py:1530-1566). | Only a vintage-correct, pre-registered test report is defensible. |
| 11 | Professional teams would pay for this research tooling. | The tooling is commoditised, and the buyers with the most money build in-house. | FACT: OpenSTEF 4.4.3, EQ and Volue clients. UNVERIFIED (search summaries): enspired and Entrix build in-house. | Likely consulting-sized at most (INFERENCE). **[v2: Exp 1 scope; stand-alone tool only.]** |
| 12 | "Currently leading" can be certified. | Regime breaks come every 12–18 months. | §1 dates: IFS 50r1 is FACT; the market dates are UNVERIFIED. | Only rolling decay monitoring can say what holds now. |
| 13 | Exp 0's controls carry over. | They were keyed on event time, assumed zero lag and definitive data, trusted self-censoring, fitted nothing, and applied Holm only in prose. | §2.2 rows a–p (FACT: file:line). | The point-in-time layer must be written fresh from the threat model in §7. |
| 14 | Option C (build Exp 1 as a separate package) is low-risk by default. | Its real failure mode is copying solarbench and extending it. | INFERENCE. | The Exp 1 point-in-time layer is written from scratch. Only the listed helpers are copied, each with a provenance comment. |
| 15 | API publishTime values are genuine historical availability times. | Not always. | IGCPU: "The database was populated from a data dump lacking publishTime values, all entries were assigned a default publishTime of 2023-01-01 00:00 during the migration" (FACT: elexon-bmrs 0.3.0 `generated_client.py:7896-7897`). | Nothing before D0 is used. IGCA and IGCPU are banned for normalisation. |

### 3.2 Where this memo is itself most likely wrong

- **GB may fail Stage 0 outright** (UNKNOWN). The first DISEBSP message could be a later run, the archive could start late, or UploadTime could have been backfilled. If so, choosing the domain on rigour will have cost a week and bought only a clean negative on feasibility. ERCOT is the fallback: its postDatetime archive exists (FACT: gridstatus `ercot_api.py:435-443`), but its depth is UNKNOWN.
- **k3 could falsely kill GB.** Suppose the archive storage was copied or migrated, for example during the August 2025 release. Then every older blob's `x-ms-creation-time` equals the copy date, and k3's first test fails for all historical months even if the UploadTime tags are genuine. A fallback is pre-declared in §6.5 (INFERENCE).
- **Two kill criteria were not mechanical as written.** k1's "expected messages" and k5's "median lag" were undefined for datasets whose cadence is unknown. §6.5 proposes operational definitions that must be frozen before any count is computed. They are my proposal, not part of the decision record.
- **The minimum detectable effect is extrapolated from solar.** The 1.2–3.2% figure scales Exp 0 dispersion ratios of 0.10–0.22 (INFERENCE). Daily loss differentials for imbalance prices are spikier and may be more persistent. The true MDE could exceed 3%, triggering the MDE rule and deferral.
- **The simulation numbers are not reproducible.** The broad-thesis verdict cites them. They are supported qualitatively by Exp 0's CI widths and standard holdout-reuse theory, but the specific percentages could move materially under a different data-generating process.
- **The literature prior rests on search summaries.** None of Kremer et al., Hirsch & Ziel, Narajewski & Ziel or Marcjasz et al. was read in full, because publisher hosts were blocked. The 1–3% effect-size prior is INFERENCE.
- **I overruled economic relevance in favour of rigour.** The internal economic-relevance judge preferred DE-ID1 (7/10). The GB cash-out price is administered, not traded, and GB results do not transfer to coupled EU markets.
- **"ENTSO-E serves latest only" is inference, not fact.** No ENTSO-E document was read. If the 2025 platform keeps versions, or SMARD's `versions` array holds true vintages, DE-LU moves up the ranking.
- **The mediation arm may not separate the channels cleanly.** If W* (an all-vintage wind prediction) is poorly specified, the "market channel" label could be over- or under-assigned (INFERENCE).
- **The confirmation window is not clean of the designer.** This design was written by a model whose training cutoff (June 2026, FACT: session model information) overlaps most of the confirmation window (2025-03-22 to 2026-08-31). Choices may have been shaped, even unconsciously, by knowledge of GB market events in 2025–26 (INFERENCE). Only data after the pre-registration freeze is clean.
- **The prospective window starts before the freeze.**
  - Capture runs from 2026-10-01.
  - Stage 0 (1–2 weeks after approval), a build of 4–6 engineer-weeks and Stage 1 (about 1 week) put the pre-registration freeze no earlier than mid-November 2026, plausibly December (INFERENCE).
  - The early prospective days will exist before the design is frozen. §7 row 34 proposes counting only post-freeze days. That would move the earliest STRONG-final from about January 2027 to about March 2027 (INFERENCE).
  - This is a recommended amendment, not yet in the decision record.
- **The BMU→fuel mapping for wind-only PN has no verified vintaged source** (§6.1). A poorly mapped B item weakens B and could inflate F1 skill (INFERENCE).
- **The commercial verdict rests on zero buyer conversations.** It could be too pessimistic.
- **Chronos-2's weight licence and pretraining cut-off are unverified**, because Hugging Face was blocked. It was released 2025-10-20 (FACT: repo README), so overlap with 2023–26 GB data cannot be excluded.
- **All compute, transfer and labour figures are INFERENCE.**

## 4. Market landscape

### 4.1 What the literature establishes, by level on the ladder

| Study | Finding | Ladder level | Status |
|---|---|---|---|
| Kiesel & Paraschiv 2017, Energy Econ. 64 | German 15-min intraday prices respond asymmetrically to wind and PV forecast errors | 1–2 with a level-4 story (explanatory, contemporaneous) | UNVERIFIED (search summary) |
| Kremer, Kiesel & Paraschiv 2021, Phil. Trans. A 379 | Renewable forecast updates are priced within about one trading minute | 2; negative for level 3 at the minutes scale | UNVERIFIED (search summary) |
| Hirsch & Ziel 2024, Energy J. 45(3) | No fundamental explains the expected intraday return beyond the first price-change lag; fundamentals drive volatility and tails | 3 (negative for the mean; positive for scale) | UNVERIFIED (search summary) |
| Narajewski & Ziel 2020, J. Commodity Mkts | German ID3 prices are weak-form efficient; the last price is the benchmark to beat | 3 (negative) | UNVERIFIED (search summary) |
| Marcjasz, Uniejewski & Weron 2020, Energies 13 | Gains are about 2–4% over the naive once the naive is itself a regressor | 3 | UNVERIFIED (search summary) |
| arXiv 2509.04452 (DE, 2024–25) | Order-book features raise directional accuracy from 51.73% to 58.22%; fundamentals add little | 3 | UNVERIFIED (search summary; arxiv.org blocked, not opened) |
| Narajewski 2022, Energies 15 | German imbalance prices forecast 30 min ahead do not substantially beat the intraday index | 3 (negative) | UNVERIFIED (search summary) |
| Browell & Gilbert 2022, Energies 15 | Imbalance price forecasting is under-studied; GB examples show skill before DA and before ID gate closure | 3 (positive, GB) | UNVERIFIED (search summary) |
| epftoolbox / NBEATSx repo (Nord Pool, 2-yr test) | MAE: LEAR 1.74 vs AR 2.26 (−23%); DNN 1.68 (−3% vs LEAR); NBEATSx 1.58 (−9% vs LEAR) | Engineered information vs sophistication | FACT: https://raw.githubusercontent.com/cchallu/nbeatsx/main/README.md |
| fev-bench EPF (5 tasks, 20 daily windows each) | TSFMs within 4% of each other (geometric-mean scaled QL 0.452–0.469). Generic AutoML LightGBM 0.825, worse than seasonal naive on PJM | Strawman comparators | FACT: computed from github.com/autogluon/fev results CSVs |
| Belgian TSFM study, arXiv 2605.17045 | Chronos-2 is about 10% worse in MAE on BE imbalance prices | 3 (TSFM negative) | UNVERIFIED (search summary; not opened) |

**Reading.**
- Most of the revision literature, as summarised, is explanatory. It works at levels 1–2 with a level-4 narrative: a revision *explains* a contemporaneous price difference (INFERENCE).
- One question was not found answered in any source read: whether a public forecast revision known 2 h ahead adds point-in-time information to the *distribution* of the GB imbalance price beyond a strong baseline (level 3). This is INFERENCE; the search was limited and relied on summaries.

### 4.2 Already commoditised

| Workflow layer | Existing offer | Evidence (label, source) |
|---|---|---|
| Point-in-time forecast vintages | Energy Quantified *instances* with issued, created and modified timestamps; relative, rolling and absolute queries; free users see only the last 30 days | FACT: https://raw.githubusercontent.com/energyquantified/eq-python-client/master/docs/userguide/instances.rst |
| | Volue Insight INSTANCE curves: `issue_date`, `get_relative`, `get_absolute`, `modified_since` | FACT: volue-insight-timeseries 2.3.1 wheel, `curves.py` |
| | Commodity weather APIs sold "as issued" to "trade forecast surprises" and "momentum" (Prescient / World Climate Service) | UNVERIFIED (search summary) |
| Vintage-aware backtesting | OpenSTEF 4.4.3 `VersionedTimeSeriesDataset` (`filter_by_available_before`, `select_version`), MPL-2.0 | FACT: openstef_core-4.4.3 wheel |
| Forecasts of the target itself | Volue IntraDay Price Predict; Dexter imbalance-price forecasts; Meteologica; Enfor PriceFor; Kpler (ex-COR-e); S&P Global–Enertel (Mar 2026) | UNVERIFIED (search summaries) |
| In-sample lead-lag "explanations" and sample paths | nixtla 0.9.0 `explain()` (Granger / transfer entropy), `feature_contributions`, `simulate()`. First appeared in 0.9.0.dev2 on 2026-09-17; released 2026-09-21 | FACT: nixtla-0.9.0 wheel |
| | tsfresh FRESH (univariate tests plus BY FDR); Tigramite PCMCI (GPL-3.0; assumes causal stationarity) | FACT: tsfresh docs; tigramite README |
| Incremental-contribution scoring | Numerai MMC/BMC (covariance after neutralising to the meta-model or benchmark; scored live) | FACT: numerai/docs `meta-model-contribution-mmc.md` |
| | Exabel `known_time` bitemporal reads, point-in-time backtests, revision tracking | FACT: exabel-9.1.0 wheel, `time_series_api.py:109-139` |
| Dataset scouting | Neudata, Eagle Alpha, BattleFin | UNVERIFIED (search summaries) |
| Execution | PowerBot client 2.35.3 (2026-09-16); Volue Algo Trader (>70 companies) | FACT (PyPI) / UNVERIFIED (search summary) |

### 4.3 Where genuine whitespace might remain (all INFERENCE, all thin)

1. **An independent, pre-registered, vintage-correct audit of incremental information.** It would test whether feed or vendor X adds point-in-time information to the forecast distribution of a power target *beyond the buyer's own baseline*. It needs placebos, a multiple-testing ledger and £-scale scoring. This combination was not found as a product. The search was limited, and vendors may already do it internally.
2. **Live monitoring of incremental skill and signal decay**, in the spirit of Numerai's live MMC, applied to power features.
3. **Independence.** The vendors best placed to do this (EQ, Volue, Dexter, Meteologica) sell the forecasts that would be graded.

**None of these has an infrastructure moat.** **[v2: Exp 1 scope for public-data feeds. The product's moat is an open question, which binds the product: a source-available referee is not a moat by itself (condensed memo v2 §13).]**
- For GB, a self-recorded archive of public vintages is *not* a moat. The IRIS archive is itself public, anonymous and "a carbon copy of every JSON message" (FACT: insights_data_platform.md:87; iris_archive.md). Our own capture adds only an audit of UploadTime.
- In GB the defensible asset reduces to **an audited live track record plus the method** (INFERENCE).
- In markets without a public vintage archive (DE-LU, FR), a self-recorded archive could be an asset, but it only accumulates from the day recording starts.

### 4.4 Value propositions and buyers

| Rank | Value proposition | Assessment |
|---|---|---|
| 1 | Feed / alternative-data validation | The most concrete wedge. Budgets exist in equities: about $2.8bn in 2025 (UNVERIFIED, search summary of Neudata). Power has no marketplace equivalent (INFERENCE). |
| 2 | Monitoring of incremental skill and decay | Not found as a power product (INFERENCE). |
| 3 | Research productivity | A real need, but largely covered by free tools (FACT: OpenSTEF, nixtla, EQ/Volue queries). |
| 4 | Alpha | Highest willingness to pay, lowest credibility for an entrant. On ERCOT a 38% MAE cut bought about 6% more profit (FACT: t0_paper.txt:1516-1554). |
| 5 (tied) | Signal discovery; explainable market intelligence | Discovery is where false discoveries come from. Narrative intelligence is crowded: Montel, LSEG, Kpler, Aurora, Modo, Dexter (UNVERIFIED, search summaries). |

**Most credible first buyer and workflow (INFERENCE; no demand evidence yet).**
- Buyer: the quant or fundamentals lead at a mid-size European trading house, a GB battery optimiser or a GB balancing responsible party (BRP).
- Workflow: they must decide whether a data feed or vendor forecast adds point-in-time information to their own imbalance or intraday forecasts, priced against the cost of that feed.

**Blocking problems (INFERENCE):**
- **Baseline access.** "Incremental" only means something against the buyer's own forecasts, which they are unlikely to share. **[v2: Exp 1 scope in this form; in the product it becomes an integration requirement: the customer supplies a codified baseline.]**
- **Build, not buy.** The buyers with the most money build in-house. **[v2: binds the product too; tested in the buyer calls.]**
- **Wrong budget pool.** The large alternative-data budgets are equity-centric and low-frequency.
- **Skill is not money.** Forecast skill need not convert into profit.

**Is European power too crowded, or technically unsuitable?**
- *Forecasting the prices themselves:* crowded and commoditised (INFERENCE).
- *A historical point-in-time revision test on free data:* technically unsuitable in DE-LU and FR (§6.6). Feasible only in GB, and there only conditionally.

## 5. Market / target / horizon decision

### 5.1 Recommended Experiment 1 (conditional on Stage 0)

**GB-IMB-2H-H (hardened GB-IMB-2H).** The question is whether point-in-time NESO wind-forecast revisions add information about the first-published GB imbalance price 2 hours ahead. The bar is to add information beyond four things: current forecast levels, the live notified position, NESO's indicated imbalance, and recent first-published prices.

| Element | Choice |
|---|---|
| Market | GB balancing and settlement under the BSC. Single imbalance price SSP = SBP (P305, from 2015-11-05; UNVERIFIED search summary). 30-min SPs; 46, 48 or 50 per settlement day. |
| Primary target | First-published SSP_s (£/MWh), taken from the minimum-UploadTime DISEBSP message in the IRIS archive. known_at = UploadTime + 2 min. An SP whose first message arrives more than 60 min after SP end is excluded for every arm. |
| Secondary endpoint (Holm) | First-published NIV_s (signed MWh) from the same message. |
| Horizon | h = 2 h. The target SP starts exactly 120 min after the origin. BM gate closure is s − 60 min (FACT: https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/mil_mel_resolution.md). h = 1 h and h = 4 h are descriptive only. |
| Origins | Every UTC half-hour, 48 per UTC day. Inference unit: the daily mean loss per target settlement date. Weekly refits, Monday 00:00 UTC. Chronos-2 runs only at 00/06/12/18 UTC. |
| Windows (base case, D0 = 2023-06-01) | Warm-up 2023-06-01 to 2023-11-30. Tuning 2023-12-01 to 2024-02-29. Discovery 2024-03-01 to 2025-02-28 (26 batches). Embargo 2025-03-01 to 2025-03-21. Sealed confirmation 2025-03-22 to 2026-08-31 (528 days, 25,342 SPs, 37 batches). Prospective 2026-10-01 to 2027-03-31. Only prospective days after the tagged pre-registration freeze are post-freeze (§7 row 34; recommended amendment). |
| Baseline B | Calendar; first-published DISEBSP history; MID; the latest WINDFOR, NDF, TSDF, INDGEN, INDDEM, IMBALNGC, MELNGC and LOLP/DRM for s; FUELINST, INDO, ITSDO; the live aggregate Physical Notification (PN) for s; FREQ; information age. B+ adds BOALF. B+W* adds W*_s, an L-model median prediction of wind outturn for s fitted on all WINDFOR vintages known at t. |
| Primary covariate F1 | WINDFOR revision for s: W_latest(t)[s] − W_ref[s], with ref ∈ {09:00 Europe/London D-1; previous publish; vintage ≥ 6 h old} × {MW; normalised}. F2–F8 are screened. |
| Instrument | L: L1-penalised linear quantile regression on z = asinh(Y/c), 19 levels. G: LightGBM, which must agree in sign. |
| Primary metric, SESOI | Mean pinball loss over τ = 0.05…0.95 on z. SESOI = 2.0%. |
| Confirmatory test | One-sided, 37 fourteen-day batch means, t(36). Holm at α = 0.04 over ≤4 hypotheses. One pooled extension at α = 0.01. |

### 5.2 Why this design

It had the highest aggregate score, 7.5 (informativeness 8, point-in-time feasibility 8, economic relevance 6.5). These scores come from an **internal LLM judge panel** in this session. They are not external evidence.

- **Auditable timestamps, pending k3/k4.** It is the only candidate where both the target and the revision covariates carry machine-readable availability times from a free source, with a second timestamp that can be audited.
  - The IRIS archive is anonymous. It is described as "a carbon copy of every JSON message sent to IRIS users … updated in near-real-time". Its blobs carry an UploadTime tag, "the time when the blob was uploaded to IRIS" (FACT: insights_data_platform.md:87; iris_archive.md:40).
  - Whether those tags are genuine for historical blobs is UNKNOWN until k3 and k4 pass.
- **Intraday vintages.** WINDFOR publishes up to 8 times a day. INDDEM, MELNGC and LOLPDRM are half-hourly (FACT: elexonpy 1.0.16, `generation_forecast_api.py` and `datasets_api.py` docstrings).
- **One settlement regime throughout.** 30-min SPs, with no change of settlement period length (INFERENCE).
- **A concrete mechanism**, as a level-4 hypothesis, not a claim. BRPs position on earlier forecasts, later revisions become NIV, and NIV sets the cash-out price.
- **Sample.** The windows span about 1,000 daily units in total (decision record). Confirmatory inference, however, rests on **37 confirmation batches (518 days)**, plus ≥90 prospective days (6 full 14-day batches; 13 batches for the full 182-day window).

### 5.3 Overrules

- **DE-ID1 is rejected, although the internal economic-relevance judge preferred it (7/10).**
  - Its target and baseline are paid, non-transferable EPEX data.
  - Its revision covariate (TSO A40/A18) cannot be reconstructed.
  - Its only historical X is open NWP, and its only timestamped copy shows a lag of 6.45–8.57 h. So a null cannot be interpreted.
- **GB-NIV-REV-90 is not primary.**
  - NIV is a system quantity, not the market variable.
  - Its baseline left outturns and BOALF out of the STRONG gate.
  - Its F6 was infeasible before 2024-03-06.
  - It is grafted in as the Holm secondary endpoint.
- **ES-IDA1 is rejected.**
  - A PASS is mostly built in: fresh X is compared against a baseline deliberately frozen at 11:30.
  - Its dose-response check is confounded with season, DST and the 2025-10-01 break.
  - IDA-era OMIE files are unverified.
  - IDA1 − DA cannot be monetised.

### 5.4 Verifier corrections and grafts already folded into the spec

**Corrections from verifiers:**
- D0 moved to 2023-06-01, with a mechanical rule for moving it again.
- F6 restricted to ifs/0p25 100u/100v from 2024-03-06.
- The 0.25° grid starts 2024-02-01. The 06/18z stream changes from `scda` to `oper` on 2026-05-12.
- NDF/TSDF cadence treated as unknown, with a collapse rule.
- IGCA/IGCPU banned for normalisation.
- First-DISEBSP timing and UploadTime genuineness added to Stage 0.

**Grafts from the judges and red team:**
1. Live aggregate PN in B.
2. FREQ in B.
3. First-published NIV as a Holm secondary.
4. F1 alone decides the revision thesis. F7 success is labelled "information, not revisions".
5. Mediation: B+W* plus a wind-outturn target.
6. Gates on £-scale skill and on same-sign skill against the latest-run price.
7. Corrected placebos: +1 cycle is a positive control, and a block shuffle replaces random signs.
8. Oracle-leak and planted-signal controls.
9. Asymmetric known_at margins that work against X. **Scope:** this applies to X-only sources (REMIT, NESO, ECMWF; margin_X = 10 min). F1 and F2 derive from WINDFOR, which is also in B, so they use margin_B = 2 min. Their protection is that B holds the same latest WINDFOR level.
10. An α split of 0.04 / 0.01.
11. At least 90 prospective days for STRONG-final.
12. An in-sample Granger / transfer-entropy competitor arm.
13. A confirmation-window metadata parser that never materialises value fields.

### 5.5 Candidates against the brief's §7 criteria

Judge scores are from the internal judge panel, not external evidence. The aggregate is their mean, computed in this pass.

| Design | Econ. relevance | Point-in-time integrity | Data availability and cost | Obs. (confirmation) | Mechanism | Baseline strength | Feedback | X testability | Judges I / PIT / Econ → mean |
|---|---|---|---|---|---|---|---|---|---|
| **GB-IMB-2H(-H)** | Cash-out price every GB BRP and battery faces; administered, not traded | Target and revisions stamped with publishTime + UploadTime (FACT that the tags exist; genuineness UNKNOWN) | £0; hinges on the IRIS archive (UNKNOWN) | 528 days, 37 batches | BRP positioning → NIV → price (hypothesis) | Strong public: latest levels, NESO incumbent, PN, FREQ, B+ | Target resolves about t+2h45 (UNVERIFIED) | Nested; F1 at intraday cadence | 8 / 8 / 6.5 → **7.5** |
| GB-NIV-REV-90 | System quantity, one step from money | Same basis; F6 infeasible before 2024-03-06 | £0; same dependence on IRIS | 365 days, 26 batches | Most direct | Weaker (no outturns, no BOALF in STRONG) | About 2.5 h | Nested | 7 / 7.5 / 5.5 → 6.7 |
| ES-IDA1 news test | Cannot be monetised; Iberian IDA1 liquidity UNKNOWN | Cleanest target (single-shot auction); X is NWP only | €0; IDA-era OMIE files UNVERIFIED | 341 days, 24 batches | Clean gate-to-gate | Deliberately frozen at 11:30, so a PASS is largely built in | One origin per day | NWP news only; no TSO revisions | 5 / 7 / 3.5 → 5.2 |
| DE-ID1-REV | Highest: Europe's most liquid continuous market | Trades time-stamped; TSO revisions cannot be reconstructed | Paid EPEX; €480/yr academic, non-transferable; 2026 files UNKNOWN | 335 days, 23 batches | Strong prior of efficiency (UNVERIFIED literature) | Strongest (live traded price) | 90 min | Only open NWP historically (6.45–8.57 h LastModified lag) | 4 / 3 / 7 → 4.7 |

### 5.6 Rejected alternatives

| Alternative | Reason for rejection (substance of the decision record, plus additions marked †) |
|---|---|
| EXP1-DE-ID1-REV | The target and baseline are paid, non-transferable EPEX data: academic €480/yr, internal use only (FACT). The commercial price is quote-only. 2026 files may not be sold, which would cut confirmation to 92 days. TSO A40/A18 history cannot be reconstructed: ENTSO-E serves latest only (INFERENCE), and the KU Leuven and baakflo archives start in 2026. The only historical X is open NWP, whose only timestamped copy shows 6.45–8.57 h LastModified lag (ECMWF release time UNKNOWN), so a null cannot be interpreted. The literature prior is weak-form efficiency, about 1 minute (UNVERIFIED). Third parties cannot audit results. Kept only as a forward-recorded Phase 2, and only if GB reaches STRONG. |
| GB-NIV-REV-90 as primary | NIV is a system quantity, not the market variable. The baseline omitted outturns and BOALF from STRONG. F6 was infeasible before 2024-03-06 (FACT). Grafted in as the Holm secondary. |
| ES-IDA1 news test | A PASS is mostly built in (fresh X vs a baseline frozen at 11:30). The dose-response check is confounded with season, DST and the 2025-10-01 break. IDA-era OMIE files are unverified (G1), as is the absence of continuous trading before IDA1 (G2). IDA1 − DA cannot be monetised. The Iberian buyer pool is small. A cheap continental replication candidate once G1 and G2 are verified. |
| FR imbalance price (PRE) or any French target | PRE is revisable from M+1 to M+12, with no archive of first-published values. RTE vintage depth and overwrite behaviour are UNKNOWN. Intraday data is paid. Breaks (UNVERIFIED search summaries): 15-min settlement 2025-01, PICASSO 2025-04, MARI 2026-01, and a disputed start of marginal pricing. Forward recording only. |
| BE Elia quarter-hour imbalance price | Per-minute prices have been published as-is, never validated, since 2024-05-22 (FACT; elia-py docstrings). But forecasts come only as fixed vintages, and "mostrecentforecast" is overwritten, so there is no intraday revision history. About 28 months since MARI. Designated as the continental replication market. |
| NL TenneT | 12-s balance delta published about 2 min later, but no forecast-vintage covariates. Licence and depth UNKNOWN. It would test nowcasting, not revisions. |
| DE-LU / FR day-ahead price with revisions | One origin per day. Commoditised (LEAR/DNN rMAE about 0.38–0.40). TSO day-ahead renewable forecasts are due by 18:00 D-1, after the 12:00 gate, which is a look-ahead trap. |
| **† Cross-market spreads** (e.g. DE-FR +1 h, as named in the brief; GB–continent) | *DA spreads* have one origin per day and are commoditised. Their covariates come from ENTSO-E, which serves the latest version with no issue time (INFERENCE). *Continental ID spreads* need paid EPEX continuous data for both legs. *GB–continent spreads* need paid GB DA or intraday prices (INFERENCE: Obsyd README says "GB has no day-ahead auction feed at all"). None allows a free, point-in-time revision test (INFERENCE). |
| German reBAP / NRV-Saldo | The quality-assured value arrives by the 20th working day of M+1. Whether operational values are kept as first published is UNKNOWN. Licence unclear. reBAP is mechanically ID-AEP ± a mark-up. |
| ERCOT RT price with hourly-posted TSO vintages | A genuine point-in-time mechanism: the public API archive filters by postDatetime (FACT: gridstatus `ercot_api.py:435-443`). Archive depth UNKNOWN. RTC+B break with data from 2025-12-06 (FACT: same file:1044-1048). Outside the European hypothesis. Fallback domain: a one-day probe if GB fails Stage 0. |
| Realised volatility or traded-volume targets | They need paid tick or trade data in every market checked. |
| Automated lag/covariate mining over thousands of candidates | SIMULATION: 33% wrong-lag rate and about 3 confirmatory families per holdout. Commoditised in-sample screens already exist. Included instead as a competitor arm to be beaten. |
| t0 or any TSFM as the instrument of record | t0 lost in Exp 0. t0-alpha quantiles are clamped to 0.1–0.9. There is no imbalance or intraday evidence. A TSFM ablation confounds information content with covariate handling. Chronos-2 is kept only for the sophistication question. |

**† Why continental day-ahead prices are not in B.**
- SDAC results are free, but their known_at could come only from a nominal auction schedule. PIT rule 2 bans nominal schedules.
- Their ENTSO-E copies carry no issue time (INFERENCE).
- Their exclusion makes B weaker, which biases toward X. It is recorded as a scope limit, not a protection (INFERENCE).

### 5.7 What this choice gives up (stated explicitly)

- Point-in-time reconstruction in DE-LU and FR on free data.
- A continuously traded target: the GB price is administered from BM actions.
- The live GB intraday price and GB day-ahead auction prices, which are paid or not free (INFERENCE: Obsyd README).
- Continental DA prices as baseline items (no audited known_at).
- Transferability to coupled EU markets.
- Any professional-edge claim: every result is "beyond public information". **[v2: Exp 1 scope.]**

## 6. Data reality

**Scope.** This section covers GB-IMB-2H-H only. "Checked" means read in this pass or in a prior digest marked verified.

**Elexon primary sources used:**
- insights-docs: `iris_archive.md`, `insights_data_platform.md`, `dataset_and_timestamp_reference.md` and `mil_mel_resolution.md`, all at `https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/`;
- the iris-clients README;
- the elexonpy 1.0.16 wheel (PyPI, 2025-01-26) and the elexon-bmrs 0.3.0 wheel (PyPI, 2025-10-16). Both are generated from the Insights OpenAPI spec and were re-read in memory in this pass.

**ECMWF source:** anonymous S3 listings and `.index` files on `https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com`.

### 6.1 Inventory, part A: source, coverage and access

| Variable (role) | Exact source / provider | Historical coverage | Frequency | Geography | Publication mechanism | API / download | Cost | Licence |
|---|---|---|---|---|---|---|---|---|
| **Y: first-published SSP_s; NIV_s** (primary target; Holm secondary; lagged features in B) | Elexon IRIS Data Archive, container `iris-archive`, folder `data/DISEBSP/`. IRIS Timestamp tag = createdDateTime (FACT: dataset_and_timestamp_reference.md:14-16) | **UNKNOWN.** Doc examples dated 2023-06-18 and 2023-11-14 (FACT). D0 base case 2023-06-01 is an assumption | Per SP; possibly several messages per SP across settlement runs (INFERENCE) | GB | IRIS push (AMQP) plus archive blob. **Timing of the first message UNKNOWN.** REST describes the prices as SAA output "relating to the data for a settlement run" (FACT: elexonpy `indicative_imbalance_settlement_api.py:1566`). DISEBSP shares its Timestamp group with "Indicative Volumes" and "Indicative Cashflows" (FACT; weak INFERENCE toward near-real-time). About 15 min after the SP per a search summary (UNVERIFIED) | Anonymous Azure Blob API, find-blobs-by-tags query on Dataset/Timestamp/UploadTime (FACT) | Free | BMRS data licence UNKNOWN (summaries conflict: commercial with attribution vs non-commercial) |
| Latest-run SSP/NIV (sensitivity and economic check only; **banned from features**) | Insights REST `/balancing/settlement/system-prices` | "Full access to historic data" claimed, depth not stated (FACT) | Per SP | GB | Returns "only messages generated for the latest settlement run" (FACT: elexonpy `indicative_imbalance_settlement_api.py:1665`). The response model has no run-type field (FACT: elexon-bmrs `generated_models.py:593`) | REST, no auth (FACT). Snapshot on a fixed date on or after 2026-10-15 | Free | BMRS licence UNKNOWN |
| MID: APXMIDP price and volume; N2EXMIDP volume (B; economic check) | IRIS archive `data/MID/` | UNKNOWN | Per SP | GB | Received from MID providers. **No publishTime field** (FACT: elexonpy MID model). IRIS Timestamp = startTime (FACT: dataset_and_timestamp_reference.md) | Blob tags | Free | BMRS licence UNKNOWN |
| WINDFOR (latest level in B; **F1**, F2) | IRIS `data/WINDFOR/`; REST `/forecast/generation/wind/{history,evolution,earliest,latest}` | Archive UNKNOWN. REST superseded-vintage depth UNKNOWN | Up to 8 publishes a day: 03:30, 05:30, 08:30, 10:30, 12:30, 16:30, 19:30, 23:30. **Timezone unstated** (FACT) | GB, metered wind visible to the ESO only (FACT) | Carries publishTime (FACT) | Blob tags; REST cross-check only | Free | BMRS licence UNKNOWN |
| NDF, TSDF (B; F3) | IRIS `data/NDF/`, `data/TSDF/`; REST `/forecast/demand/day-ahead/history` | UNKNOWN | **Contradictory:** NDF "available daily"; TSDF "received daily" vs "updated every 30 minutes" (FACT; the 30-min sentence is boilerplate repeated on INDO/MEL/MIL) | GB, national (TSDF also zonal) | publishTime (FACT) | Blob tags | Free | BMRS licence UNKNOWN |
| INDGEN, INDDEM, IMBALNGC (B; F4) | IRIS `data/INDGEN/`, `data/INDDEM/`, `data/IMBALNGC/` | UNKNOWN | IMBALNGC and INDGEN "received daily by midday"; INDDEM "updated every half hour" (FACT) | GB | publishTime. IMBALNGC = generation PNs − TSDF; the stream variant says National Demand (FACT: the docs are inconsistent) | Blob tags | Free | BMRS licence UNKNOWN |
| MELNGC, LOLP/DRM (B; F5) | IRIS `data/MELNGC/`, `data/LOLPDM/` (API name LOLPDRM) | UNKNOWN | MELNGC "received every half an hour"; LOLPDRM "received half-hourly", horizons 1/2/4/8/12h+ (FACT) | GB | publishTime, publishingPeriodCommencingTime, forecastHorizon (FACT) | Blob tags | Free | BMRS licence UNKNOWN |
| FUELINST; INDO/ITSDO (B outturns) | IRIS `data/FUELINST/`, `data/INDO/`, `data/ITSDO/` | UNKNOWN | FUELINST 5-min; INDO "updated at 15 min intervals" (FACT) | GB; FUELINST excludes embedded generation (FACT per digest) | IRIS Timestamp = publishTime (FACT) | Blob tags | Free | BMRS licence UNKNOWN |
| Aggregate PN for s, total and wind BMUs (B item 6) | IRIS `data/PN/` | UNKNOWN | Per BMU submission | GB | IRIS Timestamp = **timeFrom** (FACT: dataset_and_timestamp_reference.md), never used | Blob tags; the volume could add several million blobs (INFERENCE) | Free | BMRS licence UNKNOWN |
| **BMU → fuel-type mapping** (needed only for the *wind-only* PN in B item 6; total PN needs none) | Insights REST `/reference/bmunits/all`: "a current list of BM units held by Elexon" (FACT: elexonpy 1.0.16 `reference_api.py:38`). Fields: nationalGridBmUnit, elexonBmUnit, eic, fuelType, leadPartyName, bmUnitType, fpnFlag. **No effective-date or publishTime field** (FACT: elexonpy model `insights_api_models_responses_reference_bm_unit_data.py`). Not an IRIS-archive dataset (FACT: absent from dataset_and_timestamp_reference.md). **Candidate vintaged alternative:** UOU2T14D availability rows carry bmUnit, fuelType and publishTime (FACT: elexonpy model `..._availability_by_bm_unit_daily.py`), and UOU2T14D is in the IRIS archive (FACT). Whether it covers every wind BMU is UNKNOWN | REST: current snapshot only. UOU2T14D: archive coverage UNKNOWN | Snapshot (REST); daily publishes (UOU2T14D, INFERENCE) | GB BMUs | REST: latest state only | REST, no auth; archive tags | Free | BMRS licence UNKNOWN |
| FREQ (B) | IRIS `data/FREQ/` | UNKNOWN | "Received every 2 minutes" (FACT); about 720 messages a day (INFERENCE) | GB | measurementTime only (FACT) | Blob tags | Free | BMRS licence UNKNOWN |
| BOALF (B+) | IRIS `data/BOALF/` | UNKNOWN | Per acceptance | GB, per BMU | acceptanceTime (the IRIS Timestamp, FACT); `amendment_flag` (FACT) | Blob tags | Free | BMRS licence UNKNOWN |
| REMIT (F7) | IRIS `data/REMIT/`; REST `/remit`, `/remit/revisions` | UNKNOWN | Event messages | GB | mrid, revisionNumber, publishTime, createdTime (the IRIS Timestamp). The revisions endpoint returns all revisions (FACT) | Blob tags plus REST cross-check | Free | BMRS licence UNKNOWN |
| ECMWF IFS HRES 100u/100v (F6) | `s3://ecmwf-forecasts` (eu-central-1), `ifs/0p25` only | Date folders from 20230118 (1,339 folders to 20260923; a 6-day gap 2023-04-27 to 2023-05-02). **100u/100v/ssrd from 2024-03-06** (FACT; one verifier saw them already in the 2024-03-05 06z scda index; the spec uses 2024-03-06). 0.25° from 2024-02-01, with 0.4° in parallel to 2025-02-25 (FACT) | 4 runs a day; 3-hourly steps (FACT: S3 listings; ecmwf-opendata README:376-381) | Global, cropped to GB boxes | Mirror upload to S3. **The AWS mirror's LastModified is 6.45–8.57 h after init** (FACT: 280-run sample; a second sample reported regime shifts, discrepancy unresolved). ECMWF portal release time UNKNOWN. known_at is conservative by construction | Byte-range reads via `.index`, about 1.3–1.4 MB per field per step (FACT) | Free | CC BY 4.0 plus ECMWF Terms of Use (FACT: ecmwf-opendata README:730-732) |
| NESO embedded solar/wind forecasts (F8, conditional) | NESO Data Portal (CKAN) | 2022 archive seen only in a search summary; other years UNVERIFIED | Hourly issues, 0–14 days (UNVERIFIED) | GB distribution-connected | Issue-time column UNVERIFIED | CKAN API; host blocked here | Free | NESO Open Data Licence v1.0, OGL-based (UNVERIFIED) |
| GB bank holidays (calendar) | Pinned table committed to the repo | n/a | Annual | GB | Deterministic | gov.uk blocked here (FACT: 403) | Free | OGL (INFERENCE) |
| Own forward recorder (k4 check; prospective cross-audit) | Elexon's stock IRIS AMQP client plus REST polls every 15 min, on an always-on VM (needs your approval and IRIS registration) | From capture start | Message-level | GB | Push. 3-day TTL. Client secrets expire after 2 years. "IRIS Release August 2025": re-registration required before 2 October 2025, new tenant ID and Service Bus namespace, old queues deleted after that date (FACT: iris-clients README:1-11; TTL at :141) | Free registration | VM about £5–20/month (INFERENCE) | Same as the data captured |

### 6.2 Inventory, part B: time semantics, vintages, quality, suitability

| Variable | Historical vintages available | event_time | known_at_time (pre-registered rule) | issue_time | Revisions stored? | Likely quality problems | Suitability for Exp 1 |
|---|---|---|---|---|---|---|---|
| **Y: first DISEBSP SSP/NIV** | The archive claims every message (FACT); completeness UNKNOWN. REST: latest run only (FACT) | settlementDate + SP; payload startTime in UTC | **min UploadTime + 2 min.** Assert UploadTime > SP end. Exclude the SP if first UploadTime > SP end + 60 min | createdDateTime (the IRIS Timestamp for DISEBSP, FACT) | In the archive, if complete (UNKNOWN); not via REST | Which run the first message belongs to is UNKNOWN (§1). RSP/VoLL spikes; negative prices; 46/50-SP days; archive gaps; the August 2025 IRIS release. The NIV sign convention matches spec arithmetic (FACT) but needs an empirical check | **Decisive.** Valid only if k1, k2, k3 and k5 pass |
| Latest-run SSP/NIV | No | Same | Snapshot date | createdDateTime | No | Changes with download date | Sensitivity and economic check only |
| MID | Via the archive only | SP startTime | **First UploadTime + 2 min.** Dropped from B before discovery if first UploadTime − SP end > 60 min for >5% of SPs | None (no publishTime) | UNKNOWN whether restated | Thin; N2EX volumes may be sparse (UNKNOWN); a VWAP that may include trades after t (INFERENCE) | Conditional B item; execution reference only for economic variant B |
| WINDFOR | publishTime vintages (FACT); REST /history depth UNKNOWN | Target SP | max(publishTime, UploadTime) + 2 min (margin_B; the same margin as its B level) | publishTime, audited against UploadTime | Yes, if the archive is complete | Visible-farm coverage drifts. Publish timezone resolved from UploadTime. k6 needs ≥2 vintages between reference and t on ≥90% of origins | **Primary covariate.** Feasible if k1 and k6 pass |
| NDF / TSDF | publishTime vintages | Target SP | max(publishTime, UploadTime) + 2 min | publishTime | Yes, if the archive is complete | Cadence unknown. **Collapse rule:** if <2 vintages per target SP on ≥50% of origins, F3 becomes a single daily revision | B level; F3 conditional |
| INDGEN / INDDEM / IMBALNGC | publishTime vintages | Target SP | max(publishTime, UploadTime) + 2 min | publishTime | Yes, if complete | IMBALNGC and INDGEN may be about 24 h stale (the information-age trap); definitions inconsistent | B level; F4 subject to the same collapse rule |
| MELNGC / LOLP / DRM | publishTime vintages | Target SP | max(publishTime, UploadTime) + 2 min. **Only horizons legal at t:** the 1-h LOLP horizon is illegal at a 2-h origin | publishTime | Yes | LoLP near gate closure feeds RSP (INFERENCE), so use it strictly as-of | B level; F5 |
| FUELINST, INDO, ITSDO | Via the archive | 5-min interval / SP | max(publishTime, UploadTime) + 2 min | publishTime | Via the archive. REST without publish filters returns latest (FACT) | FUELINST excludes embedded generation | B outturns |
| Aggregate PN | Via the archive | timeFrom to timeTo | **UploadTime** (+2 min). The PN Timestamp tag (timeFrom) is never used | n/a | Via the archive | Large volume. Wind-only aggregation depends on the BMU mapping (next row) | **Optional** if IMBALNGC, INDGEN and INDDEM refresh at least every 60 min within the 6 h before t on ≥95% of origins; otherwise **mandatory** |
| **BMU → fuel mapping** | REST: **none**, current list only (FACT). UOU2T14D: publishTime-stamped fuelType per BMU (FACT that the fields exist; coverage UNKNOWN) | n/a | REST snapshot: known_at = capture date (2026), so **not point-in-time for history.** UOU2T14D, if used: as-of on max(publishTime, UploadTime) + 2 min | UOU2T14D publishTime | REST no; UOU2T14D via the archive | *Survivorship:* BMUs retired before the snapshot are missing from the current list, so their PNs go unmapped and wind PN is biased low in early months, correlated with fleet growth (INFERENCE). *Look-ahead from new units* is limited, because a unit has PNs only after commissioning (INFERENCE). Fuel reclassification of wind units is probably rare (INFERENCE). A weaker B inflates X skill, so this is not harmless | The decision record's rule "frozen from the earliest available snapshot" is kept. The earliest REST snapshot is capture day, so Stage 0-E checks UOU2T14D as an as-of source. Total PN (no mapping) always stays in B. The unmapped-PN share is reported by month |
| FREQ | Via the archive | measurementTime | UploadTime + 2 min | n/a | n/a | High volume | B: mean and min deviation over [t − 30 min, t − margin] |
| BOALF | Via the archive; amendments exist (FACT) | Acceptance interval | **UploadTime**, never acceptanceTime; first messages only | acceptanceTime | Via the archive | Volume; system vs energy tagging | B+ only (STRONG gate h) |
| REMIT | mrid + revisionNumber (FACT) | Unavailability window | max(publishTime, UploadTime) + **10 min (margin_X)** | createdTime | Yes (/remit/revisions, including withdrawals) | Free-text causes; duplicates and withdrawals | F7, labelled "information, not revisions" |
| ECMWF 100u/100v | Each run immutable, keyed by path | Valid time of s, linearly interpolated from 3-hourly steps | **max S3 LastModified over the files used + 10 min.** Never init_time | Init time (recorded, never used as known_at) | Runs are separate (FACT) | Grid overlap 2024-02-01 to 2025-02-25. `scda`→`oper` rename 2026-05-12. IFS cycle breaks 2024-11-12 and 2026-05-12. No vintaged geographic capacity source (IGCPU has no coordinates, FACT) | F6. Evaluable in discovery only from 2024-09-04 (178 days); low power, cannot be primary |
| NESO embedded forecasts | UNVERIFIED | SP | issue_time + a measured lag bound + 10 min | UNVERIFIED | UNVERIFIED | Column semantics; capacity drift | **Dropped before discovery** unless Stage 0 verifies per-row issue times and complete as-published archives (the drop is ledgered) |
| IGCA / IGCPU | **Synthetic:** migrated IGCPU history was "assigned a default publishTime of 2023-01-01 00:00" (FACT: elexon-bmrs `generated_client.py:7896-7897`) | Effective date | n/a | Fake for migrated rows | n/a | No coordinates (FACT) | **Banned** for normalisation. The normaliser is the trailing 90-day p99 of WINDFOR levels known at t |
| B1610 | Revised across runs | SP | "Published five days after the end of the operational period based on the Interim Information (II) Settlement Run" (FACT: elexon-bmrs `generated_client.py:7726`) | n/a | Latest only (INFERENCE) | Leakage trap | **Banned** |

### 6.3 Disposition of every covariate class in the brief (§5), and sources explicitly not used

| Brief covariate class | Disposition | Reason (label) |
|---|---|---|
| Historical electricity prices | **B:** first-published DISEBSP history; MID | FACT for source semantics (§6.1) |
| Order book / microstructure; live GB intraday price | **Excluded** | EPEX GB continuous is paid. The continuous read-only API was €3,360/month for internal use (UNVERIFIED search summary). This limits every claim to "beyond public information" **[v2: Exp 1 scope]** |
| Traded volume | **B:** MID volume | Thin (INFERENCE) |
| Load; load forecasts; load-forecast revisions | **B:** INDO/ITSDO, latest NDF/TSDF. **F3:** revisions | Cadence contradictory (FACT); collapse rule |
| Wind generation; wind forecasts; wind revisions | **B:** FUELINST wind, latest WINDFOR, wind PN. **F1/F2:** WINDFOR revisions. **F6:** ECMWF 100 m wind revisions | §6.1 |
| Solar generation / forecasts / revisions | **F8** (conditional on NESO embedded-forecast verification) | FUELINST excludes embedded generation (FACT per digest). Most GB solar is embedded (INFERENCE) |
| Temperature / weather forecasts and revisions | **Excluded as a separate family** | No free vintaged GB temperature *forecast* verified. The IRIS dataset TEMP is a daily outturn, "measured at midday … Values are received from 5pm each day" (FACT: elexonpy 1.0.16 `datasets_api.py:14373`). Temperature enters B indirectly through NESO's NDF/TSDF (INFERENCE). ECMWF 2 m temperature is not in the pre-registered family grid, to keep the family count at ≤8 |
| Gas prices (NBP, SAP) | **Excluded** | NBP intraday/day-ahead prices are paid (INFERENCE). Free daily gas indicators would at best be daily and without an audited known_at (UNKNOWN). Gas sets the price *level*, which lagged SSP and MID already carry at a 2-h horizon (INFERENCE) |
| Carbon prices (UKA) | **Excluded** | Paid exchange data (INFERENCE); daily; same level argument |
| Nuclear availability; generation outages | **F7:** REMIT (publishTime, revisionNumber, withdrawals) | FACT (§6.1). UOU2T14D day-level availability is excluded as a family (horizon mismatch, INFERENCE), but it is a candidate as-of source for the BMU mapping |
| Hydro; storage (pumped, batteries) | **Not a separate family.** They enter B through total PN, FUELINST totals and B+ BOALF | Hydro is small in GB (INFERENCE). Batteries act through PN/BOA (INFERENCE) |
| Cross-border physical flows | **B:** FUELINST interconnector totals (outturn) | FACT per spec |
| ATC / NTC | **Excluded** | ENTSO-E copies are latest-version-only, with no issue time (INFERENCE) |
| Neighbouring-market prices | **Excluded** | Continental DA: known_at only from a nominal auction schedule, which PIT rule 2 bans. Continental ID: paid. IRIS SOSO prices (publishTime group, FACT) are excluded as thin and not pre-registered (INFERENCE) |
| Calendar | **B** | Pinned bank-holiday table |

| Source | Reason for non-use |
|---|---|
| EPEX GB continuous intraday; GB day-ahead auction results | Paid or not free (INFERENCE: the Obsyd README says "GB has no day-ahead auction feed at all"). |
| ENTSO-E GB series | Latest version only (INFERENCE). |
| Open-Meteo Historical Forecast; Open-Meteo 49R1 hindcasts; ERA5; WeatherNext2 "historical" | Reconstructions, not forecasts as issued (FACT: open-meteo-website docs source, per digest). |
| AIFS files in the F6 lineage | Model mixing. AIFS uploads earlier than IFS: about 05:13 UTC for 00z (FACT: S3). |
| Vendor NIV and price forecasts; Energy Quantified / Volue archives | Quote-only (price UNKNOWN). The EQ free trial covers the last 30 days only (FACT). Optional prospective professional-baseline arm. |
| REST data before D0, including `/history` vintages | Migrated history can carry a synthetic publishTime (FACT: IGCPU). |
| REST `/reference/bmunits/all` as a historical mapping | Current state only (FACT). Used only as the fallback described in §6.2. |

### 6.4 Costs and licences

- **Data licences: £0.** This is FACT for the access terms that were read: Insights needs no auth, the archive is anonymous, and ECMWF is CC BY 4.0.
  - Whether the **BMRS licence permits commercial use is UNKNOWN.** That blocks only the PRODUCT path (kill criterion K-licence).
  - NESO licence: unread (UNVERIFIED search summary only).
- **Transfer (INFERENCE):** about 0.1–0.2 TB in total.
  - IRIS: about 1.3–2M blobs for the core datasets, roughly 10–50 GB of JSON. PN and BOALF could add several million more blobs.
  - ECMWF: roughly 80–120 GB of transfer, under 2 GB after cropping to GB.
- **Infrastructure (INFERENCE):** recorder VM about £5–20/month; compute about £0–50; 70–150 CPU-hours, no GPU.
- **Labour dominates.** Stage 0 about 1 week; build 4–6 engineer-weeks; about 10 buyer calls of 45 minutes.
- **Hidden prerequisite:** an environment with egress to `archive.data.elexon.co.uk` and `data.elexon.co.uk`. From this sandbox both return CONNECT 403 (FACT, re-probed 2026-09-23).

### 6.5 Vintage limitations that decide feasibility (Stage 0 = k1–k7, metadata only; k8 = first build gate)

**Operational definitions for k1 and k5.** These are *proposed here* (INFERENCE), because the decision record leaves "expected messages" and "median lag" undefined. They must be frozen in the Stage 0 plan before any count is computed. A "message" is one archive blob.

- **k1: expected messages per dataset.**

  | Dataset | Expected count |
  |---|---|
  | DISEBSP | ≥1 per SP (46/48/50 per settlement date) |
  | MID | ≥1 APXMIDP message per SP (INFERENCE that the provider sends one per SP) |
  | WINDFOR | 8 publishes/day as documented; the pass rule is ≥6 on ≥95% of days (decision record) |
  | INDDEM, MELNGC, LOLPDM | 48 per day (46/50 on clock-change days), as documented half-hourly |
  | FUELINST | 288 per day (5-min) |
  | TSDF, IMBALNGC (cadence contradictory) | The median daily count over discovery-era months 2024-03 to 2025-02, fixed once before any other month is counted, plus ≥1 message on every day |

- **k5: median lag per dataset-month.**
  - publishTime datasets: median over messages of (UploadTime − publishTime).
  - DISEBSP: median of (first UploadTime − SP end).
  - MID: median of (first UploadTime − SP end).
  - Pass: |median(month) − median(2025-06)| < 5 min for every dataset.

| Unknown | Why fatal if it goes the wrong way | Stage 0 check (pass threshold) |
|---|---|---|
| IRIS archive start and per-dataset completeness | If D0 falls after 2024-02-11, confirmation cannot be fully historical. If after 2025-03-01, the historical design is dead | **k1:** ≥95% of expected messages (definitions above) in every month from D0 to 2026-08 for DISEBSP, WINDFOR, TSDF, INDDEM, IMBALNGC, MELNGC, LOLPDM, FUELINST and MID. WINDFOR ≥6 publishes on ≥95% of days |
| Timing of the first DISEBSP message | If it is a later settlement run (the II run for B1610 is published five days after the operational period, FACT), then lagged SSP/NIV in B never existed in real time | **k2:** first UploadTime ≤60 min after SP end for ≥95% of SPs in every month used; otherwise D0 moves. The run identity is checked against REST latest-run values on a discovery-window sample only |
| Genuineness of UploadTime | Circular or backfilled tags make the audit meaningless. Batched uploads make features hours stale | **k3:** (i) blob creation time within 10 min of the UploadTime tag for ≥99% of sampled blobs; (ii) UploadTime − publishTime in [−1, 30] min for ≥99% of vintages; (iii) a bulk-upload signature (≥1,000 blobs within 60 s spanning >24 h of publishTimes) in ≤1% of blobs. **Pre-declared fallback for (i)** (INFERENCE, proposed): if `x-ms-creation-time` for all months before some date clusters on one day (≥90% of blobs within ±1 day), treat creation time as uninformative for those months. Rely on (ii), (iii), the stability of the (UploadTime − publishTime) distribution across that date (median shift <5 min), and k4. Label those months "UploadTime genuineness unverifiable" in verdict.json. **k4:** over 14 days of own capture, first-seen − UploadTime ≤5 min for ≥99% of messages |
| Continuity across the August 2025 IRIS release | An artefactual difference between discovery and confirmation | **k5:** 2025-07 to 2025-11 each ≥95% complete (k1 definitions); median-lag shift <5 min vs 2025-06 (definition above) |
| WINDFOR vintage density | F1 is undefined without ≥2 vintages | **k6:** ≥2 distinct vintages between reference and t on ≥90% of origins |
| BMRS licence | Research may be blocked; the product certainly is | **k7** |
| Test harness | Controls must work before real data is touched | **k8, the first gate of the approved build, not Stage 0:** poisoning, truncation, vintage-swap and mutation tests pass on synthetic fixtures. It requires Experiment 1 code, so it cannot run before approval |

### 6.6 Cross-market point-in-time verdict (free data, as of 2026-09-23)

| Market | Verdict | Basis |
|---|---|---|
| **GB** | Conditionally feasible, not yet verified | The archive and publishTime vintages are FACT. The four decisive items are UNKNOWN (§6.5). The historical BMU mapping has no verified vintage |
| BE | Fixed forecast vintages only | Per-minute prices never validated, from 2024-05-22 (FACT). "mostrecentforecast" is overwritten |
| FR | Not feasible | PRE revisable to M+12, with no first-published archive. RTE vintage depth UNKNOWN. Intraday data paid |
| DE-LU | Not feasible historically, pending one check | ENTSO-E latest only (INFERENCE). netztransparenz `prognose` ended 2022-12-15 (FACT). EPEX paid. Free recorders recent. The SMARD `versions`/`created` fields have UNKNOWN semantics (FACT that they exist) |
| NL | Target feasible, no forecast vintages | TenneT API; licence and depth UNKNOWN |
| ES | IDA-era OMIE files unverified | OMIEData still uses the legacy session pattern (FACT) |
| ERCOT (non-EU comparator) | Every hourly posting filterable by postDatetime (FACT); depth UNKNOWN | gridstatus `ercot_api.py:435-443` |
| Weather | ECMWF open data on the AWS mirror from 2023-01-18: 0 missing runs in a 280-run sample, LastModified lag 6.45–8.57 h (FACT). Hub-height wind and SSRD only from 2024-03-06 (FACT). ECMWF portal release time UNKNOWN | S3 |

## 7. Leakage threat model

**Scope.** Threats are mapped to the brief's §9 categories plus threats specific to GB and to this design. "R-n" refers to the numbered point-in-time rules in the spec.

**Severity key:**
- *fatal*: invalidates the historical design;
- *high*: can manufacture or erase the primary effect;
- *medium*: biases secondary results or wastes power.

| # | Threat (§9 category) | How it fools us in GB-IMB-2H-H | Detection | Mitigation (pre-registered) | Severity |
|---|---|---|---|---|---|
| 1 | Target vintage: settlement-run revisions (target leakage) | REST returns the latest run only (FACT). Lagged SSP/NIV built from REST carry corrections made after t. A missing first message silently turns the "first" message into a later run, possibly on stress-correlated days | Stage 0 k2 by month. Fixture: an original message plus a later revised message must give the original value at every origin before the revision's known_at. Lineage audit: no DISEBSP row with known_at > t | Target = min-UploadTime DISEBSP, with the message id stored. An SP is excluded for all arms if first UploadTime > SP end + 60 min; the excluded share is reported by month and \|NIV\| decile. REST price endpoints are on the feature denylist (R3, R8) | high |
| 2 | First DISEBSP is not near-real-time (publication delay, target definition) | If the first message belongs to a later settlement run (the II run for B1610 is published five days after the operational period, FACT: elexon-bmrs `generated_client.py:7726`; the same timing for DISEBSP is INFERENCE), then "last known SSP/NIV" in B never existed in real time and the target means something else. The REST docs describe prices "relating to the data for a settlement run" (FACT: elexonpy `:1566`) | k2: distribution of first UploadTime − SP end, by month. Run identity checked against REST latest-run values on discovery-window samples | D0 moves to the first month that passes. Otherwise the target definition is void | **fatal** |
| 3 | Incorrect timestamps: meaning of the IRIS `Timestamp` tag | The tag means publishTime for forecasts, but startTime for MID, timeFrom for PN, acceptanceTime for BOALF, createdDateTime for DISEBSP and settlementDate for NETBSAD/DISBSAD (FACT: dataset_and_timestamp_reference.md). A generic `Timestamp ≤ t` join admits unpublished MID, BSAD and PN | Per-dataset fixture: a blob with Timestamp ≤ t < UploadTime is excluded at t. Property test: known_at never reads Timestamp or blob-name times | known_at rule table in the hashed YAML. The loader refuses datasets not in the table (R2) | high |
| 4 | UploadTime not genuine (backfill, bulk upload, synthetic tags, storage migration) | If tags were copied from publishTime, the audit is circular and any early publishTime leaks. Batched uploads make features stale. The "IRIS Release August 2025" (re-registration by 2 October 2025, new tenant and namespace, old queues deleted; FACT: iris-clients README:1-11) falls inside confirmation. Whether the archive uploader changed is INFERENCE. A storage copy could also make creation times useless and falsely fail k3 | k3 (creation time vs tag; bulk signature; pre-declared fallback when creation times cluster, §6.5); k4 (own capture vs UploadTime); k5 (changepoint across 2025-07 to 2025-11) | Months that fail are excluded before discovery. Months on the k3 fallback carry the label "UploadTime genuineness unverifiable". If k4 fails, the historical design is killed | **fatal** |
| 5 | Revised forecasts via REST "latest/earliest" views, and dedup | Without publish filters REST returns the latest vintage (FACT: `/datasets/WINDFOR` docstring). The IMBALNGC "level" then equals the final notified position, which is close to realised NIV. Dedup that keeps the last upload back-dates corrections | Truncation equivalence on ≥1,000 stratified origins: deleting rows with known_at > t gives byte-identical features. Fixture: same publishTime, different UploadTime | REST lives in a cross-check module that cannot write features (import-boundary test). The dedup key includes UploadTime (R9) | **fatal** |
| 6 | Migrated history with synthetic publishTime (revised fundamentals) | IGCPU migrated rows carry publishTime 2023-01-01 00:00 (FACT). A capacity normaliser built from it encodes future fleet growth, a time-trend proxy | Stage 0 compares publishTime and UploadTime distributions per dataset per month | Nothing before D0. IGCA/IGCPU banned for normalisation. Normaliser = trailing 90-day p99 of WINDFOR levels known at t | high |
| 7 | Settlement inputs for the same SP (target leakage) | LoLP near gate closure feeds RSP (INFERENCE). NETBSAD/DISBSAD, DISPTAV, EBOCF, ISPSTACK, BOAV and the composite "market depth" / "settlement summary" endpoints contain parts of Y_s (FACT: elexonpy docstrings) | Denylist plus lineage test. A fixture vintage published at s − 1 h must not change a forecast made at t = s − 2 h | Denylist (R8). LOLP/DRM only through as-of joins at horizons legal at t | **fatal** |
| 8 | Revised fundamentals, outturns and reference data | B1610 appears at T+5 days (FACT). REST INDO returns latest data. `/reference/bmunits/all` is "a current list" with no effective dates (FACT: elexonpy `reference_api.py:38`). Using it for history drops retired units and may reclassify units retroactively. This biases wind-only PN, weakens B and can inflate F1 skill (INFERENCE) | Discovery-window comparison of IRIS first messages vs REST latest values. Unmapped-PN share by month | IRIS first messages only. B1610 banned. BMU mapping as-of from UOU2T14D if Stage 0-E verifies it; otherwise frozen earliest snapshot, reported unmapped share, and total PN (no mapping) always in B | medium |
| 9 | Publication delays (the zero-lag convention inherited from Exp 0) | Porting "context must end at the origin" (FACT: forecasters.py:405-406) or a too-short constant lag hands N1, L and Chronos-2 an SP not yet published | min(t − known_at) ≥ margin for every row. Chronos-2 context-end assertion. Fixture with UploadTime = SP end + 20 min | Measured UploadTime, no nominal-lag constants. Staleness is an explicit feature. Sensitivity run with a uniform 5-min margin | high |
| 10 | Exchange data downloaded retrospectively (MID) | MID has no publishTime (FACT). Treating it as known at startTime, or backfilling from REST, uses indices built from trades after t. N5's spread and economic variant A inherit this | Stage 0 distribution of MID UploadTime − SP end. Fixture: startTime ≤ t < UploadTime is excluded | MID known_at = first UploadTime + 2 min. Drop rule (>60 min for >5% of SPs). Variant B executes at MID_ref; variant A is labelled optimistic | high |
| 11 | Incorrect timezones | WINDFOR's schedule has no timezone (FACT). Naive parsing shifts features by 1 h in BST. A reference time taken from the schedule would admit a vintage up to 1 h early | The parser rejects naive datetimes. Assert payload startTime equals the Europe/London mapping of (settlementDate, SP). Assert target start − origin = 120 min on every row | UTC internally. startTime is read, never computed. The F1 reference is resolved per date from UploadTime against 09:00 Europe/London (R10) | high |
| 12 | DST | 46/50-SP days inside the data: 2023-10-29, 2024-03-31, 2024-10-27, 2025-03-30, 2025-10-26, 2026-03-29 (FACT: zoneinfo). Collisions, unexplained drops and 1-h horizon drift. Exp 0 lost 6 UTC steps on fall-back days and skipped the 2024-10-27 test day (FACT: run11/run_meta.json) | Fixture per date. Invariants: 46, 48 or 50 SPs per date; no duplicate UTC startTime; every dropped row carries a reason code | Key on UTC startTime. "Same SP D-1/D-7" in local clock time (23 or 25 h back). No silent dedup | medium |
| 13 | Weather reanalysis or hindcasts masquerading as forecasts; model and stream mixing (F6) | Hindcasts or ERA5 replace issued forecasts. AIFS/IFS or 0p4/0p25 mixing creates fake revisions. Alternating oper and scda (06/18z) runs creates a diurnal proxy. The `scda`→`oper` rename (2026-05-12, FACT) silently drops half the runs | Manifest audit: every F6 value traces to an S3 key, ETag and LastModified. One (model, stream, grid) per declared date range. Unit test: identical runs give zero revision across layout boundaries | ifs/0p25 100u/100v only, from 2024-03-06. Per-date path rules. known_at = max LastModified + 10 min (conservative; the mirror lag is not ECMWF's release time). Missing = NaN plus staleness, never gap-filled. Denylist for reconstructions | medium |
| 14 | Feature normalisation or fitted transforms using future observations | A full-sample c, scalers or thresholds import confirmation-period volatility into the definition of the loss | Transform-invariance test: perturbing all data after refit time T leaves every parameter fitted at T unchanged | c = warm-up MAD, frozen in the YAML. Everything else fitted inside each training window. Regime thresholds from discovery only (R11) | medium |
| 15 | Label availability in training, baselines and conformal pools (target leakage) | A label is known only at about SP end + first-upload lag. Rolling statistics keyed on the target index (EWMA, 28-day medians, residual pools) use prices not yet published | Label poisoning (known_at > refit time) for learners, N1–N6, EWMA and conformal pools. Max label known_at recorded per prediction | A training row is admitted only if its label known_at ≤ refit time. All rolling statistics go through the as-of API | high |
| 16 | Overlapping horizons and dependent units | 48 origins a day share information. SIMULATION: half-hourly iid inference gave a 75% false-positive rate at nominal 5%, and HAC with h−1 lags gave 52% | Politis–White block length on daily differentials. Full-pipeline size on placebos | Daily unit. 37 non-overlapping 14-day batches with t(36); switch to 28-day batches if Politis–White > 14 days. CV purge of 7 days + 2 h + label lag | high |
| 17 | Hyperparameter selection against the test period | Tuning on B+X, or tuning months that drift into discovery, favours X | Hyperparameter code asserts every date < discovery start | LightGBM tuned once on the B-only arm over 2023-12-01 to 2024-02-29, then frozen for every arm. LASSO penalty by purged 28-day blocked CV inside each window | medium |
| 18 | Repeated testing and holdout reuse | Post-unsealing "fixes", or pooling prospective data without a boundary, spend the guarantee. SIMULATION: 10 reuses gave FWER 19% | Hash-chained ledger. Git tag at unsealing. The verdict engine refuses a second confirmation computation without an α spend | Unsealed exactly once. The only extension is one pooled test at α = 0.01. ~~Any other reuse spends 0.005.~~ **[v2: no other confirmatory reuse; later tests are exploratory.]** Code frozen at the unsealing tag | high |
| 19 | Multiple-comparison bias | Exp 0 emitted about 44 interval-bearing comparisons against a family of 19–20 (FACT). INTERESTING has several routes: about 1 − 0.95⁶ ≈ 26% chance of at least one false route if six were independent (INFERENCE, arithmetic) | Code counts every emitted p-value or interval, tagged gating or non-gating | Bonferroni within each family. BH q = 0.10 over F2–F8. Holm α = 0.04 over ≤4 hypotheses. INTERESTING routes Holm-corrected or labelled exploratory | high |
| 20 | Data snooping, including by the designer | The confirmation window already exists (it ends 2026-08-31; today is 2026-09-23). The design was shaped by a model whose training cutoff (June 2026, FACT: session model information) overlaps most of confirmation, and by public commentary on GB markets in 2025–26 (INFERENCE) | Ledger of every download range. The loader refuses value-bearing confirmation blobs without the hash | Stage 0 reads confirmation metadata only, through a parser that never materialises value fields. STRONG-final needs ≥90 prospective days, counted post-freeze (row 34). Design-stage configurations counted in the ledger N. Confirmation results are reported as "designer-contamination not excluded" | high |
| 21 | Missing-data imputation using future observations | Elexon allows filling IRIS gaps from the APIs (FACT: iris-clients README:141). Such fills insert latest-version values with back-dated known_at. Also interpolation across t and full-sample means | Mandatory capture_mode column. Assert no API gap-fill row has known_at < capture time | NaN + indicator + staleness. Gap-fills get known_at = capture time. Training-window medians only. No interpolation across t (R13) | high |
| 22 | Survivorship and selection bias | WINDFOR's visible-farm set grows (FACT: scope text). "Latest" REMIT views lose withdrawn messages. Dropping days when X is missing removes stress days. Archive gaps may cluster on stress days. The current BMU list omits retired units (row 8) | Completeness by month and by \|NIV\| decile. B-only score with and without X-missing days | Units dropped only when the target is missing, identically for every arm. REMIT via /remit/revisions, including withdrawals | medium |
| 23 | Information-set asymmetry: stale incumbent baseline (the Exp 0 band lesson) | IMBALNGC and INDGEN arrive daily by midday (FACT) while WINDFOR is fresh. Leaving out live PN manufactures X skill | The same snapshot object for every arm. Test: B columns in B+X equal B's exactly. Skill by information age for B and X sources | Live aggregate PN in B (optional or mandatory rule). **For F1/F2 the protection is that B holds the same latest WINDFOR level, at the same margin_B = 2 min.** The asymmetric margin (margin_X = 10 min) protects only X-only sources: REMIT, NESO, ECMWF | high |
| 24 | Forecast combination read as market information (interpretation, not leakage) | B+F1 ≡ B+W_ref. A gain may only mean NESO's latest wind forecast can be improved (level 3 without level 4) | Mediation: F1 against B+W*; the same ablation with the first-published FUELINST wind outturn as target | "Market channel" label only if F1 skill ≥1.0% against B+W* with one-sided p < 0.10. Otherwise "physical / forecast-combination channel" | high |
| 25 | Placebo and positive-control design errors | A +1-cycle shift is future information, so the real statistic can never beat it and genuine effects are killed. Random signs keep \|revision\|, which carries scale information | Simulate each placebo on synthetic mean-only and scale-only effects before discovery | +1 cycle is a positive control. Block shuffle within hour × month. Whole-week circular shifts of ≥8 weeks. 364-day shift on its own subsample. ≥99 draws per type. The oracle leak must give ≥20% skill. A planted X at 2% must be recovered | high |
| 26 | As-of boundary ties at half-hourly publications | MELNGC, INDDEM and LOLPDRM publish half-hourly (FACT), near origins at hh:00 and hh:30. Second-level jitter decides inclusion | Distribution of UploadTime modulo 30 min. Fixtures at t − 1 s, t, t + 1 s | Strict comparison with margin_B = 2 min. Uniform 5-min margin as a sensitivity. Report how often the latest vintage is excluded | medium |
| 27 | Transaction-cost assumptions | £1.5/MWh is assumed (the real value is UNKNOWN). MID is thin. Variant A executes at a VWAP formed after t. A structural skew in SSP − MID can pay with no forecast: always-short earned $11.82M on ERCOT (FACT: t0 paper) | Cost grid £0/1.5/3/5/10 (reported, not tuned). Always-long and always-short controls | Rule frozen and non-gating for the forecasting verdict. PRODUCT SIGNAL requires variant B's lower bound > 0 and beating both controls | medium |
| 28 | Regimes selected after seeing outcomes | Plots invite post-hoc "after the platform change" or "high-NIV" claims. Exp 0's daytime mask used test actuals (FACT: metrics.py:33-65) | The verdict engine accepts only regimes in the hashed YAML. A test forbids masks built from Y or NIV | R1–R3 defined from information known at t, thresholds from discovery. New regimes only on prospective data with a ledgered α | medium |
| 29 | Market-rule and infrastructure changes | BSC modifications to price derivation in 2023-06 to 2026-08 are unenumerated (UNKNOWN). Open Balancing Platform (about Dec 2023) and ESO→NESO (Oct 2024) (INFERENCE). The August 2025 IRIS release (FACT; any uploader change INFERENCE) and IFS cycles (FACT) | Enumerate from the BSC modification register before discovery | Dates pre-registered as descriptive markers only. No post-hoc sample cuts | medium |
| 30 | Pretraining contamination (Chronos-2) | Released 2025-10-20 (FACT). Its corpus may contain GB data from 2023–26, so it could spuriously win or fail the sophistication comparison | Confirmation vs prospective skill | The sophistication comparison gates only on the prospective window (post-freeze days, row 34). Labelled "contamination not excluded". Never used to attribute information to X | medium |
| 31 | Forward recorder clock and back-dating | A capture time recorded as the nominal cron time, clock skew, or back-dated gap-fills leak into the only clean window | NTP-synced recorder clock. Alarm when capture_time − UploadTime < −skew | known_at = max(UploadTime, capture_time) + 2 min. Raw payload plus sha256 stored | medium |
| 32 | Provenance, caching and archive mutation | Exp 0's cache key omits code identity (FACT: run_benchmark.py:187-203). fillna(−1) (FACT: data.py:192). Clipping at zero (FACT: backtest.py:234). The live archive gains blobs later, changing which message counts as "first" | Reproduction runs recompute and never read the cache. Listing snapshots hashed. Negative-price fixtures | Cache key per the spec. Hash (value, isnull). No clipping. Immutable raw store outside git, with manifests hashed in git (R1) | medium |
| 33 | Human and prose leakage; vacuous controls | Numbers written from memory; controls that always pass (FACT: tests/test_benchmark.py:866, 1031; the 92-vs-90 slip). Unsaved simulations quoted as evidence (§1) | Prose-number diff test. Mutation tests: known_at shifted by −1 h, margin set to 0, a join on the Timestamp tag, the REST latest view, a rolling window on the target index. Each must make its control fail | The verdict engine writes verdict.json, and memo numbers are templated from it (R14). The simulations are saved with code, seed and data-generating process before they are cited again | medium |
| 34 | Prospective window begins before the pre-registration freeze (data snooping) | Capture starts 2026-10-01. The freeze lands no earlier than mid-November and plausibly in December 2026 (Stage 0 + 4–6 engineer-weeks + Stage 1; INFERENCE). Prospective days before the freeze can shape the design, and the ≥90-day STRONG-final requirement would then include pre-freeze data | Ledger timestamp of the freeze tag vs each prospective day. The verdict engine flags pre-freeze days | **Recommended amendment** (not yet in the decision record): STRONG-final and the Chronos-2 comparison count only prospective days *after* the tagged freeze commit. Pre-freeze prospective days go to a descriptive bucket. The earliest STRONG-final moves from about January 2027 to about March 2027 (INFERENCE); the 2027-03-31 window end may need extending | high |

**Exp 0 controls that are necessary but not sufficient here** (details in §2.2):
- The event-time contract (backtest.py:150-167) must be re-keyed to per-row known_at.
- Poisoning by event time on one series (tests/test_benchmark.py:474-535) must become poisoning by known_at per source, plus vintage-swap and label poisoning.
- Self-censoring models (forecasters.py:74) must be replaced by harness-built snapshots.
- Nothing was fitted, so there were no label-availability or transform controls.
- Holm existed only in prose.
- The 7-day moving-block bootstrap was undersized.

**Residual risks that no test removes:**
- For history, UploadTime genuineness can be checked only indirectly. Our own contemporaneous record starts with the recorder. Months on the k3 fallback are labelled, not proven.
- Soft snooping by public commentary and by the designer's training data on GB markets in 2025–26. Only prospective days after the freeze are fully clean.
- The historical BMU→fuel mapping may never be fully point-in-time if UOU2T14D does not cover all wind units.
- Every result is "beyond public information". The live GB intraday tape and BM data that professional NIV chasers use are absent from B. **[v2: Exp 1 scope.]**

## 8. Experiment 1 specification

**Status.** This section is the content of the pre-registration for **GB-IMB-2H-H**. The question it tests: do point-in-time NESO wind-forecast revisions add information about the first-published GB imbalance price 2 hours ahead, beyond current forecast levels, the live notified position, NESO's indicated imbalance and recent first-published prices?

Two gates come before anything is used on real data:
- **Stage 0, then the user.** Stage 0 must pass **k1–k7** (§8.25), and the user must then approve. Stage 0 consists of metadata audits, a small IRIS capture client for k4, and a licence read. The recommendation is RESEARCH MORE BEFORE CODING.
- **k8, after approval.** k8 is the first gate after approval: the harness tests must pass on synthetic fixtures before any real data is modelled. The decision record lists k1–k8 together as Stage 0. k8 is split out here because it cannot run without harness code (§8.0 A1).

Design parameters are decisions and carry no label. Every empirical claim is labelled FACT, INFERENCE or UNKNOWN.

**Source keys used in §§8–12.** Repo paths are relative to `/home/user/solar` at 406c92c.

| Key | Source |
|---|---|
| [IA] | Elexon IRIS archive doc: https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/iris_archive.md |
| [IP] | Elexon Insights platform doc: https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/insights_data_platform.md |
| [TS] | Elexon dataset/timestamp reference: https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/dataset_and_timestamp_reference.md |
| [GC] | Elexon MIL/MEL resolution (gate closure): https://raw.githubusercontent.com/elexon-data/insights-docs/main/docs/mil_mel_resolution.md |
| [IC] | Elexon iris-clients README: https://raw.githubusercontent.com/elexon-data/iris-clients/main/README.md |
| [EX] | `elexonpy` 1.0.16 wheel (PyPI), generated from the Insights OpenAPI spec. Read in memory again this session. |
| [EB] | `elexon-bmrs` 0.3.0 wheel (PyPI, 2025-10-16): `generated_models.py`, `generated_client.py`, `enums.py`, `field_mixins.py`. Read in memory again this session. |
| [NX] | `nixtla` 0.9.0 wheel (PyPI, uploaded 2026-09-21T05:33): `nixtla_client.py`. Read in memory this session. |
| [CH] | https://raw.githubusercontent.com/amazon-science/chronos-forecasting/main/README.md (read this session) |
| [S3] | Anonymous listings and `.index` files of https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com (read 2026-09-23) |
| [EO] | https://raw.githubusercontent.com/ecmwf/ecmwf-opendata/main/README.md |
| [R11] | Exp 0 run #11 outputs, `scratchpad/run11/*.csv`. Figures re-read this session. |
| [T0] | t0 paper text, `scratchpad/t0_paper.txt` |
| [SIM] | In-memory Monte Carlo from this session's methodology digest. **Not persisted**: no code, seeds or full parameter set exist in the scratchpad or the workflow records (searched this session). Only the parameters stated inside each result are known (listed where cited); everything else is UNKNOWN. Every [SIM] number is therefore labelled INFERENCE (simulation output that cannot be reproduced). Persistence task **P-SIM**: re-implement, seed and commit the simulation before the pre-registration is hashed. Until then these numbers motivate design choices but set no threshold. |
| [PD] | Prior digests: `scratchpad/prior_digest.json`, `weights_wf.json`, `useful_wf.json`, `product_wf.json` |

### 8.0 Amendments to the decision record made in this section

Everything not listed here uses the decision record's numbers and choices verbatim.

| # | Decision record | This spec | Reason |
|---|---|---|---|
| A1 | Stage 0 passes k1–k8 | Stage 0 = k1–k7; k8 is the first build gate | k8 needs harness code |
| A2 | Prospective window 2026-10-01 → 2027-03-31; ≥ 90 days by 2026-12-29 | Prospective start = max(2026-10-01, P + 1), where P is the date the pre-registration tag is committed; ≥ 90 days after P. 2026-09-01 → P is sealed as a "post-design, pre-freeze" block | P cannot precede about mid-November 2026 (INFERENCE: Stage 0 ≥ 15 days for k4, build 4–6 engineer-weeks, Stage 1 about 1 week, all from 2026-09-23). Days observed before P are not prospective |
| A3 | ≥ 99 draws per placebo type | A draw rule per type (§8.10) | A 364-day shift is 1 draw; whole-week circular shifts of ≥ 8 weeks give 37 |
| A4 | The +1-cycle vintage must improve skill and the 2% planted X must be recovered, or the run is INVALID | Validity gates are high-power by construction. The 2% planted X and the +1-cycle skill become power calibration | 2% sits at or below the MDE, so a true null would often end INVALID instead of FAIL |
| A5 | FAIL, INTERESTING and STRONG overlap | Separate verdicts for claims C1 and C2, with precedence. FAIL = UB < 2.0% **and** no Holm rejection. New label INTERESTING-below-SESOI | Example: Holm-significant with UB < 2.0% was both FAIL and INTERESTING |
| A6 | k1 "expected messages", k5 "median lag", k5 → design kill, D0 "from which" | Expected counts declared per dataset. Lag defined. Failing months excluded, with batches recomputed. > 15% of confirmation excluded → hybrid design. D0 needs 9 consecutive passing months | Makes these criteria mechanical |
| A7 | Latest-run SSP called a "non-gating sensitivity", yet gate (g) uses it | Used for gate (g) only, with its run-type mix stated. Prospective settled price = the recorder's REST value at s + 30 days | Internal contradiction |
| A8 | Information-age bands 0–2 h, 2–4 h, > 4 h | WINDFOR bands follow the publish schedule; DISEBSP bands are warm-up terciles | WINDFOR publish gaps are ≤ 4 h, so the > 4 h band is nearly empty (§8.4) |
| A9 | Competitor arm "nixtla explain() style" | Local statsmodels Granger plus a pinned local transfer-entropy (TE) estimator; no hosted API | explain() runs as a server-side job (FACT, [NX] `nixtla_client.py:1530-1555`) |
| A10 | α 0.04 + 0.01, reuse at 0.005 | Unchanged. Any reuse is now disclosed as pushing FWER above 0.05 **[v2 correction: withdrawn. The 0.05 + 0.005k bound is invalid under adaptive reuse. Post-unseal tests are exploratory only.]** | The 0.05 budget is already fully spent |
| A11 | K-competence: "fix B before sealing" | A pre-declared repair list, one ledgered round, otherwise STOP | Open-ended redesign of B creates forking paths |
| A12 | Open items in the economic rule | Decided in §12.2 | A rule called "frozen" must be complete |
| A13 | Chronos-2 comparison gated on the prospective window | Gate unchanged. Added: a descriptive comparison on confirmation days after the checkpoint date, and an optional chronos-2-synth control | Days after the checkpoint cannot be in its pretraining (INFERENCE) |
| A14 | "≤ 48 variants" | An explicit 27-variant grid; F2 is one joint variant | Bonferroni divisors must be fixed |
| A15 | B item 2 "first-published", but also "latest vintage ≤ t" | First-published values only, for every SSP/NIV lag, median and N1–N6 | Matches the target's vintage |

### 8.1 Market

- **Venue.** GB balancing and settlement under the BSC (Elexon).
- **Price.** A single imbalance ("cash-out") price, SSP = SBP.
  - "Single price since P305 on 2015-11-05" is UNVERIFIED (search summary only).
  - Weak support: the spec example record has `systemSellPrice = systemBuyPrice = 215` (FACT, [EB] `generated_models.py:596-597`).
- **Settlement periods.** 30-minute SPs. A settlement day has 46, 48 or 50 SPs around clock changes (FACT, computed with `zoneinfo` Europe/London).
- **Why GB.** Of the markets examined, GB is the only one where the target and multi-vintage TSO forecast revisions both have free, machine-checkable first-availability times. Every IRIS message is archived with an `UploadTime` tag, and the forecast datasets carry `publishTime` (FACT, [IA], [TS], [EX]).
- **What is given up:**
  - DE-LU and FR (point-in-time reconstruction on free data is infeasible);
  - a continuously traded target (the GB price is administered from BM actions);
  - the live GB intraday price and GB day-ahead auction prices (paid or not free);
  - transferability to coupled EU markets.
- **Fallbacks:**
  - **Belgium: continental replication.** Elia per-minute imbalance prices are "never validated" from 2024-05-22 (FACT, `elia-py` 0.3.1 docstrings, per [PD]).
  - **ERCOT: out-of-Europe fallback if Stage 0 kills GB.** The archive filters on `postDatetime` and returns every hourly posting (FACT, gridstatus `ercot_api.py:435-443`). How deep the archive goes is UNKNOWN.

### 8.2 Target

| Role | Definition | Notes |
|---|---|---|
| **Primary Y_s** | The first-published SSP_s (£/MWh): the DISEBSP message with the minimum `UploadTime` for (settlementDate, settlementPeriod) in the IRIS archive. The message id is stored. `known_at(Y_s) = max(createdDateTime, UploadTime) + 2 min`; this equals `UploadTime + 2 min` whenever createdDateTime ≤ UploadTime. | REST cannot supply this: it returns "only messages generated for the latest settlement run" (FACT, [EX] `indicative_imbalance_settlement_api.py:1566, 1665`). `SystemPriceResponse` carries `createdDateTime` but no run-type field (FACT, [EB] `generated_models.py:593-613`, `field_mixins.py:139-141`). |
| **Exclusion** | If the first DISEBSP `UploadTime` is later than SP end + 60 min, flag the SP "first vintage missing" and exclude it from every arm. | Excluded share reported by month and by \|NIV\| decile. |
| **Secondary (in the Holm family)** | First-published NIV_s in signed MWh (`netImbalanceVolume` from the same message). | NIV > 0 means the system is short. The spec example arithmetic agrees: 790.6547 − 738.74115 + 240 − 0 = 291.91355 vs the example 291.9136 (FACT, [EB] `generated_models.py:601-609`). Check empirically before sealing. |
| **Latest-run price (gate (g) only)** | Historical windows: the SSP from a single REST snapshot, downloaded on one fixed, recorded date on or after 2026-10-15. Prospective window: the recorder's REST value captured at s + 30 days (± 1 day; capture_time stored). | Used only by STRONG gate (g) (§8.24) and by the §12 P&L. It is not in the Holm family, and it is banned from features (PIT rule 3). **Heterogeneity:** one snapshot mixes settlement runs across the window. Older SPs will be at later reconciliation runs than recent ones, and REST exposes no run-type field, so the mix cannot be controlled or observed (FACT that the field is absent; the run timetable is UNVERIFIED). Gate (g) is lenient (skill ≥ 0) for this reason. |
| **Precondition (k2)** | The first DISEBSP message must be a near-real-time run, published ≤ 60 min after SP end, in every month used. | **UNKNOWN.** See the evidence list below this table. If the first message comes days after the SP, this target and B item 2 are void. |

**Evidence on the precondition (k2).**
1. The REST endpoints return prices "generated by the SAA … relating to the data for a settlement run", "latest settlement run" only (FACT, [EX] `indicative_imbalance_settlement_api.py:1566, 1665`).
2. The REST client groups DISEBSP under an "indicative imbalance settlement" module (FACT, [EX] module `indicative_imbalance_settlement_api.py`).
3. `SettlementruntypeEnum` (II/SF/R1/R2/R3/RF/DF) is attached only to `IndicativeDemandPeak`, `TudmDatasetRow` and `TotalExemptSupplyVolumeResponse`, not to `SystemPriceResponse` (FACT, [EB] `generated_models.py:1142-1146, 1388-1395, 1893-1897`; `enums.py:285-295`). The enum therefore says nothing about DISEBSP.

That IRIS DISEBSP includes a near-real-time indicative run is INFERENCE from the grouping alone. The run type of the first IRIS DISEBSP message is UNKNOWN. Only Stage 0-B (R0-B) resolves it, from the distributions of `UploadTime − SP end` and `createdDateTime − SP end`.

### 8.3 Horizon

- **h = 2 h.** The target SP starts exactly 120 min after the origin t; this is asserted on every row.
- **Gate closure.** BM gate closure for SP s is at s − 60 min (FACT, [GC]: "one hour prior to the start of a Settlement Period"). A participant therefore still has 60 min to act.
- **Resolution.** The target resolves at the first DISEBSP upload, nominally around s + 45 min, i.e. about t + 2 h 45. This is UNVERIFIED and Stage 0-B measures it.
- **Other horizons.** h = 1 h and h = 4 h are computed for description only and belong to no test family.

### 8.4 Forecast origin, frequency and shared definitions

- **Origins.** Every UTC half-hour (hh:00 and hh:30), 48 per UTC day. Target settlement days in Europe/London have 46, 48 or 50 SPs.
- **Inference unit.** The target's settlement date. The unit statistic is the daily mean loss over that date's SPs.
- **Refits** (all at Monday 00:00 UTC):

  | Refit schedule | Applies to |
  |---|---|
  | Weekly | Every model in Stage 2 and the prospective window; in Stage 1, all 6 F1 variants, the finalists, G, and the placebo and positive-control arms compared with them |
  | Monthly (first Monday of the month) | Stage 1 screening of F2–F8 (L at 5 quantiles) only |
- **SP block** (used by the N-rule bands, N6, the conformal pools and coverage). Six blocks by the SP's local (Europe/London) start time: [00:00, 04:00), [04:00, 08:00), [08:00, 12:00), [12:00, 16:00), [16:00, 20:00), [20:00, 24:00).
  - On 46-SP days, block 1 has 6 SPs; on 50-SP days it has 10 (both copies of the repeated hour).
  - Block 5 coincides with regime R3.
- **Chronos-2 subset.** Origins at 00:00, 06:00, 12:00 and 18:00 UTC only. Every model is scored on the same subset for the Q2 comparison.
- **Mandatory diagnostic: skill by information age**, where age = t − `known_at`.
  - **WINDFOR.** Bands are [0, 1) h, [1, 2) h, [2, 3) h and [3, 4.5) h, plus a count of origins with age ≥ 4.5 h (a missed or late publish).
    - Why these bands: the scheduled publishes at 03:30, 05:30, 08:30, 10:30, 12:30, 16:30, 19:30 and 23:30 leave gaps of 2, 3, 2, 2, 4, 3, 4 and 4 h (FACT, schedule in [EX] `generation_forecast_api.py:1128`; gaps are arithmetic; the timezone is unstated). Normal ages are therefore about 0.5–4.1 h. The decision record's "> 4 h" band would be almost empty.
    - Note: line 1128 is the docstring of the "earliest" forecast view, which is itself denylisted (PIT rule 8).
  - **Latest first-published DISEBSP.** Terciles of age over the warm-up window, frozen in the YAML, because the first-publication lag is UNKNOWN until k2.
  - **Why this diagnostic is mandatory.** In Exp 0, t0 scored −15.6% against prev_day in the D-1-source band and +13.7% in the D-2-source band (FACT, [R11] `pairwise_by_band.csv` rows 2 and 4).

### 8.5 Historical period (conditional on Stage 0)

| Block | Dates | Size | Use |
|---|---|---|---|
| D0 (base case) | 2023-06-01 | — | The earliest dated IRIS example in Elexon's docs is 2023-06-18 (FACT, [IA]). Actual coverage is UNKNOWN. |
| Warm-up | 2023-06-01 → 2023-11-30 | 183 days | Training only, never scored. Fixes c, the N4 α and the DISEBSP age terciles. |
| Tuning | 2023-12-01 → 2024-02-29 | 91 days | LightGBM hyperparameters on the B-only arm. Excluded from Stage 1 tests. |
| Discovery test | 2024-03-01 → 2025-02-28 | 365 days, 17,520 SPs, 26 × 14-day batches | DST days: 2024-03-31 (46 SPs) and 2024-10-27 (50). Counts are FACT, computed. |
| F6 evaluable | 2024-09-04 → 2025-02-28 | 178 days | 100u/100v/ssrd exist from 2024-03-06 (FACT, [S3] index files). The 06z run of 2024-03-05 already carries them; the design starts conservatively at 2024-03-06. With 182 days of training, the first F6 forecast falls on 2024-09-04. |

- **D0 rule (pre-registered).** D0 is the first calendar month m such that m and the next 8 months (the warm-up plus tuning span) all pass k1–k3 for every B and F1 dataset. Later failing months are excluded under the §8.25 exclusion rule; they do not move D0.
- **If D0 slips:**
  - Discovery shrinks first, to a minimum of 273 days. Confirmation stays ≥ 365 days and ends 2026-08-31.
  - The latest D0 that still allows a fully historical design is 2024-02-11 (computed: 183 + 91 + 273 + 21 + 365 days ending 2026-08-31).
  - D0 after 2024-02-11 and on or before 2025-03-01: confirmation becomes the historical remainder pooled with post-P prospective capture until it reaches ≥ 365 days.
  - D0 after 2025-03-01: forward capture only, for ≥ 12 months, or STOP.
- **Nothing before D0 is used, including REST `/history` vintages.** Insights history migrated from dumps can carry a synthetic `publishTime`: IGCPU entries "were assigned a default publishTime of 2023-01-01 00:00 during the migration" (FACT, [EB] `generated_client.py`, `get_datasets_igcpu`).

### 8.6 Test period

| Block | Dates | Size and rules |
|---|---|---|
| Embargo | 2025-03-01 → 2025-03-21 | 21 days (≥ 14 days + 7-day maximum feature lag + h) |
| Leftover days | 2025-03-22 → 2025-03-31 | 10 days. Sensitivity only: in no batch and not in gate (d). |
| **Sealed confirmation (batched)** | 2025-04-01 → 2026-08-31 | 518 days = 37 non-overlapping 14-day batches (the only split that yields 518 batch days; computed). Including the leftover days, the confirmation window is 2025-03-22 → 2026-08-31: 528 settlement days and 25,342 SPs. DST days: 2025-03-30 (46; a leftover day), 2025-10-26 (50) and 2026-03-29 (46). Counts FACT, computed. |
| Quarters for gate (d) | Q2-2025, Q3-2025, Q4-2025, Q1-2026, Q2-2026, **Q3-2026 partial (July–August only, 62 days)** | 6 quarters. The March leftover days are excluded. |
| Why confirmation ends 2026-08-31 | — | 2026-08 was the last complete month before the design date of 2026-09-23 (INFERENCE about the decision record's intent). September 2026 is not assigned to confirmation. |
| **Post-design, pre-freeze** | 2026-09-01 → P | Sealed. Values are routed into the hash-gated store (PIT rule 12). After unsealing it is reported once, descriptively. It is never used in a gate, never pooled into the extension, and never called prospective. |
| **Prospective** | max(2026-10-01, P + 1) → max(2027-03-31, P + 90) | P = the date the pre-registration tag is committed. Read from the IRIS archive and cross-audited by our own capture. STRONG-final needs ≥ 90 days after P. This window also hosts the single pre-committed pooled extension at α = 0.01. The decision record's nominal 2026-10-01 → 2027-03-31 (182 days, 13 batches) holds only if P ≤ 2026-09-30, which is infeasible (INFERENCE, §8.0 A2). If P falls between mid-November and December 2026 (INFERENCE), the earliest STRONG-final moves from about January 2027 to about February–March 2027. |

**Sealing**
- The confirmation window is unsealed exactly once, after the SHA-256 of the pre-registration YAML is committed and tagged.
- The loader refuses value-bearing blobs with a valid time after 2025-02-28 unless it is given that hash.
- Stage 0 may read confirmation **metadata only**: blob tags, plus key fields parsed by a parser that never materialises price, NIV or forecast values.

**Known hazards inside confirmation**
- IRIS was re-platformed in August–October 2025, and old queues were deleted on 2025-10-02 (FACT, [IC]). Audited by k5.
- ECMWF IFS 50r1 took effect on 2026-05-12, and the 06/18z stream was renamed from `scda` to `oper` (FACT, [S3]: 2026-05-11 06z is still `scda`; 2026-05-12 06z is `oper`).

### 8.7 Walk-forward procedure

Rolling-origin evaluation of direct h = 2 h models. Each is fitted on a fixed-length 182-day window that never expands. A rolling or fixed window keeps Giacomini–White finite-sample inference valid (INFERENCE, recalled from Giacomini & White 2006, not re-read).

1. **As-of snapshot.** At each origin, the harness builds the feature matrix from the latest row with `known_at ≤ t` for each (series, valid period). The exception is SSP/NIV lags, which are always first-published (§8.9 item 2). Models see only this matrix, never the store.
   - This replaces Exp 0's `predict(series, windows)` (FACT, `solarbench/forecasters.py:74`), which handed each model the full series, future included, and trusted it to censor itself.
2. **Refit admission.** At each refit (§8.4), a training row (t′, s′) is admitted only if:
   - its features were built as of t′, **and**
   - its label's `known_at` is at or before the refit time.
3. **What is fitted where.**
   - Inside each window: scalers, imputation medians, the capacity normaliser (trailing 90-day p99 of WINDFOR levels known at t) and the conformal residual pools.
   - Frozen in the YAML from warm-up: the asinh constant c, the N4 α and the DISEBSP age terciles.
   - From discovery only: regime thresholds.
4. **LASSO-QR penalty.** Chosen by purged blocked CV inside each window: 28-day folds, with a purge of 7 days + 2 h + label lag.
5. **LightGBM hyperparameters** (num_leaves, min_data_in_leaf, learning_rate, n_rounds).
   - Chosen once, on the B-only arm, over the tuning window 2023-12-01 → 2024-02-29.
   - Then frozen identically for B and every B+X arm.
   - Settings: `deterministic=true`, `force_row_wise=true`, seed 0, pinned version.
6. **Stage 1.**
   - Screening of F2–F8: L at 5 quantiles (0.1, 0.25, 0.5, 0.75, 0.9) with monthly refits.
   - F1 (all 6 variants) and every finalist: 19 quantiles with weekly refits, plus G.
   - **F1 futility** uses that full specification (§8.24).
7. **Stage 2.** Specifications are frozen; parameters keep re-estimating on the rolling window.
8. **Forecast cache.** Keyed on:
   - raw-snapshot manifest hash;
   - as-of definition hash;
   - pre-registration hash;
   - model spec;
   - git SHA;
   - lock hash.

   Reproduction runs always recompute and never read the cache. Exp 0's cache key omitted code identity (FACT, `run_benchmark.py:187-203`).

### 8.8 Target transformation

- **Fit and primary score on z = asinh(Y/c).**
  - c = the median absolute deviation of first-published SSP over warm-up, rounded to £1, and frozen before any discovery forecast.
  - Back-transform: q_Y = c·sinh(q_z). This is exact because quantiles are equivariant under monotone maps.
  - Pinball loss on z is a consistent (GPL) quantile score, so a few scarcity spikes cannot decide the result (INFERENCE, scoring-rule theory).
- **£ scale.** £ pinball is co-reported. STRONG requires £-scale skill > 0 (gate f).
- **NIV endpoint.** Raw MWh, no transform.
- **No clipping.** Negative prices are legitimate. Exp 0's `np.clip(pred.values, 0.0, None)` (FACT, `solarbench/backtest.py:234`) must not be reused.
- **Quantile crossing.** Fixed by sorting; the number of crossings is reported.

### 8.9 Initial baseline information set B

Every item is the latest vintage with `known_at ≤ t` under PIT rule 2 (margin_B = 2 min). The one exception is item 2.

| # | Block | Content | known_at and facts |
|---|---|---|---|
| 1 | Calendar | Europe/London SP-of-day, day-of-week, GB bank holiday (pinned, committed table), two day-of-year harmonics, clock-change flag | Deterministic |
| 2 | DISEBSP history, **first-published only** | Last known SSP and NIV; mean of the last 4 known values; same SP on D-1 and D-7 in local clock time (23 or 25 h back on switch days); 28-day same-SP median | The first message's `known_at` (§8.2). **Declared deviation:** later settlement runs of a lagged SP are never used, even when known at t, so features and target share one vintage (YAML `lag_vintage: first_published`). |
| 3 | MID | APXMIDP price and volume; N2EXMIDP volume; last known value | First `UploadTime`. MID has no `publishTime` (FACT, [EX] market-index models). Data comes "from each of the appointed Market Index Data Providers … for each Settlement Period" (FACT, [EX] `datasets_api.py:7647-7649`). Its IRIS Timestamp tag is `startTime` (FACT, [TS]). **Drop MID from B before discovery** if first-`UploadTime` − SP end exceeds 60 min for more than 5% of SPs. |
| 4 | Latest forecast levels for s | WINDFOR, NDF, TSDF, INDGEN, INDDEM; IMBALNGC (NESO's indicated imbalance = generation PNs − TSDF); MELNGC; LOLP and DRM at the latest horizon legal at t | `publishTime`, audited against `UploadTime`. Cadences are listed below this table. |
| 5 | Latest outturns | FUELINST wind, CCGT and interconnector totals; INDO/ITSDO | `UploadTime` / `publishTime`. FUELINST is "updated at five-minute intervals" and aggregated by fuel type (FACT, [EX] `datasets_api.py:4562-4564`). |
| 6 | Live notified position | Latest aggregate Physical Notification for s: total, and wind BMUs only | From `UploadTime` (+ margin_B). **Never** the PN Timestamp tag, which equals `timeFrom` (FACT, [TS]). The wind/non-wind split uses the static BMU mapping exception (PIT rule 2, §8.12). Optional only if Stage 0 shows IMBALNGC, INDGEN and INDDEM each refreshed at least every 60 min within the 6 h before t on ≥ 95% of origins; otherwise mandatory. |
| 7 | FREQ | Mean and minimum deviation from 50 Hz over [t − 30 min, t − margin] | `UploadTime`. FREQ carries only `measurementTime` and is "received every 2 minutes" (FACT, [EB] `get_datasets_freq`). |
| 8 | Information age | t − `known_at` for every source | — |

**Published cadences for item 4** (FACT unless marked):
- WINDFOR: up to 8 publishes a day ([EX] `generation_forecast_api.py:1128`).
- INDDEM: "every half hour"; MELNGC: "every half an hour" ([EX] `datasets_api.py:5214-5416`).
- LOLPDRM: "received half-hourly" ([EX] `datasets_api.py:6226`).
- IMBALNGC and INDGEN: "received daily by midday" ([EX]).
- NDF/TSDF: **conflicting**. The docs say both "received daily" and "updated every 30 minutes" ([EB] `get_datasets_ndf`/`tsdf`; [EX] `demand_forecast_api.py:545`).

**Arm definitions**
- **B+ (STRONG gate (h) only).** B plus the net BOALF accepted offer and bid volume over [t − 60 min, t − margin].
  - Only first messages are used. BOALF rows carry an `amendment_flag` (FACT, [EX] BOALF model).
  - known_at comes from `UploadTime`, never `acceptanceTime`.
- **B+W\* (mediation arm).** B plus W\*_s: the L-model median prediction of wind outturn for s, fitted on all WINDFOR vintages known at t.
- **B-PNtotal (sensitivity).** B with the wind/non-wind PN split removed. This removes any dependence on the BMU mapping.

**Key algebra.** B holds the latest level L_t of every forecast whose revision is tested. So B + (L_t − L_ref) spans the same information as B + L_ref. A gain from F1 therefore means the **older vintage, or the path of revisions**, carries information beyond the current level. It does not show that "revisions move markets" (§10.6).

**Excluded:** the live GB continuous intraday price (EPEX GB, paid); GB day-ahead auction prices; vendor NIV or price forecasts; licensed NWP. The further omissions listed in §8.10.2 mean every claim reads strictly as **"beyond B"**. B is a strong public baseline, but it is not all public information (INFERENCE).

### 8.10 Candidate covariates

Claims are made per family (a physical variable × a mechanism), never per lag. The limits are ≤ 8 families and ≤ 6 variants per family (≤ 48 in total). The declared grid below has **27 variants**. It is hashed in the YAML, and each family's Bonferroni divisor is its declared count after the Stage 0 collapse rules have been applied.

#### 8.10.1 Families and variant grid

| Family | Definition | Variants (count) | Vintage key and facts |
|---|---|---|---|
| **F1, PRIMARY:** NESO WINDFOR revision for SP s | W_latest(t)[s] − W_ref[s]. Always carried to Stage 2 unless futility fires. IGCA/IGCPU are never used for normalisation. | ref ∈ {last vintage with `known_at` ≤ 09:00 Europe/London on D-1; previous publish; vintage ≥ 6 h old} × {MW; MW ÷ trailing 90-day p99 of WINDFOR levels known at t} **(6)** | `publishTime`, audited against `UploadTime`. Covers ESO-visible metered wind only (FACT, [EX] `generation_forecast_api.py:1128`). The GB day-ahead auction times behind the 09:00 reference are UNVERIFIED. |
| **F2:** path beyond the endpoints (brief §4D) | One joint feature group of 4 statistics: count of consecutive same-sign revisions in the last 24 h; cumulative revision over 6 h; cumulative revision over 12 h; time since the last revision. All in normalised units. | **(1)**. Tested as B+F1\*+F2 vs B+F1\*, where F1\* is the frozen best F1 variant. | As F1 |
| **F3:** demand revision | latest − ref | ref ∈ {D-1 09:00; vintage ≥ 2 h old} × series ∈ {NDF; TSDF} **(4)**. **Collapse rule:** if fewer than 2 vintages per target SP exist on ≥ 50% of origins, the "≥ 2 h" variants are dropped **(2)**. | Cadence conflicted (§8.9) |
| **F4:** position revision | latest − ref | ref ∈ {D-1 09:00; change over the last 2 h} × group ∈ {NESO: INDDEM, IMBALNGC and INDGEN jointly; PN: total and wind jointly} **(4)**. Same collapse rule as F3. Without PN: **(2)**. | `publishTime` / `UploadTime` |
| **F5:** tightness revision | Change, using only horizons legal at t. The 1-h LOLP horizon is illegal at a 2-h origin. | window ∈ {2 h; 6 h} × series ∈ {MELNGC; DRM; LOLP} **(6)** | Horizons 1/2/4/8/12 h (FACT, [EB] `get_forecast_system_loss_of_load`) |
| **F6:** free NWP run-to-run revision | ECMWF IFS HRES `ifs/0p25`, from 2024-03-06. Streams: 00/12z `oper`; 06/18z `scda` until 2026-05-11, `oper` from 2026-05-12. 100u/100v → fixed power curve → GB wind proxy. Latest run − previous run at s, linearly interpolated from 3-hourly steps. Spatial weights: a frozen capacity map if Stage 0 verifies a vintaged source; otherwise equal weights over pre-declared GB onshore/offshore boxes. | **(1)** | `known_at` = max S3 `LastModified` over the step files used + 10 min. Upload lag 6.45–8.57 h after init; 0 of 280 sampled runs missing (FACT, [S3]). Steps are 3-hourly (FACT, [EO] lines 376–381). IGCPU has no coordinates (FACT, [EB] `IgcpuDatasetRow`). |
| **F7:** REMIT news | MW of unplanned unavailability newly published in a lookback window and covering s. Uses `publishTime` and `revisionNumber`, including withdrawals via `/remit/revisions`. Labelled **"information, not revisions"**. | lookback ∈ {1 h; 3 h; 6 h} **(3)** | FACT, [EB] `RemitMessage`; [EX] `remit_api.py` |
| **F8 (conditional):** NESO embedded solar/wind forecast revision | Solar and wind jointly | ref ∈ {D-1 09:00; previous publish} **(2)**. Admitted only if Stage 0 verifies per-row issue timestamps and complete as-published archives; otherwise dropped before discovery and recorded in the ledger. | Issue-time columns UNVERIFIED (neso.energy returned 403) |

#### 8.10.2 Disposition of the brief's other candidate covariates

| Brief §5 covariate | Where it sits | Reason |
|---|---|---|
| Historical prices; traded volume | B (first-published SSP/NIV; MID price and volume) | MID volume is the only free traded-volume proxy (FACT that MID carries volume, [EX]) |
| Order book / microstructure | Excluded | EPEX GB data is paid (§8.12) |
| Load and load forecasts, level | B (NDF, TSDF, INDDEM, INDO/ITSDO) | — |
| Load forecasts, revisions | F3, F4 | — |
| Wind generation and forecasts, level | B (WINDFOR, FUELINST wind) | — |
| Wind forecasts, revisions | F1, F2, F6 | — |
| Solar | F8 only (conditional); not in B | Whether FUELINST has a solar category is UNVERIFIED; GB solar is largely embedded (INFERENCE) |
| Temperature forecasts and their revisions | Not a separate X; weather-forecast revisions enter only through F6 | Elexon TEMP is a daily outturn "measured at midday … received from 5pm each day", not a forecast (FACT, [EX] `datasets_api.py:14371-14373`). NGESO already uses it in demand forecasting (FACT, [EX] `temperature_api.py:38`), so the temperature-forecast channel runs through NDF/TSDF (INFERENCE). |
| Gas and carbon prices | Excluded | No free point-in-time intraday source was identified; NBP and UKA prices are exchange data (INFERENCE: paid). Their slow level effect reaches B only through trailing price medians (INFERENCE). This is a disclosed gap in B. |
| Nuclear availability; generation outages | F7 | — |
| Hydro; storage | Not in X; partly present in B through PN and MELNGC (INFERENCE) | No forecast vintages, so no revision mechanism. The FUELINST category list is UNVERIFIED here. |
| Cross-border flows | B (FUELINST interconnector totals) | — |
| Available transmission capacity; neighbouring-market prices | Excluded | ENTSO-E serves the latest version only and carries no publication timestamp (INFERENCE, strongly supported [PD]). A `known_at` would have to come from a nominal schedule, which PIT rule 2 forbids. Neighbouring continuous prices are paid. **Disclosed gap:** B omits information that professionals see. |
| Calendar | B | — |

#### 8.10.3 Controls (not families)

**Placebos.** Each is run through the same pipeline as the statistic it is compared with.

| Type | Draws | Pass rule |
|---|---|---|
| 364-day shift, evaluated on its own subsample (discovery days with a shifted source ≥ D0) | **1** (deterministic) | The real statistic on the same subsample exceeds the placebo statistic |
| Whole-week circular shift within the discovery window | **All 37 admissible shifts** (k = 8 … 44 weeks) | Exact rank p = (1 + #{placebo ≥ real}) / 38 ≤ 0.05. This means the real statistic must beat all 37. |
| Block shuffle of the revision vector within hour × month cells | **≥ 99** | Rank p = (1 + #≥) / (N + 1) ≤ 0.05. This replaces random sign flips, which keep \|revision\| and so can carry real scale information. |

**Validity controls.** Failure makes the run INVALID. Each is high-power by construction.

| Control | Requirement |
|---|---|
| Oracle leak of first-published Y_s | ≥ 20% skill. It must raise when the `known_at` contract is enforced. |
| Planted synthetic X at **10%** skill (calibrated on warm-up only; registry-flagged synthetic, `known_at = t` by construction) | Recovered: discovery skill ≥ 5% and one-sided Newey–West p ≤ 0.01 |
| +1 publication-cycle (future) vintage | Forecasts change on ≥ 99% of origins where the future vintage differs, **and** the contract raises when enforced. Its skill is **not** gated. |

**Power calibration.** Reported, not gated:
- the recovery rate of a planted X at 2% skill over the discovery pipeline;
- the skill of the +1-cycle vintage.

These show how far a 2%-sized effect is detectable here, and whether even future wind information improves the price forecast.

**Mediation.** B+W\*, plus a physical target (first-published FUELINST wind outturn for s). These determine the channel label (§10.6).

**Competitor arm.** An in-sample screen over all 27 variants on each training window. Level 2 on the ladder in §11.1: lead/lag association only.
- Implementation: local `statsmodels` Granger tests, plus a pinned local transfer-entropy estimator. The package choice is UNKNOWN and will be fixed in the YAML.
- **No hosted API.** nixtla's `explain()` runs "as an asynchronous job on the server" (FACT, [NX] `nixtla_client.py:1530-1555`). Using it would send BMRS data to a third party, and the BMRS licence is UNKNOWN.
- Reported: the share of the screen's picks that also pass the out-of-sample and placebo gates.

### 8.11 Point-in-time rules

1. **Row schema.** Each row carries:
   - source, dataset, series_key;
   - valid_start_utc, valid_end_utc;
   - issue_time (`publishTime`, `createdDateTime`, `createdTime` or init);
   - upload_time, s3_last_modified or capture_time;
   - known_at, vintage_id (blob name + sha256), revision_number;
   - capture_mode ∈ {iris_archive, s3, forward_capture, rest_crosscheck};
   - value, is_missing.

   Raw payloads are immutable and live outside git; their manifests are hashed in git.
2. **known_at = max(issue_time if present, `UploadTime`) + margin.**
   - margin_B = 2 min for datasets in B.
   - margin_X = 10 min for X-only sources (REMIT, NESO).
   - ECMWF: max `LastModified` + 10 min.
   - Own capture: max(`UploadTime`, capture_time) + 2 min.
   - Never use init_time, nominal schedules, settlementDate, blob-name times or the IRIS Timestamp tag. That tag means `startTime` for MID, `timeFrom` for PN and `settlementDate` for BSAD (FACT, [TS]: "the tag is always called Timestamp, regardless of the time it references").
   - **The only exception: static BMU reference data.** The BMU → fuelType classification is captured once from `/reference/bmunits/all`, which is "a current list of BM units", with no effective-from or publish field (FACT, [EX] `reference_api.py:38`; `ReferenceBmUnitData` fields). Its `known_at` (the capture time) is later than every historical origin. It is used only to split PN into wind and non-wind. It is declared in the YAML and bounded by the B-PNtotal sensitivity (§8.9). The leak channel is fuel-type reclassification, judged small (INFERENCE).
   - Sensitivity run: a uniform 5-min margin.
3. **Target.** The first DISEBSP message by minimum `UploadTime`; assert `UploadTime` > SP end. Latest-run REST prices and later settlement runs are banned from features.
4. **As-of builder.** This is the only path from data to models. Lineage is persisted per prediction: row ids, per-source max `known_at` and max label `known_at`. The harness asserts that every value is ≤ t. This is Exp 0's contract (FACT, `solarbench/backtest.py:150-167`) re-keyed from event time to `known_at`.
5. **Truncation equivalence.** On ≥ 1,000 stratified origins, physically deleting rows with `known_at` > t must give byte-identical features. Strata: all DST days, publish boundaries, and the August–November 2025 migration months.
6. **Poisoning.** Run over one registry shared by the CLI and the tests. Features and forecasts must not change when:
   - rows with `known_at` > t are rewritten per source (affine, NaN, sign-flip);
   - later vintages of periods that are already valid are rewritten;
   - labels with `known_at` > refit time are poisoned. This applies to the learners, N1–N6, the EWMA and the conformal pools.
7. **Validity controls must fire** (§8.10.3):
   - oracle ≥ 20% skill;
   - the planted 10% X is recovered;
   - the +1-cycle vintage changes forecasts;
   - with the contract enabled, the leak arm and the +1-cycle arm must raise.
8. **Denylist**, enforced by an import and lineage test:
   - REST latest-run system prices and all non-first DISEBSP runs in features;
   - DISPTAV, EBOCF, ISPSTACK, BOAV;
   - the composite market-depth and settlement-summary endpoints;
   - B1610, "published five days after the end of the operational period based on the Interim Information (II) Settlement Run" (FACT, [EX] `datasets_api.py:1088`);
   - "latest/earliest" forecast views;
   - NETBSAD and DISBSAD;
   - pre-D0 IGCA/IGCPU `publishTime`s;
   - Open-Meteo Historical Forecast and 49R1 hindcasts;
   - ERA5;
   - WeatherNext2 "historical";
   - AIFS files in the F6 lineage;
   - any hosted-API call in the competitor arm.
9. **Deduplication.** The key includes `UploadTime`, and rows are never collapsed across `UploadTime`s. API gap-fills, which Elexon permits (FACT, [IC]), get `known_at` = capture time.
10. **Time handling.**
    - UTC internally; naive datetimes are rejected.
    - Payload `startTime` must equal the Europe/London mapping of (settlementDate, SP).
    - Each date has 46, 48 or 50 SPs, with no duplicate UTC `startTime`.
    - Every dropped row is logged with a reason code. Exp 0 lost 6 rows silently (FACT, [PD] run_meta vs manifest).
    - The WINDFOR publish timezone is resolved from `UploadTime`.
11. **Fit inside the fold.**
    - Transform-invariance test: perturbing all data after refit time T leaves every parameter fitted at T unchanged.
    - CV folds are purged.
    - Hyperparameter code asserts that every date it uses precedes the discovery test start.
12. **Sealing.**
    - The YAML hash is committed and tagged (on date P) before any discovery forecast.
    - The loader refuses value-bearing blobs with a valid time after 2025-02-28 unless given that hash. This covers confirmation, the post-design block and anything the recorder captures before P, all of which go to the sealed store.
    - The metadata parser drops value fields.
    - A hash-chained, append-only ledger records every download range, window access, rerun and configuration. It feeds α-spending and the N of the deflated Sharpe ratio (DSR).
13. **Missingness.**
    - Explicit NaN plus a missing indicator and a staleness feature. The fingerprint hashes (value, isnull).
    - Never `fillna(-1)`: Exp 0's fingerprint cannot tell NaN from −1 (FACT, `solarbench/data.py:192`).
    - No interpolation across t.
    - Units are dropped only when the target is missing, identically for every arm; never because X is missing.
14. **Numbers and mutation tests.**
    - Every memo number is generated from committed code via run outputs, and a prose-number diff test checks them.
    - Each control has a mutation test that must make it fail: `known_at` shifted by −1 h; margin = 0; joining on the Timestamp tag; using the REST latest view; a rolling window on the target index.
    - Exp 0 had two vacuous asserts (FACT, `tests/test_benchmark.py:866,1031`).
15. **Subsets.** Only pre-registered regimes built from information known at t. Outcome-defined subsets are forbidden.

### 8.12 Data sources

| Source | Used for | Access | Licence | Status |
|---|---|---|---|---|
| Elexon IRIS archive, https://archive.data.elexon.co.uk/iris-archive | DISEBSP, MID, WINDFOR, NDF, TSDF, INDGEN, INDDEM, IMBALNGC, MELNGC, LOLPDRM, FUELINST, INDO, ITSDO, FREQ, REMIT, PN, BOALF | Anonymous Azure Blob; tag queries on Dataset, Timestamp and UploadTime (FACT, [IA]); "a carbon copy of every JSON message" (FACT, [IP]) | BMRS licence UNKNOWN; search summaries conflict | Start date, completeness and `UploadTime` semantics UNKNOWN (403 from this sandbox). LOLPDRM is the REST dataset code (FACT, [EX] `datasets_api.py:6226`); the decision record writes "LOLPDM" for IRIS, and the IRIS code is UNKNOWN until Stage 0-A. |
| Elexon Insights REST, https://data.elexon.co.uk/bmrs/api/v1 | Cross-checks; the latest-run price snapshot; prospective settled prices at s + 30 days | No authentication (FACT, [IP]) | As above | `/history` depth UNKNOWN. Migrated history can carry a synthetic `publishTime` (FACT, [EB] IGCPU). |
| Elexon BMU reference, `/reference/bmunits/all` | BMU → fuelType for the PN wind split | "A current list of BM units held by Elexon"; fields `nationalGridBmUnit`, `elexonBmUnit`, `eic`, `fuelType`, `leadPartyName`, `bmUnitType`, `fpnFlag`; no vintage field (FACT, [EX] `reference_api.py:38`, `ReferenceBmUnitData`) | As above | Current snapshot only. Whether historical snapshots exist is UNKNOWN. Covered by the static exception in PIT rule 2. The decision record's "earliest available snapshot" can only be our first capture. |
| ECMWF open data on AWS, `s3://ecmwf-forecasts` (eu-central-1) | F6 | Anonymous. Byte ranges via `.index`, about 1.3–1.4 MB per field per step (FACT, [S3]) | CC BY 4.0 + ECMWF Terms of Use (FACT, [EO] line 732) | Folders from 20230118. `ifs/0p25` from 2024-02-01 (as `0p25/` until 2024-02-28), with 0.4° in parallel until 2025-02-25. 100u/100v/ssrd from 2024-03-06 (FACT, [S3]). |
| NESO Data Portal (CKAN) | F8 only, if verified | Host returned 403 here | NESO Open Data Licence v1.0, OGL-based (search summary only) | UNVERIFIED |
| Own forward recorder | k4 live check; prospective cross-audit; prospective settled prices | IRIS AMQP: free registration, 3-day message TTL, client secrets expire after 2 years (FACT, [IC]). REST polling every 15 min. Runs on an always-on VM, not GitHub cron. | — | Stores raw payload, sha256 and capture_time. Values dated after 2025-02-28 go to the sealed store until P. |
| Pinned GB bank-holiday table | Calendar | Committed to the repo (gov.uk returned 403 here) | — | — |

**Not used:**
- EPEX GB continuous intraday and GB day-ahead auctions (paid);
- ENTSO-E GB and neighbouring series (latest version only; no issue time; INFERENCE, strongly supported);
- Elexon TEMP (§8.10.2);
- Open-Meteo archives and hindcasts; ERA5;
- vendor forecasts. The one exception is an optional prospective Energy Quantified trial arm; the free trial covers the last 30 days only (FACT, [PD] eq-python-client docs).

### 8.13 Baseline models

All SSP/NIV inputs to N1–N6 are first-published values (§8.9 item 2).

| ID | Model | Fitted? | Role |
|---|---|---|---|
| N1 | Persistence: last first-published SSP | No | Floor |
| N2 | Same SP, D-1, local clock time | No | Seasonal naive |
| N3 | Same-SP rolling median, 7 days and 28 days | No | Smoothed rule |
| N4 | Same-SP EWMA, α frozen on warm-up | No | The rule type that won Exp 0: ewma 640.8 MW vs t0 703.8 MW (FACT, [R11] `metrics.csv`) |
| N5 | MID anchor: last known MID + trailing 28-day same-SP median of (SSP − MID) | No | Market-price anchor |
| N6 | NESO incumbent: trailing 28-day conditional median of SSP given sign(latest IMBALNGC_s) × SP block | No | The system operator's own ex-ante signal |
| L | L1-penalised linear quantile regression on z. 19 levels 0.05…0.95, plus 0.01 and 0.99 for tails. One direct h = 2 h model. Arms: I0, B, B+X_f, B+, B+W\*, B-PNtotal. About 150 lines of scikit-learn. | Yes | **Instrument of record** |
| G | LightGBM quantile regression on the identical table and levels. Arms: B and B+X_f. | Yes | Corroboration; must agree in sign with L |
| (opt.) | Equal-weight L+G quantile average | — | Reported only |

- **Bands for N1–N6.** Trailing 28-day empirical residual quantiles per SP block (§8.4), as rolling split-conformal intervals.
- **epftoolbox is not vendored.** Its LICENSE says Apache-2.0 but its README says AGPL-3.0, and it pulls in TensorFlow (FACT, https://raw.githubusercontent.com/jeslago/epftoolbox/master/LICENSE and README.md line 9).

### 8.14 Foundation models

- **Chronos-2 is the only one.**
  - `amazon/chronos-2`, 120M parameters, released 2025-10-20; code licence Apache-2.0 (FACT, [CH] lines 20 and 39, and LICENSE).
  - The weights licence is UNVERIFIED (Hugging Face is blocked here).
- **Setup.** Zero-shot, `cross_learning=False`, pinned revision, reproducibility tolerance 1e-3 £ per quantile.
- **Arms.** I0, B and B+F1\*.
  - The full B enters as past and future covariates. Every future key must also appear in `past_covariates` (FACT, chronos `pipeline.py:468-560`, per [PD]).
  - Origins 00/06/12/18 UTC only.
- **Never used for attribution.** A TSFM covariate ablation confounds "X carries information" with "the model reads X". In the t0 report, 11 of 30 fev known-future tasks got **worse** with covariates (FACT, [T0] lines 885–886).
- **Contamination and the Q2 rule.**
  - **Gate (unchanged).** The champion-vs-Chronos-2 comparison gates only on the post-P prospective window. A margin under 5% is pre-registered as "no evidence that sophistication matters".
  - **Before the checkpoint date.** Confirmation days before the pinned revision's commit date are labelled "contamination not excluded".
  - **Descriptive addition.** Confirmation days after the pinned revision's commit date cannot be in that checkpoint's pretraining (INFERENCE: training data precede release). For the 2025-10-20 release, those days are 2025-10-21 → 2026-08-31, 315 days (computed). The Q2 comparison is **reported** on them but does not gate.
  - **Optional control.** `autogluon/chronos-2-synth` (120M) is listed in the README (FACT, [CH] line 40). That it was trained on synthetic data only is UNVERIFIED (model card blocked). If Stage 0 verifies this, it runs as a contamination-free comparator in the descriptive comparison.
- **Excluded:**
  - t0 (§9.3);
  - TimesFM-3: non-commercial, non-production weights (FACT, https://raw.githubusercontent.com/google-research/timesfm/master/README.md lines 58–64);
  - TimesFM-2.5: its XReg path duplicates L;
  - TabPFN-TS: non-commercial (per [PD]).

### 8.15 Metrics

| Tier | Metric |
|---|---|
| **PRIMARY** | Mean pinball on z over τ = 0.05, 0.10, …, 0.95 (19 levels). Skill_f = 1 − ΣP(B+X_f) / ΣP(B), from pooled sums, with the same learner, the same origins and the same drop set. Inference unit: the daily mean over each target settlement date's SPs. |
| SECONDARY (in the Holm family) | The same metric on raw NIV (MWh), F1 only |
| Reported (non-gating unless a gate names it) | £-scale pinball; median MAE (£); pinball at τ = 0.01 and 0.99. Brier score and reliability for the four events {SSP_s > last known MID; SSP_s ≥ £200; SSP_s < 0; NIV_s > 0}. 80%/90% coverage; Murphy diagram. Skill by information-age band (§8.4), quarter, SP block and regime. Concentration: top 5/10/20 days' share, skill after dropping the 5 best days, pooled skill vs an equal-weight daily sign test. Mediation decomposition; physical-target skill. Rolling 90-day skill. L/G/Chronos-2 spread. Completeness by month and \|NIV\| decile. A count of every emitted p-value or interval, each tagged gating or non-gating. |

### 8.16 Probabilistic evaluation

- **Yes: full predictive distributions are the primary object.**
  - The price is bimodal by system direction and heavy-tailed (INFERENCE from BSC price mechanics).
  - Fundamentals move scale and tails more than the mean (Hirsch & Ziel 2024; search summary only, [PD]).
- **Representation.** 19 quantiles; crossings fixed by sorting. CRPS ≈ 2 × mean pinball. PIT values come from interpolating between quantiles, with flat tails.
- **Calibration.** PIT histograms per 30-day block. They are descriptive only, because PITs are serially dependent.
- **Recalibration.**
  - One rolling split-conformal wrapper (trailing 28 days per SP block), applied identically to every model.
  - **Raw scores are primary.**
  - Recalibrated 80% coverage within [0.75, 0.85] is STRONG gate (k).
- **Threshold events.** Only the four pre-registered ones.
- **Never:** scoring on outcome-defined subsets such as realised spikes (the forecaster's dilemma).
- **Out of scope:** joint or path distributions across SPs. The quantiles are marginal.

### 8.17 Lag-search methodology

- **No target-side lag search.** h is fixed at 2 h, and every covariate is aligned to the target SP s.
- **"Lag" means the revision's reference vintage and window**, drawn from the family grids in §8.10.1 and hashed in the YAML.
- **Stage 1 selection.**
  - Each variant gets a one-sided Newey–West t (L = 7) on the 365 discovery daily differentials of L(B+variant) vs L(B).
  - Family p-value: Bonferroni over the family's declared variant count.
  - The best variant per family is frozen (F1\* for F1).
- **F1 futility.** Uses 19-quantile, weekly-refit L on 26 batch means with t(25). F1 is futile **only if all 6 variants** have a one-sided 95% upper bound below 2.0%.
  - Using the best of 6 makes a false FAIL less likely (INFERENCE).
  - Per variant, the upper bound sits about 0.9–2.0 points above the estimate. Futility therefore fires wrongly under a true 2.5% effect with probability about 0.4–1.6% (INFERENCE: normal approximation, SE ≈ r/√364, with r = 0.10–0.22 from Exp 0 and weak dependence assumed).
- **Reported only.** The reference/lag profile and the release-age profile (skill by time since the last WINDFOR publish), with 14-day moving-block-bootstrap (MBB) bands.
- **No lag claim is ever made.** In simulation, about 33% of true-signal claims named the wrong lag of the correct variable (INFERENCE, [SIM]; the effect size and lag grid are UNKNOWN).

### 8.18 Ablation methodology

| Test | Contrast | Role |
|---|---|---|
| Primary | L(B) vs L(B+X_f), mirrored with G; d_j = daily mean over SPs of P(B) − P(B+X_f) | Gating |
| F2 path | B+F1\*+F2 vs B+F1\* | Screened family (C1 evidence) |
| Leave-one-family-out | Among confirmed families | Redundancy |
| Conditional | Giacomini–White with the 3 regime dummies | Regime claims (Holm over 3) |
| Robustness | B+ (with BOALF) must keep ≥ 1.0% skill | STRONG gate (h) |
| PN-mapping sensitivity | B-PNtotal vs B+X_f on B-PNtotal | Reported; bounds the static-BMU exception |
| Mediation | (1) F1 against B+W\*; (2) the same nested ablation with the first-published FUELINST wind outturn for s as the target | Channel label (§10.6) |
| Encompassing | Regress y on the B and B+X medians, with 14-day-block HAC standard errors | Diagnostic |
| Mechanism check | F1 skill should rise with \|revision\| and with revision freshness, within SP-of-day × month cells | Reported, directional |
| Competitor | Share of in-sample Granger/TE picks that also pass the out-of-sample and placebo gates | Reported |
| **Precondition** | Placebo arms, validity controls, poisoning, truncation-equivalence and vintage-swap tests all pass before **any** statistic is read | INVALID otherwise |

### 8.19 Multiple-testing safeguards

The full protocol is in §10. Summary:

- **Stage 1.**
  - Newey–West t per variant; Bonferroni within each family.
  - Benjamini–Hochberg (BH) at q = 0.10 over F2–F8 (≤ 7 families).
  - F1 is exempt from screening but subject to **futility** (§8.17).
  - Every family carried forward, F1 included, must pass the placebo rule of each type (§8.10.3).
  - At most F1 + 2 screened families go forward.
- **MDE rule before unsealing** (§10.3), recomputed from the actual batch count.
- **Stage 2.**
  - One-sided test on 37 non-overlapping 14-day batch means with t(36), or on n_b batches after exclusions (§8.25).
  - Holm at α = 0.04 over ≤ 4 hypotheses {F1-price, F1-NIV, ≤ 2 screened families on price}.
  - If the Politis–White block length exceeds 14 days, switch to 28-day batches (18 batches, t(17)).
- **Regime claims.** Holm over the 3 regimes at α = 0.05.
- **Extension.** Exactly one pooled confirmation + post-P prospective test at α = 0.01, only for INCONCLUSIVE hypotheses.
- **α budget, stated plainly.** The pre-registered path spends 0.04 + 0.01 = 0.05, which is the whole budget. ~~Any other reuse spends α = 0.005 from the ledger and **raises** the cumulative FWER bound to 0.05 + 0.005k after k reuses. `verdict.json` reports that running bound. It is a disclosed overrun, not an allowance.~~ **[v2 correction: withdrawn. Once graded verdicts or an evidence package have been released, a flat α per reuse does not bound adaptive FWER (SIM: false significance at α = 0.005 reached 40% after 20 reuses and 95% after 50). After the single unseal, any further test on this window is exploratory and uncharged and cannot yield a confirmatory verdict; see the v2 addendum, point 2.]**
- **Deliberately skipped:** knockoffs, Benjamini–Yekutieli, White's Reality Check / SPA / Romano–Wolf, MCS over candidates, PBO.

### 8.20 Regime analysis

**Regimes.** All three are defined only from information known at t. Thresholds are set on discovery data and then frozen.

| ID | Regime | Definition |
|---|---|---|
| R1 | Wind share | Tercile of latest WINDFOR[s] / latest TSDF[s] |
| R2 | Large revision | \|F1\*\| > discovery 80th percentile |
| R3 | Evening peak | Target SP starts 16:00–19:30 Europe/London (= SP block 5) |

**Test.** A Giacomini–White conditional test on the daily or batch differentials, with Holm correction over the 3 regimes. Rolling 90-day skill and a quarterly table are descriptive only.

**Pre-registered structural dates.** Plot markers only; never used to cut samples.

| Date | Event | Status |
|---|---|---|
| 2024-02-01 | ECMWF 0.25° grid | FACT, [S3] |
| 2024-11-12 | IFS 49r1 | FACT, [PD] |
| 2026-05-12 | IFS 50r1 and stream rename | FACT, [S3] |
| August–October 2025 | IRIS re-platform | FACT, [IC] |
| October 2024 | ESO → NESO | INFERENCE |
| About December 2023 | Open Balancing Platform | INFERENCE |
| 2023-06 → 2026-08 | Every BSC modification that changed price derivation in this period | UNKNOWN; must be enumerated from the modification register before discovery |

**Forbidden:** regimes defined from realised prices, NIV or forecast errors; thresholds set after results; regimes added after unsealing.

### 8.21 Economic sanity check

One frozen mechanical rule, secondary only. The full specification, including the decided open items, is in §12.2.

- **Position.** 1 MW notional, i.e. 0.5 MWh per SP, decided at t.
- **Signal.** q50 from L. Long if q50(SSP_s) − MID_ref > +£5/MWh, short if it is < −£5/MWh, otherwise flat.
- **P&L.** position × (settled SSP_s − P_exec) − £1.5/MWh × \|position\|.
- **Execution price, two variants.** A: P_exec = realised MID_s (optimistic). B: P_exec = MID_ref (stale, but known at t).

### 8.22 Computational requirements

All figures are INFERENCE: projections, not measurements.

| Item | Estimate |
|---|---|
| IRIS ingest | About 1.3–2M blobs for the core datasets. FREQ alone is about 720/day, which follows from "every 2 minutes" (FACT, [EB]). PN and BOALF could add several million more. Roughly 10–50 GB of JSON. |
| ECMWF ingest | 2 fields × ~8 three-hourly steps × 4 runs × ~910 days × ~1.35 MB ≈ 80–120 GB of transfer; < 2 GB after cropping to GB |
| Stage 1 screening (L, 5 quantiles, monthly refits, 29 arms = 27 variants + B + I0) | 10–25 CPU-h |
| F1 (6 variants) + finalists + G + placebos (137 draws per carried family: 1 + 37 + 99) | 30–60 CPU-h. This is now conservative: the decision record assumed ≥ 297 draws per family. |
| Stage 2 (≤ 5 arms × 2 learners × 19 quantiles, weekly refits) | 15–30 CPU-h |
| Chronos-2 (3 arms × ~4,000 origins × ~5 s) | 15–20 CPU-h. Projected from Exp 0's 0.19 s per univariate t0 origin (FACT, [PD] `run6_log.txt` timestamps); the scaling with covariates is INFERENCE. |
| **Total** | About 70–150 CPU-h, no GPU; 1–2 days on one 16-core workstation |

**Where it runs.** Ingest needs a host that can reach Elexon. The recorder needs an always-on VM. Offline tests run in GitHub Actions on synthetic IRIS-shaped fixtures (6 h job limit; FACT, [PD]).

### 8.23 Expected API and data costs

| Item | Cost |
|---|---|
| Data licences | **£0**. The Elexon API, IRIS archive, ECMWF CC BY 4.0 data and NESO data are free (FACT, access terms). Whether the BMRS licence permits commercial use is UNKNOWN; that blocks only the PRODUCT path. |
| Transfer | About 0.1–0.2 TB; a few GB retained |
| Recorder VM | About £5–20/month (INFERENCE) |
| Compute | About £0–50 (INFERENCE) |
| Not bought | EPEX GB continuous and day-ahead data (quote-only; a search summary gives €3,360/month for the continuous read-only API, internal use); vendor NIV forecasts (quote-only) |
| Optional | Energy Quantified free trial (last 30 days only) for a prospective professional-baseline arm |
| Labour (dominant) | Stage 0 about 1–2 weeks elapsed (k4 needs ≥ 14 days of capture); build 4–6 engineer-weeks; about 10 buyer calls of 45 min |

### 8.24 Success criteria

All criteria are computed by committed code, and the verdict engine writes `verdict.json`.
- **Primary metric:** z-pinball skill of B+X over B, same learner.
- **SESOI = 2.0%.**
- **Notation:** ŝ = L point skill; UB = one-sided 95% upper bound (batch means); p = Holm-adjusted one-sided p.

**Two claims, with one verdict each.** The Holm family is shared across both claims.

| Claim | Hypotheses | Rule |
|---|---|---|
| **C1: the §4D wind-revision thesis** | F1-price (decides C1); F1-NIV; F2 (conditional on F1\*) | Only F1-price can take C1 above INTERESTING. F1-NIV or F2 alone can lift C1 to INTERESTING at most, labelled "volume only" or "path only". `verdict.json` then also records the F1-price outcome, e.g. "price-level revision thesis: FAIL". |
| **C2: public information beyond B** | F3–F8. F2 moves here if F1 was futile at discovery. | F3–F6 and F8 are labelled "revision information of another kind". F7 is labelled "information, not revisions". C2 can reach STRONG through gate (a)'s alternative route. |

**Hypothesis-level outcomes (Stage 2)**

| Outcome | Condition |
|---|---|
| STRONG-provisional | p ≤ 0.04, ŝ ≥ 2.0% and gates (b)–(l) all pass |
| INTERESTING | p ≤ 0.04, UB ≥ 2.0%, and either ŝ ∈ [0.5%, 2.0%) or at least one of gates (c)–(k) fails. Also any result whose sign flips when the top 10 days are dropped. |
| INTERESTING-below-SESOI | p ≤ 0.04, UB < 2.0% and ŝ ≥ 0.5%. The SESOI-level claim FAILS; a smaller effect is detected. There is no STRONG path. |
| INCONCLUSIVE | No Holm rejection and UB ≥ 2.0%. The only permitted next step is the extension. |
| FAIL | No Holm rejection and UB < 2.0%; or p ≤ 0.04 with ŝ < 0.5% (negligible) |
| FAIL-BY-POWER | Still no rejection after the single pooled extension at α = 0.01. GB is then not retested, and no new families are mined against these windows. |

**Precedence within a claim:** INVALID > STRONG-final > STRONG-provisional > INTERESTING > INTERESTING-below-SESOI > INCONCLUSIVE > FAIL-BY-POWER > FAIL. An INVALID anywhere voids both claims.

**Discovery exits (Stage 1)**
- **F1 futile** (§8.17) → C1 = FAIL, and the confirmation window is never unsealed for C1.
- **F1 futile and no F2–F8 family passes BH q = 0.10 plus the placebo rule** → both claims FAIL, and the confirmation window stays sealed.

**Regime route (exploratory).** It applies only when F1-price has no Stage 2 rejection. F1 must be significant in exactly one regime with all of:
- GW Holm-adjusted p ≤ 0.05 over the 3 regimes;
- the regime covers ≥ 20% of SPs;
- regime skill ≥ 3.0%.

The result is labelled "INTERESTING-exploratory (α outside the confirmatory 0.05)".

**STRONG gates**
- **(a)** p ≤ 0.04 on 37 batches (or n_b after exclusions). For C2, a family among F3–F6 or F8 may carry this gate.
- **(b)** L skill ≥ 2.0%.
- **(c)** G skill ≥ 1.0%, same sign.
- **(d)** Skill > 0 in ≥ 4 of the 6 quarters defined in §8.6.
- **(e)** Skill ≥ 1.0% after dropping the 5 best days, and the top 10 days carry < 50% of the gain.
- **(f)** £-scale skill > 0 with one-sided unadjusted p < 0.10.
- **(g)** Skill ≥ 0 when scored against the latest-run SSP snapshot (§8.2; its run-type mix is uncontrolled).
- **(h)** Skill ≥ 1.0% against B+.
- **(i)** Placebo rule of every type passed (§8.10.3).
- **(j)** The best B+X model is at least as good as N1–N6, L(B) and G(B).
- **(k)** Recalibrated 80% coverage in [0.75, 0.85].
- **(l)** Zero `known_at`, PIT, poisoning or mutation failures (any failure is INVALID).

**STRONG-final**
- Requires STRONG-provisional **plus** ≥ 90 days after P with F1 skill ≥ 0 for both L and G.
- If the extension was used, pooled p ≤ 0.01 is also required.
- The Chronos-2 Q2 comparison is evaluated here.
- **Operating characteristics (INFERENCE):** normal approximation, SE ≈ r/√90 with r = 0.10–0.22, weak dependence assumed.
  - Under the null, P(L ≥ 0) = 0.50, and requiring G to agree cuts this to 0.25–0.50 depending on the L–G correlation.
  - Under a true 2.5% effect, P(L ≥ 0) ≈ 0.86–0.99; under a true 1.0% effect, ≈ 0.67–0.83.
  - This is a replication-consistency check applied after STRONG-provisional, not an independent test.
- The result carries the mechanism label (§10.6). Only "market channel" supports the brief's §4D claim.

**PRODUCT SIGNAL** requires all of:
- STRONG-final on C1, or on C2 with a pre-registered revision family. Any "revisions" claim also needs the market-channel label.
- The economic gates in §12.5.
- Buyer calls:
  - ≥ 3 of 10 structured calls name an existing budget line of ≥ £10k/yr for independent, vintage-correct feed or signal validation, and confirm they run no equivalent point-in-time ablation in-house;
  - ≥ 1 commits to a paid pilot, or to sharing baseline forecasts under NDA.
- F1 skill ≥ 1.0% (descriptive) after adding the latest vendor wind instance level (EQ or Volue trial) to B, on ≥ 30 post-P days.
- The BMRS licence permits the commercial use and any redistribution of derived vintage evidence.

**INVALID RUN (no verdict)** if any of the following occurs:
- a `known_at` violation;
- any poisoning, truncation or vintage-swap change;
- oracle-leak skill < 20%;
- the planted 10% X is not recovered;
- the +1-cycle arm leaves forecasts unchanged, or fails to raise under the contract;
- a mutation or planted-bug test fails to fail;
- L(B) fails K-competence. This triggers the repair round in §8.25; it is not a thesis result.

### 8.25 Kill criteria

**Stage 0 (before approval to build): k1–k7.** Metadata only, plus the capture client and the licence read.

| ID | Check | Threshold | Action on fail |
|---|---|---|---|
| k1 | Coverage, in the units defined in the table below | ≥ 95% of expected units in every month from D0 to 2026-08. WINDFOR also needs ≥ 6 publishes on ≥ 95% of days. | D0 rule (§8.5). D0 after 2024-02-11 → hybrid confirmation. D0 after 2025-03-01 → historical design killed (forward capture for ≥ 12 months, or STOP). |
| k2 | First price timing | First DISEBSP `UploadTime` ≤ SP end + 60 min for ≥ 95% of SPs | Before D0: moves D0. After D0: exclusion rule. |
| k3 | `UploadTime` is genuine | Blob `x-ms-creation-time` vs the tag within 10 min for ≥ 99% of sampled blobs. `UploadTime − publishTime` ∈ [−1, 30] min for ≥ 99% of WINDFOR/TSDF/INDDEM/MELNGC/IMBALNGC vintages. ≤ 1% of blobs with a bulk-upload signature (≥ 1,000 blobs within 60 s whose `publishTime`s span > 24 h). | Exclusion rule |
| k4 | Live check | Over 14 days of our own capture, first-seen − `UploadTime` ≤ 5 min for ≥ 99% of messages | **Historical design killed** |
| k5 | Continuity across the August–October 2025 re-platform | 2025-07 … 2025-11 each ≥ 95% complete in k1 units. Median lag shifts < 5 min vs 2025-06, per dataset. Lag = `UploadTime − publishTime` for forecasts; `UploadTime − SP end` for DISEBSP. | Exclusion rule |
| k6 | F1 feasibility | ≥ 2 distinct WINDFOR vintages between the reference and t on ≥ 90% of origins | C1 cannot be tested → do not build GB-IMB-2H-H; run the ERCOT probe |
| k7 | Licence | The BMRS licence permits the research use | STOP |

**k1 expected units** (declared before any month is counted):

| Dataset | Unit counted | Expected per day |
|---|---|---|
| DISEBSP | SPs with ≥ 1 message | Every SP of the settlement day (46, 48 or 50) |
| MID | (provider, SP) pairs with ≥ 1 record, for APXMIDP and N2EXMIDP | 2 × SPs of the settlement day |
| WINDFOR | Distinct `publishTime` per UTC day | 8 |
| MELNGC, INDDEM, LOLPDRM | Distinct `publishTime` per UTC day | 48 |
| FUELINST | Distinct 5-min `startTime` per UTC day | 288 |
| TSDF, NDF, IMBALNGC, INDGEN | Distinct `publishTime` per UTC day | The modal daily count in the dataset's reference month (its first full month with ≥ 1 blob every day), fixed before later months are counted; floor 1 |
| FREQ, PN, BOALF, REMIT, INDO/ITSDO | — | Reported, not gating |

**Build gate (after approval, before any real data is modelled)**

| ID | Check | Action on fail |
|---|---|---|
| k8 | Poisoning, truncation, vintage-swap, mutation and validity-control tests pass on synthetic fixtures | No real data is modelled |

**Exclusion rule for k2, k3 and k5 failures after D0**
1. A failing (dataset, month) for any B or F1 dataset excludes that month from every arm. A failure in an X-only dataset sets that family missing for the month (NaN + indicator); the units stay in.
2. Batches are rebuilt as 14-day blocks over the remaining days in chronological order. No batch straddles an excluded month; incomplete blocks become sensitivity only. n_b is recomputed; the test uses t(n_b − 1), and the MDE is recomputed.
3. If discovery falls below 273 days, apply the D0-slip rule (§8.5). If excluded days exceed **15%** of the 518 confirmation batch days, switch to the hybrid design: the historical remainder plus post-P prospective days until ≥ 365 days.
4. Among the Stage 0 checks, only k1 (D0 after 2025-03-01), k4, k6 and k7 kill the design. k2, k3 and k5 only exclude months.

**Later kills**
- **K-competence.** In discovery, L(B) must beat the best of N1–N6 by ≥ 5% z-pinball. If it does not:
  - One ledgered repair round is allowed, using only these pre-declared repairs:
    - (R-a) N1–N6 point predictions added to B as features;
    - (R-b) SP block × sign(latest IMBALNGC) and SP block × sign(last NIV) interactions;
    - (R-c) SP block × day-type dummies in place of the harmonics;
    - (R-d) a widened LASSO penalty grid, or 14-day CV folds.
  - If L(B) still fails, STOP with "no competent public baseline".
  - Repairs touch discovery only. They can overfit B to discovery, which makes the Stage 1 screens conservative, but cannot inflate confirmatory false positives (INFERENCE).
- **K-target-vintage.** If first-published and latest-run NIV disagree in sign on more than 5% of discovery SPs, re-examine the target by a written rule before sealing.
- **K-invalid.** As defined under INVALID RUN in §8.24.
- **K-power.** The MDE rule (§10.3).
- **K-thesis.** A FAIL ends this hypothesis line on GB. ~~New candidate pools against the same holdout cost α = 0.005 each, and are disclosed as FWER overrun (§8.19).~~ **[v2: new candidate pools on the same holdout are exploratory only. Confirmation needs a fresh vault or post-freeze prospective data (G1–G3, v2 addendum).]**
- **K-budget.** More than 6 engineer-weeks before the first discovery result, more than 150 CPU-h, or more than 1 TB transferred: drop F6, F8, and PN if it is optional.
- **K-licence.** If the licence blocks commercial use, keep the science and kill the product path.

## 9. Model tournament

### 9.1 What the tournament is for

It answers two questions, and they must not be merged.

| Question | Answered by | Never answered by |
|---|---|---|
| **Q1. Does X add information?** (level 3 of §11.1) | Nested L(B) vs L(B+X) on identical origins and drop sets, with G(B) vs G(B+X) required to agree in sign | Any TSFM ablation, SHAP or feature importance, or in-sample screens (level 2) |
| **Q2. Does sophistication beat competent conventional methods?** | One pre-declared comparison: Chronos-2 vs the frozen champion from {L, G}, on the 00/06/12/18 UTC subset. It gates only on the post-P prospective window; post-checkpoint confirmation days are descriptive (§8.14). | Comparisons against naive rules or untuned AutoML |

### 9.2 Brief §11 candidates → decision

| Brief candidate | Decision | Implemented as | Reason |
|---|---|---|---|
| Persistence | Required | N1 | The floor. At h = 2 h the last known first-published price is probably about 2.5 h old (INFERENCE, conditional on the k2 result: it assumes the first publication lands about 30–45 min after SP end). Weak but mandatory. |
| Seasonal naive | Required | N2 (same SP, D-1, local clock); D-7 enters B | Civil-time price seasonality needs local-clock lags. Exp 0's UTC-lag convention was solar-specific (FACT, [PD] Exp 0 digest). |
| Rolling mean/median | Required | N3 (7- and 28-day medians), N4 (EWMA) | Exp 0's winners were smoothed same-slot rules: ewma 640.8 MW and blend_50 645.6 MW vs t0 703.8 MW (FACT, [R11] `metrics.csv`). |
| Domain incumbents | Required (added) | N5 MID anchor; N6 NESO IMBALNGC-conditional rule | Public market and system-operator expectations are the real bar for "beyond B". |
| Autoregression | Not separate | L on I0 | An AR model is the I0 arm of L. |
| Linear model | Required: **instrument of record** | L (L1 linear quantile regression on z) | Engineered linear EPF models capture most of the gain (§9.4). Transparent nested ablation. |
| Gradient boosting | Required: corroboration | G (LightGBM quantile, identical features) | Catches non-linear revision effects that L misses. The sign-agreement requirement blocks learner-specific artefacts. |
| t0 | **Excluded** | — | §9.3 |
| One alternative TSFM | Optional; Q2 only | Chronos-2 (optionally the chronos-2-synth control) | §8.14 |

### 9.3 Is t0 relevant? No.

| Reason | Evidence |
|---|---|
| It lost to smoothed baselines under the stronger benchmark | t0 vs blend_50: −9.0% [−13.8, −4.3]; won 150 days, lost 213; sign-test p = 0.0011 (FACT, [R11] `pairwise.csv` row 1). Rank 7 of 9 (FACT, [R11] `ranking.csv`). |
| Tails cannot be scored | t0-alpha's released package clamps requested 0.01/0.99 quantiles to empirical coverage of 0.109/0.893 (FACT, [T0] lines 1200–1206). Imbalance-price tails are the economically relevant part. |
| API constraints | `group_ids` cannot be combined with `future_covariates` (FACT, tfc-t0 0.3.2 `t0/data.py:109`, per [PD]). tfc-t0 0.5.0 renames the quantile argument, which breaks Exp 0's adapter at `solarbench/forecasters.py:422-424` (FACT, [PD] `weights_wf.json`; not re-checked this session). |
| Its covariate evidence is not evidence of incremental information | The epf_de −51% compares the same checkpoint with and without covariates, over 20 windows of epftoolbox-era data. 11 of 30 known-future tasks got worse (FACT, [T0] lines 880–886; [PD] `fevb_tasks.yaml`). |
| No imbalance or intraday evidence | Absent from the t0 report (FACT, grep over [T0]). |
| Forecast skill ≠ money, even in its own case study | ERCOT: t0-alpha MAE 14.55 vs 23.57 for the lagged baseline; profit $15.00M vs $14.11M; an always-short control with no forecast earned $11.82M (FACT, [T0] lines 1538–1547). |

Neither t0-alpha nor t0-beta gets a slot, optional or otherwise. Any future inclusion would be a pre-registration amendment charged to the ledger.

### 9.4 Prior evidence that sets expectations

| Evidence | Numbers | Label |
|---|---|---|
| Engineered linear vs AR vs deep (epftoolbox Nord Pool, 2-year test) | MAE: AR 2.26, OLS ARX 2.01, **LEAR 1.74** (rMAE 0.55), DNN 1.68 (GW p = 0.087 vs LEAR), NBEATSx-G 1.58. Information and lag structure are worth tens of percent; sophistication, single digits. | FACT, https://raw.githubusercontent.com/cchallu/nbeatsx/main/README.md and `main_results.ipynb`, per [PD] |
| An untuned GBM is a strawman | fev-bench EPF geometric-mean scaled quantile loss: t0-beta 0.452, Chronos-2 0.468, TimesFM-3 0.469, CatBoost 0.805, LightGBM 0.825, seasonal naive 1.094. On PJM, LightGBM is worse than seasonal naive (0.598 vs 0.515). | FACT, https://raw.githubusercontent.com/autogluon/fev/main/benchmarks/fev_bench/results/, per [PD] |
| TSFM on imbalance | Chronos-2 had about 10% higher MAE than an ML ensemble on Belgian imbalance prices | Search summary only (arXiv 2605.17045), [PD] |

**Pre-registered implications**
- G's hyperparameters are tuned once on the B-only arm (§8.7), so G is not a strawman.
- A Chronos-2 margin < 5% counts as "no evidence that sophistication matters".
- The Q2 prior is "no" (INFERENCE).

### 9.5 Determinism and reproducibility

| Component | Setting | Evidence |
|---|---|---|
| G | `deterministic=true`, `force_row_wise=true`, seed 0, pinned version | Stable only for the same data, parameters, version and system (FACT, https://raw.githubusercontent.com/microsoft/LightGBM/master/docs/Parameters.rst lines 285–297) |
| L | Pinned scikit-learn; single-threaded BLAS if bitwise equality is required | INFERENCE |
| Chronos-2 | `cross_learning=False`, pinned revision, tolerance 1e-3 £ per quantile | Cross-learning makes results depend on batch size (FACT, chronos `pipeline.py`, per [PD]). Exp 0's t0 reproduced only to ≤ 0.003 MW per point (FACT, `README.md:50-59`). |
| All | Cache key per §8.7; reproduction never reads the cache | Exp 0's cache key excluded code identity (FACT, `run_benchmark.py:187-203`) |

### 9.6 What the tournament cannot tell us

- **Performance against a professional baseline.** B lacks the live intraday tape, the BM stack beyond BOALF, vendor forecasts, licensed NWP, neighbouring prices and ATC.
- **Memorisation.** Whether Chronos-2's performance on confirmation days before the checkpoint reflects memorisation is UNKNOWN.
- **Other markets.** Nothing here speaks to markets other than GB cash-out.

## 10. Predictive-information methodology

### 10.1 The question, stated as a test

For family f, learner ℓ ∈ {L, G} and settlement date j:

d_j^f = mean over the SPs s of date j of [P_ℓ(B)(s) − P_ℓ(B+X_f)(s)]

Here P is the 19-level pinball loss on z, with the same learner, the same origins and the same drop set.

- **Confirmatory hypothesis:** E[d_j^f] > 0 over the sealed confirmation window, with skill_f = 1 − ΣP(B+X_f)/ΣP(B) ≥ SESOI = 2.0%.
- **Only level 3 of the ladder in §11.1 is tested.**
  - Levels 1 and 2 (correlation, lead/lag association) are neither sufficient nor claimed.
  - Level 4 (mechanism) is supported only by pre-registered mediation and directional checks.
  - Level 5 (causality) is never claimed.

### 10.2 The protocol

| Stage | Window | What happens | Exit |
|---|---|---|---|
| **0: PIT audit** | Metadata, D0 → 2026-09 | k1–k7 (§8.25). Confirmation-window payloads parsed for key fields only. | Design kill, D0 shift, month exclusions, or pass → user approval |
| **Build gate** | Synthetic fixtures | k8 | No real data until it passes |
| **Pre-registration (date P)** | — | Commit and tag a SHA-256-hashed YAML containing: target; h; windows; B; F1–F8 grids; learners; losses; SESOI = 2.0%; c; α/q/K; regimes; placebo rules; the economic rule; the dataset → `known_at` rule table; the k1 expected counts | Loader seal active; prospective clock starts at P + 1 |
| **1: Discovery** | 2024-03-01 → 2025-02-28 (365 days, 26 batches) | Rolling-origin nested ablations; NW t per variant; Bonferroni within family; BH over F2–F8; F1 futility; placebo rules; validity controls; freeze at most F1\* + 2 specs | FAIL (seal kept) or proceed |
| **MDE gate** | Discovery SE | §10.3 | Cut the Holm family, defer, or unseal |
| **2: Confirmation (once)** | 2025-04-01 → 2026-08-31 (37 batches, or n_b after exclusions) | Frozen specs; batch-means t(n_b − 1); Holm α = 0.04 over ≤ 4; gates (b)–(l) | Per-claim verdicts (§8.24) |
| **Post-design, pre-freeze** | 2026-09-01 → P | Reported once, descriptively | None |
| **3: Prospective** | From max(2026-10-01, P + 1); ≥ 90 days needed | STRONG-final; Q2 gate; the single pooled extension at α = 0.01 for INCONCLUSIVE hypotheses | STRONG-final or FAIL-BY-POWER |

### 10.3 Statistics and defaults

| Setting | Default | Failure mode it prevents | Evidence |
|---|---|---|---|
| Inference unit | Settlement-date mean differential; days are never split | Treating SPs as independent | In [SIM], an iid t on hourly differentials gave 74.7% false positives at nominal 5%, and HAC with h−1 lags gave 51.9% (INFERENCE, unpersisted; the dependence model and n are UNKNOWN) |
| Stage 1 per variant | One-sided Newey–West t, L = 7, on 365 daily differentials | — | — |
| Within family | Bonferroni over the declared variant count (1–6) | Picking the lucky reference vintage | About 33% wrong-lag rate (INFERENCE, [SIM]) |
| Across families | BH at q = 0.10 over F2–F8 | Screening noise | BH is valid under positive dependence for one-sided tests (INFERENCE, recalled from Benjamini & Yekutieli 2001; statsmodels `multitest.py` docstrings, FACT per [PD]) |
| F1 | Exempt from screening. Futile only if all 6 variants have UB < 2.0% (19 quantiles, weekly refits, 26 batch means) | Burying the primary hypothesis in a screen | False-futility probability ≈ 0.4–1.6% per variant under a true 2.5% effect (INFERENCE, §8.17) |
| Placebo rule | Per type: 364-day shift (1 draw, must beat it); 37 circular shifts (must beat all; rank p = 1/38); ≥ 99 within-cell block shuffles (rank p ≤ 0.05). Same pipeline as the compared statistic. | Seasonal proxies; pipeline artefacts | In [SIM], a pure seasonal proxy scored +1.18% against a no-calendar baseline, a random circular-shift placebo +0.36% and a wrong-year placebo +1.23%; a calendar baseline removed the effect (−0.31%) (INFERENCE, unpersisted) |
| K | F1 + ≤ 2 screened | Holdout exhaustion | — |
| MDE rule | MDE_80 from the discovery SE, scaled to n_b confirmation batches. Expected ≈ 0.12–0.14 × r, where r = sd(daily differential) / mean(daily B loss). If > 3.0%, cut the Holm family to {F1-price}. If still > 3.0%, defer Stage 2 until confirmation + post-P prospective ≥ 700 days. | Unsealing an unpowered test | (t₀.₉₆,₃₆ + t₀.₈₀,₃₆)/√518 = (1.802 + 0.852)/22.76 = 0.117; with α = 0.01, 0.144 (computed). With Exp 0's r = 0.10–0.22 this gives MDE ≈ 1.2–3.2% (INFERENCE; assumes weakly dependent daily differentials, which is UNKNOWN for imbalance prices). |
| Stage 2 test | One-sided, non-overlapping 14-day batch means, t(n_b − 1) (37 batches → t(36)) | Dependence | In [SIM], size was 5.3–6.5% at nominal 5%, vs 7–10% for a 7-day MBB (INFERENCE, unpersisted) |
| Stage 2 multiplicity | Holm α = 0.04 over ≤ 4 hypotheses {F1-price, F1-NIV, ≤ 2 screened} | Several shots at confirmation | — |
| Block-length switch | Politis–White > 14 days → 28-day batches (18 batches, t(17)) | Long-memory regimes | Implemented in `arch.bootstrap.optimal_block_length` (FACT, https://raw.githubusercontent.com/bashtage/arch/main/arch/bootstrap/base.py lines 126–200, per [PD]) |
| Extension | Exactly one pooled confirmation + post-P prospective test at α = 0.01 | Optional stopping | — |
| Reuse | ~~α = 0.005 per reuse from the ledger, disclosed as FWER overrun (§8.19)~~ **[v2: no confirmatory reuse; exploratory only, ledgered as such]** | Silent holdout reuse by humans | In [SIM], 10 unledgered reuses took FWER from 1% to 19%; ledgered spending gave 2.5% (INFERENCE, unpersisted) |
| Sensitivities (never gating) | MBB with 7/14/28-day blocks, B = 10,000; NW with L = 7 and L ≈ 1.3√n; the 10 leftover days; uniform 5-min margin; B-PNtotal | Block-choice and vintage fragility | Exp 0's bootstrap used B = 2,000, so each Bonferroni tail rested on about 2.6 draws (FACT, [PD] Exp 0 digest) |
| Emitted-statistic census | Every p-value or interval is tagged gating or non-gating, and the count is asserted | Uncounted comparisons | Exp 0 emitted about 44 CI-bearing comparisons against a stated family of 19–20, and applied Holm only in prose (FACT, [R11] `ranking.csv` + `pairwise.csv`; grep over `*.py`) |

**[SIM] parameters known from the result statements only:**
- 2,000 candidates in the global-null scan;
- 100 global-null protocol runs;
- 10 reuse rounds;
- a true effect of 2.5%;
- a 1-year confirmation window;
- hourly differentials with HAC at h−1 lags;
- a 7-day MBB comparator.

Everything else is UNKNOWN until P-SIM is done.

**Deliberately skipped:**
- knockoffs (they assume iid rows);
- Benjamini–Yekutieli;
- White's Reality Check / SPA / Romano–Wolf;
- MCS over candidates;
- PBO.

A sealed, single-use holdout already makes FWER independent of how many candidates were screened (§10.8).

### 10.4 Lag search

- **What "lag" means.** The reference vintage or window of a revision, not a target-side shift.
- **Where it is searched.** Only over the declared variants (§8.10.1), in discovery, with L at 5 quantiles (F1 at the full specification), with Bonferroni within family. The best variant is frozen.
- **What is published.** The profile across variants and the release-age profile, with 14-day MBB bands, as **descriptive only** (level 2 at most).
- **Why.** At realistic effect sizes, about 33% of true-signal claims pick the wrong lag of the correct variable (INFERENCE, [SIM], unpersisted).

### 10.5 Ablations

The table is in §8.18. Each ablation's role:
- **Nested primary:** carries the claim.
- **F2 path test:** the brief's §4D "path beyond endpoints". It is part of C1, conditional on F1\*.
- **Leave-one-family-out:** tests redundancy between families.
- **GW conditional test:** the only route to a regime claim.
- **B+:** guards against an artefact from missing BM state.
- **B-PNtotal:** bounds the static BMU-mapping exception.
- **Encompassing regression:** checks whether X's forecast carries weight beyond B's forecast, not merely a lower loss.

### 10.6 Separating forecast combination from a market channel

Because B+F1 ≡ B+L_ref (§8.9), an F1 gain can arise purely because NESO's latest wind forecast can be improved by averaging it with an older vintage. That would be a physical effect, with no positioning effect at all (INFERENCE).

The pre-registered decomposition is:

| Arm | Reading |
|---|---|
| F1 skill on the **physical target** (first-published FUELINST wind outturn) | Does F1 predict wind? |
| B vs B+W\* | Price information in the best all-vintage wind prediction |
| B+W\* vs B+W\*+F1 | Price information in F1 beyond that wind prediction |

- **Label B, "market channel":** F1 skill against B+W\* ≥ 1.0% with one-sided p < 0.10.
- **Otherwise label A, "physical / forecast-combination channel".**
- The label is applied, not gated. Only label B supports the §4D claim that the revision itself carries market-moving information.
- Even label B is level 3 conditional on B+W\*. It is consistent with level 4 but does not show under-reaction, mispricing or causality (level 5).

### 10.7 Stability and decay

| Check | Rule | Gating? |
|---|---|---|
| Quarterly sign | Skill > 0 in ≥ 4 of the 6 quarters (Q3-2026 partial; March 2025 leftover days excluded) | Gate (d) |
| Concentration | Skill ≥ 1.0% after dropping the 5 best days; top 10 days < 50% of the gain; a sign flip when the top 10 days are dropped caps the result at INTERESTING | Gate (e) |
| Scale and vintage | £ skill > 0 (p < 0.10); skill ≥ 0 against the latest-run price | Gates (f), (g) |
| Prospective replication | ≥ 90 days after P; skill ≥ 0 for L and G. Pass probability ≤ 0.5 under the null and ≈ 0.86–0.99 under a true 2.5% effect (INFERENCE, §8.24) | STRONG-final |
| Rolling 90-day skill | Signal-decay monitor, with structural dates marked | Descriptive |
| Information age | Skill by schedule-derived WINDFOR bands and DISEBSP terciles (§8.4) | Descriptive, mandatory |

**Precedent** (FACT, [R11] `concentration.csv`): in Exp 0 the top 10 days carried 77.4% of t0's net gain over prev_day, and skill was only +1.4% without them.

### 10.8 Why mining thousands of covariates cannot trivially produce fake discoveries

**The guarantee.** Suppose the confirmation window stays untouched until the specifications are frozen, and is then used once. Then:

P(any false confirmatory claim) ≤ P(Holm rejects ≥ 1 true null among ≤ 4) ≤ α = 0.04

This holds whatever the number M of candidates screened in discovery (INFERENCE, standard sample-splitting argument).

**Simulation evidence** (INFERENCE, [SIM], unpersisted; to be reproduced under P-SIM):
- In one global-null run with M = 2,000 candidates, the naive in-sample scan gave 84 hits at \|t\| > 1.96 and 5 at \|t\| > 3 (max 3.69). BH, BY, Bonferroni and a max-t block bootstrap all gave 0 hits. The top 3 failed confirmation (skill −0.53%, −0.17%, +0.04%).
- The full protocol over 100 global-null runs produced 0 false claims.

**What the guarantee depends on, and how each dependency is enforced:**

| Condition | Enforcement |
|---|---|
| Confirmation not seen before freezing | Loader hash gate; metadata-only Stage 0 parser; hash-chained ledger; the recorder's pre-P values in the sealed store |
| Used once | Unsealing git tag; the verdict engine refuses a second **confirmatory** computation ~~without a ledgered α spend (0.005, disclosed as overrun)~~ **[v2: unconditionally]** |
| Claims per family, not per lag or per regime | ≤ 8 families, 27 declared variants; lag profile descriptive; ≤ 3 regimes under Holm |
| No outcome-chosen subsets | Only regimes in the YAML hash are accepted; masks built from Y or NIV fail a test |
| Every statistic counted | Emitted-statistic census |

**What the holdout does not protect against.** A bias present in both windows passes a holdout just as a real signal does. Examples: leakage, a weak baseline, a seasonal proxy, a target-vintage artefact, stale incumbent features. These are handled separately:

| Bias | Guard |
|---|---|
| Leakage | `known_at` contract, truncation equivalence, poisoning, mutation tests, high-power validity controls (§8.11) |
| Weak or stale baseline | B includes the latest levels, live PN, FREQ and outturns; B+ gate (h); K-competence (≥ 5% over N1–N6, one bounded repair round); information-age bands |
| Seasonal or trend proxy | Phase-preserving placebos (364-day shift, whole-week circular shifts, within-cell block shuffle); calendar terms in B |
| Target-vintage artefact | Gate (g) (latest-run price); K-target-vintage (> 5% NIV sign flips); first-published lags in B |
| Forecast combination presented as market information | Mediation label (§10.6) |
| Post-design data treated as prospective | The prospective clock starts at P + 1; 2026-09-01 → P is sealed and descriptive |

**The honest trade-off.** Scaling M from 27 to thousands does not raise the false-claim rate. What it does is lower the chance that a true 1–3% family survives: the per-family screening bars rise, and each sealed market-year supports only about 3 confirmatory families. In [SIM], a true 2.5% effect ranked in the top 3 in discovery 93% of the time but was confirmed only 13–14% of the time with a 1-year confirmation window (INFERENCE, unpersisted). Mining at scale produces fewer discoveries, not fake ones.

The competitor arm makes this measurable. It reports what share of in-sample Granger/TE picks (level 2) survive the out-of-sample, placebo-gated test (level 3). That share is the empirical value of point-in-time out-of-sample discipline over commoditised in-sample screens.

## 11. Explainability / evidence

### 11.1 The five-way ladder, applied

| Level | Meaning here | Statistic in Exp 1 | Can Exp 1 claim it? | Permitted wording | Forbidden wording |
|---|---|---|---|---|---|
| 1. Correlation | Contemporaneous or unconditional co-movement of X and Y | None gating | No | — | "X is linked to the imbalance price" |
| 2. Lead/lag association | X at t associated in-sample with Y at t+h | The competitor arm only (local Granger/TE screen on training windows) | Only as "the in-sample screen selected X" | "The screen selected F1 variant (a); it did / did not survive the out-of-sample test" | "X leads Y by 2 h"; any lag claim |
| 3. Incremental predictive information | Point-in-time, out-of-sample, nested, beyond B, same learner, sealed holdout | Holm-adjusted batch-means test; skill with CI; gates (a)–(l) | **Yes: the only confirmatory claim** | "F1 added x% [lo, hi] z-pinball skill beyond public baseline B for the first-published GB imbalance price 2 h ahead, confirmation window 2025-04-01 → 2026-08-31" | "F1 predicts prices"; "beyond what traders know"; "beyond all public information" |
| 4. Plausible mechanism | A physical or economic channel consistent with the evidence | Mediation (B+W\*, physical target); directional checks on \|revision\| and freshness within SP-of-day × month cells | Support only, labelled A or B | "Consistent with a market channel (label B)" | "Proves BRPs position on stale forecasts"; "the market under-reacts" |
| 5. Causal effect | Changing X would change Y | None | **Never** | — | "Revisions drive / cause prices" |

**Why level 5 is out of reach (INFERENCE).**
- Weather is a common cause of forecasts, revisions, positions, NIV and prices.
- BRP positions are observed only through PNs.
- There is no intervention or randomisation.
- Variation in publication timing is used only as a directional mechanism check, not as an identification strategy.

### 11.2 Evidence package per claimed family

Every family that reaches INTERESTING-below-SESOI or better ships with all of the items below, generated from run outputs by committed code.

| # | Item | Content | Rules out | Gating? |
|---|---|---|---|---|
| 1 | Incremental skill | L and G skill; batch-means CI (n_b × 14 days, t(n_b − 1)); MBB CIs (7/14/28-day blocks, B = 10,000); £ scale; latest-run price scale | Chance; learner artefact; scale artefact; target-vintage artefact | Yes: (a)–(c), (f), (g) |
| 2 | Placebos and validity controls | The real statistic against each placebo type (1 / 37 / ≥ 99 draws); oracle ≥ 20%; planted 10% X recovered; +1-cycle changes forecasts and raises. Power calibration: planted-2% recovery rate and +1-cycle skill. | Seasonal proxy; an insensitive pipeline | Yes: (i); INVALID |
| 3 | Baseline robustness | Skill against B+ (BOALF); B-PNtotal sensitivity; K-competence result and any repair used | Stale or weak baseline; mapping artefact | Yes: (h); INVALID |
| 4 | Mediation | B vs B+W\* vs B+W\*+F1; F1 skill on the physical target; channel label | Forecast combination presented as a market channel | Label |
| 5 | Conditional regime table | GW test per R1–R3, Holm-adjusted | Pooled averages hiding regime structure | Holm; exploratory if no Stage 2 rejection |
| 6 | Reference-vintage/lag profile | Skill per variant with 14-day MBB bands | — | Descriptive (level 2) |
| 7 | Information-age bands | Skill by schedule-derived WINDFOR age band and by DISEBSP age tercile | Freshness asymmetry presented as skill (Exp 0: −15.6% vs +13.7%) | Descriptive, mandatory |
| 8 | Encompassing | y on the B and B+X medians, 14-day-block HAC | "Lower loss but no independent weight" | Diagnostic |
| 9 | Concentration | Top 5/10/20 days' share; drop-5 skill; pooled vs equal-weight daily sign test | A few scarcity days carrying the result | Yes: (e); cap rule |
| 10 | Stability and decay | Quarterly table; rolling 90-day skill with structural dates; ≥ 90 post-P days; the post-design block (descriptive) | A regime-bound or decaying effect | (d); STRONG-final |
| 11 | Calibration | PIT per 30-day block; raw and recalibrated 80%/90% coverage; reliability for the 4 events; Murphy diagram | Sharp but miscalibrated gains | Yes: (k) |
| 12 | Model disagreement | Spread across L, G and Chronos-2; the Chronos-2 post-checkpoint comparison | A single-model artefact | Descriptive |
| 13 | Competitor arm | Share of in-sample-screen picks that survive | Commoditised screens performing as well | Descriptive |
| 14 | Data completeness | By month and \|NIV\| decile; "first vintage missing" share; excluded months and the recomputed n_b | Survivorship: gaps on stress days | Descriptive; k1–k5 |
| 15 | Provenance | Per prediction: vintage ids, row ids, per-source max `known_at`, max label `known_at`. Per run: raw manifest hash, as-of definition hash, pre-registration hash and P, git SHA, lock hash, ledger entries | Unreproducible or leaked numbers | Yes: (l) |
| 16 | Statistic census | Count of every emitted p-value or interval, tagged gating or non-gating; the running FWER bound | Cherry-picking uncorrected intervals | Asserted |
| 17 | Economic check | §12 output, labelled secondary | Presenting skill as money | PRODUCT SIGNAL only |

### 11.3 Brief §4B evidence types: included, or omitted and why

| Type | Status |
|---|---|
| Incremental forecast improvement; ablations; conditional ablations | Included (items 1, 3, 5) |
| Lag stability | Descriptive only (item 6); no lag claims |
| Forecast revisions | The subject of F1/F2. Separated from forecast level by construction (§8.9) and from forecast combination by mediation (item 4). |
| Rolling forecast skill; regime dependence | Included (items 5, 10) |
| Model disagreement; calibration; provenance | Included (items 11, 12, 15) |
| Sensitivity | Uniform 5-min margin; block lengths; £ scale; target vintage; B-PNtotal; the 10 leftover days |
| **Historical analogues** | **Omitted.** They protect against no identified failure mode and invite outcome-selected storytelling. |
| **LLM narratives; SHAP or importance from G; in-sample Granger/TE weights as "explanation"** | **Omitted as evidence.** None of them measures out-of-sample incremental information. nixtla's own docstring says its weights "do not establish that changing a feature will cause the target to change" (FACT, [NX] `nixtla_client.py:1545-1549`). |

### 11.4 Verdict card template

This is the only form in which a relationship may be reported:

> **Claim:** C1 / C2. **Family:** F1 (NESO WINDFOR revision, variant ⟨frozen⟩). **Target:** first-published GB SSP, h = 2 h. **Baseline:** B (public; excludes live intraday, BM stack beyond BOALF, vendor forecasts, licensed NWP, neighbouring prices and ATC). **Window:** confirmation 2025-04-01 → 2026-08-31, ⟨n_b⟩ batches; excluded months ⟨list⟩. **Skill (L / G):** x% [lo, hi] / y%. **Holm-adjusted p:** ⟨·⟩. **Gates (a)–(l):** ⟨pass/fail list⟩. **Channel label:** A/B. **Verdict:** ⟨FAIL / FAIL-BY-POWER / INCONCLUSIVE / INTERESTING-below-SESOI / INTERESTING / STRONG-provisional / STRONG-final⟩. ~~**Running FWER bound:** ⟨0.05 + 0.005k⟩.~~ **Guarantee class:** G1 (single-use) **[v2]**. **α spent:** 0.04 (+0.01 if extended). **Claim level:** 3 (incremental predictive information). No lag claim; no causal claim; not evidence of tradability (see §12).

## 12. Economic sanity check

### 12.1 What it is and is not

The check keeps four questions apart:
1. forecast improvement (§§10–11);
2. tradable information;
3. net economic value after costs;
4. commercially useful software. Only buyer calls can test this; the check does not address it.

It is one mechanical rule, frozen in the pre-registration before any results, never optimised, and **never gating the forecasting verdict**. It gates only PRODUCT SIGNAL.

### 12.2 The rule (complete; no open items)

| Element | Specification |
|---|---|
| Notional asset | A 1 MW flexible position: **0.5 MWh per SP**, decided at origin t for target SP s (2 h ahead) |
| Forecast source | q50 from **L**, the instrument of record. B+X arm: L(B+X_f\*). B arm: L(B). N1 arm: the last first-published SSP. |
| Reference price | MID_ref = the last first-published APXMIDP price with `known_at` ≤ t |
| Entry rule | q50 − MID_ref > +£5/MWh → position = +0.5 MWh (be long into imbalance instead of selling intraday). q50 − MID_ref < −£5/MWh → position = −0.5 MWh. Otherwise flat. |
| Missing reference | If no APXMIDP record for any of the 4 SPs before t is known at t, or the latest one has zero volume → **flat** (counted) |
| P&L per SP | position × (settled SSP_s − P_exec) − £1.5/MWh × \|position\| |
| Settled SSP_s | Historical windows: the latest-run SSP from the single REST snapshot on a fixed, recorded date on or after 2026-10-15. Prospective window: the recorder's REST value captured at s + 30 days (± 1 day; capture_time stored). Both are labels only, never features. |
| Execution variant A | P_exec = realised MID_s. **Optimistic:** a VWAP that includes trades after t (INFERENCE). If MID_s is missing or has zero volume, the SP is excluded from variant A only (counted). |
| Execution variant B | P_exec = MID_ref. **Stale, but known at t.** |
| Arms | B+X, B, N1. Same SPs as the forecasting evaluation (identical drop set). |
| Sizing | Fixed 1 MW; no scaling by confidence, no compounding, no stops |
| Asset realism | The notional ±0.5 MWh per SP ignores state of charge, energy capacity and round-trip losses. A real 1 MW battery could not hold 48 consecutive same-sign positions (INFERENCE). This is a directional value test, not an asset simulation. |
| Turnover cap | At most 48 decisions per day: ≤ 24 MWh/day and ≤ 8,760 MWh per MW-year (arithmetic) |
| Cost | £1.5/MWh × \|position\|, covering exchange/clearing fees plus half-spread and slippage. Real GB values are UNKNOWN. At maximum turnover, costs are ≤ £13,140 per MW-year (arithmetic). |
| Cost grid (reported, not tuned) | £0 / 1.5 / 3 / 5 / 10 per MWh, plus the breakeven cost |
| Liquidity | No liquidity model; price-taker. MID is thin (INFERENCE). No free GB intraday tape exists to validate execution (FACT: EPEX GB is paid, §8.12). |

### 12.3 Report

| Output | Detail |
|---|---|
| Per arm (B+X, B, N1) | £/MW-year; hit rate; turnover; count of flat-by-missing-MID SPs; 14-day block-bootstrap 90% CI |
| **Incremental P&L** | P&L(B+X) − P&L(B) under both variants, with block-bootstrap CI and the top-10-day share |
| Structural controls | Always-long and always-short at identical costs. On ERCOT, always-short earned $11.82M with no forecast (FACT, [T0] line 1547). |
| Cost sensitivity | The full cost grid and the breakeven cost |
| Overfitting correction | Deflated Sharpe ratio, with N = the ledger's configuration count (design-stage configurations included) |
| Scale reminder | ERCOT: t0-alpha's MAE was 38% below the lagged baseline (14.55 vs 23.57), but profit was only about 6% higher ($15.00M vs $14.11M), under a rule selected after the fact (FACT, [T0] lines 1540–1543) |

### 12.4 Known weaknesses (stated before results)

- **Variant A is an upper bound.** Realised MID includes trades after the origin (INFERENCE).
- **Variant B executes at a price for an earlier SP.** It is stale, and liquidity at that price is not established.
- **The cost is an assumption.** £1.5/MWh may understate the real spread 2 hours ahead (UNKNOWN).
- **Structural skew.** Skew in (SSP − MID) can generate P&L with no forecast at all. That is why the structural controls are gates.
- **The settled price mixes run types.** The historical snapshot mixes settlement runs by SP age (§8.2).
- **Asset realism.** State of charge and energy limits are ignored (§12.2).
- **Regulatory stance.** Deliberately holding imbalance positions may attract BSC/Ofgem scrutiny (UNKNOWN).
- **Not how real NIV chasers trade.** They act inside the SP using BOA data (INFERENCE). A rule 2 hours ahead does not model that workflow.
- **Interpretation.** A positive result indicates **monetary significance, not tradability**. A negative result may reflect only the cost assumption.

### 12.5 Economic requirements for PRODUCT SIGNAL (all required)

1. Incremental P&L of the B+X rule minus the B rule is **> 0 at £3/MWh under both execution variants**. **[v2: gate on variant B only; variant A is reported, not gating.]**
2. The 14-day block-bootstrap **90% lower bound is > 0 under variant B** (execution at MID_ref, known at t).
3. B+X P&L **exceeds the larger of the always-long and always-short controls**.
4. The **deflated-Sharpe probability is ≥ 0.95**, with N taken from the ledger's configuration count.
5. The **top 10 days carry < 50%** of the incremental P&L.

These are necessary, not sufficient. PRODUCT SIGNAL also requires STRONG-final, the buyer-call conditions, the professional-baseline check and licence clearance (§8.24). No parameter of this rule may change after results are seen, except as a ledgered pre-registration amendment tested only on days after the amendment's own tag date.

## 13. Commercial reality

**Verdict.** The commercial case is thin. Experiment 1 cannot answer the commercial question whatever it finds, so that question has to be tested separately, in parallel. The expected ceiling is **consulting-sized** unless buyer calls show otherwise (INFERENCE: landscape digest). **[v2: Exp 1 scope. The rest of §13 assesses a stand-alone forecasting / feed-validation / audit tool. It is not a verdict on the AI-researcher product, whose commercial case is untested (condensed memo v2 §13).]**

A GB result would mean only "beyond *public* information":
- **ECMWF timing.** The only historically timestamped copy of ECMWF open data is the AWS mirror. Its S3 `LastModified` falls 6.45–8.57 h after init (FACT: 280-run sample, verify-top check). ECMWF's own portal release time is UNKNOWN.
- **What desks hold.** Professional desks typically hold licensed ECMWF feeds, vendor vintages (EQ, Volue) and live BM and intraday data that B lacks (INFERENCE).

### 13.1 What the capability could certify, by rung of the five-rung ladder

| Rung | Claim type | Can Exp 1 certify it? | Who already sells it or gives it away | Commercial consequence |
|---|---|---|---|---|
| 1 | Correlation | Not tested | Any analytics stack | None |
| 2 | Lead/lag association | Descriptive only. In simulation, 33% of true-signal claims named the wrong lag (SIMULATION: unpersisted, not independently reproducible; §1) | **nixtla 0.9.0 `explain()`**, released 2026-09-21. It is a method of the *hosted* TimeGPT client, so the data go to Nixtla's API. It returns Granger and transfer-entropy weights and says they "do not establish that changing a feature will cause the target to change" (FACT: nixtla-0.9.0 wheel, `nixtla_client.py:1530-1566`).<br>**Tigramite PCMCI**, GPL-3.0 (FACT: jakobrunge/tigramite README) | Commoditised. Not whitespace |
| 3 | Incremental predictive information | **Yes, and it is the only thing tested.** Claims are made per family, against a public B, on a sealed holdout | **Equities:** Numerai MMC/BMC (FACT: numerai/docs `meta-model-contribution-mmc.md`) and Exabel `known_time` PIT backtests (FACT: exabel-9.1.0 wheel, `time_series_api.py:109-139`).<br>**PIT engine without a test protocol:** OpenSTEF 4.4.3 `VersionedTimeSeriesDataset` (FACT: openstef_core-4.4.3 wheel) | The only plausible whitespace: an independent, pre-registered, vintage-correct audit of incremental information against the **buyer's own** baseline (INFERENCE) |
| 4 | Plausible mechanism | Only as a pre-registered label from the mediation arm. "Market channel" if F1 skill against B+W\* is ≥1.0% with one-sided p < 0.10; otherwise "physical / forecast-combination channel" | Analyst narrative from Montel, LSEG, Kpler, Aurora, Modo, Dexter (UNVERIFIED: search summaries) | A label on an audited result. It cannot be sold as "discovery" |
| 5 | Causal effect | Never claimed | None | Must not be marketed |

### 13.2 The four questions the brief keeps separate

| Question (brief §4E) | Exp 1 artefact | Gate | What a "yes" still does **not** show |
|---|---|---|---|
| Forecast improvement | z-pinball skill of L(B+X) against L(B), same learner | STRONG (claim C1 or C2, §17.0) | That the information is tradable |
| Tradable information | Incremental P&L of the pre-registered rule under variant B (P_exec = MID_ref, known at t), compared with always-long and always-short | PRODUCT SIGNAL, economic item | Value to a real desk: MID is thin, and NIV chasers act within the SP using BOA data (INFERENCE) |
| Net economic value after costs | Cost grid £0 / 1.5 / 3 / 5 / 10 per MWh; gate at £3/MWh; deflated-Sharpe probability ≥0.95 with N from the ledger | PRODUCT SIGNAL | Demand for software |
| Commercially useful research software | ≤10 structured buyer calls, run by the user | PRODUCT SIGNAL, user-validation item | n/a |

Forecast skill and money are clearly different things. The ERCOT evidence is in `scratchpad/t0_paper.txt:1515-1554`, Table 12 (FACT):
- t0-alpha cut MAE against the lagged-price baseline by 38% (14.55 vs 23.57 $/MWh).
- It earned $15.00M against the baseline's $14.11M, about 6% more.
- An always-short rule with no forecast earned $11.82M.
- The trading rule was selected retrospectively.

### 13.3 What is already commoditised

| Workflow layer | Incumbent or free substitute | Label and source |
|---|---|---|
| Vintage (as-of) queries on power fundamentals | **Energy Quantified instances.** Fields `issued`, `created`, `modified`; relative, rolling and absolute queries; free users are limited to the last 30 days | FACT: eq-python-client `metadata/instance.py:1-24`, `docs/userguide/instances.rst` |
| | **Volue Insight INSTANCE curves.** `issue_date`, `get_relative`, `get_absolute`, `modified_since` | FACT: volue-insight-timeseries 2.3.1 wheel, `curves.py` |
| Point-in-time backtesting engine | **OpenSTEF 4.4.3.** `filter_by_available_before/at`, `select_version`; openstef-beam; MPL-2.0 | FACT: openstef_core-4.4.3, `datasets/versioned_timeseries_dataset.py:27,146-161` |
| In-sample lead/lag "explanations" and sample paths | **nixtla 0.9.0** `explain()` and `simulate()` (up to 10,000 paths). Hosted API | FACT: nixtla-0.9.0 wheel `_types.py:91-94` |
| Incremental-contribution scoring | **Numerai MMC/BMC.** **Exabel** PIT backtests with 1-week and 1-month revision tracking | FACT (sources above) |
| The target forecasts themselves | **Dexter** imbalance-price forecasts. **Meteologica** (claims 400+ traders). **Volue IDPP** (intraday VWAP up to 8 h ahead). **Kpler** (after acquiring COR-e). **Enfor** PriceFor | UNVERIFIED: search summaries |
| Execution and algo trading | **Volue Algo Trader** (claims >70 companies) | UNVERIFIED: search summary |
| | **PowerBot client** v2.35.3, published 2026-09-16 | FACT: `https://pypi.org/pypi/powerbot-client/json` |

**What is missing.** Nothing in this stack certifies rung 3 for power with pre-registration, placebos and a sealed holdout. That absence was **not** proven: the search was limited, and incumbents may do this internally (UNKNOWN).

### 13.4 The six value propositions compared

| # (brief) | Proposition | Existing budget? | Substitutes | What Exp 1 would need to show | Main objection | Rank |
|---|---|---|---|---|---|---|
| 3 | **Alternative-data / feed validation** | **Equities: yes.** About $2.8bn of alt-data spend in 2025; the average buyer spends about $1.6M/yr (UNVERIFIED: Neudata report via search summary).<br>**Power:** feed choice goes through in-house, often free, trials (INFERENCE) | Exabel/BattleFin, Neudata, Eagle Alpha (equity, low frequency); vendor trials | A vintage-correct ablation of a *specific feed* against the buyer's baseline, priced against the feed's cost | Needs the buyer's baseline under NDA, or on-premise software that competes with free tools | **1** |
| 6 | **Monitoring of incremental skill and signal decay** | UNKNOWN | Nixtla online anomaly detection covers part of it (INFERENCE). No rolling incremental-skill-with-CI product for power features was found | Rolling 90-day skill with CIs; the ledger | Only valuable once a signal exists | **2** |
| 2 | Quant research productivity | Buyers mostly build their own (INFERENCE) | OpenSTEF, Nixtla, Darts, skforecast, statsforecast (FACT: PyPI, actively maintained); EQ and Volue PIT queries | Faster, safer ablations | Free open source covers most of it | 3 |
| 1 | Alpha generation | Highest willingness to pay (INFERENCE) | In-house desks; vendor price forecasts | STRONG-final, plus an economic gate, plus a professional-baseline check | Least credible for a new entrant: the method is treated as IP and needs a live audited track record. ERCOT's skill-to-profit ratio is about 6/38 (FACT, t0 paper) | 4 |
| 4 | Signal discovery | Weak | nixtla `explain()`; tsfresh FRESH + BY-FDR (FACT: `blue-yonder/tsfresh docs/text/feature_filtering.rst`); tigramite | Discoveries that survive the sealed test | Automated discovery is where false discoveries come from. SIMULATION (unpersisted): a holdout supports about 3 confirmatory families per market-year, and reuse raised FWER from 1% to 19% over 10 rounds | 5= |
| 5 | Explainable market intelligence | Crowded | Montel, LSEG, Kpler, Aurora, Modo, Dexter, LLM narrative tools (UNVERIFIED: search summaries) | Rung-4 labels only | Explanation does not differentiate; in-sample explanations are a free SDK call | 5= |

### 13.5 Buyer types

| Buyer | Already holds (INFERENCE unless noted) | Build or buy | Fit |
|---|---|---|---|
| Commodity trading houses, utilities | EQ, Volue, Meteologica, LSEG, Kpler; in-house quants and meteorologists | Buy data, not methodology; slow procurement | Medium (feed-validation wedge) |
| Prop power desks, algo shops | Vendor data plus execution | Build | Low |
| GB BESS optimisers and BRPs, e.g. enspired, Entrix (UNVERIFIED: search summaries) | Forecasting is their core IP | Build; buy fundamentals | Medium, for GB-specific feed validation |
| Hedge funds | Large data budgets, evaluated through Neudata, Eagle Alpha and BattleFin trials | Buy data after trials | Low: power is niche for them |
| Retailers, suppliers | Small forecast budgets; buy vendor forecasts | Buy forecasts | Low |
| Quant research teams | Open source | Build | Low |
| Equity alt-data teams | Exabel-type tools | Buy | Low: wrong frequency |

Sales cycles and procurement processes are UNKNOWN; no primary evidence was found.

### 13.6 Most credible initial buyer and workflow (INFERENCE; no demand evidence)

- **Buyer.** The quant or fundamentals lead at a mid-size European trading house, or at a GB battery optimiser or BRP.
- **Workflow.** They must decide whether a data feed or forecast vendor adds point-in-time information to their own imbalance or intraday forecasts. Examples: a second NWP provider, or EQ against Volue. The answer is worth something only when set against the feed's cost.
- **Deliverable: a rung-3 audit report** containing:
  - the nested ablation against *their* baseline;
  - the placebo distribution and positive controls;
  - known_at lineage;
  - the pre-registration hash and ledger;
  - £ decision scoring.
- **What Exp 1 contributes.** A public worked example and a methodological credential. It is not a sellable result. A GB public-baseline finding says nothing about incremental value over a desk that already buys EQ or Volue vintages.

### 13.7 Blocking problems

1. **Baseline access.** "Incremental" only matters against the buyer's own baseline. That needs their forecasts under NDA, or an on-premise harness (INFERENCE). **[v2: Exp 1 scope in this form. With in-customer deployment, which is the product's shape, it changes form: the customer must supply a codified, runnable baseline. Security, data-governance and on-prem requirements come with it.]**
2. **Build, not buy.** The segments most willing to pay build in-house (UNVERIFIED: search summaries on enspired and Entrix; INFERENCE). **[v2: binds the product too. Top funds reportedly build agentic research in-house (UNVERIFIED), and this is tested in the buyer calls.]**
3. **Wrong budget pool.** Large alt-data budgets sit in equities, at low frequency (INFERENCE).
4. **Licence.** Whether the BMRS licence permits commercial use is UNKNOWN; search summaries conflict. If it forbids commercial use, K-licence kills the product path, not the science.
5. **Thin moat.** **[v2: this form is Exp 1 scope (public-data feed). The product's moat is an open question, see condensed memo v2 §13.]**
   - The IRIS archive is itself public and anonymous (FACT: `insights-docs/docs/iris_archive.md`). A self-recorded copy adds only an audit of UploadTime.
   - For GB, the non-copyable asset reduces to an audited live track record plus the method (INFERENCE).
   - Independence from forecast sellers (EQ, Volue, Dexter, Meteologica) is the only other angle, and it is thin (INFERENCE).

### 13.8 Buyer discovery: start now, in parallel, independent of the data

**[v2: superseded for the product by the two call scripts, kill rules and positive signal in condensed memo v2 §13. This v1 script remains valid only for the stand-alone-tool question.]**

**Owner: the user.** The calls need the user's network and identity; Claude can draft the script and synthesise notes. Plan up to 10 structured calls of about 45 minutes each, with GB BESS optimisers, BRP/NIV desks, and EU intraday quant or fundamentals leads.

Ask every call:
1. Is there an existing budget line for independent, vintage-correct feed validation, and is it larger than the cost of the feed being validated?
2. Do you already run point-in-time ablations in-house?
3. Would you share baseline forecasts under NDA, or run a harness on-premise?
4. Do you already hold licensed ECMWF, Energy Quantified or Volue data? If so, open-data revisions would not matter to you.

**Definition of "equivalent in-house ablation":** an out-of-sample, nested (same-learner) ablation on issue-time-stamped vintages, for the same target class (imbalance or intraday price or volume).

**Pass rule** (identical to PRODUCT SIGNAL item 3, §17.8):
- At least 3 of 10 name an existing budget line of ≥£10k/yr, and confirm they run no equivalent in-house ablation.
- At least 1 commits to a paid pilot, or to sharing its baseline under NDA.

---

## 14. Repository architecture decision

### 14.1 Facts about Experiment 0's shape that drive the decision

All FACT, re-verified at `406c92c` in this pass; working tree clean (`git status`).

- **Clipping.** Forecasts are clipped at zero: `solarbench/backtest.py:234` (`np.clip(pred.values, 0.0, None)`). Negative GB prices would be corrupted.
- **Fixed 30-minute grid.** `solarbench/data.py:36-37` defines `STEP = 30 min` and `STEPS_PER_DAY = 48` as module constants. They are used in the window, slot, band and context code.
- **Univariate, self-censoring protocol.** `predict(series, windows)` at `solarbench/forecasters.py:74`.
  - Every model receives the full series, future included, and is trusted to censor itself.
  - The t0 context must end *exactly* at the origin (`forecasters.py:405-406`). That is a zero-publication-lag convention.
- **Event-time leakage contract.** `_check_contract` at `solarbench/backtest.py:150-167` is keyed on event time, not on known_at.
- **Fingerprint conflates missing and −1.** `solarbench/data.py:192` calls `fillna(-1.0)` before hashing.
- **Cache key omits code identity.** `_cache_key` at `run_benchmark.py:187-203` has no git SHA and no package lock.
- **t0 pin.** `requirements.txt:9` pins `tfc-t0>=0.3.2,<0.4`, which blocks t0-beta and tfc-t0 0.5.0.
- **Manual CI only.** `.github/workflows/benchmark.yml:7-8` uses `workflow_dispatch`. There are 54 test functions, or 56 with parametrisations (tag message).
- **Tag byte-identity.** The `experiment-0-solar-final` tag is byte-identical to the canonical-run commit 3c4abb9, apart from the README and the PDF (FACT: exp0 digest, `git diff --stat`).
- **Artifact expiry.** The run #11 Actions artifact `results-full-11`, which holds the forecasts parquet, expires **2026-10-13**. The scratchpad copy holds CSV and JSON only (FACT: tag message).
- **Little is generic.**
  - About 15–20% of the 2,809 non-test lines are plausibly generic, and only about 90 lines are truly domain-free.
  - The domain-free lines: `binomial_two_sided_p` (`metrics.py:191-203`), `_sha256` (`data.py:71-76`), `_git_sha` (`run_benchmark.py:107-113`), `_versions` (`run_benchmark.py:735-744`), `skill_score`/`_pooled_mae` (`metrics.py:95-101`), and parts of `concentration`/`bootstrap_sensitivity` (FACT: exp0 digest, AST line counts).
- **The component Exp 1 needs most has no counterpart.** That component is a known_at as-of store with vintages and label-availability gating. Nothing like it exists in Exp 0 (FACT: code reading).

### 14.2 Assessment on the brief's six criteria

| Criterion | A: extend solarbench | B: extract a generic core now | C: Exp 0 immutable, Exp 1 alongside |
|---|---|---|---|
| Risk to Exp 0 reproducibility | **High.** Every Exp 1 change edits frozen modules and breaks the verified invariant tag = run #11 | **High.** Migrating Exp 0 onto the core forfeits byte-identity, and re-verification is weak:<br>• the cache key excludes code, so a naive rerun passes from cache;<br>• t0 reproduces only within 0.003–0.03 MW;<br>• the artifact expires 2026-10-13 | **Nil for code.** The residual risk is environment rot, handled by a cheap CI job (§14.3) |
| Complexity | High: solar and market semantics mixed in one package | Highest: the abstraction is designed from one example of the wrong shape | Lowest |
| Duplicated code | None | None in principle | About 90 lines, copied with provenance comments |
| Premature-abstraction risk | Entrenches the *wrong* abstractions: univariate, event-time, clip-at-zero, UTC-lag slots | Maximal | Low, given an explicit extraction trigger |
| Scientific auditability | Poor: one package serves two experiments with different semantics | Moderate: Exp 0's results would be served by code that did not produce them | **Best:** each experiment's code maps one-to-one to its results |
| Future maintainability | Poor | Good only if the abstraction happens to be right | Fine until a second consumer exists |

### 14.3 Recommendation: **Option C, with hard conditions.** A and B are rejected for now.

1. **Exp 0 is immutable.** README errata only; the tag is the reference.
2. **Exp 1 gets its own top-level home.** It has its own `pyproject`, lock file and workflow, all path-filtered. The root `requirements.txt`, `constraints-ci.txt` and `benchmark.yml` stay Exp 0's.
3. **Import boundary.** A test fails if Exp 1 imports `solarbench`.
4. **Golden test.** It re-derives run #11's primary CI **[−13.81%, −4.29%]** from a committed copy of `per_day_errors_wide.csv`. That proves the copied bootstrap matches. The CI was recomputed in memory in an earlier pass (FACT: exp0 digest).
5. **Exp 0 test job.** A cheap push/PR job keeps Exp 0's 56 offline tests running, to catch environment rot.
6. **No data in git.** Only manifests and hashes are committed.
7. **Housekeeping (R6, §18) before 2026-10-13.** Download `results-full-11` to durable storage outside the repo. This is a download, not a code change, and needs the user's approval.

### 14.4 Challenge to the user's bias ("C initially, possibly evolving toward B")

1. **C is forced, not a cautious compromise.** With a GB imbalance target, the overlap with Exp 0 is about 90 lines of statistics helpers (INFERENCE from the FACT inventory). Choosing C is no virtue here; the alternatives do not fit.
2. **C's real failure mode is "copy solarbench and extend".** That recreates A's assumptions in a new folder:
   - full-series self-censoring;
   - zero publication lag;
   - definitive-only vintages;
   - an event-time contract;
   - clipping;
   - one daily origin.

   **Rule:** Exp 1's point-in-time layer is written fresh from the red-team threat model (§7, §15). Only the listed helpers are copied, each with a provenance comment.
3. **"Evolving toward B" needs an explicit trigger.** Without one it will either never happen or happen too early.
   - Trigger: a second consumer (the Belgium replication or Exp 2) reuses Exp 1's as-of core *unchanged* in at least 2 modules.
   - Extraction is from Exp 1, never from solarbench.
   - Exp 0 never migrates; it lives on its tag.
4. **A separate repository may be the better variant of C.** Either condition would force it:
   - repo-level CI and dependencies cannot be isolated with path filters;
   - licensed data could ever enter the repo. GB data is free, but the BMRS licence is UNKNOWN. EPEX DE data is internal-use and non-transferable (FACT per decision record: €480/yr academic route).

---

## 15. Minimum architecture

**Principle.** Build only what Experiment 1 needs: a plain Python package, files on disk, no database server, no service, no UI, no authentication.

**Size.** About **2,750–3,350 lines including tests** (INFERENCE):
- The component estimates in §15.2 sum to 3,050–3,350 lines, or 2,750–2,950 without component 1.
- The decision record's "2,000–3,000" is below its own component sum.
- For comparison, Exp 0 has 2,809 non-test lines plus 1,058 test lines (FACT: exp0 digest).

**Nothing below is authorised before approval** (§18, §20).

### 15.1 Stage 0 needs none of it

Stage 0 (k1–k7) uses only:
- read-only metadata audit scripts, written to the scratchpad and not part of the Exp 1 package;
- a confirmation-window parser that never materialises value fields;
- Elexon's stock IRIS client for the k4 live capture, which the user registers and runs;
- output tables in the scratchpad.

It uses no Exp 1 code, no store, no models and no repository changes. **k8 is the first gate of the approved build** (§17.1).

### 15.2 Components for Experiment 1

Each component exists because it blocks a named failure mode.

| # | Component | Responsibility | Threat it defends against | Size (lines, INFERENCE) |
|---|---|---|---|---|
| 1 | Forward recorder | A wrapper around the IRIS AMQP client plus 15-min REST polls, on an always-on VM. Writes raw payload, sha256 and capture_time into the **hash-gated sealed store**; values stay unreadable until the freeze (§17.0).<br>IRIS facts: free registration, 3-day TTL, secrets expire after 2 years (FACT: `iris-clients/README.md`) | Archive gaps, backfill, synthetic UploadTime; cron lag; pre-freeze peeking at "prospective" values | 300–400 |
| 2 | Raw store | Immutable blobs outside git: IRIS JSON, GRIB byte ranges, recorder payloads.<br>Manifest parquet: source key, sha256, tags, UploadTime/LastModified, fetch time, client version. Manifest hashes are committed | Archive mutation; provenance loss (Exp 0 recorded no query parameters or ETag: `data.py:82-140`) | 150 |
| 3 | Vintage table | One long parquet per dataset with the PIT row schema, built by versioned parsers. The known_at rule table lives in the pre-registration YAML | The IRIS `Timestamp` tag means different things per dataset (FACT: `insights-docs/docs/dataset_and_timestamp_reference.md`); REST latest views | 300 |
| 4 | As-of builder | One function (DuckDB ASOF JOIN, or pandas `merge_asof` on known_at) that produces the per-origin feature matrix plus lineage. **The only path from data to models** | Self-censoring models (Exp 0 `forecasters.py:74`); stale-B vs fresh-X asymmetry | 200 |
| 5 | Target builder | First DISEBSP per SP by minimum UploadTime; message id stored; exclusion flags | Settlement-run revisions; REST returns only the latest run (FACT: elexonpy 1.0.16 `indicative_imbalance_settlement_api.py:1665`) | 100 |
| 6 | Model adapters | N1–N6, L, G and Chronos-2, each exposing `fit(X, y)` and `predict_quantiles(X)` on matrices only | Information leaking through model interfaces | 400 |
| 7 | Runner | Walk-forward and arm runner with **one arm registry shared by the CLI and the tests**: B, B+X variants, B+, B+W\*, placebos, positive controls, and the competitor screen.<br>The competitor screen is a **local** statsmodels Granger test plus a pinned transfer-entropy estimator; no hosted API, because BMRS data must not go to third parties while the licence is UNKNOWN.<br>Weekly refits.<br>Cache key = raw-snapshot manifest hash + as-of definition hash + pre-registration hash + model spec + git SHA + lock hash | Unpoisoned arms; a stale cache (Exp 0 `_cache_key`, `run_benchmark.py:187-203`); data egress | 300 |
| 8 | Statistics and verdict engine | Daily differentials, batch-means t, Newey-West, BH, Holm, MBB, per-type placebo ranks, the MDE rule. Writes `verdict.json` **per claim with the precedence table of §17.0**, and counts every emitted statistic as gating or non-gating | Overlapping verdicts; multiplicity handled only in prose (Exp 0 emitted about 44 comparisons against a stated 19–20) | 300 |
| 9 | Seal and ledger | Pre-registration-hash gate in the loader, covering confirmation *and* recorder values. Append-only, hash-chained JSONL ledger that feeds α-spending, the DSR N and the freeze date P | Holdout reuse (SIMULATION, unpersisted: FWER 1% → 19% over 10 rounds); pre-freeze prospective data | 100 |
| 10 | Report generator | Built from run outputs only, with a prose-number diff test | The 92-vs-90 slip; numbers from outside the repo | 100 |
| 11 | Tests | Truncation equivalence on ≥1,000 stratified origins. Poisoning: affine, NaN, sign-flip, later-vintage rewrite, label poisoning. Vintage swap. DST days (46/50 SPs). Mutation tests: known_at −1 h, margin 0, join on the Timestamp tag, REST latest view, rolling window on the target index. Denylist. Import boundary. Golden bootstrap against run #11.<br>All run in CI on synthetic IRIS-shaped fixtures | Vacuous controls (Exp 0 `tests/test_benchmark.py:866,1031`) | 800–1,000 |

### 15.3 Row schema and known_at rules (from the decision record's PIT rules)

**Row fields:** `source, dataset, series_key, valid_start_utc, valid_end_utc, issue_time, upload_time | s3_last_modified | capture_time, known_at, vintage_id (blob name + sha256), revision_number, capture_mode ∈ {iris_archive, s3, forward_capture, rest_crosscheck}, value, is_missing`.

**known_at rules:**
- General rule: `known_at = max(publishTime if present, UploadTime) + margin`.
  - margin_B = 2 min for datasets that enter B. That includes WINDFOR, so **F1 and F2 use margin_B**.
  - margin_X = 10 min for X-only sources: REMIT (F7), NESO (F8) and ECMWF (F6).
  - The asymmetric margin protects only those X-only families. F1's protection is different: B holds the same latest WINDFOR level (§8.9 key algebra).
- ECMWF: max LastModified over the files used, + 10 min.
- Own capture: max(UploadTime, capture_time) + 2 min.
- **Never used as known_at:** init_time, nominal schedules, settlementDate, blob-name times, or the IRIS `Timestamp` tag.

**Time and value hygiene:**
- UTC internally; naive datetimes are rejected.
- Payload `startTime` must equal the Europe/London mapping of (settlementDate, SP).
- Every dropped row is logged with a reason code. Exp 0 counted its drops (`missing_steps = 6` in the manifest) but did not itemise rows or reasons (FACT per §2.2).
- Missing values stay explicit: NaN, plus an indicator, plus staleness. The fingerprint hashes (value, isnull).
- No clipping. No interpolation across t.

### 15.4 Data flow

```
IRIS archive / ECMWF S3 / recorder ──► raw store (immutable, hashed manifest; recorder values sealed until P)
        ──► versioned parsers ──► vintage table (known_at per row; rule table from pre-reg YAML)
        ──► as-of builder(t) ──► feature matrix + lineage ──► model adapters (fit/predict on matrices)
target builder (first DISEBSP) ─────────────────────────────►┘
        ──► runner (arm registry, weekly refits, cache) ──► per-origin quantiles + lineage
        ──► stats/verdict engine ──► verdict.json (per claim, §17.0) ──► report (prose-number diff test)
seal gate + hash-chained ledger wrap every window access
```

### 15.5 Where it runs

| Activity | Where | Why |
|---|---|---|
| Ingest | A machine with egress to `archive.data.elexon.co.uk`, `data.elexon.co.uk` and the ECMWF S3 bucket | This sandbox gets CONNECT 403 from all Elexon and NESO hosts (FACT: re-probed 2026-09-23) |
| IRIS recorder | An always-on VM, not GitHub cron | GitHub cron can lag or drop runs (INFERENCE: digest) |
| Offline tests | GitHub Actions on synthetic fixtures | 6 h job limit (FACT per prior digest; not re-verified) |

### 15.6 Evidence package per claimed family

Each item is tagged with the ladder rung it can support.

| Evidence | Rung |
|---|---|
| Incremental skill with batch-means and MBB CIs, for L and G | 3 |
| Per-type placebo ranks; positive controls | Validity of 3 |
| GW conditional regime table | 3, conditional (a separate INTERESTING family) |
| Reference-vintage / lag profile with bands | 2, descriptive only |
| Skill by information-age band | Validity of 3 |
| Mediation (B vs B+W\* vs B+W\*+F1) and skill on the physical target | 4, label only |
| Forecast-encompassing regression | 3 |
| Rolling 90-day skill | Decay monitoring |
| PIT, coverage, reliability | Calibration |
| L / G / Chronos-2 disagreement | Robustness |
| Vintage ids and known_at lineage; pre-registration hash; ledger | Provenance |

Nothing supports rung 5.

### 15.7 Explicitly not built

- A generic vintage-registry service.
- A feature store.
- An experiment-tracking server.
- A plugin system for markets.
- An orchestration framework.
- Any frontend, API, authentication or deployment.
- Any hosted-model call on BMRS data.
- LLM narratives or historical-analogue search; they protect against no identified failure mode.

---

## 16. Cost / complexity

### 16.1 Money

| Item | Cost | Label and source |
|---|---|---|
| Elexon Insights API, IRIS archive | £0, no authentication | FACT: `insights-docs/docs/insights_data_platform.md`, `iris_archive.md` |
| ECMWF open data (AWS) | £0; CC BY 4.0 plus ECMWF Terms of Use | FACT: `ecmwf/ecmwf-opendata` README lines 730-732; `awslabs/open-data-registry datasets/ecmwf-forecasts.yaml` |
| NESO Data Portal (F8 only, if verified; R0-G cross-check) | £0 | UNVERIFIED (search summary); host blocked |
| Whether the BMRS licence permits commercial use | UNKNOWN | Search summaries conflict. Blocks only the PRODUCT path |
| IRIS recorder VM | About £5–20/month | INFERENCE |
| Compute | About £0–50 | INFERENCE |
| Not bought: EPEX GB continuous and day-ahead data | Quote-only. The EPEX continuous read-only API was reportedly €3,360/month for internal use | UNVERIFIED (search summary) |
| Not bought: vendor NIV forecasts, EQ/Volue archives | Quote-only. The EQ free tier covers the last 30 days only. GB wind coverage and trial terms are UNKNOWN (R1) | FACT for the 30-day limit: eq-python-client docs |

### 16.2 Transfer and storage (INFERENCE, corrected by the verifier)

- **IRIS.** About 1.3–2M blobs for the core datasets, roughly 10–50 GB of JSON.
  - FREQ alone is about 720 messages/day (FACT: elexon-bmrs 0.3.0 `get_datasets_freq` docstring).
  - PN and BOALF could add several million more blobs.
- **ECMWF.** 2 fields × about 8 three-hourly steps × 4 runs × about 910 days × about 1.35 MB comes to roughly 80–120 GB transferred, and under 2 GB after cropping to GB.
  - Steps are 3-hourly, not hourly (FACT: ecmwf-opendata README 376-381).
  - 100u, 100v and ssrd exist only from 2024-03-06 (FACT: S3 `.index` files).
- **Total:** about 0.1–0.2 TB transferred, a few GB retained.

### 16.3 Compute (INFERENCE; projected, not measured)

| Stage | CPU-h |
|---|---|
| Stage 1 screening (L at 5 quantiles, monthly refits, ≤49 arms) | 10–25 |
| Finalists, G and placebos (per type: 1 + 37 + ≥99 full-pipeline draws on L); planted-X controls | 30–60 |
| Stage 2 (≤5 arms × 2 learners × 19 quantiles, weekly refits) | 15–30 |
| Chronos-2: 3 arms × about 4,000 sparse origins × about 5 s. Projected from Exp 0's measured 0.19 s per univariate t0 origin | 15–20 |
| **Total** | **About 70–150 CPU-h, no GPU; 1–2 days on one 16-core workstation** |

### 16.4 Implementation effort in person-days

**Stage 0, stated once.** About **5–7 person-days** of audit effort for k1–k7 (decision record); the §18.2 item estimates for R0-A to R0-F plus R1 sum to 5.5–7.5. Supporting items (R0-G, R2, R3, R6, R7) add about 2–3.5 days. The **decision gate falls at least 15 calendar days after IRIS registration**, because k4 needs 14 days of live capture. This replaces the looser "about 1 week" and "about 1–2 weeks".

| Phase | Person-days | Label | Notes |
|---|---|---|---|
| Stage 0 core (k1–k7) | 5–7 | INFERENCE (decision record) | Gate ≥15 calendar days after IRIS registration |
| Stage 0 supporting items | About 2–3.5 | INFERENCE | §18.2 |
| Buyer calls (about 10 × 45 min, plus prep and synthesis) | About 2–3 of the user's time | INFERENCE | About 2 weeks elapsed, in parallel |
| Build (components 1–11, §15.2) | 20–30 (4–6 engineer-weeks) | INFERENCE | About 2,750–3,350 lines including tests |
| Stage 1 plus pre-registration freeze (P) | About 5 | INFERENCE | |
| Stage 2 plus report | About 5 | INFERENCE | Can run during the prospective window |
| **Sum to STRONG-provisional** | **About 39–54** | INFERENCE: sum of the rows | Excludes waiting for the prospective window |

### 16.5 Calendar (INFERENCE; recomputed from the freeze date P)

**P** is the date the pre-registration tag is committed. Prospective evidence starts at **P + 1 day** (§17.0).

The decision record's "earliest final verdict about January 2027" assumed that days from 2026-10-01 would count. **They do not.** From 2026-10-01 until P, the recorder provides an audit trail of UploadTime only, and its values stay sealed.

| Milestone | Earliest (arithmetic) | Plausible |
|---|---|---|
| Stage 0 decision gate | IRIS registration + 15 days: 2026-10-13 if registered 2026-09-28 | Mid-to-late October 2026 |
| Build (4–6 weeks) + Stage 1 → freeze P | 2026-11-18 to 2026-12-02 | December 2026 |
| **STRONG-final** (P + 90 days) | 2027-02-16 | **March–April 2027** |
| PRODUCT SIGNAL economic check (needs the settled price at s + 30 days) | 2027-03-18 | April–May 2027 |
| Full prospective window / pooled extension (P + 182 days, 13 batches) | 2027-05-19 | June–July 2027 |

**If GB fails Stage 0:**
- the ERCOT depth probe takes about 1 day;
- otherwise forward capture for at least 12 months, at about £60–240/year of VM cost, plus the wait.

### 16.6 Complexity and budget kill

- **Complexity is driven by point-in-time correctness, not modelling.** The heavy parts are components 3, 4, 5 and 11. L is about 150 lines of scikit-learn, and G is a pinned LightGBM (INFERENCE).
- **K-budget.** Any one of these triggers simplification (drop F6, F8, and PN if it is optional):
  - more than 6 engineer-weeks before the first discovery result;
  - more than 150 CPU-hours;
  - more than 1 TB transferred.
- **Comparison with DE-LU.** EPEX data costs €480/yr on the academic licence (internal use, non-transferable; FACT per decision record, source `pucandrzej/csvr_scenario_generation` README), or an unknown commercial quote. The TSO revision covariate would still need 12 or more months of forward recording.

---

## 17. Pre-registered success and kill criteria

**Frozen definitions** (from the decision record unless marked as an amendment):
- **Primary metric:** z-pinball skill = 1 − ΣP(B+X_f)/ΣP(B), with the same learner, the same origins and the same drop set. Pinball loss is averaged over τ = 0.05…0.95 on z = asinh(Y/c).
- **Inference unit:** the daily mean over a settlement date's SPs.
- **SESOI = 2.0%.**
- **Confirmation:**
  - 37 non-overlapping 14-day batches covering 2025-04-01 → 2026-08-31, with t(36) critical values.
  - The 10 leftover days, 2025-03-22 → 2025-03-31, are sensitivity only.
  - Holm at α = 0.04 over ≤4 hypotheses: {F1-price, F1-NIV, ≤2 screened families}.
  - One pre-committed extension at α = 0.01.
- **α accounting.** 0.04 + 0.01 uses up FWER 0.05. ~~Any further ledgered reuse at α = 0.005 raises the family-wise bound (to 0.055 after one reuse). `verdict.json` reports the raised bound.~~ **[v2: no further confirmatory reuse; see the addendum.]**
- **Engine:** every verdict is computed by committed code into `verdict.json`.

**Amendment: prospective window** (recommended; the decision record's 2026-10-01 → 2027-03-31 window predates the freeze; mirrors §7 row 34 and §8.6):
- Prospective = [P + 1 day, P + 182 days], 13 batches.
- STRONG-final needs ≥90 of those days.
- 2026-09-01 → P is a sealed "post-design, pre-freeze holdout". It is descriptive only and is never called prospective.
- September 2026 is the design month and belongs to no scored window.
- The prospective "settled" price is the recorder's REST value captured at s + 30 days.

**Ladder mapping:**
- STRONG certifies rung 3 only: incremental predictive information beyond *public* B.
- The mechanism label is rung 4, applied as a label, not a gate.
- No verdict certifies rung 5.

### 17.0 Claims and verdict precedence (mirrors §8.24; this resolves the decision record's overlaps)

`verdict.json` emits **one verdict per claim**:
- **C1: the §4D wind-revision thesis.**
  - F1-price (primary) and F1-NIV (Holm secondary).
  - F2 is tested only as B+F1+F2 against B+F1, and only if F1 is carried.
  - C1 is decided by F1 alone.
- **C2: other public information.** The ≤2 screened families from F3–F8 that are carried to Stage 2.
  - F3–F6 and F8 are labelled "revision information of another kind".
  - F7 is labelled "information, not revisions".
  - A C2 result never changes C1. A C1 FAIL does not block a C2 STRONG, but a C2 STRONG never supports the §4D claim.

**Precedence within each claim.** Evaluate top-down; the first matching row wins.

| Order | Verdict | Condition (confirmation unless stated) |
|---|---|---|
| 0 | **INVALID** (whole run; no claim verdicts) | Any §17.3 condition |
| 1 | **STRONG-provisional** | All gates (a)–(l) in §17.7 |
| 2 | **INTERESTING** | Holm-adjusted one-sided p ≤ 0.04 and point skill ≥ 0.5%, but not STRONG. Sub-labels:<br>• `-below-SESOI` if point skill < 2.0% or the one-sided 95% upper bound (UB) < 2.0%;<br>• `-unstable` if a stability gate fails;<br>• `-capped` if the sign flips when the top 10 days are dropped |
| 2′ | **INTERESTING** (C1-only routes) | (i) F1-NIV passes Holm with skill ≥ 2.0% while F1-price does not.<br>(ii) The single-regime route in §17.6 |
| 3 | **FAIL-negligible** | Holm rejection, but point skill < 0.5% |
| 4 | **INCONCLUSIVE** | No Holm rejection, and UB ≥ 2.0% |
| 5 | **FAIL** | No Holm rejection, and UB < 2.0% |
| — | **FAIL-BY-POWER** | INCONCLUSIVE at confirmation, and still INCONCLUSIVE after the single extension (α = 0.01) |

**Overall FAIL.** C1 and C2 are both FAIL (or FAIL-BY-POWER). That is a FAIL for the claim that "public NESO/NWP/REMIT information adds to the GB imbalance-price distribution at 2 h beyond B".

### 17.1 Stage 0 kills (metadata only, before any modelling) and the build gate

The operational definitions mirror §6.5 and are frozen in the Stage 0 plan before any count is computed.

| ID | Condition to pass | On failure |
|---|---|---|
| **k1 Coverage** | Each dataset has ≥95% of expected blobs in every month from D0 to 2026-08. Expected counts:<br>• DISEBSP ≥1 per SP;<br>• MID ≥1 APXMIDP per SP;<br>• WINDFOR 8 per day;<br>• INDDEM, MELNGC, LOLPDM 48 per day (46/50 on clock-change days);<br>• FUELINST 288 per day;<br>• TSDF, IMBALNGC: the median daily count over 2024-03 to 2025-02, fixed before any other month is counted, plus ≥1 on every day.<br>In addition, WINDFOR ≥6 publishes on ≥95% of days. D0 = the first qualifying month | D0 after 2024-02-11 → hybrid historical-plus-prospective confirmation.<br>D0 after 2025-03-01 → historical design killed: forward-capture for ≥12 months, or STOP |
| **k2 First-price timing** | First DISEBSP UploadTime ≤60 min after SP end, for ≥95% of SPs in every month used | In months before the first passing month, D0 moves. In a later month, **exclude the month** (rule below). If no dataset in R0-B's list has a near-real-time first message, the target definition is void |
| **k3 UploadTime is genuine** | Per dataset-month:<br>(i) blob creation time within 10 min of the UploadTime tag, for ≥99% of sampled blobs;<br>(ii) UploadTime − publishTime in [−1, 30] min, for ≥99% of WINDFOR, TSDF, INDDEM, MELNGC and IMBALNGC vintages;<br>(iii) ≤1% of blobs show a bulk-upload signature (≥1,000 blobs within 60 s whose publishTimes span >24 h).<br>**Fallback for (i):** if ≥90% of creation times for all months before some date fall within ±1 day, treat creation time as uninformative there. Rely on (ii), (iii), a <5 min shift in the median of (UploadTime − publishTime) across that date, and k4. Label those months "UploadTime genuineness unverifiable" | **Exclude the month** (rule below) |
| **k4 Live check** | Over 14 days of own capture, first-seen − UploadTime ≤5 min for ≥99% of messages | **Historical design killed** |
| **k5 Continuity across the August 2025 IRIS release** | 2025-07 to 2025-11 are each ≥95% complete (k1 definitions).<br>Median lag shifts by <5 min against 2025-06. Lag is defined as:<br>• UploadTime − publishTime for publishTime datasets;<br>• first UploadTime − SP end for DISEBSP and MID | **Exclude the month** (rule below) |
| **k6 F1 feasibility** | ≥2 distinct WINDFOR vintages between the reference time and t, on ≥90% of origins | C1 cannot be tested historically in GB |
| **k7 Licence** | The BMRS licence permits the research use | No run |
| **k8 Build gate** (not Stage 0; needs Exp 1 code, so only after approval) | Poisoning, truncation, vintage-swap and mutation tests pass on synthetic fixtures | No real-data modelling |

**Month-exclusion rule (k2, k3, k5 after D0).**
- A failing month is excluded for every arm.
- Batches are recomputed over the remaining consecutive days, with t critical values at the new degrees of freedom.
- If excluded days exceed 15% of confirmation (79 of 528 days), switch to hybrid confirmation.
- Among k2–k5, only k4 kills the historical design outright.

### 17.2 Rules applied before unsealing

- **F1 futility (discovery).**
  - Uses the 19-quantile, weekly-refit L, B+F1 against B, and 26 fourteen-day batches.
  - F1 is futile only if **all 6 F1 variants** have a one-sided 95% UB below 2.0%. C1 is then FAIL at discovery.
  - If, in addition, no F2–F8 family passes BH at q = 0.10 plus the placebo gate, the whole hypothesis FAILS and **confirmation is never unsealed**.
- **Placebo gate, per type.** Every passing family must clear all three (mirrors the §8.10 correction):
  1. **364-day shift:** a single draw; the real statistic must exceed it.
  2. **Whole-week circular shifts of ≥8 weeks:** all 37 admissible shifts; exact rank p = (1 + #≥real)/38 ≤ 0.05.
  3. **Block-shuffle within hour × month:** ≥99 draws; the real statistic must exceed their 95th percentile.
- **K-competence.**
  - In discovery, L(B) must beat the best of N1–N6 by ≥5% z-pinball.
  - If it does not, one ledgered repair round is allowed, drawn from a list fixed in the YAML before discovery is read. Proposed list (INFERENCE): make PN mandatory; add B+'s BOALF items to B; add the N4 and N5 forecasts as features.
  - If L(B) still fails, **STOP: "no competent public baseline"**.
  - The loader refuses to unseal until K-competence passes.
- **K-target-vintage.** If first-published and latest-run NIV disagree in sign on >5% of SPs, re-examine the target by a written rule before sealing. Checked on the discovery window only.
- **MDE rule.** Compute MDE_80 from the discovery standard error, scaled to 37 batches. The expected value is about 0.12–0.14 × r, where r = sd(daily differential) / mean(daily B loss).
  - If MDE_80 > 3.0%: first cut the Holm family to {F1-price}.
  - If it is still > 3.0%: defer Stage 2 until confirmation plus post-freeze prospective data reach ≥700 days.
- **Block length.** If the Politis-White block length exceeds 14 days, switch to 28-day batches: 18 batches, t(17).

### 17.3 INVALID RUN (no verdict for any claim)

Only mechanical, high-power checks are validity gates:
- any known_at violation;
- any poisoning, truncation-equivalence or vintage-swap test changes a forecast;
- the oracle-leak control scores < 20% skill;
- a planted synthetic X at **≥10% skill** is not detected at one-sided p ≤ 0.01 in the discovery pipeline;
- the +1-cycle future-vintage arm leaves forecasts unchanged, or the known_at contract fails to raise when the arm is run with the contract enabled;
- a planted-bug or mutation test fails to fail.

**Reported as power calibration, not gates:**
- the +1-cycle arm's *skill*;
- the recovery rate of a 2%-skill planted X.

Under a true null, a future wind vintage need not improve a price forecast, and 2% is at or below the MDE (1.2–3.2%). Gating on either would let a true null end INVALID instead of FAIL.

### 17.4 FAIL (per claim, precedence rows 3, 5 and FAIL-BY-POWER)

1. **Discovery:** C1 FAIL by F1 futility (§17.2).
2. **Confirmation** (37 batches, t(36)): a claim with no Holm rejection and UB < 2.0% is FAIL.
   - For C1, this kills the §4D revision thesis whatever C2 shows.
   - A surviving F7 is reported under C2 only, as "information, not revisions".
3. **FAIL-negligible:** Holm rejection, but point skill < 0.5%.
4. **FAIL-BY-POWER:** INCONCLUSIVE after the single pooled confirmation + post-freeze prospective test at α = 0.01. GB is not retested, and no new families are mined against these windows (K-thesis).

### 17.5 INCONCLUSIVE

No Holm rejection, and UB ≥ 2.0%. The only permitted action is the single pre-committed extension. It re-tests the INCONCLUSIVE Stage-2 hypotheses as one Holm family at α = 0.01.

### 17.6 INTERESTING (precedence rows 2 and 2′)

- **Holm-significant but not STRONG.**
  - Holm-adjusted p ≤ 0.04 and skill ≥ 0.5%, with a sub-label:
    - `-below-SESOI`: skill < 2.0% or UB < 2.0%;
    - `-unstable`: a stability gate fails (quarters, drop-5-days, £ scale, latest-run price, B+, coverage).
  - A result whose sign flips when the top 10 days are dropped is capped at INTERESTING.
- **C1, NIV route.** F1-NIV passes Holm (p ≤ 0.04) with skill ≥ 2.0%, while F1-price does not. Reading: the revision informs imbalance volume, but not price beyond BM-stack noise.
- **C1, single-regime route.** Applies to F1 as tested in Stage 2. The regimes are R1 (wind-share tercile), R2 (|F1| above the discovery 80th percentile) and R3 (target SP starting 16:00–19:30 Europe/London). Requires all of:
  - GW conditional test, Holm-adjusted across the 3 regimes, p ≤ 0.05;
  - the regime covers ≥ 20% of SPs;
  - regime skill ≥ 3.0%.

  This is a separate error family. It never supports STRONG.
- **Holm across routes.** All INTERESTING routes are Holm-corrected among themselves at α = 0.05, or labelled "exploratory, uncorrected" in `verdict.json`.

### 17.7 STRONG

**STRONG-provisional (confirmation), per claim, requires all of:**

| Gate | Threshold |
|---|---|
| (a) | Holm-adjusted one-sided p ≤ 0.04 on 37 batches, t(36). F1-price for C1; the family itself for C2 |
| (b) | L point skill ≥ 2.0% z-pinball |
| (c) | G skill ≥ 1.0%, same sign |
| (d) | Skill > 0 in ≥4 of 6 calendar quarters: Q2-2025 (April–June) through Q3-2026 (July–August only, partial). The leftover days 2025-03-22 → 03-31 are excluded |
| (e) | Skill ≥ 1.0% after dropping the 5 best days, and the top 10 days carry < 50% of the net gain |
| (f) | £-scale pinball skill > 0, one-sided unadjusted batch-means p < 0.10 |
| (g) | Skill ≥ 0 against the latest-run SSP from one REST snapshot on a fixed date ≥ 2026-10-15. **A gate, with its heterogeneity stated.** The snapshot mixes settlement runs across the window: early SPs sit at later reconciliation runs, late SPs at early runs (INFERENCE). REST has no run-type field (FACT: elexon-bmrs 0.3.0 `generated_models.py:593`, SystemPriceResponse). Skill that exists only against first-published prices and reverses against settled prices is a target-vintage artefact |
| (h) | Skill ≥ 1.0% against B+ (BOALF acceptances added) |
| (i) | Passes the per-type placebo gate (§17.2) and every §17.3 control |
| (j) | The best B+X model is at least as good as N1–N6, L(B) and G(B) on confirmation pooled z-pinball |
| (k) | Recalibrated 80% coverage within [0.75, 0.85] |
| (l) | Zero known_at violations; every PIT, poisoning and mutation test passes |

**STRONG-final** = STRONG-provisional, plus all of:
- ≥90 prospective days **after P** with skill ≥ 0, and L and G agreeing in sign;
- if the extension was used, pooled p ≤ 0.01.

**Operating characteristics of the prospective check** (INFERENCE: normal approximation, scaling the 37-batch MDE_80 of 1.2–3.2% to 90 days):
- it passes about 50% of the time under the null, and about 80–99% under a true 2.5% effect;
- it is a sign-replication check, not a test. Error control comes from the confirmation Holm test.

**Chronos-2 sophistication comparison.** Gates on post-freeze prospective days only; §8.14 governs any report on confirmation days. A margin under 5% is pre-registered as "no evidence that sophistication matters".

**Mechanism label** (rung 4, applied, not a gate):
- "Market channel" if F1 skill against B+W\* is ≥ 1.0% with one-sided p < 0.10.
- Otherwise "physical / forecast-combination channel".
- Only the market-channel label supports the brief's §4D claim that the revision itself carries market-moving information.

### 17.8 PRODUCT SIGNAL

**[v2: moved out of Experiment 1, to the commercial track and Exps 2–4. Kept here as the 1B economic reporting spec. See addendum point 1.]**

**All** of the following:

1. **STRONG-final on C1** (a pre-registered F1 or revision family). The market-channel label is required for any claim that the product is about "revisions". A C2-only STRONG-final supports at most a "feed validation" pitch, never a "revisions" pitch.
2. **Economic check** under the §12 rule. The rule: ±0.5 MWh when |q50 − MID_ref| > £5/MWh, with L supplying q50; flat when MID is missing or has zero volume; prospective settled price at s + 30 days. Requirements:
   - incremental P&L (B+X minus B) > 0 at £3/MWh under both execution variants **[v2: variant B only gates]**;
   - 14-day block-bootstrap 90% lower bound > 0 under variant B (P_exec = MID_ref);
   - B+X P&L exceeds the larger of the always-long and always-short controls;
   - deflated-Sharpe probability ≥ 0.95, with N from the ledger;
   - the top 10 days carry < 50% of the incremental P&L.
3. **User validation.** At least 3 of 10 structured calls:
   - name an existing budget line of ≥ £10k/yr for independent, vintage-correct validation; and
   - confirm they run no *equivalent* in-house ablation, meaning an out-of-sample nested ablation on issue-time-stamped vintages for the same target class.

   At least 1 commits to a paid pilot, or to sharing its baseline under NDA.
4. **Professional-baseline check** (descriptive). F1 skill stays ≥ 1.0% after the latest vendor wind instance level known at t is added to B, on ≥ 30 prospective days. The vendor is EQ or Volue under a trial. The trial terms and GB wind coverage are UNKNOWN (checked in R1). The EQ free tier covers the last 30 days only (FACT).
5. **Licence.** The BMRS licence text permits the intended commercial use and the redistribution of derived vintage evidence (K-licence).

---

## 18. Build plan

**[v2: this is the 1B plan. The primary 1A build order and the Exp 2–4 roadmap are in condensed memo v2 §18.]**

**Status.** The recommendation is RESEARCH MORE BEFORE CODING (§20). No build is proposed; this section is the **research-before-coding plan**.

**Stage 0 scope:**
- About 5–7 person-days of audit effort for k1–k7, plus about 2–3.5 days of supporting items.
- The decision gate falls at least 15 calendar days after IRIS registration.
- Every item runs only after user approval, including the recorder and the artifact download.
- Outputs go to the scratchpad or elsewhere outside the repository, never to `main`.
- No Experiment 1 code is written.

### 18.1 Precondition

An environment with egress to:
- `archive.data.elexon.co.uk` and `data.elexon.co.uk`;
- `api.neso.energy` / `www.neso.energy`;
- `www.gov.uk`;
- the Elexon licence pages.

All of these returned CONNECT 403 here (FACT: re-probed 2026-09-23). Without that egress, none of the go/no-go facts can be checked. **Owner: the user.** Either add the hosts to this cloud environment's allowlist, or run Claude Code locally.

### 18.2 Work items

| ID | Owner | Item | Pass rule | If it fails | Effort (INFERENCE) |
|---|---|---|---|---|---|
| R0-A | Claude | **IRIS coverage.** For DISEBSP, WINDFOR, NDF, TSDF, INDGEN, INDDEM, IMBALNGC, MELNGC, LOLPDM, MID, FUELINST, INDO, ITSDO, FREQ, REMIT, PN and BOALF: earliest blob, and monthly blob counts against the §17.1 expected counts, 2023-01 to 2026-09. Tags only in the confirmation window | k1 | D0 slip rules (§17.1) | 1–2 d |
| R0-B | Claude | **First-price timing and run identity.**<br>1. List every IRIS dataset that could carry a near-real-time price or NIV: the createdDateTime group, i.e. BOAV, DISEBSP, DISPTAV ("Indicative Volumes"), EBOCF ("Indicative Cashflows"), ISPSTACK and SMSG (FACT: `dataset_and_timestamp_reference.md:14-20`).<br>2. For each, by month: the distribution of first UploadTime − SP end, from tags.<br>3. Identify DISEBSP's run by comparing it with REST latest-run values, **on a discovery-window sample only**.<br>DISPTAV, EBOCF, ISPSTACK and BOAV stay on the feature denylist; they are read here only to date the indicative calculation.<br>**Evidence either way:**<br>• *Toward the risk (FACT):* REST describes the prices as SAA output "relating to the data for a settlement run" and returns "only messages generated for the latest settlement run" (elexonpy 1.0.16 `indicative_imbalance_settlement_api.py:1566, :1665`). B1610 II-run data is "published five days after the end of the operational period" (elexon-bmrs 0.3.0 `generated_client.py:7726`). That DISEBSP's II run has the same timing is INFERENCE.<br>• *Against the risk (weak):* DISEBSP's IRIS grouping with "Indicative" datasets (weak INFERENCE toward near-real-time). A reported "about 15 min after the SP" (UNVERIFIED: search summary) | k2 | D0 moves or months are excluded (§17.1). If no dataset in the list shows a first message ≤60 min after SP end, B's lagged price and NIV features never existed in real time: **the design collapses** | 1 d |
| R0-C | Claude | **Is UploadTime genuine?** Per dataset-month, compare blob `x-ms-creation-time`, the UploadTime tag ("the time when the blob was uploaded to IRIS", FACT: `iris_archive.md:40`), blob-name time, and publishTime/Timestamp. Screen for bulk-upload signatures. Run a changepoint check over the August 2025 IRIS release: "all users must re-register … before 2 October 2025 … old queues … deleted" (FACT: `iris-clients` README). Whether the archive's uploader changed is INFERENCE. Apply the k3 creation-time fallback. **Confirmation window: key fields only, never value fields** | k3, k5 | Months excluded; over 15% excluded → hybrid | 1–2 d |
| R0-D | **User** (register for IRIS in their own name; run Elexon's stock client on a VM); Claude (metadata analysis) | **Live check.** Capture for 14 days. Compare first-seen time with UploadTime and publishTime. Resolve the WINDFOR publish timezone. Captured values are treated as sealed (pre-freeze holdout) | k4 | Historical design killed | 0.5 d setup + 14 d elapsed |
| R0-E | Claude | **Cadence and position data.**<br>• Vintages per target SP for NDF, TSDF, IMBALNGC, INDGEN, INDDEM and MELNGC in the 6 h before t.<br>• PN blob granularity and volume.<br>• BMU→fuel mapping: UOU2T14D coverage of wind BMUs, compared with `/reference/bmunits/all`, which is a current list only (§6.1).<br>• MID first-upload latency | k6; F3/F4 collapse rules; the PN-optional rule; the MID drop rule (>60 min on >5% of SPs) | Families collapse or drop by the pre-registered rule; wind-only PN falls back as in §6.2 | 1 d |
| R0-F | Claude | **Target vintage (discovery window only).** How often, and by how much, first-published SSP and NIV differ from latest-run values; the share of NIV sign flips | K-target-vintage (>5% flips → written re-examination rule) | Target re-examined before sealing | 0.5 d |
| R0-G | Claude | **NESO historic day-ahead wind forecast archive** (from 2018, UNVERIFIED search summary: `neso.energy/data-portal/day-ahead-wind-forecast/historic_day_ahead_wind_forecasts`). Does each row carry an issue time? | An issue-time column exists and matches WINDFOR publishTime vintages | Used as an independent k3 cross-check, and as a fallback history if IRIS starts late. If it has no issue time, record it as unusable | 0.5 d |
| R1 | Claude (reading) | **Licences and terms.** BMRS data licence (commercial use, redistribution of archived vintages, attribution); NESO Open Data Licence; ECMWF CC BY 4.0 attribution; Chronos-2 weights licence and pretraining corpus/cutoff; EQ/Volue trial terms and GB wind coverage | k7; K-licence | No run (k7), or the product path is killed (K-licence) | 0.5 d |
| R2 | Claude | **Regime inventory.** From the BSC modification register, every modification that changed imbalance-price derivation and took effect 2023-06 to 2026-08, with dates | Complete list | Break markers are pre-registered with the gap disclosed | 0.5 d |
| R3 | Claude | **F6/F8 feasibility.**<br>• *F6 capacity map:* IGCPU is unusable (synthetic publishTime 2023-01-01, no coordinates; FACT: elexon-bmrs 0.3.0 docstring and `IgcpuDatasetRow`). The third-party `geoffhancock/neso-wind-forecast-archive` holds per-windfarm capacity, forecast MW and region. Per its README, NESO publishes "only as a rolling snapshot (no historical archive)", archived once daily at 06:00 UTC (FACT: README, read this pass; example file dated 2026-04-11). That makes it a **prospective-only** capacity map, holding one of about 8 daily vintages.<br>• *F8:* NESO embedded-forecast archives with per-row issue timestamps | A vintaged source is found and verified | F6 uses equal-weight boxes historically; F8 is dropped and the drop recorded in the ledger | 0.5–1 d |
| R4 | **User** | **Buyer discovery.** ≤10 calls (§13.8); Claude drafts the script and synthesises notes | PRODUCT SIGNAL user-validation thresholds | The commercial path is parked; the science can proceed | 2–3 d of the user's time over about 2 weeks |
| R5 | Claude | **Fallback, only if GB fails Stage 0.** One-day ERCOT probe: earliest postDatetime for NP4-732-CD, NP4-737-CD and NP3-565-CD; real-time price history; the RTC+B break (data from 2025-12-06). FACT for the mechanism: gridstatus `ercot_api.py:435-443, 1044-1048` | ≥2 years of point-in-time history | Forward-capture for ≥12 months, or STOP | 1 d |
| R6 | **User approves**; Claude can download to a location the user names, outside the repo | **Housekeeping, deadline 2026-10-13.** Download the run #11 artifact `results-full-11` (forecasts parquet) to durable storage, with its sha256 | Artifact saved with sha256 | The only complete per-row record of Exp 0's canonical run is lost | 0.25 d |
| R7 | Claude | **Persist the methodology simulations** (§1): code, seed and data-generating process, in the scratchpad | Reproducible numbers | Simulation numbers stay labelled "unpersisted" | 0.5–1 d |

### 18.3 Sequencing (elapsed days from approval)

| When | Items |
|---|---|
| Day 0 | **User:** grants egress; registers for IRIS and starts the stock client, which starts the k4 clock; approves R6 (deadline 2026-10-13) |
| Days 1–7 | R6 first; R0-A, R0-B, R0-C, R0-E, R0-F, R0-G; R1; R7. The user schedules the R4 calls |
| Days 5–14 | R2, R3; R4 calls continue |
| Day ≥15 | R0-D completes → decision gate (§18.4) |

**Timing note (INFERENCE).**
- The recorder running from 2026-10-01 gives an **audit trail only** (an UploadTime cross-audit). It gives no prospective evidence.
- Prospective evidence starts at P + 1 day (§17.0).
- Starting the recorder late loses no prospective evidence. The archive supplies the values, and the recorder's role is the independent timing audit.

### 18.4 Decision gate at the end of Stage 0

The deliverable is a go/no-go table against k1–k7, with: the measured D0; excluded months; the R0-B dataset timing table; the licence text; the call results; and the branch taken.

- **k1–k7 pass, D0 ≤ 2024-02-11, excluded confirmation days ≤ 15%** → present the frozen Experiment 1 plan (this memo, with the Stage 0 numbers substituted) for **explicit approval**. No code before approval.
- **D0 after 2024-02-11 and on or before 2025-03-01, or excluded confirmation days > 15%** → hybrid confirmation (historical remainder plus post-freeze prospective until ≥365 days); re-present the plan.
- **k2, k3 or k5 fail in individual months after D0** → exclude those months and recompute batches (§17.1). This is not a design kill.
- **D0 after 2025-03-01, or k4 fails, or R0-B finds no near-real-time price dataset** → run R5, then forward-capture for ≥12 months, or STOP.
- **k6 fails** → C1 cannot be tested historically in GB. Run R5, or STOP.
- **k7 fails** → no run.

### 18.5 Contingent build order (not authorised; only after Stage 0 passes and the user approves)

1. Recorder (component 1), writing into the sealed store. Values stay unreadable until P.
2. Raw store, vintage table, as-of builder, and point-in-time tests on fixtures. **k8 is evaluated here, before any real data is modelled.** It is the only kill criterion that needs code.
3. Target builder, naive baselines, and the discovery competence check (K-competence, one ledgered repair round at most).
4. L and G; Stage 1; per-type placebos; the §17.3 controls.
5. Freeze the pre-registration and seal: the hash is committed and tagged. **This date is P.**
6. Stage 2 (confirmation, once).
7. Prospective window from P + 1 day; STRONG-final at P + 90 days at the earliest; the economic check; buyer-call synthesis.

---

## 19. Open questions

| # | Question | Why it matters | Resolved by | Decisive? |
|---|---|---|---|---|
| 1 | Is the first DISEBSP message per SP a near-real-time indicative price, or a settlement run days later? If near-real-time, since when? Does any other createdDateTime-group dataset (DISPTAV, EBOCF, ISPSTACK, BOAV) carry an earlier indicative calculation? | Decides whether B's lagged price and NIV features ever existed in real time. UNKNOWN; the evidence points both ways:<br>• toward the risk: SAA "settlement run" wording and latest-run-only REST (FACT: elexonpy `indicative_imbalance_settlement_api.py:1566, :1665`);<br>• against it: the "Indicative" IRIS grouping (weak INFERENCE) and "about 15 min" (UNVERIFIED) | R0-B | **Yes** |
| 2 | When does the IRIS archive start, dataset by dataset? How complete is it? Does UploadTime reflect original first availability, including across the August 2025 IRIS release? | The whole historical design rests on it.<br>• Doc examples are dated only 2023-06-18 and 2023-11-14 (FACT: `iris_archive.md`).<br>• The August 2025 release required re-registration and deleted old queues (FACT: iris-clients README).<br>• Any archive change is INFERENCE | R0-A, R0-C, R0-D, R0-G | **Yes** |
| 3 | How often are NDF, TSDF, IMBALNGC and INDGEN actually published? The docs say both "daily" and "30 minutes". What timezone do WINDFOR publish times use? | F3/F4 may collapse to daily. IMBALNGC may be up to about 24 h stale, which weakens B (FACT: the docstrings conflict, elexonpy `datasets_api.py`) | R0-E, R0-D | Partly |
| 4 | How often, and by how much, do first-published SSP and NIV differ from latest-run values? Do the differences correlate with wind or stress regimes? | A target-vintage artefact could be read as signal; gate (g) depends on it | R0-F | Partly |
| 5 | How are imbalance-price loss differentials distributed, and how dependent are they? Exp 0's solar daily lag-1 ACF was −0.04 to 0.20 and may not transfer | Determines the real MDE (ex ante about 1.2–3.2% over 37 batches, INFERENCE) | Discovery standard error, before unsealing | For power |
| 6 | If F1 shows skill, is it forecast combination (NESO's latest wind forecast can be improved) or a market channel (positioning on stale vintages)? | Separates rung 3 from a rung-4 market-channel label | Mediation arm (B+W\*, physical target) | For interpretation |
| 7 | Which BSC modifications or NESO process changes between 2023 and 2026 changed price derivation or WINDFOR coverage? | Undetected breaks can fail a real signal or create a spurious one | R2 | No |
| 8 | What does the BMRS licence allow: commercial use, and redistribution of derived vintage evidence? | k7; K-licence; the product path | R1 | For the product path |
| 9 | Would any professional buyer share baseline forecasts under NDA, or run an on-premise harness? | Without that, "incremental beyond a professional baseline" cannot be measured | R4 (user) | For the product path |
| 10 | Does a GB result transfer to coupled EU markets? The Belgian replication tests only fixed vintages | External validity | Not resolvable in Exp 1 | No |
| 11 | Would BSC or Ofgem accept deliberate imbalance positioning? | Realism of the economic check (UNKNOWN) | Regulatory reading | No |
| 12 | How deep is ERCOT's postDatetime archive? Would ERCOT be a better PIT domain than GB if GB fails? | Fallback domain | R5, only if GB fails | Conditional |
| 13 | Is Chronos-2's pretraining cutoff after 2023 GB data, and what licence covers its weights? | Contamination labelling; the sophistication comparison | R1 | No |
| 14 | Is there a vintaged BMU→fuel mapping? Does UOU2T14D cover every wind BMU? | Wind-only PN in B; a poorly mapped B item could inflate F1 skill (INFERENCE; §6.1) | R0-E | Partly (PN may be optional) |
| 15 | Does NESO's historic day-ahead wind archive carry per-row issue times? | An independent k3 cross-check, and a fallback history if IRIS starts late | R0-G | No |
| 16 | When will P fall, and will ≥90 post-freeze days fit before any structural break (for example new BSC modifications in 2027)? | STRONG-final timing (March–April 2027 plausible, INFERENCE) | Build progress; R2 | No |

---

## 20. Final recommendation

**[v2: superseded by addendum point 6. The v1 text below is the 1B recommendation, and it still stands for 1B.]**

**RESEARCH MORE BEFORE CODING.** This is neither STOP nor BUILD. Scope it as a bounded Stage 0: read-only metadata audits and licence reading, plus buyer calls run by the user. It takes about 5–7 person-days of audit effort for k1–k7 (plus about 2–3.5 days of supporting items). Its decision gate falls **at least 15 calendar days after IRIS registration**, because k4 needs a 14-day live capture.

**Why not BUILD.** GB is the only market examined where the test can be point-in-time from free data. The chosen design, GB-IMB-2H-H, rests on three facts that cannot be verified from this environment. `archive.data.elexon.co.uk`, `data.elexon.co.uk` and `api.neso.energy` returned CONNECT 403 on 2026-09-23 (FACT).

1. **Archive start and completeness per dataset** (UNKNOWN).
2. **Whether the first DISEBSP message per SP is a near-real-time indicative price** (UNKNOWN).
   - *Toward the risk.* REST describes the prices as SAA output "relating to the data for a settlement run", and returns "only messages generated for the latest settlement run" (FACT: elexonpy 1.0.16 `indicative_imbalance_settlement_api.py:1566, :1665`).
   - *Against it, weakly.* In IRIS, DISEBSP shares the createdDateTime group with "Indicative Volumes" and "Indicative Cashflows" (FACT: `dataset_and_timestamp_reference.md:14-20`; weak INFERENCE toward near-real-time).
   - *Stakes.* If the first message is a run days later, the baseline's lagged price features never existed in real time and the design collapses.
3. **Whether UploadTime tags are genuine first-availability times.**
   - The tag-query examples are dated 2025-04-14 (FACT).
   - The August 2025 IRIS release falls inside the confirmation window (FACT). Whether the archive changed with it is INFERENCE.

Verifiers also contradicted four data claims in the candidate designs:
- the NDF/TSDF "30-minute" cadence;
- 100 m wind and SSRD before 2024-03-06;
- the 0.25° grid date, which is 2024-02-01;
- the 06/18z stream name, which changes from `scda` to `oper` on 2026-05-12.

They also found IGCPU history carrying a synthetic publishTime of 2023-01-01 (FACT). Building on unverified timing semantics would repeat Exp 0's silent assumptions: zero publication delay, a definitive vintage, and a single `fetched_at`.

**Why not STOP.**
- The narrow core is credible and costs £0 in data. The narrow core asks: does one pre-registered, point-in-time-verified public forecast-revision family add *incremental predictive information* (rung 3) to one fast-resolving market variable, beyond a strong baseline?
- A FAIL or FAIL-BY-POWER would end this narrow GB public-data version.
- INCONCLUSIVE has material probability: the plausible effect is 1–3% against an MDE of 1.2–3.2%.
- No result transfers to other markets or to richer information sets (INFERENCE).

**What is already decided.**
- **DE-LU, the user's first hypothesis: STOP for that version.** **[v2: Exp 1 scope; free historical test only.]**
  - TSO revision vintages cannot be reconstructed. ENTSO-E serves the latest version only (INFERENCE, strongly supported), and netztransparenz prognose ended 2022-12-15 (FACT: client code).
  - The target and baseline are paid EPEX data for internal use only (academic €480/yr, non-transferable; FACT per decision record).
  - The only historically timestamped open NWP copy, the AWS mirror, shows LastModified 6.45–8.57 h after init (FACT; ECMWF portal release time UNKNOWN). Its expected null therefore cannot be interpreted.
- **The broad thesis is not credible as stated.** **[v2: reframed; see addendum point 4. The principles bind the product, and the magnitudes are Exp 1 scope.]**
  - Lag and regime are not identifiable at 1–3% effects. SIMULATION (unpersisted): a 33% wrong-lag rate, and a true 2.5% effect confirmed only 13–14% of the time with 1 year of data.
  - Exp 0's pooled-skill CIs of about ±2–5 points on 363 days make the same point without the simulation (FACT: run11).
  - Discovery at scale uses up the holdout.
  - "Currently leading" cannot be certified.
  - Public data can establish only "beyond public information". **[v2: Exp 1 scope.]**
- **Every claim is labelled.**
  - Experiment 1 tests only rung 3.
  - It emits separate verdicts for C1 (the §4D wind-revision thesis) and C2 (other public information), under a fixed precedence table (§17.0).
  - It attaches a rung-4 mechanism label from the mediation arm, and never claims rung 5.
  - Rungs 1–2 are reported descriptively.
- **t0 is not relevant.**
  - It lost by −9.0% [−13.8, −4.3] against blend_50 in Exp 0.
  - t0-alpha clamps quantiles to 0.1–0.9.
  - There is no intraday or imbalance evidence for it.
  - The instrument of record is a classical nested linear quantile model (L), corroborated by LightGBM (G). Chronos-2 is used only for the pre-declared sophistication question.
- **Commercially, the thesis is the weakest link.** **[v2: Exp 1 scope. This applies to a stand-alone tool, not to the AI-researcher product.]**
  - Vintage queries, PIT backtesting and in-sample lead/lag explanations are commoditised (FACT: EQ and Volue clients, OpenSTEF 4.4.3, nixtla 0.9.0).
  - For GB, the moat reduces to an audited live track record plus the method.
  - The likely ceiling is consulting-sized (INFERENCE).
- **Calendar.** Counted from the freeze date P, the earliest STRONG-final is plausibly March–April 2027 (INFERENCE, §16.5), not January 2027.

**Condition for BUILD.**
1. Stage 0 passes k1–k7 (§17.1), with no Exp 1 code.
2. The user explicitly approves the frozen Experiment 1 plan.
3. k8 passes on synthetic fixtures as the first gate of the build, before any real data is modelled.

Nothing is implemented before that approval.

**Process disclosure** (full list in §1):
- **Files still present.** Thirteen third-party files were written to the scratchpad after the brief was saved (`exp1_brief.md`, 2026-09-23 09:00:32 UTC). They existed when this memo was written; since deleted:
  - `_entsoe_py.txt` and `_entsoe_parsers.txt`;
  - `_smard_openapi.yaml` and `_smard_README.md`;
  - `_jao_readme.md`, `_jao_jao.py`, `_jao_publicationtool.py` and `_jao___init__.py`;
  - `_obsyd_README.md`, `_obsyd_data-sources.md`, `_obsyd_DATA_SOURCES.md`, `_obsyd_LICENSES.md` and `_obsyd_NOTICE.md`.

  **Update after the workflow:** the main session has since deleted all thirteen. They were scratch copies of public third-party files and were never in the repository.
- **Files created and deleted in the same session:** gridstatus `ercot_api.py`, `_prior_dump.txt`, `_ukspf_readme.md` and `_uwf_view.txt`.
- **Earlier phases.** Files from earlier research phases are listed in §1; whether those phases permitted scratchpad writes is UNKNOWN.
- **This revision pass wrote nothing.** Remote documents were read to stdout only.
- **The repository is untouched:** `406c92c`, clean working tree (FACT: `git status`, this pass).

**Deadline alongside the next action.** Separately, the user should approve R6 before **2026-10-13**: download the run #11 artifact `results-full-11` to durable storage outside the repo. After that date, the only complete per-row record of Exp 0's canonical run is lost.

**Single next action.** Give Claude Code network access to `archive.data.elexon.co.uk` and `data.elexon.co.uk`, either by adding both hosts to this cloud environment's network allowlist or by running Claude Code locally. Then ask it to run a read-only Stage 0 metadata audit of the Elexon IRIS archive:

- **Scope:** DISEBSP, WINDFOR, NDF, TSDF, IMBALNGC, INDGEN, INDDEM, MELNGC, LOLPDM, MID, FUELINST, INDO, ITSDO, FREQ, PN, BOALF and REMIT, plus the createdDateTime group (DISPTAV, EBOCF, ISPSTACK, BOAV) for price timing only. Period 2023-01 to 2026-09.
- **Writes:** scratchpad only, with no repository changes.
- **Report 1:** earliest blob, and monthly blob counts against the §17.1 expected counts.
- **Report 2:** by month and dataset, the first UploadTime per SP minus SP end.
- **Report 3:** UploadTime against blob `x-ms-creation-time` and against publishTime/Timestamp, including August–November 2025.
- **Rule:** key fields only for confirmation-window payloads, never value fields.
- **Deliverable:** a go/no-go table against k1–k3 and k5–k6.