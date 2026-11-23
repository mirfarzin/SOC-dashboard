import React, { useState, useEffect } from 'react'
import {
  Settings,
  Clock,
  Shield,
  Sliders,
  Cpu,
  Lock,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'
import type { ConfigResponse } from '../types/api'
import { fetchConfig } from '../services/api'

export const ConfigurationView: React.FC = () => {
  const [config, setConfig] = useState<ConfigResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchConfig()
      .then((cfg) => setConfig(cfg))
      .catch((err) => setError(err.message || 'Failed to fetch configuration'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col gap-6 p-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="border-b border-cream-400 pb-5">
        <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cream-700">
          <Settings className="w-3.5 h-3.5 text-cream-900" />
          <span>Stage 6 • Governance & Operational Thresholds</span>
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-ink mt-1">
          System Configuration & Detection Rules
        </h2>
        <p className="text-sm text-cream-700 mt-0.5">
          Transparent operational thresholds, sliding window parameters, and strict air-gapped security safeguards.
        </p>
      </div>

      {loading ? (
        <div className="neu-card p-16 text-center text-xs font-mono text-cream-700 animate-pulse">
          Loading system configuration parameters...
        </div>
      ) : error || !config ? (
        <div className="neu-card p-8 text-center text-sm font-mono text-red-700">
          {error || 'Configuration could not be loaded.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Organization & Working Hours */}
          <div className="neu-card p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 border-b border-cream-400 pb-3 mb-4">
                <Clock className="w-4 h-4 text-ink" />
                <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Organization & Working Hours
                </h3>
              </div>

              <div className="space-y-2.5 font-mono text-xs">
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Organization Name</span>
                  <span className="font-bold text-ink">{config.organization.name}</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Primary Timezone</span>
                  <span className="font-bold text-ink">{config.organization.timezone} (IST • UTC+05:30)</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Standard Working Hours</span>
                  <span className="font-bold text-ink">
                    {String(config.organization.working_hours.start_hour).padStart(2, '0')}:00 – {String(config.organization.working_hours.end_hour).padStart(2, '0')}:00 IST
                  </span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Working Days</span>
                  <span className="font-bold text-ink">Mon – Fri (Days 0, 1, 2, 3, 4)</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Weekend Activity Flagging</span>
                  <span className="font-bold text-emerald-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Enabled (Unusual Hours Rule)
                  </span>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-cream-700 mt-4 pt-3 border-t border-cream-400">
              * Any authentication events outside 09:00 - 18:00 IST trigger RULE_UNUSUAL_LOGIN_HOURS.
            </div>
          </div>

          {/* Suspicious Activity Detectors */}
          <div className="neu-card p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 border-b border-cream-400 pb-3 mb-4">
                <Shield className="w-4 h-4 text-ink" />
                <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Core Detection Rule Parameters
                </h3>
              </div>

              <div className="space-y-2.5 font-mono text-xs">
                <div className="neu-well p-3">
                  <div className="flex items-center justify-between font-bold text-ink">
                    <span>RULE_FAILED_LOGIN_BURST</span>
                    <span className="text-emerald-800">ACTIVE</span>
                  </div>
                  <div className="text-[11px] text-cream-700 mt-1">
                    Threshold: ≥ 5 failed logins within 300s window. Escalates on subsequent success within 600s.
                  </div>
                </div>

                <div className="neu-well p-3">
                  <div className="flex items-center justify-between font-bold text-ink">
                    <span>RULE_UNUSUAL_LOGIN_HOURS</span>
                    <span className="text-emerald-800">ACTIVE</span>
                  </div>
                  <div className="text-[11px] text-cream-700 mt-1">
                    Flags logons outside organization working hours or during weekend windows.
                  </div>
                </div>

                <div className="neu-well p-3">
                  <div className="flex items-center justify-between font-bold text-ink">
                    <span>RULE_UNAUTHORIZED_PRIV_ESCALATION</span>
                    <span className="text-emerald-800">ACTIVE</span>
                  </div>
                  <div className="text-[11px] text-cream-700 mt-1">
                    Flags role elevation or admin account addition lacking verifiable approval reference.
                  </div>
                </div>

                <div className="neu-well p-3">
                  <div className="flex items-center justify-between font-bold text-ink">
                    <span>RULE_SECURITY_CONTROL_TAMPERING</span>
                    <span className="text-emerald-800">ACTIVE</span>
                  </div>
                  <div className="text-[11px] text-cream-700 mt-1">
                    Flags service stops, registry modifications, or process termination targeting EDR/Antivirus.
                  </div>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-cream-700 mt-4 pt-3 border-t border-cream-400">
              * Fully deterministic rule evaluation runs across normalized events in linear time.
            </div>
          </div>

          {/* Correlation & Severity Scoring */}
          <div className="neu-card p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 border-b border-cream-400 pb-3 mb-4">
                <Sliders className="w-4 h-4 text-ink" />
                <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Correlation & Severity Weights
                </h3>
              </div>

              <div className="space-y-2.5 font-mono text-xs">
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Clustering Time Window</span>
                  <span className="font-bold text-ink">{config.correlation.time_window_seconds}s (30 minutes)</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Graph Correlation Algorithm</span>
                  <span className="font-bold text-ink">Disjoint Set (Union-Find)</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Entity Pivots</span>
                  <span className="font-bold text-ink">Username, Hostname, Source IP</span>
                </div>
                <div className="neu-well p-3">
                  <span className="text-cream-700 block text-[10px] uppercase">Severity Score Thresholds (0–100)</span>
                  <div className="grid grid-cols-4 gap-2 text-center mt-1.5 font-bold">
                    <span className="p-1 rounded bg-red-100 text-red-800">
                      CRIT ≥ {config.severity.thresholds.critical}
                    </span>
                    <span className="p-1 rounded bg-amber-100 text-amber-800">
                      HIGH ≥ {config.severity.thresholds.high}
                    </span>
                    <span className="p-1 rounded bg-yellow-100 text-yellow-900">
                      MED ≥ {config.severity.thresholds.medium}
                    </span>
                    <span className="p-1 rounded bg-emerald-100 text-emerald-800">
                      LOW ≥ {config.severity.thresholds.low}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-cream-700 mt-4 pt-3 border-t border-cream-400">
              * Multi-stage synergy bonus applies when credential attacks precede privilege escalation or tampering.
            </div>
          </div>

          {/* Small Language Model Air-Gap Profile */}
          <div className="neu-card p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 border-b border-cream-400 pb-3 mb-4">
                <Cpu className="w-4 h-4 text-ink" />
                <h3 className="text-sm font-bold text-ink uppercase font-mono tracking-wide">
                  Air-Gapped SLM Specification
                </h3>
              </div>

              <div className="space-y-2.5 font-mono text-xs">
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Configured Model ID</span>
                  <span className="font-bold text-ink">{config.slm.model_id}</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Local Disk Location</span>
                  <span className="font-bold text-ink">{config.slm.local_model_path}</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Strict Offline Mode</span>
                  <span className="font-bold text-emerald-800 flex items-center gap-1">
                    <Lock className="w-3.5 h-3.5" /> Enforced (Zero Cloud APIs)
                  </span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Execution Hardware</span>
                  <span className="font-bold text-ink">{config.slm.device.toUpperCase()} (Torch PyTorch)</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Max Generated Tokens</span>
                  <span className="font-bold text-ink">{config.slm.max_new_tokens} tokens</span>
                </div>
                <div className="neu-well p-3 flex items-center justify-between">
                  <span className="text-cream-700">Sampling Temperature</span>
                  <span className="font-bold text-ink">{config.slm.temperature} (Deterministic)</span>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-cream-700 mt-4 pt-3 border-t border-cream-400">
              * Hallucination validation regex rejects any response citing unverified event identifiers.
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
