# beta1: results and dispatch log

*Owner instruction: [`NEXT_MILESTONE_PROMPT.md`](NEXT_MILESTONE_PROMPT.md). Frozen spec:
[`BETA1_SPEC.md`](BETA1_SPEC.md). Every dispatch of `.github/workflows/research-loop-beta1.yml` is listed here. The
published records are on branches `beta1/run-<id>` (manifest-checked). Phase 0's results and verdict are unchanged.*

## Dispatch log

| # | Run | Mode | Commit | Outcome |
|---|---|---|---|---|
| 1 | [37199765266](https://github.com/xuanhuyle/solar/actions/runs/37199765266) | qualify | `44a6455` | **PASS** |
| 2 | [37200762398](https://github.com/xuanhuyle/solar/actions/runs/37200762398) | preflight | `9e5f6a9` | **FAIL**: call 1 refused twice, `reasoning_extraction` |

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
