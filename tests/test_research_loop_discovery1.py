"""Discovery1 (docs/research_loop_proof/NEXT_DISCOVERY_MILESTONE_PROMPT.md): the eight-candidate world, lab and
researcher L8, the fixed comparator, the gates, the evaluation and programme reading, and the workflow. Parts that need
torch or anthropic skip without them."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research_loop_proof.beta1.lab import researcher as bres
from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth import observe as bobs
from research_loop_proof.discovery1.lab import comparator
from research_loop_proof.discovery1.lab import executor as dex
from research_loop_proof.discovery1.lab import researcher as dres
from research_loop_proof.discovery1.truth import evaluate as dev
from research_loop_proof.discovery1.truth import observe as dobs
from research_loop_proof.discovery1.truth import preflight as dpre
from research_loop_proof.discovery1.truth import spec as dspec
from research_loop_proof.discovery1.truth import world as dworld
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.learn1.truth import observe as lobs
from research_loop_proof.phase0.lab import executor
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen
from research_loop_proof.policy1.truth import observe as pobs

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "discovery1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-discovery1.yml"
TEST_MODEL = "test-model-id"
IDS8 = dex.IDS8


# ----------------------------------------------------------------- fakes

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
        return self.replies.pop(0)


def _rows(status="untested", cites=None, overrides=None, ids=IDS8):
    rows = {i: {"candidate": i, "status": status, "cites": list(cites or []), "reason": "r"} for i in ids}
    for i, row in (overrides or {}).items():
        rows[i].update(row)
    return [rows[i] for i in ids]


def _exp(cov, ref=(), win=28):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves", "because": "b"}


def _reply(rows, exps=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": rows, "experiments": list(exps), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies():
    return [_resp(_reply(_rows(), [_exp(IDS8[:4]), _exp(IDS8[4:])])),
            _resp(_reply(_rows("promising", ["E1"]), [_exp(IDS8[4:6], win=14), _exp(IDS8[6:], win=14)])),
            _resp(_reply(_rows("promising", ["E3"]), [_exp(["X07"], win=14), _exp(["X08"], ["X07"], win=14)])),
            _resp(_reply(_rows("accepted", ["E5"], {"X08": {"status": "rejected", "cites": ["E6"]}}), final=["X07"],
                         conclusion="X07 helps."))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def unfrozen_ok(monkeypatch):
    """Before the freeze some frozen files may be missing; tests that generate worlds treat them as present."""
    monkeypatch.setattr(dspec, "missing", lambda root=None: [])


def _lab(world_id="4242"):
    return dex.Lab8(gen.observed_arrays(dobs.preflight_world(world_id), 126), _Inst())


# ----------------------------------------------------------------- separation and the mechanical adaptation

def test_the_discovery1_lab_never_imports_a_truth_package():
    for path in (PKG / "lab").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


def test_l8_is_learn1s_l_with_only_the_eight_candidate_enumeration():
    old, new = bres.BRIEF.splitlines(), dres.BRIEF8.splitlines()
    changed = [(a, b) for a, b in zip(old, new) if a != b]
    assert len(old) == len(new) and len(changed) == 2
    assert changed[0][0].replace(dres.CANDIDATES_LINE[0], dres.CANDIDATES_LINE[1]) == changed[0][1]
    assert changed[1][0].replace(dres.BELIEFS_LINE[0], dres.BELIEFS_LINE[1]) == changed[1][1]
    s8 = dres.system_text8()
    back = (s8.replace(dres.CANDIDATES_LINE[1], dres.CANDIDATES_LINE[0])
            .replace(dres.BELIEFS_LINE[1], dres.BELIEFS_LINE[0])
            .replace(json.dumps(dres.response_schema8(), indent=1), json.dumps(p0res.response_schema(), indent=1)))
    assert back == lres.system_text("L")
    assert lres.lesson_section(lres.frozen_lesson()) in s8 and "policy" not in s8.lower()
    s4, s8j = json.dumps(p0res.response_schema()), json.dumps(dres.response_schema8())
    assert s8j.count('"X08"') == 4 and s8j.replace(', "X05", "X06", "X07", "X08"', "") == s4


def _source(fn) -> str:
    return inspect.getsource(fn)


@pytest.mark.parametrize("ours, theirs, subs", [
    (dex.Lab8.__init__, executor.Lab.__init__, [("IDS8", "IDS")]),
    (dex.Lab8.run, executor.Lab.run, [("request_errors(req, IDS8)", "request_errors(req)")]),
    (dres.response_errors8, p0res.response_errors,
     [("def response_errors8(", "def response_errors("), ("request_errors(e, IDS8)", "request_errors(e)"),
      ("IDS8", "IDS")]),
    (dres.attempt_errors8, p0res.attempt_errors,
     [("def attempt_errors8(", "def attempt_errors("), ("response_errors8(", "response_errors(")]),
    (dres.Researcher8.run_call, p0res.Researcher.run_call, [("attempt_errors8(", "attempt_errors(")]),
    (dres.rebuild_mismatches8, p0res.rebuild_mismatches,
     [("def rebuild_mismatches8(", "def rebuild_mismatches("), ("attempt_errors8(", "attempt_errors(")]),
])
def test_each_adapted_function_is_phase0s_with_the_id_substitution_only(ours, theirs, subs):
    text = _source(ours)
    for a, b in subs:
        text = text.replace(a, b)
    assert text == _source(theirs)


def test_lab8_matches_phase0s_lab_on_four_candidates_and_validates_eight():
    w = dobs.preflight_world("31")
    obs8 = gen.observed_arrays(w, 126)
    obs4 = {"y": obs8["y"], **{i: obs8[i] for i in executor.IDS}}
    lab8, lab4 = dex.Lab8(obs8, _Inst()), executor.Lab(obs4, _Inst())
    req = {"covariates": ["X02", "X04"], "reference": ["X01"], "window_days": 14}
    assert lab8.run(req, 112, "E1") == lab4.run(req, 112, "E1")
    res = lab8.run({"covariates": ["X05", "X06", "X07", "X08"], "reference": [], "window_days": 28}, 126, "E2")
    assert res["scored_days"] == [99, 126] and set(res) == set(lab4.run(req, 112, "E1"))
    with pytest.raises(ValueError):
        lab8.run({"covariates": list(IDS8[:5]), "reference": [], "window_days": 28}, 126, "E3")
    with pytest.raises(ValueError):
        lab8.run({"covariates": ["X09"], "reference": [], "window_days": 28}, 126, "E3")


def test_the_l8_checks_enumerate_eight_candidates():
    step = dres.call_plan()[0]
    assert dres.response_errors8(_reply(_rows(), [_exp(["X05", "X06", "X07", "X08"])]), step, []) == []
    four = dres.response_errors8(_reply(_rows(ids=executor.IDS)), step, [])
    assert any("exactly one row for each of X01, X02, X03, X04, X05, X06, X07, X08" in e for e in four)
    assert dres.response_errors8(_reply(_rows(), [_exp(IDS8[:5])]), step, [])
    assert dres.response_errors8(_reply(_rows(), [_exp(["X05"], ["X05"])]), step, [])
    final = dres.call_plan()[-1]
    assert dres.response_errors8(_reply(_rows(), final=["X08"], conclusion="c"), final, []) == []
    assert dres.response_errors8(_reply(_rows(), final=["X09"], conclusion="c"), final, [])


def test_l8_runs_with_one_repair_and_its_prompts_rebuild(pinned):
    replies = _replies()
    replies.insert(1, _resp(_reply(_rows(ids=executor.IDS), [_exp(["X05"])])))  # call 2: 4 rows -> repaired
    client = _Client(replies)
    rec = dres.Researcher8(client, TEST_MODEL, _lab()).run()
    assert rec["condition"] == "L" and rec["final_valid"] and rec["final_selection"] == ["X07"]
    assert rec["system_text"] == dres.system_text8() and rec["system_sha256"] == p0res.sha256_text(dres.system_text8())
    assert [len(c["attempts"]) for c in rec["calls"]] == [1, 2, 1, 1]
    assert "X01, X02, X03, X04, X05, X06, X07, X08" in rec["calls"][1]["attempts"][1]["repair_prompt"]
    assert sum(len(c["experiments"]) for c in rec["calls"]) == 6
    sent = client.sent[0]
    assert sent["output_config"]["format"]["schema"] == dres.response_schema8()
    assert sent["system"][0]["text"] == dres.system_text8()
    assert dres.rebuild_mismatches8(rec["calls"]) == []
    rec["calls"][2]["user_prompt"] += "x"
    assert dres.rebuild_mismatches8(rec["calls"]) == ["call 3: user prompt"]


# ----------------------------------------------------------------- the comparator

class _ScriptedLab:
    """Returns given skills and lower bounds per (round cutoff, covariates)."""

    def __init__(self, table):
        self.table, self.calls = table, []

    def run(self, req, cutoff, exp_id):
        self.calls.append((cutoff, tuple(req["covariates"]), tuple(req["reference"]), req["window_days"]))
        skill, lo = self.table.get((cutoff, tuple(req["covariates"])), (0.0, -0.1))
        return {"id": exp_id, "covariates": req["covariates"], "reference": req["reference"], "skill": skill,
                "lo95": lo, "scored_days": [cutoff - 27, cutoff]}


def test_the_comparator_is_the_frozen_group_screen_split():
    a, b = tuple(IDS8[:4]), tuple(IDS8[4:])
    lab = _ScriptedLab({(84, a): (0.3, 0.1), (112, a): (0.05, -0.02), (112, b): (0.2, 0.1),
                        (126, ("X07", "X08")): (0.25, 0.12)})
    rec = comparator.run(lab)
    assert [c[:2] for c in lab.calls] == [(84, a), (84, b), (112, a), (112, b), (126, ("X05", "X06")),
                                          (126, ("X07", "X08"))]
    assert all(c[2] == () and c[3] == 28 for c in lab.calls)
    assert rec["winner"] == list(b) and rec["final_selection"] == ["X07", "X08"]
    assert [e["round"] for e in rec["experiments"]] == [1, 1, 2, 2, 3, 3]
    assert comparator.selection_errors(rec) == []
    tie = comparator.run(_ScriptedLab({(112, a): (0.1, 0.0), (112, b): (0.1, 0.0)}))
    assert tie["winner"] == list(a) and tie["final_selection"] == []
    bad = json.loads(json.dumps(rec))
    bad["final_selection"] = ["X07"]
    assert comparator.selection_errors(bad)
    bad = json.loads(json.dumps(rec))
    bad["experiments"][4]["request"]["covariates"] = ["X05", "X07"]
    assert comparator.selection_errors(bad)


def test_the_comparator_is_deterministic_on_the_lab():
    r1, r2 = comparator.run(_lab("77")), comparator.run(_lab("77"))
    assert r1 == r2 and len(r1["experiments"]) == 6


# ----------------------------------------------------------------- the world and the gates

def test_the_eight_candidate_world_keeps_the_base_world():
    w = dworld.make_world8(98765)
    base = gen.make_world(98765, n_days=154, tau=None, form="linear", m=gen.WORLD["calibration"]["m"],
                          tau_rule=True)
    assert np.array_equal(w.y, base.y) and w.tau == base.tau and 86 <= w.tau <= 92 and w.n_days == 154
    for r, b in (("R", "R"), ("E", "E"), ("D", "D"), ("N1", "N")):
        assert np.array_equal(w.x[r], base.x[b]) and w.signs[r] == base.signs[b]
    assert set(w.ids) == set(dworld.ROLES8) and sorted(w.ids.values()) == list(IDS8)
    pre = slice(0, (w.tau - 1) * 24)
    for r in dworld.NOISE[1:]:
        assert abs(w.x[r][pre].mean()) < 1e-9 and abs(w.x[r][pre].std() - 1) < 1e-9 and w.signs[r] in (1, -1)
        assert not np.array_equal(np.abs(w.x[r]), np.abs(w.x["N1"]))
    again = dworld.make_world8(98765)
    assert again.ids == w.ids and all(np.array_equal(again.x[r], w.x[r]) for r in dworld.ROLES8)
    assert w.canary.startswith("CANARY-") and w.canary != base.canary
    obs = gen.observed_arrays(w, 126)
    assert sorted(obs) == list(IDS8) + ["y"] and len(obs["y"]) == 126 * 24
    perms = {tuple(dworld.make_world8(s).ids[r] for r in dworld.ROLES8) for s in range(20)}
    assert len(perms) > 15


def test_the_worlds_are_new_and_gated(tmp_path, unfrozen_ok):
    ws = [dobs.hidden_world("777", k) for k in dobs.SCORED_WORLDS]
    assert [w.seed for w in ws] == [gen.seed_of(f"discovery1:{dspec.spec_sha()}:777:{k}") for k in dobs.SCORED_WORLDS]
    pf = dobs.preflight_world("777")
    others = [pf, bobs.hidden_world("777"), lobs.hidden_world("777"), pobs.hidden_world("777")]
    for a in ws:
        assert not any(np.array_equal(a.y, o.y) for o in others + [b for b in ws if b is not a])
    with pytest.raises(ValueError):
        dobs.hidden_world("777", "w4")
    assert dobs.refusals("preflight", None) == [] and dobs.refusals("run", str(tmp_path / "none"))

    def write(verdict, sha, phase="discovery1-preflight"):
        body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", dspec.spec_sha())
    assert dobs.refusals("run", str(tmp_path)) == []
    for args in (("FAIL", dspec.spec_sha()), ("PASS", "0" * 64), ("PASS", dspec.spec_sha(), "policy1-preflight")):
        write(*args)
        assert dobs.published_errors(tmp_path, "discovery1-preflight")


def test_observe_writes_one_world_in_preflight_and_three_in_run(tmp_path, unfrozen_ok):
    assert dobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "p")]) == 0
    assert sorted(p.name for p in (tmp_path / "p").iterdir()) == ["observed.json", "w1"]
    meta = json.loads((tmp_path / "p" / "w1" / "observed.json").read_text())
    obs = executor.load_observed(tmp_path / "p" / "w1" / "observed.npz")
    assert meta["keys"] == list(IDS8) + ["y"] and executor.arrays_sha256(obs) == meta["arrays_sha256"]
    assert gen.arrays_sha256(gen.observed_arrays(dobs.preflight_world("5"), 126)) == meta["arrays_sha256"]


def test_missing_frozen_files_refuse_worlds(tmp_path):
    if not dspec.missing():
        pytest.skip("frozen: nothing is missing")
    assert dobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "o")]) == 1


# ----------------------------------------------------------------- indicators, success and the reading

ROLES = {"R": "X03", "E": "X06", "D": "X01", "N1": "X02", "N2": "X04", "N3": "X05", "N4": "X07", "N5": "X08"}


def _x(i, rnd, cov, lo, ref=()):
    return {"id": i, "round": rnd, "request": {"covariates": list(cov), "reference": list(ref), "window_days": 28},
            "result": {"skill": lo + 0.1, "lo95": lo, "hi95": lo + 0.2, "scored_days": [1, 28]}}


def test_indicators_and_the_six_criteria():
    exps = [_x("E1", 1, ["X05", "X06", "X07", "X08"], -0.1), _x("E3", 2, ["X05", "X06"], 0.1),
            _x("E5", 3, ["X06"], 0.12), _x("E6", 3, ["X01"], 0.05, ["X06"])]
    ind = dev.indicators(exps, ["X06"], ROLES)
    assert ind["first_entered"] == {"id": "E1", "round": 1, "as": "covariate"} and ind["first_post_change_test"] == "E3"
    assert ind["distinguished"] and ind["supporting_evidence"] == ["E5"] and ind["e_selected"]
    assert not ind["noise_selected"] and not ind["d_selected"] and [x["id"] for x in ind["d_experiments"]] == ["E6"]
    s = dev.success(ind, True, {"lo95": 0.05})
    assert s["success"] and all(s["criteria"].values())
    assert not dev.success(ind, False, {"lo95": 0.05})["success"]
    assert not dev.success(ind, True, {"lo95": -0.01})["success"] and not dev.success(ind, True, None)["success"]
    noisy = dev.indicators(exps, ["X05", "X06"], ROLES)
    assert noisy["noise_selected"] == ["X05"] and noisy["supporting_evidence"] == ["E5", "E3"]
    assert not dev.success(noisy, True, {"lo95": 0.2})["criteria"]["4_no_r_no_noise"]
    pair = dev.indicators([_x("C5", 3, ["X06", "X01"], 0.1)], ["X01", "X06"], ROLES)
    assert pair["supporting_evidence"] == ["C5"] and not pair["distinguished"] and pair["d_selected"]
    assert dev.success(pair, True, {"lo95": 0.1})["success"]  # D may be selected
    ref_only = dev.indicators([_x("E2", 2, ["X01"], 0.1, ["X06"])], ["X06"], ROLES)
    assert ref_only["first_entered"]["as"] == "reference" and not ref_only["tested_post_change"]
    assert not dev.success(ref_only, True, {"lo95": 0.1})["success"]
    pre_only = dev.indicators([_x("E1", 1, ["X06"], 0.1)], ["X06"], ROLES)
    assert not pre_only["tested_post_change"] and not pre_only["supporting_evidence"]


def _worlds(*triples):
    return {f"w{i + 1}": {"informative": inf, "L8": {"success": l8}, "comparator": {"success": c}}
            for i, (inf, l8, c) in enumerate(triples)}


@pytest.mark.parametrize("triples, label, row", [
    (((True, True, False), (True, True, False), (True, False, False)), "DISCOVERY SIGNAL", "row 3"),
    (((True, True, True), (True, True, False), (True, False, False)), "DISCOVERY SIGNAL", "row 3"),
    (((True, True, True), (True, True, True), (True, False, False)), "BOTH SUCCEED", "row 4"),
    (((True, True, True), (True, True, True), (True, True, True)), "BOTH SUCCEED", "row 4"),
    (((True, False, False), (True, False, True), (True, True, False)), "NO DISCOVERY SIGNAL", "row 5"),
    (((True, False, False), (True, False, False), (False, False, False)), "NO DISCOVERY SIGNAL", "row 5"),
    (((True, True, False), (True, False, False), (False, False, False)), "NO DISCOVERY SIGNAL", "row 6"),
    (((True, True, False), (False, False, False), (False, False, False)), "BENCHMARK FAILURE", "row 2"),
    (((True, True, True), (True, True, True), (False, False, False)), "BOTH SUCCEED", "row 4"),
    (((True, True, False), (True, True, False), (False, False, False)), "DISCOVERY SIGNAL", "row 3"),
])
def test_every_programme_row(triples, label, row):
    got = dev.programme([], [], _worlds(*triples))
    assert got[0] == label and got[1].startswith(row)
    assert dev.CLOSING[label] in ("MOVE TO A REAL-WORLD RESEARCH TEST", "NARROW TO HUMAN-SUPPLIED HYPOTHESES",
                                  "BENCHMARK/INFRASTRUCTURE RESULT ONLY")


def test_infrastructure_failure_comes_first_and_the_closing_lines_are_predeclared():
    good = _worlds((True, True, False), (True, True, False), (True, True, False))
    assert dev.programme(["w2: guard"], [], good)[0] == "INFRASTRUCTURE FAILURE"
    assert dev.programme([], ["w1: L8 call 4: never made"], good)[0] == "INFRASTRUCTURE FAILURE"
    assert dev.CLOSING == {"DISCOVERY SIGNAL": "MOVE TO A REAL-WORLD RESEARCH TEST",
                           "NO DISCOVERY SIGNAL": "NARROW TO HUMAN-SUPPLIED HYPOTHESES",
                           "BOTH SUCCEED": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
                           "BENCHMARK FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
                           "INFRASTRUCTURE FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY"}


# ----------------------------------------------------------------- the preflight

def test_the_preflight_checks_l8_and_the_comparator(tmp_path, pinned, unfrozen_ok):
    d = tmp_path / "r" / "w1"
    d.mkdir(parents=True)
    lab = _lab()
    (d / "ai.json").write_text(json.dumps(dres.Researcher8(_Client(_replies()), TEST_MODEL, lab).run()))
    (d / "integrity.json").write_text('{"failure": null}')
    (d / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    (d / "comparator.json").write_text(json.dumps(comparator.run(lab)))
    (tmp_path / "obs" / "w1").mkdir(parents=True)
    (tmp_path / "obs" / "w1" / "observed.json").write_text("{}")
    args = ["--research", str(tmp_path / "r"), "--observed", str(tmp_path / "obs"), "--out", str(tmp_path / "out")]
    assert dpre.main(args) == 0
    v = json.loads((tmp_path / "out" / "verdict.json").read_text())
    assert v["verdict"] == "PASS" and v["phase"] == "discovery1-preflight" and v["spec_sha"] == dspec.spec_sha()
    rec = json.loads((tmp_path / "out" / "preflight.json").read_text())["w1"]
    assert rec["illegal_experiments"] == 0 and rec["enumeration_ok"] and rec["experiments"] == 6

    def verdict_after(name, change):
        good = (d / name).read_text()
        obj = json.loads(good)
        change(obj)
        (d / name).write_text(json.dumps(obj))
        dpre.main(args)
        (d / name).write_text(good)
        return json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"]
    assert verdict_after("ai.json", lambda a: a["calls"][1].update(user_prompt=a["calls"][1]["user_prompt"] + "x")) \
        == "FAIL"
    assert verdict_after("ai.json", lambda a: a.update(system_text=lres.system_text("L"))) == "FAIL"
    assert verdict_after("comparator.json", lambda c: c.update(final_selection=["X01"])) == "FAIL"
    assert verdict_after("guard.json", lambda g: g.update(truth_absent=False)) == "FAIL"
    assert dpre.main(args) == 0 and json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"] == "PASS"


# ----------------------------------------------------------------- end to end with stand-ins

class _FakeBetaModel:
    def predict(self, ctx, horizon, quantile_levels, future_covariates=None):
        med = ctx[:, -24:].clone()
        if future_covariates is not None:
            med = med + 0.3 * future_covariates[:, :, -24:].sum(1)
        return SimpleNamespace(median=med)


def test_preflight_and_the_three_world_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned, unfrozen_ok):
    pytest.importorskip("torch")
    anthropic = pytest.importorskip("anthropic")
    from research_loop_proof.beta1.lab import run as brun
    from research_loop_proof.discovery1.lab import run as drun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (_FakeBetaModel(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_replies()))

    def research(obs_dir, out_dir, worlds):
        for k in worlds:
            meta = json.loads((obs_dir / k / "observed.json").read_text())
            common = ["--observed", str(obs_dir / k / "observed.npz"), "--observed-sha", meta["arrays_sha256"],
                      "--weights", "unused", "--out", str(out_dir / k)]
            assert drun.main(["comparator", *common]) == 0
            assert drun.main(["loop", *common]) == 0
            (out_dir / k / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    assert dobs.main(["--mode", "preflight", "--run-id", "11", "--out", str(tmp_path / "pobs")]) == 0
    research(tmp_path / "pobs", tmp_path / "pres", ["w1"])
    assert dpre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    assert json.loads(body)["verdict"] == "PASS"
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    assert dobs.main(["--mode", "run", "--run-id", "12", "--preflight-dir", str(tmp_path / "pout"),
                      "--out", str(tmp_path / "obs")]) == 0
    research(tmp_path / "obs", tmp_path / "res", dobs.SCORED_WORLDS)
    out = tmp_path / "out"
    assert dev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
                     "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity_issues"] == [] and rec["call_failures"] == []
    for k in dobs.SCORED_WORLDS:
        r = rec["worlds"][k]
        assert r["integrity"]["experiments_recomputed"] == 6 and r["integrity"]["comparator_recomputed"] == 6
        assert len(r["truth"]["roles"]) == 8 and r["L8"]["experiments_used"] == 6
    assert rec["reading"] in dev.CLOSING and rec["closing_line"] == dev.CLOSING[rec["reading"]]
    report = (out / "REPORT.md").read_text()
    assert report.startswith(f"# Discovery1 three-world result: {rec['reading']}") and TEST_MODEL not in report
    assert all((out / k / "ai.json").is_file() and (out / k / "comparator.json").is_file() for k in dobs.SCORED_WORLDS)
    swap = tmp_path / "swap"
    for k, src in (("w1", "w2"), ("w2", "w1"), ("w3", "w3")):
        (swap / k).mkdir(parents=True)
        for f in (tmp_path / "res" / src).iterdir():
            (swap / k / f.name).write_bytes(f.read_bytes())
    dev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(swap), "--weights", "unused",
              "--out", str(tmp_path / "out2")])
    assert json.loads((tmp_path / "out2" / "evaluation.json").read_text())["reading"] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_the_discovery1_workflow_is_manual_scoped_and_isolated(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["preflight", "run"]
    jobs = wf["jobs"]
    assert set(jobs) == {"observe", "research_w1", "research_w2", "research_w3", "check", "evaluate", "publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    for name in ("observe", "check", "evaluate", "publish"):
        assert _secret_steps(jobs[name]) == [], name
    for k in ("w1", "w2", "w3"):
        job = jobs[f"research_{k}"]
        steps = _secret_steps(job)
        assert len(steps) == 1 and f" loop --observed obs/{k}/observed.npz " in steps[0]["run"]
        assert steps[0]["env"]["HF_HUB_OFFLINE"] == "1"
        assert [key for key, v in steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        comp = [st for st in job["steps"] if " comparator " in st.get("run", "")]
        assert len(comp) == 1 and "secrets." not in json.dumps(comp[0])
        patterns = job["steps"][0]["with"]["sparse-checkout"]
        for d in ("!/research_loop_proof/phase0/truth/", "!/research_loop_proof/beta1/truth/",
                  "!/research_loop_proof/learn1/truth/", "!/research_loop_proof/policy1/truth/",
                  "!/research_loop_proof/discovery1/truth/", "!/tests/"):
            assert d in patterns, k
        guard = job["steps"][1]
        assert "rm -rf .git" in guard["run"] and "research_loop_proof/discovery1/truth" in guard["run"]
    assert jobs["research_w1"]["if"] == "inputs.mode == 'preflight' || inputs.mode == 'run'"
    assert jobs["research_w2"]["if"] == jobs["research_w3"]["if"] == "inputs.mode == 'run'"
    assert jobs["check"]["needs"] == ["observe", "research_w1"]
    assert jobs["evaluate"]["needs"] == ["observe", "research_w1", "research_w2", "research_w3"]
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "discovery1/run-${{ github.run_id }}" in pub
    assert "needs.check.outputs.manifest_sha256 || needs.evaluate.outputs.manifest_sha256" in pub
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text and "HF_TOKEN" not in text


def test_the_three_research_jobs_are_identical_except_for_the_world(wf):
    j = {k: json.dumps({n: v for n, v in wf["jobs"][f"research_{k}"].items() if n != "if"}, sort_keys=True)
         for k in ("w1", "w2", "w3")}
    assert j["w1"] != j["w2"] and j["w1"].replace("w1", "w2") == j["w2"] and j["w1"].replace("w1", "w3") == j["w3"]


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    import re

    pattern = re.compile(r"^def make_world", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]
    excluded = tuple(f"research_loop_proof/{p}/truth/" for p in ("phase0", "beta1", "learn1", "policy1", "discovery1"))
    kept = [f for f in set(files) if not f.startswith(excluded + ("tests/",))]
    assert kept and not [f for f in kept if pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

FROZEN_SHA256 = {
    "docs/research_loop_proof/DISCOVERY1_SPEC.md":
        "17e8f4704d381d533e4c2268fac3b146157a2de85f584be0d26525df41069645",
    "research_loop_proof/discovery1/lab/executor.py":
        "1b6fae001c69ca5e7207cd9f4697807e17fb7ea0fe5cafbf1a2489804746ee0e",
    "research_loop_proof/discovery1/lab/researcher.py":
        "ced33dd4727129a2a670755d03cccbbe12fff0fe2ddc55a8d459e673d48f30fa",
    "research_loop_proof/discovery1/lab/comparator.py":
        "3613266162abc068daa50d4d7f5ee8d6825ea1e83d4f5131b6cca5e46296db97",
    "research_loop_proof/discovery1/lab/run.py":
        "a1b33a42a3b51ab140bbfc0875b941f9e8f71c505fe57fa275244266c79f8e32",
    "research_loop_proof/discovery1/truth/world.py":
        "76c3d3d95b7f6fc63ecf033276f5f408447b4138ee62cf1bd716cf5f47cdbc26",
    "research_loop_proof/discovery1/truth/observe.py":
        "c8c40f7914306ef9a201c78d31129f8248f0adfcffe6ea9c7eaf85ef51ae56a9",
    "research_loop_proof/discovery1/truth/evaluate.py":
        "da5a51ceaafcd12fe8b6f7532b01de43c56dbac77d5261975e51f3dfc2c198e6",
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
SPEC_SHA = "52e737b5a885b456596a8e71f23c9daaefa426b6aa99dfc0a3165973aeca5d96"


def test_the_discovery1_files_are_frozen():
    assert dspec.missing() == []
    assert dspec.file_hashes() == FROZEN_SHA256
    assert dspec.spec_sha() == SPEC_SHA
