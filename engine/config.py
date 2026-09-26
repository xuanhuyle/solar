"""The referee's configuration fingerprint: which code judged a result.

``config_sha256`` hashes every file that can change a verdict - the engine,
``solarbench`` and the pinned dependency lists - so a ledger entry names the
exact referee that produced it. The record job adds a ``config`` entry whenever
the fingerprint changes. Standard library only (the record job installs nothing).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ("engine/**/*.py", "solarbench/*.py", "requirements.txt", "constraints-ci.txt",
            "requirements-researcher.txt")


def config_manifest(root: Path = ROOT) -> dict[str, str]:
    files: dict[str, str] = {}
    for pattern in PATTERNS:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and "__pycache__" not in path.parts:
                files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(files.items()))


def config_sha256(root: Path = ROOT) -> str:
    h = hashlib.sha256()
    for name, digest in config_manifest(root).items():
        h.update(f"{name}\0{digest}\n".encode("utf-8"))
    return h.hexdigest()
