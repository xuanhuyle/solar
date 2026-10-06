"""The two researcher conditions of learn1 (NEXT_LEARNING_MILESTONE_PROMPT.md sections 5-7).

- F (fresh): beta1's researcher exactly (``beta1/lab/researcher.py``): the same system text (beta1's brief and the
  response schema), user and repair prompts, code checks with one repair turn, the 6-experiment budget with at most 3
  per round, the 80k token cap, the pinned model and effort, and an empty notebook at the start.
- L (learned): the same researcher with one difference: its system text carries the frozen portable lesson
  (``lesson.json``, distilled from the beta1 failure before this world existed) in one labelled section between the
  brief and the schema. It never receives beta1's notebook.

No code acts on the lesson: there is no rule, quota, reserved experiment or forced re-screen. Each condition is its
own researcher with its own record; neither sees the other's experiments or conclusions.
"""
from __future__ import annotations

import json
from pathlib import Path

from research_loop_proof.beta1.lab import researcher as beta1
from research_loop_proof.phase0.lab.researcher import IntegrityError, response_schema, sha256_text

HERE = Path(__file__).resolve().parent
LESSON_FILE = HERE / "lesson.json"
LESSON_HEADER = "PRIOR RESEARCH LESSON (distilled from an earlier, separate investigation)"
CONDITIONS = ("F", "L")


def frozen_lesson() -> str:
    """The frozen lesson exactly as the lesson call returned it (refused if missing or not matching its hash)."""
    if not LESSON_FILE.is_file():
        raise IntegrityError("no frozen lesson yet (learn1/lab/lesson.json)")
    rec = json.loads(LESSON_FILE.read_text(encoding="utf-8"))
    if sha256_text(rec["lesson"]) != rec["lesson_sha256"]:
        raise IntegrityError("the frozen lesson does not match its sha256")
    return rec["lesson"]


def lesson_section(lesson: str) -> str:
    return LESSON_HEADER + "\n" + lesson


def system_text(condition: str) -> str:
    if condition == "F":
        return beta1.system_text()
    if condition == "L":
        return (beta1.BRIEF.rstrip("\n") + "\n\n" + lesson_section(frozen_lesson())
                + "\n\nRESPONSE SCHEMA (JSON)\n" + json.dumps(response_schema(), indent=1) + "\n")
    raise ValueError(f"unknown condition {condition!r}")


class Researcher(beta1.Researcher):
    def __init__(self, client, model: str, lab, *, condition: str, **kwargs):
        super().__init__(client, model, lab, **kwargs)
        self.condition = condition
        self.system = system_text(condition)

    def run(self) -> dict:
        return {"condition": self.condition, **super().run()}


rebuild_mismatches = beta1.rebuild_mismatches  # user and repair prompts do not depend on the system text
call_plan = beta1.call_plan
