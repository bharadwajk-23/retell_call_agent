import { useEffect, useState } from 'react'

const RECHECK_INTERVAL_MS = 60_000

const PERIODS = [
  { key: 'morning', label: 'Morning', icon: '🌤️', greeting: 'Good morning', from: 5, to: 11 },
  { key: 'afternoon', label: 'Afternoon', icon: '☀️', greeting: 'Good afternoon', from: 12, to: 16 },
  { key: 'evening', label: 'Evening', icon: '🌇', greeting: 'Good evening', from: 17, to: 20 },
  { key: 'night', label: 'Night', icon: '🌙', greeting: 'Good night', from: 21, to: 4 },
]

function periodForHour(hour) {
  return (
    PERIODS.find(({ from, to }) => (from <= to ? hour >= from && hour <= to : hour >= from || hour <= to)) ||
    PERIODS[0]
  )
}

// Testing override: ?tod=morning|afternoon|evening|night forces a period
// regardless of the clock, so every banner state can be previewed on demand.
function periodOverrideFromUrl() {
  const key = new URLSearchParams(window.location.search).get('tod')
  return PERIODS.find((p) => p.key === key) || null
}

export function useTimeOfDay() {
  const override = periodOverrideFromUrl()
  const [period, setPeriod] = useState(() => override || periodForHour(new Date().getHours()))

  useEffect(() => {
    if (override) return
    const tick = () => setPeriod(periodForHour(new Date().getHours()))
    tick()
    const interval = setInterval(tick, RECHECK_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [override])

  return period
}
