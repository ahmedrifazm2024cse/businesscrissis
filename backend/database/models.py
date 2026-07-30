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

class AgentRegistry(Document):
    agent_id: str
    name: str
    domain: str
    status: str = "online"
    capabilities: List[str]
    last_ping: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "agent_registry"

class WorkflowHistory(Document):
    workflow_id: str
    crisis_description: str
    severity: str
    status: str
    executed_agents: List[str] = []
    agent_outputs: Dict[str, Any] = {}
    executive_decision: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "workflow_history"

class KnowledgeItem(Document):
    title: str
    content: str
    tags: List[str] = []
    source: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "knowledge_base"

class Report(Document):
    workflow_id: str
    title: str
    content: str
    generated_by: str = "Report Agent"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reports"
