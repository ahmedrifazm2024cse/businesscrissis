import asyncio
import httpx
import logging
import socket
import os

logger = logging.getLogger("agent_adapter")

class LifecycleManager:
    def __init__(self, agent_name: str, port: int, capabilities: list = None, dependencies: list = None, commander_url: str = None):
        self.agent_name = agent_name
        self.port = port
        self.capabilities = capabilities or []
        self.dependencies = dependencies or []
        self.commander_url = commander_url or os.getenv("COMMANDER_URL", "http://localhost:8000")
        self.is_running = False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    async def register(self):
        """Register the agent with the Commander on startup."""
        ip = self.get_local_ip()
        payload = {
            "name": self.agent_name,
            "capabilities": self.capabilities,
            "status": "online",
            "health": "healthy",
            "version": "1.0.0",
            "endpoint": f"http://{ip}:{self.port}",
            "priority": 1,
            "dependencies": self.dependencies
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(f"{self.commander_url}/api/register", json=payload)
                resp.raise_for_status()
                logger.info(f"[{self.agent_name}] Registered with Commander successfully.")
        except Exception as e:
            logger.warning(f"Failed to register with Commander: {e}")

    async def start_heartbeat(self):
        """Starts a background loop sending heartbeats every 30 seconds."""
        self.is_running = True
        while self.is_running:
            try:
                # The commander pings the agent's /health endpoint automatically,
                # but we can optionally push heartbeats.
                pass
            except Exception:
                pass
            await asyncio.sleep(30)

    def stop(self):
        self.is_running = False
