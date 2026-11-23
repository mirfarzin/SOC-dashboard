"""
Detector 1: Repeated Failed Logins with Potential Burst Compromise Escalation.
Detects >= N failed authentication attempts within a sliding time window.
Escalates significantly if followed by a successful authentication attempt.
"""

from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Tuple
from src.detection.base import BaseDetector
from src.schema import NormalizedEvent, DetectionFinding, AuthResult
from src.config import AppConfig


class FailedLoginsDetector(BaseDetector):
    @property
    def rule_id(self) -> str:
        return "RULE_FAILED_LOGIN_BURST"

    @property
    def rule_name(self) -> str:
        return "Repeated Failed Logins with Burst Escalation"

    def evaluate(self, events: List[NormalizedEvent]) -> List[DetectionFinding]:
        cfg = self.config.detectors.failed_logins
        if not cfg.enabled:
            return []

        findings: List[DetectionFinding] = []

        # Filter authentication events
        auth_events = [
            e for e in events
            if e.event_type in ["login", "authentication", "logon", "auth", "general"]
            or e.authentication_result != AuthResult.UNKNOWN
        ]
        # Sort chronologically
        auth_events.sort(key=lambda x: x.timestamp)

        # Group by correlation key: primarily username; if missing, source_ip
        grouped: Dict[str, List[NormalizedEvent]] = defaultdict(list)
        for e in auth_events:
            key = e.username or e.source_ip or e.device_id or "unknown_identity"
            grouped[key].append(e)

        window_delta = timedelta(seconds=cfg.window_seconds)
        success_delta = timedelta(seconds=cfg.success_window_seconds)

        for identity, id_events in grouped.items():
            n = len(id_events)
            i = 0
            while i < n:
                # Only start from a failure
                if id_events[i].authentication_result != AuthResult.FAILURE:
                    i += 1
                    continue

                window_start = id_events[i].timestamp
                window_end = window_start + window_delta

                # Collect all failures within window
                failures_in_window: List[NormalizedEvent] = []
                j = i
                while j < n and id_events[j].timestamp <= window_end:
                    if id_events[j].authentication_result == AuthResult.FAILURE:
                        failures_in_window.append(id_events[j])
                    j += 1

                if len(failures_in_window) >= cfg.failure_threshold:
                    # Burst detected!
                    last_failure_time = failures_in_window[-1].timestamp
                    burst_event_ids = [e.event_id for e in failures_in_window]
                    burst_timestamps = [e.timestamp for e in failures_in_window]

                    # Check for follow-up successful login within success_window_seconds
                    success_follow_up: List[NormalizedEvent] = []
                    if cfg.escalate_on_success_after_burst:
                        for ev in id_events:
                            if ev.timestamp > last_failure_time and ev.timestamp <= (last_failure_time + success_delta):
                                if ev.authentication_result == AuthResult.SUCCESS:
                                    success_follow_up.append(ev)

                    users = list(set(e.username for e in failures_in_window if e.username))
                    hosts = list(set(e.device_id for e in failures_in_window if e.device_id))
                    ips = list(set(e.source_ip for e in failures_in_window if e.source_ip))

                    if success_follow_up:
                        succ = success_follow_up[0]
                        burst_event_ids.append(succ.event_id)
                        burst_timestamps.append(succ.timestamp)
                        if succ.username and succ.username not in users:
                            users.append(succ.username)
                        if succ.device_id and succ.device_id not in hosts:
                            hosts.append(succ.device_id)
                        if succ.source_ip and succ.source_ip not in ips:
                            ips.append(succ.source_ip)

                        weight = self.config.severity.weights.get("RULE_BURST_FOLLOWED_BY_SUCCESS", 65)
                        findings.append(DetectionFinding(
                            rule_id="RULE_BURST_FOLLOWED_BY_SUCCESS",
                            rule_name="Brute-Force / Credential Burst Followed by Successful Login",
                            description=(
                                f"Detected {len(failures_in_window)} failed authentications within "
                                f"{cfg.window_seconds}s followed by successful authentication for '{identity}'."
                            ),
                            severity_contribution=weight,
                            supporting_event_ids=burst_event_ids,
                            timestamps=burst_timestamps,
                            relevant_entities={"users": users, "hosts": hosts, "ips": ips},
                            explanation=(
                                f"High-risk pattern: Entity '{identity}' experienced {len(failures_in_window)} consecutive "
                                f"authentication failures between {window_start.strftime('%H:%M:%S')} and "
                                f"{last_failure_time.strftime('%H:%M:%S')}, followed immediately by successful logon "
                                f"(Event {succ.event_id}) at {succ.timestamp.strftime('%H:%M:%S')}. "
                                "This indicates potential password guessing, spray, or brute-force compromise."
                            ),
                            is_authorized=False
                        ))
                    else:
                        weight = self.config.severity.weights.get("RULE_FAILED_LOGIN_BURST", 35)
                        findings.append(DetectionFinding(
                            rule_id=self.rule_id,
                            rule_name=self.rule_name,
                            description=f"Detected {len(failures_in_window)} failed authentication attempts within {cfg.window_seconds}s for '{identity}'.",
                            severity_contribution=weight,
                            supporting_event_ids=burst_event_ids,
                            timestamps=burst_timestamps,
                            relevant_entities={"users": users, "hosts": hosts, "ips": ips},
                            explanation=(
                                f"Entity '{identity}' registered {len(failures_in_window)} failed logins within "
                                f"a {cfg.window_seconds//60}-minute sliding window. Source IPs involved: {', '.join(ips) or 'Local'}."
                            ),
                            is_authorized=False
                        ))

                    # Move index past the current burst window
                    i = j
                else:
                    i += 1

        return findings
