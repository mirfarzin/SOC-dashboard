export interface HealthResponse {
  status: string
  system: string
  participant: string
  usn: string
  track: string
  operating_mode: string
  model_cached: boolean
  model_name: string
  version: string
}

export interface ModelStatus {
  name: string
  cached: boolean
  device: string
  offline_enforced: boolean
}

export interface RecentIncidentItem {
  incident_id: string
  title: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational'
  severity_score: number
  users: string[]
  hosts: string[]
  event_count: number
  created_at: string
}

export interface IngestionDiagnostics {
  total_valid_events: number
  total_errors: number
  unique_users_count: number
  unique_hosts_count: number
  unique_source_ips_count: number
  log_sources: string[]
  auth_summary: {
    successes: number
    failures: number
  }
  privilege_changes_count: number
  time_range: {
    start: string | null
    end: string | null
    duration_minutes: number
  }
  error_sample: Array<{
    row_number?: number
    error: string
    raw: Record<string, any>
  }>
}

export interface DashboardResponse {
  total_events: number
  total_incidents: number
  high_critical_count: number
  severity_distribution: {
    Critical: number
    High: number
    Medium: number
    Low: number
    Informational: number
  }
  operating_mode: string
  model_status: ModelStatus
  recent_incidents: RecentIncidentItem[]
  diagnostics: IngestionDiagnostics
}

export interface FindingItem {
  rule_id: string
  rule_name: string
  description: string
  supporting_event_ids: string[]
  confidence: number
}

export interface TimelineEvent {
  event_id: string
  timestamp: string
  username?: string
  device_id?: string
  result?: string
  action?: string
  detail?: string
}

export interface IncidentRecord {
  incident_id: string
  title: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational'
  severity_score: number
  severity_breakdown: string[]
  correlation_explanation: string
  entities_involved: {
    users?: string[]
    hosts?: string[]
    ips?: string[]
  }
  event_ids: string[]
  timeline: TimelineEvent[]
  findings: FindingItem[]
  created_at: string
}

export interface IncidentListItem {
  incident_id: string
  title: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational'
  severity_score: number
  severity_breakdown: string[]
  correlation_explanation: string
  users: string[]
  hosts: string[]
  ips: string[]
  event_count: number
  finding_count: number
  created_at: string
}

export interface SLMAnalysis {
  incident_id?: string
  title?: string
  executive_summary: string
  facts: string[]
  hypotheses: string[]
  rule_explanations: string[]
  missing_evidence: string[]
  recommended_actions: string[]
  referenced_event_ids: string[]
  model_name: string
  is_fallback: boolean
  validation_passed: boolean
}

export interface Provenance {
  system: string
  version: string
  participant: string
  operating_mode: string
  local_model: string
  inference_latency_ms: number
  generated_at: string
  validation_passed: boolean
  evidence_count: number
  human_in_the_loop_notice: string
}

export interface NormalizedEventDetail {
  event_id: string
  timestamp: string
  event_source: string
  event_type: string
  username?: string
  device_id?: string
  source_ip?: string
  destination_ip?: string
  action?: string
  authentication_result?: string
  privilege_change?: string
  target_user?: string
  approval_reference?: string
  raw_event: Record<string, any>
}

export interface IncidentDetailResponse {
  incident: IncidentRecord
  slm_analysis: SLMAnalysis
  provenance: Provenance
  events_detail: NormalizedEventDetail[]
}

export interface EvaluationAccuracy {
  true_positives: number
  false_positives: number
  false_negatives: number
  precision: number
  recall: number
  f1_score: number
  false_positive_rate: number
}

export interface EvaluationPerformance {
  total_events_processed: number
  ingestion_throughput_eps: number
  ingestion_latency_s: number
  detection_latency_ms: number
  correlation_latency_ms: number
  severity_scoring_latency_ms: number
  total_pipeline_latency_ms: number
}

export interface ScenarioEvalItem {
  matched: boolean
  incident_id?: string
  rules_matched?: string[]
  severity_assigned?: string
  expected_severity?: string
  severity_correct?: boolean
  reason?: string
}

export interface EvaluationResponse {
  evaluation_notice: string
  metrics: EvaluationAccuracy
  performance: EvaluationPerformance
  incidents_summary: {
    total_incidents_formed: number
    severity_distribution: Record<string, number>
  }
  scenarios_evaluation: Record<string, ScenarioEvalItem>
}

export interface ConfigResponse {
  organization: {
    name: string
    timezone: string
    working_hours: {
      start_hour: number
      end_hour: number
    }
    working_days: number[]
    weekend_is_unusual: boolean
  }
  detectors: Record<string, any>
  correlation: {
    time_window_seconds: number
    correlate_by_user: boolean
    correlate_by_host: boolean
    correlate_by_ip: boolean
  }
  severity: {
    weights: Record<string, number>
    thresholds: {
      critical: number
      high: number
      medium: number
      low: number
    }
  }
  slm: {
    model_id: string
    fallback_model_id: string
    local_model_path: string
    max_new_tokens: number
    temperature: number
    device: string
    offline_mode: boolean
    timeout_seconds: number
  }
}
