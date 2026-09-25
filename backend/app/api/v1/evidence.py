"""
LexMatter AI — Evidence Intelligence & Gap Analysis API Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.models.analysis import EvidenceGap, EvidenceMapping
from backend.app.models.source import DocumentVersion, Page, SourceSpan
from backend.app.models.extraction import SourceAssertion
from backend.app.schemas.analysis import EvidenceGapSchema, EvidenceMappingSchema
from backend.app.services.evidence_service import evidence_service

router = APIRouter(tags=["Evidence Intelligence"])


@router.post("/matters/{matter_id}/evidence/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_evidence(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Evaluate matter evidence against legal requirements and generate evidence gaps."""
    try:
        metrics = await evidence_service.evaluate_matter_evidence(db, matter_id)
        return {
            "matter_id": matter_id,
            "status": "COMPLETED",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence evaluation failed: {str(e)}",
        )


from sqlalchemy import select, func, delete
from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan


@router.get("/matters/{matter_id}/evidence", response_model=List[EvidenceMappingSchema])
async def list_evidence_mappings(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all evidence mappings for a matter with resolved source_span_id and document_id citations."""
    try:
        doc_count_stmt = select(func.count(Document.id)).where(Document.matter_id == matter_id)
        doc_count_res = await db.execute(doc_count_stmt)
        searched_docs = doc_count_res.scalar() or 0

        if searched_docs == 0:
            await db.execute(delete(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id))
            await db.commit()
            return []

        stmt = (
            select(
                EvidenceMapping,
                SourceAssertion.source_span_id,
                DocumentVersion.document_id,
            )
            .join(SourceAssertion, EvidenceMapping.source_assertion_id == SourceAssertion.id)
            .outerjoin(SourceSpan, SourceAssertion.source_span_id == SourceSpan.id)
            .outerjoin(Page, SourceSpan.page_id == Page.id)
            .outerjoin(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .where(EvidenceMapping.matter_id == matter_id)
            .order_by(EvidenceMapping.created_at.desc())
        )
        res = await db.execute(stmt)
        rows = res.all()

        output = []
        for mapping, span_id, doc_id in rows:
            output.append(EvidenceMappingSchema(
                id=mapping.id,
                matter_id=mapping.matter_id,
                source_assertion_id=mapping.source_assertion_id,
                source_span_id=span_id,
                document_id=doc_id,
                requirement_version_id=mapping.requirement_version_id,
                relationship=mapping.relationship,
                target_dimension=mapping.target_dimension,
                relevance_score=mapping.relevance_score,
                analysis_notes=mapping.analysis_notes,
                created_at=mapping.created_at,
            ))
        return output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch evidence mappings: {str(e)}",
        )


@router.get("/matters/{matter_id}/gaps", response_model=List[EvidenceGapSchema])
async def list_evidence_gaps(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all detected evidence gaps for a matter."""
    try:
        doc_count_stmt = select(func.count(Document.id)).where(Document.matter_id == matter_id)
        doc_count_res = await db.execute(doc_count_stmt)
        searched_docs = doc_count_res.scalar() or 0

        if searched_docs == 0:
            await db.execute(delete(EvidenceGap).where(EvidenceGap.matter_id == matter_id))
            await db.commit()
            return []

        stmt = select(EvidenceGap).where(EvidenceGap.matter_id == matter_id).order_by(EvidenceGap.created_at.desc())
        res = await db.execute(stmt)
        return res.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch evidence gaps: {str(e)}",
        )
