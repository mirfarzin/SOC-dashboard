import React, { useState, useEffect } from 'react'
import { Sidebar, type TabId } from './components/Sidebar'
import { OverviewView } from './pages/OverviewView'
import { TelemetryIngestionView } from './pages/TelemetryIngestionView'
import { CorrelatedIncidentsView } from './pages/CorrelatedIncidentsView'
import { IncidentDeepDiveView } from './pages/IncidentDeepDiveView'
import { EvaluationView } from './pages/EvaluationView'
import { ConfigurationView } from './pages/ConfigurationView'
import type { DashboardResponse, HealthResponse } from './types/api'
import { fetchDashboard, fetchHealth, loadDemoDataset } from './services/api'
import { Shield, WifiOff } from 'lucide-react'

export function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null)
  const [triageMode, setTriageMode] = useState<'fast' | 'neural'>('fast')
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null)
  const [healthData, setHealthData] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [isReloading, setIsReloading] = useState<boolean>(false)

  useEffect(() => {
    // Initial fetch of dashboard and health
    Promise.all([fetchDashboard(), fetchHealth()])
      .then(([dash, health]) => {
        setDashboardData(dash)
        setHealthData(health)
      })
      .catch((err) => {
        console.error('Initial dashboard/health load error:', err)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleReloadDemo = async () => {
    setIsReloading(true)
    try {
      const updated = await loadDemoDataset()
      setDashboardData(updated)
    } catch (err) {
      console.error('Reload demo error:', err)
    } finally {
      setIsReloading(false)
    }
  }

  const handleSelectIncident = (incidentId: string) => {
    setSelectedIncidentId(incidentId)
    setActiveTab('deepdive')
  }

  return (
    <div className="flex min-h-screen bg-cream-200 text-ink antialiased">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        dashboardData={dashboardData}
        triageMode={triageMode}
        setTriageMode={setTriageMode}
        onReloadDemo={handleReloadDemo}
        isReloading={isReloading}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Subtle Top Status Bar */}
        <header className="h-12 border-b border-cream-400 bg-cream-100/60 backdrop-blur-md px-8 flex items-center justify-between text-xs font-mono shrink-0 select-none">
          <div className="flex items-center gap-3 text-cream-700">
            <span className="font-bold text-ink">PS02 Offline Security Incident Triage Assistant</span>
            <span>•</span>
            <span>Hackathon Phase 2</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-cream-800">
              Participant: <strong className="text-ink">Mir Farzin Hussain</strong> (1MS24CI073)
            </span>
            <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              <span>100% OFFLINE</span>
            </div>
          </div>
        </header>

        {/* View Switcher */}
        <div className="flex-1 pb-16">
          {loading ? (
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="neu-card p-8 flex flex-col items-center gap-3">
                <div className="w-8 h-8 rounded-full border-2 border-ink border-t-transparent animate-spin" />
                <span className="text-xs font-mono text-cream-700">
                  Initializing PS02 SOC Workstation...
                </span>
              </div>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && dashboardData && (
                <OverviewView
                  dashboard={dashboardData}
                  onSelectIncident={handleSelectIncident}
                />
              )}

              {activeTab === 'ingestion' && dashboardData && (
                <TelemetryIngestionView
                  dashboard={dashboardData}
                  onDashboardUpdate={setDashboardData}
                  triageMode={triageMode}
                />
              )}

              {activeTab === 'incidents' && (
                <CorrelatedIncidentsView
                  onSelectIncident={handleSelectIncident}
                />
              )}

              {activeTab === 'deepdive' && (
                <IncidentDeepDiveView
                  selectedIncidentId={selectedIncidentId}
                  onBackToIncidents={() => setActiveTab('incidents')}
                />
              )}

              {activeTab === 'evaluation' && (
                <EvaluationView />
              )}

              {activeTab === 'config' && (
                <ConfigurationView />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
