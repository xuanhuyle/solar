"""Data bundles and the methods a probe runs, built from the bundle alone.

``load_bundle`` reads, through ``engine.data`` only, everything a probe on one
target needs: the target series, RTE's own forecast (consumption) and the
archived weather forecasts its covariates use. ``build_method`` turns a
catalogue arm or comparator into forecasters that read nothing else - so the
referee can poison a bundle and rebuild them.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path

import pandas as pd

from engine import catalogue as cat
from engine import covs, data, zones
from solarbench import covariates as cov
from solarbench.data import STEPS_PER_DAY
from solarbench.forecasters import T0Forecaster, night_zero_variant, statistical_baselines
from solarbench.probes import ReferenceForecast

CONTEXT_DAYS = cat.T0["context_days"]
LEAD_IN_DAYS = CONTEXT_DAYS + 10  # the context of the first scored day, plus the baselines' lookback


@dataclass
class DataBundle:
    target_id: str
    target: pd.Series
    reference: pd.Series | None = None
    weather: dict[str, pd.Series] = field(default_factory=dict)
    meta: dict = field(default_factory=dict)

    def replaced(self, **changes) -> "DataBundle":
        return replace(self, **changes)


def weather_needs(spec: dict) -> set[str]:
    needs = set()
    for arm in spec["arms"]:
        for c in arm["covariates"]:
            if c["id"] == "wx_temperature":
                needs.add("temperature")
            if c["id"] == "wx_radiation":
                needs.add("radiation")
    return needs


def _national_weather(variable: str, model: str, lead: int, weights: dict[str, float], start, end,
                      cache_dir: Path) -> pd.Series:
    """Weighted national hourly series, fetched a calendar year at a time (each year cached)."""
    parts = []
    first, last = pd.Timestamp(start).date(), pd.Timestamp(end).date()
    for year in range(first.year, last.year + 1):
        a = max(first, pd.Timestamp(f"{year}-01-01").date())
        b = min(last, pd.Timestamp(f"{year}-12-31").date())
        var = f"{variable}_previous_day{lead}"
        frame = data.fetch_weather_previous_runs(model, [var], a, b, cache_dir, points=cov.REGION_POINTS)[var]
        parts.append(cov.national_mean(frame, weights))
    out = pd.concat(parts).sort_index()
    return out[~out.index.duplicated(keep="first")]


def load_bundle(target_id: str, start, end, cache_dir: Path, *, weather: set[str] = frozenset(),
                with_reference: bool = True) -> DataBundle:
    """Everything a probe on ``target_id`` needs for scored days ``start .. end`` (local, inclusive)."""
    zones.assert_discovery(start, end)
    t = cat.TARGETS[target_id]
    read_start = (pd.Timestamp(start) - pd.Timedelta(days=LEAD_IN_DAYS)).date()
    series = data.load_odre(t["dataset"], t["column"], read_start, end, cache_dir)
    reference = None
    if with_reference and t["reference"] == "rte_j1":
        try:
            reference = data.load_odre(t["dataset"], "prevision_j1", read_start, end, cache_dir, extra=())
        except Exception:
            reference = None  # a reference only: its absence changes no verdict
    wx: dict[str, pd.Series] = {}
    if "temperature" in weather:
        if covs.TEMPERATURE_MODEL is None or covs.CONSUMPTION_WEIGHTS is None:
            raise RuntimeError("wx_temperature is not frozen yet (engine.covs): run the avail mode first")
        wx["temperature"] = _national_weather(covs.TEMPERATURE_VARIABLE, covs.TEMPERATURE_MODEL,
                                              covs.TEMPERATURE_LEAD_DAYS, covs.CONSUMPTION_WEIGHTS,
                                              max(read_start, pd.Timestamp(covs.TEMPERATURE_FIRST).date()), end, cache_dir)
    if "radiation" in weather:
        wx["radiation"] = _national_weather(covs.RADIATION_VARIABLE, covs.RADIATION_MODEL, covs.RADIATION_LEAD_DAYS,
                                            cov.REGION_WEIGHTS, max(read_start, pd.Timestamp("2024-03-08").date()),
                                            end, cache_dir)
    meta = {"target": target_id, "dataset": t["dataset"], "column": t["column"], "read": [str(read_start), str(end)],
            "first": str(series.first_valid_index()), "last": str(series.last_valid_index())}
    return DataBundle(target_id, series, reference, wx, meta)


@dataclass
class Method:
    """What the backtest runs for one arm or comparator, and the name it is scored under."""

    name: str
    forecasters: list
    scored: str
    providers: tuple = ()

    def spec(self) -> dict:
        return {f.name: f.spec() for f in self.forecasters}


def _t0(name: str, providers: tuple, model) -> T0Forecaster:
    return T0Forecaster(context_steps=CONTEXT_DAYS * STEPS_PER_DAY, repo_id=cat.T0["repo_id"],
                        revision=cat.T0["revision"], batch_size=64, name=name, label=name,
                        fixed_horizon=cov.COV_HORIZON if providers else None, covariates=providers, _model=model)


def _t0_method(name: str, covariates: list[dict], bundle: DataBundle, model) -> Method:
    providers = tuple(covs.build_covariate(c["id"], c["transform"], bundle) for c in covariates)
    t0 = _t0(name, providers, model)
    if cat.TARGETS[bundle.target_id]["night_zero"]:
        nz = night_zero_variant(name)
        return Method(name, [t0, nz], nz.name, providers)
    return Method(name, [t0], name, providers)


def build_method(name: str, spec: dict, bundle: DataBundle, model, accepted: dict | None) -> Method:
    """An arm of the spec, or one of the catalogue's comparators."""
    for arm in spec["arms"]:
        if arm["name"] == name:
            return _t0_method(name, arm["covariates"], bundle, model)
    if name == "t0_base":
        return _t0_method("t0_base", [], bundle, model)
    if name == "best_simple":
        rule = cat.TARGETS[bundle.target_id]["best_simple"]
        base = next(m for m in statistical_baselines() if m.name == rule)
        return Method("best_simple", [base], rule)
    if name == "accepted":
        if not accepted:
            raise ValueError(f"no accepted finding for target {bundle.target_id}")
        return _t0_method("accepted", accepted["arm"]["covariates"], bundle, model)
    if name == "rte_j1":
        if bundle.reference is None:
            raise ValueError("RTE's own forecast is not available")
        return Method("rte_j1", [ReferenceForecast(bundle.reference, name="rte_j1", label="RTE D-1 forecast")], "rte_j1")
    raise KeyError(name)


def latest_accepted(entries: list[dict], target_id: str) -> dict | None:
    """The newest accepted finding for a target, from the ledger (or the legacy seed if there is none)."""
    found = [e["payload"] for e in entries if e.get("kind") == "accepted_finding" and e["payload"].get("target") == target_id]
    if found:
        return found[-1]
    if target_id == "consumption":
        from engine.legacy import c1_entry

        return c1_entry()[1]
    return None
