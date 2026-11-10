"""Mounts the UNCF squad's API, which lives in the repo's top-level api/ folder (AGENTS.md)."""

from fastapi import APIRouter


def uncf_router() -> APIRouter:
    """The UNCF Explorer's router (api/route.py), from the repo's pdp-student-success package."""
    from api.route import router

    return router
