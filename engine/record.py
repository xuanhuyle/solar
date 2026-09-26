"""The record job: chain pending entries onto the ledger (standard library only).

    python -m engine.record --mode probe --research research/pending_research.jsonl \
        --pending pending/pending.jsonl --ledger ledgerwt/ledger.jsonl [--require-pending]
    python -m engine.record --verify ledgerwt/ledger.jsonl

Only the workflow's ``record`` job runs the first form; it alone may write the
``engine-ledger`` branch. It trusts the producing jobs as little as it can:

* **kinds by source and mode** - the research job's file may carry only
  ``research_call``; a vault's ``unseal``/``verdict``/``accepted_finding`` only
  in vault mode; seed entries only in seed mode; and so on (``ALLOWED``);
* **its own run identity** - ``run_id``, ``run_attempt`` and ``mode`` are taken
  from this job's environment, not from what a producer wrote;
* **idempotent** - an item already on the ledger (same kind and payload) is
  skipped, so re-running a failed record job is safe;
* **no stale decisions** - a freeze or unseal decided against an older ledger
  head than the one it would be appended to is refused;
* ``--require-pending`` - fail when a job that must leave a record (the vault)
  left none.

Every run prints the verified head as a notice.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from engine import ledger
from engine.canon import sha256_of
from engine.config import config_manifest

RESEARCH_KINDS = frozenset({"research_call"})
ALLOWED: dict[str, frozenset] = {
    "selftest": frozenset(),
    "avail": frozenset(),
    "seed": frozenset({"genesis", "legacy_result", "accepted_finding"}),
    "probe": frozenset({"probe_submitted", "probe_result", "probe_rejected", "note", "error"}),
    "loop": frozenset({"probe_submitted", "probe_result", "probe_rejected", "note", "error", "freeze"}),
    "freeze": frozenset({"freeze", "probe_rejected"}),
    "reproduce": frozenset({"probe_submitted", "probe_result", "probe_rejected", "gate", "note", "error"}),
    "gate": frozenset({"gate", "note", "error"}),
    "vault_dryrun": frozenset({"probe_submitted", "probe_result", "probe_rejected", "note", "error"}),
    "vault": frozenset({"unseal", "verdict", "accepted_finding", "error"}),
}
HEAD_CHECKED = frozenset({"freeze", "unseal"})


class RecordError(RuntimeError):
    pass


def _item_key(kind: str, payload: dict) -> str:
    return sha256_of({"kind": kind, "payload": payload})


def prepare(entries: list[dict], research: list[dict], pending: list[dict], *, mode: str, run_id: str,
            run_attempt: str) -> list[dict]:
    """Validate, re-stamp and de-duplicate this run's items (research first). Raises RecordError."""
    if mode not in ALLOWED:
        raise RecordError(f"unknown mode {mode!r}")
    head_before = entries[-1]["seq"] if entries else -1
    seen = {_item_key(e["kind"], e["payload"]) for e in entries}
    out = []
    for source, items, allowed in (("research", research, RESEARCH_KINDS), ("pending", pending, ALLOWED[mode])):
        if source == "research" and items and mode != "loop":
            raise RecordError("research entries outside loop mode")
        for item in items:
            kind = item["kind"]
            if kind not in allowed:
                raise RecordError(f"{source} file may not carry {kind!r} in mode {mode!r}")
            if kind in HEAD_CHECKED and item["payload"].get("ledger_head_seq") != head_before:
                raise RecordError(f"{kind} was decided against ledger head {item['payload'].get('ledger_head_seq')}, "
                                  f"but the ledger is at {head_before}: refused")
            key = _item_key(kind, item["payload"])
            if key in seen:
                continue
            seen.add(key)
            ctx = dict(item["context"], run_id=run_id, run_attempt=run_attempt, mode=mode)
            out.append({"kind": kind, "payload": item["payload"], "context": ctx})
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m engine.record")
    p.add_argument("--research", type=Path)
    p.add_argument("--pending", type=Path)
    p.add_argument("--ledger", type=Path)
    p.add_argument("--mode", default=os.environ.get("MODE", ""))
    p.add_argument("--require-pending", action="store_true")
    p.add_argument("--verify", type=Path)
    args = p.parse_args(argv)
    if args.verify is not None:
        entries = ledger.read(args.verify)
        h = ledger.head(entries)
        print(f"::notice title=Engine ledger head::seq {h['seq']} sha256 {h['sha256']} ({len(entries)} entries, chain verified)")
        return 0
    if args.ledger is None:
        p.error("--ledger is required unless --verify is given")
    research = ledger.read_pending(args.research) if args.research else []
    pending = ledger.read_pending(args.pending) if args.pending else []
    if args.require_pending and not pending:
        print("::error title=Nothing recorded::this run had to leave ledger entries and left none")
        return 1
    entries = ledger.read(args.ledger)
    try:
        items = prepare(entries, research, pending, mode=args.mode, run_id=os.environ.get("GITHUB_RUN_ID", "local"),
                        run_attempt=os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    except RecordError as exc:
        print(f"::error title=Record refused::{exc}")
        return 1
    new = ledger.append(args.ledger, items, manifest=config_manifest())
    h = ledger.head(ledger.read(args.ledger))
    for e in new:
        print(json.dumps({"seq": e["seq"], "kind": e["kind"], "sha256": e["sha256"]}))
    print(f"::notice title=Engine ledger head::seq {h['seq']} sha256 {h['sha256']} (+{len(new)} entries, chain verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
