# Research-loop proof: a disposable sandbox (design only)

*Design and implementation plan for the owner's approval (2026-10-02). Nothing here is implemented or run. It
makes no researcher proposal call and changes nothing in Experiment 4, batch B1, the vault or the engine ledger. N1
and its review stay as historical evidence. B1's content-addressed loading fix stays separate. It is not part of this
sandbox.*

## 0. In one page

**Purpose.** Show the autonomous research loop end to end in a controlled world where the truth is known. The
researcher:
- uses t0-alpha as a cheap instrument to test candidate covariates under a fixed budget;
- keeps a notebook of every result, including failed hypotheses;
- notices when a relationship stops working;
- submits its conclusions.

An evaluator that alone holds the truth then scores them on data nobody has seen.

**Shape.**
- **Scenarios:** 10 seeded synthetic scenarios, each an hourly target with 12 anonymised candidate covariates:
  - genuine drivers (strong, nonlinear and weak);
  - a driver that is retired at a hidden change point;
  - a driver that emerges at that point;
  - a correlated decoy;
  - a seasonal proxy;
  - a diurnal proxy;
  - noise.
- **Rounds and budget:** 6 research rounds, 14 experiments per scenario.
- **Data:** a 90-day confirmation segment after the change, which no research job ever holds.
- **Arms, all on the same budget:**
  - the AI researcher with t0;
  - a fixed scripted screen with t0;
  - the same script with a matched conventional model.

**What it can establish.** Within planted worlds, whether t0 plus the AI researcher:
- finds the real drivers;
- rejects the decoys;
- recognises the change;
- does better than a script on the same budget.

It also measures t0's own covariate use, by history length, against the conventional model. It cannot establish
anything about real markets.

**Effort.**
- **Recommended (cut) version:** about 3.5 engineer-days, about half a day over the 1–3 day target, for the reasons
  in section 9. A stop-or-continue check after day 1 tests whether t0 can see the planted drivers at all; if it
  cannot, the work stops there, at about 1.5 days.
- **Fuller version:** about 5 days (section 9).

**Compute and cost (estimates).**
- 50–65k t0 forecast-days, or 3–11 runner-hours: about 1–1.5 h of wall time for the scored run with parallel
  jobs, plus about 1 h for calibration.
- About 80 API calls, about 0.8–1.0M tokens.

## 1. Can the repository support it? Yes, as a small isolated package

| Need | Existing component | Use |
|---|---|---|
| Load t0-alpha by content | `solarbench/t0_pinned.py` (`fetch` :45, `load` :77, `PINNED_SHA256` :25) | As-is; plus about 10 lines to load a verified local snapshot offline |
| Call t0 on arrays with known-future covariates | `model.predict(context [B,L], horizon, future_covariates [B,K,L+H])`; single-row pattern in `solarbench/price_gates.py:350` (`k2_reference`) | Pattern, batched |
| Catch silently sanitised t0 output | `_NonFiniteWatcher`, `solarbench/forecasters.py:369` | Copy about 10 lines (importing it pulls in heavy modules) |
| Paired skill with a block-bootstrap interval | `solarbench/metrics.py` `per_day_errors` :87, `bootstrap_skill` :104, `pair_skill` :224 (numpy and pandas only) | As-is |
| Canonical JSON and hashes | `engine/canon.py` (`canonical_json`, `sha256_of`) | As-is |
| API call helpers (usage, retries, cleaning) | `engine/researcher.py` `_usage` :163, `_text` :169, `_storable` :180, `transient` :193, `_retry_after` :202 | Copy and adapt about 60 lines; the module imports engine internals, and `call_model` is tied to its own schema |
| Declared-hash artifacts and static workflow tests | `engine/record.py:133-149`; `tests/test_engine_workflow.py` | Pattern |
| Offline test doubles | fake API client `tests/test_engine_researcher.py:27-42`; tiny real t0 `tests/test_t0_pinned.py:16-23` | As-is |

**Not reused.**
- `engine/ledger.py`: its schema is pinned by B1.
- `solarbench/lear.py`: price-specific and not information-matched.
- The engine's probe path: it cannot load t0 today and is shared with B1.

**What must be written new:**
- a generator;
- a small experiment executor;
- the AI loop;
- two scripted arms;
- a numpy ridge;
- an evaluator;
- one workflow.

**Constraint.** t0 weights and the API key exist only on GitHub Actions, so every run, timing and calibration
happens there.

## 2. The world (frozen before any run)

**Grid.** Hourly data, day-ahead: the forecast origin is the end of day D−1 and the horizon is the 24 hours of day D.

**Segments of each scenario (390 days):**
- 120 warm-up days;
- 180 research days, revealed in 6 rounds of 30;
- 90 confirmation days, all after the change.

**Target.** `y = level + daily profile + weekly profile + slow annual cycle + Σ planted effects + daily AR(1) shock + hourly AR(1) noise`.

**Candidates, anonymised as X01–X12 and shuffled per scenario.**
- All candidates are published ahead (known-future).
- They are standardised with warm-up statistics only, so later data does not leak through the scaling.
- "Weather-like" means a daily AR(1) level times a smooth daily shape, plus noise.

| Slot | Generation | Truth in change / stable / null scenarios |
|---|---|---|
| G1 | weather-like, φ = 0.8 | linear driver, strong / strong / phantom |
| G2 | weather-like, φ = 0.7 | hinge above its own 70th percentile, strong / strong / phantom |
| G3 | weather-like, φ = 0.6 | linear driver, weak / weak / phantom |
| RA | weather-like | strong driver retired at τ / strong throughout / phantom |
| RB | weather-like | zero before τ, strong after / phantom / phantom |
| C1 | 0.8·G1 + 0.6·independent | non-causal, correlated with G1 |
| S1 | the target's annual phase + noise | non-causal, slow seasonal proxy |
| D1 | fixed daily shape × (1 + small daily noise) | non-causal, diurnal proxy |
| N1–N4 | AR(1) with φ_d ∈ {0.2, 0.5, 0.8, 0.95}; two have a daily shape | non-causal noise |

"Phantom" means generated exactly like a driver but with zero effect.

**Change.** τ is drawn from research days 95–125, never at a round boundary. Total driver variance is kept constant
across τ, so the change shows only through covariate experiments, not through the target's variance.

**Effect sizes.**
- They are set as variance ratios against the noise: strong 0.6, weak 0.15, times a multiplier m ∈ {1, 2}.
- m is fixed once, by the calibration rule (section 7), on 3 calibration seeds that are never scored.
- Effects act through day-to-day variation, because t0 z-scores each covariate within its own window and so cannot
  see slow level shifts.

**Scenarios.**
- 10 are scored: 6 with a change, 2 stable, 2 null.
- Evaluation seeds = `sha256(<F1 commit sha>:<scored workflow run id>:i)`. The run id is assigned only when the
  owner-approved scored run is dispatched, so the implementer cannot generate and preview the scored worlds
  beforehand. Every dispatch is reported, aborted ones included, so a re-dispatch cannot be used to re-roll quietly.

**Decoy labels.** A non-causal candidate counts as a decoy for an instrument only if adding it to the true set does not
improve that instrument on the confirmation data (95% lower bound ≤ 0). Otherwise it is labelled "useful non-causal"
and is neither rewarded nor penalised. This settles the diurnal proxy: t0 receives no timestamps, so a daily-shaped
series can carry real phase information for t0.

## 3. Hiding the truth, mechanically

The researcher is an API call with no tools, so it sees only its prompts. The guarantee is therefore that every
prompt is built from the observed data and its own earlier answers, and from nothing else. The mechanisms are below.

**Jobs.**

| Job | Holds | Never holds |
|---|---|---|
| `generate` (no secrets) | generator, seeds | uploads only the observed data: the 120 warm-up days and the 180 research days (anonymised IDs, standardised values), with a declared sha256 |
| `lab` (matrix: scenario × arm) | observed artifact only. Sparse checkout without `research_loop_proof/truth/`, and a guard step that fails if that directory exists | truth, labels, effects, τ, the confirmation segment |
| `evaluate` (matrix over scenarios, after `lab`) | full checkout; regenerates its scenario from the seeds, checks the observed data bit for bit, runs the oracle and label forecasts and scores the arms | — |
| `report` (no secrets) | aggregates the per-scenario scores and applies the outcome map | — |

**Inside `lab`.**
- Each round gets a copy of the data truncated at that round's cutoff, and the executor checks every window against it.
- Warm-up days serve only as context. Experiment windows must lie within the research days revealed so far.
- t0 sees only the L days ending at each forecast origin, plus covariates up to the forecast horizon.

**Checks.**
- The evaluator rebuilds every prompt byte for byte from the observed artifact and the recorded responses. Any
  mismatch makes the run VOID.
- The evaluator scans prompts for canary strings planted in the truth files.
- **Tests:**
  - no module under `lab/` imports `truth`;
  - a poison test: data after a cutoff set to NaN leaves prompts and results identical;
  - a static workflow test checks which job gets which artifact and secret.

**Secrets, scoped by step.**
- `HF_TOKEN` only for the weights download.
- The API key only for the loop step, which runs with `HF_HUB_OFFLINE=1`.
- The model's output is parsed as data and never reaches a shell.

## 4. The research loop

**What the researcher sees.** A fixed brief, the same for every scenario:
- an hourly day-ahead target;
- 12 anonymous candidates, all published ahead;
- "any number of them, including none, may be useful";
- "the process is not guaranteed to be stationary";
- the experiment menu and the budget.

Each round it also gets:
- the revealed date range and the budget left;
- the full notebook: every earlier experiment and result, its earlier belief tables and notes, failed ones included.

It writes no code and never sees raw data.

**Experiment menu (declarative JSON).** The researcher chooses:
- 1–4 covariates;
- a reference set of 0–3 candidates (for conditional tests such as "does X07 add anything given X03?");
- a t0 context of 7, 28 or 112 days;
- a window of 14–60 revealed research days (14 days is the shortest window on which the bootstrap keeps its 7-day
  blocks);
- optionally, the `shift7` placebo on one covariate: its own values from 7 days earlier, which keeps its shape and
  breaks its day-specific alignment.

Each experiment returns:
- the MAE of the covariate set and of the reference;
- paired skill with a 95% block-bootstrap interval (`metrics.bootstrap_skill`, 7-day blocks);
- days won;
- skill per 10-day sub-block, marked indicative;
- CPU seconds.

**Budget.** 14 experiments per scenario, at most 3 per round. Unspent budget is allowed and costs nothing.

**AI researcher.** 7 calls per scenario: one per round, plus a final call after round 6's results.
- **Output, one small schema** (a large one failed before with "compiled grammar too large"):
  - notes;
  - a belief row for each of the 12 candidates: status ∈ {untested, promising, accepted, rejected, redundant,
    deteriorated}, `since_day`, cited experiment ids;
  - up to 3 experiments, each with a `because` that cites earlier entries.
- **The final call's belief table is the submission.**
- **Invalid output:** one repair turn; after that the round is skipped and the skip recorded. If the final call fails
  after its repair, the last valid belief table is the submission; if there is none, the arm counts as missing for
  that scenario.
- **Token cap:** the sandbox enforces its own cap in code. Each AI job stops at its share of the run budget (the run
  budget ÷ 10 scenarios, about 100k tokens). The engine's 2M-per-day cap does not apply: it counts only
  `research_call` entries on the engine ledger, which the sandbox never writes.

**Notebook.** An append-only JSONL file of calls (full prompt, response, usage), experiment specs, results and belief
tables. It is the artifact the evaluator audits.

## 5. Comparators

- **M1 (scripted, t0)**, fixed before any run:
    - Rounds 1–6: screen 2 candidates per round against no covariates, in shuffled order, at a 28-day context, on that
    round's 30 new days. Each candidate is screened once. A candidate is accepted if its 95% lower bound is above 0.
  - Round 6: with the 2 remaining experiments, recheck the 2 accepted candidates with the oldest evidence on round
    6's days, and drop any whose lower bound is now ≤ 0, marking it deteriorated.
  - It is a fixed, pre-planned schedule: what a simple screen does with the same budget. It cannot adapt (for example,
    rescreen a rejected candidate after a change), and adaptivity is exactly what the AI may add.
- **M2 (scripted, conventional):** the same rule with an information-matched numpy ridge ARX.
  - Features: hour dummies; target lags of 24 and 48 hours (168 hours only when L ≥ 14); each covariate as x and x².
  - α is chosen by GCV.
  - It is fitted on the same L-day window only, with no day-of-week dummies, because t0 cannot see the day of the week.
- **What each comparison isolates:**
  - AI vs M1: the researcher (same instrument, same budget).
  - M1 vs M2: the instrument (same research rule).
- **Evaluator oracle, on the confirmation data:**
  - t0 and ridge, each with no covariates, the true current set, and the true set plus RA, at contexts of 7, 28 and
    112 days. This answers the forecasting questions.
  - A marginal value for each candidate given the true set.
    - Single-driver **discoverability** for t0. A strong driver is discoverable if t0 with that driver alone, against
    no covariates, at a 28-day context, has a 95% lower bound above 0 on the last 60 research days on which the
    driver is active (for RA, the days before τ; for RB, the days after τ, all of them if fewer than 60). This
    separates what t0 can use from what the researcher found.
  - **The oracle fraction** of a final set is its t0 confirmation skill against no covariates, divided by the true
    current set's, both at a 28-day context. The ridge competence check (section 7) also uses a 28-day window.

## 6. What is measured

**Forecasting capability** (evaluator, truth known):
- t0 true-set skill against t0 with no covariates, at 7, 28 and 112 days of history;
- the same for ridge;
- t0 against ridge at each history length;
- which non-causal candidates each instrument nonetheless benefits from.

**Autonomous research capability** (per scenario and arm):
- recall of strong drivers, overall and counting only the discoverable ones;
- whether the weak driver was found;
- decoy acceptances, separately for C1, S1, D1 and noise;
- RA kept in the final set;
- RA flagged as deteriorated, and the error of its `since_day` against τ;
- RB found;
- detection delay in rounds, read from the belief tables;
- false alarms in stable and null scenarios;
- the confirmation skill of the final set, against no covariates and as a fraction of the oracle's;
- each experiment classified as screen, follow-up, recheck, conditional, placebo or repeat.

**Learning from experience.**
- **What is measured.** Retention is guaranteed by construction, because the whole notebook is in every prompt. What is
  measured is its influence:
  - the share of experiments and beliefs whose citations are valid;
  - whether actions are consistent with earlier evidence (no re-testing a rejected candidate without a stated reason;
    rechecking accepted drivers after sub-block skill falls);
  - whether failed experiments are cited later.
- **What it does not show.** That accumulated knowledge improves research across problems. That needs the comparison
  in section 11.

**Research economics** (per arm):
- experiments run;
- t0 forecast-days and CPU seconds;
- API calls, input and output tokens, repairs;
- wall time per round;
- implementation effort, as engineer-hours logged by the implementer;
- valid discoveries (true drivers found, minus decoys accepted, minus RA kept) per experiment and per 100k tokens.

Using more experiments never scores as better research. Unspent budget counts in an arm's favour.

## 7. Freezes and the outcome map

**F0, frozen before any real t0 run:**
- the generator, labels and strengths;
- the calibration seeds and the calibration rule;
- M1 and M2;
- the brief, including a pre-declared condition on its menu: if the smoke run measures more than 1.5 s per t0
  forecast-day at a 28-day context with 4 covariates, the 112-day context is removed.

**Calibration (stop-or-continue check, day 1)**, on the 3 calibration seeds, with t0 at a 28-day context on 30-day
windows:
- Pass if the median z of single-strong-driver skill is at least 3 and the ridge true set gains at least 15%.
- If not, double the strengths once and recheck.
- If it still fails, the result is **INSTRUMENT FAILURE** and the work stops there.

**F1, frozen before the scored run:**
- `frozen.json`: m, every threshold, the brief's sha256, the schema and the evaluator code.
- A short independent review of the scoring code checks it against this document.
- The owner approves F1.
- The scored run follows with no changes, and every run is reported, aborted ones included.

**Outcome map** (the first match wins, so the outcomes cannot overlap):

1. **VOID:** any of:
   - the observed data are not bit-identical on regeneration;
   - a prompt cannot be rebuilt, or a canary is found;
   - the poison test failed;
   - the ridge true set has a lower bound ≤ 0 in 2 or more non-null scenarios;
   - an arm is missing in 2 or more scenarios.
2. **INSTRUMENT FAILURE:** the median t0 true-set skill at a 28-day context is below 5%, or fewer than half the strong
   drivers are discoverable with t0.
3. **CEILING (the world is too easy):** the fixed script M1 finds every discoverable static strong driver (G1, G2)
   with no decoy accepted in at least 7 of 8 non-null scenarios, and drops RA in at least 5 of 6 change scenarios.
   The emerging driver RB is left out of this test, because a fixed schedule cannot rescreen after a change.
4. **RESEARCH SUCCESS:** all of:
      - the AI scores at least 6 points against M1 over the 8 non-null scenarios (1 point for a higher oracle fraction,
     half a point for a tie);
   - recall of discoverable strong drivers is at least 0.8;
      - mean decoys accepted plus RA kept is at most 0.5 per scenario, and at most M1's (RA kept counts only in change
     scenarios: in stable scenarios RA is a true driver);
   - RA is kept in at most 1 of 6 change scenarios;
   - at most 1 false alarm across the 4 stable and null scenarios;
   - each null scenario has at most 1 accepted candidate.
5. **RESEARCH FAILURE:** any of:
      - the AI scores at most 3 points against M1 (the mirror image of the success rule);
   - mean decoy errors are at least 1.5;
   - RA is kept in 3 or more of 6;
   - at least 2 candidates are accepted in a null scenario.
6. **MIXED:** anything else.

**How results are read.**
- Learning and economics are reported descriptively. They do not enter the outcome.
- Results are counts, not significance tests. If the AI and the script were interchangeable and never tied, 6 or
  more points of 8 would occur by chance about 14% of the time; ties are reported alongside.
- No result is described as validation on real markets.

## 8. The owner's requirements and safeguards, mapped

| Requirement | Where |
|---|---|
| 1-3. Target depends on several candidates; some genuine; others irrelevant, correlated decoys or seasonal proxies | §2 table |
| 4. Relationships change at a predefined point | τ, RA/RB (§2) |
| 5. Researcher not told the relationships | anonymised, shuffled IDs; the truth physically absent from `lab` (§3) |
| 6. t0-alpha evaluates candidates without task-specific training | the only instrument in the AI's menu (§4) |
| 7. A competent conventional comparison | matched ridge (M2 and oracle); VOID if it is not competent (§5, §7) |
| 8. Fixed experimentation budget | 14 per scenario, at most 3 per round (§4) |
| 9. Evidence retained and used | notebook in every prompt; cited beliefs (§4, §6) |
| 10. Untouched confirmation segment | 90 post-change days, never uploaded and never held by a `lab` job; only `evaluate` uses them (§2, §3) |
| Safeguard: freeze generation rules and seeds | F0/F1; seeds derived from the F1 sha (§2, §7) |
| Safeguard: mechanisms hidden | §3 |
| Safeguard: t0's use separate from the researcher's discovery | oracle and discoverability labels (§5) |
| Safeguard: equivalent information | matched L-day ridge; no day-of-week for either (§5) |
| Safeguard: no future access | per-round truncated data, window checks, poison test (§3) |
| Safeguard: failed hypotheses preserved | notebook (§4) |
| Safeguard: independent evaluator | separate job, regenerates from seeds, rebuilds prompts (§3) |
| Safeguard: allowed to fail | INSTRUMENT FAILURE, CEILING, RESEARCH FAILURE (§7) |
| Safeguard: not real-market validation | §12 |

## 9. Implementation plan

**Files** (disposable; deleting the folder, the workflow and the test removes it):
```
research_loop_proof/truth/{generator.py, evaluate.py, frozen.json}
research_loop_proof/lab/{data.py, instruments.py, executor.py, researcher.py, scripted.py, run.py, brief.md}
.github/workflows/research-loop-proof.yml     (modes: smoke | calibrate | run)
tests/test_research_loop_proof.py
docs/research_loop_proof/                       (this design; later the frozen spec and results)
```

**Engineer-days**, cut version:

| Component | Days |
|---|---|
| Generator, labels, seed rule, hash pins | 0.5 |
| Observed export, per-round view, poison test | 0.25 |
| Instruments: batched t0 with offline load; ridge | 0.5 |
| Executor: validation, bootstrap, sub-blocks, `shift7`, reference sets | 0.4 |
| AI loop: prompt builder, schema, repair, notebook, cap; fake-client tests | 0.5 |
| M1 and M2 | 0.2 |
| Evaluator: regeneration, prompt rebuild, canary scan, oracle and label runs, outcome map, markdown report | 0.6 |
| Workflow and static tests | 0.3 |
| Smoke and calibration runs on Actions, fixes | 0.3 |
| **Total** | **about 3.5** |

The full version adds about 1.4 days, for about 5: a second AI replicate per scenario, re-running a sample of AI
experiments in the evaluator, a script with twice the budget, extra oracle contexts, and plots.

**Order.**
- **Day 1:** generator, instruments, the brief and M1/M2 rules frozen (F0), the timing smoke run, then calibration as
  the stop-or-continue check.
  - The smoke run measures t0 timing at each context with 0, 2 and 4 covariates, plus ridge timing, and applies the
    pre-declared 112-day rule.
- **Day 2:** executor, AI loop, M1 and M2; then two real API rounds on a calibration seed, to confirm the schema is
  accepted and to measure tokens.
- **Day 3 and a half:** evaluator, workflow, F1 freeze, the scored run, the report.

**Why not 1 day, and why it lands about half a day over 3.**
- t0 cannot run in this development container, so every timing or calibration step is an Actions round trip of
  15–60 minutes.
- Hiding the truth (the evaluator, the prompt rebuild, the separate jobs) is about a third of the work. It is also what
  makes any result credible.
- A 1-day version would have to drop either the truth separation or the scripted control, and its results could not
  be read.

## 10. Compute and cost (planning estimates; the smoke run replaces them)

**t0 forecast-days (one day of 24 hourly forecasts at one origin):**

| Item | Forecast-days |
|---|---|
| AI arm, per scenario | about 860 |
| M1, per scenario | about 600 |
| Evaluator, per scenario | about 3,200 |
| 10 scenarios, total | about 47k |
| Calibration (doubles if the strengths are doubled) | about 8k |

- **Runtime:** at the expected 0.2–0.6 s per forecast-day, this is 3–9 runner-hours, or up to about 11 if the
  strengths have to be doubled at calibration. Recorded figures for the engine's
  larger 90-day half-hourly context were 0.37–0.74 s.
- **Wall time:** about 1–1.5 h for the scored run, because both `lab` and `evaluate` run as matrix jobs (one
  evaluator job holds about 3,200 forecast-days, 11–32 minutes), plus about 1 h for calibration.
- **Ridge:** negligible.
- **API:** 7 calls × 10 scenarios plus about 10% repairs, so about 80 calls.
  - Prompts grow from about 3k to 14k tokens as the notebook fills.
  - Output, including thinking, is about 2–4k tokens per call.
  - Total about 0.8–1.0M tokens, limited by the sandbox's own cap (section 4). Dollar cost = these tokens × the configured researcher
    model's list price.
- **Owner setup:** none. It uses the existing `HF_TOKEN`, `ANTHROPIC_API_KEY` and `RESEARCHER_*` settings.

## 11. Later: the controlled comparison for accumulated knowledge (designed, not run)

- **Conditions** (12 fresh scenarios, run in 3 random orders):
  - **L:** the researcher writes a lessons note (at most 1,500 characters) at the end of each scenario and carries it
    into the next;
  - **F:** always starts with an empty note.
- **Held fixed:** brief, schema, model, effort and budget.
- **Primary measure:** the mean research score on positions 7–12, L minus F, judged against the spread between orders.
- **Cost:** about 72 trajectories and 5.5M tokens, spread over about 3 days to keep each day's spend under the owner's 2M-per-day budget, which the sandbox
  enforces itself.
- **When:** only after this sandbox shows the loop works at all.
- **What it would show:** accumulated knowledge improving research choices, which the sandbox alone cannot show.

## 12. Limits

- **Synthetic worlds.** Success shows research behaviour under controlled conditions, not value on real markets.
- **Opposite biases.** The linear-additive world suits ridge. t0 was partly pretrained on synthetic covariate
  generators, which favours t0. Neither instrument result transfers to real data.
- **Selection, not invention.** A fixed menu of 12 candidates tests selection, validation and adaptation, not the
  generation of new hypotheses.
- **Shared model family.** The designer and the researcher are the same model family, so the researcher might guess
  what a benchmark would plant. The brief stays identical across scenarios to limit this, and null and stable
  scenarios score false alarms.
- **Small sample.** 10 scenarios support only descriptive conclusions.
- **Planted effects may be too weak or too strong.** Calibration on separate seeds limits this but cannot remove it.

## 13. Compared with completing N1

| | Completing N1 | This sandbox |
|---|---|---|
| Relevance to the North Star | Instrument only: t0 against a specialist as local history shrinks. No discovery, adaptation or learning | The whole loop: discovery, decoy rejection, change recognition, use of evidence, economics. Also measures t0's covariate use by history length, with known truth |
| Scientific interpretability | Real data, no ground truth. The specialist is fixed at short history, the outcome map is not partitioned, and about 12 choices are still open | Every decision scored against the truth. AI vs script isolates the researcher; t0 vs ridge isolates the instrument. Synthetic only |
| Engineering effort | 4.5–5.5 days by its own count, plus items the review found missing, inside the engine next to B1 | About 3.5 days (about 5 full), in an isolated package that touches no engine code, ledger, B1 or Experiment 4 |
| Costs | About 11–16k t0 forecast-days; no API calls | About 55k t0 forecast-days; about 0.8–1.0M tokens |
| What success would establish | Exploratory evidence that t0's edge concentrates at short history, on one real series, confounded | In planted worlds, the AI with t0 finds drivers, rejects decoys and notices change better than a script on the same budget |
| What failure would establish | Hard to read, given the comparator's flaws | Located by the outcome map: the instrument (t0 cannot use the drivers), the researcher (no better than a script, or lured by decoys), or a world too easy to tell |

## 14. Decisions for the owner

1. **Approve the cut version** (about 3.5 engineer-days) or the full one (about 5).
2. **The day-1 stop rule:** INSTRUMENT FAILURE ends the work with a short report.
3. **The token budget for the scored run** (about 1M).
4. **Approval of F1** before the scored run.
