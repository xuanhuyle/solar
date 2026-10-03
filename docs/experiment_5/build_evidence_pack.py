"""Build the evidence pack the AI researcher receives for its Experiment 5 proposal.

The pack is assembled MECHANICALLY from recorded sources; the engineering orchestrator adds no interpretation,
no ranking and no recommendation. Every record carries an id the researcher can cite, the experiment it belongs
to, its evidence grade, how far it has been verified, and its source (path or ledger seq, commit, run).

Sources:
- the engine ledger (branch ``engine-ledger``, pinned head; its hash chain is verified);
- Experiment 4's committed run outputs, its K1 log, amendment A1, the retrieval event and the replication report;
- claim C1's confirmation record;
- the README's result and limitation sections, verbatim and labelled as narrative written at the time;
- the external t0 report page (``docs/experiment_3/T0_STRENGTHS.md``);
- infrastructure facts read from the code.

``EXCLUDED`` below lists what is deliberately left out, and why. The brief discloses that list.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/build_evidence_pack.py

Writes ``evidence_pack.json`` (compact canonical JSON, whose sha256 is printed and pinned by the proposal call) and a readable
``evidence_pack.md`` next to this file.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from engine import catalogue, claims, gates, ledger, zones  # noqa: E402
from engine.referee import budget  # noqa: E402
from solarbench.price_spec import PRICE_SPEC  # noqa: E402

LEDGER_REF = "origin/engine-ledger"
LEDGER_HEAD = {"seq": 72, "git": "de956e4a4b5215d1fb2ff5e36178b3d9bf007d68"}
PACK_VERSION = "exp5-evidence/1"

GRADES = {
    "confirmed_on_sealed_data": "a claim frozen before the data were scored and confirmed once on sealed data",
    "discovery_grade_preregistered": "a pre-registered test whose rules were frozen before any data were seen, run on "
                                     "public or already-explored data: exploratory, never confirmation",
    "exploratory": "a measurement on explored data with no pre-registered verdict: exploratory only",
    "rehearsal": "a vault dry run on already-consumed data: tests the machinery, confirms nothing",
    "legacy": "a result recorded before the engine existed, as summarised in the ledger seed; it says when and how "
              "the result was recorded, not its quality or design: whether its comparisons were frozen before the "
              "run is stated in that experiment's narrative record",
    "process": "a frozen specification, gate, rule change, amendment or provenance event: how the evidence was "
               "produced; any rationale in it is the argument made at the time, a claim to evaluate",
    "design_only": "a design document; nothing ran",
    "external_report": "the project's page summarising claims made by t0's authors in their technical report, with "
                       "the project's own notes on what it tested; the authors' claims are not tested here unless "
                       "stated",
    "researcher_note": "the AI researcher's earlier decision and reasoning in the engine loop, as it wrote it under "
                       "that loop's instructions (choose catalogue probes that could become a clean, freezable claim: "
                       "one arm, one comparator, a large and stable effect; freeze a claim batch when the exploratory "
                       "evidence is strong and stable); where set, owner_question is the project owner's question that "
                       "the iteration was answering, verbatim",
    "owner_directive": "the project owner's instruction; any reasoning in it is a claim to evaluate",
    "narrative": "the project's write-up at the time, verbatim: it contains numbers, caveats and the authors' "
                 "interpretations, which are claims to evaluate, not established knowledge",
    "infrastructure": "a fact about what the current code, data and rules allow",
}
VERIFICATION = {
    "independently_reproduced": "recomputed by an independent implementation from the original recorded outputs",
    "rerun_agreed": "re-runs on separate runners agreed at the displayed precision",
    "reproduced_within_tolerance": "the engine's own declarative code path, not the original code, re-ran a "
                                   "computation recorded earlier; its numbers matched the recorded ones within the "
                                   "tolerance stated in the reproduction-check gate record of the same run, not "
                                   "exactly; a pointer record means a later run, after code changes, gave numbers "
                                   "identical to the record it points to",
    "audited": "reviewed by an independent read-only audit; caveats recorded",
    "internal_consistency_only": "checked against the run's own records only",
    "not_independently_verified": "taken as recorded",
    "not_applicable": "",
}
EXCLUDED = [
    {"what": "Earlier engineering recommendations about which experiment to run next (for example the Experiment 2 "
             "pre-registration's 'recommended next experiment' and recommendations made in chat)",
     "why": "the researcher, not the engineering orchestrator, chooses the next investigation"},
    {"what": "README sections not included as records: the introduction; Experiment 0's 'Reading it' and "
             "'Reproducing these numbers'; 'The experiment' (Methods, Pre-registered analysis, Metrics); Model access; "
             "Data and Data vintage; Outputs; Running it on GitHub Actions; Useful flags; Sanity checks; Tests; Layout; "
             "Scope; and the README Experiment 4 section",
     "why": "methods and operating documentation, or a restatement of records included here; the text is in README.md"},
    {"what": "Experiment 4's FACT_SHEET.md (all sections), verify_integrity.md, verify_reading.md, "
             "verify_statistics.md, k2_attempts.jsonl, and INDEPENDENT_REPLICATION.md sections 1, 2 and 'Files'",
     "why": "they restate results.json, run_meta.json and PRICE_SPEC['carry_forward'] (included), or record "
            "provenance and field-by-field comparisons whose outcome the replication's other sections state; their "
            "earlier verification gap is superseded by X4-REPLICATION"},
    {"what": "The per-day series ('per_day') of every probe_result and vault-rehearsal record, and the probe records' "
             "per-method leak-check detail, dropped_nonfinite, data and windows_built fields",
     "why": "size; each comparison's skill, 95% interval, p, MAEs, days won and lost, and each verdict are included; "
            "the full series stay on the ledger at the cited seq"},
    {"what": "The first proposal request of this stage (ledger seq 72, run 36855164105) and its automatic config "
             "entry (seq 71)",
     "why": "an interface failure, not research: the API rejected the request (its answer schema was too large to "
            "compile as a constrained format) before any answer was produced"},
    {"what": "Ledger entries of kind genesis (seq 0), config, and probe_submitted",
     "why": "code fingerprints and submissions whose spec, rationale, builds_on and submitter reappear in the matching "
            "probe_result record; they stay on the ledger"},
    {"what": "Model identifiers, API usage and request ids of earlier research calls",
     "why": "not evidence about forecasting; they stay on the ledger"},
    {"what": "Any data from 2026 onward",
     "why": "sealed: readable only through the forward vault"},
]
README_SECTIONS = [
    ("EXP0", "## Results — full year 2024", ("### Reading it", "### Reproducing these numbers")),
    ("EXP0", "## Results — Phase 2: competent historical-only baselines, full year 2024", ()),
    ("COV", "## Covariate slice: t0 with geometry and weather", ()),
    ("EXP3", "## Experiment 3: t0 strengths probe", ()),
    ("C1", "## Claim C1: a one-shot confirmation on sealed 2025 data", ()),
    ("LIMITS", "## Known limitations", ()),
    ("ENGINE", "## Knowledge engine v0", ()),
]


LEGACY_VERIFICATION = {
    "E0": ("rerun_agreed", "R-EXP0-0 and R-EXP0-1: runs on separate runners agree at displayed precision (Phase 1 "
                           "runs #5 and #6; Phase 2 runs #9, #10 and #11)"),
    "P4": ("reproduced_within_tolerance", "R-C1-4: the 2024 dry run #19 reproduced P4 exactly; engine reproductions "
                                          "L12 and L27 agree within 0.5% (gates L15, L29)"),
    "C1": ("audited", "the same result as C1-CONFIRMATION and L9 (audited); engine re-run L14 within 0.5% (gate L15)"),
}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


FILES: dict[str, str] = {}


def read(rel: str) -> str:
    b = (ROOT / rel).read_bytes()
    FILES[rel] = sha256(b)
    return b.decode("utf-8")


def section(text: str, heading: str, skip: tuple[str, ...] = ()) -> str:
    """The README text from ``heading`` to the next heading of the same or a higher level, minus ``skip`` sections."""
    lines = text.split("\n")
    level = len(heading) - len(heading.lstrip("#"))
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if re.match(rf"^#{{1,{level}}} ", lines[i])), len(lines))
    body, dropping = [], None
    for line in lines[start:end]:
        m = re.match(r"^(#+) ", line)
        if m:
            if line in skip:
                dropping = len(m.group(1))
                continue
            if dropping is not None and len(m.group(1)) <= dropping:
                dropping = None
        if dropping is None:
            body.append(line)
    return "\n".join(body).strip() + "\n"


def rec(rid, experiment, title, grade, verification, content, source) -> dict:
    assert grade in GRADES and verification in VERIFICATION, (grade, verification)
    return {"id": rid, "experiment": experiment, "title": title, "evidence_grade": grade,
            "verification": verification, "content": content, "source": source}


def ledger_records(entries: list[dict]) -> list[dict]:
    out = []
    by_seq = {e["seq"]: e for e in entries}
    led = lambda e: {"ledger": "engine-ledger", "seq": e["seq"], "run_id": e.get("run_id"),
                     "code_commit": e.get("code_commit"), "mode": e.get("mode")}
    for e in entries:
        k, p, s = e["kind"], e["payload"], e["seq"]
        if k == "legacy_result":
            exp = {"E0": "EXP0", "COV": "COV", "C1": "C1"}.get(p.get("id"), "EXP3")
            ver, basis = LEGACY_VERIFICATION.get(p.get("id"), ("not_independently_verified", None))
            out.append(rec(f"L{s}", exp, p.get("title") or p.get("id"), "legacy", ver, p,
                           {**led(e), **({"verification_basis": basis} if basis else {})}))
        elif k == "accepted_finding":
            out.append(rec(f"L{s}", "C1", "Accepted finding C1 (the engine's 'accepted' comparator for consumption)",
                           "confirmed_on_sealed_data", "audited", p, led(e)))
        elif k == "gate":
            grade = "process"
            title = (f"Known-answer gate {p.get('target')}/{p.get('covariate')} under {p.get('rules_version', 'ka/1')}: "
                     f"{'PASS' if p.get('pass') else 'FAIL'}") if "covariate" in p else "Reproduction check"
            out.append(rec(f"L{s}", "ENGINE", title, grade, "not_applicable", p, led(e)))
        elif k == "note":
            if "rule_change" in p:
                out.append(rec(f"L{s}", "ENGINE", "Known-answer rule change ka/1 -> ka/2 (owner decision)", "process",
                               "not_applicable", p, led(e)))
            elif "batch" in p:
                keep = {kk: p[kk] for kk in p if kk != "batch"}
                if isinstance(keep.get("vault_dryrun"), dict):  # the verdicts, not the per-day series
                    keep["vault_dryrun"] = {kk: v for kk, v in keep["vault_dryrun"].items() if kk != "per_day"}
                keep["batch_claims"] = p["batch"].get("claims")
                keep["batch_window"] = p["batch"].get("window")
                out.append(rec(f"L{s}", "ENGINE", "Vault rehearsal on consumed 2025 data (NON-CONFIRMATORY)",
                               "rehearsal", "not_applicable", keep, led(e)))
        elif k == "probe_result":
            spec = p.get("spec", {})
            keep = ("arm", "vs", "days", "skill", "ci95", "p_one_sided", "mae_arm", "mae_vs", "days_won", "days_lost",
                    "error", "note")
            content = {"status": p.get("status"), "target": p.get("target"), "period": p.get("period"),
                       "scope": p.get("scope"), "limit_days": p.get("limit_days"),
                       "leak_checks_passed": p.get("leak_checks_passed"), "accepted_arm": p.get("accepted_arm"),
                       "arms": spec.get("arms"), "builds_on": spec.get("builds_on"), "rationale": spec.get("rationale"),
                       "submitted_by": p.get("submitted_by"),
                       "eligible_days": {m: v.get("eligible_days") for m, v in (p.get("methods") or {}).items()},
                       "comparisons": [{kk: c[kk] for kk in keep if kk in c} for c in p.get("comparisons", [])]}
            grade = "exploratory"
            title = {"loop": "Researcher probe result", "reproduce": "Reproduction of a legacy result through the engine",
                     "vault_dryrun": "Evidence probe run during a vault rehearsal"}.get(e.get("mode"), "Probe result")
            out.append(rec(f"L{s}", "ENGINE", title, grade, "reproduced_within_tolerance" if e.get("mode") == "reproduce"
                           else "not_independently_verified", content, led(e)))
        elif k == "freeze" and not p.get("rehearsal"):
            out.append(rec(f"L{s}", "B1", f"Frozen batch {p.get('batch_id')} (open; scored on forward data only)",
                           "process", "not_applicable",
                           {kk: p[kk] for kk in ("batch_id", "claims", "receipt", "test", "alpha", "frozen_at", "t0",
                                                  "source_rule", "accepted_at_freeze") if kk in p}, led(e)))
        elif k == "research_call" and e.get("mode") == "propose":
            continue  # the proposal mode's own calls are not loop reasoning (see EXCLUDED)
        elif k == "research_call":
            try:
                answer = json.loads(p.get("response_text") or "{}")
            except json.JSONDecodeError:
                answer = {"unparsed_response": p.get("response_text")}
            content = {"iteration": p.get("iteration"), "action": answer.get("action"), "note": answer.get("note"),
                       "owner_question": p.get("owner_question"),
                       "probe_rationale": (answer.get("probe") or {}).get("rationale"),
                       "probe_builds_on": (answer.get("probe") or {}).get("builds_on"),
                       "claim_batch": answer.get("claim_batch")}
            out.append(rec(f"L{s}", "ENGINE", "The researcher's own earlier decision and reasoning", "researcher_note",
                           "not_applicable", content, led(e)))
    # A repeated reproduction or rehearsal whose numbers equal an earlier record's is shortened to a pointer, so every
    # seq stays citable without repeating identical content.
    seen: dict[str, str] = {}
    for r in out:
        if r["source"].get("mode") not in ("reproduce", "vault_dryrun"):
            continue
        c = r["content"]
        key = json.dumps(c.get("comparisons") or c.get("checks") or c.get("vault_dryrun", {}).get("claims"),
                         sort_keys=True, default=str)
        if key in seen:
            ptr = {"identical_numbers_to": seen[key],
                   "note": "a repeat run (after a code change) that reproduced the same numbers"}
            for kk in ("leak_checks_passed", "accepted_arm"):
                if c.get(kk) is not None:
                    ptr[kk] = c[kk]
            r["content"] = ptr
        else:
            seen[key] = r["id"]
    return out


def exp4_records() -> list[dict]:
    d = "docs/experiment_4"
    res = json.loads(read(f"{d}/scored_run/results.json"))
    meta = json.loads(read(f"{d}/scored_run/run_meta.json"))
    src = lambda path, ptr="": {"path": path, "pointer": ptr, "run_id": 36823477529, "commit": "2b407f4"}
    out = [rec("X4-SPEC", "EXP4", "Experiment 4's frozen questions, comparators and reading rules (owner-approved)",
               "process", "not_applicable", read(f"{d}/ONE_PAGER.md"), {"path": f"{d}/ONE_PAGER.md"}),
           rec("X4-ROLE", "EXP4", "Experiment 4's place in the programme (owner directive, 2026-09-29)",
               "owner_directive", "not_applicable", read(f"{d}/PROGRAM_ROLE.md"), {"path": f"{d}/PROGRAM_ROLE.md"}),
           rec("X4-READING", "EXP4", "The frozen reading, as printed by the scored run", "discovery_grade_preregistered",
               "independently_reproduced", read(f"{d}/scored_run/summary.md"), src(f"{d}/scored_run/summary.md"))]
    for pid in ("P1", "P2", "P3", "P4"):
        out.append(rec(f"X4-{pid}", "EXP4", f"Experiment 4 primary {pid}", "discovery_grade_preregistered",
                       "independently_reproduced" if pid != "P2" else "internal_consistency_only",
                       {"primary": res["primaries"][pid], "verdict": res["verdicts"][pid],
                        "carry_forward": res["carry_forward"].get(pid)},
                       src(f"{d}/scored_run/results.json", f"/primaries/{pid}, /verdicts/{pid}, /carry_forward/{pid}")))
    read("solarbench/price_spec.py")
    out.append(rec("X4-CARRY", "EXP4", "Experiment 4's frozen carry-forward rule, what the vault can express, and the "
                   "route (PRICE_SPEC)", "process", "not_applicable", dict(PRICE_SPEC["carry_forward"]),
                   {"path": "solarbench/price_spec.py", "pointer": "PRICE_SPEC['carry_forward']"}))
    out.append(rec("X4-STRICT", "EXP4", "Experiment 4 strict check (report-only)", "exploratory",
                   "independently_reproduced", res["strict"], src(f"{d}/scored_run/results.json", "/strict")))
    out.append(rec("X4-SECONDARIES", "EXP4", "Experiment 4 secondaries (report-only, not adjusted for multiplicity)",
                   "exploratory", "independently_reproduced", res["secondaries"],
                   src(f"{d}/scored_run/results.json", "/secondaries")))
    for pid in ("P1", "P3", "P4"):
        out.append(rec(f"X4-SLICES-{pid}", "EXP4", f"Experiment 4 slices of {pid} (report-only, not adjusted)",
                       "exploratory", "independently_reproduced", res["slices"][pid],
                       src(f"{d}/scored_run/results.json", f"/slices/{pid}")))
        out.append(rec(f"X4-TABLES-{pid}", "EXP4", f"Experiment 4 concentration and bootstrap sensitivity of {pid}",
                       "exploratory", "independently_reproduced", res["tables"][pid],
                       src(f"{d}/scored_run/results.json", f"/tables/{pid}")))
    keep = ("selection", "k1", "k3", "k2_record", "leak_check", "prices", "agreement", "licence", "weather",
            "t0_weights", "missing_by_arm", "amendments", "versions")
    m = {k: meta[k] for k in keep if k in meta}
    leaves = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, bool):
            leaves.append(x)
    walk(meta["leak_check"])
    m["leak_check"] = {"pass": meta["leak_check"].get("pass"), "checks": len(leaves), "checks_true": sum(leaves),
                       "detail": "every control of PRICE_SPEC leak_controls at the 11 TEST_ORIGINS and P4's first day; "
                                 "full record in run_meta.json /leak_check"}
    m["k3"] = {k: v for k, v in meta["k3"].items() if k in ("pass", "conventions", "period", "days")}
    m["forecast"] = {k: v for k, v in meta["forecast"].items() if k != "p4_days"}
    m["forecast"]["p4_days"] = {k: v for k, v in meta["forecast"]["p4_days"].items() if k != "kept_days"}
    out.append(rec("X4-RUN", "EXP4", "Experiment 4 run record: selection on 2023, gates, data checks, provenance",
                   "process", "internal_consistency_only", m, src(f"{d}/scored_run/run_meta.json")))
    k1 = [json.loads(line) for line in read(f"{d}/k1_attempts.jsonl").splitlines() if line.strip()]
    out.append(rec("X4-K1", "EXP4", "K1: the LEAR reproduction gate, all three attempts (failed)", "process",
                   "not_independently_verified", k1, {"path": f"{d}/k1_attempts.jsonl"}))
    out.append(rec("X4-A1", "EXP4", "Amendment A1 and the unexplained long-window difference L1", "process",
                   "not_applicable", read(f"{d}/AMENDMENTS.md"), {"path": f"{d}/AMENDMENTS.md"}))
    out.append(rec("X4-T0FETCH", "EXP4", "Retrieval event: t0's frozen revision vanished upstream; weights loaded "
                   "by content", "process", "not_applicable", read(f"{d}/RETRIEVAL_EVENTS.md"),
                   {"path": f"{d}/RETRIEVAL_EVENTS.md"}))
    rep = read(f"{d}/INDEPENDENT_REPLICATION.md")
    out.append(rec("X4-REPLICATION", "EXP4", "Independent replication of Experiment 4's statistics (2026-10-01)",
                   "process", "not_applicable", "\n".join(section(rep, h) for h in (
                       "## Summary", "## 3. Checked for internal consistency only", "## 4. Not independently verified",
                       "## 5. Discrepancies", "## 6. Monte-Carlo robustness (Track 3, report-only)",
                       "## 7. What this means for reading Experiment 4", "## 8. Limits of this replication")),
                   {"path": f"{d}/INDEPENDENT_REPLICATION.md"}))
    return out


def readme_records() -> list[dict]:
    text = read("README.md")
    out = []
    for i, (exp, heading, skip) in enumerate(README_SECTIONS):
        out.append(rec(f"R-{exp}-{i}", exp, heading.lstrip("# "), "narrative", "not_applicable",
                       section(text, heading, skip), {"path": "README.md", "section": heading}))
    return out


def other_records() -> list[dict]:
    c1 = [json.loads(line) for line in read("ledger/confirmations.jsonl").splitlines() if line.strip()]
    return [
        rec("C1-CONFIRMATION", "C1", "Claim C1's one-shot confirmation on sealed 2025 data", "confirmed_on_sealed_data",
            "audited", c1, {"path": "ledger/confirmations.jsonl", "run_id": 36145552543, "commit": "46bf8b0"}),
        rec("T0-REPORT", "EXP3", "The project's summary of t0's technical report (the authors' claims) and its own "
            "notes on what was tested here",
            "external_report", "not_applicable", read("docs/experiment_3/T0_STRENGTHS.md"),
            {"path": "docs/experiment_3/T0_STRENGTHS.md", "report": "arXiv:2609.24559 (docs/2609.24559.pdf)"}),
        rec("DESIGN-1A-2", "DESIGN", "Experiments 1A and 2: pre-registration drafts", "design_only", "not_applicable",
            {"status": "design only: draft pre-registrations of a referee certification on synthetic data (1A) and a "
                       "blinded synthetic knowledge-creation benchmark (2); nothing ran, nothing was frozen",
             "where": "branch experiment-1a-preregistration, docs/experiment_1a/ and docs/experiment_2/ (draft PR #2)"},
            {"branch": "experiment-1a-preregistration"}),
    ]


def infrastructure_records(entries: list[dict]) -> list[dict]:
    dig = ledger.digest(entries)
    used = sum(1 for e in entries if e["kind"] == "probe_submitted" and e.get("mode") == "loop")
    return [
        rec("INFRA-ZONES", "INFRA", "Data zones (Europe/Paris local days)", "infrastructure", "not_applicable",
            {"discovery": [str(zones.DISCOVERY_START), str(zones.DISCOVERY_END)],
             "consumed_years": {str(k): v for k, v in zones.CONSUMED.items()},
             "forward_from": str(zones.FORWARD_FROM),
             "rule": "discovery data may be explored freely; a consumed year is explorable but never confirmable; "
                     "forward data are readable only through the vault, once, with the owner's approval"},
            {"path": "engine/zones.py"}),
        rec("INFRA-ENGINE-CATALOGUE", "INFRA", "What the engine's referee can run today (its catalogue)",
            "infrastructure", "not_applicable",
            {"t0": catalogue.T0, "targets": catalogue.TARGETS, "covariates": catalogue.COVARIATES,
             "comparators": catalogue.COMPARATORS, "metrics": catalogue.METRICS, "scopes": catalogue.SCOPES,
             "periods": catalogue.PERIODS, "limits": catalogue.LIMITS,
             "not_in_the_catalogue": "French day-ahead prices (Experiment 4's code lives outside the engine, in "
                                     "solarbench/price_*.py and run_prices.py); any data source not listed above"},
            {"path": "engine/catalogue.py"}),
        rec("INFRA-VAULT", "INFRA", "Confirmation rules of the forward vault", "infrastructure", "not_applicable",
            {"batch_budget": claims.BATCH_BUDGET, "alpha_per_batch": 0.05 / claims.BATCH_BUDGET,
             "batches_used": len([e for e in entries if e["kind"] == "freeze" and not e["payload"].get("rehearsal")]),
             "max_claims_per_batch": claims.MAX_CLAIMS, "deltas": list(claims.DELTAS),
             "embargo_days": claims.EMBARGO_DAYS, "window_days": claims.WINDOW_DAYS,
             "block_days": claims.BLOCK_DAYS, "min_days_per_block": claims.MIN_DAYS_PER_BLOCK,
             "min_window_blocks": claims.MIN_WINDOW_BLOCKS, "open_batches": dig["open_batches"],
             "one_open_batch_at_a_time": True,
             "consequence": "no new claim can be frozen until batch B1 has been opened (after 2027-04-01)"},
            {"path": "engine/claims.py", "ledger_seq": 56}),
        rec("INFRA-BUDGET", "INFRA", "The researcher's discovery budget", "infrastructure", "not_applicable",
            {"evaluations_total": budget.DISCOVERY_BUDGET, "evaluations_spent": budget.spent(entries),
             "evaluations_remaining": budget.remaining(entries),
             "unit": "one evaluation per comparison in a researcher probe; an identical probe (same probe hash) "
                     "returns its recorded result at no cost; referee and owner runs are not charged",
             "probes_submitted_by_the_researcher": used, "weather_usable_now": dig["weather_usable_now"]},
            {"path": "engine/referee/budget.py", "ledger_head_seq": LEDGER_HEAD["seq"]}),
        rec("INFRA-DATA", "INFRA", "Public data sources already wired, and their point-in-time rules",
            "infrastructure", "not_applicable",
            {"consumption_and_solar": "ODRÉ eco2mix national (definitive or consolidated) and regional series, "
                                      "30 min; RTE's own day-ahead forecast 'prevision_j1' is a reference only (its "
                                      "issue time is not verified)",
             "weather": "Open-Meteo previous-runs archive of ECMWF IFS 0.25°, run issued three days before "
                        "('previous_day3'), 12 regional points: temperature from 2024-02-06 (scorable from "
                        "2024-05-06 for consumption), radiation from 2024-03-08 (scorable from 2024-06-06); a "
                        "2-day-old forecast was not used because its issue time could not be verified",
             "prices": "French day-ahead prices from Energy-Charts (scored) and SMARD (cross-check), hourly, "
                       "2019-12-01..2025-12-31, CC BY 4.0; at 12:00 on D-1 every price of D-1 is already public",
             "decision_time": "12:00 Europe/Paris on D-1 for every experiment so far",
             "anything_else": "no other source is wired; a new one needs proof that each value was published "
                              "before the decision time, and a licence that allows this use"},
            {"paths": ["solarbench/covariates.py", "engine/covs.py", "solarbench/price_spec.py", "README.md#data"]}),
        rec("INFRA-T0", "INFRA", "The forecasting instrument", "infrastructure", "not_applicable",
            {"in_use": "t0-alpha (102M parameters), zero-shot, 90-day context; it emits five native quantiles "
                       "0.1..0.9; the engine and claim C1 request 0.1, 0.5 and 0.9 and score the median; Experiment "
                       "4 and Experiment 3's P1 used all five; covariates are passed as known-future inputs; the "
                       "past-only covariate route has never been used here",
             "covariate_roles": "in the pinned tfc-t0 0.3.2, predict() builds its input with TimeSeries.from_array, "
                                "which types every context row as TARGET (t0/data.py): an extra context series passed "
                                "through predict() is forecast jointly with the target as a co-target, and its horizon "
                                "is withheld. The HISTORICAL (past-covariate) role the t0 paper describes is reached "
                                "only through a hand-built TimeSeries passed to predict_from_time_series. The package "
                                "does not say which path produced the paper's past-covariate results, and no "
                                "experiment here has passed a past covariate by either path. The only multi-row "
                                "predict() context so far is Experiment 3's P3 (L6, R-EXP3-3): the 12 regional solar "
                                "series forecast jointly as co-targets, joint vs independent +0.1%. Known-future "
                                "covariates span context and horizon, "
                                "are standardised with statistics over that whole span (t0/scaler.py), and are read "
                                "bidirectionally (t0/mask.py), so every value in the span enters every forecast",
             "loading": "Experiment 4 loads t0-alpha by the sha256 of its weight files (the frozen revision id "
                        "vanished upstream on 2026-09-29); the engine and earlier experiments still load it by that "
                        "revision id, so an engine probe would currently fail to load t0 until that is fixed",
             "t0_beta": "the authors' larger t0-beta is reported as stronger on their benchmarks; it has never been "
                        "tested here, and no frozen experiment may switch from alpha to beta"},
            {"paths": ["docs/experiment_3/T0_STRENGTHS.md", "docs/experiment_4/RETRIEVAL_EVENTS.md",
                       "solarbench/t0_pinned.py", "engine/catalogue.py",
                       "tfc-t0 0.3.2: t0/data.py, t0/model/model.py, t0/scaler.py, t0/mask.py",
                       "solarbench/forecasters.py (T0_QUANTILES)", "solarbench/probes.py (T0JointForecaster)",
                       "branch experiment-1a-preregistration: docs/experiment_2/PREREGISTRATION.md section T.1, "
                       "rows M-02 and M-10 (findings only)"]}),
        rec("INFRA-COST", "INFRA", "Observed run costs", "infrastructure", "not_applicable",
            {"experiment_4_scored_run": "about 39 minutes of the run step on a standard Actions runner, CPU only, "
                                        "nine arms over 731 days (FACT_SHEET section 4)",
             "engine_probe": "one probe of up to 3 arms over 2022-2025 runs within one Actions job",
             "research_call": "earlier researcher calls used about 13-19 thousand input tokens and 0.7-1.5 "
                              "thousand output tokens each"},
            {"paths": ["docs/experiment_4/scored_run/FACT_SHEET.md", "engine-ledger research_call entries"]}),
    ]


def render_md(pack: dict) -> str:
    lines = [f"# Evidence pack `{pack['pack_version']}`", "",
             "Built mechanically by `build_evidence_pack.py`. Each record has an id to cite.", "",
             "## Evidence grades", ""]
    lines += [f"- **{k}**: {v}" for k, v in pack["evidence_grades"].items()]
    lines += ["", "## Verification labels", ""]
    lines += [f"- **{k}**: {v}" for k, v in pack["verification_labels"].items() if v]
    lines += ["", "## Deliberately excluded", ""]
    lines += [f"- {x['what']}. *Why:* {x['why']}." for x in pack["excluded"]]
    lines += ["", "## Records", ""]
    for r in pack["records"]:
        lines += [f"### {r['id']}: {r['title']}", "",
                  f"*Experiment:* {r['experiment']} · *grade:* {r['evidence_grade']} · *verification:* "
                  f"{r['verification']} · *source:* `{json.dumps(r['source'], ensure_ascii=False)}`", ""]
        if isinstance(r["content"], str):
            lines += ["````text", r["content"].rstrip("\n"), "````", ""]
        else:
            lines += ["```json", json.dumps(r["content"], indent=1, ensure_ascii=False, default=str), "```", ""]
    return "\n".join(lines) + "\n"


def main() -> int:
    head = git("rev-parse", LEDGER_REF).strip()
    if head != LEDGER_HEAD["git"]:
        raise SystemExit(f"{LEDGER_REF} is at {head}, not the pinned {LEDGER_HEAD['git']}")
    raw = git("show", f"{LEDGER_REF}:ledger.jsonl")
    entries = [json.loads(line) for line in raw.splitlines() if line.strip()]
    ledger.verify_chain(entries)
    if entries[-1]["seq"] != LEDGER_HEAD["seq"]:
        raise SystemExit("unexpected ledger head")
    readme, led, other = readme_records(), ledger_records(entries), other_records()
    of = lambda *exps: [r for r in led if r["experiment"] in exps]
    # Chronological: Experiment 0, the covariate slice, Experiment 3 and the t0 report, C1, the engine and B1,
    # Experiment 4, the design-only drafts, the README's known limitations, then the infrastructure facts.
    records = (readme[:2] + of("EXP0") + [readme[2]] + of("COV") + [readme[3]] + of("EXP3") + [other[1]]
               + [readme[4], other[0]] + of("C1") + [readme[6]] + of("ENGINE", "B1") + exp4_records()
               + [other[2], readme[5]]
               + infrastructure_records(entries))
    # The code the infrastructure records are computed from (gates.FINGERPRINT_FILES and catalogue.T0 decide
    # weather_usable_now), and this builder: the proposal call refuses the pack if any of them changed since.
    for rel in ("docs/experiment_5/build_evidence_pack.py", "engine/catalogue.py", "engine/claims.py", "engine/zones.py",
                "engine/referee/budget.py", "engine/ledger.py", *gates.FINGERPRINT_FILES):
        read(rel)
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate record ids")
    pack = {"pack_version": PACK_VERSION,
            "built_from": {"ledger": {"ref": "engine-ledger", "head_seq": entries[-1]["seq"],
                                      "head_sha256": entries[-1]["sha256"], "git": head},
                           "repo_files_sha256": dict(sorted(FILES.items()))},
            "evidence_grades": GRADES, "verification_labels": VERIFICATION, "excluded": EXCLUDED,
            "record_ids": ids, "records": records}
    blob = (json.dumps(pack, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str) + "\n").encode("utf-8")
    (HERE / "evidence_pack.json").write_bytes(blob)
    (HERE / "evidence_pack.md").write_text(render_md(pack), encoding="utf-8")
    print(f"{len(records)} records, {len(blob):,} bytes, sha256 {sha256(blob)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
