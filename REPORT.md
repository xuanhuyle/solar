# Phase A result: PASS

spec_sha `6ab46db996e345de093e5b650a3cd104ec60da23a1d4a0966ed72ce68b8788dc`; run 37083726113; commit 810c45a2533ef71f6e7dd00160a9b0ee88d867de; t0 forecast-days 3696 scored (3830 t0 forecasts in all, timing and poison check included); elapsed 97.0 s.

## Competence criterion (linear worlds, 7-day context)

- **C1** (skill over k = 7-20 >= 0.05 and lower bound > 0; both comparisons): E vs none +31.3% [+27.5, +34.8]; E vs N +32.5% [+28.2, +36.5] - pass
- **C2** (skill over k = 1-6 has lower bound > 0; both comparisons): E vs none +20.5% [+15.7, +25.0]; E vs N +20.1% [+14.7, +25.1] - pass
- **C3** (in >= 20 of 40 worlds the k = 7-20 window alone has pair_skill lower bound > 0; both comparisons): E vs none 34 of 40 worlds; E vs N 36 of 40 worlds - pass

Ridge on the same criteria: C1 pass; C2 pass; C3 pass

## linear_L7: skill by days since the change (k)

| k | days | t0 E vs none | t0 E vs N | t0 N vs none | ridge E vs none | ridge E vs N | ridge N vs none |
|---|---|---|---|---|---|---|---|
| 0-0 | 40 | -4.7% [-19.4, +6.7] | +2.5% [-10.1, +13.5] | -7.4% [-16.4, +0.3] | -7.1% [-15.0, +0.0] | -10.0% [-20.0, -0.5] | +2.6% [-4.8, +10.0] |
| 1-3 | 120 | +15.5% [+9.1, +21.9] | +15.4% [+9.2, +21.1] | +0.0% [-4.9, +5.0] | +14.3% [+4.1, +23.8] | +14.6% [+5.3, +23.0] | -0.3% [-5.7, +4.5] |
| 4-6 | 120 | +25.6% [+20.2, +30.6] | +24.9% [+18.1, +30.8] | +0.9% [-3.9, +5.7] | +33.1% [+25.7, +39.7] | +30.2% [+22.8, +36.6] | +4.2% [-1.1, +9.3] |
| 7-13 | 280 | +33.5% [+28.8, +37.8] | +34.0% [+28.7, +38.9] | -0.7% [-4.2, +2.6] | +40.1% [+35.3, +44.8] | +42.6% [+37.5, +47.3] | -4.2% [-8.5, +0.5] |
| 14-20 | 280 | +28.9% [+24.1, +33.5] | +31.0% [+25.8, +35.9] | -3.0% [-6.7, +0.6] | +39.5% [+33.2, +45.4] | +41.9% [+35.3, +48.1] | -4.3% [-8.1, -0.6] |

How soon (every later bin's lower bound above 0): t0 E vs none k = 1-3; t0 E vs N k = 1-3; ridge E vs none k = 1-3; ridge E vs N k = 1-3.

Mean absolute error by bin, each arm on its own (linear_L7):

| k | t0 none | t0 E | t0 N | ridge none | ridge E | ridge N |
|---|---|---|---|---|---|---|
| 0-0 | 1.398 | 1.463 | 1.501 | 1.478 | 1.583 | 1.439 |
| 1-3 | 1.312 | 1.109 | 1.311 | 1.503 | 1.288 | 1.508 |
| 4-6 | 1.300 | 0.968 | 1.289 | 1.508 | 1.008 | 1.444 |
| 7-13 | 1.370 | 0.912 | 1.381 | 1.529 | 0.916 | 1.594 |
| 14-20 | 1.303 | 0.926 | 1.342 | 1.504 | 0.910 | 1.568 |

## hinge_L7: skill by days since the change (k)

| k | days | t0 E vs none | ridge E vs none |
|---|---|---|---|
| 0-0 | 12 | -1.2% [-29.7, +17.7] | -27.3% [-51.4, -5.9] |
| 1-3 | 36 | -0.5% [-18.5, +12.7] | +5.2% [-2.2, +12.1] |
| 4-6 | 36 | +10.3% [-1.2, +19.1] | +10.4% [-5.9, +22.5] |
| 7-13 | 84 | +22.4% [+12.3, +32.4] | +23.3% [+7.8, +35.3] |
| 14-20 | 84 | +18.5% [+5.9, +30.4] | +19.7% [+4.4, +32.9] |

How soon (every later bin's lower bound above 0): t0 E vs none k = 7-13; ridge E vs none k = 7-13.

Mean absolute error by bin, each arm on its own (hinge_L7):

| k | t0 none | t0 E | ridge none | ridge E |
|---|---|---|---|---|
| 0-0 | 1.143 | 1.157 | 1.076 | 1.370 |
| 1-3 | 0.956 | 0.961 | 1.210 | 1.147 |
| 4-6 | 1.094 | 0.981 | 1.243 | 1.114 |
| 7-13 | 1.406 | 1.091 | 1.527 | 1.170 |
| 14-20 | 1.342 | 1.094 | 1.567 | 1.258 |

## linear_L28: skill by days since the change (k)

| k | days | t0 E vs none | ridge E vs none |
|---|---|---|---|
| 0-0 | 8 | +8.1% [-11.6, +20.7] | -2.7% [-13.3, +9.4] |
| 1-3 | 24 | +8.4% [-5.3, +23.9] | +9.7% [+1.0, +18.7] |
| 4-6 | 24 | +11.1% [-0.1, +20.9] | +10.0% [-0.1, +19.8] |
| 7-13 | 56 | +25.3% [+18.0, +30.6] | +19.1% [+11.8, +26.6] |
| 14-27 | 112 | +34.1% [+28.2, +40.5] | +24.6% [+17.9, +31.5] |
| 28-41 | 112 | +34.6% [+30.6, +37.9] | +33.0% [+26.6, +39.9] |

How soon (every later bin's lower bound above 0): t0 E vs none k = 7-13; ridge E vs none k = 7-13.

Mean absolute error by bin, each arm on its own (linear_L28):

| k | t0 none | t0 E | ridge none | ridge E |
|---|---|---|---|---|
| 0-0 | 1.527 | 1.403 | 1.092 | 1.121 |
| 1-3 | 1.010 | 0.925 | 1.058 | 0.955 |
| 4-6 | 1.254 | 1.115 | 1.311 | 1.180 |
| 7-13 | 1.443 | 1.078 | 1.295 | 1.048 |
| 14-27 | 1.228 | 0.810 | 1.177 | 0.887 |
| 28-41 | 1.260 | 0.824 | 1.285 | 0.862 |

Control k = 0 (no post-change day in context): t0 E vs none -4.7% [-19.4, +6.7]; t0 E vs N +2.5% [-10.1, +13.5]; t0 N vs none -7.4% [-16.4, +0.3]
Integrity: {'calibration_reproduced': True, 'sanitised_outputs': 0, 'poison': True}
