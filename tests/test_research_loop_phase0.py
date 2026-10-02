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
        "bb71c29967eaac748574913fb80d75b004395dfaa15b1c7bb4257a5e152e4ad4",
    "research_loop_proof/phase0/truth/world.json":
        "8f24652964b76147ae5535f7c7dafc3f2c0e95d95182ea6b621fce1410990cc7",
    "research_loop_proof/phase0/truth/generator.py":
        "12d524bac4933231ef4957fed33e1e9cb4779e9a680fd03d5659f2123b93bb28",
    "research_loop_proof/phase0/truth/calibrate.py":
        "3dd491e25849acbe50b92f26ae1ca279563a1dad27e176525e988adbbaabdd27",
    "research_loop_proof/phase0/lab/menu.json":
        "72bb74167e4f70c978edd428dcd5c49aa8db13b6f1902bc071839c6db383148d",
    "research_loop_proof/phase0/lab/brief.md":
        "5d004eacde766e1a1c203b0200f8363ba28fb1516f01599c878c31b440dcfb2f",
}
SPEC_SHA = "6bebad3a8fb16855acbdc1afe107101c97ea0bcd04f0dc5a5d8d32a2b0d03dda"


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

    for r in gen.ROLES:  # standardised on pre-change days only
        assert abs(w.x[r][pre].mean()) < 1e-12 and abs(w.x[r][pre].std() - 1) < 1e-12
    assert abs(corr(w.x["D"], w.x["E"]) - 0.8) < 0.06
    # two independent persistent series can correlate by about +-0.15 over 200 days, hence the loose bounds
    assert corr(w.y[pre], w.x["R"][pre]) > 0.6 and abs(corr(w.y[post], w.x["R"][post])) < 0.3
    assert abs(corr(w.y[pre], w.x["E"][pre])) < 0.3 and corr(w.y[post], w.x["E"][post]) > 0.6
    assert abs(corr(w.y[pre], w.x["N"][pre])) < 0.3 and abs(corr(w.y[post], w.x["N"][post])) < 0.3
    assert 0.75 < w.y[post].var() / w.y[pre].var() < 1.3


def test_the_change_starts_at_midnight_of_day_tau():
    w = gen.make_world(7, n_days=40, tau=20, form="linear", m=2.0)
    w0 = gen.make_world(7, n_days=40, tau=20, form="linear", m=0.0)
    effect = w.y - w0.y
    c = np.sqrt(0.75 * 2.0)
    assert np.allclose(effect[: 19 * 24], c * w.x["R"][: 19 * 24])
    assert np.allclose(effect[19 * 24:], c * w.x["E"][19 * 24:])


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


def test_phase_a_runs_end_to_end_with_a_tiny_untrained_t0(tmp_path):
    pytest.importorskip("t0")
    smoke = phase_a.run(tmp_path / "smoke", fake=True, smoke=True)
    assert smoke["calibration_reproduced"] and smoke["finite"] and smoke["sanitised"] == 0
    assert "verdict" not in smoke and "criteria" not in smoke
    rec = phase_a.run(tmp_path / "run", fake=True)
    assert rec["integrity"] == {"calibration_reproduced": True, "sanitised_outputs": 0, "poison": True}
    assert rec["t0_forecast_days"] == 40 * 21 * 3 + 12 * 21 * 2 + 8 * 42 * 2
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
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["smoke", "phaseA"]
    assert wf["permissions"] == {}


def test_only_publish_writes_and_it_holds_no_secret(wf):
    jobs = wf["jobs"]
    assert set(jobs) == {"phase_a", "publish"}
    assert jobs["phase_a"]["permissions"] == {"contents": "read"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    pub = json.dumps(jobs["publish"])
    assert "secrets." not in pub and "actions/checkout" not in pub
    assert "ls-remote --exit-code" in pub and "phase0/run-${{ github.run_id }}" in pub
    assert "sha256sum -c MANIFEST.sha256" in pub and "needs.phase_a.outputs.manifest_sha256" in pub


def test_secrets_are_scoped_to_the_one_step_that_needs_them(wf):
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "ANTHROPIC" not in text and "actions/cache" not in text
    steps = wf["jobs"]["phase_a"]["steps"]
    with_secret = [s for s in steps if "secrets." in json.dumps(s)]
    assert len(with_secret) == 1 and with_secret[0]["env"]["HF_TOKEN"] == "${{ secrets.HF_TOKEN }}"
    assert "research_loop_proof.phase0.truth.phase_a" in with_secret[0]["run"]
    checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout"))
    assert checkout["with"]["persist-credentials"] is False
    assert any("tests/test_research_loop_phase0.py" in s.get("run", "") for s in steps)
