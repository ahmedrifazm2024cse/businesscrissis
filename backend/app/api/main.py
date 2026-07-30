from fastapi import APIRouter
from app.api import auth, dashboard, workflow, agents, reports, chat, notifications, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
