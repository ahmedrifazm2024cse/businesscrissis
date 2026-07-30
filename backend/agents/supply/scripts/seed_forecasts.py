import asyncio
import os
import sys
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.database import init_db
from models.domain import Inventory
from models.forecast import ForecastResult, ForecastHistory

def utc_now():
    return datetime.now(timezone.utc)

async def main():
    settings.MONGODB_URI = 'mongodb://localhost:27017/abcc_db'
    await init_db()
    
    print('Seeding ForecastResults...')
    await ForecastResult.delete_all()
    await ForecastHistory.delete_all()
    
    inventories = await Inventory.find_all().to_list()
    if not inventories:
        print('No inventory found. Seed database first.')
        return
        
    forecasts = []
    histories = []
    
    algorithms = ['LinearRegression', 'ARIMA', 'ExponentialSmoothing', 'Prophet', 'LSTM']
    trends = ['Increasing', 'Stable', 'Decreasing', 'Sudden Spike', 'Sudden Drop']
    
    for item in inventories:
        base_demand = random.uniform(10, 100)
        for i in range(14):
            hist = ForecastHistory(
                sku=item.sku,
                date=utc_now() - timedelta(days=14-i),
                sales_quantity=max(0, base_demand + random.uniform(-10, 10)),
                inventory_movement=max(0, base_demand + random.uniform(-10, 10))
            )
            histories.append(hist)
            
        trend = random.choices(trends, weights=[30, 40, 10, 15, 5])[0]
        
        forecast = ForecastResult(
            sku=item.sku,
            forecast_type='Weekly',
            target_date=utc_now() + timedelta(days=7),
            forecast_quantity=base_demand * 7 * random.uniform(0.8, 1.5),
            confidence_score=random.uniform(0.5, 0.98),
            trend=trend,
            growth_percentage=random.uniform(-10.0, 45.0),
            expected_demand=base_demand * 7 * random.uniform(0.9, 1.4),
            algorithm_used=random.choice(algorithms)
        )
        forecasts.append(forecast)
        
    print(f'Inserting {len(forecasts)} forecasts and {len(histories)} histories...')
    if histories:
        await ForecastHistory.insert_many(histories)
    if forecasts:
        await ForecastResult.insert_many(forecasts)
    
    print('Forecast seeding complete.')

if __name__ == '__main__':
    asyncio.run(main())
