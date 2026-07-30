from fastapi import APIRouter
from app.models.domain import User, AuditLog, SystemSetting
from pydantic import BaseModel
from typing import List

router = APIRouter()

@router.get("/users")
async def list_users():
    users = await User.find_all().to_list()
    # Mask passwords
    for user in users:
        user.hashed_password = "***"
    return {"status": "success", "users": users}

@router.get("/audit")
async def list_audit_logs():
    logs = await AuditLog.find_all().to_list()
    return {"status": "success", "logs": logs}

@router.get("/health")
async def system_health():
    # In a real app, this would check DB connections, agent statuses, etc.
    return {
        "status": "healthy",
        "database": "connected",
        "uptime": "99.9%",
        "active_agents": 12
    }
