"""The fixed comparator of Human1: one deterministic four-experiment protocol over the two supplied candidates
(NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md section 6). Frozen before any scored world existed; not optimised; it never
knows the hidden roles.

The owner's sequence, with the same lab, instrument, cutoffs and budget as the researcher (4 experiments, 2 per round),
every window the last 28 revealed days (as Discovery1's comparator; no knowledge of when the change happened):
- C1: X01 against no covariate, round 1 (days 1-112 observed);
- C2: X02 against no covariate, round 1;
- C3: X01 given X02, round 2 (days 1-126 observed);
- C4: X02 given X01, round 2.

Decision for each candidate X with partner Y, from the 95% lower bounds:
- accepted if X given Y is above 0;
- otherwise redundant if Y given X is above 0;
- otherwise promising if X alone (round 1) is above 0;
- otherwise rejected.
The final selection is the accepted candidates (possibly none). The evaluator recomputes it from the observed data.
"""
from __future__ import annotations

from research_loop_proof.human1.lab.executor import IDS2

WINDOW = 28
CUTOFFS = {1: 112, 2: 126}
X, Y = IDS2
PLAN = ((1, [X], []), (1, [Y], []), (2, [X], [Y]), (2, [Y], [X]))
RULE = ("C1 X01 vs none and C2 X02 vs none at day 112, C3 X01 given X02 and C4 X02 given X01 at day 126, all 28 days; "
        "per candidate: accepted if it adds given the other (lower bound > 0), else redundant if the other adds given "
        "it, else promising if positive alone, else rejected; selection = the accepted candidates")


def decide(results: list[dict]) -> tuple[dict, list[str]]:
    """Statuses and final selection from the four results, in plan order."""
    alone = {X: results[0]["lo95"] > 0, Y: results[1]["lo95"] > 0}
    given = {X: results[2]["lo95"] > 0, Y: results[3]["lo95"] > 0}
    statuses = {}
    for c, p in ((X, Y), (Y, X)):
        statuses[c] = ("accepted" if given[c] else "redundant" if given[p] else "promising" if alone[c]
                       else "rejected")
    return statuses, [c for c in IDS2 if statuses[c] == "accepted"]


def run(lab) -> dict:
    """The four experiments on ``lab`` (an ``executor.Lab2`` on the observed data), the statuses and the selection."""
    exps = []
    for rnd, cov, ref in PLAN:
        exp_id = f"C{len(exps) + 1}"
        req = {"covariates": list(cov), "reference": list(ref), "window_days": WINDOW}
        exps.append({"id": exp_id, "round": rnd, "cutoff": CUTOFFS[rnd], "request": req,
                     "result": lab.run(req, CUTOFFS[rnd], exp_id)})
    statuses, selection = decide([e["result"] for e in exps])
    return {"experiments": exps, "statuses": statuses, "final_selection": selection, "rule": RULE}


def selection_errors(record: dict) -> list[str]:
    """Why a recorded comparator run does not follow the protocol given its own recorded results (empty when it does)."""
    exps = record.get("experiments", [])
    if len(exps) != len(PLAN):
        return [f"{len(exps)} experiments, not {len(PLAN)}"]
    errs = []
    for e, (rnd, cov, ref) in zip(exps, PLAN):
        want = {"covariates": list(cov), "reference": list(ref), "window_days": WINDOW}
        if e["round"] != rnd or e["cutoff"] != CUTOFFS[rnd] or e["request"] != want:
            errs.append(f"{e['id']}: not the protocol's experiment (round {rnd}, {cov} given {ref})")
    statuses, selection = decide([e["result"] for e in exps])
    if record.get("statuses") != statuses or record.get("final_selection") != selection:
        errs.append(f"statuses {record.get('statuses')} / selection {record.get('final_selection')} are not the rule's "
                    f"{statuses} / {selection}")
    return errs
