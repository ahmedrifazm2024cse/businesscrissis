from repositories.domain_repos import agent_memory_repo, conversation_history_repo
from typing import Any, List, Dict
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    async def save_memory(self, agent_name: str, key: str, value: Any):
        logger.info(f"Saving memory for {agent_name}: {key}")
        # Check if exists
        existing = await agent_memory_repo.get_by_field("memory_key", key)
        if existing and existing.agent_name == agent_name:
            await agent_memory_repo.update(existing, {"memory_value": value})
        else:
            await agent_memory_repo.create({
                "agent_name": agent_name,
                "memory_key": key,
                "memory_value": value
            })

    async def get_memory(self, agent_name: str, key: str) -> Any:
        # For simplicity, we just filter locally or we can use get_multi_by_query
        memories = await agent_memory_repo.get_multi_by_query({
            "agent_name": agent_name,
            "memory_key": key
        })
        if memories:
            return memories[0].memory_value
        return None

    async def log_conversation(self, session_id: str, role: str, content: str):
        await conversation_history_repo.create({
            "session_id": session_id,
            "role": role,
            "content": content
        })

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        history = await conversation_history_repo.get_multi_by_query(
            {"session_id": session_id}
        )
        return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in history]

memory_manager = MemoryManager()
