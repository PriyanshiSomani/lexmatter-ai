# Project Memory Index

Read this file at session start. Load specific topic files only when relevant to the active task.

| File | Description | Last Updated |
| :--- | :--- | :--- |
| `tools/run-commands.md` | Exact commands for Docker, FastAPI, Next.js, and Pytest | 2026-10-08 |
| `tools/docker-and-db.md` | PostgreSQL pgvector & SQLite dual-engine setup | 2026-10-08 |
| `domain/langgraph-orchestrator.md` | Multi-agent state graph, checkpoints & human review gate | 2026-10-08 |
| `domain/legal-ontology-and-l1b.md` | 21 database tables, L-1B requirements & dimension schema | 2026-10-08 |

---

## Knowledge Lifecycle
1. **Staging:** New gotchas, CLI patterns, or edge cases accumulate in `tools/` or `domain/`.
2. **Promotion:** When stable, promote core architectural constraints to `.agents/rules/` or create an on-demand skill.
3. **Index Sync:** Keep the table above updated whenever memory files are added or modified.
