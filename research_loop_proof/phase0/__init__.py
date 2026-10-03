"""Phase 0: a falsification spike (docs/research_loop_proof/PHASE0_SPEC.md).

- ``truth/``: the generator, the calibration and the evaluators. The research job never has this folder.
- ``lab/``: what the research job runs: the instruments, the experiment executor, the AI researcher loop and the
  frozen scripted strategy. Nothing under ``lab/`` imports ``truth`` (a test enforces it).
"""
