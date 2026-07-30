from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import Orchestrator
from models import CrisisRequest, CommanderResponse
from registry import AgentConfig

app = FastAPI(title="Executive Commander Agent", version="1.0.0")
orchestrator = Orchestrator()

@app.post("/api/crisis/analyze", response_model=CommanderResponse)
async def analyze_crisis(request: CrisisRequest):
    """
    Entry point for the Executive Commander Agent.
    Orchestrates the entire multi-agent workflow for a crisis.
    """
    try:
        response = await orchestrator.handle_crisis(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Commander health check and dependent agent status."""
    statuses = await orchestrator.registry.check_health_all()
    return {"status": "online", "agents": statuses}

@app.post("/api/register")
async def register_agent(agent_config: AgentConfig):
    """Dynamically register an agent with the Commander."""
    orchestrator.registry.register_agent(agent_config)
    return {"status": "registered", "agent": agent_config.name}

@app.get("/api/registry/capabilities")
async def get_all_capabilities():
    """Return map of agent names to capabilities."""
    return orchestrator.registry.get_all_capabilities()

if __name__ == "__main__":
    import uvicorn
    # The Commander will run on port 8000 (which used to be the default for the other agents)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
