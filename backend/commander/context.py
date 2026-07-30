from typing import Dict, Any, List
from models import AgentResponse

class SharedContextManager:
    """Maintains a shared JSON context for all agents during a crisis."""
    
    def __init__(self):
        self._context: Dict[str, Any] = {}
        self._agent_outputs: Dict[str, AgentResponse] = {}

    def initialize_crisis(self, crisis_id: str, initial_data: Dict[str, Any]) -> None:
        """Sets up the initial shared context."""
        self._context = {
            "crisis_id": crisis_id,
            "global_parameters": initial_data,
            "agent_outputs": {}
        }
        self._agent_outputs = {}

    def append_agent_findings(self, agent_name: str, response: AgentResponse) -> None:
        """
        Appends an agent's findings to the shared context.
        NEVER overwrites previous agent outputs.
        """
        if agent_name in self._agent_outputs:
            raise ValueError(f"Agent {agent_name} has already appended findings. Overwriting is strictly prohibited.")
        self._agent_outputs[agent_name] = response
        self._context["agent_outputs"][agent_name] = response.model_dump()

    def get_context_snapshot(self) -> Dict[str, Any]:
        """Returns the current state of the shared context for the next agent to read."""
        import copy
        return copy.deepcopy(self._context)
