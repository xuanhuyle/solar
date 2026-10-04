"""Next milestone (docs/research_loop_proof/NEXT_MILESTONE_PROMPT.md): t0-beta loading, the 0.5.0 adapter and the
minimal qualification. Parts that need tfc-t0 0.5.0 skip under the historical 0.3.2 environment."""

from __future__ import annotations

import ast
import json
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth import qualify

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "beta1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-beta1.yml"


def _runtime_at_least_050() -> bool:
    try:
        return tuple(int(p) for p in metadata.version("tfc-t0").split(".")[:3]) >= (0, 5, 0)
    except Exception:
        return False


needs_050 = pytest.mark.skipif(not _runtime_at_least_050(), reason="needs tfc-t0 >= 0.5.0 (the beta jobs install it)")


def test_beta_lab_never_imports_a_truth_package():
    for path in (PKG / "lab").glob("*.py"):
        src = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


def test_the_runtime_must_read_beta_normalization(monkeypatch):
    monkeypatch.setattr(t0_beta, "runtime_version", lambda: "0.3.2")
    with pytest.raises(t0_beta.BetaError):
        t0_beta.require_runtime()
    monkeypatch.setattr(t0_beta, "runtime_version", lambda: "0.5.0")
    assert t0_beta.require_runtime() == "0.5.0"


def _hub(tmp_path, body=b"weights"):
    src = tmp_path / "hub"
    src.mkdir(parents=True)
    (src / "config.json").write_text('{"embed_dim": 16}')
    (src / "model.safetensors").write_bytes(body)
    return src


def test_fetch_records_the_bytes_and_refuses_others_once_pinned(tmp_path):
    src = _hub(tmp_path)
    rec = t0_beta.fetch(tmp_path / "w", head=lambda r: "rev1", download=lambda r, rev: str(src), pinned={})
    assert rec["repo"] == "theforecastingcompany/t0-beta" and rec["served_revision"] == "rev1"
    assert set(rec["sha256"]) == {"config.json", "model.safetensors"} and not rec["pinned"]
    assert (tmp_path / "w" / "model.safetensors").read_bytes() == b"weights"
    pins = {"revision": "rev1", "sha256": rec["sha256"]}
    again = t0_beta.fetch(tmp_path / "w2", head=lambda r: "rev2", download=lambda r, rev: str(src), pinned=pins)
    assert again["pinned"] and again["qualified_revision"] == "rev1"
    other = _hub(tmp_path / "x", b"other")
    with pytest.raises(t0_beta.BetaError):
        t0_beta.fetch(tmp_path / "w3", head=lambda r: "rev3", download=lambda r, rev: str(other), pinned=pins)
    assert not (tmp_path / "w3").exists()
    (other / "model.safetensors").unlink()
    with pytest.raises(t0_beta.BetaError):
        t0_beta.fetch(tmp_path / "w4", head=lambda r: "r", download=lambda r, rev: str(other), pinned={})


def test_load_refuses_files_that_differ_from_their_record(tmp_path, monkeypatch):
    src = _hub(tmp_path)
    t0_beta.fetch(tmp_path / "w", head=lambda r: "rev1", download=lambda r, rev: str(src), pinned={})
    (tmp_path / "w" / "model.safetensors").write_bytes(b"tampered")
    monkeypatch.setattr(t0_beta, "runtime_version", lambda: "0.5.0")
    with pytest.raises(t0_beta.BetaError):
        t0_beta.load(tmp_path / "w")


class _FakeBeta:
    def __init__(self):
        self.calls = []

    def predict(self, ctx, **kw):
        import torch

        self.calls.append({"ctx": tuple(ctx.shape), **{k: (tuple(v.shape) if hasattr(v, "shape") else v)
                                                      for k, v in kw.items()}})
        return SimpleNamespace(median=torch.zeros(ctx.shape[0], kw["horizon"]) + ctx[:, -1:])


def test_the_beta_adapter_uses_the_050_call_shape():
    pytest.importorskip("torch")
    model = _FakeBeta()
    inst = t0_beta.BetaT0(model, batch_size=2)
    ctx = np.arange(168, dtype=float)
    reqs = [(ctx, None), (ctx + 1, np.ones((1, 192))), (ctx + 2, np.ones((1, 192))), (ctx + 3, np.ones((1, 192))),
            (ctx + 4, np.ones((2, 192)))]
    out = inst.forecast(reqs)
    assert inst.rows == 5 and [o.shape for o in out] == [(24,)] * 5
    assert out[3][0] == 170.0 and out[4][0] == 171.0  # each answer goes back to its own request
    shapes = sorted(((c["ctx"], c.get("future_covariates")) for c in model.calls), key=str)
    assert shapes == sorted([((1, 168), None), ((1, 168), (1, 2, 192)), ((1, 168), (1, 1, 192)),
                             ((2, 168), (2, 1, 192))], key=str)
    assert all(c["quantile_levels"] == [0.1, 0.5, 0.9] and c["horizon"] == 24 and "quantiles" not in c
               for c in model.calls)


def test_a_beta_that_cannot_run_is_recorded_as_not_viable(tmp_path, monkeypatch):
    monkeypatch.setattr(t0_beta, "runtime_version", lambda: "0.5.0")

    def broken(weights):
        raise t0_beta.BetaError("no such repository")
    rec = qualify.run(tmp_path / "w", tmp_path / "out", fetch=broken)
    assert rec["verdict"] == "BETA NOT VIABLE" and "no such repository" in rec["error"]
    assert json.loads((tmp_path / "out" / "verdict.json").read_text())["verdict"] == "BETA NOT VIABLE"
    assert (tmp_path / "out" / "REPORT.md").read_text().startswith("# t0-beta qualification: BETA NOT VIABLE")


@needs_050
def test_qualification_runs_end_to_end_with_a_tiny_untrained_beta(tmp_path, monkeypatch):
    monkeypatch.setattr(t0_beta, "PINNED", {})  # the tiny model is not the qualified bytes
    import torch
    from t0 import T0Forecaster

    torch.manual_seed(0)
    m = T0Forecaster(embed_dim=32, num_layers=2, num_heads=2, mlp_hidden_dim=64, patch_size=32, group_every_n=1,
                     dropout=0.0, quantile_levels=[0.01, 0.1, 0.5, 0.9, 0.99], scaler_eps=0.01,
                     scaler_eps_mode="std_clamp").eval()
    m.save_pretrained(tmp_path / "hub")
    rec = qualify.run(tmp_path / "w", tmp_path / "out",
                      fetch=lambda w: t0_beta.fetch(w, head=lambda r: "rev", download=lambda r, rev: str(tmp_path / "hub"),
                                                    pinned={}))
    assert "error" not in rec, rec.get("error")
    assert rec["Q1"]["pass"] and rec["Q2"]["pass"] and rec["Q3"]["pass"]
    assert rec["t0_beta_forecasts"] == 16 * 2 + 2 + 240
    assert rec["verdict"] in ("PASS", "BETA NOT VIABLE")


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_the_beta_workflow_is_manual_and_scoped(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["qualify", "preflight", "run"]
    jobs = wf["jobs"]
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "actions/checkout" not in pub and "beta1/run-${{ github.run_id }}" in pub
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text and "HF_TOKEN" not in text  # t0-beta is ungated
    assert "constraints-ci.txt" not in text.replace("keep constraints-ci.txt", "")
    q = jobs["qualify"]["steps"]
    install = next(s for s in q if s.get("name", "").startswith("Install"))
    assert "research_loop_proof/beta1/constraints-beta.txt" in install["run"] and "requirements.txt" not in install["run"]
    assert any("tests/test_research_loop_beta1.py" in s.get("run", "") for s in q)


def test_the_beta_constraints_differ_from_ci_only_in_the_runtime():
    def pins(p):
        return {ln.split("==")[0]: ln.split("==")[1] for ln in p.read_text().splitlines() if "==" in ln and
                not ln.startswith("#")}
    ci, beta = pins(ROOT / "constraints-ci.txt"), pins(PKG / "constraints-beta.txt")
    assert beta.pop("tfc-t0") == "0.5.0" and ci.pop("tfc-t0") == "0.3.2" and beta == ci


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_only_the_loop_step_holds_the_api_key_and_the_research_job_has_no_truth(wf):
    jobs = wf["jobs"]
    assert set(jobs) == {"qualify", "observe", "research", "check", "evaluate", "publish"}
    for name in ("qualify", "observe", "check", "evaluate", "publish"):
        assert _secret_steps(jobs[name]) == [], name
    r = _secret_steps(jobs["research"])
    assert len(r) == 1 and " loop " in r[0]["run"] and r[0]["env"]["HF_HUB_OFFLINE"] == "1"
    assert [k for k, v in r[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
    checkout = jobs["research"]["steps"][0]
    patterns = checkout["with"]["sparse-checkout"]
    for d in ("!/research_loop_proof/phase0/truth/", "!/research_loop_proof/beta1/truth/", "!/tests/"):
        assert d in patterns
    guard = jobs["research"]["steps"][1]
    assert "rm -rf .git" in guard["run"] and "research_loop_proof/beta1/truth" in guard["run"]
    downloads = [st["with"]["name"] for st in jobs["research"]["steps"] if st.get("uses", "").startswith("actions/download")]
    assert downloads == ["beta1-observed-${{ github.run_id }}"]
    pub = json.dumps(jobs["publish"])
    assert "needs.qualify.outputs.manifest_sha256 || needs.check.outputs.manifest_sha256 || " \
           "needs.evaluate.outputs.manifest_sha256" in pub
    assert jobs["check"]["if"].count("preflight") == 1 and "inputs.mode == 'run'" in jobs["evaluate"]["if"]


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    import re
    import subprocess

    pattern = re.compile(r"^def make_world\(", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    kept = [f for f in files if not f.startswith(("research_loop_proof/phase0/truth/", "research_loop_proof/beta1/truth/",
                                                  "tests/"))]
    assert kept and not [f for f in kept if pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the researcher and the brief

from research_loop_proof.beta1.lab import researcher as bres  # noqa: E402
from research_loop_proof.beta1.truth import evaluate as bev, observe as bobs, preflight as bpre, spec as bspec  # noqa: E402
from research_loop_proof.phase0.lab import executor  # noqa: E402
from research_loop_proof.phase0.lab import researcher as p0res  # noqa: E402
from research_loop_proof.phase0.truth import generator as gen  # noqa: E402

TEST_MODEL = "test-model-id"


def test_the_brief_adds_exactly_the_owners_rule():
    old = (ROOT / "research_loop_proof/phase0/lab/brief.md").read_text().splitlines()
    new = (PKG / "lab" / "brief.md").read_text().splitlines()
    added = [ln for ln in new if ln not in old]
    assert added == ["- Evidence about a multi-variable set applies to the set. It does not by itself establish that every "
                     "member is useful. Claims about individual candidates require evidence that distinguishes them."]
    assert [ln for ln in new if ln != added[0]] == old
    assert bres.system_text().startswith(bres.BRIEF.rstrip("\n")) and "RESPONSE SCHEMA" in bres.system_text()


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


def _beliefs(status="untested", cites=None, overrides=None):
    rows = {i: {"candidate": i, "status": status, "cites": list(cites or []), "reason": "r"} for i in executor.IDS}
    for i, row in (overrides or {}).items():
        rows[i].update(row)
    return [rows[i] for i in executor.IDS]


def _exp(cov, ref=(), win=28):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves", "because": "b"}


def _reply(beliefs, experiments=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": beliefs, "experiments": list(experiments), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies():
    return [_resp(_reply(_beliefs(), [_exp(["X01"]), _exp(["X02"])])),
            _resp(_reply(_beliefs("promising", ["E1"]), [_exp(["X03"], win=14), _exp(["X04"], win=14)])),
            _resp(_reply(_beliefs("promising", ["E3"]), [_exp(["X01"], win=14), _exp(["X02"], ["X01"], win=14)])),
            _resp(_reply(_beliefs("accepted", ["E5"], {"X02": {"status": "rejected", "cites": ["E6"]}}),
                         final=["X01"], conclusion="X01 helps."))]


REFUSAL = SimpleNamespace(type="refusal", category="reasoning_extraction", explanation="asked for internal reasoning")


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


def _obs_world():
    return bobs.preflight_world("4242")


def test_every_attempt_records_the_refusal_details(pinned):
    w = _obs_world()
    events = []
    replies = [_resp("", stop="refusal", details=REFUSAL, tokens=200)] + _replies()
    client = _Client(replies)
    rec = bres.Researcher(client, TEST_MODEL, executor.Lab(gen.observed_arrays(w, 126), _Inst()),
                          emit=events.append).run()
    first = rec["calls"][0]["attempts"]
    assert first[0]["stop_reason"] == "refusal" and first[0]["refusal_category"] == "reasoning_extraction"
    assert first[0]["stop_details"] == {"type": "refusal", "category": "reasoning_extraction",
                                        "explanation": "asked for internal reasoning"}
    assert first[0]["repair"] == 0 and first[1]["repair"] == 1 and first[1]["retry"] == 0
    for a in first:
        assert a["elapsed_s"] >= 0 and a["served_matches_requested"] is True and a["request_id"] == "req-test"
        assert a["requested_model_sha256"] == a["served_model_sha256"] == p0res.sha256_text(TEST_MODEL)
        assert set(a["usage"]) == {"input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"}
    assert rec["calls"][0]["valid"] and rec["final_valid"]
    assert client.sent[0]["system"][0]["text"] == bres.system_text()
    assert bres.rebuild_mismatches(rec["calls"]) == []
    assert TEST_MODEL not in json.dumps(rec) and TEST_MODEL not in json.dumps(events)


def test_the_preflight_check_is_operational(tmp_path, pinned):
    w = _obs_world()
    client = _Client(_replies())
    rec = bres.Researcher(client, TEST_MODEL, executor.Lab(gen.observed_arrays(w, 126), _Inst())).run()
    d = tmp_path / "r"
    d.mkdir()
    (d / "ai.json").write_text(json.dumps(rec))
    (d / "integrity.json").write_text('{"failure": null}')
    out = bpre.check(d)
    assert out["verdict"] == "PASS" and out["valid_calls"] == 4 and out["refusals"] == 0 and out["experiments"] == 6
    two = json.loads(json.dumps(rec))
    for a in (two["calls"][0]["attempts"][0], two["calls"][1]["attempts"][0]):
        a.update(stop_reason="refusal", refusal_category="bio")
    (d / "ai.json").write_text(json.dumps(two))
    assert bpre.check(d)["verdict"] == "FAIL" and bpre.check(d)["refusal_categories"] == {"bio": 2}
    bad = json.loads(json.dumps(rec))
    bad["calls"][2]["valid"] = False
    (d / "ai.json").write_text(json.dumps(bad))
    assert bpre.check(d)["verdict"] == "FAIL"


def test_worlds_are_new_and_the_scored_run_needs_a_preflight_pass(tmp_path):
    import hashlib

    from research_loop_proof.phase0.truth import observe as p0obs

    a, b = bobs.hidden_world("777"), bobs.preflight_world("777")
    assert not np.array_equal(a.y, b.y) and not np.array_equal(a.y, p0obs.hidden_world("777").y)
    assert a.seed == gen.seed_of(f"beta1:{bspec.spec_sha()}:777") and 86 <= a.tau <= 92 and a.n_days == 154
    with pytest.raises(ValueError):
        bobs.hidden_world("x1")

    def write(verdict, sha, phase="beta1-preflight"):
        body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", bspec.spec_sha())
    assert bobs.published_errors(tmp_path, "beta1-preflight") == []
    write("FAIL", bspec.spec_sha())
    assert bobs.published_errors(tmp_path, "beta1-preflight")
    write("PASS", "0" * 64)
    assert bobs.published_errors(tmp_path, "beta1-preflight")
    write("PASS", bspec.spec_sha(), phase="beta1-qualify")
    assert bobs.published_errors(tmp_path, "beta1-preflight")
    assert bobs.main(["--mode", "run", "--run-id", "5", "--preflight-dir", str(tmp_path / "none"),
                      "--out", str(tmp_path / "o")]) == 1


def _notebook(roles, e_lo=0.2, r_lo=-0.05, final=None, extra=None):
    def res(i, cov, lo, last, ref=()):
        return {"id": f"E{i}", "request": {**_exp(cov, ref)},
                "result": {"id": f"E{i}", "covariates": cov, "reference": list(ref), "skill": lo + 0.05, "lo95": lo,
                           "hi95": lo + 0.1, "scored_days": [last - 27, last]}}
    r, e = roles["R"], roles["E"]
    b2 = _beliefs(overrides={r: {"status": "promising", "cites": ["E1"]}})
    b3 = _beliefs(overrides={r: {"status": "deteriorated", "cites": ["E3"]}, e: {"status": "promising", "cites": ["E2"]}})
    b4 = _beliefs(overrides={r: {"status": "rejected", "cites": ["E3"]}, e: {"status": "accepted", "cites": ["E2"]}})
    calls = [
        {"call": 1, "round": 1, "cutoff": 84, "final": False, "valid": True, "attempts": [],
         "response": _reply(_beliefs(), [_exp([r])]), "experiments": [res(1, [r], 0.1, 84)]},
        {"call": 2, "round": 2, "cutoff": 112, "final": False, "valid": True, "attempts": [],
         "response": _reply(b2), "experiments": [res(2, [e], e_lo, 112), res(3, [r], r_lo, 112)]},
        {"call": 3, "round": 3, "cutoff": 126, "final": False, "valid": True, "attempts": [],
         "response": _reply(b3), "experiments": [res(4, [roles["D"]], 0.05, 126, ref=[e])]},
        {"call": 4, "round": None, "cutoff": 126, "final": True, "valid": True, "attempts": [],
         "response": _reply(b4, final=final or [e], conclusion="c"), "experiments": []},
    ]
    return calls


def test_the_verdict_map_separates_infrastructure_from_research():
    w = bobs.hidden_world("31")
    roles = {k: w.ids[k] for k in ("R", "E", "D", "N")}
    calls = _notebook(roles)
    ai = {"calls": calls, "final_valid": True, "final_selection": [roles["E"]]}
    beh = bev.behaviours(calls, roles, w.tau, ai["final_selection"])
    assert beh["B3"] and beh["B5"] and beh["B7"] and beh["B8"] and beh["B9"] and beh["B10"]
    ev = {"E_days_99_126": {"lo95": 0.1}, "R_days_57_84": {"lo95": 0.1}}
    good = {"t0": {"lo95": 0.05}}
    assert bev.verdict([], [], ai, beh, roles, ev, good)[0] == "BASIC AUTONOMOUS LOOP OBSERVED"
    assert bev.verdict([], ["call 1: no valid response after its repair (refusal)"], ai, beh, roles, ev, good)[0] == \
        "RESEARCH INFRASTRUCTURE FAILURE"
    assert bev.verdict(["guard"], [], ai, beh, roles, ev, good)[0] == "RESEARCH INFRASTRUCTURE FAILURE"
    with_r = dict(ai, final_selection=[roles["E"], roles["R"]])
    assert bev.verdict([], [], with_r, beh, roles, ev, good)[0] == "RESEARCHER FEASIBILITY FAILED"
    with_n = dict(ai, final_selection=[roles["E"], roles["N"]])
    beh_n = bev.behaviours(calls, roles, w.tau, with_n["final_selection"])
    assert not beh_n["B10"] and bev.verdict([], [], with_n, beh_n, roles, ev, good)[0] == "RESEARCHER FEASIBILITY FAILED"
    d_only = dict(ai, final_selection=[roles["D"]])
    beh_d = bev.behaviours(calls, roles, w.tau, d_only["final_selection"])
    assert bev.verdict([], [], d_only, beh_d, roles, ev, good)[0] == "AMBIGUOUS"
    assert bev.verdict([], [], ai, beh, roles, ev, {"t0": {"lo95": -0.01}})[0] == "AMBIGUOUS"
    invalid = json.loads(json.dumps(ai))
    invalid["calls"][1]["valid"] = False
    invalid["calls"][1]["attempts"] = [{"stop_reason": "refusal", "refusal_category": "bio"}] * 2
    invalid["calls"][1]["errors"] = ["the response was a refusal"]
    assert "bio" in bev.call_failures(invalid)[0] and len(bev.call_failures({"calls": []})) == 4


class _FakeBetaModel:
    """A stand-in for t0-beta behind the 0.5.0 predict API: last day plus 0.3 times the covariates' last day."""

    def predict(self, ctx, horizon, quantile_levels, future_covariates=None):
        import torch

        med = ctx[:, -24:].clone()
        if future_covariates is not None:
            med = med + 0.3 * future_covariates[:, :, -24:].sum(1)
        return SimpleNamespace(median=med)


def test_preflight_and_scored_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned):
    pytest.importorskip("torch")
    anthropic = pytest.importorskip("anthropic")
    from research_loop_proof.beta1.lab import run as brun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (_FakeBetaModel(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    # preflight
    assert bobs.main(["--mode", "preflight", "--run-id", "11", "--out", str(tmp_path / "pobs")]) == 0
    pmeta = json.loads((tmp_path / "pobs" / "observed.json").read_text())
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_replies()))
    pargs = ["--observed", str(tmp_path / "pobs" / "observed.npz"), "--observed-sha", pmeta["arrays_sha256"],
             "--weights", "unused", "--out", str(tmp_path / "pres")]
    assert brun.main(["loop", *pargs]) == 0
    assert bpre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    pv = json.loads((tmp_path / "pout" / "verdict.json").read_text())
    assert pv["verdict"] == "PASS" and pv["spec_sha"] == bspec.spec_sha()
    import hashlib
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    # scored run
    assert bobs.main(["--mode", "run", "--run-id", "12", "--preflight-dir", str(tmp_path / "pout"),
                      "--out", str(tmp_path / "obs")]) == 0
    meta = json.loads((tmp_path / "obs" / "observed.json").read_text())
    args = ["--observed", str(tmp_path / "obs" / "observed.npz"), "--observed-sha", meta["arrays_sha256"],
            "--weights", "unused", "--out", str(tmp_path / "res")]
    assert brun.main(["scripted", *args]) == 0
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_replies()))
    assert brun.main(["loop", *args]) == 0
    (tmp_path / "res" / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    out = tmp_path / "out"
    assert bev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
                     "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity"]["issues"] == [] and rec["call_failures"] == [] and rec["integrity"]["experiments_recomputed"] == 6
    assert rec["verdict"] in ("RESEARCHER FEASIBILITY FAILED", "BASIC AUTONOMOUS LOOP OBSERVED", "AMBIGUOUS")
    assert {c["incremental_label"] for c in rec["candidates"]} == {"E given D", "R given E", "D given E", "N given E"}
    assert (out / "REPORT.md").read_text().startswith(f"# beta1 hidden-world result: {rec['verdict']}")
    # a refusal-ended call is an infrastructure failure, not a research failure
    ai = json.loads((tmp_path / "res" / "ai.json").read_text())
    ai["calls"][1]["valid"] = False
    (tmp_path / "res" / "ai.json").write_text(json.dumps(ai))
    bev.main(["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(tmp_path / "res"),
              "--weights", "unused", "--out", str(tmp_path / "out2")])
    assert json.loads((tmp_path / "out2" / "evaluation.json").read_text())["verdict"] == "RESEARCH INFRASTRUCTURE FAILURE"


FROZEN_SHA256 = {
    "docs/research_loop_proof/BETA1_SPEC.md":
        "5455252d62c6b461029515349af95ce8b95db42438bbdd33d278352cc603486b",
    "research_loop_proof/beta1/lab/brief.md":
        "cecefc956fc6dc651b430616b164d24e73ae5d87e8539cadfb19d495ada39635",
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
SPEC_SHA = "68094b40170f1ab5719187ee1025f75ac17de916fccdc435c5498f09b7edd5b6"


def test_the_beta1_files_are_frozen():
    assert bspec.file_hashes() == FROZEN_SHA256
    assert bspec.spec_sha() == SPEC_SHA
