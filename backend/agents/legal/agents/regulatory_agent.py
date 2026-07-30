"""
LexGuardian Regulatory Compliance Agent
Analyzes incidents against GDPR, HIPAA, PCI DSS, CCPA, ISO 27001, NIST, DPDP, SOC 2, EU AI Act
"""
import logging
from typing import Any
from datetime import datetime

from schemas.analysis import (
    LegalFinding, Regulation, PenaltyEstimate, RiskLevel,
    ComplianceAction, AuditEntry
)

logger = logging.getLogger(__name__)

REGULATIONS_DB = {
    "GDPR": {
        "full_name": "General Data Protection Regulation",
        "jurisdiction": ["EU", "EEA", "UK"],
        "applies_to": ["personal_data", "data_breach", "privacy", "consent"],
        "key_articles": {
            "Article 5": "Principles of data processing",
            "Article 17": "Right to erasure",
            "Article 25": "Privacy by design and default",
            "Article 33": "72-hour breach notification to supervisory authority",
            "Article 34": "Communication of breach to data subjects",
            "Article 35": "Data Protection Impact Assessment (DPIA)",
            "Article 83": "General conditions for imposing fines",
        },
        "max_penalty": 20_000_000,
        "penalty_basis": "4% of global annual turnover or €20M, whichever is higher",
        "penalty_currency": "EUR",
    },
    "CCPA": {
        "full_name": "California Consumer Privacy Act",
        "jurisdiction": ["USA", "California"],
        "applies_to": ["personal_data", "data_breach", "privacy", "consumer_rights"],
        "key_articles": {
            "Section 1798.82": "Breach notification requirements",
            "Section 1798.100": "Consumer right to know",
            "Section 1798.150": "Private right of action for data breaches",
        },
        "max_penalty": 7500,
        "penalty_basis": "Per intentional violation; $2,500 per unintentional violation",
        "penalty_currency": "USD",
    },
    "HIPAA": {
        "full_name": "Health Insurance Portability and Accountability Act",
        "jurisdiction": ["USA"],
        "applies_to": ["healthcare", "medical", "health_data", "PHI"],
        "key_articles": {
            "45 CFR §164.400": "Breach notification requirements",
            "45 CFR §164.502": "Uses and disclosures of PHI",
            "45 CFR §164.530": "Administrative requirements",
        },
        "max_penalty": 1_900_000,
        "penalty_basis": "Per violation category per year; up to $1.9M per violation type",
        "penalty_currency": "USD",
    },
    "PCI_DSS": {
        "full_name": "Payment Card Industry Data Security Standard",
        "jurisdiction": ["Global"],
        "applies_to": ["payment_data", "credit_card", "financial_data"],
        "key_articles": {
            "Requirement 12.10": "Incident response plan",
            "Requirement 3": "Protect stored cardholder data",
            "Requirement 6": "Develop and maintain secure systems",
            "Requirement 11": "Test security systems and processes",
        },
        "max_penalty": 100_000,
        "penalty_basis": "USD $5,000–$100,000 per month until compliance restored",
        "penalty_currency": "USD",
    },
    "ISO_27001": {
        "full_name": "ISO/IEC 27001 Information Security Management",
        "jurisdiction": ["Global"],
        "applies_to": ["information_security", "data_breach", "risk_management"],
        "key_articles": {
            "A.16.1.5": "Response to information security incidents",
            "A.16.1.6": "Learning from information security incidents",
            "A.18.2": "Information security compliance",
        },
        "max_penalty": 0,
        "penalty_basis": "Certification loss — operational and contractual impact",
        "penalty_currency": "USD",
    },
    "NIST": {
        "full_name": "NIST Cybersecurity Framework",
        "jurisdiction": ["USA", "Global"],
        "applies_to": ["cybersecurity", "information_security", "critical_infrastructure"],
        "key_articles": {
            "IR-6": "Incident reporting",
            "IR-4": "Incident handling",
            "AC-2": "Account management",
        },
        "max_penalty": 0,
        "penalty_basis": "Regulatory framework — agency-specific penalties may apply",
        "penalty_currency": "USD",
    },
    "SOC2": {
        "full_name": "SOC 2 Type II Compliance",
        "jurisdiction": ["USA", "Global"],
        "applies_to": ["cloud_services", "data_security", "availability"],
        "key_articles": {
            "CC7.4": "Security incident response",
            "CC7.3": "Identified security events evaluated",
            "CC9.2": "Business disruption and vendor risk",
        },
        "max_penalty": 0,
        "penalty_basis": "Audit failure — impact on customer contracts and certifications",
        "penalty_currency": "USD",
    },
    "DPDP": {
        "full_name": "Digital Personal Data Protection Act (India)",
        "jurisdiction": ["India"],
        "applies_to": ["personal_data", "data_breach", "indian_citizens"],
        "key_articles": {
            "Section 8": "Obligations of Data Fiduciary",
            "Section 9": "Processing of personal data of children",
            "Section 33": "Penalties",
        },
        "max_penalty": 500_000_000,
        "penalty_basis": "Up to INR 250 crore per breach",
        "penalty_currency": "INR",
    },
    "EU_AI_ACT": {
        "full_name": "EU Artificial Intelligence Act",
        "jurisdiction": ["EU", "EEA"],
        "applies_to": ["ai_system", "machine_learning", "automated_decision"],
        "key_articles": {
            "Article 6": "Classification rules for high-risk AI systems",
            "Article 9": "Risk management system",
            "Article 13": "Transparency and provision of information",
            "Article 43": "Conformity assessment",
        },
        "max_penalty": 35_000_000,
        "penalty_basis": "€35M or 7% of global annual turnover for prohibited AI",
        "penalty_currency": "EUR",
    },
}


class RegulatoryComplianceAgent:
    """Agent responsible for mapping incidents to applicable regulations and calculating compliance risk."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Regulatory Agent"

    def analyze(self, incident: dict) -> dict:
        """Perform full regulatory analysis on an incident."""
        logger.info(f"[{self.name}] Starting regulatory analysis")
        start = datetime.utcnow()

        description = incident.get("description", "").lower()
        jurisdiction = incident.get("jurisdiction", "EU / GDPR")
        industry = incident.get("industry", "")

        triggered_regulations = self._detect_applicable_regulations(description, jurisdiction, industry)
        findings = self._generate_findings(description, triggered_regulations)
        penalties = self._estimate_penalties(triggered_regulations, description)
        risk_score = self._calculate_risk_score(triggered_regulations, description)

        duration = (datetime.utcnow() - start).total_seconds()
        logger.info(f"[{self.name}] Completed in {duration:.2f}s — {len(triggered_regulations)} regulations triggered")

        return {
            "agent": self.name,
            "regulations_triggered": triggered_regulations,
            "findings": findings,
            "penalty_estimates": penalties,
            "regulatory_risk_score": risk_score,
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="Regulatory Mapping",
                details=f"Identified {len(triggered_regulations)} applicable regulations: {', '.join([r['name'] for r in triggered_regulations])}",
            ).model_dump(),
        }

    def _detect_applicable_regulations(self, description: str, jurisdiction: str, industry: str) -> list:
        """Map incident keywords to applicable regulations."""
        applicable = []
        keywords_map = {
            "GDPR": ["personal data", "email", "phone", "customer", "user data", "pii", "exposed", "breach", "database", "privacy"],
            "CCPA": ["california", "consumer", "customer data", "ccpa", "personal information"],
            "HIPAA": ["medical", "health", "patient", "phi", "hospital", "healthcare", "clinical"],
            "PCI_DSS": ["payment", "credit card", "card data", "financial", "invoice", "billing", "pci"],
            "ISO_27001": ["security", "breach", "incident", "risk", "access control", "unauthorized"],
            "NIST": ["cybersecurity", "network", "system", "infrastructure", "hack"],
            "SOC2": ["cloud", "saas", "service provider", "vendor", "availability", "audit"],
            "DPDP": ["india", "indian", "dpdp"],
            "EU_AI_ACT": ["ai", "artificial intelligence", "machine learning", "algorithm", "automated", "recruitment", "hiring"],
        }

        for reg_key, keywords in keywords_map.items():
            if any(kw in description for kw in keywords):
                reg_data = REGULATIONS_DB[reg_key]
                # Determine severity based on regulation and context
                severity = self._get_severity(reg_key, description)
                applicable.append({
                    "name": reg_key.replace("_", " "),
                    "article": list(reg_data["key_articles"].keys())[0] if reg_data["key_articles"] else None,
                    "section": None,
                    "description": list(reg_data["key_articles"].values())[0] if reg_data["key_articles"] else reg_data["full_name"],
                    "applicable": True,
                    "severity": severity,
                })

        return applicable

    def _get_severity(self, reg_key: str, description: str) -> str:
        high_severity_regs = ["GDPR", "HIPAA", "PCI_DSS", "EU_AI_ACT"]
        if reg_key in high_severity_regs:
            if any(kw in description for kw in ["exposed", "breach", "leaked", "unauthorized", "public"]):
                return RiskLevel.CRITICAL.value
            return RiskLevel.HIGH.value
        return RiskLevel.SIGNIFICANT.value

    def _generate_findings(self, description: str, regulations: list) -> list:
        findings = []
        if any(r["name"] == "GDPR" for r in regulations):
            findings.append(LegalFinding(
                category="Data Protection",
                title="GDPR Mandatory Breach Notification Obligation",
                description="Personal data breach detected triggering mandatory 72-hour notification obligation to supervisory authority under GDPR Article 33.",
                severity=RiskLevel.CRITICAL,
                regulations=[Regulation(name="GDPR", article="Article 33-34", description="72-hour DPA notification and data subject communication requirement", applicable=True, severity=RiskLevel.CRITICAL)],
                recommendation="Notify the Data Protection Authority immediately. Prepare Article 33 notification including nature of breach, data categories, approximate number of individuals, and remedial measures taken.",
                reasoning="GDPR Article 33 mandates notification without undue delay and where feasible within 72 hours. Failure to notify can result in administrative fines of up to €10M or 2% of global annual turnover under Article 83(4).",
            ).model_dump())
        return findings

    def _estimate_penalties(self, regulations: list, description: str) -> list:
        estimates = []
        for reg in regulations:
            reg_name = reg["name"].replace(" ", "_")
            if reg_name in REGULATIONS_DB:
                db_entry = REGULATIONS_DB[reg_name]
                if db_entry["max_penalty"] > 0:
                    estimates.append(PenaltyEstimate(
                        regulation=reg["name"],
                        min_amount=db_entry["max_penalty"] * 0.01,
                        max_amount=float(db_entry["max_penalty"]),
                        currency=db_entry["penalty_currency"],
                        basis=db_entry["penalty_basis"],
                    ).model_dump())
        return estimates

    def _calculate_risk_score(self, regulations: list, description: str) -> int:
        base_score = min(100, len(regulations) * 12)
        if any(kw in description for kw in ["exposed", "public", "breach", "unauthorized"]):
            base_score = min(100, base_score + 20)
        return max(0, 100 - base_score)
