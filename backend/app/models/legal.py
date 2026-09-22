"""
LexMatter AI — Layer 4: Legal Knowledge Layer ORM Models
Models: Authority, Requirement, RequirementVersion, RequirementApplicability
"""

from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import (
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from backend.app.core.db import Base
from backend.app.core.id_generator import (
    PREFIX_AUTHORITY,
    PREFIX_REQUIREMENT,
    PREFIX_REQUIREMENT_APPLICABILITY,
    PREFIX_REQUIREMENT_VERSION,
    generate_id,
)


class Authority(Base):
    """Authoritative legal source (statutes, CFR, USCIS policy manual)."""
    __tablename__ = "authorities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_AUTHORITY),
    )
    authority_type: Mapped[str] = mapped_column(String(50), nullable=False)
    citation_title: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), nullable=False, default="US_FEDERAL")
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    requirement_versions: Mapped[List["RequirementVersion"]] = relationship("RequirementVersion", back_populates="authority")

    __table_args__ = (
        Index("idx_authorities_type_citation", "authority_type", "citation_title"),
    )


class Requirement(Base):
    """Conceptual legal eligibility, evidentiary, or procedural requirement."""
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_REQUIREMENT),
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False, default="L1B")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="ELIGIBILITY")
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    versions: Mapped[List["RequirementVersion"]] = relationship("RequirementVersion", back_populates="requirement", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_requirements_case_cat", "case_type", "category"),
    )


class RequirementVersion(Base):
    """Versioned definition of a requirement with evaluation dimensions and vector embedding."""
    __tablename__ = "requirement_versions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_REQUIREMENT_VERSION),
    )
    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    authority_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("authorities.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_dimensions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, default=date(2020, 1, 1))
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="versions")
    authority: Mapped[Optional["Authority"]] = relationship("Authority", back_populates="requirement_versions")
    applicabilities: Mapped[List["RequirementApplicability"]] = relationship("RequirementApplicability", back_populates="requirement_version")
    evidence_mappings: Mapped[List["EvidenceMapping"]] = relationship("EvidenceMapping", back_populates="requirement_version")
    evidence_gaps: Mapped[List["EvidenceGap"]] = relationship("EvidenceGap", back_populates="requirement_version")

    __table_args__ = (
        UniqueConstraint("requirement_id", "version_number", name="uq_req_versions_num"),
        Index(
            "idx_req_versions_vector_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class RequirementApplicability(Base):
    """Binds a versioned requirement to a specific matter and tracks case readiness."""
    __tablename__ = "requirement_applicabilities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_REQUIREMENT_APPLICABILITY),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    requirement_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("requirement_versions.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOT_EVALUATED")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="requirement_applicabilities")
    requirement_version: Mapped["RequirementVersion"] = relationship("RequirementVersion", back_populates="applicabilities")

    __table_args__ = (
        UniqueConstraint("matter_id", "requirement_version_id", name="uq_reqapp_matter_version"),
        Index("idx_reqapp_status", "matter_id", "status"),
    )
