import os
import uuid

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select

from app.config import settings
from app.models.database import async_session
from app.models.document import Document
from app.models.schemas import DocumentResponse
from app.services.document_parser import extract_text, is_supported, normalize_content_type

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content_type = normalize_content_type(file.content_type or "", file.filename)
    if not is_supported(content_type, file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: PDF, TXT, MD",
        )

    doc_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1] or ".txt"
    file_path = os.path.join(settings.upload_dir, f"{doc_id}{ext}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    extracted_text = extract_text(file_path, content_type)
    if not extracted_text.strip():
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Could not extract text from document")

    doc = Document(
        id=doc_id,
        filename=file.filename,
        content_type=content_type,
        extracted_text=extracted_text,
        file_path=file_path,
    )

    async with async_session() as session:
        session.add(doc)
        await session.commit()

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        text_preview=extracted_text[:500],
        created_at=doc.created_at,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents():
    async with async_session() as session:
        result = await session.execute(select(Document).order_by(Document.created_at.desc()))
        docs = result.scalars().all()
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            content_type=d.content_type,
            text_preview=d.extracted_text[:500],
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    async with async_session() as session:
        result = await session.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        await session.delete(doc)
        await session.commit()
    return {"status": "deleted"}
