"""Project ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Project(Base):
    """Stores a project with its name, user list, and creation timestamp.

    document_ids is derived by querying Document; not stored here.
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    user_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=lambda: [10, 20])
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
