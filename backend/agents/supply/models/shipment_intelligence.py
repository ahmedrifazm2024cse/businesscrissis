from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class ShipmentTracking(Document):
    shipment_id: str
    current_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed_kmh: float = 0.0
    distance_remaining_km: float
    travel_time_remaining_hours: float
    progress_percentage: float # 0-100
    last_updated: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_tracking"

class ShipmentETA(Document):
    shipment_id: str
    original_eta: datetime
    updated_eta: datetime
    best_case_eta: datetime
    worst_case_eta: datetime
    most_probable_eta: datetime
    calculated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_eta"

class ShipmentPrediction(Document):
    shipment_id: str
    expected_delay_hours: float
    delay_probability: float # 0.0 - 1.0
    confidence_score: float # 0.0 - 1.0
    root_cause: str
    predicted_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_predictions"

class ShipmentRisk(Document):
    shipment_id: str
    traffic_risk: float
    weather_risk: float
    port_congestion_risk: float
    border_delay_risk: float
    political_risk: float
    overall_risk_score: float # 0-100
    risk_category: str # "Low", "Medium", "High", "Critical"
    health_score: float # 0-100, combines risk + tracking progress
    assessed_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_risk"

class ShipmentRoute(Document):
    shipment_id: str
    target_destination: str
    recommended_routes: List[Dict[str, Any]] 
    # [{"route_name": "I-95", "distance": 500, "estimated_time": "5h", "risk_score": 20, "rank": 1}]
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_routes"

class ShipmentAlert(Document):
    shipment_id: str
    title: str
    message: str
    severity: str # "Low", "Medium", "High", "Critical"
    event_type: str # e.g. "Severe Weather", "Traffic Jam", "Route Deviation"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_alerts"

class ShipmentHistory(Document):
    shipment_id: str
    date: datetime = Field(default_factory=utc_now)
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    event_summary: str
    
    class Settings:
        name = "shipment_history"

class ShipmentAIAnalysis(Document):
    shipment_id: str
    root_cause_explanation: str
    business_impact: str # Impact on inventory, production, etc.
    recommended_action: str
    recovery_strategy: str
    priority: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipment_ai_analysis"
