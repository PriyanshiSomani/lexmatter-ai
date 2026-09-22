"""
LexMatter AI — Layer 6: Workflow & Audit Layer ORM Models
Models: AgentRun, HumanReview, AuditEvent
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base
from backend.app.core.id_generator import (
    PREFIX_AGENT_RUN,
    PREFIX_AUDIT_EVENT,
    PREFIX_HUMAN_REVIEW,
    generate_id,
)


class AgentRun(Base):
    """Tracks execution, token usage, latency, and status of LangGraph agent runs."""
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_AGENT_RUN),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="QUEUED")
    input_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="agent_runs")

    __table_args__ = (
        Index("idx_agent_runs_status", "matter_id", "agent_name", "status"),
    )


class HumanReview(Base):
    """Stores human reviewer decisions on findings, conflicts, or gaps."""
    __tablename__ = "human_reviews"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_HUMAN_REVIEW),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reviewer_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=False)

    reviewed_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="human_reviews")

    __table_args__ = (
        Index("idx_human_reviews_target", "target_type", "target_id"),
        Index("idx_human_reviews_matter", "matter_id", "decision"),
    )


class AuditEvent(Base):
    """Append-only immutable audit trail for security, governance, and defensibility."""
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_AUDIT_EVENT),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    timestamp: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="audit_events")

    __table_args__ = (
        Index("idx_audit_events_matter_time", "matter_id", "timestamp"),
    )
