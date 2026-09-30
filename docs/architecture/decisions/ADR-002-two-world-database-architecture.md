# ADR-002: Two-World Database Architecture (Source vs. Knowledge)

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

In legal-matter intelligence systems, mixing raw extracted assertions directly with synthesized or consolidated knowledge leads to data corruption, loss of audit lineage, and invalidation of legal evidence. Legal evidence must maintain strict immutability post-ingestion while allowing downstream reasoning engines to synthesize, deduplicate, and resolve conflicts.

---

## 2. Decision

We establish a strict **Two-World Architecture** separating raw immutable source data from synthesized consolidated knowledge:

1. **World 1 (Immutable Source Data):**
   * Entities: `Document`, `DocumentChunk`, `SourceSpan`, `SourceAssertion`.
   * **Rule:** Created exclusively during ingestion/extraction and **never updated or deleted**. Contains exact text character ranges (`start_char` to `end_char`), page bounding boxes, structural block types, and raw LLM extraction outputs.

2. **World 2 (Consolidated Knowledge & Legal Analysis):**
   * Entities: `CanonicalFact`, `CanonicalEntity`, `Conflict`, `EvidenceMapping`, `EvidenceGap`.
   * **Rule:** Represents the system's synthesized understanding of the matter. Multi-agent nodes resolve cross-document entity identity, flag contradictions (`Conflict`), and evaluate evidentiary support (`EvidenceMapping`) pointing back to World 1 source spans.

---

## 3. Consequences

### Positive
* **Immutability & Integrity:** Raw evidence claims are never overwritten or corrupted by agent reasoning.
* **Traceable Auditability:** Every consolidated fact or evidence gap in World 2 maintains explicit foreign key references down to World 1 `SourceSpan` offsets.
* **Flexible Re-Analysis:** Ingestion can be performed once while analytical rules and agent algorithms can be re-run across World 2 without re-parsing documents.

### Trade-offs
* Requires dual-layer data schemas and entity resolution mapping logic (`entity_resolver_service.py`).
