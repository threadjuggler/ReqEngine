"""FastAPI router for /api/testcases endpoints (read-only in step 1)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.testcase import Testcase
from app.schemas.testcase import TestcaseOut

router = APIRouter(prefix="/api/testcases", tags=["testcases"])


@router.get("", response_model=list[TestcaseOut])
async def list_testcases(
    project_id_number: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[TestcaseOut]:
    """Return all test cases ordered by id; optionally filter by project_id_number."""
    stmt = select(Testcase).order_by(Testcase.id)
    if project_id_number is not None:
        stmt = stmt.where(Testcase.project_id_number == project_id_number)
    result = await session.execute(stmt)
    testcases = result.scalars().all()
    return [TestcaseOut.model_validate(tc) for tc in testcases]
