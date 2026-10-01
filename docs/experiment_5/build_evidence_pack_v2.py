"""Build the evidence pack for the second proposal-only decision (mandate v2), mechanically, from recorded sources.

The first pack (``evidence_pack.json``, sha256 64e93aaf…, built against ledger head 72) is history and is not
rebuilt: its committed bytes are read, checked against their hash, and its 85 records are kept verbatim. Between
ledger seqs 72 and 74 the ledger gained only a config entry and the first proposal call, so those records are still
current, with one exception: ``INFRA-COST`` is replaced, because it predates the proposal calls (disclosed in the
pack). Added, at the owner's request (``NORTH_STAR_CLARIFICATION.md``, section 5 and 11):

- the first decision: its mandate (E5-MANDATE-V1) and rules text (E5-RULES-V1), its interface events
  (E5-PROCESS-V1) and its answer, verbatim,
  in parts (E5-P1-*), labelled as the decision under the previous mandate;
- the engineering team's fact-check annotations (E5-ANNOT) and feasibility review (E5-REVIEW-*) of that answer, and
  the review's power analogue (E5-POWER);
- the owner's clarification, verbatim, by section (OWNER-NS2-*);
- facts about historical data coverage read from the code (INFRA-DATA-HISTORY), and the replaced INFRA-COST.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/build_evidence_pack_v2.py
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

from engine import arms, catalogue, covs, ledger, propose_v2, researcher, zones  # noqa: E402
from solarbench import price_data, price_spec, weather  # noqa: E402

LEDGER_REF = "origin/engine-ledger"
LEDGER_HEAD = {"seq": 74, "git": "e743eceb90d5e2d94ea621f4078e4733a7c5bd06"}
V1_PACK = "docs/experiment_5/evidence_pack.json"
V1_PACK_SHA256 = "64e93aaf66487c054e0bf2eb455f17fe6675321258757c9765485ccaf8a53cdd"
PACK_VERSION = "exp5-evidence/2"

NEW_GRADES = {
    "researcher_proposal": ("the AI researcher's own earlier answer in proposal mode, verbatim, under the mandate named "
                            "in the record; it is the researcher's reasoning at the time, a claim to evaluate, not "
                            "evidence"),
    "engineering_review": ("written by the engineering orchestrator after a read-only review in which independent "
                           "skeptics checked each finding; its readings and recommendations are claims to evaluate, "
                           "and where it conflicts with the owner's latest clarification, the clarification takes "
                           "precedence"),
}

EXCLUDED = [
    {"what": "Engineering recommendations about which experiment to run next, including the orchestrator's report to "
             "the owner after the first proposal (its options and recommendation, made in chat)",
     "why": "the researcher, not the engineering orchestrator, chooses the next investigation; the one exception is "
            "the feasibility review of the first proposal, included at the owner's request (E5-REVIEW-*)"},
    {"what": "README sections not included as records in the first pack (the introduction, methods and operating "
             "sections such as 'Data', 'Useful flags' and 'Scope', the Experiment 4 and Experiment 5 sections)",
     "why": "methods and operating documentation, or a restatement of records included here; the first pack's README "
            "records are kept verbatim; the operating facts that bear on data history and t0's context length are "
            "in INFRA-DATA-HISTORY"},
    {"what": "Experiment 4's FACT_SHEET.md, verify_*.md, k2_attempts.jsonl, and INDEPENDENT_REPLICATION.md sections 1, "
             "2 and 'Files'",
     "why": "they restate included records (as in the first pack)"},
    {"what": "The per-day series ('per_day') of every probe_result and vault-rehearsal record, and the probe records' "
             "per-method leak-check detail, dropped_nonfinite and data fields; windows_built is kept only in "
             "INFRA-COST, for the six consumption probes over period ALL (seqs 51, 54, 60, 63, 66, 69)",
     "why": "size; the full series stay on the ledger at the cited seq. LEDGER-PER-YEAR gives every probe_result's "
            "per-day series summarised by calendar year (days and mean daily MAE per method); E5-POWER holds "
            "bootstrap statistics (skill, interval, SD, MDE) by pair, year and season, computed from the per-day "
            "errors of seq 51 on the 602 days the B1 arm was scored"},
    {"what": "Ledger entries of kind genesis (seq 0) and probe_submitted, and the payloads (code fingerprints) of "
             "config entries",
     "why": "code fingerprints and submissions whose content reappears in other records; they stay on the ledger. "
            "Config seqs 71 and 73 appear in E5-PROCESS-V1 with seq, time, run, commit and mode only"},
    {"what": "Model identifiers and request ids of research calls, and the full prompts and responses of the loop's "
             "research calls",
     "why": "not evidence about forecasting; they stay on the ledger. Token usage is in INFRA-COST"},
    {"what": "The first decision's brief and prompt appendix (RESEARCHER_BRIEF.md, brief_appendix.md) and the answer "
             "schema that was part of its system text",
     "why": "they describe the first call's interface; its mandate and its rules text (the instructions that framed "
            "I1) are in E5-MANDATE-V1 and E5-RULES-V1, and the first pack's records are included unchanged"},
    {"what": "Part 2 of NORTH_STAR_CLARIFICATION.md (the engineering note comparing the two mandates)",
     "why": "engineering commentary; the owner's text is included verbatim (OWNER-NS2-*) and the previous mandate is "
            "E5-MANDATE-V1, so the two can be compared directly"},
    {"what": "FEASIBILITY_REVIEW.md's 'Files' section except its 'Where the numbers come from' block (included in "
             "E5-REVIEW-SUMMARY), and the scripts that render or compute the Experiment 5 documents",
     "why": "file lists and code; their outputs are included"},
    {"what": "B1_T0_LOADING_DESIGN.md (the design for loading t0 in batch B1's future vault run)",
     "why": "engineering design for a frozen batch the researcher may not change; INFRA-T0, X4-T0FETCH and "
            "E5-REVIEW-3 state the loading problem"},
    {"what": "Any data from 2026 onward",
     "why": "sealed: readable only through the forward vault"},
]

FILES: dict[str, str] = {}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_bytes(rel: str) -> bytes:
    b = (ROOT / rel).read_bytes()
    FILES[rel] = sha256(b)
    return b


def read(rel: str) -> str:
    return read_bytes(rel).decode("utf-8")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def rec(rid, experiment, title, grade, verification, content, source) -> dict:
    return {"id": rid, "experiment": experiment, "title": title, "evidence_grade": grade,
            "verification": verification, "content": content, "source": source}


def h2_sections(text: str) -> list[tuple[str, str]]:
    """(heading, body) for each '## ' section, body including the heading line."""
    parts = re.split(r"(?m)^(?=## )", text)
    return [(p.split("\n", 1)[0][3:].strip(), p.strip() + "\n") for p in parts if p.startswith("## ")]


# ------------------------------------------------------------------ the first decision


def first_decision_records(entries: list[dict]) -> list[dict]:
    from engine import propose as v1
    replaced_by = "the owner's clarification of 2026-10-01 (OWNER-NS2-*)"
    out = [rec("E5-MANDATE-V1", "EXP5", "The mandate the first proposal answered (v1), verbatim; superseded by the "
                                        "owner's clarification", "owner_directive", "not_applicable",
               {"mandate": v1.MANDATE, "mandate_sha256": sha256(v1.MANDATE.encode("utf-8")),
                "replaced_by": replaced_by},
               {"path": "engine/propose.py", "constants": ["MANDATE"]}),
           rec("E5-RULES-V1", "EXP5", "The rules text the first proposal answered (v1), verbatim; written by "
                                      "engineering; superseded by the owner's clarification", "process",
               "not_applicable",
               {"rules_text": v1.PROPOSAL_RULES, "rules_sha256": sha256(v1.PROPOSAL_RULES.encode("utf-8")),
                "note": ("the first call's system text without its answer schema, written by engineering; it embeds "
                         "the owner's v1 mandate (E5-MANDATE-V1), and only that part is the owner's; its sha256 is "
                         "the proposal_rules_sha256 recorded at ledger seq 74 (E5-PROCESS-V1)"),
                "replaced_by": replaced_by},
               {"path": "engine/propose.py", "constants": ["PROPOSAL_RULES"]})]
    read("engine/propose.py")
    keep = ("seq", "kind", "at", "run_id", "code_commit", "mode")
    events = []
    for e in entries:
        if not 71 <= e["seq"] <= 74:  # the first decision's entries only
            continue
        item = {k: e.get(k) for k in keep}
        p = e.get("payload") or {}
        if e["kind"] == "research_call":
            item.update({k: p.get(k) for k in ("purpose", "attempt", "retry", "stop_reason", "action", "error",
                                               "usage", "ledger_head", "evidence_pack_sha256", "system_sha256",
                                               "proposal_rules_sha256", "schema_sha256") if k in p})
            if "error" in item:  # the error text embeds the request id: dropped, as the other ids are
                item["error"] = re.sub(r",?\s*'request_id':\s*'[^']*'", "", str(item["error"]))[:300]
        events.append(item)
    out.append(rec("E5-PROCESS-V1", "EXP5", "How the first proposal call ran (ledger seqs 71-74)", "process",
                   "not_applicable",
                   {"events": events,
                    "summary": ("the first dispatch (run 36855164105) was rejected by the API before any answer "
                                "(its answer schema was sent as a grammar-constrained format that was too large to "
                                "compile). Before the second dispatch the schema was sent as text and checked in code "
                                "(so the system text changed, system_sha256 5cc6c446... to 29b8b29b...), and the "
                                "first evidence pack was rebuilt against ledger head 72 instead of 70, because the "
                                "call refuses a pack built against an older head: its 85 records' content was "
                                "unchanged (only INFRA-BUDGET's source now names head 72 instead of 70), and its "
                                "build header and exclusion list changed, which is why seqs 72 and 74 carry "
                                "different evidence_pack_sha256. The second dispatch (run 36855466970) was answered "
                                "in one request with no repair"),
                    "omitted_fields": ("only the keys shown are kept from each entry; dropped among others: model "
                                       "identifiers, request ids, the full prompts and their hashes, the response text "
                                       "(records E5-P1-*), effort, iteration, transient, evidence_pack_path, "
                                       "run_attempt, actor, the chain hashes, and the config payloads of seqs 71 and "
                                       "73")},
                   {"ledger": "engine-ledger seqs 71-74"}))
    answer = json.loads(read(f"docs/experiment_5/researcher_output.json"))
    label = "I1 was the researcher's decision under the previous mandate."
    src = {"path": "docs/experiment_5/researcher_output.json", "ledger": "seq 74 payload.response_text",
           "mandate": "E5-MANDATE-V1", "rules": "E5-RULES-V1"}
    parts = [("E5-P1-DECISION", f"The first proposal: action, summary and decision. {label}",
              {"action": answer["action"], "summary": answer["summary"], "D_decision": answer["D_decision"]}),
             ("E5-P1-A", "The first proposal, section A: what it believed had been learned",
              {"A_learned": answer["A_learned"]}),
             ("E5-P1-B", "The first proposal, section B: what remained unexplained",
              {"B_unexplained": answer["B_unexplained"]})]
    for c in answer["C_candidates"]:
        parts.append((f"E5-P1-{c['id']}", f"The first proposal's candidate {c['id']}"
                      + (f" (chosen). {label}" if c["id"] == answer["D_decision"]["chosen"] else ""), c))
    parts += [("E5-P1-E", f"The first proposal, section E: the protocol proposed for I1. {label}",
               {"E_protocol": answer["E_protocol"]}),
              ("E5-P1-F", "The first proposal, section F: how each outcome would update knowledge",
               {"F_knowledge_update": answer["F_knowledge_update"]})]
    out += [rec(rid, "EXP5", title, "researcher_proposal", "not_applicable", content, src)
            for rid, title, content in parts]
    return out


def review_records() -> list[dict]:
    annot = read("docs/experiment_5/RESEARCHER_PROPOSAL.md")
    marker = "## 3. Engineering annotations (not the researcher's)"
    if annot.count(marker) != 1:
        raise SystemExit("RESEARCHER_PROPOSAL.md: annotation section not found exactly once")
    out = [rec("E5-ANNOT", "EXP5", "Engineering fact-check of the first proposal (the flags that survived skeptics)",
               "engineering_review", "audited", marker + annot.split(marker, 1)[1],
               {"path": "docs/experiment_5/RESEARCHER_PROPOSAL.md", "section": marker[3:]})]
    review = read("docs/experiment_5/FEASIBILITY_REVIEW.md")
    preamble = review.split("\n## ", 1)[0].strip() + "\n\n"
    sections = h2_sections(review)
    files = dict(sections)["Files"]
    provenance = "**Where the numbers come from:**" + files.split("**Where the numbers come from:**", 1)[1]
    for heading, body in sections:
        if heading == "Files":
            continue
        m = re.match(r"^(\d+)\. ", heading)
        rid = f"E5-REVIEW-{m.group(1)}" if m else "E5-REVIEW-SUMMARY"
        if rid == "E5-REVIEW-SUMMARY":  # the review's title and scope, then the summary, then its provenance note
            body = preamble + body + "\n(From the review's 'Files' section:)\n\n" + provenance
        out.append(rec(rid, "EXP5", f"Feasibility review of the first proposal: {heading}", "engineering_review",
                       "audited", body, {"path": "docs/experiment_5/FEASIBILITY_REVIEW.md", "section": heading}))
    power = json.loads(read("docs/experiment_5/feasibility_power.json"))
    out.append(rec("E5-POWER", "EXP5", "Power analogue: bootstrap precision of paired comparisons on the 602 days of "
                                       "ledger seq 51, by pair, year and season", "exploratory", "audited", power,
                   {"path": "docs/experiment_5/feasibility_power.json",
                    "computed_by": "docs/experiment_5/feasibility_power.py from engine-ledger seq 51 per_day"}))
    return out


def owner_records() -> list[dict]:
    read("docs/experiment_5/NORTH_STAR_CLARIFICATION.md")
    text = propose_v2.owner_text()
    pieces = text.split("\n---\n")
    out = []
    for i, piece in enumerate(pieces):
        body = piece.strip() + "\n"
        title = body.split("\n", 1)[0].lstrip("# ").strip()
        out.append(rec(f"OWNER-NS2-{i}", "OWNER", f"Owner clarification (2026-10-01): {title}", "owner_directive",
                       "not_applicable", body,
                       {"path": "docs/experiment_5/NORTH_STAR_CLARIFICATION.md", "part": "1 (verbatim)",
                        "section": i}))
    return out


# ------------------------------------------------------------------ infrastructure


def cost_record(entries: list[dict], v1_cost: dict) -> dict:
    read("engine/researcher.py")
    loop = [e["payload"] for e in entries if e["kind"] == "research_call" and e.get("mode") == "loop"
            and (e["payload"].get("usage") or {}).get("input_tokens")]
    span = lambda key: [min(p["usage"][key] for p in loop), max(p["usage"][key] for p in loop)]  # noqa: E731
    v1_call = next(e for e in entries if e["seq"] == 74)
    probes = [{"seq": e["seq"], "scope": e["payload"].get("scope"),
               "candidate_arms": len((e["payload"].get("spec") or {}).get("arms") or []),
               "comparisons": len(e["payload"].get("comparisons") or []),
               "windows_built": e["payload"].get("windows_built"), "elapsed_s": e["payload"].get("elapsed_s")}
              for e in entries if e["kind"] == "probe_result" and e["payload"].get("target") == "consumption"
              and e["payload"].get("period") == "ALL" and e["payload"].get("elapsed_s")]
    content = dict(v1_cost["content"])
    content["experiment_4_scored_run_qualifier"] = ("4 of the nine arms were t0 arms, and about 19 of the 39 minutes "
                                                    "were price download (see E5-REVIEW-4 for the engine's recorded "
                                                    "rate per t0 day-forecast)")
    content["research_call"] = {
        "loop_calls": {"count": len(loop), "input_tokens": span("input_tokens"),
                       "cache_creation_input_tokens": span("cache_creation_input_tokens"),
                       "output_tokens": span("output_tokens"), "ledger_seqs": [49, 70]},
        "first_proposal_call": {"ledger_seq": 74, "usage": v1_call["payload"]["usage"],
                                "note": "one request, no repair; the failed first dispatch (seq 72) reported no usage"},
        "daily_token_cap": (f"{researcher.DEFAULT_TOKEN_CAP:,} tokens per UTC day across research calls by default "
                            "(input, output and cache tokens counted)")}
    content["engine_probe"] = {
        "statement": v1_cost["content"]["engine_probe"],
        "consumption_probes_period_ALL": probes,
        "note": ("elapsed_s covers data download, window building, live leak checks and the backtests of one probe; "
                 "a scoped probe (winter or summer) builds fewer windows")}
    return rec("INFRA-COST", "INFRA", "Observed run costs (replaces the first pack's record of the same id)",
               "infrastructure", "not_applicable", content,
               {"paths": ["docs/experiment_4/scored_run/FACT_SHEET.md", "engine/researcher.py (DEFAULT_TOKEN_CAP)",
                          "docs/experiment_5/FEASIBILITY_REVIEW.md section 4"],
                "ledger": "engine-ledger research_call and probe_result entries to seq 74"})


def data_history_record() -> dict:
    for rel in ("engine/zones.py", "engine/arms.py", "engine/covs.py", "engine/catalogue.py", "engine/data.py",
                "solarbench/weather.py", "solarbench/odre.py", "solarbench/data.py", "solarbench/backtest.py",
                "solarbench/probes.py", "solarbench/price_data.py", "solarbench/price_spec.py",
                "solarbench/price_gates.py", "run_benchmark.py", "run_probes.py", "run_confirm.py", "run_prices.py"):
        read(rel)
    covariate_runner = read("run_covariates.py")
    era5 = re.search(r'WX_FETCH_START, WX_FETCH_END = "([\d-]+)", "([\d-]+)"', covariate_runner).groups()
    periods = price_spec.PRICE_SPEC["periods"]
    content = {
        "engine_zones": {
            "discovery": [zones.DISCOVERY_START.isoformat(), zones.DISCOVERY_END.isoformat()],
            "consumed_years": {str(k): v for k, v in zones.CONSUMED.items()},
            "before_the_discovery_zone": ("days before the discovery zone may be read as context (each engine read "
                                          f"starts {arms.LEAD_IN_DAYS} days before the scored period) but an engine "
                                          "probe never scores them: probes name one of the fixed periods "
                                          f"{sorted(catalogue.PERIODS)}"),
            "context": (f"t0's context in the engine is fixed at {catalogue.T0['context_days']} days, in the "
                        "referee-owned catalogue entry T0; the catalogue sha256 recorded in every probe result and in "
                        "the frozen batch covers it, while the gate fingerprint covers only T0's repo and revision (a "
                        "change to context_days would not invalidate a gate pass)")},
        "t0_context_outside_the_engine": (
            "outside the engine, t0's context length is a run parameter: run_benchmark.py, run_probes.py, "
            "run_confirm.py and run_covariates.py take --context-days (default 90), and no workflow has passed "
            "another value. A day without a full context is skipped, not forecast from a shorter history "
            "(solarbench/backtest.py, skipped_short_history). Experiment 4's frozen spec fixes the price context at "
            f"{price_spec.PRICE_SPEC['t0']['context_hours']} hours and run_prices.py has no such flag. Every recorded "
            "t0 forecast of a target series used a 90-day context; the one shorter context is Experiment 3's P1/P2 "
            f"residual model (L4, L5), where t0 read {__import__('solarbench.probes', fromlist=['x']).RESID_CONTEXT_DAYS} "
            "days of wx_ratio's past errors"),
        "solarbench_doors": ("solarbench/odre.py's fetch_columns (ODRÉ consumption and regional exports) refuses dates "
                             f"from {weather.SEALED_FROM.isoformat()} unless given the one-shot access of claim C1's "
                             "sealed-data vault, which has been used (ledger/confirmations.jsonl); solarbench/weather.py's "
                             "fetchers (fetch_previous_runs, fetch_era5, fetch_single_run; Open-Meteo archives) refuse "
                             f"dates from {weather.SEALED_FROM.isoformat()} with no exception. Neither sets an earlier "
                             "limit. Experiment 0's loader (solarbench/data.py) has no date check. The engine's door "
                             "(engine/data.py) calls these modules' unguarded download helpers (odre._download_columns, "
                             "weather.fetch_json) and applies the engine's zones instead (engine_zones above: discovery "
                             "to 2025-12-31; the forward zone only through the vault); this is how the engine read "
                             "2022-2025 ODRÉ and Open-Meteo data. Experiment 4's price door applies the engine's zones"),
        "prices": {"fetched_window": periods["fetch_prices"],
                   "fetch_start_rule": periods["price_first_day_max"],
                   "scored_periods": {"selection": periods["selection"], "k3_gate": periods["k3_gate"],
                                      "test": periods["test"]},
                   "not_scored": ("2019-12-01..2022-12-31 were read only as LEAR training windows and lags, t0 "
                                  "contexts and, from 2022-01-01, the SMARD cross-check; no price error was scored "
                                  "there"),
                   "first_day_requested_and_checked_complete": price_spec.AVAIL["price_first_day"],
                   "also_fetched": {**periods["fetch_prices_overlap_check"],
                                    "compared_with": "EPF-FR's FR.csv, to decide the price stamp convention"},
                   "quarter_hour_products_from": price_data.QUARTER_HOUR_FROM.isoformat(),
                   "quarter_hour_rule": "from that delivery day each hour is the mean of its four quarter-hour prices"},
        "weather_forecast_archive": {
            "temperature_previous_day3_valid_from": covs.TEMPERATURE_FIRST,
            "radiation_previous_day3_valid_from": "2024-03-08 (engine/arms.py)",
            "model": covs.TEMPERATURE_MODEL,
            "other_models": ("ARPEGE, ICON and GFS returned identical 2024 coverage to four decimals (not independent "
                             "archives), and GFS's apparent 2022-2023 history could not be verified, so they are not "
                             "used (engine/covs.py)")},
        "reanalysis": ("ERA5 (Open-Meteo archive) is read only by the solarbench covariate-slice code "
                       f"(run_covariates.py), for {era5[0]}..{era5[1]}, as a declared oracle that is never "
                       f"point-in-time; solarbench/weather.py refuses it from {weather.SEALED_FROM.isoformat()}, and the "
                       "engine has no ERA5 reader"),
        "epf_fr": ("the public EPF-FR file (Zenodo 4624805, FR.csv: prices, a generation forecast and a system load "
                   "forecast) has two uses in Experiment 4, neither feeding a scored arm: deciding the price stamp "
                   "convention (compared with Energy-Charts 2015-2016 prices), and the K1 code check scored on "
                   "2015-01-04..2016-12-31, whose LEAR windows of up to 1456 days read FR.csv rows from about 2011"),
        "transcribed": ("the radiation start date, the other-models note and the EPF-FR description are transcribed "
                        "from the cited files rather than read as constants"),
    }
    return rec("INFRA-DATA-HISTORY", "INFRA", "Historical data coverage, access rules and t0's context length, "
                                              "from the code", "infrastructure", "not_applicable", content,
               {"paths": ["engine/zones.py", "engine/arms.py", "engine/catalogue.py", "engine/covs.py",
                          "engine/data.py", "solarbench/weather.py", "solarbench/odre.py", "solarbench/data.py",
                          "solarbench/backtest.py", "solarbench/probes.py", "solarbench/price_data.py",
                          "solarbench/price_spec.py", "solarbench/price_gates.py", "run_benchmark.py",
                          "run_probes.py", "run_confirm.py", "run_covariates.py", "run_prices.py"]})


def loop_digest_record() -> dict:
    read("engine/ledger.py")
    content = {
        "what_each_loop_call_sees": ("the loop's system text (its rules, the owner's objective and the catalogue "
                                     "brief) and one user message: the iteration number, the "
                                     "remaining discovery budget, the owner's question if there is one, and the "
                                     "ledger digest; there is no message history between iterations or runs"),
        "digest_includes": ["the ledger head", "accepted findings (last 100) and the accepted arm per target",
                            "all legacy_result summaries", "the last 40 probe_result entries, compacted to arms, "
                            "spec rationale, scope, period, eligible days and comparisons (skill, interval, p, MAE, "
                            "days won and lost)", "the last 10 probe rejections", "the last 50 gates and the weather "
                            "covariates usable now", "the last 10 errors", "the last 10 engine notes (rule changes "
                            "and duplicates)", "open batches (window only) and verdicts", "a count of entries per kind"],
        "digest_excludes": ["every research_call payload: only their count appears. These are the loop researcher's "
                            "own earlier notes and responses (the researcher_note records L49, L52, L55, L58, L61, "
                            "L64, L67 and L70; the probe results and the B1 freeze between them do appear in the "
                            "digest) and the two proposal-mode calls (seqs 72 and 74), which carry the first evidence "
                            "pack in full; seq 74 also carries the first proposal",
                            "per-day series", "probe_submitted and config entries",
                            "everything not on the ledger: Experiment 4 and its replication, the first proposal's "
                            "review, and this evidence pack"],
    }
    return rec("INFRA-LOOP-DIGEST", "INFRA", "What the engine loop's researcher remembers between calls (its ledger "
                                             "digest)", "infrastructure", "not_applicable", content,
               {"paths": ["engine/ledger.py (digest)", "engine/researcher.py (system_prompt, user_prompt)"]})


def per_year_record(entries: list[dict]) -> dict:
    table = {}
    for e in entries:
        if e["kind"] != "probe_result" or not (e["payload"].get("per_day") or {}).get("dates"):
            continue
        p = e["payload"]
        days = p["per_day"]["dates"]
        methods = {}
        for m, values in p["per_day"]["mae_mw"].items():
            by_year: dict[str, list[float]] = {}
            for day, v in zip(days, values):
                if v is not None:
                    by_year.setdefault(day[:4], []).append(v)
            methods[m] = {y: {"days": len(v), "mean_daily_mae_mw": round(sum(v) / len(v), 1)}
                          for y, v in sorted(by_year.items())}
        table[str(e["seq"])] = {"target": p.get("target"), "period": p.get("period"), "scope": p.get("scope"),
                                "methods": methods}
    return rec("LEDGER-PER-YEAR", "ENGINE", "Every probe_result's per-day errors summarised by calendar year",
               "exploratory", "internal_consistency_only",
               {"how": ("for each probe_result with a per-day series: per method and calendar year, the number of "
                        "scored days and the unweighted mean of the recorded daily MAE (MW); every series is "
                        "included, none is selected; method names are those of the probe record at the same seq. "
                        "Calendar years are a fixed grouping, not a regime definition; the owner's rules 'Do not "
                        "manufacture a regime definition after seeing results' (OWNER-NS2-4) and 'Any regime boundary "
                        "must be defined from information available independently of the result' (OWNER-NS2-8) apply "
                        "to any regime boundary drawn from these figures"),
                "by_seq": table},
               {"ledger": "engine-ledger probe_result entries, payload.per_day, to seq 74"})


# ------------------------------------------------------------------ the pack


def render_md(pack: dict) -> str:
    lines = [f"# Evidence pack `{pack['pack_version']}`", "",
             "Built mechanically by `build_evidence_pack_v2.py`. Each record has an id to cite.", "",
             "## Evidence grades", ""]
    lines += [f"- **{k}**: {v}" for k, v in pack["evidence_grades"].items()]
    lines += ["", "## Verification labels", ""]
    lines += [f"- **{k}**: {v}" for k, v in pack["verification_labels"].items() if v]
    lines += ["", "## Changed from the first pack", ""] + [f"- {x}" for x in pack["changes_from_first_pack"]]
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
    entries = [json.loads(line) for line in git("show", f"{LEDGER_REF}:ledger.jsonl").splitlines() if line.strip()]
    ledger.verify_chain(entries)
    if entries[-1]["seq"] != LEDGER_HEAD["seq"]:
        raise SystemExit("unexpected ledger head")
    v1_bytes = read_bytes(V1_PACK)
    if sha256(v1_bytes) != V1_PACK_SHA256:
        raise SystemExit(f"{V1_PACK} is not the first pack (sha256 {sha256(v1_bytes)})")
    v1 = json.loads(v1_bytes)
    old = v1["records"]
    by_id = {r["id"]: r for r in old}
    infra_at = next(i for i, r in enumerate(old) if r["experiment"] == "INFRA")
    data_at = [r["id"] for r in old].index("INFRA-DATA")
    infra = [cost_record(entries, by_id["INFRA-COST"]) if r["id"] == "INFRA-COST" else r for r in old[infra_at:]]
    infra.insert(data_at - infra_at + 1, data_history_record())
    infra.append(loop_digest_record())
    records = (old[:infra_at] + [per_year_record(entries)] + first_decision_records(entries) + review_records()
               + owner_records() + infra)
    read("docs/experiment_5/build_evidence_pack_v2.py")
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)) or set(ids) & set(propose_v2.CANDIDATE_IDS):
        raise SystemExit("duplicate record ids, or a record id equal to a candidate id")
    grades = {**v1["evidence_grades"], **NEW_GRADES}
    for r in records:
        assert r["evidence_grade"] in grades and r["verification"] in v1["verification_labels"], r["id"]
    pack = {"pack_version": PACK_VERSION,
            "built_from": {"ledger": {"ref": "engine-ledger", "head_seq": entries[-1]["seq"],
                                      "head_sha256": entries[-1]["sha256"], "git": head},
                           "first_pack": {"path": V1_PACK, "sha256": V1_PACK_SHA256,
                                          "ledger_head_seq": v1["built_from"]["ledger"]["head_seq"]},
                           "repo_files_sha256": dict(sorted(FILES.items()))},
            "changes_from_first_pack": [
                "the first pack's 85 records are kept verbatim, except INFRA-COST, which is replaced because it "
                "predates the proposal calls",
                "between ledger seqs 72 and 74 the ledger gained only a config entry (73) and the first proposal "
                "call (74): no probe, gate, freeze or vault entry, and no evaluation spent; INFRA-BUDGET (computed "
                "at seq 72) is therefore unchanged",
                "added: LEDGER-PER-YEAR, E5-MANDATE-V1, E5-RULES-V1, E5-PROCESS-V1, E5-P1-*, E5-ANNOT, E5-REVIEW-*, "
                "E5-POWER, "
                "OWNER-NS2-*, INFRA-DATA-HISTORY, INFRA-LOOP-DIGEST",
                "LEDGER-PER-YEAR is included under the owner's request for the complete accumulated evidence "
                "(OWNER-NS2-5); for this pack it settles the question the feasibility review left open (section 10, "
                "item 10): every probe_result's series is summarised the same way, with nothing selected; calendar "
                "years are a fixed grouping, not a regime definition, and the owner's rules 'Do not manufacture a "
                "regime definition after seeing results' (OWNER-NS2-4) and 'Any regime boundary must be defined from "
                "information available independently of the result' (OWNER-NS2-8) apply to any regime boundary drawn "
                "from these figures",
                "INFRA-T0 is kept verbatim. Its '90-day context' is the context of every recorded t0 forecast of a "
                "target series. The one shorter t0 context is Experiment 3's P1/P2 residual model, which used "
                f"{__import__('solarbench.probes', fromlist=['x']).RESID_CONTEXT_DAYS} days. It is stated in "
                "INFRA-DATA-HISTORY (t0_context_outside_the_engine)",
                "the first pack's source files are not re-hashed: its own sha256 is; the new records' sources are"],
            "evidence_grades": grades, "verification_labels": v1["verification_labels"], "excluded": EXCLUDED,
            "record_ids": ids, "records": records}
    blob = (json.dumps(pack, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str) + "\n").encode("utf-8")
    (HERE / "evidence_pack_v2.json").write_bytes(blob)
    (HERE / "evidence_pack_v2.md").write_text(render_md(pack), encoding="utf-8")
    print(f"{len(records)} records, {len(blob):,} bytes, sha256 {sha256(blob)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
