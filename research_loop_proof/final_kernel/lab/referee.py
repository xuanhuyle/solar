"""The final-kernel referee and memory builder (NEXT_FINAL_KERNEL_PROMPT.md sections 3C, 3D and 7; FINAL_KERNEL_SPEC.md
section 6). Deterministic and truth-free: it reads only the episode's context tags, the research record (the
researcher's own experiments, final beliefs and selection) and, through a callback, the holdout confirmation of
configurations that were actually tested and approved or explicitly selected. It never imports a truth package.

Rules:
- a configuration is (sorted covariates, sorted reference); results with windows under 14 days are indicative (the
  menu's own words) and never decide a status: a configuration with only indicative results is unresolved;
- the governing result of a configuration is its non-indicative result with the latest last scored day, then the
  longer window, then the later experiment id;
- status: positive if the governing lower bound is above 0; deteriorated if it is not but an earlier non-indicative
  result of the configuration (one with an earlier last scored day) was; negative otherwise;
- approved positive findings exist only at the tested granularity: individual ([x] against no reference),
  conditional (x given the reference) or set (several covariates, attribution among them unresolved). A set never
  yields individual claims;
- the headline is the narrowest approved positive finding (fewest covariates), then the highest governing lower bound,
  then the earliest experiment;
- confirmation (days 127-154, 28-day window) is computed for every approved positive configuration as tested, and for
  the final selection (1 to 4 candidates, against no reference) when the final response is valid.
Memory holds one entry per tested configuration with its status, granularity, experiments, research-window result
(the governing result, or for an unresolved configuration its latest indicative result, labelled as such) and, for
positive findings, its confirmation. Negative entries stay scoped to their configuration, window, episode and
regime.
"""
from __future__ import annotations

import json
import math

INDICATIVE_BELOW_DAYS = 14
CONFIRMATION = {"cutoff": 154, "window_days": 28, "days": [127, 154]}
STATUSES = ("positive", "negative", "deteriorated", "unresolved")
KEEP = ("skill", "lo95", "hi95", "reference_mae", "candidate_mae", "wins", "losses", "ties", "scored_days")


def _num(exp_id: str) -> int:
    return int(str(exp_id).lstrip("E"))


def experiments(record: dict, calls_limit: int | None = None) -> list[dict]:
    """The researcher's experiments in notebook order, each with its call and cutoff (up to call ``calls_limit``)."""
    return [dict(e, call=c["call"], cutoff=c["cutoff"]) for c in record.get("calls", [])
            if calls_limit is None or c["call"] <= calls_limit for e in c.get("experiments", [])]


def config_key(e: dict) -> tuple:
    return (tuple(sorted(e["request"]["covariates"])), tuple(sorted(e["request"]["reference"])))


def granularity(cov: tuple, ref: tuple) -> str:
    if len(cov) > 1:
        return "set (attribution unresolved)" + (f" given {', '.join(ref)}" if ref else "")
    return f"conditional on {', '.join(ref)}" if ref else "individual"


def _order(e: dict) -> tuple:
    return (e["result"]["scored_days"][1], e["request"]["window_days"], _num(e["id"]))


def _brief(e: dict) -> dict:
    r = e["result"]
    return {"experiment": e["id"], "call": e["call"], "window_days": e["request"]["window_days"],
            "scored_days": list(r["scored_days"]), "skill": r["skill"], "lo95": r["lo95"], "hi95": r["hi95"]}


def configurations(exps: list[dict]) -> list[dict]:
    """Every tested configuration with its results, governing result and status (first appearance order)."""
    groups: dict = {}
    for e in exps:
        groups.setdefault(config_key(e), []).append(e)
    out = []
    for (cov, ref), es in groups.items():
        decisive = sorted((e for e in es if e["request"]["window_days"] >= INDICATIVE_BELOW_DAYS), key=_order)
        if not decisive:
            status, gov = "unresolved", None
        else:
            gov = decisive[-1]
            if gov["result"]["lo95"] > 0:
                status = "positive"
            elif any(e["result"]["lo95"] > 0 and e["result"]["scored_days"][1] < gov["result"]["scored_days"][1]
                     for e in decisive[:-1]):
                status = "deteriorated"
            else:
                status = "negative"
        out.append({"covariates": list(cov), "reference": list(ref), "granularity": granularity(cov, ref),
                    "status": status, "experiments": [e["id"] for e in es],
                    "governing": _brief(gov) if gov else None,
                    "indicative": None if gov else _brief(sorted(es, key=_order)[-1]),
                    "indicative_only": gov is None, "first": min(_num(e["id"]) for e in es)})
    return out


def headline(configs: list[dict]) -> dict | None:
    pos = [c for c in configs if c["status"] == "positive"]
    if not pos:
        return None
    return min(pos, key=lambda c: (len(c["covariates"]), -c["governing"]["lo95"], c["first"]))


def _row(res: dict) -> dict:
    return {k: res[k] for k in KEEP}


def confirmation_status(row: dict | None) -> str:
    if row is None:
        return "not run"
    return "confirmed" if row["lo95"] > 0 else "not confirmed"


def adjudicate(record: dict, confirm, calls_limit: int | None = None, with_selection: bool = True) -> dict:
    """The referee's report on one research record. ``confirm(covariates, reference)`` returns the holdout result of
    a configuration (or raises); it is called only for approved positive configurations and the final selection."""
    exps = experiments(record, calls_limit)
    configs = configurations(exps)
    for c in configs:
        c["confirmation"] = _row(confirm(c["covariates"], c["reference"])) if c["status"] == "positive" else None
        c["confirmation_status"] = confirmation_status(c["confirmation"])
    head = headline(configs)
    sel = None
    if with_selection:
        valid = bool(record.get("final_valid")) and isinstance(record.get("final_selection"), list)
        ids = sorted(record.get("final_selection") or []) if valid else None
        if ids is None:
            sel = {"valid": False, "covariates": None, "confirmation": None, "status": "no valid final response"}
        elif not 1 <= len(ids) <= 4:
            sel = {"valid": True, "covariates": ids, "confirmation": None,
                   "status": "empty selection" if not ids else "not confirmable (more than 4 candidates)"}
        else:
            row = _row(confirm(ids, []))
            tested = any(c["covariates"] == ids and not c["reference"] for c in configs)
            sel = {"valid": True, "covariates": ids, "confirmation": row, "status": confirmation_status(row),
                   "tested_as_configuration": tested}
    return {"experiments": len(exps), "configurations": configs,
            "approved_positive": [c for c in configs if c["status"] == "positive"],
            "headline": head, "selection": sel}


# ----------------------------------------------------------------- memory

def memory_entries(report: dict, *, company: str, episode: int, regime: str, names: dict, start: int) -> list[dict]:
    """One memory entry per tested configuration of an episode's report, numbered from ``start``."""
    out = []
    for i, c in enumerate(report["configurations"], start):
        out.append({"id": f"M{i}", "company": company, "episode": episode, "regime": regime,
                    "covariates": c["covariates"], "covariate_names": [names[x] for x in c["covariates"]],
                    "reference": c["reference"], "reference_names": [names[x] for x in c["reference"]],
                    "status": c["status"], "granularity": c["granularity"],
                    "indicative_only": c["indicative_only"],
                    "experiments": [f"episode {episode} experiment {x}" for x in c["experiments"]],
                    "research_result": c["governing"] or c["indicative"], "confirmation": c["confirmation"],
                    "confirmation_status": c["confirmation_status"]})
    return out


def extend_memory(memory: list[dict], report: dict, *, company: str, episode: int, regime: str,
                  names: dict) -> list[dict]:
    return list(memory) + memory_entries(report, company=company, episode=episode, regime=regime, names=names,
                                         start=len(memory) + 1)


def _pct(v: float) -> str:
    return f"{v * 100:+.1f}%"


def _ids(ids: list[str], names: list[str]) -> str:
    return ", ".join(f"{i} ({n})" for i, n in zip(ids, names)) if ids else "none"


def render_entry(m: dict) -> str:
    r = m["research_result"]
    kind = "latest indicative result (under 14 days; no decisive result)" if m["indicative_only"] else \
        "decisive result"
    research = (f"evidence {', '.join(m['experiments'])}; {kind} days {r['scored_days'][0]}-"
                f"{r['scored_days'][1]}: skill {_pct(r['skill'])} (95% interval {_pct(r['lo95'])} to "
                f"{_pct(r['hi95'])})")
    c = m["confirmation"]
    holdout = ("holdout days 127-154: not run" if c is None else
               f"holdout days 127-154: {m['confirmation_status']}, skill {_pct(c['skill'])} (95% interval "
               f"{_pct(c['lo95'])} to {_pct(c['hi95'])})")
    return (f"{m['id']} | study period {m['episode']} | regime: {m['regime']} | covariates "
            f"{_ids(m['covariates'], m['covariate_names'])} | reference {_ids(m['reference'], m['reference_names'])}"
            f" | status {m['status']} | granularity {m['granularity']} | {research} | {holdout}")


def render_memory(memory: list[dict]) -> str:
    return "\n".join(render_entry(m) for m in memory)


def memory_json(memory: list[dict]) -> str:
    return json.dumps(memory, indent=1, sort_keys=True) + "\n"


def _close(a, b, tol: float) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
        except (TypeError, ValueError):
            return False
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b))
    return a == b


def memory_differences(shipped: list[dict], recomputed: list[dict], tol: float = 1e-4) -> list[str]:
    """Where a shipped memory differs from its recomputation: ids, configurations, granularity and statuses exactly,
    numbers within ``tol`` (a status may differ only when its deciding lower bound is within ``tol`` of 0)."""
    if len(shipped) != len(recomputed):
        return [f"{len(shipped)} entries shipped, {len(recomputed)} recomputed"]
    out = []
    for a, b in zip(shipped, recomputed):
        exact = ("id", "company", "episode", "regime", "covariates", "reference", "granularity", "experiments",
                 "indicative_only", "covariate_names", "reference_names")
        if any(a.get(k) != b.get(k) for k in exact):
            out.append(f"{b['id']}: identity or configuration differs")
            continue
        if a["status"] != b["status"]:
            lo = (b.get("research_result") or {}).get("lo95")
            if lo is None or abs(lo) > tol:
                out.append(f"{b['id']}: status {a['status']} shipped, {b['status']} recomputed")
                continue
        if not _close(a.get("research_result"), b.get("research_result"), tol):
            out.append(f"{b['id']}: research result differs")
        if a["status"] == b["status"] and not _close(a.get("confirmation"), b.get("confirmation"), tol):
            out.append(f"{b['id']}: confirmation differs")
    return out
