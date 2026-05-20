"""Pydantic schemas for Requirement create, update, and read."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, field_validator

from app.sanitize import sanitize_text


class RequirementStatus(StrEnum):
    """Allowed status values for a requirement."""

    draft = "draft"
    in_review = "in_review"
    wait_for_approval = "wait_for_approval"
    approved = "approved"
    expired = "expired"


class RequirementType(StrEnum):
    """Allowed requirement type values."""

    customer = "customer_requirement"
    system = "system_requirement"
    software = "software_requirement"
    hardware = "hardware_requirement"


class RequirementCreate(BaseModel):
    """Schema for creating a new requirement using a pre-reserved requirement_number."""

    requirement_number: int
    project_id: str
    project_id_number: int
    title: str
    description: str = ""
    status: RequirementStatus = RequirementStatus.draft
    requirement_type: RequirementType
    revision: str = "0.1"

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Sanitize title: strip HTML, enforce max 200 chars."""
        return sanitize_text(v, 200)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Sanitize description: strip HTML, enforce max 500 chars."""
        return sanitize_text(v, 500)

    @field_validator("revision")
    @classmethod
    def validate_revision(cls, v: str) -> str:
        """Sanitize revision: strip HTML, enforce max 30 chars."""
        return sanitize_text(v, 30)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Sanitize project_id: strip HTML, enforce max 100 chars."""
        return sanitize_text(v, 100)


class RequirementUpdate(BaseModel):
    """Schema for updating mutable fields of an existing requirement."""

    title: str
    description: str = ""
    status: RequirementStatus
    requirement_type: RequirementType
    revision: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Sanitize title: strip HTML, enforce max 200 chars."""
        return sanitize_text(v, 200)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Sanitize description: strip HTML, enforce max 500 chars."""
        return sanitize_text(v, 500)

    @field_validator("revision")
    @classmethod
    def validate_revision(cls, v: str) -> str:
        """Sanitize revision: strip HTML, enforce max 30 chars."""
        return sanitize_text(v, 30)


class LinkSideOut(BaseModel):
    """Compact representation of one side of a link — may be a requirement or a testcase."""

    kind: str
    id: int
    project_id: str
    title: str

    model_config = {"from_attributes": True}


class LinkItemOut(BaseModel):
    """One entry in the list_of_links on a requirement detail response."""

    link_id: int
    link_type: str
    start_project_id: str
    destination_project_id: str
    other_side: LinkSideOut


class RequirementSummaryOut(BaseModel):
    """List-view projection of a requirement."""

    id: int
    project_id: str
    project_id_number: int
    title: str
    status: str
    requirement_type: str
    last_edited_on: datetime

    model_config = {"from_attributes": True}


class RequirementDetailOut(BaseModel):
    """Full requirement detail including resolved list_of_links."""

    id: int
    requirement_number: int
    project_id: str
    project_id_number: int
    title: str
    description: str
    status: str
    requirement_type: str
    author: str
    last_edited_by: str
    created_on: datetime
    last_edited_on: datetime
    revision: str
    list_of_links: list[LinkItemOut] = []

    model_config = {"from_attributes": True}


class ReserveIdOut(BaseModel):
    """Response for reserve-id endpoint."""

    requirement_number: int
    project_id: str
