"""Human1 (docs/research_loop_proof/NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md): the human-supplied pair, the two-candidate
lab and researcher L2, the fixed comparator, the adjudication rules, the gates, the programme reading and the workflow.
Parts that need torch or anthropic skip without them."""

from __future__ import annotations

import ast
import difflib
import hashlib
import inspect
import itertools
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research_loop_proof.beta1.lab import researcher as bres
from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth import observe as bobs
from research_loop_proof.discovery1.truth import observe as dobs
from research_loop_proof.human1.lab import comparator
from research_loop_proof.human1.lab import executor as hex_
from research_loop_proof.human1.lab import researcher as hres
from research_loop_proof.human1.truth import adjudicate as adj
from research_loop_proof.human1.truth import evaluate as hev
from research_loop_proof.human1.truth import observe as hobs
from research_loop_proof.human1.truth import preflight as hpre
from research_loop_proof.human1.truth import spec as hspec
from research_loop_proof.human1.truth import world as hworld
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.learn1.truth import observe as lobs
from research_loop_proof.phase0.lab import executor
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "human1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-human1.yml"
TEST_MODEL = "test-model-id"
IDS2 = hex_.IDS2


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


def _rows(statuses=None, cites=None, ids=IDS2):
    statuses = statuses or {}
    return [{"candidate": i, "status": statuses.get(i, "untested"), "cites": list(cites or []), "reason": "r"}
            for i in ids]


def _exp(cov, ref=(), win=28):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves", "because": "b"}


def _reply(rows, exps=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": rows, "experiments": list(exps), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies():
    return [_resp(_reply(_rows(), [_exp(["X01"], win=14), _exp(["X02"], win=14)])),
            _resp(_reply(_rows({"X01": "promising"}, ["E1"]), [_exp(["X01"], ["X02"]), _exp(["X02"], ["X01"])])),
            _resp(_reply(_rows({"X01": "accepted", "X02": "redundant"}, ["E3"]), final=["X01"],
                         conclusion="X01 helps; X02 adds nothing given X01."))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def unfrozen_ok(monkeypatch):
    """Before the freeze some frozen files may be missing; tests that generate worlds treat them as present."""
    monkeypatch.setattr(hspec, "missing", lambda root=None: [])


def _lab(world_id="4242"):
    return hex_.Lab2(gen.observed_arrays(hobs.preflight_world(world_id), 126), _Inst())


# ----------------------------------------------------------------- separation and the mechanical adaptation

def test_the_human1_lab_never_imports_a_truth_package():
    for path in (PKG / "lab").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


def test_l2_is_learn1s_l_with_only_the_five_mechanical_edits():
    old, new = bres.BRIEF.splitlines(), hres.BRIEF2.splitlines()
    ops = [op for op in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes() if op[0] != "equal"]
    changed = [(old[i1:i2], new[j1:j2]) for _, i1, i2, j1, j2 in ops]
    edited = [(o, n) for o, n in changed for o, n in zip(o, n)]
    inserted = [line for o, n in changed for line in n[len(o):]]
    assert len(edited) == 4 and inserted == ["- " + hres.PACKET]
    for (o, n), (a, b) in zip(edited, hres.REPLACEMENTS):
        assert o.replace(a, b) == n
    owner = (ROOT / "docs/research_loop_proof/NEXT_HUMAN_HYPOTHESIS_MILESTONE_PROMPT.md").read_text(encoding="utf-8")
    assert "> " + hres.PACKET in owner
    s2 = hres.system_text2()
    back = s2.replace("- " + hres.PACKET + "\n", "")
    for a, b in hres.REPLACEMENTS:
        back = back.replace(b, a)
    back = back.replace(json.dumps(hres.response_schema2(), indent=1), json.dumps(p0res.response_schema(), indent=1))
    assert back == lres.system_text("L")
    assert lres.lesson_section(lres.frozen_lesson()) in s2
    assert "1 to 4 candidate ids" in s2 and "0 to 2 candidate ids" in s2
    for word in ("retire", "proxy", "noise", "emerg", "test each", "conditional"):
        assert word not in hres.PACKET.lower()
    s4, s2j = json.dumps(p0res.response_schema()), json.dumps(hres.response_schema2())
    assert s2j.count('"X02"') == 4 and '"X03"' not in s2j
    assert s2j.replace('["X01", "X02"]', '["X01", "X02", "X03", "X04"]') == s4


def _source(fn) -> str:
    return inspect.getsource(fn)


@pytest.mark.parametrize("ours, theirs, subs", [
    (hex_.Lab2.__init__, executor.Lab.__init__, [("IDS2", "IDS")]),
    (hex_.Lab2.run, executor.Lab.run, [("request_errors(req, IDS2)", "request_errors(req)")]),
    (hres.call_plan2, p0res.call_plan,
     [("def call_plan2(", "def call_plan("), ("The three calls: rounds 1-2", "The four calls: rounds 1-3"),
      ("FINAL_CUTOFF2", "FINAL_CUTOFF"), ("ROUNDS2", "ROUNDS")]),
    (hres.budget_left2, p0res.budget_left, [("def budget_left2(", "def budget_left("), ("BUDGET2", "BUDGET")]),
    (hres.user_prompt2, p0res.user_prompt,
     [("def user_prompt2(", "def user_prompt("), ("budget_left2(", "budget_left("), ("call_plan2(", "call_plan("),
      ("BUDGET2", "BUDGET")]),
    (hres.response_errors2, p0res.response_errors,
     [("def response_errors2(", "def response_errors("), ("request_errors(e, IDS2)", "request_errors(e)"),
      ("budget_left2(", "budget_left("), ("BUDGET2", "BUDGET"), ("IDS2", "IDS")]),
    (hres.attempt_errors2, p0res.attempt_errors,
     [("def attempt_errors2(", "def attempt_errors("), ("response_errors2(", "response_errors(")]),
    (hres.Researcher2.run_call, p0res.Researcher.run_call,
     [("user_prompt2(", "user_prompt("), ("attempt_errors2(", "attempt_errors(")]),
    (hres.Researcher2.run_plan2, p0res.Researcher.run, [("def run_plan2(", "def run("), ("call_plan2(", "call_plan(")]),
    (hres.rebuild_mismatches2, p0res.rebuild_mismatches,
     [("def rebuild_mismatches2(", "def rebuild_mismatches("), ("call_plan2(", "call_plan("),
      ("user_prompt2(", "user_prompt("), ("attempt_errors2(", "attempt_errors(")]),
    (hev.call_failures2, __import__("research_loop_proof.beta1.truth.evaluate", fromlist=["x"]).call_failures,
     [("def call_failures2(", "def call_failures("), ("call_plan2(", "call_plan(")]),
])
def test_each_adapted_function_is_the_original_with_the_substitution_only(ours, theirs, subs):
    text = _source(ours)
    for a, b in subs:
        text = text.replace(a, b)
    assert text == _source(theirs)


def test_lab2_matches_phase0s_lab_and_validates_two_ids():
    w = hobs.preflight_world("31")
    obs2 = gen.observed_arrays(w, 126)
    base = gen.make_world(w.seed, n_days=154, tau=None, form="linear", m=gen.WORLD["calibration"]["m"], tau_rule=True)
    obs4 = gen.observed_arrays(base, 126)
    role_of = {v: r for r, v in w.ids.items()}
    alias = {"y": obs2["y"], "X01": obs2["X01"], "X02": obs2["X02"], "X03": obs4["X03"], "X04": obs4["X04"]}
    lab2, lab4 = hex_.Lab2(obs2, _Inst()), executor.Lab(alias, _Inst())
    req = {"covariates": ["X02"], "reference": ["X01"], "window_days": 14}
    assert lab2.run(req, 112, "E1") == lab4.run(req, 112, "E1")
    assert np.array_equal(obs2["X01"], base.x[role_of["X01"]][:126 * 24])
    with pytest.raises(ValueError):
        lab2.run({"covariates": ["X03"], "reference": [], "window_days": 28}, 126, "E2")


def test_the_l2_checks_and_budget():
    plan = hres.call_plan2()
    assert [(s["round"], s["cutoff"], s["final"]) for s in plan] == [(1, 112, False), (2, 126, False), (None, 126, True)]
    step = plan[0]
    assert hres.response_errors2(_reply(_rows(), [_exp(["X01"]), _exp(["X02"], ["X01"])]), step, []) == []
    assert any("at most 2 experiments" in e for e in
               hres.response_errors2(_reply(_rows(), [_exp(["X01"])] * 3), step, []))
    assert any("exactly one row for each of X01, X02" in e for e in
               hres.response_errors2(_reply(_rows(ids=executor.IDS)), step, []))
    assert hres.response_errors2(_reply(_rows(), [_exp(["X03"])]), step, [])
    final = plan[-1]
    assert hres.response_errors2(_reply(_rows(), final=["X02"], conclusion="c"), final, []) == []
    assert hres.response_errors2(_reply(_rows(), final=["X03"], conclusion="c"), final, [])
    prompt = hres.user_prompt2(step, [])
    assert prompt.startswith("CALL 1 OF 3: ROUND 1\nObserved so far: days 1-112.\nExperiment budget: 4 of 4 left; you "
                             "may request at most 2 in this call.")


def test_l2_runs_three_calls_with_one_repair_and_its_prompts_rebuild(pinned):
    replies = _replies()
    replies.insert(0, _resp(_reply(_rows(), [_exp(["X01"])] * 3)))  # call 1: three experiments -> repaired
    client = _Client(replies)
    rec = hres.Researcher2(client, TEST_MODEL, _lab()).run()
    assert rec["condition"] == "L" and rec["final_valid"] and rec["final_selection"] == ["X01"]
    assert rec["system_text"] == hres.system_text2() and rec["system_sha256"] == p0res.sha256_text(hres.system_text2())
    assert [len(c["attempts"]) for c in rec["calls"]] == [2, 1, 1]
    assert "at most 2 experiments may be requested" in rec["calls"][0]["attempts"][1]["repair_prompt"]
    assert sum(len(c["experiments"]) for c in rec["calls"]) == 4
    assert client.sent[0]["output_config"]["format"]["schema"] == hres.response_schema2()
    assert client.sent[0]["system"][0]["text"] == hres.system_text2()
    assert rec["calls"][1]["user_prompt"].startswith("CALL 2 OF 3: ROUND 2\nObserved so far: days 1-126.\n"
                                                     "Experiment budget: 2 of 4 left")
    assert hres.rebuild_mismatches2(rec["calls"]) == []
    rec["calls"][2]["user_prompt"] += "x"
    assert hres.rebuild_mismatches2(rec["calls"]) == ["call 3: user prompt"]


# ----------------------------------------------------------------- the world and the packet

def test_the_world_is_the_base_world_and_only_the_pair_is_exported():
    for pair in hworld.PAIRS.values():
        w = hworld.make_world_pair(98765, pair)
        base = gen.make_world(98765, n_days=154, tau=None, form="linear", m=gen.WORLD["calibration"]["m"],
                              tau_rule=True)
        assert np.array_equal(w.y, base.y) and w.tau == base.tau and 86 <= w.tau <= 92
        assert set(w.ids) == set(pair) and sorted(w.ids.values()) == list(IDS2)
        for r in pair:
            assert np.array_equal(w.x[r], base.x[r])
        obs = gen.observed_arrays(w, 126)
        assert sorted(obs) == ["X01", "X02", "y"]
        assert np.array_equal(obs[w.ids["E"]], base.x["E"][:126 * 24])
        assert w.canary.startswith("CANARY-") and w.canary != base.canary
    orders = {hworld.make_world_pair(s, ("E", "D")).ids["E"] for s in range(12)}
    assert orders == {"X01", "X02"}
    assert hworld.PAIRS == {"w1": ("E", "D"), "w2": ("E", "N"), "w3": ("E", "R")}
    with pytest.raises(ValueError):
        hworld.make_world_pair(1, ("E", "E"))


def test_the_worlds_are_new_and_gated(tmp_path, unfrozen_ok):
    ws = {k: hobs.hidden_world("777", k) for k in hobs.SCORED_WORLDS}
    for k, w in ws.items():
        assert w.seed == gen.seed_of(f"human1:{hspec.spec_sha()}:777:{k}") and set(w.ids) == set(hworld.PAIRS[k])
    pf = hobs.preflight_world("777")
    assert set(pf.ids) == {"E", "D"}
    others = [pf, bobs.hidden_world("777"), lobs.hidden_world("777"), dobs.hidden_world("777", "w1")]
    for w in ws.values():
        assert not any(np.array_equal(w.y, o.y) for o in others + [v for v in ws.values() if v is not w])
    with pytest.raises(ValueError):
        hobs.hidden_world("777", "w4")
    assert hobs.refusals("preflight", None) == [] and hobs.refusals("run", str(tmp_path / "none"))

    def write(verdict, sha, phase="human1-preflight"):
        body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", hspec.spec_sha())
    assert hobs.refusals("run", str(tmp_path)) == []
    for args in (("FAIL", hspec.spec_sha()), ("PASS", "0" * 64), ("PASS", hspec.spec_sha(), "discovery1-preflight")):
        write(*args)
        assert hobs.published_errors(tmp_path, "human1-preflight")


def test_observe_exports_the_pair_only_with_no_role_information(tmp_path, unfrozen_ok):
    assert hobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "p")]) == 0
    assert sorted(p.name for p in (tmp_path / "p").iterdir()) == ["observed.json", "w1"]
    text = (tmp_path / "p" / "w1" / "observed.json").read_text()
    meta = json.loads(text)
    assert meta["keys"] == ["X01", "X02", "y"]
    assert not any(word in text for word in ('"E"', '"D"', '"R"', '"N"', "E+", "pair", "role", "tau"))
    obs = executor.load_observed(tmp_path / "p" / "w1" / "observed.npz")
    assert sorted(obs) == ["X01", "X02", "y"] and executor.arrays_sha256(obs) == meta["arrays_sha256"]


def test_missing_frozen_files_refuse_worlds(tmp_path):
    if not hspec.missing():
        pytest.skip("frozen: nothing is missing")
    assert hobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "o")]) == 1


# ----------------------------------------------------------------- adjudication

E, Z = "X02", "X01"
ROLES = {"E": E, "Z": Z}


def _x(i, cov, ref, lo, hi, win=28, cutoff=126):
    return {"id": i, "round": 1 if cutoff == 112 else 2, "cutoff": cutoff,
            "request": {"covariates": list(cov), "reference": list(ref), "window_days": win},
            "result": {"skill": (lo + hi) / 2, "lo95": lo, "hi95": hi, "scored_days": [cutoff - win + 1, cutoff]}}


def _judge(exps, statuses, selection, pair_type="E+R", informative=True):
    return adj.adjudicate(exps, statuses, selection, ROLES, pair_type, informative)


def test_freshness_is_structural_and_matches_every_possible_change_day():
    for tau in range(86, 93):
        for cutoff, win in itertools.product((112, 126), (7, 14, 28)):
            x = _x("E1", [E], [], 0.1, 0.2, win=win, cutoff=cutoff)
            assert adj.usable(x) == (x["result"]["scored_days"][0] >= tau and win >= 14)


def test_t1_elimination_supports_e_from_the_pair_and_a_null_partner_increment():
    exps = [_x("E1", [E, Z], [], 0.15, 0.42, win=14, cutoff=112), _x("E2", [Z], [E], -0.06, 0.03, win=14, cutoff=112)]
    out = _judge(exps, {E: "accepted", Z: "rejected"}, [E])
    assert out["claims"][E]["pos_alone"] and out["claims"][E]["alone_by_elimination"] and out["success"]


def test_t2_a_loose_elimination_is_refused():
    exps = [_x("E1", [E, Z], [], 0.02, 0.22), _x("E2", [Z], [E], -0.03, 0.11)]
    out = _judge(exps, {E: "accepted", Z: "redundant"}, [E], "E+D")
    assert not out["claims"][E]["supported"] and not out["success"]


def test_t3_the_governing_result_supersedes_a_shorter_spurious_positive():
    exps = [_x("E1", [Z], [], 0.01, 0.2, win=14, cutoff=112), _x("E2", [E], [], 0.1, 0.3, win=14, cutoff=112),
            _x("E3", [Z], [], -0.04, 0.02), _x("E4", [E], [], 0.12, 0.3)]
    out = _judge(exps, {E: "accepted", Z: "rejected"}, [E], "E+noise")
    assert out["claims"][Z]["supported"] and out["success"] and out["unsupported_rejections"] == []


def test_t4_t5_incoherence_and_completeness():
    exps = [_x("E1", [E], [], 0.1, 0.3), _x("E2", [Z], [E], -0.05, 0.04)]
    assert not _judge(exps, {E: "accepted", Z: "rejected"}, [])["success"]  # accepted but not selected
    assert _judge(exps, {E: "accepted", Z: "rejected"}, [])["incoherent"] == [E]
    thin = _judge([_x("E1", [E], [], 0.1, 0.3)], {E: "accepted", Z: "untested"}, [E], "E+noise")
    assert not thin["criteria"]["2_complete"] and not thin["success"]
    selected_rejected = _judge(exps, {E: "accepted", Z: "rejected"}, [E, Z])
    assert selected_rejected["incoherent"] == [Z] and not selected_rejected["success"]


def test_t6_e_plus_d_rules():
    base = [_x("E1", [E], [], 0.1, 0.3), _x("E2", [Z], [], 0.05, 0.25, win=14, cutoff=112)]
    resolved = base + [_x("E3", [Z], [E], -0.05, 0.04, win=14)]
    ok = _judge(resolved, {E: "accepted", Z: "redundant"}, [E, Z], "E+D")
    assert ok["success"] and ok["selection_supported"]  # D selected as redundant, with its own positive alone result
    assert not _judge(base, {E: "accepted", Z: "promising"}, [E], "E+D")["success"]  # never tested D given E
    joint = _judge(resolved, {E: "accepted", Z: "accepted"}, [E, Z], "E+D")
    assert not joint["success"] and Z in joint["unsupported_acceptances"]  # joint acceptance needs D given E positive
    wrong_way = _judge(resolved, {E: "redundant", Z: "accepted"}, [Z], "E+D")
    assert not wrong_way["success"]
    rejected_proxy = _judge(resolved, {E: "accepted", Z: "rejected"}, [E], "E+D")
    assert not rejected_proxy["success"] and rejected_proxy["unsupported_rejections"] == [Z]  # D alone was positive


def test_t7_a_lower_bound_of_exactly_zero_is_null_and_mixed_or_short_windows_never_count():
    exps = [_x("E1", [E], [], 0.0, 0.2), _x("E2", [Z], [E], -0.1, 0.1)]
    out = _judge(exps, {E: "accepted", Z: "rejected"}, [E])
    assert not out["claims"][E]["pos_alone"] and out["claims"][E]["neg_alone"] and not out["success"]
    mixed = [_x("E1", [E], [], 0.2, 0.4, win=28, cutoff=112), _x("E2", [E], [], 0.2, 0.4, win=7, cutoff=126),
             _x("E3", [Z], [E], -0.1, 0.05)]
    out = _judge(mixed, {E: "accepted", Z: "rejected"}, [E])
    assert not out["claims"][E]["supported"] and not out["success"]


def test_e_plus_noise_and_e_plus_r_distractor_rules():
    exps = [_x("E1", [E], [], 0.1, 0.3), _x("E2", [Z], [], 0.02, 0.2), _x("E3", [Z], [E], 0.01, 0.1)]
    noisy = _judge(exps, {E: "accepted", Z: "accepted"}, [E, Z], "E+noise")
    assert not noisy["criteria"]["4_distractor_treated_correctly"]  # noise never accepted, whatever its evidence
    retired = _judge(exps, {E: "accepted", Z: "promising"}, [E, Z], "E+R")
    assert retired["criteria"]["4_distractor_treated_correctly"]  # R selected with fresh positive evidence of its own
    no_fresh = [_x("E1", [E], [], 0.1, 0.3), _x("E2", [Z], [], 0.02, 0.2, win=28, cutoff=112),
                _x("E3", [E, Z], [], 0.1, 0.3)]
    stale = _judge(no_fresh, {E: "accepted", Z: "promising"}, [E, Z], "E+R")
    assert not stale["criteria"]["4_distractor_treated_correctly"] and not stale["success"]


def test_the_elimination_identity_holds_on_the_lab():
    lab = _lab("99")
    for c, p in (("X01", "X02"), ("X02", "X01")):
        s = lab.run({"covariates": [c, p], "reference": [], "window_days": 28}, 126, "S")["skill"]
        q = lab.run({"covariates": [p], "reference": [c], "window_days": 28}, 126, "Q")["skill"]
        a = lab.run({"covariates": [c], "reference": [], "window_days": 28}, 126, "A")["skill"]
        y = lab.run({"covariates": [p], "reference": [], "window_days": 28}, 126, "Y")["skill"]
        cc = lab.run({"covariates": [c], "reference": [p], "window_days": 28}, 126, "C")["skill"]
        assert abs(a - (1 - (1 - s) / (1 - q))) < 1e-12 and abs(cc - (1 - (1 - s) / (1 - y))) < 1e-12


def test_adjudication_is_a_pure_function_of_the_record():
    exps = [_x("E1", [E], [], 0.1, 0.3), _x("E2", [Z], [E], -0.05, 0.04)]
    snapshot = json.dumps(exps)
    a, b = _judge(exps, {E: "accepted", Z: "redundant"}, [E]), _judge(exps, {E: "accepted", Z: "redundant"}, [E])
    assert a == b and json.dumps(exps) == snapshot
    assert list(inspect.signature(hev.informativeness).parameters) == ["w", "pair", "model"]


# ----------------------------------------------------------------- the comparator

class _ScriptedLab:
    def __init__(self, los):
        self.los, self.calls = list(los), []

    def run(self, req, cutoff, exp_id):
        self.calls.append((cutoff, tuple(req["covariates"]), tuple(req["reference"]), req["window_days"]))
        lo = self.los[len(self.calls) - 1]
        return {"id": exp_id, "skill": lo + 0.05, "lo95": lo, "hi95": lo + 0.1,
                "scored_days": [cutoff - req["window_days"] + 1, cutoff]}


def test_the_comparator_is_the_owners_fixed_sequence():
    lab = _ScriptedLab([0.1, -0.1, 0.05, -0.02])
    rec = comparator.run(lab)
    assert lab.calls == [(112, ("X01",), (), 28), (112, ("X02",), (), 28), (126, ("X01",), ("X02",), 28),
                         (126, ("X02",), ("X01",), 28)]
    assert rec["statuses"] == {"X01": "accepted", "X02": "redundant"} and rec["final_selection"] == ["X01"]
    assert [e["round"] for e in rec["experiments"]] == [1, 1, 2, 2] and comparator.selection_errors(rec) == []
    bad = json.loads(json.dumps(rec))
    bad["final_selection"] = ["X01", "X02"]
    assert comparator.selection_errors(bad)
    bad = json.loads(json.dumps(rec))
    bad["experiments"][2]["request"]["window_days"] = 14
    assert comparator.selection_errors(bad)


@pytest.mark.parametrize("signs", list(itertools.product((0.1, -0.1), repeat=4)))
@pytest.mark.parametrize("pair_type", ["E+D", "E+noise", "E+R"])
def test_the_comparator_never_makes_an_unsupported_claim(signs, pair_type):
    rec = comparator.run(_ScriptedLab(list(signs)))
    roles = {"E": "X01", "Z": "X02"}
    out = adj.adjudicate(rec["experiments"], rec["statuses"], rec["final_selection"], roles, pair_type, True)
    assert out["criteria"]["2_complete"] and out["criteria"]["5_no_unsupported_claim"]
    assert out["unsupported_acceptances"] == [] and out["unsupported_rejections"] == []
    assert out["criteria"]["3_e_supported"] == (signs[2] > 0)  # E accepted exactly when E given its partner is positive


def test_the_comparator_is_deterministic_on_the_lab():
    assert comparator.run(_lab("77")) == comparator.run(_lab("77"))


# ----------------------------------------------------------------- the programme reading

def _worlds(*rows):
    return {f"w{i + 1}": {"informative": inf, "L2": {"success": l2, "experiments_used": n},
                          "comparator": {"success": c, "experiments_used": 4}}
            for i, (inf, l2, c, n) in enumerate(rows)}


@pytest.mark.parametrize("rows, label, row, line", [
    (((True, True, True, 4),) * 3, "SCRIPTABLE NARROW KERNEL", "row 4", "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW"),
    (((True, True, True, 3),) * 3, "AGENTIC VALUE SIGNAL", "row 5", "AUTONOMOUS RESEARCH KERNEL SURVIVES"),
    (((True, True, True, 4), (True, True, False, 4), (True, True, True, 4)), "AGENTIC VALUE SIGNAL", "row 5",
     "AUTONOMOUS RESEARCH KERNEL SURVIVES"),
    (((True, True, True, 4), (True, True, True, 4), (False, False, True, 4)), "SCRIPTABLE NARROW KERNEL", "row 4",
     "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW"),
    (((True, True, True, 3), (True, True, True, 3), (False, False, False, 1)), "AGENTIC VALUE SIGNAL", "row 5",
     "AUTONOMOUS RESEARCH KERNEL SURVIVES"),
    (((True, False, True, 4), (True, False, True, 4), (True, True, True, 4)), "NARROW RESEARCHER FAILURE", "row 3",
     "STOP THIS RESEARCHER LINE"),
    (((True, False, False, 4), (True, False, False, 4), (False, True, True, 4)), "NARROW RESEARCHER FAILURE", "row 3",
     "STOP THIS RESEARCHER LINE"),
    (((True, False, True, 4), (True, True, True, 4), (True, True, True, 4)), "MIXED", "row 6",
     "STOP THIS RESEARCHER LINE"),
    (((True, False, False, 4), (True, True, True, 4), (True, True, True, 4)), "MIXED", "row 6",
     "USE A SCRIPT / HUMAN-DRIVEN WORKFLOW"),
    (((True, False, True, 4), (True, True, True, 3), (False, False, False, 4)), "MIXED", "row 6",
     "STOP THIS RESEARCHER LINE"),
    (((True, True, True, 4), (False, False, False, 4), (False, False, False, 4)), "BENCHMARK FAILURE", "row 2",
     "BENCHMARK/INFRASTRUCTURE RESULT ONLY"),
])
def test_every_programme_row_and_its_closing_line(rows, label, row, line):
    worlds = _worlds(*rows)
    got = hev.programme([], [], worlds)
    assert got[0] == label and got[1].startswith(row)
    assert hev.closing_line(label, worlds) == line and line in hev.LINES


def test_infrastructure_failure_comes_first():
    good = _worlds(*((True, True, True, 3),) * 3)
    assert hev.programme(["w2: guard"], [], good)[0] == "INFRASTRUCTURE FAILURE"
    assert hev.programme([], ["w1: L2 call 3: never made"], good)[0] == "INFRASTRUCTURE FAILURE"
    assert hev.closing_line("INFRASTRUCTURE FAILURE", good) == "BENCHMARK/INFRASTRUCTURE RESULT ONLY"
    assert hev.call_failures2({"calls": []}) == ["call 1: never made", "call 2: never made", "call 3: never made"]


# ----------------------------------------------------------------- the preflight

def test_the_preflight_checks_l2_and_the_comparator(tmp_path, pinned, unfrozen_ok):
    d = tmp_path / "r" / "w1"
    d.mkdir(parents=True)
    lab = _lab()
    (d / "ai.json").write_text(json.dumps(hres.Researcher2(_Client(_replies()), TEST_MODEL, lab).run()))
    (d / "integrity.json").write_text('{"failure": null}')
    (d / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    (d / "comparator.json").write_text(json.dumps(comparator.run(lab)))
    (tmp_path / "obs" / "w1").mkdir(parents=True)
    (tmp_path / "obs" / "w1" / "observed.json").write_text("{}")
    args = ["--research", str(tmp_path / "r"), "--observed", str(tmp_path / "obs"), "--out", str(tmp_path / "out")]
    assert hpre.main(args) == 0
    v = json.loads((tmp_path / "out" / "verdict.json").read_text())
    assert v["verdict"] == "PASS" and v["phase"] == "human1-preflight" and v["spec_sha"] == hspec.spec_sha()
    rec = json.loads((tmp_path / "out" / "preflight.json").read_text())["w1"]
    assert rec["calls"] == 3 and rec["experiments"] == 4 and rec["enumeration_ok"] and rec["illegal_experiments"] == 0

    def verdict_after(name, change):
        good = (d / name).read_text()
        obj = json.loads(good)
        change(obj)
        (d / name).write_text(json.dumps(obj))
        hpre.main(args)
        (d / name).write_text(good)
        return json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"]
    assert verdict_after("ai.json", lambda a: a["calls"][1].update(user_prompt=a["calls"][1]["user_prompt"] + "x")) \
        == "FAIL"
    assert verdict_after("ai.json", lambda a: a.update(system_text=lres.system_text("L"))) == "FAIL"
    assert verdict_after("ai.json", lambda a: a.update(calls=a["calls"][:2])) == "FAIL"
    assert verdict_after("comparator.json", lambda c: c.update(final_selection=[] if c["final_selection"] else ["X01"])) \
        == "FAIL"
    assert verdict_after("guard.json", lambda g: g.update(truth_absent=False)) == "FAIL"
    assert hpre.main(args) == 0 and json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"] == "PASS"


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
    from research_loop_proof.human1.lab import run as hrun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (_FakeBetaModel(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_replies()))

    def research(obs_dir, out_dir, worlds):
        for k in worlds:
            meta = json.loads((obs_dir / k / "observed.json").read_text())
            common = ["--observed", str(obs_dir / k / "observed.npz"), "--observed-sha", meta["arrays_sha256"],
                      "--weights", "unused", "--out", str(out_dir / k)]
            assert hrun.main(["comparator", *common]) == 0
            assert hrun.main(["loop", *common]) == 0
            (out_dir / k / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    assert hobs.main(["--mode", "preflight", "--run-id", "11", "--out", str(tmp_path / "pobs")]) == 0
    research(tmp_path / "pobs", tmp_path / "pres", ["w1"])
    assert hpre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    assert json.loads(body)["verdict"] == "PASS"
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    assert hobs.main(["--mode", "run", "--run-id", "12", "--preflight-dir", str(tmp_path / "pout"),
                      "--out", str(tmp_path / "obs")]) == 0
    research(tmp_path / "obs", tmp_path / "res", hobs.SCORED_WORLDS)
    out = tmp_path / "out"
    assert hev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
                     "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity_issues"] == [] and rec["call_failures"] == []
    for k in hobs.SCORED_WORLDS:
        r = rec["worlds"][k]
        assert r["integrity"]["experiments_recomputed"] == 4 and r["integrity"]["comparator_recomputed"] == 4
        assert r["pair_type"] == hworld.PAIR_TYPE[hworld.PAIRS[k]] and set(r["truth"]["roles"]) == set(hworld.PAIRS[k])
        assert r["L2"]["experiments_used"] == 4 and r["L2"]["elapsed_s"] is not None
    assert rec["reading"] in ("INFRASTRUCTURE FAILURE", "BENCHMARK FAILURE", "NARROW RESEARCHER FAILURE",
                              "SCRIPTABLE NARROW KERNEL", "AGENTIC VALUE SIGNAL", "MIXED")
    assert rec["closing_line"] in hev.LINES
    report = (out / "REPORT.md").read_text()
    assert report.startswith(f"# Human1 three-world result: {rec['reading']}") and TEST_MODEL not in report
    swap = tmp_path / "swap"
    for k, src in (("w1", "w2"), ("w2", "w1"), ("w3", "w3")):
        (swap / k).mkdir(parents=True)
        for f in (tmp_path / "res" / src).iterdir():
            (swap / k / f.name).write_bytes(f.read_bytes())
    hev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(swap), "--weights", "unused",
              "--out", str(tmp_path / "out2")])
    assert json.loads((tmp_path / "out2" / "evaluation.json").read_text())["reading"] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")
TRUTH_DIRS = tuple(f"research_loop_proof/{p}/truth" for p in ("phase0", "beta1", "learn1", "policy1", "discovery1",
                                                                "human1"))


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_the_human1_workflow_is_manual_scoped_and_isolated(wf):
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
        assert len(steps) == 1 and f"human1.lab.run loop --observed obs/{k}/observed.npz " in steps[0]["run"]
        assert steps[0]["env"]["HF_HUB_OFFLINE"] == "1"
        assert [key for key, v in steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        comp = [st for st in job["steps"] if "human1.lab.run comparator" in st.get("run", "")]
        assert len(comp) == 1 and "secrets." not in json.dumps(comp[0])
        patterns = job["steps"][0]["with"]["sparse-checkout"]
        for d in TRUTH_DIRS:
            assert f"!/{d}/" in patterns, (k, d)
        assert "!/tests/" in patterns
        guard = job["steps"][1]["run"]
        assert "rm -rf .git" in guard and all(d in guard for d in TRUTH_DIRS)
    assert jobs["research_w1"]["if"] == "inputs.mode == 'preflight' || inputs.mode == 'run'"
    assert jobs["research_w2"]["if"] == jobs["research_w3"]["if"] == "inputs.mode == 'run'"
    assert jobs["check"]["needs"] == ["observe", "research_w1"]
    assert jobs["evaluate"]["needs"] == ["observe", "research_w1", "research_w2", "research_w3"]
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "human1/run-${{ github.run_id }}" in pub
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text and "HF_TOKEN" not in text and "discovery1.lab" not in text


def test_the_three_research_jobs_are_identical_except_for_the_world(wf):
    j = {k: json.dumps({n: v for n, v in wf["jobs"][f"research_{k}"].items() if n != "if"}, sort_keys=True)
         for k in ("w1", "w2", "w3")}
    assert j["w1"] != j["w2"] and j["w1"].replace("w1", "w2") == j["w2"] and j["w1"].replace("w1", "w3") == j["w3"]


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    import re

    pattern = re.compile(r"^def make_world", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]
    kept = [f for f in set(files) if not f.startswith(tuple(d + "/" for d in TRUTH_DIRS) + ("tests/",))]
    assert kept and not [f for f in kept if pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

FROZEN_SHA256 = {
    "docs/research_loop_proof/HUMAN1_SPEC.md":
        "f346b15cb3703d50e064f452236f2ded71d79da6746bedb0233611e48b23ec0b",
    "research_loop_proof/human1/lab/executor.py":
        "97d813f51b967f3ff81f344e73d8577da395aa5c4c653f1b4ad89f0124367f34",
    "research_loop_proof/human1/lab/researcher.py":
        "52ceae0ae771a405d2dbe6c6d77aa8352c909ff154b40d123925e4ebf0cac981",
    "research_loop_proof/human1/lab/comparator.py":
        "bdbcb7acf45eed7792a6829a39cf1a64a8878ee7613c1367c8f3d0fa4954a222",
    "research_loop_proof/human1/lab/run.py":
        "56f213264bc7076e4dd347ffab21bc1fc272b09e99eb9e5292f76ef28240891a",
    "research_loop_proof/human1/truth/world.py":
        "808eafac0c8c665dd7982e772a1fde538b1cc85d53453636e3fc86bb01209cae",
    "research_loop_proof/human1/truth/observe.py":
        "d80c886e339484c3e3c24adc37e65c85c7ed98f1866d085c37e3c47101c25720",
    "research_loop_proof/human1/truth/adjudicate.py":
        "a18bca914ddc876ea82918e8ba75c8faa92518de1e153346d9c5484d8364130b",
    "research_loop_proof/human1/truth/evaluate.py":
        "07910df7ccc65ae0b60cbb4924dc7d4f77e329a6cb36ca523fa61ccf3f8b2206",
    "docs/research_loop_proof/DISCOVERY1_SPEC.md":
        "e6d31d0933aed645e5b075ead878f2c40fa787f7da33b636720cdf55c92be61a",
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
        "3a994c9d984b92e7541ba410ef360638af1329acbb0d72d0b6d32e1d0e3fc6ad",
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
SPEC_SHA = "a192ab346f54c580cc792188058ad996080f4cf5cc67cb4145f9d4e56b29e709"


def test_the_human1_files_are_frozen():
    assert hspec.missing() == []
    assert hspec.file_hashes() == FROZEN_SHA256
    assert hspec.spec_sha() == SPEC_SHA
