"""
LexMatter AI — Agent Tools for Case-Scoped Memory
Exposes tool functions for LangGraph and Gemini agents to read/write case memory.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.memory_service import (
    get_case_memory,
    upsert_case_memory,
    list_case_memories,
    delete_case_memory,
)


async def tool_read_case_memory(db: AsyncSession, matter_id: str, memory_key: str) -> str:
    """
    Agent tool to read a specific memory note for a case from PostgreSQL.
    """
    memory = await get_case_memory(db, matter_id, memory_key)
    if not memory:
        return f"No memory found under key '{memory_key}' for matter '{matter_id}'."
    return f"--- MEMORY: {memory_key} (Updated: {memory.updated_at.isoformat()}) ---\n{memory.content}"


async def tool_write_case_memory(
    db: AsyncSession,
    matter_id: str,
    memory_key: str,
    content: str,
    meta_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Agent tool to write or update a memory note for a case in PostgreSQL.
    """
    memory = await upsert_case_memory(db, matter_id, memory_key, content, meta_data)
    return f"Successfully saved memory '{memory_key}' (ID: {memory.id}) for matter '{matter_id}'."


async def tool_list_case_memories(db: AsyncSession, matter_id: str) -> str:
    """
    Agent tool to list all memory keys available for a case.
    """
    memories = await list_case_memories(db, matter_id)
    if not memories:
        return f"No memory entries exist for matter '{matter_id}'."

    output = [f"Found {len(memories)} memory entries for matter '{matter_id}':"]
    for m in memories:
        output.append(f"- {m.memory_key} (Last updated: {m.updated_at.isoformat()})")
    return "\n".join(output)


async def tool_delete_case_memory(db: AsyncSession, matter_id: str, memory_key: str) -> str:
    """
    Agent tool to delete a memory note for a case.
    """
    deleted = await delete_case_memory(db, matter_id, memory_key)
    if deleted:
        return f"Successfully deleted memory '{memory_key}' for matter '{matter_id}'."
    return f"Memory '{memory_key}' did not exist for matter '{matter_id}'."
