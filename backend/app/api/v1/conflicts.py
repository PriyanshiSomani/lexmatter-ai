"""
LexMatter AI — Conflicts & Consistency API Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.models.knowledge import Conflict
from backend.app.schemas.knowledge import ConflictResolutionRequest, ConflictSchema
from backend.app.services.consistency_service import consistency_service

router = APIRouter(tags=["Conflicts & Consistency"])


@router.post("/matters/{matter_id}/conflicts/analyze", status_code=status.HTTP_200_OK)
async def analyze_consistency(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger consistency analysis across matter assertions to detect cross-document conflicts."""
    try:
        metrics = await consistency_service.analyze_matter_consistency(db, matter_id)
        return {
            "matter_id": matter_id,
            "status": "COMPLETED",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Consistency analysis failed: {str(e)}",
        )


@router.get("/matters/{matter_id}/conflicts", response_model=List[ConflictSchema])
async def list_conflicts(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all detected conflicts for a matter."""
    try:
        stmt = select(Conflict).where(Conflict.matter_id == matter_id).order_by(Conflict.detected_at.desc())
        res = await db.execute(stmt)
        return res.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conflicts: {str(e)}",
        )


@router.post("/conflicts/{conflict_id}/resolve", response_model=ConflictSchema)
async def resolve_conflict(
    conflict_id: str,
    payload: ConflictResolutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resolve a conflict with attorney notes and update canonical fact status."""
    try:
        conflict = await consistency_service.resolve_conflict(db, conflict_id, payload)
        return conflict
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve conflict: {str(e)}",
        )
