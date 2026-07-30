from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Business Crisis Commander"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Security
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    MONGODB_URI: str
    
    # Redis
    REDIS_URL: str
    
    # AI
    GEMINI_API_KEY: str
    
    # External APIs
    WEATHER_API_KEY: str
    OPENROUTESERVICE_API_KEY: str
    NEWS_API_KEY: str
    EXCHANGE_RATE_API_KEY: str
    
    # Optional APIs
    RESEND_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file="../.env", case_sensitive=True, extra="ignore")

settings = Settings()
