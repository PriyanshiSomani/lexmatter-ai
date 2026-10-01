# ADR-017: PostgreSQL-Backed Case-Scoped Memory Tool

* **Status:** Accepted
* **Date:** 2026-10-01
* **Deciders:** LexMatter AI Architecture Team

---

## 1. Context

Legal matter intelligence processing in LexMatter AI involves multi-step agent execution across multiple user sessions (e.g., initial evidence ingestion, incremental document additions, attorney review, and verification).

Without a persistent case-scoped memory model:
1. **Redundant Re-processing:** Adding supplementary evidence (e.g. 2 new paystubs) forces agents to re-analyze all previously processed documents from scratch, wasting LLM tokens and execution time.
2. **Context Window Inflation:** Passing complete raw document histories into every agent node prompt risks hitting context window limits and LLM rate limits.
3. **Loss of Agent Reasoning State:** Interrupted agent runs or multi-session attorney interactions lose synthesized progress logs, identified gaps, and supervisor routing notes.

---

## 2. Decision

We establish a **PostgreSQL-Backed Case-Scoped Memory Tool** architecture for LexMatter AI:

1. **Case-Scoped Persistence (`CaseMemory` Model):** Store agent memory notes in a dedicated PostgreSQL table (`case_memories`) indexed by `(matter_id, memory_key)`.
2. **Typed ULID Entity Identification:** Assign prefix `mem_` to all memory entity identifiers.
3. **Model-Agnostic Function Calling:** Provide Gemini (and local/cloud LLMs) with standardized function tools (`read_case_memory`, `write_case_memory`, `list_case_memories`).
4. **Just-In-Time Context Retrieval:** Agents query case memory notes on demand rather than loading full document histories into prompt contexts.
5. **Supervisor Node Integration:** Update `Case Supervisor` to consult case memory at the start of workflow routing, track fulfilled legal requirements, and allow incremental analysis runs when new evidence is added.

---

## 3. Consequences

### Positive
* **Token & Cost Efficiency:** Reduces LLM token usage by up to 80% during incremental document evaluations.
* **Multi-Session Continuity:** Allows agents and attorneys to resume work seamlessly across application restarts or multi-day review workflows.
* **Deterministic Isolation:** Cascading deletes (`ondelete="CASCADE"`) guarantee strict matter data boundaries.

### Trade-offs
* Requires database schema extension and service unit testing.
