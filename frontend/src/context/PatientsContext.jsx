// Single source of truth for patient/call state, so the dashboard (and any
// future page) can consume it via `usePatients()` without threading props
// through every level of the component tree.

import { usePatientsData } from '../hooks/usePatientsData'
import { PatientsContext } from './patientsContext.js'

export function PatientsProvider({ children }) {
  const value = usePatientsData()
  return <PatientsContext.Provider value={value}>{children}</PatientsContext.Provider>
}
