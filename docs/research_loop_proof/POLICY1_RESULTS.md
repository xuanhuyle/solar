# policy1: results and dispatch log

*Owner instruction: [`NEXT_POLICY_ARCHITECTURE_PROMPT.md`](NEXT_POLICY_ARCHITECTURE_PROMPT.md). Architecture note:
[`POLICY1_ARCHITECTURE.md`](POLICY1_ARCHITECTURE.md). Frozen spec: [`POLICY1_SPEC.md`](POLICY1_SPEC.md). Every dispatch
of `.github/workflows/research-loop-policy1.yml` is listed here. The published records are on branches
`policy1/run-<id>` (manifest-checked). beta1, learn1 and Phase 0 results are unchanged.*

**Outcome: NO ARCHITECTURE SIGNAL** (frozen reading, row 5). On this world the result went against the hypothesis.

- **L (lesson only) completed the essential loop cleanly.**
  - It split its positive pair and saw the old driver decay.
  - It re-screened the two candidates it had rejected, one at a time, on post-change data.
  - It selected the emerging driver alone.
- **S (structured state) recorded everything the architecture asks for, but allocated worse.**
  - It recorded stale evidence, the regime change, unresolved attribution and the budget consequence.
  - It re-screened the rejected candidates as one group, conditional on the decaying driver.
  - It spent its last experiment confirming that group, not decomposing it.
  - It then selected all four candidates, the retired driver and the noise included.

One world, one trajectory per condition.

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37227665244](https://github.com/xuanhuyle/solar/actions/runs/37227665244) | replay (engineering) | `0660a3d` | operational **PASS** (both replays) |
| 2 | [37229442597](https://github.com/xuanhuyle/solar/actions/runs/37229442597) | preflight | `c67cd6f` | **PASS**: L and S each 4 of 4 calls valid, 0 refusals, 0 repairs |
| 3 | [37229722055](https://github.com/xuanhuyle/solar/actions/runs/37229722055) | run (scored, paired) | `c67cd6f` | **NO ARCHITECTURE SIGNAL** (integrity clean) |

**Sequence:**
- The spec was frozen at `7b3c5f6`, after the replays.
- The one pre-run check confirmed one evaluator defect: "supported" could be cancelled by a later conditional test or
  by the order in which tests were listed. It was corrected at `c67cd6f`, before any preflight or scored world
  existed (spec section 7).
- `policy1_spec_sha` is `544c2a8a56a01743d35df5ab9a963af51860f62f286e1086019e891dd6c5c497`, for both the preflight and
  the scored run.

## 1. The minimal architecture

S's state is filled by the researcher every call and rendered back to it the next call:

| Field | Purpose |
|---|---|
| `regime_assessment` | stable / possible_change / changed / unknown, with cites and a justification |
| at most 3 `decision_uncertainties` | what is unresolved and why it matters; in the final call, what remains |
| `budget_needs` | what must still be resolved before the final selection |
| per candidate: `freshness`, `evidence_type`, `last_scored_day`, `attribution` | when and how each status was established, and what is unresolved about the candidate's own contribution |
| per experiment: `targets_uncertainty`, `possible_followup`, `budget_rationale` | which uncertainty it targets, its likely follow-up, and why it is worth a budget slot now |

**The software only validates the fields.** Nothing was hard-coded:
- no re-test after a change;
- no reserved experiment;
- no forced split;
- no single-variable rule;
- no quota or sequence.

The model chose every experiment and the final selection. S received the same lesson as L and no new prose.

## 2. Regression replays (run 37227665244): engineering checks, not evidence

These replays are contaminated by our knowledge of these worlds, so they are never validation.

**Setup:**
- Both published worlds regenerated to their published observed hashes, and the replayed results equal the published
  originals.
- S made round 3 (one experiment left) and the final call.
- 4 valid calls, 0 refusals, 0 repairs; 35,963 tokens.

**beta1 replay: stale evidence was represented.**
- X03 was marked deteriorated and possibly_stale; X01 and X02 were marked "stale … dated to the pre-change regime".
- The regime was marked possible_change, citing the decay and a 44% rise in the baseline error.
- S chose to re-screen X01+X02 "rather than re-confirming X03's decline", and the pair gave +38.2%.
- The final state marked attribution within the pair unresolved, and S selected the pair.

**learn1 replay: attribution and follow-up cost were represented.**
- The positive group's members were typed "grouped", each with "share of the set's gain is unknown".
- Its stated budget consequence: "Attribution (U2) … will stay unresolved" with one experiment left.
- S chose to re-confirm the set on recent data (+23.6%) and selected the set whole.

**No interface correction was made.**

## 3. Integrity (scored run 37229722055)

- **Issues:** none. Call failures: none.
- **Observed data:** the hash is identical across the regenerated, shipped and declared copies.
- **System texts:**
  - L's equals learn1's lesson condition byte for byte (same sha256);
  - S's equals L's plus the research-state section and schema;
  - both were checked against the frozen texts.
- **Prompts and experiments:** every prompt was rebuilt byte for byte from that condition's own record (L with Phase 0's
  renderer, S with its own). All 12 experiments were recomputed with t0-beta.
- **Separation:**
  - no canary;
  - the guard confirmed both jobs had no truth on disk;
  - two parallel jobs, identical except for the condition, with separate artifacts.
- **Model:** the pinned model on all 8 attempts.

## 4. Hidden world (revealed after both runs)

**Change point:** the first changed day is τ = 90.

**Roles:**
- R (retired) = X01;
- E (emerging) = X03;
- D (proxy) = X04, sign −1;
- N (noise) = X02, sign −1.

**Evidence available by round** (t0-beta, against no covariate):

| Test | Skill |
|---|---|
| R on days 57–84 (round 1) | +40.9% [+32.7, +49.1] (strong) |
| E on days 99–112 (round 2) | +27.5% [+9.8, +42.0] |
| E on days 99–126 (round 3) | +32.0% [+20.8, +39.7] |

Every element of the problem was present and detectable.

## 5. Lesson-only trajectory (L)

| Round | Experiments → evidence | Belief updates / budget left |
|---|---|---|
| 1 (days 1–84) | E1 {X01, X02}: **+39.9%** [+30.7, +48.4]; E2 {X03, X04}: −6.0% [−20.0, +9.3] (both days 57–84). "A positive set result will need follow-up to attribute it." | X01, X02 promising; X03, X04 rejected; 4 left |
| 2 (days 1–112) | **Split the positive pair:** E3 X01 alone, 85–112: +2.2% [−10.1, +12.7]; E4 X02 given X01: −1.5% [−5.2, +1.8] | X01, X02 deteriorated; 2 left |
| 3 (days 1–126) | "By the prior lesson, every earlier rejection is now provisional." **Re-screened individually:** E5 X03 alone, 99–126: **+32.0%** [+20.8, +39.7]; E6 X04 alone: +18.0% [+4.7, +29.4] | X03 accepted; X04 promising; 0 left |
| Final | **Selected {X03}.** X04 left out because it was "never tested given X03, so its incremental value is unknown". | |

## 6. Structured-policy trajectory (S)

| Round | State (regime / uncertainties / freshness) | Experiments → evidence (targets, follow-up) | Updates / budget left |
|---|---|---|---|
| 1 | regime **unknown**; U1 X01/X02 alone?; U2 X03/X04 and "which member of the pair is responsible"; U3 drift; all freshness unknown | E1 X01 alone: **+40.9%** [+32.7, +49.1]; E2 X02 alone: −4.6%; E3 {X03, X04}: −6.0% [−20.0, +9.3] (targets U1, U1, U2; follow-ups state "if positive, test X03 alone …") | X01 promising; X02, X03, X04 rejected; 3 left |
| 2 | regime **stable**; U1 does X01 persist?; U2 "do X02–X04 add skill given X01 (their nulls rest only on days 57–84)"; U3 drift; every row **possibly_stale**; X03 and X04 typed "grouped" with attribution unknown | E4 X01 alone, 85–112: +2.2% [−10.1, +12.7]; **E5 {X02, X03, X04} given X01**: +16.5% [−0.5, +34.9] (follow-up: "if positive, use round 3 to attribute the gain to a single member") | X01 deteriorated; X02, X03, X04 promising; 1 left |
| 3 | regime **changed**; U1 does the set persist?; U2 "which members carry the E5 gain … with one experiment left full attribution is impossible"; U3 X01's residual value | **E6 {X02, X03, X04} given X01**, 99–126: **+29.0%** [+10.2, +40.8] (targets U1; rationale: "attribution cannot be completed with one experiment anyway") | 0 left |
| Final | regime changed; final uncertainties U1 attribution within X02–X04, U2 X01 residual, U3 persistence | | **Selected {X01, X02, X03, X04}**, "the configuration directly validated on the most recent data". X01 is "retained as the reference base under which the set was tested, not because it helps". |

## 7. Side by side: the ten behavioural questions

| # | Question | L | S |
|---|---|---|---|
| 1 | Recognised old evidence might be stale? | yes, after seeing the decay (round 3) | yes, earlier: every row possibly_stale from round 2, regime changed in round 3 |
| 2 | Re-opened stale hypotheses when warranted? | yes: X03 and X04 individually, after the decay | yes, earlier: X02, X03 and X04 jointly in round 2, conditional on X01 |
| 3 | Identified unresolved attribution after grouped evidence? | yes, and acted on it at once: split its positive pair in round 2 | yes, explicitly (U2 and the attribution fields), but did not act on it |
| 4 | Spent the remaining budget to resolve the final decision? | yes: the round 3 single re-screens decided the selection | no: the last experiment re-confirmed the group, and attribution was left open by choice |
| 5 | Avoided spending the last experiment on redundant confirmation? | yes (X04 alone, new information) | no: E6 repeated E5's design on fresher days |
| 6 | Identified the emerging driver? | **yes** | no: E was inside the selected set, never isolated |
| 7 | Excluded the retired driver? | yes | **no**: X01 kept as "reference base" |
| 8 | Avoided unsupported noise? | yes | **no**: X02 selected |
| 9 | Final selection better supported by its own experiments? | yes: E alone +32.0% [+20.8, +39.7] | no: no selected member has its own positive test |
| 10 | Fewer decision-critical uncertainties left at the end? | one gap (X04 given X03), outside the selection | three, all about its own selection |

**Frozen indicators:**

| | L | S |
|---|---|---|
| found | yes | no |
| supported | yes | no |
| essential loop | yes | no |
| beta1 reading | BASIC AUTONOMOUS LOOP OBSERVED | RESEARCHER FEASIBILITY FAILED |

## 8. Confirmation (days 127–154)

| Comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} (the true emerging information; L's selection) | **+30.7%** [+22.7, +37.9] | +32.6% [+20.9, +44.1] |
| S's selection {X01, X02, X03, X04} vs {} | +26.8% [+15.9, +35.8] | +37.2% [+28.7, +44.5] |
| E given D | +22.8% [+12.9, +30.3] | +31.2% [+22.4, +40.0] |
| D given E | −6.4% [−15.1, +1.4] | +4.0% [−5.9, +11.6] |
| R given E | −1.0% [−7.9, +5.9] | +1.9% [−5.9, +7.9] |
| N given E | −3.1% [−8.9, +2.8] | −4.7% [−13.3, +2.5] |
| {R} vs {} | −12.4% [−22.8, −3.5] | +1.3% [−4.6, +7.5] |

With t0-beta, S's extra covariates cost about 4 points against E alone. Ridge fits several covariates jointly and
scores S's set higher. That is forecast accuracy, not research behaviour.

## 9. Cost

**API:**
- **Replays:** 4 attempts, 35,963 tokens.
- **Preflight:** L 4 attempts, 25,161 tokens; S 4 attempts, 40,964 tokens.
- **Scored:** L 4 attempts, 24,024 tokens; S 4 attempts, 40,780 tokens.
- **Total:** 20 attempts, 0 refusals, 0 repairs, 166,892 tokens. S costs about 1.7 times L's tokens.

**t0-beta forecasts:**
- replays: 462;
- preflight: 490;
- scored research: 462;
- evaluate: 602;
- total: 2,016.

**Runner time:** 1,007 job-seconds (about 17 minutes). The three runs' wall time was 270 s, 240 s and 300 s.

**Pre-run check:** 7 agents.

**Implementation:** about 2,800 new lines including tests, the workflow and the two documents, and about 2.5 hours of
agent time.

## 10. Reading

**Why the frozen label is NO ARCHITECTURE SIGNAL:**
- found(S) is false and found(L) is true, so neither (a) nor (b) applies;
- only L completed the essential loop.

Under the owner's prose definitions the reading is the same: S's research policy was not better than L's. In this
world it was worse.

**What the structure did:** it made S state, earlier and more explicitly than L, that its old evidence might be stale,
that its group result left attribution open, and that one experiment could not close it.

**What it did not do:** change the allocation. S designed grouped and conditional screens in rounds 1 and 2 that
created the attribution problem. It then spent its last experiment confirming the group, and kept the whole "validated
configuration", the decayed driver included.

L, without the structure, split its positive pair at once and re-screened one candidate at a time. It found the driver.

**Caveat:** one world and one stochastic trajectory per condition. No reroll; a rerun is the owner's decision.
