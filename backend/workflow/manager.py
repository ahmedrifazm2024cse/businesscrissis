import os
import json
import logging
import asyncio
from typing import Dict, Any, List

from backend.shared.memory import memory
from backend.shared.eventbus import eventbus
from backend.database.models import WorkflowHistory

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangChain not found. Synthetic data generation will be limited.")

logger = logging.getLogger(__name__)

# Define the 13 Agents with their specific business personas for realistic synthetic generation
AGENT_PERSONAS = {
    # Business Agents
    "customer": "You are the Customer Reputation Agent. Analyze how the crisis impacts customer sentiment, brand trust, and reviews. Generate highly realistic synthetic data (e.g. sentiment dropped by X%, specific complaints on social media). Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "market": "You are the Market Intelligence Agent. Analyze how the crisis affects market share, competitor movements, and industry trends. Use realistic synthetic data. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "finance": "You are the Financial Agent. Analyze revenue loss, stock impact, and budget requirements based on the crisis. Use realistic synthetic data (e.g., $1.2M daily burn rate). Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "supply": "You are the Supply Chain Agent. Analyze vendor delays, logistics failures, and inventory impacts. Generate realistic synthetic data. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "cyber": "You are the Cyber Security Agent. Analyze network breaches, data exfiltration, or vulnerability exploitation. Generate realistic synthetic data (e.g., specific CVEs or compromised partitions). Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "legal": "You are the Legal Compliance Agent. Analyze regulatory violations (e.g. GDPR, SLAs) and legal liability. Generate realistic synthetic data. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    
    # Executive Agents
    "decision": "You are the Executive Decision Agent. Synthesize all previous agent findings into a cohesive corporate strategy. Generate a realistic executive strategy. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "communication": "You are the Communication & PR Agent. Create a CEO Statement, a Customer Email, and an Internal Memo based on the crisis and decisions. Return ONLY a JSON object with 'findings' (list containing the assets) and 'recommendations' (list).",
    "resource": "You are the Resource Allocation Agent. Reallocate budgets and personnel based on the financial and supply chain impacts. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "notification": "You are the Notification Agent. Generate a list of critical stakeholders who must be immediately alerted based on the crisis severity. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list).",
    "report": "You are the Report Generation Agent. Compile a comprehensive Markdown report summarizing the entire crisis resolution workflow. Return ONLY a JSON object with 'findings' (list containing the markdown string) and 'recommendations' (list).",
    "knowledge": "You are the Knowledge Manager Agent. Extract key learnings and playbook updates from this crisis to store in the corporate database. Return ONLY a JSON object with 'findings' (list) and 'recommendations' (list)."
}

class WorkflowManager:
    def __init__(self):
        os.environ["MEMORY_URL"] = "http://localhost:8000/api/commander/status"
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and LLM_AVAILABLE:
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=self.api_key, temperature=0.2)
        else:
            self.llm = None
            logger.warning("No LLM initialized. Agents will use fallback deterministic logic.")

    async def invoke_agent(self, workflow_id: str, agent_id: str, crisis_desc: str, shared_state: dict) -> dict:
        """Dynamically invokes a real LangChain agent to generate realistic synthetic business data."""
        await eventbus.publish("agent_started", {"workflow_id": workflow_id, "agent": agent_id})
        memory.write(workflow_id, "status", f"executing_{agent_id}_agent")
        
        if not self.llm:
            await asyncio.sleep(0.5)
            await eventbus.publish("agent_completed", {"workflow_id": workflow_id, "agent": agent_id})
            return {"findings": [f"{agent_id.capitalize()} fallback data."], "recommendations": ["Fallback strategy."]}

        try:
            # Build Context from previous agents
            context_str = json.dumps({k: v for k, v in shared_state.items() if "_analysis" in k or k == "decision"}, indent=2)
            
            prompt = f"""Crisis: {crisis_desc}
Shared Memory Context:
{context_str}

Analyze the crisis given the above context.
Ensure your output is strictly valid JSON with no markdown block formatting.
Format: {{"findings": ["string"], "recommendations": ["string"]}}"""

            messages = [
                SystemMessage(content=AGENT_PERSONAS.get(agent_id, "You are a business agent.")),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Clean JSON response
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            await eventbus.publish("agent_completed", {"workflow_id": workflow_id, "agent": agent_id})
            return data
        except Exception as e:
            logger.error(f"{agent_id} Agent execution failed: {e}")
            await eventbus.publish("agent_failed", {"workflow_id": workflow_id, "agent": agent_id, "error": str(e)})
            return {"findings": [f"Execution failed: {str(e)}"], "recommendations": ["Manual intervention required."]}

    async def analyze_crisis_and_plan(self, description: str) -> list[str]:
        """Intelligent LLM Orchestrator to determine the DAG workflow."""
        if not self.llm:
            return ["customer", "market", "finance", "supply", "cyber", "legal"]
            
        try:
            prompt = f"""Crisis: {description}
Available Business Agents: 'customer', 'market', 'finance', 'supply', 'cyber', 'legal'.
Identify exactly which of these agents are strictly necessary to handle this crisis.
Return ONLY a JSON array of strings containing the necessary agent IDs. Do not include markdown formatting.
Example: ["cyber", "legal"]"""
            
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = res.content.replace("```json", "").replace("```", "").strip()
            plan = json.loads(content)
            
            # Filter to ensure only valid business agents are included
            valid_agents = {"customer", "market", "finance", "supply", "cyber", "legal"}
            plan = [a for a in plan if a in valid_agents]
            
            if not plan:
                plan = list(valid_agents)
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return ["customer", "market", "finance", "supply", "cyber", "legal"]
        
    async def execute_workflow(self, workflow_id: str, crisis_description: str):
        logger.info(f"[{workflow_id}] Executive Commander initiating workflow.")
        await eventbus.publish("workflow_started", {"workflow_id": workflow_id})
        
        # Step 4: Executive Commander dynamically generates workflow
        business_plan = await self.analyze_crisis_and_plan(crisis_description)
        memory.write(workflow_id, "execution_plan", business_plan)
        
        # Step 5 & 6: Execute Business Agents dynamically (Parallel Execution for speed)
        tasks = []
        for agent in business_plan:
            await eventbus.publish("agent_assigned", {"workflow_id": workflow_id, "agent": agent})
            state = memory.read_all(workflow_id)
            task = asyncio.create_task(self.invoke_agent(workflow_id, agent, crisis_description, state))
            tasks.append((agent, task))
            
        for agent, task in tasks:
            result = await task
            # Step 8: Agents write findings to Shared Memory
            memory.write(workflow_id, f"{agent}_analysis", result.get("findings", [])[0] if result.get("findings") else "Analyzed.")
            memory.write(workflow_id, f"{agent}_recommendations", result.get("recommendations", []))

        # Step 10: Executive Decision Agent
        state = memory.read_all(workflow_id)
        decision_res = await self.invoke_agent(workflow_id, "decision", crisis_description, state)
        memory.write(workflow_id, "decision", " | ".join(decision_res.get("recommendations", [])))

        # Step 11: Execute Remaining Executive Agents sequentially based on the decision
        exec_agents = ["resource", "communication", "notification", "report", "knowledge"]
        for agent in exec_agents:
            state = memory.read_all(workflow_id)
            res = await self.invoke_agent(workflow_id, agent, crisis_description, state)
            memory.write(workflow_id, f"{agent}_analysis", res.get("findings", [])[0] if res.get("findings") else "Processed.")

        memory.write(workflow_id, "status", "completed")
        await eventbus.publish("workflow_completed", {"workflow_id": workflow_id})
        
        # Persist to MongoDB
        try:
            state = memory.read_all(workflow_id)
            history = WorkflowHistory(
                workflow_id=workflow_id,
                crisis_description=crisis_description,
                severity="CRITICAL",
                status="completed",
                executed_agents=business_plan + exec_agents + ["decision"],
                agent_outputs={k: v for k, v in state.items() if "_analysis" in k},
                executive_decision=state.get("decision")
            )
            await history.insert()
            logger.info(f"[{workflow_id}] Saved to MongoDB WorkflowHistory.")
        except Exception as e:
            logger.error(f"Failed to persist WorkflowHistory: {e}")
            
        logger.info(f"[{workflow_id}] Workflow completed successfully.")
