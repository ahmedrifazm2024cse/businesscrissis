import logging
from datetime import datetime, timedelta, timezone
from models.forecast import (
    ForecastHistory, ForecastResult, ForecastRecommendation,
    ForecastAlert, ForecastJob
)
from models.domain import CoordinatorMessage, Inventory
from services.forecasting_engine import forecasting_engine
from services.trend_analyzer import trend_analyzer
from services.demand_ai import demand_ai_engine
from api.routers.websockets import manager
import json

logger = logging.getLogger(__name__)

async def run_forecast_monitor():
    """Autonomous Background Monitor - generates demand forecasts and AI recommendations."""
    logger.info("Running autonomous demand forecast monitor...")
    
    # Create a job record
    job_id = f"job_forecast_{int(datetime.now().timestamp())}"
    job = ForecastJob(job_id=job_id, status="Running")
    await job.insert()
    
    try:
        results = []
        # Get all distinct SKUs that have inventory (or we could fetch from ForecastHistory)
        inventories = await Inventory.find_all().to_list()
        
        items_processed = 0
        for item in inventories:
            sku = item.sku
            
            # 1. Collect historical demand
            # In a real system, we'd query ForecastHistory. For this architecture,
            # if missing, we'll generate some synthetic historical data to feed the engine based on current stock/outgoing
            hist_records = await ForecastHistory.find(ForecastHistory.sku == sku).sort("date").to_list()
            
            # Synthesize if not enough data
            if len(hist_records) < 14:
                base_demand = item.outgoing_stock / 30 if item.outgoing_stock > 0 else 5.0
                import random
                for i in range(30 - len(hist_records)):
                    dt = datetime.now(timezone.utc) - timedelta(days=30-i)
                    val = max(0.0, base_demand + random.uniform(-2, 2))
                    record = ForecastHistory(
                        sku=sku,
                        date=dt,
                        sales_quantity=val,
                        inventory_movement=val
                    )
                    await record.insert()
                    hist_records.append(record)
                    
            # 2. Extract values for engines
            raw_data = [{"date": r.date, "value": r.sales_quantity + r.inventory_movement} for r in hist_records]
            cleaned_data = forecasting_engine.clean_data(raw_data)
            values = [d['value'] for d in cleaned_data]
            
            # 3. Generate Forecast (Next 7 days as expected demand)
            forecast_metrics = forecasting_engine.generate_forecast(cleaned_data, horizon_days=7)
            
            # 4. Trend & Seasonality Detection
            trend = trend_analyzer.detect_trend(values)
            seasonality = trend_analyzer.detect_seasonality(values)
            pattern = trend_analyzer.detect_demand_pattern(values)
            
            # Update metrics with trend info
            forecast_metrics["trend"] = trend
            
            # Save Forecast Result
            result = ForecastResult(
                sku=sku,
                forecast_type="Weekly",
                target_date=datetime.now(timezone.utc) + timedelta(days=7),
                forecast_quantity=forecast_metrics["forecast_quantity"],
                confidence_score=forecast_metrics["confidence_score"],
                trend=trend,
                growth_percentage=forecast_metrics["growth_percentage"],
                expected_demand=forecast_metrics["expected_demand"],
                algorithm_used=forecast_metrics["algorithm_used"]
            )
            await result.insert()
            
            # 5. Determine if an anomaly / alert is needed
            # e.g., sudden spike/drop, or very low confidence, or demand > current_stock
            is_critical = False
            anomaly_type = ""
            
            if trend in ["Sudden Spike", "Sudden Drop"]:
                is_critical = True
                anomaly_type = trend
            elif forecast_metrics["expected_demand"] > item.current_stock + item.incoming_stock:
                is_critical = True
                anomaly_type = "Inventory Shortage Predicted"
            elif forecast_metrics["confidence_score"] < 0.4:
                is_critical = True
                anomaly_type = "Low Forecast Confidence"
                
            ai_rec = None
            if is_critical:
                logger.info(f"Anomaly detected for {sku}: {anomaly_type}. Running AI Analysis...")
                
                # Create Alert
                alert = ForecastAlert(
                    sku=sku,
                    title=f"Demand Anomaly: {anomaly_type}",
                    message=f"Detected {anomaly_type} for product {item.product_name}. Expected demand: {forecast_metrics['expected_demand']}",
                    severity="Critical",
                    anomaly_type=anomaly_type
                )
                await alert.insert()
                
                # 6. Gemini AI Analysis
                ai_rec = await demand_ai_engine.analyze_forecast(
                    sku=sku,
                    trend=trend,
                    seasonality=seasonality,
                    demand_pattern=pattern,
                    forecast_metrics=forecast_metrics
                )
                
                rec_data = ai_rec.get("recommendation", {})
                recommendation = ForecastRecommendation(
                    sku=sku,
                    reason=rec_data.get("reason", ai_rec.get("root_cause", "")),
                    priority=rec_data.get("priority", "High"),
                    expected_impact=rec_data.get("expected_impact", ""),
                    confidence=forecast_metrics["confidence_score"],
                    action_type=rec_data.get("action_type", "Manual Review")
                )
                await recommendation.insert()
                
                # 7. Coordinator Integration
                payload = {
                    "agent": "Demand Forecasting Agent",
                    "finding": f"Detected {anomaly_type} for {sku}.",
                    "severity": "Critical",
                    "confidence": forecast_metrics["confidence_score"],
                    "forecast": forecast_metrics,
                    "recommendations": [ai_rec],
                    "metadata": {
                        "sku": sku,
                        "trend": trend,
                        "seasonality": seasonality
                    },
                    "contributing_evidence": [{"pattern": pattern, "cleaned_data_points": len(values)}]
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_fcst_{sku}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "sku": sku,
                    "anomaly_type": anomaly_type,
                    "finding": payload["finding"],
                    "recommendation": ai_rec.get("recommendation", {}).get("action_type")
                })
                
            # 8. WebSockets Push
            await manager.broadcast(json.dumps({
                "type": "NEW_FORECAST",
                "data": {
                    "sku": sku,
                    "forecast": forecast_metrics,
                    "trend": trend,
                    "anomaly": anomaly_type if is_critical else None,
                    "ai_recommendation": ai_rec
                }
            }))
            
            items_processed += 1
            
        job.status = "Completed"
        job.end_time = datetime.now(timezone.utc)
        job.items_processed = items_processed
        await job.save()
        logger.info(f"Forecast monitor completed. Processed {items_processed} items.")
        return results
        
    except Exception as e:
        logger.error(f"Forecast monitor failed: {e}")
        job.status = "Failed"
        job.end_time = datetime.now(timezone.utc)
        job.error_message = str(e)
        await job.save()
        return []
