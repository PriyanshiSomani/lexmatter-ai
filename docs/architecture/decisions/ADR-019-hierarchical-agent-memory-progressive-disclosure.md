# ADR-019: Hierarchical Multi-Tier Agent Memory & Progressive Disclosure Architecture

* **Status:** Accepted
* **Date:** 2026-10-08
* **Deciders:** LexMatter AI Architecture Team

---

## 1. Context

As LexMatter AI expanded across 14 development phases (incorporating 21 PostgreSQL tables, FastAPI async session handling, Next.js 14 frontend architecture, LangGraph multi-agent orchestration, and dual-engine test fallbacks), the operational complexity of maintaining AI assistant alignment grew significantly.

Prior to this decision, developer guidance and agent instructions were prone to two failure modes:
1. **Context Bloat & Token Waste (Monolithic Rules):** Dumping comprehensive architectural specifications, all 21 database table schemas, Docker recipes, and test fixture rules into a single prompt or root instruction file consumed **3,500 – 5,000 tokens on every single turn**, introducing significant latency, higher API overhead, and attention dilution.
2. **Context Drift & Knowledge Fragmentation:** Without structured persistence, operational quirks (e.g., SQLAlchemy async `await db.flush()` requirements per ADR-013, typed ULID generator prefixes, and Windows PowerShell command patterns) had to be repeatedly manually provided across developer sessions.

---

## 2. Decision

We adopt a **Hierarchical Multi-Tier Agent Memory and Progressive Disclosure Architecture** for LexMatter AI:

```text
lexmatter-ai/
├── GEMINI.md                                  <-- Root Pre-Flight Anchor (~45 lines)
└── .agents/
    ├── rules/
    │   ├── architecture-conventions.md        <-- Two-World DB, Typed ULIDs, Guardrails
    │   ├── backend-async.md                   <-- FastAPI, SQLAlchemy 2.0 async, db.flush rules
    │   └── frontend-standards.md              <-- Next.js 14 App Router, React, Tailwind
    │
    └── memory/
        ├── memory.md                          <-- Lightweight master index with update dates
        ├── tools/
        │   ├── run-commands.md                <-- Docker, FastAPI, Next.js, and Pytest commands
        │   └── docker-and-db.md               <-- PostgreSQL pgvector & SQLite dual-engine setup
        └── domain/
            ├── langgraph-orchestrator.md      <-- Agent state graph, checkpoints, review gate
            └── legal-ontology-and-l1b.md      <-- 21-table schema, L-1B requirements & dimensions
```

### Key Structural Principles:
1. **Lightweight Root Anchor (`GEMINI.md`):** Serves as an unbloated traffic controller (~45 lines). Contains non-negotiable project guardrails and a pre-flight directive commanding the agent to consult `.agents/memory/memory.md` before executing tasks.
2. **Progressive Disclosure:** Memory files are categorized into `tools/` and `domain/`. The LLM inspects the lightweight `memory.md` table index first, and dynamically reads specific topic files only when relevant to the active task.
3. **Knowledge Graduation Lifecycle:**
   - **Staging:** New architectural gotchas or setup quirks accumulate in `.agents/memory/`.
   - **Promotion:** When notes mature into stable project standards, they graduate into `.agents/rules/` or formal `.agents/skills/`.
   - **Pointer:** The memory entry is reduced to a concise reference pointer.
4. **Maintenance Directive (`"reorganize memory"`):** A built-in command instructing the agent to scan memory files, prune duplicates, re-sort chronologically (`Date, What, Why`), and synchronize the `memory.md` index table.

---

## 3. Quantitative Token & Performance Metrics

| Metric | Monolithic Baseline (Before) | Hierarchical Memory (After) | Impact |
| :--- | :--- | :--- | :--- |
| **Startup Prompt Tokens** | ~4,200 tokens / turn | **~220 tokens** (`GEMINI.md` + `memory.md`) | **~94.7% Reduction** |
| **Instruction Adherence** | Prone to attention dilution across unrelated domains | Focused context tailored directly to the active task | Eliminates hallucinated cross-domain rules |
| **Developer Onboarding** | 5–15 mins re-prompting setup commands per session | **Zero manual onboarding:** Instant tool-runbook retrieval | Increased developer velocity |
| **Token Cost Efficiency** | High recurring overhead on idle turns | Pay-as-needed on targeted topic file reads | Significant cost savings at scale |

---

## 4. Consequences

### Positive
* **Drastic Token Savings:** Cuts baseline context consumption by over 90%, preventing prompt bloat.
* **Deterministic Execution:** Provides unambiguous runbooks for Docker, FastAPI, Next.js, and Pytest.
* **Team-Shared Memory:** Fully version-controlled in Git without risking secrets or credential leaks.

### Trade-offs
* Requires agents to execute one quick file-reading step when switching domains (mitigated by fast local tool execution).
