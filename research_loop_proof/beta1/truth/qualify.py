"""Minimal t0-beta qualification (NEXT_MILESTONE_PROMPT.md section 3). Not a benchmark.

It asks only: does t0-beta load reproducibly, accept known-future covariates, give finite and non-degenerate
forecasts, and show a clearly positive signal from the emerging covariate in a few post-change cases? Worlds: Phase
A's linear worlds 0-7 from the frozen Phase 0 generator (E's sign balanced, change at day 60, 7-day context), arms
{} / {E} / {N}, days k = 1-3 and 7-13 after the change (240 forecasts). The rules below are fixed before the run:

- Q1 reproducible: a second load of the same verified files gives bit-identical forecasts on 16 requests.
- Q2 covariates accepted: forecasts with 1 and with 2 covariate rows run and have 24 values.
- Q3 finite, non-degenerate: no non-finite output (none sanitised); every forecast has an hourly sd above 0.05;
  {E} forecasts differ from {} forecasts.
- Q4 clear signal: over k = 7-13, pooled skill of {E} vs {} and of {E} vs {N} each above 10%, and {E} beats {} in at
  least 6 of the 8 worlds. (k = 1-3 is reported only.)

PASS when Q1-Q4 all hold; otherwise BETA NOT VIABLE (and t0-alpha is retained).

    python -m research_loop_proof.beta1.truth.qualify --weights DIR --out DIR
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.phase0.lab.instruments import window
from research_loop_proof.phase0.truth.phase_a import worlds

WORLDS, CONTEXT = 8, 7
K_EARLY, K_POST = (1, 2, 3), tuple(range(7, 14))
RULES = {"Q3_hourly_sd_min": 0.05, "Q4_pooled_skill_min": 0.10, "Q4_worlds_positive_min": 6}


def _errors(inst, ws, ks, roles):
    reqs, truths = [], []
    for w in ws:
        for k in ks:
            day = w.tau + k
            reqs.append(window(w.y, [w.x[r] for r in roles], day, CONTEXT))
            truths.append(w.y[w.day_slice(day, day)])
    preds = inst.forecast(reqs)
    err = np.array([np.abs(p - t).sum() for p, t in zip(preds, truths)]).reshape(len(ws), len(ks))
    return err, preds


def checks(inst, inst2, ws) -> dict:
    out = {}
    probe = [window(w.y, [w.x["E"]], w.tau + k, CONTEXT) for w in ws[:4] for k in (2, 9, 12, 13)]
    a, b = inst.forecast(probe), inst2.forecast(probe)
    out["Q1"] = {"rule": "a second load gives bit-identical forecasts on 16 requests",
                 "pass": bool(all(np.array_equal(x, y) for x, y in zip(a, b)))}
    w = ws[0]
    two = inst.forecast([window(w.y, [w.x["E"], w.x["N"]], w.tau + 9, CONTEXT)])[0]
    one = inst.forecast([window(w.y, [w.x["E"]], w.tau + 9, CONTEXT)])[0]
    out["Q2"] = {"rule": "1 and 2 covariate rows accepted, 24 values each",
                 "pass": bool(one.shape == (24,) and two.shape == (24,))}
    arms, preds = {}, {}
    for label, roles in (("none", []), ("E", ["E"]), ("N", ["N"])):
        for name, ks in (("early", K_EARLY), ("post", K_POST)):
            arms[(label, name)], preds[(label, name)] = _errors(inst, ws, ks, roles)
    allp = [p for v in preds.values() for p in v]
    finite = all(np.isfinite(p).all() for p in allp)
    min_sd = float(min(np.std(p) for p in allp))
    moved = float(max(np.abs(x - y).max() for x, y in zip(preds[("E", "post")], preds[("none", "post")])))
    out["Q3"] = {"rule": "finite, none sanitised, hourly sd > 0.05 for every forecast, {E} differs from {}",
                 "finite": finite, "sanitised": inst.sanitised + inst2.sanitised, "min_hourly_sd": round(min_sd, 4),
                 "max_abs_change_from_E": round(moved, 4),
                 "pass": bool(finite and inst.sanitised + inst2.sanitised == 0 and min_sd > RULES["Q3_hourly_sd_min"]
                              and moved > 1e-6)}

    def skill(m, r, name):
        return float(1.0 - arms[(m, name)].sum() / arms[(r, name)].sum())

    per_world = 1.0 - arms[("E", "post")].sum(1) / arms[("none", "post")].sum(1)
    q4 = {"skill_E_vs_none": skill("E", "none", "post"), "skill_E_vs_N": skill("E", "N", "post"),
          "worlds_E_beats_none": int((per_world > 0).sum()), "per_world_skill": [round(float(s), 4) for s in per_world]}
    q4["pass"] = bool(q4["skill_E_vs_none"] > RULES["Q4_pooled_skill_min"] and q4["skill_E_vs_N"] >
                      RULES["Q4_pooled_skill_min"] and q4["worlds_E_beats_none"] >= RULES["Q4_worlds_positive_min"])
    out["Q4"] = {"rule": "k = 7-13: pooled skill E vs none and E vs N each > 10%; E beats none in >= 6 of 8 worlds", **q4}
    out["reported_k_1_3"] = {"skill_E_vs_none": skill("E", "none", "early"), "skill_E_vs_N": skill("E", "N", "early"),
                             "skill_N_vs_none": skill("N", "none", "early")}
    out["reported_k_7_13_N_vs_none"] = skill("N", "none", "post")
    out["mae"] = {f"{m}_{n}": round(float(v.sum() / v.size / 24), 4) for (m, n), v in arms.items()}
    return out


def run(weights: Path, out: Path, *, load=None, fetch=None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rec = {"phase": "beta1-qualify", "repo": t0_beta.REPO, "rules": RULES, "run_id": os.environ.get("GITHUB_RUN_ID"),
           "commit": os.environ.get("GITHUB_SHA")}
    try:
        rec["tfc_t0"] = t0_beta.require_runtime()
        rec["retrieval"] = (fetch or t0_beta.fetch)(weights)
        loader = load or t0_beta.load
        m1, _ = loader(weights)
        m2, _ = loader(weights)
        i1, i2 = t0_beta.BetaT0(m1), t0_beta.BetaT0(m2)
        res = checks(i1, i2, worlds("linear", WORLDS))
        rec.update(res)
        rec["t0_beta_forecasts"] = i1.rows + i2.rows
        rec["verdict"] = "PASS" if all(res[q]["pass"] for q in ("Q1", "Q2", "Q3", "Q4")) else "BETA NOT VIABLE"
    except Exception as exc:  # recorded: a beta that cannot run is the BETA NOT VIABLE outcome
        rec.update(verdict="BETA NOT VIABLE", error=f"{type(exc).__name__}: {exc}"[:2000],
                   traceback=traceback.format_exc()[-4000:])
    rec["elapsed_s"] = round(time.time() - started, 1)
    (out / "qualify.json").write_text(json.dumps(rec, indent=1) + "\n")
    (out / "verdict.json").write_text(json.dumps({k: rec.get(k) for k in ("phase", "verdict", "repo", "run_id",
                                                                          "commit")}, indent=1) + "\n")
    (out / "REPORT.md").write_text(report(rec), encoding="utf-8")
    return rec


def report(rec: dict) -> str:
    lines = [f"# t0-beta qualification: {rec['verdict']}", ""]
    r = rec.get("retrieval") or {}
    lines += [f"Model `{rec['repo']}` at revision `{r.get('served_revision')}`; tfc-t0 {rec.get('tfc_t0')}.",
              "", "| file | sha256 |", "|---|---|"]
    lines += [f"| {n} | `{h}` |" for n, h in (r.get("sha256") or {}).items()]
    lines.append("")
    if "error" in rec:
        lines += [f"Error: {rec['error']}", ""]
    for q in ("Q1", "Q2", "Q3", "Q4"):
        if q in rec:
            extra = ""
            if q == "Q4":
                extra = (f": E vs none {rec[q]['skill_E_vs_none'] * 100:+.1f}%, E vs N {rec[q]['skill_E_vs_N'] * 100:+.1f}%, "
                         f"E beats none in {rec[q]['worlds_E_beats_none']} of 8 worlds")
            if q == "Q3":
                extra = f": min hourly sd {rec[q]['min_hourly_sd']}, sanitised {rec[q]['sanitised']}"
            lines.append(f"- **{q}** ({rec[q]['rule']}){extra} - {'pass' if rec[q]['pass'] else 'FAIL'}")
    if "reported_k_1_3" in rec:
        e = rec["reported_k_1_3"]
        lines += ["", f"Reported only, k = 1-3: E vs none {e['skill_E_vs_none'] * 100:+.1f}%, E vs N "
                      f"{e['skill_E_vs_N'] * 100:+.1f}%, N vs none {e['skill_N_vs_none'] * 100:+.1f}%; "
                      f"k = 7-13 N vs none {rec['reported_k_7_13_N_vs_none'] * 100:+.1f}%."]
    lines += ["", f"t0-beta forecasts: {rec.get('t0_beta_forecasts')}; elapsed {rec['elapsed_s']} s.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rec = run(Path(args.weights), Path(args.out))
    print(json.dumps({"verdict": rec["verdict"], "error": rec.get("error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
