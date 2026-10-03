"""The frozen scripted strategy (menu.json "scripted_strategy"; PHASE0_SPEC.md section 4): the same menu and budget
as the AI researcher, a fixed sequence, descriptive only."""
from __future__ import annotations

from research_loop_proof.phase0.lab.executor import IDS, MENU

PLAN = MENU["scripted_strategy"]


def run(lab) -> dict:
    """Rounds 1-3 as listed, then: every candidate whose latest single-candidate result has a lower bound above 0."""
    experiments = []
    for rnd, cutoff in ((r["round"], r["revealed_through_day"]) for r in MENU["rounds"]):
        for req in PLAN[f"round_{rnd}"]:
            exp_id = f"S{len(experiments) + 1}"
            experiments.append({"id": exp_id, "round": rnd, "request": req, "result": lab.run(req, cutoff, exp_id)})
    latest = {}
    for e in experiments:
        if len(e["request"]["covariates"]) == 1:
            latest[e["request"]["covariates"][0]] = e["result"]
    selection = [c for c in IDS if c in latest and latest[c]["lo95"] > 0]
    return {"experiments": experiments, "final_selection": selection,
            "rule": PLAN["final_selection"]}
