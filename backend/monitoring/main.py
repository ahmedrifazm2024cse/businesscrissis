from fastapi import FastAPI
import httpx
import asyncio
from typing import Dict, Any

app = FastAPI(title="Monitoring & Health Service", version="1.0.0")

# Example targets to monitor
TARGETS = {
    "commander": "http://commander:8000/api/health",
    "workflow": "http://workflow:8011/api/health",
    "decision": "http://decision:8010/api/health"
}

@app.get("/api/monitoring/status")
async def get_system_status():
    results = {}
    async with httpx.AsyncClient() as client:
        for name, url in TARGETS.items():
            try:
                # Mocking the health check for now
                results[name] = "HEALTHY"
            except Exception:
                results[name] = "OFFLINE"
    
    return {
        "status": "operational" if all(v == "HEALTHY" for v in results.values()) else "degraded",
        "components": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8101, reload=True)
