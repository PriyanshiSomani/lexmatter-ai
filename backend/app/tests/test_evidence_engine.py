"""
LexMatter AI — Phase 8 Evidence Engine Unit Tests
"""

from datetime import datetime
from backend.app.schemas.analysis import EvidenceGapSchema, EvidenceMappingSchema
from backend.app.services.evidence_service import evidence_service


def test_predicate_dimension_mappings():
    """Verify predicate to requirement dimension mapping rules."""
    assert evidence_service.PREDICATE_DIMENSION_MAP["job_title"] == "us_position_duties_described"
    assert evidence_service.PREDICATE_DIMENSION_MAP["foreign_employment_start_date"] == "continuous_one_year_duration"
    assert evidence_service.PREDICATE_DIMENSION_MAP["specialized_tool_used"] == "proprietary_product_process_or_system"


def test_guarded_gap_schema_validation():
    """Verify EvidenceGapSchema schema defaults and guarded phrasing."""
    gap = EvidenceGapSchema(
        id="gap_01",
        matter_id="mat_01",
        requirement_version_id="reqv_01",
        dimension="organizational_comparison",
        status="POTENTIAL_GAP",
        observation="Potential evidence gap detected for dimension organizational_comparison. 3 documents searched.",
        searched_document_count=3,
        created_at=datetime.utcnow(),
    )

    assert gap.status == "POTENTIAL_GAP"
    assert "Potential evidence gap" in gap.observation
    assert gap.searched_document_count == 3


def test_evidence_mapping_schema():
    """Verify EvidenceMappingSchema validation."""
    mapping = EvidenceMappingSchema(
        id="evm_01",
        matter_id="mat_01",
        source_assertion_id="asrt_01",
        requirement_version_id="reqv_01",
        relationship="SUPPORTS",
        target_dimension="continuous_one_year_duration",
        relevance_score=0.95,
        created_at=datetime.utcnow(),
    )

    assert mapping.relationship == "SUPPORTS"
    assert mapping.relevance_score == 0.95


import pytest
from backend.app.core.db import init_db, AsyncSessionLocal
from backend.app.core.id_generator import generate_id, PREFIX_MATTER, PREFIX_DOCUMENT
from backend.app.models.source import Matter, Document
from backend.app.models.extraction import SourceAssertion
from backend.app.models.analysis import EvidenceMapping, EvidenceGap
from sqlalchemy import select


@pytest.mark.asyncio
async def test_per_dimension_evidence_evaluation_isolation():
    """Verify that evaluate_dimension_evidence evaluates one dimension without wiping other dimension mappings."""
    from backend.app.core.id_generator import PREFIX_DOCUMENT_VERSION, PREFIX_PAGE, PREFIX_SOURCE_SPAN
    from backend.app.models.source import DocumentVersion, Page, SourceSpan

    await init_db()
    async with AsyncSessionLocal() as db:
        matter_id = generate_id(PREFIX_MATTER)
        doc_id = generate_id(PREFIX_DOCUMENT)
        doc_ver_id = generate_id(PREFIX_DOCUMENT_VERSION)
        page_id = generate_id(PREFIX_PAGE)
        span_id = generate_id(PREFIX_SOURCE_SPAN)

        matter = Matter(id=matter_id, title="Test Matter", matter_type="IMMIGRATION", case_type="L1B")
        doc = Document(id=doc_id, matter_id=matter_id, title="Test.pdf", document_type="PETITION_LETTER")
        doc_ver = DocumentVersion(id=doc_ver_id, document_id=doc_id, version_number=1, file_hash_sha256="hash123", file_path="/path", file_size_bytes=1024)
        page = Page(id=page_id, document_version_id=doc_ver_id, page_number=1, raw_text="Senior Engineer since 2020.")
        span = SourceSpan(id=span_id, page_id=page_id, start_char=0, end_char=25, text_snippet="Senior Engineer", text_hash="hashspan")
        
        db.add_all([matter, doc, doc_ver, page, span])
        await db.flush()

        # Add assertions for 2 separate dimensions referencing span_id
        asrt_1 = SourceAssertion(
            matter_id=matter_id,
            source_span_id=span_id,
            predicate="job_title",  # maps to us_position_duties_described
            object_value={"raw_text": "Senior Engineer"},
            confidence=0.9,
            extraction_method="RULE_ENGINE",
        )
        asrt_2 = SourceAssertion(
            matter_id=matter_id,
            source_span_id=span_id,
            predicate="foreign_employment_start_date",  # maps to continuous_one_year_duration
            object_value={"raw_text": "2020-01-01"},
            confidence=0.9,
            extraction_method="RULE_ENGINE",
        )
        db.add_all([asrt_1, asrt_2])
        await db.flush()

        # Evaluate Dimension 1
        res1 = await evidence_service.evaluate_dimension_evidence(db, matter_id, "us_position_duties_described")
        assert res1["mappings_created"] == 1

        # Check mappings after Dimension 1
        stmt1 = select(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id)
        res_stmt1 = await db.execute(stmt1)
        mappings_after_dim1 = res_stmt1.scalars().all()
        assert len(mappings_after_dim1) == 1
        dim1_mapping_id = mappings_after_dim1[0].id

        # Evaluate Dimension 2
        res2 = await evidence_service.evaluate_dimension_evidence(db, matter_id, "continuous_one_year_duration")
        assert res2["mappings_created"] == 1

        # Check mappings after Dimension 2: Dimension 1 mapping MUST STILL EXIST
        res_stmt2 = await db.execute(stmt1)
        mappings_after_dim2 = res_stmt2.scalars().all()
        assert len(mappings_after_dim2) == 2

        mapped_ids = [m.id for m in mappings_after_dim2]
        assert dim1_mapping_id in mapped_ids

