// Data-access hook for patients: polling, start-call, and reset actions.
// Consumed exclusively through PatientsContext (see src/context) so any
// component in the tree can read this state without prop drilling.

import { useCallback, useEffect, useState } from 'react'
import { getPatients, resetPatients, startCall } from '../services/api'
import { POLL_INTERVAL_MS } from '../constants/config'

export function usePatientsData() {
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
      await resetPatients()
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
