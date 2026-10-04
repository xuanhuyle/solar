"""learn1 (docs/research_loop_proof/NEXT_LEARNING_MILESTONE_PROMPT.md): the lesson call, the two researcher conditions,
the paired evaluation and the workflow. Parts that need torch or anthropic skip without them."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research_loop_proof.beta1.lab import researcher as bres
from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth import observe as bobs
from research_loop_proof.learn1 import lesson as les
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.learn1.truth import evaluate as lev
from research_loop_proof.learn1.truth import observe as lobs
from research_loop_proof.learn1.truth import preflight as lpre
from research_loop_proof.learn1.truth import spec as lspec
from research_loop_proof.phase0.lab import executor
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "learn1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-learn1.yml"
BETA1_REF = "origin/beta1/run-37201189113"
TEST_MODEL = "test-model-id"
TEST_LESSON = ("A negative result describes the regime in which it was gathered. When an established relationship "
               "weakens, treat earlier rejections as possibly stale and spend part of the remaining budget re-testing "
               "them on recent data.")


def _git_show(ref_path: str) -> bytes | None:
    r = subprocess.run(["git", "show", ref_path], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


# ----------------------------------------------------------------- fakes (as in the beta1 tests)

class _Inst:
    rows = sanitised = 0

    def forecast(self, requests):
        self.rows += len(requests)
        return [ctx[-24:] + (0 if b is None else 0.3 * b[:, -24:].sum(0)) for ctx, b in requests]


def _resp(obj, *, model=TEST_MODEL, stop="end_turn", details=None, tokens=1000):
    text = obj if isinstance(obj, str) else json.dumps(obj)
    usage = SimpleNamespace(input_tokens=tokens, output_tokens=tokens // 2, cache_read_input_tokens=0,
                            cache_creation_input_tokens=0)
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], model=model, stop_reason=stop,
                           usage=usage, _request_id="req-test", stop_details=details)


class _Client:
    def __init__(self, replies):
        self.replies, self.sent = list(replies), []
        self.messages = self

    def create(self, **kw):
        self.sent.append(kw)
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def _beliefs(status="untested", cites=None, overrides=None):
    rows = {i: {"candidate": i, "status": status, "cites": list(cites or []), "reason": "r"} for i in executor.IDS}
    for i, row in (overrides or {}).items():
        rows[i].update(row)
    return [rows[i] for i in executor.IDS]


def _exp(cov, ref=(), win=28, because="b"):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves",
            "because": because}


def _reply(beliefs, experiments=(), final=None, conclusion="", notes="n"):
    return {"notes": notes, "beliefs": beliefs, "experiments": list(experiments), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies():
    return [_resp(_reply(_beliefs(), [_exp(["X01"]), _exp(["X02"])])),
            _resp(_reply(_beliefs("promising", ["E1"]), [_exp(["X03"], win=14), _exp(["X04"], win=14)])),
            _resp(_reply(_beliefs("promising", ["E3"]), [_exp(["X01"], win=14), _exp(["X02"], ["X01"], win=14)])),
            _resp(_reply(_beliefs("accepted", ["E5"], {"X02": {"status": "rejected", "cites": ["E6"]}}),
                         final=["X01"], conclusion="X01 helps."))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def lesson(monkeypatch, tmp_path):
    """The frozen lesson once it exists; before the freeze, a stand-in lesson file."""
    if lres.LESSON_FILE.is_file():
        return lres.frozen_lesson()
    f = tmp_path / "lesson.json"
    f.write_text(json.dumps({"lesson": TEST_LESSON, "lesson_sha256": p0res.sha256_text(TEST_LESSON)}))
    monkeypatch.setattr(lres, "LESSON_FILE", f)
    monkeypatch.setattr(lev, "LESSON_FILE", f)
    monkeypatch.setattr(lspec, "missing", lambda root=None: [])
    return TEST_LESSON


# ----------------------------------------------------------------- separation

def test_the_learn1_lab_and_lesson_call_never_import_a_truth_package():
    for path in [*(PKG / "lab").glob("*.py"), PKG / "lesson.py"]:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


# ----------------------------------------------------------------- the lesson call

def _beta1_like_record():
    w = bobs.preflight_world("4242")
    return bres.Researcher(_Client(_replies()), TEST_MODEL, executor.Lab(gen.observed_arrays(w, 126), _Inst())).run()


def test_the_lesson_prompt_is_the_notebook_and_the_feedback_only(pinned):
    ai = _beta1_like_record()
    user = les.user_prompt(ai)
    assert les.notebook(ai) in user and les.FEEDBACK in user
    assert user.count("=== Call ") == 4 and "Conclusion: X01 helps." in user
    assert user == les.user_prompt(json.loads(json.dumps(ai)))  # a pure function of the record
    for word in ("learn1", "spec_sha", "seed", "PRIOR RESEARCH LESSON"):
        assert word not in user
    for rule in ("at most 1,000 characters", "general empirical-research principle", "candidate identifiers",
                 "numerals", "fixed sequence of experiments", "unhelpful under one regime"):
        assert rule in les.SYSTEM
    assert les.FEEDBACK == ("The process changed. A candidate rejected on pre-change evidence became strongly predictive "
                            "after the change. The researcher detected deterioration in the previously useful "
                            "relationship but did not re-test candidates rejected under the earlier regime, so it "
                            "missed the emerging signal.")


def test_the_real_beta1_record_is_pinned_and_feeds_the_prompt(tmp_path):
    body, manifest = _git_show(f"{BETA1_REF}:ai.json"), _git_show(f"{BETA1_REF}:MANIFEST.sha256")
    if body is None or manifest is None:
        pytest.skip("the beta1 result branch is not fetched here")
    (tmp_path / "ai.json").write_bytes(body)
    (tmp_path / "MANIFEST.sha256").write_bytes(manifest)
    ai = les.beta1_record(tmp_path)
    user = les.user_prompt(ai)
    assert ai["calls"][-1]["response"]["conclusion"] in user and les.FEEDBACK in user
    assert ai["system_sha256"] == p0res.sha256_text(lres.system_text("F"))  # F is beta1's system text exactly
    (tmp_path / "ai.json").write_bytes(body + b" ")
    with pytest.raises(p0res.IntegrityError):
        les.beta1_record(tmp_path)


def test_the_lesson_is_checked_in_code():
    assert les.lesson_errors({"lesson": TEST_LESSON}) == []
    assert les.lesson_errors({"lesson": "Re-test X01 after day 84."})  # an id and numerals
    assert les.lesson_errors({"lesson": "seven days"}) == [] and les.lesson_errors({"lesson": "7 days"})
    assert les.lesson_errors({"lesson": "a" * 1001}) and les.lesson_errors({"lesson": "a" * 1000}) == []
    assert les.lesson_errors({"lesson": "  "}) and les.lesson_errors({"lesson": "x", "extra": 1})
    assert les.lesson_errors(["lesson"])


def test_one_repair_then_the_lesson_or_a_distillation_failure(pinned):
    client = _Client([_resp({"lesson": "Re-test X01 after day 84."}), _resp({"lesson": TEST_LESSON})])
    rec = les.Distiller(client, TEST_MODEL, sleep=lambda s: None).run("U")
    assert rec["status"] == "OK" and rec["lesson"] == TEST_LESSON
    assert rec["lesson_sha256"] == hashlib.sha256(TEST_LESSON.encode()).hexdigest()
    a1, a2 = rec["attempts"]
    assert a1["errors"] and a2["repair"] == 1 and a2["messages"][0]["role"] == "assistant"
    assert "candidate identifiers" in a2["messages"][1]["content"]
    assert client.sent[0]["system"][0]["text"] == les.SYSTEM and client.sent[0]["messages"] == [
        {"role": "user", "content": "U"}]
    assert client.sent[0]["output_config"]["format"]["schema"] == les.SCHEMA
    assert TEST_MODEL not in json.dumps(rec)
    refusal = SimpleNamespace(type="refusal", category="general_harms", explanation="e")
    rec = les.Distiller(_Client([_resp("", stop="refusal", details=refusal)] * 2), TEST_MODEL).run("U")
    assert rec["status"] == les.FAILURE and rec["lesson"] is None and len(rec["attempts"]) == 2
    assert rec["attempts"][0]["refusal_category"] == "general_harms"

    class _Down(Exception):
        status_code = 400
    rec = les.Distiller(_Client([_Down("bad request"), _resp({"lesson": TEST_LESSON})]), TEST_MODEL).run("U")
    assert rec["status"] == "OK" and rec["attempts"][0]["api_errors"] and rec["attempts"][1]["messages"] == []


def test_the_lesson_job_refuses_an_unpinned_beta1_record(tmp_path, monkeypatch, pinned):
    d = tmp_path / "b1"
    d.mkdir()
    body = json.dumps({"calls": []}).encode()
    (d / "ai.json").write_bytes(body)
    (d / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  ai.json\n")
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    assert les.main(["--beta1", str(d), "--out", str(tmp_path / "out")]) == 0
    v = json.loads((tmp_path / "out" / "verdict.json").read_text())
    assert v["verdict"] == les.FAILURE and not (tmp_path / "out" / "lesson.json").exists()
    rec = json.loads((tmp_path / "out" / "lesson_record.json").read_text())
    assert "pinned" in rec["failure"]["error"]


# ----------------------------------------------------------------- the two conditions

def test_the_two_conditions_differ_only_by_the_lesson(lesson):
    f, l = lres.system_text("F"), lres.system_text("L")
    assert f == bres.system_text()
    section = lres.lesson_section(lesson)
    assert section == "PRIOR RESEARCH LESSON (distilled from an earlier, separate investigation)\n" + lesson
    assert l.count(section) == 1 and l.replace("\n\n" + section, "", 1) == f
    assert lesson not in f and "PRIOR RESEARCH LESSON" not in f
    assert lres.rebuild_mismatches is bres.rebuild_mismatches is p0res.rebuild_mismatches
    with pytest.raises(ValueError):
        lres.system_text("X")


def test_the_lesson_must_be_frozen_and_match_its_hash(tmp_path, monkeypatch):
    monkeypatch.setattr(lres, "LESSON_FILE", tmp_path / "none.json")
    with pytest.raises(p0res.IntegrityError):
        lres.system_text("L")
    assert lres.system_text("F") == bres.system_text()  # the control never needs the lesson
    f = tmp_path / "lesson.json"
    f.write_text(json.dumps({"lesson": "edited", "lesson_sha256": p0res.sha256_text("original")}))
    monkeypatch.setattr(lres, "LESSON_FILE", f)
    with pytest.raises(p0res.IntegrityError):
        lres.frozen_lesson()


def test_both_conditions_run_the_same_researcher(pinned, lesson):
    w = bobs.preflight_world("4242")
    recs = {}
    for c in lres.CONDITIONS:
        client = _Client(_replies())
        recs[c] = lres.Researcher(client, TEST_MODEL, executor.Lab(gen.observed_arrays(w, 126), _Inst()),
                                  condition=c).run()
        assert recs[c]["condition"] == c and all(s["system"][0]["text"] == lres.system_text(c) for s in client.sent)
        assert recs[c]["system_text"] == lres.system_text(c) and lres.rebuild_mismatches(recs[c]["calls"]) == []
    assert [c["user_prompt"] for c in recs["F"]["calls"]] == [c["user_prompt"] for c in recs["L"]["calls"]]
    assert recs["F"]["calls"][0]["user_prompt"].count("(empty: this is the first call)") == 1


# ----------------------------------------------------------------- indicators and the paired outcome

def _roles():
    w = lobs.preflight_world("31")
    return {k: w.ids[k] for k in ("R", "E", "D", "N")}, w.tau


def _res(i, cov, lo, scored, ref=()):
    return {"id": f"E{i}", "request": _exp(cov, ref, because=f"because {i}"),
            "result": {"id": f"E{i}", "covariates": list(cov), "reference": list(ref), "skill": lo + 0.05, "lo95": lo,
                       "hi95": lo + 0.1, "scored_days": list(scored)}}


def _call(n, rnd, cutoff, beliefs, exps=(), final=None, notes="n"):
    return {"call": n, "round": rnd, "cutoff": cutoff, "final": rnd is None, "valid": True, "attempts": [],
            "errors": [], "response": _reply(beliefs, [e["request"] for e in exps], final, "c" if rnd is None else "",
                                             notes), "experiments": list(exps)}


def _fresh_failure(roles):
    """beta1's pattern: R found, then deteriorating; E and D rejected before the change and never re-tested."""
    r, e, d, n = roles["R"], roles["E"], roles["D"], roles["N"]
    rej = {"status": "rejected", "cites": ["E1"]}
    return [
        _call(1, 1, 84, _beliefs(), [_res(1, [e], -0.05, (57, 84)), _res(2, [d], -0.04, (57, 84)),
                                     _res(3, [r], 0.1, (57, 84))]),
        _call(2, 2, 112, _beliefs(overrides={e: rej, d: rej, r: {"status": "promising", "cites": ["E3"]}}),
              [_res(4, [n], -0.03, (85, 112)), _res(5, [r], 0.0, (85, 112))]),
        _call(3, 3, 126, _beliefs(overrides={e: rej, d: rej, n: rej, r: {"status": "deteriorated", "cites": ["E5"]}}),
              [_res(6, [r], -0.02, (113, 126))]),
        _call(4, None, 126, _beliefs(overrides={e: rej, d: rej, n: rej, r: {"status": "rejected", "cites": ["E6"]}}),
              final=[]),
    ]


def _learned_success(roles, notes="Per the prior research lesson, earlier rejections may be stale."):
    r, e, d, n = roles["R"], roles["E"], roles["D"], roles["N"]
    rej = {"status": "rejected", "cites": ["E1"]}
    return [
        _call(1, 1, 84, _beliefs(), [_res(1, [e], -0.05, (57, 84)), _res(2, [d], -0.04, (57, 84)),
                                     _res(3, [r], 0.1, (57, 84))]),
        _call(2, 2, 112, _beliefs(overrides={e: rej, d: rej, r: {"status": "promising", "cites": ["E3"]}}),
              [_res(4, [r], 0.0, (85, 112)), _res(5, [e], 0.2, (99, 112))], notes=notes),
        _call(3, 3, 126, _beliefs(overrides={e: {"status": "promising", "cites": ["E5"]}, d: rej,
                                             r: {"status": "deteriorated", "cites": ["E4"]}}),
              [_res(6, [d], 0.01, (113, 126), ref=[e])]),
        _call(4, None, 126, _beliefs(overrides={e: {"status": "accepted", "cites": ["E5"]},
                                                d: {"status": "redundant", "cites": ["E6"]},
                                                r: {"status": "rejected", "cites": ["E4"]}}), final=[e]),
    ]


def _analysed(calls, roles, tau, condition, confirm_lo=0.2):
    ai = {"calls": calls, "final_valid": True, "final_selection": calls[-1]["response"]["final_selection"]}
    ev = {"E_days_99_126": {"lo95": 0.2}, "R_days_57_84": {"lo95": 0.1}, "E_days_99_112": {"lo95": 0.1}}
    sel = {"t0": {"lo95": confirm_lo}} if ai["final_selection"] else None
    return lev.analyse(condition, ai, roles, tau, ev, [], sel)


def test_the_indicators_read_the_behaviour():
    roles, tau = _roles()
    f, l = _fresh_failure(roles), _learned_success(roles)
    a_f, a_l = _analysed(f, roles, tau, "F"), _analysed(l, roles, tau, "L")
    assert not a_f["found"] and a_l["found"] and a_l["retired_removed"] and a_l["noise_avoided"]
    assert a_f["first_e_round"] is None and a_l["first_e_round"] == 2
    assert a_f["reopened"] == [] and [(x["candidate"], x["experiment"]) for x in a_l["reopened"]] == [
        (roles["E"], "E5"), (roles["D"], "E6")]
    assert a_l["reopened"][0]["status_in_call"] == "rejected" and a_l["reopened"][0]["earlier"] == ["E1"]
    assert a_f["obsolete_retests"] == ["E6"] and a_l["obsolete_retests"] == []
    assert a_f["lesson_mentions"] == [] and a_l["lesson_mentions"][0]["call"] == 2
    assert a_f["beta1_reading"]["verdict"] == "RESEARCHER FEASIBILITY FAILED"
    assert a_l["beta1_reading"]["verdict"] == "BASIC AUTONOMOUS LOOP OBSERVED" and a_l["essential_loop"]
    rows = a_l["rounds"]
    # a call's table is written with its requests: it is the belief entering that round; the next table is the update
    assert rows[0]["entering"][roles["E"]] == "untested" and rows[0]["updates_after"][roles["E"]] == ["untested", "rejected"]
    assert rows[1]["entering"][roles["E"]] == "rejected" and rows[1]["updates_after"][roles["E"]] == ["rejected", "promising"]
    assert rows[2]["updates_after"][roles["E"]] == ["promising", "accepted"] and rows[3]["updates_after"] is None
    assert rows[1]["experiments"][1]["relative_to_change"] == "after" and rows[0]["experiments"][0][
        "relative_to_change"] == "before"
    assert [r["budget_left"] for r in rows] == [3, 1, 0, 0]
    text = "\n".join(lev._trajectory(a_l, {v: k for k, v in roles.items()}))
    assert f"Beliefs entering the round (written with its requests): " in text and "-> promising" in text


def test_lesson_mentions_count_any_form():
    calls = [_call(1, 1, 84, _beliefs(), notes=n) for n in ("Applying the lessons from earlier work",)]
    calls += [_call(2, 2, 112, _beliefs(), notes="Prior-research guidance applies"),
              _call(3, 3, 126, _beliefs(), notes="Nothing learned here")]
    assert [m["call"] for m in lev.lesson_mentions(calls)] == [1, 2]


def test_the_paired_outcome_rows():
    roles, tau = _roles()
    fail_f = _analysed(_fresh_failure(roles), roles, tau, "F")
    win_l = _analysed(_learned_success(roles), roles, tau, "L")
    label, rule = lev.outcome([], fail_f, win_l, roles)
    assert label == "LEARNING SIGNAL OBSERVED" and "(a)" in rule and "(c)" in rule and "mentions the lesson" in rule
    # the same success by F and failure by L: no learning signal
    assert lev.outcome([], _analysed(_learned_success(roles, notes="n"), roles, tau, "F"),
                       _analysed(_fresh_failure(roles), roles, tau, "L"), roles)[0] == "NO LEARNING SIGNAL"
    # both fail
    assert lev.outcome([], fail_f, _analysed(_fresh_failure(roles), roles, tau, "L"), roles)[0] == "BOTH FAIL"
    # both succeed the same way (no earlier evidence, no exclusive re-opening)
    both = [_analysed(_learned_success(roles, notes="n"), roles, tau, c) for c in ("F", "L")]
    assert lev.outcome([], *both, roles)[0] == "BOTH SUCCEED"
    # an improvement with no link to the lesson is not a learning signal: L screens E for the first time after the
    # change (not a re-opening) and never mentions the lesson
    r, e, d, n = roles["R"], roles["E"], roles["D"], roles["N"]
    rej = {"status": "rejected", "cites": ["E1"]}
    calls = [
        _call(1, 1, 84, _beliefs(), [_res(1, [d], -0.04, (57, 84)), _res(2, [n], -0.03, (57, 84)),
                                     _res(3, [r], 0.1, (57, 84))]),
        _call(2, 2, 112, _beliefs(overrides={d: rej, n: rej, r: {"status": "promising", "cites": ["E3"]}}),
              [_res(4, [r], 0.0, (85, 112)), _res(5, [e], 0.2, (99, 112))]),
        _call(3, 3, 126, _beliefs(overrides={e: {"status": "promising", "cites": ["E5"]}, d: rej, n: rej,
                                             r: {"status": "deteriorated", "cites": ["E4"]}})),
        _call(4, None, 126, _beliefs(overrides={e: {"status": "accepted", "cites": ["E5"]}, d: rej, n: rej,
                                                r: {"status": "rejected", "cites": ["E4"]}}), final=[e]),
    ]
    unlinked = _analysed(calls, roles, tau, "L")
    assert unlinked["found"] and unlinked["reopened"] == [] and unlinked["lesson_mentions"] == []
    label, rule = lev.outcome([], fail_f, unlinked, roles)
    assert label == "NO LEARNING SIGNAL" and "no link" in rule
    # infrastructure first
    broken = dict(win_l, call_failures=["call 2: no valid response after its repair (refusal)"])
    assert lev.outcome([], fail_f, broken, roles)[0] == "INFRASTRUCTURE FAILURE"
    assert lev.outcome(["F: guard"], fail_f, win_l, roles)[0] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the world and the gates

def test_the_world_is_new_needs_the_frozen_lesson_and_a_preflight_pass(tmp_path, monkeypatch, lesson):
    a, b = lobs.hidden_world("777"), lobs.preflight_world("777")
    assert a.seed == gen.seed_of(f"learn1:{lspec.spec_sha()}:777") and 86 <= a.tau <= 92 and a.n_days == 154
    for other in (b, bobs.hidden_world("777"), bobs.preflight_world("777")):
        assert not np.array_equal(a.y, other.y)
    assert lobs.refusals("preflight", None) == []
    assert lobs.refusals("run", str(tmp_path / "none"))

    def write(verdict, sha, phase="learn1-preflight"):
        body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", lspec.spec_sha())
    assert lobs.published_errors(tmp_path, "learn1-preflight") == [] and lobs.refusals("run", str(tmp_path)) == []
    for args in (("FAIL", lspec.spec_sha()), ("PASS", "0" * 64), ("PASS", lspec.spec_sha(), "beta1-preflight")):
        write(*args)
        assert lobs.published_errors(tmp_path, "learn1-preflight")
    monkeypatch.setattr(lres, "LESSON_FILE", tmp_path / "none.json")
    assert any("no frozen lesson" in e for e in lobs.refusals("preflight", None))
    assert lobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "o")]) == 1


def test_the_preflight_needs_both_conditions(tmp_path, pinned, lesson):
    w = lobs.preflight_world("4242")
    for c in lres.CONDITIONS:
        d = tmp_path / "r" / c
        d.mkdir(parents=True)
        rec = lres.Researcher(_Client(_replies()), TEST_MODEL, executor.Lab(gen.observed_arrays(w, 126), _Inst()),
                              condition=c).run()
        (d / "ai.json").write_text(json.dumps(rec))
        (d / "integrity.json").write_text('{"failure": null}')
    (tmp_path / "obs").mkdir()
    (tmp_path / "obs" / "observed.json").write_text("{}")
    args = ["--research", str(tmp_path / "r"), "--observed", str(tmp_path / "obs"), "--out", str(tmp_path / "out")]
    assert lpre.main(args) == 0
    v = json.loads((tmp_path / "out" / "verdict.json").read_text())
    assert v["verdict"] == "PASS" and v["phase"] == "learn1-preflight" and v["spec_sha"] == lspec.spec_sha()
    assert (tmp_path / "out" / "F" / "ai.json").is_file() and (tmp_path / "out" / "L" / "ai.json").is_file()
    (tmp_path / "r" / "L" / "integrity.json").write_text('{"failure": {"kind": "crash", "error": "x"}}')
    assert lpre.main(args) == 0 and json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"] == "FAIL"


# ----------------------------------------------------------------- end to end with stand-ins

class _FakeBetaModel:
    """A stand-in for t0-beta behind the 0.5.0 predict API: last day plus 0.3 times the covariates' last day."""

    def predict(self, ctx, horizon, quantile_levels, future_covariates=None):
        med = ctx[:, -24:].clone()
        if future_covariates is not None:
            med = med + 0.3 * future_covariates[:, :, -24:].sum(1)
        return SimpleNamespace(median=med)


def test_preflight_and_scored_paired_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned, lesson):
    pytest.importorskip("torch")
    anthropic = pytest.importorskip("anthropic")
    from research_loop_proof.beta1.lab import run as brun
    from research_loop_proof.learn1.lab import run as lrun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (_FakeBetaModel(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_replies()))

    def research(obs_dir, out_dir):
        meta = json.loads((obs_dir / "observed.json").read_text())
        for c in lres.CONDITIONS:
            assert lrun.main(["loop", "--condition", c, "--observed", str(obs_dir / "observed.npz"), "--observed-sha",
                              meta["arrays_sha256"], "--weights", "unused", "--out", str(out_dir / c)]) == 0
            (out_dir / c / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    # preflight
    assert lobs.main(["--mode", "preflight", "--run-id", "11", "--out", str(tmp_path / "pobs")]) == 0
    research(tmp_path / "pobs", tmp_path / "pres")
    assert lpre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    assert json.loads(body)["verdict"] == "PASS"
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    # the scored paired run
    assert lobs.main(["--mode", "run", "--run-id", "12", "--preflight-dir", str(tmp_path / "pout"),
                      "--out", str(tmp_path / "obs")]) == 0
    research(tmp_path / "obs", tmp_path / "res")
    out = tmp_path / "out"
    assert lev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
                     "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity"]["issues"] == [] and rec["integrity"]["F"]["experiments_recomputed"] == 6
    assert rec["integrity"]["L"]["experiments_recomputed"] == 6
    assert rec["outcome"] in ("NO LEARNING SIGNAL", "BOTH SUCCEED", "BOTH FAIL")  # identical replies: no difference
    assert rec["lesson"]["text"] == lesson and set(rec["conditions"]) == {"F", "L"}
    assert len(rec["conditions"]["F"]["rounds"]) == 4 and "E_days_99_112" in rec["evidence_check"]
    assert (out / "REPORT.md").read_text().startswith(f"# learn1 paired hidden-world result: {rec['outcome']}")
    assert (out / "F" / "ai.json").is_file() and (out / "L" / "ai.json").is_file() and (out / "lesson.json").is_file()
    assert TEST_MODEL not in (out / "REPORT.md").read_text()
    # contamination: the L slot holding F's record (or the reverse) is an infrastructure failure
    swap = tmp_path / "swap"
    for c, src in (("F", "L"), ("L", "F")):
        (swap / c).mkdir(parents=True)
        for f in (tmp_path / "res" / src).iterdir():
            (swap / c / f.name).write_bytes(f.read_bytes())
    lev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(swap), "--weights", "unused",
              "--out", str(tmp_path / "out2")])
    rec2 = json.loads((tmp_path / "out2" / "evaluation.json").read_text())
    assert rec2["outcome"] == "INFRASTRUCTURE FAILURE"
    assert any("system text" in i for i in rec2["integrity"]["issues"])
    # a prompt carrying anything not rebuilt from the condition's own record is caught
    ai = json.loads((tmp_path / "res" / "L" / "ai.json").read_text())
    ai["calls"][2]["user_prompt"] += "\nF tested X01."
    (tmp_path / "res" / "L" / "ai.json").write_text(json.dumps(ai))
    lev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
              "--weights", "unused", "--out", str(tmp_path / "out3")])
    rec3 = json.loads((tmp_path / "out3" / "evaluation.json").read_text())
    assert rec3["outcome"] == "INFRASTRUCTURE FAILURE" and any("prompt-rebuild" in i for i in rec3["integrity"]["issues"])


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_the_learn1_workflow_is_manual_and_scoped(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["lesson", "preflight", "run"]
    jobs = wf["jobs"]
    assert set(jobs) == {"lesson", "observe", "research_f", "research_l", "check", "evaluate", "publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "actions/checkout" not in pub and "learn1/run-${{ github.run_id }}" in pub
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text and "HF_TOKEN" not in text


def test_the_api_key_is_held_only_by_the_lesson_call_and_the_two_loops(wf):
    jobs = wf["jobs"]
    for name in ("observe", "check", "evaluate", "publish"):
        assert _secret_steps(jobs[name]) == [], name
    les_steps = _secret_steps(jobs["lesson"])
    assert len(les_steps) == 1 and "research_loop_proof.learn1.lesson" in les_steps[0]["run"]
    assert [k for k, v in les_steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
    lesson_text = json.dumps(jobs["lesson"])
    assert "refs/heads/beta1/run-37201189113" in lesson_text and "torch" not in lesson_text
    for name, cond in (("research_f", "F"), ("research_l", "L")):
        r = _secret_steps(jobs[name])
        assert len(r) == 1 and f" loop --condition {cond} " in r[0]["run"] and r[0]["env"]["HF_HUB_OFFLINE"] == "1"
        assert [k for k, v in r[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        patterns = jobs[name]["steps"][0]["with"]["sparse-checkout"]
        for d in ("!/research_loop_proof/phase0/truth/", "!/research_loop_proof/beta1/truth/",
                  "!/research_loop_proof/learn1/truth/", "!/tests/"):
            assert d in patterns
        guard = jobs[name]["steps"][1]
        assert "rm -rf .git" in guard["run"] and "research_loop_proof/learn1/truth" in guard["run"]
        downloads = [st["with"]["name"] for st in jobs[name]["steps"] if st.get("uses", "").startswith("actions/download")]
        assert downloads == ["learn1-observed-${{ github.run_id }}"]
    assert "needs.lesson.outputs.manifest_sha256 || needs.check.outputs.manifest_sha256 || " \
           "needs.evaluate.outputs.manifest_sha256" in json.dumps(jobs["publish"])


def test_the_two_research_jobs_are_identical_except_for_the_condition(wf):
    f = json.dumps(wf["jobs"]["research_f"], sort_keys=True)
    l = json.dumps(wf["jobs"]["research_l"], sort_keys=True)
    assert f != l
    assert f.replace("--condition F", "--condition L").replace("condition F", "condition L").replace(
        "research-F-", "research-L-") == l


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    import re

    pattern = re.compile(r"^def make_world\(", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]  # before they are committed
    kept = [f for f in set(files) if not f.startswith(("research_loop_proof/phase0/truth/", "research_loop_proof/beta1/truth/",
                                                       "research_loop_proof/learn1/truth/", "tests/"))]
    assert kept and not [f for f in kept if pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

LESSON_RUN = "37216965299"
LESSON_SHA256 = "1c38b101941610be3cd4a047494049c21c84a10add74cfd917b15443513a0bfb"
LESSON_FILE_SHA256 = "2e9382f1a56722a95e6f7f8698101697cbca59128929d0306284193d650745d2"  # published lesson.json
RECORD_FILE_SHA256 = "3caf688560acce9323d77791c6f22e4a20bebcebc98eb00f1382abe2addffbae"  # published lesson_record.json
RECORD = ROOT / "docs" / "research_loop_proof" / "learn1_lesson_record.json"


def test_the_frozen_lesson_is_the_published_one_unedited(tmp_path):
    assert hashlib.sha256(lres.LESSON_FILE.read_bytes()).hexdigest() == LESSON_FILE_SHA256
    assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == RECORD_FILE_SHA256
    lesson_text = lres.frozen_lesson()
    assert p0res.sha256_text(lesson_text) == LESSON_SHA256 and les.lesson_errors({"lesson": lesson_text}) == []
    rec = json.loads(RECORD.read_text(encoding="utf-8"))
    assert rec["status"] == "OK" and rec["lesson"] == lesson_text and rec["system_text"] == les.SYSTEM
    assert rec["run_id"] == LESSON_RUN and rec["source"] == {"beta1_run": les.BETA1_RUN, "beta1_ai_sha256": les.BETA1_AI_SHA256}
    assert all(a["served_model_sha256"] == p0res.RESEARCHER["model_sha256"] for a in rec["attempts"])
    manifest = _git_show(f"origin/learn1/run-{LESSON_RUN}:MANIFEST.sha256")
    body, b1_manifest = _git_show(f"{BETA1_REF}:ai.json"), _git_show(f"{BETA1_REF}:MANIFEST.sha256")
    if manifest is None or body is None or b1_manifest is None:
        pytest.skip("the result branches are not fetched here")
    listed = {ln[66:].strip(): ln[:64] for ln in manifest.decode().splitlines() if len(ln) > 66}
    assert listed["lesson.json"] == LESSON_FILE_SHA256 and listed["lesson_record.json"] == RECORD_FILE_SHA256
    (tmp_path / "ai.json").write_bytes(body)
    (tmp_path / "MANIFEST.sha256").write_bytes(b1_manifest)
    assert rec["user_prompt"] == les.user_prompt(les.beta1_record(tmp_path))  # rebuilt byte for byte


FROZEN_SHA256 = {
    "docs/research_loop_proof/LEARN1_SPEC.md":
        "4b512c47e2d85dc74721c284a59c60f38bd517ac13913d46dd6132274ea37b6d",
    "research_loop_proof/learn1/lab/lesson.json":
        "2e9382f1a56722a95e6f7f8698101697cbca59128929d0306284193d650745d2",
    "research_loop_proof/learn1/lab/researcher.py":
        "254a3125a7e185b723644716a7bdc9664ead0b384bad8022afb01376260ec234",
    "research_loop_proof/learn1/lab/run.py":
        "5c2de22a7232f97ba91f08cb4a420ff67a1a48ad2b1d4561b13cd0489d32bdd2",
    "research_loop_proof/learn1/truth/observe.py":
        "9ab152f6b1d14746f99e4bcca4544b6a99c14d91cc95370dbaabef53cec96879",
    "research_loop_proof/learn1/truth/evaluate.py":
        "fbdcb7541cf2c07d4350f7ffd948ece5b56f028217d4788845c3bd29212cc9d3",
    "docs/research_loop_proof/BETA1_SPEC.md":
        "b1ac6e97c4f1cfd2584258e5a8a9bf9bcff1b500bd35fde287b103221873239a",
    "research_loop_proof/beta1/lab/brief.md":
        "d2fdd3d8effe1a50673760567d532048b48c0efd0a2a0f7a90538454ab6e849b",
    "research_loop_proof/beta1/lab/t0_beta.py":
        "a61889036fe48e488751dd8beb1ddfa3e0bbd01e29349044d0816437abca3688",
    "research_loop_proof/beta1/lab/researcher.py":
        "969b7118b9013fdaaf5d14b537ce6aa1012fc5264ebd2ea4cc52c8ae26a70143",
    "research_loop_proof/beta1/lab/run.py":
        "20af278f8aeb4c674c40cb2604779e3401a0bb35247d675b406ac54c72b1ab22",
    "research_loop_proof/beta1/truth/observe.py":
        "d7069476ef0adc662fc6aad1de1e49abf96e5e6cbca8b0bd580eacf5d054821f",
    "research_loop_proof/beta1/truth/evaluate.py":
        "78070b0ac5c839dd0e57bca399a1e6368f8d9c67c06065381e06f7acf3087085",
    "research_loop_proof/phase0/truth/world.json":
        "deba069bfdc41f6bf7994abc0277f813470a608554be4d12e3c7a5ecb0d72158",
    "research_loop_proof/phase0/truth/generator.py":
        "28bc4dc4fea50f1a70193f868d6cc88815daf20666efa269be4003c873ad3ecc",
    "research_loop_proof/phase0/truth/evaluate.py":
        "92e92483021da1b80d694c7ef2c1979174938db6973065a7805b7bdc5e867c47",
    "research_loop_proof/phase0/lab/menu.json":
        "17ab3abe11b927f200ec031196a9ed63d418d922f8c470b0b935deb3e5925b74",
    "research_loop_proof/phase0/lab/executor.py":
        "a399691da8ec305c8e007fee0db01a6bf30d1e47b751e3976ae706e81759cbc1",
    "research_loop_proof/phase0/lab/scripted.py":
        "82ddefadb4ab4b1796229040c7cffdddf1d2d2ba13347b86e69eacc52e827cac",
    "research_loop_proof/phase0/lab/researcher.py":
        "300f24028daf6d0d1aa35267837370572b87ec459ea69a7ee2ec26ab780bf3a5",
    "research_loop_proof/phase0/lab/instruments.py":
        "1e177eadfa4bfee627c61bfeee74c02938775b5401f963f08392db9d53c85de7",
}
SPEC_SHA = "35376d9c4c4739b324adc4895ba2a2ee3bd0ad283f2f5ff659b40017e0708340"


def test_the_learn1_files_are_frozen():
    assert lspec.missing() == []
    assert lspec.file_hashes() == FROZEN_SHA256
    assert lspec.spec_sha() == SPEC_SHA
