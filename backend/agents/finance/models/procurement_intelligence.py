from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class PurchasePlan(Document):
    plan_id: str
    sku: str
    supplier_id: str
    warehouse_id: str
    order_quantity: float
    eoq: float
    safety_stock_requirement: float
    buffer_stock: float
    min_stock: float
    max_stock: float
    timing_strategy: str # "Immediate", "Delay", "Split"
    priority_level: str # "Low", "Medium", "High", "Critical"
    estimated_cost: float
    status: str # "Draft", "Approved", "Executed"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "purchase_plans"

class ProcurementRisk(Document):
    plan_id: str
    supplier_risk: float
    inventory_risk: float
    demand_risk: float
    transportation_risk: float
    currency_risk: float
    political_risk: float
    weather_risk: float
    contract_risk: float
    overall_risk_score: float # 0-100
    confidence_score: float
    assessed_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_risk"

class ProcurementPrediction(Document):
    sku: str
    predicted_price_change: float # percentage, positive or negative
    market_trend: str # "Bullish", "Bearish", "Stable"
    predicted_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_predictions"

class ProcurementRecommendation(Document):
    plan_id: str
    action_type: str # "Split Purchase", "Bulk Purchase", "Change Supplier"
    reason: str
    expected_savings: float
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_recommendations"

class ProcurementAlert(Document):
    alert_id: str
    title: str
    message: str
    severity: str # "Low", "Medium", "High", "Critical"
    event_type: str # "Shortage", "Budget Exceeded", "Supplier Failure"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_alerts"

class ProcurementHistory(Document):
    plan_id: str
    action_taken: str
    savings_realized: float
    date: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_history"

class ProcurementAIAnalysis(Document):
    plan_id: str
    purchase_strategy: str
    negotiation_strategy: str
    supplier_recommendation: str
    expected_savings_explanation: str
    business_impact: str
    risk_mitigation: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "procurement_ai_analysis"
