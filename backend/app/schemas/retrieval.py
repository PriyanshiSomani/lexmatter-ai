"""
LexMatter AI — Pydantic Schemas for Search Queries and Citation Packages
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Input query payload for hybrid retrieval."""
    query_text: str = Field(description="Search string or question")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of top search results to return")
    document_type_filter: Optional[str] = Field(None, description="Optional document type metadata filter (e.g. PETITION_LETTER)")
    query_vector: Optional[List[float]] = Field(None, description="Optional 768-dim query embedding vector")


class SearchResultSpan(BaseModel):
    """Retrieved SourceSpan enriched with document provenance metadata and fusion scores."""
    span_id: str
    document_id: str
    document_title: str
    document_type: str
    page_number: int
    start_char: int
    end_char: int
    text_snippet: str
    bounding_box: Optional[Dict[str, float]] = None
    vector_score: float = Field(default=0.0, description="Cosine similarity score (0.0 to 1.0)")
    keyword_score: float = Field(default=0.0, description="Full-text rank score")
    rrf_score: float = Field(default=0.0, description="Reciprocal Rank Fusion score")


class CitationPackage(BaseModel):
    """Container payload returned to agents with formatted search results and citations."""
    matter_id: str
    query_text: str
    total_results: int
    results: List[SearchResultSpan] = Field(default_factory=list)
