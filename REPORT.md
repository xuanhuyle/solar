# Phase B result: RESEARCHER FEASIBILITY FAILED

Verdict map row 2: N in the final selection with its latest lower bound <= 0 or never tested.

- One world is an existence check, not a rate.
- Even an ideal researcher completes the whole chain only when both R's and E's evidence is present in this world; the evidence check reports whether it was.

spec_sha `6ab46db996e345de093e5b650a3cd104ec60da23a1d4a0966ed72ce68b8788dc`; run 37088704906; commit 1fb0d078830a662066fc3f92cbf609af9370b04e.

## The hidden world (revealed after the research job)

Change at day 90 (first changed day). Roles: R = X02 (sign +1), E = X01 (sign +1), D = X04 (sign -1), N = X03 (sign -1).

## Integrity

Issues: none.

## Evidence check (t0, 28 days, against no covariate)

- R on days 57-84 (before the change): +29.3% [+18.0, +38.3]
- E on days 99-126 (after the change): +13.2% [+0.7, +24.6]

## Researcher trajectory

### Call 1 (round 1, days 1-84)

No valid response: the response was a refusal

### Call 2 (round 2, days 1-112)

No valid response: the response was a refusal

### Call 3 (round 3, days 1-126)

Notes: Calls 1 and 2 produced no valid response, so no experiments have run. Data now covers days 1-126. 6 experiments remain, but only 3 can run now because the final call allows none. Plan: screen the candidates in pairs and jointly against a no-covariate reference over a 28-day window (days 99-126). The per-week skill breakdown will show whether any effect is recent or fading, since the process may be non-stationary. Pair results plus the joint result should show which pair carries the signal and whether the pairs add to each other.

- X01 (E): **untested**; cites none; No experiments have run yet.
- X02 (R): **untested**; cites none; No experiments have run yet.
- X03 (N): **untested**; cites none; No experiments have run yet.
- X04 (D): **untested**; cites none; No experiments have run yet.
- E1: covariates ['X01', 'X02'], reference [], 28 days, expected no_change: +12.8% [-0.2, +25.9] on days 99-126
- E2: covariates ['X03', 'X04'], reference [], 28 days, expected no_change: +21.7% [+8.2, +34.4] on days 99-126
- E3: covariates ['X01', 'X02', 'X03', 'X04'], reference [], 28 days, expected no_change: +18.3% [+0.9, +34.0] on days 99-126

### Call 4 (final, days 1-126)

Notes: Only three experiments ran (E1-E3, all in call 3, all on a 28-day window, days 99-126, against a no-covariate reference). E2: the X03/X04 pair gave skill +21.7%, with a 95% interval of +8.2% to +34.4%, which excludes zero. It won 17 of 28 days. E1: the X01/X02 pair gave +12.8%, with an interval of -0.2% to +25.9%. That is borderline, and it won only 15 of 28 days. E3: all four together gave +18.3% (MAE 1.067), worse than X03/X04 alone (MAE 1.023). So adding X01/X02 to X03/X04 appears to add noise rather than signal. This is only an indirect comparison; X01/X02 was never tested with X03/X04 as reference. Caveat: in the last week (days 120-126) all three setups were at or below zero (-8.1%, -1.5%, -8.5%). This could be one noisy week or the start of deterioration, and the remaining budget could not be used to check. X03/X04 held up best in that week (-1.5%, close to neutral). I never separated X03 from X04, so I keep them as a pair.

- X01 (E): **redundant**; cites E1, E3; Tested only as a pair with X02. That pair's skill (+12.8%) had an interval touching zero. Adding X01/X02 to X03/X04 lowered skill from +21.7% (E2) to +18.3% (E3), so it adds nothing on top of X03/X04.
- X02 (R): **redundant**; cites E1, E3; Same evidence as X01: borderline alone as a pair, and it worsened the joint model relative to X03/X04 alone. Its individual contribution was never isolated.
- X03 (N): **accepted**; cites E2, E3; The X03/X04 pair gave +21.7% skill, with an interval of +8.2% to +34.4%, and was the best configuration tested. The last week was near neutral (-1.5%), so it is worth monitoring. Not separated from X04.
- X04 (D): **accepted**; cites E2, E3; Accepted jointly with X03 on the strength of E2. Its individual contribution was never isolated, so I keep the pair as tested.
- Final selection: ['X03', 'X04']
- Conclusion: Select X03 and X04. As a pair they gave the clearest gain over no covariates on days 99-126: +21.7% skill, with a 95% interval excluding zero. Adding X01 and X02 lowered skill to +18.3%, so I leave them out. Caveats: (1) X03 and X04 were never tested individually, so one of them may carry all the signal. (2) Every configuration weakened in the final week (days 120-126), and X03/X04 was roughly neutral there. Given possible non-stationarity, forecast performance after day 126 should be monitored, and the selection dropped if the gain does not recover.

## Behaviours

B1 no | B2 yes | B3 yes | B4 yes | B5 no | B6 no | B7 no | B8 no
Interpretation errors: 0.

## Candidates: causal role, predictive use, selection

| id | role | causal effect | t0 on days 127-154 vs no covariate | researcher final | selected | script |
|---|---|---|---|---|---|---|
| X01 | E | from the change on | +30.8% [+21.9, +39.5] | redundant | False | False |
| X02 | R | before the change only | +4.0% [-3.9, +12.6] | redundant | False | False |
| X03 | N | never | +0.3% [-5.7, +5.4] | accepted | True | False |
| X04 | D | never (proxy of E) | +25.7% [+12.6, +38.2] | accepted | True | True |

## Confirmation (days 127-154; t0 and ridge)

| comparison | t0 | ridge |
|---|---|---|
| {E} vs {} | +30.8% [+21.9, +39.5] | +35.2% [+23.0, +45.1] |
| {R} vs {} | +4.0% [-3.9, +12.6] | +2.1% [-8.9, +11.1] |
| {D} vs {} | +25.7% [+12.6, +38.2] | +23.2% [+11.5, +32.9] |
| {N} vs {} | +0.3% [-5.7, +5.4] | -3.9% [-12.9, +2.2] |
| {E, D} vs {} | +26.6% [+12.1, +39.6] | +31.8% [+17.7, +43.0] |
| D given E ({E, D} vs {E}) | -6.1% [-20.0, +6.5] | -5.2% [-14.2, +1.0] |
| E given D ({E, D} vs {D}) | +1.3% [-2.3, +4.8] | +11.1% [+0.6, +20.4] |
| AI selection vs {} | +23.5% [+10.8, +36.7] | +17.3% [-1.2, +31.9] |
| script selection vs {} | +25.7% [+12.6, +38.2] | +23.2% [+11.5, +32.9] |

Script selection: ['X04']; AI selection: ['X03', 'X04'].

## Cost

API calls 7; tokens 24435 ({'input_tokens': 2625, 'output_tokens': 2315, 'cache_read_input_tokens': 16710, 'cache_creation_input_tokens': 2785}); t0 forecasts {'research_scripted': 168, 'research_ai': 112, 'evaluate': 392}; evaluate 13.8 s.
