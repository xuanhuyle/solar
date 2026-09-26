"""The researcher's discovery budget, read from the ledger.

Each comparison the researcher runs costs one evaluation; the budget is
``DISCOVERY_BUDGET`` (the design documents' Q = 200). An identical spec (same
probe hash) returns the recorded result at no cost. Referee and owner runs
(reproductions, gates, manual probes) are not charged.
"""

from __future__ import annotations

DISCOVERY_BUDGET = 200


def _researcher(p: dict) -> bool:
    return str(p.get("submitted_by", "")).startswith("researcher")


def spent(entries: list[dict]) -> int:
    return sum(len(e["payload"].get("comparisons", [])) for e in entries
               if e.get("kind") == "probe_result" and _researcher(e["payload"]))


def remaining(entries: list[dict]) -> int:
    return max(0, DISCOVERY_BUDGET - spent(entries))


def recorded(entries: list[dict], probe_sha256: str) -> dict | None:
    """The latest valid result for an identical probe, with its ledger sequence number."""
    for e in reversed(entries):
        p = e.get("payload", {})
        if e.get("kind") == "probe_result" and p.get("probe_sha256") == probe_sha256 and "comparisons" in p:
            return {"seq": e["seq"], **p}
    return None
