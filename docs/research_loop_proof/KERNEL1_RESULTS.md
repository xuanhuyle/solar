# Kernel1 results: the current researcher kernel, unchanged, on twelve hidden worlds

*Owner instruction: [`NEXT_KERNEL_PROOF_PROMPT.md`](NEXT_KERNEL_PROOF_PROMPT.md). Frozen specification:
[`KERNEL1_SPEC.md`](KERNEL1_SPEC.md) (`kernel1_spec_sha` `816d4d973c61d1ef20d0833f624cd35babd3115647a67652c2bab0dca65f1ca2`,
commit `35d6aa6`). The scored record is the orphan branch `kernel1/run-37298605583` (`evaluation.json`,
`REPORT.md`, every research record, `MANIFEST.sha256`). Every number below comes from that record.*

## Reading: KERNEL NOT PROVEN

Row 4 of the frozen programme reading applies:
- change successes: 0 of 8;
- stable: 1 of 2;
- null: 2 of 2;
- median oracle fraction 0.985 over 9 informative non-null worlds;
- worlds with pure noise selected: 6 (w01, w02, w05, w06, w07, w10);
- false accepts in null worlds: 0.

Integrity was clean. 7 of the 8 change worlds were informative, so row 2 (BENCHMARK FAILURE) does not apply.

**Closing line:** `STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL`

## 1. The frozen question

> Does the current autonomous researcher kernel, unchanged, reliably discover useful predictive information in a
> non-trivial hidden hypothesis space, reject false information, adapt when relationships change, and support its
> conclusions with experiments that survive unseen confirmation?

## 2. The kernel was unchanged

- **The research job is Discovery1's own.** Each of the 12 research jobs ran
  `python -m research_loop_proof.discovery1.lab.run weights` and then `… loop`. Kernel1 has no lab code, and the
  research checkout held no Kernel1 file. Workflow tests prove which commands each job runs.
- **System text:** every one of the 12 records has system text sha256
  `78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d`. That is the frozen L8 text, equal to the value
  in Discovery1's scored run `discovery1/run-37238629496`. Every prompt was rebuilt byte for byte from its record.
- **Lesson:** sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`, unchanged.
- **Hashes:** `kernel1_spec_sha` covers discovery1's whole frozen list (the lab, researcher, run step, learn1's lesson
  and conditions, beta1's brief, researcher and t0-beta, Phase 0's generator, menu and executor). Discovery1's own pin
  tests still pass.
- **Untouched:** the diff of this milestone touches no file under phase0, beta1, learn1, policy1, discovery1, human1,
  `engine/`, `solarbench/`, Experiment 4 or the engine ledger.
- **Settings:** the pinned model and effort, X01–X08, the menu, the 7-day t0-beta context, 3 rounds plus a final call,
  6 experiments with at most 3 per round, one repair turn and the 80k cap. All 12 researchers used all 6 experiments.

## 3. Batch composition

Kinds and seeds were derived from the spec hash and the run id (spec §3), so no world existed before dispatch. There
was one scored dispatch and no reroll.

| world | kind | change day τ | R | E | D | N1–N5 |
|---|---|---|---|---|---|---|
| w01 | change | 86 | X04 | X02 | X05 | X01 X07 X06 X03 X08 |
| w02 | change | 91 | X05 | X04 | X02 | X07 X06 X03 X01 X08 |
| w03 | stable | – | X08 | X04 | X01 | X07 X06 X03 X02 X05 |
| w04 | change | 86 | X03 | X02 | X05 | X04 X08 X01 X06 X07 |
| w05 | change | 90 | X01 | X08 | X02 | X04 X07 X05 X06 X03 |
| w06 | stable | – | X04 | X05 | X08 | X07 X01 X03 X06 X02 |
| w07 | change | 86 | X05 | X03 | X06 | X02 X07 X04 X08 X01 |
| w08 | change | 87 | X05 | X06 | X02 | X03 X08 X07 X01 X04 |
| w09 | null | – | X02 | X01 | X05 | X03 X07 X06 X04 X08 |
| w10 | change | 89 | X07 | X06 | X02 | X01 X03 X04 X08 X05 |
| w11 | change | 90 | X07 | X08 | X03 | X04 X02 X05 X01 X06 |
| w12 | null | – | X07 | X08 | X06 | X05 X02 X03 X04 X01 |

**Every dispatch of the Kernel1 workflow** (the complete list from the Actions API):

| run | mode | commit | result |
|---|---|---|---|
| 37298150843 | preflight | `35d6aa6` | PASS, attempt 1: 4 valid calls, 0 refusals, 0 repairs, 6 legal experiments, frozen system text, every prompt rebuilt, guard confirmed. It was operational only; its roles were not read. |
| 37298605583 | run (scored) | `35d6aa6` | attempt 1, preflight 37298150843 |

**Before the preflight:** the one independent pre-run check confirmed two implementation defects, and both were fixed
and re-pinned (`35d6aa6`):
- a failed branch listing could have let a second scored batch through;
- the canary scan skipped worlds without a final record.

It also flagged the structural reading of null criterion 3. That reading is frozen in the spec (§7) and was kept; it
plays no part in this result (see section 8).

## 4. Integrity

| check | status |
|---|---|
| Material integrity issues | none |
| Generator defects | none |
| Worlds without a valid final response | none |
| Calls without a valid response | none |
| Observed-data hashes (regenerated, shipped, declared) | equal in all 12 worlds |
| Guard | truth absent, first attempt, in all 12 |
| Experiment recompute | all 72 experiments recomputed equal on the observed data |
| Poison tests | all 72 experiments unchanged on the full 154-day data poisoned after their cutoffs (+1e6 and NaN) |
| Canary scan | no canary of any world in any research file |
| Researcher model | the pinned model, requested and served, on every attempt |
| t0-beta weights | verified against their pins at load |
| Per-world artifacts | each research job downloaded only its own world's observed artifact |

## 5. Per-world results

**Columns:**
- "Inf." means informative (spec §5).
- "Oracle fr." is the final set's confirmation skill divided by the oracle set's.
- Confirmation is t0-beta, days 127–154, final set vs no covariate (95% interval).

| world | kind | inf. | final selection (roles) | supported | confirmation | oracle (skill) | oracle fr. | result |
|---|---|---|---|---|---|---|---|---|
| w01 | change | yes | X01, X02 (N1, E) | no | +30.8% [+16.5, +43.0] | {E, D} (+31.3%) | 0.985 | fail: noise; unsupported |
| w02 | change | yes | X03, X04 (N3, E) | no | +27.9% [+17.8, +36.7] | {E} (+28.1%) | 0.994 | fail: noise; unsupported |
| w03 | stable | yes | X08 (R) | yes, elimination E4 → E6 | +32.5% [+21.3, +41.3] | {R} (+32.5%) | 1.000 | **success** |
| w04 | change | **no** | none | – | not scored | {E} (+42.3%) | 0 | fail: not informative (and empty, unsupported) |
| w05 | change | yes | X01, X02, X05, X06, X07, X08 (R, D, N3, N4, N2, E) | no | not scored (more than 4) | {E} (+34.9%) | 0 | fail: R; noise; unsupported; not confirmed; fraction |
| w06 | stable | yes | X03, X04 (N3, R) | yes, direct E4 | +21.8% [+3.4, +37.6] | {R} (+21.9%) | 0.998 | fail: noise |
| w07 | change | yes | X03, X04 (E, N3) | yes, direct E6 | +18.2% [+6.0, +28.3] | {E} (+18.7%) | 0.974 | fail: noise |
| w08 | change | yes | X06 (E) | **no** | +20.0% [+9.9, +28.4] | {E} (+20.0%) | 1.000 | fail: unsupported |
| w09 | null | – | none | – | – | – | – | **success** |
| w10 | change | yes | X05, X06 (N5, E) | no | +17.6% [+1.5, +34.5] | {E} (+20.7%) | 0.852 | fail: noise; unsupported |
| w11 | change | yes | X07, X08 (R, E) | no | +21.1% [+8.9, +33.9] | {E, D} (+25.5%) | 0.828 | fail: R; unsupported |
| w12 | null | – | none | – | – | – | – | **success** |

### Informativeness checks (t0-beta, evaluator only)

| world | detection, E alone (change) or R alone (stable) | oracle candidates on confirmation |
|---|---|---|
| w01 | days 99–112 +29.0% [+17.1, +37.8]; 99–126 +21.3% [+4.3, +35.0] | {E} +30.6% [+16.5, +41.9]; {D} +20.2% [+3.6, +35.8]; {E, D} +31.3% [+17.7, +42.7] |
| w02 | +48.8% [+35.4, +59.0]; +43.7% [+33.1, +52.4] | {E} +28.1% [+17.1, +37.2]; {D} +9.9% [−1.5, +23.5]; {E, D} +26.1% [+13.9, +35.9] |
| w03 | days 57–84 +37.9% [+25.2, +46.8]; 85–112 +48.0% [+34.5, +57.1]; 99–126 +41.8% [+26.0, +55.2] | {R} +32.5% [+21.3, +41.3] |
| w04 | +3.6% [−29.1, +25.1]; +14.6% [−1.3, +28.8] (**not detectable**) | {E} +42.3% [+31.1, +54.8]; {D} +31.3% [+18.4, +43.2]; {E, D} +39.8% [+28.7, +50.8] |
| w05 | +32.5% [+17.8, +48.8]; +34.4% [+21.5, +46.8] | {E} +34.9% [+18.6, +46.1]; {D} +13.9% [−4.7, +29.5]; {E, D} +32.9% [+15.0, +45.6] |
| w06 | +30.2% [+11.9, +41.6]; +27.0% [+4.4, +45.0]; +20.0% [−1.4, +37.4] | {R} +21.9% [+2.9, +38.6] |
| w07 | +32.0% [+2.8, +45.9]; +24.6% [+6.3, +35.8] | {E} +18.7% [+6.8, +28.0]; {D} +7.6% [−2.4, +18.1]; {E, D} +16.6% [+4.2, +27.1] |
| w08 | +22.1% [+7.9, +34.0]; +22.4% [+9.3, +34.9] | {E} +20.0% [+9.9, +28.4]; {D} +7.1% [−3.2, +17.0]; {E, D} +16.6% [+5.1, +26.2] |
| w10 | +41.6% [+31.7, +48.3]; +39.2% [+31.5, +46.8] | {E} +20.7% [+2.5, +36.7]; {D} +4.7% [−14.5, +21.9]; {E, D} +13.4% [−6.9, +30.1] |
| w11 | +15.5% [−5.6, +31.8]; +22.9% [+8.0, +35.5] | {E} +24.2% [+13.2, +35.9]; {D} +5.1% [−9.8, +17.3]; {E, D} +25.5% [+13.1, +37.1] |

**E and D on confirmation.** The table gives D given E and E given D. D-alone and E-alone are in the table above. D
never added value given E (no lower bound above 0). E added value given D in 6 of 8 change worlds.

| world | D given E | E given D |
|---|---|---|
| w01 | +0.9% [−3.4, +5.6] | +13.8% [+1.5, +26.4] |
| w02 | −2.7% [−6.1, +0.6] | +18.0% [+5.7, +28.0] |
| w04 | −4.4% [−21.2, +6.6] | +12.4% [+5.4, +21.2] |
| w05 | −3.1% [−7.6, +1.0] | +22.0% [+4.1, +37.5] |
| w07 | −2.6% [−9.1, +3.4] | +9.7% [−3.3, +20.0] |
| w08 | −4.2% [−10.5, +1.5] | +10.2% [+4.5, +16.0] |
| w10 | −9.2% [−21.1, −0.5] | +9.1% [−3.5, +19.2] |
| w11 | +1.7% [−5.2, +8.8] | +21.5% [+9.1, +35.3] |

### Every experiment, in order

Each entry reads: covariates (roles) | reference | scored days | skill [95%].
- "cur." marks current-regime evidence: in change worlds, scored entirely from τ on.
- In stable and null worlds every experiment is current.

**w01 (change, τ 86)**
- E1 {N1,E,N4,R} | – | 57–84 | +39.7% [+28.9]
- E2 {D,N3,N2,N5} | – | 57–84 | −9.8% [−22.9]
- E3 {N1,E} | – | 85–112 | +29.1% [+13.6]
- E4 {N4,R} | – | 85–112 | +3.7% [−15.2]
- E5 {E} | given N1 | 99–126 | +20.5% [+3.9], cur.
- E6 {D,N3,N2,N5} | given N1,E | 99–126 | −3.0% [−13.1], cur.

Beliefs: R rejected after call 2; E promising → accepted after call 3; N1 promising. Final {N1, E}. Its own conclusion
says N1's marginal value over E "was never isolated".

**w02 (change, τ 91)**
- E1 {N4,D,N3,E} | – | 57–84 | −9.7% [−20.2]
- E2 {R,N2,N1,N5} | – | 57–84 | +49.6% [+37.6]
- E3 {R,N2} | – | 85–112 | +4.0% [−10.8]
- E4 {N1,N5} | – | 85–112 | −1.4% [−13.7]
- E5 {N4,D,N3,E} | – | 85–112 | +31.9% [+10.7]
- E6 {N4,D} | given N3,E | 99–126 | −1.0% [−8.1], cur.

Beliefs: R deteriorated after call 2; the rejected block re-opened (rejected → promising), then E and N3 accepted, N4
and D redundant. Final {N3, E}: "X03 and X04 were not separated".

**w03 (stable)**
- E1 {D,N4,N3,E} | – | 57–84 | +4.0% [−8.2]
- E2 {N5,N2,N1,R} | – | 57–84 | +37.3% [+22.6]
- E3 {N5,N2} | – | 85–112 | −11.5% [−22.1]
- E4 {N1,R} | – | 85–112 | +48.5% [+35.0]
- E5 {D,N4,N3,E} | – | 85–112 | −18.1% [−32.5]
- E6 {N1} | given R | 99–126 | −2.8% [−8.5]

Final {R}, supported by elimination (E4 positive, then N1 given R null in a later call). R accepted, not declared
deteriorated.

**w04 (change, τ 86; not informative)**
- E1 {N3,E,R,N1} | – | 57–84 | +37.0% [+23.5]
- E2 {D,N4,N5,N2} | – | 57–84 | −8.3% [−19.8]
- E3 {N3,E} | – | 85–112 | +11.7% [−4.1]
- E4 {R,N1} | – | 85–112 | +2.0% [−10.6]
- E5 {D,N4,N5,N2} | – | 85–112 | +2.5% [−13.3]
- E6 {D,N4,N5,N2} | – | 113–126 | +7.0% [−12.6], cur.

E marked deteriorated. Final: none. E alone was not detectable on the observed post-change windows (+3.6% and +14.6%,
both lower bounds below 0), though E was strong on confirmation (+42.3%).

**w05 (change, τ 90)**
- E1 {R,D,N5,N1} | – | 57–84 | +36.4% [+15.9]
- E2 {N3,N4,N2,E} | – | 57–84 | −5.1% [−15.5]
- E3 {R,D} | – | 85–112 | +14.8% [−1.3]
- E4 {N5,N1} | – | 85–112 | −10.1% [−24.8]
- E5 {N3,N4,N2,E} | – | 85–112 | +19.7% [+7.0]
- E6 {N3,N4,N2,E} | given R,D | 99–126 | +14.4% [−0.2], cur.

R and D deteriorated; the rejected block re-opened. Final: six candidates (R, D, three noise, E), "the evidence is
set-level throughout".

**w06 (stable)**
- E1 {N2,N5,N3,R} | – | 57–84 | +22.8% [+5.2]
- E2 {E,N4,N1,D} | – | 57–84 | −13.4% [−26.0]
- E3 {N2,N5} | – | 85–112 | −4.9% [−16.2]
- E4 {N3,R} | – | 85–112 | +23.5% [+0.5]
- E5 {E,N4,N1,D} | – | 85–112 | −16.0% [−38.9]
- E6 {R} | given N3 | 99–126 | +22.3% [+2.1]

Final {N3, R}, directly supported by E4. N3 is included "on pair-level evidence only"; its own status stayed
promising. R accepted.

**w07 (change, τ 86)**
- E1 {N5,N1,E,N3} | – | 57–84 | +2.8% [−3.8]
- E2 {R,D,N2,N4} | – | 57–84 | +32.8% [+15.3]
- E3 {R,D} | – | 85–112 | +7.5% [−9.0]
- E4 {N2,N4} | – | 85–112 | −9.0% [−16.9]
- E5 {N5,N1} | – | 99–126 | +0.6% [−10.0], cur.
- E6 {E,N3} | – | 99–126 | +23.0% [+2.2], cur.

R deteriorated; re-screened the earlier-dismissed block. Final {E, N3}, directly supported by E6: "I cannot say
whether both members contribute".

**w08 (change, τ 87)**
- E1 {N4,D,N1,N5} | – | 57–84 | −7.7% [−22.4]
- E2 {R,E,N3,N2} | – | 57–84 | +27.2% [+13.7]
- E3 {R,E} | – | 85–112 | +21.1% [+2.5]
- E4 {N3,N2} | – | 85–112 | −5.3% [−12.3]
- E5 {R} | – | 99–126 | −6.4% [−13.9], cur.
- E6 {N4,D,N1,N5} | given R,E | 99–126 | +1.0% [−13.3], cur.

Final {E}, accepted, with oracle fraction 1.00. It is unsupported under the frozen rule:
- the only positive test on a set containing E is E3, whose days 85–112 include two pre-change days (τ 87);
- the post-change tests (R alone null; the noise set given R and E null) never put E among the covariates;
- the researcher itself noted that "X06 alone was never tested directly".

**w09 (null)**
- {E,R,N1,N4} and {D,N3,N2,N5} were each screened on days 57–84, 85–112 and 99–126.
- All six lower bounds were below 0.
- All candidates rejected. Final: none.

**w10 (change, τ 89)**
- E1 {N1,D,N2,N3} | – | 57–84 | −3.7% [−16.7]
- E2 {N5,E,R,N4} | – | 57–84 | +29.9% [+14.4]
- E3 {N5,E} | – | 85–112 | +37.3% [+26.0]
- E4 {R,N4} | – | 85–112 | +0.9% [−14.5]
- E5 {N1,D,N2,N3} | – | 85–112 | +19.1% [+3.5]
- E6 {N1,D,N2,N3} | given N5,E | 99–126 | −5.4% [−14.7], cur.

Final {N5, E}, both accepted, and "their individual contributions were never separated". E3 straddles the change (τ
89).

**w11 (change, τ 90)**
- E1 {N4,N2,D,N1} | – | 57–84 | −2.0% [−14.3]
- E2 {N3,N5,R,E} | – | 57–84 | +14.7% [+0.2]
- E3 {N3,N5} | – | 85–112 | −4.5% [−18.5]
- E4 {R,E} | – | 85–112 | +15.4% [−0.0]
- E5 {N4,N2,D,N1} | – | 85–112 | +2.6% [−10.9]
- E6 {N3,N5} | given R,E | 113–126 | −1.0% [−13.2], cur.

R and E both accepted. Final {R, E}, which keeps the retired driver. No post-change experiment had E or D as a
covariate.

**w12 (null)**
- Both blocks were screened on days 57–84, 85–112 and 99–126.
- All lower bounds were below 0, and the last two were significantly harmful.
- All statuses stayed untested. Final: none.

### Per-world cost (all: 4 API attempts, 0 refusals, 0 repairs, every call valid)

| world | tokens | t0-beta forecasts, research / evaluate | loop wall time | job time |
|---|---|---|---|---|
| w01 | 27,582 | 238 / 994 | 98 s | 157 s |
| w02 | 27,012 | 238 / 994 | 96 s | 149 s |
| w03 | 27,416 | 238 / 1,050 | 93 s | 153 s |
| w04 | 29,840 | 224 / 896 | 108 s | 170 s |
| w05 | 28,318 | 238 / 966 | 102 s | 161 s |
| w06 | 27,714 | 238 / 1,078 | 96 s | 150 s |
| w07 | 27,514 | 238 / 994 | 97 s | 154 s |
| w08 | 28,852 | 252 / 1,036 | 105 s | 158 s |
| w09 | 26,602 | 210 / 882 | 85 s | 139 s |
| w10 | 27,527 | 238 / 994 | 95 s | 156 s |
| w11 | 27,105 | 224 / 896 | 93 s | 149 s |
| w12 | 27,356 | 210 / 882 | 82 s | 137 s |

## 6. Aggregates

| measure | value |
|---|---|
| Change-world success | 0 of 8 (7 informative) |
| Stable-world success | 1 of 2 (w03) |
| Null-world success | 2 of 2 |
| Useful-information recall | E in the final selection in all 7 informative change worlds (w04, not informative, had an empty selection). R in the selection in both stable worlds |
| Retired driver R kept | 2 of 8 change worlds (w05, w11) |
| Pure noise in the final selection | 6 worlds: change w01, w02, w05, w07, w10; stable w06 |
| False accepts in null worlds | 0 |
| Oracle fractions, informative non-null worlds | w01 0.985, w02 0.994, w03 1.000, w05 0.000, w06 0.998, w07 0.974, w08 1.000, w10 0.852, w11 0.828 |
| Median oracle fraction | 0.985 (threshold 0.80) |
| Experiments used | 6 in all 12 worlds |

**Descriptive only, never scored:**
- **Reopened stale negatives** (learn1's rule): in all 8 change worlds the researcher re-tested, after the change,
  candidates whose earlier evidence was negative and from before the change.
- **Conditional or separation experiments:** used in 10 of 12 worlds; not in the two null worlds, where it screened
  blocks only.
- **All six experiments used:** in 12 of 12 worlds.
- **Earlier failed experiments cited in later calls:** in 12 of 12 worlds.

## 7. Evidence-support failures

Support was evaluated only for change and stable worlds with a non-empty selection.
- **Supported** (3 worlds):
  - w03 {R}, by elimination;
  - w06 {N3, R}, directly;
  - w07 {E, N3}, directly.

  Two of these contain a noise candidate.
- **Unsupported** (6 informative worlds):
  - **w01, w02, w10, w11:** the only positive test of the final set, or of a superset, is on days 85–112, which
    straddles the change, or comes before it. No post-change experiment tests the final set or each member alone.
  - **w08:** the selection {E} is correct, but no post-change experiment had E as a covariate, and E3 (days 85–112)
    starts two days before τ.
  - **w05:** a six-candidate set with no positive post-change test of it or of a superset (E6's lower bound is −0.2%).
- **Recurring pattern:**
  - the researcher kept the pair or group that tested positive and did not separate its members;
  - in four worlds it said so in its conclusion: w01 "never isolated", w02 "not separated", w07 "cannot say whether
    both members contribute", w10 "never separated";
  - that left a noise candidate in the final set.

## 8. Null-world false discoveries

None.
- **w09:** all candidates rejected; selection empty.
- **w12:** all left untested; selection empty.
- **Neither conclusion claims an established effect.** "Final selection: none. The target-only forecast is used after
  day 126 … No group showed skill whose interval excluded zero" (w09). "Final selection: no covariates; forecast from
  target history only … no result gave any positive signal to justify including a candidate" (w12).
- So the frozen structural reading of null criterion 3 and a reading of the prose give the same result here.

## 9. Cost

**Scored run:**
- tokens: 332,838 over 48 attempts (0 refusals, 0 repairs);
- t0-beta forecasts: 2,786 in research and 11,662 in evaluate;
- research loops: 82–108 s each;
- research jobs: 137–170 s each;
- evaluate: 690 s;
- wall time 20.5 minutes (three waves), about 43 runner-minutes in all.

**Preflight:**
- 27,906 tokens over 4 attempts;
- 210 t0-beta forecasts;
- about 3.4 runner-minutes.

**Total:** 360,744 researcher tokens, 52 API attempts, 14,658 t0-beta forecasts, about 46 runner-minutes.

## 10. The frozen programme reading

| row 3 criterion | required | observed | met |
|---|---|---|---|
| Change successes | ≥ 6 of 8 | 0 | no |
| Stable successes | 2 of 2 | 1 (w06 selected noise) | no |
| Null successes | 2 of 2 | 2 | yes |
| Median oracle fraction | ≥ 0.80 | 0.985 | yes |
| Informative non-null worlds with pure noise selected | ≤ 1 | 6 | no |
| False accepts in null worlds | 0 | 0 | yes |

**Programme reading: KERNEL NOT PROVEN** (row 4). Under the spec, "proven" would have meant demonstrated against this
frozen synthetic benchmark at these thresholds, so "not proven" is likewise a statement about this benchmark only.

**Scope:**
- twelve synthetic worlds from one generator family, with one stochastic trajectory of the researcher in each;
- this result says nothing about real markets;
- no threshold, rule or world was changed after the run, and no second batch was run.

**Closing line:** `STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL`
