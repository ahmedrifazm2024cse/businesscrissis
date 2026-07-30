from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from models.procurement_intelligence import (
    PurchasePlan, ProcurementRisk, ProcurementPrediction,
    ProcurementRecommendation, ProcurementAlert, ProcurementHistory,
    ProcurementAIAnalysis
)
from workflows.procurement_monitor import run_procurement_monitor
from models.domain import Inventory

router = APIRouter(prefix="/procurements", tags=["procurements"])

@router.get("/plans", response_model=List[PurchasePlan])
async def get_purchase_plans(skip: int = 0, limit: int = 50):
    return await PurchasePlan.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/risk", response_model=List[ProcurementRisk])
async def get_procurement_risk(skip: int = 0, limit: int = 50):
    return await ProcurementRisk.find_all().sort("-assessed_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[ProcurementPrediction])
async def get_procurement_predictions(skip: int = 0, limit: int = 50):
    return await ProcurementPrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/recommendations", response_model=List[ProcurementRecommendation])
async def get_procurement_recommendations(skip: int = 0, limit: int = 50):
    return await ProcurementRecommendation.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[ProcurementAlert])
async def get_procurement_alerts(skip: int = 0, limit: int = 50):
    return await ProcurementAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[ProcurementAIAnalysis])
async def get_procurement_analysis(skip: int = 0, limit: int = 50):
    return await ProcurementAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.post("/analyze")
async def trigger_procurement_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_procurement_monitor)
    return {"message": "Procurement Intelligence Monitor started in background"}

@router.post("/simulate")
async def simulate_emergency(sku: str):
    """Injects a critical inventory shortage to trigger emergency procurement."""
    inv = await Inventory.find_one(Inventory.sku == sku)
    if not inv:
        # Create dummy inventory
        inv = Inventory(sku=sku, name=f"Test {sku}", category="Simulation",
                        current_stock=1000, reserved_stock=0,
                        safety_stock=500, reorder_point=600,
                        unit_cost=10.0, warehouse_id="WH-1")
    
    # Drop stock way below reorder point
    inv.current_stock = inv.reorder_point * 0.1
    await inv.save()
    
    return {"message": f"Injected critical shortage for {sku}. Run analysis to see the emergency procurement plan."}
