"""
LexMatter AI — Requirement Engine & Applicability Service
Handles legal requirement seeding, matter binding, and evaluation status tracking.
"""

from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.l1b_requirements_seed import AUTHORITIES_SEED, REQUIREMENTS_SEED
from backend.app.models.legal import Authority, Requirement, RequirementVersion, RequirementApplicability
from backend.app.schemas.legal import RequirementApplicabilitySchema


class RequirementService:
    """Manages legal authorities, requirements seeding, and matter-level requirement applicability."""

    async def seed_l1b_requirements(self, db: AsyncSession) -> Dict[str, int]:
        """Seed official L-1B authorities and requirements into PostgreSQL if not present."""
        authorities_seeded = 0
        requirements_seeded = 0

        # 1. Seed Authorities
        for auth_data in AUTHORITIES_SEED:
            stmt = select(Authority).where(Authority.id == auth_data["id"])
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                auth = Authority(
                    id=auth_data["id"],
                    authority_type=auth_data["authority_type"],
                    citation_title=auth_data["citation_title"],
                    jurisdiction=auth_data["jurisdiction"],
                    source_url=auth_data["source_url"],
                    full_text=auth_data["full_text"],
                    effective_date=auth_data["effective_date"],
                )
                db.add(auth)
                authorities_seeded += 1

        await db.flush()

        # 2. Seed Requirements & RequirementVersions
        for req_data in REQUIREMENTS_SEED:
            stmt = select(Requirement).where(Requirement.code == req_data["code"])
            result = await db.execute(stmt)
            req = result.scalar_one_or_none()

            if not req:
                req = Requirement(
                    code=req_data["code"],
                    case_type=req_data["case_type"],
                    category=req_data["category"],
                    title=req_data["title"],
                )
                db.add(req)
                await db.flush()
                requirements_seeded += 1

            # Version check
            v_stmt = select(RequirementVersion).where(
                RequirementVersion.requirement_id == req.id,
                RequirementVersion.version_number == req_data["version_number"],
            )
            v_result = await db.execute(v_stmt)
            if not v_result.scalar_one_or_none():
                req_version = RequirementVersion(
                    requirement_id=req.id,
                    version_number=req_data["version_number"],
                    authority_id=req_data.get("authority_id"),
                    description=req_data["description"],
                    evaluation_dimensions=req_data["evaluation_dimensions"],
                )
                db.add(req_version)

        await db.flush()
        return {
            "authorities_seeded": authorities_seeded,
            "requirements_seeded": requirements_seeded,
        }

    async def bind_requirements_to_matter(self, db: AsyncSession, matter_id: str) -> int:
        """Bind all active L-1B RequirementVersions to a matter with NOT_EVALUATED status."""
        # Ensure seed data exists first
        await self.seed_l1b_requirements(db)

        # Query all active RequirementVersions
        stmt = select(RequirementVersion)
        result = await db.execute(stmt)
        req_versions = result.scalars().all()

        bound_count = 0
        for rv in req_versions:
            app_stmt = select(RequirementApplicability).where(
                RequirementApplicability.matter_id == matter_id,
                RequirementApplicability.requirement_version_id == rv.id,
            )
            app_res = await db.execute(app_stmt)
            if not app_res.scalar_one_or_none():
                app = RequirementApplicability(
                    matter_id=matter_id,
                    requirement_version_id=rv.id,
                    status="NOT_EVALUATED",
                )
                db.add(app)
                bound_count += 1

        await db.flush()
        return bound_count

    async def get_matter_requirements(self, db: AsyncSession, matter_id: str) -> List[RequirementApplicabilitySchema]:
        """Fetch all bound requirements and evaluation statuses for a matter."""
        # Auto-bind if not bound yet
        await self.bind_requirements_to_matter(db, matter_id)

        stmt = (
            select(RequirementApplicability, RequirementVersion, Requirement)
            .join(RequirementVersion, RequirementApplicability.requirement_version_id == RequirementVersion.id)
            .join(Requirement, RequirementVersion.requirement_id == Requirement.id)
            .where(RequirementApplicability.matter_id == matter_id)
            .order_by(Requirement.code)
        )
        result = await db.execute(stmt)
        rows = result.all()

        output = []
        for app, rv, req in rows:
            output.append(RequirementApplicabilitySchema(
                id=app.id,
                matter_id=app.matter_id,
                requirement_version_id=app.requirement_version_id,
                status=app.status,
                notes=app.notes,
                requirement_code=req.code,
                requirement_title=req.title,
            ))
        return output


requirement_service = RequirementService()
