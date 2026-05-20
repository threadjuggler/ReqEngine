"""Idempotent seed: ensures Project rows, counters, and testcases exist for both projects."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_counter import ProjectCounter
from app.models.testcase import Testcase
from app.services.counter import format_project_id, reserve_project_number

_PROJECTS = [
    {"id": 1, "project_name": "Project1"},
    {"id": 2, "project_name": "Project2"},
]

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
    """Insert projects, counters, and testcases for each project if missing."""
    for proj_data in _PROJECTS:
        await _seed_project(session, proj_data["id"], proj_data["project_name"])
    await session.commit()
    for proj_data in _PROJECTS:
        await _seed_testcases(session, proj_data["id"], proj_data["project_name"])


async def _seed_project(session: AsyncSession, project_id: int, project_name: str) -> None:
    """Insert a Project row and its ProjectCounter if they don't already exist."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    if result.scalar_one_or_none() is None:
        session.add(Project(id=project_id, project_name=project_name, user_ids=[10, 20]))

    counter_result = await session.execute(
        select(ProjectCounter).where(ProjectCounter.project_name == project_name)
    )
    if counter_result.scalar_one_or_none() is None:
        session.add(ProjectCounter(project_name=project_name, next_number=1))


async def _seed_testcases(
    session: AsyncSession, project_id_number: int, project_name: str
) -> None:
    """Insert missing seed testcases for a project, deduping by (project_name, title)."""
    now = datetime.now(tz=UTC)
    for tc_data in _SEED_TESTCASES:
        existing = await session.execute(
            select(Testcase).where(
                Testcase.project_id_number == project_id_number,
                Testcase.title == tc_data["title"],
            )
        )
        if existing.scalar_one_or_none() is not None:
            continue
        number = await reserve_project_number(session, project_name)
        session.add(
            Testcase(
                project_id=format_project_id(project_name, number),
                project_id_number=project_id_number,
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
