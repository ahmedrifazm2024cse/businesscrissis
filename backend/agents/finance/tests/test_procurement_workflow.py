import pytest
from services.procurement_engine import procurement_engine
import math

def test_eoq_calculation():
    annual_demand = 12000
    order_cost = 50.0
    holding_cost = 2.0
    
    # sqrt( (2 * 12000 * 50) / 2 ) = sqrt( 1,200,000 / 2 ) = sqrt( 600,000 ) = 774.6
    
    eoq = procurement_engine.calculate_eoq(annual_demand, order_cost, holding_cost)
    assert math.isclose(eoq, 774.6, abs_tol=0.1)

def test_eoq_zero_holding_cost():
    eoq = procurement_engine.calculate_eoq(1000, 50, 0)
    assert eoq == 0.0

def test_timing_strategy_emergency():
    # current_stock <= reorder_point * 0.5
    timing = procurement_engine.determine_timing_strategy(20, 100, 5.0)
    assert timing == "Emergency Purchase"

def test_timing_strategy_buy_immediate():
    # current_stock <= reorder_point and price going up
    timing = procurement_engine.determine_timing_strategy(90, 100, 5.0)
    assert timing == "Buy Immediately"

def test_timing_strategy_delay():
    # current_stock <= reorder_point and price going down
    timing = procurement_engine.determine_timing_strategy(90, 100, -2.0)
    assert timing == "Delay Purchase"

def test_timing_strategy_bulk():
    # stock fine, but massive price spike coming
    timing = procurement_engine.determine_timing_strategy(150, 100, 15.0)
    assert timing == "Bulk Purchase"

def test_supplier_ranking():
    suppliers = [
        {"supplier_id": "S1", "price_per_unit": 100, "lead_time_days": 10, "risk_score": 50, "capacity": 1000},
        {"supplier_id": "S2", "price_per_unit": 80,  "lead_time_days": 15, "risk_score": 40, "capacity": 1000},
        {"supplier_id": "S3", "price_per_unit": 90,  "lead_time_days": 5,  "risk_score": 20, "capacity": 1000}, # Should win: low price, low lead time, low risk
        {"supplier_id": "S4", "price_per_unit": 50,  "lead_time_days": 2,  "risk_score": 10, "capacity": 100}   # Cannot fulfill quantity
    ]
    
    ranked = procurement_engine.rank_suppliers(suppliers, required_quantity=500)
    
    assert len(ranked) == 3
    assert ranked[0]["supplier_id"] == "S3"

def test_risk_calculation():
    factors = {
        "supplier_risk": 50, # 0.4 = 20
        "transportation_risk": 60, # 0.2 = 12
        "political_risk": 30, # 0.2 = 6
        "weather_risk": 10, # 0.1 = 1
        "currency_risk": 20 # 0.1 = 2
    }
    
    # 20 + 12 + 6 + 1 + 2 = 41
    
    risk = procurement_engine.calculate_risk(factors)
    assert math.isclose(risk, 41.0, abs_tol=0.1)
