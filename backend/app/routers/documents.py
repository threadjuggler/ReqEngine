"""FastAPI router for /api/documents endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.document import Document
from app.models.project import Project
from app.schemas.document import DocumentCreate, DocumentOut, DocumentUpdate
from app.services.counter import format_project_id, reserve_project_number

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=201)
async def create_document(
    body: DocumentCreate,
    session: AsyncSession = Depends(get_session),
) -> DocumentOut:
    """Create a blank document for the given project, allocating a project_id from the counter."""
    proj_result = await session.execute(
        select(Project).where(Project.id == body.project_id_number)
    )
    project = proj_result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    number = await reserve_project_number(session, project.project_name)
    now = datetime.now(tz=UTC)
    doc = Document(
        project_id=format_project_id(project.project_name, number),
        project_id_number=body.project_id_number,
        author="User1",
        last_change_by="User1",
        document_content={"type": "doc", "content": []},
        created_on=now,
        last_edit_on=now,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
) -> DocumentOut:
    """Return full document including document_content. 404 if not found."""
    result = await session.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentOut.model_validate(doc)


@router.put("/{doc_id}", response_model=DocumentOut)
async def update_document(
    doc_id: int,
    body: DocumentUpdate,
    session: AsyncSession = Depends(get_session),
) -> DocumentOut:
    """Save updated document content; updates last_change_by and last_edit_on."""
    result = await session.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    doc.document_content = body.document_content
    doc.last_change_by = "User1"
    doc.last_edit_on = datetime.now(tz=UTC)
    await session.commit()
    await session.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a document by its primary key id."""
    result = await session.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    await session.delete(doc)
    await session.commit()
