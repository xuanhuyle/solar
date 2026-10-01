# Experiment 4: the scored run's original artifact

`prices-run-36823477529.zip` is the artifact `prices-run-36823477529` (id 11145568607) of Actions run 36823477529, the scored run of
Experiment 4 at commit `2b407f42c03d2734ef4170cfb3e66962dbba9552`. It was copied byte for byte by run 36844558893 of
`.github/workflows/exp4-evidence-copy.yml` (workflow commit `ca8d73b0959ea276f963c0849861cc07c02ee566`). That run checked the copy
against the sha256 digest GitHub recorded when the artifact was uploaded:
`98d8ca1f7c6f8f6bdfeba807b925bfee25ed1cd9da7a5e46b24acc88be436165`.

- `artifact_api.json` and `run_api.json`: the GitHub API records of the artifact and of its run, as
  returned at copy time.
- `manifest.json`: the zip's size and sha256, and each member's size, CRC32 and sha256.
- `SHA256SUMS`: sha256 of every file on this branch except itself and this README.

To check the copy, compare `sha256sum prices-run-36823477529.zip` with the `digest` field of
`https://api.github.com/repos/xuanhuyle/solar/actions/artifacts/11145568607` (until the artifact expires) and with
`artifact_api.json`. Nothing on this branch is ever overwritten.
