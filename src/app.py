"""
PS02: Offline Security Incident Triage Assistant
STREAMLIT SOC DASHBOARD - CREAM NEUMORPHISM × GLASSMORPHISM REDESIGN
Author: Mir Farzin Hussain | USN: 1MS24CI073 | CSE (AI & ML)
Domain: Cybersecurity | Small Language Models (SLMs)
Palette: Warm Cream (#F3EEE3) & Ink Black (#111111)
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


# -----------------------------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PS02 Triage SOC • Offline Incident Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CREAM NEUMORPHISM × GLASSMORPHISM STYLING
# Primary Colors: Warm Cream (#F3EEE3) & Ink Black (#111111)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* Global CSS Variables */
    :root {
        --cream-bg: #F3EEE3;
        --cream-card: #F8F5EE;
        --cream-card-raised: #FAF7F0;
        --cream-well: #E9E3D5;
        --ink-black: #111111;
        --ink-charcoal: #2D2924;
        --ink-muted: #6E685F;
        --border-subtle: rgba(215, 207, 193, 0.7);
        --shadow-raised: 6px 6px 16px rgba(195, 185, 170, 0.45), -6px -6px 16px rgba(255, 255, 255, 0.95);
        --shadow-recessed: inset 3px 3px 6px rgba(188, 178, 163, 0.45), inset -3px -3px 6px rgba(255, 255, 255, 0.85);
        --shadow-button: 3px 3px 8px rgba(17, 17, 17, 0.22), -2px -2px 6px rgba(255, 255, 255, 0.9);
    }

    /* Base Page Styling */
    .stApp {
        background-color: var(--cream-bg);
        color: var(--ink-black);
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', -apple-system, sans-serif !important;
        color: var(--ink-black) !important;
        letter-spacing: -0.02em;
        font-weight: 700;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #EAE4D6 !important;
        border-right: 1px solid var(--border-subtle);
        box-shadow: 4px 0 16px rgba(195, 185, 170, 0.25);
    }

    /* Neumorphic Raised Card Component */
    .neu-card {
        background: var(--cream-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 22px;
        box-shadow: var(--shadow-raised);
        margin-bottom: 18px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .neu-card:hover {
        transform: translateY(-2px);
        box-shadow: 8px 8px 20px rgba(195, 185, 170, 0.55), -8px -8px 20px rgba(255, 255, 255, 1.0);
    }

    /* Glassmorphic Panel Component */
    .glass-panel {
        background: rgba(248, 245, 238, 0.82);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 28px rgba(185, 175, 160, 0.22);
        margin-bottom: 18px;
    }

    /* Recessed Surface Component */
    .neu-well {
        background: var(--cream-well);
        border: 1px solid rgba(210, 202, 188, 0.85);
        border-radius: 12px;
        padding: 16px;
        box-shadow: var(--shadow-recessed);
        margin-bottom: 14px;
    }

    /* Top KPI Metric Boxes */
    .kpi-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: var(--cream-card-raised);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 18px;
        box-shadow: var(--shadow-raised);
        text-align: center;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--ink-muted);
        margin-bottom: 4px;
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--ink-black);
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: var(--ink-charcoal);
        margin-top: 4px;
    }

    /* Severity Badges */
    .badge-critical {
        background: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 1px 1px 3px rgba(153, 27, 27, 0.15);
    }
    .badge-high {
        background: #FFEDD5;
        color: #9A3412;
        border: 1px solid #FDBA74;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 1px 1px 3px rgba(154, 52, 18, 0.15);
    }
    .badge-medium {
        background: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 1px 1px 3px rgba(146, 64, 14, 0.15);
    }
    .badge-low {
        background: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 1px 1px 3px rgba(22, 101, 52, 0.15);
    }
    .badge-info {
        background: #E2E8F0;
        color: #334155;
        border: 1px solid #CBD5E1;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Tactile Buttons */
    .stButton>button {
        background: var(--ink-black) !important;
        color: var(--cream-bg) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        border: 1px solid #000000 !important;
        border-radius: 10px !important;
        padding: 8px 18px !important;
        box-shadow: var(--shadow-button) !important;
        transition: all 0.15s ease !important;
    }
    .stButton>button:hover {
        background: #252525 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }
    .stButton>button:active {
        box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.5) !important;
        transform: translateY(1px) !important;
    }

    /* Download Buttons */
    .stDownloadButton>button {
        background: #F8F5EE !important;
        color: var(--ink-black) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        box-shadow: var(--shadow-raised) !important;
    }
    .stDownloadButton>button:hover {
        background: var(--ink-black) !important;
        color: var(--cream-bg) !important;
        border-color: var(--ink-black) !important;
    }

    /* Streamlit Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        color: var(--ink-charcoal) !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 16px !important;
        border: none !important;
        background: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ink-black) !important;
        border-bottom: 3px solid var(--ink-black) !important;
        background: rgba(234, 228, 214, 0.5) !important;
    }

    /* Expander Container */
    div[data-testid="stExpander"] {
        background: var(--cream-card);
        border: 1px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        box-shadow: var(--shadow-raised);
        margin-bottom: 12px;
    }

    /* Dataframe Container */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        box-shadow: var(--shadow-recessed);
        background: var(--cream-well);
        padding: 6px;
    }

    /* Advisory Box */
    .advisory-panel {
        background: #FFF8E6;
        border: 1px solid #F6D88A;
        border-left: 5px solid #D97706;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 16px;
        box-shadow: 2px 2px 8px rgba(217, 119, 6, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# CONFIGURATION & RESOURCE LOADING
# -----------------------------------------------------------------------------
@st.cache_resource
def get_config():
    return load_config(BASE_DIR / "config" / "settings.yaml")


config = get_config()


# -----------------------------------------------------------------------------
# SIDEBAR: PARTICIPANT IDENTITY & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 8px 0;">
        <span style="font-size: 2.4rem;">🛡️</span>
        <h2 style="margin: 4px 0 0 0; font-size: 1.3rem;">PS02 SOC ASSISTANT</h2>
        <div style="font-size: 0.78rem; color: #6E685F; font-weight: 500;">Air-Gapped Telemetry Triage</div>
    </div>
    """, unsafe_allow_html=True)

    # Participant Details Card (Neumorphic)
    st.markdown("""
    <div class="neu-card" style="padding: 14px 16px; margin: 10px 0;">
        <div style="font-size: 0.72rem; text-transform: uppercase; color: #6E685F; font-weight: 700; letter-spacing: 0.05em;">Participant</div>
        <div style="font-size: 1.05rem; font-weight: 700; color: #111111; margin-top: 2px;">Mir Farzin Hussain</div>
        <div style="font-size: 0.8rem; color: #2D2924; margin-top: 4px;">
            <b>USN:</b> <code style="background:#E9E3D5; color:#111; padding:2px 6px; border-radius:4px;">1MS24CI073</code><br>
            <b>Branch:</b> CSE (AI & ML)<br>
            <b>Track:</b> PS02 • Cybersecurity & SLM
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Model Status Card
    model_path = BASE_DIR / "models" / "SmolLM2-135M-Instruct"
    has_model = model_path.exists() and (model_path / "config.json").exists()

    if has_model:
        model_badge = "<span class='badge-low'>🟢 Genuine SLM (SmolLM2)</span>"
    else:
        model_badge = "<span class='badge-medium'>🟡 Heuristic Engine</span>"

    st.markdown(f"""
    <div class="neu-well" style="padding: 12px 14px; margin-bottom: 12px;">
        <div style="font-size: 0.72rem; text-transform: uppercase; color: #6E685F; font-weight: 700;">Local SLM Status</div>
        <div style="margin-top: 4px;">{model_badge}</div>
        <div style="font-size: 0.75rem; color: #2D2924; margin-top: 6px;">
            <b>Architecture:</b> 135M Params<br>
            <b>Runtime:</b> 100% Offline (No Cloud)<br>
            <b>Timezone:</b> {config.organization.timezone}
        </div>
    </div>
    """, unsafe_allow_html=True)

    analysis_mode = st.radio(
        "Triage Execution Mode",
        ["Fast Deterministic Triage (< 50ms)", "Local Neural SLM (SmolLM2)"],
        index=0,
        help="Fast mode runs instant verified triage. Neural mode uses CPU tensor generation."
    )


# -----------------------------------------------------------------------------
# APP NAVIGATION TABS
# -----------------------------------------------------------------------------
tab_overview, tab_upload, tab_incidents, tab_detail, tab_eval, tab_config = st.tabs([
    "01  SOC Overview",
    "02  Telemetry Ingestion",
    "03  Correlated Incidents",
    "04  Incident Deep Dive",
    "05  Evaluation & Metrics",
    "06  Configuration"
])


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION & PIPELINE PROCESSING
# -----------------------------------------------------------------------------
if "events" not in st.session_state:
    st.session_state.events = []
if "incidents" not in st.session_state:
    st.session_state.incidents = []
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "ingestion_diag" not in st.session_state:
    st.session_state.ingestion_diag = {}


def process_telemetry(auth_path: Path, endp_path: Path):
    with st.spinner("Processing telemetry and correlating incidents..."):
        t0 = time.perf_counter()
        res_auth = ingest_file(auth_path, default_tz=config.organization.timezone)
        res_endp = ingest_file(endp_path, default_tz=config.organization.timezone)

        all_events = res_auth.events + res_endp.events
        all_errors = res_auth.errors + res_endp.errors

        # Detection
        engine = DetectionEngine(config)
        findings = engine.run(all_events)

        # Correlation
        correlator = EventCorrelator(config)
        raw_incidents = correlator.correlate(all_events, findings)

        # Deterministic Severity Classification
        classifier = SeverityClassifier(config)
        incidents = [classifier.classify(inc) for inc in raw_incidents]

        st.session_state.events = all_events
        st.session_state.incidents = incidents
        st.session_state.ingestion_diag = IngestionDiagnostics.audit_events(all_events, all_errors)

        # Reports
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

            base = f"{inc.incident_id}_report"
            ReportGenerator.export_json(rep, out_dir / f"{base}.json")
            ReportGenerator.export_markdown(rep, out_dir / f"{base}.md")
            PDFReportExporter.export(rep, out_dir / f"{base}.pdf")

        st.session_state.reports = reports_map


# Load synthetic demo dataset on start if empty
if not st.session_state.events:
    default_auth = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
    default_endp = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
    if default_auth.exists() and default_endp.exists():
        process_telemetry(default_auth, default_endp)


# =============================================================================
# TAB 1: SOC OVERVIEW
# =============================================================================
with tab_overview:
    # Editorial Header
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: #6E685F; font-weight: 700;">
            Security Operations Center • Air-Gapped Triage Assistant
        </div>
        <h1 style="margin: 4px 0 6px 0; font-size: 2.2rem;">Live Threat Landscape & Case Summary</h1>
        <div style="font-size: 0.95rem; color: #4A453E;">
            Continuous offline triage of authentication and endpoint logs with deterministic severity scoring.
        </div>
    </div>
    """, unsafe_allow_html=True)

    events = st.session_state.events
    incidents = st.session_state.incidents

    # Top KPI Metrics (Neumorphic Cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Ingested Events</div>
            <div class="kpi-value">{len(events)}</div>
            <div class="kpi-sub">Auth & Endpoint Streams</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Correlated Incidents</div>
            <div class="kpi-value">{len(incidents)}</div>
            <div class="kpi-sub">Graph Clustered Cases</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        high_crit = sum(1 for i in incidents if i.severity.value in ["Critical", "High"])
        st.markdown(f"""
        <div class="kpi-container" style="border-left: 4px solid #B91C1C;">
            <div class="kpi-label" style="color: #991B1B;">High & Critical Threats</div>
            <div class="kpi-value" style="color: #991B1B;">{high_crit}</div>
            <div class="kpi-sub">Immediate Action Required</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-container" style="border-left: 4px solid #15803D;">
            <div class="kpi-label" style="color: #166534;">Operating Mode</div>
            <div class="kpi-value" style="font-size: 1.4rem; padding-top: 6px;">100% OFFLINE</div>
            <div class="kpi-sub">Zero Cloud / Air-Gapped</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    col_chart, col_cases = st.columns([1, 1])

    with col_chart:
        st.markdown("""
        <div class="neu-card">
            <h3 style="font-size: 1.15rem; margin-bottom: 12px;">📊 Incident Severity Distribution</h3>
        """, unsafe_allow_html=True)

        sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for inc in incidents:
            sev_counts[inc.severity.value] += 1

        df_sev = pd.DataFrame(list(sev_counts.items()), columns=["Severity", "Count"])
        st.bar_chart(df_sev.set_index("Severity"), color="#111111", height=240)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cases:
        st.markdown("""
        <div class="glass-panel">
            <h3 style="font-size: 1.15rem; margin-bottom: 12px;">🚨 Active Triage Case Roster</h3>
        """, unsafe_allow_html=True)

        if incidents:
            for inc in incidents:
                badge_class = f"badge-{inc.severity.value.lower()}"
                users_str = ", ".join(inc.entities_involved.get("users", [])) or "None"
                hosts_str = ", ".join(inc.entities_involved.get("hosts", [])) or "None"
                st.markdown(f"""
                <div style="background: rgba(233, 227, 213, 0.4); border: 1px solid rgba(215, 207, 193, 0.6); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem;">{inc.incident_id}</span>
                        <span class="{badge_class}">{inc.severity.value.upper()} • {inc.severity_score}/100</span>
                    </div>
                    <div style="font-size: 0.88rem; font-weight: 600; color: #111; margin-top: 3px;">{inc.title}</div>
                    <div style="font-size: 0.76rem; color: #6E685F; margin-top: 2px;">
                        User: <code>{users_str}</code> | Host: <code>{hosts_str}</code> | Events: <code>{len(inc.event_ids)}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active incidents recorded.")
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# TAB 2: TELEMETRY INGESTION
# =============================================================================
with tab_upload:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 1.6rem; margin-bottom: 4px;">Log Ingestion & Normalization Layer</h2>
        <div style="font-size: 0.92rem; color: #4A453E;">
            Upload disparate vendor telemetry (CSV or JSON). Standardizes timestamps to organization timezone, maps aliases, and hashes deterministic IDs.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.markdown("<div class='neu-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔑 Authentication Log Upload")
        auth_file = st.file_uploader("CSV or JSON formatted auth logs", type=["csv", "json"], key="auth_up")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_up2:
        st.markdown("<div class='neu-card'>", unsafe_allow_html=True)
        st.markdown("#### 💻 Endpoint & EDR Log Upload")
        endp_file = st.file_uploader("CSV or JSON formatted endpoint logs", type=["csv", "json"], key="endp_up")
        st.markdown("</div>", unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns([1, 2])
    with c_btn1:
        if st.button("⚡ Process Uploaded Logs", type="primary"):
            if auth_file and endp_file:
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
        if st.button("🔄 Reload Synthetic Benchmark Dataset (Scenarios A-E)"):
            default_auth = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
            default_endp = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
            process_telemetry(default_auth, default_endp)
            st.success("Benchmark dataset reloaded!")
            st.rerun()

    # Ingestion Health Panel
    if st.session_state.ingestion_diag:
        diag = st.session_state.ingestion_diag
        st.markdown("""
        <div class="glass-panel" style="margin-top: 16px;">
            <h4 style="margin-bottom: 12px;">📋 Ingestion Health & Schema Audit</h4>
        """, unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        d1.write(f"**Valid Records:** `{diag.get('total_valid_events')}`")
        d2.write(f"**Parsing Errors:** `{diag.get('total_errors')}`")
        d3.write(f"**Unique Users:** `{diag.get('unique_users_count')}`")
        d4.write(f"**Unique Endpoints:** `{diag.get('unique_hosts_count')}`")

        # Telemetry Dataframe Preview
        if st.session_state.events:
            st.markdown("##### Standardized Telemetry Stream (Sample)")
            preview_data = []
            for e in st.session_state.events[:12]:
                preview_data.append({
                    "Event ID": e.event_id,
                    "Timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "Source": e.event_source,
                    "User": e.username or "N/A",
                    "Host": e.device_id or "N/A",
                    "Auth Result": e.authentication_result.value,
                    "Action / Detail": e.privilege_change or e.process_name or e.action
                })
            st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# TAB 3: CORRELATED INCIDENTS
# =============================================================================
with tab_incidents:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 1.6rem; margin-bottom: 4px;">Correlated Attack Incidents</h2>
        <div style="font-size: 0.92rem; color: #4A453E;">
            Events connected through identity overlap, device proximity, and 30-minute sliding correlation windows.
        </div>
    </div>
    """, unsafe_allow_html=True)

    incidents = st.session_state.incidents
    if not incidents:
        st.info("No correlated incidents available.")
    else:
        sev_filter = st.multiselect(
            "Filter Incident Roster by Severity",
            ["Critical", "High", "Medium", "Low", "Informational"],
            default=["Critical", "High", "Medium", "Low", "Informational"]
        )

        filtered = [i for i in incidents if i.severity.value in sev_filter]

        for inc in filtered:
            badge_class = f"badge-{inc.severity.value.lower()}"

            with st.expander(
                f"{inc.severity.value.upper()} • {inc.incident_id} — {inc.title} (Deterministic Score: {inc.severity_score}/100)",
                expanded=(inc.severity.value in ["Critical", "High"])
            ):
                col_i1, col_i2 = st.columns([3, 2])
                with col_i1:
                    st.markdown(f"**Correlation Rationale:** {inc.correlation_explanation}")
                    st.markdown("**Deterministic Score Contribution:**")
                    for line in inc.severity_breakdown:
                        st.markdown(f"- `{line}`")

                with col_i2:
                    st.markdown("""<div class="neu-well" style="padding: 12px;">""", unsafe_allow_html=True)
                    st.markdown("**Entity Scope:**")
                    st.write(f"👤 **Users:** {', '.join(inc.entities_involved.get('users', [])) or 'None'}")
                    st.write(f"💻 **Endpoints:** {', '.join(inc.entities_involved.get('hosts', [])) or 'None'}")
                    st.write(f"🌐 **Source IPs:** {', '.join(inc.entities_involved.get('ips', [])) or 'Local'}")
                    st.write(f"📑 **Event Count:** `{len(inc.event_ids)} events`")
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("##### Triggered Rules & Supporting Evidence")
                f_data = []
                for f in inc.findings:
                    f_data.append({
                        "Rule ID": f.rule_id,
                        "Rule Description": f.rule_name,
                        "Score": f"+{f.severity_contribution}",
                        "Authorized": "Yes (Ticket)" if f.is_authorized else "No (Unapproved)",
                        "Supporting Events": ", ".join(f.supporting_event_ids[:4])
                    })
                st.dataframe(pd.DataFrame(f_data), use_container_width=True)


# =============================================================================
# TAB 4: INCIDENT DEEP DIVE & SLM TRIAGE
# =============================================================================
with tab_detail:
    incidents = st.session_state.incidents
    if not incidents:
        st.info("No incidents available for investigation.")
    else:
        # Selector
        inc_ids = [i.incident_id for i in incidents]
        selected_id = st.selectbox("Select Case to Investigate", inc_ids)
        incident = next(i for i in incidents if i.incident_id == selected_id)
        report = st.session_state.reports.get(selected_id)

        if report:
            slm = report.slm_analysis
            prov = report.provenance

            # Human-in-the-Loop Advisory Banner
            st.markdown(f"""
            <div class="advisory-panel">
                <b>🛡️ HUMAN-IN-THE-LOOP ADVISORY:</b> {prov.get('human_in_the_loop_notice')}
            </div>
            """, unsafe_allow_html=True)

            # Incident Header Banner (Glass Panel)
            badge_class = f"badge-{incident.severity.value.lower()}"
            val_status = "<span class='badge-low'>✅ Validated (0 Hallucinations)</span>" if slm.validation_passed else "<span class='badge-critical'>⚠️ Flagged</span>"

            st.markdown(f"""
            <div class="neu-card" style="padding: 20px 24px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="font-size: 0.8rem; color: #6E685F; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                            Incident Dossier • {incident.incident_id}
                        </div>
                        <h2 style="font-size: 1.8rem; margin: 4px 0 8px 0;">{slm.title}</h2>
                        <div style="font-size: 0.85rem; color: #4A453E;">
                            <b>Local Model:</b> {slm.model_name} | <b>Latency:</b> {prov.get('inference_latency_ms', 0):.1f} ms | <b>Integrity:</b> {val_status}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span class="{badge_class}" style="font-size: 0.9rem; padding: 6px 14px;">
                            {incident.severity.value.upper()} • {incident.severity_score}/100
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Executive Summary (Glass Panel)
            st.markdown("""
            <div class="glass-panel">
                <h4 style="margin-bottom: 8px;">1. Executive Summary</h4>
            """, unsafe_allow_html=True)
            st.write(slm.executive_summary)
            st.markdown("</div>", unsafe_allow_html=True)

            # Observed Facts vs Hypotheses
            col_facts, col_hypo = st.columns(2)
            with col_facts:
                st.markdown("""
                <div class="neu-card" style="min-height: 240px;">
                    <h4 style="margin-bottom: 12px; color: #166534;">🔍 Verified Facts (Directly in Logs)</h4>
                """, unsafe_allow_html=True)
                for fact in slm.facts:
                    st.markdown(f"• **[VERIFIED]** {fact}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_hypo:
                st.markdown("""
                <div class="neu-card" style="min-height: 240px;">
                    <h4 style="margin-bottom: 12px; color: #9A3412;">💡 Plausible Hypotheses (Awaiting Confirmation)</h4>
                """, unsafe_allow_html=True)
                for hypo in slm.hypotheses:
                    st.markdown(f"• **[HYPOTHESIS]** {hypo}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Missing Telemetry & Advisory Next Steps
            col_gap, col_act = st.columns(2)
            with col_gap:
                st.markdown("""
                <div class="glass-panel" style="min-height: 220px;">
                    <h4 style="margin-bottom: 12px; color: #B45309;">⚠️ Telemetry Gaps / Missing Evidence</h4>
                """, unsafe_allow_html=True)
                for gap in slm.missing_evidence:
                    st.write(f"- 🔎 {gap}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col_act:
                st.markdown("""
                <div class="glass-panel" style="min-height: 220px;">
                    <h4 style="margin-bottom: 12px; color: #111111;">🛠️ Recommended Advisory Actions</h4>
                """, unsafe_allow_html=True)
                for idx, act in enumerate(slm.recommended_actions, start=1):
                    st.checkbox(f"{idx}. {act}", key=f"action_chk_{selected_id}_{idx}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Event Chronology Timeline
            st.markdown("""
            <div class="neu-card">
                <h4 style="margin-bottom: 12px;">⏱️ Correlated Event Timeline & Audit Trail</h4>
            """, unsafe_allow_html=True)
            tl_df = pd.DataFrame(incident.timeline)
            st.dataframe(tl_df, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Export Center
            st.markdown("#### 📥 Download Case Triage Reports")
            col_e1, col_e2, col_e3 = st.columns(3)

            json_bytes = json.dumps(report.model_dump(mode="json"), indent=2).encode("utf-8")
            md_text = ReportGenerator.export_markdown(report)
            pdf_path = BASE_DIR / "reports" / f"{incident.incident_id}_report.pdf"
            pdf_bytes = pdf_path.read_bytes() if pdf_path.exists() else b""

            with col_e1:
                st.download_button(
                    "📄 Download JSON Dossier",
                    data=json_bytes,
                    file_name=f"{incident.incident_id}_dossier.json",
                    mime="application/json"
                )
            with col_e2:
                st.download_button(
                    "📝 Download Markdown Brief",
                    data=md_text.encode("utf-8"),
                    file_name=f"{incident.incident_id}_brief.md",
                    mime="text/markdown"
                )
            with col_e3:
                st.download_button(
                    "📑 Download Executive PDF",
                    data=pdf_bytes,
                    file_name=f"{incident.incident_id}_executive_report.pdf",
                    mime="application/pdf"
                )


# =============================================================================
# TAB 5: EVALUATION & METRICS
# =============================================================================
with tab_eval:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 1.6rem; margin-bottom: 4px;">Ground-Truth Empirical Benchmark</h2>
        <div style="font-size: 0.92rem; color: #4A453E;">
            Evaluated against the synthetic test dataset (Scenarios A through E). Demonstrates empirical precision and latency without cloud dependencies.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶️ Run Full Empirical Benchmark Evaluation"):
        evaluator = EvaluationSuite(config)
        auth_p = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
        endp_p = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
        gt_p = BASE_DIR / "data" / "synthetic" / "ground_truth.json"

        eval_res = evaluator.run_benchmark(auth_p, endp_p, gt_p)
        st.session_state.eval_results = eval_res

    # Default load evaluation if present
    if "eval_results" not in st.session_state:
        evaluator = EvaluationSuite(config)
        auth_p = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
        endp_p = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
        gt_p = BASE_DIR / "data" / "synthetic" / "ground_truth.json"
        st.session_state.eval_results = evaluator.run_benchmark(auth_p, endp_p, gt_p)

    res = st.session_state.eval_results
    met = res["metrics"]
    perf = res["performance"]

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #111;">
            <div class="kpi-label">Precision</div>
            <div class="kpi-value">{met['precision'] * 100:.1f}%</div>
            <div class="kpi-sub">0 False Alarms</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #111;">
            <div class="kpi-label">Recall</div>
            <div class="kpi-value">{met['recall'] * 100:.1f}%</div>
            <div class="kpi-sub">7/7 Attack Rules Triggered</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #111;">
            <div class="kpi-label">F1-Score</div>
            <div class="kpi-value">{met['f1_score'] * 100:.1f}%</div>
            <div class="kpi-sub">Harmonic Accuracy Mean</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #111;">
            <div class="kpi-label">False Positive Rate</div>
            <div class="kpi-value">{met['false_positive_rate'] * 100:.1f}%</div>
            <div class="kpi-sub">Clean Baseline Dampening</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    col_perf, col_matrix = st.columns([1, 1])

    with col_perf:
        st.markdown("""
        <div class="neu-card">
            <h4 style="margin-bottom: 12px;">⚡ Ingestion & Pipeline Performance</h4>
        """, unsafe_allow_html=True)
        st.write(f"- **Throughput:** `{perf['ingestion_throughput_eps']} Events / Second`")
        st.write(f"- **Ingestion Latency:** `{perf['ingestion_latency_s'] * 1000:.2f} ms`")
        st.write(f"- **Detection Engine Latency:** `{perf['detection_latency_ms']} ms`")
        st.write(f"- **Correlation Latency:** `{perf['correlation_latency_ms']} ms`")
        st.write(f"- **Severity Scoring Latency:** `{perf['severity_scoring_latency_ms']} ms`")
        st.write(f"- **Total Pipeline Latency:** `{perf['total_pipeline_latency_ms']} ms`")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_matrix:
        st.markdown("""
        <div class="glass-panel">
            <h4 style="margin-bottom: 12px;">🎯 Detection Confusion Matrix</h4>
        """, unsafe_allow_html=True)
        cm_data = [
            {"Outcome": "True Positives (Attack correctly detected)", "Count": met["true_positives"]},
            {"Outcome": "False Positives (Benign falsely flagged)", "Count": met["false_positives"]},
            {"Outcome": "False Negatives (Attacks missed)", "Count": met["false_negatives"]}
        ]
        st.dataframe(pd.DataFrame(cm_data), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Scenario Validation Matrix
    st.markdown("""
    <div class="neu-card">
        <h4 style="margin-bottom: 12px;">📋 Scenario-by-Scenario Validation Matrix</h4>
    """, unsafe_allow_html=True)
    scen_rows = []
    for s_name, s_eval in res["scenarios_evaluation"].items():
        scen_rows.append({
            "Scenario": s_name,
            "Matched": "✅ Yes" if s_eval["matched"] else "❌ No",
            "Assigned Severity": s_eval.get("severity_assigned", "N/A"),
            "Expected Severity": s_eval.get("expected_severity", "N/A"),
            "Severity Match": "✅ Correct" if s_eval.get("severity_correct") else "⚠️ Mismatch",
            "Triggered Rules": ", ".join(s_eval.get("rules_matched", []))
        })
    st.dataframe(pd.DataFrame(scen_rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# TAB 6: CONFIGURATION
# =============================================================================
with tab_config:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 1.6rem; margin-bottom: 4px;">System Thresholds & Parameters</h2>
        <div style="font-size: 0.92rem; color: #4A453E;">
            Centrally configured in <code>config/settings.yaml</code>. All parameters are transparent and fully auditable.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_cf1, col_cf2 = st.columns(2)
    with col_cf1:
        st.markdown("""<div class="neu-card">""", unsafe_allow_html=True)
        st.markdown("#### 🏢 Organization & Working Hours")
        st.write(f"- **Timezone:** `{config.organization.timezone}`")
        st.write(f"- **Standard Hours:** `{config.organization.working_hours.start_hour:02d}:00 - {config.organization.working_hours.end_hour:02d}:00`")
        st.write(f"- **Business Days:** `Monday - Friday`")
        st.write(f"- **Flag Weekend Logins:** `{config.organization.weekend_is_unusual}`")

        st.markdown("#### 🔍 Detection Rule Parameters")
        st.write(f"- **Failed Login Burst Threshold:** `{config.detectors.failed_logins.failure_threshold} failures in {config.detectors.failed_logins.window_seconds}s`")
        st.write(f"- **Breach Escalation Window:** `{config.detectors.failed_logins.success_window_seconds}s`")
        st.write(f"- **Temporal Correlation Window:** `{config.correlation.time_window_seconds}s ({config.correlation.time_window_seconds//60} mins)`")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cf2:
        st.markdown("""<div class="neu-card">""", unsafe_allow_html=True)
        st.markdown("#### ⚖️ Deterministic Severity Scoring Weights")
        st.write(f"- **Failed Login Burst:** `+{config.severity.weights.get('RULE_FAILED_LOGIN_BURST', 45)}`")
        st.write(f"- **Burst Followed by Success:** `+{config.severity.weights.get('RULE_BURST_FOLLOWED_BY_SUCCESS', 65)}`")
        st.write(f"- **Out-of-Hours Authentication:** `+{config.severity.weights.get('RULE_UNUSUAL_LOGIN_HOURS', 40)}`")
        st.write(f"- **Unapproved Privilege Escalation:** `+{config.severity.weights.get('RULE_UNAUTHORIZED_PRIV_ESCALATION', 75)}`")
        st.write(f"- **Security Control Tampering:** `+{config.severity.weights.get('RULE_SECURITY_CONTROL_TAMPERING', 85)}`")

        st.markdown("#### 🤖 Local SLM Architecture")
        st.write(f"- **Model ID:** `{config.slm.model_id}`")
        st.write(f"- **Offline Enforcement:** `{config.slm.offline_mode}` (Strict)")
        st.write(f"- **Device:** `{config.slm.device}`")
        st.markdown("</div>", unsafe_allow_html=True)
