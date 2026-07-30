import logging
from typing import Dict, List, Any
import math

logger = logging.getLogger(__name__)

class CostEngine:
    def __init__(self):
        pass

    def aggregate_costs(self, inventory_data: List[Any], warehouse_data: List[Any], procurement_data: List[Any], shipment_data: List[Any]) -> Dict[str, float]:
        """Aggregates costs from various supply chain sectors into a single breakdown."""
        # Simulated logic for parsing all cross-domain data
        inv_cost = sum(i.current_stock * (i.unit_cost * 0.1) for i in inventory_data) if inventory_data else 5000.0
        wh_cost = sum(w.utilization_percentage * 100 for w in warehouse_data) if warehouse_data else 15000.0
        proc_cost = sum(p.estimated_cost for p in procurement_data) if procurement_data else 25000.0
        ship_cost = len(shipment_data) * 1500.0 if shipment_data else 8000.0
        
        fuel_cost = ship_cost * 0.2
        emergency_cost = sum(p.estimated_cost for p in procurement_data if getattr(p, 'priority_level', '') == 'Critical') if procurement_data else 0.0

        total = inv_cost + wh_cost + proc_cost + ship_cost + fuel_cost + emergency_cost
        
        return {
            "inventory_holding_cost": inv_cost,
            "warehouse_cost": wh_cost,
            "transportation_cost": ship_cost,
            "procurement_cost": proc_cost,
            "supplier_cost": proc_cost * 0.9, # Supplier base cost
            "fuel_cost": fuel_cost,
            "emergency_shipping_cost": emergency_cost,
            "total_cost": total
        }

    def check_budgets(self, actual_costs: Dict[str, float], budgets: Dict[str, float]) -> List[Dict[str, Any]]:
        """Compares actuals against allocated budgets and returns variances."""
        results = []
        mapping = {
            "Inventory": "inventory_holding_cost",
            "Warehouse": "warehouse_cost",
            "Transportation": "transportation_cost",
            "Procurement": "procurement_cost"
        }
        
        for dept, budget in budgets.items():
            actual = actual_costs.get(mapping.get(dept, ""), 0.0)
            variance = budget - actual
            status = "Under Budget"
            if variance < 0:
                status = "Over Budget"
            elif variance < (budget * 0.1):
                status = "On Track"
                
            results.append({
                "department": dept,
                "allocated_budget": budget,
                "actual_spend": actual,
                "variance": variance,
                "status": status
            })
            
        return results

    def analyze_trend(self, current_total: float, historical_total: float) -> Dict[str, float]:
        """Calculates growth or reduction percentage."""
        if historical_total == 0:
            return {"growth_percentage": 0.0, "reduction_percentage": 0.0}
            
        diff = current_total - historical_total
        pct = (abs(diff) / historical_total) * 100
        
        if diff > 0:
            return {"growth_percentage": round(pct, 2), "reduction_percentage": 0.0}
        else:
            return {"growth_percentage": 0.0, "reduction_percentage": round(pct, 2)}

    def identify_waste(self, costs: Dict[str, float], trends: Dict[str, float]) -> List[str]:
        """Identifies specific areas of cost waste based on thresholds."""
        waste = []
        if costs.get("emergency_shipping_cost", 0) > (costs.get("total_cost", 1) * 0.1):
            waste.append("High Emergency Shipping Costs detected (>10% of total spend).")
        if costs.get("inventory_holding_cost", 0) > (costs.get("total_cost", 1) * 0.25):
            waste.append("Overstocking identified. Holding costs exceed 25% of total spend.")
        if trends.get("growth_percentage", 0) > 15.0:
            waste.append("Rapid overall cost growth (+15%) without corresponding revenue indicator.")
        return waste

cost_engine = CostEngine()
