"""
LexMatter AI — Case Supervisor & Routing Engine
Phase 9: LangGraph Multi-Agent Orchestration

Provides deterministic Python routing logic to direct execution across specialist nodes.
"""

from typing import Dict, Any
from backend.app.agents.state import MatterAnalysisState
from backend.app.core.logger import get_logger

logger = get_logger("agents.supervisor")


def route_next(state: MatterAnalysisState) -> str:
    """
    Deterministic Python routing decision function evaluated by the Case Supervisor.
    
    Order of operations:
    1. Loop safety guard check (max_iterations limit)
    2. Evidence Analyst (processes 1 dimension per step until unprocessed_dimensions is empty)
    3. Consistency Analyst (runs once when consistency_check_completed is False)
    4. Research Agent (runs once when research_completed is False)
    5. Verification Agent (runs once when verification_completed is False)
    6. Human Review Interrupt (if requires_human_review is True)
    7. Finish (__end__)
    """
    iteration = state.get("iteration_count", 0)
    max_iters = state.get("max_iterations", 20)
    matter_id = state.get("matter_id", "unknown")

    # 1. Safety Guard against infinite loops
    if iteration >= max_iters:
        logger.warning(f"[SUPERVISOR] Iteration limit reached ({iteration}/{max_iters}) for Matter '{matter_id}'. Escalating to verification or human review.")
        if not state.get("verification_completed", False):
            return "verification_agent"
        return "human_review" if state.get("requires_human_review", False) else "__end__"

    # 2. Phase 1: Evidence Analyst (Process ONE dimension at a time)
    unprocessed = state.get("unprocessed_dimensions", [])
    if len(unprocessed) > 0:
        logger.info(f"[SUPERVISOR] Matter '{matter_id}' [Iteration {iteration+1}] -> Routing to 'evidence_analyst' (Target Dimension: '{unprocessed[0]}', Remaining: {len(unprocessed)})")
        return "evidence_analyst"

    # 3. Phase 2: Consistency Analyst
    if not state.get("consistency_check_completed", False):
        logger.info(f"[SUPERVISOR] Matter '{matter_id}' [Iteration {iteration+1}] -> Routing to 'consistency_analyst'")
        return "consistency_analyst"

    # 4. Phase 3: Research Agent
    if not state.get("research_completed", False):
        logger.info(f"[SUPERVISOR] Matter '{matter_id}' [Iteration {iteration+1}] -> Routing to 'research_agent'")
        return "research_agent"

    # 5. Phase 4: Verification Agent
    if not state.get("verification_completed", False):
        logger.info(f"[SUPERVISOR] Matter '{matter_id}' [Iteration {iteration+1}] -> Routing to 'verification_agent'")
        return "verification_agent"

    # 6. Phase 5: Human Review Gate or Workflow End
    if state.get("requires_human_review", False):
        logger.info(f"[SUPERVISOR] Matter '{matter_id}' -> Human review interrupt triggered.")
        return "human_review"

    logger.info(f"[SUPERVISOR] Matter '{matter_id}' -> All analysis phases complete. Ending workflow.")
    return "__end__"


def supervisor_node(state: MatterAnalysisState) -> Dict[str, Any]:
    """
    Synchronous Supervisor node wrapper that records routing decisions in state.
    """
    next_step = route_next(state)
    logger.debug(f"[SUPERVISOR] Node evaluated. Recorded next step: '{next_step}'")
    return {
        "current_step": "supervisor",
        "next_agent": next_step,
    }


async def async_supervisor_node(state: MatterAnalysisState, db: Any = None) -> Dict[str, Any]:
    """
    Asynchronous Supervisor node wrapper that integrates PostgreSQL case memory.
    Reads prior case memory notes, evaluates routing decisions, and persists progress summary.
    """
    matter_id = state.get("matter_id", "unknown")
    next_step = route_next(state)

    if db is not None:
        try:
            from backend.app.services.memory_service import get_case_memory, upsert_case_memory

            # Read existing case memory for context
            existing_mem = await get_case_memory(db, matter_id, "supervisor_summary")
            if existing_mem:
                logger.info(f"[SUPERVISOR] Loaded case memory for Matter '{matter_id}': key='supervisor_summary'")

            # Record updated progress log in case memory
            unprocessed_cnt = len(state.get("unprocessed_dimensions", []))
            summary_content = (
                f"Iteration: {state.get('iteration_count', 0)}\n"
                f"Next Agent: {next_step}\n"
                f"Unprocessed Dimensions Remaining: {unprocessed_cnt}\n"
                f"Consistency Checked: {state.get('consistency_check_completed', False)}\n"
                f"Research Completed: {state.get('research_completed', False)}\n"
                f"Verification Completed: {state.get('verification_completed', False)}"
            )
            await upsert_case_memory(
                db=db,
                matter_id=matter_id,
                memory_key="supervisor_summary",
                content=summary_content,
                meta_data={
                    "current_step": "supervisor",
                    "next_agent": next_step,
                    "iteration": state.get("iteration_count", 0),
                },
            )
            logger.info(f"[SUPERVISOR] Persisted routing decision memory for Matter '{matter_id}'")
        except Exception as exc:
            logger.warning(f"[SUPERVISOR] Failed to persist case memory for Matter '{matter_id}': {exc}")

    return {
        "current_step": "supervisor",
        "next_agent": next_step,
    }

