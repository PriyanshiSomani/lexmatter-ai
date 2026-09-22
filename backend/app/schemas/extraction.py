"""
LexMatter AI — Pydantic Schemas for Extraction Engine Output Validation
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    """Schema for an extracted named entity."""
    name: str = Field(description="Surface name extracted from text")
    entity_type: str = Field(description="PERSON, ORGANIZATION, ROLE_TITLE, PRODUCT_SYSTEM, LOCATION, DATE_PERIOD")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata attributes")


class ExtractedAssertion(BaseModel):
    """Schema for an immutable source claim."""
    subject_name: Optional[str] = Field(None, description="Entity name that is the subject of the claim")
    predicate: str = Field(description="Attribute claim (e.g. foreign_employment_start_date, job_title, salary)")
    normalized_value: Any = Field(description="Normalized value (ISO date, string, or number)")
    raw_text: str = Field(description="Verbatim string from text")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ExtractedEvent(BaseModel):
    """Schema for a chronological milestone event."""
    event_type: str = Field(description="EMPLOYMENT_START, EMPLOYMENT_END, PROMOTION, PETITION_SUBMITTED, DEGREE_CONFERRED")
    event_date: str = Field(description="ISO date or partial date string (e.g. 2021-06-01 or 2021-06)")
    description: str = Field(description="Brief narrative summary of milestone")
    participant_names: List[str] = Field(default_factory=list, description="Entity names involved in event")


class ExtractionBatchResult(BaseModel):
    """Batch container for extraction results from a SourceSpan snippet."""
    span_id: str
    entities: List[ExtractedEntity] = Field(default_factory=list)
    assertions: List[ExtractedAssertion] = Field(default_factory=list)
    events: List[ExtractedEvent] = Field(default_factory=list)
