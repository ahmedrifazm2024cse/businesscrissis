from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch
import asyncio

async def setup_test_db(document_models):
    client = AsyncMongoMockClient()
    
    # Patch list_collection_names on the client database instance itself
    original_lcn = client.abcc_test_db.list_collection_names
    async def mocked_lcn(*args, **kwargs):
        kwargs.pop('authorizedCollections', None)
        kwargs.pop('nameOnly', None)
        return await original_lcn(*args, **kwargs)
        
    # We must patch the class method because Beanie might call it on the class or a new instance
    with patch('mongomock_motor.AsyncMongoMockDatabase.list_collection_names', side_effect=mocked_lcn):
        await init_beanie(database=client.abcc_test_db, document_models=document_models)
    
    return client
