"""
LexMatter AI — Hybrid Search & Citation API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.schemas.retrieval import CitationPackage, SearchQuery
from backend.app.services.hybrid_search_service import hybrid_search_service

router = APIRouter(prefix="/matters/{matter_id}/search", tags=["Search & Retrieval"])


@router.post("", response_model=CitationPackage, status_code=status.HTTP_200_OK)
async def search_matter_spans(
    matter_id: str,
    query: SearchQuery,
    db: AsyncSession = Depends(get_db),
):
    """Execute hybrid retrieval (dense pgvector + sparse keyword search) with RRF fusion.
    
    Returns a CitationPackage containing exact page numbers, document titles,
    character spans (start_char, end_char), and PDF bounding box coordinates.
    """
    try:
        citation_package = await hybrid_search_service.hybrid_search(
            db=db,
            matter_id=matter_id,
            query=query,
        )
        return citation_package
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid search failed: {str(e)}",
        )
