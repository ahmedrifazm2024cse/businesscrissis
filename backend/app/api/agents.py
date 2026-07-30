from fastapi import APIRouter
from app.models.domain import AgentResult, Workflow
from typing import List

router = APIRouter()

# Core list of agents defined in our system
CORE_AGENTS = [
    "Cybersecurity", "Legal & Compliance", "Financial Risk", 
    "Supply Chain", "Market Intelligence", "Customer Reputation", 
    "Operations", "HR", "Communication & PR", "Strategy", 
    "Predictive Analytics", "Executive Decision", "Report Generator", "Workflow Manager"
]

@router.get("/")
async def list_agents():
    # Base list of agents
    agents_info = []
    for idx, name in enumerate(CORE_AGENTS):
        agents_info.append({
            "id": name, # Frontend matches by name as ID
            "name": name,
            "type": "Analysis" if idx < 8 else ("Strategy" if idx < 12 else "Output"),
            "status": "idle",
            "cpu": "12%",
            "mem": "256MB",
            "latency": "45ms",
            "task": "Awaiting instructions...",
            "output": None
        })
        
    # Get the latest active or completed workflow
    latest_workflow = await Workflow.find().sort("-created_at").first_or_none()
    
    if latest_workflow:
        # Check if it's active
        workflow_active = latest_workflow.status == "in_progress"
        
        # Get all agent results for this workflow
        results = await AgentResult.find({"workflow_id": latest_workflow.id}).to_list()
        
        # Map completed agents
        completed_agents = {res.agent_name: res.output for res in results}
        
        for agent in agents_info:
            if agent["name"] in completed_agents:
                agent["status"] = "completed"
                agent["output"] = completed_agents[agent["name"]]
                agent["task"] = "Task completed."
            elif workflow_active:
                # If workflow is active but agent hasn't completed, it might be running or waiting.
                # For simplicity, if it's not completed and workflow is active, we can set waiting or running
                # Let's say if it's the Orchestrator, it's running
                if agent["name"] == "Workflow Manager":
                    agent["status"] = "running"
                    agent["task"] = "Orchestrating agents..."
                else:
                    agent["status"] = "idle" # Frontend will update to running via WS

    return {
        "status": "success",
        "agents": agents_info
    }

