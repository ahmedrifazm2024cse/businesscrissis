import uuid
import logging
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.shared.memory import memory
from backend.shared.eventbus import eventbus
from backend.workflow.manager import WorkflowManager

logger = logging.getLogger(__name__)
router = APIRouter()
workflow_manager = WorkflowManager()

class CrisisInput(BaseModel):
    description: str

@router.post("/crisis")
async def handle_crisis(crisis: CrisisInput):
    workflow_id = str(uuid.uuid4())
    logger.info(f"Received new crisis: {crisis.description}. Initiating workflow {workflow_id}")
    
    # 1. Initialize Shared Memory
    memory.initialize_workflow(workflow_id)
    memory.write(workflow_id, "crisis_description", crisis.description)
    memory.write(workflow_id, "status", "analyzing")
    
    # 2. Publish Event
    await eventbus.publish("crisis_received", {
        "workflow_id": workflow_id,
        "description": crisis.description
    })
    
    # 3. Commander uses Workflow Manager to analyze and build strategy
    asyncio.create_task(workflow_manager.execute_workflow(workflow_id, crisis.description))
    
    return {
        "status": "success",
        "workflow_id": workflow_id,
        "message": "Crisis received. Commander is analyzing and deploying agents."
    }

@router.get("/status/{workflow_id}")
async def get_status(workflow_id: str):
    state = memory.read_all(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Inject agent_outputs for legacy handlers compatibility
    state["agent_outputs"] = {
        "customer_reputation": state.get("customer_analysis"),
        "cyberagent": state.get("cyber_analysis"),
        "financial": state.get("finance_analysis"),
        "supply_chain": state.get("supply_analysis"),
        "legal": state.get("legal_analysis"),
        "market": state.get("market_analysis")
    }
    return state

@router.get("/health")
async def health_check():
    return {"status": "healthy", "commander": "online", "agents_registered": 13}

@router.get("/agents")
async def get_agents():
    # Return simulated or actual agent registry
    return {
        "status": "success",
        "agents": [
            {"name": "Customer Reputation Agent", "status": "online", "domain": "customer"},
            {"name": "Market Intelligence Agent", "status": "online", "domain": "market"},
            {"name": "Financial Agent", "status": "online", "domain": "finance"},
            {"name": "Supply Chain Agent", "status": "online", "domain": "supply"},
            {"name": "Cyber Security Agent", "status": "online", "domain": "cyber"},
            {"name": "Legal Compliance Agent", "status": "online", "domain": "legal"}
        ]
    }
