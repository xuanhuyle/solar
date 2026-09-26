"""Engine zones and the data door: forward data is refused before any request."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine import data, zones
from solarbench import odre, weather


def _no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network touched")

    monkeypatch.setattr(odre.requests, "get", boom)
    monkeypatch.setattr(weather.requests, "get", boom)


def test_forward_boundary_is_paris_midnight():
    assert zones.local_midnight_utc(zones.FORWARD_FROM) == pd.Timestamp("2025-12-31 23:00", tz="UTC")
    assert zones.zone_of("2025-12-31") == "discovery" and zones.zone_of("2026-01-01") == "forward"
    assert zones.zone_of("2021-12-31") == "before"


def test_request_bounds_round_inward_across_dst():
    # winter end: local midnight 2026-01-01 = 23:00 UTC on 2025-12-31 -> exclusive UTC date 2025-12-31
    assert zones.utc_request_days("2022-01-01", "2025-12-31") == ("2021-12-31", "2025-12-31")
    # summer end: local midnight = 22:00 UTC the day before
    assert zones.utc_request_days("2024-06-01", "2024-06-30")[1] == "2024-06-30"
    for end in ("2024-03-31", "2024-10-27", "2025-12-31"):
        _, b = zones.utc_request_days("2024-01-01", end)
        assert pd.Timestamp(b, tz="UTC") <= zones.local_midnight_utc(pd.Timestamp(end) + pd.Timedelta(days=1))


def test_consumed_and_forward_rules():
    assert not zones.confirmable("2025-07-01")  # consumed by C1
    assert not zones.confirmable("2024-07-01")  # discovery
    assert zones.confirmable("2026-07-01")
    zones.assert_readable("2021-10-01", "2025-12-31")  # context may reach back
    with pytest.raises(zones.ZoneError):
        zones.assert_readable("2025-12-01", "2026-01-01")
    with pytest.raises(zones.ZoneError):
        zones.assert_discovery("2021-12-01", "2022-01-31")


def test_forward_reads_are_refused_before_any_request(tmp_path, monkeypatch):
    _no_network(monkeypatch)
    with pytest.raises(zones.ZoneError):
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2025-12-01", "2026-01-02", tmp_path)
    with pytest.raises(zones.ZoneError):
        data.fetch_weather_previous_runs("ecmwf_ifs025", ["temperature_2m_previous_day3"], "2026-01-01",
                                         "2026-01-31", tmp_path, points={"p": (48.8, 2.3)})
    forged = data.ForwardAccess("B1", "0" * 64, "2026-01-01", "2026-03-31")
    with pytest.raises(zones.ZoneError):  # no vault yet: every access is invalid
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2026-01-01", "2026-01-31", tmp_path, access=forged)


def test_discovery_reads_request_inward_bounds(tmp_path, monkeypatch):
    seen = {}

    def fake(dataset, columns, start, end, cache_dir, **k):
        seen.update(dataset=dataset, start=start, end=end)
        idx = pd.date_range("2025-12-30 00:00", "2025-12-30 23:30", freq="30min", tz="UTC")
        path = tmp_path / "f.csv"
        pd.DataFrame({"date_heure": idx.strftime("%Y-%m-%dT%H:%M:%S+00:00"), "perimetre": "France",
                      "nature": "x", "consommation": np.arange(len(idx), dtype=float)}).to_csv(path, sep=";", index=False)
        return path

    monkeypatch.setattr(odre, "_download_columns", fake)
    series = data.load_odre(data.NATIONAL, "consommation", "2025-12-01", "2025-12-31", tmp_path)
    assert seen["end"] == "2025-12-31" and series.index.max() < zones.local_midnight_utc("2026-01-01")


def test_rows_past_the_end_are_caught():
    idx = pd.date_range("2025-12-31 22:00", "2025-12-31 23:30", freq="30min", tz="UTC")
    with pytest.raises(zones.ZoneError):
        data.assert_rows_within(pd.Series(1.0, index=idx), "2025-12-31")
    data.assert_rows_within(pd.Series([1.0, 1.0, np.nan, np.nan], index=idx), "2025-12-31")  # NaN rows are not data
