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
    Supervisor node wrapper that records routing decisions in state.
    """
    next_step = route_next(state)
    logger.debug(f"[SUPERVISOR] Node evaluated. Recorded next step: '{next_step}'")
    return {
        "current_step": "supervisor",
        "next_agent": next_step,
    }
