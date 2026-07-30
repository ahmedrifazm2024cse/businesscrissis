import logging
import os
from typing import Dict, Any
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class SharedMemory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedMemory, cls).__new__(cls)
        return cls._instance

    def initialize_workflow(self, workflow_id: str):
        """Create a document for a new workflow if it does not already exist."""
        if collection.find_one({"workflow_id": workflow_id}) is None:
            collection.insert_one({"workflow_id": workflow_id, "data": {}})
            logger.info(f"Initialized shared memory document for workflow {workflow_id}")

    def write(self, workflow_id: str, key: str, value: Any):
        """Upsert a single key/value pair into the workflow document."""
        self.initialize_workflow(workflow_id)
        result = collection.update_one(
            {"workflow_id": workflow_id},
            {"$set": {f"data.{key}": value}},
            upsert=True,
        )
        logger.debug(f"Memory write: {workflow_id}[{key}] = {value} (matched {result.matched_count})")

    def read(self, workflow_id: str, key: str) -> Any:
        """Read a single key from the workflow document."""
        doc = collection.find_one({"workflow_id": workflow_id}, {"data": 1})
        if doc and "data" in doc:
            return doc["data"].get(key)
        return None

    def read_all(self, workflow_id: str) -> Dict[str, Any]:
        """Return the full key/value map for a workflow."""
        doc = collection.find_one({"workflow_id": workflow_id}, {"data": 1})
        return doc.get("data", {}) if doc else {}

    def clear(self, workflow_id: str):
        """Delete the workflow document entirely."""
        result = collection.delete_one({"workflow_id": workflow_id})
        if result.deleted_count:
            logger.info(f"Cleared shared memory for workflow {workflow_id}")

# Export singleton used throughout the codebase
memory = SharedMemory()
