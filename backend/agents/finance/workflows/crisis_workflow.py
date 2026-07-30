import logging
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, START, END
from agents.core_agents import (
    InventoryIntelligenceAgent,
    DemandForecastingAgent,
    SupplierIntelligenceAgent,
    ShipmentIntelligenceAgent,
    ShortagePredictionAgent,
    BusinessCrisisImpactAgent,
    RecommendationAI
)
from repositories.domain_repos import (
    inventory_repo, supplier_repo, shipment_repo
)

logger = logging.getLogger(__name__)

# Define the State
class SupplyChainState(TypedDict):
    # Inputs
    trigger_event: str
    
    # Internal state
    inventory_analysis: Dict[str, Any]
    demand_forecast: Dict[str, Any]
    supplier_analysis: Dict[str, Any]
    shipment_analysis: Dict[str, Any]
    
    shortage_predictions: Dict[str, Any]
    crisis_impact: Dict[str, Any]
    recommendations: Dict[str, Any]
    
    # Output to Coordinator
    coordinator_payload: Dict[str, Any]

async def analyze_inventory_node(state: SupplyChainState):
    logger.info("Running Inventory Analysis")
    agent = InventoryIntelligenceAgent()
    # In a real scenario, we'd fetch actual DB records here
    # For now, we simulate fetching recent records
    # inventory = await inventory_repo.get_multi(limit=50)
    # mock data for testing flow without db seeded
    inventory_data = [{"product_id": "P1", "quantity": 100, "status": "Low Stock"}]
    result = await agent.analyze(inventory_data)
    return {"inventory_analysis": result}

async def forecast_demand_node(state: SupplyChainState):
    logger.info("Running Demand Forecasting")
    agent = DemandForecastingAgent()
    hist_data = [{"product_id": "P1", "date": "2024-01-01", "sales": 10}]
    result = await agent.forecast(hist_data)
    return {"demand_forecast": result}

async def analyze_suppliers_node(state: SupplyChainState):
    logger.info("Running Supplier Analysis")
    agent = SupplierIntelligenceAgent()
    sup_data = [{"supplier_id": "S1", "reliability": 0.8}]
    news = {"query": "S1 Country", "articles": []}
    result = await agent.evaluate(sup_data, news)
    return {"supplier_analysis": result}

async def analyze_shipments_node(state: SupplyChainState):
    logger.info("Running Shipment Analysis")
    agent = ShipmentIntelligenceAgent()
    ship_data = [{"shipment_id": "SH1", "status": "In Transit"}]
    weather = {"status": "Storm"}
    result = await agent.analyze_shipments(ship_data, weather)
    return {"shipment_analysis": result}

async def predict_shortages_node(state: SupplyChainState):
    logger.info("Running Shortage Prediction")
    agent = ShortagePredictionAgent()
    result = await agent.predict(
        state.get("inventory_analysis", {}),
        state.get("shipment_analysis", {}),
        state.get("demand_forecast", {})
    )
    return {"shortage_predictions": result}

async def assess_crisis_node(state: SupplyChainState):
    logger.info("Assessing Business Crisis Impact")
    agent = BusinessCrisisImpactAgent()
    result = await agent.estimate_impact(
        state.get("shortage_predictions", {}),
        state.get("supplier_analysis", {}) # using as risk scores proxy
    )
    return {"crisis_impact": result}

async def generate_recommendations_node(state: SupplyChainState):
    logger.info("Generating Recommendations")
    agent = RecommendationAI()
    result = await agent.generate_recommendations(
        state.get("crisis_impact", {}),
        state.get("shortage_predictions", {})
    )
    return {"recommendations": result}

async def prepare_coordinator_payload_node(state: SupplyChainState):
    logger.info("Preparing Coordinator Output")
    # Format per user requirement
    payload = {
        "agent": "Supply Chain Agent",
        "finding": state.get("crisis_impact", {}).get("crisis_summary", "No crisis identified."),
        "confidence": 0.95, # In real app, aggregate confidences
        "severity": state.get("crisis_impact", {}).get("customer_impact_level", "Low"),
        "recommendations": state.get("recommendations", {}).get("recommendations", []),
        "metadata": {
            "trigger": state.get("trigger_event"),
            "revenue_loss_estimate": state.get("crisis_impact", {}).get("revenue_loss_estimate", 0)
        },
        "contributing_evidence": [
            state.get("shortage_predictions", {}),
            state.get("supplier_analysis", {})
        ]
    }
    return {"coordinator_payload": payload}


def build_graph():
    builder = StateGraph(SupplyChainState)
    
    # Add nodes
    builder.add_node("analyze_inventory", analyze_inventory_node)
    builder.add_node("forecast_demand", forecast_demand_node)
    builder.add_node("analyze_suppliers", analyze_suppliers_node)
    builder.add_node("analyze_shipments", analyze_shipments_node)
    
    builder.add_node("predict_shortages", predict_shortages_node)
    builder.add_node("assess_crisis", assess_crisis_node)
    builder.add_node("generate_recommendations", generate_recommendations_node)
    builder.add_node("prepare_payload", prepare_coordinator_payload_node)
    
    # Connect nodes in a sequential/parallel workflow
    builder.add_edge(START, "analyze_inventory")
    builder.add_edge(START, "forecast_demand")
    builder.add_edge(START, "analyze_suppliers")
    builder.add_edge(START, "analyze_shipments")
    
    # Wait for the first layer to finish before predicting shortages
    builder.add_edge("analyze_inventory", "predict_shortages")
    builder.add_edge("forecast_demand", "predict_shortages")
    builder.add_edge("analyze_shipments", "predict_shortages")
    
    # Assess crisis using shortages and supplier risk
    builder.add_edge("predict_shortages", "assess_crisis")
    builder.add_edge("analyze_suppliers", "assess_crisis")
    
    # Finally, recommendations and payload preparation
    builder.add_edge("assess_crisis", "generate_recommendations")
    builder.add_edge("generate_recommendations", "prepare_payload")
    builder.add_edge("prepare_payload", END)
    
    return builder.compile()

# Instantiated graph for execution
crisis_graph = build_graph()
