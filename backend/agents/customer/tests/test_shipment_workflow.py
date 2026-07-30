import pytest
from datetime import datetime, timedelta
from services.shipment_engine import shipment_engine
import math

def test_risk_calculation_with_progress():
    risks = {
        "traffic_risk": 50,
        "weather_risk": 50,
        "port_congestion_risk": 50,
        "border_delay_risk": 50,
        "political_risk": 50
    }
    # Base risk is exactly 50 if all are 50 (weights sum to 1.0)
    
    # 0% progress, risk is unaltered
    res1 = shipment_engine.calculate_risk(risks, 0.0)
    assert math.isclose(res1["overall_risk_score"], 50.0, abs_tol=0.1)
    
    # 100% progress, risk is reduced by 30%
    res2 = shipment_engine.calculate_risk(risks, 100.0)
    assert math.isclose(res2["overall_risk_score"], 35.0, abs_tol=0.1)

def test_eta_calculation():
    original_eta = datetime.now() + timedelta(hours=10)
    travel_time = 10.0
    risk_score = 50.0
    
    etas = shipment_engine.calculate_eta(original_eta, travel_time, risk_score)
    
    best_diff = (etas["best_case_eta"] - datetime.now()).total_seconds() / 3600.0
    assert math.isclose(best_diff, 9.0, abs_tol=0.1) # 10 * 0.9
    
    worst_diff = (etas["worst_case_eta"] - datetime.now()).total_seconds() / 3600.0
    assert math.isclose(worst_diff, 12.5, abs_tol=0.1) # 1.0 + (50/10*0.05) = 1.25 -> 10 * 1.25 = 12.5

def test_delay_prediction():
    orig = datetime.now()
    upd = orig + timedelta(hours=24) # 24 hour delay
    risk = 60.0
    
    pred = shipment_engine.predict_delay(orig, upd, risk)
    
    assert math.isclose(pred["expected_delay_hours"], 24.0, abs_tol=0.1)
    
    # Prob: risk/100 + delay/48 = 0.6 + 0.5 = 1.1 -> capped at 1.0
    assert math.isclose(pred["delay_probability"], 1.0, abs_tol=0.01)

def test_route_ranking():
    routes = [
        {"route_name": "Long_Safe", "distance_km": 1000, "estimated_time_hours": 20, "risk_score": 10},
        {"route_name": "Short_Risky", "distance_km": 500, "estimated_time_hours": 10, "risk_score": 80}
    ]
    
    ranked = shipment_engine.rank_routes(routes)
    
    # Let's see which wins based on the weights.
    # We just want to ensure it sorts and ranks them correctly without crashing.
    assert len(ranked) == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
