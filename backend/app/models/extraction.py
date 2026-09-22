"""
LexMatter AI — Layer 2: Extraction Layer ORM Models
Models: Entity, SourceAssertion, Event
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base
from backend.app.core.id_generator import (
    PREFIX_ENTITY,
    PREFIX_EVENT,
    PREFIX_SOURCE_ASSERTION,
    generate_id,
)


class Entity(Base):
    """Named entity mentioned in matter documents."""
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_ENTITY),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="entities")
    source_assertions: Mapped[List["SourceAssertion"]] = relationship("SourceAssertion", back_populates="subject_entity")
    canonical_facts: Mapped[List["CanonicalFact"]] = relationship("CanonicalFact", back_populates="subject_entity")
    source_relationships: Mapped[List["Relationship"]] = relationship("Relationship", foreign_keys="[Relationship.source_entity_id]", back_populates="source_entity")
    target_relationships: Mapped[List["Relationship"]] = relationship("Relationship", foreign_keys="[Relationship.target_entity_id]", back_populates="target_entity")
    conflicts: Mapped[List["Conflict"]] = relationship("Conflict", back_populates="subject_entity")

    __table_args__ = (
        Index("idx_entities_canonical", "matter_id", "entity_type", "canonical_name"),
        Index("idx_entities_attrs_gin", "attributes", postgresql_using="gin"),
    )


class SourceAssertion(Base):
    """Immutable structured claim extracted from a specific SourceSpan."""
    __tablename__ = "source_assertions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_SOURCE_ASSERTION),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    source_span_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_spans.id", ondelete="RESTRICT"), nullable=False)
    subject_entity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True)
    predicate: Mapped[str] = mapped_column(String(100), nullable=False)
    object_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    extraction_method: Mapped[str] = mapped_column(String(50), nullable=False, default="LLM_STRUCTURED")
    is_immutable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    extracted_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="source_assertions")
    source_span: Mapped["SourceSpan"] = relationship("SourceSpan", back_populates="source_assertions")
    subject_entity: Mapped[Optional["Entity"]] = relationship("Entity", back_populates="source_assertions")
    evidence_mappings: Mapped[List["EvidenceMapping"]] = relationship("EvidenceMapping", back_populates="source_assertion")

    __table_args__ = (
        Index("idx_assertions_lookup", "matter_id", "predicate", "subject_entity_id"),
        Index("idx_assertions_value_gin", "object_value", postgresql_using="gin"),
    )


class Event(Base):
    """Chronological milestone in the matter timeline."""
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_EVENT),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    participants: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    supporting_assertion_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="events")

    __table_args__ = (
        Index("idx_events_timeline", "matter_id", "event_date", "event_type"),
        Index("idx_events_participants_gin", "participants", postgresql_using="gin"),
        Index("idx_events_assertions_gin", "supporting_assertion_ids", postgresql_using="gin"),
    )
