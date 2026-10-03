"""Phase 0 falsification spike (docs/research_loop_proof/PHASE0_SPEC.md): frozen rule files, the worlds, the two
instruments' information sets, the Phase A gate and its integrity checks, and the workflow's separation rules.
Offline: Phase A runs here with a tiny untrained t0, whose numbers mean nothing."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from research_loop_proof.phase0.lab import instruments
from research_loop_proof.phase0.lab.instruments import ridge_forecast, window
from research_loop_proof.phase0.truth import generator as gen
from research_loop_proof.phase0.truth import phase_a, spec
from research_loop_proof.phase0.truth.calibrate import calibrate

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "phase0"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-phase0.yml"

FROZEN_SHA256 = {
    "docs/research_loop_proof/PHASE0_SPEC.md":
        "9795d414cb7b327d17a84232cd4e29681c3af86f62aa391a39ce0887a45060bf",
    "research_loop_proof/phase0/truth/world.json":
        "deba069bfdc41f6bf7994abc0277f813470a608554be4d12e3c7a5ecb0d72158",
    "research_loop_proof/phase0/truth/generator.py":
        "28bc4dc4fea50f1a70193f868d6cc88815daf20666efa269be4003c873ad3ecc",
    "research_loop_proof/phase0/truth/calibrate.py":
        "3dd491e25849acbe50b92f26ae1ca279563a1dad27e176525e988adbbaabdd27",
    "research_loop_proof/phase0/truth/phase_a.py":
        "5516aa22b63b0c3e6d4549a91d35c22fd2c2e0ef1117f3495ea309bb4c6c93fd",
    "research_loop_proof/phase0/lab/instruments.py":
        "1e177eadfa4bfee627c61bfeee74c02938775b5401f963f08392db9d53c85de7",
    "research_loop_proof/phase0/lab/menu.json":
        "17ab3abe11b927f200ec031196a9ed63d418d922f8c470b0b935deb3e5925b74",
    "research_loop_proof/phase0/lab/brief.md":
        "5d004eacde766e1a1c203b0200f8363ba28fb1516f01599c878c31b440dcfb2f",
}
SPEC_SHA = "6ab46db996e345de093e5b650a3cd104ec60da23a1d4a0966ed72ce68b8788dc"


# ----------------------------------------------------------------- the freeze

def test_the_rule_files_are_frozen():
    assert spec.file_hashes() == FROZEN_SHA256
    assert spec.spec_sha() == SPEC_SHA


def test_the_calibration_reproduces_the_recorded_attempts():
    cal, frozen = calibrate(), gen.WORLD["calibration"]
    assert cal["m"] == frozen["m"] == 2.0
    assert [(a["m"], a["median"], a["per_world_skill"]) for a in cal["attempts"]] == \
        [(a["m"], a["median"], a["per_world_skill"]) for a in frozen["record"]["attempts"]]


def test_the_brief_and_menu_carry_no_truth():
    brief = (PKG / "lab" / "brief.md").read_text(encoding="utf-8").lower()
    for word in ("retired", "emerging", "decoy", "proxy", "correlated", "change point", "tau", "hinge", "role"):
        assert word not in brief, word
    menu = json.loads((PKG / "lab" / "menu.json").read_text(encoding="utf-8"))
    text = json.dumps(menu).lower()
    assert "roles" not in menu and "retired" not in text and "emerging" not in text
    assert menu["candidates"] == ["X01", "X02", "X03", "X04"]
    researcher = menu["researcher"]
    assert len(researcher["model_sha256"]) == 64 and researcher["effort"] == "high"
    assert "claude-" not in text and "opus" not in text and "sonnet" not in text


def test_the_lab_never_imports_the_truth():
    for path in (PKG / "lab").glob("*.py"):
        src = path.read_text(encoding="utf-8")
        assert "truth" not in src, path
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n or "generator" in n for n in names), path


# ----------------------------------------------------------------- the worlds

def test_a_world_is_a_function_of_its_seed():
    a = gen.make_world(123, n_days=30, tau=15, form="linear", m=2.0)
    b = gen.make_world(123, n_days=30, tau=15, form="linear", m=2.0)
    c = gen.make_world(124, n_days=30, tau=15, form="linear", m=2.0)
    assert np.array_equal(a.y, b.y) and all(np.array_equal(a.x[r], b.x[r]) for r in gen.ROLES)
    assert not np.array_equal(a.y, c.y)


@pytest.mark.parametrize("s", range(3))
def test_the_roles_behave_as_specified(s):
    w = gen.make_world(gen.seed_of(f"roles-{s}"), n_days=400, tau=201, form="linear", m=2.0)
    pre, post = slice(0, 200 * 24), slice(200 * 24, 400 * 24)

    def corr(a, b):
        return float(np.corrcoef(a, b)[0, 1])

    z = {r: w.signs[r] * w.x[r] for r in gen.ROLES}  # the unsigned series the target is built from
    for r in gen.ROLES:  # standardised on pre-change days only
        assert abs(z[r][pre].mean()) < 1e-12 and abs(z[r][pre].std() - 1) < 1e-12
    assert abs(corr(z["D"], z["E"]) - 0.8) < 0.06
    # two independent persistent series can correlate by about +-0.15 over 200 days, hence the loose bounds
    assert corr(w.y[pre], z["R"][pre]) > 0.6 and abs(corr(w.y[post], z["R"][post])) < 0.3
    assert abs(corr(w.y[pre], z["E"][pre])) < 0.3 and corr(w.y[post], z["E"][post]) > 0.6
    assert abs(corr(w.y[pre], z["N"][pre])) < 0.3 and abs(corr(w.y[post], z["N"][post])) < 0.3
    assert 0.75 < w.y[post].var() / w.y[pre].var() < 1.3


def test_the_change_starts_at_midnight_of_day_tau():
    w = gen.make_world(7, n_days=40, tau=20, form="linear", m=2.0)
    w0 = gen.make_world(7, n_days=40, tau=20, form="linear", m=0.0)
    effect = w.y - w0.y
    c = np.sqrt(0.75 * 2.0)
    assert np.allclose(effect[: 19 * 24], c * w.signs["R"] * w.x["R"][: 19 * 24])
    assert np.allclose(effect[19 * 24:], c * w.signs["E"] * w.x["E"][19 * 24:])


def test_the_observed_sign_leaves_the_target_unchanged_and_is_balanced_in_phase_a():
    a = gen.make_world(5, n_days=30, tau=15, form="linear", m=2.0, e_sign=1)
    b = gen.make_world(5, n_days=30, tau=15, form="linear", m=2.0, e_sign=-1)
    assert np.array_equal(a.y, b.y) and np.array_equal(a.x["E"], -b.x["E"])
    assert all(np.array_equal(a.x[r], b.x[r]) for r in ("R", "D", "N"))
    signs = [w.signs["E"] for w in phase_a.worlds("linear", 40)]
    assert signs == [1, -1] * 20
    assert sum(w.signs["E"] for w in phase_a.worlds("hinge", 12)) == 0
    drawn = [gen.make_world(gen.seed_of(f"s-{i}"), n_days=20, tau=10, form="linear", m=2.0).signs
             for i in range(200)]
    for r in gen.ROLES:
        assert 60 < sum(d[r] == 1 for d in drawn) < 140


def test_a_fixed_sign_response_to_the_covariate_does_not_pass():
    """An instrument that adds a fixed multiple of the covariate, using no post-change evidence (here on top of a
    persistence forecast), gains in half the Phase A worlds and loses in the other half."""
    ws = phase_a.worlds("linear", 40)
    arms = {}
    for label, role in (("none", None), ("E", "E"), ("N", "N")):
        err = np.empty((40, 21))
        for i, w in enumerate(ws):
            for k in range(21):
                d = w.tau + k
                f = w.y[w.day_slice(d - 1, d - 1)] + (0 if role is None else 0.3 * w.x[role][w.day_slice(d, d)])
                err[i, k] = np.abs(f - w.y[w.day_slice(d, d)]).sum()
        arms[f"x_{label}"] = err
    crit = phase_a.criteria(arms, "x")
    assert not any(crit["pass"].values())


def test_the_hinge_effect_is_centred_and_scaled():
    z = np.random.default_rng(0).normal(size=1_000_000)
    e = gen.effect(z, "hinge")
    assert abs(e.mean()) < 0.005 and abs(e.std() - 1) < 0.005
    assert np.all(e[z < gen._hinge_moments(0.7)[0]] == e.min())


def test_phase_b_worlds_follow_the_tau_rule_and_hide_the_roles():
    taus = set()
    for s in range(40):
        w = gen.make_world(gen.seed_of(f"b-{s}"), n_days=154, tau=None, form="linear", m=2.0, tau_rule=True)
        taus.add(w.tau)
        assert 86 <= w.tau <= 92 and sorted(w.ids.values()) == ["X01", "X02", "X03", "X04"]
        assert w.canary.startswith("CANARY-") and len(w.canary) == 27
    assert len(taus) >= 5
    obs = gen.observed_arrays(w, 126)
    assert sorted(obs) == ["X01", "X02", "X03", "X04", "y"] and all(len(v) == 126 * 24 for v in obs.values())
    h = gen.arrays_sha256(obs)
    assert h == gen.arrays_sha256({k: v.copy() for k, v in obs.items()})
    obs["X02"][5] = np.nextafter(obs["X02"][5], np.inf)
    assert gen.arrays_sha256(obs) != h


# ----------------------------------------------------------------- the instruments' information

def _poisoned(w, day, context):
    """Copies with everything outside the information set of forecasting ``day`` set to NaN."""
    y, xe = w.y.copy(), w.x["E"].copy()
    y[(day - 1) * 24:] = np.nan
    xe[day * 24:] = np.nan
    y[: (day - context - 1) * 24] = np.nan
    xe[: (day - context - 1) * 24] = np.nan
    return y, xe


@pytest.mark.parametrize("context,square", [(7, False), (28, True)])
def test_ridge_uses_only_the_window(context, square):
    w = gen.make_world(11, n_days=90, tau=40, form="linear", m=2.0)
    for day in (45, 60, 89):
        clean = ridge_forecast(w.y, [w.x["E"]], day, context, square=square)
        y, xe = _poisoned(w, day, context)
        assert np.array_equal(clean, ridge_forecast(y, [xe], day, context, square=square))
        y2 = w.y.copy()
        y2[(day - 2) * 24 + 5] += 1.0  # a legal change inside the window moves the forecast
        assert not np.array_equal(clean, ridge_forecast(y2, [w.x["E"]], day, context, square=square))


def test_the_t0_window_holds_exactly_the_information_set():
    w = gen.make_world(11, n_days=90, tau=40, form="linear", m=2.0)
    ctx, block = window(w.y, [w.x["E"], w.x["N"]], 50, 7)
    assert ctx.shape == (7 * 24,) and block.shape == (2, 8 * 24)
    assert np.array_equal(ctx, w.y[42 * 24: 49 * 24]) and np.array_equal(block[0], w.x["E"][42 * 24: 50 * 24])
    y, xe = _poisoned(w, 50, 7)
    ctx2, block2 = window(y, [xe], 50, 7)
    assert np.isfinite(ctx2).all() and np.isfinite(block2).all()
    with pytest.raises(ValueError):
        window(w.y, [], 5, 7)


# ----------------------------------------------------------------- Phase A gate and checks

def _arms(e_gain, n_gain, worlds=40, days=21, seed=0):
    rng = np.random.default_rng(seed)
    base = rng.uniform(20, 30, size=(worlds, days))
    noise = lambda: rng.normal(0, 0.3, size=(worlds, days))  # noqa: E731
    return {"t0_none": base + noise(), "t0_N": base * (1 - n_gain) + noise(), "t0_E": base * (1 - e_gain) + noise()}


def test_the_gate_needs_e_to_beat_both_no_covariate_and_the_placebo():
    assert all(phase_a.criteria(_arms(0.20, 0.0), "t0")["pass"].values())
    # a gain any covariate row gives (N as large as E) does not pass
    assert not any(phase_a.criteria(_arms(0.10, 0.10), "t0")["pass"].values())
    # nor does beating the placebo while not beating "without"
    assert not all(phase_a.criteria(_arms(0.0, -0.20), "t0")["pass"].values())
    small = phase_a.criteria(_arms(0.03, 0.0), "t0")
    assert not small["pass"]["C1"]


def test_the_gate_uses_unrounded_values_and_two_day_blocks_for_c3(monkeypatch):
    a, b = np.full((2, 21), 0.950004), np.ones((2, 21))
    assert phase_a.cluster_skill(a, b, 7, 20)["skill"] == pytest.approx(1 - 0.950004, abs=1e-12)
    seen = []
    real = phase_a.metrics.pair_skill

    def spy(*args, **kw):
        seen.append(kw.get("block_days"))
        return real(*args, **kw)

    monkeypatch.setattr(phase_a.metrics, "pair_skill", spy)
    phase_a.per_world_pairs(np.random.default_rng(1).uniform(1, 2, (2, 21)), np.ones((2, 21)) * 1.5, 7, 20)
    assert seen == [2, 2] and phase_a.C3_BLOCK_DAYS == 2


def test_how_soon_reads_the_earliest_bin_after_which_all_are_positive():
    rows = [{"k": [0, 0], "lo95": 0.1}, {"k": [1, 3], "lo95": 0.01}, {"k": [4, 6], "lo95": -0.01},
            {"k": [7, 13], "lo95": 0.02}, {"k": [14, 20], "lo95": 0.03}]
    assert phase_a.how_soon(rows) == "k = 7-13"
    assert phase_a.how_soon(rows[:3]) == "never within the measured range"


class _Stub:
    """A stand-in instrument: tomorrow = the last context day plus the summed covariates of the forecast day."""

    sanitised = 0

    def forecast(self, requests):
        return [ctx[-24:] + (0 if block is None else block[:, -24:].sum(0)) for ctx, block in requests]


def test_the_poison_check_catches_a_window_that_leaks(monkeypatch):
    w = phase_a.worlds("linear", 1)[0]
    assert phase_a.poison_check(_Stub(), w, 7)["pass"]

    def leaky(y, x, day, context_days):
        ctx, block = window(y, x, day, context_days)
        return np.r_[ctx[24:], y[(day - 1) * 24: day * 24]], block

    monkeypatch.setattr(phase_a, "window", leaky)
    assert not phase_a.poison_check(_Stub(), w, 7)["pass"]


def test_phase_a_runs_end_to_end_with_a_tiny_untrained_t0(tmp_path, monkeypatch):
    pytest.importorskip("t0")
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)  # set on Actions; the record would carry them
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    smoke = phase_a.run(tmp_path / "smoke", fake=True, smoke=True)
    assert smoke["calibration_reproduced"] and smoke["finite"] and smoke["sanitised"] == 0
    assert "verdict" not in smoke and "criteria" not in smoke
    rec = phase_a.run(tmp_path / "run", fake=True)
    assert rec["integrity"] == {"calibration_reproduced": True, "sanitised_outputs": 0, "poison": True}
    assert rec["t0_forecast_days"] == 40 * 21 * 3 + 12 * 21 * 2 + 8 * 42 * 2
    assert rec["t0_forecasts_total"] == rec["t0_forecast_days"] + 4 * 32 + 6
    assert smoke["t0_forecasts_total"] == 4 * 32 + 1
    assert rec["verdict"] in ("PASS", "INSTRUMENT FEASIBILITY FAILED")
    assert set(rec["criteria"]["by_comparison"]) == {"E_vs_none", "E_vs_N"}
    verdict = json.loads((tmp_path / "run" / "verdict.json").read_text())
    assert verdict == {"phase": "A", "verdict": rec["verdict"], "spec_sha": spec.spec_sha(), "run_id": None,
                       "commit": None}
    assert (tmp_path / "run" / "REPORT.md").read_text().startswith(f"# Phase A result: {rec['verdict']}")


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_the_workflow_is_manual_with_only_the_built_modes(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"]
    inputs = on["workflow_dispatch"]["inputs"]
    assert inputs["mode"]["options"] == ["smoke", "phaseA", "phaseB"] and "phase_a_run" in inputs
    assert wf["permissions"] == {}


def test_only_publish_writes_and_it_holds_no_secret(wf):
    jobs = wf["jobs"]
    assert set(jobs) == {"phase_a", "observe", "research", "evaluate", "publish"}
    for name in ("phase_a", "observe", "research", "evaluate"):
        assert jobs[name]["permissions"] == {"contents": "read"}, name
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "actions/checkout" not in pub
    assert "ls-remote --exit-code" in pub and "phase0/run-${{ github.run_id }}" in pub
    assert "sha256sum -c MANIFEST.sha256" in pub
    assert "needs.phase_a.outputs.manifest_sha256 || needs.evaluate.outputs.manifest_sha256" in pub
    assert jobs["phase_a"]["if"] == "inputs.mode != 'phaseB'"
    assert all("inputs.mode == 'phaseB'" in jobs[n]["if"] for n in ("observe", "research", "evaluate"))


def _secret_steps(job):
    return [s for s in job["steps"] if "secrets." in json.dumps(s)]


def test_secrets_are_scoped_to_the_steps_that_need_them(wf):
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/cache" not in text
    jobs = wf["jobs"]
    a = _secret_steps(jobs["phase_a"])
    assert len(a) == 1 and a[0]["env"] == {"HF_TOKEN": "${{ secrets.HF_TOKEN }}", "MODE": "${{ inputs.mode }}"}
    assert "research_loop_proof.phase0.truth.phase_a" in a[0]["run"]
    assert _secret_steps(jobs["observe"]) == []
    r = _secret_steps(jobs["research"])
    assert [sorted(k for k, v in s["env"].items() if "secrets." in v) for s in r] == [["HF_TOKEN"], ["ANTHROPIC_API_KEY"]]
    assert " weights " in r[0]["run"] and " loop " in r[1]["run"] and r[1]["env"]["HF_HUB_OFFLINE"] == "1"
    e = _secret_steps(jobs["evaluate"])
    assert len(e) == 1 and list(e[0]["env"]) == ["HF_TOKEN"] and " weights " in e[0]["run"]
    assert text.count("secrets.ANTHROPIC_API_KEY") == 1
    for name in ("phase_a", "observe", "research", "evaluate"):
        checkout = next(s for s in jobs[name]["steps"] if s.get("uses", "").startswith("actions/checkout"))
        assert checkout["with"]["persist-credentials"] is False
    assert any("tests/test_research_loop_phase0.py" in s.get("run", "") for s in jobs["phase_a"]["steps"])


def test_the_research_job_runs_without_the_truth_on_disk(wf):
    steps = wf["jobs"]["research"]["steps"]
    checkout = steps[0]
    assert checkout["uses"].startswith("actions/checkout")
    assert checkout["with"]["sparse-checkout-cone-mode"] is False
    assert "!/research_loop_proof/phase0/truth/" in checkout["with"]["sparse-checkout"]
    guard = steps[1]
    assert guard["name"].startswith("Guard")
    assert "research_loop_proof/phase0/truth" in guard["run"] and "rm -rf .git" in guard["run"]
    assert "def make_world" in guard["run"]
    assert not any("truth" in s.get("run", "").replace("research_loop_proof/phase0/truth", "")
                   for s in steps[2:])
    downloads = [s for s in steps if s.get("uses", "").startswith("actions/download-artifact")]
    assert [d["with"]["name"] for d in downloads] == ["phase0-observed-${{ github.run_id }}"]
    observe = wf["jobs"]["observe"]["steps"]
    uploads = [s for s in observe if s.get("uses", "").startswith("actions/upload-artifact")]
    assert [u["with"]["path"] for u in uploads] == ["obs/"]


# ----------------------------------------------------------------- Phase B

from types import SimpleNamespace  # noqa: E402

from research_loop_proof.phase0.lab import executor, researcher, scripted  # noqa: E402
from research_loop_proof.phase0.truth import evaluate, observe  # noqa: E402

TEST_MODEL = "test-model-id"


class _Inst:
    """Stand-in instrument: tomorrow = the last context day plus 0.3 times each covariate's forecast-day values."""

    rows = sanitised = 0

    def forecast(self, requests):
        self.rows += len(requests)
        return [ctx[-24:] + (0 if b is None else 0.3 * b[:, -24:].sum(0)) for ctx, b in requests]


def _resp(obj, *, model=TEST_MODEL, stop="end_turn", tokens=1000):
    text = obj if isinstance(obj, str) else json.dumps(obj)
    usage = SimpleNamespace(input_tokens=tokens, output_tokens=tokens // 2, cache_read_input_tokens=0,
                            cache_creation_input_tokens=0)
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], model=model, stop_reason=stop,
                           usage=usage, _request_id="req-test")


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


def _exp(cov, ref=(), win=28, expect="improves"):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": expect, "because": "b"}


def _reply(beliefs, experiments=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": beliefs, "experiments": list(experiments),
            "final_selection": list(final or []), "conclusion": conclusion}


def _script_replies():
    return [
        _resp(_reply(_beliefs(), [_exp(["X01"]), _exp(["X02"])])),
        _resp(_reply(_beliefs("promising", ["E1"]), [_exp(["X03"], win=14), _exp(["X04"], win=14)])),
        _resp(_reply(_beliefs("promising", ["E3"]), [_exp(["X01"], win=14), _exp(["X02"], win=14)])),
        _resp(_reply(_beliefs("accepted", ["E5"], {"X02": {"status": "rejected", "cites": ["E6"]}}),
                     final=["X01"], conclusion="X01 helps.")),
    ]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(researcher.RESEARCHER, "model_sha256", researcher.sha256_text(TEST_MODEL))


@pytest.fixture(scope="module")
def hidden():
    return observe.hidden_world("4242")


def _obs(w):
    return gen.observed_arrays(w, 126)


def test_the_schema_uses_only_supported_constraints():
    text = json.dumps(researcher.response_schema())
    for word in ("minLength", "maxLength", "minimum", "maximum", "minItems", "maxItems", "pattern"):
        assert word not in text

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node["additionalProperties"] is False and set(node["required"]) == set(node["properties"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(researcher.response_schema())
    assert researcher.system_text().startswith(researcher.BRIEF.rstrip("\n"))


def test_the_hidden_world_follows_the_frozen_rule(hidden):
    again = observe.hidden_world("4242")
    assert np.array_equal(again.y, hidden.y) and again.ids == hidden.ids
    assert 86 <= hidden.tau <= 92 and hidden.n_days == 154 and hidden.form == "linear"
    assert hidden.seed == gen.seed_of(f"{spec.spec_sha()}:4242")
    assert not np.array_equal(observe.hidden_world("4243").y, hidden.y)
    with pytest.raises(ValueError):
        observe.hidden_world("abc")
    obs = _obs(hidden)
    assert executor.arrays_sha256(obs) == gen.arrays_sha256(obs)
    assert all(len(v) == 126 * 24 for v in obs.values())


def test_phase_b_refuses_without_a_published_phase_a_pass(tmp_path):
    def write(verdict, sha):
        body = json.dumps({"phase": "A", "verdict": verdict, "spec_sha": sha}).encode()
        (tmp_path / "verdict.json").write_bytes(body)
        import hashlib
        (tmp_path / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    write("PASS", spec.spec_sha())
    assert observe.phase_a_errors(tmp_path) == []
    write("INSTRUMENT FEASIBILITY FAILED", spec.spec_sha())
    assert observe.phase_a_errors(tmp_path)
    write("PASS", "0" * 64)
    assert observe.phase_a_errors(tmp_path)
    write("PASS", spec.spec_sha())
    (tmp_path / "verdict.json").write_text('{"phase": "A", "verdict": "PASS"}')
    assert any("manifest" in e for e in observe.phase_a_errors(tmp_path))


def test_the_executor_checks_requests_and_reads_only_revealed_days(hidden):
    assert executor.request_errors(_exp(["X01"])) == []
    for bad in (_exp([]), _exp(["X01", "X01"]), _exp(["X09"]), _exp(["X01"], ["X01"]), _exp(["X01"], win=10),
                _exp(["X01"], ["X02", "X03", "X04"]), {"covariates": ["X01"]}):
        assert executor.request_errors(bad), bad
    obs = _obs(hidden)
    lab = executor.Lab(obs, _Inst())
    res = lab.run(_exp(["X01"]), 84, "E1")
    assert res["scored_days"] == [57, 84] and res["block_days"] == 2 and len(res["skill_by_7_days"]) == 4
    assert res["wins"] + res["losses"] + res["ties"] == 28
    poisoned = {k: v.copy() for k, v in obs.items()}
    for v in poisoned.values():
        v[84 * 24:] = np.nan
    again = executor.Lab(poisoned, _Inst()).run(_exp(["X01"]), 84, "E1")
    assert again == res
    assert executor.block_days(7) == 1 and executor.block_days(14) == 2 and executor.block_days(28) == 2
    text = executor.render_result(res)
    assert "scored days 57-84" in text and "nan" not in text.lower()


def test_the_scripted_strategy_follows_the_menu(hidden):
    out = scripted.run(executor.Lab(_obs(hidden), _Inst()))
    reqs = [(e["round"], e["request"]["covariates"], e["request"]["window_days"]) for e in out["experiments"]]
    assert reqs == [(1, ["X01"], 28), (1, ["X02"], 28), (2, ["X03"], 14), (2, ["X04"], 14),
                    (3, ["X01"], 14), (3, ["X02"], 14)]
    latest = {e["request"]["covariates"][0]: e["result"] for e in out["experiments"]}
    assert out["final_selection"] == [c for c in executor.IDS if latest[c]["lo95"] > 0]


def test_the_researcher_loop_records_everything_and_prompts_rebuild(hidden, pinned):
    events = []
    client = _Client(_script_replies())
    r = researcher.Researcher(client, TEST_MODEL, executor.Lab(_obs(hidden), _Inst()), emit=events.append)
    rec = r.run()
    assert rec["final_valid"] and rec["final_selection"] == ["X01"] and len(client.sent) == 4
    assert [len(c["experiments"]) for c in rec["calls"]] == [2, 2, 2, 0]
    assert [e["id"] for c in rec["calls"] for e in c["experiments"]] == ["E1", "E2", "E3", "E4", "E5", "E6"]
    assert researcher.rebuild_mismatches(rec["calls"]) == []
    sent = client.sent[1]
    assert sent["output_config"]["effort"] == "high" and sent["thinking"] == {"type": "adaptive"}
    assert sent["system"][0]["text"] == researcher.system_text()
    assert "E1: covariates [X01]" in sent["messages"][0]["content"] and "Result E1" in sent["messages"][0]["content"]
    assert hidden.canary not in json.dumps(client.sent) and hidden.canary not in json.dumps(events)
    assert {e["event"] for e in events} == {"system", "prompt", "attempt", "experiment", "beliefs"}
    assert [e["user_prompt"] for e in events if e["event"] == "prompt"] == [c["user_prompt"] for c in rec["calls"]]
    assert rec["tokens_used"] == 4 * 1500


def test_an_invalid_response_gets_one_repair_and_then_runs_nothing(hidden, pinned):
    bad = _reply(_beliefs()[:3], [_exp(["X01"])] * 4)
    replies = [_resp(bad), _resp(_reply(_beliefs(), [_exp(["X01"])])),  # call 1: repaired
               _resp("not json"), _resp(bad),  # call 2: invalid twice
               _resp(_reply(_beliefs("promising", ["E1"]), [_exp(["X02"], win=14), _exp(["X03"], win=14)])),
               _resp(_reply(_beliefs("accepted", ["E2"]), final=["X02"], conclusion="X02 helps."))]
    client = _Client(replies)
    rec = researcher.Researcher(client, TEST_MODEL, executor.Lab(_obs(hidden), _Inst())).run()
    c1, c2 = rec["calls"][0], rec["calls"][1]
    assert c1["valid"] and len(c1["attempts"]) == 2 and "repair_prompt" in c1["attempts"][1]
    assert "exactly one row" in c1["attempts"][1]["repair_prompt"] and "at most 3" in c1["attempts"][1]["repair_prompt"]
    assert not c2["valid"] and c2["experiments"] == [] and len(c2["attempts"]) == 2
    assert client.sent[1]["messages"][1] == {"role": "assistant", "content": json.dumps(bad)}
    assert researcher.rebuild_mismatches(rec["calls"]) == []
    assert "No valid response after one repair" in rec["calls"][2]["user_prompt"]


def test_the_checks_enforce_the_menu(pinned):
    step1, final = researcher.call_plan()[0], researcher.call_plan()[-1]
    good = _reply(_beliefs(), [_exp(["X01"])])
    assert researcher.response_errors(good, step1, []) == []
    assert researcher.response_errors(_reply(_beliefs("promising", ["E1"])), step1, [])  # unknown cite
    assert researcher.response_errors(dict(good, conclusion="x"), step1, [])
    assert researcher.response_errors(dict(good, notes="x" * 1501), step1, [])
    assert researcher.response_errors(_reply(_beliefs(), [_exp(["X01"])], final=["X01"], conclusion="c"), final, [])
    assert researcher.response_errors(_reply(_beliefs(), final=[], conclusion=""), final, [])
    assert researcher.response_errors(_reply(_beliefs(), final=[], conclusion="none helps"), final, []) == []
    spent = [{"experiments": [{"id": f"E{i}"} for i in range(1, 6)]}]
    assert researcher.response_errors(_reply(_beliefs(), [_exp(["X01"]), _exp(["X02"])]), step1, spent)
    assert researcher.attempt_errors("{}", "max_tokens", step1, [])[0] == ["the response was cut off at the output limit"]


def test_the_token_cap_and_the_model_hash_are_enforced(hidden, pinned):
    lab = executor.Lab(_obs(hidden), _Inst())
    with pytest.raises(researcher.IntegrityError):
        researcher.Researcher(_Client([]), "another-model", lab)
    client = _Client([_resp(_reply(_beliefs(), [_exp(["X01"])]), model="another-model")])
    with pytest.raises(researcher.IntegrityError):
        researcher.Researcher(client, TEST_MODEL, lab).run()
    huge = [_resp(_reply(_beliefs(), [_exp(["X01"])]), tokens=50000)]
    client = _Client(huge)
    rec = researcher.Researcher(client, TEST_MODEL, lab).run()
    assert len(client.sent) == 1 and rec["tokens_used"] == 75000 and not rec["final_valid"]
    assert all("token cap" in c["errors"][0] for c in rec["calls"][1:])
    assert all(kw["max_tokens"] <= researcher.MAX_TOKENS for kw in client.sent)


def _calls_for(roles, results):
    """A notebook: call 1 marks R promising, call 2 tests E and marks R deteriorated citing a post-change result."""
    def res(i, cov, lo, last):
        return {"id": f"E{i}", "request": {**_exp(cov), "because": "b"},
                "result": {"id": f"E{i}", "covariates": cov, "reference": [], "skill": lo + 0.05, "lo95": lo,
                           "hi95": lo + 0.1, "scored_days": [last - 27, last]}}
    r, e = roles["R"], roles["E"]
    b1 = _beliefs()
    b2 = _beliefs(overrides={r: {"status": "promising", "cites": ["E1"]}})
    b3 = _beliefs(overrides={r: {"status": "deteriorated", "cites": ["E3"]}, e: {"status": "promising", "cites": ["E2"]}})
    b4 = _beliefs(overrides={r: {"status": "rejected", "cites": ["E3"]}, e: {"status": "accepted", "cites": ["E2"]}})
    return [
        {"call": 1, "round": 1, "cutoff": 84, "final": False, "valid": True, "attempts": [],
         "response": _reply(b1, [_exp([r])]), "experiments": [res(1, [r], 0.1, 84)]},
        {"call": 2, "round": 2, "cutoff": 112, "final": False, "valid": True, "attempts": [],
         "response": _reply(b2, [_exp([e]), _exp([r])]), "experiments": [res(2, [e], results["E"], 112),
                                                                         res(3, [r], results["R"], 112)]},
        {"call": 3, "round": 3, "cutoff": 126, "final": False, "valid": True, "attempts": [],
         "response": _reply(b3), "experiments": []},
        {"call": 4, "round": None, "cutoff": 126, "final": True, "valid": True, "attempts": [],
         "response": _reply(b4, final=[e], conclusion="c"), "experiments": []},
    ]


def test_behaviours_and_the_verdict_map(hidden):
    roles = {k: hidden.ids[k] for k in ("R", "E", "D", "N")}
    calls = _calls_for(roles, {"E": 0.2, "R": -0.05})
    beh = evaluate.behaviours(calls, roles, hidden.tau)
    assert beh["B1"] and beh["B2"] and beh["B3"] and beh["B5"] and beh["B7"] and beh["B8"]
    assert not beh["B6"]  # nothing is tested after the negative result E3
    more = _calls_for(roles, {"E": 0.2, "R": -0.05})
    d = roles["D"]
    more[2]["experiments"] = [{"id": "E4", "request": _exp([d], win=14),
                               "result": {"id": "E4", "covariates": [d], "reference": [], "skill": 0.1, "lo95": 0.02,
                                          "hi95": 0.2, "scored_days": [113, 126]}}]
    assert evaluate.behaviours(more, roles, hidden.tau)["B6"]
    ai = {"calls": calls, "final_valid": True, "final_selection": [roles["E"]]}
    ev = {"E_days_99_126": {"lo95": 0.1}, "R_days_57_84": {"lo95": 0.1}}
    good = {"t0": {"lo95": 0.05}}
    assert evaluate.verdict([], True, ai, beh, roles, ev, good)[0] == "BASIC LOOP FEASIBLE"
    assert evaluate.verdict(["x"], True, ai, beh, roles, ev, good)[0].startswith("INTEGRITY FAILURE")
    assert evaluate.verdict([], True, ai, beh, roles, ev, {"t0": {"lo95": -0.01}})[0] == "AMBIGUOUS"
    with_r = dict(ai, final_selection=[roles["E"], roles["R"]])
    assert evaluate.verdict([], True, with_r, beh, roles, ev, good)[0] == "RESEARCHER FEASIBILITY FAILED"
    with_n = dict(ai, final_selection=[roles["E"], roles["N"]])
    assert evaluate.verdict([], True, with_n, beh, roles, ev, good)[0] == "RESEARCHER FEASIBILITY FAILED"
    assert evaluate.verdict([], True, dict(ai, final_valid=False), beh, roles, ev, good)[0] == \
        "RESEARCHER FEASIBILITY FAILED"
    wrong = _calls_for(roles, {"E": 0.2, "R": -0.05})
    wrong[3]["response"]["beliefs"] = _beliefs("accepted", [], {roles["R"]: {"status": "accepted", "cites": ["E3"]}})
    wrong[2]["response"]["beliefs"] = _beliefs(overrides={roles["R"]: {"status": "accepted", "cites": ["E3"]}})
    beh2 = evaluate.behaviours(wrong, roles, hidden.tau)
    assert len(beh2["B3_errors"]) >= 2
    assert evaluate.verdict([], True, ai, beh2, roles, ev, good)[0] == "RESEARCHER FEASIBILITY FAILED"


def test_phase_b_runs_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned):
    pytest.importorskip("t0")
    from research_loop_proof.phase0.lab import run as lab_run

    monkeypatch.setattr(lab_run, "load_t0", lambda weights: (phase_a.fake_model()[0], {"fake": True}))
    phase_a_dir = tmp_path / "phase_a"
    phase_a_dir.mkdir()
    body = json.dumps({"phase": "A", "verdict": "PASS", "spec_sha": spec.spec_sha()}).encode()
    (phase_a_dir / "verdict.json").write_bytes(body)
    import hashlib
    (phase_a_dir / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    assert observe.main(["--run-id", "777", "--phase-a-dir", str(phase_a_dir), "--out", str(tmp_path / "obs")]) == 0
    meta = json.loads((tmp_path / "obs" / "observed.json").read_text())
    assert set(meta) == {"spec_sha", "run_id", "days", "keys", "arrays_sha256"}
    research = tmp_path / "research"
    args = ["--observed", str(tmp_path / "obs" / "observed.npz"), "--observed-sha", meta["arrays_sha256"],
            "--weights", "unused", "--out", str(research)]
    assert lab_run.main(["scripted", *args]) == 0
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: _Client(_script_replies()))
    assert lab_run.main(["loop", *args]) == 0
    (research / "guard.json").write_text('{"truth_absent": true, "git_removed": true}')
    assert json.loads((research / "integrity.json").read_text()) == {"failure": None}
    out = tmp_path / "out"
    assert evaluate.main(["--run-id", "777", "--phase-a-dir", str(phase_a_dir), "--observed", str(tmp_path / "obs"),
                          "--research", str(research), "--weights", "unused", "--out", str(out)]) == 0
    rec = json.loads((out / "evaluation.json").read_text())
    assert rec["integrity"]["issues"] == [] and rec["integrity"]["experiments_recomputed"] == 6
    assert rec["verdict"] in ("RESEARCHER FEASIBILITY FAILED", "BASIC LOOP FEASIBLE", "AMBIGUOUS")
    assert (out / "REPORT.md").read_text().startswith(f"# Phase B result: {rec['verdict']}")
    assert set(rec["confirmation"]) >= {"{E} vs {}", "D given E ({E, D} vs {E})", "E given D ({E, D} vs {D})"}
    assert {(out / n).is_file() for n in ("notebook.jsonl", "ai.json", "scripted.json", "verdict.json")} == {True}
    # a tampered prompt, a missing guard and an absent research record are each integrity failures
    ai = json.loads((research / "ai.json").read_text())
    ai["calls"][1]["user_prompt"] += " extra"
    (research / "ai.json").write_text(json.dumps(ai))
    (research / "guard.json").unlink()
    evaluate.main(["--run-id", "777", "--phase-a-dir", str(phase_a_dir), "--observed", str(tmp_path / "obs"),
                   "--research", str(research), "--weights", "unused", "--out", str(tmp_path / "out2")])
    rec2 = json.loads((tmp_path / "out2" / "evaluation.json").read_text())
    assert rec2["verdict"] == "INTEGRITY FAILURE (no verdict)"
    assert any("prompt-rebuild" in i for i in rec2["integrity"]["issues"])
    assert any("guard" in i for i in rec2["integrity"]["issues"])
    empty = tmp_path / "empty"
    empty.mkdir()
    evaluate.main(["--run-id", "777", "--phase-a-dir", str(phase_a_dir), "--observed", str(tmp_path / "obs"),
                   "--research", str(empty), "--weights", "unused", "--out", str(tmp_path / "out3")])
    rec3 = json.loads((tmp_path / "out3" / "evaluation.json").read_text())
    assert rec3["verdict"] == "INTEGRITY FAILURE (no verdict)"
