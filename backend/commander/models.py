from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentResponseMetadata(BaseModel):
    execution_time_ms: int
    timestamp: str
    version: str

class AgentResponse(BaseModel):
    """Common JSON Schema that every agent MUST return"""
    status: str = Field(..., description="'success' or 'error'")
    agent_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_score: int = Field(..., ge=1, le=10)
    findings: List[str]
    recommendations: List[str]
    data: Dict[str, Any] = {}
    metadata: AgentResponseMetadata

class CrisisRequest(BaseModel):
    crisis_id: str
    description: str
    severity: str
    context: Dict[str, Any]

class ExecutiveSummary(BaseModel):
    executive_summary: str
    business_impact: str
    financial_impact: str
    operational_impact: str
    legal_risk: str
    cyber_risk: str
    reputation_risk: str
    priority_score: int
    recommended_actions: List[str]
    short_term_plan: str
    long_term_strategy: str

class CommanderResponse(BaseModel):
    crisis_id: str
    global_status: str
    executive_report: ExecutiveSummary
    agent_responses: Dict[str, AgentResponse]
