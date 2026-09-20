# LexMatter AI — System Architecture Overview

## 1. High-Level Vision
LexMatter AI is an agentic legal-matter intelligence platform that ingests large collections of legal and supporting documents, builds a structured representation of the matter, maps evidence to requirements or claims, identifies inconsistencies and evidence gaps, researches authoritative external sources, and generates source-grounded outputs for human review.

---

## 2. Multi-Agent Topology
The system adopts an orchestrator-specialist topology managed via LangGraph:

```text
                              +--------------------+
                              |  User / Client UI  |
                              +---------+----------+
                                        |
                                        v
                              +--------------------+
                              |   Case Supervisor  |
                              +---------+----------+
                                        |
         +------------------------------+------------------------------+
         |                              |                              |
         v                              v                              v
+--------------------+        +--------------------+        +--------------------+
|  Evidence Analyst  |        | Consistency Analyst|        |   Research Agent   |
+---------+----------+        +---------+----------+        +---------+----------+
         |                              |                              |
         +------------------------------+------------------------------+
                                        |
                                        v
                              +--------------------+
                              | Verification Agent |
                              +---------+----------+
                                        |
                                        v
                              +--------------------+
                              |    Human Review    |
                              +--------------------+
```

### Agent Responsibilities
- **Case Supervisor**: Coordinates the workflow, determines missing analysis dimensions, schedules sub-agent runs, and aggregates findings.
- **Evidence Analyst**: Traverses structured assertions, extracts requirement mappings, and evaluates evidentiary strength against USCIS standards.
- **Consistency Analyst**: Evaluates cross-document assertion pairs, flags contradictory dates/roles/salaries/entities, and constructs `Conflict` objects.
- **Research Agent**: Queries primary legal sources (USCIS Policy Manual, 8 CFR, AAO Decisions) for specific legal ambiguities.
- **Verification Agent**: Validates that all findings, citations, and evidence links trace back to exact `SourceSpan` offsets before human review.
- **Human Review**: Interactive human-in-the-loop checkpoint where attorneys accept, reject, or modify findings.

---

## 3. Data Processing Layers
1. **Source Layer**: Matter, Document, DocumentVersion, Page, SourceSpan.
2. **Extraction Layer**: Entity, SourceAssertion, Event.
3. **Knowledge Layer**: CanonicalFact, Relationship, Conflict.
4. **Legal Knowledge Layer**: Authority, Requirement, RequirementVersion, RequirementApplicability.
5. **Analysis Layer**: EvidenceMapping, Finding, EvidenceGap, ResearchIssue.
6. **Workflow / Audit Layer**: AgentRun, HumanReview, AuditEvent.
