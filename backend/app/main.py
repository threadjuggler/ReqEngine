"""FastAPI application factory with CORS, lifespan, and router registration."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import AsyncSessionLocal
from app.routers import links, requirements, testcases
from app.services.seed import run_seed


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Run seed on startup; clean up on shutdown."""
    async with AsyncSessionLocal() as session:
        await run_seed(session)
    yield


app = FastAPI(
    title="ReqEngine API",
    version="0.1.0",
    description="Requirements management backend",
    lifespan=lifespan,
)

_cors_origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router)
app.include_router(links.router)
app.include_router(testcases.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health-check endpoint — returns status ok."""
    return {"status": "ok"}
