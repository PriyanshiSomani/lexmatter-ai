"""
LexMatter AI — FastAPI Main Application Server
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.db import init_db
from backend.app.core.logger import get_logger
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.extraction import router as extraction_router
from backend.app.api.v1.retrieval import router as retrieval_router
from backend.app.api.v1.requirements import router as requirements_router
from backend.app.api.v1.conflicts import router as conflicts_router
from backend.app.api.v1.evidence import router as evidence_router
from backend.app.api.v1.orchestration import router as orchestration_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.audit import router as audit_router

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: handles automatic DB table creation with fallback."""
    logger.info(f"Starting {settings.PROJECT_NAME} application server (Environment: {settings.ENVIRONMENT})...")
    try:
        await init_db()
        logger.info("Database connection & ORM tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Primary database connection failed ({e}). Switching to local SQLite engine...")
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
        logger.info("Local SQLite database engine initialized (lexmatter_dev.db).")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} application server...")


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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured request/response duration and status logging middleware."""
    start_time = time.time()
    path = request.url.path
    query = request.url.query
    full_path = f"{path}?{query}" if query else path
    client_ip = request.client.host if request.client else "unknown"

    logger.info(f"--> {request.method} {full_path} (Client IP: {client_ip})")
    try:
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        if response.status_code >= 500:
            logger.error(f"<-- {request.method} {full_path} | HTTP {response.status_code} SERVER ERROR | Duration: {process_time_ms:.2f}ms")
        else:
            logger.info(f"<-- {request.method} {full_path} | Status: {response.status_code} | Duration: {process_time_ms:.2f}ms")
        return response
    except Exception as exc:
        process_time_ms = (time.time() - start_time) * 1000
        logger.error(f"<-- {request.method} {full_path} | UNHANDLED EXCEPTION: {str(exc)} | Duration: {process_time_ms:.2f}ms", exc_info=True)
        raise

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
