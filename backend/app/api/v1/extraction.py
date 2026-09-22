"""
LexMatter AI — Structured Extraction API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.services.extraction_service import extraction_service

router = APIRouter(prefix="/matters/{matter_id}/extract", tags=["Extraction"])


@router.post("", status_code=status.HTTP_200_OK)
async def extract_matter_knowledge(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Trigger structured extraction across all SourceSpans in a matter.
    
    Extracts named entities, resolves canonical names, creates immutable SourceAssertions,
    and builds chronological timeline Events.
    """
    try:
        result = await extraction_service.process_matter_extractions(db, matter_id)
        return {
            "matter_id": matter_id,
            "status": "COMPLETED",
            "metrics": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )
