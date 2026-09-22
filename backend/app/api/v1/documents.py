"""
LexMatter AI — Document Upload & Ingestion API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents (.pdf) are supported in V1.",
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
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}",
        )
