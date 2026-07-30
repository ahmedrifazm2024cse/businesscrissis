from fastapi import FastAPI
from pydantic import BaseSettings
from functools import lru_cache

app = FastAPI(title="Configuration Service", version="1.0.0")

class Settings(BaseSettings):
    platform_name: str = "Agentverse Enterprise"
    environment: str = "production"
    max_retries: int = 3
    workflow_timeout_seconds: int = 300
    cache_enabled: bool = True

@lru_cache()
def get_settings():
    return Settings()

@app.get("/api/config")
async def read_config():
    return get_settings()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8103, reload=True)
