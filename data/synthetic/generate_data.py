"""
Synthetic Security Telemetry Generator for PS02 Demonstration and Evaluation.
Generates Scenarios A, B, C, D, E with authentic field structures and ground-truth labels.
Labels synthetic data accurately; does NOT represent it as real enterprise telemetry.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
import zoneinfo

TZ = zoneinfo.ZoneInfo("Asia/Kolkata")
BASE_DATE = datetime(2026, 11, 23, tzinfo=TZ)


def generate_synthetic_dataset(output_dir: Path | str = None):
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    auth_records = []
    endpoint_records = []
    ground_truth = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "description": "Synthetic benchmark security dataset for PS02 evaluation (Scenarios A through E).",
        "scenarios": {}
    }

    # =========================================================================
    # SCENARIO A: Repeated Failed Logins (Brute-Force / Credential Spray)
    # Target: user 'finance_user' from IP 198.51.100.44 on workstation 'WS-FIN-02'
    # 6 rapid failed attempts between 11:00:00 and 11:02:30 IST. No success.
    # Expected: RULE_FAILED_LOGIN_BURST, Medium Severity.
    # =========================================================================
    scenario_a_events = []
    t_a = BASE_DATE.replace(hour=11, minute=0, second=0)
    for i in range(6):
        evt_time = t_a + timedelta(seconds=i * 25)
        eid = f"EVT-SCEN-A-{i+1:03d}"
        rec = {
            "event_id": eid,
            "timestamp": evt_time.isoformat(),
            "event_source": "auth_service",
            "event_type": "authentication",
            "username": "finance_user",
            "device_id": "WS-FIN-02",
            "source_ip": "198.51.100.44",
            "destination_ip": "10.0.1.15",
            "action": "user_logon",
            "authentication_result": "FAILURE",
            "privilege_change": None,
            "approval_reference": None
        }
        auth_records.append(rec)
        scenario_a_events.append(eid)

    ground_truth["scenarios"]["Scenario_A"] = {
        "title": "Repeated Failed Logins (Credential Burst)",
        "entity": "finance_user",
        "expected_rules": ["RULE_FAILED_LOGIN_BURST"],
        "expected_severity": "Medium",
        "event_ids": scenario_a_events
    }

    # =========================================================================
    # SCENARIO B: Successful Out-of-Hours Login (Deep Night)
    # Target: user 'dba_admin' from IP 203.0.113.88 on server 'SQL-PROD-01'
    # Login at 02:45:10 AM IST (Sunday deep night).
    # Expected: RULE_UNUSUAL_LOGIN_HOURS, Low/Medium Severity.
    # =========================================================================
    t_b = BASE_DATE.replace(hour=2, minute=45, second=10)
    eid_b = "EVT-SCEN-B-001"
    rec_b = {
        "event_id": eid_b,
        "timestamp": t_b.isoformat(),
        "event_source": "active_directory",
        "event_type": "logon",
        "username": "dba_admin",
        "device_id": "SQL-PROD-01",
        "source_ip": "203.0.113.88",
        "destination_ip": "10.0.2.50",
        "action": "kerberos_preauth",
        "authentication_result": "SUCCESS",
        "privilege_change": None,
        "approval_reference": None
    }
    auth_records.append(rec_b)

    ground_truth["scenarios"]["Scenario_B"] = {
        "title": "Successful Out-of-Hours Login",
        "entity": "dba_admin",
        "expected_rules": ["RULE_UNUSUAL_LOGIN_HOURS"],
        "expected_severity": "Medium",
        "event_ids": [eid_b]
    }

    # =========================================================================
    # SCENARIO C: Privilege Escalation Without Approval
    # Target: user 'intern_guest' added to group 'Administrators' by 'shadow_svc'
    # On DC-01 at 14:20:00 IST. Missing change ticket.
    # Expected: RULE_UNAUTHORIZED_PRIV_ESCALATION, High Severity.
    # =========================================================================
    t_c = BASE_DATE.replace(hour=14, minute=20, second=0)
    eid_c = "EVT-SCEN-C-001"
    rec_c = {
        "event_id": eid_c,
        "timestamp": t_c.isoformat(),
        "event_source": "active_directory",
        "event_type": "group_modification",
        "username": "shadow_svc",
        "target_user": "intern_guest",
        "device_id": "DC-PRIMARY-01",
        "source_ip": "10.0.0.100",
        "action": "member_added_to_security_group",
        "authentication_result": "SUCCESS",
        "privilege_change": "Administrators",
        "approval_reference": None
    }
    auth_records.append(rec_c)

    ground_truth["scenarios"]["Scenario_C"] = {
        "title": "Unapproved Privilege Escalation",
        "entity": "intern_guest",
        "expected_rules": ["RULE_UNAUTHORIZED_PRIV_ESCALATION"],
        "expected_severity": "High",
        "event_ids": [eid_c]
    }

    # =========================================================================
    # SCENARIO D: Correlated Multi-Stage Incident (APT Attack Chain)
    # Entity: 'target_admin' on host 'CRITICAL-DC-01' from IP 185.220.101.5
    # Sequence starting 03:15:00 AM IST:
    # 1. 5 rapid failed logins (03:15:00 - 03:17:00)
    # 2. Successful logon at 03:17:40
    # 3. Security control disabled (Set-MpPreference -DisableRealtimeMonitoring $true)
    # 4. Privilege escalation: added to 'Domain Admins' without ticket
    # 5. Attack tool execution: mimikatz.exe sekurlsa::logonpasswords
    # Expected: Multi-Stage Correlation, Critical Severity (Score > 85).
    # =========================================================================
    scenario_d_events = []
    t_d = BASE_DATE.replace(hour=3, minute=15, second=0)

    # 1. Failed burst (5 events)
    for i in range(5):
        evt_t = t_d + timedelta(seconds=i * 20)
        eid = f"EVT-SCEN-D-FAIL-{i+1:03d}"
        auth_records.append({
            "event_id": eid,
            "timestamp": evt_t.isoformat(),
            "event_source": "auth_service",
            "event_type": "authentication",
            "username": "target_admin",
            "device_id": "CRITICAL-DC-01",
            "source_ip": "185.220.101.5",
            "action": "user_logon",
            "authentication_result": "FAILURE",
            "privilege_change": None,
            "approval_reference": None
        })
        scenario_d_events.append(eid)

    # 2. Successful logon following burst
    t_d_succ = t_d + timedelta(seconds=160)
    eid_d_succ = "EVT-SCEN-D-SUCC-001"
    auth_records.append({
        "event_id": eid_d_succ,
        "timestamp": t_d_succ.isoformat(),
        "event_source": "auth_service",
        "event_type": "authentication",
        "username": "target_admin",
        "device_id": "CRITICAL-DC-01",
        "source_ip": "185.220.101.5",
        "action": "user_logon",
        "authentication_result": "SUCCESS",
        "privilege_change": None,
        "approval_reference": None
    })
    scenario_d_events.append(eid_d_succ)

    # 3. Security control tampering (endpoint log)
    t_d_tamper = t_d + timedelta(seconds=220)
    eid_d_tamper = "EVT-SCEN-D-ENDP-001"
    endpoint_records.append({
        "event_id": eid_d_tamper,
        "timestamp": t_d_tamper.isoformat(),
        "event_source": "endpoint_edr",
        "event_type": "defense_evasion",
        "username": "target_admin",
        "device_id": "CRITICAL-DC-01",
        "process_name": "powershell.exe",
        "command_line": "powershell.exe -Command Set-MpPreference -DisableRealtimeMonitoring $true",
        "action": "service_tamper",
        "authentication_result": "SUCCESS"
    })
    scenario_d_events.append(eid_d_tamper)

    # 4. Privilege escalation without ticket
    t_d_priv = t_d + timedelta(seconds=300)
    eid_d_priv = "EVT-SCEN-D-PRIV-001"
    auth_records.append({
        "event_id": eid_d_priv,
        "timestamp": t_d_priv.isoformat(),
        "event_source": "active_directory",
        "event_type": "group_modification",
        "username": "target_admin",
        "target_user": "target_admin",
        "device_id": "CRITICAL-DC-01",
        "action": "member_added_to_security_group",
        "privilege_change": "Domain Admins",
        "approval_reference": None,
        "authentication_result": "SUCCESS"
    })
    scenario_d_events.append(eid_d_priv)

    # 5. Suspicious utility execution
    t_d_tool = t_d + timedelta(seconds=360)
    eid_d_tool = "EVT-SCEN-D-ENDP-002"
    endpoint_records.append({
        "event_id": eid_d_tool,
        "timestamp": t_d_tool.isoformat(),
        "event_source": "endpoint_edr",
        "event_type": "process_execution",
        "username": "target_admin",
        "device_id": "CRITICAL-DC-01",
        "process_name": "mimikatz.exe",
        "command_line": "mimikatz.exe sekurlsa::logonpasswords exit",
        "action": "process_start",
        "authentication_result": "SUCCESS"
    })
    scenario_d_events.append(eid_d_tool)

    ground_truth["scenarios"]["Scenario_D"] = {
        "title": "Correlated Multi-Stage APT Attack Chain",
        "entity": "target_admin",
        "expected_rules": [
            "RULE_BURST_FOLLOWED_BY_SUCCESS",
            "RULE_UNUSUAL_LOGIN_HOURS",
            "RULE_SECURITY_CONTROL_TAMPERING",
            "RULE_UNAUTHORIZED_PRIV_ESCALATION",
            "RULE_SUSPICIOUS_PROCESS_EXECUTION"
        ],
        "expected_severity": "Critical",
        "event_ids": scenario_d_events
    }

    # =========================================================================
    # SCENARIO E: Benign Activity (Normal business day & approved maintenance)
    # Legitimate daytime login at 10:30 AM IST by 'analyst_alice'
    # Approved change ticket 'CHG-8041' adding service account 'svc_backup'
    # Expected: Low or Informational severity. No false alarms.
    # =========================================================================
    scenario_e_events = []
    t_e = BASE_DATE.replace(hour=10, minute=30, second=0)

    # Normal login
    eid_e1 = "EVT-SCEN-E-001"
    auth_records.append({
        "event_id": eid_e1,
        "timestamp": t_e.isoformat(),
        "event_source": "auth_service",
        "event_type": "authentication",
        "username": "analyst_alice",
        "device_id": "WS-SEC-01",
        "source_ip": "10.0.5.12",
        "action": "user_logon",
        "authentication_result": "SUCCESS",
        "privilege_change": None,
        "approval_reference": None
    })
    scenario_e_events.append(eid_e1)

    # Authorized privilege change
    eid_e2 = "EVT-SCEN-E-002"
    auth_records.append({
        "event_id": eid_e2,
        "timestamp": (t_e + timedelta(minutes=5)).isoformat(),
        "event_source": "active_directory",
        "event_type": "group_modification",
        "username": "analyst_alice",
        "target_user": "svc_backup",
        "device_id": "WS-SEC-01",
        "action": "member_added_to_security_group",
        "privilege_change": "SecurityAdmins",
        "approval_reference": "CHG-8041",
        "authentication_result": "SUCCESS"
    })
    scenario_e_events.append(eid_e2)

    # Normal endpoint activity
    eid_e3 = "EVT-SCEN-E-003"
    endpoint_records.append({
        "event_id": eid_e3,
        "timestamp": (t_e + timedelta(minutes=8)).isoformat(),
        "event_source": "endpoint_edr",
        "event_type": "process_execution",
        "username": "analyst_alice",
        "device_id": "WS-SEC-01",
        "process_name": "notepad.exe",
        "command_line": "notepad.exe C:\\Users\\analyst_alice\\notes.txt",
        "action": "process_start",
        "authentication_result": "SUCCESS"
    })
    scenario_e_events.append(eid_e3)

    ground_truth["scenarios"]["Scenario_E"] = {
        "title": "Benign Daytime Operations & Approved Maintenance",
        "entity": "analyst_alice",
        "expected_rules": ["RULE_AUTHORIZED_PRIV_ESCALATION"],
        "expected_severity": "Low",
        "event_ids": scenario_e_events
    }

    # Write files: auth_logs.csv, auth_logs.json, endpoint_logs.csv, endpoint_logs.json, ground_truth.json
    # 1. auth_logs.json
    with open(output_dir / "auth_logs.json", "w", encoding="utf-8") as f:
        json.dump(auth_records, f, indent=2)

    # 2. auth_logs.csv
    auth_fields = [
        "event_id", "timestamp", "event_source", "event_type", "username", "target_user",
        "device_id", "source_ip", "destination_ip", "action", "authentication_result",
        "privilege_change", "approval_reference"
    ]
    with open(output_dir / "auth_logs.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=auth_fields)
        writer.writeheader()
        writer.writerows(auth_records)

    # 3. endpoint_logs.json
    with open(output_dir / "endpoint_logs.json", "w", encoding="utf-8") as f:
        json.dump(endpoint_records, f, indent=2)

    # 4. endpoint_logs.csv
    endpoint_fields = [
        "event_id", "timestamp", "event_source", "event_type", "username", "device_id",
        "process_name", "command_line", "action", "authentication_result"
    ]
    with open(output_dir / "endpoint_logs.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=endpoint_fields)
        writer.writeheader()
        writer.writerows(endpoint_records)

    # 5. ground_truth.json
    with open(output_dir / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    print(f"Generated synthetic telemetry successfully in {output_dir}:")
    print(f"- {len(auth_records)} authentication logs (auth_logs.csv, auth_logs.json)")
    print(f"- {len(endpoint_records)} endpoint logs (endpoint_logs.csv, endpoint_logs.json)")
    print(f"- Ground-truth labels with 5 scenarios (ground_truth.json)")


if __name__ == "__main__":
    generate_synthetic_dataset()
