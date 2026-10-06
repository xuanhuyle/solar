"""The ledger's seed: what was established before the engine existed.

Each entry restates a result exactly as the README and the committed C1 ledger
record it, with the Actions run and commit that produced it, stamped LEGACY.
They inform the researcher; none of them is re-derived here. Only C1, confirmed
once on sealed 2025 data, becomes an accepted finding - the first baseline the
engine's claims must build on.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from solarbench import confirm

REPO = "https://github.com/xuanhuyle/solar"


def _run(run_id: int) -> str:
    return f"{REPO}/actions/runs/{run_id}"


GENESIS = {
    "engine": "knowledge engine v0",
    "zones": {"discovery": "2022-01-01..2025-12-31 (Europe/Paris days)",
              "consumed": {"2025": "claim C1, Actions run #20"}, "forward": "from 2026-01-01, vault only"},
    "rules": [
        "every discovery result is exploratory and never creditable",
        "claims are confirmed only on forward data arriving after their freeze (14-day embargo, >= 84 days)",
        "each vault window is opened once, after the owner approves the run in the engine-vault environment",
        "the referee owns targets, covariates, comparators, metrics, day rules and seeds",
    ],
}

LEGACY_RESULTS: list[dict] = [
    {
        "id": "E0", "title": "Experiment 0: t0 zero-shot vs historical baselines, French national solar, 2024",
        "runs": [_run(34682454351), _run(34683244310), _run(34744546087)], "commits": ["2438a03", "4f8dfc5", "3c4abb9"],
        "summary": ("t0 alone (704 MW MAE) beats previous day (747) by +5.8% but loses to blend_50 (646) by "
                    "-9.0% [-13.8, -4.3]; ewma 641 is best; 363 days, 2024"),
        "numbers": {"mae_mw": {"t0": 704, "t0_night_zero": 656, "ewma": 641, "blend_50": 646, "prev_day": 747,
                               "prev_week": 822}, "t0_vs_blend_50": [-0.090, -0.138, -0.043], "days": 363},
    },
    {
        "id": "COV", "title": "Covariate slice: t0 + geometry + archived weather forecast, national solar, Jun-Dec 2024",
        "runs": [_run(36059249513), _run(36098545565), _run(36104401204)], "commits": ["e807a62", "258aed0"],
        "summary": ("t0 + weather cuts t0's MAE by +25.6% [21.6, 29.6] (496 vs 668 MW) but a one-line "
                    "weather ratio without t0 is better still (401 MW; t0 + weather -23.8%); geometry adds nothing"),
        "numbers": {"mae_mw": {"t0_wx_night_zero": 496, "t0_night_zero": 668, "wx_ratio": 401, "ewma": 662},
                    "t0_wx_vs_t0": [0.256, 0.216, 0.296], "t0_wx_vs_wx_ratio": [-0.238, -0.337, -0.155], "days": 205},
    },
    {
        "id": "P1", "title": "Experiment 3, probe P1: t0 uncertainty bands (pinball) vs wx_ratio + empirical bands, solar",
        "runs": [_run(36113438085)], "commits": ["f2dec78", "1e1e769"],
        "summary": "lost: pinball -34.4% [-46.5, -23.7]; t0's 10-90% band covers 57% of daytime outcomes",
        "numbers": {"skill": [-0.344, -0.465, -0.237], "coverage_10_90": 0.57, "days": 207},
    },
    {
        "id": "P2", "title": "Experiment 3, probe P2: t0 forecasting wx_ratio's residuals, solar",
        "runs": [_run(36113438085)], "commits": ["f2dec78", "1e1e769"],
        "summary": "lost: -3.8% [-11.4, +3.0] MAE vs wx_ratio",
        "numbers": {"skill": [-0.038, -0.114, 0.030], "days": 207},
    },
    {
        "id": "P3", "title": "Experiment 3, probe P3: 12 regional solar series jointly, summed, vs ewma",
        "runs": [_run(36113438085)], "commits": ["f2dec78", "1e1e769"],
        "summary": ("tie: +0.8% [-3.1, +4.7]; regional sum beats national t0 by +3.1%, joint vs independent "
                    "regions +0.1%"),
        "numbers": {"skill": [0.008, -0.031, 0.047], "days": 365},
    },
    {
        "id": "P4", "title": "Experiment 3, probe P4: t0 + holidays vs blend_50, French national consumption, 2024",
        "runs": [_run(36113438085)], "commits": ["f2dec78", "1e1e769"],
        "summary": ("won: +49.6% [44.2, 55.1] (1,571 vs 3,114 MW), Holm p 0.002; plain t0 +47.2%; "
                    "RTE's own D-1 forecast is 14.8% better than t0 + holidays"),
        "numbers": {"mae_mw": {"t0_cal": 1571.0, "blend_50": 3114.4, "t0": 1644.4, "rte_j1": 1368.2},
                    "skill": [0.496, 0.442, 0.551], "days": 364},
    },
]


def c1_entry(ledger_path: Path = confirm.LEDGER) -> tuple[dict, dict]:
    """C1 as a legacy result (its committed ledger line embedded, with the line's sha256) and as the
    first accepted finding."""
    line = next(l for l in Path(ledger_path).read_text(encoding="utf-8").splitlines() if l.strip())
    import json

    record = json.loads(line)
    legacy = {
        "id": "C1", "title": "Claim C1: one-shot confirmation on sealed 2025 data (t0 + holidays vs blend_50, consumption)",
        "runs": [record["run"], record["dry_run_2024"]], "commits": [record["commit"][:7], "2a91197", "bf7ee94"],
        "summary": (f"CONFIRMED: skill {record['skill']:+.1%} [{record['skill_ci95'][0]:+.1%}, "
                    f"{record['skill_ci95'][1]:+.1%}], one-sided 95% lower bound {record['lower_bound_one_sided_95']:+.1%} "
                    f"> 25%; RTE's own forecast still 23.1% better"),
        "confirmations_jsonl_line": record,
        "confirmations_jsonl_line_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
        "claim_sha256": confirm.FROZEN_CLAIM_SHA256,
    }
    accepted = {
        "finding_id": "C1",
        "statement": confirm.CLAIM["statement"],
        "target": "consumption",
        "arm": {"covariates": [{"id": "holiday", "transform": "raw"}], "context_days": 90},
        "comparator": "best_simple (blend_50)",
        "metric": "mae",
        "confirmed_on": "2025 (sealed, one shot)",
        "skill": round(record["skill"], 4),
        "lower_bound_one_sided_95": round(record["lower_bound_one_sided_95"], 4),
        "run": record["run"],
        "note": "RTE's own day-ahead forecast (weather-driven) was still 23.1% better than this arm in 2025",
    }
    return legacy, accepted


def seed_items(context: dict) -> list[dict]:
    from engine import ledger

    legacy_c1, accepted = c1_entry()
    items = [ledger.pending("genesis", GENESIS, context)]
    items += [ledger.pending("legacy_result", dict(r, status=ledger.LEGACY), context) for r in LEGACY_RESULTS]
    items.append(ledger.pending("legacy_result", dict(legacy_c1, status=ledger.LEGACY), context))
    items.append(ledger.pending("accepted_finding", accepted, context))
    return items
