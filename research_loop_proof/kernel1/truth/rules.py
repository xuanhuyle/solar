"""Kernel1's frozen scoring rules (KERNEL1_SPEC.md sections 5-7), pure functions of the researcher's record, the
world's kind and roles, and the evaluator's numbers. Nothing here reads files, runs a forecast or uses randomness.

Experiments are the researcher's own, in notebook order, each carrying its call number (``experiments``). An
experiment is current-regime when, in a change world, its first scored day is on or after the change day tau (the
first changed day), and always in a stable or null world.
"""
from __future__ import annotations

ORACLE_FRACTION_MIN = 0.70  # per-world success, change and stable worlds
MEDIAN_ORACLE_FRACTION_MIN = 0.80  # programme row 3
MIN_INFORMATIVE_CHANGE = 6  # programme row 2
MIN_CHANGE_SUCCESSES = 6  # programme row 3
MAX_NOISY_WORLDS = 1  # programme row 3: informative non-null worlds with any pure-noise candidate in the selection
MAX_NO_FINAL = 1  # programme row 1: worlds without a valid final researcher response
MAX_COVARIATES = 4  # the lab's covariate limit, so the largest set the evaluator can confirm
OUTAGE_PREFIX = "IntegrityError: API outage:"
CLOSING = {"INFRASTRUCTURE FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "BENCHMARK FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
           "KERNEL PROVEN FOR THIS BENCHMARK": "MOVE THE CURRENT KERNEL TO A REAL-WORLD RESEARCH TEST",
           "KERNEL NOT PROVEN": "STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL"}


def experiments(ai: dict) -> list[dict]:
    """The researcher's experiments in notebook order, each with its call, round and cutoff."""
    return [dict(e, call=c["call"], round=c["round"], cutoff=c["cutoff"])
            for c in ai.get("calls", []) for e in c.get("experiments", [])]


def current(exp: dict, kind: str, tau: int) -> bool:
    return kind != "change" or exp["result"]["scored_days"][0] >= tau


def _cov(e: dict) -> list[str]:
    return list(e["request"]["covariates"])


def _ref(e: dict) -> list[str]:
    return list(e["request"]["reference"])


def _lo(e: dict) -> float:
    return float(e["result"]["lo95"])


def support(exps: list[dict], selection: list | None, kind: str, tau: int) -> dict:
    """Section 7. Direct support: a current experiment with covariates exactly F and lower bound > 0 (any reference);
    or, for every member f, a current experiment with covariates [f] and lower bound > 0 (any reference). Support by
    elimination: a current experiment X with covariates S, a proper superset of F, and lower bound > 0 (any
    reference), and for every z in S minus F a current experiment Y from a later call than X with z among its
    covariates, its covariates within S minus F, a non-empty reference within F and lower bound <= 0. The first
    qualifying experiments in notebook order form the reported chain."""
    sel = sorted(selection or [])
    if not sel:
        return {"supported": False, "how": None, "chain": []}
    cur = [e for e in exps if current(e, kind, tau)]
    for e in cur:
        if sorted(_cov(e)) == sel and _lo(e) > 0:
            return {"supported": True, "how": "direct: an experiment on exactly the final set", "chain": [e["id"]]}
    singles = []
    for f in sel:
        hit = next((e for e in cur if _cov(e) == [f] and _lo(e) > 0), None)
        if hit is None:
            break
        singles.append(hit["id"])
    else:
        return {"supported": True, "how": "direct: every member positive as the sole covariate", "chain": singles}
    for x in cur:
        s = set(_cov(x))
        if not (s > set(sel) and _lo(x) > 0):
            continue
        chain = [x["id"]]
        for z in sorted(s - set(sel)):
            y = next((e for e in cur if e["call"] > x["call"] and z in _cov(e) and set(_cov(e)) <= s - set(sel)
                      and _ref(e) and set(_ref(e)) <= set(sel) and _lo(e) <= 0), None)
            if y is None:
                break
            chain.append(y["id"])
        else:
            return {"supported": True, "how": "elimination", "chain": list(dict.fromkeys(chain))}
    return {"supported": False, "how": None, "chain": []}


def oracle(rows: dict) -> str | None:
    """The oracle set's label among ``rows`` (label -> {"size", "lo95", "candidate_mae", "ids"}): the lowest candidate
    MAE among those with lower bound > 0; ties go to the smaller set, then to the sorted ids."""
    ok = [k for k, r in rows.items() if r["lo95"] > 0]
    if not ok:
        return None
    return min(ok, key=lambda k: (rows[k]["candidate_mae"], rows[k]["size"], sorted(rows[k]["ids"])))


def oracle_fraction(selection_skill: float | None, oracle_skill: float | None) -> float:
    """The final set's confirmation skill over the oracle set's (0 when the final set was not confirmable: no valid
    final response, an empty set or more than four candidates)."""
    if selection_skill is None or not oracle_skill:
        return 0.0
    return float(selection_skill) / float(oracle_skill)


def median(values: list[float]) -> float | None:
    v = sorted(values)
    if not v:
        return None
    mid = len(v) // 2
    return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2


def scorable(selection: list | None) -> bool:
    return bool(selection) and len(selection) <= MAX_COVARIATES


def success(kind: str, *, final_valid: bool, informative: bool | None, selection: list | None, roles: dict,
            supported: bool, confirm_lo95: float | None, fraction: float, statuses: dict) -> dict:
    """Section 8, per world. ``roles`` maps role -> X id; ``statuses`` the final belief status per id."""
    sel = list(selection or [])
    noise = {roles[n] for n in ("N1", "N2", "N3", "N4", "N5")}
    crit = {"0_valid_final_response": bool(final_valid)}
    if kind == "change":
        crit.update({"1_informative": bool(informative), "2_selection_non_empty": bool(sel),
                     "3_r_absent": roles["R"] not in sel, "4_no_pure_noise": not (set(sel) & noise),
                     "5_supported_by_own_current_evidence": bool(supported),
                     "6_confirmation_lower_bound_above_0": confirm_lo95 is not None and confirm_lo95 > 0,
                     "7_oracle_fraction_at_least_0.70": fraction >= ORACLE_FRACTION_MIN})
    elif kind == "stable":
        crit.update({"1_informative": bool(informative), "2_selection_non_empty": bool(sel),
                     "3_no_pure_noise": not (set(sel) & noise), "4_supported_by_own_evidence": bool(supported),
                     "5_confirmation_lower_bound_above_0": confirm_lo95 is not None and confirm_lo95 > 0,
                     "6_oracle_fraction_at_least_0.70": fraction >= ORACLE_FRACTION_MIN})
    elif kind == "null":
        accepted = sorted(c for c, s in statuses.items() if s == "accepted")
        crit.update({"1_selection_empty": not sel, "2_no_final_status_accepted": not accepted,
                     "3_no_candidate_presented_as_established": not sel and not accepted})
    else:
        raise ValueError(f"unknown world kind {kind!r}")
    return {"criteria": crit, "success": all(crit.values()),
            "failed": [k for k, v in crit.items() if not v]}


def programme(worlds: dict, material: list[str], defects: list[str]) -> tuple[str, str]:
    """Section 9, first match. ``worlds`` maps world id -> {"kind", "final_valid", "informative", "success",
    "oracle_fraction", "noise_selected", "accepted"}."""
    no_final = sorted(k for k, w in worlds.items() if not w["final_valid"])
    if material or len(no_final) > MAX_NO_FINAL:
        why = list(material) + ([f"{len(no_final)} worlds without a valid final response ({', '.join(no_final)})"]
                                if len(no_final) > MAX_NO_FINAL else [])
        return "INFRASTRUCTURE FAILURE", "row 1: " + "; ".join(why)
    by = {kind: sorted(k for k, w in worlds.items() if w["kind"] == kind) for kind in ("change", "stable", "null")}
    inf_change = [k for k in by["change"] if worlds[k]["informative"]]
    inf_stable = [k for k in by["stable"] if worlds[k]["informative"]]
    if len(inf_change) < MIN_INFORMATIVE_CHANGE or len(inf_stable) < len(by["stable"]) or defects:
        return "BENCHMARK FAILURE", (f"row 2: informative change worlds {len(inf_change)} of {len(by['change'])} "
                                     f"({', '.join(inf_change) or 'none'}); informative stable worlds "
                                     f"{len(inf_stable)} of {len(by['stable'])}"
                                     + (f"; defects: {'; '.join(defects)}" if defects else ""))
    change_ok = [k for k in by["change"] if worlds[k]["success"]]
    stable_ok = [k for k in by["stable"] if worlds[k]["success"]]
    null_ok = [k for k in by["null"] if worlds[k]["success"]]
    informative = inf_change + inf_stable
    med = median([worlds[k]["oracle_fraction"] for k in informative])
    noisy = [k for k in informative if worlds[k]["noise_selected"]]
    false_accepts = sum(len(worlds[k]["accepted"]) for k in by["null"])
    counts = (f"change successes {len(change_ok)} of {len(by['change'])} ({', '.join(change_ok) or 'none'}); stable "
              f"{len(stable_ok)} of {len(by['stable'])}; null {len(null_ok)} of {len(by['null'])}; median oracle "
              f"fraction {med:.3f} over {len(informative)} informative non-null worlds; worlds with pure noise "
              f"selected {len(noisy)} ({', '.join(noisy) or 'none'}); false accepts in null worlds {false_accepts}")
    if (len(change_ok) >= MIN_CHANGE_SUCCESSES and len(stable_ok) == len(by["stable"])
            and len(null_ok) == len(by["null"]) and med >= MEDIAN_ORACLE_FRACTION_MIN
            and len(noisy) <= MAX_NOISY_WORLDS and false_accepts == 0):
        return "KERNEL PROVEN FOR THIS BENCHMARK", "row 3: " + counts
    return "KERNEL NOT PROVEN", "row 4: " + counts
