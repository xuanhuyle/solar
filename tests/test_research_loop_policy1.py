"""policy1 (docs/research_loop_proof/NEXT_POLICY_ARCHITECTURE_PROMPT.md): the structured research-state interface,
the lesson-only comparator, the replays, the paired evaluation and the workflow. Parts that need torch or anthropic skip
without them."""

from __future__ import annotations

import ast
import copy
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
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.learn1.truth import observe as lobs
from research_loop_proof.phase0.lab import executor
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen
from research_loop_proof.policy1.lab import researcher as pres
from research_loop_proof.policy1.truth import evaluate as pev
from research_loop_proof.policy1.truth import observe as pobs
from research_loop_proof.policy1.truth import preflight as ppre
from research_loop_proof.policy1.truth import replay as prep
from research_loop_proof.policy1.truth import spec as pspec

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "policy1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-policy1.yml"
TEST_MODEL = "test-model-id"


def _git_show(ref_path: str) -> bytes | None:
    r = subprocess.run(["git", "show", ref_path], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


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


def _rows(status="untested", cites=None, overrides=None, structured=True):
    rows = {i: {"candidate": i, "status": status, "cites": list(cites or []), "reason": "r"} for i in executor.IDS}
    if structured:
        for r in rows.values():
            r.update(freshness="unknown", evidence_type="none", last_scored_day=0, attribution="")
    for i, row in (overrides or {}).items():
        rows[i].update(row)
    return [rows[i] for i in executor.IDS]


def _exp(cov, ref=(), win=28, structured=True, target="U1"):
    e = {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves", "because": "b"}
    if structured:
        e.update(targets_uncertainty=target, possible_followup="split if positive", budget_rationale="needed now")
    return e


def _reply(rows, exps=(), final=None, conclusion="", structured=True, uncertainties=None, regime="unknown", cites=()):
    r = {"notes": "n", "beliefs": rows, "experiments": list(exps), "final_selection": list(final or []),
         "conclusion": conclusion}
    if structured:
        r.update(regime_assessment={"status": regime, "cites": list(cites), "justification": "j"},
                 decision_uncertainties=[{"id": "U1", "uncertainty": "which candidate helps now",
                                          "why_it_matters": "it decides the selection"}]
                 if uncertainties is None else uncertainties, budget_needs="resolve U1")
    return r


def _replies(structured=True):
    s = structured
    return [_resp(_reply(_rows(structured=s), [_exp(["X01"], structured=s), _exp(["X02"], structured=s)],
                         structured=s)),
            _resp(_reply(_rows("promising", ["E1"], structured=s),
                         [_exp(["X03"], win=14, structured=s), _exp(["X04"], win=14, structured=s)], structured=s,
                         cites=["E1"])),
            _resp(_reply(_rows("promising", ["E3"], structured=s),
                         [_exp(["X01"], win=14, structured=s), _exp(["X02"], ["X01"], win=14, structured=s)],
                         structured=s, regime="possible_change", cites=["E3"])),
            _resp(_reply(_rows("accepted", ["E5"], {"X02": {"status": "rejected", "cites": ["E6"]}}, structured=s),
                         final=["X01"], conclusion="X01 helps.", structured=s, uncertainties=[] if s else None))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def unfrozen_ok(monkeypatch):
    """Before the freeze the spec file is missing; tests that generate worlds treat the files as present."""
    monkeypatch.setattr(pspec, "missing", lambda root=None: [])


def _lab(world_id="4242"):
    return executor.Lab(gen.observed_arrays(bobs.preflight_world(world_id), 126), _Inst())


# ----------------------------------------------------------------- separation and the two conditions

def test_the_policy1_lab_never_imports_a_truth_package():
    for path in (PKG / "lab").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


def test_l_is_learn1s_lesson_condition_and_s_adds_only_the_research_state():
    l, s = pres.system_text("L"), pres.system_text("S")
    assert l == lres.system_text("L")
    head = "\n\nRESPONSE SCHEMA (JSON)\n"
    l_pre, l_schema = l.split(head)
    s_pre, s_schema = s.split(head)
    assert s_pre == l_pre + "\n\n" + pres.STATE_SECTION.rstrip("\n")
    assert json.loads(l_schema) == p0res.response_schema() and json.loads(s_schema) == pres.response_schema_s()
    assert lres.frozen_lesson() in s and "reasoning" not in s.lower()
    base = p0res.response_schema()
    ss = pres.response_schema_s()
    assert set(ss["properties"]) == set(base["properties"]) | {"regime_assessment", "decision_uncertainties",
                                                               "budget_needs"}
    row = ss["properties"]["beliefs"]["items"]
    assert set(row["properties"]) - set(base["properties"]["beliefs"]["items"]["properties"]) == {
        "freshness", "evidence_type", "last_scored_day", "attribution"}
    exp = ss["properties"]["experiments"]["items"]
    assert set(exp["properties"]) - set(base["properties"]["experiments"]["items"]["properties"]) == {
        "targets_uncertainty", "possible_followup", "budget_rationale"}
    for words in ("re-test", "retest", "reserve", "split", "must test", "always"):
        assert words not in pres.STATE_SECTION.lower()  # no policy is written into the interface
    with pytest.raises(ValueError):
        pres.system_text("F")


def test_the_s_checks_cover_the_research_state():
    step = pres.call_plan()[0]
    good = _reply(_rows(), [_exp(["X01"])])
    assert pres.response_errors_s(good, step, []) == []

    def broken(f):
        obj = copy.deepcopy(good)
        f(obj)
        return pres.response_errors_s(obj, step, [])
    assert broken(lambda o: o.pop("budget_needs"))
    assert broken(lambda o: o["regime_assessment"].update(status="shifting"))
    assert broken(lambda o: o["regime_assessment"].update(cites=["E9"]))
    assert broken(lambda o: o.update(decision_uncertainties=o["decision_uncertainties"] * 4))
    assert broken(lambda o: o["beliefs"][0].update(freshness="old"))
    assert broken(lambda o: o["beliefs"][0].update(last_scored_day=200))
    assert broken(lambda o: o["beliefs"][0].update(last_scored_day=True))
    assert broken(lambda o: o["beliefs"][0].pop("attribution"))
    assert broken(lambda o: o["experiments"][0].update(targets_uncertainty="U2"))  # not in this call's list
    assert broken(lambda o: o["experiments"][0].update(budget_rationale="x" * 301))
    assert broken(lambda o: o["experiments"][0].pop("possible_followup"))
    assert broken(lambda o: o.update(experiments=[_exp(["X01"]), _exp(["X02"]), _exp(["X03"]), _exp(["X04"])]))


def test_both_conditions_run_with_one_repair_and_prompts_rebuild(pinned):
    recs = {}
    for c, structured in (("L", False), ("S", True)):
        replies = _replies(structured)
        if c == "S":
            bad = json.loads(replies[0].content[0].text)
            bad["experiments"][0]["targets_uncertainty"] = "U3"
            replies = [_resp(bad)] + replies
        client = _Client(replies)
        r = pres.researcher_for(c, client, TEST_MODEL, _lab())
        recs[c] = r.run()
        assert recs[c]["condition"] == c and recs[c]["final_valid"]
        assert all(s["system"][0]["text"] == pres.system_text(c) for s in client.sent)
        schema = client.sent[0]["output_config"]["format"]["schema"]
        assert schema == (pres.response_schema_s() if c == "S" else p0res.response_schema())
        assert pres.rebuild_for(c)(recs[c]["calls"]) == []
    s_first = recs["S"]["calls"][0]
    assert len(s_first["attempts"]) == 2 and "targets_uncertainty" in s_first["attempts"][1]["repair_prompt"]
    assert "Regime assessment: possible_change" in recs["S"]["calls"][3]["user_prompt"]
    assert "freshness: unknown" in recs["S"]["calls"][1]["user_prompt"] and "targets: U1" in recs["S"]["calls"][1][
        "user_prompt"]
    assert "Regime assessment" not in recs["L"]["calls"][3]["user_prompt"]
    tampered = copy.deepcopy(recs["S"]["calls"])
    tampered[2]["user_prompt"] += " extra"
    assert pres.rebuild_mismatches_s(tampered) == ["call 3: user prompt"]
    assert TEST_MODEL not in json.dumps(recs)


# ----------------------------------------------------------------- the replays

BETA1_PREFIX = [[{"covariates": ["X01"], "reference": [], "window_days": 28},
                 {"covariates": ["X02"], "reference": [], "window_days": 28},
                 {"covariates": ["X03"], "reference": [], "window_days": 28}],
                [{"covariates": ["X04"], "reference": [], "window_days": 28},
                 {"covariates": ["X03"], "reference": [], "window_days": 28}]]


def test_a_replay_shows_recorded_evidence_then_lets_s_decide(pinned, tmp_path):
    late = [_replies()[2], _replies()[3]]
    one_left = json.loads(late[0].content[0].text)
    one_left["experiments"] = one_left["experiments"][:1]
    one_left["experiments"][0]["covariates"] = ["X01", "X02"]
    client = _Client([_resp(one_left), late[1]])
    lab = _lab()
    rec = pres.StructuredResearcher(client, TEST_MODEL, lab).run_replay(BETA1_PREFIX)
    calls = rec["calls"]
    assert [c.get("replayed", False) for c in calls] == [True, True, False, False]
    assert [e["id"] for c in calls for e in c["experiments"]] == ["E1", "E2", "E3", "E4", "E5", "E6"]
    assert "replayed: evidence from an earlier investigation" in calls[2]["user_prompt"]
    assert "Experiment budget: 1 of 6 left" in calls[2]["user_prompt"] and rec["final_valid"]
    assert pres.rebuild_mismatches_s(calls) == []
    original = {"calls": [{"experiments": [{"result": e["result"]} for e in c["experiments"]]} for c in calls[:2]]}
    d = tmp_path / "beta1"
    d.mkdir()
    (d / "ai.json").write_text(json.dumps(rec))
    (d / "integrity.json").write_text('{"failure": null}')
    assert prep.check_replay(d, original)["operational"] == "PASS"
    original["calls"][0]["experiments"][0]["result"] = dict(original["calls"][0]["experiments"][0]["result"],
                                                            skill=0.99)
    assert prep.check_replay(d, original)["replayed_results_match_published"] is False


def test_the_replay_export_uses_the_pinned_published_worlds_and_records(tmp_path):
    for name, r in pobs.REPLAYS.items():
        obs = gen.observed_arrays(r["world"](r["run"]), 126)
        assert gen.arrays_sha256(obs) == r["observed_sha256"], name
    pub = tmp_path / "published"
    for name, r in pobs.REPLAYS.items():
        body = _git_show(f"origin/{r['branch']}:{r['record']}")
        manifest = _git_show(f"origin/{r['branch']}:MANIFEST.sha256")
        if body is None or manifest is None:
            pytest.skip("the result branches are not fetched here")
        (pub / name).mkdir(parents=True)
        (pub / name / "record.json").write_bytes(body)
        (pub / name / "MANIFEST.sha256").write_bytes(manifest)
    assert pobs.main(["--mode", "replay", "--published", str(pub), "--out", str(tmp_path / "obs")]) == 0
    b = json.loads((tmp_path / "obs" / "beta1" / "prefix.json").read_text())["prefix"]
    assert b == BETA1_PREFIX
    l1 = json.loads((tmp_path / "obs" / "learn1" / "prefix.json").read_text())["prefix"]
    assert l1[1][1]["covariates"] == ["X01", "X02", "X03"] and set(l1[1][1]) == {"covariates", "reference",
                                                                              "window_days"}
    meta = json.loads((tmp_path / "obs" / "learn1" / "observed.json").read_text())
    assert meta["arrays_sha256"] == pobs.REPLAYS["learn1"]["observed_sha256"] and "spec_sha" not in meta
    (pub / "beta1" / "record.json").write_bytes(body + b" ")
    with pytest.raises(ValueError):
        pobs.published_record(pub / "beta1", "beta1")


# ----------------------------------------------------------------- indicators and outcome

def _roles():
    w = pobs.preflight_world("31")
    return {k: w.ids[k] for k in ("R", "E", "D", "N")}, w.tau


def _res(i, cov, lo, scored, ref=()):
    return {"id": f"E{i}", "request": _exp(cov, ref, structured=False),
            "result": {"id": f"E{i}", "covariates": list(cov), "reference": list(ref), "skill": lo + 0.05, "lo95": lo,
                       "hi95": lo + 0.1, "scored_days": list(scored)}}


def _call(n, rnd, cutoff, rows, exps=(), final=None):
    return {"call": n, "round": rnd, "cutoff": cutoff, "final": rnd is None, "valid": True, "attempts": [],
            "errors": [], "response": _reply(rows, [e["request"] for e in exps], final, "c" if rnd is None else "",
                                             structured=False), "experiments": list(exps)}


def _trajectory(roles, last, final):
    """Rounds 1-2 as in learn1 L (singles, then the three rejected re-screened jointly), round 3 given, final given."""
    r, e, d, n = roles["R"], roles["E"], roles["D"], roles["N"]
    return [_call(1, 1, 84, _rows(structured=False), [_res(1, [e], -0.05, (57, 84)), _res(2, [n], -0.04, (57, 84)),
                                                      _res(3, [d], -0.06, (57, 84))]),
            _call(2, 2, 112, _rows("rejected", ["E1"], structured=False),
                  [_res(4, [r], 0.0, (85, 112)), _res(5, [e, n, d], 0.15, (85, 112))]),
            _call(3, 3, 126, _rows("promising", ["E5"], structured=False), last),
            _call(4, None, 126, _rows("promising", ["E5"], structured=False), final=final)]


def _analysed(calls, roles, tau, cond, confirm_lo=0.2):
    ai = {"calls": calls, "final_valid": True, "final_selection": calls[-1]["response"]["final_selection"]}
    ev = {"E_days_99_126": {"lo95": 0.2}, "R_days_57_84": {"lo95": 0.1}, "E_days_99_112": {"lo95": 0.1}}
    sel = {"t0": {"lo95": confirm_lo}} if ai["final_selection"] else None
    return pev.analyse(cond, ai, roles, tau, ev, [], sel)


def test_support_reconfirmation_and_last_experiment():
    roles, tau = _roles()
    e, n, d = roles["E"], roles["N"], roles["D"]
    lesson_like = _analysed(_trajectory(roles, [_res(6, [n, e], 0.2, (99, 126), ref=[d])], [e, n, d]), roles, tau, "L")
    assert not lesson_like["found"] and not lesson_like["supported"]
    assert set(lesson_like["unsupported_members"]) == {e, n, d}
    assert lesson_like["last_experiment"]["type"] == "group-conditional"
    resolving = _analysed(_trajectory(roles, [_res(6, [e], 0.2, (99, 126), ref=[d, n])], [e]), roles, tau, "S")
    assert resolving["found"] and resolving["supported"] and resolving["essential_loop"]
    assert resolving["support"][e]["reference"] == sorted([d, n]) or resolving["support"][e]["supported"]
    assert resolving["last_experiment"]["tests_a_selected_member_alone"]
    again = _analysed(_trajectory(roles, [_res(6, [roles["R"]], 0.0, (99, 126))], []), roles, tau, "S")
    assert again["reconfirmations"] == ["E6"]  # R alone again after its post-change sole test E4
    assert again["essential_loop"] is False and again["supported"] is False


def test_the_outcome_rows():
    roles, tau = _roles()
    e, n, d = roles["E"], roles["N"], roles["D"]
    group = _analysed(_trajectory(roles, [_res(6, [n, e], 0.2, (99, 126), ref=[d])], [e, n, d]), roles, tau, "L")
    solo = _analysed(_trajectory(roles, [_res(6, [e], 0.2, (99, 126))], [e]), roles, tau, "S")
    with_d = _analysed(_trajectory(roles, [_res(6, [e], 0.2, (99, 126))], [e, d]), roles, tau, "L")
    nothing = _analysed(_trajectory(roles, [_res(6, [roles["R"]], 0.0, (99, 126))], []), roles, tau, "S")
    assert pev.outcome([], group, solo)[0] == "ARCHITECTURE SIGNAL OBSERVED"       # (a)
    label, rule = pev.outcome([], with_d, solo)                                    # (b): D unsupported in L
    assert with_d["found"] and not with_d["supported"] and label == "ARCHITECTURE SIGNAL OBSERVED" and "(b)" in rule
    assert pev.outcome([], solo, dict(solo, condition="S"))[0] == "BOTH SUCCEED"
    assert pev.outcome([], group, nothing)[0] == "BOTH FAIL"
    assert pev.outcome([], solo, group)[0] == "NO ARCHITECTURE SIGNAL"
    broken = dict(solo, call_failures=["call 2: no valid response after its repair (refusal)"])
    assert pev.outcome([], group, broken)[0] == "INFRASTRUCTURE FAILURE"
    assert pev.outcome(["S: guard"], group, solo)[0] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the world and the gates

def test_the_world_is_new_and_gated(tmp_path, unfrozen_ok):
    a, b = pobs.hidden_world("777"), pobs.preflight_world("777")
    assert a.seed == gen.seed_of(f"policy1:{pspec.spec_sha()}:777") and 86 <= a.tau <= 92 and a.n_days == 154
    for other in (b, bobs.hidden_world("777"), lobs.hidden_world("777")):
        assert not np.array_equal(a.y, other.y)
    assert pobs.refusals("preflight", None) == [] and pobs.refusals("run", str(tmp_path / "none"))

    def write(verdict, sha, phase="policy1-preflight"):
        body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", pspec.spec_sha())
    assert pobs.refusals("run", str(tmp_path)) == []
    for args in (("FAIL", pspec.spec_sha()), ("PASS", "0" * 64), ("PASS", pspec.spec_sha(), "learn1-preflight")):
        write(*args)
        assert pobs.published_errors(tmp_path, "policy1-preflight")


def test_missing_frozen_files_refuse_worlds(tmp_path):
    if not pspec.missing():
        pytest.skip("frozen: nothing is missing")
    assert pobs.main(["--mode", "preflight", "--run-id", "5", "--out", str(tmp_path / "o")]) == 1


def test_the_preflight_needs_both_conditions(tmp_path, pinned, unfrozen_ok):
    for c, structured in (("L", False), ("S", True)):
        d = tmp_path / "r" / c
        d.mkdir(parents=True)
        rec = pres.researcher_for(c, _Client(_replies(structured)), TEST_MODEL, _lab()).run()
        (d / "ai.json").write_text(json.dumps(rec))
        (d / "integrity.json").write_text('{"failure": null}')
    (tmp_path / "obs").mkdir()
    (tmp_path / "obs" / "observed.json").write_text("{}")
    args = ["--research", str(tmp_path / "r"), "--observed", str(tmp_path / "obs"), "--out", str(tmp_path / "out")]
    assert ppre.main(args) == 0
    v = json.loads((tmp_path / "out" / "verdict.json").read_text())
    assert v["verdict"] == "PASS" and v["phase"] == "policy1-preflight" and v["spec_sha"] == pspec.spec_sha()
    ai = json.loads((tmp_path / "r" / "S" / "ai.json").read_text())
    ai["calls"][1]["user_prompt"] += "x"
    (tmp_path / "r" / "S" / "ai.json").write_text(json.dumps(ai))
    assert ppre.main(args) == 0 and json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"] == "FAIL"


# ----------------------------------------------------------------- end to end with stand-ins

class _FakeBetaModel:
    def predict(self, ctx, horizon, quantile_levels, future_covariates=None):
        med = ctx[:, -24:].clone()
        if future_covariates is not None:
            med = med + 0.3 * future_covariates[:, :, -24:].sum(1)
        return SimpleNamespace(median=med)


def test_preflight_and_scored_paired_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned, unfrozen_ok):
    pytest.importorskip("torch")
    anthropic = pytest.importorskip("anthropic")
    from research_loop_proof.beta1.lab import run as brun
    from research_loop_proof.policy1.lab import run as prun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (_FakeBetaModel(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    clients = {"L": lambda: _Client(_replies(False)), "S": lambda: _Client(_replies(True))}

    def research(obs_dir, out_dir):
        meta = json.loads((obs_dir / "observed.json").read_text())
        for c in pres.CONDITIONS:
            monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: clients[c]())
            assert prun.main(["loop", "--condition", c, "--observed", str(obs_dir / "observed.npz"), "--observed-sha",
                              meta["arrays_sha256"], "--weights", "unused", "--out", str(out_dir / c)]) == 0
            (out_dir / c / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    assert pobs.main(["--mode", "preflight", "--run-id", "11", "--out", str(tmp_path / "pobs")]) == 0
    research(tmp_path / "pobs", tmp_path / "pres")
    assert ppre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    assert json.loads(body)["verdict"] == "PASS"
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    assert pobs.main(["--mode", "run", "--run-id", "12", "--preflight-dir", str(tmp_path / "pout"),
                      "--out", str(tmp_path / "obs")]) == 0
    research(tmp_path / "obs", tmp_path / "res")
    out = tmp_path / "out"
    assert pev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
                     "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity"]["issues"] == [] and rec["integrity"]["S"]["experiments_recomputed"] == 6
    assert rec["outcome"] in ("NO ARCHITECTURE SIGNAL", "BOTH SUCCEED", "BOTH FAIL")  # same choices: no difference
    s_state = rec["conditions"]["S"]["structured_state"]
    assert len(s_state) == 4 and s_state[2]["regime_assessment"]["status"] == "possible_change"
    assert rec["conditions"]["L"]["structured_state"] == [] and rec["conditions"]["S"]["final_uncertainties"] == []
    report = (out / "REPORT.md").read_text()
    assert report.startswith(f"# policy1 paired hidden-world result: {rec['outcome']}") and "Regime assessment" in report
    assert (out / "L" / "ai.json").is_file() and (out / "S" / "ai.json").is_file() and TEST_MODEL not in report
    swap = tmp_path / "swap"
    for c, src in (("L", "S"), ("S", "L")):
        (swap / c).mkdir(parents=True)
        for f in (tmp_path / "res" / src).iterdir():
            (swap / c / f.name).write_bytes(f.read_bytes())
    pev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(swap), "--weights", "unused",
              "--out", str(tmp_path / "out2")])
    assert json.loads((tmp_path / "out2" / "evaluation.json").read_text())["outcome"] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_the_policy1_workflow_is_manual_scoped_and_isolated(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["replay", "preflight", "run"]
    jobs = wf["jobs"]
    assert set(jobs) == {"replay_observe", "replay_research", "replay_check", "observe", "research_l", "research_s",
                         "check", "evaluate", "publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    for name in ("replay_observe", "replay_check", "observe", "check", "evaluate", "publish"):
        assert _secret_steps(jobs[name]) == [], name
    for name, marker in (("replay_research", " replay "), ("research_l", " loop --condition L "),
                         ("research_s", " loop --condition S ")):
        steps = _secret_steps(jobs[name])
        assert len(steps) == 1 and marker in steps[0]["run"] and steps[0]["env"]["HF_HUB_OFFLINE"] == "1", name
        assert [k for k, v in steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        patterns = jobs[name]["steps"][0]["with"]["sparse-checkout"]
        for d in ("!/research_loop_proof/phase0/truth/", "!/research_loop_proof/beta1/truth/",
                  "!/research_loop_proof/learn1/truth/", "!/research_loop_proof/policy1/truth/", "!/tests/"):
            assert d in patterns, name
        guard = jobs[name]["steps"][1]
        assert "rm -rf .git" in guard["run"] and "research_loop_proof/policy1/truth" in guard["run"]
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "policy1/run-${{ github.run_id }}" in pub
    assert "needs.replay_check.outputs.manifest_sha256 || needs.check.outputs.manifest_sha256 || " \
           "needs.evaluate.outputs.manifest_sha256" in pub
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text and "HF_TOKEN" not in text


def test_the_two_research_jobs_are_identical_except_for_the_condition(wf):
    l = json.dumps(wf["jobs"]["research_l"], sort_keys=True)
    s = json.dumps(wf["jobs"]["research_s"], sort_keys=True)
    assert l != s and l.replace("condition L", "condition S").replace("research-L-", "research-S-") == s


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    import re

    pattern = re.compile(r"^def make_world\(", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]
    kept = [f for f in set(files) if not f.startswith(("research_loop_proof/phase0/truth/", "research_loop_proof/beta1/truth/",
                                                       "research_loop_proof/learn1/truth/",
                                                       "research_loop_proof/policy1/truth/", "tests/"))]
    assert kept and not [f for f in kept if pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

FROZEN_SHA256 = {
    "docs/research_loop_proof/POLICY1_SPEC.md":
        "864948793a402d5f97d019633b18c85f56d9f3cc0740fd921831d9d427443ffa",
    "docs/research_loop_proof/POLICY1_ARCHITECTURE.md":
        "3c95b22934d4a09f7dec3b40d5fa7a296460f6449383c7cb63ace3ffa2b54192",
    "research_loop_proof/policy1/lab/researcher.py":
        "48d01bdf55830518a84ca3bb311ad536e1c26f330ffbcbdaab298968cf9ab6b9",
    "research_loop_proof/policy1/lab/run.py":
        "221d3df9b193d6943e07340bfb97bd6e6dcb10a90af5e815fd96abc885561995",
    "research_loop_proof/policy1/truth/observe.py":
        "c04b4d795ee3f9a875500599446024364c6252ce5ecf8a45a56e179a66d9b2b2",
    "research_loop_proof/policy1/truth/evaluate.py":
        "f92a408a31c311eaec75072c9bb1eb5da32eb6309f1aa1deab5860ee340a2ad6",
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
SPEC_SHA = "0d1b03766f9af4bb93d859bdcccf68e3be603382151c3183719058d3aa961502"


def test_the_policy1_files_are_frozen():
    assert pspec.missing() == []
    assert pspec.file_hashes() == FROZEN_SHA256
    assert pspec.spec_sha() == SPEC_SHA
