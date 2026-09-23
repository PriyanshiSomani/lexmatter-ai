"""
LexMatter AI — Consistency Engine & Conflict Detection Service
Reconciles immutable SourceAssertions into CanonicalFacts and generates explicit Conflict records.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.extraction import SourceAssertion
from backend.app.models.knowledge import CanonicalFact, Conflict
from backend.app.models.audit import HumanReview, AuditEvent
from backend.app.schemas.knowledge import ConflictResolutionRequest


class ConsistencyService:
    """Detects cross-document contradictions and manages canonical fact state transitions."""

    @staticmethod
    def _determine_conflict_type(predicate: str) -> str:
        """Categorize conflict type based on predicate name."""
        if "date" in predicate:
            return "DATE_MISMATCH"
        elif "title" in predicate or "role" in predicate:
            return "TITLE_MISMATCH"
        elif "salary" in predicate or "compensation" in predicate:
            return "SALARY_MISMATCH"
        return "FACTUAL_CONTRADICTION"

    @staticmethod
    def _determine_severity(predicate: str, conflict_type: str) -> str:
        """Assign conflict severity level."""
        if conflict_type == "DATE_MISMATCH" or "employment" in predicate:
            return "HIGH"
        return "MEDIUM"

    async def analyze_matter_consistency(self, db: AsyncSession, matter_id: str) -> Dict[str, int]:
        """Group matter assertions by subject and predicate, detecting conflicts and updating canonical facts."""
        stmt = select(SourceAssertion).where(SourceAssertion.matter_id == matter_id)
        result = await db.execute(stmt)
        assertions = result.scalars().all()

        # Group assertions by (subject_entity_id, predicate)
        groups: Dict[tuple, List[SourceAssertion]] = {}
        for asrt in assertions:
            subj_id = asrt.subject_entity_id or "UNASSIGNED"
            key = (subj_id, asrt.predicate)
            if key not in groups:
                groups[key] = []
            groups[key].append(asrt)

        conflicts_created = 0
        facts_created = 0

        for (subj_id, predicate), group_asrts in groups.items():
            if subj_id == "UNASSIGNED":
                continue

            # Collect candidate values
            values_map: Dict[str, List[str]] = {}
            candidate_values_payload = []

            for asrt in group_asrts:
                val_str = str(asrt.object_value.get("normalized_value", "")).strip().lower()
                if val_str not in values_map:
                    values_map[val_str] = []
                values_map[val_str].append(asrt.id)

                candidate_values_payload.append({
                    "value": asrt.object_value.get("normalized_value"),
                    "raw_text": asrt.object_value.get("raw_text"),
                    "assertion_id": asrt.id,
                })

            # Fetch or create CanonicalFact
            fact_stmt = select(CanonicalFact).where(
                CanonicalFact.matter_id == matter_id,
                CanonicalFact.subject_entity_id == subj_id,
                CanonicalFact.predicate == predicate,
            )
            fact_res = await db.execute(fact_stmt)
            fact = fact_res.scalar_one_or_none()

            if not fact:
                fact = CanonicalFact(
                    matter_id=matter_id,
                    subject_entity_id=subj_id,
                    predicate=predicate,
                )
                db.add(fact)
                facts_created += 1

            fact.candidate_values = candidate_values_payload

            # Check for conflict (multiple distinct values exist)
            if len(values_map) > 1:
                fact.status = "CONFLICTING"
                fact.canonical_value = None

                # Generate Conflict record if not already generated
                conf_stmt = select(Conflict).where(
                    Conflict.matter_id == matter_id,
                    Conflict.subject_entity_id == subj_id,
                    Conflict.predicate == predicate,
                    Conflict.status == "UNRESOLVED",
                )
                conf_res = await db.execute(conf_stmt)
                if not conf_res.scalar_one_or_none():
                    conflict_type = self._determine_conflict_type(predicate)
                    severity = self._determine_severity(predicate, conflict_type)
                    all_asrt_ids = [a.id for a in group_asrts]

                    conflict = Conflict(
                        matter_id=matter_id,
                        subject_entity_id=subj_id,
                        predicate=predicate,
                        conflict_type=conflict_type,
                        conflicting_assertion_ids=all_asrt_ids,
                        severity=severity,
                        status="UNRESOLVED",
                    )
                    db.add(conflict)
                    conflicts_created += 1
            else:
                # Disagreement absent: Corroborated or Uncontested
                fact.status = "CORROBORATED" if len(group_asrts) > 1 else "UNCONTESTED"
                fact.canonical_value = {"value": group_asrts[0].object_value.get("normalized_value")}

        await db.flush()
        return {
            "assertion_groups_analyzed": len(groups),
            "conflicts_created": conflicts_created,
            "facts_processed": len(groups),
        }

    async def resolve_conflict(
        self,
        db: AsyncSession,
        conflict_id: str,
        payload: ConflictResolutionRequest,
    ) -> Conflict:
        """Resolve a conflict with attorney notes and update the associated CanonicalFact."""
        stmt = select(Conflict).where(Conflict.id == conflict_id)
        res = await db.execute(stmt)
        conflict = res.scalar_one_or_none()

        if not conflict:
            raise ValueError(f"Conflict with ID {conflict_id} not found.")

        # Update Conflict status
        conflict.status = "HUMAN_RESOLVED"
        conflict.resolution_notes = payload.resolution_notes
        conflict.resolved_at = datetime.utcnow()

        # Update associated CanonicalFact
        if conflict.subject_entity_id:
            fact_stmt = select(CanonicalFact).where(
                CanonicalFact.matter_id == conflict.matter_id,
                CanonicalFact.subject_entity_id == conflict.subject_entity_id,
                CanonicalFact.predicate == conflict.predicate,
            )
            fact_res = await db.execute(fact_stmt)
            fact = fact_res.scalar_one_or_none()

            if fact:
                fact.status = "RESOLVED_BY_HUMAN"
                fact.canonical_value = {"value": payload.accepted_value, "resolved_by": payload.reviewer_id}

        # Create HumanReview record
        review = HumanReview(
            matter_id=conflict.matter_id,
            target_type="CONFLICT",
            target_id=conflict.id,
            decision="ACCEPT",
            reviewer_comment=payload.resolution_notes,
            reviewer_id=payload.reviewer_id,
        )
        db.add(review)

        # Log AuditEvent
        audit = AuditEvent(
            matter_id=conflict.matter_id,
            actor_type="USER",
            actor_id=payload.reviewer_id,
            action="CONFLICT_RESOLVED",
            entity_type="Conflict",
            entity_id=conflict.id,
            payload={
                "accepted_value": payload.accepted_value,
                "resolution_notes": payload.resolution_notes,
            }
        )
        db.add(audit)

        await db.flush()
        return conflict


consistency_service = ConsistencyService()
