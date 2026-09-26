"""The forward vault: freeze a claim batch, wait for fresh data, open it once, decide.

* ``freeze`` - a batch of at most 4 claims, each naming an arm, a comparator,
  a scope and a margin ``delta``, and citing the exploratory results it rests
  on. The referee attaches its own constants. The batch's window starts 15
  local days after the freeze (the 14-day embargo) and runs 84 days (6 blocks
  of 14). It gets the next share of the ledger's alpha budget (0.05 over 4
  batches); a new freeze is refused while a batch is open or once the budget
  is spent. The researcher then sees a fixed-length receipt only.
* ``open_forward`` - only after the window has ended (plus the data lag), with
  the pinned model loaded, for a batch never opened before, in a run the owner
  approved for the ``engine-vault`` environment. It issues the one
  ``ForwardAccess`` that ``engine.data`` accepts for forward days.
* ``decide`` - per claim, a one-sided block t-test of ``skill > delta`` (14-day
  blocks), Holm across the batch at the batch's alpha. PASS / NOT PASS; the
  full numbers are released once, at closing, and a PASS becomes an accepted
  finding. The window is consumed whatever the outcome.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd

from engine import catalogue as cat
from engine import zones
from engine.canon import sha256_of
from engine.referee import stats

BATCH_VERSION = "claims/0"
EMBARGO_DAYS = 14
WINDOW_DAYS = stats.BLOCK_DAYS * stats.MIN_BLOCKS  # 84
MAX_CLAIMS = 4
DELTAS = (0.0, 0.05, 0.10, 0.20)
DATA_LAG_DAYS = 3  # after the window, before it may be opened (the real-time feed; the source rule decides)
SOURCES = ("eco2mix-national-cons-def", "eco2mix-national-tr")
MIN_VALID = 0.95
CLAIM_FIELDS = {"id", "statement", "target", "arm", "comparator", "scope", "delta", "evidence"}


class VaultError(RuntimeError):
    """The vault stays closed (or refuses a freeze)."""


# ------------------------------------------------------------------ freeze


def _batches(entries: list[dict]) -> tuple[list[dict], set[str], set[str]]:
    freezes = [e for e in entries if e.get("kind") == "freeze"]
    unsealed = {e["payload"]["batch_id"] for e in entries if e.get("kind") == "unseal"}
    decided = {e["payload"]["batch_id"] for e in entries if e.get("kind") == "verdict"}
    return freezes, unsealed, decided


def validate_batch(batch: dict, entries: list[dict]) -> list[dict]:
    """The normalised claims, or VaultError listing every problem."""
    errors: list[str] = []
    if not isinstance(batch, dict) or set(batch) - {"batch_version", "claims"} or batch.get("batch_version") != BATCH_VERSION:
        raise VaultError(f"a batch is {{'batch_version': {BATCH_VERSION!r}, 'claims': [...]}} and nothing else")
    claims = batch.get("claims")
    if not isinstance(claims, list) or not 1 <= len(claims) <= MAX_CLAIMS:
        raise VaultError(f"1..{MAX_CLAIMS} claims required")
    results = {e["seq"]: e["payload"] for e in entries if e.get("kind") == "probe_result"}
    out = []
    for i, c in enumerate(claims):
        w = f"claims[{i}]"
        if not isinstance(c, dict) or set(c) - CLAIM_FIELDS or CLAIM_FIELDS - set(c):
            errors.append(f"{w}: fields must be exactly {sorted(CLAIM_FIELDS)}")
            continue
        if c["target"] not in cat.TARGETS:
            errors.append(f"{w}: unknown target")
        if c["comparator"] not in ("best_simple", "t0_base", "accepted"):
            errors.append(f"{w}: comparator must be best_simple, t0_base or accepted (rte_j1 never decides)")
        if c["scope"] not in cat.SCOPES:
            errors.append(f"{w}: unknown scope")
        if c["delta"] not in DELTAS:
            errors.append(f"{w}: delta must be one of {DELTAS}")
        if not isinstance(c["statement"], str) or not 0 < len(c["statement"]) <= 300:
            errors.append(f"{w}: statement of 1..300 characters")
        covs = c["arm"].get("covariates") if isinstance(c["arm"], dict) else None
        if not isinstance(covs, list) or set(c["arm"]) != {"covariates"}:
            errors.append(f"{w}: arm is {{'covariates': [...]}}")
            covs = []
        for cv in covs:
            entry = cat.COVARIATES.get(cv.get("id")) if isinstance(cv, dict) else None
            if entry is None or c["target"] not in entry["targets"] or cv.get("transform", "raw") not in entry["transforms"]:
                errors.append(f"{w}: covariate {cv} is not in the catalogue for {c['target']}")
        ev = c["evidence"]
        if not isinstance(ev, list) or not ev:
            errors.append(f"{w}: cite at least one probe_result by ledger seq")
        else:
            for seq in ev:
                p = results.get(seq)
                if p is None or not str(p.get("status", "")).startswith("EXPLORATORY") or not p.get("leak_checks_passed", True):
                    errors.append(f"{w}: evidence seq {seq} is not a valid exploratory probe result")
                elif p.get("target") != c["target"]:
                    errors.append(f"{w}: evidence seq {seq} is about another target")
        out.append({"id": f"C{i + 1}", "statement": c["statement"], "target": c["target"],
                    "arm": {"covariates": sorted(({"id": cv["id"], "transform": cv.get("transform", "raw")}
                                                  for cv in covs if isinstance(cv, dict)), key=lambda x: (x["id"], x["transform"]))},
                    "comparator": c["comparator"], "scope": c["scope"], "metric": "mae", "delta": c["delta"],
                    "evidence": sorted(set(ev)) if isinstance(ev, list) else []})
    if errors:
        raise VaultError("; ".join(errors))
    return out


def window_for(frozen_at: datetime) -> tuple[date, date]:
    local = pd.Timestamp(frozen_at).tz_convert(zones.PARIS).date()
    first = local + timedelta(days=EMBARGO_DAYS + 1)
    return first, first + timedelta(days=WINDOW_DAYS - 1)


def freeze(batch: dict, entries: list[dict], frozen_at: datetime, accepted: dict | None = None, *,
           rehearsal: bool = False) -> dict:
    """The freeze payload (which includes the receipt), or VaultError.

    ``rehearsal`` builds the same payload for a past window on consumed data (batch id ``DRY``):
    it spends no alpha, opens nothing and can never be a verdict.
    """
    freezes, _, decided = _batches(entries)
    open_ = [f["payload"]["batch_id"] for f in freezes if f["payload"]["batch_id"] not in decided]
    if open_ and not rehearsal:
        raise VaultError(f"batch {open_[0]} is still open: one batch at a time")
    alpha = stats.alpha_for_batch(0 if rehearsal else len(freezes))
    claims = validate_batch(batch, entries)
    first, last = window_for(frozen_at)
    if rehearsal:
        if zones.zone_of(last) == "forward":
            raise VaultError("a rehearsal must stay in the discovery zone")
    elif not (zones.confirmable(first) and first > pd.Timestamp(frozen_at).date()):
        raise VaultError(f"the window {first}..{last} is not confirmable forward data")
    batch_id = "DRY" if rehearsal else f"B{len(freezes) + 1}"
    frozen = {
        "batch_version": BATCH_VERSION, "batch_id": batch_id, "claims": claims,
        "frozen_at": pd.Timestamp(frozen_at).isoformat(), "window": [first.isoformat(), last.isoformat()],
        "alpha": alpha, "alpha_spent_before": 0.0 if rehearsal else round(len(freezes) * alpha, 6),
        "rehearsal": rehearsal,
        "test": {"kind": "one-sided block t-test of skill > delta", "block_days": stats.BLOCK_DAYS,
                 "min_blocks": stats.MIN_BLOCKS, "multiplicity": "Holm across the batch at alpha"},
        "t0": cat.T0, "source_rule": {"sources": list(SOURCES), "min_valid": MIN_VALID},
        "catalogue_sha256": cat.catalogue_sha256(),
        "accepted_at_freeze": accepted,
    }
    frozen["batch_sha256"] = sha256_of(frozen)
    frozen["receipt"] = {"batch_id": batch_id, "batch_sha256": frozen["batch_sha256"],
                         "window": frozen["window"], "opens_after": (last + timedelta(days=DATA_LAG_DAYS)).isoformat()}
    return frozen


def frozen_batch(entries: list[dict], batch_id: str) -> dict:
    for e in entries:
        if e.get("kind") == "freeze" and e["payload"].get("batch_id") == batch_id:
            p = dict(e["payload"])
            body = {k: v for k, v in p.items() if k not in ("batch_sha256", "receipt")}
            if sha256_of(body) != p["batch_sha256"]:
                raise VaultError(f"batch {batch_id} does not match its freeze hash")
            return p
    raise VaultError(f"no frozen batch {batch_id}")


# ------------------------------------------------------------------ open


_ISSUED: dict[str, object] = {}


def access_is_valid(access) -> bool:
    """Only the exact object ``open_forward`` issued in this process, for a batch not yet closed."""
    return _ISSUED.get(getattr(access, "batch_id", None)) is access


def open_forward(entries: list[dict], batch_id: str, *, now: datetime, model_loaded: bool, approved_by: str | None):
    from engine.data import ForwardAccess

    batch = frozen_batch(entries, batch_id)
    _, unsealed, decided = _batches(entries)
    if batch_id in unsealed or batch_id in decided:
        raise VaultError(f"batch {batch_id} was already opened: a window is used once")
    first, last = (date.fromisoformat(d) for d in batch["window"])
    if pd.Timestamp(now).date() < last + timedelta(days=DATA_LAG_DAYS):
        raise VaultError(f"batch {batch_id} matures on {last + timedelta(days=DATA_LAG_DAYS)}")
    if not model_loaded:
        raise VaultError("load the pinned model before opening the vault")
    if not approved_by:
        raise VaultError("no owner approval of this run for the engine-vault environment")
    read_first = first - timedelta(days=cat.T0["context_days"] + 10)
    access = ForwardAccess(batch_id, batch["batch_sha256"], read_first.isoformat(), last.isoformat())
    _ISSUED[batch_id] = access
    return access, batch


def close(access) -> None:
    _ISSUED.pop(getattr(access, "batch_id", None), None)


# ------------------------------------------------------------------ decide


def decide(batch: dict, per_day: pd.DataFrame, names: dict[str, tuple[str, str]]) -> dict:
    """PASS / NOT PASS per claim. ``names`` maps claim id -> (arm method, comparator method) in ``per_day``."""
    rows, pvals = [], []
    for c in batch["claims"]:
        arm, ref = names[c["id"]]
        test = stats.block_t_test(per_day, arm, ref, c["delta"])
        pd_pair = per_day.loc[per_day["method"].isin([arm, ref])]
        sums = pd_pair.groupby("method")[["sum_abs_err", "n"]].sum()
        skill = None
        if {arm, ref} <= set(sums.index):
            skill = 1.0 - (sums.loc[arm, "sum_abs_err"] / sums.loc[arm, "n"]) / (sums.loc[ref, "sum_abs_err"] / sums.loc[ref, "n"])
        rows.append({"claim": c["id"], "delta": c["delta"], "skill": None if skill is None else round(float(skill), 6),
                     "blocks": test["blocks"], "t": test["t"], "p": test["p"]})
        pvals.append(test["p"])
    adjusted = stats.holm(pvals)
    for r, p in zip(rows, adjusted):
        r["p_holm"] = round(p, 8)
        r["verdict"] = "PASS" if p < batch["alpha"] else "NOT PASS"
    return {"batch_id": batch["batch_id"], "batch_sha256": batch["batch_sha256"], "alpha": batch["alpha"], "claims": rows}
