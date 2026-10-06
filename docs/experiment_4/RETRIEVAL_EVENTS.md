# Experiment 4: retrieval events

A record of events that changed *how* a frozen input is fetched, never *what* it is. The frozen specification
(`solarbench/price_spec.py`) and the one-pager are unchanged by every event listed here.

## 2026-09-29: t0-alpha's frozen revision id vanished upstream; the frozen bytes are unchanged

**What happened.** The frozen specification pins t0-alpha at `theforecastingcompany/t0-alpha` revision
`9b02c5f4bb6c89ba15d9fa74554018fe6464220b`. The engine loaded that revision on 2026-09-28. On 2026-09-29 the
Hugging Face Hub answered `RevisionNotFoundError` ("Invalid rev id") for it
([Actions run 36646007553](https://github.com/xuanhuyle/solar/actions/runs/36646007553)). The token was
valid (account `xuanhuyle`). The repository's history had been rewritten upstream: its commit list no longer
contains that revision, and its head is `fdd189642a529fee59ba7d491235a06779e41a83` (2026-09-24, "Cite the t0
arXiv paper").

**The bytes are the same.** [Actions run 36646852265](https://github.com/xuanhuyle/solar/actions/runs/36646852265)
restored the benchmark workflow's cached snapshot of the frozen revision (read-only) and compared it with the
Hub head:

| file | sha256 (frozen revision's snapshot) | bytes | Hub head `fdd18964` |
|---|---|---|---|
| `config.json` | `b2b545685283c579b99c774da0d7f07525683efca2b27dc4ffec99c109d5beba` | 250 | identical |
| `model.safetensors` | `16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f` | 406,601,492 | identical |

The Hub's last change to the weights is dated 2026-06-11 ("update weights").

**Owner's decision (2026-09-30).** Keep the frozen Experiment 4 specification unchanged. Record the upstream
history rewrite as a retrieval event (this entry). Pin the SHA-256 hashes of the previously frozen
`config.json` and `model.safetensors`. Fetch from the current Hugging Face repository and permit loading only
when both files match those hashes exactly. Any mismatch aborts before forecasting.

**How it is enforced.** `solarbench/t0_pinned.py` holds the two hashes, fetches both files from the
repository's current head, and builds the model only from the verified local files; a mismatch or a missing
file raises before any forecast (`tests/test_t0_pinned.py`). Every command that loads t0 writes the retrieval
record (frozen revision, the head that served the bytes, both sha256) to its `run_meta` under `t0_weights`.

**Not covered here.** The engine (`engine/catalogue.py`) and the earlier experiments' workflows still load t0
by the vanished revision id. Batch B1's vault scoring is affected; its fix is a separate, owner-approved change
made before 2027-04-01. Experiment 4 edits none of those files.
