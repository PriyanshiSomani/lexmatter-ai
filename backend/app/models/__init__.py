"""
LexMatter AI — Unified ORM Models Package
Exports all 21 domain models across 6 layers for Alembic and application discovery.
"""

# Layer 1: Source Layer
from backend.app.models.source import (
    Matter,
    Document,
    DocumentVersion,
    Page,
    SourceSpan,
)

# Layer 2: Extraction Layer
from backend.app.models.extraction import (
    Entity,
    SourceAssertion,
    Event,
)

# Layer 3: Knowledge Layer
from backend.app.models.knowledge import (
    CanonicalFact,
    Relationship,
    Conflict,
)

# Layer 4: Legal Knowledge Layer
from backend.app.models.legal import (
    Authority,
    Requirement,
    RequirementVersion,
    RequirementApplicability,
)

# Layer 5: Analysis Layer
from backend.app.models.analysis import (
    EvidenceMapping,
    Finding,
    EvidenceGap,
    ResearchIssue,
)

# Layer 6: Workflow & Audit Layer
from backend.app.models.audit import (
    AgentRun,
    HumanReview,
    AuditEvent,
)

__all__ = [
    # Layer 1
    "Matter",
    "Document",
    "DocumentVersion",
    "Page",
    "SourceSpan",
    # Layer 2
    "Entity",
    "SourceAssertion",
    "Event",
    # Layer 3
    "CanonicalFact",
    "Relationship",
    "Conflict",
    # Layer 4
    "Authority",
    "Requirement",
    "RequirementVersion",
    "RequirementApplicability",
    # Layer 5
    "EvidenceMapping",
    "Finding",
    "EvidenceGap",
    "ResearchIssue",
    # Layer 6
    "AgentRun",
    "HumanReview",
    "AuditEvent",
]
