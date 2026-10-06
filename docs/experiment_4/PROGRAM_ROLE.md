# Experiment 4's place in the programme

*Owner's directive, 29 September 2026. This note frames Experiment 4; it is not part of it. The binding
experiment is `PRICE_SPEC` in `solarbench/price_spec.py` (hash pinned at `aa28301`, data facts filled at
`f9f0a2f`) and its restatement `ONE_PAGER.md`. Neither is changed by this note, and nothing here alters how
any result of Experiment 4 is computed or read.*

## Experiment 4 stays exactly as frozen
- Its four questions, comparators, statistics and reading table were fixed before any price was fetched. They
  are applied as written.
- Each question's result is read only by its own frozen rule. No question is re-weighted, re-tested or
  re-interpreted after the data are seen.

## Question 4 is the first price test of the core idea
The project's core product idea is that extra public information, supplied to t0 as inputs ("covariates"),
makes its forecasts better than t0 on its own. On French electricity demand this has been tested with
temperature (claim B1, sealed until 2027). On prices, question 4 is the first test.

- **The comparison:** t0 with the holiday calendar and public weather forecasts, against t0 with the holiday
  calendar only, on the same days.
- **The weather forecasts:** temperature and sunshine, archived and issued well before the noon decision.

It is read by its frozen rules and nothing else:
- **Plumbing check first:** it runs only if the planted-signal check of the weather plumbing (K3) passes and
  at least one weather day can be scored.
- **Statistical test:** it must pass one test over its days, allowing for four questions being asked at once.
- **Each year:** it must also point the same way in the 2024 part and in 2025 alone.

Each possible outcome has its frozen reading:
- **won:** public weather forecasts add value to t0 on prices;
- **lost or not stable:** no value is shown;
- **not run:** nothing is concluded about weather.

## Experiment 4 is discovery-grade
- **Why:** the 2024–2025 French prices are public and already studied, and 2025 was already used once for
  claim C1. Whatever Experiment 4 finds is exploratory.
- **What it cannot do:** it cannot by itself satisfy the project's milestone of "one bounded, reproducible,
  independently confirmed predictive finding using t0, followed by an investigation that builds on it".
- **What could satisfy it:** only a claim frozen in advance and then confirmed on data that did not exist when
  it was frozen. That means the engine's sealed forward vault, opened once with the owner's approval.
- **How Experiment 4 would feed that:** a winning question can at most become a candidate, under its frozen
  carry-forward rule. The route into the vault is the owner's decision.

## What happens after Experiment 4 is scored
- **The follow-up is not chosen by hand.** No next covariate experiment is prescribed. The AI researcher
  receives the Experiment 4 evidence and chooses one bounded follow-up investigation based on what was learned.
  The evidence covers every question's state, skill, error range, the pre-declared slices and the plumbing and
  reproduction checks.
- **It is a separate stage** with its own specification and code (Experiment 5 or later). Experiment 4's code,
  specification and results are read-only inputs to it, so the frozen experiment stays scientifically intact.
- **"Bounded" means limits:**
  - a few probes at most, within an evaluation budget;
  - on the exploratory years only (2025 and earlier), never on sealed future data;
  - using only inputs the referee can run without leakage;
  - if the researcher wants a public input that is not yet available, it may request it, and the referee first
    checks that its publication time can be proven and that its licence allows use.
- **Before anything runs:** the referee checks the researcher's proposal, the protocol is frozen, and the owner
  approves it.
- **Its results are exploratory too.** Independent confirmation still goes only through the forward vault.
