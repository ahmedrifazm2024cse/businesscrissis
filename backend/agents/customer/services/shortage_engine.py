import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ShortageEngine:
    def __init__(self):
        pass

    def calculate_shortage_probability(
        self,
        current_stock: int,
        reserved_stock: int,
        incoming_inventory: int,
        outgoing_inventory: int,
        daily_demand_forecast: float,
        safety_stock: int,
        supplier_risk_score: float = 0.0,
        shipment_delay_prob: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates the probability of a shortage and the expected days remaining.
        """
        available_stock = current_stock - reserved_stock
        net_stock_future = available_stock + incoming_inventory - outgoing_inventory
        
        # Base days remaining based purely on demand vs current stock
        days_remaining = available_stock / daily_demand_forecast if daily_demand_forecast > 0 else 999.0
        
        probability = 0.0
        
        # Factor 1: Current stock vs Safety Stock
        if available_stock <= safety_stock:
            probability += 0.4
        
        # Factor 2: Future net stock (if negative, we are guaranteed a shortage unless we procure)
        if net_stock_future < safety_stock:
            probability += 0.3
            
        # Factor 3: Upstream risks
        probability += (supplier_risk_score / 100.0) * 0.15
        probability += shipment_delay_prob * 0.15
        
        # Cap probability at 1.0
        probability = min(1.0, max(0.0, probability))
        
        # Calculate expected shortage date
        expected_date = datetime.utcnow() + timedelta(days=days_remaining)
        
        trend = "Stable"
        if probability > 0.7:
            trend = "Worsening"
        elif probability < 0.3:
            trend = "Improving"
            
        confidence = 0.9 - (shipment_delay_prob * 0.2) # lower confidence if shipments are volatile
        
        return {
            "probability_of_shortage": round(probability, 2),
            "expected_shortage_date": expected_date,
            "days_remaining": round(days_remaining, 1),
            "confidence_score": round(confidence, 2),
            "trend": trend
        }

    def identify_root_causes(
        self,
        daily_demand: float,
        historical_demand: float,
        supplier_risk: float,
        shipment_delay_prob: float,
        warehouse_capacity_utilization: float,
        inventory_accuracy: float = 1.0
    ) -> List[str]:
        """Identifies driving factors behind the shortage prediction."""
        causes = []
        if daily_demand > historical_demand * 1.2:
            causes.append("Demand surge (20%+ over historical)")
        if supplier_risk > 60:
            causes.append("High supplier failure risk")
        if shipment_delay_prob > 0.5:
            causes.append("High probability of incoming shipment delays")
        if warehouse_capacity_utilization > 90:
            causes.append("Warehouse capacity bottlenecks delaying intake")
        if inventory_accuracy < 0.95:
            causes.append("Inventory record inaccuracy")
            
        if not causes:
            causes.append("Standard burn rate / Misaligned procurement planning")
            
        return causes

    def classify_risk(self, probability: float, days_remaining: float, revenue_per_unit: float, daily_demand: float) -> Tuple[float, str, float]:
        """
        Classifies risk level and estimates revenue impact.
        Returns: (risk_score, classification, revenue_impact)
        """
        risk_score = (probability * 60) + (max(0, 30 - days_remaining) / 30 * 40)
        risk_score = min(100.0, max(0.0, risk_score))
        
        classification = "Healthy"
        if risk_score >= 90 or days_remaining < 3:
            classification = "Emergency"
        elif risk_score >= 75:
            classification = "Critical"
        elif risk_score >= 50:
            classification = "High Risk"
        elif risk_score >= 25:
            classification = "Watch List"
            
        # Estimate impact: assume a 7-day shortage if it occurs
        revenue_impact = (daily_demand * 7) * revenue_per_unit * probability
        
        return round(risk_score, 2), classification, round(revenue_impact, 2)

shortage_engine = ShortageEngine()
