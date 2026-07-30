from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math

class StockoutPredictionEngine:
    @staticmethod
    def predict(available_stock: int, daily_demand_history: List[float]) -> Dict[str, Any]:
        """
        Predicts stockout date using Moving Average (MA), Weighted Moving Average (WMA),
        and Trend-Adjusted Forecasting.
        """
        if not daily_demand_history or available_stock <= 0:
            return {
                "stockout_date": datetime.now().isoformat(),
                "probability": 1.0,
                "confidence": 0.95,
                "days_until_stockout": 0,
                "forecast_method": "Immediate"
            }

        n = len(daily_demand_history)
        
        # 1. Simple Moving Average (SMA)
        sma = sum(daily_demand_history) / n
        
        # 2. Weighted Moving Average (WMA) - giving more weight to recent days
        weights = list(range(1, n + 1))
        wma = sum(d * w for d, w in zip(daily_demand_history, weights)) / sum(weights)
        
        # 3. Trend-Adjusted Forecast (Simple linear regression over the history)
        # y = mx + b
        sum_x = sum(range(n))
        sum_y = sum(daily_demand_history)
        sum_xy = sum(x * y for x, y in enumerate(daily_demand_history))
        sum_xx = sum(x * x for x in range(n))
        
        if (n * sum_xx - sum_x * sum_x) == 0:
            m = 0
        else:
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        
        trend_demand = max(0.1, sma + m * n) # Prevent negative demand
        
        # We will use an ensemble approach (Average of SMA, WMA, Trend)
        ensemble_daily_demand = (sma + wma + trend_demand) / 3.0
        
        if ensemble_daily_demand <= 0.01:
            return {
                "stockout_date": None,
                "probability": 0.01,
                "confidence": 0.90,
                "days_until_stockout": 999,
                "forecast_method": "Ensemble"
            }
            
        days_until_stockout = available_stock / ensemble_daily_demand
        
        # Calculate Probability and Confidence based on variance and days remaining
        variance = sum((x - sma) ** 2 for x in daily_demand_history) / n
        std_dev = math.sqrt(variance)
        
        # If variance is very high, confidence is lower. 
        # If days_until_stockout is very short, probability is higher.
        confidence = max(0.5, 1.0 - (std_dev / (sma + 0.1)))
        
        probability = 1.0
        if days_until_stockout > 30:
            probability = 0.1
        elif days_until_stockout > 14:
            probability = 0.3
        elif days_until_stockout > 7:
            probability = 0.6
        elif days_until_stockout > 3:
            probability = 0.85
            
        stockout_date = datetime.now() + timedelta(days=int(days_until_stockout))
        
        return {
            "stockout_date": stockout_date.isoformat(),
            "probability": round(probability, 2),
            "confidence": round(confidence, 2),
            "days_until_stockout": round(days_until_stockout, 2),
            "forecast_method": "Ensemble (SMA, WMA, Trend)"
        }

stockout_prediction_engine = StockoutPredictionEngine()
