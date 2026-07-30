import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
settings.MONGODB_URI = 'mongodb://localhost:27017/abcc_db'
from core.database import init_db
from workflows.inventory_monitor import run_inventory_monitor

async def main():
    await init_db()
    await run_inventory_monitor()
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
