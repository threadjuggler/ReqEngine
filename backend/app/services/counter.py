"""Atomic project counter reservation service shared by all object types."""

from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_counter import ProjectCounter


def format_project_id(project_name: str, number: int) -> str:
    """Format a project_id like 'Project1_00000007' from a project name and counter."""
    return f"{project_name}_{number:08d}"


async def reserve_project_number(session: AsyncSession, project_name: str) -> int:
    """Atomically increment next_number for project_name and return the reserved value.

    If no counter row exists for project_name, creates one (starting at 1) via
    INSERT ... ON CONFLICT DO NOTHING, then retries the UPDATE. Uses a single
    UPDATE ... RETURNING to avoid race conditions under concurrent requests.
    """
    stmt = (
        update(ProjectCounter)
        .where(ProjectCounter.project_name == project_name)
        .values(next_number=ProjectCounter.next_number + 1)
        .returning(ProjectCounter.next_number)
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        # Auto-create counter row then retry
        await session.execute(
            text(
                "INSERT INTO project_counters (project_name, next_number) "
                "VALUES (:name, 1) ON CONFLICT DO NOTHING"
            ),
            {"name": project_name},
        )
        result2 = await session.execute(stmt)
        row = result2.scalar_one_or_none()
        if row is None:
            raise LookupError(f"Could not create or find counter for project '{project_name}'.")
    await session.commit()
    return row - 1
