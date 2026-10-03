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

## Defects

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
