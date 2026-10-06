"""Render the parts of the Experiment 5 researcher documents that must match the recorded call exactly.

- ``brief_appendix.md``: the system text (``PROPOSAL_RULES``), the output schema and the evidence pack's record
  index, rendered from the code and the committed pack (the hashes are printed so they can be checked against the
  ``research_call`` entries on the engine ledger).
- ``researcher_output.json`` and ``proposal_rendered.md``: the researcher's answer exactly as recorded on the
  ledger (``response_text`` of the final ``research_call`` of the propose run), and a mechanical rendering of it.
  Nothing in the answer is edited. The same rendering is written between the ``researcher-output`` markers of
  ``RESEARCHER_PROPOSAL.md``, so re-running this script and ``git diff --exit-code docs/experiment_5`` proves that
  the committed documents still match the ledger.

Usage::

    git fetch origin engine-ledger:refs/remotes/origin/engine-ledger
    python docs/experiment_5/render_researcher_docs.py [--run-id <the propose run's id> [--verify]]
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

from engine import propose  # noqa: E402


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def brief_appendix() -> str:
    pack_bytes = (HERE / "evidence_pack.json").read_bytes()
    pack = json.loads(pack_bytes)
    lines = ["# Appendix: exactly what the researcher received", "",
             "Rendered by `render_researcher_docs.py` from the code and the committed pack.", "",
             "## A. System text (`engine/propose.py`, `system_text()`: `PROPOSAL_RULES` plus the answer format)", "",
             f"sha256 `{sha(propose.system_text())}` (this is the `system_sha256` of the research_call); "
             f"`PROPOSAL_RULES` alone sha256 `{sha(propose.PROPOSAL_RULES)}`; {len(propose.system_text()):,} characters.", "",
             "````text", propose.system_text(), "````", "",
             "## B. User message", "",
             "Built by `propose.user_prompt`:", "", "````text",
             propose.user_prompt("<the evidence pack: docs/experiment_5/evidence_pack.json, verbatim>",
                                 hashlib.sha256(pack_bytes).hexdigest()),
             "````", "",
             f"Evidence pack: `docs/experiment_5/evidence_pack.json`, sha256 `{hashlib.sha256(pack_bytes).hexdigest()}`, "
             f"{len(pack_bytes):,} bytes, {len(pack['records'])} records. A readable rendering is "
             "`docs/experiment_5/evidence_pack.md`.", "",
             "## C. Answer schema (`propose.proposal_schema()`)", "",
             f"sha256 of the canonical schema `{propose.schema_sha256()}`. It is part of the system text above and the "
             "code checks the answer against it (`propose.schema_errors`, `propose.validate_proposal`); it is not sent "
             "as a grammar-constrained output format.", "",
             "## D. Evidence pack record index", "",
             "| id | experiment | grade | verification | title |", "|---|---|---|---|---|"]
    for r in pack["records"]:
        title = r["title"].replace("|", "/")
        lines.append(f"| {r['id']} | {r['experiment']} | {r['evidence_grade']} | {r['verification']} | {title} |")
    lines += ["", "## E. Deliberately excluded (verbatim from the pack)", ""]
    lines += [f"- {x['what']}. *Why:* {x['why']}." for x in pack["excluded"]]
    lines += ["", "## F. Sources the pack was built from (sha256 at build time)", "",
              "| file | sha256 |", "|---|---|"]
    lines += [f"| `{k}` | `{v}` |" for k, v in pack["built_from"]["repo_files_sha256"].items()]
    led = pack["built_from"]["ledger"]
    lines += ["", f"Engine ledger: branch `engine-ledger` at `{led['git']}`, head seq {led['head_seq']} "
                  f"(entry sha256 `{led['head_sha256']}`).", ""]
    return "\n".join(lines) + "\n"


def _render_value(v, indent=0) -> list[str]:
    pad = "  " * indent
    if isinstance(v, dict):
        out = []
        for k, x in v.items():
            if isinstance(x, (dict, list)):
                out.append(f"{pad}- **{k}:**")
                out += _render_value(x, indent + 1)
            else:
                out.append(f"{pad}- **{k}:** {x}")
        return out
    if isinstance(v, list):
        out = []
        for x in v:
            if isinstance(x, (dict, list)):
                sub = _render_value(x, indent + 1)
                out.append(f"{pad}- " + sub[0].strip().lstrip("- ") if sub else f"{pad}-")
                out += sub[1:]
            else:
                out.append(f"{pad}- {x}")
        return out
    return [f"{pad}{v}"]


def render_proposal(answer: dict) -> str:
    """A mechanical rendering: every field of the answer, in the schema's order, without edits."""
    lines = []
    titles = {"action": "Action", "summary": "Summary", "A_learned": "A. What I believe I have learned",
              "B_unexplained": "B. What remains unexplained", "C_candidates": "C. Candidate investigations",
              "D_decision": "D. Chosen next investigation", "E_protocol": "E. Proposed scientific protocol",
              "F_knowledge_update": "F. Knowledge update"}
    for key, title in titles.items():
        lines += [f"### {title}", ""]
        v = answer.get(key)
        if v is None:
            lines.append("null")
        elif isinstance(v, str):
            lines.append(v)
        elif key == "C_candidates":
            for c in v:
                lines += [f"#### Candidate {c.get('id')}", ""] + _render_value({k: x for k, x in c.items() if k != "id"})
                lines.append("")
        else:
            lines += _render_value(v)
        lines.append("")
    return "\n".join(lines) + "\n"


BEGIN = "<!-- researcher-output:begin (written by render_researcher_docs.py; do not edit) -->"
END = "<!-- researcher-output:end -->"


def embed(doc: str, rendered: str) -> str:
    """Replace the text between the markers of ``doc`` with ``rendered``; refuse if the markers are not there once."""
    if doc.count(BEGIN) != 1 or doc.count(END) != 1 or doc.index(BEGIN) > doc.index(END):
        raise SystemExit("RESEARCHER_PROPOSAL.md must hold each researcher-output marker exactly once, in order")
    head, rest = doc.split(BEGIN)
    _, tail = rest.split(END)
    return head + BEGIN + "\n\n" + rendered + "\n" + END + tail


def final_call(run_id: str) -> dict:
    raw = subprocess.run(["git", "-C", str(ROOT), "show", "origin/engine-ledger:ledger.jsonl"], check=True,
                         capture_output=True, text=True).stdout
    calls = [json.loads(line) for line in raw.splitlines() if line.strip()]
    calls = [e for e in calls if e["kind"] == "research_call" and str(e.get("run_id")) == str(run_id)
             and e.get("mode") == "propose"]
    if not calls:
        raise SystemExit(f"no propose research_call for run {run_id} on the ledger")
    return calls[-1]


def verify_call(e: dict, committed_answer: str | None) -> list[str]:
    """Compare the recorded call with the committed answer, pack and code; return the failed checks."""
    p = e["payload"]
    pack_bytes = (HERE / "evidence_pack.json").read_bytes()
    pack_sha = hashlib.sha256(pack_bytes).hexdigest()
    pack = json.loads(pack_bytes)
    ids = {r["id"] for r in pack["records"]}
    answer = json.loads(p["response_text"])
    cited = set(propose.cited_ids(answer))
    checks = {
        "committed researcher_output.json equals the ledger's response_text": committed_answer == p["response_text"],
        "evidence_pack_sha256 equals the committed pack": p.get("evidence_pack_sha256") == pack_sha,
        "system_sha256 equals propose.system_text()": p.get("system_sha256") == sha(propose.system_text()),
        "proposal_rules_sha256 equals PROPOSAL_RULES": p.get("proposal_rules_sha256") == sha(propose.PROPOSAL_RULES),
        "schema_sha256 equals propose.schema_sha256()": p.get("schema_sha256") == propose.schema_sha256(),
        "user_prompt equals propose.user_prompt(pack)":
            p.get("user_prompt") == propose.user_prompt(pack_bytes.decode("utf-8"), pack_sha),
        f"all {len(cited)} cited ids exist in the pack": bool(cited) and cited <= ids,
        "validate_proposal finds no error": not propose.validate_proposal(answer, ids),
    }
    for name, ok in checks.items():
        print(("ok    " if ok else "FAIL  ") + name)
    return [name for name, ok in checks.items() if not ok]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--verify", action="store_true", help="with --run-id: check the recorded call against the "
                    "committed pack and the code; exit 1 on any mismatch")
    args = ap.parse_args()
    (HERE / "brief_appendix.md").write_text(brief_appendix(), encoding="utf-8")
    print("wrote brief_appendix.md")
    if args.run_id:
        e = final_call(args.run_id)
        out = HERE / "researcher_output.json"
        committed = out.read_text(encoding="utf-8") if out.exists() else None  # read before it is rewritten
        text = e["payload"].get("response_text") or ""
        (HERE / "researcher_output.json").write_text(text, encoding="utf-8")
        answer = json.loads(text)
        rendered = render_proposal(answer)
        (HERE / "proposal_rendered.md").write_text(rendered, encoding="utf-8")
        doc = HERE / "RESEARCHER_PROPOSAL.md"
        if doc.exists():
            doc.write_text(embed(doc.read_text(encoding="utf-8"), rendered), encoding="utf-8")
            print("embedded the rendering in RESEARCHER_PROPOSAL.md")
        print(f"ledger seq {e['seq']}: response_text sha256 {sha(text)}; action {answer.get('action')}")
        if args.verify and verify_call(e, committed):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
