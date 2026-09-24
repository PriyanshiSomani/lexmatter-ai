"""
LexMatter AI — Audit & Provenance Verification API Router
Phase 11: Audit & Provenance Verification Engine
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.schemas.audit import LineageGraphResponse, ConfidenceMetricsSchema, ConfidenceCalculationRequest
from backend.app.services.audit_service import audit_service

router = APIRouter(tags=["Audit & Provenance Verification"])


@router.get("/audit/lineage/{entity_id}", response_model=LineageGraphResponse)
async def get_entity_lineage(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the backward provenance DAG lineage graph for any entity ULID down to its root SourceSpan and Document.
    """
    try:
        lineage = await audit_service.trace_entity_lineage(db, entity_id=entity_id)
        return lineage
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lineage graph traversal failed: {str(e)}",
        )


@router.post("/audit/confidence/calculate", response_model=ConfidenceMetricsSchema)
async def calculate_confidence_metrics(
    request: ConfidenceCalculationRequest,
):
    """
    Calculate composite confidence metrics using Weighted Average paired with Minimum Component Guardrail.
    """
    try:
        return audit_service.calculate_confidence(
            extraction_confidence=request.extraction_confidence,
            resolution_confidence=request.resolution_confidence,
            relevance_confidence=request.relevance_confidence,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confidence calculation failed: {str(e)}",
        )
