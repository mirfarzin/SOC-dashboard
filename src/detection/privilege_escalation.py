"""
Detector 3: Privilege Escalation and Sensitive Group Modification.
Detects additions to privileged groups (Administrators, sudo, Domain Admins) or role elevation.
Distinguishes authorized changes (linked to valid change tickets) from unexpected/unauthorized changes.
"""

from typing import List
from src.detection.base import BaseDetector
from src.schema import NormalizedEvent, DetectionFinding
from src.config import AppConfig


class PrivilegeEscalationDetector(BaseDetector):
    @property
    def rule_id(self) -> str:
        return "RULE_UNAUTHORIZED_PRIV_ESCALATION"

    @property
    def rule_name(self) -> str:
        return "Privilege Escalation / Sensitive Group Assignment"

    def evaluate(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        cfg = self.config.detectors.privilege_escalation
        if not cfg.enabled:
            return []

        sensitive_groups = [g.lower() for g in cfg.sensitive_groups]
        elevated_roles = [r.lower() for r in cfg.elevated_roles]

        findings: List[DetectionFinding] = []

        for e in events:
            # Check privilege_change field or action/event_type
            priv_field = (e.privilege_change or "").lower()
            action_field = (e.action or "").lower()
            event_type = (e.event_type or "").lower()

            is_priv_event = False
            detected_group = None

            # Pattern 1: Explicit privilege change field
            for g in sensitive_groups:
                if g in priv_field or g in action_field:
                    is_priv_event = True
                    detected_group = g
                    break

            # Pattern 2: Explicit role or sudo assignment
            if not is_priv_event:
                for r in elevated_roles:
                    if r in priv_field or r in action_field:
                        is_priv_event = True
                        detected_group = r
                        break

            # Pattern 3: Windows Event ID 4728/4732/4756 (member added to security group)
            raw = e.raw_event or {}
            win_evt_id = str(raw.get("EventID") or raw.get("event_id") or "")
            if win_evt_id in ["4728", "4732", "4756"]:
                is_priv_event = True
                detected_group = detected_group or "Local/Domain Security Group"

            # Linux sudoers modification or usermod -aG sudo/wheel
            if "sudo" in action_field or "wheel" in action_field or "usermod" in action_field:
                is_priv_event = True
                detected_group = detected_group or "sudo/wheel group"

            if not is_priv_event:
                continue

            # Determine authorization status via approval_reference or change ticket
            has_approval = bool(e.approval_reference and len(e.approval_reference.strip()) > 2)
            ticket_id = e.approval_reference if has_approval else None

            target = e.target_user or e.username or "Unknown Target User"
            actor = e.username or "SYSTEM/Unknown Actor"
            host = e.device_id or "Unknown Host"

            users = list(set(u for u in [actor, target] if u))

            if has_approval:
                # Authorized change: low severity contribution, transparently documented
                weight = self.config.severity.weights.get("RULE_AUTHORIZED_PRIV_ESCALATION", 10)
                explanation = (
                    f"User '{target}' was granted elevated group membership / role ({detected_group or priv_field}) "
                    f"by '{actor}' on host '{host}'. "
                    f"Evidence indicates this change is formally authorized under Change Ticket '{ticket_id}'."
                )
                findings.append(DetectionFinding(
                    rule_id="RULE_AUTHORIZED_PRIV_ESCALATION",
                    rule_name="Authorized Sensitive Privilege Modification",
                    description=f"Privilege change for '{target}' with ticket '{ticket_id}'",
                    severity_contribution=weight,
                    supporting_event_ids=[e.event_id],
                    timestamps=[e.timestamp],
                    relevant_entities={"users": users, "hosts": [host] if host else [], "ips": [e.source_ip] if e.source_ip else []},
                    explanation=explanation,
                    is_authorized=True
                ))
            else:
                # Unexpected / Unauthorized change: high severity
                weight = self.config.severity.weights.get("RULE_UNAUTHORIZED_PRIV_ESCALATION", 75)
                explanation = (
                    f"CRITICAL PRIVILEGE ANOMALY: User '{target}' was added to high-privilege group/role "
                    f"'{detected_group or priv_field}' by actor '{actor}' on '{host}' without any recorded change ticket, "
                    "approval reference, or maintenance authorization in telemetry. "
                    "This strongly resembles persistence establishment or unauthorized privilege escalation."
                )
                findings.append(DetectionFinding(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    description=f"Unapproved privilege escalation: '{target}' added to '{detected_group or priv_field}'",
                    severity_contribution=weight,
                    supporting_event_ids=[e.event_id],
                    timestamps=[e.timestamp],
                    relevant_entities={"users": users, "hosts": [host] if host else [], "ips": [e.source_ip] if e.source_ip else []},
                    explanation=explanation,
                    is_authorized=False
                ))

        return findings
