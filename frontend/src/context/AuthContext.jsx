import React, { createContext, useState, useCallback, useEffect } from 'react'

const AuthContext = createContext(null)

const HARDCODED_CREDENTIALS = {
  username: 'admin',
  password: 'admin123',
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedAuth = localStorage.getItem('auth')
    if (storedAuth) {
      const auth = JSON.parse(storedAuth)
      if (auth.isAuthenticated && auth.username) {
        setIsAuthenticated(true)
        setUsername(auth.username)
      }
    }
    setLoading(false)
  }, [])

  const login = useCallback((inputUsername, inputPassword) => {
    if (
      inputUsername === HARDCODED_CREDENTIALS.username &&
      inputPassword === HARDCODED_CREDENTIALS.password
    ) {
      setIsAuthenticated(true)
      setUsername(inputUsername)
      localStorage.setItem(
        'auth',
        JSON.stringify({ isAuthenticated: true, username: inputUsername }),
      )
      return { success: true }
    }
    return { success: false, error: 'Invalid credentials' }
  }, [])

  const logout = useCallback(() => {
    setIsAuthenticated(false)
    setUsername('')
    localStorage.removeItem('auth')
  }, [])

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
