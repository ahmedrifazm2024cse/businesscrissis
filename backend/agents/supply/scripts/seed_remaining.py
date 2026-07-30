import asyncio
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.database import init_db

import models.cost_intelligence as ci
import models.warehouse_intelligence as wi
import models.route_intelligence as ri
import models.procurement_intelligence as pi
import models.shipment_intelligence as si
import models.shortage_intelligence as sh

def utc_now():
    return datetime.now(timezone.utc)

def generate_fake_data(field_type, field_name=""):
    try:
        # Resolve Optional types
        origin = getattr(field_type, '__origin__', None)
        if origin is not None and str(origin) == 'typing.Union':
            field_type = getattr(field_type, '__args__', [str])[0]
            origin = getattr(field_type, '__origin__', None)
        
        if field_type == str:
            if "id" in field_name.lower():
                return f"ID-{random.randint(1000, 9999)}"
            return f"Mock {field_name} {random.randint(1, 100)}"
        if field_type == int:
            return random.randint(10, 1000)
        if field_type == float:
            return random.uniform(0.0, 100.0)
        if field_type == bool:
            return random.choice([True, False])
        if field_type == datetime:
            return utc_now() - timedelta(days=random.randint(0, 30))
        if origin == list or origin == List:
            inner_type = getattr(field_type, '__args__', [str])[0]
            return [generate_fake_data(inner_type) for _ in range(3)]
        if origin == dict or origin == Dict:
            return {"Zone A": random.uniform(0, 100), "Zone B": random.uniform(0, 100)}
    except Exception:
        pass
    return "Unknown"

async def seed_module(module):
    print(f"Seeding models in {module.__name__}...")
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and hasattr(attr, "Settings") and hasattr(attr, "insert_many"):
            print(f"  -> Seeding {attr_name}")
            try:
                await attr.delete_all()
                docs = []
                for i in range(15): # 15 records per model
                    kwargs = {}
                    # Pydantic v1 vs v2 compatibility
                    fields = getattr(attr, '__fields__', getattr(attr, 'model_fields', {}))
                    for field_name, model_field in fields.items():
                        if field_name == "id" or field_name == "_id" or field_name == "revision_id": continue
                        
                        ftype = getattr(model_field, 'type_', getattr(model_field, 'annotation', str))
                        
                        val = generate_fake_data(ftype, field_name)
                        kwargs[field_name] = val
                    docs.append(attr(**kwargs))
                await attr.insert_many(docs)
            except Exception as e:
                print(f"    Failed to seed {attr_name}: {e}")

async def main():
    settings.MONGODB_URI = 'mongodb://localhost:27017/abcc_db'
    await init_db()
    
    modules_to_seed = [ci, wi, ri, pi, si, sh]
    for m in modules_to_seed:
        await seed_module(m)
        
    print("Generic seeding complete.")

if __name__ == '__main__':
    asyncio.run(main())
