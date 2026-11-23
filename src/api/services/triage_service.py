"""
Core Triage Service for FastAPI Backend.
Reuses existing detection, correlation, severity, SLM, and reporting engines
without altering any underlying cybersecurity logic.
"""

from __future__ import annotations
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import load_config, AppConfig
from src.ingestion.parser import ingest_file, ingest_json, ingest_csv, IngestionResult
from src.ingestion.validator import IngestionDiagnostics
from src.detection.engine import DetectionEngine
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier
from src.slm.model_runner import LocalSLMRunner, RuleBasedSLMFallback
from src.reporting.generator import ReportGenerator
from src.reporting.pdf_exporter import PDFReportExporter
from src.evaluation.evaluator import EvaluationSuite
from src.schema import Incident, NormalizedEvent, TriageReport


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class TriageService:
    _instance: Optional[TriageService] = None

    def __init__(self):
        self.config: AppConfig = load_config(BASE_DIR / "config" / "settings.yaml")
        self.events: List[NormalizedEvent] = []
        self.incidents: List[Incident] = []
        self.reports: Dict[str, TriageReport] = {}
        self.diagnostics: Dict[str, Any] = {}
        self.evaluation_results: Optional[Dict[str, Any]] = None
        self.slm_runner = LocalSLMRunner(self.config)
        self.reports_dir = BASE_DIR / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Pre-load demo dataset on initialization
        self.load_demo_dataset()

    @classmethod
    def get_instance(cls) -> TriageService:
        if cls._instance is None:
            cls._instance = TriageService()
        return cls._instance

    def load_demo_dataset(self) -> Dict[str, Any]:
        """Load synthetic Scenarios A through E and execute full triage."""
        auth_p = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
        endp_p = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
        gt_p = BASE_DIR / "data" / "synthetic" / "ground_truth.json"

        if not auth_p.exists() or not endp_p.exists():
            return {"status": "error", "message": "Synthetic data files not found"}

        res_auth = ingest_file(auth_p, default_tz=self.config.organization.timezone)
        res_endp = ingest_file(endp_p, default_tz=self.config.organization.timezone)

        self._process_events(res_auth.events + res_endp.events, res_auth.errors + res_endp.errors)

        # Run evaluation against ground truth
        evaluator = EvaluationSuite(self.config)
        self.evaluation_results = evaluator.run_benchmark(auth_p, endp_p, gt_p)

        return self.get_dashboard_summary()

    def ingest_logs(
        self,
        auth_content: Optional[bytes] = None,
        auth_filename: Optional[str] = None,
        endpoint_content: Optional[bytes] = None,
        endpoint_filename: Optional[str] = None,
        mode: str = "fast"
    ) -> Dict[str, Any]:
        """Ingest uploaded authentication and endpoint log files."""
        events = []
        errors = []

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            if auth_content and auth_filename:
                p_auth = tmp_path / auth_filename
                p_auth.write_bytes(auth_content)
                res_auth = ingest_file(p_auth, default_tz=self.config.organization.timezone)
                events.extend(res_auth.events)
                errors.extend(res_auth.errors)

            if endpoint_content and endpoint_filename:
                p_endp = tmp_path / endpoint_filename
                p_endp.write_bytes(endpoint_content)
                res_endp = ingest_file(p_endp, default_tz=self.config.organization.timezone)
                events.extend(res_endp.events)
                errors.extend(res_endp.errors)

        if not events and not errors:
            raise ValueError("No valid logs provided for processing.")

        self._process_events(events, errors, mode=mode)
        return self.get_dashboard_summary()

    def _process_events(self, events: List[NormalizedEvent], errors: List[Dict[str, Any]], mode: str = "fast"):
        """Internal pipeline orchestrating detection, correlation, severity, and report generation."""
        t0 = time.perf_counter()

        # 1. Detection
        engine = DetectionEngine(self.config)
        findings = engine.run(events)

        # 2. Correlation
        correlator = EventCorrelator(self.config)
        raw_incidents = correlator.correlate(events, findings)

        # 3. Severity Classification
        classifier = SeverityClassifier(self.config)
        incidents = [classifier.classify(inc) for inc in raw_incidents]

        self.events = events
        self.incidents = incidents
        self.diagnostics = IngestionDiagnostics.audit_events(events, errors)

        # 4. Generate Reports for every incident
        reports_map = {}
        for inc in incidents:
            if mode == "neural" and self.slm_runner.is_available:
                analysis, latency = self.slm_runner.analyze(inc)
            else:
                analysis = RuleBasedSLMFallback.generate(inc, reason="Fast Deterministic Mode")
                latency = (time.perf_counter() - t0) * 1000

            rep = ReportGenerator.create_report(inc, analysis, inference_latency_ms=latency, offline_mode=True)
            reports_map[inc.incident_id] = rep

            # Export files
            base = f"{inc.incident_id}_report"
            ReportGenerator.export_json(rep, self.reports_dir / f"{base}.json")
            ReportGenerator.export_markdown(rep, self.reports_dir / f"{base}.md")
            PDFReportExporter.export(rep, self.reports_dir / f"{base}.pdf")

        self.reports = reports_map

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Return high-level summary KPIs for the SOC Overview."""
        sev_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        for inc in self.incidents:
            sev_dist[inc.severity.value] += 1

        recent_cases = []
        for inc in self.incidents:
            rep = self.reports.get(inc.incident_id)
            recent_cases.append({
                "incident_id": inc.incident_id,
                "title": inc.title,
                "severity": inc.severity.value,
                "severity_score": inc.severity_score,
                "users": inc.entities_involved.get("users", []),
                "hosts": inc.entities_involved.get("hosts", []),
                "event_count": len(inc.event_ids),
                "created_at": inc.created_at.isoformat() if hasattr(inc.created_at, "isoformat") else str(inc.created_at)
            })

        model_path = BASE_DIR / "models" / "SmolLM2-135M-Instruct"
        has_weights = model_path.exists() and (model_path / "config.json").exists()

        return {
            "total_events": len(self.events),
            "total_incidents": len(self.incidents),
            "high_critical_count": sev_dist["Critical"] + sev_dist["High"],
            "severity_distribution": sev_dist,
            "operating_mode": "100% OFFLINE",
            "model_status": {
                "name": self.config.slm.model_id,
                "cached": has_weights,
                "device": self.config.slm.device,
                "offline_enforced": True
            },
            "recent_incidents": recent_cases,
            "diagnostics": self.diagnostics
        }

    def get_incidents_list(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return list of incidents with filtering."""
        result = []
        for inc in self.incidents:
            if severity and inc.severity.value.lower() != severity.lower():
                continue
            rep = self.reports.get(inc.incident_id)
            result.append({
                "incident_id": inc.incident_id,
                "title": inc.title,
                "severity": inc.severity.value,
                "severity_score": inc.severity_score,
                "severity_breakdown": inc.severity_breakdown,
                "correlation_explanation": inc.correlation_explanation,
                "users": inc.entities_involved.get("users", []),
                "hosts": inc.entities_involved.get("hosts", []),
                "ips": inc.entities_involved.get("ips", []),
                "event_count": len(inc.event_ids),
                "finding_count": len(inc.findings),
                "created_at": inc.created_at.isoformat() if hasattr(inc.created_at, "isoformat") else str(inc.created_at)
            })
        return result

    def get_incident_detail(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Return full incident details including SLM report, timeline, facts, hypotheses, and recommendations."""
        inc = next((i for i in self.incidents if i.incident_id == incident_id), None)
        if not inc:
            return None

        rep = self.reports.get(incident_id)
        slm_data = rep.slm_analysis.model_dump() if rep else {}
        prov = rep.provenance if rep else {}

        findings_data = []
        for f in inc.findings:
            findings_data.append({
                "rule_id": f.rule_id,
                "rule_name": f.rule_name,
                "description": f.description,
                "severity_contribution": f.severity_contribution,
                "is_authorized": f.is_authorized,
                "supporting_event_ids": f.supporting_event_ids,
                "explanation": f.explanation
            })

        return {
            "incident": {
                "incident_id": inc.incident_id,
                "title": inc.title,
                "severity": inc.severity.value,
                "severity_score": inc.severity_score,
                "severity_breakdown": inc.severity_breakdown,
                "correlation_explanation": inc.correlation_explanation,
                "entities_involved": inc.entities_involved,
                "event_ids": inc.event_ids,
                "timeline": inc.timeline,
                "findings": findings_data,
                "created_at": inc.created_at.isoformat() if hasattr(inc.created_at, "isoformat") else str(inc.created_at)
            },
            "slm_analysis": slm_data,
            "provenance": prov
        }

    def get_evaluation(self) -> Dict[str, Any]:
        """Return ground truth benchmark results."""
        if self.evaluation_results is None:
            auth_p = BASE_DIR / "data" / "synthetic" / "auth_logs.csv"
            endp_p = BASE_DIR / "data" / "synthetic" / "endpoint_logs.csv"
            gt_p = BASE_DIR / "data" / "synthetic" / "ground_truth.json"
            evaluator = EvaluationSuite(self.config)
            self.evaluation_results = evaluator.run_benchmark(auth_p, endp_p, gt_p)
        return self.evaluation_results

    def get_config_view(self) -> Dict[str, Any]:
        """Return runtime configuration."""
        return {
            "organization": self.config.organization.model_dump(),
            "detectors": self.config.detectors.model_dump(),
            "correlation": self.config.correlation.model_dump(),
            "severity": self.config.severity.model_dump(),
            "slm": self.config.slm.model_dump()
        }

    def get_report_export(self, incident_id: str, fmt: str) -> Tuple[Optional[bytes], str, str]:
        """
        Return export bytes, media_type, and filename for an incident report.
        fmt can be 'json', 'md', or 'pdf'.
        """
        fmt = fmt.lower()
        if fmt == "json":
            file_path = self.reports_dir / f"{incident_id}_report.json"
            if file_path.exists():
                return file_path.read_bytes(), "application/json", f"{incident_id}_triage.json"
        elif fmt in ["md", "markdown"]:
            file_path = self.reports_dir / f"{incident_id}_report.md"
            if file_path.exists():
                return file_path.read_bytes(), "text/markdown", f"{incident_id}_triage.md"
        elif fmt == "pdf":
            file_path = self.reports_dir / f"{incident_id}_report.pdf"
            if file_path.exists():
                return file_path.read_bytes(), "application/pdf", f"{incident_id}_executive_report.pdf"

        return None, "", ""
