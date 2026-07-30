from repositories.base import BaseRepository
from models.domain import (
    Inventory, Supplier, Shipment, Warehouse, PurchaseOrder, RiskScore,
    ForecastResult, Recommendation, Alert, CrisisEvent, AgentLog, AgentMemory,
    ConversationHistory, CoordinatorMessage, InventoryAlert, InventoryPrediction, InventoryRecommendation
)

inventory_repo = BaseRepository(Inventory)
supplier_repo = BaseRepository(Supplier)
shipment_repo = BaseRepository(Shipment)
warehouse_repo = BaseRepository(Warehouse)
po_repo = BaseRepository(PurchaseOrder)
risk_score_repo = BaseRepository(RiskScore)
forecast_repo = BaseRepository(ForecastResult)
recommendation_repo = BaseRepository(Recommendation)
alert_repo = BaseRepository(Alert)
crisis_event_repo = BaseRepository(CrisisEvent)
agent_log_repo = BaseRepository(AgentLog)
agent_memory_repo = BaseRepository(AgentMemory)
conversation_history_repo = BaseRepository(ConversationHistory)
coordinator_message_repo = BaseRepository(CoordinatorMessage)
inventory_alert_repo = BaseRepository(InventoryAlert)
inventory_prediction_repo = BaseRepository(InventoryPrediction)
inventory_recommendation_repo = BaseRepository(InventoryRecommendation)
