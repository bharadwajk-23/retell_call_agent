import { useCallback, useEffect, useRef, useState } from 'react'
import { getPatients, resetDemo, startCall } from '../services/api'

const POLL_INTERVAL_MS = 2000

export function usePatients() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pendingId, setPendingId] = useState(null)
  const hasLoadedOnce = useRef(false)

  const loadPatients = useCallback(async () => {
    try {
      const data = await getPatients()
      setPatients(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load patients')
    } finally {
      hasLoadedOnce.current = true
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadPatients()
    const interval = setInterval(loadPatients, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [loadPatients])

  const handleStartCall = useCallback(
    async (patientId) => {
      setPendingId(patientId)
      try {
        await startCall(patientId)
        await loadPatients()
      } catch (err) {
        setError(err.message || 'Failed to start call')
      } finally {
        setPendingId(null)
      }
    },
    [loadPatients],
  )

  const handleReset = useCallback(async () => {
    try {
      await resetDemo()
      await loadPatients()
    } catch (err) {
      setError(err.message || 'Failed to reset demo')
    }
  }, [loadPatients])

  return {
    patients,
    loading,
    error,
    pendingId,
    startCall: handleStartCall,
    resetDemo: handleReset,
    dismissError: () => setError(null),
  }
}
