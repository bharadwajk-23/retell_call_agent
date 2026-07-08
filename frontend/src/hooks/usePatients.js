// Thin consumer hook for PatientsContext — the only way components should
// read patient/call state (never call usePatientsData directly).

import { useContext } from 'react'
import { PatientsContext } from '../context/patientsContext.js'

export function usePatients() {
  const context = useContext(PatientsContext)
  if (!context) {
    throw new Error('usePatients() must be used within a <PatientsProvider>')
  }
  return context
}
