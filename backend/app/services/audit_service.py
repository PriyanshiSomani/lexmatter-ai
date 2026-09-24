"""
LexMatter AI — Audit & Provenance Verification Service
Phase 11: Audit & Provenance Verification Engine

Traces backward lineage graphs (DAGs) and computes hybrid confidence metrics with guardrails.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Document, DocumentChunk, SourceSpan
from app.models.extraction import SourceAssertion
from app.models.knowledge import CanonicalFact, Conflict
from app.models.analysis import EvidenceMapping, EvidenceGap
from app.schemas.audit import (
    ConfidenceMetricsSchema,
    OperationalTier,
    LineageNode,
    LineageNodeType,
    LineageEdge,
    LineageGraphResponse,
)


class AuditService:
    """Service for backward lineage graph traversal and calibrated confidence scoring."""

    @staticmethod
    def calculate_confidence(
        extraction_confidence: float = 1.0,
        resolution_confidence: float = 1.0,
        relevance_confidence: float = 1.0,
    ) -> ConfidenceMetricsSchema:
        """
        Calculates composite confidence score using Weighted Linear Average
        paired with a Minimum Component Guardrail.
        
        Formula:
          C_weighted = 0.40 * relevance + 0.30 * resolution + 0.30 * extraction
          C_min = min(extraction, resolution, relevance)
          If C_min < 0.55 -> C_composite = min(C_weighted, C_min) (Guardrail Triggered)
          Else -> C_composite = C_weighted
        """
        ext = max(0.0, min(1.0, extraction_confidence))
        res = max(0.0, min(1.0, resolution_confidence))
        rel = max(0.0, min(1.0, relevance_confidence))

        c_weighted = (0.40 * rel) + (0.30 * res) + (0.30 * ext)
        c_min = min(ext, res, rel)

        guardrail_triggered = False
        if c_min < 0.55:
            composite = min(c_weighted, c_min)
            guardrail_triggered = True
        else:
            composite = c_weighted

        # Calibrated Operational Tiers
        if composite >= 0.80 and not guardrail_triggered:
            tier = OperationalTier.HIGH
            label = "Eligible for normal processing"
            exp = f"Composite confidence ({composite:.2f}) meets baseline requirements."
        elif composite >= 0.65 and not guardrail_triggered:
            tier = OperationalTier.MEDIUM
            label = "Flagged for optional attorney review"
            exp = f"Composite confidence ({composite:.2f}) is moderate; optional review recommended."
        else:
            tier = OperationalTier.NEEDS_REVIEW
            label = "Requires human review"
            reason = "minimum component guardrail breach" if guardrail_triggered else "low composite score"
            exp = f"Composite confidence ({composite:.2f}) requires human attorney review due to {reason}."

        return ConfidenceMetricsSchema(
            extraction_confidence=round(ext, 4),
            resolution_confidence=round(res, 4),
            relevance_confidence=round(rel, 4),
            composite_confidence=round(composite, 4),
            operational_tier=tier,
            tier_label=label,
            guardrail_triggered=guardrail_triggered,
            explanation=exp,
        )

    async def trace_entity_lineage(
        self,
        db: AsyncSession,
        entity_id: str,
    ) -> LineageGraphResponse:
        """
        Traces backward provenance DAG for any entity ULID down to the root Document and Page.
        """
        now = datetime.utcnow()
        nodes: List[LineageNode] = []
        edges: List[LineageEdge] = []
        matter_id = "UNKNOWN"

        # 1. Attempt EvidenceMapping Lookup
        map_stmt = select(EvidenceMapping).where(EvidenceMapping.id == entity_id)
        map_res = await db.execute(map_stmt)
        mapping = map_res.scalar_one_or_none()

        asrt_id = None
        if mapping:
            matter_id = mapping.matter_id
            asrt_id = mapping.source_assertion_id

            nodes.append(
                LineageNode(
                    node_id=mapping.id,
                    node_type=LineageNodeType.EVIDENCE_MAPPING,
                    label=f"Evidence Mapping: {mapping.target_dimension}",
                    metadata={"relationship": mapping.relationship, "relevance_score": mapping.relevance_score},
                    confidence=self.calculate_confidence(relevance_confidence=mapping.relevance_score or 0.90),
                )
            )

        # 2. Attempt Conflict Lookup if not mapping
        if not mapping:
            conf_stmt = select(Conflict).where(Conflict.id == entity_id)
            conf_res = await db.execute(conf_stmt)
            conflict = conf_res.scalar_one_or_none()

            if conflict:
                matter_id = conflict.matter_id
                asrt_id = conflict.assertion1_id
                nodes.append(
                    LineageNode(
                        node_id=conflict.id,
                        node_type=LineageNodeType.CONFLICT,
                        label=f"Conflict: {conflict.conflict_type}",
                        metadata={"severity": conflict.severity, "status": conflict.status},
                        confidence=self.calculate_confidence(resolution_confidence=0.75),
                    )
                )

        # 3. Trace SourceAssertion
        span_id = None
        if asrt_id:
            asrt_stmt = select(SourceAssertion).where(SourceAssertion.id == asrt_id)
            asrt_res = await db.execute(asrt_stmt)
            asrt = asrt_res.scalar_one_or_none()

            if asrt:
                matter_id = asrt.matter_id
                span_id = asrt.source_span_id
                nodes.append(
                    LineageNode(
                        node_id=asrt.id,
                        node_type=LineageNodeType.SOURCE_ASSERTION,
                        label=f"Source Assertion: {asrt.predicate} -> {asrt.object_value}",
                        metadata={"predicate": asrt.predicate, "subject": asrt.subject_name},
                        confidence=self.calculate_confidence(extraction_confidence=asrt.confidence_score or 0.90),
                    )
                )
                if mapping:
                    edges.append(LineageEdge(source_id=mapping.id, target_id=asrt.id, relationship_type="SUPPORTED_BY"))

        # 4. Trace SourceSpan
        doc_id = None
        if span_id:
            span_stmt = select(SourceSpan).where(SourceSpan.id == span_id)
            span_res = await db.execute(span_stmt)
            span = span_res.scalar_one_or_none()

            if span:
                doc_id = span.document_id
                nodes.append(
                    LineageNode(
                        node_id=span.id,
                        node_type=LineageNodeType.SOURCE_SPAN,
                        label=f"Source Span (Page {span.page_number or 1})",
                        metadata={"char_start": span.start_char_offset, "char_end": span.end_char_offset, "text": span.text_content[:80]},
                    )
                )
                if asrt_id:
                    edges.append(LineageEdge(source_id=asrt_id, target_id=span.id, relationship_type="LOCATED_IN_SPAN"))

        # 5. Trace Root Document
        if doc_id:
            doc_stmt = select(Document).where(Document.id == doc_id)
            doc_res = await db.execute(doc_stmt)
            doc = doc_res.scalar_one_or_none()

            if doc:
                nodes.append(
                    LineageNode(
                        node_id=doc.id,
                        node_type=LineageNodeType.DOCUMENT,
                        label=f"Document: {doc.title}",
                        metadata={"file_type": doc.file_type, "status": doc.status},
                    )
                )
                if span_id:
                    edges.append(LineageEdge(source_id=span_id, target_id=doc.id, relationship_type="EXTRACTED_FROM_DOC"))

        # Fallback node if direct lineage record not found
        if not nodes:
            nodes.append(
                LineageNode(
                    node_id=entity_id,
                    node_type=LineageNodeType.SOURCE_ASSERTION,
                    label=f"Entity {entity_id}",
                )
            )

        overall_conf = self.calculate_confidence()

        return LineageGraphResponse(
            root_entity_id=entity_id,
            matter_id=matter_id,
            generated_at=now,
            nodes=nodes,
            edges=edges,
            overall_confidence=overall_conf,
            provenance_verified=len(nodes) >= 3,
        )


audit_service = AuditService()
