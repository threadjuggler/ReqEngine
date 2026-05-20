"""ProjectCounter model: tracks next requirement number per project."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ProjectCounter(Base):
    """One row per project; next_number is atomically incremented on reserve."""

    __tablename__ = "project_counters"

    project_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    next_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
