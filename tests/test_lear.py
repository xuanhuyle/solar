"""The clean-room LEAR: DST mapping, scaling, the no-leak window rule, the ensemble (offline, synthetic data)."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from engine import zones
from solarbench import lear

sklearn = pytest.importorskip("sklearn")


def _hourly(start: str, end: str, seed: int = 0) -> pd.Series:
    idx = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(end), freq="1h", tz="UTC",
                        inclusive="left")
    local = idx.tz_convert(zones.PARIS)
    rng = np.random.default_rng(seed)
    base = 50 + 15 * np.sin(2 * np.pi * local.hour / 24) + 5 * (local.dayofweek >= 5)
    return pd.Series(base + rng.normal(0, 3, len(idx)), index=idx)


def test_day_matrix_maps_dst_days_to_24_local_hours():
    s = _hourly("2024-03-30", "2024-04-01")
    m = lear.day_matrix(s, [date(2024, 3, 31)])
    local = s.index.tz_convert(zones.PARIS)
    day = s[local.date == date(2024, 3, 31)]
    assert len(day) == 23 and m.shape == (1, 24)
    by_h = dict(zip(day.index.tz_convert(zones.PARIS).hour, day.to_numpy()))
    assert m.iloc[0, 2] == pytest.approx(0.5 * (by_h[1] + by_h[3]))
    s = _hourly("2024-10-26", "2024-10-28")
    day = s[s.index.tz_convert(zones.PARIS).date == date(2024, 10, 27)]
    m = lear.day_matrix(s, [date(2024, 10, 27)])
    assert len(day) == 25
    twos = day[day.index.tz_convert(zones.PARIS).hour == 2].to_numpy()
    assert m.iloc[0, 2] == pytest.approx(twos.mean())
    back = lear.to_utc_hours(date(2024, 10, 27), m.iloc[0].to_numpy())
    assert len(back) == 25 and back.iloc[2] == back.iloc[3] == pytest.approx(twos.mean())


def test_a_missing_hour_makes_the_day_missing():
    s = _hourly("2024-01-01", "2024-01-03")
    s.iloc[5] = np.nan
    m = lear.day_matrix(s, [date(2024, 1, 1), date(2024, 1, 2)])
    assert m.iloc[0].isna().all() and m.iloc[1].notna().all()


def test_invariant_scaler_roundtrip_and_zero_mad_fallback():
    x = np.column_stack([np.arange(10.0), np.r_[np.zeros(8), 1.0, 2.0], np.full(10, 3.0)])
    sc = lear.InvariantScaler.fit(x)
    assert sc.fallbacks == 2 and sc.scale[2] == 1.0 and sc.scale[1] == pytest.approx(x[:, 1].std())
    np.testing.assert_allclose(sc.inverse(sc.transform(x)), x, atol=1e-12)


def test_features_layout_and_missing_lag():
    days = pd.date_range("2024-01-01", "2024-01-20").date
    prices = pd.DataFrame(np.arange(len(days) * 24, dtype=float).reshape(len(days), 24), index=list(days))
    row = lear.features(prices, date(2024, 1, 15), extra_dummies=[1.0])
    assert len(row) == 96 + 1 + 7 and row[96] == 1.0 and row[97 + date(2024, 1, 15).weekday()] == 1.0
    assert (row[:24] == prices.loc[date(2024, 1, 14)].to_numpy()).all()  # D-1 first
    assert lear.features(prices, date(2024, 1, 5)) is None  # D-7 before the data


def _prices(n_days: int = 140, seed: int = 0) -> pd.DataFrame:
    s = _hourly("2023-01-01", (date(2023, 1, 1) + timedelta(days=n_days)).isoformat(), seed)
    days = sorted(set(s.index.tz_convert(zones.PARIS).date))[:n_days]
    return lear.day_matrix(s, days)


def test_the_forecast_of_D_never_reads_D_or_later():
    prices = _prices()
    d = prices.index[100]
    base, _ = lear.forecast(prices, [d], window=56)
    poisoned = prices.copy()
    poisoned.loc[[t for t in prices.index if t >= d]] = -7.5 * poisoned.loc[[t for t in prices.index if t >= d]] + 1234.5
    after, _ = lear.forecast(poisoned, [d], window=56)
    np.testing.assert_array_equal(base.to_numpy(), after.to_numpy())
    legal = prices.copy()
    legal.loc[d - timedelta(days=1)] *= 1.5
    moved, _ = lear.forecast(legal, [d], window=56)
    assert not np.array_equal(base.to_numpy(), moved.to_numpy())


def test_window_uses_n_minus_7_training_rows_and_logs_drops():
    prices = _prices()
    d = prices.index[100]
    prices.loc[d - timedelta(days=20)] = np.nan
    f, log = lear.forecast(prices, [d], window=56)
    assert log.forecast_days == 1 and np.isfinite(f.to_numpy()).all()
    # the NaN day is a training target (1 row) and a lag of rows d-19, d-18, d-17, d-13 (4 rows): 5 drops
    assert log.dropped_rows == 5


def test_alpha_ignores_column_scale():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(60, 30))
    y = x[:, 0] - 2 * x[:, 3] + rng.normal(0, 0.5, 60)
    a = lear.aic_alpha(x, y)
    b = lear.aic_alpha(x * np.linspace(1, 50, 30), y)
    assert a == pytest.approx(b, rel=1e-6)


def test_ensemble_needs_every_window():
    a = pd.DataFrame(np.ones((2, 24)), index=[date(2024, 1, 1), date(2024, 1, 2)])
    b = a.copy()
    b.iloc[1, :] = np.nan
    e = lear.ensemble([a, b * 3])
    assert e.iloc[0].eq(2.0).all() and e.iloc[1].isna().all()
