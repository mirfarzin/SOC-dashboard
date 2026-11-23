"""
FastAPI Route Handlers for PS02 SOC Dashboard.
"""

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse

from src.api.schemas.api_schemas import (
    DashboardResponse,
    HealthResponse,
    IncidentListItemSchema,
    IngestResponse,
    TriageRequest,
    TriageResponse,
)
from src.api.services.triage_service import TriageService

router = APIRouter(prefix="/api", tags=["SOC Triage API"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Health status and offline operational readiness."""
    service = TriageService.get_instance()
    has_model = service.get_dashboard_summary()["model_status"]["cached"]
    return HealthResponse(
        status="healthy",
        system="PS02 Offline Security Incident Triage Assistant",
        participant="Mir Farzin Hussain",
        usn="1MS24CI073",
        track="PS02 - Cybersecurity | Small Language Models",
        operating_mode="100% OFFLINE (Air-Gapped)",
        model_cached=has_model,
        model_name=service.config.slm.model_id,
        version="2.0.0 (React + FastAPI)"
    )


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard():
    """High-level summary metrics, severity distributions, and active incidents."""
    service = TriageService.get_instance()
    return service.get_dashboard_summary()


@router.post("/demo/load", response_model=DashboardResponse)
def load_demo():
    """Reload synthetic evaluation dataset (Scenarios A through E)."""
    service = TriageService.get_instance()
    return service.load_demo_dataset()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_logs(
    auth_file: Optional[UploadFile] = File(None),
    endpoint_file: Optional[UploadFile] = File(None),
    mode: str = Form("fast")
):
    """
    Upload and parse authentication and/or endpoint logs (CSV or JSON).
    Executes detection, correlation, severity scoring, and SLM report generation.
    """
    service = TriageService.get_instance()

    auth_bytes = await auth_file.read() if auth_file else None
    auth_name = auth_file.filename if auth_file else None

    endp_bytes = await endpoint_file.read() if endpoint_file else None
    endp_name = endpoint_file.filename if endpoint_file else None

    if not auth_bytes and not endp_bytes:
        raise HTTPException(status_code=400, detail="Please upload at least one log file (Authentication or Endpoint).")

    try:
        summary = service.ingest_logs(
            auth_content=auth_bytes,
            auth_filename=auth_name,
            endpoint_content=endp_bytes,
            endpoint_filename=endp_name,
            mode=mode
        )
        return IngestResponse(
            status="success",
            message=f"Successfully processed {summary['total_events']} events into {summary['total_incidents']} incidents.",
            dashboard=summary
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Log parsing or processing error: {str(e)}")


@router.post("/triage", response_model=TriageResponse)
def trigger_triage(req: TriageRequest):
    """Re-execute triage pipeline across current events with specified mode ('fast' or 'neural')."""
    service = TriageService.get_instance()
    if not service.events:
        service.load_demo_dataset()
    else:
        service._process_events(service.events, [], mode=req.mode)

    summary = service.get_dashboard_summary()
    return TriageResponse(
        status="success",
        message=f"Triage re-executed in '{req.mode}' mode.",
        dashboard=summary
    )


@router.get("/incidents")
def list_incidents(severity: Optional[str] = None):
    """Return all correlated incidents with optional severity filtering."""
    service = TriageService.get_instance()
    return service.get_incidents_list(severity=severity)


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Return comprehensive case dossier for a specific incident."""
    service = TriageService.get_instance()
    detail = service.get_incident_detail(incident_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return detail


@router.get("/evaluation")
def get_evaluation():
    """Return ground truth empirical evaluation metrics (Precision, Recall, F1, Latencies)."""
    service = TriageService.get_instance()
    return service.get_evaluation()


@router.get("/config")
def get_configuration():
    """Return transparent organization parameters, thresholds, and severity weights."""
    service = TriageService.get_instance()
    return service.get_config_view()


@router.get("/incidents/{incident_id}/export")
def export_incident(incident_id: str, format: str = "json"):
    """Download incident report in JSON, Markdown, or PDF format."""
    service = TriageService.get_instance()
    content, media_type, filename = service.get_report_export(incident_id, format)
    if not content:
        raise HTTPException(status_code=404, detail=f"Export for incident '{incident_id}' in format '{format}' not found.")

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=content, media_type=media_type, headers=headers)
