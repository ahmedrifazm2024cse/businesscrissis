from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time

class AgentRegistration(BaseModel):
    name: str
    capabilities: List[str]
    status: str = "online"
    health: str = "healthy"
    version: str = "1.0.0"
    endpoint: str
    priority: int = 1
    dependencies: List[str] = []

class ExecutePayload(BaseModel):
    workflow_id: str
    crisis_id: str
    description: str
    severity: str
    context: Dict[str, Any]

class StandardResponseMetadata(BaseModel):
    execution_time_ms: int = 0
    timestamp: str = ""
    version: str = "1.0.0"

class StandardResponse(BaseModel):
    agent_name: str
    status: str
    confidence: float
    risk_score: int
    findings: List[str]
    recommendations: List[str]
    data: Dict[str, Any] = {}
    metadata: StandardResponseMetadata
