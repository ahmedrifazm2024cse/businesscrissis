from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from workflows.crisis_workflow import crisis_graph
from repositories.domain_repos import coordinator_message_repo
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coordinator", tags=["Coordinator"])

class CoordinatorRequest(BaseModel):
    task_id: str
    crisis_object: Optional[Dict[str, Any]] = None
    shared_context: Optional[Dict[str, Any]] = None

class CoordinatorResponse(BaseModel):
    agent: str = "Supply Chain Agent"
    finding: str
    confidence: float
    severity: str
    recommendations: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    contributing_evidence: List[Dict[str, Any]]

async def process_coordinator_task(task_id: str, trigger: str):
    logger.info(f"Processing background coordinator task: {task_id}")
    try:
        # Run the LangGraph workflow
        result = await crisis_graph.ainvoke({"trigger_event": trigger})
        
        # In a real scenario, we'd send a webhook back to the Coordinator here.
        # For now, we save it to the DB.
        payload = result.get("coordinator_payload", {})
        
        await coordinator_message_repo.create({
            "message_id": task_id,
            "direction": "outbound",
            "payload": payload,
            "status": "completed"
        })
        logger.info(f"Task {task_id} completed successfully.")
    except Exception as e:
        logger.error(f"Failed to process task {task_id}: {e}")
        await coordinator_message_repo.create({
            "message_id": task_id,
            "direction": "outbound",
            "payload": {"error": str(e)},
            "status": "failed"
        })

@router.post("/trigger", response_model=Dict[str, str])
async def trigger_agent(request: CoordinatorRequest, background_tasks: BackgroundTasks):
    """
    Endpoint for the Coordinator to trigger the Supply Chain Agent.
    """
    # Log incoming message
    await coordinator_message_repo.create({
        "message_id": request.task_id,
        "direction": "inbound",
        "payload": request.model_dump(),
        "status": "received"
    })
    
    # Process asynchronously to avoid blocking the coordinator
    background_tasks.add_task(process_coordinator_task, request.task_id, "Coordinator Trigger")
    
    return {"status": "accepted", "task_id": request.task_id}

@router.get("/result/{task_id}", response_model=Dict[str, Any])
async def get_result(task_id: str):
    """
    Polling endpoint for Coordinator if webhooks aren't used.
    """
    results = await coordinator_message_repo.get_multi_by_query({
        "message_id": task_id,
        "direction": "outbound"
    })
    
    if not results:
        raise HTTPException(status_code=404, detail="Result not found or still processing.")
    
    return results[0].payload
