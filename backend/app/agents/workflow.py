"""
LexMatter AI — LangGraph Multi-Agent Workflow Engine
Phase 9: LangGraph Multi-Agent Orchestration

Assembles the StateGraph, registers specialist nodes, sets up conditional routing,
and compiles the graph with MemorySaver checkpointer.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from backend.app.agents.state import MatterAnalysisState, create_initial_matter_state
from backend.app.agents.supervisor import route_next, supervisor_node
from backend.app.agents.nodes.evidence_node import evidence_analyst_node
from backend.app.agents.nodes.consistency_node import consistency_analyst_node
from backend.app.agents.nodes.research_node import research_agent_node
from backend.app.agents.nodes.verification_node import verification_agent_node
from backend.app.models.legal import RequirementVersion, RequirementApplicability


# --- Node Wrappers to Inject AsyncSession from RunnableConfig ---

async def call_evidence_analyst(state: MatterAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
    db: AsyncSession = config["configurable"]["db"]
    return await evidence_analyst_node(state, db)


async def call_consistency_analyst(state: MatterAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
    db: AsyncSession = config["configurable"]["db"]
    return await consistency_analyst_node(state, db)


async def call_research_agent(state: MatterAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
    db: AsyncSession = config["configurable"]["db"]
    return await research_agent_node(state, db)


async def call_verification_agent(state: MatterAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
    db: AsyncSession = config["configurable"]["db"]
    return await verification_agent_node(state, db)


# --- Human Review Gate Node ---

async def human_review_node(state: MatterAnalysisState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Human Review interrupt gate. Updates step status.
    """
    return {
        "current_step": "human_review",
        "requires_human_review": True,
    }


# --- Graph Assembly & Compilation ---

def build_matter_analysis_graph():
    """
    Constructs and compiles the StateGraph for matter intelligence analysis.
    """
    builder = StateGraph(MatterAnalysisState)

    # 1. Add Specialist Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("evidence_analyst", call_evidence_analyst)
    builder.add_node("consistency_analyst", call_consistency_analyst)
    builder.add_node("research_agent", call_research_agent)
    builder.add_node("verification_agent", call_verification_agent)
    builder.add_node("human_review", human_review_node)

    # 2. Add Start Edge -> Supervisor
    builder.add_edge(START, "supervisor")

    # 3. Add Conditional Routing Edges from Supervisor
    builder.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "evidence_analyst": "evidence_analyst",
            "consistency_analyst": "consistency_analyst",
            "research_agent": "research_agent",
            "verification_agent": "verification_agent",
            "human_review": "human_review",
            "__end__": END,
        },
    )

    # 4. Add Return Edges from Specialist Nodes back to Supervisor
    builder.add_edge("evidence_analyst", "supervisor")
    builder.add_edge("consistency_analyst", "supervisor")
    builder.add_edge("research_agent", "supervisor")
    builder.add_edge("verification_agent", "supervisor")
    builder.add_edge("human_review", END)

    # 5. Compile with MemorySaver Checkpointer
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


from backend.app.core.logger import get_logger

logger = get_logger("agents.workflow")


# Singleton compiled graph instance
matter_analysis_graph = build_matter_analysis_graph()


async def run_matter_analysis_workflow(
    db: AsyncSession,
    matter_id: str,
    case_type_code: str = "L1B",
    max_iterations: int = 20,
) -> MatterAnalysisState:
    """
    High-level entry point to execute the multi-agent analysis workflow for a legal matter.
    """
    logger.info(f"Initiating multi-agent analysis workflow for Matter '{matter_id}' (Case Type: {case_type_code}, Max Iterations: {max_iterations})...")

    # 1. Fetch requirement dimensions for the case type
    req_stmt = (
        select(RequirementVersion.evaluation_dimensions)
        .join(RequirementApplicability, RequirementApplicability.requirement_version_id == RequirementVersion.id)
        .where(RequirementApplicability.matter_id == matter_id)
    )
    req_res = await db.execute(req_stmt)
    dimension_lists = req_res.scalars().all()

    unprocessed_dims = []
    for dims in dimension_lists:
        if dims:
            unprocessed_dims.extend(dims)
    # Deduplicate while preserving order
    unprocessed_dims = list(dict.fromkeys(unprocessed_dims))

    if not unprocessed_dims:
        # Default fallback dimensions for L1B if no bound applicability found yet
        unprocessed_dims = [
            "us_position_duties_described",
            "continuous_one_year_duration",
            "qualifying_capacity_executive_managerial_or_specialized",
            "proprietary_product_process_or_system",
        ]
        logger.info(f"No bound applicability dimensions found yet for Matter '{matter_id}'. Using default L1B fallback dimensions ({len(unprocessed_dims)} dimensions).")
    else:
        logger.info(f"Fetched {len(unprocessed_dims)} target evaluation dimensions for Matter '{matter_id}': {unprocessed_dims}")

    # 2. Build initial state
    initial_state = create_initial_matter_state(
        matter_id=matter_id,
        case_type_code=case_type_code,
        unprocessed_dimensions=unprocessed_dims,
        max_iterations=max_iterations,
    )

    # 3. Configure execution context
    config = {
        "configurable": {
            "thread_id": f"matter_{matter_id}",
            "db": db,
        }
    }

    # 4. Invoke LangGraph workflow
    logger.info(f"Executing LangGraph state graph for Matter '{matter_id}'...")
    final_state = await matter_analysis_graph.ainvoke(initial_state, config=config)

    logger.info(
        f"Multi-agent workflow execution completed for Matter '{matter_id}' "
        f"[Total Iterations: {final_state.get('iteration_count')}, "
        f"Mapped Evidence: {len(final_state.get('mapped_evidence_ids', []))}, "
        f"Conflicts: {len(final_state.get('identified_conflict_ids', []))}, "
        f"Gaps: {len(final_state.get('identified_gap_ids', []))}, "
        f"Human Review Required: {final_state.get('requires_human_review')}]"
    )
    return final_state
