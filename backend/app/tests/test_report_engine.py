"""
LexMatter AI — Phase 10 Briefing & Report Generation Unit Tests
"""

from datetime import datetime
from app.schemas.report import BriefingReportSchema, ReportSection, CitationItem, ReportExportFormat
from app.services.report_service import report_service


def test_report_schema_defaults_and_disclaimer():
    """Verify BriefingReportSchema disclaimer and section structure."""
    section = ReportSection(
        section_id="sec_01",
        title="1. Matter Overview",
        content_markdown="Sample overview content",
        citations=[
            CitationItem(
                source_span_id="span_01",
                document_title="Support_Letter.pdf",
                page_number=1,
                snippet="Sample evidence text",
            )
        ],
        status_badge="EVALUATED",
    )

    report = BriefingReportSchema(
        report_id="rep_01",
        matter_id="mat_01",
        case_type_code="L1B",
        generated_at=datetime.utcnow(),
        title="Legal Briefing Report: Matter 01",
        executive_summary="Sample executive summary",
        sections=[section],
        mapped_evidence_count=1,
        identified_conflict_count=0,
        identified_gap_count=0,
        full_markdown="# Legal Briefing Report\nSample content",
    )

    assert report.report_id == "rep_01"
    assert "NOTICE: This briefing report is generated for attorney review" in report.non_adjudicative_disclaimer
    assert len(report.sections) == 1
    assert report.sections[0].citations[0].source_span_id == "span_01"


def test_pdf_export_generation():
    """Verify PyMuPDF PDF binary rendering for BriefingReportSchema."""
    section = ReportSection(
        section_id="sec_01",
        title="1. Matter Overview",
        content_markdown="Sample test content for PDF generation",
    )

    report = BriefingReportSchema(
        report_id="rep_test_01",
        matter_id="mat_test_01",
        case_type_code="L1B",
        generated_at=datetime.utcnow(),
        title="Test Briefing PDF Export",
        executive_summary="Executive summary sample for PDF export",
        sections=[section],
        mapped_evidence_count=2,
        identified_conflict_count=1,
        identified_gap_count=1,
        full_markdown="# Test Report Title",
    )

    pdf_bytes = report_service.export_report_pdf(report)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
