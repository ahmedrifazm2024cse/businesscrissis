from models.domain import Inventory
from typing import Dict, Any

class InventoryHealthEngine:
    @staticmethod
    def calculate_health(item: Inventory, estimated_daily_demand: float = 10.0) -> Dict[str, Any]:
        """Calculates health metrics for a given inventory item."""
        
        # 1. Available Stock
        available_stock = item.current_stock + item.incoming_stock - item.reserved_stock - item.outgoing_stock
        
        # 2. Days Remaining
        if estimated_daily_demand > 0:
            days_remaining = available_stock / estimated_daily_demand
        else:
            days_remaining = 999.0 # arbitrary large number if no demand
            
        # 3. Stock Status & Risk Score
        risk_score = 0.0
        status = "Healthy"
        understock = False
        overstock = False
        dead_stock = False
        
        if available_stock <= item.safety_stock:
            status = "Critical"
            risk_score = 90.0 + max(0.0, 10.0 * (1 - (available_stock / max(1, item.safety_stock))))
            understock = True
        elif available_stock <= item.reorder_point:
            status = "Warning"
            risk_score = 50.0 + (40.0 * (1 - (available_stock - item.safety_stock) / max(1, item.reorder_point - item.safety_stock)))
        else:
            # Overstock check: if days remaining > 90
            if days_remaining > 90:
                overstock = True
                status = "Warning"
                risk_score = 40.0 # moderate risk for holding costs
            
        # Dead stock check (high stock, 0 outgoing over time - using heuristic here)
        if item.current_stock > 0 and estimated_daily_demand == 0.0:
            dead_stock = True
            status = "Warning"
            risk_score = max(risk_score, 60.0)
            
        # 4. Inventory Health Score (Inverse of Risk)
        health_score = max(0.0, 100.0 - risk_score)
        
        return {
            "available_stock": available_stock,
            "days_remaining": round(days_remaining, 2),
            "health_score": round(health_score, 2),
            "risk_score": round(risk_score, 2),
            "stock_status": status,
            "is_overstock": overstock,
            "is_understock": understock,
            "is_dead_stock": dead_stock
        }

inventory_health_engine = InventoryHealthEngine()
