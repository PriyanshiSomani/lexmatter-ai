"""
LexMatter AI — Phase 6 Requirement Engine Unit Tests
"""

from backend.app.core.l1b_requirements_seed import AUTHORITIES_SEED, REQUIREMENTS_SEED
from backend.app.schemas.legal import RequirementApplicabilitySchema


def test_seed_dataset_completeness():
    """Verify L-1B seed dataset contains 2 authorities and 6 requirements (R1 through R6)."""
    assert len(AUTHORITIES_SEED) == 2
    assert len(REQUIREMENTS_SEED) == 6

    req_codes = [r["code"] for r in REQUIREMENTS_SEED]
    assert "L1B-REQ-R1" in req_codes
    assert "L1B-REQ-R3" in req_codes
    assert "L1B-REQ-R4" in req_codes


def test_r4_specialized_knowledge_dimensions():
    """Verify R4 (Specialized Knowledge) contains its 4 evaluation dimensions."""
    r4 = next(r for r in REQUIREMENTS_SEED if r["code"] == "L1B-REQ-R4")
    dims = r4["evaluation_dimensions"]

    assert len(dims) == 4
    assert "proprietary_product_process_or_system" in dims
    assert "advanced_expertise_level" in dims


def test_applicability_schema_defaults():
    """Verify RequirementApplicabilitySchema default values."""
    app = RequirementApplicabilitySchema(
        id="reqapp_01",
        matter_id="mat_01",
        requirement_version_id="reqv_01",
        requirement_code="L1B-REQ-R1",
        requirement_title="Qualifying Organization",
    )
    assert app.status == "NOT_EVALUATED"
    assert app.notes is None
