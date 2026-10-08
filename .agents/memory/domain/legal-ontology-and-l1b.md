# Domain Guide: Legal Ontology & L-1B Requirements Schema

## 1. 21-Table Relational Schema
* **Source Domain:** `documents`, `document_chunks`, `source_spans`, `source_assertions`
* **Knowledge Domain:** `canonical_entities`, `canonical_facts`
* **Legal Domain:** `matters`, `matter_participants`, `matter_documents`
* **Requirement Domain:** `case_types`, `visa_requirements`, `requirement_dimensions`, `dimension_rules`
* **Analysis Domain:** `conflicts`, `evidence_mappings`, `evidence_gaps`
* **Audit Domain:** `processing_jobs`, `extraction_audit_logs`, `agent_execution_logs`, `audit_lineage`, `human_reviews`
* **Case Memory:** `case_memories` (ADR-017)

## 2. Initial Vertical: L-1B Visa Petitions
* **Scope:** Intracompany Transferee Specialized Knowledge (established U.S. offices, non-blanket).
* **Core Dimensions Evaluated:**
  1. Qualifying foreign corporate relationship (parent/subsidiary/affiliate).
  2. One continuous year of foreign employment within preceding 3 years.
  3. Advanced / specialized knowledge proprietary to the petitioning organization.
  4. Specialized role description in the U.S. operation.
