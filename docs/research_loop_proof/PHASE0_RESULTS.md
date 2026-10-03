# Phase 0: results and dispatch log

*Frozen spec: `PHASE0_SPEC.md`, `spec_sha` `6ab46db996e345de093e5b650a3cd104ec60da23a1d4a0966ed72ce68b8788dc`
(freeze commit `43da2c4`). Every dispatch of `.github/workflows/research-loop-phase0.yml` is listed here, with any
defect documented before the rerun it led to.*

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37083332774](https://github.com/xuanhuyle/solar/actions/runs/37083332774) | smoke | `43da2c4` | Failed in the test step, before any t0 load: defect D1. Nothing published. |

## Defects

- **D1 (test only).** `test_phase_a_runs_end_to_end_with_a_tiny_untrained_t0` expected `run_id` and `commit` to be
  empty in the record, which holds locally but not on Actions, where `GITHUB_RUN_ID` and `GITHUB_SHA` are set. Fix:
  the test removes both variables for its own fake-model run. No rule file changed, so `spec_sha` is unchanged.
