"""Link ORM model — polymorphic, can connect requirements and/or testcases."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Link(Base):
    """Directed link between two objects; each side has (kind, id). Self-link is forbidden."""

    __tablename__ = "links"
    __table_args__ = (
        CheckConstraint(
            "NOT (link_start_kind = link_destination_kind AND link_start = link_destination)",
            name="ck_link_no_self_ref",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    link_type: Mapped[str] = mapped_column(String(60), nullable=False)
    link_start_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    link_start: Mapped[int] = mapped_column(Integer, nullable=False)
    link_destination_kind: Mapped[str] = mapped_column(String(20), nullable=False)
    link_destination: Mapped[int] = mapped_column(Integer, nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_edited_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
