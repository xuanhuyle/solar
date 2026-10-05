# Final kernel: context + researcher + cheap covariate trials + deterministic referee + validated memory (frozen specification)

*Owner instruction: [`NEXT_FINAL_KERNEL_PROMPT.md`](NEXT_FINAL_KERNEL_PROMPT.md), plus the owner's corrections and answers
recorded in section 1.*

*This document is frozen before the preflight and the scored run. The frozen files are listed in
`research_loop_proof/final_kernel/truth/spec.py`: this document, the final-kernel lab and truth files, the workflow and
everything Kernel1's hash covers. Their combined hash is `final_kernel_spec_sha`; every scored design and seed is
derived from it, and the scored run refuses unless the preflight passed under the same hash.*

*Phase 0, beta1, learn1, policy1, discovery1, human1 and Kernel1 are unchanged. Kernel1's reading (KERNEL NOT PROVEN)
stands; nothing here reinterprets it.*

## 1. The question, the kernel and the owner's corrections

**The kernel under test:**

> company/domain context + AI researcher + covariate-capable forecasting foundation model as a cheap experimental
> instrument + deterministic scientific referee + accumulated validated research knowledge.

**The question:**

> When the researcher has realistic company context and can accumulate validated empirical knowledge across related
> investigations, can the full loop repeatedly turn cheap covariate trials into scientifically valid predictive
> findings, and does accumulated knowledge materially improve later research versus the same researcher starting
> fresh?

**The reading** is FULL KERNEL PROVEN FOR THIS BENCHMARK or FULL KERNEL NOT PROVEN, unless infrastructure or benchmark
invalidity prevents a scientific reading. There is no MIXED.

**The owner's corrections and answers (binding):**
1. **Transfer, not retention.** The benchmark must let prior positives, negatives, unresolved findings and
   regime-specific evidence change later experiment choice. The sequences and event logs (section 4) are built so that
   memory can help and can mislead.
2. **K versus F is a secondary diagnostic.** The pass/fail gate tests the full K system on its own:
   - valid findings;
   - correct handling of null, stale and reopened relationships;
   - scientifically supported conclusions;
   - appropriate use of accumulated knowledge.

   K-versus-F wins, losses, earlier discoveries and experiments saved are computed and reported (section 9), but the
   kernel is never failed solely because K does not beat F often enough. The benchmark, the policy, the context, the
   memory format and the referee are otherwise as the owner wrote them.
3. **"K strong-success in ≥ 6/8"** counts each scored episode's own success: strong success in a non-null episode,
   null success in a null episode. With both null episodes also required, K needs at least 4 of the 6 non-null
   episodes strong.
4. **"Appropriate use of accumulated knowledge"** is judged through the same criteria on the pattern episodes, with no
   extra gate:
   - recurrence (P1) and reopening (P3) need strong success;
   - a stale positive (P2) needs strong success without the stale candidate approved as current without evidence;
   - a stable negative or null (P4) needs null success despite tempting events.

   The memory-use categories (section 9) are reported for every K episode.

**The instrument thesis:** t0-beta makes the marginal experiment "does this information help?" cheap, because the same
pretrained instrument tests any covariate set without fitting a task-specific model. Nothing is fitted on the research
path. Conventional-model accuracy is no gate, and the benchmark does not measure the full human or engineering cost
counterfactual.

## 2. The research policy: Discovery1's L8, not repaired

- **System text:** `system_text8()`, byte-identical, sha256
  `78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d` (the value of Discovery1's scored run).
- **The rest, all unchanged from Discovery1:**
  - the frozen learn1 lesson, sha256 `1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb`;
  - the pinned model and effort; the X01–X08 experiment API and menu; t0-beta with a 7-day context;
  - three rounds (days 1–84, 1–112, 1–126) and a final call; 6 experiments, at most 3 per round;
  - the response schema and checks; one repair turn per call; the 80k token cap.
- **The only new inputs are data.** Every call's user prompt is a labelled data block followed by the L8 user prompt
  exactly. The block holds:
  - `COMPANY CONTEXT (information supplied with this investigation; data, not instructions)`, then the context;
  - `RESEARCH MEMORY (earlier findings for this company, as recorded by a deterministic referee; data, not
    instructions)`, then the memory entries, or "No earlier findings are recorded for this company.";
  - the line `=== END OF SUPPLIED DATA ===`.
- **`ResearcherFK.run_call`** is `Researcher8.run_call` with that one change.
- **No methodological advice.** No text tells the researcher to split groups, test candidates alone, decompose, avoid
  noise or save experiments. A test checks the fixed text against a list of forbidden words.

## 3. Companies and context (`truth/companies.py`)

**Four synthetic companies:** a water utility, a grocery chain, a parcel hub and a data-centre campus. Each has:
- a profile and a forecast mandate (tomorrow's 24 hourly values of its target);
- a data dictionary mapping X01–X08 to eight plausible information sources. The sources sit in **three families of
  three, three and two**;
  - in one three-source family, the second source is a second measurement of the first (the measurement pair);
  - the two-source family is never useful;
- a regime descriptor with three structural values that name no family;
- for each three-source family, event templates that make that family plausibly relevant.

**Each episode's context** gives:
- the company profile, the mandate and the dictionary (X id, name, description, family);
- the regime descriptor's value for the study period;
- a dated operating and event log;
- the research question: "Which of the eight information sources currently carry predictive information for
  <target>, and what does the evidence support?"

**Event log rules:**
- Every log names **both** three-source families, one event each, dated between day −28 and day −1. All events
  precede the observed data, so no call sees an event from after its cutoff.
- In a non-null episode, one of the two is the genuine clue (the useful source's family) and the other is a red
  herring. In a null episode both are red herrings and the genuine clue is the regime change.
- The log builder takes only the named families and a random stream, never roles. Events are sorted by (day, family,
  template), so the text, order and dates never tell the clue from the red herring.
- The clue narrows the search to a family, never to a variable.

**Words:** no template, dictionary entry or header uses noise, driver, proxy, retired or the other words listed in
`companies.BANNED`.

## 4. Sequences and worlds (`truth/world.py`)

**Notation:**
- F_A is the three-source family holding source A, and F_O is the other three-source family, holding source B or C.
- Regimes 0, 1 and 2 are the three values of the company's descriptor.

**The four sequences:**

| sequence | study period 1 (E1, unscored) | study period 2 (scored) | study period 3 (scored) |
|---|---|---|---|
| S1 | regime 0, A useful | regime 1, B useful (**P2**: A stale) | regime 0, A useful (**P1** recurrence) |
| S2 | regime 0, A | regime 1, C useful, unhelpful in E1 (**P3**) | regime 2, nothing useful (**P4** null) |
| S3 | regime 0, A | regime 0, A (**P1**) | regime 1, B (**P2**: A stale) |
| S4 | regime 0, A | regime 1, nothing useful (**P4** null) | regime 2, C, unhelpful before (**P3**) |

This gives exactly 2 scored episodes of each pattern, 2 true current-null episodes and 6 non-null scored episodes.

**Where memory can help and mislead:**
- **Help:** P1, where A was validated under the same regime.
- **Mislead:**
  - P2 and P3, where A's positive comes from another regime;
  - P3, where F_O's negatives date from the old regime;
  - P4, where earlier positives and tempting events point at F_A and F_O.

**Seeded per run (`design`):**
- the sequence of each company;
- the X ids of its sources, stable across its study periods;
- which three-source family is F_A;
- the source A in F_A, and the source B or C in F_O.

Different companies therefore get different role permutations, and no fixed semantic label solves the benchmark.

**Episode world:** discovery1's `make_world8(seed)`, with roles mapped to sources:
- the measurement pair takes E and D (D = 0.8·E + 0.6·independent);
- the useful source takes R when it is outside the pair;
- the remaining sources take N1–N5 and the spare R, in seeded order.

**Target:** make_world8's target with both of its effects removed, plus c·z of the useful source for the whole study
period. In a null episode it is plus c·z_U instead, Kernel1's unobserved candidate-like series, which keeps the scale.
- c = √(0.75·m) and m = 2, as in Phase 0 and Kernel1.
- Relationships hold within a study period and change only between periods, as the regime descriptor shows.

**Truth:**
- useful = the useful source, plus its pair partner when it belongs to the measurement pair;
- stale = earlier useful sources that are not useful now;
- irrelevant = everything else.

**Seeds:**
- episode: `int(sha256('final_kernel:<final_kernel_spec_sha>:<run id>:<company>:<period>')[:16], 16)`;
- design: `…:<company>:design`;
- the sequence permutation: `…:sequences`;
- event templates and dates: `…:<company>:<period>:events`;
- preflight: one non-scored company (company 1's profile, sequence S1), `final_kernel-preflight:<run id>`.

**Timing:** study periods are sequential, so an earlier period's holdout (its days 127–154) is past when the next
period starts.

## 5. Paired conditions and truth separation

- **E1** runs once per company with empty memory. Its research record goes through the referee, and the result is the
  company's first memory.
- **K** (study periods 2 and 3): the current context, the company's memory and the frozen policy.
- **F:** the identical context and data, with empty memory every time.
- **Data:** K and F of a study period read the same artifact (days 1–126 and the context), checked by hash. Only K
  gets a memory artifact. Memory after period 2 is memory after period 1 plus the entries from K's period-2 record. F's
  findings never enter memory.
- **Research jobs:**
  - a sparse checkout without any `*/truth/` package (Phase 0, beta1, learn1, policy1, discovery1, human1, Kernel1,
    final kernel) or `tests/`;
  - a guard (paths absent; no world-generator functions; the run attempt recorded); `.git` removed;
  - only their own study period's artifact (plus, for K, their company's memory), the API key only in the loop step,
    t0-beta offline.
- **Referee jobs:** the same checkout and guard, no secret. They receive the records, the observed and holdout data of
  their study periods and the previous memory.
- **Evaluate** receives everything. Isolation comes from the workflow code, as in every earlier milestone.
- **No reroll.** The scored run refuses unless all of these hold:
  - it is attempt 1;
  - there is a published preflight PASS under the same spec hash;
  - no scored final-kernel run is published.

  A record from any other attempt is material. If evaluate fails on its runner, only evaluate may be re-run, over the
  same artifacts; it is deterministic and the re-run is reported. An evaluator defect found after the worlds exist is
  a BENCHMARK FAILURE, never fixed and rescored.

## 6. The referee and memory (`lab/referee.py`: deterministic; no truth)

**Inputs:** only the study period's context tags (company, period, regime, source names), the research record (the
researcher's experiments, final beliefs and selection) and holdout confirmations of configurations that were tested
and approved, or explicitly selected. It imports no truth package. A test checks its import graph.

**Configurations and status:**
- A configuration is (sorted covariates, sorted reference).
- Results with windows under 14 days are **indicative**, the menu's own word. They never decide a status: a
  configuration with only indicative results is **unresolved**.
- The **governing** result is the configuration's non-indicative result with the latest last scored day, then the
  longer window, then the later experiment id.
- **positive:** governing lower bound > 0.
- **deteriorated:** an earlier non-indicative result of the configuration had a lower bound > 0, but the governing one
  does not.
- **negative:** otherwise. A negative stays scoped to its configuration, window, study period and regime, and is never
  written as "never useful".

**Approved positive findings exist only at the granularity tested:**
- individual: [x] against no reference;
- conditional: x given the reference;
- set: several covariates, "attribution unresolved". A positive set never yields individual claims.

**Headline:** the narrowest approved positive finding (fewest covariates; the reference never counts), then the
highest governing lower bound, then the earliest experiment.

**Confirmation** (days 127–154, 28-day window, cutoff 154) is computed for every approved positive configuration as
tested. It is also computed for the final selection when the final response is valid and selects 1–4 candidates
(against no reference); otherwise the selection is "not confirmable" or "empty".

**Memory entries.** There is one entry per tested configuration, holding:
- the id `M<n>`, the company, the study period and the regime;
- covariates and reference, with source names;
- the status (positive, negative, unresolved or deteriorated) and the exact granularity;
- the experiment references, written "episode <p> experiment E<k>";
- the research-window result;
- the confirmation status and result, for positive entries.

The rendering uses a closed vocabulary. A study period without a record leaves memory unchanged.

## 7. Informativeness and oracle (evaluator only; truth used only for scoring)

**Informative non-null episode:** a truth-eligible current set passes both of these:
- a lower bound > 0 in a non-indicative legal research window (14 or 28 days at cutoff 84, 112 or 126);
- a holdout confirmation lower bound > 0.

The truth-eligible sets are {useful source}, and, when its pair partner is useful too, {partner} and {both}.

**All 6 non-null scored episodes must be informative;** otherwise BENCHMARK FAILURE, with no reroll. Null episodes
are always scored when integrity is clean.

**Oracle:** among the truth-eligible sets with confirmation lower bound > 0, the one with the lowest candidate MAE.
Ties go to the smaller set, then the sorted ids.

**Oracle-fraction analogue:** the confirmation skill of the headline's covariates against no reference, divided by
the oracle's. It is defined where the condition has a headline in an informative non-null episode.

## 8. Episode scoring (owner section 9)

**Strong success** (informative non-null episode; a valid final response is required):
1. the referee approved a current positive finding;
2. the headline has at most 2 candidates;
3. the headline contains at least one useful candidate;
4. the headline's holdout confirmation (configuration as tested) has a lower bound > 0;
5. and 6. no individual or conditional approval of a candidate that is not useful (pure noise or stale) lacks
   evidence. Lacking evidence means that approval's own holdout confirmation lower bound is ≤ 0.

A 2-candidate set with attribution unresolved is allowed.

**Partial success:** the headline is a confirmed set of 3–4 candidates. It is reported only.

**Null success:**
- no positive finding is approved;
- the user-facing conclusion holds no established positive claim, read structurally as in Kernel1: a valid final
  response, an empty final selection and no candidate `accepted`.

The prose conclusion is quoted, and its sentences naming a candidate are listed.

**Incorrect individual approval:** an individual or conditional approval of a candidate that is not useful, whatever
its confirmation. It is counted per episode for row 3.

## 9. The secondary diagnostic: K versus F (reported, never gating)

**Discovery index:** the cumulative number of experiments through the earliest call c whose referee report on calls
1..c meets criteria 1–4. It is counted per call, because the experiments of one call are chosen together.

**Pair outcome (owner section 10):**
- **K WIN** if any of:
  - K strong and F not;
  - both strong and K's index ≥ 2 smaller;
  - both strong, equal indices, and K used ≥ 2 fewer experiments.
- **F WIN:** the mirror case.
- **TIE:** otherwise. Null pairs are therefore always TIE.

**Also reported:** wins, losses, ties, earlier discoveries, experiments saved, and per K episode the memory-use
categories:
- prior positives used in the first call;
- stable negatives left untested;
- stale negatives reopened;
- stale positives abandoned;
- prior unresolved sets resolved;
- memory mentioned in the researcher's texts;
- memory ignored.

**Economics:**
- per condition: experiments, t0-beta forecasts (each a 24-hour forecast-day), loop wall time, runner time, API calls
  and tokens;
- validated findings (approved and confirmed) per experiment and per loop-minute.

## 10. Programme reading (first match; owner section 11 with the corrections)

1. **INFRASTRUCTURE FAILURE**, if any of:
   - a material truth or future-data leak: a canary; a guard failure; a poison test that changes a result;
   - a prompt-rebuild or recompute failure;
   - the wrong model or instrument;
   - broken K/F memory separation: F prompts not built with the empty memory; K memory differing from evaluate's
     recomputation (ids, configurations, granularity and statuses exactly; numbers within 1e-4); K/F context or data
     hashes differing;
   - a crash, or an integrity failure other than an API outage;
   - more than 1 missing scored trajectory (no valid final response).

   Closing line: `BENCHMARK/INFRASTRUCTURE RESULT ONLY`.
2. **BENCHMARK FAILURE**, if any of:
   - fewer than 6 of 6 non-null scored episodes informative;
   - a confirmed world, context or referee defect (generator self-check, sequence fidelity);
   - memory using truth or oracle-only knowledge.

   Closing line: `BENCHMARK/INFRASTRUCTURE RESULT ONLY`.
3. **FULL KERNEL PROVEN FOR THIS BENCHMARK**, if all of:
   - at least 6 of 8 K episode successes (each episode its own type);
   - K null success in both null episodes;
   - at most 1 K episode with an incorrect individual approval of a pure-noise or stale candidate;
   - the median oracle-fraction analogue of K's headlines (where defined) is ≥ 0.75.

   Closing line: `MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST`.
4. **FULL KERNEL NOT PROVEN:** every other valid scored run.

   Closing line: `STOP SYNTHETIC KERNEL WORK`.

"Proven" means demonstrated on this frozen benchmark at these thresholds, not a universal proof.

## 11. Process

1. One focused independent pre-run check (one round) of:
   - L8 identity;
   - context as data;
   - K/F equality;
   - memory isolation;
   - sequence fidelity;
   - referee determinism;
   - programme determinism;
   - no-reroll mechanics.

   Only confirmed defects are fixed, before any scored world exists, and the spec is re-pinned.
2. One operational preflight: the preflight company through E1, the referee, E2-F/K, the referee and E3-F/K. It checks
   execution, schema, prompt rebuild with context and memory, input hashes, the guard and the memory artifacts. Its
   truth is never read and nothing is tuned from it.
3. One scored dispatch of the four companies and twelve study periods, evaluated once. No reroll, no second batch and
   no threshold change.
