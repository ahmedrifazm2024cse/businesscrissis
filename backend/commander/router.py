import uuid
import logging
import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.shared.memory import memory
from backend.shared.eventbus import eventbus
from backend.workflow.manager import WorkflowManager

logger = logging.getLogger(__name__)
router = APIRouter()
workflow_manager = WorkflowManager()

class LoginRequest(BaseModel):
    username: str
    password: str

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
    # Return simulated or actual agent registry with 13 agents for UI parity
    return {
        "status": "success",
        "agents": [
            {"id": "1", "name": "Executive Decision", "type": "Executive", "status": "Running", "latency": "45ms", "cpu": "12%", "mem": "1.2GB", "task": "Aggregating Risk Scores"},
            {"id": "2", "name": "Workflow Manager", "type": "Executive", "status": "Running", "latency": "22ms", "cpu": "8%", "mem": "400MB", "task": "Orchestrating DAG"},
            {"id": "3", "name": "Customer Reputation", "type": "Business", "status": "Idle", "latency": "15ms", "cpu": "1%", "mem": "250MB", "task": "Waiting for trigger"},
            {"id": "4", "name": "Market Intelligence", "type": "Business", "status": "Running", "latency": "120ms", "cpu": "45%", "mem": "2.1GB", "task": "Scraping competitor pricing"},
            {"id": "5", "name": "Cyber Security", "type": "Business", "status": "Offline", "latency": "-", "cpu": "0%", "mem": "0MB", "task": "Disconnected"},
            {"id": "6", "name": "Legal Compliance", "type": "Business", "status": "Idle", "latency": "20ms", "cpu": "3%", "mem": "300MB", "task": "Waiting for trigger"},
            {"id": "7", "name": "Financial Analysis", "type": "Business", "status": "Idle", "latency": "18ms", "cpu": "2%", "mem": "280MB", "task": "Waiting for trigger"},
            {"id": "8", "name": "Supply Chain", "type": "Business", "status": "Idle", "latency": "25ms", "cpu": "4%", "mem": "320MB", "task": "Waiting for trigger"},
            {"id": "9", "name": "Human Resources", "type": "Business", "status": "Idle", "latency": "10ms", "cpu": "1%", "mem": "150MB", "task": "Waiting for trigger"},
            {"id": "10", "name": "Public Relations", "type": "Business", "status": "Idle", "latency": "12ms", "cpu": "1%", "mem": "180MB", "task": "Waiting for trigger"},
            {"id": "11", "name": "IT Operations", "type": "Business", "status": "Running", "latency": "5ms", "cpu": "30%", "mem": "1.8GB", "task": "Monitoring system health"},
            {"id": "12", "name": "Risk Management", "type": "Executive", "status": "Idle", "latency": "30ms", "cpu": "5%", "mem": "400MB", "task": "Waiting for trigger"},
            {"id": "13", "name": "Strategic Planning", "type": "Executive", "status": "Idle", "latency": "40ms", "cpu": "6%", "mem": "500MB", "task": "Waiting for trigger"},
        ]
    }

@router.get("/workflows/active")
async def get_active_workflows():
    # Return simulated active workflows/tasks for the dashboard
    return {
        "status": "success",
        "tasks": [
            {"id": "WF-847291", "description": "Awaiting Cyber Agent Response"},
            {"id": "WF-847292", "description": "Market Sentiment Analysis Running"},
            {"id": "WF-847293", "description": "Compiling Executive Summary"}
        ]
        ]
    }

@router.post("/auth")
async def login(req: LoginRequest):
    if req.username == "admin" and req.password == "admin":
        return {"token": "fake-jwt-token-12345", "role": "admin"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
