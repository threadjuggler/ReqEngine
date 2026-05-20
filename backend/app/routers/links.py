"""FastAPI router for /api/links endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.link import Link
from app.models.requirement import Requirement
from app.schemas.link import LinkCreate, LinkOut
from app.services.counter import format_project_id, reserve_project_number

router = APIRouter(prefix="/api/links", tags=["links"])

PROJECT_NAME = "Project1"


@router.post("", response_model=LinkOut, status_code=201)
async def create_link(
    body: LinkCreate,
    session: AsyncSession = Depends(get_session),
) -> LinkOut:
    """Resolve human project_ids to numeric ids, allocate the link's project_id, insert."""
    start_result = await session.execute(
        select(Requirement).where(Requirement.project_id == body.link_start_project_id)
    )
    start_req = start_result.scalar_one_or_none()
    if start_req is None:
        raise HTTPException(
            status_code=404, detail=f"Requirement '{body.link_start_project_id}' not found."
        )

    dest_result = await session.execute(
        select(Requirement).where(Requirement.project_id == body.link_destination_project_id)
    )
    dest_req = dest_result.scalar_one_or_none()
    if dest_req is None:
        raise HTTPException(
            status_code=404, detail=f"Requirement '{body.link_destination_project_id}' not found."
        )

    if start_req.id == dest_req.id:
        raise HTTPException(status_code=422, detail="link_start and link_destination must differ.")

    number = await reserve_project_number(session, PROJECT_NAME)
    link = Link(
        project_id=format_project_id(PROJECT_NAME, number),
        link_type=body.link_type.value,
        link_start=start_req.id,
        link_destination=dest_req.id,
    )
    session.add(link)
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
