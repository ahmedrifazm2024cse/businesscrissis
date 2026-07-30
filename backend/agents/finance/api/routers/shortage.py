from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import random
from models.domain import Inventory
from models.shortage_intelligence import (
    ProductShortage, ShortagePrediction, ProductRiskScore, ShortageAlert,
    ShortageRecommendation, ShortageAIAnalysis, ShortageHistory
)
from workflows.shortage_monitor import run_shortage_monitor

router = APIRouter(prefix="/shortages", tags=["shortage"])

@router.get("", response_model=List[ProductShortage])
async def get_shortages(skip: int = 0, limit: int = 50):
    return await ProductShortage.find_all().sort("-calculated_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[ShortagePrediction])
async def get_predictions(skip: int = 0, limit: int = 50):
    return await ShortagePrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/risk", response_model=List[ProductRiskScore])
async def get_risk(skip: int = 0, limit: int = 50):
    return await ProductRiskScore.find_all().sort("-scored_at").skip(skip).limit(limit).to_list()

@router.get("/recommendations", response_model=List[ShortageRecommendation])
async def get_recommendations(skip: int = 0, limit: int = 50):
    return await ShortageRecommendation.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[ShortageAlert])
async def get_alerts(skip: int = 0, limit: int = 50):
    return await ShortageAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[ShortageAIAnalysis])
async def get_ai_analysis(skip: int = 0, limit: int = 50):
    return await ShortageAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.post("/analyze")
async def trigger_shortage_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_shortage_monitor)
    return {"message": "Shortage prediction monitor started in background"}

@router.post("/simulate")
async def simulate_shortage():
    """Injects a critical product shortage for demonstration."""
    mock_sku = f"SKU-{random.randint(1000,9999)}"
    
    # Fake Inventory
    inv = Inventory(sku=mock_sku, product_name="Critical Component XYZ", category="Electronics", quantity=50, unit_price=250.0)
    await inv.insert()
    
    ps = ProductShortage(
        product_id=str(inv.id),
        sku=mock_sku,
        current_stock=50,
        reserved_stock=40,
        incoming_inventory=0,
        outgoing_inventory=40,
        daily_demand_forecast=20.0,
        safety_stock=100,
        reorder_point=150,
        buffer_stock=50
    )
    await ps.insert()
    
    sp = ShortagePrediction(
        product_id=str(inv.id),
        sku=mock_sku,
        probability_of_shortage=0.98,
        days_remaining=0.5,
        confidence_score=0.95,
        criticality_level="Emergency",
        trend="Worsening"
    )
    await sp.insert()
    
    prs = ProductRiskScore(
        product_id=str(inv.id),
        sku=mock_sku,
        risk_score=99.0,
        classification="Emergency",
        root_causes=["Demand surge (20%+ over historical)", "High probability of incoming shipment delays"],
        revenue_impact_estimate=35000.0
    )
    await prs.insert()
    
    return {"message": f"Injected Emergency Shortage for product {mock_sku}. Dashboard updated."}
