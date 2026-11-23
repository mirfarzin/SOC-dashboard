"""
Automated tests for Event Correlation and Deterministic Severity Engine.
"""

from datetime import datetime, timedelta
import zoneinfo
import pytest

from src.config import load_config
from src.schema import NormalizedEvent, DetectionFinding, AuthResult, SeverityLevel
from src.correlation.correlator import EventCorrelator
from src.severity.classifier import SeverityClassifier

TZ = zoneinfo.ZoneInfo("Asia/Kolkata")
BASE_TIME = datetime(2026, 11, 23, 12, 0, 0, tzinfo=TZ)


def test_event_correlation_and_timeline():
    cfg = load_config()
    correlator = EventCorrelator(cfg)

    e1 = NormalizedEvent(
        event_id="EVT-1",
        timestamp=BASE_TIME,
        username="john_doe",
        device_id="WS-CORR",
        action="logon_fail",
        authentication_result=AuthResult.FAILURE
    )
    e2 = NormalizedEvent(
        event_id="EVT-2",
        timestamp=BASE_TIME + timedelta(minutes=5),
        username="john_doe",
        device_id="WS-CORR",
        action="logon_success",
        authentication_result=AuthResult.SUCCESS
    )

    f1 = DetectionFinding(
        rule_id="RULE_FAILED_LOGIN_BURST",
        rule_name="Failed Login Burst",
        description="Burst",
        severity_contribution=45,
        supporting_event_ids=["EVT-1"],
        timestamps=[e1.timestamp],
        relevant_entities={"users": ["john_doe"], "hosts": ["WS-CORR"], "ips": []},
        explanation="Test finding 1"
    )
    f2 = DetectionFinding(
        rule_id="RULE_BURST_FOLLOWED_BY_SUCCESS",
        rule_name="Burst Followed by Success",
        description="Breach",
        severity_contribution=65,
        supporting_event_ids=["EVT-2"],
        timestamps=[e2.timestamp],
        relevant_entities={"users": ["john_doe"], "hosts": ["WS-CORR"], "ips": []},
        explanation="Test finding 2"
    )

    incidents = correlator.correlate([e1, e2], [f1, f2])
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.entities_involved["users"] == ["john_doe"]
    assert inc.entities_involved["hosts"] == ["WS-CORR"]
    assert len(inc.timeline) == 2
    assert inc.timeline[0]["event_id"] == "EVT-1"
    assert inc.timeline[1]["event_id"] == "EVT-2"


def test_deterministic_severity_classification_and_synergy():
    cfg = load_config()
    classifier = SeverityClassifier(cfg)
    correlator = EventCorrelator(cfg)

    e1 = NormalizedEvent(event_id="E-1", timestamp=BASE_TIME, username="victim")
    f_cred = DetectionFinding(
        rule_id="RULE_BURST_FOLLOWED_BY_SUCCESS",
        rule_name="Credential Burst",
        description="Breach",
        severity_contribution=65,
        supporting_event_ids=["E-1"],
        timestamps=[BASE_TIME],
        relevant_entities={"users": ["victim"]},
        explanation="Credential compromise"
    )
    f_priv = DetectionFinding(
        rule_id="RULE_UNAUTHORIZED_PRIV_ESCALATION",
        rule_name="Unapproved Priv Escalation",
        description="Priv escalation",
        severity_contribution=75,
        supporting_event_ids=["E-1"],
        timestamps=[BASE_TIME],
        relevant_entities={"users": ["victim"]},
        explanation="Unapproved privilege change"
    )

    inc = correlator.correlate([e1], [f_cred, f_priv])[0]
    classified = classifier.classify(inc)

    # Multi-stage attack synergy bonus (+25) elevates to Critical (Score 100/100)
    assert classified.severity == SeverityLevel.CRITICAL
    assert classified.severity_score >= 85
    assert any("Multi-Stage Synergy Bonus" in line for line in classified.severity_breakdown)
