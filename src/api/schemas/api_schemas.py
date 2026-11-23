"""
Pydantic Request and Response Schemas for the FastAPI Backend.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    system: str
    participant: str
    usn: str
    track: str
    operating_mode: str
    model_cached: bool
    model_name: str
    version: str


class ModelStatusSchema(BaseModel):
    name: str
    cached: bool
    device: str
    offline_enforced: bool


class IncidentListItemSchema(BaseModel):
    incident_id: str
    title: str
    severity: str
    severity_score: int
    severity_breakdown: List[str]
    correlation_explanation: str
    users: List[str]
    hosts: List[str]
    ips: List[str]
    event_count: int
    finding_count: int
    created_at: str


class DashboardResponse(BaseModel):
    total_events: int
    total_incidents: int
    high_critical_count: int
    severity_distribution: Dict[str, int]
    operating_mode: str
    model_status: ModelStatusSchema
    recent_incidents: List[Dict[str, Any]]
    diagnostics: Dict[str, Any]


class TriageRequest(BaseModel):
    mode: str = Field(default="fast", description="'fast' for deterministic or 'neural' for local SLM")


class TriageResponse(BaseModel):
    status: str
    message: str
    dashboard: DashboardResponse


class IngestResponse(BaseModel):
    status: str
    message: str
    dashboard: DashboardResponse
