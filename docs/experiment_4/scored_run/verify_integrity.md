# Integrity and provenance check: Actions run 36823477529 (job 110243900839), prices.yml, mode "run"

**Verdict: no defects.** Every item below is OK. Four observations at the end are not defects.

**Scope.** I checked:
- `run_meta.json`, `results.json` and `run.log` in this directory
- the repository at 2b407f42c03d2734ef4170cfb3e66962dbba9552 (the local checkout is this commit, with a clean working tree)

The rules come only from PRICE_SPEC in `solarbench/price_spec.py` and the owner-approved records beside it.

**Extraction re-checked.** I re-extracted each file from the "Show results" groups of `run.log` myself. All four match the extractor's files byte for byte:

| file | sha256 |
|---|---|
| results.json | a5d509f8… |
| run_meta.json | 63e13ded… |
| summary.md | ad576ac4… |
| program_role.md | 179a58b1… |

## Items

1. **Spec hash: OK.**
   - `spec_sha256` = `pinned_spec_sha256` = 225774c89e301166c2d4850e2f894335fd5ae703dc410bc4a06aa246ac5755bc.
   - Recomputing `ps.spec_sha256()` locally at 2b407f4 gives the same value, which equals `PRICE_SPEC_SHA256`.
   - `run_meta.avail` equals `ps.AVAIL` exactly.
   - `status`, `experiment`, `attribution` and the `t0` repo/revision equal the spec.

2. **Commit: OK.**
   - `run_meta.commit` = 2b407f42c03d2734ef4170cfb3e66962dbba9552. It comes from GITHUB_SHA.
   - The checkout log fetched `+2b407f4…` and `git log -1` printed 2b407f4 (log lines 92-107).
   - The run step was `python run_prices.py "run" … --run-id "36823477529"`, and `run_id` = 36823477529.
   - Since the K2 check commit e47a6e9, the only change is one appended line in `docs/experiment_4/k2_attempts.jsonl`. So the check attempt ran on the same code.

3. **LEAR code unchanged during the run: OK.**
   - `lear_sha256_start` = `lear_sha256_end` = 7770361a7b69f20b66cc93577f9f6b024ef80932ac0a41247d358054d009d19a.
   - This equals sha256(`solarbench/lear.py` @2b407f4) and attempt 3's `lear_sha256`.
   - There is no `stopped` key in run_meta.

4. **K1: OK.**
   - `k1` = {attempts 3, passed false, passing_attempt null, over_budget false, log_present true, log_sha256 b111286d051e40fbe74367136180a3fcf56300071fd3295bf4f980a9f64ff5e4}.
   - That log_sha256 equals sha256 of `docs/experiment_4/k1_attempts.jsonl` @2b407f4. The workflow's log step printed the same hash with "tracked" (log line 439).
   - All three logged attempts failed on `mean_abs_diff_ensemble`. Attempt 3 is marked final.
   - The attempts ran at d861b78, d799add and 62bcf38, in runs 36697501545, 36712555696 and 36780460835. All three commits are ancestors of 2b407f4, so every attempt came before the freeze commit, as `gates.K1.attempts` requires.

5. **Amendments: OK.**
   - `amendments` = {ids ["A1"], record docs/experiment_4/AMENDMENTS.md, sha256 354f8e4c2bf962bc7812a1b40b1562bf7e2caf119c2604a0a05a2c26e6e56654}.
   - That sha equals `AMENDMENTS.md` @2b407f4 and `tests/test_price_spec.py`'s `AMENDMENTS_SHA256`. The record contains only A1.
   - summary.md ends with the A1 line, after the frozen lines.

6. **t0 weights: OK.**
   - `t0_weights` = frozen_revision 9b02c5f4bb6c89ba15d9fa74554018fe6464220b, served_by_revision fdd189642a529fee59ba7d491235a06779e41a83, verified true, event `docs/experiment_4/RETRIEVAL_EVENTS.md`.
   - config.json b2b54568… and model.safetensors 16c030d3… are byte-equal to `t0_pinned.PINNED_SHA256[9b02c5f4…]`.
   - The run log says "frozen bytes of 9b02c5f4… verified, fetched from the Hub head fdd18964…" (06:21:27).
   - The pre-check step printed head fdd18964 with model.safetensors 16c030d3…. This matches the head that RETRIEVAL_EVENTS.md records.

7. **Licence: OK.**
   - `licence` = {files 73, refusals [], seen ["CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur | SMARD.de"]}.
   - The seen string is in `AVAIL.licence_info` and contains both required substrings.
   - 73 = monthly chunks Dec 2019 .. Dec 2025.

8. **Agreement: OK.**
   - Hours 34992 (= 1458 Paris days 2022-01-01..2025-12-28 × 24).
   - hours_differing 0, missing_a 0, missing_b 0, share_agreeing 1.0, max_abs_diff 0.0, first_mismatches [].
   - not_cross_checked = 2025-12-29..31, as the agreement rule says.
   - `day_2024_06_26` is present: 24 Energy-Charts values and 24 SMARD values, identical.
   - region "DE" is SMARD's URL region for filter 254 (Marktpreis: Frankreich), the first one `fetch_smard` tries. It is not a different series.

9. **Prices: OK.**
   - Stamp "start". 53352 hours = 2223 days 2019-12-01..2025-12-31 × 24.
   - native 51143 + from_quarters 2209. 2209 = Q4 2025: 92 days × 24 + 1.
   - incomplete_quarter_hours 0, off-grid 0.
   - first 2019-11-30 23:00Z (00:00 Paris), last 2025-12-31 22:00Z.

10. **Leak check: OK.**
    - `leak_check.pass` = true. I walked the whole structure: 459 leaves, all boolean, all `true`. No false leaf anywhere.
    - Origins: all 11 TEST_ORIGINS plus `p4_first_day:2024-06-06`. Every origin's `pass` is true.
    - The `whitelist` passes for t0, t0_cal, t0_cal_strict and t0_cal_wx. t0_cal_wx also has weather_is_loaded.

    Every control in `leak_controls` is present on the arms it names:

    | control | arms checked | where |
    |---|---|---|
    | target poisoning (affine and NaN) | t0, t0_cal, best_simple_2023, best_simple_eq, naive_std, prev_week, t0_cal_strict, best_simple_2023_strict | every origin |
    | target poisoning (affine and NaN) | t0_cal_wx | the 9 TEST_ORIGINS on or after 2024-06-06, and the p4_first_day origin |
    | legal change (D-1 afternoon, D-2) | t0, t0_cal (and t0_cal_wx where it is checked) | every origin |
    | `legal_d1_moves_eq_error_quantiles` | best_simple_eq | every origin |
    | covariate issue-time refusal | the generic window check, t0_cal, t0_cal_strict (and t0_cal_wx where it is checked) | every origin |
    | strict-rule controls (`poison:` on the strict windows, `strict_afternoon_does_not_move`, `strict_noon_moves`) | t0_cal_strict, best_simple_2023_strict | every origin |
    | `context_end` | t0, t0_cal, best_simple_2023, t0_cal_strict, best_simple_2023_strict (and t0_cal_wx where it is checked) | every origin |
    | weather controls (`after_d_no_effect` and `before_d_moves`, the +50 control) | t0_cal_wx | where it is checked |

    - On 2024-01-01 and 2024-03-31, the dates before p4_first_day, t0_cal_wx is correctly not checked.
    - At `p4_first_day:2024-06-06`, `in_run_leak_check` (price_run.py:208-219) writes t0_cal_wx's controls under unqualified names: poison, weather, legal_afternoon, legal_d2, context_end, covariate_refusal. All are true.
    - No lear_ens or lear_ens_eq control was run, which is correct because K1 failed.
    - Order in `cmd_run`: the leak check, then K2, then `forecast_all`.

11. **K2: OK.**
    - `k2_record` = {run_id 36823477529, commit 2b407f4, pass true}. The run step printed the same record.
    - `k2_attempts[0]` is identical to the single line of `k2_attempts.jsonl` @2b407f4. That line is the check run 36820039916 at e47a6e9 with pass true.
    - `k2_attempts[1]` is this run (this_run true, command "run").
    - All four arms pass. Every day has single-window bit-identity, and batch_max_abs_diff ≤ 5.34e-05, under the 0.01 tolerance.
    - Window kinds and horizons: t0/t0_cal/t0_cal_wx use cutoff and 25 h; t0_cal_strict uses strict and 36 h.
    - t0_cal_wx has 9 origins, the ones on or after 2024-06-06.
    - Covariates: t0 none; t0_cal and t0_cal_strict holiday; t0_cal_wx holiday + wx_temperature + wx_radiation.
    - K2 has no false leaf. arms_missing and windows_given are empty, and every `missing` list is empty.
    - `k2_log`: tracked true, sha256 3b18f984… equals the file @2b407f4.

12. **K3: OK.**
    - pass true, period 2023-10-02..2023-12-03 (63 days, all built, 0 dropped). Both conventions pass every check.

      | convention | planted_ratio (≤ 0.95) | decoy_ratio (0.98-1.10) | shift_penalty (≥ 1.01) |
      |---|---|---|---|
      | instant | 0.3049 | 0.9970 | 1.3012 |
      | mean_preceding_hour | 0.3012 | 0.9943 | 1.4574 |

    - non_finite_warnings 0 and sanitised [] for every arm.
    - I recomputed every ratio from the MAE table, and noise_sd = 0.05 × p99. All match.
    - The grid runs from 2023-07-03 22:00Z to 2023-12-04 01:00Z, 3676 stamps. That matches the spec's planted-grid rule.

13. **Selection: OK.**
    - best = blend_50, MAE 21.4212. That is the argmin of the 8 candidates, listed in spec order. Runner-up: prev_day 22.7481.
    - 365 days, windows built 365, incomplete 0, no candidate drops.

14. **Windows: OK.**
    - Test windows: built 731 (366 + 365), incomplete_target 0.
    - Strict windows: built 731, incomplete 0.

15. **P4 days: OK.**
    - 574 candidates (2024-06-06..2025-12-31), 572 kept.
    - Dropped: horizon [2025-12-30, 2025-12-31], context []. These are exactly the expected drops.
    - The kept days are the remaining 572, sorted, with no duplicates.

16. **t0_missing: OK.**
    - Context [] and sanitised [] for t0, t0_cal, t0_cal_strict and t0_cal_wx.

17. **missing_by_arm: OK.**
    - Every arm has 0 missing over its 731 days. best_simple_eq uses the pinball metric; the strict arms use the strict windows' days.
    - The exception is t0_cal_wx: 574 days, 2 missing, by cause {"weather_p4.day_rule: horizon": [2025-12-30, 2025-12-31]}.

18. **Scored arms: OK.**
    - `scored_arms` = best_simple_2023, best_simple_2023_strict, best_simple_eq, naive_std, prev_week, t0, t0_cal, t0_cal_strict, t0_cal_wx.
    - It contains no lear_ens or lear_ens_eq, and it contains t0_cal_wx (K3 passed).
    - `forecast` has no `lear_logs`.
    - P2 = 'not runnable', cause "K1 failed", Holm p 1.
    - All three LEAR secondaries read "not run", cause "lear_ens(_eq) not scored (K1 failed)".
    - The upload step's "8 files" equals the four printed files plus forecasts.csv.gz and per_day_P1/P3/P4.csv. No per_day_P2 is expected.

19. **Forecast timings: OK (not recorded).**
    - run_meta holds no per-phase timings, so these come from log timestamps only.
    - Tests: 06:12:26-06:21:18 (501 passed).
    - Run step: 06:21:22-06:59:58, 38.6 min:
      - t0 verified at 06:21:27.
      - The Energy-Charts fetch, with 66 HTTP 429 retries, ran from 06:21:28 to 06:40:26.
      - Nothing else is logged until 06:59:34. That ~19 min covers SMARD, selection, weather, K3, the leak check, K2 and `forecast_all`.
      - Statistics took ~24 s.
    - Upload finished at 07:00:00.

20. **Warnings and errors in the run step, other than 429 retries: OK (no errors).** All 66 "429" lines are `solarbench.price_data WARNING HTTP 429 … retrying`. The other entries:
    - At 06:59:34, a pandas FutureWarning at `solarbench/price_run.py:284`: the `pd.concat` of the backtest frames in `forecast_all`, about all-NA columns being excluded from result-dtype inference.
      - This only affects how the result's dtype is inferred. y and y_hat are float64 by construction.
      - The same warning was raised by the offline end-to-end test in the test step.
    - At 06:59:49-50, two `solarbench.metrics` warnings: "only 25 delivery days: block 12" and "only 21 delivery days: block 10".
      - I matched them in results.json to the report-only P4 slices: 2024Q2 has 25 days (2024-06-06..30), and "the weeks after each DST switch" has 21 days (3 switches × 7).
      - No primary is affected.
    - There are no tracebacks, no "STOPPED" line and no `##[error]`.

## Observations (not defects)

- **Artifact not checked.** The artifact zip could not be downloaded (proxy 403), so forecasts.csv.gz and per_day_P*.csv were not checked. The upload step logged digest 98d8ca1f…, which matches the digest the API reported.
- **Buffered output.** "Loading weights from local directory" appears at 06:59:58 rather than at load time because stdout was buffered.
- **Runner and job-level notices** (outside the run step): a Node 20 deprecation notice, punycode and url.parse DeprecationWarnings, and a git init hint.
- **The run cannot be confirmed.** Experiment 4 is discovery-grade, and this run cannot satisfy the independent-confirmation milestone.
