"""
LexMatter AI — Phase 5 Hybrid Retrieval Unit Tests
"""

from backend.app.schemas.retrieval import SearchQuery, CitationPackage, SearchResultSpan
from backend.app.services.hybrid_search_service import hybrid_search_service


def test_rrf_fusion_scoring():
    """Verify that Reciprocal Rank Fusion correctly combines vector and keyword rank lists."""
    vec_results = [
        {
            "span_id": "span_01",
            "document_id": "doc_01",
            "document_title": "Support_Letter.pdf",
            "document_type": "PETITION_LETTER",
            "page_number": 1,
            "start_char": 0,
            "end_char": 50,
            "text_snippet": "Beneficiary possesses specialized knowledge of Titan.",
            "vector_score": 0.95,
        },
        {
            "span_id": "span_02",
            "document_id": "doc_01",
            "document_title": "Support_Letter.pdf",
            "document_type": "PETITION_LETTER",
            "page_number": 2,
            "start_char": 100,
            "end_char": 150,
            "text_snippet": "Foreign employment started May 2021.",
            "vector_score": 0.82,
        },
    ]

    key_results = [
        {
            "span_id": "span_02",
            "document_id": "doc_01",
            "document_title": "Support_Letter.pdf",
            "document_type": "PETITION_LETTER",
            "page_number": 2,
            "start_char": 100,
            "end_char": 150,
            "text_snippet": "Foreign employment started May 2021.",
            "keyword_score": 0.88,
        },
    ]

    fused = hybrid_search_service.apply_rrf_fusion(vec_results, key_results, top_k=5)

    assert len(fused) == 2
    # span_02 appears in both vector and keyword lists, so its RRF score is higher
    assert fused[0].span_id == "span_02"
    assert fused[0].rrf_score > fused[1].rrf_score


def test_search_query_schema():
    """Verify SearchQuery Pydantic defaults and validation."""
    query = SearchQuery(query_text="specialized knowledge")
    assert query.top_k == 5
    assert query.document_type_filter is None
