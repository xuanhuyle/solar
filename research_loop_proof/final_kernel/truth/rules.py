"""The final kernel's frozen scoring rules (FINAL_KERNEL_SPEC.md sections 8-10), pure functions of the referee's
reports, the hidden truth of an episode and the evaluator's confirmation numbers. Nothing here reads files, runs a
forecast or uses randomness.

The owner's corrections are part of these rules: the hard gate tests the full K system alone; K versus F is a
secondary diagnostic, computed and reported but never gating; "K strong-success in >=6/8" counts each episode's own
success (strong when non-null, null success when null); appropriate use of accumulated knowledge is judged through the
same criteria on the pattern episodes.
"""
from __future__ import annotations

from research_loop_proof.kernel1.truth.rules import median, oracle, oracle_fraction

MIN_EPISODE_SUCCESSES = 6
NON_NULL_SCORED = 6
MAX_INCORRECT_APPROVAL_EPISODES = 1
MEDIAN_ORACLE_FRACTION_MIN = 0.75
MAX_MISSING_SCORED = 1
MAX_STRONG_CANDIDATES = 2
OUTAGE_PREFIX = "IntegrityError: API outage:"
CLOSING = {"INFRASTRUCTURE FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "BENCHMARK FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "FULL KERNEL PROVEN FOR THIS BENCHMARK": "MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST",
           "FULL KERNEL NOT PROVEN": "STOP SYNTHETIC KERNEL WORK"}


def individual_approvals(report: dict) -> list[dict]:
    """Approved positive findings about one candidate: individual ([x], no reference) or conditional (x given R)."""
    return [c for c in report.get("approved_positive", []) if len(c["covariates"]) == 1]


def incorrect_approvals(report: dict, useful: list[str]) -> list[dict]:
    """Individual or conditional approvals of a candidate that is not currently useful (pure noise or stale)."""
    return [c for c in individual_approvals(report) if c["covariates"][0] not in useful]


def strong(report: dict, useful: list[str], informative: bool | None) -> dict:
    """Owner section 9, an informative non-null episode. Criteria 5-6 (frozen reading): no individual or conditional
    approval of a candidate that is not useful lacks evidence, where lacking evidence means its own holdout
    confirmation lower bound is at or below 0."""
    head = report.get("headline")
    conf = head and head.get("confirmation")
    unsupported = [c for c in incorrect_approvals(report, useful)
                   if not (c.get("confirmation") and c["confirmation"]["lo95"] > 0)]
    crit = {"0_informative": bool(informative),
            "1_approved_current_positive": bool(report.get("approved_positive")),
            "2_headline_at_most_2_candidates": bool(head) and len(head["covariates"]) <= MAX_STRONG_CANDIDATES,
            "3_headline_contains_useful_candidate": bool(head) and bool(set(head["covariates"]) & set(useful)),
            "4_headline_confirmation_lower_bound_above_0": bool(conf) and conf["lo95"] > 0,
            "5_6_no_unsupported_approval_of_irrelevant_candidate": not unsupported}
    partial = (bool(head) and 3 <= len(head["covariates"]) <= 4 and bool(conf) and conf["lo95"] > 0)
    return {"criteria": crit, "strong": all(crit.values()), "partial": partial and not all(crit.values()),
            "failed": [k for k, v in crit.items() if not v],
            "unsupported_approvals": [c["covariates"] + c["reference"] for c in unsupported]}


def null_success(report: dict, record: dict) -> dict:
    """Owner section 9: no positive current finding approved, and the user-facing conclusion holds no established
    positive claim (frozen structural reading: a valid final response with an empty selection and no candidate
    accepted; the prose is quoted in the report)."""
    final = (record.get("calls") or [{}])[-1]
    statuses = {b["candidate"]: b["status"] for b in final["response"]["beliefs"]} \
        if record.get("final_valid") and final.get("response") else {}
    crit = {"0_valid_final_response": bool(record.get("final_valid")),
            "1_no_approved_positive_finding": not report.get("approved_positive"),
            "2_empty_final_selection": record.get("final_valid") is True and not record.get("final_selection"),
            "3_no_candidate_accepted": not any(s == "accepted" for s in statuses.values())}
    return {"criteria": crit, "success": all(crit.values()), "failed": [k for k, v in crit.items() if not v]}


def strong_at(report: dict, useful: list[str]) -> bool:
    """Criteria 1-4 on a (prefix) report: the headline is a confirmed finding of at most 2 candidates containing a
    useful candidate."""
    head = report.get("headline")
    conf = head and head.get("confirmation")
    return (bool(head) and len(head["covariates"]) <= MAX_STRONG_CANDIDATES
            and bool(set(head["covariates"]) & set(useful)) and bool(conf) and conf["lo95"] > 0)


def discovery_index(prefixes: list[tuple[int, dict]], useful: list[str]) -> int | None:
    """The cumulative number of experiments through the earliest call whose referee report (calls 1..c) meets
    criteria 1-4; None when no call does. Counted per call: experiments of one call are chosen together."""
    for n, rep in prefixes:
        if strong_at(rep, useful):
            return n
    return None


def pair_outcome(k: dict, f: dict) -> tuple[str, str]:
    """Owner section 10, the secondary K-versus-F diagnostic. ``k`` and ``f`` hold ``strong`` (bool), ``index``
    (discovery index or None) and ``experiments`` (experiments used)."""
    def beats(a: dict, b: dict) -> str | None:
        if a["strong"] and not b["strong"]:
            return "strong success where the other was not"
        if a["strong"] and b["strong"]:
            if a["index"] is not None and b["index"] is not None and a["index"] <= b["index"] - 2:
                return f"first strong finding after {a['index']} experiments against {b['index']}"
            if a["index"] == b["index"] and a["experiments"] <= b["experiments"] - 2:
                return f"same discovery timing with {a['experiments']} experiments against {b['experiments']}"
        return None
    kw, fw = beats(k, f), beats(f, k)
    if kw:
        return "K WIN", kw
    if fw:
        return "F WIN", fw
    return "TIE", "neither condition met a win rule"


def episode_success(ep: dict) -> bool:
    return bool(ep["K"]["null"]["success"]) if ep["null"] else bool(ep["K"]["strong"]["strong"])


def programme(episodes: dict, material: list[str], defects: list[str], missing_scored: list[str]) -> tuple[str, str]:
    """Owner section 11 with the owner's corrections, first match. ``episodes`` maps an episode key to
    {"null", "pattern", "informative", "K": {"strong", "null", "incorrect", "oracle_fraction"}}."""
    if material or len(missing_scored) > MAX_MISSING_SCORED:
        why = list(material) + ([f"{len(missing_scored)} missing scored trajectories ({', '.join(missing_scored)})"]
                                if len(missing_scored) > MAX_MISSING_SCORED else [])
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(why)
    non_null = sorted(k for k, e in episodes.items() if not e["null"])
    informative = [k for k in non_null if e_inf(episodes[k])]
    if len(informative) < NON_NULL_SCORED or len(non_null) != NON_NULL_SCORED or defects:
        return "BENCHMARK FAILURE", (f"row 2: informative non-null episodes {len(informative)} of {len(non_null)}"
                                     + (f"; defects: {'; '.join(defects)}" if defects else ""))
    succ = sorted(k for k, e in episodes.items() if episode_success(e))
    nulls = sorted(k for k, e in episodes.items() if e["null"])
    null_ok = [k for k in nulls if episode_success(episodes[k])]
    incorrect = sorted(k for k, e in episodes.items() if e["K"]["incorrect"])
    fractions = [e["K"]["oracle_fraction"] for k, e in episodes.items()
                 if not e["null"] and e["K"]["oracle_fraction"] is not None]
    med = median(fractions)
    counts = (f"K episode successes {len(succ)} of {len(episodes)} ({', '.join(succ) or 'none'}); null successes "
              f"{len(null_ok)} of {len(nulls)}; episodes with an incorrect individual approval {len(incorrect)} "
              f"({', '.join(incorrect) or 'none'}); median oracle fraction "
              + ("undefined" if med is None else f"{med:.3f}") + f" over {len(fractions)} episodes")
    if (len(succ) >= MIN_EPISODE_SUCCESSES and len(null_ok) == len(nulls)
            and len(incorrect) <= MAX_INCORRECT_APPROVAL_EPISODES and med is not None
            and med >= MEDIAN_ORACLE_FRACTION_MIN):
        return "FULL KERNEL PROVEN FOR THIS BENCHMARK", "row 3: " + counts
    return "FULL KERNEL NOT PROVEN", "row 4: " + counts


def e_inf(ep: dict) -> bool:
    return bool(ep.get("informative"))


__all__ = ["CLOSING", "MAX_INCORRECT_APPROVAL_EPISODES", "MAX_MISSING_SCORED", "MAX_STRONG_CANDIDATES",
           "MEDIAN_ORACLE_FRACTION_MIN", "MIN_EPISODE_SUCCESSES", "NON_NULL_SCORED", "OUTAGE_PREFIX",
           "discovery_index", "e_inf", "episode_success", "incorrect_approvals", "individual_approvals", "median",
           "null_success", "oracle", "oracle_fraction", "pair_outcome", "programme", "strong", "strong_at"]
