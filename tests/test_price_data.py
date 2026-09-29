"""Experiment 4's price door: zone guard, inward bounds, forward refusal, hourly aggregation (offline)."""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd
import pytest

from engine import zones
from solarbench import price_data as pdm

SWITCH = zones.local_midnight_utc(pdm.QUARTER_HOUR_FROM)


def _raw(hours_before: int = 5, quarters: int = 8) -> pd.Series:
    h = pd.date_range(SWITCH - pd.Timedelta(hours=hours_before), SWITCH - pd.Timedelta(hours=1), freq="1h", tz="UTC")
    q = pd.date_range(SWITCH, SWITCH + pd.Timedelta(minutes=15 * (quarters - 1)), freq="15min", tz="UTC")
    return pd.concat([pd.Series(np.arange(len(h), dtype=float), index=h),
                      pd.Series(10.0 * np.arange(len(q)), index=q)])


def test_quarter_hours_average_into_start_stamped_hours():
    out, info = pdm.to_hourly(_raw())
    assert out[SWITCH] == np.mean([0, 10, 20, 30]) and out[SWITCH + pd.Timedelta(hours=1)] == np.mean([40, 50, 60, 70])
    assert out[SWITCH - pd.Timedelta(hours=1)] == 4.0 and info["hours_from_quarters"] == 2


def test_an_hour_missing_a_quarter_is_missing_not_its_lone_value():
    raw = _raw().drop(SWITCH + pd.Timedelta(minutes=75))
    out, info = pdm.to_hourly(raw)
    assert np.isnan(out[SWITCH + pd.Timedelta(hours=1)]) and info["incomplete_quarter_hours"] == 1
    lone = pd.concat([_raw(quarters=4), pd.Series([99.0], index=[SWITCH + pd.Timedelta(hours=1)])])
    assert np.isnan(pdm.to_hourly(lone)[0][SWITCH + pd.Timedelta(hours=1)])


def test_end_stamped_sources_give_the_same_hours():
    raw = _raw()
    ends = [t + (pd.Timedelta(hours=1) if t < SWITCH else pd.Timedelta(minutes=15)) for t in raw.index]
    end_raw = pd.Series(raw.to_numpy(), index=pd.DatetimeIndex(ends))
    a, _ = pdm.to_hourly(raw, stamp="start")
    b, _ = pdm.to_hourly(end_raw, stamp="end")
    pd.testing.assert_series_equal(a, b)
    with pytest.raises(ValueError):
        pdm.to_hourly(raw, stamp="middle")


def test_negative_prices_pass_through_untouched():
    raw = _raw()
    raw.iloc[:3] = [-5.0, -0.01, -120.0]
    out, _ = pdm.to_hourly(raw)
    assert (out.dropna() < 0).sum() == 3


def test_bounds_are_inward_paris_days_and_refuse_the_forward_zone():
    lo, hi = pdm.unix_bounds("2025-12-01", "2025-12-31")
    assert pd.Timestamp(lo, unit="s", tz="UTC") == pd.Timestamp("2025-11-30 23:00", tz="UTC")
    assert pd.Timestamp(hi, unit="s", tz="UTC") == pd.Timestamp("2025-12-31 22:59:59", tz="UTC")
    with pytest.raises(zones.ZoneError):
        pdm.unix_bounds("2025-12-31", "2026-01-01")
    assert pdm.month_chunks("2023-11-27", "2024-01-03")[0] == (date(2023, 11, 27), date(2023, 11, 30))


def test_smard_never_requests_the_week_that_reaches_2026():
    weeks = pd.date_range("2025-12-08", periods=6, freq="7D", tz=zones.PARIS).tz_convert("UTC")
    ms = [int(t.timestamp() * 1000) for t in weeks]
    picked = pdm.smard_chunks_to_fetch(ms, "2025-12-01", "2025-12-31")
    picked_starts = [pd.Timestamp(t, unit="ms", tz="UTC") for t in picked]
    assert all(t + pd.Timedelta(days=7) <= pdm.forward_limit() for t in picked_starts)
    assert pd.Timestamp("2025-12-29", tz=zones.PARIS).tz_convert("UTC") not in picked_starts


class _Resp:
    def __init__(self, body: dict, status: int = 200):
        self.content = json.dumps(body).encode()
        self.status_code = status
        self.headers = {}
        self.text = self.content.decode()

    def json(self):
        return json.loads(self.content)


class _Session:
    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def get(self, url, params=None, timeout=None, headers=None):
        self.calls.append((url, params))
        return self.reply(url, params)


def test_energy_charts_cache_manifest_and_forward_refusal(tmp_path):
    def ok(url, params):
        start = int(params["start"])
        return _Resp({"unix_seconds": [start, start + 3600], "price": [50.0, None], "license_info": "CC BY 4.0 x"})

    s = _Session(ok)
    paths = pdm.fetch_energy_charts("2024-01-01", "2024-02-10", tmp_path, session=s)
    assert len(paths) == 2 and len(s.calls) == 2
    series, licences = pdm.load_energy_charts(paths)
    assert series.notna().sum() == 2 and licences == {"CC BY 4.0 x"}
    manifest = (tmp_path / "energy-charts-v1" / "manifest.jsonl").read_text().splitlines()
    assert len(manifest) == 2 and all("sha256" in json.loads(m) for m in manifest)
    pdm.fetch_energy_charts("2024-01-01", "2024-02-10", tmp_path, session=s)  # cached: no new request
    assert len(s.calls) == 2

    def leaky(url, params):
        return _Resp({"unix_seconds": [int(pdm.forward_limit().timestamp())], "price": [1.0]})

    with pytest.raises(pdm.PriceDataError, match="outside"):
        pdm.fetch_energy_charts("2025-12-01", "2025-12-31", tmp_path / "b", session=_Session(leaky))
    assert not list((tmp_path / "b" / "energy-charts-v1").glob("*.json"))  # nothing out of bounds is cached


def test_licence_rule():
    assert pdm.licence_ok("CC BY 4.0 from Bundesnetzagentur | SMARD.de (https://...)")
    assert not pdm.licence_ok("for private and internal use only") and not pdm.licence_ok(None)


def test_conflicting_repeated_stamps_are_refused():
    t = pd.DatetimeIndex([pd.Timestamp("2024-01-01", tz="UTC")] * 2)
    with pytest.raises(pdm.PriceDataError):
        pdm._merge([pd.Series([1.0], index=t[:1]), pd.Series([2.0], index=t[1:])], "x")


def test_compare_sources_counts_disagreements():
    idx = pd.date_range("2024-01-01", periods=48, freq="1h", tz="UTC")
    a = pd.Series(np.arange(48.0), index=idx)
    b = a.copy()
    b.iloc[5] += 1.0
    rep = pdm.compare_sources(a, b, start="2024-01-01", end="2024-01-01")
    # 2024-01-01 Paris = 2023-12-31 23:00Z .. 2024-01-01 23:00Z: the first hour is missing in both (a disagreement)
    assert rep["hours"] == 24 and rep["hours_differing"] == 2 and rep["missing_a"] == 1


def test_stamp_test_tells_start_from_end_by_content():
    local = pd.date_range("2015-03-02", "2015-03-20 23:00", freq="1h")  # naive Paris hours, no DST switch
    rng = np.random.default_rng(1)
    epf = pd.Series(rng.normal(40, 10, len(local)), index=local)
    starts = local.tz_localize(zones.PARIS).tz_convert("UTC")
    as_start = pd.Series(epf.to_numpy(), index=starts)
    as_end = pd.Series(epf.to_numpy(), index=starts + pd.Timedelta(hours=1))
    assert pdm.stamp_test(as_start, epf)["verdict"] == "start"
    assert pdm.stamp_test(as_end, epf)["verdict"] == "end"
    shuffled = pd.Series(rng.permutation(epf.to_numpy()), index=starts)
    assert pdm.stamp_test(shuffled, epf)["verdict"] is None
