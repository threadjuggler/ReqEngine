"""FastAPI router for /api/requirements endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user
from app.models.link import Link
from app.models.requirement import Requirement
from app.models.testcase import Testcase
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
    """Return full requirement detail including the computed polymorphic list_of_links."""
    result = await session.execute(select(Requirement).where(Requirement.id == req_id))
    req = result.scalar_one_or_none()
    if req is None:
        raise HTTPException(status_code=404, detail="Requirement not found.")

    # All links that touch this requirement on either side
    link_rows = await session.execute(
        select(Link).where(
            or_(
                and_(Link.link_start_kind == "requirement", Link.link_start == req_id),
                and_(
                    Link.link_destination_kind == "requirement",
                    Link.link_destination == req_id,
                ),
            )
        )
    )
    all_links = list(link_rows.scalars().all())

    # Collect every endpoint referenced (both start AND destination of every link),
    # then batch-resolve project_ids and titles in two queries.
    needed_req_ids: set[int] = set()
    needed_tc_ids: set[int] = set()
    for lnk in all_links:
        for kind, oid in (
            (lnk.link_start_kind, lnk.link_start),
            (lnk.link_destination_kind, lnk.link_destination),
        ):
            if kind == "requirement":
                needed_req_ids.add(oid)
            elif kind == "testcase":
                needed_tc_ids.add(oid)

    req_map: dict[int, Requirement] = {}
    if needed_req_ids:
        r = await session.execute(select(Requirement).where(Requirement.id.in_(needed_req_ids)))
        req_map = {x.id: x for x in r.scalars().all()}
    tc_map: dict[int, Testcase] = {}
    if needed_tc_ids:
        t = await session.execute(select(Testcase).where(Testcase.id.in_(needed_tc_ids)))
        tc_map = {x.id: x for x in t.scalars().all()}

    def lookup(kind: str, oid: int) -> Requirement | Testcase | None:
        """Return the ORM object for (kind, id) using the prefetched maps."""
        return req_map.get(oid) if kind == "requirement" else tc_map.get(oid)

    links: list[LinkItemOut] = []
    for lnk in all_links:
        start_obj = lookup(lnk.link_start_kind, lnk.link_start)
        dest_obj = lookup(lnk.link_destination_kind, lnk.link_destination)
        if start_obj is None or dest_obj is None:
            # Dangling link (an endpoint was deleted) — skip
            continue
        if lnk.link_start_kind == "requirement" and lnk.link_start == req_id:
            other_kind, other_obj = lnk.link_destination_kind, dest_obj
        else:
            other_kind, other_obj = lnk.link_start_kind, start_obj
        links.append(
            LinkItemOut(
                link_id=lnk.id,
                link_type=lnk.link_type,
                start_project_id=start_obj.project_id,
                destination_project_id=dest_obj.project_id,
                other_side=LinkSideOut(
                    kind=other_kind,
                    id=other_obj.id,
                    project_id=other_obj.project_id,
                    title=other_obj.title,
                ),
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

    # No more FK cascade — links are polymorphic, so app-level delete by (kind, id) match
    await session.execute(
        delete(Link).where(
            or_(
                and_(Link.link_start_kind == "requirement", Link.link_start == req_id),
                and_(
                    Link.link_destination_kind == "requirement",
                    Link.link_destination == req_id,
                ),
            )
        )
    )
    await session.delete(req)
    await session.commit()
