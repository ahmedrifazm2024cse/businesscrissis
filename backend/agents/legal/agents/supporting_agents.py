"""
LexGuardian Governance, Litigation, and Disclosure Agents
"""
import logging
from datetime import datetime, timedelta
from schemas.analysis import LegalFinding, Regulation, RiskLevel, AuditEntry, DisclosureNotice, ComplianceAction

logger = logging.getLogger(__name__)


class GovernanceAgent:
    """Corporate governance and internal policy compliance agent."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Governance Agent"

    def analyze(self, incident: dict) -> dict:
        logger.info(f"[{self.name}] Starting governance analysis")
        description = incident.get("description", "").lower()

        findings = self._generate_findings(description)
        risk_score = self._calculate_score(description)

        return {
            "agent": self.name,
            "findings": findings,
            "governance_risk_score": risk_score,
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="Governance Assessment",
                details=f"Evaluated board obligations, ethics policies, and internal compliance requirements. Score: {risk_score}/100",
            ).model_dump(),
        }

    def _generate_findings(self, description: str) -> list:
        findings = []
        if any(kw in description for kw in ["employee", "hr", "insider", "resignation"]):
            findings.append(LegalFinding(
                category="Corporate Governance",
                title="Internal Policy Violation — Insider Threat",
                description="An employee action appears to violate internal data handling policies, code of conduct, and acceptable use policies.",
                severity=RiskLevel.HIGH,
                regulations=[
                    Regulation(name="SOC 2", section="CC9.1", description="Risk assessment for insider threats", applicable=True, severity=RiskLevel.SIGNIFICANT),
                    Regulation(name="ISO 27001", section="A.7.2.3", description="Disciplinary process for security policy violations", applicable=True, severity=RiskLevel.SIGNIFICANT),
                ],
                recommendation="Conduct formal internal investigation per disciplinary procedures. Brief Audit Committee. Preserve evidence per legal hold. Update insider threat controls.",
                reasoning="Insider data theft triggers multiple governance obligations including board notification for material incidents, HR disciplinary process, and potential criminal referral under applicable computer fraud statutes.",
            ).model_dump())

        if any(kw in description for kw in ["ai", "artificial intelligence", "algorithm", "model", "automated decision"]):
            findings.append(LegalFinding(
                category="AI Governance",
                title="AI System Deployed Without Formal Risk Assessment",
                description="AI system deployment without documented risk assessment violates EU AI Act obligations and internal governance frameworks.",
                severity=RiskLevel.HIGH,
                regulations=[
                    Regulation(name="EU AI Act", article="Article 9", description="Risk management system required for high-risk AI", applicable=True, severity=RiskLevel.HIGH),
                    Regulation(name="EU AI Act", article="Article 13", description="Transparency and information provision requirements", applicable=True, severity=RiskLevel.SIGNIFICANT),
                ],
                recommendation="Immediately suspend AI system pending risk assessment. Conduct DPIA if personal data is processed. Prepare EU AI Act conformity documentation.",
                reasoning="The EU AI Act classifies AI systems used in employment (e.g., recruitment, promotion) as HIGH-RISK under Annex III. Article 9 requires a documented risk management system before deployment.",
            ).model_dump())

        return findings

    def _calculate_score(self, description: str) -> int:
        score = 80
        if any(kw in description for kw in ["no risk assessment", "without assessment", "undocumented"]):
            score -= 25
        if any(kw in description for kw in ["employee", "insider"]):
            score -= 10
        return max(0, score)


class LitigationAgent:
    """Litigation risk prediction and evidence preservation agent."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Litigation Agent"

    def analyze(self, incident: dict) -> dict:
        logger.info(f"[{self.name}] Starting litigation risk analysis")
        description = incident.get("description", "").lower()

        lawsuit_prob = self._estimate_lawsuit_probability(description)
        legal_hold = self._recommend_legal_hold(description)
        findings = self._generate_findings(description, lawsuit_prob)

        return {
            "agent": self.name,
            "lawsuit_probability": lawsuit_prob,
            "legal_hold_recommended": legal_hold,
            "findings": findings,
            "litigation_risk_score": 100 - int(lawsuit_prob * 100),
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="Litigation Risk Prediction",
                details=f"Lawsuit probability: {lawsuit_prob:.0%}. Legal hold recommended: {legal_hold}",
            ).model_dump(),
        }

    def _estimate_lawsuit_probability(self, description: str) -> float:
        prob = 0.1
        if any(kw in description for kw in ["exposed", "breach", "leaked", "public"]):
            prob += 0.4
        if any(kw in description for kw in ["payment", "financial", "medical", "health"]):
            prob += 0.2
        if any(kw in description for kw in ["employee", "hr", "discrimination"]):
            prob += 0.15
        if any(kw in description for kw in ["hospital", "patient", "clinical"]):
            prob += 0.2
        return min(1.0, prob)

    def _recommend_legal_hold(self, description: str) -> bool:
        hold_triggers = ["breach", "exposed", "leaked", "employee", "resigned", "lawsuit", "investigation"]
        return any(kw in description for kw in hold_triggers)

    def _generate_findings(self, description: str, prob: float) -> list:
        findings = []
        if prob >= 0.4:
            findings.append(LegalFinding(
                category="Litigation Risk",
                title="Elevated Lawsuit Probability",
                description=f"LexGuardian AI estimates {prob:.0%} probability of regulatory investigation or civil litigation based on incident characteristics.",
                severity=RiskLevel.HIGH if prob >= 0.6 else RiskLevel.SIGNIFICANT,
                regulations=[Regulation(name="Evidence Law", article="Legal Hold Doctrine", description="Preservation of evidence obligation triggered by reasonably anticipated litigation", applicable=True, severity=RiskLevel.HIGH)],
                recommendation="Issue immediate legal hold notice. Suspend auto-deletion policies. Engage external litigation counsel. Document all incident response steps.",
                reasoning=f"Based on incident analysis, factors indicating {prob:.0%} litigation probability include: data breach scope, regulatory breaches, and affected party characteristics. The duty to preserve evidence arises when litigation is reasonably anticipated.",
            ).model_dump())
        return findings


class DisclosureAgent:
    """Disclosure notice generation and regulatory filing agent."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Disclosure Agent"

    def analyze(self, incident: dict) -> dict:
        logger.info(f"[{self.name}] Generating disclosure notices")
        description = incident.get("description", "").lower()
        jurisdiction = incident.get("jurisdiction", "EU / GDPR")

        notices = self._generate_notices(description, jurisdiction)
        immediate_actions = self._generate_immediate_actions(description, jurisdiction)
        timeline = self._generate_timeline()
        risk_score = 80 if notices else 95

        return {
            "agent": self.name,
            "disclosure_notices": notices,
            "immediate_actions": immediate_actions,
            "compliance_timeline": timeline,
            "disclosure_risk_score": risk_score,
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="Disclosure Notice Generation",
                details=f"Generated {len(notices)} disclosure notices across {len(set(n['audience'] for n in notices))} stakeholder groups",
            ).model_dump(),
        }

    def _generate_notices(self, description: str, jurisdiction: str) -> list:
        notices = []
        now = datetime.utcnow()

        if any(kw in description for kw in ["exposed", "breach", "leaked", "unauthorized", "database", "customer"]):
            notices.append(DisclosureNotice(
                type="Regulatory Filing",
                audience="Data Protection Authority (DPA)",
                deadline=f"Within 72 hours ({(now + timedelta(hours=72)).strftime('%Y-%m-%d %H:%M')} UTC)",
                content="""GDPR Article 33 Breach Notification

Nature of breach: Unauthorized access to personal data
Categories of data: Names, email addresses, phone numbers, financial data
Approximate number of individuals affected: Under investigation
Likely consequences: Financial loss, identity theft, reputational harm
Remedial action taken: Access contained, forensic investigation initiated, affected systems isolated

Contact: [DPO Name and Contact Details]""",
                regulatory_requirement="GDPR Article 33",
            ).model_dump())

            notices.append(DisclosureNotice(
                type="Customer Notification",
                audience="Affected Data Subjects",
                deadline=f"Within 7 days ({(now + timedelta(days=7)).strftime('%Y-%m-%d')})",
                content="""Dear [Customer Name],

Notice of Data Security Incident

We are writing to inform you that we recently discovered a security incident that may have affected some of your personal information.

What happened: [Brief description of incident]
What information was involved: [Data categories]
What we are doing: We immediately contained the issue and are working with security experts to investigate.
What you can do: Monitor your accounts for suspicious activity. Consider placing a fraud alert.

We sincerely apologize for any concern this may cause. Please contact our privacy team at [email] with any questions.

[Company Name] Privacy Team""",
                regulatory_requirement="GDPR Article 34 / CCPA Section 1798.82",
            ).model_dump())

        return notices

    def _generate_immediate_actions(self, description: str, jurisdiction: str) -> list:
        actions = []
        now = datetime.utcnow()

        actions.append(ComplianceAction(
            priority="immediate",
            action="Contain the incident and revoke unauthorized access",
            owner="CISO / IT Security Team",
            deadline="Within 2 hours",
            legal_basis="GDPR Article 32 — Security of processing",
        ).model_dump())

        if any(kw in description for kw in ["exposed", "breach", "leaked", "database"]):
            actions.append(ComplianceAction(
                priority="immediate",
                action="Notify Data Protection Authority (DPA) — 72-hour GDPR deadline",
                owner="Data Protection Officer (DPO) / Legal",
                deadline=f"By {(now + timedelta(hours=72)).strftime('%Y-%m-%d %H:%M')} UTC",
                legal_basis="GDPR Article 33 — Controller obligations for breach notification",
            ).model_dump())

        actions.append(ComplianceAction(
            priority="immediate",
            action="Issue Legal Hold notice — preserve all electronic evidence",
            owner="General Counsel / Legal Team",
            deadline="Within 24 hours",
            legal_basis="Duty to preserve evidence for reasonably anticipated litigation",
        ).model_dump())

        actions.append(ComplianceAction(
            priority="immediate",
            action="Commission independent forensic investigation",
            owner="CISO + External Forensic Firm",
            deadline="Within 4 hours",
            legal_basis="Best evidence preservation practice / regulatory expectation",
        ).model_dump())

        return actions

    def _generate_timeline(self) -> list:
        now = datetime.utcnow()
        return [
            {"date": now.isoformat(), "event": "Incident Discovered & Initial Containment", "type": "incident", "status": "completed"},
            {"date": (now + timedelta(hours=2)).isoformat(), "event": "Forensic Investigation Initiated", "type": "action", "status": "pending"},
            {"date": (now + timedelta(hours=24)).isoformat(), "event": "Internal Legal Hold Issued", "type": "action", "status": "pending"},
            {"date": (now + timedelta(hours=72)).isoformat(), "event": "GDPR DPA Notification Deadline", "type": "deadline", "status": "pending"},
            {"date": (now + timedelta(days=5)).isoformat(), "event": "Board of Directors Briefing", "type": "action", "status": "pending"},
            {"date": (now + timedelta(days=7)).isoformat(), "event": "Affected Data Subject Notification Deadline", "type": "notification", "status": "pending"},
            {"date": (now + timedelta(days=30)).isoformat(), "event": "DPIA Completion", "type": "filing", "status": "pending"},
            {"date": (now + timedelta(days=60)).isoformat(), "event": "Remediation Plan Implementation", "type": "action", "status": "pending"},
        ]
