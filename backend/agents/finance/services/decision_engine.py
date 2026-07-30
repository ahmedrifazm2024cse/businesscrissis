import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Merges results from all 9 intelligence modules.
    Removes duplicate alerts, ranks issues by severity, and generates Critical/Recommended Actions.
    """
    def process_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Decision Engine processing telemetry...")
        
        all_issues = []
        
        # Flatten issues from telemetry
        for key, items in telemetry.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and ("severity" in item or "risk_level" in item or "anomaly_type" in item or "risk_category" in item):
                        # Extract finding/recommendation
                        finding = item.get("finding", item.get("message", ""))
                        if not finding:
                            if "anomaly_type" in item:
                                finding = f"Demand Anomaly: {item['anomaly_type']} for {item.get('sku')}"
                            elif "risk_category" in item:
                                finding = f"{key.capitalize()} risk: {item['risk_category']}"
                            else:
                                finding = f"Issue detected in {key}"
                        
                        severity = item.get("severity", item.get("risk_level", item.get("risk_category", "Medium")))
                        
                        rec = item.get("recommendation", item.get("recommendations", []))
                        if isinstance(rec, list) and rec:
                            rec = rec[0]
                        elif isinstance(rec, list):
                            rec = "Review immediately."
                        
                        all_issues.append({
                            "source": key,
                            "finding": finding,
                            "severity": severity,
                            "recommendation": str(rec)
                        })
        
        # Deduplicate
        unique_issues = []
        seen = set()
        for issue in all_issues:
            sig = (issue["source"], issue["finding"])
            if sig not in seen:
                seen.add(sig)
                unique_issues.append(issue)
        
        # Rank by severity
        severity_map = {"Emergency": 5, "Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        unique_issues.sort(key=lambda x: severity_map.get(x["severity"], 0), reverse=True)
        
        critical_actions = []
        recommended_actions = []
        for issue in unique_issues:
            if severity_map.get(issue["severity"], 0) >= 4:
                critical_actions.append(f"[{issue['source'].upper()}] {issue['finding']} -> ACTION: {issue['recommendation']}")
            else:
                recommended_actions.append(f"[{issue['source'].upper()}] {issue['finding']} -> ACTION: {issue['recommendation']}")
        
        return {
            "critical_actions": critical_actions,
            "recommended_actions": recommended_actions,
            "top_issues": unique_issues[:5],
            "total_issues_count": len(unique_issues)
        }

decision_engine = DecisionEngine()
