"""Atomic project counter reservation service shared by all object types."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_counter import ProjectCounter


def format_project_id(project_name: str, number: int) -> str:
    """Format a project_id like 'Project1_00000007' from a project name and counter."""
    return f"{project_name}_{number:08d}"


async def reserve_project_number(session: AsyncSession, project_name: str) -> int:
    """Atomically increment next_number for project_name and return the reserved value.

    Shared by Requirements, Links, and Testcases so all project_ids draw from one
    sequence. Uses UPDATE ... RETURNING to avoid race conditions under concurrent
    requests. Raises LookupError if no counter row exists for the project_name.
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
        raise LookupError(f"No counter found for project '{project_name}'.")
    await session.commit()
    return row - 1
