"""The frozen Human1 adjudication rules (HUMAN1_SPEC.md section 6): a pure, deterministic function of a searcher's own
recorded experiments, its final statuses and its final selection. The same rules apply to researcher L2 and to the
fixed comparator.

The scored claims are each candidate's final status (the existing vocabulary: untested, promising, accepted, rejected,
deteriorated, redundant) and the final selection. The prose conclusion is reported verbatim and never scored.

Evidence is the searcher's own experiments that are
- fresh: scored entirely after the change, i.e. the first scored day is 93 or later (the latest possible change day of
  the frozen generator is 92); in practice every window except the 28-day window at day 112 (days 85-112), which always
  contains pre-change days;
- non-indicative: at least 14 days (the brief itself calls intervals under 14 days indicative only).

For a candidate c with partner p, the test shapes are A(c) = [c] against no covariate, C(c) = [c] given [p], and
S = [c, p] against no covariate. Each shape's governing result is its longest window, then its later cutoff, then its
later experiment. A lower bound of exactly 0 counts as null.
- Positive alone: the governing A(c) has a lower bound above 0. Without any A(c) test, by elimination: the governing S
  and the governing C(p) were scored on the same days, S's lower bound is above 0 and C(p)'s upper bound is below S's
  lower bound. (On the same days skill is a ratio of pooled errors, so c alone beats no covariate exactly when
  skill(p given c) < skill(S).)
- Positive conditional: the governing C(c) has a lower bound above 0. Without any C(c) test, by elimination: the
  governing S and the governing A(p) on the same days, S's lower bound above 0 and A(p)'s upper bound below it (c adds
  given p exactly when skill(p alone) < skill(S)). A null conditional alone never licenses elimination.
- Negative alone / negative conditional: the governing A(c) / C(c) exists with a lower bound at or below 0.

Claim support:
- accepted: positive alone or positive conditional; when both candidates are accepted, each needs a positive
  conditional (a joint claim that each adds given the other);
- promising: always allowed (it states uncertainty);
- redundant: a negative conditional;
- rejected or deteriorated: a negative result (alone or conditional) and no positive one;
- untested: no claim.
The selection is supported when it is empty, when every selected candidate has positive evidence of its own, or when it
is exactly the pair and the governing S is positive. Incoherence (counted as unsupported): a selected candidate whose
status is rejected, deteriorated or untested, or an accepted candidate that is not selected.

Success needs all of: (1) the world is informative; (2) completeness: neither status is untested and each candidate
entered a fresh, non-indicative experiment as a covariate; (3) E accepted with a supported claim, and selected; (4) the
pair-type rule for the distractor Z: E+D: a fresh, non-indicative D-given-E test exists and D is not accepted unless D
given E is positive; E+noise: N neither accepted nor selected; E+R: R accepted or selected only with positive evidence
of its own; (5) every claim and the selection supported, and no incoherence.
"""
from __future__ import annotations

FRESH_FIRST_DAY = 93
MIN_WINDOW_DAYS = 14
NEGATIVE = ("rejected", "deteriorated", "redundant")


def usable(x: dict) -> bool:
    return x["result"]["scored_days"][0] >= FRESH_FIRST_DAY and x["request"]["window_days"] >= MIN_WINDOW_DAYS


def _shape(x: dict, c: str, p: str) -> str | None:
    cov, ref = x["request"]["covariates"], x["request"]["reference"]
    if cov == [c] and ref == []:
        return "A"
    if cov == [c] and ref == [p]:
        return "C"
    if sorted(cov) == sorted([c, p]) and ref == []:
        return "S"
    return None


def governing(exps: list[dict], shape: str, c: str, p: str) -> dict | None:
    """The governing usable result of ``shape`` for candidate ``c``: longest window, then later cutoff, then later."""
    hits = [(x["request"]["window_days"], x["cutoff"], i, x) for i, x in enumerate(exps)
            if usable(x) and _shape(x, c, p) == shape]
    return max(hits, key=lambda h: h[:3])[3] if hits else None


def _derived(s: dict | None, other: dict | None) -> bool:
    return bool(s and other and s["result"]["scored_days"] == other["result"]["scored_days"]
                and s["result"]["lo95"] > 0 and other["result"]["hi95"] < s["result"]["lo95"])


def evidence(exps: list[dict], c: str, p: str) -> dict:
    a, cond, s = governing(exps, "A", c, p), governing(exps, "C", c, p), governing(exps, "S", c, p)
    a_p, cond_p = governing(exps, "A", p, c), governing(exps, "C", p, c)
    pos_alone = a["result"]["lo95"] > 0 if a else _derived(s, cond_p)
    pos_cond = cond["result"]["lo95"] > 0 if cond else _derived(s, a_p)
    return {"alone": a and a["id"], "conditional": cond and cond["id"], "set": s and s["id"],
            "pos_alone": bool(pos_alone), "alone_by_elimination": bool(not a and pos_alone),
            "neg_alone": bool(a and a["result"]["lo95"] <= 0),
            "pos_cond": bool(pos_cond), "cond_by_elimination": bool(not cond and pos_cond),
            "neg_cond": bool(cond and cond["result"]["lo95"] <= 0),
            "pos_set": bool(s and s["result"]["lo95"] > 0),
            "entered": any(usable(x) and c in x["request"]["covariates"] for x in exps)}


def claim_supported(status: str | None, ev: dict, partner_status: str | None) -> tuple[bool, str]:
    if status == "accepted":
        if partner_status == "accepted":
            return ev["pos_cond"], "joint acceptance needs positive evidence that it adds given the other"
        return ev["pos_alone"] or ev["pos_cond"], "acceptance needs positive evidence, alone or given the other"
    if status == "redundant":
        return ev["neg_cond"], "redundancy needs a conditional test given the other that is not positive"
    if status in ("rejected", "deteriorated"):
        ok = (ev["neg_alone"] or ev["neg_cond"]) and not ev["pos_alone"] and not ev["pos_cond"]
        return ok, "a rejection needs a negative result and no positive one"
    if status in ("promising", "untested"):
        return True, "no claim of support or of absence"
    return False, f"unknown or missing status {status!r}"


def adjudicate(exps: list[dict], statuses: dict | None, selection: list | None, roles: dict, pair_type: str,
               informative: bool) -> dict:
    """``roles`` maps "E" and "Z" (the supplied distractor) to their ids; ``statuses`` maps ids to final statuses."""
    statuses = dict(statuses or {})
    sel = list(selection or [])
    e, z = roles["E"], roles["Z"]
    ev = {e: evidence(exps, e, z), z: evidence(exps, z, e)}
    claims = {}
    for c, p in ((e, z), (z, e)):
        ok, why = claim_supported(statuses.get(c), ev[c], statuses.get(p))
        claims[c] = {"status": statuses.get(c), "supported": ok, "rule": why, "selected": c in sel, **ev[c]}
    own = {c: ev[c]["pos_alone"] or ev[c]["pos_cond"] for c in (e, z)}
    sel_ok = not sel or all(own[c] for c in sel) or (sorted(sel) == sorted([e, z]) and ev[e]["pos_set"])
    incoherent = [c for c in (e, z) if (c in sel and statuses.get(c) in ("rejected", "deteriorated", "untested", None))
                  or (statuses.get(c) == "accepted" and c not in sel)]
    unsupported_acceptances = [c for c in (e, z) if (statuses.get(c) == "accepted" and not claims[c]["supported"])
                               or (c in sel and not sel_ok and not own[c])]
    unsupported_rejections = [c for c in (e, z) if statuses.get(c) in NEGATIVE and not claims[c]["supported"]]
    if pair_type == "E+D":
        distractor_ok = bool(ev[z]["conditional"]) and (statuses.get(z) != "accepted" or ev[z]["pos_cond"])
    elif pair_type == "E+noise":
        distractor_ok = statuses.get(z) != "accepted" and z not in sel
    elif pair_type == "E+R":
        distractor_ok = (statuses.get(z) != "accepted" and z not in sel) or own[z]
    else:
        raise ValueError(f"unknown pair type {pair_type!r}")
    criteria = {
        "1_informative": bool(informative),
        "2_complete": all(statuses.get(c) not in (None, "untested") and ev[c]["entered"] for c in (e, z)),
        "3_e_supported": statuses.get(e) == "accepted" and claims[e]["supported"] and e in sel,
        "4_distractor_treated_correctly": bool(distractor_ok),
        "5_no_unsupported_claim": all(claims[c]["supported"] for c in (e, z)) and sel_ok and not incoherent,
    }
    return {"claims": claims, "selection": sel, "selection_supported": sel_ok, "incoherent": incoherent,
            "unsupported_acceptances": unsupported_acceptances, "unsupported_rejections": unsupported_rejections,
            "criteria": criteria, "success": all(criteria.values())}
