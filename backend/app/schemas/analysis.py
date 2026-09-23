"""
LexMatter AI — Pydantic Schemas for Evidence Mappings, Evidence Gaps, and Findings
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceMappingSchema(BaseModel):
    """Schema for a formal link between a SourceAssertion and a RequirementVersion dimension."""
    id: str
    matter_id: str
    source_assertion_id: str
    requirement_version_id: str
    relationship: str = Field(description="SUPPORTS, PARTIALLY_SUPPORTS, CONTRADICTS, CONTEXT_ONLY, DUPLICATES, UNCLEAR")
    target_dimension: Optional[str] = None
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    analysis_notes: Optional[str] = None
    created_at: datetime


class EvidenceGapSchema(BaseModel):
    """Schema for a detected missing or weak evidence dimension."""
    id: str
    matter_id: str
    requirement_version_id: str
    dimension: str
    status: str = Field(description="POTENTIAL_GAP, DOCUMENT_REQUESTED, RESOLVED, DISMISSED")
    observation: str = Field(description="Factual, guarded description of missing evidence")
    searched_document_count: int = 0
    created_at: datetime


class FindingSchema(BaseModel):
    """Schema for an analytical conclusion or consistency finding."""
    id: str
    matter_id: str
    category: str = Field(description="CONSISTENCY, EVIDENCE_STRENGTH, ELIGIBILITY_RISK, PROCEDURAL_DEFECT")
    severity: str = Field(description="INFO, LOW, MEDIUM, HIGH, CRITICAL")
    title: str
    description: str
    supporting_span_ids: List[str] = Field(default_factory=list)
    impacted_requirement_ids: List[str] = Field(default_factory=list)
    status: str = Field(description="PENDING_REVIEW, ACCEPTED, REJECTED, MODIFIED")
    created_at: datetime


class RequirementCoverageSummary(BaseModel):
    """Summary of evidence coverage across all matter requirements."""
    matter_id: str
    total_requirements: int
    evaluated_requirements: int
    total_evidence_mappings: int
    total_evidence_gaps: int
    coverage_percentage: float
