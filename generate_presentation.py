"""
Final Presentation Generator for PS02 Offline Security Incident Triage Assistant.
Replicates the visual language, typography, editorial hierarchy, and card treatments
of TARS_Hackathon_Deck.pdf while fulfilling the official 7-slide PS02 presentation format.

Generates:
1. PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pptx (Editable PowerPoint)
2. PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pdf (High-resolution PDF)
"""

import os
from pathlib import Path

# PPTX Imports
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ReportLab Imports
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "outputs" / "presentation_assets"
SCREENSHOTS_DIR = BASE_DIR / "outputs" / "screenshots" / "react_dashboard"

PPTX_PATH = BASE_DIR / "PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pptx"
PDF_PATH = BASE_DIR / "PS02_Offline_Security_Incident_Triage_Assistant_FINAL.pdf"

# Monochrome Editorial Color Palette (Matching TARS Reference Deck)
COLOR_WHITE = RGBColor(255, 255, 255)       # Canvas White
COLOR_INK = RGBColor(17, 17, 17)            # Deep Ink Black #111111
COLOR_DARK_PANEL = RGBColor(10, 10, 10)     # Panel Black #0A0A0A
COLOR_GREY_HEADING = RGBColor(115, 115, 115)# Muted Grey #737373
COLOR_GREY_BODY = RGBColor(70, 70, 70)      # Charcoal Body #464646
COLOR_GREY_LIGHT = RGBColor(130, 130, 130)  # Light Muted Grey #828282
COLOR_SURFACE = RGBColor(246, 246, 248)     # Card Surface Off-White #F6F6F8
COLOR_BORDER = RGBColor(226, 226, 230)      # Neutral Border #E2E2E6
COLOR_CONTAINER = RGBColor(236, 236, 240)   # Icon Container Grey #ECECF0
COLOR_EMERALD = RGBColor(22, 101, 52)       # Restrained Green #166534
COLOR_RED = RGBColor(185, 28, 28)           # Restrained Red #B91C1C
COLOR_AMBER = RGBColor(180, 83, 9)          # Restrained Amber #B45309

HEX_WHITE = HexColor('#FFFFFF')
HEX_INK = HexColor('#111111')
HEX_DARK_PANEL = HexColor('#0A0A0A')
HEX_GREY_HEADING = HexColor('#737373')
HEX_GREY_BODY = HexColor('#464646')
HEX_GREY_LIGHT = HexColor('#828282')
HEX_SURFACE = HexColor('#F6F6F8')
HEX_BORDER = HexColor('#E2E2E6')
HEX_CONTAINER = HexColor('#ECECF0')
HEX_EMERALD = HexColor('#166534')
HEX_RED = HexColor('#B91C1C')


def build_pptx_deck():
    """Generates the 7-slide native PowerPoint presentation."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_blank_slide():
        slide = prs.slides.add_slide(blank_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_WHITE
        bg.line.fill.background()
        return slide

    def add_card(slide, left, top, width, height, fill_color=COLOR_SURFACE, border_color=COLOR_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    def add_header(slide, section_tag, title_black, title_grey=None, subtitle=None):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_tag = tf.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_GREY_LIGHT
        p_tag.space_after = Pt(4)

        p_title1 = tf.add_paragraph()
        p_title1.text = title_black
        p_title1.font.size = Pt(24)
        p_title1.font.bold = True
        p_title1.font.color.rgb = COLOR_INK

        if title_grey:
            p_title2 = tf.add_paragraph()
            p_title2.text = title_grey
            p_title2.font.size = Pt(24)
            p_title2.font.bold = True
            p_title2.font.color.rgb = COLOR_GREY_HEADING

        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.size = Pt(11.5)
            p_sub.font.color.rgb = COLOR_GREY_BODY
            p_sub.space_before = Pt(4)

    # -------------------------------------------------------------------------
    # SLIDE 0: TITLE SLIDE (Matches TARS Page 1 Split Composition)
    # -------------------------------------------------------------------------
    s0 = add_blank_slide()

    # Right side dark panel
    right_panel = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.333), Inches(0), Inches(5.0), Inches(7.5))
    right_panel.fill.solid()
    right_panel.fill.fore_color.rgb = COLOR_DARK_PANEL
    right_panel.line.fill.background()

    # Cover image inside right panel
    cover_img_path = ASSETS_DIR / "cover_security_node.png"
    if cover_img_path.exists():
        s0.shapes.add_picture(str(cover_img_path), Inches(8.7), Inches(0.8), width=Inches(4.3))

    # Badge in right panel
    add_card(s0, Inches(8.7), Inches(6.4), Inches(4.2), Inches(0.6), fill_color=RGBColor(25, 25, 28), border_color=RGBColor(50, 50, 55))
    tb_b = s0.shapes.add_textbox(Inches(8.8), Inches(6.5), Inches(4.0), Inches(0.4))
    p_b = tb_b.text_frame.paragraphs[0]
    p_b.text = "100% OFFLINE • AIR-GAPPED SOC ASSISTANT"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # Left content area
    tb0 = s0.shapes.add_textbox(Inches(0.9), Inches(1.1), Inches(7.0), Inches(3.6))
    tf0 = tb0.text_frame
    tf0.word_wrap = True

    p_ev = tf0.paragraphs[0]
    p_ev.text = "TINYVERSE HACKATHON • PHASE 2 FINALS"
    p_ev.font.size = Pt(11)
    p_ev.font.bold = True
    p_ev.font.color.rgb = COLOR_GREY_LIGHT
    p_ev.space_after = Pt(14)

    p_t1 = tf0.add_paragraph()
    p_t1.text = "OFFLINE SECURITY"
    p_t1.font.size = Pt(44)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_INK

    p_t2 = tf0.add_paragraph()
    p_t2.text = "INCIDENT TRIAGE"
    p_t2.font.size = Pt(44)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_INK

    p_t3 = tf0.add_paragraph()
    p_t3.text = "ASSISTANT"
    p_t3.font.size = Pt(44)
    p_t3.font.bold = True
    p_t3.font.color.rgb = COLOR_GREY_HEADING
    p_t3.space_after = Pt(14)

    p_tag = tf0.add_paragraph()
    p_tag.text = "From raw security logs to evidence-backed incident investigations — entirely on-device."
    p_tag.font.size = Pt(15)
    p_tag.font.color.rgb = COLOR_GREY_BODY

    # Divider line
    line0 = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(5.1), Inches(6.8), Inches(0.02))
    line0.fill.solid()
    line0.fill.fore_color.rgb = COLOR_BORDER
    line0.line.fill.background()

    # Participant Meta Cards
    add_card(s0, Inches(0.9), Inches(5.4), Inches(3.25), Inches(1.4))
    tb_p1 = s0.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(2.8), Inches(1.1))
    tf_p1 = tb_p1.text_frame
    p_p1_l = tf_p1.paragraphs[0]
    p_p1_l.text = "PARTICIPANT NAME:"
    p_p1_l.font.size = Pt(9)
    p_p1_l.font.color.rgb = COLOR_GREY_LIGHT
    p_p1_v1 = tf_p1.add_paragraph()
    p_p1_v1.text = "Mir Farzin Hussain"
    p_p1_v1.font.size = Pt(12)
    p_p1_v1.font.bold = True
    p_p1_v1.font.color.rgb = COLOR_INK
    p_p1_v2 = tf_p1.add_paragraph()
    p_p1_v2.text = "USN: 1MS24CI073"
    p_p1_v2.font.size = Pt(10)
    p_p1_v2.font.color.rgb = COLOR_GREY_BODY

    add_card(s0, Inches(4.35), Inches(5.4), Inches(3.35), Inches(1.4))
    tb_p2 = s0.shapes.add_textbox(Inches(4.55), Inches(5.55), Inches(2.9), Inches(1.1))
    tf_p2 = tb_p2.text_frame
    p_p2_l = tf_p2.paragraphs[0]
    p_p2_l.text = "PROBLEM STATEMENT & DEPT:"
    p_p2_l.font.size = Pt(9)
    p_p2_l.font.color.rgb = COLOR_GREY_LIGHT
    p_p2_v1 = tf_p2.add_paragraph()
    p_p2_v1.text = "Problem Statement: PS02"
    p_p2_v1.font.size = Pt(12)
    p_p2_v1.font.bold = True
    p_p2_v1.font.color.rgb = COLOR_INK
    p_p2_v2 = tf_p2.add_paragraph()
    p_p2_v2.text = "CSE (AI & ML) • Phase 2"
    p_p2_v2.font.size = Pt(10)
    p_p2_v2.font.color.rgb = COLOR_GREY_BODY

    # -------------------------------------------------------------------------
    # SLIDE 1: THE PROBLEM & EXISTING SOLUTIONS (Matches TARS Page 2)
    # -------------------------------------------------------------------------
    s1 = add_blank_slide()

    # Right side dark panel "Why it matters?"
    add_card(s1, Inches(9.1), Inches(0.4), Inches(3.45), Inches(6.7), fill_color=COLOR_DARK_PANEL, border_color=None)
    tb_wim = s1.shapes.add_textbox(Inches(9.35), Inches(0.65), Inches(3.0), Inches(0.9))
    tf_wim = tb_wim.text_frame
    p_w1 = tf_wim.paragraphs[0]
    p_w1.text = "Why it matters?"
    p_w1.font.size = Pt(22)
    p_w1.font.bold = True
    p_w1.font.color.rgb = COLOR_WHITE
    p_w2 = tf_wim.add_paragraph()
    p_w2.text = "When context is fragmented, triage breaks down."
    p_w2.font.size = Pt(11)
    p_w2.font.color.rgb = COLOR_GREY_LIGHT

    card_wim_data = [
        ("Alert overload", "High event volumes overwhelm analyst capacity; low-frequency attack signals get lost."),
        ("Fragmented context", "Attacker steps span auth and endpoint silos without unified identity linkage."),
        ("Cloud dependency", "Restricted enclaves and defense sites cannot stream logs to cloud LLM APIs."),
        ("Evidence gaps", "Generic chatbots hallucinate; analysts need exact, auditable event citations.")
    ]
    for idx, (title, desc) in enumerate(card_wim_data):
        y_top = 1.65 + (idx * 1.25)
        add_card(s1, Inches(9.35), Inches(y_top), Inches(2.95), Inches(1.15), fill_color=COLOR_WHITE, border_color=None)
        tb_c = s1.shapes.add_textbox(Inches(9.5), Inches(y_top + 0.1), Inches(2.65), Inches(0.95))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = f"0{idx+1}  {title}"
        p_ct.font.size = Pt(11)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_INK
        p_cd = tf_c.add_paragraph()
        p_cd.text = desc
        p_cd.font.size = Pt(9.5)
        p_cd.font.color.rgb = COLOR_GREY_BODY
        p_cd.space_before = Pt(3)

    add_header(
        s1,
        "THE PROBLEM & EXISTING SOLUTIONS",
        "SECURITY TEAMS SEE EVERYTHING.",
        "BUT CAN'T INVESTIGATE EVERYTHING.",
        "Security Operations Centers process thousands of authentication and endpoint events. Manual triage is slow, subtle killchains are missed, and cloud AI introduces severe data leakage risks."
    )

    iceberg_path = ASSETS_DIR / "problem_iceberg.png"
    if iceberg_path.exists():
        s1.shapes.add_picture(str(iceberg_path), Inches(4.3), Inches(2.1), width=Inches(4.6))

    tb_cw = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(3.3), Inches(2.4))
    tf_cw = tb_cw.text_frame
    tf_cw.word_wrap = True
    p_cw1 = tf_cw.paragraphs[0]
    p_cw1.text = "EXISTING WORKFLOW LIMITATIONS"
    p_cw1.font.size = Pt(10)
    p_cw1.font.bold = True
    p_cw1.font.color.rgb = COLOR_GREY_LIGHT

    cw_points = [
        ("SIEM Rule Fatigue:", "Static rules trigger thousands of disparate alerts without multi-source correlation."),
        ("Manual Investigation:", "Analysts manually write SQL queries across auth and endpoint siloes."),
        ("Cloud AI Unsuitability:", "Air-gapped sites cannot send proprietary telemetry to external LLM APIs.")
    ]
    for h, b in cw_points:
        p_p = tf_cw.add_paragraph()
        p_p.space_before = Pt(6)
        r_h = p_p.add_run()
        r_h.text = h + " "
        r_h.font.bold = True
        r_h.font.size = Pt(10)
        r_h.font.color.rgb = COLOR_INK
        r_b = p_p.add_run()
        r_b.text = b
        r_b.font.size = Pt(9.5)
        r_b.font.color.rgb = COLOR_GREY_BODY

    # Who is affected
    tb_wia = s1.shapes.add_textbox(Inches(0.8), Inches(4.8), Inches(3.3), Inches(0.6))
    tf_wia = tb_wia.text_frame
    p_wia_t = tf_wia.paragraphs[0]
    p_wia_t.text = "Who is affected?"
    p_wia_t.font.size = Pt(16)
    p_wia_t.font.bold = True
    p_wia_t.font.color.rgb = COLOR_INK
    p_wia_s = tf_wia.add_paragraph()
    p_wia_s.text = "Security operations teams & air-gapped enclaves."
    p_wia_s.font.size = Pt(11)
    p_wia_s.font.color.rgb = COLOR_GREY_BODY

    aff_data = [
        ("SOC Analysts", "Tier 1 & 2 triaging fatigue"),
        ("SecOps Teams", "Multi-source log correlation"),
        ("Air-Gapped Units", "Zero external network access")
    ]
    for idx, (title, desc) in enumerate(aff_data):
        y_pos = 5.5 + (idx * 0.5)
        add_card(s1, Inches(0.8), Inches(y_pos), Inches(3.2), Inches(0.45), fill_color=COLOR_SURFACE)
        tb_a = s1.shapes.add_textbox(Inches(0.9), Inches(y_pos + 0.05), Inches(3.0), Inches(0.35))
        p_a = tb_a.text_frame.paragraphs[0]
        run_at = p_a.add_run()
        run_at.text = title + " — "
        run_at.font.bold = True
        run_at.font.size = Pt(9.5)
        run_at.font.color.rgb = COLOR_INK
        run_ad = p_a.add_run()
        run_ad.text = desc
        run_ad.font.size = Pt(9)
        run_ad.font.color.rgb = COLOR_GREY_BODY

    # -------------------------------------------------------------------------
    # SLIDE 2: PROPOSED SOLUTION (Matches TARS Page 3 Pipeline Treatment)
    # -------------------------------------------------------------------------
    s2 = add_blank_slide()

    add_header(
        s2,
        "THE SOLUTION",
        "FROM RAW TELEMETRY TO AN EXPLAINABLE INCIDENT.",
        "FULLY LOCAL, ON-DEVICE.",
        "An air-gapped triage assistant executing deterministic detection, temporal graph correlation, deterministic severity scoring, and local SLM reporting entirely in CPU memory."
    )

    pipe_steps = [
        ("01", "INGEST", "Schema Normalization", "Auth & endpoint logs parsed to Pydantic schema with RFC-3339 timestamps (< 2ms)."),
        ("02", "DETECT", "Deterministic Rules", "4 independent rules: login bursts, unusual hours, priv escalation, and tampering."),
        ("03", "CORRELATE", "Union-Find Graph", "Disjoint-Set clustering links disparate events across user, host, IP within 30m."),
        ("04", "PRIORITIZE", "Synergy Severity", "Deterministic 0–100 scoring engine with compound attack-chain synergy bonuses."),
        ("05", "EXPLAIN", "Local SLM Dossier", "SmolLM2-135M synthesizes dossiers with strict evidence grounding and PDF/MD/JSON exports.")
    ]

    card_w = Inches(2.15)
    card_gap = Inches(0.24)
    start_x = Inches(0.8)

    for idx, (num, tag, title, body) in enumerate(pipe_steps):
        x = start_x + idx * (card_w + card_gap)
        add_card(s2, x, Inches(2.2), card_w, Inches(2.45))

        tb_step = s2.shapes.add_textbox(x + Inches(0.12), Inches(2.3), card_w - Inches(0.24), Inches(2.25))
        tf_step = tb_step.text_frame
        tf_step.word_wrap = True

        p_num = tf_step.paragraphs[0]
        p_num.text = num
        p_num.font.size = Pt(14)
        p_num.font.bold = True
        p_num.font.color.rgb = COLOR_GREY_LIGHT

        p_tag = tf_step.add_paragraph()
        p_tag.text = tag
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_INK

        p_title = tf_step.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(10)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_GREY_HEADING

        p_desc = tf_step.add_paragraph()
        p_desc.text = body
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = COLOR_GREY_BODY

        if idx < 4:
            arrow_x = x + card_w + Inches(0.04)
            tb_arr = s2.shapes.add_textbox(arrow_x, Inches(3.2), Inches(0.2), Inches(0.4))
            p_arr = tb_arr.text_frame.paragraphs[0]
            p_arr.text = "→"
            p_arr.font.size = Pt(16)
            p_arr.font.bold = True
            p_arr.font.color.rgb = COLOR_GREY_LIGHT

    tb_kch = s2.shapes.add_textbox(Inches(0.8), Inches(4.85), Inches(11.7), Inches(0.3))
    p_kch = tb_kch.text_frame.paragraphs[0]
    p_kch.text = "KEY CAPABILITIES"
    p_kch.font.size = Pt(10)
    p_kch.font.bold = True
    p_kch.font.color.rgb = COLOR_GREY_LIGHT

    caps_data = [
        ("Local SLM Intelligence", "Genuine Small Language Model (SmolLM2-135M) running entirely offline in CPU memory. Zero cloud LLM dependency, zero telemetry egress, zero external latency."),
        ("Evidence-First Analysis", "Strict programmatic validation checks every cited event ID against real ingested logs. Ungrounded claims or hallucinated events are automatically stripped and flagged."),
        ("Human-in-the-Loop Governance", "Deterministic detection and severity scores ensure mathematical auditability. SLM provides advisory triage checklists; human analysts retain sole authority for remediation.")
    ]

    cap_w = Inches(3.75)
    cap_gap = Inches(0.22)

    for idx, (title, desc) in enumerate(caps_data):
        x = start_x + idx * (cap_w + cap_gap)
        add_card(s2, x, Inches(5.2), cap_w, Inches(1.85))

        tb_ct = s2.shapes.add_textbox(x + Inches(0.2), Inches(5.35), cap_w - Inches(0.4), Inches(1.6))
        tf_ct = tb_ct.text_frame
        tf_ct.word_wrap = True

        p_ct = tf_ct.paragraphs[0]
        p_ct.text = title
        p_ct.font.size = Pt(12)
        p_ct.font.bold = True
        p_ct.font.color.rgb = COLOR_INK
        p_ct.space_after = Pt(3)

        p_cd = tf_ct.add_paragraph()
        p_cd.text = desc
        p_cd.font.size = Pt(9.5)
        p_cd.font.color.rgb = COLOR_GREY_BODY

    # -------------------------------------------------------------------------
    # SLIDE 3: TECHNOLOGY STACK (Matches TARS Page 5 Feasibility Layout)
    # -------------------------------------------------------------------------
    s3 = add_blank_slide()

    add_header(
        s3,
        "FEASIBILITY & EXECUTION",
        "BUILT WITH PRACTICAL TOOLS.",
        "DESIGNED FOR OFFLINE OPERATION.",
        "Engineered with verified lightweight technologies executing smoothly on consumer laptops with zero external dependencies."
    )

    col_w = Inches(3.75)
    col_gap = Inches(0.22)

    cols_data = [
        ("01", "The Application Stack", [
            ("React 19 + TypeScript + Vite", "High-performance SPA with client-side state management, type safety, and sub-second hot reload."),
            ("Tailwind CSS + Neumorphism", "Tactile Warm Cream (#F3EEE3) and Ink Black (#111111) design system with custom dual shadows."),
            ("Recharts & Lucide React", "SVG severity charts and standard cybersecurity iconography bundled offline with zero CDN dependencies."),
            ("Python 3.14 + FastAPI + Uvicorn", "Asynchronous, typed REST API endpoints with Pydantic request/response validation."),
            ("Single-Port Judging Launcher", "Unified launcher serving REST API and static React bundle on http://127.0.0.1:8000.")
        ]),
        ("02", "The Security Intelligence", [
            ("Pydantic Normalization", "Strict schema enforcement mapping disparate log headers to uniform NormalizedEvent schema."),
            ("Deterministic Rule Engine", "Four Python detectors checking login bursts, unusual hours, privilege changes, and tampering."),
            ("Union-Find Graph Clustering", "Disjoint-Set algorithm clustering events across users, endpoints, and IPs in linear time O(α(N))."),
            ("Deterministic Severity Scorer", "0–100 transparent scoring incorporating multi-stage synergy bonuses for compound attacks."),
            ("Local SmolLM2-135M-Instruct", "Genuine Hugging Face TB Small Language Model running locally via PyTorch CPU weights (270 MB).")
        ]),
        ("03", "Data & Delivery", [
            ("Synthetic Benchmark Scenarios", "Scenarios A through E with ground-truth labels for rigorous empirical accuracy validation."),
            ("ReportLab PDF Exporter", "Generates professional executive SOC triage PDFs with event timelines and advisory steps."),
            ("Multi-Format Incident Dossiers", "One-click export to Markdown briefing documents and structured JSON datasets."),
            ("Prompt Defense & Sanitizer", "Log content wrapped in strict delimiters with prompt injection stripping before inference."),
            ("Programmatic Evidence Guard", "Regex citation validator cross-checks all SLM-generated event references against raw telemetry.")
        ])
    ]

    for c_idx, (col_num, col_title, items) in enumerate(cols_data):
        cx = start_x + c_idx * (col_w + col_gap)
        add_card(s3, cx, Inches(2.2), col_w, Inches(4.85))

        tb_col = s3.shapes.add_textbox(cx + Inches(0.18), Inches(2.35), col_w - Inches(0.36), Inches(4.55))
        tf_col = tb_col.text_frame
        tf_col.word_wrap = True

        p_cnum = tf_col.paragraphs[0]
        p_cnum.text = col_num
        p_cnum.font.size = Pt(13)
        p_cnum.font.bold = True
        p_cnum.font.color.rgb = COLOR_GREY_LIGHT

        p_ctitle = tf_col.add_paragraph()
        p_ctitle.text = col_title
        p_ctitle.font.size = Pt(14)
        p_ctitle.font.bold = True
        p_ctitle.font.color.rgb = COLOR_INK
        p_ctitle.space_after = Pt(10)

        for item_title, item_desc in items:
            p_it = tf_col.add_paragraph()
            p_it.space_before = Pt(5)
            r_it = p_it.add_run()
            r_it.text = "• " + item_title + ": "
            r_it.font.bold = True
            r_it.font.size = Pt(9.5)
            r_it.font.color.rgb = COLOR_INK
            r_id = p_it.add_run()
            r_id.text = item_desc
            r_id.font.size = Pt(9)
            r_id.font.color.rgb = COLOR_GREY_BODY

    # -------------------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE (Official PS02 Required Diagram)
    # -------------------------------------------------------------------------
    s4 = add_blank_slide()

    add_header(
        s4,
        "SYSTEM ARCHITECTURE",
        "ONE PIPELINE. DETERMINISTIC SECURITY.",
        "LOCAL AI EXPLANATION.",
        "End-to-end dataflow from raw authentication and endpoint logs to deterministic severity and hallucination-guarded SLM reporting."
    )

    add_card(s4, Inches(0.8), Inches(2.2), Inches(2.4), Inches(4.85))
    tb_in = s4.shapes.add_textbox(Inches(0.95), Inches(2.35), Inches(2.1), Inches(4.5))
    tf_in = tb_in.text_frame
    tf_in.word_wrap = True
    p_in_t = tf_in.paragraphs[0]
    p_in_t.text = "INPUT TELEMETRY"
    p_in_t.font.size = Pt(11)
    p_in_t.font.bold = True
    p_in_t.font.color.rgb = COLOR_GREY_LIGHT
    p_in_t.space_after = Pt(8)

    in_blocks = [
        ("Authentication Logs", "CSV & JSON streams\n• Timestamp & User\n• Source IP & Action\n• Status (Success/Fail)"),
        ("Endpoint Logs", "CSV & JSON streams\n• Device / Hostname\n• Target User & Role\n• Tampering Actions\n• Approval References"),
        ("Air-Gap Assertion", "Zero Cloud Sockets\n• Strict offline operation\n• Local file system paths\n• No API keys required")
    ]
    for b_title, b_desc in in_blocks:
        p_bt = tf_in.add_paragraph()
        p_bt.space_before = Pt(8)
        p_bt.text = "📄 " + b_title
        p_bt.font.size = Pt(10.5)
        p_bt.font.bold = True
        p_bt.font.color.rgb = COLOR_INK
        p_bd = tf_in.add_paragraph()
        p_bd.text = b_desc
        p_bd.font.size = Pt(9)
        p_bd.font.color.rgb = COLOR_GREY_BODY

    flow_steps = [
        ("1. Ingestion & Normalization", "Pydantic V2 model mapping aliases to NormalizedEvent schema. Enforces ISO-8601 UTC timestamps and generates SHA-256 event IDs while preserving raw records."),
        ("2. Deterministic Detection Engine", "4 independent rules evaluated in linear time:\n• Failed Login Bursts (≥5 in 300s)\n• Unusual / Weekend Hours (Asia/Kolkata)\n• Unapproved Privilege Escalation\n• Security Control & EDR Tampering"),
        ("3. Temporal Entity Correlation", "Union-Find disjoint-set graph clustering linking related events across user identity, device hostname, and source IP within a 30-minute sliding window."),
        ("4. Deterministic Severity Engine", "0–100 transparent scoring based on base rule weights, off-hours multipliers, and compound multi-stage attack synergy bonuses (Critical, High, Medium, Low)."),
        ("5. Air-Gapped SLM Inference & Guardrails", "Prompt Sanitizer wraps events in containment tags → SmolLM2-135M generates briefing on CPU → Programmatic Validator verifies all cited Event IDs before reporting.")
    ]

    card_y = Inches(2.2)
    step_h = Inches(0.9)
    step_gap = Inches(0.08)

    for idx, (stitle, sdesc) in enumerate(flow_steps):
        sy = card_y + idx * (step_h + step_gap)
        add_card(s4, Inches(3.4), sy, Inches(5.1), step_h)
        tb_s = s4.shapes.add_textbox(Inches(3.55), sy + Inches(0.06), Inches(4.8), step_h - Inches(0.12))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        p_st = tf_s.paragraphs[0]
        p_st.text = stitle
        p_st.font.size = Pt(10.5)
        p_st.font.bold = True
        p_st.font.color.rgb = COLOR_INK
        p_sd = tf_s.add_paragraph()
        p_sd.text = sdesc
        p_sd.font.size = Pt(8.5)
        p_sd.font.color.rgb = COLOR_GREY_BODY

    add_card(s4, Inches(8.7), Inches(2.2), Inches(3.85), Inches(4.85))
    tb_out = s4.shapes.add_textbox(Inches(8.85), Inches(2.35), Inches(3.55), Inches(1.3))
    tf_out = tb_out.text_frame
    tf_out.word_wrap = True
    p_ot = tf_out.paragraphs[0]
    p_ot.text = "DELIVERABLES & REPORTING"
    p_ot.font.size = Pt(11)
    p_ot.font.bold = True
    p_ot.font.color.rgb = COLOR_GREY_LIGHT

    p_od = tf_out.add_paragraph()
    p_od.space_before = Pt(4)
    p_od.text = "• React 19 SOC Workstation (Port 8000)\n• ReportLab PDF Executive Reports\n• Markdown Dossiers & Audit JSON\n• Human Analyst Authorization Gate"
    p_od.font.size = Pt(9.5)
    p_od.font.color.rgb = COLOR_GREY_BODY

    screen_path = SCREENSHOTS_DIR / "01_soc_overview.png"
    if screen_path.exists():
        s4.shapes.add_picture(str(screen_path), Inches(8.85), Inches(3.7), width=Inches(3.55))

    tb_cap = s4.shapes.add_textbox(Inches(8.85), Inches(6.5), Inches(3.55), Inches(0.4))
    p_cap = tb_cap.text_frame.paragraphs[0]
    p_cap.text = "React 19 Console: Warm Cream × Ink Black Neumorphism"
    p_cap.font.size = Pt(8.5)
    p_cap.font.color.rgb = COLOR_GREY_LIGHT
    p_cap.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------------------
    # SLIDE 5: IMPACT (Matches TARS Page 6 Large Metric Layout)
    # -------------------------------------------------------------------------
    s5 = add_blank_slide()

    add_header(
        s5,
        "IMPACT",
        "BETTER INCIDENT CONTEXT. LESS DEPENDENCE ON THE CLOUD.",
        "MORE TRACEABLE INVESTIGATION.",
        "Transforming fragmented event noise into actionable, auditable, and locally reasoned incident intelligence."
    )

    start_x = Inches(0.8)
    card_m_w = Inches(3.75)
    card_m_gap = Inches(0.22)
    pan_w = Inches(5.72)
    pan_gap = Inches(0.26)

    outcomes = [
        ("🔒", "100% OFFLINE", "Air-Gapped Operation", "Zero cloud telemetry egress. Enables compliance with defense, banking, and critical infrastructure mandates without external LLM API costs."),
        ("⚡", "19.8 MS", "Pipeline Latency", "Near-instantaneous ingestion, detection, graph correlation, and deterministic scoring across all incoming security event streams."),
        ("🛡️", "EVIDENCE VALIDATED", "Evidence References Validated", "Strict programmatic regex validation ensures every cited Event ID exists in real telemetry. Eliminates ungrounded forensic claims.")
    ]

    for idx, (icon, metric, title, body) in enumerate(outcomes):
        mx = start_x + idx * (card_m_w + card_m_gap)
        add_card(s5, mx, Inches(2.2), card_m_w, Inches(2.15))

        tb_m = s5.shapes.add_textbox(mx + Inches(0.2), Inches(2.35), card_m_w - Inches(0.4), Inches(1.85))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True

        p_m_val = tf_m.paragraphs[0]
        p_m_val.text = f"{icon}  {metric}"
        p_m_val.font.size = Pt(22)
        p_m_val.font.bold = True
        p_m_val.font.color.rgb = COLOR_INK

        p_m_title = tf_m.add_paragraph()
        p_m_title.text = title
        p_m_title.font.size = Pt(11)
        p_m_title.font.bold = True
        p_m_title.font.color.rgb = COLOR_GREY_HEADING
        p_m_title.space_after = Pt(4)

        p_m_desc = tf_m.add_paragraph()
        p_m_desc.text = body
        p_m_desc.font.size = Pt(9.5)
        p_m_desc.font.color.rgb = COLOR_GREY_BODY

    panels_data = [
        ("SOC Operational Value", [
            ("Alert De-Noising & Prioritization:", "Combines compound anomalies (e.g. login bursts + privilege change) into single incidents, preventing alert fatigue."),
            ("Accelerated Investigation Time:", "Replaces hours of manual cross-log SQL querying with instant graph correlation and timeline synthesis."),
            ("Auditable Forensic Reporting:", "Auto-generates standardized PDF, Markdown, and JSON briefing packages for leadership and shift handovers."),
            ("Human-in-the-Loop Governance:", "Advisory action recommendations keep human analysts fully accountable; no autonomous disruptive actions.")
        ]),
        ("Technical & Engineering Value", [
            ("Deterministic Security Baseline:", "Detection and severity scoring are mathematically explainable and auditable, never dependent on stochastic model drift."),
            ("Low Resource Footprint:", "SmolLM2-135M runs in ~500 MB RAM on commodity laptop CPUs without requiring expensive cloud GPU infrastructure."),
            ("Resilient Air-Gapped Readiness:", "Functions seamlessly during network blackouts, tactical deployments, or physically isolated enclaves."),
            ("Strict Programmatic Verification:", "SLMOutputValidator prevents AI confabulation by rejecting ungrounded event identifiers.")
        ])
    ]

    for p_idx, (ptitle, pitems) in enumerate(panels_data):
        px = start_x + p_idx * (pan_w + pan_gap)
        add_card(s5, px, Inches(4.55), pan_w, Inches(2.5))

        tb_pan = s5.shapes.add_textbox(px + Inches(0.25), Inches(4.7), pan_w - Inches(0.5), Inches(2.2))
        tf_pan = tb_pan.text_frame
        tf_pan.word_wrap = True

        p_pt = tf_pan.paragraphs[0]
        p_pt.text = ptitle
        p_pt.font.size = Pt(14)
        p_pt.font.bold = True
        p_pt.font.color.rgb = COLOR_INK
        p_pt.space_after = Pt(6)

        for it_title, it_desc in pitems:
            p_pi = tf_pan.add_paragraph()
            p_pi.space_before = Pt(3)
            r_pit = p_pi.add_run()
            r_pit.text = "• " + it_title + " "
            r_pit.font.bold = True
            r_pit.font.size = Pt(9.5)
            r_pit.font.color.rgb = COLOR_INK
            r_pid = p_pi.add_run()
            r_pid.text = it_desc
            r_pid.font.size = Pt(9)
            r_pid.font.color.rgb = COLOR_GREY_BODY

    # -------------------------------------------------------------------------
    # SLIDE 6: RESULTS, BENCHMARKS & FUTURE SCOPE (Matches TARS Page 5 & 6)
    # -------------------------------------------------------------------------
    s6 = add_blank_slide()

    add_header(
        s6,
        "VALIDATION & NEXT STEPS",
        "BUILT. TESTED. MEASURED.",
        "WITH CLEAR EVALUATION LIMITS.",
        "Empirically validated against synthetic ground-truth scenarios with 22 automated integration tests passing."
    )

    benchmarks = [
        ("100.0%", "Precision", "TP=5, FP=0 • Zero false positive alerts on baseline operations"),
        ("100.0%", "Recall", "TP=5, FN=0 • All ground-truth attack scenarios detected"),
        ("1.000", "F1-Score", "Optimal balance across all attack vectors and log sources"),
        ("0.00%", "False Positive Rate", "Legitimate overtime activity recognized and properly dampened")
    ]

    start_x = Inches(0.8)
    card_b_w = Inches(2.8)
    card_b_gap = Inches(0.18)

    for idx, (bval, btitle, bdesc) in enumerate(benchmarks):
        bx = start_x + idx * (card_b_w + card_b_gap)
        add_card(s6, bx, Inches(2.2), card_b_w, Inches(1.3))

        tb_b = s6.shapes.add_textbox(bx + Inches(0.15), Inches(2.28), card_b_w - Inches(0.3), Inches(1.15))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        p_bv = tf_b.paragraphs[0]
        p_bv.text = bval
        p_bv.font.size = Pt(20)
        p_bv.font.bold = True
        p_bv.font.color.rgb = COLOR_INK

        p_bt = tf_b.add_paragraph()
        p_bt.text = btitle
        p_bt.font.size = Pt(10)
        p_bt.font.bold = True
        p_bt.font.color.rgb = COLOR_GREY_HEADING

        p_bd = tf_b.add_paragraph()
        p_bd.text = bdesc
        p_bd.font.size = Pt(8.5)
        p_bd.font.color.rgb = COLOR_GREY_BODY

    add_card(s6, Inches(0.8), Inches(3.62), Inches(11.7), Inches(0.36), fill_color=COLOR_CONTAINER, border_color=None)
    tb_ban = s6.shapes.add_textbox(Inches(0.9), Inches(3.66), Inches(11.5), Inches(0.3))
    p_ban = tb_ban.text_frame.paragraphs[0]
    p_ban.text = "OFFICIAL BENCHMARK DISCLOSURE: RESULTS BASED ON SYNTHETIC BENCHMARK DATASET (SCENARIOS A–E). NOT AN ENTERPRISE PRODUCTION BENCHMARK."
    p_ban.font.size = Pt(8.5)
    p_ban.font.bold = True
    p_ban.font.color.rgb = COLOR_GREY_BODY
    p_ban.alignment = PP_ALIGN.CENTER

    scen_w = Inches(2.25)
    scen_gap = Inches(0.11)
    scenarios = [
        ("A", "Brute Force Escalation", "CRITICAL (95/100)", "MATCHED", COLOR_RED),
        ("B", "Out-of-Hours DBA Logon", "MEDIUM (50/100)", "MATCHED", COLOR_AMBER),
        ("C", "EDR Tool Tampering", "HIGH (75/100)", "MATCHED", COLOR_AMBER),
        ("D", "Multi-Stage Killchain", "CRITICAL (100/100)", "MATCHED", COLOR_RED),
        ("E", "Legitimate Overtime", "BENIGN (0 ALERTS)", "MATCHED", COLOR_EMERALD)
    ]

    for idx, (sletter, sname, ssev, smatch, scol) in enumerate(scenarios):
        sx = start_x + idx * (scen_w + scen_gap)
        add_card(s6, sx, Inches(4.1), scen_w, Inches(0.85))

        tb_sc = s6.shapes.add_textbox(sx + Inches(0.1), Inches(4.15), scen_w - Inches(0.2), Inches(0.75))
        tf_sc = tb_sc.text_frame
        tf_sc.word_wrap = True

        p_sct = tf_sc.paragraphs[0]
        p_sct.text = f"Scenario {sletter}: {sname}"
        p_sct.font.size = Pt(9)
        p_sct.font.bold = True
        p_sct.font.color.rgb = COLOR_INK

        p_scs = tf_sc.add_paragraph()
        p_scs.text = f"{ssev} • {smatch} ✓"
        p_scs.font.size = Pt(8.5)
        p_scs.font.bold = True
        p_scs.font.color.rgb = scol

    low_w = Inches(5.75)
    add_card(s6, Inches(0.8), Inches(5.1), low_w, Inches(1.95))
    tb_fs = s6.shapes.add_textbox(Inches(0.95), Inches(5.2), low_w - Inches(0.3), Inches(1.75))
    tf_fs = tb_fs.text_frame
    tf_fs.word_wrap = True
    p_fst = tf_fs.paragraphs[0]
    p_fst.text = "FUTURE SCOPE & TECHNICAL ROADMAP"
    p_fst.font.size = Pt(11)
    p_fst.font.bold = True
    p_fst.font.color.rgb = COLOR_INK
    p_fst.space_after = Pt(4)

    fs_items = [
        ("Windows Event Log (EVTX) Parser:", "Direct binary ingestion for Security, System, and Sysmon channels."),
        ("Expanded MITRE ATT&CK Mapping:", "Heuristics covering persistence, credential dumping, and data staging."),
        ("INT4 / GGUF Quantization:", "Compressing model weights for sub-500ms CPU inference on edge devices."),
        ("Enterprise Log Volume Evals:", "Testing scalability against high-throughput multi-gigabyte corporate streams.")
    ]
    for it_t, it_d in fs_items:
        p_fsi = tf_fs.add_paragraph()
        p_fsi.space_before = Pt(2)
        r_ft = p_fsi.add_run()
        r_ft.text = "• " + it_t + " "
        r_ft.font.bold = True
        r_ft.font.size = Pt(9)
        r_ft.font.color.rgb = COLOR_INK
        r_fd = p_fsi.add_run()
        r_fd.text = it_d
        r_fd.font.size = Pt(8.5)
        r_fd.font.color.rgb = COLOR_GREY_BODY

    add_card(s6, Inches(6.76), Inches(5.1), low_w, Inches(1.95))
    tb_ref = s6.shapes.add_textbox(Inches(6.91), Inches(5.2), low_w - Inches(0.3), Inches(1.75))
    tf_ref = tb_ref.text_frame
    tf_ref.word_wrap = True
    p_reft = tf_ref.paragraphs[0]
    p_reft.text = "REFERENCES, ATTRIBUTION & DISCLOSURE"
    p_reft.font.size = Pt(11)
    p_reft.font.bold = True
    p_reft.font.color.rgb = COLOR_INK
    p_reft.space_after = Pt(4)

    ref_items = [
        ("Model Attribution:", "HuggingFaceTB/SmolLM2-135M-Instruct (Apache 2.0 License)."),
        ("Software Stack:", "FastAPI, React 19, Vite, Tailwind CSS, ReportLab, Pydantic, Pytest."),
        ("Test Verification:", "22 / 22 automated integration tests verified passing in 4.75s."),
        ("AI Assistance Disclosure:", "Assisted by AI coding agents under participant direction. All code, architecture, and verification by Mir Farzin Hussain (USN: 1MS24CI073).")
    ]
    for rt_t, rt_d in ref_items:
        p_refi = tf_ref.add_paragraph()
        p_refi.space_before = Pt(2)
        r_rt = p_refi.add_run()
        r_rt.text = "• " + rt_t + " "
        r_rt.font.bold = True
        r_rt.font.size = Pt(9)
        r_rt.font.color.rgb = COLOR_INK
        r_rd = p_refi.add_run()
        r_rd.text = rt_d
        r_rd.font.size = Pt(8.5)
        r_rd.font.color.rgb = COLOR_GREY_BODY

    prs.save(str(PPTX_PATH))
    print(f"[✓] Generated PPTX presentation: {PPTX_PATH}")


def build_pdf_deck():
    """Generates the high-resolution 7-slide PDF matching the PPTX design."""
    w, h = 960, 540
    c = canvas.Canvas(str(PDF_PATH), pagesize=(w, h))

    def draw_rounded_card(x, y, width, height, radius=6, fill_color=HEX_SURFACE, stroke_color=HEX_BORDER):
        c.saveState()
        if fill_color:
            c.setFillColor(fill_color)
        if stroke_color:
            c.setStrokeColor(stroke_color)
            c.setLineWidth(1)
        else:
            c.setStrokeColor(fill_color)
        c.roundRect(x, y, width, height, radius, fill=1 if fill_color else 0, stroke=1 if stroke_color else 0)
        c.restoreState()

    def draw_header_pdf(section_tag, title_black, title_grey_line2=None, subtitle=None):
        c.saveState()
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HEX_GREY_LIGHT)
        c.drawString(55, 508, section_tag.upper())

        c.setFont("Helvetica-Bold", 17)
        c.setFillColor(HEX_INK)
        c.drawString(55, 486, title_black)

        y_sub = 468
        if title_grey_line2:
            c.setFont("Helvetica-Bold", 17)
            c.setFillColor(HEX_GREY_HEADING)
            c.drawString(55, 466, title_grey_line2)
            y_sub = 448

        if subtitle:
            c.setFont("Helvetica", 9)
            c.setFillColor(HEX_GREY_BODY)
            c.drawString(55, y_sub, subtitle)

        c.restoreState()

    # -------------------------------------------------------------------------
    # SLIDE 0: TITLE SLIDE
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setFillColor(HEX_DARK_PANEL)
    c.rect(600, 0, 360, h, fill=1, stroke=0)

    cover_img_path = ASSETS_DIR / "cover_security_node.png"
    if cover_img_path.exists():
        c.drawImage(str(cover_img_path), 625, 60, width=310, height=420, preserveAspectRatio=True)

    draw_rounded_card(625, 25, 310, 30, radius=4, fill_color=HexColor('#19191C'), stroke_color=HexColor('#323237'))
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_WHITE)
    c.drawCentredString(780, 36, "100% OFFLINE • AIR-GAPPED SOC ASSISTANT")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(65, 460, "TINYVERSE HACKATHON • PHASE 2 FINALS")

    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(HEX_INK)
    c.drawString(65, 415, "OFFLINE SECURITY")
    c.drawString(65, 375, "INCIDENT TRIAGE")
    c.setFillColor(HEX_GREY_HEADING)
    c.drawString(65, 335, "ASSISTANT")

    c.setFont("Helvetica", 11)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(65, 295, "From raw security logs to evidence-backed incident investigations — entirely on-device.")

    c.setStrokeColor(HEX_BORDER)
    c.setLineWidth(1)
    c.line(65, 260, 560, 260)

    draw_rounded_card(65, 140, 240, 95)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(80, 210, "PARTICIPANT NAME:")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HEX_INK)
    c.drawString(80, 188, "Mir Farzin Hussain")
    c.setFont("Helvetica", 9)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(80, 168, "USN: 1MS24CI073")

    draw_rounded_card(320, 140, 240, 95)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(335, 210, "PROBLEM STATEMENT & DEPT:")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HEX_INK)
    c.drawString(335, 188, "Problem Statement: PS02")
    c.setFont("Helvetica", 9)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(335, 168, "CSE (AI & ML) • Phase 2")

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 1: THE PROBLEM
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_rounded_card(660, 25, 250, 485, radius=8, fill_color=HEX_DARK_PANEL, stroke_color=None)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HEX_WHITE)
    c.drawString(680, 480, "Why it matters?")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(680, 464, "When context is fragmented, triage breaks down.")

    wim_cards = [
        ("01  Alert overload", "High event volumes overwhelm analyst capacity; low-frequency attack signals get lost."),
        ("02  Fragmented context", "Attacker steps span auth and endpoint silos without unified identity linkage."),
        ("03  Cloud dependency", "Restricted enclaves and defense sites cannot stream logs to cloud LLM APIs."),
        ("04  Evidence gaps", "Generic chatbots hallucinate; analysts need exact, auditable event citations.")
    ]
    for idx, (ctitle, cdesc) in enumerate(wim_cards):
        cy = 360 - idx * 95
        draw_rounded_card(678, cy, 214, 82, radius=6, fill_color=HEX_WHITE, stroke_color=None)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HEX_INK)
        c.drawString(690, cy + 62, ctitle)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        words = cdesc.split()
        c.drawString(690, cy + 46, " ".join(words[:6]))
        c.drawString(690, cy + 33, " ".join(words[6:12]))
        if len(words) > 12:
            c.drawString(690, cy + 20, " ".join(words[12:]))

    draw_header_pdf(
        "THE PROBLEM & EXISTING SOLUTIONS",
        "SECURITY TEAMS SEE EVERYTHING.",
        "BUT CAN'T INVESTIGATE EVERYTHING.",
        "Security Operations Centers process thousands of authentication and endpoint events. Manual triage is slow, subtle killchains are missed."
    )

    iceberg_path = ASSETS_DIR / "problem_iceberg.png"
    if iceberg_path.exists():
        c.drawImage(str(iceberg_path), 310, 130, width=335, height=290, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(55, 415, "EXISTING WORKFLOW LIMITATIONS")

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_INK)
    c.drawString(55, 390, "• SIEM Rule Fatigue:")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(65, 376, "Static rules trigger thousands of disparate alerts without")
    c.drawString(65, 364, "multi-source correlation.")

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_INK)
    c.drawString(55, 342, "• Manual Investigation:")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(65, 328, "Analysts manually write SQL queries across auth and")
    c.drawString(65, 316, "endpoint telemetry silos.")

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_INK)
    c.drawString(55, 294, "• Cloud AI Unsuitability:")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(65, 280, "Air-gapped sites cannot send proprietary telemetry")
    c.drawString(65, 268, "to external LLM APIs.")

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HEX_INK)
    c.drawString(55, 225, "Who is affected?")
    c.setFont("Helvetica", 8)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(55, 210, "Security operations teams & air-gapped enclaves.")

    aff_p = [
        ("SOC Analysts", "Tier 1 & 2 triaging fatigue"),
        ("SecOps Teams", "Multi-source log correlation"),
        ("Air-Gapped Units", "Zero external network access")
    ]
    for idx, (t, d) in enumerate(aff_p):
        ay = 165 - idx * 38
        draw_rounded_card(55, ay, 240, 32)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HEX_INK)
        c.drawString(65, ay + 12, f"• {t} — ")
        tw = c.stringWidth(f"• {t} — ", "Helvetica-Bold", 8)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        c.drawString(65 + tw, ay + 12, d)

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 2: PROPOSED SOLUTION
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_header_pdf(
        "THE SOLUTION",
        "FROM RAW TELEMETRY TO AN EXPLAINABLE INCIDENT.",
        "FULLY LOCAL, ON-DEVICE.",
        "An air-gapped triage assistant executing deterministic detection, temporal graph correlation, deterministic severity scoring, and local SLM reporting."
    )

    pipe_steps_pdf = [
        ("01", "INGEST", "Schema Normalization", "Auth & endpoint logs parsed to Pydantic schema with RFC-3339 timestamps (< 2ms)."),
        ("02", "DETECT", "Deterministic Rules", "4 independent rules: login bursts, unusual hours, priv escalation, and tampering."),
        ("03", "CORRELATE", "Union-Find Graph", "Disjoint-Set clustering links disparate events across user, host, IP within 30m."),
        ("04", "PRIORITIZE", "Synergy Severity", "Deterministic 0–100 scoring engine with compound attack-chain synergy bonuses."),
        ("05", "EXPLAIN", "Local SLM Dossier", "SmolLM2-135M synthesizes dossiers with strict evidence grounding and PDF/MD/JSON exports.")
    ]

    p_w = 160
    p_gap = 14
    for idx, (num, tag, title, body) in enumerate(pipe_steps_pdf):
        px = 55 + idx * (p_w + p_gap)
        draw_rounded_card(px, 245, p_w, 175)

        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HEX_GREY_LIGHT)
        c.drawString(px + 12, 400, num)

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HEX_INK)
        c.drawString(px + 12, 382, tag)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HEX_GREY_HEADING)
        c.drawString(px + 12, 366, title)

        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        words = body.split()
        c.drawString(px + 12, 340, " ".join(words[:4]))
        c.drawString(px + 12, 326, " ".join(words[4:8]))
        c.drawString(px + 12, 312, " ".join(words[8:12]))
        if len(words) > 12:
            c.drawString(px + 12, 298, " ".join(words[12:]))

        if idx < 4:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(HEX_GREY_LIGHT)
            c.drawString(px + p_w + 3, 325, "→")

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(55, 222, "KEY CAPABILITIES")

    caps_pdf = [
        ("Local SLM Intelligence", "Genuine Small Language Model (SmolLM2-135M) running entirely offline in CPU memory. Zero cloud LLM dependency, zero telemetry egress, zero external latency."),
        ("Evidence-First Analysis", "Strict programmatic validation checks every cited event ID against real ingested logs. Ungrounded claims or hallucinated events are automatically stripped and flagged."),
        ("Human-in-the-Loop Governance", "Deterministic detection and severity scores ensure mathematical auditability. SLM provides advisory triage checklists; human analysts retain sole authority for remediation.")
    ]
    c_w = 274
    c_gap = 16
    for idx, (title, desc) in enumerate(caps_pdf):
        cx = 55 + idx * (c_w + c_gap)
        draw_rounded_card(cx, 35, c_w, 175)

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HEX_INK)
        c.drawString(cx + 14, 187, title)

        c.setFont("Helvetica", 8)
        c.setFillColor(HEX_GREY_BODY)
        words = desc.split()
        c.drawString(cx + 14, 163, " ".join(words[:6]))
        c.drawString(cx + 14, 149, " ".join(words[6:12]))
        c.drawString(cx + 14, 135, " ".join(words[12:18]))
        c.drawString(cx + 14, 121, " ".join(words[18:24]))
        c.drawString(cx + 14, 107, " ".join(words[24:]))

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 3: TECHNOLOGY STACK
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_header_pdf(
        "FEASIBILITY & EXECUTION",
        "BUILT WITH PRACTICAL TOOLS.",
        "DESIGNED FOR OFFLINE OPERATION.",
        "Engineered with verified lightweight technologies executing smoothly on consumer laptops with zero external dependencies."
    )

    t_col_w = 274
    t_col_gap = 16
    stack_cols = [
        ("01", "The Application Stack", [
            ("React 19 + TypeScript + Vite", "Fast SPA with client-side state management & type safety."),
            ("Tailwind CSS + Neumorphism", "Warm Cream (#F3EEE3) and Ink Black (#111111) dual shadows."),
            ("Recharts & Lucide React", "SVG severity charts and standard cybersecurity iconography."),
            ("Python 3.14 + FastAPI + Uvicorn", "Asynchronous, typed REST API endpoints with Pydantic."),
            ("Single-Port Judging Launcher", "Unified launcher serving API & React on port 8000.")
        ]),
        ("02", "The Security Intelligence", [
            ("Pydantic Normalization", "Strict schema enforcement mapping disparate log headers."),
            ("Deterministic Rule Engine", "4 detectors: bursts, hours, escalation, and tampering."),
            ("Union-Find Graph Clustering", "Disjoint-Set clustering across user, host, IP in linear time."),
            ("Deterministic Severity Scorer", "0–100 transparent scoring with compound attack synergy."),
            ("Local SmolLM2-135M-Instruct", "Genuine Hugging Face TB SLM running locally on CPU (270 MB).")
        ]),
        ("03", "Data & Delivery", [
            ("Synthetic Benchmark Scenarios", "Scenarios A–E with ground truth for empirical validation."),
            ("ReportLab PDF Exporter", "Generates professional executive SOC triage PDFs with timelines."),
            ("Multi-Format Incident Dossiers", "One-click export to Markdown briefs and structured JSON."),
            ("Prompt Defense & Sanitizer", "Log content wrapped in delimiters with injection stripping."),
            ("Programmatic Evidence Guard", "Regex citation validator verifies SLM event references.")
        ])
    ]

    for c_idx, (col_num, col_title, items) in enumerate(stack_cols):
        cx = 55 + c_idx * (t_col_w + t_col_gap)
        draw_rounded_card(cx, 30, t_col_w, 395)

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HEX_GREY_LIGHT)
        c.drawString(cx + 14, 407, col_num)

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HEX_INK)
        c.drawString(cx + 14, 389, col_title)

        y = 363
        for it_title, it_desc in items:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(HEX_INK)
            c.drawString(cx + 14, y, f"• {it_title}:")
            c.setFont("Helvetica", 7.5)
            c.setFillColor(HEX_GREY_BODY)
            words = it_desc.split()
            c.drawString(cx + 22, y - 12, " ".join(words[:6]))
            if len(words) > 6:
                c.drawString(cx + 22, y - 23, " ".join(words[6:]))
                y -= 38
            else:
                y -= 28

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_header_pdf(
        "SYSTEM ARCHITECTURE",
        "ONE PIPELINE. DETERMINISTIC SECURITY.",
        "LOCAL AI EXPLANATION.",
        "End-to-end dataflow from raw authentication and endpoint logs to deterministic severity and hallucination-guarded SLM reporting."
    )

    draw_rounded_card(55, 30, 175, 395)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(68, 407, "INPUT TELEMETRY")

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HEX_INK)
    c.drawString(68, 380, "📄 Authentication Logs")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(76, 365, "CSV & JSON formats")
    c.drawString(76, 353, "• Timestamp & User")
    c.drawString(76, 341, "• Source IP & Action")
    c.drawString(76, 329, "• Status (Success/Fail)")

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HEX_INK)
    c.drawString(68, 300, "📄 Endpoint Logs")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(76, 285, "CSV & JSON formats")
    c.drawString(76, 273, "• Device / Hostname")
    c.drawString(76, 261, "• Target User & Role")
    c.drawString(76, 249, "• Tampering Actions")

    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HEX_INK)
    c.drawString(68, 220, "🔒 Air-Gap Assertion")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(76, 205, "Zero Cloud Sockets")
    c.drawString(76, 193, "• Strict offline operation")
    c.drawString(76, 181, "• Local file system paths")

    core_steps_pdf = [
        ("1. Ingestion & Normalization", "Pydantic V2 model mapping aliases to NormalizedEvent schema. Enforces ISO-8601 UTC timestamps and SHA-256 event IDs."),
        ("2. Deterministic Detection Engine", "4 independent rules evaluated in linear time: Failed Login Bursts, Unusual Hours, Privilege Escalation, and Control Tampering."),
        ("3. Temporal Entity Correlation", "Union-Find disjoint-set graph clustering linking related events across user identity, device hostname, and IP within 30 minutes."),
        ("4. Deterministic Severity Engine", "0–100 transparent scoring based on base rule weights, off-hours multipliers, and compound multi-stage attack synergy bonuses."),
        ("5. Air-Gapped SLM Inference & Guardrails", "Prompt Sanitizer wraps events in containment tags → SmolLM2-135M on CPU → Programmatic Validator verifies cited Event IDs.")
    ]
    for idx, (stitle, sdesc) in enumerate(core_steps_pdf):
        sy = 355 - idx * 72
        draw_rounded_card(245, sy, 380, 64)
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(HEX_INK)
        c.drawString(258, sy + 46, stitle)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        words = sdesc.split()
        c.drawString(258, sy + 30, " ".join(words[:9]))
        c.drawString(258, sy + 18, " ".join(words[9:]))

    draw_rounded_card(640, 30, 270, 395)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawString(654, 407, "DELIVERABLES & REPORTING")

    c.setFont("Helvetica", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawString(654, 389, "• React 19 SOC Workstation (Port 8000)")
    c.drawString(654, 377, "• ReportLab PDF Executive Reports")
    c.drawString(654, 365, "• Markdown Dossiers & Audit JSON")
    c.drawString(654, 353, "• Human Analyst Authorization Gate")

    screen_path = SCREENSHOTS_DIR / "01_soc_overview.png"
    if screen_path.exists():
        c.drawImage(str(screen_path), 652, 95, width=246, height=195, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(HEX_GREY_LIGHT)
    c.drawCentredString(775, 75, "React 19 Console: Warm Cream × Ink Black")

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 5: IMPACT
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_header_pdf(
        "IMPACT",
        "BETTER INCIDENT CONTEXT. LESS DEPENDENCE ON THE CLOUD.",
        "MORE TRACEABLE INVESTIGATION.",
        "Transforming fragmented event noise into actionable, auditable, and locally reasoned incident intelligence."
    )

    outcomes_pdf = [
        ("100% OFFLINE", "Air-Gapped Operation", "Zero cloud telemetry egress. Enables compliance with defense, banking, and critical infrastructure mandates without external LLM API costs."),
        ("19.8 MS", "Pipeline Latency", "Near-instantaneous ingestion, detection, graph correlation, and deterministic scoring across all incoming security event streams."),
        ("EVIDENCE VALIDATED", "Evidence References Validated", "Strict programmatic regex validation ensures every cited Event ID exists in real telemetry. Eliminates ungrounded forensic claims.")
    ]
    for idx, (metric, title, body) in enumerate(outcomes_pdf):
        mx = 55 + idx * (t_col_w + t_col_gap)
        draw_rounded_card(mx, 255, t_col_w, 170)

        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(HEX_INK)
        c.drawString(mx + 16, 395, metric)

        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HEX_GREY_HEADING)
        c.drawString(mx + 16, 377, title)

        c.setFont("Helvetica", 8)
        c.setFillColor(HEX_GREY_BODY)
        words = body.split()
        c.drawString(mx + 16, 350, " ".join(words[:6]))
        c.drawString(mx + 16, 336, " ".join(words[6:12]))
        c.drawString(mx + 16, 322, " ".join(words[12:18]))
        if len(words) > 18:
            c.drawString(mx + 16, 308, " ".join(words[18:]))

    pan_w_pdf = 419
    pan_gap_pdf = 16
    panels_pdf = [
        ("SOC Operational Value", [
            ("Alert De-Noising & Prioritization:", "Combines compound anomalies into single unified cases."),
            ("Accelerated Investigation Time:", "Replaces hours of cross-log SQL queries with instant correlation."),
            ("Auditable Forensic Reporting:", "Auto-generates executive PDF, Markdown, and JSON briefings."),
            ("Human-in-the-Loop Governance:", "Advisory recommendations keep human analysts fully accountable.")
        ]),
        ("Technical & Engineering Value", [
            ("Deterministic Security Baseline:", "Detection and severity scoring are mathematically explainable."),
            ("Low Resource Footprint:", "SmolLM2-135M runs in ~500 MB RAM on commodity laptop CPUs."),
            ("Resilient Air-Gapped Readiness:", "Functions seamlessly during network blackouts or isolated sites."),
            ("Strict Programmatic Verification:", "SLMOutputValidator prevents AI confabulation by rejecting bad IDs.")
        ])
    ]
    for p_idx, (ptitle, pitems) in enumerate(panels_pdf):
        px = 55 + p_idx * (pan_w_pdf + pan_gap_pdf)
        draw_rounded_card(px, 30, pan_w_pdf, 210)

        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HEX_INK)
        c.drawString(px + 16, 218, ptitle)

        y = 190
        for it_title, it_desc in pitems:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(HEX_INK)
            c.drawString(px + 16, y, f"• {it_title} ")
            tw = c.stringWidth(f"• {it_title} ", "Helvetica-Bold", 8)
            c.setFont("Helvetica", 7.5)
            c.setFillColor(HEX_GREY_BODY)
            c.drawString(px + 16 + tw, y, it_desc)
            y -= 26

    c.showPage()

    # -------------------------------------------------------------------------
    # SLIDE 6: RESULTS, BENCHMARKS & FUTURE SCOPE
    # -------------------------------------------------------------------------
    c.setFillColor(HEX_WHITE)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    draw_header_pdf(
        "VALIDATION & NEXT STEPS",
        "BUILT. TESTED. MEASURED.",
        "WITH CLEAR EVALUATION LIMITS.",
        "Empirically validated against synthetic ground-truth scenarios with 22 automated integration tests passing."
    )

    bench_w = 200
    bench_gap = 18
    benchmarks_pdf = [
        ("100.0%", "Precision", "TP=5, FP=0 • Zero false positive alerts on baseline operations"),
        ("100.0%", "Recall", "TP=5, FN=0 • All ground-truth attack scenarios detected"),
        ("1.000", "F1-Score", "Optimal balance across all attack vectors and log sources"),
        ("0.00%", "False Positive Rate", "Legitimate overtime activity recognized and dampened")
    ]
    for idx, (bval, btitle, bdesc) in enumerate(benchmarks_pdf):
        bx = 55 + idx * (bench_w + bench_gap)
        draw_rounded_card(bx, 340, bench_w, 95)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(HEX_INK)
        c.drawString(bx + 14, 412, bval)

        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(HEX_GREY_HEADING)
        c.drawString(bx + 14, 396, btitle)

        c.setFont("Helvetica", 7)
        c.setFillColor(HEX_GREY_BODY)
        words = bdesc.split()
        c.drawString(bx + 14, 375, " ".join(words[:5]))
        c.drawString(bx + 14, 363, " ".join(words[5:]))

    draw_rounded_card(55, 305, 855, 24, radius=4, fill_color=HEX_CONTAINER, stroke_color=None)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(HEX_GREY_BODY)
    c.drawCentredString(480, 313, "OFFICIAL BENCHMARK DISCLOSURE: RESULTS BASED ON SYNTHETIC BENCHMARK DATASET (SCENARIOS A–E). NOT AN ENTERPRISE PRODUCTION BENCHMARK.")

    scen_w_pdf = 162
    scen_gap_pdf = 11
    scenarios_pdf = [
        ("A", "Brute Force Escalation", "CRITICAL (95/100)", HEX_RED),
        ("B", "Out-of-Hours DBA Logon", "MEDIUM (50/100)", HexColor('#B45309')),
        ("C", "EDR Tool Tampering", "HIGH (75/100)", HexColor('#B45309')),
        ("D", "Multi-Stage Killchain", "CRITICAL (100/100)", HEX_RED),
        ("E", "Legitimate Overtime", "BENIGN (0 ALERTS)", HEX_EMERALD)
    ]
    for idx, (slet, sname, ssev, scol) in enumerate(scenarios_pdf):
        sx = 55 + idx * (scen_w_pdf + scen_gap_pdf)
        draw_rounded_card(sx, 235, scen_w_pdf, 60)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HEX_INK)
        c.drawString(sx + 10, 278, f"Scenario {slet}: {sname}")

        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(scol)
        c.drawString(sx + 10, 258, f"{ssev} • MATCHED ✓")

    draw_rounded_card(55, 25, 419, 195)
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(HEX_INK)
    c.drawString(70, 202, "FUTURE SCOPE & TECHNICAL ROADMAP")

    fs_pdf = [
        ("Windows Event Log (EVTX) Parser:", "Direct binary ingestion for Security & Sysmon."),
        ("Expanded MITRE ATT&CK Mapping:", "Heuristics covering persistence & dumping."),
        ("INT4 / GGUF Quantization:", "Compressing weights for sub-500ms CPU generation."),
        ("Enterprise Log Volume Evals:", "Testing scalability against high-throughput streams.")
    ]
    fy = 176
    for ft, fd in fs_pdf:
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(HEX_INK)
        c.drawString(70, fy, f"• {ft} ")
        tw = c.stringWidth(f"• {ft} ", "Helvetica-Bold", 7.5)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        c.drawString(70 + tw, fy, fd)
        fy -= 24

    draw_rounded_card(490, 25, 419, 195)
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(HEX_INK)
    c.drawString(505, 202, "REFERENCES, ATTRIBUTION & DISCLOSURE")

    ref_pdf = [
        ("Model Attribution:", "HuggingFaceTB/SmolLM2-135M-Instruct (Apache 2.0)."),
        ("Software Stack:", "FastAPI, React 19, Vite, Tailwind CSS, ReportLab, Pydantic."),
        ("Test Verification:", "22 / 22 automated integration tests verified in 4.75s."),
        ("AI Assistance Disclosure:", "Assisted by AI coding agents under participant direction.")
    ]
    ry = 176
    for rt, rd in ref_pdf:
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(HEX_INK)
        c.drawString(505, ry, f"• {rt} ")
        tw = c.stringWidth(f"• {rt} ", "Helvetica-Bold", 7.5)
        c.setFont("Helvetica", 7.5)
        c.setFillColor(HEX_GREY_BODY)
        c.drawString(505 + tw, ry, rd)
        ry -= 24

    c.showPage()
    c.save()
    print(f"[✓] Generated PDF presentation: {PDF_PATH}")


def main():
    print("[1/2] Building PPTX presentation...")
    build_pptx_deck()

    print("[2/2] Building high-resolution PDF presentation...")
    build_pdf_deck()

    if PPTX_PATH.exists():
        size_mb = PPTX_PATH.stat().st_size / (1024 * 1024)
        print(f"      PPTX Size: {size_mb:.2f} MB (Limit: 10.0 MB)")
    if PDF_PATH.exists():
        size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
        print(f"      PDF Size:  {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
