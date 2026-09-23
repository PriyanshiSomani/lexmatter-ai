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
