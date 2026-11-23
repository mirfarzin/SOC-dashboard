"""
Command Line Interface (CLI) for PS02 Offline Security Incident Triage Assistant.
Enables reliable, non-interactive or scripted demonstrations of ingestion,
detection, event correlation, SLM triage, evaluation, and multi-format reporting.
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import load_config
from src.ingestion.parser import ingest_file
from src.ingestion.validator import IngestionDiagnostics
from src.detection.engine import DetectionEngine
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier
from src.slm.model_runner import LocalSLMRunner
from src.reporting.generator import ReportGenerator
from src.reporting.pdf_exporter import PDFReportExporter
from src.evaluation.evaluator import EvaluationSuite
from src.slm.download_model import download_and_cache_model


def run_triage(args):
    print("=" * 70)
    print("PS02: OFFLINE SECURITY INCIDENT TRIAGE ASSISTANT")
    print("Domain: Cybersecurity | Small Language Models (SLMs)")
    print("Author: Mir Farzin Hussain (USN: 1MS24CI073)")
    print("=" * 70)

    cfg = load_config(args.config)
    if args.model_path:
        cfg.slm.local_model_path = args.model_path

    # Ingestion
    print(f"\n[1/5] Ingesting Telemetry Logs...")
    events = []
    errors = []

    if args.auth_file:
        res_auth = ingest_file(args.auth_file, default_tz=cfg.organization.timezone)
        events.extend(res_auth.events)
        errors.extend(res_auth.errors)
        print(f"  - Authentication Logs ({args.auth_file}): {len(res_auth.events)} valid events, {len(res_auth.errors)} errors")

    if args.endpoint_file:
        res_endp = ingest_file(args.endpoint_file, default_tz=cfg.organization.timezone)
        events.extend(res_endp.events)
        errors.extend(res_endp.errors)
        print(f"  - Endpoint Logs ({args.endpoint_file}): {len(res_endp.events)} valid events, {len(res_endp.errors)} errors")

    if not events:
        print("[ERROR] No valid events found. Exiting.")
        return

    # Detection
    print(f"\n[2/5] Running Suspicious Activity Detectors...")
    detection_engine = DetectionEngine(cfg)
    findings = detection_engine.run(events)
    print(f"  - Triggered Findings: {len(findings)}")
    for f in findings:
        print(f"    • [{f.rule_id}] {f.rule_name} (+{f.severity_contribution}) | Evidence: {', '.join(f.supporting_event_ids[:3])}")

    # Correlation
    print(f"\n[3/5] Correlating Related Security Events...")
    correlator = EventCorrelator(cfg)
    raw_incidents = correlator.correlate(events, findings)
    print(f"  - Correlated Incidents Formed: {len(raw_incidents)}")

    # Severity Classification
    print(f"\n[4/5] Executing Deterministic Severity Classifier...")
    classifier = SeverityClassifier(cfg)
    incidents = [classifier.classify(inc) for inc in raw_incidents]

    for inc in incidents:
        print(f"  - Case {inc.incident_id}: [{inc.severity.value.upper()}] (Score: {inc.severity_score}/100) - {inc.title}")

    # SLM Triage & Reporting
    print(f"\n[5/5] Generating Evidence-Backed SLM Triage Briefs...")
    slm_runner = LocalSLMRunner(cfg)
    is_offline_ready = slm_runner.load_model()
    print(f"  - Local SLM Engine Status: {'Active (Local Weights)' if is_offline_ready else 'Deterministic Heuristic Fallback'}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for inc in incidents:
        analysis, latency = slm_runner.analyze(inc)
        report = ReportGenerator.create_report(
            incident=inc,
            slm_analysis=analysis,
            inference_latency_ms=latency,
            offline_mode=True
        )

        base_name = f"{inc.incident_id}_report"
        json_path = out_dir / f"{base_name}.json"
        md_path = out_dir / f"{base_name}.md"
        pdf_path = out_dir / f"{base_name}.pdf"

        ReportGenerator.export_json(report, json_path)
        ReportGenerator.export_markdown(report, md_path)
        PDFReportExporter.export(report, pdf_path)

        print(f"\n  ========================================================")
        print(f"  INCIDENT: {inc.incident_id} | SEVERITY: {inc.severity.value.upper()} ({inc.severity_score}/100)")
        print(f"  TITLE:    {analysis.title}")
        print(f"  MODEL:    {analysis.model_name} (Inference: {latency:.1f}ms)")
        print(f"  AUDIT:    Hallucination Validation: {'PASSED' if analysis.validation_passed else 'FLAGGED'}")
        print(f"  EXECUTIVE SUMMARY:")
        print(f"    {analysis.executive_summary}")
        print(f"  VERIFIED FACTS ({len(analysis.facts)}):")
        for f in analysis.facts[:2]:
            print(f"    • {f}")
        print(f"  RECOMMENDED ADVISORY ACTIONS ({len(analysis.recommended_actions)}):")
        for a in analysis.recommended_actions[:2]:
            print(f"    • {a}")
        print(f"  EXPORTS:")
        print(f"    - JSON:     {json_path}")
        print(f"    - Markdown: {md_path}")
        print(f"    - PDF:      {pdf_path}")
        print(f"  ========================================================")

    print(f"\n[SUCCESS] Triage completed successfully. All artifacts written to '{out_dir}'.")


def run_benchmark(args):
    print("=" * 70)
    print("PS02 EVALUATION BENCHMARK (Synthetic Ground-Truth Verification)")
    print("=" * 70)
    cfg = load_config(args.config)
    evaluator = EvaluationSuite(cfg)
    results = evaluator.run_benchmark(args.auth_file, args.endpoint_file, args.ground_truth)
    print(json.dumps(results, indent=2))


def run_download(args):
    download_and_cache_model(args.model_id, args.target_dir)


def main():
    parser = argparse.ArgumentParser(
        description="PS02 Offline Security Incident Triage Assistant CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: triage
    p_triage = subparsers.add_parser("triage", help="Run full offline incident triage pipeline")
    p_triage.add_argument("--auth-file", default="PS02_Offline_Security_Incident_Triage_Assistant/data/synthetic/auth_logs.csv", help="Path to authentication log CSV/JSON")
    p_triage.add_argument("--endpoint-file", default="PS02_Offline_Security_Incident_Triage_Assistant/data/synthetic/endpoint_logs.csv", help="Path to endpoint log CSV/JSON")
    p_triage.add_argument("--config", default="PS02_Offline_Security_Incident_Triage_Assistant/config/settings.yaml", help="Path to settings.yaml")
    p_triage.add_argument("--model-path", default="PS02_Offline_Security_Incident_Triage_Assistant/models/SmolLM2-135M-Instruct", help="Path to local SLM weights")
    p_triage.add_argument("--output-dir", default="PS02_Offline_Security_Incident_Triage_Assistant/reports", help="Directory for exported reports")
    p_triage.set_defaults(func=run_triage)

    # Subcommand: benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run evaluation benchmark against ground truth")
    p_bench.add_argument("--auth-file", default="PS02_Offline_Security_Incident_Triage_Assistant/data/synthetic/auth_logs.csv")
    p_bench.add_argument("--endpoint-file", default="PS02_Offline_Security_Incident_Triage_Assistant/data/synthetic/endpoint_logs.csv")
    p_bench.add_argument("--ground-truth", default="PS02_Offline_Security_Incident_Triage_Assistant/data/synthetic/ground_truth.json")
    p_bench.add_argument("--config", default="PS02_Offline_Security_Incident_Triage_Assistant/config/settings.yaml")
    p_bench.set_defaults(func=run_benchmark)

    # Subcommand: download-model
    p_down = subparsers.add_parser("download-model", help="Download and cache model for offline use")
    p_down.add_argument("--model-id", default="HuggingFaceTB/SmolLM2-135M-Instruct")
    p_down.add_argument("--target-dir", default="PS02_Offline_Security_Incident_Triage_Assistant/models/SmolLM2-135M-Instruct")
    p_down.set_defaults(func=run_download)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
