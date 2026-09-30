# ADR-004: Hybrid Retrieval Strategy (Reciprocal Rank Fusion RRF k=60)

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Legal retrieval queries require both **semantic understanding** (e.g. matching specialized technical expertise concepts) and **exact lexical precision** (e.g. matching specific dates, salary figures, employer EINs, or statutory section numbers). Standalone dense vector retrieval suffers from lexical blindness (missing exact names/numbers), while sparse keyword retrieval (BM25/`tsvector`) fails to capture conceptual paraphrasing.

---

## 2. Decision

We implement a **Reciprocal Rank Fusion (RRF)** hybrid retrieval pipeline (`hybrid_search_service.py`):

1. **Dense Vector Search (`vector_search_service.py`):** Compute 768-dimensional embeddings for document chunks using PostgreSQL `pgvector` with cosine similarity (`<=>`).
2. **Sparse Text Search:** Execute PostgreSQL full-text search (`tsvector` / `tsquery`) with English stemming and word-boundary dictionary matching.
3. **RRF Rank Combination:** Combine rank positions using the standard RRF formula with rank constant $k=60$:
   $$\text{RRF\_Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
   where $r_m(d)$ is the rank of document $d$ in retrieval method $m$.

---

## 3. Consequences

### Positive
* **Balanced Precision & Recall:** Outperforms single-retrieval models by surfacing exact entity matches alongside semantically relevant legal spans.
* **No Score Calibration Required:** RRF operates on ordinal rank positions rather than raw distance scores, avoiding arbitrary score normalization heuristics.

### Trade-offs
* Requires running dual database queries (vector cosine search and `tsvector` keyword search) per retrieval request.
