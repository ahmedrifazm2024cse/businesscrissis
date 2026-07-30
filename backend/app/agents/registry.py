import asyncio
import logging
import json
import os
from typing import Dict, Any, Type, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from app.graph.state import GraphState
from app.models.domain import AgentResult
from app.websocket.manager import manager
from app.agents.schemas import (
    CybersecurityOutput, MarketIntelligenceOutput, CustomerReputationOutput,
    OperationsOutput, HROutput, LegalComplianceOutput, FinancialRiskOutput,
    SupplyChainOutput, PredictiveAnalyticsOutput, StrategyOutput,
    ExecutiveDecisionOutput, CommunicationPROutput, ReportGeneratorOutput
)

logger = logging.getLogger(__name__)

# Initialize the LLM
# Assuming GEMINI_API_KEY is in environment or .env
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}. Check GEMINI_API_KEY.")
    llm = None

async def run_llm_agent(agent_name: str, workflow_id: str, prompt_text: str, schema: Type[BaseModel], state: GraphState) -> Dict[str, Any]:
    logger.info(f"[{agent_name}] started for workflow {workflow_id}")
    await manager.broadcast_json({"event": "agent_running", "agent": agent_name, "workflow_id": workflow_id})
    
    output = {}
    if llm is None:
        logger.warning("LLM not initialized. Returning fallback mock data.")
        # Fallback if no LLM
        output = schema.construct().dict()
    else:
        try:
            # Use structured output
            structured_llm = llm.with_structured_output(schema)
            # Create a comprehensive prompt containing state
            incident_desc = state.get("incident_description", "Unknown Incident")
            past_results = state.get("agent_results", {})
            context_str = json.dumps({"incident": incident_desc, "previous_findings": past_results}, indent=2)
            final_prompt = f"You are the {agent_name} for a major enterprise.\n\nContext and shared workflow state:\n{context_str}\n\nTask:\n{prompt_text}\n\nProvide your analysis matching the required output schema exactly."
            
            # Execute LLM (asynchronously if possible, using ainvoke, but ChatGoogleGenerativeAI supports it)
            response = await structured_llm.ainvoke(final_prompt)
            output = response.model_dump()
        except Exception as e:
            logger.error(f"[{agent_name}] LLM execution failed: {e}")
            output = {"error": str(e)}

    # Save result to DB
    agent_res = AgentResult(workflow_id=workflow_id, agent_name=agent_name, output=output)
    await agent_res.insert()
    
    await manager.broadcast_json({"event": "agent_completed", "agent": agent_name, "workflow_id": workflow_id, "output": output})
    logger.info(f"[{agent_name}] completed for workflow {workflow_id}")
    return output

# --- Level 1 Agents (Parallel) ---

async def cybersecurity_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Analyze the incident for cybersecurity threats, affected assets, and recommend containment steps."
    res = await run_llm_agent("Cybersecurity", state["workflow_id"], prompt, CybersecurityOutput, state)
    return {"cybersecurity": res}

async def market_intelligence_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Analyze market intelligence, competitor activity, and business opportunities based on the incident."
    res = await run_llm_agent("Market Intelligence", state["workflow_id"], prompt, MarketIntelligenceOutput, state)
    return {"market_intelligence": res}

async def customer_reputation_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Evaluate customer sentiment, satisfaction, and brand health given the current incident."
    res = await run_llm_agent("Customer Reputation", state["workflow_id"], prompt, CustomerReputationOutput, state)
    return {"customer_reputation": res}

async def operations_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Assess operational health, potential bottlenecks, and estimate downtime."
    res = await run_llm_agent("Operations", state["workflow_id"], prompt, OperationsOutput, state)
    return {"operations": res}

async def hr_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Evaluate workforce impact, morale, and employee risk."
    res = await run_llm_agent("HR", state["workflow_id"], prompt, HROutput, state)
    return {"hr": res}

# --- Level 2 Agents (Dependent) ---

async def legal_compliance_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Analyze the incident and level 1 agent findings for legal risks and compliance violations."
    res = await run_llm_agent("Legal & Compliance", state["workflow_id"], prompt, LegalComplianceOutput, state)
    return {"legal_compliance": res}

async def financial_risk_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Calculate projected financial losses and overall financial risk based on the current incident and agent reports."
    res = await run_llm_agent("Financial Risk", state["workflow_id"], prompt, FinancialRiskOutput, state)
    return {"financial_risk": res}

async def supply_chain_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Determine supply chain risk, affected vendors, and inventory health."
    res = await run_llm_agent("Supply Chain", state["workflow_id"], prompt, SupplyChainOutput, state)
    return {"supply_chain": res}

# --- Level 3 Agents ---

async def predictive_analytics_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Predict future escalations, probabilities, and risks using all gathered intelligence."
    res = await run_llm_agent("Predictive Analytics", state["workflow_id"], prompt, PredictiveAnalyticsOutput, state)
    return {"predictive_analytics": res}

# --- Level 4 Agents ---

async def strategy_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Develop a high-level strategic action plan and priority matrix to resolve the crisis."
    res = await run_llm_agent("Strategy", state["workflow_id"], prompt, StrategyOutput, state)
    return {"strategy": res}

# --- Level 5 Agents ---

async def executive_decision_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Act as the CEO/Board. Synthesize all agent outputs, determine the final executive decision, and state priority and confidence."
    res = await run_llm_agent("Executive Decision", state["workflow_id"], prompt, ExecutiveDecisionOutput, state)
    return {"executive_decision": res}

from app.models.domain import AgentResult, Report

# --- Level 6 Agents ---

async def communication_pr_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Draft public relations and internal communications based on the executive decision."
    res = await run_llm_agent("Communication & PR", state["workflow_id"], prompt, CommunicationPROutput, state)
    return {"communication_pr": res}

async def generate_report_agent(state: GraphState) -> Dict[str, Any]:
    prompt = "Format a final status summary. Return a report generation status."
    res = await run_llm_agent("Report Generator", state["workflow_id"], prompt, ReportGeneratorOutput, state)
    
    # Save an actual Report document to MongoDB
    incident_desc = state.get("incident_description", "Unknown Incident")
    title = f"Post-Incident Report: {incident_desc[:30]}..."
    
    report = Report(
        workflow_id=state["workflow_id"],
        title=title,
        content=str(state.get("executive_decision", "No executive decision made.")) + f"\n\nDetails: {res}",
        generated_by="Report Generator LLM"
    )
    await report.insert()
    
    await manager.broadcast_json({"event": "report_generated", "workflow_id": state["workflow_id"]})
    return {"report": res}
