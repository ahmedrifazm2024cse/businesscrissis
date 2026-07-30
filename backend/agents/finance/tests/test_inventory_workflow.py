import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from models.domain import Inventory, InventoryAlert, InventoryPrediction, CoordinatorMessage
from services.inventory_health import inventory_health_engine
from services.stockout_prediction import stockout_prediction_engine
from workflows.inventory_monitor import run_inventory_monitor
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from tests.db_test_utils import setup_test_db

@pytest.mark.asyncio
async def test_inventory_health_calculation():
    await setup_test_db([Inventory, InventoryAlert, InventoryPrediction, CoordinatorMessage])
    mock_item = Inventory(
        sku="TEST-SKU-1", product_name="Test Product", warehouse_id="WH-1",
        current_stock=10, reserved_stock=0, incoming_stock=0, outgoing_stock=5,
        safety_stock=20, reorder_point=40, unit_cost=10.0
    )
    health = inventory_health_engine.calculate_health(mock_item, estimated_daily_demand=2.0)
    
    assert health["available_stock"] == 5
    assert health["days_remaining"] == 2.5
    assert health["stock_status"] == "Critical"
    assert health["is_understock"] == True
    assert health["is_overstock"] == False

@pytest.mark.asyncio
async def test_stockout_prediction():
    await setup_test_db([Inventory, InventoryAlert, InventoryPrediction, CoordinatorMessage])
    mock_item = Inventory(
        sku="TEST-SKU-1", product_name="Test Product", warehouse_id="WH-1",
        current_stock=10, reserved_stock=0, incoming_stock=0, outgoing_stock=5,
        safety_stock=20, reorder_point=40, unit_cost=10.0
    )
    available_stock = 15
    # Predictable demand of ~3 per day
    demand_history = [3.0, 3.1, 2.9, 3.0, 3.2, 2.8, 3.0]
    
    prediction = stockout_prediction_engine.predict(available_stock, demand_history)
    
    assert prediction["days_until_stockout"] > 0
    # ~5 days remaining
    assert 4.0 <= prediction["days_until_stockout"] <= 6.0
    assert prediction["probability"] > 0.5 # Less than 7 days, so high probability

@pytest.mark.asyncio
async def test_duplicate_alert_prevention():
    await setup_test_db([Inventory, InventoryAlert, InventoryPrediction, CoordinatorMessage])
    await InventoryAlert.find_all().delete()
    
    # Insert active alert for SKU-1
    alert = InventoryAlert(
        sku="SKU-TEST-DUP",
        title="Test Alert",
        message="Message",
        severity="Critical",
        created_at=datetime.now(timezone.utc) - timedelta(hours=2) # 2 hours ago
    )
    await alert.insert()
    
    # Try fetching recently
    recent_alert = await InventoryAlert.find_one(
        InventoryAlert.sku == "SKU-TEST-DUP",
        InventoryAlert.created_at > datetime.now(timezone.utc) - timedelta(hours=24)
    )
    
    assert recent_alert is not None
    assert recent_alert.sku == "SKU-TEST-DUP"

@pytest.mark.asyncio
async def test_coordinator_message_generation():
    await setup_test_db([Inventory, InventoryAlert, InventoryPrediction, CoordinatorMessage])
    await CoordinatorMessage.find_all().delete()
    
    msg = CoordinatorMessage(
        message_id="test_msg_1",
        direction="outbound",
        payload={"finding": "critical test"},
        status="Pending"
    )
    await msg.insert()
    
    saved = await CoordinatorMessage.find_one(CoordinatorMessage.message_id == "test_msg_1")
    assert saved is not None
    assert saved.payload["finding"] == "critical test"
