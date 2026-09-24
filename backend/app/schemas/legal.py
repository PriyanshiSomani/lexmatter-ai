"""
LexMatter AI — Pydantic Schemas for Legal Authorities and Requirements
"""

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuthoritySchema(BaseModel):
    """Schema for an authoritative legal source (statute, regulation, policy manual)."""
    id: str
    authority_type: str
    citation_title: str
    jurisdiction: str = "US_FEDERAL"
    source_url: Optional[str] = None
    full_text: str
    effective_date: Optional[date] = None


class RequirementVersionSchema(BaseModel):
    """Schema for a versioned legal requirement standard with evaluation dimensions."""
    id: str
    requirement_id: str
    version_number: int
    authority_id: Optional[str] = None
    description: str
    evaluation_dimensions: List[str] = Field(default_factory=list)
    effective_from: date


class RequirementSchema(BaseModel):
    """Schema for a top-level legal requirement."""
    id: str
    code: str
    case_type: str
    category: str
    title: str
    active_version: Optional[RequirementVersionSchema] = None


class RequirementApplicabilitySchema(BaseModel):
    """Schema for matter-specific requirement evaluation readiness status."""
    id: str
    matter_id: str
    requirement_version_id: str
    status: str = Field(default="NOT_EVALUATED", description="NOT_EVALUATED, EVIDENCE_LOCATED, PARTIAL_SUPPORT, CONFLICT_DETECTED, POTENTIAL_GAP, HUMAN_VERIFIED")
    notes: Optional[str] = None
    requirement_code: Optional[str] = None
    requirement_title: Optional[str] = None
