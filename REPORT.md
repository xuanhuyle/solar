# policy1 paired hidden-world result: NO ARCHITECTURE SIGNAL

Outcome row 5.

- One world and one trajectory per condition: an existence test, not a rate. The researcher is stochastic, so a difference between L and S can arise by chance as well as from the architecture.
- The outcome reads research behaviour first; forecast accuracy alone is not an architecture signal.

policy1_spec_sha `544c2a8a56a01743d35df5ab9a963af51860f62f286e1086019e891dd6c5c497`; run 37229722055; commit c67cd6fabe5735ebd4b604aead9f0eab892e1f29; instrument theforecastingcompany/t0-beta @ c8885416fab935d604749a90cdcbf9b54fffcaeb (tfc-t0 0.5.0).

## Integrity

Issues: none. Call failures: L none; S none.

## Revealed world

First changed day 90. R = X01 (sign +1), E = X03 (sign +1), D = X04 (sign -1), N = X02 (sign -1).

Evidence check (t0-beta, against no covariate):

- R on days 57-84 (before the change): +40.9% [+32.7, +49.1]
- E on days 99-112 (available in round 2): +27.5% [+9.8, +42.0]
- E on days 99-126 (available in round 3): +32.0% [+20.8, +39.7]

## Side by side

| | L (lesson only) | S (structured state) |
|---|---|---|
| final selection | ['X03'] | ['X01', 'X02', 'X03', 'X04'] |
| found the emerging driver (E selected, R and N not) | yes | no |
| every selected member supported by its own test | yes | no (unsupported: ['X01', 'X02', 'X03', 'X04']) |
| essential loop (found, supported, confirmation lower bound > 0) | yes | no |
| first round with positive evidence for E | 3 | 3 |
| re-opened stale negatives | X03 (E) in E5; X04 (D) in E6 | X02 (N) in E5; X03 (E) in E5; X04 (D) in E5 |
| retired driver excluded | yes | no |
| unsupported noise avoided (B10) | yes | no |
| reconfirmations (sole re-tests after a post-change sole test) | none | none |
| last experiment | E6 single ['X04'] ref [] (lo +4.7%); tests a selected member alone: no | E6 group-conditional ['X02', 'X03', 'X04'] ref ['X01'] (lo +10.2%); tests a selected member alone: no |
| decision uncertainties left at the end (S's own list) | - | 3 |
| beta1 reading | BASIC AUTONOMOUS LOOP OBSERVED | RESEARCHER FEASIBILITY FAILED |
| tokens | 24024 | 40780 |

S's attribution entries after positive group results:

- after E6 ['X02', 'X03', 'X04'] (call 4 table): X02: grouped, Its share of the group gain is unknown; never tested individually after the change.; X03: grouped, Never tested individually; its share of the gain is unknown.; X04: grouped, Never tested individually; its share of the gain is unknown.

S's unresolved uncertainties at the end:

- U1: Which of X02, X03 and X04 carry the group gain seen in E5 and E6; no member was tested individually after the change. (matters: The set is selected whole. Some members may be useless or add noise, but dropping any member is untested.)
- U2: Whether X01 still adds value or only noise after its decay (E4 null, 20/8 days won). (matters: X01 is kept because the set was only tested with X01 as reference; removing it would be an untested configuration.)
- U3: Whether the post-change regime persists beyond day 126, or the system shifts again. (matters: The selection is used after day 126; a further change could invalidate the group signal as it did X01's.)

## Trajectory L (lesson only)

#### Call 1 (round 1, days 1-84); budget left after it: 4

Beliefs entering the round (written with its requests): X01 (R) untested, X02 (N) untested, X03 (E) untested, X04 (D) untested.
Notes (written with the requests): Round 1 (days 1-84). No results yet. Plan: screen the candidates in two pairs against a no-covariate reference over a 28-day window (days 57-84). Then split whichever pair shows skill into individual tests in round 2. I am keeping budget (4 of 6) so I can re-screen on the most recent data in rounds 2-3 in case the system drifts.
- E1: covariates ['X01', 'X02'], reference [], 28 days, expected improves -> +39.9% [+30.7, +48.4] on days 57-84 (before the change). Because: First screen of the X01/X02 pair against no covariates. The 28-day window gives a usable interval, and the per-week skill will show any trend within the window. A positive set result will need follow-up to attribute it to a member.
- E2: covariates ['X03', 'X04'], reference [], 28 days, expected no_change -> -6.0% [-20.0, +9.3] on days 57-84 (before the change). Because: Matching screen of the X03/X04 pair over the same window, so all four candidates are covered in round 1 with two experiments. That keeps budget for splitting pairs and for re-screening after any drift.
Belief updates after these results (the next call's table): X01 (R) untested -> promising, X02 (N) untested -> promising, X03 (E) untested -> rejected, X04 (D) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 2

Beliefs entering the round (written with its requests): X01 (R) promising, X02 (N) promising, X03 (E) rejected, X04 (D) rejected.
Notes (written with the requests): Round 1 (days 57-84). E1: the X01+X02 pair gave strong skill, +39.9% [30.7, 48.4], won 27 of 28 days and was positive in every week. This is set-level evidence only and does not yet say which member carries it. E2: the X03+X04 pair gave -6.0% [-20.0, +9.3], with the last week at -23.3%. That is a null-to-negative result, but it describes only the days 57-84 regime. Round 2 plan: split the X01/X02 pair on the newest 28 days (85-112). E3 tests X01 alone against no covariates. E4 tests X02 given X01, which shows whether X02 adds anything or is redundant. The per-week skill in both will also show any decay. I am holding 2 experiments for round 3 so I can re-screen X03/X04, and whichever pair member looks weak, on the most recent data (days 113-126) in case the system drifts.
- E3: covariates ['X01'], reference [], 28 days, expected improves -> +2.2% [-10.1, +12.7] on days 85-112 (straddles the change). Because: Splits E1: tests whether X01 alone carries skill on the newest data (days 85-112). The per-week skill will show whether the E1 relationship is holding or decaying.
- E4: covariates ['X02'], reference ['X01'], 28 days, expected no_change -> -1.5% [-5.2, +1.8] on days 85-112 (straddles the change). Because: Splits E1: tests whether X02 adds anything beyond X01 on days 85-112. Together with E3, this attributes E1's skill to individual members and shows whether X02 is redundant.
Belief updates after these results (the next call's table): X01 (R) promising -> deteriorated, X02 (N) promising -> deteriorated.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) deteriorated, X02 (N) deteriorated, X03 (E) rejected, X04 (D) rejected.
Notes (written with the requests): Days 57-84 (E1): the X01+X02 pair gave +39.9% [30.7, 48.4] and won 27 of 28 days. Days 85-112: X01 alone (E3) gave +2.2% [-10.1, +12.7], and X02 given X01 (E4) gave -1.5% [-5.2, +1.8]. So the strong E1 relationship has decayed. Neither member shows clear skill in the newer regime, which is evidence of drift. By the prior lesson, every earlier rejection is now provisional. X03 and X04 were only tested as a pair on days 57-84 (E2, -6.0%), which is the old regime. Round 3 plan: use the last 2 experiments to re-screen X03 and X04 individually against no covariates on the newest 28 days (99-126). Individual tests, rather than a pair, let me attribute any emerging signal. The per-week parts will show whether a signal appears in the most recent weeks.
- E5: covariates ['X03'], reference [], 28 days, expected no_change -> +32.0% [+20.8, +39.7] on days 99-126 (after the change). Because: E3/E4 show that the X01/X02 relationship from E1 decayed after day 84, so the system likely changed. X03 was dismissed only on old-regime data (E2, days 57-84). This re-screens it alone on the newest days (99-126), with per-week skill to catch an emerging signal.
- E6: covariates ['X04'], reference [], 28 days, expected no_change -> +18.0% [+4.7, +29.4] on days 99-126 (after the change). Because: This is the matching individual re-screen of X04 on days 99-126. E2 rejected the X03+X04 set only in the old regime and did not separate the members. Testing X04 separately lets any new signal be attributed to a single candidate before the final call.
Belief updates after these results (the next call's table): X03 (E) rejected -> accepted, X04 (D) rejected -> promising.

#### Call 4 (final call, days 1-126); budget left after it: 0

Beliefs entering the round (written with its requests): X01 (R) deteriorated, X02 (N) deteriorated, X03 (E) accepted, X04 (D) promising.
Notes (written with the requests): E1 (days 57-84): the X01+X02 pair gave +39.9% [30.7, 48.4] and won 27 of 28 days. E2 (days 57-84): the X03+X04 pair gave -6.0% [-20.0, +9.3], a null result in the old regime. E3/E4 (days 85-112): X01 alone gave +2.2% [-10.1, +12.7], and X02 given X01 gave -1.5% [-5.2, +1.8]. The old relationship decayed, which points to a regime change. Following the prior lesson, I re-screened the previously dismissed candidates individually on the newest data. E5 (days 99-126): X03 alone gave +32.0% [20.8, 39.7], won 24 of 28 days, and its weekly skill rose from +20.8% to +37.1%. E6 (days 99-126): X04 alone gave +18.0% [4.7, 29.4], won 19 of 28 days, and its weekly skill was uneven (one negative week). The E2 rejection is superseded for both. One gap remains: X04 was never tested given X03, so its skill may overlap with X03's. Budget is exhausted.
Final selection: ['X03']
Conclusion: The system appears to have changed after about day 84. The X01/X02 relationship that dominated days 57-84 (E1 +39.9%) decayed to near zero on days 85-112 (E3, E4). Re-screening the candidates dismissed in the old regime found an emerging signal on the newest data. X03 alone gave +32.0% [20.8, 39.7] on days 99-126 and was strengthening each week (E5). I select X03 as the most clearly supported covariate for the current regime. X04 also showed individual skill (+18.0% [4.7, 29.4], E6), but it was weaker and more erratic. It was never tested given X03, so its incremental value is unknown and it could be redundant; E4 shows that adding a redundant covariate can slightly hurt. I therefore leave X04 out, but it is the first candidate to test as an addition to X03. X01 and X02 are excluded as deteriorated. Given the observed drift, all conclusions are dated to days 99-126 and should be re-checked as new data arrive.

## Trajectory S (structured research state)

#### Call 1 (round 1, days 1-84); budget left after it: 3

Notes (written with the requests): Call 1, days 1-84 observed, no results yet. Plan: screen all four candidates on the last 28 days (days 57-84) with 3 experiments. X01 and X02 are tested alone against no reference. X03 and X04 are tested as a pair; if the pair helps, a later round separates them. The per-week skills will be used to watch for drift. I am keeping 3 experiments for rounds 2-3, to re-screen on recent data and to attribute effects within groups.
Regime assessment: **unknown** (cites none): No experiments have been run yet, so stationarity cannot be judged.
Decision uncertainties: U1: Whether X01 or X02 alone improves the day-ahead forecast over no covariates. (matters: It decides which single candidates enter the final selection.) | U2: Whether X03 and/or X04 add skill, and which member of the pair is responsible. (matters: A positive result for the pair does not establish that each member is useful, so attribution is needed before either is selected.) | U3: Whether relationships are stable over time or drift by days 112-126. (matters: The selection is used after day 126, so the evidence must describe the latest regime.)
Budget needs: After this round, 3 experiments remain: one or two to separate any group effect and to check interactions, and at least one recent re-screen to detect drift before the final call.
Candidates (entering the round):
- X01 (R): untested; freshness unknown; evidence none; last scored day -; attribution: Not yet tested.
- X02 (N): untested; freshness unknown; evidence none; last scored day -; attribution: Not yet tested.
- X03 (E): untested; freshness unknown; evidence none; last scored day -; attribution: Will be tested only as part of a pair with X04 at first.
- X04 (D): untested; freshness unknown; evidence none; last scored day -; attribution: Will be tested only as part of a pair with X03 at first.
- E1: covariates ['X01'], reference [], 28 days, targets U1 -> +40.9% [+32.7, +49.1] on days 57-84 (before the change). Because: This is a direct screen of X01 alone against a no-covariate forecast over days 57-84. The per-week skills will show any trend. I have no prior expectation. Follow-up: If positive, test X01 conditionally against other helpful candidates and re-check it on recent data. If null, re-screen it later in case the regime changes. If ambiguous, extend the test in round 2. Budget: A direct single-candidate screen gives clean attribution, and a 28-day window gives a usable confidence interval.
- E2: covariates ['X02'], reference [], 28 days, targets U1 -> -4.6% [-15.1, +6.0] on days 57-84 (before the change). Because: This is a direct screen of X02 alone over days 57-84, run in parallel with X01 so their effects can be compared on the same days. Follow-up: If positive, test X02 conditionally on X01 if both help, to check for redundancy. If null, re-screen it later in case the regime changes. Budget: A single-candidate screen gives clean attribution, and testing early leaves time to track drift.
- E3: covariates ['X03', 'X04'], reference [], 28 days, targets U2 -> -6.0% [-20.0, +9.3] on days 57-84 (before the change). Because: This is a grouped screen of X03 and X04 over days 57-84, which covers the remaining candidates with one experiment and saves budget. A null result would cover both candidates for this regime only. Follow-up: If positive, test X03 alone, or X04 conditional on X03, to attribute the effect. If null, mark both as provisionally rejected and re-screen them on recent data if drift appears. Budget: Pairing these two saves one experiment that can later be spent on attribution or on a recent re-screen.
Belief updates after these results: X01 (R) untested -> promising, X02 (N) untested -> rejected, X03 (E) untested -> rejected, X04 (D) untested -> rejected.

#### Call 2 (round 2, days 1-112); budget left after it: 1

Notes (written with the requests): Round 1 (days 57-84). E1: X01 alone gave +40.9% skill (CI +32.7 to +49.1), won 26/28 days, and was steady across all four weeks. E2: X02 alone gave -4.6% (CI -15.1 to +6.0), a null. E3: the X03+X04 pair gave -6.0% (CI -20.0 to +9.3), also a null; its last week was -23.3%, likely noise. All nulls are dated to days 57-84 and are provisional. Round 2 plan: (E4) re-test X01 alone on the new days 85-112 to check that its effect persists. (E5) re-screen X02, X03 and X04 together, conditional on X01, on days 85-112, because that is the decision-relevant question if X01 is kept. One experiment is held back for round 3, to attribute any group effect or to re-check drift on days 113-126.
Regime assessment: **stable** (cites E1, E2, E3): X01's skill was steady across all weeks of days 57-84 and the other candidates were flat; this rests on a single 28-day window and is unverified for days 85-112.
Decision uncertainties: U1: Whether X01's strong effect seen on days 57-84 persists on days 85-112 and later. (matters: X01 is the only candidate supported so far. If its effect decays, the selection and the regime assessment both change.) | U2: Whether X02, X03 or X04 add skill on recent data, given X01 (their nulls rest only on days 57-84). (matters: An emerging signal would be missed if the old nulls were treated as settled; a group gain would need attribution before selection.) | U3: Whether a regime change occurs within days 113-126, just before the forecast period. (matters: The final selection is used after day 126, so the latest evidence must describe the current process.)
Budget needs: After E4-E5, one experiment remains for round 3: either to attribute a positive group effect from E5 or to re-check X01 and the others on days 113-126 if drift appears.
Candidates (entering the round):
- X01 (R): promising; freshness possibly_stale; evidence direct; last scored day 84; attribution: Persistence after day 84 is unverified.
- X02 (N): rejected; freshness possibly_stale; evidence direct; last scored day 84; attribution: Not tested on recent data, nor conditional on X01.
- X03 (E): rejected; freshness possibly_stale; evidence grouped; last scored day 84; attribution: Evidence is grouped with X04; its individual effect is unknown.
- X04 (D): rejected; freshness possibly_stale; evidence grouped; last scored day 84; attribution: Evidence is grouped with X03; its individual effect is unknown.
- E4: covariates ['X01'], reference [], 28 days, targets U1 -> +2.2% [-10.1, +12.7] on days 85-112 (straddles the change). Because: E1 showed +40.9% skill, steady across weeks. Re-testing X01 directly on the new days 85-112 checks whether the effect persists; the per-week skills will reveal any decay. Follow-up: If positive, keep X01 and use it as the reference in later tests. If decaying, re-screen the others without X01 in round 3. If ambiguous, re-check on days 113-126. Budget: X01 is the only supported candidate, so confirming it on fresh data is the most decision-relevant test.
- E5: covariates ['X02', 'X03', 'X04'], reference ['X01'], 28 days, targets U2 -> +16.5% [-0.5, +34.9] on days 85-112 (straddles the change). Because: E2 and E3 were nulls on days 57-84 only. This re-screens all three dismissed candidates on recent data, conditional on X01 (the likely final base), so that an emerging signal is caught. Follow-up: If positive, use round 3 to attribute the gain to a single member. If null, the rejections are updated to days 85-112. If X01 decays in E4, re-screen without the X01 reference. Budget: One experiment covers all three dismissed candidates on recent data and leaves one experiment for attribution or a drift check.
Belief updates after these results: X01 (R) promising -> deteriorated, X02 (N) rejected -> promising, X03 (E) rejected -> promising, X04 (D) rejected -> promising.

#### Call 3 (round 3, days 1-126); budget left after it: 0

Notes (written with the requests): Round 1 (days 57-84): E1 X01 alone +40.9% (CI +32.7 to +49.1), steady. E2 X02 alone -4.6% (null). E3 X03+X04 -6.0% (null). Round 2 (days 85-112): E4 X01 alone fell to +2.2% (CI -10.1 to +12.7), so its effect collapsed. E5 X02+X03+X04 given X01 gave +16.5% (CI -0.5 to +34.9), with weeks +2.4, +36.7, +21.2, -4.6. So the system likely changed after day 84: the old favourite decayed and the previously dismissed group now shows a possible signal. The old nulls (E2, E3) describe days 57-84 only. Round 3, last experiment: re-test the three-candidate set conditional on X01 over days 99-126. This window adds the fresh days 113-126 and has enough power to judge the set. With one experiment, attribution within the set cannot be finished. If the set holds, it would be selected as a set and flagged as unattributed.
Regime assessment: **changed** (cites E1, E4, E5): X01 skill dropped from +40.9% (days 57-84) to +2.2% (days 85-112), while the previously null group X02-X04 rose to +16.5% given X01.
Decision uncertainties: U1: Whether the X02+X03+X04 gain seen in E5 (marginal CI, last week -4.6%) persists through days 113-126. (matters: It decides whether the set enters the final selection used after day 126.) | U2: Which members of X02, X03 and X04 carry the E5 gain. (matters: Selecting the whole set may add useless or noisy inputs, but with one experiment left full attribution is impossible.) | U3: Whether X01 still adds anything or now only adds noise after its decay. (matters: It decides whether X01 is kept as the base of the selection.)
Budget needs: The one remaining experiment should confirm or refute the group signal on the freshest days; member attribution and X01's residual value will stay partly unresolved.
Candidates (entering the round):
- X01 (R): deteriorated; freshness current; evidence direct; last scored day 112; attribution: Residual value after day 112 is unclear.
- X02 (N): promising; freshness possibly_stale; evidence grouped; last scored day 112; attribution: Its share of the E5 group gain is unknown.
- X03 (E): promising; freshness possibly_stale; evidence grouped; last scored day 112; attribution: Never tested individually; its share of the gain is unknown.
- X04 (D): promising; freshness possibly_stale; evidence grouped; last scored day 112; attribution: Never tested individually; its share of the gain is unknown.
- E6: covariates ['X02', 'X03', 'X04'], reference ['X01'], 28 days, targets U1 -> +29.0% [+10.2, +40.8] on days 99-126 (after the change). Because: E5 showed +16.5% for this set given X01, but its CI just touched zero and its last week was -4.6%. Re-testing on days 99-126 adds the fresh days 113-126. Its per-week skills show whether the post-change signal holds, so the final decision on the set rests on the newest regime. Follow-up: If positive, select X01 plus the set, flagged as unattributed. If null or negative, select X01 only or nothing. If ambiguous, weigh the latest weekly skills. No budget remains for any follow-up. Budget: Whether the set helps after day 112 is the most decision-relevant open question; attribution cannot be completed with one experiment anyway.
Belief updates after these results: none.

#### Call 4 (final call, days 1-126); budget left after it: 0

Notes (written with the requests): Round 1 (days 57-84): E1 X01 alone +40.9% (CI +32.7 to +49.1), steady. E2 X02 alone -4.6% (null). E3 X03+X04 -6.0% (null). Round 2 (days 85-112): E4 X01 alone fell to +2.2% (CI -10.1 to +12.7), so its effect collapsed. E5 X02+X03+X04 given X01 gave +16.5% (CI -0.5 to +34.9). Round 3 (days 99-126): E6 re-tested the same set given X01 and got +29.0% (CI +10.2 to +40.8), winning 22 of 28 days. Its weekly skills were +21.2, -4.6, +43.3 and +42.2; the last two weeks are the fresh days 113-126. So the regime changed after day 84. X01 decayed, and the previously dismissed group now carries a clear, strengthening signal. The old nulls (E2, E3) describe days 57-84 only. The supported configuration is X01 plus X02+X03+X04, which E6 measured directly against X01 alone. The individual roles of X02, X03 and X04 were never separated, and X01's residual value is unclear.
Regime assessment: **changed** (cites E1, E4, E5, E6): X01 skill fell from +40.9% (days 57-84) to +2.2% (days 85-112), while the previously null X02-X04 set rose to +16.5% and then +29.0%, with about +43% on days 113-126.
Decision uncertainties: U1: Which of X02, X03 and X04 carry the group gain seen in E5 and E6; no member was tested individually after the change. (matters: The set is selected whole. Some members may be useless or add noise, but dropping any member is untested.) | U2: Whether X01 still adds value or only noise after its decay (E4 null, 20/8 days won). (matters: X01 is kept because the set was only tested with X01 as reference; removing it would be an untested configuration.) | U3: Whether the post-change regime persists beyond day 126, or the system shifts again. (matters: The selection is used after day 126; a further change could invalidate the group signal as it did X01's.)
Budget needs: No budget remains. Attribution within X02-X04 and X01's residual value are left unresolved and should be checked first if more experiments become possible.
Candidates (entering the round):
- X01 (R): deteriorated; freshness current; evidence direct; last scored day 112; attribution: Residual value after day 112 untested; it may contribute nothing in the current regime.
- X02 (N): promising; freshness current; evidence grouped; last scored day 126; attribution: Its share of the group gain is unknown; never tested individually after the change.
- X03 (E): promising; freshness current; evidence grouped; last scored day 126; attribution: Never tested individually; its share of the gain is unknown.
- X04 (D): promising; freshness current; evidence grouped; last scored day 126; attribution: Never tested individually; its share of the gain is unknown.
Final selection: ['X01', 'X02', 'X03', 'X04']
Conclusion: The process changed after day 84. X01, strongly useful on days 57-84 (E1), decayed to a null on days 85-112 (E4). Meanwhile the earlier-dismissed X02, X03 and X04, whose nulls dated from the old regime, added skill given X01: +16.5% (E5) and then +29.0% on days 99-126 (E6, CI +10.2 to +40.8). E6 reached about +43% on the freshest days 113-126. I select X01+X02+X03+X04, the configuration directly validated on the most recent data. X01 is retained as the reference base under which the set was tested, not because it helps on its own now. Caveats: the gain is attributed to the X02-X04 set only, and no individual member is established as useful. X01 may now be dead weight. The regime could shift again. If more budget were available, the first steps would be to test each of X02-X04 conditional on the others and to test the set without X01.

## Candidates

| id | role | causal effect | t0-beta alone (127-154) | incremental | L final | L selected | S final | S selected |
|---|---|---|---|---|---|---|---|---|
| X01 | R | before the change only | -12.4% [-22.8, -3.5] | R given E: -1.0% [-7.9, +5.9] | deteriorated | False | deteriorated | True |
| X02 | N | never | -6.0% [-17.5, +3.7] | N given E: -3.1% [-8.9, +2.8] | deteriorated | False | promising | True |
| X03 | E | from the change on | +30.7% [+22.7, +37.9] | E given D: +22.8% [+12.9, +30.3] | accepted | True | promising | True |
| X04 | D | never (proxy of E) | +4.5% [-15.2, +21.3] | D given E: -6.4% [-15.1, +1.4] | promising | False | promising | True |

## Confirmation (days 127-154; t0-beta and ridge)

| comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} | +30.7% [+22.7, +37.9] | +32.6% [+20.9, +44.1] |
| {R} vs {} | -12.4% [-22.8, -3.5] | +1.3% [-4.6, +7.5] |
| {D} vs {} | +4.5% [-15.2, +21.3] | +6.0% [-4.9, +15.6] |
| {N} vs {} | -6.0% [-17.5, +3.7] | +3.9% [-4.5, +13.9] |
| {E, D} vs {} | +26.3% [+16.6, +34.5] | +35.3% [+27.0, +42.8] |
| R given E ({E, R} vs {E}) | -1.0% [-7.9, +5.9] | +1.9% [-5.9, +7.9] |
| D given E ({E, D} vs {E}) | -6.4% [-15.1, +1.4] | +4.0% [-5.9, +11.6] |
| N given E ({E, N} vs {E}) | -3.1% [-8.9, +2.8] | -4.7% [-13.3, +2.5] |
| E given D ({E, D} vs {D}) | +22.8% [+12.9, +30.3] | +31.2% [+22.4, +40.0] |
| L's selection ['X03'] vs {} | +30.7% [+22.7, +37.9] | +32.6% [+20.9, +44.1] |
| S's selection ['X01', 'X02', 'X03', 'X04'] vs {} | +26.8% [+15.9, +35.8] | +37.2% [+28.7, +44.5] |

## Cost

- L: API attempts 4 (refusals 0 [], repairs 0); tokens 24024 ({'input_tokens': 5852, 'output_tokens': 5656, 'cache_read_input_tokens': 12516, 'cache_creation_input_tokens': 0}); t0-beta forecasts 238.
- S: API attempts 4 (refusals 0 [], repairs 0); tokens 40780 ({'input_tokens': 10831, 'output_tokens': 9425, 'cache_read_input_tokens': 20524, 'cache_creation_input_tokens': 0}); t0-beta forecasts 224.
- evaluate: t0-beta forecasts 602; 39.5 s.
