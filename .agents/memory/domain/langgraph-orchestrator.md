# Domain Guide: LangGraph Multi-Agent Orchestration

## 1. Agent Topology & State Graph (ADR-006)
* **Case Supervisor Node:** Coordinates state transitions and selects target agent node based on matter phase.
* **Evidence Analyst Node:** Ingests document chunks, extracts `SourceSpan` character offsets, and maps multi-span evidence.
* **Consistency Agent Node:** Analyzes cross-document contradictions and populates `Conflict` records.
* **Research Agent Node:** Retrieves USCIS regulations, precedent cases, and statutory criteria.
* **Verification Node (4-Tier Hierarchy - ADR-014):**
  1. `EXACT_LEXICAL_CORROBORATION`
  2. `REGEX_WORD_BOUNDARY_SUPPORT`
  3. `SEMANTIC_HYBRID_SUPPORT`
  4. `LLM_ADJUDICATED_SUPPORT`

## 2. Persistent Checkpointing & Human Review Gate (ADR-015, ADR-018)
* **Checkpointer Provider:** `get_checkpointer()` provides `AsyncPostgresSaver` in production and `MemorySaver` in test fixtures.
* **Interrupt Gate:** Graph automatically pauses execution at `human_review_node`.
* **Attorney Resume Endpoint:** `POST /api/v1/matters/{matter_id}/orchestration/review` submits attorney decision (`APPROVED`, `REJECTED`, `OVERRIDDEN`) and unpauses state execution.
