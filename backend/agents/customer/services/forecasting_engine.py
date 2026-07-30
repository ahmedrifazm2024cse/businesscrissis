import math
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ForecastingEngine:
    """
    Core engine for handling data cleaning and executing multiple forecasting algorithms.
    """
    
    def __init__(self):
        pass

    def clean_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cleans historical data: removes duplicates, handles missing values (forward fill),
        normalizes values, and detects basic anomalies.
        Expects a list of dicts with 'date' and 'value'.
        """
        if not raw_data:
            return []
            
        # 1. Remove duplicates & Sort by date
        unique_data = {}
        for item in raw_data:
            # Assumes 'date' is a datetime object or parseable string
            dt = item['date'] if isinstance(item['date'], datetime) else datetime.fromisoformat(str(item['date']))
            key = dt.strftime("%Y-%m-%d")
            # If duplicate exists for same day, we can average them or take latest. We'll take latest.
            if key not in unique_data or item.get('recorded_at', datetime.min) >= unique_data[key].get('recorded_at', datetime.min):
                unique_data[key] = {
                    'date': dt,
                    'value': float(item.get('sales_quantity', 0.0) + item.get('inventory_movement', 0.0)),
                    'original': item
                }
                
        sorted_keys = sorted(unique_data.keys())
        cleaned = [unique_data[k] for k in sorted_keys]
        
        # 2. Handle missing values (Forward fill)
        for i in range(1, len(cleaned)):
            if cleaned[i]['value'] is None or math.isnan(cleaned[i]['value']):
                cleaned[i]['value'] = cleaned[i-1]['value']
                
        # 3. Detect anomalies (simple z-score approach)
        values = [item['value'] for item in cleaned]
        n = len(values)
        if n > 2:
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            std_dev = math.sqrt(variance) if variance > 0 else 1.0
            
            for item in cleaned:
                z_score = abs(item['value'] - mean) / std_dev
                # If z-score > 2, cap it to 2 standard deviations to normalize
                if z_score > 2:
                    item['value'] = mean + (2 * std_dev * (1 if item['value'] > mean else -1))
                    item['value'] = max(0.0, item['value']) # Ensure non-negative demand
                    
        return cleaned

    def simple_moving_average(self, data: List[float], window: int = 7) -> float:
        if not data:
            return 0.0
        n = len(data)
        window = min(window, n)
        return sum(data[-window:]) / window

    def weighted_moving_average(self, data: List[float], window: int = 7) -> float:
        if not data:
            return 0.0
        n = len(data)
        window = min(window, n)
        subset = data[-window:]
        weights = list(range(1, window + 1))
        return sum(d * w for d, w in zip(subset, weights)) / sum(weights)

    def linear_regression(self, data: List[float]) -> float:
        if not data:
            return 0.0
        n = len(data)
        if n == 1:
            return data[0]
            
        sum_x = sum(range(n))
        sum_y = sum(data)
        sum_xy = sum(x * y for x, y in enumerate(data))
        sum_xx = sum(x * x for x in range(n))
        
        denominator = (n * sum_xx - sum_x * sum_x)
        if denominator == 0:
            return data[-1]
            
        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n
        
        # Predict the next point (x = n)
        return max(0.0, m * n + b)

    def exponential_smoothing(self, data: List[float], alpha: float = 0.3) -> float:
        if not data:
            return 0.0
        if len(data) == 1:
            return data[0]
            
        forecast = data[0]
        for actual in data[1:]:
            forecast = alpha * actual + (1 - alpha) * forecast
            
        return max(0.0, forecast)

    def generate_forecast(self, historical_data: List[Dict[str, Any]], horizon_days: int = 1) -> Dict[str, Any]:
        """
        Runs all models, picks the one that fits best on a validation split, and predicts the next 'horizon_days'.
        """
        cleaned = self.clean_data(historical_data)
        values = [item['value'] for item in cleaned]
        
        if not values:
            return {
                "forecast_quantity": 0.0,
                "confidence_score": 0.0,
                "algorithm_used": "Fallback",
                "trend": "Stable",
                "growth_percentage": 0.0,
                "expected_demand": 0.0
            }
            
        # If we have very little data, use SMA
        if len(values) < 4:
            val = self.simple_moving_average(values, window=3)
            return {
                "forecast_quantity": val * horizon_days,
                "confidence_score": 0.3,
                "algorithm_used": "SMA",
                "trend": "Stable",
                "growth_percentage": 0.0,
                "expected_demand": val * horizon_days
            }
            
        # Simple backtesting to pick best algorithm
        train = values[:-1]
        actual = values[-1]
        
        predictions = {
            "SMA": self.simple_moving_average(train, window=7),
            "WMA": self.weighted_moving_average(train, window=7),
            "LinearRegression": self.linear_regression(train),
            "ExponentialSmoothing": self.exponential_smoothing(train, alpha=0.3)
        }
        
        # Find algorithm with lowest error
        best_algo = min(predictions, key=lambda k: abs(predictions[k] - actual))
        
        # Now forecast using the best algorithm on ALL data
        daily_forecast = 0.0
        if best_algo == "SMA":
            daily_forecast = self.simple_moving_average(values, window=7)
        elif best_algo == "WMA":
            daily_forecast = self.weighted_moving_average(values, window=7)
        elif best_algo == "LinearRegression":
            daily_forecast = self.linear_regression(values)
        elif best_algo == "ExponentialSmoothing":
            daily_forecast = self.exponential_smoothing(values, alpha=0.3)
            
        expected_demand = daily_forecast * horizon_days
        
        # Calculate Confidence
        variance = sum((x - daily_forecast) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        # Higher variation -> lower confidence
        confidence = max(0.2, min(0.95, 1.0 - (std_dev / (daily_forecast + 0.1))))
        
        # Calculate Growth Percentage
        recent_avg = sum(values[-3:]) / 3
        old_avg = sum(values[:3]) / 3 if len(values) >= 6 else values[0]
        
        growth = 0.0
        if old_avg > 0:
            growth = ((recent_avg - old_avg) / old_avg) * 100.0
            
        # Basic Trend
        trend = "Stable"
        if growth > 15.0:
            trend = "Increasing"
        elif growth < -15.0:
            trend = "Decreasing"
            
        return {
            "forecast_quantity": round(expected_demand, 2),
            "confidence_score": round(confidence, 2),
            "algorithm_used": best_algo,
            "trend": trend,
            "growth_percentage": round(growth, 2),
            "expected_demand": round(expected_demand, 2)
        }

forecasting_engine = ForecastingEngine()
