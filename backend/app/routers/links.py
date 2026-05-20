"""FastAPI router for /api/links endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.link import Link
from app.models.requirement import Requirement
from app.models.testcase import Testcase
from app.schemas.link import LinkCreate, LinkOut
from app.services.counter import format_project_id, reserve_project_number

router = APIRouter(prefix="/api/links", tags=["links"])

PROJECT_NAME = "Project1"


async def _resolve_project_id(session: AsyncSession, project_id: str) -> tuple[str, int]:
    """Resolve a human project_id to (kind, numeric_id) by checking requirements then testcases.

    Raises HTTP 404 if the project_id matches no row in either table.
    Returns ('requirement', id) or ('testcase', id).
    """
    req_result = await session.execute(
        select(Requirement.id).where(Requirement.project_id == project_id)
    )
    req_id = req_result.scalar_one_or_none()
    if req_id is not None:
        return ("requirement", req_id)
    tc_result = await session.execute(
        select(Testcase.id).where(Testcase.project_id == project_id)
    )
    tc_id = tc_result.scalar_one_or_none()
    if tc_id is not None:
        return ("testcase", tc_id)
    raise HTTPException(
        status_code=404, detail=f"No requirement or testcase found with project_id '{project_id}'."
    )


@router.post("", response_model=LinkOut, status_code=201)
async def create_link(
    body: LinkCreate,
    session: AsyncSession = Depends(get_session),
) -> LinkOut:
    """Resolve human project_ids (requirement OR testcase) and insert a new link row."""
    start_kind, start_id = await _resolve_project_id(session, body.link_start_project_id)
    dest_kind, dest_id = await _resolve_project_id(session, body.link_destination_project_id)

    if start_kind == dest_kind and start_id == dest_id:
        raise HTTPException(status_code=422, detail="link_start and link_destination must differ.")

    number = await reserve_project_number(session, PROJECT_NAME)
    link = Link(
        project_id=format_project_id(PROJECT_NAME, number),
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

    start_kind, start_id = await _resolve_project_id(session, body.link_start_project_id)
    dest_kind, dest_id = await _resolve_project_id(session, body.link_destination_project_id)
    if start_kind == dest_kind and start_id == dest_id:
        raise HTTPException(status_code=422, detail="link_start and link_destination must differ.")

    link.link_type = body.link_type.value
    link.link_start_kind = start_kind
    link.link_start = start_id
    link.link_destination_kind = dest_kind
    link.link_destination = dest_id
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
