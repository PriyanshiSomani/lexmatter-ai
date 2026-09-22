"""
LexMatter AI — Phase 4 Extraction Engine Unit Tests
"""

from backend.app.schemas.extraction import ExtractedAssertion, ExtractedEntity, ExtractedEvent
from backend.app.services.entity_resolver_service import entity_resolver_service
from backend.app.services.extraction_service import extraction_service


def test_entity_canonicalization():
    """Verify entity name normalization strips noise words and punctuation."""
    raw1 = "Mr. Rajesh Sharma"
    raw2 = "Apex Technologies Pvt. Ltd."
    raw3 = "Apex Technologies Inc."

    assert entity_resolver_service.normalize_canonical_name(raw1) == "rajesh sharma"
    assert entity_resolver_service.normalize_canonical_name(raw2) == "apex technologies"
    assert entity_resolver_service.normalize_canonical_name(raw3) == "apex technologies"


def test_pattern_extraction_from_snippet():
    """Verify regex extraction identifies job title, employment start date, and salary claims."""
    snippet = (
        "Mr. Rajesh Sharma was employed as Lead Architect at Apex India Pvt. Ltd. "
        "commenced from May 15, 2021 with an annual salary of $125,000."
    )

    batch = extraction_service.extract_from_snippet(snippet)

    # Verify extracted entities
    role_entities = [e for e in batch["entities"] if e.entity_type == "ROLE_TITLE"]
    assert len(role_entities) == 1
    assert "Lead Architect" in role_entities[0].name

    # Verify extracted assertions
    predicates = [a.predicate for a in batch["assertions"]]
    assert "job_title" in predicates
    assert "foreign_employment_start_date" in predicates
    assert "annual_salary" in predicates

    # Verify timeline event
    assert len(batch["events"]) == 1
    assert batch["events"][0].event_type == "EMPLOYMENT_START"
    assert batch["events"][0].event_date == "May 15, 2021"


def test_pydantic_schema_validation():
    """Verify ExtractedAssertion Pydantic schema validation rules."""
    asrt = ExtractedAssertion(
        subject_name="Rajesh Sharma",
        predicate="job_title",
        normalized_value="Lead Architect",
        raw_text="employed as Lead Architect",
        confidence=0.95,
    )
    assert asrt.confidence == 0.95
    assert asrt.predicate == "job_title"
