"""
LexMatter AI — Evidence Analyst Node
Phase 9: LangGraph Multi-Agent Orchestration

Processes legal requirement dimensions one by one for a given matter.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.agents.state import MatterAnalysisState
from backend.app.services.evidence_service import evidence_service
from backend.app.models.analysis import EvidenceMapping, EvidenceGap
from backend.app.models.audit import AgentRun
from backend.app.core.id_generator import generate_id
from backend.app.core.logger import get_logger

logger = get_logger("agents.evidence_node")


async def evidence_analyst_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Evidence Analyst node execution.
    Pops the next requirement dimension from unprocessed_dimensions,
    evaluates supporting source assertions via evidence_service, and updates state.
    """
    unprocessed = list(state.get("unprocessed_dimensions", []))
    processed = list(state.get("processed_dimensions", []))
    mapped_ids = list(state.get("mapped_evidence_ids", []))
    gap_ids = list(state.get("identified_gap_ids", []))
    iteration = state.get("iteration_count", 0)
    matter_id = state.get("matter_id", "unknown")

    if not unprocessed:
        logger.info(f"[EVIDENCE_ANALYST] No unprocessed dimensions remaining for Matter '{matter_id}'. Node step skipped.")
        return {
            "current_step": "evidence_analyst",
            "current_dimension": None,
            "iteration_count": iteration + 1,
        }

    # Pop one dimension to process
    current_dim = unprocessed.pop(0)
    processed.append(current_dim)
    logger.info(f"[AGENT REQUEST] [EVIDENCE_ANALYST] Matter '{matter_id}' - Evaluating dimension '{current_dim}' (Remaining unprocessed: {len(unprocessed)})")

    # Run evidence service evaluation
    eval_res = await evidence_service.evaluate_matter_evidence(db, matter_id)

    # Query latest generated mappings and gaps for this matter
    map_stmt = select(EvidenceMapping.id).where(EvidenceMapping.matter_id == matter_id)
    map_res = await db.execute(map_stmt)
    new_mapped_ids = list(set(mapped_ids + [r for r in map_res.scalars().all()]))

    gap_stmt = select(EvidenceGap.id).where(EvidenceGap.matter_id == matter_id)
    gap_res = await db.execute(gap_stmt)
    new_gap_ids = list(set(gap_ids + [r for r in gap_res.scalars().all()]))

    logger.info(f"[AGENT RESPONSE] [EVIDENCE_ANALYST] Matter '{matter_id}' - Completed evaluation for '{current_dim}' | Total Mappings: {len(new_mapped_ids)}, Total Gaps: {len(new_gap_ids)}")

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentRun(
        id=log_id,
        matter_id=matter_id,
        agent_name="EvidenceAnalyst",
        status="COMPLETED",
        input_payload={"current_dimension": current_dim, "iteration": iteration},
        output_payload={"eval_result": eval_res, "mappings_count": len(new_mapped_ids), "gaps_count": len(new_gap_ids)},
        model_used="rule_engine",
    )
    db.add(audit_log)
    await db.flush()

    audit_ids = list(state.get("audit_log_ids", [])) + [log_id]

    return {
        "unprocessed_dimensions": unprocessed,
        "processed_dimensions": processed,
        "current_dimension": current_dim,
        "mapped_evidence_ids": new_mapped_ids,
        "identified_gap_ids": new_gap_ids,
        "current_step": "evidence_analyst",
        "iteration_count": iteration + 1,
        "audit_log_ids": audit_ids,
    }
