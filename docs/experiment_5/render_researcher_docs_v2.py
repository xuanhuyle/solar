"""Render the parts of the second-decision documents (mandate v2) that must match the recorded call exactly.

- ``brief_appendix_v2.md``: what the researcher received: the full system text (the owner's text, the standing
  rules and the answer format), the user-message template, the schema hash, and the evidence pack's index,
  exclusions and changes from the first pack. It is rendered from the code and the committed v2 pack.
- With ``--run-id``:
  - ``researcher_output_v2.json``: the researcher's answer exactly as recorded on the ledger (``response_text`` of
    the last v2 ``research_call`` of that run);
  - ``proposal_v2_rendered.md``: a mechanical rendering of it, also embedded between the ``researcher-output``
    markers of ``RESEARCHER_PROPOSAL_V2.md``. Nothing in the answer is edited.
- With ``--verify``: every provenance fact is checked against the ledger, the committed files and the code; any
  mismatch exits 1.

The first decision's script (``render_researcher_docs.py``) and its outputs are not touched.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/render_researcher_docs_v2.py [--run-id <the v2 propose run's id> [--verify]]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from engine import propose, propose_v2  # noqa: E402
from render_researcher_docs import _render_value, embed  # noqa: E402

PACK = HERE / "evidence_pack_v2.json"
OUTPUT = HERE / "researcher_output_v2.json"
DOC = HERE / "RESEARCHER_PROPOSAL_V2.md"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def brief_appendix_v2() -> str:
    pack_bytes = PACK.read_bytes()
    pack = json.loads(pack_bytes)
    pack_sha = hashlib.sha256(pack_bytes).hexdigest()
    system = propose_v2.system_text_v2()
    lines = ["# Appendix: exactly what the researcher received in the second decision (mandate v2)", "",
             "Rendered by `render_researcher_docs_v2.py` from the code and the committed v2 pack.", "",
             "## A. System text (`engine/propose_v2.py`, `system_text_v2()`)", "",
             f"sha256 `{sha(system)}` (the `system_sha256` of the research call, which also records the full text); "
             f"rules alone sha256 `{sha(propose_v2.proposal_rules_v2())}`; {len(system):,} characters. The owner's "
             "sections in it are read verbatim from `NORTH_STAR_CLARIFICATION.md`.", "",
             "````text", system, "````", "",
             "## B. User message", "", "Built by `propose.user_prompt` (the same function as the first decision):", "",
             "````text", propose.user_prompt("<the evidence pack: docs/experiment_5/evidence_pack_v2.json, verbatim>",
                                             pack_sha), "````", "",
             f"Evidence pack: `docs/experiment_5/evidence_pack_v2.json`, sha256 `{pack_sha}`, {len(pack_bytes):,} bytes, "
             f"{len(pack['records'])} records. A readable rendering is `docs/experiment_5/evidence_pack_v2.md`.", "",
             "## C. Answer schema (`propose_v2.proposal_schema_v2()`)", "",
             f"sha256 of the canonical schema `{propose_v2.schema_sha256_v2()}`. It is part of the system text above and "
             "the code checks the answer against it (`propose_v2.validate_proposal_v2`).", "",
             "## D. Mandate hashes", "",
             f"- v2 `MANDATE_V2`: `{sha(propose_v2.MANDATE_V2)}`",
             *[f"- {k}: `{v}`" for k, v in propose_v2.previous_hashes().items()], "",
             "## E. Changed from the first pack (verbatim from the pack)", ""]
    lines += [f"- {x}" for x in pack["changes_from_first_pack"]]
    lines += ["", "## F. Deliberately excluded (verbatim from the pack)", ""]
    lines += [f"- {x['what']}. *Why:* {x['why']}." for x in pack["excluded"]]
    lines += ["", "## G. Evidence pack record index", "", "| id | experiment | grade | verification | title |",
              "|---|---|---|---|---|"]
    for r in pack["records"]:
        lines.append(f"| {r['id']} | {r['experiment']} | {r['evidence_grade']} | {r['verification']} | "
                     f"{r['title'].replace('|', '/')} |")
    led = pack["built_from"]["ledger"]
    lines += ["", "## H. Sources the pack was built from (sha256 at build time)", "", "| file | sha256 |", "|---|---|"]
    lines += [f"| `{k}` | `{v}` |" for k, v in pack["built_from"]["repo_files_sha256"].items()]
    lines += ["", f"Engine ledger: branch `engine-ledger` at `{led['git']}`, head seq {led['head_seq']} (entry sha256 "
                  f"`{led['head_sha256']}`). First pack: `{pack['built_from']['first_pack']['path']}`, sha256 "
                  f"`{pack['built_from']['first_pack']['sha256']}`.", ""]
    return "\n".join(lines) + "\n"


TITLES = {"action": "Action", "summary": "Summary", "A_learned": "A. What I believe I have learned",
          "B_unexplained": "B. What remains unexplained", "C_candidates": "C. Candidate investigations",
          "D_decision": "D. Decision (including what happens to I1)", "E_protocol": "E. Proposed protocol",
          "G_accumulated_knowledge": "G. Accumulated knowledge"}


def render_proposal_v2(answer: dict) -> str:
    """A mechanical rendering: every field of the answer, in the schema's order, without edits."""
    lines = []
    for key, title in TITLES.items():
        lines += [f"### {title}", ""]
        v = answer.get(key)
        if v is None:
            lines.append("null")
        elif isinstance(v, str):
            lines.append(v)
        elif key == "C_candidates":
            if not v:
                lines.append("(none)")
            for c in v:
                lines += [f"#### Candidate {c.get('id')}", ""] + _render_value({k: x for k, x in c.items() if k != "id"})
                lines.append("")
        else:
            lines += _render_value(v)
        lines.append("")
    return "\n".join(lines) + "\n"


def ledger_entries() -> list[dict]:
    raw = subprocess.run(["git", "-C", str(ROOT), "show", "origin/engine-ledger:ledger.jsonl"], check=True,
                         capture_output=True, text=True).stdout
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def final_call(entries: list[dict], run_id: str) -> dict:
    calls = [e for e in entries if e["kind"] == "research_call" and str(e.get("run_id")) == str(run_id)
             and (e.get("payload") or {}).get("mandate_version") == "v2"]
    if not calls:
        raise SystemExit(f"no v2 research_call for run {run_id} on the ledger")
    return calls[-1]


def verify_call(e: dict, committed_answer: str | None) -> list[str]:
    """Compare the recorded call with the committed answer, pack and code; return the failed checks."""
    p = e["payload"]
    pack_bytes = PACK.read_bytes()
    pack_sha = hashlib.sha256(pack_bytes).hexdigest()
    pack = json.loads(pack_bytes)
    ids = {r["id"] for r in pack["records"]}
    system = propose_v2.system_text_v2()
    checks = {
        "committed researcher_output_v2.json equals the ledger's response_text": committed_answer == p["response_text"],
        "evidence_pack_sha256 equals the committed v2 pack": p.get("evidence_pack_sha256") == pack_sha,
        "the recorded system_text equals propose_v2.system_text_v2()": p.get("system_text") == system,
        "system_sha256 equals the sha of that text": p.get("system_sha256") == sha(system),
        "proposal_rules_sha256 equals proposal_rules_v2()": p.get("proposal_rules_sha256") == sha(
            propose_v2.proposal_rules_v2()),
        "schema_sha256 equals schema_sha256_v2()": p.get("schema_sha256") == propose_v2.schema_sha256_v2(),
        "mandate_sha256 equals MANDATE_V2": p.get("mandate_sha256") == sha(propose_v2.MANDATE_V2),
        "the previous-decision hashes equal the first decision's code and ledger seq 74": all(
            p.get(k) == v for k, v in propose_v2.previous_hashes().items()),
        "user_prompt equals propose.user_prompt(pack)":
            p.get("user_prompt") == propose.user_prompt(pack_bytes.decode("utf-8"), pack_sha),
        "the served model equals the requested model": p.get("served_model") == p.get("requested_model"),
    }
    if p.get("action"):
        answer = json.loads(p["response_text"])
        cited = set(propose.cited_ids(answer))
        checks[f"all {len(cited)} cited ids exist in the pack"] = cited <= ids
        checks["validate_proposal_v2 finds no error"] = not propose_v2.validate_proposal_v2(answer, ids)
    for name, ok in checks.items():
        print(("ok    " if ok else "FAIL  ") + name)
    return [name for name, ok in checks.items() if not ok]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    (HERE / "brief_appendix_v2.md").write_text(brief_appendix_v2(), encoding="utf-8")
    print("wrote brief_appendix_v2.md")
    if args.run_id:
        entries = ledger_entries()
        e = final_call(entries, args.run_id)
        committed = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None  # read before it is rewritten
        text = e["payload"].get("response_text") or ""
        OUTPUT.write_text(text, encoding="utf-8")
        print(f"ledger seq {e['seq']}: response_text sha256 {sha(text)}; action {e['payload'].get('action')}")
        if text.strip() and e["payload"].get("action"):
            rendered = render_proposal_v2(json.loads(text))
            (HERE / "proposal_v2_rendered.md").write_text(rendered, encoding="utf-8")
            if DOC.exists():
                DOC.write_text(embed(DOC.read_text(encoding="utf-8"), rendered), encoding="utf-8")
                print("embedded the rendering in RESEARCHER_PROPOSAL_V2.md")
        if args.verify and verify_call(e, committed):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
