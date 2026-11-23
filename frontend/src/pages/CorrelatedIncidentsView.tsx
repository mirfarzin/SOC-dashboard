import React, { useState, useEffect } from 'react'
import {
  Activity,
  Search,
  Filter,
  ArrowUpRight,
  ShieldAlert,
  Server,
  User,
  Clock,
  Layers,
  ChevronRight,
} from 'lucide-react'
import type { IncidentListItem } from '../types/api'
import { fetchIncidents } from '../services/api'
import { SeverityBadge } from '../components/SeverityBadge'

interface CorrelatedIncidentsViewProps {
  onSelectIncident: (id: string) => void
}

export const CorrelatedIncidentsView: React.FC<CorrelatedIncidentsViewProps> = ({
  onSelectIncident,
}) => {
  const [incidents, setIncidents] = useState<IncidentListItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All')
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [selectedSeverity])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const sevParam = selectedSeverity === 'All' ? undefined : selectedSeverity
      const data = await fetchIncidents(sevParam)
      setIncidents(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch incidents')
    } finally {
      setLoading(false)
    }
  }

  const filteredIncidents = incidents.filter((inc) => {
    if (!searchTerm) return true
    const term = searchTerm.toLowerCase()
    return (
      inc.incident_id.toLowerCase().includes(term) ||
      inc.title.toLowerCase().includes(term) ||
      inc.users.some((u) => u.toLowerCase().includes(term)) ||
      inc.hosts.some((h) => h.toLowerCase().includes(term)) ||
      inc.correlation_explanation.toLowerCase().includes(term)
    )
  })

  const severityFilters = ['All', 'Critical', 'High', 'Medium', 'Low', 'Informational']

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="border-b border-cream-400 pb-5">
        <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cream-700">
          <Activity className="w-3.5 h-3.5 text-cream-900" />
          <span>Stage 2 & 3 • Graph Clustering & Synergy Scoring</span>
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-ink mt-1">
          Correlated Security Incidents
        </h2>
        <p className="text-sm text-cream-700 mt-0.5">
          Temporal Union-Find clustering connects disparate identity, host, and network anomalies into unified incident cases.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="neu-card p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-cream-700" />
          <input
            type="text"
            placeholder="Search by case ID, user, host, IP, or rule title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="neu-well w-full pl-10 pr-4 py-2 text-xs text-ink placeholder-cream-600 focus:outline-none focus:ring-1 focus:ring-ink"
          />
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <Filter className="w-3.5 h-3.5 text-cream-700 shrink-0 mr-1" />
          {severityFilters.map((sev) => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              className={`text-xs px-3 py-1.5 rounded-lg font-mono font-medium transition-all shrink-0 ${
                selectedSeverity === sev
                  ? 'neu-btn text-cream-100 font-bold'
                  : 'neu-btn-secondary text-cream-800 hover:text-ink'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Incidents Table / Cards */}
      <div className="neu-card p-6">
        <div className="flex items-center justify-between border-b border-cream-400 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cream-800" />
            <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
              Correlated Case Table ({filteredIncidents.length})
            </h3>
          </div>
          <span className="text-xs font-mono text-cream-700">
            Window: 1800s (30m) • Graph pivots: user, host, ip
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-cream-700 animate-pulse">
            Loading correlated incidents from backend engine...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs font-mono text-red-700">
            Error loading cases: {error}
          </div>
        ) : filteredIncidents.length === 0 ? (
          <div className="p-12 text-center text-xs font-mono text-cream-700">
            No incidents found matching the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-cream-400 text-cream-700 font-mono uppercase text-[11px]">
                  <th className="py-2.5 px-3">Case ID</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Case Title</th>
                  <th className="py-2.5 px-3">Identities & Endpoints</th>
                  <th className="py-2.5 px-3">Correlation Logic</th>
                  <th className="py-2.5 px-3 text-center">Telemetry</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-300">
                {filteredIncidents.map((inc) => (
                  <tr
                    key={inc.incident_id}
                    onClick={() => onSelectIncident(inc.incident_id)}
                    className="hover:bg-cream-200/70 transition-colors group cursor-pointer"
                  >
                    <td className="py-3 px-3 font-mono font-bold text-ink whitespace-nowrap">
                      {inc.incident_id}
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      <SeverityBadge severity={inc.severity} score={inc.severity_score} showScore />
                    </td>
                    <td className="py-3 px-3 font-medium text-ink max-w-[200px]">
                      <div className="truncate font-semibold">{inc.title}</div>
                      <div className="text-[10px] text-cream-700 font-mono mt-0.5">
                        {inc.finding_count} detection rule(s) fired
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-col gap-0.5 font-mono text-[11px]">
                        <span className="text-ink font-medium">
                          👤 {inc.users.length > 0 ? inc.users.join(', ') : 'N/A'}
                        </span>
                        <span className="text-cream-700">
                          💻 {inc.hosts.length > 0 ? inc.hosts.join(', ') : 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-cream-800 text-[11px] max-w-xs">
                      <p className="line-clamp-2 italic">
                        "{inc.correlation_explanation}"
                      </p>
                    </td>
                    <td className="py-3 px-3 text-center font-mono">
                      <span className="font-bold text-ink text-sm">{inc.event_count}</span>
                      <span className="text-[10px] text-cream-700 block">events</span>
                    </td>
                    <td className="py-3 px-3 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onSelectIncident(inc.incident_id)
                        }}
                        className="neu-btn px-3 py-1.5 rounded-lg text-xs font-semibold inline-flex items-center gap-1 group-hover:bg-cream-900 transition-all"
                      >
                        <span>Deep Dive</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
