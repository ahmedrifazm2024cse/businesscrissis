from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class ForecastHistory(Document):
    sku: str
    date: datetime
    sales_quantity: float = 0.0
    inventory_movement: float = 0.0
    purchase_history: float = 0.0
    weather_impact_factor: float = 1.0 # 1.0 means normal
    holiday_impact_factor: float = 1.0
    marketing_campaign_impact: float = 1.0
    supplier_delay_days: int = 0
    stock_availability: int = 0
    recorded_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_history"

class ForecastResult(Document):
    sku: str
    forecast_type: str # "Daily", "Weekly", "Monthly", "Quarterly", "Yearly"
    target_date: datetime
    forecast_quantity: float
    confidence_score: float # 0.0 to 1.0
    trend: str # "Increasing", "Decreasing", "Stable", etc.
    growth_percentage: float
    expected_demand: float
    forecast_accuracy: Optional[float] = None # Filled later when actual data arrives
    algorithm_used: str
    generated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_results"

class ForecastModelConfig(Document):
    sku: str
    active_algorithms: List[str] # ["SMA", "WMA", "LinearRegression", "ExponentialSmoothing"]
    best_algorithm: str
    parameters: Dict[str, Any] # e.g. {"sma_window": 7, "alpha": 0.2}
    updated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_models"

class ForecastLog(Document):
    agent_name: str = "Demand Forecasting Agent"
    action: str
    details: str
    status: str = "Success"
    timestamp: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_logs"

class ForecastRecommendation(Document):
    sku: str
    reason: str
    priority: str # "Low", "Medium", "High", "Critical"
    expected_impact: str
    confidence: float
    action_type: str # "Increase inventory", "Reduce inventory", "Delay procurement", etc.
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_recommendations"

class ForecastAlert(Document):
    sku: str
    title: str
    message: str
    severity: str # "Warning", "Critical"
    anomaly_type: str # "Spike", "Drop", "Out of Stock"
    created_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_alerts"

class ForecastAccuracy(Document):
    sku: str
    algorithm: str
    rmse: float
    mape: float
    calculated_at: datetime = Field(default_factory=utc_now)
    
    class Settings:
        name = "forecast_accuracy"

class ForecastJob(Document):
    job_id: str
    status: str # "Running", "Completed", "Failed"
    start_time: datetime = Field(default_factory=utc_now)
    end_time: Optional[datetime] = None
    items_processed: int = 0
    error_message: Optional[str] = None
    
    class Settings:
        name = "forecast_jobs"
