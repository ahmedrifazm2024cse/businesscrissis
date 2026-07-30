import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        pass
        
    def detect_trend(self, values: List[float]) -> str:
        """
        Classifies trend into: Increasing, Decreasing, Stable, Sudden Spike, Sudden Drop, Recovering, Declining.
        """
        if len(values) < 5:
            return "Stable"
            
        recent = values[-2:]
        previous = values[-5:-2]
        
        avg_recent = sum(recent) / len(recent)
        avg_previous = sum(previous) / len(previous)
        
        if avg_previous == 0:
            return "Stable" if avg_recent == 0 else "Sudden Spike"
            
        change = (avg_recent - avg_previous) / avg_previous
        
        # Look at the very last point vs second to last point for sudden changes
        last_change = 0
        if values[-2] > 0:
            last_change = (values[-1] - values[-2]) / values[-2]
            
        if last_change > 0.8:
            return "Sudden Spike"
        elif last_change < -0.8:
            return "Sudden Drop"
            
        if change > 0.15:
            if avg_recent > sum(values)/len(values):
                return "Increasing"
            else:
                return "Recovering"
        elif change < -0.15:
            if avg_recent < sum(values)/len(values):
                return "Decreasing"
            else:
                return "Declining"
                
        return "Stable"

    def detect_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """
        Detects Weekly/Monthly/Quarterly seasonality patterns using simple autocorrelation approximations.
        """
        if len(values) < 14:
            return {"seasonality": "None", "strength": 0.0}
            
        # Very simple autocorrelation for lag 7 (Weekly)
        def auto_corr(lag):
            if len(values) <= lag: return 0.0
            mean = sum(values) / len(values)
            numerator = sum((values[i] - mean) * (values[i-lag] - mean) for i in range(lag, len(values)))
            denominator = sum((x - mean)**2 for x in values)
            if denominator == 0: return 0.0
            return numerator / denominator

        lag_7 = auto_corr(7)
        lag_30 = auto_corr(30) if len(values) >= 60 else 0.0
        
        if lag_7 > 0.6:
            return {"seasonality": "Weekly", "strength": round(lag_7, 2)}
        elif lag_30 > 0.6:
            return {"seasonality": "Monthly", "strength": round(lag_30, 2)}
            
        return {"seasonality": "None", "strength": 0.0}

    def detect_demand_pattern(self, values: List[float]) -> str:
        """
        Identifies if product is Fast Moving, Slow Moving, Dead, Trending, etc.
        """
        if not values:
            return "Unknown"
            
        avg_demand = sum(values) / len(values)
        non_zero_days = sum(1 for x in values if x > 0)
        
        if avg_demand == 0:
            return "Dead Product"
            
        frequency = non_zero_days / len(values)
        
        if frequency > 0.8 and avg_demand > 20:
            return "Fast Moving"
        elif frequency < 0.3 or avg_demand < 2:
            return "Slow Moving"
            
        trend = self.detect_trend(values)
        if trend == "Increasing" or trend == "Sudden Spike":
            return "Trending Product"
            
        return "Regular Product"

trend_analyzer = TrendAnalyzer()
