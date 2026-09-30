# ADR-006: Multi-Agent Topology & State Graph Routing

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Analyzing a legal matter requires distinct cognitive capabilities: cross-document entity extraction, consistency contradiction detection, requirement evidence mapping, legal research lookup, and audit provenance verification. A single monolithic LLM prompt fails due to context limits, hallucination risks, and inability to execute targeted deterministic database queries.

---

## 2. Decision

We implement an **Orchestrator-Specialist Multi-Agent Topology** managed via LangGraph (`backend/app/agents/`):

1. **`CaseSupervisor` (`supervisor.py`):** Central orchestrator node managing global state (`MatterAnalysisState`), inspecting current analysis completeness, and routing execution to specialist agents.
2. **`EvidenceAnalyst` (`evidence_node.py`):** Traverses structured assertions, extracts requirement mappings, and evaluates evidentiary strength.
3. **`ConsistencyAnalyst` (`consistency_node.py`):** Compares cross-document assertion pairs to flag contradictory dates, job titles, salaries, or entity names (`Conflict`).
4. **`VerificationAgent` (`verification_node.py`):** Executes 4-tier verification hierarchy validating that all findings map to real `SourceSpan` offsets.
5. **Human Review Gate (`workflow.py`):** LangGraph `interrupt_before=["human_review"]` checkpoint pausing state graph execution for attorney review.

---

## 3. Consequences

### Positive
* **Specialized Agent Roles:** Each node executes targeted, deterministic service calls and localized LLM prompts.
* **Controlled Routing:** Supervisor node prevents execution deadlocks and enforces structured state transitions.

### Trade-offs
* State serialization and deserialization overhead between multi-agent graph iterations.
