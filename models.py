from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    role = Column(String(20), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    log_in_active = Column(Integer, default=0)
    last_log_in = Column(DateTime, nullable=True)


class UserCreate(BaseModel):
    name: str
    role: str
    password: str


class UserLogin(BaseModel):
    name: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    log_in_active: Optional[int] = None
    last_log_in: Optional[datetime] = None


class UserResponse(BaseModel):
    id: int
    name: str
    role: str
    log_in_active: int
    last_log_in: Optional[datetime]

    model_config = {"from_attributes": True}
