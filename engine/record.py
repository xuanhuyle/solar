"""The record job: chain pending entries onto the ledger (standard library only).

    python -m engine.record --pending results/engine/pending.jsonl --ledger ledgerwt/ledger.jsonl
    python -m engine.record --verify ledgerwt/ledger.jsonl

Only the workflow's ``record`` job runs the first form; it alone may write the
``engine-ledger`` branch. Every run prints the verified head as a notice.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine import ledger
from engine.config import config_manifest


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m engine.record")
    p.add_argument("--pending", type=Path)
    p.add_argument("--ledger", type=Path)
    p.add_argument("--verify", type=Path)
    args = p.parse_args(argv)
    if args.verify is not None:
        entries = ledger.read(args.verify)
        h = ledger.head(entries)
        print(f"::notice title=Engine ledger head::seq {h['seq']} sha256 {h['sha256']} ({len(entries)} entries, chain verified)")
        return 0
    if args.pending is None or args.ledger is None:
        p.error("--pending and --ledger are required unless --verify is given")
    items = ledger.read_pending(args.pending)
    new = ledger.append(args.ledger, items, manifest=config_manifest())
    entries = ledger.read(args.ledger)
    h = ledger.head(entries)
    for e in new:
        print(json.dumps({"seq": e["seq"], "kind": e["kind"], "sha256": e["sha256"]}))
    print(f"::notice title=Engine ledger head::seq {h['seq']} sha256 {h['sha256']} (+{len(new)} entries, chain verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
