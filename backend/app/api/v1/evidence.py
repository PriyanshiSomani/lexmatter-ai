"""
LexMatter AI — Evidence Intelligence & Gap Analysis API Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.models.analysis import EvidenceGap, EvidenceMapping
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


@router.get("/matters/{matter_id}/evidence", response_model=List[EvidenceMappingSchema])
async def list_evidence_mappings(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all evidence mappings for a matter."""
    try:
        stmt = select(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id).order_by(EvidenceMapping.created_at.desc())
        res = await db.execute(stmt)
        return res.scalars().all()
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
        stmt = select(EvidenceGap).where(EvidenceGap.matter_id == matter_id).order_by(EvidenceGap.created_at.desc())
        res = await db.execute(stmt)
        return res.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch evidence gaps: {str(e)}",
        )
