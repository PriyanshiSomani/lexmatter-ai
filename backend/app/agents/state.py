"""
LexMatter AI — Agent Orchestration State Schema
Phase 9: LangGraph Multi-Agent Orchestration
"""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class MatterAnalysisState(TypedDict):
    """
    Central state container passed across all specialist nodes in the LangGraph workflow.
    Tracks matter context, processing work queues, phase completion flags, evidence snapshots,
    safety iteration counters, and audit log links.
    """
    # --- Matter & Case Context ---
    matter_id: str
    case_type_code: str                  # e.g., "L1B"
    document_ids: List[str]

    # --- Work Queue & Current Work Item ---
    unprocessed_dimensions: List[str]    # e.g., ["l1b_spec_knowledge_prop", "l1b_spec_knowledge_comp"]
    processed_dimensions: List[str]
    current_dimension: Optional[str]     # Active dimension being evaluated

    # --- Phase Completion Flags (Explicit State Tracking) ---
    consistency_check_completed: bool
    research_completed: bool
    verification_completed: bool

    # --- Domain Results Snapshot (Entity IDs) ---
    mapped_evidence_ids: List[str]      # EvidenceMapping IDs generated
    identified_conflict_ids: List[str]  # Conflict IDs detected
    identified_gap_ids: List[str]       # EvidenceGap IDs flagged

    # --- Execution & Safety Controls ---
    current_step: str                    # e.g., "supervisor", "evidence_analyst", etc.
    next_agent: Optional[str]
    iteration_count: int                 # Loop protection counter
    max_iterations: int                  # Hard limit (e.g., 20)

    # --- Human-in-the-Loop (HITL) Controls ---
    requires_human_review: bool
    human_review_reasons: List[str]

    # --- Conversation & Audit Logs ---
    messages: Annotated[List[BaseMessage], add_messages]
    audit_log_ids: List[str]             # Linked AgentExecutionLog IDs


def create_initial_matter_state(
    matter_id: str,
    case_type_code: str = "L1B",
    document_ids: Optional[List[str]] = None,
    unprocessed_dimensions: Optional[List[str]] = None,
    max_iterations: int = 20,
) -> MatterAnalysisState:
    """
    Helper function to initialize a clean MatterAnalysisState for a given legal matter.
    """
    return MatterAnalysisState(
        matter_id=matter_id,
        case_type_code=case_type_code,
        document_ids=document_ids or [],
        unprocessed_dimensions=unprocessed_dimensions or [],
        processed_dimensions=[],
        current_dimension=None,
        consistency_check_completed=False,
        research_completed=False,
        verification_completed=False,
        mapped_evidence_ids=[],
        identified_conflict_ids=[],
        identified_gap_ids=[],
        current_step="init",
        next_agent=None,
        iteration_count=0,
        max_iterations=max_iterations,
        requires_human_review=False,
        human_review_reasons=[],
        messages=[],
        audit_log_ids=[],
    )
