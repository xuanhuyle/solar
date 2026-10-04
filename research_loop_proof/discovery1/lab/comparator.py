"""The fixed comparator of Discovery1: one simple group-screen/split search over the eight anonymous candidates,
budget-matched to the researcher (NEXT_DISCOVERY_MILESTONE_PROMPT.md, "Comparator"). Frozen before any scored world
existed; not optimised; no planning.

Same lab, same menu, same rounds and the same budget as the researcher: 6 experiments, at most 3 per round, at most
4 covariates each, every one against no covariate on the last 28 revealed days.
- Round 1 (days 1-84 observed): screen group A = X01-X04 and group B = X05-X08.
- Round 2 (days 1-112): screen A and B again. The winning group W is the one with the higher round-2 skill (A on a
  tie). The rule always decides from the latest results, so the round-1 screen is superseded and not used.
- Round 3 (days 1-126): split W into its two halves (its first two ids and its last two ids) and test each.
- Final selection: every candidate of a round-3 half whose 95% interval lower bound is above 0 (possibly none).

It resolves candidates to pairs only: it can pick the emerging driver without any other candidate only when its pair
partner is the emerging driver's proxy. The evaluator recomputes it from the observed data.
"""
from __future__ import annotations

from research_loop_proof.discovery1.lab.executor import IDS8

GROUP_A, GROUP_B = list(IDS8[:4]), list(IDS8[4:])
WINDOW = 28
CUTOFFS = {1: 84, 2: 112, 3: 126}
RULE = ("round 1: A = X01-X04 and B = X05-X08, each vs none, 28 days; round 2: A and B again; W = the group with the "
        "higher round-2 skill (A on a tie); round 3: W's first two ids and W's last two ids, each vs none, 28 days; "
        "final selection: every candidate of a round-3 half with a lower bound above 0")


def run(lab) -> dict:
    """The six experiments on ``lab`` (an ``executor.Lab8`` on the observed data) and the final selection."""
    exps = []

    def test(rnd: int, cov: list[str]) -> dict:
        exp_id = f"C{len(exps) + 1}"
        req = {"covariates": list(cov), "reference": [], "window_days": WINDOW}
        res = lab.run(req, CUTOFFS[rnd], exp_id)
        exps.append({"id": exp_id, "round": rnd, "cutoff": CUTOFFS[rnd], "request": req, "result": res})
        return res

    test(1, GROUP_A)
    test(1, GROUP_B)
    a2, b2 = test(2, GROUP_A), test(2, GROUP_B)
    winner = GROUP_A if a2["skill"] >= b2["skill"] else GROUP_B
    halves = [winner[:2], winner[2:]]
    split = [test(3, h) for h in halves]
    final = sorted(c for h, res in zip(halves, split) if res["lo95"] > 0 for c in h)
    return {"experiments": exps, "winner": winner, "halves": halves, "final_selection": final, "rule": RULE}


def selection_errors(record: dict) -> list[str]:
    """Why a recorded comparator run does not follow the rule given its own recorded results (empty when it does)."""
    exps = record.get("experiments", [])
    plan = [(1, GROUP_A), (1, GROUP_B), (2, GROUP_A), (2, GROUP_B)]
    if len(exps) != 6:
        return [f"{len(exps)} experiments, not 6"]
    a2, b2 = exps[2]["result"], exps[3]["result"]
    winner = GROUP_A if a2["skill"] >= b2["skill"] else GROUP_B
    plan += [(3, winner[:2]), (3, winner[2:])]
    errs = []
    for e, (rnd, cov) in zip(exps, plan):
        want = {"covariates": cov, "reference": [], "window_days": WINDOW}
        if e["round"] != rnd or e["cutoff"] != CUTOFFS[rnd] or e["request"] != want:
            errs.append(f"{e['id']}: not the rule's experiment (round {rnd}, covariates {cov})")
    final = sorted(c for e in exps[4:] if e["result"]["lo95"] > 0 for c in e["request"]["covariates"])
    if record.get("final_selection") != final:
        errs.append(f"final selection {record.get('final_selection')} is not the rule's {final}")
    return errs
