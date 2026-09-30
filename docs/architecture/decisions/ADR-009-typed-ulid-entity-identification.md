# ADR-009: Global Typed ULID Entity Identification

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

System entities across 21 database tables require global unique identifiers. Using standard auto-incrementing integer IDs exposes database metrics and leads to primary key collisions in distributed environments. Using standard 36-character UUID strings (e.g. `8f3b2c1a-...`) creates un-ordered database indexes and makes debugging difficult because raw UUIDs carry no domain type context.

---

## 2. Decision

We mandate **Typed Universally Unique Lexicographically Sortable Identifiers (ULIDs)** across all domain entities (`app/core/id_generator.py`):

1. **Format Structure:** `prefix_ULID` (e.g. `mat_01H...`, `doc_01H...`, `span_01H...`, `fact_01H...`, `evm_01H...`, `gap_01H...`, `hrev_01H...`).
2. **Standardized Prefixes:**
   * `mat_` $\rightarrow$ Matter
   * `doc_` $\rightarrow$ Document
   * `span_` $\rightarrow$ SourceSpan
   * `fact_` $\rightarrow$ CanonicalFact
   * `evm_` $\rightarrow$ EvidenceMapping
   * `gap_` $\rightarrow$ EvidenceGap
   * `hrev_` $\rightarrow$ HumanReview
3. **Lexicographical Ordering:** ULIDs encode a timestamp in their leading 48 bits, ensuring natural chronological sorting in database primary key indexes.

---

## 3. Consequences

### Positive
* **Instant Visual Domain Recognition:** Developers and auditors immediately recognize entity types in API payloads, logs, and tracebacks.
* **B-Tree Indexing Efficiency:** Chronological ordering prevents database B-tree index fragmentation compared to random UUID v4s.

### Trade-offs
* Requires wrapping primary key generation in SQLAlchemy model default generators (`id_generator.py`).
