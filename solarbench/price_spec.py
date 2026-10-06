"""Experiment 4, "t0 on French day-ahead prices": the frozen specification.

Everything a result of Experiment 4 is read against lives in ``PRICE_SPEC``:
the target and its publication rule, the decision time, the periods, the four
primary probes with their comparators, metrics and success rules, the known-
answer gates, the verdict states, the reading table and the rule for carrying a
result into the engine vault. It was committed (and ``PRICE_SPEC_SHA256``
pinned) before any French price was fetched, after an adversarial review of the
draft (workflow wf_40ed0e82-455: 36 confirmed findings, all resolved here), and
must not be edited afterwards; the code that runs it is built around it.

``AVAIL`` is the one exception: a few facts only a coverage-only run can
establish. They are filled once by ``run_prices.py avail`` - which never
forecasts or scores anything - and committed before the first forecast. They
are not part of the hash; the runner refuses to run while any is ``None``.

Standard library only, so the spec can be read and hashed without the
forecasting stack.
"""

from __future__ import annotations

from engine.canon import sha256_of

EXPERIMENT = "exp4-prices/1"

#: The CC BY 4.0 attribution printed with every published price result.
ATTRIBUTION = "Day-ahead prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE)"

TEST_ORIGINS = ["2024-01-01", "2024-12-31", "2025-12-31", "2024-03-31", "2024-06-26", "2024-10-27", "2025-03-30",
                "2025-09-30", "2025-10-01", "2025-10-02", "2025-10-26"]

PRICE_SPEC: dict = {
    "experiment": EXPERIMENT,
    "status": "discovery-grade: 2024-2025 French prices are public and already studied; 2025 is consumed "
              "(explorable, never confirmable). No result here counts as confirmed.",
    # ------------------------------------------------------------------ target
    "target": {
        "series": "French bidding-zone day-ahead auction price (SDAC), EUR/MWh",
        "grid": "hourly, UTC-indexed; after target.stamp_rule is applied each stamp is the start of its hour",
        "stamp_rule": (
            "PRICE_STAMP (AVAIL) says which period a raw source stamp t labels: 'start' = [t, t + len), 'end' = "
            "[t - len, t), len = 60 min before 2025-10-01 00:00 Paris and 15 min from then. It is decided only by "
            "content, never by stamp patterns, day counts or SMARD agreement (identical under both conventions): on "
            "the 24-hour Paris days of periods.fetch_prices_overlap_check the raw Energy-Charts values are mapped to "
            "Paris local hours once as 'start' and once as 'end' and compared with EPF-FR (Zenodo 4624805 FR.csv, "
            "whose row stamped local h is the hour starting h). PRICE_STAMP is the convention under which >= 99% of "
            "the hours present under both mappings agree with FR.csv within 0.01 EUR/MWh, provided the other agrees "
            "on < 50%. If Energy-Charts has no complete 2015-2016 days, the same test is run on SMARD's raw 2015-2016 "
            "stamps, and SMARD's convention is transferred to Energy-Charts only if their raw stamps agree within "
            "0.01 EUR/MWh on >= 99.9% of the hours compared under sources.agreement_rule. Any other outcome stops "
            "the run; the owner decides and the decision is reported as an amendment. If PRICE_STAMP is 'end', "
            "every raw stamp up to and including 2025-10-01 00:00 Paris moves back 60 min and every later one 15 "
            "min, right after parsing and before quarter-hour grouping, window building, poisoning and every "
            "publication-rule test. The seal works on raw stamps (sources.scored.params); under 'end' the last "
            "quarter-hour of 2025-12-31 is therefore never fetched and that day is dropped under target.missing"),
        "quarter_hours": "from delivery day 2025-10-01 (15-minute products) each UTC hour is the arithmetic mean of "
                         "its four quarter-hours; the hour is NaN unless all four are present; a :00 value alone "
                         "is never used",
        "scored_hours": "the real 23, 24 or 25 hours of each Europe/Paris delivery day D",
        "clipping": "none anywhere (prices can be negative)",
        "outliers": "none removed; concentration and bootstrap-sensitivity tables are reported instead",
        "missing": "a day with any missing target hour is excluded from every comparison (counted)",
    },
    "sources": {
        "scored": {"name": "Energy-Charts", "endpoint": "https://api.energy-charts.info/price",
                   "params": ("bzn=FR; start and end are integer unix seconds (never the day format, whose end means "
                              "23:59 local); per request (one calendar month): start = the Paris-local midnight "
                              "opening the chunk's first day, end = the Paris-local midnight closing its last day "
                              "minus 1 s (the API's end is inclusive), so chunks are disjoint and cover every stamp; "
                              "a fetch ending 2025-12-31 ends at 1767221999 = 2025-12-31 23:59:59 Paris. Every "
                              "returned stamp must lie in [start, end], checked before any byte is cached, or the "
                              "read fails; the bound is never widened"),
                   "licence_expected": "CC BY 4.0 from Bundesnetzagentur | SMARD.de",
                   "licence_rule": ("every Energy-Charts response used must carry a license_info containing both "
                                    "'CC BY 4.0' and 'Bundesnetzagentur | SMARD.de' (case-sensitive); the avail run "
                                    "writes the distinct strings it saw to AVAIL.licence_info; the runner refuses to "
                                    "forecast, score or publish if any string seen fails this test or is not in "
                                    "AVAIL.licence_info; the owner then decides (an amendment, never a silent edit)"),
                   "key": "none"},
        "cross_check": {"name": "SMARD chart_data", "filter": 254, "series": "Marktpreis: Frankreich"},
        "agreement_rule": ("SMARD serves fixed weekly files, each starting Monday 00:00 Europe/Berlin (= Paris); "
                           "only whole files whose last day is on or before 2025-12-28 are requested (the file "
                           "starting 2025-12-29 holds 2026 prices and is never requested). Compared: every UTC hour "
                           "of the Paris days 2022-01-01..2025-12-28, SMARD hours built from 2025-10-01 by the "
                           "target's quarter-hour rule under the same PRICE_STAMP; an hour missing or NaN in either "
                           "source counts as a disagreement. Pass: |Energy-Charts - SMARD| <= 0.01 EUR/MWh on "
                           ">= 99.9% of those hours. Every disagreement is listed and 2024-06-26 is always printed; "
                           "2025-12-29..31 are reported 'not cross-checked'. If the rule fails, or either source "
                           "cannot be reached (an HTTP or network failure, not a zone refusal), the run stops and "
                           "the owner decides; the source is never switched silently"),
        "attribution": ATTRIBUTION,
    },
    # ----------------------------------------------------- time and knowledge
    "decision": {"time": "12:00 Europe/Paris on D-1", "note": "the engine's gate and C1's; the builder refuses "
                 "any later decision time"},
    "publication_rule": {
        "pub_latest": "any hour of delivery day X: X 00:00 Europe/Paris (a day-ahead price is published before "
                      "its delivery day starts)",
        "pub_earliest": "any hour of delivery day X: 12:00 Europe/Paris on X-1 (gate closure of X's auction)",
        "known_at_decision": "a price cell is known at decision time d iff pub_latest <= d",
        "cutoff": "so at d = 12:00 D-1 all of D-1 is known and nothing of D: the context ends with the last hour "
                  "of D-1 (cutoff = first target hour - 1 h); no context value comes from any part of D",
        "covariates": "every covariate cell's issue time is checked against d, never against the cutoff",
        "legacy_equivalence": "for load and solar (published at their timestamps) this is identical to the "
                              "existing rule 'nothing after the origin'",
        "approved": "owner, 2026-09-29 (Experiment 4 plan approval)",
    },
    # ------------------------------------------------------------------ model
    "t0": {"repo_id": "theforecastingcompany/t0-alpha", "revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b",
           "context_hours": 2160, "min_context_valid": 0.98, "fixed_horizon_hours": 25,
           "quantiles": [0.1, 0.25, 0.5, 0.75, 0.9], "point": "the median (0.5 quantile)",
           "context": "univariate: the French price only",
           "once": "every arm is forecast once per day; every probe and secondary reads those same forecasts",
           "missing": ("a t0 arm (t0, t0_cal, t0_cal_wx, t0_cal_strict) has no forecast for day D (NaN at every hour, "
                       "median and all five quantiles), counted per arm by cause, if (a) fewer than min_context_valid "
                       "of the 2160 French price values of that arm's own context are finite ('context'; never a "
                       "reason to stop the run), or (b) t0 replaced non-finite output ('sanitised'): "
                       "solarbench.forecasters._NonFiniteWatcher is attached to every predict call of every t0 arm, "
                       "the rows of a flagged batch are re-run one at a time, and a window whose single-row run is "
                       "also flagged is NaN (as T0Forecaster._predict_covariates); the re-run only detects, the batch "
                       "forecast is scored for every window not flagged; a replaced value is never scored")},
    # ---------------------------------------------------------------- periods
    "periods": {
        "fetch_prices": ["2019-12-01", "2025-12-31"],
        "fetch_prices_overlap_check": {"days": ["2015-01-01", "2016-12-31"],
                                       "use": "target.stamp_rule only; never scored, never used by any arm or gate"},
        "fetch_weather": ["2024-02-06", "2025-12-31"],
        "selection": ["2023-01-01", "2023-12-31"],
        "test": ["2024-01-01", "2025-12-31"],
        "test_years": ["2024", "2025"],
        "p4_days": ["2024-06-06", "2025-12-31"],
        "p4_first_day_rule": "AVAIL.p4_first_day: the first day on which the weather day_rule can hold; the avail "
                             "run may move P4's first day later, never earlier",
        "k3_gate": ["2023-10-02", "2023-12-03"],
        "lear_run": ["2023-11-27", "2025-12-31"],
        "price_first_day_max": "2019-12-02 (the first day of the 1456-day window of lear_run's first day): the "
                               "runner stops before any forecast if AVAIL.price_first_day is later",
        "forward": "nothing on or after 2026-01-01 00:00 Europe/Paris is ever requested or cached (engine.zones)",
    },
    # ------------------------------------------------------------------- arms
    "simple_candidates": ["naive_std", "prev_day", "prev_week", "mean_7d", "median_7d", "ewma", "blend_50",
                          "weekday_mean_4w"],
    "simple_selection": ("best_simple_2023: the eight candidates are run together on the 2023 price windows (the "
                         "Paris delivery days of periods.selection, built exactly as the test windows: decision "
                         "12:00 D-1, origin = cutoff). The selection day set is the days whose target is complete "
                         "and on which all eight candidates are finite at every scored hour (a day any candidate "
                         "misses is dropped for all eight, counted and listed). The candidate with the lowest pooled "
                         "MAE (sum |err| over every scored hour / number of hours) is chosen; exact ties are broken "
                         "by list order. The MAE table, the day count and the drops are recorded in run_meta. "
                         "Chosen once, never reselected"),
    "naive_std": ("Lago et al. standard naive on local wall-clock hours: the price at the same local hour of D-7 for "
                  "a Monday, Saturday or Sunday delivery day, of D-1 otherwise; a local hour missing on the lag day "
                  "(spring) takes the preceding local hour; a local hour repeated on D (autumn) takes the lag day's "
                  "single value for both; a local hour repeated on the lag day takes the mean of its two values"),
    "other_simple_rules": "the existing solarbench.forecasters rules (UTC lags), reused unchanged; with the price "
                          "window's origin at the cutoff they may read D-1",
    "lear": {
        "name": "lear_ens",
        "implementation": "clean-room (numpy + scikit-learn); no epftoolbox code; behaviour as "
                          "jeslago/epftoolbox@47d6e0629f65ebd19d3c12cb5689dbad0c2ea078 models/_lear.py",
        "per_hour_model": "one LASSO per local hour of the day (24 models) per window",
        "features_exp4": "French prices of D-1, D-2, D-3 and D-7 (24 local hours each, after the dst rule), then a "
                         "holiday dummy of D equal to 1 iff D is in solarbench.probes.french_holidays(D.year) (the "
                         "calendar of t0_cal's HolidayCovariate), then 7 weekday dummies of D",
        "features_k1": "the published configuration: prices of D-1, D-2, D-3, D-7; each EPF-FR exogenous series at "
                       "D-1, D-7 and D; 7 weekday dummies; no holiday dummy",
        "window_rule": ("the window of N for delivery day D is the N Paris calendar days D-N..D-1 (K1: the last "
                        "N x 24 rows of FR.csv before D, as epftoolbox). Its first 7 days only supply lags, so its "
                        "training rows are its last N-7 days (49, 77, 1085, 1449). A training row is dropped if its "
                        "target or any of its lags is non-finite (a lag before the first fetched day counts as "
                        "missing); the window is never extended or shifted; drops are counted"),
        "calibration_windows_days": [56, 84, 1092, 1456],
        "recalibration": "daily: each delivery day D is forecast by the 24 per-hour models of each window, fitted "
                         "on that window's training rows only; nothing of D enters any fit",
        "transform": ("per column, z = asinh((x - m) / s), m = the median and s = median|x - m| / 0.6744897501960817 "
                      "over the window's kept training rows; applied to every price column of X (K1: also every "
                      "exogenous column) and to each of the 24 columns of y; D's row is transformed with the same "
                      "m and s, and each hour's forecast is inverted as m_y + s_y * sinh(z_hat). The dummy columns "
                      "are never transformed. If s = 0, s is the column's population standard deviation on the same "
                      "rows, and 1 if that is 0 too; every fallback is counted"),
        "penalty": ("per local hour h, X = the transformed design (dummies raw) and y_h the transformed target: "
                    "(1) alpha_h = LassoLarsIC(criterion='aic', fit_intercept=True, max_iter=2500, "
                    "noise_variance=np.var(y_h, ddof=0)) fitted on X with each column centred on its mean and "
                    "divided by the L2 norm of the centred column (a zero-norm column is divided by 1): scikit-learn "
                    "< 1.2's LassoLarsIC with its default normalize=True, whose criterion n*MSE/var(y) + 2*df has "
                    "the same argmin; (2) the hour-h model is Lasso(alpha=alpha_h, fit_intercept=True, "
                    "max_iter=2500, tol=1e-4, selection='cyclic') fitted on X itself, NOT normalised (Lasso's "
                    "normalize=False default), as epftoolbox's recalibrate() does; convergence warnings are ignored; "
                    "(3) the forecast is this Lasso's prediction on D's row. The LARS solution is never the forecast"),
        "dst": "on a 23-hour day the missing local 02:00 is the mean of 01:00 and 03:00; on a 25-hour day the "
               "two 02:00 hours are averaged; forecasts are mapped back to the real UTC hours (a repeated local "
               "hour gets the same forecast twice)",
        "missing": ("a window cannot forecast D if any feature of D is non-finite or its fit fails; lear_ens is the "
                    "hour-by-hour mean of the four windows and is NaN for D if any window cannot forecast D (never "
                    "a mean of fewer); every such day is counted by cause"),
        "scored_only_if": ("K1 passed on the LEAR code that scores lear_ens. The freeze commit is the commit at which "
                           "the scored run (every arm's test forecasts) is made. K1 counts as passed only if one of its "
                           "logged attempts passed with a solarbench/lear.py byte-identical to the freeze commit's, "
                           "both sha256 recorded in run_meta; an edit of solarbench/lear.py after a passing attempt "
                           "needs a new attempt within gates.K1.attempts, otherwise K1 counts as failed"),
    },
    "empirical_bands": {
        "name": "best_simple_eq", "base": "best_simple_2023",
        "rule": ("for each target hour t of D: q_tau(t) = f_D(t) + Q_tau(E_t) at the five t0 levels, f_D the base's "
                 "scored forecast, Q_tau numpy.quantile's default (linear). E_t holds the base's past errors y - f "
                 "at the same UTC hour: candidate cells s = t - j x 24 h, j = 1..35. f(s) is the base's forecast "
                 "from the price window of s's own Paris delivery day X (decision 12:00 X-1, origin = X's cutoff), "
                 "exactly as it would be scored on X. Each cell is legal on its own iff it lies in a Paris delivery "
                 "day <= D-1 and its error is finite; E_t is the 28 most recent legal cells; with fewer than 14, "
                 "q(t) is NaN. Nothing is clipped"),
        "as": "Experiment 3 P1's EmpiricalQuantiles cell logic (probes.EQ_WINDOW_DAYS 28, EQ_MIN_N 14, "
              "EQ_LOOKBACK_DAYS 35), except no clipping and past forecasts made at each day's cutoff"},
    "weather_p4": {
        "covariates": ["holiday", "wx_temperature", "wx_radiation"],
        "constructions": ("the two national hourly series exactly as engine.arms._national_weather builds them from "
                          "the frozen engine/covs.py constants, none changed: ecmwf_ifs025, previous_day3 (lead 3), "
                          "the 12 points of solarbench.covariates.REGION_POINTS, covs.CONSUMPTION_WEIGHTS for "
                          "temperature_2m (from covs.TEMPERATURE_FIRST) and solarbench.covariates.REGION_WEIGHTS for "
                          "shortwave_radiation (from 2024-03-08). The port onto the price grid never calls "
                          "covs.build_covariate or covs.weather_provider and never reads cov.STAMP_OFFSET_MIN (an "
                          "eCO2mix half-hour constant): radiation values, latest = "
                          "solarbench.covariates.hourly_to_slots(radiation, price_index, 30); temperature values, "
                          "latest = engine.covs.instant_to_slots(temperature, price_index, 30); each wrapped as a "
                          "SeriesCovariate with issued = solarbench.covariates.issue_bound(latest, 3)"),
        "hourly_conventions": ("for the price hour [h, h + 1 h) stamped h: radiation is the single reading stamped "
                               "h + 1 h (Open-Meteo's mean over [h, h + 1 h)); temperature is the interpolation at "
                               "h + 30 min, the mean of the readings stamped h and h + 1 h; the latest reading used "
                               "is h + 1 h for both; a missing contributing reading makes the cell NaN. Parity: "
                               "readings 0, 10, 20 at 00:00, 01:00, 02:00 UTC give radiation 10 and temperature 5 "
                               "for the hour stamped 00:00, radiation 20 and temperature 15 for 01:00"),
        "day_rule": ("a P4 day is scored only if (a) for every covariate all 25 fixed-horizon hourly cells given to "
                     "t0 are present (t0 reads a NaN covariate as 0), and (b) each weather covariate's 2160 context "
                     "cells are >= 98% valid, judged on the worst covariate (an hourly port of "
                     "solarbench.covariates.window_coverage); the price context is governed by t0.min_context_valid. "
                     "Weather is read only through the unchanged engine.data.fetch_weather_previous_runs, which "
                     "rounds inward at the seal, so 2025-12-30 and 2025-12-31 are expected to fail (a) and be "
                     "counted; no other fetch may recover them"),
    },
    "strict_arm": {
        "name": "t0_cal_strict", "role": "report-only robustness check of the publication rule; never changes a "
                                         "primary's state",
        "rule": ("t0_cal (French price + holiday) with origin = d: the context ends at the price stamp equal to "
                 "12:00 Europe/Paris on D-1 (the literal old rule 'nothing after the origin'; it reads D-1 up to and "
                 "including the 12:00-13:00 local hour, never 13:00-23:00); fixed 36-hour horizon; D's hours scored"),
        "comparators": {"best_simple_2023": "the P1 comparator unchanged (reads all of D-1): only t0 loses the "
                                            "allowance",
                        "best_simple_2023_strict": ("the same selected rule, not reselected, on windows with origin "
                                                    "= d (existing rules unchanged: their lag steps back past the "
                                                    "origin; naive_std takes D-2's same local hour for any D-1 "
                                                    "source stamped after the origin): both arms lose the "
                                                    "allowance")},
        "days": "the test days on which t0_cal_strict and the comparator in question both scored (counted)",
        "leak_check": ("under the literal old rule (every price stamped after the 12:00 D-1 stamp, affine and NaN) "
                       "t0_cal_strict and best_simple_2023_strict are byte-identical; an edit of D-1 13:00-23:00 "
                       "local must NOT move t0_cal_strict; an edit of the 12:00 D-1 stamp must move it"),
    },
    # ---------------------------------------------------------------- statistics
    "statistics": {
        "day_sets": ("every comparison (each primary, its per-year parts, each secondary and slice) is scored on its "
                     "own paired day set: the delivery days its period and days rule allow, whose target is complete "
                     "and on which both of its two arms are finite at every scored hour (P3: all five quantiles of "
                     "both). A day enters or leaves a day set whole: it is never kept with only some of its hours "
                     "because an arm or the target missed some. Arms outside a comparison never remove its days: "
                     "run_backtest's all-methods drop is applied only inside simple_selection. Day sets decide "
                     "scoring only and never change an arm's inputs. Each arm's missing days are reported by cause. "
                     "The hour slices of report_only.slices score only their own hours of the days in the "
                     "comparison's day set: 'negative-price hours' = the hours with y < 0; 'top 1% absolute prices' = "
                     "the hours whose |y| is at or above numpy.quantile(|y|, 0.99) (default linear method) over every "
                     "scored hour of that comparison's day set; '11:00-16:00 local' = the hours starting 11:00 to "
                     "15:00 Europe/Paris; an hour slice's per-day table holds only those hours, and a day with none of "
                     "them is left out for both arms. A comparison, per-year part or slice is computed only if both "
                     "of its arms were scored and its day set is non-empty; otherwise it computes nothing, calls no "
                     "metrics function and stops nothing, and every numeric field is printed 'not run' (an arm was "
                     "not scored: lear_ens after K1 failed, t0_cal_wx after K3 failed) or 'no days' (an empty day "
                     "set, year or slice); a year printed 'no days' fails statistics.per_year_rule. For every "
                     "comparison that is computed, the per-day table is checked before any bootstrap "
                     "(metrics._day_pivot: same days, equal hour counts, no NaN); a failed check, or a non-finite "
                     "skill or draw, stops the run with nothing reported"),
        "metric_point": "MAE in EUR/MWh pooled over every scored hour of the comparison's day set; skill = "
                        "1 - sum|err_arm| / sum|err_ref| over that set",
        "metric_bands": "mean pinball loss over the five t0 levels pooled over every scored hour of the day set; "
                        "pinball skill = 1 - sum pinball_arm / sum pinball_ref",
        "bootstrap": ("metrics.bootstrap_skill(per_day_common, model=arm, reference=comparator, block_days=14, "
                      "samples=2000, seed=0, return_draws=True) on the per-day table restricted to the day set, in "
                      "date order (a dropped day is skipped, not left as a gap); 14-day blocks as the vault test "
                      "and power_table (engine.claims.BLOCK_DAYS); for P3 on the per-day pinball sums; never "
                      "through run_probes.compare (7-day default). The same draws give the 95% interval and p. The "
                      "block-length table (metrics.bootstrap_sensitivity, 1, 3, 7, 14, 30) is report-only"),
        "p_value": "one-sided p = (1 + #draws <= m) / 2001, m = 0 for superiority, m = -0.05 for P2",
        "family": ["P1", "P2", "P3", "P4"],
        "multiplicity": "Holm over the four primaries at alpha 0.05; a not-runnable primary enters with p = 1",
        "per_year_rule": ("each primary's per-year check uses its own metric and threshold (MAE skill for P1, P2, "
                          "P4; pinball skill for P3, never the MAE of its medians): the pooled-sum skill over its day "
                          "set restricted to the Paris delivery days of year Y (P4's 2024 part: from AVAIL "
                          "p4_first_day). It passes only strictly above the threshold (> 0; P2 > -0.05). No per-year "
                          "bootstrap or p. A year with no day in the set fails"),
        "verdict_states": ("each primary gets exactly one state, the first that applies: 'not runnable' (P2: K1 "
                           "failed or P2 coverage < 0.95; P4: K3 failed or no P4 day scored; P1 and P3 never); "
                           "'lost' (its pooled skill does not pass its threshold, or Holm p >= 0.05); 'not stable' "
                           "(pooled passes but a year's skill does not); for P3 only 'lost on coverage' (pooled and "
                           "both years pass on pinball, but coverage is outside [0.70, 0.90]); otherwise 'won'. Only "
                           "'won' is a win. Pooled skill, 95% interval, raw p, Holm p, both yearly skills (and P3's "
                           "coverage) are printed for every primary whatever its state; a field statistics.day_sets "
                           "leaves uncomputed is printed 'not run' or 'no days'; a not-runnable primary enters Holm "
                           "with p = 1 and its Holm p is printed"),
        "p2_coverage": "lear_ens finite at every hour on >= 95% of the test days whose target is complete",
        "alpha": 0.05,
    },
    # ------------------------------------------------------------------ probes
    "probes": [
        {"id": "P1",
         "question": "Using only price history and the holiday calendar, does t0 beat the best simple price rule?",
         "t0_arm": "t0_cal", "comparator": "best_simple_2023", "metric": "mae",
         "success": "skill > 0; Holm p < 0.05; skill > 0 in 2024 and in 2025",
         "days": "its day set (statistics.day_sets) within periods.test"},
        {"id": "P2",
         "question": "Is t0 no more than 5% worse than the standard free price model (LEAR) on the same information?",
         "t0_arm": "t0_cal", "comparator": "lear_ens", "metric": "mae",
         "success": "non-inferiority, margin 5%: skill > -0.05; Holm p < 0.05 with m = -0.05; skill > -0.05 in "
                    "2024 and in 2025; not runnable (p = 1) if K1 failed or statistics.p2_coverage fails",
         "days": "its day set (statistics.day_sets) within periods.test"},
        {"id": "P3",
         "question": "Are t0's native price bands better than simple empirical bands, and honest?",
         "t0_arm": "t0_cal (quantiles)", "comparator": "best_simple_eq", "metric": "pinball",
         "success": ("pinball skill > 0; Holm p < 0.05; pinball skill > 0 in 2024 and in 2025; and coverage in "
                     "[0.70, 0.90] (closed, unrounded): the share of the scored hours of P3's pooled day set with "
                     "q10 <= y <= q90, t0_cal's q10 and q90 as output (unclipped, unsorted; both hours of a "
                     "repeated autumn hour count); coverage is pooled only, per-year coverage is printed"),
         "days": "its day set (statistics.day_sets) within periods.test"},
        {"id": "P4",
         "question": "Do public weather forecasts issued before the gate help t0 on prices?",
         "t0_arm": "t0_cal_wx", "comparator": "t0_cal", "metric": "mae",
         "success": "only after K3 passed and with at least one P4 day scored (else not runnable, p = 1); skill > 0; "
                    "Holm p < 0.05; skill > 0 in the 2024 part and in 2025",
         "days": "its day set (statistics.day_sets) within periods.p4_days from AVAIL.p4_first_day, also passing "
                 "weather_p4.day_rule"},
    ],
    # ------------------------------------------------------------------- gates
    "gates": {
        "K1": {"what": "the clean-room LEAR reproduces the published EPF-FR results (code check only; never a claim)",
               "data": "Zenodo record 4624805, FR.csv (sha256 recorded by avail)",
               "reference": "jeslago/epftoolbox@47d6e0629f65ebd19d3c12cb5689dbad0c2ea078 "
                            "forecasts/Forecasts_FR_DNN_LEAR_ensembles.csv, sha256 "
                            "671d65842180fd7fc0f603eca6281f4ddc581983cbfb4991e97e291d5d88ab08",
               "test_period": ["2015-01-04", "2016-12-31"],
               "published_mae": {"LEAR 56": 4.6806, "LEAR 84": 4.5754, "LEAR 1092": 4.2499, "LEAR 1456": 4.3781,
                                 "LEAR Ensemble": 3.9798},
               "tolerance": ("the reference MAEs are recomputed at run time from the pinned CSV over its 17,472 "
                             "hours (2015-01-04 00:00 .. 2016-12-31 23:00) and must equal published_mae to 4 "
                             "decimals, else K1 stops and the owner decides; the clean-room must forecast every one "
                             "of those hours with the published configuration (each of the four windows and the "
                             "ensemble finite at every hour), else the attempt fails (it counts as one attempt, and "
                             "no MAE or difference is ever computed on a subset of those hours); deviation = "
                             "clean-room MAE / reference MAE - 1, each MAE over all 17,472 hours; K1 passes only if "
                             "every hour was forecast, the ensemble deviation is in [-2%, +1%], each window's in "
                             "[-3%, +2%], and the mean absolute difference from the published 'LEAR Ensemble' "
                             "forecasts over the same 17,472 hours is <= 0.25 EUR/MWh (asymmetric because P2's "
                             "margin is measured against this LEAR)"),
               "attempts": "at most 3, each logged with the sha256 of the solarbench/lear.py it ran, all before the "
                           "freeze commit (lear.scored_only_if) and none after it"},
        "K2": {"what": ("t0 adapter parity at each TEST_ORIGINS day, in one process, for t0, t0_cal, t0_cal_strict "
                        "and (at origins on or after AVAIL.p4_first_day) t0_cal_wx: a reference built independently "
                        "of the adapter (the 2160 hourly prices ending at the arm's context end as float32, the "
                        "arm's covariate block, one model.predict call on that single row with the arm's fixed "
                        "horizon and the five levels, D's hours selected by UTC time). (a) The arm's predict() on "
                        "that window alone equals the reference bit for bit, median and all five quantiles. (b) Its "
                        "predict() on all those windows in one batch is within 0.01 EUR/MWh of the reference on "
                        "every scored hour and quantile (batch composition moves t0 slightly)"),
               "on_fail": "the run stops before any arm is scored; the adapter may be fixed and K2 rerun, every "
                          "attempt logged in run_meta"},
        "K3": {"what": "the hourly weather port carries a signal t0 can use (engine ka/2 thresholds)",
               "period": ["2023-10-02", "2023-12-03"],
               "windows": "the t0_cal windows of the K3 days (publication rule, 2160-h context, 25-h horizon, D's "
                          "real hours scored)",
               "runs": "one per convention: 'instant' (the wx_temperature port) and 'mean_preceding_hour' (the "
                       "wx_radiation port)",
               "arms": "base t0_cal; four oracle arms, each t0_cal plus exactly one extra covariate through the "
                       "convention's port as P4 ports real weather: planted, decoy, planted shifted -1 h, planted "
                       "shifted +1 h (readings shifted before the port); no real weather (none before 2024-02-06); "
                       "oracle arms run under the backtest's two-key exemption and are never findings",
               "planted": ("readings on the hourly UTC grid from the first context hour of the first K3 window to "
                           "2 h after the last horizon hour of the last; p(h) = the price of the hour starting h. "
                           "mean_preceding_hour: the reading stamped h + 1 h is p(h) + e(h + 1 h). instant: the "
                           "reading stamped h is (p(h - 1 h) + p(h)) / 2 + e(h). So each port returns a signal "
                           "centred on the hour it fills. e ~ N(0, (0.05 x p99)^2), p99 = metrics.peak_proxy(prices, 0.99) "
                           "(numpy.quantile, default linear method, float64) of the French hourly prices over the "
                           "scored hours of the K3 days (NaN dropped); a missing p makes the reading missing"),
               "decoy": "N(0, sd^2) readings on the same grid, sd = the sample standard deviation (ddof 1, as pandas "
                        "Series.std in engine.referee.known_answer) of the same prices p99 is taken over; the decoy "
                        "readings are not shifted",
               "rng": "numpy default_rng(0), fresh for each convention; e drawn first, then the decoy, one value "
                      "per hourly stamp",
               "ratios": "MAE pooled over every scored hour of the K3 days all five arms of the convention scored: "
                         "planted_ratio = MAE(planted)/MAE(t0_cal); decoy_ratio = MAE(decoy)/MAE(t0_cal); "
                         "shift_penalty = min(MAE(shift -1 h), MAE(shift +1 h))/MAE(planted)",
               "rules": {"planted_ratio_max": 0.95, "decoy_ratio_min": 0.98, "decoy_ratio_max": 1.10,
                         "shift_penalty_min": 1.01, "noise_sd_share_of_p99": 0.05, "seed": 0,
                         "no_sanitised_output": True},
               "pass": "K3 passes only if both conventions meet every rule and t0 replaced no non-finite output in "
                       "any K3 arm; otherwise P4 is not runnable (p = 1); P4 is never run with a subset of its "
                       "covariates",
               "on_fail": "any fix is an owner-approved amendment, reported as amended"},
    },
    # -------------------------------------------------------------- leak rules
    "leak_controls": [
        "independent re-derivation of the publication rule in the tests (pub_latest, pub_earliest, cutoff = first "
        "target - 1 h, 23/24/25 targets) for every window 2023-2025 and the TEST_ORIGINS days",
        "target poisoning (affine and NaN) of every price cell whose pub_latest is after d must leave every arm's "
        "forecast byte-identical (np.array_equal, equal_nan=True)",
        "legal-change controls: editing D-1 13:00-23:00 local or a D-2 hour must move t0_cal, t0, t0_cal_wx and "
        "lear_ens; editing D-1 must move best_simple_eq's error quantiles",
        "a covariate cell issued at 18:00 D-1 is refused (issue times checked against d)",
        "weather cells issued after d are poisoned without effect on t0_cal_wx; a +50 shift of cells issued before "
        "d moves it",
        "variate whitelist: target = French price; covariates = holiday, wx_temperature, wx_radiation (plus K3's "
        "oracle series under the two-key exemption); no realised series",
        "the strict arm's own old-rule poisoning and its two controls (strict_arm.leak_check)",
        "in-run real-model leak check before any scoring, at each TEST_ORIGINS date taken as the delivery day D "
        "(decision 12:00 D-1; fixed dates, used whether or not D is later scored). Each control is named by its "
        "content and runs on the arms its own text names: target poisoning (affine and NaN) for every arm; the "
        "legal-change controls for the arms and quantiles they name; the covariate issue-time refusal for every arm "
        "with a covariate; the strict arm's old-rule poisoning and its two controls (strict_arm.leak_check) for "
        "t0_cal_strict and best_simple_2023_strict only. lear_ens is checked only if K1 passed; t0_cal_wx only if K3 "
        "passed, then also with the weather poisoning and +50 control, at AVAIL.p4_first_day and at the TEST_ORIGINS "
        "dates on or after it. The last context value must be the price of the hour [D-1 23:00, D 00:00) Paris for "
        "t0, t0_cal, t0_cal_wx and best_simple_2023 (publication_rule.cutoff), and of the hour [D-1 12:00, D-1 "
        "13:00) Paris for t0_cal_strict and best_simple_2023_strict (strict_arm.rule). Any failure aborts the run "
        "with nothing scored",
        "seal: before each Energy-Charts request, engine.zones.assert_readable(first day, last day) of its one-month "
        "chunk, called with Paris-local dates (never unix seconds or UTC instants, which it would read as 1970 or as "
        "UTC dates); the request's unix bounds are then derived from those days as in sources.scored.params; before "
        "each SMARD data file is requested, assert_readable(its own first day, its own last day); returned stamps "
        "checked before caching; a separate price cache; no cached stamp at or after 2026-01-01 00:00 Paris",
        "no clipping anywhere; parity of the price backtest with run_backtest on a non-negative series whose "
        "forecasters are finite on every window (the all-methods drop is not part of Experiment 4's scoring)",
        "the seven gate-fingerprinted files and every existing module, test and workflow stay unedited",
    ],
    # --------------------------------------------------------- report only
    "report_only": {
        "secondaries": ["t0 (no calendar) vs best_simple_2023", "t0_cal vs t0",
                        "t0_cal_strict vs best_simple_2023 (t0 alone without the allowance)",
                        "t0_cal_strict vs best_simple_2023_strict (the old rule for both)",
                        "t0_cal vs t0_cal_strict (value of the D-1 afternoon to t0)",
                        "lear_ens vs best_simple_2023", "t0_cal vs lear_ens (superiority)",
                        "lear_ens + empirical bands vs t0_cal bands", "rMAE vs naive_std and vs prev_week", "RMSE"],
        "slices": ["each year", "each quarter (2025 Q4 is quarter-hour derived)", "April-September",
                   "negative-price hours", "top 1% absolute prices", "11:00-16:00 local", "weekends and holidays",
                   "the weeks after each DST switch"],
        "tables": ["concentration (share of the gain from the best days)", "bootstrap sensitivity (block length)"],
    },
    # --------------------------------------------------------- reading table
    "reading_table": {
        "printing": ("summary.md opens with the status line (discovery-grade, nothing confirmed), then prints "
                     "verbatim exactly one P1/P2 row, one P3 row and one P4 row matching the states, then the "
                     "'not stable' row for each primary with that state, and the strict row; each probe's pooled "
                     "skill, 95% interval, raw p, Holm p and yearly skills are printed beside its row"),
        "P1 won, P2 won": "On public price data alone, t0 beats the best simple rule and is no more than 5% worse "
                          "than the standard free price model (LEAR) on the same information (discovery-grade).",
        "P1 won, P2 lost or not stable": "t0 beats the best simple rule, but it is not shown to be within 5% of LEAR "
                                         "on the same information; it may be more than 5% worse (the report-only "
                                         "t0_cal vs lear_ens is printed).",
        "P1 won, P2 not runnable": "t0 beats the best simple rule; the comparison with LEAR was not made (K1 failed "
                                   "or LEAR forecast too few days), so nothing is concluded about LEAR.",
        "P1 not won, P2 won": "t0 is no more than 5% worse than LEAR but is not shown to beat the best simple rule; "
                              "the report-only lear_ens vs best_simple_2023 shows whether the simple rule was hard "
                              "to beat in 2024-2025.",
        "P1 not won, P2 not won": "This study does not show that t0 is useful on French prices from price history "
                                  "alone. If P2 is not runnable, add: 'the comparison with LEAR was not made.' If "
                                  "t0_cal's pooled 95% interval against best_simple_2023 lies entirely below 0, add: "
                                  "'the best simple rule was more accurate (interval not adjusted for "
                                  "multiplicity).'",
        "P3 won": "t0's native bands score better than simple empirical bands, and its 10-90 band covers 70-90% of "
                  "scored hours.",
        "P3 lost on coverage": "t0's native bands score better than simple empirical bands but are mis-calibrated: "
                               "their 10-90 coverage (printed) is outside 70-90%, so as they stand they are not "
                               "trustworthy for risk.",
        "P3 lost or not stable": "t0's native bands are not shown to beat simple empirical bands.",
        "P4 won": "Public weather forecasts issued before the gate add value to t0 on prices (P4 days only).",
        "P4 lost or not stable": "This study does not show value in these public weather forecasts for t0 on prices.",
        "P4 not runnable": "P4 was not tested: the weather pipeline failed its planted-signal gate (K3), or no P4 day "
                           "could be scored (the cause is printed). Nothing is concluded about weather.",
        "not stable": "<probe>: the pooled result passes but does not hold in each year; printed 'not stable' and "
                      "read as not won.",
        "strict": ("Report-only, on point MAE skill (statistics.metric_point) pooled and in 2024 and in 2025 alone, "
                   "each comparison on its own strict_arm.days; 'beats' means that skill is > 0 pooled, in 2024 and "
                   "in 2025 (no interval, no p). The pooled, 2024 and 2025 skills of t0_cal_strict vs "
                   "best_simple_2023 and vs best_simple_2023_strict are printed beside the row whatever its sentence. "
                   "If P1 is 'won': if t0_cal_strict beats best_simple_2023: 'P1 does not rest on t0 reading the D-1 "
                   "afternoon prices.' Otherwise, if t0_cal_strict beats best_simple_2023_strict: 'Under the old rule "
                   "for every arm t0 still beats the same simple rule; its edge over the rule that keeps the "
                   "allowance needs the D-1 afternoon.' Otherwise: 'P1's win depends on the D-1 afternoon allowance.' "
                   "If P1 is not 'won': 'P1 was not won, so the strict check is not read; its skills are printed for "
                   "information only.'"),
    },
    # ---------------------------------------------------- toward confirmation
    "carry_forward": {
        "rule": ("a primary is a vault candidate only if its state is 'won' and some delta in {0, 0.05, 0.10, 0.20} "
                 "satisfies S - delta >= M. A = the per-day table (sum_abs_err, n; P3: pinball sums) of its t0 arm "
                 "and comparator on its own day set, restricted to Paris delivery dates in April-September of 2024 "
                 "or 2025. S = its skill on A. M = engine.referee.stats.power_table(A, t0_arm, comparator, "
                 "alpha=0.0125)['min_detectable_skill']['12']. delta is the largest value satisfying the inequality; "
                 "if none does, it is not a candidate. S, M, A's day count, block_sd and ref_mae are printed, and M "
                 "at alpha 0.0125/2, /3 and /4 for information only"),
        "expressible_today": "P1 (vs best_simple) and P4 (vs accepted, once P1's arm is accepted); P2 and P3 need "
                             "vault extensions",
        "route": "decided by the owner after the results (default: an engine price lane after B1 opens)",
    },
}

#: Filled once by ``run_prices.py avail`` (coverage and semantics only, no forecasts) and committed before the
#: first forecast. Not hashed; the runner refuses to run while any value is None.
AVAIL: dict = {
    # From the avail run 36610144690 (2026-09-29; coverage and semantics only, no forecast, no error metric):
    # the stamp convention decided by content against EPF-FR (start: 17,443 hours, share 1.000; end: 0.007);
    # 2,223 of 2,223 days 2019-12-01..2025-12-31 complete; DST days 23/25 hours; Q4 2025 91 days x 96 and 1 x 100
    # quarter-hours; Energy-Charts = SMARD on all 34,992 hours 2022-01-01..2025-12-28 (max diff 0.00); FR.csv
    # equals the published 'Real price' on all 17,472 K1 hours and the published MAEs recompute exactly;
    # 572 P4 days from 2024-06-06 (2025-12-30 and 2025-12-31 fail the horizon rule, as the spec expects).
    "price_stamp": "start",
    "price_first_day": "2019-12-01",
    "p4_first_day": "2024-06-06",
    "epf_fr_sha256": "ee8b07cbf9204de8a222954936695fb36fb5d344a7ab4a4a9e27d4107d633a5d",
    "licence_info": ["CC BY 4.0 (creativecommons.org/licenses/by/4.0) from Bundesnetzagentur | SMARD.de"],
    "avail_run": "36610144690",
}

#: Pinned when the spec was frozen; tests/test_price_spec.py checks it.
PRICE_SPEC_SHA256 = "225774c89e301166c2d4850e2f894335fd5ae703dc410bc4a06aa246ac5755bc"


def spec_sha256() -> str:
    return sha256_of({"spec": PRICE_SPEC, "test_origins": TEST_ORIGINS, "attribution": ATTRIBUTION})


def require_frozen() -> None:
    """The runner's guard: the spec is unchanged and every AVAIL fact is filled."""
    if PRICE_SPEC_SHA256 is None or spec_sha256() != PRICE_SPEC_SHA256:
        raise RuntimeError("PRICE_SPEC differs from the frozen PRICE_SPEC_SHA256")
    missing = [k for k, v in AVAIL.items() if v is None]
    if missing:
        raise RuntimeError(f"AVAIL not filled: {missing} (run 'run_prices.py avail' and commit its facts)")
