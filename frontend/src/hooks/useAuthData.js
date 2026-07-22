// Data-access hook for the static login gate: checks credentials against
// one hardcoded username/password and persists the result in localStorage
// so a page refresh doesn't log the user back out.

import { useCallback, useState } from 'react'
import { AUTH_PASSWORD, AUTH_STORAGE_KEY, AUTH_USERNAME } from '../constants/config'

export function useAuthData() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => window.localStorage.getItem(AUTH_STORAGE_KEY) === 'true',
  )
  const [error, setError] = useState(null)

  const login = useCallback((username, password) => {
    if (username === AUTH_USERNAME && password === AUTH_PASSWORD) {
      window.localStorage.setItem(AUTH_STORAGE_KEY, 'true')
      setIsAuthenticated(true)
      setError(null)
      return true
    }
    setError('Invalid username or password')
    return false
  }, [])

  const logout = useCallback(() => {
    window.localStorage.removeItem(AUTH_STORAGE_KEY)
    setIsAuthenticated(false)
  }, [])

  return {
    isAuthenticated,
    error,
    login,
    logout,
    dismissError: () => setError(null),
  }
}
