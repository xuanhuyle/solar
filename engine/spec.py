"""Declarative probe specs: validated against the catalogue, canonicalised, hashed.

A spec names catalogue entries only. Any unknown field, unknown value, or a
covariate not allowed for the target is rejected with every reason listed, so
the researcher can repair it. The hash excludes ``rationale`` (free text that
changes nothing the referee runs). Standard library only.
"""

from __future__ import annotations

import re

from engine import catalogue as cat
from engine.canon import sha256_of

PROBE_VERSION = "probe/0"
NAME = re.compile(r"^[a-z][a-z0-9_]*$")
PROBE_FIELDS = {"spec_version", "target", "period", "scope", "arms", "comparisons", "builds_on", "rationale"}
ARM_FIELDS = {"name", "covariates"}
COV_FIELDS = {"id", "transform"}
CMP_FIELDS = {"arm", "vs", "metric"}


class SpecError(ValueError):
    def __init__(self, reasons: list[str]):
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def _unknown(obj: dict, allowed: set, where: str, errors: list[str]) -> None:
    extra = sorted(set(obj) - allowed)
    if extra:
        errors.append(f"{where}: unknown field(s) {extra}")


def validate_probe(spec) -> dict:
    """The normalised spec, or ``SpecError`` listing every problem."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        raise SpecError(["the spec must be a JSON object"])
    _unknown(spec, PROBE_FIELDS, "spec", errors)
    missing = [k for k in ("spec_version", "target", "period", "scope", "arms", "comparisons") if k not in spec]
    if missing:
        raise SpecError(errors + [f"spec: missing {missing}"])
    if spec["spec_version"] != PROBE_VERSION:
        errors.append(f"spec_version must be {PROBE_VERSION!r}")
    target = spec["target"]
    if target not in cat.TARGETS:
        errors.append(f"target {target!r} not in {sorted(cat.TARGETS)}")
    if spec["period"] not in cat.PERIODS:
        errors.append(f"period {spec['period']!r} not in {sorted(cat.PERIODS)}")
    if spec["scope"] not in cat.SCOPES:
        errors.append(f"scope {spec['scope']!r} not in {sorted(cat.SCOPES)}")
    arms = spec["arms"]
    if not isinstance(arms, list) or not 1 <= len(arms) <= cat.LIMITS["arms"]:
        errors.append(f"arms: 1..{cat.LIMITS['arms']} required")
        arms = []
    names: list[str] = []
    norm_arms = []
    for i, arm in enumerate(arms):
        where = f"arms[{i}]"
        if not isinstance(arm, dict):
            errors.append(f"{where}: must be an object")
            continue
        _unknown(arm, ARM_FIELDS, where, errors)
        name = arm.get("name")
        if not isinstance(name, str) or not NAME.match(name) or len(name) > cat.LIMITS["name_chars"]:
            errors.append(f"{where}: name must match {NAME.pattern} (<= {cat.LIMITS['name_chars']} chars)")
        elif name in cat.COMPARATORS or name in names:
            errors.append(f"{where}: name {name!r} is taken")
        names.append(name)
        covs = arm.get("covariates", [])
        if not isinstance(covs, list) or len(covs) > cat.LIMITS["covariates_per_arm"]:
            errors.append(f"{where}: covariates must be a list of <= {cat.LIMITS['covariates_per_arm']}")
            covs = []
        norm_covs, seen = [], set()
        for j, c in enumerate(covs):
            cw = f"{where}.covariates[{j}]"
            if not isinstance(c, dict):
                errors.append(f"{cw}: must be an object")
                continue
            _unknown(c, COV_FIELDS, cw, errors)
            cid, tr = c.get("id"), c.get("transform", "raw")
            entry = cat.COVARIATES.get(cid)
            if entry is None:
                errors.append(f"{cw}: covariate {cid!r} not in {sorted(cat.COVARIATES)}")
                continue
            if target in cat.TARGETS and target not in entry["targets"]:
                errors.append(f"{cw}: {cid} is not available for target {target}")
            if tr not in entry["transforms"]:
                errors.append(f"{cw}: transform {tr!r} not in {entry['transforms']} for {cid}")
            if (cid, tr) in seen:
                errors.append(f"{cw}: duplicate covariate {cid}/{tr}")
            seen.add((cid, tr))
            first = entry["first_day"]
            if first and spec["period"] in cat.PERIODS and cat.PERIODS[spec["period"]][1] < first:
                errors.append(f"{cw}: {cid} covers days from {first} only; period {spec['period']} ends before")
            norm_covs.append({"id": cid, "transform": tr})
        norm_arms.append({"name": name, "covariates": sorted(norm_covs, key=lambda c: (c["id"], c["transform"]))})
    cmps = spec["comparisons"]
    if not isinstance(cmps, list) or not 1 <= len(cmps) <= cat.LIMITS["comparisons"]:
        errors.append(f"comparisons: 1..{cat.LIMITS['comparisons']} required")
        cmps = []
    norm_cmps = []
    for i, c in enumerate(cmps):
        where = f"comparisons[{i}]"
        if not isinstance(c, dict):
            errors.append(f"{where}: must be an object")
            continue
        _unknown(c, CMP_FIELDS, where, errors)
        if c.get("arm") not in names:
            errors.append(f"{where}: arm {c.get('arm')!r} is not one of the spec's arms {names}")
        if c.get("vs") not in set(cat.COMPARATORS) | set(names) or c.get("vs") == c.get("arm"):
            errors.append(f"{where}: vs {c.get('vs')!r} must be a comparator {sorted(cat.COMPARATORS)} or another arm")
        if c.get("vs") == "rte_j1" and target in cat.TARGETS and cat.TARGETS[target]["reference"] != "rte_j1":
            errors.append(f"{where}: rte_j1 exists for consumption only")
        if c.get("metric", "mae") not in cat.METRICS:
            errors.append(f"{where}: metric {c.get('metric')!r} not in {sorted(cat.METRICS)}")
        norm_cmps.append({"arm": c.get("arm"), "vs": c.get("vs"), "metric": c.get("metric", "mae")})
    builds_on = spec.get("builds_on", [])
    if not isinstance(builds_on, list) or not all(isinstance(x, int) and x >= 0 for x in builds_on):
        errors.append("builds_on must be a list of ledger sequence numbers")
        builds_on = []
    rationale = spec.get("rationale", "")
    if not isinstance(rationale, str) or len(rationale) > cat.LIMITS["rationale_chars"]:
        errors.append(f"rationale must be text of <= {cat.LIMITS['rationale_chars']} characters")
        rationale = ""
    if errors:
        raise SpecError(errors)
    return {"spec_version": PROBE_VERSION, "target": target, "period": spec["period"], "scope": spec["scope"],
            "arms": norm_arms, "comparisons": norm_cmps, "builds_on": sorted(set(builds_on)), "rationale": rationale}


def spec_sha256(normalised: dict) -> str:
    """The probe's identity: everything the referee runs, not the rationale."""
    return sha256_of({k: v for k, v in normalised.items() if k not in ("rationale", "builds_on")})
