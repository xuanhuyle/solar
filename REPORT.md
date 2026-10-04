# policy1 regression replays (engineering check, not evidence)

Contaminated by our knowledge of these worlds; never reported as validation.

## beta1 replay: operational PASS

Published roles (not shown to the researcher): R = X03, E = X02, D = X01, N = X04; first changed day 88.

Replayed results equal the published ones: True. Live calls 2 (valid 2); attempts 2; repairs 0; refusals 0; prompt rebuild mismatches none; tokens 17645; t0-beta forecasts 238; failure None.

### The notebook S produced (replayed evidence, then its own calls), verbatim

```
=== Call 1: round 1, days 1-84 observed (replayed: evidence from an earlier investigation; no research state was recorded) ===
Experiments run:
- E1: covariates [X01], reference [none], window 28 days
  Result E1: scored days 57-84; reference MAE 0.970; candidate MAE 1.008; skill -3.9% (95% interval -12.4% to +5.5%); days won/lost/tied 14/14/0; skill per 7-day part: -13.2%, +9.0%, -5.3%, -9.5%
- E2: covariates [X02], reference [none], window 28 days
  Result E2: scored days 57-84; reference MAE 0.970; candidate MAE 1.024; skill -5.5% (95% interval -13.9% to +3.2%); days won/lost/tied 13/15/0; skill per 7-day part: -13.5%, +4.7%, -5.5%, -10.4%
- E3: covariates [X03], reference [none], window 28 days
  Result E3: scored days 57-84; reference MAE 0.970; candidate MAE 0.798; skill +17.8% (95% interval +9.8% to +26.6%); days won/lost/tied 18/10/0; skill per 7-day part: +31.8%, +14.9%, +15.9%, +10.0%

=== Call 2: round 2, days 1-112 observed (replayed: evidence from an earlier investigation; no research state was recorded) ===
Experiments run:
- E4: covariates [X04], reference [none], window 28 days
  Result E4: scored days 85-112; reference MAE 1.395; candidate MAE 1.397; skill -0.1% (95% interval -7.4% to +6.4%); days won/lost/tied 12/16/0; skill per 7-day part: -2.1%, +0.6%, -1.0%, +2.9%
- E5: covariates [X03], reference [none], window 28 days
  Result E5: scored days 85-112; reference MAE 1.395; candidate MAE 1.355; skill +2.8% (95% interval -4.8% to +10.7%); days won/lost/tied 15/13/0; skill per 7-day part: +7.5%, +4.8%, -0.7%, +0.3%

=== Call 3: round 3, days 1-126 observed ===
Notes: E1-E3 (days 57-84): X03 helped clearly (+17.8%, CI +9.8 to +26.6). X01 (-3.9%) and X02 (-5.5%) did not help. E4 (days 85-112): X04 null (-0.1%). E5 (days 85-112): X03 fell to +2.8% (CI includes 0), with per-week skill sliding to about 0. The no-covariate reference MAE also jumped from 0.970 to 1.395. Together these suggest a regime change near day 85. So the X01/X02 rejections date from the old regime and are only provisional. No experiment has yet scored days 113-126. I am spending the last experiment on re-screening X01+X02 on the most recent 28 days rather than re-confirming X03's decline.
Regime assessment: possible_change; cites: E3, E5, E1, E4; justification: X03 skill decayed from +17.8% to +2.8% and the baseline error rose by 44% between days 57-84 and 85-112, consistent with a shift in the process around day 85.
Decision uncertainties:
- U1: Whether X01 and/or X02, rejected only on pre-change days 57-84, help in the new regime (days 99-126). Why it matters: An emerging signal in a previously dismissed candidate would be the only basis for selecting anything after day 126.
- U2: Whether X03 retains any skill after day 112 or has fully decayed. Why it matters: It decides whether the former favourite stays in the final selection.
- U3: Whether X04's null on days 85-112 persists through days 113-126. Why it matters: X04 was tested only once, early in the new regime; a late-emerging effect would be missed.
Budget needs: With one experiment left, re-screen X01+X02 on days 99-126; X03 and X04 for days 113-126 must be judged from existing evidence.
Beliefs:
- X01: rejected; cites: E1; reason: No skill on days 57-84 (-3.9%, CI -12.4 to +5.5). The rejection is provisional, dated to the pre-change regime, and is being re-screened.; freshness: stale; evidence: direct; last scored day: 84; attribution: Untested after the suspected change near day 85.
- X02: rejected; cites: E2; reason: No skill on days 57-84 (-5.5%, CI -13.9 to +3.2). The rejection is provisional, dated to the pre-change regime, and is being re-screened.; freshness: stale; evidence: direct; last scored day: 84; attribution: Untested after the suspected change near day 85.
- X03: deteriorated; cites: E3, E5; reason: Strong on days 57-84 (+17.8%) but only +2.8% (CI includes 0) on days 85-112. Per-week skill fell to roughly 0 by days 99-112.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Unknown whether any skill remains after day 112.
- X04: rejected; cites: E4; reason: Null on days 85-112 (-0.1%, CI -7.4 to +6.4), with all weekly parts near 0. This was tested in the new regime but not on the latest 14 days.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Not tested on days 113-126.
Experiments requested:
- E6: covariates [X01, X02], reference [none], window 28 days; expected: no_change; because: X01 and X02 were rejected only on pre-change days (E1, E2). E3 to E5 suggest a regime shift near day 85, so those nulls may not hold. Re-screening both on days 99-126 checks for an emerging signal; the per-week parts show the latest weeks.; targets: U1; possible follow-up: No budget remains. If positive, consider selecting the pair (attribution between X01 and X02 stays unresolved). If null, select none or reconsider X03. If ambiguous, rely on the latest weekly parts.; budget rationale: Two candidates have never been examined after the change, so this covers the largest unscreened area. Combining them is the only way to cover both with one experiment.
  Result E6: scored days 99-126; reference MAE 1.459; candidate MAE 0.902; skill +38.2% (95% interval +27.0% to +48.7%); days won/lost/tied 24/4/0; skill per 7-day part: +38.5%, +30.0%, +22.9%, +53.3%

=== Call 4: final call, days 1-126 observed ===
Notes: E1-E3 (days 57-84): X03 helped (+17.8%), while X01 (-3.9%) and X02 (-5.5%) did not. E4 (days 85-112): X04 was null (-0.1%). E5 (days 85-112): X03 decayed to +2.8% (CI includes 0) and the baseline MAE rose from 0.970 to 1.395, pointing to a regime change near day 85. Following the lesson that nulls are regime-specific, E6 re-screened X01+X02 on days 99-126. The pair gave +38.2% (CI +27.0 to +48.7), won 24 of 28 days, and was strong in every week, including +53.3% in the last week. The old regime's rejections of X01/X02 do not hold now. Attribution within the pair is unresolved, because they were only tested together.
Regime assessment: changed; cites: E3, E5, E1, E2, E6; justification: X03 went from clear skill to roughly none and the baseline error rose 44%. X01+X02, null on days 57-84, became strongly useful on days 99-126, so the process changed around day 85.
Decision uncertainties:
- U1: Whether X01, X02 or both drive E6's +38.2% skill; they were never separated after the change. Why it matters: Selecting both may carry a redundant or harmful member. Dropping either risks losing the signal, so the pair is kept as a set.
- U2: Whether X03 has any skill after day 112; it was last scored on days 85-112 with near-zero weekly skill. Why it matters: Excluding X03 rests on evidence 14 days old. A residual effect would be missed, though its trend was downward.
- U3: Whether X04 stays null after day 112, or adds anything on top of X01+X02. Why it matters: X04 is excluded on one null test scored up to day 112. A late-emerging effect would be missed.
Budget needs: No experiments remain. Separating X01 from X02, and rechecking X03 and X04 on days 113-126, would have been the next steps.
Beliefs:
- X01: promising; cites: E1, E6; reason: Null on days 57-84 (E1, old regime). As part of X01+X02 it gave +38.2% on days 99-126 (E6), consistent across all weeks. The old rejection is superseded. The individual contribution is unproven.; freshness: current; evidence: grouped; last scored day: 126; attribution: Tested only jointly with X02 after the change; its own share of the skill is unknown.
- X02: promising; cites: E2, E6; reason: Null on days 57-84 (E2, old regime). As part of X01+X02 it gave +38.2% on days 99-126 (E6), with a CI well above 0. The individual contribution is unproven.; freshness: current; evidence: grouped; last scored day: 126; attribution: Tested only jointly with X01 after the change; its own share of the skill is unknown.
- X03: deteriorated; cites: E3, E5; reason: +17.8% on days 57-84 fell to +2.8% (CI includes 0) on days 85-112, with weekly skill near 0 by the end.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Not scored after day 112; any residual or conditional value given X01+X02 is unknown.
- X04: rejected; cites: E4; reason: Null on days 85-112 (-0.1%, CI -7.4 to +6.4), with all weekly parts near 0. This was tested in the new regime, but only once.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Not tested on days 113-126 or conditional on X01+X02.
Final selection: [X01, X02]
Conclusion: The process changed around day 85. X03, the old favourite, lost its skill, and X01+X02, dismissed in the old regime, became strongly useful on the latest data (E6: +38.2%, CI +27.0 to +48.7, 24/28 days won, +53.3% in the final week). I select X01 and X02 together, because the evidence supports the set, not each member. Which of them carries the signal is unresolved, and keeping both avoids dropping the true driver. X03 is excluded as deteriorated and X04 as null, both on evidence scored only up to day 112. These exclusions are dated and provisional. Further drift is possible, so performance should be monitored.

```

## learn1 replay: operational PASS

Published roles (not shown to the researcher): R = X04, E = X01, D = X03, N = X02; first changed day 88.

Replayed results equal the published ones: True. Live calls 2 (valid 2); attempts 2; repairs 0; refusals 0; prompt rebuild mismatches none; tokens 18318; t0-beta forecasts 224; failure None.

### The notebook S produced (replayed evidence, then its own calls), verbatim

```
=== Call 1: round 1, days 1-84 observed (replayed: evidence from an earlier investigation; no research state was recorded) ===
Experiments run:
- E1: covariates [X01], reference [none], window 28 days
  Result E1: scored days 57-84; reference MAE 1.091; candidate MAE 1.183; skill -8.4% (95% interval -21.3% to +3.9%); days won/lost/tied 11/17/0; skill per 7-day part: -10.8%, -6.4%, -17.1%, +3.4%
- E2: covariates [X02], reference [none], window 28 days
  Result E2: scored days 57-84; reference MAE 1.091; candidate MAE 1.198; skill -9.8% (95% interval -23.2% to +2.4%); days won/lost/tied 11/17/0; skill per 7-day part: -12.2%, +3.0%, -28.2%, +1.4%
- E3: covariates [X03], reference [none], window 28 days
  Result E3: scored days 57-84; reference MAE 1.091; candidate MAE 1.207; skill -10.6% (95% interval -23.7% to +2.2%); days won/lost/tied 11/17/0; skill per 7-day part: -13.3%, -17.0%, -15.9%, +8.1%

=== Call 2: round 2, days 1-112 observed (replayed: evidence from an earlier investigation; no research state was recorded) ===
Experiments run:
- E4: covariates [X04], reference [none], window 28 days
  Result E4: scored days 85-112; reference MAE 1.115; candidate MAE 1.093; skill +2.0% (95% interval -4.9% to +8.7%); days won/lost/tied 16/12/0; skill per 7-day part: +3.6%, +12.0%, -7.1%, +0.4%
- E5: covariates [X01, X02, X03], reference [none], window 28 days
  Result E5: scored days 85-112; reference MAE 1.115; candidate MAE 0.948; skill +15.0% (95% interval +4.5% to +26.5%); days won/lost/tied 18/10/0; skill per 7-day part: +9.5%, +23.0%, +23.7%, +2.7%

=== Call 3: round 3, days 1-126 observed ===
Notes: E1-E3 (days 57-84): X01, X02 and X03 each tested alone hurt the forecast, with skill of about -8% to -11%. Each interval includes zero, and each of the three was positive in its last week (days 78-84). E4 (days 85-112): X04 alone was close to null at +2.0%, interval -4.9 to +8.7. E5 (days 85-112): the set X01+X02+X03 helped clearly, +15.0% with interval +4.5 to +26.5. Its weekly skill was +9.5, +23.0, +23.7 and then only +2.7% in the last week. Two readings fit this. Either the system changed around day 78-85 so that one or more of X01-X03 became useful, or the members help only jointly. The individual rejections date from before day 85, so they are provisional and stale. The weak last week of E5 is a possible sign of decay. One experiment remains. I will re-test the set on the most recent data (days 99-126) to see whether it still helps in days 113-126 before choosing the final selection. Attribution to individual members cannot be resolved with the budget left.
Regime assessment: possible_change; cites: E1, E2, E3, E5; justification: X01-X03 each hurt on days 57-84, yet the set helped strongly on days 85-112, and its last week weakened to +2.7%. This suggests a shift around day 80-85 and possibly another near day 112.
Decision uncertainties:
- U1: Does the X01+X02+X03 set still help on the newest days 113-126, or was the weak week of days 106-112 the start of a decline? Why it matters: It decides whether to select the set or nothing for the forecasts after day 126.
- U2: Which of X01, X02 and X03 drives the set's gain? Their individual tests come only from the older days 57-84. Why it matters: Including members that do not help adds noise. Without attribution the set has to be kept whole or dropped whole.
- U3: X04 was only tested alone and was near null. Its value on top of the set, or after day 112, is untested. Why it matters: It could be a missed addition, though the evidence so far favours leaving it out.
Budget needs: With one experiment left, the priority is checking that the set still helps on the most recent data. Attribution (U2) and X04 conditional on the set (U3) will stay unresolved.
Beliefs:
- X01: promising; cites: E1, E5; reason: It hurt when tested alone on days 57-84 (stale, earlier regime), but it is part of the set that helped strongly on days 85-112. Its own contribution is unknown.; freshness: possibly_stale; evidence: grouped; last scored day: 112; attribution: Its individual effect has not been tested since day 84, and its share of the set's gain is unknown.
- X02: promising; cites: E2, E5; reason: It hurt when tested alone on days 57-84 (stale), and it is a member of the set that helped on days 85-112.; freshness: possibly_stale; evidence: grouped; last scored day: 112; attribution: Its individual effect has not been tested since day 84, and its share of the set's gain is unknown.
- X03: promising; cites: E3, E5; reason: It hurt when tested alone on days 57-84 (stale), though it was +8.1% in the last of those weeks. It is a member of the set that helped on days 85-112.; freshness: possibly_stale; evidence: grouped; last scored day: 112; attribution: Its individual effect has not been tested since day 84, and its share of the set's gain is unknown.
- X04: rejected; cites: E4; reason: Tested alone on days 85-112 it was near null (+2.0%, interval -4.9 to +8.7). This rejection is provisional and dated to that period.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Not tested on top of X01-X03, and not tested after day 112.
Experiments requested:
- E6: covariates [X01, X02, X03], reference [none], window 28 days; expected: improves; because: E5 showed the set helping by +15% on days 85-112, but its last week fell to +2.7%. Scoring days 99-126 adds the two unseen weeks (113-126) and the per-week parts will show whether the gain has decayed.; targets: U1; possible follow-up: No budget will remain. If the result is positive, select the set. If the newest weeks are null or negative, select none. If ambiguous, weigh the per-week trend.; budget rationale: The final selection rests mainly on the set. Checking it on the newest data is the most decision-relevant use of the last experiment, and one experiment cannot resolve attribution anyway.
  Result E6: scored days 99-126; reference MAE 1.169; candidate MAE 0.894; skill +23.6% (95% interval +7.6% to +34.2%); days won/lost/tied 18/10/0; skill per 7-day part: +23.7%, +2.7%, +35.9%, +22.8%

=== Call 4: final call, days 1-126 observed ===
Notes: E1-E3 (days 57-84): X01, X02 and X03 each tested alone scored -8% to -11%, with every interval including zero. Each improved in the last week. E4 (days 85-112): X04 alone was near null at +2.0% (interval -4.9 to +8.7). E5 (days 85-112): the set X01+X02+X03 gave +15.0% (interval +4.5 to +26.5), but its last week was only +2.7%. E6 (days 99-126): the set gave +23.6% (interval +7.6 to +34.2), with weekly skill +23.7, +2.7, +35.9 and +22.8. The weak week (days 106-112) was a dip, not decay, and the set is strongest on the newest days 113-126. The single-variable rejections of X01-X03 come from before day 85, so they are stale. Attribution within the set was never tested, so the set is kept whole. X04 was tested only alone, before day 113, and is left out provisionally.
Regime assessment: changed; cites: E1, E2, E3, E5, E6; justification: X01-X03 each hurt on days 57-84, while the set helped clearly and consistently from day 85 to day 126, which points to a shift around day 80-85 that persists in the newest weeks.
Decision uncertainties:
- U1: Which of X01, X02 and X03 drives the set's gain. No member was tested alone or conditionally after day 84. Why it matters: Some members may only add noise, but without attribution the set must be used whole.
- U2: Whether X04 adds value on top of the set, or after day 112. It was tested only alone, on days 85-112. Why it matters: It could be a missed addition. The available evidence (near null alone) supports leaving it out.
- U3: Whether a further regime change after day 126 could erode the set's gain, as hinted by the one weak week (days 106-112). Why it matters: The selection assumes the regime of days 85-126 continues. Forecasts should be monitored.
Budget needs: No budget remains. Attribution within X01-X03 and the value of X04 conditional on the set stay unresolved and would be the next tests.
Beliefs:
- X01: promising; cites: E1, E5, E6; reason: It is a member of the set that helped on days 85-112 (+15%) and days 99-126 (+23.6%, strongest in days 113-126). Its single-variable harm on days 57-84 predates the change and is stale.; freshness: current; evidence: grouped; last scored day: 126; attribution: Its individual contribution within the set is untested after day 84.
- X02: promising; cites: E2, E5, E6; reason: It is a member of the set that helped on days 85-126 and remains strong in the newest weeks. Its single-variable result from days 57-84 is stale.; freshness: current; evidence: grouped; last scored day: 126; attribution: Its individual contribution within the set is untested after day 84.
- X03: promising; cites: E3, E5, E6; reason: It is a member of the set that helped on days 85-126. Its single-variable result from days 57-84 is stale, and it was already +8.1% in the last of those weeks.; freshness: current; evidence: grouped; last scored day: 126; attribution: Its individual contribution within the set is untested after day 84.
- X04: rejected; cites: E4; reason: Tested alone on days 85-112 it was near null (+2.0%, interval -4.9 to +8.7). This rejection is provisional and dated to that period.; freshness: possibly_stale; evidence: direct; last scored day: 112; attribution: Not tested on top of X01-X03, and not tested after day 112.
Final selection: [X01, X02, X03]
Conclusion: Select X01, X02 and X03 together. The set helped clearly after an apparent regime change around day 85: +15.0% on days 85-112 (E5) and +23.6% on days 99-126 (E6), with the newest weeks at +35.9% and +22.8%. The weak week of days 106-112 was a transient dip, not decay. Earlier single-variable harm (E1-E3, days 57-84) describes the old regime only. The evidence supports the set, not each member individually, so it is kept whole. X04 is excluded provisionally: it was near null when tested alone on days 85-112 and was never tested conditionally or on the newest data. Performance should be monitored for further drift, and attribution within the set and X04 on top of the set should be tested if more budget becomes available.

```
