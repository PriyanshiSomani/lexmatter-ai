"""
LexMatter AI — Pydantic Schemas for Canonical Facts, Conflicts, and Resolution
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConflictSchema(BaseModel):
    """Schema for a detected cross-document discrepancy."""
    id: str
    matter_id: str
    subject_entity_id: Optional[str] = None
    predicate: str
    conflict_type: str = Field(description="DATE_MISMATCH, TITLE_MISMATCH, SALARY_MISMATCH, RELATIONSHIP_MISMATCH, FACTUAL_CONTRADICTION")
    conflicting_assertion_ids: List[str] = Field(default_factory=list)
    severity: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    status: str = Field(description="UNRESOLVED, HUMAN_RESOLVED, DISMISSED")
    resolution_notes: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None


class CanonicalFactSchema(BaseModel):
    """Schema for a consolidated, matter-level fact."""
    id: str
    matter_id: str
    subject_entity_id: str
    predicate: str
    canonical_value: Optional[Dict[str, Any]] = None
    candidate_values: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = Field(description="UNCONTESTED, CORROBORATED, CONFLICTING, RESOLVED_BY_HUMAN")
    created_at: datetime
    updated_at: datetime


class ConflictResolutionRequest(BaseModel):
    """Payload sent by an attorney to resolve a conflict."""
    accepted_value: Any = Field(description="Value accepted by the human reviewer")
    resolution_notes: str = Field(description="Explanatory comment regarding how the conflict was resolved")
    reviewer_id: str = Field(description="Attorney user ID or email")
