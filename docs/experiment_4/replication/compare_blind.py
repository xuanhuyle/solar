#!/usr/bin/env python3
"""Experiment 4 replication, Track 1: compare the blind re-implementation with the published results.

Applies ``TOLERANCES.md`` (committed before any comparison) exactly. Three classes per compared field:

- ``exact``: a deterministic quantity within a relative difference of 1e-9 (absolute 1e-12 when the published
  value is 0); an integer, a state, a candidacy or a delta that is equal; a rounded published value that equals the
  blind value rounded to the published precision; or a bootstrap quantity whose blind seed-0 value is bit-identical.
- ``within_mc``: a bootstrap quantity (interval endpoint or one-sided p) that is not bit-identical at seed 0 but
  whose published value lies inside the 0.5-99.5% range of the same statistic across the blind seeds 0..199
  (``numpy.percentile(spread, [0.5, 99.5])``, default linear method, inclusive, as in ``mc_tolerance.py``). For p
  the comparison uses the draw count k = p * 2001 - 1.
- ``discrepancy``: anything else.

Holm is recomputed from the published raw p and must be equal. States must equal the blind states and follow the
spec's verdict rules applied to the published numbers. M, block_sd and ref_mae are rounded in ``results.json``
(M to 4 decimals, block_sd and ref_mae to 3), so they are compared at the published precision; M is "conditional on
the code's formula" (given to the replicator as a written statement).

Every published leaf is accounted for: compared (one of the three classes), a label used only to check the mapping,
or not compared (with the reason). Every blind leaf is mapped to the published path(s) it was compared with, or
given the reason it has no published counterpart. The blind outputs and the blind script are read, never changed.

Usage::

    python docs/experiment_4/replication/compare_blind.py [--blind <dir containing blind_outputs.json>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PUBLISHED = HERE.parent / "scored_run" / "results.json"
DEFAULT_BLIND = HERE / "blind"
OUT = HERE / "compare_blind.json"

REL_TOL = 1e-9
ABS_TOL_AT_ZERO = 1e-12
MC_RANGE = (0.5, 99.5)
N_DRAWS = 2000
ALPHA = 0.05
PIDS_RUN = ("P1", "P3", "P4")
YEARS = ("2024", "2025")
LABEL_KEYS = {"attribution", "arm", "ref", "metric", "model", "reference", "status", "runnable", "cause",
              "block_days"}
SLICE_GROUPS = {"each year": "year", "each quarter (2025 Q4 is quarter-hour derived)": "quarter"}
LEAR_NOT_RUN = ("published 'not run' placeholder: lear_ens was not scored (K1 failed), so the run computed "
                "nothing here; the blind computes nothing for P2/lear_ens either (its assumption 9), so there is "
                "no value to compare")

# --------------------------------------------------------------------------------------------------------------
# Paths (RFC 6901 JSON pointers: '~' -> '~0', '/' -> '~1'), leaf walking
# --------------------------------------------------------------------------------------------------------------


def ptr(keys) -> str:
    return "/" + "/".join(str(k).replace("~", "~0").replace("/", "~1") for k in keys)


def get(obj, keys):
    for k in keys:
        obj = obj[k]
    return obj


def has(obj, keys) -> bool:
    try:
        get(obj, keys)
        return True
    except (KeyError, IndexError, TypeError):
        return False


def leaves(obj, keys=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, keys + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, keys + (i,))
    else:
        yield keys, obj


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def num(x):
    """JSON-safe number (keeps ints, turns numpy scalars into Python)."""
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    return x


# --------------------------------------------------------------------------------------------------------------
# The comparison ledger
# --------------------------------------------------------------------------------------------------------------


class Ledger:
    def __init__(self, pub: dict, blind: dict):
        self.pub, self.blind = pub, blind
        self.fields: dict[str, dict] = {}
        self.labels: dict[str, dict] = {}
        self.not_compared: dict[str, dict] = {}
        self.blind_used: dict[str, set] = {}

    # bookkeeping ------------------------------------------------------------------------------------------
    def _use(self, bkeys, pkeys):
        if bkeys is None:
            return
        self.blind_used.setdefault(ptr(bkeys), set()).add(ptr(pkeys))

    def _add(self, pkeys, rec):
        p = ptr(pkeys)
        assert p not in self.fields and p not in self.labels and p not in self.not_compared, p
        rec = {"published_path": p, **rec}
        self.fields[p] = rec
        return rec

    # deterministic -----------------------------------------------------------------------------------------
    def det(self, pkeys, bkeys, note=""):
        pub, bl = get(self.pub, pkeys), get(self.blind, bkeys)
        self._use(bkeys, pkeys)
        rec = {"blind_path": ptr(bkeys), "kind": "deterministic", "published": pub, "blind": bl}
        if isinstance(pub, bool) or isinstance(bl, bool) or (isinstance(pub, int) and isinstance(bl, int)):
            ok = (pub == bl) and type(pub) is type(bl)
            rec.update(rule="deterministic integer/boolean: equal", bit_exact=ok)
        else:
            pub_f, bl_f = float(pub), float(bl)
            diff = abs(bl_f - pub_f)
            rec["bit_exact"] = (pub_f == bl_f) and math.copysign(1.0, pub_f) == math.copysign(1.0, bl_f)
            rec["abs_diff"] = diff
            if pub_f == 0.0:
                ok = diff <= ABS_TOL_AT_ZERO
                rec["rule"] = "deterministic: |blind - published| <= 1e-12 (published value is 0)"
            else:
                rel = diff / abs(pub_f)
                rec["rel_diff"] = rel
                ok = rel <= REL_TOL
                rec["rule"] = "deterministic: |blind - published| / |published| <= 1e-9"
        rec["class"] = "exact" if ok else "discrepancy"
        if note:
            rec["note"] = note
        return self._add(pkeys, rec)

    def rounded(self, pkeys, bkeys_unrounded, decimals, note="", bkeys_rounded=None):
        """Published value printed rounded: compare at the published precision."""
        pub = get(self.pub, pkeys)
        if bkeys_unrounded is not None:
            raw = float(get(self.blind, bkeys_unrounded))
            self._use(bkeys_unrounded, pkeys)
            at_prec = round(raw, decimals)
            src = ptr(bkeys_unrounded)
        else:
            raw = None
            at_prec = float(get(self.blind, bkeys_rounded))
            src = ptr(bkeys_rounded)
        if bkeys_rounded is not None:
            self._use(bkeys_rounded, pkeys)
        ok = (at_prec == pub)
        rec = {"blind_path": src, "kind": "rounded", "published": pub, "blind": raw if raw is not None else at_prec,
               "blind_at_published_precision": at_prec,
               "rule": f"published value is printed rounded to {decimals} decimals: round(blind, {decimals}) == "
                       f"published",
               "class": "exact" if ok else "discrepancy"}
        if bkeys_rounded is not None and bkeys_unrounded is not None:
            rec["blind_rounded_field"] = {"path": ptr(bkeys_rounded), "value": get(self.blind, bkeys_rounded)}
        if raw is not None:
            rec["abs_diff_to_unrounded"] = abs(raw - pub)
        rec["note"] = ("compared at the published precision because results.json rounds this field"
                       + ("; " + note if note else ""))
        return self._add(pkeys, rec)

    def cat(self, pkeys, blind_value, bsrc, note="", extra_ok=True, extra=None):
        """Categorical / exact-equality result (state, candidacy, delta, Holm p)."""
        pub = get(self.pub, pkeys)
        if isinstance(bsrc, tuple):
            self._use(bsrc, pkeys)
            bsrc = ptr(bsrc)
        ok = (pub == blind_value) and (pub is None) == (blind_value is None) and extra_ok
        rec = {"blind_path": bsrc, "kind": "categorical", "published": pub, "blind": blind_value,
               "rule": "must be equal", "class": "exact" if ok else "discrepancy"}
        if extra:
            rec.update(extra)
        if note:
            rec["note"] = note
        return self._add(pkeys, rec)

    # bootstrap -----------------------------------------------------------------------------------------------
    def endpoint(self, pkeys, bkeys_seed0, bkeys_spread, note=""):
        pub = float(get(self.pub, pkeys))
        s0 = float(get(self.blind, bkeys_seed0))
        self._use(bkeys_seed0, pkeys)
        rec = {"blind_path": ptr(bkeys_seed0), "kind": "bootstrap_endpoint", "published": pub, "blind_seed0": s0,
               "seed0_bit_exact": pub == s0, "seed0_abs_diff": abs(s0 - pub),
               "seed0_rel_diff": abs(s0 - pub) / abs(pub) if pub != 0 else None}
        if bkeys_spread is not None:
            self._use(bkeys_spread, pkeys)
            spread = np.asarray(get(self.blind, bkeys_spread), dtype="float64")
            assert len(spread) == 200
            lo, hi = np.percentile(spread, MC_RANGE)
            inside = bool(lo <= pub <= hi)
            rec.update(spread_path=ptr(bkeys_spread), spread_seed0_matches_blind=bool(spread[0] == s0),
                       spread_min=float(spread.min()), spread_p0_5=float(lo), spread_p99_5=float(hi),
                       spread_max=float(spread.max()), published_rank_share=float(np.mean(spread <= pub)),
                       inside_mc_range=inside)
            if rec["seed0_bit_exact"]:
                rec["class"], rec["rule"] = "exact", ("bootstrap: blind seed-0 value bit-identical to published "
                                                      "(the 0.5-99.5% seed-range test is also recorded)")
            else:
                rec["class"] = "within_mc" if inside else "discrepancy"
                rec["rule"] = ("bootstrap: published value inside the 0.5-99.5% range of the blind seeds 0..199 "
                               "(numpy.percentile linear, inclusive)")
        else:
            if rec["seed0_bit_exact"]:
                rec["class"], rec["rule"] = "exact", "bootstrap: blind seed-0 value bit-identical to published"
            else:
                return None  # caller records it as not compared
        if note:
            rec["note"] = note
        return self._add(pkeys, rec)

    def pval(self, pkeys, bkeys_seed0_p, bkeys_k_spread, bkeys_seed0_k=None, note=""):
        pub = float(get(self.pub, pkeys))
        s0 = float(get(self.blind, bkeys_seed0_p))
        self._use(bkeys_seed0_p, pkeys)
        if bkeys_seed0_k is not None:
            self._use(bkeys_seed0_k, pkeys)
        k_pub = pub * (N_DRAWS + 1) - 1
        k_pub_int = int(round(k_pub))
        spread = np.asarray(get(self.blind, bkeys_k_spread), dtype="float64")
        self._use(bkeys_k_spread, pkeys)
        assert len(spread) == 200
        lo, hi = np.percentile(spread, MC_RANGE)
        inside = bool(lo <= k_pub <= hi)
        rec = {"blind_path": ptr(bkeys_seed0_p), "kind": "bootstrap_p", "published": pub, "blind_seed0": s0,
               "seed0_bit_exact": pub == s0, "published_k": k_pub, "published_k_is_integer":
                   abs(k_pub - k_pub_int) < 1e-6, "blind_seed0_k": int(round(s0 * (N_DRAWS + 1) - 1)),
               "spread_path": ptr(bkeys_k_spread), "spread_k_min": float(spread.min()),
               "spread_k_p0_5": float(lo), "spread_k_p99_5": float(hi), "spread_k_max": float(spread.max()),
               "spread_seed0_matches_blind": bool(int(spread[0]) == int(round(s0 * (N_DRAWS + 1) - 1))),
               "published_rank_share": float(np.mean(spread <= k_pub)), "inside_mc_range": inside}
        if rec["seed0_bit_exact"]:
            rec["class"], rec["rule"] = "exact", ("bootstrap p: blind seed-0 p bit-identical to published (the "
                                                  "k-range test is also recorded)")
        else:
            rec["class"] = "within_mc" if inside else "discrepancy"
            rec["rule"] = ("bootstrap p: published k = p*2001 - 1 inside the 0.5-99.5% range of the blind k over "
                           "seeds 0..199 (numpy.percentile linear, inclusive)")
        if note:
            rec["note"] = note
        return self._add(pkeys, rec)

    # labels and gaps -----------------------------------------------------------------------------------------
    def label(self, pkeys, blind_value=None, bsrc=None, note=""):
        p = ptr(pkeys)
        assert p not in self.fields and p not in self.labels and p not in self.not_compared, p
        pub = get(self.pub, pkeys)
        rec = {"published_path": p, "published": pub}
        if bsrc is not None:
            if isinstance(bsrc, tuple):
                self._use(bsrc, pkeys)
                bsrc = ptr(bsrc)
            rec.update(blind_source=bsrc, blind=blind_value, consistent=(pub == blind_value))
        else:
            rec["consistent"] = None
        if note:
            rec["note"] = note
        self.labels[p] = rec

    def skip(self, pkeys, reason):
        p = ptr(pkeys)
        assert p not in self.fields and p not in self.labels and p not in self.not_compared, p
        self.not_compared[p] = {"published_path": p, "published": get(self.pub, pkeys), "reason": reason}


# --------------------------------------------------------------------------------------------------------------
# Spec rules applied to the published numbers (verdict states, Holm)
# --------------------------------------------------------------------------------------------------------------


def holm(pvalues):
    """Holm step-down adjusted p in input order, capped at 1 (ties broken by input order)."""
    p = list(map(float, pvalues))
    m = len(p)
    order = sorted(range(m), key=lambda i: (p[i], i))
    adj, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def spec_state(pid, pub):
    """statistics.verdict_states applied to the published numbers (the first state that applies)."""
    prim, ver = pub["primaries"][pid], pub["verdicts"][pid]
    if pid == "P2" and not prim["runnable"]:
        return "not runnable"
    if pid == "P4" and (not prim["runnable"] or prim["days"] in (0, "no days", "not run")):
        return "not runnable"
    thr = float(ver["threshold"])
    if not (prim["skill"] > thr) or not (ver["p_holm"] < ALPHA):
        return "lost"
    if any((not isinstance(prim["yearly"][y], float)) or not (prim["yearly"][y] > thr) for y in YEARS):
        return "not stable"
    if pid == "P3" and not (0.70 <= prim["coverage"] <= 0.90):
        return "lost on coverage"
    return "won"


# --------------------------------------------------------------------------------------------------------------
# The mapping
# --------------------------------------------------------------------------------------------------------------


def compare_block(L: Ledger, pbase, bbase, *, ci_key="ci95", p_key="p_one_sided", bp_key="p",
                  with_won_lost=True, with_margin=True, slice_mode=False):
    """A computed comparison: skill, ci95, p, days, hours, losses, days won/lost, margin, m."""
    pub = get(L.pub, pbase)
    L.det(pbase + ("skill",), bbase + ("skill",))
    for i, sk in ((0, "ci_lo"), (1, "ci_hi")):
        L.endpoint(pbase + (ci_key, i), bbase + ("ci95", i), bbase + ("seed_spread", sk))
    L.pval(pbase + (p_key,), bbase + (bp_key,), bbase + ("seed_spread", "k"), bbase + ("draws_le_margin",))
    for k in ("days", "hours", "loss_arm", "loss_ref"):
        if k in pub:
            L.det(pbase + (k,), bbase + (k,))
    for k in ("days_won", "days_lost"):
        if k in pub:
            if with_won_lost:
                L.det(pbase + (k,), bbase + (k,))
            else:
                L.skip(pbase + (k,), "the blind's slice outputs carry no days_won/days_lost (it prints them only "
                                     "for primaries and secondaries)")
    if "margin" in pub:
        if with_margin:
            L.det(pbase + ("margin",), bbase + ("margin",),
                  note="superiority margin; the blind's 'margin' is also its draw threshold m")
        else:
            L.skip(pbase + ("margin",), "the blind's slice outputs carry no margin field (its assumption 14 fixes "
                                        "margin 0 for every slice, consistent, but it is not an output)")
    if "m" in pub:
        if with_margin:
            L.det(pbase + ("m",), bbase + ("margin",),
                  note="published m = -margin is the draw threshold in p = (1 + #draws <= m)/2001; the blind's "
                       "threshold is its 'margin' field (draws <= margin, assumption 5: m = 0). -0.0 == 0.0; the "
                       "sign of zero differs, so this is equal but not bit-identical in its JSON text")
        else:
            L.skip(pbase + ("m",), "the blind's slice outputs carry no m/margin field (assumption 14: margin 0, "
                                   "consistent, but not an output)")


def build(L: Ledger):
    P, B = L.pub, L.blind

    # ---------------------------------------------------------------- top level
    L.label(("attribution",), note="data attribution text, not a result")

    # ---------------------------------------------------------------- primaries
    for pid in PIDS_RUN:
        pb, bb = ("primaries", pid), ("primaries", pid)
        bprim = B["primaries"][pid]
        for k in ("arm", "ref", "metric"):
            L.label(pb + (k,), bprim[k], bb + (k,))
            L.label(pb + ("compare", k), bprim[k], bb + (k,))
        L.label(pb + ("status",), "ok", "computed entry in blind primaries", note="blind computed this primary")
        L.label(pb + ("compare", "status"), "ok", "computed entry in blind primaries")
        L.label(pb + ("runnable",), True, "computed entry in blind primaries")
        L.label(pb + ("cause",), None, "computed entry in blind primaries", note="no cause: primary was run")
        L.det(pb + ("skill",), bb + ("skill",))
        for i, sk in ((0, "ci_lo"), (1, "ci_hi")):
            L.endpoint(pb + ("ci95", i), bb + ("ci95", i), bb + ("seed_spread", sk))
        L.pval(pb + ("p",), bb + ("p",), bb + ("seed_spread", "k"), bb + ("draws_le_margin",))
        for y in YEARS:
            L.det(pb + ("yearly", y), bb + ("yearly", y))
            L.det(pb + ("compare", "yearly", y), bb + ("yearly", y))
        L.det(pb + ("days",), bb + ("days",))
        compare_block(L, pb + ("compare",), bb)
        if pid == "P3":
            L.det(pb + ("coverage",), bb + ("coverage",))
            for y in YEARS:
                L.det(pb + ("coverage_yearly", y), bb + ("coverage_yearly", y))

    # P2: not runnable
    pb, bb = ("primaries", "P2"), ("primaries", "P2")
    for k in ("arm", "ref", "metric"):
        L.label(pb + (k,), B["primaries"]["P2"][k], bb + (k,))
        L.label(pb + ("compare", k), B["primaries"]["P2"][k], bb + (k,))
    L.label(pb + ("runnable",), False, bb + ("runnable",))
    L.label(pb + ("status",), "not run", bb + ("runnable",), note="blind runnable = False")
    L.label(pb + ("compare", "status"), "not run", bb + ("runnable",), note="blind runnable = False")
    L.label(pb + ("cause",), note="free text; blind reason: " + B["primaries"]["P2"]["reason"])
    L._use(bb + ("reason",), pb + ("cause",))
    L.label(pb + ("compare", "cause"), note="free text")
    for keys, v in leaves(P["primaries"]["P2"], pb):
        if v == "not run" and ptr(keys) not in L.labels:
            L.skip(keys, LEAR_NOT_RUN)

    # ---------------------------------------------------------------- verdicts (Holm, states)
    order = ["P1", "P2", "P3", "P4"]
    pub_raw = [P["verdicts"][q]["p_holm_input"] for q in order]
    holm_pub = holm(pub_raw)
    for j, pid in enumerate(order):
        vb = ("verdicts", pid)
        ver = P["verdicts"][pid]
        # Holm: recomputed from the published raw p, must be equal; the blind's Holm p recorded alongside
        blind_h = B["primaries"][pid]["holm_p"]
        L._use(("primaries", pid, "holm_p"), vb + ("p_holm",))
        L._use(("holm", "adjusted", j), vb + ("p_holm",))
        ok_pub = holm_pub[j] == ver["p_holm"]
        L.cat(vb + ("p_holm",), blind_h, ("holm", "adjusted", j), extra_ok=ok_pub,
              extra={"holm_recomputed_from_published_raw_p": holm_pub[j],
                     "recomputed_equals_published": ok_pub,
                     "blind_holm_equals_published": blind_h == ver["p_holm"]},
              note="TOLERANCES: Holm must be equal when recomputed from the published raw p "
                   f"({pub_raw}); also equal to the blind's Holm p")
        # states: equal to the blind's and following the spec's rules on the published numbers
        st_rule = spec_state(pid, P)
        L._use(("states", pid), vb + ("state",))
        L.cat(vb + ("state",), B["primaries"][pid]["state"], ("primaries", pid, "state"),
              extra_ok=(ver["state"] == st_rule and B["states"][pid] == ver["state"]),
              extra={"state_from_spec_rules_on_published_numbers": st_rule,
                     "blind_states_block": B["states"][pid]},
              note="statistics.verdict_states applied to the published skill, Holm p, yearly skills (P3: "
                   "coverage) and threshold")
        L.skip(vb + ("threshold",), "the blind prints no threshold (its verdict code uses 0 for P1/P3/P4); the "
                                    "threshold is an input of the state rule checked above, not a result")
        if pid == "P2":
            L.det(vb + ("p_holm_input",), ("holm", "input", 1),
                  note="P2 is not runnable and enters Holm with p = 1")
            L._use(("primaries", "P2", "p"), vb + ("p_holm_input",))
            L.skip(vb + ("p",), LEAR_NOT_RUN)
            L.skip(vb + ("ci95",), LEAR_NOT_RUN)
            L.label(vb + ("cause",), note="free text 'K1 failed'; blind reason: K1 failed on all three attempts")
        else:
            bb = ("primaries", pid)
            L.pval(vb + ("p_holm_input",), bb + ("p",), bb + ("seed_spread", "k"),
                   note="the raw p that enters Holm (= primaries p)")
            L._use(("holm", "input", j), vb + ("p_holm_input",))
            L.pval(vb + ("p",), bb + ("p",), bb + ("seed_spread", "k"))
            for i, sk in ((0, "ci_lo"), (1, "ci_hi")):
                L.endpoint(vb + ("ci95", i), bb + ("ci95", i), bb + ("seed_spread", sk))
            L.label(vb + ("cause",), None, "computed entry in blind primaries")

    # ---------------------------------------------------------------- strict
    strict_map = {
        "best_simple_2023": "t0_cal_strict vs best_simple_2023 (t0 alone without the allowance)",
        "best_simple_2023_strict": "t0_cal_strict vs best_simple_2023_strict (the old rule for both)",
    }
    for ref, bname in strict_map.items():
        pb, bb = ("strict", ref), ("strict", bname)
        L.det(pb + ("pooled",), bb + ("skill",), note=f"t0_cal_strict vs {ref}")
        for y in YEARS:
            L.det(pb + (y,), bb + ("yearly", y))
        L.det(pb + ("days",), bb + ("days",))

    # ---------------------------------------------------------------- secondaries
    for name, sec in P["secondaries"].items():
        pb = ("secondaries", name)
        if name.startswith("rMAE"):
            for ref, arms in sec.items():
                for arm, ent in arms.items():
                    eb = pb + (ref, arm)
                    if ent["status"] == "not run":
                        L.label(eb + ("status",), None, None, note="lear_ens not scored; blind rmae has no "
                                                                   "lear_ens entry (assumption 9)")
                        L.label(eb + ("cause",), note="free text")
                        continue
                    L.label(eb + ("status",), "ok", ("rmae", ref, arm))
                    L.det(eb + ("rmae",), ("rmae", ref, arm))
                    L.skip(eb + ("days",), "the blind prints no day count per rMAE (assumption 12: each pair's own "
                                           "paired day set, 572 for t0_cal_wx); no blind field to compare")
            continue
        if name == "RMSE":
            for pid, ent in sec.items():
                eb = pb + (pid,)
                if ent["status"] == "not run":
                    L.label(eb + ("status",), None, None, note="P2 not run; blind rmse has no P2 entry")
                    L.label(eb + ("cause",), note="free text")
                    continue
                L.label(eb + ("status",), "ok", ("rmse", pid))
                for arm in ent:
                    if arm in ("status", "days"):
                        continue
                    L.det(eb + (arm,), ("rmse", pid, arm))
                L.det(eb + ("days",), ("primaries", pid, "days"),
                      note="blind assumption 13: RMSE is pooled over the primary's day set, so its day count is "
                           "the primary's")
            continue
        bsec = B["secondaries"].get(name)
        if sec["status"] == "not run":
            blind_status = "not run" if (bsec and "not_run" in bsec) else None
            L.label(pb + ("status",), blind_status, ("secondaries", name, "not_run"),
                    note="blind: " + str(bsec and bsec.get("not_run")))
            for k in ("arm", "ref", "metric", "cause"):
                L.label(pb + (k,), note="label of a not-run secondary")
            for y in YEARS:
                L.skip(pb + ("yearly", y), LEAR_NOT_RUN)
            continue
        bb = ("secondaries", name)
        for k in ("arm", "ref", "metric"):
            L.label(pb + (k,), bsec[k], bb + (k,))
        L.label(pb + ("status",), "ok", "computed entry in blind secondaries")
        compare_block(L, pb, bb)
        for y in YEARS:
            L.det(pb + ("yearly", y), bb + ("yearly", y))

    # ---------------------------------------------------------------- slices
    for pid, groups in P["slices"].items():
        for gname, g in groups.items():
            kind = SLICE_GROUPS.get(gname, "single")
            entries = g.items() if kind in ("year", "quarter") else [(gname, g)]
            for sname, ent in entries:
                pb = ("slices", pid, gname) + ((sname,) if kind != "single" else ())
                if ent["status"] == "not run":
                    for keys, v in leaves(ent, pb):
                        L.label(keys, note="P2 slice not run; the blind has no P2 slices (assumption 9)")
                    continue
                bb = ("slices", pid, sname)
                L.label(pb + ("arm",), B["primaries"][pid]["arm"], ("primaries", pid, "arm"))
                L.label(pb + ("ref",), B["primaries"][pid]["ref"], ("primaries", pid, "ref"))
                if ent["status"] == "no days":
                    # an empty day set is a result: the blind must also find no days
                    L.cat(pb + ("status",), B["slices"][pid][sname]["status"], bb + ("status",),
                          note="empty slice (P4 starts at AVAIL.p4_first_day 2024-06-06)")
                    for k in ("skill", "days", "hours", "ci95", "p"):
                        L._use(bb + (k,), pb + ("status",))
                    continue
                L.label(pb + ("status",), "ok", "computed entry in blind slices")
                if kind == "year":
                    L.det(pb + ("skill",), bb + ("skill",))
                    L.det(pb + ("days",), bb + ("days",))
                    continue
                compare_block(L, pb, bb, with_won_lost=False, with_margin=False, slice_mode=True)

    # ---------------------------------------------------------------- tables
    for pid, tab in P["tables"].items():
        if tab["status"] == "not run":
            L.label(("tables", pid, "status"), note="P2 not run; the blind has no P2 tables")
            continue
        L.label(("tables", pid, "status"), "ok", "computed entry in blind tables")
        cb = ("tables", pid, "concentration")
        L.label(cb + ("model",), B["primaries"][pid]["arm"], ("primaries", pid, "arm"))
        L.label(cb + ("reference",), B["primaries"][pid]["ref"], ("primaries", pid, "ref"))
        bc = ("concentration", pid)
        L.det(cb + ("net_gain_mw",), bc + ("net_gain",))
        L.det(cb + ("n_days",), ("primaries", pid, "days"), note="concentration runs on the primary's per-day "
                                                                  "table, so n_days is the primary's day count")
        L.det(cb + ("skill",), ("primaries", pid, "skill"), note="the primary's pooled skill")
        for n in (5, 10, 20):
            L.det(cb + (f"top{n}_share_of_net_gain",), bc + (f"top{n}_share",))
            L.det(cb + (f"skill_without_top{n}",), bc + (f"skill_without_top{n}",))
        brows = {r["block"]: i for i, r in enumerate(B["bootstrap_sensitivity"][pid])}
        for i, row in enumerate(tab["bootstrap_sensitivity"]):
            rb = ("tables", pid, "bootstrap_sensitivity", i)
            L_ = row["block_days"]
            j = brows[L_]
            bsb = ("bootstrap_sensitivity", pid, j)
            L.label(rb + ("model",), B["primaries"][pid]["arm"], ("primaries", pid, "arm"))
            L.label(rb + ("reference",), B["primaries"][pid]["ref"], ("primaries", pid, "ref"))
            L.label(rb + ("block_days",), B["bootstrap_sensitivity"][pid][j]["block"], bsb + ("block",))
            L.det(rb + ("skill",), ("primaries", pid, "skill"), note="the primary's pooled skill")
            for k, ci_i, sk in (("skill_lo95", 0, "ci_lo"), ("skill_hi95", 1, "ci_hi")):
                if L_ == 14:
                    L.endpoint(rb + (k,), bsb + ("ci95", ci_i), ("primaries", pid, "seed_spread", sk),
                               note="block 14 is the primary's own bootstrap, so the primary's 200-seed spread "
                                    "applies")
                else:
                    rec = L.endpoint(rb + (k,), bsb + ("ci95", ci_i), None)
                    if rec is None:
                        pubv, s0 = row[k], B["bootstrap_sensitivity"][pid][j]["ci95"][ci_i]
                        L.skip(rb + (k,), f"bootstrap endpoint at block {L_}: the blind prints seed 0 only (no "
                                          f"200-seed spread at this block length), and its seed-0 value "
                                          f"{s0!r} is not bit-identical to the published {pubv!r} "
                                          f"(rel diff {abs(s0 - pubv) / abs(pubv):.2e}), so the pre-committed "
                                          f"Monte-Carlo rule cannot be applied")
                        L._use(bsb + ("ci95", ci_i), rb + (k,))

    # ---------------------------------------------------------------- carry-forward
    for pid, cf in P["carry_forward"].items():
        pb = ("carry_forward", pid)
        L.label(pb + ("arm",), B["primaries"][pid]["arm"], ("primaries", pid, "arm"))
        L.label(pb + ("ref",), B["primaries"][pid]["ref"], ("primaries", pid, "ref"))
        if pid == "P2":
            L.label(pb + ("status",), note="P2 not run; the blind has no P2 carry-forward")
            L.cat(pb + ("state",), B["states"]["P2"], ("states", "P2"))
            L.skip(pb + ("candidate",), "the blind prints no carry-forward for P2 (not runnable); its rule makes "
                                        "candidacy require 'won', which is consistent with false, but there is no "
                                        "blind field")
            L.skip(pb + ("delta",), "the blind prints no carry-forward for P2 (not runnable); no blind delta")
            continue
        bb = ("carry_forward", pid)
        L.label(pb + ("status",), "ok", "computed entry in blind carry_forward")
        L.cat(pb + ("state",), B["carry_forward"][pid]["state"], bb + ("state",))
        L.cat(pb + ("candidate",), B["carry_forward"][pid]["candidate"], bb + ("candidate",),
              note="TOLERANCES: candidacy must be equal")
        L.cat(pb + ("delta",), B["carry_forward"][pid]["delta"], bb + ("delta",),
              note="TOLERANCES: delta must be equal")
        L.det(pb + ("S",), bb + ("S",))
        L.det(pb + ("days",), bb + ("A_days",), note="A's day count")
        L.rounded(pb + ("block_sd",), bb + ("unrounded", "block_sd"), 3, bkeys_rounded=bb + ("block_sd",))
        L.rounded(pb + ("ref_mae",), bb + ("unrounded", "ref_mae"), 3, bkeys_rounded=bb + ("ref_mae",))
        rec = L.rounded(pb + ("M",), bb + ("unrounded", "M"), 4, bkeys_rounded=bb + ("M",),
                        note="conditional on the code's formula (power_table given to the replicator as a written "
                             "statement); TOLERANCES: M must agree to 4 decimals")
        L._use(bb + ("unrounded", "M_k", "12"), pb + ("M",))
        L._use(bb + ("M_k_rounded", "12"), pb + ("M",))
        rec["conditional_on_code_formula"] = True
        for key in cf["M_info"]:
            div = key.split("/")[1]
            r2 = L.rounded(pb + ("M_info", key), None, 4, bkeys_rounded=bb + ("M_info", f"alpha/{div}"),
                           note="information only; the blind prints M_info rounded to 4 decimals only, so rounded "
                                "values are compared; conditional on the code's formula")
            r2["conditional_on_code_formula"] = True


# --------------------------------------------------------------------------------------------------------------
# Short series: the frozen bootstrap shortens the block when a day set has fewer than 2 * 14 days
# --------------------------------------------------------------------------------------------------------------
BLOCK_DAYS = 14
SHORT_NOTE = ("short series: n_days = {n} < 2 * 14. The frozen metrics.bootstrap_skill (unchanged since 2b407f4) "
              "uses block = max(1, min(block_days, n_days // 2)) = {fb} days here and logs that the interval is "
              "'indicative only'; the blind used min(14, n) = {bb} days (the packet's documented behaviour of "
              "bootstrap_skill and the spec's 'block_days=14' do not mention the reduction). The two procedures "
              "differ, so the seed spread is not a like-for-like range for this field{tail}")


def annotate_short_series(L: Ledger):
    for r in L.fields.values():
        if r["kind"] not in ("bootstrap_endpoint", "bootstrap_p"):
            continue
        parts = r["published_path"].split("/")
        # the comparison block is the path without its last key (and without the ci95 index)
        base = parts[:-2] if parts[-2] == "ci95" else parts[:-1]
        try:
            n = get(L.pub, [s.replace("~1", "/").replace("~0", "~") for s in base[1:]] + ["days"])
        except (KeyError, TypeError):
            continue
        if not isinstance(n, int) or n >= 2 * BLOCK_DAYS:
            continue
        tail = ("; it passes the Monte-Carlo rule by coincidence" if r["class"] == "within_mc" else "")
        r["short_series"] = {"n_days": n, "frozen_block": max(1, min(BLOCK_DAYS, n // 2)),
                             "blind_block": min(BLOCK_DAYS, n)}
        r["note"] = (r.get("note", "") + "; " if r.get("note") else "") + SHORT_NOTE.format(
            n=n, fb=r["short_series"]["frozen_block"], bb=r["short_series"]["blind_block"], tail=tail)


def frozen_short_series_check(artifact: Path, pub: dict) -> dict:
    """Optional diagnosis (NOT independent): rerun the repository's metrics.bootstrap_skill on the artifact's
    per-day table restricted to each short whole-day slice, and see whether it reproduces the published values.
    Only quarter and DST-week slices of P4 are short in this run; their day sets are rebuilt here."""
    import pandas as pd
    sys.path.insert(0, str(HERE.parents[2]))
    from solarbench import metrics  # noqa: E402  (repository code, used for diagnosis only)
    import logging
    logging.disable(logging.WARNING)
    out = {}
    dst_switch = ["2024-03-31", "2024-10-27", "2025-03-30", "2025-10-26"]  # Paris 23/25-hour days
    dst_days = {str((pd.Timestamp(d) + pd.Timedelta(days=k)).date()) for d in dst_switch for k in range(7)}
    for pid in PIDS_RUN:
        table = pd.read_csv(artifact / f"per_day_{pid}.csv", float_precision="round_trip")
        arm, ref = pub["primaries"][pid]["arm"], pub["primaries"][pid]["ref"]
        cands = {("the weeks after each DST switch",): table["delivery_date"].isin(dst_days)}
        for q, ent in pub["slices"][pid]["each quarter (2025 Q4 is quarter-hour derived)"].items():
            yr, qn = int(q[:4]), int(q[-1])
            lo = f"{yr}-{3 * qn - 2:02d}-01"
            hi = str((pd.Timestamp(yr, 3 * qn, 1) + pd.offsets.MonthEnd(0)).date())
            cands[("each quarter (2025 Q4 is quarter-hour derived)", q)] = table["delivery_date"].between(lo, hi)
        for keys, mask in cands.items():
            ent = get(pub["slices"][pid], keys)
            if ent.get("status") != "ok" or ent["days"] >= 2 * BLOCK_DAYS:
                continue
            sub = table[mask]
            n = int(sub["delivery_date"].nunique())
            res = {"n_days_rebuilt": n, "n_days_published": ent["days"]}
            for label, bd in (("frozen_block_days_14", 14),):
                r = metrics.bootstrap_skill(sub, model=arm, reference=ref, block_days=bd, samples=N_DRAWS, seed=0,
                                            return_draws=True)
                k = int(np.sum(np.asarray(r["draws"]) <= 0.0))
                res[label] = {"block_used": max(1, min(bd, n // 2)), "ci95": [r["skill_lo95"], r["skill_hi95"]],
                              "p": (1 + k) / (N_DRAWS + 1)}
                res["reproduces_published_bit_for_bit"] = (
                    [r["skill_lo95"], r["skill_hi95"]] == ent["ci95"] and (1 + k) / (N_DRAWS + 1) ==
                    ent["p_one_sided"])
            out[ptr(("slices", pid) + keys)] = res
    logging.disable(logging.NOTSET)
    return out


# --------------------------------------------------------------------------------------------------------------
# Blind-only fields
# --------------------------------------------------------------------------------------------------------------


def blind_only_reason(bkeys) -> str | None:
    k = [str(x) for x in bkeys]
    top = k[0]
    if top in ("files_read", "assumptions", "data_checks"):
        return "blind metadata (files read, assumptions, data checks); no published counterpart"
    if "seed_spread" in k:
        return "blind seed spread; used as the Monte-Carlo range wherever its seed-0 statistic is compared"
    if top == "holm" and k[1] == "order":
        return "Holm input order; matches the published family order P1, P2, P3, P4"
    if top == "primaries":
        if k[2] in ("yearly_pass",):
            return "per-year pass flags; results.json prints no flags (they enter the state, which is compared)"
        if k[2] == "coverage_hours_in_band":
            return "coverage numerator; results.json prints only the share (compared)"
    if top == "strict":
        return ("duplicate of the blind's secondaries entry of the same name (identical values; that entry is the "
                "one compared with results.json secondaries)" if k[2] in ("ci95", "p", "arm", "ref") or
                k[1].startswith("t0_cal vs") else None)
    if top == "secondaries" and k[-1] == "not_run":
        if k[1].startswith("rMAE") or k[1] == "RMSE":
            return "pointer to the blind's top-level rmae/rmse blocks (compared there)"
    if top == "rmae" and k[2] == "best_simple_eq":
        return "rMAE of best_simple_eq; results.json prints no rMAE for best_simple_eq"
    if top == "slices":
        if k[2] in YEARS and k[3] in ("hours", "ci95", "p", "draws_le_margin", "loss_arm", "loss_ref"):
            return "results.json's per-year slices print only skill and days"
        if k[3] == "threshold_abs_y":
            return "the |y| threshold of the top-1% slice; results.json does not print it"
    if top == "bootstrap_sensitivity" and k[3] == "p":
        return "results.json's sensitivity table prints no p"
    if top == "carry_forward":
        if k[2] == "n_blocks_kept":
            return "number of 14-day blocks kept; results.json does not print it"
        if k[2] in ("unrounded", "M_k_rounded") and k[-1] in ("6", "8"):
            return "M at 6 and 8 blocks; results.json prints only M (12 blocks)"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--blind", type=Path, default=DEFAULT_BLIND,
                    help="directory holding blind_outputs.json and blind_replicate.py")
    ap.add_argument("--artifact", type=Path, default=None,
                    help="optional: the authenticated unzipped artifact (per_day_P*.csv) for the short-series "
                         "diagnosis with the repository's bootstrap (not independent; decides nothing)")
    args = ap.parse_args()
    blind_json = args.blind / "blind_outputs.json"
    blind_py = args.blind / "blind_replicate.py"
    pub = json.loads(PUBLISHED.read_text())
    blind = json.loads(blind_json.read_text())
    L = Ledger(pub, blind)
    build(L)
    annotate_short_series(L)

    # ------------------------------------------------------------ coverage: every published leaf accounted for
    accounted = set(L.fields) | set(L.labels) | set(L.not_compared)
    missing = []
    for keys, v in leaves(pub):
        p = ptr(keys)
        if p in accounted:
            continue
        # a leaf of a list-valued field compared element-wise is accounted under its index pointer
        missing.append(p)
    if missing:
        raise SystemExit(f"published leaves not accounted for: {missing[:20]} (+{max(0, len(missing) - 20)})")
    extra = accounted - {ptr(k) for k, _ in leaves(pub)}
    if extra:
        raise SystemExit(f"ledger paths not in results.json: {sorted(extra)[:20]}")

    # ------------------------------------------------------------ every blind field mapped or explained
    blind_map, unmapped = {}, []
    spread_parents = set()
    for keys, v in leaves(blind):
        if "seed_spread" in keys:
            idx = keys.index("seed_spread")
            spread_parents.add(keys[: idx + 2])
            continue
        p = ptr(keys)
        if p in L.blind_used:
            blind_map[p] = {"published": sorted(L.blind_used[p])}
        else:
            reason = blind_only_reason(keys)
            if reason is None:
                unmapped.append(p)
            else:
                blind_map[p] = {"published": [], "reason": reason}
    for sk in sorted(spread_parents, key=ptr):
        p = ptr(sk)
        if p in L.blind_used:
            blind_map[p + "[0..199]"] = {"published": sorted(L.blind_used[p]),
                                         "reason": "seed spread (seeds 0..199) used as the Monte-Carlo range"}
        elif sk[0] == "slices" and sk[2] in YEARS:
            blind_map[p + "[0..199]"] = {"published": [], "reason": "seed spread of a per-year slice; results.json's "
                                                                    "per-year slices print no interval or p"}
        elif sk[0] == "slices" and blind["slices"][sk[1]][sk[2]].get("status") == "no days":
            blind_map[p] = {"published": sorted(L.blind_used.get(ptr(sk[:3] + ("status",)), [])),
                            "reason": "null spread of an empty ('no days') slice"}
        else:
            unmapped.append(p)
    if unmapped:
        raise SystemExit(f"blind leaves neither mapped nor explained: {unmapped[:30]}")

    # ------------------------------------------------------------ consistency of the blind with itself
    self_checks = {}
    for pid in PIDS_RUN:
        b = blind["primaries"][pid]
        s14 = next(r for r in blind["bootstrap_sensitivity"][pid] if r["block"] == 14)
        self_checks[f"{pid}: sensitivity block 14 == primary ci95 and p"] = (s14["ci95"] == b["ci95"]
                                                                             and s14["p"] == b["p"])
        self_checks[f"{pid}: holm_p == holm.adjusted"] = (
            b["holm_p"] == blind["holm"]["adjusted"][["P1", "P2", "P3", "P4"].index(pid)])
    for name, s in blind["strict"].items():
        sec = blind["secondaries"][name]
        self_checks[f"strict '{name}' == secondaries entry"] = all(
            s[k] == sec[k] for k in ("skill", "yearly", "days", "ci95", "p"))
    bad_self = [k for k, v in self_checks.items() if not v]

    # ------------------------------------------------------------ label consistency
    bad_labels = [r for r in L.labels.values() if r.get("consistent") is False]

    # ------------------------------------------------------------ seed-0 bit-for-bit summary
    def boot(rs, kind):
        return [r for r in rs if r["kind"] == kind]

    all_rec = list(L.fields.values())
    ends = boot(all_rec, "bootstrap_endpoint")
    prim_ci = [r for r in ends if r["published_path"].startswith("/primaries/") and "/ci95/" in r["published_path"]
               and "/compare/" not in r["published_path"]]
    ps = boot(all_rec, "bootstrap_p")
    # the not-compared sensitivity endpoints are seed-0 comparisons too
    sens_nc = [r for r in L.not_compared.values() if "bootstrap_sensitivity" in r["published_path"]]

    def rel_max(rs):
        vals = [r["seed0_rel_diff"] for r in rs if r.get("seed0_rel_diff") is not None]
        return max(vals) if vals else None

    bit = {
        "primaries_ci95_bit_identical_at_seed0": all(r["seed0_bit_exact"] for r in prim_ci),
        "primaries_ci95_endpoints": {r["published_path"]: {"published": r["published"], "blind_seed0":
                                                           r["blind_seed0"], "bit_exact": r["seed0_bit_exact"],
                                                           "rel_diff": r["seed0_rel_diff"]} for r in prim_ci},
        "all_endpoints_compared": len(ends),
        "all_endpoints_bit_identical_at_seed0": sum(r["seed0_bit_exact"] for r in ends),
        "endpoints_not_bit_identical_but_within_1e-12_relative": sum(
            (not r["seed0_bit_exact"]) and r["seed0_rel_diff"] is not None and r["seed0_rel_diff"] <= 1e-12
            for r in ends),
        "endpoints_max_seed0_rel_diff_excluding_short_series": rel_max(
            [r for r in ends if "short_series" not in r]),
        "short_series_endpoints (block reduced by the frozen code; see discrepancies)": len(
            [r for r in ends if "short_series" in r]),
        "sensitivity_endpoints_without_spread_not_bit_identical": len(sens_nc),
        "sensitivity_endpoints_without_spread_max_seed0_rel_diff": max(
            (abs(float(r["reason"].split("rel diff ")[1].split(")")[0])) for r in sens_nc), default=None),
        "p_values_compared": len(ps),
        "p_values_bit_identical_at_seed0": sum(r["seed0_bit_exact"] for r in ps),
        "reading": ("the blind seed-0 bootstrap reproduces the published draws (same numpy default_rng(0) block "
                    "starts) but not bit for bit: endpoints differ in the last few ulps because the blind sums "
                    "block totals in a different order; p (an integer count) matches exactly wherever the "
                    "procedures agree"),
    }

    # ------------------------------------------------------------ counts and output
    counts = {"exact": 0, "within_mc": 0, "discrepancy": 0, "not_compared": len(L.not_compared)}
    by_kind: dict[str, dict[str, int]] = {}
    for r in all_rec:
        counts[r["class"]] += 1
        by_kind.setdefault(r["kind"], {}).setdefault(r["class"], 0)
        by_kind[r["kind"]][r["class"]] += 1
    discrepancies = [r for r in all_rec if r["class"] == "discrepancy"]
    diagnosis = None
    if args.artifact is not None:
        diagnosis = {
            "what": "the repository's metrics.bootstrap_skill (unchanged since the frozen commit 2b407f4) rerun on "
                    "the authenticated artifact's per-day table, restricted to each short slice; NOT independent, "
                    "diagnosis only, changes no classification",
            "artifact": str(args.artifact),
            "per_day_sha256": {pid: sha256(args.artifact / f"per_day_{pid}.csv") for pid in PIDS_RUN},
            "slices": frozen_short_series_check(args.artifact, pub),
        }

    out = {
        "track": "1: blind independent re-implementation vs published results.json",
        "tolerances": "docs/experiment_4/replication/TOLERANCES.md (committed before any comparison), applied as "
                      "written; see this script's docstring",
        "inputs": {
            "published": {"path": str(PUBLISHED.relative_to(HERE.parents[2])), "sha256": sha256(PUBLISHED)},
            "blind_outputs": {"path": str(blind_json), "sha256": sha256(blind_json)},
            "blind_script": {"path": str(blind_py), "sha256": sha256(blind_py) if blind_py.exists() else None},
        },
        "rules": {
            "deterministic": "relative difference <= 1e-9, or absolute <= 1e-12 when the published value is 0; "
                             "integers equal",
            "rounded": "results.json prints block_sd and ref_mae to 3 decimals and M, M_info to 4: compared as "
                       "round(blind, d) == published; M is conditional on the code's formula",
            "bootstrap_endpoint": "exact if the blind seed-0 value is bit-identical; otherwise within_mc if the "
                                  "published value is inside numpy.percentile(blind seeds 0..199, [0.5, 99.5]) "
                                  "(linear, inclusive); otherwise discrepancy",
            "bootstrap_p": "as for endpoints, on the draw count k = p*2001 - 1 against the blind k spread",
            "holm": "recomputed from the published raw p (Holm step-down, capped at 1) and equal to the published "
                    "p_holm; the blind's Holm p is also required equal",
            "states": "equal to the blind state and to statistics.verdict_states applied to the published numbers",
            "delta_candidate": "equal",
        },
        "counts": counts,
        "counts_by_kind": by_kind,
        "seed0_bit_for_bit": bit,
        "blind_self_consistency": {"checks": self_checks, "failed": bad_self},
        "label_mapping_inconsistencies": bad_labels,
        "discrepancies": discrepancies,
        "short_series_diagnosis": diagnosis,
        "fields": all_rec,
        "not_compared": list(L.not_compared.values()),
        "labels": list(L.labels.values()),
        "blind_field_map": blind_map,
    }
    OUT.write_text(json.dumps(out, indent=1, default=num, allow_nan=False) + "\n")

    print(f"wrote {OUT}")
    print("counts:", json.dumps(counts))
    print("by kind:", json.dumps(by_kind))
    print("primaries ci95 bit-identical at seed 0:", bit["primaries_ci95_bit_identical_at_seed0"])
    print(f"endpoints bit-identical at seed 0: {bit['all_endpoints_bit_identical_at_seed0']}/{len(ends)}; "
          f"p bit-identical: {bit['p_values_bit_identical_at_seed0']}/{len(ps)}")
    print("blind self-consistency failures:", bad_self)
    print("label inconsistencies:", [r["published_path"] for r in bad_labels])
    for r in discrepancies:
        extra_s = ""
        if r["kind"] == "bootstrap_endpoint":
            extra_s = f" range=[{r['spread_p0_5']!r}, {r['spread_p99_5']!r}] min={r['spread_min']!r} " \
                      f"max={r['spread_max']!r}"
        elif r["kind"] == "bootstrap_p":
            extra_s = f" k_pub={r['published_k']:.6f} k_range=[{r['spread_k_p0_5']}, {r['spread_k_p99_5']}]"
        print(f"DISCREPANCY {r['published_path']}: published={r['published']!r} "
              f"blind={r.get('blind', r.get('blind_seed0'))!r}{extra_s}")
    if diagnosis is not None:
        for p, d in diagnosis["slices"].items():
            print(f"diagnosis {p}: n={d['n_days_rebuilt']} frozen block={d['frozen_block_days_14']['block_used']} "
                  f"reproduces published bit for bit: {d['reproduces_published_bit_for_bit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
