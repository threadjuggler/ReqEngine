"""Startup and health-check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/init")
async def get_all():
    """Health-check endpoint — returns 'ok' when the API is reachable."""
    return "ok"
