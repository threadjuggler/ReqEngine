"""FastAPI router for /api/testcases endpoints (read-only in step 1)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.testcase import Testcase
from app.schemas.testcase import TestcaseOut

router = APIRouter(prefix="/api/testcases", tags=["testcases"])


@router.get("", response_model=list[TestcaseOut])
async def list_testcases(
    session: AsyncSession = Depends(get_session),
) -> list[TestcaseOut]:
    """Return all test cases ordered by id (read-only for step 1)."""
    result = await session.execute(select(Testcase).order_by(Testcase.id))
    testcases = result.scalars().all()
    return [TestcaseOut.model_validate(tc) for tc in testcases]
