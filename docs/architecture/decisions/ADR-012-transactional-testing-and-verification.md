# ADR-012: Transactional Testing & Verification Strategy

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Testing multi-agent systems and multi-tier database pipelines risks database pollution, slow test execution, and non-deterministic test failures if test suites write persistent data across runs or rely on live external LLM API calls.

---

## 2. Decision

We establish an isolated, transactional testing strategy using **Pytest** (`backend/app/tests/`):

1. **Transactional Database Fixtures (`conftest.py`):** Each test run executes inside an isolated SQLAlchemy async transaction that automatically rolls back upon test completion, keeping the database clean.
2. **Dual-Engine Vector Fallback:** Test runner automatically detects availability of live PostgreSQL/pgvector databases; if unavailable, vector search degrades gracefully to in-memory cosine math simulation (`test_db_setup.py`).
3. **Comprehensive Engine Test Coverage:** 28 modular Pytest suites verifying each engine independently:
   * `test_document_engine.py` (PDF ingestion & chunking)
   * `test_extraction_engine.py` (Entity resolution & assertions)
   * `test_retrieval_engine.py` (RRF hybrid search)
   * `test_consistency_engine.py` (Cross-document conflict detection)
   * `test_evidence_engine.py` (Per-dimension evidence mapping)
   * `test_agent_orchestration.py` (LangGraph state graph & review interrupts)
   * `test_report_engine.py` (Briefing PDF exporter)
   * `test_audit_engine.py` (Lineage verification)

---

## 3. Consequences

### Positive
* **100% Test Pass Reliability:** Fast, deterministic test execution with zero database side-effects between runs.
* **Continuous Integration Ready:** Test suites run cleanly in lightweight CI runner containers.

### Trade-offs
* Requires writing comprehensive mock fixtures for external LLM calls.
