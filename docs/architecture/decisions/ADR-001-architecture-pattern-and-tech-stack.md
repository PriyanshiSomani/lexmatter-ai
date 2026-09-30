# ADR-001: Architecture Pattern & Technology Stack

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Legal-matter processing requires ingesting large volumes of unstructured evidence documents (PDF petitions, support letters, financial records), mapping evidence against statutory criteria, detecting contradictions across exhibits, and producing verifiable, source-grounded briefing reports.

Building a monolithic, synchronous application for this domain presents critical challenges:
1. **Long-Running & Non-Blocking I/O:** Document parsing, vector embedding, and LLM reasoning steps are IO-heavy operations that would block standard web frameworks.
2. **Stateful Multi-Agent Workflows:** Complex legal analysis requires orchestrated multi-step reasoning with state persistence and human-in-the-loop review gates.
3. **Strict Auditability:** Legal applications must prevent hallucination and maintain pinpoint provenance linking claims to exact character offsets.

---

## 2. Decision

We adopt a decoupled, multi-tier architecture pattern combining **FastAPI**, **LangGraph**, **PostgreSQL + pgvector**, and **Next.js**:

1. **Backend Framework (FastAPI + Async SQLAlchemy 2.0):** Python async REST backend utilizing `AsyncSession` for high-concurrency non-blocking database and LLM operations.
2. **Stateful Orchestration Engine (LangGraph):** Orchestrator-specialist multi-agent state graph managing step routing, state persistence, cycle prevention, and human review interrupts.
3. **Data Layer (PostgreSQL + pgvector):** Unified relational and vector database housing structured entities, character-level source spans, RRF hybrid retrieval indexes, and provenance lineage logs.
4. **Frontend Architecture (Next.js 14 App Router + React + Tailwind CSS):** Decoupled React frontend providing real-time workflow tracking, evidence gap visualization, and audit span highlighting.

---

## 3. Consequences

### Positive
* **High Concurrency & Scalability:** Non-blocking async Python backend efficiently handles parallel document parsing and vector search.
* **Deterministic & Stateful Workflows:** LangGraph provides structured state management and persistent checkpoints.
* **Type Safety & Data Integrity:** Shared schemas and typed entities ensure strict contract enforcement between services and UI.

### Trade-offs
* Requires careful async session management in database helper functions.
* Increases deployment complexity (multi-container orchestration).
