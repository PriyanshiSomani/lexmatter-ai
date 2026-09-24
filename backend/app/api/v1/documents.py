"""
LexMatter AI — Document Upload & Ingestion API Endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan
from backend.app.services.ingestion_service import ingestion_service

router = APIRouter(prefix="/matters/{matter_id}/documents", tags=["Documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    matter_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and deterministically ingest a legal document into a matter.
    
    Processes PDF pages, runs OCR fallback if scanned, extracts character-level SourceSpans,
    computes SHA-256 hashes, classifies the document type, and persists all records.
    """
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF (.pdf) and Text (.txt) documents are supported in V1.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file payload is empty.",
        )

    try:
        result = await ingestion_service.ingest_document(
            db=db,
            matter_id=matter_id,
            file_name=file.filename,
            file_bytes=file_bytes,
        )
        return {
            "id": result["document_id"],
            "matter_id": matter_id,
            "title": file.filename,
            "file_type": file.filename.split(".")[-1].upper() if "." in file.filename else "PDF",
            "document_type": result.get("document_type", "UNKNOWN"),
            "status": result.get("status", "PROCESSED"),
            "chunk_count": result.get("total_spans", 0),
            "created_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}",
        )


@router.get("", status_code=status.HTTP_200_OK)
async def list_matter_documents(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all ingested documents for a given matter."""
    try:
        stmt = (
            select(Document)
            .options(selectinload(Document.versions))
            .where(Document.matter_id == matter_id)
            .order_by(Document.created_at.desc())
        )
        result = await db.execute(stmt)
        docs = result.scalars().all()

        response = []
        for doc in docs:
            response.append({
                "id": doc.id,
                "matter_id": doc.matter_id,
                "title": doc.title,
                "file_type": doc.title.split(".")[-1].upper() if "." in doc.title else "PDF",
                "document_type": doc.document_type,
                "status": doc.status,
                "chunk_count": doc.versions[0].page_count if doc.versions else 0,
                "created_at": doc.created_at.isoformat() if doc.created_at else "",
            })
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch matter documents: {str(e)}",
        )


@router.get("/{document_id}/spans", status_code=status.HTTP_200_OK)
async def get_document_source_spans(
    matter_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch extracted character-level SourceSpans and text snippets for a document."""
    try:
        stmt = (
            select(SourceSpan)
            .options(selectinload(SourceSpan.page))
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .where(DocumentVersion.document_id == document_id)
            .order_by(Page.page_number, SourceSpan.start_char)
        )
        result = await db.execute(stmt)
        spans = result.scalars().all()

        response = []
        for span in spans:
            response.append({
                "id": span.id,
                "page_id": span.page_id,
                "page_number": span.page.page_number if span.page else 1,
                "start_char": span.start_char,
                "end_char": span.end_char,
                "text_snippet": span.text_snippet,
                "text_hash": span.text_hash,
            })
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch document source spans: {str(e)}",
        )
