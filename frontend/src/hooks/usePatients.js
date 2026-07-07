import { useCallback, useEffect, useState } from 'react'
import { getPatients, resetDemo, startCall } from '../services/api'

const POLL_INTERVAL_MS = 2000

export function usePatients() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pendingId, setPendingId] = useState(null)

  const loadPatients = useCallback(async (options = {}) => {
    const { skipLoading = false } = options

    if (!skipLoading) {
      setLoading(true)
    }

    try {
      const data = await getPatients()
      setPatients(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load patients')
    } finally {
      if (!skipLoading) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    let active = true

    const refreshPatients = async () => {
      await loadPatients({ skipLoading: true })
      if (!active) {
        return
      }
      setLoading(false)
    }

    refreshPatients()
    const interval = window.setInterval(refreshPatients, POLL_INTERVAL_MS)

    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [loadPatients])

  const handleStartCall = useCallback(
    async (patientId) => {
      setPendingId(patientId)
      try {
        await startCall(patientId)
        await loadPatients({ skipLoading: true })
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
      await loadPatients({ skipLoading: true })
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
