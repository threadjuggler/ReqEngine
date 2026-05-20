"""Requirement ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Requirement(Base):
    """Stores a single requirement with all metadata, linked to a Project row."""

    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requirement_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    project_id_number: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    requirement_type: Mapped[str] = mapped_column(String(80), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    last_edited_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_edited_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    revision: Mapped[str] = mapped_column(String(30), nullable=False, default="0.1")
