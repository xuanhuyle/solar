"""Static checks of .github/workflows/engine.yml: the job graph and trust boundaries the engine relies on.

No runner is available offline, so these pin the properties a fix-check found broken or easy to break:
the chain job's status function, where pending entries may come from, and which code scores a batch.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "engine.yml"
STATUS_FUNCTIONS = ("always()", "!cancelled()", "success()", "failure()", "cancelled()")


@pytest.fixture(scope="module")
def jobs():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


def _run_text(job) -> str:
    return "\n".join(str(s.get("run", "")) for s in job["steps"])


def test_every_dependent_job_has_an_explicit_status_function(jobs):
    """Without one GitHub adds success(), false whenever any upstream job was skipped (vault, in loop mode)."""
    for name, job in jobs.items():
        if job.get("needs") and "if" in job:
            assert any(f in str(job["if"]) for f in STATUS_FUNCTIONS), name


def test_the_chain_needs_a_successful_referee_and_record(jobs):
    chain = jobs["chain"]
    assert set(chain["needs"]) >= {"research", "referee", "record"}
    cond = str(chain["if"])
    for part in ("!cancelled()", "needs.referee.result == 'success'", "needs.record.result == 'success'",
                 "needs.research.outputs.action == 'probe'", "fromJSON(inputs.iteration) < fromJSON(inputs.max_iterations)"):
        assert part in cond, part
    assert chain["permissions"] == {"actions": "write"}


def test_pending_entries_are_read_only_as_declared_by_their_producer(jobs):
    for name in ("referee", "vault"):
        job = jobs[name]
        assert job["outputs"]["pending_sha256"] == "${{ steps.declare.outputs.sha256 }}", name
        declare = next(s for s in job["steps"] if s.get("id") == "declare")
        assert declare["if"] == "always()" and "sha256sum" in declare["run"], name
    rec = jobs["record"]
    step = next(s for s in rec["steps"] if s.get("name") == "Chain them onto engine-ledger")
    assert "--pending-sha256" in step["run"] and "needs.referee.outputs.pending_sha256" in step["env"]["PENDING_SHA256"]
    assert "--referee-result" in step["run"] and "--vault-result" in step["run"]


def test_research_records_are_kept_per_attempt(jobs):
    assert "github.run_attempt" in jobs["research"]["outputs"]["artifact"]
    upload = next(s for s in jobs["research"]["steps"] if "upload-artifact" in str(s.get("uses", "")))
    assert "github.run_attempt" in upload["with"]["name"]
    dl = next(s for s in jobs["referee"]["steps"] if "download-artifact" in str(s.get("uses", "")))
    assert dl["with"]["name"] == "${{ needs.research.outputs.artifact }}"
    rec = next(s for s in jobs["record"]["steps"] if "researcher" in str(s.get("name", "")))
    assert rec["with"]["pattern"].endswith("-*")


def test_the_vault_scores_with_the_code_the_batch_was_frozen_with(jobs):
    vault = jobs["vault"]
    assert vault["environment"] == "engine-vault" and vault["if"] == "inputs.mode == 'vault'"
    assert "--freeze-commit" in _run_text(vault) and "git worktree add --detach frozen" in _run_text(vault)
    open_step = next(s for s in vault["steps"] if s.get("name") == "Open the batch once")
    assert open_step["working-directory"] == "frozen"
    assert open_step["env"]["ENGINE_CODE_COMMIT"] == "${{ steps.frozen.outputs.commit }}"
    for name in ("Install dependencies (the frozen commit's)", "Run tests (the frozen commit's)"):
        assert next(s for s in vault["steps"] if s.get("name") == name)["working-directory"] == "frozen"
    upload = next(s for s in vault["steps"] if "upload-artifact" in str(s.get("uses", "")))
    assert upload["with"]["path"] == "frozen/results/engine/pending.jsonl"
    assert not any("actions/cache@" in str(s.get("uses", "")) for s in vault["steps"])  # restore only, never save


def test_only_the_record_job_may_write_and_only_the_chain_may_dispatch(jobs):
    for name, job in jobs.items():
        perms = job.get("permissions", {})
        assert (perms.get("contents") == "write") == (name == "record"), name
        assert (perms.get("actions") == "write") == (name == "chain"), name


def test_no_job_reads_any_cache(jobs):
    """Re-checks (major): any job holding the runtime token could plant a cache - discovery data, a t0
    snapshot the loader trusts without a hash check, pip's HTTP cache - that the referee or vault would read."""
    for name, job in jobs.items():
        for step in job["steps"]:
            assert "actions/cache" not in str(step.get("uses", "")), (name, step.get("name"))
            assert "cache" not in (step.get("with") or {}), (name, step.get("name"))  # setup-python cache: pip
    assert "enginecache" not in WORKFLOW.read_text(encoding="utf-8")


def test_the_record_job_requires_the_research_record_and_pins_every_freeze(jobs):
    step = next(s for s in jobs["record"]["steps"] if s.get("name") == "Chain them onto engine-ledger")
    assert step["env"]["RESEARCH_RESULT"] == "${{ needs.research.result }}" and "--research-result" in step["run"]
    run = step["run"]
    assert "--freezes" in run and "refs/tags/engine-freeze/" in run
    assert run.index("push origin HEAD:refs/heads/engine-ledger") < run.index("refs/tags/engine-freeze/")
    assert "exit 0; fi\ngit -C ledgerwt add" in run and run.count("exit 0") == 1  # only a missing ledger skips pinning



def test_the_record_step_names_this_attempts_research_record(jobs):
    step = next(s for s in jobs["record"]["steps"] if s.get("name") == "Chain them onto engine-ledger")
    assert step["env"]["RESEARCH_ARTIFACT"] == "${{ needs.research.outputs.artifact }}"
    assert '--research-own "research/${RESEARCH_ARTIFACT:-none}/pending_research.jsonl"' in step["run"]
