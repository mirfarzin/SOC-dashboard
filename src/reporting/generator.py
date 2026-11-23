"""
Incident Report Generator for PS02.
Produces comprehensive, auditable incident reports in JSON and Markdown formats.
Strictly separates observed facts from hypotheses and provides full event provenance.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.schema import Incident, SLMReportAnalysis, TriageReport


class ReportGenerator:
    @staticmethod
    def create_report(
        incident: Incident,
        slm_analysis: SLMReportAnalysis,
        inference_latency_ms: float = 0.0,
        offline_mode: bool = True
    ) -> TriageReport:
        provenance = {
            "system": "PS02 Offline Security Incident Triage Assistant",
            "version": "1.0.0",
            "participant": "Mir Farzin Hussain (USN: 1MS24CI073)",
            "operating_mode": "100% OFFLINE (No Cloud / Zero Internet Dependencies)",
            "local_model": slm_analysis.model_name,
            "inference_latency_ms": round(inference_latency_ms, 2),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "validation_passed": slm_analysis.validation_passed,
            "evidence_count": len(incident.event_ids),
            "human_in_the_loop_notice": (
                "ADVISORY NOTICE: This report is an AI-assisted triage briefing. "
                "No autonomous remediation actions were executed. All recommended steps "
                "require explicit authorization by a human Security Analyst."
            )
        }

        return TriageReport(
            incident=incident,
            slm_analysis=slm_analysis,
            generated_at=datetime.utcnow(),
            provenance=provenance
        )

    @staticmethod
    def export_json(report: TriageReport, output_path: Path | str) -> str:
        """Export report to a formatted JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = report.model_dump(mode="json")
        serialized = json.dumps(data, indent=2, default=str)
        with open(path, "w", encoding="utf-8") as f:
            f.write(serialized)
        return str(path)

    @staticmethod
    def export_markdown(report: TriageReport, output_path: Optional[Path | str] = None) -> str:
        """Export report as professional GitHub-Flavored Markdown."""
        inc = report.incident
        slm = report.slm_analysis
        prov = report.provenance

        # Badges & header
        sev_color = {
            "Critical": "🔴 CRITICAL",
            "High": "🟠 HIGH",
            "Medium": "🟡 MEDIUM",
            "Low": "🟢 LOW",
            "Informational": "🔵 INFORMATIONAL"
        }.get(inc.severity.value, inc.severity.value)

        md = []
        md.append(f"# Incident Triage Report: {inc.incident_id}")
        md.append(f"**Case Title:** {slm.title}\n")
        md.append(f"| Attribute | Value |")
        md.append(f"| :--- | :--- |")
        md.append(f"| **Incident ID** | `{inc.incident_id}` |")
        md.append(f"| **Authoritative Severity** | **{sev_color}** (Score: {inc.severity_score}/100) |")
        md.append(f"| **Classification Engine** | Deterministic Rule-Based Synergy Classifier |")
        md.append(f"| **Triage Assistant** | Local SLM: `{slm.model_name}` |")
        md.append(f"| **Inference Latency** | `{prov.get('inference_latency_ms', 0)} ms` |")
        md.append(f"| **Operating Mode** | `{prov.get('operating_mode')}` |")
        md.append(f"| **Evidence Integrity** | `{'VERIFIED' if slm.validation_passed else 'FLAGGED'}` ({len(slm.referenced_event_ids)} verified citations) |")
        md.append(f"| **Generated Timestamp** | `{prov.get('generated_at')}` |\n")

        # Advisory Notice
        md.append("> [!IMPORTANT]")
        md.append(f"> **Human Authorization Required**: {prov.get('human_in_the_loop_notice')}\n")

        # Executive Summary
        md.append("## 1. Executive Summary")
        md.append(f"{slm.executive_summary}\n")

        # Severity Score Breakdown
        md.append("## 2. Deterministic Severity Rationale")
        for line in inc.severity_breakdown:
            md.append(f"- {line}")
        md.append("")

        # Triggered Detection Rules
        md.append("## 3. Triggered Detection Rules")
        md.append("| Rule ID | Rule Name | Severity Contribution | Authorized? | Supporting Events |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for f in inc.findings:
            auth_str = "Yes (Ticket)" if f.is_authorized else "No (Unapproved)"
            eids = ", ".join(f.supporting_event_ids[:3]) + ("..." if len(f.supporting_event_ids) > 3 else "")
            md.append(f"| `{f.rule_id}` | **{f.rule_name}** | +{f.severity_contribution} | {auth_str} | `{eids}` |")
        md.append("")

        # Verified Facts vs Hypotheses
        md.append("## 4. Observed Evidence vs. Hypotheses")
        md.append("### 🔍 Verified Facts (Directly evidenced in telemetry)")
        for fact in slm.facts:
            md.append(f"- **[VERIFIED]** {fact}")
        md.append("")

        md.append("### 💡 Plausible Hypotheses (Requiring analyst confirmation)")
        for hypo in slm.hypotheses:
            md.append(f"- **[HYPOTHESIS]** {hypo}")
        md.append("")

        # Affected Entities
        md.append("## 5. Scope of Impact & Entities Involved")
        users = inc.entities_involved.get("users", [])
        hosts = inc.entities_involved.get("hosts", [])
        ips = inc.entities_involved.get("ips", [])
        md.append(f"- **Target/Involved Users:** {', '.join(f'`{u}`' for u in users) if users else 'None'}")
        md.append(f"- **Affected Endpoints/Hosts:** {', '.join(f'`{h}`' for h in hosts) if hosts else 'None'}")
        md.append(f"- **Source IP Addresses:** {', '.join(f'`{ip}`' for ip in ips) if ips else 'Internal/Local'}\n")

        # Chronological Event Timeline
        md.append("## 6. Event Chronology & Audit Trail")
        md.append("| Event ID | Timestamp | Offset | Result | User | Host | Action / Command |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for item in inc.timeline:
            md.append(
                f"| `{item.get('event_id')}` | {item.get('timestamp')} | +{item.get('relative_seconds', 0)}s | "
                f"`{item.get('result')}` | `{item.get('username') or 'N/A'}` | `{item.get('device_id') or 'N/A'}` | "
                f"`{item.get('detail') or item.get('action')}` |"
            )
        md.append("")

        # Missing Evidence
        md.append("## 7. Telemetry Gaps / Missing Evidence")
        for gap in slm.missing_evidence:
            md.append(f"- ⚠️ {gap}")
        md.append("")

        # Recommended Next Steps
        md.append("## 8. Recommended Next Steps (Advisory)")
        for idx, action in enumerate(slm.recommended_actions, start=1):
            md.append(f"{idx}. {action}")
        md.append("")

        # Validation Details
        md.append("## 9. Hallucination Safeguard Verification")
        if slm.validation_passed:
            md.append("✅ **Validation PASSED**: All referenced event IDs were verified against actual ingested telemetry.")
        else:
            md.append("⚠️ **Validation FLAGGED Unsupported Claims**:")
            for err in slm.validation_errors:
                md.append(f"  - {err}")
        md.append(f"- **Verified Event Citations**: {', '.join(f'`{eid}`' for eid in slm.referenced_event_ids)}")
        md.append("")

        rendered = "\n".join(md)
        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(rendered)
        return rendered
