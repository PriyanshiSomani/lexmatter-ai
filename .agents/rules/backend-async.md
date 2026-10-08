# Rule: Backend FastAPI & Async Database Guidelines

## 1. Async Session Lifecycle
* Use SQLAlchemy 2.0 `AsyncSession` with `asyncpg` for PostgreSQL and `aiosqlite` for test fallbacks.
* Inject sessions via FastAPI dependency: `db: AsyncSession = Depends(get_db)`.
* Always use `await db.commit()` or `await db.rollback()` within structured exception blocks.

## 2. Granular Evaluation & Flush Order (ADR-013)
* When inserting mapped entities in nested loops (e.g. `EvidenceMapping` during requirement evaluation):
  - Always execute `await db.flush()` immediately after adding records before running count/aggregate queries within the same transaction.
  - Failure to flush leads to undercounting ($N-1$) in active dimension support checks.

## 3. Pydantic 2.0 Schemas
* Keep domain schemas in `backend/app/schemas/` separate from database models in `backend/app/models/`.
* Use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.
