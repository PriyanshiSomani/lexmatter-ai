"""
LexMatter AI — Entity Resolution Service
Normalizes entity surface names to canonical keys and resolves database Entity records.
"""

import re
from typing import Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.extraction import Entity
from backend.app.schemas.extraction import ExtractedEntity


class EntityResolverService:
    """Handles entity canonicalization and matter-level entity deduplication."""

    # Words to strip during canonicalization
    STRIP_NOISE_WORDS = [
        r"\bmr\b", r"\bmrs\b", r"\bms\b", r"\bdr\b",
        r"\binc\b", r"\bcorp\b", r"\bcorporation\b", r"\bllc\b", r"\bltd\b", r"\bpvt\b",
    ]

    def normalize_canonical_name(self, raw_name: str) -> str:
        """Convert a surface entity name to a canonical lowercase search key."""
        clean = raw_name.lower().strip()
        # Remove punctuation except spaces
        clean = re.sub(r"[^\w\s]", "", clean)
        for noise in self.STRIP_NOISE_WORDS:
            clean = re.sub(noise, "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean or raw_name.lower().strip()

    async def resolve_or_create_entity(
        self,
        db: AsyncSession,
        matter_id: str,
        extracted: ExtractedEntity,
    ) -> Entity:
        """Look up an existing entity by canonical name or create a new Entity record."""
        canonical = self.normalize_canonical_name(extracted.name)

        # 1. Search existing matter entities
        stmt = select(Entity).where(
            Entity.matter_id == matter_id,
            Entity.entity_type == extracted.entity_type,
            Entity.canonical_name == canonical,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        # 2. Create new Entity record if not found
        new_entity = Entity(
            matter_id=matter_id,
            name=extracted.name,
            canonical_name=canonical,
            entity_type=extracted.entity_type,
            attributes=extracted.attributes,
        )
        db.add(new_entity)
        await db.flush()
        return new_entity


entity_resolver_service = EntityResolverService()
