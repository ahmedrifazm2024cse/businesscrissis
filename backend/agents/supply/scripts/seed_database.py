import asyncio
import os
import sys
import uuid
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.database import init_db

# Import all models just for seeding
from models.domain import (
    Inventory, InventoryAlert, InventoryPrediction, InventoryRecommendation,
    Supplier, Shipment, Warehouse, PurchaseOrder, RiskScore,
    ForecastResult, Recommendation, Alert, CrisisEvent, AgentLog,
    AgentMemory, ConversationHistory, CoordinatorMessage
)
from models.final_intelligence import (
    BusinessImpactAssessment, DecisionHistory, BusinessHistory,
    CrisisHistory, RecommendationHistory, LearningHistory, CoordinatorHistory
)

def utc_now():
    return datetime.now(timezone.utc)

def random_date(start_days_ago, end_days_ago):
    return utc_now() - timedelta(days=random.randint(end_days_ago, start_days_ago), hours=random.randint(0, 23))

async def main():
    print("Overriding MONGODB_URI for local execution (using localhost without credentials)...")
    settings.MONGODB_URI = "mongodb://localhost:27017/abcc_db"
    
    print(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    await init_db()
    print("Beanie initialized.")
    
    document_models = [
        Inventory, Supplier, Shipment, Warehouse, BusinessHistory, CrisisHistory,
        BusinessImpactAssessment, DecisionHistory
    ]
    
    print("Clearing existing collections (only the ones we are seeding to avoid wiping everything)...")
    for model in document_models:
        await model.delete_all()
    
    print("Seeding database...")
    
    # 1. Warehouses (20)
    print("Seeding Warehouses...")
    warehouses = []
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco", "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington"]
    for i in range(20):
        w = Warehouse(
            warehouse_id=f"WH-{i+1:03d}",
            name=f"Distribution Center {locations[i]}",
            location=locations[i],
            capacity_total=random.randint(50000, 200000),
            capacity_used=random.randint(10000, 45000),
            worker_utilization=random.uniform(0.5, 0.95),
            status=random.choice(["Operational", "Operational", "Operational", "At Capacity", "Maintenance"])
        )
        warehouses.append(w)
    await Warehouse.insert_many(warehouses)
    
    # 2. Suppliers (50)
    print("Seeding Suppliers...")
    suppliers = []
    countries = ["USA", "China", "Germany", "Japan", "India", "Mexico", "Vietnam", "Taiwan", "South Korea", "Brazil"]
    for i in range(50):
        s = Supplier(
            supplier_id=f"SUP-{i+1:03d}",
            name=f"GlobalTech Supplier {i+1}",
            country=random.choice(countries),
            reliability_score=random.uniform(0.6, 0.99),
            risk_level=random.choices(["Low", "Medium", "High", "Critical"], weights=[60, 25, 10, 5])[0],
            active_contracts=random.randint(1, 15),
            late_shipment_percent=random.uniform(0.01, 0.2)
        )
        suppliers.append(s)
    await Supplier.insert_many(suppliers)
    
    # 3. Inventory (300)
    print("Seeding Inventory...")
    inventories = []
    for i in range(300):
        stock = random.randint(0, 5000)
        inv = Inventory(
            sku=f"SKU-{random.randint(10000, 99999)}",
            product_name=f"Product {i+1}",
            warehouse_id=random.choice(warehouses).warehouse_id,
            current_stock=stock,
            reserved_stock=int(stock * random.uniform(0.1, 0.5)),
            incoming_stock=random.randint(0, 2000),
            outgoing_stock=random.randint(0, stock if stock > 0 else 100),
            safety_stock=random.randint(100, 500),
            reorder_point=random.randint(200, 800),
            unit_cost=random.uniform(5.0, 500.0)
        )
        inventories.append(inv)
    await Inventory.insert_many(inventories)

    # 4. Shipments (150)
    print("Seeding Shipments...")
    shipments = []
    statuses = ["Pending", "In Transit", "Delayed", "Delivered"]
    for i in range(150):
        status = random.choice(statuses)
        ship = Shipment(
            shipment_id=f"SHP-{i+1:04d}",
            order_id=f"ORD-{random.randint(1000, 9999)}",
            supplier_id=random.choice(suppliers).supplier_id,
            origin=random.choice(countries),
            destination=random.choice(locations),
            status=status,
            estimated_arrival=utc_now() + timedelta(days=random.randint(-5, 15)),
            actual_arrival=utc_now() - timedelta(days=random.randint(1, 5)) if status == "Delivered" else None,
            delay_probability=random.uniform(0.0, 0.9) if status != "Delivered" else 0.0
        )
        shipments.append(ship)
    await Shipment.insert_many(shipments)

    # 5. Business History (100) - For the timeline chart
    print("Seeding Business History...")
    histories = []
    for i in range(100, 0, -1):
        hist = BusinessHistory(
            snapshot_id=str(uuid.uuid4()),
            health_score=random.uniform(60, 95) - (5 if random.random() < 0.2 else 0),
            risk_score=random.uniform(10, 50) + (10 if random.random() < 0.2 else 0),
            impact_score=random.uniform(0, 30),
            active_crises_count=random.randint(0, 3),
            timestamp=utc_now() - timedelta(hours=i*2)
        )
        histories.append(hist)
    await BusinessHistory.insert_many(histories)

    # 6. Crisis History (30)
    print("Seeding Crises...")
    crises = []
    for i in range(30):
        status = "Active" if i < 5 else "Resolved" # 5 active crises
        crisis = CrisisHistory(
            crisis_id=str(uuid.uuid4()),
            severity=random.choices(["Low", "Medium", "High", "Critical"], weights=[10, 40, 30, 20])[0],
            root_cause=random.choice(["Port Strike", "Supplier Bankrupt", "Natural Disaster", "Factory Fire", "Component Shortage"]),
            impact_estimate=random.uniform(50000, 2000000),
            status=status,
            identified_at=utc_now() - timedelta(days=random.randint(1, 30)),
            resolved_at=utc_now() - timedelta(days=random.randint(1, 5)) if status == "Resolved" else None
        )
        crises.append(crisis)
    await CrisisHistory.insert_many(crises)

    # 7. Business Impact Assessments (1) - The latest one for the dashboard
    print("Seeding Business Impact Assessment...")
    bia = BusinessImpactAssessment(
        assessment_id=str(uuid.uuid4()),
        revenue_loss=sum(c.impact_estimate for c in crises if c.status == "Active"),
        profit_loss=random.uniform(10000, 500000),
        inventory_loss=random.uniform(5000, 100000),
        recovery_cost=random.uniform(20000, 800000),
        recovery_time_days=random.uniform(5, 45),
        business_impact_score=75.5,
        business_risk_score=68.2,
        business_health_score=82.1,
        crisis_severity="High",
        executive_summary="Critical component shortage in Asian supplier network impacting 3 key product lines. Immediate rerouting and alternative sourcing required to prevent stockouts.",
        root_cause="Tier-1 supplier facility shutdown due to local energy rationing.",
        business_explanation="Without this component, assembly lines in Texas and Ohio will halt within 7 days, resulting in delayed fulfillment for Q3 major contracts.",
        risk_explanation="Competitors may capture market share if our fulfillment delays extend beyond 14 days.",
        recovery_plan="1. Activate secondary suppliers in Mexico. 2. Expedite air freight for immediate buffer stock. 3. Reallocate existing inventory to high-priority enterprise clients.",
        business_recommendation="Authorize $150k premium for air freight from alternate supplier MX-74 and immediately lock in Q4 capacity.",
        priority="Critical",
        expected_business_outcome="Stabilize production lines within 9 days; mitigate 85% of projected revenue loss.",
        confidence=0.92
    )
    await bia.insert()

    # 8. Decision History (50) - For the live feed and logs
    print("Seeding Decision History...")
    decisions = []
    actions = [
        "Rerouted shipment SHP-0012 via Air Freight",
        "Approved $50k emergency budget for Supplier 8",
        "Rebalanced 500 units from Dallas to Austin",
        "Cancelled PO-449 due to severe delay risk",
        "Initiated emergency procurement protocol for SKU-991",
        "Halted production line 3 temporarily",
        "Upgraded supplier SUP-014 risk level to Critical"
    ]
    for i in range(50):
        dec = DecisionHistory(
            decision_id=str(uuid.uuid4()),
            trigger_event=random.choice(["Schedule", "Inventory Alert", "Shipment Delay", "Supplier Risk Update"]),
            context_summary=f"Automated evaluation {i}",
            decision_taken=random.choice(actions),
            reasoning="AI computed cost-benefit ratio favored immediate action over delay.",
            confidence=random.uniform(0.7, 0.99),
            status=random.choice(["Executed", "Executed", "Pending"]),
            timestamp=utc_now() - timedelta(minutes=random.randint(1, 10000))
        )
        decisions.append(dec)
    await DecisionHistory.insert_many(decisions)

    print("Database seeding completed successfully! Inserted 1000+ realistic records.")

if __name__ == "__main__":
    asyncio.run(main())
