/**
 * LexMatter AI — Main Dashboard Landing Page
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Scale, FileText, ArrowRight, ShieldCheck, Cpu } from "lucide-react";

export default function Home() {
  const [matterIdInput, setMatterIdInput] = useState("mat_demo_01");

  return (
    <main className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between p-8">
      {/* Navigation Header */}
      <header className="max-w-6xl w-full mx-auto flex justify-between items-center pb-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600 rounded-lg text-white shadow-lg">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white">LexMatter AI</h1>
            <p className="text-xs text-slate-400">Agentic Legal-Matter Intelligence Platform</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-3 py-1 rounded-full">
            ● Backend Engine Connected
          </span>
        </div>
      </header>

      {/* Main Hero Card */}
      <div className="max-w-3xl w-full mx-auto my-auto text-center space-y-6 py-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-800 text-blue-400 text-xs font-medium">
          <Cpu className="w-3.5 h-3.5" /> LangGraph Multi-Agent Engine Operational
        </div>

        <h2 className="text-3xl font-extrabold text-white sm:text-4xl tracking-tight leading-snug">
          Legal Matter Intelligence & Proof Verification
        </h2>

        <p className="text-sm text-slate-300 leading-relaxed max-w-2xl mx-auto">
          Synthesizes petition files, maps 8 CFR statutory requirements, reconciles cross-document contradictions,
          detects evidence gaps, and exports fully cited attorney briefing reports.
        </p>

        {/* Quick Start Matter Input */}
        <div className="max-w-md mx-auto p-4 bg-slate-800/90 rounded-xl border border-slate-700 shadow-xl space-y-3">
          <label className="block text-xs font-semibold text-slate-300 text-left">
            Enter Matter ULID or Load Demo Petition:
          </label>

          <div className="flex gap-2">
            <input
              type="text"
              value={matterIdInput}
              onChange={(e) => setMatterIdInput(e.target.value)}
              className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-blue-500"
            />

            <Link
              href={`/matters/${matterIdInput}`}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center gap-2 shadow-lg transition-colors"
            >
              Open Workspace <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="max-w-6xl w-full mx-auto pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
        LexMatter AI © 2026 — Dual-World Architecture for Attorney Briefing & Provenance Tracing
      </footer>
    </main>
  );
}
