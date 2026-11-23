import type {
  HealthResponse,
  DashboardResponse,
  IncidentListItem,
  IncidentDetailResponse,
  EvaluationResponse,
  ConfigResponse,
} from '../types/api'

const API_BASE = '/api'

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`)
  return res.json()
}

export async function fetchDashboard(): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE}/dashboard`)
  if (!res.ok) throw new Error(`Dashboard load failed: ${res.statusText}`)
  return res.json()
}

export async function loadDemoDataset(): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE}/demo/load`, { method: 'POST' })
  if (!res.ok) throw new Error(`Demo load failed: ${res.statusText}`)
  return res.json()
}

export async function fetchIncidents(severity?: string): Promise<IncidentListItem[]> {
  const url = severity ? `${API_BASE}/incidents?severity=${encodeURIComponent(severity)}` : `${API_BASE}/incidents`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Incidents fetch failed: ${res.statusText}`)
  return res.json()
}

export async function fetchIncidentDetail(incidentId: string): Promise<IncidentDetailResponse> {
  const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}`)
  if (!res.ok) throw new Error(`Incident ${incidentId} fetch failed: ${res.statusText}`)
  return res.json()
}

export async function fetchEvaluation(): Promise<EvaluationResponse> {
  const res = await fetch(`${API_BASE}/evaluation`)
  if (!res.ok) throw new Error(`Evaluation metrics fetch failed: ${res.statusText}`)
  return res.json()
}

export async function fetchConfig(): Promise<ConfigResponse> {
  const res = await fetch(`${API_BASE}/config`)
  if (!res.ok) throw new Error(`Configuration fetch failed: ${res.statusText}`)
  return res.json()
}

export async function ingestLogs(
  authFile: File | null,
  endpointFile: File | null,
  mode: 'fast' | 'neural' = 'fast'
): Promise<{ status: string; message: string; dashboard: DashboardResponse }> {
  const formData = new FormData()
  if (authFile) formData.append('auth_file', authFile)
  if (endpointFile) formData.append('endpoint_file', endpointFile)
  formData.append('mode', mode)

  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const errorJson = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(errorJson.detail || 'Ingestion failed')
  }
  return res.json()
}

export async function triggerTriage(mode: 'fast' | 'neural' = 'fast'): Promise<{ status: string; message: string; dashboard: DashboardResponse }> {
  const res = await fetch(`${API_BASE}/triage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  })
  if (!res.ok) throw new Error(`Triage run failed: ${res.statusText}`)
  return res.json()
}

export function getExportUrl(incidentId: string, format: 'json' | 'markdown' | 'pdf'): string {
  return `${API_BASE}/incidents/${encodeURIComponent(incidentId)}/export?format=${format}`
}
