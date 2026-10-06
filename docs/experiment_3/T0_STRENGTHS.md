# What t0 is built to be good at, and what we have tested

Sources:
- The t0 technical report, [arXiv:2609.24559](https://arxiv.org/abs/2609.24559), `docs/2609.24559.pdf`. Page numbers in brackets.
- The installed `tfc-t0` 0.3.2 code.

We use **t0-alpha**, which has 102M parameters. The report's larger **t0-beta** (256M parameters, 21 quantile levels) scores clearly better on its benchmarks [p.13–16]. It is not tested here.

| t0 is designed to… | What the report shows | Tested by us? |
|---|---|---|
| **Give uncertainty ranges**, not just one number: five levels from 10% to 90%, which cannot cross | Scored on probabilistic benchmarks. Its 10–90% band covers 78% of outcomes, slightly narrow. Levels outside 10–90% are clamped to the edges [p.9, 20–22] | **No.** We only scored the middle forecast → **probe P1** |
| **Use inputs known in advance** (forecasts, calendars) | Helps on 19 of 30 benchmark tasks (+6.3 skill points). Cuts error on German power prices by 51% when given load, solar and wind forecasts. Hurts on 11 of 30 tasks, including a 15-minute electricity series with weather [p.16–18] | **Yes** (covariate slice). A weather forecast cut t0's error by 26%, but a one-line weather ratio still beat t0 by 24%. A planted-signal test showed t0 uses such inputs only weakly |
| **Use inputs seen only in the past** | Helps on 9 of 12 tasks (+2.7 skill points) [p.18] | No, and not in this round |
| **Forecast several related series together** (attention across series) | A core design feature [p.7]. No results are given for regional or hierarchical data | **No** → **probe P3** |
| **Handle harder targets driven by calendar and weather**, such as electricity demand | Victoria demand, with temperature and holidays: t0-alpha MAE 373–380 MW, against 324–349 for the Chronos-2 model [p.29] | **No** → **probe P4** (national consumption with public holidays) |
| **Correct another model's errors** | Not claimed anywhere in the report | **No** → **probe P2** (our idea, not the authors') |
| **Work zero-shot with long histories**, up to 8,192 steps | Trained on 8,192-step windows. Reaches 95% of its accuracy from 1,024 steps [p.9, 25] | Partly: we use 4,320 steps (90 days) |

**Where the report says t0-alpha is ordinary:**
- It ranks 11th of 17 models on the GIFT-Eval benchmark.
- On energy data, it wins no clear majority of comparisons [p.14–15].
- Missing data hurts it more than its peers [p.24].

## The four probes (frozen in `solarbench/probes.py` before any run)

| Probe | Question | t0 arm | Compared with (best simple) | Metric | Counts as a win |
|---|---|---|---|---|---|
| P1 | Are t0's uncertainty bands better than simple bands? | t0 with the weather forecast, 5 native quantiles | `wx_ratio` plus the spread of its own past errors (28 days) | Pinball loss | Better, *and* t0's 10–90% band covers 70–90% of daytime outcomes |
| P2 | Can t0 correct the best simple forecast's errors? | `wx_ratio` + t0's forecast of `wx_ratio`'s own errors | `wx_ratio` | MAE | Better |
| P3 | Is forecasting the 12 regions together better than forecasting the nation? | t0 on 12 regional series at once, summed | `ewma` | MAE | Better |
| P4 | Is t0 better on national electricity consumption? | t0 + public-holiday calendar | The best simple method on 2023, chosen by rule | MAE | Better |

**Rules for all four:**
- Data up to 2024-12-31 only.
- "Better" means the error is lower with statistical confidence: a one-sided block bootstrap, corrected for testing four probes (Holm), at 5%.
- Every comparison is also reported in each probe's own units.
