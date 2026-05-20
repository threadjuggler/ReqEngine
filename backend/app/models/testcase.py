"""Testcase ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Testcase(Base):
    """Stores a test case with metadata; linked to requirements via the links table."""

    __tablename__ = "testcases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    test_state: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    last_edited_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_edited_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    revision: Mapped[str] = mapped_column(String(30), nullable=False, default="0.1")
