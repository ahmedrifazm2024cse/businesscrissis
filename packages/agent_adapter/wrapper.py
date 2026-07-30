import asyncio
import time
import logging
import traceback
import httpx
from fastapi import FastAPI, Request, BackgroundTasks
from .models import ExecutePayload, StandardResponse, StandardResponseMetadata
from .lifecycle import LifecycleManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_adapter")

import os

EVENT_BUS_URL = os.getenv("EVENT_BUS_URL", "http://localhost:8101/api/eventbus/publish")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")

class AgentverseWrapper:
    def __init__(self, app: FastAPI):
        self.app = app
        self.agent_name = "unknown"
        self.capabilities = []
        self.dependencies = []
        self.lifecycle = None
        self.legacy_handler = None

    def register(self, agent_name: str, port: int, capabilities: list, dependencies: list, legacy_handler):
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.dependencies = dependencies
        self.lifecycle = LifecycleManager(agent_name, port, capabilities, dependencies)
        self.legacy_handler = legacy_handler
        self._inject_endpoints()
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.lifecycle.register()
            asyncio.create_task(self.lifecycle.start_heartbeat())
            
        @self.app.on_event("shutdown")
        async def shutdown_event():
            self.lifecycle.stop()

    async def publish_event(self, event_type: str, workflow_id: str, crisis_id: str, data: dict = None):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                payload = {
                    "event_id": f"evt-{time.time()}",
                    "event_type": event_type,
                    "publisher": self.agent_name,
                    "workflow_id": workflow_id,
                    "crisis_id": crisis_id,
                    "timestamp": time.time(),
                    "data": data or {}
                }
                await client.post(EVENT_BUS_URL, json=payload)
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Failed to publish event {event_type}: {e}")

    async def write_memory(self, crisis_id: str, output: dict):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(f"{MEMORY_URL}/{crisis_id}/append_output", params={"agent_name": self.agent_name}, json=output)
        except Exception as e:
            logger.warning(f"[{self.agent_name}] Failed to write to shared memory: {e}")

    def _inject_endpoints(self):
        @self.app.get("/health")
        def health_check():
            return {"status": "healthy", "version": "1.0.0"}

        @self.app.get("/capabilities")
        def get_capabilities():
            return {
                "agent_name": self.agent_name,
                "capabilities": self.capabilities,
                "accepted_inputs": ["ExecutePayload"]
            }

        @self.app.post("/register")
        async def manual_register():
            await self.lifecycle.register()
            return {"status": "registered"}

        @self.app.get("/status")
        def get_status():
            return {"status": "online", "agent_name": self.agent_name}

        @self.app.post("/execute", response_model=StandardResponse)
        async def execute_crisis(payload: ExecutePayload, background_tasks: BackgroundTasks):
            start_time = time.time()
            logger.info(f"[{self.agent_name}] Incoming Request for Workflow: {payload.workflow_id}")
            
            await self.publish_event("AgentStarted", payload.workflow_id, payload.crisis_id)
            
            try:
                # The legacy_handler must accept payload and return (findings, recommendations, confidence, risk_score)
                # Ensure backward compatibility by mapping ExecutePayload to old dict/format if needed by legacy
                # But we pass the raw payload here. If legacy_handler requires specific old structure, it handles it inside.
                findings, recommendations, confidence, risk_score = await self.legacy_handler(payload)
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                resp = StandardResponse(
                    agent_name=self.agent_name,
                    status="success",
                    confidence=confidence,
                    risk_score=risk_score,
                    findings=findings,
                    recommendations=recommendations,
                    data={},
                    metadata=StandardResponseMetadata(
                        execution_time_ms=execution_time_ms,
                        timestamp=str(time.time())
                    )
                )
                
                # Write to shared memory and publish event in background
                background_tasks.add_task(self.write_memory, payload.crisis_id, resp.dict())
                background_tasks.add_task(self.publish_event, "AgentCompleted", payload.workflow_id, payload.crisis_id, {"status": "success"})
                
                logger.info(f"[{self.agent_name}] Outgoing Response: Success ({execution_time_ms}ms)")
                return resp
            
            except Exception as e:
                execution_time_ms = int((time.time() - start_time) * 1000)
                logger.error(f"[{self.agent_name}] Error executing legacy logic: {traceback.format_exc()}")
                
                err_resp = StandardResponse(
                    agent_name=self.agent_name,
                    status="error",
                    confidence=0.0,
                    risk_score=10,
                    findings=[f"Internal Agent Error: {str(e)}"],
                    recommendations=[],
                    data={},
                    metadata=StandardResponseMetadata(
                        execution_time_ms=execution_time_ms,
                        timestamp=str(time.time())
                    )
                )
                
                background_tasks.add_task(self.write_memory, payload.crisis_id, err_resp.dict())
                background_tasks.add_task(self.publish_event, "AgentFailed", payload.workflow_id, payload.crisis_id, {"error": str(e)})
                
                return err_resp
