# Verify: the frozen reading of Experiment 4 (run 36823477529)

VERDICT: CONFIRMED. No disagreements with PRICE_SPEC.

- I re-derived every primary's state, the Holm values, the per-year and coverage rules, the reading-table rows, the strict row, carry_forward and the LEAR secondaries from results.json and run_meta.json.
- Each one matches what the run reports.
- I checked summary.md line by line against the PRICE_SPEC text and results.json. It matches.
- PRICE_SPEC hash: spec_sha256() equals PRICE_SPEC_SHA256 (225774c8…). run_meta records the same value under both spec_sha256 and pinned_spec_sha256.
- Script used: `_verify_reading.py`, in this directory. It is read-only and imports solarbench.price_spec.

## 1. Gate facts the states depend on

**K1 failed.**
- k1_attempts.jsonl has 3 attempts, all `"pass": false`. Attempt 3 is final under A1. It failed only `mean_abs_diff_ensemble`: 0.4076 against the 0.25 limit.
- run_meta.k1 reads `{"attempts": 3, "passed": false, "passing_attempt": null}`. lear_sha256 is 7770361a… at both start and end.
- So, by lear.scored_only_if, `lear_ens` and `lear_ens_eq` are not scored. They are absent from run_meta.scored_arms.

**K3 passed.** run_meta.k3.pass is true. Both conventions meet every rule:

| convention | planted_ratio (max 0.95) | decoy_ratio ([0.98, 1.10]) | shift_penalty (min 1.01) | no_sanitised_output |
|---|---|---|---|---|
| instant | 0.3049 | 0.9970 | 1.3012 | true |
| mean_preceding_hour | 0.3012 | 0.9943 | 1.4574 | true |

**P4 days.**
- AVAIL.p4_first_day is 2024-06-06.
- 572 P4 days were kept, from 2024-06-06 to 2025-12-29.
- 2025-12-30 and 2025-12-31 were dropped under day_rule (a), the horizon rule, as weather_p4.day_rule expects.

## 2. Holm, recomputed by hand

statistics.multiplicity: "Holm over the four primaries at alpha 0.05; a not-runnable primary enters with p = 1".

**Raw p.** The values sit on the p_value grid (1 + k)/2001:
- P1 = 1/2001 = 0.00049975
- P3 = 1/2001
- P4 = 2/2001 = 0.0009995
- P2 = 1, because it is not runnable

**Step-down,** in ascending order P1, P3, P4, P2:

| rank | primary | computation | adjusted p |
|---|---|---|---|
| 1 | P1 | 4 × 1/2001 | 0.0019990 |
| 2 | P3 | max(0.0019990, 3 × 1/2001 = 0.0014993) | 0.0019990 |
| 3 | P4 | max(0.0019990, 2 × 2/2001 = 0.0019990) | 0.0019990 |
| 4 | P2 | max(0.0019990, 1 × 1) | 1 |

- The P1/P3 tie does not change any value.
- The rejection form gives the same answer:
  - P1: 1/2001 < 0.0125, rejected
  - P3: 1/2001 < 0.01667, rejected
  - P4: 2/2001 < 0.025, rejected
  - P2: 1 ≥ 0.05, stop
- verdicts.p_holm is P1 0.001999000499750125, P3 the same, P4 the same, and P2 1.0. That is exactly 4/2001, with P2 at 1. p_holm_input is 1.0 for P2. **Matches.**

## 3. States, re-derived

statistics.verdict_states: "each primary gets exactly one state, the first that applies: 'not runnable' (P2: K1 failed or P2 coverage < 0.95; P4: K3 failed or no P4 day scored; P1 and P3 never); 'lost' (its pooled skill does not pass its threshold, or Holm p >= 0.05); 'not stable' (pooled passes but a year's skill does not); for P3 only 'lost on coverage' (pooled and both years pass on pinball, but coverage is outside [0.70, 0.90]); otherwise 'won'."

The per-year rule passes "only strictly above the threshold (> 0; P2 > -0.05)", with "P4's 2024 part: from AVAIL p4_first_day".

| primary | not runnable? | pooled vs threshold, Holm | 2024 / 2025 (> threshold) | coverage | derived | reported |
|---|---|---|---|---|---|---|
| P1 MAE | never | 0.227107 > 0; Holm 0.001999 < 0.05 | 0.225383 > 0 / 0.228779 > 0 | n/a | won | won |
| P2 MAE | yes: K1 failed | not run | not run | p2_coverage "not run" | not runnable | not runnable (cause "K1 failed") |
| P3 pinball | never | 0.251885 > 0; Holm 0.001999 < 0.05 | 0.256492 > 0 / 0.247378 > 0 | 0.732786 in [0.70, 0.90] | won | won |
| P4 MAE | no: K3 passed, 572 days | 0.0284216 > 0; Holm 0.001999 < 0.05 | 0.0151408 > 0 (209 days, 2024-06-06..12-31) / 0.0367856 > 0 (363 days) | n/a | won | won |

Thresholds in verdicts: P1, P3 and P4 are 0.0; P2 is -0.05. These are correct.

**Internal consistency checks.** These rebuild the reported numbers from the quarter slices' loss_arm × hours sums. They are not a recomputation from the per-day tables, which are only in the artifact that could not be downloaded.
- Each yearly and pooled skill agrees to within 4e-16:
  - P1: 2024 has 366 days and 8784 h; 2025 has 365 days and 8760 h.
  - P3: the same day and hour counts as P1.
  - P4: 2024 has 209 days and 5017 h (24 × 209 + 1 for the October 2024 fall-back day); 2025 has 363 days and 8712 h; 2024Q1 is "no days".
- Each pooled skill equals 1 - loss_arm/loss_ref of its compare block.
- Each 95% interval contains its skill.

**P3 coverage.**
- Pooled coverage is 12856/17544 = 0.732786: 6347/8784 hits in 2024 and 6509/8760 in 2025, both integer counts.
- It lies inside the closed band.
- The per-year coverage figures (0.722564 and 0.743037) are printed as information only. That is correct, since "coverage is pooled only, per-year coverage is printed".

## 4. summary.md against reading_table

**Line 1** is `Status: ` followed by PRICE_SPEC["status"], verbatim. This satisfies printing: "summary.md opens with the status line (discovery-grade, nothing confirmed)".

**Row choice:**
- With P1 'won' and P2 'not runnable', the correct key is "P1 won, P2 not runnable". It is printed byte-identical: "t0 beats the best simple rule; the comparison with LEAR was not made (K1 failed or LEAR forecast too few days), so nothing is concluded about LEAR."
- The rows "P1 won, P2 lost or not stable" and "P1 not won, …" correctly do not appear.
- **P3 'won'**: the "P3 won" row is printed byte-identical.
- **P4 'won'**: the "P4 won" row is printed byte-identical.
- **'not stable' rows**: no primary is 'not stable', so none is printed. This is correct.
- **Order**: P1/P2 row, P3 row, P4 row, then the strict row, as `printing` requires.

**Strict row.**
- It is read because P1 is 'won'.
- t0_cal_strict vs best_simple_2023 is 0.067768 pooled, 0.0809742 in 2024 and 0.0549668 in 2025, all > 0. So it "beats", and the first sentence applies.
- The printed text "P1 does not rest on t0 reading the D-1 afternoon prices." is byte-identical to the sentence quoted in reading_table.strict.
- Both comparisons' pooled, 2024 and 2025 skills are printed beside the row:
  - vs best_simple_2023_strict: 0.153247 / 0.159079 / 0.147675.
  - Both comparisons use 731 days. results.json strict equals the matching secondaries exactly.

**Numbers beside rows.** Each value is printed at 6 significant digits, and each printed line equals one rebuilt from results.json.
- P1: pooled skill, 95% interval, raw p, Holm p, 2024, 2025 and days (731).
- P2: every field reads "not run" except "Holm p 1", plus "cause: K1 failed". This satisfies "a not-runnable primary enters Holm with p = 1 and its Holm p is printed" and the day_sets wording ("printed 'not run' (an arm was not scored: lear_ens after K1 failed …)").
- P3: the same fields as P1, plus pooled coverage and per-year coverage.
- P4: the same fields as P1, with days 572.

**Attribution** is the line after the rows and equals ATTRIBUTION exactly.

**The A1 line** comes after the attribution, so after every frozen line. It names A1 (2026-09-30, owner-approved), the record docs/experiment_4/AMENDMENTS.md, and that the spec and every threshold are unchanged, with penalty step (1) superseded. This is consistent with AMENDMENTS.md.

**stdout copy.** summary.md is identical to the run step's stdout copy at log lines 543-557 (1-based; the extractor said 542-556) and again at 4329-4343.

## 5. carry_forward

The rule: "a primary is a vault candidate only if its state is 'won' and some delta in {0, 0.05, 0.10, 0.20} satisfies S - delta >= M … delta is the largest value satisfying the inequality".

In each case, S equals that primary's "April-September" slice skill on its own day set, and ref_mae equals that slice's loss_ref.

| primary | state | days (Apr-Sep 2024/25) | S | M (alpha 0.0125, '12') | S − delta ≥ M for | delta | candidate |
|---|---|---|---|---|---|---|---|
| P1 | won | 366 | 0.155133 | 0.1223 | 0 only (0.05 gives 0.1051 < M) | 0 | true |
| P2 | not runnable | — | — | — | — | null | false |
| P3 | won | 366 | 0.179853 | 0.117 | 0 and 0.05 (0.10 gives 0.0799 < M) | 0.05 | true |
| P4 | won | 300 (2024-06-06..09-30: 117, plus 2025 Apr-Sep: 183) | 0.011223 | 0.0489 | none | null | false |

- Only 'won' primaries are candidates, and A is restricted to April-September of 2024/2025.
- block_sd, ref_mae and M at 0.0125/2, /3 and /4 are present for P1, P3 and P4.
- The M values are stored at 4 decimals. No decision is within that rounding: the nearest margin is 0.013, for P3 at delta 0.05.

**Read with care:**
- P4 is 'won' on the frozen reading but is not a vault candidate. Its April-September skill is 0.0112: the slice's 95% interval is [-0.0088, 0.0333] with p 0.149, below M 0.0489. So the first price-domain test of the covariate primitive gives a discovery-grade 'won' that does not carry forward under the frozen rule.
- P3 is a candidate by the rule, but carry_forward.expressible_today says "P2 and P3 need vault extensions". Of today's expressible probes, only P1 (vs best_simple) is a candidate.
- The carry_forward block is in results.json and stdout, not in summary.md. reading_table.printing does not require it there, so this is not a disagreement.

## 6. Secondaries involving lear_ens

Every one reads "not run", with cause K1. As statistics.day_sets puts it: "every numeric field is printed 'not run' (an arm was not scored: lear_ens after K1 failed …)".
- "lear_ens vs best_simple_2023": not run, "lear_ens not scored (K1 failed)"
- "t0_cal vs lear_ens (superiority)": not run, "lear_ens not scored (K1 failed)"
- "lear_ens + empirical bands vs t0_cal bands": not run, "lear_ens_eq not scored (K1 failed)"
- the lear_ens entries of rMAE (vs naive_std and vs prev_week): not run, K1 cause
- RMSE P2: not run, K1 cause
- the P2 slices and P2 tables: "not run". These entries carry no cause field. That is cosmetic, because the cause is given at the primary, verdict and secondary level.

All ten report_only.secondaries are present. The five non-LEAR secondaries were computed, on 731 days each.

## 7. Minor notes (not disagreements)

- **Bootstrap warnings.** The two solarbench.metrics warnings come from report-only P4 slices, not from primaries:
  - "25 delivery days" is P4's 2024Q2 slice (2024-06-06..06-30).
  - "21 delivery days" is P4's "weeks after each DST switch" slice.
- **No artifact.** The raw p values and intervals could only be checked for consistency with the p grid and with each other. The bootstrap draws and per-day tables are in the artifact, which was not obtained.
