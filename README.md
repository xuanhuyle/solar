# Day-ahead solar forecasting: `t0-alpha` vs. naive persistence

A minimal, reproducible benchmark answering one question:

> Can [The Forecasting Company's `t0-alpha`](https://huggingface.co/theforecastingcompany/t0-alpha)
> zero-shot foundation model beat trivial persistence at day-ahead forecasting of
> **French national solar generation**, given nothing but the historical
> generation series?

No weather covariates. That is the point of the experiment, not an oversight —
it isolates how much a general-purpose time-series model can extract from the
signal's own history, and it sets the expectation that absolute errors will sit
well above an operational NWP-driven forecast.

```bash
pip install -r requirements.txt
hf auth login          # once — see "Model access" below
python run_benchmark.py
```

That one command downloads the data, runs the backtest, and writes every number
and figure to `results/`. Re-runs read the caches and recompute nothing.

**There are no results checked into this repository.** `results/summary.md` is
written by the run, on your machine, from real RTE data and the real model.
Synthetic data appears only in `tests/`.

## The experiment

| | |
|---|---|
| **Target** | RTE national solar (photovoltaic) generation, MW, 30-minute resolution |
| **Forecast origin** | 12:00 Europe/Paris on D-1 — the European day-ahead market gate |
| **Forecast window** | the whole delivery day D, 00:00–24:00 local (48 half-hours) |
| **Horizons** | +12 h to +35.5 h, i.e. steps 24–71 of a 30-minute grid |
| **Inputs** | 90 days of past generation. Nothing else — no weather, no calendar, no capacity |
| **Backtest** | one origin per delivery day, rolling across the test period (366 days by default) |
| **Metrics** | MAE, two nMAE variants, relative improvement over each baseline |

### Methods

| Name | Definition |
|---|---|
| `t0` | `t0-alpha`, zero-shot. The 0.5 quantile is the point forecast, because MAE is minimised by the conditional median. |
| `prev_day` | The same UTC clock time on the most recent day whose value was observable at the origin. |
| `prev_week` | The same UTC clock time seven days earlier. |

Two details in `prev_day` are worth stating plainly, because both are easy to get
silently wrong:

**It is not always yesterday.** At a 12:00 D-1 gate, only the first half of D-1
has happened. For delivery half-hours up to local noon, "same time yesterday"
means D-1 and is legal; after that the D-1 value lies beyond the gate, so the
baseline falls back to D-2. Using D-1 across the whole day would be leakage — a
forecast that quietly knows how yesterday afternoon turned out. Expect a visible
step at midday in the per-horizon chart; that step is real, and an operator
running this baseline lives with it.

**The lag is taken in UTC, not local clock time.** The diurnal solar cycle
follows solar time, so a fixed 24-hour UTC lag *is* "the same solar time
yesterday" and stays aligned through both DST switches.

Plain last-value persistence is deliberately absent: from any night-time origin
it forecasts a flat zero day, which is a strawman rather than a comparator.

### Metrics

With errors `e = y - ŷ` over the scored points:

| Metric | Definition | Why |
|---|---|---|
| `mae_mw` | `mean(|e|)` | Physical units. What a trading or balancing desk feels. |
| `nmae_mean` | `sum(|e|) / sum(y)` | The ranking metric. Note it is a **ratio of sums**, never a mean of per-point ratios — solar is zero for half of every day, so per-point ratios are undefined at night and explode at dawn. It is also close to invariant to how much night you include, which makes it comparable across studies that made different choices there. |
| `nmae_peak` | `mae / p99(y)` | A capacity-normalised view, comparable with the solar literature's convention. The p99 of observed generation over the scored period stands in for installed capacity, so the benchmark needs no second dataset. Reporting scale only — no model sees it. |
| relative improvement | `1 - mae_model / mae_baseline` | The headline comparison, with a 95% moving-block bootstrap CI (7-day blocks, resampling delivery days) and a win rate. |

Every metric is reported twice: **all hours** and **daytime only**. Night is
roughly half of every day and every sane method predicts ~0 there, which flatters
all of them equally and compresses the differences.

The daytime mask marks a `(month, half-hour)` pair as daytime when its mean
observed generation over the scored period clears 1% of the peak proxy. It is a
**reporting filter**, not a model input: it chooses which observed rows the
daytime tables average over, identically for every method, so it cannot leak
anything into a forecast. Deriving it from the scored period rather than from
prior history means it is always defined for every month being scored — a mask
learned from a short history marks whole calendar months as night and silently
corrupts both the daytime tables and the night diagnostic. Using generation
climatology rather than solar geometry also keeps the benchmark free of
astronomical inputs.

There is also a **night sanity check**: the mean forecast over night half-hours,
per method. It should be ~0 MW. A foundation model that hallucinates generation
in the dark shows up there immediately.

## Model access

`t0-alpha` is Apache-2.0 but its Hugging Face repository is **gated**:

1. Sign in at <https://huggingface.co/theforecastingcompany/t0-alpha> and accept
   the access conditions.
2. Authenticate your Python environment with a token from that same account —
   `hf auth login`, or set `HF_TOKEN` for scripts and CI. Signing in to the
   website alone is not enough.

The model is ~102M parameters and runs on CPU; no GPU is required. Every origin
in a batch goes through one forward pass, so a full year is minutes, not hours.
Pin `--revision <sha>` if you want byte-identical reruns across model updates.

Run `python run_benchmark.py --no-t0` to exercise the baselines without
downloading any weights.

## Data

Source: **RTE éCO2mix**, published as open data on Open Data Réseaux Énergies
(ODRÉ), dataset [`eco2mix-national-cons-def`](https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/).
Downloaded through the Explore v2.1 CSV export — no API key, no OAuth.

Things the loader handles, because each of them will otherwise corrupt a
30-minute benchmark:

- **30-minute production on a 15-minute row grid.** Only `:00` and `:30` carry
  generation; the rest are consumption forecasts and are dropped.
- **Timezones.** Everything is normalised to a strict 30-minute **UTC** index.
  Naive local timestamps are localised to Europe/Paris first.
- **DST.** Delivery days are local, so they are 46 or 50 half-hours twice a year;
  those days are forecast at their true length rather than truncated or skipped.
  In the annual bulk files the spring-forward gap is padded with repeated rows
  (discarded) and the autumn repeated hour is missing (left as an explicit gap).
- **Gaps.** Missing values stay NaN on the grid and are reported in
  `data/manifest.json`; they are never interpolated. Delivery days with an
  incomplete target window are dropped from the backtest and counted in
  `results/summary.md`.
- **Negative night values.** RTE really does report −1/−2 MW at night. Observations
  are left alone; only *forecasts* are clipped at zero, identically for every
  method.
- **Revisions.** The series is consolidated at M+1 and definitive in H2 of A+1,
  so recent months will change under you. The default test year is 2024, which is
  definitive — that, plus the caches, is what makes a rerun reproduce.

If the download fails, or you would rather work offline, pass any eCO2mix file
directly — the parser accepts both the ODRÉ CSV and the annual `.xls` bulk files
(which are really cp1252 TSV):

```bash
python run_benchmark.py --csv path/to/eCO2mix_RTE_Annuel-Definitif_2024.xls
```

A single annual file scores fewer days than the default: the first ~90 delivery
days of the file have no full context window and are skipped (and counted) rather
than forecast from a short history. Pass two or three years for the full test
period.

> **Licence / attribution.** Licence Ouverte / Open Licence (Etalab). Reuse is
> permitted, including commercially, with attribution:
> *Source: RTE — éCO2mix, via Open Data Réseaux Énergies (ODRÉ), Licence Ouverte
> (Etalab).* RTE publishes these indicators for information and accepts no
> responsibility for the use made of them.

## Outputs

Everything lands in `results/` (gitignored — it is derived data):

| File | Contents |
|---|---|
| `summary.md` | The headline tables: MAE/nMAE all-hours and daytime, improvement over each baseline with CIs and win rates, the night check, and what was dropped |
| `metrics.csv` | The same metrics, tidy |
| `skill.csv` | Per-baseline skill, CI, win rate, for both the all-hours and daytime slices |
| `per_day_errors.csv` | Per delivery day and method — the unit of analysis for the bootstrap |
| `by_month.csv`, `by_slot.csv` | Pooled MAE / nMAE by calendar month and by half-hour of the delivery day — the tables behind figures 2 and 3 |
| `forecasts_<hash>.parquet` | Every forecast, keyed by run config, so reruns skip inference |
| `run_meta.json` | Git SHA, arguments, package versions, data manifest, timings |
| `figures/fig1_representative_days.png` | Four delivery days chosen by a fixed rule: median-error, worst-error, highest-output summer, lowest-output winter. Stated up front so the panel cannot be cherry-picked |
| `figures/fig2_error_by_time_of_day.png` | MAE by position in the delivery day — is the edge uniform, or concentrated on the ramps? |
| `figures/fig3_by_month.png` | Seasonal breakdown, so one season cannot be sold as a general result |
| `figures/fig4_skill.png` | Improvement over each baseline with bootstrap CIs, and the per-day paired differences — separating "wins consistently" from "wins on five spectacular days" |
| `figures/fig5_forecast_vs_actual.png` | Daytime forecast vs actual, with slope and bias — exposes regression toward the diurnal mean, the classic zero-shot failure mode |

## Running it on GitHub Actions

If you would rather not run it locally, `.github/workflows/benchmark.yml` runs the
same benchmark on a GitHub runner. It is **manual only** — it downloads real RTE
data and the gated model, so no push or PR triggers it.

**Actions** tab → **Benchmark** → **Run workflow** → pick a **size** → **Run workflow**.

| Size | Delivery days | What it is for |
|---|---|---|
| `smoke` (default) | 5 | Proves the whole path works: data download, gated model, backtest, figures |
| `month` | 30 | A quick sanity read before committing to the full year |
| `full` | all of 2024 | The real benchmark |

Only the number of scored delivery days changes — the forecast origin, horizon,
context, baselines and metrics are identical across all three.

The run needs one repository secret, **`HF_TOKEN`**: a Hugging Face token whose
account has accepted the `t0-alpha` access conditions. Before doing any work the
workflow checks that ODRÉ is reachable and that the token can actually read the
gated repo, so a misconfiguration fails in seconds with a message saying which of
the two it was, rather than deep inside the run.

Results come back two ways:

- **Job summary** — `results/summary.md` is rendered on the run's page, so the
  headline tables are readable without downloading anything.
- **Artifact** — `results-<size>-<run number>` contains the whole `results/`
  folder: metrics, per-day errors, forecasts and all five figures. Kept 30 days.

Both are produced even if the run fails partway, so a partial result is still
inspectable.

Runs cache the pip downloads, the Hugging Face model and the downloaded RTE data,
so a second run is much faster. If a cache is ever stale or half-written, bump
`HF_CACHE_VERSION` or `DATA_CACHE_VERSION` at the top of the workflow.

## Useful flags

```bash
python run_benchmark.py --help

--test-start 2023-01-01 --test-end 2023-12-31   # a different test year
--data-start 2021-01-01 --data-end 2026-01-01   # widen the download
--context-days 30                               # shorter context for t0
--gate-hour 0                                   # midnight issue instead of the market gate
--limit-days 20                                 # quick end-to-end check
--no-t0                                         # baselines only, no weights
--revision <sha>                                # pin the model for exact reruns
--force-download / --force-forecast             # bypass the caches
```

## Sanity checks

Rough expectations from the solar-forecasting literature, for checking your run
is in the right universe (all-hours, `nmae_mean`): same-time-yesterday style
baselines land around 45–65%; a good no-weather foundation model would be
roughly 30–45%; operational NWP-driven forecasts reach 12–25% and are not a fair
comparison here. **A method below ~10% has a leak, not a breakthrough.**

## Tests

```bash
python -m pytest tests/ -q
```

They cover the four things that silently break this kind of benchmark:

- **Data alignment** — strict 30-minute UTC grid, unique and monotonic; negative
  night values preserved.
- **Forecast horizons** — 48 targets and a 71-step horizon on a normal day; 46/69
  and 50/73 on the DST days; the first target exactly 12 h after the gate.
- **Timezone/DST** — the spring padding is discarded, the autumn gap stays an
  explicit NaN, and across both switches a baseline's source is the observation
  exactly 7×24 h earlier *and* at a different local clock time, which is what
  distinguishes a UTC lag from a naive same-local-time lookup. A day truncated by
  the edge of the data is not mistaken for a 46-slot DST day.
- **Leakage** — every source timestamp is at or before the origin; the backtest
  raises on a forecaster that peeks; and rewriting all data after a window's
  origin changes none of its forecasts.

Fixtures are synthetic and no test touches the network.

## Layout

```
.github/workflows/
  benchmark.yml         manual GitHub Actions run (smoke / month / full)
run_benchmark.py        CLI: download → backtest → metrics → figures
solarbench/
  data.py               ODRE download, parsing, UTC normalisation, caching, manifest
  forecasters.py        the two baselines and the t0 adapter
  backtest.py           windows, rolling origins, leakage assertions
  metrics.py            MAE, nMAE, skill, block bootstrap, daytime mask
  plots.py              the five figures
tests/test_benchmark.py alignment, horizons, timezone/DST, leakage
```

## Scope

Deliberately out: weather covariates, regional models, storage optimisation,
dashboards, deployment. Adding a forecaster is a small class with a `predict`
method plus one line in `run_benchmark.py` — a 7-day same-half-hour mean, or a
clear-sky-index persistence, are the obvious next baselines.

## Known limitations

- **One gate.** Only 12:00 D-1 is a first-class citizen. `--gate-hour` moves it,
  but the baselines' D-1/D-2 switchover point moves with it.
- **`nmae_peak` uses a proxy.** p99 of observed generation, not RTE's installed
  capacity series. French PV capacity grew quickly, so comparisons across
  distant years are approximate.
- **The point forecast throws away `t0`'s distribution.** The model emits
  quantiles; only the median is scored. Pinball loss / CRPS would use the rest.
- **Mask sensitivity is not swept.** The daytime threshold is 1% of the peak
  proxy, fixed.
- **Bootstrap intervals need days.** Below ~14 delivery days the 7-day block is
  shortened and the interval is indicative only; the run warns when this happens.
