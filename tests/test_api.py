"""
Integration tests for PS02 FastAPI Backend.
Verifies all REST endpoints: health, dashboard, demo loading, ingestion, triage,
incidents, deep-dive exports, evaluation benchmarks, and configuration.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_health():
    """Verify system health, offline operation assertion, and participant identity."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "OFFLINE" in data["operating_mode"]
    assert data["usn"] == "1MS24CI073"
    assert data["participant"] == "Mir Farzin Hussain"
    assert "SmolLM2-135M-Instruct" in data["model_name"]


def test_static_frontend_serving():
    """Verify FastAPI serves the compiled React Single Page Application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "<!doctype html>" in response.text.lower()
    assert "PS02 SOC Assistant" in response.text


def test_api_config():
    """Verify configuration parameters exposure."""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["organization"]["working_hours"]["start_hour"] == 9
    assert data["organization"]["working_hours"]["end_hour"] == 18
    assert data["slm"]["offline_mode"] is True
    assert data["severity"]["thresholds"]["critical"] == 85
    assert data["severity"]["thresholds"]["high"] == 65


def test_demo_load_and_dashboard():
    """Verify synthetic scenario loading and SOC dashboard metrics."""
    # 1. Load demo dataset
    load_resp = client.post("/api/demo/load")
    assert load_resp.status_code == 200
    load_data = load_resp.json()
    assert load_data["total_events"] >= 20
    assert load_data["total_incidents"] >= 5

    # 2. Check dashboard metrics
    dash_resp = client.get("/api/dashboard")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_events"] == load_data["total_events"]
    assert dash_data["total_incidents"] == load_data["total_incidents"]
    assert "Critical" in dash_data["severity_distribution"]
    assert len(dash_data["recent_incidents"]) >= 5


def test_incidents_list_and_detail():
    """Verify incident roster and deep-dive incident retrieval."""
    client.post("/api/demo/load")

    incidents_resp = client.get("/api/incidents")
    assert incidents_resp.status_code == 200
    incidents = incidents_resp.json()
    assert len(incidents) >= 5

    first_incident = incidents[0]
    inc_id = first_incident["incident_id"]
    assert inc_id.startswith("INC-")

    detail_resp = client.get(f"/api/incidents/{inc_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["incident"]["incident_id"] == inc_id
    assert "timeline" in detail["incident"]
    assert len(detail["incident"]["timeline"]) > 0
    assert "slm_analysis" in detail
    assert detail["slm_analysis"]["executive_summary"] != ""
    assert isinstance(detail["slm_analysis"]["facts"], list)
    assert isinstance(detail["slm_analysis"]["recommended_actions"], list)


def test_incident_not_found():
    """Verify 404 response for unknown incident ID."""
    response = client.get("/api/incidents/INC-NONEXISTENT-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_incident_exports():
    """Verify multi-format report exports (Markdown, JSON, PDF)."""
    client.post("/api/demo/load")
    incidents = client.get("/api/incidents").json()
    inc_id = incidents[0]["incident_id"]

    # Export Markdown
    md_resp = client.get(f"/api/incidents/{inc_id}/export?format=markdown")
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert f"# Incident Triage Report: {inc_id}" in md_resp.text

    # Export JSON
    json_resp = client.get(f"/api/incidents/{inc_id}/export?format=json")
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers["content-type"]
    assert json_resp.json()["incident"]["incident_id"] == inc_id

    # Export PDF
    pdf_resp = client.get(f"/api/incidents/{inc_id}/export?format=pdf")
    assert pdf_resp.status_code == 200
    assert "application/pdf" in pdf_resp.headers["content-type"]
    assert pdf_resp.content.startswith(b"%PDF")


def test_evaluation_benchmark():
    """Verify 100% precision, 100% recall benchmark endpoint."""
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    metrics = data["metrics"]
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["false_positive_rate"] == 0.0
    assert len(data["scenarios_evaluation"]) == 5


def test_ingest_and_triage_pipeline():
    """Verify raw log multipart file upload ingestion and manual triage triggering."""
    raw_auth_csv = (
        b"event_id,timestamp,user,device,ip,action,status\n"
        b"EVT-T1,2026-11-23T23:10:00Z,eve_test,WS-TEST,192.168.1.50,LOGON,FAILURE\n"
        b"EVT-T2,2026-11-23T23:11:00Z,eve_test,WS-TEST,192.168.1.50,LOGON,FAILURE\n"
        b"EVT-T3,2026-11-23T23:12:00Z,eve_test,WS-TEST,192.168.1.50,LOGON,FAILURE\n"
        b"EVT-T4,2026-11-23T23:13:00Z,eve_test,WS-TEST,192.168.1.50,LOGON,SUCCESS\n"
    )

    files = {
        "auth_file": ("test_auth.csv", raw_auth_csv, "text/csv")
    }

    ingest_resp = client.post("/api/ingest", files=files, data={"mode": "fast"})
    assert ingest_resp.status_code == 200
    ingest_data = ingest_resp.json()
    assert ingest_data["status"] == "success"
    assert ingest_data["dashboard"]["total_events"] == 4
    assert ingest_data["dashboard"]["total_incidents"] >= 1

    # Trigger manual triage
    triage_resp = client.post("/api/triage", json={"mode": "fast"})
    assert triage_resp.status_code == 200
    triage_data = triage_resp.json()
    assert triage_data["status"] == "success"
    assert triage_data["dashboard"]["total_incidents"] >= 1
