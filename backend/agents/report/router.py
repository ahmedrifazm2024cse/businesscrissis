from fastapi import APIRouter

import sys
import os
import httpx
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

router = APIRouter()

try:
    AgentverseWrapper(router).register(
        agent_name=AGENT_NAME,
        port=PORT,
        capabilities=CAPABILITIES,
        dependencies=[],
        legacy_handler=report_logic
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")
