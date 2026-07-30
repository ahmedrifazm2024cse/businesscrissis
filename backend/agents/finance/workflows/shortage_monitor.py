import logging
from datetime import datetime
import json
import random
from models.domain import Inventory, CoordinatorMessage
from models.shortage_intelligence import (
    ProductShortage, ShortagePrediction, ProductRiskScore, ShortageAlert,
    ShortageRecommendation, ShortageAIAnalysis, ShortageHistory
)
from services.shortage_engine import shortage_engine
from services.shortage_ai import shortage_ai_engine
from api.routers.websockets import manager

logger = logging.getLogger(__name__)

async def run_shortage_monitor():
    """Autonomous Background Monitor - predicts product shortages."""
    logger.info("Running autonomous product shortage monitor...")
    
    try:
        results = []
        products = await Inventory.find_all().to_list()
        
        # If no products, we can't really monitor, but for safety just return
        if not products:
            logger.info("No products found for shortage monitoring.")
            return []

        for product in products:
            # Gather aggregate signals (mocking upstream engines for now if real data not easily mapped, but we have Inventory)
            # In a real integrated system we'd pull from SupplierRisk, ForecastResult, ShipmentPrediction, etc.
            daily_demand = random.uniform(5.0, 50.0)
            supplier_risk = random.uniform(10.0, 50.0)
            shipment_delay_prob = random.uniform(0.0, 0.4)
            
            ps = ProductShortage(
                product_id=str(product.id),
                sku=product.sku,
                current_stock=product.quantity,
                reserved_stock=int(product.quantity * 0.1),
                incoming_inventory=random.randint(0, 100),
                outgoing_inventory=int(product.quantity * 0.15),
                daily_demand_forecast=daily_demand,
                safety_stock=int(daily_demand * 5),
                reorder_point=int(daily_demand * 10),
                buffer_stock=int(daily_demand * 2)
            )
            await ps.insert()
            
            # Predict
            pred_data = shortage_engine.calculate_shortage_probability(
                current_stock=ps.current_stock,
                reserved_stock=ps.reserved_stock,
                incoming_inventory=ps.incoming_inventory,
                outgoing_inventory=ps.outgoing_inventory,
                daily_demand_forecast=ps.daily_demand_forecast,
                safety_stock=ps.safety_stock,
                supplier_risk_score=supplier_risk,
                shipment_delay_prob=shipment_delay_prob
            )
            
            # Root causes
            root_causes = shortage_engine.identify_root_causes(
                daily_demand=ps.daily_demand_forecast,
                historical_demand=daily_demand * 0.9,
                supplier_risk=supplier_risk,
                shipment_delay_prob=shipment_delay_prob,
                warehouse_capacity_utilization=random.uniform(50, 95)
            )
            
            # Risk
            risk_score, risk_level, revenue_impact = shortage_engine.classify_risk(
                probability=pred_data["probability_of_shortage"],
                days_remaining=pred_data["days_remaining"],
                revenue_per_unit=product.unit_price,
                daily_demand=ps.daily_demand_forecast
            )
            
            # Save Prediction & Risk
            sp = ShortagePrediction(
                product_id=ps.product_id,
                sku=ps.sku,
                criticality_level=risk_level,
                **pred_data
            )
            await sp.insert()
            
            prs = ProductRiskScore(
                product_id=ps.product_id,
                sku=ps.sku,
                risk_score=risk_score,
                classification=risk_level,
                root_causes=root_causes,
                revenue_impact_estimate=revenue_impact
            )
            await prs.insert()
            
            # If critical or emergency, trigger AI and Coordinator
            ai_data = None
            if risk_level in ["Critical", "Emergency"] or pred_data["probability_of_shortage"] > 0.7:
                logger.info(f"Critical shortage predicted for {ps.sku}. Running AI analysis...")
                
                # Alert
                alert = ShortageAlert(
                    alert_id=f"ALT-{random.randint(1000,9999)}",
                    product_id=ps.product_id,
                    sku=ps.sku,
                    title=f"{risk_level} Shortage Imminent",
                    message=f"Probability: {pred_data['probability_of_shortage']*100}%. Days remaining: {pred_data['days_remaining']}",
                    severity=risk_level
                )
                await alert.insert()
                
                # AI
                ai_result = await shortage_ai_engine.analyze_shortage(
                    product_id=ps.product_id,
                    sku=ps.sku,
                    probability=pred_data["probability_of_shortage"],
                    days_remaining=pred_data["days_remaining"],
                    root_causes=root_causes,
                    risk_classification=risk_level,
                    revenue_impact=revenue_impact
                )
                
                ai_analysis = ShortageAIAnalysis(
                    analysis_id=f"AI-{random.randint(1000,9999)}",
                    product_id=ps.product_id,
                    sku=ps.sku,
                    **ai_result
                )
                await ai_analysis.insert()
                ai_data = ai_analysis.dict()
                
                # Recommendation
                for action in ai_result.get("recommended_actions", []):
                    rec = ShortageRecommendation(
                        recommendation_id=f"REC-{random.randint(1000,9999)}",
                        product_id=ps.product_id,
                        sku=ps.sku,
                        action_type="Recovery Action",
                        reason=ai_result.get("root_cause", "Mitigate shortage"),
                        priority="High",
                        expected_impact=ai_result.get("business_explanation", ""),
                        confidence=ai_result.get("confidence_score", 0.8)
                    )
                    await rec.insert()
                    
                # Coordinator Escalation
                coord_payload = {
                    "agent": "Product Shortage Prediction Agent",
                    "finding": f"Severe product shortage predicted for {ps.sku}. Risk: {risk_level}.",
                    "severity": risk_level,
                    "confidence": ai_result.get("confidence_score", 0.9),
                    "recommendations": ai_result.get("recommended_actions", []),
                    "metadata": {
                        "product_id": ps.product_id,
                        "sku": ps.sku,
                        "probability": pred_data["probability_of_shortage"],
                        "days_remaining": pred_data["days_remaining"],
                        "revenue_impact": revenue_impact
                    },
                    "contributing_evidence": root_causes
                }
                
                coord_msg = CoordinatorMessage(
                    message_id=f"msg_shortage_{ps.sku}_{int(datetime.now().timestamp())}",
                    direction="outbound",
                    payload=coord_payload,
                    status="Pending"
                )
                await coord_msg.insert()
                
                results.append({
                    "sku": ps.sku,
                    "risk_level": risk_level,
                    "finding": coord_payload["finding"],
                    "recommendations": ai_result.get("recommended_actions", [])
                })

            # Broadcast
            await manager.broadcast(json.dumps({
                "type": "SHORTAGE_UPDATE",
                "data": {
                    "sku": ps.sku,
                    "risk_level": risk_level,
                    "probability": pred_data["probability_of_shortage"],
                    "ai_analysis": ai_data
                }
            }))
            
        logger.info(f"Shortage monitor completed successfully. Analyzed {len(products)} products.")
        return results
        
    except Exception as e:
        logger.error(f"Shortage monitor failed: {e}")
        return []
