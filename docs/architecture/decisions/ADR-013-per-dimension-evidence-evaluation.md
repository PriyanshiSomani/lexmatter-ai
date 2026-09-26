# ADR-013: Granular Per-Dimension Evidence Evaluation & State Synchronization

* **Status:** Accepted
* **Date:** 2026-09-26
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

The `EvidenceAnalyst` node in the multi-agent workflow processes legal requirement dimensions iteratively. Originally, on each iteration step, the node invoked `evidence_service.evaluate_matter_evidence()`, which performed a global table wipe (`DELETE FROM evidence_mappings` and `DELETE FROM evidence_gaps`) across all matter dimensions.

This global reset pattern introduced two critical architectural defects:
1. **State Invalidation & Dead References:** Primary key IDs stored in the LangGraph `MatterAnalysisState` (`mapped_evidence_ids` and `identified_gap_ids`) became stale/dead references pointing to deleted database records after each loop iteration.
2. **Computational Inefficiency:** For $N$ requirement dimensions, the engine evaluated all $N$ dimensions globally $N$ times, leading to $O(N^2)$ redundant database reads/writes.

---

## 2. Decision

We refactored `EvidenceService` to support isolated, atomic per-dimension evidence evaluation (`evaluate_dimension_evidence`):

1. **Targeted Per-Dimension Mutations:** When evaluating dimension $X$, only `EvidenceMapping` records where `target_dimension == X` and `EvidenceGap` records where `dimension == X` are cleared and rebuilt. Mappings and gaps for all other dimensions remain completely untouched.
2. **Session Flush Before Applicability Scoring:** An explicit `await db.flush()` is invoked after adding new `EvidenceMapping` objects, ensuring that SQL count queries calculating requirement applicability status (`supported_dims == len(dims)`) read flushed records within the active database transaction.
3. **State ID Synchronization:** LangGraph state mapped IDs are synchronized directly against active database primary keys after each node execution step.

---

## 3. Consequences

### Positive
* **Atomicity & Data Integrity:** Prevents stale primary key references in LangGraph state.
* **Performance:** Reduces computational complexity from $O(N^2)$ to $O(N)$ during sequential multi-agent execution.
* **Accuracy:** Resolves false `PARTIAL_SUPPORT` status degradations, allowing fully supported legal requirements to achieve `EVIDENCE_LOCATED` status.

### Trade-offs
* Requires explicit session management and flushes inside service helper functions during per-dimension iterations.
