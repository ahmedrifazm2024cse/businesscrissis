from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(str, Enum):
    DATA_BREACH = "Data Breach"
    CONTRACT_BREACH = "Contract Breach"
    PRIVACY_VIOLATION = "Privacy Violation"
    GOVERNANCE_ISSUE = "Governance Issue"
    REGULATORY_VIOLATION = "Regulatory Violation"
    INSIDER_THREAT = "Insider Threat"
    CYBER_INCIDENT = "Cyber Incident"
    EMPLOYMENT_ISSUE = "Employment Issue"
    VENDOR_RISK = "Vendor Risk"
    AI_COMPLIANCE = "AI Compliance Issue"


class IncidentInput(BaseModel):
    """Input schema for incident analysis."""
    description: str = Field(..., min_length=20, description="Detailed incident description")
    incident_type: Optional[str] = Field(None, description="Type of incident if known")
    affected_systems: Optional[List[str]] = Field(default_factory=list)
    affected_data_types: Optional[List[str]] = Field(default_factory=list)
    jurisdiction: Optional[str] = Field("EU / GDPR", description="Primary legal jurisdiction")
    company_size: Optional[str] = Field(None, description="Company size category")
    industry: Optional[str] = Field(None, description="Industry vertical")


class Regulation(BaseModel):
    name: str
    article: Optional[str] = None
    section: Optional[str] = None
    description: str
    applicable: bool = True
    severity: RiskLevel


class LegalFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: str
    title: str
    description: str
    severity: RiskLevel
    regulations: List[Regulation] = Field(default_factory=list)
    recommendation: str
    reasoning: str


class PenaltyEstimate(BaseModel):
    regulation: str
    min_amount: float
    max_amount: float
    currency: str = "EUR"
    basis: str


class DisclosureNotice(BaseModel):
    type: str
    audience: str
    deadline: str
    content: str
    regulatory_requirement: str


class ComplianceAction(BaseModel):
    priority: str  # immediate | short_term | long_term
    action: str
    owner: str
    deadline: str
    legal_basis: str


class ComplianceScore(BaseModel):
    privacy: int = Field(ge=0, le=100)
    contracts: int = Field(ge=0, le=100)
    regulatory: int = Field(ge=0, le=100)
    governance: int = Field(ge=0, le=100)
    disclosure: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class AuditEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    details: str


class TimelineEvent(BaseModel):
    date: str
    event: str
    type: str  # incident | notification | action | deadline | filing
    status: str  # pending | completed | overdue


class AnalysisReport(BaseModel):
    """Complete legal analysis report output."""
    id: str = Field(default_factory=lambda: f"LEX-{str(uuid.uuid4())[:8].upper()}")
    incident_id: str = Field(default_factory=lambda: f"INC-{str(uuid.uuid4())[:8].upper()}")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    incident_summary: str
    incident_type: str
    risk_level: RiskLevel
    compliance_scores: ComplianceScore
    legal_findings: List[LegalFinding] = Field(default_factory=list)
    regulations_triggered: List[Regulation] = Field(default_factory=list)
    penalty_estimates: List[PenaltyEstimate] = Field(default_factory=list)
    immediate_actions: List[ComplianceAction] = Field(default_factory=list)
    long_term_actions: List[ComplianceAction] = Field(default_factory=list)
    disclosure_notices: List[DisclosureNotice] = Field(default_factory=list)
    legal_hold_recommended: bool = False
    executive_summary: str
    ai_reasoning: str
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    compliance_timeline: List[TimelineEvent] = Field(default_factory=list)
