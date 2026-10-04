# learn1 paired hidden-world result: BOTH FAIL

Outcome row 4: neither found the emerging driver.

- One world and one trajectory per condition: an existence test, not a rate. The researcher is stochastic, so a difference between F and L can arise by chance as well as from the lesson.
- The outcome reads research behaviour first; a forecasting gain alone is not a learning signal.

learn1_spec_sha `35376d9c4c4739b324adc4895ba2a2ee3bd0ad283f2f5ff659b40017e0708340`; run 37218439239; commit 0c9ab856b043f815b8f516cfce6ed33f40e4193f; instrument theforecastingcompany/t0-beta @ c8885416fab935d604749a90cdcbf9b54fffcaeb (tfc-t0 0.5.0).

## The prior research lesson (condition L only)

When a relationship you relied on starts to decay, treat that as evidence that the system itself may have changed. A change in the system invalidates negative findings as much as positive ones. A null result describes one regime only. It says a factor did not help under the conditions in which it was tested. It does not say the factor will stay unhelpful once those conditions have shifted. If you see drift, mark every earlier rejection as provisional and dated, not settled. Then move budget away from repeatedly confirming the decline of the old favourite and towards re-screening previously dismissed factors on the most recent data, where an emerging signal would first show. Concluding that nothing works is safe only if every option has been examined after the change. Before calling a field empty, check whether your absence of evidence comes from the current regime or an outdated one.

sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`.

## Integrity

Issues: none. Call failures: F none; L none.

## Revealed world

First changed day 88. R = X04 (sign +1), E = X01 (sign -1), D = X03 (sign +1), N = X02 (sign -1).

Evidence check (t0-beta, against no covariate):

- R on days 57-84 (before the change): +13.3% [-0.4, +28.4]
- E on days 99-112 (available in round 2): +12.5% [+0.2, +25.9]
- E on days 99-126 (available in round 3): +23.6% [+10.2, +32.8]

## Side by side

| | F (fresh) | L (lesson) |
|---|---|---|
| final selection | ['X03'] | ['X01', 'X02', 'X03'] |
| found the emerging driver (E selected, R and N not) | no | no |
| first round with positive evidence for E | never | 2 |
| re-opened stale negatives | X03 (D) in E5, round 2 | X01 (E) in E5, round 2; X02 (N) in E5, round 2; X03 (D) in E5, round 2 |
| retired driver removed | yes | yes |
| unsupported noise avoided (B10) | yes | no |
| reconfirmations of R after a post-change R result | none | none |
| mentions of the lesson | 0 | 0 |
| beta1 reading | RESEARCHER FEASIBILITY FAILED | RESEARCHER FEASIBILITY FAILED |
| behaviours B1-B10 | B1 B2 B3 B4 B6 B8 B10 | B1 B2 B3 B4 B6 B8 B9 |
| tokens | 23064 | 25255 |

## Trajectory F (fresh)

#### Call 1 (round 1, days 1-84); budget left after it: 3

Beliefs entering the round (written with its requests): X01 (E) untested, X02 (N) untested, X03 (D) untested, X04 (R) untested.
Notes (written with the requests): Round 1 (days 1-84). No results yet. Plan: screen candidates one at a time against a no-covariate reference over 28-day windows. These windows have the most scored days and give per-week skill to check for drift. X01-X03 are screened now. X04 and re-tests of any winners (to check for non-stationarity) are deferred to rounds 2-3.
- E1: covariates ['X01'], reference [], 28 days, expected no_change -> -8.4% [-21.3, +3.9] on days 57-84 (before the change). Because: Individual screen of X01 against the target-only model. A 28-day window gives the tightest interval and lets per-week skill show drift. No prior evidence, so the expectation is neutral.
- E2: covariates ['X02'], reference [], 28 days, expected no_change -> -9.8% [-23.2, +2.4] on days 57-84 (before the change). Because: Individual screen of X02 against the target-only model, same design as the X01 screen so the results are comparable. No prior evidence.
- E3: covariates ['X03'], reference [], 28 days, expected no_change -> -10.6% [-23.7, +2.2] on days 57-84 (before the change). Because: Individual screen of X03 against the target-only model, same design. No prior evidence.
Belief updates after these results (the next call's table): X01 (E) untested -> rejected, X02 (N) untested -> rejected, X03 (D) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Beliefs entering the round (written with its requests): X01 (E) rejected, X02 (N) rejected, X03 (D) rejected, X04 (R) untested.
Notes (written with the requests): Round 1 (days 57-84 scored): X01, X02 and X03 were each screened alone against the no-covariate reference. All three had negative skill: X01 -8.4%, X02 -9.8%, X03 -10.6%. Every interval included zero, and each lost 17 of 28 days. None showed evidence of helping. In the last week (days 78-84) all three had small positive skill: X01 +3.4%, X02 +1.4%, X03 +8.1%. That could be noise or the start of a change in the process, so a fresh window is worth checking. Round 2 plan: screen X04 alone over 28 days (85-112). Re-test X03 alone over the same new window, since it had the largest late swing, to look for drift. Keep 1 experiment for round 3 to confirm any winner on days 113-126.
- E4: covariates ['X04'], reference [], 28 days, expected no_change -> +2.0% [-4.9, +8.7] on days 85-112 (straddles the change). Because: Individual screen of X04 with the same design as E1-E3 (alone, no reference, 28 days), now on days 85-112. There is no prior evidence about it.
- E5: covariates ['X03'], reference [], 28 days, expected no_change -> +5.1% [-2.9, +14.0] on days 85-112 (straddles the change). Because: Re-test of X03 on new data (days 85-112) to check for non-stationarity. E3 was negative overall, but its last week was +8.1%, the largest late swing of the three. Skill that turns positive here would point to a regime change.
Belief updates after these results (the next call's table): X03 (D) rejected -> promising, X04 (R) untested -> promising.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) rejected, X02 (N) rejected, X03 (D) promising, X04 (R) promising.
Notes (written with the requests): E1-E3 (days 57-84) screened X01, X02 and X03 alone against no covariates. All three were negative: X01 -8.4%, X02 -9.8%, X03 -10.6%. Each lost 17 of 28 days and every interval included zero. In the last week (78-84) all three turned slightly positive, and X03 most (+8.1%), which hinted at a possible regime change. E4 (days 85-112) screened X04 alone: +2.0% (interval -4.9% to +8.7%), 16/12 days, weekly results mixed (+3.6, +12.0, -7.1, +0.4). E5 re-tested X03 alone on days 85-112: +5.1% (interval -2.9% to +14.0%), 17/11 days, three of four weeks positive. X03 is now consistently positive from day 78 onward, which fits a regime change, but no interval excludes zero. Last experiment: re-test X03 alone over days 99-126. Weeks 3-4 of that window (113-126) are fresh data and confirm whether its benefit persists; the 28-day window keeps the interval tight. X04 is weaker and untested against X03, so it is unlikely to be added. X01 and X02 were tested only before the apparent change, so their rejection is somewhat tentative.
- E6: covariates ['X03'], reference [], 28 days, expected improves -> +2.6% [-6.1, +11.3] on days 99-126 (after the change). Because: Confirms X03 on fresh data. E5 gave +5.1% on days 85-112 and E3's last week was +8.1%. The window covers days 99-126: its last two weekly parts (113-126) are new data and show whether the benefit persists. 28 days gives a tighter interval than 14. X03 has the strongest case for final selection.
Belief updates after these results (the next call's table): none.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) rejected, X02 (N) rejected, X03 (D) promising, X04 (R) promising.
Notes (written with the requests): E1-E3 (days 57-84): X01, X02 and X03 each alone against no covariates were negative (-8.4%, -9.8%, -10.6%). Each lost 17 of 28 days and every interval included zero. In days 78-84 all three turned slightly positive, X03 most (+8.1%). E4 (85-112): X04 alone +2.0% (interval -4.9% to +8.7%), 16/12 days, weeks mixed. E5 (85-112): X03 alone +5.1% (interval -2.9% to +14.0%), 17/11 days. E6 (99-126): X03 alone +2.6% (interval -6.1% to +11.3%), 17/11 days. Its fresh weeks (113-119, 120-126) were +4.4% and +6.2%. E5 and E6 overlap on days 99-112, so they are not independent. Across the seven distinct weeks from day 78, X03 was positive in six (+8.1, +5.4, +16.1, -4.6, +5.4, +4.4, +6.2). This fits a regime change after about day 77 that made X03 modestly useful. However, no single interval excludes zero. X04 was never tested on fresh data or against X03. X01 and X02 were tested only before the apparent change.
Final selection: ['X03']
Conclusion: Select X03 only. Before about day 78 no candidate helped: X01-X03 alone all cost 8-11% (E1-E3). From day 78, X03 alone improved on the no-covariate model in 6 of 7 distinct weeks. E5 (85-112) gave +5.1% and E6 (99-126) gave +2.6%, each winning 17 of 28 days. Both fresh weeks, 113-126, were positive (+4.4%, +6.2%). This points to a regime in which X03 adds a small benefit that has persisted into the most recent data. The evidence is not conclusive: every interval includes zero, and E5 and E6 share days 99-112. Expect a gain of a few percent, not a large one. X04 showed only a weak, mixed +2.0% on days 85-112 and was never tested against X03 or on later data, so adding it is unsupported. X01 and X02 had no positive evidence and are excluded. Their rejection is tentative because they were tested only before the apparent regime change. Given the non-stationarity, X03's contribution should be monitored and dropped if weekly skill turns persistently negative.

## Trajectory L (lesson)

#### Call 1 (round 1, days 1-84); budget left after it: 3

Beliefs entering the round (written with its requests): X01 (E) untested, X02 (N) untested, X03 (D) untested, X04 (R) untested.
Notes (written with the requests): Round 1 (days 1-84). No evidence yet. Plan: screen candidates one at a time against a no-covariate reference over 28-day windows, so each claim rests on evidence about that candidate alone. Screen X01-X03 now and X04 in round 2. Save the remaining budget to re-check findings on the most recent data, because the process may drift.
- E1: covariates ['X01'], reference [], 28 days, expected no_change -> -8.4% [-21.3, +3.9] on days 57-84 (before the change). Because: Individual screen of X01 against a target-only forecast over days 57-84. A 28-day window gives a usable interval, and its 7-day parts show any drift. No prior evidence, so the neutral expectation is no change.
- E2: covariates ['X02'], reference [], 28 days, expected no_change -> -9.8% [-23.2, +2.4] on days 57-84 (before the change). Because: Individual screen of X02 against a target-only forecast over days 57-84, so its effect is isolated from the other candidates. No prior evidence, so the neutral expectation is no change.
- E3: covariates ['X03'], reference [], 28 days, expected no_change -> -10.6% [-23.7, +2.2] on days 57-84 (before the change). Because: Individual screen of X03 against a target-only forecast over days 57-84. X04 is deferred to round 2, keeping budget for re-screening recent data later.
Belief updates after these results (the next call's table): X01 (E) untested -> rejected, X02 (N) untested -> rejected, X03 (D) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Beliefs entering the round (written with its requests): X01 (E) rejected, X02 (N) rejected, X03 (D) rejected, X04 (R) untested.
Notes (written with the requests): Round 1 (days 57-84): X01, X02 and X03 were each screened alone against a target-only reference. All three were negative, at -8% to -11%, but every 95% interval included zero. Every one of them turned slightly positive in the last 7-day part (days 78-84): X01 +3.4%, X02 +1.4%, X03 +8.1%. This could be noise or the start of a regime change. The round-1 rejections are therefore provisional and dated to days 57-84. Round 2 plan has two parts. First, screen the untested X04 alone on days 85-112. Second, re-screen X01, X02 and X03 jointly on days 85-112 to look for an emerging signal. One experiment is held back for round 3, to separate members or to confirm on the most recent data.
- E4: covariates ['X04'], reference [], 28 days, expected no_change -> +2.0% [-4.9, +8.7] on days 85-112 (straddles the change). Because: X04 is the only candidate never examined. An individual screen against a target-only reference on the most recent 28 days (85-112) isolates its effect. There is no prior evidence about it, so the expectation is neutral.
- E5: covariates ['X01', 'X02', 'X03'], reference [], 28 days, expected no_change -> +15.0% [+4.5, +26.5] on days 85-112 (straddles the change). Because: E1-E3 rejected these on days 57-84 only, and all turned positive in the last part (days 78-84), a possible regime shift. This re-screens them on days 85-112. If the set helps, round 3 will separate the members. If it does not, all three are rejected for the current regime too.
Belief updates after these results (the next call's table): X01 (E) rejected -> promising, X02 (N) rejected -> promising, X03 (D) rejected -> promising, X04 (R) untested -> rejected.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (N) promising, X03 (D) promising, X04 (R) rejected.
Notes (written with the requests): Round 1 (days 57-84): X01, X02 and X03 were each screened alone against a target-only reference (E1-E3). All three were negative, at -8% to -11%, and every interval included zero. All three turned slightly positive in days 78-84, so those rejections were dated and provisional. Round 2 (days 85-112): X04 alone gave +2.0% (E4, interval -4.9% to +8.7%), which is not a demonstrated gain. The joint set X01+X02+X03 gave +15.0% (E5, interval +4.5% to +26.5%), with parts +9.5%, +23.0%, +23.7%, +2.7%. This fits a regime change in which the earlier nulls no longer hold. The evidence applies to the set, not to individual members. The last part of E5 fell to +2.7%, so the signal may be weakening, or that may be noise. Round 3 uses the last experiment to separate members: does X01+X02 add anything beyond X03? The 28-day window (days 99-126) covers the new days 113-126, and its per-part skills show whether the gain persists.
- E6: covariates ['X01', 'X02'], reference ['X03'], 28 days, expected no_change -> +21.5% [+2.4, +34.8] on days 99-126 (after the change). Because: E5 showed the set X01-X03 helps on days 85-112 but cannot attribute the gain. X03 is the leading suspect: it had the largest late uptick in E3. If X01+X02 add nothing beyond X03, select X03 alone; if they add, keep all three. The 28-day window (99-126) covers new days and tests persistence after E5's weak last part.
Belief updates after these results (the next call's table): none.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (E) promising, X02 (N) promising, X03 (D) promising, X04 (R) rejected.
Notes (written with the requests): Days 57-84 (E1-E3): X01, X02 and X03 were each tested alone against a target-only forecast. All were negative (-8% to -11%), every interval included zero, and all turned positive in days 78-84. Those rejections are provisional and apply only to that period. Days 85-112: X04 alone gave +2.0% (E4, interval -4.9% to +8.7%), so no gain is demonstrated. The set X01+X02+X03 gave +15.0% (E5, interval +4.5% to +26.5%), which suggests a regime change. Days 99-126: adding X01+X02 on top of X03 gave +21.5% (E6, interval +2.4% to +34.8%), positive in 3 of 4 parts, with +17.7% in the latest part, so the signal persists into the newest data. Open questions: the experiments never separate X01 from X02, never test X03 alone in the new regime, and never re-test X04 after day 112. The three-variable configuration was the candidate forecast in both E5 and E6, so it is the best-validated choice.
Final selection: ['X01', 'X02', 'X03']
Conclusion: Select X01, X02 and X03. The process appears to have changed around day 85. These candidates did not help on days 57-84 (E1-E3), but the set of all three helped on days 85-112 (+15%, E5). On the most recent days, 99-126, adding X01+X02 to X03 gave +21.5% (E6, interval +2.4% to +34.8%), and the latest part was still strongly positive. The full three-variable configuration was the candidate forecast in both E5 and E6, so it is the best-supported choice. Caveats: the evidence is about sets. X01 and X02 were never separated, and X03's own marginal value in the new regime was not isolated; it is kept because it belongs to the validated configuration. X04 is excluded because it showed no demonstrated gain on days 85-112 (E4). That exclusion is provisional, since X04 was not re-tested on the latest days. Because the process has already changed once, the selection should be re-checked as new data arrive.

## Candidates

| id | role | causal effect | t0-beta alone (127-154) | incremental | F final | F selected | L final | L selected |
|---|---|---|---|---|---|---|---|---|
| X01 | E | from the change on | +41.9% [+25.5, +53.6] | E given D: +16.1% [-6.1, +32.7] | rejected | False | promising | True |
| X02 | N | never | +2.2% [-8.8, +11.3] | N given E: +2.4% [-2.4, +7.7] | rejected | False | promising | True |
| X03 | D | never (proxy of E) | +27.1% [+10.2, +40.3] | D given E: -5.2% [-10.4, +1.2] | promising | True | promising | True |
| X04 | R | before the change only | -2.0% [-11.2, +5.9] | R given E: -0.5% [-5.1, +3.7] | promising | False | rejected | False |

## Confirmation (days 127-154; t0-beta and ridge)

| comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} | +41.9% [+25.5, +53.6] | +49.2% [+35.3, +56.3] |
| {R} vs {} | -2.0% [-11.2, +5.9] | -0.6% [-16.7, +12.2] |
| {D} vs {} | +27.1% [+10.2, +40.3] | +29.4% [+5.6, +46.4] |
| {N} vs {} | +2.2% [-8.8, +11.3] | -2.4% [-20.6, +13.1] |
| {E, D} vs {} | +38.8% [+23.0, +50.9] | +52.7% [+40.1, +59.9] |
| R given E ({E, R} vs {E}) | -0.5% [-5.1, +3.7] | -2.1% [-6.8, +3.2] |
| D given E ({E, D} vs {E}) | -5.2% [-10.4, +1.2] | +7.0% [-1.3, +15.8] |
| N given E ({E, N} vs {E}) | +2.4% [-2.4, +7.7] | +0.5% [-8.6, +10.2] |
| E given D ({E, D} vs {D}) | +16.1% [-6.1, +32.7] | +33.0% [+13.5, +44.6] |
| F's selection ['X03'] vs {} | +27.1% [+10.2, +40.3] | +29.4% [+5.6, +46.4] |
| L's selection ['X01', 'X02', 'X03'] vs {} | +36.6% [+20.6, +48.4] | +52.4% [+41.0, +58.8] |

## Cost

- F: API attempts 4 (refusals 0 [], repairs 0); tokens 23064 ({'input_tokens': 6254, 'output_tokens': 5422, 'cache_read_input_tokens': 11388, 'cache_creation_input_tokens': 0}); t0-beta forecasts 224.
- L: API attempts 4 (refusals 0 [], repairs 0); tokens 25255 ({'input_tokens': 6437, 'output_tokens': 6302, 'cache_read_input_tokens': 12516, 'cache_creation_input_tokens': 0}); t0-beta forecasts 238.
- evaluate: t0-beta forecasts 574; 24.1 s.
