# ADR-010: Non-Adjudicative Guardrails & Legal Phrasing Rules

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

AI legal analysis tools face severe legal, ethical, and regulatory risks regarding the Unauthorized Practice of Law (UPL) if automated outputs attempt to render final legal adjudications, issue legal guarantees, or mimic government adjudicative decisions (e.g. state *"Petition Approved"* or *"Ineligible for Visa"*).

---

## 2. Decision

We establish strict **Non-Adjudicative Phrasing Guardrails** across all services, schemas, and briefing generators (`evidence_service.py`, `report_service.py`, `schemas/analysis.py`):

1. **Mandatory Conditional Terminology:** All automated findings, evidence mapping statuses, and gap summaries must use conditional, non-adjudicative terminology:
   * *Allowed:* *"Potential evidence gap detected"*, *"Unresolved contradiction identified"*, *"Evidence mapping located"*, *"Sufficient documentary support indicated for dimension X"*.
   * *Prohibited:* *"Case approved"*, *"Ineligible"*, *"Petition legally deficient"*, *"Definitive proof"*.
2. **Explanatory Disclaimers:** All exported PDF briefing reports (`report_service.py`) and UI views must include mandatory legal disclaimers stating that outputs constitute automated legal analytical support for reviewing attorneys, not formal legal advice or USCIS adjudications.

---

## 3. Consequences

### Positive
* **UPL & Regulatory Safety:** Protects platform and legal practice from unauthorized practice of law liability.
* **Appropriate Framing:** Correctly positions system outputs as analytical input for human attorney judgment.

### Trade-offs
* Requires enforcing guardrail regex patterns and string validators in report generation functions.
