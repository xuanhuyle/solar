"""Final kernel (docs/research_loop_proof/NEXT_FINAL_KERNEL_PROMPT.md): L8 unchanged with company context and validated
memory as data, the deterministic referee and memory, the companies, sequences and worlds, K/F separation, the scoring
rules, the programme reading, the evaluator end to end with stand-ins, the workflow and the freeze. Parts that need
anthropic skip without it."""

from __future__ import annotations

import ast
import difflib
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
from research_loop_proof.discovery1.truth import world as dworld
from research_loop_proof.final_kernel.lab import referee as ref
from research_loop_proof.final_kernel.lab import researcher as fres
from research_loop_proof.final_kernel.lab import run as frun
from research_loop_proof.final_kernel.truth import companies as C
from research_loop_proof.final_kernel.truth import evaluate as fev
from research_loop_proof.final_kernel.truth import observe as fobs
from research_loop_proof.final_kernel.truth import preflight as fpre
from research_loop_proof.final_kernel.truth import rules
from research_loop_proof.final_kernel.truth import spec as fspec
from research_loop_proof.final_kernel.truth import world as fworld
from research_loop_proof.kernel1.truth import spec as kspec
from research_loop_proof.learn1.lab import researcher as lres
from research_loop_proof.phase0.lab import researcher as p0res
from research_loop_proof.phase0.truth import generator as gen

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "research_loop_proof" / "final_kernel"
WORKFLOW = ROOT / ".github" / "workflows" / "research-loop-final-kernel.yml"
TEST_MODEL = "test-model-id"
IDS8 = dex.IDS8
H = 24


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


def _req(cov, ref_=(), win=28):
    return {"covariates": list(cov), "reference": list(ref_), "window_days": win, "expect": "improves", "because": "b"}


def _reply(rows, exps=(), final=None, conclusion=""):
    return {"notes": "n", "beliefs": rows, "experiments": list(exps), "final_selection": list(final or []),
            "conclusion": conclusion}


def _replies(final=("X07",)):
    return [_resp(_reply(_rows(), [_req(IDS8[:4]), _req(IDS8[4:])])),
            _resp(_reply(_rows("promising", ["E1"]), [_req(IDS8[4:6], win=14), _req(IDS8[6:], win=14)])),
            _resp(_reply(_rows("promising", ["E3"]), [_req(["X07"], win=14), _req(["X08"], ["X07"], win=7)])),
            _resp(_reply(_rows("accepted", ["E5"], {"X08": {"status": "rejected", "cites": ["E6"]}}),
                         final=list(final), conclusion="X07 helps."))]


@pytest.fixture()
def pinned(monkeypatch):
    monkeypatch.setitem(p0res.RESEARCHER, "model_sha256", p0res.sha256_text(TEST_MODEL))


@pytest.fixture()
def unfrozen_ok(monkeypatch):
    monkeypatch.setattr(fspec, "missing", lambda root=None: [])


@pytest.fixture()
def fake_t0(monkeypatch):
    from research_loop_proof.beta1.lab import run as brun

    monkeypatch.setattr(brun, "load_t0", lambda weights: (object(), {"repo": t0_beta.REPO, "fake": True}))
    monkeypatch.setattr(t0_beta, "BetaT0", lambda model: _Inst())


def _e(i, call, cov, ref_=(), lo=0.1, last=126, win=14):
    return {"id": f"E{i}", "call": call, "cutoff": last,
            "request": {"covariates": list(cov), "reference": list(ref_), "window_days": win},
            "result": {"scored_days": [last - win + 1, last], "lo95": lo, "skill": lo + 0.1, "hi95": lo + 0.2,
                       "reference_mae": 1.0, "candidate_mae": 0.9, "wins": 1, "losses": 0, "ties": 0}}


def _record(exps, final=None, final_valid=True):
    calls = {}
    for e in exps:
        calls.setdefault(e["call"], []).append({k: v for k, v in e.items() if k not in ("call", "cutoff")})
    out = [{"call": c, "cutoff": 84 + 14 * c, "final": False, "experiments": xs, "valid": True}
           for c, xs in sorted(calls.items())]
    out.append({"call": 4, "cutoff": 126, "final": True, "valid": final_valid, "experiments": [],
                "response": {"beliefs": _rows(), "final_selection": list(final or [])} if final_valid else None})
    return {"calls": out, "final_valid": final_valid, "final_selection": list(final or []) if final_valid else None}


def _confirm(lo=0.1):
    def f(cov, refs):
        return {"skill": lo + 0.1, "lo95": lo, "hi95": lo + 0.2, "reference_mae": 1.0, "candidate_mae": 0.9,
                "wins": 1, "losses": 0, "ties": 0, "scored_days": [127, 154]}
    return f


# ----------------------------------------------------------------- L8 identity and the data block

def test_the_researcher_is_l8_with_only_the_data_block_added():
    a = inspect.getsource(dres.Researcher8.run_call).splitlines()
    b = inspect.getsource(fres.ResearcherFK.run_call).splitlines()
    diff = [ln for ln in difflib.unified_diff(a, b, lineterm="", n=0) if ln[:1] in "+-" and ln[:3] not in ("---", "+++")]
    assert diff == ["-        user = user_prompt(step, self.calls)",
                    "+        user = self.data + user_prompt(step, self.calls)"]
    assert p0res.sha256_text(dres.system_text8()) == fev.L8_SYSTEM_SHA256 == \
        "78fb006123c860cb74063394d817370c76b20e3951b2a9fe1457e9549ce3854d"
    assert p0res.sha256_text(lres.frozen_lesson()) == fev.LESSON_SHA256
    assert fev.LESSON_SHA256.startswith("1c38b101")


def test_the_data_block_is_labelled_data_and_removing_it_gives_the_l8_prompt(pinned):
    block = fres.data_block("CONTEXT TEXT", "")
    assert block.startswith(fres.CONTEXT_HEADER) and fres.EMPTY_MEMORY in block and block.endswith(
        fres.END_OF_DATA + "\n\n")
    assert fres.data_block("C", "M1 | x") != block and "M1 | x" in fres.data_block("C", "M1 | x")
    lab = dex.Lab8(gen.observed_arrays(fworld.episode_world(fworld.design("s", "1")["c1"], 1)[0], 126), _Inst())
    r = fres.ResearcherFK(_Client(_replies()), TEST_MODEL, lab, context_text="CTX", memory_text="MEM")
    rec = r.run()
    assert rec["system_sha256"] == fev.L8_SYSTEM_SHA256 and rec["final_valid"]
    for c in rec["calls"]:
        assert c["user_prompt"].startswith(fres.data_block("CTX", "MEM"))
    assert fres.rebuild_mismatches_fk(rec["calls"], fres.data_block("CTX", "MEM")) == []
    assert fres.rebuild_mismatches_fk(rec["calls"], fres.data_block("CTX", "")) != []
    stripped = [dict(c, user_prompt=c["user_prompt"][len(fres.data_block("CTX", "MEM")):]) for c in rec["calls"]]
    assert dres.rebuild_mismatches8(stripped) == []


def test_fixed_texts_carry_no_methodological_or_role_words():
    texts = [fres.CONTEXT_HEADER, fres.MEMORY_HEADER, fres.EMPTY_MEMORY, fres.END_OF_DATA, C.QUESTION]
    for c in C.COMPANIES:
        texts += [c["name"], c["profile"], c["target"], c["regime_name"], *c["regimes"]]
        texts += [x for f in c["families"] for s in f["sources"] for x in s] + [f["name"] for f in c["families"]]
        texts += [t for fe in c["events"] for t in fe]
    for t in texts:
        assert not [b for b in C.BANNED if b in t.lower()], t
    labels = inspect.getsource(ref.render_entry)
    for word in ("noise", "driver", "proxy", "retired", "split", "individually", "avoid", "budget"):
        assert word not in labels.lower()


def test_the_lab_side_never_imports_a_truth_package():
    for path in (PKG / "lab").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
                assert not any("truth" in n for n in names), path


# ----------------------------------------------------------------- companies, sequences, worlds

def test_companies_have_three_families_of_three_three_two_and_one_measurement_pair():
    assert len(C.COMPANIES) == 4
    for c in C.COMPANIES:
        assert tuple(len(f["sources"]) for f in c["families"]) == C.FAMILY_SIZES
        assert sum(f["pair"] for f in c["families"]) == 1 and not c["families"][2]["pair"]
        assert len(c["events"]) == 2 and all(len(e) >= 2 for e in c["events"]) and len(c["regimes"]) == 3


def test_sequences_give_two_of_each_pattern_two_nulls_and_six_non_null():
    pats = Counter(p for s in fworld.SEQUENCES.values() for (_, _, p) in s[1:])
    assert pats == Counter({"P1": 2, "P2": 2, "P3": 2, "P4": 2})
    nulls = [(k, i) for k, s in fworld.SEQUENCES.items() for i, (_, letter, _) in enumerate(s) if letter is None]
    assert len(nulls) == 2 and all(i > 0 for _, i in nulls)
    for k, s in fworld.SEQUENCES.items():
        assert s[0][2] is None and s[0][1] == "A" and s[0][0] == 0
        for regime, letter, pat in s[1:]:
            if pat == "P1":
                assert letter == "A" and regime == 0
            if pat in ("P2", "P3", "P4"):
                assert regime != 0


def test_designs_are_seeded_by_spec_and_run_and_vary_across_companies():
    seen = set()
    for run in ("100", "101", "102", "103"):
        d = fworld.design("specsha", run)
        assert sorted(x["sequence"] for x in d.values()) == ["S1", "S2", "S3", "S4"]
        assert d == fworld.design("specsha", run)
        for x in d.values():
            srcs = C.sources(fworld.company(x["company"]))
            assert sorted(x["x_ids"].values()) == list(IDS8)
            assert srcs[x["letters"]["A"]]["family"] == x["F_A"] and srcs[x["letters"]["B"]]["family"] == x["F_O"]
            seen.add((x["company"], x["F_A"], x["letters"]["A"]))
    assert len({fa for _, fa, _ in seen}) == 2 and len(seen) > 4
    assert fworld.design("other", "100") != fworld.design("specsha", "100")


def test_episode_worlds_follow_their_frozen_construction():
    for run in ("7", "8"):
        for d in fworld.design("s", run).values():
            for e in fworld.EPISODES:
                w, t = fworld.episode_world(d, e)
                assert fev.generator_defects(d, e, w, t) == []
                b = dworld.make_world8(t["seed"])
                assert w.tau == b.tau and all(np.array_equal(w.x[r], b.x[r]) for r in b.x)
                assert sorted(w.ids.values()) == list(IDS8) and len(set(w.ids)) == 8
                plan = t["plan"]
                if plan["useful_source"] is None:
                    assert t["useful"] == []
                else:
                    assert d["x_ids"][plan["useful_source"]] in t["useful"] and 1 <= len(t["useful"]) <= 2
                assert set(t["useful"]) | set(t["irrelevant"]) == set(IDS8)


def test_null_and_useful_episodes_keep_the_target_scale():
    var = {"null": [], "useful": []}
    for run in map(str, range(12)):
        for d in fworld.design("s", run).values():
            for e in fworld.EPISODES:
                w, t = fworld.episode_world(d, e)
                var["null" if not t["useful"] else "useful"].append(w.y[:126 * H].var())
    assert 0.8 < np.mean(var["null"]) / np.mean(var["useful"]) < 1.25


def test_contexts_name_both_three_source_families_before_day_one_and_hold_no_role():
    for d in fworld.design("s", "5").values():
        for e in fworld.EPISODES:
            ctx = fworld.episode_context(d, e)
            days = [int(m) for m in re.findall(r"- Day (-?\d+):", ctx["text"])]
            assert len(days) == 2 and all(-28 <= x <= -1 for x in days)
            comp = fworld.company(d["company"])
            assert sum(any(t in ctx["text"] for t in comp["events"][f]) for f in (0, 1)) == 2
            assert all(x in ctx["text"] for x in IDS8)
            for word in ("useful", "stale", "P1", "P2", "P3", "P4", "canary", "CANARY"):
                assert word not in ctx["text"]
    assert list(inspect.signature(C.event_log).parameters) == ["company", "families", "rng"]


# ----------------------------------------------------------------- referee and memory

def test_referee_approves_only_at_tested_granularity():
    exps = [_e(1, 1, ["X01", "X02"], last=84, win=28), _e(2, 2, ["X03"]), _e(3, 2, ["X04"], ["X03"]),
            _e(4, 3, ["X05"], lo=-0.1), _e(5, 3, ["X06"], win=7)]
    rep = ref.adjudicate(_record(exps, final=["X03"]), _confirm())
    by = {(tuple(c["covariates"]), tuple(c["reference"])): c for c in rep["configurations"]}
    assert by[(("X01", "X02"), ())]["granularity"] == "set (attribution unresolved)"
    assert by[(("X01", "X02"), ())]["status"] == "positive"
    assert by[(("X03",), ())]["granularity"] == "individual" and by[(("X03",), ())]["status"] == "positive"
    assert by[(("X04",), ("X03",))]["granularity"] == "conditional on X03"
    assert by[(("X05",), ())]["status"] == "negative" and by[(("X05",), ())]["confirmation"] is None
    assert by[(("X06",), ())]["status"] == "unresolved" and by[(("X06",), ())]["indicative_only"]
    assert rep["headline"]["covariates"] == ["X03"]
    assert {tuple(c["covariates"]) for c in rules.individual_approvals(rep)} == {("X03",), ("X04",)}
    assert rep["selection"]["status"] == "confirmed" and rep["selection"]["tested_as_configuration"]


def test_indicative_windows_never_decide_and_governing_is_latest_then_longest():
    rep = ref.adjudicate(_record([_e(1, 1, ["X01"], last=84, win=28), _e(2, 3, ["X01"], lo=-0.2, win=7)]),
                         _confirm())
    assert rep["configurations"][0]["status"] == "positive"
    rep = ref.adjudicate(_record([_e(1, 1, ["X01"], lo=-0.1, last=84, win=28), _e(2, 3, ["X01"], lo=0.3, win=7)]),
                         _confirm())
    assert rep["configurations"][0]["status"] == "negative"
    rep = ref.adjudicate(_record([_e(1, 1, ["X01"], last=84, win=28), _e(2, 3, ["X01"], lo=-0.05, win=14)]),
                         _confirm())
    assert rep["configurations"][0]["status"] == "deteriorated" and not rep["approved_positive"]
    rep = ref.adjudicate(_record([_e(1, 2, ["X01"], lo=-0.1, win=14), _e(2, 3, ["X01"], lo=0.1, win=28)]),
                         _confirm())
    assert rep["configurations"][0]["governing"]["experiment"] == "E2"


def test_referee_handles_empty_oversized_and_missing_final_selections():
    exps = [_e(1, 1, ["X01"])]
    assert ref.adjudicate(_record(exps, final=[]), _confirm())["selection"]["status"] == "empty selection"
    assert "not confirmable" in ref.adjudicate(_record(exps, final=list(IDS8[:5])), _confirm())["selection"]["status"]
    assert ref.adjudicate(_record(exps, final_valid=False), _confirm())["selection"]["status"] == \
        "no valid final response"
    assert ref.adjudicate({"calls": []}, _confirm())["configurations"] == []


def test_memory_is_deterministic_scoped_and_rendered_in_a_closed_vocabulary():
    exps = [_e(1, 1, ["X01", "X02"], last=84, win=28), _e(2, 2, ["X03"], lo=-0.1)]
    rep = ref.adjudicate(_record(exps), _confirm())
    names = {x: f"Source {x}" for x in IDS8}
    m1 = ref.extend_memory([], rep, company="c1", episode=1, regime="Regime one", names=names)
    m2 = ref.extend_memory(m1, rep, company="c1", episode=2, regime="Regime two", names=names)
    assert [m["id"] for m in m2] == ["M1", "M2", "M3", "M4"] and m2[:2] == m1
    assert m1[1]["status"] == "negative" and m1[1]["confirmation"] is None and m1[1]["regime"] == "Regime one"
    assert m1[0]["experiments"] == ["episode 1 experiment E1"]
    text = ref.render_memory(m2)
    pattern = re.compile(r"^M\d+ \| study period \d \| regime: [^|]+ \| covariates [^|]+ \| reference [^|]+ \| "
                         r"status (positive|negative|deteriorated|unresolved) \| granularity (individual|conditional on "
                         r"[X0-9, ]+|set \(attribution unresolved\)( given [X0-9, ]+)?) \| [^|]+ \| holdout days "
                         r"127-154: [^|]+$")
    assert all(pattern.match(line) for line in text.splitlines())
    assert ref.memory_differences(m2, json.loads(ref.memory_json(m2))) == []
    tampered = json.loads(ref.memory_json(m2))
    tampered[0]["status"] = "negative"
    assert ref.memory_differences(tampered, m2)
    nudged = json.loads(ref.memory_json(m2))
    nudged[0]["research_result"]["skill"] += 5e-5
    assert ref.memory_differences(nudged, m2) == []


# ----------------------------------------------------------------- scoring rules

USEFUL = ["X03"]


def test_strong_partial_and_criteria_five_six():
    good = ref.adjudicate(_record([_e(1, 2, ["X03"]), _e(2, 2, ["X03", "X05"])]), _confirm())
    assert rules.strong(good, USEFUL, True)["strong"]
    pair = ref.adjudicate(_record([_e(1, 2, ["X03", "X05"])]), _confirm())
    assert rules.strong(pair, USEFUL, True)["strong"]
    three = ref.adjudicate(_record([_e(1, 2, ["X03", "X05", "X06"])]), _confirm())
    s = rules.strong(three, USEFUL, True)
    assert not s["strong"] and s["partial"] and "2_headline_at_most_2_candidates" in s["failed"]
    wrong = ref.adjudicate(_record([_e(1, 2, ["X05"], lo=0.2), _e(2, 2, ["X03"], lo=0.1)]), _confirm())
    assert rules.strong(wrong, USEFUL, True)["failed"] == ["3_headline_contains_useful_candidate"]
    unconf = ref.adjudicate(_record([_e(1, 2, ["X03"]), _e(2, 2, ["X05"], lo=0.05)]),
                            lambda cov, r: _confirm(0.1 if cov == ["X03"] else -0.1)(cov, r))
    s = rules.strong(unconf, USEFUL, True)
    assert s["failed"] == ["5_6_no_unsupported_approval_of_irrelevant_candidate"]
    assert rules.incorrect_approvals(unconf, USEFUL)[0]["covariates"] == ["X05"]
    assert not rules.strong(good, USEFUL, False)["strong"]


def test_null_success_is_structural():
    rec = _record([_e(1, 2, ["X03"], lo=-0.1)], final=[])
    rep = ref.adjudicate(rec, _confirm())
    assert rules.null_success(rep, rec)["success"]
    rec2 = _record([_e(1, 2, ["X03"], lo=-0.1)], final=["X03"])
    assert not rules.null_success(ref.adjudicate(rec2, _confirm()), rec2)["success"]
    rec3 = _record([_e(1, 2, ["X03"], lo=0.1)], final=[])
    assert rules.null_success(ref.adjudicate(rec3, _confirm()), rec3)["failed"] == ["1_no_approved_positive_finding"]
    rec4 = _record([], final=[], final_valid=False)
    assert not rules.null_success(ref.adjudicate(rec4, _confirm()), rec4)["success"]


def test_discovery_index_is_per_call_and_ignores_order_within_a_call():
    exps = [_e(1, 1, ["X05"], lo=-0.1), _e(2, 1, ["X06"], lo=-0.1), _e(3, 2, ["X03"]), _e(4, 2, ["X07"], lo=-0.1)]
    rec = _record(exps)
    pre = [(n, ref.adjudicate(rec, _confirm(), calls_limit=c, with_selection=False)) for c, n in ((1, 2), (2, 4))]
    assert rules.discovery_index(pre, USEFUL) == 4
    swapped = _record([exps[0], exps[1], dict(exps[3], id="E3"), dict(exps[2], id="E4")])
    pre2 = [(n, ref.adjudicate(swapped, _confirm(), calls_limit=c, with_selection=False)) for c, n in ((1, 2), (2, 4))]
    assert rules.discovery_index(pre2, USEFUL) == 4


def test_pair_outcomes_follow_section_ten():
    def s(strong, index, n=6):
        return {"strong": strong, "index": index, "experiments": n}
    assert rules.pair_outcome(s(True, 2), s(False, None))[0] == "K WIN"
    assert rules.pair_outcome(s(True, 2), s(True, 4))[0] == "K WIN"
    assert rules.pair_outcome(s(True, 3), s(True, 4))[0] == "TIE"
    assert rules.pair_outcome(s(True, 3, 4), s(True, 3, 6))[0] == "K WIN"
    assert rules.pair_outcome(s(False, None), s(True, 2))[0] == "F WIN"
    assert rules.pair_outcome(s(False, None), s(False, None))[0] == "TIE"


def _eps(**over):
    keys = [f"c{c}e{e}" for c in range(1, 5) for e in (2, 3)]
    nulls = {"c2e3", "c4e2"}
    eps = {k: {"null": k in nulls, "pattern": "P1", "informative": None if k in nulls else True,
               "K": {"strong": {"strong": k not in nulls}, "null": {"success": k in nulls}, "incorrect": False,
                     "oracle_fraction": None if k in nulls else 0.9}} for k in keys}
    for key, val in over.items():
        k, field = key.split("__")
        if field in ("strong",):
            eps[k]["K"]["strong"] = {"strong": val}
        elif field == "nullok":
            eps[k]["K"]["null"] = {"success": val}
        elif field in ("incorrect", "oracle_fraction"):
            eps[k]["K"][field] = val
        else:
            eps[k][field] = val
    return eps


def test_every_programme_row_is_reachable_with_its_closing_line():
    def label(eps, material=(), defects=(), missing=()):
        return rules.programme(eps, list(material), list(defects), list(missing))[0]
    assert label(_eps()) == "FULL KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_eps(), material=["x"]) == "INFRASTRUCTURE FAILURE"
    assert label(_eps(), missing=["a", "b"]) == "INFRASTRUCTURE FAILURE"
    assert label(_eps(), missing=["a"]) == "FULL KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_eps(c1e2__informative=False)) == "BENCHMARK FAILURE"
    assert label(_eps(), defects=["d"]) == "BENCHMARK FAILURE"
    assert label(_eps(c1e2__strong=False, c1e3__strong=False)) == "FULL KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_eps(c1e2__strong=False, c1e3__strong=False, c2e2__strong=False)) == "FULL KERNEL NOT PROVEN"
    assert label(_eps(c2e3__nullok=False)) == "FULL KERNEL NOT PROVEN"
    assert label(_eps(c1e2__incorrect=True)) == "FULL KERNEL PROVEN FOR THIS BENCHMARK"
    assert label(_eps(c1e2__incorrect=True, c1e3__incorrect=True)) == "FULL KERNEL NOT PROVEN"
    two = {f"{k}__oracle_fraction": 0.5 for k in ("c1e2", "c1e3")}  # six fractions: median (0.9 + 0.9) / 2
    assert label(_eps(**two)) == "FULL KERNEL PROVEN FOR THIS BENCHMARK"
    three = {f"{k}__oracle_fraction": 0.5 for k in ("c1e2", "c1e3", "c2e2")}  # median (0.5 + 0.9) / 2 = 0.7
    assert label(_eps(**three)) == "FULL KERNEL NOT PROVEN"
    assert set(rules.CLOSING.values()) == {"BENCHMARK/INFRASTRUCTURE RESULT ONLY",
                                           "MOVE THE FULL KERNEL TO A REAL-WORLD COMPANY-CONTEXT RESEARCH TEST",
                                           "STOP SYNTHETIC KERNEL WORK"}
    owner = (ROOT / "docs/research_loop_proof/NEXT_FINAL_KERNEL_PROMPT.md").read_text(encoding="utf-8")
    assert all(line in owner for line in rules.CLOSING.values())


def test_k_versus_f_never_gates_the_reading():
    src = inspect.getsource(rules.programme)
    assert "pair" not in src and "WIN" not in src


# ----------------------------------------------------------------- gates

def _published(d: Path, phase="final-kernel-preflight", verdict="PASS", sha=None):
    d.mkdir(parents=True, exist_ok=True)
    body = json.dumps({"phase": phase, "verdict": verdict, "spec_sha": sha or fspec.spec_sha()}).encode()
    (d / "verdict.json").write_bytes(body)
    (d / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")


def test_the_scored_run_is_refused_on_a_rerun_or_a_second_batch(tmp_path, unfrozen_ok):
    _published(tmp_path / "pre")
    (tmp_path / "pub").mkdir()
    assert fobs.refusals("run", "1", str(tmp_path / "pre"), str(tmp_path / "pub")) == []
    assert any("attempt 2" in e for e in fobs.refusals("run", "2", str(tmp_path / "pre"), str(tmp_path / "pub")))
    assert fobs.refusals("run", "1", str(tmp_path / "pre"), None)
    (tmp_path / "pub" / "9").mkdir()
    (tmp_path / "pub" / "9" / "verdict.json").write_text(json.dumps({"phase": "final-kernel-run"}))
    assert fobs.refusals("run", "1", str(tmp_path / "pre"), str(tmp_path / "pub"))
    _published(tmp_path / "old", sha="0" * 64)
    assert fobs.refusals("run", "1", str(tmp_path / "old"), str(tmp_path / "pub" / "none"))


def test_observe_exports_per_episode_observed_context_and_holdout(tmp_path, unfrozen_ok):
    assert fobs.main(["--mode", "preflight", "--run-id", "7", "--run-attempt", "1", "--out", str(tmp_path)]) == 0
    assert sorted(p.name for p in (tmp_path / "obs").iterdir()) == ["c1e1", "c1e2", "c1e3"]
    meta = json.loads((tmp_path / "obs" / "c1e2" / "observed.json").read_text())
    assert set(meta) == {"episode", "days", "keys", "arrays_sha256"}
    with np.load(tmp_path / "obs" / "c1e2" / "observed.npz") as z:
        assert all(len(z[k]) == 126 * H for k in z.files)
    with np.load(tmp_path / "holdout" / "c1e2" / "holdout.npz") as z:
        assert all(len(z[k]) == 154 * H for k in z.files)
    ctx = json.loads((tmp_path / "obs" / "c1e2" / "context.json").read_text())
    assert set(ctx) == {"company", "company_name", "episode", "regime", "names"}
    blob = b"".join(p.read_bytes() for p in (tmp_path / "obs").rglob("*") if p.is_file())
    d = fobs.designs("preflight", "7")["c1"]
    for e in fworld.EPISODES:
        w, t = fworld.episode_world(d, e)
        assert w.canary.encode() not in blob
    assert b"useful" not in blob and b"stale" not in blob


# ----------------------------------------------------------------- end to end with stand-ins

def _loop(obs, job, cond, ep, out, monkeypatch, client, memory=None):
    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", lambda **kw: client)
    meta = json.loads((obs / ep / "observed.json").read_text())
    args = ["loop", "--condition", cond, "--observed", str(obs / ep / "observed.npz"), "--observed-sha",
            meta["arrays_sha256"], "--context", str(obs / ep / "context.txt"), "--context-sha",
            frun.file_sha(obs / ep / "context.txt"), "--weights", "unused", "--out", str(out / job)]
    if memory is not None:
        args += ["--memory", str(memory / "memory.txt"), "--memory-sha", frun.file_sha(memory / "memory.txt")]
    assert frun.main(args) == 0
    (out / job / "guard.json").write_text(json.dumps({"truth_absent": True, "git_removed": True, "run_attempt": "1"}))
    (out / job / "timing.json").write_text('{"loop_wall_s": 2}')


def _referee(root, job, ep, out, memory_in=None):
    hold = json.loads((root / "holdout" / ep / "holdout.json").read_text())
    args = ["referee", "--record", str(root / "res" / job / "ai.json"), "--context-json",
            str(root / "obs" / ep / "context.json"), "--holdout", str(root / "holdout" / ep / "holdout.npz"),
            "--holdout-sha", hold["arrays_sha256"], "--weights", "unused", "--out", str(out)]
    if memory_in is not None:
        args += ["--memory-in", str(memory_in / "memory.json")]
    assert frun.main(args) == 0


def _chain(root, companies, monkeypatch, finals=None):
    obs, res, mem = root / "obs", root / "res", root / "mem"
    for c in companies:
        def client(job):
            return _Client(_replies((finals or {}).get(job, ("X07",))))
        _loop(obs, f"e1_{c}", "E1", f"{c}e1", res, monkeypatch, client(f"e1_{c}"))
        _referee(root, f"e1_{c}", f"{c}e1", mem / f"{c}-e1")
        for e in (2, 3):
            _loop(obs, f"e{e}f_{c}", "F", f"{c}e{e}", res, monkeypatch, client(f"e{e}f_{c}"))
            _loop(obs, f"e{e}k_{c}", "K", f"{c}e{e}", res, monkeypatch, client(f"e{e}k_{c}"),
                  memory=mem / f"{c}-e{e - 1}")
            if e == 2:
                _referee(root, f"e2k_{c}", f"{c}e2", mem / f"{c}-e2", memory_in=mem / f"{c}-e1")


def test_preflight_and_the_scored_run_end_to_end_with_stand_ins(tmp_path, monkeypatch, pinned, unfrozen_ok, fake_t0):
    pytest.importorskip("anthropic")
    monkeypatch.setenv("RESEARCHER_MODEL", TEST_MODEL)
    pre = tmp_path / "pre"
    assert fobs.main(["--mode", "preflight", "--run-id", "11", "--run-attempt", "1", "--out", str(pre)]) == 0
    _chain(pre, ["c1"], monkeypatch)
    assert fpre.main(["--research", str(pre / "res"), "--observed", str(pre / "obs"), "--memory", str(pre / "mem"),
                      "--out", str(pre / "out")]) == 0
    verdict = json.loads((pre / "out" / "preflight.json").read_text())
    assert verdict["verdict"] == "PASS", verdict
    k_prompt = json.loads((pre / "res" / "e2k_c1" / "ai.json").read_text())["calls"][0]["user_prompt"]
    f_prompt = json.loads((pre / "res" / "e2f_c1" / "ai.json").read_text())["calls"][0]["user_prompt"]
    assert fres.EMPTY_MEMORY in f_prompt and fres.EMPTY_MEMORY not in k_prompt and "M1 |" in k_prompt
    assert f_prompt.split(fres.MEMORY_HEADER)[0] == k_prompt.split(fres.MEMORY_HEADER)[0]
    body = (pre / "out" / "verdict.json").read_bytes()
    (pre / "out" / "MANIFEST.sha256").write_text(f"{hashlib.sha256(body).hexdigest()}  verdict.json\n")
    (tmp_path / "pub").mkdir()
    run = tmp_path / "run"
    assert fobs.main(["--mode", "run", "--run-id", "12", "--run-attempt", "1", "--preflight-dir", str(pre / "out"),
                      "--published-dir", str(tmp_path / "pub"), "--out", str(run)]) == 0
    _chain(run, fworld.COMPANY_KEYS, monkeypatch, finals={"e3k_c4": list(IDS8[:5]), "e2f_c1": []})
    jobs = [j for j, *_ in fev.jobs_of(fworld.COMPANY_KEYS)]
    assert len(jobs) == 20

    def evaluate(research, memory, name):
        out = tmp_path / name
        args = ["--run-id", "12", "--observed", str(run / "obs"), "--holdout", str(run / "holdout"), "--research",
                str(research), "--memory", str(memory), "--weights", "unused", "--out", str(out)]
        args += [x for j in jobs for x in ("--job-result", f"{j}=success")]
        assert fev.main(args) == 0
        return json.loads((out / "evaluation.json").read_text()), out

    rec, out = evaluate(run / "res", run / "mem", "out")
    assert rec["material_integrity_issues"] == [] and rec["generator_defects"] == [] and rec["missing_scored"] == []
    assert all(not c["differences"] for c in rec["memory_checks"].values())
    assert rec["reading"] in rules.CLOSING and rec["closing_line"] == rules.CLOSING[rec["reading"]]
    assert sorted(k for k in rec["episodes"]) == sorted(f"{c}e{e}" for c in fworld.COMPANY_KEYS for e in (1, 2, 3))
    assert len(rec["pairs"]) == 8 and set(rec["aggregates"]["pair_outcomes"]) <= {"K WIN", "F WIN", "TIE"}
    for key, ep in rec["episodes"].items():
        for cond, x in ep["conditions"].items():
            assert x["integrity"]["experiments_recomputed"] == 6 and x["integrity"]["poison_tests"]["mismatches"] == []
            if cond == "K":
                assert x["transfer"]["memory_entries"] > 0
    report = (out / "REPORT.md").read_text()
    assert report.startswith(f"# Final kernel result: {rec['reading']}") and TEST_MODEL not in report

    def copy(src, dst):
        import shutil
        shutil.copytree(src, dst)

    copy(run / "mem", tmp_path / "mem_t")
    m = json.loads((tmp_path / "mem_t" / "c2-e1" / "memory.json").read_text())
    m[0]["status"] = "positive" if m[0]["status"] != "positive" else "negative"
    (tmp_path / "mem_t" / "c2-e1" / "memory.json").write_text(json.dumps(m))
    assert evaluate(run / "res", tmp_path / "mem_t", "out_t")[0]["reading"] == "INFRASTRUCTURE FAILURE"
    copy(run / "res", tmp_path / "res_s")
    import shutil
    shutil.rmtree(tmp_path / "res_s" / "e2f_c3")
    shutil.copytree(run / "res" / "e2k_c3", tmp_path / "res_s" / "e2f_c3")
    assert evaluate(tmp_path / "res_s", run / "mem", "out_s")[0]["reading"] == "INFRASTRUCTURE FAILURE"


# ----------------------------------------------------------------- the workflow

yaml = pytest.importorskip("yaml")
TRUTH_DIRS = tuple(f"research_loop_proof/{p}/truth" for p in ("phase0", "beta1", "learn1", "policy1", "discovery1",
                                                                "human1", "kernel1", "final_kernel"))
RESEARCH_JOBS = [f"e1_c{i}" for i in range(1, 5)] + [f"e{e}{x}_c{i}" for e in (2, 3) for x in "fk" for i in
                                                      range(1, 5)]


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _downloads(job):
    return [st for st in job["steps"] if st.get("uses", "").startswith("actions/download-artifact")]


def _secret_steps(job):
    return [st for st in job["steps"] if "secrets." in json.dumps(st)]


def test_the_workflow_is_manual_scoped_and_isolated(wf):
    on = wf.get("on", wf.get(True))
    assert list(on) == ["workflow_dispatch"] and wf["permissions"] == {}
    jobs = wf["jobs"]
    assert set(jobs) == {"observe", *RESEARCH_JOBS, "referee_e1", "referee_e2", "check", "evaluate", "publish"}
    assert jobs["publish"]["permissions"] == {"contents": "write"}
    assert all(j["permissions"] == {"contents": "read"} for n, j in jobs.items() if n != "publish")
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("secrets.ANTHROPIC_API_KEY") == 20 and "secrets." not in text.replace(
        "secrets.ANTHROPIC_API_KEY", "")
    assert "actions/cache" not in text and "HF_TOKEN" not in text and "pattern:" not in text
    for job in jobs.values():
        assert all(st["with"].get("name") for st in _downloads(job))


def test_research_jobs_get_only_their_period_and_k_only_its_memory(wf):
    jobs = wf["jobs"]
    for j in RESEARCH_JOBS:
        job = jobs[j]
        e, cond, c = int(j[1]), ("E1" if j.startswith("e1") else j[2].upper()), j.split("_")[1]
        names = [st["with"]["name"] for st in _downloads(job)]
        expect = [f"fk-observed-{c}e{e}-${{{{ github.run_id }}}}"]
        if cond == "K":
            expect.append(f"fk-memory-{c}-e{e - 1}-${{{{ github.run_id }}}}")
        assert names == expect, j
        steps = _secret_steps(job)
        assert len(steps) == 1
        run = steps[0]["run"]
        assert f"final_kernel.lab.run loop --condition {cond} " in run
        assert ("--memory memory/memory.txt" in run) == (cond == "K")
        assert steps[0]["env"]["HF_HUB_OFFLINE"] == "1"
        assert [k for k, v in steps[0]["env"].items() if "secrets." in v] == ["ANTHROPIC_API_KEY"]
        if cond == "K":
            assert steps[0]["env"]["MEM_SHA"] == f"${{{{ needs.referee_e{e - 1}.outputs.{c}_memory }}}}"
        patterns = job["steps"][0]["with"]["sparse-checkout"]
        assert all(f"!/{d}/" in patterns for d in TRUTH_DIRS) and "!/tests/" in patterns
        guard = job["steps"][1]["run"]
        assert "rm -rf .git" in guard and all(d in guard for d in TRUTH_DIRS) and "GITHUB_RUN_ATTEMPT" in guard
        assert "episode_world" in guard


def test_at_most_four_researcher_jobs_can_run_at_once(wf):
    jobs = wf["jobs"]
    waves = [[f"e1_c{i}" for i in range(1, 5)], [f"e2f_c{i}" for i in range(1, 5)],
             [f"e2k_c{i}" for i in range(1, 5)], [f"e3f_c{i}" for i in range(1, 5)], [f"e3k_c{i}" for i in range(1, 5)]]
    for prev, wave in zip(waves, waves[1:]):
        for j in wave:
            assert set(prev) <= set(jobs[j]["needs"]), j
    assert {"referee_e1"} <= set(jobs["e2k_c1"]["needs"]) and {"referee_e2"} <= set(jobs["e3k_c1"]["needs"])
    assert set(jobs["referee_e1"]["needs"]) == {"observe", *waves[0]}
    assert set(jobs["referee_e2"]["needs"]) == {"observe", "referee_e1", *waves[2]}
    for r in ("referee_e1", "referee_e2"):
        assert _secret_steps(jobs[r]) == []
        assert all(f"!/{d}/" in jobs[r]["steps"][0]["with"]["sparse-checkout"] for d in TRUTH_DIRS)


def test_the_guard_passes_on_what_the_research_checkout_keeps():
    pattern = re.compile(r"^def (make_world|pair_world|kernel_world|episode_world)", re.MULTILINE)
    files = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True,
                           check=True).stdout.split()
    files += [str(p.relative_to(ROOT)) for p in PKG.rglob("*.py")]
    kept = [f for f in set(files) if not f.startswith(tuple(d + "/" for d in TRUTH_DIRS) + ("tests/",))]
    assert kept and not [f for f in kept if (ROOT / f).is_file()
                         and pattern.search((ROOT / f).read_text(encoding="utf-8"))]


# ----------------------------------------------------------------- the freeze

FROZEN_SHA256 = {
    "docs/research_loop_proof/FINAL_KERNEL_SPEC.md":
        "879e8db75db9fb7e051a6d016bf00e7d3fc10ead9803405ee42e0696c3f7df67",
    "research_loop_proof/final_kernel/lab/researcher.py":
        "6a14525bbed6f604c220688b5e9e6cefef058e7d9372644a7afb8ef96cc19c47",
    "research_loop_proof/final_kernel/lab/referee.py":
        "e2450ab8992e91b82f92c0d50aa51b5717958545deadd996f21dbc0e60421848",
    "research_loop_proof/final_kernel/lab/run.py":
        "330677d4020483a85ceec32fd61c2f32ff3aa8fe0507890ed808238932d45c4a",
    "research_loop_proof/final_kernel/truth/companies.py":
        "813e8cfb1667bffe06fd18b6015cf7bc563bfec18434aa4edbbf4d6d1568e3bb",
    "research_loop_proof/final_kernel/truth/world.py":
        "e803d12f0e3fd63a77b787ba2b6cc849b9cfbe67bf0bff39b06eac09d876642f",
    "research_loop_proof/final_kernel/truth/observe.py":
        "e2ae6fc117d4d5b6623bce98706671bf87b01324d9b7a631b60cddf26ce145ca",
    "research_loop_proof/final_kernel/truth/rules.py":
        "4a3d9810e5c09958655945ded34153ad4cef824574c51018c59be7178623f3b3",
    "research_loop_proof/final_kernel/truth/evaluate.py":
        "2bad23e7f5f4fb2567cc57464ca4455f5e0d6d2c3ce18d9996f28d0baec6a694",
    "research_loop_proof/final_kernel/truth/preflight.py":
        "241b8da3ec49b643ed2723fa632bb90602a1efee87379f1148e05a32cd7777b7",
    ".github/workflows/research-loop-final-kernel.yml":
        "3ed96eda9021deeaf3ba030a76cc71aedae41e2844eb7984acbb0e54723dfb61",
}
SPEC_SHA = "4c488b9dc7a8b2c76b00794da8e5bd8709dfab5fad9cfc8946e2eadc80f7a149"


def test_the_frozen_files_and_the_spec_hash_are_pinned():
    assert fspec.missing() == []
    assert set(kspec.FROZEN) <= set(fspec.FROZEN)
    got = fspec.file_hashes()
    assert {rel: got[rel] for rel in FROZEN_SHA256} == FROZEN_SHA256
    assert set(FROZEN_SHA256) == {rel for rel in fspec.FROZEN if rel not in kspec.FROZEN}
    assert fspec.spec_sha() == SPEC_SHA
