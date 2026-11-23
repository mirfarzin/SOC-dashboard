"""
Detection Engine Orchestrator for PS02.
Coordinates execution of all independent detection rules.
"""

from typing import List
from src.detection.base import BaseDetector
from src.detection.failed_logins import FailedLoginsDetector
from src.detection.unusual_hours import UnusualHoursDetector
from src.detection.privilege_escalation import PrivilegeEscalationDetector
from src.detection.endpoint_activity import EndpointActivityDetector
from src.schema import NormalizedEvent, DetectionFinding
from src.config import AppConfig


class DetectionEngine:
    def __init__(self, config: AppConfig):
        self.config = config
        self.detectors: List[BaseDetector] = [
            FailedLoginsDetector(config),
            UnusualHoursDetector(config),
            PrivilegeEscalationDetector(config),
            EndpointActivityDetector(config),
        ]

    def run(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        """Run all configured detectors across events and collect all findings."""
        all_findings: List[DetectionFinding] = []
        for detector in self.detectors:
            try:
                findings = detector.evaluate(events)
                all_findings.extend(findings)
            except Exception as e:
                # Keep engine resilient
                print(f"[WARN] Detector {detector.rule_id} failed with error: {e}")
        return all_findings
