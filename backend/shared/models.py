from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class EventPayload(BaseModel):
    event_id: str
    event_type: str
    timestamp: float
    publisher: str
    workflow_id: Optional[str] = None
    crisis_id: Optional[str] = None
    data: Dict[str, Any] = {}

class TaskInfo(BaseModel):
    task_id: str
    assigned_agent: str
    priority: str
    deadline: str
    dependencies: List[str]
    status: str
    retries_attempted: int

class WorkflowSchema(BaseModel):
    workflow_id: str
    crisis_id: str
    status: str
    execution_mode: str
    tasks: List[TaskInfo]

class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    duration_ms: Optional[int] = None

class MemorySchema(BaseModel):
    crisis_id: str
    conversation_id: str
    timeline: List[TimelineEvent] = []
    agent_outputs: Dict[str, Any] = {}
