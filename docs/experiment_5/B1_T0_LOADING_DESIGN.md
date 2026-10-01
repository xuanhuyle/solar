# Batch B1: loading t0 by content in its future vault run (design only)

*Engineering design for the owner's approval. Nothing here is implemented. B1's frozen protocol, its frozen code
(commit `710b2b37`, tag `engine-freeze/B1`), its ledger entries and its sealed forward data are not touched, and no
data from 2026 on is read.*

## 1. The problem

**The failure.**
- B1 (ledger seq 56) is scored by the vault with the code of its freeze commit `710b2b37`; that rule is the owner's
  decision of 2026-09-27.
- That code loads t0-alpha by the revision id `9b02c5f4bb6c89ba15d9fa74554018fe6464220b`.
- That revision vanished from the Hugging Face Hub on 2026-09-29 (`docs/experiment_4/RETRIEVAL_EVENTS.md`).
- So B1's vault run, due after 2027-04-01, would fail at load time.

**The bytes are unchanged.** At the Hub head `fdd18964…` the two files are byte-identical to the frozen snapshot:

| File | sha256 |
|---|---|
| `config.json` | `b2b545685283c579b99c774da0d7f07525683efca2b27dc4ffec99c109d5beba` |
| `model.safetensors` | `16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f` |

Both are pinned in `solarbench/t0_pinned.py` (`PINNED_SHA256`).

**What a fix must do:** give the frozen code exactly those bytes without changing it.

## 2. What the frozen code does (read at `710b2b37`, identical at HEAD)

**The load path.**
- `engine/__main__.py:378` (`vault_open`) runs `arms._t0("loader", (), None).load()`.
- That goes to `engine/arms.py:121-124`, which builds `T0Forecaster(repo_id=cat.T0["repo_id"],
  revision=cat.T0["revision"])`.
- `solarbench/forecasters.py:434-443` then calls `T0Forecaster.from_pretrained(repo_id, revision=…, token=True)`,
  with no `cache_dir` and no `local_files_only`.

**The order is safe.** The model is loaded first: before the frozen-commit and gate-fingerprint check
(`_check_frozen_code`, line 381), before `vault.open_forward` (which refuses without a loaded model) and before the
`unseal` entry.
- A load failure therefore unseals nothing and consumes no window.
- The job fails, and the record job stops with "Nothing recorded".

**How the installed library resolves it.**
- The frozen constraints pin `tfc-t0==0.3.2` and `huggingface-hub==1.31.0`.
- `t0.T0Forecaster` uses `PyTorchModelHubMixin.from_pretrained` unchanged. It needs `config.json` and
  `model.safetensors`, and loads with `strict=False`, so hashing the bytes is the only content guarantee.

**The cache shortcut that makes the fix possible.** In huggingface_hub 1.31.0, `hf_hub_download` with a 40-hex
commit revision returns `<cache>/models--theforecastingcompany--t0-alpha/snapshots/<revision>/<file>` if that file
exists, without any request to the Hub (`file_download.py:1087-1101`).

**Two traps:**
- **The token is still required.** `token=True` builds headers before that shortcut, so a missing token raises
  `LocalTokenNotFoundError` even when the files are cached.
- **The local-directory trap.** If a directory `theforecastingcompany/t0-alpha` exists relative to the working
  directory (`frozen/`), the mixin loads from it with no revision and no hash check (`hub_mixin.py:501, 776`).

## 3. The design: one staging step in the vault job

**Where it goes.** One new step in `.github/workflows/engine.yml`, vault job, between "Run tests (the frozen
commit's)" and "Open the batch once".
- It is the dispatched branch's workflow and code, as every vault step before the frozen worktree is.
- It runs after the frozen install, so `huggingface_hub` 1.31.0 and `tfc-t0` are present.
- It runs after the frozen tests, so they are unaffected.

**What it does.** It runs from the workspace root (not `frozen/`), calling a small new function beside
`t0_pinned.fetch`, for example `t0_pinned.stage(repo_id, frozen_revision, cache_dir)`:
1. Refuses if `frozen/theforecastingcompany/t0-alpha` exists (the local-directory trap).
2. Fetches both files from the repository's current head into a temporary directory.
3. Verifies both sha256 against `PINNED_SHA256["9b02c5f4…"]`. Any mismatch or missing file stops the job.
4. Copies the two verified files, as regular files, into
   `$HF_HUB_CACHE/models--theforecastingcompany--t0-alpha/snapshots/9b02c5f4bb6c89ba15d9fa74554018fe6464220b/`.
   It refuses if that folder already holds different bytes.
5. Re-hashes the placed copies, and prints the retrieval record: the frozen revision, the head that served the
   bytes, both sha256 and the time.

**Environment.**
- **Staging step:** `HF_TOKEN` and `HF_HUB_CACHE: ${{ runner.temp }}/hf-hub`.
- **"Open the batch once":** the same `HF_HUB_CACHE`, `HF_HUB_OFFLINE: "1"`, and `HF_TOKEN` kept. Offline mode makes
  any request other than the cache hit fail closed, and stops the library's telemetry and agent-registry calls.
  `HF_HUB_CACHE` is read when the library is imported, so it must be set in both steps' environments.

**Retrieval record.**
- Written to the job summary and a notice.
- Also saved as a file uploaded in a separate artifact, after the pending-ledger upload. A static test requires the
  first upload to be the pending file.
- **Never** appended to `frozen/results/engine/pending.jsonl`: vault mode allows only `unseal`, `verdict`,
  `accepted_finding` and `error` entries (`engine/record.py:57`). A `note` there would make the record job refuse
  the whole vault record, including the unseal and verdict.
- Artifacts are kept 7 days, so the record must be committed to the repository promptly after the run, by a small
  copy workflow like `exp4-evidence-copy.yml`.

**Code changes, all in the dispatched branch:**
- the new step and two environment changes in `engine.yml`;
- `stage()` in `solarbench/t0_pinned.py`, with tests;
- static workflow-test pins:
  - step order;
  - the hashes come from `PINNED_SHA256`;
  - `HF_HUB_OFFLINE` and `HF_TOKEN` on the open step;
  - the same cache variable on both steps;
  - no `actions/cache`.

**Effort:** about 0.5–1 engineer-day.

## 4. Why this does not alter B1

- **Frozen code:** unchanged. The vault still checks out `710b2b37` and `_check_frozen_code` still passes.
- **Gate fingerprint:** unchanged. It hashes the fingerprinted files and `repo_id@revision` (`engine/gates.py:38-51`),
  and the frozen copies of both are untouched.
- **What the frozen code loads:** exactly the bytes it was frozen with. The pins come from the frozen revision's own
  cached snapshot.
- **Ledger and record job:** unchanged. Kinds and context fields still hash to the `ce2ed6e8…` B1 pinned, and no
  new entry kind is written.
- **Scientific protocol:** unchanged. Claims, window, comparator, test, margin and alpha are all untouched.

## 5. Failure modes

| Event | What happens |
|---|---|
| The Hub head's bytes change | Staging refuses; the job stops before the load; nothing is unsealed |
| The repository is removed, renamed or access is revoked | Staging fails; nothing is unsealed. Remedy: a durable copy (section 7) |
| The token is missing | Staging fails, and the frozen load would raise anyway before any unseal |
| Something needs the Hub during scoring | Nothing should: scoring reuses the model loaded before the unseal (`engine/vault_run.py:88`). Offline mode affects only the Hugging Face library, not the forward-data downloads. A failure after the unseal would still consume the window, as the vault's code always has, so the rehearsal (section 6) matters |
| The staging step is skipped by mistake | The frozen load asks the Hub for the vanished revision and fails before any unseal |

## 6. Proving it before April 2027: a load-only rehearsal

A separate, manually dispatched workflow with:
- no `engine-vault` environment, no ledger read or write, and no data read;
- `contents: read` permission and `HF_TOKEN` only.

What it does:
1. Checks out the `engine-freeze/B1` tag into a worktree.
2. Installs and tests the frozen code exactly as the vault job does.
3. Runs the same staging step.
4. In the worktree, with `HF_HUB_OFFLINE=1`, runs only the frozen loader (`arms._t0(...).load()`) and the frozen
   gate fingerprint, and asserts the fingerprint equals B1's recorded one.

Run it once after approval and again shortly before B1 opens.

## 7. Alternatives rejected

| Alternative | Why not |
|---|---|
| Change the revision in the frozen code, or score at a later commit | Breaks the freeze-commit rule (owner, 2026-09-27); the frozen check refuses another commit |
| Re-freeze B1 | Changes a frozen claim and spends alpha |
| A `theforecastingcompany/t0-alpha` directory inside `frozen/` | Loaded with no revision and no hash check: the trap of section 2 |
| Restore an Actions cache of the old snapshot | The engine reads no caches since the cache-poisoning finding of the third review round |

## 8. Decisions for the owner

1. **Approve this design** for implementation before 2027-04-01. The implementation and the rehearsal are a separate
   authorisation.
2. **A durable copy of the weights.** The Hub repository could change or disappear again before April 2027. Keeping
   a private copy of the two files elsewhere needs a check of the gated repository's licence terms. If it is
   allowed, the staging step can take the copy as a second source and verify it against the same hashes.
3. **Whether the same staging step should also serve future engine probes.** It would let current HEAD code load t0
   without editing fingerprinted files. The alternative is a content-verified loader at the probe call sites. This
   only matters if an Experiment 5 build is approved.
