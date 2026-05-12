"""SQLAlchemy ORM models and Pydantic schemas for the users domain."""

from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import Base


class User(Base):
    """ORM mapping for the `users` table in MariaDB."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    role = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    log_in_active = Column(Integer, default=0)
    last_log_in = Column(DateTime, nullable=True)


class UserCreate(BaseModel):
    """Request body for creating a new user."""

    name: str
    role: str
    email: str
    password: str


class UserLogin(BaseModel):
    """Request body for authenticating a user."""

    name: str
    password: str


class UserUpdate(BaseModel):
    """Request body for partially updating a user — all fields are optional."""

    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    log_in_active: Optional[int] = None
    last_log_in: Optional[datetime] = None


class UserResponse(BaseModel):
    """Response schema for user data — hashed_password is intentionally excluded."""

    id: int
    name: str
    role: str
    email: str
    log_in_active: int
    last_log_in: Optional[datetime]

    model_config = {"from_attributes": True}
