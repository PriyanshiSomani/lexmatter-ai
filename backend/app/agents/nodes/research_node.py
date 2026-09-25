"""
LexMatter AI — Research Agent Node
Phase 9: LangGraph Multi-Agent Orchestration

Queries primary legal authorities and performs secondary hybrid retrieval across the matter corpus
to investigate flagged EvidenceGap items.
"""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.agents.state import MatterAnalysisState
from backend.app.services.hybrid_search_service import hybrid_search_service
from backend.app.models.analysis import EvidenceGap
from backend.app.models.audit import AgentRun
from backend.app.core.id_generator import generate_id
from backend.app.core.logger import get_logger

logger = get_logger("agents.research_node")


async def research_agent_node(state: MatterAnalysisState, db: AsyncSession) -> Dict[str, Any]:
    """
    Research Agent node execution.
    Inspects flagged EvidenceGaps, runs hybrid search to find potential candidate evidence,
    updates gap records if findings emerge, and sets research_completed = True.
    """
    iteration = state.get("iteration_count", 0)
    matter_id = state.get("matter_id", "unknown")
    gap_ids = state.get("identified_gap_ids", [])
    logger.info(f"[AGENT REQUEST] [RESEARCH_AGENT] Matter '{matter_id}' - Request payload: Investigating {len(gap_ids)} potential evidence gaps via hybrid search")

    gaps_researched = 0
    spans_discovered = 0

    if gap_ids:
        # Fetch potential gaps
        stmt = select(EvidenceGap).where(EvidenceGap.id.in_(gap_ids), EvidenceGap.status == "POTENTIAL_GAP")
        res = await db.execute(stmt)
        potential_gaps = res.scalars().all()

        for gap in potential_gaps:
            gaps_researched += 1
            # Build targeted research query from gap dimension name
            search_query = f"{gap.dimension.replace('_', ' ')} evidence support"
            
            # Execute hybrid search across matter corpus
            search_results = await hybrid_search_service.search_matter_spans(
                db,
                matter_id=matter_id,
                query_text=search_query,
                top_k=3,
            )

            if search_results and search_results[0].score >= 0.70:
                top_hit = search_results[0]
                spans_discovered += 1
                gap.observation += (
                    f" [Research Note: Potential supporting span discovered ({top_hit.span_id}) "
                    f"with relevance score {top_hit.score:.2f}]."
                )

        await db.flush()

    logger.info(f"[AGENT RESPONSE] [RESEARCH_AGENT] Matter '{matter_id}' - Response output: Researched {gaps_researched} gaps | Discovered {spans_discovered} candidate spans")

    # Audit logging
    log_id = generate_id("log")
    audit_log = AgentRun(
        id=log_id,
        matter_id=state["matter_id"],
        agent_name="ResearchAgent",
        status="COMPLETED",
        input_payload={"gap_count": len(gap_ids), "iteration": iteration},
        output_payload={"gaps_researched": gaps_researched, "spans_discovered": spans_discovered},
        model_used="rule_engine",
    )
    db.add(audit_log)
    await db.flush()

    audit_ids = list(state.get("audit_log_ids", [])) + [log_id]

    return {
        "research_completed": True,
        "current_step": "research_agent",
        "iteration_count": iteration + 1,
        "audit_log_ids": audit_ids,
    }
