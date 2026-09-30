# ADR-007: Provenance Audit Lineage & Character-Offset Tracing

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

AI legal tools frequently suffer from trust deficits due to potential LLM hallucinations or un-grounded claims. For an attorney or adjudicator to rely on an automated legal briefing, every assertion, canonical fact, conflict, and evidence mapping must trace back to verifiable text within the ingested source exhibits.

---

## 2. Decision

We mandate immutable, character-offset level provenance audit lineage across the platform (`audit_service.py`):

1. **`SourceSpan` Offsets:** Every extracted claim stores exact character ranges (`start_char`, `end_char`), page numbers, and bounding box coordinates.
2. **`AuditLineage` Mapping:** Structured relational database records explicitly map each `CanonicalFact`, `EvidenceMapping`, and `Conflict` to its underlying `SourceSpan` IDs.
3. **`ExtractionAuditLog`:** Audit log recording exact prompt parameters, model outputs, and raw JSON payloads for full forensic auditability.
4. **Verification Enforcement:** `VerificationAgent` rejects any finding or report snippet whose citation cannot be programmatically validated against registered `SourceSpan` records.

---

## 3. Consequences

### Positive
* **Zero-Hallucination Guarantee:** Findings without valid character offset lineage are rejected prior to report generation.
* **Auditor Transparency:** Attorneys can click any finding in the frontend UI to immediately jump to and highlight the exact text on the source PDF exhibit.

### Trade-offs
* Requires maintaining explicit foreign key relationships and audit verification steps throughout extraction and analysis pipelines.
