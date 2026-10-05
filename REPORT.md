# Kernel1 twelve-world result: KERNEL NOT PROVEN

Rule: row 4: change successes 0 of 8 (none); stable 1 of 2; null 2 of 2; median oracle fraction 0.985 over 9 informative non-null worlds; worlds with pure noise selected 6 (w01, w02, w05, w07, w10, w06); false accepts in null worlds 0

Closing line: STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL

Spec 816d4d973c61d1ef20d0833f624cd35babd3115647a67652c2bab0dca65f1ca2; run 37298605583; commit 35d6aa6f12e077bcfd4b0099dcd8084b8ff1b4dd; lesson 1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb; L8 system text 78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d (pinned 78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d).
Composition {'change': 8, 'stable': 2, 'null': 2}; kinds {'w01': 'change', 'w02': 'change', 'w03': 'stable', 'w04': 'change', 'w05': 'change', 'w06': 'stable', 'w07': 'change', 'w08': 'change', 'w09': 'null', 'w10': 'change', 'w11': 'change', 'w12': 'null'}.
Material integrity issues: none. Generator defects: none. Worlds without a valid final response: none.

Change successes 0 of 8 (informative 7); stable 1 of 2; null 2 of 2; median oracle fraction 0.985 ({'w01': 0.985323322982661, 'w02': 0.9935210830578778, 'w05': 0.0, 'w07': 0.9737234386027827, 'w08': 1.0, 'w10': 0.8521746579241751, 'w11': 0.8277491514997329, 'w03': 1.0, 'w06': 0.9979628992065694}); pure-noise selections {'w01': ['X01'], 'w02': ['X03'], 'w05': ['X05', 'X06', 'X07'], 'w06': ['X03'], 'w07': ['X04'], 'w10': ['X05']}; null false accepts {'w09': [], 'w12': []}; R retained ['w05', 'w11'].
Tokens 332838; attempts 48; refusals 0; repairs 0; t0-beta forecasts research 2786, evaluate 11662; evaluate 613.8 s.

Caveats: Twelve worlds and one stochastic trajectory of the researcher in each. Synthetic worlds from one frozen generator family: a pass does not establish real-market performance or commercial value; 'proven' means demonstrated against this benchmark at the predeclared thresholds. The benchmark tests predictive information, not causal identification: D (E's proxy) may be selected.

## w01: change world, FAILURE (failed: 4_no_pure_noise, 5_supported_by_own_current_evidence)

Roles: R X04, E X02, D X05, N1 X01, N2 X07, N3 X06, N4 X03, N5 X08. Change day: 86.
Informative: True; detection: E alone, days 99-112 +29.0% [+17.1, +37.8]; E alone, days 99-126 +21.3% [+4.3, +35.0]; oracle set {E, D} (['X02', 'X05']), skill 0.313.
Confirmation (t0-beta, days 127-154): {E} vs {} +30.6% [+16.5, +41.9]; {D} vs {} +20.2% [+3.6, +35.8]; {R} vs {} -5.4% [-14.4, +2.1]; {E, D} vs {} +31.3% [+17.7, +42.7]; D given E ({E, D} vs {E}) +0.9% [-3.4, +5.6]; E given D ({E, D} vs {D}) +13.8% [+1.5, +26.4]; R given E ({E, R} vs {E}) +0.3% [-4.6, +6.3].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N1, E, N4, R) | [] (-) | 57-84 | +39.7% [+28.9, +49.6] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (D, N3, N2, N5) | [] (-) | 57-84 | -9.8% [-22.9, +2.6] | no |
| E3 | 2 | ['X01', 'X02'] (N1, E) | [] (-) | 85-112 | +29.1% [+13.6, +41.9] | no |
| E4 | 2 | ['X03', 'X04'] (N4, R) | [] (-) | 85-112 | +3.7% [-15.2, +14.2] | no |
| E5 | 3 | ['X02'] (E) | ['X01'] (N1) | 99-126 | +20.5% [+3.9, +35.5] | yes |
| E6 | 3 | ['X05', 'X06', 'X07', 'X08'] (D, N3, N2, N5) | ['X01', 'X02'] (N1, E) | 99-126 | -3.0% [-13.1, +7.0] | yes |

Final selection: ['X01', 'X02'] (N1, E); valid final response: True.
Final statuses: {'X01 (N1)': 'promising', 'X02 (E)': 'accepted', 'X03 (N4)': 'rejected', 'X04 (R)': 'rejected', 'X05 (D)': 'rejected', 'X06 (N3)': 'rejected', 'X07 (N2)': 'rejected', 'X08 (N5)': 'rejected'}.
Support: False (-; chain []).
Confirmation of the selection: +30.8% [+16.5, +43.0] (ridge, context only: +36.7% [+27.7, +48.6]); oracle fraction 0.985.
R selected False (final status rejected); E selected True; D selected False; pure noise selected ['X01']; accepted ['X02'].
First current experiment containing useful information: E5; conditional or separation experiments: ['E3', 'E4', 'E5', 'E6']; reopened stale negatives: ['E6', 'E6', 'E6', 'E6']; cited earlier failed experiments: ['E2', 'E2', 'E4', 'E2', 'E4', 'E6']; experiments used 6.
Conclusion (verbatim): Select X01 and X02. X02 is individually supported on the most recent data: it adds +20.5% over X01 alone on days 99-126 (CI +3.9 to +35.5). The pair X01,X02 has helped in every period tested (E1 block, E3 +29.1%, E5/E6 best MAE 0.942). X01 is kept because X01+X02 is the configuration actually validated, though its marginal value over X02 alone was never isolated. That is the main residual uncertainty. X05-X08 were rejected twice, including on the latest days 99-126 on top of X01,X02 (E6 -3.0%), so no new signal is emerging there. X03,X04 are excluded on evidence dated to days 85-112 (E4). That rejection is provisional, since it was not re-tested on days 113-126. The weekly skills varied (occasional negative weeks) but showed no sustained decay, so I do not infer a regime change. If future performance of X01,X02 degrades, X03,X04 should be re-screened first.
Cost: {'tokens_used': 27582, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7123, 'output_tokens': 7123, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 994}; timing {'loop_started_unix': 1791197220, 'loop_finished_unix': 1791197318, 'loop_wall_s': 98}.
Integrity: material none; notes none; call failures none.

## w02: change world, FAILURE (failed: 4_no_pure_noise, 5_supported_by_own_current_evidence)

Roles: R X05, E X04, D X02, N1 X07, N2 X06, N3 X03, N4 X01, N5 X08. Change day: 91.
Informative: True; detection: E alone, days 99-112 +48.8% [+35.4, +59.0]; E alone, days 99-126 +43.7% [+33.1, +52.4]; oracle set {E} (['X04']), skill 0.281.
Confirmation (t0-beta, days 127-154): {E} vs {} +28.1% [+17.1, +37.2]; {D} vs {} +9.9% [-1.5, +23.5]; {R} vs {} +1.4% [-9.8, +11.8]; {E, D} vs {} +26.1% [+13.9, +35.9]; D given E ({E, D} vs {E}) -2.7% [-6.1, +0.6]; E given D ({E, D} vs {D}) +18.0% [+5.7, +28.0]; R given E ({E, R} vs {E}) +0.8% [-4.2, +6.0].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N4, D, N3, E) | [] (-) | 57-84 | -9.7% [-20.2, +0.2] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (R, N2, N1, N5) | [] (-) | 57-84 | +49.6% [+37.6, +56.2] | no |
| E3 | 2 | ['X05', 'X06'] (R, N2) | [] (-) | 85-112 | +4.0% [-10.8, +16.2] | no |
| E4 | 2 | ['X07', 'X08'] (N1, N5) | [] (-) | 85-112 | -1.4% [-13.7, +8.1] | no |
| E5 | 2 | ['X01', 'X02', 'X03', 'X04'] (N4, D, N3, E) | [] (-) | 85-112 | +31.9% [+10.7, +47.7] | no |
| E6 | 3 | ['X01', 'X02'] (N4, D) | ['X03', 'X04'] (N3, E) | 99-126 | -1.0% [-8.1, +6.2] | yes |

Final selection: ['X03', 'X04'] (N3, E); valid final response: True.
Final statuses: {'X01 (N4)': 'redundant', 'X02 (D)': 'redundant', 'X03 (N3)': 'accepted', 'X04 (E)': 'accepted', 'X05 (R)': 'deteriorated', 'X06 (N2)': 'deteriorated', 'X07 (N1)': 'deteriorated', 'X08 (N5)': 'deteriorated'}.
Support: False (-; chain []).
Confirmation of the selection: +27.9% [+17.8, +36.7] (ridge, context only: +28.9% [+12.7, +41.1]); oracle fraction 0.994.
R selected False (final status deteriorated); E selected True; D selected False; pure noise selected ['X03']; accepted ['X03', 'X04'].
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: ['E5', 'E5', 'E5', 'E5']; cited earlier failed experiments: ['E1', 'E1', 'E3', 'E4', 'E1', 'E3', 'E4', 'E6']; experiments used 6.
Conclusion (verbatim): The system changed around days 85-99. The old signal in X05-X08 (E2) decayed (E3, E4). A new signal appeared in block X01-X04 (E5), growing to about +50% skill in days 99-112. E6 shows that X01/X02 add nothing on top of X03/X04 and slightly hurt on days 113-126, so the selection is pruned to X03 and X04. Caveats: X03 and X04 were not separated, so either may be the sole driver. Their value on days 113-126 is inferred from the low reference MAE in E6, not measured against a no-covariate baseline. X05-X08 were not re-screened after day 112, so their rejection is provisional. If the regime shifts again, re-screen all candidates on recent data.
Cost: {'tokens_used': 27012, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 6987, 'output_tokens': 6689, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 994}; timing {'loop_started_unix': 1791197220, 'loop_finished_unix': 1791197316, 'loop_wall_s': 96}.
Integrity: material none; notes none; call failures none.

## w03: stable world, SUCCESS

Roles: R X08, E X04, D X01, N1 X07, N2 X06, N3 X03, N4 X02, N5 X05. Change day: none (no change in this world).
Informative: True; detection: R alone, days 57-84 +37.9% [+25.2, +46.8]; R alone, days 85-112 +48.0% [+34.5, +57.1]; R alone, days 99-126 +41.8% [+26.0, +55.2]; oracle set {R} (['X08']), skill 0.325.
Confirmation (t0-beta, days 127-154): {E} vs {} -10.3% [-21.5, -2.7]; {D} vs {} -8.6% [-18.3, -1.4]; {R} vs {} +32.5% [+21.3, +41.3]; {E, D} vs {} -8.4% [-21.6, +0.5]; D given E ({E, D} vs {E}) +1.7% [-2.7, +6.8]; E given D ({E, D} vs {D}) +0.2% [-7.5, +6.6]; R given E ({E, R} vs {E}) +38.5% [+28.9, +47.1].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (D, N4, N3, E) | [] (-) | 57-84 | +4.0% [-8.2, +13.5] | yes |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (N5, N2, N1, R) | [] (-) | 57-84 | +37.3% [+22.6, +47.9] | yes |
| E3 | 2 | ['X05', 'X06'] (N5, N2) | [] (-) | 85-112 | -11.5% [-22.1, -1.5] | yes |
| E4 | 2 | ['X07', 'X08'] (N1, R) | [] (-) | 85-112 | +48.5% [+35.0, +57.1] | yes |
| E5 | 2 | ['X01', 'X02', 'X03', 'X04'] (D, N4, N3, E) | [] (-) | 85-112 | -18.1% [-32.5, -7.6] | yes |
| E6 | 3 | ['X07'] (N1) | ['X08'] (R) | 99-126 | -2.8% [-8.5, +2.6] | yes |

Final selection: ['X08'] (R); valid final response: True.
Final statuses: {'X01 (D)': 'rejected', 'X02 (N4)': 'rejected', 'X03 (N3)': 'rejected', 'X04 (E)': 'rejected', 'X05 (N5)': 'rejected', 'X06 (N2)': 'rejected', 'X07 (N1)': 'redundant', 'X08 (R)': 'accepted'}.
Support: True (elimination; chain ['E4', 'E6']).
Confirmation of the selection: +32.5% [+21.3, +41.3] (ridge, context only: +24.5% [+6.5, +37.8]); oracle fraction 1.000.
R selected True (final status accepted); E selected False; D selected False; pure noise selected none; accepted ['X08'].
First current experiment containing useful information: E2; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: none; cited earlier failed experiments: ['E1', 'E1', 'E3', 'E5', 'E1', 'E3', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Use X08 alone. The strong gain of block X05-X08 (E2: +37%) and of pair X07+X08 (E4: +48.5%) is carried by X08. E6 showed X07 adds nothing given X08 (-2.8%, CI spans 0, last week -12%). With X08 alone, error stayed around 0.82 MAE through day 126, about half the no-covariate error, so there is no sign of decay. X05+X06 and X01-X04 hurt on days 85-112. Those rejections are provisional: they are block or pair level and were never screened on days 113-126. Since the favourite has not decayed, there is no drift signal to justify reviving them now. Caveats: X08's individual skill is inferred by comparing MAEs across experiments rather than from a direct test against no covariates. If X08's performance starts to decay after day 126, re-screen X01-X07 on the newest data.
Cost: {'tokens_used': 27416, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7401, 'output_tokens': 6679, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 1050}; timing {'loop_started_unix': 1791197222, 'loop_finished_unix': 1791197315, 'loop_wall_s': 93}.
Integrity: material none; notes none; call failures none.

## w04: change world, FAILURE (failed: 1_informative, 2_selection_non_empty, 5_supported_by_own_current_evidence, 6_confirmation_lower_bound_above_0, 7_oracle_fraction_at_least_0.70)

Roles: R X03, E X02, D X05, N1 X04, N2 X08, N3 X01, N4 X06, N5 X07. Change day: 86.
Informative: False; detection: E alone, days 99-112 +3.6% [-29.1, +25.1]; E alone, days 99-126 +14.6% [-1.3, +28.8]; oracle set {E} (['X02']), skill 0.423.
Confirmation (t0-beta, days 127-154): {E} vs {} +42.3% [+31.1, +54.8]; {D} vs {} +31.3% [+18.4, +43.2]; {R} vs {} +10.6% [-6.4, +24.7]; {E, D} vs {} +39.8% [+28.7, +50.8]; D given E ({E, D} vs {E}) -4.4% [-21.2, +6.6]; E given D ({E, D} vs {D}) +12.4% [+5.4, +21.2]; R given E ({E, R} vs {E}) +3.3% [-10.3, +16.5].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N3, E, R, N1) | [] (-) | 57-84 | +37.0% [+23.5, +47.9] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (D, N4, N5, N2) | [] (-) | 57-84 | -8.3% [-19.8, +2.1] | no |
| E3 | 2 | ['X01', 'X02'] (N3, E) | [] (-) | 85-112 | +11.7% [-4.1, +25.9] | no |
| E4 | 2 | ['X03', 'X04'] (R, N1) | [] (-) | 85-112 | +2.0% [-10.6, +12.0] | no |
| E5 | 2 | ['X05', 'X06', 'X07', 'X08'] (D, N4, N5, N2) | [] (-) | 85-112 | +2.5% [-13.3, +19.6] | no |
| E6 | 3 | ['X05', 'X06', 'X07', 'X08'] (D, N4, N5, N2) | [] (-) | 113-126 | +7.0% [-12.6, +24.3] | yes |

Final selection: [] (-); valid final response: True.
Final statuses: {'X01 (N3)': 'deteriorated', 'X02 (E)': 'deteriorated', 'X03 (R)': 'rejected', 'X04 (N1)': 'rejected', 'X05 (D)': 'rejected', 'X06 (N4)': 'rejected', 'X07 (N5)': 'rejected', 'X08 (N2)': 'rejected'}.
Support: False (-; chain []).
Confirmation of the selection: not scored; oracle fraction 0.000.
R selected False (final status rejected); E selected False; D selected False; pure noise selected none; accepted none.
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4']; reopened stale negatives: ['E5', 'E5', 'E5', 'E5']; cited earlier failed experiments: ['E2', 'E2', 'E3', 'E4', 'E5', 'E2', 'E3', 'E4', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Final selection: none. The X01-X04 relationship that helped strongly in days 57-77 broke down around day 78, consistent with a regime change. After the change, no set showed a significant gain. X01-X02 scored +11.7% on days 85-112, but it was not significant, was declining, and its last tested week was negative. X03-X04 was null. X05-X08 was null on days 57-84, 85-112 and 113-126; its latest +7% has a CI from -12.6% to +24.3%. Adding four unproven covariates risks the harm seen in E2. I also cannot attribute any effect to individual members. This conclusion is provisional and dated. X01-X04 were not tested on days 113-126, and X05-X08 shows a weak rising trend. If monitoring continues, re-screen first X05-X08 (split into pairs) and then X01-X02 on the newest data.
Cost: {'tokens_used': 29840, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7840, 'output_tokens': 8664, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 224}; t0-beta forecasts {'research': 224, 'evaluate': 896}; timing {'loop_started_unix': 1791197223, 'loop_finished_unix': 1791197331, 'loop_wall_s': 108}.
Integrity: material none; notes none; call failures none.

## w05: change world, FAILURE (failed: 3_r_absent, 4_no_pure_noise, 5_supported_by_own_current_evidence, 6_confirmation_lower_bound_above_0, 7_oracle_fraction_at_least_0.70)

Roles: R X01, E X08, D X02, N1 X04, N2 X07, N3 X05, N4 X06, N5 X03. Change day: 90.
Informative: True; detection: E alone, days 99-112 +32.5% [+17.8, +48.8]; E alone, days 99-126 +34.4% [+21.5, +46.8]; oracle set {E} (['X08']), skill 0.349.
Confirmation (t0-beta, days 127-154): {E} vs {} +34.9% [+18.6, +46.1]; {D} vs {} +13.9% [-4.7, +29.5]; {R} vs {} -12.0% [-21.4, -3.8]; {E, D} vs {} +32.9% [+15.0, +45.6]; D given E ({E, D} vs {E}) -3.1% [-7.6, +1.0]; E given D ({E, D} vs {D}) +22.0% [+4.1, +37.5]; R given E ({E, R} vs {E}) +1.5% [-1.7, +4.5].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (R, D, N5, N1) | [] (-) | 57-84 | +36.4% [+15.9, +50.2] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (N3, N4, N2, E) | [] (-) | 57-84 | -5.1% [-15.5, +9.1] | no |
| E3 | 2 | ['X01', 'X02'] (R, D) | [] (-) | 85-112 | +14.8% [-1.3, +27.2] | no |
| E4 | 2 | ['X03', 'X04'] (N5, N1) | [] (-) | 85-112 | -10.1% [-24.8, -1.1] | no |
| E5 | 2 | ['X05', 'X06', 'X07', 'X08'] (N3, N4, N2, E) | [] (-) | 85-112 | +19.7% [+7.0, +32.6] | no |
| E6 | 3 | ['X05', 'X06', 'X07', 'X08'] (N3, N4, N2, E) | ['X01', 'X02'] (R, D) | 99-126 | +14.4% [-0.2, +24.9] | yes |

Final selection: ['X01', 'X02', 'X05', 'X06', 'X07', 'X08'] (R, D, N3, N4, N2, E); valid final response: True.
Final statuses: {'X01 (R)': 'deteriorated', 'X02 (D)': 'deteriorated', 'X03 (N5)': 'rejected', 'X04 (N1)': 'rejected', 'X05 (N3)': 'promising', 'X06 (N4)': 'promising', 'X07 (N2)': 'promising', 'X08 (E)': 'promising'}.
Support: False (-; chain []).
Confirmation of the selection: not scored; oracle fraction 0.000.
R selected True (final status deteriorated); E selected True; D selected True; pure noise selected ['X05', 'X06', 'X07']; accepted none.
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: ['E5', 'E5', 'E5', 'E5']; cited earlier failed experiments: ['E2', 'E2', 'E3', 'E4', 'E2', 'E3', 'E4', 'E6']; experiments used 6.
Conclusion (verbatim): The system appears to have drifted. X01-X02 drove the early signal (E1, E3), but their skill decayed through days 85-112. X05-X08 were useless in days 57-84 (E2) but became helpful afterwards (E5). They still added skill on top of X01-X02 in days 99-126 (E6 +14.4%), rising to +29.8% in the latest week. X03-X04 were harmful (E4). I select X01, X02 and X05-X08, because this exact set was evaluated most recently (E6) and performed best of all tested configurations. Dropping X01-X02 was never tested, and they were not negative in any part of E3. Caveats: the evidence is set-level throughout, and no individual member is established as useful. The E6 interval just touches 0. X01-X02 are fading and may become dead weight. The X03-X04 rejection and the decline of X01-X02 are dated findings and should be re-screened as new data arrive. Priorities for further work would be splitting X05-X08 and testing X05-X08 without X01-X02.
Cost: {'tokens_used': 28318, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7410, 'output_tokens': 7572, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 966}; timing {'loop_started_unix': 1791197393, 'loop_finished_unix': 1791197495, 'loop_wall_s': 102}.
Integrity: material none; notes none; call failures none.

## w06: stable world, FAILURE (failed: 3_no_pure_noise)

Roles: R X04, E X05, D X08, N1 X07, N2 X01, N3 X03, N4 X06, N5 X02. Change day: none (no change in this world).
Informative: True; detection: R alone, days 57-84 +30.2% [+11.9, +41.6]; R alone, days 85-112 +27.0% [+4.4, +45.0]; R alone, days 99-126 +20.0% [-1.4, +37.4]; oracle set {R} (['X04']), skill 0.219.
Confirmation (t0-beta, days 127-154): {E} vs {} -0.8% [-9.8, +8.7]; {D} vs {} -1.9% [-10.9, +8.0]; {R} vs {} +21.9% [+2.9, +38.6]; {E, D} vs {} -1.4% [-12.0, +9.6]; D given E ({E, D} vs {E}) -0.6% [-4.1, +3.0]; E given D ({E, D} vs {D}) +0.5% [-3.3, +3.8]; R given E ({E, R} vs {E}) +21.5% [+3.4, +35.0].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N2, N5, N3, R) | [] (-) | 57-84 | +22.8% [+5.2, +34.6] | yes |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (E, N4, N1, D) | [] (-) | 57-84 | -13.4% [-26.0, -6.3] | yes |
| E3 | 2 | ['X01', 'X02'] (N2, N5) | [] (-) | 85-112 | -4.9% [-16.2, +3.0] | yes |
| E4 | 2 | ['X03', 'X04'] (N3, R) | [] (-) | 85-112 | +23.5% [+0.5, +42.1] | yes |
| E5 | 2 | ['X05', 'X06', 'X07', 'X08'] (E, N4, N1, D) | [] (-) | 85-112 | -16.0% [-38.9, -2.3] | yes |
| E6 | 3 | ['X04'] (R) | ['X03'] (N3) | 99-126 | +22.3% [+2.1, +38.1] | yes |

Final selection: ['X03', 'X04'] (N3, R); valid final response: True.
Final statuses: {'X01 (N2)': 'rejected', 'X02 (N5)': 'rejected', 'X03 (N3)': 'promising', 'X04 (R)': 'accepted', 'X05 (E)': 'rejected', 'X06 (N4)': 'rejected', 'X07 (N1)': 'rejected', 'X08 (D)': 'rejected'}.
Support: True (direct: an experiment on exactly the final set; chain ['E4']).
Confirmation of the selection: +21.8% [+3.4, +37.6] (ridge, context only: +30.0% [+16.4, +40.5]); oracle fraction 0.998.
R selected True (final status accepted); E selected False; D selected False; pure noise selected ['X03']; accepted ['X04'].
First current experiment containing useful information: E1; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: none; cited earlier failed experiments: ['E2', 'E2', 'E3', 'E5', 'E2', 'E3', 'E5']; experiments used 6.
Conclusion (verbatim): Select X03 and X04. This exact configuration was tested on the most recent data (E6 candidate, days 99-126), and X04 added +22.3% skill over X03 (CI +2.1% to +38.1%). That gain was strongest in the last two weeks, so the earlier suspected decay did not persist. X04 is individually supported. X03 is included on pair-level evidence only (E4), because X04 alone was never tested and the measured gain is conditional on X03 being present. X01/X02 (E3) and X05-X08 (E2, E5) are excluded. Those exclusions rest on data up to day 112 and on pair- or set-level tests, so they are provisional. If the system shifts again, they should be re-screened first.
Cost: {'tokens_used': 27714, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7352, 'output_tokens': 7026, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 1078}; timing {'loop_started_unix': 1791197389, 'loop_finished_unix': 1791197485, 'loop_wall_s': 96}.
Integrity: material none; notes none; call failures none.

## w07: change world, FAILURE (failed: 4_no_pure_noise)

Roles: R X05, E X03, D X06, N1 X02, N2 X07, N3 X04, N4 X08, N5 X01. Change day: 86.
Informative: True; detection: E alone, days 99-112 +32.0% [+2.8, +45.9]; E alone, days 99-126 +24.6% [+6.3, +35.8]; oracle set {E} (['X03']), skill 0.187.
Confirmation (t0-beta, days 127-154): {E} vs {} +18.7% [+6.8, +28.0]; {D} vs {} +7.6% [-2.4, +18.1]; {R} vs {} -2.6% [-13.1, +7.0]; {E, D} vs {} +16.6% [+4.2, +27.1]; D given E ({E, D} vs {E}) -2.6% [-9.1, +3.4]; E given D ({E, D} vs {D}) +9.7% [-3.3, +20.0]; R given E ({E, R} vs {E}) -0.6% [-7.2, +5.8].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N5, N1, E, N3) | [] (-) | 57-84 | +2.8% [-3.8, +10.3] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (R, D, N2, N4) | [] (-) | 57-84 | +32.8% [+15.3, +47.3] | no |
| E3 | 2 | ['X05', 'X06'] (R, D) | [] (-) | 85-112 | +7.5% [-9.0, +21.0] | no |
| E4 | 2 | ['X07', 'X08'] (N2, N4) | [] (-) | 85-112 | -9.0% [-16.9, -0.2] | no |
| E5 | 3 | ['X01', 'X02'] (N5, N1) | [] (-) | 99-126 | +0.6% [-10.0, +11.0] | yes |
| E6 | 3 | ['X03', 'X04'] (E, N3) | [] (-) | 99-126 | +23.0% [+2.2, +35.9] | yes |

Final selection: ['X03', 'X04'] (E, N3); valid final response: True.
Final statuses: {'X01 (N5)': 'rejected', 'X02 (N1)': 'rejected', 'X03 (E)': 'accepted', 'X04 (N3)': 'accepted', 'X05 (R)': 'deteriorated', 'X06 (D)': 'deteriorated', 'X07 (N2)': 'deteriorated', 'X08 (N4)': 'deteriorated'}.
Support: True (direct: an experiment on exactly the final set; chain ['E6']).
Confirmation of the selection: +18.2% [+6.0, +28.3] (ridge, context only: +30.4% [+16.3, +41.3]); oracle fraction 0.974.
R selected False (final status deteriorated); E selected True; D selected False; pure noise selected ['X04']; accepted ['X03', 'X04'].
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4', 'E5', 'E6']; reopened stale negatives: ['E5', 'E5', 'E6', 'E6']; cited earlier failed experiments: ['E1', 'E1', 'E3', 'E4', 'E1', 'E3', 'E4', 'E5']; experiments used 6.
Conclusion (verbatim): The system appears to have changed around days 85-112. The X05-X08 block that drove skill on days 57-84 (E2) decayed. X05+X06 became non-significant (E3), and X07+X08 became significantly harmful (E4). Re-screening the previously dismissed X01-X04 on the latest data (days 99-126) found a significant, consistent gain from X03+X04 (E6: +23.0%, CI +2.2 to +35.9, positive in all parts). X01+X02 stayed null (E5). I select X03 and X04 together. The evidence is pair-level, and I cannot say whether both members contribute or only one. Caveats: the CI lower bound is close to zero, won/lost was only 16/12, and the process is non-stationary. All rejections are dated to their test windows and should be re-screened if the X03/X04 skill decays.
Cost: {'tokens_used': 27514, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7288, 'output_tokens': 6890, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 994}; timing {'loop_started_unix': 1791197391, 'loop_finished_unix': 1791197488, 'loop_wall_s': 97}.
Integrity: material none; notes none; call failures none.

## w08: change world, FAILURE (failed: 5_supported_by_own_current_evidence)

Roles: R X05, E X06, D X02, N1 X03, N2 X08, N3 X07, N4 X01, N5 X04. Change day: 87.
Informative: True; detection: E alone, days 99-112 +22.1% [+7.9, +34.0]; E alone, days 99-126 +22.4% [+9.3, +34.9]; oracle set {E} (['X06']), skill 0.200.
Confirmation (t0-beta, days 127-154): {E} vs {} +20.0% [+9.9, +28.4]; {D} vs {} +7.1% [-3.2, +17.0]; {R} vs {} -1.8% [-13.1, +8.8]; {E, D} vs {} +16.6% [+5.1, +26.2]; D given E ({E, D} vs {E}) -4.2% [-10.5, +1.5]; E given D ({E, D} vs {D}) +10.2% [+4.5, +16.0]; R given E ({E, R} vs {E}) -3.8% [-10.2, +2.3].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N4, D, N1, N5) | [] (-) | 57-84 | -7.7% [-22.4, +5.0] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (R, E, N3, N2) | [] (-) | 57-84 | +27.2% [+13.7, +40.8] | no |
| E3 | 2 | ['X05', 'X06'] (R, E) | [] (-) | 85-112 | +21.1% [+2.5, +33.0] | no |
| E4 | 2 | ['X07', 'X08'] (N3, N2) | [] (-) | 85-112 | -5.3% [-12.3, +0.6] | no |
| E5 | 3 | ['X05'] (R) | [] (-) | 99-126 | -6.4% [-13.9, +0.6] | yes |
| E6 | 3 | ['X01', 'X02', 'X03', 'X04'] (N4, D, N1, N5) | ['X05', 'X06'] (R, E) | 99-126 | +1.0% [-13.3, +14.3] | yes |

Final selection: ['X06'] (E); valid final response: True.
Final statuses: {'X01 (N4)': 'rejected', 'X02 (D)': 'rejected', 'X03 (N1)': 'rejected', 'X04 (N5)': 'rejected', 'X05 (R)': 'rejected', 'X06 (E)': 'accepted', 'X07 (N3)': 'rejected', 'X08 (N2)': 'rejected'}.
Support: False (-; chain []).
Confirmation of the selection: +20.0% [+9.9, +28.4] (ridge, context only: +23.0% [+12.8, +30.5]); oracle fraction 1.000.
R selected False (final status rejected); E selected True; D selected False; pure noise selected none; accepted ['X06'].
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4', 'E5', 'E6']; reopened stale negatives: ['E6', 'E6', 'E6', 'E6']; cited earlier failed experiments: ['E1', 'E1', 'E4', 'E1', 'E4', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Select X06 only. The X05-X08 block helped on days 57-84 (E2). X05+X06 helped out-of-sample on days 85-112 (+21.1%, E3) and still gave about +22% vs no covariates on days 99-126 (E5/E6 reference MAEs 1.291 vs 1.010), so there was no sign of decay. On the same days X05 alone was harmful (-6.4%, 9/19 days, E5), while adding X06 to X05 cut MAE by about 26%. This locates the signal in X06. X05 is dropped because it showed no standalone value, and uninformative covariates cost about 5-6% elsewhere (E4, E5). The main risk is that X06 alone was never tested directly; if X05 helps only in combination with X06, X05+X06 would be the fallback. X01-X04 added nothing on the most recent days (E6), though that evidence is set-level only. X07/X08 rest on days 85-112 only, so their rejection is provisional and should be re-screened first if X06 performance decays.
Cost: {'tokens_used': 28852, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7474, 'output_tokens': 8042, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 252}; t0-beta forecasts {'research': 252, 'evaluate': 1036}; timing {'loop_started_unix': 1791197387, 'loop_finished_unix': 1791197492, 'loop_wall_s': 105}.
Integrity: material none; notes none; call failures none.

## w09: null world, SUCCESS

Roles: R X02, E X01, D X05, N1 X03, N2 X07, N3 X06, N4 X04, N5 X08. Change day: none (no change in this world).
Informative: always scored (null); detection: -; oracle set none (-), skill -.
Confirmation (t0-beta, days 127-154): {E} vs {} -7.7% [-18.3, +5.3]; {D} vs {} -4.1% [-14.2, +7.1]; {R} vs {} -8.9% [-20.5, +2.8]; {E, D} vs {} -10.7% [-25.8, +4.7]; D given E ({E, D} vs {E}) -2.8% [-13.0, +5.0]; E given D ({E, D} vs {D}) -6.3% [-15.3, +0.7]; R given E ({E, R} vs {E}) -2.0% [-10.2, +4.0].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (E, R, N1, N4) | [] (-) | 57-84 | -1.7% [-11.4, +5.9] | yes |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (D, N3, N2, N5) | [] (-) | 57-84 | -1.7% [-10.3, +5.3] | yes |
| E3 | 2 | ['X01', 'X02', 'X03', 'X04'] (E, R, N1, N4) | [] (-) | 85-112 | +1.5% [-10.9, +8.8] | yes |
| E4 | 2 | ['X05', 'X06', 'X07', 'X08'] (D, N3, N2, N5) | [] (-) | 85-112 | -0.3% [-10.7, +5.6] | yes |
| E5 | 3 | ['X01', 'X02', 'X03', 'X04'] (E, R, N1, N4) | [] (-) | 99-126 | -2.7% [-12.5, +6.0] | yes |
| E6 | 3 | ['X05', 'X06', 'X07', 'X08'] (D, N3, N2, N5) | [] (-) | 99-126 | +2.9% [-6.2, +9.5] | yes |

Final selection: [] (-); valid final response: True.
Final statuses: {'X01 (E)': 'rejected', 'X02 (R)': 'rejected', 'X03 (N1)': 'rejected', 'X04 (N4)': 'rejected', 'X05 (D)': 'rejected', 'X06 (N3)': 'rejected', 'X07 (N2)': 'rejected', 'X08 (N5)': 'rejected'}.
Support: None (-; chain []).
Confirmation of the selection: not scored; oracle fraction -.
R selected False (final status rejected); E selected False; D selected False; pure noise selected none; accepted none.
First current experiment containing useful information: None; conditional or separation experiments: none; reopened stale negatives: none; cited earlier failed experiments: ['E1', 'E2', 'E1', 'E2', 'E3', 'E4', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Final selection: none. The target-only forecast is used after day 126. All eight candidates were screened in two groups of four on three successive 28-day windows, the last covering days 99-126 including the newest 14 days. No group showed skill whose interval excluded zero. X01-X04 was slightly negative most recently (-2.7%). X05-X08 had a small positive point estimate (+2.9%), but its newest week was -8.3%, so the earlier uptick did not hold. Because every candidate was examined in the current regime, the empty selection does not rest on outdated evidence. Adding covariates without evidence risks adding noise. Caveats: these are group-level results, so a single useful candidate masked by harmful partners cannot be ruled out. The tests also could not detect small effects. The process may not be stationary, so these rejections are provisional. If monitoring continues, X05-X08 should be re-screened first, ideally split into individual candidates.
Cost: {'tokens_used': 26602, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7451, 'output_tokens': 5815, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 210}; t0-beta forecasts {'research': 210, 'evaluate': 882}; timing {'loop_started_unix': 1791197553, 'loop_finished_unix': 1791197638, 'loop_wall_s': 85}.
Integrity: material none; notes none; call failures none.

## w10: change world, FAILURE (failed: 4_no_pure_noise, 5_supported_by_own_current_evidence)

Roles: R X07, E X06, D X02, N1 X01, N2 X03, N3 X04, N4 X08, N5 X05. Change day: 89.
Informative: True; detection: E alone, days 99-112 +41.6% [+31.7, +48.3]; E alone, days 99-126 +39.2% [+31.5, +46.8]; oracle set {E} (['X06']), skill 0.207.
Confirmation (t0-beta, days 127-154): {E} vs {} +20.7% [+2.5, +36.7]; {D} vs {} +4.7% [-14.5, +21.9]; {R} vs {} -2.9% [-9.8, +3.2]; {E, D} vs {} +13.4% [-6.9, +30.1]; D given E ({E, D} vs {E}) -9.2% [-21.1, -0.5]; E given D ({E, D} vs {D}) +9.1% [-3.5, +19.2]; R given E ({E, R} vs {E}) -4.7% [-13.4, +1.5].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N1, D, N2, N3) | [] (-) | 57-84 | -3.7% [-16.7, +8.3] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (N5, E, R, N4) | [] (-) | 57-84 | +29.9% [+14.4, +43.1] | no |
| E3 | 2 | ['X05', 'X06'] (N5, E) | [] (-) | 85-112 | +37.3% [+26.0, +46.0] | no |
| E4 | 2 | ['X07', 'X08'] (R, N4) | [] (-) | 85-112 | +0.9% [-14.5, +13.6] | no |
| E5 | 2 | ['X01', 'X02', 'X03', 'X04'] (N1, D, N2, N3) | [] (-) | 85-112 | +19.1% [+3.5, +30.9] | no |
| E6 | 3 | ['X01', 'X02', 'X03', 'X04'] (N1, D, N2, N3) | ['X05', 'X06'] (N5, E) | 99-126 | -5.4% [-14.7, +4.2] | yes |

Final selection: ['X05', 'X06'] (N5, E); valid final response: True.
Final statuses: {'X01 (N1)': 'redundant', 'X02 (D)': 'redundant', 'X03 (N2)': 'redundant', 'X04 (N3)': 'redundant', 'X05 (N5)': 'accepted', 'X06 (E)': 'accepted', 'X07 (R)': 'rejected', 'X08 (N4)': 'rejected'}.
Support: False (-; chain []).
Confirmation of the selection: +17.6% [+1.5, +34.5] (ridge, context only: +26.2% [+9.6, +42.7]); oracle fraction 0.852.
R selected False (final status rejected); E selected True; D selected False; pure noise selected ['X05']; accepted ['X05', 'X06'].
First current experiment containing useful information: E6; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: ['E5', 'E5', 'E5', 'E5']; cited earlier failed experiments: ['E1', 'E1', 'E4', 'E1', 'E4', 'E6']; experiments used 6.
Conclusion (verbatim): Select X05 and X06. The X05+X06 pair carried the X05-X08 block's skill on days 57-84 (E2). It was strong on days 85-112 (E3: +37.3%, CI +26% to +46%). As the E6 reference on days 99-126, its MAE of 0.823 was far below the earlier no-covariate MAE of about 1.31. X01-X04 became informative alone after about day 92 (E5: +19.1%). However, they added nothing beyond X05+X06 on the newest data (E6: -5.4%, 10/18 days won), so they are redundant and are excluded. X07 and X08 are provisionally rejected on days 85-112 evidence (E4). Caveats: X05 and X06 are kept as a pair because their individual contributions were never separated. The rejections of X01-X04 and X07-X08 are dated to their test windows. If the system shifts again, the X01-X04 block, which carries partly overlapping signal, and X07/X08 should be re-screened on recent data first.
Cost: {'tokens_used': 27527, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7419, 'output_tokens': 6772, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 238}; t0-beta forecasts {'research': 238, 'evaluate': 994}; timing {'loop_started_unix': 1791197558, 'loop_finished_unix': 1791197653, 'loop_wall_s': 95}.
Integrity: material none; notes none; call failures none.

## w11: change world, FAILURE (failed: 3_r_absent, 5_supported_by_own_current_evidence)

Roles: R X07, E X08, D X03, N1 X04, N2 X02, N3 X05, N4 X01, N5 X06. Change day: 90.
Informative: True; detection: E alone, days 99-112 +15.5% [-5.6, +31.8]; E alone, days 99-126 +22.9% [+8.0, +35.5]; oracle set {E, D} (['X03', 'X08']), skill 0.255.
Confirmation (t0-beta, days 127-154): {E} vs {} +24.2% [+13.2, +35.9]; {D} vs {} +5.1% [-9.8, +17.3]; {R} vs {} -6.3% [-16.5, +3.5]; {E, D} vs {} +25.5% [+13.1, +37.1]; D given E ({E, D} vs {E}) +1.7% [-5.2, +8.8]; E given D ({E, D} vs {D}) +21.5% [+9.1, +35.3]; R given E ({E, R} vs {E}) -4.1% [-10.6, +2.8].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N4, N2, D, N1) | [] (-) | 57-84 | -2.0% [-14.3, +9.6] | no |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (N3, N5, R, E) | [] (-) | 57-84 | +14.7% [+0.2, +27.2] | no |
| E3 | 2 | ['X05', 'X06'] (N3, N5) | [] (-) | 85-112 | -4.5% [-18.5, +4.7] | no |
| E4 | 2 | ['X07', 'X08'] (R, E) | [] (-) | 85-112 | +15.4% [-0.0, +27.9] | no |
| E5 | 2 | ['X01', 'X02', 'X03', 'X04'] (N4, N2, D, N1) | [] (-) | 85-112 | +2.6% [-10.9, +14.7] | no |
| E6 | 3 | ['X05', 'X06'] (N3, N5) | ['X07', 'X08'] (R, E) | 113-126 | -1.0% [-13.2, +9.2] | yes |

Final selection: ['X07', 'X08'] (R, E); valid final response: True.
Final statuses: {'X01 (N4)': 'rejected', 'X02 (N2)': 'rejected', 'X03 (D)': 'rejected', 'X04 (N1)': 'rejected', 'X05 (N3)': 'rejected', 'X06 (N5)': 'rejected', 'X07 (R)': 'accepted', 'X08 (E)': 'accepted'}.
Support: False (-; chain []).
Confirmation of the selection: +21.1% [+8.9, +33.9] (ridge, context only: +15.6% [-5.1, +33.1]); oracle fraction 0.828.
R selected True (final status accepted); E selected True; D selected False; pure noise selected none; accepted ['X07', 'X08'].
First current experiment containing useful information: None; conditional or separation experiments: ['E3', 'E4', 'E6']; reopened stale negatives: ['E5', 'E5', 'E5', 'E5']; cited earlier failed experiments: ['E1', 'E1', 'E3', 'E4', 'E5', 'E1', 'E3', 'E4', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Select the pair {X07, X08}. It is the only set with repeated positive evidence: it is the likely source of the +14.7% in E2 on days 57-84, and it gave +15.4% in E4 on days 85-112. Adding X05+X06 did not help on the newest days (E6: -1.0%), and X01-X04 were null in two periods. Caveats: the evidence supports the pair, not each member, so X07 or X08 alone may carry the signal. E4's last week was weak, and X07+X08 was not re-tested against no covariates on days 113-126, so some decay cannot be ruled out. X01-X04 were not examined after day 112. All rejections are provisional and should be re-screened if the performance of X07+X08 drops.
Cost: {'tokens_used': 27105, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7254, 'output_tokens': 6515, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 224}; t0-beta forecasts {'research': 224, 'evaluate': 896}; timing {'loop_started_unix': 1791197553, 'loop_finished_unix': 1791197646, 'loop_wall_s': 93}.
Integrity: material none; notes none; call failures none.

## w12: null world, SUCCESS

Roles: R X07, E X08, D X06, N1 X05, N2 X02, N3 X03, N4 X04, N5 X01. Change day: none (no change in this world).
Informative: always scored (null); detection: -; oracle set none (-), skill -.
Confirmation (t0-beta, days 127-154): {E} vs {} +1.9% [-8.5, +11.2]; {D} vs {} +4.6% [-9.1, +15.5]; {R} vs {} -4.6% [-10.8, +3.3]; {E, D} vs {} +5.7% [-6.9, +16.6]; D given E ({E, D} vs {E}) +3.9% [-0.3, +8.2]; E given D ({E, D} vs {D}) +1.1% [-1.0, +4.9]; R given E ({E, R} vs {E}) -3.8% [-6.8, +1.3].

| exp | call | covariates (roles) | reference (roles) | days | skill [95%] | current |
|---|---|---|---|---|---|---|
| E1 | 1 | ['X01', 'X02', 'X03', 'X04'] (N5, N2, N3, N4) | [] (-) | 57-84 | -0.8% [-10.2, +8.2] | yes |
| E2 | 1 | ['X05', 'X06', 'X07', 'X08'] (N1, D, R, E) | [] (-) | 57-84 | -2.8% [-14.1, +5.2] | yes |
| E3 | 2 | ['X01', 'X02', 'X03', 'X04'] (N5, N2, N3, N4) | [] (-) | 85-112 | -4.5% [-12.3, +3.2] | yes |
| E4 | 2 | ['X05', 'X06', 'X07', 'X08'] (N1, D, R, E) | [] (-) | 85-112 | -2.5% [-10.6, +5.6] | yes |
| E5 | 3 | ['X01', 'X02', 'X03', 'X04'] (N5, N2, N3, N4) | [] (-) | 99-126 | -10.0% [-16.4, -0.1] | yes |
| E6 | 3 | ['X05', 'X06', 'X07', 'X08'] (N1, D, R, E) | [] (-) | 99-126 | -17.4% [-29.1, -4.1] | yes |

Final selection: [] (-); valid final response: True.
Final statuses: {'X01 (N5)': 'untested', 'X02 (N2)': 'untested', 'X03 (N3)': 'untested', 'X04 (N4)': 'untested', 'X05 (N1)': 'untested', 'X06 (D)': 'untested', 'X07 (R)': 'untested', 'X08 (E)': 'untested'}.
Support: None (-; chain []).
Confirmation of the selection: not scored; oracle fraction -.
R selected False (final status untested); E selected False; D selected False; pure noise selected none; accepted none.
First current experiment containing useful information: None; conditional or separation experiments: none; reopened stale negatives: none; cited earlier failed experiments: ['E1', 'E2', 'E1', 'E2', 'E3', 'E4', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6']; experiments used 6.
Conclusion (verbatim): Final selection: no covariates; forecast from target history only. Both covariate groups were screened in every regime available (days 57-84, 85-112, 99-126). Neither ever produced a positive skill whose interval excluded zero. On the most recent data both became significantly harmful: X01-X04 -10.0% and X05-X08 -17.4%, both with CIs below zero. The damage concentrated in days 113-126 (weekly skill down to -22% and -38%). Together with the jump in reference error, this points to a system change around day 113 that the covariates do not help with. This is not a claim that every candidate is individually useless. The evidence is group-level, and a single helpful member masked by harmful partners cannot be excluded. Still, no result gave any positive signal to justify including a candidate, and the recent regime penalises adding them. These conclusions are dated to days 57-126 and should be revisited if the process shifts again, ideally with individual screens on fresh data.
Cost: {'tokens_used': 27356, 'api_attempts': 4, 'refusals': 0, 'refusal_categories': [], 'repairs': 0, 'usage_total': {'input_tokens': 7366, 'output_tokens': 6654, 'cache_read_input_tokens': 13336, 'cache_creation_input_tokens': 0}, 't0_forecasts': 210}; t0-beta forecasts {'research': 210, 'evaluate': 882}; timing {'loop_started_unix': 1791197551, 'loop_finished_unix': 1791197633, 'loop_wall_s': 82}.
Integrity: material none; notes none; call failures none.

