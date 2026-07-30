from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class SupplierProfile(Document):
    supplier_id: str
    name: str
    categories: List[str]
    products_supplied: List[str]
    location: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_primary: bool = False
    capacity_per_month: int
    contract_status: str # "Active", "Expired", "Pending"
    contact_email: str
    preferred_status: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "suppliers"

class SupplierPerformance(Document):
    supplier_id: str
    on_time_delivery_pct: float
    avg_delivery_delay_days: float
    order_fulfillment_rate: float
    quality_acceptance_rate: float
    defect_rate: float
    cancellation_rate: float
    return_rate: float
    sla_compliance: float
    overall_performance_score: float # 0-100
    recorded_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_scores"

class SupplierRisk(Document):
    supplier_id: str
    financial_risk: float # 0-100
    delivery_risk: float
    country_risk: float
    political_risk: float
    natural_disaster_risk: float
    weather_impact: float
    currency_risk: float
    single_source_dependency: float
    capacity_risk: float
    quality_risk: float
    compliance_risk: float
    contract_expiration_risk: float
    overall_risk_score: float # 0-100
    risk_category: str # "Low", "Medium", "High", "Critical"
    calculated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_risk"

class SupplierPrediction(Document):
    supplier_id: str
    failure_probability: float # 0-1.0
    expected_disruption_date: Optional[datetime] = None
    expected_delivery_delays_days: float
    potential_inventory_shortages: List[str] # SKUs
    estimated_business_impact: str
    confidence_score: float
    predicted_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_predictions"

class SupplierRecommendation(Document):
    target_supplier_id: str # The supplier we are replacing/backing up
    alternative_supplier_ids: List[str] # IDs of alternatives
    ranked_alternatives: List[Dict[str, Any]] # [{"supplier_id": "123", "rank": 1, "score": 95, "reason": "..."}]
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_recommendations"

class SupplierAlert(Document):
    supplier_id: str
    title: str
    message: str
    severity: str # "Low", "Medium", "High", "Critical"
    event_type: str # e.g. "Shutdown", "Repeated Delays", "Political Instability"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_alerts"

class SupplierHistory(Document):
    supplier_id: str
    date: datetime = Field(default_factory=utc_now)
    performance_score: float
    risk_score: float
    event_summary: Optional[str] = None
    
    class Settings:
        name = "supplier_history"

class SupplierAIAnalysis(Document):
    supplier_id: str
    health_score: float
    reliability_score: float
    stability_score: float
    business_continuity_score: float
    root_cause: str
    business_impact: str
    recommended_actions: List[str]
    procurement_advice: str
    risk_mitigation_strategy: str
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "supplier_ai_analysis"
