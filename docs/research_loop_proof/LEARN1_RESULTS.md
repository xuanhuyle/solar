# learn1: results and dispatch log

*Owner instruction: [`NEXT_LEARNING_MILESTONE_PROMPT.md`](NEXT_LEARNING_MILESTONE_PROMPT.md). Frozen spec:
[`LEARN1_SPEC.md`](LEARN1_SPEC.md). Every dispatch of `.github/workflows/research-loop-learn1.yml` is listed here. The
published records are on branches `learn1/run-<id>` (manifest-checked). beta1's and Phase 0's results and verdicts are
unchanged.*

**Outcome: BOTH FAIL** (frozen reading, row 4: neither condition found the emerging driver).

**What differed:**
- The lesson visibly changed how the learned researcher (L) allocated experiments. After round 1 it marked its earlier
  rejections "provisional and dated", which is the lesson's own wording. It re-screened all three rejected
  candidates on post-change data, found a set effect, and ran a conditional test.
- The fresh researcher (F) re-tested only one rejected candidate, the proxy. It never returned to the emerging driver.

**Why neither counts as a success:**
- L's final selection contains the emerging driver, but L never isolated it, and it also kept the noise candidate
  without evidence that distinguished it.
- F selected the proxy alone.

**Scope:** one world, one stochastic trajectory per condition.

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37216965299](https://github.com/xuanhuyle/solar/actions/runs/37216965299) | lesson | `94c46fe` | **OK**: valid lesson on the first attempt |
| 2 | [37218198669](https://github.com/xuanhuyle/solar/actions/runs/37218198669) | preflight | `0c9ab85` | **PASS**: F and L each 4 of 4 calls valid, 0 refusals, 0 repairs |
| 3 | [37218439239](https://github.com/xuanhuyle/solar/actions/runs/37218439239) | run (scored, paired) | `0c9ab85` | **BOTH FAIL** (integrity clean) |

**Sequence:**
- The lesson was frozen at `21fb959`.
- The one pre-run check confirmed two evaluator defects, which were fixed at `0c9ab85` before any world existed (spec
  section 7).
- `learn1_spec_sha` is `35376d9c4c4739b324adc4895ba2a2ee3bd0ad283f2f5ff659b40017e0708340`. Both the preflight and the
  scored run ran under it.

## 1. The lesson (run 37216965299)

**Input** (built in code; the published `user_prompt` is rebuilt byte for byte by a test):
- the beta1 notebook as its researcher saw it, all four calls, ending with the final selection (none) and its
  conclusion;
- the owner's feedback paragraph, verbatim.

**What it did not receive:** no beta1 roles and no information about the new world. Its seed hashes this lesson, so it
did not exist yet.

**System text:** the owner's section 3 output requirements.

**The call:**
- **Result:** one attempt, `end_turn`, no refusal, no repair; 4,500 input and 259 output tokens; 7 s.
- **Model:** the served model's hash equals the pinned researcher model.

**The frozen lesson** (896 characters, sha256 `1c38b101…3a0bfb`), verbatim:

> When a relationship you relied on starts to decay, treat that as evidence that the system itself may have changed. A
> change in the system invalidates negative findings as much as positive ones. A null result describes one regime
> only. It says a factor did not help under the conditions in which it was tested. It does not say the factor will
> stay unhelpful once those conditions have shifted. If you see drift, mark every earlier rejection as provisional and
> dated, not settled. Then move budget away from repeatedly confirming the decline of the old favourite and towards
> re-screening previously dismissed factors on the most recent data, where an emerging signal would first show.
> Concluding that nothing works is safe only if every option has been examined after the change. Before calling a
> field empty, check whether your absence of evidence comes from the current regime or an outdated one.

**Records:**
- `research_loop_proof/learn1/lab/lesson.json` is byte-identical to the published file.
- The full record (prompts, response, usage, model hashes) is `learn1_lesson_record.json`.

## 2. Integrity (run 37218439239)

- **Issues:** none in either condition. Call failures: none.
- **Observed data:** the hash is identical across the regenerated, shipped and declared copies (`659772fe…`).
- **System texts:**
  - F's equals beta1's (the same sha256 as the beta1 scored run);
  - L's equals F's plus the lesson section, and nothing else;
  - both were checked against the frozen texts.
- **Prompts and experiments:** every user prompt was rebuilt byte for byte from that condition's own record. All 12
  experiments were recomputed with t0-beta.
- **Separation:**
  - the canary is absent from both records;
  - the guard confirmed both jobs had no truth on disk;
  - the two research jobs ran in parallel on separate runners with separate artifacts.
- **Model:** all 8 scored-run attempts were served by the pinned model.

## 3. Revealed world

**Change point:** the first changed day is τ = 88.

**Roles:**
- R (retired) = X04;
- E (emerging) = X01, sign −1;
- D (proxy of E) = X03;
- N (noise) = X02.

**Evidence availability** (t0-beta, against no covariate):

| Test | Skill | Reading |
|---|---|---|
| R on days 57–84 (before the change) | +13.3% [−0.4, +28.4] | the old relationship was weak; its interval includes 0 |
| E on days 99–112 (findable in round 2) | +12.5% [+0.2, +25.9] | barely |
| E on days 99–126 (findable in round 3) | +23.6% [+10.2, +32.8] | clear |

**How this world differs from beta1's:** neither researcher screened R in round 1. Both screened X01–X03 first. So
neither condition ever had an incumbent relationship to watch decay, which is the lesson's opening trigger. What both
saw instead was a late uptick in the week before the change.

## 4. Fresh trajectory (F)

| Round (days seen) | Beliefs entering | Experiments → evidence | Update / budget left |
|---|---|---|---|
| 1 (1–84) | all untested | E1 X01 alone, 57–84: −8.4% [−21.3, +3.9]; E2 X02 alone: −9.8% [−23.2, +2.4]; E3 X03 alone: −10.6% [−23.7, +2.2] | X01, X02, X03 rejected; 3 left |
| 2 (1–112) | X01–X03 rejected, X04 untested | E4 X04 alone, 85–112: +2.0% [−4.9, +8.7]; **E5 X03 alone (re-test, "largest late swing")**, 85–112: +5.1% [−2.9, +14.0] | X03 and X04 promising; 1 left |
| 3 (1–126) | X03, X04 promising | E6 X03 alone, 99–126: +2.6% [−6.1, +11.3] | unchanged; 0 left. Notes: "X01 and X02 were tested only before the apparent change, so their rejection is somewhat tentative." |
| Final | | | **Selection {X03}** (the proxy) |

F's conclusion again caveats that X01 and X02 were "tested only before the apparent regime change". beta1's researcher
wrote the same caveat. F noticed the gap and did not act on it.

## 5. Learned trajectory (L)

| Round (days seen) | Beliefs entering | Experiments → evidence | Update / budget left |
|---|---|---|---|
| 1 (1–84) | all untested | the same three screens as F, with the same results (E1–E3) | X01, X02, X03 rejected; 3 left |
| 2 (1–112) | X01–X03 rejected, X04 untested | E4 X04 alone, 85–112: +2.0% [−4.9, +8.7]; **E5 {X01, X02, X03} jointly (re-screen of all three rejections)**, 85–112: **+15.0% [+4.5, +26.5]** | X01, X02, X03 promising; X04 rejected; 1 left |
| 3 (1–126) | X01–X03 promising, X04 rejected | **E6 {X01, X02} given {X03}** (a separation attempt), 99–126: **+21.5% [+2.4, +34.8]** | unchanged; 0 left |
| Final | | | **Selection {X01, X02, X03}** = {E, N, D} |

**Where the lesson affected decisions** (L never wrote "lesson"; it used the lesson's language):
- **Call 1 notes:** "Save the remaining budget to re-check findings on the most recent data, because the process may
  drift."
- **Call 2 notes:** "The round-1 rejections are therefore provisional and dated to days 57-84." The lesson says:
  "mark every earlier rejection as provisional and dated, not settled".
- **E5's because:** "E1-E3 rejected these on days 57-84 only … a possible regime shift. This re-screens them on days
  85-112." The lesson says: "re-screening previously dismissed factors on the most recent data".
- **Call 3 notes:** "This fits a regime change in which the earlier nulls no longer hold." The lesson says: "A null
  result describes one regime only".

**Its final conclusion** acknowledges the gap: "X01 and X02 were never separated, and X03's own marginal value in the
new regime was not isolated".

Round 1 was identical in both conditions: the same three screens, with the same results. The two diverged exactly
where the lesson applies: after the first sign of change.

## 6. Side by side

| Did L, relative to F… | F | L |
|---|---|---|
| re-open stale negative findings? | one: X03 (D), alone | all three rejections: X01, X02 and X03 jointly |
| detect the emerging driver? | no; E never re-tested after round 1 | not individually; E sits inside a set that clearly helps |
| detect it earlier? | never | positive evidence for a set containing E in round 2 (E5) |
| spend fewer experiments reconfirming an obsolete driver? | no incumbent in this world; spent 2 of 6 re-testing the proxy alone (E5, E6) | 0 reconfirmations |
| avoid noise? | yes | **no**: N selected, with its only single result negative (E2) |
| produce a better supported final selection? | {D}: no interval excluded 0 | {E, N, D}: strong set-level support (E5, E6) but members not distinguished, which breaks the brief's own rule |

**Frozen indicators and beta1's reading:**

| | F | L |
|---|---|---|
| found(c) | no | no (N selected) |
| first round with positive evidence for E | never | 2 |
| reopened | X03 | X01, X02, X03 |
| lesson mentions | 0 | 0 |
| B1–B10 | B1 B2 B3 B4 B6 B8 B10 | B1 B2 B3 B4 B6 B8 B9 |
| beta1 reading | RESEARCHER FEASIBILITY FAILED (E detectable, never tested in rounds 2–3, not selected) | RESEARCHER FEASIBILITY FAILED (N selected, latest single result ≤ 0) |

## 7. Confirmation (days 127–154)

| Comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} (the true emerging information) | +41.9% [+25.5, +53.6] | +49.2% [+35.3, +56.3] |
| {D} vs {} | +27.1% [+10.2, +40.3] | +29.4% [+5.6, +46.4] |
| {R} vs {} | −2.0% [−11.2, +5.9] | −0.6% [−16.7, +12.2] |
| {N} vs {} | +2.2% [−8.8, +11.3] | −2.4% [−20.6, +13.1] |
| {E, D} vs {} | +38.8% [+23.0, +50.9] | +52.7% [+40.1, +59.9] |
| D given E | −5.2% [−10.4, +1.2] | +7.0% [−1.3, +15.8] |
| N given E | +2.4% [−2.4, +7.7] | +0.5% [−8.6, +10.2] |
| R given E | −0.5% [−5.1, +3.7] | −2.1% [−6.8, +3.2] |
| E given D | +16.1% [−6.1, +32.7] | +33.0% [+13.5, +44.6] |
| **F's selection {X03} = {D}** | **+27.1%** [+10.2, +40.3] | **+29.4%** [+5.6, +46.4] |
| **L's selection {X01, X02, X03} = {E, N, D}** | **+36.6%** [+20.6, +48.4] | **+52.4%** [+41.0, +58.8] |

L's selection forecasts better than F's with both instruments, but below E alone with t0-beta. The owner's rule
applies: a forecasting gain alone is not a learning signal.

## 8. Cost

**API:**
- **Lesson:** 1 attempt, 4,759 tokens.
- **Preflight:** F 4 attempts, 23,343 tokens; L 4 attempts, 25,126 tokens.
- **Scored run:** F 4 attempts, 23,064 tokens; L 4 attempts, 25,255 tokens.
- **Total:** 17 attempts, 0 refusals, 0 repairs, 101,547 tokens.

**t0-beta forecasts:**
- preflight: 476 (238 + 238);
- scored research: 462 (F 224, L 238);
- evaluate: 574;
- total: 1,512.

**Runner time:** 737 job-seconds (about 12 minutes). The three runs' wall time was 45 s, 201 s and 255 s.

**Pre-run check:** one workflow of 7 agents (5 checkers, 2 skeptics).

**Implementation:** about 2,500 new lines including tests and the workflow, and about 2 hours of agent time
(planning, build, runs and report).

## 9. Reading

**Why the frozen label is BOTH FAIL:**
- found(L) is false because L also selected N;
- found(F) is false;
- criterion (c) does not apply because F also re-opened one stale negative (the proxy).

None of the three improvement criteria holds, so the result reads "LEARNING SIGNAL OBSERVED" under none of them.

**The lesson-mention check (literal words) missed L's paraphrases.** That does not change the label, because there was
no qualifying improvement for a link to qualify.

**What was observed:** the pattern the owner described, in part:
- L recognised that its old negative evidence might be stale, in the lesson's words;
- it moved budget to re-screen the dismissed candidates on recent data;
- it found and kept the signal that contains the emerging driver.

**What was not observed:**
- an incumbent decaying (this world never gave either researcher one);
- the emerging driver isolated;
- noise kept out.

**Caveats:** one world and one trajectory per condition. With a stochastic researcher, part of the difference may be
chance. No reroll; a rerun is the owner's decision.
