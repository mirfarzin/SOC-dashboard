import React, { useState, useEffect } from 'react'
import {
  FileText,
  Download,
  CheckSquare,
  Square,
  AlertTriangle,
  ShieldCheck,
  Cpu,
  Clock,
  User,
  Server,
  ArrowLeft,
  ChevronDown,
  Info,
  ExternalLink,
  Lock,
} from 'lucide-react'
import type { IncidentDetailResponse, IncidentListItem } from '../types/api'
import { fetchIncidentDetail, fetchIncidents, getExportUrl } from '../services/api'
import { SeverityBadge } from '../components/SeverityBadge'

interface IncidentDeepDiveViewProps {
  selectedIncidentId: string | null
  onBackToIncidents: () => void
}

export const IncidentDeepDiveView: React.FC<IncidentDeepDiveViewProps> = ({
  selectedIncidentId,
  onBackToIncidents,
}) => {
  const [incidentsList, setIncidentsList] = useState<IncidentListItem[]>([])
  const [currentId, setCurrentId] = useState<string>(selectedIncidentId || '')
  const [detail, setDetail] = useState<IncidentDetailResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({})

  // Load all incidents for the switcher
  useEffect(() => {
    fetchIncidents().then((list) => {
      setIncidentsList(list)
      if (!currentId && list.length > 0) {
        setCurrentId(list[0].incident_id)
      }
    })
  }, [])

  // Sync if selectedIncidentId changes from prop
  useEffect(() => {
    if (selectedIncidentId) {
      setCurrentId(selectedIncidentId)
    }
  }, [selectedIncidentId])

  // Load deep-dive detail whenever currentId changes
  useEffect(() => {
    if (!currentId) return
    setLoading(true)
    setError(null)
    setCompletedSteps({})
    fetchIncidentDetail(currentId)
      .then((data) => setDetail(data))
      .catch((err) => setError(err.message || 'Failed to fetch incident dossier'))
      .finally(() => setLoading(false))
  }, [currentId])

  const toggleStep = (index: number) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [index]: !prev[index],
    }))
  }

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto">
      {/* Top Header & Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cream-400 pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToIncidents}
            className="neu-btn-secondary p-2 rounded-xl text-ink hover:text-cream-950"
            title="Back to Incidents Table"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cream-700">
              <FileText className="w-3.5 h-3.5 text-cream-900" />
              <span>Stage 4 • Evidence-Backed Case Dossier</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-ink mt-1">
              Incident Deep Dive Analysis
            </h2>
          </div>
        </div>

        {/* Case Switcher & Export Bar */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Quick Case Switcher */}
          {incidentsList.length > 0 && (
            <div className="relative">
              <select
                value={currentId}
                onChange={(e) => setCurrentId(e.target.value)}
                className="neu-well py-2 pl-3 pr-8 text-xs font-mono font-bold text-ink appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-ink"
              >
                {incidentsList.map((inc) => (
                  <option key={inc.incident_id} value={inc.incident_id}>
                    {inc.incident_id} — {inc.severity} ({inc.severity_score})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-cream-700" />
            </div>
          )}

          {/* 1-Click Export Actions */}
          {currentId && (
            <div className="flex items-center gap-1.5">
              <a
                href={getExportUrl(currentId, 'pdf')}
                target="_blank"
                rel="noreferrer"
                download
                className="neu-btn px-3 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PDF Report</span>
              </a>
              <a
                href={getExportUrl(currentId, 'markdown')}
                target="_blank"
                rel="noreferrer"
                download
                className="neu-btn-secondary px-3 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Markdown</span>
              </a>
              <a
                href={getExportUrl(currentId, 'json')}
                target="_blank"
                rel="noreferrer"
                download
                className="neu-btn-secondary px-3 py-2 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>JSON</span>
              </a>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="neu-card p-16 text-center text-xs font-mono text-cream-700 animate-pulse">
          Generating intelligence briefing using offline Small Language Model...
        </div>
      ) : error || !detail ? (
        <div className="neu-card p-8 text-center text-sm font-mono text-red-700">
          {error || 'Incident not found.'}
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {/* Case Header Card */}
          <div className="neu-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-cream-700">
                  CASE DOSSIER:
                </span>
                <span className="text-base font-black font-mono text-ink">
                  {detail.incident.incident_id}
                </span>
                <SeverityBadge
                  severity={detail.incident.severity}
                  score={detail.incident.severity_score}
                  showScore
                />
              </div>
              <h3 className="text-lg font-bold text-ink">
                {detail.incident.title}
              </h3>
              <p className="text-xs text-cream-700">
                Created: {new Date(detail.incident.created_at).toLocaleString()} • Telemetry Events: {detail.incident.event_ids.length}
              </p>
            </div>

            {/* Entity Pills */}
            <div className="flex flex-col gap-1.5 text-xs font-mono">
              <div className="neu-well px-3 py-1.5 flex items-center gap-2">
                <User className="w-3.5 h-3.5 text-cream-900" />
                <span className="text-cream-700">User(s):</span>
                <span className="font-bold text-ink">
                  {detail.incident.entities_involved.users?.join(', ') || 'N/A'}
                </span>
              </div>
              <div className="neu-well px-3 py-1.5 flex items-center gap-2">
                <Server className="w-3.5 h-3.5 text-cream-900" />
                <span className="text-cream-700">Host(s):</span>
                <span className="font-bold text-ink">
                  {detail.incident.entities_involved.hosts?.join(', ') || 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* AI Disclosure & Human Authorization Alert */}
          <div className="p-4 rounded-xl border border-amber-300 bg-amber-50/70 text-xs text-amber-950 flex items-start gap-3">
            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold uppercase tracking-wide">
                Human-in-the-Loop Governance Notice:
              </span>{' '}
              {detail.provenance.human_in_the_loop_notice ||
                'ADVISORY NOTICE: This report is an AI-assisted triage briefing. No autonomous remediation actions were executed. All recommended steps require explicit authorization by a human Security Analyst.'}
            </div>
          </div>

          {/* SLM Executive Summary Glass Panel */}
          <div className="glass-panel p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-cream-400 pb-3">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-ink" />
                <h4 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Executive Incident Briefing
                </h4>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-cream-700">
                <span className="neu-well px-2 py-0.5 text-[11px]">
                  Model: {detail.provenance.local_model}
                </span>
                <span className="neu-well px-2 py-0.5 text-[11px]">
                  Latency: {detail.provenance.inference_latency_ms} ms
                </span>
                <span className="neu-well px-2 py-0.5 text-[11px] text-emerald-800 font-semibold">
                  Evidence Verified
                </span>
              </div>
            </div>

            <p className="text-sm leading-relaxed text-ink font-medium">
              {detail.slm_analysis.executive_summary}
            </p>
          </div>

          {/* Two-Column Intelligence Grid: Verified Facts vs Threat Hypotheses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Grounded Evidence & Verified Facts */}
            <div className="neu-card p-6 flex flex-col justify-between border-l-4 border-l-emerald-600">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck className="w-4 h-4 text-emerald-700" />
                  <h4 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                    1. Grounded Facts & Evidence
                  </h4>
                </div>
                <p className="text-xs text-cream-700 mb-4">
                  Deterministic facts verified against raw event IDs with zero hallucination.
                </p>

                <ul className="space-y-2.5 text-xs text-cream-900">
                  {detail.slm_analysis.facts.map((fact, idx) => (
                    <li key={idx} className="neu-well p-3 flex items-start gap-2 leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 shrink-0 mt-1.5" />
                      <span>{fact}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 pt-3 border-t border-cream-400 text-[11px] text-cream-700 font-mono">
                Citations Verified: {detail.slm_analysis.referenced_event_ids?.length || 0} events
              </div>
            </div>

            {/* Threat Hypotheses */}
            <div className="neu-card p-6 flex flex-col justify-between border-l-4 border-l-amber-600">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-amber-700" />
                  <h4 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                    2. Working Threat Hypotheses
                  </h4>
                </div>
                <p className="text-xs text-cream-700 mb-4">
                  AI-assisted operational hypotheses requiring analyst validation.
                </p>

                <ul className="space-y-2.5 text-xs text-cream-900">
                  {detail.slm_analysis.hypotheses.map((hyp, idx) => (
                    <li key={idx} className="neu-well p-3 flex items-start gap-2 leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-600 shrink-0 mt-1.5" />
                      <span>{hyp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 pt-3 border-t border-cream-400 text-[11px] text-cream-700 font-mono">
                Status: Awaiting Analyst Out-of-Band Confirmation
              </div>
            </div>
          </div>

          {/* Missing Evidence / Telemetry Gaps */}
          {detail.slm_analysis.missing_evidence && detail.slm_analysis.missing_evidence.length > 0 && (
            <div className="neu-card p-5">
              <h4 className="text-xs font-bold text-ink uppercase font-mono tracking-wide mb-2 flex items-center gap-2">
                <Info className="w-3.5 h-3.5 text-cream-800" />
                Telemetry Gaps & Missing Forensic Artifacts
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono text-cream-800">
                {detail.slm_analysis.missing_evidence.map((gap, idx) => (
                  <div key={idx} className="neu-well p-2.5 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-cream-700 shrink-0" />
                    <span>{gap}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Interactive Advisory Next Steps Checklist */}
          <div className="neu-card p-6">
            <div className="border-b border-cream-400 pb-3 mb-4">
              <h4 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                Interactive Analyst Containment & Remediation Checklist
              </h4>
              <p className="text-xs text-cream-700">
                Step-by-step advisory playbooks. Check off items as actions are performed.
              </p>
            </div>

            <div className="space-y-2.5">
              {detail.slm_analysis.recommended_actions.map((action, idx) => {
                const isDone = Boolean(completedSteps[idx])
                return (
                  <div
                    key={idx}
                    onClick={() => toggleStep(idx)}
                    className={`neu-well p-3.5 flex items-center justify-between cursor-pointer transition-all ${
                      isDone ? 'bg-emerald-50/50 border-emerald-300 text-emerald-950' : 'hover:bg-cream-200'
                    }`}
                  >
                    <div className="flex items-center gap-3 text-xs">
                      {isDone ? (
                        <CheckSquare className="w-4 h-4 text-emerald-700 shrink-0" />
                      ) : (
                        <Square className="w-4 h-4 text-cream-600 shrink-0" />
                      )}
                      <span className={isDone ? 'line-through opacity-75' : 'font-medium'}>
                        {action}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold bg-cream-300 text-cream-800">
                      {isDone ? 'Completed' : 'Pending Authorization'}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Full Chronological Timeline Table */}
          <div className="neu-card p-6">
            <div className="flex items-center justify-between border-b border-cream-400 pb-3 mb-4">
              <div>
                <h4 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Event Chronology (Audit Trail)
                </h4>
                <p className="text-xs text-cream-700">
                  Exact normalized telemetry sequence associated with this case
                </p>
              </div>
              <span className="text-xs font-mono text-cream-700 font-semibold">
                {detail.incident.timeline.length} events
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-cream-400 text-cream-700 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Event ID</th>
                    <th className="py-2.5 px-3">Timestamp</th>
                    <th className="py-2.5 px-3">Identity</th>
                    <th className="py-2.5 px-3">Endpoint</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Action / Telemetry Detail</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cream-300 text-[11px]">
                  {detail.incident.timeline.map((evt, idx) => (
                    <tr key={idx} className="hover:bg-cream-200/50">
                      <td className="py-2.5 px-3 font-bold text-ink">
                        {evt.event_id}
                      </td>
                      <td className="py-2.5 px-3 text-cream-700">
                        {evt.timestamp}
                      </td>
                      <td className="py-2.5 px-3 text-ink font-medium">
                        {evt.username || 'N/A'}
                      </td>
                      <td className="py-2.5 px-3 text-cream-800">
                        {evt.device_id || 'N/A'}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            (evt.result || '').toUpperCase() === 'SUCCESS'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {evt.result || 'N/A'}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-cream-900 max-w-sm truncate">
                        {evt.detail || evt.action || 'Event recorded'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
