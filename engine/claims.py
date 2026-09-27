"""Claim batches: every check a freeze must pass, in the standard library only.

``structure_errors`` checks the shape; ``ledger_errors`` checks it against the
ledger (weather gates, the accepted finding, the cited evidence, the calendar).
The researcher job runs both before proposing a freeze - so a bad citation gets
its one repair - and the vault runs the very same functions when it freezes.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from engine import catalogue as cat
from engine.findings import latest_accepted

BATCH_VERSION = "claims/0"
MAX_CLAIMS = 4
DELTAS = (0.0, 0.05, 0.10, 0.20)
COMPARATORS = ("best_simple", "t0_base", "accepted")  # rte_j1 never decides
CLAIM_FIELDS = frozenset({"id", "statement", "target", "arm", "comparator", "scope", "delta", "evidence"})
WEATHER = ("wx_temperature", "wx_radiation")

# The forward window (owner's choice, 2026-09-26): 12 blocks of 14 days after a 14-day embargo; a block
# counts with >= 10 days and the test needs >= 10 of the 12 blocks. engine.referee.stats uses the same values.
PARIS = ZoneInfo("Europe/Paris")
EMBARGO_DAYS = 14
BLOCK_DAYS = 14
WINDOW_BLOCKS = 12
MIN_WINDOW_BLOCKS = 10
MIN_DAYS_PER_BLOCK = 10
WINDOW_DAYS = BLOCK_DAYS * WINDOW_BLOCKS  # 168


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
        if not isinstance(c["target"], str) or c["target"] not in cat.TARGETS:
            errors.append(f"{w}: unknown target {c['target']!r}")
        else:
            targets.add(c["target"])
        if not isinstance(c["comparator"], str) or c["comparator"] not in COMPARATORS:
            errors.append(f"{w}: comparator must be one of {list(COMPARATORS)} (rte_j1 never decides)")
        if not isinstance(c["scope"], str) or c["scope"] not in cat.SCOPES:
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
            if not isinstance(cv, dict) or not set(cv) <= {"id", "transform"} or "id" not in cv \
                    or not all(isinstance(v, str) for v in cv.values()):
                errors.append(f"{w}: covariate {cv!r} must be {{'id': ..., 'transform': ...}} (strings)")
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


# ------------------------------------------------------------------ against the ledger


def window_for(frozen_at: datetime) -> tuple[date, date]:
    """The forward window of a batch frozen at ``frozen_at`` (Paris-local days, inclusive)."""
    local = frozen_at.astimezone(PARIS).date()
    first = local + timedelta(days=EMBARGO_DAYS + 1)
    return first, first + timedelta(days=WINDOW_DAYS - 1)


def scope_days_per_block(scope: str, first: date) -> list[int]:
    months = cat.SCOPES[scope]
    out = []
    for b in range(WINDOW_BLOCKS):
        days = [first + timedelta(days=b * BLOCK_DAYS + i) for i in range(BLOCK_DAYS)]
        out.append(sum(1 for d in days if months is None or d.month in months))
    return out


def normalise(batch: dict) -> list[dict]:
    """The frozen form of a structurally valid batch's claims."""
    return [{"id": f"C{i + 1}", "statement": c["statement"], "target": c["target"],
             "arm": {"covariates": normal_arm(c["arm"]["covariates"])}, "comparator": c["comparator"],
             "scope": c["scope"], "metric": "mae", "delta": float(c["delta"]), "evidence": sorted(set(c["evidence"]))}
            for i, c in enumerate(batch["claims"])]


def evidence_matches(p: dict, claim: dict, accepted_arm: dict | None = None) -> bool:
    """A cited result supports a claim only if it tested exactly the claim's arm against its comparator and
    scope - and, for ``accepted``, against the very arm that ``accepted`` means now."""
    if not str(p.get("status", "")).startswith("EXPLORATORY") or p.get("leak_checks_passed") is not True:
        return False
    if p.get("limit_days") or p.get("target") != claim["target"] or p.get("scope") != claim["scope"]:
        return False
    if claim["comparator"] == "accepted":
        used = (p.get("accepted_arm") or {}).get("covariates")
        if accepted_arm is None or used is None or normal_arm(used) != normal_arm(accepted_arm.get("covariates", [])):
            return False
    spec = p.get("spec") or {}
    arms = {a.get("name"): normal_arm(a.get("covariates", [])) for a in spec.get("arms", []) if isinstance(a, dict)}
    return any(c.get("vs") == claim["comparator"] and arms.get(c.get("arm")) == claim["arm"]["covariates"]
               and "skill" in c for c in p.get("comparisons", []))


def ledger_errors(batch: dict, entries: list[dict], *, gates: set[tuple[str, str]], first: date | None = None) -> list[str]:
    """Every problem with a structurally valid batch against the ledger (empty list = freezable)."""
    errors: list[str] = []
    results = {e["seq"]: e["payload"] for e in entries if e.get("kind") == "probe_result"}
    for i, norm in enumerate(normalise(batch)):
        w, target = f"claims[{i}]", norm["target"]
        for cv in norm["arm"]["covariates"]:
            if cv["id"] in WEATHER and (target, cv["id"]) not in gates:
                errors.append(f"{w}: {cv['id']} has no passed known-answer gate for {target}")
        acc = latest_accepted(entries, target) if entries else None
        acc_arm = (acc or {}).get("arm")
        if norm["comparator"] == "accepted":
            if acc is None:
                errors.append(f"{w}: there is no accepted finding for {target} to compare with")
            else:
                for cv in acc["arm"].get("covariates", []):
                    if cv["id"] in WEATHER and (target, cv["id"]) not in gates:
                        errors.append(f"{w}: the accepted arm uses {cv['id']}, which has no passed gate")
                if normal_arm(acc["arm"].get("covariates", [])) == norm["arm"]["covariates"]:
                    errors.append(f"{w}: the arm is the accepted arm itself - it cannot beat itself")
        cited = [s for s in norm["evidence"] if s in results]
        if not any(evidence_matches(results[s], norm, acc_arm) for s in cited):
            why = "; ".join(f"seq {s}: {_why_not(results[s], norm, acc_arm)}" for s in cited) or "no cited seq is a probe_result"
            errors.append(f"{w}: no cited probe_result (full-length, leak checks passed, exploratory) tested this exact "
                          f"arm against {norm['comparator']} on scope {norm['scope']} ({why})")
        if first is not None:
            short = [n for n in scope_days_per_block(norm["scope"], first) if n < MIN_DAYS_PER_BLOCK]
            if len(short) > WINDOW_BLOCKS - MIN_WINDOW_BLOCKS:
                errors.append(f"{w}: scope {norm['scope']} leaves fewer than {MIN_DAYS_PER_BLOCK} days in "
                              f"{len(short)} of the window's {WINDOW_BLOCKS} blocks - it could never pass")
    return errors


def _why_not(p: dict, claim: dict, accepted_arm: dict | None) -> str:
    if not str(p.get("status", "")).startswith("EXPLORATORY"):
        return "not an exploratory result"
    if p.get("leak_checks_passed") is not True:
        return "leak checks did not pass"
    if p.get("limit_days"):
        return "a smoke run (limit_days)"
    if p.get("target") != claim["target"] or p.get("scope") != claim["scope"]:
        return "another target or scope"
    if claim["comparator"] == "accepted":
        used = (p.get("accepted_arm") or {}).get("covariates")
        if used is None or accepted_arm is None or normal_arm(used) != normal_arm(accepted_arm.get("covariates", [])):
            return "measured against another accepted arm"
    return "it did not compare this exact arm against this comparator"
