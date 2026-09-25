"""
LexMatter AI — Document Upload, Ingestion & Deletion API Endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan
from backend.app.services.ingestion_service import ingestion_service
from backend.app.services.extraction_service import extraction_service
from backend.app.core.logger import get_logger

logger = get_logger("api.documents")

router = APIRouter(prefix="/matters/{matter_id}/documents", tags=["documents"])


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
        logger.info(f"Ingesting uploaded document '{file.filename}' for Matter '{matter_id}'...")
        result = await ingestion_service.ingest_document(
            db=db,
            matter_id=matter_id,
            file_name=file.filename,
            file_bytes=file_bytes,
        )

        # Auto-trigger assertion & entity extraction for matter spans
        logger.info(f"Auto-extracting SourceAssertions and entities for Matter '{matter_id}'...")
        ext_result = await extraction_service.process_matter_extractions(db, matter_id)
        logger.info(f"Assertion extraction complete for '{file.filename}' (Assertions created: {ext_result.get('assertions_created')}).")
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
        logger.error(f"Document ingestion failed for '{file.filename}' in Matter '{matter_id}': {e}", exc_info=True)
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
        logger.error(f"Failed to fetch matter documents for Matter '{matter_id}': {e}", exc_info=True)
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
        logger.error(f"Failed to fetch source spans for Document '{document_id}' in Matter '{matter_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch document source spans: {str(e)}",
        )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    matter_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific document and all associated version/span/assertion records from the matter."""
    try:
        from backend.app.models.analysis import EvidenceGap, EvidenceMapping, Finding
        from backend.app.models.extraction import SourceAssertion
        from backend.app.models.legal import RequirementApplicability
        from sqlalchemy import func, update

        stmt = select(Document).where(Document.id == document_id, Document.matter_id == matter_id)
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        # 1. Query all SourceSpan IDs belonging to pages in this document
        span_ids_stmt = (
            select(SourceSpan.id)
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .where(DocumentVersion.document_id == document_id)
        )
        span_ids_res = await db.execute(span_ids_stmt)
        target_span_ids = span_ids_res.scalars().all()

        # 2. Query all SourceAssertion IDs referencing these spans
        if target_span_ids:
            asrt_ids_stmt = select(SourceAssertion.id).where(SourceAssertion.source_span_id.in_(target_span_ids))
            asrt_ids_res = await db.execute(asrt_ids_stmt)
            target_asrt_ids = asrt_ids_res.scalars().all()

            if target_asrt_ids:
                # Delete linked EvidenceMappings
                await db.execute(delete(EvidenceMapping).where(EvidenceMapping.source_assertion_id.in_(target_asrt_ids)))
                # Delete linked SourceAssertions
                await db.execute(delete(SourceAssertion).where(SourceAssertion.id.in_(target_asrt_ids)))

        # 3. Delete Document (cascades to DocumentVersions, Pages, SourceSpans)
        await db.delete(doc)
        await db.flush()

        # 4. Re-evaluate matter evidence to sync requirement statuses, mappings, and gaps
        from backend.app.services.evidence_service import evidence_service
        eval_res = await evidence_service.evaluate_matter_evidence(db, matter_id)

        await db.commit()
        return {"status": "DELETED", "document_id": document_id, "remaining_documents": eval_res.get("searched_document_count", 0)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete document '{document_id}' for Matter '{matter_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_matter_documents(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Clear all documents and perform a clean-slate analysis reset for a matter."""
    try:
        from backend.app.models.analysis import EvidenceGap, EvidenceMapping, Finding
        from backend.app.models.knowledge import Conflict
        from backend.app.models.extraction import SourceAssertion
        from backend.app.models.legal import RequirementApplicability
        from sqlalchemy import update

        # 1. Delete all document records
        await db.execute(delete(Document).where(Document.matter_id == matter_id))

        # 2. Delete all analysis & gap records for this matter
        await db.execute(delete(EvidenceGap).where(EvidenceGap.matter_id == matter_id))
        await db.execute(delete(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id))
        await db.execute(delete(Conflict).where(Conflict.matter_id == matter_id))
        await db.execute(delete(Finding).where(Finding.matter_id == matter_id))
        await db.execute(delete(SourceAssertion).where(SourceAssertion.matter_id == matter_id))

        # 3. Reset RequirementApplicability status back to NOT_EVALUATED
        await db.execute(
            update(RequirementApplicability)
            .where(RequirementApplicability.matter_id == matter_id)
            .values(status="NOT_EVALUATED", notes=None)
        )

        await db.commit()
        return {"status": "CLEARED", "matter_id": matter_id}
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to clear matter documents for Matter '{matter_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear matter documents: {str(e)}",
        )
