"""
LexMatter AI — Audit & Provenance Verification Schemas
Phase 11: Audit & Provenance Verification Engine
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class OperationalTier(str, Enum):
    HIGH = "HIGH"                  # Eligible for normal processing (score >= 0.80)
    MEDIUM = "MEDIUM"              # Flagged for optional attorney review (0.65 <= score < 0.80)
    NEEDS_REVIEW = "NEEDS_REVIEW"  # Requires human review (score < 0.65 or guardrail breach)


class ConfidenceMetricsSchema(BaseModel):
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="OCR and text extraction clarity score")
    resolution_confidence: float = Field(..., ge=0.0, le=1.0, description="Entity resolution similarity score")
    relevance_confidence: float = Field(..., ge=0.0, le=1.0, description="Vector/semantic relevance score")
    composite_confidence: float = Field(..., ge=0.0, le=1.0, description="Hybrid weighted average with min-component guardrail")
    operational_tier: OperationalTier
    tier_label: str
    guardrail_triggered: bool = False
    explanation: str


class ConfidenceCalculationRequest(BaseModel):
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    resolution_confidence: float = Field(..., ge=0.0, le=1.0, description="Entity resolution confidence score")
    relevance_confidence: float = Field(..., ge=0.0, le=1.0, description="Semantic relevance score")


class LineageNodeType(str, Enum):
    DOCUMENT = "DOCUMENT"
    DOCUMENT_CHUNK = "DOCUMENT_CHUNK"
    SOURCE_SPAN = "SOURCE_SPAN"
    SOURCE_ASSERTION = "SOURCE_ASSERTION"
    CANONICAL_FACT = "CANONICAL_FACT"
    EVIDENCE_MAPPING = "EVIDENCE_MAPPING"
    CONFLICT = "CONFLICT"
    EVIDENCE_GAP = "EVIDENCE_GAP"
    REPORT_SECTION = "REPORT_SECTION"


class LineageNode(BaseModel):
    node_id: str
    node_type: LineageNodeType
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[ConfidenceMetricsSchema] = None


class LineageEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str = "DERIVED_FROM"


class LineageGraphResponse(BaseModel):
    root_entity_id: str
    matter_id: str
    generated_at: datetime
    nodes: List[LineageNode]
    edges: List[LineageEdge]
    overall_confidence: ConfidenceMetricsSchema
    provenance_verified: bool
