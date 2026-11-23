"""
Log Ingestion and Schema Normalization Layer for PS02.
Supports CSV and JSON input with flexible field mapping, robust timestamp parsing,
deterministic ID generation, and full preservation of raw records.
"""

from __future__ import annotations
import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dateutil import parser as dt_parser
import zoneinfo

from src.schema import NormalizedEvent, AuthResult


# Canonical field aliases mapping diverse vendor schemas to standard schema
FIELD_ALIASES = {
    "event_id": ["event_id", "EventID", "id", "record_id", "RecordId", "log_id", "EventRecordID"],
    "timestamp": ["timestamp", "TimeCreated", "DateTime", "time", "date_time", "@timestamp", "EventTime"],
    "event_source": ["event_source", "source", "ProviderName", "LogName", "Source", "channel"],
    "event_type": ["event_type", "type", "Category", "TaskCategory", "event_category"],
    "username": ["username", "user", "UserName", "TargetUserName", "AccountName", "SubjectUserName", "user_id"],
    "device_id": ["device_id", "hostname", "ComputerName", "Computer", "host", "endpoint_id", "Workstation"],
    "source_ip": ["source_ip", "src_ip", "IpAddress", "ClientIP", "source_address", "SourceIP", "remote_ip"],
    "destination_ip": ["destination_ip", "dst_ip", "DestIP", "TargetIP", "dest_address", "DestinationIP"],
    "action": ["action", "Activity", "EventAction", "operation", "command", "task"],
    "authentication_result": ["authentication_result", "auth_result", "status", "Status", "result", "SubStatus", "LoginStatus"],
    "privilege_change": ["privilege_change", "PrivilegeList", "TargetSid", "GroupAdded", "MemberName", "privilege"],
    "target_user": ["target_user", "TargetUser", "MemberName", "AffectedUser", "SubjectUser"],
    "approval_reference": ["approval_reference", "ticket_id", "change_ticket", "jira_id", "approval_id", "ChangeId"],
    "process_name": ["process_name", "ProcessName", "NewProcessName", "Image", "process", "app_name"],
    "command_line": ["command_line", "CommandLine", "ProcessCommandLine", "arguments", "cmd"]
}


def _extract_aliased_field(record: Dict[str, Any], canonical_key: str) -> Optional[Any]:
    """Find value matching canonical key or any of its known aliases."""
    aliases = FIELD_ALIASES.get(canonical_key, [canonical_key])
    for alias in aliases:
        if alias in record and record[alias] is not None and str(record[alias]).strip() != "":
            return record[alias]
    return None


def _normalize_auth_result(val: Any) -> AuthResult:
    """Normalize vendor status strings into standard AuthResult enum."""
    if val is None:
        return AuthResult.UNKNOWN
    s = str(val).strip().upper()
    if any(k in s for k in ["SUCCESS", "OK", "0X0", "AUDIT_SUCCESS", "LOGON_SUCCESS", "PASS", "TRUE"]):
        return AuthResult.SUCCESS
    if any(k in s for k in ["FAIL", "FAILURE", "ERROR", "AUDIT_FAILURE", "0XC000006A", "0XC0000064", "BAD_PASSWORD", "DENY", "FALSE"]):
        return AuthResult.FAILURE
    if "CHALLENGE" in s or "MFA" in s:
        return AuthResult.CHALLENGE
    return AuthResult.UNKNOWN


def parse_timestamp(val: Any, default_tz: str = "Asia/Kolkata") -> datetime:
    """
    Parse timestamp string, float/int epoch, or ISO format into timezone-aware datetime.
    Defaults to configured organization timezone if naive.
    """
    tz = zoneinfo.ZoneInfo(default_tz)
    if isinstance(val, (int, float)):
        # Epoch timestamp
        dt = datetime.fromtimestamp(val, tz=timezone.utc)
        return dt.astimezone(tz)

    val_str = str(val).strip()
    try:
        dt = dt_parser.parse(val_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
        return dt
    except Exception as e:
        raise ValueError(f"Could not parse timestamp '{val_str}': {e}")


def generate_event_id(raw_record: Dict[str, Any], prefix: str = "EVT") -> str:
    """Generate a stable, deterministic event ID based on SHA-256 hash of record content."""
    serialized = json.dumps(raw_record, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def normalize_record(raw: Dict[str, Any], default_tz: str = "Asia/Kolkata") -> NormalizedEvent:
    """
    Convert a raw dictionary into a strictly validated NormalizedEvent.
    Preserves raw event completely.
    """
    # 1. Timestamp (required)
    raw_ts = _extract_aliased_field(raw, "timestamp")
    if raw_ts is None:
        raise ValueError("Missing mandatory timestamp in log record")
    ts = parse_timestamp(raw_ts, default_tz=default_tz)

    # 2. Event ID
    raw_id = _extract_aliased_field(raw, "event_id")
    event_id = str(raw_id).strip() if raw_id else generate_event_id(raw)

    # 3. Source & Type
    event_source = str(_extract_aliased_field(raw, "event_source") or "general_log").strip()
    event_type = str(_extract_aliased_field(raw, "event_type") or "activity").strip()

    # 4. Identity & Network
    username = _extract_aliased_field(raw, "username")
    username = str(username).strip() if username else None

    device_id = _extract_aliased_field(raw, "device_id")
    device_id = str(device_id).strip() if device_id else None

    source_ip = _extract_aliased_field(raw, "source_ip")
    source_ip = str(source_ip).strip() if source_ip else None

    dest_ip = _extract_aliased_field(raw, "destination_ip")
    dest_ip = str(dest_ip).strip() if dest_ip else None

    action = str(_extract_aliased_field(raw, "action") or "unknown").strip()

    # 5. Auth Result
    auth_val = _extract_aliased_field(raw, "authentication_result")
    auth_result = _normalize_auth_result(auth_val)

    # 6. Privilege & Approval
    privilege_change = _extract_aliased_field(raw, "privilege_change")
    privilege_change = str(privilege_change).strip() if privilege_change else None

    target_user = _extract_aliased_field(raw, "target_user")
    target_user = str(target_user).strip() if target_user else None

    approval_ref = _extract_aliased_field(raw, "approval_reference")
    approval_ref = str(approval_ref).strip() if approval_ref else None

    # 7. Endpoint metadata
    process_name = _extract_aliased_field(raw, "process_name")
    process_name = str(process_name).strip() if process_name else None

    command_line = _extract_aliased_field(raw, "command_line")
    command_line = str(command_line).strip() if command_line else None

    return NormalizedEvent(
        event_id=event_id,
        timestamp=ts,
        event_source=event_source,
        event_type=event_type,
        username=username,
        device_id=device_id,
        source_ip=source_ip,
        destination_ip=dest_ip,
        action=action,
        authentication_result=auth_result,
        privilege_change=privilege_change,
        target_user=target_user,
        approval_reference=approval_ref,
        process_name=process_name,
        command_line=command_line,
        raw_event=raw
    )


class IngestionResult:
    def __init__(self):
        self.events: List[NormalizedEvent] = []
        self.errors: List[Dict[str, Any]] = []

    @property
    def total_processed(self) -> int:
        return len(self.events) + len(self.errors)

    @property
    def success_rate(self) -> float:
        if not self.total_processed:
            return 1.0
        return len(self.events) / self.total_processed


def ingest_file(file_path: Path | str, default_tz: str = "Asia/Kolkata") -> IngestionResult:
    """
    Ingest a log file (CSV or JSON) and return an IngestionResult containing
    successfully normalized events and any record-level validation errors.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return ingest_json(path, default_tz=default_tz)
    elif suffix in [".csv", ".txt", ".log"]:
        return ingest_csv(path, default_tz=default_tz)
    else:
        # Attempt JSON then CSV fallback
        try:
            return ingest_json(path, default_tz=default_tz)
        except Exception:
            return ingest_csv(path, default_tz=default_tz)


def ingest_json(path: Path, default_tz: str = "Asia/Kolkata") -> IngestionResult:
    result = IngestionResult()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()

    records: List[Dict[str, Any]] = []
    # Support both JSON array and JSON Lines (NDJSON)
    if content.startswith("["):
        try:
            records = json.loads(content)
        except Exception as e:
            result.errors.append({"line": 0, "error": f"JSON Array parse error: {e}", "raw": content[:200]})
            return result
    else:
        # Try JSON Lines
        for line_no, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except Exception as e:
                result.errors.append({"line": line_no, "error": f"JSON Line parse error: {e}", "raw": line})

    for idx, raw_record in enumerate(records, start=1):
        if not isinstance(raw_record, dict):
            result.errors.append({"record_index": idx, "error": "Record is not a JSON object", "raw": raw_record})
            continue
        try:
            ev = normalize_record(raw_record, default_tz=default_tz)
            result.events.append(ev)
        except Exception as e:
            result.errors.append({"record_index": idx, "error": str(e), "raw": raw_record})

    return result


def ingest_csv(path: Path, default_tz: str = "Asia/Kolkata") -> IngestionResult:
    result = IngestionResult()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row_no, row in enumerate(reader, start=2): # start=2 accounting for header
            try:
                # Strip keys and values
                clean_row = {str(k).strip(): v.strip() if isinstance(v, str) else v for k, v in row.items() if k is not None}
                ev = normalize_record(clean_row, default_tz=default_tz)
                result.events.append(ev)
            except Exception as e:
                result.errors.append({"row_number": row_no, "error": str(e), "raw": row})

    return result
