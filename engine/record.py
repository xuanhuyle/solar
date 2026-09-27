"""The record job: chain pending entries onto the ledger (standard library only).

    python -m engine.record --mode probe --research research/*/pending_research.jsonl \
        --pending pending/pending.jsonl --pending-sha256 <sha|none> --ledger ledgerwt/ledger.jsonl \
        [--referee-result success --vault-result skipped --action probe]
    python -m engine.record --verify ledgerwt/ledger.jsonl
    python -m engine.record --freeze-commit B1 --ledger ledgerro/ledger.jsonl

Only the workflow's ``record`` job runs the first form; it alone may write the
``engine-ledger`` branch. It trusts the producing jobs as little as it can:

* **kinds by source and mode** - the research job's files may carry only
  ``research_call``; a vault's ``unseal``/``verdict``/``accepted_finding`` only
  in vault mode; seed entries only in seed mode; and so on (``ALLOWED``);
* **provenance** - the pending file is read only if its sha256 is the one the
  producing job (referee or vault) declared as its output; a file nobody
  declared (``none``) is ignored, and a different file is refused;
* **its own run identity** - ``run_id``, ``run_attempt`` and ``mode`` are taken
  from this job's environment, not from what a producer wrote;
* **idempotent within a run** - an item already recorded *by this run* (same
  kind and payload) is skipped, so re-running a failed record job is safe;
  identical items from other runs are always appended;
* **no stale freezes** - a freeze is refused if a freeze, unseal, verdict,
  accepted finding or gate landed after the ledger head it was decided on;
  an unseal and its verdict are facts about data already read and are always
  recorded, but only for a batch that really was frozen;
* **must leave a record** - a vault run, and a referee run that succeeded in a
  producing mode, must leave pending entries (``must_leave_record``).

Every run prints the verified head as a notice.
"""

from __future__ import annotations

import argparse
import hashlib
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
FACTS = frozenset({"unseal", "verdict", "accepted_finding"})  # about data already read: never refused as stale
STATE_KINDS = frozenset({"freeze", "unseal", "verdict", "accepted_finding", "gate"})  # what a freeze decision rests on
PRODUCING_MODES = frozenset({"probe", "gate", "reproduce", "freeze", "vault_dryrun"})


class RecordError(RuntimeError):
    pass


def _item_key(kind: str, payload: dict) -> str:
    return sha256_of({"kind": kind, "payload": payload})


def _check_freeze(entries: list[dict], payload: dict, head_before: int) -> None:
    h = payload.get("ledger_head_seq")
    if not isinstance(h, int) or isinstance(h, bool) or h > head_before:
        raise RecordError(f"freeze decided against ledger head {h!r}, which this ledger (head {head_before}) "
                          "does not have: refused")
    moved = [f"{e['seq']}:{e['kind']}" for e in entries if e["seq"] > h and e["kind"] in STATE_KINDS]
    if moved:
        raise RecordError(f"freeze decided against ledger head {h}, but {', '.join(moved)} landed since: refused")


def _check_fact(entries: list[dict], kind: str, payload: dict) -> None:
    """An unseal/verdict/accepted finding must belong to a batch that really was frozen (not a rehearsal)."""
    batch_id, sha = payload.get("batch_id"), payload.get("batch_sha256")
    if kind == "accepted_finding":
        batch_id = str(payload.get("finding_id", "")).split("-")[0]
    frozen = [e["payload"] for e in entries if e["kind"] == "freeze" and not e["payload"].get("rehearsal")
              and e["payload"].get("batch_id") == batch_id]
    if not frozen or (sha is not None and frozen[0].get("batch_sha256") != sha):
        raise RecordError(f"{kind} for batch {batch_id!r} matches no frozen batch on the ledger: refused")


def prepare(entries: list[dict], research: list[dict], pending: list[dict], *, mode: str, run_id: str,
            run_attempt: str) -> list[dict]:
    """Validate, re-stamp and de-duplicate this run's items (research first). Raises RecordError."""
    if mode not in ALLOWED:
        raise RecordError(f"unknown mode {mode!r}")
    head_before = entries[-1]["seq"] if entries else -1
    # Only this run's own earlier records (an earlier attempt of this record job) are skipped.
    seen = {_item_key(e["kind"], e["payload"]) for e in entries if str(e.get("run_id")) == str(run_id)}
    out = []
    for source, items, allowed in (("research", research, RESEARCH_KINDS), ("pending", pending, ALLOWED[mode])):
        if source == "research" and items and mode != "loop":
            raise RecordError("research entries outside loop mode")
        for item in items:
            kind = item["kind"]
            if kind not in allowed:
                raise RecordError(f"{source} file may not carry {kind!r} in mode {mode!r}")
            if _item_key(kind, item["payload"]) in seen:
                continue
            if kind == "freeze":
                _check_freeze(entries, item["payload"], head_before)
            if mode == "vault" and kind in FACTS:
                _check_fact(entries, kind, item["payload"])
            ctx = dict(item["context"], run_id=run_id, run_attempt=run_attempt, mode=mode)
            out.append({"kind": kind, "payload": item["payload"], "context": ctx})
    return out


def must_leave_record(mode: str, referee_result: str, vault_result: str, action: str) -> bool:
    """Did a job that always writes pending entries on success run in this mode?"""
    if vault_result not in ("", "skipped"):
        return True
    if referee_result != "success":
        return False
    return mode in PRODUCING_MODES or (mode == "loop" and action in ("probe", "freeze"))


def file_sha256(path: Path | None) -> str:
    if path is None or not Path(path).is_file() or Path(path).stat().st_size == 0:
        return "none"
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def declared_pending(path: Path | None, declared: str | None) -> list[dict]:
    """The pending file, read only if it is the one the producing job declared."""
    if declared is None:  # local use: no provenance to check
        return ledger.read_pending(path) if path else []
    declared = declared.strip() or "none"
    if declared == "none":
        return []  # no producing job wrote a file: whatever is there is not ours to record
    got = file_sha256(path)
    if got != declared:
        raise RecordError(f"pending file sha256 {got} is not the {declared} its producing job declared: refused")
    return ledger.read_pending(path)


def schema_errors(entries: list[dict], mode: str) -> list[str]:
    """Open batches frozen under another ledger schema: the vault reads the ledger with the code of the
    freeze commit, so the schema may not change while a batch is open. Caught on the first run after the
    change (while it can still be reverted) instead of when the vault opens. A vault run is exempt: its
    unseal and verdict are facts that must be recorded."""
    if mode == "vault":
        return []
    closed = {e["payload"].get("batch_id") for e in entries if e["kind"] in ("unseal", "verdict")}
    return [f"batch {e['payload']['batch_id']} was frozen under ledger schema {e['payload']['ledger_schema'][:12]}, "
            f"this code has {ledger.schema_sha256()[:12]}: revert the schema change until the batch is opened"
            for e in entries if e["kind"] == "freeze" and not e["payload"].get("rehearsal")
            and e["payload"].get("batch_id") not in closed and "ledger_schema" in e["payload"]
            and e["payload"]["ledger_schema"] != ledger.schema_sha256()]


def freezes(entries: list[dict]) -> list[tuple[str, str]]:
    """(batch id, code commit) of every recorded real freeze - each is pinned as tag engine-freeze/<id>."""
    return [(e["payload"]["batch_id"], str(e.get("code_commit", ""))) for e in entries
            if e["kind"] == "freeze" and not e["payload"].get("rehearsal")]


def freeze_commit(entries: list[dict], batch_id: str) -> str:
    """The code commit a batch was frozen at (the vault scores it with that code)."""
    for e in entries:
        if e["kind"] == "freeze" and e["payload"].get("batch_id") == batch_id and not e["payload"].get("rehearsal"):
            commit = str(e.get("code_commit", ""))
            if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
                raise RecordError(f"batch {batch_id}'s freeze entry names no usable commit ({commit!r})")
            return commit
    raise RecordError(f"no frozen batch {batch_id!r} on the ledger")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m engine.record")
    p.add_argument("--research", type=Path, nargs="*", default=[])
    p.add_argument("--pending", type=Path)
    p.add_argument("--pending-sha256", default=None, help="sha256 the producing job declared, or 'none'")
    p.add_argument("--ledger", type=Path)
    p.add_argument("--mode", default=os.environ.get("MODE", ""))
    p.add_argument("--require-pending", action="store_true")
    p.add_argument("--referee-result", default="")
    p.add_argument("--vault-result", default="")
    p.add_argument("--action", default="")
    p.add_argument("--research-result", default="", help="the research job's result (success: its record must exist)")
    p.add_argument("--freezes", action="store_true", help="list 'batch_id commit' of every recorded freeze")
    p.add_argument("--verify", type=Path)
    p.add_argument("--freeze-commit", default=None, metavar="BATCH_ID")
    args = p.parse_args(argv)
    if args.verify is not None:
        entries = ledger.read(args.verify)
        h = ledger.head(entries)
        print(f"::notice title=Engine ledger head::seq {h['seq']} sha256 {h['sha256']} ({len(entries)} entries, chain verified)")
        return 0
    if args.ledger is None:
        p.error("--ledger is required unless --verify is given")
    if args.freezes:
        for batch_id, commit in freezes(ledger.read(args.ledger)):
            print(batch_id, commit)
        return 0
    if args.freeze_commit is not None:
        try:
            print(freeze_commit(ledger.read(args.ledger), args.freeze_commit))
        except RecordError as exc:
            print(f"::error title=Vault refused::{exc}", file=sys.stderr)
            return 1
        return 0
    try:
        if args.research_result == "success" and not any(Path(p).is_file() for p in args.research):
            raise RecordError("the research job succeeded but its record (pending_research.jsonl) was not "
                              "downloaded: its billed calls would be lost")
        research = [item for path in args.research for item in ledger.read_pending(path)]
        pending = declared_pending(args.pending, args.pending_sha256)
    except (RecordError, ledger.LedgerError) as exc:
        print(f"::error title=Record refused::{exc}")
        return 1
    required = args.require_pending or must_leave_record(args.mode, args.referee_result, args.vault_result, args.action)
    if required and not pending:
        print("::error title=Nothing recorded::this run had to leave ledger entries and left none")
        return 1
    entries = ledger.read(args.ledger)
    drift = schema_errors(entries, args.mode)
    if drift:
        print(f"::error title=Record refused::{'; '.join(drift)}")
        return 1
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
