# Experiment 5: the researcher's proposal

*Section 2 is the AI researcher's answer, rendered mechanically from its recorded output with no edits. Sections 1
and 3 are written by the engineering orchestrator and are not the researcher's. Nothing here has been run or
frozen.*

## 1. Provenance (orchestrator)

**The call:**
- Run [36855466970](https://github.com/xuanhuyle/solar/actions/runs/36855466970) of `engine.yml` in mode
  `propose`, at commit `b13e596`.
- Recorded on the engine ledger (branch `engine-ledger`):
  - **seq 73:** the automatic `config` entry for the changed engine code;
  - **seq 74:** the `research_call`.
- The chain was verified afterwards: head seq 74, entry sha256 `589109b8…3b35`.

**How it went:**
- One request: attempt 1, no transient retry, no repair round; stop reason `end_turn`.
- Answer: **propose**.
- Effort setting: high.
- **Usage:**
  - input: 104,312 tokens;
  - output: 21,829 tokens;
  - cache writes: 6,619 tokens;
  - cache reads: 0.
- **Model identity:** recorded on the ledger at seq 74 (`requested_model`, `served_model`; they are equal). It is
  not written in this repository's documents.

**Checks made after the call:**

| Check | Result |
|---|---|
| `researcher_output.json` against the ledger's `response_text` | identical, sha256 `3a6b662b…d503` |
| `evidence_pack_sha256` against the committed `evidence_pack.json` | identical, `64e93aaf…3cdd` |
| `system_sha256` against `propose.system_text()` | identical, `29b8b29b…fc04` |
| `proposal_rules_sha256` and `schema_sha256` against the code | identical, `5cc6c446…` and `cf2ecda7…` |
| Recorded `user_prompt` against `propose.user_prompt(pack)` | identical |
| Evidence ids cited | 57 distinct ids, all present in the pack |
| `propose.validate_proposal` (schema, at most 3 candidates, ids, consistency, lengths) | no errors |

**To reproduce these checks:**
```
git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
python docs/experiment_5/render_researcher_docs.py --run-id 36855466970
git diff --exit-code docs/experiment_5
```

What the researcher received is in [`RESEARCHER_BRIEF.md`](RESEARCHER_BRIEF.md) and
[`brief_appendix.md`](brief_appendix.md).

## 2. The researcher's answer (verbatim rendering)

The rendering follows the answer's own field order. Field names are the schema's. Section C lists candidate
ids (I1–I3), which are the researcher's labels. The JSON is [`researcher_output.json`](researcher_output.json).

<!-- researcher-output:begin (written by render_researcher_docs.py; do not edit) -->

### Action

propose

### Summary

The only confirmed finding is C1: t0 plus holidays beats blend_50 on consumption. Every covariate gain so far, including the +19% from temperature behind batch B1, has been measured only against t0 without that covariate. On solar, a one-line model using the same weather beat t0+weather by 24%. I propose I1, a bounded exploratory test on 2024-05..2025-12 consumption data. It asks whether passing temperature through t0's known-future covariate channel beats a pre-specified linear post-hoc temperature correction of the same t0+holiday forecast. An oracle-temperature diagnostic separates forecast staleness from how well t0 uses the input. It leaves B1 untouched and cannot confirm anything.

### A. What I believe I have learned

- **finding:** On French national consumption, t0 with the holiday calendar cut day-ahead MAE against blend_50 by more than 25% on sealed 2025 data (skill +46.3%, one-sided 95% lower bound +42.0%). Three limits apply: RTE's weather-driven forecast was still 23% better, the calendar's own contribution was not tested in 2025, and the 2025 rows were consolidated rather than definitive.
  - **status:** confirmed
  - **evidence_ids:**
    - C1-CONFIRMATION
    - L9
    - L8
    - R-C1-4
    - L14
    - L15
- **finding:** Zero-shot t0 on solar, using history only, is indistinguishable from smoothed historical baselines in daylight (vs blend_50 -0.1% [-4.9, +4.5]). Over all hours it is worse (-9.0% [-13.8, -4.3]) because it forecasts a night floor; night-zeroing makes it indistinguishable from blend_50. It extracts roughly what a 7-day same-slot mean extracts.
  - **status:** exploratory
  - **evidence_ids:**
    - R-EXP0-1
    - R-EXP0-0
    - L2
- **finding:** An archived lead-3 irradiance forecast given to t0 cuts solar MAE by 25.6% [21.6, 29.6] against t0 alone. However, the no-t0 ratio model wx_ratio, built from the same forecast, is better still: t0+weather is 23.8% worse. Replacing the forecast with ERA5 improves t0 by only about 6%, which points to how t0 uses the input rather than to forecast quality. Evidence is from Jun–Dec 2024 only, not independently verified.
  - **status:** exploratory
  - **evidence_ids:**
    - R-COV-2
    - L3
- **finding:** Several solar probes found no value or lost. Solar geometry adds nothing to t0 (-0.3%). t0's solar quantile bands lose to simple empirical bands (pinball -34%, coverage 57%). t0 correcting wx_ratio's residuals adds nothing (-3.8%). Forecasting the 12 regions jointly ties ewma, and the joint-attention component adds +0.1% over independent forecasts.
  - **status:** negative
  - **evidence_ids:**
    - R-COV-2
    - L3
    - L4
    - L5
    - L6
    - R-EXP3-3
- **finding:** Calendar covariates contribute little on consumption beyond t0's own history: holidays +4.5% [-1.7, +8.4] in 2024, and bridge days -5.1% [-7.8, -2.1] against the accepted arm in 2024. Almost all of C1's gain comes from t0 reading the load history.
  - **status:** negative
  - **evidence_ids:**
    - R-EXP3-3
    - L7
    - L33
    - R-C1-4
- **finding:** Adding a raw archived lead-3 temperature forecast to t0+holiday on consumption cut MAE against the C1 arm by +19.3% [14.9, 23.7] over 602 days, +11.1% in summer and +24.4% in winter. Heating-degree encodings were no better than raw temperature. The arm was selected on these same 2024–2025 data, and per-year stability was not checked by the referee. It is frozen as B1, awaiting a forward-vault verdict after 2027-04-01.
  - **status:** exploratory
  - **evidence_ids:**
    - L51
    - L54
    - L69
    - L55
    - L56
    - R-ENGINE-6
- **finding:** Against RTE's day-ahead forecast (a reference only; its issue time is unverified), the temperature arm trails by 26% in winter and leads by 31% in summer; all-year it is level.
  - **status:** uncertain
  - **evidence_ids:**
    - L60
    - L63
    - L66
- **finding:** On French day-ahead prices (pre-registered, discovery grade, statistics independently reproduced), t0+holiday beats the best simple rule by +22.7% [18.6, 25.9]. Its native bands beat empirical bands (pinball +25.2%) with 73% coverage of the 10–90 band. Both results hold in each year.
  - **status:** exploratory
  - **evidence_ids:**
    - X4-P1
    - X4-P3
    - X4-READING
    - X4-REPLICATION
    - X4-SLICES-P1
    - X4-TABLES-P1
- **finding:** Public temperature and sunshine forecasts add only +2.8% [1.1, 4.4] to t0 on prices. The gain is concentrated: the best 20 of 572 days carry 83% of it. It is indistinguishable from zero in April–September and is not a vault candidate.
  - **status:** exploratory
  - **evidence_ids:**
    - X4-P4
    - X4-TABLES-P4
    - X4-SLICES-P4
    - X4-REPLICATION
- **finding:** On prices, much of t0's skill comes from the already-published D-1 afternoon prices, worth +17.1% to t0. Held to the strict information set, t0 still beats the best simple rule by +6.8% (+15.3% when the rule is held to the same strict set).
  - **status:** exploratory
  - **evidence_ids:**
    - X4-STRICT
    - X4-SECONDARIES
- **finding:** No comparison with a strong statistical price model has been made: the LEAR reproduction gate K1 failed on all three attempts, so P2 was not runnable.
  - **status:** uncertain
  - **evidence_ids:**
    - X4-K1
    - X4-P2
    - X4-A1
- **finding:** Known-answer tests show the covariate plumbing is aligned and leak-free, but t0 recovers only part of a planted signal. The planted-to-base error ratio varies: 0.86 in the covariate slice, 0.59–0.65 for solar radiation, 0.77–0.91 for consumption temperature, about 0.30 for prices. What governs t0's covariate uptake is unknown.
  - **status:** uncertain
  - **evidence_ids:**
    - R-COV-2
    - L18
    - L26
    - L17
    - L25
    - L36
    - X4-RUN
- **finding:** Past-only covariates have never been tested. In the pinned package, extra context rows passed through predict() become co-targets. Known-future covariates are standardised over the whole context-plus-horizon span and read bidirectionally.
  - **status:** uncertain
  - **evidence_ids:**
    - INFRA-T0
    - L6

### B. What remains unexplained

- **issue:** Every covariate gain on consumption has been measured only against t0 without that covariate. No simple model using the same temperature forecast has been compared, unlike solar, where such a model (wx_ratio) beat t0+covariate by 24%.
  - **why_it_matters:** There are two possible readings. One: temperature is valuable information and t0's covariate channel exploits it well. Two: temperature is valuable, but t0 underuses it, as it did with irradiance on solar. B1's eventual verdict cannot separate these, and the project's core idea (information delivered through t0's covariates) depends on which is true.
  - **evidence_ids:**
    - L51
    - L56
    - R-COV-2
    - L3
    - L5
    - INFRA-ENGINE-CATALOGUE
- **issue:** The temperature arm trails RTE by about 26% in winter, the season where temperature helps most against C1.
  - **why_it_matters:** There are four competing causes: the temperature forecast is 3 days old (INFRA-DATA), the 12-point spatial model is crude, t0 maps covariates weakly or too linearly, or RTE has information we do not. These imply different next steps: better data, a better instrument, or a hybrid model.
  - **evidence_ids:**
    - L63
    - L69
    - INFRA-DATA
    - R-COV-2
- **issue:** Planted-signal uptake ratios differ widely across targets and periods (0.30 to 0.91).
  - **why_it_matters:** It is unknown whether t0's covariate use depends on the target's history structure, the covariate's scale, or the noise level. That determines where covariates are worth trying through t0.
  - **evidence_ids:**
    - R-COV-2
    - L17
    - L18
    - L25
    - L26
    - L36
    - L37
    - X4-RUN
- **issue:** The temperature gain was never checked separately in 2024 and 2025 by the referee; only an unofficial winter split exists.
  - **why_it_matters:** Selection and evaluation used the same days. This is a data-snooping risk for interpreting B1.
  - **evidence_ids:**
    - L55
    - R-ENGINE-6
    - L69
- **issue:** Weather adds little to t0 on prices, and the inputs omit the main fundamental drivers: wind generation and load forecasts.
  - **why_it_matters:** A small P4 could mean public weather carries little price information, or that the wrong variables were supplied. The German 51% result in t0's report used load, wind and solar forecasts whose issue time is unverified.
  - **evidence_ids:**
    - X4-P4
    - X4-TABLES-P4
    - T0-REPORT
    - X4-SPEC
- **issue:** The engine still loads t0 by a revision id that vanished upstream, so engine probes, and B1's vault scoring, would fail until this is fixed.
  - **why_it_matters:** Any engine-run investigation depends on the owner-approved loading fix (load by content hash) being in place first.
  - **evidence_ids:**
    - X4-T0FETCH
    - INFRA-T0
- **issue:** On prices there is no strong statistical comparator.
  - **why_it_matters:** "t0 beats simple rules" on prices may not survive a competent statistical model, as happened on solar against blend_50.
  - **evidence_ids:**
    - X4-K1
    - X4-P2
    - R-EXP0-1

### C. Candidate investigations

#### Candidate I1

- **research_question:** On French national consumption, does passing a temperature forecast through t0's known-future covariate channel extract more predictive value than a simple, pre-specified linear post-hoc use of the same forecast on top of the same t0+holiday forecast? How much of the remaining error, especially in winter, is due to forecast staleness rather than to how t0 uses the input?
- **hypothesis:** H1: the covariate-channel arm (t0+holiday+raw temperature, the B1 arm) has lower MAE than the C1 arm plus a linear temperature correction fitted on C1's own trailing residuals. This would hold overall and in both the 2024 and 2025 parts. The alternative, H0', mirrors solar: the external linear correction is at least as good, so t0's channel underuses the information.
- **information_required:** The following are already wired: ODRÉ eco2mix consumption, the holiday calendar, and the archived Open-Meteo ECMWF IFS lead-3 2 m temperature at 12 regional points weighted by 2023 consumption, scorable from 2024-05-06 and gate-passed. New: (a) a per-hour OLS correction on C1's past errors, using only fully observed days up to D-2; (b) ERA5 reanalysis 2 m temperature at the same points, used only in a clearly named, unranked oracle diagnostic (not point-in-time, Open-Meteo CC BY 4.0).
- **relevance_to_t0_covariates:** This directly tests the efficiency of t0's known-future covariate channel against the simplest external alternative that uses identical information and an identical base forecast. It is the consumption counterpart of the solar comparison that found the channel weak, so it tells whether that weakness is target-specific or general.
- **appropriate_comparison:** Primary: the B1 arm vs the C1 arm with external temperature correction. Competence check: the corrected C1 arm vs the plain C1 arm (does the simple correction extract temperature value at all?). Diagnostic: t0+holiday+ERA5 temperature (oracle) vs the B1 arm. RTE is reported as a reference only.
- **what_a_negative_result_would_teach:** If the external correction matches or beats the channel, temperature's value on consumption is real, but t0's covariate channel is not the efficient route on either target studied. Covariate findings would then need to be stated as information value plus a hybrid architecture, not as a t0 covariate capability. That reframes how B1's eventual verdict is read.
- **expected_information_gain:** High. The outcome splits two mechanistically different readings of every covariate result so far. It also measures staleness cost against model-use cost for the open winter-gap question. Every plausible outcome changes what the next investigation should be.
- **feasibility_and_resources:** Moderate. Prerequisites are the engine's t0 loading-by-hash fix (pending anyway for B1), a new referee arm type (post-hoc linear correction) with live leak checks, and an ERA5 temperature read for the oracle. Compute is about 4 t0 arms over about 660 days, under an hour of CPU on Actions, plus 3 of the 184 remaining researcher evaluations. Results are exploratory; nothing can be frozen before B1 opens.
- **scientific_information_value:** High. It answers a question the project cannot currently answer: whether t0 adds value as a covariate integrator, as opposed to the covariate simply carrying information. It also produces the first consumption oracle diagnostic.
- **possible_economic_usefulness:** Indirect. If the external correction wins, a cheaper hybrid would be preferred. If the channel wins, it supports t0 as a covariate integrator. Neither result beats RTE's operational forecast, and Open-Meteo's free API is non-commercial.
- **motivating_evidence:**
  - **explanation:** The solar covariate slice showed a large t0+covariate gain that a one-line covariate model still beat by 24%. t0 correcting that model's residuals did not help. The consumption temperature gain (+19%) has only been benchmarked against t0 without temperature and against an RTE reference. The known-answer gates show t0 recovers only part of planted signals. The winter RTE gap is unexplained, and no consumption oracle has been run.
  - **evidence_ids:**
    - R-COV-2
    - L3
    - L5
    - L51
    - L54
    - L69
    - L63
    - L25
    - L36
    - L56
- **competing_explanations:**
  - t0's covariate channel is efficient for consumption, whose rich history structure lets t0 model interactions, but inefficient for solar's physics-dominated multiplicative relation.
  - t0's channel is generally weak; a linear external use of temperature would capture as much or more.
  - Both routes are limited by the stale lead-3 forecast and crude 12-point weighting, so they tie and the oracle gap is large.
  - The temperature gain is partly an artefact of the 2024–2025 period used to select it, so it appears unevenly across years.
  - A linear correction on 56 trailing days is too noisy or too slow at season transitions to be a fair competitor (checked by the competence comparison and window sensitivity).

#### Candidate I2

- **research_question:** On solar, is t0's weak use of irradiance due to how the covariate is represented? Would t0 given a target-unit covariate (the wx_ratio forecast itself, or a clear-sky index) match or beat wx_ratio?
- **hypothesis:** t0 handles near-target covariates well (planted ratios 0.59–0.65) but cannot learn the multiplicative irradiance-to-output map, so a target-unit covariate closes most of the 24% gap.
- **information_required:** Existing lead-3 irradiance archive and the wx_ratio construction; a new derived covariate in the engine catalogue; point-in-time proof that historical wx_ratio values in the context window used only data available at each past time.
- **relevance_to_t0_covariates:** Tests whether covariate representation (scaling over the whole span, additive vs multiplicative) governs t0's uptake.
- **appropriate_comparison:** t0 + wx_ratio-as-covariate (night-zeroed) vs wx_ratio; secondary vs t0+raw irradiance.
- **what_a_negative_result_would_teach:** If even a target-unit covariate does not let t0 reach wx_ratio, the limit is the instrument, not the encoding, for this target.
- **expected_information_gain:** Moderate. It is mechanistic and narrow, and P2 (residual correction) already showed that combining the two did not help.
- **feasibility_and_resources:** Moderate: a new derived covariate plus leak checks, using solar data from 2024-06-06 onward; compute similar to I1.
- **scientific_information_value:** Moderate: it clarifies an instrument mechanism on one target.
- **possible_economic_usefulness:** Low. National solar day-ahead forecasting is dominated by NWP-driven operational models far better than any arm here.
- **motivating_evidence:**
  - **explanation:** wx_ratio beats t0+weather by 24%; the ERA5 oracle helps only 6%; the solar planted-signal gate shows strong uptake of a target-like covariate.
  - **evidence_ids:**
    - R-COV-2
    - L3
    - L5
    - L18
    - L26
- **competing_explanations:**
  - Representation (units and scale) limits t0's uptake.
  - t0 weights its 90-day history over covariates regardless of representation.
  - wx_ratio's 14-day calibration is simply a near-optimal estimator that t0 cannot improve on.

#### Candidate I3

- **research_question:** On French day-ahead prices, do fundamental drivers, namely a wind forecast and a point-in-time-verified day-ahead load forecast, add incremental value to t0+holiday beyond temperature and sunshine?
- **hypothesis:** P4's small effect reflects missing drivers. Wind and load forecasts issued before 12:00 D-1 would add materially more than +2.8%.
- **information_required:** An archived wind-speed forecast (Open-Meteo lead-3) at points weighted by wind capacity; an ENTSO-E or RTE day-ahead load forecast with proven publication before 12:00 D-1 and a licence permitting use. Neither is wired.
- **relevance_to_t0_covariates:** Tests whether t0's covariate channel exploits strong fundamental drivers on a target where t0's history-based skill is already established.
- **appropriate_comparison:** t0_cal_wx + wind (+ load) vs t0_cal_wx on the same days; ideally also a strong statistical price model, which is unavailable since K1 failed.
- **what_a_negative_result_would_teach:** If fundamentals add little, t0's price skill is history-driven and public fundamentals pass weakly through its channel, which would match solar.
- **expected_information_gain:** Moderate, held back by the missing strong baseline and concentrated, noisy effects.
- **feasibility_and_resources:** Low to moderate: two new sources needing proof of issue time and a licence check, and Experiment 4's code sits outside the engine.
- **scientific_information_value:** Moderate to high if it can run cleanly.
- **possible_economic_usefulness:** Highest of the three, since price forecasts feed trading and storage decisions, but unproven and not required.
- **motivating_evidence:**
  - **explanation:** P4 gain is small and concentrated; the t0 report's German gain came from load, wind and solar forecasts of unverified issue time; strict checks show t0 relies heavily on recent prices.
  - **evidence_ids:**
    - X4-P4
    - X4-TABLES-P4
    - T0-REPORT
    - X4-SPEC
    - X4-STRICT
    - INFRA-DATA
- **competing_explanations:**
  - Wind and load carry the price information that temperature and sunshine lack.
  - That information is already reflected in the D-1 prices t0 reads.
  - t0's channel underuses any fundamental covariate.


### D. Chosen next investigation

- **chosen:** I1
- **why_this_is_a_meaningful_next_step:** Every covariate claim so far, including B1's, compares t0+covariate with t0 alone. That design cannot tell whether value comes from the information or from t0's covariate capability, which is exactly what the mandate asks about. On solar, adding a simple same-information comparator reversed the reading (R-COV-2, L3). On consumption, that comparator has never been run (L51, L54, L69). I1 adds it, with a competence check that rules out a strawman baseline, and adds an oracle diagnostic for the unexplained winter gap (L63). It uses already-gated data and leaves frozen B1 untouched. Its outcome determines how B1's 2027 verdict should be interpreted and whether the next claim batch should target the covariate channel or a hybrid. This is a change of comparison logic, not another encoding or season slice of the same arm.
- **why_not_the_others:** I2 probes a narrower mechanism on the target where t0's covariate use is already shown to be weak and where combining t0 with wx_ratio already failed (L5). It is a natural follow-up if I1 is negative. I3 needs two new sources whose publication time and licence are unproven, lacks a strong statistical comparator because LEAR's gate failed (X4-K1), and would chase effects that are currently small and concentrated (X4-TABLES-P4). Its information gain per unit of effort and risk is lower now. It would be better posed once I1 shows whether t0's channel is an efficient integrator at all.
- **abstention_reason:** None

### E. Proposed scientific protocol

- **target:**
  - **value:** French national electricity consumption, ODRÉ eco2mix-national-cons-def 'consommation', MW, 30-minute, all half-hours of each Paris delivery day.
  - **status:** validated
  - **evidence_ids:**
    - INFRA-ENGINE-CATALOGUE
    - C1-CONFIRMATION
    - L51
- **decision_time:**
  - **value:** 12:00 Europe/Paris on D-1, forecasting local day D; the origin slot is treated as observed, as in all earlier work.
  - **status:** validated
  - **evidence_ids:**
    - INFRA-DATA
    - L56
    - R-ENGINE-6
- **forecast_horizon:**
  - **value:** Day-ahead: every half-hour of day D (t0's fixed 73-step horizon from the gate, scored on day D).
  - **status:** validated
  - **evidence_ids:**
    - R-C1-4
    - INFRA-ENGINE-CATALOGUE
- **information_family:**
  - **value:** Archived lead-3 2 m temperature forecast (raw transform), delivered two ways: (a) as a t0 known-future covariate (B1 arm, validated by gates); (b) as regressors [T, HDD15, CDD22 + intercept] in a per-hour OLS fitted on the C1 arm's trailing 56 fully observed days of errors (new, proposed). ERA5 temperature is used only as an unranked oracle diagnostic.
  - **status:** proposed
  - **evidence_ids:**
    - L25
    - L36
    - L51
    - INFRA-DATA
    - R-COV-2
- **t0_configuration:**
  - **value:** t0-alpha only, zero-shot, 90-day context, median scored, loaded by the sha256 of its frozen weight files (requires the engine loading fix). Arms: C1 arm (t0+holiday), B1 arm (t0+holiday+raw temperature), oracle arm (t0+holiday+ERA5 temperature, name contains 'oracle'). No t0-beta.
  - **status:** proposed
  - **evidence_ids:**
    - INFRA-T0
    - X4-T0FETCH
    - L56
    - INFRA-ENGINE-CATALOGUE
- **comparisons_and_baselines:**
  - **value:** Decision comparisons (Holm over 2): (1) primary: B1 arm vs C1+external temperature correction; (2) competence: C1+correction vs C1 arm. Diagnostic: oracle arm vs B1 arm. Report-only: C1+correction applied to the B1 arm vs the B1 arm (is temperature information left unused?); blend_50; RTE as reference only; correction window sensitivity at 28 and 112 days.
  - **status:** proposed
  - **evidence_ids:**
    - R-COV-2
    - L5
    - L9
    - INFRA-ENGINE-CATALOGUE
- **point_in_time_constraints:**
  - **value:** Temperature forecasts come only from runs issued at least about 3 days before the target hour, asserted per forecast. Correction training uses only days up to D-2 whose actuals are fully published by the gate, and only C1 forecasts made at their own gates. Coefficients are refitted per origin. Live leak checks apply to every arm: poisoned post-origin data leaves forecasts byte-identical, and a legal pre-origin change moves them, including a weather positive control. The ERA5 arm is exempt only as a declared, unranked oracle.
  - **status:** proposed
  - **evidence_ids:**
    - INFRA-DATA
    - R-ENGINE-6
    - R-COV-2
    - L25
- **discovery_sample:**
  - **value:** Delivery days 2024-05-06..2025-12-31 (about 600 days), scored on the intersection where every arm has a forecast; warm-up for the 56-day window draws on temperature archived from 2024-02. 2025 is explored, never confirmed. No 2026 data.
  - **status:** proposed
  - **evidence_ids:**
    - INFRA-ZONES
    - INFRA-DATA
    - L51
- **validation_method:**
  - **value:** Rolling-origin backtest with per-origin refits. Paired 14-day moving-block bootstrap of pooled MAE skill (B=2000, fixed seed), one-sided p, Holm over the two decision comparisons. Directional consistency required in the 2024 part and in 2025, and in the winter and summer slices. All results exploratory; any later claim must wait until B1 is opened and then go through the forward vault.
  - **status:** proposed
  - **evidence_ids:**
    - X4-SPEC
    - INFRA-VAULT
    - X4-REPLICATION
- **outcome_measures:**
  - **value:** MAE skill with 95% CI; days won and lost; per-year, winter and summer slices; top-10/20 concentration; oracle gap by season; report-only pinball loss of t0 arms.
  - **status:** proposed
  - **evidence_ids:**
    - X4-TABLES-P4
    - L69
    - R-EXP0-1
- **falsification_criteria:**
  - **value:** Validity first: if the competence check fails (CI includes or is below 0), the primary comparison is uninformative. Given a valid competence check, the primary comparison reads as follows. H1 is supported if its skill is above 0 with Holm p < 0.05 and both years point the same way. H1 is falsified if its CI lies entirely below 0. Equivalence-level evidence (the channel adds nothing beyond linear) requires a CI within ±5%; otherwise the result is inconclusive. Oracle diagnostic: a gain of 10% or more (overall or winter) indicates staleness matters; under 5% indicates a model-use bottleneck, as on solar.
  - **status:** proposed
  - **evidence_ids:**
    - R-COV-2
    - R-EXP0-1
    - X4-SPEC
- **leakage_and_snooping_risks:**
  - **value:** These days were used to select and freeze B1's arm and encoding. The correction's specification (features, 56-day window, OLS) must therefore be frozen before any run, with no search; the sensitivity windows are report-only. Other leakage risks: residual-window leakage from partially observed D-1 actuals (excluded by design); oracle contamination (never ranked); RTE issue time unverified (reference only). Data risks: consolidated vs definitive vintages, and the crude 12-point weighting. Nothing here may modify B1.
  - **status:** proposed
  - **evidence_ids:**
    - L55
    - L51
    - L69
    - R-C1-4
    - L56
    - R-ENGINE-6
- **compute_budget:**
  - **value:** About 3–4 t0 arms × about 660 days on CPU, under 1 hour on a standard Actions runner (Experiment 4 scored nine arms × 731 days in about 39 minutes), plus OLS refits. Uses 3 of the 184 remaining researcher evaluations, plus a one-time engineering build of the correction arm, the ERA5 read and the t0 loading fix.
  - **status:** proposed
  - **evidence_ids:**
    - INFRA-COST
    - INFRA-BUDGET
    - INFRA-T0

### F. Knowledge update

- **supports_relationship:**
  - **what_would_count:** Competence passes, and the primary comparison has CI lower bound above 0 with Holm p < 0.05 and the same sign in 2024 and 2025 (and non-negative winter and summer point estimates).
  - **knowledge_update:** Exploratory: on consumption, t0's covariate channel extracts temperature information beyond a linear external use of it. Combined with solar, this suggests channel efficiency depends on the target, being better where history structure is rich. B1's verdict would then be readable as evidence about t0's capability.
  - **what_next:** Test whether a richer non-linear external model closes the gap. Run the representation test on solar (I2) to explain the contrast. After B1 opens, consider a vault claim of channel vs external correction (needs a vault comparator extension).
- **against_relationship:**
  - **what_would_count:** Competence passes, and the primary comparison's CI lies entirely below 0: the linear correction beats the channel.
  - **knowledge_update:** On both studied targets, simple external use of a covariate outperforms t0's covariate channel. Covariate value is real, but it is not a t0 capability. B1, even if confirmed, would show information value delivered inefficiently. The product idea shifts toward hybrids (t0 for history structure, external models for covariates).
  - **what_next:** Investigate why: representation and scaling tests (I2) and multi-point temperature covariates. Consider evaluating t0-beta as an instrument under the same known-answer gate, without assuming it is better.
- **underpowered_or_uninformative:**
  - **what_would_count:** Competence fails, or the primary comparison's CI straddles 0 and is wider than ±5%, or years disagree in sign.
  - **knowledge_update:** No update on channel efficiency. If competence failed, the linear correction is not a fair strong baseline and the question remains open. If the CI is merely wide, about 600 days cannot resolve differences of a few percent.
  - **what_next:** Pre-register a stronger external baseline. Plan a forward-vault comparison once B1 opens. Seek a longer point-in-time temperature archive to extend the discovery sample.
- **t0_failed_to_exploit_available_information:**
  - **what_would_count:** The report-only correction applied to the B1 arm significantly improves it, or the oracle arm gains little while the external correction gains more than the channel.
  - **knowledge_update:** t0 leaves available temperature information unused; the limitation lies in the instrument's uptake, consistent with planted ratios well above the ideal (0.77–0.91 on consumption).
  - **what_next:** Run a known-answer sweep of covariate scaling and encoding on consumption to locate the uptake limit, then a representation probe on solar (I2).
- **insufficient_data_quality:**
  - **what_would_count:** Temperature archive or ERA5 gaps leave too few scorable days or correction windows that cannot fill; leak checks or the positive control fail; vintage problems arise.
  - **knowledge_update:** Nothing is learned about channel efficiency; the data pipeline needs repair before the question can be asked.
  - **what_next:** Fix or replace the sources: fresher forecasts with verifiable issue times, and regional temperature weighting. Rerun the gate, then repeat I1.


<!-- researcher-output:end -->

---

## 3. Engineering annotations (not the researcher's)

*Written by the orchestrator after the answer was recorded. They do not edit the answer or change its choice.
Whether any of them should go back to the researcher is an owner decision (`FEASIBILITY_REVIEW.md`, section 10).*

**How the answer was checked.**
- Four fact-check agents checked 246 factual or numeric statements against the evidence pack and its sources.
- Each flagged statement went to an independent skeptic, told to refute the flag.
- **Results:**
  - 30 statements were flagged;
  - 10 flags were refuted, because the researcher's wording was a fair reading of the evidence;
  - 20 survived, all of them about how evidence is characterised.
- A separate spot-check of 12 numeric citations found every number matching. All 57 cited ids exist.

**The 20 flags that survived** (corrected readings in brackets):

*Characterisation of the evidence:*
- **A, finding 5: calendar covariates "contribute little" (status "negative").**
  - The all-year holiday effect is inconclusive rather than negative: +4.5% [−1.7, +8.4] in 2024.
  - Bridge days are shown negative.
  - The pack's own summer slice (L54) gives t0 + holiday about 9% over t0 alone: 971.9 vs 1071.0 MW on 302 days.
  - This does not affect I1: both of its arms keep the holiday calendar.
- **A, finding 12: "t0 recovers only part of a planted signal".**
  - This holds for the covariate slice, but not for prices. There the planted copy alone would score about 8.4 EUR/MWh,
    and t0 with it scores 6.4, so t0 uses the signal fully and adds its history.
  - The planted-to-base ratios are not comparable measures of uptake: the noise is fixed at 5% of each target's p99.
- **A, finding 2: t0 "extracts roughly what a 7-day same-slot mean extracts".** [This is a null result in daylight,
  not equivalence. Over all hours, raw t0 extracts less.]
- **B, issue 7: prices "may not survive a competent statistical model, as happened on solar against blend_50".** [The
  solar episode has already been repeated on prices, and t0 survived: it beats blend_50 by +22.7%. What remains open is
  a genuinely stronger model such as LEAR, which K1 prevented. The point of the issue stands.]
- **Summary, and D: "every covariate gain so far … measured only against t0 without that covariate".** [Too broad. On
  solar, t0 + weather was compared with the same-information wx_ratio (−23.8%), and the B1 arm was also compared with
  RTE as a reference. Accurate version: no non-t0 model using the same information has been run on consumption or
  prices. B, issue 1 already says this correctly.]
- **Summary: the oracle "separates forecast staleness from how well t0 uses the input".** [It bounds what the lead-3
  forecast's whole error costs t0. It cannot separate staleness from uptake, or from the 12-point weighting, and
  swapping in ERA5 also changes t0's 90-day context.]
- **C, I2: the solar gates "show strong uptake".** [Partial uptake: ratios 0.65 and 0.59, which still miss the earlier
  ≤ 0.5 bar.]
- **F, "t0 failed to exploit": "planted ratios well above the ideal (0.77–0.91)".** [The pack defines no ideal. 0.91
  comes from the failed ka/1 gate, and the passing ka/2 gate gives 0.77.]
- **E, falsification: the oracle's "under 5% … as on solar".** [The solar oracle gain was +6.4% [+2.7, +10.6]. That is
  in the 5–10% band the rule leaves unassigned.]

*Feasibility statements:*
- **C, I1 prerequisites (the loading fix, a correction arm, an ERA5 read).** [Incomplete. Also needed:
  - the oracle exemption in discovery and the leak harness;
  - claims and spec guards;
  - a frozen readout;
  - a re-gate, if fingerprinted files change.]
- **D: "It uses already-gated data".** [True for the decision comparisons. ERA5, used only by the oracle, is neither
  wired nor gated.]
- **E, compute: "3 of the 184 remaining researcher evaluations".** [That covers only the decision-and-diagnostic
  probe. The full protocol needs about 5–8 or more if the researcher submits it, and 0 if the owner dispatches it.]
- **E, validation: the 14-day blocks and Holm over 2.** [Not what the engine's referee computes (7-day blocks, no
  Holm). The proposal does not say how they would be produced. They can be computed from the recorded per-day errors.]
- **C, I2 feasibility.** [Understated. I2 also needs the loading fix and a wx_ratio comparator. Its covariate cannot
  start before about 2024-06-20.]

*Citations:*
- **A, finding 9: "temperature and sunshine".** [Correct, but the variables are named in X4-ROLE, which was not cited.]
- **C, I3: "strict checks show t0 relies heavily on recent prices".** [The size comes from X4-SECONDARIES (+17.1%),
  which was not cited.]

*Internal consistency of the protocol:*
- **D: the competence check "rules out a strawman baseline".** [It rules out a correction that extracts nothing, not a
  weak one. A correction worth about 3% would pass it and still lose to the B1 arm by about 17%.]
- **E vs F: the support rule.** [It is stated three ways: in E.falsification_criteria, in E.validation_method and in
  F.supports.]
- **E vs F: the equivalence outcome.** [The equivalence outcome E defines (a CI within ±5%) maps to no F outcome.]

**One flag concerns the orchestrator, not the researcher.**
- B, issue 6 calls the engine's t0 loading fix "the owner-approved loading fix".
- The pack's source for that phrase is the Experiment 4 retrieval record written by the orchestrator. It says the
  engine and B1 fix "is a separate, owner-approved change made before 2027-04-01".
- That wording can be read as approved or as needing approval. The skeptic judged the researcher's reading fair.
- No dated owner decision for an engine fix exists. B1's vault fix and the probe-path fix that I1 needs are also two
  different changes (`FEASIBILITY_REVIEW.md`, section 3).
- The retrieval record is an Experiment 4 document and is left unedited.

**A limit of the pack, also the orchestrator's.**
- The researcher correctly says that B1's per-year stability "was not checked by the referee".
- The per-day errors that would show it are on the ledger, but the pack left per-day series out for size.
- Recomputed for this review, on B1's own selection days and as exploratory figures:
  - 2024: +16.0% [+7.0, +25.7];
  - 2025: +21.0% [+15.1, +26.6].
