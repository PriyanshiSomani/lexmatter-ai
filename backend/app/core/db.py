"""
LexMatter AI — Database Engine and Asynchronous Session Management
Phase 2 / Phase 13: PostgreSQL & SQLite Dual Engine Support
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import settings

# SQLite DDL Compilation Hooks for PostgreSQL-specific dialect types
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(Vector, "sqlite")
def compile_vector_sqlite(type_, compiler, **kw):
    return "JSON"


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 ORM models."""
    pass


# Select engine URL: Default to SQLite for local development unless USE_SQLITE=false or running in container
use_sqlite = os.getenv("USE_SQLITE", "true").lower() == "true" or "sqlite" in settings.DATABASE_URL
db_url = "sqlite+aiosqlite:///./lexmatter_dev.db" if use_sqlite else settings.DATABASE_URL

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
engine_kwargs = {"connect_args": connect_args} if "sqlite" in db_url else {
    "pool_size": settings.DB_POOL_SIZE,
    "max_overflow": settings.DB_MAX_OVERFLOW,
}

# Async database engine (silence raw SQL engine output by default for clean application logs)
sql_echo = os.getenv("SQL_ECHO", "false").lower() == "true"
engine: AsyncEngine = create_async_engine(
    db_url,
    echo=sql_echo,
    future=True,
    **engine_kwargs,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Create all database tables on application startup."""
    # Import all models to register with Base.metadata
    import backend.app.models.source
    import backend.app.models.extraction
    import backend.app.models.knowledge
    import backend.app.models.legal
    import backend.app.models.analysis
    import backend.app.models.audit

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
