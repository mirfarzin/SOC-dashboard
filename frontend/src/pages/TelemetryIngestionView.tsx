import React, { useState } from 'react'
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Database,
  ArrowRight,
  RefreshCw,
  Clock,
  UserCheck,
  Server,
  ShieldCheck,
} from 'lucide-react'
import type { DashboardResponse } from '../types/api'
import { ingestLogs, loadDemoDataset } from '../services/api'

interface TelemetryIngestionViewProps {
  dashboard: DashboardResponse
  onDashboardUpdate: (dash: DashboardResponse) => void
  triageMode: 'fast' | 'neural'
}

export const TelemetryIngestionView: React.FC<TelemetryIngestionViewProps> = ({
  dashboard,
  onDashboardUpdate,
  triageMode,
}) => {
  const [authFile, setAuthFile] = useState<File | null>(null)
  const [endpointFile, setEndpointFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!authFile && !endpointFile) {
      setFeedback({ type: 'error', message: 'Please select at least one log file (Auth or Endpoint).' })
      return
    }

    setIsUploading(true)
    setFeedback(null)
    try {
      const res = await ingestLogs(authFile, endpointFile, triageMode)
      onDashboardUpdate(res.dashboard)
      setFeedback({ type: 'success', message: res.message })
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to ingest logs' })
    } finally {
      setIsUploading(false)
    }
  }

  const handleReloadBenchmark = async () => {
    setIsUploading(true)
    setFeedback(null)
    try {
      const updated = await loadDemoDataset()
      onDashboardUpdate(updated)
      setFeedback({ type: 'success', message: 'Successfully loaded synthetic Scenarios A through E (20 events, 5 incidents).' })
      setAuthFile(null)
      setEndpointFile(null)
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to load benchmark' })
    } finally {
      setIsUploading(false)
    }
  }

  const diag = dashboard.diagnostics || {
    total_valid_events: dashboard.total_events,
    total_errors: 0,
    unique_users_count: 0,
    unique_hosts_count: 0,
    unique_source_ips_count: 0,
    log_sources: ['auth', 'endpoint'],
    auth_summary: { successes: 0, failures: 0 },
    privilege_changes_count: 0,
    time_range: { start: null, end: null, duration_minutes: 0 },
    error_sample: [],
  }

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="border-b border-cream-400 pb-5">
        <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cream-700">
          <Database className="w-3.5 h-3.5 text-cream-900" />
          <span>Stage 1 • Log Normalization & Audit</span>
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-ink mt-1">
          Telemetry Ingestion & Preprocessing
        </h2>
        <p className="text-sm text-cream-700 mt-0.5">
          Ingest raw CSV/JSON security event logs into the normalized schema with timestamp validation and field aliasing.
        </p>
      </div>

      {/* Notification Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl flex items-center gap-3 text-sm font-medium border ${
            feedback.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
              : 'bg-red-50 text-red-900 border-red-200'
          }`}
        >
          {feedback.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
          )}
          <span>{feedback.message}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload Wells */}
        <div className="lg:col-span-5 flex flex-col gap-5">
          <div className="neu-card p-6">
            <h3 className="text-base font-bold text-ink mb-1">
              Upload Telemetry Logs
            </h3>
            <p className="text-xs text-cream-700 mb-5">
              Supports CSV or JSON logs with automatic header mapping (user, host, ip, action, status).
            </p>

            <form onSubmit={handleUpload} className="space-y-4">
              {/* Auth File Well */}
              <div>
                <label className="text-xs font-mono font-semibold text-cream-800 uppercase block mb-1.5">
                  1. Authentication Logs (CSV / JSON)
                </label>
                <div className="neu-well p-4 flex flex-col items-center justify-center text-center cursor-pointer hover:border-cream-500 transition-colors relative">
                  <input
                    type="file"
                    accept=".csv,.json"
                    onChange={(e) => setAuthFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <Upload className="w-6 h-6 text-cream-700 mb-2" />
                  {authFile ? (
                    <div className="text-xs font-mono font-bold text-ink truncate max-w-xs">
                      {authFile.name} ({(authFile.size / 1024).toFixed(1)} KB)
                    </div>
                  ) : (
                    <>
                      <div className="text-xs font-medium text-ink">
                        Click or drag auth log file here
                      </div>
                      <div className="text-[10px] text-cream-700 mt-0.5">
                        auth_logs.csv, security_events.json
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Endpoint File Well */}
              <div>
                <label className="text-xs font-mono font-semibold text-cream-800 uppercase block mb-1.5">
                  2. Endpoint Logs (CSV / JSON)
                </label>
                <div className="neu-well p-4 flex flex-col items-center justify-center text-center cursor-pointer hover:border-cream-500 transition-colors relative">
                  <input
                    type="file"
                    accept=".csv,.json"
                    onChange={(e) => setEndpointFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <Upload className="w-6 h-6 text-cream-700 mb-2" />
                  {endpointFile ? (
                    <div className="text-xs font-mono font-bold text-ink truncate max-w-xs">
                      {endpointFile.name} ({(endpointFile.size / 1024).toFixed(1)} KB)
                    </div>
                  ) : (
                    <>
                      <div className="text-xs font-medium text-ink">
                        Click or drag endpoint log file here
                      </div>
                      <div className="text-[10px] text-cream-700 mt-0.5">
                        endpoint_logs.csv, sysmon.json
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isUploading || (!authFile && !endpointFile)}
                className="neu-btn w-full py-2.5 px-4 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isUploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Processing & Triaging...</span>
                  </>
                ) : (
                  <>
                    <span>Ingest & Triage Logs</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="relative my-6 text-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-cream-400" />
              </div>
              <span className="relative bg-cream-100 px-3 text-[11px] font-mono text-cream-700 uppercase">
                Or Use Built-in Benchmark
              </span>
            </div>

            <button
              type="button"
              onClick={handleReloadBenchmark}
              disabled={isUploading}
              className="neu-btn-secondary w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Load Synthetic Benchmark Dataset (Scenarios A–E)</span>
            </button>
          </div>
        </div>

        {/* Right Column: Live Ingestion Diagnostics Panel */}
        <div className="lg:col-span-7 flex flex-col gap-5">
          <div className="neu-card p-6">
            <div className="flex items-center justify-between border-b border-cream-400 pb-3 mb-4">
              <div>
                <h3 className="text-base font-bold text-ink">
                  Ingestion Audit & Telemetry Diagnostics
                </h3>
                <p className="text-xs text-cream-700">
                  Integrity metrics calculated across active normalized telemetry
                </p>
              </div>
              <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200">
                Schema: Pydantic NormalizedEvent
              </span>
            </div>

            {/* 6 Diagnostics Metric Tiles */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Valid Events</span>
                <span className="text-xl font-bold font-mono text-ink mt-0.5 block">
                  {diag.total_valid_events}
                </span>
                <span className="text-[10px] text-emerald-700 flex items-center gap-1 mt-1">
                  <ShieldCheck className="w-3 h-3" /> Successfully parsed
                </span>
              </div>

              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Rejected / Errors</span>
                <span className="text-xl font-bold font-mono text-ink mt-0.5 block">
                  {diag.total_errors}
                </span>
                <span className="text-[10px] text-cream-700 mt-1 block">
                  {diag.total_errors === 0 ? 'Zero schema violations' : 'Logged in audit table'}
                </span>
              </div>

              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Unique Identities</span>
                <span className="text-xl font-bold font-mono text-ink mt-0.5 block">
                  {diag.unique_users_count}
                </span>
                <span className="text-[10px] text-cream-700 flex items-center gap-1 mt-1">
                  <UserCheck className="w-3 h-3" /> Distinct user accounts
                </span>
              </div>

              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Unique Endpoints</span>
                <span className="text-xl font-bold font-mono text-ink mt-0.5 block">
                  {diag.unique_hosts_count}
                </span>
                <span className="text-[10px] text-cream-700 flex items-center gap-1 mt-1">
                  <Server className="w-3 h-3" /> Monitored hostnames
                </span>
              </div>

              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Auth Activity</span>
                <div className="text-sm font-bold font-mono text-ink mt-0.5">
                  <span className="text-emerald-700">{diag.auth_summary?.successes || 0} OK</span>
                  <span className="text-cream-600 mx-1">/</span>
                  <span className="text-red-700">{diag.auth_summary?.failures || 0} Fail</span>
                </div>
                <span className="text-[10px] text-cream-700 mt-1 block">Authentication results</span>
              </div>

              <div className="neu-well p-3">
                <span className="text-[10px] font-mono uppercase text-cream-700 block">Window Duration</span>
                <span className="text-xl font-bold font-mono text-ink mt-0.5 block">
                  {diag.time_range?.duration_minutes || 0}m
                </span>
                <span className="text-[10px] text-cream-700 flex items-center gap-1 mt-1">
                  <Clock className="w-3 h-3" /> Telemetry span
                </span>
              </div>
            </div>

            {/* Ingestion Rules & Telemetry Norms */}
            <div className="mt-5 pt-4 border-t border-cream-400 space-y-2 text-xs">
              <div className="font-semibold text-ink font-mono uppercase text-[11px]">
                Active Normalization Field Mappings
              </div>
              <div className="grid grid-cols-2 gap-2 font-mono text-[11px] text-cream-800">
                <div className="neu-well p-2">
                  <span className="text-cream-600 block text-[10px]">TIMESTAMP ALIASES</span>
                  timestamp, time, datetime, @timestamp, Date
                </div>
                <div className="neu-well p-2">
                  <span className="text-cream-600 block text-[10px]">IDENTITY ALIASES</span>
                  user, username, account, TargetUserName
                </div>
                <div className="neu-well p-2">
                  <span className="text-cream-600 block text-[10px]">HOST ALIASES</span>
                  device, hostname, computer_name, Workstation
                </div>
                <div className="neu-well p-2">
                  <span className="text-cream-600 block text-[10px]">TIMEZONE ENFORCEMENT</span>
                  Asia/Kolkata (IST • UTC+05:30)
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
