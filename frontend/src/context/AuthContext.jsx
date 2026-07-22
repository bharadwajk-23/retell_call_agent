// Single source of truth for the (static, client-side-only) login gate.

import { useAuthData } from '../hooks/useAuthData'
import { AuthContext } from './authContext.js'

export function AuthProvider({ children }) {
  const value = useAuthData()
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
