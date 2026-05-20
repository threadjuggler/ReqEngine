"""FastAPI router for /api/links endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.link import Link
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.testcase import Testcase
from app.schemas.link import LinkCreate, LinkOut
from app.services.counter import format_project_id, reserve_project_number

router = APIRouter(prefix="/api/links", tags=["links"])


async def _resolve_project_id(session: AsyncSession, project_id: str) -> tuple[str, int, int]:
    """Resolve a human project_id to (kind, numeric_id, project_id_number).

    Checks requirements then testcases. Raises HTTP 404 if not found.
    Returns ('requirement', id, project_id_number) or ('testcase', id, project_id_number).
    """
    req_result = await session.execute(
        select(Requirement.id, Requirement.project_id_number).where(
            Requirement.project_id == project_id
        )
    )
    row = req_result.one_or_none()
    if row is not None:
        return ("requirement", row[0], row[1])
    tc_result = await session.execute(
        select(Testcase.id, Testcase.project_id_number).where(Testcase.project_id == project_id)
    )
    tc_row = tc_result.one_or_none()
    if tc_row is not None:
        return ("testcase", tc_row[0], tc_row[1])
    raise HTTPException(
        status_code=404, detail=f"No requirement or testcase found with project_id '{project_id}'."
    )


@router.post("", response_model=LinkOut, status_code=201)
async def create_link(
    body: LinkCreate,
    session: AsyncSession = Depends(get_session),
) -> LinkOut:
    """Create a link; validates both endpoints belong to the specified project."""
    proj_result = await session.execute(
        select(Project).where(Project.id == body.project_id_number)
    )
    project = proj_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=422, detail="project_id_number references unknown project.")

    start_kind, start_id, start_pin = await _resolve_project_id(
        session, body.link_start_project_id
    )
    dest_kind, dest_id, dest_pin = await _resolve_project_id(
        session, body.link_destination_project_id
    )

    if start_pin != body.project_id_number or dest_pin != body.project_id_number:
        raise HTTPException(
            status_code=422,
            detail="Both link endpoints must belong to the specified project_id_number.",
        )

    if start_kind == dest_kind and start_id == dest_id:
        raise HTTPException(status_code=422, detail="link_start and link_destination must differ.")

    number = await reserve_project_number(session, project.project_name)
    link = Link(
        project_id=format_project_id(project.project_name, number),
        project_id_number=body.project_id_number,
        link_type=body.link_type.value,
        link_start_kind=start_kind,
        link_start=start_id,
        link_destination_kind=dest_kind,
        link_destination=dest_id,
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return LinkOut.model_validate(link)


@router.put("/{link_id}", response_model=LinkOut)
async def update_link(
    link_id: int,
    body: LinkCreate,
    session: AsyncSession = Depends(get_session),
) -> LinkOut:
    """Re-resolve both project_ids and update the link's type and endpoints."""
    result = await session.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found.")

    start_kind, start_id, start_pin = await _resolve_project_id(
        session, body.link_start_project_id
    )
    dest_kind, dest_id, dest_pin = await _resolve_project_id(
        session, body.link_destination_project_id
    )
    if start_pin != body.project_id_number or dest_pin != body.project_id_number:
        raise HTTPException(
            status_code=422,
            detail="Both link endpoints must belong to the specified project_id_number.",
        )
    if start_kind == dest_kind and start_id == dest_id:
        raise HTTPException(status_code=422, detail="link_start and link_destination must differ.")

    link.link_type = body.link_type.value
    link.link_start_kind = start_kind
    link.link_start = start_id
    link.link_destination_kind = dest_kind
    link.link_destination = dest_id
    link.project_id_number = body.project_id_number
    await session.commit()
    await session.refresh(link)
    return LinkOut.model_validate(link)


@router.delete("/{link_id}", status_code=204)
async def delete_link(
    link_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a link row by its primary key id."""
    result = await session.execute(select(Link).where(Link.id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found.")
    await session.delete(link)
    await session.commit()
