"""
Bonus Detector 4: Suspicious Endpoint Activity and Security Control Tampering.
Detects malicious process execution, credential dumping utilities, shadow copy deletion,
and defensive security service disabling.
"""

from typing import List
from src.detection.base import BaseDetector
from src.schema import NormalizedEvent, DetectionFinding
from src.config import AppConfig


class EndpointActivityDetector(BaseDetector):
    @property
    def rule_id(self) -> str:
        return "RULE_SUSPICIOUS_ENDPOINT_ACTIVITY"

    @property
    def rule_name(self) -> str:
        return "Suspicious Endpoint Execution & Defense Tampering"

    def evaluate(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        cfg = self.config.detectors.endpoint_activity
        if not cfg.enabled:
            return []

        suspicious_procs = [p.lower() for p in cfg.suspicious_processes]
        security_tampering = [t.lower() for t in cfg.security_controls_tampered]

        findings: List[DetectionFinding] = []

        for e in events:
            proc = (e.process_name or "").lower()
            cmd = (e.command_line or "").lower()
            action = (e.action or "").lower()
            combined = f"{proc} {cmd} {action}".strip()

            if not combined:
                continue

            # 1. Security control tampering / defense evasion
            tamper_match = next((t for t in security_tampering if t in combined), None)
            if tamper_match:
                weight = self.config.severity.weights.get("RULE_SECURITY_CONTROL_TAMPERING", 85)
                findings.append(DetectionFinding(
                    rule_id="RULE_SECURITY_CONTROL_TAMPERING",
                    rule_name="Security Control / EDR Tampering Detected",
                    description=f"Defense evasion indicator detected: '{tamper_match}' on '{e.device_id or 'host'}'",
                    severity_contribution=weight,
                    supporting_event_ids=[e.event_id],
                    timestamps=[e.timestamp],
                    relevant_entities={
                        "users": [e.username] if e.username else [],
                        "hosts": [e.device_id] if e.device_id else [],
                        "ips": [e.source_ip] if e.source_ip else []
                    },
                    explanation=(
                        f"CRITICAL DEFENSE EVASION: Command execution matching security control tampering "
                        f"('{tamper_match}') was observed under user '{e.username or 'SYSTEM'}' on "
                        f"endpoint '{e.device_id or 'unknown'}'. Full command: {e.command_line or e.action}. "
                        "This indicates an attempt to blind endpoint detection capabilities."
                    ),
                    is_authorized=False
                ))
                continue

            # 2. Suspicious process / tool execution
            proc_match = next((p for p in suspicious_procs if p in combined), None)
            if proc_match:
                weight = self.config.severity.weights.get("RULE_SUSPICIOUS_PROCESS_EXECUTION", 60)
                findings.append(DetectionFinding(
                    rule_id="RULE_SUSPICIOUS_PROCESS_EXECUTION",
                    rule_name="Suspicious Attack Utility Execution",
                    description=f"Offensive process/tool indicator detected: '{proc_match}'",
                    severity_contribution=weight,
                    supporting_event_ids=[e.event_id],
                    timestamps=[e.timestamp],
                    relevant_entities={
                        "users": [e.username] if e.username else [],
                        "hosts": [e.device_id] if e.device_id else [],
                        "ips": [e.source_ip] if e.source_ip else []
                    },
                    explanation=(
                        f"Suspicious utility '{proc_match}' executed on endpoint '{e.device_id or 'host'}' "
                        f"by account '{e.username or 'unknown'}'. Full command line: {e.command_line or e.process_name}. "
                        "This behavior is consistent with post-exploitation discovery or credential access."
                    ),
                    is_authorized=False
                ))

        return findings
