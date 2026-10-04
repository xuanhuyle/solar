# Discovery1 three-world result: NO DISCOVERY SIGNAL

Reading row 5: informative 3 (w1, w2, w3); L8 succeeds in 0 (none); comparator in 1 (w1).

- Three worlds and one stochastic trajectory of the researcher in each: a small batch, not a rate.
- The comparator resolves candidates to pairs only; it can succeed only where the emerging driver's pair partner is its proxy.
- Forecast accuracy alone is not discovery: success needs the six criteria, supporting evidence included.

discovery1_spec_sha `3a3801bbfdce36ca47eb1d32b91315407a90273850d3922740969c5e74c4d97e`; run 37238629496; commit 56ee1c3c9f1f947f7ae06f86bfd3ad87dbaa5eef; instrument theforecastingcompany/t0-beta @ c8885416fab935d604749a90cdcbf9b54fffcaeb (tfc-t0 0.5.0); lesson sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`.

Integrity: clean. L8 call failures: none.

| world | informative | L8 success | L8 criteria 1-6 | comparator success | comparator criteria 1-6 |
|---|---|---|---|---|---|
| w1 | yes | no | 1:Y 2:Y 3:Y 4:Y 5:n 6:Y | yes | 1:Y 2:Y 3:Y 4:Y 5:Y 6:Y |
| w2 | yes | no | 1:Y 2:n 3:n 4:n 5:n 6:Y | no | 1:Y 2:Y 3:Y 4:n 5:Y 6:Y |
| w3 | yes | no | 1:Y 2:Y 3:Y 4:Y 5:n 6:Y | no | 1:Y 2:Y 3:Y 4:n 5:Y 6:Y |

Closing line (predeclared): NARROW TO HUMAN-SUPPLIED HYPOTHESES

## World w1: informative

First changed day 89. R = X01, E = X05, D = X06, N1 = X08, N2 = X07, N3 = X04, N4 = X02, N5 = X03.

Detectability (t0-beta, E alone vs no covariate): days 99-112 +46.6% [+34.9, +55.6]; days 99-126 +49.3% [+40.1, +57.9].

Integrity: clean.

| | L8 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 6 | 6 |
| first experiment E entered | E2 (round 1, as covariate) | C2 (round 1, as covariate) |
| E tested after the change (as a covariate, rounds 2-3) | yes (E5) | yes (C4) |
| E distinguished from its companions (E the only covariate, lower bound > 0) | no | no |
| supporting evidence of its own (criterion 5) | none | C5 |
| final selection | [X05 (E), X06 (D)] | [X05 (E), X06 (D)] |
| R removed | yes | yes |
| noise selected | none | none |
| D selected | yes | yes |
| criteria 1-6 | 1:Y 2:Y 3:Y 4:Y 5:n 6:Y | 1:Y 2:Y 3:Y 4:Y 5:Y 6:Y |
| SUCCESS | no | **yes** |
| final selection vs {} on days 127-154 (t0-beta) | +31.9% [+12.9, +48.3] | +31.9% [+12.9, +48.3] |
| same, ridge (context only) | +44.3% [+30.2, +55.6] | +44.3% [+30.2, +55.6] |

D (X06): L8 final status accepted; L8 experiments including D: E2 ['X05', 'X06', 'X07', 'X08'] vs [] -2.0% [-19.1, +11.8]; E5 ['X05', 'X06', 'X07', 'X08'] vs [] +26.0% [+9.2, +43.5]; E6 ['X05', 'X06'] vs ['X07', 'X08'] +42.7% [+31.1, +52.4]. On confirmation, D alone +18.5% [+5.3, +31.9], D given E -0.7% [-5.6, +4.4].

L8 re-opened stale negatives: X05 (E) in E5; X06 (D) in E5; X07 (N2) in E5; X08 (N1) in E5. Lesson mentions: 0. Tokens 28445; API attempts 4 (repairs 0, refusals 0).

### L8 trajectory

#### Call 1 (round 1, days 1-84); budget left after it: 4

Beliefs entering the round (written with its requests): X01 (R) untested, X02 (N4) untested, X03 (N5) untested, X04 (N3) untested, X05 (E) untested, X06 (D) untested, X07 (N2) untested, X08 (N1) untested.
Notes (written with the requests): Round 1 (days 1-84). No evidence yet. Plan: screen all 8 candidates in two blocks of 4 (X01-X04, X05-X08) against a no-covariate reference over the last 28 days, then split any block that helps in later rounds. Keep budget for the most recent data (rounds 2-3), since the process may be non-stationary. The per-7-day skill breakdown will be watched for decay or emergence.
- E1: covariates ['X01', 'X02', 'X03', 'X04'], reference [], 28 days, expected no_change -> +46.5% [+31.1, +60.5] on days 57-84 (before the change). Because: Initial block screen of X01-X04 against a target-only forecast over days 57-84. A 28-day window gives an interval and four weekly skill values for spotting drift. There is no prior, so the expectation is neutral.
- E2: covariates ['X05', 'X06', 'X07', 'X08'], reference [], 28 days, expected no_change -> -2.0% [-19.1, +11.8] on days 57-84 (before the change). Because: Matching block screen of X05-X08, so that all 8 candidates are covered once in round 1. Blocks that help will be split in round 2. Budget is held back for recent-data re-screens.
Belief updates after these results (the next call's table): X01 (R) untested -> promising, X02 (N4) untested -> promising, X03 (N5) untested -> promising, X04 (N3) untested -> promising.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Beliefs entering the round (written with its requests): X01 (R) promising, X02 (N4) promising, X03 (N5) promising, X04 (N3) promising, X05 (E) untested, X06 (D) untested, X07 (N2) untested, X08 (N1) untested.
Notes (written with the requests): Round 1 (days 57-84): block X01-X04 helped strongly (E1 skill +46.5%, CI +31 to +61, 23/5 days won). The weekly skill was +37, +62, +49 and +30%. The last week is the lowest, which is a mild hint of decay to watch. Block X05-X08 was null (E2 -2.0%, CI -19 to +12). That null is dated to days 57-84 and is provisional given possible non-stationarity. Round 2 (days 1-112): split the X01-X04 block into pairs on the newest 28 days (85-112) to localise the signal and check for decay. Re-screen X05-X08 on the same recent window to catch any emerging signal. Keep 1 experiment for round 3 (days 113-126) to split the winning pair or confirm the regime.
- E3: covariates ['X01', 'X02'], reference [], 28 days, expected improves -> +6.3% [-11.1, +23.9] on days 85-112 (straddles the change). Because: Splits the helpful E1 block (+46.5%) to localise the signal. It uses the newest 28 days (85-112), so the weekly parts also show whether the E1 last-week dip (+30%) continues as decay.
- E4: covariates ['X03', 'X04'], reference [], 28 days, expected no_change -> +3.9% [-6.7, +13.4] on days 85-112 (straddles the change). Because: This is the other half of the E1 block, on the same recent window as E3, so the two pairs are comparable. Together with E3 it shows which pair carries the E1 skill. The neutral expectation reflects no individual evidence yet.
- E5: covariates ['X05', 'X06', 'X07', 'X08'], reference [], 28 days, expected no_change -> +26.0% [+9.2, +43.5] on days 85-112 (straddles the change). Because: The E2 null covers only days 57-84. With possible non-stationarity, this re-screens X05-X08 on days 85-112, where an emerging signal would first show. A null here would extend the null into the current regime.
Belief updates after these results (the next call's table): X01 (R) promising -> deteriorated, X02 (N4) promising -> deteriorated, X03 (N5) promising -> deteriorated, X04 (N3) promising -> deteriorated, X05 (E) untested -> promising, X06 (D) untested -> promising, X07 (N2) untested -> promising, X08 (N1) untested -> promising.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) deteriorated, X02 (N4) deteriorated, X03 (N5) deteriorated, X04 (N3) deteriorated, X05 (E) promising, X06 (D) promising, X07 (N2) promising, X08 (N1) promising.
Notes (written with the requests): R1 (days 57-84): block X01-X04 helped strongly (E1 +46.5%, CI +31 to +61). Block X05-X08 was null (E2 -2.0%). R2 (days 85-112): the X01-X04 signal largely vanished. E3 (X01,X02) gave +6.3% (CI -11 to +24, 14/14 days) and E4 (X03,X04) gave +3.9% (CI -7 to +13). This looks like decay or regime change, not localisation. Meanwhile X05-X08 emerged (E5 +26.0%, CI +9 to +44, 22/6 days). Its weekly skill was -5, +39, +44 and +40%, so the change started around day 92. The earlier E2 null is therefore outdated. R3: one experiment left. I will use it to split the emergent block on the newest data (days 99-126), testing X05,X06 on top of an X07,X08 reference. This shows whether X05,X06 add anything beyond X07,X08 in the current regime. Caveat: X07,X08 alone will still not have been tested against no covariates. The final choice will be between the full X05-X08 block and a pair.
- E6: covariates ['X05', 'X06'], reference ['X07', 'X08'], 28 days, expected no_change -> +42.7% [+31.1, +52.4] on days 99-126 (after the change). Because: E5 showed X05-X08 emerging from about day 92. This splits the block on the newest 28 days (99-126) and tests whether X05,X06 add beyond X07,X08. Positive skill means keep X05,X06; null means X07,X08 likely carry the E5 signal. The weekly parts also check persistence through days 113-126.
Belief updates after these results (the next call's table): X05 (E) promising -> accepted, X06 (D) promising -> accepted, X07 (N2) promising -> untested, X08 (N1) promising -> untested.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) deteriorated, X02 (N4) deteriorated, X03 (N5) deteriorated, X04 (N3) deteriorated, X05 (E) accepted, X06 (D) accepted, X07 (N2) untested, X08 (N1) untested.
Notes (written with the requests): R1 (days 57-84): block X01-X04 helped strongly (E1 +46.5%, CI +31 to +61). Block X05-X08 was null (E2 -2.0%). R2 (days 85-112): the X01-X04 signal collapsed. E3 (X01,X02) gave +6.3% with a CI spanning 0. E4 (X03,X04) gave +3.9% with a CI spanning 0. X05-X08 emerged (E5 +26%, CI +9 to +44), with weekly skill near +40% from about day 92. This points to a regime change around day 85-92, and it makes the E2 null outdated. R3 (days 99-126): E6 showed that X05,X06 add +42.7% (CI +31 to +52, 22/6 days) on top of an X07,X08 reference. The weekly skill was stable at +37/+43/+47/+41%, so the signal persists through day 126. X05 and X06 were never separated from each other. X07,X08 were never tested against no covariates, so their own value is unknown. X01-X04 were not re-tested on days 113-126; their deterioration is dated to days 85-112.
Final selection: ['X05', 'X06']
Conclusion: The system appears to have changed regime around days 85-92. Before that, block X01-X04 drove a forecast gain of about +46% (E1). That gain decayed to inconclusive levels afterwards (E3, E4). In parallel, the previously null X05-X08 block emerged (E5). On the newest data (days 99-126), X05,X06 add +42.7% beyond X07,X08, with a CI of +31 to +52 and stable weekly skill (E6). I therefore select X05 and X06. This is a set-level acceptance: the two were never separated from each other. X07 and X08 are excluded because their own contribution was never isolated. Caveat: the tested 0.800-MAE configuration also included X07,X08. If X07 or X08 carry some signal, dropping them could cost a little accuracy. X01-X04 are excluded as deteriorated. That judgement is dated to days 85-112, so they should be re-screened if X05,X06 start to decay, since the system has already shifted once.

### Comparator

Winning group in round 2: [X05 (E), X06 (D), X07 (N2), X08 (N1)].

- C1 (round 1): [X01 (R), X02 (N4), X03 (N5), X04 (N3)] vs none, 28 days -> +46.5% [+31.1, +60.5]
- C2 (round 1): [X05 (E), X06 (D), X07 (N2), X08 (N1)] vs none, 28 days -> -2.0% [-19.1, +11.8]
- C3 (round 2): [X01 (R), X02 (N4), X03 (N5), X04 (N3)] vs none, 28 days -> +9.1% [-10.6, +29.1]
- C4 (round 2): [X05 (E), X06 (D), X07 (N2), X08 (N1)] vs none, 28 days -> +26.0% [+9.2, +43.5]
- C5 (round 3): [X05 (E), X06 (D)] vs none, 28 days -> +45.7% [+34.6, +54.5]
- C6 (round 3): [X07 (N2), X08 (N1)] vs none, 28 days -> +1.5% [-8.0, +9.0]

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +32.3% [+11.2, +49.0] | +45.3% [+30.9, +56.7] |
| {R} vs {} | -2.1% [-8.4, +5.3] | -13.7% [-26.9, -4.1] |
| {D} vs {} | +18.5% [+5.3, +31.9] | +36.1% [+19.5, +50.3] |
| {E, D} vs {} | +31.9% [+12.9, +48.3] | +44.3% [+30.2, +55.6] |
| D given E ({E, D} vs {E}) | -0.7% [-5.6, +4.4] | -1.8% [-8.1, +4.3] |
| E given D ({E, D} vs {D}) | +16.4% [+0.8, +30.7] | +12.9% [-1.9, +24.2] |
| R given E ({E, R} vs {E}) | -3.6% [-10.4, +1.9] | -6.2% [-22.4, +4.2] |

## World w2: informative

First changed day 92. R = X05, E = X08, D = X02, N1 = X01, N2 = X06, N3 = X07, N4 = X03, N5 = X04.

Detectability (t0-beta, E alone vs no covariate): days 99-112 +13.9% [+3.2, +25.3]; days 99-126 +23.4% [+10.8, +34.8].

Integrity: clean.

| | L8 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 6 | 6 |
| first experiment E entered | E3 (round 1, as covariate) | C2 (round 1, as covariate) |
| E tested after the change (as a covariate, rounds 2-3) | no | yes (C4) |
| E distinguished from its companions (E the only covariate, lower bound > 0) | no | no |
| supporting evidence of its own (criterion 5) | none | C6 |
| final selection | [X01 (N1), X02 (D), X03 (N4), X07 (N3)] | [X07 (N3), X08 (E)] |
| R removed | yes | yes |
| noise selected | [X01 (N1), X03 (N4), X07 (N3)] | [X07 (N3)] |
| D selected | yes | no |
| criteria 1-6 | 1:Y 2:n 3:n 4:n 5:n 6:Y | 1:Y 2:Y 3:Y 4:n 5:Y 6:Y |
| SUCCESS | no | no |
| final selection vs {} on days 127-154 (t0-beta) | +27.3% [+14.8, +37.5] | +34.5% [+18.0, +47.2] |
| same, ridge (context only) | +31.7% [+16.2, +44.1] | +36.7% [+22.6, +48.2] |

D (X02): L8 final status promising; L8 experiments including D: E1 ['X01', 'X02', 'X03'] vs [] +1.3% [-8.1, +8.7]; E6 ['X01', 'X02', 'X03', 'X07'] vs [] +13.2% [-4.8, +27.2]. On confirmation, D alone +30.6% [+16.1, +42.0], D given E -7.8% [-19.4, +1.9].

L8 re-opened stale negatives: X01 (N1) in E6; X02 (D) in E6; X03 (N4) in E6; X07 (N3) in E6. Lesson mentions: 0. Tokens 30346; API attempts 4 (repairs 0, refusals 0).

### L8 trajectory

#### Call 1 (round 1, days 1-84); budget left after it: 3

Beliefs entering the round (written with its requests): X01 (N1) untested, X02 (D) untested, X03 (N4) untested, X04 (N5) untested, X05 (R) untested, X06 (N2) untested, X07 (N3) untested, X08 (E) untested.
Notes (written with the requests): Round 1 (days 1-84): no experiments yet. Plan: screen all eight candidates in three groups against a no-covariate reference over the last 28 days, giving finer resolution than two groups of four. This keeps 3 experiments for rounds 2-3. Later rounds will be used to split any helpful group and to re-check findings on recent data, since the process may not be stationary.
- E1: covariates ['X01', 'X02', 'X03'], reference [], 28 days, expected no_change -> +1.3% [-8.1, +8.7] on days 57-84 (before the change). Because: Initial group screen of X01-X03 against no covariates over 28 days (days 57-84), long enough for a usable interval. Expectation neutral: no prior information.
- E2: covariates ['X04', 'X05', 'X06'], reference [], 28 days, expected no_change -> +36.2% [+21.6, +47.0] on days 57-84 (before the change). Because: Initial group screen of X04-X06 against no covariates over the same 28-day window, so results are comparable across groups.
- E3: covariates ['X07', 'X08'], reference [], 28 days, expected no_change -> +5.2% [-5.9, +14.8] on days 57-84 (before the change). Because: Initial group screen of X07-X08 against no covariates over the same 28-day window. This completes coverage of all eight candidates in round 1.
Belief updates after these results (the next call's table): X01 (N1) untested -> rejected, X02 (D) untested -> rejected, X03 (N4) untested -> rejected, X04 (N5) untested -> promising, X05 (R) untested -> promising, X06 (N2) untested -> promising, X07 (N3) untested -> rejected, X08 (E) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Beliefs entering the round (written with its requests): X01 (N1) rejected, X02 (D) rejected, X03 (N4) rejected, X04 (N5) promising, X05 (R) promising, X06 (N2) promising, X07 (N3) rejected, X08 (E) rejected.
Notes (written with the requests): Round 1 (days 57-84, no-covariate reference): the X04-X06 group helped strongly (E2 +36.2%, CI +21.6 to +47.0, 22/6 days). Its last 7-day part fell to +8.0%, which may be an early sign of decay or may be noise. X01-X03 (E1 +1.3%) and X07-X08 (E3 +5.2%) were null, and both CIs span zero. These nulls are dated to days 57-84 and are provisional if the system changes. Round 2 plan: split X04-X06 on the newest 28 days (85-112) by testing X04 and X05 singly. The per-part skills will also show whether the group's value is decaying. X06 is judged by comparison with E2. I keep the last experiment for round 3, to re-screen the earlier-dismissed candidates on days 113-126, where an emerging signal would first show. If X04-X06 shows decay, that re-screen takes priority.
- E4: covariates ['X04'], reference [], 28 days, expected improves -> +6.0% [-3.7, +14.0] on days 85-112 (straddles the change). Because: Splits the strong X04-X06 set (E2 +36.2%) on the newest 28 days (85-112). The per-part skills test whether the decay hinted at by E2's last part (+8%) continues.
- E5: covariates ['X05'], reference [], 28 days, expected improves -> +16.0% [-1.7, +33.7] on days 85-112 (straddles the change). Because: Second single-member test of the X04-X06 set (E2), on the same days 85-112 so it is comparable with E4. Together with E2 this bounds X06's role and shows each member's trend over time.
Belief updates after these results (the next call's table): X04 (N5) promising -> rejected, X05 (R) promising -> deteriorated, X06 (N2) promising -> deteriorated.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (N1) rejected, X02 (D) rejected, X03 (N4) rejected, X04 (N5) rejected, X05 (R) deteriorated, X06 (N2) deteriorated, X07 (N3) rejected, X08 (E) rejected.
Notes (written with the requests): R1 (days 57-84, no-covariate reference): the X04-X06 set helped strongly (E2 +36.2%, CI +21.6 to +47.0). Its last part fell to +8%. X01-X03 (E1 +1.3%) and X07-X08 (E3 +5.2%) were null. R2 (days 85-112): X04 alone gave +6.0% (CI spans zero, flat per part). X05 alone gave +16.0%, but this came from the first part (+53.3%), then -7.6%, -0.8%, +14.0%. Reading: the strong X04-X06/X05 relationship held to about day 91 and then decayed. The system likely changed around days 84-92. So the E1/E3 nulls (days 57-84) are provisional and dated to the old regime. No dismissed candidate has been examined since the change. R3 plan: spend the last experiment re-screening the dismissed candidates on the newest 28 days (99-126), which all fall after the apparent change. Only 4 slots: X01, X02, X03, X07 are tested. X08 stays unexamined post-change, which the final call must acknowledge. X06 has never been tested alone. A group result will apply to the set, not to individual members.
- E6: covariates ['X01', 'X02', 'X03', 'X07'], reference [], 28 days, expected no_change -> +13.2% [-4.8, +27.2] on days 99-126 (after the change). Because: E4/E5 show the X04-X06/X05 signal decayed after about day 91, so the E1/E3 nulls are dated to the old regime. This re-screens the dismissed candidates on days 99-126, all post-change. Per-part skills show any emerging signal. Reference is none, comparable to E1-E5.
Belief updates after these results (the next call's table): X01 (N1) rejected -> promising, X02 (D) rejected -> promising, X03 (N4) rejected -> promising, X07 (N3) rejected -> promising.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (N1) promising, X02 (D) promising, X03 (N4) promising, X04 (N5) rejected, X05 (R) deteriorated, X06 (N2) deteriorated, X07 (N3) promising, X08 (E) rejected.
Notes (written with the requests): E1-E3 (days 57-84, no-covariate reference): the X04-X06 set was strong at +36.2%. The X01-X03 set (+1.3%) and the X07-X08 set (+5.2%) were null. E4-E5 (days 85-112): X04 alone gave +6.0%, small and flat. X05 alone was strong on days 85-91 (+53%), then about zero, then +14%. So the old signal decayed and the system likely changed around days 84-92. E6 (days 99-126, all post-change) re-screened the dismissed X01, X02, X03 and X07 as one set: +13.2%, CI -4.8 to +27.2, 18/10 days won. Per part: +0.1%, +22.4%, +9.4%, +18.9%. The pattern is consistent with a signal emerging after about day 105. This is set-level evidence only; no member is individually established. Gaps: X08 and X06 were never examined after the change. The E6 set was never tested with X05. X06 was never tested alone.
Final selection: ['X01', 'X02', 'X03', 'X07']
Conclusion: The X04-X06 relationship that dominated days 57-84 decayed after about day 91 (E4, E5), indicating a regime change. Re-screening the earlier-dismissed candidates on post-change days 99-126 (E6) found the set X01, X02, X03, X07 helping by +13.2%, positive in each of its last three weeks. The CI (-4.8 to +27.2) still spans zero, so this is suggestive, not conclusive. It is the only set with consistent post-change gains, so I select X01, X02, X03 and X07 as a set. This choice rests on set-level evidence: it does not show that each member is useful, and some may be inert. X04, X05 and X06 are excluded because their signal decayed, although X05's +14% on days 106-112 is noted. X08 was never examined after the change, so its exclusion is provisional and reflects a gap in the evidence.

### Comparator

Winning group in round 2: [X05 (R), X06 (N2), X07 (N3), X08 (E)].

- C1 (round 1): [X01 (N1), X02 (D), X03 (N4), X04 (N5)] vs none, 28 days -> +6.2% [-3.1, +13.6]
- C2 (round 1): [X05 (R), X06 (N2), X07 (N3), X08 (E)] vs none, 28 days -> +34.3% [+19.4, +46.0]
- C3 (round 2): [X01 (N1), X02 (D), X03 (N4), X04 (N5)] vs none, 28 days -> +14.1% [+3.5, +24.7]
- C4 (round 2): [X05 (R), X06 (N2), X07 (N3), X08 (E)] vs none, 28 days -> +25.1% [+5.4, +42.6]
- C5 (round 3): [X05 (R), X06 (N2)] vs none, 28 days -> -0.6% [-10.7, +8.4]
- C6 (round 3): [X07 (N3), X08 (E)] vs none, 28 days -> +19.4% [+2.4, +32.7]

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +36.9% [+21.8, +48.6] | +39.9% [+25.7, +50.9] |
| {R} vs {} | -5.2% [-17.5, +4.7] | +0.9% [-5.5, +6.8] |
| {D} vs {} | +30.6% [+16.1, +42.0] | +32.9% [+20.1, +43.6] |
| {E, D} vs {} | +32.0% [+14.7, +44.8] | +38.4% [+22.5, +50.2] |
| D given E ({E, D} vs {E}) | -7.8% [-19.4, +1.9] | -2.5% [-8.7, +3.2] |
| E given D ({E, D} vs {D}) | +2.0% [-5.9, +8.8] | +8.2% [-4.5, +16.9] |
| R given E ({E, R} vs {E}) | +1.5% [-5.8, +7.4] | -0.7% [-6.9, +5.4] |

## World w3: informative

First changed day 91. R = X02, E = X01, D = X06, N1 = X05, N2 = X07, N3 = X03, N4 = X08, N5 = X04.

Detectability (t0-beta, E alone vs no covariate): days 99-112 +35.1% [+16.0, +45.8]; days 99-126 +36.3% [+20.4, +48.3].

Integrity: clean.

| | L8 (lesson-only researcher) | fixed comparator |
|---|---|---|
| experiments used | 6 | 6 |
| first experiment E entered | E1 (round 1, as covariate) | C1 (round 1, as covariate) |
| E tested after the change (as a covariate, rounds 2-3) | yes (E3) | yes (C3) |
| E distinguished from its companions (E the only covariate, lower bound > 0) | no | no |
| supporting evidence of its own (criterion 5) | none | C5 |
| final selection | [X01 (E)] | [X01 (E), X02 (R)] |
| R removed | yes | no |
| noise selected | none | none |
| D selected | no | no |
| criteria 1-6 | 1:Y 2:Y 3:Y 4:Y 5:n 6:Y | 1:Y 2:Y 3:Y 4:n 5:Y 6:Y |
| SUCCESS | no | no |
| final selection vs {} on days 127-154 (t0-beta) | +29.3% [+17.4, +39.7] | +28.1% [+15.1, +39.1] |
| same, ridge (context only) | +33.1% [+15.3, +43.4] | +28.7% [+9.5, +40.4] |

D (X06): L8 final status rejected; L8 experiments including D: E2 ['X05', 'X06', 'X07', 'X08'] vs [] -7.8% [-15.8, +2.0]; E5 ['X05', 'X06', 'X07', 'X08'] vs [] +4.7% [-5.5, +13.0]. On confirmation, D alone -1.1% [-17.6, +12.6], D given E -4.8% [-14.8, +2.2].

L8 re-opened stale negatives: X01 (E) in E3; X02 (R) in E3; X03 (N3) in E4; X04 (N5) in E4; X05 (N1) in E5; X06 (D) in E5; X07 (N2) in E5; X08 (N4) in E5. Lesson mentions: 0. Tokens 29372; API attempts 4 (repairs 0, refusals 0).

### L8 trajectory

#### Call 1 (round 1, days 1-84); budget left after it: 4

Beliefs entering the round (written with its requests): X01 (E) untested, X02 (R) untested, X03 (N3) untested, X04 (N5) untested, X05 (N1) untested, X06 (D) untested, X07 (N2) untested, X08 (N4) untested.
Notes (written with the requests): Round 1 (days 1-84). There are no results yet. Plan: screen all eight candidates in two groups of 4 against a no-covariate reference over a 28-day window (days 57-84). This spends 2 of 6 experiments and keeps 4 for later rounds. Later budget goes to splitting any helpful group into individual candidates and to re-screening on recent data in case the system drifts, since it may not be stationary. Group results apply to the set only, not to individual members.
- E1: covariates ['X01', 'X02', 'X03', 'X04'], reference [], 28 days, expected improves -> +19.8% [-0.0, +33.9] on days 57-84 (before the change). Because: First-pass group screen of half the candidates against the target's own history. The 28-day window gives a usable interval and four 7-day parts, so a trend in skill over time would be visible.
- E2: covariates ['X05', 'X06', 'X07', 'X08'], reference [], 28 days, expected improves -> -7.8% [-15.8, +2.0] on days 57-84 (before the change). Because: Group screen of the other half under the same setup as E1, so the two groups are directly comparable. Weekly parts let me check stability within the window.
Belief updates after these results (the next call's table): X01 (E) untested -> promising, X02 (R) untested -> promising, X03 (N3) untested -> promising, X04 (N5) untested -> promising, X05 (N1) untested -> rejected, X06 (D) untested -> rejected, X07 (N2) untested -> rejected, X08 (N4) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (R) promising, X03 (N3) promising, X04 (N5) promising, X05 (N1) rejected, X06 (D) rejected, X07 (N2) rejected, X08 (N4) rejected.
Notes (written with the requests): Round 1, scoring days 57-84. E1 tested the set X01-X04 against no covariates: skill +19.8% (CI -0.0 to +33.9), 20/8 days won/lost, positive in 3 of 4 weeks (week 3 at -1.6%). The set looks helpful, but we do not know which members carry it. E2 tested the set X05-X08 against no covariates: skill -7.8% (CI -15.8 to +2.0), 9/19 won/lost, with the later weeks worse. That set did not help in this regime. This is a set-level and provisional result: it does not rule out a single useful member being masked by the others, and it says nothing about later days. Round 2 plan, scoring days 85-112: split E1 into pairs (X01+X02 and X03+X04) on the new data, and re-screen the X05-X08 set on the new data in case the system has drifted. One experiment is kept for round 3 to resolve individuals or to check for drift.
- E3: covariates ['X01', 'X02'], reference [], 28 days, expected improves -> +23.2% [+2.3, +37.1] on days 85-112 (straddles the change). Because: E1 showed X01-X04 helps as a set. Testing this pair on new data (days 85-112) shows whether the signal sits in X01/X02, and whether the E1 gain still holds out of sample.
- E4: covariates ['X03', 'X04'], reference [], 28 days, expected improves -> -0.6% [-13.2, +8.7] on days 85-112 (straddles the change). Because: This is the complement of E3 within the E1 set, using the same window and reference so the two pairs can be compared directly. Together they localise the E1 gain and check that it persists on days 85-112.
- E5: covariates ['X05', 'X06', 'X07', 'X08'], reference [], 28 days, expected no_change -> +4.7% [-5.5, +13.0] on days 85-112 (straddles the change). Because: E2 was null or harmful on days 57-84, but the system may be non-stationary. Re-screening on the newest days (85-112) checks whether that rejection still holds before it is relied on.
Belief updates after these results (the next call's table): X03 (N3) promising -> rejected, X04 (N5) promising -> rejected.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (R) promising, X03 (N3) rejected, X04 (N5) rejected, X05 (N1) rejected, X06 (D) rejected, X07 (N2) rejected, X08 (N4) rejected.
Notes (written with the requests): E1 (days 57-84): the set X01-X04 helped by +19.8%. E2: the set X05-X08 hurt by -7.8%. E3 (days 85-112): the pair X01+X02 scored +23.2% (CI +2.3 to +37.1), 19/9 days won/lost. That is a significant out-of-sample confirmation, positive in 3 of 4 weeks and +20.6% in the last week, so the favourite shows no clear decay. E4: the pair X03+X04 scored -0.6%, null. Its weeks went +21.8% then negative, a possible decay, but this is noisy. E5: the set X05-X08 scored +4.7% (CI -5.5 to +13.0), up from -7.8% in E2 but still null. Its weeks alternate (+17.9, -13.3, +18.5, -8.9), so it shows no consistent emerging signal. All rejections are provisional and dated to day 112 or earlier. Days 113-126 are unscreened for every candidate. Last experiment: X02 added to an X01 reference over days 99-126. This attributes the X01+X02 gain to individual members on the most recent data, including the 14 new days, and the weekly parts track drift.
- E6: covariates ['X02'], reference ['X01'], 28 days, expected no_change -> -3.9% [-8.5, +0.8] on days 99-126 (after the change). Because: E3 showed X01+X02 helps, but not which member carries it. Adding X02 to an X01 reference over days 99-126 shows whether X02 is needed beyond X01, and the final selection depends on that. The weekly parts cover the new days 113-126 and would show any decay. E5 gave no consistent sign of an emerging signal in X05-X08.
Belief updates after these results (the next call's table): X01 (E) promising -> accepted, X02 (R) promising -> redundant.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) accepted, X02 (R) redundant, X03 (N3) rejected, X04 (N5) rejected, X05 (N1) rejected, X06 (D) rejected, X07 (N2) rejected, X08 (N4) rejected.
Notes (written with the requests): E1 (days 57-84): the set X01-X04 scored +19.8% and the set X05-X08 (E2) scored -7.8%. E3 (days 85-112): X01+X02 scored +23.2%, with an interval above 0. E4: X03+X04 scored -0.6%, null. E5: X05-X08 scored +4.7%, null, with weeks alternating in sign. E6 (days 99-126): adding X02 to an X01 reference gave -3.9% (CI -8.5 to +0.8) and 13/15 days won/lost, so X02 adds nothing beyond X01. The X01-only reference MAE was 0.781 on days 99-126, far below the no-covariate MAE of about 1.15-1.19 in earlier windows. This suggests X01 still carries a strong signal and has not decayed, but no same-window no-covariate test confirms it. Days 113-126 were never re-screened for X03-X08, so their rejections are dated, provisional and mostly set-level.
Final selection: ['X01']
Conclusion: Select X01 only. The X01-X04 set helped on days 57-84 (E1), and X01+X02 helped significantly out of sample on days 85-112 (E3). On days 99-126, X02 added nothing beyond X01 (E6: -3.9%, CI -8.5 to +0.8), so X02 is redundant and is dropped to avoid noise. The X01-only error in E6 (MAE 0.781) is well below earlier no-covariate errors, which indicates X01's signal persisted through day 126 with no decay. Caveat: X01 was never scored alone against no covariates in the same window, so its individual value is inferred from E3 and E6 together. X03 and X04 (null pair, days 85-112) and X05-X08 (null set, days 57-112) remain excluded. These are provisional, dated, mostly group-level rejections: none was re-screened on days 113-126, so a late-emerging signal cannot be ruled out. Because the favourite showed no decay, the evidence for drift that would justify adding unverified candidates is weak.

### Comparator

Winning group in round 2: [X01 (E), X02 (R), X03 (N3), X04 (N5)].

- C1 (round 1): [X01 (E), X02 (R), X03 (N3), X04 (N5)] vs none, 28 days -> +19.8% [-0.0, +33.9]
- C2 (round 1): [X05 (N1), X06 (D), X07 (N2), X08 (N4)] vs none, 28 days -> -7.8% [-15.8, +2.0]
- C3 (round 2): [X01 (E), X02 (R), X03 (N3), X04 (N5)] vs none, 28 days -> +19.9% [+2.2, +32.9]
- C4 (round 2): [X05 (N1), X06 (D), X07 (N2), X08 (N4)] vs none, 28 days -> +4.7% [-5.5, +13.0]
- C5 (round 3): [X01 (E), X02 (R)] vs none, 28 days -> +33.8% [+18.7, +46.7]
- C6 (round 3): [X03 (N3), X04 (N5)] vs none, 28 days -> -3.0% [-14.2, +9.8]

### Confirmation (days 127-154)

| comparison | t0-beta | ridge (context) |
|---|---|---|
| {E} vs {} | +29.3% [+17.4, +39.7] | +33.1% [+15.3, +43.4] |
| {R} vs {} | -12.2% [-25.1, -0.4] | +1.0% [-11.2, +10.0] |
| {D} vs {} | -1.1% [-17.6, +12.6] | +13.7% [-9.8, +26.8] |
| {E, D} vs {} | +25.9% [+9.2, +38.1] | +25.7% [-0.2, +40.7] |
| D given E ({E, D} vs {E}) | -4.8% [-14.8, +2.2] | -11.0% [-20.6, -1.6] |
| E given D ({E, D} vs {D}) | +26.7% [+10.9, +41.1] | +14.0% [+4.1, +22.1] |
| R given E ({E, R} vs {E}) | -1.7% [-7.3, +3.3] | -6.6% [-17.3, +1.1] |

## Cost

- w1: L8 tokens 28445 ({'input_tokens': 7524, 'output_tokens': 7585, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}); API attempts 4; t0-beta forecasts: L8 238, comparator 238, evaluate 504.
- w2: L8 tokens 30346 ({'input_tokens': 7646, 'output_tokens': 9364, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}); API attempts 4; t0-beta forecasts: L8 238, comparator 238, evaluate 658.
- w3: L8 tokens 29372 ({'input_tokens': 7779, 'output_tokens': 8257, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}); API attempts 4; t0-beta forecasts: L8 238, comparator 238, evaluate 462.
- evaluate: 114.8 s.
