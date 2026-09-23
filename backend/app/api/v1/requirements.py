"""
LexMatter AI — Legal Requirements API Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.schemas.legal import RequirementApplicabilitySchema
from backend.app.services.requirement_service import requirement_service

router = APIRouter(tags=["Legal Requirements"])


@router.post("/requirements/seed", status_code=status.HTTP_200_OK)
async def seed_legal_requirements(db: AsyncSession = Depends(get_db)):
    """Seed official L-1B authorities and Requirements R1-R6 into PostgreSQL."""
    try:
        result = await requirement_service.seed_l1b_requirements(db)
        return {
            "status": "COMPLETED",
            "metrics": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}",
        )


@router.get("/matters/{matter_id}/requirements", response_model=List[RequirementApplicabilitySchema])
async def get_matter_requirements(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all L-1B requirements and evaluation status for a matter."""
    try:
        return await requirement_service.get_matter_requirements(db, matter_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch requirements: {str(e)}",
        )
