"""
LexMatter AI — Evidence Intelligence Engine & Gap Analysis Service
Maps SourceAssertions to RequirementVersion dimensions and detects evidentiary gaps.
"""

from typing import Any, Dict, List
import re
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan
from backend.app.models.extraction import SourceAssertion
from backend.app.models.legal import RequirementVersion, RequirementApplicability, Requirement
from backend.app.models.analysis import EvidenceMapping, EvidenceGap, Finding
from backend.app.models.knowledge import Conflict
from backend.app.services.requirement_service import requirement_service


class EvidenceService:
    """Evaluates evidence coverage across legal requirements and detects potential evidence gaps."""

    # Heuristic mapping dictionary connecting assertion predicates to requirement dimensions
    PREDICATE_DIMENSION_MAP = {
        "job_title": "us_position_duties_described",
        "foreign_employment_start_date": "continuous_one_year_duration",
        "annual_salary": "qualifying_capacity_executive_managerial_or_specialized",
        "specialized_tool_used": "proprietary_product_process_or_system",
        "academic_degree": "education_records_present",
        "corporate_relationship": "qualifying_corporate_ownership_relationship",
    }

    # Keyword mappings connecting evaluation dimensions to key text terms
    DIMENSION_KEYWORDS: Dict[str, List[str]] = {
        "qualifying_foreign_entity_exists": ["foreign", "parent", "subsidiary", "affiliate", "branch", "ltd", "limited", "gmbh", "pvt", "employer"],
        "qualifying_us_entity_exists": ["u.s.", "united states", "petitioner", "corp", "inc", "llc", "company", "employer"],
        "qualifying_corporate_ownership_relationship": ["corporate", "relationship", "ownership", "wholly owned", "parent", "subsidiary", "affiliate", "branch", "shareholder", "100%"],
        "active_business_us": ["active", "business", "doing business", "operations", "office", "revenue", "commercial", "u.s."],
        "active_business_foreign": ["active", "business", "doing business", "operations", "foreign office", "international", "revenue", "foreign"],
        "regular_systematic_provision_of_goods_or_services": ["provision", "goods", "services", "commercial", "contracts", "clients", "customers", "systematic", "operations"],
        "qualifying_foreign_employer": ["foreign employer", "employed abroad", "foreign branch", "foreign entity", "employed by"],
        "continuous_one_year_duration": ["continuous", "1 year", "one year", "12 months", "employed from", "employment period", "start date"],
        "within_prior_three_years_window": ["prior three years", "preceding", "three years", "window", "recent employment", "2021", "2022", "2023", "2024"],
        "qualifying_capacity_executive_managerial_or_specialized": ["specialized knowledge", "manager", "executive", "specialist", "engineer", "capacity", "salary"],
        "proprietary_product_process_or_system": ["titan risk engine", "proprietary", "patent", "trade secret", "custom system", "framework", "internal platform", "software"],
        "advanced_expertise_level": ["advanced", "expertise", "expert", "senior", "lead", "mastery", "deep understanding", "specialized"],
        "organizational_or_industry_comparison": ["comparison", "unique", "distinguished", "key contributor", "rare", "industry", "selective", "unavailable", "commercial market", "exclusive", "proprietary"],
        "beneficiary_possession_evidence": ["beneficiary", "experience", "qualifications", "skills", "resume", "cv", "possession"],
        "us_position_duties_described": ["duties", "position", "responsibilities", "proposed role", "u.s. position", "job description", "title"],
        "specialized_knowledge_required_for_role": ["requires", "specialized knowledge", "necessitates", "critical role", "key position", "knowledge required", "leading", "deployment", "principal", "architect"],
        "alignment_with_foreign_experience": ["alignment", "foreign experience", "prior role", "continued involvement", "experience"],
        "education_records_present": ["bachelor", "master", "degree", "university", "diploma", "transcript", "education", "phd"],
        "training_certificates_or_internal_records": ["training", "certificate", "certification", "internal course", "workshop", "record"],
        "prior_project_or_product_contributions": ["project", "product", "contribution", "developed", "built", "designed", "architecture", "lead"],
    }

    async def evaluate_matter_evidence(self, db: AsyncSession, matter_id: str) -> Dict[str, Any]:
        """Evaluate matter assertions against requirement dimensions and generate EvidenceMappings and EvidenceGaps."""
        # Ensure requirements are bound to matter
        await requirement_service.bind_requirements_to_matter(db, matter_id)

        # 1. Count total documents in matter
        doc_count_stmt = select(func.count(Document.id)).where(Document.matter_id == matter_id)
        doc_count_res = await db.execute(doc_count_stmt)
        searched_docs = doc_count_res.scalar() or 0

        # Fetch bound requirement applicabilities
        reqapp_stmt = (
            select(RequirementApplicability, RequirementVersion, Requirement)
            .join(RequirementVersion, RequirementApplicability.requirement_version_id == RequirementVersion.id)
            .join(Requirement, RequirementVersion.requirement_id == Requirement.id)
            .where(RequirementApplicability.matter_id == matter_id)
        )
        reqapp_res = await db.execute(reqapp_stmt)
        rows = reqapp_res.all()

        # Handle 0 documents: Clean slate reset
        if searched_docs == 0:
            await db.execute(delete(EvidenceGap).where(EvidenceGap.matter_id == matter_id))
            await db.execute(delete(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id))
            await db.execute(delete(Conflict).where(Conflict.matter_id == matter_id))
            await db.execute(delete(Finding).where(Finding.matter_id == matter_id))
            await db.execute(
                update(RequirementApplicability)
                .where(RequirementApplicability.matter_id == matter_id)
                .values(status="NOT_EVALUATED", notes=None)
            )
            await db.flush()
            return {
                "requirements_evaluated": len(rows),
                "mappings_created": 0,
                "gaps_created": 0,
                "searched_document_count": 0,
            }

        # Clear stale gaps and mappings prior to re-evaluating remaining documents
        await db.execute(delete(EvidenceGap).where(EvidenceGap.matter_id == matter_id))
        await db.execute(delete(EvidenceMapping).where(EvidenceMapping.matter_id == matter_id))
        await db.flush()

        # 2. Fetch all matter assertions
        asrt_stmt = select(SourceAssertion).where(SourceAssertion.matter_id == matter_id)
        asrt_res = await db.execute(asrt_stmt)
        assertions = asrt_res.scalars().all()

        # Fetch all matter SourceSpans (for hybrid text-span keyword fallback)
        span_stmt = (
            select(SourceSpan)
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(Document.matter_id == matter_id)
        )
        span_res = await db.execute(span_stmt)
        spans = span_res.scalars().all()

        # Index existing assertions by source_span_id
        span_to_asrt: Dict[str, SourceAssertion] = {a.source_span_id: a for a in assertions if a.source_span_id}

        mappings_created = 0
        gaps_created = 0

        # 4. Evaluate each requirement
        for app, req_version, req in rows:
            dimensions = req_version.evaluation_dimensions or []
            dimension_support_count: Dict[str, int] = {dim: 0 for dim in dimensions}

            for dim in dimensions:
                matched_assertion: SourceAssertion | None = None

                # Step 4a: Direct Predicate Matching
                for asrt in assertions:
                    matched_dim = self.PREDICATE_DIMENSION_MAP.get(asrt.predicate)
                    if matched_dim == dim or asrt.predicate == dim:
                        matched_assertion = asrt
                        break

                # Step 4b: Assertion Value / Keyword Matching
                if not matched_assertion:
                    keywords = self.DIMENSION_KEYWORDS.get(dim, [dim.replace("_", " ")])
                    for asrt in assertions:
                        obj_str = str(asrt.object_value).lower()
                        if any(kw.lower() in obj_str for kw in keywords):
                            matched_assertion = asrt
                            break

                # Step 4c: Hybrid SourceSpan Keyword Fallback
                if not matched_assertion and spans:
                    keywords = self.DIMENSION_KEYWORDS.get(dim, [dim.replace("_", " ")])
                    for span in spans:
                        snippet_lower = span.text_snippet.lower()
                        if any(kw.lower() in snippet_lower for kw in keywords):
                            # Reuse existing assertion or create synthesized assertion for this span
                            if span.id in span_to_asrt:
                                matched_assertion = span_to_asrt[span.id]
                            else:
                                new_asrt = SourceAssertion(
                                    matter_id=matter_id,
                                    source_span_id=span.id,
                                    predicate=dim,
                                    object_value={
                                        "normalized_value": span.text_snippet[:120],
                                        "raw_text": span.text_snippet[:250],
                                    },
                                    confidence=0.88,
                                    extraction_method="HYBRID_KEYWORD_SEARCH",
                                    is_immutable=True,
                                )
                                db.add(new_asrt)
                                await db.flush()
                                span_to_asrt[span.id] = new_asrt
                                assertions.append(new_asrt)
                                matched_assertion = new_asrt
                            break

                if matched_assertion:
                    dimension_support_count[dim] += 1

                    # Create EvidenceMapping if not existing
                    map_stmt = select(EvidenceMapping).where(
                        EvidenceMapping.matter_id == matter_id,
                        EvidenceMapping.source_assertion_id == matched_assertion.id,
                        EvidenceMapping.requirement_version_id == req_version.id,
                        EvidenceMapping.target_dimension == dim,
                    )
                    map_res = await db.execute(map_stmt)
                    if not map_res.scalar_one_or_none():
                        ev_mapping = EvidenceMapping(
                            matter_id=matter_id,
                            source_assertion_id=matched_assertion.id,
                            requirement_version_id=req_version.id,
                            relationship="SUPPORTS",
                            target_dimension=dim,
                            relevance_score=0.95,
                            analysis_notes=f"Evidentiary support located for requirement dimension '{dim}'.",
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
            if searched_docs == 0:
                app.status = "NOT_EVALUATED"
            elif supported_dims == len(dimensions) and len(dimensions) > 0:
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

