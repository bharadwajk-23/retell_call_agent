// Thin consumer hook for AuthContext — the only way components should read
// login state (never call useAuthData directly).

import { useContext } from 'react'
import { AuthContext } from '../context/authContext.js'

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth() must be used within an <AuthProvider>')
  }
  return context
}
