# Phase 0: results and dispatch log

*Frozen spec: `PHASE0_SPEC.md`, `spec_sha` `6ab46db996e345de093e5b650a3cd104ec60da23a1d4a0966ed72ce68b8788dc`
(freeze commit `43da2c4`). Every dispatch of `.github/workflows/research-loop-phase0.yml` is listed here, with any
defect documented before the rerun it led to.*

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37083332774](https://github.com/xuanhuyle/solar/actions/runs/37083332774) | smoke | `43da2c4` | Failed in the test step, before any t0 load: defect D1. Nothing published. |
| 2 | [37083618990](https://github.com/xuanhuyle/solar/actions/runs/37083618990) | smoke | `810c45a` | Success. Weights verified by sha256; calibration reproduced; output finite; nothing sanitised. Published to `phase0/run-37083618990`. |
| 3 | [37083726113](https://github.com/xuanhuyle/solar/actions/runs/37083726113) | phaseA | `810c45a` | **PASS** (integrity clean). Published to `phase0/run-37083726113`. |
| 4 | [37088704906](https://github.com/xuanhuyle/solar/actions/runs/37088704906) | phaseB | `1fb0d07` | **RESEARCHER FEASIBILITY FAILED** (integrity clean; 5 of 7 API attempts were refusals, see below). Published to `phase0/run-37088704906`. |

## Defects and disclosures

- **D1 (test only).** `test_phase_a_runs_end_to_end_with_a_tiny_untrained_t0` expected `run_id` and `commit` to be
  empty in the record, which holds locally but not on Actions, where `GITHUB_RUN_ID` and `GITHUB_SHA` are set. Fix:
  the test removes both variables for its own fake-model run. No rule file changed, so `spec_sha` is unchanged.

## Phase A (run 37083726113): PASS

The scored record is `phase_a.json` on branch `phase0/run-37083726113` (manifest-checked by the publish job); the
numbers below are copied from its `REPORT.md`. Skill = 1 − MAE(with) / MAE(reference), pooled over worlds, with a
95% bootstrap interval over worlds.

**Gate (40 linear worlds, 7-day context; each criterion must hold for both comparisons):**

| Criterion | t0 {E} vs t0 {} | t0 {E} vs t0 {N} (placebo) | Result |
|---|---|---|---|
| C1: skill over k = 7–20 ≥ 5%, lower bound > 0 | +31.3% [+27.5, +34.8] | +32.5% [+28.2, +36.5] | pass |
| C2: lower bound over k = 1–6 > 0 | +20.5% [+15.7, +25.0] | +20.1% [+14.7, +25.1] | pass |
| C3: ≥ 20 of 40 worlds with a 14-day lower bound > 0 | 34 of 40 | 36 of 40 | pass |

Ridge on the same information passes C1–C3 too (reported, not gating).

**Skill by days since the change (linear, 7-day context):**

| k | t0 {E} vs {} | t0 {N} vs {} | ridge {E} vs {} |
|---|---|---|---|
| 0 (control) | −4.7% [−19.4, +6.7] | −7.4% [−16.4, +0.3] | −7.1% [−15.0, +0.0] |
| 1–3 | +15.5% [+9.1, +21.9] | +0.0% [−4.9, +5.0] | +14.3% [+4.1, +23.8] |
| 4–6 | +25.6% [+20.2, +30.6] | +0.9% [−3.9, +5.7] | +33.1% [+25.7, +39.7] |
| 7–13 | +33.5% [+28.8, +37.8] | −0.7% [−4.2, +2.6] | +40.1% [+35.3, +44.8] |
| 14–20 | +28.9% [+24.1, +33.5] | −3.0% [−6.7, +0.6] | +39.5% [+33.2, +45.4] |

Mean absolute error of each arm on its own (same bins): t0 {} 1.40 / 1.31 / 1.30 / 1.37 / 1.30; t0 {E} 1.46 /
1.11 / 0.97 / 0.91 / 0.93; ridge {} 1.48 / 1.50 / 1.51 / 1.53 / 1.50; ridge {E} 1.58 / 1.29 / 1.01 / 0.92 / 0.91.

**Secondary sets (reported, not gating; no placebo arm):**
- Hinge form (12 worlds, 7-day context), t0 {E} vs {}: −0.5% at k = 1–3, +10.3% [−1.2, +19.1] at 4–6, +22.4%
  [+12.3, +32.4] at 7–13, +18.5% [+5.9, +30.4] at 14–20; ridge similar (+23.3% at 7–13).
- 28-day context (8 linear worlds), t0 {E} vs {}: +8.4% at k = 1–3 (interval includes 0), +25.3% at 7–13, +34.1% at
  14–27, +34.6% at 28–41; ridge +9.7%, +19.1%, +24.6%, +33.0%.

**Integrity:** calibration reproduced; 0 sanitised outputs; poison check identical at k = 3, 10, 17; no k = 0
warning. **Cost:** 3,696 scored t0 forecast-days (3,830 in all); the phase_a job ran 2 min 56 s, of which the
Phase A computation took 97 s.

**Per the frozen stop rule, Phase A passing allows Phase B.**
- **D2 (recording gap, found after Phase B).** When the API returns `stop_reason: refusal`, the Phase B code recorded
  the stop reason, the usage and the request id, but not the refusal's category (`stop_details`), which
  `engine/researcher.py` does record. The five refusals below therefore cannot be attributed from the record. It
  changed no result.
- **Disclosure (frozen design).** Candidates are standardised on pre-change days, so the observed data encode the
  change day: a program reading the raw arrays could find it. Only the lab code reads them; the researcher sees
  experiment results only, so it could not.

Before the Phase B dispatch, the build was reviewed twice against the frozen spec. The first review found a blocker:
the research job's guard pattern also matched text in the test file, which would have failed the job and spent the
world on an integrity failure. It was fixed in `1fb0d07`, with a test that runs the pattern over the files the job
checks out. No rule file changed (`spec_sha` unchanged).

## Phase B (run 37088704906): RESEARCHER FEASIBILITY FAILED

The scored record is on branch `phase0/run-37088704906` (`evaluation.json`, `REPORT.md`, `notebook.jsonl`,
`ai.json`, `scripted.json`); the numbers below are copied from it.

**The hidden world (revealed only to the evaluate job).** First changed day τ = 90. R = X02, E = X01, D = X04,
N = X03.

**Integrity: no issue.**
- the observed-data hash matched the regenerated world;
- every prompt was rebuilt byte for byte;
- the 3 experiments were recomputed from the observed data and matched;
- the canary was absent;
- the served model hashed to the pin on every attempt;
- the guard confirmed the truth was absent from the research job.

**Evidence check (t0, 28 days, against no covariate).**

| Candidate | Days | Skill |
|---|---|---|
| R | 57–84, before the change | +29.3% [+18.0, +38.3] |
| E | 99–126, after the change | +13.2% [+0.7, +24.6] |

Both were detectable, E only narrowly.

**What happened to the researcher.**

| Call | Days seen | API attempts | Outcome |
|---|---|---|---|
| 1 (round 1) | 1–84 | 2, both `stop_reason: refusal`, 0 output tokens, about 1 s each | invalid: no experiment |
| 2 (round 2) | 1–112 | 2, both refusals, 0 output tokens | invalid: no experiment |
| 3 (round 3) | 1–126 | 1 refusal, then a valid response | 3 experiments |
| 4 (final) | 1–126 | 1 valid response | final selection X03, X04 |

The refusals came before any output was produced. Their category was not recorded (D2), and the same request shape
later succeeded, so their cause is unknown. Per the frozen rule, an invalid round runs no experiment and is
recorded. Rounds 1 and 2 were therefore lost, including the only round that could show R working before the change.

**Round 3: three experiments against no covariate, 28 days (99–126), all candidates in pairs or together.**

| Experiment | Covariates (roles) | Skill |
|---|---|---|
| E1 | X01 + X02 (E + R) | +12.8% [−0.2, +25.9] |
| E2 | X03 + X04 (N + D) | +21.7% [+8.2, +34.4] |
| E3 | all four | +18.3% [+0.9, +34.0] |

**Final call.**
- **Selection:** X03 and X04 (N and D), both "accepted"; X01 (E) and X02 (R) were marked "redundant".
- **Caveats the researcher stated itself:** the pair was never separated, so one member may carry all the signal;
  all configurations weakened in the last week (days 120–126).
- **Interpretation errors:** none under the frozen rule, but vacuously so. B3 compares each accepted or rejected
  status with that candidate's latest single-candidate result, and no single-candidate experiment ran. The two
  "accepted" statuses (X03, X04) rest only on the pair result E2 and on E3.

**Verdict map.** Row 2, "N in the final selection with its latest lower bound ≤ 0 or never tested": N was never
tested on its own.

**Behaviours.**

| B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 |
|---|---|---|---|---|---|---|---|
| no | yes | yes (vacuous: nothing to check) | yes | no | no | no | no |

**Confirmation (days 127–154, t0; ridge in the published report).** Single covariates and selections are against no
covariate. "D given E" is {E, D} against {E}, and "E given D" is {E, D} against {D}.

| Selection or set | t0 skill |
|---|---|
| E (X01) | +30.8% [+21.9, +39.5] |
| D (X04) | +25.7% [+12.6, +38.2] |
| R (X02) | +4.0% [−3.9, +12.6] |
| N (X03) | +0.3% [−5.7, +5.4] |
| D given E | −6.1% [−20.0, +6.5] |
| E given D | +1.3% [−2.3, +4.8] |
| AI selection {N, D} | +23.5% [+10.8, +36.7] |
| Script selection {D} | +25.7% [+12.6, +38.2] |

So the AI's selection forecast usefully, because D is a correlated proxy of E, and N added nothing. Neither the AI
nor the script found E.

**The frozen scripted strategy (descriptive).**

| Round | Days | Candidate | Skill |
|---|---|---|---|
| 1 | 57–84 | X01 (E) | −0.8% |
| 1 | 57–84 | X02 (R) | +29.3% [+18.0, +38.3] |
| 2 | 99–112 | X03 (N) | +5.9% |
| 2 | 99–112 | X04 (D) | +28.3% [+7.6, +41.0] |
| 3 | 113–126 | X01 (E) | +16.1% [−8.3, +34.2] |
| 3 | 113–126 | X02 (R) | +2.1% |

Its final selection was {D}. It saw R's pre-change strength and the post-change drop, but its 14-day test of E did
not exclude zero.

**Cost.**
- **API:** 7 requests (4 calls, 3 repair turns), 24,435 tokens in all:
  - input 2,625;
  - output 2,315;
  - cache read 16,710;
  - cache write 2,785.
- **t0 forecasts in Phase B:** 672 (script 168, AI 112, evaluate 392).
- **Runner time:** observe 13 s, research 1 min 48 s, evaluate 1 min 4 s, publish 5 s.

**What this run does and does not show.**
- It is one world: an existence check, not a rate.
- The researcher, as deployed (model, API, brief), did not complete the loop in this world. Most of the loss
  happened before it could reason at all: two of three rounds ended in instant refusals, with no output.
- With one round left, it chose a coarse pairwise screen. It then selected an untested noise candidate along with
  the proxy, while correctly reporting that the pair had never been separated.
- Whether refusals should count as an "API outage", which would make the run an integrity failure under verdict
  row 0, was not decided here after seeing the result. The frozen map was applied as written. That decision, and any
  rerun (which would be a new world), are the owner's.

