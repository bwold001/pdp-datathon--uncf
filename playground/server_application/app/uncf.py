"""Mounts the UNCF squad's API, which lives in the repo's top-level uncf/ folder (AGENTS.md)."""

import logging
import sys

from fastapi import APIRouter

from app.sandbox.chat.repo import RepoNotFound, repo_root

logger = logging.getLogger(__name__)


def uncf_router() -> APIRouter | None:
    """The UNCF Explorer's router, or None when the server is deployed without the repository."""
    try:
        root = str(repo_root())
    except RepoNotFound:
        logger.warning("uncf/ isn't around Playground, so the UNCF Explorer API is off.")
        return None
    # Appended, not put first: an installed package wins over a same-named repo folder (mcp/).
    if root not in sys.path:
        sys.path.append(root)
    from uncf.api_route import router

    return router
