"""Phase A: can t0-alpha use a covariate that has only just become predictive? (PHASE0_SPEC.md, section 3)

No AI researcher is involved. For each world the change is at day 60; day 60+k is forecast at the end of day
59+k, so a context of L days holds min(k, L) post-change days. Arms: t0 and the matched ridge, each without
covariates and with the emerging driver E only; on the primary set (linear, 7-day context) also with the noise
candidate N only, a placebo with the same number of covariate rows as {E}.

    python -m research_loop_proof.phase0.truth.phase_a --mode smoke|run --out DIR [--fake-model]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from research_loop_proof.phase0.lab.instruments import T0, ridge_forecast, window
from research_loop_proof.phase0.truth.calibrate import calibrate
from research_loop_proof.phase0.truth.generator import WORLD, World, make_world, seed_of
from research_loop_proof.phase0.truth.spec import file_hashes, spec_sha
from solarbench import metrics

REPO, REVISION = "theforecastingcompany/t0-alpha", "9b02c5f4bb6c89ba15d9fa74554018fe6464220b"
PA = WORLD["phase_a"]
BINS_7 = [(0, 0), (1, 3), (4, 6), (7, 13), (14, 20)]
BINS_28 = [(0, 0), (1, 3), (4, 6), (7, 13), (14, 27), (28, 41)]
BOOT, BOOT_SEED = 2000, 0
C3_BLOCK_DAYS = 2  # pair_skill block length for the 14-day window (7-day blocks: null rate 16.8%, see the spec)
# (name, model arm, reference arm). C1-C3 must hold for both gate comparisons: E against none is the incremental
# value asked about (and what a researcher's experiment against an empty reference measures); E against N removes a
# change that any one covariate row would cause (an untrained model showed one in the dry run).
GATE = (("E_vs_none", "E", "none"), ("E_vs_N", "E", "N"))
COMPARISONS = GATE + (("N_vs_none", "N", "none"),)
# (name, form, context days, last k, arms); the world count comes from world.json.
SETS = (("linear_L7", "linear", 7, 20, ("none", "E", "N")), ("hinge_L7", "hinge", 7, 20, ("none", "E")),
        ("linear_L28", "linear", 28, 41, ("none", "E")))


def load_model():
    from solarbench import t0_pinned

    model, record = t0_pinned.load(REPO, REVISION)
    return model, record


def fake_model():
    """A tiny random t0 (tests and dry runs only; its numbers mean nothing)."""
    import torch
    from t0 import T0Forecaster

    torch.manual_seed(0)
    return T0Forecaster(embed_dim=16, num_layers=1, num_heads=2, mlp_hidden_dim=32, patch_size=16, group_every_n=1,
                        dropout=0.0, quantile_levels=[0.1, 0.25, 0.5, 0.75, 0.9]).eval(), {"fake": True}


def worlds(form: str, n: int) -> list[World]:
    m = WORLD["calibration"]["m"]
    return [make_world(seed_of(f"phase0-A-{form}-{i}"), n_days=PA["n_days"], tau=PA["tau"], form=form, m=m,
                       e_sign=1 if i % 2 == 0 else -1) for i in range(n)]


def t0_errors(inst: T0, ws: list[World], context: int, kmax: int, roles: list[str]) -> np.ndarray:
    """Sum of absolute errors over the 24 hours of each forecast day: shape [worlds, kmax+1]."""
    reqs, truths = [], []
    for w in ws:
        for k in range(kmax + 1):
            day = w.tau + k
            reqs.append(window(w.y, [w.x[r] for r in roles], day, context))
            truths.append(w.y[w.day_slice(day, day)])
    preds = inst.forecast(reqs)
    err = np.array([np.abs(p - t).sum() for p, t in zip(preds, truths)])
    return err.reshape(len(ws), kmax + 1)


def ridge_errors(ws: list[World], context: int, kmax: int, roles: list[str]) -> np.ndarray:
    out = np.empty((len(ws), kmax + 1))
    for i, w in enumerate(ws):
        for k in range(kmax + 1):
            day = w.tau + k
            f = ridge_forecast(w.y, [w.x[r] for r in roles], day, context, square=context == 28)
            out[i, k] = np.abs(f - w.y[w.day_slice(day, day)]).sum()
    return out


def cluster_skill(e_with: np.ndarray, e_without: np.ndarray, k0: int, k1: int) -> dict:
    """Pooled skill over k0..k1 with a 95% bootstrap interval over worlds (worlds resampled)."""
    a, b = e_with[:, k0:k1 + 1].sum(1), e_without[:, k0:k1 + 1].sum(1)
    point = 1.0 - a.sum() / b.sum()
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, len(a), size=(BOOT, len(a)))
    draws = 1.0 - a[idx].sum(1) / b[idx].sum(1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    # unrounded: every threshold is tested on these values; rounding is for display only
    return {"k": [k0, k1], "skill": float(point), "lo95": float(lo), "hi95": float(hi),
            "worlds": int(len(a)), "days": int(len(a) * (k1 - k0 + 1))}


def per_world_pairs(e_with: np.ndarray, e_without: np.ndarray, k0: int, k1: int) -> list[dict]:
    """``metrics.pair_skill`` on each world's window k0..k1 alone (2-day blocks, seed 0)."""
    out = []
    for i in range(e_with.shape[0]):
        rows = []
        for k in range(k0, k1 + 1):
            rows.append({"delivery_date": k, "method": "with", "sum_abs_err": e_with[i, k], "n": 24})
            rows.append({"delivery_date": k, "method": "without", "sum_abs_err": e_without[i, k], "n": 24})
        r = metrics.pair_skill(pd.DataFrame(rows), model="with", reference="without", block_days=C3_BLOCK_DAYS)
        out.append({"skill": float(r["skill"]), "lo95": float(r["skill_lo95"]), "hi95": float(r["skill_hi95"])})
    return out


def curve(e_with, e_without, bins) -> list[dict]:
    return [cluster_skill(e_with, e_without, k0, k1) for k0, k1 in bins]


def how_soon(rows: list[dict]) -> str:
    """The earliest bin (control k = 0 excluded) from which every later bin has a lower bound above 0."""
    later = [r for r in rows if r["k"][0] > 0]
    for i, r in enumerate(later):
        if all(x["lo95"] > 0 for x in later[i:]):
            return f"k = {r['k'][0]}-{r['k'][1]}"
    return "never within the measured range"


def _criteria(e_with, e_without) -> dict:
    c1 = cluster_skill(e_with, e_without, 7, 20)
    c2 = cluster_skill(e_with, e_without, 1, 6)
    pairs = per_world_pairs(e_with, e_without, 7, 20)
    n_pos = sum(p["lo95"] > 0 for p in pairs)
    return {
        "C1": {"rule": "skill over k = 7-20 >= 0.05 and lower bound > 0", **c1,
               "pass": bool(c1["skill"] >= 0.05 and c1["lo95"] > 0)},
        "C2": {"rule": "skill over k = 1-6 has lower bound > 0", **c2, "pass": bool(c2["lo95"] > 0)},
        "C3": {"rule": "in >= 20 of 40 worlds the k = 7-20 window alone has pair_skill lower bound > 0",
               "worlds_with_lb_above_0": int(n_pos), "of": len(pairs), "per_world": pairs, "pass": bool(n_pos >= 20)},
    }


def criteria(arms: dict, instrument: str) -> dict:
    """C1-C3 on the primary set for each gate comparison; a criterion passes only if it passes for both."""
    by = {cmp: _criteria(arms[f"{instrument}_{m}"], arms[f"{instrument}_{r}"]) for cmp, m, r in GATE}
    return {"by_comparison": by, "pass": {c: all(by[cmp][c]["pass"] for cmp in by) for c in ("C1", "C2", "C3")}}


def poison_check(inst: T0, w: World, context: int) -> dict:
    """Target values after the forecast origin and covariate values after the forecast day set to NaN must leave
    single-row forecasts bit-identical."""
    out = []
    for k in (3, 10, 17):
        day = w.tau + k
        clean = inst.forecast([window(w.y, [w.x["E"]], day, context)])[0]
        y, xe = w.y.copy(), w.x["E"].copy()
        y[(day - 1) * 24:] = np.nan
        xe[day * 24:] = np.nan
        poisoned = inst.forecast([window(y, [xe], day, context)])[0]
        out.append(bool(np.array_equal(clean, poisoned)))
    return {"origins_k": [3, 10, 17], "identical": out, "pass": all(out)}


def timing(inst: T0, w: World, context: int, roles: list[str], rows: int = 32) -> float:
    reqs = [window(w.y, [w.x[r] for r in roles], w.tau + (i % 20), context) for i in range(rows)]
    t = time.perf_counter()
    inst.forecast(reqs)
    return (time.perf_counter() - t) / rows


def run(out: Path, *, fake: bool = False, smoke: bool = False) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    model, load_record = fake_model() if fake else load_model()
    inst = T0(model)
    cal = calibrate()
    frozen_cal = WORLD["calibration"]
    cal_ok = cal["m"] == frozen_cal["m"] and [a["median"] for a in cal["attempts"]] == \
        [a["median"] for a in frozen_cal["record"]["attempts"]]
    cal_world = make_world(seed_of("phase0-cal-0"), n_days=WORLD["calibration"]["n_days"], tau=60, form="linear",
                           m=frozen_cal["m"])
    secs = {f"L{L}_K{len(r)}": round(timing(inst, cal_world, L, r), 4) for L in (7, 28) for r in ([], ["E"])}
    n28 = PA["l28_worlds"]
    record = {"phase": "A", "spec_sha": spec_sha(), "frozen_files": file_hashes(), "load": load_record,
              "calibration_reproduced": cal_ok, "calibration": cal, "seconds_per_forecast_day": secs,
              "l28_worlds": n28, "e_signs": PA["e_sign_rule"], "fake_model": fake,
              "run_id": os.environ.get("GITHUB_RUN_ID"),
              "commit": os.environ.get("GITHUB_SHA")}
    if smoke:
        finite = bool(np.all(np.isfinite(inst.forecast([window(cal_world.y, [cal_world.x["E"]], 70, 7)])[0])))
        record.update({"mode": "smoke", "finite": finite, "sanitised": inst.sanitised,
                       "t0_forecasts_total": inst.rows, "elapsed_s": round(time.time() - started, 1)})
        (out / "smoke.json").write_text(json.dumps(record, indent=1) + "\n")
        return record

    lin, hin = worlds("linear", PA["linear_worlds"]), worlds("hinge", PA["hinge_worlds"])
    world_sets = {"linear_L7": lin, "hinge_L7": hin, "linear_L28": lin[:n28]}
    arms, curves = {}, {}
    for name, _form, L, kmax, labels in SETS:
        ws = world_sets[name]
        arms[name] = {f"{inst_name}_{label}": fn(ws, L, kmax, [] if label == "none" else [label])
                      for inst_name, fn in (("t0", lambda *a: t0_errors(inst, *a)), ("ridge", ridge_errors))
                      for label in labels}
        a, bins = arms[name], (BINS_28 if L == 28 else BINS_7)
        cmps = [c for c in COMPARISONS if c[1] in labels and c[2] in labels]
        curves[name] = {f"{i}_{cmp}": curve(a[f"{i}_{m}"], a[f"{i}_{r}"], bins) for i in ("t0", "ridge")
                        for cmp, m, r in cmps}
        curves[name]["mae"] = {arm: [round(float(v), 4) for v in a[arm].mean(0) / 24] for arm in a}
        curves[name]["how_soon"] = {f"{i}_{cmp}": how_soon(curves[name][f"{i}_{cmp}"]) for i in ("t0", "ridge")
                                    for cmp, m, r in cmps if cmp != "N_vs_none"}
    t0_forecast_days = sum(v.size for a in arms.values() for arm, v in a.items() if arm.startswith("t0_"))
    curves_mae = {name: {arm: [float(v[:, k0:k1 + 1].sum() / (v.shape[0] * (k1 - k0 + 1) * 24))
                               for k0, k1 in (BINS_28 if L == 28 else BINS_7)] for arm, v in arms[name].items()}
                  for name, _f, L, _k, _l in SETS}
    crit = criteria(arms["linear_L7"], "t0")
    ridge_crit = criteria(arms["linear_L7"], "ridge")
    poison = poison_check(inst, lin[0], 7)
    control = {cmp: curves["linear_L7"][f"t0_{cmp}"][0] for cmp, _m, _r in COMPARISONS}
    integrity = {"calibration_reproduced": cal_ok, "sanitised_outputs": inst.sanitised, "poison": poison["pass"]}
    integrity_ok = cal_ok and inst.sanitised == 0 and poison["pass"]
    passed = all(crit["pass"].values())
    verdict = ("INTEGRITY FAILURE (no verdict)" if not integrity_ok else
               "PASS" if passed else "INSTRUMENT FEASIBILITY FAILED")
    record.update({
        "mode": "run", "verdict": verdict, "criteria": crit, "ridge_on_same_criteria": ridge_crit,
        "curves": curves, "control_k0": {cmp: {**c, "warning": c["lo95"] > 0} for cmp, c in control.items()},
        "poison": poison, "integrity": integrity, "mae_by_bin": curves_mae,
        "t0_forecast_days": int(t0_forecast_days), "t0_forecasts_total": inst.rows,
        "elapsed_s": round(time.time() - started, 1),
        "raw_day_errors": {n: {arm: np.round(v, 6).tolist() for arm, v in a.items()} for n, a in arms.items()},
    })
    (out / "phase_a.json").write_text(json.dumps(record, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({"phase": "A", "verdict": verdict, "spec_sha": record["spec_sha"],
                                                  "run_id": record["run_id"], "commit": record["commit"]}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(record), encoding="utf-8")
    return record


def _fmt(r: dict) -> str:
    return f"{r['skill'] * 100:+.1f}% [{r['lo95'] * 100:+.1f}, {r['hi95'] * 100:+.1f}]"


def report(rec: dict) -> str:
    lines = [f"# Phase A result: {rec['verdict']}", "",
             f"spec_sha `{rec['spec_sha']}`; run {rec['run_id']}; commit {rec['commit']}; "
             f"t0 forecast-days {rec['t0_forecast_days']} scored ({rec['t0_forecasts_total']} t0 forecasts in all, "
             f"timing and poison check included); elapsed {rec['elapsed_s']} s.", "",
             "## Competence criterion (linear worlds, 7-day context)", ""]
    for c in ("C1", "C2", "C3"):
        parts = []
        for cmp, block in rec["criteria"]["by_comparison"].items():
            x = block[c]
            parts.append(f"{cmp.replace('_vs_', ' vs ')} " + (f"{x['worlds_with_lb_above_0']} of {x['of']} worlds"
                                                             if c == "C3" else _fmt(x)))
        rule = next(iter(rec["criteria"]["by_comparison"].values()))[c]["rule"]
        lines.append(f"- **{c}** ({rule}; both comparisons): " + "; ".join(parts) +
                     f" - {'pass' if rec['criteria']['pass'][c] else 'FAIL'}")
    lines += ["", "Ridge on the same criteria: " + "; ".join(
        f"{c} {'pass' if ok else 'fail'}" for c, ok in rec["ridge_on_same_criteria"]["pass"].items()), ""]
    for name, cv in rec["curves"].items():
        cols = [k for k in cv if k.startswith("t0_")]
        cols += [k for k in cv if k.startswith("ridge_")]
        lines += [f"## {name}: skill by days since the change (k)", "",
                  "| k | days | " + " | ".join(c.replace("_vs_", " vs ").replace("_", " ") for c in cols) + " |",
                  "|---|---|" + "---|" * len(cols)]
        for j, t in enumerate(cv[cols[0]]):
            lines.append(f"| {t['k'][0]}-{t['k'][1]} | {t['days']} | " + " | ".join(_fmt(cv[c][j]) for c in cols) + " |")
        lines += ["", "How soon (every later bin's lower bound above 0): " + "; ".join(
            f"{k.replace('_vs_', ' vs ').replace('_', ' ')} {v}" for k, v in cv["how_soon"].items()) + ".", ""]
        mae = rec["mae_by_bin"][name]
        lines += [f"Mean absolute error by bin, each arm on its own ({name}):", "",
                  "| k | " + " | ".join(a.replace("_", " ") for a in mae) + " |", "|---|" + "---|" * len(mae)]
        for j, t in enumerate(cv[cols[0]]):
            lines.append(f"| {t['k'][0]}-{t['k'][1]} | " + " | ".join(f"{mae[a][j]:.3f}" for a in mae) + " |")
        lines.append("")
    lines += ["Control k = 0 (no post-change day in context): " + "; ".join(
        f"t0 {cmp.replace('_vs_', ' vs ')} {_fmt(c)}" + (" (warning: lower bound above 0)" if c["warning"] else "")
        for cmp, c in rec["control_k0"].items()), f"Integrity: {rec['integrity']}", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "run"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fake-model", action="store_true")
    args = ap.parse_args(argv)
    rec = run(Path(args.out), fake=args.fake_model, smoke=args.mode == "smoke")
    print(json.dumps({k: rec[k] for k in ("mode", "spec_sha", "seconds_per_forecast_day", "l28_worlds")
                      if k in rec} | ({"verdict": rec["verdict"]} if "verdict" in rec else {})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
