# Human1: results and dispatch log

*Owner instruction: [`NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md`](NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md). Frozen spec:
[`HUMAN1_SPEC.md`](HUMAN1_SPEC.md). Every dispatch of `.github/workflows/research-loop-human1.yml` is listed here. The
published records are on branches `human1/run-<id>` (manifest-checked). Phase 0, beta1, learn1, policy1 and discovery1
results are unchanged.*

**Reading: SCRIPTABLE NARROW KERNEL** (frozen programme reading, row 4).
- **w1 (E + D) was uninformative:** E given D was not detectable on the observed post-change days.
- **w2 (E + noise) and w3 (E + R) were informative.** In both, researcher L2 reached a correct, evidence-supported
  conclusion, and so did the fixed four-experiment script. Each used 4 experiments per world, 8 in all.
- **Competence (question A):** shown on the two informative worlds.
- **Residual agentic value (question B):** not shown. In two of the three worlds L2 ran exactly the script's four tests,
  in a different order; in the third it changed one test. It reached the same adjudications with the same budget.

E is in every packet by construction, a benchmark condition, not a discovery claim. Three worlds with one trajectory
each are not a rate estimate.

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37283756090](https://github.com/xuanhuyle/solar/actions/runs/37283756090) | preflight | `037b7b4` | **PASS**: 3 of 3 L2 calls valid, 0 refusals, 0 repairs, 4 legal experiments over X01–X02, every prompt rebuilt, comparator followed its protocol |
| 2 | [37284111531](https://github.com/xuanhuyle/solar/actions/runs/37284111531) | run (scored, three worlds) | `037b7b4` | **SCRIPTABLE NARROW KERNEL** (integrity clean) |

**Sequence:**
1. **Freeze** (`c4e207a`).
2. **Merge of the owner's commit `6347fdc`** (research documents and a Human1 scaffold). Its four scaffold files were
   kept as the owner wrote them; the `Lab2` code was identical and only docstrings differed (`d1e64b1`).
3. **Rename** of the world function, so the frozen Discovery1 guard test still passes (`037b7b4`). The hash was re-pinned
   each time: `human1_spec_sha` `5a3f984e…`. No world existed before this hash.
4. **One focused check** (a single agent). It found nothing invalidating in the owner's five items:
   - truth separation;
   - pair construction;
   - prompt reconstruction: the system text equals learn1's L text except for the five mechanical edits;
   - adjudication determinism: an independent implementation of section 6 agreed on 200,000 random trajectories, with
     no crash on 300,000 more; the programme table and closing lines agreed on 64,000 combinations;
   - comparator budget matching.

   It noted one point that does not invalidate the run: each research job downloads the whole observed artifact, so
   the other worlds' target and pair series are also on disk. They carry no role information, the code reads only its
   own world, and Discovery1 did the same.
5. **Preflight**, then **the one scored run**.

The full test suite passed at the frozen commit (808 tests). The preflight was operational only. It was not read for
science, and nothing was tuned on it.

## 1. The frozen question

> If a human supplies a small, genuinely relevant hypothesis set, the existing researcher can turn it into a
> scientifically supported conclusion under a tight experimental budget, rather than merely choosing a good forecast set
> or relying on an obvious deterministic test script.

- **A. Competence:** does it reach a correct, evidence-supported conclusion?
- **B. Residual agentic value:** does adaptive planning add anything beyond a fixed protocol?

## 2. Integrity (scored run 37284111531)

All three worlds were clean:
- **Data:** the observed-data hash regenerated equal to the shipped and declared hashes.
- **L2's prompts:** the system text equalled the frozen L2 text, and every prompt rebuilt byte for byte from its own
  world's record.
- **Recomputation:** all 4 of L2's experiments per world recomputed equal; so did the comparator's 4 experiments,
  statuses and selection.
- **Checks:** no canary in any record; the model hash matched; the guard confirmed the truth absent; every job
  succeeded.
- **API:** 0 refusals, 0 repairs, every call valid.

The frozen lesson was unchanged (sha256 `1c38b101…`).

## 3. The worlds and informativeness (revealed after the run)

| world | pair (ids) | first changed day | E alone, days 99–112 | E alone, days 99–126 | contrast checks (required) | informative |
|---|---|---|---|---|---|---|
| w1 | E + D (E = X01, D = X02) | 90 | +20.4% [+7.0, +31.7] | +23.3% [+12.7, +33.6] | E given D +5.0% [−3.0, +13.6] (needed > 0); D given E −13.5% [−24.8, −2.4] | **no**: E and D not distinguishable on the observed data |
| w2 | E + noise (E = X01, N = X02) | 90 | +23.2% [−6.3, +38.2] | +27.0% [+9.4, +35.6] | N alone −14.7% [−36.0, +2.7] and −8.5% [−20.1, +2.3]; N given E +6.8% [−8.3, +22.6] and −2.9% [−12.7, +8.3] | yes |
| w3 | E + R (E = X02, R = X01) | 92 | +29.5% [+11.5, +43.9] | +27.5% [+16.5, +37.6] | R alone −1.6% [−13.2, +7.2] and −1.0% [−8.5, +5.2]; R given E −0.1% [−2.5, +4.3] and +1.0% [−4.3, +6.5] | yes |

**Descriptive (not required):**
- w1: D alone was +5.8% [−9.4, +17.5] on days 99–112 and +8.3% [−4.8, +21.9] on days 99–126.
- w2: E given N was +30.7% [+14.5, +39.4].
- w3: R alone was +23.2% [+6.2, +39.2] before the change (days 57–84) and +15.5% [−1.2, +28.1] on days 85–112. E given R
  was +28.9% [+17.2, +40.7].

As the spec warned, the E + D world was the one at risk. With 2 informative worlds, BENCHMARK FAILURE does not apply.

## 4. Per world: every experiment, the conclusions, and their support

"Usable" means fresh (scored entirely after the change) and at least 14 days. The 28-day window at day 112 (days 85–112)
always contains pre-change days, so it supports no claim.

### w2: E + noise (informative). L2 and the comparator both succeed.

**L2's experiments, in order:**

| id | round | covariates | reference | window | scored days | skill [95% interval] | usable |
|---|---|---|---|---|---|---|---|
| E1 | 1 | X01 (E) | none | 28 | 85–112 | +11.8% [−4.0, +26.9] | no (mixed) |
| E2 | 1 | X02 (N) | none | 28 | 85–112 | −7.8% [−20.9, +3.7] | no (mixed) |
| E3 | 2 | X01 (E) | none | 28 | 99–126 | +27.0% [+9.4, +35.6] | yes |
| E4 | 2 | X02 (N) | X01 (E) | 28 | 99–126 | −2.9% [−12.7, +8.3] | yes |

**L2's final conclusion (verbatim):**
- X01: accepted; cites E1, E3: "E3 skill is +27.0% with a 95% interval of +9.4 to +35.6 that excludes zero, and 20/8
  days won. Both new weeks (113-126) are strongly positive (+28.7%, +32.1%). The E1 last-week drop did not persist."
- X02: rejected; cites E2, E4: "Re-screened on the newest data given X01 (E4): -2.9%, 9/19 days, last two weeks
  negative. Alone on days 85-112 (E2) it scored -7.8%. No sign of an emerging signal. X02 alone was never tested on days
  113-126, so this rejection is dated to the data observed so far."
- Selection: [X01].
- Conclusion: "Select X01 only. Supported: X01 currently improves day-ahead forecasts. E3 measured +27% skill over no
  covariates on days 99-126, with an interval excluding zero and both newest weeks positive. The apparent decay in E1's
  last week was a single bad week that reversed. Also supported: X02 adds no value given X01 on the most recent data
  (E4: -2.9%, 9/19 days, last two weeks negative), and alone it did not help on days 85-112 (E2). Uncertain: X01's
  effect varies from week to week (one week at -17.6%), so its future size is uncertain if the process shifts again.
  E4's interval (-12.7% to +8.3%) cannot exclude a small X02 benefit. X02 alone was not re-tested after day 112, so its
  rejection rests on its redundancy given X01 and should be revisited if behaviour changes again."

**Support:**
- E accepted: supported by E3, a usable positive test of E alone.
- N rejected: supported by E4, a usable null conditional, with no positive evidence for N.
- The selection is supported; nothing is incoherent.
- Unsupported acceptances 0; unsupported rejection or zero-effect claims 0.
- All five criteria met: **success**.

**The prose and the table agree.** The prose hedges its "adds no value" statement with the interval itself.

**Comparator:**
- C1: X01 vs none, days 85–112: +11.8% [−4.0, +26.9].
- C2: X02 vs none, days 85–112: −7.8% [−20.9, +3.7].
- C3: X01 given X02, days 99–126: +30.7% [+14.5, +39.4].
- C4: X02 given X01, days 99–126: −2.9% [−12.7, +8.3].
- Conclusion: X01 accepted, X02 redundant, selection [X01]. All claims supported: **success**.

### w3: E + R (informative). L2 and the comparator both succeed.

**L2's experiments, in order:**

| id | round | covariates | reference | window | scored days | skill [95% interval] | usable |
|---|---|---|---|---|---|---|---|
| E1 | 1 | X01 (R) | none | 28 | 85–112 | +15.5% [−1.2, +28.1] | no (mixed) |
| E2 | 1 | X02 (E) | none | 28 | 85–112 | +17.3% [−1.4, +32.9] | no (mixed) |
| E3 | 2 | X02 (E) | X01 (R) | 28 | 99–126 | +28.9% [+17.2, +40.7] | yes |
| E4 | 2 | X01 (R) | X02 (E) | 28 | 99–126 | +1.0% [−4.3, +6.5] | yes |

After round 1, L2 marked R "deteriorated", reading its weekly parts (+46.6, +4.5, −13.0, +11.4) as decay, and E
"promising".

**L2's final conclusion (verbatim):**
- X01: redundant; cites E1, E4: "E1 showed strong early skill that faded after days 85-91. E4 shows no added value given
  X02 on days 99-126: +1.0%, interval includes zero, lost 16 of 28 days. Any information it carries seems to be covered
  by X02. This judgement holds for the current regime only and is provisional."
- X02: accepted; cites E2, E3: "E2 showed emerging marginal skill. E3 shows X02 adds +28.9% over X01 on days 99-126,
  with an interval excluding zero and positive skill in every week. Its single-covariate MAE (0.859) is far below X01's
  (1.197) over the same days."
- Selection: [X02].
- Conclusion: "Use X02 alone. Supported: in the most recent 28 days (99-126), X02 adds substantial, statistically clear
  skill on top of X01 (E3: +28.9%, CI +17.2 to +40.7, positive every week). X01 adds nothing detectable given X02 (E4:
  +1.0%, CI -4.3 to +6.5, 12/16 days). The data are consistent with a regime change around day 91: X01's usefulness
  decayed (E1) while X02's emerged (E2). Uncertain: (1) X02's skill against a no-covariate reference was not re-measured
  on days 113-126. Its benefit there is inferred from E3 and its lower single-covariate error, not tested directly. (2)
  Weekly skill in E3 fluctuates (+9.9 to +44.9), so the size of the gain is uncertain. (3) The process is non-stationary.
  X01's redundancy holds for the current regime only; it could become useful again, or X02 could decay, after a further
  shift. (4) The E4 interval allows a small benefit from X01, but adding it is not justified by the evidence."

**Support:**
- E accepted: supported by E3, a usable positive conditional (E given R).
- R redundant: supported by E4, a usable null conditional.
- R was neither accepted nor selected, so its old usefulness was not taken as current.
- The selection is supported. Unsupported acceptances 0; unsupported rejections 0.
- All five criteria met: **success**.

**The prose and the table agree.** The prose correctly marks E's standalone benefit after day 112 as inferred, not
tested.

**Comparator:**
- C1: X01 vs none, days 85–112: +15.5% [−1.2, +28.1].
- C2: X02 vs none, days 85–112: +17.3% [−1.4, +32.9].
- C3: X01 given X02, days 99–126: +1.0% [−4.3, +6.5].
- C4: X02 given X01, days 99–126: +28.9% [+17.2, +40.7].
- Conclusion: X02 accepted, X01 redundant, selection [X02]. **Success.**

### w1: E + D (uninformative; no success or failure counted)

**L2's experiments, in order** (the same four tests as the comparator):

| id | round | covariates | reference | window | scored days | skill [95% interval] | usable |
|---|---|---|---|---|---|---|---|
| E1 | 1 | X01 (E) | none | 28 | 85–112 | +16.3% [+3.1, +26.5] | no (mixed) |
| E2 | 1 | X02 (D) | none | 28 | 85–112 | +7.5% [−10.6, +20.3] | no (mixed) |
| E3 | 2 | X02 (D) | X01 (E) | 28 | 99–126 | −13.5% [−24.8, −2.4] | yes |
| E4 | 2 | X01 (E) | X02 (D) | 28 | 99–126 | +5.0% [−3.0, +13.6] | yes |

**L2's final conclusion (verbatim):**
- X01: accepted; cites E1, E3, E4: "Marginal skill +16.3% with a CI excluding zero on days 85-112 (E1). On days 99-126
  X01 alone had the lowest MAE tested (0.839), below X02 alone (1.002) and both together (0.952). Its incremental value
  over X02 alone is +5% but the CI spans zero (E4). Its marginal value against no covariates on days 113-126 was not
  tested directly."
- X02: rejected; cites E2, E3: "Given X01, adding X02 worsened forecasts on days 99-126 (-13.5%, CI excluding zero,
  negative in every week including the newest). Its marginal value was unresolved on days 85-112 (E2). This rejection
  rests on current-regime data but is dated: it holds to day 126 and could change if the system shifts again."
- Selection: [X01].
- Conclusion: "Select X01 only. Supported: X01 improved on no covariates through day 112 (E1, +16.3%, CI excluding zero).
  Supported: on days 99-126, adding X02 to X01 made forecasts significantly worse (E3, -13.5%, CI -24.8 to -2.4),
  consistently in every week. That window includes the post-day-112 data, so the finding against X02 comes from the
  current regime, not an outdated one. Among the configurations tested on days 99-126, X01 alone had the lowest error.
  Uncertain: whether X01 still beats no covariates after day 112, since that was never tested directly. Uncertain:
  X01's increment over X02 alone (E4, +5%, CI spans zero), though its newest week was strongly positive (+15.8%).
  Uncertain: X02's standalone value against no covariates after day 112, which was also never tested. Given possible
  non-stationarity, the X02 rejection is dated to day 126, and performance of the X01 model should be monitored."

**What the rules would have said** (descriptive only; this world is not scored):
- L2 accepted E on E1, whose window contains pre-change days. It had no usable positive evidence for E, so the acceptance
  would have been unsupported. Its own prose names exactly this gap ("whether X01 still beats no covariates after day 112
  … was never tested directly").
- D rejected is supported by E3.

**Comparator:** the same four results. Conclusion: E promising, D rejected, empty selection.

### Summary of the criteria

| world | pair | informative | L2: 1 2 3 4 5 | L2 | comparator: 1 2 3 4 5 | comparator | experiments, L2 / comparator |
|---|---|---|---|---|---|---|---|
| w1 | E + D | no | n Y n Y n | not counted | n Y n Y Y | not counted | 4 / 4 |
| w2 | E + noise | yes | Y Y Y Y Y | **success** | Y Y Y Y Y | **success** | 4 / 4 |
| w3 | E + R | yes | Y Y Y Y Y | **success** | Y Y Y Y Y | **success** | 4 / 4 |

**Criteria:**
1. informative;
2. complete;
3. E accepted, supported and selected;
4. distractor treated correctly;
5. no unsupported claim.

**Totals:** unsupported acceptances, L2 0 and comparator 0 in the informative worlds (L2 1 in uninformative w1).
Unsupported rejection or zero-effect claims: 0 everywhere.

## 5. Did adaptive planning add anything beyond the script? (question B)

| world | L2's four tests compared with the script's | same adjudication as the script? |
|---|---|---|
| w1 | identical set (each candidate alone on days 85–112, then each given the other on days 99–126); only the order of the conditionals differed | not scored |
| w2 | three of four identical; in round 2 L2 re-tested E alone on days 99–126 where the script tested E given N | yes: E accepted, N not accepted (L2 "rejected", script "redundant") |
| w3 | identical set; order differed | yes: E accepted, R redundant |

**Measured outcome:**
- The script succeeded in every informative world, and L2 used 8 experiments over them, the same as the script.
- L2 never stopped early, even though unused budget was allowed.
- So there was neither a failure of the script that L2 avoided nor an efficiency advantage.

The disclosed design property still holds: the script's day-126 conditionals are the contrasts the informativeness check
runs.

## 6. Confirmation (days 127–154; reported separately, never a rescue)

| comparison | w1 t0-beta | w2 t0-beta | w3 t0-beta |
|---|---|---|---|
| {E} vs {} | +34.7% [+24.4, +44.0] | +43.2% [+32.8, +52.4] | +40.2% [+20.8, +52.2] |
| {Z} vs {} | D: +24.9% [+12.8, +36.1] | N: −1.9% [−10.7, +6.5] | R: +0.7% [−14.6, +16.2] |
| {E, Z} vs {} | +28.2% [+16.0, +38.9] | +44.1% [+33.9, +52.9] | +38.1% [+18.7, +50.4] |
| Z given E | −10.0% [−22.0, −0.8] | +1.5% [−4.6, +7.2] | −3.7% [−8.7, +0.7] |
| E given Z | +4.4% [−3.0, +12.6] | +45.1% [+33.7, +54.8] | +37.6% [+19.3, +49.0] |
| L2's selection vs {} | {E} +34.7% | {E} +43.2% | {E} +40.2% |
| comparator's selection vs {} | empty | {E} +43.2% | {E} +40.2% |

The ridge rows (in `REPORT.md` on the run branch) are context only.

## 7. Cost

| | L2 tokens | API attempts (refusals, repairs) | L2 loop wall time | t0-beta forecasts |
|---|---|---|---|---|
| preflight (1 world) | 14,549 | 3 (0, 0) | 50.2 s (comparator 8.6 s) | 266 (L2 126, comparator 140) |
| w1 | 14,846 | 3 (0, 0) | 48.2 s (comparator 8.0 s) | 644 (L2 140, comparator 140, evaluate 364) |
| w2 | 14,536 | 3 (0, 0) | 43.1 s (comparator 8.4 s) | 658 (140, 140, 378) |
| w3 | 14,996 | 3 (0, 0) | 43.1 s (comparator 10.3 s) | 728 (140, 140, 448) |
| **total** | **58,927** | **12 (0, 0)** | | **2,296** |

- **Scored-run tokens:** input 7,595; output 8,433; cache reads 28,350.
- **Experiments:** 4 per world for each searcher.
- **Runner time:** about 2.6 minutes for the preflight and 7.9 for the scored run. The three world jobs ran in parallel
  at about 1.8 minutes each; evaluate took 2.0 minutes. Wall time was about 7 minutes in all.

## 8. Reading

| # | Row | Holds? |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | no: integrity clean, every call valid |
| 2 | BENCHMARK FAILURE | no: 2 informative worlds (w2, w3) |
| 3 | NARROW RESEARCHER FAILURE | no: L2 failed in none |
| 4 | **SCRIPTABLE NARROW KERNEL** | **yes**: L2 and the comparator both succeeded in both informative worlds, with 8 experiments each (no efficiency advantage) |

Predeclared closing line: **USE A SCRIPT / HUMAN-DRIVEN WORKFLOW**. The owner's kill logic is explicit that this is not
evidence for autonomous research. At most, the forecasting and testing substrate may be useful; this benchmark does not
show that an LLM research planner is necessary.
