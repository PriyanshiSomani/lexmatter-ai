# ADR-011: Containerized Deployment Architecture

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Deploying an agentic legal platform with vector databases, Python AI runtimes, PDF parsing tools (PyMuPDF), and Node.js frontend frameworks creates environment configuration drift if services are run natively on local host systems.

---

## 2. Decision

We mandate a fully containerized deployment strategy managed via **Docker** and **Docker Compose** (`docker-compose.yml`):

1. **Database Container (`postgres`):** PostgreSQL 16 container with `pgvector` pre-installed, exposing volume persistence and vector similarity extensions.
2. **Backend API Container (`backend/Dockerfile`):** Python 3.11/3.13 container running FastAPI via `uvicorn`, pre-configured with Alembic migrations and PyMuPDF bindings.
3. **Frontend Container (`frontend/Dockerfile`):** Node.js multi-stage container building Next.js application bundles.
4. **Health Check Polling:** Docker Compose health check dependencies ensuring PostgreSQL vector extensions are fully initialized before API server startup.

---

## 3. Consequences

### Positive
* **Environment Parity:** Identical execution behavior across local developer workstations, CI/CD pipelines, and cloud production hosting.
* **Simplified Setup:** Single command `docker compose up --build` launches the complete multi-tier system.

### Trade-offs
* Docker build times and local container resource overhead (RAM/CPU allocation).
