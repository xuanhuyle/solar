"""t0-alpha pinned by content: the previously frozen bytes, fetched from the current Hub repository.

Retrieval event (docs/experiment_4/RETRIEVAL_EVENTS.md): the Hub rewrote the history of
theforecastingcompany/t0-alpha after 2026-09-28, and the frozen revision 9b02c5f4bb6c89ba15d9fa74554018fe6464220b
no longer resolves (RevisionNotFoundError, Actions run 36646007553). Its files survive byte for byte: the
benchmark workflow's cached snapshot of that revision and the Hub head fdd189642a529fee59ba7d491235a06779e41a83
hold the same config.json and model.safetensors (Actions run 36646852265).

Owner's decision (2026-09-30): the frozen specification is unchanged; the sha256 of the previously frozen
config.json and model.safetensors are pinned here; both files are fetched from the current Hugging Face
repository (its head, resolved at load time) and the model is built only when both match exactly. Any
mismatch aborts before any forecast. What was fetched, and from which revision, is returned for run_meta.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

log = logging.getLogger(__name__)

FILES = ("config.json", "model.safetensors")
# sha256 of the previously frozen revision's files (its cached snapshot, Actions run 36646852265)
PINNED_SHA256 = {
    "9b02c5f4bb6c89ba15d9fa74554018fe6464220b": {
        "config.json": "b2b545685283c579b99c774da0d7f07525683efca2b27dc4ffec99c109d5beba",
        "model.safetensors": "16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f",
    },
}


class PinnedWeightsError(RuntimeError):
    """The files the Hub served are not the frozen bytes: nothing may be forecast with them."""


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(repo_id: str, frozen_revision: str, *, token=True, download=None, head=None) -> tuple[Path, dict]:
    """A local directory holding the two files fetched from the repository's current head, verified against the
    pinned sha256 of ``frozen_revision``, and the retrieval record.

    ``head(repo_id)`` returns the current head revision and ``download(repo_id, revision)`` a directory holding
    the files (default: huggingface_hub, just those two files); both are injectable for tests.
    """
    if frozen_revision not in PINNED_SHA256:
        raise PinnedWeightsError(f"no pinned sha256 for {repo_id}@{frozen_revision}")
    want = PINNED_SHA256[frozen_revision]
    if head is None:
        from huggingface_hub import HfApi

        def head(repo):
            return HfApi().model_info(repo, token=token).sha
    if download is None:
        from huggingface_hub import snapshot_download

        def download(repo, rev):
            return snapshot_download(repo, revision=rev, allow_patterns=list(FILES), token=token)

    served_by = head(repo_id)
    local = Path(download(repo_id, served_by))
    got = {name: sha256_file(local / name) if (local / name).is_file() else None for name in FILES}
    if got != want:
        raise PinnedWeightsError(f"{repo_id}@{served_by} does not hold the frozen bytes of {frozen_revision}: "
                                 f"got {got}, want {want}")
    log.info("t0-alpha: frozen bytes of %s verified, fetched from the Hub head %s", frozen_revision, served_by)
    return local, {"repo_id": repo_id, "frozen_revision": frozen_revision, "served_by_revision": served_by,
                   "sha256": got, "verified": True, "event": "docs/experiment_4/RETRIEVAL_EVENTS.md"}


def load(repo_id: str, frozen_revision: str, *, token=True):
    """t0-alpha built from the verified local files only (never from an unverified download)."""
    from t0 import T0Forecaster as _T0

    local, record = fetch(repo_id, frozen_revision, token=token)
    model = _T0.from_pretrained(str(local)).eval()
    return model, record
