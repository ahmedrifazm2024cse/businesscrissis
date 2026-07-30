from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models.domain import Warehouse
from models.warehouse_intelligence import (
    WarehouseCapacity, WarehousePerformance, WarehousePrediction,
    WarehouseRisk, WarehouseRecommendation, WarehouseAlert,
    WarehouseHistory, WarehouseAIAnalysis
)
from workflows.warehouse_monitor import run_warehouse_monitor

router = APIRouter(prefix="/warehouses", tags=["warehouses"])

@router.get("", response_model=List[Warehouse])
async def get_warehouses(skip: int = 0, limit: int = 50):
    return await Warehouse.find_all().skip(skip).limit(limit).to_list()

@router.get("/capacity", response_model=List[WarehouseCapacity])
async def get_warehouse_capacity(skip: int = 0, limit: int = 50):
    return await WarehouseCapacity.find_all().sort("-recorded_at").skip(skip).limit(limit).to_list()

@router.get("/health", response_model=List[WarehouseRisk])
async def get_warehouse_health(skip: int = 0, limit: int = 50):
    return await WarehouseRisk.find_all().sort("-assessed_at").skip(skip).limit(limit).to_list()

@router.get("/performance", response_model=List[WarehousePerformance])
async def get_warehouse_performance(skip: int = 0, limit: int = 50):
    return await WarehousePerformance.find_all().sort("-recorded_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[WarehouseAlert])
async def get_warehouse_alerts(skip: int = 0, limit: int = 50):
    return await WarehouseAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[WarehousePrediction])
async def get_warehouse_predictions(skip: int = 0, limit: int = 50):
    return await WarehousePrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[WarehouseAIAnalysis])
async def get_warehouse_analysis(skip: int = 0, limit: int = 50):
    return await WarehouseAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/{warehouse_id}")
async def get_warehouse_details(warehouse_id: str):
    wh = await Warehouse.find_one(Warehouse.warehouse_id == warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
        
    cap = await WarehouseCapacity.find_one(WarehouseCapacity.warehouse_id == warehouse_id, sort=[("recorded_at", -1)])
    health = await WarehouseRisk.find_one(WarehouseRisk.warehouse_id == warehouse_id, sort=[("assessed_at", -1)])
    pred = await WarehousePrediction.find_one(WarehousePrediction.warehouse_id == warehouse_id, sort=[("predicted_at", -1)])
    perf = await WarehousePerformance.find_one(WarehousePerformance.warehouse_id == warehouse_id, sort=[("recorded_at", -1)])
    
    return {
        "warehouse": wh,
        "capacity": cap,
        "health": health,
        "prediction": pred,
        "performance": perf
    }

@router.post("/analyze")
async def trigger_warehouse_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_warehouse_monitor)
    return {"message": "Warehouse Intelligence Monitor started in background"}

@router.post("/simulate")
async def simulate_bottleneck(warehouse_id: str, bottleneck_type: str = "Congestion"):
    """Injects a bottleneck to trigger prediction and AI analysis."""
    cap = await WarehouseCapacity.find(WarehouseCapacity.warehouse_id == warehouse_id).sort("-recorded_at").first_or_none()
    if not cap:
        raise HTTPException(status_code=404, detail="Warehouse capacity data not found. Run agent first.")
        
    if bottleneck_type == "Congestion":
        # Force utilization to 98%
        cap.used_capacity = cap.total_capacity * 0.98
        cap.utilization_percentage = 98.0
        cap.available_capacity = cap.total_capacity * 0.02
        await cap.save()
        
    return {"message": f"Injected {bottleneck_type} for {warehouse_id}. Run analysis to see the effect."}
