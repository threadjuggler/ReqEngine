"""Pydantic schemas for Testcase read (read-only in step 1)."""

from datetime import datetime

from pydantic import BaseModel


class TestcaseOut(BaseModel):
    """Full testcase representation returned by the API."""

    id: int
    project_id: str
    title: str
    description: str
    test_state: str
    author: str
    last_edited_by: str
    created_on: datetime
    last_edited_on: datetime
    revision: str

    model_config = {"from_attributes": True}
