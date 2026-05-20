"""FastAPI router for /api/requirements endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user
from app.models.link import Link
from app.models.requirement import Requirement
from app.schemas.requirement import (
    LinkItemOut,
    LinkSideOut,
    RequirementCreate,
    RequirementDetailOut,
    RequirementSummaryOut,
    RequirementUpdate,
    ReserveIdOut,
)
from app.services.counter import format_project_id, reserve_project_number

router = APIRouter(prefix="/api/requirements", tags=["requirements"])

PROJECT_NAME = "Project1"


@router.post("/reserve-id", response_model=ReserveIdOut)
async def reserve_id(session: AsyncSession = Depends(get_session)) -> ReserveIdOut:
    """Atomically reserve a new project number and return the formatted project_id."""
    number = await reserve_project_number(session, PROJECT_NAME)
    project_id = format_project_id(PROJECT_NAME, number)
    return ReserveIdOut(requirement_number=number, project_id=project_id)


@router.get("", response_model=list[RequirementSummaryOut])
async def list_requirements(
    session: AsyncSession = Depends(get_session),
) -> list[RequirementSummaryOut]:
    """Return summary list of all requirements ordered by id."""
    result = await session.execute(select(Requirement).order_by(Requirement.id))
    reqs = result.scalars().all()
    return [RequirementSummaryOut.model_validate(r) for r in reqs]


@router.get("/{req_id}", response_model=RequirementDetailOut)
async def get_requirement(
    req_id: int,
    session: AsyncSession = Depends(get_session),
) -> RequirementDetailOut:
    """Return full requirement detail including the computed list_of_links."""
    result = await session.execute(
        select(Requirement)
        .options(
            selectinload(Requirement.links_as_start).selectinload(Link.destination_requirement),
            selectinload(Requirement.links_as_destination).selectinload(Link.start_requirement),
        )
        .where(Requirement.id == req_id)
    )
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    links: list[LinkItemOut] = []
    for lnk in req.links_as_start:
        other = lnk.destination_requirement
        links.append(
            LinkItemOut(
                link_id=lnk.id,
                link_type=lnk.link_type,
                other_side=LinkSideOut(id=other.id, project_id=other.project_id, title=other.title),
            )
        )
    for lnk in req.links_as_destination:
        other = lnk.start_requirement
        links.append(
            LinkItemOut(
                link_id=lnk.id,
                link_type=lnk.link_type,
                other_side=LinkSideOut(id=other.id, project_id=other.project_id, title=other.title),
            )
        )

    detail = RequirementDetailOut.model_validate(req)
    detail.list_of_links = links
    return detail


@router.post("", response_model=RequirementDetailOut, status_code=201)
async def create_requirement(
    body: RequirementCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
) -> RequirementDetailOut:
    """Create a new requirement using a pre-reserved requirement_number."""
    now = datetime.now(tz=UTC)
    req = Requirement(
        requirement_number=body.requirement_number,
        project_id=body.project_id,
        title=body.title,
        description=body.description,
        status=body.status.value,
        requirement_type=body.requirement_type.value,
        revision=body.revision,
        author=current_user,
        last_edited_by=current_user,
        created_on=now,
        last_edited_on=now,
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)
    detail = RequirementDetailOut.model_validate(req)
    return detail


@router.put("/{req_id}", response_model=RequirementDetailOut)
async def update_requirement(
    req_id: int,
    body: RequirementUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
) -> RequirementDetailOut:
    """Update mutable fields of a requirement; sets last_edited_by and last_edited_on."""
    result = await session.execute(select(Requirement).where(Requirement.id == req_id))
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    req.title = body.title
    req.description = body.description
    req.status = body.status.value
    req.requirement_type = body.requirement_type.value
    req.revision = body.revision
    req.last_edited_by = current_user
    req.last_edited_on = datetime.now(tz=UTC)

    await session.commit()
    await session.refresh(req)
    detail = RequirementDetailOut.model_validate(req)
    return detail


@router.delete("/{req_id}", status_code=204)
async def delete_requirement(
    req_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a requirement and cascade-delete any links referencing it."""
    result = await session.execute(select(Requirement).where(Requirement.id == req_id))
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    # Explicit link deletion (cascade via FK ondelete should handle it, but be explicit)
    await session.execute(
        delete(Link).where((Link.link_start == req_id) | (Link.link_destination == req_id))
    )
    await session.delete(req)
    await session.commit()
