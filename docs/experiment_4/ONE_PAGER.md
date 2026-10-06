# Experiment 4: can t0 forecast French electricity prices from public data?

*Written and frozen before any French price was fetched. The binding version is `PRICE_SPEC` in
`solarbench/price_spec.py`; this page restates it in plain words.*

## Why this experiment
On national electricity demand, RTE's own forecast still beats t0. RTE has data and expertise nobody
outside can match. Prices are different: the day-ahead auction price is public, and so is most of what drives
it. t0's makers present prices as a showcase use. So prices are a fair place to ask whether t0 is useful
**without proprietary data**.

What t0's report actually shows on prices is thin:
- **France:** one test of 20 day-ahead forecasts, probably 12–31 December 2016 (the dates are inferred, not
  confirmed).
  - On that task, t0 with extra inputs ranks about 8th of 26 published entries.
  - One model that uses price history alone is within 5% of it.
  - The extra inputs helped t0 by about 5%.
- **Germany:** the 51% gain came from the grid operators' day-ahead load, wind and solar forecasts.
  - The report does not say when these were issued.
  - Wind and solar forecasts are reportedly due only at 18:00 the day before, after the auction closes (not
    verified).
  - If so, a forecaster working at noon could not have used them.

t0 may lose here. Either answer is useful.

## The forecasting task
- **When the forecast is made:** at noon on the day before delivery, the latest moment before the day-ahead
  auction closes.
- **What is forecast:** the French price (EUR/MWh) for each hour of the next day.
- **What the forecast may use:**
  - every price already published, which includes all of today's prices, since they were set yesterday;
  - the holiday calendar;
  - for one question, public weather forecasts made well before noon.
- **What is never used:** anything published after noon, and any data from 2026 on.
- **Test period:** 2024 and 2025 (731 days).
  - The best of 8 simple rules is picked once, on 2023.
  - The result is tested once on the two years together. It must then also point the same way in 2024 alone
    and in 2025 alone. Each single year is not tested separately.
- **What the results can and cannot claim:** they are exploratory. These years are public and already studied,
  so nothing here counts as proven. Proof would come later, on future data, through the engine's sealed vault.

## The four questions (all decided before any data is seen)
| # | Question | t0 is compared with | Counts as a win when |
|---|---|---|---|
| P1 | Does t0 beat simple rules? | The best of 8 simple rules, chosen on 2023 | Over 2024–2025 together, t0's average error is clearly lower. In 2024 alone and in 2025 alone it is also lower (no test for each year). |
| P2 | Is t0 no more than 5% worse than the standard free price model? | LEAR, the model price-forecasting researchers use as a yardstick, given the same information | Over both years together, t0 is clearly no more than 5% worse, and it is also less than 5% worse in each year alone. LEAR only counts if our copy first reproduces its published results and forecasts at least 95% of the test days. Otherwise P2 is "not run" and counts as not won. |
| P3 | Can t0's "likely range" be trusted? | Simple ranges built from past errors | Over both years together, t0's ranges score clearly better, and they also score better in each year alone. Over both years, its 80% range contains 70–90% of the prices. |
| P4 | Do free public weather forecasts help t0? | t0 without weather | On its test days, t0 with weather is clearly better overall. It is also better in the 2024 part alone and in 2025 alone. The test days run from 6 June 2024 to the end of 2025; the start may move later if weather data are missing, never earlier. P4 runs only if a planted-signal test first shows the weather plumbing works and at least one weather day can be scored. |

"Clearly" means the win survives one statistical test on all the test days together. The test allows for
noise from day to day and for the fact that four questions are asked at once. Each year only has to point the
same way; it is not tested on its own.

## How the results will be read (frozen)
- **P1 and P2 won:** on public price data alone, t0 beats the best simple rule and is no more than 5% worse
  than the standard free model.
- **P1 won, P2 lost or not stable:** t0 beats the best simple rule, but it is not shown to be within 5% of the
  standard free model. It may be more than 5% worse.
- **P1 won, P2 not run:** LEAR failed its reproduction check or missed too many days, so t0 was not compared
  with it. Nothing is concluded about LEAR.
- **P1 not won, P2 won:** t0 is within 5% of the standard free model but is not shown to beat the best simple
  rule.
- **P1 and P2 not won:** this study does not show that t0 is useful on French prices from price history alone.
  - This is not proof that t0 is useless.
  - If P2 was not run, it adds that the comparison with LEAR was not made.
  - It says "the simple rule was more accurate" only if the error range is entirely on that side.
- **P3 won:** t0's ranges score better and contain 70–90% of prices. If they score better but contain too few or
  too many prices, they are reported as not trustworthy for risk. Otherwise they are not shown to be better.
- **P4:**
  - **won:** public weather forecasts add value;
  - **lost:** no value is shown;
  - **not run:** the planted-signal test failed, or no weather day could be scored; nothing is said about weather.
- **If a question passes overall but one year does not,** it is reported as "not stable" and counts as not won.

## Safeguards
- **No peeking:** no forecast may use a price published after noon on the day before.
  - Tests rewrite every later price and check that no forecast changes.
  - They also check that changing a legal, earlier price does change it.
- **One exception, checked separately:** the only new allowance is that this afternoon's and evening's prices,
  already set yesterday, may be used.
  - A "strict" version of t0 whose price history ends with today's noon-to-1 pm price (the old rule used for
    demand and solar: nothing stamped after the forecast time) is compared with the simple rule that keeps the
    allowance.
  - It is also compared with the same simple rule held to the same old rule.
  - Tests check that the strict version sees today's prices up to and including the noon-to-1 pm price, and
    nothing later.
  - It is read only if P1 is won; otherwise its numbers are printed for information.
  - How each outcome will be read is fixed in advance, and this check never changes the four answers.
- **Real-model check:** before any scoring, the real model is checked the same way on 11 days:
  - the first, middle and last test days;
  - 8 tricky ones: the four clock changes, 26 June 2024, and 30 September to 2 October 2025 around the switch to
    15-minute prices.
- **Nothing existing changes:** no existing code or experiment is modified.

*Prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE).*
