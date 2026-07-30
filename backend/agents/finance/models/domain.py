from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class Inventory(Document):
    sku: str
    product_name: str
    warehouse_id: str
    current_stock: int
    reserved_stock: int
    incoming_stock: int
    outgoing_stock: int
    safety_stock: int
    reorder_point: int
    unit_cost: float
    last_updated: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "inventory"

class InventoryAlert(Document):
    sku: str
    title: str
    message: str
    severity: str # "Warning", "Critical"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "inventory_alerts"

class InventoryPrediction(Document):
    sku: str
    stockout_date: Optional[datetime] = None
    probability: float
    confidence: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "inventory_predictions"

class InventoryRecommendation(Document):
    sku: str
    root_cause: str
    business_impact: str
    recommended_action: str
    expected_outcome: str
    priority: str
    confidence: float
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "inventory_recommendations"

class Supplier(Document):
    supplier_id: str
    name: str
    country: str
    reliability_score: float # 0.0 to 1.0
    risk_level: str # "Low", "Medium", "High", "Critical"
    active_contracts: int
    late_shipment_percent: float
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "suppliers"

class Shipment(Document):
    shipment_id: str
    order_id: str
    supplier_id: str
    origin: str
    destination: str
    status: str # "Pending", "In Transit", "Delayed", "Delivered"
    estimated_arrival: datetime
    actual_arrival: Optional[datetime] = None
    delay_probability: float = 0.0
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "shipments"

class Warehouse(Document):
    warehouse_id: str
    name: str
    location: str
    capacity_total: int
    capacity_used: int
    worker_utilization: float # percentage
    status: str
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "warehouses"

class PurchaseOrder(Document):
    po_id: str
    supplier_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    order_date: datetime
    expected_delivery: datetime
    status: str
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "purchase_orders"

class RiskScore(Document):
    entity_type: str # "Supplier", "Inventory", "Shipment"
    entity_id: str
    score: float
    factors: List[str]
    calculated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "risk_scores"

class ForecastResult(Document):
    product_id: str
    forecast_type: str # "Demand", "Price"
    horizon: str # "Daily", "Weekly", "Monthly"
    predictions: List[Dict[str, Any]] # e.g., [{"date": "2024-01-01", "value": 100}]
    confidence_score: float
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_results"

class Recommendation(Document):
    agent_source: str
    title: str
    description: str
    priority: str # "Low", "Medium", "High", "Critical"
    expected_benefits: str
    metadata: Dict[str, Any]
    status: str = "Pending" # "Pending", "Approved", "Rejected"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "recommendations"

class Alert(Document):
    title: str
    message: str
    severity: str
    source_agent: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "alerts"

class CrisisEvent(Document):
    crisis_id: str
    title: str
    description: str
    impact_estimate: Dict[str, Any] # e.g., {"revenue_loss": 50000}
    status: str # "Active", "Mitigated", "Resolved"
    identified_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "crisis_events"

class AgentLog(Document):
    agent_name: str
    action: str
    details: str
    timestamp: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "agent_logs"

class AgentMemory(Document):
    agent_name: str
    memory_key: str
    memory_value: Any
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "agent_memory"

class ConversationHistory(Document):
    session_id: str
    role: str # "user", "assistant", "system", "coordinator"
    content: str
    timestamp: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "conversation_history"

class CoordinatorMessage(Document):
    message_id: str
    direction: str # "inbound", "outbound"
    payload: Dict[str, Any]
    status: str
    timestamp: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "coordinator_messages"
