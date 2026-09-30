# ADR-005: Legal Domain Ontology & Requirements Modeling

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

USCIS adjudication standards require evaluating petitions against specific statutory and regulatory criteria (such as 8 CFR 214.2(l) for L-1B intracompany transferees). Hardcoding requirement logic inside application scripts creates rigid, unmaintainable code that cannot adapt to regulatory updates or new visa categories (O-1A, H-1B, EB-1A).

---

## 2. Decision

We establish a declarative, 4-tier hierarchical legal domain ontology (`backend/app/models/legal.py`):

1. **`CaseType`:** Top-level legal category (e.g. `L1B_INDIVIDUAL`, `O1A_EXTRAORDINARY`).
2. **`VisaRequirement`:** Statutory requirement (e.g. *Specialized Knowledge*, *Continuous 1-Year Foreign Employment*, *Qualifying Corporate Relationship*).
3. **`RequirementDimension`:** Specific evaluation vector within a requirement (e.g. *Proprietary System Expertise*, *Advanced Technical Degree*, *Overseas Managerial/Specialized Role*).
4. **`DimensionRule`:** Deterministic scoring threshold or rule logic defining necessary supporting evidence.

The ontology is seeded declaratively (`l1b_requirements_seed.py`) and managed via `requirement_service.py`.

---

## 3. Consequences

### Positive
* **Extensibility:** New visa categories and statutory updates can be added via database seeds without modifying backend service code.
* **Granular Evidence Evaluation:** Allows evaluating evidentiary coverage at the atomic dimension level rather than blanket pass/fail scoring.

### Trade-offs
* Requires initial ontology modeling effort for each new visa vertical.
