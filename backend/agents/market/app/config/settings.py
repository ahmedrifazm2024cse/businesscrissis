import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./market_intelligence.db"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o"
    SAMPLE_DATA_DIR: str = "../sample-data"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
