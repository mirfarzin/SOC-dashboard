"""
Central configuration loader for PS02 Offline Incident Triage.
Loads settings from YAML with sensible defaults.
"""

from pathlib import Path
from typing import Any, Dict, List
import yaml
from pydantic import BaseModel, Field


class WorkingHoursConfig(BaseModel):
    start_hour: int = 9
    end_hour: int = 18


class OrganizationConfig(BaseModel):
    name: str = "Tinyverse SOC"
    timezone: str = "Asia/Kolkata"
    working_hours: WorkingHoursConfig = Field(default_factory=WorkingHoursConfig)
    working_days: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4])
    weekend_is_unusual: bool = True


class FailedLoginsConfig(BaseModel):
    enabled: bool = True
    failure_threshold: int = 5
    window_seconds: int = 300
    escalate_on_success_after_burst: bool = True
    success_window_seconds: int = 600


class UnusualHoursConfig(BaseModel):
    enabled: bool = True
    allow_weekend_for_oncall: bool = True
    flag_weekend: bool = True
    context_weight: float = 0.7


class PrivilegeEscalationConfig(BaseModel):
    enabled: bool = True
    sensitive_groups: List[str] = Field(default_factory=lambda: [
        "Administrators", "Domain Admins", "Enterprise Admins", "sudo", "root", "wheel", "SecurityAdmins"
    ])
    elevated_roles: List[str] = Field(default_factory=lambda: [
        "GlobalAdmin", "SecurityAdmin", "CloudAdmin"
    ])
    require_approval_metadata: bool = True


class EndpointActivityConfig(BaseModel):
    enabled: bool = True
    suspicious_processes: List[str] = Field(default_factory=list)
    security_controls_tampered: List[str] = Field(default_factory=list)


class DetectorsConfig(BaseModel):
    failed_logins: FailedLoginsConfig = Field(default_factory=FailedLoginsConfig)
    unusual_hours: UnusualHoursConfig = Field(default_factory=UnusualHoursConfig)
    privilege_escalation: PrivilegeEscalationConfig = Field(default_factory=PrivilegeEscalationConfig)
    endpoint_activity: EndpointActivityConfig = Field(default_factory=EndpointActivityConfig)


class CorrelationConfig(BaseModel):
    time_window_seconds: int = 1800
    correlate_by_user: bool = True
    correlate_by_host: bool = True
    correlate_by_ip: bool = True


class SeverityThresholds(BaseModel):
    critical: int = 85
    high: int = 65
    medium: int = 40
    low: int = 20


class SeverityConfig(BaseModel):
    weights: Dict[str, int] = Field(default_factory=dict)
    thresholds: SeverityThresholds = Field(default_factory=SeverityThresholds)


class SLMConfig(BaseModel):
    model_id: str = "HuggingFaceTB/SmolLM2-135M-Instruct"
    fallback_model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"
    local_model_path: str = "models/SmolLM2-135M-Instruct"
    max_new_tokens: int = 512
    temperature: float = 0.1
    device: str = "cpu"
    offline_mode: bool = True
    timeout_seconds: int = 30


class AppConfig(BaseModel):
    organization: OrganizationConfig = Field(default_factory=OrganizationConfig)
    detectors: DetectorsConfig = Field(default_factory=DetectorsConfig)
    correlation: CorrelationConfig = Field(default_factory=CorrelationConfig)
    severity: SeverityConfig = Field(default_factory=SeverityConfig)
    slm: SLMConfig = Field(default_factory=SLMConfig)


def load_config(config_path: Path | str | None = None) -> AppConfig:
    """Load configuration from settings.yaml or return defaults."""
    if config_path is None:
        # Default search path relative to project root
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "config" / "settings.yaml"
    else:
        config_path = Path(config_path)

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return AppConfig(**data)
    return AppConfig()
