import logging
import uuid
from typing import Dict, Any
from models.final_intelligence import (
    BusinessImpactAssessment, DecisionHistory, BusinessHistory, CrisisHistory,
    RecommendationHistory, LearningHistory, CoordinatorHistory
)
from google import genai
from core.config import settings

logger = logging.getLogger(__name__)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class MemoryEngine:
    async def log_business_history(self, health_score: float, risk_score: float, impact_score: float, crises_count: int):
        hist = BusinessHistory(
            snapshot_id=str(uuid.uuid4()),
            health_score=health_score,
            risk_score=risk_score,
            impact_score=impact_score,
            active_crises_count=crises_count
        )
        await hist.insert()
        return hist

    async def log_decision(self, trigger: str, context: str, decision: str, reasoning: str, confidence: float, status: str):
        dec = DecisionHistory(
            decision_id=str(uuid.uuid4()),
            trigger_event=trigger,
            context_summary=context,
            decision_taken=decision,
            reasoning=reasoning,
            confidence=confidence,
            status=status
        )
        await dec.insert()
        return dec

    async def log_crisis(self, severity: str, root_cause: str, impact_estimate: float, status: str):
        crisis = CrisisHistory(
            crisis_id=str(uuid.uuid4()),
            severity=severity,
            root_cause=root_cause,
            impact_estimate=impact_estimate,
            status=status
        )
        await crisis.insert()
        return crisis

    async def generate_learning_summary(self, crisis_id: str, outcome: str):
        prompt = f"Analyze the outcome of this crisis (ID: {crisis_id}): {outcome}. What is the key lesson learned and how should we adjust our strategy next time? Respond in JSON with keys: lesson_learned, strategy_adjustment, confidence_improvement (float)."
        try:
            resp = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = resp.text.strip()
            if text.startswith('```json'): text = text[7:-3].strip()
            import json
            data = json.loads(text)
            
            learning = LearningHistory(
                learning_id=str(uuid.uuid4()),
                crisis_id=crisis_id,
                lesson_learned=data.get("lesson_learned", "N/A"),
                strategy_adjustment=data.get("strategy_adjustment", "N/A"),
                confidence_improvement=float(data.get("confidence_improvement", 0.05))
            )
            await learning.insert()
            return learning
        except Exception as e:
            logger.error(f"Failed to generate learning: {e}")
            return None

    async def log_coordinator_interaction(self, direction: str, payload: dict, status: str):
        interaction = CoordinatorHistory(
            interaction_id=str(uuid.uuid4()),
            direction=direction,
            payload=payload,
            status=status
        )
        await interaction.insert()
        return interaction

    async def retrieve_similar_crises(self, current_severity: str, limit: int = 3) -> list[dict]:
        logger.info(f"Retrieving past crises with severity {current_severity}...")
        crises = await CrisisHistory.find(CrisisHistory.severity == current_severity).sort("-identified_at").limit(limit).to_list()
        
        results = []
        for c in crises:
            # Try to find corresponding learning
            learning = await LearningHistory.find_one(LearningHistory.crisis_id == c.crisis_id)
            results.append({
                "crisis_id": c.crisis_id,
                "root_cause": c.root_cause,
                "impact_estimate": c.impact_estimate,
                "lesson_learned": learning.lesson_learned if learning else "N/A",
                "strategy_adjustment": learning.strategy_adjustment if learning else "N/A"
            })
        return results

    async def retrieve_recent_context(self) -> dict:
        logger.info("Loading recent context from memory...")
        last_business = await BusinessHistory.find_all().sort("-timestamp").limit(1).to_list()
        last_decision = await DecisionHistory.find_all().sort("-timestamp").limit(1).to_list()
        active_crises = await CrisisHistory.find(CrisisHistory.status == "Active").to_list()
        
        return {
            "last_health_score": last_business[0].health_score if last_business else 100.0,
            "last_decision": last_decision[0].decision_taken if last_decision else "None",
            "active_crises_count": len(active_crises),
            "active_crises_details": [{"root_cause": c.root_cause, "severity": c.severity} for c in active_crises]
        }

memory_engine = MemoryEngine()
