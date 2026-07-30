from fastapi import APIRouter

import sys, os
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

router = APIRouter()

AgentverseWrapper(router).register(
    agent_name=AGENT_NAME,
    port=PORT,
    capabilities=CAPABILITIES,
    dependencies=[],
    legacy_handler=decision_logic
)
