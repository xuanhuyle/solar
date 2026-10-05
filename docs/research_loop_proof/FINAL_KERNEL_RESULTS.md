# Final kernel results: context, cheap trials, referee and memory on four synthetic companies

*Owner instruction: [`NEXT_FINAL_KERNEL_PROMPT.md`](NEXT_FINAL_KERNEL_PROMPT.md). Frozen specification:
[`FINAL_KERNEL_SPEC.md`](FINAL_KERNEL_SPEC.md) (`final_kernel_spec_sha`
`a28b39a5aad3e6a548fff903e57b1b93edae1635af5b8a63b71dbf043f979694`, commit `ea9902d`). The scored record is the orphan
branch `final-kernel/run-37332048132` (`evaluation.json`, `REPORT.md`, every research record, every memory artifact,
every context, `MANIFEST.sha256`). Every number below comes from that record unless it says otherwise.*

## Reading: FULL KERNEL PROVEN FOR THIS BENCHMARK

Row 3 of the frozen programme reading applies. Every condition holds, and the first one holds with no margin:
- **K episode successes:** 6 of 8, exactly the threshold. They are c1e3, c2e3, c3e2, c3e3, c4e2 and c4e3.
  - Non-null episodes strong: 4 of 6. Null episodes: 2 of 2 null successes.
  - The two failures are c1e2 (P3) and c2e2 (P2), both for lack of a confirmed headline (section 9).
- **Incorrect approvals:** no K episode had an incorrect individual or conditional approval of a pure-noise or stale
  candidate (allowance: 1).
- **Oracle fraction:** the median of K's oracle-fraction analogue is 1.000 over the 6 non-null episodes
  (0.007, 1, 1, 1, 1, 1).

Rows 1 and 2 do not apply:
- material integrity issues: none; missing scored trajectories: none; generator defects: none;
- the 8 memory artifacts recomputed by evaluate are identical to the shipped ones;
- all 6 non-null scored episodes were informative.

**Secondary diagnostic (never gating):** K against F over the 8 pairs was 2 K WIN, 1 F WIN and 5 TIE.
- F reached strong success in 5 of 6 non-null episodes, K in 4 of 6.
- Both K wins are the two recurrence episodes (P1), where K found the validated source after 3 experiments; F needed 5
  and 6.
- K saved no experiments: every trajectory used all 6.

Accumulated knowledge made K faster where the past repeated itself. It did not make K more often right.

**Closing line:** `MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST`

**Scope:**
- Four synthetic companies from one generator family, and eight scored episodes, each with one stochastic trajectory
  per condition.
- The pass sits exactly at the 6-of-8 threshold. One more failed episode would have read FULL KERNEL NOT PROVEN.
- "Proven" means demonstrated on this frozen benchmark at its thresholds. It is not a universal proof and not evidence
  of real-market performance.

## 1. The kernel tested

> company/domain context + AI researcher + covariate-capable forecasting foundation model as a cheap experimental
> instrument + deterministic scientific referee + accumulated validated research knowledge.

- **Context:** each study period's company context (section 3), placed in the user prompt as labelled data.
- **Researcher:** Discovery1's L8, not repaired (section 2).
- **Instrument:** t0-beta with a 7-day context.
  - Each experiment scores a covariate set against a reference set on a legal window.
  - Nothing is fitted on the research path.
  - Served revision `c8885416…`; `model.safetensors` sha256 `a0fd8abd…`; `tfc-t0` 0.5.0; pinned and verified on
    load.
- **Referee:** deterministic and truth-free (`final_kernel/lab/referee.py`). It approves positive findings only at the
  granularity tested and confirms them on the period's holdout days 127–154.
- **Memory:** the referee's entries for each company, carried from period to period.

**Two conditions per scored study period:**
- **K:** context plus memory.
- **F:** the identical context and data with empty memory.

E1 runs once per company with empty memory and seeds K's memory.

**The question (owner):** when the researcher has realistic company context and can accumulate validated empirical
knowledge across related investigations, can the full loop repeatedly turn cheap covariate trials into scientifically
valid predictive findings, and does accumulated knowledge materially improve later research versus the same
researcher starting fresh?

**The owner's binding corrections, frozen in the spec before any world existed:**
- K against F is a secondary diagnostic, never a gate.
- "≥ 6/8" counts each episode's own success: strong when non-null, null success when null.
- Appropriate use of knowledge is judged through the pattern criteria, with no extra gate.

## 2. The L8 research policy was not repaired

- **System text:** all 20 research records carry system sha256
  `78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d`. That is Discovery1's scored value and the value
  Kernel1 used.
- **Lesson:** learn1's frozen lesson, sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`
  (`lesson.json` on the record).
- **Unchanged:** the pinned model and effort, the X01–X08 menu, three rounds (cutoffs 84, 112 and 126) plus a final
  call, 6 experiments with at most 3 per round, the schema and checks, one repair turn per call, and the 80k token cap.
  The Phase 0, beta1, learn1, policy1, discovery1, human1 and Kernel1 packages, their specs, results and workflows are
  untouched. `git diff cb215e6..ea9902d` adds only new files: the final_kernel package, its spec, its workflow and its
  test file.
- **Code:** `ResearcherFK.run_call` is `Researcher8.run_call` with one changed line,
  `user = self.data + user_prompt(step, self.calls)`. A source-diff test checks it.
- **Prompt rebuild:** evaluate rebuilt every call's prompt with the expected data block. F and E1 got the empty memory
  text and K got the shipped memory. Nothing differed.
- **No Kernel1 lesson was added.** Nothing was derived from Kernel1's failures: no rule about noise, splitting,
  decomposition or saving experiments. The data block headers say "data, not instructions", and a banned-word test
  covers every fixed text.

## 3. Context construction

- **Companies:** four synthetic companies, each with a profile, a forecast mandate (tomorrow's 24 hourly values of
  its target) and a data dictionary:

  | company | target | regime descriptor |
  |---|---|---|
  | c1 Northbrook Water | treated-water demand | supply configuration |
  | c2 Coastline Grocers | checkout transactions | store format mix |
  | c3 Ridgeway Parcels | parcels arriving at the sorting hub | network role |
  | c4 Helios Data Centres | electricity drawn by the campus | tenant mix |
- **Dictionary:** X01–X08 map to eight plausible sources in three families of three, three and two.
  - One three-source family holds a measurement pair: a second measurement of the same quantity. Examples are c1's
    two temperature forecasts and c3's client order forecast from two channels.
  - The two-source family is never useful.
- **Each context** gives the profile, the mandate, the dictionary, the period's regime value, a two-event operating
  log dated between day −28 and day −1, and the research question. Contexts run 1.8–2.2 kB.
- **Clues and red herrings:** the log always names both three-source families. One is the genuine clue (the useful
  source's family) and the other a red herring. In a null period both are red herrings and the clue is the regime
  change.
  - The log builder never sees roles. Text, order and dates cannot tell the clue from the red herring.
  - The clue narrows the search to a family, never to a variable.
- **Example (c2, period 2):** both 3-source families are named.
  - "Day −7: The city councils changed bus and tram timetables and pedestrianised several shopping streets." This is
    the local-movement family, the red herring: footfall was the old useful source.
  - "Day −5: A new pricing and promotions system was rolled out to all stores." This is the promotions family, the
    genuine clue.
- **Every regime value:**
  - **c1:** E1 Configuration North; E2 Configuration South (one works, part bulk import); E3 Configuration Combined
    (merged network).
  - **c2:** E1 Format mix A (large-format); E2 Format mix B (convenience, after conversions); E3 Format mix A again.
  - **c3:** E1 Role 1 (regional hub); E2 Role 2 (national overflow); E3 Role 3 (new automated sorting line).
  - **c4:** E1 Tenant mix 1 (enterprise); E2 Tenant mix 1 again; E3 Tenant mix 2 (research and model-training).
- **Leak checks:** no context contains a role word (`companies.BANNED`; tested). Every context is published under
  `context/` on the record, and its sha256 matches the hash each research job declared.

## 4. Memory construction and proof that it holds no truth

**How memory is built:**
- The referee job of period p reads only:
  - period p's records (E1 or K);
  - period p's context tags (company, period, regime, source names);
  - the period's observed and holdout data, used only to confirm configurations that were tested and approved, or
    explicitly selected;
  - the previous memory.
- It writes one entry per tested configuration:
  - id, company, period and regime;
  - covariates and reference, with names;
  - status (positive, negative, unresolved or deteriorated) and exact granularity (individual, conditional on the
    reference, or set with attribution unresolved);
  - experiment references;
  - the governing research-window result;
  - holdout confirmation status and result, for approved positives.

**Which memory each K job gets:**
- K in period 2 gets memory after E1.
- K in period 3 gets memory after E1 plus K's period-2 entries.
- F's findings never enter memory.
- Memory sizes: c1 6 then 12 entries; c2 6 then 12; c3 5 then 10; c4 6 then 12.

**Why it cannot hold truth:**
- `lab/referee.py` imports only `json` and `math`.
- Referee jobs use the same truth-free sparse checkout and guard as research jobs, and hold no secret.
- Evaluate recomputed all 8 memory artifacts from the records and found 0 differences (`memory_checks`).
- Every entry is written in a closed vocabulary, and a test checks the rendering line by line.

**The c2 memory K received in period 2**, the first three of six entries (the full set is
`memory/c2-e1/memory.txt`):

```
M1 | study period 1 | regime: Format mix A: mostly large-format stores, weekly-shop focus | covariates X02 (Planned promotion intensity), X03 (Recorded promotion intensity), X04 (Competitor discount index) | reference none | status negative | granularity set (attribution unresolved) | evidence episode 1 experiment E1; decisive result days 57-84: skill -9.5% (95% interval -19.1% to +2.1%) | holdout days 127-154: not run
M2 | study period 1 | regime: Format mix A: mostly large-format stores, weekly-shop focus | covariates X05 (Local events index), X06 (Footfall forecast), X08 (Public-transport ridership forecast) | reference none | status positive | granularity set (attribution unresolved) | evidence episode 1 experiment E2; decisive result days 57-84: skill +25.3% (95% interval +10.9% to +38.0%) | holdout days 127-154: confirmed, skill +34.8% (95% interval +21.3% to +46.2%)
M4 | study period 1 | regime: Format mix A: mostly large-format stores, weekly-shop focus | covariates X06 (Footfall forecast) | reference X05 (Local events index), X08 (Public-transport ridership forecast) | status positive | granularity conditional on X05, X08 | evidence episode 1 experiment E4; decisive result days 85-112: skill +25.1% (95% interval +11.0% to +34.3%) | holdout days 127-154: confirmed, skill +32.8% (95% interval +16.5% to +45.3%)
```

**Pre-run revisions** (spec section 11), made before any preflight or scored world existed:
- an unresolved entry is rendered with its experiment references and its latest indicative result;
- "deteriorated" requires a positive result with an earlier last scored day.

The focused pre-run check refuted all seven of its findings. These two were applied anyway to match the owner's memory
field list. Neither touches approvals, headlines or scores.

## 5. Company sequences and patterns

**Patterns:**
- **P1 recurrence:** a validated relationship is useful again under the same regime.
- **P2 stale positive:** the earlier useful source stops after an observable change.
- **P3 reopened negative:** a source unhelpful before becomes useful after a change.
- **P4 null:** nothing is useful.

**Sequence assignment:** each company's sequence, X ids, families and roles were drawn from the spec sha and the run
id at dispatch. Different companies got different role permutations.

| company | sequence | E1 (memory seed) | E2 | E3 |
|---|---|---|---|---|
| c1 Northbrook Water | S2 | E1: useful X02 (Visitor-occupancy index) | P3: useful X05 (Area air-temperature forecast), X06 (Second-service temperature forecast); stale X02 | P4: null (no source useful); stale X02, X05, X06 |
| c2 Coastline Grocers | S1 | E1: useful X06 (Footfall forecast) | P2: useful X02 (Planned promotion intensity), X03 (Recorded promotion intensity); stale X06 | P1: useful X06 (Footfall forecast); stale X02, X03 |
| c3 Ridgeway Parcels | S4 | E1: useful X01 (Largest client's order forecast), X08 (Client order forecast from the shared portal) | P4: null (no source useful); stale X01, X08 | P3: useful X05 (Trunk-road congestion forecast); stale X01, X08 |
| c4 Helios Data Centres | S3 | E1: useful X06 (Solar-irradiance forecast) | P1: useful X06 (Solar-irradiance forecast) | P2: useful X05 (Tenant deployment calendar); stale X06 |


**What memory could do, by pattern:**
- **P1:** help. An earlier period validated the same source under the same regime value.
- **P2:** mislead. The old positive comes from another regime.
- **P3:** mislead twice over. The old positive points elsewhere. In this run the new source had also been tested in
  period 1 only inside sets that came out negative (c1: E6; c3: E2 and E6).
- **P4:** mislead. Earlier positives and the two named families tempt.

**Counts:** two scored periods of each pattern, two true nulls (c1e3 and c3e2), six non-null scored periods.

**Measurement pairs:** the useful source belongs to the measurement pair in three periods, and in each both members
count as useful:
- c1e2 (scored): two temperature services;
- c2e2 (scored): promotion intensity from the plan and from the pricing system;
- c3e1 (unscored): a client's order forecast from two channels.

## 6. Integrity

From `evaluation.json`, re-checked independently from the published files after the run (see "Verification" at the
end):

| check | result |
|---|---|
| material integrity issues; generator defects; missing scored trajectories | none; none; none |
| system text | sha256 `78fb0061…` in all 20 records, equal to `system_text8()` |
| lesson | `1c38b101…`, byte-identical to learn1's `lesson.json`, verbatim in every system text |
| model | 83 attempts (80 calls + 3 repairs); served model hash = requested hash = the pinned hash in every attempt; every attempt ended `end_turn` |
| instrument | t0-beta pinned; served revision = qualified revision; weights verified on load |
| guard | 20/20 `{truth_absent: true, git_removed: true, run_attempt: "1"}` |
| experiments recomputed | 120/120 identical |
| poison tests (every experiment re-run with the future shifted by +1e6 and set to NaN) | 0 mismatches |
| prompt rebuild | every call of every record, with the expected data block: 0 mismatches |
| K/F inputs | in all 8 scored periods K and F share the observed-data and context hashes; K's memory hash equals that of `memory/<c>-e<p−1>/memory.txt`; E1 and F have no memory and their prompts carry "No earlier findings are recorded for this company." |
| memory recomputation | 8/8 artifacts identical to evaluate's recomputation (confirmation numbers agree to about 1e-8, within the 1e-4 tolerance) |
| truth strings | 0 hits for canaries, seeds, role labels (N1–N5), pattern or sequence labels in the 136 published research, memory and context files |
| regeneration | designs, observed-data hashes, contexts and roles of all 12 periods regenerate exactly from the frozen code |
| manifest | all 140 entries verify |

Dispatches of the final-kernel workflow, all of them:

| run | mode | commit | attempt | result |
|---|---|---|---|---|
| 37329939712 | preflight (company c1 profile, sequence S1, non-scored) | `ea9902d` | 1 | PASS (5 trajectories valid, both memories checked; its truth was never read) |
| 37332048132 | run (`preflight_run=37329939712`) | `ea9902d` | 1 | evaluated once: FULL KERNEL PROVEN FOR THIS BENCHMARK |

## 7. Per-episode experiments, K and F

Every experiment of every trajectory is listed in order. Each entry gives the experiment id and its call, the covariates,
the reference ("given"), the window and its last scored day, and the t0-beta skill with its 95% interval. Skill is
measured against the reference, or against no covariates when there is no reference. E1 rows are the unscored first
period, which seeds memory.

### c1e1: S2, E1, non-null

Useful: X02; stale: none.

| | E1 |
|---|---|
| 1 | E1 (call 1): {X05}, 28 d to day 84: -3.7% [-13.6, +5.8] |
| 2 | E2 (call 1): {X02, X03, X07}, 28 d to day 84: +26.3% [+14.7, +34.4] |
| 3 | E3 (call 1): {X01, X04, X08}, 28 d to day 84: -4.5% [-21.0, +8.6] |
| 4 | E4 (call 2): {X02} given {X03, X07}, 28 d to day 112: +20.8% [+7.7, +32.7] |
| 5 | E5 (call 2): {X03} given {X02, X07}, 28 d to day 112: -1.2% [-10.9, +8.9] |
| 6 | E6 (call 3): {X05, X06, X08, X04} given {X02, X07}, 14 d to day 126: -21.3% [-40.5, -7.3] |
| final selection | {X02} |

### c1e2: S2, P3, non-null

Useful: X05, X06; stale: X02.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X05, X08}, 28 d to day 84: +38.9% [+22.9, +51.1] | E1 (call 1): {X02, X03, X07}, 28 d to day 84: +1.6% [-10.6, +13.4] |
| 2 | E2 (call 1): {X02, X03, X07}, 28 d to day 84: +1.6% [-10.6, +13.4] | E2 (call 1): {X05, X06, X08}, 28 d to day 84: +44.8% [+34.5, +53.0] |
| 3 | E3 (call 1): {X01, X04}, 28 d to day 84: +14.4% [+5.7, +24.0] | E3 (call 1): {X01, X04}, 28 d to day 84: +14.4% [+5.7, +24.0] |
| 4 | E4 (call 2): {X08} given {X05}, 28 d to day 112: -2.9% [-7.8, +2.4] | E4 (call 2): {X01, X04} given {X05, X06}, 28 d to day 112: -0.6% [-10.3, +7.0] |
| 5 | E5 (call 2): {X04} given {X01}, 28 d to day 112: -5.4% [-11.8, -0.6] | E5 (call 2): {X08} given {X05, X06}, 28 d to day 112: -0.1% [-3.4, +4.3] |
| 6 | E6 (call 3): {X02, X03, X07} given {X01, X05}, 28 d to day 126: -3.3% [-14.1, +6.5] | E6 (call 3): {X02, X03, X07} given {X05, X06}, 28 d to day 126: -1.5% [-8.2, +3.5] |
| final selection | {X01, X05} | {X05, X06} |

### c1e3: S2, P4, null

Useful: none; stale: X02, X05, X06.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X05, X06, X08}, 28 d to day 84: -0.6% [-16.2, +11.3] | E1 (call 1): {X02, X03, X07}, 28 d to day 84: -4.2% [-17.8, +9.0] |
| 2 | E2 (call 1): {X02, X03, X07}, 28 d to day 84: -4.2% [-17.8, +9.0] | E2 (call 1): {X05, X06, X08}, 28 d to day 84: -0.6% [-16.2, +11.3] |
| 3 | E3 (call 1): {X01, X04}, 28 d to day 84: -6.6% [-16.9, +3.1] | E3 (call 1): {X01, X04}, 28 d to day 84: -6.6% [-16.9, +3.1] |
| 4 | E4 (call 2): {X05, X06, X08}, 28 d to day 112: +5.8% [-11.0, +17.1] | E4 (call 2): {X02, X03, X07}, 28 d to day 112: -1.6% [-9.2, +6.3] |
| 5 | E5 (call 2): {X02, X03, X07}, 28 d to day 112: -1.6% [-9.2, +6.3] | E5 (call 2): {X05, X06, X08}, 28 d to day 112: +5.8% [-11.0, +17.1] |
| 6 | E6 (call 3): {X05}, 14 d to day 126: -4.6% [-20.7, +7.0] | E6 (call 3): {X05, X06, X08}, 14 d to day 126: -5.4% [-35.5, +17.4] |
| final selection | ∅ | ∅ |

### c2e1: S1, E1, non-null

Useful: X06; stale: none.

| | E1 |
|---|---|
| 1 | E1 (call 1): {X02, X03, X04}, 28 d to day 84: -9.5% [-19.1, +2.1] |
| 2 | E2 (call 1): {X05, X06, X08}, 28 d to day 84: +25.3% [+10.9, +38.0] |
| 3 | E3 (call 1): {X01, X07}, 28 d to day 84: -7.3% [-16.3, +0.5] |
| 4 | E4 (call 2): {X06} given {X05, X08}, 28 d to day 112: +25.1% [+11.0, +34.3] |
| 5 | E5 (call 2): {X08} given {X05, X06}, 28 d to day 112: -9.1% [-23.6, +1.5] |
| 6 | E6 (call 3): {X03, X04, X01, X07} given {X05, X06}, 28 d to day 126: -3.9% [-15.6, +6.1] |
| final selection | {X06} |

### c2e2: S1, P2, non-null

Useful: X02, X03; stale: X06.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X02, X03, X04}, 28 d to day 84: +41.7% [+22.8, +56.4] | E1 (call 1): {X05, X06, X08}, 28 d to day 84: -4.6% [-23.2, +9.9] |
| 2 | E2 (call 1): {X05, X06, X08}, 28 d to day 84: -4.6% [-23.2, +9.9] | E2 (call 1): {X02, X03, X04}, 28 d to day 84: +41.7% [+22.8, +56.4] |
| 3 | E3 (call 1): {X01, X07}, 28 d to day 84: -9.7% [-19.1, -0.5] | E3 (call 1): {X01, X07}, 28 d to day 84: -9.7% [-19.1, -0.5] |
| 4 | E4 (call 2): {X03}, 28 d to day 112: +20.0% [+9.0, +31.3] | E4 (call 2): {X03} given {X02, X04}, 28 d to day 112: +4.2% [-4.2, +16.6] |
| 5 | E5 (call 2): {X02, X04} given {X03}, 28 d to day 112: +17.2% [+1.5, +29.7] | E5 (call 2): {X02} given {X03, X04}, 28 d to day 112: +18.8% [+2.0, +30.8] |
| 6 | E6 (call 3): {X05, X06, X08, X01} given {X03}, 28 d to day 126: -10.8% [-19.8, -2.9] | E6 (call 3): {X04} given {X02, X03}, 28 d to day 126: +1.7% [-2.3, +6.0] |
| final selection | {X03} | {X02} |

### c2e3: S1, P1, non-null

Useful: X06; stale: X02, X03.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X02, X03, X04}, 28 d to day 84: +1.3% [-8.1, +9.3] | E1 (call 1): {X06}, 28 d to day 84: +33.1% [+18.6, +45.6] |
| 2 | E2 (call 1): {X05, X06, X08}, 28 d to day 84: +34.6% [+21.4, +47.7] | E2 (call 1): {X02, X03, X04}, 28 d to day 84: +1.3% [-8.1, +9.3] |
| 3 | E3 (call 1): {X01, X07}, 28 d to day 84: +2.9% [-7.3, +11.8] | E3 (call 1): {X01, X05, X07, X08} given {X06}, 28 d to day 84: +0.5% [-12.9, +13.2] |
| 4 | E4 (call 2): {X06}, 28 d to day 112: +33.6% [+21.0, +45.2] | E4 (call 2): {X06}, 28 d to day 112: +33.6% [+21.0, +45.2] |
| 5 | E5 (call 2): {X05, X08} given {X06}, 28 d to day 112: -3.4% [-14.0, +6.2] | E5 (call 2): {X02, X03, X04} given {X06}, 28 d to day 112: +0.7% [-5.7, +5.4] |
| 6 | E6 (call 3): {X02, X03, X04} given {X06}, 28 d to day 126: +4.0% [-4.9, +11.9] | E6 (call 3): {X01, X05, X07, X08} given {X06}, 28 d to day 126: +1.8% [-11.2, +13.3] |
| final selection | {X06} | {X06} |

### c3e1: S4, E1, non-null

Useful: X01, X08; stale: none.

| | E1 |
|---|---|
| 1 | E1 (call 1): {X08}, 28 d to day 84: +37.7% [+27.1, +47.8] |
| 2 | E2 (call 1): {X05, X02}, 28 d to day 84: +3.6% [-3.9, +11.8] |
| 3 | E3 (call 1): {X03, X04, X06, X07}, 28 d to day 84: -1.5% [-9.8, +8.3] |
| 4 | E4 (call 2): {X08}, 28 d to day 112: +44.1% [+29.1, +55.8] |
| 5 | E5 (call 2): {X01} given {X08}, 28 d to day 112: +1.1% [-4.8, +6.5] |
| 6 | E6 (call 2): {X05, X02} given {X08}, 28 d to day 112: +0.5% [-3.8, +4.1] |
| final selection | {X08} |

### c3e2: S4, P4, null

Useful: none; stale: X01, X08.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X08, X01, X03}, 28 d to day 84: -2.8% [-11.1, +4.6] | E1 (call 1): {X08}, 28 d to day 84: -2.3% [-11.9, +5.5] |
| 2 | E2 (call 1): {X05, X02, X04}, 28 d to day 84: -6.7% [-21.3, +3.0] | E2 (call 1): {X02, X04, X05}, 28 d to day 84: -6.7% [-21.3, +3.0] |
| 3 | E3 (call 1): {X06, X07}, 28 d to day 84: -4.6% [-17.4, +5.6] | E3 (call 1): {X03, X06, X07}, 28 d to day 84: -2.6% [-15.3, +7.8] |
| 4 | E4 (call 2): {X08, X01, X03}, 28 d to day 112: -3.6% [-14.2, +5.0] | E4 (call 2): {X01, X03, X06, X07}, 28 d to day 112: -6.0% [-17.6, +1.7] |
| 5 | E5 (call 2): {X05, X02, X04}, 28 d to day 112: -4.0% [-21.9, +9.3] | E5 (call 2): {X02, X04, X05, X08}, 28 d to day 112: -5.7% [-23.3, +7.9] |
| 6 | E6 (call 2): {X06, X07}, 28 d to day 112: -2.1% [-8.1, +2.1] | E6 (call 3): {X02, X04, X05}, 28 d to day 126: -2.6% [-24.7, +16.0] |
| final selection | ∅ | ∅ |

### c3e3: S4, P3, non-null

Useful: X05; stale: X01, X08.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X08, X01, X03}, 28 d to day 84: -2.3% [-15.2, +11.2] | E1 (call 1): {X08}, 28 d to day 84: +5.4% [-5.3, +13.7] |
| 2 | E2 (call 1): {X05, X02, X04}, 28 d to day 84: +42.6% [+32.9, +49.0] | E2 (call 1): {X03, X04}, 28 d to day 84: +4.2% [-7.6, +14.2] |
| 3 | E3 (call 1): {X06, X07}, 28 d to day 84: +9.6% [+3.5, +16.6] | E3 (call 1): {X02, X05, X06, X07}, 28 d to day 84: +44.4% [+31.2, +54.2] |
| 4 | E4 (call 2): {X04} given {X02, X05}, 28 d to day 112: -6.3% [-13.2, -2.1] | E4 (call 2): {X06, X07} given {X02, X05}, 28 d to day 112: -7.3% [-15.1, -1.9] |
| 5 | E5 (call 2): {X05} given {X02, X04}, 28 d to day 112: +44.1% [+35.8, +53.8] | E5 (call 2): {X02, X05} given {X06, X07}, 28 d to day 112: +41.7% [+30.2, +53.3] |
| 6 | E6 (call 3): {X02} given {X05}, 28 d to day 126: -4.8% [-11.2, +1.2] | E6 (call 3): {X05} given {X02}, 28 d to day 126: +41.1% [+22.8, +54.5] |
| final selection | {X05} | {X02, X05} |

### c4e1: S3, E1, non-null

Useful: X06; stale: none.

| | E1 |
|---|---|
| 1 | E1 (call 1): {X02, X06, X01}, 28 d to day 84: +42.3% [+28.8, +50.9] |
| 2 | E2 (call 1): {X04, X07, X05}, 28 d to day 84: -4.2% [-21.7, +10.5] |
| 3 | E3 (call 1): {X08, X03}, 28 d to day 84: -5.7% [-16.9, +5.4] |
| 4 | E4 (call 2): {X02}, 28 d to day 112: +1.1% [-8.6, +10.4] |
| 5 | E5 (call 2): {X06, X01} given {X02}, 28 d to day 112: +31.3% [+16.5, +39.7] |
| 6 | E6 (call 3): {X04, X05, X08, X03} given {X06, X01}, 28 d to day 126: +2.5% [-6.9, +10.9] |
| final selection | {X06, X01} |

### c4e2: S3, P1, non-null

Useful: X06; stale: none.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X04}, 28 d to day 84: -6.5% [-24.9, +8.2] | E1 (call 1): {X01, X06}, 28 d to day 84: +34.6% [+20.2, +48.6] |
| 2 | E2 (call 1): {X02, X06, X01}, 28 d to day 84: +30.9% [+12.4, +48.0] | E2 (call 1): {X04, X05, X07}, 28 d to day 84: -2.7% [-23.7, +16.8] |
| 3 | E3 (call 1): {X05, X08, X03}, 28 d to day 84: -0.5% [-15.3, +13.4] | E3 (call 1): {X02, X03, X08} given {X01, X06}, 28 d to day 84: -10.4% [-21.8, +0.3] |
| 4 | E4 (call 2): {X02} given {X06, X01}, 28 d to day 112: -3.6% [-8.6, +1.4] | E4 (call 2): {X01} given {X06}, 28 d to day 112: -0.7% [-6.8, +5.8] |
| 5 | E5 (call 2): {X06} given {X02, X01}, 28 d to day 112: +30.2% [+18.0, +41.7] | E5 (call 2): {X06} given {X01}, 28 d to day 112: +33.2% [+19.3, +45.7] |
| 6 | E6 (call 2): {X01} given {X02, X06}, 28 d to day 112: -1.0% [-5.6, +2.5] | E6 (call 3): {X02, X04, X05, X08} given {X06}, 28 d to day 126: -4.5% [-13.7, +3.3] |
| final selection | {X06} | {X06} |

### c4e3: S3, P2, non-null

Useful: X05; stale: X06.

| | F | K |
|---|---|---|
| 1 | E1 (call 1): {X04, X07, X05}, 28 d to day 84: +27.5% [+13.0, +41.8] | E1 (call 1): {X04, X05, X07}, 28 d to day 84: +27.5% [+13.0, +41.8] |
| 2 | E2 (call 1): {X02, X06, X01}, 28 d to day 84: -7.0% [-16.4, +1.5] | E2 (call 1): {X01, X02, X06}, 28 d to day 84: -7.0% [-16.4, +1.5] |
| 3 | E3 (call 1): {X08, X03}, 28 d to day 84: -9.7% [-19.5, +0.0] | E3 (call 1): {X03, X08}, 28 d to day 84: -9.7% [-19.5, +0.0] |
| 4 | E4 (call 2): {X04}, 28 d to day 112: -4.6% [-13.7, +4.5] | E4 (call 2): {X04} given {X05}, 28 d to day 112: -6.7% [-14.5, -0.1] |
| 5 | E5 (call 2): {X05, X07} given {X04}, 28 d to day 112: +27.2% [+11.8, +39.9] | E5 (call 2): {X05} given {X04}, 28 d to day 112: +30.2% [+18.3, +41.5] |
| 6 | E6 (call 3): {X02, X06, X08, X03} given {X05, X07}, 28 d to day 126: -4.5% [-17.1, +6.2] | E6 (call 3): {X07} given {X05}, 28 d to day 126: -5.4% [-12.5, +1.6] |
| final selection | {X05, X07} | {X05} |


## 8. Referee-approved findings

These are approved positive findings at the granularity tested. Each gives the configuration and the holdout
confirmation of that configuration as tested (days 127–154, 28-day window). The headline is the narrowest approved
finding: fewest covariates, then the highest governing lower bound, then the earliest experiment.
| episode | condition | approved positive findings (configuration as tested: granularity, holdout confirmation) | headline |
|---|---|---|---|
| c1e1 | E1 | {X02, X03, X07} (set (attribution unresolved)): +26.3% [+12.2, +35.4]; {X02} given {X03, X07} (conditional on X03, X07): +24.4% [+9.1, +32.9] | {X02} given {X03, X07} |
| c1e2 | F | {X05, X08} (set (attribution unresolved)): +17.2% [-5.3, +33.3]; {X01, X04} (set (attribution unresolved)): +0.2% [-10.2, +15.5] | {X05, X08} |
| c1e2 | K | {X05, X06, X08} (set (attribution unresolved)): +30.9% [+16.9, +41.8]; {X01, X04} (set (attribution unresolved)): +0.2% [-10.2, +15.5] | {X01, X04} |
| c1e3 | F | none | none |
| c1e3 | K | none | none |
| c2e1 | E1 | {X05, X06, X08} (set (attribution unresolved)): +34.8% [+21.3, +46.2]; {X06} given {X05, X08} (conditional on X05, X08): +32.8% [+16.5, +45.3] | {X06} given {X05, X08} |
| c2e2 | F | {X02, X03, X04} (set (attribution unresolved)): +28.4% [+17.1, +36.0]; {X03} (individual): +19.3% [+5.9, +32.5]; {X02, X04} given {X03} (set (attribution unresolved) given X03): +11.3% [-8.1, +23.4] | {X03} |
| c2e2 | K | {X02, X03, X04} (set (attribution unresolved)): +28.4% [+17.1, +36.0]; {X02} given {X03, X04} (conditional on X03, X04): +8.9% [-7.2, +21.4] | {X02} given {X03, X04} |
| c2e3 | F | {X05, X06, X08} (set (attribution unresolved)): +33.4% [+23.2, +41.4]; {X06} (individual): +31.3% [+21.6, +39.3] | {X06} |
| c2e3 | K | {X06} (individual): +31.3% [+21.6, +39.3] | {X06} |
| c3e1 | E1 | {X08} (individual): +30.0% [+15.9, +40.3] | {X08} |
| c3e2 | F | none | none |
| c3e2 | K | none | none |
| c3e3 | F | {X02, X04, X05} (set (attribution unresolved)): +28.9% [+14.5, +41.3]; {X06, X07} (set (attribution unresolved)): -6.8% [-12.1, -3.4]; {X05} given {X02, X04} (conditional on X02, X04): +32.2% [+16.0, +45.5] | {X05} given {X02, X04} |
| c3e3 | K | {X02, X05, X06, X07} (set (attribution unresolved)): +28.3% [+12.9, +40.4]; {X02, X05} given {X06, X07} (set (attribution unresolved) given X06, X07): +32.8% [+19.1, +44.3]; {X05} given {X02} (conditional on X02): +34.8% [+21.1, +46.6] | {X05} given {X02} |
| c4e1 | E1 | {X01, X02, X06} (set (attribution unresolved)): +21.8% [+2.7, +33.9]; {X01, X06} given {X02} (set (attribution unresolved) given X02): +28.5% [+8.4, +41.1] | {X01, X06} given {X02} |
| c4e2 | F | {X01, X02, X06} (set (attribution unresolved)): +23.1% [+7.6, +35.1]; {X06} given {X01, X02} (conditional on X01, X02): +29.4% [+16.2, +40.6] | {X06} given {X01, X02} |
| c4e2 | K | {X01, X06} (set (attribution unresolved)): +18.6% [+1.5, +31.8]; {X06} given {X01} (conditional on X01): +23.6% [+9.9, +36.3] | {X06} given {X01} |
| c4e3 | F | {X04, X05, X07} (set (attribution unresolved)): +19.4% [+7.1, +30.9]; {X05, X07} given {X04} (set (attribution unresolved) given X04): +22.0% [+13.1, +30.7] | {X05, X07} given {X04} |
| c4e3 | K | {X04, X05, X07} (set (attribution unresolved)): +19.4% [+7.1, +30.9]; {X05} given {X04} (conditional on X04): +25.1% [+15.7, +34.5] | {X05} given {X04} |


## 9. Strong, partial and null success

**Results by episode:**
- **Partial success:** none in either condition.
- **Null success:** both null episodes, c1e3 and c3e2, succeeded for K and for F. There was no approved positive, the
  final selection was empty and no candidate was accepted.
- **Strong success:** K had it in 4 of 6 non-null episodes, F in 5 of 6.
- **Incorrect approvals:** neither condition made an individual or conditional approval of a pure-noise or stale
  candidate in any episode.

**Why K failed twice:**
- **c1e2 (P3, reopened negative).** K's own conclusion and final selection were exactly right.
  - **K's result:** it selected {X05, X06}, the two temperature forecasts that are this period's useful pair, and the
    selection confirmed at +30.5% [+15.3, +42.0]. Its approved set {X05, X06, X08} confirmed at +30.9%.
  - **The headline:** the referee also approved the set {X01, X04} from E3 (days 57–84: +14.4% [+5.7, +24.0]), a
    research-window false positive. On holdout it scored +0.2% [−10.2, +15.5]. It has fewer covariates, so the frozen
    headline rule picked it, and criteria 3 and 4 failed.
  - **K's own counter-evidence:** K's E4 showed {X01, X04} adds nothing given {X05, X06} (−0.6%). By design the referee
    does not use a different configuration to eliminate an approved set.
  - **F:** F had the same false-positive E3. Its headline was {X05, X08}, which was not confirmed (lower bound −5.3%).
- **c2e2 (P2, stale positive).** K dropped the stale footfall source (X06 "deteriorated") and found the promotions
  family.
  - **K's headline:** "X02 given X03, X04" (days 85–112: +18.8% [+2.0, +30.8]).
  - **On holdout:** +8.9% [−7.2, +21.4], so criterion 4 failed. X02 and X03 are two measurements of one quantity, so
    the increment of one over the other is small.
  - **K's selection:** {X02} alone confirmed at +34.5% [+24.3, +42.4].
  - **F:** F tested X03 alone, got an individual approval and confirmed it at +19.3% [+5.9, +32.5]. That was strong
    success.

**Pattern criteria (the owner's "appropriate use of accumulated knowledge"):**

| pattern | episodes | K result | requirement |
|---|---|---|---|
| P1 recurrence | c2e3, c4e2 | strong, strong | strong |
| P2 stale positive | c2e2, c4e3 | not strong, strong; stale source approved in neither | strong, stale not approved |
| P3 reopened negative | c1e2, c3e3 | not strong, strong | strong |
| P4 null | c1e3, c3e2 | null success, null success | null success |

## 10. K against F: wins, losses and ties (secondary diagnostic, never gating)

**Discovery index:** the cumulative number of experiments up to the first call whose referee report meets strong
criteria 1–4 ("–" if never). "Strong" means strong success.
| episode | pattern | K | F | K discovery index | F discovery index | pair |
|---|---|---|---|---|---|---|
| c1e2 | P3 | not strong: 3_headline_contains_useful_candidate, 4_headline_confirmation_lower_bound_above_0 | not strong: 4_headline_confirmation_lower_bound_above_0 | – | – | TIE |
| c1e3 | P4 | null success | null success | – | – | TIE |
| c2e2 | P2 | not strong: 4_headline_confirmation_lower_bound_above_0 | strong | – | 5 | F WIN |
| c2e3 | P1 | strong | strong | 3 | 5 | K WIN |
| c3e2 | P4 | null success | null success | – | – | TIE |
| c3e3 | P3 | strong | strong | 5 | 5 | TIE |
| c4e2 | P1 | strong | strong | 3 | 6 | K WIN |
| c4e3 | P2 | strong | strong | 5 | 5 | TIE |


- **Outcome:** K WIN 2, F WIN 1, TIE 5. The two null pairs are TIE by rule.
- **Earlier discoveries:** both K WINs.
  - c2e3: K used 3 experiments to F's 5. K's first experiment was footfall X06 alone, the source its memory held as
    confirmed under the same store format.
  - c4e2: 3 to F's 6. K first tested {X01, X06}, the set its memory held as confirmed with attribution unresolved,
    and then separated it.
  - In the other two episodes where both were strong (c3e3, c4e3) the indices were equal (5 and 5).
- **The F WIN:** c2e2. F's individual test of X03 confirmed; K's conditional headline did not (section 9).
- **Experiments saved:** 0. Every trajectory used all 6 experiments, and the policy has no rule to stop early.
- **Validated findings:** equal. K and F each produced 10 approved findings that confirmed on holdout (section 12).

## 11. Where memory helped, hurt or was ignored

Descriptive, from K's own notes, reasons and conclusions (M ids quoted from its texts) against F's record of the same
period. F never mentions an M id. K's structured "cites" can only hold experiment ids: the three repairs were K
listing M ids there in its first call.

| period | pattern | how memory changed K's design | effect | outcome |
|---|---|---|---|---|
| c1e2 | P3 reopened | K reopened the old weather nulls ("Those nulls are dated to the old regime") and put X06 in its weather screen; F held X06 back and never tested it. After the first null test of the stale community set, K wrote "the M2/M4 positive appears to have decayed". | helped (K's selection {X05, X06} was the useful pair and confirmed); not credited by the headline rule | TIE, neither strong |
| c1e3 | P4 null | first round identical to F's; memory only set expectations ("Its North usefulness (M4) does not carry over") | ignored for design; stale positives dropped | TIE, both null success |
| c2e2 | P2 stale | same sets as F; memory reversed K's expectations (the stale footfall set "improves", the promotions null "is dated"); K dropped the stale positive after one test ("the regime-A positives M2 and M4 have not carried over") | neutral; the failure came from K's conditional-only attribution of a measurement pair, not from memory | F WIN |
| c2e3 | P1 recurrence | K's first experiment was footfall X06 alone ("Checks whether the mix-A favourite X06 (M4) still adds skill"); F group-screened first | **helped: strong after 3 experiments vs F's 5** | K WIN |
| c3e2 | P4 null | K tested its old favourite X08 alone first, deferred X01 ("Added nothing beyond X08 in Role 1 (memory M4)"), reopened the transport nulls; it dropped X08 after one test ("The Role 1 favourite (M1) has lost its signal") | neutral | TIE, both null success |
| c3e3 | P3 reopened | first experiment on the stale X08 alone; dismissed sources reopened as a 4-wide set "so that no option is left unexamined after the change" (+44.4%) | neutral: the reopening worked, no faster than F (index 5 each); X01 left untested, harmless (stale) | TIE, both strong |
| c4e2 | P1 recurrence | K's first experiment was the remembered pair {X01, X06} ("Retest whether the period-1 wind+solar signal (M1, M5) still holds"), then it resolved the unresolved attribution ("wind X01 is redundant given X06") | **helped: strong after 3 experiments vs F's 6** | K WIN |
| c4e3 | P2 stale | same sets as F; memory set the expectations ("Checks whether the old favourite weather set (M1, M5, M11) still helps"); K dropped the stale solar signal after one test ("the mix-1 solar signal (M11) has decayed") | neutral | TIE, both strong |

Across the eight periods:
- **Helped:** the two recurrence periods (earlier discovery, the two K WINs); c1e2's reopening of X06, which F never
  tested.
- **Stale positives:** seven of the eight periods had one (all but c4e2). In each, K's first test of the stale prior came out null and K recorded
  that it no longer carried over. K never approved or selected a stale source.
- **Hurt:** in no period did memory make K skip a now-useful source. Its costs were small: a round-1 slot on a stale
  favourite (c3e2, c3e3), expectations pointing the wrong way (c1e2, c2e2, c3e3, c4e3) that never stopped a test, and
  the three first-call repairs.
- **Ignored for design:** c1e3, c2e2 and c4e3 had first rounds identical to F's.
- **Stable negatives:** never used to skip a test. K re-screened every source in every period, as the frozen lesson
  asks.
- **K's two non-successes** (c1e2, c2e2) came from its attribution design and the frozen headline rule, not from
  memory. In both, K's own final selection held the oracle source and confirmed.

## 12. Cheap-trial economics

Each experiment is a t0-beta comparison of a covariate set against a reference set over a 7- to 28-day window: no model
is fitted. Per research trajectory (6 experiments, 4 calls), from the records:

| condition | records | experiments | t0-beta forecasts | loop wall time (min) | API attempts | repairs | tokens | approved positives | validated (confirmation lower bound > 0) | validated per experiment | validated per loop-minute |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 4 | 24 | 938 | 6.50 | 16 | 0 | 126,908 | 7 | 7 | 0.29 | 1.08 |
| F | 8 | 48 | 1,918 | 12.28 | 32 | 0 | 251,745 | 14 | 10 | 0.21 | 0.81 |
| K | 8 | 48 | 1,890 | 13.45 | 35 | 3 | 332,729 | 12 | 10 | 0.21 | 0.74 |
| all | 20 | 120 | 4,746 | 32.23 | 83 | 3 | 711,382 | 33 | 27 | 0.23 | 0.84 |

- **A trial is cheap:** about 40 t0-beta forecast-days per experiment. A whole six-experiment investigation took 73–113
  s of loop time and 2.2–2.9 runner-minutes per research job.
- **Memory costs input tokens:** K used 332,729 tokens against F's 251,745 (+32%) for the same 48 experiments and the
  same number of validated findings. The memory block adds 2–6 kB to every call.
  - K also had the only 3 repairs, all in call 1 of a period-2 K job (c1e2, c3e2 and c4e2), all for the same reason.
    The researcher listed memory entry ids (M1, M2, …) as "cites" on its beliefs, a field the unchanged L8 check
    reserves for ids of experiments already run. The one repair turn fixed each call, so every call was valid.
  - There were no refusals.
- **K saved no experiments:** every trajectory of every condition used all 6.
- **Non-null periods only:** K and F each validated 10 findings in 36 experiments (0.28 per experiment). Per validated
  finding, K used 33,273 tokens and F 25,175.
- **Memory has its own overhead:** the two referee jobs that build K's memory used 728 t0-beta forecasts for holdout
  confirmations and 3.5 runner-minutes.

## 13. Total cost

| item | preflight (run 37329939712) | scored run (run 37332048132) |
|---|---|---|
| research trajectories | 5 (company c1 only) | 20 |
| researcher tokens | 183,103 | 711,382 |
| API attempts | 21 | 83 |
| refusals / repairs | 0 / 1 | 0 / 3 |
| t0-beta forecasts on the research path | – | 4,746 |
| runner minutes (all jobs) | 16.4 | 78.3 (evaluate 21.9) |
| wall time | 14.1 min | 37.0 min |

- **Preflight tokens:** per job, from its `REPORT.md`: 32,441, 30,720, 37,891, 31,355 and 50,696.
- **Runner minutes and wall times:** from the Actions jobs API.
- **Totals:** scored run plus preflight, 894,485 researcher tokens and 94.7 runner-minutes.
- **Evaluator forecasts on top of the research path:** for the scored run, 4,746 recompute, 9,800 poison-test and
  1,820 informativeness forecasts, plus the referee's 728 confirmations.
- **Not derivable:** the dollar cost (the records identify the model only by hash and hold no prices) and thinking
  tokens separately from visible output.
- **Not counted above:** engineering review (the focused pre-run check and the post-run verification of this
  document) used separate agent tokens. They are not part of the kernel's cost.

## 14. The frozen programme reading

The rows of spec section 10, checked in order:
1. **INFRASTRUCTURE FAILURE: does not apply.**
   - No material integrity issue: no canary, guard failure, poison mismatch, recompute or rebuild failure.
   - Instrument and model as pinned.
   - K/F memory separation intact. Memory recomputation was identical.
   - 0 missing scored trajectories.
2. **BENCHMARK FAILURE: does not apply.**
   - 6 of 6 non-null scored episodes were informative.
   - No generator defect.
   - Memory recomputed without truth.
3. **FULL KERNEL PROVEN FOR THIS BENCHMARK: applies.**

   | condition | required | observed | holds |
   |---|---|---|---|
   | K episode successes | ≥ 6 of 8 | 6 of 8 | yes, at the threshold |
   | K null successes | 2 of 2 | 2 of 2 | yes |
   | K episodes with an incorrect individual or conditional approval | ≤ 1 | 0 | yes |
   | median K oracle-fraction analogue | ≥ 0.75 | 1.000 over 6 | yes |

**Closing line:** `MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST`

## What this result does and does not show

**Shown, on this frozen benchmark:**
- The full loop reached a scientifically supported conclusion in 6 of 8 later investigations.
  - Context in the prompt, an unrepaired L8 researcher, cheap t0-beta trials, a deterministic referee and the
    referee's own memory together made up the loop.
  - "Supported" means a confirmed narrow headline, or a correct null.
- It handled both null periods, both recurrences, one stale positive and one reopened negative under the frozen rules.
- It made no incorrect individual or conditional approval.

**Accumulated knowledge was used:**
- K cited memory entries in every period.
- It found recurring sources faster (3 against 5 and 6 experiments).
- It abandoned stale positives after one null test.

**Accumulated knowledge did not make later research better in outcome:**
- F, with the same context and no memory, was strong as often or more often: 5 of 6 against 4 of 6.
- Both produced 10 validated findings.
- K saved no experiments and used 32% more tokens.

This is the secondary diagnostic the owner made non-gating.

**Not shown:**
- Real-market performance, commercial value or causal identification.
- Robustness beyond one trajectory per condition and period.
- Robustness beyond four companies from one generator family.
- The margin is zero: one more failed period reads FULL KERNEL NOT PROVEN.
- Both failures are headline-attribution failures in which K's own final selection was right. That makes the referee's
  headline rule (the narrowest approved finding) as consequential as the researcher.

## Verification

After the run, a read-only workflow re-checked the published record without changing anything. It had five verifiers,
and every discrepancy they raised went to an adversarial skeptic:
- **Reading:** an independent scorer, written from the spec text without importing the frozen rules, reproduced every
  status, headline, criterion, oracle fraction and row of the reading.
- **Referee:** an independent re-implementation from the spec reproduced all 108 configurations, the 8 memories, the
  discovery indices and the 8 pair outcomes.
- **Integrity:** an integrity and isolation audit, including regeneration of all 12 worlds and contexts and a truth
  scan.
- **Memory use:** the memory-use reading in section 11.
- **Economics:** an economics recomputation.

All five agreed with `evaluation.json`. The skeptics refuted all five discrepancies raised as immaterial:
- memory confirmation numbers differing from evaluate's by about 1e-8;
- the label "empty selection";
- the unlisted publish stub `README.md`;
- the canary scan counting the job manifest;
- the word "Role" in c3's regime descriptor.
