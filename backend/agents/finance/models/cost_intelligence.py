from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class CostAnalysis(Document):
    analysis_id: str
    inventory_holding_cost: float
    warehouse_cost: float
    transportation_cost: float
    procurement_cost: float
    supplier_cost: float
    fuel_cost: float
    emergency_shipping_cost: float
    total_cost: float
    date: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_analysis"

class CostTrend(Document):
    period: str # "Daily", "Weekly", "Monthly", "Quarterly", "Yearly"
    total_cost: float
    growth_percentage: float
    reduction_percentage: float
    date: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_trends"

class CostPrediction(Document):
    predicted_future_cost: float
    predicted_inventory_cost: float
    predicted_warehouse_cost: float
    predicted_transportation_cost: float
    predicted_procurement_cost: float
    confidence_score: float
    predicted_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_predictions"

class BudgetMonitoring(Document):
    department: str # "Warehouse", "Procurement", "Transportation", "Inventory"
    allocated_budget: float
    actual_spend: float
    variance: float
    status: str # "Under Budget", "On Track", "Over Budget"
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "budget_monitoring"

class CostRecommendation(Document):
    recommendation_id: str
    action_type: str # "Change Supplier", "Consolidate Shipments", "Move Inventory"
    reason: str
    estimated_savings: float
    priority: str # "Low", "Medium", "High"
    business_impact: str
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_recommendations"

class CostAlert(Document):
    alert_id: str
    title: str
    message: str
    severity: str # "Warning", "Critical"
    department: str
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_alerts"

class CostHistory(Document):
    action_taken: str
    savings_realized: float
    department: str
    date: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_history"

class CostAIAnalysis(Document):
    analysis_id: str
    root_cause: str
    cost_summary: str
    cost_drivers: List[str]
    business_impact: str
    optimization_strategy: str
    long_term_savings_plan: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "cost_ai_analysis"
