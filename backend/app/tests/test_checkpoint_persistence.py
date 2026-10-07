"""
LexMatter AI — LangGraph Checkpoint Persistence & Resumption Unit Tests
Phase 9 / ADR-015 / Issue #4 Verification
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from backend.app.agents.state import create_initial_matter_state
from backend.app.agents.workflow import (
    get_checkpointer,
    build_matter_analysis_graph,
    route_after_review,
)


@pytest.mark.asyncio
async def test_get_checkpointer_fallback_mode():
    """Verify get_checkpointer resolves a functional checkpointer in SQLite/test environments."""
    checkpointer = await get_checkpointer()
    assert checkpointer is not None


def test_build_matter_analysis_graph_with_custom_checkpointer():
    """Verify graph compiles cleanly with custom checkpointer instances."""
    custom_saver = MemorySaver()
    graph = build_matter_analysis_graph(checkpointer=custom_saver)
    assert graph is not None


def test_route_after_review_logic():
    """Verify post-review conditional routing for accept vs reject decisions."""
    state = create_initial_matter_state(matter_id="mat_test_persist")

    # When review is cleared / accepted -> routes to supervisor for downstream finalization
    state["requires_human_review"] = False
    assert route_after_review(state) == "supervisor"

    # When review is flagged / rejected -> routes to __end__
    state["requires_human_review"] = True
    assert route_after_review(state) == "__end__"
