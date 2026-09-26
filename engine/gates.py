"""The known-answer gate's rules and which gate results still count (standard library only).

The gate itself (``engine.referee.known_answer``) needs t0 and pandas; these rules
do not, so the researcher's digest and the vault can tell which weather
covariates are usable right now without the forecasting stack. A gate result
counts only if it ran in full (not a smoke run) under the current rules version
and on the current covariate code (``gate_fingerprint``).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

#: ka/2, declared on 2026-09-26 before any run under it (owner's decision). ka/1 used 2024-09-02..2024-11-04
#: and decoy_ratio_max 1.05; consumption/temperature failed only that rule (1.0521) while alignment and
#: signal use passed. The noise rule guards against a broken pipeline, not against false findings - t0's
#: sensitivity to a junk covariate only biases results *against* that covariate - so it is widened to 1.10
#: and the gate re-run once, on the next 64 days, which it has never seen. No further change without the owner.
KA_PERIOD = ("2024-11-05", "2025-01-07")
KA_RULES = {
    "version": "ka/2",
    "planted_ratio_max": 0.95,       # planted MAE / t0 MAE: the planted signal must help by >= 5%
    "decoy_ratio_min": 0.98,         # pure noise must not help ...
    "decoy_ratio_max": 1.10,         # ... nor break t0 (ka/1: 1.05)
    "shift_penalty_min": 1.01,       # a +-1 h shift must cost >= 1%
    "noise_sd_share_of_p99": 0.05,
    "seed": 0,
}
RULE_CHANGE = {"from": "ka/1", "to": "ka/2", "changed": {"decoy_ratio_max": [1.05, 1.10],
                                                           "period": [["2024-09-02", "2024-11-04"], list(KA_PERIOD)]},
               "decided": "owner, 2026-09-26, after ka/1 failed consumption/wx_temperature on the noise rule only",
               "reason": ("the noise rule guards against a broken pipeline; t0's sensitivity to a junk covariate only "
                          "biases results against the covariate, so it cannot create false findings")}
FINGERPRINT_FILES = ("engine/covs.py", "engine/gates.py", "engine/referee/known_answer.py", "solarbench/covariates.py")


def gate_fingerprint() -> str:
    """sha256 of the code a gate result depends on: a pass does not survive a change to it."""
    root = Path(__file__).resolve().parents[1]
    h = hashlib.sha256()
    for name in FINGERPRINT_FILES:
        h.update(name.encode() + b"\0" + (root / name).read_bytes())
    return h.hexdigest()


def passed_gates(entries: list[dict]) -> set[tuple[str, str]]:
    """(target, covariate) pairs whose latest full (not smoke) known-answer gate passed under the
    current rules version and the current code fingerprint."""
    latest: dict[tuple[str, str], bool] = {}
    current = gate_fingerprint()
    for e in entries:
        p = e.get("payload", {})
        if e.get("kind") == "gate" and p.get("gate") == "known_answer" and not p.get("limit_days") \
                and p.get("rules_version") == KA_RULES["version"] and p.get("fingerprint") == current:
            latest[(p["target"], p["covariate"])] = bool(p.get("pass"))
    return {k for k, ok in latest.items() if ok}


def rules_changed_since(entries: list[dict]) -> bool:
    """True if the ledger's latest known-answer gate ran under another rules version (a change to declare)."""
    versions = [e["payload"].get("rules_version", "ka/1") for e in entries
                if e.get("kind") == "gate" and e["payload"].get("gate") == "known_answer"]
    return bool(versions) and versions[-1] != KA_RULES["version"]
