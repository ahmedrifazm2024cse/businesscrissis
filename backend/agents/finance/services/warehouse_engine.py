import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WarehouseEngine:
    def __init__(self):
        pass

    def calculate_utilization(self, total_capacity: float, used_capacity: float, zone_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates warehouse storage utilization percentages.
        """
        if total_capacity <= 0:
            return {"utilization_percentage": 0.0, "available_capacity": 0.0}
            
        util_pct = (used_capacity / total_capacity) * 100.0
        available = total_capacity - used_capacity
        
        # Determine specific utilizations (mock math for now)
        rack = util_pct * 0.9
        shelf = util_pct * 1.1
        cold_storage_used = zone_data.get("cold_storage_used", 0)
        cold_storage_cap = zone_data.get("cold_storage_capacity", 1)
        
        return {
            "utilization_percentage": round(util_pct, 2),
            "available_capacity": round(available, 2),
            "rack_utilization": round(min(100.0, rack), 2),
            "shelf_utilization": round(min(100.0, shelf), 2),
            "cold_storage_used": cold_storage_used,
            "cold_storage_capacity": cold_storage_cap,
            "zone_utilization": zone_data
        }

    def predict_capacity(self, current_utilization: float, inbound_velocity_daily: float, outbound_velocity_daily: float, total_capacity: float) -> Dict[str, Any]:
        """
        Predicts when the warehouse will hit 100% capacity based on net velocity.
        """
        net_velocity = inbound_velocity_daily - outbound_velocity_daily
        
        if net_velocity <= 0 or current_utilization >= 100.0:
            return {
                "predicted_full_date": None,
                "capacity_remaining_days": None,
                "storage_growth_trend": net_velocity,
                "overflow_risk_score": 0.0 if current_utilization < 90 else 100.0,
                "expansion_requirement": current_utilization >= 95,
                "confidence_score": 0.9
            }
            
        remaining_capacity = total_capacity * ((100.0 - current_utilization) / 100.0)
        days_to_full = remaining_capacity / net_velocity
        
        predicted_date = datetime.now() + timedelta(days=days_to_full)
        
        risk = 0.0
        if days_to_full < 7:
            risk = 95.0
        elif days_to_full < 30:
            risk = 70.0
        elif days_to_full < 90:
            risk = 40.0
            
        return {
            "predicted_full_date": predicted_date,
            "capacity_remaining_days": round(days_to_full, 1),
            "storage_growth_trend": round(net_velocity, 2),
            "overflow_risk_score": risk,
            "expansion_requirement": days_to_full < 30,
            "confidence_score": 0.85
        }

    def analyze_risk_and_bottlenecks(self, risk_factors: Dict[str, float], performance: Dict[str, float], utilization: float) -> Dict[str, Any]:
        """
        Evaluates hazards and identifies operational bottlenecks.
        """
        # 1. Risk calculation
        weights = {
            "fire_risk": 0.2,
            "flood_risk": 0.1,
            "equipment_risk": 0.2,
            "power_outage_risk": 0.1,
            "temperature_risk": 0.2,
            "inventory_damage_risk": 0.1,
            "security_risk": 0.1
        }
        
        overall_risk = sum(risk_factors.get(k, 0.0) * w for k, w in weights.items())
        
        # 2. Bottleneck detection
        bottlenecks = []
        if utilization > 90:
            bottlenecks.append("Storage Congestion")
        if performance.get("avg_loading_time_hours", 0) > 4:
            bottlenecks.append("Dock Congestion")
        if performance.get("picking_efficiency", 100) < 70:
            bottlenecks.append("Picking Delays")
        if risk_factors.get("equipment_risk", 0) > 80:
            bottlenecks.append("Equipment Failure Risk")
            
        # 3. Health Score
        health = 100.0 - (overall_risk * 0.5) - (len(bottlenecks) * 10)
        
        return {
            "overall_risk_score": round(overall_risk, 2),
            "health_score": max(0.0, round(health, 2)),
            "bottlenecks_detected": bottlenecks
        }

warehouse_engine = WarehouseEngine()
