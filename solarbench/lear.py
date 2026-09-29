"""LEAR, the standard free day-ahead price model (Lago, Marcjasz, De Schutter & Weron, 2021), clean-room.

Written from the paper's description with numpy and scikit-learn; no code of
the authors' toolbox is used. Per delivery day D and local hour h, one LASSO
maps the day-ahead features to the price of hour h:

* the prices of D-1, D-2, D-3 and D-7 (24 local hours each);
* each exogenous series at D, D-1 and D-7 (24 each), if any;
* extra dummies of D (Experiment 4: a French-holiday dummy);
* 7 weekday dummies of D.

Every non-dummy column and the 24 targets are put through the "invariant"
transform: ``asinh((x - median) / MAD)`` with the normal-consistent MAD
(``median |x - median| / 0.6745``), fitted per column on the calibration
window. The penalty of each hour is chosen by LARS with the AIC, computed as
the reference implementation's scikit-learn version did (``normalize=True``:
columns centred and scaled to unit L2 norm; noise variance ``var(y)``), and the
LASSO is then refitted with that penalty on the transformed, unnormalised
design. A calibration window of N days is the last N days of data before D; the
first 7 of them serve only as lags, so it gives N - 7 training days.

Days are 24 local hours: on a 23-hour day the missing local 02:00 is the mean
of 01:00 and 03:00; on a 25-hour day the two 02:00 hours are averaged
(``day_matrix``). ``to_utc_hours`` maps a 24-hour forecast back to the real
hours of the day.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Sequence

import numpy as np
import pandas as pd

from engine import zones

MAD_NORMAL = 0.6744897501960817  # the 0.75 quantile of the standard normal
LAGS = (1, 2, 3, 7)
EXOG_LAGS = (0, 1, 7)
WINDOWS = (56, 84, 1092, 1456)


# ------------------------------------------------------------ day matrices


def day_matrix(hourly: pd.Series, days: Sequence[date]) -> pd.DataFrame:
    """``[len(days), 24]`` local-hour values from an hourly, start-stamped UTC series (DST rule above).

    A day with any of its real hours missing is all NaN.
    """
    rows = []
    for d in days:
        a, b = zones.local_midnight_utc(d), zones.local_midnight_utc(d + timedelta(days=1))
        vals = hourly.reindex(pd.date_range(a, b, freq="1h", tz="UTC", inclusive="left"))
        n = len(vals)
        if vals.isna().any() or n not in (23, 24, 25):
            rows.append(np.full(24, np.nan))
            continue
        local_h = vals.index.tz_convert(zones.PARIS).hour
        v = vals.to_numpy(dtype="float64")
        if n == 24:
            rows.append(v)
        elif n == 23:  # spring: local 02:00 does not exist
            by_h = dict(zip(local_h, v))
            by_h[2] = 0.5 * (by_h[1] + by_h[3])
            rows.append(np.array([by_h[h] for h in range(24)]))
        else:  # autumn: local 02:00 happens twice
            out = np.zeros(24)
            for h in range(24):
                out[h] = v[local_h == h].mean()
            rows.append(out)
    return pd.DataFrame(np.vstack(rows) if rows else np.zeros((0, 24)), index=list(days))


def to_utc_hours(day: date, forecast24: np.ndarray) -> pd.Series:
    """A 24-local-hour forecast placed on the real UTC hours of ``day`` (a repeated hour gets it twice)."""
    a, b = zones.local_midnight_utc(day), zones.local_midnight_utc(day + timedelta(days=1))
    idx = pd.date_range(a, b, freq="1h", tz="UTC", inclusive="left")
    local_h = idx.tz_convert(zones.PARIS).hour
    return pd.Series(np.asarray(forecast24, dtype="float64")[local_h], index=idx)


# --------------------------------------------------------------- features


def features(prices: pd.DataFrame, day: date, *, exog: Sequence[pd.DataFrame] = (),
             extra_dummies: Sequence[float] = ()) -> np.ndarray | None:
    """The feature row of delivery day ``day`` (``None`` if any input is missing).

    ``prices`` and each ``exog`` are day matrices indexed by date. Layout:
    price lags, then exogenous series, then extra dummies, then 7 weekday dummies.
    """
    parts = []
    for lag in LAGS:
        d = day - timedelta(days=lag)
        if d not in prices.index:
            return None
        parts.append(prices.loc[d].to_numpy())
    for x in exog:
        for lag in EXOG_LAGS:
            d = day - timedelta(days=lag)
            if d not in x.index:
                return None
            parts.append(x.loc[d].to_numpy())
    row = np.concatenate(parts + [np.asarray(extra_dummies, dtype="float64"), np.eye(7)[day.weekday()]])
    return None if not np.isfinite(row).all() else row


# ---------------------------------------------------------------- scaling


@dataclass
class InvariantScaler:
    """Per-column asinh((x - median) / s), s = normal-consistent MAD.

    If a column's MAD is 0, s is its population standard deviation, and 1 if
    that is 0 too; ``fallbacks`` counts those columns.
    """

    median: np.ndarray
    scale: np.ndarray
    fallbacks: int = 0

    @classmethod
    def fit(cls, x: np.ndarray) -> "InvariantScaler":
        med = np.median(x, axis=0)
        mad = np.median(np.abs(x - med), axis=0) / MAD_NORMAL
        sd = x.std(axis=0, ddof=0)
        scale = np.where(mad > 0, mad, np.where(sd > 0, sd, 1.0))
        return cls(med, scale, int((mad <= 0).sum()))

    def transform(self, x: np.ndarray) -> np.ndarray:
        return np.arcsinh((x - self.median) / self.scale)

    def inverse(self, z: np.ndarray) -> np.ndarray:
        return np.sinh(z) * self.scale + self.median


# ---------------------------------------------------------------- the model


def aic_alpha(x: np.ndarray, y: np.ndarray) -> float:
    """The LARS-AIC penalty as the reference version computed it (normalize=True, noise variance var(y))."""
    from sklearn.linear_model import LassoLarsIC

    xc = x - x.mean(axis=0)
    norms = np.sqrt((xc ** 2).sum(axis=0))
    xn = xc / np.where(norms > 0, norms, 1.0)
    var = float(np.var(y))
    model = LassoLarsIC(criterion="aic", max_iter=2500, noise_variance=var if var > 0 else 1.0)
    return float(model.fit(xn, y).alpha_)


def fit_predict_day(x_train: np.ndarray, y_train: np.ndarray, x_next: np.ndarray, n_dummies: int
                    ) -> tuple[np.ndarray, int]:
    """Fit the 24 hourly LASSOs on one calibration window and forecast the next day (24 local hours).

    The last ``n_dummies`` columns are dummies and are never transformed.
    Returns the forecast and the number of scale fallbacks.
    """
    import warnings

    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import Lasso

    k = x_train.shape[1] - n_dummies
    sx = InvariantScaler.fit(x_train[:, :k])
    sy = InvariantScaler.fit(y_train)
    xt = x_train.copy()
    xt[:, :k] = sx.transform(x_train[:, :k])
    xn = x_next.copy()[None, :]
    xn[:, :k] = sx.transform(xn[:, :k])
    yt = sy.transform(y_train)
    out = np.zeros(24)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        for h in range(24):
            alpha = aic_alpha(xt, yt[:, h])
            out[h] = Lasso(alpha=alpha, max_iter=2500, tol=1e-4, selection="cyclic").fit(xt, yt[:, h]).predict(xn)[0]
    return sy.inverse(out[None, :])[0], sx.fallbacks + sy.fallbacks


@dataclass
class WindowLog:
    """What one window did over a run: forecasts made, days it could not forecast, dropped rows, fallbacks."""

    window: int
    forecast_days: int = 0
    no_forecast: dict = None
    dropped_rows: int = 0
    scale_fallbacks: int = 0

    def __post_init__(self):
        self.no_forecast = {"missing_features": [], "fit_failed": []}


def forecast(prices: pd.DataFrame, days: Sequence[date], *, window: int, exog: Sequence[pd.DataFrame] = (),
             dummies: dict[date, Sequence[float]] | None = None, n_extra: int = 0
             ) -> tuple[pd.DataFrame, WindowLog]:
    """LEAR with one calibration window, recalibrated daily: a ``[len(days), 24]`` forecast (NaN if unbuildable).

    The window of N for D is the N days D-N..D-1; its first 7 days only supply
    lags, so the training rows are D-N+7..D-1 (a row with any non-finite target
    or feature is dropped; the window is never extended). Nothing of D enters any fit.
    """
    dummies = dummies or {}
    log = WindowLog(window)
    rows = {}
    for d in days:
        train_days = [d - timedelta(days=i) for i in range(window - 7, 0, -1)]
        xs, ys = [], []
        for t in train_days:
            x = features(prices, t, exog=exog, extra_dummies=dummies.get(t, [0.0] * n_extra))
            y = prices.loc[t].to_numpy() if t in prices.index else None
            if x is None or y is None or not np.isfinite(y).all():
                log.dropped_rows += 1
                continue
            xs.append(x)
            ys.append(y)
        x_next = features(prices, d, exog=exog, extra_dummies=dummies.get(d, [0.0] * n_extra))
        if x_next is None:
            rows[d] = np.full(24, np.nan)
            log.no_forecast["missing_features"].append(str(d))
            continue
        try:
            if len(xs) < 2:
                raise ValueError("fewer than 2 training rows")
            f, fallbacks = fit_predict_day(np.vstack(xs), np.vstack(ys), x_next, n_dummies=7 + n_extra)
            if not np.isfinite(f).all():
                raise ValueError("non-finite forecast")
        except Exception:  # a failed fit: the window cannot forecast D (counted)
            rows[d] = np.full(24, np.nan)
            log.no_forecast["fit_failed"].append(str(d))
            continue
        rows[d] = f
        log.forecast_days += 1
        log.scale_fallbacks += fallbacks
    return pd.DataFrame.from_dict(rows, orient="index"), log


def ensemble(forecasts: Sequence[pd.DataFrame]) -> pd.DataFrame:
    """The hour-by-hour mean of all windows' forecasts; a day any window misses is NaN (never fewer windows)."""
    stack = np.stack([f.to_numpy() for f in forecasts])
    return pd.DataFrame(stack.mean(axis=0), index=forecasts[0].index)  # a NaN in any window propagates


def epf_day_matrix(column: pd.Series) -> pd.DataFrame:
    """EPF-FR's own 24 local hours per day (the dataset already has 24 rows per day), indexed by date."""
    s = column.sort_index()
    days = pd.Index(s.index.date)
    out = {}
    for d, grp in s.groupby(days):
        out[d] = grp.to_numpy(dtype="float64") if len(grp) == 24 else np.full(24, np.nan)
    return pd.DataFrame.from_dict(out, orient="index")
