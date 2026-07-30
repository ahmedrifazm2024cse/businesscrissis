import pytest
from services.cost_engine import cost_engine
import math

class MockItem:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_aggregate_costs():
    inv_data = [MockItem(current_stock=1000, unit_cost=10.0), MockItem(current_stock=500, unit_cost=20.0)]
    # (1000 * 1.0) + (500 * 2.0) = 1000 + 1000 = 2000
    
    wh_data = [MockItem(utilization_percentage=80.0), MockItem(utilization_percentage=90.0)]
    # (80 * 100) + (90 * 100) = 8000 + 9000 = 17000
    
    proc_data = [MockItem(estimated_cost=5000.0, priority_level="Normal"), MockItem(estimated_cost=2000.0, priority_level="Critical")]
    # total = 7000
    # emergency = 2000
    
    ship_data = [MockItem(), MockItem(), MockItem()]
    # 3 * 1500 = 4500
    
    costs = cost_engine.aggregate_costs(inv_data, wh_data, proc_data, ship_data)
    
    assert costs["inventory_holding_cost"] == 2000.0
    assert costs["warehouse_cost"] == 17000.0
    assert costs["procurement_cost"] == 7000.0
    assert costs["transportation_cost"] == 4500.0
    assert costs["emergency_shipping_cost"] == 2000.0
    assert costs["fuel_cost"] == 4500.0 * 0.2
    assert costs["total_cost"] == 2000 + 17000 + 7000 + 4500 + 900 + 2000 # 33400

def test_check_budgets():
    actual_costs = {
        "inventory_holding_cost": 25000,
        "warehouse_cost": 14000,
        "transportation_cost": 90000,
        "procurement_cost": 290000
    }
    
    budgets = {
        "Inventory": 30000.0,      # Under Budget
        "Warehouse": 15000.0,      # On Track (within 10%)
        "Transportation": 80000.0, # Over Budget
        "Procurement": 300000.0    # On Track
    }
    
    results = cost_engine.check_budgets(actual_costs, budgets)
    
    res_dict = {r["department"]: r["status"] for r in results}
    
    assert res_dict["Inventory"] == "Under Budget"
    assert res_dict["Warehouse"] == "On Track"
    assert res_dict["Transportation"] == "Over Budget"
    assert res_dict["Procurement"] == "On Track"

def test_analyze_trend():
    # Growth
    res = cost_engine.analyze_trend(1200, 1000)
    assert math.isclose(res["growth_percentage"], 20.0)
    assert res["reduction_percentage"] == 0.0
    
    # Reduction
    res2 = cost_engine.analyze_trend(800, 1000)
    assert res2["growth_percentage"] == 0.0
    assert math.isclose(res2["reduction_percentage"], 20.0)

def test_identify_waste():
    costs = {
        "total_cost": 100000.0,
        "emergency_shipping_cost": 15000.0, # 15% -> High Emergency
        "inventory_holding_cost": 30000.0   # 30% -> Overstocking
    }
    trends = {"growth_percentage": 20.0} # -> Rapid growth
    
    waste = cost_engine.identify_waste(costs, trends)
    
    assert len(waste) == 3
    assert any("Emergency" in w for w in waste)
    assert any("Overstocking" in w for w in waste)
    assert any("Rapid" in w for w in waste)
