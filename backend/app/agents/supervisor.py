"""
LexMatter AI — Case Supervisor & Routing Engine
Phase 9: LangGraph Multi-Agent Orchestration

Provides deterministic Python routing logic to direct execution across specialist nodes.
"""

from typing import Dict, Any
from backend.app.agents.state import MatterAnalysisState


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

    # 1. Safety Guard against infinite loops
    if iteration >= max_iters:
        if not state.get("verification_completed", False):
            return "verification_agent"
        return "human_review" if state.get("requires_human_review", False) else "__end__"

    # 2. Phase 1: Evidence Analyst (Process ONE dimension at a time)
    unprocessed = state.get("unprocessed_dimensions", [])
    if len(unprocessed) > 0:
        return "evidence_analyst"

    # 3. Phase 2: Consistency Analyst
    if not state.get("consistency_check_completed", False):
        return "consistency_analyst"

    # 4. Phase 3: Research Agent
    if not state.get("research_completed", False):
        return "research_agent"

    # 5. Phase 4: Verification Agent
    if not state.get("verification_completed", False):
        return "verification_agent"

    # 6. Phase 5: Human Review Gate or Workflow End
    if state.get("requires_human_review", False):
        return "human_review"

    return "__end__"


def supervisor_node(state: MatterAnalysisState) -> Dict[str, Any]:
    """
    Supervisor node wrapper that records routing decisions in state.
    """
    next_step = route_next(state)
    return {
        "current_step": "supervisor",
        "next_agent": next_step,
    }
