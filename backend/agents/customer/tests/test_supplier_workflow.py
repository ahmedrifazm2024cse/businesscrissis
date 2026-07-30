import pytest
from datetime import datetime
from services.supplier_engine import supplier_engine
import math

def test_performance_score():
    metrics = {
        "on_time_delivery_pct": 90.0,
        "quality_acceptance_rate": 95.0,
        "order_fulfillment_rate": 100.0,
        "sla_compliance": 100.0,
        "defect_rate": 2.0,
        "cancellation_rate": 1.0,
        "return_rate": 0.0
    }
    score = supplier_engine.calculate_performance_score(metrics)
    
    base = (90 * 0.4) + (95 * 0.3) + (100 * 0.2) + (100 * 0.1) # 36 + 28.5 + 20 + 10 = 94.5
    penalty = (2 * 2.0) + (1 * 1.5) # 4 + 1.5 = 5.5
    expected = 94.5 - 5.5 # 89.0
    
    assert math.isclose(score, 89.0, abs_tol=0.1)

def test_risk_score():
    risks = {
        "financial_risk": 50.0,
        "delivery_risk": 50.0,
        "country_risk": 50.0,
        "political_risk": 50.0,
        "natural_disaster_risk": 50.0,
        "single_source_dependency": 100.0, # 15
        "capacity_risk": 50.0,
        "compliance_risk": 50.0
    }
    
    result = supplier_engine.calculate_risk_score(risks)
    
    # 50 * (0.85) + 100 * 0.15 = 42.5 + 15 = 57.5
    assert math.isclose(result["overall_risk_score"], 57.5, abs_tol=0.1)
    assert result["risk_category"] == "High"

def test_failure_prediction():
    perf = 50.0 # prob_perf = 0.5
    risk = 80.0 # prob_risk = 0.8
    delay = 15.0 # prob_delay = 0.5
    
    result = supplier_engine.predict_failure(perf, risk, delay)
    
    # (0.8 * 0.5) + (0.5 * 0.3) + (0.5 * 0.2)
    # 0.40 + 0.15 + 0.10 = 0.65
    
    assert math.isclose(result["failure_probability"], 0.65, abs_tol=0.01)
    assert result["estimated_business_impact"] == "High"
    assert result["expected_disruption_date"] is not None

def test_rank_alternatives():
    target = {"id": "SUP1", "cost": 1.0}
    alts = [
        {"id": "ALT1", "cost_multiplier": 1.5, "distance_km": 100, "risk_score": 20, "capacity_pct": 100},
        {"id": "ALT2", "cost_multiplier": 1.0, "distance_km": 500, "risk_score": 80, "capacity_pct": 50}
    ]
    
    ranked = supplier_engine.rank_alternatives(target, alts)
    
    assert len(ranked) == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    
    # ALT1 should be higher due to much lower risk and higher capacity, despite cost
    assert ranked[0]["supplier_id"] == "ALT1"
