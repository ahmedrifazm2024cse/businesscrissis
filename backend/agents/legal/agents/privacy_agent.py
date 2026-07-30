"""
LexGuardian Privacy Agent
Analyzes PII exposure, consent issues, data retention violations, cross-border transfers
"""
import logging
from datetime import datetime
from schemas.analysis import LegalFinding, Regulation, RiskLevel, AuditEntry

logger = logging.getLogger(__name__)

PII_CATEGORIES = {
    "names": {"risk": "moderate", "gdpr_special": False},
    "email": {"risk": "moderate", "gdpr_special": False},
    "phone": {"risk": "moderate", "gdpr_special": False},
    "address": {"risk": "significant", "gdpr_special": False},
    "payment": {"risk": "critical", "gdpr_special": False},
    "credit card": {"risk": "critical", "gdpr_special": False},
    "ssn": {"risk": "critical", "gdpr_special": False},
    "passport": {"risk": "critical", "gdpr_special": False},
    "health": {"risk": "critical", "gdpr_special": True},
    "medical": {"risk": "critical", "gdpr_special": True},
    "biometric": {"risk": "critical", "gdpr_special": True},
    "religion": {"risk": "critical", "gdpr_special": True},
    "political": {"risk": "critical", "gdpr_special": True},
    "children": {"risk": "critical", "gdpr_special": True},
}


class PrivacyAgent:
    """Agent for privacy risk analysis and PII assessment."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Privacy Agent"

    def analyze(self, incident: dict) -> dict:
        logger.info(f"[{self.name}] Starting privacy analysis")
        start = datetime.utcnow()
        description = incident.get("description", "").lower()

        detected_pii = self._detect_pii(description)
        special_categories = [p for p in detected_pii if PII_CATEGORIES.get(p, {}).get("gdpr_special")]
        findings = self._generate_findings(description, detected_pii, special_categories)
        risk_score = self._calculate_privacy_score(description, detected_pii, special_categories)

        duration = (datetime.utcnow() - start).total_seconds()
        logger.info(f"[{self.name}] Detected PII: {detected_pii}")

        return {
            "agent": self.name,
            "detected_pii_categories": detected_pii,
            "special_categories": special_categories,
            "findings": findings,
            "privacy_risk_score": risk_score,
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="PII Assessment",
                details=f"Detected PII: {', '.join(detected_pii) if detected_pii else 'None identified'}. Special categories: {', '.join(special_categories) if special_categories else 'None'}",
            ).model_dump(),
        }

    def _detect_pii(self, description: str) -> list:
        detected = []
        for pii_type in PII_CATEGORIES:
            if pii_type in description:
                detected.append(pii_type)
        # Additional keyword mapping
        if any(kw in description for kw in ["customer data", "user data", "personal information", "pii"]):
            if "names" not in detected:
                detected.append("names")
            if "email" not in detected:
                detected.append("email")
        return list(set(detected))

    def _generate_findings(self, description: str, pii: list, special: list) -> list:
        findings = []
        if pii:
            severity = RiskLevel.CRITICAL if special else (RiskLevel.HIGH if "payment" in pii else RiskLevel.SIGNIFICANT)
            findings.append(LegalFinding(
                category="Privacy & Data Protection",
                title="Personally Identifiable Information (PII) Exposure",
                description=f"The incident involves exposure of PII categories: {', '.join(pii)}. {'Special category data under GDPR Article 9 detected.' if special else ''}",
                severity=severity,
                regulations=[
                    Regulation(name="GDPR", article="Article 4, 33, 34", description="PII breach notification obligations", applicable=True, severity=severity),
                    Regulation(name="CCPA", section="1798.82", description="California breach notification", applicable=True, severity=RiskLevel.HIGH),
                ],
                recommendation="Immediately assess the scope of PII exposure. Engage DPO for legal assessment. Prepare breach notification under GDPR Article 33.",
                reasoning=f"GDPR defines personal data broadly under Article 4(1). Exposure of {', '.join(pii)} constitutes a personal data breach requiring regulatory notification.",
            ).model_dump())

        if "payment" in pii or "credit card" in pii:
            findings.append(LegalFinding(
                category="Financial Data",
                title="Payment Card Data Exposure — PCI DSS Triggered",
                description="Payment or financial data types detected in the incident, triggering PCI DSS compliance obligations.",
                severity=RiskLevel.CRITICAL,
                regulations=[Regulation(name="PCI DSS", section="Requirement 3, 12.10", description="Cardholder data protection and incident response", applicable=True, severity=RiskLevel.CRITICAL)],
                recommendation="Notify payment card brands within 24 hours. Engage PCI QSA. Assess scope of cardholder data exposure per PCI DSS Requirement 3.",
                reasoning="PCI DSS Requirement 12.10 mandates an immediate incident response. Exposure of card data triggers notification to acquiring banks and card brands.",
            ).model_dump())

        return findings

    def _calculate_privacy_score(self, description: str, pii: list, special: list) -> int:
        score = 100
        score -= len(pii) * 8
        score -= len(special) * 15
        if any(kw in description for kw in ["exposed", "public", "breach", "leaked"]):
            score -= 25
        return max(0, score)
