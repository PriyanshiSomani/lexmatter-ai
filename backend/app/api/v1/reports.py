"""
LexMatter AI — Briefing & Report Generation API Router
Phase 10: Briefing & Report Generation
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.db import get_db
from backend.app.schemas.report import BriefingReportSchema, ReportGenerationRequest, ReportExportFormat
from backend.app.services.report_service import report_service

router = APIRouter(tags=["Briefing & Reports"])


@router.post("/matters/{matter_id}/reports/generate", response_model=BriefingReportSchema)
async def generate_matter_report(
    matter_id: str,
    request: ReportGenerationRequest = ReportGenerationRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a comprehensive legal briefing report for a matter, synthesizing requirements,
    evidence mappings, cross-document conflicts, and evidence gaps.
    """
    try:
        report = await report_service.generate_briefing_report(
            db,
            matter_id=matter_id,
            case_type_code=request.case_type_code,
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@router.get("/matters/{matter_id}/reports/export")
async def export_matter_report(
    matter_id: str,
    export_format: ReportExportFormat = ReportExportFormat.MARKDOWN,
    case_type_code: str = "L1B",
    db: AsyncSession = Depends(get_db),
):
    """
    Export a legal briefing report as formatted Markdown or downloadable PDF document.
    """
    try:
        report = await report_service.generate_briefing_report(
            db,
            matter_id=matter_id,
            case_type_code=case_type_code,
        )

        if export_format == ReportExportFormat.PDF:
            pdf_bytes = report_service.export_report_pdf(report)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="LexMatter_Briefing_{matter_id}.pdf"'
                },
            )
        elif export_format == ReportExportFormat.JSON:
            return report
        else:
            # Default Markdown
            return Response(
                content=report.full_markdown,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'inline; filename="LexMatter_Briefing_{matter_id}.md"'
                },
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report export failed: {str(e)}",
        )
