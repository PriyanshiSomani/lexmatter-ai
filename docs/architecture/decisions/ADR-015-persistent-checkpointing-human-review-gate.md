# ADR-015: Persistent PostgreSQL Checkpointing & Interrupt/Resume Human-Review Gate

* **Status:** Accepted (Fully Implemented)
* **Date:** 2026-09-26 (Updated: 2026-10-07)
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context & What Was Before

In the initial LangGraph multi-agent orchestration setup:
1. **Ephemeral In-Memory State (`MemorySaver`):** The workflow compiled with `MemorySaver()`, storing active graph state in Python process heap memory.
2. **Flag-and-Finish Pseudo-Review:** The `human_review` node set `requires_human_review = True` and transitioned directly to `END`, acting as a terminal flag rather than an interactive pause/resume workflow.

---

## 2. Root Cause & What It Was Causing

1. **State Loss on Server Restarts:** If an attorney took hours or days to review an L-1B compliance matrix and the backend server restarted, updated, or scaled across multiple worker processes, the checkpoint in RAM was destroyed.
2. **Resume Failure:** Subsequent calls to `POST /matters/{matter_id}/orchestration/review` attempted to load checkpoint thread `matter_{matter_id}`, found no state in memory, and failed.
3. **State Overwrite & Premature Termination:** On initial resume implementation, `human_review_node` unconditionally overwrote attorney decisions back to `requires_human_review = True`, and the static `human_review -> END` edge prevented execution from reaching downstream reporting agents.

---

## 3. Decision & What We Resolved

We established and implemented a production-grade, dual-mode persistent checkpointing and human-in-the-loop lifecycle architecture:

1. **Persistent PostgreSQL Checkpointer (`AsyncPostgresSaver`):**
   - Implemented `get_checkpointer()` in `backend/app/agents/workflow.py`.
   - When running against PostgreSQL (`USE_SQLITE=false`), initializes `AsyncPostgresSaver` backed by an asynchronous connection pool (`psycopg_pool.AsyncConnectionPool`).
   - Automatically provisions and manages PostgreSQL checkpoint tables (`checkpoints`, `checkpoint_writes`, `checkpoint_blobs`).
2. **FastAPI Lifespan Schema Initialization:**
   - In `backend/app/main.py` (`lifespan`), calls `await get_checkpointer()` during startup to verify connection and provision checkpoint tables ahead of runtime requests.
3. **Dual-Engine Test Fallback:**
   - When running unit tests or local SQLite fallback (`USE_SQLITE=true`), `get_checkpointer()` gracefully falls back to `MemorySaver()`, ensuring 100% test pass rate (35/35 tests) without requiring a live PostgreSQL daemon.
4. **Dynamic Graph Compilation & Checkpoint Binding:**
   - Parameterized `build_matter_analysis_graph(checkpointer=...)`. Both `run_matter_analysis_workflow()` and `resume_matter_analysis_workflow()` dynamically acquire the persistent checkpointer and execute graph updates against persistent storage.
5. **Conditional Post-Review Routing:**
   - Integrated `route_after_review()`:
     - `ACCEPT` / `OVERRIDE` $\to$ clears review flag and routes back to `supervisor` to finalize downstream tasks.
     - `REJECT` $\to$ terminates graph with deficiency status and presents client request action items.

---

## 4. Consequences & Improvements

### Positive
* **Durability:** Active legal matter workflows survive container redeployments, server restarts, and long attorney review intervals.
* **Audit Lineage Compliance:** Every attorney decision (`ACCEPT`, `REJECT`, `OVERRIDE`) and justification note is durably bound to the `human_reviews` PostgreSQL table.
* **Zero-Regress Testing:** Dual-mode checkpointer allows all pytest suites to run fast and isolated in SQLite memory while production runs on persistent PostgreSQL.

### Trade-offs
* Requires `psycopg[binary,pool]` and `langgraph-checkpoint-postgres` dependencies in production deployment.
