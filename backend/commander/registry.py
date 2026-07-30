from typing import List, Dict, Optional
from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str
    capabilities: List[str]
    status: str = "online"
    health: str = "healthy"
    version: str = "1.0.0"
    endpoint: str
    priority: int = 1
    dependencies: List[str] = []

class AgentRegistry:
    """Maintains a registry of all active agents and their capabilities."""
    
    def __init__(self):
        self._agents: Dict[str, AgentConfig] = {}

    def register_agent(self, config: AgentConfig):
        self._agents[config.name] = config
        print(f"Registered Agent: {config.name} at {config.endpoint} with capabilities {config.capabilities}")

    async def check_health_all(self) -> Dict[str, str]:
        """Pings all agents to update their health status."""
        import httpx
        import asyncio
        
        async def check_agent(agent: AgentConfig):
            try:
                url = f"{agent.endpoint}/health"
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        agent.health = "online"
                        agent.status = "online"
                    else:
                        agent.health = "offline"
                        agent.status = "offline"
            except Exception:
                agent.health = "offline"
                agent.status = "offline"
                
        await asyncio.gather(*(check_agent(a) for a in self._agents.values()))
        return {name: agent.health for name, agent in self._agents.items()}

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Returns the configuration for a specific agent."""
        return self._agents.get(name)

    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Returns a mapping of agent name to its capabilities."""
        return {name: agent.capabilities for name, agent in self._agents.items()}
