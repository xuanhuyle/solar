# beta1: results and dispatch log

*Owner instruction: [`NEXT_MILESTONE_PROMPT.md`](NEXT_MILESTONE_PROMPT.md). Frozen spec:
[`BETA1_SPEC.md`](BETA1_SPEC.md). Every dispatch of `.github/workflows/research-loop-beta1.yml` is listed here. The
published records are on branches `beta1/run-<id>` (manifest-checked). Phase 0's results and verdict are unchanged.*

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37199765266](https://github.com/xuanhuyle/solar/actions/runs/37199765266) | qualify | `44a6455` | **PASS** |
| 2 | [37200762398](https://github.com/xuanhuyle/solar/actions/runs/37200762398) | preflight | `9e5f6a9` | **FAIL**: call 1 refused twice, `reasoning_extraction` |
| 3 | [37200991688](https://github.com/xuanhuyle/solar/actions/runs/37200991688) | preflight | `0888695` | **PASS**: 4 of 4 calls valid, 0 refusals, 0 repairs |
| 4 | [37201189113](https://github.com/xuanhuyle/solar/actions/runs/37201189113) | run (scored) | `0888695` | **RESEARCHER FEASIBILITY FAILED** (infrastructure clean) |

## 1. t0-beta qualification (run 37199765266): PASS

**Model:**
- **Source:** `theforecastingcompany/t0-beta` (ungated), revision `c8885416fab935d604749a90cdcbf9b54fffcaeb`,
  retrieved from huggingface.co on 2026-10-04.
- **Runtime:** `tfc-t0` 0.5.0. Releases before 0.5.0 would silently apply t0-alpha's normalization.
- **sha256:**
  - `config.json`: `bd0ef3c2b1c1a130e32a6ce6132d895297d3a42e1fa84ac2d516e794c5c881ff`
  - `model.safetensors`: `a0fd8abd51275dd30afd21f4892c763ebd45e2cb1811eff26eed43f89a543f7d`

Both are pinned in `beta1/lab/t0_beta.py`.

**Smoke checks** (Phase-A linear worlds 0–7, 7-day context; 274 forecasts in 24 s):
- **Q1, reproducible:** pass. A second load gave bit-identical forecasts.
- **Q2, covariates accepted:** pass, with 1 and with 2 covariate rows.
- **Q3, finite and non-degenerate:** pass. Nothing was sanitised, and the minimum hourly sd was 0.12.
- **Q4, emerging covariate:** pass. At days 7–13, {E} beat {} by +34.2% and {N} by +36.4%, and E won in 8 of 8
  worlds. Reported only: at days 1–3, {E} vs {} was +15.7%, and {N} vs {} was +0.7%.

Alpha did not have to be retained.

## 2. Researcher preflight

**Preflight 1 (run 37200762398): FAIL** (operational check only; the world is not scored).
- **Call 1:** both attempts refused, category `reasoning_extraction`, 0 output, about 1–2 s each. The API's
  explanation: "This request was blocked as it seems to violate Anthropic's Terms of Service restrictions on reverse
  engineering or duplicating model outputs."
- **Calls 2–4:** valid.
- **Experiments:** 6 requested, all legal.
- **Tokens:** 22,344.
- **Minimal cause:** the brief asked for "notes: your reasoning so far, briefly." in the response text. The
  `reasoning_extraction` category is a request to reproduce internal reasoning.
- **Minimal correction:** only that line became "notes: a brief research log: what you have tested and concluded so
  far." The preflight is then repeated once (new `beta1_spec_sha`).

**Preflight 2 (run 37200991688): PASS.**
- 4 of 4 calls valid on the first attempt; 0 refusals; 0 repairs.
- 6 legal experiments.
- 23,218 tokens.

## 3. The scored hidden world (run 37201189113)

**Setup:** `beta1_spec_sha` `9b6ea2ae…`; t0-beta at the pinned revision. Integrity: no issue. The observed hash
matched, the prompts rebuilt, all 6 experiments recomputed with t0-beta, no canary was found, the model hash matched,
and the guard passed. Infrastructure: 4 API attempts, 0 refusals, 0 repairs.

**Revealed truth (after the run):**
- first changed day 88;
- R (retired driver) = X03;
- E (emerging driver) = X02;
- D (proxy of E) = X01;
- N (noise) = X04;
- all observed signs +1.

**Evidence check (t0-beta, 28 days, against no covariate):**
- R on days 57–84: +17.8% [+9.8, +26.6];
- E on days 99–126: +42.1% [+32.1, +50.8].

Both were present.

**Trajectory.** Every prompt, response, belief table and result is in `notebook.jsonl` and `ai.json` on the branch.

| Round (days seen) | Beliefs going in | Experiments (each against no covariate) and results | Belief update |
|---|---|---|---|
| 1 (1–84) | all untested; plan: screen one at a time on 28 days, recheck later because "the process may be non-stationary" | E1 X01 (D), days 57–84: −3.9% [−12.4, +5.5]; E2 X02 (E): −5.5% [−13.9, +3.2]; E3 X03 (R): +17.8% [+9.8, +26.6] | X01, X02 rejected; X03 promising, flagged "weekly trend is declining (+31.8% down to +10.0%)" |
| 2 (1–112) | as above, X04 untested | E4 X04 (N), days 85–112: −0.1% [−7.4, +6.4]; E5 X03 recheck on new days 85–112: +2.8% [−4.8, +10.7] | X04 rejected; X03 deteriorated ("declines steadily … about zero in the latest two weeks") |
| 3 (1–126) | X01, X02 noted as "last tested on days 57–84; their effect may have changed since, but the remaining budget cannot cover them" | E6 X03 again, days 113–126: −1.4% [−6.6, +3.4] | X03 stays deteriorated |
| final | | none | selection: none; X03 deteriorated; X01, X02, X04 rejected. Its own caveat: X01 and X02 tested only before day 84 |

**Behaviours.**

| Behaviour | Result |
|---|---|
| B1 hypothesis | yes |
| B2 test | yes |
| B3 interpretation | yes (0 errors) |
| B4 negative result kept | yes |
| B5 weakening noticed | yes |
| B6 another candidate investigated | yes |
| B7 new covariate identified | **no** |
| B8 beliefs revised | yes |
| B9 separation or conditional test | no |
| B10 no unsupported noise | yes |

**Verdict map row 2:** E was detectable on days 99–126, yet never in an experiment's covariates in rounds 2–3, and not
selected.

**Confirmation (days 127–154).**

| Set or comparison | t0-beta | ridge |
|---|---|---|
| {E} vs {} | +41.3% [+32.3, +50.1] | +44.3% [+31.2, +53.0] |
| {D} vs {} | +13.0% [−0.6, +28.8] | +10.0% [−9.0, +31.3] |
| {R} vs {} | +0.6% [−7.6, +10.0] | −1.3% |
| {N} vs {} | +2.3% [−6.1, +11.7] | −1.2% |
| {E, D} vs {} | +44.8% [+34.5, +54.6] | +42.7% |
| D given E | +5.9% [−0.3, +13.0] | −2.8% |
| E given D | +36.5% [+21.9, +47.3] | +36.4% |
| R given E | +1.4% | +1.6% |
| N given E | +0.7% | +1.8% |
| AI selection (empty) | 0 by definition (no covariates) | |
| script selection {D, E} | +44.8% | +42.7% |

**Per candidate: causal role, predictive use, researcher.**
- **E (X02):** causal from the change; the most useful candidate (+41.3%), and largely not redundant with D (E given
  D +36.5%). The researcher rejected it on pre-change evidence and never re-tested it.
- **D (X01):** a non-causal proxy; weakly useful alone (+13.0%, interval includes zero) and nearly redundant given E.
  Rejected by the researcher on pre-change evidence.
- **R (X03):** causal before the change only; useless after it (+0.6%). Correctly marked deteriorated and excluded.
- **N (X04):** noise (+2.3%, interval includes zero). Correctly rejected.

**The frozen script.** Round 1 tested X01 and X02 (−3.9%, −5.5%); round 2 tested X03 and X04 on days 99–112 (−0.3%,
+0.6%); round 3 re-tested X01 (+20.6%) and X02 (+45.2%) on days 113–126. It selected {X01, X02} = {D, E}. It found E
because its fixed schedule happens to re-test X01 and X02 last. One world shows no superiority either way.

**Cost (whole milestone).**
- **t0-beta forecasts:** 1,576 in all:
  - qualification 274;
  - preflight 1: 196;
  - preflight 2: 238;
  - scored run 868 (script 168, AI 224, evaluate 476).
- **Runner time:** about 11 minutes of job time (qualify 1 min, preflights 2.6 and 3.1 min, scored run 3.7 min).
- **Researcher API:** 13 attempts (preflight 1: 5; preflight 2: 4; scored run: 4); 2 refusals, both in preflight 1;
  1 repair; 66,785 tokens (22,344 + 23,218 + 21,223).
- **Engineering:** about 1.5 hours of agent session time, from the prompt to the result; about 2,000 new lines
  including tests and the workflow.

**What this run does and does not show.**
- It is one world: an existence check, not a rate.
- The research loop ran end to end without a service failure. It produced a coherent hypothesis → test → evidence →
  revision chain for the retired driver: detected (+17.8%), re-tested twice on fresh windows, downgraded to
  "deteriorated" and excluded.
- It did not complete the discovery half. After detecting the change, it spent its remaining budget confirming R's
  decline instead of re-screening candidates it had rejected before the change. It named that gap itself and missed
  a strongly detectable new driver.

