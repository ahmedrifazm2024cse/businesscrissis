from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document
from pydantic import Field

class User(Document):
    email: str
    hashed_password: str
    role: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class Incident(Document):
    title: str
    description: str
    severity: str
    status: str = "active"
    reported_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "incidents"

class Workflow(Document):
    incident_id: str
    status: str = "running"
    current_agent: Optional[str] = None
    executed_agents: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "workflows"

class AgentResult(Document):
    workflow_id: str
    agent_name: str
    output: Dict[str, Any]
    status: str = "completed"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "agent_results"

class Report(Document):
    workflow_id: str
    title: str
    content: str
    generated_by: str = "Report Agent"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reports"

class Notification(Document):
    type: str
    title: str
    message: str
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"

class ChatHistory(Document):
    session_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_history"

class BusinessMetric(Document):
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "business_metrics"

class AuditLog(Document):
    action: str
    user_id: Optional[str] = None
    details: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"

class SystemSetting(Document):
    key: str
    value: Any
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "settings"
