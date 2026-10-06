# Discovery1: results and dispatch log

*Owner instruction: [`NEXT_DISCOVERY_MILESTONE_PROMPT.md`](NEXT_DISCOVERY_MILESTONE_PROMPT.md). Frozen spec:
[`DISCOVERY1_SPEC.md`](DISCOVERY1_SPEC.md). Every dispatch of `.github/workflows/research-loop-discovery1.yml` is listed
here. The published records are on branches `discovery1/run-<id>` (manifest-checked). Phase 0, beta1, learn1 and policy1
results are unchanged.*

**Reading: NO DISCOVERY SIGNAL** (frozen programme reading, row 5).
- All three worlds were informative: the emerging driver E was clearly detectable after the change.
- L8 (learn1's lesson-only researcher, adapted only to enumerate X01–X08) succeeded in **0 of 3** under the six
  conservative criteria. The fixed comparator succeeded in **1 of 3** (w1).
- **L8's final selection was right in two worlds, but its own evidence for it fell short of criterion 5 in both:**
  - **w1:** it selected E and its proxy D;
  - **w3:** it selected E alone.

  In neither world did it test E alone, and it never tested its final set against no covariate.
- **w2:** L8 never re-tested E after the change and selected D with three noise candidates.

Three worlds, one trajectory each: a small batch, not a rate.

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37238368870](https://github.com/xuanhuyle/solar/actions/runs/37238368870) | preflight | `56ee1c3` | **PASS**: 4 of 4 L8 calls valid, 0 refusals, 0 repairs, 6 legal experiments over X01–X08, every prompt rebuilt, comparator followed its rule |
| 2 | [37238629496](https://github.com/xuanhuyle/solar/actions/runs/37238629496) | run (scored, three worlds) | `56ee1c3` | **NO DISCOVERY SIGNAL** (integrity clean) |

**Sequence:**
1. **Freeze** (`cdc8584`).
2. **One focused pre-run check** (a single agent, five items; [spec section 7](DISCOVERY1_SPEC.md)).
   - It found one evaluator defect: an L8 selection of more than 4 candidates would have stopped the evaluation.
   - The defect was corrected and re-pinned (`56ee1c3`, `discovery1_spec_sha` `3a3801bb…`) before any preflight or
     scored world existed.
3. **Preflight.**
4. **The one scored run**, under the same hash. No reroll; no change between worlds.

The preflight was operational only. Its trajectory was not read for science, and nothing was tuned on it.

## 1. Integrity (scored run 37238629496)

All three worlds were clean:
- **Data:** the observed data's hash regenerated equal to the shipped and declared hashes.
- **L8:** its system text equalled the frozen text (`system_sha256` as expected), and every user prompt rebuilt byte
  for byte from its own world's record. All 6 of its experiments per world recomputed equal from that world's data.
- **Comparator:** its 6 experiments and its selection recomputed equal.
- **Checks:** no canary of any world in any record; the model hash matched; the guard confirmed the truth absent; every
  job succeeded.
- **API:** no refusals, no repairs, every call valid.

The frozen lesson was unchanged (sha256 `1c38b101…`).

## 2. The worlds (revealed after the run)

| world | first changed day | R | E | D | noise N1–N5 | E alone, days 99–112 | E alone, days 99–126 | informative |
|---|---|---|---|---|---|---|---|---|
| w1 | 89 | X01 | X05 | X06 | X08, X07, X04, X02, X03 | +46.6% [+34.9, +55.6] | +49.3% [+40.1, +57.9] | yes |
| w2 | 92 | X05 | X08 | X02 | X01, X06, X07, X03, X04 | +13.9% [+3.2, +25.3] | +23.4% [+10.8, +34.8] | yes |
| w3 | 91 | X02 | X01 | X06 | X05, X07, X03, X08, X04 | +35.1% [+16.0, +45.8] | +36.3% [+20.4, +48.3] | yes |

Detectability is t0-beta with E alone against no covariate, on the observed days. With 3 informative worlds, BENCHMARK
FAILURE does not apply.

## 3. Per world: L8 and the comparator

### w1: L8 found E and its proxy, but its only test of that pair was conditional

**L8's path:**
1. **Round 1:** screened X01–X04 (+46.5%; R's group, before the change) and X05–X08 (−2.0%).
2. **Round 2:**
   - split R's group into pairs on days 85–112 (+6.3% and +3.9%, both null);
   - re-screened the dismissed X05–X08 on the same days: +26.0% [+9.2, +43.5], weekly −5, +39, +44, +40%;
   - its next notes: "The earlier E2 null is therefore outdated", the change "started around day 92".
3. **Round 3, last experiment:** X05, X06 (E, D) given X07, X08 (two noise candidates): +42.7% [+31.1, +52.4].
4. **Final:** it marked R's group deteriorated and selected **{X05 (E), X06 (D)}**, calling it "a set-level acceptance:
   the two were never separated from each other".

| | L8 | comparator |
|---|---|---|
| first experiment E entered | E2 (round 1, in a group of 4) | C2 (round 1, in a group of 4) |
| E tested after the change | yes (E5, group of 4) | yes (C4, group of 4) |
| E distinguished from its companions | no | no |
| R removed / noise selected | removed / none | removed / none |
| D | selected; D given E on confirmation −0.7% [−5.6, +4.4] (no incremental value) | selected (same) |
| final selection | {E, D} | {E, D} |
| criterion 5 (own supporting evidence) | **no**: the test of exactly {E, D} had a reference of two noise candidates | **yes**: C5, {E, D} against none, +45.7% [+34.6, +54.5] |
| final selection on confirmation (t0-beta) | +31.9% [+12.9, +48.3] | +31.9% [+12.9, +48.3] |
| success | **no** (criterion 5) | **yes** |

### w2: L8 spent its budget on the decaying group and never re-tested E after the change

**L8's path:**
1. **Round 1:** screened three groups: {X01, X02, X03} +1.3%; {X04, X05, X06} +36.2% (R's group); {X07, X08} +5.2%
   (E's group, before the change). It rejected both null groups, E included.
2. **Round 2:** spent two experiments on single members of R's group, X04 (+6.0%) and X05 (R, +16.0%). Its notes saw R
   decay after about day 91.
3. **Round 3, last experiment:** re-screened four dismissed candidates, X01, X02, X03, X07, on days 99–126: +13.2%
   [−4.8, +27.2]. With only four slots it left E out, writing "X08 stays unexamined post-change".
4. **Final:** it selected that set, **{X01 (N1), X02 (D), X03 (N4), X07 (N3)}**, "suggestive, not conclusive".

| | L8 | comparator |
|---|---|---|
| E tested after the change | **no** (E only in round 1, in a pair) | yes (C4, group of 4) |
| E distinguished | no | no |
| R removed / noise selected | removed / **N1, N4, N3** | removed / **N3** |
| D | selected; D alone +30.6% on confirmation, D given E −7.8% [−19.4, +1.9] | not selected |
| final selection | {N1, D, N4, N3} | {N3, E} (pair C6, +19.4% [+2.4, +32.7]) |
| final selection on confirmation (t0-beta) | +27.3% [+14.8, +37.5] (carried by the proxy) | +34.5% [+18.0, +47.2] |
| success | no (criteria 2, 3, 4, 5) | no (criterion 4: noise partner) |

### w3: L8 selected E alone, but inferred it from a pair without ever testing E alone

**L8's path:**
1. **Round 1:** screened X01–X04 (+19.8%, holding E and R) and X05–X08 (−7.8%).
2. **Round 2:**
   - split the first group into pairs: {X01 (E), X02 (R)} +23.2% [+2.3, +37.1] on days 85–112, and {X03, X04} null;
   - re-screened X05–X08: +4.7%, null.
3. **Round 3, last experiment:** X02 (R) given X01 (E) on days 99–126: −3.9% [−8.5, +0.8], so R adds nothing beyond E.
4. **Final:** it selected **{X01 (E)}**, noting "X01 was never scored alone against no covariates in the same window,
   so its individual value is inferred from E3 and E6 together".

| | L8 | comparator |
|---|---|---|
| E tested after the change | yes (E3, pair with R) | yes (C3, group of 4) |
| E distinguished | no (attributed by elimination of R) | no |
| R removed / noise selected | removed (marked redundant given E) / none | **R selected** / none |
| D | rejected (only ever in a group of 4) | not selected |
| final selection | {E} | {E, R} (pair C5, +33.8% [+18.7, +46.7]) |
| criterion 5 (own supporting evidence) | **no**: no experiment with E as the only covariate or {E} alone | yes (C5) |
| final selection on confirmation (t0-beta) | +29.3% [+17.4, +39.7] | +28.1% [+15.1, +39.1] |
| success | **no** (criterion 5) | no (criterion 4: R selected) |

### Summary of the six criteria

| world | L8: 1 2 3 4 5 6 | L8 success | comparator: 1 2 3 4 5 6 | comparator success |
|---|---|---|---|---|
| w1 | Y Y Y Y n Y | no | Y Y Y Y Y Y | **yes** |
| w2 | Y n n n n Y | no | Y Y Y n Y Y | no |
| w3 | Y Y Y Y n Y | no | Y Y Y n Y Y | no |

## 4. What the result does and does not depend on (reported, not a reinterpretation)

The reading is the frozen one. Criterion 5 is predeclared as: a round 2–3 experiment with a lower bound above 0 that
has either E as its only covariate (any reference), or exactly the final selection as covariates and no reference.
Both of L8's near-misses fail only on that definition:

| world | what L8's own evidence was | under the frozen criterion 5 |
|---|---|---|
| w1 | exactly its final set {E, D}, tested against a reference of two noise candidates (+42.7%, lower bound +31.1%) | fails: the set test had a reference |
| w3 | {E, R} positive (lower bound +2.3%, on days that straddle the change), then R given E null; E never tested alone | fails: E's value only inferred |

**Sensitivity to looser readings of criterion 5:**
- **Accepting a conditional test of the set:** w1 becomes a success. L8 then succeeds in 1 of 3, ties the comparator
  at 1, and fails in 2 of 3: still NO DISCOVERY SIGNAL (row 5).
- **Also accepting attribution by elimination:** w3 becomes a success too. L8 would then succeed in 2 of 3 against the
  comparator's 1, which is the DISCOVERY SIGNAL row.

The conservative definition was frozen before any world existed, as the owner asked ("define a successful discovery
conservatively"; "do not reinterpret these labels"). The frozen reading stands. The sensitivity is reported so the owner
can see exactly where the boundary lies.

**What L8 did across the three worlds:**
- **In all three:** it screened all eight candidates in groups in round 1, and re-opened earlier group-level
  rejections on post-change data.
- **In w1 and w2:** it saw the old relationship deteriorate. In w3, R shared a pair with E, and it removed R as
  redundant given E.
- **In w1 and w3:** it narrowed to E.
- **Never:** it spent no experiment on E alone in any world.
- **Its final set against no covariate:** never tested in w1 or w3. In w2 it was tested, and the lower bound was not
  above 0.

In w1 and w3 it recorded these gaps itself in its conclusions, and selected anyway. The frozen lesson was never cited by
name (0 mentions in all three worlds).

## 5. Confirmation (days 127–154; t0-beta, ridge for context only)

| comparison | w1 t0-beta | w2 t0-beta | w3 t0-beta |
|---|---|---|---|
| {E} vs {} | +32.3% [+11.2, +49.0] | +36.9% [+21.8, +48.6] | +29.3% [+17.4, +39.7] |
| {R} vs {} | −2.1% [−8.4, +5.3] | −5.2% [−17.5, +4.7] | −12.2% [−25.1, −0.4] |
| {D} vs {} | +18.5% [+5.3, +31.9] | +30.6% [+16.1, +42.0] | −1.1% [−17.6, +12.6] |
| {E, D} vs {} | +31.9% [+12.9, +48.3] | +32.0% [+14.7, +44.8] | +25.9% [+9.2, +38.1] |
| D given E | −0.7% [−5.6, +4.4] | −7.8% [−19.4, +1.9] | −4.8% [−14.8, +2.2] |
| E given D | +16.4% [+0.8, +30.7] | +2.0% [−5.9, +8.8] | +26.7% [+10.9, +41.1] |
| R given E | −3.6% [−10.4, +1.9] | +1.5% [−5.8, +7.4] | −1.7% [−7.3, +3.3] |
| L8's selection vs {} | +31.9% [+12.9, +48.3] | +27.3% [+14.8, +37.5] | +29.3% [+17.4, +39.7] |
| comparator's selection vs {} | +31.9% [+12.9, +48.3] | +34.5% [+18.0, +47.2] | +28.1% [+15.1, +39.1] |

- Every final selection beat no covariate (criterion 6 held for both searchers in all three worlds).
- D added nothing given E in any world.
- The ridge rows (in `REPORT.md` on the run branch) agree in direction. They are context only.
- Forecast accuracy alone is not discovery: L8's w2 selection gained +27.3% through the proxy while holding three noise
  candidates.

## 6. Cost

| | L8 tokens | API attempts | t0-beta forecasts |
|---|---|---|---|
| preflight (1 world) | 26,828 | 4 (0 refusals, 0 repairs) | 476 (L8 238, comparator 238) |
| w1 | 28,445 | 4 | 980 (L8 238, comparator 238, evaluate 504) |
| w2 | 30,346 | 4 | 1,134 (238, 238, 658) |
| w3 | 29,372 | 4 | 938 (238, 238, 462) |
| **total** | **114,991** | **16** | **3,528** |

- **Scored-run tokens:** input 22,949, output 25,206, cache reads 40,008.
- **Experiments:** each searcher used 6 per world.
- **Runner time:** about 3 minutes for the preflight and 13 for the scored run (the three world jobs ran in parallel,
  about 3.3 minutes each; evaluate 3 minutes). Wall time was about 10 minutes in all.

## 7. Reading

| # | Row | Holds? |
|---|---|---|
| 1 | INFRASTRUCTURE FAILURE | no: integrity clean, every call valid |
| 2 | BENCHMARK FAILURE | no: 3 informative worlds |
| 3 | DISCOVERY SIGNAL | no: L8 succeeded in 0 |
| 4 | BOTH SUCCEED | no |
| 5 | **NO DISCOVERY SIGNAL** | **yes: L8 failed in all 3 informative worlds** |

Predeclared closing line: **NARROW TO HUMAN-SUPPLIED HYPOTHESES**.
