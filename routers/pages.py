"""HTML page routes — login screen, admin user management, user dashboard.

All authentication state lives in the session cookie set by SessionMiddleware.
"""

import hashlib
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _session_user(request: Request, db: Session) -> Optional[User]:
    uid = request.session.get("user_id")
    if not uid:
        return None
    return db.query(User).filter(User.id == uid).first()


def _require_admin(request: Request, db: Session) -> User:
    user = _session_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="not logged in")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = _session_user(request, db)
    if user is None:
        return templates.TemplateResponse(request, "login.html", {"error": None})
    target = "/admin" if user.role == "admin" else "/dashboard"
    return RedirectResponse(url=target, status_code=303)


@router.post("/login")
async def login_submit(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(User).filter(User.name == name).first()
    if not user or user.hashed_password != hashed:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or password"},
            status_code=401,
        )
    user.log_in_active = 1
    user.last_log_in = datetime.now()
    db.commit()
    request.session["user_id"] = user.id
    request.session["name"] = user.name
    request.session["role"] = user.role
    target = "/admin" if user.role == "admin" else "/dashboard"
    return RedirectResponse(url=target, status_code=303)


@router.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if uid:
        user = db.query(User).filter(User.id == uid).first()
        if user:
            user.log_in_active = 0
            db.commit()
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _session_user(request, db)
    if user is None:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request, "dashboard.html", {"current_user": user}
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    user = _session_user(request, db)
    if user is None:
        return RedirectResponse(url="/", status_code=303)
    if user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=303)
    users = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse(
        request,
        "admin.html",
        {"current_user": user, "users": users, "error": None},
    )


@router.post("/admin/users")
async def admin_create_user(
    request: Request,
    name: str = Form(...),
    role: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    current = _require_admin(request, db)
    if db.query(User).filter(User.name == name).first():
        users = db.query(User).order_by(User.id).all()
        return templates.TemplateResponse(
            request,
            "admin.html",
            {
                "current_user": current,
                "users": users,
                "error": f"User '{name}' already exists",
            },
            status_code=400,
        )
    db.add(
        User(
            name=name,
            role=role,
            email=email,
            hashed_password=hashlib.sha256(password.encode()).hexdigest(),
            log_in_active=0,
        )
    )
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/admin/users/{user_id}/delete")
async def admin_delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current = _require_admin(request, db)
    if current.id == user_id:
        users = db.query(User).order_by(User.id).all()
        return templates.TemplateResponse(
            request,
            "admin.html",
            {
                "current_user": current,
                "users": users,
                "error": "You cannot delete your own account",
            },
            status_code=400,
        )
    target = db.query(User).filter(User.id == user_id).first()
    if target:
        db.delete(target)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)
