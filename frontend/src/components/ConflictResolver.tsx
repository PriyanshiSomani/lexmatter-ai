/**
 * LexMatter AI — Cross-Document Conflict Resolver Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import { GitCompare, AlertOctagon, CheckCircle, MessageSquare } from "lucide-react";
import { ConflictItem, resolveConflict } from "../lib/api";

interface ConflictResolverProps {
  conflicts: ConflictItem[];
  onConflictResolved?: () => void;
}

export const ConflictResolver: React.FC<ConflictResolverProps> = ({ conflicts, onConflictResolved }) => {
  const [activeNotes, setActiveNotes] = useState<{ [key: string]: string }>({});
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const handleResolve = async (conflictId: string) => {
    const notes = activeNotes[conflictId] || "Resolved by attorney review.";
    setResolvingId(conflictId);
    try {
      await resolveConflict(conflictId, notes);
      if (onConflictResolved) onConflictResolved();
    } catch (err) {
      console.error(err);
    } finally {
      setResolvingId(null);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-3">
      <div className="flex justify-between items-center pb-2 border-b border-slate-200">
        <h3 className="text-xs font-semibold text-slate-800 flex items-center gap-2">
          <GitCompare className="w-4 h-4 text-purple-600" /> Cross-Document Contradiction Audit
        </h3>
        <span className="text-[11px] font-medium text-slate-500 bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-200 font-semibold">
          {conflicts.length} Contradictions Detected
        </span>
      </div>

      {conflicts.length > 0 ? (
        <div className="space-y-3">
          {conflicts.map((conf) => {
            const isResolved = conf.status === "ATTORNEY_RESOLVED";
            return (
              <div
                key={conf.id}
                className={`p-3 rounded border text-xs space-y-2 transition-colors ${
                  isResolved ? "bg-slate-50 border-slate-200 opacity-75" : "bg-red-50/50 border-red-200"
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                    <AlertOctagon className={`w-3.5 h-3.5 ${conf.severity === "HIGH" ? "text-red-600" : "text-amber-600"}`} />
                    {conf.conflict_type}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${conf.severity === "HIGH" ? "bg-red-200 text-red-800" : "bg-amber-200 text-amber-800"}`}>
                      {conf.severity} SEVERITY
                    </span>
                    <span className="text-[10px] font-medium text-slate-500 bg-slate-200 px-1.5 py-0.5 rounded">
                      {conf.status}
                    </span>
                  </div>
                </div>

                <p className="text-slate-700 leading-relaxed text-[11px]">{conf.description}</p>

                {!isResolved && (
                  <div className="pt-2 border-t border-red-100 flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Input attorney resolution explanation..."
                      value={activeNotes[conf.id] || ""}
                      onChange={(e) => setActiveNotes({ ...activeNotes, [conf.id]: e.target.value })}
                      className="flex-1 text-[11px] px-2.5 py-1 bg-white border border-slate-300 rounded focus:outline-none focus:border-purple-500"
                    />
                    <button
                      onClick={() => handleResolve(conf.id)}
                      disabled={resolvingId === conf.id}
                      className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-[11px] font-semibold flex items-center gap-1 shadow-sm transition-colors"
                    >
                      <CheckCircle className="w-3 h-3" /> Resolve
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-6 text-center text-slate-400 text-xs flex flex-col items-center gap-1">
          <CheckCircle className="w-6 h-6 text-emerald-500 opacity-60" />
          <p>No cross-document contradictions identified across analyzed assertions.</p>
        </div>
      )}
    </div>
  );
};
