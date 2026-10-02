"""The frozen calibration rule (world.json "calibration"): ridge only, never t0.

On 3 fixed calibration worlds (linear, change at day 60), the information-matched ridge with a 7-day context
forecasts days 60+7 .. 60+20 with and without E. The measure is the median over worlds of the pooled skill of
ridge{E} against ridge{}. m = 1 if it lies in [0.20, 0.40]; otherwise one step, to m = 2 if below or m = 0.5 if
above, and the stepped m is used whatever it measures. Every attempt is returned for the record.

    python -m research_loop_proof.phase0.truth.calibrate
"""
from __future__ import annotations

import json
import sys

import numpy as np

from research_loop_proof.phase0.lab.instruments import ridge_forecast
from research_loop_proof.phase0.truth.generator import WORLD, make_world, seed_of

CAL = WORLD["calibration"]


def measure(m: float) -> dict:
    per_world = []
    for i in range(CAL["worlds"]):
        w = make_world(seed_of(f"phase0-cal-{i}"), n_days=CAL["n_days"], tau=CAL["tau"], form=CAL["form"], m=m)
        err_with = err_without = 0.0
        for k in range(7, 21):
            day = w.tau + k
            truth = w.y[w.day_slice(day, day)]
            err_without += np.abs(ridge_forecast(w.y, [], day, CAL["context_days"]) - truth).sum()
            err_with += np.abs(ridge_forecast(w.y, [w.x["E"]], day, CAL["context_days"]) - truth).sum()
        per_world.append(1.0 - err_with / err_without)
    return {"m": m, "per_world_skill": [round(s, 4) for s in per_world], "median": round(float(np.median(per_world)), 4)}


def calibrate() -> dict:
    first = measure(1.0)
    attempts = [first]
    if 0.20 <= first["median"] <= 0.40:
        m = 1.0
    else:
        m = 2.0 if first["median"] < 0.20 else 0.5
        attempts.append(measure(m))
    return {"m": m, "attempts": attempts}


if __name__ == "__main__":
    json.dump(calibrate(), sys.stdout, indent=1)
    print()
