"""The lab's experiment executor for Phase B (PHASE0_SPEC.md section 4, lab/menu.json).

It sees only the observed data (the target and the anonymous candidates X01-X04 for days 1-126) and, for each round,
a copy truncated at that round's cutoff day. An experiment names covariates, a reference (disjoint) and a window of
the last 7, 14 or 28 revealed days; each scored day d is forecast at the end of day d-1 from days d-7..d-1 with t0.
The candidate arm uses reference + covariates, the reference arm the reference only, the covariate rows in id order.
The result carries the menu's fields only (no raw values). A forecast depends only on its covariate set and its day
(context and covariates up to that day), so identical forecasts are computed once and reused.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_loop_proof.phase0.lab.instruments import window
from solarbench import metrics

HERE = Path(__file__).resolve().parent
MENU = json.loads((HERE / "menu.json").read_text(encoding="utf-8"))
IDS = tuple(MENU["candidates"])
H = MENU["horizon_hours"]
CONTEXT = MENU["context_days"]
WINDOWS = tuple(MENU["experiment"]["window_days"])


def block_days(window_days: int) -> int:
    """The menu's interval rule: blocks of min(2, window_days // 7) days."""
    return min(2, window_days // 7)


def request_errors(req, known_ids=IDS) -> list[str]:
    """Why a requested experiment is not valid (empty when it is)."""
    if not isinstance(req, dict):
        return ["an experiment must be an object"]
    errs = []
    cov, ref, win = req.get("covariates"), req.get("reference"), req.get("window_days")
    if not isinstance(cov, list) or not 1 <= len(cov) <= 4 or len(set(map(str, cov))) != len(cov):
        errs.append("covariates must be 1 to 4 distinct candidate ids")
    elif any(c not in known_ids for c in cov):
        errs.append(f"unknown covariate id in {cov}")
    if not isinstance(ref, list) or len(ref) > 2 or len(set(map(str, ref))) != len(ref):
        errs.append("reference must be 0 to 2 distinct candidate ids")
    elif any(c not in known_ids for c in ref):
        errs.append(f"unknown reference id in {ref}")
    if isinstance(cov, list) and isinstance(ref, list) and set(map(str, cov)) & set(map(str, ref)):
        errs.append("covariates and reference must be disjoint")
    if win not in WINDOWS or isinstance(win, bool):
        errs.append(f"window_days must be one of {list(WINDOWS)}")
    return errs


class Lab:
    """Runs experiments on the observed arrays with a forecasting instrument (``T0`` or a stand-in)."""

    def __init__(self, observed: dict, instrument):
        self.y = np.asarray(observed["y"], dtype="float64")
        self.x = {i: np.asarray(observed[i], dtype="float64") for i in IDS}
        self.days = len(self.y) // H
        self.inst = instrument
        self._cache: dict = {}

    def _forecasts(self, ids: tuple, days: list[int], cutoff: int) -> dict:
        """24-hour forecasts of each day from the data truncated at ``cutoff``, computed once per (ids, day)."""
        y = self.y[:cutoff * H]
        xs = [self.x[i][:cutoff * H] for i in ids]
        missing = [d for d in days if (ids, d) not in self._cache]
        if missing:
            preds = self.inst.forecast([window(y, xs, d, CONTEXT) for d in missing])
            for d, p in zip(missing, preds):
                self._cache[(ids, d)] = np.asarray(p, dtype="float64")
        return {d: self._cache[(ids, d)] for d in days}

    def run(self, req: dict, cutoff: int, exp_id: str) -> dict:
        """One experiment on the days revealed through ``cutoff``. ``req`` must be valid (``request_errors``)."""
        if request_errors(req):
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


def render_result(res: dict) -> str:
    """The result as the researcher reads it (the menu's fields; no raw values)."""
    def pct(v):
        return f"{v * 100:+.1f}%"
    note = " (indicative: window under 14 days)" if res["window_days"] < 14 else ""
    return (f"scored days {res['scored_days'][0]}-{res['scored_days'][1]}; reference MAE {res['reference_mae']:.3f}; "
            f"candidate MAE {res['candidate_mae']:.3f}; skill {pct(res['skill'])} (95% interval {pct(res['lo95'])} "
            f"to {pct(res['hi95'])}{note}); days won/lost/tied {res['wins']}/{res['losses']}/{res['ties']}; "
            f"skill per 7-day part: {', '.join(pct(p) for p in res['skill_by_7_days'])}")


def arrays_sha256(arrays: dict) -> str:
    """sha256 over the raw bytes of the arrays in key order (the same rule as the generator's export hash)."""
    import hashlib

    h = hashlib.sha256()
    for key in sorted(arrays):
        a = np.ascontiguousarray(arrays[key], dtype="float64")
        h.update(key.encode() + b"\0" + str(a.shape).encode() + b"\0" + a.tobytes())
    return h.hexdigest()


def load_observed(path) -> dict:
    with np.load(path) as z:
        return {k: np.array(z[k]) for k in z.files}
