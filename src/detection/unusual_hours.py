"""
Detector 2: Unusual Login Hours Analysis.
Detects successful authentications occurring outside configured organization working hours
or during weekends, recording timezone and providing contextual reasoning.
"""

from typing import List
import zoneinfo
from src.detection.base import BaseDetector
from src.schema import NormalizedEvent, DetectionFinding, AuthResult
from src.config import AppConfig


class UnusualHoursDetector(BaseDetector):
    @property
    def rule_id(self) -> str:
        return "RULE_UNUSUAL_LOGIN_HOURS"

    @property
    def rule_name(self) -> str:
        return "Authentication Outside Standard Working Hours"

    def evaluate(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        cfg = self.config.detectors.unusual_hours
        if not cfg.enabled:
            return []

        org_cfg = self.config.organization
        tz_name = org_cfg.timezone
        tz = zoneinfo.ZoneInfo(tz_name)

        start_h = org_cfg.working_hours.start_hour
        end_h = org_cfg.working_hours.end_hour
        working_days = org_cfg.working_days
        flag_weekend = org_cfg.weekend_is_unusual

        findings: List[DetectionFinding] = []

        for e in events:
            # Only evaluate successful logins
            if e.authentication_result != AuthResult.SUCCESS:
                continue

            event_time = e.timestamp.astimezone(tz)
            weekday = event_time.weekday()  # 0=Monday, 6=Sunday
            hour = event_time.hour
            is_weekend = weekday not in working_days
            is_outside_hours = (hour < start_h) or (hour >= end_h)

            if is_outside_hours or (is_weekend and flag_weekend):
                # Contextual reasoning
                reasons = []
                if is_outside_hours:
                    reasons.append(f"time {event_time.strftime('%H:%M:%S')} is outside business hours ({start_h:02d}:00 - {end_h:02d}:00 {tz_name})")
                if is_weekend and flag_weekend:
                    day_name = event_time.strftime('%A')
                    reasons.append(f"login occurred on {day_name} (non-business day)")

                # Entity context
                user = e.username or "Unknown User"
                host = e.device_id or "Unknown Host"
                ip = e.source_ip or "Local"

                # Check if privileged account
                is_admin = any(k in user.lower() for k in ["admin", "root", "secops", "service"])
                context_notes = []
                if is_admin:
                    context_notes.append("Account possesses administrative privileges, elevating triage priority")
                else:
                    context_notes.append("Account is a standard user; out-of-hours access requires supervisor verification")

                weight = self.config.severity.weights.get(self.rule_id, 25)
                # Boost weight slightly if admin or middle of the night (00:00 - 05:00)
                if hour < 5:
                    weight = min(weight + 10, 50)
                    context_notes.append("Deep night logon window (00:00 - 05:00) carries heightened risk of unauthorized access")

                explanation = (
                    f"User '{user}' successfully logged into '{host}' from IP '{ip}' at "
                    f"{event_time.strftime('%Y-%m-%d %H:%M:%S %Z')}. "
                    f"Flagged because: {'; '.join(reasons)}. "
                    f"Context: {'. '.join(context_notes)}."
                )

                findings.append(DetectionFinding(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    description=f"Out-of-hours login for '{user}' at {event_time.strftime('%H:%M %Z')}",
                    severity_contribution=weight,
                    supporting_event_ids=[e.event_id],
                    timestamps=[e.timestamp],
                    relevant_entities={
                        "users": [user] if user else [],
                        "hosts": [host] if host else [],
                        "ips": [ip] if ip else []
                    },
                    explanation=explanation,
                    is_authorized=False
                ))

        return findings
