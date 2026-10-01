# Experiment 4: independent replication of the scored run's statistics

*Written 2026-10-01, after the owner approved closing the verification gap. Nothing in Experiment 4 was changed:
the frozen specification, its methods, thresholds and source data, and every reported result stay as they were.
No forecast was rerun.*

## Summary

- **Verdict: independently reproduced, with no defect found.** An analyst who never saw the run's code or
  results worked from the run's original hourly forecasts and the frozen specification text. It reproduced every
  primary skill, interval, p-value, Holm adjustment and state. It also reproduced P3's coverage, P4's concentration
  and every carry-forward decision.
- **Comparison:** 614 published fields were compared:
  - 520 matched exactly;
  - 90 matched within the Monte-Carlo tolerance fixed in advance;
  - 4 disagreed, and all 4 are explained below.
- **Discrepancies:** the 4 disagreements sit in two report-only P4 slices of 25 and 21 days. The specification does
  not settle the block length the bootstrap should use on series that short. They are not defects and change
  nothing.
- **Re-execution of the frozen code:** run on the same forecasts, it reproduces the published `results.json`,
  `summary.md` and every per-day table byte for byte. This check is not independent.
- **Limits:** forecast generation itself, the gates (K1–K3), the leak check and the choice of P4's days could not
  be re-derived from the artifact. They remain checked for internal consistency only, or not independently
  verified (sections 3 and 4).

## 1. The original evidence and its provenance

**Retrieval.** The run's per-day files existed only in its Actions artifact, and this session's network proxy
refuses the artifact's storage host. With the owner's approval, the one-off workflow
`.github/workflows/exp4-evidence-copy.yml` (run [36844558893](https://github.com/xuanhuyle/solar/actions/runs/36844558893))
did three things:
- downloaded the artifact zip through the GitHub API;
- required its sha256 to equal the digest GitHub recorded when the artifact was uploaded;
- pushed the zip, unchanged, to the new orphan branch `evidence/exp4-run-36823477529` (commit `4c508ca`), with the
  API records and a member manifest.

The workflow runs no forecast and reads no data source.

| Item | Value |
|---|---|
| Source run | [36823477529](https://github.com/xuanhuyle/solar/actions/runs/36823477529), commit `2b407f42c03d2734ef4170cfb3e66962dbba9552` (the freeze commit) |
| Artifact | `prices-run-36823477529`, id 11145568607, 5,588,744 bytes, expires 2026-12-30 (the branch copy does not) |
| Zip sha256 | `98d8ca1f7c6f8f6bdfeba807b925bfee25ed1cd9da7a5e46b24acc88be436165`, equal to the digest recorded at upload and to the digest the GitHub API reported again at check time |
| `forecasts.csv.gz` | sha256 `295dd6801513f85865c3651536c34aa75e34e5bcb3ed33fdd9a720746c31ab7a`; 154,081 rows, 9 arms |
| `per_day_P1.csv` | `b684fb20362210bc779d20794b6b60a0189b79a28cfe03c8d85fdc031f5dad11` |
| `per_day_P3.csv` | `180953fcd4dde0a4966268956c155e698a5e8af48f4a22074245ae78c4ebdc50` |
| `per_day_P4.csv` | `79c9f1f6614905d62c41d2e8c9b0e51d51f2af2243524b4d358ace0fa41d3d71` |

**Authentication.** `replication/provenance.py` ran 26 checks; all passed (`replication/provenance.json`):
- the zip digest matches;
- the members equal the copying workflow's manifest;
- the four files the run printed to its log are **byte-identical** to the copies committed in `scored_run/`;
- the commit and run ids are the scored run's;
- the arm set is the scored set;
- every arm has every hour of each of its days (23, 24 or 25);
- each hour has one observed price shared by all arms;
- every per-day file equals, **bit for bit**, the per-day sums of the hourly forecasts;
- P4's 572 days equal the run's recorded list;
- point in time: every price an arm read is stamped no later than its window allows (23:00 D-1 Paris, or 12:00 D-1
  for the strict arms), and every weather input of `t0_cal_wx` was issued by 12:00 D-1 Paris. This rests on the
  run's own per-row provenance columns.

**Tolerances were fixed before comparing.** `replication/TOLERANCES.md` was committed (`0aeee24`) before any
replicated value was compared with a published one.

## 2. Independently reproduced

**Track 1, blind re-implementation** (`replication/blind/`):
- **What the analyst received:** a packet holding only:
  - the original `forecasts.csv.gz`;
  - verbatim sections of the frozen specification;
  - P4's recorded day list;
  - the documented behaviour (docstrings, not code) of the functions the specification names.
- **What it never received:** the published results, the fact sheet, the README or any code under `solarbench/` or
  `engine/`.
- **What it produced:** its own implementation in numpy and pandas only (`blind_replicate.py`), with 18 recorded
  assumptions.
- **Reproducibility:** rerun from a clean copy of the packet, the script reproduces its outputs exactly.
- **Comparison:** `replication/compare_blind.py` → `compare_blind.json`.

| Quantity | Published (frozen run) | Blind re-implementation | Agreement |
|---|---|---|---|
| P1 skill, t0_cal vs best_simple_2023 (MAE) | 0.227107 | 0.227107 | bit-identical |
| P1 95% interval | [0.186116, 0.259087] | same | ≤ 1.2e-15 relative |
| P1 one-sided p; 2024 / 2025 | 1/2001; 0.225383 / 0.228779 | same | exact |
| P3 pinball skill, t0_cal vs best_simple_eq | 0.251885 | 0.251885 | bit-identical |
| P3 95% interval | [0.213317, 0.280905] | same | ≤ 1e-15 relative |
| P3 coverage of the 10–90 band (pooled; 2024; 2025) | 0.732786; 0.722564; 0.743037 | same | exact |
| P4 skill, t0_cal_wx vs t0_cal (MAE) | 0.0284216 | 0.0284216 | bit-identical |
| P4 95% interval | [0.0114454, 0.0441206] | same | ≤ 1e-13 relative |
| P4 one-sided p; 2024 part / 2025 | 2/2001; 0.0151408 / 0.0367856 | same | exact |
| Holm (P1, P2, P3, P4), with P2 entering at p = 1 | 0.001999, 1, 0.001999, 0.001999 | same | exact |
| States | won, not runnable, won, won | same | exact |
| P4 concentration: share of net gain in the top 5 / 10 / 20 days | 28.4% / 49.3% / 83.4% | same | exact |
| P4 skill without the top 20 days | 0.00506 | same | exact |
| Carry-forward P1: S, M, delta, candidate | 0.1551, 0.1223, 0, yes | same | exact |
| Carry-forward P3: S, M, delta, candidate | 0.1799, 0.1170, 0.05, yes | same | exact |
| Carry-forward P4: S, M, delta, candidate | 0.0112, 0.0489, none, no | same | exact |

**Field counts.** Of the 614 compared fields:

| Kind of field | Fields | Agreement |
|---|---|---|
| Deterministic: skills, per-year skills, day and hour counts, pooled losses, days won and lost, coverage, concentration, rMAE, RMSE, carry-forward S, block_sd and ref_mae | 397 | exact |
| Categorical (states) | 19 | exact |
| Rounded (M and its information values) | 18 | exact at the published precision |
| Bootstrap interval endpoints and p-values | 180 | see below |

**The bootstrap fields:**
- **Agreement.** 174 of the 180 equal the published value at seed 0 within 1e-12 relative, and 86 of those are
  bit-identical. The remaining differences are summation order.
- **How the analyst got there.** Working from the specification's words "14-day blocks, 2000 draws, seed 0", it
  wrote a standard moving-block bootstrap that draws the same blocks as the run's.
- **The other 6** are the two short P4 slices of section 5:
  - 4 are discrepancies;
  - 2 agree only within the Monte-Carlo band, and by coincidence, since the procedures differ there.

The pre-declared rule judged the 90 endpoints that are not bit-identical against the spread of the blind bootstrap
over seeds 0–199. All 90 fall inside it.

**Also reproduced:**
- the 5 computed secondaries and the strict comparisons (skill, interval, p and per-year values);
- every slice skill, day count and hour count;
- the block-length sensitivity table: 30 endpoints, all within 3e-14 of the published values.

**What "conditional" means for M.**
- M, the smallest skill the vault test could detect, comes from a formula that is in the engine's code, not in the
  specification's text.
- The analyst received that formula as a written statement and implemented it with its own Student-t quantile
  (scipy).
- M therefore matches **conditionally on the code's formula**. The formula itself is not independently derived.

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
- **The gates and the leak check:** K1 (failed), K2 and K3 (passed), and the in-run leak check (459 of 459 passed).
  Their inputs are not in the artifact.
- **219 published fields that the blind outputs do not cover.** None is a primary or a state. They are:
  - slice days won and lost;
  - the slice margins;
  - "not run" placeholders;
  - the rMAE day counts;
  - the verdict thresholds;
  - P2's carry-forward placeholders.

  The block-length sensitivity endpoints are also in this list, but they were compared directly instead (section 2).

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
  - With the same block length, both implementations give identical draws.
- **Classification.** One skeptic reviewed each discrepancy independently with full access to the code. All four
  concluded class (b), not a defect:
  - the published values are exactly what the specification's named call produces;
  - that function's behaviour predates the freeze (commit `0a32dc1`).
- **Materiality.** None changes a state, a Holm decision, the coverage band, carry-forward candidacy or any
  published reading. Both slices' skills, days and hours agree exactly.

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
- **Where the remaining risk is:** in what could not be re-derived here. That is forecast generation, the gates and
  the leak check, the choice of P4's days, and the 2023 rule selection. These rest on the run's own checks and the
  earlier reviews.

## 8. Limits of this replication

- **The blinding was procedural.** The analyst worked in the same file system, under instructions to read only its
  packet, and it listed every file it read: the four packet files.
  - It reported one slip: a scratch script written just outside the packet folder, then deleted. That script ran
    only its own functions on synthetic data.
  - Nothing indicates it saw a published value. Its outputs are committed before and apart from the comparison.
- **Independence is partial in two places:**
  - M rests on a formula supplied as a written statement of the code's formula;
  - P4's day list was supplied from the run.
- **The packet's description of `bootstrap_skill` omitted the short-series block reduction.** That omission is the
  sole cause of the four class (b) discrepancies, which lie in report-only slices.

## Files

All under `docs/experiment_4/replication/`; none existed before this replication.

| Path | Contents |
|---|---|
| `TOLERANCES.md` | the comparison rules, committed before any comparison |
| `provenance.py`, `provenance.json` | authentication and the internal-consistency checks |
| `blind/` | the packet the analyst received (`README_PACKET.md`, `spec_excerpt.json`, `p4_kept_days.json`), its code (`blind_replicate.py`) and its outputs (`blind_outputs.json`). `forecasts.csv.gz` is on the evidence branch |
| `compare_blind.py`, `compare_blind.json` | the field-by-field comparison |
| `reexecute_frozen.py`, `reexecute_frozen.json` | Track 2, the frozen code re-executed (not independent) |
| `mc_tolerance.py`, `mc_tolerance.json` | Track 3, the seed spread (report-only) |

**To rerun:**
1. Fetch `evidence/exp4-run-36823477529`.
2. Unzip `prices-run-36823477529.zip`.
3. Copy `forecasts.csv.gz` into `blind/`.
4. Run each script as its docstring says, with numpy 2.4.6 and pandas 2.3.3.
