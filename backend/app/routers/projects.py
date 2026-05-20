"""FastAPI router for /api/projects endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.document import Document
from app.models.project import Project
from app.schemas.document import DocumentSummaryOut
from app.schemas.project import ProjectCreate, ProjectDetailOut, ProjectListOut, ProjectOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> ProjectOut:
    """Create a project and initialize its ProjectCounter row at next_number=1."""
    existing = await session.execute(
        select(Project).where(Project.project_name == body.project_name)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Project name already exists.")
    project = Project(project_name=body.project_name, user_ids=[10, 20])
    session.add(project)
    await session.flush()  # populate project.id
    await session.execute(
        text(
            "INSERT INTO project_counters (project_name, next_number) "
            "VALUES (:name, 1) ON CONFLICT DO NOTHING"
        ),
        {"name": body.project_name},
    )
    await session.commit()
    await session.refresh(project)
    return ProjectOut.model_validate(project)


@router.get("", response_model=list[ProjectListOut])
async def list_projects(
    session: AsyncSession = Depends(get_session),
) -> list[ProjectListOut]:
    """Return all projects with a derived document_count."""
    result = await session.execute(select(Project).order_by(Project.id))
    projects = result.scalars().all()
    out = []
    for proj in projects:
        count_result = await session.execute(
            select(func.count()).where(Document.project_id_number == proj.id)
        )
        doc_count = count_result.scalar_one()
        out.append(
            ProjectListOut(
                id=proj.id,
                project_name=proj.project_name,
                user_ids=proj.user_ids,
                document_count=doc_count,
            )
        )
    return out


@router.get("/{project_id}", response_model=ProjectDetailOut)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_session),
) -> ProjectDetailOut:
    """Return full project detail including derived document_ids list."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    docs_result = await session.execute(
        select(Document.id).where(Document.project_id_number == project_id).order_by(Document.id)
    )
    doc_ids = list(docs_result.scalars().all())
    return ProjectDetailOut(
        id=project.id,
        project_name=project.project_name,
        user_ids=project.user_ids,
        created_on=project.created_on,
        document_ids=doc_ids,
        document_count=len(doc_ids),
    )


@router.get("/{project_id}/documents", response_model=list[DocumentSummaryOut])
async def list_project_documents(
    project_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[DocumentSummaryOut]:
    """Return summary list of all documents for the given project."""
    proj_result = await session.execute(select(Project).where(Project.id == project_id))
    if proj_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    docs_result = await session.execute(
        select(Document)
        .where(Document.project_id_number == project_id)
        .order_by(Document.id)
    )
    docs = docs_result.scalars().all()
    return [DocumentSummaryOut.model_validate(d) for d in docs]
