"""
LexMatter AI — Consistency Analyst Node
Phase 9: LangGraph Multi-Agent Orchestration

Reconciles cross-document assertion pairs and flags contradictory dates, roles, salaries, or entity details.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.agents.state import MatterAnalysisState
from backend.app.services.consistency_service import consistency_service
from backend.app.models.knowledge import Conflict
from backend.app.models.audit import AgentRun
from backend.app.core.id_generator import generate_id


async def consistency_analyst_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Consistency Analyst node execution.
    Runs consistency_service cross-document analysis, records Conflict records,
    and updates state flags.
    """
    iteration = state.get("iteration_count", 0)

    # Execute consistency engine analysis
    result_metrics = await consistency_service.analyze_matter_consistency(db, state["matter_id"])

    # Query all conflict IDs for this matter
    conflict_stmt = select(Conflict).where(Conflict.matter_id == state["matter_id"])
    conflict_res = await db.execute(conflict_stmt)
    conflicts = conflict_res.scalars().all()
    conflict_ids = [c.id for c in conflicts]

    # Check for severe conflicts requiring human review
    high_severity_conflicts = [c for c in conflicts if c.severity == "HIGH"]
    requires_review = state.get("requires_human_review", False)
    review_reasons = list(state.get("human_review_reasons", []))

    if high_severity_conflicts:
        requires_review = True
        review_reasons.append(
            f"Detected {len(high_severity_conflicts)} high-severity cross-document conflicts (e.g. date/employment mismatches)."
        )

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentRun(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="ConsistencyAnalyst",
        status="COMPLETED",
        input_payload={"iteration": iteration},
        output_payload={
            "metrics": result_metrics,
            "total_conflicts": len(conflict_ids),
            "high_severity_count": len(high_severity_conflicts),
        },
        model_used="rule_engine",
    )
    db.add(audit_log)
    await db.flush()

    audit_ids = list(state.get("audit_log_ids", [])) + [log_id]

    return {
        "consistency_check_completed": True,
        "identified_conflict_ids": conflict_ids,
        "requires_human_review": requires_review,
        "human_review_reasons": review_reasons,
        "current_step": "consistency_analyst",
        "iteration_count": iteration + 1,
        "audit_log_ids": audit_ids,
    }
