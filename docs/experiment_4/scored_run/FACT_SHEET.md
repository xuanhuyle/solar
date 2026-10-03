# Experiment 4 (t0 on French day-ahead prices): verified fact sheet

- **Run:** GitHub Actions run 36823477529 (job 110243900839), workflow `prices.yml`, mode "run", 2026-10-01 06:11-07:00 UTC.
- **Commit:** 2b407f42c03d2734ef4170cfb3e66962dbba9552.
- **Sheet location:** `docs/experiment_4/scored_run/FACT_SHEET.md`
- **Inputs:** `results.json`, `run_meta.json`, `summary.md` and `program_role.md`, extracted from `run.log`. The integrity verifier re-extracted all four and got byte-identical files.
- **Verification reports:** `verify_integrity.md` (I), `verify_reading.md` (R) and `verify_statistics.md` (S), in the same folder.
- **Rules:** the only authority is `PRICE_SPEC` in `solarbench/price_spec.py`, read together with the owner-approved records in `docs/experiment_4/` (AMENDMENTS.md, RETRIEVAL_EVENTS.md, k1_attempts.jsonl, k2_attempts.jsonl).
- **Paths:** JSON Pointer notation. `R#/x/y` is `results.json` and `M#/x/y` is `run_meta.json`. Keys are written as stored, spaces included.

---

## 1. Defects and verification limits

**There is no unresolved defect.** All three verifiers reported no defect and no mismatch:

- **Integrity (I): "no defects".** 20 items all OK. They cover the spec hash, commit, LEAR code identity, K1, amendments, t0 weights, licence, source agreement, prices, leak check, K2, K3, selection, windows, P4 days, missing days, scored arms, timings and log warnings.
- **Reading (R): "CONFIRMED".**
  - Every primary's state, the Holm values, the per-year and coverage rules, the reading-table rows, the strict row, carry_forward and the LEAR secondaries were re-derived from PRICE_SPEC. All match the run.
  - `summary.md` matches the spec text and `results.json` line by line.
- **Statistics (S): 621 checks, 0 failures.** In addition, the repository's own `price_stats.states`, `holm` and `summary_lines` at 2b407f4 reproduce `verdicts` and `summary.md` exactly (byte-identical, 1961 bytes).

**Verification gap.** This is a limit on what could be checked, not a defect.

- The run's artifact 11145568607 could not be downloaded: the proxy returned 403 on its blob host. It holds `per_day_P1/P3/P4.csv` and `forecasts.csv.gz`.
- **Not independently recomputed:**
  - the 2000 bootstrap draws, so every 95% interval and every raw p beyond lattice and interval consistency;
  - the per-day losses;
  - the pinball computation;
  - P3 coverage at the hour level;
  - the hour-slice membership (negative-price hours, the top-1% threshold);
  - `block_sd` and therefore the carry-forward M.
- **What was checked instead:** these values come from the run and are internally consistent.
  - Every p lies on the (1+k)/2001 grid and agrees with its interval.
  - Yearly and pooled skills rebuilt from the quarter sums agree to ≤ 4e-16.
  - The block-14 sensitivity row equals each primary's `ci95` bit for bit.
  - M agrees with `t_crit`, the printed `block_sd` and `ref_mae`.
- **Artifact digest:** the upload digest 98d8ca1f7c6f8f6bdfeba807b925bfee25ed1cd9da7a5e46b24acc88be436165 matches the digest the API reports.

**Minor notes (not defects):**

- **P2 cause field.** The P2 slices and P2 tables read "not run" but carry no `cause` field. This is cosmetic: the primary, the verdict and the secondaries all give the cause "K1 failed".
- **carry_forward location.** `carry_forward` is in `results.json` and stdout, not in `summary.md`. `reading_table.printing` does not require it there.
- **Two `solarbench.metrics` short-block warnings.** "only 25 delivery days: block 12" and "only 21 delivery days: block 10". They come from the report-only P4 slices 2024Q2 (25 days) and "the weeks after each DST switch" (21 days). No primary or secondary is affected.
- **pandas FutureWarning.** One warning at `solarbench/price_run.py:284`, the `pd.concat` in `forecast_all`. It concerns dtype inference only: y and y_hat are float64 by construction. The offline end-to-end test raises the same warning.
- **K1 long windows.** An unexplained K1 long-window difference (audit finding L1, recorded in AMENDMENTS.md) "may remain … and is reported with the result". It has no bearing on any scored arm, because lear_ens was not scored.

---

## 2. Primaries P1-P4

All four rules come from PRICE_SPEC:

- **Holm:** "Holm over the four primaries at alpha 0.05; a not-runnable primary enters with p = 1".
- **p:** one-sided p = (1 + #draws ≤ m)/2001, with 14-day blocks, 2000 draws and seed 0.
- **Per-year:** each year passes only if its skill is strictly above the threshold (> 0; P2 > −0.05).
- **States:** a primary gets the first state that applies, in the order 'not runnable', 'lost', 'not stable', 'lost on coverage' (P3 only), 'won'.

### P1: t0_cal vs best_simple_2023, MAE skill

| field | value | path |
|---|---|---|
| frozen state | **won** | `R#/verdicts/P1/state` |
| pooled skill | 0.227107 (0.22710738685445464) | `R#/primaries/P1/skill` |
| 95% interval | [0.186116, 0.259087] | `R#/primaries/P1/ci95` |
| raw p (one-sided) | 0.00049975 (= 1/2001) | `R#/primaries/P1/p` |
| Holm p | 0.001999 (= 4/2001) | `R#/verdicts/P1/p_holm` |
| 2024 skill | 0.225383 (366 days) | `R#/primaries/P1/yearly/2024`; days `R#/slices/P1/each year/2024/days` |
| 2025 skill | 0.228779 (365 days) | `R#/primaries/P1/yearly/2025`; days `R#/slices/P1/each year/2025/days` |
| days / hours | 731 / 17544 | `R#/primaries/P1/days`; `R#/primaries/P1/compare/hours` |
| pooled MAE (arm / ref), EUR/MWh | 15.2766 / 19.7655 | `R#/primaries/P1/compare/loss_arm`, `…/loss_ref` |
| days won / lost | 519 / 212 | `R#/primaries/P1/compare/days_won`, `…/days_lost` |
| threshold | 0.0 | `R#/verdicts/P1/threshold` |
| comparator identity | best_simple_2023 = blend_50 (2023 MAE 21.4212; runner-up prev_day 22.7481; 365 days) | `M#/selection/best`, `M#/selection/mae` |

### P2: t0_cal vs lear_ens, MAE skill, non-inferiority margin 5%

| field | value | path |
|---|---|---|
| frozen state | **not runnable** (cause: "K1 failed") | `R#/verdicts/P2/state`, `R#/verdicts/P2/cause` |
| pooled skill / 95% interval / raw p | 'not run' / 'not run' / 'not run' | `R#/primaries/P2/skill`, `…/ci95`, `…/p` |
| Holm p | 1 (Holm input 1.0) | `R#/verdicts/P2/p_holm`, `R#/verdicts/P2/p_holm_input` |
| 2024 / 2025 skill | 'not run' / 'not run' | `R#/primaries/P2/yearly/2024`, `…/2025` |
| days | 'not run' | `R#/primaries/P2/days` |
| p2_coverage | 'not run' | `R#/primaries/P2/p2_coverage` |
| runnable | false | `R#/primaries/P2/runnable` |
| threshold | −0.05 | `R#/verdicts/P2/threshold` |

### P3: t0_cal quantiles vs best_simple_eq, pinball skill

| field | value | path |
|---|---|---|
| frozen state | **won** | `R#/verdicts/P3/state` |
| pooled skill | 0.251885 (0.2518851196137203) | `R#/primaries/P3/skill` |
| 95% interval | [0.213317, 0.280905] | `R#/primaries/P3/ci95` |
| raw p | 0.00049975 (= 1/2001) | `R#/primaries/P3/p` |
| Holm p | 0.001999 (= 4/2001) | `R#/verdicts/P3/p_holm` |
| 2024 skill | 0.256492 (366 days) | `R#/primaries/P3/yearly/2024` |
| 2025 skill | 0.247378 (365 days) | `R#/primaries/P3/yearly/2025` |
| days / hours | 731 / 17544 | `R#/primaries/P3/days`; `R#/primaries/P3/compare/hours` |
| **coverage (pooled; the rule)** | **0.732786** (0.7327861377108983 = 12856/17544), inside the closed band [0.70, 0.90] | `R#/primaries/P3/coverage` |
| coverage per year (printed only) | 2024 0.722564 (6347/8784); 2025 0.743037 (6509/8760) | `R#/primaries/P3/coverage_yearly/2024`, `…/2025` |
| pooled pinball (arm / ref) | 5.45992 / 7.29824 | `R#/primaries/P3/compare/loss_arm`, `…/loss_ref` |
| days won / lost | 568 / 163 | `R#/primaries/P3/compare/days_won`, `…/days_lost` |
| threshold | 0.0 | `R#/verdicts/P3/threshold` |

### P4: t0_cal_wx vs t0_cal, MAE skill (the first price-domain test of the core product primitive)

| field | value | path |
|---|---|---|
| frozen state | **won** | `R#/verdicts/P4/state` |
| pooled skill | 0.0284216 (0.02842160653111203) | `R#/primaries/P4/skill` |
| 95% interval | [0.0114454, 0.0441206] | `R#/primaries/P4/ci95` |
| raw p | 0.0009995 (= 2/2001; one draw ≤ 0) | `R#/primaries/P4/p` |
| Holm p | 0.001999 (= 4/2001) | `R#/verdicts/P4/p_holm` |
| 2024 part (from AVAIL.p4_first_day 2024-06-06) | 0.0151408 (209 days, 5017 h) | `R#/primaries/P4/yearly/2024`; days `R#/slices/P4/each year/2024/days` |
| 2025 skill | 0.0367856 (363 days, 8712 h) | `R#/primaries/P4/yearly/2025`; days `R#/slices/P4/each year/2025/days` |
| days / hours | 572 / 13729 (2024-06-06 .. 2025-12-29) | `R#/primaries/P4/days`; `R#/primaries/P4/compare/hours` |
| days dropped | 2025-12-30 and 2025-12-31, by weather_p4.day_rule (a), the horizon rule, as the spec expects | `M#/forecast/p4_days/dropped/horizon` |
| pooled MAE (arm / ref), EUR/MWh | 15.6352 / 16.0926 (difference 0.457) | `R#/primaries/P4/compare/loss_arm`, `…/loss_ref` |
| days won / lost | 307 / 265 | `R#/primaries/P4/compare/days_won`, `…/days_lost` |
| prerequisites | K3 passed; 572 P4 days scored | `M#/k3/pass`; `M#/forecast/p4_days/kept` |
| threshold | 0.0 | `R#/verdicts/P4/threshold` |

### Holm, recomputed by R and S

| rank | primary | raw p | step | Holm p |
|---|---|---|---|---|
| 1 | P1 | 1/2001 | 4 × 1/2001 | 0.0019990 |
| 2 | P3 | 1/2001 | max(…, 3/2001) | 0.0019990 |
| 3 | P4 | 2/2001 | max(…, 2 × 2/2001) | 0.0019990 |
| 4 | P2 | 1 (not runnable) | max(…, 1) | 1 |

### Reading-table rows, exactly as printed in `summary.md`

R confirmed each row byte-identical to `PRICE_SPEC["reading_table"]`:

- **Row key "P1 won, P2 not runnable":** "t0 beats the best simple rule; the comparison with LEAR was not made (K1 failed or LEAR forecast too few days), so nothing is concluded about LEAR."
- **Row key "P3 won":** "t0's native bands score better than simple empirical bands, and its 10-90 band covers 70-90% of scored hours."
- **Row key "P4 won":** "Public weather forecasts issued before the gate add value to t0 on prices (P4 days only)."
- **No 'not stable' row is printed,** which is correct because no primary has that state.

The complete `summary.md` (1961 bytes; it equals the run's stdout copy):

```
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
```

### Strict check (report-only; never changes a primary's state)

- **Why it is read:** the strict row is read because P1 is 'won'.
- **Rule:** "beats" means MAE skill > 0 pooled, in 2024 and in 2025, with no interval and no p.
- **Result:** t0_cal_strict beats best_simple_2023 on all three. So the frozen first sentence applies: **"P1 does not rest on t0 reading the D-1 afternoon prices."**

| comparison | pooled | 2024 | 2025 | days | path |
|---|---|---|---|---|---|
| t0_cal_strict vs best_simple_2023 | 0.067768 | 0.0809742 | 0.0549668 | 731 | `R#/strict/best_simple_2023` |
| t0_cal_strict vs best_simple_2023_strict | 0.153247 | 0.159079 | 0.147675 | 731 | `R#/strict/best_simple_2023_strict` |

`R#/strict` equals the two matching secondaries exactly (S).

---

## 3. Secondaries, slices, concentration and carry-forward (all report-only)

None of these change a state. Intervals and p are not adjusted for multiplicity.

### Secondaries (`R#/secondaries/<name>`), each on 731 days

| secondary | skill | 95% interval | one-sided p | 2024 | 2025 | won / lost days | MAE arm / ref |
|---|---|---|---|---|---|---|---|
| t0 (no calendar) vs best_simple_2023 | 0.206327 | [0.167606, 0.236407] | 0.00049975 | 0.200744 | 0.211739 | 514 / 217 | 15.6874 / 19.7655 |
| **t0_cal vs t0** (value of the holiday calendar) | 0.0261824 | [0.00265033, 0.0531526] | 0.0164918 | 0.0308277 | 0.0216166 | 429 / 302 | 15.2766 / 15.6874 |
| t0_cal_strict vs best_simple_2023 | 0.067768 | [0.0264149, 0.102263] | 0.00149925 | 0.0809742 | 0.0549668 | 427 / 304 | 18.4261 / 19.7655 |
| t0_cal_strict vs best_simple_2023_strict | 0.153247 | [0.113678, 0.185828] | 0.00049975 | 0.159079 | 0.147675 | 488 / 243 | 18.4261 / 21.7608 |
| t0_cal vs t0_cal_strict (value of the D-1 afternoon to t0) | 0.170922 | [0.140721, 0.198385] | 0.00049975 | 0.157132 | 0.183922 | 460 / 271 | 15.2766 / 18.4261 |
| lear_ens vs best_simple_2023 | not run: "lear_ens not scored (K1 failed)" | | | | | | |
| t0_cal vs lear_ens (superiority) | not run: "lear_ens not scored (K1 failed)" | | | | | | |
| lear_ens + empirical bands vs t0_cal bands | not run: "lear_ens_eq not scored (K1 failed)" | | | | | | |

**t0 vs best_simple and t0_cal vs t0.** Without the calendar, t0 already has skill 0.206 against best_simple_2023 (first row). The holiday calendar adds a further 0.026 (t0_cal vs t0: one-sided p 0.016, not adjusted, interval above 0).

S checked transitivity on these rows: (1−s(t0_cal,t0))·(1−s(t0,bs)) = 1 − s(P1), to within 1e-13.

**rMAE** (`R#/secondaries/rMAE vs naive_std and vs prev_week/<ref>/<arm>/rmae`). All on 731 days, except t0_cal_wx on 572.

| arm | vs naive_std | vs prev_week |
|---|---|---|
| t0_cal_wx (572 days) | 0.641771 | 0.502149 |
| t0_cal | 0.668398 | 0.519269 |
| t0 | 0.686369 | 0.533231 |
| t0_cal_strict | 0.806195 | 0.626322 |
| best_simple_2023 | 0.864801 | 0.671852 |
| best_simple_2023_strict | 0.952101 | 0.739674 |
| naive_std | — | 0.776886 |
| prev_week | 1.28719 | — |
| lear_ens | not run (K1) | not run (K1) |

The implied pooled MAE is 22.8556 EUR/MWh for naive_std and 29.4195 for prev_week (S).

**RMSE** (`R#/secondaries/RMSE`):

- P1 (731 days): t0_cal 21.2457, best_simple_2023 26.3251.
- P4 (572 days): t0_cal_wx 21.5307, t0_cal 22.1785.
- P2: not run (K1).

### Slices (`R#/slices/<P>/<slice>`)

Skills are rounded to 4 decimals. Intervals and p are not adjusted for multiplicity.

| slice | P1 skill [95%] (days) | P3 pinball skill [95%] (days) | P4 skill [95%] (days) |
|---|---|---|---|
| 2024Q1 | 0.2828 [0.1907, 0.3631] (91) | 0.3569 [0.2643, 0.4248] (91) | no days |
| 2024Q2 | 0.1188 [0.0731, 0.1956] (91) | 0.1545 [0.1215, 0.2267] (91) | −0.0172 [−0.0600, 0.0009] (25; p 0.970) |
| 2024Q3 | 0.2237 [0.1725, 0.2915] (92) | 0.2391 [0.2030, 0.2959] (92) | 0.0057 [−0.0312, 0.0455] (92) |
| 2024Q4 | 0.2762 [0.1604, 0.3611] (92) | 0.2909 [0.1869, 0.3688] (92) | 0.0323 [−0.0120, 0.0660] (92) |
| 2025Q1 | 0.3576 [0.2759, 0.4193] (90) | 0.3592 [0.2780, 0.4208] (90) | 0.0633 [0.0144, 0.1158] (90) |
| 2025Q2 | 0.0698 [0.0252, 0.1471] (91) | 0.0932 [0.0454, 0.1797] (91) | 0.0260 [−0.0220, 0.0837] (91) |
| 2025Q3 | 0.1927 [0.1371, 0.2336] (92) | 0.2211 [0.1426, 0.2614] (92) | 0.0104 [−0.0150, 0.0239] (92) |
| 2025Q4 (quarter-hour derived) | 0.2430 [0.1405, 0.3165] (92) | 0.2728 [0.1975, 0.3303] (92) | 0.0479 [0.0134, 0.0808] (90) |
| April-September | 0.1551 [0.1229, 0.1948] (366) | 0.1799 [0.1480, 0.2171] (366) | 0.0112 [−0.0088, 0.0333] (300; p 0.149; won/lost 144/156) |
| weekends and holidays | 0.2660 [0.2194, 0.3063] (228) | 0.2862 [0.2257, 0.3329] (228) | 0.0187 [−0.0147, 0.0410] (178) |
| weeks after each DST switch | **−0.0536** [−0.1569, 0.1437] (28; p 0.300) | **−0.0580** [−0.2290, 0.1511] (28; p 0.351) | 0.0427 [−0.0361, 0.1044] (21) |
| negative-price hours | 0.2660 [0.1660, 0.3255] (163 d / 865 h) | 0.2234 [0.1312, 0.2775] (163 d / 865 h) | 0.0459 [−0.0148, 0.0924] (131 d / 689 h) |
| top 1% absolute prices | 0.1595 [0.1174, 0.3138] (45 d / 176 h) | 0.0496 [−0.0055, 0.3296] (45 d / 176 h) | 0.0382 [0.0042, 0.1090] (36 d / 138 h) |
| 11:00-16:00 local | 0.2104 [0.1624, 0.2453] (731) | 0.2295 [0.1855, 0.2610] (731) | 0.0458 [0.0189, 0.0754] (572; p 0.0005) |

P2's slices all read 'not run' (`R#/slices/P2`).

**Notable slices (report-only):**

- **P1 and P3 in the weeks after each DST switch.** Both are negative, on 28 days, with intervals spanning 0.
- **The weakest quarter.** For both P1 and P3 it is 2025Q2: 0.0698 and 0.0932.
- **P3 at the top 1% absolute prices.** The interval includes 0 (0.0496 [−0.0055, 0.3296]).
- **P4 by period.**
  - Positive, with an interval above 0, in 2025Q1, 2025Q4, the top 1% hours and 11:00-16:00 local.
  - Negative in its first partial quarter, 2024Q2: 25 days, and the interval only just includes 0.
  - In April-September its interval includes 0, and it won fewer days than it lost (144 / 156).

### Concentration and bootstrap sensitivity (`R#/tables/<P>`)

| | P1 | P3 | P4 |
|---|---|---|---|
| top 5 days' share of net gain | 6.5% | 6.9% | **28.4%** |
| skill without top 5 | 0.2169 | 0.2400 | 0.0207 |
| top 10 share / skill without | 11.1% / 0.2096 | 11.9% / 0.2316 | **49.3%** / 0.0149 |
| top 20 share / skill without | 19.1% / 0.1965 | 20.2% / 0.2171 | **83.4%** / 0.0051 |
| 95% interval, block 1 / 30 days | [0.1960, 0.2550] / [0.1819, 0.2651] | [0.2227, 0.2798] / [0.2104, 0.2839] | [0.0113, 0.0448] / [0.0105, 0.0483] |

- **Paths:** `R#/tables/<P>/concentration` and `R#/tables/<P>/bootstrap_sensitivity`.
- **Concentration.** P1 and P3 gains are broad-based. P4's gain is concentrated: the best 20 of 572 days carry 83.4% of the net gain, and without them its skill is 0.0051.
- **Sensitivity.** Every primary's interval stays above 0 at every block length from 1 to 30 days. The block-14 row equals each `ci95` bit for bit (S).

### Carry-forward (`R#/carry_forward/<P>`)

The rule: "vault candidate only if state 'won' and some delta in {0, 0.05, 0.10, 0.20} satisfies S − delta ≥ M". It is evaluated on April-September of 2024 and 2025.

| primary | state | A days | S | M (α 0.0125) | block_sd | ref_mae | delta | candidate | M at α/2, /3, /4 (info) |
|---|---|---|---|---|---|---|---|---|---|
| P1 | won | 366 | 0.155133 | 0.1223 | 2.343 | 18.998 | **0** | **true** | 0.1361, 0.1442, 0.15 |
| P2 | not runnable | — | — | — | — | — | null | false | — |
| P3 | won | 366 | 0.179853 | 0.117 | 0.822 | 6.968 | **0.05** | **true** | 0.1302, 0.1379, 0.1434 |
| P4 | won | 300 | 0.011223 | 0.0489 | 0.789 | 16.005 | null | **false** | 0.0544, 0.0577, 0.06 |

- **Expressible today.** `PRICE_SPEC.carry_forward.expressible_today` reads: "P1 (vs best_simple) and P4 (vs accepted, once P1's arm is accepted); P2 and P3 need vault extensions".
  - Only P1 is a candidate that can be stored in the vault today.
  - P3 is a candidate by the rule but needs a vault extension.
  - P4 wins on the frozen reading but is not a vault candidate (S 0.0112 < M 0.0489).
- **Route.** The route into the vault is the owner's decision; the default is an engine price lane after B1 opens.
- **Margins.** The smallest margin in any carry-forward decision is 0.013 (P3 at delta 0.05). So the 4-decimal storage of M decides nothing.

---

## 4. Gates and provenance

### K1 (LEAR reproduces the published EPF-FR results): FAILED after 3 attempts, the third under amendment A1

- **Run record.** `M#/k1` = {attempts 3, passed false, passing_attempt null, over_budget false, log_present true, log_sha256 b111286d…}. That hash equals sha256(`docs/experiment_4/k1_attempts.jsonl` @2b407f4).
- **Limits (PRICE_SPEC `gates.K1.tolerance`):**
  - every one of the 17,472 hours forecast;
  - ensemble MAE deviation in [−2%, +1%];
  - each window's deviation in [−3%, +2%];
  - mean absolute difference from the published "LEAR Ensemble" ≤ 0.25 EUR/MWh.

| attempt | commit | run | lear.py sha256 | ensemble MAE dev. | windows 56 / 84 / 1092 / 1456 | mean abs diff (≤ 0.25) | failed check |
|---|---|---|---|---|---|---|---|
| 1 | d861b78 | 36697501545 | 3abae213… | +0.22% | −1.60% / −0.36% / +0.02% / +0.02% | 0.548 | mean_abs_diff_ensemble |
| 2 | d799add (hour-major columns) | 36712555696 | c36ad5de… | +0.26% | −1.60% / −0.36% / +0.14% / +0.21% | 0.558 | mean_abs_diff_ensemble |
| 3 (A1, final) | 62bcf38 | 36780460835 | 7770361a… | +0.09% | +0.53% / +0.36% / +0.14% / +0.21% | **0.408** (0.4076) | mean_abs_diff_ensemble |

- **Final status.** All three attempts forecast every hour and met every MAE tolerance. Each failed only the 0.25 EUR/MWh mean-absolute-difference limit.
- **Timing of the attempts.** All three ran before the freeze commit; their commits are ancestors of 2b407f4 (I).
- **LEAR code unchanged.** `M#/lear_sha256_start` = `M#/lear_sha256_end` = 7770361a… = attempt 3's lear.py = sha256(`solarbench/lear.py` @2b407f4).
- **Amendment A1** (owner-approved 2026-09-30; `M#/amendments` = {ids ["A1"], sha256 354f8e4c…} = `AMENDMENTS.md` @2b407f4):
  - It superseded LEAR penalty step (1) only, so that it reproduces scikit-learn ≤ 0.23.1, as the published forecasts were made.
  - It changed no threshold and no other rule.
  - It made attempt 3 final regardless of outcome.
  - It moved the short windows as predicted and left the long windows unchanged.
  - Because K1 failed, A1 affects no scored arm. It stays recorded because the K1 attempt it governed counts.
- **Consequence.** Under `lear.scored_only_if`, lear_ens and lear_ens_eq are not scored, and both are absent from `M#/scored_arms`. As a result:
  - P2 reads 'not runnable' (Holm p 1).
  - The three LEAR secondaries, lear_ens rMAE and RMSE P2 all read 'not run' with cause K1.
  - No LEAR leak control was run, which is correct.
- **Long windows (L1).** An unexplained long-window difference remains, as AMENDMENTS.md records.

### K2 (t0 adapter parity): PASSED

- **Check run.** `M#/k2_attempts/0` is check run 36820039916 at e47a6e9, pass. It is identical to the single line of `docs/experiment_4/k2_attempts.jsonl`; `M#/k2_log/sha256` 3b18f984… equals that file.
- **This run.** `M#/k2_attempts/1` is this run, and `M#/k2_record` = {run_id 36823477529, commit 2b407f4, pass true}.
- **Coverage.** t0, t0_cal and t0_cal_strict were checked at all 11 TEST_ORIGINS. t0_cal_wx was checked at the 9 origins on or after 2024-06-06.
- **Results.** Every single window was bit-identical, and the batch max abs diff was ≤ 5.34e-05 against the 0.01 tolerance.
- **Windows and horizons.** t0, t0_cal and t0_cal_wx: cutoff windows, 25 h. t0_cal_strict: strict windows, 36 h.
- **Code.** Between e47a6e9 and 2b407f4 the only change is the appended K2 log line (I).

### K3 (weather port carries a usable signal): PASSED

`M#/k3/pass` is true. Period 2023-10-02..2023-12-03: 63 days, all built, none dropped. There were 0 non-finite warnings and no sanitised output in any arm.

| convention | planted_ratio (≤ 0.95) | decoy_ratio ([0.98, 1.10]) | shift_penalty (≥ 1.01) | path |
|---|---|---|---|---|
| instant (wx_temperature port) | 0.3049 | 0.9970 | 1.3012 | `M#/k3/conventions/instant` |
| mean_preceding_hour (wx_radiation port) | 0.3012 | 0.9943 | 1.4574 | `M#/k3/conventions/mean_preceding_hour` |

### In-run leak check: PASSED

- **Result.** `M#/leak_check/pass` is true. All 459 leaves are boolean `true`.
- **Origins.** The 11 TEST_ORIGINS plus `p4_first_day:2024-06-06`. The whitelist passes for t0, t0_cal, t0_cal_strict and t0_cal_wx.
- **Controls present on the arms they name:**
  - target poisoning (affine and NaN);
  - the legal-change controls;
  - best_simple_eq's error-quantile control;
  - covariate issue-time refusal;
  - the strict-rule controls;
  - context_end;
  - for t0_cal_wx, the weather after-d and +50 controls, at the origins on or after 2024-06-06.
- **Order.** The leak check ran before K2, and K2 before `forecast_all`.

### Integrity, data and sources

- **Spec.** `M#/spec_sha256` = `M#/pinned_spec_sha256` = 225774c89e301166c2d4850e2f894335fd5ae703dc410bc4a06aa246ac5755bc = `PRICE_SPEC_SHA256`, recomputed locally at 2b407f4. `M#/avail` equals `AVAIL` (avail run 36610144690).
- **Commit and run.** `M#/commit` 2b407f4 (from GITHUB_SHA) and `M#/run_id` 36823477529.
- **Test suite.** 501 tests passed before the run step.
- **Run step.** 06:21:22-06:59:58 (38.6 min). Apart from the 66 HTTP 429 retries, it logged no errors, no tracebacks and no STOPPED line.
- **Versions** (`M#/versions`): Python 3.11.16, numpy 2.4.6, pandas 2.3.3, scikit-learn 1.7.2, torch 2.14.0+cpu, tfc-t0 0.3.2, huggingface-hub 1.31.0.
- **Prices** (`M#/prices`), scored source Energy-Charts, bzn=FR, stamp "start":
  - 53,352 hours, which is 2,223 days 2019-12-01..2025-12-31.
  - 51,143 native hours plus 2,209 from quarter-hours (Q4 2025).
  - 0 incomplete and 0 off-grid hours.
- **Cross-check** (`M#/agreement`), SMARD filter 254, "Marktpreis: Frankreich":
  - All 34,992 hours of 2022-01-01..2025-12-28 agree: 0 differing and max abs diff 0.0.
  - 2024-06-26 is printed and identical in both sources.
  - 2025-12-29..31 are "not cross-checked", as the rule says.
- **Licence** (`M#/licence`): 73 files, 0 refusals. The one string seen is "CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur | SMARD.de", which is in AVAIL.
- **Attribution** (`R#/attribution`): "Day-ahead prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE)".
- **Weather** (`M#/weather`), ECMWF IFS 0.25° previous_day3 through the frozen engine constants:
  - wx_temperature: 16,655 cells from 2024-02-06.
  - wx_radiation: 15,889 cells from 2024-03-08.
  - Both end 2025-12-30 22:00Z.
- **Windows** (`M#/forecast`):
  - Test windows: 731 built (366 + 365), 0 incomplete.
  - Strict windows: 731 built, 0 incomplete.
  - P4 days: 574 candidates, 572 kept.
  - t0 context and sanitised misses: none for any t0 arm.
- **Missing days** (`M#/missing_by_arm`). Every arm has 0 missing over its days. The one exception is t0_cal_wx: 2 of 574 missing, both on the horizon rule (2025-12-30 and 2025-12-31).
- **Scored arms** (`M#/scored_arms`): best_simple_2023, best_simple_2023_strict, best_simple_eq, naive_std, prev_week, t0, t0_cal, t0_cal_strict, t0_cal_wx.
- **Artifact.** `prices-run-36823477529`, ID 11145568607, 8 files. The four printed files match; the other four were not checked (§1).

### t0 weights: retrieval event (docs/experiment_4/RETRIEVAL_EVENTS.md)

- **What happened.** The frozen revision 9b02c5f4bb6c89ba15d9fa74554018fe6464220b of `theforecastingcompany/t0-alpha` vanished upstream in a history rewrite.
- **Owner's decision (2026-09-30).** Keep the spec unchanged and load t0 by content. Both files must match the pinned sha256, or the run aborts before forecasting.
- **This run** (`M#/t0_weights`):
  - frozen_revision 9b02c5f4…;
  - served_by_revision fdd189642a529fee59ba7d491235a06779e41a83 (the Hub head recorded in the event);
  - config.json b2b54568… and model.safetensors 16c030d3…, both equal to the pinned hashes;
  - `verified: true`.
- **Run log.** At 06:21:27 it reads "frozen bytes of 9b02c5f4… verified, fetched from the Hub head fdd18964…".

---

## 5. Plain-language reading for the owner

**The four questions, by their frozen rules:**

1. **Question 1: does t0 beat the best simple price rule? Frozen state: WON.**
   - Using only past prices and the holiday calendar, t0's day-ahead forecasts of French prices had about 23% smaller average error than the best simple rule chosen on 2023. On average that is 15.3 against 19.8 EUR/MWh.
   - It held in each year separately: about 23% in 2024 and 23% in 2025.
   - A robustness check asked whether this depends on t0 seeing the previous afternoon's prices. Without them, t0 still beats the same simple rule in both years. So, by the frozen rule, "P1 does not rest on t0 reading the D-1 afternoon prices."
2. **Question 2: is t0 within 5% of the standard free price model (LEAR)? Frozen state: NOT RUNNABLE.**
   - The comparison was not made. Before LEAR could be used, our rebuild of it had to reproduce its published results closely. It failed that check (K1) on all three permitted attempts, the last under the owner-approved amendment A1.
   - Its average errors matched the published ones within tolerance, but its individual forecasts differed from the published forecasts by 0.41 EUR/MWh on average, against a 0.25 limit.
   - **Nothing is concluded about how t0 compares with LEAR.** This is neither a win nor a loss for t0.
3. **Question 3: are t0's built-in uncertainty bands better than simple bands, and honest? Frozen state: WON.**
   - t0's bands scored about 25% better than simple empirical bands, in both years.
   - Its 10-90% band contained the actual price in 73.3% of hours, inside the 70-90% range the test requires.
4. **Question 4: do public weather forecasts help t0 on prices? Frozen state: WON.**
   - The frozen reading is: "Public weather forecasts issued before the gate add value to t0 on prices (P4 days only)."
   - **This is the first test on prices of the project's core product idea**: that extra public information, given to t0 as inputs, improves its forecasts. Here the inputs were temperature and sunshine forecasts issued before the noon decision.
   - It ran only after the weather plumbing passed its planted-signal check (K3).
   - The gain is small: about 2.8% lower average error, 16.09 to 15.64 EUR/MWh, over 572 days from 6 June 2024 to 29 December 2025. It was positive in the 2024 part (1.5%) and in 2025 (3.7%).

**Context that does not change any verdict:**

- **The weather gain is concentrated.** The best 20 of 572 days account for about 83% of it. With weather, t0 did better on 307 days and worse on 265.
- **The weather gain in April-September.** For that period it is 1.1%, with a range that includes zero. That is below 4.9%, the smallest gain the vault test could detect on that period (M). So under the frozen carry-forward rule, question 4 is **not** a candidate for the forward vault.
- **Candidates for the vault.** Question 1 is a candidate that can be stored in the vault today. Question 3 is a candidate but needs a vault extension first. Which route, if any, is your decision.
- **Weakest periods.** The weeks right after the clock changes were the one reported period where t0 did slightly worse than its comparator on questions 1 and 3. That is 28 days, and the range includes zero.

**What this result is and is not:**

- **Experiment 4 is discovery-grade.** The 2024-2025 French prices are public and already studied, and 2025 was already used once. **No result here counts as confirmed.**
- **It cannot by itself satisfy the project's independent-confirmation milestone.** Only a claim frozen in advance and then confirmed on data that did not exist when it was frozen can do that. That means the engine's sealed forward vault, opened once with your approval.
- **The checks behind the numbers.**
  - The run's code, data, gates, leak checks and reading were verified with no defects found.
  - The published wording is exactly the frozen reading table's.
  - One limit remains: the per-day files could not be downloaded. The error ranges and p-values are therefore taken from the run, where they are internally consistent, but were not recomputed independently.
