"""
LexMatter AI — Dense Vector Search Service
Executes pgvector HNSW cosine distance queries over SourceSpan embeddings.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan


class VectorSearchService:
    """Performs dense vector similarity retrieval using pgvector HNSW index."""

    async def search_vectors(
        self,
        db: AsyncSession,
        matter_id: str,
        query_vector: List[float],
        top_k: int = 10,
        doc_type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search SourceSpans by embedding vector cosine similarity.
        
        Returns list of dicts with span data and vector_score.
        """
        # Calculate cosine distance using pgvector operator
        distance_col = SourceSpan.embedding.cosine_distance(query_vector).label("distance")

        stmt = (
            select(SourceSpan, Page, Document, distance_col)
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(Document.matter_id == matter_id)
            .where(SourceSpan.embedding.isnot(None))
        )

        if doc_type_filter:
            stmt = stmt.where(Document.document_type == doc_type_filter)

        # Order by closest distance first
        stmt = stmt.order_by(distance_col).limit(top_k)

        result = await db.execute(stmt)
        rows = result.all()

        results = []
        for span, page, doc, dist in rows:
            # Convert cosine distance to cosine similarity (1.0 - distance)
            sim_score = round(max(0.0, 1.0 - float(dist)), 4)
            results.append({
                "span_id": span.id,
                "document_id": doc.id,
                "document_title": doc.title,
                "document_type": doc.document_type,
                "page_number": page.page_number,
                "start_char": span.start_char,
                "end_char": span.end_char,
                "text_snippet": span.text_snippet,
                "bounding_box": span.bounding_box,
                "vector_score": sim_score,
            })

        return results


vector_search_service = VectorSearchService()
