"""The forward vault: freeze a claim batch, wait for fresh data, open it once, decide.

* ``freeze`` - a batch of at most 4 claims on one target, each naming an arm, a
  comparator, a scope and a margin ``delta``, and citing the exploratory result
  that tested exactly that arm against that comparator. Weather covariates need
  a passed known-answer gate; ``accepted`` needs an accepted finding. The window
  starts 15 local days after the freeze (the 14-day embargo) and runs 168 days
  (12 blocks of 14); every block must hold at least 10 in-scope days. The batch
  gets the next share of the ledger's alpha budget (0.05 over 4 batches); a new
  freeze is refused while a batch is open or once the budget is spent. The
  researcher then sees a fixed-length receipt only.
* ``open_forward`` - only after the window has ended (plus the data lag), with
  the pinned model loaded, for a batch never opened before, in a run the owner
  approved for the ``engine-vault`` environment. It issues the one
  ``ForwardAccess`` that ``engine.data`` accepts for forward days.
* ``decide`` - per claim, a one-sided block t-test of ``skill > delta`` over the
  window's calendar blocks (at least 10 of 12), Holm across the whole batch at
  its alpha; a claim that could not be scored stays in the family at p = 1.
  PASS / NOT PASS; the full numbers are released once, at closing. The window
  is consumed whatever happens: an opened batch is closed even if scoring
  crashes (a VOID verdict).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd

from engine import catalogue as cat
from engine import claims as cl
from engine import gates as gates_mod
from engine import zones
from engine.canon import sha256_of
from engine.findings import latest_accepted
from engine.ledger import schema_sha256 as ledger_schema
from engine.referee import stats

BATCH_VERSION = cl.BATCH_VERSION
EMBARGO_DAYS = cl.EMBARGO_DAYS
WINDOW_BLOCKS = cl.WINDOW_BLOCKS
MIN_WINDOW_BLOCKS = cl.MIN_WINDOW_BLOCKS
WINDOW_DAYS = cl.WINDOW_DAYS  # 168 (owner's choice, 2026-09-26)
MAX_CLAIMS = cl.MAX_CLAIMS
DELTAS = cl.DELTAS
DATA_LAG_DAYS = 3  # after the window, before it may be opened (the real-time feed; the source rule decides)
SOURCES = ("eco2mix-national-cons-def", "eco2mix-national-tr")
MIN_VALID = 0.95
WEATHER = cl.WEATHER
window_for = cl.window_for
scope_days_per_block = cl.scope_days_per_block


class VaultError(RuntimeError):
    """The vault stays closed (or refuses a freeze)."""


# ------------------------------------------------------------------ freeze


_batches = cl.batches
open_batches = cl.open_batches


def validate_batch(batch, entries: list[dict], *, gates: set[tuple[str, str]], first: date | None = None) -> list[dict]:
    """The normalised claims, or VaultError listing every problem (the same checks the researcher runs)."""
    errors = cl.structure_errors(batch)
    if not errors:
        errors = cl.ledger_errors(batch, entries, gates=gates, first=first)
    if errors:
        raise VaultError("; ".join(errors))
    return cl.normalise(batch)


def freeze(batch, entries: list[dict], frozen_at: datetime, *, gates: set[tuple[str, str]],
           submitted_by: str = "", rehearsal: bool = False) -> dict:
    """The freeze payload (which includes the receipt), or VaultError.

    ``rehearsal`` builds the same payload for a past window on consumed data (batch id ``DRY``):
    it spends no alpha, opens nothing and can never be a verdict.
    """
    freezes, _, _ = _batches(entries)
    if open_batches(entries) and not rehearsal:
        raise VaultError(f"batch {open_batches(entries)[0]} is still open: one batch at a time")
    alpha = stats.alpha_for_batch(0 if rehearsal else len(freezes))
    first, last = window_for(frozen_at)
    claims = validate_batch(batch, entries, gates=gates, first=first)
    if rehearsal:
        if zones.zone_of(last) == "forward":
            raise VaultError("a rehearsal must stay in the discovery zone")
    elif not (zones.confirmable(first) and first > pd.Timestamp(frozen_at).date()):
        raise VaultError(f"the window {first}..{last} is not confirmable forward data")
    target = claims[0]["target"]
    batch_id = "DRY" if rehearsal else f"B{len(freezes) + 1}"
    frozen = {
        "batch_version": BATCH_VERSION, "batch_id": batch_id, "claims": claims, "target": target,
        "submitted_by": submitted_by,
        "frozen_at": pd.Timestamp(frozen_at).isoformat(), "window": [first.isoformat(), last.isoformat()],
        "alpha": alpha, "alpha_spent_before": 0.0 if rehearsal else round(len(freezes) * alpha, 6),
        "rehearsal": rehearsal,
        "test": {"kind": "one-sided block t-test of skill > delta", "block_days": stats.BLOCK_DAYS,
                 "blocks": f"{WINDOW_BLOCKS} calendar spans from the window's first day",
                 "min_days_per_block": stats.MIN_DAYS_PER_BLOCK, "min_blocks": MIN_WINDOW_BLOCKS,
                 "multiplicity": "Holm across the batch at alpha; an unscorable claim stays in at p = 1"},
        "t0": cat.T0, "source_rule": {"sources": list(SOURCES), "min_valid": MIN_VALID},
        "catalogue_sha256": cat.catalogue_sha256(), "gate_fingerprint": gates_mod.gate_fingerprint(),
        "ledger_schema": ledger_schema(),
        "accepted_at_freeze": {target: latest_accepted(entries, target)},
        "ledger_head_seq": entries[-1]["seq"] if entries else -1,
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
    if batch.get("rehearsal"):
        raise VaultError("a rehearsal batch never opens the vault")
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


def _common_skill(per_day: pd.DataFrame, arm: str, ref: str) -> float | None:
    sub = per_day.loc[per_day["method"].isin([arm, ref])]
    if sub.empty:
        return None
    wide = sub.pivot(index="delivery_date", columns="method", values="sum_abs_err")
    n = sub.pivot(index="delivery_date", columns="method", values="n")
    if not {arm, ref} <= set(wide.columns):
        return None
    common = wide[[arm, ref]].dropna().index
    if not len(common):
        return None
    m_arm = wide.loc[common, arm].sum() / n.loc[common, arm].sum()
    m_ref = wide.loc[common, ref].sum() / n.loc[common, ref].sum()
    return float(1.0 - m_arm / m_ref)


def decide(batch: dict, per_day: pd.DataFrame, names: dict[str, tuple[str, str]],
           errors: dict[str, str] | None = None) -> dict:
    """PASS / NOT PASS per claim. ``names`` maps claim id -> (arm method, comparator method) in ``per_day``;
    a claim in ``errors`` (or missing from ``names``) is unscorable: p = 1, kept in the Holm family."""
    errors = dict(errors or {})
    rows, pvals = [], []
    for c in batch["claims"]:
        row = {"claim": c["id"], "delta": c["delta"]}
        if c["id"] in errors or c["id"] not in names:
            row.update({"skill": None, "blocks": 0, "t": None, "p": 1.0,
                        "error": errors.get(c["id"], "not scored")})
        else:
            arm, ref = names[c["id"]]
            test = stats.block_t_test(per_day, arm, ref, c["delta"], start=batch["window"][0],
                                      n_blocks=WINDOW_BLOCKS, min_blocks=MIN_WINDOW_BLOCKS)
            skill = _common_skill(per_day, arm, ref)
            row.update({"skill": None if skill is None else round(skill, 6), "blocks": test["blocks"],
                        "t": test["t"], "p": test["p"]})
        rows.append(row)
        pvals.append(row["p"])
    adjusted = stats.holm(pvals)
    for r, p in zip(rows, adjusted):
        r["p_holm"] = round(p, 8)
        r["verdict"] = "PASS" if p < batch["alpha"] else "NOT PASS"
    return {"batch_id": batch["batch_id"], "batch_sha256": batch["batch_sha256"], "alpha": batch["alpha"], "claims": rows}


def void_verdict(batch: dict, error: str) -> dict:
    """The verdict of an opened batch whose scoring failed: every claim NOT PASS. The window stays consumed."""
    out = decide(batch, pd.DataFrame(columns=["delivery_date", "method", "sum_abs_err", "n"]), {},
                 {c["id"]: f"VOID: {error}" for c in batch["claims"]})
    out["void"] = True
    return out
