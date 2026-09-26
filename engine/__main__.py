"""Command line for the knowledge engine: ``python -m engine <mode>``.

Modes built so far (milestone M0):

* ``selftest`` - no network: zones, fingerprints, the data door's refusals.
* ``avail`` - data coverage only, never forecast skill: national consumption
  2021-10 .. 2025-12 by month and vintage; Open-Meteo archived temperature
  forecasts by model and year at one point; 2023 regional consumption weights.
"""

from __future__ import annotations

import argparse
import json
import logging
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from engine import canon, data, zones

log = logging.getLogger("engine")
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "engine"
CACHE = ROOT / "enginecache"


def _write(name: str, obj) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / name
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return path


def selftest(args) -> dict:
    checks: dict[str, bool] = {}
    checks["forward boundary is Paris midnight"] = str(zones.local_midnight_utc(zones.FORWARD_FROM)) == "2025-12-31 23:00:00+00:00"
    checks["request bounds round inward"] = zones.utc_request_days("2022-01-01", "2025-12-31")[1] == "2025-12-31"
    try:
        data.fetch_odre(data.NATIONAL, ["date_heure"], "2025-12-01", "2026-01-15", CACHE)
        checks["forward read refused"] = False
    except zones.ZoneError:
        checks["forward read refused"] = True
    checks["2025 is not confirmable"] = not zones.confirmable("2025-06-01")
    checks["2026 is confirmable"] = zones.confirmable("2026-06-01")
    checks["canonical hash is stable"] = canon.sha256_of({"b": 1, "a": [1, 2]}) == canon.sha256_of({"a": [1, 2], "b": 1})
    out = {"mode": "selftest", "python": platform.python_version(), "checks": checks, "ok": all(checks.values())}
    return out


def _month_coverage(series: pd.Series, start: str, end: str) -> dict[str, float]:
    grid = pd.date_range(zones.local_midnight_utc(start), zones.local_midnight_utc(pd.Timestamp(end) + pd.Timedelta(days=1)),
                         freq="30min", inclusive="left")
    ok = series.reindex(grid).notna()
    local = grid.tz_convert(zones.PARIS)
    return {str(k): round(float(v), 4) for k, v in ok.groupby(local.strftime("%Y-%m")).mean().items()}


def avail(args) -> dict:
    out: dict = {"mode": "avail", "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    # 1. National consumption, discovery zone plus the context lead-in.
    try:
        cons = data.load_odre(data.NATIONAL, "consommation", "2021-10-01", "2025-12-31", CACHE)
        out["consumption"] = {"first": str(cons.first_valid_index()), "last": str(cons.last_valid_index()),
                              "by_month": _month_coverage(cons, "2021-10-01", "2025-12-31")}
    except Exception as exc:  # report, do not hide
        out["consumption"] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
    # 2. Archived temperature forecasts at Paris, per model and year (coverage only).
    from solarbench.weather import WX_MODEL_PREFERENCE

    paris = {"Île-de-France": (48.857, 2.352)}
    variables = [f"temperature_2m_previous_day{n}" for n in (1, 2, 3)]
    wx: dict = {}
    for model in WX_MODEL_PREFERENCE:
        wx[model] = {}
        for year in (2022, 2023, 2024, 2025):
            start, end = f"{year}-01-01", f"{year}-12-31"
            try:
                frames = data.fetch_weather_previous_runs(model, variables, start, end, CACHE, points=paris)
                wx[model][year] = {v: {"valid_share": round(float(f.iloc[:, 0].notna().mean()), 4),
                                       "first_valid": str(f.iloc[:, 0].first_valid_index())}
                                   for v, f in frames.items()}
            except Exception as exc:
                wx[model][year] = {"error": f"{type(exc).__name__}: {exc}"[:300]}
    out["temperature_previous_runs"] = wx
    # 3. 2023 regional consumption shares (weights for a national temperature).
    try:
        weights, meta = data.consumption_region_weights_2023(CACHE)
        out["consumption_region_weights_2023"] = {k: round(v, 6) for k, v in weights.items()}
    except Exception as exc:
        out["consumption_region_weights_2023"] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
    return out


MODES = {"selftest": selftest, "avail": avail}


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser(prog="python -m engine", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=sorted(MODES))
    args = p.parse_args(argv)
    out = MODES[args.mode](args)
    path = _write(f"{args.mode}.json", out)
    print(path.read_text(encoding="utf-8"))
    return 0 if out.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
