import logging
from typing import Dict, List, Any
import math
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProcurementEngine:
    def __init__(self):
        pass

    def calculate_eoq(self, annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
        """
        Calculates Economic Order Quantity (EOQ).
        Formula: sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
        """
        if holding_cost_per_unit <= 0:
            return 0.0
        eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
        return round(eoq, 2)

    def determine_timing_strategy(self, current_stock: float, reorder_point: float, predicted_price_change: float) -> str:
        """
        Determines the purchase timing strategy based on inventory levels and market price trends.
        """
        if current_stock <= reorder_point * 0.5:
            return "Emergency Purchase"
        elif current_stock <= reorder_point:
            if predicted_price_change > 0:
                return "Buy Immediately" # Prices going up
            else:
                return "Delay Purchase" # Wait for prices to drop
        else:
            if predicted_price_change > 10.0:
                return "Bulk Purchase" # Stock up before huge price spike
            return "Stable"

    def rank_suppliers(self, suppliers: List[Dict[str, Any]], required_quantity: float) -> List[Dict[str, Any]]:
        """
        Ranks suppliers based on Price, Lead Time, and Risk.
        Lower score is better.
        """
        ranked = []
        for s in suppliers:
            if s.get("capacity", float('inf')) < required_quantity:
                continue # Cannot fulfill
                
            price_weight = 0.5
            lead_time_weight = 0.3
            risk_weight = 0.2
            
            # Normalize (assuming higher is worse for all these)
            score = (s["price_per_unit"] * price_weight) + (s["lead_time_days"] * lead_time_weight) + (s["risk_score"] * risk_weight)
            ranked.append({
                "supplier_id": s["supplier_id"],
                "score": score,
                "price": s["price_per_unit"],
                "lead_time": s["lead_time_days"]
            })
            
        ranked.sort(key=lambda x: x["score"])
        return ranked

    def calculate_risk(self, factors: Dict[str, float]) -> float:
        """
        Calculates overall procurement risk based on multiple factors.
        """
        weights = {
            "supplier_risk": 0.4,
            "transportation_risk": 0.2,
            "political_risk": 0.2,
            "weather_risk": 0.1,
            "currency_risk": 0.1
        }
        
        overall_risk = sum(factors.get(k, 0.0) * w for k, w in weights.items())
        return min(100.0, round(overall_risk, 2))

procurement_engine = ProcurementEngine()
