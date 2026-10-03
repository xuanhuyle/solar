"""Did the owner approve *this* run for the vault environment? (GitHub REST API, standard library.)

The vault job declares ``environment: engine-vault``, whose required reviewer is
the owner, so GitHub does not start it without that approval. The vault also
checks the approval itself: it reads the run's approval record and requires an
``approved`` review by an allowed login for ``engine-vault``. This module talks
to api.github.com only - never to a data source (the door test allows it).
"""

from __future__ import annotations

import json
import os
import urllib.request

VAULT_ENVIRONMENT = "engine-vault"
APPROVERS = frozenset({"xuanhuyle"})


def approvals(repo: str, run_id: str, token: str) -> list[dict]:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/approvals",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def approved_by(records: list[dict], environment: str = VAULT_ENVIRONMENT, allowed=APPROVERS) -> str | None:
    """The login of an allowed reviewer who approved ``environment`` in these records, else None."""
    for r in records:
        envs = {e.get("name") for e in r.get("environments", [])}
        login = (r.get("user") or {}).get("login")
        if r.get("state") == "approved" and environment in envs and login in allowed:
            return login
    return None


def owner_approval_from_env() -> str | None:
    repo, run_id, token = (os.environ.get(k, "") for k in ("GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_TOKEN"))
    if not (repo and run_id and token):
        return None
    try:
        return approved_by(approvals(repo, run_id, token))
    except Exception:
        return None
