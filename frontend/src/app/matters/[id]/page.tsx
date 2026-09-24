/**
 * LexMatter AI — Main Matter Workspace Page
 * Phase 12: Frontend Integration & UI
 * Split-screen attorney workspace with separate Technical Audit tab
 */

"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Scale, ArrowLeft, ShieldCheck, Cpu, RefreshCw } from "lucide-react";

import { DocumentUploader } from "../../../components/DocumentUploader";
import { DocumentViewer } from "../../../components/DocumentViewer";
import { RequirementMatrix } from "../../../components/RequirementMatrix";
import { ConflictResolver } from "../../../components/ConflictResolver";
import { ReportExporter } from "../../../components/ReportExporter";
import { AgentWorkflowPanel } from "../../../components/AgentWorkflowPanel";

import {
  fetchMatterDocuments,
  fetchRequirements,
  fetchEvidenceMappings,
  fetchConflicts,
  fetchEvidenceGaps,
  DocumentItem,
  RequirementItem,
  EvidenceMappingItem,
  ConflictItem,
  EvidenceGapItem,
} from "../../../lib/api";

export default function MatterWorkspace({ params }: { params: { id: string } }) {
  const matterId = params.id;
  const [activeTab, setActiveTab] = useState<"legal" | "technical">("legal");
  const [loading, setLoading] = useState(true);

  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [requirements, setRequirements] = useState<RequirementItem[]>([]);
  const [evidenceMappings, setEvidenceMappings] = useState<EvidenceMappingItem[]>([]);
  const [conflicts, setConflicts] = useState<ConflictItem[]>([]);
  const [evidenceGaps, setEvidenceGaps] = useState<EvidenceGapItem[]>([]);

  const loadMatterData = async () => {
    setLoading(true);
    try {
      const [docs, reqs, evs, confs, gaps] = await Promise.all([
        fetchMatterDocuments(matterId),
        fetchRequirements(matterId),
        fetchEvidenceMappings(matterId),
        fetchConflicts(matterId),
        fetchEvidenceGaps(matterId),
      ]);
      setDocuments(docs);
      setRequirements(reqs);
      setEvidenceMappings(evs);
      setConflicts(confs);
      setEvidenceGaps(gaps);
    } catch (err) {
      console.error("Failed to load matter workspace data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMatterData();
  }, [matterId]);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      {/* Top Application Header */}
      <header className="bg-slate-900 text-white px-6 py-3 border-b border-slate-800 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-blue-400" />
            <div>
              <h1 className="text-sm font-bold text-white flex items-center gap-2">
                Matter Intelligence Workspace
                <span className="text-[11px] font-mono font-medium text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                  {matterId}
                </span>
              </h1>
              <p className="text-[11px] text-slate-400">Case Type: L-1B (Specialized Knowledge Transferee)</p>
            </div>
          </div>
        </div>

        {/* Tab Switcher: Primary Legal Workspace vs Technical Audit */}
        <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700">
          <button
            onClick={() => setActiveTab("legal")}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold transition-colors ${
              activeTab === "legal" ? "bg-blue-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" /> Legal Analysis Workspace
          </button>
          <button
            onClick={() => setActiveTab("technical")}
            className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold transition-colors ${
              activeTab === "technical" ? "bg-blue-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <Cpu className="w-3.5 h-3.5" /> Technical Audit & Agent Logs
          </button>
        </div>

        <button
          onClick={loadMatterData}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors text-xs flex items-center gap-1"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </header>

      {/* Main Workspace Body */}
      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto">
        {activeTab === "legal" ? (
          /* TAB 1: Clean Attorney Legal Workspace (Split-Screen) */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-120px)]">
            {/* Left Column (5 Cols): PDF Document Uploader & Source Viewer */}
            <div className="lg:col-span-5 flex flex-col gap-4 h-full overflow-hidden">
              <DocumentUploader matterId={matterId} onUploadSuccess={loadMatterData} />
              <div className="flex-1 overflow-hidden">
                <DocumentViewer documents={documents} />
              </div>
            </div>

            {/* Right Column (7 Cols): Legal Compliance Matrix, Conflicts, PDF Exporter */}
            <div className="lg:col-span-7 flex flex-col gap-4 overflow-y-auto pr-1">
              <RequirementMatrix
                requirements={requirements}
                evidenceGaps={evidenceGaps}
                evidenceMappings={evidenceMappings}
              />
              <ConflictResolver conflicts={conflicts} onConflictResolved={loadMatterData} />
              <ReportExporter matterId={matterId} />
            </div>
          </div>
        ) : (
          /* TAB 2: Technical Audit & Agent Execution Controls */
          <div className="space-y-6 max-w-4xl mx-auto py-4">
            <AgentWorkflowPanel matterId={matterId} onWorkflowComplete={loadMatterData} />

            <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 space-y-3">
              <h3 className="text-xs font-semibold text-slate-800 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-600" /> Database Entities & Lineage Summary
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3 bg-slate-50 border rounded space-y-1">
                  <p className="text-slate-500 font-medium">Ingested Documents</p>
                  <p className="text-lg font-bold text-slate-800">{documents.length}</p>
                </div>
                <div className="p-3 bg-slate-50 border rounded space-y-1">
                  <p className="text-slate-500 font-medium">Evidence Mappings</p>
                  <p className="text-lg font-bold text-emerald-700">{evidenceMappings.length}</p>
                </div>
                <div className="p-3 bg-slate-50 border rounded space-y-1">
                  <p className="text-slate-500 font-medium">Flagged Conflicts</p>
                  <p className="text-lg font-bold text-purple-700">{conflicts.length}</p>
                </div>
                <div className="p-3 bg-slate-50 border rounded space-y-1">
                  <p className="text-slate-500 font-medium">Evidence Gaps</p>
                  <p className="text-lg font-bold text-amber-700">{evidenceGaps.length}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
