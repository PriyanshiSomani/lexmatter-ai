"""
LexMatter AI — Briefing & Report Generation Schemas
Phase 10: Briefing & Report Generation
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ReportExportFormat(str, Enum):
    MARKDOWN = "MARKDOWN"
    PDF = "PDF"
    JSON = "JSON"


class CitationItem(BaseModel):
    source_span_id: str
    document_title: str
    page_number: Optional[int] = None
    snippet: str


class ReportSection(BaseModel):
    section_id: str
    title: str
    content_markdown: str
    citations: List[CitationItem] = Field(default_factory=list)
    status_badge: Optional[str] = None


class BriefingReportSchema(BaseModel):
    report_id: str
    matter_id: str
    case_type_code: str
    generated_at: datetime
    title: str
    executive_summary: str
    sections: List[ReportSection]
    non_adjudicative_disclaimer: str = Field(
        default=(
            "NOTICE: This briefing report is generated for attorney review and informational purposes only. "
            "All findings, potential evidence gaps, and cross-document contradiction flags represent automated "
            "analytical indicators and do NOT constitute formal legal advice or binding USCIS adjudication decisions."
        )
    )
    mapped_evidence_count: int
    identified_conflict_count: int
    identified_gap_count: int
    full_markdown: str


class ReportGenerationRequest(BaseModel):
    case_type_code: str = "L1B"
    include_audit_trail: bool = True
    export_format: ReportExportFormat = ReportExportFormat.MARKDOWN
