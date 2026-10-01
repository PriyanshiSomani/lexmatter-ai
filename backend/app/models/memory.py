"""
LexMatter AI — Layer 7: Case Memory Layer ORM Model
Model: CaseMemory
"""

from datetime import datetime
from typing import Optional
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
    PREFIX_CASE_MEMORY,
    generate_id,
)


class CaseMemory(Base):
    """Stores case-scoped agent memory notes in PostgreSQL for LexMatter AI."""
    __tablename__ = "case_memories"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_CASE_MEMORY),
    )
    matter_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("matters.id", ondelete="CASCADE"),
        nullable=False,
    )
    memory_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    meta_data: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="case_memories")

    __table_args__ = (
        UniqueConstraint("matter_id", "memory_key", name="uq_matter_memory_key"),
        Index("idx_case_memory_lookup", "matter_id", "memory_key"),
        {"extend_existing": True},
    )
