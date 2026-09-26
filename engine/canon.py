"""Canonical JSON and its sha256: the one way the engine fingerprints anything."""

from __future__ import annotations

import hashlib
import json


def canonical_json(obj) -> str:
    """Sorted keys, no whitespace, UTF-8 kept: equal content gives equal bytes."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def sha256_of(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
