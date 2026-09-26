"""The forward vault (milestone M5). Until it is built, it opens nothing."""

from __future__ import annotations


def access_is_valid(access) -> bool:
    """No forward access is valid before the vault exists."""
    return False
