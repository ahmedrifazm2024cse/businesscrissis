from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import random
from models.route_intelligence import (
    Route, TrafficAnalysis, WeatherAnalysis, FuelAnalysis, RouteRisk,
    RoutePrediction, RouteRecommendation, RouteAlert, RouteHistory, RouteAIAnalysis
)
from workflows.route_monitor import run_route_monitor

router = APIRouter(prefix="/routes", tags=["route"])

@router.get("", response_model=List[Route])
async def get_routes(skip: int = 0, limit: int = 50):
    return await Route.find_all().sort("-created_at").skip(skip).limit(limit).to_list()

@router.get("/traffic", response_model=List[TrafficAnalysis])
async def get_traffic(skip: int = 0, limit: int = 50):
    return await TrafficAnalysis.find_all().sort("-analyzed_at").skip(skip).limit(limit).to_list()

@router.get("/weather", response_model=List[WeatherAnalysis])
async def get_weather(skip: int = 0, limit: int = 50):
    return await WeatherAnalysis.find_all().sort("-analyzed_at").skip(skip).limit(limit).to_list()

@router.get("/fuel", response_model=List[FuelAnalysis])
async def get_fuel(skip: int = 0, limit: int = 50):
    return await FuelAnalysis.find_all().sort("-analyzed_at").skip(skip).limit(limit).to_list()

@router.get("/risk", response_model=List[RouteRisk])
async def get_risk(skip: int = 0, limit: int = 50):
    return await RouteRisk.find_all().sort("-analyzed_at").skip(skip).limit(limit).to_list()

@router.get("/predictions", response_model=List[RoutePrediction])
async def get_predictions(skip: int = 0, limit: int = 50):
    return await RoutePrediction.find_all().sort("-predicted_at").skip(skip).limit(limit).to_list()

@router.get("/analysis", response_model=List[RouteAIAnalysis])
async def get_ai_analysis(skip: int = 0, limit: int = 50):
    return await RouteAIAnalysis.find_all().sort("-generated_at").skip(skip).limit(limit).to_list()

@router.post("/analyze")
async def trigger_route_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_route_monitor)
    return {"message": "Route monitor started in background"}

@router.post("/simulate")
async def simulate_route_emergency():
    """Injects a severe traffic and weather scenario for demonstration."""
    mock_id = f"RT-{random.randint(1000,9999)}"
    mock_route = Route(
        route_id=mock_id,
        origin="LA-PORT",
        destination="NYC-HUB",
        distance_km=4500.0,
        estimated_travel_time_hours=48.0,
        vehicle_type="Truck",
        shipment_priority="Critical",
        status="Active"
    )
    await mock_route.insert()
    
    ta = TrafficAnalysis(
        route_id=mock_id,
        congestion_level="Severe",
        accidents_reported=3,
        road_closures=2,
        construction_zones=1,
        peak_hour_overlap_hours=4.0,
        traffic_risk_score=95.0
    )
    await ta.insert()
    
    wa = WeatherAnalysis(
        route_id=mock_id,
        conditions=["Storm", "Windy"],
        visibility_km=0.5,
        temperature_celsius=-2.0,
        wind_speed_kmh=120.0,
        weather_risk_score=90.0
    )
    await wa.insert()
    
    rr = RouteRisk(
        route_id=mock_id,
        traffic_risk=95.0,
        weather_risk=90.0,
        political_risk=10,
        security_risk=10,
        road_quality_risk=40,
        vehicle_risk=5,
        overall_risk_score=92.5,
        risk_level="Critical"
    )
    await rr.insert()
    
    return {"message": f"Injected Critical Route Emergency for route {mock_id}. Dashboard updated."}
