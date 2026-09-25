/**
 * LexMatter AI — Legal Requirement Compliance Matrix Component (Attorney Interactive)
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Info,
  X,
  FileSearch,
  BookOpen,
  ClipboardList,
} from "lucide-react";
import { RequirementItem, EvidenceGapItem, EvidenceMappingItem } from "../lib/api";

interface RequirementMatrixProps {
  requirements: RequirementItem[];
  evidenceGaps: EvidenceGapItem[];
  evidenceMappings: EvidenceMappingItem[];
  onSelectCitation?: (docId?: string, spanId?: string) => void;
}

// Utility function to format raw snake_case dimension identifiers into attorney-friendly titles
const formatDimensionTitle = (raw: string): string => {
  if (!raw) return "General Evidentiary Requirement";
  return raw
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

// Map raw enum statuses to polished single-line attorney badges
const renderStatusBadge = (status: string) => {
  switch (status) {
    case "EVIDENCE_LOCATED":
      return (
        <span className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" /> Verified Evidence
        </span>
      );
    case "PARTIAL_SUPPORT":
      return (
        <span className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 shadow-2xs">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" /> Partial Support
        </span>
      );
    case "POTENTIAL_GAP":
      return (
        <span className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 shadow-2xs">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" /> Potential Gap
        </span>
      );
    default:
      return (
        <span className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
          <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" /> Not Evaluated
        </span>
      );
  }
};

// Recommendation mapper for evidence gaps based on requirement title or dimension
const getRecommendedActionItems = (titleOrDimension: string): string[] => {
  const text = titleOrDimension.toLowerCase();
  if (text.includes("foreign") || text.includes("duration") || text.includes("employment") || text.includes("continuous")) {
    return [
      "Official foreign payroll statements or tax summaries (W-2 equivalent).",
      "Signed verification letter from foreign entity HR detailing continuous employment dates.",
      "Employment contract specifying qualifying capacity abroad.",
    ];
  }
  if (text.includes("specialized") || text.includes("proprietary") || text.includes("advanced") || text.includes("knowledge")) {
    return [
      "Detailed technical support letter from senior engineering or product lead.",
      "Patents, proprietary architecture docs, or copyright registrations.",
      "Internal specialized training completion certificates.",
    ];
  }
  if (text.includes("corporate") || text.includes("ownership") || text.includes("relationship") || text.includes("doing business")) {
    return [
      "Articles of Incorporation / Organization for foreign & domestic entities.",
      "Stock certificates, capitalization tables, or Form 1120 corporate tax returns.",
      "Commercial lease agreements or client invoices proving active business operations.",
    ];
  }
  return [
    "Exhaustive evidentiary documentation corroborating petition assertions.",
    "Sworn corporate affidavit from petitioning company officer.",
  ];
};

export const RequirementMatrix: React.FC<RequirementMatrixProps> = ({
  requirements,
  evidenceGaps,
  evidenceMappings,
  onSelectCitation,
}) => {
  const [expandedReqId, setExpandedReqId] = useState<string | null>(null);
  const [activeModalGap, setActiveModalGap] = useState<EvidenceGapItem | null>(null);

  const toggleReqExpand = (reqId: string) => {
    setExpandedReqId((prev) => (prev === reqId ? null : reqId));
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-4">
      {/* Matrix Header */}
      <div className="flex justify-between items-center pb-3 border-b border-slate-200">
        <div>
          <h3 className="text-xs font-bold text-slate-800 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-600" /> Legal Requirement Compliance Matrix
          </h3>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Click any requirement row to inspect verified source evidence or missing evidence action plans.
          </p>
        </div>
        <span className="text-[11px] font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded border border-slate-200">
          Statute: 8 CFR § 214.2(l)
        </span>
      </div>

      {/* Requirements Interactive Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
              <th className="py-2.5 px-3 w-8"></th>
              <th className="py-2.5 px-3">Statutory Requirement Title</th>
              <th className="py-2.5 px-3">Statutory Citation</th>
              <th className="py-2.5 px-3 text-right">Evaluation Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {requirements.length > 0 ? (
              requirements.map((req) => {
                const isExpanded = expandedReqId === req.id;
                // Filter mappings related to this requirement code/title if any
                const relatedMappings = evidenceMappings.filter((m) =>
                  req.evaluation_dimensions?.includes(m.target_dimension)
                );

                return (
                  <React.Fragment key={req.id}>
                    <tr
                      onClick={() => toggleReqExpand(req.id)}
                      className={`cursor-pointer transition-colors ${
                        isExpanded ? "bg-blue-50/40" : "hover:bg-slate-50/70"
                      }`}
                    >
                      <td className="py-3 px-3 text-slate-400">
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-blue-600" />
                        ) : (
                          <ChevronRight className="w-4 h-4" />
                        )}
                      </td>
                      <td className="py-3 px-3 font-semibold text-slate-800">
                        {req.requirement_title}
                      </td>
                      <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                        {req.statutory_reference || "8 CFR § 214.2(l)"}
                      </td>
                      <td className="py-3 px-3 text-right">{renderStatusBadge(req.status)}</td>
                    </tr>

                    {/* Expandable Evidentiary Accordion Panel */}
                    {isExpanded && (
                      <tr className="bg-slate-50/80">
                        <td colSpan={4} className="p-4 border-b border-slate-200">
                          {relatedMappings.length > 0 ? (
                            /* SCENARIO A: Verified Evidence Mappings Present */
                            <div className="bg-white rounded-md border border-slate-200 p-3.5 space-y-3 shadow-xs">
                              <div className="flex justify-between items-center text-xs font-semibold text-slate-700 border-b border-slate-100 pb-2">
                                <span className="flex items-center gap-1.5 text-blue-800">
                                  <BookOpen className="w-3.5 h-3.5 text-blue-600" />
                                  Verified Evidentiary Support & Source Spans
                                </span>
                                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                                  {relatedMappings.length} Evidence Spans Mapped
                                </span>
                              </div>

                              <div className="space-y-2">
                                {relatedMappings.map((map) => (
                                  <div
                                    key={map.id}
                                    className="p-3 bg-slate-50 rounded border border-slate-200 text-xs flex justify-between items-start gap-3 hover:border-blue-300 transition-colors"
                                  >
                                    <div className="space-y-1">
                                      <div className="flex items-center gap-2">
                                        <span className="font-semibold text-slate-800">
                                          {formatDimensionTitle(map.target_dimension)}
                                        </span>
                                        <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-mono font-medium">
                                          {Math.round(map.relevance_score * 100)}% Relevance Match
                                        </span>
                                      </div>
                                      <p className="text-slate-700 text-[11px] leading-relaxed italic bg-white p-2 rounded border border-slate-200/80">
                                        "{map.analysis_notes || "Verified source assertion extracted from petition documentation."}"
                                      </p>
                                    </div>

                                    {onSelectCitation && (
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          onSelectCitation(undefined, map.source_assertion_id);
                                        }}
                                        className="shrink-0 flex items-center gap-1 text-[11px] font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded-md transition-colors border border-blue-200"
                                      >
                                        Inspect Source <ExternalLink className="w-3 h-3" />
                                      </button>
                                    )}
                                  </div>
                                ))}
                              </div>

                              {req.evaluation_dimensions && req.evaluation_dimensions.length > 0 && (
                                <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                                  <span className="font-semibold text-slate-700">Evaluated Statutory Dimensions:</span>{" "}
                                  {req.evaluation_dimensions.map(formatDimensionTitle).join(" • ")}
                                </div>
                              )}
                            </div>
                          ) : (
                            /* SCENARIO B: Potential Gap / Missing Evidence Action Plan */
                            <div className="bg-amber-50/90 border border-amber-200/90 rounded-lg p-4 space-y-3 shadow-xs">
                              <div className="flex items-center justify-between border-b border-amber-200 pb-2">
                                <span className="font-bold text-amber-950 text-xs flex items-center gap-1.5">
                                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                                  Evidentiary Deficiency & Remedial Action Plan
                                </span>
                                <span className="text-[10px] font-semibold text-rose-800 bg-rose-100 px-2 py-0.5 rounded border border-rose-200">
                                  Action Required Prior to Filing
                                </span>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                                <div className="p-3 bg-white/90 rounded border border-amber-200 space-y-1">
                                  <span className="font-bold text-slate-800 block text-[11px]">
                                    ⚠️ Missing Evidence Analysis:
                                  </span>
                                  <p className="text-slate-700 text-[11px] leading-relaxed">
                                    No affirmative assertions or direct document spans were identified across ingested matter files to substantiate <strong>{req.requirement_title}</strong>.
                                  </p>
                                </div>

                                <div className="p-3 bg-white/90 rounded border border-amber-200 space-y-1">
                                  <span className="font-bold text-slate-800 block text-[11px]">
                                    📜 Statutory Basis & Citation:
                                  </span>
                                  <p className="text-slate-700 text-[11px] leading-relaxed">
                                    <strong>{req.statutory_reference || "8 CFR § 214.2(l)"}</strong> — USCIS regulations mandate explicit evidentiary proof for each required element prior to adjudication.
                                  </p>
                                </div>
                              </div>

                              <div className="bg-white/90 p-3 rounded border border-amber-200 space-y-2">
                                <span className="font-bold text-slate-800 flex items-center gap-1.5 text-xs">
                                  <ClipboardList className="w-3.5 h-3.5 text-emerald-600" />
                                  Recommended Client Evidentiary Request List:
                                </span>
                                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-slate-700">
                                  {getRecommendedActionItems(req.requirement_title).map((action, i) => (
                                    <li key={i} className="flex items-start gap-2 bg-slate-50 p-2 rounded border border-slate-200/80">
                                      <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                                        {i + 1}
                                      </span>
                                      <span>{action}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            ) : (
              <tr>
                <td colSpan={4} className="py-6 px-3 text-center text-slate-400">
                  Standard L-1B statutory requirements loaded.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Guarded Potential Evidence Gaps Section */}
      {evidenceGaps.length > 0 && (
        <div className="pt-4 border-t border-slate-200 space-y-3">
          <div className="flex justify-between items-center">
            <h4 className="text-xs font-bold text-slate-800 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" /> Potential Evidence Gaps (Guarded Phrasing)
            </h4>
            <span className="text-[10px] font-semibold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-200">
              {evidenceGaps.length} Action Items Flagged
            </span>
          </div>

          <div className="space-y-2.5">
            {evidenceGaps.map((gap) => (
              <div
                key={gap.id}
                onClick={() => setActiveModalGap(gap)}
                className="p-3 bg-amber-50/80 border border-amber-200 hover:border-amber-400 rounded-lg text-xs space-y-2 cursor-pointer transition-all shadow-2xs hover:shadow-xs group"
              >
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-amber-950 text-xs">
                      {formatDimensionTitle(gap.dimension)}
                    </span>
                    <span className="text-[10px] font-mono text-amber-700 bg-amber-200/60 px-1.5 py-0.5 rounded">
                      Dim: {gap.dimension}
                    </span>
                  </div>
                  <span className="text-[11px] font-semibold text-amber-800 group-hover:text-amber-950 flex items-center gap-1">
                    Inspect Gap & Remedial Plan <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>

                <p className="text-amber-900 leading-relaxed text-[11px]">
                  Potential evidence gap identified: No direct supporting assertions were located across{" "}
                  <strong>{gap.searched_document_count} ingested document(s)</strong> for this statutory dimension.
                </p>

                <div className="flex items-center justify-between text-[10px] text-amber-700 border-t border-amber-200/60 pt-1.5 mt-1">
                  <span>Guarded Non-Adjudicative Indicator</span>
                  <span className="font-semibold text-amber-900">Click to view recommended attorney action items</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Attorney Legal Deficiency Audit Modal */}
      {activeModalGap && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden space-y-4 animate-in fade-in zoom-in duration-150">
            {/* Modal Header */}
            <div className="bg-amber-50 px-5 py-4 border-b border-amber-200 flex justify-between items-start">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-amber-100 text-amber-800 rounded-lg shrink-0">
                  <FileSearch className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-amber-950">
                    Evidentiary Gap Inspection & Attorney Action Plan
                  </h3>
                  <p className="text-xs text-amber-800 mt-0.5">
                    Requirement Dimension: <strong>{formatDimensionTitle(activeModalGap.dimension)}</strong>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveModalGap(null)}
                className="text-amber-800 hover:text-amber-950 p-1 rounded-md hover:bg-amber-200/50 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-5 space-y-4 text-xs">
              {/* Finding Breakdown */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5">
                <span className="font-bold text-slate-800 flex items-center gap-1.5 text-xs">
                  <Info className="w-3.5 h-3.5 text-blue-600" /> Automated Analytical Finding
                </span>
                <p className="text-slate-600 text-[11px] leading-relaxed">
                  During automated matter analysis, {activeModalGap.searched_document_count} ingested petition document(s) were scanned using hybrid vector/keyword search. No affirmative assertions or explicit evidence spans were mapped for <strong>{formatDimensionTitle(activeModalGap.dimension)}</strong>.
                </p>
              </div>

              {/* Recommended Documentation Checklist for Attorney */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-800 flex items-center gap-1.5 text-xs">
                  <ClipboardList className="w-4 h-4 text-emerald-600" /> Recommended Client Evidentiary Request Checklist
                </h4>
                <p className="text-[11px] text-slate-500">
                  To cure this potential gap before USCIS filing, consider requesting the following documentation:
                </p>
                <ul className="space-y-1.5 pl-1">
                  {getRecommendedActionItems(activeModalGap.dimension).map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-[11px] text-slate-700">
                      <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Guarded Legal Disclaimer */}
              <div className="p-2.5 bg-amber-50/60 rounded border border-amber-200/80 text-[10px] text-amber-900 leading-relaxed">
                <strong>NON-ADJUDICATIVE NOTICE:</strong> This analytical finding represents an automated gap indicator intended for attorney review only. It does not constitute binding legal advice or a formal USCIS adjudication determination.
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-5 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setActiveModalGap(null)}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg transition-colors shadow-xs"
              >
                Close Audit Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
