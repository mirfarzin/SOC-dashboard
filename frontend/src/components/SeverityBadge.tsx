import React from 'react'
import { cn } from '../lib/utils'

interface SeverityBadgeProps {
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational' | string
  score?: number
  className?: string
  showScore?: boolean
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  score,
  className,
  showScore = false,
}) => {
  const norm = (severity || '').toUpperCase()

  let colorClasses = 'bg-cream-200 text-cream-900 border-cream-400'
  let dotColor = 'bg-cream-700'

  if (norm === 'CRITICAL') {
    colorClasses = 'bg-red-50 text-red-900 border-red-200'
    dotColor = 'bg-red-600'
  } else if (norm === 'HIGH') {
    colorClasses = 'bg-amber-50 text-amber-900 border-amber-200'
    dotColor = 'bg-amber-600'
  } else if (norm === 'MEDIUM') {
    colorClasses = 'bg-yellow-50 text-yellow-900 border-yellow-300'
    dotColor = 'bg-yellow-600'
  } else if (norm === 'LOW') {
    colorClasses = 'bg-emerald-50 text-emerald-900 border-emerald-200'
    dotColor = 'bg-emerald-600'
  } else if (norm === 'INFORMATIONAL' || norm === 'INFO') {
    colorClasses = 'bg-cream-100 text-cream-800 border-cream-300'
    dotColor = 'bg-cream-600'
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border shadow-sm font-mono tracking-wide',
        colorClasses,
        className
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full', dotColor)} />
      <span>{severity}</span>
      {showScore && score !== undefined && (
        <span className="text-[10px] opacity-75 font-semibold">({score})</span>
      )}
    </span>
  )
}
