"""
PS02: Offline Security Incident Triage Assistant - Streamlit SOC Dashboard.
Author: Mir Farzin Hussain | USN: 1MS24CI073 | CSE (AI & ML)
Domain: Cybersecurity | Small Language Models (SLMs)
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.config import load_config
from src.ingestion.parser import ingest_file, IngestionResult
from src.ingestion.validator import IngestionDiagnostics
from src.detection.engine import DetectionEngine
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier
from src.slm.model_runner import LocalSLMRunner, RuleBasedSLMFallback
from src.reporting.generator import ReportGenerator
from src.reporting.pdf_exporter import PDFReportExporter
from src.evaluation.evaluator import EvaluationSuite


# Streamlit Page Setup
st.set_page_config(
    page_title="PS02 Offline Security Incident Triage Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Professional SOC Dark/Navy Theme)
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .badge-critical {
        background-color: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-high {
        background-color: #F97316; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-medium {
        background-color: #F59E0B; color: black; padding: 3px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-low {
        background-color: #10B981; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;
    }
    .badge-info {
        background-color: #3B82F6; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_config():
    return load_config(BASE_DIR / "config" / "settings.yaml")


config = get_config()

# Sidebar: Controls & Metadata
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("PS02 Triage SOC")
    st.caption("Offline Security Incident Triage Assistant")

    st.markdown("---")
    st.markdown("**Participant Information**")
    st.write("👤 **Name:** Mir Farzin Hussain")
    st.write("🎓 **USN:** `1MS24CI073`")
    st.write("🏛️ **Branch:** CSE (AI & ML)")
    st.write("🎯 **Problem Statement:** PS02")

    st.markdown("---")
    st.markdown("**Offline Status**")
    model_path = BASE_DIR / "models" / "SmolLM2-135M-Instruct"
    has_model = model_path.exists() and (model_path / "config.json").exists()
    if has_model:
        st.success("🟢 Genuine Local SLM Ready (Offline)")
    else:
        st.info("🟡 Heuristic Fallback Active")

    st.write(f"⚙️ **Timezone:** `{config.organization.timezone}`")
    st.write(f"🏢 **Hours:** `{config.organization.working_hours.start_hour:02d}:00 - {config.organization.working_hours.end_hour:02d}:00`")

    st.markdown("---")
    analysis_mode = st.radio(
        "SLM Inference Mode",
        ["Deterministic Fast Triage (Instant)", "Full Local Neural SLM (SmolLM2)"],
        index=0,
        help="Fast triage generates verified findings in milliseconds. Neural SLM uses CPU weights."
    )


# App Navigation Tabs
tab_overview, tab_upload, tab_incidents, tab_detail, tab_eval, tab_config = st.tabs([
    "📊 SOC Overview",
    "📁 Telemetry Ingestion",
    "🚨 Correlated Incidents",
    "🔍 Incident Deep Dive",
    "📈 Evaluation & Metrics",
    "⚙️ Configuration"
])


# Initialize Session State
if "events" not in st.session_state:
    st.session_state.events = []
if "incidents" not in st.session_state:
    st.session_state.incidents = []
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "ingestion_diag" not in st.session_state:
    st.session_state.ingestion_diag = {}


def process_telemetry(auth_path: Path, endp_path: Path):
    with st.spinner("Parsing logs, running detectors, and correlating incidents..."):
        t0 = time.perf_counter()
        res_auth = ingest_file(auth_path, default_tz=config.organization.timezone)
        res_endp = ingest_file(endp_path, default_tz=config.organization.timezone)

        all_events = res_auth.events + res_endp.events
        all_errors = res_auth.errors + res_endp.errors

        # Run Detection
        engine = DetectionEngine(config)
        findings = engine.run(all_events)

        # Correlate
        correlator = EventCorrelator(config)
        raw_incidents = correlator.correlate(all_events, findings)

        # Severity
        classifier = SeverityClassifier(config)
        incidents = [classifier.classify(inc) for inc in raw_incidents]

        st.session_state.events = all_events
        st.session_state.incidents = incidents
        st.session_state.ingestion_diag = IngestionDiagnostics.audit_events(all_events, all_errors)

        # Generate Reports
        reports_map = {}
        out_dir = BASE_DIR / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)

        for inc in incidents:
            if "Fast" in analysis_mode:
                analysis = RuleBasedSLMFallback.generate(inc, reason="Fast Deterministic Mode")
                latency = (time.perf_counter() - t0) * 1000
            else:
                runner = LocalSLMRunner(config)
                analysis, latency = runner.analyze(inc)

            rep = ReportGenerator.create_report(inc, analysis, inference_latency_ms=latency, offline_mode=True)
            reports_map[inc.incident_id] = rep

            # Export files
            base = f"{inc.incident_id}_report"
            ReportGenerator.export_json(rep, out_dir / f"{base}.json")
            ReportGenerator.export_markdown(rep, out_dir / f"{base}.md")
            PDFReportExporter.export(rep, out_dir / f"{base}.pdf")

        st.session_state.reports = reports_map


# Auto-load demo dataset on initial launch if empty
if not st.session_state.events:
    default_auth = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
    default_endp = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
    if default_auth.exists() and default_endp.exists():
        process_telemetry(default_auth, default_endp)


# =============================================================================
# TAB 1: SOC OVERVIEW
# =============================================================================
with tab_overview:
    st.subheader("🛡️ Security Operations Center (SOC) Live Dashboard")
    st.caption("Offline Security Incident Triage Assistant | Problem Statement PS02")

    events = st.session_state.events
    incidents = st.session_state.incidents

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Events Ingested", len(events))
    with c2:
        st.metric("Correlated Incidents", len(incidents))
    with c3:
        high_crit = sum(1 for i in incidents if i.severity.value in ["Critical", "High"])
        st.metric("High / Critical Threats", high_crit, delta=f"{high_crit} Urgent" if high_crit > 0 else "0", delta_color="inverse")
    with c4:
        st.metric("Operating Mode", "100% Offline", "Zero Cloud APIs")

    st.markdown("---")

    # Severity Distribution
    col_chart, col_summary = st.columns([1, 1])

    with col_chart:
        st.markdown("### 📊 Incident Severity Distribution")
        sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for inc in incidents:
            sev_counts[inc.severity.value] += 1

        df_sev = pd.DataFrame(list(sev_counts.items()), columns=["Severity", "Count"])
        st.bar_chart(df_sev.set_index("Severity"), color="#3B82F6")

    with col_summary:
        st.markdown("### 🚨 Current Active Case Summary")
        if incidents:
            for inc in incidents:
                badge_class = f"badge-{inc.severity.value.lower()}"
                st.markdown(
                    f"**{inc.incident_id}**: <span class='{badge_class}'>{inc.severity.value.upper()}</span> "
                    f"**{inc.title}** (Score: `{inc.severity_score}/100`)",
                    unsafe_allow_html=True
                )
                st.caption(f"Entities: {', '.join(inc.entities_involved.get('users', []))} | Host: {', '.join(inc.entities_involved.get('hosts', []))} | Events: {len(inc.event_ids)}")
        else:
            st.info("No incidents currently detected. Ingest telemetry logs to begin analysis.")


# =============================================================================
# TAB 2: TELEMETRY INGESTION
# =============================================================================
with tab_upload:
    st.subheader("📁 Log Ingestion and Normalization Engine")
    st.markdown("""
    Accepts **Authentication** and **Endpoint** logs in **CSV** or **JSON** format.
    The normalizer parses timestamps into the organization timezone, maps disparate vendor schemas,
    generates deterministic IDs, and preserves original raw logs without losing evidence.
    """)

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        auth_file = st.file_uploader("Upload Authentication Logs (CSV/JSON)", type=["csv", "json"], key="auth_up")
    with col_up2:
        endp_file = st.file_uploader("Upload Endpoint / EDR Logs (CSV/JSON)", type=["csv", "json"], key="endp_up")

    c_btn1, c_btn2 = st.columns([1, 3])
    with c_btn1:
        if st.button("🚀 Process Uploaded Logs", type="primary"):
            if auth_file and endp_file:
                # Save temp uploads
                tmp_auth = BASE_DIR / "data" / "temp_auth"
                tmp_endp = BASE_DIR / "data" / "temp_endp"
                tmp_auth.write_bytes(auth_file.getvalue())
                tmp_endp.write_bytes(endp_file.getvalue())
                process_telemetry(tmp_auth, tmp_endp)
                st.success("Uploaded telemetry processed successfully!")
                st.rerun()
            else:
                st.warning("Please upload both Authentication and Endpoint log files.")

    with c_btn2:
        if st.button("🔄 Reload Synthetic Evaluation Dataset (Scenarios A-E)"):
            default_auth = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
            default_endp = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
            process_telemetry(default_auth, default_endp)
            st.success("Synthetic evaluation dataset reloaded!")
            st.rerun()

    # Ingestion Diagnostics Table
    if st.session_state.ingestion_diag:
        st.markdown("---")
        st.markdown("### 📋 Ingestion Health & Audit Statistics")
        diag = st.session_state.ingestion_diag
        d1, d2, d3, d4 = st.columns(4)
        d1.write(f"**Valid Events:** `{diag.get('total_valid_events')}`")
        d2.write(f"**Ingestion Errors:** `{diag.get('total_errors')}`")
        d3.write(f"**Unique Users:** `{diag.get('unique_users_count')}`")
        d4.write(f"**Unique Hosts:** `{diag.get('unique_hosts_count')}`")

        # Telemetry Dataframe Preview
        if st.session_state.events:
            st.markdown("#### Sample Normalized Telemetry")
            preview_data = []
            for e in st.session_state.events[:10]:
                preview_data.append({
                    "Event ID": e.event_id,
                    "Timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Source": e.event_source,
                    "User": e.username,
                    "Device": e.device_id,
                    "Result": e.authentication_result.value,
                    "Action / Detail": e.privilege_change or e.process_name or e.action
                })
            st.dataframe(pd.DataFrame(preview_data), use_container_width=True)


# =============================================================================
# TAB 3: CORRELATED INCIDENTS
# =============================================================================
with tab_incidents:
    st.subheader("🚨 Correlated Security Incidents")
    st.caption("Incidents grouped by shared identity, endpoint, IP, and temporal correlation windows.")

    incidents = st.session_state.incidents
    if not incidents:
        st.info("No incidents detected.")
    else:
        # Severity Filter
        sev_filter = st.multiselect(
            "Filter by Severity",
            ["Critical", "High", "Medium", "Low", "Informational"],
            default=["Critical", "High", "Medium", "Low", "Informational"]
        )

        filtered = [i for i in incidents if i.severity.value in sev_filter]

        for inc in filtered:
            badge_color = {
                "Critical": "🔴 CRITICAL",
                "High": "🟠 HIGH",
                "Medium": "🟡 MEDIUM",
                "Low": "🟢 LOW",
                "Informational": "🔵 INFORMATIONAL"
            }.get(inc.severity.value, inc.severity.value)

            with st.expander(f"{badge_color} | {inc.incident_id}: {inc.title} (Score: {inc.severity_score}/100)", expanded=(inc.severity.value in ["Critical", "High"])):
                col_i1, col_i2 = st.columns([2, 1])
                with col_i1:
                    st.markdown(f"**Correlation Rationale:** {inc.correlation_explanation}")
                    st.markdown("**Deterministic Score Breakdown:**")
                    for b in inc.severity_breakdown:
                        st.write(f"- {b}")

                with col_i2:
                    st.markdown("**Involved Entities:**")
                    st.write(f"👤 Users: {', '.join(inc.entities_involved.get('users', [])) or 'None'}")
                    st.write(f"💻 Hosts: {', '.join(inc.entities_involved.get('hosts', [])) or 'None'}")
                    st.write(f"🌐 IPs: {', '.join(inc.entities_involved.get('ips', [])) or 'None'}")
                    st.write(f"📅 Participating Events: `{len(inc.event_ids)}`")

                # Triggered Rules
                st.markdown("**Triggered Detection Findings:**")
                f_data = []
                for f in inc.findings:
                    f_data.append({
                        "Rule ID": f.rule_id,
                        "Rule Name": f.rule_name,
                        "Score Contribution": f"+{f.severity_contribution}",
                        "Authorized": "Yes (Ticket)" if f.is_authorized else "No (Unapproved)",
                        "Key Evidence IDs": ", ".join(f.supporting_event_ids[:3])
                    })
                st.dataframe(pd.DataFrame(f_data), use_container_width=True)


# =============================================================================
# TAB 4: INCIDENT DEEP DIVE & SLM TRIAGE
# =============================================================================
with tab_detail:
    st.subheader("🔍 Incident Investigation & Local SLM Triage Briefing")

    incidents = st.session_state.incidents
    if not incidents:
        st.info("No incidents available for inspection.")
    else:
        inc_ids = [i.incident_id for i in incidents]
        selected_id = st.selectbox("Select Incident to Triage", inc_ids)
        incident = next(i for i in incidents if i.incident_id == selected_id)
        report = st.session_state.reports.get(selected_id)

        if report:
            slm = report.slm_analysis
            prov = report.provenance

            # Top Advisory Banner
            st.warning(f"🛡️ **HUMAN-IN-THE-LOOP ADVISORY:** {prov.get('human_in_the_loop_notice')}")

            # Overview Card
            c_d1, c_d2, c_d3 = st.columns([2, 1, 1])
            with c_d1:
                st.markdown(f"### {slm.title}")
                st.write(f"**Incident ID:** `{incident.incident_id}`")
            with c_d2:
                st.metric("Authoritative Severity", f"{incident.severity.value.upper()}", f"{incident.severity_score}/100")
            with c_d3:
                val_status = "✅ Verified" if slm.validation_passed else "⚠️ Flagged"
                st.metric("Hallucination Audit", val_status, f"{len(slm.referenced_event_ids)} Citations")

            st.markdown("---")

            # Executive Summary
            st.markdown("#### 1. Executive Summary")
            st.info(slm.executive_summary)

            # Verified Facts vs Hypotheses
            col_facts, col_hypo = st.columns(2)
            with col_facts:
                st.markdown("#### 🔍 Verified Facts (Grounded in Logs)")
                for fact in slm.facts:
                    st.write(f"✅ **[VERIFIED]** {fact}")

            with col_hypo:
                st.markdown("#### 💡 Plausible Hypotheses (Requiring Confirmation)")
                for hypo in slm.hypotheses:
                    st.write(f"🤔 **[HYPOTHESIS]** {hypo}")

            # Telemetry Gaps and Recommended Actions
            col_gap, col_act = st.columns(2)
            with col_gap:
                st.markdown("#### ⚠️ Missing Telemetry / Telemetry Gaps")
                for gap in slm.missing_evidence:
                    st.write(f"- 🔎 {gap}")

            with col_act:
                st.markdown("#### 🛠️ Recommended Safe Investigation Steps (Advisory)")
                for idx, act in enumerate(slm.recommended_actions, start=1):
                    checked = st.checkbox(f"{idx}. {act}", key=f"act_{selected_id}_{idx}")

            # Event Timeline Audit Trail
            st.markdown("---")
            st.markdown("#### ⏱️ Event Chronology & Audit Trail")
            tl_df = pd.DataFrame(incident.timeline)
            st.dataframe(tl_df, use_container_width=True)

            # Export Buttons
            st.markdown("---")
            st.markdown("#### 📥 Download Incident Triage Reports")
            col_exp1, col_exp2, col_exp3 = st.columns(3)

            json_bytes = json.dumps(report.model_dump(mode="json"), indent=2).encode("utf-8")
            md_text = ReportGenerator.export_markdown(report)
            pdf_path = BASE_DIR / "reports" / f"{incident.incident_id}_report.pdf"
            pdf_bytes = pdf_path.read_bytes() if pdf_path.exists() else b""

            with col_exp1:
                st.download_button(
                    "📄 Download JSON Report",
                    data=json_bytes,
                    file_name=f"{incident.incident_id}_triage_report.json",
                    mime="application/json"
                )
            with col_exp2:
                st.download_button(
                    "📝 Download Markdown Report",
                    data=md_text.encode("utf-8"),
                    file_name=f"{incident.incident_id}_triage_report.md",
                    mime="text/markdown"
                )
            with col_exp3:
                st.download_button(
                    "📑 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{incident.incident_id}_triage_report.pdf",
                    mime="application/pdf"
                )


# =============================================================================
# TAB 5: EVALUATION & METRICS
# =============================================================================
with tab_eval:
    st.subheader("📈 Ground-Truth Benchmark Evaluation")
    st.markdown("""
    **Evaluation Notice:** All reported metrics are evaluated against the labelled synthetic demonstration dataset
    (Scenarios A through E). This is an empirical validation of detection and correlation accuracy, not an enterprise production benchmark.
    """)

    if st.button("▶️ Execute Full Evaluation Suite"):
        evaluator = EvaluationSuite(config)
        auth_p = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
        endp_p = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
        gt_p = BASE_DIR / "data" / "synthetic" / "ground_truth.json"

        eval_res = evaluator.run_benchmark(auth_p, endp_p, gt_p)
        st.session_state.eval_results = eval_res

    if "eval_results" in st.session_state:
        res = st.session_state.eval_results
        met = res["metrics"]
        perf = res["performance"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precision", f"{met['precision'] * 100:.1f}%")
        m2.metric("Recall", f"{met['recall'] * 100:.1f}%")
        m3.metric("F1-Score", f"{met['f1_score'] * 100:.1f}%")
        m4.metric("False Positive Rate", f"{met['false_positive_rate'] * 100:.1f}%")

        st.markdown("---")
        st.markdown("#### ⚡ System Performance & Latencies")
        p1, p2, p3, p4 = st.columns(4)
        p1.write(f"**Ingestion Throughput:** `{perf['ingestion_throughput_eps']} EPS`")
        p2.write(f"**Detection Latency:** `{perf['detection_latency_ms']} ms`")
        p3.write(f"**Correlation Latency:** `{perf['correlation_latency_ms']} ms`")
        p4.write(f"**Pipeline Latency:** `{perf['total_pipeline_latency_ms']} ms`")

        st.markdown("---")
        st.markdown("#### 🎯 Scenario-by-Scenario Validation Matrix")
        scen_rows = []
        for s_name, s_eval in res["scenarios_evaluation"].items():
            scen_rows.append({
                "Scenario": s_name,
                "Matched": "✅ Yes" if s_eval["matched"] else "❌ No",
                "Assigned Severity": s_eval.get("severity_assigned", "N/A"),
                "Expected Severity": s_eval.get("expected_severity", "N/A"),
                "Severity Correct": "✅ Correct" if s_eval.get("severity_correct") else "⚠️ Mismatch",
                "Rules Matched": ", ".join(s_eval.get("rules_matched", []))
            })
        st.dataframe(pd.DataFrame(scen_rows), use_container_width=True)


# =============================================================================
# TAB 6: CONFIGURATION
# =============================================================================
with tab_config:
    st.subheader("⚙️ System Configuration & Thresholds")
    st.markdown("All parameters are loaded from `config/settings.yaml` and can be inspected here.")

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        st.markdown("#### Organization & Working Hours")
        st.write(f"- **Timezone:** `{config.organization.timezone}`")
        st.write(f"- **Working Hours:** `{config.organization.working_hours.start_hour}:00 - {config.organization.working_hours.end_hour}:00`")
        st.write(f"- **Working Days:** `{config.organization.working_days}` (Mon-Fri)")
        st.write(f"- **Flag Weekend:** `{config.organization.weekend_is_unusual}`")

        st.markdown("#### Detector Thresholds")
        st.write(f"- **Failed Login Threshold:** `{config.detectors.failed_logins.failure_threshold}` failures in `{config.detectors.failed_logins.window_seconds}`s")
        st.write(f"- **Escalate on Success Follow-Up:** `{config.detectors.failed_logins.escalate_on_success_after_burst}`")
        st.write(f"- **Correlation Window:** `{config.correlation.time_window_seconds}`s ({config.correlation.time_window_seconds//60} mins)")

    with col_cfg2:
        st.markdown("#### Severity Scoring Thresholds")
        st.write(f"- **Critical:** `>= {config.severity.thresholds.critical}`")
        st.write(f"- **High:** `>= {config.severity.thresholds.high}`")
        st.write(f"- **Medium:** `>= {config.severity.thresholds.medium}`")
        st.write(f"- **Low:** `>= {config.severity.thresholds.low}`")

        st.markdown("#### Small Language Model (SLM)")
        st.write(f"- **Model ID:** `{config.slm.model_id}`")
        st.write(f"- **Local Cache Path:** `{config.slm.local_model_path}`")
        st.write(f"- **Inference Device:** `{config.slm.device}`")
        st.write(f"- **Offline Enforcement:** `{config.slm.offline_mode}`")
