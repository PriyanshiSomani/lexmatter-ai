/**
 * LexMatter AI — Legal Briefing Report & PDF Exporter Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import { FileDown, FileCode, CheckCircle2, Loader2, Sparkles } from "lucide-react";
import { generateBriefingReport, getPdfReportDownloadUrl, BriefingReportResponse } from "../lib/api";

interface ReportExporterProps {
  matterId: string;
}

export const ReportExporter: React.FC<ReportExporterProps> = ({ matterId }) => {
  const [report, setReport] = useState<BriefingReportResponse | null>(null);
  const [generating, setGenerating] = useState(false);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const rep = await generateBriefingReport(matterId);
      setReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const pdfUrl = getPdfReportDownloadUrl(matterId);

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-3">
      <div className="flex justify-between items-center pb-2 border-b border-slate-200">
        <h3 className="text-xs font-semibold text-slate-800 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" /> Executive Briefing Report & Export
        </h3>
        <div className="flex gap-2">
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium flex items-center gap-1.5 shadow-sm transition-colors"
          >
            {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileCode className="w-3.5 h-3.5" />}
            Synthesize Report
          </button>

          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-medium flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <FileDown className="w-3.5 h-3.5" /> Export PDF
          </a>
        </div>
      </div>

      {report ? (
        <div className="space-y-3">
          <div className="p-3 bg-blue-50/60 border border-blue-200 rounded text-xs space-y-1">
            <p className="font-semibold text-blue-900 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" /> {report.title}
            </p>
            <p className="text-blue-800 text-[11px] leading-relaxed">{report.executive_summary}</p>
          </div>

          <div className="p-3 bg-slate-900 text-slate-100 rounded font-mono text-[11px] max-h-48 overflow-y-auto whitespace-pre-wrap">
            {report.full_markdown}
          </div>
        </div>
      ) : (
        <div className="py-6 text-center text-slate-400 text-xs">
          Click "Synthesize Report" to generate the structured legal briefing Markdown and export formatted PDF.
        </div>
      )}
    </div>
  );
};
