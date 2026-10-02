# Experiment 5, second decision: review of the researcher's proposal (v2)

*An engineering review by the orchestrator of the researcher's answer recorded at ledger seq 76 and rendered in
[`RESEARCHER_PROPOSAL_V2.md`](RESEARCHER_PROPOSAL_V2.md) (section 2). It flags; it does not change the hypothesis,
choose another investigation, fill gaps in the protocol or freeze anything. Nothing has been run: no forecast, no
fetch, no probe. The checks are read-only arithmetic on recorded data, the calendar and the repository's code.*

*Attribution. Between the first decision (seq 74) and this one, the system text, the answer schema, the evidence pack
(85 to 127 records) and the output limit (64,000 to 128,000 tokens) all changed together. The model and the effort
setting did not (seq 74 against seq 76, compared by equality only). The per-call wall-clock limits also changed (20 to
40 minutes per attempt, 50 to 90 minutes per job), as did the read timeout (600 to 900 s), the repair-turn format and
the handling of mid-stream errors; seq 76 used no repair or retry. Each condition had one call, so call-to-call variation is not
measured either. Differences between the two answers therefore cannot be attributed to the clarified mandate alone, or
to any one of these changes.*

**How to read the references.**
- `R:123` is line 123 of [`proposal_v2_rendered.md`](proposal_v2_rendered.md), the mechanical rendering of the answer.
- `A_learned[17]`, `B_unexplained[4]` and similar are zero-based positions in
  [`researcher_output_v2.json`](researcher_output_v2.json).
- N1's outcomes are numbered 1 to 10 in the order listed at R:322-341, and its competing explanations 1 to 6 in the
  order listed at R:295-300.
- Record ids (`L51`, `E5-REVIEW-7`, ...) are evidence-pack records. "Seq N" is engine ledger entry N (verified chain,
  head seq 76). File and line references are to commit `153e12e`.
- "Not in the pack; not verified by engineering" marks a fact that comes from outside the evidence pack and the
  repository and that this review did not check.

## Summary

**What was proposed.**
- **N1, chosen.** A matched local-history learning curve on French national consumption. At history levels L = 7, 14,
  28, 56 and 112 days, t0 with holiday (T0H), with holiday and the gated lead-3 temperature (T0HT), and with a lag-28
  temperature placebo (T0HP, report-only) is compared with a frozen non-t0 similar-day specialist without (SD) and
  with (SDT) a per-hour temperature slope. A(L) = 1 - MAE(T0HT)/MAE(SDT) is t0's advantage at level L; G_t0(L) =
  1 - MAE(T0HT)/MAE(T0H) and G_S(L) = 1 - MAE(SDT)/MAE(SD) are temperature's gain under each instrument. Two
  primaries, Holm at 0.05 one-sided: b_A, the slope of A(L) on log2 L, and b_G, the slope of G_t0(L) - G_S(L). About
  545 days, 2024-07-01..2025-12-29. Exploratory (R:273-342, R:457-584).
- **I1, recorded as "redesigned".** N1 reuses I1's target, gated temperature, its C1 and B1 arms (now T0H(90) and
  T0HT(90)), a frozen untuned comparator and the 14-day-block, Holm statistics. I1's own question, t0's channel
  against an external linear temperature correction on the same t0 + holiday base, is tested nowhere in N1 (R:450;
  `RESEARCHER_PROPOSAL.md:224-228,353`).
- **N2, not chosen.** A no-weather test around the March 2020 lockdown. It needs scoring outside the 2022-2025
  discovery zone. Set aside for the zone extension, the lack of point-in-time weather and possible pretraining
  exposure (R:344-391, R:452).
- **N3, not chosen.** A discovery audit over at most 6 pre-declared candidates, run after N1 at a history level N1
  would fix (R:393-443, R:452).
- **Constraints.** No candidate reads 2026+ data, changes B1 or Experiment 4, or proposes a t0-beta experiment. Only
  C1 is called confirmed.
- **Main flags.** Numbers and citations hold. Two material factual errors: an unsupported "no dated break" premise and
  D's account of I1. At the short end the specialist is fixed by its own rules (SD is the same forecast at every
  level; SDT's slope is off at L = 7 under the natural reading), which shapes both primaries. The outcome map is not
  partitioned as the answer claims. Several protocol details must be decided before any freeze (section 11).

| Owner criterion (`NORTH_STAR_CLARIFICATION.md:451-458`) | Finding in one line | Key evidence |
|---|---|---|
| Factual accuracy | Figures and citations hold (224 citations to 76 ids, none missing; no figure copied wrongly). Two material errors: A_learned[17]'s "no independently dated break", and D's claim that I1's comparison survives as N1's 90-day anchor | A_learned[17] (R:172); D (R:450); `RESEARCHER_PROPOSAL.md:353` |
| North Star | The answer takes owner points A-D in turn. It tests A partly, as exploratory evidence on one series; argues B cannot be tested now; touches C and D with a first cost datum, a placebo and descriptive detection cost. Its component list claims more than its decision rules use | R:11-13, R:26-27, R:37-38, R:47-48, R:276-281 |
| Foundation-model advantage vs information value | Better posed than I1 (no t0 inside the comparator; temperature's gain measured under each instrument). But SD does not vary with L, SDT's slope is off at L = 7 under the day-pair reading, and the two gains have different bases, so both primaries partly measure rule choices | R:491, R:539; scratch `fm/sd_invariance.py`, `fm/pairs.py` |
| Scarcity and regime tested credibly | Scarcity: varied for t0; for the specialist only through its temperature slope; the scaling confound has no control; the placebo cannot carry the seasonal level it is meant to proxy. Regime: not tested, and the answer says so; one premise rests on outside knowledge | INFRA-T0; `t0/scaler.py:107-139,181-184`; R:27 |
| Comparator fair | History span and inputs are matched, frozen, with no t0 inside (holds). The competence gate is a floor at one level; functional form, holiday handling and selection are not neutralised | `solarbench/forecasters.py:445-451`; L7; R:531 |
| Cost claims measurable | Calls, tokens and evaluations are measurable from existing records. Engineer-hours, runner minutes per route and level and approval-to-readout time need new recording; "cost per resolved primary question" is undefined. The answer calls it a first datum, not a test | `engine/discover.py:140`; R:546 |
| Every outcome teaches | Invalid and Incompetent come first. Below them, labels overlap (SUPPORTS with FLAT), some result combinations match two outcomes with conflicting lessons and others match none, the placebo override can fire on noise, and Invalid can fire on a data revision | R:554, R:322-341; scratch `skeptic_cost/check1.py`, `sk2/omap_check.py` |
| Scope proportionate | Every arm and level feeds a stated statistic. The answer's work items sum to 4.5-5.5 engineer-days against a stated 4.5-6 (I1 was costed at 5-8). The compute figure assumes only common days are forecast (the engine would make about 11,300-15,700), and some required work items are not listed | R:318-319; `FEASIBILITY_REVIEW.md:26`; `engine/discover.py:35-39` |

## 1. Factual accuracy

**What was checked.**
- The summary, section_4, A_learned and B_unexplained: 136 factual or numeric statements, checked against the cited
  records, the code, the installed t0 package and the ledger. That count is the checking lens's own and was not
  re-verified.
- C (N1, N2, N3), D, E and G: checked statement by statement in 42 items by two further lenses.
- Citations (script over `researcher_output_v2.json` and `evidence_pack_v2.json`): 224 citations to 76 unique ids
  across the answer, none missing. In the summary, section_4, A_learned and B_unexplained: 138 citations to 70 ids.
- Record integrity: `payload.response_text` at seq 76 equals `researcher_output_v2.json` (51,803 characters; compared
  as strings and as parsed JSON).
- Schema: `engine.propose_v2.validate_proposal_v2` returns no errors for the answer against the 127 pack ids.

**What holds.**
- **No figure is copied wrongly.** Recomputed examples:
  - C1: +46.3%, lower bound +42.0% against a 25% threshold (C1-CONFIRMATION). "RTE 23% better": 1627.8/1322.4 - 1
    = 0.231 (L8, L9).
  - Plain t0 against blend_50: 1 - 1644.4/3114.4 = +47.2% (L7). Summer holiday slice: 1 - 971.918/1071.017 = 9.25%
    (L54). Bridge days -5.1% [-7.8, -2.1] (L33).
  - Temperature (B1 arm): +19.3% [14.9, 23.7] over 602 days (L51); summer +11.1% (L54), winter +24.4% (L69); RTE
    reference +7.6% [-2.7, +16.0] (L60).
  - Solar: daylight -0.1% [-4.9, +4.5], called a null, not equivalence (R-EXP0-1); wx_ratio -23.8% (L3).
  - Prices: P1 +22.7% [18.6, 25.9]; P4 +2.8% [1.1, 4.4], 83% of the gain on 20 of 572 days (X4-P1, X4-P4,
    X4-TABLES-P4).
  - Engine: 0.37-0.74 s per t0 day-forecast, all-in (seqs 51-69, elapsed_s over eligible days); 184 of 200 discovery
    evaluations left (`engine.referee.budget`, read-only); gate seq 36's fingerprint `b2d50d2f…` equals the fingerprint
    at HEAD.
- **Status rule.** Only A_learned[0] (C1) is "confirmed", and it cites the two records graded
  confirmed_on_sealed_data. The other 19 findings: exploratory 8, uncertain 9, negative 2.
- **Infrastructure facts.**
  - Every recorded t0 target forecast used a 90-day context: all 25 `context_days` values on the ledger are 90. The
    one exception the answer names, a 60-day residual model, is in INFRA-DATA-HISTORY.
  - Context length is outside the gate fingerprint (`engine/gates.py:38-51`; `engine/catalogue.py:16-17`).
  - No per-arm context field exists yet, and the answer lists it as work (`engine/spec.py:19`; `engine/arms.py:24`).
  - Route A exists: an owner-dispatched probe mode, not charged to the discovery budget
    (`.github/workflows/engine.yml:18-28,81,208-228`; `engine/referee/budget.py:14-20`).
  - The step limit is 120 minutes in a 150-minute job (`.github/workflows/engine.yml:160,218`).
- **Caveats stated.** Possible pretraining exposure; no same-information non-t0 model has been run on consumption or
  prices (A_learned[10], in E5-ANNOT's corrected wording); compounding research intelligence not demonstrated (R:182);
  data vintage (R:260-261); results stay exploratory.

**Material errors.**

1. **"No independently dated break lies inside the window where point-in-time weather exists (2024-02 onward)"**
   (A_learned[17], R:172; restated without qualification in N2's motivation, R:353).
   - The cited records (LEDGER-PER-YEAR, INFRA-DATA, OWNER-NS2-4) say nothing about dated breaks. A script search of
     all 127 records for lockdown, covid, confinement, crisis, sobriety and related terms found no record on breaks in
     consumption.
   - Section_4 words the premise as the researcher's own belief, limited to consumption and to 2024-05..2025-12: "I
     know of no externally dated structural break in French consumption" (R:27). A_learned[17] drops both the hedge
     and the limit to consumption, and gives a different window start (2024-02).
   - In that general form the pack contradicts it: the price market switched to quarter-hour products on 2025-10-01
     (INFRA-DATA-HISTORY), inside the weather window (X4-RUN: temperature 2024-02-06..2025-12-30). Section_4 itself
     calls that change externally dated (R:27).
   - **Effect.** The summary's "Regime change cannot be tested credibly with the point-in-time covariates now wired"
     (R:7) and N2's motivation rest partly on it.
     For consumption the premise is unverified, not shown false: whether a dated break in French consumption exists in
     2024-05..2025-12 is not in the pack; not verified by engineering.
2. **D's account of I1** (R:450, reason 2): "I1 was a full-sample contest at one 90-day history ... I1's comparison is
   roughly its 90-day anchor."
   - N1's 90-day anchor holds only T0H(90) and T0HT(90), used to reproduce seq 51 (R:482, R:531). That pair is seq 51's
     B1-arm-vs-C1 comparison, which the review of I1 called "not among I1's decision comparisons" (E5-REVIEW-8,
     `evidence_pack_v2.md:8329-8330`).
   - I1's primary was the B1 arm against C1 plus an external temperature correction, fitted on C1's trailing 56 days,
     with 28- and 112-day windows report-only (`RESEARCHER_PROPOSAL.md:336,353`). So "at one 90-day history" also
     leaves out the correction's own history.
   - **Effect.** "Redesigned" can read as keeping a question the owner called "scientifically interesting"
     (`NORTH_STAR_CLARIFICATION.md:119`); N1 drops it. See "The account of I1" below.

**Minor errors and gaps.**

| Statement in the answer | What the evidence shows | Evidence |
|---|---|---|
| "The only low-data specialist ever run here points against the thesis" (R:12) | Not the only one. X4-K1 recorded LEAR at 56, 84, 1092 and 1456-day windows (56 days is 10.6% worse than 1092 days: 4.7055/4.2560 - 1). Short-window simple rules (ewma over 14 days, mean_7d) were also run against a 90-day t0. LEAR's windows were a reproduction gate with no t0 comparison, so they refute "only" but not the direction. The short-window simple rules, run against a 90-day t0 with no matched history, point the same way (all hours), so the conclusion stands | X4-K1 attempt 3; R-EXP0-1; L3 |
| Regime discussion: the March 2020 lockdown is decree-dated; the 2022 demand fall had a diffuse onset; "Both 2020 and 2022 are also likely to fall inside t0's pretraining period" (R:27) | None is cited or labelled as an outside fact, although the system text requires record ids for material claims. The repository's copy of the authors' report (not summarised in the pack) says "Every real series of the corpus ends before 2022", which runs against the 2022 part. The decree facts are not in the pack; not verified by engineering | `brief_appendix_v2.md:252`; `docs/2609.24559.pdf` p.27 |
| "The known-answer gates show the covariate plumbing is aligned and leak-free" (A_learned[16]) | The gates test alignment and covariate use, not leakage; their planted and decoy arms read the future by design. Leakage is checked by the live leak checks (`leak_checks_passed` in L51, L54, L60, L63, L66, L69), which are not cited. X4-RUN's 459/459 leak check covers prices, not the engine | `engine/referee/known_answer.py:1-9`; L17, L18, L25, L36 |
| The temperature gate "passed only after an owner rule change and a new period (L24, L25)" (R:38) | The order is right, but in the new period the decoy ratios (1.0013 at L25, 1.0132 at L36) were within the original 1.05 limit. R-ENGINE-6: "the new period, not the wider rule, made the difference". B_unexplained[5] reports both values | L17, L24, L25, L36; R-ENGINE-6 |
| "A non-t0 route needs a bespoke model per covariate" (R:38) | Stated as fact, but the owner frames it as part of what is under investigation, and no record establishes it. Unsupported, not shown wrong. The second clause ("nobody has measured that cost here") is accurate | `NORTH_STAR_CLARIFICATION.md:97`; E5-REVIEW-8 |
| Temperature "may help t0 partly by telling it where it is in the annual cycle"; the placebo "keeps the seasonal position" (B_unexplained[4], R:213; R:48) | INFRA-T0, which B_unexplained[4] cites, says known-future covariates are standardised over the context-plus-horizon span, which removes the absolute level t0 sees. The answer states the standardisation elsewhere (R:178, R:298) without connecting it (section 4) | `t0/scaler.py:145,181-184`; `t0/mask.py:63-67` |
| Interactions across history levels smaller than 4-7 points "will be inconclusive" (B_unexplained[13]; R:13) | 4-7 points is the precision of single paired 90-day t0 contrasts over 602 days. The pack has no precision figure for a cross-level slope, and N1's sample is smaller. The protocol defers the estimate to a pre-freeze step (section 7) | E5-POWER pairs a-d; R:531 |
| "The data needed are already wired and gated" (R:12) | True at the 90-day context where the gate ran. Context length is outside the fingerprint, so the pass carries over to 7-112 days with no evidence there; any re-gate also runs at 90 days | `engine/referee/known_answer.py:50`; B_unexplained[5] (R:221) |
| "with the lag-28 placebo the first common day is 2024-07-01" (R:306) | A conservative round date. With the engine's covariate and coverage rules, the L = 112 placebo arm can start on 2024-06-26 (full coverage) or 2024-06-24 (98% rule), giving 550-552 days. The decision arms alone could start about 2024-05-27/29 | scratch `skf/firstday2.py` (reproduces seq 51's first B1-arm day at L = 90) |
| "Autumn clock-change days and days dependent on them are excluded, as before" (R:523) | The ~545 days include the day after and the week after each autumn change. "Dependent" is not defined. Experiment 0's rule would give 541 days; the 7 days with no specialist source at L = 7 (section 4) would drop under the intersection rule. The sample is about 534-545 days depending on an undefined rule | seq 51 `per_day`; R-EXP0-0; scratch `skf/nosource.py` |
| "plus about 1,500 leak-check rebuilds" (R:319, R:578) | No stated basis in the answer or the pack. The current harness implies about 270 rebuild forecasts for N1's 17 t0 series, or about 370 with a 3-origin, 2-variant history-budget check. If that check re-ran every forecast it would add about 9,300 | `engine/referee/leakcheck.py:78-134` |
| "about 20-25 [evaluations] if the researcher submitted them" (R:320) | Not available without changing the loop: the loop's answer schema fixes an arm to a name and catalogue covariates, so it cannot express a per-arm context. E5-REVIEW-3 places changing the loop outside the approved scope | `engine/researcher.py:98-102`; `engine/spec.py:19,65` |
| N2: "reading earlier dates needs an owner decision" (R:353) | The code refuses scoring before 2022, not reading: seq 51 read from 2021-09-23, and INFRA-DATA-HISTORY says earlier days "may be read as context". N2's own work item says "read 2017-2020 as explored data" | `engine/zones.py:46-53,56-63` |
| D: N3 "needs two new sources" (R:452) | Only the school-holiday calendar is new. The consumption-weighted radiation would come from the Open-Meteo archive already wired (same 12 points and fetch path as temperature, licence terms recorded); it lacks a catalogue entry and a gate. D's other two reasons do not depend on this | `engine/arms.py:51-64,92-102`; `engine/covs.py:33-44`; `README.md:975` |
| G: the drafted benchmark (DESIGN-1A-2) has "planted regime shifts and varying history lengths" (R:591) | The pack record is a status line only. The draft itself (branch `experiment-1a-preregistration`, `docs/experiment_2/PREREGISTRATION.md`) has null series, traps, decoys, regime-conditional mechanisms and hidden change points, but fixed segment lengths, and says "As drafted, this benchmark does not exercise t0" (line 11). A contamination-free replication of N1's learning curve on it is not available as drafted | DESIGN-1A-2; draft lines 11, 405-415, 471, 498, 1320-1333 |

**The account of I1.**

| Element | I1 | N1 | Evidence |
|---|---|---|---|
| Question | Does t0's channel (B1 arm) beat C1 plus a frozen linear temperature correction on the same base? | Does t0's advantage over a non-t0 specialist, and temperature's gain under each, change with matched history? | `RESEARCHER_PROPOSAL.md:224-228`; R:274 |
| Comparator | C1 + correction fitted on C1's trailing 56 days | SD and SDT, no t0 | `RESEARCHER_PROPOSAL.md:336`; R:491 |
| History | t0 at 90 days; correction at 56 (28 and 112 report-only) | 7-112 days, matched; 90 days only to reproduce seq 51 | `RESEARCHER_PROPOSAL.md:353`; R:482 |
| ERA5 oracle | Diagnostic | Dropped | R:450 |
| Sample | About 600 days | About 545 days | `RESEARCHER_PROPOSAL.md:369`; R:523 |
| Statistics | 14-day blocks, B = 2000, Holm; same direction in both years and seasons | 14-day blocks, B = 2000, Holm; slices report-only | `RESEARCHER_PROPOSAL.md:376,390`; R:531, R:539 |
| Pinball loss | Report-only | Not mentioned | `RESEARCHER_PROPOSAL.md:383` |
| Budget route | 3 researcher evaluations | Route A, 0 evaluations | `RESEARCHER_PROPOSAL.md:407`; R:578 |

- **Holds.** The reasoning opens with the owner's required label ("I1 was the researcher's decision under the previous
  mandate") and picks one of the owner's four options (`NORTH_STAR_CLARIFICATION.md:18,188-192`;
  `engine/propose_v2.py:57,248`). I1's record is unchanged: `researcher_output.json` and `RESEARCHER_PROPOSAL.md` were
  last changed before the clarification commit `e84d83d` (git log). The elements it says are kept exist in both
  proposals.
- **Gap, material (with error 2 above).** I1's hypothesis H1 is tested at no history level. The answer explains why it
  replaced the comparator (reason 1), but never says whether H1's question is deferred or dropped.
- **Error, minor (reason 1).** "The review showed that I1 could not separate foundation-model advantage from
  information value" (R:283, R:450). E5-REVIEW-7 concluded that "a channel win cannot be attributed to the target"
  (`evidence_pack_v2.md:8277-8281`). The foundation-model-versus-information wording is the owner's section 13
  criterion (`NORTH_STAR_CLARIFICATION.md:453`). The inference follows from I1's design, but it is the researcher's
  own. The answer cites no E5-P1-* record anywhere (seq 76 `evidence_ids_cited`).
- **Error, minor (reason 2).** "Exactly where the owner notes the hypothesised advantage is smallest" drops the owner's
  "may" (`NORTH_STAR_CLARIFICATION.md:121`). I1's correction was fitted on 56 days, not plainly "abundant
  observations".
- **Error, minor (reason 3).** The unchecked ERA5 licence is cited to E5-REVIEW-7 and E5-REVIEW-2. It appears in
  E5-REVIEW-SUMMARY and E5-REVIEW-10 item 6 (`evidence_pack_v2.md:7914-7916,8438-8441`), neither cited anywhere in the
  answer. The other two parts of reason 3 are correctly sourced.
- **Error, material (reason 4).** "The review's gaps are closed ... the outcome map is partitioned with precedence
  (E5-REVIEW-6)". The day set (gap 5) is fixed. The outcome map (gap 2) is not partitioned (section 7), and the
  competence bar (gap 6) is not addressed (section 5).
- **Gap, minor.** Changes not listed in the disposition: the pinball loss is dropped; the both-years and both-seasons
  direction rule is dropped; I1's report-only arms are dropped; the sample shrinks from about 600 to about 545 days.
  The researcher may make these changes; the record of what changed is incomplete.

## 2. Does it address the North Star?

**What holds.**
- **Owner section 4, point by point.** Section_4 takes A-D in turn (R:11-13, R:26-27, R:37-38, R:47-48):
  - A: "Partly", as exploratory evidence on one series, with three reasons it cannot show generalisation to new
    systems.
  - B: not tested, with the reasons given.
  - C: "a start, not a test of the cost claim".
  - D: a lag-28 placebo (false uptake) and a detection-cost measure as steps toward discovery; the audit itself is
    deferred to N3.
- **Instrument versus researcher.** N1 measures a property of the instrument: t0 against a specialist as local history
  shrinks. Owner section 8 lists low-data generalisation as a component (OWNER-NS2-8). Running N1 exercises none of the
  researcher's own steps, and makes no AI calls under route A (R:316). The answer does not say this in so many words.
  Researcher-level tests appear in N3 (R:395) and in G's future experiment (R:591).
- **No outcome treats a t0 win as success** (R:330-335, R:451, R:589; owner section 14).
- **Section 8 fields.** All are present for N1-N3 and the validator passes. N1 gives six competing explanations
  (R:295-300), when a specialist should win (R:303), each comparator's history (R:305), level choice without outcome
  tuning (R:306), five separate cost lines (R:316-320), and a null regime field with an explicit not_applicable
  (R:507).
- **Section 9.** t0_beta is null for all three candidates, and the protocol is alpha-only (R:482). This complies:
  "No beta experiment is authorized in this task" (`NORTH_STAR_CLARIFICATION.md:353`).
- **Section 10.** G gives all three items. The new knowledge is "Exploratory, for one series ... None is demonstrated
  now" (R:589). The future experiment is small: held-out synthetic tasks, the whole request held fixed, at least 3
  replicates for a noise floor, blinded graders (R:591). It builds on elements of the first review's design table and
  does not override that table's choice, which was left to the owner (E5-REVIEW-9, `evidence_pack_v2.md:8391-8408`).
- **Precedence of the owner's text.** Where older records differ, the answer follows the owner: no beta; B1 kept
  separate (I1's "pending anyway for B1" is gone); the 90-day full-sample contest replaced by matched varied history;
  a small compounding comparison (`NORTH_STAR_CLARIFICATION.md:121-123,353,382,413-425`).

**Flags.**
- **Gap, minor: the component list.** N1 lists low_data_generalisation, cheap_trial_and_error and covariate_discovery
  (R:276-281). Only low-data behaviour is decided by the primaries.
  - Discovery: the universe is fixed at two candidates, temperature and the placebo, with "no generation or search"
    (R:309-310).
  - Cheap trial-and-error: only report-only detection-cost curves and a per-route cost log; no outcome uses either
    (R:321-341, R:561).
  - Section_4 itself says the cost part is "a start, not a test" and that N1 only "moves toward" discovery (R:38,
    R:48). Whether a placebo control and a descriptive detection cost are the material move toward D that the owner
    asks for (`NORTH_STAR_CLARIFICATION.md:157-169`) is for the owner to judge.
- **Risk, material: the abstention condition.** The owner asks the researcher to abstain, and name the smallest new
  benchmark or dataset, if public data cannot test the central hypothesis credibly
  (`NORTH_STAR_CLARIFICATION.md:253`). The answer proposes instead, judging the low-data part "partly" testable.
  - By its own account, truncation cannot tell memorisation from a transferable prior, and a supporting result stays
    "confounded by possible pretraining exposure" (R:13, R:202, R:327). Only the non-supporting branches bear on the claim
    free of that confound.
  - The abstention field is null, as the schema expects for a proposal (`engine/propose_v2.py:252`). The answer names
    what would be needed elsewhere (a contamination-free synthetic benchmark, a longer point-in-time archive; R:341,
    R:452, R:590) but not as a "smallest new benchmark".
  - The repository's copy of the authors' report says every real training series ends before 2022
    (`docs/2609.24559.pdf` p.27; not summarised in the pack). If so, the 2024-2025 scored values cannot have been seen
    in training, which narrows the confound for N1. Whether earlier years of French load were seen is not settled.
  - Whether "Partly. It can be tested credibly as exploratory evidence" (R:13) meets the owner's condition, or the mandate's "an important part"
    (`NORTH_STAR_CLARIFICATION.md:234`), is for the owner to judge.
- **Gap, minor: alpha generalised to "t0".** The instrument is "t0-alpha only" (R:482), but outcome lessons and G's
  candidate policy records say "t0" in general: "t0 needs context" (R:333), "t0 is or is not preferred", "a seasonal
  placebo is or is not required for t0 covariate trials" (R:589). E5-REVIEW-7 flagged the same for I1. With beta now
  available (OWNER-NS2-9), such records would not say that they cover alpha only. No reason is required for leaving
  beta out (`brief_appendix_v2.md:271`), and none is given.

## 3. Foundation-model advantage versus ordinary information value

**What holds.**
- **I1's flaw is removed.** I1's comparator contained t0 (E5-REVIEW-7: "the comparator is t0 plus a correction of its
  residuals"). N1's SD and SDT contain no t0, and temperature's gain is measured under each instrument (G_t0, G_S;
  R:539).
- **Confounds named.** The six competing explanations cover memorisation, seasonal anchoring, the specialist's form,
  covariate scaling, weekly-cycle coverage and encoding selection (R:295-300). The Incompetent outcome withholds the
  A(L) reading (R:554).
- **The evidence is stated as it is.** "No non-t0 model using the same information has been run on consumption or
  prices" (A_learned[10]), in E5-ANNOT's corrected wording. B_unexplained[0] frames the open question as instrument
  versus information. A_learned[3] gives wx_ratio on solar as a same-information comparison (L3: -23.8%), and
  A_learned[10] says none exists on consumption or prices.

**Flags.**
- **Risk, material: the pair minimum at L = 7.** SDT's slope is "beta_h = 0 if there are fewer than 4 pairs" (R:491).
  - Under N1's own source and gate rules, an L = 7 window holds 1-4 same-type day pairs per local hour (median 2). If a pair is a
    day pair, 13,118 of 13,128 target-day hours (99.9%) over the 547 calendar days 2024-07-01..2025-12-29 have fewer
    than 4; at L = 14 none do (scratch `fm/pairs.py`,
    calendar only; an independent count in `sk3/pairs_indep.py` agrees).
  - So under that reading SDT(7) = SD(7) and G_S(7) = 0 by rule, not by measurement. A(7) then compares t0 with
    temperature against a specialist without temperature. That mixes the value of the information into the instrument
    contrast at the level that anchors both slopes.
  - Outcome 9 ("G_t0 and G_S are both near zero at 7-14 days ... the scarcity limit is informational", R:338-339)
    cannot be read for the specialist at L = 7.
  - D says "the estimator is well-posed with a pair minimum" (R:450) and does not mention L = 7.
- **Gap, material: the unit of "pairs" is not defined.** Half-hours are pooled per local hour, so each day pair gives
  two observations. Under the half-hour reading about 60% of L = 7 hours get a slope from about 4 points (every hour
  from 0 to 11; about a fifth of afternoon hours) (scratch `fm/pairs_hh.py`). The source is defined per slot, so a
  Wednesday's morning source is Tuesday and its afternoon source the previous Thursday: "pair (d, source(d))" has no
  single day-level meaning. The two readings give different specialists, and so different SDT(7), G_S(7) and A(7).
- **Risk, material: SD does not depend on L.** SD's source is "the most recent same-type day inside the L-day window"
  (R:491). The window only decides whether that day is available.
  - On the 545-day set, SD's source differs from the L = 112 source in 0 of 26,160 (day, slot) cells at L = 14, 28
    and 56, and in 336 cells (7 days x 48) at L = 7 (scratch `fm/sd_invariance.py`).
  - So the specialist's evidence varies with L only through SDT's 24 hourly slopes. The change of A(L) with L is t0's
    own learning curve against a fixed SD base, plus the slope term. How much each part contributes is not measured.
  - The answer notes that SD "needs only one source day" (R:303) and lists the specialist's form as a competing
    explanation (R:297). It draws neither consequence for b_A, or for "History is matched between instruments"
    (R:281). Competing explanation 5 ("At 7 days both routes lose weekly-cycle replication", R:299) applies to SDT's
    slope pairs only.
- **Risk, material: the two gains have different bases.** G_t0 = 1 - MAE(T0HT)/MAE(T0H) and G_S = 1 - MAE(SDT)/MAE(SD)
  (R:539).
  - G_t0 - G_S also reflects how much temperature-related error each base leaves, not only how well each instrument
    takes up temperature. SD carries the load of a day 1 to 8 days earlier (14 days on 7 post-holiday days), and that
    load already embeds that day's weather.
  - MAE(SD) is fixed across L while MAE(T0H) changes with L, so G_t0(L) can move with L through T0H's non-temperature
    error even when uptake is equal. A base difference constant over L would cancel in b_G; this one is not constant.
  - The placebo controls only t0's side. This confound is not among the six competing explanations.
- **Risk, minor: readings beyond one specialist form.** Some outcome readings go from one frozen similar-day form, one
  covariate and one series to a claim about the foundation model or a policy rule, without "against this form":
  "For physically understood covariates an explicit transformation is preferred" (R:335); a policy with no scarcity
  qualifier (R:331); "the solar wx_ratio precedent generalises" (R:333); "Each outcome changes a research-policy rule"
  (R:451). E5-REVIEW-7 flagged the same pattern in I1. G does scope its policy records as exploratory and for one
  series (R:589), so the outcome texts should be read under that scope.
- **Risk, minor: mechanism hedges.** Outcome 3 carries a hedge for pretraining exposure (R:327). Outcomes 6 and 7 carry
  none for the answer's own explanations 4 and 5 (scaling, day-type coverage), and no arm separates them. The practical
  reading (t0 as configured is not the low-data instrument on this series) would survive them; the mechanism
  ("consistent with the roughly 1,024-step claim", R:333) is unhedged.

## 4. Are data scarcity and regime change tested credibly?

**Data scarcity: what holds.**
- **History span is matched.** t0's context is the 48L steps ending at the gate (`solarbench/forecasters.py:445-451`),
  the specialist is confined to the same L days, and a history-budget check enforces the upper bound (R:515).
- **t0 accepts 7-day contexts.** The installed package sets only 1 <= context <= input width
  (`t0/model/model.py:230-232`) and left-pads: 16 padding steps at L = 7; 14 to 112 days are patch-aligned
  (`t0/model/rollout.py:115`). The levels bracket the authors' 1,024-step figure (1,024 x 30 minutes = 21.3 days;
  T0-REPORT).
- **The pretraining caveat** is accurate for what the pack says (no record documents the training corpus) and is
  carried into outcome 3 (R:327) and B_unexplained[2] (R:201).

**Data scarcity: flags.**
- **Error, material: what the design measures.** Section_4 says N1 "tests how much local evidence each route needs to
  extract history structure and covariate value" (R:12). By the protocol's rules the specialist's history structure is
  one source day at every L (section 3). So b_A compares t0's dependence on context with a rule whose structure is
  fixed.
- **Risk, material: the short end sets part of b_G.** The levels are equally spaced in log2 L (2.81 to 6.81), so the
  slope weights are (-2, -1, 0, 1, 2)/10 and L = 7 and L = 112 have the largest leverage (hat value 0.6 each).
  - If G_S is g points at L >= 14 and 0 at L = 7 by rule, and nothing else changes with L, then b_G = -0.2g per
    doubling. At g = 12.5 points b_G reaches -2.5, the edge of the FLAT band; at g = 15 it is -3.0 (arithmetic; scratch
    `scarcity_pit/slope_leverage.py`). For scale, t0's temperature gain at 90 days is +19.3% (L51).
  - The direction is fixed only if a fitted slope would have helped the specialist at L = 7 (then toward SUPPORTS). If
    a noisy slope would have hurt it, the rule pushes the other way.
- **Gap, minor: a 7-day window does not always contain the day type.** On 7 sample days the same weekday one week
  earlier was a public holiday (typed Sun-or-holiday), so SD(7) has no source: 2024-11-08, 2024-11-18, 2025-04-28,
  2025-06-16, 2025-07-21, 2025-08-22, 2025-11-08 (checked against `solarbench/probes.py:176-180`). The protocol gives
  no fallback. Under its intersection rule these days leave every level, giving 538 days (181 in 2024), a non-random
  calendar subset. This contradicts "one weekly cycle (the minimum containing every day type)" (R:499).
- **Gap, minor: scaling has no control.** Known-future rows are standardised over context plus horizon
  (`t0/scaler.py:107-139,181-184`), so the same temperature reaches t0 on a different scale at each L. The answer names
  this (R:298). Unlike explanations 2 and 3, it has no assigned check, and no outcome mentions it. Neither b_A nor b_G
  can attribute a short-history effect in t0 to evidence rather than to scaling.
- **Risk, minor: what the placebo can show.** The package standardises each known-future row by its own window mean
  and standard deviation.
  - Neither real temperature nor the placebo gives t0 its seasonal level on any valid cell. In an offline check of the
    installed scaler (no forecast), adding 10 to a covariate changed valid cells by at most about 1e-5 at L = 7 and L = 112;
    doubling it changed nothing; only the 23 trailing padding cells moved, by about 0.6 (scratch
    `scarcity_pit/t0_checks.py`). Whether t0 uses those padding cells is unknown.
  - What the placebo carries is the 28-day-old shape inside the window: the daily cycle, old day-specific weather, and
    the seasonal trend that fits in the window. That trend is smallest where the override is read: the largest
    within-window swing of an annual cycle of amplitude A is 0.147A at L = 7 and 0.266A at L = 14, against 1.658A at
    L = 112 (scratch `scarcity_pit/placebo_coverage.py`).
  - The placebo still separates day-specific from non-day-specific uptake. But calling a high P(L) "seasonal
    anchoring" (outcome 8, the override, the B1 caveat; R:336-337, R:554) relies on a mechanism the package mostly
    removes. At short L a high P(L) could equally come from the daily shape both series share. INFRA-T0 gave the
    researcher the standardisation fact.
- **Gap, minor: the channel is validated only at 90 days.** The known-answer gate, and any re-gate, builds windows at
  `am.CONTEXT_DAYS` = 90 (`engine/referee/known_answer.py:50`; `engine/catalogue.py:17`). Nothing checks at 7-112 days
  that a planted signal is used or that noise does not break t0. Noise cost t0 5.2% at 90 days in one period (L17).
  The answer lists how this harm scales with context as unknown (R:221).
- **Gap, minor: pretraining, narrowed by a source outside the pack.** The authors' report in the repository says the
  real corpus is a public benchmark's pretraining split and that "Every real series of the corpus ends before 2022"
  (`docs/2609.24559.pdf` p.9, p.27). The pack's T0-REPORT record does not contain this. It bears on the strength of
  the answer's caveat, not on its accuracy for the pack.

**Regime change.**
- **Holds.** N1 makes no regime claim. The answer says plainly that point B is argued, not tested (R:26-27). The
  April-October stratum is report-only and "explicitly not a regime" (R:507).
- **Holds, in part.** N2's own judgement that it is not credible now rests partly on pack facts (no point-in-time
  weather for 2020, INFRA-DATA; five public holidays in the break and recovery windows, `solarbench/probes.py:176-180`)
  and on the mechanical point that a short-memory rule recovers by construction (R:361-364). It also rests on outside
  facts the answer asserts without a record: the decree-based window dates (R:372) and school closures (not in the
  pack; not verified by engineering).
- **Risk, minor: the basis for "cannot be tested credibly now".** It rests on pack facts (temperature from 2024-02-06;
  an undocumented training corpus) and on the premise in section 1, error 1. The 2022-pretraining premise runs against
  the authors' report (above). The conclusion does not depend on that premise.
- **Gap, minor: "its only crisp break (2020)"** (R:452). The answer's "earlier data" (R:353) includes
  2022-01-01..2024-02-05, which is inside the discovery zone and scorable (`engine/catalogue.py:67-71`). Section_4 sets
  aside the one candidate it names there, the 2022 demand reduction, as having a diffuse onset (R:27, uncited). No
  other candidate in that span is examined, and no pack record surveys dated breaks.

## 5. Is the comparator fair?

**What holds.**
- **Same history and inputs.** "Every decision comparator, t0 and specialist alike, reads exactly the L days before
  the gate" (R:491). Both use the same raw archived lead-3 temperature and the same holiday calendar, both are
  recomputed at every origin, and the specialist is frozen untuned before any run (R:561, R:568). Neither route is
  denied an input the other receives.
- **Specialist inputs are legal.** Pair days and sources lie inside the window that ends at the gate, each source is
  chosen by the rule at its own gate, and both temperatures are archived forecasts. The backtest asserts source times that a method reports (`solarbench/backtest.py:168-178`).

**Flags.**
- **Risk, material: the competence gate is a floor.** V2 is "SDT(56) beats blend_50 with a 95% lower bound above 0"
  (R:531).
  - Plain t0 beats blend_50 by +47.2% (L7), and t0 + holiday by +49.6% in 2024 (R-EXP3-3; `README.md:1013`). V2 has
    no minimum margin, runs at one level, and does not require SDT to beat SD, so a specialist whose temperature slope
    adds nothing, or harms, can pass.
  - The minimum-size question E5-REVIEW-6 gap 6 raised for I1 ("rules out a useless correction but not a weak one")
    is not among the gaps D says are closed.
  - The 2023 selection of blend_50 (`engine/catalogue.py:55`) does not show how likely V2 is to fail: the pack has no
    per-candidate consumption MAEs for 2023, and SD differs from the rules compared then.
- **Risk, material: functional form is not tested where it matters.** SDT fits one no-intercept linear slope per hour,
  pooled across day types and across the window (R:491). The catalogue's own temperature transforms have thresholds
  (hdd15, cdd22; `engine/catalogue.py:46-50`). Windows that span both the winter and summer catalogue scopes: 0 days at
  L = 7, 14 and 28; 76 days (13.9%) at L = 56; 243 days (44.6%) at L = 112 (scratch `skeptic_fm/span.py`, calendar
  only). The checks the answer cites for form (R:297) do not test it: V2 is against blend_50 at one level, and the
  April-October stratum "never decides anything" (R:507). G_S can change with L because of the form, and b_G carries
  that into outcome 7's policy reading (R:335).
- **Risk, minor: holiday information reaches the routes differently.** The specialist treats a holiday as the latest
  Sunday at every level. t0 gets a 0/1 flag, standardised over the window and then passed through arcsinh. A lone
  holiday's ones become 2.74 at L = 7 and 9.91 at L = 112 before arcsinh (1.73 and 2.99 after); with one other holiday
  in the window they become 7.47 before and 2.71 after at L = 112 (`t0/scaler.py:20,107-138,172-184,198-200`;
  `t0/model/model.py:89`). t0's
  context holds another holiday for 2 of 16 holiday target days at L = 7 and for 16 of 16 at L = 112. Holiday days are
  about 3% of the sample. Direction and size are not measured.
- **Risk, minor: selection.** The raw encoding was chosen for t0's channel at 90 days on these days (L55; E5-POWER pair
  b: raw beat hdd15 by +7.1% [3.4, 11.9]), and N1's 545 days lie inside the 602 selection days. "The same raw encoding
  for symmetry" (R:300) is not the same as sharing the selection, and no reading rule discounts it, as E5-REVIEW-7
  noted for I1. The answer acknowledges the bias but not which way it moves the slopes.
- **Risk, minor: revised load inputs.** Every arm reads RTE's revised series, not the values available at 12:00 on D-1
  (`README.md:655-667`; `engine/data.py:23-24`). That is the same for all arms, but SD copies single recent values: it
  reads the last legal day on 28.5% of days, mostly Wednesday and Thursday mornings (scratch
  `scarcity_pit/sd_specialist_calendar.py`). Whether SD's accuracy, and with it A(L), holds on real-time inputs is
  untested; the answer does not mention it.

## 6. Are the cost claims measurable?

| Measure (R:546) | Recorded today? | What is missing | Evidence |
|---|---|---|---|
| AI calls and tokens | Yes: every completed call is a ledger `research_call` with usage (seqs 49-76; seq 72 failed without usage) | The protocol-revision and interpretation calls (R:316) have no engine mode yet; `propose_v2` refuses a second answered v2 call | Seq 76: 161,958 input + 50,481 output + 11,356 cache-write tokens = 223,795, 11.2% of the 2,000,000 daily cap (INFRA-COST); `engine/propose_v2.py:16,414-418` |
| Evaluations | Yes | Nothing; owner probes are uncharged `probe_result` entries whose arm series can be counted | `engine/referee/budget.py:18-20`; INFRA-BUDGET |
| Engineer-hours per bucket | No: recorded nowhere | Who logs, how each work item is booked, where the log is kept; no item for it in the 4.5-6 days | grep for engineer-hour, person-hour, time_spent, effort_log: matches only the answer's files |
| Runner minutes per route and level | No: one `elapsed_s` per probe, covering download, windows, leak checks and every method; Actions job durations are not stored | The protocol does not say how runner minutes are attributed to a route and a level | `engine/discover.py:72,140`; INFRA-COST |
| Approval-to-readout time | No: no approval moment is recorded for N1 | No recording rule is stated | R:546 |
| Cost per resolved primary question | Not computable | "Resolved" is not defined (which of SUPPORTS, CONTRADICTS, FLAT, INCONCLUSIVE, Invalid, Incompetent?); no rule for zero resolved; both primaries span both routes, so a per-route figure is undefined. Defining it after results would be a choice made with the outcome known | R:546, R:554; E5-REVIEW-9 ("cost can also fall because ambition does") |

- **Holds.** In its cost fields the answer claims no more than a first datum: "With one covariate this is a first
  datum, not a test of the cost hypothesis" (R:546); "a start, not a test" (R:38). None of the ten outcomes reads a
  cost measure.
- **Gap, minor: booking rules.** The protocol defines the t0 route as "adding temperature and the placebo" and the
  specialist route as "designing and testing the slope model" (R:546). It assigns none of the other items (loading fix,
  per-arm context field, history-budget leak control, readout: about 2.5-3 of the 4.5-6 days). The per-arm context
  field and the read lead-in serve both routes (t0's context and the specialist's 112-day window;
  `engine/arms.py:24-25,78`; `engine/discover.py:32`), so where they are booked is a choice. The
  earlier t0-specific cost of gating temperature (a failed gate, an owner rule change, a re-gate: L17, L24, L25) is
  not counted. As booked, the first datum would show roughly 0.5 day on the t0 route against 1.5-2 days on the
  specialist route, partly because of the booking. Whether to count sunk work needs an owner decision.
- **Risk, minor: cheapness read from accuracy measures.** Outside the cost fields, the answer calls the detection-cost
  curves "the cost of a discovery trial" (R:281), and outcome 4 teaches "Being cheap for covariate trials is not
  supported by low-data uptake on this series" (R:329); G sends N3 to "short history, where the instrument is
  cheapest" (R:590). Scored days to detection and uptake are not the research-effort cost of owner point C ("materially
  less task-specific modelling work", "valid information gained per research effort"; OWNER-NS2-4).
- **Gap, minor: the detection-cost measure is underspecified** (R:539): where the 20 subsamples sit, how much they
  overlap, the level of the "one-sided bootstrap lower bound", and whether "contiguous" means calendar days or scored
  days. On about 545 days, 20 disjoint windows fit at none of the four lengths (19, 9, 4 and 2 fit for 28, 56, 112 and
  224 days), so at 56-224 days the 20 results are strongly dependent (scratch `skeptic_cost/check1.py`). It decides
  nothing.
- **Gap, minor: the non-chosen candidates' costs.** N2's 3-5 engineer-days is not itemised; N1 budgets 2.5-3.5 days
  for the three parts N2 reuses, leaving about 0.5 to 1.5 days (at most 2.5) for N2's own work (zone and catalogue change, a loader beyond
  the 100-day lead-in, a long-window specialist, an indicator with an issue-time bound, a readout). N3's 4-7 days is an
  unlabelled increment after N1 and omits a Benjamini-Hochberg implementation and a decoy catalogue entry. N3's
  compute (2-4 h) is not understated: 7 x 545 = 3,815 forecasts is 24-47 minutes at recorded rates (N2: R:377-381;
  N3: R:433-434).

## 7. Does every outcome teach something?

**What holds.**
- The precedence Invalid, then Incompetent, then the primaries' readings is stated (R:554).
- The predicted signs match the definitions: a t0 advantage that grows as history shrinks gives b_A < 0, and a larger
  G_t0 - G_S at short L gives b_G < 0. The FLAT band arithmetic holds (2.5 x 4 doublings = 10 points). Slopes are
  computed from pooled sums inside each resample, as the engine's metrics do (`solarbench/metrics.py:104-164`).
- The pre-freeze check of whether FLAT is reachable takes up a lesson from E5-REVIEW-5 (R:531, R:554).
- No outcome treats a t0 win as success (section 2).

**Flags.**
- **Error, material: the labels can both hold.** SUPPORTS needs a point below 0 with Holm one-sided p < 0.05;
  CONTRADICTS a 95% CI above 0; FLAT a 95% CI within +/-2.5 (R:554).
  - Example: b = -1.2 with SE 0.6 has CI [-2.38, -0.02], inside the band (FLAT), and one-sided p = 0.023 (SUPPORTS at
    either Holm step). The mirror case is CONTRADICTS and FLAT.
  - The overlap needs a slope SE of at most 0.638 (Holm step 1) or 0.694 (step 2). With per-level SDs of 2.3-2.7 points and correlations of 0-0.9 between levels, b_A's SE is about 0.23-0.85
    (below), so the overlap is not a corner case.
  - No order among the readings is stated, and the outcome map draws opposite lessons from them: outcome 3,
    "concentrates where local evidence is scarce", against outcome 5, "does not depend on history length" (R:327,
    R:331).
- **Error, material: the outcome map is not partitioned.** D claims it is "partitioned with precedence (E5-REVIEW-6)"
  (R:450). Enumerating the rules (scratch `sk2/omap_check.py`):
  - **Overlaps:** outcomes 3 and 5 (b_A SUPPORTS and FLAT, b_G SUPPORTS, placebo under 0.5, t0 ahead at every level);
    3 and 7 (both SUPPORTS, G_S >= G_t0 at every level); 4 and 9; 5 and 7.
  - **Holes:** b_A FLAT with t0 not ahead at every level and b_G FLAT or SUPPORTS; b_A INCONCLUSIVE with b_G SUPPORTS
    or FLAT, if outcome 10's "the slope CIs" means both.
  - **Undefined conditions:** "ahead at every level", "near zero", "A(7) and A(14) not above A(112)" have no stated
    threshold.
  - **FLAT stated two ways:** E falsifies the thesis if b_A is FLAT with A(7) and A(14) not above A(112) (R:554); C
    reads "b_A flat, with t0 ahead at every level" as "scarcity is not the mechanism" (R:330-331).
  - E5-REVIEW-6 item 2 asked I1 to close exactly this (`evidence_pack_v2.md:8204-8211`).
- **Risk, minor: asymmetric thresholds.** At Holm's second step SUPPORTS uses one-sided 0.05, while CONTRADICTS always
  needs a 95% CI above 0 (about one-sided 0.025) (R:554, R:561).
- **Risk, material: the placebo override can fire on noise.** P(L) = (1 - MAE(T0HP)/MAE(T0H))/G_t0(L) has no
  interval, no minimum denominator and no sign rule; a negative over a negative is positive (R:539).
  - A simulation with a true placebo gain of 0 and an SD of 2.7 points per gain (the bootstrap SD of a 90-day t0 pair on the 545 days, computed here from seq 51's per-day errors, is 2.65; E5-POWER
    records 2.58 on 602 days) gives these chances of P >= 0.5 at a single level, for a true G_t0 of 1, 2, 3, 5 and
    10 points: 0.475, 0.412, 0.324, 0.166, 0.017 at a correlation of 0.5 between the gains; 0.344, 0.318, 0.284, 0.199,
    0.049 at a correlation of 0 (scratch `skeptic_cost/check1.py`, 400,000 normal draws).
  - The override fires on L = 7 or L = 14, two chances, and outcome 9 contemplates G_t0 near zero there (R:338).
  - Outcome 8 extends the caveat to B1's 90-day gain, but no placebo arm runs at 90 days (R:337, R:482).
- **Risk, minor: a non-monotone curve reads as FLAT.** The answer expects t0 may degrade below about 21 days (R:303).
  A = (2, 7, 7, 7, 2) points at L = 7..112 has slope 0, and with t0 ahead at every level outcome 5 would read it as
  "does not depend on history length". Outcome 5 has no curvature or per-level condition (E's falsification clause has one, R:554); per-level contrasts
  are otherwise descriptive (R:561).
- **Risk, minor: Invalid may come from a data revision.** V1 requires T0H(90) and T0HT(90) within 0.5% MAE of seq 51
  (R:531). Seq 51 recorded no vintage or target hash (payload `data` keys); the 2025 rows were "consolidated" when C1
  ran on 2026-09-25 (C1-CONFIRMATION); RTE makes rows definitive in the second half of the following year
  (E5-REVIEW-2), around when N1 would run. The Invalid lesson reads every V1 failure as plumbing and says "Fix and
  rerun" (R:323), which cannot remove a data cause. The protocol also does not say what happens if vintage counts or
  hashes differ between N1 probes (R:458).
- **Risk, material: whether FLAT is reachable is not settled.**
  - b_A's 95% half-width depends on the per-level SD of a t0-against-specialist contrast and on the correlation
    between levels, neither recorded. With per-level SDs of 2.3-2.7 points (three of the t0-against-t0 analogues computed here on 545 days, which span
    1.5-3.0) it is about 0.5-1.7; with
    cross-family SDs computed here from recorded per-day errors (t0 against RTE, 5.8-8.7 points) about 1.1-5.4, for
    correlations of 0 to 0.9. Per-day errors of the non-t0 rule blend_50 are also on the ledger (seqs 12, 14, 27, 28, 31, 39, 41 and 45) and were not used.
  - For b_G, taking each gain at the within-family SD computed here gives about 1.0-2.3 (correlations 0-0.8), where
    P(FLAT | true slope 0) falls to about 0.1 at the upper end. G_S's variance is unrecorded, so b_G's reachability is
    not settled either.
  - P(FLAT | true slope 0) is 0.81 at a half-width of 1.5, 0.38 at 2.0 and 0.07 at 2.4 (scratch
    `skeptic_cost/check1.py`; normal approximations on analogue data, not measurements).
  - The promised pre-freeze estimate uses "the analogue pairs" (R:531), which are all t0 against t0 at 90 days
    (`docs/experiment_5/feasibility_power.py:42-47`). They contain neither the specialist's variance nor the
    between-level correlation. The cut-off (FLAT declared unreachable only above 2.5) leaves FLAT nominally reachable
    where it is improbable. If FLAT is declared unreachable, outcome 5 and the FLAT route to falsification disappear,
    a true-null slope reads INCONCLUSIVE, and the map is not restated for that case.
- **Gap, minor: some outcomes have no next decision.** G maps four families (both supported; flat or contradicted;
  placebo dominates; inconclusive; R:590). Outcome 4 and outcome 9 get no next step in G or in their own lessons;
  Incompetent has one only in its own lesson (R:325). N3's history level is "fixed by N1's pre-declared outcome map"
  (R:313, R:421), but no rule maps an N1 result to a level and "short history" is not defined, so the level would be
  chosen after N1's per-level results are seen.
- **Gap, minor (N3, not chosen).** N3 lists three outcomes; none covers t0 missing an expected positive, or the
  specialist route finding more or finding it more cheaply (R:436-442). Its Benjamini-Hochberg control at q = 0.10
  exists nowhere in the code (the referee and every frozen spec use Holm: `engine/referee/stats.py:6,111`), no reason
  is given for it, and the lag-28 placebo sits inside the family while also serving as a false-positive check, without
  a stated null.

## 8. Is the scope proportionate?

**What holds.**
- **Each arm feeds a statistic.** A needs T0HT and SDT; G_t0 needs T0H and T0HT; G_S needs SD and SDT; P needs T0HP.
  Five levels give the slope its spread over 7-112 days (R:539).
- **The answer's arithmetic reproduces.** Its work items sum to 4.5-5.5 engineer-days (stated 4.5-6; R:318); its
  forecast count is 3 x 5 x 545 + 2 x 545 = 9,265 (stated about 9,300); 10,800 forecasts at 0.37-0.74 s is 1.11-2.22 h
  (stated 1-2.2 h; R:319).
- **Comparable to I1.** Engineering costed I1 at about 5-8 engineer-days and 1-3 h of runner time
  (`FEASIBILITY_REVIEW.md:26-28`). N1 needs no new source, no ERA5 door and no beta, and stays exploratory.

**Flags.**
- **Gap, minor: the compute basis.** The 9,300 figure assumes t0 arms are forecast only on the common days. The engine
  forecasts each named method on every eligible day of a fixed catalogue period, and arms without a weather provider
  are eligible on every window (`engine/discover.py:35-39,79-80,86-90,108`; `engine/catalogue.py:67-71`).
  - That gives about 15,700 t0 day-forecasts if the probes use period ALL, or about 11,300 with Y2024 and Y2025c:
    about 1.2-3.2 h at the recorded rates before leak-check rebuilds (scratch `skf/counts.py`). Shorter contexts may be
    faster; that is not measured.
  - The protocol does not name probe periods or a day restriction (section 11, open choices).
  - With at most 3 arms per probe (`engine/catalogue.py:73`), the 27 series need at least 9 probes if the specialists
    run as arms, against the stated 6-8. Each probe fits the 120-minute step: a worst case of 3 non-weather t0 arms
    over ALL is about 4,400 forecasts, about 54 minutes at 0.74 s.
- **Risk, minor: items missing from the effort list.**
  - Vintage recording: E.target requires nature counts and a target hash in every probe (R:458), but the code drops
    `nature` (`solarbench/odre.py:102-117`; `engine/data.py:89-94`), and E5-REVIEW-2 marked it "needs change".
  - Whether the guards engineering costed for I1's non-plain arms (about 0.5 day, E5-REVIEW-3 change 4) are needed for
    the specialist and placebo arms is not said.
  - Engineer-hour and approval-time recording (section 6).
  - The read lead-in (section 9) and the leak-check definitions for the specialist and placebo (section 9).
- **Risk, minor: the re-gate.** The cost line budgets a known-answer gate run only under the placebo item, "if
  fingerprinted files change" (R:318). The in-place builds touch fingerprinted files: per-arm context sits in
  `engine/arms.py` (`:24-25,78,121-124`), a lag transform in `engine/covs.py` (`:77-81,137-155`), and both are in
  `FINGERPRINT_FILES` (`engine/gates.py:38-39`). Weather probes are refused until a pass at the new fingerprint
  (`engine/__main__.py:180-184`). The gate is a real t0 run that can fail (L17 failed at 1.0521; L25 1.0013, L36
  1.0132), and it tests the channel only at 90 days.

## 9. Data existence and point-in-time status of the proposed design

| Element | Exists? | Point-in-time status | Evidence |
|---|---|---|---|
| Consumption target (ODRÉ eco2mix-national-cons-def) | Yes; seq 51 read 2021-09-23..2025-12-31 | Values up to the gate slot only. They are RTE's revised figures, not the real-time vintage; the same for all arms (section 5) | `engine/data.py:23-24`; `README.md:655-667` |
| Target vintage | Not recorded by seq 51 or any probe | 2025 rows "consolidated" on 2026-09-25; definitive in the second half of the following year | C1-CONFIRMATION; E5-REVIEW-2; `solarbench/odre.py:102-117` |
| Lead-3 temperature (12 points, 2023 consumption weights) | Yes; no gaps 2024-02-06 00:00 to 2025-12-30 23:00 UTC | Issue bound = valid time - 62 h; the backtest refuses later cells and the referee recomputes the bounds; 25 h margin at the gate at every seq 51 leak-check origin | `engine/covs.py:24-32`; `solarbench/covariates.py:154-156`; `solarbench/backtest.py:155-167`; `engine/referee/leakcheck.py:54-58` |
| Lag-28 placebo | Derivable from the same archive; covers the sample at L = 112 from 2024-06-26 | Each value is about 30.6 days older than its valid time when used: a wide margin | scratch `scarcity_pit/placebo_coverage.py` |
| Holiday calendar | Yes | Known in advance | `solarbench/probes.py:176-180` |
| Specialist training pairs | Built from the above | Legal at D's gate as specified | R:515; `solarbench/backtest.py:168-178` |
| Data from 2026 on | Not read by any candidate | The data N1's scored forecasts use reach back at most about 140 days before 2024-07-01 (to about 2024-02-11), after the archive start; engine reads over period ALL start 2021-09-23 (seq 51); all before 2026 | R:523; `engine/zones.py:46-53` |
| N2: ODRÉ consumption 2017-2020 | Both doors can request it (the solarbench door refuses dates from 2025; the engine door, `engine/data.py:43-48`, refuses only the forward zone); no record shows complete 30-minute data back to 2017; the earliest read on record starts 2021-09-23 | `README.md:645` says rows become definitive in the second half of the following year, so 2017-2020 rows would be expected definitive; not checked. Coverage is not in the pack; not verified by engineering | `solarbench/odre.py:49-50`; ledger seqs 12-69 |
| N2: weather for 2020 | None wired; ERA5 is a reanalysis, never point-in-time | Whether an archive outside the wired sources exists is not in the pack | INFRA-DATA; INFRA-DATA-HISTORY |
| N2: lockdown indicator | Not in the pack | Dates and the 12:00 time are not in the pack; not verified by engineering. No announcement time is given; the answer requires fixing them from the decree record before any data are read (R:372-373). Its licence is not stated, although the standing rules require it | `brief_appendix_v2.md:262` |
| N3: consumption-weighted radiation | Archive wired from 2024-03-08 (2024-03-08 + 112 days = 2024-06-28, before 2024-07-01) | Same issue bounds as temperature; needs a catalogue entry and a gate | `engine/arms.py:51-64,92-102`; `engine/catalogue.py:43-45` |
| N3: school-holiday calendar | No source in the code | "Published years ahead" (R:424) is not in the pack; not verified by engineering. The answer flags its source and licence as unchecked | grep for school, scolaire, vacances: no hits |

**Point-in-time and data details the protocol leaves open.**
- **History-budget check, boundary cases.** The first context slot's temperature interpolates hourly stamps at 10:00
  and 11:00 UTC in summer (11:00 and 12:00 UTC in winter), one of them exactly L days before the gate (`engine/covs.py:90-104`). The placebo inside the window is
  built from temperature 28 days older than the window. A literal "rewriting data older than the L-day window must
  leave each forecast identical" (R:515) could fail on both. The existing harness rebuilds every method from a poisoned bundle
  (`engine/referee/leakcheck.py:78-139`).
- **Weather positive control against the placebo.** The control shifts legal values valid within 48 h after the origin
  and requires the forecast to move (`engine/referee/leakcheck.py:117-134,139`). A 28-day-lagged read never uses those
  values, so T0HP would not move; one failed method marks the probe INVALID (`engine/discover.py:103-106,135`), and V3
  then makes N1 Invalid (R:554). The protocol does not say how the placebo is carried or checked.
- **Positive control for the specialist.** "A legal pre-origin change must move them" (R:515). The existing control
  rescales only the last 24 h before the origin (`engine/referee/leakcheck.py:104-111`). SD reads that span on 156 of
  545 days, mostly Wednesdays and Thursdays (scratch `skeptic_fm/lastday.py`), and on none of the period endpoints a
  probe could use except 2024-01-01, the first window of Y2024 (scratch `skeptic_spit/ctrl_origins.py`); because the
  harness requires the control to move at every checked origin (`engine/referee/leakcheck.py:90,112`), the check would
  still fail. The history-budget check's "a change inside the window must
  move it" is likewise undefined for SD and for SDT(7) with its slope off. The protocol does not say which change
  applies to which arm.
- **The lag's unit.** 28 local days and 1,344 UTC half-hours differ by one hour across a clock change, on up to 82
  sample days (35 in April and October) (scratch `scarcity_pit/lag_dst.py`). The engine's grid is UTC
  (`solarbench/covariates.py:111-114`). The protocol does not say which unit the lag uses.
- **The read lead-in.** Engine reads start 100 days before the scored period, tied to the 90-day context
  (`engine/arms.py:24-25,78`). L = 112 with the lag-28 placebo needs about 141 days, so a probe whose period starts on
  2025-01-01 would lose early-2025 days unless the lead-in changes. Probes over ALL, like seq 51, are unaffected. The
  protocol does not name its probe periods.
- **Reading versus scoring before 2022.** The engine reads before the discovery zone; it refuses to score there
  (`engine/zones.py:46-63`). N2 would also need loading beyond the 100-day lead-in for its 2017-2019 fit.

## 10. Regime boundaries: defined independently of the results?

- **N1, holds.** No regime is defined (R:507). The report-only April+October stratum is the months outside both
  catalogue season scopes (`engine/catalogue.py:63`: winter 11-3, summer 5-9). That literal was committed in `cd821be`
  at 2026-09-26 12:34:06 UTC (`git log -S`), before the first temperature result on the ledger (gate seq 17, 12:46:29
  UTC the same day). E5-POWER counts 90 days in April or October.
- **N1, risk, minor.** The stratum's 90-day result can be recovered from the pack: for 2025 April and October, the
  raw-temperature arm's mean daily MAE is 1220.4 MW against 1578.0 MW for the accepted arm (+22.7%), against +21.0%
  for all of 2025 on matched days (E5-REVIEW-5) (scratch `scarcity_pit/ao_stratum.py` on LEDGER-PER-YEAR). The value is close to the full-year
  figure, the stratum decides nothing, and the answer discloses that its slices are not blind (R:568).
- **Holds.** Calendar years are not treated as regimes (LEDGER-PER-YEAR; OWNER-NS2-4: "Do not manufacture a regime
  definition after seeing results").
- **N2, holds.** The boundary comes from government decrees and is to be fixed "before any data are read" (R:372-373),
  as owner section 8 asks (`NORTH_STAR_CLARIFICATION.md:294-298`). No 2020 consumption result exists in the pack or on
  the ledger (consumption `per_day` dates run 2022-01-01..2025-12-30), so it was not drawn after seeing results.
- **N2, gap, minor.** The dates and the 12:00 effective time are not in the pack; not verified by engineering. No
  announcement time is given, so the first gate at which the indicator becomes usable cannot be worked out from the
  proposal. The answer declares a rule for fixing them.
- **Gap, minor: "a future dated break".** D names "archived point-in-time covariates spanning a future dated break" as
  one route to a credible regime test (R:452). Any break after 2025-12-31 lies in the forward zone, readable only
  through the vault, once, for a frozen claim batch, with the owner's approval (`engine/zones.py:7-8,46-53`;
  INFRA-ZONES), and no new batch can be frozen before B1 opens after 2027-04-01 (INFRA-VAULT). D does not apply this
  constraint to that route; the answer states the freeze constraint only for N1's results (R:13).
- **Gap, minor: the synthetic route.** The drafted benchmark has hidden change points and regime-conditional
  mechanisms, but as drafted it "does not exercise t0" (section 1). It is not a regime test of t0 as drafted.

## 11. What it would take to run N1

**Approvals and decisions (owner).**
1. **t0 loading on the probe path.** The answer calls it "the owner-approved t0 content-hash loading fix" (R:578) and
   "a content-addressed loading fix approved by the owner" (R:255). The answer uses "owner-approved" in the
   same sense for N2's zone extension (R:452), so it may mean "to be approved" (E5-ANNOT); either way no recorded
   owner decision exists. The first
   review lists the probe-path loader as its own approval item and leaves "one fix or two" to the owner (E5-REVIEW-10
   items 1 and 4, `evidence_pack_v2.md:8419-8424,8435`; E5-REVIEW-3, `:8070-8076`). The answer does keep B1's vault fix
   separate. B1's fix is not to be implemented unless separately authorised (`NORTH_STAR_CLARIFICATION.md:423`).
2. **The route.** Route A: owner-dispatched probes, 0 evaluations, no API calls. A researcher-submitted route would
   need a loop change outside the approved scope (section 1).
3. **Who closes the protocol's open choices** (below): the researcher, in a recorded revision call the answer budgets
   (R:316) but for which no engine mode exists, or the owner. Engineering does not close them.
4. **The engine build** (table below), and a known-answer re-gate if fingerprinted files change.
5. **A frozen protocol and readout script, approved before any run.**

**Open choices that need a decision before any freeze** (listed, not answered):
- the unit of SDT's "4 pairs" (day pairs or half-hour observations);
- what SD and SDT do at L = 7 when no same-type source lies in the window, and which exclusion rule fixes the day set
  ("days dependent on them");
- the order between SUPPORTS, CONTRADICTS and FLAT; a rule for combining b_A and b_G readings into outcomes; thresholds
  for "ahead at every level" and "near zero"; whether outcome 10 means one CI or both;
- a minimum denominator, interval or sign rule for P(L);
- whether V2's single-level bar (SDT(56) against blend_50, R:531) is the intended competence test at the other levels;
- the positive control for SD and SDT, the placebo's treatment in the weather control, and the history-budget check's
  boundary cases;
- the lag-28 unit (local days or UTC half-hours);
- the probe periods (or a day filter) and the read lead-in;
- what happens if vintage counts or target hashes differ, between N1 probes or against seq 51;
- cost recording: engineer-hour logging and booking, whether sunk gating cost counts, the approval moment, and what
  "resolved" means;
- the placement and overlap of the detection-cost subsamples;
- whether N1's policy records are scoped to t0-alpha.

**Engineering's estimate of the changes** (estimates, not measurements):

| Change | In the answer's list? | Estimate | Evidence |
|---|---|---|---|
| Probe-path t0 loading fix | Yes, 0.5 day | About 0.5 day, as for I1 | `FEASIBILITY_REVIEW.md:141` |
| Per-arm context field | Yes, 0.5-1 day | As stated; the 100-day lead-in is tied to the global context and is not mentioned | `engine/spec.py:19`; `engine/arms.py:24-25,78`; `engine/discover.py:32` |
| History-budget leak control | Yes, 0.5 day | As stated, once its boundary cases are decided | `engine/referee/leakcheck.py:78-139` |
| Specialist module (gate and pair rules, tests) | Yes, 1.5-2 days | As stated, once the pair unit, the L = 7 fallback and its positive control are decided | R:318 |
| Lag-28 placebo, plus a gate run if fingerprinted files change | Yes, 0.5 day + gate | A re-gate is likely for in-place builds; it can fail | `engine/gates.py:38-39` |
| Frozen readout script | Yes, 1 day | As stated | R:318 |
| Vintage (nature counts) and target-hash recording | No | Not estimated here | `solarbench/odre.py:102-117`; E5-REVIEW-2 |
| Guards against citing or freezing specialist or placebo arms as plain arms | Not said whether needed | About 0.5 day for I1's equivalent | E5-REVIEW-3 change 4 |
| Probe periods or a day restriction (the protocol names neither; the 9,300 basis assumes common days only) | No | Not estimated here | `engine/catalogue.py:67-71` |
| Engineer-hour and approval-moment recording | No | Not estimated here | section 6 |

The answer's own items sum to 4.5-5.5 engineer-days. Engineering gives no total for the unlisted items.

**Compute and budget** (arithmetic on recorded rates; estimates):
- t0 day-forecasts: about 11,300-15,700 depending on the probe periods (the answer: about 9,300); about 1.2-3.2 h at
  0.37-0.74 s before leak-check rebuilds.
- Leak-check rebuilds: about 270 under the current harness for the 17 t0 series over one period (3 origins x 4 or 6
  forecasts; `engine/referee/leakcheck.py:90,95-134`), or about 370 with a 3-origin, 2-variant history-budget check
  (section 1); about 540 if series run in two yearly probes; more if that check uses more origins or variants, up to
  about 9,300 if it re-ran every forecast.
- Probes: at least 9 if the specialists run as arms; each fits the 120-minute step.
- API: none to run under route A. The protocol-revision and interpretation calls the answer budgets have no engine mode.
- Discovery budget: 0 of the 184 remaining under route A.

**Constraints that hold.** The per-arm context field is a catalogue or spec value, not a ledger context field, so B1's
pinned schema hash is untouched (`engine/ledger.py:27-39`; E5-REVIEW-3 warning, `evidence_pack_v2.md:8053-8054`). The
catalogue hash is recorded in probe results but never compared with open batches (`engine/discover.py:136`;
`engine/vault.py:106`).

**Not authorised now.** Implementing, freezing or running Experiment 5; new predictive experiments; 2026+ data;
altering B1 or Experiment 4 (`NORTH_STAR_CLARIFICATION.md:468-480`). The B1 loading fix without separate authorisation
(`:423`). Any beta experiment (`:353`). A loop change (E5-REVIEW-3). Any result of N1 stays exploratory: no batch can be
frozen before B1 opens (INFRA-VAULT).

## 12. What this review does not settle

Open questions for the owner:
1. **Whether "redesigned" describes what happened to I1.** N1 is a new question built from I1's parts; I1's H1 is
   tested nowhere, and the answer does not say whether it is deferred or dropped. "Redesigned" is one of the four
   permitted labels.
2. **Whether "Partly. It can be tested credibly as exploratory evidence" (R:13) meets the abstention condition** (`NORTH_STAR_CLARIFICATION.md:253`)
   or the mandate's "an important part" (`:234`).
3. **Whether a placebo control and a descriptive detection cost are the material move toward discovery** that owner
   point D asks for.
4. **Facts outside the pack** that bear on the answer's reasoning: whether a dated break in French consumption exists
   in 2024-05..2025-12; what t0's training corpus covers before 2022; the 2020 decree dates and times; whether ODRÉ
   holds complete 2017-2020 data; how the school-holiday calendar is published and licensed. None is verified here.
5. **Whether FLAT is reachable.** It depends on the specialist's variance and the correlation between levels, which no
   recorded run measures.
6. **Who closes the open choices in section 11**, and in what form.
7. **Whether the researcher should see this review.** Facts that bear on it, without a position:
   - the answer budgets "at most one protocol-revision call if the owner wants the researcher to close gaps the review
     finds" (R:316), which presupposes it;
   - `engine.propose_v2` refuses a second answered v2 call, so a revision call would need a new mode;
   - the v2 pack already included the first review, and the answer reuses its wording (below), so a further call with
     this review would again change the inputs together.
8. **Whether sunk gating cost counts** in the t0 route's cost.
9. **Which of the owner's four closing recommendations applies** (`NORTH_STAR_CLARIFICATION.md:494-499`). This review
   makes none.

Also not settled:
- **Whether the second answer shows learning.** Many v1-to-v2 differences trace to new pack records or to the schema:
  A_learned[10]'s first sentence is E5-ANNOT's wording; the holiday-slice figures, "a null result, not equivalence"
  and the non-comparable planted ratios come from E5-ANNOT; B1's per-year +16.0% and +21.0% existed only in the v2 pack
  (E5-REVIEW-5); route A, vintage hashes, the frozen readout, the re-gate and dropping the oracle come from
  E5-REVIEW-2, -3 and -7; the answer's structure follows the schema, which follows owner sections 4, 8 and 10. Output
  grew from 21,829 to 50,481 tokens and from 29,538 to 51,803 response characters under a doubled limit (seqs 74 and
  76). The mandate tells the researcher to review "the critique of your previous proposal"
  (`NORTH_STAR_CLARIFICATION.md:230`), so this reuse follows the mandate. These differences cannot be credited to the
  mandate text, or to learning, alone. The answer makes no such claim (R:182).
- **The orchestrator's record note.** As first committed (`153e12e`), the note in `RESEARCHER_PROPOSAL_V2.md`
  section 3 was correct that the system text, schema, pack and output limit changed together and the model and effort
  did not, but it left out the changed wall-clock limits, read timeout, repair-turn format and handling of mid-stream errors
  (`engine/propose_v2.py:20-22,50-52` against `git show b13e596:engine/propose.py:40-42`) and call-to-call variation. The note was corrected in the commit that
  adds this review. Neither call was cut off: both have stop reason `end_turn`, attempt 1, retry 0.

## Method

**Lenses.** Eight review lenses, read-only:
- facts-context: the summary, section_4, A_learned and B_unexplained;
- facts-N1: N1, D and E;
- facts-N2-N3: N2, N3 and D;
- north-star-outcomes-scope: owner sections 4, 8-10 and 13-14, outcomes and scope;
- fm-vs-information-comparator: criterion 3 and comparator fairness;
- scarcity-regime-pit: scarcity, regime and point-in-time status;
- cost-statistics: cost measurability and the statistical design;
- disposition-and-constraints: the I1 disposition and the owner's hard constraints.

**Skeptic verification.** Every lens item went to an independent skeptic told to refute it. Each item came back
confirmed, corrected or refuted; the corrected versions are the ones used here, and refuted items are not used.
- **Kept:** 162 items, 104 confirmed and 58 corrected. By kind: 58 holds, 46 gaps, 37 risks, 21 errors. Of the 104
  flags, 24 are material and 80 minor.
- **Refuted:** 3 of 165 items (facts-context-09, north-star-outcomes-scope-18, scarcity-regime-pit-07); they are not
  used.
- **Merging.** Several lenses reached the same finding (for example, the pair minimum at L = 7 appears in seven items),
  so the number of distinct findings above is lower than the item count.

**Computations.** All read-only. Nothing was forecast or fetched, and no data from 2026 on was read.
- Calendar-only enumeration of the specialist's source, pair and window rules, with the engine's own covariate time
  and coverage helpers where stated.
- Ledger reads of the engine ledger to seq 76: seq 51 and seq 60 `per_day`; `data.read` of every probe_result; gate
  and note entries 17-36; research_call metadata and usage, seqs 49-76. Model and request fields
  were compared by equality only and never printed.
- Text searches of the 127 pack records; schema validation with `engine.propose_v2.validate_proposal_v2`.
- The installed t0 package's scaler run offline on synthetic inputs (no model forecast).
- Power and placebo figures: normal approximations on analogue bootstrap SDs, not measurements.
- Scratch scripts (not committed), under the review's scratch area: `fm/` (`pairs.py`, `pairs_hh.py`,
  `sd_invariance.py`, `age8.py`, `sametype.py`), `skf/` (`firstday2.py`, `nosource.py`, `pairs2.py`, `counts.py`),
  `sk2/` (`omap_check.py`, `pairs_check.py`), `sk3/pairs_indep.py`, `scarcity_pit/` (`sd_specialist_calendar.py`,
  `slope_leverage.py`, `t0_checks.py`, `placebo_coverage.py`, `lag_dst.py`, `ao_stratum.py`), `skeptic_cost/`
  (`check1.py`, `sdt_count.py`), `skeptic_fm/` (`span.py`, `lastday.py`), `skeptic_spit/ctrl_origins.py`,
  `skeptic/n2check.py`, `disp_checks.py`.

**Where each section's findings come from** (item ids, for audit):

| Section | Items |
|---|---|
| 1 | facts-context-01 to 08, 10 to 19; facts-N1-02, 04, 13, 17 to 20, 24, 26; facts-N2-N3-00, 01, 06, 07, 09; disposition-01 to 05, 08, 09; north-star-13; scarcity-21 |
| 2 | north-star-01 to 03, 10, 13, 15, 16; disposition-13, 14, 21, 22; scarcity-14 |
| 3 | fm-01, 02, 04, 05, 11, 13, 14; facts-N1-22; north-star-05, 06, 09; disposition-07, 15 |
| 4 | scarcity-01 to 03, 05, 10 to 14, 18, 20; facts-context-08, 10; facts-N2-N3-05 to 07; north-star-19; cost-15 |
| 5 | fm-03, 06 to 09, 12; scarcity-23, 25 |
| 6 | cost-01 to 07, 19; facts-context-07; facts-N2-N3-08, 13, 14 |
| 7 | cost-10 to 14, 16 to 18, 20; north-star-04, 07, 08, 14, 17, 20; facts-N1-21, 23; disposition-06; facts-N2-N3-12 |
| 8 | north-star-11, 12; facts-N1-08, 11, 12, 16; cost-08, 09 |
| 9 | facts-N1-01, 03, 09; scarcity-04, 06, 08, 09, 15, 22 to 25; facts-N2-N3-02 to 04, 10, 11; fm-10; disposition-10, 16, 19 |
| 10 | scarcity-16, 17, 19; facts-N2-N3-04 to 06; disposition-11, 18 |
| 11 | facts-N1-05 to 08, 12 to 17; disposition-12, 20; scarcity-10, 15; north-star-12; cost-01, 02, 05 |
| 12 | disposition-01, 22 to 25; cost-16, 17; facts-context-01; scarcity-14 |

**Evidence references.** File and line references are to commit `153e12e`. "Seq N" is the engine ledger entry N
(hash-chained, head seq 76; the file holds 77 entries, seqs 0-76). The researcher's answer is quoted from
[`proposal_v2_rendered.md`](proposal_v2_rendered.md) and [`researcher_output_v2.json`](researcher_output_v2.json),
which equal the response recorded at seq 76.
