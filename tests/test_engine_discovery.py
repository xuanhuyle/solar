"""Engine catalogue, probe specs and the discovery runner (offline, stub t0)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_probes as tp
from engine import arms as am
from engine import catalogue as cat
from engine import covs, discover
from engine.ledger import EXPLORATORY
from engine.spec import SpecError, spec_sha256, validate_probe
from solarbench.data import STEP


def spec(**over):
    base = {"spec_version": "probe/0", "target": "consumption", "period": "Y2024", "scope": "all",
            "arms": [{"name": "t0_cal", "covariates": [{"id": "holiday", "transform": "raw"}]}],
            "comparisons": [{"arm": "t0_cal", "vs": "best_simple", "metric": "mae"}]}
    base.update(over)
    return base


# ------------------------------------------------------------------ spec


def test_valid_spec_is_normalised_and_hash_ignores_rationale():
    a = validate_probe(spec(rationale="because"))
    b = validate_probe(spec(rationale="another reason", builds_on=[9]))
    assert a["arms"][0]["covariates"] == [{"id": "holiday", "transform": "raw"}]
    assert spec_sha256(a) == spec_sha256(b)
    assert spec_sha256(a) != spec_sha256(validate_probe(spec(period="Y2023")))


@pytest.mark.parametrize("bad, reason", [
    ({"extra": 1}, "unknown field"),
    ({"target": "wind"}, "target"),
    ({"period": "Y2026"}, "period"),
    ({"arms": [{"name": "t0_cal", "covariates": [{"id": "wx_radiation"}]}]}, "not available for target"),
    ({"arms": [{"name": "t0_cal", "covariates": [{"id": "holiday", "transform": "hdd15"}]}]}, "transform"),
    ({"arms": [{"name": "t0_cal", "covariates": [{"id": "wx_temperature"}]}], "period": "Y2023"}, "ends before"),
    ({"arms": [{"name": "best_simple", "covariates": []}]}, "taken"),
    ({"arms": [{"name": "a", "covariates": [], "code": "import os"}]}, "unknown field"),
    ({"comparisons": [{"arm": "t0_cal", "vs": "my_model"}]}, "comparator"),
    ({"comparisons": [{"arm": "t0_cal", "vs": "t0_base", "metric": "rmse"}]}, "metric"),
    ({"rationale": "x" * 801}, "rationale"),
    ({"arms": [{"name": f"a{i}", "covariates": []} for i in range(4)]}, "arms"),
])
def test_invalid_specs_are_refused_with_reasons(bad, reason):
    with pytest.raises(SpecError) as exc:
        validate_probe(spec(**bad))
    assert any(reason in r for r in exc.value.reasons), exc.value.reasons


def test_solar_only_covariates_and_references_stay_on_their_target():
    with pytest.raises(SpecError):
        validate_probe(spec(target="solar", comparisons=[{"arm": "t0_cal", "vs": "rte_j1"}]))
    ok = validate_probe(spec(target="solar", period="Y2024",
                             arms=[{"name": "t0_wx", "covariates": [{"id": "wx_radiation"}, {"id": "geometry"}]}],
                             comparisons=[{"arm": "t0_wx", "vs": "t0_base"}]))
    assert ok["arms"][0]["covariates"][0]["id"] == "geometry"  # sorted


def test_catalogue_brief_is_stable_and_lists_every_entry():
    brief = cat.catalogue_brief()
    assert brief == cat.catalogue_brief() and cat.catalogue_sha256()[:16] in brief
    for key in [*cat.TARGETS, *cat.COVARIATES, *cat.COMPARATORS, *cat.PERIODS]:
        assert key in brief


def test_bridge_days_follow_the_holiday_calendar():
    assert covs.bridge_days(2024) == {date(2024, 5, 10), date(2024, 8, 16)}
    assert date(2025, 11, 10) in covs.bridge_days(2025)  # Monday before Tuesday 11 November


# --------------------------------------------------------------- discovery


def consumption_bundle(with_temperature=True) -> am.DataBundle:
    index = pd.date_range("2023-09-01", "2024-12-31 22:30", freq=STEP, tz="UTC")
    local = index.tz_convert("Europe/Paris")
    rng = np.random.default_rng(1)
    y = (50_000 + 8_000 * np.sin((local.hour + local.minute / 60) / 24 * 2 * np.pi)
         - 6_000 * (local.dayofweek >= 5) + rng.normal(0, 700, len(index)))
    series = pd.Series(y, index=index)
    weather = {}
    if with_temperature:
        hours = pd.date_range("2024-02-06", "2024-12-31 23:00", freq="h", tz="UTC")
        weather["temperature"] = pd.Series(12 + 8 * np.sin(np.arange(len(hours)) / 24 / 365 * 2 * np.pi), index=hours)
    return am.DataBundle("consumption", series, series * 1.01, weather, {"synthetic": True})


def test_probe_runs_end_to_end_and_is_exploratory():
    s = spec(arms=[{"name": "t0_cal", "covariates": [{"id": "holiday"}]}, {"name": "t0_plain", "covariates": []}],
             comparisons=[{"arm": "t0_cal", "vs": "best_simple"}, {"arm": "t0_plain", "vs": "accepted"},
                          {"arm": "t0_cal", "vs": "rte_j1"}])
    out = discover.run_probe(s, cache_dir=Path("."), bundle=consumption_bundle(False), model=tp.QuantModel(),
                             accepted=am.latest_accepted([], "consumption"), limit_days=12)
    assert out["status"] == EXPLORATORY and len(out["probe_sha256"]) == 64
    assert [c["days"] for c in out["comparisons"]] == [12, 12, 12]
    assert all(np.isfinite(c["skill"]) and len(c["ci95"]) == 2 for c in out["comparisons"])
    assert out["comparisons"][2]["note"].startswith("reference only")
    assert out["methods"]["best_simple"]["scored_as"] == "blend_50"
    assert "HolidayCovariate" in str(out["methods"]["accepted"]["spec"])  # C1's arm
    assert len(out["per_day"]["dates"]) == 12 and set(out["per_day"]["mae_mw"]) >= {"t0_cal", "best_simple"}


def test_weather_arms_score_only_the_days_their_archive_covers():
    s = spec(arms=[{"name": "t0_temp", "covariates": [{"id": "wx_temperature", "transform": "hdd15"}]}],
             comparisons=[{"arm": "t0_temp", "vs": "t0_base"}])
    out = discover.run_probe(s, cache_dir=Path("."), bundle=consumption_bundle(), model=tp.QuantModel())
    elig = out["methods"]["t0_temp"]["eligible_days"]
    assert 0 < elig < out["windows_built"] and out["methods"]["t0_base"]["eligible_days"] == out["windows_built"]
    first = pd.Timestamp(out["per_day"]["dates"][0])
    assert out["comparisons"][0]["days"] == elig
    t0_temp_days = [d for d, v in zip(out["per_day"]["dates"], out["per_day"]["mae_mw"]["t0_temp"]) if v is not None]
    assert pd.Timestamp(t0_temp_days[0]) >= pd.Timestamp("2024-05-04") and first == pd.Timestamp("2024-01-01")


def test_temperature_covariate_is_issued_before_every_gate():
    bundle = consumption_bundle()
    provider = covs.build_covariate("wx_temperature", "raw", bundle)
    times = bundle.target.index[(bundle.target.index >= "2024-06-01") & (bundle.target.index < "2024-06-03")]
    issued = provider.issued_at(times)
    lead = (times - issued).min()
    assert lead >= pd.Timedelta(hours=24 * covs.TEMPERATURE_LEAD_DAYS - 10 - 1)
    hdd = covs.build_covariate("wx_temperature", "hdd15", bundle)
    assert np.all(hdd.values(times) >= 0) and hdd.name == "wx_temperature_hdd15"
