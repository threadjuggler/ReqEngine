"""Document ORM model — stores TipTap document content per project."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

_EMPTY_DOC: dict = {"type": "doc", "content": []}


class Document(Base):
    """One editable document per project; content stored as TipTap JSON in JSONB."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    project_id_number: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_edit_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    last_change_by: Mapped[str] = mapped_column(String(100), nullable=False)
    document_content: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=lambda: {"type": "doc", "content": []}
    )
