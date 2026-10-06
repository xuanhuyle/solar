# Phase 0: falsification spike, frozen specification

*Frozen before any t0 run of Phase 0 and before the hidden world exists. The freeze is the commit from which the
Phase A run is dispatched; that run records the commit and `spec_sha`. The rule files are this document and
`research_loop_proof/phase0/{truth/world.json, truth/generator.py, truth/calibrate.py, truth/phase_a.py,
lab/instruments.py, lab/menu.json, lab/brief.md}`. Their combined hash is `spec_sha` (`truth/spec.py`), and a
test pins each file's sha256. Nothing here may change after a result is seen. A software defect is documented in
`PHASE0_RESULTS.md` before any rerun, and every dispatch is listed there. Changes made before the freeze are listed
in section 7.*

## 1. What is being tested

The proposition, which is **not** assumed true:

> A pretrained forecasting model may let an AI researcher test newly relevant information before enough local
> post-change evidence exists to train and redesign a bespoke forecasting workflow from scratch.

Two indispensable assumptions are tested, in order. A failure is a result.

- **A. Instrument:** can t0-alpha use a covariate that has only just become predictive, with little post-change
  history? No AI call is made unless A passes.
- **B. Researcher:** with four anonymous candidates and at most six t0 experiments, can the AI researcher find the
  new covariate and update its beliefs, without seeing the truth?

Not in scope: the 10-scenario sandbox (`DESIGN.md`), Experiment 4, B1, the vault, the engine ledger, any 2026+
data, any engine code.

## 2. The world (`truth/world.json`, `truth/generator.py`)

**Target**, hourly:
`y = sin(2π(h−6)/24) + daily AR(1) shock (φ 0.6, variance 0.5) + hourly AR(1) noise (φ 0.7, variance 0.5) + effects`.
- The noise variance totals 1.
- There is no weekly profile: t0 receives no timestamps, and a 7-day context could not learn one.

**Candidates**, each built the same way:
- a daily AR(1) level (φ 0.5, variance 0.7), repeated over the 24 hours;
- plus an hourly AR(1) (φ 0.9, variance 0.3);
- no fixed daily shape, so the target's daily profile cannot reveal a change;
- standardised on pre-change days only;
- **observed with a random sign:** each candidate is shown multiplied by its own s = +1 or −1. The target is built
  from the unsigned series, so the sign of every relationship is unknown in advance. A model with a fixed-sign
  response to a covariate therefore gains nothing on average. In Phase A, E's sign is balanced by design (+1 in
  even-numbered worlds, −1 in odd ones); in Phase B all four signs are drawn from the seed.

**Roles.**

| Role | Before the change | From the change on |
|---|---|---|
| R | `c·x_R` (drives the target) | nothing (retired) |
| E | nothing | `c·f(x_E)` (emerging) |
| D | built from `0.8·E + 0.6·(an independent candidate)` before standardisation (correlation with E about 0.8) | the same; never causal, but predictive after the change because it is correlated with E |
| N | independent noise | independent noise |

Here x denotes the unsigned standardised series; the candidate as observed is s·x.

- **Emerging relationship.** `f` is linear (`f(x) = x`) or a hinge: `max(0, x − q₀.₇)`, centred and scaled with
  closed-form standard-normal moments.
- **Choice of forms.** Both forms were fixed before any t0 run. Neither was chosen because t0 does well on it. The
  hinge is the form the gating criterion does not use.
- **What the target's own history shows.** E's post-change relationship does not exist in the pre-change target
  history. Total effect variance is the same before and after the change, so the target's variance does not reveal
  it either.
- **The change** happens at 00:00 of day τ.

**Strength.**
- `c² = 0.75·m`.
- **Calibration** (`truth/calibrate.py`) uses ridge only, never t0:
  - On 3 fixed worlds (linear, τ = 60), measure the median over worlds of the pooled skill of ridge{E} against
    ridge{} on days 60+7 to 60+20, with a 7-day context.
  - m = 1 if the median is in [0.20, 0.40]. Otherwise take one step (m = 2 if below, 0.5 if above) and use the stepped
    value whatever it measures.
- **Record** (local, before this freeze):
  - m = 1: per-world skill 0.387, −0.033, 0.152; median 0.152, below 0.20, so step to m = 2.
  - m = 2: per-world skill 0.499, 0.045, 0.369; median 0.369.
  - **m = 2 is used.** The Phase A job re-runs the calibration and must reproduce these medians.

**How this may resemble t0's pretraining.** t0 was partly pretrained on synthetic covariate-effect data, and this is
a simple additive synthetic effect. So a Phase A pass shows only that t0 can use such an effect here. It does not
show adaptation in general, or on real data.

**Planning simulation (disclosed).** The design review ran a ridge-only simulation in memory, on non-scored worlds
with no t0. It found two things:
- a 28-day context mainly measures how many pre-change days remain in the window, which is dilution;
- a decoy correlated only at the daily level is invisible to the test.

That is why the primary context is 7 days and why D is correlated with E hour by hour. No scored seed existed then.

## 3. Phase A: the instrument

**Worlds** (seeds `int(sha256('phase0-A-<form>-<i>')[:16], 16)`; τ = 60; 102 days each):

| Set | Context L | Days after the change k | Arms (each for t0 and for ridge) |
|---|---|---|---|
| 40 linear worlds | 7 days (primary) | 0–20 | without covariates; with {E}; with {N} (placebo) |
| Linear worlds 0–7 | 28 days (secondary) | 0–41 | without covariates; with {E} |
| 12 hinge worlds | 7 days | 0–20 | without covariates; with {E} |

**Why a placebo arm.** {N} carries one covariate row, as {E} does, but no information about the target. Comparing
{E} with {N} removes any change that the mere presence of a covariate row causes. The pre-freeze dry run with a tiny
*untrained* t0 (`--fake-model`; its skill numbers mean nothing and are not results) showed such a change: {E} and
{N} each beat "without" by about 7%, at k = 0 as well.

**Forecasts and the comparator.**
- Day 60+k is forecast at the end of day 59+k, so the context holds min(k, L) post-change days.
- **Ridge** (`lab/instruments.py`) is fitted on the same L days only:
  - 24 hour dummies (unpenalised);
  - the target 24 and 48 hours earlier, using only rows whose lags fall inside the window;
  - the covariate x (plus x² at L = 28);
  - the penalty chosen by generalised cross-validation over 13 values from 10⁻³ to 10³.
- **Why ridge is the comparator:** it is cheap, it is what a practitioner would fit first, and it has exactly the same
  information as t0.

**Bins, chosen before any result.**
- L = 7: k = 0 | 1–3 | 4–6 | 7–13 | 14–20.
- L = 28: k = 0 | 1–3 | 4–6 | 7–13 | 14–27 | 28–41.
- Why these bins:
  - k = 0 is a control: no post-change data in the context, so no gain is expected.
  - 1–3 and 4–6 are "very little" evidence.
  - At L = 7, 7–20 is a fully post-change context.
  - At L = 28, the context is fully post-change only from k = 28.

**Statistic.**
- Skill of arm A against arm B = 1 − (sum of absolute errors of A) / (sum of B), pooled over worlds and days in the
  bin. Reported comparisons: E against none, E against N, and N against none (where the arms exist).
- The 95% interval comes from a bootstrap over worlds: 2,000 resamples, seed 0.
- **"How soon"** = the earliest bin (k = 0 excluded) from which every later bin has a lower bound above 0.

**Competence criterion (frozen).** On the linear worlds with L = 7, PASS needs all three, and each must hold **both**
for t0 {E} against t0 without covariates **and** for t0 {E} against t0 {N}:
- **C1:** skill over k = 7–20 is at least 5%, with a lower bound above 0. *Can t0 use E at all?*
- **C2:** skill over k = 1–6, pooled, has a lower bound above 0. *With very little post-change evidence?*
- **C3:** in at least 20 of 40 worlds, the 14-day window k = 7–20 alone gives `metrics.pair_skill` a lower bound above
  0 (2-day blocks, seed 0). *Can one research-sized experiment show it?* (In Phase B an experiment against an empty
  reference is exactly the "against none" comparison.)
  - **Why 2-day blocks.** With 7-day blocks, a 14-day window has only 2 blocks drawn from 8 overlapping starts, and
    the interval is far too narrow. A pre-freeze measurement (ridge only, non-scored seeds) compared ridge{R} with
    ridge{N} after the change, where neither has an effect. The share of worlds with a lower bound above 0 was
    16.8% with 7-day blocks and 4.2% with 2-day blocks (nominal 2.5%), so 2-day blocks remain slightly generous.
    The full table is in section 7.
- Every threshold is tested on unrounded values.

The same criteria are computed for ridge and reported. Ridge does not affect the verdict.

**Integrity.** Any failure here means *no verdict*: it is documented as a defect, followed by a disclosed rerun.
- the calibration reproduces;
- t0 sanitises no output (a non-finite output replaced silently);
- the poison check: target values after the forecast origin, and E after the forecast day, set to NaN leave
  single-row forecasts bit-identical (worlds 0, k = 3, 10, 17).
- The k = 0 control is reported for each comparison. A lower bound above 0 there is flagged for examination, but it
  does not decide the verdict.

**Timing.** The smoke run measures seconds per t0 forecast-day. It changes nothing: the L = 28 secondary uses 8
worlds, fixed.

**Stop rule.** If C1, C2 or C3 fails, the outcome is **INSTRUMENT FEASIBILITY FAILED**:
- Phase 0 ends;
- no AI researcher call;
- no strengthening of the signal;
- no redesign.

**Reported, not gating:**
- the L = 28 and hinge curves (E against none only: they have no placebo arm, so the primary set's N-against-none
  curve shows how much of such a gain could be generic);
- the ridge curves;
- the mean absolute errors of every arm;
- "how soon" for t0 and for ridge.

## 4. Phase B: one hidden world (only if Phase A passed)

**The world.**
- Seed = `int(sha256('<spec_sha>:<phaseB run id>')[:16], 16)`. The run id exists only when the run is dispatched, so
  nobody can preview the world.
- Linear form, m = 2, 154 days, τ = 86 + U{0..6}.
- Candidate ids X01–X04 are a seeded permutation of R, E, D and N.

**Timeline.**

| Days | Content | Seen by research? |
|---|---|---|
| 1–84 | before the change | yes, from round 1 |
| 85–112 | the change falls in days 86–92 | yes, from round 2 |
| 113–126 | after the change | yes, from round 3 |
| 127–154 | confirmation, all after the change | **never**: exists only in the evaluate job |

- Each round sees the data truncated at its cutoff day: 84, 112, 126.

**Menu (`lab/menu.json`).**
- The context is 7 days throughout.
- An experiment names 1–4 covariate ids and a reference of 0–2 ids, disjoint from the covariates. The candidate arm
  uses covariates plus reference; the reference arm uses the reference only. So the experiment measures what the
  covariates add to the reference.
- The window is the last 7, 14 or 28 revealed days. Re-tests are allowed.
- **Budget:** 6 experiments, at most 3 per round.
- **A result gives:**
  - experiment id and scored day range;
  - reference MAE and candidate MAE;
  - skill with a 95% moving-block interval, with blocks of min(2, window_days // 7) days, so 1, 2 or 2 days for
    windows of 7, 14 or 28 days. The 14-day block is the same as C3's. Indicative below 14 days;
  - days won, lost and tied;
  - skill per 7-day sub-block.

  No raw values.

**The researcher.**
- **Calls:** 4 (rounds 1–3, then a final call with no experiments). The brief is `lab/brief.md`, verbatim.
- **Each call** is one fresh request containing the brief, the schema, the revealed range, the remaining budget and
  the notebook as text: every earlier request, result, belief table and note.
- **Schema:**
  - notes;
  - one belief row per candidate: status ∈ {untested, promising, accepted, rejected, deteriorated, redundant},
    cites, reason;
  - experiments, each with covariates, reference, window_days, expect ∈ {improves, no_change, worsens}, and because;
  - final_selection;
  - conclusion.
- **Checks in code:** counts, ids and lengths are checked in code, with one repair turn per call. An invalid round
  runs no experiment and is recorded.
- **The model is frozen by hash.** `lab/menu.json` holds the sha256 of the model id, which is the id requested and
  served at engine-ledger seqs 74 and 76. The identifier itself is not written in the repository.
  - The research job refuses to start unless sha256 of `vars.RESEARCHER_MODEL` equals it.
  - Every response's served model must hash to it; otherwise the run is an integrity failure (verdict row 0).
  - The effort is the literal `high` from `menu.json`; no variable or default overrides it.
- **Limits:** a hard cap of 80k tokens, enforced in code.
- **Notebook:** every prompt, response, request, result, belief table, usage and timestamp is stored as JSONL.

**Mechanical separation.**
- The research job's checkout has no `research_loop_proof/phase0/truth/`, and a guard step fails if the directory
  exists. It downloads only the observed data: days 1–126, ids X01–X04, the target, hashed over the raw array bytes.
- The truth (roles, τ, forms, the confirmation days) is never uploaded. Only the evaluate job regenerates it from
  the seed.
- The evaluator rebuilds every prompt from the observed data and the recorded responses, and scans them for the
  world's canary string.
- HF_TOKEN is used only to download the verified weights. The API-calling step loads them offline.

**Frozen scripted strategy (the same budget; descriptive only):**
- Round 1: X01, then X02, each against none, on the last 28 days.
- Round 2: X03, then X04, each against none, on the last 14 days.
- Round 3: X01, then X02, each against none, on the last 14 days.
- Final selection: every candidate whose latest single-candidate result has a lower bound above 0.

**Evaluate job.**
- **Confirmation** (days 127–154, L = 7): t0 and ridge on
  - the sets {}, {E}, {R}, {D}, {N} and {E, D};
  - the AI's final set and the script's final set;
  - D given E ({E, D} against {E}) and E given D ({E, D} against {D}).
- **Evidence check:** t0 {R} against {} on days 57–84, and t0 {E} against {} on days 99–126 (`pair_skill`, 2-day
  blocks, as for any 28-day window). This separates "missed by the researcher" from "not there to find".
- Every `pair_skill` interval in Phase B, including the confirmation comparisons, uses the block rule of the menu.
- **Reported for each candidate:** its causal role, its predictive usefulness on the confirmation days, and the
  researcher's selection. A correlated proxy that forecasts well is reported as such, not as a failure by itself.

**Behaviours, computed from the notebook.** "Latest result for c" means the latest experiment whose covariates are
exactly [c], with any reference.
- **B1 Initial hypothesis:** round 1 has an experiment with expect and because filled.
- **B2 Test:** at least one valid experiment ran.
- **B3 Correct interpretation:** no belief table marks a candidate accepted when its latest result's lower bound is
  ≤ 0, or rejected when it is above 0. Each such (call, candidate) pair is one interpretation error.
- **B4 Negative result preserved:** some result with lower bound ≤ 0 is cited in a later call, and that candidate is
  not later accepted without a newer result above 0.
- **B5 Weakening noticed:** R is promising or accepted at some call, and later deteriorated or rejected, citing an
  experiment whose scored days include days from τ on.
- **B6 Another candidate investigated:** after a negative or weakened result, a later round tests a candidate not yet
  tested, or re-tests a rejected one.
- **B7 New covariate identified:** E is accepted in the final call and is in final_selection.
- **B8 Beliefs revised:** some candidate's status changes between two tested statuses, citing an experiment newer
  than the earlier call.

**Verdict map** (the first match wins):

| # | Outcome | Condition |
|---|---|---|
| 0 | Integrity failure (no verdict) | observed-hash mismatch, a prompt-rebuild mismatch, a canary found, the guard tripped, a researcher-model hash mismatch, a crash, or an API outage. Documented as a defect; disclosed rerun |
| 1 | INSTRUMENT FEASIBILITY FAILED | Phase A verdict |
| 2 | RESEARCHER FEASIBILITY FAILED | any of: no valid final conclusion; R in the final selection; N in the final selection with its latest lower bound ≤ 0 or never tested; 2 or more interpretation errors; the evidence check shows E detectable (lower bound above 0 on days 99–126), yet E was never in an experiment's covariates in rounds 2–3 and is not selected |
| 3 | BASIC LOOP FEASIBLE | E selected; R and N not selected; B3, B5, B7 and B8 hold; and t0 with the final selection beats t0 without covariates on the confirmation days (`pair_skill` lower bound above 0) |
| 4 | AMBIGUOUS | anything else, including D selected without E when the confirmation days do not clearly favour E, or a missing B5 when the evidence check shows R was not detectable before the change |

**Two caveats always reported with the verdict:**
- One world is an existence check, not a rate.
- Even an ideal researcher completes the whole chain only when both R's and E's evidence is present in this world;
  the evidence check reports whether it was.

## 5. Budgets

- **t0 forecast-days:**
  - Phase A: 40×21×3 + 8×42×2 + 12×21×2 = 3,696 scored, plus 134 for timing and the poison check. The smoke run
    makes 129.
  - Phase B: at most about 870 (AI ≤ 336, script ≤ 168, confirmation and evidence checks ≤ 364). A forecast depends
    only on its covariate set and its day, so identical forecasts are computed once.
- **API:** about 15–35k tokens expected; hard cap 80k.
- **Runner time:** about 1–1.5 hours.
- **Engineering:** about 1.5 days (about 0.9 if Phase A fails).

## 6. What Phase 0 can and cannot show

- **A Phase A pass** shows that t0 can use a simple synthetic emerging covariate within the measured number of
  post-change days, compared with a matched ridge.
- **A Phase A fail** shows it cannot, under these conditions.
- **BASIC LOOP FEASIBLE** shows that in one hidden world the AI researcher, using t0, found the new covariate and
  downgraded the old one, for stated reasons that its own results support.
- **None of these** validates the autonomous-researcher thesis, real-data adaptation, or superiority over the script.
  One scenario supports no claim of superiority.

## 7. Pre-freeze revisions (all made before any real t0 run of Phase 0)

1. **Placebo arm {N} added to the primary set; the gate needs both comparisons.** Reason: the dry run with a tiny
   *untrained* t0 showed that a covariate row alone moved its forecasts. Also, the L = 28 secondary was fixed at 8
   worlds (no timing rule), so Phase A stays at 3,696 scored forecast-days.
2. **Random observed sign per candidate; E's sign balanced in Phase A.** Reason: the pre-freeze review showed that
   with every effect positive, an instrument that adds a fixed positive multiple of E, using no post-change evidence,
   passed C1–C3. The sign stream is a 4th spawned seed child, so the series, τ, the ids and the target are unchanged.
   Ridge does not depend on a column's sign, so the recorded calibration reproduces exactly (m = 2).
3. **C3 uses 2-day blocks; Phase B intervals use min(2, window_days // 7)-day blocks.** Reason: the review found that
   7-day blocks on 14 days are far too narrow. Measured null rate of "lower bound above 0" (ridge{R} against ridge{N},
   days 7 to 34 after the change, non-scored seeds `phase0-null-<i>`, 400 worlds; one-sided, nominal 2.5%):

   | window | 1-day | 2-day | 3-day | 4-day | 5-day | 6-day | 7-day |
   |---|---|---|---|---|---|---|---|
   | 7 days | 7.8% / 5.5% | 9.0% / 8.8% | 11.0% / 11.2% | 11.0% / 11.2% | 11.0% / 11.2% | 11.0% / 11.2% | 11.0% / 11.2% |
   | 14 days | 3.0% / 5.8% | 4.2% / 5.2% | 4.5% / 7.0% | 6.5% / 9.2% | 9.8% / 11.5% | 9.2% / 11.5% | 16.8% / 18.2% |
   | 28 days | 2.2% / 2.5% | 2.8% / 2.2% | 3.8% / 3.0% | 4.5% / 4.2% | 5.0% / 5.8% | 5.2% / 5.2% | 6.8% / 8.2% |

   Each cell: share of worlds with the lower bound above 0 / the upper bound below 0 (`metrics.pair_skill` caps the
   block at half the window, so at 7 days every block from 3 days up acts as 3). Rule chosen from this table, on
   null comparisons only, before any t0 run: blocks of min(2, window_days // 7) days, so 1, 2 and 2 days for windows
   of 7, 14 and 28 days. 7-day windows stay "indicative". Script: `truth/null_rates.py`; output:
   `docs/research_loop_proof/phase0_null_rates.json`.

4. **Thresholds are tested on unrounded values.** Before, the gate compared values rounded to 4 decimals.
5. **`truth/phase_a.py` and `lab/instruments.py` added to the frozen files.** The researcher model is pinned by hash
   and the effort fixed (section 4).
