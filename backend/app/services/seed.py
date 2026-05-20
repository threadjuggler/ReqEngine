"""Idempotent seed: ensures ProjectCounter('Project1') row and three test cases exist."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_counter import ProjectCounter
from app.models.testcase import Testcase
from app.services.counter import format_project_id, reserve_project_number

PROJECT_NAME = "Project1"

_SEED_TESTCASES = [
    {
        "title": "Lorem ipsum basic flow",
        "description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Verifica quod systema ad statum initialem revertatur post executionem."
        ),
        "test_state": "draft",
    },
    {
        "title": "Consectetur adipiscing validation",
        "description": (
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Probare quod inputs invalidi recusantur cum errore appropriato."
        ),
        "test_state": "draft",
    },
    {
        "title": "Ut labore et dolore boundary check",
        "description": (
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. "
            "Confirmare quod limites systematis recte tractantur in omnibus casibus."
        ),
        "test_state": "approved",
    },
]


async def run_seed(session: AsyncSession) -> None:
    """Insert ProjectCounter and three test cases if they are missing."""
    await _seed_counter(session)
    await session.commit()
    await _seed_testcases(session)


async def _seed_counter(session: AsyncSession) -> None:
    """Insert the ProjectCounter row for Project1 if missing."""
    result = await session.execute(
        select(ProjectCounter).where(ProjectCounter.project_name == PROJECT_NAME)
    )
    if result.scalar_one_or_none() is None:
        session.add(ProjectCounter(project_name=PROJECT_NAME, next_number=1))


async def _seed_testcases(session: AsyncSession) -> None:
    """Insert any missing seed testcases, reserving a project_id for each from the counter."""
    now = datetime.now(tz=UTC)
    for tc_data in _SEED_TESTCASES:
        existing = await session.execute(
            select(Testcase).where(Testcase.title == tc_data["title"])
        )
        if existing.scalar_one_or_none() is not None:
            continue
        number = await reserve_project_number(session, PROJECT_NAME)
        session.add(
            Testcase(
                project_id=format_project_id(PROJECT_NAME, number),
                title=tc_data["title"],
                description=tc_data["description"],
                test_state=tc_data["test_state"],
                author="User1",
                last_edited_by="User1",
                revision="0.1",
                created_on=now,
                last_edited_on=now,
            )
        )
        await session.commit()
