from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # AI API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # AI Models
    primary_model: str = "gpt-4o"
    fallback_model: str = "claude-3-5-sonnet-20241022"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/lexguardian"
    redis_url: str = "redis://localhost:6379"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # App
    app_env: str = "development"
    secret_key: str = "dev-secret-key"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
