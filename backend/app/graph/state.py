from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    workflow_id: str
    incident_description: str
    selected_agents: List[str]
    agent_results: Dict[str, Any]
    executive_decision: Optional[str]
    error: Optional[str]
    status: str
