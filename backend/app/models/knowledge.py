"""
LexMatter AI — Layer 3: Knowledge Layer ORM Models
Models: CanonicalFact, Relationship, Conflict
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base
from backend.app.core.id_generator import (
    PREFIX_CANONICAL_FACT,
    PREFIX_CONFLICT,
    PREFIX_RELATIONSHIP,
    generate_id,
)


class CanonicalFact(Base):
    """Normalized, consolidated fact for an entity in the matter."""
    __tablename__ = "canonical_facts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_CANONICAL_FACT),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    subject_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    predicate: Mapped[str] = mapped_column(String(100), nullable=False)
    canonical_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    candidate_values: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="UNCONTESTED")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="canonical_facts")
    subject_entity: Mapped["Entity"] = relationship("Entity", back_populates="canonical_facts")

    __table_args__ = (
        UniqueConstraint("matter_id", "subject_entity_id", "predicate", name="uq_canonical_facts_subject_pred"),
        Index("idx_canonical_facts_status", "matter_id", "status"),
    )


class Relationship(Base):
    """Directed semantic connection between two entities."""
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_RELATIONSHIP),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    source_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    supporting_assertion_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PROPOSED")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="relationships")
    source_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[source_entity_id], back_populates="source_relationships")
    target_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[target_entity_id], back_populates="target_relationships")

    __table_args__ = (
        Index("idx_relationships_pair", "matter_id", "source_entity_id", "relationship_type", "target_entity_id"),
        Index("idx_relationships_assertions_gin", "supporting_assertion_ids", postgresql_using="gin"),
    )


class Conflict(Base):
    """Explicit discrepancy across documents flagged for human review."""
    __tablename__ = "conflicts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_CONFLICT),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    subject_entity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True)
    predicate: Mapped[str] = mapped_column(String(100), nullable=False)
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    conflicting_assertion_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="UNRESOLVED")
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    detected_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="conflicts")
    subject_entity: Mapped[Optional["Entity"]] = relationship("Entity", back_populates="conflicts")

    __table_args__ = (
        Index("idx_conflicts_status_severity", "matter_id", "status", "severity"),
        Index("idx_conflicts_assertions_gin", "conflicting_assertion_ids", postgresql_using="gin"),
    )
