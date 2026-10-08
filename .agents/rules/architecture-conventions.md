# Rule: Architecture Conventions & Data Integrity

## 1. Two-World Database Pattern (ADR-002)
* **World 1 (Immutable Source Claims):**
  - Tables: `documents`, `document_chunks`, `source_spans`, `source_assertions`.
  - Ingestion extracts verbatim character offsets (`start_char`, `end_char`), page numbers, and bounding boxes.
  - **Rule:** Never update or mutate existing World 1 records once created.
* **World 2 (Consolidated Knowledge & Legal Analysis):**
  - Tables: `canonical_entities`, `canonical_facts`, `conflicts`, `evidence_mappings`, `evidence_gaps`.
  - Synthesized by multi-agent analysis and verified through human review.

## 2. Global Typed ULIDs (ADR-009)
* All entity primary keys use typed ULIDs generated via `app.core.id_generator.generate_id(prefix)`:
  - Matter: `mat_...`
  - Document: `doc_...`
  - Chunk: `chk_...`
  - Span: `span_...`
  - Assertion: `asrt_...`
  - Fact: `fact_...`
  - Conflict: `cnf_...`
  - Requirement: `req_...`
  - Human Review: `hrev_...`
  - Case Memory: `mem_...`

## 3. Non-Adjudicative Guardrails (ADR-010)
* Never output definitive adjudication language (e.g. *"The applicant fails to qualify"* or *"This visa will be denied"*).
* Always employ guarded, conditional phrase templates:
  - *"Potential evidence gap detected for specialized knowledge requirement."*
  - *"Documentary inconsistency observed between Form I-129 and paystub dates."*
