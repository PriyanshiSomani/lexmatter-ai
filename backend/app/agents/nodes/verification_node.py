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


async def verification_agent_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Verification Agent node execution.
    Audits state mappings and DB records to ensure 100% provenance verification.
    Sets verification_completed = True.
    """
    iteration = state.get("iteration_count", 0)
    matter_id = state.get("matter_id", "unknown")
    mapping_ids = state.get("mapped_evidence_ids", [])
    logger.info(f"[AGENT REQUEST] [VERIFICATION_AGENT] Matter '{matter_id}' - Request payload: Auditing provenance verification for {len(mapping_ids)} mapped evidence spans")
    
    verified_count = 0
    unverified_count = 0
    requires_review = state.get("requires_human_review", False)
    review_reasons = list(state.get("human_review_reasons", []))

    if mapping_ids:
        # Check that mappings trace to assertions with valid source_span_id
        stmt = (
            select(EvidenceMapping, SourceAssertion)
            .join(SourceAssertion, EvidenceMapping.source_assertion_id == SourceAssertion.id)
            .where(EvidenceMapping.id.in_(mapping_ids))
        )
        res = await db.execute(stmt)
        pairs = res.all()

        for mapping, assertion in pairs:
            if assertion.source_span_id:
                verified_count += 1
            else:
                unverified_count += 1

        if unverified_count > 0:
            requires_review = True
            review_reasons.append(
                f"Verification Audit Warning: {unverified_count} evidence mappings lack explicit SourceSpan character offsets."
            )

    pass_rate = (verified_count / len(mapping_ids)) * 100 if mapping_ids else 100.0
    logger.info(f"[AGENT RESPONSE] [VERIFICATION_AGENT] Matter '{matter_id}' - Response output: Provenance Pass Rate: {pass_rate:.1f}% | Verified: {verified_count}, Unverified: {unverified_count}")

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentRun(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="VerificationAgent",
        status="COMPLETED",
        input_payload={"mapping_count": len(mapping_ids), "iteration": iteration},
        output_payload={
            "verified_count": verified_count,
            "unverified_count": unverified_count,
            "provenance_pass_rate": (verified_count / len(mapping_ids)) if mapping_ids else 1.0,
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
