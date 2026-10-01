# Experiment 5: feasibility review of the researcher's proposal

*An engineering review by the orchestrator. It checks whether the researcher's chosen investigation (I1, in
[`RESEARCHER_PROPOSAL.md`](RESEARCHER_PROPOSAL.md)) can run, what it would cost, what its result could and could not
show, and what must be decided first. It flags; it does not change the hypothesis, choose another investigation,
fill gaps in the protocol or freeze anything. Nothing here has been run.*

## Summary

**The question I1 asks.** On French consumption, does feeding a temperature forecast through t0's covariate channel
(the B1 arm) beat the simplest external use of the same forecast: a frozen linear temperature correction of the same
t0 + holiday forecast? An ERA5 "oracle" arm is a diagnostic. Everything is exploratory: it reuses the 2024-05..2025-12
days that were used to select B1.

**Can the existing system run it?** Not today, for three reasons. Each has a bounded fix.

1. **No engine probe can load t0.** The engine asks for t0-alpha by a revision id that vanished upstream on
   2026-09-29. Every engine mode that forecasts is affected: probe, gate, reproduce, vault and vault rehearsal.
2. **The engine cannot express I1.** It has no post-hoc correction arm, no ERA5 temperature source, and no way to
   run an oracle arm inside a discovery probe. An oracle arm today stops the probe with an error, or marks the whole
   probe invalid.
3. **The protocol has gaps.** They have to be closed before it can be frozen. Some are scientific choices, so this
   review does not close them (section 6).

**Effort to make it runnable.** None of it is infeasible:
- about 5–8 engineer-days of engine work (changes 1–6 in section 3);
- at least 3 probe dispatches;
- roughly 1–3 hours of Actions runner time in total, including job overhead;
- no further API call, if the owner dispatches the probes.

**Data.** Every input to the decision comparisons is already wired, and point-in-time safe under the repository's
rules:
- consumption;
- the holiday calendar;
- the archived lead-3 temperature, whose known-answer gate (ledger seq 36) still matches the code.

Only the oracle needs a new source: ERA5 temperature, through a new door. For it the repository records only
Open-Meteo's terms: CC BY 4.0 data on a non-commercial free API (`README.md:975`). The upstream Copernicus/ERA5
licence and an attribution line are not recorded, and a human must check them (section 10, item 6).

**What the result can show.** Measured on the closest recorded analogue, about 600 days resolve differences of
roughly 4–7 points of skill:
- **Larger differences:** a clear "channel better" or "external correction better" is likely.
- **Smaller ones:** mostly inconclusive.
- **The proposal's "equivalence" outcome** (95% interval within ±5%) is realistic only if the two routes differ by
  about 2 points or less and the pair's variance is as low as the best analogue's. In that case the chance is about
  84% at a true difference of 0. Otherwise it is unlikely (about 13–26%), or impossible at the variance of the B1-vs-C1
  pair.

**What it is worth.** Its scientific value is real but capped:
- **What it adds:** the first same-information comparison on consumption, and the first oracle on consumption that
  uses real temperature (ERA5).
- **How far it reaches:** it can change how B1's verdict is read and what is probed next. It cannot establish a
  finding.
- **Where the proposal overreaches:** several of its own readings claim more than the design can show (section 7).

It has no direct economic use, and none is claimed.

**Approvals needed.** Section 10 lists the decisions only the owner can take. One of them is due whatever happens to
I1: B1's own vault run cannot load t0 either, and needs its own fix before 2027-04-01.

## 1. How this review was made

**The workflow.** All of it was read-only, and nothing was fetched or forecast:
- **Fact-check:** 4 agents checked 246 factual or numeric statements in the proposal against the evidence pack and
  its sources.
- **Feasibility:** 5 agents researched data, the engine delta, compute and power, scientific limits, and what the
  step shows about the researcher.
- **Skeptics:** every finding then went to an independent skeptic, told to refute it and to default to "refuted".
  - Fact-check: 30 findings; 20 survived, 10 were refuted.
  - Feasibility: 102 findings; 101 survived, most with corrections.
  - The corrected versions are the ones used here.
- **Size:** 141 agents in all.

**Computations.** All of them are read-only arithmetic on recorded data. Nothing was forecast.
- **Committed:** [`feasibility_power.py`](feasibility_power.py), with output
  [`feasibility_power.json`](feasibility_power.json). It produces every figure in section 5 and the day counts:
  - It rebuilds each day's error sum from the per-day MAE at seq 51 and that Paris day's half-hours.
  - It runs the engine's own bootstrap. Its 7-day check reproduces seq 51's recorded skill, interval and p to the 6
    decimals recorded.
  - Its power, equivalence and both-years probabilities are normal approximations on the bootstrap SDs.
- **Not committed:** the review agents' other scratch checks, such as citation spot-checks and coverage reads of
  recorded series. Section 4's runtime figures are arithmetic on the recorded timings and day counts it states.

**Evidence references.** File and line references are to commit `39f7d1a`. "Seq N" is the engine ledger entry N
(branch `engine-ledger`, verified chain, head seq 74).

## 2. Element by element

Status key:
- **ready:** can be used as it stands;
- **needs change:** bounded engineering, or a wording fix in the protocol;
- **blocked:** cannot run until a prerequisite is met;
- **gap:** an open protocol choice that someone other than the orchestrator must make (section 6).

| Protocol element (section E) | Status | What it needs | Evidence |
|---|---|---|---|
| Target: national consumption, 30 min, MAE | ready | Nothing. Licence Ouverte permits reuse with attribution | `engine/catalogue.py:20-24`; seq 51 read 2021-09-23..2025-12-31; `README.md:685-689` |
| Data vintage of the target | needs change | The engine records no vintage and no hash of the target. Every 2025 row was "consolidated" when C1 ran, and RTE makes them definitive in the second half of the following year. A rerun may therefore read different 2025 values from seq 51. Record nature counts and a target hash in every I1 result, and require them equal across I1's probes | `solarbench/odre.py:102-117` drops `nature`; `engine.yml:73-77` (no caches); `ledger/confirmations.jsonl` |
| Decision time 12:00 Paris D-1; horizon 73 steps | ready | Nothing | seq 51 leak-check origins (10:00 UTC in summer, 11:00 UTC in winter) |
| Information (a): lead-3 temperature as a t0 covariate (the B1 arm) | ready | Nothing, as long as the gate fingerprint is unchanged. The archive has no gaps from 2024-02-06 00:00 to 2025-12-30 23:00 UTC. Gate seq 36 (ka/2, pass) has fingerprint `b2d50d2f…`, which equals the fingerprint at HEAD | `engine/covs.py:24-39`; `engine/gates.py:38-64` |
| Information (b): the linear correction, `[T, HDD15, CDD22, 1]`, per-hour OLS on C1's trailing 56 days up to D-2 | needs change + gap | A new method type (section 3). The estimator is undefined in most windows (section 6, item 4) | `engine/arms.py:136-155` builds only t0 arms and the fixed comparators |
| Information (c): the ERA5 oracle | needs change | A new ERA5 door in `engine/data.py` and a catalogue entry. A declared-oracle exemption in `discover.py` and the leak harness. A guard so it can never be ranked or claimed. One coverage-only read. ERA5 temperature has never been fetched here; `solarbench.weather.fetch_era5` refuses dates from 2025 | `solarbench/weather.py:161-166`; `tests/test_covariates.py:205`; `engine/discover.py:108`; `solarbench/backtest.py:211-222` |
| t0 configuration (t0-alpha, zero-shot, 90-day context, loaded by content) | blocked | The engine loads t0 by the vanished revision `9b02c5f4…` at every entry point. Porting the content-verified loader (`solarbench/t0_pinned.py`) to the non-fingerprinted call sites would keep the gate fingerprint. This is an owner decision | `engine/catalogue.py:16`; `engine/discover.py:93`; `engine/__main__.py:243,284,378,433`; `solarbench/forecasters.py:439-442` |
| Comparisons: primary (B1 arm vs C1 + correction), competence (C1 + correction vs C1), oracle diagnostic | needs change | Expressible once the correction and oracle arms exist. All three fit one probe at the current limits (3 arms, 3 comparisons) | `engine/catalogue.py:73`; `engine/spec.py:55-56,101-114` |
| Report-only: correction applied to B1, 28/112-day windows, blend_50, RTE, pinball | needs change | Extra arms take at least 2 more probes. blend_50 and RTE daily errors are already on the ledger and can be paired offline. The protocol keeps a pinball loss of the t0 arms. That needs quantiles, which the engine's t0 arms do not keep, so it needs change 6. Dropping it would change the protocol and needs the researcher's or the owner's agreement | seqs 27/28/39/41 (best_simple), seq 60 (rte_j1); `engine/arms.py:121-124` |
| Point-in-time rules | ready for (a); needs change for (b) | (a) is asserted twice: by the backtest contract and by the referee's leak check, with a 25 h margin at every checked origin (seq 51). (b) has three needs. Its D-2 cut-off is stricter than the contract can enforce, so it needs its own rule and a unit test. It must declare its temperature input, or the leak harness silently skips its weather control. It must report the issue times of its training regressors | `engine/referee/leakcheck.py:117-135`; `engine/discover.py:37-39`; `solarbench/probes.py:253,347-351` |
| Discovery sample 2024-05-06..2025-12-31 | needs change + gap | In practice the B1 arm scores 602 days, 2024-05-05..2025-12-29 (601 inside the stated span). Missing: the two autumn clock-change days (never built for any arm), 2025-12-30 (weather arms) and 2025-12-31 (all arms). The proposal scores "on the intersection where every arm has a forecast", and its arms include the oracle. Read literally, "every arm" also covers the report-only arms. The correction applied to B1 cannot start before about 2024-07-01, which would cut the sample to about 545 days (183 in 2024). The 112-day window cannot fill before 2024-05-30. The oracle's coverage is unknown until ERA5 is read. Which arms define the day set is an open choice (section 6, item 5) | seq 51 `per_day`; `feasibility_power.json` `day_counts`; `engine/zones.py:69-86` |
| Validation (14-day blocks, Holm over 2, year and season direction) | ready offline | The protocol fixes these statistics. The engine's discovery statistics use 7-day blocks with no Holm, and its ledger entries will show those. Every protocol statistic can be computed from the per-day errors each probe records: `feasibility_power.py` reproduces seq 51's figures to the 6 decimals recorded. A readout script must be frozen before any run. It must compute the protocol's 14-day, Holm-adjusted figures and record that the ledger's 7-day ones do not decide | `engine/catalogue.py:76`; `solarbench/metrics.py:20`; `engine/referee/stats.py:111-119` |
| Falsification criteria and F map | gap | See section 6 | — |
| Leakage and snooping | ready (stated) | The proposal states the snooping risk and freezes the correction in advance. No reading rule discounts B1's in-sample selection (section 7) | seq 51, 54 (selection), seq 56 (freeze) |
| Compute budget | ready, with corrections | Section 4 | — |

## 3. What would have to be built, and by which route

**Routes.**
- **A. The engine, with probes dispatched by the owner.** This is the realistic route:
  - the specs are written by the orchestrator from the frozen protocol;
  - the readout script is frozen before any run;
  - the results land on the hash-chained ledger as ordinary `probe_result` entries, with live leak checks;
  - it is not charged to the discovery budget.

  It departs from the researcher's plan in one respect: the proposal assumed researcher-submitted probes ("3 of the
  184 remaining researcher evaluations").
- **B. The engine, through the researcher loop.** The loop researcher cannot name a correction or oracle arm:
  - its answer schema allows only names and catalogue covariates (`engine/researcher.py:99-100`);
  - its digest omits propose-mode calls, so it has never seen this proposal;
  - its rules push it towards single-arm freezable claims (`engine/researcher.py:63-65`).

  Changing it goes beyond the scope the owner approved for this step (the brief records that the loop stays
  unchanged).
- **C. A standalone runner like Experiment 4's.** It is not needed:
  - the target, the gated temperature, the leak harness and the per-day output already exist in the engine;
  - a runner would move more of the design into orchestrator code, and its results off the ledger.

**The minimum change set for route A.** This set leaves the gate fingerprint, B1 and the ledger schema untouched:

| # | Change | Where | Effort |
|---|---|---|---|
| 1 | Load t0 through `solarbench/t0_pinned.py` at the call sites and pass the model in. Catalogue `T0` stays unchanged, so the gate fingerprint stays `b2d50d2f…`. Record the retrieval in each probe result | `engine/discover.py:93`, `engine/__main__.py` | about 0.5 day |
| 2 | The correction arm as a new module. It forecasts C1 once over a continuous span (its days plus the 56 training days) and fits per origin. It needs the D-2 mask, a declared temperature provider, issue-time propagation and a 56-day eligibility rule. It also needs a catalogue/spec field, normalised and hashed, so that corrected and plain arms never share a spec hash | new module; `engine/spec.py`; `engine/catalogue.py` | about 2–3 days |
| 3 | The ERA5 door, the catalogue entry, the oracle two-key exemption in `discover.py` and the leak harness, and a `LEADS` entry. Without that entry, the leak harness raises `KeyError` for every arm | `engine/data.py`, `engine/discover.py`, `engine/referee/leakcheck.py` | about 1–2 days |
| 4 | Guards so that a corrected or oracle arm can never be cited as evidence for, or frozen as, a plain arm | `engine/claims.py:63-82,134-137`; `engine/spec.py:99,134-136` | about 0.5 day |
| 5 | A frozen readout script. It computes the protocol's statistics (14-day blocks, Holm over 2, year and season direction, concentration) on the day set fixed under section 6, item 5. It records that the ledger's 7-day intervals do not decide | new file | about 0.5–1 day |
| 6 | The report-only pinball loss that the protocol keeps (quantiles kept outside `engine/arms.py`). Dropping it would change the protocol | new module | about 1 day |

**Constraints that protect B1:**
- **No new ledger kind or context field.** Either would change the schema hash B1 pinned (`ce2ed6e8…`). While B1 is
  open, the record job would then refuse every non-vault record.
- **The vault job and `record.py`'s vault rules stay as they are.**
- **Probes can run while B1 is open.** Seqs 59–69 did so after B1's freeze at seq 56.

**What happens if fingerprinted files change.** If the build edits `engine/arms.py`, `engine/covs.py`,
`solarbench/forecasters.py` or another fingerprinted file:
- every weather gate lapses, and B1-arm probes are refused until a full known-answer gate passes again;
- that gate run is a real t0 run, and it can fail: the decoy ratio moved from 1.0013 to 1.0132 at the last
  fingerprint change, still within its limit.

**B1's own loading problem is separate.** It is not solved by any of the above:
- The vault scores B1 only at its freeze commit `710b2b37`. `engine/__main__.py:342-359` refuses any other checkout.
- That commit loads t0 by the vanished revision before anything else runs.
- So an engine-code fix on the branch, such as change 1, cannot reach B1, because the vault runs the frozen code.
  B1 needs its own owner-approved change before 2027-04-01. One example is a step in the vault job of the dispatched
  branch's `engine.yml` that stages hash-verified weights under the frozen revision for the frozen code.
- **One fix or two.** The proposal's "pending anyway for B1" assumes the engine's loading fix also serves B1. An
  engine-code fix does not.
  - **A workflow-level step could serve both.** The frozen code and the probe path at HEAD request t0 the same way,
    `from_pretrained(..., revision=9b02c5f4…)`. The same staging step added to the referee job would also unblock
    I1's probes.
  - **Change 1 would then still be needed,** but only to record the retrieval in each probe result.
  - **Which design to use is an owner decision** (section 10, items 1 and 4).

## 4. Runtime, API cost and discovery budget

**t0 compute** (an analogue estimate from recorded engine timings, not a measurement of I1):
- The recorded rate is 0.37–0.74 s per t0 day-forecast, all-in. Seq 51 made 3,262 day-forecasts in 20.4 minutes.
- **The decision probe:**
  - The three arms need about 1,900–2,700 t0 day-forecasts, depending on whether C1 runs over the whole engine
    period.
  - The correction arm's leak check rebuilds it from the bundle at 3 origins, with 6 variants of 57 days each. That
    adds up to about 1,000 more.
  - **Time:** these 2,900–3,700 day-forecasts take about 18–46 minutes of the engine step at the recorded rates. Seq
    51 is in line with this: 3,262 day-forecasts in 20.4 minutes.
  - **Not included:** the ERA5 read has no recorded timing and comes on top.
  - **Limits:** the step limit is 120 minutes. Job overhead (installing dependencies, the test suite, the ledger
    fetch) counts against the 150-minute job limit instead (`engine.yml:160,218`).
- **A condition on the correction arm:** it must forecast its base once and reuse it. Rebuilding the base for every
  window would need about 34,000 forecasts, which is far over the limit.
- **Three probes:** about 0.9–2.3 hours of probe steps, plus each dispatch's job overhead.
  - The two extra probes carry the report-only arms. Their leak-check rebuilds can be heavier: the 112-day window
    alone needs about 18 × 113 ≈ 2,000 rebuild forecasts.
  - So roughly 1–3 hours of runner time in all.
- **The proposal's own basis does not fit.** It used "nine arms × 731 days in about 39 minutes", from Experiment 4.
  - That run had only 4 t0 arms, spent about 19 of its 39 minutes downloading prices, and used a shorter context.
  - At the engine's recorded rates, the workload the proposal counted (3–4 t0 arms × about 660 days) takes about
    12–33 minutes. So its "under 1 hour" holds for that workload.
  - It does not hold for I1 as this review sizes it: at least three probes, about 1–3 hours in all.

**API.**
- **The decision itself:** 132,760 tokens counted against the daily cap (seq 74):
  - input: 104,312;
  - output: 21,829;
  - cache writes: 6,619.

  That is 6.6% of the default 2,000,000-token daily cap, and about 7–9 times a loop call. No price is recorded in the
  repository, so none is quoted.
- **Running I1:** route A makes no API call.

**Discovery budget.**
- **What remains:** 184 of 200 evaluations, which is correct (16 spent at seqs 51–69).
- **What "3" covers:** only the decision-and-diagnostic probe.
- **The full protocol:** if the researcher submitted it, it would cost about 5–8 or more evaluations. If the owner
  dispatches it (route A), it costs 0.

## 5. Statistical power (analogue only)

The proposed primary comparison has never been run, so its precision is unknown. The closest recorded analogue is:
- **what it compares:** four pairs of t0 arms scored on the same 602 days. One is the B1 arm against C1 (t0 +
  holiday, with no temperature input), the competence-check analogue. The other three are pairs of temperature-aware
  arms that differ only in how temperature enters;
- **where it comes from:** seq 51;
- **how it is computed:** the engine's own bootstrap with 14-day blocks, as the protocol specifies
  (`feasibility_power.json`).

All of these days were used to select B1, so every figure is exploratory.

| Pair (seq 51) | Pooled skill [95% CI] | Half-width | ≈ MDE at 80% power, one-sided 0.025 |
|---|---|---|---|
| B1 arm vs C1 (the competence-check analogue) | +19.3% [+14.2, +24.4] | 5.1 pts | 7.2 pts |
| raw vs hdd15 temperature | +7.1% [+3.4, +11.9] | 4.2 pts | 6.1 pts |
| raw vs hdd15+cdd22 | +8.6% [+5.8, +11.5] | 2.8 pts | 4.1 pts |
| hdd15 vs hdd15+cdd22 (near-null pair) | +1.6% [−3.7, +5.5] | 4.6 pts | 6.6 pts |

**What this implies for I1's reading rules.** These are the orchestrator's arithmetic, not a redesign.
- **Decisive results.** "Supported" and "falsified" are likely only when the two routes differ by about 4–7 points
  or more. At 1–2 points the overall test is significant in only about 6–27% of cases at one-sided 0.025. At 0.05
  (Holm's second step) it is about 10–39%.
- **Equivalence.** The "equivalence" outcome (95% CI within ±5%) depends on the pair's variance:
  - **At the variance of the three temperature-vs-temperature pairs,** the point estimate must lie within about
    ±0.4–2.1 points.
  - **At the variance of the B1-vs-C1 pair** (half-width 5.1 points), no point estimate can meet it.
  - **The recorded near-null pair** already fails it at 602 days.
  - **The chance of declaring it at a true difference of exactly 0:**
    - about 84% at the lowest-variance pair (raw vs hdd15+cdd22), and 52% if the true difference is 2 points;
    - about 26% and 13% at the other two temperature pairs;
    - 0% at the B1-vs-C1 pair's variance.
- **The year rule.** "Both years point the same way":
  - **How likely both year estimates are positive:** about 49–70% at a true difference of 2 points, and 80–97% at 5
    points, if the years are treated as independent. Requiring a significant overall result first already selects
    results that are mostly positive in both years.
  - **What it partly tests:** the 2024 part is only 240 days, with no January–April and only 61 winter days, so a
    year split partly tests the season mix.
- **The season rule.** Season results can diverge from the overall one: the raw-vs-hdd15 pair is +7.1% overall, but
  +0.3% in winter and +15.3% in summer.
- **A by-product, on selection days and exploratory.** The per-year split the researcher listed as never checked
  can be computed from the recorded per-day errors. The B1 arm vs C1 gives:
  - 2024: +16.0% [+7.0, +25.7];
  - 2025: +21.0% [+15.1, +26.6].

  The pack had excluded per-day series for size, so the researcher could not compute this.
- **Probabilities:** every probability in this section is a normal approximation on the recorded bootstrap SDs
  (`feasibility_power.json`, `derived`). None is a measurement.

## 6. Protocol gaps that must be closed before any freeze

Each gap is a choice. The orchestrator does not make them (section 10 asks who should).

1. **Settle the support rule.** It is stated three ways:
   - E.falsification_criteria: skill > 0, Holm p < 0.05, both years.
   - E.validation_method: adds the winter and summer direction.
   - F.supports: a 95% CI lower bound above 0 plus non-negative season points.

   These give different verdicts when the primary's raw p lies in [0.025, 0.05), or when one season is negative.
2. **Close the outcome map.** It has holes and overlaps:
   - Two results map to no F outcome:
     - equivalence: a CI inside ±5% that straddles 0, with both years agreeing, unless a "t0 failed" condition also
       holds;
     - a significant overall result with a negative season.
   - "against" and "underpowered" both apply when the CI is wholly below 0 but one year is positive. Their knowledge
     updates contradict each other.
   - There is no precedence rule.
3. **Set the oracle reading:**
   - The 5–10% band is unassigned. The solar anchor (+6.4% [+2.7, +10.6]) falls in it.
   - It is not stated whether the point estimate or the CI is compared.
   - The 10% and 5% cut-offs are new and unsupported by any cited record.
4. **Define the correction estimator.** `[T, HDD15, CDD22, 1]` is rank-deficient in most hour-by-window cases:
   - CDD22 is all zero outside summer windows.
   - In a window that stays below 15 °C, HDD15 = 15 − T exactly, so it is collinear with T and the intercept.

   The resolution rule changes the forecast on season-transition days, which lie inside the sample. Also undefined:
   - whether "per hour" means 24 local hours, 24 hours pooling both slots, or 48 half-hour slots;
   - how 46-slot clock-change days count among the "56 fully observed days".
5. **Define the scoring day set.** The researcher set it as "scored on the intersection where every arm has a
   forecast", and the oracle is among its arms. Which arms count is not defined, and the answer changes the sample:
   - **Every arm, including the report-only "correction applied to B1":**
     - about 545 days, 183 of them in 2024, because that arm cannot start before about 2024-07-01;
     - the 112-day window alone would start on 2024-05-30;
     - ERA5's coverage is not yet known and could remove more days.
   - **The decision arms only (C1, B1, C1 + correction):** 602 days, 2024-05-05..2025-12-29. The other comparisons
     would then be scored on their own day sets, or on this one.

   The trade-off is power, especially per year, against having every comparison on the same days.

   Whichever set is chosen must also fix two details:
   - the dates: the stated span starts on 2024-05-06, but the B1 arm starts on 2024-05-05; scoring ends on
     2025-12-29; the autumn clock-change days are absent;
   - April and October, which are in neither season slice: 90 of the 602 days.
6. **Decide whether the competence check needs a minimum size.** As written, it needs only a 95% CI above 0, so it
   rules out a useless correction but not a weak one.
   - **A small correction could pass.** A correction recovering about 3% would pass if its CI clears 0. Whether it
     does depends on the correction's per-day variance, which is unknown:
     - at the variance of the section 5 analogue (B1 arm vs C1), a true 3-point gain would usually fail;
     - a smooth, consistent gain would pass.
   - **What a pass would mean.** Such a correction would still lose to the B1 arm by about 17%
     (1 − 1198.8 / (0.97 × 1485.2)), and that would read as "supports".

   This is a scientific choice.

The protocol already settles two related points, so they are implementation items rather than gaps: section 3,
changes 5 and 6.
- **The decision statistics:** 14-day blocks with Holm. The engine's ledger will also show its own 7-day intervals.
- **The report-only pinball loss:** the protocol keeps it.

Using the 7-day figures, or dropping the pinball loss, would change the protocol.

## 7. Scientific limits

These are flags. None of them changes the hypothesis.

**What the design cannot separate:**
- **Explanations 1 and 5.** Explanation 1 is that the channel is efficient. Explanation 5 is that a 56-day linear
  correction is too weak or slow to compete. They predict the same result: the B1 arm wins and the competence check
  passes. The only thing that could separate them, window sensitivity, is report-only.
- **Selection.** The selection-artefact explanation (4) cannot be tested on these days, which are the selection
  sample. Only B1's forward window can address it.
- **The oracle.** It does not separate staleness from how t0 uses the input.
  - Its gain mixes how wrong the lead-3 forecast is with how strongly t0 responds.
  - The pack has no measurement of lead-3 error against ERA5.
  - Swapping in ERA5 also changes the 90-day context t0 reads, not only day D.
  - It reads ERA5 at the same 12 points, so it cannot implicate or clear the crude spatial weighting.
- **The solar contrast.** I1 is not the consumption counterpart of the solar comparison:
  - on solar the winning comparator used no t0;
  - here the comparator is t0 plus a correction of its residuals;
  - so a channel win cannot be attributed to the target ("efficiency depends on the target");
  - a channel loss does show, across both targets, that external use beat the channel.

**Fairness:**
- Only the channel arm carries selection on these days. Its encoding was picked from three on them, and no reading
  rule discounts this. The pick was not a near-tie: raw beat hdd15 by +7.1% [+3.4, +11.9]. So the winner's-curse part
  is probably modest, but not zero.
- The correction is frozen untuned, which is right.

**Where the proposal's knowledge updates overreach:**
- **"against".** It says the value "is not a t0 capability". The design could show only that the channel is less
  efficient than one linear correction. The B1 arm already beats C1 by +19.3%. The update also has no "Exploratory:"
  prefix, and it generalises from t0-alpha's known-future route to "t0".
- **"supports".** It says B1's verdict becomes "evidence about t0's capability". That drops the qualifier "against one
  frozen linear form, on in-sample days".
- **"t0 failed to exploit".** It rests on undefined terms:
  - a report-only comparison with no test;
  - an "ideal" planted ratio the pack does not define;
  - it also ignores a documented alternative mechanism: covariate noise made t0 worse on consumption in the ka/1 gate
    (+5.2%).

**What the result can reach.**
- **Exploratory for good:**
  - 2025 is consumed;
  - these days selected B1;
  - no batch can be frozen before B1 opens after 2027-04-01;
  - the vault has no comparator for a correction (`engine/claims.py:20,63-66`).
- **What it can do:** change how B1's verdict is read, and what is probed next.
- **What it cannot do:** establish a finding.
- **When it changes nothing:** in its "underpowered" and "data quality" outcomes it changes nothing about channel
  efficiency, which the proposal itself concedes.

## 8. Scientific information value and economic usefulness, kept apart

**Scientific information value.**
- **What I1 adds:**
  - It would add the first same-information comparator on consumption. Every consumption covariate gain so far has
    been measured against t0 without that covariate, or against RTE as a reference.
  - It would add the first oracle diagnostic on consumption that uses real temperature (ERA5 in place of the lead-3
    forecast). The only oracle arms run on consumption so far are the known-answer gates' planted, decoy and shifted
    arms. Those check the pipeline; they do not value better temperature.
  - It tests how efficiently the project's core primitive (incremental information through t0's covariate channel)
    uses temperature, against the simplest external route using the same forecast on the same t0 + holiday base.
  - It does not test whether the primitive adds value at all. That is the B1-arm-vs-C1 comparison, which is not
    among I1's decision comparisons and is already +19.3% in-sample.
- **Its limits:** sections 5 and 7.

**Economic usefulness.** None directly, and none is claimed:
- I1 measures consumption-forecast accuracy only: MAE skill and its breakdowns, plus a report-only pinball loss. It
  measures no price, trading or monetary quantity.
- **Licence:** the weather source is Open-Meteo's free API, which the repository records as non-commercial
  (`README.md:975`). Any economic use of either temperature arm would need a licensed feed, with its issue times
  proven again.
- **Freshness:** the lead-3 forecast is about 3 days old, staler than an operator would use.
- **The researcher's two economic statements are predictions, not evidence:**
  - "neither result beats RTE": the B1 arm is level with RTE's stored forecast all year (+7.6% [−2.7, +16.0]) and
    +30.6% in summer;
  - "a cheaper hybrid": there is no cost evidence, since both routes run t0.
- **For the owner's long-term market application:** no market claim follows from any I1 outcome. The only measured
  price-side weather evidence is still Experiment 4's P4: +2.8% [+1.1, +4.4], concentrated in 20 of 572 days.

## 9. What this step shows about the researcher, and what would show compounding learning

**This decision against the mandate.**
- **Coverage:** the answer covers all four items:
  - how I1 follows from the evidence;
  - five competing explanations;
  - support and falsification criteria;
  - a next step for each outcome.
- **Citations:** all 57 cited records exist. A spot-check of 12 numeric citations found every number matching.
- **Evidence grades:** respected overall. Only C1 is called confirmed, nothing is claimed before B1 opens, and
  t0-beta is handled as the rules ask. There is one exception. The "against" knowledge update states its would-be
  exploratory result as established. It lacks the "Exploratory:" prefix the "supports" entry carries, and its solar
  half rests on a legacy result that was never independently verified (section 7).
- **Its slips:** none is a figure copied wrongly from the pack. They lie in how it characterises evidence,
  feasibility and its own protocol. The 20 surviving fact-check flags are in `RESEARCHER_PROPOSAL.md` section 3; the
  knowledge-update overreach is in section 7 above. The largest:
  - an overstated reading of the planted-signal gates;
  - an incomplete feasibility account, with I1's prerequisites missing and compute counted for one probe only;
  - the support rule stated three ways;
  - the overreaching knowledge updates.
- **Grading:** none was fixed in advance, so "defensible" is a reviewer's judgement, not a score.

**Instructions versus learning.**
- **What the loop already had:** the fact that motivates I1 (on solar, a one-line weather ratio without t0 beat
  t0 + weather by 23.8%) was in all eight loop researcher prompts (seqs 49–70). The loop never acted on it. The same
  model and effort setting answered all of those calls and this one.
- **What changed:** the instructions, the interface (the loop could not even express a non-catalogue comparator) and
  the evidence (a 232 KB pack with the full covariate-slice narrative) all changed at once. One call cannot say which
  of them produced the better question.
- **Anchoring:**
  - **Against it:** I1's central element appears in none of the loop's notes. That element is a same-information
    comparator: a linear correction that uses the same temperature forecast outside t0's channel. The loop compared
    its arms only with catalogue comparators, including RTE's forecast as a reference.
  - **For it:** I1 continues the loop's topic, arm and sample.
  - It can be neither ruled out nor confirmed.
- **The pack:** what the researcher can reuse is set by how the pack was curated (the per-day series were left out,
  section 5). So for now any compounding belongs to the builder and the researcher together.

**Compounding learning is not shown by this step and must not be claimed.** Designs that would test it are below.
None has been run, and section 10 leaves the choice of any of them to the owner.
- **Answer-shopping:** only pack ablation (its head-72 cells) and replicate variance call the researcher again on a
  decision already answered. Those collide with the approved "no answer-shopping" rule. Retrodiction's extra calls
  also go beyond the approved one research decision.
- **Engineering:** every design that makes new calls needs it. The pack builder is pinned to ledger head 72, and
  propose mode refuses a pack built at any other head or from changed source files.
- **No new calls:** holding the request fixed is a protocol rule, and tracking cost is bookkeeping.

| Design | What it would show | What it would not show | Rough cost |
|---|---|---|---|
| **Pack ablation at several decision points.** Heads 9, 48 and 72. Full pack, rules only, and (at head 72) without the loop notes. At least 3 replicates. Blind graders, rubric fixed in advance | Whether accumulated evidence improves decisions with the instructions held fixed. At head 72, whether the loop notes steer the choice | That better-graded proposals lead to better results; any trend over time | 7 cells × 3 = 21 calls, about 2M tokens; packs must be rebuilt from git history to avoid leaking later knowledge |
| **Replicate variance.** The identical seq-74 request, about 5 times | The noise floor any with/without-pack difference must exceed; whether I1 is a stable choice | Learning. Its outputs must never re-select the investigation | about 0.66M tokens; a separate harness |
| **Hold the whole request fixed** (system text, schema, wrapper, model, effort) across conditions and cycles | Separates the effect of instructions from the effect of evidence | Learning by itself | a protocol rule |
| **Calibration of the F map.** The researcher states probabilities for its outcomes and an interval for the primary skill before each run; these are scored over at least 5 cycles | Whether its expectations sharpen and stay calibrated as evidence accumulates | Decision value; the owner's choice of what to run biases the sample | a schema change (about 0.5 day plus validation). The F outcomes now overlap and leave gaps (section 6, item 2): a multi-class score needs a partitioned set, otherwise each outcome is scored as its own yes/no event. The choice is the researcher's or the owner's |
| **Builds-on tracking.** The next pack includes I1's results and this answer, with stable ids | Whether the next proposal cites and follows its own pre-stated next steps, or explains why not | That doing so improved outcomes; it raises anchoring | a builder change; one normal call |
| **Cost per decision and per resolved question** | Whether reusable parts (a correction arm, an ERA5 door) make later questions cheaper | Scientific quality: cost can also fall because ambition does | bookkeeping |
| **Retrodiction.** A pack sliced at head 48 asks for predictions of the six temperature probes later run | Cheap calibration, with no forecast | Learning in real time; n is small and dependent | 5–10 small calls; strict time slicing |

## 10. Approvals and decisions required (owner)

**Due regardless of I1:**
1. **How B1's vault run will load t0** without altering B1.
   - The vault runs frozen code that asks for the vanished revision, and B1 opens after 2027-04-01.
   - No recorded owner decision covers this. The Experiment 4 retrieval record says the fix "is a separate,
     owner-approved change", and that wording is ambiguous.
   - A workflow-level staging step could also serve I1's probes (section 3). Whether to use one fix or two is part of
     this decision.

**To make I1 runnable:**
2. **Who closes the protocol gaps in section 6.** For example:
   - the researcher, in one recorded revision call that receives this review as data and may only revise I1's
     protocol or abstain;
   - or the owner directly.

   The orchestrator should not close them.
3. **The route.** Section 3, route A is the realistic one. It departs from the researcher's assumption of
   researcher-submitted probes.
4. **The engine probe-path t0 loader** (change 1). It keeps the gate fingerprint.
5. **The engine extension** (changes 2–6), at about 5–7.5 engineer-days: about 4–6.5 for changes 2–5 and about 1 for
   the pinball loss. Building it outside the fingerprinted files avoids a re-gate.
6. **The ERA5 source:**
   - the read itself;
   - the upstream licence and attribution, which a human must check;
   - the oracle exemption rule: never ranked, never decides, never claim evidence.
7. **A one-page frozen protocol, approved before any run.** Freeze it as a document; it is not a vault batch. It
   covers:
   - the correction specification and estimator rule;
   - one decision rule;
   - the Holm family;
   - the margins;
   - the oracle reading;
   - the day set;
   - the bootstrap settings;
   - the slices;
   - the readout script;
   - the data-vintage check.
8. **Discovery budget and API spend.** Route A charges 0 evaluations and makes no API calls.
9. **Whether I1 is exploratory only, or should be built so that a later vault claim could cite it.** The latter needs a
   claims extension and a new batch after B1.

**About the researcher programme:**
10. **The policy for the next evidence pack:**
    - whether it includes this answer and I1's results;
    - whether per-day series, or per-year and per-season slices computed by the builder, stay excluded.
11. **Whether to approve any compounding-learning measurement in section 9**, and its token budget.

## Files

**This review's files:**
- [`feasibility_power.py`](feasibility_power.py) and [`feasibility_power.json`](feasibility_power.json): the power
  analogue. The 7-day check reproduces seq 51's interval exactly.

**Related documents:**
- The proposal: [`RESEARCHER_PROPOSAL.md`](RESEARCHER_PROPOSAL.md).
- What the researcher received: [`RESEARCHER_BRIEF.md`](RESEARCHER_BRIEF.md).

**Not committed:** the review workflow's agents' scratch scripts, which stay outside the repository.

**Where the numbers come from:**
- **Measured numbers** trace to a ledger seq, a file and line, or `feasibility_power.json`.
- **The probabilities in section 5** are normal approximations in `feasibility_power.json`.
- **The runtime figures in section 4** are arithmetic on the recorded timings and day counts it states.
- **The effort estimates** are engineering judgement.
- **The workflow counts in section 1** come from the review workflow itself.
