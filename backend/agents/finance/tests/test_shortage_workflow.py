import pytest
from services.shortage_engine import shortage_engine
import math
from datetime import datetime, timedelta

def test_calculate_shortage_probability():
    # Healthy scenario
    # available = 100 - 10 = 90
    # incoming = 50, outgoing = 20 -> net future = 120
    # daily demand = 10, safety stock = 30
    # days remaining = 90 / 10 = 9
    # available (90) > safety (30) -> ok
    # net future (120) > safety (30) -> ok
    # probability = 0
    res1 = shortage_engine.calculate_shortage_probability(
        current_stock=100,
        reserved_stock=10,
        incoming_inventory=50,
        outgoing_inventory=20,
        daily_demand_forecast=10.0,
        safety_stock=30,
        supplier_risk_score=0.0,
        shipment_delay_prob=0.0
    )
    assert res1["probability_of_shortage"] == 0.0
    assert math.isclose(res1["days_remaining"], 9.0)
    assert res1["trend"] == "Improving"

    # Emergency scenario
    # available = 20 - 5 = 15
    # incoming = 0, outgoing = 10 -> net future = 5
    # daily demand = 10, safety stock = 30
    # available (15) <= safety (30) -> +0.4
    # net future (5) < safety (30) -> +0.3
    # supplier risk = 100 -> +0.15
    # shipment delay prob = 1.0 -> +0.15
    # prob = 1.0
    res2 = shortage_engine.calculate_shortage_probability(
        current_stock=20,
        reserved_stock=5,
        incoming_inventory=0,
        outgoing_inventory=10,
        daily_demand_forecast=10.0,
        safety_stock=30,
        supplier_risk_score=100.0,
        shipment_delay_prob=1.0
    )
    assert res2["probability_of_shortage"] == 1.0
    assert math.isclose(res2["days_remaining"], 1.5)
    assert res2["trend"] == "Worsening"

def test_classify_risk():
    # Healthy
    score, level, impact = shortage_engine.classify_risk(
        probability=0.0,
        days_remaining=40.0,
        revenue_per_unit=100.0,
        daily_demand=10.0
    )
    assert score == 0.0
    assert level == "Healthy"
    assert impact == 0.0
    
    # Critical
    # prob=0.8, days=15 -> score = (0.8 * 60) + (15/30 * 40) = 48 + 20 = 68 (High Risk)
    score2, level2, impact2 = shortage_engine.classify_risk(
        probability=0.8,
        days_remaining=15.0,
        revenue_per_unit=100.0,
        daily_demand=10.0
    )
    assert score2 == 68.0
    assert level2 == "High Risk"
    assert impact2 == 10.0 * 7 * 100.0 * 0.8
    
    # Emergency (days < 3 overrides to Emergency)
    score3, level3, impact3 = shortage_engine.classify_risk(
        probability=0.5,
        days_remaining=2.0,
        revenue_per_unit=100.0,
        daily_demand=10.0
    )
    assert level3 == "Emergency"

def test_identify_root_causes():
    # Multiple causes
    causes = shortage_engine.identify_root_causes(
        daily_demand=20.0,
        historical_demand=10.0, # 100% surge
        supplier_risk=80.0,
        shipment_delay_prob=0.8,
        warehouse_capacity_utilization=95.0,
        inventory_accuracy=0.9
    )
    assert len(causes) == 5
    
    # Standard burn rate
    causes2 = shortage_engine.identify_root_causes(
        daily_demand=10.0,
        historical_demand=10.0,
        supplier_risk=20.0,
        shipment_delay_prob=0.1,
        warehouse_capacity_utilization=50.0,
        inventory_accuracy=1.0
    )
    assert len(causes2) == 1
    assert "Standard burn rate" in causes2[0]
