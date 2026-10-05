"""The final-kernel observe step: per episode, the observed data and the context for the research jobs, and the holdout
data for the referee jobs (FINAL_KERNEL_SPEC.md sections 4-5). Nothing else leaves the truth side.

Per episode ``<company>e<episode>`` (``c1e1`` ... ``c4e3``):
- ``obs/<ep>/``: ``observed.npz`` (days 1-126 of the target and X01-X08), ``observed.json`` (neutral: episode key,
  days, keys, array hash), ``context.txt`` (the rendered context the researcher reads) and ``context.json`` (company,
  period, regime and the source names by X id, for the referee). K and F of an episode read this same directory.
- ``holdout/<ep>/``: ``holdout.npz`` (days 1-154 of the same observed series) and ``holdout.json``.
Seeds and designs come from ``world.design`` (spec hash and run id; preflight: ``final_kernel-preflight:<run id>``,
company c1 only). Refusals: t0-beta pinned, frozen files present, the lesson's hash; the scored run also needs a
published preflight PASS under the same ``final_kernel_spec_sha``, must be the run's first attempt and must find no
published scored final-kernel run.

    python -m research_loop_proof.final_kernel.truth.observe --mode preflight|run --run-id ID --run-attempt N \
        [--preflight-dir D] [--published-dir D] --out D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth.observe import _run_id
from research_loop_proof.final_kernel.truth import spec
from research_loop_proof.final_kernel.truth.world import EPISODES, design, episode_context, episode_world
from research_loop_proof.learn1.lab.researcher import frozen_lesson
from research_loop_proof.phase0.truth.generator import WORLD, arrays_sha256, observed_arrays

RUN_PHASE = "final-kernel-run"
PREFLIGHT_PHASE = "final-kernel-preflight"
PB = WORLD["phase_b"]


def ep_key(company: str, episode: int) -> str:
    return f"{company}e{episode}"


def designs(mode: str, run_id: str) -> dict:
    return design(spec.spec_sha(), _run_id(run_id), preflight=(mode == "preflight"))


def published_errors(d: Path, phase: str) -> list[str]:
    try:
        body = (d / "verdict.json").read_bytes()
        manifest = (d / "MANIFEST.sha256").read_text()
    except OSError as exc:
        return [f"published result not readable: {exc}"]
    listed = {ln[66:].strip(): ln[:64] for ln in manifest.splitlines() if len(ln) > 66}
    errs = []
    if listed.get("verdict.json") != hashlib.sha256(body).hexdigest():
        errs.append("verdict.json does not match its manifest")
    v = json.loads(body)
    if v.get("phase") != phase or v.get("verdict") != "PASS":
        errs.append(f"{v.get('phase')!r} verdict {v.get('verdict')!r}, not a {phase} PASS")
    if v.get("spec_sha") != spec.spec_sha():
        errs.append(f"it ran under final_kernel_spec_sha {v.get('spec_sha')}, not the current {spec.spec_sha()}")
    return errs


def scored_runs(published_dir: str | None) -> list[str]:
    found = []
    for p in sorted(Path(published_dir).glob("*/verdict.json")) if published_dir else []:
        try:
            if json.loads(p.read_text()).get("phase") == RUN_PHASE:
                found.append(p.parent.name)
        except (OSError, ValueError):
            found.append(p.parent.name + " (unreadable verdict)")
    return found


def refusals(mode: str, run_attempt: str, preflight_dir: str | None, published_dir: str | None) -> list[str]:
    errs = [] if t0_beta.PINNED else ["t0-beta is not pinned"]
    if spec.missing():
        errs.append("frozen files missing: " + ", ".join(spec.missing()))
    try:
        frozen_lesson()
    except Exception as exc:
        errs.append(str(exc))
    if mode == "run":
        errs += published_errors(Path(preflight_dir or "missing"), PREFLIGHT_PHASE)
        if str(run_attempt) != "1":
            errs.append(f"run attempt {run_attempt}: the scored batch is dispatched once and never re-run")
        if published_dir is None or not Path(published_dir).is_dir():
            errs.append("the list of published final-kernel runs was not provided")
        elif scored_runs(published_dir):
            errs.append("a scored final-kernel run is already published: " + ", ".join(scored_runs(published_dir)))
    return errs


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(d: dict, episode: int, out: Path) -> dict:
    """Write one episode's observed and holdout directories; return their hashes."""
    w, _ = episode_world(d, episode)
    ctx = episode_context(d, episode)
    key = ep_key(d["company"], episode)
    obs_dir, hold_dir = out / "obs" / key, out / "holdout" / key
    obs_dir.mkdir(parents=True, exist_ok=True)
    hold_dir.mkdir(parents=True, exist_ok=True)
    obs = observed_arrays(w, PB["observed_days"][1])
    np.savez(obs_dir / "observed.npz", **obs)
    (obs_dir / "observed.json").write_text(json.dumps({"episode": key, "days": PB["observed_days"],
                                                       "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)},
                                                      indent=1) + "\n")
    (obs_dir / "context.txt").write_text(ctx["text"], encoding="utf-8")
    (obs_dir / "context.json").write_text(json.dumps({k: ctx[k] for k in ("company", "company_name", "episode",
                                                                          "regime", "names")}, indent=1) + "\n")
    full = observed_arrays(w, w.n_days)
    np.savez(hold_dir / "holdout.npz", **full)
    (hold_dir / "holdout.json").write_text(json.dumps({"episode": key, "days": [1, w.n_days], "keys": sorted(full),
                                                       "arrays_sha256": arrays_sha256(full)}, indent=1) + "\n")
    return {"obs": arrays_sha256(obs), "ctx": file_sha(obs_dir / "context.txt"), "hold": arrays_sha256(full)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["preflight", "run"], required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--run-attempt", required=True)
    ap.add_argument("--preflight-dir")
    ap.add_argument("--published-dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    errs = refusals(args.mode, args.run_attempt, args.preflight_dir, args.published_dir)
    if errs:
        print("refused: " + "; ".join(errs))
        return 1
    out = Path(args.out)
    shas = {}
    for k, d in designs(args.mode, args.run_id).items():
        for e in EPISODES:
            for kind, sha in export(d, e, out).items():
                shas[f"{ep_key(k, e)}_{kind}"] = sha
    (out / "shas.env").write_text("".join(f"{k}={v}\n" for k, v in shas.items()))
    print(json.dumps({"mode": args.mode, "spec_sha": spec.spec_sha(), "run_id": args.run_id, "shas": shas}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
