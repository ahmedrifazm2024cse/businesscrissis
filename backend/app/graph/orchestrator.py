import logging
import asyncio
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.models.domain import Workflow
from app.websocket.manager import manager

from app.agents.registry import (
    cybersecurity_agent,
    market_intelligence_agent,
    customer_reputation_agent,
    operations_agent,
    hr_agent,
    legal_compliance_agent,
    financial_risk_agent,
    supply_chain_agent,
    predictive_analytics_agent,
    strategy_agent,
    executive_decision_agent,
    communication_pr_agent,
    generate_report_agent
)

logger = logging.getLogger(__name__)

async def analyze_incident(state: GraphState):
    logger.info(f"Orchestrator analyzing incident for {state['workflow_id']}")
    await manager.broadcast_json({"event": "orchestrator_log", "message": "Analyzing incident requirements...", "workflow_id": state["workflow_id"]})
    
    # In a real system, the Orchestrator LLM would decide which agents to run.
    # We select all for this demonstration workflow.
    state["selected_agents"] = [
        "cyber", "market", "customer", "operations", "hr",
        "legal", "finance", "supply",
        "predictive", "strategy", "executive", "comm", "report"
    ]
    state["status"] = "analyzing"
    return state

# Node for Level 1 (Parallel)
async def level_1_agents(state: GraphState):
    logger.info("Starting Level 1 Agents in parallel")
    tasks = [
        cybersecurity_agent(state),
        market_intelligence_agent(state),
        customer_reputation_agent(state),
        operations_agent(state),
        hr_agent(state)
    ]
    results = await asyncio.gather(*tasks)
    for res in results:
        state["agent_results"].update(res)
    return state

# Node for Level 2 (Dependent on Level 1)
async def level_2_agents(state: GraphState):
    logger.info("Starting Level 2 Agents in parallel")
    tasks = [
        legal_compliance_agent(state),
        financial_risk_agent(state),
        supply_chain_agent(state)
    ]
    results = await asyncio.gather(*tasks)
    for res in results:
        state["agent_results"].update(res)
    return state

# Level 3, 4, 5, 6, 7
async def level_3_predictive(state: GraphState):
    res = await predictive_analytics_agent(state)
    state["agent_results"].update(res)
    return state

async def level_4_strategy(state: GraphState):
    res = await strategy_agent(state)
    state["agent_results"].update(res)
    return state

async def level_5_executive(state: GraphState):
    res = await executive_decision_agent(state)
    state["agent_results"].update(res)
    state["executive_decision"] = res["executive_decision"]["final_decision"]
    return state

async def level_6_comm_pr(state: GraphState):
    res = await communication_pr_agent(state)
    state["agent_results"].update(res)
    return state

async def level_7_report(state: GraphState):
    res = await generate_report_agent(state)
    state["agent_results"].update(res)
    return state

# Build Graph
builder = StateGraph(GraphState)

builder.add_node("analyze", analyze_incident)
builder.add_node("level_1", level_1_agents)
builder.add_node("level_2", level_2_agents)
builder.add_node("level_3", level_3_predictive)
builder.add_node("level_4", level_4_strategy)
builder.add_node("level_5", level_5_executive)
builder.add_node("level_6", level_6_comm_pr)
builder.add_node("level_7", level_7_report)

builder.set_entry_point("analyze")

# Sequential flow for levels
builder.add_edge("analyze", "level_1")
builder.add_edge("level_1", "level_2")
builder.add_edge("level_2", "level_3")
builder.add_edge("level_3", "level_4")
builder.add_edge("level_4", "level_5")
builder.add_edge("level_5", "level_6")
builder.add_edge("level_6", "level_7")
builder.add_edge("level_7", END)

orchestrator_graph = builder.compile()

async def run_orchestrator(workflow_id: str, incident_description: str):
    logger.info(f"Starting orchestration for workflow {workflow_id}")
    
    try:
        workflow = await Workflow.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return
            
        workflow.status = "running"
        await workflow.save()
        await manager.broadcast_json({"event": "workflow_started", "workflow_id": workflow_id, "status": workflow.status})
        
        initial_state = GraphState(
            workflow_id=workflow_id,
            incident_description=incident_description,
            selected_agents=[],
            agent_results={},
            executive_decision=None,
            error=None,
            status="started"
        )
        
        # Invoke the graph asynchronously
        final_state = await orchestrator_graph.ainvoke(initial_state)
        
        # Update workflow as completed
        workflow = await Workflow.get(workflow_id)
        if workflow:
            workflow.status = "completed"
            await workflow.save()
            await manager.broadcast_json({"event": "workflow_completed", "workflow_id": workflow_id, "status": "completed"})
            
        logger.info(f"Orchestration completed for workflow {workflow_id}")
        
    except Exception as e:
        logger.error(f"Error in orchestrator for workflow {workflow_id}: {e}")
        workflow = await Workflow.get(workflow_id)
        if workflow:
            workflow.status = "failed"
            await workflow.save()
            await manager.broadcast_json({"event": "workflow_failed", "workflow_id": workflow_id, "status": "failed"})
