"""t0-alpha pinned by content (owner's decision, 2026-09-30): the two files are fetched from the repository's
current head and the model is built only when both match the frozen sha256; any mismatch aborts before a
forecast. Offline: a tiny t0 saved locally stands in for the Hub."""

from __future__ import annotations

import pytest

from solarbench import price_spec as ps
from solarbench import t0_pinned

FROZEN = ps.PRICE_SPEC["t0"]["revision"]
REPO = ps.PRICE_SPEC["t0"]["repo_id"]


def tiny_t0_dir(tmp_path, dropout=0.0):
    from t0 import T0Forecaster

    m = T0Forecaster(embed_dim=16, num_layers=1, num_heads=2, mlp_hidden_dim=32, patch_size=16, group_every_n=1,
                     dropout=dropout, quantile_levels=[0.1, 0.25, 0.5, 0.75, 0.9])
    d = tmp_path / f"snap-{dropout}"
    m.save_pretrained(d)
    return d


def pin_to(monkeypatch, directory):
    monkeypatch.setitem(t0_pinned.PINNED_SHA256, FROZEN,
                        {n: t0_pinned.sha256_file(directory / n) for n in t0_pinned.FILES})


def test_the_frozen_revision_and_its_hashes_are_pinned():
    assert list(t0_pinned.PINNED_SHA256) == [FROZEN]
    pins = t0_pinned.PINNED_SHA256[FROZEN]
    assert set(pins) == set(t0_pinned.FILES) and all(len(v) == 64 for v in pins.values())
    assert pins["model.safetensors"] == "16c030d3fd70f06dc4238e9a8356e9b5a631d07f80f1bc76ba539991aed5897f"


def test_the_files_come_from_the_current_head_and_load_only_when_they_match(tmp_path, monkeypatch):
    good = tiny_t0_dir(tmp_path)
    pin_to(monkeypatch, good)
    asked = []

    def download(repo, rev):
        asked.append(rev)
        return good

    local, record = t0_pinned.fetch(REPO, FROZEN, download=download, head=lambda repo: "headrev")
    assert asked == ["headrev"] and local == good  # never the vanished frozen revision id
    assert record["served_by_revision"] == "headrev" and record["frozen_revision"] == FROZEN and record["verified"]


def test_any_mismatch_or_missing_file_aborts(tmp_path, monkeypatch):
    good, other = tiny_t0_dir(tmp_path), tiny_t0_dir(tmp_path, dropout=0.1)  # a different config.json
    pin_to(monkeypatch, good)
    with pytest.raises(t0_pinned.PinnedWeightsError, match="does not hold the frozen bytes"):
        t0_pinned.fetch(REPO, FROZEN, download=lambda r, v: other, head=lambda r: "headrev")
    (tmp_path / "partial").mkdir()
    (tmp_path / "partial" / "config.json").write_bytes((good / "config.json").read_bytes())
    with pytest.raises(t0_pinned.PinnedWeightsError):
        t0_pinned.fetch(REPO, FROZEN, download=lambda r, v: tmp_path / "partial", head=lambda r: "headrev")
    with pytest.raises(t0_pinned.PinnedWeightsError, match="no pinned sha256"):
        t0_pinned.fetch(REPO, "another-revision", download=lambda r, v: good, head=lambda r: "headrev")


def test_a_mismatch_builds_no_model(tmp_path, monkeypatch):
    good, other = tiny_t0_dir(tmp_path), tiny_t0_dir(tmp_path, dropout=0.1)
    pin_to(monkeypatch, good)
    built = []
    import t0

    real = t0.T0Forecaster.from_pretrained
    monkeypatch.setattr(t0.T0Forecaster, "from_pretrained", classmethod(
        lambda cls, *a, **k: built.append(a) or real.__func__(cls, *a, **k)))
    real_fetch = t0_pinned.fetch
    monkeypatch.setattr(t0_pinned, "fetch", lambda repo, rev, token=True: real_fetch(
        repo, rev, download=lambda r, v: other, head=lambda r: "headrev"))
    with pytest.raises(t0_pinned.PinnedWeightsError):
        t0_pinned.load(REPO, FROZEN)
    assert built == []
    monkeypatch.setattr(t0_pinned, "fetch", lambda repo, rev, token=True: real_fetch(
        repo, rev, download=lambda r, v: good, head=lambda r: "headrev"))
    model, record = t0_pinned.load(REPO, FROZEN)
    assert type(model).__name__ == "T0Forecaster" and not model.training and record["verified"]
    assert built == [(str(good),)]
