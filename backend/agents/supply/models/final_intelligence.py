from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class BusinessImpactAssessment(Document):
    assessment_id: str
    revenue_loss: float
    profit_loss: float
    inventory_loss: float
    recovery_cost: float
    recovery_time_days: float
    business_impact_score: float # 0 to 100
    business_risk_score: float # 0 to 100
    business_health_score: float # 0 to 100
    crisis_severity: str # "Low", "Medium", "High", "Critical"
    executive_summary: str
    root_cause: str
    business_explanation: str
    risk_explanation: str
    recovery_plan: str
    business_recommendation: str
    priority: str
    expected_business_outcome: str
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "business_impact_assessments"

class DecisionHistory(Document):
    decision_id: str
    trigger_event: str
    context_summary: str
    decision_taken: str
    reasoning: str
    confidence: float
    status: str # e.g., "Executed", "Pending", "Failed"
    timestamp: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "decision_history"

class BusinessHistory(Document):
    snapshot_id: str
    health_score: float
    risk_score: float
    impact_score: float
    active_crises_count: int
    timestamp: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "business_history"

class CrisisHistory(Document):
    crisis_id: str
    severity: str
    root_cause: str
    impact_estimate: float
    recovery_time_actual: Optional[float] = None
    status: str # "Active", "Resolved"
    identified_at: datetime = Field(default_factory=utc_now)
    resolved_at: Optional[datetime] = None

    class Settings:
        name = "crisis_history"

class RecommendationHistory(Document):
    recommendation_id: str
    agent_source: str
    recommendation: str
    priority: str
    outcome: Optional[str] = None
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "recommendation_history"

class LearningHistory(Document):
    learning_id: str
    crisis_id: Optional[str] = None
    lesson_learned: str
    strategy_adjustment: str
    confidence_improvement: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "learning_history"

class CoordinatorHistory(Document):
    interaction_id: str
    direction: str # "inbound" or "outbound"
    payload: Dict[str, Any]
    status: str
    timestamp: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "coordinator_history"
