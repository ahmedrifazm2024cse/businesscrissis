from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import sys
import os
import uuid
import datetime
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.models import WorkflowSchema, TaskInfo

app = FastAPI(title="Workflow Engine & Task Queue", version="1.0.0")

# In-memory storage for workflows
workflows_store: Dict[str, WorkflowSchema] = {}

COMMANDER_URL = os.getenv("COMMANDER_URL", "http://localhost:8000")

async def fetch_agent_capabilities() -> Dict[str, List[str]]:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{COMMANDER_URL}/api/registry/capabilities")
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print("Failed to fetch capabilities from Commander:", e)
    return {}

def map_capabilities_to_agents(description: str, agent_caps: Dict[str, List[str]]) -> List[str]:
    """Matches words in description to agent capabilities."""
    selected_agents = set()
    desc_lower = description.lower()
    
    # We always need the communication agent, decision agent, report generator, etc. (Executive suite)
    # The orchestration will handle executive agents mostly via events, but for business agents we select dynamically.
    for agent, caps in agent_caps.items():
        for cap in caps:
            # simple keyword match
            if cap.lower() in desc_lower:
                selected_agents.add(agent)
                break
    
    # Fallback mappings for MVP
    if "cyber" in desc_lower or "hack" in desc_lower or "breach" in desc_lower:
        selected_agents.add("cyberagent")
    if "supply" in desc_lower or "logistics" in desc_lower:
        selected_agents.add("supply_chain")
    if "social media" in desc_lower or "reputation" in desc_lower:
        selected_agents.add("customer_reputation")
    if "finance" in desc_lower or "revenue" in desc_lower:
        selected_agents.add("financial")
    if "legal" in desc_lower or "lawsuit" in desc_lower:
        selected_agents.add("legal_compliance")
    if "competitor" in desc_lower or "market" in desc_lower:
        selected_agents.add("market_intelligence")
        
    return list(selected_agents)

async def calculate_dag(description: str) -> List[TaskInfo]:
    agent_caps = await fetch_agent_capabilities()
    selected = map_capabilities_to_agents(description, agent_caps)
    
    if not selected:
        selected = ["market_intelligence", "customer_reputation"] # Fallback
        
    tasks = []
    
    # All selected agents run in parallel for MVP DAG
    for agent in selected:
        tasks.append(TaskInfo(
            task_id=f"T-{uuid.uuid4().hex[:6]}",
            assigned_agent=agent,
            priority="HIGH",
            deadline=(datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).isoformat(),
            dependencies=[],
            status="queued",
            retries_attempted=0
        ))
        
    return tasks

@app.post("/api/workflow/initiate", response_model=WorkflowSchema)
async def initiate_workflow(crisis_id: str, payload: Dict[str, Any]):
    workflow_id = f"WF-{uuid.uuid4().hex[:8]}"
    description = payload.get("description", "")
    
    tasks = await calculate_dag(description)
    
    wf = WorkflowSchema(
        workflow_id=workflow_id,
        crisis_id=crisis_id,
        status="in_progress",
        execution_mode="dynamic_dependency",
        tasks=tasks
    )
    
    workflows_store[workflow_id] = wf
    return wf

@app.get("/api/workflow/{workflow_id}", response_model=WorkflowSchema)
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows_store:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows_store[workflow_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8103, reload=True)

