"""Entry point for the ReqEngine API. Registers all routers and middleware."""

import hashlib
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from database import SessionLocal
from models import User
from routers import auth, pages, startx

SESSION_MAX_AGE_SECONDS = 4 * 60 * 60

ADMIN_NAME = "admin"
ADMIN_PASSWORD = "Admin128!"
ADMIN_EMAIL = "admin@reqengine.local"


def _ensure_admin_user() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.name == ADMIN_NAME).first():
            return
        db.add(
            User(
                name=ADMIN_NAME,
                role="admin",
                email=ADMIN_EMAIL,
                hashed_password=hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
                log_in_active=0,
            )
        )
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _ensure_admin_user()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY") or secrets.token_urlsafe(32),
    max_age=SESSION_MAX_AGE_SECONDS,
    same_site="lax",
    https_only=False,
)

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(startx.router)
