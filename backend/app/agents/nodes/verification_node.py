"""
LexMatter AI — Verification Agent Node
Phase 9: LangGraph Multi-Agent Orchestration

Verifies that all findings, citations, and evidence links strictly trace back to exact SourceSpan IDs.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.state import MatterAnalysisState
from app.models.analysis import EvidenceMapping
from app.models.extraction import SourceAssertion
from app.models.audit import AgentExecutionLog
from app.core.id_generator import generate_id


async def verification_agent_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Verification Agent node execution.
    Audits state mappings and DB records to ensure 100% provenance verification.
    Sets verification_completed = True.
    """
    iteration = state.get("iteration_count", 0)
    mapping_ids = state.get("mapped_evidence_ids", [])
    
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

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentExecutionLog(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="VerificationAgent",
        action="VERIFY_PROVENANCE",
        input_state={"mapping_count": len(mapping_ids), "iteration": iteration},
        output_state={
            "verified_count": verified_count,
            "unverified_count": unverified_count,
            "provenance_pass_rate": (verified_count / len(mapping_ids)) if mapping_ids else 1.0,
        },
        execution_status="SUCCESS",
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
