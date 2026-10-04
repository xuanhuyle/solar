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
def test_qualification_runs_end_to_end_with_a_tiny_untrained_beta(tmp_path):
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
