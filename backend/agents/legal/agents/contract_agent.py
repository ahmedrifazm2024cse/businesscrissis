"""
LexGuardian Contract Analysis Agent
Analyzes SLA breaches, NDA violations, vendor agreements, employment contracts
"""
import logging
from datetime import datetime
from schemas.analysis import LegalFinding, Regulation, RiskLevel, AuditEntry

logger = logging.getLogger(__name__)


class ContractAgent:
    """Agent for contract breach detection and liability analysis."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.name = "Contract Agent"

    def analyze(self, incident: dict) -> dict:
        logger.info(f"[{self.name}] Starting contract analysis")
        start = datetime.utcnow()
        description = incident.get("description", "").lower()

        contract_issues = self._detect_contract_issues(description)
        findings = self._generate_findings(description, contract_issues)
        risk_score = self._calculate_contract_score(description, contract_issues)

        duration = (datetime.utcnow() - start).total_seconds()
        logger.info(f"[{self.name}] Contract issues detected: {contract_issues}")

        return {
            "agent": self.name,
            "contract_issues": contract_issues,
            "findings": findings,
            "contract_risk_score": risk_score,
            "audit_entry": AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                agent=self.name,
                action="Contract Liability Analysis",
                details=f"Identified contract issues: {', '.join(contract_issues) if contract_issues else 'None detected'}",
            ).model_dump(),
        }

    def _detect_contract_issues(self, description: str) -> list:
        issues = []
        issue_keywords = {
            "SLA Breach": ["sla", "service level", "uptime", "availability", "delivery", "failed to deliver", "delayed"],
            "NDA Violation": ["confidential", "trade secret", "proprietary", "nda", "non-disclosure"],
            "Employment Violation": ["employee", "employment", "hr", "resignation", "termination", "contractor"],
            "Vendor Non-Performance": ["vendor", "supplier", "third-party", "outsource", "partner"],
            "Data Processor Breach": ["data processor", "cloud provider", "saas", "hosting", "misconfigured"],
        }
        for issue, keywords in issue_keywords.items():
            if any(kw in description for kw in keywords):
                issues.append(issue)
        return issues

    def _generate_findings(self, description: str, issues: list) -> list:
        findings = []
        if "SLA Breach" in issues:
            findings.append(LegalFinding(
                category="Contract Law",
                title="Service Level Agreement (SLA) Breach Detected",
                description="Vendor/service provider failed to meet contractual SLA obligations, creating legal exposure for damages and potential termination rights.",
                severity=RiskLevel.HIGH,
                regulations=[Regulation(name="Common Law", article="Breach of Contract", description="General contract breach doctrine — right to damages, rescission, or specific performance", applicable=True, severity=RiskLevel.HIGH)],
                recommendation="Review SLA terms for express remedies (service credits, penalty clauses, termination triggers). Issue formal written notice of breach. Preserve all evidence of non-performance.",
                reasoning="A breach of SLA constitutes a breach of contract under general common law principles. The non-breaching party is entitled to damages that flow naturally from the breach (Hadley v Baxendale test).",
            ).model_dump())

        if "Employment Violation" in issues:
            findings.append(LegalFinding(
                category="Employment Law",
                title="Employment Policy and Data Security Breach",
                description="Employee action appears to violate employment contract terms around data security obligations and acceptable use of company systems.",
                severity=RiskLevel.HIGH,
                regulations=[
                    Regulation(name="Employment Contract", article="Data Security Obligations", description="Contractual duty of confidentiality and data protection", applicable=True, severity=RiskLevel.HIGH),
                    Regulation(name="GDPR", article="Article 32", description="Employee data handling obligations as part of organizational security", applicable=True, severity=RiskLevel.SIGNIFICANT),
                ],
                recommendation="Issue legal hold notice to preserve employee records. Conduct internal investigation. Review NDA and employment terms for remedies. Consider civil action for breach of confidence.",
                reasoning="Employees owe a duty of confidentiality both under express contract terms and implied by law (Faccenda Chicken Ltd v Fowler). Unauthorized data exfiltration may constitute conversion and breach of fiduciary duty.",
            ).model_dump())

        return findings

    def _calculate_contract_score(self, description: str, issues: list) -> int:
        score = 100
        score -= len(issues) * 10
        if any(kw in description for kw in ["breach", "failed", "violated", "unauthorized"]):
            score -= 15
        return max(0, score)
