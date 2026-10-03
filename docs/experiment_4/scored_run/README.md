# Experiment 4: the scored run's outputs

These are the outputs of the one scored run of Experiment 4, copied here so the record outlives the run's
Actions artifact. Nothing in this folder is read by the code.

- **Run:** [Actions run 36823477529](https://github.com/xuanhuyle/solar/actions/runs/36823477529)
  (job 110243900839), workflow `prices.yml`, mode `run`, 2026-10-01.
- **Commit:** `2b407f42c03d2734ef4170cfb3e66962dbba9552`, the freeze commit.
- **Frozen specification:** `PRICE_SPEC_SHA256`
  `225774c89e301166c2d4850e2f894335fd5ae703dc410bc4a06aa246ac5755bc`.

## What each file is

| file | what it is | sha256 |
|---|---|---|
| `summary.md` | the frozen reading, as printed by the run | `ad576ac41c69b5921802f2c754b10283b679f6a50e5f9b4b13f02eb35eb0bdae` |
| `results.json` | every primary, secondary, slice, table and carry-forward value | `a5d509f867066f0af7d53f5d3dd5e802bde2465e7a86355d88dad8294c49b8dc` |
| `run_meta.json` | gates, provenance, data checks, the leak check and the amendments | `63e13ded2fc60ff7760d5acfca231fe25e9363c287ba610a07c7d1efaa199b53` |
| `program_role.md` | the programme-role note the run printed beside the summary | `179a58b17fe8f262423c3e0f60fa1c60cd837359741b21f36e657300e21bb05f` |
| `FACT_SHEET.md` | every published figure, with its JSON path, after independent verification | |
| `verify_integrity.md`, `verify_reading.md`, `verify_statistics.md` | the three independent verification reports behind the fact sheet | |

## Where they came from

- The run echoes these four output files to its log, between `##[group]` markers. They were extracted from that
  log. An independent re-extraction gave byte-identical files.
- The run's artifact is `prices-run-36823477529`, id 11145568607, upload digest
  `98d8ca1f7c6f8f6bdfeba807b925bfee25ed1cd9da7a5e46b24acc88be436165`. It also holds `per_day_P1.csv`,
  `per_day_P3.csv`, `per_day_P4.csv` and `forecasts.csv.gz`.
- Those four files could not be downloaded from this session, because the proxy refuses the artifact host. For
  that reason the bootstrap draws and the per-day losses were not recomputed independently. The figures taken
  from the run are internally consistent: see `FACT_SHEET.md`, section 1.
