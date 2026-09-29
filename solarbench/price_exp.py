"""Experiment 4's core: price windows under the frozen publication rule, the price backtest and the arms.

Everything here implements ``solarbench.price_spec.PRICE_SPEC`` as written; nothing
reinterprets it. The key difference from the load and solar experiments is the
publication rule: a day-ahead price is published before its delivery day starts,
so at the decision time ``d`` (12:00 Europe/Paris on D-1) all of D-1 is known and
nothing of D. A ``PriceWindow`` therefore separates

* ``decision`` - the time the forecast is made (covariates are checked against it);
* ``origin`` - the last price stamp the context may read: the cutoff, the hour
  [D-1 23:00, D 00:00) Paris (or, for the strict arm, the 12:00 D-1 stamp itself).

Because ``origin`` is the cutoff, every existing "nothing after the origin" check -
the leakage contract, the poisoning tests - enforces "nothing unpublished" unchanged,
and a separate check makes sure every price read was published by ``decision``.
Nothing is ever clipped: prices can be negative.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Sequence

import numpy as np
import pandas as pd

from engine import zones
from solarbench import covariates as cov
from solarbench import forecasters as fc
from solarbench import price_spec as ps
from solarbench import probes as pr
from solarbench.forecasters import Prediction, Window, _NonFiniteWatcher

log = logging.getLogger(__name__)

HOUR = pd.Timedelta(hours=1)
T0 = ps.PRICE_SPEC["t0"]
LEVELS: tuple[float, ...] = tuple(T0["quantiles"])
CONTEXT_HOURS: int = T0["context_hours"]
HORIZON: int = T0["fixed_horizon_hours"]
STRICT_HORIZON = 36
MIN_VALID: float = T0["min_context_valid"]
DECISION_HOUR = 12


# ------------------------------------------------------------- time and the publication rule


def day_hours(d: date) -> pd.DatetimeIndex:
    """The UTC start stamps of the real hours of Paris day ``d`` (23, 24 or 25)."""
    a = zones.local_midnight_utc(d)
    b = zones.local_midnight_utc(d + timedelta(days=1))
    return pd.date_range(a, b, freq="1h", tz="UTC", inclusive="left")


def decision_time(d: date, hour: int = DECISION_HOUR) -> pd.Timestamp:
    """12:00 Europe/Paris on D-1, in UTC."""
    return pr.gate(d, hour)


def paris_day(stamps) -> np.ndarray:
    """The Paris delivery day of each (start-stamped) UTC hour."""
    return np.asarray(pd.DatetimeIndex(stamps).tz_convert(zones.PARIS).date)


def pub_latest(stamps) -> pd.DatetimeIndex:
    """Latest publication time of each price cell: 00:00 Paris of its delivery day."""
    days = paris_day(stamps)
    return pd.DatetimeIndex([zones.local_midnight_utc(d) for d in days])


def pub_earliest(stamps) -> pd.DatetimeIndex:
    """Earliest publication time of each price cell: 12:00 Paris on the day before its delivery day."""
    return pd.DatetimeIndex([decision_time(d) for d in paris_day(stamps)])


@dataclass(frozen=True)
class PriceWindow(Window):
    """One delivery day of Experiment 4: ``origin`` is the last readable price stamp, ``decision`` is d."""

    decision: pd.Timestamp | None = None
    strict: bool = False

    @property
    def horizon(self) -> int:
        return int((self.targets[-1] - self.origin) / HOUR)

    @property
    def steps(self) -> np.ndarray:
        return np.asarray((self.targets - self.origin) / HOUR, dtype=int)


@dataclass
class WindowReport:
    built: int = 0
    incomplete_target: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"built": self.built, "incomplete_target": len(self.incomplete_target),
                "incomplete_days": [str(d) for d in self.incomplete_target][:100]}


def build_price_windows(series: pd.Series | None, days: Sequence[date], *, strict: bool = False,
                        decision_hour: int = DECISION_HOUR, require_target: bool = True,
                        report: WindowReport | None = None) -> list[PriceWindow]:
    """One window per Paris delivery day: decision 12:00 D-1, origin = cutoff (strict: origin = d).

    With ``require_target`` a day whose target has any missing hour is left out
    (target.missing) and counted; the calendar alone decides every time stamp.
    """
    if decision_hour > DECISION_HOUR:
        raise ValueError(f"decision hour {decision_hour}:00 is later than 12:00 D-1: refused")
    report = report if report is not None else WindowReport()
    out = []
    for d in days:
        targets = day_hours(d)
        decision = decision_time(d, decision_hour)
        origin = decision if strict else targets[0] - HOUR
        if not (targets[0] > origin and pub_latest([origin])[0] <= decision):
            raise AssertionError(f"{d}: the window breaks the publication rule")
        if require_target:
            y = series.reindex(targets) if series is not None else None
            if y is None or y.isna().any():
                report.incomplete_target.append(d)
                continue
        out.append(PriceWindow(delivery_date=d, origin=origin, targets=targets, decision=decision, strict=strict))
    report.built += len(out)
    return out


def days_between(start, end) -> list[date]:
    return list(pd.date_range(start, end, freq="D").date)


# ------------------------------------------------------------------ the leakage contract


def check_price_contract(name: str, w: Window, pred: Prediction, *, oracle: bool = False) -> None:
    """Target sources: never after the origin, and published by the decision time.
    Covariates: issued by the decision time (never checked against the cutoff), unless oracle."""
    decision = getattr(w, "decision", None) or w.origin
    issued = pred.covariate_issued_latest
    if not oracle and issued is not None and pd.notna(issued) and issued > decision:
        raise AssertionError(f"{name} read a covariate issued at {issued} for {w.delivery_date}, after d = {decision}")
    stamps = []
    if pred.source_latest is not None:
        stamps = pred.source_latest[pred.source_latest.notna()]
    elif pd.notna(pred.max_source_time):
        stamps = pd.DatetimeIndex([pred.max_source_time])
    if len(stamps):
        if stamps.max() > w.origin:
            raise AssertionError(f"{name} read {stamps.max()} for {w.delivery_date}, after the origin {w.origin}")
        if isinstance(w, PriceWindow) and pub_latest([stamps.max()])[0] > decision:
            raise AssertionError(f"{name} read a price unpublished at d = {decision} for {w.delivery_date}")
    if len(pred.values) != len(w.targets):
        raise AssertionError(f"{name} returned {len(pred.values)} values for {len(w.targets)} targets")


def _oracle_flags(forecasters, oracle_methods: frozenset[str]) -> dict[str, bool]:
    flags = {f.name: bool(getattr(f, "oracle", False)) for f in forecasters}
    for name, flagged in flags.items():
        if flagged != (name in oracle_methods):
            raise AssertionError(f"{name}: oracle flag and oracle_methods disagree (two-key exemption)")
        if flagged and "oracle" not in name.split("_"):
            raise AssertionError(f"{name}: an oracle arm must carry 'oracle' in its name")
    unknown = sorted(set(oracle_methods) - set(flags))
    if unknown:
        raise AssertionError(f"oracle_methods names methods that are not run: {unknown}")
    return flags


def quantile_column(level: float) -> str:
    return f"q{int(round(level * 100)):02d}"


def run_price_backtest(series: pd.Series, forecasters: Sequence, windows: Sequence[Window], *,
                       oracle_methods: frozenset[str] = frozenset()) -> pd.DataFrame:
    """Every forecaster over every window, one tidy row per (method, target hour).

    Unlike ``solarbench.backtest.run_backtest`` nothing is clipped and no window is
    dropped for all methods: a non-finite forecast stays NaN in its own rows, and each
    comparison later keeps only the days both of its arms scored (statistics.day_sets).
    """
    flags = _oracle_flags(forecasters, oracle_methods)
    frames = []
    y_all = series
    for f in forecasters:
        preds = f.predict(series, windows)
        if len(preds) != len(windows):
            raise AssertionError(f"{f.name} returned {len(preds)} predictions for {len(windows)} windows")
        for w, p in zip(windows, preds):
            check_price_contract(f.name, w, p, oracle=flags[f.name])
        for w, p in zip(windows, preds):
            n = len(w.targets)
            frame = {
                "delivery_date": w.delivery_date, "method": f.name, "target_time": w.targets,
                "local_time": w.targets.tz_convert(zones.PARIS),
                "y": y_all.reindex(w.targets).to_numpy(dtype="float64"),
                "y_hat": np.asarray(p.values, dtype="float64"),
                "source_latest": p.source_latest if p.source_latest is not None else pd.DatetimeIndex(
                    [p.max_source_time] * n),
                "cov_issued_latest": pd.DatetimeIndex([p.covariate_issued_latest] * n)
                if p.covariate_issued_latest is not None else pd.DatetimeIndex([pd.NaT] * n, tz="UTC"),
            }
            for j, level in enumerate(LEVELS):
                col = np.full(n, np.nan)
                if p.quantiles is not None and p.quantile_levels is not None and level in p.quantile_levels:
                    col = np.asarray(p.quantiles[:, p.quantile_levels.index(level)], dtype="float64")
                frame[quantile_column(level)] = col
            frames.append(pd.DataFrame(frame))
    if not frames:
        raise RuntimeError("no windows")
    return pd.concat(frames, ignore_index=True)


# ------------------------------------------------------------------------- simple rules


@dataclass
class NaiveStd:
    """Lago et al.'s standard naive on local wall-clock hours (PRICE_SPEC['naive_std']).

    D-7 for a Monday, Saturday or Sunday delivery day, D-1 otherwise; a local hour
    missing on the lag day (spring) takes the preceding local hour; a repeated local
    hour on the lag day (autumn) takes the mean of its two values; a repeated hour on D
    takes the lag day's value for both. ``strict``: any source stamped after the
    window's origin is replaced by the same local hour of the day before the lag day.
    """

    name: str = "naive_std"
    label: str = "Standard naive (D-7 Mon/Sat/Sun, else D-1; local hours)"
    strict: bool = False

    def spec(self) -> dict:
        return {"class": "NaiveStd", "strict": self.strict}

    @staticmethod
    def _sources(lag_day: date, hour: int) -> list[pd.Timestamp]:
        stamps = day_hours(lag_day)
        local = stamps.tz_convert(zones.PARIS).hour
        picks = [t for t, h in zip(stamps, local) if h == hour]
        if not picks:  # spring: the local hour does not exist on the lag day
            picks = [t for t, h in zip(stamps, local) if h == hour - 1]
        return picks

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        out = []
        for w in windows:
            d = w.delivery_date
            lag = 7 if d.weekday() in (0, 5, 6) else 1
            lag_day = d - timedelta(days=lag)
            values, latest = [], []
            for t in w.targets:
                hour = t.tz_convert(zones.PARIS).hour
                src = self._sources(lag_day, hour)
                if self.strict and any(s > w.origin for s in src):
                    src = self._sources(lag_day - timedelta(days=1), hour)
                v = series.reindex(pd.DatetimeIndex(src)).to_numpy(dtype="float64")
                values.append(float(np.mean(v)) if len(v) and np.isfinite(v).all() else np.nan)
                latest.append(max(src))
            idx = pd.DatetimeIndex(latest)
            out.append(Prediction(values=np.asarray(values), max_source_time=idx.max(), source_latest=idx,
                                  source_earliest=idx, n_sources=np.ones(len(idx), dtype=int)))
        return out


def simple_rules(strict: bool = False) -> dict[str, object]:
    """The eight frozen candidates (PRICE_SPEC['simple_candidates']), by name."""
    rules = {"naive_std": NaiveStd(strict=strict), "prev_day": fc.same_day_baseline(),
             "prev_week": fc.same_week_baseline(), "mean_7d": fc.mean_7d_baseline(),
             "median_7d": fc.median_7d_baseline(), "ewma": fc.ewma_baseline(), "blend_50": fc.blend_50_baseline(),
             "weekday_mean_4w": pr.weekday_mean_4w()}
    assert list(rules) == ps.PRICE_SPEC["simple_candidates"]
    return rules


@dataclass
class Renamed:
    """A forecaster run under another name (best_simple_2023, best_simple_2023_strict)."""

    inner: object
    name: str

    @property
    def label(self) -> str:
        return f"{self.name} ({self.inner.name})"

    def spec(self) -> dict:
        return {"class": "Renamed", "inner": self.inner.name, "inner_spec": self.inner.spec()}

    def predict(self, series, windows):
        return self.inner.predict(series, windows)


# ---------------------------------------------------------------------------------- t0


@dataclass
class PriceT0Forecaster:
    """t0-alpha on the hourly price grid: univariate French price context of 2160 hours ending at the origin,
    known-future covariates over context + horizon, the five native quantiles, nothing clipped.

    PRICE_SPEC['t0']['missing']: a day whose context is under 98% valid, or whose output t0
    sanitised, has no forecast (NaN everywhere); ``missing`` records it by cause.
    """

    name: str
    covariates: tuple = ()
    horizon: int = HORIZON
    context_hours: int = CONTEXT_HOURS
    min_valid: float = MIN_VALID
    repo_id: str = T0["repo_id"]
    revision: str = T0["revision"]
    batch_size: int = 32
    levels: tuple[float, ...] = LEVELS
    _model: object | None = field(default=None, repr=False)
    missing: dict = field(default_factory=lambda: {"context": [], "sanitised": []})

    @property
    def label(self) -> str:
        return f"t0-alpha, {len(self.covariates)} covariates"

    @property
    def oracle(self) -> bool:
        return any(getattr(c, "oracle", False) for c in self.covariates)

    def spec(self) -> dict:
        return {"class": "PriceT0Forecaster", "repo_id": self.repo_id, "revision": self.revision,
                "context_hours": self.context_hours, "horizon": self.horizon, "levels": list(self.levels),
                "min_valid": self.min_valid, "covariates": [c.spec() for c in self.covariates]}

    def load(self):
        if self._model is None:
            from t0 import T0Forecaster as _T0

            self._model = _T0.from_pretrained(self.repo_id, token=True, revision=self.revision).eval()
        return self._model

    def use_model(self, model) -> "PriceT0Forecaster":
        self._model = model
        return self

    def context(self, series: pd.Series, origin: pd.Timestamp) -> tuple[np.ndarray, float]:
        ctx = series.loc[:origin]
        if len(ctx) < self.context_hours or ctx.index[-1] != origin:
            raise ValueError(f"{self.name}: the context must hold {self.context_hours} hours ending at {origin}")
        ctx = ctx.iloc[-self.context_hours:]
        if not ctx.index.equals(pd.date_range(end=origin, periods=self.context_hours, freq="1h")):
            raise ValueError(f"{self.name}: the context is not on the hourly grid ending at {origin}")
        v = ctx.to_numpy(dtype="float32")
        return v, float(np.isfinite(v).mean())

    def block_times(self, origin: pd.Timestamp) -> pd.DatetimeIndex:
        return pd.date_range(origin - (self.context_hours - 1) * HOUR, periods=self.context_hours + self.horizon,
                             freq="1h")

    def block(self, origin: pd.Timestamp) -> tuple[np.ndarray, pd.Timestamp]:
        times = self.block_times(origin)
        arr = np.stack([np.asarray(c.values(times), dtype="float64") for c in self.covariates])
        latest = [i[i.notna()].max() for i in (pd.DatetimeIndex(c.issued_at(times)) for c in self.covariates)
                  if i.notna().any()]
        return arr.astype("float32"), (max(latest) if latest else pd.NaT)

    def _run(self, model, ctx: np.ndarray, fut: np.ndarray | None):
        import torch

        watcher = _NonFiniteWatcher()
        t0_log = logging.getLogger("t0.model.model")
        t0_log.addHandler(watcher)
        try:
            kwargs = {"horizon": self.horizon, "quantiles": list(self.levels)}
            if fut is not None:
                kwargs["future_covariates"] = torch.from_numpy(fut)
            f = model.predict(torch.from_numpy(ctx), **kwargs)
        finally:
            t0_log.removeHandler(watcher)
        return (f.median.detach().cpu().numpy().astype("float64"),
                f.quantiles.detach().cpu().numpy().astype("float64"), watcher.count)

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        model = self.load()
        results: list[Prediction] = []
        for start in range(0, len(windows), self.batch_size):
            batch = list(windows[start:start + self.batch_size])
            for w in batch:
                if w.horizon > self.horizon:
                    raise ValueError(f"{self.name}: {w.delivery_date} needs {w.horizon} steps, horizon is {self.horizon}")
            ctxs, shares = zip(*(self.context(series, w.origin) for w in batch))
            ctx = np.stack(ctxs)
            blocks = [self.block(w.origin) for w in batch] if self.covariates else None
            fut = np.stack([b for b, _ in blocks]) if blocks else None
            median, q, flagged = self._run(model, ctx, fut)
            bad = np.zeros(len(batch), dtype=bool)
            if flagged:
                log.warning("%s: t0 sanitised output in a batch; re-running row by row", self.name)
                for r in range(len(batch)):
                    _, _, f1 = self._run(model, ctx[r:r + 1], fut[r:r + 1] if fut is not None else None)
                    bad[r] = bool(f1)
            for r, w in enumerate(batch):
                n = len(w.targets)
                values = median[r, w.steps - 1]
                quant = q[r, w.steps - 1, :]
                if shares[r] < self.min_valid:
                    self.missing["context"].append(str(w.delivery_date))
                    values, quant = np.full(n, np.nan), np.full((n, len(self.levels)), np.nan)
                elif bad[r]:
                    self.missing["sanitised"].append(str(w.delivery_date))
                    values, quant = np.full(n, np.nan), np.full((n, len(self.levels)), np.nan)
                results.append(Prediction(
                    values=values, max_source_time=w.origin, source_latest=pd.DatetimeIndex([w.origin] * n),
                    source_earliest=pd.DatetimeIndex([w.origin - (self.context_hours - 1) * HOUR] * n),
                    n_sources=np.full(n, self.context_hours, dtype=int),
                    covariate_issued_latest=blocks[r][1] if blocks else None,
                    quantiles=quant, quantile_levels=tuple(self.levels)))
        return results


# ------------------------------------------------------------------------ covariates


def holiday() -> pr.HolidayCovariate:
    return pr.HolidayCovariate()


def weather_covariates(temperature: pd.Series, radiation: pd.Series, grid: pd.DatetimeIndex
                       ) -> tuple[cov.SeriesCovariate, cov.SeriesCovariate]:
    """The P4 weather covariates on the hourly price grid (PRICE_SPEC['weather_p4']).

    Radiation: the reading stamped h + 1 h (mean over [h, h + 1 h)); temperature: interpolated
    at h + 30 min. Issue bound: lead 3 days from the latest reading used (+ 10 h publication).
    """
    from engine import covs

    tv, tl = covs.instant_to_slots(temperature.sort_index(), grid, 30)
    rv, rl = cov.hourly_to_slots(radiation.sort_index(), grid, 30)
    t = cov.SeriesCovariate(name="wx_temperature", series=pd.Series(tv, index=grid),
                            issued=pd.Series(cov.issue_bound(tl, 3), index=grid),
                            description={"convention": "instant", "lead_days": 3, "port": "centre h+30min"})
    r = cov.SeriesCovariate(name="wx_radiation", series=pd.Series(rv, index=grid),
                            issued=pd.Series(cov.issue_bound(rl, 3), index=grid),
                            description={"convention": "mean_preceding_hour", "lead_days": 3,
                                         "port": "reading stamped h+1h"})
    return t, r


# ----------------------------------------------------------------- empirical bands


@dataclass
class PriceEmpiricalQuantiles:
    """best_simple_eq (PRICE_SPEC['empirical_bands']): the base's scored forecast plus the empirical quantiles
    of its own past errors at the same UTC hour. Past forecasts are the base's own forecasts from each past
    day's price window; each cell is legal on its own when its Paris day is <= D-1 and its error is finite."""

    base: object
    name: str = "best_simple_eq"
    levels: tuple[float, ...] = LEVELS
    window: int = pr.EQ_WINDOW_DAYS
    min_n: int = pr.EQ_MIN_N
    lookback: int = pr.EQ_LOOKBACK_DAYS

    @property
    def label(self) -> str:
        return f"{self.base.name} + empirical error quantiles"

    def spec(self) -> dict:
        return {"class": "PriceEmpiricalQuantiles", "base": self.base.spec(), "levels": list(self.levels),
                "window": self.window, "min_n": self.min_n, "lookback": self.lookback}

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        base_scored = self.base.predict(series, windows)
        need = sorted({w.delivery_date - timedelta(days=k) for w in windows for k in range(1, self.lookback + 2)})
        hist_windows = build_price_windows(None, need, require_target=False)
        hist_preds = self.base.predict(series, hist_windows)
        f_hist = pd.concat([pd.Series(p.values, index=hw.targets) for hw, p in zip(hist_windows, hist_preds)])
        f_hist = f_hist[~f_hist.index.duplicated(keep="first")]
        out = []
        for w, p in zip(windows, base_scored):
            d = w.delivery_date
            n = len(w.targets)
            q = np.full((n, len(self.levels)), np.nan)
            latest = list(p.source_latest) if p.source_latest is not None else [p.max_source_time] * n
            for i, t in enumerate(w.targets):
                cells = pd.DatetimeIndex([t - pd.Timedelta(days=j) for j in range(1, self.lookback + 1)])
                legal_day = paris_day(cells) <= d - timedelta(days=1)
                err = series.reindex(cells).to_numpy(dtype="float64") - f_hist.reindex(cells).to_numpy(dtype="float64")
                ok = legal_day & np.isfinite(err)
                picks = np.flatnonzero(ok)[: self.window]
                if len(picks) >= self.min_n and np.isfinite(p.values[i]):
                    q[i] = p.values[i] + np.quantile(err[picks], self.levels)
                    latest[i] = max(latest[i], cells[picks[0]]) if pd.notna(latest[i]) else cells[picks[0]]
            idx = pd.DatetimeIndex(latest)
            out.append(Prediction(values=np.asarray(p.values, dtype="float64"), max_source_time=idx.max(),
                                  source_latest=idx, source_earliest=p.source_earliest, n_sources=p.n_sources,
                                  quantiles=q, quantile_levels=tuple(self.levels)))
        return out


# ------------------------------------------------------------------------------ LEAR


def _lear_window(n: int, prices: pd.DataFrame, days: list[date], hol: dict):
    """One LEAR window over ``days`` (features_exp4), BLAS held to one thread so a window gives the same bits
    in a worker process and in-process (as price_gates' K1 windows)."""
    from threadpoolctl import threadpool_limits

    from solarbench import lear

    with threadpool_limits(limits=1):
        return lear.forecast(prices, days, window=n, dummies=hol, n_extra=1)


@dataclass
class LearEnsemble:
    """lear_ens (PRICE_SPEC['lear']): the clean-room LEAR's four calibration windows, averaged hour by hour.

    Each delivery day D is forecast from days D-N..D-1 only (all published by d);
    the forecast is placed on D's real UTC hours. ``processes`` > 1 runs the four windows in spawned
    worker processes when there are at least ``parallel_min_days`` days (same bits, less wall time).
    """

    name: str = "lear_ens"
    windows: tuple[int, ...] = tuple(ps.PRICE_SPEC["lear"]["calibration_windows_days"])
    logs: dict = field(default_factory=dict)
    processes: int = 1
    parallel_min_days: int = 30

    @property
    def label(self) -> str:
        return "LEAR ensemble (56/84/1092/1456 days), clean-room"

    def spec(self) -> dict:
        return {"class": "LearEnsemble", "windows": list(self.windows), "features": "exp4"}

    def forecast_days(self, series: pd.Series, days: Sequence[date]) -> pd.DataFrame:
        from solarbench import lear

        first = min(days) - timedelta(days=max(self.windows) + 7)
        all_days = days_between(first, max(days))
        prices = lear.day_matrix(series, all_days)
        hol = {d: [1.0 if d in pr.french_holidays(d.year) else 0.0] for d in all_days}
        args = [(n, prices, list(days), hol) for n in self.windows]
        if self.processes > 1 and len(days) >= self.parallel_min_days:
            import multiprocessing as mp
            from concurrent.futures import ProcessPoolExecutor

            with ProcessPoolExecutor(max_workers=min(self.processes, len(args)),
                                     mp_context=mp.get_context("spawn")) as ex:
                results = [f.result() for f in [ex.submit(_lear_window, *a) for a in args]]
        else:
            results = [_lear_window(*a) for a in args]
        parts = []
        for n, (f, lg) in zip(self.windows, results):
            parts.append(f)
            self.logs[n] = lg
        return lear.ensemble(parts)

    def predict(self, series: pd.Series, windows: Sequence[Window]) -> list[Prediction]:
        from solarbench import lear

        ens = self.forecast_days(series, [w.delivery_date for w in windows])
        out = []
        for w in windows:
            row = ens.loc[w.delivery_date].to_numpy(dtype="float64")
            values = lear.to_utc_hours(w.delivery_date, row).reindex(w.targets).to_numpy(dtype="float64")
            last = day_hours(w.delivery_date - timedelta(days=1))[-1]  # D-1's last hour: the latest price used
            out.append(Prediction(values=values, max_source_time=last,
                                  source_latest=pd.DatetimeIndex([last] * len(w.targets))))
        return out
