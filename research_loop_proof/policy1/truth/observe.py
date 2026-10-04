"""The policy1 observe step: observed data only, for the replays, the preflight and the one scored world.

- ``replay`` (non-scored engineering check, NEXT_POLICY_ARCHITECTURE_PROMPT.md section 6): regenerates the beta1
  and learn1 scored worlds from their frozen code and refuses unless their observed hashes equal the published ones. It
  exports days 1-126 of each, plus the requests (covariates, reference, window only) of the first two calls of the
  published research record (beta1's researcher; learn1's L), checked against pinned hashes and their manifests.
  These worlds' truths are already published; the research job still receives none of it.
- ``preflight``: a non-scored world, seed ``int(sha256('policy1-preflight:<run id>')[:16], 16)``.
- ``run``: the one scored world, beta1's family unchanged (Phase 0's "phase_b" parameters and generator), seed
  ``int(sha256('policy1:<policy1_spec_sha>:<run id>')[:16], 16)``: it cannot exist before the dispatch. Refused unless
  every frozen file is present, the lesson matches its hash, t0-beta is pinned and a published policy1 preflight PASS
  ran under the same ``policy1_spec_sha``.

    python -m research_loop_proof.policy1.truth.observe --mode replay --published D --out D
    python -m research_loop_proof.policy1.truth.observe --mode preflight|run --run-id ID [--preflight-dir D] --out D
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from research_loop_proof.beta1.lab import t0_beta
from research_loop_proof.beta1.truth import observe as beta1_observe
from research_loop_proof.beta1.truth.observe import PB, _run_id, _world
from research_loop_proof.learn1.lab.researcher import frozen_lesson
from research_loop_proof.learn1.truth import observe as learn1_observe
from research_loop_proof.policy1.truth import spec
from research_loop_proof.phase0.truth.generator import World, arrays_sha256, observed_arrays

PREFIX_CALLS = 2
REPLAYS = {
    "beta1": {"run": "37201189113", "branch": "beta1/run-37201189113", "record": "ai.json",
              "record_sha256": "901658e89c57506ace63149eae941860f95d5df33c6f5385c4c2deef04a81b39",
              "observed_sha256": "e2a06ade080cd260c06634cb204be035a56161efca0c836b90a65e2612888143",
              "world": beta1_observe.hidden_world},
    "learn1": {"run": "37218439239", "branch": "learn1/run-37218439239", "record": "L/ai.json",
               "record_sha256": "8c2a7f41badbd050ed86f454ed382ac445e9bc8e4b4434bb40df0bfe40dc00f9",
               "observed_sha256": "659772fe4e1ca42e3f3d26da3a284761e9b61a26d4aee48300457c85cc40a612",
               "world": learn1_observe.hidden_world},
}


def hidden_world(run_id: str) -> World:
    return _world(f"policy1:{spec.spec_sha()}:{_run_id(run_id)}")


def preflight_world(run_id: str) -> World:
    return _world(f"policy1-preflight:{_run_id(run_id)}")


def published_errors(d: Path, phase: str) -> list[str]:
    """Why a published result (verdict.json listed in its manifest) is not a PASS of ``phase`` under this spec."""
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
        errs.append(f"it ran under policy1_spec_sha {v.get('spec_sha')}, not the current {spec.spec_sha()}")
    return errs


def refusals(mode: str, preflight_dir: str | None) -> list[str]:
    errs = [] if t0_beta.PINNED else ["t0-beta is not pinned"]
    if spec.missing():
        errs.append("frozen files missing: " + ", ".join(spec.missing()))
    try:
        frozen_lesson()
    except Exception as exc:
        errs.append(str(exc))
    if mode == "run":
        errs += published_errors(Path(preflight_dir or "missing"), "policy1-preflight")
    return errs


def published_record(d: Path, name: str) -> dict:
    """A published research record, refused unless it holds the pinned bytes and its manifest lists them."""
    r = REPLAYS[name]
    body = (d / "record.json").read_bytes()
    got = hashlib.sha256(body).hexdigest()
    listed = {ln[66:].strip(): ln[:64] for ln in (d / "MANIFEST.sha256").read_text().splitlines() if len(ln) > 66}
    if got != r["record_sha256"] or listed.get(r["record"]) != got:
        raise ValueError(f"{name}: {r['record']} sha256 {got} is not the pinned published record")
    return json.loads(body)


def replay_prefix(ai: dict) -> list[list[dict]]:
    return [[{k: e["request"][k] for k in ("covariates", "reference", "window_days")} for e in c["experiments"]]
            for c in ai["calls"][:PREFIX_CALLS]]


def export(out: Path, obs: dict, meta: dict) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "observed.npz", **obs)
    meta = {**meta, "days": PB["observed_days"], "keys": sorted(obs), "arrays_sha256": arrays_sha256(obs)}
    (out / "observed.json").write_text(json.dumps(meta, indent=1) + "\n")
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["replay", "preflight", "run"], required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--preflight-dir")
    ap.add_argument("--published")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    if args.mode == "replay":
        metas = {}
        for name, r in REPLAYS.items():
            obs = observed_arrays(r["world"](r["run"]), PB["observed_days"][1])
            if arrays_sha256(obs) != r["observed_sha256"]:
                print(f"refused: the regenerated {name} world does not match its published observed hash")
                return 1
            prefix = replay_prefix(published_record(Path(args.published) / name, name))
            metas[name] = export(out / name, obs, {"mode": "replay", "replay_of": r["branch"]})
            (out / name / "prefix.json").write_text(json.dumps({"replay_of": r["branch"], "prefix": prefix},
                                                               indent=1) + "\n")
        print(json.dumps(metas))
        return 0
    errs = refusals(args.mode, args.preflight_dir)
    if errs:
        print("refused: " + "; ".join(errs))
        return 1
    w = preflight_world(args.run_id) if args.mode == "preflight" else hidden_world(args.run_id)
    meta = export(out, observed_arrays(w, PB["observed_days"][1]),
                  {"mode": args.mode, "spec_sha": spec.spec_sha(), "run_id": args.run_id})
    print(json.dumps(meta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
