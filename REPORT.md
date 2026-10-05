# Human1 three-world result: SCRIPTABLE NARROW KERNEL

Reading row 4: informative 2 (w2, w3); L2 succeeds in 2 (w2, w3), comparator in 2 (w2, w3); experiments over informative worlds: L2 8, comparator 8 (efficiency advantage: no).

- Three worlds and one stochastic trajectory of the researcher in each: a small batch, not a rate.
- E is in every packet by construction: a benchmark condition (a good hypothesis supplied by a human), not a discovery claim. Hypothesis generation is not tested.
- The question is predictive information, not causation.
- The comparator's day-126 conditional tests are the contrasts the informativeness check runs, so in an informative E+D world the script resolves the pair by construction: it is the competence floor.
- Confirmation skill is reported separately and never rescues an unsupported conclusion.

human1_spec_sha `5a3f984e7456d21c50ae68080752499bccb9bac68e0dd673de1f7219a6bbd295`; run 37284111531; commit 037b7b44d0a5c2f313a0b41f80d8161b4a0bdfad; instrument theforecastingcompany/t0-beta @ c8885416fab935d604749a90cdcbf9b54fffcaeb (tfc-t0 0.5.0); lesson sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`.

Integrity: clean. L2 call failures: none.

| world | pair | informative | L2 success | L2 criteria 1-5 | comparator success | comparator criteria 1-5 | experiments L2 / comparator |
|---|---|---|---|---|---|---|---|
| w1 | E+D | no | no | 1:n 2:Y 3:n 4:Y 5:n | no | 1:n 2:Y 3:n 4:Y 5:Y | 4 / 4 |
| w2 | E+noise | yes | yes | 1:Y 2:Y 3:Y 4:Y 5:Y | yes | 1:Y 2:Y 3:Y 4:Y 5:Y | 4 / 4 |
| w3 | E+R | yes | yes | 1:Y 2:Y 3:Y 4:Y 5:Y | yes | 1:Y 2:Y 3:Y 4:Y 5:Y | 4 / 4 |

Closing line (predeclared): USE A SCRIPT / HUMAN-DRIVEN WORKFLOW

## World w1: E+D, UNINFORMATIVE

First changed day 90. Supplied pair: E = X01, D = X02. Integrity: clean.

Informativeness (direct t0-beta on the observed data; required: E alone, days 99-112 or 99-126 (above 0); E given D, days 99-126 (above 0); D given E, days 99-126 (at or below 0)):

- E alone, days 99-112: +20.4% [+7.0, +31.7]
- E alone, days 99-126: +23.3% [+12.7, +33.6]
- E given D, days 99-126: +5.0% [-3.0, +13.6]
- D given E, days 99-126: -13.5% [-24.8, -2.4]
- (descriptive) D alone, days 99-112: +5.8% [-9.4, +17.5]
- (descriptive) D alone, days 99-126: +8.3% [-4.8, +21.9]

E detectable: yes; contrast present: no.

| | L2 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 4 | 4 |
| final statuses | X01 (E) accepted, X02 (D) rejected | X01 (E) promising, X02 (D) rejected |
| final selection | ['X01'] | [] |
| criteria 1-5 | 1:n 2:Y 3:n 4:Y 5:n | 1:n 2:Y 3:n 4:Y 5:Y |
| unsupported acceptances / rejections | 1 / 0 | 0 / 0 |
| SUCCESS | no | no |
| final selection vs {} on days 127-154 (t0-beta; reported separately) | +34.7% [+24.4, +44.0] | empty selection |

### L2: experiments in order

- E1 (round 1): [X01 (E)] given none, 28 days, scored days 85-112 -> +16.3% [+3.1, +26.5] (not usable: mixed or under 14 days)
- E2 (round 1): [X02 (D)] given none, 28 days, scored days 85-112 -> +7.5% [-10.6, +20.3] (not usable: mixed or under 14 days)
- E3 (round 2): [X02 (D)] given [X01 (E)], 28 days, scored days 99-126 -> -13.5% [-24.8, -2.4]
- E4 (round 2): [X01 (E)] given [X02 (D)], 28 days, scored days 99-126 -> +5.0% [-3.0, +13.6]

### L2: final conclusion (verbatim)

- X01 (E): accepted; cites E1, E3, E4; reason: Marginal skill +16.3% with a CI excluding zero on days 85-112 (E1). On days 99-126 X01 alone had the lowest MAE tested (0.839), below X02 alone (1.002) and both together (0.952). Its incremental value over X02 alone is +5% but the CI spans zero (E4). Its marginal value against no covariates on days 113-126 was not tested directly.
- X02 (D): rejected; cites E2, E3; reason: Given X01, adding X02 worsened forecasts on days 99-126 (-13.5%, CI excluding zero, negative in every week including the newest). Its marginal value was unresolved on days 85-112 (E2). This rejection rests on current-regime data but is dated: it holds to day 126 and could change if the system shifts again.

Conclusion: Select X01 only. Supported: X01 improved on no covariates through day 112 (E1, +16.3%, CI excluding zero). Supported: on days 99-126, adding X02 to X01 made forecasts significantly worse (E3, -13.5%, CI -24.8 to -2.4), consistently in every week. That window includes the post-day-112 data, so the finding against X02 comes from the current regime, not an outdated one. Among the configurations tested on days 99-126, X01 alone had the lowest error. Uncertain: whether X01 still beats no covariates after day 112, since that was never tested directly. Uncertain: X01's increment over X02 alone (E4, +5%, CI spans zero), though its newest week was strongly positive (+15.8%). Uncertain: X02's standalone value against no covariates after day 112, which was also never tested. Given possible non-stationarity, the X02 rejection is dated to day 126, and performance of the X01 model should be monitored.

### L2: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X01 (E) | accepted | yes | no | no | no | yes | no (acceptance needs positive evidence, alone or given the other) |
| X02 (D) | rejected | no | no | no | no | yes | yes (a rejection needs a negative result and no positive one) |

Selection ['X01'] supported: no; incoherent: none; unsupported acceptances: ['X01']; unsupported rejection or zero-effect claims: none.

### L2 trajectory

#### Call 1 (round 1, days 1-112); budget left after it: 2

Beliefs entering the round (written with its requests): X01 (E) untested, X02 (D) untested.
Notes (written with the requests): Round 1 (days 1-112). Nothing tested yet. Plan: screen each candidate individually against a no-covariate baseline over the last 28 days. The per-week skill breakdown can show drift around the reported change in forecast behaviour. Round 2 will test conditional value (each candidate given the other) on the most recent data, including days 113-126.
- E1: covariates ['X01'], reference [], 28 days, expected improves -> +16.3% [+3.1, +26.5] on days 85-112 (straddles the change). Because: Individual screen of X01 against no covariates. A 28-day window gives a usable interval, and the 7-day parts can show whether any effect is growing or decaying recently.
- E2: covariates ['X02'], reference [], 28 days, expected improves -> +7.5% [-10.6, +20.3] on days 85-112 (straddles the change). Because: Individual screen of X02 against no covariates on the same window, so the two can be compared directly. The weekly parts can show an emerging or fading signal after the reported change.
Belief updates after these results (the next call's table): X01 (E) untested -> promising, X02 (D) untested -> promising.

#### Call 2 (round 2, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (D) promising.
Notes (written with the requests): Round 1 (days 85-112, no-covariate reference): E1 X01 skill +16.3% (CI +3.1 to +26.5), 20/8 days won, positive in 3 of 4 weeks (first week -0.9%). E2 X02 skill +7.5% (CI -10.6 to +20.3), 16/12, mixed weeks. So X01 has supported marginal value up to day 112. X02's marginal value is unresolved. Neither result says anything about days 113-126 or about value conditional on the other candidate. Round 2 plan: use both remaining experiments on conditional tests over days 99-126. That window includes the 14 new days, and its weekly parts show any recent change. E3 tests X02 given X01. E4 tests X01 given X02.
- E3: covariates ['X02'], reference ['X01'], 28 days, expected no_change -> -13.5% [-24.8, -2.4] on days 99-126 (after the change). Because: E2 showed weak, uncertain marginal value for X02, possibly overlapping with X01's (E1). This tests whether X02 adds value given X01 on days 99-126. That covers the new days, where an emerging signal would first show in the weekly parts.
- E4: covariates ['X01'], reference ['X02'], 28 days, expected improves -> +5.0% [-3.0, +13.6] on days 99-126 (after the change). Because: E1 supported X01 marginally to day 112. This checks whether X01 adds value beyond X02 and whether its effect persists or decays on days 113-126, using the last two weekly parts. This distinguishes the individual contributions.
Belief updates after these results (the next call's table): X01 (E) promising -> accepted, X02 (D) promising -> rejected.

#### Call 3 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) accepted, X02 (D) rejected.
Notes (written with the requests): E1 (days 85-112, no covariates as reference): X01 skill +16.3% (CI +3.1 to +26.5), 20 days won and 8 lost. E2 (same window): X02 skill +7.5% (CI -10.6 to +20.3), 16 won and 12 lost, with mixed weeks. E3 (days 99-126): adding X02 to X01 gave skill -13.5% (CI -24.8 to -2.4), 8 won and 20 lost, negative in all 4 weeks including the newest two. E4 (days 99-126): adding X01 to X02 gave skill +5.0% (CI -3.0 to +13.6), 14 won and 14 lost; the last week was +15.8%. MAE on days 99-126: X01 alone 0.839, X02 alone 1.002, both 0.952. X01 alone was the best of the three configurations tested in the window that includes the new days. No test compared any candidate with the no-covariate baseline after day 112.
Final selection: ['X01']
Conclusion: Select X01 only. Supported: X01 improved on no covariates through day 112 (E1, +16.3%, CI excluding zero). Supported: on days 99-126, adding X02 to X01 made forecasts significantly worse (E3, -13.5%, CI -24.8 to -2.4), consistently in every week. That window includes the post-day-112 data, so the finding against X02 comes from the current regime, not an outdated one. Among the configurations tested on days 99-126, X01 alone had the lowest error. Uncertain: whether X01 still beats no covariates after day 112, since that was never tested directly. Uncertain: X01's increment over X02 alone (E4, +5%, CI spans zero), though its newest week was strongly positive (+15.8%). Uncertain: X02's standalone value against no covariates after day 112, which was also never tested. Given possible non-stationarity, the X02 rejection is dated to day 126, and performance of the X01 model should be monitored.

### Comparator: experiments in order

- C1 (round 1): [X01 (E)] given none, 28 days, scored days 85-112 -> +16.3% [+3.1, +26.5] (not usable: mixed or under 14 days)
- C2 (round 1): [X02 (D)] given none, 28 days, scored days 85-112 -> +7.5% [-10.6, +20.3] (not usable: mixed or under 14 days)
- C3 (round 2): [X01 (E)] given [X02 (D)], 28 days, scored days 99-126 -> +5.0% [-3.0, +13.6]
- C4 (round 2): [X02 (D)] given [X01 (E)], 28 days, scored days 99-126 -> -13.5% [-24.8, -2.4]

### Comparator: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X01 (E) | promising | no | no | no | no | yes | yes (no claim of support or of absence) |
| X02 (D) | rejected | no | no | no | no | yes | yes (a rejection needs a negative result and no positive one) |

Selection [] supported: yes; incoherent: none; unsupported acceptances: none; unsupported rejection or zero-effect claims: none.

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +34.7% [+24.4, +44.0] | +46.6% [+30.0, +60.9] |
| {D} vs {} | +24.9% [+12.8, +36.1] | +27.9% [+13.7, +38.6] |
| {E, D} vs {} | +28.2% [+16.0, +38.9] | +49.0% [+33.8, +61.1] |
| D given E ({E, D} vs {E}) | -10.0% [-22.0, -0.8] | +4.6% [-3.9, +9.7] |
| E given D ({E, D} vs {D}) | +4.4% [-3.0, +12.6] | +29.3% [+13.6, +42.8] |

## World w2: E+noise, informative

First changed day 90. Supplied pair: E = X01, N = X02. Integrity: clean.

Informativeness (direct t0-beta on the observed data; required: E alone, days 99-112 or 99-126 (above 0); N alone, days 99-112 (at or below 0); N alone, days 99-126 (at or below 0); N given E, days 99-112 (at or below 0); N given E, days 99-126 (at or below 0)):

- E alone, days 99-112: +23.2% [-6.3, +38.2]
- E alone, days 99-126: +27.0% [+9.4, +35.6]
- N alone, days 99-112: -14.7% [-36.0, +2.7]
- N alone, days 99-126: -8.5% [-20.1, +2.3]
- N given E, days 99-112: +6.8% [-8.3, +22.6]
- N given E, days 99-126: -2.9% [-12.7, +8.3]
- (descriptive) E given N, days 99-126: +30.7% [+14.5, +39.4]

E detectable: yes; contrast present: yes.

| | L2 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 4 | 4 |
| final statuses | X01 (E) accepted, X02 (N) rejected | X01 (E) accepted, X02 (N) redundant |
| final selection | ['X01'] | ['X01'] |
| criteria 1-5 | 1:Y 2:Y 3:Y 4:Y 5:Y | 1:Y 2:Y 3:Y 4:Y 5:Y |
| unsupported acceptances / rejections | 0 / 0 | 0 / 0 |
| SUCCESS | **yes** | **yes** |
| final selection vs {} on days 127-154 (t0-beta; reported separately) | +43.2% [+32.8, +52.4] | +43.2% [+32.8, +52.4] |

### L2: experiments in order

- E1 (round 1): [X01 (E)] given none, 28 days, scored days 85-112 -> +11.8% [-4.0, +26.9] (not usable: mixed or under 14 days)
- E2 (round 1): [X02 (N)] given none, 28 days, scored days 85-112 -> -7.8% [-20.9, +3.7] (not usable: mixed or under 14 days)
- E3 (round 2): [X01 (E)] given none, 28 days, scored days 99-126 -> +27.0% [+9.4, +35.6]
- E4 (round 2): [X02 (N)] given [X01 (E)], 28 days, scored days 99-126 -> -2.9% [-12.7, +8.3]

### L2: final conclusion (verbatim)

- X01 (E): accepted; cites E1, E3; reason: E3 skill is +27.0% with a 95% interval of +9.4 to +35.6 that excludes zero, and 20/8 days won. Both new weeks (113-126) are strongly positive (+28.7%, +32.1%). The E1 last-week drop did not persist.
- X02 (N): rejected; cites E2, E4; reason: Re-screened on the newest data given X01 (E4): -2.9%, 9/19 days, last two weeks negative. Alone on days 85-112 (E2) it scored -7.8%. No sign of an emerging signal. X02 alone was never tested on days 113-126, so this rejection is dated to the data observed so far.

Conclusion: Select X01 only. Supported: X01 currently improves day-ahead forecasts. E3 measured +27% skill over no covariates on days 99-126, with an interval excluding zero and both newest weeks positive. The apparent decay in E1's last week was a single bad week that reversed. Also supported: X02 adds no value given X01 on the most recent data (E4: -2.9%, 9/19 days, last two weeks negative), and alone it did not help on days 85-112 (E2). Uncertain: X01's effect varies from week to week (one week at -17.6%), so its future size is uncertain if the process shifts again. E4's interval (-12.7% to +8.3%) cannot exclude a small X02 benefit. X02 alone was not re-tested after day 112, so its rejection rests on its redundancy given X01 and should be revisited if behaviour changes again.

### L2: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X01 (E) | accepted | yes | yes | no | no | no | yes (acceptance needs positive evidence, alone or given the other) |
| X02 (N) | rejected | no | no | no | no | yes | yes (a rejection needs a negative result and no positive one) |

Selection ['X01'] supported: yes; incoherent: none; unsupported acceptances: none; unsupported rejection or zero-effect claims: none.

### L2 trajectory

#### Call 1 (round 1, days 1-112); budget left after it: 2

Beliefs entering the round (written with its requests): X01 (E) untested, X02 (N) untested.
Notes (written with the requests): Round 1 (days 1-112). Nothing tested yet. Plan: screen each candidate on its own against a no-covariate reference over the last 28 days. The 7-day part skills will show any recent drift. In round 2, test incremental value (one given the other) on the newest data, depending on these results.
- E1: covariates ['X01'], reference [], 28 days, expected improves -> +11.8% [-4.0, +26.9] on days 85-112 (straddles the change). Because: Marginal screen of X01 alone vs no covariates. A 28-day window gives a usable interval, and its weekly parts can reveal whether usefulness is changing over time.
- E2: covariates ['X02'], reference [], 28 days, expected improves -> -7.8% [-20.9, +3.7] on days 85-112 (straddles the change). Because: Marginal screen of X02 alone vs no covariates, on the same window so the two can be compared directly. Weekly parts will show emerging or decaying signal.
Belief updates after these results (the next call's table): X01 (E) untested -> promising, X02 (N) untested -> rejected.

#### Call 2 (round 2, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (N) rejected.
Notes (written with the requests): Round 1 (days 85-112): E1 X01 alone vs none: +11.8% (CI -4.0 to +26.9), 16/12, weekly parts -12, +18, +43, -18. The skill is positive on average but not conclusive, and the last week turned negative, so the signal may be drifting. E2 X02 alone vs none: -7.8% (CI -20.9 to +3.7), 11/17, weekly parts -15, +9, -4, -36. X02 tends to hurt, but that finding is dated to days 85-112. Round 2 plan: re-test X01 on days 99-126 to check whether its benefit holds or decays in the new days 113-126. Re-screen X02 on the same recent window, conditional on X01, to test incremental value and any emerging signal.
- E3: covariates ['X01'], reference [], 28 days, expected improves -> +27.0% [+9.4, +35.6] on days 99-126 (after the change). Because: Re-tests X01 alone on days 99-126. This overlaps E1's strong weeks and adds two new weeks (113-126), so the weekly parts show whether E1's last-week drop (-17.6%) persisted into a decline or was noise.
- E4: covariates ['X02'], reference ['X01'], 28 days, expected no_change -> -2.9% [-12.7, +8.3] on days 99-126 (after the change). Because: Tests what X02 adds given X01 on the most recent days 99-126. This answers the incremental question and re-screens X02, whose rejection (E2) is dated, where an emerging signal would first appear (weeks 113-126).
Belief updates after these results (the next call's table): X01 (E) promising -> accepted.

#### Call 3 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) accepted, X02 (N) rejected.
Notes (written with the requests): E1 (days 85-112) tested X01 alone against no covariates: +11.8% (CI -4.0 to +26.9), 16/12 days, last week -17.6%. E2 (same window) tested X02 alone: -7.8% (CI -20.9 to +3.7), 11/17 days. E3 (days 99-126) re-tested X01 alone: +27.0% (CI +9.4 to +35.6), 20/8 days. Its weekly parts were +43.3, -17.6, +28.7 and +32.1. So the E1 last-week dip was one bad week, not a lasting decline; both new weeks (113-126) were clearly positive. E4 (days 99-126) tested X02 given X01: -2.9% (CI -12.7 to +8.3), 9/19 days, weekly parts +15.8, -2.1, -18.5 and -6.9. X02 adds nothing over X01 on the newest data, and is if anything harmful.
Final selection: ['X01']
Conclusion: Select X01 only. Supported: X01 currently improves day-ahead forecasts. E3 measured +27% skill over no covariates on days 99-126, with an interval excluding zero and both newest weeks positive. The apparent decay in E1's last week was a single bad week that reversed. Also supported: X02 adds no value given X01 on the most recent data (E4: -2.9%, 9/19 days, last two weeks negative), and alone it did not help on days 85-112 (E2). Uncertain: X01's effect varies from week to week (one week at -17.6%), so its future size is uncertain if the process shifts again. E4's interval (-12.7% to +8.3%) cannot exclude a small X02 benefit. X02 alone was not re-tested after day 112, so its rejection rests on its redundancy given X01 and should be revisited if behaviour changes again.

### Comparator: experiments in order

- C1 (round 1): [X01 (E)] given none, 28 days, scored days 85-112 -> +11.8% [-4.0, +26.9] (not usable: mixed or under 14 days)
- C2 (round 1): [X02 (N)] given none, 28 days, scored days 85-112 -> -7.8% [-20.9, +3.7] (not usable: mixed or under 14 days)
- C3 (round 2): [X01 (E)] given [X02 (N)], 28 days, scored days 99-126 -> +30.7% [+14.5, +39.4]
- C4 (round 2): [X02 (N)] given [X01 (E)], 28 days, scored days 99-126 -> -2.9% [-12.7, +8.3]

### Comparator: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X01 (E) | accepted | yes | no | yes | no | no | yes (acceptance needs positive evidence, alone or given the other) |
| X02 (N) | redundant | no | no | no | no | yes | yes (redundancy needs a conditional test given the other that is not positive) |

Selection ['X01'] supported: yes; incoherent: none; unsupported acceptances: none; unsupported rejection or zero-effect claims: none.

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +43.2% [+32.8, +52.4] | +32.6% [+19.9, +41.8] |
| {N} vs {} | -1.9% [-10.7, +6.5] | -9.5% [-21.5, +0.5] |
| {E, N} vs {} | +44.1% [+33.9, +52.9] | +31.1% [+19.3, +41.0] |
| N given E ({E, N} vs {E}) | +1.5% [-4.6, +7.2] | -2.2% [-9.8, +4.3] |
| E given N ({E, N} vs {N}) | +45.1% [+33.7, +54.8] | +37.1% [+27.4, +45.1] |

## World w3: E+R, informative

First changed day 92. Supplied pair: E = X02, R = X01. Integrity: clean.

Informativeness (direct t0-beta on the observed data; required: E alone, days 99-112 or 99-126 (above 0); R alone, days 99-112 (at or below 0); R alone, days 99-126 (at or below 0); R given E, days 99-112 (at or below 0); R given E, days 99-126 (at or below 0)):

- E alone, days 99-112: +29.5% [+11.5, +43.9]
- E alone, days 99-126: +27.5% [+16.5, +37.6]
- R alone, days 99-112: -1.6% [-13.2, +7.2]
- R alone, days 99-126: -1.0% [-8.5, +5.2]
- R given E, days 99-112: -0.1% [-2.5, +4.3]
- R given E, days 99-126: +1.0% [-4.3, +6.5]
- (descriptive) E given R, days 99-126: +28.9% [+17.2, +40.7]
- (descriptive) R alone, days 57-84 (before the change): +23.2% [+6.2, +39.2]
- (descriptive) R alone, days 85-112 (straddles the change): +15.5% [-1.2, +28.1]

E detectable: yes; contrast present: yes.

| | L2 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 4 | 4 |
| final statuses | X02 (E) accepted, X01 (R) redundant | X02 (E) accepted, X01 (R) redundant |
| final selection | ['X02'] | ['X02'] |
| criteria 1-5 | 1:Y 2:Y 3:Y 4:Y 5:Y | 1:Y 2:Y 3:Y 4:Y 5:Y |
| unsupported acceptances / rejections | 0 / 0 | 0 / 0 |
| SUCCESS | **yes** | **yes** |
| final selection vs {} on days 127-154 (t0-beta; reported separately) | +40.2% [+20.8, +52.2] | +40.2% [+20.8, +52.2] |

### L2: experiments in order

- E1 (round 1): [X01 (R)] given none, 28 days, scored days 85-112 -> +15.5% [-1.2, +28.1] (not usable: mixed or under 14 days)
- E2 (round 1): [X02 (E)] given none, 28 days, scored days 85-112 -> +17.3% [-1.4, +32.9] (not usable: mixed or under 14 days)
- E3 (round 2): [X02 (E)] given [X01 (R)], 28 days, scored days 99-126 -> +28.9% [+17.2, +40.7]
- E4 (round 2): [X01 (R)] given [X02 (E)], 28 days, scored days 99-126 -> +1.0% [-4.3, +6.5]

### L2: final conclusion (verbatim)

- X01 (R): redundant; cites E1, E4; reason: E1 showed strong early skill that faded after days 85-91. E4 shows no added value given X02 on days 99-126: +1.0%, interval includes zero, lost 16 of 28 days. Any information it carries seems to be covered by X02. This judgement holds for the current regime only and is provisional.
- X02 (E): accepted; cites E2, E3; reason: E2 showed emerging marginal skill. E3 shows X02 adds +28.9% over X01 on days 99-126, with an interval excluding zero and positive skill in every week. Its single-covariate MAE (0.859) is far below X01's (1.197) over the same days.

Conclusion: Use X02 alone. Supported: in the most recent 28 days (99-126), X02 adds substantial, statistically clear skill on top of X01 (E3: +28.9%, CI +17.2 to +40.7, positive every week). X01 adds nothing detectable given X02 (E4: +1.0%, CI -4.3 to +6.5, 12/16 days). The data are consistent with a regime change around day 91: X01's usefulness decayed (E1) while X02's emerged (E2). Uncertain: (1) X02's skill against a no-covariate reference was not re-measured on days 113-126. Its benefit there is inferred from E3 and its lower single-covariate error, not tested directly. (2) Weekly skill in E3 fluctuates (+9.9 to +44.9), so the size of the gain is uncertain. (3) The process is non-stationary. X01's redundancy holds for the current regime only; it could become useful again, or X02 could decay, after a further shift. (4) The E4 interval allows a small benefit from X01, but adding it is not justified by the evidence.

### L2: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X02 (E) | accepted | yes | no | yes | no | no | yes (acceptance needs positive evidence, alone or given the other) |
| X01 (R) | redundant | no | no | no | no | yes | yes (redundancy needs a conditional test given the other that is not positive) |

Selection ['X02'] supported: yes; incoherent: none; unsupported acceptances: none; unsupported rejection or zero-effect claims: none.

### L2 trajectory

#### Call 1 (round 1, days 1-112); budget left after it: 2

Beliefs entering the round (written with its requests): X01 (R) untested, X02 (E) untested.
Notes (written with the requests): Round 1 start. No prior results. Plan: screen each candidate alone against a no-covariate reference on the last 28 days (days 85-112), using the per-week skill breakdown to detect drift. In round 2, run conditional tests (one candidate given the other) on the most recent data to settle redundancy and whether any signal is emerging or decaying.
- E1: covariates ['X01'], reference [], 28 days, expected improves -> +15.5% [-1.2, +28.1] on days 85-112 (straddles the change). Because: Marginal screen of X01 against no covariates over the last 28 days. Per-week skills will show whether any effect is stable, emerging or decaying, given the reported change in forecast behaviour.
- E2: covariates ['X02'], reference [], 28 days, expected improves -> +17.3% [-1.4, +32.9] on days 85-112 (straddles the change). Because: Marginal screen of X02 against no covariates over the same 28 days, so it can be compared directly with X01 and checked week by week for drift.
Belief updates after these results (the next call's table): X01 (R) untested -> deteriorated, X02 (E) untested -> promising.

#### Call 2 (round 2, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) deteriorated, X02 (E) promising.
Notes (written with the requests): Round 1 (days 85-112, no-covariate reference): E1 X01 skill +15.5% (CI -1.2 to +28.1), 19/9 days, but per-week +46.6, +4.5, -13.0, +11.4. Most of its gain came in days 85-91, so it looks like a decaying signal. E2 X02 skill +17.3% (CI -1.4 to +32.9), 23/5 days, per-week +1.3, +15.6, +38.6, +19.2. This looks like an emerging signal. Both intervals include zero, so neither is established. Round 2 plan: conditional tests on days 99-126, which include 14 new days. First, X02 given X01, to see whether X02 adds value beyond X01 recently. Second, X01 given X02, to see whether X01 still adds anything or is now redundant or harmful. Per-week parts will show the trend in the newest weeks. Any rejection would be dated to this regime only.
- E3: covariates ['X02'], reference ['X01'], 28 days, expected improves -> +28.9% [+17.2, +40.7] on days 99-126 (after the change). Because: E2 suggests X02 is emerging and E1 that X01 is decaying. Testing X02 on top of X01 over days 99-126 (14 new days) checks whether X02 adds value beyond X01 in the current regime. Per-week parts show whether the gain persists in the newest weeks.
- E4: covariates ['X01'], reference ['X02'], 28 days, expected no_change -> +1.0% [-4.3, +6.5] on days 99-126 (after the change). Because: E1 per-week skills suggest X01's signal faded after day 91. Testing X01 given X02 over days 99-126 determines whether X01 is redundant or harmful once X02 is used, or still adds something, so the final selection can be X02 alone, both, or neither.
Belief updates after these results (the next call's table): X01 (R) deteriorated -> redundant, X02 (E) promising -> accepted.

#### Call 3 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) redundant, X02 (E) accepted.
Notes (written with the requests): E1 (days 85-112, vs none): X01 +15.5% (CI -1.2 to +28.1). Weekly skill was +46.6, +4.5, -13.0, +11.4, so its gain was front-loaded and looked like decay. E2 (same window): X02 +17.3% (CI -1.4 to +32.9), 23/5 days. Weekly skill was +1.3, +15.6, +38.6, +19.2, so it looked like an emerging signal. E3 (days 99-126): X02 given X01 +28.9% (CI +17.2 to +40.7), 22/6 days, every week positive (+44.9, +9.9, +38.9, +11.7). X02 adds clear value beyond X01 in the current regime. E4 (days 99-126): X01 given X02 +1.0% (CI -4.3 to +6.5), 12/16 days, weekly skill -1.5 to +2.2. X01 adds nothing detectable once X02 is used. Over days 99-126, X02 alone had MAE 0.859 and X01 alone 1.197.
Final selection: ['X02']
Conclusion: Use X02 alone. Supported: in the most recent 28 days (99-126), X02 adds substantial, statistically clear skill on top of X01 (E3: +28.9%, CI +17.2 to +40.7, positive every week). X01 adds nothing detectable given X02 (E4: +1.0%, CI -4.3 to +6.5, 12/16 days). The data are consistent with a regime change around day 91: X01's usefulness decayed (E1) while X02's emerged (E2). Uncertain: (1) X02's skill against a no-covariate reference was not re-measured on days 113-126. Its benefit there is inferred from E3 and its lower single-covariate error, not tested directly. (2) Weekly skill in E3 fluctuates (+9.9 to +44.9), so the size of the gain is uncertain. (3) The process is non-stationary. X01's redundancy holds for the current regime only; it could become useful again, or X02 could decay, after a further shift. (4) The E4 interval allows a small benefit from X01, but adding it is not justified by the evidence.

### Comparator: experiments in order

- C1 (round 1): [X01 (R)] given none, 28 days, scored days 85-112 -> +15.5% [-1.2, +28.1] (not usable: mixed or under 14 days)
- C2 (round 1): [X02 (E)] given none, 28 days, scored days 85-112 -> +17.3% [-1.4, +32.9] (not usable: mixed or under 14 days)
- C3 (round 2): [X01 (R)] given [X02 (E)], 28 days, scored days 99-126 -> +1.0% [-4.3, +6.5]
- C4 (round 2): [X02 (E)] given [X01 (R)], 28 days, scored days 99-126 -> +28.9% [+17.2, +40.7]

### Comparator: claims against its own experiments

| candidate | final status | selected | positive alone | positive given the other | negative alone | negative given the other | claim supported |
|---|---|---|---|---|---|---|---|
| X02 (E) | accepted | yes | no | yes | no | no | yes (acceptance needs positive evidence, alone or given the other) |
| X01 (R) | redundant | no | no | no | no | yes | yes (redundancy needs a conditional test given the other that is not positive) |

Selection ['X02'] supported: yes; incoherent: none; unsupported acceptances: none; unsupported rejection or zero-effect claims: none.

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +40.2% [+20.8, +52.2] | +37.3% [+23.0, +47.5] |
| {R} vs {} | +0.7% [-14.6, +16.2] | -10.1% [-19.0, -3.6] |
| {E, R} vs {} | +38.1% [+18.7, +50.4] | +35.3% [+18.1, +48.0] |
| R given E ({E, R} vs {E}) | -3.7% [-8.7, +0.7] | -3.1% [-13.5, +6.3] |
| E given R ({E, R} vs {R}) | +37.6% [+19.3, +49.0] | +41.2% [+27.2, +52.2] |

## Cost

- w1: L2 tokens 14846 ({'input_tokens': 2556, 'output_tokens': 2840, 'cache_read_input_tokens': 9450, 'cache_creation_input_tokens': 0}); API attempts 3 (refusals 0, repairs 0); research wall time L2 48.2 s, comparator 8.0 s; t0-beta forecasts: L2 140, comparator 140, evaluate 364.
- w2: L2 tokens 14536 ({'input_tokens': 2442, 'output_tokens': 2644, 'cache_read_input_tokens': 9450, 'cache_creation_input_tokens': 0}); API attempts 3 (refusals 0, repairs 0); research wall time L2 43.1 s, comparator 8.4 s; t0-beta forecasts: L2 140, comparator 140, evaluate 378.
- w3: L2 tokens 14996 ({'input_tokens': 2597, 'output_tokens': 2949, 'cache_read_input_tokens': 9450, 'cache_creation_input_tokens': 0}); API attempts 3 (refusals 0, repairs 0); research wall time L2 43.1 s, comparator 10.3 s; t0-beta forecasts: L2 140, comparator 140, evaluate 448.
- evaluate: 64.1 s.
