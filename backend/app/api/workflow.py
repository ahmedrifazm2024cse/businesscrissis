from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.domain import Workflow, Incident
from app.schemas.domain import IncidentCreate
from app.graph.orchestrator import run_orchestrator
import uuid

router = APIRouter()

@router.post("/start")
async def start_workflow(incident_data: IncidentCreate, background_tasks: BackgroundTasks):
    # 1. Create incident record
    incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        reported_by=incident_data.reported_by
    )
    await incident.insert()

    # 2. Create workflow record
    workflow = Workflow(
        incident_id=str(incident.id),
        status="running"
    )
    await workflow.insert()

    # 3. Start LangGraph orchestrator in background
    background_tasks.add_task(run_orchestrator, str(workflow.id), incident.description)

    return {
        "status": "success",
        "workflow_id": str(workflow.id),
        "message": "Crisis received. Orchestrator started."
    }

@router.get("/active")
async def get_active_workflows():
    active = await Workflow.find({"status": "running"}).to_list()
    tasks = []
    for wf in active:
        # Fetch the associated incident to get the description
        incident = await Incident.get(wf.incident_id)
        desc = incident.description if incident else "Unknown task"
        tasks.append({"id": str(wf.id), "description": desc})
        
    return {"status": "success", "tasks": tasks}

@router.get("/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    workflow = await Workflow.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
