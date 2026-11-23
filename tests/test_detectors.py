"""
Automated tests for Suspicious Activity Detectors.
Verifies failed login burst detection, unusual hours, and privilege escalation with ticket checks.
"""

from datetime import datetime, timedelta
import zoneinfo
import pytest

from src.config import load_config
from src.schema import NormalizedEvent, AuthResult
from src.detection.failed_logins import FailedLoginsDetector
from src.detection.unusual_hours import UnusualHoursDetector
from src.detection.privilege_escalation import PrivilegeEscalationDetector
from src.detection.endpoint_activity import EndpointActivityDetector

TZ = zoneinfo.ZoneInfo("Asia/Kolkata")
BASE_TIME = datetime(2026, 11, 23, 10, 0, 0, tzinfo=TZ)


def test_failed_logins_burst_and_success_escalation():
    cfg = load_config()
    detector = FailedLoginsDetector(cfg)

    # 1. Five rapid failures
    events = []
    for i in range(5):
        events.append(NormalizedEvent(
            event_id=f"EVT-F-{i}",
            timestamp=BASE_TIME + timedelta(seconds=i * 20),
            username="victim_user",
            device_id="WS-01",
            source_ip="192.168.1.50",
            action="login",
            authentication_result=AuthResult.FAILURE
        ))

    findings = detector.evaluate(events)
    assert len(findings) == 1
    assert findings[0].rule_id == "RULE_FAILED_LOGIN_BURST"
    assert len(findings[0].supporting_event_ids) == 5

    # 2. Add successful login following burst
    events.append(NormalizedEvent(
        event_id="EVT-SUCCESS-01",
        timestamp=BASE_TIME + timedelta(seconds=120),
        username="victim_user",
        device_id="WS-01",
        source_ip="192.168.1.50",
        action="login",
        authentication_result=AuthResult.SUCCESS
    ))

    escalated_findings = detector.evaluate(events)
    assert len(escalated_findings) == 1
    assert escalated_findings[0].rule_id == "RULE_BURST_FOLLOWED_BY_SUCCESS"
    assert "EVT-SUCCESS-01" in escalated_findings[0].supporting_event_ids


def test_unusual_hours_detector():
    cfg = load_config()
    detector = UnusualHoursDetector(cfg)

    # Legitimate daytime login (11:00 AM)
    day_evt = NormalizedEvent(
        event_id="EVT-DAY",
        timestamp=BASE_TIME.replace(hour=11),
        username="normal_user",
        action="login",
        authentication_result=AuthResult.SUCCESS
    )
    assert len(detector.evaluate([day_evt])) == 0

    # Night login at 02:30 AM
    night_evt = NormalizedEvent(
        event_id="EVT-NIGHT",
        timestamp=BASE_TIME.replace(hour=2, minute=30),
        username="normal_user",
        action="login",
        authentication_result=AuthResult.SUCCESS
    )
    findings = detector.evaluate([night_evt])
    assert len(findings) == 1
    assert findings[0].rule_id == "RULE_UNUSUAL_LOGIN_HOURS"
    assert "EVT-NIGHT" in findings[0].supporting_event_ids


def test_privilege_escalation_authorized_vs_unauthorized():
    cfg = load_config()
    detector = PrivilegeEscalationDetector(cfg)

    # Unauthorized: User added to Administrators without ticket
    unauth_evt = NormalizedEvent(
        event_id="EVT-UNAUTH-PRIV",
        timestamp=BASE_TIME,
        username="actor_admin",
        target_user="bad_actor",
        privilege_change="Administrators",
        action="member_added",
        approval_reference=None
    )
    f_unauth = detector.evaluate([unauth_evt])
    assert len(f_unauth) == 1
    assert f_unauth[0].rule_id == "RULE_UNAUTHORIZED_PRIV_ESCALATION"
    assert f_unauth[0].is_authorized is False

    # Authorized: Valid change ticket CHG-5512 present
    auth_evt = NormalizedEvent(
        event_id="EVT-AUTH-PRIV",
        timestamp=BASE_TIME,
        username="secops_lead",
        target_user="backup_service",
        privilege_change="Administrators",
        action="member_added",
        approval_reference="CHG-5512"
    )
    f_auth = detector.evaluate([auth_evt])
    assert len(f_auth) == 1
    assert f_auth[0].rule_id == "RULE_AUTHORIZED_PRIV_ESCALATION"
    assert f_auth[0].is_authorized is True


def test_endpoint_tampering_detector():
    cfg = load_config()
    detector = EndpointActivityDetector(cfg)

    tamper_evt = NormalizedEvent(
        event_id="EVT-TAMPER-01",
        timestamp=BASE_TIME,
        username="admin",
        device_id="ENDPOINT-99",
        process_name="powershell.exe",
        command_line="Set-MpPreference -DisableRealtimeMonitoring $true"
    )
    findings = detector.evaluate([tamper_evt])
    assert len(findings) == 1
    assert findings[0].rule_id == "RULE_SECURITY_CONTROL_TAMPERING"
