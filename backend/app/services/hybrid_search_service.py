"""
LexMatter AI — Sparse Keyword Search & Reciprocal Rank Fusion (RRF) Service
Combines pgvector dense retrieval and PostgreSQL full-text keyword retrieval into unified hybrid results.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan
from backend.app.schemas.retrieval import CitationPackage, SearchQuery, SearchResultSpan
from backend.app.services.vector_search_service import vector_search_service


class HybridSearchService:
    """Executes hybrid vector + keyword search and applies Reciprocal Rank Fusion (RRF)."""

    RRF_K = 60  # RRF smoothing constant

    async def search_keywords(
        self,
        db: AsyncSession,
        matter_id: str,
        query_text: str,
        top_k: int = 10,
        doc_type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform PostgreSQL full-text keyword search over SourceSpan snippets."""
        ts_query = func.plainto_tsquery("english", query_text)
        ts_vector = func.to_tsvector("english", SourceSpan.text_snippet)
        rank_col = func.ts_rank(ts_vector, ts_query).label("rank")

        stmt = (
            select(SourceSpan, Page, Document, rank_col)
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(Document.matter_id == matter_id)
            .where(ts_vector.op("@@")(ts_query))
        )

        if doc_type_filter:
            stmt = stmt.where(Document.document_type == doc_type_filter)

        stmt = stmt.order_by(rank_col.desc()).limit(top_k)

        result = await db.execute(stmt)
        rows = result.all()

        results = []
        for span, page, doc, rank_val in rows:
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
                "keyword_score": round(float(rank_val), 4),
            })
        return results

    def apply_rrf_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[SearchResultSpan]:
        """Combine dense vector ranks and sparse keyword ranks using Reciprocal Rank Fusion (RRF)."""
        rrf_scores: Dict[str, float] = {}
        span_map: Dict[str, Dict[str, Any]] = {}

        # 1. Process Vector Ranks
        for rank_idx, item in enumerate(vector_results, start=1):
            sid = item["span_id"]
            span_map[sid] = item
            rrf_scores[sid] = rrf_scores.get(sid, 0.0) + (1.0 / (self.RRF_K + rank_idx))

        # 2. Process Keyword Ranks
        for rank_idx, item in enumerate(keyword_results, start=1):
            sid = item["span_id"]
            if sid not in span_map:
                span_map[sid] = item
            else:
                span_map[sid]["keyword_score"] = item.get("keyword_score", 0.0)
            rrf_scores[sid] = rrf_scores.get(sid, 0.0) + (1.0 / (self.RRF_K + rank_idx))

        # 3. Sort by combined RRF score descending
        sorted_spans = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        fused_results: List[SearchResultSpan] = []
        for sid, score in sorted_spans:
            raw = span_map[sid]
            fused_results.append(SearchResultSpan(
                span_id=raw["span_id"],
                document_id=raw["document_id"],
                document_title=raw["document_title"],
                document_type=raw["document_type"],
                page_number=raw["page_number"],
                start_char=raw["start_char"],
                end_char=raw["end_char"],
                text_snippet=raw["text_snippet"],
                bounding_box=raw.get("bounding_box"),
                vector_score=raw.get("vector_score", 0.0),
                keyword_score=raw.get("keyword_score", 0.0),
                rrf_score=round(score, 6),
            ))

        return fused_results

    async def hybrid_search(
        self,
        db: AsyncSession,
        matter_id: str,
        query: SearchQuery,
    ) -> CitationPackage:
        """Orchestrate hybrid vector + keyword retrieval and return a CitationPackage."""
        vector_res = []
        if query.query_vector:
            vector_res = await vector_search_service.search_vectors(
                db=db,
                matter_id=matter_id,
                query_vector=query.query_vector,
                top_k=query.top_k * 2,
                doc_type_filter=query.document_type_filter,
            )

        keyword_res = await self.search_keywords(
            db=db,
            matter_id=matter_id,
            query_text=query.query_text,
            top_k=query.top_k * 2,
            doc_type_filter=query.document_type_filter,
        )

        fused = self.apply_rrf_fusion(vector_res, keyword_res, top_k=query.top_k)

        return CitationPackage(
            matter_id=matter_id,
            query_text=query.query_text,
            total_results=len(fused),
            results=fused,
        )


hybrid_search_service = HybridSearchService()
