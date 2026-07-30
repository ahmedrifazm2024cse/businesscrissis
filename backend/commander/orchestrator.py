import asyncio
import httpx
import json
import time
import os
from typing import List, Dict, Any
from models import CrisisRequest, ExecutiveSummary, CommanderResponse, AgentResponse, AgentResponseMetadata
from context import SharedContextManager
from registry import AgentRegistry, AgentConfig

try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
except ImportError:
    client = None

import asyncio
import httpx
import json
import time
import os
from typing import List, Dict, Any
from models import CrisisRequest, ExecutiveSummary, CommanderResponse, AgentResponse, AgentResponseMetadata
from registry import AgentRegistry, AgentConfig

WORKFLOW_URL = os.getenv("WORKFLOW_URL", "http://localhost:8103/api/workflow/initiate")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
EVENT_BUS_URL = os.getenv("EVENT_BUS_URL", "http://localhost:8009/api/eventbus/publish")

class TaskScheduler:
    """Executes the plan by calling agent APIs concurrently or sequentially based on DAG."""
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    async def execute_plan(self, workflow: dict, crisis: CrisisRequest) -> None:
        """Executes tasks following dependencies."""
        tasks_data = workflow.get("tasks", [])
        completed = set()
        pending = {t["task_id"]: t for t in tasks_data}

        while pending:
            ready = []
            for tid, t in pending.items():
                if all(dep in completed for dep in t.get("dependencies", [])):
                    ready.append(t)
            
            if not ready:
                print("Workflow stuck due to unresolved dependencies or errors.")
                break

            coroutines = [self._call_agent(task, crisis, workflow["workflow_id"]) for task in ready]
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for task, result in zip(ready, results):
                completed.add(task["task_id"])
                del pending[task["task_id"]]
                
    async def _call_agent(self, task: dict, crisis: CrisisRequest, workflow_id: str):
        agent_name = task["assigned_agent"]
        agent = self.registry.get_agent(agent_name)
        if not agent or agent.health != "online":
            print(f"Agent {agent_name} unavailable. Skipping.")
            return

        payload = {
            "workflow_id": workflow_id,
            "crisis_id": crisis.crisis_id,
            "description": crisis.description,
            "severity": crisis.severity,
            "context": {} # In a real implementation, we'd fetch snapshot from memory
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                await client.post(f"{agent.endpoint}/execute", json=payload)
        except Exception as e:
            print(f"Failed to execute agent {agent_name}: {e}")

class ExecutiveDecisionEngine:
    async def generate_executive_report(self, crisis_id: str) -> ExecutiveSummary:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{MEMORY_URL}/{crisis_id}")
                memory_data = resp.json() if resp.status_code == 200 else {}
        except:
            memory_data = {}

        return ExecutiveSummary(
            executive_summary="System processed crisis autonomously using available agents.",
            business_impact="Evaluated based on dynamic workflow outputs.",
            financial_impact="Aggregated in Shared Memory.",
            operational_impact="Ongoing mitigation.",
            legal_risk="Under review.",
            cyber_risk="Assessed dynamically.",
            reputation_risk="Monitored.",
            priority_score=9,
            recommended_actions=["Review comprehensive dashboard", "Implement immediate containment"],
            short_term_plan="Execute agent recommendations",
            long_term_strategy="System resilience enhancement"
        )

class Orchestrator:
    def __init__(self):
        self.registry = AgentRegistry()
        self.scheduler = TaskScheduler(self.registry)
        self.decision_engine = ExecutiveDecisionEngine()

    async def _publish_event(self, event_type: str, data: dict):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(EVENT_BUS_URL, json={
                    "event_id": f"evt-{time.time()}",
                    "event_type": event_type,
                    "publisher": "Commander",
                    "timestamp": time.time(),
                    "data": data
                })
        except:
            pass

    async def handle_crisis(self, request: CrisisRequest) -> CommanderResponse:
        await self.registry.check_health_all()
        
        # Init Memory
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(f"{MEMORY_URL}/initialize", params={"crisis_id": request.crisis_id, "conversation_id": "auto"})
        except:
            pass

        # Request Workflow Plan
        workflow = {}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(WORKFLOW_URL, params={"crisis_id": request.crisis_id}, json={"description": request.description})
                if resp.status_code == 200:
                    workflow = resp.json()
        except Exception as e:
            print("Failed to get workflow:", e)
            workflow = {"workflow_id": "WF-FAIL", "tasks": []}

        await self._publish_event("WorkflowStarted", {"workflow_id": workflow.get("workflow_id"), "crisis_id": request.crisis_id})
        
        # Execute Workflow
        await self.scheduler.execute_plan(workflow, request)
        
        await self._publish_event("DecisionRequested", {"crisis_id": request.crisis_id})
        
        # Generate Report
        report = await self.decision_engine.generate_executive_report(request.crisis_id)
        
        await self._publish_event("WorkflowCompleted", {"workflow_id": workflow.get("workflow_id"), "crisis_id": request.crisis_id})
        
        return CommanderResponse(
            crisis_id=request.crisis_id,
            global_status="completed",
            executive_report=report,
            agent_responses={} # Agents now write directly to memory
        )
