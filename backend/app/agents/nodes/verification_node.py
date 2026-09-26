"""
LexMatter AI — Verification Agent Node
Phase 9: LangGraph Multi-Agent Orchestration

Verifies that all findings, citations, and evidence links strictly trace back to exact SourceSpan IDs.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.agents.state import MatterAnalysisState
from backend.app.models.analysis import EvidenceMapping
from backend.app.models.extraction import SourceAssertion
from backend.app.models.audit import AgentRun
from backend.app.core.id_generator import generate_id
from backend.app.core.logger import get_logger

logger = get_logger("agents.verification_node")


from backend.app.services.evidence_service import evidence_service
from backend.app.models.source import SourceSpan
from backend.app.models.legal import RequirementApplicability, Requirement


async def verification_agent_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Verification Agent node execution.
    Audits state mappings and DB records using a 4-Tier Verification Hierarchy:
      - Level 1: Provenance Metadata Check (source_span_id non-null & exists)
      - Level 2: Offset Integrity Check (start_char < end_char, text_snippet present)
      - Level 3: Semantic Claim Alignment Check (boilerplate filtering & keyword/dimension entailment)
      - Level 4: Statutory Relevance Audit (validates requirement coverage status)
    Sets verification_completed = True.
    """
    iteration = state.get("iteration_count", 0)
    matter_id = state.get("matter_id", "unknown")
    mapping_ids = state.get("mapped_evidence_ids", [])
    logger.info(f"[AGENT REQUEST] [VERIFICATION_AGENT] Matter '{matter_id}' - Auditing 4-level verification for {len(mapping_ids)} mapped evidence spans")

    l1_passed = 0
    l2_passed = 0
    l3_passed = 0
    l4_passed = 0
    failed_mappings = 0

    requires_review = state.get("requires_human_review", False)
    review_reasons = list(state.get("human_review_reasons", []))
    req_rows = []

    if mapping_ids:
        # Fetch EvidenceMapping, SourceAssertion, and SourceSpan
        stmt = (
            select(EvidenceMapping, SourceAssertion, SourceSpan)
            .join(SourceAssertion, EvidenceMapping.source_assertion_id == SourceAssertion.id)
            .outerjoin(SourceSpan, SourceAssertion.source_span_id == SourceSpan.id)
            .where(EvidenceMapping.id.in_(mapping_ids))
        )
        res = await db.execute(stmt)
        triples = res.all()

        for mapping, assertion, span in triples:
            # Level 1: Provenance Metadata Check
            if not assertion.source_span_id or not span:
                failed_mappings += 1
                requires_review = True
                review_reasons.append(
                    f"Level 1 Audit Failure: EvidenceMapping '{mapping.id}' for target dimension '{mapping.target_dimension}' lacks valid SourceSpan provenance."
                )
                continue
            l1_passed += 1

            # Level 2: Offset & Bound Integrity Check
            if span.start_char is None or span.end_char is None or span.start_char >= span.end_char or not span.text_snippet:
                failed_mappings += 1
                requires_review = True
                review_reasons.append(
                    f"Level 2 Audit Failure: SourceSpan '{span.id}' has invalid character offsets [{span.start_char}..{span.end_char}]."
                )
                continue
            l2_passed += 1

            # Level 3: Semantic Claim Alignment & Boilerplate Audit
            is_boilerplate = evidence_service.is_boilerplate_span(span.text_snippet)
            is_semantically_aligned = evidence_service.match_dimension_keywords(span.text_snippet, mapping.target_dimension)

            if is_boilerplate or not is_semantically_aligned:
                failed_mappings += 1
                requires_review = True
                review_reasons.append(
                    f"Level 3 Semantic Audit Failure: SourceSpan '{span.id}' text snippet ('{span.text_snippet[:60]}...') "
                    f"does not semantically support target dimension '{mapping.target_dimension}'."
                )
                continue
            l3_passed += 1

        # Level 4: Statutory Relevance Audit across Bound Requirements
        from backend.app.models.legal import RequirementVersion
        req_stmt = (
            select(RequirementApplicability, Requirement)
            .join(RequirementVersion, RequirementApplicability.requirement_version_id == RequirementVersion.id)
            .join(Requirement, RequirementVersion.requirement_id == Requirement.id)
            .where(RequirementApplicability.matter_id == matter_id)
        )
        req_res = await db.execute(req_stmt)
        req_rows = req_res.all()

        gaps_or_partial = [
            (app, req) for app, req in req_rows if app.status in ("POTENTIAL_GAP", "PARTIAL_SUPPORT", "NOT_EVALUATED")
        ]
        if gaps_or_partial:
            requires_review = True
            gap_summary = ", ".join([f"{req.code} ({app.status})" for app, req in gaps_or_partial])
            review_reasons.append(
                f"Level 4 Statutory Threshold Warning: {len(gaps_or_partial)} requirements lack complete evidentiary coverage: {gap_summary}."
            )
        else:
            l4_passed = len(req_rows)

    total_checked = len(mapping_ids)
    pass_rate = (l3_passed / total_checked * 100) if total_checked > 0 else 100.0
    logger.info(
        f"[AGENT RESPONSE] [VERIFICATION_AGENT] Matter '{matter_id}' - "
        f"L1 Passed: {l1_passed}, L2 Passed: {l2_passed}, L3 Passed: {l3_passed}, L4 Checked: {len(req_rows)} | "
        f"Semantic Pass Rate: {pass_rate:.1f}%"
    )

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentRun(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="VerificationAgent",
        status="COMPLETED",
        input_payload={"mapping_count": total_checked, "iteration": iteration},
        output_payload={
            "l1_provenance_passed": l1_passed,
            "l2_offsets_passed": l2_passed,
            "l3_semantic_passed": l3_passed,
            "l4_statutory_passed": l4_passed,
            "failed_mappings": failed_mappings,
            "semantic_pass_rate": pass_rate / 100.0,
        },
        model_used="rule_engine",
    )
    db.add(audit_log)
    await db.flush()

    audit_ids = list(state.get("audit_log_ids", [])) + [log_id]

    return {
        "verification_completed": True,
        "requires_human_review": requires_review,
        "human_review_reasons": review_reasons,
        "current_step": "verification_agent",
        "iteration_count": iteration + 1,
        "audit_log_ids": audit_ids,
    }
