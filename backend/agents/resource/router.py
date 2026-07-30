from fastapi import APIRouter

import sys
import os
import httpx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from packages.agent_adapter.wrapper import AgentverseWrapper

router = APIRouter()
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")
