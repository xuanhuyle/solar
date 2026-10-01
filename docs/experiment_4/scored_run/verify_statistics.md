# Experiment 4, run 36823477529: statistics check

Lens: recomputing the statistics. Inputs: `results.json`, `run_meta.json` and `summary.md` from the extractor (sha256 as in its report), plus the repository at 2b407f42c03d2734ef4170cfb3e66962dbba9552 (HEAD, clean tree). `spec_sha256()` equals the pinned `PRICE_SPEC_SHA256`. The local numpy 2.4.6 and pandas 2.3.3 are the same versions the run recorded. Script: `_verify_statistics.py`; raw output: `_verify_statistics.json`. Nothing in the repository was edited.

## Verdict

- **I could not recompute the bootstrap.** The per-day tables (`per_day_P*.csv`) and `forecasts.csv.gz` exist only in artifact 11145568607. The proxy refuses its download host, `productionresultssa4.blob.core.windows.net`, with a policy 403 (`connect_rejected` in `/__agentproxy/status`), and I did not retry it. No other copy of this run's per-day data exists on disk. `scratchpad/e2e*/` holds offline synthetic test runs at other commits, which I did not use.
- So these were not independently recomputed: the 2000 draws, every 95% interval, every p, the per-day losses, the P3 pinball sums and coverage counts, and the carry-forward `block_sd` and M.
- I ran 621 internal-consistency and partial-recomputation checks on `results.json`. **All 621 passed, with no mismatches.**

## A. Recomputed with the repository's code at 2b407f4

| Check | Result |
|---|---|
| `price_stats.states(results.primaries)` against `verdicts` | Identical in all 7 fields for P1-P4 (state, p_holm, p_holm_input, p, threshold, ci95, cause) |
| `run_covariates.holm([1/2001, 1, 1/2001, 2/2001])` | P1, P3 and P4 each 4/2001 = 0.001999000499750125, P2 1.0. Identical |
| `summary_lines(primaries, verdicts, strict)` + A1 line, joined as `run_prices` writes it | Byte-identical to `summary.md` (1961 bytes), so every printed 6-significant-digit value agrees with `results.json` |
| Carry-forward delta and candidate from S, M and state (`CARRY_DELTAS`) | P1: S−M = 0.0328 ≥ 0 and S−0.05−M < 0, so delta 0 and candidate. P3: S−0.05−M = 0.0129 ≥ 0 and S−0.10−M < 0, so delta 0.05 and candidate. P4: S−M = −0.0377, so not a candidate. All three identical to the file |
| M from `t_crit(11, α)`, the printed `block_sd` (±0.0005) and the exact April-September reference MAE | P1 0.1223, P3 0.117 (range 0.1169-0.117) and P4 0.0489 (range 0.0488-0.0489) are consistent, as are all 9 M_info values at α/2, /3 and /4. Only consistency: `block_sd` itself needs the per-day data |

## B. Independent cross-checks with plain numpy

**1. Yearly and pooled skills rebuilt from the quarter slices.** Each quarter's arm and reference sums are loss × hours. Then skill = 1 − Σarm / Σref.

| | reported | rebuilt | abs diff | days | hours |
|---|---|---|---|---|---|
| P1 pooled | 0.22710738685445464 | 0.2271073868544543 | 3.3e-16 | 731 | 17544 |
| P1 2024 / 2025 | 0.225383 / 0.228779 | same | ≤3.3e-16 | 366 / 365 | 8784 / 8760 |
| P3 pooled (pinball) | 0.2518851196137203 | 0.2518851196137203 | 0 | 731 | 17544 |
| P3 2024 / 2025 | 0.256492 / 0.247378 | same | ≤1.1e-16 | 366 / 365 | 8784 / 8760 |
| P4 pooled | 0.02842160653111203 | 0.02842160653111192 | 1.1e-16 | 572 | 13729 |
| P4 2024 / 2025 | 0.0151408 / 0.0367856 | same | ≤1.1e-16 | 209 / 363 | 5017 / 8712 |

- Each `each year` slice equals the primary's yearly skill exactly, and its day count equals the sum of the quarter days.
- Each pooled skill lies between its two yearly skills.
- The arm and reference loss sums match the quarter sums to within 1e-13 relative.
- For P1, P3 and P4, `days_won`, `days_lost`, `days` and `hours` each equal the sum over the quarters (P1 519/212, P3 568/163, P4 307/265).
- The April-September slice equals Q2+Q3 of both years, in skill and in counts.
- Carry-forward S equals the April-September slice skill exactly: P1 0.1551330663119581, P3 0.17985269011604454, P4 0.011223231707229164. Its days (366/366/300) match, and so does `ref_mae` (18.998/6.968/16.005).

**2. Every computed `compare()` result (49 in all).** That is 3 primaries, 41 slices (P1 14, P3 14, P4 13) and 5 computed secondaries.
- skill = 1 − loss_arm / loss_ref to within 1e-14.
- Every p equals (1+k)/2001 for an integer k.
- p agrees with the interval under `np.percentile`'s linear rule on 2000 draws. If lo > m then p ≤ 51/2001, otherwise p ≥ 51/2001; the same holds at the upper end with 1951/2001.
- Every interval contains its point skill.
- days_won + days_lost = days in every case (no tied days).
- margin = m = 0 for P1, P3, P4 and their slices.
- The primaries' p values are P1 = P3 = 1/2001 (no draw ≤ 0) and P4 = 2/2001 (one draw ≤ 0). All three intervals lie above 0, which is consistent.

**3. Day and hour counts against the calendar** (`price_exp.day_hours`, `weekend_holiday_days`, `dst_week_days`). Every quarter, weekend/holiday (228 days, 5472 h; P4 178 days, 4273 h), DST-week (28 days, 672 h; P4 21 days, 505 h) and 11:00-16:00 slice (3655 h = 731×5; P4 2860 h = 572×5) matches the calendar. The top-1% hour counts are 176 of 17544 and 138 of 13729, as expected with no ties at the threshold. P1 and P3 share identical hour slices (negative 163 days / 865 h, top-1% 45 / 176). P4's 572 days are 2024-06-06..2025-12-29, matching `run_meta.forecast.p4_days` (574 candidates, 2025-12-30 and 2025-12-31 dropped by the horizon rule). Windows 731 and strict windows 731 have no incomplete target. Every other arm is finite on all 731 days.

**4. The two `solarbench.metrics` warnings.** Exactly two `compare()` calls have fewer than 28 days. They are **P4 slice 2024Q2** (25 days, block 12) and **P4 slice "the weeks after each DST switch"** (21 days, block 10), in the order the log shows. Both are report-only slices; no primary, secondary or table is affected. P1 and P3 DST weeks have 28 days, so no warning.

**5. Consistency across comparisons on the same days.**
- Each arm's pooled MAE is identical in every 731-day comparison: t0_cal 15.276627816199383, t0 15.687360088000057, best_simple_2023 19.765524416161814, t0_cal_strict 18.426054314003654.
- t0_cal's quarter losses in P4 (as the reference) equal P1's (as the arm) exactly for 2024Q3 through 2025Q3.
- Transitivity holds pooled and in each year to within 1e-13: (1−s(t0_cal,t0))(1−s(t0,bs)) = (1−s(t0_cal,t0_cal_strict))(1−s(t0_cal_strict,bs)) = 1−s(P1).
- `strict` equals the two strict secondaries exactly, in pooled, 2024, 2025 and days.

**6. rMAE and RMSE.**
- The naive_std MAE implied by all five 731-day rMAE values agrees to 1e-13 (22.855583889078…), and so does the prev_week MAE (29.41947232672…).
- rMAE(prev_week vs naive_std) × rMAE(naive_std vs prev_week) = 1.
- t0_cal_wx rMAE is on 572 days.
- RMSE ≥ MAE for all four RMSE values.

**7. Tables.**
- For P1, P3 and P4, the concentration skill equals the pooled skill and n_days equals the day count.
- net_gain = (loss_ref − loss_arm) × hours to within 1e-12.
- The top-k shares increase with k, and the skill without the top-k days decreases.
- The sensitivity table's point skill equals the pooled skill in every row. **Its block-14 row equals the primary's `ci95` bit for bit** for P1, P3 and P4, which shows that the same seed-0 draws produced both.

**8. P3 coverage.** coverage_yearly × hours is an integer: 6347 of 8784 in 2024 and 6509 of 8760 in 2025. (6347+6509)/17544 = 0.7327861377108983, exactly as reported, and inside [0.70, 0.90].

**9. P2 and LEAR.**
- P2's skill, ci95, p, days, status and p2_coverage, and both yearly values, are 'not run'. runnable is false, the cause is 'K1 failed', the state is 'not runnable' and the Holm input is 1.
- The three LEAR secondaries, lear_ens rMAE, RMSE P2, every P2 slice, the P2 tables and the P2 carry-forward are all 'not run' with cause K1.
- `run_meta.k1` records 3 attempts and passed false.

## Mismatches

None. 621 checks, 0 failures.

## Not verified (needs the artifact)

- The per-day sums and the 2000 bootstrap draws. So every 95% interval, every p (beyond lattice and interval consistency) and the Holm inputs are taken from the run.
- The pinball computation itself.
- P3 coverage at the hour level.
- The hour-slice membership: negative prices and the top-1% threshold.
- `block_sd` and therefore M.
- `days_won` / `days_lost` beyond their sums.

If the artifact can be fetched from an allowed host, rerun `price_stats.compare` / `yearly` / `coverage` on `per_day_P{1,3,4}.csv` and `forecasts.csv.gz`. The figures above give the exact targets.

## Report-only observations (not mismatches)

- **P4 is concentrated.** The top 20 of 572 days carry 83.4% of the net gain, and without them the skill is 0.0051 (top 5: 28.4%, 0.0207).
- **P4 by period.** April-September S = 0.0112, 95% [−0.0088, 0.0333], below M = 0.0489, so P4 is not a vault candidate. The P4 2024 part is 0.0151; its 2024Q2 slice is −0.0172 (25 days, indicative), 2024Q3 is 0.0057 and 2024Q4 is 0.0323.
- **P1 and P3 in the DST weeks** are negative: −0.0536 [−0.157, 0.144] and −0.0580 [−0.229, 0.151], each on 28 days. This is report-only.
