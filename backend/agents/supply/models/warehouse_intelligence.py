from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class WarehouseCapacity(Document):
    warehouse_id: str
    total_capacity: float
    used_capacity: float
    available_capacity: float
    utilization_percentage: float
    rack_utilization: float
    shelf_utilization: float
    cold_storage_used: float
    cold_storage_capacity: float
    zone_utilization: Dict[str, float]
    recorded_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_capacity"

class WarehousePerformance(Document):
    warehouse_id: str
    inventory_turnover_rate: float
    picking_efficiency: float
    receiving_efficiency: float
    shipping_efficiency: float
    avg_order_processing_time_hours: float
    avg_loading_time_hours: float
    avg_unloading_time_hours: float
    recorded_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_metrics"

class WarehousePrediction(Document):
    warehouse_id: str
    predicted_full_date: Optional[datetime] = None
    capacity_remaining_days: Optional[float] = None
    storage_growth_trend: float
    overflow_risk_score: float # 0-100
    expansion_requirement: bool
    confidence_score: float
    predicted_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_predictions"

class WarehouseRisk(Document):
    warehouse_id: str
    fire_risk: float
    flood_risk: float
    equipment_risk: float
    power_outage_risk: float
    temperature_risk: float
    inventory_damage_risk: float
    security_risk: float
    overall_risk_score: float # 0-100
    health_score: float # 0-100
    bottlenecks_detected: List[str]
    assessed_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_health"

class WarehouseRecommendation(Document):
    warehouse_id: str
    action_type: str # "Move Inventory", "Expand", "Redistribute"
    reason: str
    priority: str # "High", "Medium", "Low"
    expected_business_impact: str
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_recommendations"

class WarehouseAlert(Document):
    warehouse_id: str
    title: str
    message: str
    severity: str # "Low", "Medium", "High", "Critical"
    event_type: str # "Capacity Breach", "Equipment Failure"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_alerts"

class WarehouseHistory(Document):
    warehouse_id: str
    date: datetime = Field(default_factory=utc_now)
    utilization_percentage: float
    health_score: float
    event_summary: str
    
    class Settings:
        name = "warehouse_history"

class WarehouseAIAnalysis(Document):
    warehouse_id: str
    root_cause: str
    warehouse_summary: str
    operational_risks: str
    business_impact: str
    optimization_strategy: str
    recovery_plan: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouse_ai_analysis"
