# Experiment 4 replication: tolerances, fixed before any comparison

This file is committed before any replicated value is compared with a published one; the commit order is the
evidence. The published values are `docs/experiment_4/scored_run/results.json`, the run's output. They are
compared with three things:
- **Track 1:** a blind, independent re-implementation, `blind_replicate.py`;
- **Track 2:** a re-execution of the frozen code at `2b407f4`, `reexecute_frozen.py`. This is not independent;
- **Track 3:** a Monte-Carlo assessment, `mc_tolerance.py`. This is report-only.

Every input comes from the authenticated copy of the run's original artifact (see `provenance.json`).

## Track 1: an independent implementation

**Deterministic quantities.** These must agree within a relative difference of 1e-9, or an absolute difference of
1e-12 when the published value is 0:
- pooled skills;
- per-year skills;
- day and hour counts, pooled losses, and days won and lost;
- P3 coverage, pooled and per year;
- P4 concentration (the top-5, 10 and 20 shares, and the skill without those days);
- carry-forward S, A's day count, block_sd and ref_mae.

**Bootstrap quantities.** These are the 95% interval endpoints and the one-sided p. Seed 0 of an independent
implementation may draw different blocks from the run's. So a published value agrees if it lies **inside the 0.5–99.5%
range** of the same statistic across seeds 0–199 of the independent bootstrap. For p, the comparison uses the draw
count k = p·2001 − 1.
- If the independent implementation happens to match bit for bit, that is reported as such.

**Holm-adjusted p and states.** Holm must be equal when recomputed from the published raw p. The states must follow
the spec's rules.

**M and delta (carry-forward).**
- **M:** the formula comes from the engine code, not from PRICE_SPEC's text. So M must agree to 4 decimals and is
  labelled "conditional on the code's formula". It is given to the replicator as a written statement.
- **delta and candidacy:** must be equal.

## Track 2: the frozen code on the original forecasts

Every recomputed field must equal `results.json` exactly, by canonical JSON. Any difference is reported in full.

## Track 3: the Monte-Carlo spread (report-only)

This track reports, for each interval endpoint and each p:
- the frozen bootstrap rerun with seeds 1–199;
- where the published seed-0 value falls in that spread;
- the share of seeds under which any primary's state would change.

It decides nothing.

## Classification of disagreements

Each disagreement is assigned to exactly one class:

| Class | Meaning |
|---|---|
| a | The replicator made an error |
| b | The spec does not determine the value |
| c | Floating-point or Monte-Carlo noise inside the tolerances above |
| d | A real defect in the run |

**What a class d finding does:**
- It is recorded, never corrected.
- It stops the work before Phase B (the researcher call) until the owner decides.
