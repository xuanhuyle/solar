"""Kernel1 (docs/research_loop_proof/NEXT_KERNEL_PROOF_PROMPT.md): Discovery1's researcher L8 unchanged on twelve hidden
worlds (8 change, 2 stable, 2 null). Kernel identity, the world kinds, truth separation, the scoring rules, the
programme reading, the evaluator end to end with stand-ins, the workflow and the freeze. Parts that need anthropic skip
without it."""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.discovery1.lab import executor as dex
from research_loop_proof.discovery1.lab import researcher as dres
from research_loop_proof.discovery1.truth import spec as dspec
from research_loop_proof.discovery1.truth import world as dworld
from research_loop_proof.kernel1.truth import evaluate as kev
from research_loop_proof.kernel1.truth import observe as kobs
from research_loop_proof.kernel1.truth import preflight as kpre
from research_loop_proof.kernel1.truth import rules
from research_loop_proof.kernel1.truth import spec as kspec
from research_loop_proof.kernel1.truth import world as kworld
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "kernel1"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-kernel1.yml"
TEST_MODEL = "test-model-id"
IDS8 = dex.IDS8
WORLDS = kworld.SCORED_WORLDS
H = 24


# ----------------------------------------------------------------- fakes

class _Inst:
    rows = sanitised = 0

    def forecast(self, requests):
        self.rows += len(requests)
        return [ctx[-24:] + (0 if b is None else 0.3 * b[:, -24:].sum(0)) for ctx, b in requests]


class _Leaky(dex.Lab8):
    """A lab that reads past its cutoff: the poison test must catch it."""

    def _forecasts(self, ids, days, cutoff):
        out = super()._forecasts(ids, days, cutoff)
        future = np.nan_to_num(self.y[cutoff * H:])
        bump = 1e-3 * float(future.mean()) if future.size else 0.0
        return {d: f + bump for d, f in out.items()}


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


def _req(cov, ref=(), win=28):
    return {"covariates": list(cov), "reference": list(ref), "window_days": win, "expect": "improves", "because": "b"}


def _reply(rows, exps=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": rows, "experiments": list(exps), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies(final=("X07",)):
    return [_resp(_reply(_rows(), [_req(IDS8[:4]), _req(IDS8[4:])])),
            _resp(_reply(_rows("promising", ["E1"]), [_req(IDS8[4:6], win=14), _req(IDS8[6:], win=14)])),
            _resp(_reply(_rows("promising", ["E3"]), [_req(["X07"], win=14), _req(["X08"], ["X07"], win=14)])),
            _resp(_reply(_rows("accepted", ["E5"], {"X08": {"status": "rejected", "cites": ["E6"]}}),
                         final=list(final), conclusion="X07 helps; E6 showed X08 adds nothing."))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def unfrozen_ok(monkeypatch):
    monkeypatch.setattr(kspec, "missing", lambda root=None: [])


@pytest.fixture()
def fake_t0(monkeypatch):
    from research_loop_proof.beta1.lab import run as brun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (object(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setattr(t0_beta, "BetaT0", lambda model: _Inst())


def _e(i, call, cov, ref=(), lo=0.1, first=113, win=14):
    return {"id": f"E{i}", "call": call, "round": min(call, 3), "cutoff": first + win - 1,
            "request": {"covariates": list(cov), "reference": list(ref), "window_days": win},
            "result": {"scored_days": [first, first + win - 1], "lo95": lo, "skill": lo + 0.1, "hi95": lo + 0.2}}


# ----------------------------------------------------------------- the kernel is Discovery1's L8, unchanged

def test_kernel1_has_no_lab_code_and_reuses_discovery1s_research_job():
    assert not (PKG / "lab").exists()
    assert set(dspec.FROZEN) <= set(kspec.FROZEN)
    assert ".github/workflows/research-loop-kernel1.yml" in kspec.FROZEN
    assert "research_loop_proof/beta1/truth/preflight.py" in kspec.FROZEN
    assert p0res.sha256_text(dres.system_text8()) == kev.L8_SYSTEM_SHA256 == \
        "78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d"
    assert p0res.sha256_text(lres.frozen_lesson()) == kev.LESSON_SHA256
    assert kev.LESSON_SHA256.startswith("1c38b101")


def test_the_truth_package_never_feeds_the_research_job():
    for path in (PKG / "truth").glob("*.py"):
        assert not re.search(r"^def (make_world|pair_world)", path.read_text(encoding="utf-8"), re.MULTILINE), path
    assert re.search(r"^def kernel_world", (PKG / "truth" / "world.py").read_text(encoding="utf-8"), re.MULTILINE)


# ----------------------------------------------------------------- worlds

def test_the_three_kinds_share_candidates_and_follow_their_frozen_targets():
    for seed in (1, 98765, 2 ** 40 + 3):
        b = dworld.make_world8(seed)
        c = kworld.effect_scale(b.m)
        zr, ze = b.signs["R"] * b.x["R"], b.signs["E"] * b.x["E"]
        before = np.arange(b.n_days * H) < (b.tau - 1) * H
        no_effect = b.y - c * np.where(before, zr, ze)
        w = {k: kworld.kernel_world(seed, k) for k in kworld.KINDS}
        assert np.array_equal(w["change"].y, b.y)
        assert np.allclose(w["stable"].y, no_effect + c * zr, rtol=0, atol=1e-12)
        zu = kworld.unobserved(seed, b.n_days, b.tau)
        assert np.allclose(w["null"].y, no_effect + c * zu, rtol=0, atol=1e-12)
        assert np.allclose(w["stable"].y[before], b.y[before], rtol=0, atol=1e-12)
        pre = slice(0, (b.tau - 1) * H)
        assert abs(zu[pre].mean()) < 1e-12 and abs(zu[pre].std() - 1) < 1e-12
        assert all(not np.allclose(zu, b.signs[r] * b.x[r]) for r in dworld.ROLES8)
        for k in kworld.KINDS:
            assert w[k].tau == b.tau and w[k].ids == b.ids and w[k].signs == b.signs
            assert all(np.array_equal(w[k].x[r], b.x[r]) for r in dworld.ROLES8)
            assert w[k].canary.startswith("CANARY-") and w[k].canary != b.canary
            assert kev.generator_defects(w[k], k) == []
        assert kev.generator_defects(w["stable"], "null") and kev.generator_defects(w["null"], "change")


def test_the_unobserved_stream_leaves_make_world8s_streams_unchanged():
    for seed in (5, 77):
        assert [c.spawn_key for c in np.random.SeedSequence(seed).spawn(8)[:7]] == \
            [c.spawn_key for c in np.random.SeedSequence(seed).spawn(7)]


def test_the_null_target_keeps_the_scale_of_the_other_kinds():
    obs = slice(0, 126 * H)
    var = {k: np.mean([kworld.kernel_world(s, k).y[obs].var() for s in range(30)]) for k in kworld.KINDS}
    assert 0.8 < var["null"] / var["change"] < 1.25 and 0.8 < var["stable"] / var["change"] < 1.25


def test_kinds_are_eight_two_two_and_depend_on_the_spec_and_the_run():
    perms = set()
    for run in ("100", "101", "102", "103", "104"):
        k = kworld.world_kinds("specsha", run)
        assert list(k) == list(WORLDS) and sorted(Counter(k.values()).items()) == sorted(kworld.COMPOSITION)
        assert k == kworld.world_kinds("specsha", run)
        perms.add(tuple(k.values()))
    assert len(perms) > 1


def test_seeds_come_from_the_spec_hash_the_run_and_the_world(monkeypatch, unfrozen_ok):
    monkeypatch.setattr(kspec, "spec_sha", lambda root=None: "S")
    w = kobs.hidden_world("123", "w05")
    assert w.seed == gen.seed_of("kernel1:S:123:w05")
    assert kobs.kinds("123") == kworld.world_kinds("S", "123")
    assert kobs.preflight_world("123").seed == gen.seed_of("kernel1-preflight:123")
    with pytest.raises(ValueError):
        kobs.hidden_world("abc", "w01")
    with pytest.raises(ValueError):
        kobs.hidden_world("123", "w13")


def test_observe_exports_only_neutral_per_world_data(tmp_path, unfrozen_ok):
    assert kobs.main(["--mode", "preflight", "--run-id", "7", "--run-attempt", "1", "--out", str(tmp_path)]) == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["shas.env", "w01"]
    meta = json.loads((tmp_path / "w01" / "observed.json").read_text())
    assert set(meta) == {"world", "days", "keys", "arrays_sha256"} and meta["keys"] == sorted(["y", *IDS8])
    with np.load(tmp_path / "w01" / "observed.npz") as z:
        assert all(len(z[k]) == 126 * H for k in z.files)
        assert gen.arrays_sha256({k: z[k] for k in z.files}) == meta["arrays_sha256"]
    blob = b"".join(p.read_bytes() for p in tmp_path.rglob("*") if p.is_file())
    w = kobs.preflight_world("7")
    assert w.canary.encode() not in blob and b"change" not in blob and b"kernel1" not in blob
    assert (tmp_path / "shas.env").read_text() == f"w01={meta['arrays_sha256']}\n"


def _published(d: Path, phase="kernel1-preflight", verdict="PASS", sha=None):
    d.mkdir(parents=True, exist_ok=True)
    body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha or kspec.spec_sha()}).encode()
    (d / "verdict.json").write_bytes(body)
    (d / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")


def test_the_scored_run_is_refused_on_a_rerun_or_a_second_batch(tmp_path, monkeypatch, unfrozen_ok):
    _published(tmp_path / "pre")
    (tmp_path / "pub").mkdir()
    assert kobs.refusals("run", "1", str(tmp_path / "pre"), str(tmp_path / "pub")) == []
    assert any("attempt 2" in e for e in kobs.refusals("run", "2", str(tmp_path / "pre"), str(tmp_path / "pub")))
    assert kobs.refusals("run", "1", str(tmp_path / "pre"), None)
    assert kobs.refusals("run", "1", str(tmp_path / "missing"), str(tmp_path / "pub"))
    _published(tmp_path / "pub" / "555", phase="kernel1-preflight")
    assert kobs.refusals("run", "1", str(tmp_path / "pre"), str(tmp_path / "pub")) == []
    (tmp_path / "pub" / "556").mkdir()
    (tmp_path / "pub" / "556" / "verdict.json").write_text(json.dumps({"phase": "kernel1-run"}))
    assert any("already published: 556" in e for e in kobs.refusals("run", "1", str(tmp_path / "pre"),
                                                                     str(tmp_path / "pub")))
    _published(tmp_path / "old", sha="0" * 64)
    assert kobs.refusals("run", "1", str(tmp_path / "old"), str(tmp_path / "pub"))
    assert kobs.refusals("preflight", "3", None, None) == []


# ----------------------------------------------------------------- support

def test_direct_support_by_the_exact_set_or_by_every_member_alone():
    assert rules.support([_e(1, 2, ["X01", "X02"], ["X03"])], ["X02", "X01"], "change", 90)["supported"]
    s = rules.support([_e(1, 2, ["X01"]), _e(2, 2, ["X02"], ["X05"])], ["X01", "X02"], "change", 90)
    assert s["supported"] and s["chain"] == ["E1", "E2"]
    assert not rules.support([_e(1, 2, ["X01"])], ["X01", "X02"], "change", 90)["supported"]
    assert not rules.support([_e(1, 2, ["X01"], lo=0.0)], ["X01"], "change", 90)["supported"]
    assert not rules.support([_e(1, 2, ["X01", "X02"])], [], "change", 90)["supported"]
    assert not rules.support([_e(1, 2, ["X01", "X02"])], None, "change", 90)["supported"]


def test_only_current_regime_experiments_support_in_change_worlds():
    straddle = _e(1, 2, ["X01"], first=85, win=28)
    assert not rules.support([straddle], ["X01"], "change", 86)["supported"]
    assert rules.support([straddle], ["X01"], "stable", 86)["supported"]
    assert rules.support([_e(1, 1, ["X01"], first=57, win=28)], ["X01"], "stable", 92)["supported"]
    assert rules.support([_e(1, 2, ["X01"], first=99, win=14)], ["X01"], "change", 92)["supported"]
    assert not rules.support([_e(1, 2, ["X01"], first=99, win=14)], ["X01"], "change", 100)["supported"]


def test_support_by_elimination_needs_a_later_call_and_a_reference_within_the_final_set():
    pos = _e(1, 2, ["X01", "X02"])
    s = rules.support([pos, _e(2, 3, ["X02"], ["X01"], lo=-0.05)], ["X01"], "change", 90)
    assert s == {"supported": True, "how": "elimination", "chain": ["E1", "E2"]}
    assert not rules.support([pos, _e(2, 2, ["X02"], ["X01"], lo=-0.05)], ["X01"], "change", 90)["supported"]
    assert not rules.support([_e(2, 2, ["X02"], ["X01"], lo=-0.05), _e(3, 3, ["X01", "X02"])], ["X01"], "change",
                             90)["supported"]
    assert rules.support([pos, _e(2, 3, ["X02"], ["X01"], lo=0.0)], ["X01"], "change", 90)["supported"]
    assert not rules.support([pos, _e(2, 3, ["X02"], ["X01"], lo=0.01)], ["X01"], "change", 90)["supported"]
    assert not rules.support([pos, _e(2, 3, ["X02"], [], lo=-0.05)], ["X01"], "change", 90)["supported"]
    assert not rules.support([pos, _e(2, 3, ["X02"], ["X03"], lo=-0.05)], ["X01"], "change", 90)["supported"]
    assert not rules.support([pos, _e(2, 3, ["X02", "X01"], [], lo=-0.05)], ["X01"], "change", 90)["supported"]
    three = _e(1, 2, ["X01", "X02", "X03"])
    assert not rules.support([three, _e(2, 3, ["X02"], ["X01"], lo=-0.1)], ["X01"], "change", 90)["supported"]
    s = rules.support([three, _e(2, 3, ["X02", "X03"], ["X01"], lo=-0.1)], ["X01"], "change", 90)
    assert s["supported"] and s["chain"] == ["E1", "E2"]
    s = rules.support([three, _e(2, 3, ["X03"], ["X01", "X02"], lo=-0.1)], ["X01", "X02"], "change", 90)
    assert s["supported"] and s["chain"] == ["E1", "E2"]
    assert not rules.support([_e(1, 2, ["X01", "X02"], first=85, win=28), _e(2, 3, ["X02"], ["X01"], lo=-0.1)],
                             ["X01"], "change", 86)["supported"]


def test_support_is_a_pure_deterministic_function():
    exps = [_e(1, 2, ["X01", "X02"]), _e(2, 3, ["X02"], ["X01"], lo=-0.1), _e(3, 3, ["X01"])]
    assert rules.support(exps, ["X01"], "change", 90) == rules.support(list(exps), ["X01"], "change", 90)
    assert rules.support(exps, ["X01"], "change", 90)["how"].startswith("direct")
    assert set(inspect.signature(rules.support).parameters) == {"exps", "selection", "kind", "tau"}


# ----------------------------------------------------------------- oracle, success, programme

def test_the_oracle_is_the_lowest_mae_set_with_a_positive_lower_bound():
    rows = {"{E}": {"lo95": 0.05, "candidate_mae": 1.0, "size": 1, "ids": ["X03"]},
            "{D}": {"lo95": 0.02, "candidate_mae": 0.9, "size": 1, "ids": ["X05"]},
            "{E, D}": {"lo95": -0.01, "candidate_mae": 0.8, "size": 2, "ids": ["X03", "X05"]}}
    assert rules.oracle(rows) == "{D}"
    rows["{D}"]["candidate_mae"] = 1.0
    assert rules.oracle(rows) == "{E}"
    rows["{E, D}"]["lo95"], rows["{E, D}"]["candidate_mae"] = 0.1, 1.0
    assert rules.oracle(rows) == "{E}"
    assert rules.oracle({k: dict(v, lo95=0.0) for k, v in rows.items()}) is None
    assert rules.oracle_fraction(0.2, 0.25) == pytest.approx(0.8)
    assert rules.oracle_fraction(None, 0.25) == 0.0 and rules.oracle_fraction(-0.1, 0.2) == pytest.approx(-0.5)
    assert rules.median([0.9, 0.7, 0.8]) == 0.8 and rules.median([0.7, 0.9, 0.8, 1.0]) == pytest.approx(0.85)
    assert rules.scorable(["X01"] * 4) and not rules.scorable(["X01"] * 5) and not rules.scorable([])


ROLES = {"R": "X01", "E": "X02", "D": "X03", "N1": "X04", "N2": "X05", "N3": "X06", "N4": "X07", "N5": "X08"}


def _succ(kind, **kw):
    base = dict(final_valid=True, informative=True, selection=["X02"], roles=ROLES, supported=True, confirm_lo95=0.1,
                fraction=0.9, statuses={})
    base.update(kw)
    return rules.success(kind, **base)


def test_per_world_success_follows_the_owners_criteria():
    assert _succ("change")["success"] and _succ("change", selection=["X03"])["success"]
    assert _succ("change", selection=["X02", "X03"])["success"]
    assert _succ("change", selection=["X02", "X01"])["failed"] == ["3_r_absent"]
    assert _succ("change", selection=["X02", "X04"])["failed"] == ["4_no_pure_noise"]
    assert _succ("change", selection=[])["failed"] == ["2_selection_non_empty"]
    assert _succ("change", supported=False)["failed"] == ["5_supported_by_own_current_evidence"]
    assert _succ("change", confirm_lo95=0.0)["failed"] == ["6_confirmation_lower_bound_above_0"]
    assert _succ("change", fraction=0.69)["failed"] == ["7_oracle_fraction_at_least_0.70"]
    assert _succ("change", fraction=0.70)["success"]
    assert _succ("change", informative=False)["failed"] == ["1_informative"]
    assert "0_valid_final_response" in _succ("change", final_valid=False)["failed"]
    assert _succ("stable", selection=["X01"])["success"]
    assert _succ("stable", selection=["X01", "X02"])["success"]  # a zero-effect extra is not pure noise
    assert _succ("stable", selection=["X01", "X08"])["failed"] == ["3_no_pure_noise"]
    assert _succ("null", selection=[], statuses={"X01": "promising"})["success"]
    assert set(_succ("null", selection=["X01"])["failed"]) == {"1_selection_empty",
                                                                "3_no_candidate_presented_as_established"}
    assert set(_succ("null", selection=[], statuses={"X04": "accepted"})["failed"]) == {
        "2_no_final_status_accepted", "3_no_candidate_presented_as_established"}
    assert _succ("null", selection=[], final_valid=False)["failed"] == ["0_valid_final_response"]


def _worlds(**over):
    kinds = ["change"] * 8 + ["stable"] * 2 + ["null"] * 2
    ws = {k: {"kind": kind, "final_valid": True, "informative": None if kind == "null" else True, "success": True,
              "oracle_fraction": None if kind == "null" else 0.9, "noise_selected": [], "accepted": []}
          for k, kind in zip(WORLDS, kinds)}
    for key, val in over.items():
        k, field = key.split("__")
        ws[k][field] = val
    return ws


def test_every_programme_row_is_reachable_with_its_closing_line():
    def label(ws, material=(), defects=()):
        return rules.programme(ws, list(material), list(defects))[0]
    assert label(_worlds()) == "KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_worlds(), material=["w01: canary"]) == "INFRASTRUCTURE FAILURE"
    assert label(_worlds(w01__final_valid=False, w11__final_valid=False)) == "INFRASTRUCTURE FAILURE"
    assert label(_worlds(w01__final_valid=False, w01__success=False)) == "KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_worlds(w01__informative=False, w02__informative=False)) == "KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_worlds(w01__informative=False, w02__informative=False, w03__informative=False)) == \
        "BENCHMARK FAILURE"
    assert label(_worlds(w09__informative=False)) == "BENCHMARK FAILURE"
    assert label(_worlds(), defects=["w01: target"]) == "BENCHMARK FAILURE"
    assert label(_worlds(w01__success=False, w02__success=False)) == "KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_worlds(w01__success=False, w02__success=False, w03__success=False)) == "KERNEL NOT PROVEN"
    assert label(_worlds(w09__success=False)) == "KERNEL NOT PROVEN"
    assert label(_worlds(w12__success=False)) == "KERNEL NOT PROVEN"
    assert label(_worlds(w12__accepted=["X01"])) == "KERNEL NOT PROVEN"
    assert label(_worlds(w01__noise_selected=["X04"])) == "KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_worlds(w01__noise_selected=["X04"], w09__noise_selected=["X05"])) == "KERNEL NOT PROVEN"
    low = {f"{k}__oracle_fraction": 0.5 for k in WORLDS[:4]}  # ten fractions: median (0.9 + 0.9) / 2
    assert label(_worlds(**low)) == "KERNEL PROVEN FOR THIS BENCHMARK"
    lower = {f"{k}__oracle_fraction": 0.5 for k in WORLDS[:5]}  # median (0.5 + 0.9) / 2 = 0.7
    assert label(_worlds(**lower)) == "KERNEL NOT PROVEN"
    assert rules.CLOSING == {"INFRASTRUCTURE FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
                             "BENCHMARK FAILURE": "BENCHMARK/INFRASTRUCTURE RESULT ONLY",
                             "KERNEL PROVEN FOR THIS BENCHMARK": "MOVE THE CURRENT KERNEL TO A REAL-WORLD RESEARCH TEST",
                             "KERNEL NOT PROVEN": "STOP SYNTHETIC RESCUE OF THE CURRENT KERNEL"}
    owner = (ROOT / "docs/research_loop_proof/NEXT_KERNEL_PROOF_PROMPT.md").read_text(encoding="utf-8")
    assert all(f"`{line}`" in owner for line in rules.CLOSING.values())


def test_the_median_threshold_is_applied_over_informative_non_null_worlds():
    ws = _worlds(**{f"{k}__oracle_fraction": 0.79 for k in WORLDS[:10]})
    assert rules.programme(ws, [], [])[0] == "KERNEL NOT PROVEN"
    ws = _worlds(**{f"{k}__oracle_fraction": 0.80 for k in WORLDS[:10]})
    assert rules.programme(ws, [], [])[0] == "KERNEL PROVEN FOR THIS BENCHMARK"
    ws = _worlds(**{f"{k}__oracle_fraction": 0.1 for k in WORLDS[:2]}, w01__informative=False,
                 w02__informative=False, **{f"{k}__oracle_fraction": 0.80 for k in WORLDS[2:10]})
    assert rules.programme(ws, [], [])[0] == "KERNEL PROVEN FOR THIS BENCHMARK"


# ----------------------------------------------------------------- informativeness and integrity

def test_informativeness_reads_only_the_world_and_the_instrument():
    assert list(inspect.signature(kev.informativeness).parameters) == ["w", "kind", "model", "confirmer"]


def test_informativeness_per_kind_with_a_stand_in(fake_t0):
    for kind in kworld.KINDS:
        w = kworld.kernel_world(424242, kind)
        inf = kev.informativeness(w, kind, object(), kev.Confirmer(w, object()))
        assert set(inf["confirmation"]) == {"{E} vs {}", "{D} vs {}", "{R} vs {}", "{E, D} vs {}",
                                            "D given E ({E, D} vs {E})", "E given D ({E, D} vs {D})",
                                            "R given E ({E, R} vs {E})"}
        assert len(inf["detect"]) == {"change": 2, "stable": 3, "null": 0}[kind]
        assert set(inf["oracle_candidates"]) == {"change": {"{E}", "{D}", "{E, D}"}, "stable": {"{R}"},
                                                 "null": set()}[kind]
        if kind == "null":
            assert inf["informative"] is None and inf["oracle"] is None
        else:
            assert inf["informative"] == (inf["detected"] and inf["oracle"] is not None)


def test_the_poison_test_passes_the_frozen_lab_and_catches_a_lab_reading_past_its_cutoff(fake_t0, monkeypatch):
    w = kworld.kernel_world(31337, "change")
    lab = dex.Lab8(gen.observed_arrays(w, 126), _Inst())
    calls = []
    for call, cutoff, reqs in ((1, 84, [_req(IDS8[:2])]), (2, 112, [_req(["X03"], win=14)]),
                               (3, 126, [_req(["X04"], ["X03"], win=7)])):
        calls.append({"call": call, "cutoff": cutoff, "experiments": [
            {"id": f"E{call}", "request": r, "result": lab.run(r, cutoff, f"E{call}")} for r in reqs]})
    assert kev.poison_mismatches(w, calls, object())[0] == []
    monkeypatch.setattr(kev, "Lab8", _Leaky)
    bad, _ = kev.poison_mismatches(w, calls, object())
    assert {"E1 (shift)", "E2 (shift)", "E3 (shift)"} <= set(bad)


# ----------------------------------------------------------------- end to end with stand-ins

def _research(obs_dir, out_dir, worlds, client_for, monkeypatch, attempt="1"):
    import anthropic

    from research_loop_proof.discovery1.lab import run as drun
    for k in worlds:
        meta = json.loads((obs_dir / k / "observed.json").read_text())
        monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: client_for(k))
        common = ["--observed", str(obs_dir / k / "observed.npz"), "--observed-sha", meta["arrays_sha256"],
                  "--weights", "unused", "--out", str(out_dir / k)]
        assert drun.main(["loop", *common]) == 0
        (out_dir / k / "guard.json").write_text(json.dumps({"truth_absent": True, "git_removed": True,
                                                            "run_attempt": attempt}))
        (out_dir / k / "timing.json").write_text('{"loop_wall_s": 1}')


def _evaluate(tmp_path, research, name):
    out = tmp_path / name
    args = ["--run-id", "12", "--observed", str(tmp_path / "obs"), "--research", str(research), "--weights", "unused",
            "--out", str(out)] + [x for k in WORLDS for x in ("--job-result", f"{k}=success")]
    assert kev.main(args) == 0
    return json.loads((out / "evaluation.json").read_text()), out


def _copy(src, dst):
    dst.mkdir(parents=True)
    for f in src.iterdir():
        (dst / f.name).write_bytes(f.read_bytes())


def test_preflight_and_the_twelve_world_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned, unfrozen_ok,
                                                                      fake_t0):
    pytest.importorskip("anthropic")
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    assert kobs.main(["--mode", "preflight", "--run-id", "11", "--run-attempt", "1", "--out",
                      str(tmp_path / "pobs")]) == 0
    _research(tmp_path / "pobs", tmp_path / "pres", ["w01"], lambda k: _Client(_replies()), monkeypatch)
    assert kpre.main(["--research", str(tmp_path / "pres"), "--observed", str(tmp_path / "pobs"),
                      "--out", str(tmp_path / "pout")]) == 0
    pre = json.loads((tmp_path / "pout" / "preflight.json").read_text())
    assert pre["verdict"] == "PASS" and pre["w01"]["illegal_experiments"] == 0, pre
    body = (tmp_path / "pout" / "verdict.json").read_bytes()
    (tmp_path / "pout" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    (tmp_path / "pub").mkdir()
    assert kobs.main(["--mode", "run", "--run-id", "12", "--run-attempt", "1", "--preflight-dir",
                      str(tmp_path / "pout"), "--published-dir", str(tmp_path / "pub"), "--out", str(tmp_path / "obs")]) == 0
    finals = {k: (["X07"] if i % 3 else []) for i, k in enumerate(WORLDS)}
    finals["w12"] = list(IDS8[:5])
    _research(tmp_path / "obs", tmp_path / "res", WORLDS, lambda k: _Client(_replies(finals[k])), monkeypatch)
    rec, out = _evaluate(tmp_path, tmp_path / "res", "out")
    assert rec["material_integrity_issues"] == [] and rec["generator_defects"] == [] and rec["no_final_worlds"] == {}
    assert sorted(Counter(rec["kinds"].values()).items()) == sorted(kworld.COMPOSITION)
    assert rec["system_sha256_frozen_text"] == rec["system_sha256_pinned"] == kev.L8_SYSTEM_SHA256
    for k in WORLDS:
        r = rec["worlds"][k]
        assert r["integrity"]["experiments_recomputed"] == 6 and r["integrity"]["poison_tests"]["mismatches"] == []
        assert r["experiments_used"] == 6 and r["exhausted_six"] and r["final_valid"]
        assert r["kind"] == rec["kinds"][k] and set(r["truth"]["roles"]) == set(dworld.ROLES8)
        assert (r["truth"]["change_day"] is None) == (r["kind"] != "change")
        assert r["cited_failed_experiments"] == [] or all(x["experiment"].startswith("E")
                                                          for x in r["cited_failed_experiments"])
        assert r["timing"] == {"loop_wall_s": 1}
    w12 = rec["worlds"]["w12"]
    assert w12["confirmation_selection"] is None and not w12["success"]["success"]
    if w12["kind"] != "null":
        assert w12["oracle_fraction"] == 0.0
    assert rec["reading"] in rules.CLOSING and rec["closing_line"] == rules.CLOSING[rec["reading"]]
    report = (out / "REPORT.md").read_text()
    assert report.startswith(f"# Kernel1 twelve-world result: {rec['reading']}") and TEST_MODEL not in report
    assert sorted(p.name for p in (out / "w01").iterdir()) == sorted(kev.FILES + ("observed.json",))

    swap = tmp_path / "swap"
    for k in WORLDS:
        _copy(tmp_path / "res" / {"w01": "w02", "w02": "w01"}.get(k, k), swap / k)
    assert _evaluate(tmp_path, swap, "out_swap")[0]["reading"] == "INFRASTRUCTURE FAILURE"

    def outage(world_dir):
        ai = json.loads((world_dir / "ai.json").read_text())
        ai.update(final_valid=False, calls=ai["calls"][:3])
        (world_dir / "ai.json").write_text(json.dumps(ai))
        (world_dir / "integrity.json").write_text(json.dumps({"failure": {
            "kind": "integrity", "error": "IntegrityError: API outage: APIStatusError", "traceback": ""}}))
    one = tmp_path / "one"
    for k in WORLDS:
        _copy(tmp_path / "res" / k, one / k)
    outage(one / "w03")
    rec1, _ = _evaluate(tmp_path, one, "out_one")
    assert rec1["material_integrity_issues"] == [] and list(rec1["no_final_worlds"]) == ["w03"]
    assert not rec1["worlds"]["w03"]["success"]["success"] and rec1["reading"] != "INFRASTRUCTURE FAILURE"
    outage(one / "w04")
    assert _evaluate(tmp_path, one, "out_two")[0]["reading"] == "INFRASTRUCTURE FAILURE"

    crash = tmp_path / "crash"
    for k in WORLDS:
        _copy(tmp_path / "res" / k, crash / k)
    (crash / "w05" / "integrity.json").write_text(json.dumps({"failure": {"kind": "crash", "error": "boom"}}))
    rec_c, _ = _evaluate(tmp_path, crash, "out_crash")
    assert rec_c["reading"] == "INFRASTRUCTURE FAILURE" and any("w05" in x for x in rec_c["material_integrity_issues"])

    rerun = tmp_path / "rerun"
    for k in WORLDS:
        _copy(tmp_path / "res" / k, rerun / k)
    (rerun / "w06" / "guard.json").write_text(json.dumps({"truth_absent": True, "run_attempt": "2"}))
    assert _evaluate(tmp_path, rerun, "out_rerun")[0]["reading"] == "INFRASTRUCTURE FAILURE"

    gone = tmp_path / "gone"
    for k in WORLDS:
        _copy(tmp_path / "res" / k, gone / k)
    for f in (gone / "w07").iterdir():
        if f.name != "guard.json":
            f.unlink()
    rec_g, _ = _evaluate(tmp_path, gone, "out_gone")
    assert rec_g["material_integrity_issues"] == [] and list(rec_g["no_final_worlds"]) == ["w07"]


def test_the_preflight_fails_without_a_confirmed_guard(tmp_path, monkeypatch, pinned, unfrozen_ok, fake_t0):
    pytest.importorskip("anthropic")
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    assert kobs.main(["--mode", "preflight", "--run-id", "11", "--run-attempt", "1", "--out",
                      str(tmp_path / "pobs")]) == 0
    _research(tmp_path / "pobs", tmp_path / "pres", ["w01"], lambda k: _Client(_replies()), monkeypatch, attempt="2")
    assert kpre.check_k1(tmp_path / "pres" / "w01")["verdict"] == "FAIL"
    (tmp_path / "pres" / "w01" / "guard.json").write_text(json.dumps({"truth_absent": True, "run_attempt": "1"}))
    assert kpre.check_k1(tmp_path / "pres" / "w01")["verdict"] == "PASS"


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")
TRUTH_DIRS = tuple(f"research_loop_proof/{p}/truth" for p in ("phase0", "beta1", "learn1", "policy1", "discovery1",
                                                                "human1", "kernel1"))


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def _downloads(job):
    return [st for st in job["steps"] if st.get("uses", "").startswith("actions/download-artifact")]


def test_the_kernel1_workflow_is_manual_scoped_and_isolated(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    assert on["workflow_dispatch"]["inputs"]["mode"]["options"] == ["preflight", "run"]
    assert wf["run-name"] == "kernel1 ${{ inputs.mode }} ${{ inputs.preflight_run }}"
    jobs = wf["jobs"]
    assert set(jobs) == {"observe", *(f"research_{k}" for k in WORLDS), "check", "evaluate", "publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    for name in ("observe", "check", "evaluate", "publish"):
        assert _secret_steps(jobs[name]) == [], name
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("secrets.ANTHROPIC_API_KEY") == 12 and "secrets." not in text.replace(
        "secrets.ANTHROPIC_API_KEY", "")
    assert "actions/cache" not in text and "HF_TOKEN" not in text and "pattern:" not in text and \
        "merge-multiple" not in text
    for job in jobs.values():
        assert all(st["with"].get("name") for st in _downloads(job))
    observe = json.dumps(jobs["observe"])
    assert "--run-attempt \\\"$GITHUB_RUN_ATTEMPT\\\"" in observe and "--published-dir published" in observe
    assert "refs/heads/kernel1/run-*" in observe
    ups = [st["with"]["name"] for st in jobs["observe"]["steps"] if st.get("uses", "").startswith("actions/upload")]
    assert ups == [f"kernel1-observed-{k}-${{{{ github.run_id }}}}" for k in WORLDS]
    for k in WORLDS:
        assert jobs["observe"]["outputs"][f"observed_sha256_{k}"] == f"${{{{ steps.observe.outputs.{k} }}}}"


def test_each_research_job_gets_only_its_world_and_runs_discovery1s_job_unchanged(wf):
    jobs = wf["jobs"]
    for k in WORLDS:
        job = jobs[f"research_{k}"]
        assert [st["with"]["name"] for st in _downloads(job)] == [f"kernel1-observed-{k}-${{{{ github.run_id }}}}"]
        steps = _secret_steps(job)
        assert len(steps) == 1
        assert (f"python -m research_loop_proof.discovery1.lab.run loop --observed obs/{k}/observed.npz "
                "--observed-sha \"$OBS_SHA\" --weights weights --out research") in steps[0]["run"]
        assert steps[0]["env"]["OBS_SHA"] == f"${{{{ needs.observe.outputs.observed_sha256_{k} }}}}"
        assert steps[0]["env"]["HF_HUB_OFFLINE"] == "1"
        assert [key for key, v in steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        runs = [st.get("run", "") for st in job["steps"]]
        assert any(r.strip() == "python -m research_loop_proof.discovery1.lab.run weights --weights weights"
                   for r in runs)
        assert not any("research_loop_proof.kernel1" in r or "comparator" in r for r in runs)
        patterns = job["steps"][0]["with"]["sparse-checkout"]
        assert all(f"!/{d}/" in patterns for d in TRUTH_DIRS) and "!/tests/" in patterns
        guard = job["steps"][1]["run"]
        assert "rm -rf .git" in guard and all(d in guard for d in TRUTH_DIRS)
        assert "'^def (make_world|pair_world|kernel_world)'" in guard and "GITHUB_RUN_ATTEMPT" in guard
        up = [st for st in job["steps"] if st.get("uses", "").startswith("actions/upload")]
        assert len(up) == 1 and up[0]["with"]["name"] == f"kernel1-research-{k}-${{{{ github.run_id }}}}"
        assert up[0]["if"] == "always()"


def test_the_research_jobs_are_identical_except_for_the_world_and_run_in_three_waves(wf):
    jobs = wf["jobs"]
    body = {k: json.dumps({n: v for n, v in jobs[f"research_{k}"].items() if n not in ("if", "needs")},
                          sort_keys=True) for k in WORLDS}
    assert all(body["w01"].replace("w01", k) == body[k] for k in WORLDS[1:])
    later = "${{ !cancelled() && inputs.mode == 'run' && needs.observe.result == 'success' }}"
    assert jobs["research_w01"]["if"] == "inputs.mode == 'preflight' || inputs.mode == 'run'"
    for i, k in enumerate(WORLDS):
        job = jobs[f"research_{k}"]
        wave = i // 4
        if wave == 0:
            assert job["needs"] == ["observe"] and (k == "w01" or job["if"] == "inputs.mode == 'run'")
        else:
            assert job["needs"] == ["observe", *(f"research_{x}" for x in WORLDS[(wave - 1) * 4:wave * 4])]
            assert job["if"] == later


def test_check_and_evaluate_read_the_right_artifacts(wf):
    jobs = wf["jobs"]
    assert jobs["check"]["needs"] == ["observe", "research_w01"]
    assert [st["with"]["name"] for st in _downloads(jobs["check"])] == [
        "kernel1-observed-w01-${{ github.run_id }}", "kernel1-research-w01-${{ github.run_id }}"]
    assert jobs["evaluate"]["needs"] == ["observe", *(f"research_{k}" for k in WORLDS)]
    names = [st["with"]["name"] for st in _downloads(jobs["evaluate"])]
    assert names == [f"kernel1-observed-{k}-${{{{ github.run_id }}}}" for k in WORLDS] + \
        [f"kernel1-research-{k}-${{{{ github.run_id }}}}" for k in WORLDS]
    paths = {st["with"]["name"]: st["with"]["path"] for st in _downloads(jobs["evaluate"])}
    assert all(paths[f"kernel1-research-{k}-${{{{ github.run_id }}}}"] == f"research/{k}" for k in WORLDS)
    step = next(st for st in jobs["evaluate"]["steps"] if "kernel1.truth.evaluate" in st.get("run", ""))
    for k in WORLDS:
        assert step["env"][f"RESULT_{k.upper()}"] == f"${{{{ needs.research_{k}.result }}}}"
        assert f'--job-result "{k}=$RESULT_{k.upper()}"' in step["run"]
    assert "kernel1/run-${{ github.run_id }}" in json.dumps(jobs["publish"])


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    pattern = re.compile(r"^def (make_world|pair_world|kernel_world)", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True,
                           check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]
    kept = [f for f in set(files) if not f.startswith(tuple(d + "/" for d in TRUTH_DIRS) + ("tests/",))]
    assert kept and not [f for f in kept if (ROOT / f).is_file()
                         and pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

FROZEN_SHA256 = {
    "docs/research_loop_proof/KERNEL1_SPEC.md":
        "8217fe7d8e5dcf40f514940eb4972721e5daefb0722e33a2fdede042cc9b90b2",
    "research_loop_proof/kernel1/truth/world.py":
        "689160ac809d485033675f2e16e4136730da46db767a912b6d2393f5f1386d09",
    "research_loop_proof/kernel1/truth/observe.py":
        "da411c93b5dcba07313336e7b31801beee5712793029263998005aef0814dc44",
    "research_loop_proof/kernel1/truth/rules.py":
        "6ede79a7faa2d30e379de0ce81ae2c63bebff3b7d7af30421a7caf15f29d2c33",
    "research_loop_proof/kernel1/truth/evaluate.py":
        "d3dbe6094a9ad30e0d30aa4d7c3b9f608d16d4302aedb6ecd62b9e2efb957637",
    "research_loop_proof/kernel1/truth/preflight.py":
        "27e2159e032a7bac98a481cf7e59ff200f9080c00392d904068a3e79378b127c",
    ".github/workflows/research-loop-kernel1.yml":
        "757abf1207fb694fb0992cdcd9cd2ddb565dad04c2aca43ea8b81c907c08a439",
    "research_loop_proof/beta1/truth/preflight.py":
        "50442d7e5633110bd64e68d7f1b6748107620c5d802a4557ef7dfbad7ce293b9",
}
SPEC_SHA = "6ef8c21d22672de4d9fc5c4772b2c506a7882b3226a76ec00ea3ddb2e1ddd25e"


def test_the_frozen_files_and_the_spec_hash_are_pinned():
    assert kspec.missing() == []
    got = kspec.file_hashes()
    assert {rel: got[rel] for rel in FROZEN_SHA256} == FROZEN_SHA256
    assert set(FROZEN_SHA256) == {rel for rel in kspec.FROZEN if rel not in dspec.FROZEN}
    assert kspec.spec_sha() == SPEC_SHA
