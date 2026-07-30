import asyncio
import os
import sys
import random
import uuid
from datetime import datetime, timedelta, timezone

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from core.config import settings

# Import all models
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

DOCUMENT_MODELS = [
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

def utc_now():
    return datetime.now(timezone.utc)

async def purge_database():
    print("Purging existing data...")
    for model in DOCUMENT_MODELS:
        await model.find_all().delete()
    print("Database purged successfully.")

async def seed_warehouses():
    print("Seeding Warehouses...")
    locations = ["Shanghai, CN", "Los Angeles, US", "Rotterdam, NL", "Hamburg, DE", "Singapore, SG", "Dubai, AE", "Mumbai, IN", "Tokyo, JP", "Sydney, AU", "Sao Paulo, BR"]
    warehouses = []
    
    for loc in locations:
        wh_id = f"WH-{str(uuid.uuid4())[:8].upper()}"
        capacity = random.randint(50000, 200000)
        used = random.randint(int(capacity * 0.4), int(capacity * 0.95))
        
        # Base model
        wh = Warehouse(
            warehouse_id=wh_id,
            name=f"{loc.split(',')[0]} Global Distribution Center",
            location=loc,
            capacity_total=capacity,
            capacity_used=used,
            worker_utilization=random.uniform(0.6, 0.95),
            status="Active"
        )
        await wh.insert()
        
        # Intelligence model
        wc = WarehouseCapacity(
            warehouse_id=wh_id,
            total_capacity=float(capacity),
            used_capacity=float(used),
            available_capacity=float(capacity - used),
            utilization_percentage=(used/capacity) * 100,
            rack_utilization=(used/capacity) * 100,
            shelf_utilization=(used/capacity) * 100,
            cold_storage_used=float(used * 0.1),
            cold_storage_capacity=float(capacity * 0.1),
            zone_utilization={"ZoneA": 80.0, "ZoneB": 90.0}
        )
        await wc.insert()
        warehouses.append(wh)
        
    print(f"Inserted {len(warehouses)} warehouses.")
    return warehouses

async def seed_suppliers():
    print("Seeding Suppliers...")
    categories = ["Electronics", "Raw Materials", "Packaging", "Automotive Parts", "Textiles"]
    countries = ["China", "Vietnam", "India", "Mexico", "Germany", "Taiwan", "USA", "Japan"]
    
    suppliers = []
    
    for i in range(30):
        sup_id = f"SUP-{str(uuid.uuid4())[:8].upper()}"
        score = random.uniform(0.4, 0.99)
        risk = "Critical" if score < 0.5 else ("High" if score < 0.7 else ("Medium" if score < 0.85 else "Low"))
        
        # Base model
        sup = Supplier(
            supplier_id=sup_id,
            name=f"Global {random.choice(categories)} Corp {i}",
            country=random.choice(countries),
            reliability_score=score,
            risk_level=risk,
            active_contracts=random.randint(1, 15),
            late_shipment_percent=(1.0 - score) * 100
        )
        await sup.insert()
        
        # Intelligence model
        prof = SupplierProfile(
            supplier_id=sup_id,
            name=sup.name,
            category=random.choice(categories),
            country_of_origin=sup.country,
            tier=random.choice([1, 2, 3]),
            financial_health_score=random.uniform(50.0, 100.0),
            geopolitical_risk_score=random.uniform(10.0, 90.0),
            compliance_score=random.uniform(70.0, 100.0)
        )
        await prof.insert()
        
        perf = SupplierPerformance(
            supplier_id=sup_id,
            on_time_delivery_rate=score * 100,
            defect_rate=random.uniform(0.1, 5.0),
            average_lead_time_days=random.randint(7, 45),
            fulfillment_accuracy=random.uniform(90.0, 100.0)
        )
        await perf.insert()
        
        risk_doc = SupplierRisk(
            supplier_id=sup_id,
            risk_score=(1.0 - score) * 100,
            classification=risk,
            risk_factors=["Historical delays", "Geopolitical tension"] if risk in ["High", "Critical"] else []
        )
        await risk_doc.insert()
        
        suppliers.append(sup)

    print(f"Inserted {len(suppliers)} suppliers.")
    return suppliers

async def seed_inventory(warehouses, suppliers):
    print("Seeding Inventory...")
    inventory_items = []
    
    for i in range(200):
        wh = random.choice(warehouses)
        sup = random.choice(suppliers)
        
        demand = random.uniform(5.0, 100.0)
        
        # Randomly create some shortages
        is_shortage = random.random() < 0.15 # 15% chance of severe shortage
        
        if is_shortage:
            qty = int(demand * random.uniform(0.5, 2.0)) # 0.5 to 2 days of stock
            incoming = 0
        else:
            qty = int(demand * random.uniform(15.0, 45.0)) # 15 to 45 days of stock
            incoming = int(demand * random.uniform(5.0, 20.0))
            
        inv = Inventory(
            sku=f"SKU-{str(uuid.uuid4())[:8].upper()}",
            product_name=f"Enterprise Product {i}",
            warehouse_id=wh.warehouse_id,
            current_stock=qty,
            reserved_stock=int(qty * 0.1),
            incoming_stock=incoming,
            outgoing_stock=int(qty * 0.15),
            safety_stock=int(demand * 10.0),
            reorder_point=int(demand * 20.0),
            unit_cost=random.uniform(10.0, 5000.0)
        )
        await inv.insert()
        inventory_items.append(inv)
        
        # Create Forecast History for this item
        hist = ForecastHistory(
            product_id=str(inv.id),
            sku=inv.sku,
            date=utc_now() - timedelta(days=30),
            actual_demand=demand * random.uniform(0.8, 1.2),
            seasonality_index=random.uniform(0.9, 1.1),
            marketing_events_active=random.choice([True, False])
        )
        await hist.insert()
        
        # Trigger Shortage model if necessary
        if is_shortage:
            ps = ProductShortage(
                product_id=str(inv.id),
                sku=inv.sku,
                current_stock=inv.current_stock,
                reserved_stock=inv.reserved_stock,
                incoming_inventory=inv.incoming_stock,
                outgoing_inventory=inv.outgoing_stock,
                daily_demand_forecast=demand,
                safety_stock=inv.safety_stock,
                reorder_point=inv.reorder_point,
                buffer_stock=int(demand * 3)
            )
            await ps.insert()
            
            sp = ShortagePrediction(
                product_id=str(inv.id),
                sku=inv.sku,
                probability_of_shortage=random.uniform(0.8, 0.99),
                days_remaining=float(inv.current_stock) / max(demand, 1.0),
                confidence_score=0.95,
                criticality_level="Emergency" if (float(inv.current_stock) / max(demand, 1.0)) < 3 else "Critical",
                trend="Worsening"
            )
            await sp.insert()
            
            prs = ProductRiskScore(
                product_id=str(inv.id),
                sku=inv.sku,
                risk_score=random.uniform(80.0, 100.0),
                classification=sp.criticality_level,
                root_causes=["Demand surge", "Supplier failure"],
                revenue_impact_estimate=demand * inv.unit_cost * 14 # 2 weeks of lost sales
            )
            await prs.insert()
            
    print(f"Inserted {len(inventory_items)} inventory items.")
    return inventory_items

async def seed_shipments(suppliers):
    print("Seeding Shipments...")
    shipments = []
    
    ports = ["Shanghai Port", "Port of LA", "Port of Rotterdam", "JFK Airport", "Heathrow Airport", "Singapore Port"]
    
    for i in range(100):
        sup = random.choice(suppliers)
        is_delayed = random.random() < 0.2
        
        now = utc_now()
        ship_id = f"SHP-{str(uuid.uuid4())[:8].upper()}"
        
        # Base model
        ship = Shipment(
            shipment_id=ship_id,
            order_id=f"PO-{str(uuid.uuid4())[:8].upper()}",
            supplier_id=sup.supplier_id,
            origin=random.choice(ports),
            destination=random.choice(ports),
            status="Delayed" if is_delayed else "In Transit",
            estimated_arrival=now + timedelta(days=random.randint(1, 14)),
            delay_probability=random.uniform(0.7, 0.99) if is_delayed else random.uniform(0.01, 0.3)
        )
        await ship.insert()
        
        # Intelligence model
        trk = ShipmentTracking(
            tracking_number=ship.shipment_id,
            carrier="GlobalFreight Inc" if random.random() > 0.5 else "OceanLines Co",
            origin=ship.origin,
            destination=ship.destination,
            current_location="Mid Pacific" if "Port" in ship.origin else "In Air",
            status=ship.status,
            latitude=random.uniform(-90.0, 90.0),
            longitude=random.uniform(-180.0, 180.0)
        )
        await trk.insert()
        
        if is_delayed:
            pred = ShipmentPrediction(
                tracking_number=trk.tracking_number,
                predicted_delay_days=random.uniform(2.0, 10.0),
                delay_probability=ship.delay_probability,
                confidence_score=0.9,
                root_cause="Port Congestion" if "Port" in ship.origin else "Severe Weather"
            )
            await pred.insert()
            
        shipments.append(ship)

    print(f"Inserted {len(shipments)} shipments.")
    return shipments

async def main():
    print("=== STARTING DATABASE SEED ===")
    
    # Initialize Beanie
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db_name = "abcc_db"
    base_uri = settings.MONGODB_URI.split("?")[0]
    if "/" in base_uri:
        db_name = base_uri.split("/")[-1]
    
    await init_beanie(database=client[db_name], document_models=DOCUMENT_MODELS)
    
    await purge_database()
    
    warehouses = await seed_warehouses()
    suppliers = await seed_suppliers()
    inventory = await seed_inventory(warehouses, suppliers)
    shipments = await seed_shipments(suppliers)
    
    print("=== DATABASE SEED COMPLETE ===")
    print(f"Successfully generated a massive dataset for {db_name}.")
    print("The ABCC Supply Chain Agent will immediately begin autonomous analysis upon startup.")

if __name__ == "__main__":
    asyncio.run(main())
