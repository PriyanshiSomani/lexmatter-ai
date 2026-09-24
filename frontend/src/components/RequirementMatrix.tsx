/**
 * LexMatter AI — Legal Requirement Compliance Matrix Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React from "react";
import { ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2 } from "lucide-react";
import { RequirementItem, EvidenceGapItem, EvidenceMappingItem } from "../lib/api";

interface RequirementMatrixProps {
  requirements: RequirementItem[];
  evidenceGaps: EvidenceGapItem[];
  evidenceMappings: EvidenceMappingItem[];
  onSelectSpan?: (spanId: string) => void;
}

export const RequirementMatrix: React.FC<RequirementMatrixProps> = ({
  requirements,
  evidenceGaps,
  evidenceMappings,
  onSelectSpan,
}) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-4">
      <div className="flex justify-between items-center pb-3 border-b border-slate-200">
        <h3 className="text-xs font-semibold text-slate-800 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" /> Legal Requirement Compliance Matrix
        </h3>
        <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
          Statute: 8 CFR § 214.2(l)
        </span>
      </div>

      {/* Requirements Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
              <th className="py-2 px-3">Requirement Title</th>
              <th className="py-2 px-3">Statutory Ref</th>
              <th className="py-2 px-3">Status Badge</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {requirements.length > 0 ? (
              requirements.map((req) => (
                <tr key={req.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-2.5 px-3 font-medium text-slate-800">{req.requirement_title}</td>
                  <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">{req.statutory_reference}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold border ${
                        req.status === "EVIDENCE_LOCATED"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : req.status === "PARTIAL_SUPPORT"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-red-50 text-red-700 border-red-200"
                      }`}
                    >
                      {req.status === "EVIDENCE_LOCATED" && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                      {req.status === "PARTIAL_SUPPORT" && <AlertTriangle className="w-3 h-3 text-amber-600" />}
                      {req.status === "POTENTIAL_GAP" && <HelpCircle className="w-3 h-3 text-red-600" />}
                      {req.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="py-4 px-3 text-center text-slate-400">
                  Standard L-1B statutory requirements bound & evaluated.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Guarded Evidence Gaps Section */}
      {evidenceGaps.length > 0 && (
        <div className="pt-3 border-t border-slate-200 space-y-2">
          <h4 className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> Potential Evidence Gaps (Guarded Phrasing)
          </h4>
          <div className="space-y-2">
            {evidenceGaps.map((gap) => (
              <div key={gap.id} className="p-3 bg-amber-50/70 border border-amber-200 rounded text-xs space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-amber-900 font-mono text-[11px]">Dimension: {gap.dimension}</span>
                  <span className="text-[10px] font-bold text-amber-800 bg-amber-200/60 px-1.5 py-0.5 rounded">
                    {gap.status}
                  </span>
                </div>
                <p className="text-amber-800 leading-relaxed text-[11px]">{gap.observation}</p>
                <p className="text-[10px] text-amber-600 italic">Documents Searched: {gap.searched_document_count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
