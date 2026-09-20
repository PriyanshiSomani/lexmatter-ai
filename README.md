# LexMatter AI — Agentic Legal-Matter Intelligence Platform

> **Notice:** LexMatter AI is an agentic decision-support and evidence-intelligence platform designed to assist legal professionals. It is **not** an automated legal adjudicator and does **not** provide legal advice or predict case approval outcomes. All findings require mandatory human review.

---

## 1. Executive Summary

Legal teams reviewing complex immigration petitions or multi-document legal matters routinely evaluate thousands of pages of unstructured evidence (e.g., employment verification letters, resumes, tax filings, organizational charts, corporate contracts, and USCIS forms). Determining whether facts across documents are consistent, whether evidence satisfies specific legal standards, and where evidence gaps exist is a time-consuming, expensive, and error-prone process.

**LexMatter AI** automates this analysis by constructing a structured, traceable knowledge representation of legal matters. It ingests document collections, extracts immutable source assertions with character-level provenance, consolidates canonical facts, maps evidence to versioned legal requirements, detects cross-document contradictions and evidentiary gaps, performs authoritative legal research, and presents verifiable findings for human review.

---

## 2. Initial Vertical: USCIS Case Readiness

To establish a solid, production-grade foundation, LexMatter AI focuses initially on a well-defined, high-value vertical:

* **Target Workflow:** USCIS Immigration Case Readiness & Evidence Intelligence
* **Initial Case Category:** Individual **L-1B Petitions** (Intracompany Transferee Specialized Knowledge)
* **Scope Constraints:** Established U.S. offices, non-blanket petitions. (H-1B, L-1A, blanket petitions, and green card filings are reserved for future phases).

---

## 3. Core System Architecture

LexMatter AI strictly separates deterministic backend services from reasoning agents to maximize reliability and eliminate non-deterministic failure modes.

```text
                              +-------------------+
                              |     User / UI     |
                              +---------+---------+
                                        |
                                        v
                              +-------------------+
                              |  Case Supervisor  |
                              +---------+---------+
                                        |
         +------------------------------+------------------------------+
         |                              |                              |
         v                              v                              v
+-------------------+          +-------------------+          +-------------------+
| Evidence Analyst  |          | Consistency Agent |          |  Research Agent   |
+---------+---------+          +---------+---------+          +---------+---------+
         |                              |                              |
         +------------------------------+------------------------------+
                                        |
                                        v
                              +-------------------+
                              | Verification Agent|
                              +---------+---------+
                                        |
                                        v
                              +-------------------+
                              |   Human Review    |
                              +-------------------+
```

---

## 4. Key Architectural Pillars

1. **Strict Source Provenance:** Every fact, finding, and evidence mapping references an exact character offset span (`SourceSpan`) and page coordinate in the original document.
2. **Two-World Separation:** Extracted claims (`SourceAssertion`) are immutable and preserved exactly as stated in the source document. Normalized facts (`CanonicalFact`) and detected discrepancies (`Conflict`) are tracked separately.
3. **Evidence as Relationships:** Evidence is modeled not merely as a stored document, but as a formal relationship (`EvidenceMapping`) connecting source assertions to structured, versioned legal requirements (`Requirement`).
4. **Hybrid Retrieval:** Dense vector embeddings (pgvector) combined with sparse keyword search (BM25) and strict metadata filters guarantee precise, hallucination-resistant citation retrieval.
5. **Deterministic Foundation:** Deterministic operations (PDF parsing, OCR, hashing, schema validation) are never offloaded to LLMs. Agents are reserved exclusively for multi-step reasoning, synthesis, and verification.
6. **Zero-Cost Engineering:** Built entirely on open-source foundations (PostgreSQL, pgvector, SentenceTransformers, PyMuPDF, FastAPI, React, LangGraph) with support for free-tier cloud models (Gemini) and 100% offline local LLMs (Ollama).

---

## 5. Repository Structure

```text
lexmatter-ai/
├── docs/
│   ├── architecture/
│   │   ├── system_overview.md
│   │   └── decisions/        # ADR-001 through ADR-012
│   ├── ontology/             # Complete schema specifications (21 entities)
│   └── requirements/         # L-1B legal framework reference
├── backend/
│   ├── alembic/              # Database migrations
│   └── app/
│       ├── api/              # FastAPI REST endpoints
│       ├── core/             # Configuration, logging, security
│       ├── db/               # PostgreSQL & pgvector engine
│       ├── models/           # SQLAlchemy ORM models (21 entities)
│       ├── schemas/          # Pydantic validation schemas
│       ├── services/         # Deterministic ingestion, extraction & retrieval
│       └── agents/           # LangGraph multi-agent orchestration
├── frontend/                 # React + Vite case workspace UI
├── datasets/                 # Synthetic benchmark test packages
└── docker/                   # Docker Compose environment setup
```
