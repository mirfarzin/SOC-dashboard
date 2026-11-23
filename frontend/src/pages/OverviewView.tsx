import React from 'react'
import {
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Lock,
  ArrowUpRight,
  Server,
  User,
  Clock,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { DashboardResponse } from '../types/api'
import { SeverityBadge } from '../components/SeverityBadge'

interface OverviewViewProps {
  dashboard: DashboardResponse
  onSelectIncident: (id: string) => void
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  dashboard,
  onSelectIncident,
}) => {
  // Chart data for severity distribution
  const chartData = [
    { name: 'Critical', count: dashboard.severity_distribution.Critical, color: '#C0392B' },
    { name: 'High', count: dashboard.severity_distribution.High, color: '#D35400' },
    { name: 'Medium', count: dashboard.severity_distribution.Medium, color: '#B7791F' },
    { name: 'Low', count: dashboard.severity_distribution.Low, color: '#276749' },
    { name: 'Informational', count: dashboard.severity_distribution.Informational, color: '#4A5568' },
  ]

  const totalValid = dashboard.diagnostics?.total_valid_events || dashboard.total_events
  const totalErrors = dashboard.diagnostics?.total_errors || 0
  const passRate = totalValid + totalErrors > 0 ? Math.round((totalValid / (totalValid + totalErrors)) * 100) : 100

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cream-400 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cream-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Air-Gapped SOC Operations Console</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-ink mt-1">
            Security Incident Triage Synopsis
          </h2>
          <p className="text-sm text-cream-700 mt-0.5">
            Real-time telemetry ingestion, Union-Find event correlation, and local Small Language Model reporting.
          </p>
        </div>

        {/* System Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="neu-well px-3 py-1.5 flex items-center gap-2 text-xs font-mono font-medium text-ink">
            <Lock className="w-3.5 h-3.5 text-emerald-600" />
            <span>100% Offline Active</span>
          </div>
          <div className="neu-well px-3 py-1.5 flex items-center gap-2 text-xs font-mono font-medium text-ink">
            <Cpu className="w-3.5 h-3.5 text-cream-900" />
            <span>SmolLM2-135M</span>
          </div>
        </div>
      </div>

      {/* 4 Neumorphic KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* KPI 1 */}
        <div className="neu-card p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cream-700">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">
              Ingested Events
            </span>
            <div className="w-8 h-8 rounded-lg bg-cream-300 flex items-center justify-center text-ink shadow-neu-sunken">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-ink tracking-tight font-mono">
              {dashboard.total_events}
            </div>
            <div className="text-xs text-cream-700 mt-1">
              Normalized auth & endpoint records
            </div>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="neu-card p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cream-700">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">
              Correlated Cases
            </span>
            <div className="w-8 h-8 rounded-lg bg-cream-300 flex items-center justify-center text-ink shadow-neu-sunken">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-ink tracking-tight font-mono">
              {dashboard.total_incidents}
            </div>
            <div className="text-xs text-cream-700 mt-1">
              Temporal entity clusters formed
            </div>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="neu-card p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cream-700">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">
              High & Critical
            </span>
            <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center text-red-700 shadow-neu-sunken">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-red-700 tracking-tight font-mono">
              {dashboard.high_critical_count}
            </div>
            <div className="text-xs text-cream-700 mt-1">
              Priority alerts requiring action
            </div>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="neu-card p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-cream-700">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider">
              Ingestion Integrity
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-700 shadow-neu-sunken">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-black text-emerald-800 tracking-tight font-mono">
              {passRate}%
            </div>
            <div className="text-xs text-cream-700 mt-1">
              Schema validation pass rate
            </div>
          </div>
        </div>
      </div>

      {/* Middle Row: Severity Distribution & Local SLM Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Chart */}
        <div className="neu-card p-6 lg:col-span-2 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-cream-400 pb-3">
            <div>
              <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                Severity Score Distribution
              </h3>
              <p className="text-xs text-cream-700">
                Incidents categorized by deterministic multi-stage synergy score
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-cream-700">Total: {dashboard.total_incidents}</span>
            </div>
          </div>

          <div className="h-56 mt-4 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#2D2924', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#DDD6C8' }}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fill: '#6E685F', fontSize: 11, fontFamily: 'monospace' }}
                  axisLine={{ stroke: '#DDD6C8' }}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(235, 229, 216, 0.5)' }}
                  contentStyle={{
                    backgroundColor: '#F8F5EE',
                    borderColor: '#DDD6C8',
                    borderRadius: '0.5rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    fontFamily: 'monospace',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-5 gap-2 mt-4 pt-3 border-t border-cream-400 text-center font-mono text-xs">
            {chartData.map((d) => (
              <div key={d.name} className="flex flex-col items-center">
                <span className="text-[10px] text-cream-700 uppercase">{d.name}</span>
                <span className="font-bold text-ink text-sm">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Local SLM Architecture Profile */}
        <div className="neu-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-cream-700 uppercase font-semibold">
              <Cpu className="w-4 h-4 text-ink" /> Local Intelligence Engine
            </div>
            <h3 className="text-base font-bold text-ink mt-1">
              SmolLM2-135M-Instruct
            </h3>
            <p className="text-xs text-cream-700 mt-1">
              Compact generative model executing strictly in local CPU memory with verifiable evidence citations.
            </p>
          </div>

          <div className="space-y-2.5 my-4 text-xs font-mono">
            <div className="neu-well p-2.5 flex items-center justify-between">
              <span className="text-cream-700">Weights Path</span>
              <span className="font-semibold text-ink truncate max-w-[150px]">
                models/SmolLM2
              </span>
            </div>
            <div className="neu-well p-2.5 flex items-center justify-between">
              <span className="text-cream-700">Inference Device</span>
              <span className="font-semibold text-ink">CPU / Local RAM</span>
            </div>
            <div className="neu-well p-2.5 flex items-center justify-between">
              <span className="text-cream-700">Grounding Validator</span>
              <span className="font-semibold text-emerald-800 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
              </span>
            </div>
            <div className="neu-well p-2.5 flex items-center justify-between">
              <span className="text-cream-700">Network Restriction</span>
              <span className="font-semibold text-emerald-800">Air-Gapped (0 Egress)</span>
            </div>
          </div>

          <div className="text-[11px] text-cream-700 italic border-t border-cream-400 pt-3">
            * Fully offline execution eliminates sensitive telemetry transmission to external cloud services.
          </div>
        </div>
      </div>

      {/* Bottom Row: Recent Incidents Roster Table */}
      <div className="neu-card p-6">
        <div className="flex items-center justify-between border-b border-cream-400 pb-4 mb-4">
          <div>
            <h3 className="text-base font-bold text-ink tracking-tight">
              Active Incident Roster
            </h3>
            <p className="text-xs text-cream-700">
              Correlated security cases ready for analyst deep-dive review and report generation
            </p>
          </div>
          <span className="text-xs font-mono text-cream-700 font-semibold">
            Showing {dashboard.recent_incidents.length} cases
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-cream-400 text-cream-700 font-mono uppercase text-[11px]">
                <th className="py-2.5 px-3">Case ID</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Case Title</th>
                <th className="py-2.5 px-3">Identity / Users</th>
                <th className="py-2.5 px-3">Endpoints</th>
                <th className="py-2.5 px-3 text-center">Events</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cream-300">
              {dashboard.recent_incidents.map((inc) => (
                <tr
                  key={inc.incident_id}
                  className="hover:bg-cream-200/70 transition-colors group cursor-pointer"
                  onClick={() => onSelectIncident(inc.incident_id)}
                >
                  <td className="py-3 px-3 font-mono font-bold text-ink">
                    {inc.incident_id}
                  </td>
                  <td className="py-3 px-3">
                    <SeverityBadge severity={inc.severity} score={inc.severity_score} showScore />
                  </td>
                  <td className="py-3 px-3 font-medium text-ink max-w-xs truncate">
                    {inc.title}
                  </td>
                  <td className="py-3 px-3 text-cream-800 font-mono text-[11px]">
                    {inc.users.length > 0 ? inc.users.join(', ') : 'N/A'}
                  </td>
                  <td className="py-3 px-3 text-cream-800 font-mono text-[11px]">
                    {inc.hosts.length > 0 ? inc.hosts.join(', ') : 'N/A'}
                  </td>
                  <td className="py-3 px-3 text-center font-mono font-semibold text-ink">
                    {inc.event_count}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onSelectIncident(inc.incident_id)
                      }}
                      className="neu-btn-secondary px-2.5 py-1 rounded-md text-[11px] font-semibold inline-flex items-center gap-1 group-hover:bg-ink group-hover:text-cream-100 transition-all"
                    >
                      <span>Triage Dossier</span>
                      <ArrowUpRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
