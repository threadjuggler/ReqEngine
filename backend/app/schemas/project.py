"""Pydantic schemas for Project create and read."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.sanitize import sanitize_text


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    project_name: str

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Sanitize project_name: strip HTML, enforce max 120 chars."""
        return sanitize_text(v, 120)


class ProjectListOut(BaseModel):
    """Project representation for the list endpoint (includes computed document_count)."""

    id: int
    project_name: str
    user_ids: list[int]
    document_count: int

    model_config = {"from_attributes": True}


class ProjectDetailOut(BaseModel):
    """Full project detail including derived document_ids list."""

    id: int
    project_name: str
    user_ids: list[int]
    created_on: datetime
    document_ids: list[int]
    document_count: int

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    """Minimal project representation returned on create."""

    id: int
    project_name: str
    user_ids: list[int]
    created_on: datetime

    model_config = {"from_attributes": True}
