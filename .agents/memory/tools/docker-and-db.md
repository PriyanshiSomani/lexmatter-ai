# Tool Guide: Docker & Dual-Engine Database Strategy (ADR-016)

## 1. Production / Docker Database (PostgreSQL + pgvector)
* **Image:** `pgvector/pgvector:pg16`
* **Default Port:** `5432`
* **Database Name:** `lexmatter_db`
* **User/Password:** `lexmatter_user` / `lexmatter_password`
* **Connection String:**
  ```text
  postgresql+asyncpg://lexmatter_user:lexmatter_password@localhost:5432/lexmatter_db
  ```
* **Extensions:** `CREATE EXTENSION IF NOT EXISTS vector;`

## 2. In-Memory / Local SQLite Fallback Engine
* When PostgreSQL is unavailable or during fast unit test runs:
  - System switches to in-memory SQLite (`sqlite+aiosqlite:///:memory:`).
  - Simulates vector embeddings in memory for isolated test verification.
  - Documented in `ADR-016`.
