/**
 * LexMatter AI — Interactive Human Review Banner Component
 * Phase 12/14: Frontend Integration & Attorney Workflow
 * Renders persistent review decision bar and modal dialog for LangGraph human-in-the-loop gate
 */

"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Edit3,
  Loader2,
  Info,
  X,
  FileCheck,
} from "lucide-react";
import { submitHumanReview, HumanReviewDecisionResponse } from "../lib/api";

interface HumanReviewBannerProps {
  matterId: string;
  isReviewRequired: boolean;
  reviewReasons: string[];
  workflowStatus?: "COMPLETED" | "PAUSED_FOR_REVIEW" | null;
  onDecisionSubmitted?: (result: HumanReviewDecisionResponse) => void;
}

export const HumanReviewBanner: React.FC<HumanReviewBannerProps> = ({
  matterId,
  isReviewRequired,
  reviewReasons,
  workflowStatus,
  onDecisionSubmitted,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideNotes, setOverrideNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  if (!isReviewRequired && !successBanner) {
    return null;
  }

  const handleDecision = async (action: "ACCEPT" | "REJECT" | "OVERRIDE", notes?: string) => {
    setSubmitting(true);
    setError(null);

    try {
      const res = await submitHumanReview(matterId, action, notes);
      if (action === "ACCEPT") {
        setSuccessBanner("Attorney accepted analysis findings. Multi-agent workflow resumed to completion.");
      } else if (action === "OVERRIDE") {
        setSuccessBanner("Attorney recorded legal override. Workflow updated with justification notes.");
      } else {
        setSuccessBanner("Attorney flagged petition deficiencies. Remedial evidentiary action required.");
      }
      setShowOverrideModal(false);
      setOverrideNotes("");
      if (onDecisionSubmitted) {
        onDecisionSubmitted(res);
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit attorney review decision.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Active Human Review Gate Alert Bar */}
      {isReviewRequired && (
        <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-4 shadow-sm text-slate-800 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-200/80 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-amber-100 text-amber-800 rounded-lg shrink-0">
                <AlertTriangle className="w-5 h-5 text-amber-700" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-amber-950 uppercase tracking-wider flex items-center gap-2">
                  Attorney Review Gate Active
                  <span className="text-[10px] bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full font-mono font-medium lowercase">
                    paused for human-in-the-loop
                  </span>
                </h3>
                <p className="text-xs text-amber-900 mt-0.5">
                  Automated multi-agent analysis detected items requiring legal review before report finalization.
                </p>
              </div>
            </div>

            {/* Quick Action Decision Buttons */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => handleDecision("ACCEPT")}
                disabled={submitting}
                className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors disabled:opacity-50"
              >
                {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                Accept & Finalize
              </button>

              <button
                onClick={() => setShowOverrideModal(true)}
                disabled={submitting}
                className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors disabled:opacity-50"
              >
                <Edit3 className="w-3.5 h-3.5" />
                Override with Notes...
              </button>

              <button
                onClick={() => handleDecision("REJECT")}
                disabled={submitting}
                className="px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-colors disabled:opacity-50"
              >
                <XCircle className="w-3.5 h-3.5" />
                Reject Findings
              </button>
            </div>
          </div>

          {/* Trigger Reasons Breakdown */}
          <div className="space-y-1.5 text-xs">
            <span className="font-semibold text-amber-950 flex items-center gap-1">
              <Info className="w-3.5 h-3.5 text-amber-700" /> Audit Trigger Reasons:
            </span>
            <ul className="space-y-1 pl-5 list-disc text-amber-900 text-[11px]">
              {reviewReasons.length > 0 ? (
                reviewReasons.map((reason, idx) => <li key={idx}>{reason}</li>)
              ) : (
                <li>Statutory coverage or provenance audit flagged potential evidentiary gaps.</li>
              )}
            </ul>
          </div>

          {error && (
            <div className="p-2 bg-rose-100 border border-rose-300 text-rose-800 rounded text-xs flex items-center gap-2">
              <XCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}
        </div>
      )}

      {/* Dismissible Post-Submission Success Notice */}
      {successBanner && (
        <div className="bg-emerald-50 border border-emerald-300 rounded-lg p-3 text-xs text-emerald-900 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successBanner}</span>
          </div>
          <button
            onClick={() => setSuccessBanner(null)}
            className="text-emerald-700 hover:text-emerald-950 p-1 rounded"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Attorney Legal Override Modal Dialog */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden space-y-4 animate-in fade-in zoom-in duration-150">
            {/* Modal Header */}
            <div className="bg-slate-900 text-white px-5 py-4 flex justify-between items-center">
              <div className="flex items-center gap-2.5">
                <FileCheck className="w-5 h-5 text-blue-400" />
                <h3 className="text-sm font-bold">Attorney Override & Evidentiary Justification</h3>
              </div>
              <button
                onClick={() => setShowOverrideModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-5 space-y-3 text-xs text-slate-700">
              <p className="text-[11px] text-slate-600 leading-relaxed">
                Provide legal reasoning or reference external petition exhibits that substantiate any flagged gaps or conflicts before unblocking report generation:
              </p>

              <textarea
                value={overrideNotes}
                onChange={(e) => setOverrideNotes(e.target.value)}
                placeholder="e.g., Foreign employment tenure substantiated by foreign tax statements in Exhibit D-2..."
                rows={4}
                className="w-full p-2.5 border border-slate-300 rounded-lg text-xs text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-blue-500 font-sans"
              />

              <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-[10px] text-blue-900">
                <strong>AUDIT LINEAGE NOTICE:</strong> This override note will be permanently bound to the matter's compliance audit log with your attorney reviewer ID.
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-5 py-3 bg-slate-50 border-t border-slate-200 flex justify-end gap-2">
              <button
                onClick={() => setShowOverrideModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800 font-medium"
              >
                Cancel
              </button>

              <button
                onClick={() => handleDecision("OVERRIDE", overrideNotes)}
                disabled={submitting || !overrideNotes.trim()}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg transition-colors shadow-xs flex items-center gap-1.5 disabled:opacity-50"
              >
                {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                Confirm Override & Resume
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
