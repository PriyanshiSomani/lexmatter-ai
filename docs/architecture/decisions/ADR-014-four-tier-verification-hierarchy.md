# ADR-014: 4-Tier Verification Hierarchy & Provenance Integrity

* **Status:** Accepted
* **Date:** 2026-09-26
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

The initial `VerificationAgent` node performed only basic metadata presence verification (testing `if assertion.source_span_id is not None`). 

This shallow check was insufficient for legal audit standards because:
1. **False Positive Substring Collisions:** Naïve string matching (`kw in text`) mapped unrelated document text (e.g. document salutations like `"Dear USCIS Adjudicating Officer,"`) to legal dimensions (e.g. `active_business_us` matching `"Officer"` via `"office"`).
2. **Lack of Semantic Entailment:** The system could not detect when a valid `SourceSpan` was linked to a claim that the text did not actually support.

---

## 2. Decision

We established a **4-Tier Verification Hierarchy** in `verification_node.py` and `evidence_service.py`:

```text
[Level 1: Metadata Presence] ──> Verifies source_span_id foreign key exists in DB.
            │
[Level 2: Offset Integrity]  ──> Verifies start_char < end_char and snippet presence.
            │
[Level 3: Semantic Alignment] ──> Verifies word-boundary regex (\b) & filters boilerplate/greetings.
            │
[Level 4: Statutory Relevance] ──> Audits matter requirement coverage (R1-R6 thresholds).
```

### Key Technical Enforcements:
1. **Regex Word Boundaries (`\b`):** Substring matching uses regex word-boundaries (`r'\b' + re.escape(kw) + r's?\b'`) and acronym handlers (`r'\b(u\.s\.|us)\b'`).
2. **Boilerplate Span Filter:** Discards spans containing document headers, greetings (`"Dear USCIS..."`), or generic sign-offs (`"Sincerely,"`).
3. **Multi-Level Audit Logging:** If any mapping fails Level 1, 2, 3, or 4, `VerificationAgent` records an audit failure detail, sets `requires_human_review = True`, and attaches an explicit review reason.

---

## 3. Consequences

### Positive
* **Elimination of False Positives:** Salutations and header blocks are rejected, forcing the engine to select true evidentiary spans.
* **Audit Transparency:** Human attorneys receive specific, structured audit logs detailing exact failure levels.

### Trade-offs
* Strict word-boundary matching requires explicit keyword dictionary maintenance for technical and legal acronyms.
