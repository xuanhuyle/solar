# beta1 hidden-world result: RESEARCHER FEASIBILITY FAILED

Verdict map row 2: E was detectable on days 99-126 but never tested in rounds 2-3 and not selected.

- One world is an existence check, not a rate; nothing here establishes superiority over the script.
- Even an ideal researcher completes the whole chain only when both R's and E's evidence is present in this world; the evidence check reports whether it was.

beta1_spec_sha `9b6ea2ae24a07eb0532e18644663c0f94fc47666063b0efd8c11e61ff21d14b3`; run 37201189113; commit 088869550e325a525edb60fb72aea0e28ee39e45; instrument theforecastingcompany/t0-beta @ c8885416fab935d604749a90cdcbf9b54fffcaeb (tfc-t0 0.5.0).

## Research trajectory (round by round)

### Call 1 (round 1, days 1-84)

API attempts: #1 end_turn, 9.049 s

Notes: Round 1 (days 1-84). No evidence yet. Plan: screen candidates one at a time against a no-covariate reference over 28 days (4 weekly parts, which shows any drift). X01-X03 now, X04 and follow-ups in round 2, and a recent-window recheck in round 3 because the process may be non-stationary.

Beliefs:
- X01 (D): **untested**; cites none; No experiment yet; screened alone in this round.
- X02 (E): **untested**; cites none; No experiment yet; screened alone in this round.
- X03 (R): **untested**; cites none; No experiment yet; screened alone in this round.
- X04 (N): **untested**; cites none; No experiment yet; planned for round 2 because of the per-round limit.
Experiments:
- E1: covariates ['X01'], reference [], 28 days, expected no_change (Individual screen of X01 against the target-only forecast. A 28-day window gives a usable interval, and its weekly parts reveal drift. No prior, so I expect no change.) -> -3.9% [-12.4, +5.5] on days 57-84
- E2: covariates ['X02'], reference [], 28 days, expected no_change (Individual screen of X02 under the same design, so its effect can be separated from the others.) -> -5.5% [-13.9, +3.2] on days 57-84
- E3: covariates ['X03'], reference [], 28 days, expected no_change (Individual screen of X03 under the same design. X04 follows next round.) -> +17.8% [+9.8, +26.6] on days 57-84

### Call 2 (round 2, days 1-112)

API attempts: #1 end_turn, 12.399 s

Notes: Round 1 (days 57-84 scored): X01 (E1, -3.9%) and X02 (E2, -5.5%) gave no help. Both intervals straddle zero and lean negative. X03 (E3) gave +17.8% [+9.8, +26.6], winning 18 of 28 days. Its weekly skill fell from +31.8% to +10.0%, so a decay is possible. Round 2 plan: screen X04 alone on days 85-112. Recheck X03 alone on days 85-112, which do not overlap E3, to test for drift. Keep 1 experiment for round 3 to confirm the chosen set on the latest days.

Beliefs:
- X01 (D): **rejected**; cites E1; Skill -3.9% [-12.4, +5.5], 14 days won and 14 lost, weekly parts mostly negative. No evidence it helps, and it may add noise.
- X02 (E): **rejected**; cites E2; Skill -5.5% [-13.9, +3.2], 13 days won and 15 lost, weekly parts mostly negative. No evidence it helps.
- X03 (R): **promising**; cites E3; Skill +17.8% with an interval excluding zero, positive in all 4 weeks. The weekly trend is declining (+31.8% down to +10.0%), so a recheck on newer data is needed before accepting it.
- X04 (N): **untested**; cites none; Not yet screened because of the per-round limit. Screened alone in this round.
Experiments:
- E4: covariates ['X04'], reference [], 28 days, expected no_change (Individual screen of X04 against the target-only forecast on days 85-112, the same design as E1-E3. No prior, so I expect no change.) -> -0.1% [-7.4, +6.4] on days 85-112
- E5: covariates ['X03'], reference [], 28 days, expected improves (E3 showed X03 helps (+17.8%) but its weekly skill declined. Rechecking on the non-overlapping days 85-112 tests whether the effect persists or has deteriorated.) -> +2.8% [-4.8, +10.7] on days 85-112

### Call 3 (round 3, days 1-126)

API attempts: #1 end_turn, 13.299 s

Notes: Days 57-84: X01 (E1, -3.9%) and X02 (E2, -5.5%) did not help. X03 (E3) helped, +17.8% [+9.8, +26.6], but its weekly skill fell from +31.8% to +10.0%. Days 85-112: X04 (E4) had no effect, -0.1% [-7.4, +6.4]. X03 rechecked on these new days (E5) fell to +2.8% [-4.8, +10.7], with weekly parts +7.5, +4.8, -0.7, +0.3. Across E3 and E5 the X03 effect declines steadily and is about zero in the latest two weeks, so it looks deteriorated. Round 3: spend the last experiment on X03 alone over days 113-126. This 14-day window does not overlap E5, and it decides whether X03 stays in the final selection. X01 and X02 were last tested on days 57-84. Their effect may have changed since, but the remaining budget cannot cover them.

Beliefs:
- X01 (D): **rejected**; cites E1; Skill -3.9% [-12.4, +5.5], 14 days won and 14 lost, weekly parts mostly negative. No evidence it helps. It has not been retested after day 84.
- X02 (E): **rejected**; cites E2; Skill -5.5% [-13.9, +3.2], 13 days won and 15 lost, weekly parts mostly negative. No evidence it helps. It has not been retested after day 84.
- X03 (R): **deteriorated**; cites E3, E5; Days 57-84 gave +17.8% with an interval excluding zero (E3). Days 85-112 gave only +2.8% with an interval straddling zero, and the last two weeks were about 0% (E5). The steady decline suggests its value has faded. The final recheck is pending.
- X04 (N): **rejected**; cites E4; Skill -0.1% [-7.4, +6.4], 12 days won and 16 lost, weekly parts all near zero. No measurable contribution.
Experiments:
- E6: covariates ['X03'], reference [], 14 days, expected no_change (X03's skill fell from +17.8% (E3) to +2.8% (E5), and its last two weeks were about 0%. Days 113-126 do not overlap E5 and are the data closest to the forecast period. They test whether X03 still adds anything; the trend suggests it does not.) -> -1.4% [-6.6, +3.4] on days 113-126

### Call 4 (final, days 1-126)

API attempts: #1 end_turn, 12.638 s

Notes: Final call, no experiments. E1-E2 (days 57-84): X01 -3.9% [-12.4, +5.5] and X02 -5.5% [-13.9, +3.2], no help. E3 (days 57-84): X03 +17.8% [+9.8, +26.6], but its weekly skill declined from +31.8% to +10.0%. E4 (days 85-112): X04 -0.1% [-7.4, +6.4], no effect. E5 (days 85-112): X03 +2.8% [-4.8, +10.7], weekly +7.5, +4.8, -0.7, +0.3. E6 (days 113-126): X03 -1.4% [-6.6, +3.4], 7 days won and 7 lost, weekly -0.7 and -1.8. X03's effect decayed steadily across three non-overlapping windows and is now about zero to slightly negative. No candidate shows a benefit on recent data. Caveat: X01 and X02 were only tested on days 57-84, and X04 only on days 85-112, so a later change in their usefulness cannot be ruled out. Even so, no evidence supports including them.

Beliefs:
- X01 (D): **rejected**; cites E1; Skill -3.9% [-12.4, +5.5], 14 days won and 14 lost, weekly parts mostly negative. No evidence it helps. It was not retested after day 84, so later behaviour is unknown.
- X02 (E): **rejected**; cites E2; Skill -5.5% [-13.9, +3.2], 13 days won and 15 lost, weekly parts mostly negative. No evidence it helps. It was not retested after day 84.
- X03 (R): **deteriorated**; cites E3, E5, E6; Clearly helpful on days 57-84 (+17.8%, interval excluding zero; E3). It fell to +2.8% on days 85-112 (E5) and to -1.4% [-6.6, +3.4] on days 113-126 (E6). Its weekly skill declined monotonically to about zero or below, so its earlier value has faded.
- X04 (N): **rejected**; cites E4; Skill -0.1% [-7.4, +6.4] on days 85-112, 12 days won and 16 lost, weekly parts all near zero. No measurable contribution.
- Final selection: []
- Conclusion: Select no covariates and forecast from the target history alone. X01, X02 and X04 never showed skill distinguishable from zero, and their point estimates were zero or negative (E1, E2, E4). X03 was the only helpful candidate (+17.8% on days 57-84, E3). Its effect then decayed steadily across non-overlapping windows: +2.8% on days 85-112 (E5) and -1.4% [-6.6, +3.4] on days 113-126 (E6), the period closest to the forecast horizon. Given this non-stationarity, X03 is unlikely to help after day 126 and could add noise. Limitations: X01 and X02 were tested only on days 57-84, and X04 only on days 85-112, so a recent change in their usefulness is possible but was not tested. Most E6 skill estimates are small and the intervals are wide. If monitoring continues, X03 should be rechecked periodically in case its relationship with the target returns.

## Revealed truth

First changed day 88. R = X03 (sign +1), E = X02 (sign +1), D = X01 (sign +1), N = X04 (sign +1).

## Integrity and infrastructure

Integrity issues: none. Call failures: none.

## Evidence check (t0-beta, 28 days, against no covariate)

- R on days 57-84 (before the change): +17.8% [+9.8, +26.6]
- E on days 99-126 (after the change): +42.1% [+32.1, +50.8]

## Behaviours

- B1 initial hypothesis: yes
- B2 test: yes
- B3 correct interpretation: yes
- B4 negative result kept: yes
- B5 weakening noticed: yes
- B6 another candidate investigated: yes
- B7 new covariate identified: no
- B8 beliefs revised: yes
- B9 separation or conditional test: no
- B10 no unsupported noise: yes
- interpretation errors: 0

## Candidates: planted role, predictive use, researcher

| id | role | causal effect | t0-beta alone (127-154) | incremental | researcher final | selected | script |
|---|---|---|---|---|---|---|---|
| X01 | D | never (proxy of E) | +13.0% [-0.6, +28.8] | D given E: +5.9% [-0.3, +13.0] | rejected | False | True |
| X02 | E | from the change on | +41.3% [+32.3, +50.1] | E given D: +36.5% [+21.9, +47.3] | rejected | False | True |
| X03 | R | before the change only | +0.6% [-7.6, +10.0] | R given E: +1.4% [-11.6, +9.2] | deteriorated | False | False |
| X04 | N | never | +2.3% [-6.1, +11.7] | N given E: +0.7% [-5.0, +6.8] | rejected | False | False |

## Confirmation (days 127-154; t0-beta and ridge)

| comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} | +41.3% [+32.3, +50.1] | +44.3% [+31.2, +53.0] |
| {R} vs {} | +0.6% [-7.6, +10.0] | -1.3% [-15.3, +6.5] |
| {D} vs {} | +13.0% [-0.6, +28.8] | +10.0% [-9.0, +31.3] |
| {N} vs {} | +2.3% [-6.1, +11.7] | -1.2% [-9.0, +6.1] |
| {E, D} vs {} | +44.8% [+34.5, +54.6] | +42.7% [+31.5, +52.2] |
| R given E ({E, R} vs {E}) | +1.4% [-11.6, +9.2] | +1.6% [-5.8, +9.3] |
| D given E ({E, D} vs {E}) | +5.9% [-0.3, +13.0] | -2.8% [-12.2, +7.2] |
| N given E ({E, N} vs {E}) | +0.7% [-5.0, +6.8] | +1.8% [-3.0, +7.4] |
| E given D ({E, D} vs {D}) | +36.5% [+21.9, +47.3] | +36.4% [+14.3, +48.5] |
| AI selection vs {} | empty or invalid | - |
| script selection vs {} | +44.8% [+34.5, +54.6] | +42.7% [+31.5, +52.2] |

AI selection: []; script selection: ['X01', 'X02'].

## Script

- S1 (round 1): ['X01'] vs none, 28 days -> -3.9% [-12.4, +5.5] on days 57-84
- S2 (round 1): ['X02'] vs none, 28 days -> -5.5% [-13.9, +3.2] on days 57-84
- S3 (round 2): ['X03'] vs none, 14 days -> -0.3% [-10.8, +7.7] on days 99-112
- S4 (round 2): ['X04'] vs none, 14 days -> +0.6% [-10.6, +8.5] on days 99-112
- S5 (round 3): ['X01'] vs none, 14 days -> +20.6% [+8.2, +29.3] on days 113-126
- S6 (round 3): ['X02'] vs none, 14 days -> +45.2% [+31.4, +55.1] on days 113-126

## Cost

API attempts 4 (refusals 0 [], repairs 0); tokens 21223 ({'input_tokens': 5729, 'output_tokens': 4106, 'cache_read_input_tokens': 11388, 'cache_creation_input_tokens': 0}); t0-beta forecasts {'research_scripted': 168, 'research_ai': 224, 'evaluate': 476}; evaluate 27.1 s.
