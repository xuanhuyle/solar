"""Experiment 4's frozen spec: pinned hash, structure, and nothing in it reaches the forward zone."""

from __future__ import annotations

import re

from solarbench import price_spec as ps


def test_spec_hash_is_pinned():
    assert ps.PRICE_SPEC_SHA256 is not None, "PRICE_SPEC_SHA256 must be pinned when the spec is frozen"
    assert ps.spec_sha256() == ps.PRICE_SPEC_SHA256


def test_four_primaries_with_rules():
    probes = ps.PRICE_SPEC["probes"]
    assert [p["id"] for p in probes] == ["P1", "P2", "P3", "P4"] == ps.PRICE_SPEC["statistics"]["family"]
    for p in probes:
        assert all(p[k] for k in ("question", "t0_arm", "comparator", "metric", "success", "days"))
    assert {p["comparator"] for p in probes} == {"best_simple_2023", "lear_ens", "best_simple_eq", "t0_cal"}


def test_no_period_reaches_the_forward_zone():
    dates = re.findall(r"\b(20\d\d-\d\d-\d\d)\b", repr(ps.PRICE_SPEC["periods"]) + repr(ps.TEST_ORIGINS))
    assert dates and all(d <= "2026-01-01" for d in dates)
    assert all(d <= "2025-12-31" for d in ps.TEST_ORIGINS)


def test_reading_table_covers_every_state():
    rt = ps.PRICE_SPEC["reading_table"]
    for key in ("P1 won, P2 won", "P1 won, P2 lost or not stable", "P1 won, P2 not runnable", "P1 not won, P2 won",
                "P1 not won, P2 not won", "P3 won", "P3 lost on coverage", "P3 lost or not stable", "P4 won",
                "P4 lost or not stable", "P4 not runnable", "not stable", "strict"):
        assert rt[key]


def test_avail_is_not_hashed_and_the_guard_needs_it():
    import pytest

    before = ps.spec_sha256()
    saved = dict(ps.AVAIL)
    try:
        ps.AVAIL["price_stamp"] = "start"
        assert ps.spec_sha256() == before
        ps.AVAIL.update({k: None for k in ps.AVAIL})
        with pytest.raises(RuntimeError, match="AVAIL not filled"):
            ps.require_frozen()
    finally:
        ps.AVAIL.update(saved)


def test_k1_references_are_the_pinned_published_values():
    k1 = ps.PRICE_SPEC["gates"]["K1"]
    assert k1["published_mae"]["LEAR Ensemble"] == 3.9798
    assert "671d65842180fd7fc0f603eca6281f4ddc581983cbfb4991e97e291d5d88ab08" in k1["reference"]


def test_one_pager_is_frozen():
    """The plain-language restatement is frozen with the spec (owner: 'preserve Experiment 4 exactly as frozen')."""
    import hashlib
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "docs" / "experiment_4" / "ONE_PAGER.md"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == \
        "625af31f1d185e7f89d4aa53f7771d48447327ac8112d46c8653e451d53f04fa"


def test_frozen_spec_hash_is_the_exp4_spec_commits():
    """aa28301 pinned this hash before any price was fetched; it may never change."""
    assert ps.PRICE_SPEC_SHA256 == "225774c89e301166c2d4850e2f894335fd5ae703dc410bc4a06aa246ac5755bc"


def test_amendment_record_is_pinned():
    """Amendments sit beside the frozen spec, never inside it; their record may not change silently."""
    import hashlib
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "docs" / "experiment_4" / "AMENDMENTS.md"
    text = path.read_text(encoding="utf-8")
    assert "## A1 (2026-09-30)" in text and "treat attempt 3 as final regardless of outcome" in text
    assert hashlib.sha256(path.read_bytes()).hexdigest() == AMENDMENTS_SHA256


AMENDMENTS_SHA256 = "729b756c9c85956f0c14744863cd96367324ec265b5c777ff6c438971e8cf9d7"
