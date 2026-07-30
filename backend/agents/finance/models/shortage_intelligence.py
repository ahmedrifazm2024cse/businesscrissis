from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class ProductShortage(Document):
    product_id: str
    sku: str
    current_stock: int
    reserved_stock: int
    incoming_inventory: int
    outgoing_inventory: int
    daily_demand_forecast: float
    safety_stock: int
    reorder_point: int
    buffer_stock: int
    calculated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "product_shortages"

class ShortagePrediction(Document):
    product_id: str
    sku: str
    probability_of_shortage: float # 0.0 to 1.0
    expected_shortage_date: Optional[datetime] = None
    days_remaining: Optional[float] = None
    confidence_score: float # 0.0 to 1.0
    criticality_level: str # "Low", "Medium", "High", "Critical"
    trend: str # "Improving", "Stable", "Worsening"
    predicted_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "shortage_predictions"

class ProductRiskScore(Document):
    product_id: str
    sku: str
    risk_score: float # 0 to 100
    classification: str # "Healthy", "Watch List", "High Risk", "Critical", "Emergency"
    root_causes: List[str]
    revenue_impact_estimate: float
    scored_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "product_risk_scores"

class ShortageAlert(Document):
    alert_id: str
    product_id: str
    sku: str
    title: str
    message: str
    severity: str
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "shortage_alerts"

class ShortageRecommendation(Document):
    recommendation_id: str
    product_id: str
    sku: str
    action_type: str # "Emergency Procurement", "Transfer Inventory", "Switch Supplier", "Adjust Demand"
    reason: str
    priority: str
    expected_impact: str
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "shortage_recommendations"

class ShortageAIAnalysis(Document):
    analysis_id: str
    product_id: str
    sku: str
    root_cause: str
    business_explanation: str
    shortage_summary: str
    recommended_actions: List[str]
    recovery_strategy: str
    long_term_prevention_strategy: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "shortage_ai_analysis"

class ShortageHistory(Document):
    history_id: str
    product_id: str
    sku: str
    shortage_date: datetime
    duration_days: float
    recovery_action_taken: str
    business_outcome: str
    recorded_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "shortage_history"
