# Blind replication packet: Experiment 4 (t0 on French day-ahead prices)

You are to compute Experiment 4's statistics **independently**, from this packet alone.

**Data:** `forecasts.csv.gz` is the scored run's original hourly forecast table, authenticated against GitHub's
upload digest. It has one row per (method, delivery hour) and these columns:

| Column | Meaning |
|---|---|
| `delivery_date` | Paris delivery day D |
| `method` | the arm |
| `target_time` | UTC start of the hour |
| `local_time` | the same hour in Paris time |
| `y` | observed price, EUR/MWh |
| `y_hat` | the point forecast |
| `source_latest` | the latest price stamp the forecast read |
| `cov_issued_latest` | latest weather issue time; `t0_cal_wx` only |
| `q10`, `q25`, `q50`, `q75`, `q90` | quantile forecasts, where the arm has them |

Read the file with `pandas.read_csv(..., float_precision="round_trip")`.

**The arms:**
- `t0`, `t0_cal` (t0 with the holiday calendar) and `t0_cal_wx` (t0_cal with weather; P4 days only);
- `t0_cal_strict` (sees prices only up to 12:00 D-1);
- `best_simple_2023`, the simple rule chosen on 2023, and `best_simple_2023_strict`;
- `best_simple_eq`, which has empirical bands;
- `naive_std` and `prev_week`.

There are no LEAR arms.

**The rules:** `spec_excerpt.json` holds verbatim sections of the frozen specification. The relevant ones are
`statistics`, `probes`, `periods`, `report_only`, `carry_forward` and `AVAIL`. They define every quantity you
compute. Where they name a repository function, its documented behaviour is given below. Its code is deliberately
not.

**Other inputs:**
- `p4_kept_days.json` lists P4's day set as the run recorded it. The rule that chose it needs weather issue times,
  which this packet does not contain.
- P2 (t0_cal against LEAR): its reproduction gate K1 failed on all three attempts. So P2 is "not runnable" and enters
  Holm with p = 1. It has no table.

## Documented behaviour of the functions the spec names

**`metrics.bootstrap_skill(per_day, *, model, reference, block_days, samples, seed, return_draws)`**
- Its docstring: "Moving-block bootstrap CI for the skill of `model` over `reference`. Blocks of whole [block_days
  days], because forecast errors on consecutive days share a weather regime and an i.i.d. resample would understate
  the uncertainty. Each resample recomputes the skill from pooled sums — a skill score is a ratio of totals, not an
  average of daily ratios."
- `per_day` has one row per (delivery_date, method), with `sum_abs_err` (the per-day loss sum) and `n` (the hours).
- Dropped days are skipped, not left as gaps.

**`metrics.concentration(per_day, *, model, reference, top=(5, 10, 20))`**
- Its docstring: "How much of the model's net gain over the reference sits in its best days. Descriptive, no
  interval: the share of the net absolute-error reduction carried by the top-N days, and the skill once those days
  are removed."

**`engine.referee.stats.blocks(per_day, arm, ref, delta, block_days=14, start=None)`**
- Its docstring: "Block means of the shifted loss difference `(1 - delta) * loss_ref - loss_arm`. Blocks are
  *calendar* spans of `block_days` from `start` (default: the first common day), so a missing day shrinks one block
  instead of shifting every later one; a block counts only with at least `MIN_DAYS_PER_BLOCK` common days."
- `MIN_DAYS_PER_BLOCK = 10`.
- The per-day loss is the daily mean loss: `sum_abs_err / n`.

**`engine.referee.stats.power_table(per_day, arm, ref, alpha, blocks_list=(6, 8, 12))`**
- Its docstring: "Minimum detectable skill (80% power, approx.) from the spread of 14-day block means."
- Its formula, as a written statement (it is not in the spec text, so a result built on it is "conditional on the
  code's formula"):
  - Take the block means b from `blocks(per_day, arm, ref, delta=0)`, at least 3 of them.
  - `sd` is the sample standard deviation of b (ddof = 1).
  - `ref_mae = Σ ref sum_abs_err / Σ ref n` over A.
  - For each k in (6, 8, 12): `M_k = (t_crit(k − 1, alpha) + 0.8416) · sd / sqrt(k) / ref_mae`, rounded to 4
    decimals. `t_crit(df, alpha)` is the one-sided upper-alpha critical value of Student's t.
  - It reports `block_sd` and `ref_mae` rounded to 3 decimals, and `min_detectable_skill[str(k)] = M_k`.

**`run_covariates.holm(pvalues)`** returns Holm step-down adjusted p-values, in the input order, capped at 1.

## Rules for you
- Read only the files in this packet directory.
- Do not read the repository (`/home/user/solar`), any `results.json`, `summary.md`, fact sheet, README or
  verification report, or any code under `solarbench/` or `engine/`.
- List every file you read.
