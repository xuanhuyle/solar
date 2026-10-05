# Final kernel result: FULL KERNEL PROVEN FOR THIS BENCHMARK

Rule: row 3: K episode successes 6 of 8 (c1e3, c2e3, c3e2, c3e3, c4e2, c4e3); null successes 2 of 2; episodes with an incorrect individual approval 0 (none); median oracle fraction 1.000 over 6 episodes

Closing line: MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST

Spec a28b39a5aad3e6a548fff903e57b1b93edae1635af5b8a63b71dbf043f979694; run 37332048132; commit ea9902d7fecd9a62682d7fef3940193076645b9d; lesson 1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb.
Material integrity issues: none. Generator defects: none. Missing scored trajectories: none.

K strong 4 of 6, null success 2 of 2, partial 0; F strong 5 of 6, null 2 of 2. K median oracle fraction 1.000. Pairs {'TIE': 5, 'F WIN': 1, 'K WIN': 2}. Tokens 711382; attempts 83; refusals 0; repairs 3; t0 forecasts (research) 4746; evaluate 1197.4 s.

Caveats: Four synthetic companies, eight scored episodes, one stochastic trajectory per condition and episode. Synthetic worlds from one generator family: a pass does not establish real-market performance or commercial value; 'proven' means demonstrated against this frozen benchmark at its thresholds. The benchmark tests predictive information, not causal identification, and does not measure the full human or engineering cost of a conventional workflow.

## c1e1 (S2, E1; non-null)

Regime: Configuration North: both treatment works in service, network fed from the north reservoirs. Useful: ['X02'] ['Visitor-occupancy index']; stale []. Informative: True; oracle {X02}.

- E1: strong True partial False []; headline ['X02'] | ref ['X03', 'X07'] (conditional on X03, X07), confirmation +24.4% [+9.1, +32.9]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X02']
  - E1 (call 1): ['X05'] | ref - | 28 d days 57-84 | -3.7% [-13.6, +5.8]
  - E2 (call 1): ['X02', 'X03', 'X07'] | ref - | 28 d days 57-84 | +26.3% [+14.7, +34.4]
  - E3 (call 1): ['X01', 'X04', 'X08'] | ref - | 28 d days 57-84 | -4.5% [-21.0, +8.6]
  - E4 (call 2): ['X02'] | ref ['X03', 'X07'] | 28 d days 85-112 | +20.8% [+7.7, +32.7]
  - E5 (call 2): ['X03'] | ref ['X02', 'X07'] | 28 d days 85-112 | -1.2% [-10.9, +8.9]
  - E6 (call 3): ['X05', 'X06', 'X08', 'X04'] | ref ['X02', 'X07'] | 14 d days 113-126 | -21.3% [-40.5, -7.3]

## c1e2 (S2, P3; non-null)

Regime: Configuration South: one treatment works in service, part of the area fed by a bulk import. Useful: ['X05', 'X06'] ['Area air-temperature forecast', 'Second-service temperature forecast']; stale ['X02']. Informative: True; oracle {X06}.

- F: strong False partial False ['4_headline_confirmation_lower_bound_above_0']; headline ['X05', 'X08'] | ref - (set (attribution unresolved)), confirmation +17.2% [-5.3, +33.3]; discovery index None; experiments 6; oracle fraction 0.557; incorrect approvals none; selection ['X01', 'X05']
  - E1 (call 1): ['X05', 'X08'] | ref - | 28 d days 57-84 | +38.9% [+22.9, +51.1]
  - E2 (call 1): ['X02', 'X03', 'X07'] | ref - | 28 d days 57-84 | +1.6% [-10.6, +13.4]
  - E3 (call 1): ['X01', 'X04'] | ref - | 28 d days 57-84 | +14.4% [+5.7, +24.0]
  - E4 (call 2): ['X08'] | ref ['X05'] | 28 d days 85-112 | -2.9% [-7.8, +2.4]
  - E5 (call 2): ['X04'] | ref ['X01'] | 28 d days 85-112 | -5.4% [-11.8, -0.6]
  - E6 (call 3): ['X02', 'X03', 'X07'] | ref ['X01', 'X05'] | 28 d days 99-126 | -3.3% [-14.1, +6.5]
- K: strong False partial False ['3_headline_contains_useful_candidate', '4_headline_confirmation_lower_bound_above_0']; headline ['X01', 'X04'] | ref - (set (attribution unresolved)), confirmation +0.2% [-10.2, +15.5]; discovery index None; experiments 6; oracle fraction 0.007; incorrect approvals none; selection ['X05', 'X06']
  - E1 (call 1): ['X02', 'X03', 'X07'] | ref - | 28 d days 57-84 | +1.6% [-10.6, +13.4]
  - E2 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | +44.8% [+34.5, +53.0]
  - E3 (call 1): ['X01', 'X04'] | ref - | 28 d days 57-84 | +14.4% [+5.7, +24.0]
  - E4 (call 2): ['X01', 'X04'] | ref ['X05', 'X06'] | 28 d days 85-112 | -0.6% [-10.3, +7.0]
  - E5 (call 2): ['X08'] | ref ['X05', 'X06'] | 28 d days 85-112 | -0.1% [-3.4, +4.3]
  - E6 (call 3): ['X02', 'X03', 'X07'] | ref ['X05', 'X06'] | 28 d days 99-126 | -1.5% [-8.2, +3.5]
  - memory use: {'memory_entries': 6, 'prior_positive_used': ['X02', 'X03', 'X07'], 'stale_negative_reopened': ['X01', 'X04', 'X05', 'X06', 'X08'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X02', 'X03', 'X07'], 'prior_unresolved_resolved': [], 'memory_mentions': 23, 'negatives_in_memory': ['X01', 'X03', 'X04', 'X05', 'X06', 'X08'], 'memory_ignored': False}
- pair: TIE (neither condition met a win rule)

## c1e3 (S2, P4; null)

Regime: Configuration Combined: the merged network after the integration of the neighbouring company. Useful: [] []; stale ['X02', 'X05', 'X06']. Informative: None; oracle None.

- F: null success True []; headline none; discovery index None; experiments 6; oracle fraction -; incorrect approvals none; selection []
  - E1 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | -0.6% [-16.2, +11.3]
  - E2 (call 1): ['X02', 'X03', 'X07'] | ref - | 28 d days 57-84 | -4.2% [-17.8, +9.0]
  - E3 (call 1): ['X01', 'X04'] | ref - | 28 d days 57-84 | -6.6% [-16.9, +3.1]
  - E4 (call 2): ['X05', 'X06', 'X08'] | ref - | 28 d days 85-112 | +5.8% [-11.0, +17.1]
  - E5 (call 2): ['X02', 'X03', 'X07'] | ref - | 28 d days 85-112 | -1.6% [-9.2, +6.3]
  - E6 (call 3): ['X05'] | ref - | 14 d days 113-126 | -4.6% [-20.7, +7.0]
- K: null success True []; headline none; discovery index None; experiments 6; oracle fraction -; incorrect approvals none; selection []
  - E1 (call 1): ['X02', 'X03', 'X07'] | ref - | 28 d days 57-84 | -4.2% [-17.8, +9.0]
  - E2 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | -0.6% [-16.2, +11.3]
  - E3 (call 1): ['X01', 'X04'] | ref - | 28 d days 57-84 | -6.6% [-16.9, +3.1]
  - E4 (call 2): ['X02', 'X03', 'X07'] | ref - | 28 d days 85-112 | -1.6% [-9.2, +6.3]
  - E5 (call 2): ['X05', 'X06', 'X08'] | ref - | 28 d days 85-112 | +5.8% [-11.0, +17.1]
  - E6 (call 3): ['X05', 'X06', 'X08'] | ref - | 14 d days 113-126 | -5.4% [-35.5, +17.4]
  - memory use: {'memory_entries': 12, 'prior_positive_used': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07', 'X08'], 'stale_negative_reopened': [], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07', 'X08'], 'prior_unresolved_resolved': [], 'memory_mentions': 23, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07', 'X08'], 'memory_ignored': False}
- pair: TIE (neither condition met a win rule)

## c2e1 (S1, E1; non-null)

Regime: Format mix A: mostly large-format stores, weekly-shop focus. Useful: ['X06'] ['Footfall forecast']; stale []. Informative: True; oracle {X06}.

- E1: strong True partial False []; headline ['X06'] | ref ['X05', 'X08'] (conditional on X05, X08), confirmation +32.8% [+16.5, +45.3]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X06']
  - E1 (call 1): ['X02', 'X03', 'X04'] | ref - | 28 d days 57-84 | -9.5% [-19.1, +2.1]
  - E2 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | +25.3% [+10.9, +38.0]
  - E3 (call 1): ['X01', 'X07'] | ref - | 28 d days 57-84 | -7.3% [-16.3, +0.5]
  - E4 (call 2): ['X06'] | ref ['X05', 'X08'] | 28 d days 85-112 | +25.1% [+11.0, +34.3]
  - E5 (call 2): ['X08'] | ref ['X05', 'X06'] | 28 d days 85-112 | -9.1% [-23.6, +1.5]
  - E6 (call 3): ['X03', 'X04', 'X01', 'X07'] | ref ['X05', 'X06'] | 28 d days 99-126 | -3.9% [-15.6, +6.1]

## c2e2 (S1, P2; non-null)

Regime: Format mix B: mostly convenience-format stores after the store conversions. Useful: ['X02', 'X03'] ['Planned promotion intensity', 'Recorded promotion intensity']; stale ['X06']. Informative: True; oracle {X02}.

- F: strong True partial False []; headline ['X03'] | ref - (individual), confirmation +19.3% [+5.9, +32.5]; discovery index 5; experiments 6; oracle fraction 0.560; incorrect approvals none; selection ['X03']
  - E1 (call 1): ['X02', 'X03', 'X04'] | ref - | 28 d days 57-84 | +41.7% [+22.8, +56.4]
  - E2 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | -4.6% [-23.2, +9.9]
  - E3 (call 1): ['X01', 'X07'] | ref - | 28 d days 57-84 | -9.7% [-19.1, -0.5]
  - E4 (call 2): ['X03'] | ref - | 28 d days 85-112 | +20.0% [+9.0, +31.3]
  - E5 (call 2): ['X02', 'X04'] | ref ['X03'] | 28 d days 85-112 | +17.2% [+1.5, +29.7]
  - E6 (call 3): ['X05', 'X06', 'X08', 'X01'] | ref ['X03'] | 28 d days 99-126 | -10.8% [-19.8, -2.9]
- K: strong False partial False ['4_headline_confirmation_lower_bound_above_0']; headline ['X02'] | ref ['X03', 'X04'] (conditional on X03, X04), confirmation +8.9% [-7.2, +21.4]; discovery index None; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X02']
  - E1 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | -4.6% [-23.2, +9.9]
  - E2 (call 1): ['X02', 'X03', 'X04'] | ref - | 28 d days 57-84 | +41.7% [+22.8, +56.4]
  - E3 (call 1): ['X01', 'X07'] | ref - | 28 d days 57-84 | -9.7% [-19.1, -0.5]
  - E4 (call 2): ['X03'] | ref ['X02', 'X04'] | 28 d days 85-112 | +4.2% [-4.2, +16.6]
  - E5 (call 2): ['X02'] | ref ['X03', 'X04'] | 28 d days 85-112 | +18.8% [+2.0, +30.8]
  - E6 (call 3): ['X04'] | ref ['X02', 'X03'] | 28 d days 99-126 | +1.7% [-2.3, +6.0]
  - memory use: {'memory_entries': 6, 'prior_positive_used': ['X05', 'X06', 'X08'], 'stale_negative_reopened': ['X01', 'X02', 'X03', 'X04', 'X07'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X05', 'X06', 'X08'], 'prior_unresolved_resolved': [], 'memory_mentions': 19, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X07', 'X08'], 'memory_ignored': False}
- pair: F WIN (strong success where the other was not)

## c2e3 (S1, P1; non-null)

Regime: Format mix A: mostly large-format stores, weekly-shop focus. Useful: ['X06'] ['Footfall forecast']; stale ['X02', 'X03']. Informative: True; oracle {X06}.

- F: strong True partial False []; headline ['X06'] | ref - (individual), confirmation +31.3% [+21.6, +39.3]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X06']
  - E1 (call 1): ['X02', 'X03', 'X04'] | ref - | 28 d days 57-84 | +1.3% [-8.1, +9.3]
  - E2 (call 1): ['X05', 'X06', 'X08'] | ref - | 28 d days 57-84 | +34.6% [+21.4, +47.7]
  - E3 (call 1): ['X01', 'X07'] | ref - | 28 d days 57-84 | +2.9% [-7.3, +11.8]
  - E4 (call 2): ['X06'] | ref - | 28 d days 85-112 | +33.6% [+21.0, +45.2]
  - E5 (call 2): ['X05', 'X08'] | ref ['X06'] | 28 d days 85-112 | -3.4% [-14.0, +6.2]
  - E6 (call 3): ['X02', 'X03', 'X04'] | ref ['X06'] | 28 d days 99-126 | +4.0% [-4.9, +11.9]
- K: strong True partial False []; headline ['X06'] | ref - (individual), confirmation +31.3% [+21.6, +39.3]; discovery index 3; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X06']
  - E1 (call 1): ['X06'] | ref - | 28 d days 57-84 | +33.1% [+18.6, +45.6]
  - E2 (call 1): ['X02', 'X03', 'X04'] | ref - | 28 d days 57-84 | +1.3% [-8.1, +9.3]
  - E3 (call 1): ['X01', 'X05', 'X07', 'X08'] | ref ['X06'] | 28 d days 57-84 | +0.5% [-12.9, +13.2]
  - E4 (call 2): ['X06'] | ref - | 28 d days 85-112 | +33.6% [+21.0, +45.2]
  - E5 (call 2): ['X02', 'X03', 'X04'] | ref ['X06'] | 28 d days 85-112 | +0.7% [-5.7, +5.4]
  - E6 (call 3): ['X01', 'X05', 'X07', 'X08'] | ref ['X06'] | 28 d days 99-126 | +1.8% [-11.2, +13.3]
  - memory use: {'memory_entries': 12, 'prior_positive_used': ['X02', 'X03', 'X04', 'X05', 'X06', 'X08'], 'stale_negative_reopened': ['X01', 'X07'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X02', 'X03', 'X04'], 'prior_unresolved_resolved': ['M2'], 'memory_mentions': 24, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07', 'X08'], 'memory_ignored': False}
- pair: K WIN (first strong finding after 3 experiments against 5)

## c3e1 (S4, E1; non-null)

Regime: Role 1: regional hub serving the surrounding counties. Useful: ['X01', 'X08'] ["Largest client's order forecast", 'Client order forecast from the shared portal']; stale []. Informative: True; oracle {X01, X08}.

- E1: strong True partial False []; headline ['X08'] | ref - (individual), confirmation +30.0% [+15.9, +40.3]; discovery index 3; experiments 6; oracle fraction 0.996; incorrect approvals none; selection ['X08']
  - E1 (call 1): ['X08'] | ref - | 28 d days 57-84 | +37.7% [+27.1, +47.8]
  - E2 (call 1): ['X05', 'X02'] | ref - | 28 d days 57-84 | +3.6% [-3.9, +11.8]
  - E3 (call 1): ['X03', 'X04', 'X06', 'X07'] | ref - | 28 d days 57-84 | -1.5% [-9.8, +8.3]
  - E4 (call 2): ['X08'] | ref - | 28 d days 85-112 | +44.1% [+29.1, +55.8]
  - E5 (call 2): ['X01'] | ref ['X08'] | 28 d days 85-112 | +1.1% [-4.8, +6.5]
  - E6 (call 2): ['X05', 'X02'] | ref ['X08'] | 28 d days 85-112 | +0.5% [-3.8, +4.1]

## c3e2 (S4, P4; null)

Regime: Role 2: national overflow hub taking diverted volume from other hubs. Useful: [] []; stale ['X01', 'X08']. Informative: None; oracle None.

- F: null success True []; headline none; discovery index None; experiments 6; oracle fraction -; incorrect approvals none; selection []
  - E1 (call 1): ['X08', 'X01', 'X03'] | ref - | 28 d days 57-84 | -2.8% [-11.1, +4.6]
  - E2 (call 1): ['X05', 'X02', 'X04'] | ref - | 28 d days 57-84 | -6.7% [-21.3, +3.0]
  - E3 (call 1): ['X06', 'X07'] | ref - | 28 d days 57-84 | -4.6% [-17.4, +5.6]
  - E4 (call 2): ['X08', 'X01', 'X03'] | ref - | 28 d days 85-112 | -3.6% [-14.2, +5.0]
  - E5 (call 2): ['X05', 'X02', 'X04'] | ref - | 28 d days 85-112 | -4.0% [-21.9, +9.3]
  - E6 (call 2): ['X06', 'X07'] | ref - | 28 d days 85-112 | -2.1% [-8.1, +2.1]
- K: null success True []; headline none; discovery index None; experiments 6; oracle fraction -; incorrect approvals none; selection []
  - E1 (call 1): ['X08'] | ref - | 28 d days 57-84 | -2.3% [-11.9, +5.5]
  - E2 (call 1): ['X02', 'X04', 'X05'] | ref - | 28 d days 57-84 | -6.7% [-21.3, +3.0]
  - E3 (call 1): ['X03', 'X06', 'X07'] | ref - | 28 d days 57-84 | -2.6% [-15.3, +7.8]
  - E4 (call 2): ['X01', 'X03', 'X06', 'X07'] | ref - | 28 d days 85-112 | -6.0% [-17.6, +1.7]
  - E5 (call 2): ['X02', 'X04', 'X05', 'X08'] | ref - | 28 d days 85-112 | -5.7% [-23.3, +7.9]
  - E6 (call 3): ['X02', 'X04', 'X05'] | ref - | 28 d days 99-126 | -2.6% [-24.7, +16.0]
  - memory use: {'memory_entries': 5, 'prior_positive_used': ['X08'], 'stale_negative_reopened': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X08'], 'prior_unresolved_resolved': [], 'memory_mentions': 19, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07'], 'memory_ignored': False}
- pair: TIE (neither condition met a win rule)

## c3e3 (S4, P3; non-null)

Regime: Role 3: hub after the commissioning of the new automated sorting line. Useful: ['X05'] ['Trunk-road congestion forecast']; stale ['X01', 'X08']. Informative: True; oracle {X05}.

- F: strong True partial False []; headline ['X05'] | ref ['X02', 'X04'] (conditional on X02, X04), confirmation +32.2% [+16.0, +45.5]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X05']
  - E1 (call 1): ['X08', 'X01', 'X03'] | ref - | 28 d days 57-84 | -2.3% [-15.2, +11.2]
  - E2 (call 1): ['X05', 'X02', 'X04'] | ref - | 28 d days 57-84 | +42.6% [+32.9, +49.0]
  - E3 (call 1): ['X06', 'X07'] | ref - | 28 d days 57-84 | +9.6% [+3.5, +16.6]
  - E4 (call 2): ['X04'] | ref ['X02', 'X05'] | 28 d days 85-112 | -6.3% [-13.2, -2.1]
  - E5 (call 2): ['X05'] | ref ['X02', 'X04'] | 28 d days 85-112 | +44.1% [+35.8, +53.8]
  - E6 (call 3): ['X02'] | ref ['X05'] | 28 d days 99-126 | -4.8% [-11.2, +1.2]
- K: strong True partial False []; headline ['X05'] | ref ['X02'] (conditional on X02), confirmation +34.8% [+21.1, +46.6]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X02', 'X05']
  - E1 (call 1): ['X08'] | ref - | 28 d days 57-84 | +5.4% [-5.3, +13.7]
  - E2 (call 1): ['X03', 'X04'] | ref - | 28 d days 57-84 | +4.2% [-7.6, +14.2]
  - E3 (call 1): ['X02', 'X05', 'X06', 'X07'] | ref - | 28 d days 57-84 | +44.4% [+31.2, +54.2]
  - E4 (call 2): ['X06', 'X07'] | ref ['X02', 'X05'] | 28 d days 85-112 | -7.3% [-15.1, -1.9]
  - E5 (call 2): ['X02', 'X05'] | ref ['X06', 'X07'] | 28 d days 85-112 | +41.7% [+30.2, +53.3]
  - E6 (call 3): ['X05'] | ref ['X02'] | 28 d days 99-126 | +41.1% [+22.8, +54.5]
  - memory use: {'memory_entries': 10, 'prior_positive_used': ['X08'], 'stale_negative_reopened': ['X02', 'X03', 'X04', 'X05', 'X06', 'X07'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X08'], 'prior_unresolved_resolved': [], 'memory_mentions': 22, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X05', 'X06', 'X07', 'X08'], 'memory_ignored': False}
- pair: TIE (neither condition met a win rule)

## c4e1 (S3, E1; non-null)

Regime: Tenant mix 1: mostly enterprise tenants on long contracts. Useful: ['X06'] ['Solar-irradiance forecast']; stale []. Informative: True; oracle {X06}.

- E1: strong True partial False []; headline ['X01', 'X06'] | ref ['X02'] (set (attribution unresolved) given X02), confirmation +28.5% [+8.4, +41.1]; discovery index 5; experiments 6; oracle fraction 0.987; incorrect approvals none; selection ['X06', 'X01']
  - E1 (call 1): ['X02', 'X06', 'X01'] | ref - | 28 d days 57-84 | +42.3% [+28.8, +50.9]
  - E2 (call 1): ['X04', 'X07', 'X05'] | ref - | 28 d days 57-84 | -4.2% [-21.7, +10.5]
  - E3 (call 1): ['X08', 'X03'] | ref - | 28 d days 57-84 | -5.7% [-16.9, +5.4]
  - E4 (call 2): ['X02'] | ref - | 28 d days 85-112 | +1.1% [-8.6, +10.4]
  - E5 (call 2): ['X06', 'X01'] | ref ['X02'] | 28 d days 85-112 | +31.3% [+16.5, +39.7]
  - E6 (call 3): ['X04', 'X05', 'X08', 'X03'] | ref ['X06', 'X01'] | 28 d days 99-126 | +2.5% [-6.9, +10.9]

## c4e2 (S3, P1; non-null)

Regime: Tenant mix 1: mostly enterprise tenants on long contracts. Useful: ['X06'] ['Solar-irradiance forecast']; stale []. Informative: True; oracle {X06}.

- F: strong True partial False []; headline ['X06'] | ref ['X01', 'X02'] (conditional on X01, X02), confirmation +29.4% [+16.2, +40.6]; discovery index 6; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X06']
  - E1 (call 1): ['X04'] | ref - | 28 d days 57-84 | -6.5% [-24.9, +8.2]
  - E2 (call 1): ['X02', 'X06', 'X01'] | ref - | 28 d days 57-84 | +30.9% [+12.4, +48.0]
  - E3 (call 1): ['X05', 'X08', 'X03'] | ref - | 28 d days 57-84 | -0.5% [-15.3, +13.4]
  - E4 (call 2): ['X02'] | ref ['X06', 'X01'] | 28 d days 85-112 | -3.6% [-8.6, +1.4]
  - E5 (call 2): ['X06'] | ref ['X02', 'X01'] | 28 d days 85-112 | +30.2% [+18.0, +41.7]
  - E6 (call 2): ['X01'] | ref ['X02', 'X06'] | 28 d days 85-112 | -1.0% [-5.6, +2.5]
- K: strong True partial False []; headline ['X06'] | ref ['X01'] (conditional on X01), confirmation +23.6% [+9.9, +36.3]; discovery index 3; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X06']
  - E1 (call 1): ['X01', 'X06'] | ref - | 28 d days 57-84 | +34.6% [+20.2, +48.6]
  - E2 (call 1): ['X04', 'X05', 'X07'] | ref - | 28 d days 57-84 | -2.7% [-23.7, +16.8]
  - E3 (call 1): ['X02', 'X03', 'X08'] | ref ['X01', 'X06'] | 28 d days 57-84 | -10.4% [-21.8, +0.3]
  - E4 (call 2): ['X01'] | ref ['X06'] | 28 d days 85-112 | -0.7% [-6.8, +5.8]
  - E5 (call 2): ['X06'] | ref ['X01'] | 28 d days 85-112 | +33.2% [+19.3, +45.7]
  - E6 (call 3): ['X02', 'X04', 'X05', 'X08'] | ref ['X06'] | 28 d days 99-126 | -4.5% [-13.7, +3.3]
  - memory use: {'memory_entries': 6, 'prior_positive_used': ['X01', 'X02', 'X06'], 'stale_negative_reopened': [], 'stable_negative_avoided': [], 'stale_positive_abandoned': [], 'prior_unresolved_resolved': ['M1', 'M5'], 'memory_mentions': 24, 'negatives_in_memory': ['X02', 'X03', 'X04', 'X05', 'X07', 'X08'], 'memory_ignored': False}
- pair: K WIN (first strong finding after 3 experiments against 6)

## c4e3 (S3, P2; non-null)

Regime: Tenant mix 2: mostly research and model-training tenants. Useful: ['X05'] ['Tenant deployment calendar']; stale ['X06']. Informative: True; oracle {X05}.

- F: strong True partial False []; headline ['X05', 'X07'] | ref ['X04'] (set (attribution unresolved) given X04), confirmation +22.0% [+13.1, +30.7]; discovery index 5; experiments 6; oracle fraction 0.747; incorrect approvals none; selection ['X05', 'X07']
  - E1 (call 1): ['X04', 'X07', 'X05'] | ref - | 28 d days 57-84 | +27.5% [+13.0, +41.8]
  - E2 (call 1): ['X02', 'X06', 'X01'] | ref - | 28 d days 57-84 | -7.0% [-16.4, +1.5]
  - E3 (call 1): ['X08', 'X03'] | ref - | 28 d days 57-84 | -9.7% [-19.5, +0.0]
  - E4 (call 2): ['X04'] | ref - | 28 d days 85-112 | -4.6% [-13.7, +4.5]
  - E5 (call 2): ['X05', 'X07'] | ref ['X04'] | 28 d days 85-112 | +27.2% [+11.8, +39.9]
  - E6 (call 3): ['X02', 'X06', 'X08', 'X03'] | ref ['X05', 'X07'] | 28 d days 99-126 | -4.5% [-17.1, +6.2]
- K: strong True partial False []; headline ['X05'] | ref ['X04'] (conditional on X04), confirmation +25.1% [+15.7, +34.5]; discovery index 5; experiments 6; oracle fraction 1.000; incorrect approvals none; selection ['X05']
  - E1 (call 1): ['X04', 'X05', 'X07'] | ref - | 28 d days 57-84 | +27.5% [+13.0, +41.8]
  - E2 (call 1): ['X01', 'X02', 'X06'] | ref - | 28 d days 57-84 | -7.0% [-16.4, +1.5]
  - E3 (call 1): ['X03', 'X08'] | ref - | 28 d days 57-84 | -9.7% [-19.5, +0.0]
  - E4 (call 2): ['X04'] | ref ['X05'] | 28 d days 85-112 | -6.7% [-14.5, -0.1]
  - E5 (call 2): ['X05'] | ref ['X04'] | 28 d days 85-112 | +30.2% [+18.3, +41.5]
  - E6 (call 3): ['X07'] | ref ['X05'] | 28 d days 99-126 | -5.4% [-12.5, +1.6]
  - memory use: {'memory_entries': 12, 'prior_positive_used': ['X01', 'X02', 'X06'], 'stale_negative_reopened': ['X03', 'X04', 'X05', 'X07', 'X08'], 'stable_negative_avoided': [], 'stale_positive_abandoned': ['X01', 'X02', 'X06'], 'prior_unresolved_resolved': [], 'memory_mentions': 22, 'negatives_in_memory': ['X01', 'X02', 'X03', 'X04', 'X05', 'X07', 'X08'], 'memory_ignored': False}
- pair: TIE (neither condition met a win rule)

