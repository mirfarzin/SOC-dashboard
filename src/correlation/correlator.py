"""
Event Correlation Engine for PS02.
Groups related detection findings and context events into coherent, deduplicated Incident cases
based on entity overlap (user, device, IP) and configurable temporal proximity.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
from src.schema import NormalizedEvent, DetectionFinding, Incident, SeverityLevel
from src.config import AppConfig


class UnionFind:
    """Disjoint Set Union (Union-Find) data structure for finding connected components."""
    def __init__(self, elements: List[int]):
        self.parent = {e: e for e in elements}

    def find(self, i: int) -> int:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_j] = root_i


class EventCorrelator:
    def __init__(self, config: AppConfig):
        self.config = config

    def correlate(
        self,
        events: List[NormalizedEvent],
        findings: List[DetectionFinding]
    ) -> List[Incident]:
        """
        Group findings and supporting events into unified Incident objects.
        """
        if not findings:
            return []

        cfg = self.config.correlation
        window_delta = timedelta(seconds=cfg.time_window_seconds)

        # Map event_id -> NormalizedEvent for rapid lookup
        event_map: Dict[str, NormalizedEvent] = {e.event_id: e for e in events}

        n = len(findings)
        uf = UnionFind(list(range(n)))

        # Pairwise comparison to find overlapping findings within correlation window
        for i in range(n):
            f_i = findings[i]
            entities_i = self._get_finding_entities(f_i)
            t_min_i, t_max_i = self._get_finding_time_range(f_i)

            for j in range(i + 1, n):
                f_j = findings[j]
                entities_j = self._get_finding_entities(f_j)
                t_min_j, t_max_j = self._get_finding_time_range(f_j)

                # Check entity intersection
                shared_entities = entities_i.intersection(entities_j)
                if not shared_entities:
                    continue

                # Check temporal proximity (sliding window overlap or gap <= window_delta)
                # Gap between intervals [t_min_i, t_max_i] and [t_min_j, t_max_j]
                gap = max(
                    timedelta(seconds=0),
                    max(t_min_i, t_min_j) - min(t_max_i, t_max_j)
                )

                if gap <= window_delta:
                    uf.union(i, j)

        # Group finding indices by root
        clusters: Dict[int, List[DetectionFinding]] = defaultdict(list)
        for i in range(n):
            root = uf.find(i)
            clusters[root].append(findings[i])

        incidents: List[Incident] = []
        cluster_list = list(clusters.values())

        # Sort clusters by the earliest event timestamp
        cluster_list.sort(key=lambda group: min(
            min(f.timestamps) for f in group if f.timestamps
        ))

        today_str = datetime.utcnow().strftime("%Y%m%d")

        for idx, group_findings in enumerate(cluster_list, start=1):
            inc_id = f"INC-{today_str}-{idx:04d}"

            # Collect all supporting event IDs
            participating_event_ids: Set[str] = set()
            for f in group_findings:
                participating_event_ids.update(f.supporting_event_ids)

            # Gather and sort events
            inc_events = [event_map[eid] for eid in participating_event_ids if eid in event_map]
            inc_events.sort(key=lambda e: e.timestamp)

            # Build consolidated entities
            users: Set[str] = set()
            hosts: Set[str] = set()
            ips: Set[str] = set()
            for e in inc_events:
                if e.username:
                    users.add(e.username)
                if e.target_user:
                    users.add(e.target_user)
                if e.device_id:
                    hosts.add(e.device_id)
                if e.source_ip:
                    ips.add(e.source_ip)

            # Build readable timeline
            timeline: List[Dict[str, Any]] = []
            base_time = inc_events[0].timestamp if inc_events else None
            for e in inc_events:
                offset_sec = (e.timestamp - base_time).total_seconds() if base_time else 0
                timeline.append({
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "relative_seconds": int(offset_sec),
                    "action": e.action,
                    "source": e.event_source,
                    "username": e.username,
                    "device_id": e.device_id,
                    "source_ip": e.source_ip,
                    "result": e.authentication_result.value,
                    "detail": e.privilege_change or e.command_line or e.process_name or e.action
                })

            # Formulate correlation explanation
            shared_summary = []
            if users:
                shared_summary.append(f"User(s): {', '.join(sorted(users))}")
            if hosts:
                shared_summary.append(f"Host(s): {', '.join(sorted(hosts))}")
            if ips:
                shared_summary.append(f"IP(s): {', '.join(sorted(ips))}")

            rule_names = [f.rule_name for f in group_findings]
            corr_explanation = (
                f"Correlated {len(group_findings)} suspicious detection finding(s) involving "
                f"{'; '.join(shared_summary)} spanning {len(inc_events)} event(s) across a "
                f"{(inc_events[-1].timestamp - inc_events[0].timestamp).total_seconds() / 60:.1f} minute window. "
                f"Triggered detection rules: {', '.join(rule_names)}."
            )

            # Determine Title
            title = self._generate_incident_title(group_findings, users, hosts)

            incident = Incident(
                incident_id=inc_id,
                title=title,
                event_ids=sorted(list(participating_event_ids)),
                findings=group_findings,
                entities_involved={
                    "users": sorted(list(users)),
                    "hosts": sorted(list(hosts)),
                    "ips": sorted(list(ips))
                },
                correlation_explanation=corr_explanation,
                timeline=timeline,
                created_at=datetime.utcnow()
            )
            incidents.append(incident)

        return incidents

    def _get_finding_entities(self, f: DetectionFinding) -> Set[str]:
        entities: Set[str] = set()
        for u in f.relevant_entities.get("users", []):
            if u and u.lower() not in ["system", "unknown"]:
                entities.add(f"user:{u.lower()}")
        for h in f.relevant_entities.get("hosts", []):
            if h and h.lower() not in ["unknown"]:
                entities.add(f"host:{h.lower()}")
        for ip in f.relevant_entities.get("ips", []):
            if ip and ip.lower() not in ["local", "127.0.0.1", "::1"]:
                entities.add(f"ip:{ip}")
        return entities

    def _get_finding_time_range(self, f: DetectionFinding) -> Tuple[datetime, datetime]:
        if not f.timestamps:
            now = datetime.utcnow()
            return now, now
        return min(f.timestamps), max(f.timestamps)

    def _generate_incident_title(self, findings: List[DetectionFinding], users: Set[str], hosts: Set[str]) -> str:
        rule_ids = set(f.rule_id for f in findings)
        primary_user = next(iter(users)) if users else "Unknown Identity"
        primary_host = next(iter(hosts)) if hosts else "Unknown Host"

        if "RULE_SECURITY_CONTROL_TAMPERING" in rule_ids:
            return f"Defense Evasion & Security Tampering on {primary_host} ({primary_user})"
        if "RULE_UNAUTHORIZED_PRIV_ESCALATION" in rule_ids and "RULE_BURST_FOLLOWED_BY_SUCCESS" in rule_ids:
            return f"Multi-Stage Account Compromise & Privilege Escalation ({primary_user})"
        if "RULE_UNAUTHORIZED_PRIV_ESCALATION" in rule_ids:
            return f"Unauthorized Privilege Escalation for {primary_user} on {primary_host}"
        if "RULE_BURST_FOLLOWED_BY_SUCCESS" in rule_ids:
            return f"Credential Brute-Force with Successful Breach ({primary_user})"
        if "RULE_FAILED_LOGIN_BURST" in rule_ids:
            return f"Repeated Authentication Failures targeting {primary_user}"
        if "RULE_UNUSUAL_LOGIN_HOURS" in rule_ids:
            return f"Anomalous Out-of-Hours Authentication ({primary_user})"
        if "RULE_SUSPICIOUS_PROCESS_EXECUTION" in rule_ids:
            return f"Suspicious Attack Tool Execution on {primary_host}"
        return f"Correlated Security Incident on {primary_host} ({primary_user})"
