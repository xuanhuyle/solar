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
exists, without requesting the file (`file_download.py:1087-1101`).
- When the library is online it still sends one request while building headers, before the shortcut (a GET of the
  Hub's agent registry; `file_download.py:1005`, `utils/_headers.py:183-189`). Offline mode removes it.
- The shortcut checks only that the file exists, not its content (`file_download.py:1088-1101`). The only content
  guarantee is the staging step's hash check (section 3).
- Only the snapshot folder is needed: no `refs/`, `blobs/` or lock entries, and loading writes nothing to the cache.
- The loader requests exactly `config.json` and `model.safetensors`. It falls back to an unhashed `pytorch_model.bin`
  only if `model.safetensors` is missing (`hub_mixin.py:778-802`), which staging rules out.

**Two traps:**
- **The token is still required.** `token=True` builds headers before that shortcut, so a missing token raises
  `LocalTokenNotFoundError` even when the files are cached.
- **The local-directory trap.** If a directory `theforecastingcompany/t0-alpha` exists relative to the working
  directory (`frozen/`), the mixin loads from it, ignoring the frozen call's revision and token
  (`hub_mixin.py:501, 776`). It also follows symlinks.

## 3. The design: one staging step in the vault job

**Where it goes.** One new step in `.github/workflows/engine.yml`, vault job, between "Run tests (the frozen
commit's)" and "Open the batch once".
- It is the dispatched branch's workflow and code, as every vault step before the frozen worktree is.
- It runs after the frozen install, so `huggingface_hub` 1.31.0 and `tfc-t0` are present.
- It runs after the frozen tests, so they are unaffected.

**What it does.** It runs from the workspace root (not `frozen/`), calling a small new function beside
`t0_pinned.fetch`, for example `t0_pinned.stage(repo_id, frozen_revision, cache_dir)`:
1. Refuses if `frozen/theforecastingcompany/t0-alpha` exists (the local-directory trap).
2. Fetches both files from the repository's current head into an explicit temporary directory (its own `cache_dir`
   or `local_dir`). `t0_pinned.fetch()` as it stands downloads into the default cache, which in this step is
   `HF_HUB_CACHE` itself; that is harmless for a load by commit hash, but `stage()` should not reuse it unchanged.
3. Verifies both sha256 against `PINNED_SHA256["9b02c5f4…"]`. Any mismatch or missing file stops the job.
4. Copies the two verified files, as regular files, into
   `$HF_HUB_CACHE/models--theforecastingcompany--t0-alpha/snapshots/9b02c5f4bb6c89ba15d9fa74554018fe6464220b/`.
   It refuses if that folder already exists with other content, so the folder holds exactly the two files.
5. Re-hashes the placed copies, checks that `huggingface_hub.try_to_load_from_cache` resolves both to them, and
   prints the retrieval record: the frozen revision, the head that served the bytes, both sha256 and the time.

**Where `stage()`'s inputs come from.** `repo_id` and the revision are read from the batch's freeze entry
(`payload.t0`; for B1, ledger seq 56). Only B1 is frozen today, and the catalogue at HEAD still names the same
revision. A later batch frozen at a revision with no entry in `PINNED_SHA256` would be refused by `stage()` before
any load, so its vault run would stop before the unseal (fail closed). The step and the open step's offline flag apply
to every vault dispatch.

**Environment.**
- **Staging step:** `HF_TOKEN` and `HF_HUB_CACHE: ${{ runner.temp }}/hf-hub`.
- **"Open the batch once":** the same `HF_HUB_CACHE`, `HF_HUB_OFFLINE: "1"`, and `HF_TOKEN` kept. Offline mode makes
  any request other than the cache hit fail closed, and stops the library's telemetry and agent-registry calls.
  `HF_HUB_CACHE` is read when the library is imported, so it must be set in both steps' environments.

**Retrieval record.**
- Written to the job summary and a notice.
- Also saved as a file uploaded in a separate artifact (with `if: always()`, so it survives a failed open step),
  after the pending-ledger upload. A static test requires the first upload to be the pending file.
- **Never** appended to `frozen/results/engine/pending.jsonl`: vault mode allows only `unseal`, `verdict`,
  `accepted_finding` and `error` entries (`engine/record.py:57`). A `note` there would make the record job refuse
  the whole vault record, including the unseal and verdict.
- The engine's artifacts are kept 7 days (`retention-days: 7` in `engine.yml`). That is a per-step setting, so the
  new upload can keep its file longer. The record should still be committed to the repository after the run, by a
  small copy workflow like `exp4-evidence-copy.yml` (a one-off with a hard-coded run and artifact id). The job summary
  and notice last as long as the run's logs.

**Code changes, all in the dispatched branch:**
- the new step and two environment changes in `engine.yml`;
- `stage()` in `solarbench/t0_pinned.py`, with tests;
- static workflow-test pins:
  - step order;
  - the hashes come from `PINNED_SHA256`;
  - `HF_HUB_OFFLINE` and `HF_TOKEN` on the open step;
  - the same cache variable on both steps;
  - no `actions/cache`;
  - the literal sha256 values pinned for revision `9b02c5f4`.

**Effort:** about 0.5–1 engineer-day.

## 4. Why this does not alter B1

- **Frozen code:** unchanged. The vault still checks out `710b2b37` and `_check_frozen_code` still passes.
- **Gate fingerprint:** unchanged. It hashes the fingerprinted files and `repo_id@revision` (`engine/gates.py:38-51`),
  and the frozen copies of both are untouched.
- **What the frozen code loads:** the bytes pinned for the frozen revision. That these are the bytes B1 was frozen
  with is an inference, not a recorded fact:
  - B1's freeze (ledger seq 56) records t0 only as `repo_id` and revision, and the engine then loaded it by revision
    without hashing the files;
  - the two sha256 first appear in the repository on 2026-09-30 (commit `807a19c`). They were computed from the
    benchmark workflow's Actions-cache snapshot of revision `9b02c5f4` (`t0_pinned.py:24`), the kind of input the
    engine stopped trusting after the cache-poisoning finding;
  - the Hub head `fdd18964` serves byte-identical files. Commit dates in the rewritten history are not authoritative,
    so the head's "last weights change" date does not add independent evidence.
  A static test pinning the literal hash values, and printing them in the step summary for the approving owner, would
  make the guarantee checkable (section 8).
- **Ledger and record job:** unchanged. Kinds and context fields still hash to the `ce2ed6e8…` B1 pinned, and no
  new entry kind is written.
- **Scientific protocol:** unchanged. Claims, window, comparator, test, margin and alpha are all untouched.

## 5. Failure modes

| Event | What happens |
|---|---|
| The Hub head's bytes change | Staging refuses; the job stops before the load; nothing is unsealed |
| The repository is removed, renamed or access is revoked | Staging fails; nothing is unsealed. Remedy: a durable copy (section 7) |
| The token is missing | Staging fails, and the frozen load would raise anyway before any unseal |
| The token is present for staging but empty on the open step | The frozen load raises `LocalTokenNotFoundError` before any unseal |
| `HF_HUB_CACHE` unset, or different, on the open step | The frozen load raises `LocalEntryNotFoundError` before any unseal |
| The frozen install fails in 2027 (for example, a pinned wheel no longer served) | The job stops before staging; nothing is unsealed. The rehearsal (section 6) would show it first |
| The staged bytes change between staging and load | They would load without a check, but no step runs between the two |
| Something needs the Hub during scoring | Nothing should: scoring reuses the model loaded before the unseal (`engine/vault_run.py:88`). Offline mode affects only the Hugging Face library, not the forward-data downloads. A failure after the unseal would still consume the window, as the vault's code always has, so the rehearsal (section 6) matters |
| The staging step is skipped by mistake | With offline mode on the open step, the frozen load fails at once with `LocalEntryNotFoundError`, with no Hub contact. Without offline mode it asks the Hub for the vanished revision, and the load fails with a misleading `TypeError` (the mixin swallows the missing-revision error for `config.json`). Either way it fails before any unseal |

## 6. Proving it before April 2027: a load-only rehearsal

A separate, manually dispatched workflow with:
- no `engine-vault` environment, no ledger read or write, and no data read;
- `contents: read` permission and `HF_TOKEN` only.

What it does:
1. Checks out the `engine-freeze/B1` tag into a worktree.
2. Installs and tests the frozen code exactly as the vault job does.
3. Runs the same staging step.
4. In the worktree, with `HF_HUB_OFFLINE=1`, runs only the frozen loader (`arms._t0(...).load()`) and the frozen
   gate fingerprint, and asserts the fingerprint equals B1's recorded one. The expected value
   (`b2d50d2fce7653b9bfe1d71aabb39ab5308c86b768dd9d363e2f444985864273`, ledger seq 56) is written into the rehearsal,
   so it reads no ledger.

The rehearsal runs outside the `engine-vault` environment, so it does not test that environment's secret resolution.
Today `HF_TOKEN` is a repository secret (the referee job uses it without an environment); if it is ever defined as an
`engine-vault` environment secret, the rehearsal would use a different token.

Run it once after approval and again shortly before B1 opens.

## 7. Alternatives rejected

| Alternative | Why not |
|---|---|
| Change the revision in the frozen code, or score at a later commit | Breaks the freeze-commit rule (owner, 2026-09-27); the frozen check refuses another commit |
| Re-freeze B1 | Changes a frozen claim and spends alpha |
| A `theforecastingcompany/t0-alpha` directory inside `frozen/` | The trap of section 2: it ignores the frozen call's revision and token, so any directory at that path wins, and it means writing into the frozen worktree. (Neither this nor the chosen cache path checks content at load; in both, the staging-time hash is the guarantee) |
| Restore an Actions cache of the old snapshot | The engine reads no caches since the cache-poisoning finding of the third review round |

## 8. Decisions for the owner

1. **Approve this design** for implementation before 2027-04-01. The implementation and the rehearsal are a separate
   authorisation.
2. **A durable copy of the weights.** The Hub repository could change or disappear again before April 2027. Keeping
   a private copy of the two files elsewhere needs a check of the gated repository's licence terms. If it is
   allowed, the staging step can take the copy as a second source and verify it against the same hashes.
3. **The provenance of the pinned hashes** (section 4): whether a static test pinning the literal values, and their
   display in the step summary, is enough for the owner to approve the bytes B1 will load.
4. **Whether the same staging step should also serve future engine probes.** It would let current HEAD code load t0
   without editing fingerprinted files. The alternative is a content-verified loader at the probe call sites. This
   only matters if an Experiment 5 build is approved.

## 9. How this design was checked

An independent read-only review, on 2026-10-02:
- **Who:** two checkers, each followed by a skeptic.
  - One checked the code claims at `710b2b37` and at HEAD.
  - The other checked the claims about huggingface_hub 1.31.0 and tfc-t0 0.3.2 offline. It extracted the frozen tree
    (`git archive 710b2b37`) and ran its loader against a fake cache, with a dummy token and every network call
    logged and refused.
- **Results:**
  - The frozen loader, run from the extracted tree against a cache holding only the two staged files, loaded exactly
    those files with no network request.
  - Every cited line number holds, and so do B1's recorded gate fingerprint and catalogue hash, both recomputed from
    the frozen tree.
  - No finding was material. The minor corrections are applied above: two failure-mode mechanisms, where `stage()`
    downloads to and where its inputs come from, the retrieval record's retention and upload condition, the provenance
    of the pinned hashes, the rehearsal's expected fingerprint, and four more failure modes.
- **Not done:** nothing was implemented, and no real token or Hub request was used.
