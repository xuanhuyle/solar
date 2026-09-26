"""The referee-owned catalogue: everything a probe spec may name, and nothing else.

The researcher chooses among these entries; it never supplies code, data,
transforms, comparators, day rules or seeds of its own. Standard library only,
so the researcher job can read it (``catalogue_brief``) without installing the
forecasting stack.
"""

from __future__ import annotations

from engine.canon import sha256_of

VERSION = "catalogue/0"

#: The t0 configuration every arm uses (referee-owned; the researcher cannot change it).
T0 = {"repo_id": "theforecastingcompany/t0-alpha", "revision": "9b02c5f4bb6c89ba15d9fa74554018fe6464220b",
      "context_days": 90, "gate": "12:00 Europe/Paris on D-1, forecasting local day D"}

TARGETS: dict[str, dict] = {
    "consumption": {
        "description": "French national electricity consumption (ODRÉ eco2mix-national-cons-def, 'consommation', MW, 30 min)",
        "dataset": "eco2mix-national-cons-def", "column": "consommation", "night_zero": False,
        "best_simple": "blend_50", "reference": "rte_j1",
    },
    "solar": {
        "description": "French national solar generation (same dataset, 'solaire', MW, 30 min); scored after night zeroing",
        "dataset": "eco2mix-national-cons-def", "column": "solaire", "night_zero": True,
        "best_simple": "ewma", "reference": None,
    },
}

#: Known-future covariates. ``first_day`` is the first local day whose whole t0
#: window (90-day context + horizon) the covariate can cover; ``None`` = any day.
#: A period that ends before it is refused; one that starts before it is scored
#: on its covered days only (the result reports how many).
COVARIATES: dict[str, dict] = {
    "holiday": {"targets": ["consumption", "solar"], "kind": "calendar", "transforms": ["raw"], "first_day": None,
                "description": "1 on French public holidays (fixed dates and Easter-based), else 0; timestamps only"},
    "bridge_day": {"targets": ["consumption"], "kind": "calendar", "transforms": ["raw"], "first_day": None,
                   "description": "1 on a Monday before a Tuesday holiday or a Friday after a Thursday holiday; timestamps only"},
    "geometry": {"targets": ["solar"], "kind": "calendar", "transforms": ["raw"], "first_day": None,
                 "description": "capacity-weighted clear-sky solar geometry (the covariate slice's K1); timestamps only"},
    "wx_radiation": {"targets": ["solar"], "kind": "weather", "transforms": ["raw"], "first_day": "2024-06-06",
                     "description": ("archived ECMWF shortwave radiation forecast issued ~3 days ahead, weighted by 2023 "
                                     "regional solar output (the covariate slice's frozen construction)")},
    "wx_temperature": {"targets": ["consumption"], "kind": "weather", "transforms": ["raw", "hdd15", "cdd22"],
                       "first_day": "2024-05-06",  # archive from 2024-02-06 + a 90-day context
                       "description": ("archived 2 m temperature forecast issued ~3 days ahead at the 12 regional "
                                       "prefectures, weighted by 2023 regional consumption; hdd15 = max(15 - T, 0), "
                                       "cdd22 = max(T - 22, 0)")},
}

#: What an arm can be compared with. ``rte_j1`` is RTE's own forecast: reported, never a verdict.
COMPARATORS: dict[str, str] = {
    "best_simple": "the target's best simple rule, fixed by the referee (consumption: blend_50, chosen on 2023; solar: ewma)",
    "t0_base": "t0 with no covariates",
    "accepted": "the arm of the latest accepted finding for this target (consumption: C1 = t0 + holiday)",
    "rte_j1": "RTE's own day-ahead forecast (consumption only; reference only, never decides a verdict)",
}

METRICS: dict[str, str] = {"mae": "mean absolute error over all half-hours of the scored days (MW)"}

SCOPES: dict[str, list[int] | None] = {"all": None, "winter": [11, 12, 1, 2, 3], "summer": [5, 6, 7, 8, 9]}

#: Scoring periods, all in the discovery zone (local days, inclusive). 2025 is
#: consumed: explorable, never confirmable.
PERIODS: dict[str, tuple[str, str]] = {
    "Y2022": ("2022-01-01", "2022-12-31"), "Y2023": ("2023-01-01", "2023-12-31"),
    "Y2024": ("2024-01-01", "2024-12-31"), "Y2025c": ("2025-01-01", "2025-12-31"),
    "ALL": ("2022-01-01", "2025-12-31"),
}

LIMITS = {"arms": 3, "covariates_per_arm": 3, "comparisons": 3, "rationale_chars": 800, "name_chars": 32}

#: Statistics for discovery comparisons (exploratory; the vault uses its own, stricter test).
DISCOVERY_STATS = {"bootstrap": "paired moving-block, 7-day blocks", "resamples": 2000, "seed": 0}


def catalogue_dict() -> dict:
    return {"version": VERSION, "t0": T0, "targets": TARGETS, "covariates": COVARIATES, "comparators": COMPARATORS,
            "metrics": METRICS, "scopes": SCOPES, "periods": PERIODS, "limits": LIMITS,
            "discovery_stats": DISCOVERY_STATS}


def catalogue_sha256() -> str:
    return sha256_of(catalogue_dict())


def catalogue_brief() -> str:
    """The catalogue as the researcher reads it: plain text, stable byte for byte."""
    lines = [f"Catalogue {VERSION} (sha256 {catalogue_sha256()[:16]})", "",
             f"Model (fixed): t0-alpha, {T0['context_days']}-day context, gate {T0['gate']}.", "", "Targets:"]
    lines += [f"- {k}: {v['description']}; best simple rule {v['best_simple']}" for k, v in TARGETS.items()]
    lines += ["", "Covariates (id: targets; transforms; first scorable day):"]
    lines += [f"- {k}: {', '.join(v['targets'])}; {', '.join(v['transforms'])}; {v['first_day'] or 'any'} - "
              f"{v['description']}" for k, v in COVARIATES.items()]
    lines += ["", "Comparators:"] + [f"- {k}: {v}" for k, v in COMPARATORS.items()]
    lines += ["", "Metrics:"] + [f"- {k}: {v}" for k, v in METRICS.items()]
    lines += ["", "Scopes: " + ", ".join(f"{k} ({'all months' if v is None else 'months ' + str(v)})" for k, v in SCOPES.items())]
    lines += ["Periods: " + ", ".join(f"{k} {a}..{b}" for k, (a, b) in PERIODS.items()) + " (Y2025c is consumed: explore only)"]
    lines += [f"Limits: {LIMITS}"]
    return "\n".join(lines)
