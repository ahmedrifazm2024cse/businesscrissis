from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "admin"

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime

# Incident / Crisis Schemas
class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str
    reported_by: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    reported_by: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

# Workflow Schemas
class WorkflowResponse(BaseModel):
    id: str
    incident_id: str
    status: str
    current_agent: Optional[str]
    executed_agents: List[str]
    created_at: datetime
    completed_at: Optional[datetime]

# Agent Schemas
class AgentResultResponse(BaseModel):
    id: str
    workflow_id: str
    agent_name: str
    output: Dict[str, Any]
    status: str
    error_message: Optional[str]
    created_at: datetime

# Report Schemas
class ReportResponse(BaseModel):
    id: str
    workflow_id: str
    title: str
    content: str
    generated_by: str
    created_at: datetime

# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    read: bool
    created_at: datetime

# Chat Schemas
class ChatMessageCreate(BaseModel):
    session_id: str
    content: str

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: datetime

# Metrics Schemas
class BusinessMetricResponse(BaseModel):
    id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: str
    action: str
    user_id: Optional[str]
    details: str
    timestamp: datetime

# Settings Schemas
class SystemSettingUpdate(BaseModel):
    value: Any

class SystemSettingResponse(BaseModel):
    id: str
    key: str
    value: Any
    updated_at: datetime
