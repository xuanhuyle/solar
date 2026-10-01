# Evidence pack `exp5-evidence/1`

Built mechanically by `build_evidence_pack.py`. Each record has an id to cite.

## Evidence grades

- **confirmed_on_sealed_data**: a claim frozen before the data were scored and confirmed once on sealed data
- **discovery_grade_preregistered**: a pre-registered test whose rules were frozen before any data were seen, run on public or already-explored data: exploratory, never confirmation
- **exploratory**: a measurement on explored data with no pre-registered verdict: exploratory only
- **rehearsal**: a vault dry run on already-consumed data: tests the machinery, confirms nothing
- **legacy**: a result recorded before the engine existed, as summarised in the ledger seed; it says when and how the result was recorded, not its quality or design: whether its comparisons were frozen before the run is stated in that experiment's narrative record
- **process**: a frozen specification, gate, rule change, amendment or provenance event: how the evidence was produced; any rationale in it is the argument made at the time, a claim to evaluate
- **design_only**: a design document; nothing ran
- **external_report**: the project's page summarising claims made by t0's authors in their technical report, with the project's own notes on what it tested; the authors' claims are not tested here unless stated
- **researcher_note**: the AI researcher's earlier decision and reasoning in the engine loop, as it wrote it under that loop's instructions (choose catalogue probes that could become a clean, freezable claim: one arm, one comparator, a large and stable effect; freeze a claim batch when the exploratory evidence is strong and stable); where set, owner_question is the project owner's question that the iteration was answering, verbatim
- **owner_directive**: the project owner's instruction; any reasoning in it is a claim to evaluate
- **narrative**: the project's write-up at the time, verbatim: it contains numbers, caveats and the authors' interpretations, which are claims to evaluate, not established knowledge
- **infrastructure**: a fact about what the current code, data and rules allow

## Verification labels

- **independently_reproduced**: recomputed by an independent implementation from the original recorded outputs
- **rerun_agreed**: re-runs on separate runners agreed at the displayed precision
- **reproduced_within_tolerance**: the engine's own declarative code path, not the original code, re-ran a computation recorded earlier; its numbers matched the recorded ones within the tolerance stated in the reproduction-check gate record of the same run, not exactly; a pointer record means a later run, after code changes, gave numbers identical to the record it points to
- **audited**: reviewed by an independent read-only audit; caveats recorded
- **internal_consistency_only**: checked against the run's own records only
- **not_independently_verified**: taken as recorded

## Deliberately excluded

- Earlier engineering recommendations about which experiment to run next (for example the Experiment 2 pre-registration's 'recommended next experiment' and recommendations made in chat). *Why:* the researcher, not the engineering orchestrator, chooses the next investigation.
- README sections not included as records: the introduction; Experiment 0's 'Reading it' and 'Reproducing these numbers'; 'The experiment' (Methods, Pre-registered analysis, Metrics); Model access; Data and Data vintage; Outputs; Running it on GitHub Actions; Useful flags; Sanity checks; Tests; Layout; Scope; and the README Experiment 4 section. *Why:* methods and operating documentation, or a restatement of records included here; the text is in README.md.
- Experiment 4's FACT_SHEET.md (all sections), verify_integrity.md, verify_reading.md, verify_statistics.md, k2_attempts.jsonl, and INDEPENDENT_REPLICATION.md sections 1, 2 and 'Files'. *Why:* they restate results.json, run_meta.json and PRICE_SPEC['carry_forward'] (included), or record provenance and field-by-field comparisons whose outcome the replication's other sections state; their earlier verification gap is superseded by X4-REPLICATION.
- The per-day series ('per_day') of every probe_result and vault-rehearsal record, and the probe records' per-method leak-check detail, dropped_nonfinite, data and windows_built fields. *Why:* size; each comparison's skill, 95% interval, p, MAEs, days won and lost, and each verdict are included; the full series stay on the ledger at the cited seq.
- Ledger entries of kind genesis (seq 0), config, and probe_submitted. *Why:* code fingerprints and submissions whose spec, rationale, builds_on and submitter reappear in the matching probe_result record; they stay on the ledger.
- Model identifiers, API usage and request ids of earlier research calls. *Why:* not evidence about forecasting; they stay on the ledger.
- Any data from 2026 onward. *Why:* sealed: readable only through the forward vault.

## Records

### R-EXP0-0: Results — full year 2024

*Experiment:* EXP0 · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Results — full year 2024"}`

````text
## Results — full year 2024

Run on GitHub Actions against live ODRÉ data and the real `t0-alpha` weights
(Hugging Face commit `9b02c5f4bb6c89ba15d9fa74554018fe6464220b`, `tfc-t0` 0.3.2,
`torch` 2.14.0+cpu). Two runs on separate runner VMs —
[#5](https://github.com/xuanhuyle/solar/actions/runs/34682454351) at `2438a03` and
[#6](https://github.com/xuanhuyle/solar/actions/runs/34683244310) at `4f8dfc5` —
recomputed all 365 forecasts and agree on every number below at its displayed
precision (full-precision values agree to ~0.03 MW per point; CPU inference is
deterministic and the bootstrap is seeded).

Data: `eco2mix-national-cons-def`, 2022-01-01 → 2024-12-31, 52,602 half-hours
with 6 missing — the repeated autumn-DST hour in each year, which ODRÉ omits.
Only the 2024 pair touches the scored targets and lags: it removes 2024-10-27
itself (incomplete day), 2024-10-28 (the previous-day lag lands in it) and
2024-11-03 (the previous-week lag lands in it), leaving **363 of 366 delivery
days**. *[Phase 2 correction: the 2023 and 2024 gaps do sit inside t0's 90-day
context for 90 of the 363 scored origins, where the model treats them as missing
values; `run_meta.json` records the count. Corrected at the Experiment 0 freeze
from "92 of the 363 origins", a count that also included the two windows the
drop rule removes (fixed in `3c4abb9`; run #11 reports 90).]* The
scored actuals sum to 24.3 TWh, matching RTE's published 2024 solar output.
Peak proxy 14,011 MW (p99 of 2024 generation; about 0.64× the installed
capacity, which grew from 19.3 to 24.3 GW during the year).

### Headline

| Method | MAE (MW) | nMAE (mean) | nMAE (peak) | ≈ % of capacity | Daytime MAE | Daytime nMAE |
|---|---:|---:|---:|---:|---:|---:|
| **t0-alpha (zero-shot)** | **704** | **25.2%** | **5.02%** | **3.2%** | **1,293** | **23.1%** |
| Same time, previous day | 747 | 26.7% | 5.33% | 3.4% | 1,496 | 26.7% |
| Same time, previous week | 822 | 29.4% | 5.87% | 3.8% | 1,644 | 29.4% |

All-hours over 17,422 half-hours. "Daytime" is the 8,696 half-hours whose
(month, half-hour) climatological mean generation exceeds 1% of the peak proxy —
23.96 half-hours per delivery day, which coincides with geometric daylight at
French latitudes (24.1 for sun elevation > 0°). It is a reporting filter applied
identically to every method, never a model input. "% of capacity" converts
nMAE(peak) by the 0.64 factor above so it can be read against
capacity-normalised literature.

### Relative improvement of t0

| vs baseline | All hours (95% CI) | Daytime (95% CI) | Days won, all hours | Days won, daytime |
|---|---:|---:|---:|---:|
| Same time, previous day | +5.8% [+1.2, +10.3] | +13.6% [+9.1, +18.0] | 192 / 363 = 52.9% (p = 0.29) | 59% (p < 0.001) |
| Same time, previous week | +14.4% [+6.8, +21.4] | +21.3% [+14.2, +27.9] | 205 / 363 = 56.5% (p = 0.016) | 62% (p < 0.001) |

Intervals are percentile moving-block bootstraps over delivery days (7-day
blocks, B = 2000, seed 0, numpy 2.4), recomputing the skill from pooled sums in
every resample; an independent reimplementation reproduces them to four
decimals, and a different seed or numpy release moves the bounds by about
±0.2 points. Win-rate p-values are exact two-sided binomial tests against 50%,
which treat days as independent and are therefore slightly generous.

Three of the four comparisons are unambiguous (z ≈ 4–6, p < 0.001). The
all-hours comparison against previous-day — Phase 1's primary test; Phase 2
pre-registered `t0` vs `blend_50` instead — is the least
certain: p ≈ 0.01, a 99% interval would touch zero, and it sits exactly on a
Bonferroni-of-four threshold. Its lower bound with 1-, 3-, 14- and 30-day blocks
is +0.2%, +0.6%, +0.9% and +1.5%: positive throughout, never by much.

### What the numbers actually say

**Against same-time-last-week the result is clear.** +14% all hours, +21%
daytime, positive in every one of the twelve months, more days won than lost.

**Against same-time-yesterday it is real but thin and uneven.** The pooled
all-hours gain of +5.8% clears zero with little to spare, and on a day count
t0 is at a coin flip: 192 of 363 days, indistinguishable from 50%. Those two
facts are not in tension — the pooled skill is a MW-weighted mean of daily
differences (a summer day weighs about three winter days) and has more power
than counting signs; together they say the average daily edge is small relative
to the day-to-day spread of the difference. Measured directly, the annual net
gain hinges on a handful of days: the ten best — 3% of the year — carry 77% of
it. Remove them and the skill is +1.4%; remove twenty and it is negative. By
month it is positive from February to August and in December (Feb and Jun–Aug
+10 to +15%), and *negative* in January, September, October and November
(−2 to −6%). The daytime comparison (+13.6%, 59% of days) is robust to all of
this.

**Where the edge is — and what it is worth.** By local clock time, with the
previous-day baseline's source day marked:

| Delivery-day band | Mean actual | t0 MAE | prev-day MAE | t0 vs prev-day | t0 vs prev-week |
|---|---:|---:|---:|---:|---:|
| 00:00–05:30 | 0 MW | 124 | 0 | worse | worse |
| 06:00–08:30, dawn ramp | 359 MW | 121 | 75 | −61% | −3% |
| 09:00–12:00, prev-day copies **D-1** | 5,437 MW | 1,281 | 1,318 | **+2.8%** | +24.2% |
| 12:30–16:30, prev-day copies **D-2** | 8,112 MW | 1,801 | 2,301 | **+21.8%** | +22.7% |
| 17:00–19:30, dusk (D-2) | 3,258 MW | 798 | 868 | +8.1% | +14.6% |
| 20:00–21:30 | 330 MW | 141 | 65 | worse | worse |
| 22:00–23:30, horizon end | 2 MW | 259 | 1 | worse | worse |

Read the two right-hand columns together. Against previous-week, which has no
day switch, t0 is a steady +22–24% better across the whole daylight day.
Against previous-day, its edge is +2.8% in the morning — where the baseline
holds yesterday morning, 24 h old — and +21.8% in the afternoon, where the noon
gate has forced the baseline onto the day before yesterday. **t0 is worth about
a 24-hour-old copy of the same half-hour wherever one exists, and roughly 22%
better than anything older.** That is the precise form of its zero-shot skill
here. *[Phase 2 correction: in daylight. Over all hours raw t0 is 15.6% behind
previous-day on the half-hours within 24 h of the gate, because its night
floor sits there; the night-zeroed variant is 0.8% behind (`by_band.csv`).]*

It follows that the annual +5.8% over previous-day is largely the size of the
gate handicap. At a 12:00 D-1 gate the baseline may use D-1 for the 25
half-hours through 12:00 local on a normal day (13:00 CEST on 2024-03-31,
11:00 CET on 2024-10-27, because legality is decided in UTC), but the 23
half-hours after it carry 70.0% of the year's generation *[Phase 2 correction:
computed from `by_slot.csv`; originally stated as "about two-thirds (60% in
winter, 70% in summer)"]* and must be copied from D-2. On a synthetic series calibrated to this run that fallback
costs the baseline 3–8% of MAE, and on Spanish national data it costs about
15% — either way, the whole of t0's margin. The baseline is the correct,
leakage-free one; the point is what "beats same-time-yesterday" means at a
day-ahead gate. t0 is worse than previous-day on 31 of the 48 half-hours.

**Why the daytime and all-hours columns differ.** Not because night zeros
dilute anything: a half-hour where every method errs by ~0 adds nothing to
either side of a ratio-of-sums skill score, so night padding cannot move it.
The all-hours skill is lower than the daytime skill for exactly one reason —
t0's own night error, which the baselines never incur. The daytime column
approximates "t0 with its output zeroed when the sun is down" *[Phase 2
correction: only approximately — a legal, timestamp-only mask covers 78% of the
reporting night and recovers 82.8% of the night error, so the measured
night-zeroed variant lands 1.3 points below the daytime figure against
previous-day; see Phase 2]*, and the all-hours column is the raw median. The daytime figure does depend on the 1% cut: loosen it and the number
drifts toward the threshold-free +5.8%; tighten it and it moves the other way.
The ordering of the three methods never changes under any threshold tried, or
under an astronomical mask.

**t0 does not switch off at night, and it costs more than half of its margin.**
It forecasts a floor of 22–290 MW on every half-hour that is dark in all
twelve months — about 110–170 MW through the small hours, falling to 22 MW at
06:30, and rising to 290 MW at 23:30, the last step of the horizon — against an
actual of ~1 MW. That is 8% of t0's total absolute error, and it is a floor
across the night rather than a sunrise/sunset timing slip: those eighteen
always-dark slots (00:00–06:30 and 22:00–23:30 local) carry 92.0% of the night
error *[Phase 2 correction, from the run's own `daytime_mask.csv` and
`by_slot.csv`; originally stated as "a floor of 100–290 MW" and "sixteen
always-dark slots carry 83%"]*. The baselines make essentially none. t0's night error is
1,018,243 MW over 8,726 night half-hours, 116.7 MW per point, consistent with
its 117.5 MW mean night forecast. Zeroing it under the reporting mask would
move the all-hours result from +5.8% to ≈+13.6% against previous-day — exactly
the daytime figure — but that mask is derived from the scored actuals and no
legal forecaster can compute it. *[Phase 2 correction: measured with a
timestamp-only mask, `t0_night_zero` reaches +12.3% [+8.0, +16.6] over
previous-day, and the night floor costs 53% of that measured margin; originally
projected as "≈+13.6%" and "57% of the achievable margin". See Phase 2.]* It is
a one-line post-processing fix, deliberately not applied to `t0` itself, because
it would change the method under test; Phase 2 scores it as a separate method.

**These are the weakest legal naive references.** Both baselines are single-lag
copies. No smoothed naive method was run — a trailing mean or median of legal
same-slot values, or a persistence/climatology blend. On Spanish national data
under the same noon gate, a 7-day same-slot mean alone is worse than
previous-day, but a 50/50 blend of previous-day and that mean gains about +5%
over it: the same size as t0's margin here. So "beats persistence" must not be
read as "beats every naive method"; the fair reading is that t0 extracts about
what competent statistical use of the series' own history extracts. *[Phase 2
closes this: on this data the 50/50 blend gains +13.6% over previous-day, more
than twice t0's +5.8%, and beats raw t0 by 9.0% all hours; in daylight the two
are indistinguishable. See Phase 2.]*

**Absolute levels must be read against national-scale references, not
plant-level ones.** Same-time-yesterday persistence on a national PV series
lands around 25–40% nMAE(mean) — Spain 2015–18: 38% (PV+CSP); Germany: ~23–25%
on daily energy, ~30% implied at half-hourly resolution — so France's 26.7% is
at the good end of normal, and t0's 25.2% is what a no-weather method should
produce. Operational NWP-driven national day-ahead forecasts reach roughly
8–20% nMAE(mean), about 1.7–2.5% of installed capacity (Germany 2.7% and Italy
3.6% nRMSE of capacity; Spain's TSO 8.5% of mean generation over 2015–18,
+78% over previous-day). National aggregation lowers every method's error, but
least for persistence, because day-to-day synoptic change does not average out
across a country the way local cloudiness does — which is why both baselines
and t0 sit far below plant-level bands while the gap to a weather-driven
forecast stays large. This is not a leak: every baseline source is asserted at
or before the origin, t0's context is cut at the origin, the peak proxy and
daytime mask are computed from actuals after scoring and never enter a
forecast, and rewriting all post-origin data changes no forecast (tests). A
leak into t0 would show as a large margin over persistence; the observed margin
is 5.8%, an order of magnitude below what weather buys at national scale.
````

### R-EXP0-1: Results — Phase 2: competent historical-only baselines, full year 2024

*Experiment:* EXP0 · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Results — Phase 2: competent historical-only baselines, full year 2024"}`

````text
## Results — Phase 2: competent historical-only baselines, full year 2024

Same data, weights, origin, target, context, scored days and metrics as Phase 1;
only the set of methods grew. Run on GitHub Actions against the cached ODRÉ
export (raw-file sha256 and value fingerprint in `run_meta.json`) with the
pinned `t0-alpha` weights (`9b02c5f4…`, `tfc-t0` 0.3.2, `torch` 2.14.0+cpu,
`numpy` 2.4.6, `pandas` 2.3.3 — the run-#6 stack, now pinned):
[#11](https://github.com/xuanhuyle/solar/actions/runs/34744546087) at `3c4abb9`. Two earlier full runs on separate runners at the same
weights and data ([#9](https://github.com/xuanhuyle/solar/actions/runs/34743465128),
[#10](https://github.com/xuanhuyle/solar/actions/runs/34743614294)) agree with
it at displayed precision; between them the `t0` forecasts differ by at most
0.003 MW per point and every baseline row is bit-identical (compared from
their echoed per-day tables). Every table below is written by the run
(`results/readme_tables.md`, `pairwise.csv`, `ranking.csv`); nothing in this
section is hand-computed.

### What was known before Phase 2

Zero-shot `t0` scored 704 MW against two single-lag copies: +5.8 % [+1.2, +10.3]
over same-time-yesterday and +14.4 % [+6.8, +21.4] over same-time-last-week.
Phase 1 argued that the margin over yesterday was about the size of the D-2
handicap the noon gate imposes on that baseline (an estimate calibrated on
synthetic and Spanish data), found a floor through the night, and flagged one
comparison as untested: *no smoothed naive method was run*. Phase 2 ran five.

The Phase 1 rows reproduce in the Phase 2 run: per-day error sums for
`prev_day` and `prev_week` identical on all 363 days, `t0`'s per-day sums
within 0.003 MW per point (at most 0.14 MW on any day's sum; pooled MAE
703.82316 vs 703.82312 MW), all four Phase 1 skill intervals to four decimals,
days won 192 / 205 (all hours) and 215 / 226 (daytime), the same 363 days and
drop set, peak proxy 14,011 MW, and the reporting mask identical on the Phase 1
rows and on all rows.

### What the stronger baselines change

| # | Method | MAE (MW) | nMAE (mean) | vs previous day | vs `blend_50` |
|---|---|---:|---:|---:|---:|
| 1 | `ewma` (α = 0.3, 14 legal days) | 641 | 22.9 % | +14.3 % [+10.4, +18.1] | +0.7 % [−1.3, +3.0] |
| 2 | `mean_7d` | 645 | 23.1 % | +13.6 % [+8.0, +19.0] | +0.0 % [−3.8, +3.9] |
| 3 | `blend_50` (½ previous day + ½ `mean_7d`) | 646 | 23.1 % | +13.6 % [+11.0, +16.1] | — |
| 4 | `t0_night_zero` | 656 | 23.5 % | +12.3 % [+8.0, +16.6] | −1.5 % [−6.2, +2.9] |
| 5 | `median_7d` | 669 | 23.9 % | +10.5 % [+4.8, +16.0] | −3.6 % [−7.8, +0.6] |
| 6 | `mean_3d` | 696 | 24.9 % | +6.8 % [+2.6, +11.2] | −7.9 % [−11.6, −3.9] |
| 7 | **`t0` (raw, zero-shot)** | **704** | **25.2 %** | **+5.8 % [+1.2, +10.3]** | **−9.0 % [−13.8, −4.3]** |
| 8 | `prev_day` | 747 | 26.7 % | — | −15.8 % [−19.2, −12.3] |
| 9 | `prev_week` | 822 | 29.4 % | −10.0 % [−20.7, −0.3] | −27.3 % [−37.6, −17.3] |

All hours, 17,422 half-hours per method; intervals are the Phase 1 7-day
moving-block bootstrap (B = 2000, seed 0 for every pair). The daytime ranking
(8,696 half-hours) has the same order except that raw `t0` ties its
night-zeroed variant at 1,293 MW, both 0.1 % behind `blend_50`.

The obvious predetermined heuristic — half yesterday's value, half the trailing
seven-day same-slot mean — removes 13.6 % of previous-day's error, more than
twice what `t0` removes (5.8 %), and wins 259 of 363 days against previous day
(213 of 363 against `t0`). The trailing seven-day mean alone and the EWMA do
the same within noise: the top three are separated by 5 MW and both of their
intervals against `blend_50` straddle zero. The median is a little worse, the
three-day mean worse still (presumably because it keeps more of the day-to-day
noise a seven-day window averages out), and the two single-lag copies are last.
Every one of the five smoothed baselines beats same-time-yesterday beyond its
interval and by the sign test (all p ≤ 0.006). The ordering is a coin flip well
below the top three too: `t0_night_zero` sits −1.5 % [−6.2, +2.9] from
`blend_50` (185 of 363 days, p = 0.75), the median's −3.6 % [−7.8, +0.6]
against `blend_50` straddles zero, and raw `t0` is indistinguishable from
`mean_3d` (−1.1 % [−7.2, +4.4], 180 of 363 days). Only the gaps from the top
three down to `mean_3d`, `t0` and the two single-lag copies are resolved.

Where the smoothed baselines gain is instructive: split at the gate, they beat
previous-day in both halves of the day, by more in the afternoon band, where
previous-day holds a 48-hour-old copy and a seven-day mean does not care
(`by_band.csv`: `blend_50` 970 MW vs `prev_day` 1,139 MW there, −15 %; 347 vs
387 MW in the morning band, −10 %). Between 79 % (`blend_50`) and 99 %
(`median_7d`) of each smoothed baseline's error reduction against previous-day
sits in that afternoon band, against its 70 % share of generation — source
staleness, not afternoon difficulty: the methods that never switch source
(`prev_week`, `t0`) have *lower* nMAE in the afternoon band than in the morning.

### Does raw t0 still add measurable value?

**The pre-registered primary comparison, `t0` vs `blend_50`: no — the blend
is better.** All hours, `t0`'s MAE is 9.0 % *higher* [−13.8, −4.3 skill], it
loses 213 of 363 days (150 won, sign test p = 0.001), and the interval stays
below zero at each of the five block lengths tested, 1 to 30 days (upper bound
−3.5 % to −4.9 %). The deficit is not concentrated: removing `t0`'s ten best
days makes it larger (−13.6 %) and removing its twenty *worst* days still
leaves −2.7 %; it is negative in ten of twelve months all hours (worst
January −26 % and October −22 %; positive only June +4 % and August +0.2 %),
six of twelve daytime-only — monthly figures are pooled point estimates
without intervals. Daytime only, the two are indistinguishable: −0.1 %
[−4.9, +4.5], 190 days won to 173 (p = 0.40) — a null result, not
equivalence: the interval leaves room for a true daytime difference of up to
about 5 % either way. The difference between the two slices is `t0`'s night
error: 98.9 % of its all-hours deficit against `blend_50` sits on the
reporting-night half-hours, and the timestamp-only dark mask below, which
covers 78 % of that night, removes 83 % of the deficit.

Against the other smoothed baselines the pattern is the same. All hours `t0`
loses to `ewma` (−9.8 % [−15.5, −4.5]) and to `mean_7d` (−9.1 % [−15.8, −2.6]),
and is indistinguishable from `median_7d` (−5.3 % [−11.9, +1.0]) and `mean_3d`
(−1.1 % [−7.2, +4.4]). Daytime it beats only `mean_3d` (+7.2 % [+1.1, +12.4]; exploratory —
Holm-adjusted p = 0.21) and ties the other three smoothed baselines. Split by whether a D-1 same-slot
source exists at the gate, `t0` is 29 % behind `blend_50` on the half-hours
within 24 h of the origin (midnight to noon, where its pre-dawn night floor
and the morning ramp sit and the baselines hold yesterday's value; the evening
floor, 22:00–23:30, is in the other band) and 1.3 % behind on the rest of the
day, where the baselines fall back to two-day-old sources.

Read together: what zero-shot `t0` extracts from ninety days of history is, in
daylight, indistinguishable from what a seven-day same-slot mean extracts from
the last month of it (−0.2 % [−6.5, +5.8], 181 days to 182) — and over the
whole day it is less, because it forecasts generation in the dark.

### Does trivial night zeroing change the conclusion?

`t0_night_zero` is the identical forecast set to zero where the sun is below
the horizon everywhere in France. It removes 6.9 % [+6.0, +7.7] of `t0`'s error
(better on 362 of 363 days, tied on one), which lifts its margin over
previous-day from +5.8 % to **+12.3 % [+8.0, +16.6]** — and puts it at
−1.5 % [−6.2, +2.9] against `blend_50`, 185 days won to 178 (p = 0.75):
**indistinguishable from the blend, not better** — fourth in the ranking
and, like the three above it, not separable from `blend_50` by interval or
sign test; the interval is nine points wide and the point estimate sits on
the wrong side of zero on both slices. In daylight it *is* `t0` (all 363 days
tied), so nothing changes there.

The mask covers 6,804 scored half-hour rows (39.1 % of them; 78 % of the
reporting night), only three of which fall inside the reporting daytime. The
actual generation inside it sums to 1,645 MW over the whole year (0.003 % of
the year's generation) and never exceeds 8 MW in a half-hour, so the rule
zeroes no material output. Zeroing removes 841,236 MW of absolute error,
82.6 % of `t0`'s 1,018,243 MW night error (the 1,645 MW of real output inside
the mask remains as error); the variant's mean night forecast is 20.8 MW
against `t0`'s 117.5 MW. The civil-twilight variant (−6°, computed from the
same forecasts as a sensitivity, not a method) masks 5,972 rows and scores
662 MW, −2.5 % against `blend_50`: the threshold moves the number by about a
point and the conclusion not at all.

This measures what Phase 1 could only project, and corrects it: the projection
"zeroing would move +5.8 % to ≈ +13.6 % against previous-day" used the
actual-derived reporting mask, which no legal forecaster can compute; a
timestamp-only mask reaches +12.3 %. The night floor costs `t0` 48 MW of MAE,
53 % of the variant's 92 MW margin over previous-day (Phase 1 said 57 % of a
projected margin). Under the run's own reporting mask, the 18 half-hour slots
that are night in every month (00:00–06:30 and 22:00–23:30 local) carry 92.0 %
of `t0`'s night error (Phase 1 said sixteen slots and 83 %), and `t0`'s mean
error on them runs from 22 MW (06:30) to 290 MW (23:30), not 100–290 MW.

### Statistical uncertainty

Twenty pairwise rows were computed; one comparison (`t0` vs `blend_50`) was
pre-registered as primary and occupies two of them, one per slice. Its
all-hours interval excludes zero and its sign test (p = 0.001) survives a
Bonferroni correction across all twenty (Holm-adjusted p = 0.014 over the 19
informative sign tests; a Bonferroni-widened 99.74 % interval, [−16.8, −1.4],
still excludes zero). The daytime primary and the night-zeroed variant's
comparison with the blend are null results with intervals of about ±5 points,
the width the 7-day block bootstrap gives these comparisons on 363 days.
Multiplicity cuts the other way too: two secondary claims do not survive a
Holm correction and are exploratory — `t0` beats `prev_week` all hours (raw
p = 0.016, Holm 0.17) and `t0` beats `mean_3d` in daylight (raw 0.021, Holm
0.21) — and widening the 95 % intervals to a Bonferroni level removes the
zero-exclusion of three of them, among which the Phase 1 headline itself,
`t0` vs `prev_day` all hours ([−1.2, +11.9] widened). Among the secondary rows, `t0` vs `median_7d` (both
slices), vs `mean_3d` (all hours only; its daytime interval [+1.1, +12.4]
excludes zero, p = 0.021), and the daytime rows vs `mean_7d` ([−6.5, +5.8])
and vs `ewma` ([−6.4, +4.3]) cross zero and are reported as such. The two
slices disagree in sign only for `t0` vs `mean_3d` and `t0` vs `median_7d`,
where at least one interval covers zero. The bootstrap resamples 7-day blocks
of delivery days and weights days by energy; the sign test treats days as
independent and counts them equally — the two disagree on five comparisons,
most sharply for `prev_week` vs `prev_day` (−10.0 % [−20.7, −0.3] pooled, 184
days to 179 by count, p = 0.83) and for the Phase 1 headline (`t0` vs
`prev_day` all hours: interval clear of zero, 192 days to 171, p = 0.29),
which is why both are always reported. The monthly, band and per-slot
breakdowns are all-hours pooled point estimates without intervals. The export contains exactly
two half-hours whose ODRÉ vintage is "consolidated" rather than "definitive":
2024-12-31 23:00 and 23:30 UTC — 00:00 and 00:30 local on 2025-01-01, after the
last scored delivery day and outside every context window — so every value any
method read or was scored on is definitive. The 2023 and 2024 autumn-DST gaps
sit inside `t0`'s 90-day context for 90 of the 363 scored origins, where the
model treats them as missing values (the 2022 gap predates every context).

### Limitations

One year, one country, one gate, one model revision. No weather, no calendar
input, and no solar-geometry input to any model except the timestamp-only dark
mask that defines `t0_night_zero`; no tuning: the smoothed baselines'
parameters (k = 3 / 7 / 7, α = 0.3 over the 14 most recent legal sources, a
30-day search, a 50/50 blend) are conventional defaults fixed before the run,
not searched, and so is the night mask (−0.833°, the standard sunset
convention); a searched baseline is a different experiment. The monthly, band
and per-slot breakdowns are pooled MAE without intervals. `t0` is scored on its
median only; its quantiles are not used. Inputs are the ex-post definitive
series for every method (see *Data vintage*); whether the ranking transfers to
real-time inputs is untested.
````

### L2: Experiment 0: t0 zero-shot vs historical baselines, French national solar, 2024

*Experiment:* EXP0 · *grade:* legacy · *verification:* rerun_agreed · *source:* `{"ledger": "engine-ledger", "seq": 2, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed", "verification_basis": "R-EXP0-0 and R-EXP0-1: runs on separate runners agree at displayed precision (Phase 1 runs #5 and #6; Phase 2 runs #9, #10 and #11)"}`

```json
{
 "commits": [
  "2438a03",
  "4f8dfc5",
  "3c4abb9"
 ],
 "id": "E0",
 "numbers": {
  "days": 363,
  "mae_mw": {
   "blend_50": 646,
   "ewma": 641,
   "prev_day": 747,
   "prev_week": 822,
   "t0": 704,
   "t0_night_zero": 656
  },
  "t0_vs_blend_50": [
   -0.09,
   -0.138,
   -0.043
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/34682454351",
  "https://github.com/xuanhuyle/solar/actions/runs/34683244310",
  "https://github.com/xuanhuyle/solar/actions/runs/34744546087"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "t0 alone (704 MW MAE) beats previous day (747) by +5.8% but loses to blend_50 (646) by -9.0% [-13.8, -4.3]; ewma 641 is best; 363 days, 2024",
 "title": "Experiment 0: t0 zero-shot vs historical baselines, French national solar, 2024"
}
```

### R-COV-2: Covariate slice: t0 with geometry and weather

*Experiment:* COV · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Covariate slice: t0 with geometry and weather"}`

````text
## Covariate slice: t0 with geometry and weather

Experiment 0 gave t0 nothing but the solar series' own history. This slice
asks the next question with the same data, gate, horizon, metrics and baselines:
**does t0 get better when it is also given known-future covariates?** It is a
discovery-grade measurement on 2024 only; data from 2025 onwards is never read.

**Arms** (every arm scored on the same days; every t0 arm also gets the
Experiment 0 night-zero variant):

| Method | Inputs |
|---|---|
| `t0`, `t0_night_zero` | Unchanged from Experiment 0: history only |
| `t0_geo` | + solar geometry: capacity-weighted `max(sin(elevation), 0)` over 12 regional points (timestamps only) |
| `t0_wx` | + an archived weather forecast of irradiance (Open-Meteo Previous Runs API, same 12 points) |
| `t0_wx_oracle` | + ERA5 reanalysis irradiance instead. **Not point-in-time**; a reference only, never ranked or reported as a finding |
| `wx_ratio` | No t0: the forecast irradiance times the same-slot ratio of output to forecast irradiance over the last 14 usable days |
| Experiment 0 baselines | Re-run on the same days |

**Point-in-time rule.** t0 reads the whole covariate window (context *and*
horizon) at once, so every covariate value it sees must have existed at the
gate. A lead-`N` archived forecast for hour `h` comes from a run that started
at most `24N` hours earlier and was published at most 10 hours after starting.
With the fixed 73-step horizon, lead 2 clears the gate by at least half an hour
on every 2024 day and lead 1 never does (tested). Lead 2 is used only if the
probe proves that the archive's `previous_day2` values come from runs started at
least 48 hours earlier; otherwise lead 3 is used. The backtest asserts the bound
for every forecast and fails the run on a violation. The only exemption is an
arm that both declares itself an oracle and has `oracle` in its name.

**Frozen comparisons** (`run_covariates.py`, `COMPARISONS`; paired 7-day block
bootstrap, one-sided):

- *Primary:* `t0_wx_night_zero` vs `t0_night_zero`. Does weather, given through
  t0's covariates, reduce error?
- *Secondary* (Holm-adjusted): `t0_wx_night_zero` vs `wx_ratio` and vs `ewma`;
  `t0_geo_night_zero` vs `t0_night_zero`; `t0_wx_night_zero` vs `t0_geo_night_zero`.
- *Diagnostic:* the ERA5 reference vs `t0_wx_night_zero`, which shows how much
  the forecast error costs.

**Run sequence** (Actions → Benchmark → pick an `experiment`):

1. `cov-probe`: weights, stamp convention, archive coverage, and what
   `previous_day2` means. It computes no forecast and no skill. Its constants
   are then frozen in `solarbench/covariates.py`.
2. `cov-known-answer`: real t0 on 2023 with a planted covariate, a noisy copy of
   the future target. It checks four things:
   - does t0 use the covariate;
   - is it aligned (a shift of ±1 or ±2 steps must be worse);
   - is it batch-invariant;
   - is it leak-free.
3. `cov-run` (`smoke`, then `full`): the 2024 comparison.

**Probe result** ([run #13](https://github.com/xuanhuyle/solar/actions/runs/36059249513); frozen in `solarbench/covariates.py` by commit `e807a62` before any covariate forecast was made):

- **Weights** (2023 solar production share): Nouvelle-Aquitaine 24.9%,
  Occitanie 20.5%, Provence-Alpes-Côte d'Azur 14.2%, Auvergne-Rhône-Alpes 11.4%,
  and the other eight regions 1.5–6.5% each.
- **Stamp convention:** eCO2mix stamps sit at the centre of their half-hour
  (measured −4 min).
- **Weather model:** `ecmwf_ifs025`, archived from 2024-03-08.
- **Lead: 3 days, not 2.** The Single Runs API had none of the 2024 ECMWF runs
  needed to prove what `previous_day2` means, so the conservative rule applies.
- **Scored days:** 207 delivery days can be scored, from 2024-06-06; the
  90-day context needs a complete archive.
- **ERA5:** complete on every one of those days.

**Known-answer check** ([run #14](https://github.com/xuanhuyle/solar/actions/runs/36098545565),
real t0 on 64 days of 2023). The planted covariate is the future target plus
Gaussian noise with a standard deviation of 607 MW.

| Check | Result |
|---|---|
| **Use** | **Weak.** MAE falls from 669 to 576 MW (ratio 0.86); the bar was ≤ 0.5. The covariate alone would be off by about 485 MW in daylight (by construction), yet t0 lands well above that |
| **Alignment** | Correct. The error is lowest with no shift and rises steadily with the shift: −2: 615, −1: 598, 0: 576, +1: 588, +2: 599 MW. It is blunt, because t0 uses the covariate weakly |
| **Batch composition** | No effect (0.006 MW) |
| **Leakage** | None. Rewriting the future target, or covariate cells outside the window, changes nothing, while a change inside the window does show up |
| **Sanitisation** | t0 replaced no non-finite outputs |
| **Pure-noise decoy** | No harm (671 MW) |

The adapter therefore works. By the rule fixed in advance, the full run
still went ahead, and the headline became how little t0 uses its covariates.

### Covariate slice results: full run, 205 delivery days

[Run #16](https://github.com/xuanhuyle/solar/actions/runs/36104401204) at
`e807a62`, with delivery days from 2024-06-06 to 2024-12-30.

- Every method is scored on the same days.
- Three days are left out: 2024-10-27 is incomplete in RTE's data, and
  2024-10-28 and 2024-11-03 lack a source for the persistence baselines (the
  DST gap, as in Experiment 0).
- Every weather value t0 read had been issued at least 25 h before its gate.

| Method | MAE (MW), all hours | vs `t0_night_zero` [95% CI] |
|---|---:|---:|
| `wx_ratio`: forecast irradiance × same-slot ratio, **no t0** | **401** | +39.9% [+34.3%, +45.6%] |
| `t0_wx_night_zero`: t0 + geometry + weather forecast | **496** | +25.6% [+21.6%, +29.6%] |
| `t0_wx_oracle_night_zero`: t0 + geometry + ERA5 (reference, not point-in-time) | 465 | *reference only* |
| `ewma`, the best Experiment 0 baseline | 662 | +0.8% [−5.8%, +8.5%] |
| `t0_night_zero` | 668 | — |
| `t0_geo_night_zero`: t0 + geometry | 670 | −0.3% [−3.6%, +2.5%] |
| `t0`, raw | 720 | −7.9% |

**Frozen comparisons** (one-sided block bootstrap; Holm correction over the four secondaries):

| Comparison | MAE reduction [95% CI] | Days won | p | Reading |
|---|---:|---:|---:|---|
| **Primary**: t0 + weather vs t0 (both night zero) | **+25.6%** [+21.6%, +29.6%] | 146 / 205 | 0.0005 | Better |
| t0 + weather vs `wx_ratio` | **−23.8%** [−33.7%, −15.5%] | 68 / 205 | 1.0 (Holm) | **Worse** |
| t0 + weather vs `ewma` | +25.0% [+19.2%, +29.8%] | 135 / 205 | 0.002 (Holm) | Better |
| t0 + geometry vs t0 | −0.3% [−3.6%, +2.5%] | 95 / 205 | 1.0 (Holm) | No effect |
| t0 + weather vs t0 + geometry | +25.9% [+22.3%, +29.9%] | 154 / 205 | 0.002 (Holm) | Better |
| *Diagnostic*: ERA5 reference vs t0 + weather | +6.4% [+2.7%, +10.6%] | 121 / 205 | — | Forecast error costs t0 about 6% |

**What the numbers say, plainly.**

1. **Weather is the information that matters.** Both weather methods beat
   every Experiment 0 method, `wx_ratio` by 40%. The history-only ceiling of
   roughly 640–670 MW is broken.
2. **t0 does use the weather covariate, but weakly.** The primary comparison is
   large and clear, yet a one-line ratio built from the same forecast beats
   t0 + weather by 24%.
   - The known-answer check agrees: t0 captures only a small part of a planted
     signal.
   - Giving t0 the reanalysis instead of the forecast improves it by only 6%,
     so the bottleneck is how t0 uses the covariate, not the forecast quality.
3. **Solar geometry adds nothing to t0.** Ninety days of history already give
   it the daily shape.

**What this does not show.**

- This is discovery grade: June to December 2024 only, on a year Experiment 0
  already used.
- The weather forecast is 3 days old at the gate.
- Nothing here is confirmed on unseen data. That needs sealed 2025 data and the
  owner's approval.

**Caveats, stated up front.**

- The archived forecast is about 3 days old at the gate (lead 3), whereas an
  operator would use a 12–36 h one. This understates the value of weather.
- Twelve points with 2023 production weights make a crude spatial model.
- The Open-Meteo free API is for non-commercial use (CC BY 4.0 data).
````

### L3: Covariate slice: t0 + geometry + archived weather forecast, national solar, Jun-Dec 2024

*Experiment:* COV · *grade:* legacy · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 3, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed"}`

```json
{
 "commits": [
  "e807a62",
  "258aed0"
 ],
 "id": "COV",
 "numbers": {
  "days": 205,
  "mae_mw": {
   "ewma": 662,
   "t0_night_zero": 668,
   "t0_wx_night_zero": 496,
   "wx_ratio": 401
  },
  "t0_wx_vs_t0": [
   0.256,
   0.216,
   0.296
  ],
  "t0_wx_vs_wx_ratio": [
   -0.238,
   -0.337,
   -0.155
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36059249513",
  "https://github.com/xuanhuyle/solar/actions/runs/36098545565",
  "https://github.com/xuanhuyle/solar/actions/runs/36104401204"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "t0 + weather cuts t0's MAE by +25.6% [21.6, 29.6] (496 vs 668 MW) but a one-line weather ratio without t0 is better still (401 MW; t0 + weather -23.8%); geometry adds nothing",
 "title": "Covariate slice: t0 + geometry + archived weather forecast, national solar, Jun-Dec 2024"
}
```

### R-EXP3-3: Experiment 3: t0 strengths probe

*Experiment:* EXP3 · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Experiment 3: t0 strengths probe"}`

````text
## Experiment 3: t0 strengths probe

Where is t0 genuinely strong? [`docs/experiment_3/T0_STRENGTHS.md`](docs/experiment_3/T0_STRENGTHS.md)
lists in one page what t0 is built to be good at and which of those strengths
we have not tested yet.

Four probes are frozen in `solarbench/probes.py` (`PROBES`) before any run.
Each has a question, a t0 arm, the best simple comparator, a metric and a
success rule:

| Probe | What it tests |
|---|---|
| P1 | Uncertainty bands, scored by pinball loss and coverage |
| P2 | t0 correcting `wx_ratio`'s errors |
| P3 | The 12 regional solar series forecast jointly |
| P4 | National electricity consumption with a public-holiday calendar |

**How to run.** Actions → Benchmark, with `experiment` set to `probes-check`
(data coverage only) and then `probes-run`. Data up to 2024-12-31 only.

### Experiment 3 results

Full run [#18](https://github.com/xuanhuyle/solar/actions/runs/36113438085)
at `f2dec78`, the freeze commit. The data check was run
[#17](https://github.com/xuanhuyle/solar/actions/runs/36113060649).

- A probe is **won** only if its primary skill is positive and its
  Holm-adjusted one-sided block-bootstrap p is below 0.05, taken over the
  four primaries.
- Skill is the reduction in loss relative to the comparator, with a 95% CI.

| Probe | t0 arm vs best simple | Days | Loss: t0 vs simple | Skill [95% CI] | Holm p | Result |
|---|---|---:|---:|---:|---:|---|
| **P1** uncertainty bands (pinball) | t0 + weather vs `wx_ratio` + its past-error spread | 207 | 186 vs 139 | **−34.4%** [−46.5%, −23.7%] | 1.0 | **Lost** |
| **P2** correcting `wx_ratio`'s errors (MAE, MW) | `wx_ratio` + t0 on its residuals vs `wx_ratio` | 207 | 414 vs 399 | −3.8% [−11.4%, +3.0%] | 1.0 | Lost (no gain) |
| **P3** 12 regions jointly (MAE, MW) | joint regional t0, summed, vs `ewma` | 365 | 633 vs 638 | +0.8% [−3.1%, +4.7%] | 1.0 | Not won (a tie) |
| **P4** national consumption (MAE, MW) | t0 + holidays vs `blend_50` (best simple on 2023) | 364 | **1,571 vs 3,114** | **+49.6%** [+44.2%, +55.1%] | **0.002** | **Won** |

**Secondary comparisons** (descriptive, not multiplicity-adjusted):
- **P1 coverage.** t0's 10–90% band covers only **57%** of daytime outcomes,
  against 78% for the simple band; the target was 70–90%.
- **P1 residual model.** Bands from t0-on-residuals are still worse than the
  simple band (−7.2%).
- **P2.** `wx_ratio` + t0-on-residuals roughly ties a simple bias correction
  (+2.8% [−6.1%, +10.3%]).
- **P3 regional vs national.** Forecasting the 12 regions and summing beats
  forecasting the national series with t0 (+3.1% [+0.2%, +5.9%]).
- **P3 joint vs independent.** Doing the 12 regions jointly adds nothing over
  doing them one by one (+0.1%). The gain comes from splitting into regions,
  not from t0's cross-series attention.
- **P4 calendar.** Plain t0, without the holiday calendar, already beats the
  best simple method by +47.2%. The calendar adds +4.5% [−1.7%, +8.4%].
- **P4 against RTE.** RTE's own day-ahead forecast (reference only; its issue
  time is not verified, and it uses weather) is still **14.8% better** than
  t0 + holidays: 1,368 vs 1,571 MW.

**What this says.**

- **t0 shines where the series' own history holds rich structure** that
  simple rules miss: consumption, with its weekly cycle, seasonal drift and
  holidays. There, with no weather at all, t0 halves the error of the best
  simple method.
- **On solar, simple rules already capture the daily cycle**, and weather
  dominates. t0's uncertainty bands are too narrow, correcting a simple
  weather model's errors does not help, and regional joint forecasting only
  ties.
- This is discovery grade, on 2024 only. P4 was then confirmed once on
  sealed 2025 data: see *Claim C1* below.
````

### L4: Experiment 3, probe P1: t0 uncertainty bands (pinball) vs wx_ratio + empirical bands, solar

*Experiment:* EXP3 · *grade:* legacy · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 4, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed"}`

```json
{
 "commits": [
  "f2dec78",
  "1e1e769"
 ],
 "id": "P1",
 "numbers": {
  "coverage_10_90": 0.57,
  "days": 207,
  "skill": [
   -0.344,
   -0.465,
   -0.237
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36113438085"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "lost: pinball -34.4% [-46.5, -23.7]; t0's 10-90% band covers 57% of daytime outcomes",
 "title": "Experiment 3, probe P1: t0 uncertainty bands (pinball) vs wx_ratio + empirical bands, solar"
}
```

### L5: Experiment 3, probe P2: t0 forecasting wx_ratio's residuals, solar

*Experiment:* EXP3 · *grade:* legacy · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 5, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed"}`

```json
{
 "commits": [
  "f2dec78",
  "1e1e769"
 ],
 "id": "P2",
 "numbers": {
  "days": 207,
  "skill": [
   -0.038,
   -0.114,
   0.03
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36113438085"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "lost: -3.8% [-11.4, +3.0] MAE vs wx_ratio",
 "title": "Experiment 3, probe P2: t0 forecasting wx_ratio's residuals, solar"
}
```

### L6: Experiment 3, probe P3: 12 regional solar series jointly, summed, vs ewma

*Experiment:* EXP3 · *grade:* legacy · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 6, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed"}`

```json
{
 "commits": [
  "f2dec78",
  "1e1e769"
 ],
 "id": "P3",
 "numbers": {
  "days": 365,
  "skill": [
   0.008,
   -0.031,
   0.047
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36113438085"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "tie: +0.8% [-3.1, +4.7]; regional sum beats national t0 by +3.1%, joint vs independent regions +0.1%",
 "title": "Experiment 3, probe P3: 12 regional solar series jointly, summed, vs ewma"
}
```

### L7: Experiment 3, probe P4: t0 + holidays vs blend_50, French national consumption, 2024

*Experiment:* EXP3 · *grade:* legacy · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 7, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed", "verification_basis": "R-C1-4: the 2024 dry run #19 reproduced P4 exactly; engine reproductions L12 and L27 agree within 0.5% (gates L15, L29)"}`

```json
{
 "commits": [
  "f2dec78",
  "1e1e769"
 ],
 "id": "P4",
 "numbers": {
  "days": 364,
  "mae_mw": {
   "blend_50": 3114.4,
   "rte_j1": 1368.2,
   "t0": 1644.4,
   "t0_cal": 1571.0
  },
  "skill": [
   0.496,
   0.442,
   0.551
  ]
 },
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36113438085"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "won: +49.6% [44.2, 55.1] (1,571 vs 3,114 MW), Holm p 0.002; plain t0 +47.2%; RTE's own D-1 forecast is 14.8% better than t0 + holidays",
 "title": "Experiment 3, probe P4: t0 + holidays vs blend_50, French national consumption, 2024"
}
```

### T0-REPORT: The project's summary of t0's technical report (the authors' claims) and its own notes on what was tested here

*Experiment:* EXP3 · *grade:* external_report · *verification:* not_applicable · *source:* `{"path": "docs/experiment_3/T0_STRENGTHS.md", "report": "arXiv:2609.24559 (docs/2609.24559.pdf)"}`

````text
# What t0 is built to be good at, and what we have tested

Sources:
- The t0 technical report, [arXiv:2609.24559](https://arxiv.org/abs/2609.24559), `docs/2609.24559.pdf`. Page numbers in brackets.
- The installed `tfc-t0` 0.3.2 code.

We use **t0-alpha**, which has 102M parameters. The report's larger **t0-beta** (256M parameters, 21 quantile levels) scores clearly better on its benchmarks [p.13–16]. It is not tested here.

| t0 is designed to… | What the report shows | Tested by us? |
|---|---|---|
| **Give uncertainty ranges**, not just one number: five levels from 10% to 90%, which cannot cross | Scored on probabilistic benchmarks. Its 10–90% band covers 78% of outcomes, slightly narrow. Levels outside 10–90% are clamped to the edges [p.9, 20–22] | **No.** We only scored the middle forecast → **probe P1** |
| **Use inputs known in advance** (forecasts, calendars) | Helps on 19 of 30 benchmark tasks (+6.3 skill points). Cuts error on German power prices by 51% when given load, solar and wind forecasts. Hurts on 11 of 30 tasks, including a 15-minute electricity series with weather [p.16–18] | **Yes** (covariate slice). A weather forecast cut t0's error by 26%, but a one-line weather ratio still beat t0 by 24%. A planted-signal test showed t0 uses such inputs only weakly |
| **Use inputs seen only in the past** | Helps on 9 of 12 tasks (+2.7 skill points) [p.18] | No, and not in this round |
| **Forecast several related series together** (attention across series) | A core design feature [p.7]. No results are given for regional or hierarchical data | **No** → **probe P3** |
| **Handle harder targets driven by calendar and weather**, such as electricity demand | Victoria demand, with temperature and holidays: t0-alpha MAE 373–380 MW, against 324–349 for the Chronos-2 model [p.29] | **No** → **probe P4** (national consumption with public holidays) |
| **Correct another model's errors** | Not claimed anywhere in the report | **No** → **probe P2** (our idea, not the authors') |
| **Work zero-shot with long histories**, up to 8,192 steps | Trained on 8,192-step windows. Reaches 95% of its accuracy from 1,024 steps [p.9, 25] | Partly: we use 4,320 steps (90 days) |

**Where the report says t0-alpha is ordinary:**
- It ranks 11th of 17 models on the GIFT-Eval benchmark.
- On energy data, it wins no clear majority of comparisons [p.14–15].
- Missing data hurts it more than its peers [p.24].

## The four probes (frozen in `solarbench/probes.py` before any run)

| Probe | Question | t0 arm | Compared with (best simple) | Metric | Counts as a win |
|---|---|---|---|---|---|
| P1 | Are t0's uncertainty bands better than simple bands? | t0 with the weather forecast, 5 native quantiles | `wx_ratio` plus the spread of its own past errors (28 days) | Pinball loss | Better, *and* t0's 10–90% band covers 70–90% of daytime outcomes |
| P2 | Can t0 correct the best simple forecast's errors? | `wx_ratio` + t0's forecast of `wx_ratio`'s own errors | `wx_ratio` | MAE | Better |
| P3 | Is forecasting the 12 regions together better than forecasting the nation? | t0 on 12 regional series at once, summed | `ewma` | MAE | Better |
| P4 | Is t0 better on national electricity consumption? | t0 + public-holiday calendar | The best simple method on 2023, chosen by rule | MAE | Better |

**Rules for all four:**
- Data up to 2024-12-31 only.
- "Better" means the error is lower with statistical confidence: a one-sided block bootstrap, corrected for testing four probes (Holm), at 5%.
- Every comparison is also reported in each probe's own units.
````

### R-C1-4: Claim C1: a one-shot confirmation on sealed 2025 data

*Experiment:* C1 · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Claim C1: a one-shot confirmation on sealed 2025 data"}`

````text
## Claim C1: a one-shot confirmation on sealed 2025 data

Experiment 3's strongest finding is frozen as **claim C1** in `solarbench/confirm.py`
(`CLAIM`, and its sha256 in `FROZEN_CLAIM_SHA256`). It was frozen before any 2025
data was scored or looked at. There is one boundary detail, found by the audit below: the
pre-freeze download ended at 2024-12-31 23:30 UTC, which is 00:30 Paris time on
2025-01-01. It therefore held the first two half-hours of C1's first day, which were
never scored or printed. The owner approved using the sealed 2025 data **once** to test it.

> On French national electricity consumption, t0 with the public-holiday calendar
> cuts day-ahead MAE versus `blend_50` by more than 25% over 2025.

**Verdict rules:**

| Verdict | When |
|---|---|
| CONFIRMED | The one-sided 95% lower bound of the skill (7-day block bootstrap) is above 25% |
| NOT CONFIRMED | Otherwise |
| INCONCLUSIVE | Fewer than 300 days are scored, or no data source is ≥ 95% complete |

**The single door to 2025 is `confirm.open_sealed`.** It opens only if all of these hold:

- the claim's hash matches the frozen one;
- the pinned model has already loaded;
- `ledger/confirmations.jsonl` records no earlier use.

The result is committed to that ledger, which closes the door. Since the audit, the
committed ledger is always consulted, and an access pass stops being valid once
its claim is recorded. So neither another `--ledger` path nor a hand-built pass
reopens it.

**Order of runs:**

1. `confirm-dryrun-2024` runs the identical path on 2024 and must reproduce
   probe P4.
2. `confirm-2025` runs once.

### Claim C1 result: CONFIRMED on 2025

**The run:**
- The one-shot run was [#20](https://github.com/xuanhuyle/solar/actions/runs/36145552543), at `46bf8b0`, the freeze commit.
- Its result is in [`ledger/confirmations.jsonl`](ledger/confirmations.jsonl). Since that entry was committed, `open_sealed` refuses C1, and a test keeps it that way.

**The 2024 dry run:** [#19](https://github.com/xuanhuyle/solar/actions/runs/36144786834) first reproduced probe P4 exactly. Its MAE was 1,571.0 vs 3,114.4 MW, a skill of +49.6%.

| 2025, 363 of 364 buildable days | Value |
|---|---|
| Verdict | **CONFIRMED**: the frozen claim, skill > 25% |
| One-sided 95% lower bound of the skill | **+42.0%** (threshold: 25%) |
| Skill of t0 + holidays vs `blend_50` [95% CI] | **+46.3%** [+41.3%, +51.4%] |
| MAE: t0 + holidays vs `blend_50` | **1,628 vs 3,032 MW** |
| Days won / lost | 298 / 65 of 363 |
| Source | `eco2mix-national-cons-def`, 99.99% complete; every 2025 row is *consolidated*, not yet *definitive* |

**Which 2025 days were not scored:**
- 2025-10-26 (the autumn clock change) has an incomplete target, so it was skipped.
- 2025-10-27 was also dropped, because `blend_50` reads the day before, which is incomplete.
- Both rules were frozen before the run.
- **What the code drops.** The code drops a day when *any* method in the run is non-finite, including the reported-only ones. The claim text says "either method".
- **No effect here.** In run #20 only `blend_50` caused a drop, so the scored days are exactly the ones the claim text implies.

**How the skill is measured.** Skill is 1 − MAE(t0 + holidays) / MAE(`blend_50`), pooled over all 17,422 scored half-hours. It is not a per-day rule: t0 + holidays lost 65 of the 363 days.

**Reported only, not part of the verdict:**
- **Plain t0**, without the calendar, vs `blend_50`: +43.6% [+39.4%, +49.0%], with an MAE of 1,711 MW.
- **The calendar's own contribution** was not tested in 2025. In 2024 it was +4.5% [−1.7%, +8.4%]. Almost all of the gain comes from t0 itself.
- **RTE's own day-ahead forecast** is still better than t0 + holidays. Its MAE is 1,322 vs 1,628 MW, so t0 + holidays scores −23.1% [−40.3%, −5.4%] against it. In 2024 the gap was 14.8%. RTE uses weather; t0 here sees only the past load and the calendar.

**What is confirmed, and what is not:**
- **Confirmed (the frozen claim).** From the load history and a holiday calendar alone, t0 cuts day-ahead MAE by more than 25% against `blend_50` on a year it had never seen. `blend_50` was the best simple rule on 2023. The observed cut was +46.3%, with a one-sided 95% lower bound of +42.0%.
- **Not shown:**
  - that t0 is better than a professional forecast;
  - that `blend_50` is still the best simple rule in 2025;
  - that the calendar matters.

### Audit of the C1 result

After the run, an independent read-only audit checked C1 through four lenses: the seal, whether the method was identical to P4, the statistics, and leakage and data vintage. A second reviewer then tried to refute each finding. **Nothing changes the verdict.** The findings that survived are caveats:

| Caveat | Effect on C1 | Done |
|---|---|---|
| The seal date is UTC midnight, but days are counted in Paris time. Two half-hours of 2025-01-01 were therefore in the pre-freeze data. | None; they were never scored or printed | Disclosed above. A future seal should be set in local time |
| The workflow's ODRÉ connectivity check read one unfiltered row, which was sometimes a 2025 row with a null solar value. | None: no consumption values | Now selects only the timestamp and prints nothing |
| The vault could be reopened with another `--ledger` path or a hand-built access pass. | None: exactly one `confirm-2025` run exists (#20) | Fixed in `confirm.py`, and tested |
| The sealed 2025 files remained in the `probe-v1` Actions cache that later runs restore. | None: no code reads them without the vault | `PROBE_CACHE_VERSION` bumped to `v2`, so the v1 copy is never restored again |
| The Experiment 0 loader has no seal check and an unfiltered fallback. It was never used past 2024. | None | Disclosed only, because Experiment 0 stays unchanged |
| The drop rule covers every method in the run, not only the two scored ones. | None in #20 | Disclosed above |
| The 2025 rows are *consolidated*. The context for early-2025 days mixes them with *definitive* 2024 rows. | None found: both methods read the same series. Numbers on a later definitive release would differ slightly | Disclosed |
| The result file does not record the context, gate or seed. | None: the run #20 log shows context 4,320, batch 64, horizon 73 and gate 12:00, which are the defaults at `46bf8b0` | Disclosed. A future runner should assert and record every claim parameter |
| Per-day errors, bootstrap draws and the data hash were not saved. The artifact expires about 2026-10-25. | The +42.0% bound cannot be re-derived or sensitivity-checked without a second look | Disclosed. For the record: job `108105702106`, artifact `10869990312`, sha256 `200040b29e591c2cef36eb5e78d451ef63d47ae1d503f3fd4f20a162378014a9`. A future confirmation should save them before the look |
````

### C1-CONFIRMATION: Claim C1's one-shot confirmation on sealed 2025 data

*Experiment:* C1 · *grade:* confirmed_on_sealed_data · *verification:* audited · *source:* `{"path": "ledger/confirmations.jsonl", "run_id": 36145552543, "commit": "46bf8b0"}`

```json
[
 {
  "claim_id": "C1",
  "claim_sha256": "8ed512e1863ca1b74f00c299c8bad15f52104bb8382cd046d504b759aefb8832",
  "year": 2025,
  "run": "https://github.com/xuanhuyle/solar/actions/runs/36145552543",
  "run_number": 20,
  "commit": "46bf8b0aeed8d36f6a46df451f8b54b3fe205fd5",
  "run_at": "2026-09-25T14:11:45+00:00",
  "verdict": "CONFIRMED",
  "lower_bound_one_sided_95": 0.42020472600932396,
  "threshold": 0.25,
  "skill": 0.463059791566946,
  "skill_ci95": [
   0.4125771898812478,
   0.5143517212137692
  ],
  "scored_days": 363,
  "skipped_days": {
   "incomplete_target": [
    "2025-10-26"
   ],
   "nonfinite_forecast": [
    "2025-10-27"
   ]
  },
  "days_won": 298,
  "days_lost": 65,
  "mae_mw": {
   "t0_cal": 1627.8,
   "blend_50": 3031.6,
   "t0": 1711.0,
   "rte_j1": 1322.4
  },
  "source": "eco2mix-national-cons-def",
  "coverage": 0.99989,
  "nature_counts": {
   "Données consolidées": 17520
  },
  "dry_run_2024": "https://github.com/xuanhuyle/solar/actions/runs/36144786834"
 }
]
```

### L8: Claim C1: one-shot confirmation on sealed 2025 data (t0 + holidays vs blend_50, consumption)

*Experiment:* C1 · *grade:* legacy · *verification:* audited · *source:* `{"ledger": "engine-ledger", "seq": 8, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed", "verification_basis": "the same result as C1-CONFIRMATION and L9 (audited); engine re-run L14 within 0.5% (gate L15)"}`

```json
{
 "claim_sha256": "8ed512e1863ca1b74f00c299c8bad15f52104bb8382cd046d504b759aefb8832",
 "commits": [
  "46bf8b0",
  "2a91197",
  "bf7ee94"
 ],
 "confirmations_jsonl_line": {
  "claim_id": "C1",
  "claim_sha256": "8ed512e1863ca1b74f00c299c8bad15f52104bb8382cd046d504b759aefb8832",
  "commit": "46bf8b0aeed8d36f6a46df451f8b54b3fe205fd5",
  "coverage": 0.99989,
  "days_lost": 65,
  "days_won": 298,
  "dry_run_2024": "https://github.com/xuanhuyle/solar/actions/runs/36144786834",
  "lower_bound_one_sided_95": 0.42020472600932396,
  "mae_mw": {
   "blend_50": 3031.6,
   "rte_j1": 1322.4,
   "t0": 1711.0,
   "t0_cal": 1627.8
  },
  "nature_counts": {
   "Données consolidées": 17520
  },
  "run": "https://github.com/xuanhuyle/solar/actions/runs/36145552543",
  "run_at": "2026-09-25T14:11:45+00:00",
  "run_number": 20,
  "scored_days": 363,
  "skill": 0.463059791566946,
  "skill_ci95": [
   0.4125771898812478,
   0.5143517212137692
  ],
  "skipped_days": {
   "incomplete_target": [
    "2025-10-26"
   ],
   "nonfinite_forecast": [
    "2025-10-27"
   ]
  },
  "source": "eco2mix-national-cons-def",
  "threshold": 0.25,
  "verdict": "CONFIRMED",
  "year": 2025
 },
 "confirmations_jsonl_line_sha256": "3e0dada2cc038e8fec10eaf67b4292ece02dc2b992dbed4de5ba8a1a75e0b463",
 "id": "C1",
 "runs": [
  "https://github.com/xuanhuyle/solar/actions/runs/36145552543",
  "https://github.com/xuanhuyle/solar/actions/runs/36144786834"
 ],
 "status": "LEGACY (as recorded before the engine existed)",
 "summary": "CONFIRMED: skill +46.3% [+41.3%, +51.4%], one-sided 95% lower bound +42.0% > 25%; RTE's own forecast still 23.1% better",
 "title": "Claim C1: one-shot confirmation on sealed 2025 data (t0 + holidays vs blend_50, consumption)"
}
```

### L9: Accepted finding C1 (the engine's 'accepted' comparator for consumption)

*Experiment:* C1 · *grade:* confirmed_on_sealed_data · *verification:* audited · *source:* `{"ledger": "engine-ledger", "seq": 9, "run_id": "36241906152", "code_commit": "f7d7a2475cebb908efa67e3322d1fe42565f62b9", "mode": "seed"}`

```json
{
 "arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "comparator": "best_simple (blend_50)",
 "confirmed_on": "2025 (sealed, one shot)",
 "finding_id": "C1",
 "lower_bound_one_sided_95": 0.4202,
 "metric": "mae",
 "note": "RTE's own day-ahead forecast (weather-driven) was still 23.1% better than this arm in 2025",
 "run": "https://github.com/xuanhuyle/solar/actions/runs/36145552543",
 "skill": 0.4631,
 "statement": "On French national electricity consumption, t0 with the public-holiday calendar reduces day-ahead MAE versus blend_50 by more than 25% over every buildable delivery day of 2025.",
 "target": "consumption"
}
```

### R-ENGINE-6: Knowledge engine v0

*Experiment:* ENGINE · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Knowledge engine v0"}`

````text
## Knowledge engine v0

An AI researcher proposes experiments; an independent referee runs them;
fresh, sealed data confirms or refutes the few claims worth betting on; and
everything is written to a tamper-evident ledger. Code in `engine/`, run by
`.github/workflows/engine.yml` (Actions → Engine → *mode*).

| Part | What it does | Where |
|---|---|---|
| **Ledger** | Append-only, hash-chained JSON lines on the `engine-ledger` branch. It records every research call, probe, rejection, gate, freeze, unseal and verdict, plus every change of referee code. Only the workflow's `record` job may write it; every run verifies the chain and prints its head hash | `engine/ledger.py`, `engine/record.py` |
| **Referee** | Owns the catalogue: targets, covariates, comparators, periods, the fixed t0 configuration. It checks every method live for leaks: post-origin data poisoned two ways must leave the forecast byte-identical, and a legal pre-origin change must move it. It gates each weather covariate on a known-answer test and caps the researcher at 200 evaluations | `engine/catalogue.py`, `engine/spec.py`, `engine/referee/` |
| **Vault** | Freezes up to 4 claims on one target per batch, each backed by a full, leak-checked exploratory result that tested exactly that claim. It confirms them only on forward data after a 14-day embargo, over 168 days (12 blocks of 14; a block counts with 10 days or more, and at least 10 blocks are needed), opened once, in a run you approve, and scored with the code of the commit the batch was frozen at. The verdict is a one-sided block t-test with Holm correction, with 0.05 spread over 4 batches | `engine/vault.py`, `engine/vault_run.py`, `engine/claims.py`, `engine/approvals.py` |
| **Researcher** | The Claude API, in its own job with the API key only: no data, no model token, no write access. It reads the ledger digest and answers with a declarative probe, a freeze or a stop, as schema-constrained JSON | `engine/researcher.py` |

**Data zones** (`engine/zones.py`, Europe/Paris local days):
- **Discovery:** 2022–2025, explored freely. 2025 was spent on C1, so it is explorable but never confirmable.
- **Forward (from 2026):** readable only through the vault.

`engine/data.py` is the single door to data, and a test pins it.

**Modes:**

| Mode | What it runs |
|---|---|
| `selftest` | Offline checks |
| `avail` | Coverage only, no skill |
| `seed` | Starts the ledger |
| `reproduce` | Reruns P4 and C1 through the declarative path |
| `gate` | Known-answer gates |
| `probe` | One spec, given in `spec_json` |
| `loop` | The AI researcher, `max_iterations` at a time |
| `freeze` | Freezes a claim batch |
| `vault_dryrun` | A rehearsal on consumed 2025 data |
| `vault` | Opens a matured batch; needs your approval |

**Measured on Actions so far:**
- **Seed:** the ledger was seeded with Exp 0, the covariate slice, P1–P4 and C1; C1 became the first accepted finding.
- **Reproduction:** the declarative path reproduces P4 on 2024 (+49.5% vs +49.6%) and C1 on 2025 (+46.2% vs +46.3%) within 0.5%.
- **Known-answer gates:**
  - **Solar and radiation: PASS.** The planted signal cuts error by 35%, noise changes it by +2%, and a one-hour shift costs 7.6%.
  - **Consumption and temperature: FAIL on the frozen noise rule.** The pipeline is aligned (a shift costs 2.9%) and t0 uses the signal (−8.6%). But pure noise made t0 5.2% worse, against a frozen limit of 5%. Temperature therefore stays locked for discovery; the rule was not moved after the fact.
  - **The first offline run of the gate caught a real misalignment:** temperature is an instantaneous reading, not an hourly mean. It is now mapped as such.
  - **Re-gate under rules `ka/2`** (your decision, 2026-09-26, declared in code and in the ledger before the run): the noise limit is widened to 10%, since the noise rule guards against a broken pipeline and t0's sensitivity to noise only biases results against a covariate. Every other threshold is unchanged. The gate runs once more, on 64 days it has never seen (2024-11-05..2025-01-07). A gate result now counts only under the current rules and the current covariate code: it stores a fingerprint of that code.
  - **Re-gate result** ([run](https://github.com/xuanhuyle/solar/actions/runs/36274540155), ledger seqs 24–26; the rule change was recorded first):
    - **Consumption and temperature: PASS.** The planted signal cuts error by 22.6%, noise changes it by +0.13%, and a one-hour shift costs 4.6%. On this period noise would have passed the old 5% limit too: the new period, not the wider rule, made the difference.
    - **Solar and radiation: PASS** again. Planted −40.9%, noise −0.17%, shift +12.6%.
    - Temperature is now usable for discovery on consumption.
- **Vault rehearsal** (`vault_dryrun`, consumed 2025 data, labelled NON-CONFIRMATORY):
  - **What it caught:** the first run found that one missing day in the 84 cost a whole 14-day block, which forced p := 1. Blocks are now calendar spans that need 10 of their 14 days.
  - **Rerun, C1's claim** (t0 + holiday vs `blend_50`, margin 20%): skill +38.9%, p 0.016, Holm 0.032, **NOT PASS** at α 0.0125.
  - **Rerun, bridge days vs the accepted arm:** −2.1%, **NOT PASS**.
  - **What it means:** 84 days (6 blocks) and a quarter of the error budget were too strict. A C1-sized effect would pass a 20% margin only about half the time. With 168 days (12 blocks, your choice), the expected t is 4.2 against a critical 2.6. The first verdict comes about six months after a freeze.
  - **Rerun on the hardened code with the 168-day window** ([run](https://github.com/xuanhuyle/solar/actions/runs/36275944910), ledger seqs 30–34). The evidence probes ran first and were recorded, then a batch citing them was frozen as of 2025-01-01. It was scored on 2025-01-16..2025-07-02, with every arm and comparator leak-checked live:
    - **C1's claim** (margin 20%): skill +43.5%, 12 of 12 blocks, t 4.80, Holm p 0.0005, **PASS**.
    - **Bridge days vs the accepted arm:** −0.1%, **NOT PASS**. This claim is the control: its 2024 evidence was already negative (−5.1% [−7.8%, −2.1%]).
    - **Reproduction after the day-rounding fix:** P4 is unchanged (1,571.0 vs 3,114.4 MW, +49.6%), and C1 is +46.2% vs the recorded +46.3% ([run](https://github.com/xuanhuyle/solar/actions/runs/36275347257)).

- **After the three fix rounds** (commits `0f820f1` and `de7867b`, with no caches and fresh downloads; ledger seqs 35–48, chain verified):
  - **Gates, under the new fingerprint:** both PASS again ([run](https://github.com/xuanhuyle/solar/actions/runs/36339337505)). Planted and shift numbers are identical; the noise ratio is 1.013.
  - **Reproduction:** P4 is +49.6% and C1 +46.2%, as before ([run](https://github.com/xuanhuyle/solar/actions/runs/36340111693)). Its submissions are now recorded too.
  - **Rehearsal:** C1's claim PASS (t 4.80) and the control NOT PASS ([run](https://github.com/xuanhuyle/solar/actions/runs/36340931603)). The frozen batch cites exactly the right evidence seqs.
- **First live researcher loop, 2026-09-28** (three iterations, [1](https://github.com/xuanhuyle/solar/actions/runs/36404992761) · [2](https://github.com/xuanhuyle/solar/actions/runs/36407411106) · [3](https://github.com/xuanhuyle/solar/actions/runs/36408833613); ledger seqs 49–56, chain verified). An earlier attempt had stopped at its guard because the API settings were not yet set.
  - **Iteration 1.** The researcher reasoned that temperature is the missing driver, since RTE's weather-driven forecast beats C1. It probed three temperature encodings on top of holidays against the accepted C1 arm, over 602 days (2024-05 to 2025-12, all leak checks passed):
    - raw temperature: **+19.3% [+14.9%, +23.7%]**, 1,199 vs 1,485 MW, 390 days won and 212 lost;
    - heating degree-days: +13.1% [+8.0%, +17.3%];
    - heating and cooling degree-days: +11.7% [+6.2%, +16.9%].
  - **Iteration 2.** Before freezing, it checked that the gain holds in summer, when heating demand is absent: **+11.1% [+4.0%, +17.4%]** vs C1 over 302 days, and +19.3% vs plain t0.
  - **Iteration 3: it froze batch B1**, one claim: *t0 + holidays + raw temperature beats the accepted C1 arm over the forward window*, with margin 0 and evidence seq 51. It noted its own caveat: 2024 and 2025 were not checked separately.
    - The forward window is 2026-10-13..2027-03-29, with α 0.0125.
    - It opens after 2027-04-01, in a run you approve.
    - It is scored at the pinned freeze commit, tag `engine-freeze/B1`.
    - This is EXPLORATORY evidence only until then.
  - **Cost:** three API calls, one per iteration, with no repair or retry. About 30k input tokens plus 12k written to the prompt cache, and 4.1k output tokens in total.
- **Second loop, the owner's question: "how does the temperature model compare with RTE's own forecast?"** (2026-09-28; [1](https://github.com/xuanhuyle/solar/actions/runs/36415871063) · [2](https://github.com/xuanhuyle/solar/actions/runs/36418336095) · [3](https://github.com/xuanhuyle/solar/actions/runs/36419163633); ledger seqs 57–66, chain verified).
  - **How it was asked:** the question went in through the new `question` input. The researcher planned all year, then winter, then summer. Its notes reported the all-year result in iteration 2 and the winter result in iteration 3. The summer result arrived after the last call, so the summer figures come straight from the referee's probe result (seq 66).
  - **Scope:** all days are those of 2024-05 to 2025-12, compared on the same days, with every leak check passed. RTE is a reference only (its issue time is not verified), so none of this can back a claim.

  | Season (days) | t0 + holidays + raw temperature (the B1 arm) vs RTE | MAE (MW) |
  |---|---|---|
  | All year (602) | +7.6% [−2.7%, +16.0%]: level, not a clear win | 1,199 vs 1,298 |
  | Winter, Nov–Mar (210) | **−26.2% [−41.8%, −12.3%]: RTE clearly better** | 1,731 vs 1,372 |
  | Summer, May–Sep (302) | **+30.6% [+21.9%, +37.7%]: clearly better than RTE** | 864 vs 1,245 |

  - **Degree-day encodings:** they are never better than raw temperature, and none narrows the winter gap. All year: heating degree-days +0.5%, heating and cooling −1.1%. Winter: −26.6% and −37.6%. Summer: +18.1% and +22.9%.
  - **Cost:** three calls, no repair or retry. About 36k input tokens, 12k written to the prompt cache and 3.2k output tokens.
  - **Open question for B1:** B1's window (Oct–Mar) is mostly winter, but at this point the arm had been compared with C1 only all year and in summer. The third loop answers this.
- **Third loop, the owner's question: "how does the B1 model compare with C1 in winter?"** (2026-09-28; [1](https://github.com/xuanhuyle/solar/actions/runs/36428879883) · [2](https://github.com/xuanhuyle/solar/actions/runs/36430372130); ledger seqs 67–70, chain verified).
  - **Why:** B1's forward window, 2026-10-13..2027-03-29, is mostly winter.
  - **Method:** one probe, scope winter (Nov–Mar), period `ALL`. That builds 604 winter days from 2022, but the temperature forecasts start in May 2024, so both comparisons are scored on the 210 days 2024-11-01..2025-12-29. C1 was forecast on all 604 days; its error in the table is on those same 210. Every leak check passed.
    - In round 1 the researcher compared the B1 arm and the heating-degree arm with the accepted C1 arm. It dropped heating plus cooling because cooling degrees are almost always zero in winter.
    - In round 2 it read the result and stopped.

  | Winter, 210 days | vs C1 (t0 + holidays) [95% CI] | MAE (MW) | Days won / lost |
  |---|---|---|---|
  | **B1 arm** (t0 + holidays + raw temperature) | **+24.4% [+19.0%, +30.7%]** | 1,731 vs 2,289 | 155 / 55 |
  | Heating degree-days instead of raw temperature | +24.1% [+18.3%, +29.7%] | 1,737 vs 2,289 | 156 / 54 |

  - **Winter is where temperature helps most against C1.** All year +19.3%, summer +11.1%, winter +24.4%.
  - **Both winters show the gain.** Split from the recorded per-day errors, not by the referee and with no CI: Nov 2024–Mar 2025 (151 days) about +23%, and Nov–Dec 2025 (59 days) about +28%.
  - **Heating degree-days tie raw temperature.** Their CIs overlap almost entirely, so they are no better against C1 in winter.
  - **Winter against RTE is a separate question.** Both arms still trail RTE's own forecast by about 26% (second loop).
  - **This is exploratory only.** B1 was chosen after looking at these data (2024–2025), so this is a hint about the forward test, not a forecast of its verdict. The vault uses a different window (it adds late October), its own block t-test and α 0.0125.
  - **Cost:** two calls, no repair or retry. About 29k input tokens, 8k written to the prompt cache and 1.7k output tokens.

**Hardened after an independent adversarial review** (2026-09-26; 1 critical, 11 major and 26 minor findings, none of which had touched sealed data):
- **Vault:**
  - A frozen batch now matches its own hash. Before, no batch frozen from the command line could ever have been opened.
  - A crash after the unseal still closes the batch with a VOID verdict, so it can never lock the engine.
  - An unscorable claim stays in the Holm family at p = 1.
  - Skill is measured on the days both methods scored.
  - Every arm and comparator is leak-checked live on the forward window.
  - A freeze is refused if:
    - it uses a weather covariate without a current gate;
    - it uses `accepted` when nothing is accepted;
    - the cited evidence tested something else;
    - its scope could never fill the window.
- **Record:**
  - The record job accepts only the entry kinds each mode may produce.
  - It stamps its own run identity and skips entries already on the ledger, so a re-run is safe.
  - It refuses a freeze or unseal decided against an older ledger head.
  - One engine run at a time; a ledger fetch failure is fatal.
- **Discovery:**
  - A recorded result is re-used only if it is full, leak-checked, and was made by the same referee code against the same accepted arm.
  - A period no longer loses its last local day: reads ask for one extra UTC day and trim locally. Reads still round inward at the forward boundary and in the vault.
  - Rows are checked under a vault access too.
  - The door test also catches aliased imports.
- **Referee:**
  - The leak check has a weather positive control: a legal forecast change must move a weather arm.
  - It computes issue bounds itself.
- **Researcher:**
  - Every call is recorded the moment it returns, even if the job then crashes, with its full prompt and response.
  - A malformed freeze gets the vault's own structural check and one repair.
  - `anthropic` is pinned exactly.

**Second, independent fix-check** (2026-09-27; 46 agents; 34 confirmed gaps, all but the disclosed ones fixed):
- **The loop could only run one round.** The chain job had no status function while an upstream job was skipped, so the loop would have stopped after its first round.
- **The record job silently dropped repeated entries.** It de-duplicated across runs, and had already dropped the reproduce run's two submissions. It now skips only its own run's earlier records.
- **The record job now:**
  - reads only the pending file whose sha256 its producing job declared;
  - refuses a freeze only when the state it rested on moved;
  - always records a real unseal;
  - requires output from every producing run.
- **Researcher:**
  - Each API call has a hard 8-minute timeout, with no hidden retries.
  - A submission is on disk before its probe runs.
  - A freeze proposal gets the vault's full ledger checks in the research job, so a bad citation gets its repair.
  - The digest shows which results a freeze may cite.
- **Vault and findings:**
  - A batch is scored at its freeze commit (your decision).
  - Evidence for an `accepted` claim must have been measured against the arm `accepted` means now.
  - A new arm becomes the accepted comparator only if it was confirmed against the current one.
  - A weather read failure fails only the claims that need weather.
- **Gate fingerprint:** now also covers the code that hands covariates to t0 and the t0 revision.
- **Discovery:** reads run one day past the scored end, so weather arms keep their last day.

**Third round** (the adversarial re-check; 23 of the 34 items fixed, 12 new findings confirmed, all addressed):
- **The engine reads no cache at all.** Discovery data, the t0 weights (pinned revision) and packages are downloaded fresh on every run:
  - a cache is writable by any job holding the runtime token;
  - entries are evicted after 7 idle days;
  - the model loader trusts a cached snapshot without a hash check.
  A planted cache could otherwise have become evidence, or even a vault verdict. The final verify reproduced the model case offline.
- **Losses and crashes:**
  - A missing research record now fails the record job.
  - Transient API errors (rate limits, overload) are retried at most twice, each attempt recorded.
  - An unexpected error still records the billed call.
  - Malformed or unstorable input (huge numbers, lone surrogates) is recorded as a rejection instead of crashing.
- **A missing RTE forecast costs only its own rows.**
- **Freeze commits are tagged.** Every recorded freeze's commit is pinned as tag `engine-freeze/<batch>`, so the vault can always fetch the code it must score with.
- **The ledger's schema is pinned by each open batch.** A change is refused on the first run after it, not months later at the vault.
- **Config entries list files only when they match their own fingerprint.**

**Known limits of the engine:**
- **Never delete or move the `engine-freeze/*` tags.** A tag ruleset that blocks deleting and updating them, like the one recommended for `engine-ledger`, makes this a guarantee.
- **The ledger's kinds and context fields may not change while a batch is open.** The record job refuses; revert, or wait until the batch has been opened.
- **Do not dispatch an engine run while a researcher loop is running.** Engine runs share one queue, and a newer dispatch cancels an engine run that is waiting. To resume a loop that was cut short, dispatch `loop` with the next iteration number.
- **If the record job fails after a vault run, re-run that record job before anything else.** Until then the unseal exists only in the run's artifact.
- **The gate's `aligned` check cannot detect a wrong time convention.** The conventions come from Open-Meteo's documentation: temperature is instantaneous, and radiation is the mean over the preceding hour. The positive control and the ±1 h shift are the practical guard.
- **The rehearsal reads one day beyond the window; the vault does not.** The vault never reads past its window, so a real window scores at most one day fewer.
- **Approvals are per run, not per attempt:** a re-run attempt of an approved vault run is not asked again. GitHub itself gates each run.
- **Force-pushes to `engine-ledger`:** only the printed head hash would reveal them. A branch ruleset that blocks force-push and deletion on `engine-ledger` closes this gap (a one-minute setting).
- **Origin slot:** the target slot stamped at the origin is treated as known at the origin, as in Exp 0 and C1. It covers origin ± 15 minutes.
- **Researcher dependencies:** transitive dependencies are resolved by pip at install time, without hashes.

**One-time setup** (repository Settings):
- **Secret** `ANTHROPIC_API_KEY`, with a spend limit set in the Anthropic Console.
- **Variable** `RESEARCHER_MODEL`; optional `RESEARCHER_EFFORT` and `RESEARCHER_TOKEN_CAP`.
- **Environment** `engine-vault`, with you as required reviewer and deployments allowed only from this branch.

**Deliberately deferred**, compared with the design documents' referee subset:
- real-data leak trials at scale;
- receipt invariance;
- a tamper/canary campaign;
- cross-runner tolerance;
- placebo checks;
- the forward recorder;
- a scripted exhaustive screen;
- sandboxing (not needed while specs are declarative);
- signed evidence packages;
- certification.
````

### L12: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 12, "run_id": "36242331280", "code_commit": "cd821be7dd50a970b0e937345c09760b2fc416b9", "mode": "reproduce"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "Y2024",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": null,
 "accepted_arm": null,
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    }
   ],
   "name": "t0_cal"
  },
  {
   "covariates": [],
   "name": "t0_plain"
  }
 ],
 "builds_on": [],
 "rationale": "referee self-check: reproduce P4_2024 through the declarative path",
 "submitted_by": "referee:reproduction",
 "eligible_days": {
  "best_simple": 364,
  "rte_j1": 364,
  "t0_cal": 364,
  "t0_plain": 364
 },
 "comparisons": [
  {
   "arm": "t0_cal",
   "vs": "best_simple",
   "days": 363,
   "skill": 0.495156,
   "ci95": [
    0.445204,
    0.550892
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1570.023,
   "mae_vs": 3109.914,
   "days_won": 300,
   "days_lost": 63
  },
  {
   "arm": "t0_plain",
   "vs": "best_simple",
   "days": 363,
   "skill": 0.472338,
   "ci95": [
    0.425232,
    0.537788
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1640.982,
   "mae_vs": 3109.914,
   "days_won": 303,
   "days_lost": 60
  },
  {
   "arm": "t0_cal",
   "vs": "rte_j1",
   "days": 364,
   "skill": -0.151847,
   "ci95": [
    -0.288875,
    -0.023435
   ],
   "p_one_sided": 0.986507,
   "mae_arm": 1571.91,
   "mae_vs": 1364.686,
   "days_won": 198,
   "days_lost": 166,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L14: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 14, "run_id": "36242331280", "code_commit": "cd821be7dd50a970b0e937345c09760b2fc416b9", "mode": "reproduce"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "Y2025c",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": null,
 "accepted_arm": null,
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    }
   ],
   "name": "t0_cal"
  },
  {
   "covariates": [],
   "name": "t0_plain"
  }
 ],
 "builds_on": [],
 "rationale": "referee self-check: reproduce C1_2025 through the declarative path",
 "submitted_by": "referee:reproduction",
 "eligible_days": {
  "best_simple": 363,
  "rte_j1": 363,
  "t0_cal": 363,
  "t0_plain": 363
 },
 "comparisons": [
  {
   "arm": "t0_cal",
   "vs": "best_simple",
   "days": 362,
   "skill": 0.462367,
   "ci95": [
    0.413313,
    0.514826
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1629.116,
   "mae_vs": 3030.162,
   "days_won": 297,
   "days_lost": 65
  },
  {
   "arm": "t0_plain",
   "vs": "best_simple",
   "days": 362,
   "skill": 0.436594,
   "ci95": [
    0.394761,
    0.491431
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1707.212,
   "mae_vs": 3030.162,
   "days_won": 285,
   "days_lost": 77
  },
  {
   "arm": "t0_cal",
   "vs": "rte_j1",
   "days": 363,
   "skill": -0.231353,
   "ci95": [
    -0.400717,
    -0.055069
   ],
   "p_one_sided": 0.997501,
   "mae_arm": 1634.728,
   "mae_vs": 1327.586,
   "days_won": 180,
   "days_lost": 183,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L15: Reproduction check

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 15, "run_id": "36242331280", "code_commit": "cd821be7dd50a970b0e937345c09760b2fc416b9", "mode": "reproduce"}`

```json
{
 "checks": {
  "C1_2025": {
   "days": [
    362,
    362,
    363
   ],
   "mae_got": {
    "best_simple": 3030.162,
    "rte_j1": 1327.586,
    "t0_cal": 1634.728,
    "t0_plain": 1707.212
   },
   "mae_recorded": {
    "best_simple": 3031.6,
    "rte_j1": 1322.4,
    "t0_cal": 1627.8,
    "t0_plain": 1711.0
   },
   "pass": true,
   "relative_diff": {
    "best_simple": -0.00047,
    "rte_j1": 0.00392,
    "t0_cal": 0.00426,
    "t0_plain": -0.00221
   },
   "skill_got": 0.462367,
   "skill_recorded": 0.463
  },
  "P4_2024": {
   "days": [
    363,
    363,
    364
   ],
   "mae_got": {
    "best_simple": 3109.914,
    "rte_j1": 1364.686,
    "t0_cal": 1571.91,
    "t0_plain": 1640.982
   },
   "mae_recorded": {
    "best_simple": 3114.4,
    "rte_j1": 1368.2,
    "t0_cal": 1571.0,
    "t0_plain": 1644.4
   },
   "pass": true,
   "relative_diff": {
    "best_simple": -0.00144,
    "rte_j1": -0.00257,
    "t0_cal": 0.00058,
    "t0_plain": -0.00208
   },
   "skill_got": 0.495156,
   "skill_recorded": 0.496
  }
 },
 "gate": "reproduction",
 "limit_days": null,
 "pass": true,
 "tolerance": "0.5% MAE, 0.5 pp skill"
}
```

### L17: Known-answer gate consumption/wx_temperature under ka/1: FAIL

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 17, "run_id": "36242852442", "code_commit": "616799a6154d224b19aadb890e6bb9e977339406", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": false,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "instant",
 "covariate": "wx_temperature",
 "days": 62,
 "decoy_ratio": 1.0521,
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 981.92,
  "ka_oracle_planted": 853.2,
  "ka_oracle_shift_m1h": 879.34,
  "ka_oracle_shift_p1h": 877.75,
  "t0_base": 933.26
 },
 "pass": false,
 "period": [
  "2024-09-02",
  "2024-11-04"
 ],
 "planted_ratio": 0.9142,
 "rules": {
  "decoy_ratio_max": 1.05,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01
 },
 "shift_penalty": 1.0288,
 "target": "consumption"
}
```

### L18: Known-answer gate solar/wx_radiation under ka/1: PASS

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 18, "run_id": "36242852442", "code_commit": "616799a6154d224b19aadb890e6bb9e977339406", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": true,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "mean_preceding_hour",
 "covariate": "wx_radiation",
 "days": 62,
 "decoy_ratio": 1.0213,
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 890.49,
  "ka_oracle_planted": 567.34,
  "ka_oracle_shift_m1h": 610.17,
  "ka_oracle_shift_p1h": 695.71,
  "t0_base": 871.95
 },
 "pass": true,
 "period": [
  "2024-09-02",
  "2024-11-04"
 ],
 "planted_ratio": 0.6507,
 "rules": {
  "decoy_ratio_max": 1.05,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01
 },
 "shift_penalty": 1.0755,
 "target": "solar"
}
```

### L20: Vault rehearsal on consumed 2025 data (NON-CONFIRMATORY)

*Experiment:* ENGINE · *grade:* rehearsal · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 20, "run_id": "36243485653", "code_commit": "f9426a149879e4150f8b831701a0101af534e865", "mode": "vault_dryrun"}`

```json
{
 "vault_dryrun": {
  "alpha": 0.0125,
  "batch_id": "DRY",
  "batch_sha256": "736b920884650a8710184d0d09b448413ad9894f71f341260c01621406bc51f0",
  "claims": [
   {
    "blocks": 5,
    "claim": "C1",
    "delta": 0.2,
    "p": 1.0,
    "p_holm": 1.0,
    "skill": 0.388734,
    "t": null,
    "verdict": "NOT PASS"
   },
   {
    "blocks": 5,
    "claim": "C2",
    "delta": 0.0,
    "p": 1.0,
    "p_holm": 1.0,
    "skill": -0.021026,
    "t": null,
    "verdict": "NOT PASS"
   }
  ],
  "sources": {
   "consumption": {
    "chosen": "eco2mix-national-cons-def",
    "coverage": {
     "eco2mix-national-cons-def": 0.98908
    }
   }
  },
  "status": "NON-CONFIRMATORY dry run on consumed data - not a verdict",
  "window": [
   "2025-01-16",
   "2025-04-09"
  ]
 },
 "batch_claims": [
  {
   "arm": {
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "best_simple",
   "delta": 0.2,
   "evidence": [
    14
   ],
   "id": "C1",
   "metric": "mae",
   "scope": "all",
   "statement": "t0 + holiday beats blend_50 by more than 20% (C1 replayed)",
   "target": "consumption"
  },
  {
   "arm": {
    "covariates": [
     {
      "id": "bridge_day",
      "transform": "raw"
     },
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "accepted",
   "delta": 0.0,
   "evidence": [
    14
   ],
   "id": "C2",
   "metric": "mae",
   "scope": "all",
   "statement": "adding bridge days beats the accepted arm (any margin)",
   "target": "consumption"
  }
 ],
 "batch_window": [
  "2025-01-16",
  "2025-04-09"
 ]
}
```

### L22: Vault rehearsal on consumed 2025 data (NON-CONFIRMATORY)

*Experiment:* ENGINE · *grade:* rehearsal · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 22, "run_id": "36243840001", "code_commit": "ba130fae9086b739a9d68ae8b44e05316b936e2e", "mode": "vault_dryrun"}`

```json
{
 "vault_dryrun": {
  "alpha": 0.0125,
  "batch_id": "DRY",
  "batch_sha256": "4d09af461b31fe51e6eeadd45692b020b55794ab06f8982950214f051377da2b",
  "claims": [
   {
    "blocks": 6,
    "claim": "C1",
    "delta": 0.2,
    "p": 0.01609959305414995,
    "p_holm": 0.03219919,
    "skill": 0.388734,
    "t": 2.94154,
    "verdict": "NOT PASS"
   },
   {
    "blocks": 6,
    "claim": "C2",
    "delta": 0.0,
    "p": 0.9858532729305901,
    "p_holm": 0.98585327,
    "skill": -0.021026,
    "t": -3.054045,
    "verdict": "NOT PASS"
   }
  ],
  "sources": {
   "consumption": {
    "chosen": "eco2mix-national-cons-def",
    "coverage": {
     "eco2mix-national-cons-def": 0.98908
    }
   }
  },
  "status": "NON-CONFIRMATORY dry run on consumed data - not a verdict",
  "window": [
   "2025-01-16",
   "2025-04-09"
  ]
 },
 "batch_claims": [
  {
   "arm": {
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "best_simple",
   "delta": 0.2,
   "evidence": [
    14
   ],
   "id": "C1",
   "metric": "mae",
   "scope": "all",
   "statement": "t0 + holiday beats blend_50 by more than 20% (C1 replayed)",
   "target": "consumption"
  },
  {
   "arm": {
    "covariates": [
     {
      "id": "bridge_day",
      "transform": "raw"
     },
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "accepted",
   "delta": 0.0,
   "evidence": [
    14
   ],
   "id": "C2",
   "metric": "mae",
   "scope": "all",
   "statement": "adding bridge days beats the accepted arm (any margin)",
   "target": "consumption"
  }
 ],
 "batch_window": [
  "2025-01-16",
  "2025-04-09"
 ]
}
```

### L24: Known-answer rule change ka/1 -> ka/2 (owner decision)

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 24, "run_id": "36274540155", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "gate"}`

```json
{
 "period": [
  "2024-11-05",
  "2025-01-07"
 ],
 "rule_change": {
  "changed": {
   "decoy_ratio_max": [
    1.05,
    1.1
   ],
   "period": [
    [
     "2024-09-02",
     "2024-11-04"
    ],
    [
     "2024-11-05",
     "2025-01-07"
    ]
   ]
  },
  "decided": "owner, 2026-09-26, after ka/1 failed consumption/wx_temperature on the noise rule only",
  "from": "ka/1",
  "reason": "the noise rule guards against a broken pipeline; t0's sensitivity to a junk covariate only biases results against the covariate, so it cannot create false findings",
  "to": "ka/2"
 },
 "rules": {
  "decoy_ratio_max": 1.1,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01,
  "version": "ka/2"
 }
}
```

### L25: Known-answer gate consumption/wx_temperature under ka/2: PASS

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 25, "run_id": "36274540155", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": true,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "instant",
 "covariate": "wx_temperature",
 "days": 64,
 "decoy_ratio": 1.0013,
 "fingerprint": "407ffdc757e8b2318d9e45ca44fc04c2224165e336a572acc0ce48cd724847c0",
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 2798.42,
  "ka_oracle_planted": 2162.36,
  "ka_oracle_shift_m1h": 2261.03,
  "ka_oracle_shift_p1h": 2275.83,
  "t0_base": 2794.69
 },
 "pass": true,
 "period": [
  "2024-11-05",
  "2025-01-07"
 ],
 "planted_ratio": 0.7737,
 "rules": {
  "decoy_ratio_max": 1.1,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01,
  "version": "ka/2"
 },
 "rules_version": "ka/2",
 "shift_penalty": 1.0456,
 "target": "consumption"
}
```

### L26: Known-answer gate solar/wx_radiation under ka/2: PASS

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 26, "run_id": "36274540155", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": true,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "mean_preceding_hour",
 "covariate": "wx_radiation",
 "days": 64,
 "decoy_ratio": 0.9983,
 "fingerprint": "407ffdc757e8b2318d9e45ca44fc04c2224165e336a572acc0ce48cd724847c0",
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 384.67,
  "ka_oracle_planted": 227.84,
  "ka_oracle_shift_m1h": 256.59,
  "ka_oracle_shift_p1h": 277.63,
  "t0_base": 385.32
 },
 "pass": true,
 "period": [
  "2024-11-05",
  "2025-01-07"
 ],
 "planted_ratio": 0.5913,
 "rules": {
  "decoy_ratio_max": 1.1,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01,
  "version": "ka/2"
 },
 "rules_version": "ka/2",
 "shift_penalty": 1.1262,
 "target": "solar"
}
```

### L27: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 27, "run_id": "36275347257", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "reproduce"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "Y2024",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    }
   ],
   "name": "t0_cal"
  },
  {
   "covariates": [],
   "name": "t0_plain"
  }
 ],
 "builds_on": [],
 "rationale": "referee self-check: reproduce P4_2024 through the declarative path",
 "submitted_by": "referee:reproduction",
 "eligible_days": {
  "best_simple": 365,
  "rte_j1": 365,
  "t0_cal": 365,
  "t0_plain": 365
 },
 "comparisons": [
  {
   "arm": "t0_cal",
   "vs": "best_simple",
   "days": 364,
   "skill": 0.495583,
   "ci95": [
    0.442319,
    0.550657
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1570.955,
   "mae_vs": 3114.4,
   "days_won": 301,
   "days_lost": 63
  },
  {
   "arm": "t0_plain",
   "vs": "best_simple",
   "days": 364,
   "skill": 0.472005,
   "ci95": [
    0.422345,
    0.536041
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1644.388,
   "mae_vs": 3114.4,
   "days_won": 304,
   "days_lost": 60
  },
  {
   "arm": "t0_cal",
   "vs": "rte_j1",
   "days": 365,
   "skill": -0.151452,
   "ci95": [
    -0.292543,
    -0.022711
   ],
   "p_one_sided": 0.990005,
   "mae_arm": 1572.835,
   "mae_vs": 1365.958,
   "days_won": 198,
   "days_lost": 167,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L28: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 28, "run_id": "36275347257", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "reproduce"}`

```json
{
 "identical_numbers_to": "L14",
 "note": "a repeat run (after a code change) that reproduced the same numbers",
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 }
}
```

### L29: Reproduction check

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 29, "run_id": "36275347257", "code_commit": "8af2f9cf2346bd5c3dc733d28da9561e80ba9aed", "mode": "reproduce"}`

```json
{
 "checks": {
  "C1_2025": {
   "days": [
    362,
    362,
    363
   ],
   "mae_got": {
    "best_simple": 3030.162,
    "rte_j1": 1327.586,
    "t0_cal": 1634.728,
    "t0_plain": 1707.212
   },
   "mae_recorded": {
    "best_simple": 3031.6,
    "rte_j1": 1322.4,
    "t0_cal": 1627.8,
    "t0_plain": 1711.0
   },
   "pass": true,
   "relative_diff": {
    "best_simple": -0.00047,
    "rte_j1": 0.00392,
    "t0_cal": 0.00426,
    "t0_plain": -0.00221
   },
   "skill_got": 0.462367,
   "skill_recorded": 0.463
  },
  "P4_2024": {
   "days": [
    364,
    364,
    365
   ],
   "mae_got": {
    "best_simple": 3114.4,
    "rte_j1": 1365.958,
    "t0_cal": 1572.835,
    "t0_plain": 1644.388
   },
   "mae_recorded": {
    "best_simple": 3114.4,
    "rte_j1": 1368.2,
    "t0_cal": 1571.0,
    "t0_plain": 1644.4
   },
   "pass": true,
   "relative_diff": {
    "best_simple": 0.0,
    "rte_j1": -0.00164,
    "t0_cal": 0.00117,
    "t0_plain": -1e-05
   },
   "skill_got": 0.495583,
   "skill_recorded": 0.496
  }
 },
 "gate": "reproduction",
 "limit_days": null,
 "pass": true,
 "tolerance": "0.5% MAE, 0.5 pp skill"
}
```

### L31: Evidence probe run during a vault rehearsal

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 31, "run_id": "36275944910", "code_commit": "8f9add8ce6c8a9e76de9a22917ae4f7025b4f9f7", "mode": "vault_dryrun"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "Y2024",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    }
   ],
   "name": "t0_cal"
  }
 ],
 "builds_on": [],
 "rationale": "evidence for the vault rehearsal",
 "submitted_by": "referee:rehearsal-evidence",
 "eligible_days": {
  "best_simple": 365,
  "t0_cal": 365
 },
 "comparisons": [
  {
   "arm": "t0_cal",
   "vs": "best_simple",
   "days": 364,
   "skill": 0.495583,
   "ci95": [
    0.442319,
    0.550657
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1570.955,
   "mae_vs": 3114.4,
   "days_won": 301,
   "days_lost": 63
  }
 ]
}
```

### L33: Evidence probe run during a vault rehearsal

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 33, "run_id": "36275944910", "code_commit": "8f9add8ce6c8a9e76de9a22917ae4f7025b4f9f7", "mode": "vault_dryrun"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "Y2024",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "bridge_day",
     "transform": "raw"
    },
    {
     "id": "holiday",
     "transform": "raw"
    }
   ],
   "name": "t0_bridge"
  }
 ],
 "builds_on": [],
 "rationale": "evidence for the vault rehearsal",
 "submitted_by": "referee:rehearsal-evidence",
 "eligible_days": {
  "accepted": 365,
  "t0_bridge": 365
 },
 "comparisons": [
  {
   "arm": "t0_bridge",
   "vs": "accepted",
   "days": 365,
   "skill": -0.050939,
   "ci95": [
    -0.077786,
    -0.021219
   ],
   "p_one_sided": 1.0,
   "mae_arm": 1652.953,
   "mae_vs": 1572.835,
   "days_won": 149,
   "days_lost": 216
  }
 ]
}
```

### L34: Vault rehearsal on consumed 2025 data (NON-CONFIRMATORY)

*Experiment:* ENGINE · *grade:* rehearsal · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 34, "run_id": "36275944910", "code_commit": "8f9add8ce6c8a9e76de9a22917ae4f7025b4f9f7", "mode": "vault_dryrun"}`

```json
{
 "vault_dryrun": {
  "alpha": 0.0125,
  "batch_id": "DRY",
  "batch_sha256": "96ee79c9a98c973be86b2589ef8d7507a5d9b2338518a2083342cac9935c60b8",
  "claims": [
   {
    "blocks": 12,
    "claim": "C1",
    "delta": 0.2,
    "p": 0.00027459634587323906,
    "p_holm": 0.00054919,
    "skill": 0.435381,
    "t": 4.804695,
    "verdict": "PASS"
   },
   {
    "blocks": 12,
    "claim": "C2",
    "delta": 0.0,
    "p": 0.5198144054059679,
    "p_holm": 0.51981441,
    "skill": -0.001374,
    "t": -0.050831,
    "verdict": "NOT PASS"
   }
  ],
  "leak_checks": {
   "C1:arm": {
    "pass": true
   },
   "C1:ref": {
    "pass": true
   },
   "C2:arm": {
    "pass": true
   },
   "C2:ref": {
    "pass": true
   }
  },
  "sources": {
   "consumption": {
    "chosen": "eco2mix-national-cons-def",
    "coverage": {
     "eco2mix-national-cons-def": 1.0
    }
   }
  },
  "status": "NON-CONFIRMATORY dry run on consumed data - not a verdict",
  "window": [
   "2025-01-16",
   "2025-07-02"
  ]
 },
 "batch_claims": [
  {
   "arm": {
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "best_simple",
   "delta": 0.2,
   "evidence": [
    31
   ],
   "id": "C1",
   "metric": "mae",
   "scope": "all",
   "statement": "t0 + holiday beats blend_50 by more than 20% (C1 replayed)",
   "target": "consumption"
  },
  {
   "arm": {
    "covariates": [
     {
      "id": "bridge_day",
      "transform": "raw"
     },
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "accepted",
   "delta": 0.0,
   "evidence": [
    33
   ],
   "id": "C2",
   "metric": "mae",
   "scope": "all",
   "statement": "adding bridge days beats the accepted arm (any margin)",
   "target": "consumption"
  }
 ],
 "batch_window": [
  "2025-01-16",
  "2025-07-02"
 ]
}
```

### L36: Known-answer gate consumption/wx_temperature under ka/2: PASS

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 36, "run_id": "36339337505", "code_commit": "0f820f1e1b460d680ab26a319aa66afeaaac9a08", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": true,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "instant",
 "covariate": "wx_temperature",
 "days": 64,
 "decoy_ratio": 1.0132,
 "fingerprint": "b2d50d2fce7653b9bfe1d71aabb39ab5308c86b768dd9d363e2f444985864273",
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 2831.59,
  "ka_oracle_planted": 2162.16,
  "ka_oracle_shift_m1h": 2260.81,
  "ka_oracle_shift_p1h": 2275.01,
  "t0_base": 2794.69
 },
 "pass": true,
 "period": [
  "2024-11-05",
  "2025-01-07"
 ],
 "planted_ratio": 0.7737,
 "rules": {
  "decoy_ratio_max": 1.1,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01,
  "version": "ka/2"
 },
 "rules_version": "ka/2",
 "shift_penalty": 1.0456,
 "target": "consumption"
}
```

### L37: Known-answer gate solar/wx_radiation under ka/2: PASS

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 37, "run_id": "36339337505", "code_commit": "0f820f1e1b460d680ab26a319aa66afeaaac9a08", "mode": "gate"}`

```json
{
 "checks": {
  "aligned": true,
  "decoy_does_not_break": true,
  "decoy_does_not_help": true,
  "no_sanitised_output": true,
  "planted_helps": true
 },
 "convention": "mean_preceding_hour",
 "covariate": "wx_radiation",
 "days": 64,
 "decoy_ratio": 1.003,
 "fingerprint": "b2d50d2fce7653b9bfe1d71aabb39ab5308c86b768dd9d363e2f444985864273",
 "gate": "known_answer",
 "limit_days": null,
 "mae_mw": {
  "ka_oracle_decoy": 386.49,
  "ka_oracle_planted": 227.83,
  "ka_oracle_shift_m1h": 256.59,
  "ka_oracle_shift_p1h": 277.62,
  "t0_base": 385.32
 },
 "pass": true,
 "period": [
  "2024-11-05",
  "2025-01-07"
 ],
 "planted_ratio": 0.5913,
 "rules": {
  "decoy_ratio_max": 1.1,
  "decoy_ratio_min": 0.98,
  "noise_sd_share_of_p99": 0.05,
  "planted_ratio_max": 0.95,
  "seed": 0,
  "shift_penalty_min": 1.01,
  "version": "ka/2"
 },
 "rules_version": "ka/2",
 "shift_penalty": 1.1262,
 "target": "solar"
}
```

### L39: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 39, "run_id": "36340111693", "code_commit": "0f820f1e1b460d680ab26a319aa66afeaaac9a08", "mode": "reproduce"}`

```json
{
 "identical_numbers_to": "L27",
 "note": "a repeat run (after a code change) that reproduced the same numbers",
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 }
}
```

### L41: Reproduction of a legacy result through the engine

*Experiment:* ENGINE · *grade:* exploratory · *verification:* reproduced_within_tolerance · *source:* `{"ledger": "engine-ledger", "seq": 41, "run_id": "36340111693", "code_commit": "0f820f1e1b460d680ab26a319aa66afeaaac9a08", "mode": "reproduce"}`

```json
{
 "identical_numbers_to": "L14",
 "note": "a repeat run (after a code change) that reproduced the same numbers",
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 }
}
```

### L42: Reproduction check

*Experiment:* ENGINE · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 42, "run_id": "36340111693", "code_commit": "0f820f1e1b460d680ab26a319aa66afeaaac9a08", "mode": "reproduce"}`

```json
{
 "identical_numbers_to": "L29",
 "note": "a repeat run (after a code change) that reproduced the same numbers"
}
```

### L45: Evidence probe run during a vault rehearsal

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 45, "run_id": "36340931603", "code_commit": "de7867b24c00eeed4aa29b460353e903b68d61ad", "mode": "vault_dryrun"}`

```json
{
 "identical_numbers_to": "L31",
 "note": "a repeat run (after a code change) that reproduced the same numbers",
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 }
}
```

### L47: Evidence probe run during a vault rehearsal

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 47, "run_id": "36340931603", "code_commit": "de7867b24c00eeed4aa29b460353e903b68d61ad", "mode": "vault_dryrun"}`

```json
{
 "identical_numbers_to": "L33",
 "note": "a repeat run (after a code change) that reproduced the same numbers",
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 }
}
```

### L48: Vault rehearsal on consumed 2025 data (NON-CONFIRMATORY)

*Experiment:* ENGINE · *grade:* rehearsal · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 48, "run_id": "36340931603", "code_commit": "de7867b24c00eeed4aa29b460353e903b68d61ad", "mode": "vault_dryrun"}`

```json
{
 "vault_dryrun": {
  "alpha": 0.0125,
  "batch_id": "DRY",
  "batch_sha256": "b0e84cf9132bfd518110baf3c6d7ac2a97795fdcb88a85172ddafb7ea2b74716",
  "claims": [
   {
    "blocks": 12,
    "claim": "C1",
    "delta": 0.2,
    "p": 0.00027459708865876166,
    "p_holm": 0.00054919,
    "skill": 0.43538,
    "t": 4.804693,
    "verdict": "PASS"
   },
   {
    "blocks": 12,
    "claim": "C2",
    "delta": 0.0,
    "p": 0.5198142876812817,
    "p_holm": 0.51981429,
    "skill": -0.001374,
    "t": -0.050831,
    "verdict": "NOT PASS"
   }
  ],
  "leak_checks": {
   "C1:arm": {
    "pass": true
   },
   "C1:ref": {
    "pass": true
   },
   "C2:arm": {
    "pass": true
   },
   "C2:ref": {
    "pass": true
   }
  },
  "sources": {
   "consumption": {
    "chosen": "eco2mix-national-cons-def",
    "coverage": {
     "eco2mix-national-cons-def": 1.0
    }
   }
  },
  "status": "NON-CONFIRMATORY dry run on consumed data - not a verdict",
  "window": [
   "2025-01-16",
   "2025-07-02"
  ]
 },
 "batch_claims": [
  {
   "arm": {
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "best_simple",
   "delta": 0.2,
   "evidence": [
    45
   ],
   "id": "C1",
   "metric": "mae",
   "scope": "all",
   "statement": "t0 + holiday beats blend_50 by more than 20% (C1 replayed)",
   "target": "consumption"
  },
  {
   "arm": {
    "covariates": [
     {
      "id": "bridge_day",
      "transform": "raw"
     },
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "accepted",
   "delta": 0.0,
   "evidence": [
    47
   ],
   "id": "C2",
   "metric": "mae",
   "scope": "all",
   "statement": "adding bridge days beats the accepted arm (any margin)",
   "target": "consumption"
  }
 ],
 "batch_window": [
  "2025-01-16",
  "2025-07-02"
 ]
}
```

### L49: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 49, "run_id": "36404992761", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "iteration": 1,
 "action": "probe",
 "note": "Build on C1 (t0+holiday). The consumption weather covariate wx_temperature passed its ka/2 gate, and RTE's weather-driven forecast is still 15-23% better than C1, so temperature is the likeliest missing information. This probe tests three encodings added to C1, each against accepted, on all days from 2024-05-06 on (ALL period). It separates whether t0 uses raw temperature or needs heating-degree (and cooling-degree) nonlinearity. If one arm wins by a large, stable margin, the next steps are seasonal and per-year checks.",
 "owner_question": null,
 "probe_rationale": "C1 (t0+holiday) is accepted, but RTE's weather-driven D-1 forecast beats it by 15-23%, pointing to temperature as the main missing driver. wx_temperature passed the ka/2 known-answer gate (seq 25, 36) and is scorable from 2024-05-06, so ALL gives about 600 days across 2024-2025. The three arms test raw temperature, heating degree-days hdd15 alone, and hdd15 plus cooling degree-days cdd22, each added to the holiday calendar and compared against accepted. This shows whether temperature adds skill on top of C1 and which encoding t0 exploits, leading to a freezable single-arm claim versus accepted.",
 "probe_builds_on": [
  9,
  25,
  36
 ],
 "claim_batch": null
}
```

### L51: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 51, "run_id": "36404992761", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "cdd22"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15_cdd22"
  }
 ],
 "builds_on": [
  9,
  25,
  36
 ],
 "rationale": "C1 (t0+holiday) is accepted, but RTE's weather-driven D-1 forecast beats it by 15-23%, pointing to temperature as the main missing driver. wx_temperature passed the ka/2 known-answer gate (seq 25, 36) and is scorable from 2024-05-06, so ALL gives about 600 days across 2024-2025. The three arms test raw temperature, heating degree-days hdd15 alone, and hdd15 plus cooling degree-days cdd22, each added to the holiday calendar and compared against accepted. This shows whether temperature adds skill on top of C1 and which encoding t0 exploits, leading to a freezable single-arm claim versus accepted.",
 "submitted_by": "researcher:36404992761:1",
 "eligible_days": {
  "accepted": 1456,
  "cal_hdd15": 602,
  "cal_hdd15_cdd22": 602,
  "cal_temp_raw": 602
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "accepted",
   "days": 602,
   "skill": 0.192847,
   "ci95": [
    0.14916,
    0.236644
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1198.786,
   "mae_vs": 1485.203,
   "days_won": 390,
   "days_lost": 212
  },
  {
   "arm": "cal_hdd15",
   "vs": "accepted",
   "days": 602,
   "skill": 0.130968,
   "ci95": [
    0.080475,
    0.173463
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1290.689,
   "mae_vs": 1485.203,
   "days_won": 341,
   "days_lost": 261
  },
  {
   "arm": "cal_hdd15_cdd22",
   "vs": "accepted",
   "days": 602,
   "skill": 0.117162,
   "ci95": [
    0.061511,
    0.168754
   ],
   "p_one_sided": 0.001,
   "mae_arm": 1311.193,
   "mae_vs": 1485.203,
   "days_won": 351,
   "days_lost": 251
  }
 ]
}
```

### L52: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 52, "run_id": "36407411106", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "iteration": 2,
 "action": "probe",
 "note": "Seq 51: t0+holiday+raw temperature beats accepted C1 by 19.3% [14.9, 23.7] over 602 days. Before freezing, I need stability across seasons. The forward window starts about six months out and could fall in summer, where the heating signal is weak. So I test the same arm against accepted on summer scope. If the summer gain is clearly positive, an all-scope claim at delta 0 (lower bound 0.149, so 0.05 would sit less than 0.10 below it) becomes a safe freeze next iteration.",
 "owner_question": null,
 "probe_rationale": "Seq 51 showed raw wx_temperature added to the holiday calendar cuts MAE 19.3% [14.9, 23.7] versus accepted C1 on ALL (602 days, 2024-05..2025). The sealed forward window of 168 days starts about six months after a freeze and may fall mostly in summer, when heating demand vanishes. Restricting to summer months tests whether the gain persists there. If it does, a single-arm all-scope claim versus accepted is robust to the season of the forward window. If it does not, the claim should be scoped to winter. Comparing against t0_base as well separates the temperature effect from the holiday effect in summer.",
 "probe_builds_on": [
  51
 ],
 "claim_batch": null
}
```

### L54: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 54, "run_id": "36407411106", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "summer",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  }
 ],
 "builds_on": [
  51
 ],
 "rationale": "Seq 51 showed raw wx_temperature added to the holiday calendar cuts MAE 19.3% [14.9, 23.7] versus accepted C1 on ALL (602 days, 2024-05..2025). The sealed forward window of 168 days starts about six months after a freeze and may fall mostly in summer, when heating demand vanishes. Restricting to summer months tests whether the gain persists there. If it does, a single-arm all-scope claim versus accepted is robust to the season of the forward window. If it does not, the claim should be scoped to winter. Comparing against t0_base as well separates the temperature effect from the holiday effect in summer.",
 "submitted_by": "researcher:36407411106:2",
 "eligible_days": {
  "accepted": 612,
  "cal_temp_raw": 302,
  "t0_base": 612
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "accepted",
   "days": 302,
   "skill": 0.111199,
   "ci95": [
    0.040328,
    0.17353
   ],
   "p_one_sided": 0.001,
   "mae_arm": 863.842,
   "mae_vs": 971.918,
   "days_won": 179,
   "days_lost": 123
  },
  {
   "arm": "cal_temp_raw",
   "vs": "t0_base",
   "days": 302,
   "skill": 0.193438,
   "ci95": [
    0.119063,
    0.248912
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 863.842,
   "mae_vs": 1071.017,
   "days_won": 190,
   "days_lost": 112
  }
 ]
}
```

### L55: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 55, "run_id": "36408833613", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "iteration": 3,
 "action": "freeze",
 "note": "Raw wx_temperature added to the holiday calendar beat accepted C1 on ALL, scope all (seq 51): skill +19.3%, 95% CI [14.9, 23.7], 602 days, leak checks passed. The gain holds in summer (seq 54: +11.1% [4.0, 17.4]), when heating demand is absent, so it should survive a forward window in either season. Lower bound 0.149 minus 0.10 caps delta at 0.049, hence delta 0. Caveat: I never checked Y2024 and Y2025c separately, so period stability is untested. I freeze one claim only, since no other arm clears the margin rule.",
 "owner_question": null,
 "probe_rationale": null,
 "probe_builds_on": null,
 "claim_batch": {
  "batch_version": "claims/0",
  "claims": [
   {
    "id": "C2_temp",
    "statement": "On French national electricity consumption, t0 with the public-holiday calendar plus the raw archived 2 m temperature forecast has lower day-ahead MAE than the accepted C1 arm (t0 + holiday) over the forward window.",
    "target": "consumption",
    "arm": {
     "covariates": [
      {
       "id": "holiday",
       "transform": "raw"
      },
      {
       "id": "wx_temperature",
       "transform": "raw"
      }
     ]
    },
    "comparator": "accepted",
    "scope": "all",
    "delta": 0.0,
    "evidence": [
     51
    ]
   }
  ]
 }
}
```

### L56: Frozen batch B1 (open; scored on forward data only)

*Experiment:* B1 · *grade:* process · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 56, "run_id": "36408833613", "code_commit": "710b2b37a77c822911380c9bd0289b7f5d109fbf", "mode": "loop"}`

```json
{
 "batch_id": "B1",
 "claims": [
  {
   "arm": {
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     },
     {
      "id": "wx_temperature",
      "transform": "raw"
     }
    ]
   },
   "comparator": "accepted",
   "delta": 0.0,
   "evidence": [
    51
   ],
   "id": "C1",
   "metric": "mae",
   "scope": "all",
   "statement": "On French national electricity consumption, t0 with the public-holiday calendar plus the raw archived 2 m temperature forecast has lower day-ahead MAE than the accepted C1 arm (t0 + holiday) over the forward window.",
   "target": "consumption"
  }
 ],
 "receipt": {
  "batch_id": "B1",
  "batch_sha256": "66965b1332adeeab6f86c83c7cc55efea6a3158f30c572ee6c81839888efec1c",
  "opens_after": "2027-04-01",
  "window": [
   "2026-10-13",
   "2027-03-29"
  ]
 },
 "test": {
  "block_days": 14,
  "blocks": "12 calendar spans from the window's first day",
  "kind": "one-sided block t-test of skill > delta",
  "min_blocks": 10,
  "min_days_per_block": 10,
  "multiplicity": "Holm across the batch at alpha; an unscorable claim stays in at p = 1"
 },
 "alpha": 0.0125,
 "frozen_at": "2026-09-28T10:20:45.720180+00:00",
 "t0": {
  "context_days": 90,
  "gate": "12:00 Europe/Paris on D-1, forecasting local day D",
  "repo_id": "theforecastingcompany/t0-alpha",
  "revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b"
 },
 "source_rule": {
  "min_valid": 0.95,
  "sources": [
   "eco2mix-national-cons-def",
   "eco2mix-national-tr"
  ]
 },
 "accepted_at_freeze": {
  "consumption": {
   "arm": {
    "context_days": 90,
    "covariates": [
     {
      "id": "holiday",
      "transform": "raw"
     }
    ]
   },
   "comparator": "best_simple (blend_50)",
   "confirmed_on": "2025 (sealed, one shot)",
   "finding_id": "C1",
   "lower_bound_one_sided_95": 0.4202,
   "metric": "mae",
   "note": "RTE's own day-ahead forecast (weather-driven) was still 23.1% better than this arm in 2025",
   "run": "https://github.com/xuanhuyle/solar/actions/runs/36145552543",
   "skill": 0.4631,
   "statement": "On French national electricity consumption, t0 with the public-holiday calendar reduces day-ahead MAE versus blend_50 by more than 25% over every buildable delivery day of 2025.",
   "target": "consumption"
  }
 }
}
```

### L58: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 58, "run_id": "36415871063", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "iteration": 1,
 "action": "probe",
 "note": "Answers the owner's question, overall part first. The three temperature encodings from seq 51 are each compared against rte_j1 on the same ALL days (about 602 days, 2024-05 to 2025). This gives the raw-arm gap, frozen in B1, and shows whether hdd15 or hdd15+cdd22 narrows it. Iterations 2 and 3 will repeat this on the winter and summer scopes. rte_j1 is a reference only, so these results cannot support a claim; B1 is still open.",
 "owner_question": "How does the temperature model (t0 + holiday + raw wx_temperature, the arm frozen in B1) compare with RTE's own day-ahead forecast (rte_j1) on the same days? Report the gap overall and by season (winter, summer), and say whether any encoding narrows it. rte_j1 is a reference only.",
 "probe_rationale": "The owner asks how the B1 arm (t0 + holiday + raw wx_temperature) compares with RTE's day-ahead forecast, overall and by season, and whether any encoding narrows the gap. Seq 51 found raw 19.3% better than C1, with hdd15 at 13.1% and hdd15+cdd22 at 11.7%. C1 itself trailed rte_j1 by 15-23%. This probe measures each encoding against rte_j1 on the same ALL days, scope all. Winter and summer follow in the next two iterations. This is a reference-only measurement; no claim can use rte_j1.",
 "probe_builds_on": [
  51,
  54
 ],
 "claim_batch": null
}
```

### L60: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 60, "run_id": "36415871063", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "all",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "cdd22"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15_cdd22"
  }
 ],
 "builds_on": [
  51,
  54
 ],
 "rationale": "The owner asks how the B1 arm (t0 + holiday + raw wx_temperature) compares with RTE's day-ahead forecast, overall and by season, and whether any encoding narrows the gap. Seq 51 found raw 19.3% better than C1, with hdd15 at 13.1% and hdd15+cdd22 at 11.7%. C1 itself trailed rte_j1 by 15-23%. This probe measures each encoding against rte_j1 on the same ALL days, scope all. Winter and summer follow in the next two iterations. This is a reference-only measurement; no claim can use rte_j1.",
 "submitted_by": "researcher:36415871063:1",
 "eligible_days": {
  "cal_hdd15": 602,
  "cal_hdd15_cdd22": 602,
  "cal_temp_raw": 602,
  "rte_j1": 1456
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "rte_j1",
   "days": 602,
   "skill": 0.0761,
   "ci95": [
    -0.027304,
    0.159955
   ],
   "p_one_sided": 0.068966,
   "mae_arm": 1198.786,
   "mae_vs": 1297.528,
   "days_won": 379,
   "days_lost": 223,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15",
   "vs": "rte_j1",
   "days": 602,
   "skill": 0.005271,
   "ci95": [
    -0.093016,
    0.083655
   ],
   "p_one_sided": 0.522739,
   "mae_arm": 1290.689,
   "mae_vs": 1297.528,
   "days_won": 354,
   "days_lost": 248,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15_cdd22",
   "vs": "rte_j1",
   "days": 602,
   "skill": -0.010532,
   "ci95": [
    -0.120848,
    0.080896
   ],
   "p_one_sided": 0.611194,
   "mae_arm": 1311.193,
   "mae_vs": 1297.528,
   "days_won": 367,
   "days_lost": 235,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L61: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 61, "run_id": "36418336095", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "iteration": 2,
 "action": "probe",
 "note": "Owner's question, overall answer from seq 60: the B1 arm (holiday + raw temp) is 7.6% better than rte_j1 on 602 days (1199 vs 1298 MW, CI -2.7% to +16.0%), so it is not a clear win. hdd15 roughly ties RTE (+0.5%) and hdd15+cdd22 trails slightly (-1.1%), so neither alternative encoding beats raw. This probe measures the same three arms against rte_j1 in winter. Summer follows in iteration 3. rte_j1 is a reference only and cannot back a claim.",
 "owner_question": "How does the temperature model (t0 + holiday + raw wx_temperature, the arm frozen in B1) compare with RTE's own day-ahead forecast (rte_j1) on the same days? Report the gap overall and by season (winter, summer), and say whether any encoding narrows it. rte_j1 is a reference only.",
 "probe_rationale": "The owner asks for the gap between the B1 arm and rte_j1 overall and by season, and whether any encoding narrows it. Seq 60 measured the overall gap: raw is +7.6% [-2.7, 16.0] versus rte_j1, hdd15 is +0.5% and hdd15+cdd22 is -1.1%. Winter is where heating demand dominates and where RTE's weather model should be strongest. It is also where hdd15 might outperform raw. This probe measures all three encodings against rte_j1 on winter days in ALL (2024-11..2025-03, about 150 days). Reference-only measurement; it creates no claim.",
 "probe_builds_on": [
  51,
  54,
  60
 ],
 "claim_batch": null
}
```

### L63: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 63, "run_id": "36418336095", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "winter",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "cdd22"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15_cdd22"
  }
 ],
 "builds_on": [
  51,
  54,
  60
 ],
 "rationale": "The owner asks for the gap between the B1 arm and rte_j1 overall and by season, and whether any encoding narrows it. Seq 60 measured the overall gap: raw is +7.6% [-2.7, 16.0] versus rte_j1, hdd15 is +0.5% and hdd15+cdd22 is -1.1%. Winter is where heating demand dominates and where RTE's weather model should be strongest. It is also where hdd15 might outperform raw. This probe measures all three encodings against rte_j1 on winter days in ALL (2024-11..2025-03, about 150 days). Reference-only measurement; it creates no claim.",
 "submitted_by": "researcher:36418336095:2",
 "eligible_days": {
  "cal_hdd15": 210,
  "cal_hdd15_cdd22": 210,
  "cal_temp_raw": 210,
  "rte_j1": 604
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "rte_j1",
   "days": 210,
   "skill": -0.261893,
   "ci95": [
    -0.418254,
    -0.122944
   ],
   "p_one_sided": 0.999,
   "mae_arm": 1731.358,
   "mae_vs": 1372.032,
   "days_won": 83,
   "days_lost": 127,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15",
   "vs": "rte_j1",
   "days": 210,
   "skill": -0.266144,
   "ci95": [
    -0.422069,
    -0.13578
   ],
   "p_one_sided": 0.9995,
   "mae_arm": 1737.19,
   "mae_vs": 1372.032,
   "days_won": 87,
   "days_lost": 123,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15_cdd22",
   "vs": "rte_j1",
   "days": 210,
   "skill": -0.375522,
   "ci95": [
    -0.543931,
    -0.212036
   ],
   "p_one_sided": 1.0,
   "mae_arm": 1887.26,
   "mae_vs": 1372.032,
   "days_won": 83,
   "days_lost": 127,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L64: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 64, "run_id": "36419163633", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "iteration": 3,
 "action": "probe",
 "note": "Completes the owner's question. Seq 60 (all scope): B1 raw arm is +7.6% [-2.7,+16.0] vs rte_j1, hdd15 +0.5%, hdd15+cdd22 -1.1%. Seq 63 (winter): raw trails RTE by 26.2% [-41.8,-12.3], hdd15 -26.6%, hdd15+cdd22 -37.6%. No encoding narrows the winter gap. This probe measures the three encodings against rte_j1 in summer on the same ALL days, which gives the seasonal split. Reference only; it creates no claim, and B1 stays open.",
 "owner_question": "How does the temperature model (t0 + holiday + raw wx_temperature, the arm frozen in B1) compare with RTE's own day-ahead forecast (rte_j1) on the same days? Report the gap overall and by season (winter, summer), and say whether any encoding narrows it. rte_j1 is a reference only.",
 "probe_rationale": "Owner asks for the B1-vs-rte_j1 gap overall and by season, and whether any encoding narrows it. Overall (seq 60): raw +7.6%, hdd15 +0.5%, hdd15+cdd22 -1.1%. Winter (seq 63): all encodings trail RTE by 26-38%. The overall lead implies t0 is ahead of RTE outside winter. This summer probe tests that directly and checks whether cdd22 helps where cooling matters. Reference-only measurement; no claim can use rte_j1.",
 "probe_builds_on": [
  51,
  54,
  60,
  63
 ],
 "claim_batch": null
}
```

### L66: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 66, "run_id": "36419163633", "code_commit": "7ad50be471fc7969801de69c38bd42672609c3e1", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "summer",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "cdd22"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15_cdd22"
  }
 ],
 "builds_on": [
  51,
  54,
  60,
  63
 ],
 "rationale": "Owner asks for the B1-vs-rte_j1 gap overall and by season, and whether any encoding narrows it. Overall (seq 60): raw +7.6%, hdd15 +0.5%, hdd15+cdd22 -1.1%. Winter (seq 63): all encodings trail RTE by 26-38%. The overall lead implies t0 is ahead of RTE outside winter. This summer probe tests that directly and checks whether cdd22 helps where cooling matters. Reference-only measurement; no claim can use rte_j1.",
 "submitted_by": "researcher:36419163633:3",
 "eligible_days": {
  "cal_hdd15": 302,
  "cal_hdd15_cdd22": 302,
  "cal_temp_raw": 302,
  "rte_j1": 612
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "rte_j1",
   "days": 302,
   "skill": 0.30636,
   "ci95": [
    0.219113,
    0.376828
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 863.842,
   "mae_vs": 1245.374,
   "days_won": 232,
   "days_lost": 70,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15",
   "vs": "rte_j1",
   "days": 302,
   "skill": 0.180849,
   "ci95": [
    0.061241,
    0.269633
   ],
   "p_one_sided": 0.003498,
   "mae_arm": 1020.149,
   "mae_vs": 1245.374,
   "days_won": 201,
   "days_lost": 101,
   "note": "reference only: RTE's forecast never decides anything"
  },
  {
   "arm": "cal_hdd15_cdd22",
   "vs": "rte_j1",
   "days": 302,
   "skill": 0.229168,
   "ci95": [
    0.132359,
    0.303899
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 959.975,
   "mae_vs": 1245.374,
   "days_won": 218,
   "days_lost": 84,
   "note": "reference only: RTE's forecast never decides anything"
  }
 ]
}
```

### L67: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 67, "run_id": "36428879883", "code_commit": "006df234e22c2344d53f304d2ba88d823c7faa77", "mode": "loop"}`

```json
{
 "iteration": 1,
 "action": "probe",
 "note": "Answers the owner directly. Arms: B1 (holiday + raw wx_temperature) and holiday + hdd15, each against accepted C1, scope winter, period ALL. That covers about 210 winter days scorable from 2024-05, the same days for both. The result gives winter skill, CI and days won and lost for each arm. Comparing the two skills shows whether hdd15 beats raw against C1 in winter. hdd15+cdd22 is dropped because cdd22 is almost always 0 in winter. Exploratory only: no freeze, and B1 stays open.",
 "owner_question": "B1's forward window (2026-10-13..2027-03-29) is mostly winter. How does the B1 arm (t0 + holiday + raw wx_temperature) compare with the accepted C1 arm in winter (scope winter, Nov-Mar), on the same days? Report the winter skill with its CI and the days won and lost, and say whether a heating-degree encoding does better than raw temperature against C1 in winter. Exploratory only: B1 stays open and no new freeze is wanted.",
 "probe_rationale": "B1's forward window (2026-10-13..2027-03-29) is mostly winter. Seq 51 found raw temperature 19.3% better than C1 over all months, with hdd15 at 13.1%. Seq 54 found raw 11.1% better in summer, which implies a larger gain in winter. Seq 63 showed that both encodings still trail RTE in winter. This probe measures B1's arm and the hdd15 encoding against accepted C1 on the same winter days in ALL, reporting skill, CI and days won and lost. It tests whether B1's effect holds in the season its window covers, and whether heating-degree encoding beats raw temperature in winter. Exploratory only; no freeze is intended.",
 "probe_builds_on": [
  51,
  54,
  63
 ],
 "claim_batch": null
}
```

### L69: Researcher probe result

*Experiment:* ENGINE · *grade:* exploratory · *verification:* not_independently_verified · *source:* `{"ledger": "engine-ledger", "seq": 69, "run_id": "36428879883", "code_commit": "006df234e22c2344d53f304d2ba88d823c7faa77", "mode": "loop"}`

```json
{
 "status": "EXPLORATORY - discovery zone, not creditable",
 "target": "consumption",
 "period": "ALL",
 "scope": "winter",
 "limit_days": null,
 "leak_checks_passed": true,
 "accepted_arm": {
  "context_days": 90,
  "covariates": [
   {
    "id": "holiday",
    "transform": "raw"
   }
  ]
 },
 "arms": [
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "raw"
    }
   ],
   "name": "cal_temp_raw"
  },
  {
   "covariates": [
    {
     "id": "holiday",
     "transform": "raw"
    },
    {
     "id": "wx_temperature",
     "transform": "hdd15"
    }
   ],
   "name": "cal_hdd15"
  }
 ],
 "builds_on": [
  51,
  54,
  63
 ],
 "rationale": "B1's forward window (2026-10-13..2027-03-29) is mostly winter. Seq 51 found raw temperature 19.3% better than C1 over all months, with hdd15 at 13.1%. Seq 54 found raw 11.1% better in summer, which implies a larger gain in winter. Seq 63 showed that both encodings still trail RTE in winter. This probe measures B1's arm and the hdd15 encoding against accepted C1 on the same winter days in ALL, reporting skill, CI and days won and lost. It tests whether B1's effect holds in the season its window covers, and whether heating-degree encoding beats raw temperature in winter. Exploratory only; no freeze is intended.",
 "submitted_by": "researcher:36428879883:1",
 "eligible_days": {
  "accepted": 604,
  "cal_hdd15": 210,
  "cal_temp_raw": 210
 },
 "comparisons": [
  {
   "arm": "cal_temp_raw",
   "vs": "accepted",
   "days": 210,
   "skill": 0.243618,
   "ci95": [
    0.190223,
    0.307345
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1731.358,
   "mae_vs": 2288.999,
   "days_won": 155,
   "days_lost": 55
  },
  {
   "arm": "cal_hdd15",
   "vs": "accepted",
   "days": 210,
   "skill": 0.24107,
   "ci95": [
    0.182787,
    0.297403
   ],
   "p_one_sided": 0.0005,
   "mae_arm": 1737.19,
   "mae_vs": 2288.999,
   "days_won": 156,
   "days_lost": 54
  }
 ]
}
```

### L70: The researcher's own earlier decision and reasoning

*Experiment:* ENGINE · *grade:* researcher_note · *verification:* not_applicable · *source:* `{"ledger": "engine-ledger", "seq": 70, "run_id": "36430372130", "code_commit": "006df234e22c2344d53f304d2ba88d823c7faa77", "mode": "loop"}`

```json
{
 "iteration": 2,
 "action": "stop",
 "note": "Seq 69 already answers this. Winter, same 210 days: B1 arm (holiday + raw temp) vs C1 skill +24.4%, CI [19.0, 30.7], MAE 1731 vs 2289 MW, 155 days won, 55 lost. hdd15: +24.1%, CI [18.3, 29.7], 156 won, 54 lost, so heating degrees do not beat raw temperature against C1 in winter. The two are tied within overlapping CIs, and the catalogue has no direct raw-vs-hdd15 comparator. Winter is B1's strongest season (summer +11.1%, seq 54), yet both arms trail RTE by about 26% (seq 63). Exploratory only; B1 stays open, no freeze, no spend.",
 "owner_question": "B1's forward window (2026-10-13..2027-03-29) is mostly winter. How does the B1 arm (t0 + holiday + raw wx_temperature) compare with the accepted C1 arm in winter (scope winter, Nov-Mar), on the same days? Report the winter skill with its CI and the days won and lost, and say whether a heating-degree encoding does better than raw temperature against C1 in winter. Exploratory only: B1 stays open and no new freeze is wanted.",
 "probe_rationale": null,
 "probe_builds_on": null,
 "claim_batch": null
}
```

### X4-SPEC: Experiment 4's frozen questions, comparators and reading rules (owner-approved)

*Experiment:* EXP4 · *grade:* process · *verification:* not_applicable · *source:* `{"path": "docs/experiment_4/ONE_PAGER.md"}`

````text
# Experiment 4: can t0 forecast French electricity prices from public data?

*Written and frozen before any French price was fetched. The binding version is `PRICE_SPEC` in
`solarbench/price_spec.py`; this page restates it in plain words.*

## Why this experiment
On national electricity demand, RTE's own forecast still beats t0. RTE has data and expertise nobody
outside can match. Prices are different: the day-ahead auction price is public, and so is most of what drives
it. t0's makers present prices as a showcase use. So prices are a fair place to ask whether t0 is useful
**without proprietary data**.

What t0's report actually shows on prices is thin:
- **France:** one test of 20 day-ahead forecasts, probably 12–31 December 2016 (the dates are inferred, not
  confirmed).
  - On that task, t0 with extra inputs ranks about 8th of 26 published entries.
  - One model that uses price history alone is within 5% of it.
  - The extra inputs helped t0 by about 5%.
- **Germany:** the 51% gain came from the grid operators' day-ahead load, wind and solar forecasts.
  - The report does not say when these were issued.
  - Wind and solar forecasts are reportedly due only at 18:00 the day before, after the auction closes (not
    verified).
  - If so, a forecaster working at noon could not have used them.

t0 may lose here. Either answer is useful.

## The forecasting task
- **When the forecast is made:** at noon on the day before delivery, the latest moment before the day-ahead
  auction closes.
- **What is forecast:** the French price (EUR/MWh) for each hour of the next day.
- **What the forecast may use:**
  - every price already published, which includes all of today's prices, since they were set yesterday;
  - the holiday calendar;
  - for one question, public weather forecasts made well before noon.
- **What is never used:** anything published after noon, and any data from 2026 on.
- **Test period:** 2024 and 2025 (731 days).
  - The best of 8 simple rules is picked once, on 2023.
  - The result is tested once on the two years together. It must then also point the same way in 2024 alone
    and in 2025 alone. Each single year is not tested separately.
- **What the results can and cannot claim:** they are exploratory. These years are public and already studied,
  so nothing here counts as proven. Proof would come later, on future data, through the engine's sealed vault.

## The four questions (all decided before any data is seen)
| # | Question | t0 is compared with | Counts as a win when |
|---|---|---|---|
| P1 | Does t0 beat simple rules? | The best of 8 simple rules, chosen on 2023 | Over 2024–2025 together, t0's average error is clearly lower. In 2024 alone and in 2025 alone it is also lower (no test for each year). |
| P2 | Is t0 no more than 5% worse than the standard free price model? | LEAR, the model price-forecasting researchers use as a yardstick, given the same information | Over both years together, t0 is clearly no more than 5% worse, and it is also less than 5% worse in each year alone. LEAR only counts if our copy first reproduces its published results and forecasts at least 95% of the test days. Otherwise P2 is "not run" and counts as not won. |
| P3 | Can t0's "likely range" be trusted? | Simple ranges built from past errors | Over both years together, t0's ranges score clearly better, and they also score better in each year alone. Over both years, its 80% range contains 70–90% of the prices. |
| P4 | Do free public weather forecasts help t0? | t0 without weather | On its test days, t0 with weather is clearly better overall. It is also better in the 2024 part alone and in 2025 alone. The test days run from 6 June 2024 to the end of 2025; the start may move later if weather data are missing, never earlier. P4 runs only if a planted-signal test first shows the weather plumbing works and at least one weather day can be scored. |

"Clearly" means the win survives one statistical test on all the test days together. The test allows for
noise from day to day and for the fact that four questions are asked at once. Each year only has to point the
same way; it is not tested on its own.

## How the results will be read (frozen)
- **P1 and P2 won:** on public price data alone, t0 beats the best simple rule and is no more than 5% worse
  than the standard free model.
- **P1 won, P2 lost or not stable:** t0 beats the best simple rule, but it is not shown to be within 5% of the
  standard free model. It may be more than 5% worse.
- **P1 won, P2 not run:** LEAR failed its reproduction check or missed too many days, so t0 was not compared
  with it. Nothing is concluded about LEAR.
- **P1 not won, P2 won:** t0 is within 5% of the standard free model but is not shown to beat the best simple
  rule.
- **P1 and P2 not won:** this study does not show that t0 is useful on French prices from price history alone.
  - This is not proof that t0 is useless.
  - If P2 was not run, it adds that the comparison with LEAR was not made.
  - It says "the simple rule was more accurate" only if the error range is entirely on that side.
- **P3 won:** t0's ranges score better and contain 70–90% of prices. If they score better but contain too few or
  too many prices, they are reported as not trustworthy for risk. Otherwise they are not shown to be better.
- **P4:**
  - **won:** public weather forecasts add value;
  - **lost:** no value is shown;
  - **not run:** the planted-signal test failed, or no weather day could be scored; nothing is said about weather.
- **If a question passes overall but one year does not,** it is reported as "not stable" and counts as not won.

## Safeguards
- **No peeking:** no forecast may use a price published after noon on the day before.
  - Tests rewrite every later price and check that no forecast changes.
  - They also check that changing a legal, earlier price does change it.
- **One exception, checked separately:** the only new allowance is that this afternoon's and evening's prices,
  already set yesterday, may be used.
  - A "strict" version of t0 whose price history ends with today's noon-to-1 pm price (the old rule used for
    demand and solar: nothing stamped after the forecast time) is compared with the simple rule that keeps the
    allowance.
  - It is also compared with the same simple rule held to the same old rule.
  - Tests check that the strict version sees today's prices up to and including the noon-to-1 pm price, and
    nothing later.
  - It is read only if P1 is won; otherwise its numbers are printed for information.
  - How each outcome will be read is fixed in advance, and this check never changes the four answers.
- **Real-model check:** before any scoring, the real model is checked the same way on 11 days:
  - the first, middle and last test days;
  - 8 tricky ones: the four clock changes, 26 June 2024, and 30 September to 2 October 2025 around the switch to
    15-minute prices.
- **Nothing existing changes:** no existing code or experiment is modified.

*Prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE).*
````

### X4-ROLE: Experiment 4's place in the programme (owner directive, 2026-09-29)

*Experiment:* EXP4 · *grade:* owner_directive · *verification:* not_applicable · *source:* `{"path": "docs/experiment_4/PROGRAM_ROLE.md"}`

````text
# Experiment 4's place in the programme

*Owner's directive, 29 September 2026. This note frames Experiment 4; it is not part of it. The binding
experiment is `PRICE_SPEC` in `solarbench/price_spec.py` (hash pinned at `aa28301`, data facts filled at
`f9f0a2f`) and its restatement `ONE_PAGER.md`. Neither is changed by this note, and nothing here alters how
any result of Experiment 4 is computed or read.*

## Experiment 4 stays exactly as frozen
- Its four questions, comparators, statistics and reading table were fixed before any price was fetched. They
  are applied as written.
- Each question's result is read only by its own frozen rule. No question is re-weighted, re-tested or
  re-interpreted after the data are seen.

## Question 4 is the first price test of the core idea
The project's core product idea is that extra public information, supplied to t0 as inputs ("covariates"),
makes its forecasts better than t0 on its own. On French electricity demand this has been tested with
temperature (claim B1, sealed until 2027). On prices, question 4 is the first test.

- **The comparison:** t0 with the holiday calendar and public weather forecasts, against t0 with the holiday
  calendar only, on the same days.
- **The weather forecasts:** temperature and sunshine, archived and issued well before the noon decision.

It is read by its frozen rules and nothing else:
- **Plumbing check first:** it runs only if the planted-signal check of the weather plumbing (K3) passes and
  at least one weather day can be scored.
- **Statistical test:** it must pass one test over its days, allowing for four questions being asked at once.
- **Each year:** it must also point the same way in the 2024 part and in 2025 alone.

Each possible outcome has its frozen reading:
- **won:** public weather forecasts add value to t0 on prices;
- **lost or not stable:** no value is shown;
- **not run:** nothing is concluded about weather.

## Experiment 4 is discovery-grade
- **Why:** the 2024–2025 French prices are public and already studied, and 2025 was already used once for
  claim C1. Whatever Experiment 4 finds is exploratory.
- **What it cannot do:** it cannot by itself satisfy the project's milestone of "one bounded, reproducible,
  independently confirmed predictive finding using t0, followed by an investigation that builds on it".
- **What could satisfy it:** only a claim frozen in advance and then confirmed on data that did not exist when
  it was frozen. That means the engine's sealed forward vault, opened once with the owner's approval.
- **How Experiment 4 would feed that:** a winning question can at most become a candidate, under its frozen
  carry-forward rule. The route into the vault is the owner's decision.

## What happens after Experiment 4 is scored
- **The follow-up is not chosen by hand.** No next covariate experiment is prescribed. The AI researcher
  receives the Experiment 4 evidence and chooses one bounded follow-up investigation based on what was learned.
  The evidence covers every question's state, skill, error range, the pre-declared slices and the plumbing and
  reproduction checks.
- **It is a separate stage** with its own specification and code (Experiment 5 or later). Experiment 4's code,
  specification and results are read-only inputs to it, so the frozen experiment stays scientifically intact.
- **"Bounded" means limits:**
  - a few probes at most, within an evaluation budget;
  - on the exploratory years only (2025 and earlier), never on sealed future data;
  - using only inputs the referee can run without leakage;
  - if the researcher wants a public input that is not yet available, it may request it, and the referee first
    checks that its publication time can be proven and that its licence allows use.
- **Before anything runs:** the referee checks the researcher's proposal, the protocol is frozen, and the owner
  approves it.
- **Its results are exploratory too.** Independent confirmation still goes only through the forward vault.
````

### X4-READING: The frozen reading, as printed by the scored run

*Experiment:* EXP4 · *grade:* discovery_grade_preregistered · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/summary.md", "pointer": "", "run_id": 36823477529, "commit": "2b407f4"}`

````text
Status: discovery-grade: 2024-2025 French prices are public and already studied; 2025 is consumed (explorable, never confirmable). No result here counts as confirmed.

- t0 beats the best simple rule; the comparison with LEAR was not made (K1 failed or LEAR forecast too few days), so nothing is concluded about LEAR.
  - P1 (t0_cal vs best_simple_2023, MAE skill): state 'won'; pooled skill 0.227107; 95% interval [0.186116, 0.259087]; raw p 0.00049975; Holm p 0.001999; 2024 0.225383; 2025 0.228779; days 731
  - P2 (t0_cal vs lear_ens, MAE skill): state 'not runnable'; pooled skill not run; 95% interval not run; raw p not run; Holm p 1; 2024 not run; 2025 not run; days not run; cause: K1 failed
- t0's native bands score better than simple empirical bands, and its 10-90 band covers 70-90% of scored hours.
  - P3 (t0_cal vs best_simple_eq, pinball skill): state 'won'; pooled skill 0.251885; 95% interval [0.213317, 0.280905]; raw p 0.00049975; Holm p 0.001999; 2024 0.256492; 2025 0.247378; days 731; coverage 0.732786 (2024 0.722564, 2025 0.743037)
- Public weather forecasts issued before the gate add value to t0 on prices (P4 days only).
  - P4 (t0_cal_wx vs t0_cal, MAE skill): state 'won'; pooled skill 0.0284216; 95% interval [0.0114454, 0.0441206]; raw p 0.0009995; Holm p 0.001999; 2024 0.0151408; 2025 0.0367856; days 572
- P1 does not rest on t0 reading the D-1 afternoon prices.
  - t0_cal_strict vs best_simple_2023: pooled 0.067768, 2024 0.0809742, 2025 0.0549668; t0_cal_strict vs best_simple_2023_strict: pooled 0.153247, 2024 0.159079, 2025 0.147675

Day-ahead prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE)

Amended: A1 (2026-09-30, owner-approved) - the LEAR penalty is chosen as scikit-learn <= 0.23.1 chose it, as the published EPF forecasts were made (docs/experiment_4/AMENDMENTS.md). The frozen specification file and every threshold are unchanged; LEAR penalty step (1) is superseded by A1.
````

### X4-P1: Experiment 4 primary P1

*Experiment:* EXP4 · *grade:* discovery_grade_preregistered · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/primaries/P1, /verdicts/P1, /carry_forward/P1", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "primary": {
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "metric": "mae",
  "status": "ok",
  "skill": 0.22710738685445464,
  "ci95": [
   0.18611648875703038,
   0.25908681895186997
  ],
  "p": 0.0004997501249375312,
  "yearly": {
   "2024": 0.22538293157022915,
   "2025": 0.22877895847715857
  },
  "days": 731,
  "compare": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.22710738685445464,
   "ci95": [
    0.18611648875703038,
    0.25908681895186997
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 731,
   "hours": 17544,
   "loss_arm": 15.276627816199383,
   "loss_ref": 19.765524416161814,
   "days_won": 519,
   "days_lost": 212,
   "metric": "mae",
   "yearly": {
    "2024": 0.22538293157022915,
    "2025": 0.22877895847715857
   }
  },
  "runnable": true,
  "cause": null
 },
 "verdict": {
  "state": "won",
  "p_holm": 0.001999000499750125,
  "p_holm_input": 0.0004997501249375312,
  "p": 0.0004997501249375312,
  "threshold": 0.0,
  "ci95": [
   0.18611648875703038,
   0.25908681895186997
  ],
  "cause": null
 },
 "carry_forward": {
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "state": "won",
  "candidate": true,
  "delta": 0.0,
  "status": "ok",
  "S": 0.1551330663119581,
  "days": 366,
  "M": 0.1223,
  "block_sd": 2.343,
  "ref_mae": 18.998,
  "M_info": {
   "0.0125/2": 0.1361,
   "0.0125/3": 0.1442,
   "0.0125/4": 0.15
  }
 }
}
```

### X4-P2: Experiment 4 primary P2

*Experiment:* EXP4 · *grade:* discovery_grade_preregistered · *verification:* internal_consistency_only · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/primaries/P2, /verdicts/P2, /carry_forward/P2", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "primary": {
  "arm": "t0_cal",
  "ref": "lear_ens",
  "metric": "mae",
  "status": "not run",
  "skill": "not run",
  "ci95": "not run",
  "p": "not run",
  "yearly": {
   "2024": "not run",
   "2025": "not run"
  },
  "days": "not run",
  "compare": {
   "status": "not run",
   "arm": "t0_cal",
   "ref": "lear_ens",
   "metric": "mae",
   "yearly": {
    "2024": "not run",
    "2025": "not run"
   },
   "cause": "lear_ens not scored (K1 failed)"
  },
  "runnable": false,
  "cause": "K1 failed",
  "p2_coverage": "not run"
 },
 "verdict": {
  "state": "not runnable",
  "p_holm": 1.0,
  "p_holm_input": 1.0,
  "p": "not run",
  "threshold": -0.05,
  "ci95": "not run",
  "cause": "K1 failed"
 },
 "carry_forward": {
  "arm": "t0_cal",
  "ref": "lear_ens",
  "state": "not runnable",
  "candidate": false,
  "delta": null,
  "status": "not run"
 }
}
```

### X4-P3: Experiment 4 primary P3

*Experiment:* EXP4 · *grade:* discovery_grade_preregistered · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/primaries/P3, /verdicts/P3, /carry_forward/P3", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "primary": {
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "metric": "pinball",
  "status": "ok",
  "skill": 0.2518851196137203,
  "ci95": [
   0.21331719447156108,
   0.28090523787558197
  ],
  "p": 0.0004997501249375312,
  "yearly": {
   "2024": 0.2564917181607418,
   "2025": 0.2473776358890113
  },
  "days": 731,
  "compare": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.2518851196137203,
   "ci95": [
    0.21331719447156108,
    0.28090523787558197
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 731,
   "hours": 17544,
   "loss_arm": 5.459919786310282,
   "loss_ref": 7.298237114988438,
   "days_won": 568,
   "days_lost": 163,
   "metric": "pinball",
   "yearly": {
    "2024": 0.2564917181607418,
    "2025": 0.2473776358890113
   }
  },
  "runnable": true,
  "cause": null,
  "coverage": 0.7327861377108983,
  "coverage_yearly": {
   "2024": 0.722563752276867,
   "2025": 0.7430365296803653
  }
 },
 "verdict": {
  "state": "won",
  "p_holm": 0.001999000499750125,
  "p_holm_input": 0.0004997501249375312,
  "p": 0.0004997501249375312,
  "threshold": 0.0,
  "ci95": [
   0.21331719447156108,
   0.28090523787558197
  ],
  "cause": null
 },
 "carry_forward": {
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "state": "won",
  "candidate": true,
  "delta": 0.05,
  "status": "ok",
  "S": 0.17985269011604454,
  "days": 366,
  "M": 0.117,
  "block_sd": 0.822,
  "ref_mae": 6.968,
  "M_info": {
   "0.0125/2": 0.1302,
   "0.0125/3": 0.1379,
   "0.0125/4": 0.1434
  }
 }
}
```

### X4-P4: Experiment 4 primary P4

*Experiment:* EXP4 · *grade:* discovery_grade_preregistered · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/primaries/P4, /verdicts/P4, /carry_forward/P4", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "primary": {
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "metric": "mae",
  "status": "ok",
  "skill": 0.02842160653111203,
  "ci95": [
   0.011445430256543909,
   0.04412064234228268
  ],
  "p": 0.0009995002498750624,
  "yearly": {
   "2024": 0.015140844864288572,
   "2025": 0.03678561969496841
  },
  "days": 572,
  "compare": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.02842160653111203,
   "ci95": [
    0.011445430256543909,
    0.04412064234228268
   ],
   "p_one_sided": 0.0009995002498750624,
   "margin": 0.0,
   "m": -0.0,
   "days": 572,
   "hours": 13729,
   "loss_arm": 15.635187903796083,
   "loss_ref": 16.092564438339124,
   "days_won": 307,
   "days_lost": 265,
   "metric": "mae",
   "yearly": {
    "2024": 0.015140844864288572,
    "2025": 0.03678561969496841
   }
  },
  "runnable": true,
  "cause": null
 },
 "verdict": {
  "state": "won",
  "p_holm": 0.001999000499750125,
  "p_holm_input": 0.0009995002498750624,
  "p": 0.0009995002498750624,
  "threshold": 0.0,
  "ci95": [
   0.011445430256543909,
   0.04412064234228268
  ],
  "cause": null
 },
 "carry_forward": {
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "state": "won",
  "candidate": false,
  "delta": null,
  "status": "ok",
  "S": 0.011223231707229164,
  "days": 300,
  "M": 0.0489,
  "block_sd": 0.789,
  "ref_mae": 16.005,
  "M_info": {
   "0.0125/2": 0.0544,
   "0.0125/3": 0.0577,
   "0.0125/4": 0.06
  }
 }
}
```

### X4-CARRY: Experiment 4's frozen carry-forward rule, what the vault can express, and the route (PRICE_SPEC)

*Experiment:* EXP4 · *grade:* process · *verification:* not_applicable · *source:* `{"path": "solarbench/price_spec.py", "pointer": "PRICE_SPEC['carry_forward']"}`

```json
{
 "rule": "a primary is a vault candidate only if its state is 'won' and some delta in {0, 0.05, 0.10, 0.20} satisfies S - delta >= M. A = the per-day table (sum_abs_err, n; P3: pinball sums) of its t0 arm and comparator on its own day set, restricted to Paris delivery dates in April-September of 2024 or 2025. S = its skill on A. M = engine.referee.stats.power_table(A, t0_arm, comparator, alpha=0.0125)['min_detectable_skill']['12']. delta is the largest value satisfying the inequality; if none does, it is not a candidate. S, M, A's day count, block_sd and ref_mae are printed, and M at alpha 0.0125/2, /3 and /4 for information only",
 "expressible_today": "P1 (vs best_simple) and P4 (vs accepted, once P1's arm is accepted); P2 and P3 need vault extensions",
 "route": "decided by the owner after the results (default: an engine price lane after B1 opens)"
}
```

### X4-STRICT: Experiment 4 strict check (report-only)

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/strict", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "best_simple_2023": {
  "pooled": 0.06776800220200119,
  "2024": 0.08097422272925148,
  "2025": 0.054966775241547694,
  "days": 731
 },
 "best_simple_2023_strict": {
  "pooled": 0.15324667077345844,
  "2024": 0.1590786672093527,
  "2025": 0.1476745437595881,
  "days": 731
 }
}
```

### X4-SECONDARIES: Experiment 4 secondaries (report-only, not adjusted for multiplicity)

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/secondaries", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "t0 (no calendar) vs best_simple_2023": {
  "status": "ok",
  "arm": "t0",
  "ref": "best_simple_2023",
  "skill": 0.20632715036020688,
  "ci95": [
   0.16760576367188768,
   0.23640737405021137
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 17544,
  "loss_arm": 15.687360088000057,
  "loss_ref": 19.765524416161814,
  "days_won": 514,
  "days_lost": 217,
  "metric": "mae",
  "yearly": {
   "2024": 0.2007436625140202,
   "2025": 0.21173941006028396
  }
 },
 "t0_cal vs t0": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "t0",
  "skill": 0.026182370360380736,
  "ci95": [
   0.0026503292692320185,
   0.05315255290920478
  ],
  "p_one_sided": 0.01649175412293853,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 17544,
  "loss_arm": 15.276627816199383,
  "loss_ref": 15.687360088000057,
  "days_won": 429,
  "days_lost": 302,
  "metric": "mae",
  "yearly": {
   "2024": 0.03082774311644554,
   "2025": 0.021616643828632598
  }
 },
 "t0_cal_strict vs best_simple_2023 (t0 alone without the allowance)": {
  "status": "ok",
  "arm": "t0_cal_strict",
  "ref": "best_simple_2023",
  "skill": 0.06776800220200119,
  "ci95": [
   0.026414860328926273,
   0.10226277446000363
  ],
  "p_one_sided": 0.0014992503748125937,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 17544,
  "loss_arm": 18.426054314003654,
  "loss_ref": 19.765524416161814,
  "days_won": 427,
  "days_lost": 304,
  "metric": "mae",
  "yearly": {
   "2024": 0.08097422272925148,
   "2025": 0.054966775241547694
  }
 },
 "t0_cal_strict vs best_simple_2023_strict (the old rule for both)": {
  "status": "ok",
  "arm": "t0_cal_strict",
  "ref": "best_simple_2023_strict",
  "skill": 0.15324667077345844,
  "ci95": [
   0.1136775862797,
   0.1858281246617925
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 17544,
  "loss_arm": 18.426054314003654,
  "loss_ref": 21.760828895511693,
  "days_won": 488,
  "days_lost": 243,
  "metric": "mae",
  "yearly": {
   "2024": 0.1590786672093527,
   "2025": 0.1476745437595881
  }
 },
 "t0_cal vs t0_cal_strict (value of the D-1 afternoon to t0)": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "t0_cal_strict",
  "skill": 0.17092245817438678,
  "ci95": [
   0.14072085535466902,
   0.19838518727379553
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 17544,
  "loss_arm": 15.276627816199383,
  "loss_ref": 18.426054314003654,
  "days_won": 460,
  "days_lost": 271,
  "metric": "mae",
  "yearly": {
   "2024": 0.15713238128078566,
   "2025": 0.18392176981929587
  }
 },
 "lear_ens vs best_simple_2023": {
  "status": "not run",
  "arm": "lear_ens",
  "ref": "best_simple_2023",
  "metric": "mae",
  "yearly": {
   "2024": "not run",
   "2025": "not run"
  },
  "cause": "lear_ens not scored (K1 failed)"
 },
 "t0_cal vs lear_ens (superiority)": {
  "status": "not run",
  "arm": "t0_cal",
  "ref": "lear_ens",
  "metric": "mae",
  "yearly": {
   "2024": "not run",
   "2025": "not run"
  },
  "cause": "lear_ens not scored (K1 failed)"
 },
 "lear_ens + empirical bands vs t0_cal bands": {
  "status": "not run",
  "arm": "lear_ens_eq",
  "ref": "t0_cal",
  "metric": "pinball",
  "yearly": {
   "2024": "not run",
   "2025": "not run"
  },
  "cause": "lear_ens_eq not scored (K1 failed)"
 },
 "rMAE vs naive_std and vs prev_week": {
  "naive_std": {
   "best_simple_2023": {
    "status": "ok",
    "rmae": 0.8648006768099413,
    "days": 731
   },
   "best_simple_2023_strict": {
    "status": "ok",
    "rmae": 0.9521012021009753,
    "days": 731
   },
   "lear_ens": {
    "status": "not run",
    "cause": "lear_ens not scored (K1 failed)"
   },
   "prev_week": {
    "status": "ok",
    "rmae": 1.287189706878542,
    "days": 731
   },
   "t0": {
    "status": "ok",
    "rmae": 0.686368817534168,
    "days": 731
   },
   "t0_cal": {
    "status": "ok",
    "rmae": 0.6683980549496717,
    "days": 731
   },
   "t0_cal_strict": {
    "status": "ok",
    "rmae": 0.8061948626395932,
    "days": 731
   },
   "t0_cal_wx": {
    "status": "ok",
    "rmae": 0.6417710967792953,
    "days": 572
   }
  },
  "prev_week": {
   "best_simple_2023": {
    "status": "ok",
    "rmae": 0.6718517652748314,
    "days": 731
   },
   "best_simple_2023_strict": {
    "status": "ok",
    "rmae": 0.739674344048196,
    "days": 731
   },
   "lear_ens": {
    "status": "not run",
    "cause": "lear_ens not scored (K1 failed)"
   },
   "naive_std": {
    "status": "ok",
    "rmae": 0.7768862621074074,
    "days": 731
   },
   "t0": {
    "status": "ok",
    "rmae": 0.5332305050812008,
    "days": 731
   },
   "t0_cal": {
    "status": "ok",
    "rmae": 0.5192692665097121,
    "days": 731
   },
   "t0_cal_strict": {
    "status": "ok",
    "rmae": 0.6263217133662683,
    "days": 731
   },
   "t0_cal_wx": {
    "status": "ok",
    "rmae": 0.5021488325688611,
    "days": 572
   }
  }
 },
 "RMSE": {
  "P1": {
   "status": "ok",
   "t0_cal": 21.24573765974294,
   "best_simple_2023": 26.325115462924895,
   "days": 731
  },
  "P2": {
   "status": "not run",
   "cause": "lear_ens not scored (K1 failed)"
  },
  "P4": {
   "status": "ok",
   "t0_cal_wx": 21.530678436855606,
   "t0_cal": 22.178504331361857,
   "days": 572
  }
 }
}
```

### X4-SLICES-P1: Experiment 4 slices of P1 (report-only, not adjusted)

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/slices/P1", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "each year": {
  "2024": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.22538293157022915,
   "days": 366
  },
  "2025": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.22877895847715857,
   "days": 365
  }
 },
 "each quarter (2025 Q4 is quarter-hour derived)": {
  "2024Q1": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.28280551513121654,
   "ci95": [
    0.19069893020720702,
    0.363091146042608
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2183,
   "loss_arm": 9.661619021266741,
   "loss_ref": 13.471407303186963,
   "days_won": 71,
   "days_lost": 20
  },
  "2024Q2": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.11881820948602562,
   "ci95": [
    0.07313570826109903,
    0.195642358106952
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2184,
   "loss_arm": 16.525187202251,
   "loss_ref": 18.75343700941915,
   "days_won": 55,
   "days_lost": 36
  },
  "2024Q3": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.22374689408480086,
   "ci95": [
    0.17245941067436224,
    0.29150310853321576
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 16.215481398641195,
   "loss_ref": 20.889425465838507,
   "days_won": 65,
   "days_lost": 27
  },
  "2024Q4": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.2761525509899402,
   "ci95": [
    0.16043499442575895,
    0.36107149479764966
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2209,
   "loss_arm": 17.758274968407605,
   "loss_ref": 24.533173381620642,
   "days_won": 69,
   "days_lost": 23
  },
  "2025Q1": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.3575919053560346,
   "ci95": [
    0.27585396989650085,
    0.4193395991885227
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 90,
   "hours": 2159,
   "loss_arm": 16.053510703669485,
   "loss_ref": 24.98958347118375,
   "days_won": 73,
   "days_lost": 17
  },
  "2025Q2": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.06981014303541111,
   "ci95": [
    0.02517989886666485,
    0.14709656830679202
   ],
   "p_one_sided": 0.0014992503748125937,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2184,
   "loss_arm": 16.20102662813096,
   "loss_ref": 17.41690312663527,
   "days_won": 56,
   "days_lost": 35
  },
  "2025Q3": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.1926904975661241,
   "ci95": [
    0.13705857652910405,
    0.23356506927393655
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 15.266645776361663,
   "loss_ref": 18.91052406832298,
   "days_won": 62,
   "days_lost": 30
  },
  "2025Q4": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_2023",
   "skill": 0.24304543292567038,
   "ci95": [
    0.14045935648465485,
    0.3164977241680664
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2209,
   "loss_arm": 14.507785088991136,
   "loss_ref": 19.165991883851774,
   "days_won": 68,
   "days_lost": 24
  }
 },
 "April-September": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": 0.1551330663119581,
  "ci95": [
   0.12288076888091624,
   0.19479351409469087
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 366,
  "hours": 8784,
  "loss_arm": 16.050385679412628,
  "loss_ref": 18.99753090033828,
  "days_won": 238,
  "days_lost": 128
 },
 "weekends and holidays": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": 0.2660198228935332,
  "ci95": [
   0.219408761619583,
   0.3062843151030665
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 228,
  "hours": 5472,
  "loss_arm": 14.595817843327048,
  "loss_ref": 19.88584746371136,
  "days_won": 174,
  "days_lost": 54
 },
 "the weeks after each DST switch": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": -0.053638453908970485,
  "ci95": [
   -0.15685937977438713,
   0.14372667816791238
  ],
  "p_one_sided": 0.29985007496251875,
  "margin": 0.0,
  "m": -0.0,
  "days": 28,
  "hours": 672,
  "loss_arm": 19.51726195460274,
  "loss_ref": 18.52368037840136,
  "days_won": 14,
  "days_lost": 14
 },
 "negative-price hours": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": 0.26595506710842365,
  "ci95": [
   0.16596772217682335,
   0.3254670413459004
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 163,
  "hours": 865,
  "loss_arm": 12.647318699566618,
  "loss_ref": 17.229624690338564,
  "days_won": 108,
  "days_lost": 55
 },
 "top 1% absolute prices": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": 0.15952184170604466,
  "ci95": [
   0.11737086714198339,
   0.31382687579261936
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 45,
  "hours": 176,
  "loss_arm": 38.414738136638285,
  "loss_ref": 45.705813717532465,
  "days_won": 32,
  "days_lost": 13
 },
 "11:00-16:00 local": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_2023",
  "skill": 0.2103809531850488,
  "ci95": [
   0.16235953365291514,
   0.24528935342868743
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 3655,
  "loss_arm": 14.938562250056444,
  "loss_ref": 18.91869542700801,
  "days_won": 465,
  "days_lost": 266
 }
}
```

### X4-TABLES-P1: Experiment 4 concentration and bootstrap sensitivity of P1

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/tables/P1", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "status": "ok",
 "concentration": {
  "model": "t0_cal",
  "reference": "best_simple_2023",
  "net_gain_mw": 78753.20194974082,
  "n_days": 731,
  "skill": 0.22710738685445464,
  "top5_share_of_net_gain": 0.06496100177014258,
  "skill_without_top5": 0.2169110240482559,
  "top10_share_of_net_gain": 0.11141406482323217,
  "skill_without_top10": 0.20958642330231236,
  "top20_share_of_net_gain": 0.19088013161761974,
  "skill_without_top20": 0.19650893199788666
 },
 "bootstrap_sensitivity": [
  {
   "model": "t0_cal",
   "reference": "best_simple_2023",
   "block_days": 1,
   "skill": 0.22710738685445464,
   "skill_lo95": 0.19600068113332608,
   "skill_hi95": 0.2549720236280575
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_2023",
   "block_days": 3,
   "skill": 0.22710738685445464,
   "skill_lo95": 0.19583721037033378,
   "skill_hi95": 0.25755585497496286
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_2023",
   "block_days": 7,
   "skill": 0.22710738685445464,
   "skill_lo95": 0.19410290210544054,
   "skill_hi95": 0.25967864186201384
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_2023",
   "block_days": 14,
   "skill": 0.22710738685445464,
   "skill_lo95": 0.18611648875703038,
   "skill_hi95": 0.25908681895186997
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_2023",
   "block_days": 30,
   "skill": 0.22710738685445464,
   "skill_lo95": 0.1818549013630248,
   "skill_hi95": 0.26509033873713567
  }
 ]
}
```

### X4-SLICES-P3: Experiment 4 slices of P3 (report-only, not adjusted)

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/slices/P3", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "each year": {
  "2024": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.2564917181607418,
   "days": 366
  },
  "2025": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.2473776358890113,
   "days": 365
  }
 },
 "each quarter (2025 Q4 is quarter-hour derived)": {
  "2024Q1": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.3569268657941327,
   "ci95": [
    0.264301586088666,
    0.42482865420372284
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2183,
   "loss_arm": 3.376219094332783,
   "loss_ref": 5.250132395131208,
   "days_won": 78,
   "days_lost": 13
  },
  "2024Q2": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.1545095582708027,
   "ci95": [
    0.12154103195186872,
    0.2267078633601407
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2184,
   "loss_arm": 5.91752494989734,
   "loss_ref": 6.99892589890764,
   "days_won": 64,
   "days_lost": 27
  },
  "2024Q3": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.23914143543108435,
   "ci95": [
    0.20296735345079922,
    0.2959070879051385
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 5.661658385700074,
   "loss_ref": 7.441144319519929,
   "days_won": 74,
   "days_lost": 18
  },
  "2024Q4": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.29088058722298904,
   "ci95": [
    0.18694052781053044,
    0.3688498755395645
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2209,
   "loss_arm": 6.467523100699704,
   "loss_ref": 9.120499289917868,
   "days_won": 73,
   "days_lost": 19
  },
  "2025Q1": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.3592483667667091,
   "ci95": [
    0.2780163125545024,
    0.4207894050434012
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 90,
   "hours": 2159,
   "loss_arm": 5.775708474304567,
   "loss_ref": 9.01395825580626,
   "days_won": 76,
   "days_lost": 14
  },
  "2025Q2": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.09315126892549297,
   "ci95": [
    0.045434536680793704,
    0.17972269714973774
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2184,
   "loss_arm": 5.85418528936896,
   "loss_ref": 6.455525699895342,
   "days_won": 59,
   "days_lost": 32
  },
  "2025Q3": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.22114516333738188,
   "ci95": [
    0.14263563566871273,
    0.2613585484915011
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 5.43015713353088,
   "loss_ref": 6.971975877814441,
   "days_won": 73,
   "days_lost": 19
  },
  "2025Q4": {
   "status": "ok",
   "arm": "t0_cal",
   "ref": "best_simple_eq",
   "skill": 0.27282529212390205,
   "ci95": [
    0.19752152320467636,
    0.3303291576100839
   ],
   "p_one_sided": 0.0004997501249375312,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2209,
   "loss_arm": 5.188723175016017,
   "loss_ref": 7.135456058656148,
   "days_won": 71,
   "days_lost": 21
  }
 },
 "April-September": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": 0.17985269011604454,
  "ci95": [
   0.1480204463896813,
   0.2171270548487039
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 366,
  "hours": 8784,
  "loss_arm": 5.7149526217007685,
  "loss_ref": 6.968202605589709,
  "days_won": 270,
  "days_lost": 96
 },
 "weekends and holidays": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": 0.2861842072921523,
  "ci95": [
   0.2256804485578134,
   0.3328777305131531
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 228,
  "hours": 5472,
  "loss_arm": 5.301911166391177,
  "loss_ref": 7.427562153365184,
  "days_won": 181,
  "days_lost": 47
 },
 "the weeks after each DST switch": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": -0.057968071097194374,
  "ci95": [
   -0.22904430402925957,
   0.15111731670977213
  ],
  "p_one_sided": 0.35082458770614694,
  "margin": 0.0,
  "m": -0.0,
  "days": 28,
  "hours": 672,
  "loss_arm": 6.799234943020911,
  "loss_ref": 6.4266920040125415,
  "days_won": 13,
  "days_lost": 15
 },
 "negative-price hours": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": 0.22335258468741526,
  "ci95": [
   0.1312280994706261,
   0.27750463583482726
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 163,
  "hours": 865,
  "loss_arm": 5.024644445990414,
  "loss_ref": 6.469659651114782,
  "days_won": 108,
  "days_lost": 55
 },
 "top 1% absolute prices": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": 0.049574347521223694,
  "ci95": [
   -0.005525164029999572,
   0.32957502654305576
  ],
  "p_one_sided": 0.03548225887056472,
  "margin": 0.0,
  "m": -0.0,
  "days": 45,
  "hours": 176,
  "loss_arm": 16.046323737664657,
  "loss_ref": 16.88330244013798,
  "days_won": 30,
  "days_lost": 15
 },
 "11:00-16:00 local": {
  "status": "ok",
  "arm": "t0_cal",
  "ref": "best_simple_eq",
  "skill": 0.2295079545628772,
  "ci95": [
   0.18551891555274688,
   0.26095442183135503
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 731,
  "hours": 3655,
  "loss_arm": 5.425332811193297,
  "loss_ref": 7.04138718020813,
  "days_won": 522,
  "days_lost": 209
 }
}
```

### X4-TABLES-P3: Experiment 4 concentration and bootstrap sensitivity of P3

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/tables/P3", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "status": "ok",
 "concentration": {
  "model": "t0_cal",
  "reference": "best_simple_eq",
  "net_gain_mw": 32251.439214329537,
  "n_days": 731,
  "skill": 0.2518851196137203,
  "top5_share_of_net_gain": 0.06938912890772826,
  "skill_without_top5": 0.24002377976955758,
  "top10_share_of_net_gain": 0.11899546161547851,
  "skill_without_top10": 0.23155877565951954,
  "top20_share_of_net_gain": 0.20192153392590478,
  "skill_without_top20": 0.21713585418193215
 },
 "bootstrap_sensitivity": [
  {
   "model": "t0_cal",
   "reference": "best_simple_eq",
   "block_days": 1,
   "skill": 0.2518851196137203,
   "skill_lo95": 0.222742990288081,
   "skill_hi95": 0.27975489283793514
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_eq",
   "block_days": 3,
   "skill": 0.2518851196137203,
   "skill_lo95": 0.22090088344004252,
   "skill_hi95": 0.28130806518599205
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_eq",
   "block_days": 7,
   "skill": 0.2518851196137203,
   "skill_lo95": 0.2195024302168609,
   "skill_hi95": 0.2823848776151179
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_eq",
   "block_days": 14,
   "skill": 0.2518851196137203,
   "skill_lo95": 0.21331719447156108,
   "skill_hi95": 0.28090523787558197
  },
  {
   "model": "t0_cal",
   "reference": "best_simple_eq",
   "block_days": 30,
   "skill": 0.2518851196137203,
   "skill_lo95": 0.21036877654644875,
   "skill_hi95": 0.28394560145480174
  }
 ]
}
```

### X4-SLICES-P4: Experiment 4 slices of P4 (report-only, not adjusted)

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/slices/P4", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "each year": {
  "2024": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.015140844864288572,
   "days": 209
  },
  "2025": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.03678561969496841,
   "days": 363
  }
 },
 "each quarter (2025 Q4 is quarter-hour derived)": {
  "2024Q1": {
   "status": "no days",
   "arm": "t0_cal_wx",
   "ref": "t0_cal"
  },
  "2024Q2": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": -0.017234703873192814,
   "ci95": [
    -0.05999024530465347,
    0.0009291948658141094
   ],
   "p_one_sided": 0.9695152423788106,
   "margin": 0.0,
   "m": -0.0,
   "days": 25,
   "hours": 600,
   "loss_arm": 17.534109513092037,
   "loss_ref": 17.237034330749513,
   "days_won": 11,
   "days_lost": 14
  },
  "2024Q3": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.005651867881568906,
   "ci95": [
    -0.03117942058236241,
    0.04548668650458319
   ],
   "p_one_sided": 0.4102948525737131,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 16.123833640140038,
   "loss_ref": 16.215481398641195,
   "days_won": 43,
   "days_lost": 49
  },
  "2024Q4": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.03233712898477592,
   "ci95": [
    -0.011989982177879888,
    0.0660004204370938
   ],
   "p_one_sided": 0.06446776611694154,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2209,
   "loss_arm": 17.18402334020709,
   "loss_ref": 17.758274968407605,
   "days_won": 58,
   "days_lost": 34
  },
  "2025Q1": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.06326501932569284,
   "ci95": [
    0.01439287599762902,
    0.11575841535388619
   ],
   "p_one_sided": 0.0029985007496251873,
   "margin": 0.0,
   "m": -0.0,
   "days": 90,
   "hours": 2159,
   "loss_arm": 15.037885038756619,
   "loss_ref": 16.053510703669485,
   "days_won": 53,
   "days_lost": 37
  },
  "2025Q2": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.026008643822732047,
   "ci95": [
    -0.022043843635339642,
    0.08371425385128978
   ],
   "p_one_sided": 0.15642178910544727,
   "margin": 0.0,
   "m": -0.0,
   "days": 91,
   "hours": 2184,
   "loss_arm": 15.779659896997305,
   "loss_ref": 16.20102662813096,
   "days_won": 41,
   "days_lost": 50
  },
  "2025Q3": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.010352279559111666,
   "ci95": [
    -0.014991829903228388,
    0.023921347021057675
   ],
   "p_one_sided": 0.3473263368315842,
   "margin": 0.0,
   "m": -0.0,
   "days": 92,
   "hours": 2208,
   "loss_arm": 15.108601191354834,
   "loss_ref": 15.266645776361663,
   "days_won": 49,
   "days_lost": 43
  },
  "2025Q4": {
   "status": "ok",
   "arm": "t0_cal_wx",
   "ref": "t0_cal",
   "skill": 0.04793304654068997,
   "ci95": [
    0.013359218196091474,
    0.08076908905230276
   ],
   "p_one_sided": 0.001999000499750125,
   "margin": 0.0,
   "m": -0.0,
   "days": 90,
   "hours": 2161,
   "loss_arm": 14.01422227819779,
   "loss_ref": 14.719786489046264,
   "days_won": 52,
   "days_lost": 38
  }
 },
 "April-September": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.011223231707229164,
  "ci95": [
   -0.008792555647639654,
   0.033269097365632876
  ],
  "p_one_sided": 0.1489255372313843,
  "margin": 0.0,
  "m": -0.0,
  "days": 300,
  "hours": 7200,
  "loss_arm": 15.825619309838613,
  "loss_ref": 16.005249938429724,
  "days_won": 144,
  "days_lost": 156
 },
 "weekends and holidays": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.018715075637679268,
  "ci95": [
   -0.014667920301534864,
   0.04099310140814884
  ],
  "p_one_sided": 0.1729135432283858,
  "margin": 0.0,
  "m": -0.0,
  "days": 178,
  "hours": 4273,
  "loss_arm": 15.092956722963896,
  "loss_ref": 15.380809740628512,
  "days_won": 85,
  "days_lost": 93
 },
 "the weeks after each DST switch": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.042652363580294894,
  "ci95": [
   -0.03613689472124904,
   0.10442054899789266
  ],
  "p_one_sided": 0.14142928535732133,
  "margin": 0.0,
  "m": -0.0,
  "days": 21,
  "hours": 505,
  "loss_arm": 19.14894826877708,
  "loss_ref": 20.002084446973143,
  "days_won": 14,
  "days_lost": 7
 },
 "negative-price hours": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.04593063383987295,
  "ci95": [
   -0.014831033274913374,
   0.09238106964392084
  ],
  "p_one_sided": 0.08845577211394302,
  "margin": 0.0,
  "m": -0.0,
  "days": 131,
  "hours": 689,
  "loss_arm": 12.034852491857698,
  "loss_ref": 12.614232170869029,
  "days_won": 67,
  "days_lost": 64
 },
 "top 1% absolute prices": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.038247814194595664,
  "ci95": [
   0.004238874896547207,
   0.10900511319839688
  ],
  "p_one_sided": 0.013993003498250875,
  "margin": 0.0,
  "m": -0.0,
  "days": 36,
  "hours": 138,
  "loss_arm": 41.32165589263474,
  "loss_ref": 42.96497216487277,
  "days_won": 23,
  "days_lost": 13
 },
 "11:00-16:00 local": {
  "status": "ok",
  "arm": "t0_cal_wx",
  "ref": "t0_cal",
  "skill": 0.0457685119536676,
  "ci95": [
   0.018903705768496867,
   0.0754478936207551
  ],
  "p_one_sided": 0.0004997501249375312,
  "margin": 0.0,
  "m": -0.0,
  "days": 572,
  "hours": 2860,
  "loss_arm": 14.913590021226788,
  "loss_ref": 15.628901590494008,
  "days_won": 292,
  "days_lost": 280
 }
}
```

### X4-TABLES-P4: Experiment 4 concentration and bootstrap sensitivity of P4

*Experiment:* EXP4 · *grade:* exploratory · *verification:* independently_reproduced · *source:* `{"path": "docs/experiment_4/scored_run/results.json", "pointer": "/tables/P4", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "status": "ok",
 "concentration": {
  "model": "t0_cal_wx",
  "reference": "t0_cal",
  "net_gain_mw": 6279.322442741395,
  "n_days": 572,
  "skill": 0.02842160653111203,
  "top5_share_of_net_gain": 0.28402273916059506,
  "skill_without_top5": 0.020702723811522494,
  "top10_share_of_net_gain": 0.4932612405418104,
  "skill_without_top10": 0.014937738434965375,
  "top20_share_of_net_gain": 0.8336842201897061,
  "skill_without_top20": 0.005060432649566571
 },
 "bootstrap_sensitivity": [
  {
   "model": "t0_cal_wx",
   "reference": "t0_cal",
   "block_days": 1,
   "skill": 0.02842160653111203,
   "skill_lo95": 0.01128603084136178,
   "skill_hi95": 0.04478583596333975
  },
  {
   "model": "t0_cal_wx",
   "reference": "t0_cal",
   "block_days": 3,
   "skill": 0.02842160653111203,
   "skill_lo95": 0.011952017640808379,
   "skill_hi95": 0.044597336397126174
  },
  {
   "model": "t0_cal_wx",
   "reference": "t0_cal",
   "block_days": 7,
   "skill": 0.02842160653111203,
   "skill_lo95": 0.012287948658350936,
   "skill_hi95": 0.04394780854276502
  },
  {
   "model": "t0_cal_wx",
   "reference": "t0_cal",
   "block_days": 14,
   "skill": 0.02842160653111203,
   "skill_lo95": 0.011445430256543909,
   "skill_hi95": 0.04412064234228268
  },
  {
   "model": "t0_cal_wx",
   "reference": "t0_cal",
   "block_days": 30,
   "skill": 0.02842160653111203,
   "skill_lo95": 0.010510269267357764,
   "skill_hi95": 0.04828795507109961
  }
 ]
}
```

### X4-RUN: Experiment 4 run record: selection on 2023, gates, data checks, provenance

*Experiment:* EXP4 · *grade:* process · *verification:* internal_consistency_only · *source:* `{"path": "docs/experiment_4/scored_run/run_meta.json", "pointer": "", "run_id": 36823477529, "commit": "2b407f4"}`

```json
{
 "selection": {
  "best": "blend_50",
  "mae": {
   "naive_std": 23.435707762557076,
   "prev_day": 22.748060502283106,
   "prev_week": 28.70798515981735,
   "mean_7d": 24.186711513372472,
   "median_7d": 24.24153424657534,
   "ewma": 23.349127120938057,
   "blend_50": 21.42124690150033,
   "weekday_mean_4w": 31.64853852739726
  },
  "days": 365,
  "windows": {
   "built": 365,
   "incomplete_target": 0,
   "incomplete_days": []
  },
  "dropped_by_candidate": {
   "naive_std": [],
   "prev_day": [],
   "prev_week": [],
   "mean_7d": [],
   "median_7d": [],
   "ewma": [],
   "blend_50": [],
   "weekday_mean_4w": []
  },
  "dropped_count": {
   "naive_std": 0,
   "prev_day": 0,
   "prev_week": 0,
   "mean_7d": 0,
   "median_7d": 0,
   "ewma": 0,
   "blend_50": 0,
   "weekday_mean_4w": 0
  }
 },
 "k1": {
  "attempts": 3,
  "passed": false,
  "lear_sha256": "7770361a7b69f20b66cc93577f9f6b024ef80932ac0a41247d358054d009d19a",
  "passing_attempt": null,
  "over_budget": false,
  "log_present": true,
  "log_sha256": "b111286d051e40fbe74367136180a3fcf56300071fd3295bf4f980a9f64ff5e4"
 },
 "k3": {
  "period": [
   "2023-10-02",
   "2023-12-03"
  ],
  "days": 63,
  "conventions": {
   "instant": {
    "convention": "instant",
    "pass": true,
    "checks": {
     "planted_helps": true,
     "decoy_does_not_help": true,
     "decoy_does_not_break": true,
     "aligned": true,
     "no_sanitised_output": true
    },
    "planted_ratio": 0.3048781127799486,
    "decoy_ratio": 0.997018772952114,
    "shift_penalty": 1.3012170162076073,
    "mae": {
     "t0_cal": 21.280842924653815,
     "k3_oracle_planted": 6.488063229234976,
     "k3_oracle_decoy": 21.217399900125024,
     "k3_oracle_shift_m1h": 8.442378276111429,
     "k3_oracle_shift_p1h": 8.891922251921336
    },
    "arms": [
     "t0_cal",
     "k3_oracle_planted",
     "k3_oracle_decoy",
     "k3_oracle_shift_m1h",
     "k3_oracle_shift_p1h"
    ],
    "days_scored": 63,
    "days_dropped": [],
    "p99": 210.86759999999893,
    "sd": 43.994060920550226,
    "noise_sd": 10.543379999999948,
    "scale_hours": 1513,
    "grid": {
     "first": "2023-07-03 22:00:00+00:00",
     "last": "2023-12-04 01:00:00+00:00",
     "stamps": 3676
    },
    "port": "instant_to_slots",
    "missing": {
     "t0_cal": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_planted": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_decoy": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_shift_m1h": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_shift_p1h": {
      "context": [],
      "sanitised": []
     }
    },
    "non_finite_warnings": 0
   },
   "mean_preceding_hour": {
    "convention": "mean_preceding_hour",
    "pass": true,
    "checks": {
     "planted_helps": true,
     "decoy_does_not_help": true,
     "decoy_does_not_break": true,
     "aligned": true,
     "no_sanitised_output": true
    },
    "planted_ratio": 0.30120379606806524,
    "decoy_ratio": 0.9942939092904666,
    "shift_penalty": 1.457356907580933,
    "mae": {
     "t0_cal": 21.280842924653815,
     "k3_oracle_planted": 6.409870672433957,
     "k3_oracle_decoy": 21.159412504550406,
     "k3_oracle_shift_m1h": 9.341469301172067,
     "k3_oracle_shift_p1h": 9.547302675114825
    },
    "arms": [
     "t0_cal",
     "k3_oracle_planted",
     "k3_oracle_decoy",
     "k3_oracle_shift_m1h",
     "k3_oracle_shift_p1h"
    ],
    "days_scored": 63,
    "days_dropped": [],
    "p99": 210.86759999999893,
    "sd": 43.994060920550226,
    "noise_sd": 10.543379999999948,
    "scale_hours": 1513,
    "grid": {
     "first": "2023-07-03 22:00:00+00:00",
     "last": "2023-12-04 01:00:00+00:00",
     "stamps": 3676
    },
    "port": "hourly_to_slots",
    "missing": {
     "t0_cal": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_planted": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_decoy": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_shift_m1h": {
      "context": [],
      "sanitised": []
     },
     "k3_oracle_shift_p1h": {
      "context": [],
      "sanitised": []
     }
    },
    "non_finite_warnings": 0
   }
  },
  "pass": true
 },
 "k2_record": {
  "run_id": "36823477529",
  "commit": "2b407f42c03d2734ef4170cfb3e66962dbba9552",
  "pass": true
 },
 "leak_check": {
  "pass": true,
  "checks": 459,
  "checks_true": 459,
  "detail": "every control of PRICE_SPEC leak_controls at the 11 TEST_ORIGINS and P4's first day; full record in run_meta.json /leak_check"
 },
 "prices": {
  "stamp": "start",
  "hourly": {
   "hours": 53352,
   "grid_hours": 53352,
   "native_hours": 51143,
   "hours_from_quarters": 2209,
   "incomplete_quarter_hours": 0,
   "off_grid_hourly": 0,
   "off_grid_quarter": 0
  },
  "first": "2019-11-30 23:00:00+00:00",
  "last": "2025-12-31 22:00:00+00:00"
 },
 "agreement": {
  "hours": 34992,
  "hours_differing": 0,
  "missing_a": 0,
  "missing_b": 0,
  "share_agreeing": 1.0,
  "max_abs_diff": 0.0,
  "first_mismatches": [],
  "region": "DE",
  "not_cross_checked": [
   "2025-12-29",
   "2025-12-30",
   "2025-12-31"
  ],
  "day_2024_06_26": {
   "energy_charts": [
    107.43,
    99.96,
    95.32,
    95.46,
    91.7,
    97.12,
    109.59,
    130.0,
    121.1,
    101.76,
    90.98,
    85.99,
    79.41,
    77.24,
    80.62,
    90.59,
    100.08,
    105.96,
    114.98,
    145.0,
    156.98,
    137.18,
    118.98,
    110.0
   ],
   "smard": [
    107.43,
    99.96,
    95.32,
    95.46,
    91.7,
    97.12,
    109.59,
    130.0,
    121.1,
    101.76,
    90.98,
    85.99,
    79.41,
    77.24,
    80.62,
    90.59,
    100.08,
    105.96,
    114.98,
    145.0,
    156.98,
    137.18,
    118.98,
    110.0
   ]
  }
 },
 "licence": {
  "files": 73,
  "refusals": [],
  "seen": [
   "CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur | SMARD.de"
  ]
 },
 "weather": {
  "wx_temperature": {
   "cells": 16655,
   "first": "2024-02-06 00:00:00+00:00",
   "last": "2025-12-30 22:00:00+00:00"
  },
  "wx_radiation": {
   "cells": 15889,
   "first": "2024-03-08 22:00:00+00:00",
   "last": "2025-12-30 22:00:00+00:00"
  }
 },
 "t0_weights": {
  "repo_id": "theforecastingcompany/t0-alpha",
  "frozen_revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b",
  "served_by_revision": "fdd189642a529fee59ba7d491235a06779e41a83",
  "sha256": {
   "config.json": "b2b545685283c579b99c774da0d7f07525683efca2b27dc4ffec99c109d5beba",
   "model.safetensors": "16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f"
  },
  "verified": true,
  "event": "docs/experiment_4/RETRIEVAL_EVENTS.md"
 },
 "missing_by_arm": {
  "best_simple_2023": {
   "metric": "mae",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "best_simple_2023_strict": {
   "metric": "mae",
   "over": "the strict windows' complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "best_simple_eq": {
   "metric": "pinball",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "naive_std": {
   "metric": "mae",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "prev_week": {
   "metric": "mae",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "t0": {
   "metric": "mae",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "t0_cal": {
   "metric": "mae",
   "over": "the complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "t0_cal_strict": {
   "metric": "mae",
   "over": "the strict windows' complete test days",
   "days": 731,
   "missing": 0,
   "by_cause": {}
  },
  "t0_cal_wx": {
   "metric": "mae",
   "over": "the complete test days from AVAIL.p4_first_day to the end of periods.p4_days",
   "days": 574,
   "missing": 2,
   "by_cause": {
    "weather_p4.day_rule: horizon": [
     "2025-12-30",
     "2025-12-31"
    ]
   }
  }
 },
 "amendments": {
  "ids": [
   "A1"
  ],
  "record": "docs/experiment_4/AMENDMENTS.md",
  "sha256": "354f8e4c2bf962bc7812a1b40b1562bf7e2caf119c2604a0a05a2c26e6e56654"
 },
 "versions": {
  "python": "3.11.16",
  "numpy": "2.4.6",
  "pandas": "2.3.3",
  "scikit-learn": "1.7.2",
  "torch": "2.14.0+cpu",
  "tfc-t0": "0.3.2",
  "huggingface-hub": "1.31.0"
 },
 "forecast": {
  "windows": {
   "built": 731,
   "incomplete_target": 0,
   "incomplete_days": []
  },
  "strict_windows": {
   "built": 731,
   "incomplete_target": 0,
   "incomplete_days": []
  },
  "t0_missing": {
   "t0": {
    "context": [],
    "sanitised": []
   },
   "t0_cal": {
    "context": [],
    "sanitised": []
   },
   "t0_cal_strict": {
    "context": [],
    "sanitised": []
   },
   "t0_cal_wx": {
    "context": [],
    "sanitised": []
   }
  },
  "p4_days": {
   "candidates": 574,
   "kept": 572,
   "dropped": {
    "horizon": [
     "2025-12-30",
     "2025-12-31"
    ],
    "context": []
   }
  }
 }
}
```

### X4-K1: K1: the LEAR reproduction gate, all three attempts (failed)

*Experiment:* EXP4 · *grade:* process · *verification:* not_independently_verified · *source:* `{"path": "docs/experiment_4/k1_attempts.jsonl"}`

```json
[
 {
  "attempt_number": 1,
  "commit": "d861b789bca431e518a6fc5f5ae9ddc473043d8f",
  "counts_as_attempt": true,
  "deviation": {
   "LEAR 1092": 0.00017091946394209856,
   "LEAR 1456": 0.000180887997706769,
   "LEAR 56": -0.015952197239052057,
   "LEAR 84": -0.003648333607256582,
   "LEAR Ensemble": 0.0022449087339100338
  },
  "every_hour_forecast": true,
  "failed_checks": [
   "mean_abs_diff_ensemble"
  ],
  "hours": 17472,
  "lear_sha256": "3abae2133014a49b06bceba28e84dbca8077651afeb052b8eccd58fa4fefc2c1",
  "mae": {
   "LEAR 1092": 4.250638766829028,
   "LEAR 1456": 4.378891109968896,
   "LEAR 56": 4.6059383246520555,
   "LEAR 84": 4.558674385173135,
   "LEAR Ensemble": 3.9887065986985473
  },
  "mean_abs_diff_ensemble": 0.5484358717400079,
  "pass": false,
  "run_id": "36697501545",
  "smoke": false,
  "source": "https://github.com/xuanhuyle/solar/actions/runs/36697501545 (k1_attempt.json)",
  "status": "fail"
 },
 {
  "attempt_number": 2,
  "change_from_attempt_1": "design columns hour-major as the reference (d799add)",
  "commit": "d799addf1d10088233841e7261957774579e34bc",
  "counts_as_attempt": true,
  "deviation": {
   "LEAR 1092": 0.0014373908920322087,
   "LEAR 1456": 0.002094571383769006,
   "LEAR 56": -0.015978371855917883,
   "LEAR 84": -0.003646292224490977,
   "LEAR Ensemble": 0.0025548362159437676
  },
  "every_hour_forecast": true,
  "failed_checks": [
   "mean_abs_diff_ensemble"
  ],
  "hours": 17472,
  "lear_sha256": "c36ad5deaf824a655472bc144d851feccecb7ed2ccc370ff7bc2a29efeaf6ebf",
  "mae": {
   "LEAR 1092": 4.256021159422692,
   "LEAR 1456": 4.387269405602297,
   "LEAR 56": 4.605815811629196,
   "LEAR 84": 4.5586837252481685,
   "LEAR Ensemble": 3.9899400395291598
  },
  "mean_abs_diff_ensemble": 0.5582843751350908,
  "pass": false,
  "run_id": "36712555696",
  "smoke": false,
  "source": "https://github.com/xuanhuyle/solar/actions/runs/36712555696 (k1_attempt.json)",
  "status": "fail"
 },
 {
  "amendments": [
   "A1"
  ],
  "attempt_number": 3,
  "change_from_attempt_2": "amendment A1: the LEAR penalty as scikit-learn <= 0.23.1 chose it (62bcf38)",
  "commit": "62bcf386134f2cb1dfc0f5a57f967dad30cfb7de",
  "counts_as_attempt": true,
  "deviation": {
   "LEAR 1092": 0.0014373908920313205,
   "LEAR 1456": 0.002094571383769006,
   "LEAR 56": 0.005321415588567691,
   "LEAR 84": 0.003627650723788678,
   "LEAR Ensemble": 0.0008741525317936816
  },
  "every_hour_forecast": true,
  "failed_checks": [
   "mean_abs_diff_ensemble"
  ],
  "final": "the last attempt of gates.K1.attempts; final regardless of outcome (owner, 2026-09-30)",
  "hours": 17472,
  "lear_sha256": "7770361a7b69f20b66cc93577f9f6b024ef80932ac0a41247d358054d009d19a",
  "mae": {
   "LEAR 1092": 4.256021159422689,
   "LEAR 1456": 4.387269405602297,
   "LEAR 56": 4.705511687197682,
   "LEAR 84": 4.591964682681186,
   "LEAR Ensemble": 3.9832513010353288
  },
  "mean_abs_diff_ensemble": 0.4075611835746456,
  "pass": false,
  "run_id": "36780460835",
  "smoke": false,
  "source": "https://github.com/xuanhuyle/solar/actions/runs/36780460835 (k1_attempt.json)",
  "status": "fail"
 }
]
```

### X4-A1: Amendment A1 and the unexplained long-window difference L1

*Experiment:* EXP4 · *grade:* process · *verification:* not_applicable · *source:* `{"path": "docs/experiment_4/AMENDMENTS.md"}`

````text
# Experiment 4: amendments

The frozen specification (`solarbench/price_spec.py`, `PRICE_SPEC_SHA256`) and the one-pager are unchanged.
An amendment is an owner-approved change to how one frozen rule is carried out. It is recorded here, beside the
frozen text and never inside it, following the specification's convention for owner decisions ("reported as an
amendment", "never a silent edit", "reported as amended"). It is named in each command's meta file
(`k1_attempt.json`, `smoke.json`, `check.json`, `run_meta.json`), in the K1 attempt record and in `summary.md`.
This file's sha256 is pinned by `tests/test_price_spec.py`.

## A1 (2026-09-30): the LEAR penalty is chosen as scikit-learn ≤ 0.23.1 chose it

**Owner's approval (2026-09-30), verbatim:** "Approve “Amend, use attempt 3.” Make the amendment narrowly reproduce
the verified 2020 scikit-learn behaviour, document the independent evidence and historical cause, change no
thresholds or other Experiment 4 rules, and treat attempt 3 as final regardless of outcome."

**Superseded frozen text:** `PRICE_SPEC["lear"]["penalty"]`, step (1) only:

> (1) alpha_h = LassoLarsIC(criterion='aic', fit_intercept=True, max_iter=2500, noise_variance=np.var(y_h, ddof=0))
> fitted on X with each column centred on its mean and divided by the L2 norm of the centred column (a zero-norm
> column is divided by 1): scikit-learn < 1.2's LassoLarsIC with its default normalize=True, whose criterion
> n*MSE/var(y) + 2*df has the same argmin

**Replacement for step (1):**

> (1) alpha_h = the penalty that scikit-learn 0.22's LassoLarsIC(criterion='aic', max_iter=2500) (normalize=True,
> precompute='auto') selects on X. This is the behaviour of every release from 0.22 to 0.23.1, the releases the
> toolbox could use when the published EPF forecasts were made. It works as follows: each column is centred and divided by the L2 norm of the centred column (a zero norm is
> replaced by 1); y_h is centred; the lasso LARS path is computed (Gram 'auto', eps = machine epsilon,
> max_iter 2500); and alpha_h is the path point minimising n*MSE/(var(y_h) + eps) + 2*df. When the training rows
> number no more than the columns, the MSE is computed on the design as LARS leaves it (its columns permuted in
> place), as 0.22 does.

Steps (2) and (3) of the penalty, and every other rule, stay as frozen.

**Historical cause.**
- Every scikit-learn release from at least 0.18.2 to 0.23.1 has the same flaw. `lars_path` with `Gram='auto'` does not copy X when
  n_samples ≤ n_features, and swaps its columns in place as variables enter and leave the path. `LassoLarsIC.fit`
  then scores every path point with `y - X @ coef_path_`, pairing coefficients in the original column order with the
  permuted matrix. The set of candidate penalties is the same; the AIC's choice among them can differ.
- The 0.23.2 release fixed it (2020-08-03; changelog `doc/whats_new/v0.23.rst`: "linear_model.lars_path does not
  overwrite X when X_copy=True and Gram='auto'", PR #17914).
- The published LEAR forecasts that K1 compares with (`epftoolbox forecasts/Forecasts_FR_DNN_LEAR_ensembles.csv`)
  were first committed on 2020-06-25 (epftoolbox d8dad5b). Their values are unchanged since, to within 6e-14 (at most 4e-16 relative; float formatting only). At that
  date the toolbox required `scikit-learn>=0.22` and imported `sklearn.utils._testing` (0.22 onwards). No fixed
  release existed yet.
- The frozen step (1) describes the corrected computation (0.23.2 onwards). Its claim that the two share "the same
  argmin" does not hold in general for the releases that made the published forecasts when a window has no more
  training rows than columns.

**Independent evidence** (none of it uses EPF-FR data or any K1 number; audit `wf_ec1b4a41-118`, 9 agents, each
lens checked by a skeptic):
- The real released wheels on a known-answer case, `RandomState(0)`, x 49×247,
  y = x0 − 2·x3 + 0.5·x100 + N(0, 0.5):

  | computation | penalty (12 significant digits) |
  |---|---|
  | scikit-learn 0.22.2.post1 and 0.23.1 | 0.269903704353 |
  | scikit-learn 0.23.2, and the frozen step (1) on 1.7.2 | 0.0335489881715 |
  | this amendment on 1.7.2 | 0.269903704353 |

  The last one or two digits of the full doubles depend on the BLAS kernel. With the audit container's default
  OpenBLAS kernel, the real 0.22.2.post1 and 0.23.1 wheels give 0.26990370435295313, bit-identical to this
  amendment, and 0.23.2 gives 0.03354898817147152. With OPENBLAS_CORETYPE=Prescott they give 0.2699037043529531
  and 0.03354898817147161.

- With more rows than columns (60×30, 300×247), all of them agree to 1e-14 relative.
- On synthetic designs built with our own `features` and `InvariantScaler`, the amendment reproduces the real
  0.22.2.post1:
  - 34,944 short-window fits: forecasts equal to within 9.8e-12;
  - 960 of 960 penalties equal in both column orders;
  - long windows unchanged (≤ 1.3e-11 relative).
- An independent pre-flight check (`wf_192709f5-d27`) repeated this against the real 0.22.2.post1 and 0.23.1
  wheels on 35,136 fits of K1-shaped (247-column) and Experiment 4-shaped (104-column) designs: the same path point
  in every fit (relative alpha difference ≤ 3.4e-11), and forecasts equal to within 7e-11 EUR/MWh.
- Where it acts, and where it doesn't:
  - It acts only when a calibration window has no more training rows than columns: windows 56 and 84 (49 and 77
    rows). That is 247 columns in K1 and 104 in Experiment 4's `lear_ens`.
  - Windows 1092 and 1456 use a Gram matrix; X is never touched there, and nothing changes.

**Consistency with the logged attempts** (K1 numbers, not part of the evidence above). In attempts 1 and 2 the MAE
deviations were largest in the 56- and 84-day windows (−1.60% and −0.36%, unchanged by the column reorder),
consistent with A1's mechanism. The long windows also departed (+0.02% / +0.02% in attempt 1, +0.14% / +0.21% in
attempt 2); A1 does not address that (L1, below).

**What A1 changes.** Only `solarbench/lear.py::aic_alpha`, and so the penalty of the 56- and 84-day windows:
- in K1;
- in Experiment 4's `lear_ens` (and `lear_ens_eq`, its bands), because `lear.scored_only_if` requires the scored
  `lear.py` to be the one K1 validated. There is no K1-only switch.

**What A1 does not change:**
- no threshold or tolerance of K1 or of any probe;
- no feature, lag or column order (the hour-major order of 47d6e06 stays);
- no window, transform, or Lasso refit (penalty steps 2 and 3);
- no other rule of Experiment 4;
- the long windows.

**K1 under A1.** Attempt 3 (the last of `gates.K1.attempts`) runs the amended `lear.py`, and is final regardless of
its outcome.
- If it passes, P2 is scored and reported as amended (A1).
- If it fails, K1 has failed and P2 reads "not runnable", as the frozen rules say.

An unexplained difference in the long windows (audit finding L1) may remain. It has no fix within the
specification and is reported with the result.

**Outcome (2026-09-30).** Attempt 3 ran the amended `lear.py` (sha256 `7770361a…`) at commit 62bcf38 in Actions run
[36780460835](https://github.com/xuanhuyle/solar/actions/runs/36780460835).
- Every hour was forecast. Every MAE tolerance passed: 56 +0.53%, 84 +0.36%, 1092 +0.14%, 1456 +0.21%, ensemble +0.09%.
- The mean absolute difference from the published ensemble forecasts was 0.408 EUR/MWh (attempt 2: 0.558), above the
  0.25 limit.
- As predicted, A1 moved the short windows (−1.60% / −0.36% → +0.53% / +0.36%) and left the long windows unchanged.
- The attempt is final. K1 has failed, so `lear_ens` and `lear_ens_eq` are not scored: P2 reads "not runnable" and the
  LEAR secondaries read "not run", as the frozen rules say.
- A1 therefore affects no scored arm of Experiment 4. It stays recorded because the K1 attempt it governed counts.
````

### X4-T0FETCH: Retrieval event: t0's frozen revision vanished upstream; weights loaded by content

*Experiment:* EXP4 · *grade:* process · *verification:* not_applicable · *source:* `{"path": "docs/experiment_4/RETRIEVAL_EVENTS.md"}`

````text
# Experiment 4: retrieval events

A record of events that changed *how* a frozen input is fetched, never *what* it is. The frozen specification
(`solarbench/price_spec.py`) and the one-pager are unchanged by every event listed here.

## 2026-09-29: t0-alpha's frozen revision id vanished upstream; the frozen bytes are unchanged

**What happened.** The frozen specification pins t0-alpha at `theforecastingcompany/t0-alpha` revision
`9b02c5f4bb6c89ba15d9fa74554018fe6464220b`. The engine loaded that revision on 2026-09-28. On 2026-09-29 the
Hugging Face Hub answered `RevisionNotFoundError` ("Invalid rev id") for it
([Actions run 36646007553](https://github.com/xuanhuyle/solar/actions/runs/36646007553)). The token was
valid (account `xuanhuyle`). The repository's history had been rewritten upstream: its commit list no longer
contains that revision, and its head is `fdd189642a529fee59ba7d491235a06779e41a83` (2026-09-24, "Cite the t0
arXiv paper").

**The bytes are the same.** [Actions run 36646852265](https://github.com/xuanhuyle/solar/actions/runs/36646852265)
restored the benchmark workflow's cached snapshot of the frozen revision (read-only) and compared it with the
Hub head:

| file | sha256 (frozen revision's snapshot) | bytes | Hub head `fdd18964` |
|---|---|---|---|
| `config.json` | `b2b545685283c579b99c774da0d7f07525683efca2b27dc4ffec99c109d5beba` | 250 | identical |
| `model.safetensors` | `16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f` | 406,601,492 | identical |

The Hub's last change to the weights is dated 2026-06-11 ("update weights").

**Owner's decision (2026-09-30).** Keep the frozen Experiment 4 specification unchanged. Record the upstream
history rewrite as a retrieval event (this entry). Pin the SHA-256 hashes of the previously frozen
`config.json` and `model.safetensors`. Fetch from the current Hugging Face repository and permit loading only
when both files match those hashes exactly. Any mismatch aborts before forecasting.

**How it is enforced.** `solarbench/t0_pinned.py` holds the two hashes, fetches both files from the
repository's current head, and builds the model only from the verified local files; a mismatch or a missing
file raises before any forecast (`tests/test_t0_pinned.py`). Every command that loads t0 writes the retrieval
record (frozen revision, the head that served the bytes, both sha256) to its `run_meta` under `t0_weights`.

**Not covered here.** The engine (`engine/catalogue.py`) and the earlier experiments' workflows still load t0
by the vanished revision id. Batch B1's vault scoring is affected; its fix is a separate, owner-approved change
made before 2027-04-01. Experiment 4 edits none of those files.
````

### X4-REPLICATION: Independent replication of Experiment 4's statistics (2026-10-01)

*Experiment:* EXP4 · *grade:* process · *verification:* not_applicable · *source:* `{"path": "docs/experiment_4/INDEPENDENT_REPLICATION.md"}`

````text
## Summary

- **Verdict: independently reproduced, with no defect found.**
  - **What the analyst worked from:** the run's original hourly forecasts, the frozen specification text and
    written descriptions of the functions that text names. It never saw the run's code or published results.
  - **What it reproduced:** every computed primary skill, interval, p-value and Holm adjustment; the states of P1,
    P3 and P4; P3's coverage; P4's concentration; and every carry-forward decision.
  - **Independence is partial (section 8):**
    - P4's day list was taken from the run's record;
    - P2's "not runnable" state, which enters Holm at p = 1, was supplied from the recorded K1 failure;
    - M, and so the carry-forward decisions, match only conditionally on the engine code's formula, which was
      supplied as a written statement;
    - the blinding was procedural.
- **Comparison:** 614 published fields were compared:
  - 520 matched exactly;
  - 90 matched within the Monte-Carlo tolerance fixed in advance (2 of them, in the two short slices, only by
    coincidence);
  - 4 disagreed, and all 4 are explained below.
- **Discrepancies:** the 4 disagreements sit in two report-only P4 slices of 25 and 21 days.
  - **Cause:** the specification does not settle the block length the bootstrap should use on series that short.
    With the same block length, the two implementations agree.
  - **Effect:** they are not defects and change no state, decision or qualitative reading. One printed detail
    depends on the block length (section 5).
- **Re-execution of the frozen code:** run on the same forecasts, it reproduces the published `results.json`,
  `summary.md` and every per-day table byte for byte. This check is not independent.
- **Limits.** These could not be re-derived from the artifact, and remain checked for internal consistency only or
  not independently verified (sections 3, 4 and 8):
  - forecast generation itself;
  - the gates (K1–K3) and the leak check;
  - P4's day set and the other AVAIL outcomes;
  - the 2023 rule selection;
  - the per-row provenance columns;
  - the source prices;
  - the engine formula behind M.

## 3. Checked for internal consistency only

These depend on information that is not in the artifact. They were checked against the run's own records, not
re-derived.
- **P4's day set.** It is 572 days, from 6 June 2024 to 29 December 2025, with 2 days dropped by the horizon rule.
  - The rule that picks these days needs the weather issue times, which the artifact does not hold.
  - The `t0_cal_wx` days equal the run's recorded list, and every weather issue time the run recorded per row is
    at or before 12:00 D-1 Paris.
  - The list itself was taken from the run.
- **The choice of `best_simple_2023` (blend_50).** It needs the 2023 forecasts, which are not in the artifact.
  - The README and the run record show it was chosen on 2023 by the frozen rule.
  - The 2023 MAEs were not recomputed.
- **P2 "not runnable".** It follows from K1 having failed. That failure is recorded in `k1_attempts.jsonl`, all
  three attempts, and in the run's metadata. LEAR's forecasts are not in the artifact.
- **Point in time.** The per-row provenance columns (`source_latest`, `cov_issued_latest`) are the run's own
  records. They respect the publication and issue-time rules on every row, but the columns themselves were not
  re-derived from the data sources.

## 4. Not independently verified

- **The forecasts themselves.** No forecast was rerun, by design. Nothing here shows that t0, the simple rules or
  the empirical bands would produce these numbers again. What is shown is that the published statistics follow
  from the forecasts the run recorded.
- **The source prices beyond the run's own cross-check.** The run found Energy-Charts identical to SMARD on all
  34,992 hours of 2022–2025 that it compared. That check was not repeated.
- **The AVAIL outcomes** supplied to the analyst: P4's first day and the price stamp convention.
- **The gates and the leak check:** K1 (failed), K2 and K3 (passed), and the in-run leak check (459 of 459 passed).
  Their inputs are not in the artifact.
- **219 published fields outside the pre-declared comparison.** None is a computed primary value or a state; the
  P2 primary's fields appear only as "not run" placeholders.
  - **201 have no blind counterpart:**
    - slice days won and lost;
    - the slice margins;
    - "not run" placeholders (P2's primary and verdict fields, and the per-year values of the secondaries that
      involve lear_ens);
    - the rMAE day counts;
    - the verdict thresholds;
    - P2's carry-forward placeholders.
  - **18 are block-length sensitivity endpoints:** the blind computed them but gave no seed spread, so they were
    compared at seed 0 directly instead (section 2).

## 5. Discrepancies

There are 4, all in report-only slices of P4, and all of class (b): **the specification does not determine the
value.**

| Field | Published | Blind |
|---|---|---|
| P4, slice 2024Q2 (25 days): interval upper end | 0.00093 | 0.0095 |
| P4, slice 2024Q2: one-sided p | 0.9695 | 0.9480 |
| P4, slice "the weeks after each DST switch" (21 days): interval lower end | −0.0361 | −0.0231 |
| P4, the same slice: one-sided p | 0.1414 | 0.2684 |

- **Cause.** The specification prescribes `metrics.bootstrap_skill(..., block_days=14, ...)` and says "14-day
  blocks".
  - For a series shorter than 28 days, that function shortens the block to `n_days // 2`: 12 and 10 days here. The
    run logged both cases as "indicative only".
  - The specification's text and the function's docstring do not mention this. The analyst therefore used literal
    14-day blocks.
  - With the same block length, both implementations agree.
    - `replication/short_series_same_block.json`: with 12- and 10-day blocks, the blind bootstrap reproduces the
      published intervals within 1.2e-13 relative and the p-values exactly.
    - `compare_blind.json` (`short_series_diagnosis`): the frozen call reproduces the published values bit for bit.
- **Classification.** One skeptic reviewed each discrepancy independently, with full access to the code; their
  verdicts are recorded in `replication/discrepancy_review.json`. All four concluded class (b), not a defect:
  - the published values are exactly what the specification's named call produces;
  - that function's behaviour predates the freeze (commit `0a32dc1`).
- **Materiality.**
  - None changes a state, a Holm decision, the coverage band or carry-forward candidacy.
  - Both slices' skills, days and hours agree exactly.
  - Under either block length both slices' intervals include 0 and neither is significant, so their qualitative
    readings stand.
  - One published detail does depend on the shortened block. The fact sheet says the 2024Q2 interval "only just
    includes 0", and the README prints it as −1.7% [−6.0%, +0.1%]. With literal 14-day blocks its upper end is
    +0.95% (p 0.948).

**No class (d) discrepancy was found:** no case where a published value fails to follow the specification. Phase B
of the owner's task may therefore proceed.

## 6. Monte-Carlo robustness (Track 3, report-only)

`replication/mc_tolerance.py` reran the frozen bootstrap with seeds 0–199. The frozen seed is 0, and nothing here
changes a state.

| Primary | Seed-0 lower bound | Its position among 200 seeds | Lower bound above 0 in every seed? | Draws ≤ 0 across seeds |
|---|---|---|---|---|
| P1 | 0.1861 | rank share 0.05 | yes | 0 in every seed |
| P3 | 0.2133 | rank share 0.06 | yes | 0 in every seed |
| P4 | 0.01145 | rank share 0.32 | yes | 0 to 3 |

- **Holm.** The largest Holm-adjusted p for P1, P3 or P4 under any seed is 0.004, against the 0.05 threshold.
- **No seed changes any primary's state.**
- **Seed 0 is not a lucky draw.** For P1 and P3 its lower bounds sit near the low end of the seed spread, so the
  published intervals are slightly conservative there.

## 7. What this means for reading Experiment 4

- **The arithmetic is verified.** The published figures follow from the run's recorded forecasts under the frozen
  rules. An independent implementation reproduces them, and the frozen code reproduces them byte for byte. The
  earlier caveat, that "the bootstrap intervals and p-values are the run's own", no longer applies to the primaries,
  the secondaries, coverage, concentration or carry-forward.
- **What is not changed: the scientific status.**
  - Experiment 4 remains **discovery-grade**. The 2024–2025 prices are public and already studied, and 2025 was
    used before. Replicating the arithmetic does not make any result confirmed.
  - The P4 result remains small and concentrated: +2.8%, with the best 20 of 572 days carrying 83% of the net gain.
  - In April–September it is not distinguishable from zero.
  - It is not a candidate for the forward vault.
- **Where the remaining risk is:** in what could not be re-derived here. These rest on the run's own checks and the
  earlier reviews:
  - forecast generation;
  - the gates and the leak check;
  - P4's day set and the other AVAIL outcomes;
  - the 2023 rule selection;
  - the per-row provenance columns;
  - the source prices;
  - the engine formula behind M.

## 8. Limits of this replication

- **The blinding was procedural.** The analyst worked in the same file system, under instructions to read only its
  packet, and it listed every file it read: the four packet files.
  - It reported one slip: a scratch script written just outside the packet folder, then deleted. That script ran
    only its own functions on synthetic data. The slip is self-reported and cannot be checked from `files_read`.
  - Nothing indicates it saw a published value.
  - Its outputs were frozen before the comparison ran: `compare_blind.json` records their sha256 (`6109823b…`),
    which matches the committed `blind_outputs.json`.
  - They were committed in the same commit as the comparison (`24af212`), not separately before it. That they
    predate the comparison rests on the session's file times, not on commit order.
- **Independence is partial in three places:**
  - **M and block_sd** rest on the code's `power_table` and `blocks` rules (calendar 14-day blocks, at least 10 days
    per block, daily mean loss). They were supplied as a written statement of the code's formula, not taken from
    the specification's text.
  - **P4's day list**, and with it its first day (6 June 2024), was supplied from the run.
  - **P2's state was supplied.** The packet stated that K1 failed, so P2 is "not runnable" and enters Holm with
    p = 1. The 4 P2 fields counted as exact are echoed inputs, not reproductions.
- **K3 was inferred, not verified.** P4's "won" also assumes K3 passed; the analyst inferred this from `t0_cal_wx`
  having been scored (its assumption 9). K3 itself is not verified (section 4).
- **The packet's description of `bootstrap_skill` omitted the short-series block reduction.** That omission is the
  sole cause of the four class (b) discrepancies, which lie in report-only slices.
````

### DESIGN-1A-2: Experiments 1A and 2: pre-registration drafts

*Experiment:* DESIGN · *grade:* design_only · *verification:* not_applicable · *source:* `{"branch": "experiment-1a-preregistration"}`

```json
{
 "status": "design only: draft pre-registrations of a referee certification on synthetic data (1A) and a blinded synthetic knowledge-creation benchmark (2); nothing ran, nothing was frozen",
 "where": "branch experiment-1a-preregistration, docs/experiment_1a/ and docs/experiment_2/ (draft PR #2)"
}
```

### R-LIMITS-5: Known limitations

*Experiment:* LIMITS · *grade:* narrative · *verification:* not_applicable · *source:* `{"path": "README.md", "section": "## Known limitations"}`

````text
## Known limitations

- **One gate.** Only 12:00 D-1 is a first-class citizen. `--gate-hour` moves it,
  but the baselines' D-1/D-2 switchover point moves with it.
- **`nmae_peak` uses a proxy.** p99 of observed generation, not RTE's installed
  capacity series. French PV capacity grew quickly, so comparisons across
  distant years are approximate.
- **The point forecast throws away `t0`'s distribution.** The model emits
  quantiles; only the median is scored. Pinball loss / CRPS would use the rest.
- **Mask sensitivity is not swept.** The daytime threshold is 1% of the peak
  proxy, fixed.
- **Bootstrap intervals need days.** Below ~14 delivery days the 7-day block is
  shortened and the interval is indicative only; the run warns when this happens.
- **Weights follow `main` unless pinned.** The workflow pins them; locally, pass
  `--revision` for exact reruns. `run_meta.json` records the requested and the
  resolved commit.
- **Definitive data, origin slot inclusive.** Every method reads RTE's
  definitive series rather than the real-time feed an operator would hold at
  12:00 D-1 (see *Data vintage*: identical for every method, transfer to
  real-time inputs untested), and the half-hour stamped at the origin counts as
  observed for every method.
- **Fixed a-priori parameters.** The EWMA decay, the blend weight, the source
  counts and the night mask's threshold and geometry were chosen before any
  Phase 2 number existed and are not tuned; a different choice would be a
  different experiment, and the audit reports the mask's leverage.
- **Two notions of night.** The reporting daytime filter is climatological and
  the `t0_night_zero` mask is astronomical; they disagree on a few twilight
  half-hours, so the variant's night diagnostic reads small but non-zero and
  its daytime numbers could in principle differ from raw `t0`'s (in 2024 the
  three affected half-hours changed nothing: the daytime rows are identical).
  Counted in `night_zero_audit.csv`, not "fixed".
- **`t0` cannot trip the drop rule.** The `tfc-t0` package replaces non-finite
  outputs with 0.0 internally, so a numerical failure would score as a zero
  forecast rather than dropping the window.
- **Context gaps.** With a 90-day context, the 2023 and 2024 autumn-DST gaps
  sit inside `t0`'s context for 90 of the 363 scored origins (`run_meta.json`
  records the count); `t0` treats them as missing values.
````

### INFRA-ZONES: Data zones (Europe/Paris local days)

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"path": "engine/zones.py"}`

```json
{
 "discovery": [
  "2022-01-01",
  "2025-12-31"
 ],
 "consumed_years": {
  "2025": "claim C1, one-shot confirmation, Actions run #20 (36145552543)"
 },
 "forward_from": "2026-01-01",
 "rule": "discovery data may be explored freely; a consumed year is explorable but never confirmable; forward data are readable only through the vault, once, with the owner's approval"
}
```

### INFRA-ENGINE-CATALOGUE: What the engine's referee can run today (its catalogue)

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"path": "engine/catalogue.py"}`

```json
{
 "t0": {
  "repo_id": "theforecastingcompany/t0-alpha",
  "revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b",
  "context_days": 90,
  "gate": "12:00 Europe/Paris on D-1, forecasting local day D"
 },
 "targets": {
  "consumption": {
   "description": "French national electricity consumption (ODRÉ eco2mix-national-cons-def, 'consommation', MW, 30 min)",
   "dataset": "eco2mix-national-cons-def",
   "column": "consommation",
   "night_zero": false,
   "best_simple": "blend_50",
   "reference": "rte_j1"
  },
  "solar": {
   "description": "French national solar generation (same dataset, 'solaire', MW, 30 min); scored after night zeroing",
   "dataset": "eco2mix-national-cons-def",
   "column": "solaire",
   "night_zero": true,
   "best_simple": "ewma",
   "reference": null
  }
 },
 "covariates": {
  "holiday": {
   "targets": [
    "consumption",
    "solar"
   ],
   "kind": "calendar",
   "transforms": [
    "raw"
   ],
   "first_day": null,
   "description": "1 on French public holidays (fixed dates and Easter-based), else 0; timestamps only"
  },
  "bridge_day": {
   "targets": [
    "consumption"
   ],
   "kind": "calendar",
   "transforms": [
    "raw"
   ],
   "first_day": null,
   "description": "1 on a Monday before a Tuesday holiday or a Friday after a Thursday holiday; timestamps only"
  },
  "geometry": {
   "targets": [
    "solar"
   ],
   "kind": "calendar",
   "transforms": [
    "raw"
   ],
   "first_day": null,
   "description": "capacity-weighted clear-sky solar geometry (the covariate slice's K1); timestamps only"
  },
  "wx_radiation": {
   "targets": [
    "solar"
   ],
   "kind": "weather",
   "transforms": [
    "raw"
   ],
   "first_day": "2024-06-06",
   "description": "archived ECMWF shortwave radiation forecast issued ~3 days ahead, weighted by 2023 regional solar output (the covariate slice's frozen construction)"
  },
  "wx_temperature": {
   "targets": [
    "consumption"
   ],
   "kind": "weather",
   "transforms": [
    "raw",
    "hdd15",
    "cdd22"
   ],
   "first_day": "2024-05-06",
   "description": "archived 2 m temperature forecast issued ~3 days ahead at the 12 regional prefectures, weighted by 2023 regional consumption; hdd15 = max(15 - T, 0), cdd22 = max(T - 22, 0)"
  }
 },
 "comparators": {
  "best_simple": "the target's best simple rule, fixed by the referee (consumption: blend_50, chosen on 2023; solar: ewma)",
  "t0_base": "t0 with no covariates",
  "accepted": "the arm of the latest accepted finding for this target (consumption: C1 = t0 + holiday)",
  "rte_j1": "RTE's own day-ahead forecast (consumption only; reference only, never decides a verdict)"
 },
 "metrics": {
  "mae": "mean absolute error over all half-hours of the scored days (MW)"
 },
 "scopes": {
  "all": null,
  "winter": [
   11,
   12,
   1,
   2,
   3
  ],
  "summer": [
   5,
   6,
   7,
   8,
   9
  ]
 },
 "periods": {
  "Y2022": [
   "2022-01-01",
   "2022-12-31"
  ],
  "Y2023": [
   "2023-01-01",
   "2023-12-31"
  ],
  "Y2024": [
   "2024-01-01",
   "2024-12-31"
  ],
  "Y2025c": [
   "2025-01-01",
   "2025-12-31"
  ],
  "ALL": [
   "2022-01-01",
   "2025-12-31"
  ]
 },
 "limits": {
  "arms": 3,
  "covariates_per_arm": 3,
  "comparisons": 3,
  "rationale_chars": 800,
  "name_chars": 32
 },
 "not_in_the_catalogue": "French day-ahead prices (Experiment 4's code lives outside the engine, in solarbench/price_*.py and run_prices.py); any data source not listed above"
}
```

### INFRA-VAULT: Confirmation rules of the forward vault

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"path": "engine/claims.py", "ledger_seq": 56}`

```json
{
 "batch_budget": 4,
 "alpha_per_batch": 0.0125,
 "batches_used": 1,
 "max_claims_per_batch": 4,
 "deltas": [
  0.0,
  0.05,
  0.1,
  0.2
 ],
 "embargo_days": 14,
 "window_days": 168,
 "block_days": 14,
 "min_days_per_block": 10,
 "min_window_blocks": 10,
 "open_batches": [
  {
   "seq": 56,
   "batch_id": "B1",
   "window": [
    "2026-10-13",
    "2027-03-29"
   ]
  }
 ],
 "one_open_batch_at_a_time": true,
 "consequence": "no new claim can be frozen until batch B1 has been opened (after 2027-04-01)"
}
```

### INFRA-BUDGET: The researcher's discovery budget

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"path": "engine/referee/budget.py", "ledger_head_seq": 70}`

```json
{
 "evaluations_total": 200,
 "evaluations_spent": 16,
 "evaluations_remaining": 184,
 "unit": "one evaluation per comparison in a researcher probe; an identical probe (same probe hash) returns its recorded result at no cost; referee and owner runs are not charged",
 "probes_submitted_by_the_researcher": 6,
 "weather_usable_now": [
  {
   "target": "consumption",
   "covariate": "wx_temperature"
  },
  {
   "target": "solar",
   "covariate": "wx_radiation"
  }
 ]
}
```

### INFRA-DATA: Public data sources already wired, and their point-in-time rules

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"paths": ["solarbench/covariates.py", "engine/covs.py", "solarbench/price_spec.py", "README.md#data"]}`

```json
{
 "consumption_and_solar": "ODRÉ eco2mix national (definitive or consolidated) and regional series, 30 min; RTE's own day-ahead forecast 'prevision_j1' is a reference only (its issue time is not verified)",
 "weather": "Open-Meteo previous-runs archive of ECMWF IFS 0.25°, run issued three days before ('previous_day3'), 12 regional points: temperature from 2024-02-06 (scorable from 2024-05-06 for consumption), radiation from 2024-03-08 (scorable from 2024-06-06); a 2-day-old forecast was not used because its issue time could not be verified",
 "prices": "French day-ahead prices from Energy-Charts (scored) and SMARD (cross-check), hourly, 2019-12-01..2025-12-31, CC BY 4.0; at 12:00 on D-1 every price of D-1 is already public",
 "decision_time": "12:00 Europe/Paris on D-1 for every experiment so far",
 "anything_else": "no other source is wired; a new one needs proof that each value was published before the decision time, and a licence that allows this use"
}
```

### INFRA-T0: The forecasting instrument

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"paths": ["docs/experiment_3/T0_STRENGTHS.md", "docs/experiment_4/RETRIEVAL_EVENTS.md", "solarbench/t0_pinned.py", "engine/catalogue.py", "tfc-t0 0.3.2: t0/data.py, t0/model/model.py, t0/scaler.py, t0/mask.py", "solarbench/forecasters.py (T0_QUANTILES)", "solarbench/probes.py (T0JointForecaster)", "branch experiment-1a-preregistration: docs/experiment_2/PREREGISTRATION.md section T.1, rows M-02 and M-10 (findings only)"]}`

```json
{
 "in_use": "t0-alpha (102M parameters), zero-shot, 90-day context; it emits five native quantiles 0.1..0.9; the engine and claim C1 request 0.1, 0.5 and 0.9 and score the median; Experiment 4 and Experiment 3's P1 used all five; covariates are passed as known-future inputs; the past-only covariate route has never been used here",
 "covariate_roles": "in the pinned tfc-t0 0.3.2, predict() builds its input with TimeSeries.from_array, which types every context row as TARGET (t0/data.py): an extra context series passed through predict() is forecast jointly with the target as a co-target, and its horizon is withheld. The HISTORICAL (past-covariate) role the t0 paper describes is reached only through a hand-built TimeSeries passed to predict_from_time_series. The package does not say which path produced the paper's past-covariate results, and no experiment here has passed a past covariate by either path. The only multi-row predict() context so far is Experiment 3's P3 (L6, R-EXP3-3): the 12 regional solar series forecast jointly as co-targets, joint vs independent +0.1%. Known-future covariates span context and horizon, are standardised with statistics over that whole span (t0/scaler.py), and are read bidirectionally (t0/mask.py), so every value in the span enters every forecast",
 "loading": "Experiment 4 loads t0-alpha by the sha256 of its weight files (the frozen revision id vanished upstream on 2026-09-29); the engine and earlier experiments still load it by that revision id, so an engine probe would currently fail to load t0 until that is fixed",
 "t0_beta": "the authors' larger t0-beta is reported as stronger on their benchmarks; it has never been tested here, and no frozen experiment may switch from alpha to beta"
}
```

### INFRA-COST: Observed run costs

*Experiment:* INFRA · *grade:* infrastructure · *verification:* not_applicable · *source:* `{"paths": ["docs/experiment_4/scored_run/FACT_SHEET.md", "engine-ledger research_call entries"]}`

```json
{
 "experiment_4_scored_run": "about 39 minutes of the run step on a standard Actions runner, CPU only, nine arms over 731 days (FACT_SHEET section 4)",
 "engine_probe": "one probe of up to 3 arms over 2022-2025 runs within one Actions job",
 "research_call": "earlier researcher calls used about 13-19 thousand input tokens and 0.7-1.5 thousand output tokens each"
}
```

