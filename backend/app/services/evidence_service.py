"""
LexMatter AI — Evidence Intelligence Engine & Gap Analysis Service
Maps SourceAssertions to RequirementVersion dimensions and detects evidentiary gaps.
"""

from typing import Any, Dict, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Document, DocumentVersion
from backend.app.models.extraction import SourceAssertion
from backend.app.models.legal import RequirementVersion, RequirementApplicability, Requirement
from backend.app.models.analysis import EvidenceMapping, EvidenceGap
from backend.app.services.requirement_service import requirement_service


class EvidenceService:
    """Evaluates evidence coverage across legal requirements and detects potential evidence gaps."""

    # Heuristic mapping dictionary connecting assertion predicates to requirement dimensions
    PREDICATE_DIMENSION_MAP = {
        "job_title": "us_position_duties_described",
        "foreign_employment_start_date": "continuous_one_year_duration",
        "annual_salary": "qualifying_capacity_executive_managerial_or_specialized",
        "specialized_tool_used": "proprietary_product_process_or_system",
    }

    async def evaluate_matter_evidence(self, db: AsyncSession, matter_id: str) -> Dict[str, Any]:
        """Evaluate matter assertions against requirement dimensions and generate EvidenceMappings and EvidenceGaps."""
        # Ensure requirements are bound to matter
        await requirement_service.bind_requirements_to_matter(db, matter_id)

        # 1. Count total documents in matter
        doc_count_stmt = select(func.count(Document.id)).where(Document.matter_id == matter_id)
        doc_count_res = await db.execute(doc_count_stmt)
        searched_docs = doc_count_res.scalar() or 0

        # 2. Fetch all matter assertions
        asrt_stmt = select(SourceAssertion).where(SourceAssertion.matter_id == matter_id)
        asrt_res = await db.execute(asrt_stmt)
        assertions = asrt_res.scalars().all()

        # 3. Fetch bound requirement applicabilities
        reqapp_stmt = (
            select(RequirementApplicability, RequirementVersion, Requirement)
            .join(RequirementVersion, RequirementApplicability.requirement_version_id == RequirementVersion.id)
            .join(Requirement, RequirementVersion.requirement_id == Requirement.id)
            .where(RequirementApplicability.matter_id == matter_id)
        )
        reqapp_res = await db.execute(reqapp_stmt)
        rows = reqapp_res.all()

        mappings_created = 0
        gaps_created = 0

        # 4. Evaluate each requirement
        for app, req_version, req in rows:
            dimensions = req_version.evaluation_dimensions or []
            dimension_support_count: Dict[str, int] = {dim: 0 for dim in dimensions}

            # Map assertions to requirement dimensions
            for asrt in assertions:
                matched_dim = self.PREDICATE_DIMENSION_MAP.get(asrt.predicate)
                if matched_dim and matched_dim in dimension_support_count:
                    dimension_support_count[matched_dim] += 1

                    # Create EvidenceMapping if not existing
                    map_stmt = select(EvidenceMapping).where(
                        EvidenceMapping.matter_id == matter_id,
                        EvidenceMapping.source_assertion_id == asrt.id,
                        EvidenceMapping.requirement_version_id == req_version.id,
                    )
                    map_res = await db.execute(map_stmt)
                    if not map_res.scalar_one_or_none():
                        ev_mapping = EvidenceMapping(
                            matter_id=matter_id,
                            source_assertion_id=asrt.id,
                            requirement_version_id=req_version.id,
                            relationship="SUPPORTS",
                            target_dimension=matched_dim,
                            relevance_score=0.95,
                            analysis_notes=f"Source assertion for '{asrt.predicate}' supports requirement dimension '{matched_dim}'.",
                        )
                        db.add(ev_mapping)
                        mappings_created += 1

            # Detect EvidenceGaps for dimensions with 0 supporting evidence
            for dim, count in dimension_support_count.items():
                if count == 0:
                    gap_stmt = select(EvidenceGap).where(
                        EvidenceGap.matter_id == matter_id,
                        EvidenceGap.requirement_version_id == req_version.id,
                        EvidenceGap.dimension == dim,
                    )
                    gap_res = await db.execute(gap_stmt)
                    if not gap_res.scalar_one_or_none():
                        gap = EvidenceGap(
                            matter_id=matter_id,
                            requirement_version_id=req_version.id,
                            dimension=dim,
                            status="POTENTIAL_GAP",
                            observation=(
                                f"Potential evidence gap detected for requirement '{req.title}' "
                                f"(Dimension: {dim}). A total of {searched_docs} documents were searched, "
                                f"and no direct supporting assertions were identified."
                            ),
                            searched_document_count=searched_docs,
                        )
                        db.add(gap)
                        gaps_created += 1

            # Update RequirementApplicability status
            supported_dims = sum(1 for c in dimension_support_count.values() if c > 0)
            if supported_dims == len(dimensions) and len(dimensions) > 0:
                app.status = "EVIDENCE_LOCATED"
            elif supported_dims > 0:
                app.status = "PARTIAL_SUPPORT"
            else:
                app.status = "POTENTIAL_GAP"

        await db.flush()
        return {
            "requirements_evaluated": len(rows),
            "mappings_created": mappings_created,
            "gaps_created": gaps_created,
            "searched_document_count": searched_docs,
        }


evidence_service = EvidenceService()
