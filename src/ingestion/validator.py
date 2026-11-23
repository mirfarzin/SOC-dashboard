"""
Ingestion Validation and Diagnostics Layer for PS02.
Summarizes ingested telemetry, checks data completeness, and flags ingestion health.
"""

from typing import Dict, List, Any
from src.schema import NormalizedEvent


class IngestionDiagnostics:
    @staticmethod
    def audit_events(events: List[NormalizedEvent], errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive diagnostic summary of imported logs."""
        total = len(events)
        users = set(e.username for e in events if e.username)
        hosts = set(e.device_id for e in events if e.device_id)
        ips = set(e.source_ip for e in events if e.source_ip)
        sources = set(e.event_source for e in events if e.event_source)

        auth_failures = sum(1 for e in events if e.authentication_result.value == "FAILURE")
        auth_successes = sum(1 for e in events if e.authentication_result.value == "SUCCESS")
        priv_events = sum(1 for e in events if e.privilege_change)

        min_ts = min((e.timestamp for e in events), default=None)
        max_ts = max((e.timestamp for e in events), default=None)

        return {
            "total_valid_events": total,
            "total_errors": len(errors),
            "unique_users_count": len(users),
            "unique_hosts_count": len(hosts),
            "unique_source_ips_count": len(ips),
            "log_sources": sorted(list(sources)),
            "auth_summary": {
                "successes": auth_successes,
                "failures": auth_failures,
            },
            "privilege_changes_count": priv_events,
            "time_range": {
                "start": min_ts.isoformat() if min_ts else None,
                "end": max_ts.isoformat() if max_ts else None,
                "duration_minutes": round((max_ts - min_ts).total_seconds() / 60, 2) if min_ts and max_ts else 0
            },
            "error_sample": errors[:5] if errors else []
        }
