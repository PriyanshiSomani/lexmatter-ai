"""
LexMatter AI — Application Settings & Configuration
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "LexMatter AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://lexmatter_user:lexmatter_dev_password@localhost:5432/lexmatter_db"
    SYNC_DATABASE_URL: str = "postgresql://lexmatter_user:lexmatter_dev_password@localhost:5432/lexmatter_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Storage
    UPLOAD_STORAGE_PATH: str = "./storage/uploads"
    PREVIEW_STORAGE_PATH: str = "./storage/previews"

    # Embeddings
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    EMBEDDING_DIMENSION: int = 768

    # LLM Integrations
    GOOGLE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"


settings = Settings()
