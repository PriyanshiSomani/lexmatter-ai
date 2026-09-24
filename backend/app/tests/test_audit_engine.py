"""
LexMatter AI — Phase 11 Audit & Provenance Verification Unit Tests
"""

from backend.app.schemas.audit import OperationalTier
from backend.app.services.audit_service import audit_service


def test_calibrated_confidence_weighted_average():
    """Verify weighted average calculation for high confidence evidence."""
    # 0.90 across all three stages
    res = audit_service.calculate_confidence(
        extraction_confidence=0.90,
        resolution_confidence=0.90,
        relevance_confidence=0.90,
    )

    assert res.composite_confidence == 0.90
    assert res.operational_tier == OperationalTier.HIGH
    assert res.tier_label == "Eligible for normal processing"
    assert res.guardrail_triggered is False


def test_min_component_guardrail_trigger():
    """Verify that a single low component score triggers the guardrail even if others are high."""
    # High extraction (0.95) & relevance (0.95), but low resolution (0.40)
    res = audit_service.calculate_confidence(
        extraction_confidence=0.95,
        resolution_confidence=0.40,
        relevance_confidence=0.95,
    )

    assert res.guardrail_triggered is True
    assert res.composite_confidence == 0.40
    assert res.operational_tier == OperationalTier.NEEDS_REVIEW
    assert res.tier_label == "Requires human review"
    assert "minimum component guardrail breach" in res.explanation


def test_medium_confidence_tier():
    """Verify medium confidence tier operational labelling."""
    res = audit_service.calculate_confidence(
        extraction_confidence=0.75,
        resolution_confidence=0.70,
        relevance_confidence=0.72,
    )

    assert 0.65 <= res.composite_confidence < 0.80
    assert res.operational_tier == OperationalTier.MEDIUM
    assert res.tier_label == "Flagged for optional attorney review"
    assert res.guardrail_triggered is False
