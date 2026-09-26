"""Claim batches: the structural checks every freeze must pass (standard library only).

The researcher job runs these before proposing a freeze (so a malformed batch
gets its one repair), and the vault runs them first; the vault then adds the
checks that need the ledger (gates, evidence, accepted finding, calendar).
"""

from __future__ import annotations

from engine import catalogue as cat

BATCH_VERSION = "claims/0"
MAX_CLAIMS = 4
DELTAS = (0.0, 0.05, 0.10, 0.20)
COMPARATORS = ("best_simple", "t0_base", "accepted")  # rte_j1 never decides
CLAIM_FIELDS = frozenset({"id", "statement", "target", "arm", "comparator", "scope", "delta", "evidence"})


def structure_errors(batch) -> list[str]:
    """Every structural problem with a proposed batch (empty list = well formed)."""
    if not isinstance(batch, dict) or set(batch) != {"batch_version", "claims"} or batch.get("batch_version") != BATCH_VERSION:
        return [f"a batch is exactly {{'batch_version': {BATCH_VERSION!r}, 'claims': [...]}}"]
    claims = batch["claims"]
    if not isinstance(claims, list) or not 1 <= len(claims) <= MAX_CLAIMS:
        return [f"1..{MAX_CLAIMS} claims required"]
    errors: list[str] = []
    targets = set()
    for i, c in enumerate(claims):
        w = f"claims[{i}]"
        if not isinstance(c, dict) or set(c) != CLAIM_FIELDS:
            errors.append(f"{w}: fields must be exactly {sorted(CLAIM_FIELDS)}")
            continue
        if c["target"] not in cat.TARGETS:
            errors.append(f"{w}: unknown target {c['target']!r}")
        targets.add(c["target"])
        if c["comparator"] not in COMPARATORS:
            errors.append(f"{w}: comparator must be one of {list(COMPARATORS)} (rte_j1 never decides)")
        if c["scope"] not in cat.SCOPES:
            errors.append(f"{w}: unknown scope {c['scope']!r}")
        if not isinstance(c["delta"], (int, float)) or isinstance(c["delta"], bool) or float(c["delta"]) not in DELTAS:
            errors.append(f"{w}: delta must be one of {DELTAS}")
        if not isinstance(c["statement"], str) or not 0 < len(c["statement"]) <= 300:
            errors.append(f"{w}: statement of 1..300 characters")
        arm = c["arm"]
        covs = arm.get("covariates") if isinstance(arm, dict) and set(arm) == {"covariates"} else None
        if not isinstance(covs, list):
            errors.append(f"{w}: arm is exactly {{'covariates': [...]}}")
            covs = []
        if len(covs) > cat.LIMITS["covariates_per_arm"]:
            errors.append(f"{w}: at most {cat.LIMITS['covariates_per_arm']} covariates")
        seen = set()
        for cv in covs:
            if not isinstance(cv, dict) or not set(cv) <= {"id", "transform"} or "id" not in cv:
                errors.append(f"{w}: covariate {cv!r} must be {{'id': ..., 'transform': ...}}")
                continue
            entry = cat.COVARIATES.get(cv["id"])
            tr = cv.get("transform", "raw")
            if entry is None or c["target"] not in entry["targets"] or tr not in entry["transforms"]:
                errors.append(f"{w}: covariate {cv['id']}/{tr} is not in the catalogue for {c['target']}")
            if (cv["id"], tr) in seen:
                errors.append(f"{w}: duplicate covariate {cv['id']}/{tr}")
            seen.add((cv["id"], tr))
        ev = c["evidence"]
        if not isinstance(ev, list) or not ev or not all(isinstance(x, int) and not isinstance(x, bool) for x in ev):
            errors.append(f"{w}: evidence must list the ledger seq of at least one probe_result")
    if len(targets) > 1:
        errors.append("one target per batch")
    return errors


def normal_arm(covariates: list[dict]) -> list[dict]:
    return sorted(({"id": c["id"], "transform": c.get("transform", "raw")} for c in covariates),
                  key=lambda x: (x["id"], x["transform"]))
