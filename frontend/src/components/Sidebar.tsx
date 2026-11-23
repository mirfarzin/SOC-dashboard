import React from 'react'
import {
  Shield,
  Database,
  Activity,
  FileText,
  CheckCircle2,
  Settings,
  Cpu,
  RefreshCw,
  WifiOff,
  User,
  Zap,
} from 'lucide-react'
import { cn } from '../lib/utils'
import type { DashboardResponse } from '../types/api'

export type TabId = 'overview' | 'ingestion' | 'incidents' | 'deepdive' | 'evaluation' | 'config'

interface SidebarProps {
  activeTab: TabId
  setActiveTab: (tab: TabId) => void
  dashboardData: DashboardResponse | null
  triageMode: 'fast' | 'neural'
  setTriageMode: (mode: 'fast' | 'neural') => void
  onReloadDemo: () => void
  isReloading: boolean
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  dashboardData,
  triageMode,
  setTriageMode,
  onReloadDemo,
  isReloading,
}) => {
  const navItems: Array<{ id: TabId; label: string; icon: React.FC<{ className?: string }> }> = [
    { id: 'overview', label: 'SOC Overview', icon: Shield },
    { id: 'ingestion', label: 'Telemetry Ingestion', icon: Database },
    { id: 'incidents', label: 'Correlated Incidents', icon: Activity },
    { id: 'deepdive', label: 'Incident Deep Dive', icon: FileText },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: CheckCircle2 },
    { id: 'config', label: 'System Configuration', icon: Settings },
  ]

  return (
    <aside className="w-72 bg-cream-100 border-r border-cream-400 flex flex-col justify-between shrink-0 h-screen sticky top-0 shadow-sm z-30 select-none">
      {/* Top Header & Identity */}
      <div className="p-5 flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-ink text-cream-200 flex items-center justify-center shadow-neu-sm shrink-0">
            <Shield className="w-5 h-5 text-cream-100" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider font-mono font-semibold text-cream-700">
              Problem Statement PS02
            </div>
            <h1 className="text-sm font-bold text-ink tracking-tight">
              Offline Triage Assistant
            </h1>
          </div>
        </div>

        {/* Participant Identity Badge */}
        <div className="neu-well p-3 flex flex-col gap-1 text-xs">
          <div className="flex items-center justify-between text-cream-700 font-mono text-[11px]">
            <span className="flex items-center gap-1">
              <User className="w-3 h-3 text-cream-900" /> Participant
            </span>
            <span className="font-bold text-ink">1MS24CI073</span>
          </div>
          <div className="font-semibold text-ink text-[13px] truncate">
            Mir Farzin Hussain
          </div>
          <div className="text-[11px] text-cream-700 truncate">
            CSE (AI & ML) • Phase 2 Final
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={cn(
                  'flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all text-left group',
                  isActive
                    ? 'neu-btn font-semibold text-cream-100 shadow-neu-sm'
                    : 'text-cream-800 hover:bg-cream-200 hover:text-ink'
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={cn(
                      'w-4 h-4 transition-colors',
                      isActive ? 'text-cream-200' : 'text-cream-600 group-hover:text-ink'
                    )}
                  />
                  <span>{item.label}</span>
                </div>
                {item.id === 'incidents' && dashboardData && (
                  <span
                    className={cn(
                      'text-xs font-mono px-2 py-0.5 rounded-full',
                      isActive
                        ? 'bg-cream-800 text-cream-100'
                        : 'bg-cream-300 text-cream-800'
                    )}
                  >
                    {dashboardData.total_incidents}
                  </span>
                )}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Bottom Status & Controls */}
      <div className="p-4 border-t border-cream-400 flex flex-col gap-3 bg-cream-50/50">
        {/* Mode Selector */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-mono text-cream-700 flex items-center justify-between">
            <span>TRIAGE INFERENCE MODE</span>
            <span className="font-bold text-ink capitalize">{triageMode}</span>
          </label>
          <div className="grid grid-cols-2 gap-1.5 bg-cream-300 p-1 rounded-lg">
            <button
              onClick={() => setTriageMode('fast')}
              className={cn(
                'text-xs py-1.5 px-2 rounded-md font-medium transition-all flex items-center justify-center gap-1',
                triageMode === 'fast'
                  ? 'bg-ink text-cream-100 shadow-sm font-semibold'
                  : 'text-cream-800 hover:text-ink'
              )}
            >
              <Zap className="w-3 h-3" /> Fast
            </button>
            <button
              onClick={() => setTriageMode('neural')}
              className={cn(
                'text-xs py-1.5 px-2 rounded-md font-medium transition-all flex items-center justify-center gap-1',
                triageMode === 'neural'
                  ? 'bg-ink text-cream-100 shadow-sm font-semibold'
                  : 'text-cream-800 hover:text-ink'
              )}
            >
              <Cpu className="w-3 h-3" /> SLM Neural
            </button>
          </div>
        </div>

        {/* Reload Demo Button */}
        <button
          onClick={onReloadDemo}
          disabled={isReloading}
          className="neu-btn-secondary w-full py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-2"
        >
          <RefreshCw className={cn('w-3.5 h-3.5', isReloading && 'animate-spin')} />
          <span>{isReloading ? 'Reloading...' : 'Reload Benchmark Data'}</span>
        </button>

        {/* 100% Offline Air-Gap Security Badge */}
        <div className="neu-well p-2.5 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold text-ink text-[11px]">100% OFFLINE</span>
          </div>
          <span className="text-[10px] text-cream-700 flex items-center gap-1">
            <WifiOff className="w-3 h-3 text-cream-800" /> Air-Gapped
          </span>
        </div>
      </div>
    </aside>
  )
}
