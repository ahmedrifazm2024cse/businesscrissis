from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from models.domain import (
    Inventory, InventoryAlert, InventoryPrediction, InventoryRecommendation
)
from services.inventory_health import inventory_health_engine
from services.stockout_prediction import stockout_prediction_engine
from workflows.inventory_monitor import run_inventory_monitor
import random
from datetime import datetime

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("", response_model=List[Inventory])
async def get_inventory():
    return await Inventory.find_all().to_list()

@router.get("/alerts")
async def get_alerts():
    return await InventoryAlert.find_all().sort("-created_at").to_list()

@router.get("/predictions")
async def get_predictions():
    return await InventoryPrediction.find_all().sort("-generated_at").to_list()

@router.get("/recommendations")
async def get_recommendations():
    return await InventoryRecommendation.find_all().sort("-created_at").to_list()

@router.get("/health")
async def get_health_summary():
    inventories = await Inventory.find_all().to_list()
    total_items = len(inventories)
    healthy = 0
    warning = 0
    critical = 0
    
    for item in inventories:
        avg_daily = item.outgoing_stock / 30 if item.outgoing_stock > 0 else 5.0
        health = inventory_health_engine.calculate_health(item, estimated_daily_demand=avg_daily)
        if health["stock_status"] == "Healthy":
            healthy += 1
        elif health["stock_status"] == "Warning":
            warning += 1
        else:
            critical += 1
            
    return {
        "total_items": total_items,
        "status_breakdown": {
            "Healthy": healthy,
            "Warning": warning,
            "Critical": critical
        }
    }

@router.get("/{sku}")
async def get_inventory_item(sku: str):
    item = await Inventory.find_one(Inventory.sku == sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    avg_daily = item.outgoing_stock / 30 if item.outgoing_stock > 0 else 5.0
    demand_history = [max(0.0, avg_daily + random.uniform(-2, 2)) for _ in range(14)]
    
    health = inventory_health_engine.calculate_health(item, estimated_daily_demand=avg_daily)
    prediction = stockout_prediction_engine.predict(health["available_stock"], demand_history)
    
    return {
        "item": item,
        "health": health,
        "prediction": prediction
    }

@router.post("/simulate-stock-change")
async def simulate_stock_change(sku: str, amount: int):
    item = await Inventory.find_one(Inventory.sku == sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # simulate change (e.g., amount < 0 means sales, amount > 0 means delivery)
    item.current_stock += amount
    if item.current_stock < 0:
        item.current_stock = 0
        
    if amount < 0:
        item.outgoing_stock += abs(amount)
        
    await item.save()
    return {"message": "Stock updated", "current_stock": item.current_stock}

@router.post("/run-analysis")
async def run_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_inventory_monitor)
    return {"message": "Analysis started in background"}

@router.post("/seed")
async def seed_dummy_data():
    count = await Inventory.find_all().count()
    if count > 0:
        return {"message": "Data already exists. Skipping."}
        
    warehouses = ["WH-01", "WH-02", "WH-03"]
    products = [
        ("SKU-1001", "Microcontroller Board v2", 50, 150),
        ("SKU-1002", "Lithium Ion Battery Pack", 20, 50),
        ("SKU-1003", "LCD Display Module 1080p", 10, 30),
        ("SKU-1004", "Aluminum Enclosure Size M", 100, 300),
        ("SKU-1005", "Power Supply Unit 500W", 5, 10), # critical test case
    ]
    
    items = []
    for i in range(50):
        if i < len(products):
            sku, name, current, safety = products[i]
        else:
            sku = f"SKU-{2000+i}"
            name = f"Generic Component Type {i}"
            current = random.randint(5, 500)
            safety = random.randint(10, 100)
            
        items.append(
            Inventory(
                sku=sku,
                product_name=name,
                warehouse_id=random.choice(warehouses),
                current_stock=current,
                reserved_stock=random.randint(0, int(current*0.2) if current > 0 else 0),
                incoming_stock=random.randint(0, 50),
                outgoing_stock=random.randint(0, 100),
                safety_stock=safety,
                reorder_point=safety * 2,
                unit_cost=round(random.uniform(1.0, 500.0), 2)
            )
        )
        
    for item in items:
        await item.insert()
        
    return {"message": f"Inserted {len(items)} products"}
