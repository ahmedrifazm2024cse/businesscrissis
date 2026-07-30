import pytest
from services.route_engine import route_engine
import math
from datetime import datetime, timedelta

def test_calculate_fuel():
    # Truck: baseline 3 km/l. 
    # With traffic_risk=0, efficiency=3.0. 
    # For 300km, liters = 100. Cost = 150.
    res1 = route_engine.calculate_fuel(300.0, "Truck", 0.0)
    assert math.isclose(res1["estimated_fuel_consumption_liters"], 100.0)
    assert math.isclose(res1["total_fuel_cost"], 150.0)
    
    # With traffic_risk=100, efficiency degrades by 30%.
    # eff = 3.0 * 0.7 = 2.1
    # liters = 300 / 2.1 = 142.857
    res2 = route_engine.calculate_fuel(300.0, "Truck", 100.0)
    assert res2["estimated_fuel_consumption_liters"] > 140.0

def test_predict_eta():
    base_hours = 10.0
    
    # Zero risk -> delay factor 0 -> expected == best case
    res1 = route_engine.predict_eta(base_hours, 0.0, 0.0)
    assert res1["delay_probability"] == 0.0
    assert res1["arrival_confidence"] == 1.0
    # Expected should be exactly 10 hours from now
    diff = res1["expected_eta"] - res1["best_case_eta"]
    assert diff.total_seconds() < 1
    
    # Max risk (100 traffic, 100 weather) -> delay factor 1.0
    # expected = 10 * 1.5 = 15
    # worst = 10 * 2.0 = 20
    res2 = route_engine.predict_eta(base_hours, 100.0, 100.0)
    assert res2["delay_probability"] == 1.0
    assert res2["arrival_confidence"] == 0.2 # 1.0 - 0.8
    diff_expected = res2["expected_eta"] - res2["best_case_eta"]
    assert math.isclose(diff_expected.total_seconds() / 3600, 5.0, rel_tol=0.1)

def test_calculate_overall_risk():
    # Traffic (50%), Weather (30%), Security (10%), Political (10%)
    
    # Low risk
    score, level = route_engine.calculate_overall_risk(10, 10, 10, 10)
    assert score == 10.0
    assert level == "Low"
    
    # Critical risk
    score2, level2 = route_engine.calculate_overall_risk(100, 100, 100, 100)
    assert score2 == 100.0
    assert level2 == "Critical"
    
    # High risk
    score3, level3 = route_engine.calculate_overall_risk(90, 80, 20, 20)
    # (45) + (24) + (2) + (2) = 73
    assert math.isclose(score3, 73.0)
    assert level3 == "High"
