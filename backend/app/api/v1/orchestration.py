"""
LexMatter AI — LangGraph Multi-Agent Orchestration API Router
Phase 9: Multi-Agent Workflow Trigger & State Audit API
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.audit import AgentExecutionLog
from app.agents.workflow import run_matter_analysis_workflow

router = APIRouter(tags=["Multi-Agent Orchestration"])


@router.post("/matters/{matter_id}/orchestration/analyze", status_code=status.HTTP_200_OK)
async def analyze_matter_with_agents(
    matter_id: str,
    case_type_code: str = "L1B",
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the autonomous multi-agent LangGraph workflow for a legal matter.
    Coordinates Evidence Analyst, Consistency Analyst, Research Agent, and Verification Agent.
    """
    try:
        final_state = await run_matter_analysis_workflow(db, matter_id=matter_id, case_type_code=case_type_code)

        return {
            "matter_id": matter_id,
            "status": "PAUSED_FOR_REVIEW" if final_state.get("requires_human_review") else "COMPLETED",
            "phase_completion": {
                "evidence_mapping": len(final_state.get("unprocessed_dimensions", [])) == 0,
                "consistency_check": final_state.get("consistency_check_completed", False),
                "research": final_state.get("research_completed", False),
                "verification": final_state.get("verification_completed", False),
            },
            "summary_counts": {
                "mapped_evidence_count": len(final_state.get("mapped_evidence_ids", [])),
                "identified_conflict_count": len(final_state.get("identified_conflict_ids", [])),
                "identified_gap_count": len(final_state.get("identified_gap_ids", [])),
                "total_iterations": final_state.get("iteration_count", 0),
            },
            "human_review": {
                "required": final_state.get("requires_human_review", False),
                "reasons": final_state.get("human_review_reasons", []),
            },
            "audit_log_count": len(final_state.get("audit_log_ids", [])),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow execution failed: {str(e)}",
        )


@router.get("/matters/{matter_id}/orchestration/logs")
async def get_matter_agent_logs(
    matter_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the execution audit history for all agents that ran on a matter.
    """
    try:
        stmt = (
            select(AgentExecutionLog)
            .where(AgentExecutionLog.matter_id == matter_id)
            .order_by(AgentExecutionLog.timestamp.asc())
        )
        res = await db.execute(stmt)
        logs = res.scalars().all()

        return [
            {
                "id": log.id,
                "matter_id": log.matter_id,
                "agent_name": log.agent_name,
                "action": log.action,
                "input_state": log.input_state,
                "output_state": log.output_state,
                "execution_status": log.execution_status,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agent audit logs: {str(e)}",
        )
