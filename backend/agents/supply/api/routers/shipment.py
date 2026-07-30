from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from models.domain import Shipment
from models.shipment_intelligence import (
    ShipmentTracking, ShipmentETA, ShipmentPrediction, ShipmentRisk,
    ShipmentRoute, ShipmentAlert, ShipmentHistory, ShipmentAIAnalysis
)
from workflows.shipment_monitor import run_shipment_monitor

router = APIRouter(prefix="/shipments", tags=["shipments"])

@router.get("", response_model=List[Shipment])
async def get_shipments(skip: int = 0, limit: int = 50):
    return await Shipment.find_all().skip(skip).limit(limit).to_list()

@router.get("/tracking", response_model=List[ShipmentTracking])
async def get_shipment_tracking(skip: int = 0, limit: int = 50):
    return await ShipmentTracking.find_all().sort("-last_updated").skip(skip).limit(limit).to_list()

@router.get("/eta", response_model=List[ShipmentETA])
async def get_shipment_etas(skip: int = 0, limit: int = 50):
    return await ShipmentETA.find_all().sort("-calculated_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[ShipmentPrediction])
async def get_shipment_predictions(skip: int = 0, limit: int = 50):
    return await ShipmentPrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/risk", response_model=List[ShipmentRisk])
async def get_shipment_risk(skip: int = 0, limit: int = 50):
    return await ShipmentRisk.find_all().sort("-assessed_at").skip(skip).limit(limit).to_list()

@router.get("/routes", response_model=List[ShipmentRoute])
async def get_shipment_routes(skip: int = 0, limit: int = 50):
    return await ShipmentRoute.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/alerts", response_model=List[ShipmentAlert])
async def get_shipment_alerts(skip: int = 0, limit: int = 50):
    return await ShipmentAlert.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[ShipmentAIAnalysis])
async def get_shipment_analysis(skip: int = 0, limit: int = 50):
    return await ShipmentAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.get("/{shipment_id}")
async def get_shipment_details(shipment_id: str):
    shipment = await Shipment.find_one(Shipment.shipment_id == shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    tracking = await ShipmentTracking.find_one(ShipmentTracking.shipment_id == shipment_id)
    eta = await ShipmentETA.find_one(ShipmentETA.shipment_id == shipment_id, sort=[("calculated_at", -1)])
    risk = await ShipmentRisk.find_one(ShipmentRisk.shipment_id == shipment_id, sort=[("assessed_at", -1)])
    prediction = await ShipmentPrediction.find_one(ShipmentPrediction.shipment_id == shipment_id, sort=[("predicted_at", -1)])
    
    return {
        "shipment": shipment,
        "tracking": tracking,
        "eta": eta,
        "risk": risk,
        "prediction": prediction
    }

@router.post("/analyze")
async def trigger_shipment_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_shipment_monitor)
    return {"message": "Shipment Intelligence Monitor started in background"}

@router.post("/simulate")
async def simulate_shipment_delay(shipment_id: str, delay_type: str = "Weather"):
    """Injects a sudden risk spike to trigger delay prediction and AI analysis."""
    risk = await ShipmentRisk.find(ShipmentRisk.shipment_id == shipment_id).sort("-assessed_at").first_or_none()
    if not risk:
        # Create a dummy risk profile
        risk = ShipmentRisk(
            shipment_id=shipment_id,
            traffic_risk=0, weather_risk=0, port_congestion_risk=0,
            border_delay_risk=0, political_risk=0,
            overall_risk_score=0, risk_category="Low", health_score=100
        )
        
    if delay_type == "Weather":
        risk.weather_risk = 99.0
    elif delay_type == "Traffic":
        risk.traffic_risk = 95.0
    elif delay_type == "Port":
        risk.port_congestion_risk = 100.0
        
    await risk.save()
    return {"message": f"Injected {delay_type} risk for {shipment_id}. Run analysis to see the effect."}
