import pytest
from datetime import datetime, timedelta
from services.warehouse_engine import warehouse_engine
import math

def test_utilization_calculation():
    total = 10000
    used = 8500
    zones = {"A": 80, "B": 60}
    
    res = warehouse_engine.calculate_utilization(total, used, zones)
    
    assert math.isclose(res["utilization_percentage"], 85.0, abs_tol=0.1)
    assert math.isclose(res["available_capacity"], 1500.0, abs_tol=0.1)
    assert res["zone_utilization"]["A"] == 80

def test_capacity_prediction_positive_growth():
    current_utilization = 80.0 # 80% full
    inbound = 500.0
    outbound = 300.0
    total = 10000.0
    
    # Net velocity = +200 units/day
    # Remaining capacity = 2000 units
    # Days to full = 10 days
    
    res = warehouse_engine.predict_capacity(current_utilization, inbound, outbound, total)
    
    assert math.isclose(res["storage_growth_trend"], 200.0, abs_tol=0.1)
    assert math.isclose(res["capacity_remaining_days"], 10.0, abs_tol=0.1)
    assert res["expansion_requirement"] == True # < 30 days
    assert res["overflow_risk_score"] == 70.0 # < 30 days is 70.0

def test_capacity_prediction_negative_growth():
    current_utilization = 95.0
    inbound = 200.0
    outbound = 500.0
    total = 10000.0
    
    # Net velocity = -300 units/day. Will never fill.
    
    res = warehouse_engine.predict_capacity(current_utilization, inbound, outbound, total)
    
    assert res["predicted_full_date"] is None
    assert res["capacity_remaining_days"] is None
    assert res["expansion_requirement"] == True # because current_util > 95
    assert math.isclose(res["overflow_risk_score"], 100.0, abs_tol=0.1)

def test_bottleneck_detection():
    risk_factors = {"equipment_risk": 90.0}
    perf = {"avg_loading_time_hours": 5.0, "picking_efficiency": 60.0}
    util = 95.0
    
    res = warehouse_engine.analyze_risk_and_bottlenecks(risk_factors, perf, util)
    
    bottlenecks = res["bottlenecks_detected"]
    assert "Storage Congestion" in bottlenecks
    assert "Dock Congestion" in bottlenecks
    assert "Picking Delays" in bottlenecks
    assert "Equipment Failure Risk" in bottlenecks
    
    # Health should be very low due to many bottlenecks
    assert res["health_score"] < 55.0
