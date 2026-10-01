"""
LexMatter AI — Case-Scoped Memory Unit Test Suite
"""

import pytest
from backend.app.core.db import init_db, AsyncSessionLocal
from backend.app.core.id_generator import generate_id, PREFIX_CASE_MEMORY, PREFIX_MATTER
from backend.app.models.source import Matter
from backend.app.models.memory import CaseMemory
from backend.app.services.memory_service import (
    upsert_case_memory,
    get_case_memory,
    list_case_memories,
    delete_case_memory,
)
from backend.app.agents.tools.memory_tools import (
    tool_read_case_memory,
    tool_write_case_memory,
    tool_list_case_memories,
    tool_delete_case_memory,
)
from backend.app.agents.supervisor import async_supervisor_node
from backend.app.agents.state import create_initial_matter_state


def test_case_memory_id_prefix():
    """Verify that generated CaseMemory IDs have 'mem_' prefix and correct length."""
    mem_id = generate_id(PREFIX_CASE_MEMORY)
    assert mem_id.startswith("mem_")
    assert len(mem_id) == 30  # "mem_" (4 chars) + 26 ULID chars


def test_case_memory_model_instantiation():
    """Verify CaseMemory model instance creation."""
    mem = CaseMemory(
        id=generate_id(PREFIX_CASE_MEMORY),
        matter_id="mat_test_001",
        memory_key="supervisor_summary",
        content="Analyzed 2 documents. 1 gap remaining.",
        meta_data={"iteration": 1},
    )
    assert mem.id.startswith("mem_")
    assert mem.matter_id == "mat_test_001"
    assert mem.memory_key == "supervisor_summary"
    assert "Analyzed 2 documents" in mem.content
    assert mem.meta_data["iteration"] == 1


@pytest.mark.asyncio
async def test_case_memory_service_and_tools():
    """Test full CRUD operations in memory service and agent tools."""
    await init_db()
    async with AsyncSessionLocal() as db:
        matter_id = generate_id(PREFIX_MATTER)
        matter = Matter(id=matter_id, title="Memory Test Matter", matter_type="IMMIGRATION", case_type="L1B")
        db.add(matter)
        await db.commit()

        # 1. Write memory note via tool
        write_res = await tool_write_case_memory(
            db=db,
            matter_id=matter_id,
            memory_key="evidence_gaps",
            content="Missing W2 tax return for year 2024.",
        )
        assert "Successfully saved memory 'evidence_gaps'" in write_res

        # 2. Read memory note via tool
        read_res = await tool_read_case_memory(
            db=db,
            matter_id=matter_id,
            memory_key="evidence_gaps",
        )
        assert "Missing W2 tax return" in read_res

        # 3. List memories via tool
        list_res = await tool_list_case_memories(
            db=db,
            matter_id=matter_id,
        )
        assert "evidence_gaps" in list_res

        # 4. Upsert (update) memory note
        update_mem = await upsert_case_memory(
            db=db,
            matter_id=matter_id,
            memory_key="evidence_gaps",
            content="Resolved: W2 tax return provided in Doc 3.",
        )
        assert update_mem.content == "Resolved: W2 tax return provided in Doc 3."

        # 5. Delete memory note via tool
        del_res = await tool_delete_case_memory(
            db=db,
            matter_id=matter_id,
            memory_key="evidence_gaps",
        )
        assert "Successfully deleted memory 'evidence_gaps'" in del_res

        # 6. Verify deleted
        empty_mem = await get_case_memory(db, matter_id, "evidence_gaps")
        assert empty_mem is None


@pytest.mark.asyncio
async def test_supervisor_async_node_memory_integration():
    """Test async_supervisor_node memory persistence."""
    await init_db()
    async with AsyncSessionLocal() as db:
        matter_id = generate_id(PREFIX_MATTER)
        matter = Matter(id=matter_id, title="Supervisor Memory Test Matter", matter_type="IMMIGRATION", case_type="L1B")
        db.add(matter)
        await db.commit()

        state = create_initial_matter_state(
            matter_id=matter_id,
            unprocessed_dimensions=["dim_specialized_knowledge"],
        )

        # Run supervisor node
        res = await async_supervisor_node(state, db=db)
        assert res["current_step"] == "supervisor"
        assert res["next_agent"] == "evidence_analyst"

        # Verify supervisor summary memory saved in DB
        mem = await get_case_memory(db, matter_id, "supervisor_summary")
        assert mem is not None
        assert "Next Agent: evidence_analyst" in mem.content
