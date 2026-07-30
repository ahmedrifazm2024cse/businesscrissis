from fastapi import APIRouter
from app.models.domain import Report

router = APIRouter()

@router.get("/")
async def list_reports():
    reports = await Report.find_all().to_list()
    return {"status": "success", "reports": reports}

@router.post("/generate")
async def generate_report(workflow_id: str):
    # Stub for triggering report generation agent
    return {"status": "success", "message": "Report generation initiated for workflow " + workflow_id}
