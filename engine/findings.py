"""Accepted findings, read from the ledger (standard library only)."""

from __future__ import annotations


def latest_accepted(entries: list[dict], target_id: str) -> dict | None:
    """The newest accepted finding for a target that holds over *all* days (scope ``all``).

    A scope-limited finding (winter only, say) is never used as the comparator for all days.
    Without any ledger entry, consumption falls back to claim C1 from the legacy seed.
    """
    found = [e["payload"] for e in entries if e.get("kind") == "accepted_finding"
             and e["payload"].get("target") == target_id and e["payload"].get("scope", "all") == "all"]
    if found:
        return found[-1]
    if target_id == "consumption" and not entries:
        from engine.legacy import c1_entry

        return c1_entry()[1]
    return None
