"""
PDF Report Exporter for PS02 using ReportLab.
Generates an executive SOC triage report ready for leadership review and offline archival.
"""

from pathlib import Path
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)

from src.schema import TriageReport


class PDFReportExporter:
    @staticmethod
    def export(report: TriageReport, output_path: Path | str) -> str:
        """Render a professional PDF report from TriageReport data."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=6
        )
        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        )
        body_bold = ParagraphStyle(
            'ReportBodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )
        notice_style = ParagraphStyle(
            'NoticeStyle',
            parent=body_style,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#991B1B')
        )

        story = []

        inc = report.incident
        slm = report.slm_analysis
        prov = report.provenance

        # Header Title
        story.append(Paragraph("<b>PS02 OFFLINE SECURITY INCIDENT TRIAGE REPORT</b>", title_style))
        story.append(Paragraph(f"<b>Case Title:</b> {slm.title}", styles['Heading3']))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

        # Severity Badge Color
        sev_color_hex = {
            "Critical": "#DC2626",
            "High": "#EA580C",
            "Medium": "#D97706",
            "Low": "#16A34A",
            "Informational": "#2563EB"
        }.get(inc.severity.value, "#475569")

        # Metadata Table
        meta_data = [
            [Paragraph("<b>Incident ID:</b>", body_style), Paragraph(f"<code>{inc.incident_id}</code>", body_style),
             Paragraph("<b>Authoritative Severity:</b>", body_style), Paragraph(f"<b><font color='{sev_color_hex}'>{inc.severity.value.upper()} ({inc.severity_score}/100)</font></b>", body_style)],
            [Paragraph("<b>Operating Mode:</b>", body_style), Paragraph("100% Offline (Zero Cloud)", body_style),
             Paragraph("<b>Local Model:</b>", body_style), Paragraph(slm.model_name[:28], body_style)],
            [Paragraph("<b>Evidence Citations:</b>", body_style), Paragraph(f"{len(slm.referenced_event_ids)} events verified", body_style),
             Paragraph("<b>Inference Latency:</b>", body_style), Paragraph(f"{prov.get('inference_latency_ms', 0)} ms", body_style)],
            [Paragraph("<b>Target Users:</b>", body_style), Paragraph(", ".join(inc.entities_involved.get("users", [])) or "None", body_style),
             Paragraph("<b>Affected Devices:</b>", body_style), Paragraph(", ".join(inc.entities_involved.get("hosts", [])) or "None", body_style)]
        ]
        meta_table = Table(meta_data, colWidths=[110, 150, 120, 160])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # Advisory Callout Box
        advisory_box = Table(
            [[Paragraph(f"<b>HUMAN-IN-THE-LOOP ADVISORY:</b> {prov.get('human_in_the_loop_notice')}", notice_style)]],
            colWidths=[540]
        )
        advisory_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF2F2')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F87171')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(advisory_box)
        story.append(Spacer(1, 10))

        # 1. Executive Summary
        story.append(Paragraph("1. Executive Summary", h2_style))
        story.append(Paragraph(slm.executive_summary, body_style))
        story.append(Spacer(1, 8))

        # 2. Deterministic Severity Rationale
        story.append(Paragraph("2. Deterministic Severity Rationale", h2_style))
        for line in inc.severity_breakdown:
            story.append(Paragraph(f"• {line}", body_style))
        story.append(Spacer(1, 8))

        # 3. Triggered Detection Rules Table
        story.append(Paragraph("3. Triggered Detection Rules", h2_style))
        findings_table_data = [
            [Paragraph("<b>Rule Name</b>", body_bold), Paragraph("<b>Score</b>", body_bold),
             Paragraph("<b>Authorized</b>", body_bold), Paragraph("<b>Key Evidence IDs</b>", body_bold)]
        ]
        for f in inc.findings:
            auth_txt = "Yes (Ticket)" if f.is_authorized else "No (Unapproved)"
            findings_table_data.append([
                Paragraph(f.rule_name, body_style),
                Paragraph(f"+{f.severity_contribution}", body_style),
                Paragraph(auth_txt, body_style),
                Paragraph(", ".join(f.supporting_event_ids[:3]), body_style)
            ])
        ft = Table(findings_table_data, colWidths=[220, 50, 90, 180])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2F6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ft)
        story.append(Spacer(1, 8))

        # 4. Verified Facts vs Hypotheses
        story.append(Paragraph("4. Observed Facts vs. Hypotheses", h2_style))
        story.append(Paragraph("<b>Directly Evidenced Facts:</b>", body_bold))
        for fact in slm.facts:
            story.append(Paragraph(f"• [VERIFIED] {fact}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Plausible Hypotheses (Awaiting Confirmation):</b>", body_bold))
        for hypo in slm.hypotheses:
            story.append(Paragraph(f"• [HYPOTHESIS] {hypo}", body_style))
        story.append(Spacer(1, 8))

        # 5. Timeline Table (First 8 events)
        story.append(Paragraph("5. Event Chronology (Timeline)", h2_style))
        tl_data = [
            [Paragraph("<b>Event ID</b>", body_bold), Paragraph("<b>Time</b>", body_bold),
             Paragraph("<b>User</b>", body_bold), Paragraph("<b>Host</b>", body_bold),
             Paragraph("<b>Result</b>", body_bold), Paragraph("<b>Action / Detail</b>", body_bold)]
        ]
        for item in inc.timeline[:8]:
            tl_data.append([
                Paragraph(item.get("event_id", ""), body_style),
                Paragraph(str(item.get("timestamp", ""))[-8:], body_style),
                Paragraph(item.get("username", "N/A"), body_style),
                Paragraph(item.get("device_id", "N/A"), body_style),
                Paragraph(item.get("result", ""), body_style),
                Paragraph(str(item.get("detail", item.get("action", "")))[:30], body_style)
            ])
        tl_table = Table(tl_data, colWidths=[70, 60, 70, 70, 60, 210])
        tl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2F6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(tl_table)
        story.append(Spacer(1, 8))

        # 6. Recommended Next Steps
        story.append(Paragraph("6. Recommended Next Steps (Advisory Only)", h2_style))
        for idx, act in enumerate(slm.recommended_actions, start=1):
            story.append(Paragraph(f"<b>{idx}.</b> {act}", body_style))
        story.append(Spacer(1, 8))

        # Footer Provenance
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=6))
        story.append(Paragraph(
            f"Report Generated: {prov.get('generated_at')} | Participant: {prov.get('participant')} | "
            f"Hallucination Safeguard: {'PASSED' if slm.validation_passed else 'FLAGGED'}",
            notice_style
        ))

        doc.build(story)
        return str(path)
