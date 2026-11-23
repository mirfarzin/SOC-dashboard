"""
Automated End-to-End Pipeline Integration Test.
Executes complete triage lifecycle from raw log files to final JSON, Markdown, and PDF reports.
"""

from pathlib import Path
import pytest

from src.config import load_config
from src.ingestion.parser import ingest_file
from src.detection.engine import DetectionEngine
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier
from src.slm.model_runner import RuleBasedSLMFallback
from src.reporting.generator import ReportGenerator
from src.reporting.pdf_exporter import PDFReportExporter


def test_full_end_to_end_pipeline(tmp_path):
    base_dir = Path(__file__).resolve().parent.parent
    auth_csv = base_dir / "data" / "synthetic" / "auth_logs.csv"
    endp_csv = base_dir / "data" / "synthetic" / "endpoint_logs.csv"

    cfg = load_config(base_dir / "config" / "settings.yaml")

    # 1. Ingestion
    res_auth = ingest_file(auth_csv)
    res_endp = ingest_file(endp_csv)
    events = res_auth.events + res_endp.events
    assert len(events) == 20

    # 2. Detection
    engine = DetectionEngine(cfg)
    findings = engine.run(events)
    assert len(findings) > 0

    # 3. Correlation
    correlator = EventCorrelator(cfg)
    raw_incidents = correlator.correlate(events, findings)
    assert len(raw_incidents) == 5

    # 4. Severity Classification
    classifier = SeverityClassifier(cfg)
    incidents = [classifier.classify(inc) for inc in raw_incidents]

    # Verify high-priority critical incident
    crit_inc = next((i for i in incidents if i.severity.value == "Critical"), None)
    assert crit_inc is not None
    assert "target_admin" in crit_inc.entities_involved["users"]

    # 5. Triage Reporting & Multi-Format Exports
    analysis = RuleBasedSLMFallback.generate(crit_inc, reason="EndToEndTest")
    report = ReportGenerator.create_report(crit_inc, analysis, inference_latency_ms=1.5, offline_mode=True)

    json_file = tmp_path / "test_report.json"
    md_file = tmp_path / "test_report.md"
    pdf_file = tmp_path / "test_report.pdf"

    ReportGenerator.export_json(report, json_file)
    ReportGenerator.export_markdown(report, md_file)
    PDFReportExporter.export(report, pdf_file)

    assert json_file.exists() and json_file.stat().st_size > 500
    assert md_file.exists() and md_file.stat().st_size > 500
    assert pdf_file.exists() and pdf_file.stat().st_size > 1000
