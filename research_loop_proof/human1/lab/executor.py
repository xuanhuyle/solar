"""The Human1 lab: Phase 0's executor (``phase0/lab/executor.py``) for the two supplied candidates X01 and X02.

Everything else is Phase 0's, unchanged: the menu (1 to 4 distinct covariates, a disjoint reference of 0 to 2, a window
of the last 7, 14 or 28 revealed days; with two ids that allows 1 or 2 covariates and a reference of 0 or 1), the 7-day
context, the t0 forecast of each scored day from the data through the round's cutoff, and the result fields. ``Lab2``
differs from Phase 0's ``Lab`` only in the candidate ids it reads and validates against (``IDS2`` in place of ``IDS``);
a test checks that its code is Phase 0's with that one substitution.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research_loop_proof.phase0.lab.executor import CONTEXT, H, Lab, block_days, request_errors
from solarbench import metrics

IDS2 = ("X01", "X02")


class Lab2(Lab):
    """Phase 0's ``Lab`` over the two supplied candidates."""

    def __init__(self, observed: dict, instrument):
        self.y = np.asarray(observed["y"], dtype="float64")
        self.x = {i: np.asarray(observed[i], dtype="float64") for i in IDS2}
        self.days = len(self.y) // H
        self.inst = instrument
        self._cache: dict = {}

    def run(self, req: dict, cutoff: int, exp_id: str) -> dict:
        """One experiment on the days revealed through ``cutoff``. ``req`` must be valid (``request_errors``)."""
        if request_errors(req, IDS2):
            raise ValueError(f"invalid experiment {req}")
        if not CONTEXT + 1 <= cutoff <= self.days:
            raise ValueError(f"cutoff {cutoff} outside the observed data")
        win = int(req["window_days"])
        first, last = cutoff - win + 1, cutoff
        days = list(range(first, last + 1))
        ref_ids = tuple(sorted(req["reference"]))
        cand_ids = tuple(sorted(set(req["reference"]) | set(req["covariates"])))
        f_ref, f_cand = self._forecasts(ref_ids, days, cutoff), self._forecasts(cand_ids, days, cutoff)
        rows, e_ref, e_cand = [], [], []
        for d in days:
            actual = self.y[(d - 1) * H:d * H]
            a, b = float(np.abs(f_cand[d] - actual).sum()), float(np.abs(f_ref[d] - actual).sum())
            e_cand.append(a)
            e_ref.append(b)
            rows += [{"delivery_date": d, "method": "candidate", "sum_abs_err": a, "n": H},
                     {"delivery_date": d, "method": "reference", "sum_abs_err": b, "n": H}]
        r = metrics.pair_skill(pd.DataFrame(rows), model="candidate", reference="reference",
                               block_days=block_days(win))
        e_ref, e_cand = np.array(e_ref), np.array(e_cand)
        parts = [float(1.0 - e_cand[i:i + 7].sum() / e_ref[i:i + 7].sum()) for i in range(0, win, 7)]
        return {"id": exp_id, "covariates": list(req["covariates"]), "reference": list(req["reference"]),
                "window_days": win, "scored_days": [first, last],
                "reference_mae": float(e_ref.sum() / (win * H)), "candidate_mae": float(e_cand.sum() / (win * H)),
                "skill": float(r["skill"]), "lo95": float(r["skill_lo95"]), "hi95": float(r["skill_hi95"]),
                "block_days": block_days(win), "wins": int(r["wins"]), "losses": int(r["losses"]),
                "ties": int(r["ties"]), "skill_by_7_days": parts}
