"""Static check: raw downloaders are called only behind a guard.

``odre._download_columns`` has no seal check, and ``weather.fetch_json`` has none
either; each may be called only from its home module and from ``engine/data.py``.
Engine modules may not reach the network any other way.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = {"_download_columns": {"solarbench/odre.py", "engine/data.py"},
       "fetch_json": {"solarbench/weather.py", "engine/data.py"}}
#: Guarded or unguarded fetchers the engine must not call directly (it uses ``engine.data``).
ENGINE_FORBIDDEN = {"fetch_columns", "fetch_eco2mix", "load_or_fetch", "fetch_previous_runs", "fetch_era5",
                    "fetch_single_run", "fetch_region_weights_2023"}


def _sources():
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("tests/", ".git/")) or "/." in rel:
            continue
        yield rel, ast.parse(path.read_text(encoding="utf-8"), filename=rel)


def _called_names(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute):
                yield f.attr, ast.unparse(f)
            elif isinstance(f, ast.Name):
                yield f.id, f.id


def test_raw_downloaders_have_only_guarded_callers():
    bad = []
    for rel, tree in _sources():
        for name, text in _called_names(tree):
            if name in RAW and rel not in RAW[name]:
                bad.append(f"{rel}: {text}()")
    assert not bad, bad


def test_engine_reaches_the_network_only_through_its_door():
    bad = []
    for rel, tree in _sources():
        # engine/data.py is the data door; engine/approvals.py only reads the run's approval record
        # from api.github.com (no data source), which the vault needs.
        if not rel.startswith("engine/") or rel in ("engine/data.py", "engine/approvals.py"):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                if any(m.split(".")[0] in {"requests", "urllib", "httpx", "http", "socket"} for m in mods):
                    bad.append(f"{rel}: imports {mods}")
        for name, text in _called_names(tree):
            if name in ENGINE_FORBIDDEN:
                bad.append(f"{rel}: {text}()")
    assert not bad, bad
