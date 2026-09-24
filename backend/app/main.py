"""
LexMatter AI — FastAPI Main Application Server
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.db import init_db
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.extraction import router as extraction_router
from backend.app.api.v1.retrieval import router as retrieval_router
from backend.app.api.v1.requirements import router as requirements_router
from backend.app.api.v1.conflicts import router as conflicts_router
from backend.app.api.v1.evidence import router as evidence_router
from backend.app.api.v1.orchestration import router as orchestration_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: handles automatic DB table creation with fallback."""
    try:
        await init_db()
        print("Database connection & tables initialized successfully.")
    except Exception as e:
        print(f"Warning: Primary database connection failed ({e}). Switching to local SQLite engine...")
        import backend.app.core.db as db_mod
        db_mod.engine = db_mod.create_async_engine(
            "sqlite+aiosqlite:///./lexmatter_dev.db",
            connect_args={"check_same_thread": False},
        )
        db_mod.AsyncSessionLocal = db_mod.async_sessionmaker(
            bind=db_mod.engine,
            class_=db_mod.AsyncSession,
            expire_on_commit=False,
        )
        await db_mod.init_db()
        print("Local SQLite database initialized (lexmatter_dev.db).")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic Legal-Matter Intelligence Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(extraction_router, prefix=settings.API_V1_STR)
app.include_router(retrieval_router, prefix=settings.API_V1_STR)
app.include_router(requirements_router, prefix=settings.API_V1_STR)
app.include_router(conflicts_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)
app.include_router(orchestration_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
