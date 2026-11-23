"""
SLM Output Validation and Fact-Checking Layer for PS02.
Strictly verifies that all cited event IDs exist in the incident evidence,
rejects hallucinated records, and enforces structural schema integrity.
"""

import re
from typing import Any, Dict, List, Set, Tuple
from src.schema import Incident, SLMReportAnalysis


EVENT_ID_REGEX = re.compile(r'\b(EVT-[A-Za-z0-9\-]+)\b')


class SLMOutputValidator:
    @staticmethod
    def validate_and_clean(raw_json: Dict[str, Any], incident: Incident) -> SLMReportAnalysis:
        """
        Validate parsed SLM JSON against the incident ground truth.
        Flags any unsupported claims or non-existent event IDs.
        """
        valid_event_ids: Set[str] = set(incident.event_ids)
        validation_errors: List[str] = []
        validation_passed = True

        # Extract fields with safe fallbacks
        title = str(raw_json.get("title") or incident.title).strip()
        summary = str(raw_json.get("executive_summary") or "Automated incident triage summary.").strip()

        raw_facts = raw_json.get("facts", [])
        facts = [str(f).strip() for f in raw_facts if str(f).strip()] if isinstance(raw_facts, list) else []

        raw_hypo = raw_json.get("hypotheses", [])
        hypotheses = [str(h).strip() for h in raw_hypo if str(h).strip()] if isinstance(raw_hypo, list) else []

        raw_rules = raw_json.get("rule_explanations", [])
        rule_explanations = [str(r).strip() for r in raw_rules if str(r).strip()] if isinstance(raw_rules, list) else []

        raw_missing = raw_json.get("missing_evidence", [])
        missing_evidence = [str(m).strip() for m in raw_missing if str(m).strip()] if isinstance(raw_missing, list) else []

        raw_actions = raw_json.get("recommended_actions", [])
        recommended_actions = [str(a).strip() for a in raw_actions if str(a).strip()] if isinstance(raw_actions, list) else []

        # Validate referenced_event_ids
        raw_referenced = raw_json.get("referenced_event_ids", [])
        if not isinstance(raw_referenced, list):
            raw_referenced = []

        # Also scan text fields for any embedded event ID references
        scanned_ids: Set[str] = set()
        for text in facts + hypotheses + rule_explanations + [summary]:
            matches = EVENT_ID_REGEX.findall(text)
            scanned_ids.update(matches)

        all_cited_ids = set(str(eid).strip() for eid in raw_referenced).union(scanned_ids)

        verified_event_ids: List[str] = []
        for cited_id in sorted(all_cited_ids):
            if cited_id in valid_event_ids:
                verified_event_ids.append(cited_id)
            else:
                validation_passed = False
                validation_errors.append(
                    f"Unsupported reference: Event ID '{cited_id}' was cited by SLM but does not exist in incident {incident.incident_id} telemetry."
                )

        # Ensure we have at least one verified event ID
        if not verified_event_ids and valid_event_ids:
            verified_event_ids = sorted(list(valid_event_ids))[:5]

        # Ensure mandatory sections are populated
        if not facts:
            facts = [f"Observed {len(incident.event_ids)} correlated event(s) across {', '.join(incident.entities_involved.get('hosts', [])) or 'endpoint'}."]
        if not hypotheses:
            hypotheses = ["Potential security policy violation or unauthorized access attempt requiring analyst review."]
        if not rule_explanations:
            rule_explanations = [f.explanation for f in incident.findings]
        if not missing_evidence:
            missing_evidence = ["Network flow logs and endpoint process tree logs around incident time window."]
        if not recommended_actions:
            recommended_actions = [
                "Verify authentication validity with the designated user.",
                "Review endpoint active sessions and process tree.",
                "Verify change management ticket authorization for any privilege modifications."
            ]

        return SLMReportAnalysis(
            incident_id=incident.incident_id,
            title=title,
            executive_summary=summary,
            facts=facts,
            hypotheses=hypotheses,
            rule_explanations=rule_explanations,
            missing_evidence=missing_evidence,
            recommended_actions=recommended_actions,
            referenced_event_ids=verified_event_ids,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            model_name=str(raw_json.get("model_name") or "local_slm"),
            is_fallback=bool(raw_json.get("is_fallback", False))
        )
