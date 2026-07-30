from fastapi import FastAPI
from typing import List, Dict, Any

app = FastAPI(title="Enterprise Communication Facade", version="1.0.0")

# Agent discovery registry
discovery_registry: Dict[str, Dict[str, Any]] = {}

@app.post("/api/communication/register")
async def register_agent(agent_name: str, capabilities: List[str], version: str):
    discovery_registry[agent_name] = {
        "capabilities": capabilities,
        "version": version,
        "status": "online"
    }
    return {"status": "registered", "agent": agent_name}

@app.get("/api/communication/agents")
async def list_agents():
    return discovery_registry

@app.get("/api/communication/match")
async def match_capability(capability: str):
    matches = []
    for name, meta in discovery_registry.items():
        if capability in meta.get("capabilities", []):
            matches.append(name)
    return {"capability": capability, "matched_agents": matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8104, reload=True)
