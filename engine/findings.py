"""Accepted findings, read from the ledger (standard library only)."""

from __future__ import annotations


def latest_accepted(entries: list[dict], target_id: str) -> dict | None:
    """The accepted finding that ``accepted`` means for a target: a fold over the ledger in order.

    Only findings that hold over *all* days (scope ``all``) count. The first one becomes the accepted
    arm; a later one replaces it only if it was confirmed *against* it (comparator ``accepted``, and
    ``beat`` naming the finding it beat). So an arm that merely passed against a simple baseline -
    say a weaker arm frozen in the same batch - can never displace a stronger accepted arm.
    Without any ledger entry, consumption falls back to claim C1 from the legacy seed.
    """
    current = None
    for e in entries:
        p = e.get("payload", {})
        if e.get("kind") != "accepted_finding" or p.get("target") != target_id or p.get("scope", "all") != "all":
            continue
        if current is None or (p.get("comparator") == "accepted" and p.get("beat") == current.get("finding_id")):
            current = p
    if current is not None:
        return current
    if target_id == "consumption" and not entries:
        from engine.legacy import c1_entry

        return c1_entry()[1]
    return None
