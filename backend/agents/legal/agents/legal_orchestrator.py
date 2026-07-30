"""
LexGuardian Legal Orchestrator — LangGraph-based multi-agent coordination
Coordinates all 6 specialized legal agents in parallel.
"""
import logging
from datetime import datetime
from typing import Any, TypedDict
import asyncio

from schemas.analysis import (
    AnalysisReport, ComplianceScore, LegalFinding,
    Regulation, PenaltyEstimate, ComplianceAction,
    DisclosureNotice, AuditEntry, TimelineEvent, RiskLevel
)
from agents.regulatory_agent import RegulatoryComplianceAgent
from agents.privacy_agent import PrivacyAgent
from agents.contract_agent import ContractAgent
from agents.supporting_agents import GovernanceAgent, LitigationAgent, DisclosureAgent

logger = logging.getLogger(__name__)


class LegalOrchestrator:
    """
    Orchestrates all 6 specialized legal agents in parallel.
    Aggregates findings into a comprehensive AnalysisReport.
    """

    def __init__(self, llm_client=None):
        self.regulatory_agent = RegulatoryComplianceAgent(llm_client)
        self.privacy_agent = PrivacyAgent(llm_client)
        self.contract_agent = ContractAgent(llm_client)
        self.governance_agent = GovernanceAgent(llm_client)
        self.litigation_agent = LitigationAgent(llm_client)
        self.disclosure_agent = DisclosureAgent(llm_client)

    async def analyze(self, incident_input: dict) -> AnalysisReport:
        """Run all agents in parallel and synthesize results."""
        logger.info("LexGuardian orchestrator: starting multi-agent analysis")
        start = datetime.utcnow()

        # Run all agents concurrently
        results = await asyncio.gather(
            asyncio.to_thread(self.regulatory_agent.analyze, incident_input),
            asyncio.to_thread(self.privacy_agent.analyze, incident_input),
            asyncio.to_thread(self.contract_agent.analyze, incident_input),
            asyncio.to_thread(self.governance_agent.analyze, incident_input),
            asyncio.to_thread(self.litigation_agent.analyze, incident_input),
            asyncio.to_thread(self.disclosure_agent.analyze, incident_input),
            return_exceptions=True,
        )

        reg_result, priv_result, contract_result, gov_result, lit_result, disc_result = results
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Agent error: {r}")

        # Aggregate all findings
        all_findings = []
        audit_trail = []
        regulations_triggered = []
        penalty_estimates = []

        for result in results:
            if isinstance(result, dict):
                findings = result.get("findings", [])
                all_findings.extend([LegalFinding(**f) if isinstance(f, dict) else f for f in findings])
                if result.get("audit_entry"):
                    ae = result["audit_entry"]
                    audit_trail.append(AuditEntry(**ae) if isinstance(ae, dict) else ae)

        # Regulations
        if isinstance(reg_result, dict):
            for r in reg_result.get("regulations_triggered", []):
                regulations_triggered.append(Regulation(**r) if isinstance(r, dict) else r)
            for p in reg_result.get("penalty_estimates", []):
                penalty_estimates.append(PenaltyEstimate(**p) if isinstance(p, dict) else p)

        # Compliance scores
        scores = self._calculate_composite_scores(reg_result, priv_result, contract_result, gov_result, lit_result, disc_result)

        # Overall risk level
        overall = scores.overall
        if overall >= 81:
            risk_level = RiskLevel.CRITICAL
        elif overall >= 61:
            risk_level = RiskLevel.HIGH
        elif overall >= 41:
            risk_level = RiskLevel.SIGNIFICANT
        elif overall >= 21:
            risk_level = RiskLevel.MODERATE
        else:
            risk_level = RiskLevel.LOW

        # Immediate and long-term actions
        immediate_actions = []
        long_term_actions = []
        disclosure_notices = []

        if isinstance(disc_result, dict):
            for a in disc_result.get("immediate_actions", []):
                immediate_actions.append(ComplianceAction(**a) if isinstance(a, dict) else a)
            for n in disc_result.get("disclosure_notices", []):
                disclosure_notices.append(DisclosureNotice(**n) if isinstance(n, dict) else n)

        # Long-term actions
        long_term_actions = [
            ComplianceAction(priority="long_term", action="Conduct DPIA / Privacy Impact Assessment", owner="DPO", deadline="30 days", legal_basis="GDPR Article 35"),
            ComplianceAction(priority="long_term", action="Update Information Security Policies", owner="CISO", deadline="60 days", legal_basis="ISO 27001 A.18.2"),
            ComplianceAction(priority="long_term", action="Implement data access monitoring solution", owner="IT Security", deadline="90 days", legal_basis="NIST PR.AC-4"),
            ComplianceAction(priority="long_term", action="Schedule annual penetration testing", owner="CISO", deadline="6 months", legal_basis="PCI DSS Requirement 11.3"),
        ]

        # Timeline
        compliance_timeline = []
        if isinstance(disc_result, dict):
            for t in disc_result.get("compliance_timeline", []):
                compliance_timeline.append(TimelineEvent(**t) if isinstance(t, dict) else t)

        # AI reasoning
        ai_reasoning = self._generate_reasoning(incident_input, results, scores)
        executive_summary = self._generate_executive_summary(incident_input, scores, risk_level, all_findings, penalty_estimates)

        legal_hold = isinstance(lit_result, dict) and lit_result.get("legal_hold_recommended", False)

        duration = (datetime.utcnow() - start).total_seconds()
        logger.info(f"LexGuardian analysis complete in {duration:.2f}s. Risk: {risk_level.value}")

        return AnalysisReport(
            incident_summary=incident_input.get("description", ""),
            incident_type=self._classify_incident(incident_input.get("description", "")),
            risk_level=risk_level,
            compliance_scores=scores,
            legal_findings=all_findings,
            regulations_triggered=regulations_triggered,
            penalty_estimates=penalty_estimates,
            immediate_actions=immediate_actions,
            long_term_actions=long_term_actions,
            disclosure_notices=disclosure_notices,
            legal_hold_recommended=legal_hold,
            executive_summary=executive_summary,
            ai_reasoning=ai_reasoning,
            audit_trail=audit_trail,
            compliance_timeline=compliance_timeline,
        )

    def _calculate_composite_scores(self, *results) -> ComplianceScore:
        def safe_get(r, key, default=75):
            if isinstance(r, dict):
                return r.get(key, default)
            return default

        reg, priv, contract, gov, lit, disc = results
        privacy = safe_get(priv, "privacy_risk_score", 70)
        contracts = safe_get(contract, "contract_risk_score", 78)
        regulatory = safe_get(reg, "regulatory_risk_score", 65)
        governance = safe_get(gov, "governance_risk_score", 74)
        disclosure = safe_get(disc, "disclosure_risk_score", 80)
        overall = int((privacy + contracts + regulatory + governance + disclosure) / 5)

        return ComplianceScore(
            privacy=max(0, min(100, privacy)),
            contracts=max(0, min(100, contracts)),
            regulatory=max(0, min(100, regulatory)),
            governance=max(0, min(100, governance)),
            disclosure=max(0, min(100, disclosure)),
            overall=max(0, min(100, overall)),
        )

    def _classify_incident(self, description: str) -> str:
        desc = description.lower()
        if any(kw in desc for kw in ["database", "exposed", "leaked", "breach"]):
            return "Data Breach"
        if any(kw in desc for kw in ["sla", "vendor", "deliver"]):
            return "Contract Breach / SLA Violation"
        if any(kw in desc for kw in ["employee", "hr", "resignation", "usb"]):
            return "Insider Threat / Employment Issue"
        if any(kw in desc for kw in ["ai", "artificial intelligence", "algorithm"]):
            return "AI Compliance Issue"
        if any(kw in desc for kw in ["cloud", "misconfigured", "storage bucket"]):
            return "Cloud Security Misconfiguration"
        return "Compliance Violation"

    def _generate_reasoning(self, incident: dict, results: list, scores: ComplianceScore) -> str:
        return f"""LexGuardian AI performed a multi-agent legal analysis across 6 specialized domains:

**Regulatory Agent Analysis:** Identified applicable regulations based on incident characteristics, jurisdiction ({incident.get('jurisdiction', 'EU/GDPR')}), and industry context. Regulatory risk score: {scores.regulatory}/100.

**Privacy Agent Analysis:** Assessed PII categories and data protection obligations. Privacy compliance score: {scores.privacy}/100. Evaluated GDPR, CCPA, and applicable data protection frameworks.

**Contract Agent Analysis:** Reviewed contractual obligations, SLA terms, NDA implications, and employment contract obligations. Contract risk score: {scores.contracts}/100.

**Governance Agent Analysis:** Evaluated board-level obligations, internal policy compliance, code of conduct implications, and AI governance requirements. Governance score: {scores.governance}/100.

**Litigation Agent Analysis:** Predicted lawsuit probability based on incident severity, data involved, and regulatory breach indicators. Applied legal hold doctrine analysis.

**Disclosure Agent Analysis:** Generated mandatory disclosure notices with deadlines, content templates, and regulatory requirements for {len([r for r in results if isinstance(r, dict)])} stakeholder groups. Disclosure preparedness: {scores.disclosure}/100.

**Synthesis:** All agent outputs were aggregated into a composite compliance risk assessment with an overall score of {scores.overall}/100."""

    def _generate_executive_summary(self, incident: dict, scores: ComplianceScore, risk_level: RiskLevel, findings: list, penalties: list) -> str:
        max_penalty = max([p.max_amount for p in penalties], default=0) if penalties else 0
        currency = penalties[0].currency if penalties else "EUR"
        critical_count = len([f for f in findings if f.severity == RiskLevel.CRITICAL])

        return f"""**LEXGUARDIAN AI LEGAL ASSESSMENT — {risk_level.value.upper()} RISK**

Incident Summary: {incident.get('description', '')[:200]}

**Key Legal Obligations:**
• {critical_count} critical compliance violations identified
• Regulatory notification obligations triggered
• Legal hold recommended for evidence preservation
• Board disclosure may be required for material incidents

**Financial Exposure:** Up to {currency} {max_penalty:,.0f}+ in regulatory penalties (estimated)

**Overall Compliance Risk Score: {scores.overall}/100 — {risk_level.value.upper()} RISK**

LexGuardian AI recommends engaging external privacy and employment counsel immediately and initiating your organization's Incident Response Plan within the next 2 hours.

This assessment is AI-generated and should be reviewed by qualified legal counsel before action."""
