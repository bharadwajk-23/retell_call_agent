// Missed-exercise-day thresholds used to prioritize outreach.
// Derived purely from exercise_missed_days already returned by /patients.
const URGENT_THRESHOLD = 10

export function getMissedDaysSeverity(missedDays) {
  const days = Number(missedDays) || 0
  return days >= URGENT_THRESHOLD
    ? { level: 'urgent', label: 'Urgent' }
    : { level: 'follow-up', label: 'Follow-up' }
}

export function formatPatientCode(id) {
  return `P-${1040 + Number(id || 0)}`
}

export function getInitials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}
