"""Link ORM model connecting two requirements."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.requirement import Requirement


class Link(Base):
    """Directed link between two requirements; start must differ from destination."""

    __tablename__ = "links"
    __table_args__ = (
        CheckConstraint("link_start <> link_destination", name="ck_link_no_self_ref"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    link_type: Mapped[str] = mapped_column(String(60), nullable=False)
    link_start: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False
    )
    link_destination: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_edited_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    start_requirement: Mapped[Requirement] = relationship(
        "Requirement", foreign_keys=[link_start], back_populates="links_as_start"
    )
    destination_requirement: Mapped[Requirement] = relationship(
        "Requirement", foreign_keys=[link_destination], back_populates="links_as_destination"
    )
