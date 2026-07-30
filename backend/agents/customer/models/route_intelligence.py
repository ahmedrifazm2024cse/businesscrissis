from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class Route(Document):
    route_id: str
    origin: str
    destination: str
    supplier_location: Optional[str] = None
    delivery_location: Optional[str] = None
    distance_km: float
    estimated_travel_time_hours: float
    vehicle_type: str
    driver_id: Optional[str] = None
    shipment_priority: str
    status: str # "Active", "Planned", "Completed"
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "routes"

class TrafficAnalysis(Document):
    route_id: str
    congestion_level: str # "Low", "Medium", "High", "Severe"
    accidents_reported: int
    road_closures: int
    construction_zones: int
    peak_hour_overlap_hours: float
    traffic_risk_score: float # 0 to 100
    analyzed_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "traffic_analysis"

class WeatherAnalysis(Document):
    route_id: str
    conditions: List[str] # ["Rain", "Fog"]
    visibility_km: float
    temperature_celsius: float
    wind_speed_kmh: float
    weather_risk_score: float # 0 to 100
    analyzed_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "weather_analysis"

class FuelAnalysis(Document):
    route_id: str
    estimated_fuel_consumption_liters: float
    fuel_cost_per_liter: float
    total_fuel_cost: float
    carbon_emissions_kg: float
    analyzed_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "fuel_analysis"

class RouteRisk(Document):
    route_id: str
    traffic_risk: float
    weather_risk: float
    political_risk: float
    security_risk: float
    road_quality_risk: float
    vehicle_risk: float
    overall_risk_score: float
    risk_level: str # "Low", "Medium", "High", "Critical"
    analyzed_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_risk"

class RoutePrediction(Document):
    route_id: str
    best_case_eta: datetime
    expected_eta: datetime
    worst_case_eta: datetime
    delay_probability: float # 0.0 to 1.0
    arrival_confidence: float # 0.0 to 1.0
    predicted_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_predictions"

class RouteRecommendation(Document):
    route_id: str
    recommendation_type: str # "Reroute", "Change Vehicle", "Delay Departure"
    reason: str
    estimated_savings_usd: float
    time_saved_hours: float
    priority: str
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_recommendations"

class RouteAlert(Document):
    route_id: str
    title: str
    message: str
    severity: str
    created_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_alerts"

class RouteHistory(Document):
    route_id: str
    original_eta: datetime
    actual_arrival: datetime
    delay_hours: float
    total_cost: float
    completed_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_history"

class RouteAIAnalysis(Document):
    route_id: str
    best_route_description: str
    alternative_route_description: str
    reason_for_selection: str
    business_impact: str
    risk_analysis: str
    expected_savings: float
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "route_ai_analysis"
