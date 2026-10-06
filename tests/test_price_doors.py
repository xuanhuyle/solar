"""Static check for Experiment 4: price data is reached only through its door (``solarbench/price_data.py``).

Only the door and the runner import it, and no other module names a price
host. (``tests/test_engine_doors.py`` still guards the ODRÉ and Open-Meteo
downloaders, which the runner reaches only through ``engine``.)
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOOR = "solarbench/price_data.py"
ALLOWED_IMPORTERS = {DOOR, "run_prices.py"}
HOSTS = ("energy-charts.info", "smard.de")


def _sources():
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("tests/", ".git/")) or "/." in rel:
            continue
        yield rel, ast.parse(path.read_text(encoding="utf-8"), filename=rel)


def _imports_price_data(tree) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name == "solarbench.price_data" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom):
            if node.module == "solarbench.price_data":
                return True
            if node.module == "solarbench" and any(a.name == "price_data" for a in node.names):
                return True
    return False


def test_only_the_runner_imports_the_price_door():
    bad = [rel for rel, tree in _sources() if rel not in ALLOWED_IMPORTERS and _imports_price_data(tree)]
    assert not bad, bad


def test_no_other_module_names_a_price_host():
    bad = []
    for rel, tree in _sources():
        if rel in (DOOR, "solarbench/price_spec.py"):  # the spec names its source; it fetches nothing
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(h in node.value for h in HOSTS):
                bad.append(f"{rel}: {node.value[:60]}")
    assert not bad, bad


def test_the_door_check_sees_both_import_forms():
    for code in ("import solarbench.price_data", "from solarbench import price_data as x",
                 "from solarbench.price_data import fetch_energy_charts"):
        assert _imports_price_data(ast.parse(code)), code
