"""
LexGuardian AI — Enterprise Legal & Compliance Intelligence
FastAPI + MongoDB backend — fully self-contained, no external AI APIs required.
All 6 legal agents run locally with rule-based + template reasoning.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# ─── Load env ────────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lexguardian")


# ─── Settings ────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "lexguardian"
    port: int = 8003

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()


# ─── Schemas ─────────────────────────────────────────────────────────────────
class IncidentInput(BaseModel):
    description: str = Field(..., min_length=10)
    jurisdiction: str = "EU / GDPR"
    industry: str = ""
    incident_type: Optional[str] = None
    affected_systems: list[str] = []
    affected_data_types: list[str] = []
    company_size: str = ""
    api_key: Optional[str] = None


# ─── Regulation Database ─────────────────────────────────────────────────────
REGS_DB: dict[str, dict] = {
    "GDPR": {
        "full": "General Data Protection Regulation",
        "jurisdiction": "EU/EEA",
        "keywords": ["personal data", "email", "phone", "customer", "user", "pii",
                     "exposed", "breach", "database", "privacy", "name", "address"],
        "article": "Art. 33-34",
        "desc": "72-hour breach notification to supervisory authority + data subject communication",
        "penalty_max": 1800000000,
        "penalty_basis": "Up to INR 180 Crore or 4% of global annual turnover",
        "currency": "INR",
        "base_severity": "critical",
    },
    "CCPA": {
        "full": "California Consumer Privacy Act",
        "jurisdiction": "USA/California",
        "keywords": ["california", "consumer", "customer data", "ccpa", "personal information"],
        "article": "§1798.82",
        "desc": "California breach notification within 30 days; private right of action",
        "penalty_max": 625000,
        "penalty_basis": "INR 6.25 Lakhs per intentional violation / INR 2 Lakhs per unintentional",
        "currency": "INR",
        "base_severity": "high",
    },
    "HIPAA": {
        "full": "Health Insurance Portability and Accountability Act",
        "jurisdiction": "USA",
        "keywords": ["medical", "health", "patient", "phi", "hospital", "healthcare", "clinical", "nurse", "doctor"],
        "article": "45 CFR §164.400",
        "desc": "Breach notification to HHS and affected individuals within 60 days",
        "penalty_max": 150000000,
        "penalty_basis": "Up to INR 15 Crore per violation category per year",
        "currency": "INR",
        "base_severity": "critical",
    },
    "PCI DSS": {
        "full": "Payment Card Industry Data Security Standard",
        "jurisdiction": "Global",
        "keywords": ["payment", "credit card", "card data", "financial", "invoice", "billing", "pci", "transaction"],
        "article": "Req. 12.10",
        "desc": "Immediate incident response; notify card brands within 24 hours",
        "penalty_max": 8000000,
        "penalty_basis": "INR 4 Lakhs – 80 Lakhs/month until compliance restored",
        "currency": "INR",
        "base_severity": "critical",
    },
    "ISO 27001": {
        "full": "ISO/IEC 27001 Information Security Management",
        "jurisdiction": "Global",
        "keywords": ["security", "breach", "incident", "risk", "unauthorized", "access control", "cloud", "misconfigured"],
        "article": "A.16.1.5",
        "desc": "Incident response, learning from incidents, certification obligations",
        "penalty_max": 0,
        "penalty_basis": "Certification loss — operational and contractual impact",
        "currency": "INR",
        "base_severity": "significant",
    },
    "NIST CSF": {
        "full": "NIST Cybersecurity Framework",
        "jurisdiction": "USA/Global",
        "keywords": ["cybersecurity", "network", "infrastructure", "hack", "attack", "vulnerability"],
        "article": "IR-6",
        "desc": "Incident reporting and handling procedures",
        "penalty_max": 0,
        "penalty_basis": "Regulatory framework — agency-specific penalties may apply",
        "currency": "INR",
        "base_severity": "moderate",
    },
    "SOC 2": {
        "full": "SOC 2 Type II Compliance",
        "jurisdiction": "USA/Global",
        "keywords": ["cloud", "saas", "service", "vendor", "availability", "audit", "uptime"],
        "article": "CC7.4",
        "desc": "Security incident response; communication to defined parties",
        "penalty_max": 0,
        "penalty_basis": "Audit failure — loss of certifications and enterprise contracts",
        "currency": "INR",
        "base_severity": "significant",
    },
    "EU AI Act": {
        "full": "EU Artificial Intelligence Act",
        "jurisdiction": "EU/EEA",
        "keywords": ["ai", "artificial intelligence", "machine learning", "algorithm", "automated", "recruitment", "hiring", "model", "bias"],
        "article": "Art. 9, 13, 43",
        "desc": "Risk management system for high-risk AI; transparency obligations",
        "penalty_max": 3150000000,
        "penalty_basis": "INR 315 Crore or 7% of global annual turnover for prohibited AI practices",
        "currency": "INR",
        "base_severity": "high",
    },
    "DPDP Act": {
        "full": "Digital Personal Data Protection Act (India)",
        "jurisdiction": "India",
        "keywords": ["india", "indian", "dpdp", "citizen data"],
        "article": "§8, §33",
        "desc": "Data fiduciary obligations; breach notification to DPBI",
        "penalty_max": 250_000_000,
        "penalty_basis": "Up to INR 250 crore per breach",
        "currency": "INR",
        "base_severity": "high",
    },
}

PII_TYPES = {
    "names": False, "email": False, "phone": False, "address": False,
    "payment": True, "credit card": True, "ssn": True, "passport": True,
    "health": True, "medical": True, "biometric": True,
    "children": True, "racial": True, "religion": True,
}

SEVERITY_ORDER = ["low", "moderate", "significant", "high", "critical"]


# ─── Agent Functions ──────────────────────────────────────────────────────────

def _sev(score: int) -> str:
    if score >= 81: return "critical"
    if score >= 61: return "high"
    if score >= 41: return "significant"
    if score >= 21: return "moderate"
    return "low"

def _risk_level(score: int) -> str:
    # score is compliance score (higher = more compliant = lower risk)
    # risk_level based on how bad things are (inverted)
    inv = 100 - score
    return _sev(inv)


def run_regulatory_agent(desc: str, jurisdiction: str) -> dict:
    d = desc.lower()
    triggered = []
    penalties = []

    for name, reg in REGS_DB.items():
        if any(kw in d for kw in reg["keywords"]):
            severity = reg["base_severity"]
            # Escalate if breach keywords present
            if any(kw in d for kw in ["exposed", "breach", "leaked", "unauthorized", "public", "misconfigured"]):
                idx = SEVERITY_ORDER.index(severity)
                severity = SEVERITY_ORDER[min(idx + 1, len(SEVERITY_ORDER) - 1)]

            triggered.append({
                "name": name,
                "article": reg["article"],
                "section": None,
                "description": reg["desc"],
                "applicable": True,
                "severity": severity,
            })
            if reg["penalty_max"] > 0:
                penalties.append({
                    "regulation": name,
                    "min_amount": float(reg["penalty_max"] * 0.005),
                    "max_amount": float(reg["penalty_max"]),
                    "currency": reg["currency"],
                    "basis": reg["penalty_basis"],
                })

    # Regulatory risk score (lower = more at risk)
    score = max(0, 100 - len(triggered) * 13)
    if any(kw in d for kw in ["exposed", "breach", "leaked", "public"]): score = max(0, score - 20)

    findings = []
    if any(r["name"] == "GDPR" for r in triggered):
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Data Protection",
            "title": "GDPR Mandatory Breach Notification — 72-Hour Deadline",
            "description": "Personal data breach triggers mandatory notification to the supervisory authority under GDPR Article 33 within 72 hours of becoming aware of the breach.",
            "severity": "critical",
            "regulations": [{"name": "GDPR", "article": "Art. 33", "section": None, "description": "Notification to supervisory authority within 72 hours", "applicable": True, "severity": "critical"}],
            "recommendation": "File GDPR Article 33 notification to Data Protection Authority immediately. Engage DPO. Prepare Article 34 communication to affected data subjects within 7 days.",
            "reasoning": "GDPR Article 33 mandates notification without undue delay — max 72 hours from discovery. Failure triggers fines up to €10M or 2% of annual global turnover (Art. 83(4)). LexGuardian AI identified personal data keywords in the incident description consistent with a notifiable breach."
        })
    if any(r["name"] == "EU AI Act" for r in triggered):
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "AI Compliance",
            "title": "High-Risk AI System Deployed Without Conformity Assessment",
            "description": "The EU AI Act classifies AI systems used in recruitment, employment evaluation, or access to essential services as HIGH-RISK under Annex III, requiring formal conformity assessment before deployment.",
            "severity": "high",
            "regulations": [{"name": "EU AI Act", "article": "Art. 9, 43", "section": None, "description": "Risk management system and conformity assessment obligation", "applicable": True, "severity": "high"}],
            "recommendation": "Immediately suspend AI system pending formal risk assessment. Register in EU AI Act database. Prepare technical documentation per Art. 11. Conduct DPIA under GDPR Art. 35 if personal data is processed.",
            "reasoning": "EU AI Act Article 6 read with Annex III classifies AI systems for employment screening as high-risk. Article 9 requires a documented risk management system throughout the system lifecycle. Deployment without conformity assessment constitutes a direct violation."
        })

    return {
        "agent": "Regulatory Agent",
        "regulations_triggered": triggered,
        "findings": findings,
        "penalty_estimates": penalties,
        "score": score,
        "audit": {"agent": "Regulatory Agent", "action": "Regulation Mapping", "details": f"Triggered {len(triggered)} regulations: {', '.join(r['name'] for r in triggered)}"}
    }


def run_privacy_agent(desc: str) -> dict:
    d = desc.lower()
    detected_pii = [k for k in PII_TYPES if k in d]
    if any(kw in d for kw in ["customer data", "user data", "personal information", "pii", "database"]):
        for extra in ["names", "email"]:
            if extra not in detected_pii: detected_pii.append(extra)
    special = [p for p in detected_pii if PII_TYPES.get(p)]

    score = 100 - len(detected_pii) * 8 - len(special) * 12
    if any(kw in d for kw in ["exposed", "breach", "leaked", "public", "accessible"]):
        score -= 25
    score = max(0, score)

    findings = []
    if detected_pii:
        sev = "critical" if special or "payment" in detected_pii else ("high" if detected_pii else "significant")
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Privacy & Data Protection",
            "title": f"PII Exposure — {len(detected_pii)} Data Category{'s' if len(detected_pii) > 1 else ''} Affected",
            "description": f"Identified exposure of: {', '.join(detected_pii)}. {'GDPR Article 9 special category data detected.' if special else ''}",
            "severity": sev,
            "regulations": [
                {"name": "GDPR", "article": "Art. 4, 33-34", "section": None, "description": "Definition of personal data; breach notification obligation", "applicable": True, "severity": sev},
                {"name": "CCPA", "article": None, "section": "§1798.82", "description": "California breach notification", "applicable": True, "severity": "high"},
            ],
            "recommendation": "Activate Incident Response Plan. Classify breach severity. Notify DPO within 1 hour. Commission forensic audit to determine full scope of exposure.",
            "reasoning": f"GDPR Article 4(1) broadly defines personal data as any information relating to an identified or identifiable natural person. The incident involves {', '.join(detected_pii)}, constituting personal data. Unauthorized exposure triggers notification obligations under Articles 33 and 34."
        })
    if "payment" in detected_pii or "credit card" in detected_pii:
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Financial Data Security",
            "title": "Payment Card Data Exposure — PCI DSS Tier-1 Breach",
            "description": "Payment or card data exposure triggers PCI DSS incident response obligations. Acquiring banks and card brands must be notified within 24 hours.",
            "severity": "critical",
            "regulations": [{"name": "PCI DSS", "article": None, "section": "Req. 3, 12.10", "description": "Cardholder data protection and incident response", "applicable": True, "severity": "critical"}],
            "recommendation": "Notify acquiring bank immediately. Engage PCI Forensic Investigator (PFI). Do not destroy evidence. Notify card brands (Visa, Mastercard) per their programs.",
            "reasoning": "PCI DSS Requirement 12.10 requires an immediate response plan. Card brands mandate notification within 24 hours of suspected compromise. Non-compliance results in fines of $5,000–$100,000 per month."
        })

    return {
        "agent": "Privacy Agent",
        "detected_pii": detected_pii,
        "special_categories": special,
        "findings": findings,
        "score": score,
        "audit": {"agent": "Privacy Agent", "action": "PII Assessment", "details": f"PII detected: {', '.join(detected_pii) or 'none'}. Special categories: {', '.join(special) or 'none'}"}
    }


def run_contract_agent(desc: str) -> dict:
    d = desc.lower()
    issues = []
    issue_map = {
        "SLA Breach": ["sla", "service level", "delivery", "failed to deliver", "delayed", "uptime", "downtime"],
        "NDA Violation": ["confidential", "trade secret", "nda", "non-disclosure", "proprietary"],
        "Employment Contract Breach": ["employee", "employment", "hr record", "resigned", "resignation", "usb", "personal device"],
        "Vendor Non-Performance": ["vendor", "supplier", "third-party", "partner", "outsource"],
        "Data Processor Breach": ["cloud", "misconfigured", "storage bucket", "s3", "blob", "accessible", "without authentication"],
    }
    for issue, kws in issue_map.items():
        if any(kw in d for kw in kws): issues.append(issue)

    score = max(0, 100 - len(issues) * 12)
    if any(kw in d for kw in ["breach", "failed", "violated"]): score = max(0, score - 10)

    findings = []
    if "SLA Breach" in issues:
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Contract Law — SLA",
            "title": "Service Level Agreement Breach Detected",
            "description": "Third-party vendor failed to meet contractual SLA obligations, triggering rights to damages, service credits, and potentially contract termination.",
            "severity": "high",
            "regulations": [{"name": "Contract Law", "article": "Breach of Contract", "section": None, "description": "Hadley v Baxendale damages test; right to rescission or specific performance", "applicable": True, "severity": "high"}],
            "recommendation": "Issue formal written Notice of Breach. Calculate actual damages and consequential losses. Review contract for liquidated damages penalty clauses, cure periods, and termination triggers. Preserve all performance records.",
            "reasoning": "A breach of SLA constitutes a breach of contract. The innocent party is entitled to damages that flow naturally from the breach (Hadley v Baxendale [1854]) and to any express remedies specified in the agreement, including service credits or termination rights."
        })
    if "Employment Contract Breach" in issues:
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Employment Law",
            "title": "Employee Data Exfiltration — Breach of Fiduciary Duty",
            "description": "Employee downloaded confidential company data, violating employment contract terms, acceptable use policies, and potentially committing criminal offenses under computer fraud laws.",
            "severity": "high",
            "regulations": [
                {"name": "Employment Law", "article": "Fiduciary Duty", "section": None, "description": "Duty of confidentiality and fidelity — Faccenda Chicken Ltd v Fowler", "applicable": True, "severity": "high"},
                {"name": "Computer Fraud", "article": None, "section": "Criminal Code", "description": "Unauthorized access and data theft may constitute criminal offenses", "applicable": True, "severity": "significant"},
            ],
            "recommendation": "Issue Legal Hold immediately. Inspect employee's devices and accounts with appropriate authorization. Review employment contract for IP assignment and confidentiality clauses. Consult criminal law counsel.",
            "reasoning": "Employees owe a duty of confidentiality under express contract terms and implied by law (Faccenda Chicken principle). Unauthorized extraction of company data may constitute misappropriation of trade secrets and breach of fiduciary duty."
        })
    if "Data Processor Breach" in issues:
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Vendor / Data Processor",
            "title": "Cloud Storage Misconfiguration — Data Processor Liability",
            "description": "Cloud storage misconfiguration resulted in unauthorized access. Review Data Processing Agreement (DPA) for processor liability, security obligations, and indemnification clauses.",
            "severity": "critical",
            "regulations": [{"name": "GDPR", "article": "Art. 28", "section": None, "description": "Controller-processor contractual obligations; processor security requirements", "applicable": True, "severity": "critical"}],
            "recommendation": "Audit all cloud storage configurations immediately. Review DPA security obligations. Assess whether cloud provider breached Art. 28 obligations. Preserve access logs as evidence.",
            "reasoning": "GDPR Article 28 requires that data processors provide 'sufficient guarantees' to implement appropriate technical and organizational measures. Misconfiguration may indicate processor liability if they failed to meet these obligations."
        })

    return {
        "agent": "Contract Agent",
        "issues": issues,
        "findings": findings,
        "score": score,
        "audit": {"agent": "Contract Agent", "action": "Contract Liability Analysis", "details": f"Issues: {', '.join(issues) or 'none detected'}"}
    }


def run_governance_agent(desc: str) -> dict:
    d = desc.lower()
    findings = []
    score = 80

    if any(kw in d for kw in ["employee", "hr", "insider", "resignation", "usb"]):
        score -= 15
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Corporate Governance",
            "title": "Insider Threat — Internal Policy Violation",
            "description": "Employee action constitutes a violation of data security policies, acceptable use policy, and code of conduct, requiring formal disciplinary investigation.",
            "severity": "high",
            "regulations": [
                {"name": "ISO 27001", "article": None, "section": "A.7.2.3", "description": "Disciplinary process for information security violations", "applicable": True, "severity": "high"},
                {"name": "SOC 2", "article": None, "section": "CC9.1", "description": "Risk assessment for insider threats", "applicable": True, "severity": "significant"},
            ],
            "recommendation": "Initiate formal HR investigation. Suspend system access immediately. Brief Audit Committee. Document all governance actions for regulatory response.",
            "reasoning": "ISO 27001 Annex A.7.2.3 requires a formal disciplinary process for employees who commit information security violations. The insider threat constitutes a material governance incident requiring Audit Committee notification."
        })

    if any(kw in d for kw in ["ai", "artificial intelligence", "algorithm", "automated", "model", "ml"]):
        score -= 20
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "AI Governance",
            "title": "AI Deployment Without Risk Assessment — EU AI Act Violation",
            "description": "AI or automated decision-making system deployed without formal governance documentation, risk assessment, or bias testing per EU AI Act Annex III high-risk requirements.",
            "severity": "high",
            "regulations": [
                {"name": "EU AI Act", "article": "Art. 9", "section": None, "description": "Risk management system required throughout lifecycle", "applicable": True, "severity": "high"},
                {"name": "GDPR", "article": "Art. 22, 35", "section": None, "description": "Automated decision-making restrictions; DPIA requirement", "applicable": True, "severity": "significant"},
            ],
            "recommendation": "Suspend AI system pending risk assessment. Conduct DPIA under GDPR Art. 35. Prepare EU AI Act technical documentation (Art. 11). Establish ongoing monitoring per Art. 9(7).",
            "reasoning": "EU AI Act Annex III classifies AI systems for recruitment, employment evaluation, and creditworthiness as high-risk. Article 9 requires documented risk management throughout the lifecycle. GDPR Article 22 restricts solely automated decisions with significant effects."
        })

    if any(kw in d for kw in ["board", "executive", "material", "significant breach"]) or score < 60:
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Board Governance",
            "title": "Material Incident — Board Notification Required",
            "description": "Incident severity warrants timely notification to the Board of Directors and Audit Committee per corporate governance standards.",
            "severity": "significant",
            "regulations": [{"name": "SOC 2", "article": None, "section": "CC7.4", "description": "Communication of security incidents to defined internal parties", "applicable": True, "severity": "significant"}],
            "recommendation": "Brief Board of Directors within 24–48 hours. Prepare incident summary report. Engage external counsel for privilege protection. Document board decisions.",
            "reasoning": "SOC 2 CC7.4 requires that identified security incidents are communicated to defined internal and external parties in a timely manner. Material breaches triggering regulatory notification obligations require simultaneous board disclosure."
        })

    return {
        "agent": "Governance Agent",
        "findings": findings,
        "score": max(0, score),
        "audit": {"agent": "Governance Agent", "action": "Governance Assessment", "details": f"Score: {max(0, score)}/100. Issues: {len(findings)} governance findings"}
    }


def run_litigation_agent(desc: str) -> dict:
    d = desc.lower()
    prob = 0.1
    if any(kw in d for kw in ["exposed", "breach", "leaked", "public", "accessible"]): prob += 0.40
    if any(kw in d for kw in ["payment", "financial", "medical", "health"]): prob += 0.20
    if any(kw in d for kw in ["employee", "hr", "discrimination", "wrongful"]): prob += 0.15
    if any(kw in d for kw in ["hospital", "patient", "clinical"]): prob += 0.20
    if any(kw in d for kw in ["class action", "lawsuit", "litigation"]): prob += 0.30
    prob = min(prob, 0.95)

    legal_hold = any(kw in d for kw in ["breach", "exposed", "leaked", "employee", "resigned", "investigation"])
    score = max(0, 100 - int(prob * 100))

    findings = []
    if prob >= 0.35:
        sev = "critical" if prob >= 0.7 else ("high" if prob >= 0.5 else "significant")
        findings.append({
            "id": uuid.uuid4().hex[:8],
            "category": "Litigation Risk",
            "title": f"Elevated Litigation Probability — {int(prob * 100)}%",
            "description": f"LexGuardian AI estimates {int(prob * 100)}% probability of regulatory investigation or civil litigation based on incident characteristics, data types involved, and regulatory exposure.",
            "severity": sev,
            "regulations": [{"name": "Evidence Law", "article": "Legal Hold Doctrine", "section": None, "description": "Duty to preserve evidence arises upon reasonable anticipation of litigation", "applicable": True, "severity": sev}],
            "recommendation": f"Issue legal hold immediately. Suspend auto-deletion of emails, logs, backups. Engage external litigation counsel. Document all incident response steps under attorney-client privilege.",
            "reasoning": f"Factors driving {int(prob * 100)}% litigation estimate: data breach scope, regulatory obligations triggered, affected data subjects' right to remedies under GDPR Art. 82 (right to compensation). Legal hold duty arises when litigation is reasonably anticipated — Zubulake v UBS Warburg standard."
        })

    return {
        "agent": "Litigation Agent",
        "lawsuit_probability": prob,
        "legal_hold_recommended": legal_hold,
        "findings": findings,
        "score": score,
        "audit": {"agent": "Litigation Agent", "action": "Litigation Risk Prediction", "details": f"Lawsuit probability: {int(prob*100)}%. Legal hold: {legal_hold}"}
    }


def run_disclosure_agent(desc: str, jurisdiction: str) -> dict:
    d = desc.lower()
    now = datetime.now(timezone.utc)
    notices = []
    actions = []

    is_breach = any(kw in d for kw in ["exposed", "breach", "leaked", "unauthorized", "database", "customer", "accessible", "misconfigured"])

    if is_breach:
        notices.append({
            "type": "Regulatory Filing",
            "audience": "Data Protection Authority (DPA / ICO / CNIL)",
            "deadline": f"72 hours from discovery — by {(now + timedelta(hours=72)).strftime('%Y-%m-%d %H:%M')} UTC",
            "content": (
                "GDPR Article 33 — Data Breach Notification\n\n"
                "Nature of breach: Unauthorized access to personal data\n"
                "Data categories affected: [As identified in forensic investigation]\n"
                "Approximate number of individuals affected: [Under active investigation]\n"
                "Likely consequences: Identity theft, financial loss, reputational harm\n"
                "Remedial measures: Access contained; forensic investigation initiated; affected systems isolated; legal hold issued\n\n"
                "Contact: [Data Protection Officer Name and Contact]"
            ),
            "regulatory_requirement": "GDPR Article 33"
        })
        notices.append({
            "type": "Customer / Data Subject Notification",
            "audience": "Affected Individuals",
            "deadline": f"Within 7 days — by {(now + timedelta(days=7)).strftime('%Y-%m-%d')}",
            "content": (
                "Dear [Customer Name],\n\n"
                "Notice of Data Security Incident\n\n"
                "We are writing to inform you of a security incident that may have affected your personal information.\n\n"
                "What happened: [Description]\n"
                "What information was involved: [Data types]\n"
                "What we are doing: We immediately contained the issue and engaged expert investigators.\n"
                "What you can do: Monitor accounts, place fraud alert, contact credit bureaus.\n\n"
                "We sincerely apologize. Contact our Privacy Team: privacy@[company].com\n\n"
                "[Company Name] Privacy Team"
            ),
            "regulatory_requirement": "GDPR Art. 34 / CCPA §1798.82"
        })
        notices.append({
            "type": "Board / Executive Briefing",
            "audience": "Board of Directors & Audit Committee",
            "deadline": "Within 24 hours",
            "content": (
                "CONFIDENTIAL — Attorney-Client Privileged\n\n"
                "Subject: Material Data Security Incident — Board Notification\n\n"
                "Summary: [Date] data security incident detected. [Nature]. Forensic investigation underway.\n"
                "Regulatory Exposure: GDPR (€20M max), CCPA ($7,500/violation), PCI DSS ($100K/month)\n"
                "Immediate Actions Taken: Containment, legal hold, DPA filing prepared\n"
                "Next Steps: Full forensic report within 72 hours\n\n"
                "Questions: Contact General Counsel"
            ),
            "regulatory_requirement": "SOC 2 CC7.4 / Corporate Governance"
        })

        actions = [
            {"priority": "immediate", "action": "Contain breach — isolate affected systems and revoke unauthorized access", "owner": "CISO / IT Security", "deadline": "Within 2 hours", "legal_basis": "GDPR Art. 32 — Security of processing"},
            {"priority": "immediate", "action": "Notify Data Protection Authority (GDPR Art. 33 — 72-hour deadline)", "owner": "DPO / Legal Team", "deadline": f"By {(now + timedelta(hours=72)).strftime('%Y-%m-%d %H:%M')} UTC", "legal_basis": "GDPR Article 33"},
            {"priority": "immediate", "action": "Issue Legal Hold — preserve all emails, logs, backups related to incident", "owner": "General Counsel", "deadline": "Within 24 hours", "legal_basis": "Evidence preservation — reasonably anticipated litigation"},
            {"priority": "immediate", "action": "Engage PCI Forensic Investigator (PFI) if payment data involved", "owner": "CISO + External Counsel", "deadline": "Within 4 hours", "legal_basis": "PCI DSS Requirement 12.10"},
            {"priority": "immediate", "action": "Brief Board of Directors and Audit Committee", "owner": "CEO / General Counsel", "deadline": "Within 24 hours", "legal_basis": "SOC 2 CC7.4 — Material incident communication"},
        ]
    else:
        actions = [
            {"priority": "immediate", "action": "Conduct internal compliance investigation", "owner": "Legal / Compliance Team", "deadline": "Within 48 hours", "legal_basis": "Regulatory compliance obligation"},
            {"priority": "immediate", "action": "Document all relevant facts and preserve evidence", "owner": "Legal Team", "deadline": "Immediately", "legal_basis": "Evidence preservation best practice"},
        ]

    timeline = [
        {"date": now.isoformat(), "event": "Incident Discovered & Initial Response", "type": "incident", "status": "completed"},
        {"date": (now + timedelta(hours=2)).isoformat(), "event": "Systems Contained & Forensic Investigation Initiated", "type": "action", "status": "pending"},
        {"date": (now + timedelta(hours=24)).isoformat(), "event": "Legal Hold Issued & Board Briefed", "type": "action", "status": "pending"},
        {"date": (now + timedelta(hours=72)).isoformat(), "event": "GDPR DPA Notification Deadline", "type": "deadline", "status": "pending"},
        {"date": (now + timedelta(days=5)).isoformat(), "event": "PCI DSS Card Brand Notification", "type": "filing", "status": "pending"},
        {"date": (now + timedelta(days=7)).isoformat(), "event": "Data Subject Notification Deadline", "type": "notification", "status": "pending"},
        {"date": (now + timedelta(days=30)).isoformat(), "event": "DPIA Completion & Submission", "type": "filing", "status": "pending"},
        {"date": (now + timedelta(days=60)).isoformat(), "event": "Remediation Plan Full Implementation", "type": "action", "status": "pending"},
        {"date": (now + timedelta(days=90)).isoformat(), "event": "Post-Incident Security Audit", "type": "action", "status": "pending"},
    ]

    score = 75 if notices else 92
    return {
        "agent": "Disclosure Agent",
        "notices": notices,
        "immediate_actions": actions,
        "timeline": timeline,
        "score": score,
        "audit": {"agent": "Disclosure Agent", "action": "Disclosure Package Generated", "details": f"{len(notices)} notices across {len(set(n['audience'] for n in notices))} stakeholder groups"}
    }


# ─── Orchestrator ────────────────────────────────────────────────────────────

def classify_incident(desc: str) -> str:
    d = desc.lower()
    if any(kw in d for kw in ["database", "exposed", "leaked", "breach", "customer data"]): return "Data Breach"
    if any(kw in d for kw in ["sla", "vendor", "deliver", "supply"]): return "Contract / SLA Breach"
    if any(kw in d for kw in ["employee", "hr", "usb", "resignation", "insider"]): return "Insider Threat"
    if any(kw in d for kw in ["ai", "artificial intelligence", "algorithm", "automated"]): return "AI Compliance Issue"
    if any(kw in d for kw in ["cloud", "misconfigured", "storage bucket", "s3"]): return "Cloud Misconfiguration"
    if any(kw in d for kw in ["medical", "health", "patient", "hospital"]): return "Healthcare Compliance"
    return "Regulatory Compliance Issue"


async def orchestrate(incident: IncidentInput) -> dict:
    desc = incident.description
    jurisdiction = incident.jurisdiction

    results = await asyncio.gather(
        asyncio.to_thread(run_regulatory_agent, desc, jurisdiction),
        asyncio.to_thread(run_privacy_agent, desc),
        asyncio.to_thread(run_contract_agent, desc),
        asyncio.to_thread(run_governance_agent, desc),
        asyncio.to_thread(run_litigation_agent, desc),
        asyncio.to_thread(run_disclosure_agent, desc, jurisdiction),
    )
    reg, priv, cont, gov, lit, disc = results

    # Aggregate all findings
    all_findings = []
    for r in results:
        all_findings.extend(r.get("findings", []))

    # Scores
    privacy_score = priv["score"]
    contract_score = cont["score"]
    regulatory_score = reg["score"]
    governance_score = gov["score"]
    disclosure_score = disc["score"]
    overall = int((privacy_score + contract_score + regulatory_score + governance_score + disclosure_score) / 5)

    risk_level = _risk_level(overall)

    # Long-term actions
    long_term = [
        {"priority": "long_term", "action": "Conduct Data Protection Impact Assessment (DPIA)", "owner": "DPO", "deadline": "30 days", "legal_basis": "GDPR Art. 35"},
        {"priority": "long_term", "action": "Review and update Information Security Policy (ISP)", "owner": "CISO", "deadline": "60 days", "legal_basis": "ISO 27001 A.18.2"},
        {"priority": "long_term", "action": "Implement privileged access monitoring and DLP solution", "owner": "IT Security", "deadline": "90 days", "legal_basis": "NIST PR.AC-4 / ISO 27001 A.9"},
        {"priority": "long_term", "action": "Schedule annual third-party penetration testing", "owner": "CISO", "deadline": "6 months", "legal_basis": "PCI DSS Req. 11.3 / ISO 27001 A.12.6"},
        {"priority": "long_term", "action": "Update vendor contract templates with GDPR Art. 28 clauses", "owner": "Legal", "deadline": "45 days", "legal_basis": "GDPR Article 28"},
        {"priority": "long_term", "action": "Deploy employee security awareness training program", "owner": "HR / CISO", "deadline": "60 days", "legal_basis": "ISO 27001 A.7.2.2"},
    ]

    # AI Reasoning
    penalties = reg["penalty_estimates"]
    max_penalty = max((p["max_amount"] for p in penalties), default=0)
    penalty_currency = penalties[0]["currency"] if penalties else "EUR"

    ai_reasoning = f"""LexGuardian AI performed a 6-agent parallel legal analysis:

[Regulatory Agent] Identified {len(reg['regulations_triggered'])} applicable regulations across GDPR, CCPA, PCI DSS, ISO 27001, and other frameworks. Regulatory compliance score: {regulatory_score}/100. Maximum financial exposure: {penalty_currency} {max_penalty:,.0f}+.

[Privacy Agent] Detected PII categories: {', '.join(priv['detected_pii']) or 'none identified'}. Special GDPR Article 9 categories: {', '.join(priv['special_categories']) or 'none'}. Privacy risk score: {privacy_score}/100. Exposure triggers GDPR notification obligations.

[Contract Agent] Contract issues identified: {', '.join(cont['issues']) or 'none'}. Contract compliance score: {contract_score}/100. Applicable legal principles: Hadley v Baxendale (foreseeable damages), Faccenda Chicken (employee confidentiality duty).

[Governance Agent] Board and ethics assessment complete. Governance score: {governance_score}/100. {len(gov['findings'])} governance findings. Board notification may be required for material incidents.

[Litigation Agent] Lawsuit probability: {int(lit['lawsuit_probability'] * 100)}%. Legal hold recommended: {lit['legal_hold_recommended']}. Risk score: {lit['score']}/100. Litigation timeline: 6–24 months if regulatory action follows.

[Disclosure Agent] Generated {len(disc['notices'])} disclosure notices with regulatory deadlines. Disclosure preparedness score: {disclosure_score}/100. Critical 72-hour GDPR deadline identified.

Synthesis: Overall compliance risk score {overall}/100 — {risk_level.upper()} RISK. {len(all_findings)} legal findings across {len(reg['regulations_triggered'])} triggered regulatory frameworks."""

    executive_summary = f"""LEXGUARDIAN AI — {risk_level.upper()} RISK ASSESSMENT

Incident: {desc[:300]}{'...' if len(desc) > 300 else ''}

KEY LEGAL OBLIGATIONS:
• {len(all_findings)} legal findings identified across {len(reg['regulations_triggered'])} regulatory frameworks
• {"GDPR 72-hour breach notification MANDATORY" if any(r['name']=='GDPR' for r in reg['regulations_triggered']) else "Compliance review required"}
• Legal hold {"RECOMMENDED — preserve all evidence immediately" if lit['legal_hold_recommended'] else "not triggered at this stage"}
• Board notification {"REQUIRED" if governance_score < 75 else "recommended as precaution"}

FINANCIAL EXPOSURE: {penalty_currency} {max_penalty:,.0f}+ maximum regulatory penalty
OVERALL COMPLIANCE SCORE: {overall}/100 — {risk_level.upper()} RISK

LexGuardian AI recommends engaging qualified legal counsel immediately and activating your Incident Response Plan within 2 hours.

⚠️ This is AI-generated legal intelligence. Always review with qualified legal counsel before acting."""

    now = datetime.now(timezone.utc).isoformat()
    report_id = f"LEX-{uuid.uuid4().hex[:8].upper()}"
    audit_trail = [{"timestamp": now, **r["audit"]} for r in results]

    report = {
        "id": report_id,
        "incident_id": f"INC-{uuid.uuid4().hex[:8].upper()}",
        "created_at": now,
        "incident_summary": desc,
        "incident_type": classify_incident(desc),
        "risk_level": risk_level,
        "compliance_scores": {
            "privacy": privacy_score,
            "contracts": contract_score,
            "regulatory": regulatory_score,
            "governance": governance_score,
            "disclosure": disclosure_score,
            "overall": overall,
        },
        "legal_findings": all_findings,
        "regulations_triggered": reg["regulations_triggered"],
        "penalty_estimates": penalties,
        "immediate_actions": disc["immediate_actions"],
        "long_term_actions": long_term,
        "legal_hold_recommended": lit["legal_hold_recommended"],
        "executive_summary": executive_summary,
        "ai_reasoning": ai_reasoning,
        "audit_trail": audit_trail,
        "compliance_timeline": disc["timeline"],
    }

    api_key_to_use = incident.api_key or os.getenv("OPENAI_API_KEY")
    if api_key_to_use:
        try:
            import json
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key_to_use)
            prompt = f"""You are LexGuardian AI, a world-class enterprise AI Legal Operations Agent.
A heuristic engine has generated the following baseline analysis for this incident:
Incident: "{desc}"
Jurisdiction: "{jurisdiction}"

Rewrite and enhance the data into a comprehensive Enterprise Legal Operations Dashboard format. 
You must structure the executive_summary cleanly into headings: Situation, Legal Exposure, Compliance Status, Critical Risks, and Executive Recommendation.
You must generate a deep "confidence_score" and "evidence_panel" based on standard legal incident facts.
CRITICAL: Every cost, revenue, penalty, or value representing money MUST be evaluated and displayed in INR (₹) (e.g. ₹20 Crore, or INR 2,00,000). Do NOT use USD or EUR.

Heuristic Data:
{json.dumps({"executive_summary": executive_summary, "ai_reasoning": ai_reasoning, "legal_findings": all_findings})}

Return EXACTLY this JSON structure, keeping ids intact where applicable.
{{
  "executive_summary": "rewritten with structured headings...",
  "ai_reasoning": "rewritten as a step-by-step reasoning flow explaining how the AI reached the conclusion...",
  "confidence_score": {{
      "score": 96,
      "evidence_strength": "High",
      "reasoning_depth": "Deep Legal Analysis",
      "matched_regulations": 3
  }},
  "legal_findings": [
     {{
        "id": "original_id",
        "category": "original_category",
        "title": "rewritten...",
        "description": "rewritten...",
        "severity": "original_severity",
        "regulations": [], 
        "recommendation": "rewritten action...",
        "reasoning": "rewritten legal basis...",
        "confidence": "95%",
        "business_impact": "Financial loss and regulatory audit"
     }}
  ],
  "evidence": [
     {{"source": "Firewall Logs", "timestamp": "08:15 UTC", "status": "Compromised", "integrity": "Valid"}},
     {{"source": "Database Logs", "timestamp": "08:35 UTC", "status": "Exfiltrated", "integrity": "Valid"}}
  ]
}}
"""
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            llm_updates = json.loads(response.choices[0].message.content)
            
            report["executive_summary"] = llm_updates.get("executive_summary", executive_summary)
            report["ai_reasoning"] = llm_updates.get("ai_reasoning", ai_reasoning)
            if "legal_findings" in llm_updates:
                report["legal_findings"] = llm_updates["legal_findings"]
            
            report["confidence_score"] = llm_updates.get("confidence_score", {"score": 90, "evidence_strength": "Medium", "reasoning_depth": "Standard", "matched_regulations": len(reg["regulations_triggered"])})
            report["evidence"] = llm_updates.get("evidence", [])
            
            report["audit_trail"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "OpenAI Synthesizer",
                "action": "Enterprise Dashboard Upgrade",
                "details": "LLM synthesized evidence, reasoning flows, and structured executive formatting."
            })
        except Exception as e:
            logger.error(f"OpenAI LLM Rewrite Failed: {e}")

    return report


# ─── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="LexGuardian AI",
    description="Enterprise Legal & Compliance Intelligence — 6 Specialized Legal Agents",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client (lazy — set on startup)
mongo_client: AsyncIOMotorClient | None = None
db = None


@app.on_event("startup")
async def startup():
    global mongo_client, db
    try:
        mongo_client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        await mongo_client.admin.command("ping")
        db = mongo_client[settings.mongodb_db]
        # Create indexes
        await db.reports.create_index("id", unique=True)
        await db.reports.create_index("created_at")
        await db.reports.create_index("risk_level")
        logger.info(f"✅ MongoDB connected — db: {settings.mongodb_db}")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB unavailable ({e}) — using in-memory store")
        mongo_client = None
        db = None


@app.on_event("shutdown")
async def shutdown():
    if mongo_client:
        mongo_client.close()


# In-memory fallback
_mem_store: dict[str, dict] = {}


async def save_report(report: dict):
    if db is not None:
        await db.reports.replace_one({"id": report["id"]}, report, upsert=True)
    _mem_store[report["id"]] = report


async def load_report(report_id: str) -> dict | None:
    if db is not None:
        doc = await db.reports.find_one({"id": report_id}, {"_id": 0})
        return doc
    return _mem_store.get(report_id)


async def list_reports(limit: int = 20) -> list[dict]:
    if db is not None:
        cursor = db.reports.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    return list(_mem_store.values())[-limit:]


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    mongo_ok = db is not None
    return {"status": "healthy", "mongo": mongo_ok, "version": "2.0.0", "agents": 6}


@app.post("/analyze")
async def analyze(incident: IncidentInput):
    try:
        report = await orchestrate(incident)
        await save_report(report)
        logger.info(f"Report generated: {report['id']} — Risk: {report['risk_level']}")
        return report
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report/{report_id}")
async def get_report(report_id: str):
    report = await load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/reports")
async def get_reports(limit: int = 20):
    reports = await list_reports(limit)
    return {"reports": reports, "count": len(reports)}


@app.get("/dashboard")
async def dashboard():
    reports = await list_reports(100)
    if not reports:
        return {"total": 0, "avg_score": 0, "critical": 0, "high": 0, "recent": []}
    total = len(reports)
    avg = int(sum(r["compliance_scores"]["overall"] for r in reports) / total)
    by_risk = {r: sum(1 for x in reports if x["risk_level"] == r) for r in ["critical", "high", "significant", "moderate", "low"]}
    recent = [{"id": r["id"], "type": r["incident_type"], "risk": r["risk_level"], "score": r["compliance_scores"]["overall"], "date": r["created_at"]} for r in reports[:5]]
    return {"total": total, "avg_score": avg, "by_risk": by_risk, "recent": recent}


@app.post("/contract")
async def analyze_contract(payload: dict):
    text = payload.get("text", payload.get("description", ""))
    result = run_contract_agent(text)
    return {"findings": result["findings"], "score": result["score"], "issues": result["issues"]}


@app.post("/privacy")
async def analyze_privacy(payload: dict):
    desc = payload.get("description", "")
    result = run_privacy_agent(desc)
    return {"score": result["score"], "findings": result["findings"], "pii": result["detected_pii"]}


@app.post("/compliance")
async def check_compliance(payload: dict):
    desc = payload.get("description", "")
    jurisdiction = payload.get("jurisdiction", "EU / GDPR")
    reg = run_regulatory_agent(desc, jurisdiction)
    return {"regulations": reg["regulations_triggered"], "score": reg["score"], "penalties": reg["penalty_estimates"]}


@app.get("/regulations")
async def list_regulations():
    return {k: {"name": v["full"], "jurisdiction": v["jurisdiction"], "penalty_max": v["penalty_max"], "currency": v["currency"]} for k, v in REGS_DB.items()}


@app.get("/export/json/{report_id}")
async def export_json(report_id: str):
    report = await load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/export/md/{report_id}")
async def export_md(report_id: str):
    report = await load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    scores = report.get("compliance_scores", {})
    findings = report.get("legal_findings", [])
    regs = report.get("regulations_triggered", [])
    actions = report.get("immediate_actions", [])
    penalties = report.get("penalty_estimates", [])

    md = f"""# LexGuardian AI — Legal Report {report['id']}

**Date:** {report['created_at']}
**Incident Type:** {report['incident_type']}
**Risk Level:** {report['risk_level'].upper()}
**Overall Compliance Score:** {scores.get('overall', 0)}/100

---

## Executive Summary

{report.get('executive_summary', '')}

---

## Compliance Scores

| Domain | Score |
|--------|-------|
| Privacy | {scores.get('privacy', 0)}/100 |
| Contracts | {scores.get('contracts', 0)}/100 |
| Regulatory | {scores.get('regulatory', 0)}/100 |
| Governance | {scores.get('governance', 0)}/100 |
| Disclosure | {scores.get('disclosure', 0)}/100 |
| **Overall** | **{scores.get('overall', 0)}/100** |

---

## Legal Findings ({len(findings)})

{''.join([f"""### {f.get('title','')}
**Category:** {f.get('category','')} | **Severity:** {f.get('severity','').upper()}

{f.get('description','')}

**Recommendation:** {f.get('recommendation','')}

**Legal Reasoning:** {f.get('reasoning','')}

---
""" for f in findings])}

## Regulations Triggered ({len(regs)})

{''.join([f"- **{r['name']}** {r.get('article','') or r.get('section','')} — {r['description']} *(Severity: {r['severity']})*\\n" for r in regs])}

---

## Penalty Estimates

{''.join([f"- **{p['regulation']}:** {p['currency']} {p['min_amount']:,.0f}–{p['max_amount']:,.0f} ({p['basis']})\\n" for p in penalties])}

---

## Immediate Actions Required

{''.join([f"- [ ] **{a['action']}**\\n  - Owner: {a['owner']} | Deadline: {a['deadline']}\\n  - Legal Basis: {a['legal_basis']}\\n" for a in actions])}

---

*Generated by LexGuardian AI Legal Intelligence System v2.0 — Not legal advice. Consult qualified legal counsel.*
"""
    return PlainTextResponse(content=md, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename=lexguardian-{report_id}.md"})


# --- Agentverse SDK Injection ---
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')))
try:
    from packages.agent_adapter import AgentverseWrapper
    
    async def legacy_legal_handler(payload):
        import httpx
        memory_url = os.getenv("MEMORY_URL", "http://localhost:8102/api/memory")
        crisis_id = payload.crisis_id
        agent_outputs = {}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{memory_url}/{crisis_id}")
                if resp.status_code == 200:
                    agent_outputs = resp.json().get("agent_outputs", {})
        except Exception as e:
            print(f"Legal Agent failed to read memory: {e}")

        desc = payload.description.lower()
        
        findings = []
        recommendations = []
        risk_score = 2
        confidence = 0.90

        if "breach" in desc or "cyber" in desc or "data" in desc:
            findings.append("Potential GDPR and CCPA violations identified due to exposed PII.")
            findings.append("Statutory 72-hour reporting window to regulatory authorities is now active.")
            recommendations.append("Draft mandatory disclosures for relevant data protection authorities.")
            recommendations.append("Retain outside breach counsel immediately.")
            risk_score = 9

        elif "recall" in desc or "defect" in desc:
            findings.append("Consumer Protection Act liabilities identified regarding product safety.")
            recommendations.append("Halt all sales of affected SKUs to prevent further liability.")
            risk_score = 8
            
        elif "lawsuit" in desc or "sue" in desc:
            findings.append("Active litigation threat detected. Document preservation mandate is required.")
            recommendations.append("Issue enterprise-wide litigation hold on all communications.")
            risk_score = 8

        else:
            findings.append("No immediate statutory violations apparent in initial crisis report.")
            recommendations.append("Continue to monitor situation for evolving liabilities.")

        # Collaborative check: Did financial agent find high risk?
        fin_out = agent_outputs.get("financial", {})
        if fin_out.get("risk_score", 0) > 7:
            findings.append("Severe financial impact implies potential fiduciary disclosures may be required for shareholders.")
            recommendations.append("Notify SEC counsel regarding potential material impact disclosure (8-K).")
            risk_score += 1

        return (findings, recommendations, confidence, min(10, risk_score))

    AgentverseWrapper(app).register(
        agent_name="legal_compliance",
        port=8003,
        capabilities=["Liability Assessment", "Regulation Check"],
        dependencies=[],
        legacy_handler=legacy_legal_handler
    )
except ImportError as e:
    print(f"Agentverse SDK not found: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
