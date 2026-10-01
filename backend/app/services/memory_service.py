"""
LexMatter AI — Case Memory Service Layer
Provides async CRUD operations for case-scoped memory entries in PostgreSQL.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.models.memory import CaseMemory
from backend.app.core.logger import get_logger

logger = get_logger("services.memory")


async def upsert_case_memory(
    db: AsyncSession,
    matter_id: str,
    memory_key: str,
    content: str,
    meta_data: Optional[Dict[str, Any]] = None,
) -> CaseMemory:
    """
    Create or update a case memory entry in PostgreSQL (Upsert).
    """
    stmt = select(CaseMemory).where(
        CaseMemory.matter_id == matter_id,
        CaseMemory.memory_key == memory_key,
    )
    result = await db.execute(stmt)
    memory_entry = result.scalar_one_or_none()

    if memory_entry:
        memory_entry.content = content
        if meta_data is not None:
            memory_entry.meta_data = meta_data
        logger.info(f"[MEMORY SERVICE] Updated memory '{memory_key}' for Matter '{matter_id}'")
    else:
        memory_entry = CaseMemory(
            matter_id=matter_id,
            memory_key=memory_key,
            content=content,
            meta_data=meta_data or {},
        )
        db.add(memory_entry)
        logger.info(f"[MEMORY SERVICE] Created memory '{memory_key}' for Matter '{matter_id}'")

    await db.commit()
    await db.refresh(memory_entry)
    return memory_entry


async def get_case_memory(
    db: AsyncSession,
    matter_id: str,
    memory_key: str,
) -> Optional[CaseMemory]:
    """
    Fetch a specific memory note for a legal matter.
    """
    stmt = select(CaseMemory).where(
        CaseMemory.matter_id == matter_id,
        CaseMemory.memory_key == memory_key,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_case_memories(
    db: AsyncSession,
    matter_id: str,
) -> List[CaseMemory]:
    """
    Retrieve all memory notes for a legal matter.
    """
    stmt = select(CaseMemory).where(CaseMemory.matter_id == matter_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_case_memory(
    db: AsyncSession,
    matter_id: str,
    memory_key: str,
) -> bool:
    """
    Delete a specific memory note for a legal matter.
    """
    stmt = delete(CaseMemory).where(
        CaseMemory.matter_id == matter_id,
        CaseMemory.memory_key == memory_key,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
