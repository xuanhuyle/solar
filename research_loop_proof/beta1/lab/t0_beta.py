"""t0-beta for new research-loop work (NEXT_MILESTONE_PROMPT.md section 2-3), loaded by content.

Source: ``theforecastingcompany/t0-beta`` on the Hugging Face Hub (ungated; no token is sent). It needs
``tfc-t0>=0.5.0``: older releases load these weights without error but apply t0-alpha's input normalization (the
package README; ``scaler_eps`` / ``scaler_eps_mode`` in ``config.json``). The alpha loader
(``solarbench/t0_pinned.py``) and the alpha adapter (``phase0/lab/instruments.T0``) are not touched.

The qualification run fetches the files from the Hub head and records the revision and the sha256 of each file;
those are then pinned in ``PINNED`` and every later load refuses other bytes.
"""
from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import numpy as np

from research_loop_proof.phase0.lab.instruments import _NonFiniteWatcher
from solarbench.t0_pinned import sha256_file

REPO = "theforecastingcompany/t0-beta"
FILES = ("config.json", "model.safetensors")
MIN_RUNTIME = (0, 5, 0)
H = 24
# Filled from the qualification run's record (revision and sha256 of each file); empty until then.
PINNED: dict = {}


class BetaError(RuntimeError):
    """t0-beta cannot be used as required (wrong runtime, unverified or mismatched bytes)."""


def runtime_version() -> str:
    return metadata.version("tfc-t0")


def require_runtime() -> str:
    v = runtime_version()
    parts = tuple(int(p) for p in v.split(".")[:3] if p.isdigit())
    if parts < MIN_RUNTIME:
        raise BetaError(f"tfc-t0 {v} would run t0-beta under t0-alpha's normalization; >= 0.5.0 is required")
    return v


def fetch(weights: Path, *, head=None, download=None, pinned: dict | None = None) -> dict:
    """Download the files from the repository's current head into ``weights`` and record their sha256.

    With pins (``PINNED`` once qualified), any other bytes are refused before anything is written."""
    pinned = PINNED if pinned is None else pinned
    if head is None:
        from huggingface_hub import HfApi

        def head(repo):
            return HfApi().model_info(repo, token=False).sha
    if download is None:
        from huggingface_hub import snapshot_download

        def download(repo, rev):
            return snapshot_download(repo, revision=rev, allow_patterns=list(FILES), token=False)

    served = head(REPO)
    local = Path(download(REPO, served))
    got = {n: sha256_file(local / n) if (local / n).is_file() else None for n in FILES}
    if None in got.values():
        raise BetaError(f"{REPO}@{served} lacks {[n for n, h in got.items() if h is None]}")
    if pinned and got != pinned["sha256"]:
        raise BetaError(f"{REPO}@{served} does not hold the qualified bytes: got {got}, want {pinned['sha256']}")
    weights.mkdir(parents=True, exist_ok=True)
    for n in FILES:
        shutil.copyfile(local / n, weights / n)
    record = {"repo": REPO, "served_revision": served, "sha256": got, "pinned": bool(pinned),
              "qualified_revision": pinned.get("revision") if pinned else None,
              "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": "huggingface.co"}
    (weights / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


def load(weights: Path):
    """t0-beta built from the local copy only, re-verified (against the pins once qualified). No network."""
    version = require_runtime()
    from t0 import T0Forecaster

    rec = json.loads((weights / "record.json").read_text())
    got = {n: sha256_file(weights / n) for n in FILES}
    if got != rec["sha256"] or (PINNED and got != PINNED["sha256"]):
        raise BetaError(f"local t0-beta files do not match their record or the pins: {got}")
    model = T0Forecaster.from_pretrained(str(weights)).eval()
    return model, {**rec, "tfc_t0": version}


class BetaT0:
    """Batched zero-shot t0-beta medians, with the same interface as Phase 0's ``T0`` (tfc-t0 >= 0.5.0 API)."""

    LEVELS = (0.1, 0.5, 0.9)

    def __init__(self, model, batch_size: int = 32):
        self.model, self.batch_size, self.sanitised, self.rows = model, batch_size, 0, 0

    def forecast(self, requests: list[tuple[np.ndarray, np.ndarray | None]]) -> list[np.ndarray]:
        import torch

        out: list = [None] * len(requests)
        self.rows += len(requests)
        groups: dict = {}
        for i, (ctx, block) in enumerate(requests):
            groups.setdefault((len(ctx), 0 if block is None else block.shape[0]), []).append(i)
        logger = logging.getLogger("t0.model.model")
        for (_, k), idx in sorted(groups.items()):
            for s in range(0, len(idx), self.batch_size):
                part = idx[s:s + self.batch_size]
                ctx = torch.from_numpy(np.stack([requests[i][0] for i in part]).astype("float32"))
                kwargs = {"horizon": H, "quantile_levels": list(self.LEVELS)}
                if k:
                    kwargs["future_covariates"] = torch.from_numpy(
                        np.stack([requests[i][1] for i in part]).astype("float32"))
                watcher = _NonFiniteWatcher()
                logger.addHandler(watcher)
                try:
                    pred = self.model.predict(ctx, **kwargs)
                finally:
                    logger.removeHandler(watcher)
                self.sanitised += watcher.count
                med = pred.median.detach().cpu().numpy().astype("float64")
                for j, i in enumerate(part):
                    out[i] = med[j, :H]
        return out
