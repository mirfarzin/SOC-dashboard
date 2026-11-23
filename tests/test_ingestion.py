"""
Automated tests for Log Ingestion, Schema Normalization, and Timestamp Handling.
"""

import json
from datetime import datetime
from pathlib import Path
import pytest
import zoneinfo

from src.ingestion.parser import (
    normalize_record,
    parse_timestamp,
    generate_event_id,
    ingest_file
)
from src.schema import AuthResult, NormalizedEvent


def test_timestamp_parsing_iso_and_epoch():
    tz = "Asia/Kolkata"
    # ISO string with UTC Z
    dt1 = parse_timestamp("2026-11-23T10:00:00Z", default_tz=tz)
    assert dt1.hour == 15  # 10 UTC is 15:30 IST
    assert dt1.minute == 30

    # Naive ISO string
    dt2 = parse_timestamp("2026-11-23 11:45:00", default_tz=tz)
    assert dt2.hour == 11
    assert dt2.minute == 45
    assert str(dt2.tzinfo) == "Asia/Kolkata"

    # Unix epoch
    epoch_val = 1732356000
    dt3 = parse_timestamp(epoch_val, default_tz=tz)
    assert dt3.tzinfo is not None


def test_deterministic_id_generation():
    rec = {"username": "alice", "action": "login", "timestamp": "2026-11-23T10:00:00"}
    id1 = generate_event_id(rec)
    id2 = generate_event_id(rec)
    assert id1 == id2
    assert id1.startswith("EVT-")


def test_normalize_record_field_aliases_and_raw_preservation():
    raw = {
        "TimeCreated": "2026-11-23 14:00:00",
        "TargetUserName": "admin_bob",
        "ComputerName": "DC-ALPHA",
        "IpAddress": "192.168.1.105",
        "Status": "0x0",  # Windows success
        "Activity": "Logon",
        "CustomField": "ShouldBePreservedInRaw"
    }
    evt = normalize_record(raw, default_tz="Asia/Kolkata")
    assert evt.username == "admin_bob"
    assert evt.device_id == "DC-ALPHA"
    assert evt.source_ip == "192.168.1.105"
    assert evt.authentication_result == AuthResult.SUCCESS
    assert evt.action == "Logon"
    assert evt.raw_event["CustomField"] == "ShouldBePreservedInRaw"


def test_ingest_synthetic_files():
    base = Path(__file__).resolve().parent.parent / "data" / "synthetic"
    auth_csv = base / "auth_logs.csv"
    auth_json = base / "auth_logs.json"

    res_csv = ingest_file(auth_csv)
    res_json = ingest_file(auth_json)

    assert len(res_csv.events) == 17
    assert len(res_csv.errors) == 0
    assert len(res_json.events) == 17
    assert len(res_json.errors) == 0
