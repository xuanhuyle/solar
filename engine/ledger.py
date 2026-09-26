"""The engine's findings ledger: append-only, hash-chained JSON lines.

Every entry names its predecessor's sha256, so editing, dropping, inserting or
reordering any line breaks ``verify_chain``. It records *everything*: each
research call, each probe (accepted or rejected), each result - stamped
EXPLORATORY - each freeze, unseal and verdict, and each change of referee code.

The ledger lives on the ``engine-ledger`` branch. Jobs never write it: they
leave *pending* entries (``kind``, ``payload`` and the run's context) in a file,
and the workflow's ``record`` job - the only one with write permission - chains
them on. Standard library only.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from engine.canon import canonical_json, sha256_of
from engine.config import config_sha256

ZERO = "0" * 64
KINDS = frozenset({
    "genesis", "legacy_result", "accepted_finding", "config", "gate", "research_call",
    "probe_submitted", "probe_rejected", "probe_result", "freeze", "unseal", "verdict", "error", "note",
})
CONTEXT = ("at", "run_id", "run_attempt", "code_commit", "config_sha256", "actor", "mode")
FIELDS = ("seq", "prev_sha256", "kind", *CONTEXT, "payload", "sha256")
EXPLORATORY = "EXPLORATORY - discovery zone, not creditable"
LEGACY = "LEGACY (as recorded before the engine existed)"


class LedgerError(RuntimeError):
    """The ledger is malformed or its chain is broken."""


def entry_sha256(entry: dict) -> str:
    return sha256_of({k: v for k, v in entry.items() if k != "sha256"})


def _check_finite(obj, where="payload") -> None:
    if isinstance(obj, float) and not math.isfinite(obj):
        raise LedgerError(f"non-finite number in {where}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _check_finite(v, f"{where}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_finite(v, f"{where}[{i}]")


def verify_chain(entries: list[dict]) -> None:
    prev = ZERO
    for i, e in enumerate(entries):
        if tuple(sorted(e)) != tuple(sorted(FIELDS)):
            raise LedgerError(f"entry {i}: fields {sorted(e)} != {sorted(FIELDS)}")
        if e["seq"] != i:
            raise LedgerError(f"entry {i}: seq {e['seq']} (dropped, inserted or reordered line)")
        if e["prev_sha256"] != prev:
            raise LedgerError(f"entry {i}: prev_sha256 does not match entry {i - 1}")
        if e["kind"] not in KINDS:
            raise LedgerError(f"entry {i}: unknown kind {e['kind']!r}")
        if (i == 0) != (e["kind"] == "genesis"):
            raise LedgerError(f"entry {i}: genesis must be first and only first")
        if entry_sha256(e) != e["sha256"]:
            raise LedgerError(f"entry {i}: sha256 does not match its content (edited)")
        prev = e["sha256"]


def read(path: Path) -> list[dict]:
    """All entries, chain verified; an absent file is an empty ledger."""
    path = Path(path)
    if not path.exists():
        return []
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    verify_chain(entries)
    return entries


def head(entries: list[dict]) -> dict:
    if not entries:
        return {"seq": -1, "sha256": ZERO}
    return {"seq": entries[-1]["seq"], "sha256": entries[-1]["sha256"]}


def _git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True,
                              cwd=Path(__file__).resolve().parents[1]).stdout.strip()
    except Exception:
        return "unknown"


def run_context(mode: str) -> dict:
    """Who and what produced an entry: the Actions run, the code commit and the referee fingerprint."""
    return {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "1"),
        "code_commit": os.environ.get("GITHUB_SHA") or _git_commit(),
        "config_sha256": config_sha256(),
        "actor": os.environ.get("GITHUB_ACTOR", "local"),
        "mode": mode,
    }


def pending(kind: str, payload: dict, context: dict) -> dict:
    if kind not in KINDS:
        raise LedgerError(f"unknown kind {kind!r}")
    _check_finite(payload)
    canonical_json(payload)  # must serialise
    return {"kind": kind, "payload": payload, "context": {k: context[k] for k in CONTEXT}}


def write_pending(path: Path, items: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for item in items:
            fh.write(canonical_json(item) + "\n")
    return path


def read_pending(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    items = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in items:
        if set(item) != {"kind", "payload", "context"} or set(item["context"]) != set(CONTEXT):
            raise LedgerError(f"malformed pending entry: {sorted(item)}")
        pending(item["kind"], item["payload"], item["context"])  # re-validate
    return items


def chain(entries: list[dict], items: list[dict], *, manifest: dict | None = None) -> list[dict]:
    """New entries for ``items``, chained after ``entries``.

    A ``genesis`` item is dropped if the ledger already has one. A ``config``
    entry is inserted first whenever an item's referee fingerprint differs from
    the last recorded one.
    """
    out: list[dict] = []
    last_config = next((e["payload"]["config_sha256"] for e in reversed(entries) if e["kind"] == "config"), None)

    def add(kind, payload, context):
        prior = entries + out
        e = {"seq": len(prior), "prev_sha256": prior[-1]["sha256"] if prior else ZERO, "kind": kind,
             **{k: context[k] for k in CONTEXT}, "payload": payload}
        e["sha256"] = entry_sha256(e)
        out.append(e)

    for item in items:
        kind, payload, ctx = item["kind"], item["payload"], item["context"]
        if kind == "genesis":
            if entries or out:
                continue
            add(kind, payload, ctx)
            continue
        if not (entries or out):
            raise LedgerError("the ledger has no genesis yet: run the seed mode first")
        if ctx["config_sha256"] != last_config:
            add("config", {"config_sha256": ctx["config_sha256"], "code_commit": ctx["code_commit"],
                           "files": manifest or {}}, ctx)
            last_config = ctx["config_sha256"]
        add(kind, payload, ctx)
    verify_chain(entries + out)
    return out


def append(path: Path, items: list[dict], *, manifest: dict | None = None) -> list[dict]:
    path = Path(path)
    entries = read(path)
    new = chain(entries, items, manifest=manifest)
    if new:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            for e in new:
                fh.write(canonical_json(e) + "\n")
        read(path)  # the file as written must verify
    return new


def digest(entries: list[dict], max_rows: int = 40) -> dict:
    """What the researcher may see: accepted findings, recent exploratory results,
    rejections, budget, the open batch (window only) and closed verdicts."""
    by_kind: dict[str, list[dict]] = {}
    for e in entries:
        by_kind.setdefault(e["kind"], []).append(e)

    def rows(kind, n=max_rows):
        return [{"seq": e["seq"], **e["payload"]} for e in by_kind.get(kind, [])[-n:]]

    def compact_result(e):
        p = e["payload"]
        keep = ("arm", "vs", "days", "skill", "ci95", "p_one_sided", "mae_arm", "mae_vs", "days_won", "days_lost",
                "error", "note")
        spec = p.get("spec", {})
        return {"seq": e["seq"], "probe_sha256": p.get("probe_sha256"), "submitted_by": p.get("submitted_by"),
                "status": p.get("status"), "target": p.get("target"), "period": p.get("period"), "scope": p.get("scope"),
                "arms": spec.get("arms"), "rationale": spec.get("rationale"),
                "eligible_days": {k: v.get("eligible_days") for k, v in (p.get("methods") or {}).items()},
                "comparisons": [{k: c[k] for k in keep if k in c} for c in p.get("comparisons", [])]}

    def compact_gate(e):
        p = e["payload"]
        return {"seq": e["seq"], **{k: p[k] for k in ("gate", "target", "covariate", "pass", "planted_ratio",
                                                       "decoy_ratio", "shift_penalty", "checks", "limit_days") if k in p}}

    return {
        "head": head(entries),
        "accepted_findings": rows("accepted_finding", 100),
        "legacy_results": [{"seq": e["seq"], "id": e["payload"].get("id"), "summary": e["payload"].get("summary")}
                           for e in by_kind.get("legacy_result", [])],
        "probe_results": [compact_result(e) for e in by_kind.get("probe_result", [])[-max_rows:]],
        "probe_rejections": [{"seq": e["seq"], "reasons": e["payload"].get("reasons")}
                             for e in by_kind.get("probe_rejected", [])[-10:]],
        "gates": [compact_gate(e) for e in by_kind.get("gate", [])[-50:]],
        "open_batches": [{"seq": e["seq"], "batch_id": e["payload"].get("batch_id"),
                          "window": e["payload"].get("window")} for e in by_kind.get("freeze", [])
                         if not any(v["payload"].get("batch_id") == e["payload"].get("batch_id")
                                    for v in by_kind.get("verdict", []))],
        "verdicts": rows("verdict", 100),
        "counts": {k: len(v) for k, v in sorted(by_kind.items())},
    }
