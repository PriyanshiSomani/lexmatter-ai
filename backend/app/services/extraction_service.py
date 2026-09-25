"""
LexMatter AI — Structured Extraction Engine Service
Extracts Entities, immutable SourceAssertions, and timeline Events from SourceSpans.
"""

import re
from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Page, SourceSpan, DocumentVersion, Document
from backend.app.models.extraction import SourceAssertion, Event
from backend.app.schemas.extraction import ExtractedAssertion, ExtractedEntity, ExtractedEvent
from backend.app.services.entity_resolver_service import entity_resolver_service


class ExtractionService:
    """Orchestrates pattern-based and structured extraction across SourceSpans."""

    # Heuristic regex patterns for deterministic claims
    PATTERNS = {
        "employment_start_date": r"\b(employed|started|joined|commenced)\s+(?:from|on|in)?\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4}|\d{4}-\d{2}-\d{2}|[A-Z][a-z]+\s+\d{4})\b",
        "job_title": r"\b(employed\s+as|title\s+of|position\s+of|role\s+as)\s+([A-Z][A-Za-z0-9\s]{3,40})\b",
        "annual_salary": r"\b(salary|compensation|remuneration)\s+(?:of)?\s*(\$\d{2,3},\d{3}|\$\d{5,6})\b",
        "degree_conferred": r"\b(bachelor|master|doctorate|phd|b\.s\.|m\.s\.)\s+(?:of|in)?\s*([A-Za-z\s]{3,30})\b",
    }

    def extract_from_snippet(self, text_snippet: str) -> Dict[str, List[Any]]:
        """Run pattern extractions on a snippet string.
        
        Returns:
            Dict containing lists of ExtractedEntity, ExtractedAssertion, and ExtractedEvent instances.
        """
        entities: List[ExtractedEntity] = []
        assertions: List[ExtractedAssertion] = []
        events: List[ExtractedEvent] = []

        # 1. Job Title Extraction
        title_match = re.search(self.PATTERNS["job_title"], text_snippet, re.IGNORECASE)
        if title_match:
            title_str = title_match.group(2).strip()
            entities.append(ExtractedEntity(name=title_str, entity_type="ROLE_TITLE"))
            assertions.append(ExtractedAssertion(
                predicate="job_title",
                normalized_value=title_str,
                raw_text=title_match.group(0),
                confidence=0.92,
            ))

        # 2. Employment Start Date Extraction
        date_match = re.search(self.PATTERNS["employment_start_date"], text_snippet, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(2).strip()
            assertions.append(ExtractedAssertion(
                predicate="foreign_employment_start_date",
                normalized_value=date_str,
                raw_text=date_match.group(0),
                confidence=0.95,
            ))
            events.append(ExtractedEvent(
                event_type="EMPLOYMENT_START",
                event_date=date_str,
                description=f"Employment started on {date_str}",
            ))

        # 3. Salary Extraction
        salary_match = re.search(self.PATTERNS["annual_salary"], text_snippet, re.IGNORECASE)
        if salary_match:
            sal_str = salary_match.group(2).strip()
            assertions.append(ExtractedAssertion(
                predicate="annual_salary",
                normalized_value=sal_str,
                raw_text=salary_match.group(0),
                confidence=0.90,
            ))

        return {
            "entities": entities,
            "assertions": assertions,
            "events": events,
        }

    async def process_matter_extractions(self, db: AsyncSession, matter_id: str) -> Dict[str, int]:
        """Extract entities, immutable assertions, and events from all SourceSpans in a matter.
        
        Returns:
            Dict of counts: {"assertions_created": int, "events_created": int, "entities_resolved": int}
        """
        # Fetch all SourceSpans belonging to pages in this matter
        stmt = (
            select(SourceSpan)
            .join(Page, SourceSpan.page_id == Page.id)
            .join(DocumentVersion, Page.document_version_id == DocumentVersion.id)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(Document.matter_id == matter_id)
        )
        result = await db.execute(stmt)
        spans = result.scalars().all()

        assertions_created = 0
        events_created = 0
        entities_count = 0

        for span in spans:
            extracted_batch = self.extract_from_snippet(span.text_snippet)

            # Resolve entities
            resolved_entities: Dict[str, str] = {}
            for ext_ent in extracted_batch["entities"]:
                ent_obj = await entity_resolver_service.resolve_or_create_entity(db, matter_id, ext_ent)
                resolved_entities[ext_ent.name] = ent_obj.id
                entities_count += 1

            # Persist immutable SourceAssertions
            for ext_asrt in extracted_batch["assertions"]:
                assertion = SourceAssertion(
                    matter_id=matter_id,
                    source_span_id=span.id,
                    predicate=ext_asrt.predicate,
                    object_value={
                        "normalized_value": ext_asrt.normalized_value,
                        "raw_text": ext_asrt.raw_text,
                    },
                    confidence=ext_asrt.confidence,
                    extraction_method="REGEX_HEURISTIC",
                    is_immutable=True,
                )
                db.add(assertion)
                assertions_created += 1

            # Persist Event milestones
            for ext_evt in extracted_batch["events"]:
                event_obj = Event(
                    matter_id=matter_id,
                    event_type=ext_evt.event_type,
                    event_date=ext_evt.event_date,
                    description=ext_evt.description,
                    participants=list(resolved_entities.values()),
                )
                db.add(event_obj)
                events_created += 1

        await db.flush()
        return {
            "spans_processed": len(spans),
            "assertions_created": assertions_created,
            "events_created": events_created,
            "entities_resolved": entities_count,
        }


extraction_service = ExtractionService()
