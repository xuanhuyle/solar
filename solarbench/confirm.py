"""One-shot confirmation of a single frozen claim on the sealed 2025 data.

The owner allowed the sealed 2025 data to be used **once**, to confirm **one**
finding frozen beforehand.  This module holds that finding (``CLAIM``), its
fingerprint (``FROZEN_CLAIM_SHA256``, committed before any 2025 access) and
the only door to the sealed period (``open_sealed``).  The door opens when:

* the claim is byte-for-byte the frozen one (its sha256 matches);
* the pinned model has already been loaded, so a model failure cannot waste
  the one look at the data;
* ``ledger/confirmations.jsonl`` holds no earlier use of the claim.

After the run, its result is appended to the ledger and committed, which shuts
the door for good: the committed ledger is always consulted, whatever ledger
path a caller passes, and an access stops being valid once the committed ledger
records its claim (both added after the post-run audit).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger" / "confirmations.jsonl"

#: Source rule, in order: the first with >= MIN_VALID of the year's cells valid.
SOURCES = ("eco2mix-national-cons-def", "eco2mix-national-tr")

CLAIM: dict = {
    "id": "C1",
    "statement": (
        "On French national electricity consumption, t0 with the public-holiday calendar reduces "
        "day-ahead MAE versus blend_50 by more than 25% over every buildable delivery day of 2025."
    ),
    "target": {"column": "consommation", "grid": "30-minute rows (as data.load_series)", "unit": "MW"},
    "period": {"year": 2025, "days": "every buildable Europe/Paris delivery day"},
    "gate": "12:00 Europe/Paris on D-1, forecasting the whole local day D",
    "t0_arm": {
        "name": "t0_cal",
        "repo_id": "theforecastingcompany/t0-alpha",
        "revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b",
        "context_days": 90,
        "fixed_horizon": 73,
        "covariates": ["French public holidays (fixed dates + Easter-based), timestamps only"],
        "code_path": "run_probes._t0(args, 't0_cal', covariates=(probes.HolidayCovariate(),))",
    },
    "comparator": "blend_50 (chosen by rule on 2023 in Experiment 3; not reselected)",
    "metric": "MAE over all half-hours of the scored days (days where either method is non-finite are dropped)",
    "test": {
        "bootstrap": "paired moving-block, 7-day blocks, 2000 resamples, seed 0 (metrics.bootstrap_skill)",
        "lower_bound": "one-sided 95%: the 5th percentile of the bootstrap skill draws",
    },
    "threshold": 0.25,
    "min_days": 300,
    "min_valid": 0.95,
    "sources": list(SOURCES),
    "source_rule": (
        "use the first source whose consumption is >= 95% valid over the year's half-hours, for the "
        "whole window (context and target); none -> INCONCLUSIVE"
    ),
    "verdicts": {
        "CONFIRMED": "lower bound > 0.25",
        "NOT CONFIRMED": "lower bound <= 0.25",
        "INCONCLUSIVE": "fewer than 300 scored days, or no source passes the rule",
    },
    "reported_only": ["t0 (no calendar) vs blend_50", "t0_cal vs RTE prevision_j1 (reference)"],
    "evidence": "Experiment 3, probe P4 (run #18 at f2dec78): +49.6% [+44.2%, +55.1%] on 2024",
}

#: Committed before any 2025 data was read. Changing CLAIM breaks this on purpose.
FROZEN_CLAIM_SHA256 = "8ed512e1863ca1b74f00c299c8bad15f52104bb8382cd046d504b759aefb8832"


class VaultError(RuntimeError):
    """The sealed period stays closed."""


def claim_sha256(claim: dict = CLAIM) -> str:
    return hashlib.sha256(json.dumps(claim, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SealedAccess:
    """Proof that ``open_sealed`` let this run through; only it creates one."""

    claim_id: str
    claim_sha256: str

    def valid(self) -> bool:
        return (self.claim_id == CLAIM["id"] and self.claim_sha256 == FROZEN_CLAIM_SHA256 == claim_sha256()
                and not _uses(self.claim_id, LEDGER))


def ledger_entries(path: Path = LEDGER) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _uses(claim_id: str, *ledgers: Path) -> list[dict]:
    return [e for path in ledgers for e in ledger_entries(path) if e.get("claim_id") == claim_id]


def open_sealed(*, model_loaded: bool, ledger: Path = LEDGER) -> SealedAccess:
    digest = claim_sha256()
    if digest != FROZEN_CLAIM_SHA256:
        raise VaultError(f"the claim differs from the frozen one ({digest[:12]} != {FROZEN_CLAIM_SHA256[:12]})")
    if not model_loaded:
        raise VaultError("load the pinned model before opening the sealed data")
    used = _uses(CLAIM["id"], LEDGER, ledger)  # the committed ledger always counts
    if used:
        raise VaultError(f"claim {CLAIM['id']} was already tested on the sealed data: {used[0].get('run')}")
    return SealedAccess(claim_id=CLAIM["id"], claim_sha256=digest)


def lower_bound(draws: np.ndarray, level: float = 0.95) -> float:
    """One-sided lower confidence bound: the (1 - level) percentile of the draws."""
    return float(np.percentile(np.asarray(draws, dtype="float64"), 100.0 * (1.0 - level)))


def verdict(lb: float | None, n_days: int, claim: dict = CLAIM) -> str:
    if lb is None or n_days < claim["min_days"]:
        return "INCONCLUSIVE"
    return "CONFIRMED" if lb > claim["threshold"] else "NOT CONFIRMED"


def choose_source(coverage: dict[str, float], claim: dict = CLAIM) -> str | None:
    for source in claim["sources"]:
        if coverage.get(source, 0.0) >= claim["min_valid"]:
            return source
    return None
