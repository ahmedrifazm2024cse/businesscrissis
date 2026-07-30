import datetime
import json
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database.connection import Base

class MarketAnalysisReport(Base):
    __tablename__ = "market_analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    market_risk_score = Column(Integer, nullable=False)
    competitor_threat = Column(String(50), nullable=False) # e.g., "High", "Medium", "Low"
    market_opportunity = Column(String(50), nullable=False) # e.g., "High", "Medium", "Low"
    demand_forecast = Column(Text, nullable=False)
    confidence = Column(Integer, default=85)
    
    # Store lists as JSON strings
    key_findings_json = Column(Text, nullable=False)
    recommendations_json = Column(Text, nullable=False)

    @property
    def key_findings(self):
        try:
            return json.loads(self.key_findings_json)
        except Exception:
            return []

    @key_findings.setter
    def key_findings(self, value):
        self.key_findings_json = json.dumps(value)

    @property
    def recommendations(self):
        try:
            return json.loads(self.recommendations_json)
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, value):
        self.recommendations_json = json.dumps(value)
