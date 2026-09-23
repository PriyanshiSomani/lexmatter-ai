"""
LexMatter AI — Phase 7 Consistency Engine Unit Tests
"""

from backend.app.schemas.knowledge import ConflictResolutionRequest, ConflictSchema
from backend.app.services.consistency_service import consistency_service


def test_conflict_classification_rules():
    """Verify predicate conflict type and severity assignment rules."""
    ctype_date = consistency_service._determine_conflict_type("foreign_employment_start_date")
    sev_date = consistency_service._determine_severity("foreign_employment_start_date", ctype_date)

    assert ctype_date == "DATE_MISMATCH"
    assert sev_date == "HIGH"

    ctype_title = consistency_service._determine_conflict_type("job_title")
    sev_title = consistency_service._determine_severity("job_title", ctype_title)

    assert ctype_title == "TITLE_MISMATCH"
    assert sev_title == "MEDIUM"


def test_conflict_resolution_schema():
    """Verify ConflictResolutionRequest schema validation."""
    req = ConflictResolutionRequest(
        accepted_value="2021-05-15",
        resolution_notes="Attorney verified employment verification letter as authoritative.",
        reviewer_id="sarah.attorney@lexfirm.com",
    )

    assert req.accepted_value == "2021-05-15"
    assert "authoritative" in req.resolution_notes
