import logging
from datetime import datetime, timedelta, timezone
from models.domain import (
    Inventory, InventoryAlert, InventoryPrediction, 
    InventoryRecommendation, CoordinatorMessage
)
from services.inventory_health import inventory_health_engine
from services.stockout_prediction import stockout_prediction_engine
from services.inventory_ai import inventory_ai_engine
from api.routers.websockets import manager
import random

logger = logging.getLogger(__name__)

async def run_inventory_monitor():
    """Autonomous Background Monitor - scans inventory and generates intelligence."""
    logger.info("Running autonomous inventory monitor scan...")
    
    results = []
    inventories = await Inventory.find_all().to_list()
    
    for item in inventories:
        # 1. Health Engine
        # We simulate a daily demand history for the prediction engine.
        # In a real scenario, this would come from a sales/orders collection.
        # Let's generate a synthetic history based on outgoing_stock rate.
        avg_daily = item.outgoing_stock / 30 if item.outgoing_stock > 0 else 5.0
        # Add some random variance
        demand_history = [max(0.0, avg_daily + random.uniform(-2, 2)) for _ in range(14)]
        
        health_metrics = inventory_health_engine.calculate_health(item, estimated_daily_demand=avg_daily)
        prediction_metrics = stockout_prediction_engine.predict(health_metrics["available_stock"], demand_history)
        
        # Conditions for generating an alert & recommendation
        is_critical = health_metrics["stock_status"] == "Critical" or prediction_metrics["probability"] > 0.7
        
        if is_critical:
            # Check for duplicate active alerts in the last 24 hours
            recent_alert = await InventoryAlert.find_one(
                InventoryAlert.sku == item.sku,
                InventoryAlert.created_at > datetime.now(timezone.utc) - timedelta(hours=24)
            )
            
            if not recent_alert:
                logger.info(f"Critical inventory state detected for {item.sku}. Generating insights...")
                
                # Create Alert
                severity = "Critical" if prediction_metrics["probability"] > 0.85 else "Warning"
                title = f"Stockout Warning for {item.sku}"
                message = f"Product {item.product_name} is predicted to stockout in {prediction_metrics['days_until_stockout']} days."
                
                alert = InventoryAlert(
                    sku=item.sku,
                    title=title,
                    message=message,
                    severity=severity
                )
                await alert.insert()
                
                # Create Prediction Record
                stockout_date_val = None
                if prediction_metrics["stockout_date"]:
                    stockout_date_val = datetime.fromisoformat(prediction_metrics["stockout_date"])
                    
                prediction = InventoryPrediction(
                    sku=item.sku,
                    stockout_date=stockout_date_val,
                    probability=prediction_metrics["probability"],
                    confidence=prediction_metrics["confidence"]
                )
                await prediction.insert()
                
                # Generate AI Recommendation
                ai_rec = await inventory_ai_engine.generate_recommendation(
                    item.sku, item.product_name, health_metrics, prediction_metrics
                )
                
                recommendation = InventoryRecommendation(
                    sku=item.sku,
                    root_cause=ai_rec.get("root_cause", ""),
                    business_impact=ai_rec.get("business_impact", ""),
                    recommended_action=ai_rec.get("recommended_action", ""),
                    expected_outcome=ai_rec.get("expected_outcome", ""),
                    priority=ai_rec.get("priority", "High"),
                    confidence=ai_rec.get("confidence", 0.0)
                )
                await recommendation.insert()
                
                # Create Coordinator Message
                payload = {
                    "agent": "Supply Chain Agent",
                    "finding": message,
                    "severity": severity,
                    "confidence": prediction_metrics["confidence"],
                    "metadata": {
                        "sku": item.sku,
                        "days_remaining": health_metrics["days_remaining"],
                        "warehouse": item.warehouse_id
                    },
                    "recommendations": [ai_rec],
                    "contributing_evidence": [health_metrics, prediction_metrics]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_{item.sku}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                import json
                
                # Broadcast via Websockets
                await manager.broadcast(json.dumps({
                    "type": "NEW_INVENTORY_ALERT",
                    "data": {
                        "sku": item.sku,
                        "title": title,
                        "message": message,
                        "severity": severity,
                        "ai_recommendation": ai_rec
                    }
                }))
                
                results.append({
                    "sku": item.sku,
                    "severity": severity,
                    "message": message,
                    "recommendation": ai_rec.get("recommended_action")
                })
    
    logger.info("Autonomous inventory monitor scan completed.")
    return results
