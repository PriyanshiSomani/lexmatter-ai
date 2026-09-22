"""
LexMatter AI — Layer 1: Source Layer ORM Models
Models: Matter, Document, DocumentVersion, Page, SourceSpan
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from backend.app.core.db import Base
from backend.app.core.id_generator import (
    PREFIX_DOCUMENT,
    PREFIX_DOCUMENT_VERSION,
    PREFIX_MATTER,
    PREFIX_PAGE,
    PREFIX_SOURCE_SPAN,
    generate_id,
)


class Matter(Base):
    """Root workspace container for legal cases and document reviews."""
    __tablename__ = "matters"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_MATTER),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    matter_type: Mapped[str] = mapped_column(String(50), nullable=False, default="IMMIGRATION")
    case_type: Mapped[str] = mapped_column(String(50), nullable=False, default="L1B")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    filing_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    matter_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="matter", cascade="all, delete-orphan")
    entities: Mapped[List["Entity"]] = relationship("Entity", back_populates="matter", cascade="all, delete-orphan")
    source_assertions: Mapped[List["SourceAssertion"]] = relationship("SourceAssertion", back_populates="matter", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="matter", cascade="all, delete-orphan")
    canonical_facts: Mapped[List["CanonicalFact"]] = relationship("CanonicalFact", back_populates="matter", cascade="all, delete-orphan")
    relationships: Mapped[List["Relationship"]] = relationship("Relationship", back_populates="matter", cascade="all, delete-orphan")
    conflicts: Mapped[List["Conflict"]] = relationship("Conflict", back_populates="matter", cascade="all, delete-orphan")
    requirement_applicabilities: Mapped[List["RequirementApplicability"]] = relationship("RequirementApplicability", back_populates="matter", cascade="all, delete-orphan")
    evidence_mappings: Mapped[List["EvidenceMapping"]] = relationship("EvidenceMapping", back_populates="matter", cascade="all, delete-orphan")
    findings: Mapped[List["Finding"]] = relationship("Finding", back_populates="matter", cascade="all, delete-orphan")
    evidence_gaps: Mapped[List["EvidenceGap"]] = relationship("EvidenceGap", back_populates="matter", cascade="all, delete-orphan")
    research_issues: Mapped[List["ResearchIssue"]] = relationship("ResearchIssue", back_populates="matter", cascade="all, delete-orphan")
    agent_runs: Mapped[List["AgentRun"]] = relationship("AgentRun", back_populates="matter", cascade="all, delete-orphan")
    human_reviews: Mapped[List["HumanReview"]] = relationship("HumanReview", back_populates="matter", cascade="all, delete-orphan")
    audit_events: Mapped[List["AuditEvent"]] = relationship("AuditEvent", back_populates="matter", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_matters_type_status", "matter_type", "case_type", "status"),
        Index("idx_matters_metadata_gin", "metadata", postgresql_using="gin"),
    )


class Document(Base):
    """Logical document representation within a matter."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_DOCUMENT),
    )
    matter_id: Mapped[str] = mapped_column(String(36), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="UNKNOWN")
    classification_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matter: Mapped["Matter"] = relationship("Matter", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_documents_matter_type", "matter_id", "document_type"),
    )


class DocumentVersion(Base):
    """Immutable physical file version for a document."""
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_DOCUMENT_VERSION),
    )
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, default="application/pdf")
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    uploaded_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    pages: Mapped[List["Page"]] = relationship("Page", back_populates="document_version", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_document_versions_num"),
        Index("idx_document_versions_hash", "file_hash_sha256"),
    )


class Page(Base):
    """Represents a single page within a document version."""
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_PAGE),
    )
    document_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ocr_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    width: Mapped[float] = mapped_column(Float, nullable=False, default=612.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=792.0)
    image_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    document_version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="pages")
    source_spans: Mapped[List["SourceSpan"]] = relationship("SourceSpan", back_populates="page", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("document_version_id", "page_number", name="uq_pages_version_num"),
    )


class SourceSpan(Base):
    """Foundational atom of legal provenance with character offsets, bounding box, and vector embedding."""
    __tablename__ = "source_spans"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: generate_id(PREFIX_SOURCE_SPAN),
    )
    page_id: Mapped[str] = mapped_column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    text_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    bounding_box: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    # Relationships
    page: Mapped["Page"] = relationship("Page", back_populates="source_spans")
    source_assertions: Mapped[List["SourceAssertion"]] = relationship("SourceAssertion", back_populates="source_span")

    __table_args__ = (
        Index("idx_source_spans_hash", "text_hash"),
        Index(
            "idx_source_spans_vector_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
