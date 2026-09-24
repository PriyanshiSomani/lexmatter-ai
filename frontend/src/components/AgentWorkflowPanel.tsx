/**
 * LexMatter AI — Multi-Agent Workflow Execution Monitor Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import { Bot, Play, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";
import { triggerAgentOrchestration, AgentOrchestrationResponse } from "../lib/api";

interface AgentWorkflowPanelProps {
  matterId: string;
  onWorkflowComplete?: () => void;
}

export const AgentWorkflowPanel: React.FC<AgentWorkflowPanelProps> = ({ matterId, onWorkflowComplete }) => {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentOrchestrationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunWorkflow = async () => {
    setRunning(true);
    setError(null);

    try {
      const res = await triggerAgentOrchestration(matterId, "L1B");
      setResult(res);
      if (onWorkflowComplete) onWorkflowComplete();
    } catch (err: any) {
      setError(err.message || "Agent workflow execution failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="bg-slate-900 text-slate-100 rounded-lg p-4 shadow-md space-y-4">
      <div className="flex justify-between items-center pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <h3 className="text-xs font-semibold text-slate-100">LangGraph Multi-Agent Orchestrator</h3>
        </div>

        <button
          onClick={handleRunWorkflow}
          disabled={running}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center gap-1.5 shadow transition-colors disabled:opacity-50"
        >
          {running ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          {running ? "Agents Running..." : "Run Multi-Agent Analysis"}
        </button>
      </div>

      {/* Specialist Agent Progress Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        <div className="p-2.5 bg-slate-800/80 rounded border border-slate-700 space-y-1">
          <p className="text-[10px] text-slate-400 font-semibold">EVIDENCE ANALYST</p>
          <div className="flex items-center justify-between">
            <span className="font-mono text-slate-200">Requirement Mapping</span>
            {result?.phase_completion.evidence_mapping ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            )}
          </div>
        </div>

        <div className="p-2.5 bg-slate-800/80 rounded border border-slate-700 space-y-1">
          <p className="text-[10px] text-slate-400 font-semibold">CONSISTENCY ANALYST</p>
          <div className="flex items-center justify-between">
            <span className="font-mono text-slate-200">Conflict Audit</span>
            {result?.phase_completion.consistency_check ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            )}
          </div>
        </div>

        <div className="p-2.5 bg-slate-800/80 rounded border border-slate-700 space-y-1">
          <p className="text-[10px] text-slate-400 font-semibold">RESEARCH AGENT</p>
          <div className="flex items-center justify-between">
            <span className="font-mono text-slate-200">Gap Discovery</span>
            {result?.phase_completion.research ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            )}
          </div>
        </div>

        <div className="p-2.5 bg-slate-800/80 rounded border border-slate-700 space-y-1">
          <p className="text-[10px] text-slate-400 font-semibold">VERIFICATION AGENT</p>
          <div className="flex items-center justify-between">
            <span className="font-mono text-slate-200">Span Audit</span>
            {result?.phase_completion.verification ? (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-slate-600"></span>
            )}
          </div>
        </div>
      </div>

      {result && (
        <div className="p-3 bg-slate-800 rounded border border-slate-700 text-xs space-y-2">
          <div className="flex justify-between items-center text-slate-300">
            <span>Status: <strong className="text-blue-400">{result.status}</strong></span>
            <span>Total Iterations: <strong className="font-mono text-slate-100">{result.summary_counts.total_iterations}</strong></span>
          </div>

          {result.human_review.required && (
            <div className="p-2 bg-amber-950/60 border border-amber-700 text-amber-300 rounded text-[11px] flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>Human Review Triggered: {result.human_review.reasons.join("; ")}</span>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="p-2 bg-red-950/60 border border-red-800 text-red-300 rounded text-xs">
          {error}
        </div>
      )}
    </div>
  );
};
