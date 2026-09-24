"""
LexMatter AI — Phase 9 Multi-Agent Orchestration Unit Tests
"""

from backend.app.agents.state import create_initial_matter_state, MatterAnalysisState
from backend.app.agents.supervisor import route_next


def test_initial_state_creation():
    """Verify initial matter state structure and default flags."""
    state = create_initial_matter_state(
        matter_id="mat_test_01",
        case_type_code="L1B",
        unprocessed_dimensions=["dim_1", "dim_2"],
    )

    assert state["matter_id"] == "mat_test_01"
    assert state["case_type_code"] == "L1B"
    assert state["unprocessed_dimensions"] == ["dim_1", "dim_2"]
    assert state["processed_dimensions"] == []
    assert state["consistency_check_completed"] is False
    assert state["research_completed"] is False
    assert state["verification_completed"] is False
    assert state["requires_human_review"] is False
    assert state["iteration_count"] == 0
    assert state["max_iterations"] == 20


def test_deterministic_routing_sequence():
    """Verify route_next deterministic state transitions through all phases."""
    state = create_initial_matter_state(
        matter_id="mat_test_01",
        unprocessed_dimensions=["dim_1"],
    )

    # Phase 1: Unprocessed dimensions present -> Evidence Analyst
    assert route_next(state) == "evidence_analyst"

    # Move dimension to processed
    state["unprocessed_dimensions"] = []
    state["processed_dimensions"] = ["dim_1"]

    # Phase 2: Consistency check incomplete -> Consistency Analyst
    assert route_next(state) == "consistency_analyst"
    state["consistency_check_completed"] = True

    # Phase 3: Research incomplete -> Research Agent
    assert route_next(state) == "research_agent"
    state["research_completed"] = True

    # Phase 4: Verification incomplete -> Verification Agent
    assert route_next(state) == "verification_agent"
    state["verification_completed"] = True

    # Phase 5: No human review needed -> End
    assert route_next(state) == "__end__"

    # If human review flagged -> Human Review Gate
    state["requires_human_review"] = True
    assert route_next(state) == "human_review"


def test_loop_safety_guard():
    """Verify max iterations cap prevents infinite loops."""
    state = create_initial_matter_state(
        matter_id="mat_test_01",
        unprocessed_dimensions=["dim_infinite"],
        max_iterations=5,
    )
    state["iteration_count"] = 5

    # Should route to verification if not verified yet
    assert route_next(state) == "verification_agent"

    state["verification_completed"] = True
    # Should end if verification completed
    assert route_next(state) == "__end__"
