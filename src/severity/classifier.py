"""
Deterministic Severity Classification Engine for PS02.
Computes transparent, auditable severity levels using multi-factor risk scoring,
attack chain synergies, and evidence-backed rationale.
The SLM never assigns authoritative severity; this deterministic engine is the sole source of truth.
"""

from typing import List, Tuple
from src.schema import Incident, SeverityLevel, DetectionFinding
from src.config import AppConfig


class SeverityClassifier:
    def __init__(self, config: AppConfig):
        self.config = config

    def classify(self, incident: Incident) -> Incident:
        """
        Compute authoritative severity level and detailed breakdown for an incident.
        Returns the updated Incident object with severity, score, and breakdown populated.
        """
        findings = incident.findings
        if not findings:
            incident.severity = SeverityLevel.INFORMATIONAL
            incident.severity_score = 0
            incident.severity_breakdown = ["No suspicious findings detected in group."]
            return incident

        rule_ids = set(f.rule_id for f in findings)
        breakdown: List[str] = []

        # 1. Base Score from findings
        finding_scores = [f.severity_contribution for f in findings]
        max_base = max(finding_scores) if finding_scores else 0
        primary_finding = max(findings, key=lambda f: f.severity_contribution)

        score = float(max_base)
        breakdown.append(
            f"Base severity anchor: {primary_finding.rule_name} (Rule: {primary_finding.rule_id}, Contribution: +{max_base})"
        )

        # Additional non-primary distinct findings add incremental weight
        additional_findings = [f for f in findings if f != primary_finding]
        distinct_extra_rules = set()
        for af in additional_findings:
            if af.rule_id not in distinct_extra_rules:
                distinct_extra_rules.add(af.rule_id)
                increment = min(15, int(af.severity_contribution * 0.25))
                score += increment
                breakdown.append(f"Distinct rule overlap: {af.rule_name} (+{increment})")

        # 2. Multi-Stage Attack Synergies (Compound Threat Intelligence)
        synergies_added = False

        # Synergy 1: Credential Access followed by Unauthorized Privilege Escalation
        has_credential_burst = any(r in rule_ids for r in ["RULE_BURST_FOLLOWED_BY_SUCCESS", "RULE_FAILED_LOGIN_BURST"])
        has_unauth_priv = "RULE_UNAUTHORIZED_PRIV_ESCALATION" in rule_ids

        if has_credential_burst and has_unauth_priv:
            synergy_bonus = 25
            score += synergy_bonus
            breakdown.append(
                f"Multi-Stage Synergy Bonus: Credential compromise chained with unapproved privilege escalation (+{synergy_bonus})"
            )
            synergies_added = True

        # Synergy 2: Out of Hours + Unauthorized Privilege Escalation
        has_unusual_hours = "RULE_UNUSUAL_LOGIN_HOURS" in rule_ids
        if has_unusual_hours and has_unauth_priv:
            synergy_bonus = 15
            score += synergy_bonus
            breakdown.append(
                f"Stealth Synergy Bonus: Off-hours authentication combined with unapproved privilege escalation (+{synergy_bonus})"
            )
            synergies_added = True

        # Synergy 3: Security Control Tampering / Defense Evasion
        has_tampering = "RULE_SECURITY_CONTROL_TAMPERING" in rule_ids
        if has_tampering:
            synergy_bonus = 20
            score += synergy_bonus
            breakdown.append(
                f"Defense Evasion Critical Override: Tampering with EDR or security controls detected (+{synergy_bonus})"
            )
            synergies_added = True

        # 3. Mitigation / Authorization Dampeners
        all_authorized = all(f.is_authorized for f in findings)
        if all_authorized and not has_tampering and not has_credential_burst:
            score = min(score, 25.0)
            breakdown.append("Authorization Mitigation: All flagged changes possess valid change ticket metadata (-dampened)")

        # Cap score between 0 and 100
        final_score = int(max(0, min(100, round(score))))

        # 4. Map to Severity Level
        thresholds = self.config.severity.thresholds
        if final_score >= thresholds.critical:
            level = SeverityLevel.CRITICAL
        elif final_score >= thresholds.high:
            level = SeverityLevel.HIGH
        elif final_score >= thresholds.medium:
            level = SeverityLevel.MEDIUM
        elif final_score >= thresholds.low:
            level = SeverityLevel.LOW
        else:
            level = SeverityLevel.INFORMATIONAL

        breakdown.append(
            f"Final Deterministic Score: {final_score}/100 -> Classified as {level.value.upper()} "
            f"(Thresholds: Critical>={thresholds.critical}, High>={thresholds.high}, Medium>={thresholds.medium}, Low>={thresholds.low})"
        )

        incident.severity = level
        incident.severity_score = final_score
        incident.severity_breakdown = breakdown
        return incident
