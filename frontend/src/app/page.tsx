/**
 * LexMatter AI — Main Dashboard Landing Page
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Scale, ArrowRight, ShieldCheck, Cpu, Sparkles, FileText, CheckCircle2, Layers } from "lucide-react";

export default function Home() {
  const [matterIdInput, setMatterIdInput] = useState("mat_demo_01");

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-blue-500 selection:text-white">
      {/* Background Subtle Gradient Effects */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950 pointer-events-none" />

      {/* Navigation Header */}
      <header className="relative z-10 max-w-6xl w-full mx-auto flex justify-between items-center px-6 py-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl text-white shadow-lg shadow-blue-500/20 ring-1 ring-white/20">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              LexMatter AI
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">v1.0</span>
            </h1>
            <p className="text-xs text-slate-400">Agentic Legal-Matter Intelligence & Proof Verification Platform</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-3.5 py-1.5 rounded-full backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Backend Connected
          </span>
        </div>
      </header>

      {/* Main Hero Card */}
      <div className="relative z-10 max-w-4xl w-full mx-auto my-auto px-6 py-16 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-950/60 border border-blue-800/60 text-blue-300 text-xs font-medium backdrop-blur-sm shadow-inner">
          <Cpu className="w-4 h-4 text-blue-400 animate-spin-slow" />
          <span>LangGraph Multi-Agent Engine Operational</span>
        </div>

        <h2 className="text-4xl font-extrabold text-white sm:text-5xl tracking-tight leading-tight">
          Source-Grounded Legal Intelligence <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            & Provenance Tracing
          </span>
        </h2>

        <p className="text-base text-slate-300 leading-relaxed max-w-2xl mx-auto font-normal">
          Synthesizes petition files, maps 8 CFR statutory requirements, reconciles cross-document contradictions,
          detects evidence gaps, and generates audit-ready legal briefing reports.
        </p>

        {/* Quick Start Card */}
        <div className="max-w-md mx-auto p-6 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-md space-y-4 text-left">
          <div className="space-y-1">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Select or Enter Matter ULID
            </label>
            <p className="text-[11px] text-slate-500">Access the split-screen attorney workspace for this matter</p>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={matterIdInput}
              onChange={(e) => setMatterIdInput(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm font-mono text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
              placeholder="e.g. mat_demo_01"
            />

            <Link
              href={`/matters/${matterIdInput}`}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-600/30 hover:shadow-blue-600/50 transition-all transform active:scale-95"
            >
              Open Workspace <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Pre-loaded Demo Matter</span>
            <span className="font-mono text-slate-500">L-1B Petition</span>
          </div>
        </div>

        {/* Core Pillars Feature Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 max-w-3xl mx-auto text-left">
          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/60 space-y-1.5">
            <div className="text-blue-400 flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
              <FileText className="w-4 h-4" /> Evidence Mapping
            </div>
            <p className="text-xs text-slate-400">Extracts exact page & byte offsets for 8 CFR requirements.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/60 space-y-1.5">
            <div className="text-indigo-400 flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
              <ShieldCheck className="w-4 h-4" /> Conflict Audit
            </div>
            <p className="text-xs text-slate-400">Detects contradictory dates, salaries, and titles across exhibits.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/60 space-y-1.5">
            <div className="text-purple-400 flex items-center gap-2 text-xs font-bold uppercase tracking-wider">
              <Layers className="w-4 h-4" /> Dual-World UX
            </div>
            <p className="text-xs text-slate-400">Separate clean legal workspace and technical DAG provenance trace.</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 max-w-6xl w-full mx-auto px-6 py-6 border-t border-slate-800/80 text-center text-xs text-slate-500 flex flex-col sm:flex-row justify-between items-center gap-2">
        <div>LexMatter AI © 2026 — Dual-World Architecture for Attorney Briefing & Provenance Tracing</div>
        <div className="text-[11px] text-slate-600 font-mono">FastAPI • PostgreSQL pgvector • LangGraph • Next.js</div>
      </footer>
    </main>
  );
}
