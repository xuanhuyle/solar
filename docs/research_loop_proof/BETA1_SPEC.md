# beta1: one hidden-world research run with t0-beta, frozen specification

*Owner instruction: [`NEXT_MILESTONE_PROMPT.md`](NEXT_MILESTONE_PROMPT.md). Frozen before the preflight and the
scored run. The frozen files are listed in `research_loop_proof/beta1/truth/spec.py`, and their combined hash is
`beta1_spec_sha`. The scored world's seed is derived from that hash, and the scored run refuses unless the preflight
passed under the same hash. Phase 0 (its spec, results and verdict) is unchanged; beta1 reuses Phase 0 code by import.*

## 1. Foundation model

- **Model:** `theforecastingcompany/t0-beta`, run with `tfc-t0==0.5.0`. That release is the first that reads beta's
  normalization; older ones silently apply t0-alpha's.
- **Pinned bytes:** revision `c8885416fab935d604749a90cdcbf9b54fffcaeb`, with the sha256 of `config.json` and
  `model.safetensors` pinned in `beta1/lab/t0_beta.py`. Every load verifies them.
- **Qualification:** run 37199765266, PASS, on branch `beta1/run-37199765266`.
- **Call:** zero-shot, 7-day context, horizon 24, median of quantile levels 0.1 / 0.5 / 0.9.

## 2. The world (unchanged from Phase B)

The generator is the frozen Phase 0 generator, with Phase 0's `world.json` "phase_b" parameters: linear form, m = 2,
154 days.

**Candidates:** four anonymous candidates, X01–X04, a seeded permutation of:
- **R**, which drives the target until the change and then stops;
- **E**, which drives it from the change on;
- **D**, a correlated proxy of E (`0.8·E + 0.6·independent`), with no causal effect;
- **N**, noise.

Each candidate is observed with a seeded random sign.

**Change point:** the first changed day is τ = 86 + U{0..6}.

**Days:**
- days 1–126 are observed by the research job;
- days 127–154 are for confirmation and exist only in the evaluate job.

**Seeds:**
- scored world: `int(sha256('beta1:<beta1_spec_sha>:<run id>')[:16], 16)`, which does not exist before the dispatch;
- preflight world: `int(sha256('beta1-preflight:<run id>')[:16], 16)`.

## 3. Research setup (unchanged from Phase B except one rule)

- **Menu and budget:** Phase 0's `lab/menu.json`:
  - 3 rounds, seeing days 1–84, 1–112 and 1–126, then a final call;
  - 6 experiments in all, at most 3 per round;
  - 1–4 covariates, a reference of 0–2 ids, windows of 7, 14 or 28 days;
  - results with intervals from `min(2, window // 7)`-day blocks;
  - the same researcher model, pinned by hash, effort `high`, and an 80k token cap.
- **Brief:** `beta1/lab/brief.md`, which is Phase 0's brief plus one general rule, worded as the owner gave it:
  "Evidence about a multi-variable set applies to the set. It does not by itself establish that every member is
  useful. Claims about individual candidates require evidence that distinguishes them."
- **Researcher:** Phase 0's researcher (prompts, checks, one repair per call). In addition, every API attempt records:
  - the stop reason;
  - `stop_details` (type, category, explanation);
  - the request id;
  - the requested and served model's sha256 and whether they match;
  - usage;
  - elapsed time;
  - the repair and retry numbers.
- **Scripted strategy:** Phase 0's frozen script, descriptive only. Round 1 tests X01 and X02 on 28 days; round 2
  tests X03 and X04 on 14 days; round 3 tests X01 and X02 on 14 days. It then selects every candidate whose latest
  single-candidate lower bound is above 0.
- **Separation:**
  - the research job's checkout has neither world-generator package, and `.git` is removed;
  - the job receives only days 1–126, hashed;
  - the evaluator rebuilds every prompt, recomputes every experiment from the observed data, and scans for the
    canary.

## 4. Preflight (non-scored)

The preflight runs on the preflight world with the scored run's model, effort, schema, brief, interface and notebook.
It passes when:
- all 4 calls end with a valid response;
- every requested experiment is legal and ran;
- there is no integrity failure;
- at most 1 attempt in total is a refusal.

It is never scored against the world's roles. If refusals occur, the category is read, only the minimal prompt or
interface correction is made, and the preflight is repeated once. A second failure ends the milestone with RESEARCH
INFRASTRUCTURE FAILURE.

## 5. Evaluation and verdict

**Confirmation** (days 127–154, t0-beta and ridge):
- {E}, {R}, {D}, {N} and {E, D}, each against no covariate;
- R, D and N each given E ({E, x} against {E});
- E given D;
- the AI's final set and the script's final set, against no covariate.

**Evidence check:** t0-beta {R} on days 57–84 and {E} on days 99–126, each against no covariate.

**Behaviours** B1–B8 are Phase 0's definitions (PHASE0_SPEC.md section 4), plus two more:
- **B9 (separation or conditional test):** a later experiment tests a strict subset of an earlier multi-candidate set,
  or some experiment uses a non-empty reference;
- **B10 (no unsupported noise):** N is not selected, or its latest single-candidate lower bound is above 0.

**Verdict map** (the first match wins):

| # | Outcome | Condition |
|---|---|---|
| 1 | RESEARCH INFRASTRUCTURE FAILURE | any of: an integrity issue (observed hash, prompt rebuild, recompute, canary, model hash, guard, a failed research job); any of the 4 calls without a valid response after its repair (refusal, API error, malformed) |
| 2 | RESEARCHER FEASIBILITY FAILED | any of: R in the final selection; N selected while its latest single-candidate lower bound is ≤ 0, or N never tested alone; 2 or more interpretation errors; E detectable in the evidence check yet never in an experiment's covariates in rounds 2–3 and not selected |
| 3 | BASIC AUTONOMOUS LOOP OBSERVED | all of: E selected; R and N not selected; B3, B5, B7 and B8; t0-beta with the final selection beats t0-beta without covariates on the confirmation days (lower bound above 0) |
| 4 | AMBIGUOUS | anything else, including D selected without E |

**Always reported:**
- one world is an existence check, not a rate, and supports no claim of superiority over the script;
- whether R's and E's evidence was present in this world.

**Separately reported for each candidate:**
- its planted causal role;
- its standalone usefulness;
- its incremental value given the true driver;
- the researcher's final belief and selection;
- the script's selection.

**No reroll.** One scored world. A rerun is the owner's decision.
