"""Pydantic schemas for Document create, update, and read."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.sanitize import sanitize_document_content


class DocumentCreate(BaseModel):
    """Schema for creating a new blank document within a project."""

    project_id_number: int


class DocumentUpdate(BaseModel):
    """Schema for saving updated document content."""

    document_content: dict

    @field_validator("document_content")
    @classmethod
    def validate_content(cls, v: dict) -> dict:
        """Run the document content sanitizer; raises ValueError on invalid structure."""
        return sanitize_document_content(v)


class DocumentSummaryOut(BaseModel):
    """Summary document representation for project document list endpoint."""

    id: int
    project_id: str
    author: str
    last_change_by: str
    last_edit_on: datetime
    created_on: datetime

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    """Full document representation including document_content."""

    id: int
    project_id: str
    project_id_number: int
    author: str
    last_change_by: str
    created_on: datetime
    last_edit_on: datetime
    document_content: dict

    model_config = {"from_attributes": True}
