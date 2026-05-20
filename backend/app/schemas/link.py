"""Pydantic schemas for Link create and read."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, field_validator

from app.sanitize import sanitize_text


class LinkType(StrEnum):
    """Allowed link type values."""

    refines = "refines"
    depends_on = "depends_on"
    tested_by = "tested_by"


class LinkCreate(BaseModel):
    """Schema for creating a new link between two requirements using human project_ids."""

    link_type: LinkType
    link_start_project_id: str
    link_destination_project_id: str

    @field_validator("link_start_project_id", "link_destination_project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Sanitize project_id inputs: strip HTML, enforce max 100 chars."""
        return sanitize_text(v, 100)


class LinkOut(BaseModel):
    """Full link representation returned by the API."""

    id: int
    project_id: str
    link_type: str
    link_start_kind: str
    link_start: int
    link_destination_kind: str
    link_destination: int
    created_on: datetime
    last_edited_on: datetime

    model_config = {"from_attributes": True}
