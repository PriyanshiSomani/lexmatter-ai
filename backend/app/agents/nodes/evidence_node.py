"""
LexMatter AI — Evidence Analyst Node
Phase 9: LangGraph Multi-Agent Orchestration

Processes legal requirement dimensions one by one for a given matter.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.state import MatterAnalysisState
from app.services.evidence_service import evidence_service
from app.models.analysis import EvidenceMapping, EvidenceGap
from app.models.audit import AgentExecutionLog
from app.core.id_generator import generate_id


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

    if not unprocessed:
        return {
            "current_step": "evidence_analyst",
            "current_dimension": None,
            "iteration_count": iteration + 1,
        }

    # Pop one dimension to process
    current_dim = unprocessed.pop(0)
    processed.append(current_dim)

    # Run evidence service evaluation
    eval_res = await evidence_service.evaluate_matter_evidence(db, state["matter_id"])

    # Query latest generated mappings and gaps for this matter
    map_stmt = select(EvidenceMapping.id).where(EvidenceMapping.matter_id == state["matter_id"])
    map_res = await db.execute(map_stmt)
    new_mapped_ids = list(set(mapped_ids + [r for r in map_res.scalars().all()]))

    gap_stmt = select(EvidenceGap.id).where(EvidenceGap.matter_id == state["matter_id"])
    gap_res = await db.execute(gap_stmt)
    new_gap_ids = list(set(gap_ids + [r for r in gap_res.scalars().all()]))

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentExecutionLog(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="EvidenceAnalyst",
        action="EVALUATE_DIMENSION",
        input_state={"current_dimension": current_dim, "iteration": iteration},
        output_state={"eval_result": eval_res, "mappings_count": len(new_mapped_ids), "gaps_count": len(new_gap_ids)},
        execution_status="SUCCESS",
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
