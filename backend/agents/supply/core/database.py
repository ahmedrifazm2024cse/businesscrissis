from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings
from models.domain import (
    Inventory, Supplier, Shipment, Warehouse, PurchaseOrder, RiskScore,
    ForecastResult as LegacyForecastResult, Recommendation, Alert, CrisisEvent, AgentLog, AgentMemory,
    ConversationHistory, CoordinatorMessage, InventoryAlert, InventoryPrediction, InventoryRecommendation
)
from models.forecast import (
    ForecastHistory, ForecastResult, ForecastModelConfig, ForecastLog,
    ForecastRecommendation, ForecastAlert, ForecastAccuracy, ForecastJob
)
from models.supplier_intelligence import (
    SupplierProfile, SupplierPerformance, SupplierRisk, SupplierPrediction,
    SupplierRecommendation, SupplierAlert, SupplierHistory, SupplierAIAnalysis
)
from models.shipment_intelligence import (
    ShipmentTracking, ShipmentETA, ShipmentPrediction, ShipmentRisk,
    ShipmentRoute, ShipmentAlert, ShipmentHistory, ShipmentAIAnalysis
)
from models.warehouse_intelligence import (
    WarehouseCapacity, WarehousePerformance, WarehousePrediction, WarehouseRisk,
    WarehouseRecommendation, WarehouseAlert, WarehouseHistory, WarehouseAIAnalysis
)
from models.procurement_intelligence import (
    PurchasePlan, ProcurementRisk, ProcurementPrediction, ProcurementRecommendation,
    ProcurementAlert, ProcurementHistory, ProcurementAIAnalysis
)
from models.cost_intelligence import (
    CostAnalysis, CostTrend, CostPrediction, BudgetMonitoring, CostRecommendation,
    CostAlert, CostHistory, CostAIAnalysis
)
from models.route_intelligence import (
    Route, TrafficAnalysis, WeatherAnalysis, FuelAnalysis, RouteRisk,
    RoutePrediction, RouteRecommendation, RouteAlert, RouteHistory, RouteAIAnalysis
)
from models.shortage_intelligence import (
    ProductShortage, ShortagePrediction, ProductRiskScore, ShortageAlert,
    ShortageRecommendation, ShortageAIAnalysis, ShortageHistory
)
from models.final_intelligence import (
    BusinessImpactAssessment, DecisionHistory, BusinessHistory, CrisisHistory,
    RecommendationHistory, LearningHistory, CoordinatorHistory
)
import logging

logger = logging.getLogger(__name__)

# Workaround for Beanie calling append_metadata which AsyncIOMotorClient might not expose
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda self, *args, **kwargs: None

async def init_db():
    try:
        # Create Motor client
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        
        db_name = "abcc_db"
        base_uri = settings.MONGODB_URI.split("?")[0]
        if "/" in base_uri:
            db_name = base_uri.split("/")[-1]

        document_models = [
            Inventory, Supplier, Shipment, Warehouse, PurchaseOrder, RiskScore,
            LegacyForecastResult, Recommendation, Alert, CrisisEvent, AgentLog, AgentMemory,
            ConversationHistory, CoordinatorMessage, InventoryAlert, InventoryPrediction, InventoryRecommendation,
            ForecastHistory, ForecastResult, ForecastModelConfig, ForecastLog,
            ForecastRecommendation, ForecastAlert, ForecastAccuracy, ForecastJob,
            SupplierProfile, SupplierPerformance, SupplierRisk, SupplierPrediction,
            SupplierRecommendation, SupplierAlert, SupplierHistory, SupplierAIAnalysis,
            ShipmentTracking, ShipmentETA, ShipmentPrediction, ShipmentRisk,
            ShipmentRoute, ShipmentAlert, ShipmentHistory, ShipmentAIAnalysis,
            WarehouseCapacity, WarehousePerformance, WarehousePrediction, WarehouseRisk,
            WarehouseRecommendation, WarehouseAlert, WarehouseHistory, WarehouseAIAnalysis,
            PurchasePlan, ProcurementRisk, ProcurementPrediction, ProcurementRecommendation,
            ProcurementAlert, ProcurementHistory, ProcurementAIAnalysis,
            CostAnalysis, CostTrend, CostPrediction, BudgetMonitoring, CostRecommendation,
            CostAlert, CostHistory, CostAIAnalysis,
            Route, TrafficAnalysis, WeatherAnalysis, FuelAnalysis, RouteRisk,
            RoutePrediction, RouteRecommendation, RouteAlert, RouteHistory, RouteAIAnalysis,
            ProductShortage, ShortagePrediction, ProductRiskScore, ShortageAlert,
            ShortageRecommendation, ShortageAIAnalysis, ShortageHistory,
            BusinessImpactAssessment, DecisionHistory, BusinessHistory, CrisisHistory,
            RecommendationHistory, LearningHistory, CoordinatorHistory
        ]

        await init_beanie(database=client[db_name], document_models=document_models)
        logger.info(f"Successfully connected to MongoDB: {db_name}")
        return client[db_name]
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
