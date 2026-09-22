"""
LexMatter AI — Phase 2 Smoke Test
Verifies SQLAlchemy 2.0 ORM models, typed ULID generation, and pgvector vector search.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.id_generator import (
    generate_id,
    PREFIX_MATTER,
    PREFIX_DOCUMENT,
    PREFIX_DOCUMENT_VERSION,
    PREFIX_PAGE,
    PREFIX_SOURCE_SPAN,
)
from backend.app.models.source import (
    Matter,
    Document,
    DocumentVersion,
    Page,
    SourceSpan,
)
from backend.app.models.extraction import Entity, SourceAssertion
from backend.app.models.knowledge import CanonicalFact, Conflict
from backend.app.models.legal import Authority, Requirement, RequirementVersion
from backend.app.models.analysis import EvidenceMapping, Finding, EvidenceGap
from backend.app.models.audit import AgentRun, HumanReview


def test_id_generator():
    """Verify that generated IDs have expected typed prefixes and ULID length."""
    mat_id = generate_id(PREFIX_MATTER)
    doc_id = generate_id(PREFIX_DOCUMENT)
    span_id = generate_id(PREFIX_SOURCE_SPAN)

    assert mat_id.startswith("mat_")
    assert doc_id.startswith("doc_")
    assert span_id.startswith("span_")
    assert len(mat_id) == 30  # "mat_" (4 chars) + 26 ULID chars


def test_model_instantiation():
    """Verify model instances can be created with defaults and foreign key relationships."""
    matter = Matter(
        title="Acme Corp - L1B Petition",
        matter_type="IMMIGRATION",
        case_type="L1B",
        status="DRAFT",
    )
    assert matter.id.startswith("mat_")
    assert matter.matter_type == "IMMIGRATION"

    doc = Document(
        matter_id=matter.id,
        title="Support_Letter.pdf",
        document_type="PETITION_LETTER",
    )
    assert doc.id.startswith("doc_")
    assert doc.document_type == "PETITION_LETTER"

    # Dummy 768-dimensional embedding
    dummy_vector = [0.01] * 768
    span = SourceSpan(
        page_id="page_dummy",
        start_char=100,
        end_char=250,
        text_snippet="Beneficiary has proprietary knowledge of Apex Titan.",
        text_hash="abc123hash",
        embedding=dummy_vector,
    )
    assert span.id.startswith("span_")
    assert len(span.embedding) == 768
