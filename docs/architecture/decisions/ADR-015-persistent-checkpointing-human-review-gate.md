# ADR-015: Persistent Checkpointing & Interrupt/Resume Human-Review Gate

* **Status:** Accepted
* **Date:** 2026-09-26
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

In the initial LangGraph orchestration setup:
1. **Temporary In-Memory State:** Workflow checkpointers used `MemorySaver()`, which stored graph state purely in Python RAM. A server restart or worker crash destroyed all active matter execution threads.
2. **Flag-and-Finish Human Review:** The `human_review` node set `requires_human_review = True` and transitioned directly to `END`. This meant human review acted as a terminal flag rather than an interactive pause/resume gate.

---

## 2. Decision

We established the architecture for persistent checkpointing and interactive human review gates:

1. **Durable Database Checkpointer (`AsyncPostgresSaver`):** Replace in-memory checkpointers with PostgreSQL-backed graph checkpointers (`AsyncPostgresSaver`). Graph thread states persist durably across server lifecycles.
2. **LangGraph Interrupt & Resume Workflows:** Reconfigure `human_review_node` using LangGraph `interrupt()` primitives. When human review is triggered:
   - Graph execution pauses and persists state at the `human_review` checkpoint.
   - An attorney reviews findings via the UI and submits an action (`Accept`, `Reject`, or `Override`).
   - The backend API (`POST /api/v1/orchestration/matters/{id}/resume`) invokes `graph.update_state()` with attorney decisions and resumes execution seamlessly.

---

## 3. Consequences

### Positive
* **Resilience:** Thread execution survives application restarts and container redeployments.
* **True Human-in-the-Loop:** Supports asynchronous attorney review workflows where execution waits hours or days for human decisions.

### Trade-offs
* Requires dedicated database tables (`checkpoints`, `checkpoint_writes`) managed by LangGraph migration hooks.
