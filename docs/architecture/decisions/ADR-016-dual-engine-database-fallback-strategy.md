# ADR-016: Dual-Engine Database Fallback & Vector Search Degradation Strategy

* **Status:** Accepted
* **Date:** 2026-09-26
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

LexMatter AI supports PostgreSQL with `pgvector` as its primary production database. For local development and unit testing, an optional SQLite engine (`USE_SQLITE=true`) is supported via SQLAlchemy compilation hooks.

However:
- `pgvector` HNSW vector distance operators (`.cosine_distance()`) are specific to PostgreSQL.
- Under SQLite, calling dense vector queries or hybrid retrieval raises runtime SQL compilation errors because SQLite lacks native vector operators.

---

## 2. Decision

We established a formal **Dual-Engine Fallback & Degradation Strategy**:

1. **Production Engine (PostgreSQL + pgvector):** PostgreSQL is mandatory for full-featured production deployments, supporting HNSW vector indexes, JSONB GIN indexes, and full-text search.
2. **Local / Testing Engine (SQLite):** SQLite is classified strictly as a lightweight local development and unit testing mock.
3. **Graceful Vector Degradation:** In SQLite mode, dense vector similarity queries degrade gracefully to keyword/FTS search or in-memory NumPy similarity calculations, preventing application startup or runtime crashes.

---

## 3. Consequences

### Positive
* **Zero-Setup Local Testing:** Developers can run fast unit tests without requiring a running Docker PostgreSQL container.
* **Production Reliability:** Prevents silent failures by explicitly scoping full vector and FTS retrieval capabilities to PostgreSQL.

### Trade-offs
* SQLite mode does not mirror PostgreSQL HNSW vector search performance or exact ranking scores.
