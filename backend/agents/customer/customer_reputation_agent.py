"""
Customer & Brand Reputation Agent
=================================
A Business Crisis Commander AI microservice built with FastAPI, Pydantic, and Groq API.
Analyzes multi-channel customer feedback during business incidents to assess reputation damage,
cluster complaints, compute risk scores, and generate executive mitigation strategies.

Usage:
    uvicorn customer_reputation_agent:app --reload
"""

import os
import logging
import json
from typing import List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables configuration
MODEL_API_KEY = os.getenv("MODEL_API") or os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip()
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", FRONTEND_URL).split(",")
    if origin.strip()
]
CORS_ALLOWED_ORIGINS = list(dict.fromkeys(CORS_ALLOWED_ORIGINS))
if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = ["*"]

# Standardized Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("CustomerReputationAgent")

# Groq / OpenAI Client Initialization
groq_client = None
if MODEL_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=MODEL_API_KEY)
        logger.info(f"Initialized Groq client using model: {MODEL_NAME}")
    except ImportError:
        try:
            from openai import OpenAI
            groq_client = OpenAI(
                api_key=MODEL_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info(f"Initialized Groq via OpenAI client compatibility layer with model: {MODEL_NAME}")
        except ImportError:
            logger.warning("Neither 'groq' nor 'openai' libraries are installed.")
else:
    logger.warning("MODEL_API / GROQ_API_KEY is not set in environment or .env file. Running in fallback mode.")

# Optional NLP tools for sentiment enrichment/fallback
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    vader_analyzer = SentimentIntensityAnalyzer()
    HAS_VADER = True
except Exception:
    HAS_VADER = False


# ============================================================================
# ENUMS & PYDANTIC MODELS
# ============================================================================

class SeverityLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SentimentCategory(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class EmotionType(str, Enum):
    ANGER = "Anger"
    FRUSTRATION = "Frustration"
    FEAR = "Fear"
    CONFUSION = "Confusion"
    TRUST = "Trust"
    DISAPPOINTMENT = "Disappointment"


class ComplaintCategoryName(str, Enum):
    LATE_DELIVERY = "Late Delivery"
    REFUND = "Refund"
    POOR_SUPPORT = "Poor Support"
    WEBSITE_DOWN = "Website Down"
    PAYMENT_ISSUES = "Payment Issues"
    PRODUCT_DAMAGE = "Product Damage"
    COMMUNICATION = "Communication"
    OTHER = "Other"


# --- Request Schemas ---

class IncidentAnalysisRequest(BaseModel):
    company: str = Field(..., example="Amazon", description="Name of the company affected")
    industry: str = Field(..., example="E-Commerce", description="Industry domain")
    incident: str = Field(
        ...,
        example="Customers are angry because deliveries are delayed after a ransomware attack.",
        description="Core description of the crisis or incident"
    )
    social_media: List[str] = Field(default_factory=list, description="List of social media posts")
    customer_reviews: List[str] = Field(default_factory=list, description="List of direct product/service reviews")
    support_tickets: List[str] = Field(default_factory=list, description="List of support ticket summaries")

    @field_validator("social_media", "customer_reviews", "support_tickets")
    def check_non_null(cls, v):
        return v


# --- Response Models ---

class ComplaintCategoryCount(BaseModel):
    name: str = Field(..., description="Category of the complaint")
    count: int = Field(..., description="Number of instances clustered into this category")


class ReputationAnalysisResponse(BaseModel):
    agent_name: str = Field(default="Customer Reputation Agent", description="Agent identifier")
    overall_sentiment: SentimentCategory = Field(..., description="Primary overall sentiment")
    positive_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of positive feedback")
    neutral_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of neutral feedback")
    negative_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of negative feedback")
    dominant_emotions: List[EmotionType] = Field(..., description="Key emotions identified")
    complaint_categories: List[ComplaintCategoryCount] = Field(..., description="Clustered feedback categories")
    root_causes: List[str] = Field(..., description="Root causes of customer dissatisfaction")
    brand_risk_score: int = Field(..., ge=0, le=100, description="Risk score between 0 and 100")
    severity: SeverityLevel = Field(..., description="Severity level based on risk score")
    public_statement: str = Field(..., description="Drafted formal PR public statement")
    customer_email: str = Field(..., description="Drafted customer apology email")
    compensation_plan: List[str] = Field(..., description="Concrete compensation mechanisms")
    retention_strategy: List[str] = Field(..., description="Long-term customer retention strategies")
    immediate_actions: List[str] = Field(..., description="Actionable immediate next steps")
    executive_summary: str = Field(..., description="Summary for leadership & crisis commander")


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

class LocalNLPAnalyzer:
    """Helper class providing fallback rule-based sentiment statistics."""
    
    @staticmethod
    def analyze_text(text: str) -> float:
        """Returns polarity score in range [-1.0, 1.0]."""
        if HAS_VADER:
            scores = vader_analyzer.polarity_scores(text)
            return scores['compound']
        elif HAS_TEXTBLOB:
            return TextBlob(text).sentiment.polarity
        else:
            negatives = ["angry", "terrible", "disappointed", "useless", "late", "missing", "delay", "bad", "never"]
            positives = ["good", "great", "thanks", "helpful", "resolved", "love", "fast"]
            text_lower = text.lower()
            score = 0.0
            for word in negatives:
                if word in text_lower:
                    score -= 0.3
            for word in positives:
                if word in text_lower:
                    score += 0.3
            return max(-1.0, min(1.0, score))


class GroqCrisisAnalyzer:
    """Core analysis engine utilizing Groq API for high-speed sentiment and PR analysis."""

    def __init__(self, client=None, model_name: str = "llama-3.3-70b-versatile"):
        self.client = client
        self.model_name = model_name

    def run_analysis(self, payload: IncidentAnalysisRequest) -> ReputationAnalysisResponse:
        """Executes full analysis cycle using Groq or rule-based fallback."""
        
        all_feedback = payload.social_media + payload.customer_reviews + payload.support_tickets
        total_items = max(len(all_feedback), 1)

        # Calculate NLP baseline statistics
        polarity_scores = [LocalNLPAnalyzer.analyze_text(item) for item in all_feedback]
        pos_count = sum(1 for s in polarity_scores if s > 0.15)
        neg_count = sum(1 for s in polarity_scores if s < -0.15)
        neu_count = total_items - (pos_count + neg_count)

        pos_pct = round((pos_count / total_items) * 100, 1)
        neg_pct = round((neg_count / total_items) * 100, 1)
        neu_pct = round(100.0 - (pos_pct + neg_pct), 1)

        if neg_pct > 50:
            overall_sentiment = SentimentCategory.NEGATIVE
        elif pos_pct > 50:
            overall_sentiment = SentimentCategory.POSITIVE
        else:
            overall_sentiment = SentimentCategory.NEUTRAL

        # Execute via Groq API if client is present
        if self.client:
            try:
                return self._groq_analysis(payload, pos_pct, neu_pct, neg_pct, overall_sentiment)
            except Exception as e:
                logger.error(f"Groq API call failed: {str(e)}. Falling back to deterministic analysis.")

        # Local Algorithmic Fallback Engine
        return self._algorithmic_fallback(payload, pos_pct, neu_pct, neg_pct, overall_sentiment)

    def _groq_analysis(
        self,
        payload: IncidentAnalysisRequest,
        pos_pct: float,
        neu_pct: float,
        neg_pct: float,
        default_sentiment: SentimentCategory
    ) -> ReputationAnalysisResponse:

        system_prompt = (
            "You are an expert Senior AI Customer Reputation Specialist inside a Business Crisis Commander AI System. "
            "Analyze the corporate crisis data and return ONLY a valid JSON object strictly matching the required output JSON schema."
        )

        user_prompt = f"""
Analyze the following corporate crisis and feedback data.

--- INCIDENT DETAILS ---
Company: {payload.company}
Industry: {payload.industry}
Incident: {payload.incident}

--- FEEDBACK ---
Social Media: {json.dumps(payload.social_media)}
Customer Reviews: {json.dumps(payload.customer_reviews)}
Support Tickets: {json.dumps(payload.support_tickets)}

--- PRE-COMPUTED SENTIMENT METRICS ---
Positive %: {pos_pct}
Neutral %: {neu_pct}
Negative %: {neg_pct}

OUTPUT INSTRUCTIONS:
Return a valid JSON object with EXACTLY the following key names:
{{
  "agent_name": "Customer Reputation Agent",
  "overall_sentiment": "Positive" | "Neutral" | "Negative",
  "positive_percentage": {pos_pct},
  "neutral_percentage": {neu_pct},
  "negative_percentage": {neg_pct},
  "dominant_emotions": ["Anger", "Frustration", "Fear", "Confusion", "Trust", "Disappointment"],
  "complaint_categories": [
     {{"name": "Late Delivery", "count": 5}}
  ],
  "root_causes": ["string"],
  "brand_risk_score": number (0-100),
  "severity": "SAFE" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "public_statement": "string",
  "customer_email": "string",
  "compensation_plan": ["string"],
  "retention_strategy": ["string"],
  "immediate_actions": ["string"],
  "executive_summary": "string"
}}
"""

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        raw_content = completion.choices[0].message.content
        parsed_json = json.loads(raw_content)

        return ReputationAnalysisResponse(**parsed_json)

    def _algorithmic_fallback(
        self,
        payload: IncidentAnalysisRequest,
        pos_pct: float,
        neu_pct: float,
        neg_pct: float,
        overall_sentiment: SentimentCategory
    ) -> ReputationAnalysisResponse:
        """Deterministic fallback engine."""
        
        all_text = " ".join(payload.social_media + payload.customer_reviews + payload.support_tickets + [payload.incident]).lower()

        emotions = []
        if any(w in all_text for w in ["angry", "terrible", "never", "useless"]):
            emotions.append(EmotionType.ANGER)
        if any(w in all_text for w in ["wait", "delayed", "disappointed", "slow"]):
            emotions.append(EmotionType.FRUSTRATION)
        if any(w in all_text for w in ["missing", "where", "cancel"]):
            emotions.append(EmotionType.DISAPPOINTMENT)
        if not emotions:
            emotions = [EmotionType.FRUSTRATION, EmotionType.CONFUSION]

        counts = {
            ComplaintCategoryName.LATE_DELIVERY.value: 0,
            ComplaintCategoryName.REFUND.value: 0,
            ComplaintCategoryName.POOR_SUPPORT.value: 0,
            ComplaintCategoryName.COMMUNICATION.value: 0,
            ComplaintCategoryName.OTHER.value: 0
        }

        for item in payload.social_media + payload.customer_reviews + payload.support_tickets:
            item_lower = item.lower()
            if any(w in item_lower for w in ["late", "delay", "waited", "where"]):
                counts[ComplaintCategoryName.LATE_DELIVERY.value] += 1
            elif any(w in item_lower for w in ["refund", "money", "compensate"]):
                counts[ComplaintCategoryName.REFUND.value] += 1
            elif any(w in item_lower for w in ["support", "useless", "service"]):
                counts[ComplaintCategoryName.POOR_SUPPORT.value] += 1
            elif any(w in item_lower for w in ["notify", "tell", "update"]):
                counts[ComplaintCategoryName.COMMUNICATION.value] += 1
            else:
                counts[ComplaintCategoryName.OTHER.value] += 1

        complaint_categories = [
            ComplaintCategoryCount(name=k, count=v) for k, v in counts.items() if v > 0
        ]

        base_score = int(neg_pct * 0.7) + 20
        risk_score = min(100, max(0, base_score))

        if risk_score <= 20:
            severity = SeverityLevel.SAFE
        elif risk_score <= 40:
            severity = SeverityLevel.LOW
        elif risk_score <= 60:
            severity = SeverityLevel.MEDIUM
        elif risk_score <= 80:
            severity = SeverityLevel.HIGH
        else:
            severity = SeverityLevel.CRITICAL

        return ReputationAnalysisResponse(
            agent_name="Customer Reputation Agent",
            overall_sentiment=overall_sentiment,
            positive_percentage=pos_pct,
            neutral_percentage=neu_pct,
            negative_percentage=neg_pct,
            dominant_emotions=emotions,
            complaint_categories=complaint_categories,
            root_causes=[
                "Disruption in fulfillment pipeline following security incident.",
                "Inadequate proactive communications during initial crisis phase."
            ],
            brand_risk_score=risk_score,
            severity=severity,
            public_statement=(
                f"At {payload.company}, our customers come first. We are actively mitigating "
                f"the recent operational incident regarding: '{payload.incident}'. Our technical and support "
                "teams are working round-the-clock to restore full operations and compensate affected users."
            ),
            customer_email=(
                f"Dear Valued {payload.company} Customer,\n\nWe sincerely apologize for the recent disruption. "
                "We understand your frustration and are taking immediate action to address open support tickets and issue credits."
            ),
            compensation_plan=[
                "15% Discount Voucher on next order",
                "Full refund for delayed or missing packages",
                "Free priority shipping credit"
            ],
            retention_strategy=[
                "Transparent operational status updates every 6 hours",
                "Bonus loyalty points credited to impacted user accounts",
                "Dedicated hotline for high-priority support escalation"
            ],
            immediate_actions=[
                "Publish official public statement across corporate channels",
                "Scale up customer service team capacity",
                "Send proactive update email to affected users"
            ],
            executive_summary=(
                f"Incident has caused a {severity.value} brand risk with {neg_pct}% negative sentiment. "
                "Primary issue is delivery delay and customer support backlogs. Immediate proactive PR and compensation required."
            )
        )


# Instantiate Global Analyzer
analyzer_engine = GroqCrisisAnalyzer(client=groq_client, model_name=MODEL_NAME)

# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="Customer & Brand Reputation Agent API (Groq)",
    description="Business Crisis Commander AI Subsystem using Groq API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    """Root metadata endpoint."""
    return {
        "agent": "Customer Reputation Agent",
        "provider": "Groq API",
        "model": MODEL_NAME,
        "status": "ONLINE"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "HEALTHY",
        "has_groq_api_key": MODEL_API_KEY is not None,
        "model_name": MODEL_NAME,
        "has_vader": HAS_VADER,
        "has_textblob": HAS_TEXTBLOB
    }


@app.post(
    "/analyze",
    response_model=ReputationAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analysis"]
)
def analyze_reputation(payload: IncidentAnalysisRequest):
    """
    Main Crisis Analysis Endpoint.
    Analyzes customer sentiment, clusters complaints, assesses reputation risk,
    and generates PR / compensation / retention strategies using Groq API.
    """
    logger.info(f"Received crisis analysis request for company: {payload.company}")
    
    try:
        response = analyzer_engine.run_analysis(payload)
        logger.info(f"Analysis completed successfully. Risk Score: {response.brand_risk_score} ({response.severity.value})")
        return response
    except Exception as e:
        logger.error(f"Error processing crisis analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred during crisis analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("customer_reputation_agent:app", host="0.0.0.0", port=8066, reload=True)