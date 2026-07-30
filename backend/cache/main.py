from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(title="Cache Service", version="1.0.0")

# In-memory mock for Redis
_cache_store: Dict[str, Any] = {}

@app.post("/api/cache/{key}")
async def set_cache(key: str, value: Any):
    _cache_store[key] = value
    return {"status": "cached"}

@app.get("/api/cache/{key}")
async def get_cache(key: str):
    if key in _cache_store:
        return {"hit": True, "value": _cache_store[key]}
    return {"hit": False, "value": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8104, reload=True)
